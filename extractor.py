import random
import requests
import trafilatura
import config

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import pytesseract
    from pdf2image import convert_from_bytes
except ImportError:
    pytesseract = None
    convert_from_bytes = None


def _headers():
    return {"User-Agent": random.choice(config.USER_AGENTS)}


def fetch_url(url):
    try:
        resp = requests.get(url, headers=_headers(), timeout=20)
        resp.raise_for_status()
        return resp
    except Exception:
        return None


def extract_html(url):
    resp = fetch_url(url)
    if not resp:
        return None
    text = trafilatura.extract(resp.text, include_comments=False, favor_recall=True)
    if not text:
        return None
    meta = trafilatura.extract_metadata(resp.text)
    return {
        "title": meta.title if meta and meta.title else "",
        "author": meta.author if meta and meta.author else "",
        "published_date": meta.date if meta and meta.date else "",
        "text": text.strip(),
        "source_url": url,
    }


def extract_pdf_text(pdf_bytes):
    if not pdfplumber:
        return ""
    text = ""
    try:
        import io
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                t = page.extract_text() or ""
                text += t + "\n"
    except Exception:
        pass
    return text.strip()


def extract_pdf_ocr(pdf_bytes):
    """Fallback OCR for scanned PDFs (Hindi/Sanskrit/English)."""
    if not pytesseract or not convert_from_bytes:
        return ""
    text = ""
    try:
        images = convert_from_bytes(pdf_bytes)
        for img in images:
            text += pytesseract.image_to_string(img, lang=config.OCR_LANGUAGES) + "\n"
    except Exception:
        pass
    return text.strip()


def extract_pdf(url):
    resp = fetch_url(url)
    if not resp:
        return None
    text = extract_pdf_text(resp.content)
    if len(text.split()) < 30:  # likely scanned, try OCR
        ocr_text = extract_pdf_ocr(resp.content)
        if len(ocr_text) > len(text):
            text = ocr_text
    if not text:
        return None
    return {
        "title": "",
        "author": "",
        "published_date": "",
        "text": text,
        "source_url": url,
    }


def extract(url):
    if url.lower().endswith(".pdf"):
        return extract_pdf(url)
    return extract_html(url)
