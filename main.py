from fastapi import FastAPI, Request
from logic_kp5 import check_address
import os
import requests
import openai
import re

app = FastAPI()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USE_GPT = os.getenv("USE_GPT", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

if USE_GPT and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    openai.api_base = "https://api.together.xyz/v1"

def Import normalize(text: str):
    text = text.strip().lower()
    pattern = r"^(số\s*)?\d+[a-zA-Z]?(?:/\d+)*(?:\s+đường)?\s+[a-zàáảãạâầấậẫẩăằắặẵẳêềếệễểôồốộỗổơờớợỡởưừứựữửèéẹẽẻùúụũủìíịĩỉỳýỵỹỷđ\s]+$"
    return re.match(pattern, text) is not None

def send(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        if Import normalize(text):
            reply = check_address(text)
        elif USE_GPT:
            reply = gpt_reply(text)
        else:
            reply = "❗ Tôi chỉ có thể kiểm tra địa chỉ trong Khu phố 5. Vui lòng nhập theo dạng: 3/11 Hiền Vương"
        send(chat_id, reply)
    return {"ok": True}

def gpt_reply(prompt):
    try:
        print("🔁 Gọi GPT với prompt:", prompt)
        response = openai.chat.completions.create(
            model="Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý hành chính khu phố 5."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Lỗi GPT:", e)
        return "⚠️ Xin lỗi, tôi đang gặp sự cố khi truy cập GPT. Vui lòng thử lại sau."
