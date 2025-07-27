import re

kp5_data = {
    "nguyễn sơn": {"range": (3, 71), "hems": [13, 59], "side": "both"},
    "thoại ngọc hầu": {"range": (126, 244), "hems": [182, 198, 212, 240, 242, 244], "side": "even"},
    "phan văn năm": {"range": (1, 73), "hems": [19, 47], "side": "both"},
    "hiền vương": {"range": (1, 26), "hems": [3, 11, 12], "side": "both"}
}

def is_address(text):
    pattern = r"(số\s*)?(\d+(?:/\d+)*)(?:\s+đường|\s+)?\s+(.*)"
    return re.match(pattern, text.strip().lower())

def check_address(input_text):
    input_text = input_text.strip().lower()
    match = re.match(r"(số\s*)?(\d+(?:/\d+)*)(?:\s+đường|\s+)?\s+(.*)", input_text)

    if not match:
        return "⛔ Không xác định được địa chỉ. Vui lòng kiểm tra lại."

    full_number = match.group(2)  # e.g. 182/19/2
    street = match.group(3).strip()
    number_parts = full_number.split("/")
    
    try:
        so_nha = int(number_parts[0])
        hem = int(number_parts[1]) if len(number_parts) > 1 else None
    except ValueError:
        return "⛔ Không thể phân tích số nhà. Vui lòng kiểm tra lại."

    if street not in kp5_data:
        return "⛔ Địa chỉ không thuộc Khu phố 5."

    info = kp5_data[street]
    tu, den = info["range"]

    if not (tu <= so_nha <= den):
        return "⛔ Địa chỉ không thuộc Khu phố 5."

    if info["side"] == "even" and so_nha % 2 != 0:
        return "⛔ Địa chỉ không thuộc phía chẵn (KP5 quản lý)."

    if hem and hem not in info["hems"]:
        return f"⚠️ Địa chỉ không chính xác vì đường {street.title()} không có hẻm số {hem}."

    return "✅ Địa chỉ thuộc Khu phố 5."
