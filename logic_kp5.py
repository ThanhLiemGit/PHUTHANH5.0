import re
import unicodedata

# Hàm chuẩn hóa chuỗi (loại bỏ dấu, chuẩn hóa khoảng trắng)
def normalize(text):
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"\s+", " ", text)  # xóa khoảng trắng thừa
    return text.lower().strip()

# Trích số chính từ số nhà, ví dụ: 1A → 1
def extract_main_number(so):
    match = re.match(r"(\d+)", so)
    return int(match.group(1)) if match else None

def check_address(input_text):
    input_text = input_text.lower().strip()

    # Dữ liệu quản lý của KP5
    kp5_data = {
        "nguyen son": {"range": (1, 71), "side": "odd", "hems": [13, 59, 61]},
        "thoai ngoc hau": {"range": (126, 244), "side": "even", "hems": [182, 198, 212, 240, 242, 244]},
        "phan van nam": {"range": (1, 73), "side": "odd", "hems": [19, 47]},
        "hien vuong": {"range": (1, 26), "side": "both", "hems": [3, 11, 12]},
    }

    # Tách số nhà và tên đường
    match = re.match(r"(?:số\s*)?([\w/]+)\s+(?:đường\s*)?(.+)", input_text)
    if not match:
        return "⛔ Không xác định được địa chỉ. Vui lòng kiểm tra lại."

    so_nha_raw = match.group(1)
    duong_raw = match.group(2).strip()
    duong = normalize(duong_raw)

    if duong not in kp5_data:
        return f"⛔ Địa chỉ không thuộc Khu phố 5."

    info = kp5_data[duong]
    tu, den = info["range"]
    so_nha_parts = so_nha_raw.split("/")
    so_nha_chinh = extract_main_number(so_nha_parts[-1])

    if so_nha_chinh is None or not (tu <= so_nha_chinh <= den):
        return "⛔ Số nhà không thuộc phạm vi quản lý."

    # Kiểm tra chẵn/lẻ nếu có quy định
    if info["side"] == "even" and so_nha_chinh % 2 != 0:
        return "⛔ Chỉ quản lý phía số **chẵn** trên tuyến đường này."
    if info["side"] == "odd" and so_nha_chinh % 2 != 1:
        return "⛔ Chỉ quản lý phía số **lẻ** trên tuyến đường này."

    # Kiểm tra hẻm cấp 1 nếu có
    if len(so_nha_parts) > 1:
        hem_cap_1 = extract_main_number(so_nha_parts[0])
        if hem_cap_1 and info["hems"] and hem_cap_1 not in info["hems"]:
            return f"⚠️ Địa chỉ không chính xác vì đường {duong_raw.title()} không có hẻm số {so_nha_parts[0]}."

    return "✅ Địa chỉ thuộc Khu phố 5."
