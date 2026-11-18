#!/usr/bin/env python3
"""NOMUSA FIRST V35: 14 source-page image reconstructions from Q-Net 2017/2019.
Native PDF page pixels, no OCR and no invented question/answers. Image gallery is
REVIEW ONLY, not official full-text approval and not part of auto-graded QDATA.
"""
import base64, hashlib, importlib.util, io, json, re, sys, tempfile, zipfile
from pathlib import Path
from urllib.parse import urlencode
import requests, fitz

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"study-hub/first-v35-qnet-native-2017-2019"
OUT.mkdir(parents=True,exist_ok=True)
meta=ROOT/"review-artifacts/NOMUSA_FIRST_V35"
meta.mkdir(parents=True,exist_ok=True)
WANTED={
  2017:["legacy1-2017-A-civil-052","legacy1-2017-A-civil-053",
        "legacy1-2017-A-civil-064","legacy1-2017-A-economics-107",
        "legacy1-2017-A-economics-112","legacy1-2017-A-management-117"],
  2019:["legacy1-2019-A-civil-056","legacy1-2019-A-economics-107",
        "legacy1-2019-A-economics-109","legacy1-2019-A-economics-111",
        "legacy1-2019-A-economics-113","legacy1-2019-A-economics-117",
        "legacy1-2019-A-economics-119","legacy1-2019-A-economics-124"]
}
FILES=[
 (2017,5201158,2182807,"2017-management.pdf","40f88201a07d3a3e21eacc6807cbcdd532829acbef1a120ab8114fec30c1d097"),
 (2019,5205539,2190603,"2019년 공인노무사 1차 문제지 A형(경영학개론).pdf","0e25387feb54b46e004c62074b905a795dd42d64df8bed231a7d1c3be0506fdf"),
 (2019,5205539,2190604,"2019년 공인노무사 1차 문제지 A형(경제학원론).pdf","2c51016c52266a69018e3b2be550de2c71b9c669632264736e8c303fdddb3e4c")
]
def download(seq,article,filename,sha):
    q={"id":"cst00302s01","gSite":"L","gId":"05","fileCode":"R001",
       "filePath":f"bbs/Q004/Q004_{seq}","fileName":filename,"fileSeq":seq,"artlSeq":article,"href":0}
    url="https://www.q-net.or.kr/cst003.do?"+urlencode(q)
    r=requests.get(url,timeout=75,headers={"User-Agent":"Mozilla/5.0","Referer":"https://www.q-net.or.kr/"})
    r.raise_for_status()
    data=r.content
    if hashlib.sha256(data).hexdigest()!=sha: raise RuntimeError("OFFICIAL_SHA_CHANGED_"+str(seq))
    return url,data
def unzip_2017(data):
    z=zipfile.ZipFile(io.BytesIO(data))
    result={}
    for name in z.namelist():
        try: display=name.encode("cp437").decode("cp949")
        except UnicodeError: display=name
        if "A형" not in display: continue
        key="economics" if "경제학" in display else "management" if "경영학" in display else None
        if key:
            raw=z.read(name)
            if not raw.startswith(b"%PDF"): raise RuntimeError("ZIP_PDF_SIGNATURE")
            if key in result: raise RuntimeError("DUPLICATE_2017_A_"+key)
            result[key]=(raw,display)
    if set(result)!={"management","economics"}:raise RuntimeError("2017_A_ZIP_SELECTION_FAILED "+str(list(result)))
    return result
def find_anchor(page,number):
    hits=[]
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines",[]):
            txt="".join(span["text"] for span in line["spans"]).strip()
            m=re.match(r"^(\d{1,3})\.\s*",txt)
            if m and int(m.group(1))==number and 35<line["bbox"][0]<90:
                hits.append((float(line["bbox"][1]),txt))
    return hits
def crop_item(buf,year,key,page_index,number):
    doc=fitz.open(stream=buf,filetype="pdf")
    pg=doc[page_index-1]
    anchors=find_anchor(pg,number)
    if len(anchors)!=1:raise RuntimeError(f"QUESTION_START_NOT_UNIQUE {year}:{number} page{page_index}: {anchors}")
    y,heading=anchors[0]
    next_heads=find_anchor(pg,number+1)
    cutoff=min(h[0] for h in next_heads) if next_heads else pg.rect.height-42
    clip=fitz.Rect(40,max(0,y-8),pg.rect.width-39,min(pg.rect.height-35,cutoff-6))
    if clip.height<55:raise RuntimeError(f"CROP_TOO_SHORT_{year}_{number}_{clip.height}")
    pixel=pg.get_pixmap(matrix=fitz.Matrix(2,2),clip=clip,colorspace=fitz.csRGB,alpha=False)
    img=pixel.tobytes("jpeg",jpg_quality=86)
    if len(img)<6500 or pixel.width<600 or pixel.height<85:raise RuntimeError("CROP_DENSITY_HOLD")
    text=pg.get_text("text",clip=clip)
    doc.close()
    return img,dict(pdfPage=page_index,cropRect=list(clip),pixelWidth=pixel.width,
                    pixelHeight=pixel.height,jpegBytes=len(img),jpegSHA256=hashlib.sha256(img).hexdigest(),
                    pdfTextSample=re.sub(r"\s+"," ",text)[:150],
                    circledMarkerCounts={x:text.count(x) for x in "①②③④⑤"},
                    originalQuestionHeading=heading)
def main():
    m=importlib.util.spec_from_file_location("v66",ROOT/"scripts/nomusa-first-v66-pdf-bank.py")
    v66=importlib.util.module_from_spec(m);m.loader.exec_module(v66)
    queue=json.loads((ROOT/"review-artifacts/NOMUSA_FIRST_V34/NOMUSA_FIRST_V34_791_SOURCE_TARGETS.json").read_text())["rows"]
    lookup={r["id"]:r for r in queue}
    sources={}
    with tempfile.TemporaryDirectory() as d:
        temp=Path(d)
        for year,article,seq,fn,expected in FILES:
            url,data=download(seq,article,fn,expected)
            if year==2017:
                z=unzip_2017(data)
                for group,(part,filename) in z.items():sources[(year,group)]=(part,url,expected,filename)
            else:
                key="economics" if "경제학원론" in fn else "management"
                sources[(year,key)]=(data,url,expected,fn)
        rows=[]
        for year,ids in WANTED.items():
            bytype={}
            for group in ("management","economics"):
                buf,url,sha,display=sources[(year,group)]
                file=temp/f"{year}_{group}.pdf";file.write_bytes(buf)
                parsed=v66.read_booklet(file,year)
                if len(parsed)!=125:raise RuntimeError(f"ORIGINAL_125_SEQUENCE_{year}_{group}")
                bytype[group]=parsed
            for id in ids:
                entry=lookup.get(id)
                if not entry or entry["readyForQDATAImport"] or entry["scoringApproved"]:
                    raise RuntimeError("TARGET_NOT_UNAPPROVED_791_"+id)
                number=int(id.rsplit("-",1)[1]);group="economics" if "-economics-" in id else "management"
                pdf,url,sha,fn=sources[(year,group)]
                # QNet printed question number occurs once in the verified original file.
                _,_,pdfPage=bytype[group][number]
                img,proof=crop_item(pdf,year,id,pdfPage,number)
                name=f"{id}.jpg"
                (OUT/name).write_bytes(img)
                rows.append({
                  "id":id,"year":year,"number":number,"subject":entry["subject"],
                  "sourceFile":fn,"sourceSHA256":sha,"qnetOriginal":url,
                  "image":name,**proof,
                  "independentHumanOriginalTextApproval":"HOLD",
                  "answerScoringApproval":"HOLD",
                  "readyForQDATAImport":False
                })
    if len(rows)!=14 or len({x["id"] for x in rows})!=14:
        raise RuntimeError("EXPECTED_14_ORIGINAL_CROPS")
    links=[]
    for r in rows:
        original=r["qnetOriginal"]+"#page="+str(r["pdfPage"])
        links.append(f'''<article class="exam"><h2>{r['year']}년 A형 · {r['subject']} · {r['number']}번</h2>
          <p class="notice">공식 PDF <strong>{r['pdfPage']}쪽</strong> · 원본 이미지 복원 검토본 · 정답 자동채점 보류</p>
          <a class="ref" target="_blank" rel="noopener noreferrer" href="{original}">한국산업인력공단 Q-Net 원문 PDF 확인</a>
          <figure><img loading="lazy" src="{r['image']}" alt="{r['year']}년 A형 {r['subject']} {r['number']}번 공식 기출 PDF 영역 캡처, 내용 독립 교열 전" /><figcaption>출처: 한국산업인력공단 Q-Net · 공공누리 제1유형(출처표시), 문항별 지문·선택지·수식 독립 대조는 대기</figcaption></figure>
          </article>''')
    html='''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>2017·2019년 1차 원본 14문항 이미지 대조 · 미승인 검토본</title>
<style>body{margin:0;color:#1b2c41;background:#f5f7fb;font:15px/1.6 system-ui,'Malgun Gothic',sans-serif}
main{max-width:920px;margin:0 auto;padding:18px 12px 60px}h1{font-size:22px}h2{font-size:17px}
a{color:#145d9d}.exam{margin:14px 0;border:1px solid #d8e1ec;background:#fff;border-radius:14px;padding:14px}
.notice{background:#fdf3d8;padding:8px 12px;border-radius:8px}.ref{display:inline-block;margin:7px 0 12px}
figure{margin:0}img{display:block;max-width:100%;height:auto;background:white}
figcaption{font-size:12px;color:#52627b;margin-top:7px;word-break:keep-all}
@media(max-width:440px){main{padding:10px 8px}.exam{padding:10px}h1{font-size:20px}}</style></head><body><main>
<a href="../index.html">1차 학습앱으로 돌아가기</a>
<h1>2017·2019년 1차 공식 원본 이미지 14문항 — 재검토용</h1>
<p>이 화면은 실제 공식 문제지 PDF에서 문항 영역을 직접 복원한 <strong>원본 시각 검토 자료</strong>입니다.
기출 지문·그래프·선택지의 독립 대조 및 정답 승인은 아직 완료되지 않았으며,
학습 문제은행 자동채점에도 추가하지 않았습니다.</p>
'''+"\n".join(links)+'''</main></body></html>'''
    (OUT.parent/"first-v35-2017-2019-14-original-review.html").write_text(html,encoding="utf-8")
    report={"schema":"NOMUSA_FIRST_V35_QNET_NATIVE_IMAGE_14_REVIEW/1",
            "originalCrops":14,"originalPDFAndZIPExactSHA256Verified":3,
            "renderedQuestionImageReviewOnly":14,
            "actualQDATAImported":0,"independentExpertApproved":0,
            "status":"PASS_VISUAL_SOURCE_SEGMENT_IMAGES_PENDING_HUMAN_CONTENT_CHECK",
            "items":rows}
    (meta/"NOMUSA_FIRST_V35_14_ORIGINAL_CROP_PROOF.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="items"},ensure_ascii=False))
if __name__=="__main__":main()
