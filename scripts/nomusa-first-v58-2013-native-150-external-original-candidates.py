#!/usr/bin/env python3
"""V58: source-anchored 2013 A-form 150 draft text/image candidates.

The 80-page 2013 1st-stage management/economics PDF originates from a
third-party public academy mirror, SHA locked by V49. It has native text but
has NOT been independently shown identical to the original Q-Net PDF.
This tool never approves five choices, official final keys, legal validity,
model answers or automated grading. The native PDF often contains tables,
cross-page text, formula layout and two elective booklets.
"""
from __future__ import annotations
import csv, hashlib, json, re
from collections import defaultdict,Counter
from pathlib import Path
import requests, fitz

ROOT=Path(__file__).resolve().parents[1]
V34=ROOT/"review-artifacts/NOMUSA_FIRST_V34/NOMUSA_FIRST_V34_791_SOURCE_TARGETS.json"
V49=ROOT/"review/NOMUSA_FIRST_V49_ARCHIVE_DISCOVERY_SUMMARY_20261118.json"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V58"
CROPS=OUT/"third_party_mirror_candidate_crops"
SUMMARY=ROOT/"review/NOMUSA_FIRST_V58_2013_150_NATIVE_SOURCE_DRAFT_SUMMARY_20261118.json"
CROPS.mkdir(parents=True,exist_ok=True)
QHEADING=re.compile(r"^\s*(\d{1,3})\s*[.．]\s*(.*)$")
BOOK_LABEL=re.compile(r"A\s*형\s*[-–]?\s*(39|41)\s*[-–]?\s*(\d+)")
CIRCLED=("①","②","③","④","⑤")
MIRROR_SHA="57709f98343d157e7a10ebc73c1a3113661970b22a561a101a0e781cfc5e0677"

def read(p):return json.loads(p.read_text(encoding="utf8"))
def sha(blob):return hashlib.sha256(blob).hexdigest()
def check(c,msg):
    if not c:raise AssertionError("HOLD_V58_"+msg)

def download_mirror(url):
    try:
        response=requests.get(url,timeout=(12,90))
        response.raise_for_status()
        return response.content,True
    except requests.exceptions.SSLError:
        from urllib.parse import urlsplit
        check(urlsplit(url).hostname=="renew.primeedunet.com","TLS_OVERRIDE_NOT_ALLOWED")
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response=requests.get(url,timeout=(12,90),verify=False)
        response.raise_for_status()
        return response.content,False

def form(page):
    text=page.get_text("text")
    matches=BOOK_LABEL.findall(text)
    if not matches:return None
    kinds={a for a,_ in matches}
    return list(kinds)[0] if len(kinds)==1 else None

def headings(page):
    found=[]
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines",[]):
            spans=line.get("spans",[])
            if not spans:continue
            text="".join(span.get("text","") for span in spans).strip()
            match=QHEADING.match(text)
            if not match:continue
            n=int(match.group(1))
            x,y=line["bbox"][:2]
            # Reject answer options, column numbers, footer page numbers.
            if 1<=n<=125 and 15<x<page.rect.width*0.38 and 20<y<page.rect.height-30:
                found.append({"number":n,"pageY":round(y,2),"pageX":round(x,2),
                              "lineTextSample":text[:95]})
    return found

def question_region(doc,begin,following):
    p,y=begin
    current=doc[p]
    if following:
        endPage,endY=following
    else:endPage,endY=p,current.rect.height-34
    if endPage<p:return None
    if endPage-p>1:return None
    fragments=[]
    for ix in range(p,endPage+1):
        page=doc[ix]
        top=max(0,y-6) if ix==p else 28
        bottom=min(page.rect.height-28,endY-6) if ix==endPage else page.rect.height-32
        if bottom<=top:continue
        rect=fitz.Rect(15,top,page.rect.width-15,bottom)
        fragments.append((ix,rect,page.get_text("text",clip=rect,sort=True)))
    return fragments

def main():
    v49=read(V49)
    m=next(x for x in v49["rows"] if x["year"]==2013)
    check(m.get("sha256")==MIRROR_SHA and m["pdfPages"]==80,"EXTERNAL_MIRROR_SHA_PREVIOUS")
    v34=read(V34)
    qtargets=[x for x in v34["rows"] if x["year"]==2013]
    check(len(qtargets)==150 and len({x["id"] for x in qtargets})==150,"2013_150_ID")
    byte,verifiedTLS=download_mirror(m["url"])
    check(byte.startswith(b"%PDF") and sha(byte)==MIRROR_SHA,"MIRROR_DOWNLOADED_SHA_DRIFT")
    doc=fitz.open(stream=byte,filetype="pdf")
    check(len(doc)==80,"MIRROR_80_PAGES")
    pageKind={i:form(doc[i]) for i in range(len(doc))}
    categoryCounts=Counter(v for v in pageKind.values() if v)
    # Interpret filename/footer paper serials only when at least one page
    # from both form variants is individually traceable.
    check(categoryCounts["39"]>20 and categoryCounts["41"]>20,"TWO_A_FORM_BOOKLETS_NOT_LOCATED")
    bykind=defaultdict(lambda:defaultdict(list))
    for ix,page in enumerate(doc):
        kind=pageKind[ix]
        if kind is None:continue
        for x in headings(page):bykind[kind][x["number"]].append((ix,x))
    indices={}
    duplicate_heading_candidate_resolutions=[]
    for kind,byNum in bykind.items():
        validated={}
        for n,hits in byNum.items():
            original=list(hits)
            if len(original)>1:
                standalone=[(ix,a) for ix,a in original
                            if a["lineTextSample"].strip() in (str(n)+".",str(n)+"．")]
                # Exact standalone printed heading is more specific than
                # e.g. "1. 기본금액", which is a nested list item at p31.
                # This is a source-anchor heuristic, NOT human proofread.
                if len(standalone)==1:
                    hits=standalone
                    duplicate_heading_candidate_resolutions.append({
                        "booklet":kind,"questionNumber":n,
                        "chosen":[{"pdfPage":ix+1,**a} for ix,a in hits],
                        "excludedNestedListCandidates":[{"pdfPage":ix+1,**a} for ix,a in original if (ix,a) not in hits],
                        "approval":"PROVISIONAL_HEADING_DISAMBIGUATION_NOT_INDEPENDENT_SOURCE_PROOFREAD"})
            validated[n]=hits
        indices[kind]=validated
    rows=[];states=Counter();cropNum=0
    for r in qtargets:
        id=r["id"];n=r["number"]
        kind="41" if "경제학" in r["subject"] else "39"
        hits=indices.get(kind,{}).get(n,[])
        state="NO_UNIQUE_NATIVE_TEXT_HEADING_HOLD"
        fragments=None
        if len(hits)==1:
            page,a=hits[0]
            following=indices[kind].get(n+1,[])
            nextPoint=(following[0][0],following[0][1]["pageY"]) if len(following)==1 else None
            fragments=question_region(doc,(page,a["pageY"]),nextPoint)
            if fragments:
                state="NATIVE_PDF_TEXT_AND_IMAGE_CANDIDATE_UNVERIFIED"
        elif len(hits)>1:state="AMBIGUOUS_DUPLICATE_NATIVE_NUMBER_HOLD"
        textDraft="\n".join(part for _,_,part in fragments) if fragments else ""
        markers={c:textDraft.count(c) for c in CIRCLED}
        imageRef=None
        if fragments:
            # Crop only first page or both pieces, do not pretend this is
            # an independently checked entire question.
            cropParts=[]
            for i,(ix,rect,_) in enumerate(fragments):
                pix=doc[ix].get_pixmap(matrix=fitz.Matrix(1.4,1.4),
                       clip=rect,colorspace=fitz.csRGB,alpha=False)
                binary=pix.tobytes("jpeg",jpg_quality=74)
                if len(binary)<800:continue
                path=CROPS/(id+("_continued" if i else "")+".jpg")
                path.write_bytes(binary)
                cropParts.append({"path":str(path.relative_to(OUT)),
                   "sha256":sha(binary),"mirrorPdfPage":ix+1,"sourceRectPDFPoints":[round(x,2) for x in rect],
                   "thirdPartyOriginalIdentityVerified":False})
            if cropParts:
                cropNum+=len(cropParts)
                imageRef=cropParts
        states[state]+=1
        rows.append({
            "id":id,"year":2013,"subject":r["subject"],"number":n,
            "historicAFormAnswerCandidateUnapproved":r["candidateAnswers"],
            "thirdPartyMirrorPDFSHA256":MIRROR_SHA,
            "thirdPartyMirrorUrl":m["url"],
            "sourceBookletFooter":"A형-"+kind,
            "matchingNumberLocations":[{"pdfPage":ix+1,**a} for ix,a in hits][:12],
            "untrustedNativePDFTextCandidate":textDraft[:7500],
            "nativeExtractedTextChars":len(textDraft),
            "unicodeCircledOptionMarkersDetected":markers,
            "provisionalImageParts":imageRef,
            "status":state,
            "officialQNetOriginalIdentityConfirmed":False,
            "exactOriginalStemFiveChoicesVisuallyApproved":False,
            "officialFinalAFormAnswerCellApproved":False,
            "independentLawAndTheoryContentApproved":False,
            "independentHumanProofreadApproved":False,
            "readyForV44":False,"scoringApproved":False
        })
    doc.close()
    check(len(rows)==150 and len({x["id"] for x in rows})==150,"150_FINAL")
    result={
        "schema":"NOMUSA_FIRST_V58_2013_A_EXTERNAL_MIRROR_NATIVE_150_DRAFT/1",
        "asOfKST":"2026-11-18",
        "mirrorPDFSHA256":MIRROR_SHA,
        "mirrorOriginalPDFPages":80,
        "mirrorTLSCertificateVerifiedAtDownload":verifiedTLS,
        "bookletFooterPages":dict(categoryCounts),
        "targetQuestionIDs":150,
        "nativeQuestionHeadingsWithProvisionalText":states["NATIVE_PDF_TEXT_AND_IMAGE_CANDIDATE_UNVERIFIED"],
        "numberAmbiguousOrMissing":150-states["NATIVE_PDF_TEXT_AND_IMAGE_CANDIDATE_UNVERIFIED"],
        "ambiguousCandidateQuestionDetails":[{"id":z["id"],"number":z["number"],"subject":z["subject"],"booklet":z["sourceBookletFooter"],"status":z["status"],"headingPositions":z["matchingNumberLocations"]} for z in rows if z["status"]!="NATIVE_PDF_TEXT_AND_IMAGE_CANDIDATE_UNVERIFIED"],
        "provisionalImageParts":cropNum,
        "disambiguatedPrintedHeadingCandidateCount":len(duplicate_heading_candidate_resolutions),
        "disambiguatedPrintedHeadingCandidateEvidence":duplicate_heading_candidate_resolutions,
        "states":dict(sorted(states.items())),
        "officialQNetSourceEqualityApproved":0,
        "independentOriginalQuestionsApproved":0,
        "approvedIndividualAFormFinalKeyCells":0,
        "examDateLegalTheoryApproved":0,
        "newQdataImports":0,"newScoringApprovals":0,
        "status":"PASS_EXTERNAL_2013_NATIVE_TEXT_TRIAGE_ONLY_QNET_ORIGINAL_AND_CONTENT_HOLD",
        "warning":"External academy mirror, not verified identical to Q-Net official original; PDF native text and crop can miss figures, span boundaries or source content. No item or scoring approval.",
        "rows":rows
    }
    (OUT/"NOMUSA_FIRST_V58_2013_150_NATIVE_TEXT_SOURCE_REVIEW.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    with (OUT/"NOMUSA_FIRST_V58_2013_150_NATIVE_TEXT_QA_QUEUE.csv").open("w",encoding="utf-8-sig",newline="") as f:
        wr=csv.writer(f);wr.writerow(["id","subject","number","booklet","pages","state","textChars","allChoiceUnicodeMarkers","officialQNetSameSourceApproved","grading"])
        for q in rows:wr.writerow([q["id"],q["subject"],q["number"],q["sourceBookletFooter"],
         "|".join(str(p["pdfPage"]) for p in q["matchingNumberLocations"]),
         q["status"],q["nativeExtractedTextChars"],sum(n>0 for n in q["unicodeCircledOptionMarkersDetected"].values())==5,"HOLD","HOLD"])
    summary={k:v for k,v in result.items() if k!="rows"}
    summary["full150DraftArtifact"]="review-artifacts/NOMUSA_FIRST_V58/NOMUSA_FIRST_V58_2013_150_NATIVE_TEXT_SOURCE_REVIEW.json"
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()
