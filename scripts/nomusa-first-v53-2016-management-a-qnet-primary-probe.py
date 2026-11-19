#!/usr/bin/env python3
"""V53: search nearby real Q-Net source article IDs for 2016 A management PDF.
Only exact Q-Net public fileDown HTML attachment arguments are accepted; no
invented PDF links. If found, re-download and SHA-check PDF, stage 125 IDs'
year/subject source candidate only. NO individual question approval or grading.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json,re,urllib.parse
import requests
from bs4 import BeautifulSoup
import fitz

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V53"
OUT.mkdir(parents=True,exist_ok=True)
TARGET=ROOT/"review/NOMUSA_FIRST_V50_686_OFFICIAL_SOURCE_SHA_SUMMARY_20261118.json"
ARTICLE_IDS=[i for i in range(5182983,5183021) if i not in (5183001,5183003)]
HEADERS={"User-Agent":"Mozilla/5.0 Chrome/124.0","Referer":"https://www.q-net.or.kr/"}

def sha(b):return hashlib.sha256(b).hexdigest()
def search_article(n):
    url="https://www.q-net.or.kr/cst003.do?"+urllib.parse.urlencode({
        "artlSeq":n,"boardId":"Q004","gId":"05","gSite":"L",
        "id":"cst00302","menuType":"cst00309"})
    try:
        r=requests.get(url,headers=HEADERS,timeout=(8,20))
        r.raise_for_status()
        soup=BeautifulSoup(r.text,"html.parser")
        fileRows=[]
        for block in soup.select("div.file"):
            p=block.find("p")
            btn=block.find("button",onclick=True)
            if not p or not btn:continue
            label=p.get_text(" ",strip=True)
            compact=re.sub(r"\s+","",label).lower()
            if not ("경영" in compact and ("a형" in compact or "Ａ형" in compact)):
                continue
            m=re.search(r"fileDown\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'(\d+)'\s*\)",btn.get("onclick",""))
            if not m:continue
            file_path,filename,file_seq=m.groups()
            if file_path!="bbs/Q004/Q004_"+file_seq or filename!=label or not filename.lower().endswith((".pdf",".zip")):
                continue
            base="https://www.q-net.or.kr/cst003.do?"
            args=[("id","cst00302s01"),("gSite","L"),("gId","05"),("fileCode","R001"),
                  ("filePath",file_path),("fileName",filename),
                  ("fileSeq",file_seq),("artlSeq",str(n)),("href","0")]
            direct=base+urllib.parse.urlencode(args)
            fileRows.append({"label":label,"fileSeq":file_seq,"filePath":file_path,"download":direct})
        # Prevent misidentifying unrelated articles despite menu items:
        main_text=" ".join(soup.get_text(" ",strip=True).split())
        titleCheck=("2016" in main_text and "공인노무사" in main_text)
        return {"article":n,"url":url,"officialPageReached":True,
            "articleMatched2016LaborExam":titleCheck,
            "candidateAFiles":fileRows[:3]}
    except Exception as e:
        return {"article":n,"url":url,"officialPageReached":False,
                "error":type(e).__name__+":"+str(e)[:150],"candidateAFiles":[]}

def main():
    existing=json.loads(TARGET.read_text(encoding="utf-8"))
    assert existing["newOfficialAFormBookletSHAConnections"]==175
    assert existing["remainingWithoutQNetOriginalPDF"]==316
    found=[]
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures=[ex.submit(search_article,n) for n in ARTICLE_IDS]
        for fu in as_completed(futures):found.append(fu.result())
    found.sort(key=lambda a:a["article"])
    candidates=[(a,rec) for a in found if a.get("articleMatched2016LaborExam")
                for rec in a["candidateAFiles"]]
    verified=[]
    for page,rec in candidates:
        try:
            r=requests.get(rec["download"],headers=HEADERS,timeout=(10,100),stream=True)
            r.raise_for_status()
            data=bytearray()
            for part in r.iter_content(512*1024):
                data.extend(part)
                if len(data)>70_000_000:raise ValueError("SOURCE_SIZE_LIMIT")
            blob=bytes(data)
            if not blob.startswith(b"%PDF"):raise ValueError("NOT_DIRECT_PDF_A")
            doc=fitz.open(stream=blob,filetype="pdf")
            if len(doc)<25:raise ValueError("PDF_PAGES_TOO_FEW")
            evidence={"article":page["article"],"sourceArticle":page["url"],
                "officialSourceURL":rec["download"],"filename":rec["label"],
                "fileSeq":rec["fileSeq"],"sourcePDFSHA256":sha(blob),
                "pdfPages":len(doc),"pdfBytes":len(blob),
                "bookletAFromQNetFilename":"A형" in rec["label"]}
            doc.close()
            if evidence["bookletAFromQNetFilename"]:
                name=OUT/("2016_QNET_management_A_"+str(page["article"])+".pdf")
                name.write_bytes(blob)
                evidence["artifactFile"]=name.name
                verified.append(evidence)
        except Exception as e:
            verified.append({"article":page["article"],"status":"SOURCE_ATTACHMENT_HOLD",
                            "error":type(e).__name__+":"+str(e)[:150]})
    good=[v for v in verified if v.get("sourcePDFSHA256")]
    # More than one official A-booklet source is ambiguous: no candidate promotion.
    finalSource=good[0] if len(good)==1 else None
    status="PASS_SINGLE_QNET_A_BOOKLET_SHA_CANDIDATE_REVIEW_HOLD" if finalSource else "HOLD_OFFICIAL_A_BOOKLET_NOT_UNIQUELY_CONFIRMED"
    result={"schema":"NOMUSA_FIRST_V53_2016_MANAGEMENT_A_QNET_SOURCE_PROBE/1",
        "asOfKST":"2026-11-18",
        "searchedArticleCount":len(ARTICLE_IDS),
        "pagesResponded":sum(x["officialPageReached"] for x in found),
        "2016ManagementACandidateAttachments":len(candidates),
        "directQnetAFilesSHAValidated":len(good),
        "source":finalSource,
        "year2016ManagementAQuestionCandidates":125,
        "sourceBookletIndividualQuestionPagesApproved":0,
        "originalTextFiveOptionsApproved":0,
        "independentlyVerifiedAnswerCells":0,
        "historicalLegalTheoryExplanationsApproved":0,
        "newQDATAImports":0,
        "newScoringApprovals":0,
        "status":status,
        "description":"Official public Q-Net article/attachment source identification; even a valid A PDF SHA does not prove every question, option, answer or exam-time law.",
        "articleResults":found}
    (OUT/"NOMUSA_FIRST_V53_2016_A_PRIMARY_PROBE_FULL.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    short={k:v for k,v in result.items() if k!="articleResults"}
    short["fullArticleAuditArtifact"]="review-artifacts/NOMUSA_FIRST_V53/NOMUSA_FIRST_V53_2016_A_PRIMARY_PROBE_FULL.json"
    (ROOT/"review/NOMUSA_FIRST_V53_2016_MANAGEMENT_QNET_SOURCE_SUMMARY_20261118.json").write_text(json.dumps(short,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(short,ensure_ascii=False))
if __name__=="__main__":main()
