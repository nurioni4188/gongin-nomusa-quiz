#!/usr/bin/env python3
"""Fail-closed V28 sidecar smoke on both existing study pages, no deployment."""
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
   page=b.new_page(viewport={"width":390,"height":844})
   errors=[]
   page.on("pageerror",lambda x:errors.append(str(x)))
   page.goto("http://127.0.0.1:%d%s"%(http.server_port,route),wait_until="domcontentloaded")
   page.wait_for_timeout(700)
   state=page.evaluate("""() => {
     const list=window.N27_CATALOG?.items||[];
     const q=list.find(x=>x.id==='2022-hr-1');
     return {count:list.length,gate:window.NOMUSA_V28_EDITORIAL_GATE||null,
      detailed:q?.detailed||'',compact:q?.compressed||'',
      gate25:window.NOMUSA_V25_MEDIUM_GATE?.status||null};
   }""")
   g=state["gate"]
   if errors or not g or not g["status"].startswith("PASS_") or state["count"]!=328:
    raise ValueError("HOLD_V28_BROWSER_OVERLAY_"+route+" "+json.dumps({"g":g,"errors":errors[:4]},ensure_ascii=False))
   if "Human Relations" in state["detailed"] or "경영시뮬" in state["compact"]:
    raise ValueError("HOLD_V28_OBSOLETE_REFERENCE_REMAINS_"+route)
   if "Human Factors, 20(2)" not in state["detailed"] or "액션러닝" not in state["compact"]:
    raise ValueError("HOLD_V28_PUBLISHER_6_TECHNIQUES_MISSING_"+route)
   print("PASS_V28_BROWSER",route,"total",state["count"],"edited",g["count"],"humanApproval",g["independentExpertApproved"])
   page.close()
  b.close()
finally:http.shutdown()
