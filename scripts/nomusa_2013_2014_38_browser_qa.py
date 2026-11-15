#!/usr/bin/env python3
"""Local QA for 2013/2014 38 child questions in existing study hub (no deploy)."""
from __future__ import annotations
import json
import threading
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
TARGETS=[
    (2013,"2013_p1_q1",50,"2013_p1"),
    (2013,"2013_p1_q2",25,"2013_p1"),
    (2014,"2014_p5_q1",50,"2014_p5"),
    (2014,"2014_p5_q3",25,"2014_p5"),
]
# Batch 1 authored answers (detail / compressed / 3-3-3 / compare panes).
ANSWERED=[("2013_p1_q1","2013_p1"),("2013_p1_q2","2013_p1"),("2013_p2_q1","2013_p2")]

def open_question(page,width,year,id):
    if not page.locator('[data-year="'+str(year)+'"]').is_visible():
        page.locator('[data-nav="home"]:visible').first.click()
    page.locator(f'[data-year="{year}"]').click()
    if width<701:
        page.locator('[data-action="list-toggle"]').click()
    page.locator(f'[data-question="{id}"]').click()

def ensure_writer(page):
    # Answered children open on the detail pane; switch to the writer.
    if page.locator("#draft").count()==0 and page.locator('[data-pane="write"]').count():
        page.locator('[data-pane="write"]').click()
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def main():
    errors=[]
    ledger=json.loads((ROOT/"review/NOMUSA_SECOND_2013_2014_38_AND_181_LEDGER_20261115.json").read_text(encoding="utf-8"))
    assert len(ledger["legacyLedger181"])==181
    assert ledger["extractedMainQuestionCount"]==38

    server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    passed=0
    cases=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(args=["--no-sandbox"],headless=True)
            for width in (1440,390,360):
                context=browser.new_context(viewport={"width":width,"height":860})
                page=context.new_page()
                page.set_default_timeout(9500)
                page.on("pageerror",lambda exc: errors.append(str(exc)))
                url=f"http://127.0.0.1:{server.server_port}/study-hub/index.html?qa=38_181_{width}#home"
                page.goto(url,wait_until="domcontentloaded")
                pre=page.evaluate("""() => ({
                   originals: window.N27_CATALOG.items.length,
                   historical: window.NOMUSA_2013_2014_SPLIT_V1.items.length,
                   old181: window.NOMUSA_LEGACY_181_DRAFTS.stats.target,
                   collisions: window.NOMUSA_2013_2014_SPLIT_V1.items.some(
                      x => window.N27_CATALOG.items.some(old=>old.id===x.id))
                })""")
                assert pre=={"originals":309,"historical":38,"old181":181,"collisions":False},pre
                cases.append({"width":width,"test":"source_identity","status":"PASS"})
                passed+=1
                for year,id,points,parent in TARGETS:
                    try:
                        open_question(page,width,year,id)
                        ensure_writer(page)
                        assert page.locator('[data-selected-id]').get_attribute('data-selected-id')==id
                        assert f"({points}점)" in page.locator("#trace-content").inner_text() or f"{points}점" in page.locator("#trace-content").inner_text()
                        assert parent in page.locator('.detail-id').inner_text()
                        assert page.locator("#draft").count()==1
                        note=f"{id} 개별 답안 임시저장 {width} 테스트"
                        page.locator("#draft").fill(note)
                        assert page.evaluate(f'window.HubState.essay.drafts[{json.dumps(id)}]')==note
                        page.reload(wait_until="domcontentloaded")
                        if page.locator("#draft").count()==0:
                            page.locator('[data-nav="home"]:visible').first.click()
                            page.locator(f'[data-year="{year}"]').click()
                            if width<701:page.locator('[data-action="list-toggle"]').click()
                            page.locator(f'[data-question="{id}"]').click()
                        ensure_writer(page)
                        assert page.locator("#draft").input_value()==note
                        assert page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=1
                        cases.append({"width":width,"id":id,"test":"open_and_save_restore","status":"PASS"})
                        passed+=1
                    except Exception as exc:
                        cases.append({"width":width,"id":id,"status":"HOLD","error":str(exc)[-420:]})
                        break
                for id,parent in ANSWERED:
                    try:
                        open_question(page,width,2013,id)
                        assert page.locator('[data-selected-id]').get_attribute('data-selected-id')==id
                        assert parent in page.locator('.detail-id').inner_text()
                        page.locator('[data-pane="detail"]').click()
                        detail=page.locator("#trace-content").inner_text()
                        assert "상세 학습답안" in detail and ". 결론" in detail and "HOLD" in detail,detail[:200]
                        assert page.locator(".memory-groups > div").count()==3
                        page.locator('[data-pane="compressed"]').click()
                        assert "시험장 압축답안" in page.locator("#trace-content").inner_text()
                        page.locator('[data-pane="compare"]').click()
                        assert page.locator(".checklist .check-item").count()>=5
                        assert page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=1
                        cases.append({"width":width,"id":id,"test":"authored_answer_panes","status":"PASS"})
                        passed+=1
                    except Exception as exc:
                        cases.append({"width":width,"id":id,"test":"authored_answer_panes","status":"HOLD","error":str(exc)[-420:]})
                context.close()
            browser.close()
    finally:server.shutdown()
    result={
      "schema":"nomusa-2013-2014-38-browser-local/1",
      "expected":24,"passed":passed,
      "status":"PASS" if passed==24 and not errors else "HOLD",
      "cases":cases,"errors":errors,
      "sourceAndAnswerFinalApproval":"HOLD",
      "preview":"NOT_DEPLOYED",
    }
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["status"]=="PASS" else 1

if __name__=="__main__":sys.exit(main())
