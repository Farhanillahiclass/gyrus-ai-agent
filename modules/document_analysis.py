"""
document_analysis.py — read a PDF or image file and let the AI brain answer
questions about it / summarize it. Text extraction is fully local (pypdf for
PDFs, vision.py's OCR for images) — only the final summarization step calls
the configured AI brain.
"""

from pathlib import Path


def extract_text(path: str, max_chars: int = 6000) -> str:
    p = Path(path).expanduser()
    if not p.exists():
        return f"__ERROR__: File not found: {p}"

    ext = p.suffix.lower()
    if ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(str(p))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if not text.strip():
                return "__ERROR__: No extractable text — this PDF may be a scanned image; try the OCR path instead."
            return text[:max_chars]
        except Exception as e:
            return f"__ERROR__: Could not read PDF: {e}"

    if ext in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
        from modules import vision
        return vision.read_text_from_image(str(p))[:max_chars]

    try:
        return p.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except Exception as e:
        return f"__ERROR__: Unsupported file type or read error: {e}"


def analyze_document(path: str, question: str, ask_fn) -> str:
    """
    question: what to do with the document — "summarize this", "what are the
    key points", "extract all dates mentioned", etc. Pass a generic
    "summarize this document" if the user didn't specify.
    """
    content = extract_text(path)
    if content.startswith("__ERROR__"):
        return content.replace("__ERROR__: ", "")

    prompt = f"Here is the content of a document:\n\n{content}\n\nTask: {question}\n\nReply in Urdu+English mix, clearly organized."
    return ask_fn(prompt)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(extract_text(sys.argv[1])[:500])
