#!/usr/bin/env python3
"""V19: read-only 328-essay priority audit from Chromium-exported JSON."""
import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

YEARS = set(range(2007, 2027))
EVIDENCE = "review/NOMUSA_V18_2019_2020_26_POINT_EVIDENCE_20261117.json"

def classify(row, evidence):
    p = int(row["points"])
    goal = {50: 4000, 25: 2000}.get(p)
    n = len(row["detailed"])
    return {
        "id": row["id"], "year": int(row["year"]), "subject": row.get("subject", ""),
        "points": p, "detailChars": n, "compressedChars": len(row["compressed"]),
        "proxyMinimumChars": goal, "proxyDeficitChars": max(0, goal - n) if goal else 0,
        "evidence2019_2020": row["id"] in evidence,
        "source": "REVIEW_REQUIRED", "academicLegal": "HOLD",
        "handwritingMeasured": False, "independentApproval": "HOLD"
    }

def audit(root, expected, baseline):
    folder = root / "review-artifacts"
    files = sorted(folder.glob("nomusa_*_rendered*.json"))
    if len(files) != 20:
        raise ValueError("HOLD_BROWSER_OUTPUTS_EXPECT_20_GOT_%d" % len(files))
    original = []
    count = Counter()
    sha = {}
    for file in files:
        match = re.match(r"nomusa_(20\d\d)_", file.name)
        if not match:
            raise ValueError("HOLD_UNKNOWN_FILE_" + file.name)
        year = int(match.group(1))
        data = json.loads(file.read_text(encoding="utf-8"))
        if int(data.get("year", year)) != year or not isinstance(data.get("rows"), list) or year in count:
            raise ValueError("HOLD_YEAR_SCHEMA_" + str(year))
        count[year] = len(data["rows"])
        sha[file.name] = hashlib.sha256(file.read_bytes()).hexdigest()
        for row in data["rows"]:
            if int(row.get("year", -1)) != year:
                raise ValueError("HOLD_YEAR_CONFLICT_" + str(row.get("id")))
            original.append(row)
    if set(count) != YEARS:
        raise ValueError("HOLD_YEAR_COVERAGE")
    ids = [r.get("id") for r in original]
    if len(ids) != expected or any(not s for s in ids) or len(ids) != len(set(ids)):
        raise ValueError("HOLD_COUNT_OR_DUPLICATE_ID")
    if count[2022] != 19:
        raise ValueError("HOLD_2022_19_BASELINE")
    evidence_path = root / EVIDENCE
    proof = json.loads(evidence_path.read_text(encoding="utf-8"))
    proofs = proof["rows"]
    if proof["count"] != 26 or len(proofs) != 26 or len({p["id"] for p in proofs}) != 26:
        raise ValueError("HOLD_26_EVIDENCES")
    proof_ids = {p["id"] for p in proofs}
    byid = {r["id"]: r for r in original}
    for p in proofs:
        q = byid.get(p["id"])
        if not q or int(q["points"]) != p["points"] or int(q["year"]) != p["year"]:
            raise ValueError("HOLD_SCORE_EVIDENCE_CONFLICT_" + p["id"])
        if sum(int(s["points"]) for s in p["parts"]) != p["points"]:
            raise ValueError("HOLD_PROOF_PART_SUM_" + p["id"])
    for row in original:
        if not row.get("sourceText") or not row.get("detailed") or not row.get("compressed"):
            raise ValueError("HOLD_MISSING_TEXT_" + str(row.get("id")))
        if row.get("points") is None or int(row["points"]) <= 0:
            raise ValueError("HOLD_MISSING_POINTS_" + str(row["id"]))
        if row.get("scoringApproved"):
            raise ValueError("HOLD_UNEXPECTED_APPROVAL_" + str(row["id"]))
        parts = row.get("parts") or []
        if parts and all(s.get("points") is not None for s in parts):
            if sum(int(s["points"]) for s in parts) != int(row["points"]):
                raise ValueError("HOLD_PART_SUM_" + str(row["id"]))
    all_items = [classify(r, proof_ids) for r in original]
    priority = [r for r in all_items if r["proxyDeficitChars"] > 0]
    priority.sort(key=lambda r: (-r["points"], -r["proxyDeficitChars"], r["year"], r["id"]))
    n50 = sum(r["points"] == 50 for r in priority)
    n25 = sum(r["points"] == 25 for r in priority)
    status = "PASS_STRUCTURAL_AUDIT_CONTENT_HOLD" if len(priority) <= baseline else "HOLD_PROXY_COUNT_WORSE"
    v20 = [r for r in original if "## V20 원문 연동 심화논증" in r["detailed"]]
    if len(v20) != 88 or sum(int(r["points"]) == 50 for r in v20) != 32 or sum(int(r["points"]) == 25 for r in v20) != 56:
        raise ValueError("HOLD_V20_88_COVERAGE")
    summary = {
        "schema": "NOMUSA_V19_328/1", "status": status, "answers": len(all_items),
        "years": dict(sorted(count.items())), "verifiedPointEvidence": len(proof_ids),
        "priority": len(priority), "priority50": n50, "priority25": n25,
        "previousPrioritySnapshot": baseline,
        "v20SubstantiveDrafts": len(v20), "priorityReducedSinceV19": baseline - len(priority),
        "proxy": "50pt<4000 chars; 25pt<2000 chars; assumed 500 chars/page",
        "legalAcademicApproval": "HOLD", "handwrittenPageVerification": "HOLD",
        "year2022IndependentApproval": "HOLD_0_OF_19",
        "doesNotModify": ["main", "Production", "Preview", "source", "IDs", "storageKeys"],
        "inputSHA256": sha, "evidenceSHA256": hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    }
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "NOMUSA_V19_328_PRIORITY_REPORT.json").write_text(
        json.dumps({"summary": summary, "priorityQueue": priority, "all": all_items},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cols = list(priority[0]) if priority else list(all_items[0])
    with (folder / "NOMUSA_V19_88_PRIORITY_QUEUE.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(priority)
    lines = [
        "# NOMUSA V19 — 328개 답안 자동 품질검토", "",
        "**%s** — 328개 등록 / 프록시 분량 우선검토 %d개 (50점 %d, 25점 %d)" %
        (status, len(priority), n50, n25),
        "",
        "> 500자/장 환산은 컴퓨터 상의 위험 선별 기준이며 실제 필기·정답·법리 검증 아님.",
        "> 2022년 19개 독립승인 0. 수기장수·법령/판례/학술 원전·전문가 내용승인은 HOLD.",
        "", "| 순위 | ID | 연도 | 과목 | 배점 | 글자수 | 부족 프록시 글자수 |",
        "|---:|---|---:|---|---:|---:|---:|"]
    for i, r in enumerate(priority, 1):
        lines.append("| %d | %s | %d | %s | %d | %d | %d |" %
            (i, r["id"], r["year"], r["subject"].replace("|", "/"),
             r["points"], r["detailChars"], r["proxyDeficitChars"]))
    lines += ["", "## 추가 내용검증", "",
              "기출 원문/소문항→시험 당시 법령·판례 또는 학술 원전→논증/사안포섭→"
              "50점·25점 실제 필기장수/시간→독립 전문가 검토자·검토일·의견 순으로 확인한다.",
              "", "**최종승인 HOLD / 배포 없음**", ""]
    (folder / "NOMUSA_V19_328_PRIORITY_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    return summary

def test():
    item = {"id": "TEST", "year": 2022, "subject": "TEST", "points": 50,
            "detailed": "가"*3999, "compressed": "요약"}
    assert classify(item, set())["proxyDeficitChars"] == 1
    item["detailed"] += "가"
    assert classify(item, set())["proxyDeficitChars"] == 0
    item["points"] = 25; item["detailed"] = "가"*1999
    assert classify(item, set())["proxyDeficitChars"] == 1
    print("PASS_V19_SELF_TEST")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("root", nargs="?", default=".")
    p.add_argument("--expected-total", type=int, default=328)
    p.add_argument("--baseline", type=int, default=88)
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    try:
        if a.self_test: test()
        else:
            r = audit(Path(a.root), a.expected_total, a.baseline)
            print(json.dumps({k:r[k] for k in ("status", "answers", "priority", "priority50",
                                                 "priority25", "verifiedPointEvidence")},
                             ensure_ascii=False))
            if r["status"] != "PASS_STRUCTURAL_AUDIT_CONTENT_HOLD": sys.exit(2)
    except (ValueError, AssertionError, FileNotFoundError, KeyError, TypeError) as e:
        print("HOLD_V19: " + str(e), file=sys.stderr)
        sys.exit(2)
