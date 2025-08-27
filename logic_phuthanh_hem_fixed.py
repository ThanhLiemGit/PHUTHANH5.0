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
    m = re.match(r"^([\d/]+)\s+(.*)$", addr)
    if not m:
        return None
    return {
        "house": m.group(1),  # vd: 47/1/2/3
        "street": m.group(2)  # vd: tran quang co
    }

def get_side(num: int) -> str:
    """Trả về 'odd' hoặc 'even'"""
    return "even" if num % 2 == 0 else "odd"

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
        for rule in rules:
            hem_list = rule.get("hems", [])
            if hem1 in hem_list:
                return {
                    "khu_pho": rule["khu_pho"],
                    "street": street,
                    "hem": hem1
                }

    # Nếu là mặt tiền
    try:
        num = int(re.match(r"^\d+", house).group())
    except:
        return None

    def safe_int(val):
    """Lấy phần số đầu tiên từ chuỗi (vd: '25A' -> 25)"""
    m = re.match(r"^(\d+)", str(val))
    return int(m.group(1)) if m else None

for rule in rules:
    tu = safe_int(rule["tu"])
    den = safe_int(rule["den"])
    if tu is None or den is None:
        continue  # bỏ qua rule không parse được

    side = rule.get("side", "both")
    if tu <= num <= den:
        if side == "both" or get_side(num) == side:
            return {
                "khu_pho": rule["khu_pho"],
                "street": street,
                "house": str(num)
            }

    return None
