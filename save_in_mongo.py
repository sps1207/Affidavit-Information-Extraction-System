from pymongo import MongoClient
from datetime import datetime

def insert_affidavit(data):
    client = MongoClient("mongodb://127.0.0.1:27017/")
    db = client.affidavit_db
    collection = db.affidavits

    document = {
        "pan": data.get("pan"),  # searchable field
        "full_name": data.get("full_name"),
        "father_or_spouse_name": data.get("father_or_spouse_name"),
        "age": data.get("age"),
        "address": data.get("address"),
        "additional_information": data.get("additional_information"),
        "confidence": data.get("confidence"),
        "extracted_at": datetime.utcnow(),   # VERY IMPORTANT
        "source": "ocr+llm"                  # optional metadata
    }

    result = collection.insert_one(document)

    return {
        "inserted_id": str(result.inserted_id),
        "status": "inserted"
    }
