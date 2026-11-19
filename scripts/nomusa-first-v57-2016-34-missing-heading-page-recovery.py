#!/usr/bin/env python3
"""V57 conservative page-region lookup for 34 V55 unresolved 2016 A questions.

Use ordered adjacent question numbers' *provisional* PDF pages to narrow the
source-page inspection queue. Do NOT assign invented question coordinates or
auto-crop a missing heading. Page previews show the ENTIRE original page
and may contain multiple questions; even a single candidate needs human review.
"""
from __future__ import annotations
import csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path
import requests, fitz

ROOT=Path(__file__).resolve().parents[1]
V55=ROOT/"review-artifacts/NOMUSA_FIRST_V55/NOMUSA_FIRST_V55_125_QUESTION_PAGE_AND_CROP_REVIEW.json"
V53=ROOT/"review/NOMUSA_FIRST_V53_2016_MANAGEMENT_QNET_SOURCE_SUMMARY_20261118.json"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V57"
PAGES=OUT/"original_full_page_reviewer_previews"
OUT.mkdir(parents=True,exist_ok=True)
PAGES.mkdir(parents=True,exist_ok=True)
SUMMARY=ROOT/"review/NOMUSA_FIRST_V57_2016_UNRESOLVED34_PAGE_BRACKETS_20261118.json"
def check(x,msg):
    if not x:raise AssertionError("HOLD_V57_"+msg)
def load(p):return json.loads(p.read_text(encoding="utf8"))
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
    review=load(V55);source=load(V53)["source"]
    rows=review["rows"]
    check(len(rows)==125 and len({x["id"] for x in rows})==125,"125_CANDIDATE_IDS")
    unique={r["number"]:r["provisionalImage"]["officialQnetPdfPageCandidate"]
            for r in rows if r["provisionalImage"] is not None}
    check(len(unique)==91,"V55_UNIQUE_91")
    unresolved=[r for r in rows if r["provisionalImage"] is None]
    check(len(unresolved)==34,"UNRESOLVED_34")
    url=source["officialSourceURL"]
    r=requests.get(url,headers={"User-Agent":"Mozilla/5.0","Referer":"https://www.q-net.or.kr/"},
                   timeout=(12,100))
    r.raise_for_status()
    raw=r.content
    check(digest(raw)==source["sourcePDFSHA256"] and raw.startswith(b"%PDF"),"2016_PDF_SHA")
    doc=fitz.open(stream=raw,filetype="pdf")
    check(len(doc)==36,"PDF_36")
    records=[];statuses=Counter()
    previews={}
    for q in unresolved:
        n=q["number"]
        smaller=[k for k in unique if k<n]
        larger=[k for k in unique if k>n]
        prev=max(smaller) if smaller else None
        nxt=min(larger) if larger else None
        prevpage=unique.get(prev) if prev is not None else None
        nextpage=unique.get(nxt) if nxt is not None else None
        canBound=prevpage is not None and nextpage is not None and prevpage<=nextpage and nextpage-prevpage<=2
        pageCandidates=list(range(prevpage,nextpage+1)) if canBound else []
        # Never copy a neighboring page as an exact question location.
        anchorHits=[p for p in q["questionPageCandidates"] if p in pageCandidates]
        if canBound and len(anchorHits)==1:
            flag="MULTIPLE_ANCHORS_FILTERED_TO_BRACKET_PAGE_PREVIEW_ONLY"
            candidatePages=sorted(set(anchorHits))
        elif canBound and q["questionPageCandidates"]:
            flag="ORDERED_BRACKET_WITH_AMBIGUOUS_ANCHORS_REVIEW"
            candidatePages=sorted(set(pageCandidates))
        elif canBound:
            flag="ORDERED_NEIGHBOR_PAGE_BRACKET_REVIEW"
            candidatePages=sorted(set(pageCandidates))
        else:
            flag="NO_TIGHT_BOUNDED_PAGE_CANDIDATE_HOLD"
            candidatePages=[]
        previewRefs=[]
        for page in candidatePages:
            if page not in previews:
                pix=doc[page-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),
                    colorspace=fitz.csRGB,alpha=False)
                blob=pix.tobytes("jpeg",jpg_quality=74)
                dest=PAGES/("2016-A-management-p%03d.jpg"%page)
                dest.write_bytes(blob)
                previews[page]={"path":str(dest.relative_to(OUT)),"sha256":digest(blob),
                                "sourcePdfSha256":source["sourcePDFSHA256"],"pdfPage":page,
                                "notIndividualQuestionCrop":True}
            previewRefs.append(previews[page])
        statuses[flag]+=1
        records.append({
            "id":q["id"],"number":n,"subject":q["subject"],
            "priorV55State":q["status"],"priorDetectedPages":q["questionPageCandidates"],
            "previousUniqueQuestion":prev,"previousUniquePdfPage":prevpage,
            "nextUniqueQuestion":nxt,"nextUniquePdfPage":nextpage,
            "candidateSourcePdfPages":candidatePages,
            "fullPagePreviewRefs":previewRefs,
            "confidence":"NEIGHBOR_ORDER_HEURISTIC_NOT_NATIVE_SOURCE_APPROVAL",
            "status":flag,
            "stemFiveOptionsIndependentlyVerified":False,
            "questionNumberExactPageIndependentlyVerified":False,
            "officialFinalAnswerKeyCellApproved":False,
            "legalTheoryApproved":False,
            "independentReviewerApproved":False,
            "readyForV44":False,"scoringApproved":False
        })
    doc.close()
    check(len(records)==34 and all(q["scoringApproved"] is False for q in records),"NO_APPROVALS")
    output={"schema":"NOMUSA_FIRST_V57_2016_A_MANAGEMENT_34_MISSING_HEADING_SOURCE_PAGES/1",
        "asOfKST":"2026-11-18",
        "targetUnresolvedQuestionIds":34,
        "sourceOfficialQNetPdfSha256":source["sourcePDFSHA256"],
        "priorUniqueSourceCropsPreserved":91,
        "orderedAdjacentQuestionPageBrackets":sum(q["status"]!="NO_TIGHT_BOUNDED_PAGE_CANDIDATE_HOLD" for q in records),
        "noTightBrackets":statuses["NO_TIGHT_BOUNDED_PAGE_CANDIDATE_HOLD"],
        "uniqueFullPagePreviewImages":len(previews),
        "statusCounts":dict(sorted(statuses.items())),
        "nativeQuestionOriginalTextApproved":0,
        "fullFiveOptionsApproved":0,"independentAnswerKeyApproved":0,
        "newScoringApproved":0,"newAppImports":0,
        "warning":"Only candidates inferred from neighboring provisional question anchors. Full page images may show many questions. No exact source-page or question-text approval.",
        "status":"PASS_34_NEIGHBOR_PAGE_TRIAGE_HOLD_INDIVIDUAL_SOURCE_AND_SCORING",
        "rows":records}
    (OUT/"NOMUSA_FIRST_V57_34_UNRESOLVED_ORDERED_PAGE_QUEUE.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    with (OUT/"NOMUSA_FIRST_V57_34_UNRESOLVED_ORDERED_PAGE_QUEUE.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f);w.writerow(["id","number","previousQuestion","previousPage","nextQuestion","nextPage","candidatePages","pagePreview","status","scoring"])
        for q in records:w.writerow([q["id"],q["number"],q["previousUniqueQuestion"] or "",q["previousUniquePdfPage"] or "",
           q["nextUniqueQuestion"] or "",q["nextUniquePdfPage"] or "","|".join(map(str,q["candidateSourcePdfPages"])),
           "|".join(p["path"] for p in q["fullPagePreviewRefs"]),q["status"],"HOLD"])
    short={k:v for k,v in output.items() if k!="rows"}
    short["complete34Artifact"]="review-artifacts/NOMUSA_FIRST_V57/NOMUSA_FIRST_V57_34_UNRESOLVED_ORDERED_PAGE_QUEUE.json"
    SUMMARY.write_text(json.dumps(short,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(short,ensure_ascii=False))
if __name__=="__main__":main()
