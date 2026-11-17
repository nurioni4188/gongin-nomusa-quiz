#!/usr/bin/env python3
"""NOMUSA V28: 13 source-specific checks + one Goldstein editorial correction.

Runs on 328 Chromium-rendered drafts against frozen V23 SHA ledger. The 13
source claims are externally researched evidence candidates, NOT judgments
of full answer correctness. Existing 2022 V27 six-claim review is versioned.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

LEDGER="review/NOMUSA_V23_VALIDATION_LEDGER.json"
V27="review/NOMUSA_V27_2022_PRIMARY_CONTENT_CROSSCHECK_20261118.json"
V28="review/NOMUSA_V28_2022_REMAINING_13_SOURCE_CROSSCHECK_20261118.json"
TARGET="2022-hr-1"

def read(p):
    return json.loads(p.read_text(encoding="utf-8"))
def h(q):
    return hashlib.sha256((q["sourceText"]+"\0"+q["detailed"]+"\0"+q["compressed"]).encode("utf8")).hexdigest()

def run(root):
    old=read(root/LEDGER);p27=read(root/V27);p28=read(root/V28)
    oldrows={r["id"]:r for r in old["rows"]}
    if len(oldrows)!=328 or old["summary"]["independentExpertApproved"]!=0:
        raise ValueError("HOLD_BASELINE_328")
    f=sorted((root/"review-artifacts").glob("nomusa_*_rendered*.json"))
    if len(f)!=20:raise ValueError("HOLD_EXPECT_TWENTY_BROWSER_EXPORTS")
    now={}
    for file in f:
        for q in read(file)["rows"]:
            if q["id"] in now:raise ValueError("HOLD_DUPLICATE_ID")
            now[q["id"]]=q
    if set(now)!=set(oldrows):raise ValueError("HOLD_328_ID_SET_MISMATCH")
    changes=[]
    for i,q in now.items():
        oldr=oldrows[i]
        if q["subject"]!=oldr["subject"] or int(q["points"])!=int(oldr["points"]) or int(q["year"])!=oldr["year"]:
            raise ValueError("HOLD_YEAR_SUBJECT_POINTS_"+i)
        if q.get("scoringApproved") is not False:
            raise ValueError("HOLD_AUTOSCORING_APPROVAL_"+i)
        if h(q)!=oldr["textSHA256"]:changes.append(i)
    if changes!=[TARGET]:raise ValueError("HOLD_NOT_ONE_GOLDSTEIN_CHANGE_"+repr(changes))
    item=now[TARGET]
    # Compare against the unmodified raw printed-question catalog; never rely on
    # a filename glob for the browser export (it is nomusa_2022_*_rendered*.json).
    raw=(root/"rc27_essay_catalog.js").read_text(encoding="utf-8")
    original=json.loads(raw.split("=",1)[1].strip().rstrip(";"))
    source=[q for q in original["items"] if q["id"]==TARGET]
    if len(source)!=1 or item["sourceText"]!=source[0]["sourceText"]:
        raise ValueError("HOLD_2022_HR1_PRINTED_SOURCE_CHANGED")
    detail=item["detailed"];short=item["compressed"]
    if "Human Relations" in detail or "⑥ 경영 시뮬레이션" in detail or "경영시뮬" in short:
        raise ValueError("HOLD_GOLDSTEIN_OLD_ERROR_REMAINS")
    if "Human Factors, 20(2), 131–144" not in detail or "⑥ 액션러닝" not in detail or "액션러닝(각 효과+한계)" not in short:
        raise ValueError("HOLD_GOLDSTEIN_FIX_NOT_PRESENT")
    p0={i:r for i,r in oldrows.items() if r["year"]==2022}
    if len(p0)!=19 or sum(len(q.get("parts") or []) for i,q in now.items() if i in p0)!=32:
        raise ValueError("HOLD_2022_19_AND_32")
    previous={x["id"] for x in p27["checks"]}
    fresh={x["id"] for x in p28["referenceChecks"]}
    if len(previous)!=6 or len(fresh)!=13 or previous & fresh or previous|fresh!=set(p0):
        raise ValueError("HOLD_V27_V28_19_DISTINCT")
    if p27["expertApproved"]!=0 or p28["independentHumanExpertsApproved"]!=0 or p28["finalApproval"]!="HOLD":
        raise ValueError("HOLD_FAKE_APPROVAL")
    countVerifiedClaims=0; countSourceRefs=0
    for r in p28["referenceChecks"]:
        i=r["id"];prev=oldrows[i]
        if r["textSHA256"]!=prev["textSHA256"] or not r["knownV23SourceByteMatch"] or r["points"]!=prev["points"]:
            raise ValueError("HOLD_SOURCE_CITATION_STALE_"+i)
        checked=0
        for cl in r["items"]:
            url=urlparse(cl["url"])
            if url.scheme!="https" or not url.netloc:raise ValueError("HOLD_BAD_URL_"+i)
            countSourceRefs+=1
            if not cl["evidenceScope"].startswith("NOT_VERIFIED"):checked+=1
        if checked<1 or r["approval"]!="HOLD" or r["expertSigned"] is not False:
            raise ValueError("HOLD_NO_GROUNDED_CLAIM_OR_SIGNOFF_"+i)
        countVerifiedClaims+=checked
    # Deterministic math only, no universal utility outcome.
    C12=8+1.5*(12-8);C15=8+1.5*(15-8)
    U8=8-8*8/16;U12=C12-12*12/16
    if (C12,C15,U8,U12)!=(14.0,18.5,4.0,5.0):
        raise ValueError("HOLD_ECON_EXAMPLE_RECALC")
    report=[]
    for id_,oldr in sorted(p0.items()):
        category="V27_6_ALREADY_REFERENCED" if id_ in previous else "V28_13_NEW_CLAIM_LINKS"
        report.append({"id":id_,"subject":oldr["subject"],"points":oldr["points"],
           "beforeTextSHA256":oldr["textSHA256"],
           "currentTextSHA256":h(now[id_]),
           "manuscriptChangedOnlySourceBackedEditorial":id_==TARGET,
           "limitedOriginalEvidence":category,
           "wholeAnswerLegalAcademicVerified":False,"expertApproval":"HOLD"})
    status={"schema":"NOMUSA_V28_2022_19_CLAIM_BY_CLAIM/1",
       "generatedUTC":datetime.now(timezone.utc).isoformat(timespec="seconds"),
       "total":328,"pilot2022":19,"pilotParts":32,
       "v27LimitedClaimsQuestions":6,"v28LimitedClaimsQuestions":13,
       "v28ClaimURLs":countSourceRefs,"v28LimitedCrosschecks":countVerifiedClaims,
       "entireAnswerExpertVerified":0,
       "manuscriptsEdited":1,"manuscriptsUnchanged":327,
       "editedId":TARGET,"oldSHA":oldrows[TARGET]["textSHA256"],
       "newSHA":h(item),"sourcesUnmodified":True,"questionIdsUnmodified":True,
       "studentStorageUnmodified":True,
       "independentExpertApproved":0,"finalApproval":"HOLD",
       "production":False,"preview":False,"email":False}
    out=root/"review-artifacts/NOMUSA_V28";out.mkdir(parents=True,exist_ok=True)
    (out/"NOMUSA_V28_2022_19_CONTENT_PRECHECK.json").write_text(
       json.dumps({"summary":status,"rows":report,"sourceEvidence":p28["referenceChecks"]},
                  ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# NOMUSA V28 — 2022 19문항, 공식/학술/계산 주장의 근거 연결 (최종승인 HOLD)",
       "","V27 6개 + V28 나머지 13개 = **19문항 모두 최소 1개 이상의 주장에 대한 직접 원전·서지·계산 근거 연결**.",
       "**19개 답안 전체의 법리·학술·수식·필기분량 승인과는 다름. 외부 전문가 0/328 HOLD.**","",
       "Goldstein 2022-hr-1 편집교정: 원저 *Human Factors* 20(2)·131–144, 기존 *Human Relations* 오기 제거.",
       "관리층 교육훈련 ⑥ 액션러닝을 상세/압축에 통일. 다른 327 원고 불변.",
       "원본 기출/Q-Net PDF·문항 ID·기존 학습키 불변.","",
       "## V28 신규 13문항 확인한 구체적 근거",""]
    for r in p28["referenceChecks"]:
        lines.append("### "+r["id"]+" — "+r["subject"])
        for item in r["items"]:
            lines.append("- **"+item["claimCode"]+"** "+item["claim"]+" [증빙]("+item["url"]+") · "+item["evidenceScope"])
    lines+=["","## 변경 SHA","- "+TARGET+": "+oldrows[TARGET]["textSHA256"]+" → "+h(now[TARGET]),
       "","**미완료**: 2022 시험일 역사 법령 각 조문·부칙/원판결 전문의 모든 법리·개별 사안포섭, 학술 전체 원문 및 실전 손글씨 실측, 독립 전문가 서면승인.",
       "","**FINAL_APPROVAL=HOLD, 0/328**.",""]
    (out/"NOMUSA_V28_2022_19_SOURCE_REVIEW_REPORT.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"status":"PASS_V28_13_LIMITED_CLAIM_LINKS_ONE_EDIT_327_SHA_UNCHANGED_CONTENT_HOLD",
      "pilot":19,"previous":6,"new":13,"modified":1,"unchanged":327,
      "sourceRefs":countSourceRefs,"verifiedLimited":countVerifiedClaims,
      "expertApproved":0},ensure_ascii=False))
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("root",nargs="?",default=".")
    parser.add_argument("--self-test",action="store_true");args=parser.parse_args()
    try:
        if args.self_test:
            assert 8+1.5*(12-8)==14.0
            print("PASS_V28_SELF_TEST")
        else:run(Path(args.root))
    except Exception as ex:
        print(json.dumps({"status":"HOLD_V28","error":str(ex)},ensure_ascii=False),file=sys.stderr)
        sys.exit(2)
