import json
from save_in_mongo import insert_affidavit
from extract_fields import (
    load_tables,
    extract_age,
    extract_address,
    extract_mobile,
    extract_name_and_parent,
)

# -------------------------------------------------
# Load OCR text
# -------------------------------------------------
with open("azure_ocr_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Load tables (used only for context, not PAN)
tables = load_tables()

# -------------------------------------------------
# PAN — SINGLE SOURCE OF TRUTH (Azure OCR)
# -------------------------------------------------
with open("azure_pan.json", "r", encoding="utf-8") as f:
    pan_data = json.load(f)

pan = pan_data.get("pan")
pan_conf = pan_data.get("confidence", 0.0)
pan_reason = pan_data.get("reason", "PAN source unknown")

# -------------------------------------------------
# Name + Father / Spouse (deterministic regex)
# -------------------------------------------------
full_name, father_or_spouse_name, name_conf, name_reason = extract_name_and_parent(text)
father_conf = name_conf

# -------------------------------------------------
# Age
# -------------------------------------------------
age, age_conf = extract_age(text)

# -------------------------------------------------
# Address
# -------------------------------------------------
address, address_conf = extract_address(text)

# -------------------------------------------------
# Mobile
# -------------------------------------------------
mobile, mobile_conf = extract_mobile(text)

# -------------------------------------------------
# Final confidence (PAN dominates)
# -------------------------------------------------
final_confidence = round(
    max(pan_conf, name_conf, age_conf, address_conf),
    2
)

# -------------------------------------------------
# Output (line by line)
# -------------------------------------------------
print("\nFINAL EXTRACTED DATA:\n")

print(f"Name: {full_name} | {name_reason} | confidence={name_conf}")
print(f"father_or_spouse_name: {father_or_spouse_name}  (confidence: {father_conf})")
print(f"age: {age}  (confidence: {age_conf})")
print(f"address: {address}  (confidence: {address_conf})")
print(f"pan: {pan}  (confidence: {pan_conf})")
print(f"mobile_number: {mobile}  (confidence: {mobile_conf})")

print(f"\nFINAL OVERALL CONFIDENCE: {final_confidence}")

print("\nCONFIDENCE BREAKDOWN:")
print(f"PAN: {pan_conf} | {pan_reason}")
print(f"Name: {name_conf} | {name_reason}")
print(f"Age: {age_conf}")
print(f"Address: {address_conf}")
print(f"Mobile: {mobile_conf}")

# -------------------------------------------------
# Build final output dictionary
# -------------------------------------------------
final_output = {
    "full_name": full_name,
    "father_or_spouse_name": father_or_spouse_name,
    "age": age,
    "address": address,
    "pan": pan,
    "pan_status": {
        "confidence": pan_conf,
        "reason": pan_reason
    },
    "additional_information": {
        "mobile_number": mobile
    },
    "confidence": {
        "full_name": name_conf,
        "father_or_spouse_name": father_conf,
        "age": age_conf,
        "address": address_conf,
        "pan": pan_conf
    }
}

print("\nFINAL EXTRACTED DATA (DICT):\n")
for k, v in final_output.items():
    print(f"{k}: {v}")

# -------------------------------------------------
# Insert into MongoDB (immutable insert)
# -------------------------------------------------
mongo_status = insert_affidavit(final_output)

print("\nMongoDB Insert Status:")
print(mongo_status)
