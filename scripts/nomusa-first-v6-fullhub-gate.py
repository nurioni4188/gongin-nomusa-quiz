#!/usr/bin/env python3
"""NOMUSA first-stage originals + existing whole-hub browser gate.
Read-only against a complete review checkout. No deployment or baseline mutations.
"""
from pathlib import Path
import json, os, subprocess, sys
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
inputs=["data.js","index.html","rc27_essay_catalog.js","second/index.html",
"second/legacy_2007_2012_source_only.js","study-hub/index.html",
"study-hub/state.js","study-hub/app.js",
"study-hub/legacy-first-v5-correction.js",
"scripts/nomusa-auto-v12-browser-gate.py"]
missing=[p for p in inputs if not (root/p).is_file()]
source=[{"year":y,"form":f,"path":f"incoming/first/{y}_{f}_original.pdf",
"present":(root/f"incoming/first/{y}_{f}_original.pdf").is_file(),
"verifiedQuestionTextOptionAndPrintedPages":0}
for y in [2014,2020,2021] for f in ["A","B"]]
result={"schema":"nomusa-first-v6-existing-source-browser-gate/1",
"reviewOnly":True,"expectedHistoricalAnswers":3400,"approvedForScoring":0,
"sourceQuestions":source,"missingCheckoutFiles":missing,
"browser":{"status":"HOLD","reason":"FULL_REVIEW_CHECKOUT_MISSING" if missing else "PENDING"},
"sourceAlignment":"HOLD_QUESTION_TEXT_OPTIONS_PRINTED_PAGE","release":"NOT_DEPLOYED"}
if not missing:
 env=dict(os.environ)
 if Path("/usr/bin/chromium").is_file():env.setdefault("NOMUSA_CHROMIUM","/usr/bin/chromium")
 try:
  process=subprocess.run([sys.executable,str(root/"scripts/nomusa-auto-v12-browser-gate.py"),str(root)],
                         cwd=root,env=env,text=True,capture_output=True,timeout=190)
  data=json.loads(process.stdout)
  expected={f"{part}_{w}" for part in ["first","second","hub"] for w in [1440,390,360]}
  checks={r.get("name"):r.get("status") for r in data.get("results",[])}
  valid=(process.returncode==0 and data.get("status")=="PASS" and
         all(checks.get(k)=="PASS" for k in expected))
  result["browser"]={"status":"PASS" if valid else "HOLD","checks":checks,
                     "exitCode":process.returncode,"originalReport":data}
 except Exception as err:
  result["browser"]={"status":"HOLD","reason":type(err).__name__+":"+str(err)[:250]}
# File presence does not establish individual question source-page alignment.
result["status"]="PASS_BROWSER_ONLY_SOURCE_HOLD" if result["browser"]["status"]=="PASS" else "HOLD"
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(0 if result["browser"]["status"]=="PASS" else 2)
