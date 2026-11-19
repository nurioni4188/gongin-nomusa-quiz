#!/usr/bin/env python3
"""Build the 2008 A practice bank from the user-supplied HWP and its reviewed key."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

MARKERS = "①②③④⑤"
# Numerals read from the embedded bitmap of the supplied final answer HWP.
SUBJECTS = (
    ("labor1", "노동법(1)", "1435231315541352542424323"),
    ("labor2", "노동법(2)", "3215255143114514324523234"),
    ("economics", "경제학원론", "2325145132543415334124152"),
    ("civil", "민법", "3354435435123221452351125"),
    ("english", "영어", "5312424255313415221342143"),
)
SOURCE = "https://q-net.or.kr/cst006.do?artlSeq=5011154&brdId=Q006&code=1204&gSite=Q&id=cst00602"


def extract(path, ledger):
    text = subprocess.check_output(["hwp5txt", str(path)], text=True)
    questions = list(re.finditer(r"(?m)^[ \t]*(\d{1,3})\.[ \t]+(?=\S)", text))
    if [int(m[1]) for m in questions] != list(range(1, 26)) * len(SUBJECTS):
        raise ValueError("Unexpected question sequence for the five 2008 A subjects")
    previous = {
        r["id"]: r["answers"] for r in ledger["records"] if r["year"] == 2008 and r["type"] == "A"
    }
    expected = {
        f"legacy1-2008-A-{code}-{i + 1:03}": [int(answer)]
        for code, _, answers in SUBJECTS for i, answer in enumerate(answers)
    }
    if previous != expected:
        raise ValueError("The audit ledger and the final answer image differ")
    included, held = [], {}
    for i, question in enumerate(questions):
        code, subject, _ = SUBJECTS[i // 25]
        number = int(question[1])
        key = f"legacy1-2008-A-{code}-{number:03}"
        end = questions[i + 1].start() if i + 1 < len(questions) else len(text)
        block = text[question.end():end].strip()
        # At a subject boundary the standalone extraction table belongs to the next header.
        if number == 25 and i < len(questions) - 1:
            block = re.sub(r"\n\s*<표>\s*$", "", block)
        parts = re.split(f"([{MARKERS}])", block)
        if code == "english":
            held[key] = "PASSAGE_AND_TYPOGRAPHY_REVIEW"
        elif re.search(r"<(?:그림|표|수식)>|[\ufffd\ue000-\uf8ff]", block):
            held[key] = "ORIGINAL_LAYOUT_REQUIRED"
        elif parts[1::2] != list(MARKERS) or any(not part.strip() for part in parts[::2]):
            held[key] = "CHOICE_SEQUENCE_REVIEW"
        else:
            included.append({"k": key, "y": 2008, "r": 17, "form": "A", "s": subject, "n": number,
                             "q": parts[0].strip(), "o": [p.strip() for p in parts[2::2]],
                             "a": expected[key], "t": True, "src": path.name, "sourceUrl": SOURCE})
    return included, held


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("question_hwp", type=Path)
    parser.add_argument("answer_hwp", type=Path)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    bank, hold = extract(args.question_hwp, json.loads(args.ledger.read_text()))
    args.output.write_text("window.NOMUSA_FIRST_2008 = " +
                           json.dumps(bank, ensure_ascii=False, separators=(",", ":")) + ";\n")
    args.report.write_text(json.dumps({
        "year": 2008, "round": 17, "booklet": "A", "originalQuestions": 125,
        "linkedAnswerValues": 125, "answerMethod": "Direct reading of final HWP bitmap compared with previous review ledger",
        "practiceQuestions": len(bank), "bySubject": Counter(q["s"] for q in bank),
        "held": hold, "officialQuestionNotice": SOURCE,
        "sourceSHA256": {str(f.name): hashlib.sha256(f.read_bytes()).hexdigest()
                         for f in (args.question_hwp, args.answer_hwp)},
    }, indent=2, ensure_ascii=False) + "\n")
