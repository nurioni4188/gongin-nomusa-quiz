#!/usr/bin/env python3
"""NOMUSA-AUTO 1.2 local Chromium gate. Run against the exact review branch checkout.
Does not change files, GitHub, Vercel or localStorage outside temporary Chromium contexts.
Requires: python -m playwright install chromium, playwright Python module.
"""
from playwright.sync_api import sync_playwright
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
from pathlib import Path
import json, sys, threading
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
required=['second/index.html','study-hub/index.html','second/legacy_2007_2012_source_only.js']
if any(not (root/p).is_file() for p in required):
 print(json.dumps({'status':'HOLD','missing':[p for p in required if not (root/p).is_file()]}));sys.exit(2)
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
results=[]
def check(page, view, width):
 name=f'{view}_{width}'
 try:
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base+('/second/' if view=='second' else '/study-hub/#study'),wait_until='domcontentloaded')
  page.wait_for_function('window.NOMUSA_LEGACY_STATUS && window.NOMUSA_LEGACY_STATUS.added === 94',timeout=30000)
  counts=page.evaluate('''() => ({
    all:window.N27_CATALOG?.items?.length||0,
    added:window.N27_CATALOG?.items?.filter(x=>x.origin==='LEGACY_HWP_2007_2012').length||0,
    old:window.N27_CATALOG?.items?.filter(x=>x.origin!=='LEGACY_HWP_2007_2012').length||0,
    years:[...new Set((window.N27_CATALOG?.items||[]).map(x=>x.year))].sort(),
    approvals:window.N27_CATALOG?.items?.filter(x=>x.origin==='LEGACY_HWP_2007_2012'&&x.approved).length||0
  })''')
  assert counts['all']==309 and counts['added']==94 and counts['old']==215,counts
  assert counts['years'][0]==2007 and counts['years'][-1]==2026 and len(counts['years'])==20,counts
  assert counts['approvals']==0
  target='legacy2-2007-labor1-q1'
  if view=='second':
   page.wait_for_function('!!window.N27_ESSAY_TEST && window.N27_ESSAY_TEST.count === 309',timeout=30000)
   page.evaluate('(id)=>window.N27_ESSAY_TEST.select(id)',target)
   page.locator('[data-pane="write"]').first.click()
   page.locator('#n27-draft').fill('nomusa-v12-save-'+str(width))
   page.reload(wait_until='domcontentloaded')
   page.wait_for_function('window.N27_ESSAY_TEST?.count === 309',timeout=30000)
   page.evaluate('(id)=>window.N27_ESSAY_TEST.select(id)',target)
   page.locator('[data-pane="write"]').first.click()
   assert page.locator('#n27-draft').input_value()=='nomusa-v12-save-'+str(width)
  else:
   page.wait_for_selector('#search',timeout=30000)
   if page.locator('[data-stage="essay"]').count():page.locator('[data-stage="essay"]').click()
   page.locator('#search').fill(target)
   page.locator('[data-question="'+target+'"]').click()
   assert page.locator('[data-selected-id="'+target+'"]').count()==1
  overflow=page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
  assert overflow<=1,f'overflow={overflow}'
  assert not errors,errors[:2]
  results.append({'name':name,'status':'PASS','counts':counts,'overflow':overflow})
 except Exception as e:
  results.append({'name':name,'status':'HOLD','detail':str(e)[:350]})
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
 for width in (1440,390,360):
  for view in ('second','hub'):
   context=browser.new_context(viewport={'width':width,'height':860})
   check(context.new_page(),'second' if view=='second' else 'hub',width)
   context.close()
 browser.close()
server.shutdown()
out={'schema':'nomusa-auto-v1.2-browser-gate','status':'PASS' if all(x['status']=='PASS' for x in results) else 'HOLD','results':results,'actualPreview':'NOT_DEPLOYED','production':'NOT_TOUCHED','legalApproval':'HOLD'}
print(json.dumps(out,ensure_ascii=False,indent=2));sys.exit(0 if out['status']=='PASS' else 1)
