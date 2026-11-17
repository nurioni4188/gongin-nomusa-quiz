#!/usr/bin/env python3
"""V26-2 96-question evidence triage + V26-3 328-question/7-subject expert packs.
Actual official statutes, full decisions, original academic texts and handwriting
are never certified here. Read-only, no deployment, no emails, no expert approval.
"""
import argparse
import csv
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = "review/NOMUSA_V23_VALIDATION_LEDGER.json"
HEADS = "review/NOMUSA_V22_2022_OFFICIAL_PRECEDENT_CROSSCHECK.json"
CROSS = "review/NOMUSA_V23_CASE_3_CORROBORATION_20261117.json"
TEMPLATE = "review/NOMUSA_V21_INDEPENDENT_REVIEW_TEMPLATE.json"
SUBJECTS = {"labor1":"노동법Ⅰ","labor2":"노동법Ⅱ","admin":"행정쟁송법",
            "civil":"민사소송법","econ":"노동경제학",
            "hr":"인사노무관리론","org":"경영조직론"}
LAW = re.compile(r"제\s*\d+\s*조")
CASE = re.compile(r"(?:19|20)\d{2}(?:다|두|도|마|누|구합|구단|재|후|무)\d{2,7}")
HOLD = re.compile(r"HOLD|미확인|검토\s*필요|원전\s*확인",re.I)

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def sha(row):
    return hashlib.sha256((row["sourceText"]+"\0"+row["detailed"]+"\0"+
                           row["compressed"]).encode("utf-8")).hexdigest()

def subject(row):
    s=re.sub(r"\s+","",row["subject"]); i=row["id"].lower()
    for title,code in (("인사노무관리론","hr"),("경영조직론","org"),
                       ("노동경제학","econ"),("민사소송법","civil"),
                       ("행정쟁송법","admin")):
        if title==s:return code
    if "노동법" in s:
        if ("Ⅱ" in s or "2교시" in s or "노동법2" in s or
            "labor2" in i or "노동법2" in i):return "labor2"
        if ("Ⅰ" in s or "1교시" in s or "노동법1" in s or
            "labor1" in i or "노동법1" in i):return "labor1"
    raise ValueError("HOLD_SUBJECT:"+row["id"]+":"+s)

def load(root):
    doc=read(root/BASE); summary=doc["summary"]
    led={x["id"]:x for x in doc["rows"]}
    if len(led)!=328 or summary["total"]!=328 or summary["qnetOfficialByteIdentical"]!=328:
        raise ValueError("HOLD_BASELINE_328")
    if summary["storedQuestionIsSummary"]!=0 or summary["independentExpertApproved"]!=0 or summary["finalApproval"]!="HOLD (0/328)":
        raise ValueError("HOLD_BASELINE_APPROVAL")
    files=sorted((root/"review-artifacts").glob("nomusa_*_rendered*.json"))
    if len(files)!=20:raise ValueError("HOLD_EXPECT_20_BROWSER_EXPORTS")
    rows={}; years=set()
    for f in files:
        m=re.match(r"nomusa_(20\d{2})_",f.name)
        if not m or int(m.group(1)) in years:raise ValueError("HOLD_YEAR_EXPORT:"+f.name)
        year=int(m.group(1));years.add(year)
        for q in read(f)["rows"]:
            i=q["id"]
            if i in rows or q.get("scoringApproved") is not False or int(q["year"])!=year:
                raise ValueError("HOLD_RENDERED_ID_OR_SCORING:"+i)
            rows[i]=q
    if years!=set(range(2007,2027)) or set(rows)!=set(led):
        raise ValueError("HOLD_20YEARS_328_SET")
    for i,q in rows.items():
        r=led[i]
        if sha(q)!=r["textSHA256"] or int(q["points"])!=int(r["points"]) or q["subject"]!=r["subject"]:
            raise ValueError("HOLD_SHA_SCORE_SUBJECT:"+i)
        if not r["source"]["qnetOfficialByteIdentical"] or not r["source"]["pointsCheck"].startswith("PASS"):
            raise ValueError("HOLD_SOURCE_OR_POINTS:"+i)
        if r["verdicts"]["expertApproval"]!="HOLD_EXPERT_APPROVAL" or r["verdicts"]["finalApproval"]!="HOLD":
            raise ValueError("HOLD_EXPERT_STATE:"+i)
    p0={i for i,r in led.items() if r["year"]==2022}
    p1={i for i,r in led.items() if r["isLengthProxyPriority77"]}
    if len(p0)!=19 or len(p1)!=77 or p0.intersection(p1):
        raise ValueError("HOLD_PRIORITY_19_77")
    if sum(len(rows[i].get("parts") or []) for i in p0)!=32:
        raise ValueError("HOLD_2022_32_SUBPARTS")
    return rows,led,p0,p1

def claims(q,r,p0,p1,headlines,crosses):
    i=q["id"]; dom=subject(q)
    s=r["source"]; body=q["detailed"]+"\n"+q["compressed"]
    deficiency=max(0,{50:4000,25:2000}.get(int(q["points"]),0)-len(q["detailed"]))
    flags=[]
    if deficiency:flags.append("PROXY_LENGTH_DEFICIT_REAL_HANDWRITING_HOLD")
    if s["matchBand"]!="HIGH":flags.append("MEDIUM_OCR_OR_SOURCE_PROOFREAD_HOLD")
    if HOLD.search(body):flags.append("DRAFT_CONTAINS_EXPLICIT_HOLD_OR_UNVERIFIED_TEXT")
    if r["lawFlags"]:flags.append("HISTORIC_STATUTE_TIME_APPLICABILITY_REVIEW")
    if r["academicFlags"]:flags.append("ACADEMIC_YEAR_TITLE_REVIEW")
    if r["calcFlags"]:flags.append("CALC_OR_SYMBOLIC_RECHECK")
    if dom in ("labor1","labor2","admin","civil"):
        if not LAW.search(body):flags.append("NO_STATUTE_ARTICLE_TOKEN_NOT_PROOF_OF_ERROR")
        if not CASE.search(body):flags.append("NO_CASE_NUMBER_TOKEN_NOT_PROOF_OF_ERROR")
        flags.append("FULL_CASE_JUDGMENT_HISTORICAL_LAW_AND_FACT_APPLICATION_HOLD")
    elif dom in ("hr","org"):flags.append("ORIGINAL_ACADEMIC_AUTHOR_WORK_YEAR_HOLD")
    else:flags.append("FULL_ECON_MATH_GRAPH_AND_COMPARATIVE_STATICS_HOLD")
    flags.append("INDEPENDENT_EXPERT_AND_HANDWRITING_HOLD")
    cases=[];seen=set()
    for c in r["caseCitations"]:
        num=c["caseNo"]
        if num in seen:continue
        seen.add(num)
        h=[z for z in headlines.get(i,[]) if z["caseId"]==num]
        x=crosses.get(num)
        cases.append({"caseNo":num,"caseRegistry":c.get("lawGoKr"),
          "officialCaseName":c.get("caseName"),"officialDecisionDate":c.get("officialDecisionDate"),
          "statedDecisionDate":c.get("statedDate"),"caseSearchUrl":c.get("searchUrl"),
          "2022CourtHeadnote":h[0].get("officialUrl") if h else None,
          "separateCorroborationURLs":[z["url"] for z in x["sources"]] if x else [],
          "fullJudgmentActuallyRead":False,"answerFactApplicationChecked":False})
    return {"id":i,"year":int(q["year"]),"subject":q["subject"],"slug":dom,
     "points":int(q["points"]),"subquestionPoints":[p.get("points") for p in (q.get("parts") or [])],
     "priority":"P0_2022" if i in p0 else "P1_LENGTH_77" if i in p1 else "P2_P3_ROUTINE",
     "textSHA256":r["textSHA256"],"sourcePDF":s.get("repoFile"),
     "officialQNetPostUrl":s.get("qnetPostUrl"),"officialMember":s.get("qnetMember"),
     "officialMemberSHA256":s.get("qnetMemberSha256"),"officialByteMatchedInV23":True,
     "questionOverlapBand":s["matchBand"],"questionOverlapFraction":s.get("questionTextOverlap"),
     "pointsCheck":s.get("pointsCheck"),"detailedChars":len(q["detailed"]),
     "compressedChars":len(q["compressed"]),"lengthProxyDeficitChars":deficiency,
     "caseEvidenceCandidates":cases,"statuteFlags":r["lawFlags"],
     "academicPairsCandidates":r.get("academicPairs",[]),"academicFlags":r.get("academicFlags",[]),
     "arithmeticCandidateChecks":r.get("arithmeticChains",[]),
     "symbolicCandidateChecks":r.get("symbolicChains",[]),
     "mathFlags":r.get("calcFlags",[]),"economicsAIPrecalc":r.get("econManualRecalc"),
     "AI_precheckFlags":list(dict.fromkeys(flags)),
     "legalAcademicOriginalRead":False,"independentCharacterProofread":False,
     "independentExpertApproved":False,"finalApproval":"HOLD"}

def md_packet(q,e):
    p=q.get("parts") or []
    partlines=["- %s (%s점)" % (x.get("title") or x.get("name") or "소문항",x.get("points")) for x in p]
    case_lines=["- %s / 검색상태 %s / 선고일 %s / 검색 URL %s / 판결문 전문·법리 적용 HOLD" %
             (x["caseNo"],x.get("caseRegistry"),x.get("officialDecisionDate"),
              x.get("caseSearchUrl")) for x in e["caseEvidenceCandidates"]]
    lines=["# 독립 전문가 검토패킷: "+e["id"],"",
     "> 이 문서는 원전·답안·기존 사전검증 후보를 정리한 자료입니다. **전문가 승인서가 아닙니다.**",
     "> 원전 글자별 검수, 법령·판례 전문, 학술 원저, 필기 실측, 전문가 최종승인 HOLD.","",
     "## 고정 문항 정보",
     "- 연도/과목/배점: %d / %s / %d점" %(e["year"],e["subject"],e["points"]),
     "- 우선순위: "+e["priority"],
     "- 문항 ID: "+e["id"],"- 현재 학습원고 SHA-256: "+e["textSHA256"],
     "- 공식 Q-Net 게시물: "+str(e["officialQNetPostUrl"]),
     "- 공식 첨부 구성원: "+str(e["officialMember"]),
     "- 구성원 SHA-256: "+str(e["officialMemberSHA256"]),
     "- 저장소 원본 파일: "+str(e["sourcePDF"]),
     "- PDF/HWP 공식 원본 파일 바이너리 일치: V23 확인",
     "- 전사원문 일치등급(자동): "+e["questionOverlapBand"],"",
     "## 기출문제 원문 (기계/AI 전사, 사람 글자별 교열 HOLD)","",q["sourceText"],"",
     "## 소문항별 배점",*(partlines or ["- 소문항 구조 별도 검토"]),"",
     "## 상세 학습답안 — 승인 전 초안","",q["detailed"],"",
     "## 시험장 압축답안 — 승인 전 초안","",q["compressed"],"",
     "## 내용 위험 사전검증 및 누락 점검",*(["- "+z for z in e["AI_precheckFlags"]]),"",
     "- 500자/쪽 분량 프록시 부족 추정: %d자 (실제 필기분량 증빙 아님)" %
       e["lengthProxyDeficitChars"],"",
     "## 판례 인용 근거 후보",*(case_lines or ["- 판례 사건번호 탐색 미검출. 필요 여부 별도 검토."]),"",
     "## 학술 원전 확인 후보 (AI 추출, 원서 전문 미열람)",
     json.dumps(e["academicPairsCandidates"],ensure_ascii=False,indent=2),"",
     "## 계산·수식 독립검산 후보 (AI 검사 범위만 표시)",
     json.dumps({"arithmetic":e["arithmeticCandidateChecks"],
                 "symbolic":e["symbolicCandidateChecks"],"manualAI":e["economicsAIPrecalc"],
                 "flags":e["mathFlags"]},ensure_ascii=False,indent=2),"",
     "## 검토 요청",
     "1. 해당 연도 공식 원본 문제·수식·그림·소문항/배점과 전사를 글자별 대조.",
     "2. 법률: 시험 당시 연혁법령/부칙, 원판결 전문/선고일/법리/사안포섭 대조.",
     "3. 학술: 학자·원서·원논문 발행연도·연구모형의 실제 원전 대조.",
     "4. 경제학: 수식·그래프 축·조건·경계해·비교정태 독립 검산.",
     "5. 실제 필기 장수·시간 실측 및 배점별 논증 밀도 평가.",
     "6. 옆 폴더 회신 JSON의 검토자/자격/검토일/원전/의견은 전문가가 직접 기입.","",
     "**독립 전문가 승인: HOLD (0/328).**",""]
    return "\n".join(lines)

def attest(template,q,e):
    t=json.loads(json.dumps(template,ensure_ascii=False))
    t["questionId"]=q["id"];t["draftTextSHA256"]=e["textSHA256"]
    t["exam"]["year"]=e["year"]
    t["exam"]["pdfSourceUrl"]=e["officialQNetPostUrl"] or ""
    t["exam"]["pdfSHA256"]=e["officialMemberSHA256"] or ""
    t["decision"]="HOLD_UNREVIEWED_TEMPLATE"
    t["notes"]="자동완성/자동서명 금지. 자격·독립성·원전·검토일·서면결론은 실제 전문가만 기입."
    return t

def zip_files(path,base,paths):
    with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_DEFLATED,allowZip64=True) as z:
        for p in sorted(paths):
            z.write(p,arcname=p.relative_to(base).as_posix())
        if z.testzip() is not None:raise ValueError("HOLD_INVALID_ZIP")

def generate(root,out):
    out.mkdir(parents=True,exist_ok=True)
    rows,led,p0,p1=load(root)
    heads=defaultdict(list)
    for h in read(root/HEADS)["rows"]:heads[h["id"]].append(h)
    crosses={x["caseNo"]:x for x in read(root/CROSS)["cases"]}
    base_template=read(root/TEMPLATE)
    packroot=out/"NOMUSA_V26_3_EXPERT_PACKETS";packroot.mkdir(exist_ok=True)
    zroot=out/"NOMUSA_V26_3_SUBJECT_ZIPS";zroot.mkdir(exist_ok=True)
    files=defaultdict(list);evidence=[];register=[];priority_paths=[]
    for i in sorted(rows,key=lambda x:(rows[x]["year"],x)):
        q=rows[i];r=led[i];e=claims(q,r,p0,p1,heads,crosses)
        slug=e["slug"];dst=packroot/slug
        (dst/"questions").mkdir(parents=True,exist_ok=True)
        (dst/"attestations").mkdir(parents=True,exist_ok=True)
        key="%d_%s"%(e["year"],hashlib.sha256(i.encode()).hexdigest()[:18])
        md=dst/"questions"/(key+".md");att=dst/"attestations"/(key+".review.json")
        md.write_text(md_packet(q,e),encoding="utf-8")
        att.write_text(json.dumps(attest(base_template,q,e),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        files[slug].extend([md,att])
        evidence.append(e)
        register.append({"id":i,"year":e["year"],"subject":e["subject"],
          "slug":slug,"points":e["points"],"priority":e["priority"],
          "textSHA256":e["textSHA256"],"questionMd":md.relative_to(out).as_posix(),
          "expertReplyJson":att.relative_to(out).as_posix(),"status":"HOLD_UNSENT"})
        if i in p0 or i in p1:priority_paths.extend([md,att])
    if len(evidence)!=328 or set(files)!=set(SUBJECTS):
        raise ValueError("HOLD_328_OR_7_SUBJECTS")
    p=[e for e in evidence if e["id"] in p0 or e["id"] in p1]
    if len(p)!=96 or Counter(x["priority"] for x in p)!=Counter({"P0_2022":19,"P1_LENGTH_77":77}):
        raise ValueError("HOLD_P0_P1_COUNTS")
    flags=Counter(f for e in p for f in e["AI_precheckFlags"])
    summary={"schema":"NOMUSA_V26_2_3/1","generatedUTC":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "baselineSHA256":hashlib.sha256((root/BASE).read_bytes()).hexdigest(),
      "total":328,"years":20,"qnetSourceConfirmedInV23":328,
      "V26_2_pilot2022":19,"V26_2_subquestions2022":32,"V26_2_lengthProxy":77,
      "V26_2_totalPriority":96,"V26_3_subjects":7,
      "subjectCounts":dict(Counter(x["slug"] for x in evidence)),
      "uncorrectedSourceMedium":sum(x["questionOverlapBand"]=="MEDIUM" for x in evidence),
      "independentExpertApproved":0,"finalApproval":"HOLD",
      "actualFullLegalAcademicOriginalReview":False,
      "humanCertifiedSourceProofread":False,"expertEmailsSent":False,"deployment":False}
    (out/"NOMUSA_V26_2_96_CONTENT_PRECHECK.json").write_text(
      json.dumps({"summary":summary,"rows":p},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"NOMUSA_V26_3_328_ROUTING.json").write_text(
      json.dumps({"summary":summary,"rows":register},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for slug,title in SUBJECTS.items():
        count=len(files[slug])//2
        welcome=packroot/slug/"README.md"
        welcome.write_text("# "+title+" 전문가 검토패킷\n\n문항 "+str(count)+
          "개. 독립 전문가 최종승인 HOLD. Q-Net 원본은 링크와 SHA로 제공하며 PDF를 별도 첨부하지 않음.\n"
          "questions/ 원문·상세·압축 및 attestations/ 실제 전문가 회신용 빈 양식을 확인.\n",encoding="utf-8")
        name=zroot/("NOMUSA_V26_3_"+slug+"_"+str(count)+".zip")
        zip_files(name,packroot/slug,files[slug]+[welcome])
    zip_files(out/"NOMUSA_V26_2_PRIORITY_2022_19_PLUS_77.zip",out,priority_paths)
    csvfile=out/"NOMUSA_V26_3_328_DISPATCH_TRACKER.csv"
    with csvfile.open("w",encoding="utf-8-sig",newline="") as file:
        w=csv.writer(file)
        w.writerow(["id","year","subject","points","priority","textSHA256",
                    "packetFile","attestationFile","reviewer","dispatchDate","returnDate",
                    "independentReview","expertApproval"])
        for x in register:
            w.writerow([str(v) if str(v)[:1] not in "=+-@" else "'"+str(v) for v in
                [x["id"],x["year"],x["subject"],x["points"],x["priority"],x["textSHA256"],
                 x["questionMd"],x["expertReplyJson"],"","","","HOLD_UNSENT","HOLD"]])
    lines=["# V26-2: 2022년 19 + 분량 우선검토 77 = 96개 사전검증","",
      "AI/기존 V23 원전 대조자료를 재사용한 **검토용 근거 연결 및 위험 탐지**입니다.",
      "시험 당시 법령/원판결 전문·학술 원저·손글씨 실측의 독립검증 또는 내용승인이 아님.","",
      "## 결과","",
      "- 2022년 19개 / 소문항 32개, 분량 프록시 P1 77개, 중복 없는 96개.",
      "- 각 문항 SHA와 기출 원전·배점·판례/저자/수식 추출 후보 일대일 연결.",
      "- 공식 원본 328 SHA 대조는 기존 V23 검사 결과를 사용; 공식 원본 실시간 재다운로드 없음.",
      "- 독립 전문가 최종 내용승인 0/328, 모든 시험 당시 원전 전문 검증 HOLD.","",
      "## 사전검증 항목별 건수","",
      "| 사전검증 플래그 | 문항수 |","|---|---:|"]
    lines.extend("| "+flag+" | "+str(n)+" |" for flag,n in flags.most_common())
    lines.extend(["","## 96개 우선검토 대상","",
                 "| 문항ID | 과목 | 배점 | 분량 프록시 부족자수 |",
                 "|---|---|---:|---:|"])
    for x in p:
        lines.append("| "+x["id"].replace("|"," / ")+" | "+x["subject"]+" | "+
                     str(x["points"])+" | "+str(x["lengthProxyDeficitChars"])+" |")
    lines.extend(["","FINAL_APPROVAL = HOLD, 전문가 승인 = 0/328.",""])
    (out/"NOMUSA_V26_2_96_PRECHECK_REPORT.md").write_text("\n".join(lines),encoding="utf-8")
    index=["# V26-3: 328개 과목별 전문가 검토 패킷","",
      "**7개 ZIP, 328개 문제 + 328개 빈 검토자 서식. 이메일 발송 없음. 전문가 승인 0/328 HOLD.**",
      "기출 PDF/HWP 원본은 재배포하지 않고 Q-Net 공식 링크와 SHA를 제공.","",
      "| 과목 | 문항 | ZIP |","|---|---:|---|"]
    for slug,title in SUBJECTS.items():
        n=len(files[slug])//2
        index.append("| "+title+" | "+str(n)+" | NOMUSA_V26_3_SUBJECT_ZIPS/NOMUSA_V26_3_"+slug+"_"+str(n)+".zip |")
    index.extend(["","검토 순서: 원문 인쇄면·법령·판례·학술·수식·실제 필기분량 → 검토자 자격·검토일·근거·서면의견 → 동일 SHA 문항별 승인.",
                  "현재 승인된 답안은 0개이며 자동입력된 실명·서명·검토일은 없습니다.",""])
    (out/"NOMUSA_V26_3_DISPATCH_INDEX.md").write_text("\n".join(index),encoding="utf-8")
    forms=0
    for slug in SUBJECTS:
        n=len(files[slug])//2
        with zipfile.ZipFile(zroot/("NOMUSA_V26_3_"+slug+"_"+str(n)+".zip")) as z:
            if z.testzip() is not None:raise ValueError("HOLD_ZIP_CRC:"+slug)
            forms+=sum(x.startswith("attestations/") and x.endswith(".review.json") for x in z.namelist())
    with zipfile.ZipFile(out/"NOMUSA_V26_2_PRIORITY_2022_19_PLUS_77.zip") as z:
        if z.testzip() is not None or len(z.namelist())!=192:
            raise ValueError("HOLD_PRIORITY_ZIP_96")
    if forms!=328:raise ValueError("HOLD_328_EXPERT_BLANK_FORMS:"+str(forms))
    print(json.dumps({"status":"PASS_96_AI_PRECHECK_328_EXPERT_PACKETS_FINAL_APPROVAL_HOLD",
      "pilot2022":19,"subquestions2022":32,"priority77":77,
      "total96":96,"subjectZips":7,"expertPackets":328,"unfilledReviewForms":forms,
      "expertApproved":0,"deployed":False,"emailsSent":False},ensure_ascii=False))
    return summary

def test():
    assert subject({"subject":"노동법","id":"2026-노동법2|1|1"})=="labor2"
    assert subject({"subject":"노동법 1교시","id":"2015_p1_q1"})=="labor1"
    assert subject({"subject":"노동법Ⅱ","id":"2022-labor2-2"})=="labor2"
    assert hashlib.sha256(b"abc").hexdigest()=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    print("PASS_V26_2_3_SELF_TEST")

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("root",nargs="?",default=".")
    a.add_argument("--out",default="review-artifacts/NOMUSA_V26")
    a.add_argument("--self-test",action="store_true")
    args=a.parse_args()
    try:
        if args.self_test:test()
        else:generate(Path(args.root).resolve(),Path(args.root).resolve()/args.out)
    except Exception as ex:
        print(json.dumps({"status":"HOLD_V26_2_3","error":str(ex)},ensure_ascii=False),file=sys.stderr)
        sys.exit(2)
