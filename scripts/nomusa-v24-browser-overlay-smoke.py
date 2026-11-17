#!/usr/bin/env python3
"""Quick browser diagnostic for V24 30-source projection; fail closed."""
import json
import sys
import threading
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True,args=["--no-sandbox"])
  for path in ("/second/index.html","/study-hub/index.html"):
   page=b.new_page(viewport={"width":390,"height":844})
   errors=[]
   page.on("pageerror",lambda ex:errors.append(str(ex)))
   page.goto("http://127.0.0.1:%s%s"%(server.server_port,path),wait_until="domcontentloaded")
   page.wait_for_timeout(750)
   obj=page.evaluate("""() => {
     const c=window.N27_CATALOG?.items||[], target=c.find(x=>x.id==='2015_p3_q1');
     return {gate:window.NOMUSA_V24_SOURCE_GATE||null,
       v20:window.NOMUSA_V20_CONTENT_GATE?.status,
       rowCount:c.length, targetText:target?.sourceText?.slice(0,250),
       hasV24Data:!!window.NOMUSA_V24_2021,
       tagCount:document.querySelectorAll('script[src*="nomusa-v24"]').length}
   }""")
   print("V24_SMOKE",path,json.dumps({"gate":obj["gate"],"v20":obj["v20"],
     "rowCount":obj["rowCount"],"target":obj["targetText"],
     "hasV24Data":obj["hasV24Data"],"tagCount":obj["tagCount"],
     "errors":errors[:8]},ensure_ascii=False)[:9000])
   if obj["gate"] is None or not obj["gate"]["status"].startswith("PASS"):
    raise ValueError("V24_JS_OVERLAY_FAIL_"+path+":"+str(obj["gate"])[:1200])
   page.close()
  b.close()
finally:server.shutdown()
