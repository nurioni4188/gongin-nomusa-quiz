#!/usr/bin/env python3
"""V11.10 preview-only source/draft/compressed/write/review E2E; no scoring approvals."""
from __future__ import annotations
import json
import traceback
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def main():
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    results=[]
    try:
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True,args=["--no-sandbox"])
            for width in (1440,390,360):
                ctx=browser.new_context(viewport={"width":width,"height":860},accept_downloads=True)
                page=ctx.new_page()
                page.set_default_timeout(7000)
                errors=[]
                page.on("pageerror",lambda error: errors.append(str(error)))
                key="legacy2-2010-labor-economics-q1"
                try:
                    page.goto(f"http://127.0.0.1:{server.server_port}/study-hub/index.html?qa=essay181_{width}#home",wait_until="domcontentloaded")
                    inventory=page.evaluate("""() => ({
                      ...window.NOMUSA_LEGACY_181_DRAFTS.stats,
                      catalog:window.N27_CATALOG.items.length,
                      years:new Set(window.N27_CATALOG.items.map(x=>x.year)).size,
                      idCount:new Set(window.N27_CATALOG.items.map(x=>x.id)).size,
                      approved:Object.values(window.NOMUSA_LEGACY_181_DRAFTS.items).filter(x=>x.verifiedForScoring).length
                    })""")
                    assert inventory["target"]==181 and inventory["individualDrafts"]==132
                    assert inventory["bundleReview"]==14 and inventory["imageReview"]==35
                    assert inventory["catalog"]==309 and inventory["years"]==20 and inventory["idCount"]==309
                    assert inventory["approved"]==0
                    results.append({"viewport":width,"check":"original_catalog_309_and_181_registry","status":"PASS"})
                    page.locator('[data-year="2010"]').click()
                    if width<701:page.locator('[data-action="list-toggle"]').click()
                    page.locator(f'[data-question="{key}"]').click()
                    assert page.locator('[data-selected-id]').get_attribute('data-selected-id')==key
                    assert '수요독점' in page.locator('#trace-content').inner_text()
                    assert '공식 모범답안 아님' in page.locator('#trace-content').inner_text()
                    page.locator('[data-pane="compressed"]').click()
                    assert 'ME=MRP' in page.locator('#trace-content').inner_text()
                    assert page.locator(".memory-box .memory-groups > div").count()==3
                    page.locator('[data-pane="write"]').click()
                    assert '수요독점' in page.locator('.writer-original-text').inner_text()
                    draft='Ⅰ. 논점\nME=MRP의 균형을 먼저 도식화한다.\nⅡ. 비교\n경쟁시장의 w=MRP와 비교한다.'
                    page.locator('#draft').fill(draft)
                    assert page.evaluate(f'window.HubState.essay.drafts[{json.dumps(key)}]')==draft
                    page.reload(wait_until="domcontentloaded")
                    if page.locator('#draft').count()==0:
                        page.locator('[data-question="'+key+'"]').click()
                        page.locator('[data-pane="write"]').click()
                    assert page.locator('#draft').input_value()==draft
                    page.locator('[data-pane="compare"]').click()
                    assert draft in page.locator('#trace-content').inner_text()
                    assert page.locator('.memory-box .memory-groups > div').count()==3
                    page.locator('[data-action="wrong"]').click()
                    assert page.evaluate(f'window.HubState.hub.wrong[{json.dumps(key)}]') is True
                    results.append({"viewport":width,"check":"detailed_compressed_333_write_refresh_compare_review","status":"PASS"})
                    page.locator('[data-nav="home"]:visible').first.click()
                    page.locator('[data-year="2015"]').click()
                    if width<701:page.locator('[data-action="list-toggle"]').click()
                    page.locator('[data-question="2015_p1"]').click()
                    assert page.evaluate("window.NOMUSA_LEGACY_181_DRAFTS.items['2015_p1'].draftStatus") == 'IMAGE_TEXT_VERIFICATION_REQUIRED'
                    assert page.locator('[data-pane="detail"]').is_disabled()
                    page.locator('[data-pane="write"]').click()
                    assert page.locator('#draft').count()==1
                    assert not page.evaluate("window.NOMUSA_LEGACY_181_DRAFTS.items['2015_p1'].verifiedForScoring")
                    results.append({"viewport":width,"check":"image_source_HOLD_and_manual_writing","status":"PASS"})
                    page.locator('[data-nav="home"]:visible').first.click()
                    page.locator('[data-year="2026"]').click()
                    if width<701:page.locator('[data-action="list-toggle"]').click()
                    current=page.locator('[data-question]').first
                    assert current.count()==1
                    current.click()
                    assert '2026년' in page.locator('[data-selected-id]').locator("xpath=..").inner_text()
                    assert page.locator('[data-pane="detail"]').is_enabled()
                    assert page.locator('[data-pane="compressed"]').is_enabled()
                    assert '학습용 초안' in page.locator('#trace-content').inner_text()
                    assert page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')<=1
                    results.append({"viewport":width,"check":"existing_2026_answers_and_mobile_overflow","status":"PASS"})
                except Exception as exc:
                    results.append({"viewport":width,"check":"runtime_E2E","status":"HOLD","reason":traceback.format_exc()[-1600:]})
                if errors:results.append({"viewport":width,"check":"runtime_console","status":"HOLD","errors":errors[:8]})
                ctx.close()
            browser.close()
    finally:
        server.shutdown()
    ok=sum(x["status"]=="PASS" for x in results)
    status="PASS" if ok==12 and len(results)==12 else "HOLD"
    print(json.dumps({
      "schema":"nomusa-second-legacy181-browser-gate/1",
      "status":status,"expected":12,"passed":ok,
      "cases":results,
      "reviewGate":"HOLD_LEGAL_AND_ACADEMIC",
      "preview":"NOT_DEPLOYED"
    },ensure_ascii=False,indent=2))
    return 0 if status=="PASS" else 1

if __name__=="__main__":sys.exit(main())
