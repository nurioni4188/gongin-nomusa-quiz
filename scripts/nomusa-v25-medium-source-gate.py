#!/usr/bin/env python3
"""V25 three-MEDIUM source visual crosscheck and two safe sourceText edits.

No human signoff is simulated. The check compares actual browser-rendered 328
answers against the committed pre-V25 V23 ledger and the three original pages.
"""
import argparse,hashlib,json,re,sys
from pathlib import Path
from collections import Counter

EXPECTED={
 "2016_p5_q2":("2. 조직관리에서 학습의 중요성, 학습과정 그리고 학습의 주요 원리로서의 강화에 대하여 각각 설명하시오. (25점)",2016,"경영조직론",25),
 "2019_p4_q3":("【문제 3】 공동소송참가에 관하여 설명하시오. (25점)",2019,"민사소송법",25),
 "2020_p7_q3":("【문제 3】 유사필수적 공동소송에 관하여 설명하시오. (25점)",2020,"민사소송법",25)
}
CHANGED={"2019_p4_q3","2020_p7_q3"}
LEDGER="review/NOMUSA_V23_VALIDATION_LEDGER.json"
EVIDENCE="review/NOMUSA_V25_MEDIUM_3_PRIMARY_PAGE_CROSSCHECK_20261118.json"

def sha(t):
 return hashlib.sha256(t.encode("utf-8")).hexdigest()

def run(root:Path):
 baseline=json.loads((root/LEDGER).read_text(encoding="utf-8"))
 evidence=json.loads((root/EVIDENCE).read_text(encoding="utf-8"))
 if len(baseline["rows"])!=328 or baseline["summary"]["independentExpertApproved"]!=0:
  raise ValueError("HOLD_328_APPROVAL_BASELINE")
 before={r["id"]:r for r in baseline["rows"]}
 if set(EXPECTED)!={r["id"] for r in evidence["items"]}:
  raise ValueError("HOLD_EVIDENCE_ID_SET")
 files=sorted((root/"review-artifacts").glob("nomusa_*_rendered*.json"))
 if len(files)!=20:raise ValueError("HOLD_BROWSER_20_YEAR_EXPORTS_"+str(len(files)))
 now={}
 for file in files:
  for r in json.loads(file.read_text(encoding="utf-8"))["rows"]:
   if r["id"] in now:raise ValueError("DUPLICATE_ID_"+r["id"])
   now[r["id"]]=r
 if set(now)!=set(before):raise ValueError("HOLD_ID_SET_CHANGED")
 modifications=[];rows=[]
 for id,row in sorted(now.items()):
  prior=before[id]
  if row.get("scoringApproved") or row.get("approval","HOLD")!="HOLD":
   raise ValueError("HOLD_UNEXPECTED_SOURCE_APPROVAL_"+id)
  if (int(row["year"]),row["subject"],int(row["points"]))!=(int(prior["year"]),prior["subject"],int(prior["points"])):
   raise ValueError("HOLD_YEAR_SUBJECT_POINTS_CHANGE_"+id)
  draft_hash=sha(row["sourceText"]+"\0"+row["detailed"]+"\0"+row["compressed"])
  changed=(draft_hash!=prior["textSHA256"])
  if changed:modifications.append(id)
  if id in EXPECTED:
   expected_text,year,subject,pts=EXPECTED[id]
   if row["sourceText"]!=expected_text:
    raise ValueError("HOLD_VERBATIM_PRINTED_TEXT_MISMATCH_"+id)
   if (int(row["year"]),row["subject"],int(row["points"]))!=(year,subject,pts):
    raise ValueError("HOLD_TARGET_ID_META_MISMATCH_"+id)
   rows.append({"id":id,"year":year,"subject":subject,"points":pts,
                "sourceText":row["sourceText"],"beforeSHA":prior["textSHA256"],
                "afterSHA":draft_hash,"changed":changed,
                "pdfSource":prior["source"]["repoFile"],
                "pdfSha256":prior["source"]["repoSha256"],
                "officialQnetByteIdentical":prior["source"]["qnetOfficialByteIdentical"],
                "priorMatchBand":prior["source"]["matchBand"],
                "priorOcrNgramOverlap":prior["source"]["questionTextOverlap"],
                "visualCheck":"AI_PAGE_INSPECTION",
                "humanIndependentProofread":"HOLD",
                "expertContentApproval":"HOLD"})
 if set(modifications)!=CHANGED:
  raise ValueError("HOLD_NOT_ONLY_TWO_MEDIUM_SOURCE_TEXT_CHANGED_"+repr(modifications))
 if not all(before[id]["source"]["qnetOfficialByteIdentical"] for id in EXPECTED):
  raise ValueError("HOLD_QNET_ORIGINAL_FILE_STATUS")
 out={"schema":"NOMUSA_V25_MEDIUM_VISUAL_AND_SOURCE_CORRECTION/1",
      "status":"PASS_3_PRIMARY_PAGE_AI_VISUAL_2_SOURCE_TEXT_EDITS",
      "totalAnswers":328,"originalQnetByteIdentical":328,
      "mediumPreviously":3,"visuallyChecked":3,"sourceEdits":2,
      "unchanged":326,"critical2016Unchanged":True,
      "expertApproved":0,"finalApproval":"HOLD",
      "candidateProofreadNotCertified":True,"noProductionNoPreview":True}
 dest=root/"review-artifacts"
 (dest/"NOMUSA_V25_MEDIUM_3_CORRECTION_AUDIT.json").write_text(
  json.dumps({"summary":out,"rows":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(out,ensure_ascii=False))
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument("root",nargs="?",default=".")
 p.add_argument("--self-test",action="store_true");a=p.parse_args()
 try:
  if a.self_test:
   assert sha("a")==hashlib.sha256(b"a").hexdigest()
   assert len(EXPECTED)==3 and len(CHANGED)==2
   print("PASS_V25_MEDIUM_SOURCE_SELFTEST")
  else:run(Path(a.root))
  return 0
 except Exception as e:
  print(json.dumps({"status":"HOLD_V25_MEDIUM_GATE","error":str(e)},ensure_ascii=False),file=sys.stderr)
  return 2
if __name__=="__main__":sys.exit(main())
