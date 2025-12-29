import subprocess
import json
import re

OLLAMA_PATH = r"C:\Users\Sasmita\AppData\Local\Programs\Ollama\ollama.exe"
MODEL = "llama3:8b"


def extract_name_snippet(text):
    """
    Extract affidavit introduction region around 'मैं'
    Used ONLY for semantic grounding, not OCR accuracy.
    """
    match = re.search(r"मैं.{80,350}", text, flags=re.DOTALL)
    return match.group(0).strip() if match else None


def extract_name_with_llm(snippet):
    """
    Uses legal-semantic inference (NOT OCR reading).

    Returns:
    (full_name, father_or_spouse_name, confidence)

    IMPORTANT:
    - PAN, age, address are NOT inferred here
    - Output must be conservative and bounded
    """

    if not snippet:
        return None, None, 0.0

    # ⚠️ f-string SAFE prompt (escaped JSON braces)
    prompt = (
        "You are an expert system for interpreting Hindi legal affidavits.\n\n"
        "STRICT RULES:\n"
        "- OCR text may be noisy, unordered, or partially incorrect\n"
        "- Names may be handwritten\n"
        "- DO NOT guess or invent information\n"
        "- DO NOT output explanations\n"
        "- DO NOT infer PAN, age, address, or phone\n"
        "- If uncertain, return null\n\n"
        "LEGAL STRUCTURE:\n"
        "मैं <व्यक्ति का नाम> पुत्र / पत्नी / पुत्री <अभिभावक का नाम>\n\n"
        "TASK:\n"
        "Extract ONLY:\n"
        "1. full_name\n"
        "2. father_or_spouse_name\n\n"
        "OUTPUT FORMAT (STRICT JSON ONLY):\n"
        "{\n"
        '  "full_name": null,\n'
        '  "father_or_spouse_name": null,\n'
        '  "confidence": 0.0\n'
        "}\n\n"
        "TEXT:\n"
        f"{snippet}"
    )

    result = subprocess.run(
        [OLLAMA_PATH, "run", MODEL],
        input=prompt.encode("utf-8"),
        capture_output=True,
        timeout=120
    )

    raw_output = result.stdout.decode("utf-8", errors="ignore").strip()

    # ---------------- SAFE JSON EXTRACTION ----------------
    match = re.search(r"\{[\s\S]*\}", raw_output)
    if not match:
        return None, None, 0.0

    try:
        data = json.loads(match.group())

        full_name = data.get("full_name")
        parent = data.get("father_or_spouse_name")

        # ---------- Confidence bounding ----------
        base_conf = float(data.get("confidence", 0.0))

        if full_name and parent:
            confidence = min(base_conf, 0.6)
        elif full_name:
            confidence = min(base_conf, 0.5)
        else:
            confidence = 0.0

        return full_name, parent, confidence

    except Exception:
        return None, None, 0.0
