#!/usr/bin/env python3
"""V24 narrow invariant check: 30 printed-question visual transcriptions.

The previous V23 ledger is an audit baseline; no official image, case, expert,
learner ID, scoring, detailed manuscript or user-record approval is changed.
"""
from __future__ import annotations
import argparse
import json
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

DATA=[
 "second/nomusa-v24-verbatim-2015-2016.js",
 "second/nomusa-v24-verbatim-2017-2018.js",
 "second/nomusa-v24-verbatim-2021.js"
]
BASELINE="review/NOMUSA_V23_VALIDATION_LEDGER.json"
OLD_MARK=re.compile(r"\[기출문항 요지|원문 전문은 PDF 참조")
NEW_MARK=re.compile(r"원문 전문은 PDF 참조|기출문항 요지")
def sha(s):return hashlib.sha256(s.encode("utf-8")).hexdigest()
def parse_js(path:Path):
 s=path.read_text(encoding="utf-8")
 m=re.search(r"window\.NOMUSA_V24_[\w_]+\s*=\s*(\[.*\]);?\s*$",s,re.S)
 if not m:raise ValueError("NO_JSON_LITERAL_"+str(path))
 return json.loads(m.group(1))
def source_files(root):
 out=[];ids=set()
 for path in DATA:
  for r in parse_js(root/path):
   if r["id"] in ids:raise ValueError("DUP_SOURCE_"+r["id"])
   ids.add(r["id"]);out.append(r)
 if len(out)!=30 or Counter(r["year"] for r in out)!=Counter({2015:6,2016:6,2017:6,2018:6,2021:6}):
  raise ValueError("BAD_30_YEAR_COVERAGE")
 if Counter(r["points"] for r in out)!=Counter({50:10,25:20}):
  raise ValueError("BAD_50_25_DISTRIBUTION")
 for r in out:
  text=r["sourceText"]
  if not text.strip() or NEW_MARK.search(text):
   raise ValueError("STILL_SUMMARY_"+r["id"])
  if r["pdfPage"]<1 or not r["sourceFile"].startswith("source_pdf/"):
   raise ValueError("BAD_SOURCE_PROVENANCE_"+r["id"])
  # All proposed replacements are AI visual transcripts, not independent expert certificates.
  if r["expertFinalApproval"]!="HOLD" or r["transcription"]!="VISUAL_PDF_PAGE_INSPECTED_AI_DRAFT":
   raise ValueError("UNEXPECTED_APPROVAL_"+r["id"])
 return {r["id"]:r for r in out}

def check(root:Path):
 data=source_files(root)
 baseline=json.loads((root/BASELINE).read_text(encoding="utf-8"))
 base={r["id"]:r for r in baseline["rows"]}
 if len(base)!=328:raise ValueError("V23_328_BASELINE_MISSING")
 folder=root/"review-artifacts"
 files=sorted(folder.glob("nomusa_*_rendered*.json"))
 if len(files)!=20:raise ValueError("V24_REQUIRES_BROWSER_20_YEAR_EXPORTS")
 now={}
 for file in files:
  obj=json.loads(file.read_text(encoding="utf-8"))
  for row in obj["rows"]:
   if row["id"] in now:raise ValueError("V24_DUPLICATE_ID_"+row["id"])
   now[row["id"]]=row
 if set(now)!=set(base):raise ValueError("V24_BASELINE_ID_SET_CHANGED")
 changed=[]
 for id,row in now.items():
  src=row["sourceText"];detail=row["detailed"];compact=row["compressed"]
  f=sha(src+"\0"+detail+"\0"+compact)
  if row.get("scoringApproved"):raise ValueError("V24_UNEXPECTED_AUTO_APPROVAL_"+id)
  old=base[id]
  if int(old["year"])!=int(row["year"]) or int(old["points"])!=int(row["points"]) or old["subject"]!=row["subject"]:
   raise ValueError("V24_YEAR_SUBJECT_POINTS_CHANGED_"+id)
  if id in data:
   if src!=data[id]["sourceText"] or f==old["textSHA256"]:
    raise ValueError("V24_ORIGINAL_TEXT_NOT_REPLACED_"+id)
   changed.append(id)
  elif f!=old["textSHA256"]:
   raise ValueError("V24_NON_TARGET_TEXT_CHANGED_"+id)
 if len(changed)!=30:raise ValueError("V24_NOT_30_MODIFICATIONS_"+str(len(changed)))
 # A historical official Q-Net byte-match still belongs to the original PDF, not the new transcription.
 rows=[]
 for id in sorted(data):
  r=data[id]; old=base[id]; n=now[id]
  rows.append({"id":id,"year":r["year"],"subject":r["subject"],"points":r["points"],
               "pdfSource":r["sourceFile"],"pdfPage":r["pdfPage"],
               "text":r["sourceText"],"sourceCharacters":len(r["sourceText"]),
               "beforeSHA256":old["textSHA256"],
               "afterSHA256":sha(n["sourceText"]+"\0"+n["detailed"]+"\0"+n["compressed"]),
               "officialPDFHashStatus":"PREVIOUS_V23_OFFICIAL_ATTACHMENT_BYTE_MATCH_UNCHANGED",
               "visualTranscription":"AI_VISUAL_DRAFT_SECOND_PROOFREAD_HOLD",
               "expertApproval":"HOLD","finalApproval":"HOLD"})
 status={"schema":"NOMUSA_V24_30_VERBATIM_TRANSCRIPTION_AUDIT/1",
         "status":"PASS_THIRTY_SOURCE_REPLACEMENTS_SECOND_PROOFREAD_HOLD",
         "count":len(rows),"years":dict(Counter(r["year"] for r in rows)),
         "points50":sum(r["points"]==50 for r in rows),
         "points25":sum(r["points"]==25 for r in rows),
         "oldAnswersPreserved":298,"revisedAnswersOnlySourceText":30,
         "officialPDFsModified":False,"questionIDsModified":False,
         "scoringApproved":0,"independentExpertApproved":0,
         "finalApproval":"HOLD",
         "notes":"This verifies a 30-item browser sourceText replacement and hashes, not independent literal proofreading of each PDF character."
         }
 (folder/"NOMUSA_V24_30_TRANSCRIPTION_AUDIT.json").write_text(
  json.dumps({"summary":status,"rows":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 lines=["# NOMUSA V24 — 30개 요지문항 원전 이미지 전사 교체 결과","",
 "기출 원본 PDF 이미지와 Claude 원장·OCR 요약을 비교하여 인사/조직 2015~2018, 2021년 30문항의 수험생 화면 \`sourceText\`를 원문 전사본으로 교체했다.",
 "","> **검증범위:** 실제 브라우저 30개 본문 변경·기존 298개 답안 SHA 불변, 원본 PDF 파일·문제 ID·저장키·배점·상세/압축답안 변경 없음. 글자별 독립 2차 원본 교열/법리·학술 내용승인/전문가 승인 HOLD.",
 "", "## 연도별 건수", "| 연도 | 문항 |","|---|---:|"]
 lines +=["| %s | %s |"%(y,n) for y,n in sorted(status["years"].items())]
 lines +=["","## 문항별 PDF 원전 이미지·전사 SHA", "| 문항 ID | 과목 | 배점 | PDF 파일 (쪽) | 글자수 | 검토판정 |",
          "|---|---|---:|---|---:|---|"]
 for r in rows:
  lines.append("| \`%s\` | %s | %d | %s (p.%d) | %d | AI 전사, 독립 교열 HOLD |"%(
    r["id"],r["subject"],r["points"],r["pdfSource"],r["pdfPage"],r["sourceCharacters"]))
 lines +=["","특별 관문: **2018 경영조직론 제1문 물음 1은 PDF 원본 20점(30점 소문항 추가=50점)**. 2021 쓰레기통 모형의 '1971년 올슨'은 지문대로 보존하고 학술 검증 시 주석으로 구분한다.",
           "","**독립 전문가 최종승인 0/328. Production·Preview 배포하지 않는다.**",""]
 (folder/"NOMUSA_V24_30_TRANSCRIPTION_AUDIT.md").write_text("\n".join(lines),encoding="utf-8")
 return status

def main():
 ap=argparse.ArgumentParser();ap.add_argument("root",nargs="?",default=".");ap.add_argument("--self-test",action="store_true")
 args=ap.parse_args()
 try:
  if args.self_test:
   assert sha("a")==hashlib.sha256(b"a").hexdigest()
   print("PASS_V24_VERBATIM_SELF_TEST")
  else:print(json.dumps(check(Path(args.root)),ensure_ascii=False))
  return 0
 except Exception as exc:
  print(json.dumps({"status":"HOLD_V24_TRANSCRIPTION_GATE","error":str(exc)},ensure_ascii=False),file=sys.stderr)
  return 2
if __name__=="__main__":sys.exit(main())
