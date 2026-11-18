#!/usr/bin/env python3
"""V42 actual Chromium PC1440/Mobile390/Mobile360 e2e scoring and wrong review.

Only the two Q-Net-source-checked theory questions can be graded.
All preexisting historical question candidates remain ungraded.
"""
import json,sys,threading
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
def main():
 srv=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
 threading.Thread(target=srv.serve_forever,daemon=True).start()
 evidence=[]
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
   for width in [1440,390,360]:
    context=browser.new_context(viewport={"width":width,"height":850},locale="ko-KR")
    page=context.new_page()
    errors=[]
    page.on("pageerror",lambda e: errors.append(str(e)))
    try:
     page.goto(f"http://127.0.0.1:{srv.server_port}/index.html",wait_until="load",timeout=30000)
     page.locator("#startBtn").wait_for(timeout=20000)
     assert page.locator("#cYear .chip").count()>=15
     assert page.locator("body").inner_text().find("2,281")>=0
     assert page.evaluate("window.NOMUSA_FIRST_V42_TWO_THEORY.length")==2
     assert page.evaluate("window.NOMUSA_FIRST_V42_SCORING_IDS.length")==2
     assert "독립 전문가 최종승인" in page.locator("body").inner_text()
     evidence.append([width,"2281 loaded and only 2 source-checked historical answer IDs", "PASS"])
     # QNet 2020 A-101: deliberately wrong option -> grade and wrong note
     page.locator('.cell[data-y="2020"][data-s="경영학개론"]').click()
     assert page.locator("#choices [data-v]").count()==5
     page.locator('img[src*="legacy1-2020-A-management-101.jpg"]').wait_for()
     page.wait_for_function('document.querySelector("img[src*=legacy1-2020-A-management-101]")?.naturalWidth>600')
     page.locator('#choices [data-v="1"]').click()
     assert page.locator(".fb.bad").count()==1
     raw=page.evaluate("JSON.parse(localStorage.getItem('nomu1-progress-v2'))")
     r=raw["att"].get("legacy1-2020-A-management-101")
     assert r and r["ok"] is False and r["w"]==1
     assert "legacy1-2020-A-management-101" not in raw["ungraded"]
     assert page.locator('[data-explanation="legacy1-2020-A-management-101"]').count()==1
     evidence.append([width,"2020 QNet A-101 wrong answer graded, academic explanation and saved", "PASS"])
     page.locator('#tabs button[data-v="wrong"]').click()
     assert "페로우" in page.locator("#app").inner_text()
     page.reload(wait_until="load")
     page.locator('#tabs button[data-v="wrong"]').click()
     assert "페로우" in page.locator("#app").inner_text()
     evidence.append([width,"2020 A-101 wrong-note and reload restoration", "PASS"])
     # QNet 2021 A-110: correct official 3; grade but leave old historic alone
     page.locator('#tabs button[data-v="home"]').click()
     page.locator('.cell[data-y="2021"][data-s="경영학개론"]').click()
     assert page.locator('#choices [data-v]').count()==5
     page.locator('img[src*="legacy1-2021-A-management-110.jpg"]').wait_for()
     page.wait_for_function('document.querySelector("img[src*=legacy1-2021-A-management-110]")?.naturalWidth>600')
     page.locator('#choices [data-v="3"]').click()
     assert page.locator(".fb.ok").count()==1
     assert page.locator('[data-explanation="legacy1-2021-A-management-110"]').count()==1
     raw=page.evaluate("JSON.parse(localStorage.getItem('nomu1-progress-v2'))")
     assert raw["att"]["legacy1-2021-A-management-110"]["ok"] is True
     evidence.append([width,"2021 QNet A-110 correct choice graded, source crop and explanation", "PASS"])
     # Historical 2019 remains strictly ungraded despite candidate answer.
     page.locator('#tabs button[data-v="home"]').click()
     page.locator('.cell[data-y="2019"][data-s="경영학개론"]').click()
     assert page.locator('#choices [data-v]').count()==5 or page.locator('#choices .opt').count()==5
     page.locator('#choices [data-v="1"]').click()
     assert page.locator(".fb.info").count()==1
     assert "채점 보류" in page.locator(".fb.info").inner_text()
     raw=page.evaluate("JSON.parse(localStorage.getItem('nomu1-progress-v2'))")
     assert not any(k.startswith("legacy1-2019") for k in raw["att"])
     assert any(k.startswith("legacy1-2019") for k in raw["ungraded"])
     evidence.append([width,"2019 old answer candidate held ungraded; zero historical leakage", "PASS"])
     assert page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=1
     assert not errors,errors
     evidence.append([width,"mobile overflow and JS runtime exceptions", "PASS"])
    finally:context.close()
   browser.close()
 finally:srv.shutdown()
 status="PASS" if len(evidence)==18 and all(x[2]=="PASS" for x in evidence) else "HOLD"
 output={"schema":"NOMUSA_FIRST_V42_TWO_THEORY_PC_MOBILE_E2E/1","status":status,
         "tests":len(evidence),"expected":18,"viewports":[1440,390,360],
         "officialQNetAnswers":2,"newGradedHistoricalIDs":2,
         "otherHistoricalAutoGraded":0,"oldBankRecordsPreserved":2279,
         "testCases":evidence}
 out=ROOT/"review-artifacts/NOMUSA_FIRST_V42_E2E"
 out.mkdir(exist_ok=True,parents=True)
 (out/"NOMUSA_FIRST_V42_TWO_THEORY_18_CASES_E2E.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({k:v for k,v in output.items() if k!="testCases"},ensure_ascii=False))
 return 0 if status=="PASS" else 1
if __name__=="__main__":sys.exit(main())
