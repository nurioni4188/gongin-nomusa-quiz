#!/usr/bin/env python3
"""V45 browser gate for source-approved-only historical QData additions.

The original V42 E2E is run separately: this test supplements it with
approved count, save/restore, app source images and review-note grading;
it does not infer validity of source content from browser success.
"""
import json
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
PROMOTION=ROOT/"review-artifacts/NOMUSA_FIRST_V44/NOMUSA_FIRST_V44_PROMOTION_GATE.json"
REPORT=ROOT/"review-artifacts/NOMUSA_FIRST_V45/NOMUSA_FIRST_V45_PC_MOBILE_APPROVED_ONLY.json"

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*_args):pass

def main():
    proof=json.loads(PROMOTION.read_text(encoding="utf-8"))
    verified=proof["actualNewVerifiableApprovals"]
    ids=proof["approvedIDs"]
    assert verified==len(ids) and verified>=0 and proof["expectedBankTotal"]==2281+verified
    srv=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever,daemon=True).start()
    cases=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
            for width in (1440,390,360):
                c=browser.new_context(viewport={"width":width,"height":860},locale="ko-KR")
                page=c.new_page()
                errors=[]
                page.on("pageerror",lambda exc:errors.append(str(exc)))
                base=f"http://127.0.0.1:{srv.server_port}/index.html"
                try:
                    page.goto(base,wait_until="load",timeout=35000)
                    page.locator("#startBtn").wait_for(timeout=20000)
                    vals=page.evaluate("""()=>{
                        const d=window.NOMUSA_FIRST_V44_APPROVED||[];
                        const keys=window.NOMUSA_FIRST_V44_SCORING_IDS||[];
                        return {added:d.length, keys:keys.length,
                           ids:d.map(x=>x.k),allOptions:d.every(x=>x.o.length===5),
                           allExplanations:d.every(x=>window.NOMUSA_V108_EXPLANATIONS.entries[x.k]?.options?.length===5),
                           existingBase:window.QDATA.length, v42:window.NOMUSA_FIRST_V42_TWO_THEORY.length};
                    }""")
                    assert vals["existingBase"]==1020 and vals["v42"]==2
                    assert vals["added"]==vals["keys"]==verified
                    assert vals["ids"]==ids and vals["allOptions"] and vals["allExplanations"]
                    assert f"{2281+verified:,}" in page.locator("#app").inner_text()
                    cases.append({"width":width,"test":"approved_gate_2281_plus_new_source_only","PASS":True})
                    # Browser smoke test each registered novel year/subject, max 6, plus legacy V42 regression.
                    to_smoke=ids[:6]
                    for ident in to_smoke:
                        # Existing local-progress serialization; never mutate source QA metadata.
                        initial={"att":{},"star":{},"memo":{},"prefs":{},"ungraded":{},
                           "session":{"ks":[ident],"i":0,"mode":"practice","ans":{},
                                      "done":False,"t0":int(page.evaluate("Date.now()")),"limit":0}}
                        page.evaluate("(obj)=>localStorage.setItem('nomu1-progress-v2',JSON.stringify(obj))",initial)
                        page.reload(wait_until="load")
                        page.locator("#resumeBtn").click()
                        qid=page.locator(".qmeta").inner_text()
                        expected=int(page.evaluate("(key)=>window.NOMUSA_FIRST_V44_APPROVED.find(x=>x.k===key).a[0]",ident))
                        wrong=1 if expected!=1 else 2
                        page.locator(f'#choices [data-v="{wrong}"]').click()
                        assert page.locator(".fb.bad").count()==1,ident
                        assert page.locator(f'[data-explanation="{ident}"]').count()==1,ident
                        stored=page.evaluate("JSON.parse(localStorage.getItem('nomu1-progress-v2'))")
                        assert stored["att"][ident]["ok"] is False, ident
                        assert ident not in stored.get("ungraded",{}), ident
                        page.locator('#tabs button[data-v="wrong"]').click()
                        assert page.locator("#app .li").count()>=1
                        page.reload(wait_until="load")
                        page.locator('#tabs button[data-v="wrong"]').click()
                        assert page.locator("#app .li").count()>=1
                        cases.append({"width":width,"test":"source_key_explanation_scoring_wrongnote_restore_"+ident,"PASS":True})
                    assert page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=1
                    assert not errors,errors
                    cases.append({"width":width,"test":"no_mobile_overflow_or_js_error","PASS":True})
                finally:
                    c.close()
            browser.close()
    finally:
        srv.shutdown()
    out={"schema":"NOMUSA_FIRST_V45_APPROVED_ONLY_BROWSER_QA/1",
         "status":"PASS" if all(x["PASS"] for x in cases) and len(cases)==6+3*min(verified,6) else "HOLD",
         "viewports":[1440,390,360],"tests":len(cases),
         "expected":6+3*min(verified,6),"newLearningScoringItems":verified,
         "unapprovedHistoricalQuestionIDsStillHeld":789-verified,
         "oldMainQDataPreserved":1020,"oldHistoricalKeysPreserved":2279,
         "newPreviewDeployment":"NOT_DEPLOYED","cases":cases}
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k!="cases"},ensure_ascii=False))
    return 0 if out["status"]=="PASS" else 1

if __name__=="__main__":
    sys.exit(main())
