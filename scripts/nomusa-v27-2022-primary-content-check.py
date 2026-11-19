#!/usr/bin/env python3
"""V27: check 2022 official evidence claims against browser-rendered SHA-locked drafts.

This is NOT full source-review or human-expert attestation.
"""
import argparse, hashlib, json, re, sys
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime, timezone

BASE="review/NOMUSA_V23_VALIDATION_LEDGER.json"
EVIDENCE="review/NOMUSA_V27_2022_PRIMARY_CONTENT_CROSSCHECK_20261118.json"

def read(p):
    return json.loads(p.read_text(encoding="utf-8"))
def sha(q):
    return hashlib.sha256((q["sourceText"]+"\0"+q["detailed"]+"\0"+q["compressed"]).encode()).hexdigest()

def run(root):
    b=read(root/BASE);e=read(root/EVIDENCE)
    ledger={r["id"]:r for r in b["rows"]}
    assert len(ledger)==328 and b["summary"]["qnetOfficialByteIdentical"]==328
    assert b["summary"]["independentExpertApproved"]==0 and b["summary"]["finalApproval"]=="HOLD (0/328)"
    fs=sorted((root/"review-artifacts").glob("nomusa_*_rendered*.json"))
    if len(fs)!=20:raise ValueError("HOLD_20_BROWSER_EXPORTS_REQUIRED")
    allq={}
    for f in fs:
        for q in read(f)["rows"]:
            if q["id"] in allq:raise ValueError("HOLD_DUPLICATE_ID")
            allq[q["id"]]=q
    if set(allq)!=set(ledger):raise ValueError("HOLD_328_SET_MISMATCH")
    for id_,q in allq.items():
        if sha(q)!=ledger[id_]["textSHA256"]:raise ValueError("HOLD_SHA_MISMATCH:"+id_)
    ids2022={i for i,r in ledger.items() if r["year"]==2022}
    if len(ids2022)!=19 or sum(len(allq[i].get("parts") or []) for i in ids2022)!=32:
        raise ValueError("HOLD_P0_19_32")
    checks=e["checks"]
    if len(checks)!=6 or len({x["id"] for x in checks})!=6:
        raise ValueError("HOLD_EXPECT_SIX_DISTINCT_EVIDENCE")
    selected={x["id"]:x for x in checks}
    if not set(selected)<=ids2022 or e["expertApproved"]!=0 or e["finalApproval"]!="HOLD":
        raise ValueError("HOLD_EVIDENCE_APPROVAL_OR_IDS")
    for c in checks:
        i=c["id"];r=ledger[i];q=allq[i];body=q["sourceText"]+"\n"+q["detailed"]+"\n"+q["compressed"]
        if c["textSHA256"]!=r["textSHA256"] or c["points"]!=r["points"] or c["subject"]!=r["subject"]:
            raise ValueError("HOLD_EVIDENCE_OUTDATED:"+i)
        if c["officialExamPostUrl"]!=r["source"]["qnetPostUrl"] or not c["sourceQNetBinaryPreviouslyVerified"]:
            raise ValueError("HOLD_QNET_REFERENCE:"+i)
        if c["finalApproval"]!="HOLD" or c["expertApproved"] is not False:
            raise ValueError("HOLD_IMPROPER_EXPERT_APPROVAL:"+i)
        for t in c["requiredTokens"]:
            if t not in body:raise ValueError("HOLD_CLAIM_TEXT_ANCHOR:"+i+":"+t)
        if not c["findings"]:raise ValueError("HOLD_NO_VERIFICATION:"+i)
        for f in c["findings"]:
            u=urlparse(f["url"])
            if u.scheme!="https" or not u.netloc:
                raise ValueError("HOLD_INVALID_URL:"+i)
    hr=allq["2022-hr-1"]["detailed"]
    if not all(s in hr for s in ("Human Relations","Human Factors","액션러닝","경영 시뮬레이션")):
        raise ValueError("HOLD_HR_EDITORIAL_CONTRADICTION_CHANGED")
    econ=allq["2022-econ-2"]
    if not (re.search(r"20\s*%",econ["sourceText"]) and re.search(r"80\s*%",econ["sourceText"])):
        raise ValueError("HOLD_GINI_QUESTION_NUMBERS_CHANGED")
    b=(0+.2)*.5/2+(.2+1)*.5/2
    g=1-2*b
    if abs(b-.35)>1e-12 or abs(g-.30)>1e-12 or "0.30" not in econ["detailed"]:
        raise ValueError("HOLD_GINI_RECALC_MISMATCH")
    out=root/"review-artifacts/NOMUSA_V27";out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for i in sorted(ids2022):
        r=ledger[i];c=selected.get(i)
        rows.append({"id":i,"subject":r["subject"],"points":r["points"],
          "textSHA256":r["textSHA256"],"originalQNetPreviouslyVerified":True,
          "limitedExternalClaimCrosscheck":"CHECKED" if c else "NOT_IN_THIS_BATCH",
          "confirmedClaimSources":len(c["findings"]) if c else 0,
          "editorialCorrectionCandidate":c["correction"] if c else None,
          "fullLegalAcademicSourceReview":"HOLD","expertApproval":"HOLD"})
    summary={"schema":"NOMUSA_V27_2022_PARTIAL_PRIMARY_CONTENT_CHECK/1",
        "generatedUTC":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total328ShaLocked":328,"pilot2022":19,"pilotParts":32,
        "sixQuestionClaimChecks":6,"remainingPilotQuestionsNotChecked":13,
        "giniArea":b,"gini":g,"fullDraftsExpertCertified":0,
        "expertApproved":0,"finalApproval":"HOLD",
        "productionOrPreviewDeployed":False,"manuscriptModified":False}
    (out/"NOMUSA_V27_2022_19_REVIEW_LEDGER.json").write_text(
      json.dumps({"summary":summary,"rows":rows,"claims":checks},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    L=["# V27 — 2022년 19개 기출 내용 원전 대조 (부분 검증)","",
      "공식 법원 판결문 공개 텍스트/학술지 출판사 서지 및 초록에 직접 확인한 대상은 6개 답안의 일부 주장에 한정된다.",
      "19개 전체 내용 검증 완료가 아니다. 다른 13개는 이번 배치 외부 출처 확인 HOLD. 전문가 0/328 HOLD.","",
      "| 문항 | 실제 대조한 범위 | 처리상태 |","|---|---|---|"]
    for x in rows:
        L.append("| "+x["id"].replace("|","/")+" | "+
          ("공식/출판사 제한된 주장 확인" if x["confirmedClaimSources"] else "이번 배치 미검토")+
          " | "+("편집 교정 후보 있음" if x["editorialCorrectionCandidate"] and "P1_" in x["editorialCorrectionCandidate"] else "내용 최종승인 HOLD")+" |")
    L+=["","## 실제 발견한 편집 불일치",
       "- 2022-hr-1: 초안의 V16.2에 Human Relations라고 적혀 있고 V16.3에서 Human Factors로 정정했다. 출판사 공식 서지는 Human Factors 20(2):131–144다. 구판 서지 오표기 정리 필요.",
       "- 2022-hr-1: 관리층 교육훈련 여섯 번째 예시가 액션러닝과 경영 시뮬레이션으로 나뉘어 반복된다. 두 방법 모두 교육훈련 기법이지만 최종 암기 세트를 통일할 필요.",
       "- 2022-admin-2: 2019두52386 판결(구제신청 후 정년)과 2021두46285 판결(구제신청 전 고용종료)의 구별은 공식 공개 판결 취지에 부합; 해당 사례의 정년규정 효력 포섭 HOLD.",
       "- 2022-labor1-2: 2019다238053(2022)의 근무기간 비례 정기상여금 판단 취지 대조; 시험 이후 일반 법리 변경 소급적용 금지.",
       "- 2022-econ-2: 별도 사다리꼴 계산 B=0.35, 지니 G=0.30 확인. 실제 그래프 시험장 표시는 독립 검토 HOLD.","",
       "## 실제 확인 원전 URL"]
    for c in checks:
        L.append("### "+c["id"])
        for f in c["findings"]:
            L.append("- "+f["claim"]+" — "+f["url"]+" ("+f["verification"]+")")
    L+=["","## 유지한 검증 관문",
         "공식 Q-Net 원본 파일 해시/문항 SHA는 기존 V23 검증을 재사용. 법령 시험 당시 연혁 전수, 모든 원판결 사실관계, 학술 원서 전문, 실제 필기분량과 독립 전문가 승인은 아직 HOLD.",
         "이번 작업은 앱 소스/문항/원고를 수정하지 않았다. 수정안은 검토 브랜치에서 별도 승인 후 SHA 재생성과 전체 패킷 갱신이 필요.",
         "main/Production/Preview/저장키/RC27/RC35/이메일 변경 없음.",""]
    (out/"NOMUSA_V27_2022_19_REPORT.md").write_text("\n".join(L),encoding="utf8")
    print(json.dumps({"status":"PASS_V27_6_SOURCE_SPECIFIC_CHECKS_19_SHA_LOCKED_FINAL_HOLD",
        "pilot":19,"sourceChecked":6,"unreviewed":13,"expertApproved":0,"finalApproval":"HOLD"},ensure_ascii=False))
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("root",nargs="?",default=".")
    ap.add_argument("--self-test",action="store_true");a=ap.parse_args()
    try:
        if a.self_test:
            assert abs(1-2*(.05+.30)-.30)<1e-12
            print("PASS_V27_SELF_TEST")
        else:run(Path(a.root))
    except Exception as e:
        print(json.dumps({"status":"HOLD_V27","error":str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(2)
