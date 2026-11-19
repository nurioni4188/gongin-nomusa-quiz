#!/usr/bin/env python3
"""NOMUSA V31: audit 11 grounded findings, one one-sentence edit, 327 unchanged SHA.

Use after regenerating V23 ledger from exact rendered Chromium exports.
Never certifies a full judgment, statutory application, or human review.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path
from collections import Counter

EVIDENCE = "review/NOMUSA_V31_11_PRIMARY_SOURCE_EXAM_DATE_EVIDENCE_20261118.json"
LEDGER = "review/NOMUSA_V23_VALIDATION_LEDGER.json"
MANUSCRIPT = "second/nomusa-v11-admin-2024-2026.js"
TARGET = "2026-행정쟁송법|2|0"
OLD = "실제로 2026년 초 서울행정법원이 종합건설사에 대한 만인율 통보의 집행정지를 인용하였다는 보도가 있다."
NEW = ("별도 집행정지 사건에 관하여는 서울행정법원이 2024년도 사고사망만인율 통보의 "
       "효력정지 신청을 인용하였다는 2025. 8. 12. 보도가 있다. 이는 2024구합76393 "
       "본안판결이 처분성을 인정하면서도 청구를 기각한 것과 별개의 사건·판단이므로, "
       "집행정지 요건은 해당 기출 사실관계에 따라 독립적으로 심사해야 한다.")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def classify(root, previous):
    j = read(root / EVIDENCE)
    now = read(root / LEDGER)
    before = read(previous)
    assert j["targetCount"] == 11 and j["split"] == {"examTime":7,"fullCase":3,"ocr":1}
    queue = j["rows"]
    ids = [x["id"] for x in queue]
    assert len(set(ids)) == 11, "HOLD_V31_DUPLICATES"
    assert {x["category"] for x in queue} == {"EXAM_TIME","CASE_FULLTEXT","CASE_FULLTEXT_AND_EDIT","OFFICIAL_EXAM_OCR"}
    assert sum(x["category"]=="EXAM_TIME" for x in queue)==7
    assert sum(x["category"].startswith("CASE") for x in queue)==3
    assert sum(x["category"]=="OFFICIAL_EXAM_OCR" for x in queue)==1
    assert all(x["evidenceUrls"] and all(url.startswith("https://") for url in x["evidenceUrls"]) for x in queue)
    old = {x["id"]:x for x in before["rows"]}
    new = {x["id"]:x for x in now["rows"]}
    assert len(old) == len(new) == 328 and set(old)==set(new)
    assert set(ids).issubset(new)
    altered = [key for key in old if old[key]["textSHA256"]!=new[key]["textSHA256"]]
    assert altered==[TARGET], "HOLD_CHANGED_SHAS:"+repr(altered)
    for key in old:
        x,y=old[key],new[key]
        assert x["source"]==y["source"], "HOLD_QNET_OR_SOURCE_CHANGED_"+key
        assert x["points"]==y["points"] and x["subject"]==y["subject"], "HOLD_POINTS_OR_SUBJECT_"+key
        assert y["verdicts"]["finalApproval"]=="HOLD" and y["verdicts"]["expertApproval"]=="HOLD_EXPERT_APPROVAL"
        if key!=TARGET:
            assert x["textSHA256"]==y["textSHA256"]
    assert old[TARGET]["textSHA256"] != new[TARGET]["textSHA256"]
    assert now["summary"]["qnetOfficialByteIdentical"]==328
    assert now["summary"]["sourceVerifiedQuestion"]==328
    assert now["summary"]["independentExpertApproved"]==0
    assert now["summary"]["finalApproval"]=="HOLD (0/328)"
    assert new["2022-hr-1"]["textSHA256"]=="c3557e3b121836011a56822c14b3776e8567f1dd346f7a8d98b71247c9e38c89"
    code=(root / MANUSCRIPT).read_text(encoding="utf-8")
    assert OLD not in code and code.count(NEW)==1, "HOLD_V31_2026_CORRECTION_NOT_APPLIED_EXACTLY_ONCE"
    assert "M['2026-행정쟁송법|2|0']" in code
    prev25=read(root / "review/NOMUSA_V25_MEDIUM_3_PRIMARY_PAGE_CROSSCHECK_20261118.json")
    proof=next(x for x in prev25["items"] if x["id"]=="2016_p5_q2")
    assert proof["result"]=="VISUAL_MATCH_NO_SOURCE_CHANGE"
    rec=next(x for x in queue if x["id"]==TARGET)
    assert rec["verdict"]=="ONE_DATE_ATTRIBUTION_CORRECTED_REVERIFY_SHA"
    assert any("202508121351210960459" in url for url in rec["evidenceUrls"])
    assert any("seqnum=27433" in url for url in rec["evidenceUrls"])
    row=[{**x, "oldManuscriptSHA256":old[x["id"]]["textSHA256"],
          "newManuscriptSHA256":new[x["id"]]["textSHA256"],
          "exactSHAChanged":old[x["id"]]["textSHA256"]!=new[x["id"]]["textSHA256"],
          "sourceBinaryStillOriginal":True,
          "fullHumanReview":"HOLD"} for x in queue]
    summary={"schema":"NOMUSA_V31_ONE_EDIT_11_FOCUS_SHA_LOCK/1",
        "status":"PASS_SOURCE_CROSSCHECK_1_GROUNDED_SENTENCE_CORRECTION_FULL_EXPERT_REVIEW_HOLD",
        "targeted":11,"historicalTime":7,"judgmentSources":3,"sourceOCR":1,
        "singleSentenceCorrectedId":TARGET,
        "changedManuscripts":altered,"unmodifiedManuscripts":327,
        "previouslyCorrected2016OCRAlreadyFaithful":True,
        "originalQNet328":True, "originalIDs328":True,
        "expertApproved":0,"finalApproval":"HOLD",
        "requiresFurtherReview":[
            "2011두7526 original full judgment not independently checked",
            "2012다81609 original full judgment not independently checked",
            "2024구합76393 original court PDF full judgment not independently checked",
            "2009 and earlier historic statute/transitional provisions not exhaustively checked",
            "2016 OCR independent human proofreading not signed",
            "actual handwriting pages and independent expert signoff"
        ],
        "noMainProductionPreviewWrites":True}
    return {"summary":summary,"rows":row}


def save(root, result):
    out=root/"review-artifacts/NOMUSA_V31"
    out.mkdir(parents=True,exist_ok=True)
    (out/"NOMUSA_V31_11_EVIDENCE_SHA_DIFF.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    f=["id","year","category","verdict","oldManuscriptSHA256","newManuscriptSHA256","exactSHAChanged","needs"]
    with (out/"NOMUSA_V31_11_EXAM_DATE_REVIEW.csv").open("w",encoding="utf-8-sig",newline="") as fp:
        w=csv.DictWriter(fp,fieldnames=f,extrasaction="ignore")
        w.writeheader();w.writerows(result["rows"])
    s=result["summary"]
    lines=["# V31 공식 출처 11건 집중점검 및 1문장 최소교정","","## 기술검증","",
           "- "+s["status"],
           "- 328개 답안 중 "+TARGET+" **원고 SHA 1개만 변경**, 그 외 327개 SHA 불변",
           "- 2016_p5_q2 기존 V25 원본 이미지 대조 일치 재사용(사람 교열 HOLD)",
           "- 2020_p4_q2 행정기본법 제36조 2023.3.24 이후 시행 구별 보존",
           "- 2014_p2_q1, 2022-labor1-1, 2026 행정쟁송법 판결 등은 직접·간접 출처 검증수준 명시",
           "- **과거/현재 두 내용승인 모두 0/328 HOLD**; 해당 1문장 날짜표기 교정은 전체 정답 교정이 아님",
           "","## 11개 결과","",
           "| ID | 기존 검증·신규 근거 판정 | SHA 변경 | 잔여 검토 |",
           "|---|---|---|---|"]
    for row in result["rows"]:
        lines.append("| "+row["id"].replace("|","\\|")+" | "+row["verdict"]+" | "+("예" if row["exactSHAChanged"] else "아니오")+" | "+row["needs"].replace("|","/")+" |")
    lines.extend(["","공식 판결·법령 원전 및 당시 사실관계 전체 전문 심사는 별도 HOLD. main·Production·Preview 배포·병합 없음.",""])
    (out/"NOMUSA_V31_11_GROUNDED_CORRECTION_REPORT.md").write_text("\n".join(lines),encoding="utf-8")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("root",nargs="?",default=".")
    p.add_argument("--before-ledger")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        assert len(OLD)<len(NEW) and "2025. 8. 12." in NEW
        assert TARGET.startswith("2026-행정쟁송법")
        print("PASS_V31_SELFTEST")
        return
    if not a.before_ledger:
        p.error("--before-ledger required for strict SHA comparison")
    root=Path(a.root)
    res=classify(root,Path(a.before_ledger))
    save(root,res)
    print(res["summary"]["status"]+"; FINAL_APPROVAL=HOLD_0_OF_328")


if __name__=="__main__":
    main()
