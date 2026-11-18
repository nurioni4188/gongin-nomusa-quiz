#!/usr/bin/env python3
"""V54 durable 686-item source-only ledger. No 1st/2nd stage content import.

Combine previously successful V48 (195 official PDF), V50 (175 newly official
2016 econ and 2018 A), and V53 (125 newly official 2016 management A).
Every one of 686 candidate IDs gets official-QNet/source-mirror/no-source
provenance, a source SHA, a visual-proofreading queue status and strict HOLD.
Prior result has NO independently approved full QNet stem, five options,
historical statute/precedent and exam answer cell; never promote OCR/keys.
"""
from __future__ import annotations
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"review-artifacts/NOMUSA_FIRST_V34/NOMUSA_FIRST_V34_791_SOURCE_TARGETS.json"
PRIOR=ROOT/"review/NOMUSA_FIRST_V41_103_CROP_SHA_20261118.json"
V48=ROOT/"review/NOMUSA_FIRST_V48_686_SOURCE_RECOVERY_SUMMARY_20261118.json"
V49=ROOT/"review/NOMUSA_FIRST_V49_ARCHIVE_DISCOVERY_SUMMARY_20261118.json"
V50=ROOT/"review/NOMUSA_FIRST_V50_686_OFFICIAL_SOURCE_SHA_SUMMARY_20261118.json"
V53=ROOT/"review/NOMUSA_FIRST_V53_2016_MANAGEMENT_QNET_SOURCE_SUMMARY_20261118.json"
CROPS=ROOT/"review/first-v48-provisional-crops"
DEST=ROOT/"review/NOMUSA_FIRST_V54_686_UNIFIED_PRIMARY_SOURCE_LEDGER_20261118.json"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V54"
PILOTS={"legacy1-2020-A-management-101","legacy1-2021-A-management-110"}

def load(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def check(cond,msg):
    if not cond:raise AssertionError("HOLD_V54_"+msg)
def isqnet(url):
    try:
        return urlsplit(url).hostname in ("www.q-net.or.kr","q-net.or.kr")
    except Exception:return False

def main():
    base=load(BASE)
    crop=load(PRIOR)
    v48=load(V48);v49=load(V49);v50=load(V50);v53=load(V53)
    check(base["summary"]["totalTargets"]==791 and len(base["rows"])==791,"V34_791")
    excluded={x["id"] for x in crop["files"]}|PILOTS
    check(len(excluded)==105,"EXCLUDED_103_AND_2")
    todo=[x for x in base["rows"] if x["id"] not in excluded]
    check(len(todo)==686 and len({x["id"] for x in todo})==686,"686_UNIQUE")
    check(v48["targetCount"]==686 and v48["generatedProvisionalCrops"]==67,"V48_ORIGINAL_BASELINE")
    check(v50["newOfficialAFormBookletSHAConnections"]==175 and v50["remainingWithoutQNetOriginalPDF"]==316,"V50_175_SHA")
    check(v53["source"] is not None and v53["directQnetAFilesSHAValidated"]==1,"V53_SINGLE_OFFICIAL_A_PDF")
    official=v50["officialDocuments"]
    check(set(official)=={"2016_economics_A","2018_management_A","2018_economics_A"},"THREE_OFFICIAL_BOOKLETS")
    for key,obj in official.items():
        check(isqnet(obj["officialQNetSourceURL"]) and len(obj["sha256"])==64,"QNET_URL_AND_SHA_"+key)
    manager=v53["source"]
    check(isqnet(manager["officialSourceURL"]) and manager["bookletAFromQNetFilename"],"2016_MGMT_QNET_SOURCE")
    mirror=next(x for x in v49["rows"] if x["year"]==2013)
    check(mirror["sha256"]=="57709f98343d157e7a10ebc73c1a3113661970b22a561a101a0e781cfc5e0677",
          "2013_MIRROR_SHA_PRIOR_LOCK")
    rows=[]
    categories=Counter()
    perYear=Counter()
    for q in todo:
        id=q["id"]; year=q["year"]; subj=q["subject"]
        cropFile=CROPS/(id+".jpg")
        cropEvidence={"path":str(cropFile.relative_to(ROOT)),
                      "sha256":sha(cropFile.read_bytes()),
                      "boundaryIndependentlyVerified":False} if cropFile.is_file() else None
        officialRef=None
        mirrorRef=None
        if year in (2020,2021) and q["sourceDocumentSHA256"]:
            check(q.get("originalURL") and isqnet(q["originalURL"]),"V48_ORIGINAL_URL_"+id)
            officialRef={"officialQNetSourceURL":q["originalURL"].split("#")[0],
                         "officialSourcePdfSha256":q["sourceDocumentSHA256"],
                         "sourceGroup":"2020_2021_ORIGINAL_QNET_A_FORM",
                         "candidateOriginalPDFPage":q.get("candidatePdfPage"),
                         "origin":"V42_V48_SHA_PROVEN_OFFICIAL_SOURCE"}
        elif year==2018:
            doc=official["2018_economics_A" if "경제학" in subj else "2018_management_A"]
            officialRef={"officialQNetSourceURL":doc["officialQNetSourceURL"],
                         "officialSourcePdfSha256":doc["sha256"],
                         "archiveZipSha256":doc["officialArchiveZipSHA256"],
                         "sourceGroup":"2018_QNET_A_FORM_"+("ECONOMICS" if "경제학" in subj else "MANAGEMENT"),
                         "candidateOriginalPDFPage":None,
                         "origin":"V50_OFFICIAL_ZIP_A_PDF_SHA"}
        elif year==2016:
            if "경제학" in subj:
                doc=official["2016_economics_A"]
                officialRef={"officialQNetSourceURL":doc["officialQNetSourceURL"],
                             "officialSourcePdfSha256":doc["sha256"],
                             "sourceGroup":"2016_QNET_ECONOMICS_A",
                             "candidateOriginalPDFPage":None,
                             "origin":"V50_OFFICIAL_PDF_SHA"}
            else:
                officialRef={"officialQNetSourceURL":manager["officialSourceURL"],
                             "officialSourcePdfSha256":manager["sourcePDFSHA256"],
                             "sourceGroup":"2016_QNET_MANAGEMENT_A",
                             "candidateOriginalPDFPage":None,
                             "origin":"V53_OFFICIAL_PDF_SHA"}
        elif year==2013:
            mirrorRef={"candidateURL":mirror["url"],
                "thirdPartyPdfSha256":mirror["sha256"],
                "pageCount":mirror["pdfPages"],
                "officialQNetIdentityProved":False}
        if officialRef:
            categories["OFFICIAL_QNET_A_PDF_AT_BOOKLET_LEVEL"]+=1
            sourceGrade="OFFICIAL_QNET_A_PDF_AT_BOOKLET_LEVEL"
        elif mirrorRef:
            categories["THIRD_PARTY_2013_MIRROR_ONLY_HOLD"]+=1
            sourceGrade="THIRD_PARTY_2013_MIRROR_ONLY_HOLD"
        else:
            categories["NO_VERIFIED_OFFICIAL_A_PDF_HOLD"]+=1
            sourceGrade="NO_VERIFIED_OFFICIAL_A_PDF_HOLD"
        perYear[str(year)]+=1
        rows.append({
            "id":id,"year":year,"subject":subj,"form":"A",
            "questionNumber":q["number"],
            "historicCandidateAnswerNumbersUnapproved":q["candidateAnswers"],
            "officialAFormOriginalBooklet":officialRef,
            "thirdPartyMirrorOnly":mirrorRef,
            "originalCropProvisional":cropEvidence,
            "knownQNetNoticeOrOriginalURL":q["originalURL"],
            "sourceGrade":sourceGrade,
            "independentQuestionNumberAndOriginalPDFPageProof":False,
            "independentFullStemAllFiveOptionsProof":False,
            "independentFormulaTableGraphicProof":False,
            "officialAFormFinalAnswerCellIndependentlyVerified":False,
            "eachOptionExplanationIndependentlyProofed":False,
            "historicalExamDateStatuteOrAcademicBasisValidated":False,
            "independentHumanReviewerSignoff":False,
            "readyForV44":False,
            "approvedForLearningScoring":False,
            "scoringApproved":False,
            "status":"SOURCE_PROVENANCE_ONLY_INDEPENDENT_CONTENT_GATE_HOLD"
        })
    expected={"OFFICIAL_QNET_A_PDF_AT_BOOKLET_LEVEL":495,
              "THIRD_PARTY_2013_MIRROR_ONLY_HOLD":150,
              "NO_VERIFIED_OFFICIAL_A_PDF_HOLD":41}
    check(dict(categories)==expected,"PRIMARY_CATEGORIES_"+str(dict(categories)))
    check(sum(year==r["year"] for r in rows for year in [2016])==150,"2016_EXPECT_150")
    check(sum(r["year"]==2018 for r in rows)==150,"2018_EXPECT_150")
    check(sum(r["year"] in (2020,2021) and r["officialAFormOriginalBooklet"] is not None for r in rows)==195,"2020_2021_EXPECT_195")
    check(sum(r["originalCropProvisional"] is not None for r in rows)==67,"V48_67_SHA_IMAGES")
    check(all(not r["approvedForLearningScoring"] and not r["scoringApproved"] for r in rows),"NO_NEW_SCORING")
    schema={
        "schema":"NOMUSA_FIRST_V54_686_UNIFIED_QNET_SOURCE_SHA_LEDGER/1",
        "asOfKST":"2026-11-18",
        "targetCount":686,
        "prior103Excluded":103,"priorTwoV42PilotIDsExcluded":2,
        "officialQNetOriginalBookletShaLinked":495,
        "thirdPartyOnlyCandidateCount":150,
        "withoutOfficialOrMirrorSource":41,
        "categories":dict(sorted(categories.items())),
        "yearCounts":dict(sorted(perYear.items())),
        "v48ProvisionalImageCropsSHAIndexed":67,
        "separateV51CropsInEarlierArtifact":96,
        "independentOriginalStemsAllFiveChoicesValidated":0,
        "independentLegalAndTheorySourcesApproved":0,
        "individualFinalAnswerCellsApproved":0,
        "independentReviewerApproval":0,
        "newQdataImports":0,
        "newScoringApproved":0,
        "status":"PASS_495_OFFICIAL_BOOKLET_SHA_CONNECTIONS_HOLD_ALL_INDIVIDUAL_ITEM_CONTENT",
        "notes":"495 refers ONLY to exam-year/elective A-form QNet source-PDF hashes; it does NOT signify full original item transcription, legal/theory content validation or exam grading approval.",
        "rows":rows
    }
    DEST.write_text(json.dumps(schema,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/"NOMUSA_FIRST_V54_686_SOURCE_REVIEW_QUEUE.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f)
        w.writerow(["id","year","subject","number","sourceGrade","officialSourcePdfSHA",
                    "originalCropProvisional","independentQuestionAndAnswerApproval"])
        for q in rows:
            src=q["officialAFormOriginalBooklet"] or {}
            w.writerow([q["id"],q["year"],q["subject"],q["questionNumber"],q["sourceGrade"],
                src.get("officialSourcePdfSha256",""),(q["originalCropProvisional"] or {}).get("path",""),"HOLD"])
    print(json.dumps({k:v for k,v in schema.items() if k!="rows"},ensure_ascii=False))
if __name__=="__main__":main()
