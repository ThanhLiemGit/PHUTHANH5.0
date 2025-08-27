import json
from fastapi import FastAPI, Request
import httpx
import os
from logic_phuthanh_hem_fixed import check_address
from openai import AsyncOpenAI

app = FastAPI()

# Load dữ liệu cán bộ khu phố
with open("khu_pho_info.json", "r", encoding="utf-8") as f:
    khu_pho_data = json.load(f)

# Together API
client = AsyncOpenAI(api_key=os.getenv("TOGETHER_API_KEY"), base_url="https://api.together.xyz/v1")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ------------------------------------------------
def format_address_response(addr_info, user_input):
    kp = addr_info.get("khu_pho")
    if not kp:
        return f"❌ Không tìm thấy thông tin cho địa chỉ {user_input}"

    info = khu_pho_data.get(str(kp), {})
    return (
        f"📍 Địa chỉ **{user_input}** thuộc **Khu phố {kp}**, Phường Phú Thạnh.\n\n"
        f"👤 Bí thư chi bộ: {info.get('bi_thu', 'Chưa cập nhật')}\n"
        f"👤 Khu phố trưởng: {info.get('truong', 'Chưa cập nhật')}\n"
        f"📞 Liên hệ: {info.get('so_dien_thoai', 'Chưa có')}\n"
        f"👮 CSKV: {info.get('canh_sat', 'Chưa cập nhật')}"
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

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_input = data["message"]["text"].strip()
        reply = await handle_message(user_input)

        async with httpx.AsyncClient() as client:
            await client.post(f"{TELEGRAM_API_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": reply,
                "parse_mode": "Markdown"
            })

    return {"ok": True}
