#!/usr/bin/env python3
"""Local HTTP Chromium checks. Does not deploy, mutate GitHub or certify legal content."""
from playwright.sync_api import sync_playwright
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import threading, pathlib, json, traceback,sys
ROOT=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else pathlib.Path('work_v1106_site').resolve()
SERVER=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
threading.Thread(target=SERVER.serve_forever,daemon=True).start()
HOST=f'http://127.0.0.1:{SERVER.server_port}'
TARGETS=['2024-민사소송법|2|0','2024-민사소송법|3|0','2026-노동법2|1|1','2026-노동법2|1|2','2026-노동법2|2|0','2026-노동법1|2|0']
NEGATIVE='2023-admin-1'
results=[]
def add(name,ok,detail=''):
 results.append({'name':name,'status':'PASS' if ok else 'HOLD','detail':str(detail)[:550]})
 if not ok: print('HOLD',name,detail,flush=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for w in [1440,390,360]:
  for which in ['second','study-hub']:
   page=browser.new_page(viewport={'width':w,'height':860},device_scale_factor=1)
   errors=[]
   page.on('pageerror',lambda e: errors.append(str(e)))
   try:
    if which=='second':
     page.goto(HOST+'/second/',wait_until='domcontentloaded',timeout=90000)
     page.wait_for_function('window.N27_ESSAY_TEST?.count > 100 && window.N1106_LAW_REVIEW_BRIDGE?.status === "REVIEW_ONLY_HOLD"',timeout=40000)
     for id in TARGETS:
      page.evaluate('(id)=>window.N27_ESSAY_TEST.select(id)',id)
      page.wait_for_selector(f'.n1106-review[data-n1106-question="{id}"]',timeout=8000)
      assert page.locator('.n1106-review details').count()==3,(id,'cards')
      assert page.locator('.n1106-review').inner_text().count('HOLD')>=2
     page.evaluate('(id)=>window.N27_ESSAY_TEST.select(id)',NEGATIVE)
     assert page.locator('.n1106-review').count()==0,'negative not hidden'
     page.evaluate('(id)=>window.N27_ESSAY_TEST.select(id)',TARGETS[0])
     page.locator('#n27-timer').click()
     assert page.locator('.n1106-review').count()==0,'exam review leakage'
     page.once('dialog',lambda d: d.accept())
     page.locator('#n27-timer').click()
     page.wait_for_selector('.n1106-review',timeout=8000)
     # Save and refresh in legacy 2nd-stage app; the adapter must not interfere with storage.
     page.locator('[data-pane="write"]').first.click()
     page.locator('#n27-draft').fill('V1106 local smoke test ' + str(w))
     page.reload(wait_until='domcontentloaded')
     page.wait_for_function('window.N27_ESSAY_TEST?.count > 100')
     page.evaluate('(id)=>window.N27_ESSAY_TEST.select(id)',TARGETS[0])
     page.locator('[data-pane="write"]').first.click()
     assert 'V1106 local smoke test ' + str(w) in page.locator('#n27-draft').input_value(),'legacy draft restore failed'
    else:
     page.goto(HOST+'/study-hub/#study',wait_until='domcontentloaded',timeout=90000)
     page.wait_for_function('window.N1106_LAW_REVIEW_BRIDGE?.status === "REVIEW_ONLY_HOLD" && !!document.querySelector(".study-toolbar")',timeout=45000)
     if page.locator('[data-stage="essay"]').count():page.locator('[data-stage="essay"]').click()
     for id in [TARGETS[0],TARGETS[-1]]:
      page.locator('#search').fill(id)
      page.wait_for_selector(f'[data-question="{id}"]',timeout=8000)
      page.locator(f'[data-question="{id}"]').click()
      page.wait_for_selector(f'.n1106-review[data-n1106-question="{id}"]',timeout=8000)
      assert page.locator('.n1106-review details').count()==3
     page.locator('#search').fill(NEGATIVE)
     page.locator(f'[data-question="{NEGATIVE}"]').click()
     assert page.locator('.n1106-review').count()==0,'hub negative not hidden'
     page.locator('#search').fill(TARGETS[0])
     page.locator(f'[data-question="{TARGETS[0]}"]').click()
     # Switching to exam must hide proposed corrections.
     page.locator('[data-action="exam"]').first.click()
     assert page.locator('.n1106-review').count()==0,'hub exam review leakage'
    horizontal=page.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
    assert horizontal<=1,f'horizontal_overflow {horizontal}'
    assert not errors,f'JS exceptions: {errors[:2]}'
    add(f'{which}_{w}_review_exam_storage_responsive',True,f'6/6 or 2/2 targeted; zero JS exceptions; overflow={horizontal}')
   except Exception as e:
    add(f'{which}_{w}_review_exam_storage_responsive',False,f'{type(e).__name__} {str(e)[:400]} {errors[:1]}')
   finally:page.close()
 browser.close()
SERVER.shutdown()
summary={'schema':'nomusa-v1106-local-http-e2e/1','tests':results,'passed':sum(r['status']=='PASS' for r in results),'held':sum(r['status']!='PASS' for r in results),'browser':'local-Chromium','production':'UNCHANGED','remotePreview':'NOT_TESTED','finalLegalApproval':'0/47 HOLD'}
report=pathlib.Path('/mnt/data/V1106_LOCAL_BROWSER_GATE.json');report.write_text(json.dumps(summary,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(summary,ensure_ascii=False))
sys.exit(0 if summary['held']==0 else 1)
