#!/usr/bin/env python3
"""Non-deploying Chromium gate for unified 2007–2026 second-stage drafts.

Run against an existing local full review-branch checkout:
python scripts/nomusa-canonical-shared-browser-gate.py [repository_root]

Never changes GitHub, Vercel, main, Production, or old saved user records.
All storage tests use disposable browser contexts.
"""
from __future__ import annotations
import json, sys, threading, traceback
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
REQUIRED = [
    "second/index.html", "study-hub/index.html", "study-hub/app.js",
    "second/essay-app.js", "second/nomusa-canonical-selection-v1.js",
    "rc27_essay_catalog.js"
]
missing = [x for x in REQUIRED if not (ROOT / x).is_file()]
if missing:
    print(json.dumps({"status":"HOLD_FULL_SOURCE","missing":missing},ensure_ascii=False))
    sys.exit(2)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print(json.dumps({"status":"HOLD_PLAYWRIGHT_MISSING"},ensure_ascii=False))
    sys.exit(2)

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

srv = ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
threading.Thread(target=srv.serve_forever,daemon=True).start()
BASE = "http://127.0.0.1:%d" % srv.server_port
RESULTS = []
IDENTIFIERS = [
    "legacy2-2007-hrm-q1", "legacy2-2008-hrm-q2",
    "2013_p1_q1", "2014_p4_q1", "2017_p3_q1",
    "2022-org-2", "2024-인사노무관리론|1|1", "2025-org-1",
    "2026-경영조직론|1|1", "2026-경영조직론|1|2",
]
KEY = "nomusa_rc27_v103_essay_records_v1"

def capture(page):
    errors = []
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.on("response",lambda resp: errors.append("HTTP_%d: %s" % (resp.status,resp.url))
            if resp.status >= 400 and resp.url.endswith((".js",".css")) else None)
    return errors

def inventory(page):
    return page.evaluate("""() => {
      const c=window.NOMUSA_CANONICAL_SELECTION_V1, rows=window.N27_CATALOG?.items||[];
      return {status:c?.status,gate:c?.gate,yearCount:new Set(rows.map(x=>x.year)).size,
         firstCount:window.QDATA?.length||null,
         legacyCount:window.NOMUSA_LEGACY_181_DRAFTS?.stats?.target||null,
         drafts:Object.fromEntries(%s.map(id=>[id, c?.items?.[id] ?
           {detailed:c.items[id].detailed,compressed:c.items[id].compressed,
            renderable:c.items[id].renderable}:null]))};
    }""" % json.dumps(IDENTIFIERS,ensure_ascii=False))

def check_inventory(inv):
    gate=inv["gate"]
    assert inv["status"]=="DRAFT_SOURCE_READY",inv
    assert gate["catalogCount"]==377,gate
    assert gate["candidateCount"]==328 and gate["renderable"]==328,gate
    assert gate["uniqueIds"] is True
    assert not gate["missingIds"] and not gate["unexpectedIds"] and not gate["notRenderable"],gate
    assert len(gate["originalParentIds"])==49
    assert inv["yearCount"]==20 and inv["legacyCount"]==181
    assert all(x and x["renderable"] for x in inv["drafts"].values())
    # Question-specific content regression: 2026 organizational bargaining, 12 points.
    # Four comparison axes must be substantive, not a one-paragraph placeholder.
    compressed_2026 = inv["drafts"]["2026-경영조직론|1|1"]["compressed"]
    assert len(compressed_2026) >= 1100, "2026_12PT_COMPACT_STILL_TOO_SHORT"
    assert all(term in compressed_2026 for term in ("지향 목표", "정보공유 수준", "관계의 지속가능성", "분배구조")), "2026_FOUR_AXES_MISSING"
    assert "학술근거:" in compressed_2026, "2026_ACADEMIC_CITATION_MISSING"
    # Regression for literal \\n tokens previously visible in the 2026 compact answer.
    assert "\\n" not in inv["drafts"]["2026-경영조직론|1|1"]["compressed"], "LITERAL_NEWLINE_TOKENS_LEAKED"

def overflow(page,width):
    data=page.evaluate("""() => ({w:document.documentElement.scrollWidth,
      viewport:document.documentElement.clientWidth})""")
    assert data["w"]<=max(width,data["viewport"])+2,data

def choose_hub(page,id):
    year=id[:4]
    page.locator('[data-year="%s"]'%year).first.click()
    if page.viewport_size["width"]<701:
        toggle=page.locator('[data-action="list-toggle"]')
        if toggle.count() and toggle.is_visible():toggle.click()
    page.locator('[data-question="%s"]'%id).first.click()
    page.locator('[data-trace="4"]').first.click()

def check_viewports(browser,width):
    ctx=browser.new_context(viewport={"width":width,"height":880},accept_downloads=True)
    second=ctx.new_page()
    hub=ctx.new_page()
    errorsSecond=capture(second);errorsHub=capture(hub)
    try:
        second.goto(BASE+"/second/",wait_until="domcontentloaded")
        hub.goto(BASE+"/study-hub/#home",wait_until="domcontentloaded")
        second.wait_for_function("window.N27_ESSAY_TEST && window.NOMUSA_CANONICAL_SELECTION_V1?.gate",timeout=15000)
        hub.wait_for_function("window.HubState && window.NOMUSA_CANONICAL_SELECTION_V1?.gate",timeout=15000)
        a,b=inventory(second),inventory(hub)
        check_inventory(a);check_inventory(b)
        for id in IDENTIFIERS:
            assert a["drafts"][id]==b["drafts"][id],id
        overflow(second,width);overflow(hub,width)
        RESULTS.append({"name":"identical_catalog_and_drafts_%s"%width,"status":"PASS",
          "catalog":377,"candidates":328,"ids":len(IDENTIFIERS)})

        # Actual DOM across detailed, compressed, compare, and writing panes.
        id="2025-org-1"
        second.evaluate("id=>window.N27_ESSAY_TEST.select(id)",id)
        second.locator('[data-pane="detail"]').first.click()
        assert second.locator('.nomusa-canonical-draft[data-canonical-id="2025-org-1"]').count()==1
        second.locator('[data-pane="compact"]').first.click()
        assert second.locator('[data-canonical-id="2025-org-1"]').count()>=1
        second.locator('[data-pane="write"]').first.click()
        note="공인노무사 교차화면 검증 %spx"%width
        second.locator('[data-v1090-tab="editor"]').first.click()
        second.locator("#v1090-editor").fill(note)
        second.wait_for_function("([key,id,note]) => JSON.parse(localStorage.getItem(key)||'{}').drafts?.[id]===note",
          arg=[KEY,id,note])

        # Reload the already open hub tab to read the saved draft from the shared key.
        hub.reload(wait_until="domcontentloaded")
        hub.wait_for_function("window.HubState && window.NOMUSA_CANONICAL_SELECTION_V1?.gate",timeout=15000)
        choose_hub(hub,id)
        hub.locator('[data-pane="detail"]').first.click()
        assert hub.locator('.nomusa-canonical-draft[data-canonical-id="2025-org-1"]').count()==1
        hub.locator('[data-pane="compressed"]').first.click()
        assert hub.locator('.nomusa-canonical-compact[data-canonical-id="2025-org-1"]').count()==1
        hub.locator('[data-pane="write"]').first.click()
        assert hub.locator("#draft").input_value()==note
        hub.locator("#draft").fill(note+" / 허브 보강")
        hub.wait_for_function("([key,id,note])=>JSON.parse(localStorage.getItem(key)||'{}').drafts?.[id]===note",
          arg=[KEY,id,note+" / 허브 보강"])

        second.reload(wait_until="domcontentloaded")
        second.wait_for_function("window.N27_ESSAY_TEST",timeout=15000)
        second.evaluate("id=>window.N27_ESSAY_TEST.select(id)",id)
        second.locator('[data-pane="write"]').first.click()
        assert second.locator("#v1090-editor").input_value()==note+" / 허브 보강"
        second.locator('[data-pane="compare"]').first.click()
        assert second.locator('[data-canonical-id="2025-org-1"]').count()>=1
        hub.locator('[data-pane="compare"]').first.click()
        assert hub.locator('[data-canonical-id="2025-org-1"]').count()>=1
        overflow(second,width);overflow(hub,width)
        assert not errorsSecond and not errorsHub,(errorsSecond,errorsHub)
        RESULTS.append({"name":"save_reload_crosspage_detail_compact_compare_%s"%width,"status":"PASS"})
    finally:
        ctx.close()

try:
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,args=["--no-sandbox"])
        for width in (1440,390,360):
            try:check_viewports(browser,width)
            except Exception:
                RESULTS.append({"name":"viewport_%s"%width,"status":"HOLD","error":traceback.format_exc()[-2200:]})
        browser.close()
finally:
    srv.shutdown()
status="PASS" if RESULTS and all(x["status"]=="PASS" for x in RESULTS) else "HOLD"
print(json.dumps({"schema":"nomusa-canonical-shared-browser-gate/1",
  "status":status,"verifiedCode":"local checkout only","browser":"Chromium",
  "main":"UNCHANGED","production":"UNCHANGED","preview":"NOT_DEPLOYED",
  "results":RESULTS},ensure_ascii=False,indent=2))
sys.exit(0 if status=="PASS" else 2)
