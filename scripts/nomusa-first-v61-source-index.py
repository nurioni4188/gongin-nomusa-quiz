#!/usr/bin/env python3
"""Index official first-stage PDF attachments for the isolated review viewer.

Pass a directory of verified Q-Net downloads named article-attachment.pdf and,
optionally, per-PDF OCR pages named article-attachment-NN.txt. OCR matches
identify candidate pages only. The original PDF remains the source.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlencode

BOOKLETS = {
    (2014, "A", "management"): (5098604, 2089747),
    (2014, "B", "management"): (5098605, 2089749),
    (2014, "A", "economics"): (5098606, 2089750),
    (2014, "B", "economics"): (5098608, 2089753),
    (2020, "A", "management"): (5207203, 2194957),
    (2020, "B", "management"): (5207203, 2194958),
    (2020, "A", "economics"): (5207202, 2194955),
    (2020, "B", "economics"): (5207202, 2194956),
    (2021, "A", "management"): (5208526, 2199124),
    (2021, "B", "management"): (5208526, 2199125),
    (2021, "A", "economics"): (5208528, 2199132),
    (2021, "B", "economics"): (5208528, 2199133),
}
ANSWERS = {
    (2014, "A"): (5100802, 2091154, "8db082443b2d2d7ecc93baf4ac813184852bca3ab48700f887b16cf612bed3be"),
    (2014, "B"): (5100803, 2091155, "9aa4816c32fab80ddaefba8f32c61ff5c17617ad263a97f3668264dcf3bce184"),
    (2020, "AB"): (5207683, 2196321, "cd2db026287beee6869cd53c4c37bcd1dcda1a766a7239c780b0f931d1adc51b"),
    (2021, "AB"): (5209101, 2200446, "2116f86bd664e73f8c02051ef5528f4978504d60a6f24e98b16b1118d579b2ad"),
}
QNET = "https://www.q-net.or.kr/cst003.do"
QUESTION = re.compile(r"(?m)^ *([1-9][0-9]{0,2})[.．]\s")
SUBJECTS = ("labor1", "labor2", "civil", "social", "economics", "management")


def source_file(directory, article, attachment, answer=False):
    path = directory / f"{article}-{attachment}.pdf"
    data = path.read_bytes()
    if not data.startswith(b"%PDF-"):
        raise ValueError(f"Invalid PDF: {path}")
    pages = subprocess.check_output(["pdfinfo", path], text=True)
    menu = "10" if answer else "09"
    html = (directory / f"{article}.html").read_text()
    attachments = {
        int(number): (file_path, name)
        for file_path, name, number in
        re.findall(r"fileDown\('([^']+)', '([^']+)', '([^']+)'\)", html)
    }
    file_path, name = attachments[attachment]
    download = QNET + "?" + urlencode({
        "id": "cst00302s01", "gSite": "L", "gId": "05", "fileCode": "R001",
        "filePath": file_path, "fileName": name, "fileSeq": attachment, "artlSeq": article, "href": 0,
    })
    return path, {
        "article": article,
        "attachment": attachment,
        "publisher": "한국산업인력공단 Q-Net",
        "filename": name,
        "download": download,
        "notice": f"{QNET}?artlSeq={article}&boardId=Q004&gId=05&gSite=L&id=cst00302&menuType=cst003{menu}",
        "sha256": hashlib.sha256(data).hexdigest(),
        "pdfPages": int(re.search(r"(?m)^Pages:\s+(\d+)$", pages)[1]),
    }


def question_pages(path, doc, form, year, ocr_dir):
    source = subprocess.check_output(["pdftotext", "-layout", path, "-"], text=True)
    pages = source.split("\f")[:doc["pdfPages"]]
    matches = defaultdict(list)
    bodies = []
    ocr_numbers = []
    for index, page in enumerate(pages, 1):
        if year == 2014:
            footer = re.search(rf"(?m)^\s*{form}형\s*-\s*{doc['pdfPages']}\s*-\s*(\d+)\s*$", page)
            if footer is None or int(footer[1]) != index:
                continue
            page = page[:footer.start()]
            bodies.append((index, page))
        else:
            ocr = ocr_dir / f"{path.stem}-{index:02}.txt" if ocr_dir else None
            if not ocr or not ocr.is_file():
                continue
            page = ocr.read_text()
            footer = re.search(r"\(\s*\d{2}\s*[-~–]\s*(\d{1,2})\s*\)?\s*$", page)
            if footer is None:
                continue
            printed = int(footer[1])
            # Only the 2020 attachments have an unnumbered cover.
            if printed != index - (year == 2020):
                continue
            for match in QUESTION.finditer(page[:footer.start()]):
                number = int(match[1])
                if number <= 125:
                    ocr_numbers.append((number, index, printed))

    if ocr_numbers:
        for number, index, printed in unambiguous_sequence(ocr_numbers):
            matches[number].append((index, printed, "OCR_PAGE_CANDIDATE"))
    if year == 2014:
        text = "\f\n".join(body for _, body in bodies)
        numbers = list(re.finditer(r"(?m)^([1-9][0-9]{0,2})[.．]\s", text))
        if [int(match[1]) for match in numbers] != list(range(1, 126)):
            raise ValueError(f"Unexpected question sequence: {path}")
        for i, match in enumerate(numbers):
            end = numbers[i + 1].start() if i + 1 < len(numbers) else len(text)
            block = text[match.end():end]
            markers = [ch for ch in block if ch in "①②③④⑤"]
            start_page_index = text.count("\f", 0, match.start())
            end_page_index = start_page_index + block.rstrip().count("\f")
            page = bodies[start_page_index][0]
            last = bodies[end_page_index][0]
            status = "TEXT_AND_FIVE_MARKERS" if markers == list("①②③④⑤") else "TEXT_PAGE_ONLY"
            matches[int(match[1])].append((page, page, status, last))
    return matches


def unambiguous_sequence(candidates):
    """Keep positions shared by every longest in-order sequence of question numbers."""
    numbers = [entry[0] for entry in candidates]
    before = [1] * len(numbers)
    after = [1] * len(numbers)
    for i, number in enumerate(numbers):
        before[i] += max((before[j] for j in range(i) if numbers[j] < number), default=0)
    for i in range(len(numbers) - 1, -1, -1):
        after[i] += max((after[j] for j in range(i + 1, len(numbers))
                         if numbers[i] < numbers[j]), default=0)
    length = max(before)
    positions = defaultdict(set)
    for entry, prefix, suffix in zip(candidates, before, after, strict=True):
        if prefix + suffix - 1 == length:
            positions[prefix].add(entry)
    return [next(iter(entries)) for entries in positions.values() if len(entries) == 1]


def build(pdf_dir, ocr_dir):
    documents, indexed, records, answer_files = {}, {}, {}, {}
    for (year, form, optional), (article, attachment) in BOOKLETS.items():
        name = f"{year}-{form}-{optional}"
        path, doc = source_file(pdf_dir, article, attachment)
        documents[name] = dict(doc, year=year, form=form, elective=optional)
        indexed[name] = question_pages(path, doc, form, year, ocr_dir)
    for (year, form), (article, attachment, expected) in ANSWERS.items():
        _, doc = source_file(pdf_dir, article, attachment, answer=True)
        if doc["sha256"] != expected:
            raise ValueError(f"Final answer PDF differs from the V4 ledger: {year}-{form}")
        answer_files[f"{year}-{form}"] = doc

    for year in (2014, 2020, 2021):
        for form in ("A", "B"):
            for subject_index, subject in enumerate(SUBJECTS):
                optional = "economics" if subject == "economics" else "management"
                source = f"{year}-{form}-{optional}"
                start = 1 + 25 * min(subject_index, 4)
                for number in range(start, start + 25):
                    row_id = f"legacy1-{year}-{form}-{subject}-{number:03}"
                    answer = f"{year}-{form if year == 2014 else 'AB'}"
                    answer_page = 2 if year in (2020, 2021) and form == "B" else 1
                    if answer_page > answer_files[answer]["pdfPages"]:
                        raise ValueError(f"Answer page outside document: {row_id}")
                    row = {"source": source, "answerSource": answer, "answerPdfPage": answer_page,
                           "status": "BOOKLET_LINKED_PAGE_HOLD"}
                    candidates = indexed[source].get(number, [])
                    if year != 2014 and subject_index < 4 and len(candidates) != 1:
                        alternate = f"{year}-{form}-economics"
                        other_candidates = indexed[alternate].get(number, [])
                        if len(other_candidates) == 1:
                            row["source"] = alternate
                            candidates = other_candidates
                    if len(candidates) == 1:
                        page, printed, status, *last = candidates[0]
                        row.update(pdfPage=page, printedPage=printed, status=status)
                        if last and last[0] != page:
                            row["pdfLastPage"] = last[0]
                    records[row_id] = row

    return {
        "schema": "nomusa-first-v61-qnet-source-index/1",
        "documents": documents,
        "answerDocuments": answer_files,
        "records": records,
        "counts": Counter(row["status"] for row in records.values()),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_dir", type=Path)
    parser.add_argument("--ocr-dir", type=Path)
    args = parser.parse_args()
    print("window.NOMUSA_FIRST_V61_SOURCES = " +
          json.dumps(build(args.pdf_dir, args.ocr_dir), ensure_ascii=False, separators=(",", ":")) + ";")
