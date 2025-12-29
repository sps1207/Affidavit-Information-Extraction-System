import re
import ast

PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")

# =====================================================
# LOAD TABLES
# =====================================================

def load_tables(path="azure_tables.txt"):
    tables, current = [], []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "--- TABLE END ---":
                if current:
                    tables.append(current)
                current = []
            elif line.startswith("{"):
                current.append(ast.literal_eval(line))
    return tables

# =====================================================
# NAME + FATHER / SPOUSE EXTRACTION (BEST-EFFORT)
# =====================================================

def extract_name_and_parent(text):
    """
    Attempts to extract:
    - Full Name
    - Father / Spouse Name

    Returns:
    full_name, father_or_spouse_name, confidence, reason
    """

    # Normalize OCR noise
    clean = re.sub(r"\s+", " ", text)

    # Typical affidavit pattern:
    # "मैं <नाम> पुत्र/पत्नी <अभिभावक>"
    pattern = re.search(
        r"मैं\s+([^\d,।]{3,40})\s+(पुत्र|पत्नी|पुत्री)\s+([^\d,।]{3,40})",
        clean
    )

    if pattern:
        full_name = pattern.group(1).strip()
        parent = pattern.group(3).strip()
        return full_name, parent, 0.75, "Name and parent extracted from affidavit intro"

    # Fallback: only name after "मैं"
    fallback = re.search(r"मैं\s+([^\d,।]{3,40})", clean)
    if fallback:
        return fallback.group(1).strip(), None, 0.5, "Only name extracted; parent missing"

    return None, None, 0.0, "Name not reliably detected"


# =====================================================
# AGE
# =====================================================

def extract_age(text):
    m = re.search(r"आयु\s*(\d+)\s*वर्ष", text)
    if m:
        return int(m.group(1)), 0.85
    return None, 0.0


# =====================================================
# ADDRESS
# =====================================================

def extract_address(text):
    """
    Address often follows:
    'जो ... निवासी हूँ'
    """

    m = re.search(
        r"(जो|निवासी)\s+(.+?)(?:हूँ|हूं|,|\.)",
        text
    )
    if m:
        return m.group(2).strip(), 0.8

    return None, 0.0


# =====================================================
# MOBILE
# =====================================================

def extract_mobile(text):
    m = re.search(r"\b[6-9]\d{9}\b", text)
    if m:
        return m.group(), 0.75
    return None, 0.0
