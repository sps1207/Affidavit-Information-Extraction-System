# Affidavit-Information-Extraction-System

(OCR + NLP + LLM + MongoDB)

---

## 1. Project Overview

This project presents an **end-to-end Affidavit Information Extraction System** designed to automatically extract structured personal information from **Indian legal affidavit PDFs**.

Affidavits are challenging documents because they typically contain:
- Noisy OCR output
- Mixed printed and handwritten Hindi text
- Irregular layouts (tables + free text)
- Legal phrasing instead of fixed templates

To address these challenges, this system adopts a **hybrid architecture** combining:
- **Cloud-grade OCR (Azure Document Intelligence)** for robust text and table extraction  
- **Deterministic rule-based NLP** for legally sensitive fields  
- **LLM-based semantic reasoning (Ollama – LLaMA 3 8B)** for handwritten identity inference  
- **MongoDB** for structured persistence with confidence tracking  

The system is intentionally designed to **avoid hallucination**, especially for sensitive identifiers such as PAN numbers.

---

## 2. Key Features

- Accurate PAN extraction **strictly from OCR output (no LLM inference)**
- Hindi-language affidavit understanding
- Best-effort extraction of handwritten names using semantic context
- Confidence score per extracted field
- Modular, extensible, production-oriented design
- Persistent storage with auditability in MongoDB

---

## 3. Extracted Information

The system extracts the following fields:

- Full Name  
- Father / Spouse Name  
- Age  
- Address  
- PAN Number (mandatory, OCR-validated only)  
- Mobile Number  
- Confidence score per field  

---

## 4. Technology Stack

| Layer | Technology |
|-----|-----------|
| OCR & Layout | Azure Document Intelligence |
| NLP | Python (Regex, heuristics) |
| LLM | Ollama – LLaMA 3 (8B) |
| Database | MongoDB |
| Language | Python 3 |

---

## 5. Project Structure
Affidavit-Information-Extraction-System/
│
├── input/
│ └── affidavit.pdf
│
├── azure_ocr.py
├── extract_fields.py
├── llm_extractor.py
├── result.py
├── save_in_mongo.py
│
├── azure_ocr_text.txt
├── azure_tables.txt
│
├── README.md
├── requirements.txt
└── sample_output.json

---

## 6. Setup Instructions

### 6.1 Python Environment

`bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt`

### 6.2 Azure OCR Configuration

1.Create an Azure Document Intelligence resource

2.Copy the Endpoint and API Key

3.Update them in azure_ocr.py:

`python 
AZURE_ENDPOINT = "https://<your-resource>.cognitiveservices.azure.com/"
AZURE_KEY = "<your-api-key>"`

4.Place the affidavit PDF in:
`bash
input/affidavit.pdf`

### 6.3 Ollama (LLM) Setup

1.Install Ollama
https://ollama.com/

2.Pull the model:
`bash
ollama pull llama3:8b`

3.Ensure the path is correct in llm_extractor.py:
`python
OLLAMA_PATH = r"C:\Users\<username>\AppData\Local\Programs\Ollama\ollama.exe"`

### 6.4 MongoDB Setup

1.Install MongoDB Community Server

2.Start MongoDB: 
`bash
mongod`
3. Default connection used:
`mongodb://127.0.0.1:27017/`
Database and collection are created automatically:

Database: affidavit_db

Collection: affidavits
## 7. Database Configuration (MongoDB)

This project uses **MongoDB** as the persistent storage layer for storing extracted affidavit information along with field-level confidence scores and audit metadata.

MongoDB was chosen because:
- It supports **schema-flexible documents**, ideal for OCR/LLM outputs
- It allows **multiple records per PAN** for versioning and re-processing
- It is widely used in production-grade data pipelines

---

### 7.1 MongoDB Installation

Install **MongoDB Community Server** from the official website:

🔗 https://www.mongodb.com/try/download/community

During installation:
- Select **Complete Setup**
- Enable **MongoDB Compass** (optional but recommended)
- Allow MongoDB to run as a **Windows Service**

---

### 7.2 Starting MongoDB Server

Start the MongoDB daemon:

`bash
mongod`
If MongoDB is installed as a service, it may already be running.

Verify MongoDB is listening on the default port:
`mongodb://127.0.0.1:27017/`
### 7.3 Connecting to MongoDB Shell

Open MongoDB Shell:

`mongosh mongodb://127.0.0.1:27017/`

Once connected, you should see:

`test>`
### 7.4 Database and Collection Structure

The project automatically creates the database and collection.

Database Name: affidavit_db

Collection Name: affidavits

Switch to the database:

`use affidavit_db`
7.5 Document Schema (Logical Structure)

Each affidavit extraction is stored as an immutable document.
{
  "full_name": "सेवी बहादर",
  "father_or_spouse_name": "स्व० सुरेन्द्र बहादर",
  "age": 57,
  "address": "दुर्गापुर, डाकघर-नरपतगंज, जिला-अररिया (बिहार)",
  "pan": "ESZPB9277K",
  "pan_status": {
    "confidence": 0.85,
    "reason": "PAN extracted from table cell"
  },
  "additional_information": {
    "mobile_number": "6205808744"
  },
  "confidence": {
    "full_name": 0.6,
    "father_or_spouse_name": 0.6,
    "age": 0.85,
    "address": 0.8,
    "pan": 0.85
  },
  "created_at": "2025-12-29T13:14:30Z"
}
### 7.6 Insert Strategy (Important Design Choice)

1.No destructive updates

2.Each extraction run inserts a new record

3.Multiple records with the same PAN are allowed

4.This enables:

-Version tracking

-Auditability

-Model comparison over time

Insertion logic is implemented in:
`save_in_mongo.py`
### 7.7 Verifying Inserted Records

List all affidavit records:

`db.affidavits.find().pretty()`


Search records by PAN:

`db.affidavits.find({ pan: "ESZPB9277K" }).pretty()`


This may return multiple records if the same affidavit was processed multiple times.

### 7.8 Deleting Records (For Testing Only)

Delete a specific PAN record:

`db.affidavits.deleteOne({ pan: "ESZPB9277K" })`


Delete all records (⚠️ testing only):

`db.affidavits.deleteMany({})`
7.9 Why MongoDB Fits This Assessment

-OCR and LLM outputs are semi-structured

-Field presence may vary per document

-Confidence scores evolve with model improvements

-MongoDB supports rapid schema evolution without migrations

-This makes MongoDB a strong choice for real-world document intelligence pipelines.

## 8.How to Run the Project
Step 1: Run Azure OCR
`python azure_ocr.py`


This generates:

azure_ocr_text.txt

azure_tables.txt

Step 2: Run Extraction & Database Insert
`python result.py`


This performs:

-PAN validation (OCR-only)

-Name & parent extraction

-Confidence scoring

-MongoDB insertion
## 9. Sample Output (JSON)
{
  "full_name": "सेवी बहादर",
  "father_or_spouse_name": "स्व० सुरेन्द्र बहादर",
  "age": 57,
  "address": "दुर्गापुर, डाकघर-नरपतगंज, थाना-नरपतगंज, जिला-अररिया (बिहार)",
  "pan": "ESZPB9277K",
  "pan_status": {
    "confidence": 0.85,
    "reason": "PAN extracted from Azure OCR table"
  },
  "additional_information": {
    "mobile_number": "6205808744"
  },
  "confidence": {
    "full_name": 0.6,
    "father_or_spouse_name": 0.6,
    "age": 0.85,
    "address": 0.8,
    "pan": 0.85
  }
}
## 10. Design Decisions 
*PAN Handling

-PAN is never inferred by LLM

-PAN is accepted only if detected by Azure OCR

-Prevents hallucination and ensures legal correctness

*Name Extraction

-Regex used first for deterministic matches

-LLM used only when handwriting or OCR noise makes extraction ambiguous

-Confidence reflects inference strength

*Confidence Scores

-Each field has an independent confidence

-Enables downstream validation, audits, and human review

## 11. Future Scope & Improvements:
Integration with Advanced Multimodal LLMs (e.g., GPT-5.2)

While this system uses OCR + text-only LLM inference, future versions can significantly improve accuracy by leveraging multimodal foundation models such as GPT-5.2, which offer:

-Direct visual understanding of handwritten regions

-Region-aware layout reasoning (not row/column dependent)

-Joint vision-language semantics

-Better disambiguation of names, relationships, and addresses

-Reduced reliance on brittle OCR ordering

With GPT-5.2-style multimodal processing:

-Handwritten names can be extracted directly from image regions

-Legal document structure can be inferred visually

-Confidence scores can be learned rather than heuristically assigned

This would make the system more robust, scalable, and production-ready for large-scale legal document automation.

## 12. Conclusion

This project demonstrates a real-world, production-oriented approach to document intelligence by combining:

-Cloud OCR

-Deterministic NLP

-LLM semantic reasoning

-Database persistence

It prioritizes accuracy, legal safety, and explainability, making it suitable for enterprise and government-grade document processing systems.

Author: Sasmita Pala
Purpose: Technical Assessment Submission





