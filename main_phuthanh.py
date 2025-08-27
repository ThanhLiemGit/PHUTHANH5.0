from fastapi import FastAPI, Request
from logic_phuthanh_hem_fixed import check_address, normalize
import os
import requests
import re
import openai

app = FastAPI()

import openai

# Lấy token Telegram và cấu hình GPT
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"
USE_GPT = os.getenv("USE_GPT", "true").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Khởi tạo client GPT (Together API)
client = None
if USE_GPT and OPENAI_API_KEY:
    client = openai.OpenAI(
        api_key=OPENAI_API_KEY,
        base_url="https://api.together.xyz/v1"
    )

# Hàm kiểm tra định dạng địa chỉ
def is_address(text: str):
    text = normalize(text)
    # Cho phép:
    #  - 12/57/27 to hieu
    #  - 12 57/27 to hieu  (hẻm rời)
    #  - 4 158/49 phan anh
    #  - 134A luong the vinh
    patterns = [
        r"^\d+[a-zA-Z]?(?:/\d+)*(?:\s+(?:duong)\s+)?[a-z][a-z\s]+$",           # cũ
        r"^\d+[a-zA-Z]?\s+\d+(?:/\d+)+(?:\s+(?:duong)\s+)?[a-z][a-z\s]+$",     # số nhà + hẻm rời + tên đường
    ]
    return any(re.match(p, text) for p in patterns)

# Hàm gửi tin nhắn Telegram
def send(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

# ✅ Hàm xử lý GPT dùng SDK >= 1.0
def gpt_reply(prompt):
    try:
        print("🔁 Gọi GPT với prompt:", prompt)
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là trợ lý hành chính phường Phú Thạnh, Quận Tân Phú. Hãy trả lời thân thiện và chính xác theo ngữ cảnh địa phương."
                },
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Lỗi GPT:", e)
        return "⚠️ Xin lỗi, tôi đang gặp sự cố khi truy cập GPT. Vui lòng thử lại sau."


# Webhook Telegram
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        if is_address(text):
            reply = check_address(text)
        elif USE_GPT:
            reply = gpt_reply(text)
        else:
            reply = "❗ Vui lòng nhập địa chỉ theo mẫu: 3/11 Hiền Vương"
        send(chat_id, reply)
    return {"ok": True}
