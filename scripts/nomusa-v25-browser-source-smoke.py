#!/usr/bin/env python3
"""Browser source smoke: V25 three original paper pages, two corrective overlays."""
import json,sys,threading
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright
root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(headless=True,args=["--no-sandbox"])
  for u in ["/second/index.html","/study-hub/index.html"]:
   p=browser.new_page(viewport={"width":390,"height":844})
   errors=[];p.on("pageerror",lambda e:errors.append(str(e)))
   p.goto(f"http://127.0.0.1:{server.server_port}{u}",wait_until="domcontentloaded")
   p.wait_for_function("window.NOMUSA_V25_MEDIUM_GATE",timeout=16000)
   z=p.evaluate("""() => {
     const c=window.N27_CATALOG?.items||[],g=window.NOMUSA_V25_MEDIUM_GATE;
     const rows=['2016_p5_q2','2019_p4_q3','2020_p7_q3'].map(id=>{
       const q=c.find(x=>x.id===id);return {id,sourceText:q?.sourceText,
         corrected:!!q?.sourceTextBeforeV25,score:Number(q?.points||window.NOMUSA_CANONICAL_SELECTION_V1?.items?.[id]?.verifiedPointsV18||0),scoringApproved:q?.scoringApproved};
     });return {gate:g,rows,canonicalCount:Object.keys(window.NOMUSA_CANONICAL_SELECTION_V1?.items||{}).length};
   }""")
   print(json.dumps({"page":u,"status":z["gate"]["status"],"sourceCorrections":z["gate"].get("corrected"),
                     "canonical":z["canonicalCount"],"errors":errors[:4]},ensure_ascii=False))
   assert z["gate"]["status"].startswith("PASS"),z["gate"]
   assert z["gate"]["corrected"]==2
   assert z["canonicalCount"]==328
   assert [x["corrected"] for x in z["rows"]]==[False,True,True]
   assert all(x["score"]==25 for x in z["rows"])
   assert not errors,errors
   p.close()
  browser.close()
finally:server.shutdown()
