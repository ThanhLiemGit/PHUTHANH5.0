from fastapi import FastAPI, Request
from logic_phuthanh import check_address, normalize
from logic_txt import analyze_address
import os
import requests
import re
import openai

app = FastAPI()

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
    pattern = r"^\d+[a-zA-Z]?(?:/\d+)*(?:\s+duong)?\s+[a-z\s]+$"
    return re.match(pattern, text) is not None

# Hàm gửi tin nhắn Telegram
def send(chat_id, text):
    requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

# Hàm xử lý GPT
def gpt_reply(prompt):
    try:
        print("🔁 Gọi GPT với prompt:", prompt)
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là cán bộ phường tư vấn địa chỉ, nói thân thiện nhưng đúng thực tế dữ liệu địa phương."
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
            logic_result = check_address(text)
            if logic_result.startswith("✅"):
                data = analyze_address(text)
                if data:
                    prompt = f"""
Địa chỉ người dân nhập: **{text}**

✅ Hệ thống đã xác nhận địa chỉ hợp lệ: {logic_result}

Mô tả tuyến đường:
{data['mo_ta']}

Hãy phản hồi lại như cán bộ phường: xác nhận địa chỉ và chia sẻ thêm vài lưu ý nếu có.
"""
                    reply = gpt_reply(prompt)
                else:
                    reply = logic_result
            else:
                reply = logic_result  # lỗi logic, không dùng GPT
        elif USE_GPT:
            reply = gpt_reply(text)
        else:
            reply = "❗ Vui lòng nhập địa chỉ theo mẫu: 3/11 Hiền Vương"
        send(chat_id, reply)
    return {"ok": True"}