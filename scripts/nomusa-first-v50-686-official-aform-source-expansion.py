#!/usr/bin/env python3
"""V50 source-level archive expansion, NOT independent 5-option transcription.

Use V49 six external/official source references and V48 exact 686 review queue.
2018 Q-Net ZIP files contain A/B PDF books: decode ONLY A by archive entry
name, SHA-lock PDF bytes and assign correct elective's booklet provenance.
2016 Q-Net economy A: 25 candidates, PDF SHA link.
2013 external academy mirror: 150 candidate pagebook references, NOT official.
Every source question's substantive approval and automatic scoring remain HOLD.
"""
from pathlib import Path
from collections import Counter
import csv, hashlib, io, json, re, shutil, zipfile
import fitz

ROOT=Path(__file__).resolve().parents[1]
V48=ROOT/"review-artifacts/NOMUSA_FIRST_V48/NOMUSA_FIRST_V48_686_FULL_SOURCE_QUEUE.json"
V49=ROOT/"review-artifacts/NOMUSA_FIRST_V49/NOMUSA_FIRST_V49_SOURCE_DISCOVERY_FULL.json"
REF=ROOT/"review-artifacts/NOMUSA_FIRST_V49/reference_files"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V50"
BOOKS=OUT/"sha_locked_A_form_booklets"
BOOKS.mkdir(parents=True,exist_ok=True)

def j(p):return json.loads(p.read_text(encoding="utf-8"))
def digest(b):return hashlib.sha256(b).hexdigest()
def require(cond,msg):
    if not cond:raise AssertionError("HOLD_V50_"+msg)

def pdf_info(raw,key):
    require(raw.startswith(b"%PDF"),"PDF_MAGIC_"+key)
    doc=fitz.open(stream=raw,filetype="pdf")
    info={"sha256":digest(raw),"bytes":len(raw),"pages":len(doc),
          "nativeFirstPageTextChars":len(doc[0].get_text("text")),
          "sourceCaptionCandidate":doc[0].get_text("text")[:180]}
    doc.close()
    return info

def main():
    base=j(V48)
    require(base["targetCount"]==686 and len(base["rows"])==686,"V48_EXACT_686")
    source=j(V49)
    require(len(source["rows"])==4,"V49_SOURCE_FOUR")
    r2013=next(r for r in source["rows"] if r["year"]==2013)
    r2016=next(r for r in source["rows"] if r["year"]==2016 and "EXTERNAL_SOURCE" in r["role"])
    q2016=next(r for r in source["rows"] if r["year"]==2016 and "QNET_OFFICIAL" in r["role"])
    q2018=next(r for r in source["rows"] if r["year"]==2018 and "QNET_OFFICIAL" in r["role"])
    require(len(q2016["downloadedAttachments"])==1 and len(q2018["downloadedAttachments"])==2,"OFFICIAL_THREE_FILES")
    # Fixed SHA values from independent preceding V49 Q-Net retrieval.
    # A later changed attachment is a source HOLD, never silent overwrite.
    require(r2013.get("sha256")=="57709f98343d157e7a10ebc73c1a3113661970b22a561a101a0e781cfc5e0677","2013_MIRROR_SHA_CHANGED")
    require(r2016.get("sha256")=="6b6d572c48eea02f58f79005d035ef2f97f50b3579e3eceb1a2d51dde0c728e9","2016_ANSWER_MIRROR_SHA_CHANGED")
    require([x["sha256"] for x in q2016["downloadedAttachments"]]==[
        "eb20585599fee9541ea5eae5ad7d56e87cba75a4c6fe1ed674f7280e43a3ac5e"],"2016_QNET_ECON_SOURCE_SHA_CHANGED")
    require([x["sha256"] for x in q2018["downloadedAttachments"]]==[
        "16e024bc4198502bcd7bb25edc547a85e2065145b19ad5f50fd4427e71f3320d",
        "e381d7d734280d8aad8a0399cdffa2411bc3ae8a80a8b5a6aa91b79046929de6"],"2018_QNET_TWO_ZIPS_SHA_CHANGED")
    docs={}
    mirror=REF/"2013_first_question_candidate.pdf"
    require(mirror.is_file() and digest(mirror.read_bytes())==r2013["sha256"],"2013_EXTERNAL_MIRROR_SHA")
    require(r2013["year"]==2013 and r2013["pdfPages"]>=70,"2013_SOURCE_PAGES")
    check=r2016["sha256"]
    require((REF/"2016_answer_table.pdf").is_file() and digest((REF/"2016_answer_table.pdf").read_bytes())==check,
            "2016_ANSWER_TABLE_ONLY")
    economy=q2016["downloadedAttachments"][0]
    path=OUT/"2016_economics_A.pdf"
    pdfsource=REF/economy["file"].split("/")[-1]
    require(pdfsource.is_file() and digest(pdfsource.read_bytes())==economy["sha256"],"2016_ECON_QNET_PDF_SHA")
    qInfo=pdf_info(pdfsource.read_bytes(),"2016_ECONOMICS_A")
    require(qInfo["pages"]>=10,"2016_ECON_PDF_PAGES")
    path.write_bytes(pdfsource.read_bytes())
    docs["2016_economics_A"]={**qInfo,"officialQNetSourceURL":economy["sourceURL"],
                             "officialAttachmentSha256":economy["sha256"],
                             "bookletType":"A_BY_QNET_OFFICIAL_FILENAME_NOT_INDEPENDENT_PAGE_REVIEW",
                             "file":str(path.relative_to(OUT))}
    for kind,entry in zip(("2018_management_A","2018_economics_A"),q2018["downloadedAttachments"]):
        file=REF/entry["file"].split("/")[-1]
        require(file.is_file() and digest(file.read_bytes())==entry["sha256"],"2018_QNET_ZIP_SHA_"+kind)
        require(file.read_bytes().startswith(b"PK\x03\x04"),"2018_ZIP_MAGIC_"+kind)
        with zipfile.ZipFile(file) as z:
            fs=[n for n in z.namelist() if n.lower().endswith(".pdf")]
            require(len(fs)==2,"A_B_INSIDE_ZIP_"+kind)
            a=[n for n in fs if bool(re.search(r"(?:^|[\s_\-])A",n,re.I))]
            b=[n for n in fs if bool(re.search(r"(?:^|[\s_\-])B",n,re.I))]
            require(len(a)==len(b)==1 and a[0]!=b[0],"FORM_A_B_FILENAME_"+kind+":"+str(fs))
            member=z.getinfo(a[0])
            require(member.file_size<=50_000_000,"A_PDF_TOO_LARGE_"+kind)
            raw=z.read(member)
        m=pdf_info(raw,kind)
        require(m["pages"]>=12,"2018_A_PDF_PAGES_"+kind)
        dst=BOOKS/(kind+".pdf")
        dst.write_bytes(raw)
        docs[kind]={**m,"officialQNetSourceURL":entry["sourceURL"],
                    "officialArchiveZipSHA256":entry["sha256"],"pdfArchiveOriginalName":a[0],
                    "bookletType":"A_BY_OFFICIAL_QNET_ZIP_FILENAME_NOT_NATIVE_TEXT_APPROVED",
                    "file":str(dst.relative_to(OUT))}
    distinct={x["id"] for x in base["rows"]}
    require(len(distinct)==686,"V48_UNIQUE")
    rows=[];counter=Counter()
    for q in base["rows"]:
        x=dict(q)
        x["v50NewDocument"]=None
        x["currentSourceGrade"]=q["sourceStatus"]
        if x["year"]==2018:
            key="2018_economics_A" if "경제학" in x["subject"] else "2018_management_A"
            d=docs[key]
            x["v50NewDocument"]={"grade":"OFFICIAL_QNET_ZIP_SHA_AND_A_PDF_CANDIDATE",
                 "year":2018,"pdfSha256":d["sha256"],"archiveZipSha256":d["officialArchiveZipSHA256"],
                 "sourceUrl":d["officialQNetSourceURL"],"sourceBooklet":key,
                 "nativeSourceQuestionNumberAndPageValidated":False}
            x["currentSourceGrade"]="OFFICIAL_QNET_A_FORM_PDF_LINKED_PER_ELECTIVE_NOT_QUESTION_PAGES"
        elif x["year"]==2016 and "경제학" in x["subject"]:
            d=docs["2016_economics_A"]
            x["v50NewDocument"]={"grade":"OFFICIAL_QNET_ECONOMICS_A_PDF_SHA_CANDIDATE",
                "year":2016,"pdfSha256":d["sha256"],"sourceUrl":d["officialQNetSourceURL"],
                "sourceBooklet":"2016_economics_A",
                "nativeSourceQuestionNumberAndPageValidated":False}
            x["currentSourceGrade"]="OFFICIAL_QNET_A_FORM_ECON_PDF_LINKED_NOT_QUESTION_PAGES"
        elif x["year"]==2013:
            x["v50NewDocument"]={"grade":"THIRD_PARTY_MIRROR_A_FORM_CANDIDATE_NOT_QNET",
                "year":2013,"pdfSha256":r2013["sha256"],"sourceUrl":r2013["url"],
                "sourceBooklet":"2013_both_electives_mirror",
                "nativeSourceQuestionNumberAndPageValidated":False,
                "officialQNetContentIdentityVerified":False}
            x["currentSourceGrade"]="2013_EXTERNAL_A_FORM_MIRROR_SHA_CANDIDATE_HOLD"
        require(x["approvedForLearningScoring"] is False and x["scoringApproved"] is False and x["readyForV44"] is False,
                "UNEXPECTED_SCORING_CHANGE_"+x["id"])
        counter[x["currentSourceGrade"]]+=1
        rows.append(x)
    newOfficial=[q for q in rows if q["v50NewDocument"] and q["v50NewDocument"]["grade"].startswith("OFFICIAL_QNET")]
    external=[q for q in rows if q["v50NewDocument"] and q["v50NewDocument"]["grade"].startswith("THIRD_PARTY")]
    require(len(newOfficial)==175,"2018_150_PLUS_2016_ECON25:"+str(len(newOfficial)))
    require(len(external)==150,"2013_MIRROR150:"+str(len(external)))
    require(sum(q["year"]==2018 for q in newOfficial)==150,"2018_150")
    require(sum(q["year"]==2016 for q in newOfficial)==25,"2016_ECON_25")
    require(len(rows)==686 and len({x["id"] for x in rows})==686,"686_UNIQUE")
    result={"schema":"NOMUSA_FIRST_V50_686_SHA_SOURCE_ENRICHMENT/1",
            "asOfKST":"2026-11-18",
            "original686Preserved":686,
            "base2020_21OriginalPdfConnectedIncludingTwoV42":195,
            "newOfficialAFormBookletSHAConnections":175,
            "newThirdParty2013MirrorCandidates":150,
            "remainingWithoutQNetOriginalPDF":316,
            "remainingWithoutEvenExternalMirrorAmongThem":166,
            "sourceStages":dict(sorted(counter.items())),
            "officialDocuments":docs,
            "independentFullQuestionAndFiveOptionsApproved":0,
            "independentOfficialKeyIndividualCellApproved":0,
            "independentLegalTheoryExplanationsApproved":0,
            "newAppQuestionImports":0,
            "newAutoScoringApproved":0,
            "status":"PASS_175_NEW_OFFICIAL_BOOKLET_SHA_LINKS_HOLD_INDIVIDUAL_QUESTION_PAGES_AND_CONTENT",
            "notes":"Official archive PDF/elective booklet affiliation supports candidate ID source discovery, not full text, exact question pages, five-option proof, historical law, or scoring.",
            "rows":rows}
    (OUT/"NOMUSA_FIRST_V50_686_ENRICHED_SOURCE_QUEUE.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with (OUT/"NOMUSA_FIRST_V50_686_ENRICHED_SOURCE_QUEUE.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f);w.writerow(["id","year","subject","number","sourceGrade","qnetOrExternalPdfSHA",
                                   "sourceBooklet","questionPageVerified","scoringApproved"])
        for x in rows:
            e=x["v50NewDocument"] or {}
            w.writerow([x["id"],x["year"],x["subject"],x["questionNumber"],x["currentSourceGrade"],
                e.get("pdfSha256") or x.get("sourceDocumentSHA256") or "",e.get("sourceBooklet") or "",
                "HOLD","HOLD"])
    compact={k:v for k,v in result.items() if k not in ("rows","officialDocuments")}
    compact["officialDocuments"]={k:{x:y for x,y in v.items() if x!="sourceCaptionCandidate"} for k,v in docs.items()}
    compact["full686RowsInArtifact"]="review-artifacts/NOMUSA_FIRST_V50/NOMUSA_FIRST_V50_686_ENRICHED_SOURCE_QUEUE.json"
    (ROOT/"review/NOMUSA_FIRST_V50_686_OFFICIAL_SOURCE_SHA_SUMMARY_20261118.json").write_text(
        json.dumps(compact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in ("rows","officialDocuments")},ensure_ascii=False))
if __name__=="__main__":main()
