#!/usr/bin/env python3
"""Read-only targeted V24 source-page snapshots for 2015-2018 and 2021 HR/ORG.

Screenshots are reviewer-only evidence. They do NOT automatically authorize
question text replacements or assert OCR accuracy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import fitz

SRC=[
 "source_pdf/2015/2015_second_full_original.pdf",
 "source_pdf/2016/2016_second_full_original.pdf",
 "source_pdf/2017/2017_second_full_original.pdf",
 "source_pdf/2018/2018_second_full_original.pdf",
 "source_pdf/2021/2021_day1.pdf",
 "source_pdf/2021/2021_day2.pdf",
]
KEY_STARTS={
 "1f85a1b1","164204db",    # 2015 HR, ORG
 "94f7d16c","89c2523d",    # 2016 HR, ORG
 "9c1784d3","fb79ebfa",    # 2017 HR, ORG
 "19dbd66c","250716f7","7763d87a",  # 2018 covers and ORG problems
 "2c3a0e05","dccc2002","92e1d448","4af64682","5eea626f", # 2021 cover/subject pages
}
def process(root):
    cache=json.loads((root/"review/NOMUSA_V23_OCR_TEXT_CACHE.json").read_text(encoding="utf-8"))
    target=root/"review-artifacts/NOMUSA_V24_30_OFFICIAL_PAGE_IMAGES";target.mkdir(parents=True,exist_ok=True)
    rows=[]
    for p in SRC:
        pdf=root/p
        if not pdf.is_file():raise ValueError("MISSING_ORIGINAL_PDF:"+p)
        d=fitz.open(pdf)
        images=[]
        for i in range(len(d)):
            pg=d.load_page(i)
            bin200=pg.get_pixmap(matrix=fitz.Matrix(200/72,200/72),alpha=False).tobytes("png")
            sha=hashlib.sha256(bin200).hexdigest()
            snippet=cache.get(sha,"")
            images.append((i,sha,snippet))
        selected=set(i for i,k,s in images if k[:8] in KEY_STARTS)
        # Some scanned pages with their questions on the following sheet;
        # render neighbors for the source's full contextual visual review.
        expanded=set()
        for i in selected:
            expanded.update(range(max(0,i-1),min(len(d),i+2)))
        # Conservative fallback if OCR not cached / compressed differently: include
        # 2015~2017 HR+ORG expected pages and 2018 middle pages for manual inspection.
        if "2015" in p:expanded.update((2,4))
        if "2016" in p:expanded.update((2,6))
        if "2017" in p:expanded.update((2,4))
        if "2018" in p:expanded.update(range(8,min(len(d),22)))
        if "2021" in p and not selected:
            expanded.update(range(len(d)))
        for i in sorted(expanded):
            img=d.load_page(i).get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False)
            out=target/(Path(p).stem+f"__page{i+1:02d}.png")
            img.save(str(out))
            sha,raw=images[i][1],images[i][2]
            rows.append({"sourcePDF":p,"page":i+1,"pageImage":out.relative_to(root).as_posix(),
                         "pdfImageSha200dpi":sha,"cachedOcr":bool(raw),
                         "ocrTextPreview":raw[:90]})
        print(p,"totalPages",len(d),"selected",len(expanded))
    if len(rows)<12:raise ValueError("HOLD_TOO_FEW_PAGE_IMAGES")
    (root/"review-artifacts/NOMUSA_V24_VISUAL_SOURCE_PAGE_MANIFEST.json").write_text(
        json.dumps({"scope":"V24_30_HR_ORG_2015_2018_2021",
                    "images":len(rows),"reviewedByHuman":False,"sourceImages":rows},
                    ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PASS_V24_IMAGES",len(rows))
def main():
    ap=argparse.ArgumentParser();ap.add_argument("root",nargs="?",default=".")
    args=ap.parse_args();process(Path(args.root))
if __name__=="__main__":main()
