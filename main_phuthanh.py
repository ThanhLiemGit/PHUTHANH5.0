import json
from fastapi import FastAPI, Request
import httpx
import os
from logic_phuthanh_hem_fixed import check_address
from openai import AsyncOpenAI

app = FastAPI()

# Load dữ liệu khu phố & tuyến đường
with open("khu_pho_info.json", "r", encoding="utf-8") as f:
    khu_pho_data = json.load(f)

with open("phuthanh_logic_with_hem_fixed.json", "r", encoding="utf-8") as f:
    street_data = json.load(f)

# Together API
client = AsyncOpenAI(api_key=os.getenv("TOGETHER_API_KEY"), base_url="https://api.together.xyz/v1")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

DATA_DIR = "data"  # folder chứa json các phòng ban

# ------------------------------------------------
def main_menu():
    keyboard = [
        [{"text": "🏠 Tra cứu địa chỉ", "callback_data": "menu_address"}],
        [{"text": "📋 Contact Khu phố", "callback_data": "menu_contact"}],
        [{"text": "🎭 Phòng Văn Hóa - Xã Hội", "callback_data": "phong_van_hoa_xa_hoi"}],
        [{"text": "🛎️ Trung tâm Phục vụ Hành chính Công", "callback_data": "trung_tam_hanh_chinh_cong"}],
        [{"text": "🏢 Văn phòng HĐND & UBND", "callback_data": "van_phong_hdnd_ubnd"}],
        [{"text": "🏗️Phòng Kinh tế, Hạ Tầng & Đô Thị", "callback_data": "phong_kinh_te_ha_tang_do_thi"}],
        [{"text": "🤝 Ủy ban MTTQ Phường", "callback_data": "uy_ban_mttq"}],
    ]
    return {"inline_keyboard": keyboard}

def contact_menu():
    keyboard = []
    for kp in sorted(khu_pho_data.keys(), key=lambda x: int(x)):
        keyboard.append([{"text": f"Khu phố {kp}", "callback_data": f"kp_{kp}"}])
    return {"inline_keyboard": keyboard}

def get_kp_contact(kp_id):
    info = khu_pho_data.get(str(kp_id))
    if not info:
        return "❌ Không tìm thấy thông tin."
    return (
        f"📍 **Khu phố {kp_id}**\n"
        f"🧑‍💼 Bí thư chi bộ: {info.get('bi_thu', 'Chưa cập nhật')}\n"
        f"🧑‍🤝‍🧑 Khu phố trưởng: {info.get('kp_truong', 'Chưa cập nhật')}\n"
        f"🙋‍♂️ Trưởng CTMT: {info.get('truong_ctmt', 'Chưa cập nhật')}\n"
        f"👮 CSKV: {info.get('cskv', 'Chưa cập nhật')}"
    )

def get_department_info(dept_key: str) -> str:
    file_path = os.path.join(DATA_DIR, f"{dept_key}.json")
    if not os.path.exists(file_path):
        return "❌ Chưa có dữ liệu cho phòng ban này."

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nhan_vien = data.get("nhan_vien", [])
    if not nhan_vien:
        return "❌ Chưa cập nhật nhân sự."

    lines = [f"🏢 **Thông tin {dept_key.replace('_', ' ').title()}**\n"]
    for nv in nhan_vien:
        lines.append(
            f"- {nv.get('chuc_vu', 'Chức vụ')}: {nv.get('ho_ten', 'Chưa rõ')} 📞 {nv.get('so_dien_thoai', 'N/A')}"
        )
    return "\n".join(lines)

# ------------------------------------------------
def format_address_response(addr_info, user_input):
    kp = addr_info.get("khu_pho")
    if not kp:
        return f"❌ Không tìm thấy thông tin cho địa chỉ {user_input}"

    info = khu_pho_data.get(str(kp), {})
    return (
        f"📍 Địa chỉ **{user_input}** thuộc **Khu phố {kp}**, Phường Phú Thạnh.\n\n"
        f"🧑‍💼 Bí thư chi bộ: {info.get('bi_thu', 'Chưa cập nhật')}\n"
        f"🧑‍🤝‍🧑 Khu phố trưởng: {info.get('kp_truong', 'Chưa cập nhật')}\n"
        f"🙋‍♂️ Mặt trận KP: {info.get('truong_ctmt', 'Chưa cập nhật')}\n"
        f"👮 CSKV: {info.get('cskv', 'Chưa cập nhật')}"
    )

async def call_gpt_with_context(user_input: str):
    prompt = f"""
Bạn là cán bộ phường Phú Thạnh. Người dân nhắn: "{user_input}".
Nếu đây không phải địa chỉ hợp lệ trong dữ liệu thì trả lời thân thiện, giải thích rằng bạn chỉ hỗ trợ tra cứu địa chỉ trong Phường Phú Thạnh.
"""
    response = await client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )
    return response.choices[0].message.content.strip()

async def handle_message(user_input: str):
    addr_info = check_address(user_input)

    if addr_info and addr_info.get("khu_pho"):
        return format_address_response(addr_info, user_input)
    else:
        return await call_gpt_with_context(user_input)

# ------------------------------------------------
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    # Message text
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"].strip()

        if text == "/start":
            reply = "Xin chào! 👋\nChọn chức năng:"
            async with httpx.AsyncClient() as client_http:
                await client_http.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": reply,
                    "reply_markup": main_menu()
                })
        else:
            reply = await handle_message(text)
            async with httpx.AsyncClient() as client_http:
                await client_http.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": reply,
                    "parse_mode": "Markdown"
                })

    # Callback query
    if "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        message_id = query["message"]["message_id"]
        cb_data = query["data"]

        if cb_data == "menu_address":
            text = "📍 Mời bạn nhập địa chỉ (số nhà + tên đường) để tra cứu:"
            markup = None

        elif cb_data == "menu_contact":
            text = "📋 Chọn khu phố:"
            markup = contact_menu()

        elif cb_data.startswith("kp_"):
            kp_id = cb_data.replace("kp_", "")
            text = get_kp_contact(kp_id)
            markup = None

        elif cb_data in [
            "phong_van_hoa_xa_hoi",
            "trung_tam_hanh_chinh_cong",
            "van_phong_hdnd_ubnd",
            "phong_kinh_te_ha_tang_do_thi",
            "uy_ban_mttq"
        ]:
            text = get_department_info(cb_data)
            markup = None

        else:
            text = "❌ Lựa chọn không hợp lệ."
            markup = None

        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        if markup:
            payload["reply_markup"] = markup

        async with httpx.AsyncClient() as client_http:
            await client_http.post(f"{TELEGRAM_API_URL}/editMessageText", json=payload)

    return {"ok": True}
