#!/usr/bin/env python3
"""Render three V23 MEDIUM source questions as reproducible printed PDF images.

Read-only: produces review-artifacts, never changes original PDFs, manuscripts,
learner keys, or reviewer decisions.
"""
import argparse
import hashlib
import json
from pathlib import Path
import fitz

SOURCES=[
    ("2016_p5_q2","source_pdf/2016/2016_second_full_original.pdf",[7]),
    ("2019_p4_q3","source_pdf/2019/2019_p4_civil_procedure.pdf",[]),
    ("2020_p7_q3","source_pdf/2020/2020_p7_civil_procedure.pdf",[]),
]

def main(root:Path):
    out=root/"review-artifacts/NOMUSA_V25_MEDIUM_SOURCE_PAGES"
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    for qid,rel,selected in SOURCES:
        pdf=root/rel
        if not pdf.is_file():
            raise RuntimeError("HOLD_PDF_BINARY_MISSING_"+rel)
        binary=pdf.read_bytes()
        if not binary.startswith(b"%PDF-"):
            raise RuntimeError("HOLD_NOT_PDF_"+rel)
        doc=fitz.open(stream=binary,filetype="pdf")
        pages=selected or list(range(1,len(doc)+1))
        for p in pages:
            if p<1 or p>len(doc):
                raise RuntimeError("HOLD_PAGE_NOT_FOUND_"+qid)
            pix=doc[p-1].get_pixmap(matrix=fitz.Matrix(2,2),alpha=False)
            target=out/(qid+"__page%02d.png"%p)
            pix.save(str(target))
            results.append({
                "id":qid,"path":rel,"repoPdfSha256":hashlib.sha256(binary).hexdigest(),
                "pdfPage":p,"totalPdfPages":len(doc),"pageFile":str(target.relative_to(root)),
                "pageImageSha256":hashlib.sha256(target.read_bytes()).hexdigest(),
                "textLayer":bool(doc[p-1].get_text().strip()),
                "originalVisualReview":"PENDING_EXPERT",
                "finalApproval":"HOLD"})
    if not results or not all(any(r["id"]==id for r in results) for id,_,_ in SOURCES):
        raise RuntimeError("HOLD_INCOMPLETE_IMAGES")
    manifest={"schema":"NOMUSA_V25_MEDIUM_PDF_PAGE_MANIFEST/1",
              "questionCount":3,"pageCount":len(results),"originalsModified":False,
              "independentExpertApproved":0,"finalApproval":"HOLD","rows":results}
    (out.parent/"NOMUSA_V25_MEDIUM_SOURCE_PAGES.json").write_text(
        json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS_RENDERED_FOR_VISUAL_PROOFREAD_HOLD_EXPERT",
                      "questionCount":3,"images":len(results)},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("root",nargs="?",default=".")
    a=p.parse_args();main(Path(a.root))
