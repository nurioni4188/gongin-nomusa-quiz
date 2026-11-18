#!/usr/bin/env python3
"""V42: retrieve and SHA-verify exactly six existing Q-Net official reference PDFs.
4 original A-form question booklets and 2 official final answer grids.
These files live only in a CI artifact. This step does NOT approve answers.
"""
import hashlib, json
from pathlib import Path
import fitz
import requests

root=Path(__file__).resolve().parents[1]
source=root/"study-hub/legacy-first-v61-sources.js"
s=source.read_text(encoding="utf-8")
ledger=json.loads(s[s.index("{"):s.rfind(";")])
out=root/"review-artifacts/NOMUSA_FIRST_V42_OFFICIAL"
out.mkdir(parents=True,exist_ok=True)
docs={
 "2020-A-management":ledger["documents"]["2020-A-management"],
 "2020-A-economics":ledger["documents"]["2020-A-economics"],
 "2021-A-management":ledger["documents"]["2021-A-management"],
 "2021-A-economics":ledger["documents"]["2021-A-economics"],
 "2020-AB-official-final-answers":ledger["answerDocuments"]["2020-AB"],
 "2021-AB-official-final-answers":ledger["answerDocuments"]["2021-AB"],
}
session=requests.Session()
session.headers.update({"User-Agent":"Mozilla/5.0 Chrome/123","Referer":"https://www.q-net.or.kr/"})
results=[]
for key,record in docs.items():
    response=session.get(record["download"],timeout=100)
    response.raise_for_status()
    raw=response.content
    sha=hashlib.sha256(raw).hexdigest()
    if not raw.startswith(b"%PDF") or sha!=record["sha256"]:
        raise RuntimeError("HOLD_SOURCE_PDF_SHA "+key)
    doc=fitz.open(stream=raw,filetype="pdf")
    if len(doc)!=record["pdfPages"]:
        raise RuntimeError("HOLD_SOURCE_PDF_PAGE_COUNT "+key)
    (out/(key+".pdf")).write_bytes(raw)
    results.append({"key":key,"officialUrl":record["download"],"sha256":sha,
                    "pages":len(doc),"bytes":len(raw),
                    "nativeTextChars":sum(len(p.get_text("text")) for p in doc),
                    "role":"FINAL_KEY_REFERENCE_REVIEW_ONLY" if "-official-final-answers" in key else "SOURCE_BOOKLET_REVIEW_ONLY"})
    doc.close()
manifest={"schema":"NOMUSA_V42_SIX_QNET_OFFICIAL_REFERENCE_PDFS/1","pdfs":results,
          "officialSHA256Validated":6,
          "officialAnswerIndependentQuestionMatchingApproved":0,
          "questionTextAndFiveOptionsHumanApproved":0,
          "actualQDATAImported":0,
          "scoringApproved":0}
(out/"six-source-sha-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in manifest.items() if k!="pdfs"}|{"sources":[{"key":x["key"],"bytes":x["bytes"],"pages":x["pages"],"nativeTextChars":x["nativeTextChars"]}for x in results]},ensure_ascii=False))
