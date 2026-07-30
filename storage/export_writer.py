import csv
import os


def save_csv(entries, path):
    if not entries:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fieldnames = list(entries[0].keys())
    write_header = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for e in entries:
            writer.writerow(e)


def save_pdf(entries, path):
    try:
        from fpdf import FPDF
    except ImportError:
        return  # skip silently if fpdf2 not installed

    os.makedirs(os.path.dirname(path), exist_ok=True)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    for e in entries:
        pdf.set_font("Helvetica", "B", 13)
        pdf.multi_cell(0, 8, f"{e.get('title') or e['topic']} [{e['type']}]")
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 6, f"Source: {e['source_url']}")
        pdf.ln(2)
        pdf.set_font("Helvetica", size=11)
        # encode-safe for non-latin scripts is limited in core fpdf fonts
        safe_text = e["text"].encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe_text[:3000])
        pdf.ln(6)

    pdf.output(path)
