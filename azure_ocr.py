from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import re
import json

# =====================================================
# CONFIG (HARDCODED AS REQUESTED)
# =====================================================

AZURE_ENDPOINT = "https://affidavit-ocr.cognitiveservices.azure.com/"
AZURE_KEY = "9q7pGHRU9ezdO9IT1gn3t0vGjnEGY0YIm3Cbgx4rMBa9ot3rhgm1JQQJ99BLACYeBjFXJ3w3AAALACOGN1Aw"

PDF_PATH = "input/affidavit.pdf"

PAN_REGEX = r"[A-Z]{5}[0-9]{4}[A-Z]"

# =====================================================
# OCR FUNCTION
# =====================================================

def run_azure_ocr(pdf_path):
    client = DocumentAnalysisClient(
        endpoint=AZURE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_KEY)
    )

    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document(
            model_id="prebuilt-document",
            document=f
        )

    result = poller.result()

    full_text = ""
    tables_data = []

    # ---------- TEXT EXTRACTION ----------
    for page in result.pages:
        for line in page.lines:
            if line.content:
                full_text += line.content.strip() + "\n"

    # ---------- TABLE EXTRACTION ----------
    for table in result.tables:
        table_rows = []
        for cell in table.cells:
            table_rows.append({
                "row": cell.row_index,
                "col": cell.column_index,
                "text": cell.content.strip() if cell.content else ""
            })
        tables_data.append(table_rows)

    return full_text, tables_data


# =====================================================
# PAN CONFIDENCE MATRIX (UPDATED)
# =====================================================

def pan_confidence_matrix(pan_from_table, pan_from_text):
    if pan_from_table:
        return 0.85, "PAN extracted from table cell"
    if pan_from_text:
        return 0.7, "PAN extracted from OCR text (fallback)"
    return 0.0, "PAN not detected"


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    text, tables = run_azure_ocr(PDF_PATH)

    # ---------- SAVE OUTPUTS ----------
    with open("azure_ocr_text.txt", "w", encoding="utf-8") as f:
        f.write(text)

    with open("azure_tables.txt", "w", encoding="utf-8") as f:
        for table in tables:
            for cell in table:
                f.write(str(cell) + "\n")
            f.write("\n--- TABLE END ---\n")

    # ---------- PAN DETECTION (ROBUST) ----------
    pan_from_table = None

    for table in tables:
        for cell in table:
            if re.fullmatch(PAN_REGEX, cell["text"]):
                pan_from_table = cell["text"]
                break
        if pan_from_table:
            break

    # ---------- OCR TEXT FALLBACK ----------
    pan_from_text = None
    text_upper = text.upper().replace(" ", "")
    pans = re.findall(PAN_REGEX, text_upper)
    if pans:
        pan_from_text = pans[0]

    # ---------- CONFIDENCE ----------
    confidence, reason = pan_confidence_matrix(
        pan_from_table,
        pan_from_text
    )

    print("Azure OCR completed successfully.")
    print("PAN (table):", pan_from_table)
    print("PAN (text):", pan_from_text)
    print("PAN Confidence:", confidence)
    print("Confidence Reason:", reason)

with open("azure_pan.json", "w", encoding="utf-8") as f:
    json.dump({
        "pan": pan_from_table or pan_from_text,
        "confidence": confidence,
        "reason": reason
    }, f, ensure_ascii=False, indent=2)