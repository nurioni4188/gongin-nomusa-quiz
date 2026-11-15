#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Safely split 2013/2014 essay booklet pages into 38 big-question children.

Reads original repository documents. Does not modify 181 legacy parents, RC35
question identifiers, localStorage keys, GitHub main, or Vercel deployments.
Requires Python >= 3.10, Node.js, and pymupdf. No AI API/token required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

import pymupdf

REPO_FILES = (
    "rc27_essay_catalog.js",
    "second/archive_2013_2021.js",
    "second/legacy_2007_2012_source_only.js",
)
PARENT_PATTERN = re.compile(r"(?m)^[ \t]*([1-9])\s*\.[ \t]+")
POINT_PATTERN = re.compile(r"\(\s*(\d{1,2})\s*점\s*\)")
VERSION = "2026-11-15"
EXPECTED = {2013: 19, 2014: 19}

# Running repository JS inside node's built-in vm is required because the
# archive appends source-only parents to window.N27_CATALOG at load time.
NODE_SOURCE = r"""
const fs = require('fs'), vm = require('vm');
const context = vm.createContext({window:{}});
for (const name of [
  'rc27_essay_catalog.js',
  'second/archive_2013_2021.js',
  'second/legacy_2007_2012_source_only.js'
]) {
  vm.runInContext(fs.readFileSync(name, 'utf8'), context, {filename:name});
}
process.stdout.write(JSON.stringify(context.window.N27_CATALOG.items));
"""


def source_catalog(root: Path) -> list[dict]:
    for name in REPO_FILES:
        if not (root / name).is_file():
            raise RuntimeError(f"Missing trusted source: {name}")
    result = subprocess.run(
        ["node", "-e", NODE_SOURCE], cwd=root, check=True,
        capture_output=True, text=True, encoding="utf-8",
    )
    rows = json.loads(result.stdout)
    ids = [row["id"] for row in rows]
    if len(rows) != 309 or len(set(ids)) != 309:
        raise RuntimeError(
            f"Unexpected base catalog: {len(rows)} records; "
            f"{len(set(ids))} unique IDs (expected 309)"
        )
    original = [r for r in rows if r.get("sourceOnly")]
    if len(original) != 181:
        raise RuntimeError(f"Unexpected legacy source inventory: {len(original)} (expected 181)")
    return rows


def split_parent(parent: dict, root: Path) -> tuple[list[dict], dict]:
    parent_id = parent["id"]
    year = int(parent["year"])
    path = root / parent["pdfPath"]
    if not path.is_file():
        raise RuntimeError(f"{parent_id}: missing original PDF: {path}")

    page_index = int(parent["pdfPage"]) - 1
    with pymupdf.open(path) as document:
        if not (0 <= page_index < len(document)):
            raise RuntimeError(f"{parent_id}: invalid PDF page {page_index + 1}")
        pdf_text = document[page_index].get_text("text")
        page_count = len(document)
    if len(pdf_text) < 60:
        raise RuntimeError(f"{parent_id}: original PDF page has insufficient embedded text")

    raw = parent["sourceText"]
    matches = list(PARENT_PATTERN.finditer(raw))
    expected_count = 2 if parent_id.endswith(("_p1", "_p2")) else 3
    numbers = [int(m.group(1)) for m in matches]
    if numbers != list(range(1, expected_count + 1)):
        raise RuntimeError(
            f"{parent_id}: expected questions 1..{expected_count}, found {numbers}"
        )

    # PDF numbers may appear on separate lines in these two original books.
    found_pdf_numbers = [
        int(x) for x in re.findall(r"(?m)^\s*([1-3])\s*\.\s*", pdf_text)
    ]
    for q in numbers:
        if q not in found_pdf_numbers:
            raise RuntimeError(
                f"{parent_id}: original PDF page does not expose question {q}"
            )

    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    children = []
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(raw)
        block = raw[match.start():end].strip()
        point = POINT_PATTERN.search(block)
        if not point:
            raise RuntimeError(
                f"{parent_id} question {numbers[idx]}: main-question points missing"
            )
        points = int(point.group(1))
        if points not in (25, 50):
            raise RuntimeError(
                f"{parent_id} question {numbers[idx]}: unexpected {points} points"
            )
        child_id = f"{parent_id}_q{numbers[idx]}"
        children.append({
            "id": child_id,
            "parentId": parent_id,
            "year": year,
            "subject": parent["subject"],
            "questionNo": numbers[idx],
            "topic": f"제{numbers[idx]}문 · {points}점 · 원문 분리",
            "points": points,
            "sourceText": block,
            "sourceOnly": True,
            "pdfPath": parent["pdfPath"],
            "pdfPage": int(parent["pdfPage"]),
            "pdfPageVerification": "PDF_TEXT_QUESTION_NUMBER_CHECKED",
            "status": "SOURCE_TEXT_SPLIT_POINTS_CHECKED_CONTENT_HOLD",
            "basis": (
                f"{year}년 원본 PDF {int(parent['pdfPage'])}쪽과 과목별 "
                "원장에 있는 문제번호·대문항 배점 대조. "
                "지문·수식·법률근거의 독립 최종 승인은 HOLD"
            ),
            "sourcePdfSha256": sha,
            "originalQuestionIdPreserved": True,
            "draftApproval": "HOLD",
            "scoringApproved": False,
        })
    expected_total = 75 if expected_count == 2 else 100
    total_points = sum(c["points"] for c in children)
    if total_points != expected_total:
        raise RuntimeError(
            f"{parent_id}: sum of major points is {total_points}, "
            f"expected {expected_total}"
        )
    return children, {
        "parentId": parent_id,
        "sourcePdf": parent["pdfPath"],
        "sourcePdfSha256": sha,
        "pdfPage": int(parent["pdfPage"]),
        "documentPages": page_count,
        "questionNumbersInPdfText": found_pdf_numbers,
        "children": [c["id"] for c in children],
        "points": [c["points"] for c in children],
        "totalPoints": total_points,
        "pageVerifiedBy": "ORIGINAL_PDF_EMBEDDED_TEXT_AND_CATALOG_TRANSCRIPTION",
        "fullStemVisualReview": "HOLD",
        "finalAnswerApproval": "HOLD",
    }


def make_outputs(root: Path, check_only: bool) -> dict:
    rows = source_catalog(root)
    legacy = [r for r in rows if r.get("sourceOnly")]
    parents = sorted(
        (r for r in legacy if r["year"] in EXPECTED),
        key=lambda r: (r["year"], r["pdfPage"]),
    )
    if len(parents) != 14:
        raise RuntimeError(f"Expected 14 historical parents; got {len(parents)}")

    children: list[dict] = []
    audits = []
    for parent in parents:
        new, audit = split_parent(parent, root)
        children.extend(new)
        audits.append(audit)

    counts = defaultdict(int)
    for item in children:
        counts[item["year"]] += 1
    if dict(counts) != EXPECTED or len(children) != 38:
        raise RuntimeError(f"Unexpected 38-question split: {dict(counts)}")

    parent_ids = {r["id"] for r in rows}
    child_ids = [c["id"] for c in children]
    if parent_ids.intersection(child_ids) or len(set(child_ids)) != 38:
        raise RuntimeError("Child IDs collide with existing 309 source IDs")

    parent_map = {r["parentId"]: r for r in audits}
    ledger = []
    for row in sorted(legacy, key=lambda r: (r["year"], r["subject"], r["id"])):
        linked = parent_map.get(row["id"])
        ledger.append({
            "id": row["id"],
            "year": row["year"],
            "subject": row["subject"],
            "sourceOnly": True,
            "sourceTextLen": len(row["sourceText"]),
            "pdfPath": row.get("pdfPath"),
            "pdfPage": row.get("pdfPage"),
            "children": linked["children"] if linked else [],
            "sourceStatus": (
                "SPLIT_38_QUESTION_CHILDREN_CONTENT_HOLD"
                if linked else
                "SOURCE_NEEDS_ACCURACY_AND_ANSWER_REVIEW"
            ),
            "scoringApproved": False,
        })

    manifest = {
        "schema": "nomusa-essay-2013-2014-38-and-181-parent-ledger/1",
        "version": VERSION,
        "repository": "nurioni4188/gongin-nomusa-quiz",
        "sourceCatalogCount": 309,
        "sourceLegacyParentCount": 181,
        "sourceHistoricalBundleCount": 14,
        "extractedMainQuestionCount": 38,
        "yearCounts": dict(counts),
        "childrenAreAdditional": True,
        "legacyParentsRemainUnchanged": True,
        "original309QuestionIdsRemainUnchanged": True,
        "newChildIdsDistinct": True,
        "existingStorageKeysRemainUnchanged": True,
        "rc35ScoringApproved": False,
        "contentApproval": "HOLD",
        "sources": audits,
        "legacyLedger181": ledger,
    }

    js_obj = {
        "schema": "nomusa-essay-2013-2014-38-questions/1",
        "version": VERSION,
        "notes": (
            "38 original-text children of 14 preserved source bundles; "
            "PDF headings and main-question points verified; answers HOLD"
        ),
        "items": children,
        "original181Preserved": True,
        "noScoringApproval": True,
    }
    js_contents = (
        "// Generated by scripts/nomusa_split_38_181.py; do not hand-edit.\n"
        "// Source-only question children. No legal/academic model-answer approval.\n"
        "window.NOMUSA_2013_2014_SPLIT_V1 = "
        + json.dumps(js_obj, ensure_ascii=False, separators=(",", ":"))
        + ";\n"
    )
    ledger_contents = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    targets = {
        root / "second/historical-2013-2014-38.js": js_contents,
        root / "review/NOMUSA_SECOND_2013_2014_38_AND_181_LEDGER_20261115.json":
            ledger_contents,
    }
    changes = []
    for path, content in targets.items():
        if path.exists() and path.read_text(encoding="utf-8") == content:
            changes.append({"path": str(path.relative_to(root)), "status": "UNCHANGED"})
        else:
            changes.append({
                "path": str(path.relative_to(root)),
                "status": "DIFF_IN_CHECK_MODE" if check_only else "WRITTEN",
            })
            if not check_only:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8", newline="\n")
    return {
        "status": "PASS" if not check_only or all(
            x["status"] == "UNCHANGED" for x in changes
        ) else "HOLD_FILES_NOT_IN_SYNC",
        "years": dict(counts),
        "sourceParents": len(legacy),
        "historicalBundles": len(parents),
        "individualChildren": len(children),
        "parentIdsPreserved": True,
        "points": {str(y): {
            "50pt": sum(c["points"] == 50 for c in children if c["year"] == y),
            "25pt": sum(c["points"] == 25 for c in children if c["year"] == y),
        } for y in EXPECTED},
        "fileResults": changes,
        "sourceAndContentApproval": "HOLD",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="Verify generated outputs only")
    args = parser.parse_args()
    result = make_outputs(args.repo.resolve(), args.check)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
