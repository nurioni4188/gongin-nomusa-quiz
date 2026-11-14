#!/usr/bin/env python3
"""NOMUSA-AUTO 1.4 local Chromium gate. Run against the exact review branch checkout.
Does not change files, GitHub, Vercel or localStorage outside temporary Chromium contexts.
Requires Playwright and Chromium. Set NOMUSA_CHROMIUM for a custom binary.
"""
from playwright.sync_api import sync_playwright
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
from pathlib import Path
import json, os, sys, threading, traceback
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
required=['second/index.html','study-hub/index.html','second/legacy_2007_2012_source_only.js']
if any(not (root/p).is_file() for p in required):
 print(json.dumps({'status':'HOLD','missing':[p for p in required if not (root/p).is_file()]}));sys.exit(2)
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
results=[]
def check(page, view, width):
 page.set_default_timeout(6000)
 name=f'{view}_{width}'
 try:
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base+('/second/' if view=='second' else '/study-hub/#study'),wait_until='domcontentloaded')
  page.wait_for_function('window.NOMUSA_LEGACY_STATUS && window.NOMUSA_LEGACY_STATUS.added === 94',polling=100,timeout=6000)
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
  neighbor='legacy2-2007-labor1-q2'
  key='nomusa_rc27_v103_essay_records_v1'
  answer=f'검증용 {view} {width}px'
  old_id='2025-org-1'
  page.evaluate('''([key,id])=>localStorage.setItem(key,JSON.stringify({
    drafts:{[id]:'기존 답안'}, flags:{[id]:true}
  }))''',[key,old_id])
  page.reload(wait_until='domcontentloaded')
  if view=='second':
   page.wait_for_function('window.N27_ESSAY_TEST?.count === 309',polling=100,timeout=6000)
   def select_second():
    page.locator('#n27-year').select_option('2007')
    page.locator('#n27-subject').select_option('노동법Ⅰ')
    assert page.evaluate('N27_ESSAY_TEST.selected')==target
   select_second()
   editor=page.locator('#v1090-editor')
   editor.fill(answer)
   page.locator('#n27-next').click()
   assert page.evaluate('N27_ESSAY_TEST.selected')==neighbor, (errors, page.evaluate("[N27_ESSAY_TEST.selected, !!document.querySelector('#n27-next').onclick]"))
   page.locator('#n27-prev').click()
   assert editor.input_value()==answer
   page.reload(wait_until='domcontentloaded')
   select_second()
   assert editor.input_value()==answer
   page.locator('#n27-timer').click()
   assert page.locator('[data-pane="detail"]').is_disabled()
   page.once('dialog',lambda dialog:dialog.accept())
   page.locator('#n27-timer').click()
   assert page.locator('[data-pane="detail"]').is_enabled()
   page.locator('#n27-flag').click()
   assert '취소' in page.locator('#n27-flag').inner_text()
   with page.expect_download() as backup:
    page.locator('#n27-export').click()
   snapshot=backup.value.path().read_bytes()
   assert json.loads(snapshot)['saved']['drafts']=={old_id:'기존 답안',target:answer}
   editor.fill('복원 전 임시 입력')
   page.once('dialog',lambda dialog:dialog.accept())
   page.locator('#n27-import').set_input_files(
    {'name':'nomusa-backup.json','mimeType':'application/json','buffer':snapshot}
   )
   page.wait_for_function('document.querySelector("#n27-status")?.textContent.includes("복원")',
                          polling=100,timeout=6000)
   assert editor.input_value()==answer
  else:
   def select_hub():
    filters=page.locator('#study-filters')
    if not filters.evaluate('(element) => element.open'):
     filters.locator('summary').click()
    page.locator('#filter-year').select_option('2007')
    page.locator('#filter-subject').select_option('노동법Ⅰ')
    assert page.locator('[data-selected-id]').get_attribute('data-selected-id')==target
   select_hub()
   page.locator('[data-pane="write"]').click()
   editor=page.locator('#draft')
   editor.fill(answer)
   page.locator('[data-action="q-next"]').click()
   assert page.locator('[data-selected-id]').get_attribute('data-selected-id')==neighbor
   page.locator('[data-action="q-prev"]').click()
   page.locator('[data-pane="write"]').click()
   assert editor.input_value()==answer
   page.reload(wait_until='domcontentloaded')
   assert page.locator('[data-selected-id]').get_attribute('data-selected-id')==target
   assert editor.input_value()==answer
   page.locator('[data-action="exam"]').click()
   page.locator('[data-action="exam-start"]').click()
   assert page.locator('[data-trace="3"]').is_disabled()
   assert editor.input_value()==answer
   page.locator('[data-action="exam-stop"]').click()
   page.locator('[data-action="exam-end"]').click()
   assert page.locator('[data-trace="3"]').is_enabled()
   page.locator('[data-action="wrong"]').click()
   page.locator('[data-nav="review"]:visible').click()
   assert page.locator(f'[data-question="{target}"]').is_visible()
  assert page.evaluate('key=>JSON.parse(localStorage.getItem(key)).drafts',key)=={old_id:'기존 답안',target:answer}
  overflow=page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
  assert overflow<=1,f'overflow={overflow}'
  assert not errors,errors[:2]
  results.append({'name':name,'status':'PASS','counts':counts,'overflow':overflow})
 except Exception as e:
  results.append({'name':name,'status':'HOLD','detail':traceback.format_exc(limit=2)[-1700:]})
def check_first(page, width):
 name=f'first_{width}'
 page.set_default_timeout(6000)
 errors=[]
 page.on('pageerror',lambda error:errors.append(str(error)))
 try:
  page.goto(base+'/',wait_until='domcontentloaded')
  assert page.evaluate('window.QDATA.length')==1020
  page.locator('#startBtn').click()
  page.locator('#choices [data-v]').first.click()
  key='nomu1-progress-v2'
  snapshot=page.evaluate('key=>localStorage.getItem(key)',key)
  assert snapshot and json.loads(snapshot)['att']
  page.reload(wait_until='domcontentloaded')
  assert page.evaluate('key=>localStorage.getItem(key)',key)==snapshot
  assert not errors,errors
  results.append({'name':name,'status':'PASS','questions':1020,'choicePersisted':True})
 except Exception:
  results.append({'name':name,'status':'HOLD','errors':errors,
                  'detail':traceback.format_exc(limit=2)[-1700:]})

with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('NOMUSA_CHROMIUM'),headless=True,args=['--no-sandbox'])
 for width in (1440,390,360):
  for view in ('first','second','hub'):
   with browser.new_context(viewport={'width':width,'height':860}) as context:
    page=context.new_page()
    if view=='first':
     check_first(page,width)
    else:
     check(page,view,width)
 qa_page=browser.new_page(viewport={'width':1440,'height':900})
 qa_errors=[]
 qa_page.on('pageerror',lambda error:qa_errors.append(str(error)))
 try:
  qa_page.goto(base+'/study-hub/qa.html')
  qa_page.locator('#run-qa').click()
  qa_page.wait_for_function("!document.querySelector('#run-qa').disabled",
                            polling=100,timeout=100000)
  qa=qa_page.evaluate('JSON.parse(localStorage.getItem(HUB_QA.resultKey))')
  assert qa and len(qa['checks'])==21 and not qa_errors
  results.append({'name':'existing_hub_qa','status':'PASS' if all(
      check['status']=='PASS' for check in qa['checks']) else 'HOLD','checks':qa['checks']})
 except Exception:
  results.append({'name':'existing_hub_qa','status':'HOLD','errors':qa_errors,
                  'detail':traceback.format_exc(limit=2)[-1700:]})
 version=browser.version
 browser.close()
server.shutdown()
out={'schema':'nomusa-auto-v1.4-browser-gate','status':'PASS' if all(x['status']=='PASS' for x in results) else 'HOLD','chromiumVersion':version,'results':results,'actualPreview':'NOT_DEPLOYED','production':'NOT_TOUCHED','legalApproval':'HOLD'}
print(json.dumps(out,ensure_ascii=False,indent=2));sys.exit(0 if out['status']=='PASS' else 1)
