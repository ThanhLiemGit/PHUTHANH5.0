import re
import json
import unicodedata
from pathlib import Path

with open(Path(__file__).parent / "phuthanh_logic.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

def normalize(name):
    name = str(name).lower()
    name = re.sub(r"\b(hẻm|hem)\b", "", name)
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8")
    name = re.sub(r"\s+", " ", name).strip()
    if "do bi" in name or "đỗ bí" in name:
        return "do bi"
    return name

def extract_main_number(so_nha_raw):
    parts = so_nha_raw.split("/")
    for part in parts:
        digits = re.findall(r"\d+", part)
        if digits:
            return int(digits[0])
    return None

def check_address(input_text):
    input_text = input_text.lower().strip()
    match = re.match(r"(?:số\s*)?([\w/]+)\s+(?:đường\s*)?(.+)", input_text)
    if not match:
        return "⛔ Không xác định được địa chỉ."

    so_nha_raw = match.group(1)
    duong_raw = match.group(2)
    duong = normalize(duong_raw)

    if duong not in DATA:
        return f"⛔ Địa chỉ không thuộc phạm vi Phường Phú Thạnh."

    so_chinh = extract_main_number(so_nha_raw)
    if so_chinh is None:
        return "⛔ Không xác định được số nhà."

    for segment in DATA[duong]:
        tu = extract_main_number(segment["tu"])
        den = extract_main_number(segment["den"])
        if tu is None or den is None or not (tu <= so_chinh <= den):
            continue

        side = segment.get("side")
        if side == "odd" and so_chinh % 2 == 0:
            continue
        if side == "even" and so_chinh % 2 != 0:
            continue

        return f"""✅ Địa chỉ thuộc **Khu phố {segment['khu_pho']}**

📌 Thông tin quản lý:
– Bí thư chi bộ: Nguyễn Thị Hiền
– Khu phố trưởng: Lê Thị Thúy Vân
– Trưởng Ban CTMT: Lê Thanh Liêm – 📞 0909 292 289
– Cảnh sát khu vực: Nguyễn Phước Thiện

🔎 Bạn cần liên hệ với ai không?"""

    return "⛔ Địa chỉ không thuộc đoạn nào được quản lý."
