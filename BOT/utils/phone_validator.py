import csv
import re
import os

# Load country codes and length from a CSV file
# Format: country,code,min_length,max_length
COUNTRY_PHONE_RULES = {}

csv_path = os.path.join(os.path.dirname(__file__), "phone_rules.csv")
with open(csv_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        code = row["code"].strip()
        COUNTRY_PHONE_RULES[code] = {
            "country": row["country"],
            "min": int(row["min_length"]),
            "max": int(row["max_length"])
        }

def is_valid_phone(phone: str) -> bool:
    # Очищення: прибираємо +, пробіли, дужки, тире
    cleaned_phone = re.sub(r"[^\d]", "", phone)

    for code, rule in COUNTRY_PHONE_RULES.items():
        code_digits = re.sub(r"[^\d]", "", code)
        if cleaned_phone.startswith(code_digits):
            return rule["min"] <= len(cleaned_phone) <= rule["max"]
    return False
