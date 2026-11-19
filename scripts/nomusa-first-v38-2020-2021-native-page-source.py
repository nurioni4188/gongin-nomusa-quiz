#!/usr/bin/env python3
"""V38: Q-Net native original-page image extraction for 2020/2021 1st A form.

Use only original Q-Net 4 PDFs with exact existing V61 SHA256.
Create only distinct pages referenced by existing 274 OCR page candidates.
Page links are OCR_CANDIDATE, NOT VERIFIED question-to-page matches.
No OCR inference, invented text, answer approval or QDATA modification.
"""
from pathlib import Path
import hashlib, json, re, sys, requests, fitz

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"study-hub/legacy-first-v61-sources.js"
IMAGES=ROOT/"study-hub/first-v38-qnet-pages-2020-2021"
PROOF=ROOT/"review-artifacts/NOMUSA_FIRST_V38"
IMAGES.mkdir(parents=True,exist_ok=True)
PROOF.mkdir(parents=True,exist_ok=True)
raw=SOURCE.read_text()
ledger=json.loads(raw[raw.index("{"):raw.rfind(";")])
groups={}
for id,record in ledger["records"].items():
    if not re.match(r"^legacy1-202[01]-A-",id):continue
    source=record["source"]
    g=groups.setdefault(source,{"records":0,"located":0,"pageCandidates":set(),"holdIds":[]})
    g["records"]+=1
    if record["status"]=="OCR_PAGE_CANDIDATE" and isinstance(record.get("pdfPage"),int):
        g["located"]+=1
        g["pageCandidates"].add(record["pdfPage"])
    else:g["holdIds"].append(id)
expectedSources=["2020-A-management","2020-A-economics","2021-A-management","2021-A-economics"]
assert sorted(groups)==sorted(expectedSources)
assert sum(v["records"] for v in groups.values())==300
assert sum(v["located"] for v in groups.values())==274
assert sum(len(v["holdIds"]) for v in groups.values())==26
assert sum(len(v["pageCandidates"]) for v in groups.values())==88

session=requests.Session()
session.headers.update({"User-Agent":"Mozilla/5.0 Chrome/123.0","Referer":"https://www.q-net.or.kr/"})
manifest={"schema":"NOMUSA_FIRST_V38_2020_2021_SHA_PAGE_REFERENCE/1",
          "sourceStatus":"OFFICIAL_QNET_PDF_SHA_MATCH",
          "examYears":[2020,2021],
          "AFormCandidates":300,"OCRPageCandidates":274,"bookletOnlyHOLD":26,
          "uniqueImagePages":88,"sourceDocuments":[],
          "independentQuestionPageApproval":0,"scoringApproved":0,
          "recordedQDATAItemsAdded":0}
for key in expectedSources:
    docInfo=ledger["documents"][key]
    url=docInfo["download"]
    response=session.get(url,timeout=90)
    response.raise_for_status()
    buf=response.content
    if not buf.startswith(b"%PDF"):raise RuntimeError("QNET_PDF_SIGNATURE_FAIL_"+key)
    sha=hashlib.sha256(buf).hexdigest()
    if sha!=docInfo["sha256"]:raise RuntimeError(f"QNET_SHA256_MISMATCH_{key}")
    doc=fitz.open(stream=buf,filetype="pdf")
    if len(doc)!=docInfo["pdfPages"]:raise RuntimeError("QNET_PAGECOUNT_MISMATCH_"+key)
    fileList=[]
    for pageNum in sorted(groups[key]["pageCandidates"]):
        if not 1<=pageNum<=len(doc):raise RuntimeError("OCR_PAGE_OUT_OF_SOURCE_"+key)
        page=doc[pageNum-1]
        pix=page.get_pixmap(matrix=fitz.Matrix(1.85,1.85),colorspace=fitz.csGRAY,alpha=False)
        img=pix.tobytes("jpeg",jpg_quality=84)
        if pix.width<850 or pix.height<1200 or len(img)<14000:raise RuntimeError("RENDERED_PAGE_TOO_SMALL_"+key)
        name=f"{key}-p{pageNum:03}.jpg"
        path=IMAGES/name
        path.write_bytes(img)
        fileList.append({"page":pageNum,"image":name,"sha256":hashlib.sha256(img).hexdigest(),"bytes":len(img),
                         "width":pix.width,"height":pix.height,
                         "sourcePDFSHA256":sha,"pageLocationIndependentApproval":"HOLD"})
    manifest["sourceDocuments"].append({
        "key":key,"sourceURL":url,"pdfSHA256":sha,"pageCount":len(doc),
        "recordCount":groups[key]["records"],"ocrPageCandidates":groups[key]["located"],
        "unlocatedIds":groups[key]["holdIds"],"images":fileList
    })
    doc.close()
assert sum(len(d["images"]) for d in manifest["sourceDocuments"])==88
out=PROOF/"NOMUSA_FIRST_V38_88_NATIVE_SOURCE_PAGE_MANIFEST.json"
out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({
    "status":"PASS_4_OFFICIAL_SHA_88_NATIVE_PAGES_274_OCR_PAGE_CANDIDATES_26_HOLD",
    "sources":[{"key":v["key"],"pages":len(v["images"]),"candidates":v["ocrPageCandidates"],"hold":len(v["unlocatedIds"])}for v in manifest["sourceDocuments"]],
    "renderedBytes":sum(x["bytes"]for g in manifest["sourceDocuments"]for x in g["images"]),
    "confirmedQuestions":0,"newAutoGrading":0
},ensure_ascii=False))
