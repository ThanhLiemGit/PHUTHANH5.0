import re
import json
import unicodedata
from pathlib import Path

with open(Path(__file__).parent / "phuthanh_logic_with_hem_fixed.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)
with open(Path(__file__).parent / "khu_pho_info.json", "r", encoding="utf-8") as f:
    KP_INFO = json.load(f)

def normalize(name):
    name = str(name).lower()
    name = re.sub(r"\b(hẻm|hem)\b", "", name)
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8")
    name = re.sub(r"\s+", " ", name).strip()
    if "do bi" in name or "đỗ bí" in name:
        return "do bi"
    return name

# ✅ so sánh “số + hậu tố” theo thứ tự tự nhiên
def to_sortable(s: str):
    s = str(s).upper()
    # Hỗ trợ 134, 134A, 134A3...
    m = re.match(r"^(\d+)([A-Z]?)(\d*)$", s)
    if not m:
        # dùng wildcard lớn để không chặn match khi tu/den là 'nan'
        return (float("inf"), "", float("inf"))
    n = int(m.group(1))
    letter = m.group(2) or ""
    tail = int(m.group(3) or 0)
    return (n, letter, tail)

def extract_main_number(so_nha_raw):
    parts = so_nha_raw.upper().split("/")
    last = parts[-1]
    m = re.match(r"(\d+)([A-Z]*\d*)", last)
    return m.group(0) if m else None

def extract_hem_path(so_nha_raw):
    parts = so_nha_raw.split("/")
    return "/".join(parts[:-1]) if len(parts) > 1 else None

def check_address(input_text):
    input_text = input_text.lower().strip()
    m = re.match(r"(?:số\s*)?([\w/]+)\s+(?:đường\s*)?(.+)", input_text)
    if not m:
        return "⛔ Không xác định được địa chỉ."

    so_nha_raw = m.group(1)
    duong_raw = m.group(2)

    duong_norm = normalize(duong_raw)           # có thể là "57/27 to hieu" HOẶC "to hieu"
    so_chinh = extract_main_number(so_nha_raw)
    if so_chinh is None:
        return "⛔ Không xác định được số nhà."

    hem_path = extract_hem_path(so_nha_raw)     # ví dụ "57/27" từ "12/57/27" hoặc None
    candidates = []

    # 1) Ưu tiên chính xác theo người dùng gõ
    candidates.append(duong_norm)

    # 2) Nếu người dùng gõ số nhà có hẻm rời (duong_norm chỉ là tên đường)
    #    thì thử ghép "hem + duong"
    if hem_path and "/" not in duong_norm.split()[0]:
        candidates.append(f"{hem_path} {duong_norm}")

    # 3) Nếu người dùng gõ "hem + duong" nhưng DATA chỉ có tuyến gốc, fallback về tên đường
    base_duong = duong_norm.split(" ", 1)[-1] if "/" in duong_norm.split()[0] and " " in duong_norm else duong_norm
    if base_duong != duong_norm:
        candidates.append(base_duong)

    # Loại trùng, giữ thứ tự ưu tiên
    seen = set()
    ordered_candidates = []
    for c in candidates:
        if c not in seen:
            ordered_candidates.append(c); seen.add(c)

    # Duyệt theo độ đặc hiệu: tuyến có hẻm (khóa chứa "/") trước, rồi đến tuyến gốc
    ordered_candidates.sort(key=lambda x: ("/" not in x, len(x)))  # có "/" -> False -> ưu tiên trước

    # Thực thi match
    for duong_key in ordered_candidates:
        if duong_key not in DATA:
            continue
        for segment in DATA[duong_key]:
            tu = str(segment.get("tu", "nan")).upper()
            den = str(segment.get("den", "nan")).upper()

            # 'nan' nghĩa là wildcard đoạn không theo số (ví dụ khu/CC)
            if tu != "NAN" and den != "NAN":
                if not (to_sortable(tu) <= to_sortable(so_chinh) <= to_sortable(den)):
                    continue

                # Kiểm tra chẵn/lẻ nếu có
                num_match = re.match(r"\d+", so_chinh)
                if num_match:
                    num = int(num_match.group(0))
                    side = segment.get("side", "both")
                    if side == "odd" and num % 2 == 0:
                        continue
                    if side == "even" and num % 2 != 0:
                        continue
            # Không còn kiểm tra "/" trong segment["tu"]; hẻm đã được ưu tiên qua duong_key

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
