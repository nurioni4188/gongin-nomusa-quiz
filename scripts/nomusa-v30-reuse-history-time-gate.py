#!/usr/bin/env python3
"""NOMUSA V30: reuse previous edit/source evidence, no ungrounded new approvals.

Source-aware, read-only triage. Never changes manuscripts, IDs, source files or
the V23 ledger. A future-dated case must be verified against the *exam date*
before proposing a legal correction; year-only comparison is a warning.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = "review/NOMUSA_V23_VALIDATION_LEDGER.json"
V27 = "review/NOMUSA_V27_2022_PRIMARY_CONTENT_CROSSCHECK_20261118.json"
V28 = "review/NOMUSA_V28_2022_REMAINING_13_SOURCE_CROSSCHECK_20261118.json"
SUBSTANTIVE = "## V20 원문 연동 심화논증"

V9_DIRECT = {
    "2022-labor1-2", "2022-admin-2", "2023-labor1-1", "2023-admin-3"
}
HISTORICAL_CHECKS = {
    "legacy2-2007-labor2-q1": ("V15", "2011 교섭창구단일화는 2007 시험 후 법령임; 당시 배제 여부"),
    "legacy2-2009-labor2-q1": ("V15", "2010.03.25 선고 2007두8881은 2009 시험 후 판례임; 참고 분리"),
    "legacy2-2009-labor1-q1": ("V20", "2014 서면통지·2019 해고예고 관련 신법의 소급적용 금지"),
    "legacy2-2012-labor1-q1": ("V15", "2013 통상임금 전합은 2012 시험 후 참고 판례"),
    "2013_p1_q1": ("V15", "2023.05.11 취업규칙 불이익변경 전합은 2013 시험 후 참고"),
    "2020_p4_q2": ("V12", "2023 시행 행정기본법 제36조 및 2021~2022 후속 판례를 2020 시험 정답과 분리"),
    "2022-labor1-2": ("V9", "2022 당시 2019다238053 기준; 2024 통상임금 전합 소급금지"),
}
PRECEDENT_FOLLOWUP = {
    "2014_p2_q1": "2011두7526: 원판결 전문·독립 사건번호 확인 필요 (후속 보강 있음)",
    "2022-labor1-1": "2012다81609: 원판결 전문 및 답안 사실관계 포섭 확인 필요",
    "2026-행정쟁송법|2|0": "2024구합76393: 하급심 판결 전문·선고일·심급 확인 필요",
}
OCR_FOLLOWUP = {"2016_p5_q2": "공식 이미지 글자별 대조 HOLD; 유사도 MEDIUM"}

def read(root, path):
    return json.loads((root / path).read_text(encoding="utf-8"))

def load_v29(root):
    path = root / "scripts/nomusa-v29-2022-baseline-review.py"
    spec = importlib.util.spec_from_file_location("nomusa_v29_2022_baseline", path)
    assert spec is not None and spec.loader is not None, "HOLD_V29_SCRIPT"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def expected_js_ids(root, path, number):
    content = (root / path).read_text(encoding="utf-8")
    m = re.search(r"const expected=\[([\s\S]*?)\];", content)
    assert m, "HOLD_JS_EXPECTED_MISSING:" + path
    ids = re.findall(r"'([^']+)'", m.group(1))
    assert len(ids) == len(set(ids)) == number, "HOLD_JS_EXPECTED_COUNT:" + path
    return set(ids)

def same_bytes_hash(q):
    return hashlib.sha256((q["sourceText"] + "\0" + q["detailed"] + "\0" +
                           q["compressed"]).encode("utf-8")).hexdigest()

def audit(root, rendered=False):
    v29 = load_v29(root)
    base = v29.audit(root, use_rendered=rendered)
    ledger, v27, v28 = (read(root, p) for p in (BASE, V27, V28))
    rows = ledger["rows"]
    by_id = {x["id"]: x for x in rows}
    pilot6 = {c["id"] for c in v27["checks"]}
    pilot13 = {c["id"] for c in v28["referenceChecks"]}
    assert len(by_id) == 328 and len(pilot6) == 6 and len(pilot13) == 13
    assert not (pilot6 & pilot13)
    assert pilot6 | pilot13 == {x["id"] for x in rows if x["year"] == 2022}
    assert not (v27["expertApproved"] or v28["independentHumanExpertsApproved"])
    assert by_id["2022-hr-1"]["textSHA256"] == (
        "c3557e3b121836011a56822c14b3776e8567f1dd346f7a8d98b71247c9e38c89"
    ), "HOLD_V28_GOLDSTEIN_CURRENT_SHA"
    v12 = expected_js_ids(root, "second/nomusa-v12-apply.js", 20)
    v13 = expected_js_ids(root, "second/nomusa-v13-apply.js", 12)
    v15_labor = set()
    for path in ("second/nomusa-v15-labor_a.js", "second/nomusa-v15-labor_b.js"):
        content = (root / path).read_text(encoding="utf-8")
        v15_labor.update(re.findall(r"M\['([^']+)'\]\s*=", content))
    assert len(v15_labor) == 14, "HOLD_V15_LABOR_14_LINK"
    assert (V9_DIRECT | v12 | v13 | v15_labor |
            set(HISTORICAL_CHECKS) | set(PRECEDENT_FOLLOWUP) |
            set(OCR_FOLLOWUP)).issubset(by_id), "HOLD_HISTORICAL_IDS"
    rendered_rows = {}
    if rendered:
        exports = sorted((root / "review-artifacts").glob("nomusa_*_rendered*.json"))
        assert len(exports) == 20, "HOLD_BROWSER_EXPORTS_20"
        for path in exports:
            for q in json.loads(path.read_text(encoding="utf-8"))["rows"]:
                assert q["id"] not in rendered_rows
                rendered_rows[q["id"]] = q
        assert set(rendered_rows) == set(by_id)
    queue = []
    years = defaultdict(Counter)
    counts = Counter()
    post_exam_ids = set()
    history_counts = Counter()
    for r in rows:
        id_, year = r["id"], int(r["year"])
        q = rendered_rows.get(id_)
        if q:
            assert same_bytes_hash(q) == r["textSHA256"], "HOLD_SHA_" + id_
        history = ["V23_QNET_OFFICIAL_FILE_AND_QUESTION_SOURCE"]
        if id_ in V9_DIRECT:
            history.append("V9_DIRECT_PRECEDENT_SUBSTANTIVE_REWRITE")
        if id_ in v12:
            history.append("V12_2019_2020_LEGAL_REWRITE")
        if id_ in v13:
            history.append("V13_50PT_LEGAL_EXPANSION")
        if id_ in v15_labor:
            history.append("V15_LABOR_EDITION")
        if q and SUBSTANTIVE in q["detailed"]:
            history.append("V20_SOURCE_SPECIFIC_88_SUPPLEMENT")
        if id_ in pilot6:
            history.append("V27_2022_LIMITED_CLAIM")
        if id_ in pilot13:
            history.append("V28_2022_LIMITED_CLAIM")
        if id_ == "2022-hr-1":
            history.append("V28_GOLDSTEIN_VERIFIED_EDITORIAL_CORRECTION")
        for stage in history:
            history_counts[stage] += 1
        later = []
        for c in r.get("caseCitations", []):
            official = str(c.get("officialDecisionDate") or "")
            m = re.match(r"((?:19|20)\d{2})", official)
            if c.get("timing") == "AFTER_EXAM" or (m and int(m.group(1)) > year):
                later.append({"caseNo": c.get("caseNo"), "date": official,
                              "markedAsPostExam": bool(c.get("annotatedAsPostExam")),
                              "decisionYearOnlyNotExactExamDate": True})
        if later:
            post_exam_ids.add(id_)
        statute_later = r.get("statuteTimeEffect") or []
        warnings = []
        if later:
            warnings.append("AFTER_EXAM_DECISION_REFERENCE_CHECK")
        if statute_later:
            warnings.append("AFTER_EXAM_STATUTE_REFERENCE_CHECK")
        if id_ in HISTORICAL_CHECKS:
            warnings.append("CURATED_EXAM_DATE_POLICY_RECHECK")
        if id_ in PRECEDENT_FOLLOWUP:
            warnings.append("FULL_CASE_TEXT_NOT_YET_CERTIFIED")
        if id_ in OCR_FOLLOWUP:
            warnings.append("MEDIUM_OCR_CHARACTER_PROOFREAD")
        if r.get("lawFlags"):
            warnings.append("HISTORIC_STATUTE_FLAGS_REQUIRE_ORIGINAL")
        if r.get("academicFlags"):
            warnings.append("ACADEMIC_BIBLIOGRAPHY_FLAGS_REQUIRE_ORIGINAL")
        if r.get("calcFlags"):
            warnings.append("CALCULATION_FLAGS_REQUIRE_ORIGINAL")
        corrections = []
        # Never turn lack of full text / unusual timing into a confirmed error.
        # V28 Goldstein error is already fixed in the current canonical SHA.
        if any(not c["markedAsPostExam"] for c in later):
            warnings.append("POTENTIAL_UNLABELLED_AFTER_EXAM_CASE")
        focus = "CHECK_EXISTING_TIME_SEPARATION" if (later or statute_later or id_ in HISTORICAL_CHECKS) else "REFERENCES_UNDER_REVIEW"
        source_depth = "ONE_OR_MORE_CLAIMS_PARTIALLY_CORROBORATED" if year == 2022 else "OTHER_EXISTING_EVIDENCE_REUSE_INDEPENDENT_FULLTEXT_PENDING"
        classification = "기존 부분 근거 연결" if year == 2022 else "추가 원전·전문 검증 필요"
        priority = r["reviewTierV21"].split("_", 1)[0]
        out = {
            "id": id_, "year": year, "subject": r["subject"],
            "points": int(r["points"]), "priority": priority,
            "currentManuscriptSHA256": r["textSHA256"],
            "currentSHAReverified": rendered,
            "sourceOriginalQNetHashPreviouslyVerified": r["source"]["qnetOfficialByteIdentical"],
            "sourceMatchBand": r["source"]["matchBand"],
            "pastWorkEvidence": history,
            "pastWorkClaimIsNotFullTextCertification": True,
            "claimVerificationScope": source_depth,
            "reviewStatus": classification,
            "correctionConfirmed": False, "correctionNeeded": corrections,
            "historicalTimeReview": focus,
            "postExamCaseCitationOccurrences": later,
            "postExamStatuteMentions": statute_later,
            "curatedHistoricIssue": HISTORICAL_CHECKS.get(id_, (None, None))[1],
            "unresolvedFullJudgmentFollowup": PRECEDENT_FOLLOWUP.get(id_),
            "ocrFollowup": OCR_FOLLOWUP.get(id_),
            "flags": sorted(set(warnings)),
            "finalIndependentExpertSignoff": "HOLD",
        }
        queue.append(out)
        counts[classification] += 1
        years[year][classification] += 1
        years[year][priority] += 1
        years[year]["total"] += 1
    assert counts["기존 부분 근거 연결"] == 19
    assert counts["추가 원전·전문 검증 필요"] == 309
    assert not any(q["correctionConfirmed"] for q in queue)
    assert post_exam_ids == {"legacy2-2009-labor2-q1"}, post_exam_ids
    if rendered:
        assert history_counts["V20_SOURCE_SPECIFIC_88_SUPPLEMENT"] == 88, "HOLD_V20_88_ACTUAL_RENDER"
    focus_rows = [q for q in queue if q["flags"]]
    summary = {
        "schema": "NOMUSA_V30_EDITION_HISTORY_AND_TIME_EFFECT/1",
        "inspectionMethod": "V23+V27+V28 ledgers, V9/V12/V13/V15/V20 actual overlay catalog and V29 328 live browser output",
        "status": "PASS_328_HISTORY_AND_TIME_TRIAGE_FINAL_CONTENT_HOLD" if rendered else "PASS_SOURCE_METADATA_ONLY_FINAL_CONTENT_HOLD",
        "answers": 328, "years": 20, "reviewStateCounts": dict(counts),
        "expertSignoffPending": 328, "expertApproved": 0,
        "confirmedOutstandingCorrections": 0,
        "previouslyCorrectedV28": 1,
        "afterExamCaseCitationQuestionIds": sorted(post_exam_ids),
        "afterExamCaseCitationOccurrences": sum(len(q["postExamCaseCitationOccurrences"]) for q in queue),
        "historicalLegalFocusIds": sorted(HISTORICAL_CHECKS),
        "fullJudgmentFollowupIds": sorted(PRECEDENT_FOLLOWUP),
        "ocrFollowupIds": sorted(OCR_FOLLOWUP),
        "historyEvidenceCounts": dict(history_counts),
        "actualRenderedSHACompared": 328 if rendered else 0,
        "attentionRowsWithAnyFlag": len(focus_rows),
        "nextAction": "Targeted exact-exam-date historic statute/transitional-law and full-judgment review; correct only proven errors",
        "noSourceOrDeploymentChanges": True,
        "limitations": [
            "Past edit and one-claim proof are not independent full legal/academic review",
            "Decision year alone cannot establish pre/post precise exam date",
            "Labels for later-law references may be in older manuscripts or commentary; examine final view before correction",
            "No automatic rewriting and no expert approval"
        ],
        "finalApproval": "HOLD_0_OF_328",
    }
    queue.sort(key=lambda x: (0 if x["id"] in HISTORICAL_CHECKS else
                              1 if x["id"] in PRECEDENT_FOLLOWUP else
                              2 if x["id"] in OCR_FOLLOWUP else
                              3 if x["priority"] == "P0" else
                              4 if x["priority"] == "P1" else 5,
                              x["year"], x["id"]))
    return {"summary": summary,
            "byYear": [dict(year=y, **years[y]) for y in range(2007, 2027)],
            "queue": queue,
            "focus": focus_rows}

def save(root, result):
    output = root / "review-artifacts/NOMUSA_V30"
    output.mkdir(parents=True, exist_ok=True)
    (output / "NOMUSA_V30_328_REUSED_HISTORY_AND_TIME_GATE.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cols = ["id", "year", "subject", "points", "priority", "currentManuscriptSHA256",
            "reviewStatus", "historicalTimeReview", "correctionConfirmed",
            "currentSHAReverified", "finalIndependentExpertSignoff"]
    with (output / "NOMUSA_V30_328_REVIEW_QUEUE.csv").open("w", encoding="utf-8-sig",
                                                            newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(result["queue"])
    summary = result["summary"]
    focus = [q for q in result["queue"] if q["id"] in HISTORICAL_CHECKS or
             q["id"] in PRECEDENT_FOLLOWUP or q["id"] in OCR_FOLLOWUP]
    lines = [
        "# V30 — 중복 재작업 방지 / 기출 당시 법령·판례 시점 검증",
        "", "**" + summary["status"] + "**",
        "", "- 이전 V9/V12/V13/V15/V20/V27/V28의 실제 원고 교정·보강 기록은 재사용한다.",
        "- 2022년 19개: 제한된 1개 이상 주장 출처 근거 존재. 나머지 309개: 기존 편집/근거 대조 이력을 보존하며 추가 원전 전문 검토 필요.",
        "- 현재 오답 확정 0개 (새 원전 전문 독립 확인 없이 수정요구를 확정하지 않음). 과거 V28 교정 1개는 이미 반영됨.",
        "- 328개 전원 전문가 최종승인 HOLD; 과거 문항에 시험 후 판례를 참고로 표시하는 것과 소급적용은 별개.",
        "- 모든 328개 실제 학습화면 본문 SHA와 원장 대조: " + str(summary["actualRenderedSHACompared"]),
        "",
        "## 기출연도와 이후 법리의 충돌 위험 선별 (원고 재작성 없음)",
        "",
        "| 문항 ID | 점검 사유 | 정리 |",
        "|---|---|---|",
    ]
    for x in focus:
        why = (x["curatedHistoricIssue"] or x["unresolvedFullJudgmentFollowup"] or x["ocrFollowup"]).replace("|", "/")
        lines.append("| " + x["id"].replace("|", "\\|") + " | " + why + " | 독립 원전/당시 시점 확인 후 교정 여부 판정 |")
    lines += [
        "", "## 전체 연도별 분류",
        "", "| 연도 | 답안 | 2022 제한 근거 | 추가 전문 검증 | P0 | P1 | P2 | P3 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in result["byYear"]:
        lines.append("| %d | %d | %d | %d | %d | %d | %d | %d |" % (
            r["year"], r.get("total", 0), r.get("기존 부분 근거 연결", 0),
            r.get("추가 원전·전문 검증 필요", 0),
            r.get("P0", 0), r.get("P1", 0), r.get("P2", 0), r.get("P3", 0)))
    lines += ["", "### 관문",
              "1. 2016_p5_q2 글자별 교열, 미확정 판결문 3건·시험 후 법리 참고를 원문 기준 점검.",
              "2. 실제 오류가 특정 문장·판결문·시험일 시행부칙과 함께 확인된 경우에만 별도 교정안/구SHA·신SHA 기록.",
              "3. 기존 V26 7과목 328 패킷을 재사용; 전문가 서면승인 전까지 검토 상태 유지.",
              "4. main/Production/Preview/기출 원본/문제 ID/학습 저장키/원고 전부 불변.",
              "", "※ 20개년 서술이 모두 최종 법률·학술적으로 정확하다는 인증이 아니며, '재검증 필요'는 '재작성 필요'와 다릅니다.", ""]
    (output / "NOMUSA_V30_TIME_EFFECT_DELTA_REPORT.md").write_text(
        "\n".join(lines), encoding="utf-8")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("root", nargs="?", default=".")
    p.add_argument("--rendered", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        assert len(HISTORICAL_CHECKS) == 7 and len(PRECEDENT_FOLLOWUP) == 3
        assert len(OCR_FOLLOWUP) == 1 and len(V9_DIRECT) == 4
        assert not (set(HISTORICAL_CHECKS) & set(OCR_FOLLOWUP))
        print("PASS_V30_SELFTEST_NO_WRITES")
        return
    root = Path(a.root)
    result = audit(root, rendered=a.rendered)
    save(root, result)
    print(result["summary"]["status"])
    print("HISTORIC_RECHECK_7_FOCUS_FULL_CASE_3_OCR_1")
    print("FINAL_APPROVAL=HOLD_0_OF_328, NO_DEPLOY_NO_MANUSCRIPT_MUTATION")

if __name__ == "__main__":
    main()
