import re
import json
import unicodedata

# Load logic JSON
with open("phuthanh_logic_with_hem_fixed.json", "r", encoding="utf-8") as f:
    logic_data = json.load(f)

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^\w\s/]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def parse_address(addr: str):
    addr = normalize(addr)
    m = re.match(r"^([\w/]+)\s+(.*)$", addr)
    if not m:
        return None
    return {"house": m.group(1), "street": m.group(2)}

def get_side(num: int) -> str:
    return "even" if num % 2 == 0 else "odd"

def extract_number(text: str):
    m = re.search(r"(\d+)", str(text))
    return int(m.group(1)) if m else None

def check_address(addr: str):
    parsed = parse_address(addr)
    if not parsed:
        return None

    house = parsed["house"]          # ví dụ: "63/1", "25A", "11"
    street = parsed["street"]        # ví dụ: "nguyen son"
    rules = logic_data.get(street, [])
    if not rules:
        return None

    # ======================
    # CASE 1: HẺM (có "/")
    # ======================
    if "/" in house:
        hem1_raw = house.split("/")[0]   # số hẻm chính (vd: "63" trong "63/1")
        sub_part = house.split("/")[1] if len(house.split("/")) > 1 else None
        sub_num = extract_number(sub_part) if sub_part else None

        for rule in rules:
            for h in rule.get("hems", []):
                if str(h.get("hem")) == str(hem1_raw):
                    tu = extract_number(h.get("tu"))
                    den = extract_number(h.get("den"))
                    # Nếu trong JSON hẻm được định nghĩa có khoảng số
                    if tu and den and sub_num and tu <= sub_num <= den:
                        return {
                            "khu_pho": h["khu_pho"],
                            "street": street,
                            "hem": hem1_raw,
                            "house": house
                        }
                    # Nếu hẻm kiểu include all (1 → 9999)
                    if tu == 1 and den == 9999:
                        return {
                            "khu_pho": h["khu_pho"],
                            "street": street,
                            "hem": hem1_raw,
                            "house": house
                        }

        return None

    # ======================
    # CASE 2: MẶT TIỀN (không có "/")
    # ======================
    num = extract_number(house)
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

