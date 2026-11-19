#!/usr/bin/env python3
"""Import the text-layer Q-Net A-form booklets with checked numbering and answer identities."""
import argparse
from collections import Counter
import base64
import fitz
from html import escape
import hashlib
import json
from pathlib import Path
import re
import subprocess

SUBJECTS = ("노동법(1)", "노동법(2)", "민법", "사회보험법", "경제학원론", "경영학개론")
CODES = ("labor1", "labor2", "civil", "social", "economics", "management")
MARKERS = "①②③④⑤"
QUESTION = re.compile(r"(?m)^([1-9][0-9]{0,2})[.．](?:[ \t]+|(?=\n))")
KEY = (
    "42513 41235 41125 43214 53532",
    "52524 15451 24321 33431 43125",
    "44515 44532 51221 13452 32332",
    "23124 24525 24143 35351 41542",
    "25314 25334 21143 44135 24152",
    "54453 15123 32134 44521 32225",
)
BOOKLETS = {"management": "5098604-2089747.pdf", "economics": "5098606-2089750.pdf"}
ANSWER = "5100802-2091154.pdf"


def notice(article, answer=False):
    menu = "10" if answer else "09"
    return (f"https://www.q-net.or.kr/cst003.do?artlSeq={article}"
            f"&boardId=Q004&gId=05&gSite=L&id=cst00302&menuType=cst003{menu}")


def read_booklet(path, year):
    content = subprocess.check_output(["pdftotext", "-layout", path, "-"], text=True)
    pages = content.split("\f")
    if not pages[-1].strip():
        pages.pop()
    cleaned = []
    for page, text in enumerate(pages, 1):
        footer = rf"A형\s*-\s*{len(pages)}\s*-\s*{page}"
        if year == 2019:
            footer = rf"2019.*A형\s*\(\s*{len(pages)}\s*-\s*{page}\s*\)"
        foot = re.search(rf"(?m)^\s*{footer}\s*$", text)
        if not foot:
            raise ValueError(f"Invalid form or printed page: {path}:{page}")
        cleaned.append(text[:foot.start()])
    text = "\f\n".join(cleaned)
    questions = list(QUESTION.finditer(text))
    if [int(question[1]) for question in questions] != list(range(1, 126)):
        raise ValueError(f"Unexpected question sequence: {path}")
    result = {}
    for i, start in enumerate(questions):
        end = questions[i + 1].start() if i + 1 < len(questions) else len(text)
        body = text[start.end():end].rstrip().replace("\f", "\n")
        body = re.split(r"(?m)^\s*제\s*[1-5]\s*과\s*목\s*:", body)[0].rstrip()
        parts = re.split(f"([{MARKERS}])", body)
        result[i + 1] = (body, parts, text.count("\f", 0, start.start()) + 1)
    return result


def original_crop(pdf, page, number):
    with fitz.open(pdf) as doc:
        sheet = doc[page - 1]
        anchors = {}
        for block in sheet.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                value = "".join(span["text"] for span in line["spans"]).strip()
                match = re.match(r"^(\d{1,3})\.", value)
                if match and 54 < line["bbox"][0] < 68:
                    anchors[int(match[1])] = line["bbox"][1]
        if number not in anchors:
            raise ValueError(f"Question crop has no start anchor: {number}")
        end = anchors.get(number + 1, 796)
        if end <= anchors[number]:
            raise ValueError(f"Invalid question crop: {number}")
        crop = sheet.get_pixmap(matrix=fitz.Matrix(1.7, 1.7), colorspace=fitz.csGRAY,
                               clip=fitz.Rect(50, anchors[number] - 4, 551, end - 3))
        data = base64.b64encode(crop.tobytes("jpeg", jpg_quality=76)).decode("ascii")
        return f'<img src="data:image/jpeg;base64,{data}" alt="{number}번 원문 이미지">'

def generate(root, ledger, year):
    configs = {
        2014: (BOOKLETS, ANSWER, "8db082443b2d2d7ecc93baf4ac813184852bca3ab48700f887b16cf612bed3be",
               {"management": "5098604", "economics": "5098606"}, "5100802"),
        2017: ({"management": "2017-management.pdf", "economics": "2017-economics.pdf"},
               "5202226-2184843.hwp", "e9fed8b09db806d80325291c2e4110d5cfebaa6732c13f431eccf3982fabc537",
               {"management": "5201158", "economics": "5201158"}, "5202226"),
        2019: ({"management": "5205539-2190603.pdf", "economics": "5205539-2190604.pdf"},
               "5207682-2196320.pdf", "8fb66a2ad0cb0bcee0565b25efb28fa4cca90cabd44531eae5df45b198e0744e",
               {"management": "5205539", "economics": "5205539"}, "5207682"),
    }
    files, answer_file, reference, source_ids, answer_id = configs[year]
    answer_hash = hashlib.sha256((root / answer_file).read_bytes()).hexdigest()
    if answer_hash != reference:
        raise ValueError("Official answer attachment differs from the visually read reference")
    books = {subject: read_booklet(root / file, year) for subject, file in files.items()}
    historical = {r["id"]: r["answers"] for r in ledger if r["year"] == year and r["type"] == "A"}
    imported, held = [], {}
    for subject, name in enumerate(SUBJECTS):
        book = "economics" if subject == 4 else "management"
        for offset in range(25):
            number = min(subject, 4) * 25 + offset + 1
            key = f"legacy1-{year}-A-{CODES[subject]}-{number:03}"
            expected = [int(KEY[subject].replace(" ", "")[offset])] if year == 2014 else historical.get(key)
            if not expected or historical.get(key) != expected:
                held[key] = "ANSWER_MISMATCH"
                continue
            text, parts, page = books[book][number]
            if parts[1::2] != list(MARKERS) or any(not p.strip() for p in parts[::2]):
                held[key] = "CHOICE_SEQUENCE_REVIEW"
                continue
            layout = f"<pre>{number}. {escape(text)}</pre>"
            if re.search(r"[\u0000-\u0009\ufffd\ue000-\uf8ff]", text):
                if year != 2014 or book != "economics" or number not in {107, 112, 113, 115, 125}:
                    held[key] = "UNRECOGNIZED_SOURCE_CHARACTER"
                    continue
                layout = original_crop(root / files[book], page, number)
            # Inline diagrams or table geometry cannot be reconstructed from this text layer.
            if re.search(r"그래프|그림|다음\s*표|아래\s*표|위\s*표|➝|◯|▸", text):
                held[key] = "VISUAL_LAYOUT_REVIEW"
                continue
            imported.append({
                "k": key, "y": year, "r": year - 1991, "form": "A", "s": name, "n": number,
                "q": parts[0].strip(), "o": [p.strip() for p in parts[2::2]], "a": expected,
                "t": True, "paperHtml": layout,
                "sourceUrl": notice(source_ids[book]), "pg": [page],
                "answerSourceUrl": notice(answer_id, answer=True),
            })
    return imported, held, answer_hash


if __name__ == "__main__":
    arg = argparse.ArgumentParser()
    arg.add_argument("pdf_dir", type=Path)
    arg.add_argument("ledger", type=Path, help="JSON array of historical answer records")
    arg.add_argument("output", type=Path)
    arg.add_argument("--year", type=int, choices=(2014, 2017, 2019), default=2014)
    a = arg.parse_args()
    rows, held, answer_hash = generate(a.pdf_dir, json.loads(a.ledger.read_text()), a.year)
    a.output.write_text(f"window.NOMUSA_FIRST_{a.year} = " +
                        json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(json.dumps({"year": a.year, "form": "A", "questions": len(rows),
                      "bySubject": Counter(r["s"] for r in rows), "held": held,
                      "answerSHA256": answer_hash}, ensure_ascii=False, indent=2))
