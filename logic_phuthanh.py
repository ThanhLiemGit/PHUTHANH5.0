import re
import json
import unicodedata
from pathlib import Path

# Load dữ liệu JSON toàn phường
with open(Path(__file__).parent / "phuthanh_data.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

def normalize(text):
    text = unicodedata.normalize("NFD", str(text))
    text = text.encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()

def extract_main_number(so):
    match = re.match(r"(\d+)", so)
    return int(match.group(1)) if match else None

def check_address(input_text):
    input_text = input_text.lower().strip()
    match = re.match(r"(?:số\s*)?([\dA-Za-z/]+)\s+(?:đường\s*)?(.+)", input_text)
    if not match:
        return "⛔ Không xác định được địa chỉ. Vui lòng kiểm tra lại."

    so_nha_raw = match.group(1)
    duong_raw = match.group(2).strip()
    duong = normalize(duong_raw)

    if duong not in DATA:
        return f"⛔ Địa chỉ không thuộc phạm vi quản lý Phường Phú Thạnh."

    so_nha_parts = so_nha_raw.split("/")
    so_nha_chinh = extract_main_number(so_nha_parts[0])
    if so_nha_chinh is None:
        return "⛔ Không xác định được số nhà chính."

    for doan in DATA[duong]:
        try:
            tu = extract_main_number(doan["tu"])
            den = extract_main_number(doan["den"])
        except:
            continue

        if tu is not None and den is not None and tu <= so_nha_chinh <= den:
            khu_pho = doan["khu_pho"]
            return (
                f"✅ Địa chỉ thuộc **Khu phố {khu_pho}**\n\n"
                f"📌 Thông tin quản lý:\n"
                f"– Bí thư chi bộ: Nguyễn Thị Hiền\n"
                f"– Khu phố trưởng: Lê Thị Thúy Vân\n"
                f"– Trưởng Ban CTMT: Lê Thanh Liêm – 📞 0909 292 289\n"
                f"– Cảnh sát khu vực: Nguyễn Phước Thiện\n\n"
                f"🔎 Bạn cần liên hệ với ai không?"
            )

    return "⛔ Số nhà không thuộc đoạn đường nào được quản lý."