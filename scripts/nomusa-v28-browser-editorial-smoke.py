#!/usr/bin/env python3
"""Inspect Goldstein single-answer canonical overlay in two protected local pages."""
import json,sys,threading
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
class Silent(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
http=ThreadingHTTPServer(("127.0.0.1",0),partial(Silent,directory=str(root)))
threading.Thread(target=http.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True,args=["--no-sandbox"])
  for route in ("/second/index.html","/study-hub/index.html"):
   page=b.new_page(viewport={"width":390,"height":844});errors=[]
   page.on("pageerror",lambda x:errors.append(str(x)))
   page.goto("http://127.0.0.1:%d%s"%(http.server_port,route),wait_until="domcontentloaded")
   page.wait_for_timeout(650)
   state=page.evaluate("""() => {
     const q=window.NOMUSA_CANONICAL_SELECTION_V1?.items?.['2022-hr-1'];
     return {count:Object.keys(window.NOMUSA_CANONICAL_SELECTION_V1?.items||{}).length,
      gate:window.NOMUSA_V28_EDITORIAL_GATE||null,
      detailed:q?.detailed||'',compressed:q?.compressed||'',
      oldDetailRetained:!!q?.detailedBeforeV28,
      oldCompactRetained:!!q?.compressedBeforeV28};
   }""")
   g=state["gate"]
   if errors or not g or not g["status"].startswith("PASS_") or state["count"]!=328:
    raise ValueError("HOLD_V28_BROWSER_OVERLAY_"+route+" "+json.dumps({"g":g,"errors":errors[:4]},ensure_ascii=False))
   if not (state["oldDetailRetained"] and state["oldCompactRetained"]):
    raise ValueError("HOLD_OLD_DRAFTS_NOT_PRESERVED_"+route)
   if "Human Relations" in state["detailed"] or "경영시뮬" in state["compressed"]:
    raise ValueError("HOLD_V28_OBSOLETE_REFERENCE_REMAINS_"+route)
   if "Human Factors, 20(2)" not in state["detailed"] or "액션러닝" not in state["compressed"]:
    raise ValueError("HOLD_V28_PUBLISHER_SIX_METHODS_MISSING_"+route)
   print("PASS_V28_BROWSER",route,"catalog",state["count"],"edited",g["count"],"humanApproval",g["independentExpertApproved"])
   page.close()
  b.close()
finally:http.shutdown()
