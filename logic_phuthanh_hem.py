import re
import json
import unicodedata
from pathlib import Path

# Load dữ liệu tuyến đường (đã bao gồm hẻm)
with open(Path(__file__).parent / "phuthanh_logic_with_hem.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

# Load dữ liệu cán bộ khu phố
with open(Path(__file__).parent / "khu_pho_info.json", "r", encoding="utf-8") as f:
    KP_INFO = json.load(f)

# Chuẩn hóa tên đường
def normalize(name):
    name = str(name).lower()
    name = re.sub(r"\b(hẻm|hem)\b", "", name)
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8")
    name = re.sub(r"\s+", " ", name).strip()
    if "do bi" in name or "đỗ bí" in name:
        return "do bi"
    return name

# Lấy số chính từ mọi cấp số nhà (VD: 1/1/1A -> 1)
def extract_main_number(so_nha_raw):
    digits = re.findall(r"\d+", so_nha_raw)
    if digits:
        return int(digits[-1])  # Ưu tiên lấy số cuối cùng
    return None

# Lấy hẻm path (VD: 13/1/2A => "13/1/2")
def extract_hem_path(so_nha_raw):
    parts = so_nha_raw.split("/")
    if len(parts) > 1:
        return "/".join(parts[:-1])
    return None

# Logic xác định địa chỉ
def check_address(input_text):
    input_text = input_text.lower().strip()
    match = re.match(r"(?:số\s*)?([\w/]+)\s+(?:đường\s*)?(.+)", input_text)
    if not match:
        return "⛔ Không xác định được địa chỉ."

    so_nha_raw = match.group(1)
    duong_raw = match.group(2)
    duong = normalize(duong_raw)

    if duong not in DATA:
        return "⛔ Địa chỉ không thuộc phạm vi Phường Phú Thạnh."

    so_chinh = extract_main_number(so_nha_raw)
    if so_chinh is None:
        return "⛔ Không xác định được số nhà."

    hem_path = extract_hem_path(so_nha_raw)

    for segment in DATA[duong]:
        tu = extract_main_number(segment["tu"])
        den = extract_main_number(segment["den"])
        if tu is None or den is None or not (tu <= so_chinh <= den):
            continue

        side = segment.get("side", "both")
        if side == "odd" and so_chinh % 2 == 0:
            continue
        if side == "even" and so_chinh % 2 != 0:
            continue

        # Nếu đoạn là hẻm, kiểm tra hem_path có tồn tại
        if "/" in segment["tu"]:
            hem_from = extract_hem_path(segment["tu"])
            hem_to = extract_hem_path(segment["den"])
            if hem_path is None or hem_path != hem_from:
                continue

        kp_id = segment["khu_pho"]
        info = KP_INFO.get(kp_id, {})

        return f"""✅ Địa chỉ thuộc **Khu phố {kp_id}**

📌 Thông tin quản lý:
– Bí thư chi bộ: {info.get('bi_thu', 'N/A')}
– Khu phố trưởng: {info.get('kp_truong', 'N/A')}
– Trưởng Ban CTMT: {info.get('truong_ctmt', 'N/A')} – 📞 {info.get('sdt_ctmt', 'N/A')}
– Cảnh sát khu vực: {info.get('cskv', 'N/A')}

🔎 Bạn cần liên hệ với ai không?
"""

    return "⛔ Địa chỉ không thuộc đoạn nào được quản lý."