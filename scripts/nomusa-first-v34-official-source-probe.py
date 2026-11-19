#!/usr/bin/env python3
"""V34 official Q-Net retrieval/structural audit; read-only, no AI/OCR/guessing.
Uses official per-file URLs and SHA256 values already verified in V61.
Any PDF import must separately prove one-to-one original stem, five options, maths,
original booklet type and question number. No source page => no import.
"""
import hashlib, json, re, sys, time
from pathlib import Path
from collections import Counter
from urllib.parse import urlencode
import requests, fitz

ROOT=Path(__file__).resolve().parents[1]
BASE="https://www.q-net.or.kr/cst003.do"
INDEX=ROOT/"study-hub/legacy-first-v61-sources.js"
t=INDEX.read_text()
d=json.loads(t[t.index("{"):t.rfind(";")])
session=requests.Session();session.headers.update({"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122 Safari/537.36","Referer":"https://www.q-net.or.kr/"})
out={"schema":"NOMUSA_FIRST_V34_OFFICIAL_PDF_STRUCTURAL_AUDIT/1","yearRange":"2010-2021","sources":[],"officialShaVerified":0,"missingSourceNotCompleted":True,"autoGrading":False}
titles=["2020-A-management","2020-A-economics","2021-A-management","2021-A-economics","2020-B-management","2021-B-management"]
source_cache=ROOT/"review-artifacts/NOMUSA_FIRST_V34/sources"
source_cache.mkdir(parents=True,exist_ok=True)
for key in titles:
    src=d["documents"][key]
    row={"key":key,"originalURL":src["download"],"expectedSHA256":src["sha256"],"expectedPages":src["pdfPages"]}
    try:
        res=session.get(src["download"],timeout=50)
        data=res.content
        row.update(http=res.status_code,bytes=len(data),head=data[:12].hex(),contentType=res.headers.get("Content-Type"))
        if res.status_code==200 and data.startswith(b"%PDF"):
            sha=hashlib.sha256(data).hexdigest()
            row["SHA256"]=sha;row["matchOfficialSHA"]=sha==src["sha256"]
            if row["matchOfficialSHA"]:
                doc=fitz.open(stream=data,filetype="pdf")
                row["pages"]=len(doc)
                row["textPageCounts"]=[len(page.get_text("text").strip()) for page in doc]
                row["pageTextMin"]=min(row["textPageCounts"]);row["pageTextMax"]=max(row["textPageCounts"])
                row["textRichPages"]=sum(n>700 for n in row["textPageCounts"])
                row["rasterImagePages"]=sum(len(page.get_images())>=1 for page in doc)
                row["renderedPageSHA256"]=hashlib.sha256(doc[0].get_pixmap(matrix=fitz.Matrix(1,1),colorspace=fitz.csGRAY).samples).hexdigest()
                row["structurallyReady"]=len(doc)==src["pdfPages"]
                doc.close()
                (source_cache/(key+".pdf")).write_bytes(data)
                out["officialShaVerified"]+=1
    except Exception as e:
        row["error"]=type(e).__name__+": "+str(e)[:160]
    out["sources"].append(row)
# Find official attachment metadata for previously unresolved 2016/2017/2018/2019.
for year,article in [(2016,5183001),(2017,5201158),(2018,5203291),(2019,5205539)]:
    u=BASE+"?"+urlencode(dict(artlSeq=article,boardId="Q004",gId="05",gSite="L",id="cst00302",menuType="cst00309"))
    row={"year":year,"officialNotice":u,"attachmentUrls":[]}
    try:
        r=session.get(u,timeout=40)
        h=r.text
        row["http"]=r.status_code;row["htmlBytes"]=len(r.content)
        row["fileSeqCandidates"]=list(dict.fromkeys(re.findall(r"(?:fileSeq|file_seq)[\"'= :>]*(\d{6,10})",h,re.I)))[:30]
        row["Q004PathCandidates"]=list(dict.fromkeys(re.findall(r"Q004[_/](\d{6,10})",h)))[:30]
        row["pdfLinkHints"]=list(dict.fromkeys(re.findall(r"[^\n<>]{0,100}(?:\\.pdf|\\.zip|\\.hwp)[^\n<>]{0,80}",h,re.I)))[:12]
        row["officialExpectedTopicPresent"]="공인노무사" in h
    except Exception as e:row["error"]=type(e).__name__+": "+str(e)[:160]
    out["sources"].append(row)
out["passSHAIntegrity"] = all(x.get("matchOfficialSHA") for x in out["sources"] if "expectedSHA256" in x and x.get("http")==200 and x.get("head","").startswith(b"%PDF".hex()))
dst=ROOT/"review-artifacts/NOMUSA_FIRST_V34/NOMUSA_FIRST_V34_SOURCE_PROBE.json"
dst.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"verified":out["officialShaVerified"],"sourceStatus":[{"key":x.get("key",x.get("year")),"http":x.get("http"),"shaMatch":x.get("matchOfficialSHA"),"pages":x.get("pages"),"textRichPages":x.get("textRichPages"),"pdfCandidates":x.get("fileSeqCandidates"),"Q004PathCandidates":x.get("Q004PathCandidates"),"error":x.get("error")}for x in out["sources"]]},ensure_ascii=False))
# Deliberately keep original PDF downloads as CI ephemeral artifacts, never commit binary PDFs or stale data.
