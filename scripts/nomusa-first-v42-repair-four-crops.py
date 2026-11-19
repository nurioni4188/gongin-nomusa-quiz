#!/usr/bin/env python3
"""V42 4 proven crop-boundary fixes from original, SHA-pinned Q-Net scanned PDF pixels.
Manually sight-checked against original pages 2020 p32/33 and 2021 p16/35.
Four answer choices sight-checked against separate SHA-pinned official A-form answer PDF.
Original text complete in raster; structured transcription/3 law explanations still HOLD.
"""
import hashlib,json
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"review-artifacts/NOMUSA_FIRST_V42_OFFICIAL"
DEST=ROOT/"review/first-v42-four-corrected-crops"
OUT=ROOT/"review/NOMUSA_FIRST_V42_FOUR_MANUAL_CROP_REPAIRS_20261118.json"
DEST.mkdir(parents=True,exist_ok=True)
CASES={
 "legacy1-2020-A-social-098":("2020-A-management",32,[32,34,578,264],"147276ef4ba8110134835a7e7f99cf14f926a48ec71d4caec47c53293a22dd62",2,"SOCIAL_LAW_EXAM_DATE_REVIEW_HOLD"),
 "legacy1-2020-A-management-101":("2020-A-management",33,[32,94,578,211],"18534999de35d4263b0ea64c555bbf54ef0a56f9347463786fbaf503dcd0605b",3,"PERROW_THEORY_SOURCE_RECHECK"),
 "legacy1-2021-A-labor2-043":("2021-A-management",16,[32,248,578,483],"56eaf338fafbef7a0811b12d742e0dc52d5b9003b3c4ab655ce9b093cbfab2cc",4,"COLLECTIVE_LABOR_LAW_EXAM_DATE_REVIEW_HOLD"),
 "legacy1-2021-A-management-110":("2021-A-management",35,[32,461,578,570],"92ae89a85badb5aa04ef7f14576e3909006aba6da8ef6c9da6c3149620e6480f",3,"ORGANIZATIONAL_POWER_THEORY_REVIEW_HOLD")
}
source=json.loads((SRC/"six-source-sha-manifest.json").read_text(encoding="utf-8"))
assert source["officialSHA256Validated"]==6
docmeta={x["key"]:x for x in source["pdfs"]}
records=[]
for id,(key,page,box,expected,answer,topic) in CASES.items():
  info=docmeta[key]
  pdf=(SRC/(key+".pdf")).read_bytes()
  assert hashlib.sha256(pdf).hexdigest()==info["sha256"],id+"_OFFICIAL_PDF_SHA"
  anskey=id.split("-")[1]+"-AB-official-final-answers"
  ans=(SRC/(anskey+".pdf")).read_bytes()
  assert hashlib.sha256(ans).hexdigest()==docmeta[anskey]["sha256"],id+"_ANSWER_PDF_SHA"
  doc=fitz.open(stream=pdf,filetype="pdf")
  assert len(doc)==info["pages"] and 1<=page<=len(doc)
  image=doc[page-1].get_pixmap(matrix=fitz.Matrix(2.15,2.15),
    clip=fitz.Rect(box),colorspace=fitz.csRGB,alpha=False)
  jpg=image.tobytes("jpeg",jpg_quality=91)
  assert hashlib.sha256(jpg).hexdigest()==expected,id+"_CROP_DIFFERS_FROM_VISUALLY_REVIEWED_IMAGE"
  assert image.width==1175 and image.height>=220
  name=id+".jpg"
  (DEST/name).write_bytes(jpg)
  records.append({
   "id":id,"sourcePdfKey":key,"sourcePdfSHA256":info["sha256"],"page":page,
   "clipPDFPoints":box,"originalQuestionImage":"review/first-v42-four-corrected-crops/"+name,
   "sha256":expected,"sourceImageView":"VISUALLY_RECHECKED_FULL_STEM_FIVE_OPTIONS_NO_NEXT_QUESTION",
   "officialAnswerDocumentKey":anskey,
   "officialAnswerDocumentSHA256":docmeta[anskey]["sha256"],
   "officialAFormFinalAnswerVisuallyRead":answer,
   "explanationReview":topic,"expertIndependentFinalApproval":False,
   "scoringApproved":False})
  doc.close()
assert len(records)==4 and len(list(DEST.glob("*.jpg")))==4
result={"schema":"NOMUSA_FIRST_V42_FOUR_CORRECTED_ORIGINAL_CROPS/1",
 "repairedCrops":4,"originalPDF_SHA_MATCH":4,"officialAnswerPDF_SHA_MATCH":4,
 "manualSourceCropAndOfficialAnswerVisualRead":4,
 "expertIndependentFinalApproval":0,"scoringApproved":0,
 "newQDATAImported":0,"mainProductionChanged":False,"records":records}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in result.items() if k!="records"},ensure_ascii=False))
