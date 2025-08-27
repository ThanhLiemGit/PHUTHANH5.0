import json
import re

INPUT_FILE = "phuthanh_logic_with_hem_fixed.json"
OUTPUT_FILE = "phuthanh_logic_converted.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

new_data = {}

for key, rules in data.items():
    m = re.match(r"^(\d+)\s+(.*)$", key)
    if m:
        # Đây là hẻm: "16 tran quang co"
        hem_num = m.group(1)       # "16"
        street = m.group(2)        # "tran quang co"

        if street not in new_data:
            new_data[street] = []

        for rule in rules:
            # Tìm rule tương đồng đã có (trùng tu, den, khu_pho, side)
            matched = None
            for existing_rule in new_data[street]:
                if (existing_rule["tu"] == rule["tu"] and
                    existing_rule["den"] == rule["den"] and
                    existing_rule["khu_pho"] == rule["khu_pho"] and
                    existing_rule["side"] == rule.get("side", "both")):
                    matched = existing_rule
                    break

            if matched:
                matched["hems"].append(hem_num)
            else:
                new_rule = {
                    "tu": rule["tu"],
                    "den": rule["den"],
                    "khu_pho": rule["khu_pho"],
                    "side": rule.get("side", "both"),
                    "hems": [hem_num]
                }
                new_data[street].append(new_rule)

    else:
        # Đây là tuyến đường bình thường (không có số hẻm trong key)
        street = key
        if street not in new_data:
            new_data[street] = []

        for rule in rules:
            new_rule = {
                "tu": rule["tu"],
                "den": rule["den"],
                "khu_pho": rule["khu_pho"],
                "side": rule.get("side", "both"),
                "hems": []
            }
            new_data[street].append(new_rule)

# Save ra file mới
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(new_data, f, ensure_ascii=False, indent=2)

print(f"✅ Converted JSON saved to {OUTPUT_FILE}")
