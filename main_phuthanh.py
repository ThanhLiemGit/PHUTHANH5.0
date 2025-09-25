# main.py
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
from typing import Dict

# ==============================
# Cấu hình
# ==============================
API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
BASE_URL = f"https://api.telegram.org/bot{API_TOKEN}"

app = FastAPI()

# ==============================
# Data JSON (mỗi phòng ban là 1 key)
# ==============================
departments: Dict = {
    "phong_van_hoa_xa_hoi": {
        "nhan_vien": [
            {"ho_ten": "Nguyễn Văn A", "chuc_vu": "Nhân viên", "so_dien_thoai": "0909123456"}
        ]
    },
    "trung_tam_hanh_chinh_cong": {
        "nhan_vien": [
            {"ho_ten": "Trần Thị B", "chuc_vu": "Trưởng bộ phận", "so_dien_thoai": "0909765432"}
        ]
    },
    "van_phong_hdnd_ubnd": {
        "nhan_vien": [
            {"ho_ten": "Lê Văn C", "chuc_vu": "Chánh văn phòng", "so_dien_thoai": "0909988776"}
        ]
    },
    "phong_kinh_te_ha_tang_do_thi": {
        "nhan_vien": [
            {"ho_ten": "Phạm Thị D", "chuc_vu": "Chuyên viên", "so_dien_thoai": "0911222333"}
        ]
    },
    "uy_ban_mttq": {
        "nhan_vien": [
            {"ho_ten": "Võ Văn E", "chuc_vu": "Ủy viên", "so_dien_thoai": "0988111222"}
        ]
    }
}

# ==============================
# Hàm tiện ích
# ==============================
def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(f"{BASE_URL}/sendMessage", data=payload)


def build_main_menu():
    return {
        "inline_keyboard": [
            [{"text": "Tra cứu địa chỉ", "callback_data": "tra_cuu_dia_chi"}],
            [{"text": "Contact khu phố", "callback_data": "contact_khu_pho"}],
            [{"text": "Phòng Văn Hóa - Xã Hội", "callback_data": "phong_van_hoa_xa_hoi"}],
            [{"text": "Trung tâm Hành chính Công", "callback_data": "trung_tam_hanh_chinh_cong"}],
            [{"text": "Văn phòng HĐND & UBND", "callback_data": "van_phong_hdnd_ubnd"}],
            [{"text": "Phòng Kinh tế, Hạ Tầng & Đô Thị", "callback_data": "phong_kinh_te_ha_tang_do_thi"}],
            [{"text": "Ủy ban MTTQ Phường", "callback_data": "uy_ban_mttq"}]
        ]
    }


def build_department_detail(callback_key: str):
    data = departments.get(callback_key, {})
    if not data:
        return "Chưa có dữ liệu cho phòng ban này."
    
    lines = []
    for nv in data.get("nhan_vien", []):
        lines.append(f"👤 <b>{nv['ho_ten']}</b>\n"
                     f"📌 {nv['chuc_vu']}\n"
                     f"📞 {nv['so_dien_thoai']}\n")
    return "\n".join(lines)


# ==============================
# Webhook
# ==============================
@app.post("/")
async def telegram_webhook(req: Request):
    data = await req.json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Xin chào 👋\nChọn chức năng:", build_main_menu())

    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        callback_data = callback["data"]

        if callback_data in ["tra_cuu_dia_chi", "contact_khu_pho"]:
            send_message(chat_id, f"👉 Chức năng: {callback_data} đang được phát triển.")

        elif callback_data in departments:
            detail_text = build_department_detail(callback_data)
            send_message(chat_id, detail_text, build_main_menu())

    return JSONResponse(content={"ok": True})
