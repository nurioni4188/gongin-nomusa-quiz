#!/usr/bin/env python3
"""Source audit from exact Q-Net public post attachment sequence IDs (2016–2019).
Read-only proof: public article, PDF/ZIP signature, year and A-form markers,
page-level text structure. Results do not authorize item-level grading.
"""
from pathlib import Path
import requests,hashlib,json,re,io,zipfile
import fitz
from urllib.parse import urlencode

root=Path(__file__).resolve().parents[1]
out=root/"review-artifacts/NOMUSA_FIRST_V34";out.mkdir(parents=True,exist_ok=True)
specs=[
 (2016,5183001,2162962,"경제학원론(A형).pdf","economics-A"),
 (2017,5201158,2182807,"2017-management.pdf","management-A"),
 (2018,5203291,2186568,"경영학.zip","management-AB"),
 (2018,5203291,2186569,"경제학.zip","economics-AB"),
 (2019,5205539,2190603,"2019년 공인노무사 1차 문제지 A형(경영학개론).pdf","management-A"),
 (2019,5205539,2190604,"2019년 공인노무사 1차 문제지 A형(경제학원론).pdf","economics-A"),
]
s=requests.Session();s.headers.update({"User-Agent":"Mozilla/5.0","Referer":"https://www.q-net.or.kr/"})
def inspect_pdf(buf):
    p=fitz.open(stream=buf,filetype="pdf")
    info={"pages":len(p),"lengths":[len(pg.get_text("text").strip()) for pg in p],
          "pageHasImages":[len(pg.get_images())>0 for pg in p]}
    info["textRichPages"]=sum(n>=350 for n in info["lengths"])
    raw="\n".join(pg.get_text("text") for pg in p)
    info["numberedQuestionHeadingOccurrences"]=len(re.findall(r"(?m)^\s*\d{1,3}\.\s+",raw))
    info["fiveOptionMarkerCounts"]=[raw.count(m) for m in "①②③④⑤"]
    info["textSample"]=re.sub(r"\s+"," ",raw[:800])[:280]
    p.close()
    return info
rows=[]
for year,article,seq,filename,selection in specs:
    q={"id":"cst00302s01","gSite":"L","gId":"05","fileCode":"R001",
       "filePath":f"bbs/Q004/Q004_{seq}","fileName":filename,
       "fileSeq":seq,"artlSeq":article,"href":0}
    url="https://www.q-net.or.kr/cst003.do?"+urlencode(q)
    result={"year":year,"article":article,"fileSeq":seq,"originalSelectedForm":selection,
            "qnetDownload":url,"requestedName":filename}
    try:
        r=s.get(url,timeout=50)
        content=r.content
        result.update(http=r.status_code,mime=r.headers.get("Content-Type"),bytes=len(content),prefix=content[:12].hex())
        if r.ok and (content.startswith(b"%PDF") or content.startswith(b"PK")):
            result["sha256"]=hashlib.sha256(content).hexdigest()
            if content.startswith(b"%PDF"):
                result.update(format="PDF",pdf=inspect_pdf(content))
            elif content.startswith(b"PK"):
                z=zipfile.ZipFile(io.BytesIO(content))
                result["format"]="ZIP"
                result["entries"]=[]
                for name in z.namelist():
                    info={"name":name}
                    data=z.read(name)
                    info["sha256"]=hashlib.sha256(data).hexdigest()
                    if data.startswith(b"%PDF"):
                        info["pdf"]=inspect_pdf(data)
                    result["entries"].append(info)
            result["downloadedSignatureValid"]=True
        else:
            result["downloadedSignatureValid"]=False
            result["responseSample"]=content[:170].decode("utf-8","replace")
    except Exception as exc:
        result["error"]=f"{type(exc).__name__}: {exc}"[:220]
    rows.append(result)
output={"schema":"NOMUSA_FIRST_V34_OFFICIAL_2016_TO_2019_SOURCE_STRUCTURE/1","sources":rows,
        "validOfficialBinaryCount":sum(bool(x.get("downloadedSignatureValid")) for x in rows),
        "examYears":[2016,2017,2018,2019],
        "allMissingQuestionIDsStillHOLD":True,
        "autoScoringApproved":0}
(out/"NOMUSA_FIRST_V34_2016_2019_QNET_FILES.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"valid":output["validOfficialBinaryCount"],"sources":[{
  "year":x["year"],"seq":x["fileSeq"],"status":x.get("http"),"valid":x.get("downloadedSignatureValid"),
  "sha":x.get("sha256"),"pages":x.get("pdf",{}).get("pages"),
  "textRich":x.get("pdf",{}).get("textRichPages"),
  "headings":x.get("pdf",{}).get("numberedQuestionHeadingOccurrences"),
  "zipEntries":[{"name":e.get("name"),"pages":e.get("pdf",{}).get("pages"),"rich":e.get("pdf",{}).get("textRichPages")}for e in x.get("entries",[])],
  "error":x.get("error")
}for x in rows]},ensure_ascii=False))
