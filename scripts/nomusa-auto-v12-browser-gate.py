#!/usr/bin/env python3
"""NOMUSA-AUTO V6.8 local Chromium gate. Run against the exact review branch checkout.
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
   page.locator('#n1079-advanced summary').first.click()
   assert page.get_by_role('heading',name='원본 HWP 1쪽',exact=True).is_visible()
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
   page.locator('[data-trace="1"]').click()
   assert page.get_by_role('heading',name='원본 HWP 1쪽',exact=True).is_visible()
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
  page.locator('#resumeBtn').click()
  assert page.locator('.fb').is_visible()
  page.locator('#tabs [data-v="stats"]').click()
  with page.expect_download() as backup:
   page.locator('#ex').click()
  backup_data=backup.value.path().read_bytes()
  assert json.loads(backup_data)['progress']['att']==json.loads(snapshot)['att']
  page.locator('#rs').click()
  page.locator('#mOk').click()
  assert not page.evaluate('key=>JSON.parse(localStorage.getItem(key)).att && Object.keys(JSON.parse(localStorage.getItem(key)).att).length',key)
  page.locator('#im').set_input_files(
   {'name':'nomusa-first.json','mimeType':'application/json','buffer':backup_data}
  )
  page.locator('#mOk').click()
  assert page.evaluate('key=>JSON.parse(localStorage.getItem(key)).att',key)==json.loads(snapshot)['att']

  page.locator('#tabs [data-v="home"]').click()
  page.locator('#cOrder').get_by_role('button',name='10문항',exact=True).click()
  page.locator('#cMode').get_by_role('button',name='실전 · 끝나고 채점',exact=True).click()
  page.locator('#startBtn').click()
  assert page.locator('#timer').is_visible()
  first=page.locator('.qmeta').inner_text().splitlines()[0]
  page.locator('#choices [data-v="2"]').click()
  assert not page.locator('.fb').count()
  page.locator('#nx').click()
  assert page.locator('.qmeta').inner_text().splitlines()[0]!=first
  page.locator('#pv').click()
  assert page.locator('.qmeta').inner_text().splitlines()[0]==first
  assert page.locator('#choices [data-v="2"]').evaluate("button=>button.classList.contains('sel')")
  page.reload(wait_until='domcontentloaded')
  page.locator('#resumeBtn').click()
  assert page.locator('#timer').is_visible()
  assert page.locator('#choices [data-v="2"]').evaluate("button=>button.classList.contains('sel')")
  assert not page.locator('.fb').count()
  overflow=page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
  assert overflow<=1,f'overflow={overflow}'
  page.locator('#fin').click()
  page.locator('#mOk').click()
  page.locator('#reW').wait_for(state='visible')
  assert not errors,errors
  page.locator('#tabs [data-v="home"]').click()
  page.get_by_role('button',name='2008 · 17회 A형',exact=True).click()
  page.get_by_role('button',name='2026 · 35회',exact=True).click()
  page.get_by_role('button',name='연습 · 바로 채점',exact=True).click()
  page.locator('#startBtn').click()
  assert '2008년 A형' in page.locator('.qmeta').inner_text()
  assert page.locator('#choices button').count()==5
  assert '5011154' in page.get_by_role('link',name='Q-Net 제17회 A형 원문').get_attribute('href')
  page.locator('#choices [data-v="1"]').click()
  assert page.locator('.fb.info').first.is_visible()
  page.locator('#nx').click()
  assert '2번' in page.locator('.qmeta').inner_text()
  page.reload(wait_until='domcontentloaded')
  page.locator('#resumeBtn').click()
  assert '2번' in page.locator('.qmeta').inner_text()
  page.locator('#pv').click()
  assert page.locator('.fb.info').first.is_visible()
  page.locator('#markReview').click()
  assert page.locator('#markReview').get_attribute('aria-pressed')=='true'
  state=page.evaluate('key=>JSON.parse(localStorage.getItem(key))',key)
  assert state['ungraded']['legacy1-2008-A-labor1-001']['last']==1
  assert state['ungraded']['legacy1-2008-A-labor1-001']['review'] is True
  assert 'legacy1-2008-A-labor1-001' not in state['att']
  assert page.locator('.fb.ok,.fb.bad').count()==0
  assert '최종정답 <strong>' not in page.locator('#app').inner_html()
  assert all(record in state['att'] for record in json.loads(snapshot)['att'])
  page.locator('#tabs [data-v="home"]').click()
  page.get_by_role('button',name='실전 · 끝나고 채점',exact=True).click()
  page.locator('#startBtn').click()
  page.locator("#mOk").click()
  assert '2008년 A형' in page.locator('.qmeta').inner_text()
  assert page.locator('#timer').is_visible()
  page.locator('#choices [data-v="1"]').click()
  assert page.locator('.fb[role="note"]').is_visible()
  assert page.locator('.fb[role="status"]').count()==0
  page.locator('#fin').click()
  page.locator('#mOk').click()
  page.locator('#reW').wait_for(state='visible')
  assert '채점 보류' in page.locator('#app').inner_text()
  assert '100점 만점' not in page.locator('#app').inner_text()
  assert page.evaluate('window.NOMUSA_FIRST_2008.length')==125
  assert page.evaluate("NOMUSA_FIRST_2008.filter(q=>q.s==='영어').length")==25
  assert page.evaluate("NOMUSA_FIRST_2008.find(q=>q.s==='경제학원론'&&q.n===5).paperHtml.includes('<table')")
  page.locator('#tabs [data-v="home"]').click()
  page.locator('[data-y="2008"][data-s="영어"]').click()
  assert page.locator('.source-layout').is_visible()
  page.locator('#jumper summary').click()
  page.locator('#jumpN').fill('18')
  page.locator('#jumpGo').click()
  assert 'No country can give itself a new past.' in page.locator('.source-layout').inner_text()
  assert page.locator('#choices button').count()==5

  page.locator('#tabs [data-v="home"]').click()
  page.locator('[data-y="2010"][data-s="경영학개론"]').click()
  page.locator('#mOk').click()
  assert '2010년 A형' in page.locator('.qmeta').inner_text()
  assert page.evaluate('NOMUSA_FIRST_2010.length')==125
  assert '5021186' in page.get_by_role('link',name='Q-Net 정답 출처').get_attribute('href')
  page.locator('#choices [data-v="5"]').click()
  assert page.locator('.fb.info').first.is_visible()
  assert page.locator('.fb.ok,.fb.bad').count()==0
  page.locator('#tabs [data-v="home"]').click()
  page.locator('[data-y="2009"][data-s="노동법(2)"]').click()
  page.locator('#mOk').click()
  assert '2009년 A형' in page.locator('.qmeta').inner_text()
  assert page.evaluate('NOMUSA_FIRST_2009.length')==125
  page.locator('#jumper summary').click()
  page.locator('#jumpN').fill('5')
  page.locator('#jumpGo').click()
  page.locator('#choices [data-v="4"]').click()
  assert page.locator('.fb.info').first.is_visible()
  page.locator('#tabs [data-v="home"]').click()
  assert page.get_by_text('2,279문항',exact=True).is_visible()
  page.locator('[data-y="2014"][data-s="경제학원론"]').click()
  page.locator('#mOk').click()
  assert '2014년 A형' in page.locator('.qmeta').inner_text()
  page.locator('#jumper summary').click()
  page.locator('#jumpN').fill('7')
  page.locator('#jumpGo').click()
  assert page.locator('.source-layout img').evaluate('img => img.complete && img.naturalWidth > 0')
  assert '5098606' in page.get_by_role('link',name='Q-Net 제23회 A형 원문').get_attribute('href')
  page.locator('#choices [data-v="5"]').click()
  assert page.locator('.fb.info').first.is_visible()
  assert page.locator('.fb.ok,.fb.bad').count()==0
  assert page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')<=1
  assert not errors,errors
  results.append({'name':name,'status':'PASS','questions':1020,'choicePersisted':True,
                  'backupRoundTrip':True,'examNavigationAndResume':True,'added2008Questions':125,'added2009Questions':125,'added2010Questions':125,'earlyExamBatch':884,'legacyHoldAndResume':True,'legacyExam':True,'overflow':overflow})
 except Exception:
  results.append({'name':name,'status':'HOLD','errors':errors,
                  'detail':traceback.format_exc(limit=2)[-1700:]})

def check_legacy_sources(page, width):
 name=f'legacy_first_{width}'
 errors=[]
 page.on('pageerror',lambda error:errors.append(str(error)))
 try:
  page.goto(base+'/study-hub/first-legacy-answers.html',wait_until='domcontentloaded')
  assert page.evaluate('Object.keys(NOMUSA_FIRST_V61_SOURCES.records).length')==900
  assert page.evaluate('NOMUSA_FIRST_LEGACY_V5.records.length')==3400
  page.locator('#year').select_option('2014')
  page.locator('#subject').select_option('경제학원론')
  page.locator('#number').fill('101')
  row=page.locator('#rows tr')
  assert row.count()==1
  assert 'fileSeq=2089750' in row.get_by_role('link',name='A형 경제 문제지',exact=False).get_attribute('href')
  assert 'fileSeq=2091154' in row.get_by_role('link',name='최종정답 PDF',exact=False).get_attribute('href')
  page.locator('#year').select_option('2021')
  page.locator('#type').select_option('B')
  page.locator('#subject').select_option('민법')
  page.locator('#number').fill('62')
  assert row.locator('.ans').inner_text()=='1'
  assert 'fileSeq=2200446' in row.get_by_role('link',name='최종정답 PDF',exact=False).get_attribute('href')
  assert '2쪽' in row.get_by_role('link',name='최종정답 PDF',exact=False).inner_text()
  overflow=page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
  assert overflow<=1,f'overflow={overflow}'
  assert not errors,errors
  results.append({'name':name,'status':'PASS','sourceRecords':900,'overflow':overflow})
 except Exception:
  results.append({'name':name,'status':'HOLD','errors':errors,
                  'detail':traceback.format_exc(limit=2)[-1700:]})


with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('NOMUSA_CHROMIUM'),headless=True,args=['--no-sandbox'])
 for width in (1440,390,360):
  for view in ('first','second','hub','legacy_first'):
   with browser.new_context(viewport={'width':width,'height':860}) as context:
    page=context.new_page()
    if view=='first':
     check_first(page,width)
    elif view=='legacy_first':
     check_legacy_sources(page,width)
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
out={'schema':'nomusa-auto-v6.8-browser-gate','status':'PASS' if all(x['status']=='PASS' for x in results) else 'HOLD','chromiumVersion':version,'results':results,'actualPreview':'NOT_DEPLOYED','production':'NOT_TOUCHED','legalApproval':'HOLD'}
print(json.dumps(out,ensure_ascii=False,indent=2));sys.exit(0 if out['status']=='PASS' else 1)
