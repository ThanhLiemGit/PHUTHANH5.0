
import re

def is_address(input_text):
    return bool(re.match(r"^\d+(?:/\d+)?\s+.+", input_text.strip()))

def check_address(input_text):
    input_text = input_text.strip()
    kp5_data = {
        "Nguyễn Sơn": {"range": (3, 71), "hems": [13, 59], "side": "both"},
        "Thoại Ngọc Hầu": {"range": (126, 244), "hems": [182, 198, 212, 240, 242, 244], "side": "even"},
        "Phan Văn Năm": {"range": (1, 73), "hems": [19, 47], "side": "both"},
        "Hiền Vương": {"range": (1, 26), "hems": [3, 11, 12], "side": "both"}
    }

    match = re.match(r"^(\d+)(?:/(\d+))?\s+(.+)", input_text)
    if not match:
        return "⛔ Không xác định được địa chỉ. Hãy nhập theo dạng: 182/19 Thoại Ngọc Hầu"

    so1 = int(match.group(1))
    so2 = int(match.group(2)) if match.group(2) else None
    duong = match.group(3).strip()

    if duong not in kp5_data:
        return "⛔ Địa chỉ không thuộc Khu phố 5."

    info = kp5_data[duong]
    tu, den = info["range"]

    # Đảo lại: so1 = hẻm chính, so2 = số nhà trong hẻm (nếu có)
    hem = so1 if so2 else None
    so_nha = so2 if so2 else so1

    if so_nha < tu or so_nha > den:
        return "⛔ Địa chỉ không thuộc Khu phố 5."

    if info["side"] == "even" and so_nha % 2 != 0:
        return "⛔ Địa chỉ không thuộc phía chẵn (KP5 quản lý)."

    if hem and hem not in info["hems"]:
        return f"⚠️ Địa chỉ không chính xác vì đường {duong} không có hẻm số {hem}."

    return "✅ Địa chỉ thuộc Khu phố 5\n\n🏅 LÊ THANH LIÊM\nTrưởng Ban Công tác Mặt trận\n📞 0909 292 289"
