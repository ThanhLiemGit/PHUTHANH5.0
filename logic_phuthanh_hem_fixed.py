import re
import json
import unicodedata

# Load logic JSON (giữ đúng tên file bạn đang dùng)
with open("phuthanh_logic_with_hem_fixed.json", "r", encoding="utf-8") as f:
    logic_data = json.load(f)

def normalize(text: str) -> str:
    """Chuẩn hóa tên đường và địa chỉ: bỏ dấu tiếng Việt, thường hóa"""
    text = text.lower().strip()
    # bỏ dấu tiếng Việt
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    # bỏ ký tự đặc biệt (trừ '/')
    text = re.sub(r"[^\w\s/]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def parse_address(addr: str):
    """Tách phần 'house' (có thể có chữ + '/') và 'street'."""
    addr = normalize(addr)
    # Cho phép house bắt đầu bằng chữ hoặc số, có thể có nhiều '/'
    m = re.match(r"^([\w/]+)\s+(.*)$", addr)
    if not m:
        return None
    return {"house": m.group(1), "street": m.group(2)}

def get_side(num: int) -> str:
    return "even" if num % 2 == 0 else "odd"

def extract_number(text: str):
    """Lấy số đầu tiên trong chuỗi: 25A -> 25, A25 -> 25, B12C -> 12; không có số -> None."""
    m = re.search(r"(\d+)", str(text))
    return int(m.group(1)) if m else None

def check_address(addr: str):
    parsed = parse_address(addr)
    if not parsed:
        return None

    house = parsed["house"]          # ví dụ: "63/1", "A25", "25A", "11"
    street = parsed["street"]        # ví dụ: "nguyen son"
    rules = logic_data.get(street, [])
    if not rules:
        return None

    num = extract_number(house)

    # ===== CASE 1: HẺM (có "/") =====
    if "/" in house:
        hem1_raw = house.split("/")[0]   # phần trước dấu "/"
        hem1_num = extract_number(hem1_raw)

        for rule in rules:
            hem_list = rule.get("hems", []) or []

            for h in hem_list:
                if isinstance(h, dict):
                    # hẻm có range chi tiết
                    if str(h.get("hem")) == str(hem1_raw):
                        tu = extract_number(h.get("tu"))
                        den = extract_number(h.get("den"))
                        if tu and den and num and tu <= num <= den:
                            return {
                                "khu_pho": h["khu_pho"],
                                "street": street,
                                "hem": hem1_raw
                            }
                else:
                    # hẻm kiểu list string → nguyên hẻm
                    if str(hem1_raw) == str(h) or (hem1_num and str(hem1_num) == str(h)):
                        return {
                            "khu_pho": rule["khu_pho"],
                            "street": street,
                            "hem": hem1_raw
                        }

        return None  # là hẻm nhưng không có trong dữ liệu → loại luôn

    # ===== CASE 2: MẶT TIỀN (không có "/") =====
    if num is None:
        return None

    for rule in rules:
        tu = extract_number(rule.get("tu"))
        den = extract_number(rule.get("den"))
        if tu is None or den is None:
            continue

        side = rule.get("side", "both")
        if tu <= num <= den:
            if side == "both" or get_side(num) == side:
                return {
                    "khu_pho": rule["khu_pho"],
                    "street": street,
                    "house": house
                }

    return None
