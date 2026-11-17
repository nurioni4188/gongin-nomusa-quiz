#!/usr/bin/env python3
"""V22 original-PDF comparison and independent-expert review packets.

Only verifies what repository PDF bytes and browser drafts can establish.
A matching repository PDF is NOT proof it equals the official Q-Net attachment.
No legal precedent, scholarly authority, or external expert is auto-approved.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OFFICIAL_2022 = "https://www.q-net.or.kr/cst003.do?artlSeq=5210985&boardId=Q004&gId=05&gSite=L&id=cst00302"
SUBJECT_TO_SLUG = {
    "행정쟁송법": "admin", "민사소송법": "civil",
    "노동경제학": "econ", "인사노무관리론": "hr", "경영조직론": "org",
    "노동법1": "labor1", "노동법Ⅰ": "labor1", "노동법2": "labor2",
    "노동법Ⅱ": "labor2", "노동법Ⅰ/Ⅱ": "labor1",
}
# 2019/2020 filenames are matched by subject, not p-number guessed from ID.
SPECIAL_YEAR_SLUG = {
    2019: {"admin":1,"org":2,"econ":3,"civil":4,"labor1":5,"labor2":6,"hr":7},
    2020: {"labor1":1,"labor2":2,"hr":3,"admin":4,"org":5,"econ":6,"civil":7},
}
SPECIAL_LABEL = {
    "admin":"administrative","org":"organization","econ":"labor_economics",
    "civil":"civil_procedure","labor1":"labor1","labor2":"labor2","hr":"hrm"
}
HEADER = ("id","year","subject","points","sourceFile","repoSha256","binaryAvailable",
          "officialAttachmentMatch","pdfTextLayer","machineQuestionOverlap","bestPage",
          "autoSourceStatus","caseLawSourceStatus","academicOriginalStatus",
          "equationVerificationStatus","expertStatus","draftTextSHA256")
NORM = re.compile(r"[^가-힣a-zA-Z0-9]+")
HANGUL = re.compile(r"[가-힣]")
SPECIAL_YEAR_PATTERN = re.compile(r"(20\d\d)_p\d+_")
def sha_bytes(data: bytes)->str:
    return hashlib.sha256(data).hexdigest()
def sha_text(data: str)->str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()
def norm(s: str)->str:
    return NORM.sub("",s).lower()
def overlap(q: str, p: str, n:int=8)->float:
    a=norm(q);b=norm(p)
    if len(a)<n or len(b)<n:return 0.
    grams=set(a[i:i+n] for i in range(0,len(a)-n+1))
    return round(sum(s in b for s in grams)/len(grams),4) if grams else 0.
def slug(subj:str)->str|None:
    return SUBJECT_TO_SLUG.get(subj.replace(" ",""))
def paths_for(row:dict)->list[str]:
    year=int(row["year"]);name=slug(str(row["subject"]))
    if year<=2012:
        return []
    if 2013<=year<=2018:
        return [f"source_pdf/{year}/{year}_second_full_original.pdf"]
    if year==2021:
        # Day assignment is not yet an independently checked fact.
        return ["source_pdf/2021/2021_day1.pdf","source_pdf/2021/2021_day2.pdf"]
    if not name:
        return []
    if year in (2019,2020):
        p=SPECIAL_YEAR_SLUG[year].get(name)
        return [f"source_pdf/{year}/{year}_p{p}_{SPECIAL_LABEL[name]}.pdf"] if p else []
    return [f"source_pdf/{year}/{year}_{name}.pdf"]

def load(root:Path):
    items={}
    files=sorted((root/"review-artifacts").glob("nomusa_*_rendered*.json"))
    if len(files)!=20:raise ValueError(f"HOLD_20_YEAR_BROWSER_DATA_{len(files)}")
    for f in files:
        obj=json.loads(f.read_text(encoding="utf-8"))
        for row in obj["rows"]:
            if row["id"] in items:raise ValueError("HOLD_ID_DUPLICATE")
            items[row["id"]]=row
    if len(items)!=328 or sum(int(x["year"])==2022 for x in items.values())!=19:
        raise ValueError("HOLD_328_2022_COUNTS")
    v21=json.loads((root/"review-artifacts/NOMUSA_V21_328_APPROVAL_TRIAGE.json").read_text(encoding="utf-8"))
    old={r["id"]:r for r in v21["rows"]}
    if set(items)!=set(old):raise ValueError("HOLD_V21_ID_DIFFERENCE")
    for id,row in items.items():
        source=str(row["sourceText"]);detail=str(row["detailed"]);compact=str(row["compressed"])
        now=sha_text(source+"\0"+detail+"\0"+compact)
        if now!=old[id]["textSHA256"]:
            raise ValueError("HOLD_REVIEW_DRAFT_SHA_CHANGED_"+id)
    return items,old

def first_2022_pdf_check(path:Path, source:str, out:Path, cap:int=10):
    import fitz
    doc=fitz.open(path)
    pages=[doc.load_page(i).get_text("text") or "" for i in range(len(doc))]
    combined="\n".join(pages)
    scores=[overlap(source, t) for t in pages]
    page=(scores.index(max(scores))+1) if scores and max(scores)>0 else None
    if not any(HANGUL.search(x) for x in pages):
        state="HOLD_NO_KOREAN_TEXT_LAYER_MANUAL_VISUAL"
    else:
        full=overlap(source,combined)
        if full>=0.70:
            state="CANDIDATE_HIGH_TEXT_ALIGNMENT_VISUAL_REVIEW_REQUIRED"
        elif full>=0.35:
            state="HOLD_PARTIAL_TEXT_ALIGNMENT"
        else:
            state="HOLD_PDF_SOURCE_TEXT_MISMATCH_OR_OCR_NEEDED"
    return pages,round(overlap(source,combined),4),page,state

def write_csv(path,rows):
    if not rows:return
    with path.open("w",encoding="utf-8-sig",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0]),extrasaction="ignore")
        w.writeheader()
        for r in rows:
            vals={k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()}
            for k,v in vals.items():
                if isinstance(v,str) and v.startswith(("=","+","-","@")):vals[k]="'"+v
            w.writerow(vals)

def build(root:Path)->dict:
    t=time.monotonic();start=datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows,v21=load(root)
    out=root/"review-artifacts";out.mkdir(exist_ok=True)
    pack=out/"NOMUSA_V22_2022_EXPERT_PACKETS";pack.mkdir(exist_ok=True)
    previews=out/"NOMUSA_V22_2022_PDF_PAGE_PREVIEWS";previews.mkdir(exist_ok=True)
    audit=[];pdfcache={}
    for id,q in sorted(rows.items(),key=lambda z:(z[1]["year"],z[0])):
        paths=paths_for(q)
        found=[p for p in paths if (root/p).is_file()]
        p=found[0] if len(found)==1 else ""
        hit=v21[id];sHash=hit["textSHA256"];corpus=""
        status="HOLD_SOURCE_BINARY_NOT_IN_REPO"
        textLayer="NOT_CHECKED";sim=None;best=None;size=0;original_sha=""
        if len(found)>1:
            status="HOLD_MULTIPLE_DAY_PDF_CANDIDATES"
        elif p:
            pdf=root/p;size=pdf.stat().st_size
            if pdf.suffix.lower()!=".pdf" or pdf.read_bytes()[:5]!=b"%PDF-":
                raise ValueError("HOLD_INVALID_PDF_BINARY_"+p)
            original_sha=sha_bytes(pdf.read_bytes())
            status="HOLD_OFFICIAL_IDENTITY_NOT_PROVEN"
            if int(q["year"])==2022:
                pages,sim,best,status=first_2022_pdf_check(pdf,str(q["sourceText"]),out)
                textLayer="KOREAN_SEARCHABLE" if status!="HOLD_NO_KOREAN_TEXT_LAYER_MANUAL_VISUAL" else "HOLD_KOREAN_NOT_FOUND"
                # Q-Net original ZIP has NOT been downloaded and byte-compared, so no official-authentication PASS.
                if id not in pdfcache:
                    pdfcache[id]={"pages":pages}
        data={
          "id":id,"year":int(q["year"]),"subject":q["subject"],"points":int(q["points"]),
          "sourceFile":p or (";".join(found) if found else ";".join(paths)),
          "repoSha256":original_sha,"binaryAvailable":bool(p),
          "officialAttachmentMatch":"HOLD_NOT_BYTE_COMPARED_WITH_QNET_OFFICIAL",
          "pdfTextLayer":textLayer,"machineQuestionOverlap":sim,"bestPage":best,
          "autoSourceStatus":status,
          "caseLawSourceStatus":"HOLD_HISTORICAL_CASE_AND_STATUTE_PRIMARY_TEXT",
          "academicOriginalStatus":"HOLD_OR_NOT_APPLICABLE",
          "equationVerificationStatus":"HOLD_OR_NOT_APPLICABLE",
          "expertStatus":"HOLD_NO_INDEPENDENT_REVIEWER_SIGNOFF",
          "draftTextSHA256":sHash
        }
        audit.append(data)
        if int(q["year"])==2022:
            src=str(q["sourceText"]);detail=str(q["detailed"]);comp=str(q["compressed"])
            parts=q.get("parts") or [];pt=sum(int(x["points"]) for x in parts)
            if pt!=int(q["points"]):raise ValueError("HOLD_2022_PARTS_"+id)
            lines=[
                "# 2022년 공인노무사 2차 — "+str(q["subject"])+" / "+id,
                "",
                "**독립 검토자 제출용 초안. 승인서 아님.**",
                "",
                "## 문제지 대조 현황",
                "- 원문 확인 출처 후보: ["+str(p)+"](../../source_pdf/2022/"+Path(p).name+")" if p else "- 원문 PDF 후보: 미확정",
                "- 저장소 PDF SHA-256: "+(original_sha or "UNKNOWN"),
                "- 시험 주관기관 공식 2022 문제지 게시물: "+OFFICIAL_2022,
                "- Q-Net ZIP의 원본 해시와 저장소 PDF **직접 비교 미완료**",
                "- PDF/전사 텍스트 일치 후보(8글자 연속조각): "+str(sim),
                "- 최고 일치 PDF 페이지: "+str(best or "미확정"),
                "- 상태: "+status,"",
                "## 실제 기출 원문 전사 (PDF 시각 대조 필수)","",src,"",
                "## 배점별 소문항",
            ]
            lines += ["- "+str(z.get("title","")).strip()+" / "+str(z.get("points"))+"점" for z in parts]
            lines += ["","## 최신 상세답안 — 검토대상 SHA 고정","",
                "- 문항 ID: "+id,
                "- 원문+상세+압축 SHA-256: "+sHash,
                "","",detail,"",
                "## 시험장 압축답안","",comp,"",
                "## 원전대조 및 승인 체크리스트 — 전문가 입력 필수",
                "- [ ] Q-Net 원본 문제지 첨부파일과 저장소 PDF 동일성 확인",
                "- [ ] 문제의 사진·표·그래프·수식·배점·쪽수를 시각 대조",
                "- [ ] 시험일 시행 법률/부칙/판례 원문 또는 학술 저서·논문·연도를 대조",
                "- [ ] 논증·사안포섭·경제모형·그림의 충돌/누락 교정",
                "- [ ] 실제 필기분량/작성속도 실측",
                "- [ ] 독립 검토자 신원·자격·검토일·근거·서명 의견 등록",
                "- [ ] 검토 뒤 원고 SHA 변동이 있는지 재검증",
                "",
                "최종 전문가 내용승인: **HOLD** (임의 승인 금지).",""
            ]
            (pack/(id.replace("/","_")+"-review.md")).write_text("\n".join(lines),encoding="utf-8")
    if len(audit)!=328 or sum(z["year"]==2022 for z in audit)!=19:
        raise ValueError("HOLD_328_OR_2022_COVERAGE")
    for r in audit:
        if r["year"]==2022 and (not r["binaryAvailable"] or not r["repoSha256"]):
            raise ValueError("HOLD_2022_PDF_MISSING_"+r["id"])
    info=Counter(x["autoSourceStatus"] for x in audit)
    summaries={
        "schema":"NOMUSA_V22_ORIGINAL_COMPARE_EXPERT_PACKETS/1",
        "status":"PASS_REPO_PDF_COMPARISON_CANDIDATES_EXPERT_HOLD",
        "total":328,"years":20,"pilot2022":19,
        "sourceStatusCounts":dict(info),
        "pilot2022MachineHighAlignment":sum(x["year"]==2022 and x["autoSourceStatus"]=="CANDIDATE_HIGH_TEXT_ALIGNMENT_VISUAL_REVIEW_REQUIRED" for x in audit),
        "pilot2022PDFWithText":sum(x["year"]==2022 and x["pdfTextLayer"]=="KOREAN_SEARCHABLE" for x in audit),
        "pilot2022IndependentExpertApproved":0,
        "independentExpertApproved":0,
        "officialQNetAttachmentByteCompared":False,
        "originalPDFVisualReviewDone":False,
        "reviewerSignaturesProvided":False,
        "official2022SourcePage":OFFICIAL_2022,
        "startedUTC":start,
        "finishedUTC":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scriptSeconds":round(time.monotonic()-t,3),
        "noDeploymentNoMutationOfOriginals":True
    }
    write_csv(out/"NOMUSA_V22_328_SOURCE_EXPERT_ROUTING.csv",audit)
    (out/"NOMUSA_V22_328_ORIGINAL_AUDIT.json").write_text(json.dumps({"summary":summaries,"rows":audit},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# NOMUSA V22 — 원본 PDF 대조 및 독립전문가 심사 패킷","",
        "## 검증 가능한 범위",
        "- 20개년/328개 원고, SHA256 확인, 2022년 19개 PDF 원전 후보 대조.",
        "- PDF 자체는 저장소 파일이며 **Q-Net 공식 ZIP과 해시 동등성 미확인**.",
        "- OCR 불가/텍스트층 누락이나 연도 2021 day1/day2 중복후보, 2007~2012 HWP 원본 바이너리 미존재는 HOLD.",
        "- 기출 전사 원문이 PDF 본문에 어느 정도 나타나는지 텍스트 조각 일치도는 **사전후보 신호**로만 기록. 사람이 그림·수식·최초 게시물의 출처를 확인해야 한다.",
        "- 근거법령과 판례원전·학술원전의 실제 검증 및 전문가 결론은 여전히 HOLD.",
        "","## 상태별 건수",
        "| 상태 | 답안 수 |","|---|---:|"]
    lines += ["| "+k+" | "+str(v)+" |" for k,v in sorted(info.items())]
    lines += ["","## 2022년 19개 전문검토 패킷","",
      "| 문항 | 과목 | PDF SHA-256(앞12자) | 일치도 | 검증상태 |",
      "|---|---|---|---:|---|"]
    for a in audit:
        if a["year"]==2022:
            lines.append("| "+a["id"]+" | "+a["subject"]+" | "+a["repoSha256"][:12]+" | "+str(a["machineQuestionOverlap"] or "HOLD")+" | "+a["autoSourceStatus"]+" |")
    lines += ["","## 전문가 승인을 위한 증빙 조건",
      "1. PDF 원본 공식성 확인(Q-Net ZIP의 파일해시·쪽수·도표 등).",
      "2. 답안의 시험 당시 법령·판례 및 인용된 판례의 정확성 또는 학술원전의 저자·연도·모형 원문 확인.",
      "3. 경제학의 원문 숫자·수식·경계조건·그래프 독립검산.",
      "4. 실제 필기분량 측정 및 비교, 소문항 단위 분량 구분.",
      "5. 외부 독립전문가의 검토일, 실명/자격, 근거, 수정의견, 고정 SHA에 대한 서면결론.",
      "", "**자동 비교는 전문가 승인 0/328을 변경하지 않는다.**",""]
    (out/"NOMUSA_V22_ORIGINAL_COMPARE_REPORT.md").write_text("\n".join(lines),encoding="utf-8")
    return summaries

def selftest():
    assert overlap("【문제 1】가나다라 마바사","문제 1 가나다라 마바사")>0.90
    assert overlap("대한민국한글가나다","영어English987")==0
    assert paths_for({"year":2022,"subject":"노동법1"})==["source_pdf/2022/2022_labor1.pdf"]
    assert paths_for({"year":2019,"subject":"행정쟁송법"})==["source_pdf/2019/2019_p1_administrative.pdf"]
    assert paths_for({"year":2012,"subject":"노동법1"})==[]
    assert len(paths_for({"year":2021,"subject":"노동법1"}))==2
    print("PASS_V22_SOURCE_MAPPING_SELFTEST")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("root",nargs="?",default=".")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    try:
        if a.self_test:selftest()
        else:print(json.dumps(build(Path(a.root)),ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"status":"HOLD_V22_SOURCE_COMPARE","error":str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2
    return 0
if __name__=="__main__":sys.exit(main())
