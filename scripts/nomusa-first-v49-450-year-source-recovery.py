#!/usr/bin/env python3
"""V49 non-deploying recovery of actual 2013/2016/2018 historical source files.

Third-party mirrored source is NOT official Q-Net proof until year/form/sha
against official original is checked. Some archive notices list downloadable
sources; an attachment name on an HTML page is NOT a SHA-verified PDF/ZIP.
Do not write to app data, official answer approvals, or 1st/2nd learning IDs.
"""
import hashlib, html, json, re, zipfile, io, urllib.parse
from pathlib import Path
from collections import Counter

import fitz, requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V49"
SRC=OUT/"reference_files"
SRC.mkdir(parents=True,exist_ok=True)
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Referer":"https://www.q-net.or.kr/"}
S=requests.Session()
S.headers.update(UA)
SOURCES=[
 {"year":2013,"role":"EXTERNAL_SOURCE_QUESTION_BOTH_ELECTIVES_CANDIDATE",
  "authority":"ACADEMY_MIRROR_NOT_QNET_OFFICIAL",
  "url":"https://renew.primeedunet.com/public/file/board/03063ffb-3bd2-4a86-93b9-38fc71a51fbf.pdf"},
 {"year":2016,"role":"EXTERNAL_SOURCE_A_FORM_FINAL_ANSWER_TABLE_NOT_QUESTION",
  "authority":"ACADEMY_MIRROR_NOT_QNET_OFFICIAL",
  "url":"https://renew.primeedunet.com/public/file/board/043a844e-9db6-410b-b3ad-84cfc3a03192.pdf"}
]
QNET_NOTICES=[
 {"year":2016,"role":"QNET_OFFICIAL_ECONOMICS_A_PDF_NOTICE","sourcePage":"https://www.q-net.or.kr/cst003.do?artlSeq=5183001&boardId=Q004&gId=05&gSite=L&id=cst00302&menuType=cst00309",
  "attachmentLabels":["경제학원론(A형).pdf"]},
 {"year":2018,"role":"QNET_OFFICIAL_A_B_MIXED_ZIP_NOTICE","sourcePage":"https://www.q-net.or.kr/cst003.do?artlSeq=5203291&boardId=Q004&gId=05&gSite=L&id=cst00302&menuType=cst00309",
  "attachmentLabels":["경영학.zip","경제학.zip"]}
]

def inspect_blob(blob,url,fn):
    sha=hashlib.sha256(blob).hexdigest()
    ret={"sourceURL":url,"sha256":sha,"bytes":len(blob)}
    if blob.startswith(b"%PDF"):
        doc=fitz.open(stream=blob,filetype="pdf")
        ret.update({"type":"PDF","pdfPages":len(doc),
            "firstPageTextSample":doc[0].get_text("text")[:400],
            "textAccessible":len(doc[0].get_text("text"))>80})
        doc.close()
    elif blob.startswith(b"PK\x03\x04"):
        z=zipfile.ZipFile(io.BytesIO(blob))
        info=z.infolist()
        total=sum(x.file_size for x in info)
        if len(info)>60 or total>350_000_000 or any(x.file_size>200_000_000 for x in info):
            raise ValueError("HOLD_UNSAFE_ZIP_FILE_LIMITS")
        if any(".." in Path(x.filename).parts or x.filename.startswith("/") for x in info):
            raise ValueError("HOLD_UNSAFE_ZIP_PATH")
        ret.update({"type":"ZIP","archiveEntries":len(info),
            "archiveInflatedBytes":total,
            "filenames":[i.filename for i in info][:60]})
    else:
        raise ValueError("HOLD_UNSUPPORTED_SOURCE_SIGNATURE")
    fn.write_bytes(blob)
    return ret

def download(url,limit=100_000_000):
    with S.get(url,timeout=(12,85),allow_redirects=True,stream=True) as resp:
        resp.raise_for_status()
        data=bytearray()
        for chunk in resp.iter_content(chunk_size=1024*512):
            data.extend(chunk)
            if len(data)>limit:
                raise ValueError("HOLD_SOURCE_LIMIT_EXCEEDED")
        return bytes(data)

def parse_official_attachments(raw,base,labels):
    soup=BeautifulSoup(raw,"html.parser")
    candidates=[]
    for a in soup.find_all(["a","button"]):
        name=a.get_text(" ",strip=True)
        title=a.get("title","")
        markup=str(a)[:1500]
        if not any(label.lower() in (name+" "+title+" "+markup).lower() for label in labels):
            continue
        href=html.unescape(a.get("href","") or "")
        if href and not href.lower().startswith(("javascript:","#")):
            u=urllib.parse.urljoin(base,href)
            if urllib.parse.urlparse(u).scheme=="https":
                candidates.append({"label":name or title,"url":u,"evidence":"HTML_A_TAG_HREF"})
        if "fileSeq" in markup and "filePath" in markup:
            for found in re.findall(r'https?[^"\'<> ]+fileSeq[^"\'<> ]+',markup,re.I):
                link=html.unescape(found)
                if link.startswith("https://"):
                    candidates.append({"label":name or title,"url":link,"evidence":"EMBEDDED_FULL_HREF"})
    return candidates[:8]

def main():
    outcomes=[]
    for p in SOURCES:
        out=dict(p)
        file=SRC/("%s_%s.pdf"%(p["year"],"first_question_candidate" if p["year"]==2013 else "answer_table"))
        try:
            blob=download(p["url"],45_000_000)
            out.update(inspect_blob(blob,p["url"],file))
            assert out["type"]=="PDF"
            first=out["firstPageTextSample"].replace(" ","")
            if p["year"]==2013:
                assert "A형" in first or "노동법" in first or "제1과목" in first
                out["sourceContentType"]="FIRST_STAGE_QUESTION_BOOKLET_CANDIDATE"
                out["verifiedOriginalQNetIdentity"]=False
            elif p["year"]==2016:
                assert "최종" in first and "정답" in first
                out["sourceContentType"]="FINAL_ANSWER_TABLE_ONLY"
                out["verifiedOriginalQNetIdentity"]=False
            out["status"]="SHA_CAPTURED_EXTERNAL_SOURCE_EXAM_FORM_VERIFICATION_HOLD"
        except Exception as exc:
            out["status"]="DOWNLOAD_OR_STRUCTURE_HOLD"
            out["error"]=type(exc).__name__+":"+str(exc)[:220]
        outcomes.append(out)
    for p in QNET_NOTICES:
        out=dict(p)
        try:
            response=S.get(p["sourcePage"],timeout=(12,40))
            response.raise_for_status()
            body=response.text
            out["noticeHTMLHash"]=hashlib.sha256(body.encode()).hexdigest()
            out["noticeContainsAllNamedAttachments"]=all(x.lower() in body.lower() for x in p["attachmentLabels"])
            out["attachmentCandidates"]=parse_official_attachments(body,p["sourcePage"],p["attachmentLabels"])
            out["status"]="OFFICIAL_QNET_NOTICE_SEEN_NO_SHA_VERIFIED_ATTACHMENT"
            out["downloadedAttachments"]=[]
            for k,link in enumerate(out["attachmentCandidates"][:3]):
                try:
                    blob=download(link["url"],100_000_000)
                    file=SRC/("%s_QNET_%s_source_%s"%(p["year"],k+1,("pdf" if blob.startswith(b"%PDF") else "zip")))
                    suffix=".pdf" if blob.startswith(b"%PDF") else ".zip" if blob.startswith(b"PK\x03\x04") else ""
                    if not suffix:continue
                    file=file.with_suffix(suffix)
                    entry=inspect_blob(blob,link["url"],file)
                    entry["file"]=str(file.relative_to(OUT))
                    out["downloadedAttachments"].append(entry)
                except Exception as exc:
                    out.setdefault("downloadErrors",[]).append(type(exc).__name__+":"+str(exc)[:130])
            if out["downloadedAttachments"]:
                out["status"]="QNET_ATTACHMENT_SHA_RECORDED_PENDING_A_FORM_AND_PAGE_VERIFICATION"
        except Exception as exc:
            out["status"]="QNET_NOTICE_FETCH_HOLD"
            out["error"]=type(exc).__name__+":"+str(exc)[:220]
        outcomes.append(out)
    summary={
        "schema":"NOMUSA_FIRST_V49_2013_2016_2018_SOURCE_DISCOVERY/1",
        "asOfKST":"2026-11-18",
        "targetYearCounts":{"2013":150,"2016":150,"2018":150},
        "officialLinkDiscovery":len(QNET_NOTICES),
        "historicalExternalSourceAttempts":len(SOURCES),
        "actualSHAValidatedAttachments":sum(int("sha256" in x) for x in outcomes)+sum(len(x.get("downloadedAttachments",[])) for x in outcomes),
        "formAndFullTextIndependentlyConfirmed":0,
        "registeredScoringApproved":0,
        "newQdataImported":0,
        "warnings":[
            "2016 external PDF is a final answer sheet and NOT a problem booklet",
            "2013 academy mirror not independently equal to QNet original",
            "QNet ZIP postings can include A and B forms, inspect contents before linking to questions",
            "No source bytes or result implies approval of 450 actual five-option original texts"],
        "rows":outcomes}
    (OUT/"NOMUSA_FIRST_V49_SOURCE_DISCOVERY_FULL.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary_in_repo={k:v for k,v in summary.items() if k!="rows"}
    summary_in_repo["rows"]=[{k:v for k,v in row.items() if k not in ("firstPageTextSample","noticeHTMLHash")} for row in outcomes]
    (ROOT/"review/NOMUSA_FIRST_V49_ARCHIVE_DISCOVERY_SUMMARY_20261118.json").write_text(json.dumps(summary_in_repo,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!="rows"}|{"statuses":Counter(x["status"] for x in outcomes)},ensure_ascii=False,default=dict))
if __name__=="__main__":main()
