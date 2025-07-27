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
    openai.api_base = "https://openrouter.ai/api/v1"

def is_address(text: str):
    text = text.strip().lower()
    pattern = r"^(số\s*)?\d+(?:/\d+)*(?:\s+đường)?\s+[a-zàáảãạâầấậẫẩăằắặẵẳêềếệễểôồốộỗổơờớợỡởưừứựữửêèéẹẽẻùúụũủìíịĩỉỳýỵỹỷđ\s]+$"
    return re.match(pattern, text) is not None

def send(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

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
            reply = "❗ Xin lỗi, tôi chỉ có thể kiểm tra địa chỉ trong Khu phố 5. Bạn vui lòng nhập theo dạng như: 3/11 Hiền Vương"
        send(chat_id, reply)
    return {"ok": True}

def gpt_reply(prompt):
    try:
        completion = openai.ChatCompletion.create(
            model="openrouter/openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý hành chính khu phố 5, Phường Phú Thạnh, có nhiệm vụ trả lời thân thiện, chính xác, đúng vai trò KP5."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return "⚠️ Xin lỗi, tôi đang gặp sự cố khi truy cập GPT. Vui lòng thử lại sau."
