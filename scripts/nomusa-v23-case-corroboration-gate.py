#!/usr/bin/env python3
"""V23 supplemental case-corroboration gate.

Checks independent references for 3 formerly unlocated case numbers, joined
to the unmodified 328-answer V23 ledger. It cannot approve legal contents,
claim that law.go.kr listed the cases, or issue expert certifications.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

LEDGER="review/NOMUSA_V23_VALIDATION_LEDGER.json"
SUPPLEMENT="review/NOMUSA_V23_CASE_3_CORROBORATION_20261117.json"
EXPECTED={
    "2012다81609":("2022-labor1-1","2014-12-24","PRIMARY_COURT_LATER_OPINION_CITES_ORIGINAL"),
    "2011두7526":("2014_p2_q1","2011-05-26","SECONDARY_PUBLIC_RESEARCH_INSTITUTE"),
    "2024구합76393":("2026-행정쟁송법|2|0","2025-08-21","SECONDARY_REPORT_WITH_OFFICIAL_COURT_CASE_LISTING")
}

def check(root:Path):
    ledger=json.loads((root/LEDGER).read_text(encoding="utf-8"))
    doc=json.loads((root/SUPPLEMENT).read_text(encoding="utf-8"))
    rows=ledger["rows"]
    if len(rows)!=328 or len({x["id"] for x in rows})!=328:
        raise ValueError("HOLD_328_ID_COUNT_MISMATCH")
    if ledger["summary"]["independentExpertApproved"]!=0 or ledger["summary"]["finalApproval"]!="HOLD (0/328)":
        raise ValueError("HOLD_EXPERT_APPROVAL_CHANGED")
    byid={x["id"]:x for x in rows}
    evidence=doc["cases"]
    if len(evidence)!=3 or {x["caseNo"] for x in evidence}!=set(EXPECTED):
        raise ValueError("HOLD_THREE_CASES_MISMATCH")
    counts=Counter()
    for x in evidence:
        number=x["caseNo"]
        id_,date,tier=EXPECTED[number]
        if x["questionId"]!=id_ or x["decisionDate"]!=date or x["decisionDateEvidence"]!=tier:
            raise ValueError("HOLD_CASE_ID_OR_DATE_MISMATCH_"+number)
        row=byid[id_]
        if row["textSHA256"]!=x["textSHA256"] or int(row["year"])!=int(x["year"]):
            raise ValueError("HOLD_ANSWER_SHA_OR_YEAR_CHANGED_"+number)
        related=[c for c in row["caseCitations"] if c["caseNo"]==number]
        counts[number]+=len(related)
        if not related or any(c["lawGoKr"]!="NOT_FOUND_ON_LAW_GO_KR_SEARCH" for c in related):
            raise ValueError("HOLD_HISTORICAL_SEARCH_CACHE_CONTRADICTION_"+number)
        if not x["sources"] or any(not urlparse(z["url"]).scheme=="https" or not urlparse(z["url"]).netloc for z in x["sources"]):
            raise ValueError("HOLD_MISSING_REPRODUCIBLE_URL_"+number)
        if x["originalFullJudgment"]=="VERIFIED" or x["examTimeApplicability"]=="PASS":
            raise ValueError("HOLD_UNJUSTIFIED_FULL_JUDGMENT_APPROVAL_"+number)
        if row["verdicts"]["expertApproval"]!="HOLD_EXPERT_APPROVAL" or row["verdicts"]["finalApproval"]!="HOLD":
            raise ValueError("HOLD_EXPERT_STATUS_"+number)
    if sum(counts.values())!=5 or counts!=Counter({"2012다81609":2,"2011두7526":2,"2024구합76393":1}):
        raise ValueError("HOLD_FIVE_CITATION_COUNTS")
    if doc["counts"]["expertApprovals"]!=0 or doc["finalApproval"]!="HOLD_0_OF_328":
        raise ValueError("HOLD_SUPPLEMENT_APPROVAL_INVALID")
    out={"status":"PASS_INDEPENDENT_CASE_IDENTITY_CROSSCHECK_FULL_LEGAL_EXPERT_HOLD",
         "supplement":"case numbering and dates corroborated to stated evidence tiers; historic law.go.kr cache remains NOT_FOUND",
         "caseCount":3,"questionCount":3,"citationOccurrences":5,
         "historicalLawGoKrSearchResolved":0,"fullJudgmentDirectlyCompared":0,
         "expertApproved":0,"finalApproval":"HOLD","cases":dict(counts)}
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument("root",nargs="?",default=".")
    args=ap.parse_args()
    try:
        out=check(Path(args.root));print(json.dumps(out,ensure_ascii=False));return 0
    except Exception as e:
        print(json.dumps({"status":"HOLD_V23_CORROBORATION_GATE","error":str(e)},ensure_ascii=False),file=sys.stderr)
        return 2
if __name__=="__main__":sys.exit(main())
