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

    house = parsed["house"]          # ví dụ: "63/1", "A25", "25A"
    street = parsed["street"]        # ví dụ: "nguyen son"
    rules = logic_data.get(street, [])
    if not rules:
        return None

    # ===== 1) XỬ LÝ HẺM: CHỈ NHẬN KHI HẺM CÓ TRONG JSON =====
    if "/" in house:
        hem1_raw = house.split("/")[0]          # phần trước dấu '/' đầu tiên, ví dụ "63" trong "63/1/2"
        hem1_num = extract_number(hem1_raw)     # số hẻm (int) nếu parse được

        # Duyệt các rule của tuyến đường: hẻm hợp lệ khi có trong rule["hems"]
        for rule in rules:
            hem_list = rule.get("hems", []) or []

            # Chuẩn hóa hem_list về chuỗi số (nếu được), để so sánh dễ
            normalized_hems = set()
            for h in hem_list:
                hn = extract_number(h)
                if hn is not None:
                    normalized_hems.add(str(hn))
                else:
                    normalized_hems.add(str(h).strip())

            if (
                (str(hem1_raw) in hem_list)  # khớp đúng chuỗi gốc (ít dùng)
                or (hem1_num is not None and str(hem1_num) in normalized_hems)
            ):
                # Tìm thấy hẻm hợp lệ => trả ngay KP theo rule đang duyệt
                return {
                    "khu_pho": rule["khu_pho"],
                    "street": street,
                    "hem": hem1_raw
                }

        # Không tìm thấy hẻm trong bất kỳ rule nào -> coi là không thuộc
        return None

    # ===== 2) MẶT TIỀN: SO THEO RANGE + CHẴN/LẺ =====
    num = extract_number(house)  # nhận cả 25A / A25
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
                    "house": house  # giữ nguyên tiền tố/hậu tố để hiện lại cho đẹp
                }

    return None
