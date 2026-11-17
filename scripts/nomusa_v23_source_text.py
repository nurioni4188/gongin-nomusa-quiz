"""Official question-paper text per source file: PDF text layer, Tesseract(kor) OCR for image-only
pages (cached by page-image SHA-256), or HWP 5.0 text. OCR text is noisy: use for matching only."""
from __future__ import annotations
import hashlib, json, os, re, subprocess, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HANGUL = re.compile(r"[가-힣]")

def _ocr_png(png: bytes) -> str:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "p.png"; p.write_bytes(png)
        env = dict(os.environ, OMP_THREAD_LIMIT="1")
        r = subprocess.run(["tesseract", str(p), "stdout", "-l", "kor", "--psm", "6"],
                           capture_output=True, text=True, timeout=600, env=env)
        return r.stdout

def pdf_pages(path: Path, cache: dict, allow_ocr=True, on_page=None, force_ocr=False):
    import fitz
    doc = fitz.open(path); pages = []; todo = []
    for i in range(len(doc)):
        t = doc.load_page(i).get_text("text") or ""
        if len(HANGUL.findall(t)) >= 30 and not force_ocr:
            pages.append({"page": i + 1, "method": "PDF_TEXT_LAYER", "text": t}); continue
        png = doc.load_page(i).get_pixmap(matrix=fitz.Matrix(200 / 72, 200 / 72), alpha=False).tobytes("png")
        key = hashlib.sha256(png).hexdigest()
        pages.append({"page": i + 1, "method": "TESSERACT_KOR_OCR", "imageSha256": key, "text": cache.get(key)})
        if key not in cache: todo.append((len(pages) - 1, key, png))
    if todo and allow_ocr:
        with ThreadPoolExecutor(max(1, os.cpu_count() or 1)) as ex:
            for (idx, key, _), txt in zip(todo, ex.map(lambda x: _ocr_png(x[2]), todo)):
                cache[key] = txt; pages[idx]["text"] = txt
                if on_page: on_page()
    for p in pages:
        if p["text"] is None: p["text"] = ""; p["method"] = "HOLD_OCR_NOT_AVAILABLE"
    return pages

def source_text(path: Path, cache: dict, allow_ocr=True, on_page=None, force_ocr=False):
    if path.suffix.lower() == ".hwp":
        import sys; sys.path.insert(0, str(Path(__file__).parent))
        from nomusa_v23_hwp_text import hwp_text
        return [{"page": 1, "method": "HWP5_DISTRIBUTION_DOC_DECRYPTED_TEXT", "text": hwp_text(path)}]
    return pdf_pages(path, cache, allow_ocr, on_page, force_ocr)
