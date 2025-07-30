import re

def check_address(input_text):
    input_text = input_text.lower().strip()
    kp5_data = {
        "nguyễn sơn": {
            "range": (3, 71),
            "side": "odd",  # chỉ số lẻ
            "hems": [13, 59, 61]
        },
        "thoại ngọc hầu": {
            "range": (126, 244),
            "side": "even",
            "hems": [182, 198, 212, 240, 242, 244]
        },
        "phan văn năm": {
            "range": (1, 73),
            "side": "odd",
            "hems": [19, 47]
        },
        "hiền vương": {
            "range": (1, 26),
            "side": "both",
            "hems": [3, 11, 12]
        }
    }

    match = re.match(r"(?:số\s*)?([\d/]+)\s+(?:đường\s*)?(.+)", input_text)
    if not match:
        return "⛔ Không xác định được địa chỉ. Vui lòng kiểm tra lại."

    so_nha_raw = match.group(1)
    duong = match.group(2).strip()

    so_nha_parts = so_nha_raw.split("/")
    try:
        so_nha_chinh = int(so_nha_parts[0])
    except ValueError:
        return "⛔ Số nhà không hợp lệ."

    if duong not in kp5_data:
        return "⛔ Địa chỉ không thuộc Khu phố 5."

    config = kp5_data[duong]
    tu, den = config["range"]

    if not (tu <= so_nha_chinh <= den):
        return f"⛔ Số nhà {so_nha_chinh} không nằm trong phạm vi quản lý của đường {duong.title()} (từ {tu} đến {den})."

    if config["side"] == "even" and so_nha_chinh % 2 != 0:
        return f"⛔ Địa chỉ không thuộc phía chẵn trên đường {duong.title()} (KP5 quản lý phía chẵn)."

    if config["side"] == "odd" and so_nha_chinh % 2 == 0:
        return f"⛔ Địa chỉ không thuộc phía lẻ trên đường {duong.title()} (KP5 quản lý phía lẻ)."

    # Kiểm tra hẻm cấp 1 (nếu có)
    if len(so_nha_parts) > 1:
        try:
            hem_cap_1 = int(so_nha_parts[1])
        except ValueError:
            return "⛔ Hẻm không hợp lệ."

        if "hems" in config and hem_cap_1 not in config["hems"]:
            return f"⚠️ Địa chỉ không chính xác vì đường {duong.title()} không có hẻm số {hem_cap_1}."

    return "✅ Địa chỉ thuộc Khu phố 5."
