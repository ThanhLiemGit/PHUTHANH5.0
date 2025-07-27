import re

def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r"(số\s*)", "", text)
    text = re.sub(r"(đường\s*)", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def is_address(text):
    text = normalize_text(text)
    return bool(re.match(r"\d+(/\d+)*\s+.+", text))

def check_address(input_text):
    input_text = normalize_text(input_text)

    kp5_data = {
        "nguyễn sơn": {"range": (3, 71), "hems": [13, 59], "side": "both"},
        "thoại ngọc hầu": {"range": (126, 244), "hems": [182, 198, 212, 240, 242, 244], "side": "even"},
        "phan văn năm": {"range": (1, 73), "hems": [19, 47], "side": "both"},
        "hiền vương": {"range": (1, 26), "hems": [3, 11, 12], "side": "both"},
    }

    match = re.match(r"(\d+(?:/\d+)*?)\s+(.*)", input_text)
    if not match:
        return "⛔ Không xác định được địa chỉ. Vui lòng kiểm tra lại."

    so_nha_str, duong = match.groups()
    so_nha_parts = so_nha_str.split("/")
    try:
        so_nha = int(so_nha_parts[0])
    except:
        return "⛔ Số nhà không hợp lệ."

    hem_cap_1 = int(so_nha_parts[1]) if len(so_nha_parts) > 1 else None
    duong = duong.strip()

    if duong not in kp5_data:
        return "⛔ Địa chỉ không thuộc Khu phố 5."

    info = kp5_data[duong]
    tu, den = info["range"]
    if not (tu <= so_nha <= den):
        return "⛔ Địa chỉ không thuộc Khu phố 5."

    if info["side"] == "even" and so_nha % 2 != 0:
        return "⛔ Địa chỉ không thuộc phía chẵn (KP5 quản lý)."

    if hem_cap_1 and hem_cap_1 not in info["hems"]:
        return f"⚠️ Địa chỉ không chính xác vì đường {duong.title()} không có hẻm số {hem_cap_1}."

    return "✅ Địa chỉ thuộc Khu phố 5."
