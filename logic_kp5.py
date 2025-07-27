import re

def check_address(input_text):
    input_text = input_text.lower().strip()
    kp5_data = {
        "nguyễn sơn": {"range": (3, 71), "hems": [13, 59, 61], "side": "both"},
        "thoại ngọc hầu": {"range": (126, 244), "hems": [182, 198, 212, 240, 242, 244], "side": "even"},
        "phan văn năm": {"range": (1, 73), "hems": [19, 47], "side": "both"},
        "hiền vương": {"range": (1, 26), "hems": [3, 11, 12], "side": "both"},
    }

    match = re.match(r"(?:số\s*)?([\d/]+)\s+(?:đường\s*)?(.+)", input_text)
    if not match:
        return "⛔ Không xác định được địa chỉ. Vui lòng kiểm tra lại."

    so_nha_raw = match.group(1)
    duong = match.group(2).strip()

    so_nha_parts = so_nha_raw.split("/")
    so_nha_chinh = int(so_nha_parts[0]) if so_nha_parts[0].isdigit() else None
    hem_cap_1 = int(so_nha_parts[0]) if len(so_nha_parts) > 1 else None  # luôn lấy phần đầu làm hẻm cấp 1

    if duong not in kp5_data:
        return "⛔ Địa chỉ không thuộc Khu phố 5."

    info = kp5_data[duong]
    tu, den = info["range"]

    if so_nha_chinh is None or not (tu <= so_nha_chinh <= den):
        return "⛔ Địa chỉ không thuộc Khu phố 5."

    if info["side"] == "even" and so_nha_chinh % 2 != 0:
        return "⛔ Địa chỉ không thuộc phía chẵn (KP5 quản lý)."

    if hem_cap_1 and hem_cap_1 not in info["hems"]:
        return f"⚠️ Địa chỉ không chính xác vì đường {duong.title()} không có hẻm số {hem_cap_1}."

    return "✅ Địa chỉ thuộc Khu phố 5."
