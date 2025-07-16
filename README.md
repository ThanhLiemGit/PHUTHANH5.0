
# Bot KP5 – Telegram + GPT + Logic địa bàn

## Tính năng:
- Kiểm tra địa chỉ Khu phố 5 (KP5 – Phú Thạnh)
- Trả lời tự nhiên bằng GPT nếu nội dung không phải địa chỉ
- Tích hợp danh thiếp ASCII + cảnh báo logic

## Cách deploy:
1. Upload repo lên GitHub riêng
2. Deploy trên https://render.com với:
   - Build: pip install -r requirements.txt
   - Start: uvicorn main:app --host 0.0.0.0 --port 10000
3. Biến môi trường:
   - TELEGRAM_BOT_TOKEN = (token bot)
   - USE_GPT = true
   - OPENAI_API_KEY = (nếu muốn GPT)
