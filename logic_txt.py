import re
import unicodedata
from pathlib import Path

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

def get_street_description(duong: str) -> str:
    path = Path(__file__).parent / "phuthanh_descriptions.txt"
    duong = normalize(duong)
    with open(path, "r", encoding="utf-8") as f:
        blocks = f.read().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        if not lines:
            continue
        title = lines[0].strip(": ").lower()
        if title == duong:
            return "\n".join(lines[1:])
    return ""

def analyze_address(input_text):
    match = re.match(r"(?:số\s*)?([\w/]+)\s+(?:đường\s*)?(.+)", input_text.lower())
    if not match:
        return None
    so_nha_raw = match.group(1)
    duong_raw = match.group(2).strip()
    duong = normalize(duong_raw)
    so_nha = extract_main_number(so_nha_raw)
    return {
        "so_nha": so_nha,
        "so_nha_raw": so_nha_raw,
        "duong": duong,
        "duong_raw": duong_raw,
        "mo_ta": get_street_description(duong)
    }