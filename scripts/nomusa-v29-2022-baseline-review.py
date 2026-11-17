#!/usr/bin/env python3
"""V29 read-only 2022 pilot / 19-year QA, not legal/academic approval."""
import argparse
import csv
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

LEDGER = "review/NOMUSA_V23_VALIDATION_LEDGER.json"
V27 = "review/NOMUSA_V27_2022_PRIMARY_CONTENT_CROSSCHECK_20261118.json"
V28 = "review/NOMUSA_V28_2022_REMAINING_13_SOURCE_CROSSCHECK_20261118.json"
TIERS = ("P0", "P1", "P2", "P3")


def read(root, name):
    return json.loads((root / name).read_text(encoding="utf-8"))


def sha(row):
    return hashlib.sha256((row["sourceText"] + "\0" + row["detailed"] + "\0" +
                           row["compressed"]).encode("utf-8")).hexdigest()


def audit(root, use_rendered=False):
    ledger, v27, v28 = (read(root, x) for x in (LEDGER, V27, V28))
    original = ledger["rows"]
    s = ledger["summary"]
    assert len(original) == 328 and s["total"] == 328
    assert len({x["id"] for x in original}) == 328
    assert set(x["year"] for x in original) == set(range(2007, 2027))
    assert s["qnetOfficialByteIdentical"] == 328 and s["sourceVerifiedQuestion"] == 328
    assert s["storedQuestionIsSummary"] == 0 and s["independentExpertApproved"] == 0
    assert s["finalApproval"] == "HOLD (0/328)"
    source = {r["id"]: r for r in original}
    pilot = {r["id"] for r in original if r["year"] == 2022}
    v27_ids = {r["id"] for r in v27["checks"]}
    v28_ids = {r["id"] for r in v28["referenceChecks"]}
    assert len(pilot) == 19 and len(v27_ids) == 6 and len(v28_ids) == 13
    assert v27_ids.isdisjoint(v28_ids) and v27_ids | v28_ids == pilot
    assert v27["expertApproved"] == 0 and v28["independentHumanExpertsApproved"] == 0
    for r in original:
        assert r["source"]["qnetOfficialByteIdentical"] is True
        assert r["source"]["storedQuestionIsSummary"] is False
        assert r["verdicts"]["finalApproval"] == "HOLD"
        assert r["verdicts"]["expertApproval"] == "HOLD_EXPERT_APPROVAL"
    rendered = {}
    if use_rendered:
        paths = sorted((root / "review-artifacts").glob("nomusa_*_rendered*.json"))
        assert len(paths) == 20, "HOLD_RENDERED_20_FILES"
        for path in paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            for q in data["rows"]:
                assert q["id"] not in rendered
                rendered[q["id"]] = q
        assert set(rendered) == set(source), "HOLD_328_RENDERED_ID_MISMATCH"
        for id_, q in rendered.items():
            r = source[id_]
            assert sha(q) == r["textSHA256"], "HOLD_MANUSCRIPT_SHA_" + id_
            assert int(q["points"]) == int(r["points"])
            assert int(q["year"]) == int(r["year"])
            assert q["sourceText"] and q["detailed"] and q["compressed"]
            assert q.get("scoringApproved") is False
    median_by_points = {}
    if rendered:
        for points in (25, 50):
            pilot_len = [len(rendered[id_]["detailed"]) for id_ in pilot
                         if int(source[id_]["points"]) == points]
            if pilot_len:
                median_by_points[points] = statistics.median(pilot_len)
    records = []
    by_year = defaultdict(Counter)
    for r in original:
        id_, year = r["id"], int(r["year"])
        tier = r["reviewTierV21"].split("_", 1)[0]
        assert tier in TIERS
        row = rendered.get(id_)
        points = int(r["points"])
        chars = len(row["detailed"]) if row else None
        baseline = median_by_points.get(points)
        hold_word = bool(re.search(r"HOLD|미확인|검토\s*필요|원전\s*확인",
                                   row["detailed"], re.I)) if row else None
        case_ids = sorted({c["caseNo"] for c in r.get("caseCitations", [])
                           if c.get("caseNo")})
        rec = {
            "id": id_, "year": year, "subject": r["subject"],
            "points": points, "tier": tier, "textSHA256": r["textSHA256"],
            "sourceMatch": r["source"]["matchBand"],
            "detailedCharacters": chars,
            "compressedCharacters": len(row["compressed"]) if row else None,
            "2022PilotMedianCharactersForSamePoints": baseline,
            "relativeLengthToPilot": round(chars / baseline, 3) if chars is not None and baseline else None,
            "containsUnverifiedDraftWording": hold_word,
            "caseNumbersForFullTextCheck": case_ids,
            "academicPairsForOriginalTextCheck": r.get("academicPairs", []),
            "partialClaimEvidenceV27V28": year == 2022,
            "sourceLevelMatch": "V23_VERIFIED_QUESTION",
            "sameSubstantiveQualityAs2022": "NOT_ESTABLISHED",
            "independentContentApproval": "HOLD",
            "requiredReview": ("EXAM_TIME_LAW_CASE_FULL_TEXT_APPLICATION"
                               if "법" in r["subject"] or "쟁송" in r["subject"] or "소송" in r["subject"]
                               else "ACADEMIC_ORIGINAL_THEORY" if "인사노무" in r["subject"] or "조직" in r["subject"]
                               else "MATH_GRAPH_ASSUMPTIONS"),
        }
        by_year[year]["total"] += 1
        by_year[year][tier] += 1
        by_year[year]["MEDIUM"] += r["source"]["matchBand"] == "MEDIUM"
        if chars is not None:
            by_year[year]["renderedAndSHAEqual"] += 1
            by_year[year]["lowerThanPilotMedian"] += bool(baseline and chars < baseline)
        records.append(rec)
    sums = Counter(r["tier"] for r in records)
    assert [sums[t] for t in TIERS] == [19, 77, 35, 197]
    assert sum(c["MEDIUM"] for c in by_year.values()) == 1
    p1cnt = {y: by_year[y]["P1"] for y in range(2007, 2027)}
    records.sort(key=lambda x: (TIERS.index(x["tier"]),
                 -(p1cnt[x["year"]]), x["relativeLengthToPilot"] if x["relativeLengthToPilot"] is not None else 1,
                 x["year"], x["id"]))
    years = [dict(year=y, **dict(by_year[y])) for y in range(2007, 2027)]
    summary = {
        "schema": "NOMUSA_V29_2022_19YEAR_CONTENT_TRIAGE/1",
        "status": "PASS_METADATA_AND_BROWSER_SHA_CONTENT_APPROVAL_HOLD" if use_rendered else "PASS_METADATA_ONLY_CONTENT_APPROVAL_HOLD",
        "answers": 328, "baseline2022": 19, "otherYears": 309,
        "2022LimitedClaimLinks": 19, "otherYearsClaimByClaimEqualDepth": "NOT_ASSESSED",
        "priority": dict(sums), "browserRenderedVerified": len(rendered),
        "pilotMedianCharactersByScore": median_by_points,
        "sameQualityAcross20Years": "NOT_ESTABLISHED",
        "independentExpertApprovals": 0, "finalApproval": "HOLD",
        "unchangedOriginalAndDeployment": True,
        "limitation": "Length and reference tokens are triage signals, not substantive legal, scholarly, handwriting or expert verification",
    }
    return {"summary": summary, "years": years, "queue": records}


def write_outputs(result, root):
    out = root / "review-artifacts/NOMUSA_V29"
    out.mkdir(parents=True, exist_ok=True)
    (out / "NOMUSA_V29_328_CONTENT_TRIAGE.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = ["id", "year", "subject", "points", "tier", "textSHA256",
              "detailedCharacters", "relativeLengthToPilot", "sourceMatch",
              "sameSubstantiveQualityAs2022", "requiredReview"]
    with (out / "NOMUSA_V29_328_CONTENT_REVIEW_QUEUE.csv").open(
            "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(result["queue"])
    summary = result["summary"]
    lines = [
        "# V29 — 2022년 기준 19개년 본문 구조·검증 차이",
        "", "상태: " + summary["status"],
        "",
        "이 보고서는 **실제 상세·압축 표시본문 328건의 SHA 대조 및 단순 구조/분량 비교**를 지원합니다.",
        "2022년조차 전체 법률·학술 내용승인 미완료이며 다른 19개년의 동일 품질은 확정되지 않았습니다.",
        "길이 비교·판례 토큰·원전 일치는 전문 의견과 다르며 수기 분량의 실측도 아닙니다.",
        "", "| 연도 | 답안 | P0 | P1 | P2 | P3 | 원문 MEDIUM | SHA 동일 | 2022 길이 중앙값 미달 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for y in result["years"]:
        lines.append("| %d | %d | %d | %d | %d | %d | %d | %d | %d |" % (
            y["year"], y["total"], y.get("P0", 0), y.get("P1", 0),
            y.get("P2", 0), y.get("P3", 0), y.get("MEDIUM", 0),
            y.get("renderedAndSHAEqual", 0), y.get("lowerThanPilotMedian", 0)))
    lines += ["", "**다음 단계:** P0 2022년 19건 실제 원전 전문 검증 → P1 77건 논증·필기 점검 → P2 35건 → P3 197건. 각 항목 검토자/근거/원고SHA 승인 전까지 HOLD.",
              "", "main/Production/Preview/원고 불변; 재실행 가능한 검토 코드와 산출물만 생성.", ""]
    (out / "NOMUSA_V29_20YEAR_DELTA_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("root", nargs="?", default=".")
    p.add_argument("--rendered", action="store_true", help="require 20 actual Chromium exports")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        example = {"sourceText": "원문", "detailed": "상세", "compressed": "압축"}
        assert len(sha(example)) == 64
        assert "P1_TEST".split("_", 1)[0] == "P1"
        print("PASS_V29_UNIT_SELFTEST")
        return
    root = Path(args.root)
    result = audit(root, args.rendered)
    write_outputs(result, root)
    print(result["summary"]["status"])
    print("FINAL_APPROVAL=HOLD_0_OF_328; NO_DEPLOY_NO_SOURCE_MUTATION")


if __name__ == "__main__":
    main()
