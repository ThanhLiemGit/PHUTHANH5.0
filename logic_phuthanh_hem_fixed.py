import re
import json

# Load logic JSON
with open("phuthanh_logic_with_hem_fixed.json", "r", encoding="utf-8") as f:
    logic_data = json.load(f)

def normalize(text: str) -> str:
    """Chuẩn hóa tên đường và địa chỉ: bỏ dấu, thường hóa"""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s/]", " ", text)  # bỏ ký tự đặc biệt trừ dấu /
    text = re.sub(r"\s+", " ", text)  # bỏ thừa khoảng trắng
    return text

def parse_address(addr: str):
    """Tách số nhà (có thể kèm hẻm) + tên đường"""
    addr = normalize(addr)
    m = re.match(r"^([\w/]+)\s+(.*)$", addr)  # ✅ cho phép cả chữ + số
    if not m:
        return None
    return {
        "house": m.group(1),  # vd: 47/1/2/3 hoặc A25
        "street": m.group(2)  # vd: tran quang co
    }

def get_side(num: int) -> str:
    """Trả về 'odd' hoặc 'even'"""
    return "even" if num % 2 == 0 else "odd"

def extract_number(text: str):
    """Lấy số đầu tiên trong chuỗi (vd: 25A -> 25, A25 -> 25, B12C -> 12)"""
    m = re.search(r"(\d+)", str(text))
    return int(m.group(1)) if m else None

def check_address(addr: str):
    parsed = parse_address(addr)
    if not parsed:
        return None

    house = parsed["house"]
    street = parsed["street"]

    # lấy rule theo tên đường
    rules = logic_data.get(street, [])
    if not rules:
        return None

    # Nếu địa chỉ có hẻm (có "/")
    if "/" in house:
        hem1 = house.split("/")[0]  # lấy hẻm gốc
        hem1_num = extract_number(hem1)
        for rule in rules:
            hem_list = rule.get("hems", [])
            if hem1 in hem_list or (hem1_num and str(hem1_num) in hem_list):
                return {
                    "khu_pho": rule["khu_pho"],
                    "street": street,
                    "hem": hem1
                }

    # Nếu là mặt tiền
    num = extract_number(house)
    if num is None:
        return None

    for rule in rules:
        tu = extract_number(rule["tu"])
        den = extract_number(rule["den"])
        if tu is None or den is None:
            continue  # bỏ qua rule không parse được

        side = rule.get("side", "both")
        if tu <= num <= den:
            if side == "both" or get_side(num) == side:
                return {
                    "khu_pho": rule["khu_pho"],
                    "street": street,
                    "house": house  # giữ nguyên cả hậu tố/tiền tố
                }

    return None
