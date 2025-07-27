def check_address(input_text):
    input_text = input_text.strip().lower()
    input_text = input_text.replace("số ", "").replace("đường ", "")
    kp5_data = {
        "nguyễn sơn": {"range": (3, 71), "hems": [13, 59], "side": "both"},
        "thoại ngọc hầu": {"range": (126, 244), "hems": [182, 198, 212, 240, 242, 244], "side": "even"},
        "phan văn năm": {"range": (1, 73), "hems": [19, 47], "side": "both"},
        "hiền vương": {"range": (1, 26), "hems": [3, 11, 12], "side": "both"}
    }

    import re
    match = re.match(r"(\d+)(?:/(\d+))?\s+(.*)", input_text)
    if not match:
        return "⛔ Không xác định được địa chỉ. Vui lòng kiểm tra lại."

    so_nha = int(match.group(1))
    hem = int(match.group(2)) if match.group(2) else None
    duong = match.group(3).strip()

    if duong not in kp5_data:
        return "⛔ Địa chỉ không thuộc Khu phố 5."

    info = kp5_data[duong]
    tu, den = info["range"]
    if not (tu <= so_nha <= den):
        return "⛔ Địa chỉ không thuộc Khu phố 5."

    if info["side"] == "even" and so_nha % 2 != 0:
        return "⛔ Địa chỉ không thuộc phía chẵn (KP5 quản lý)."

    if hem:
        if hem not in info["hems"]:
            return f"⚠️ Địa chỉ không chính xác vì đường {duong.title()} không có hẻm số {hem}."

    return "✅ Địa chỉ thuộc Khu phố 5."
