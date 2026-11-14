#!/usr/bin/env python3
"""Chromium in-memory DOM/JS regression test: not HTTP/HTTPS E2E."""
import re, pathlib, json,sys
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else pathlib.Path('work_v1106_site').resolve()
TARGETS=['2024-민사소송법|2|0','2024-민사소송법|3|0','2026-노동법2|1|1','2026-노동법2|1|2','2026-노동법2|2|0','2026-노동법1|2|0']
NEG='2023-admin-1'
report=[]
def testout(n,ok,detail=''):
 report.append({'test':n,'status':'PASS' if ok else 'HOLD','detail':str(detail)[:480]});print(('PASS ' if ok else 'HOLD ')+n+' '+str(detail)[:160],flush=True)
def setup(page,which):
 p=ROOT/which/'index.html'
 original=p.read_text('utf8')
 scripts=re.findall(r'<script\s+src="([^"]+)"\s*></script>',original)
 original=re.sub(r'<script\s+src="[^"]+"\s*></script>','',original)
 styles=re.findall(r'<link\s+rel="stylesheet"\s+href="([^"]+)"\s*/?>',original)
 original=re.sub(r'<link\s+rel="stylesheet"\s+href="[^"]+"\s*/?>','',original)
 page.set_content(original,wait_until='domcontentloaded')
 # Substitute browser storage for the inaccessible origin. No real browser storage persistence is claimed.
 page.evaluate('''()=>{window.__mem = new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>window.__mem.has(k)?window.__mem.get(k):null,setItem:(k,v)=>window.__mem.set(k,''+v),removeItem:k=>window.__mem.delete(k),clear:()=>window.__mem.clear(),key:i=>Array.from(window.__mem.keys())[i]||null,get length(){return window.__mem.size}}});window.fetch=()=>Promise.resolve({ok:false,status:404,json:async()=>({})});}''')
 if which=='study-hub':page.evaluate('location.hash="#study"')
 for href in styles:
  target=(p.parent/href).resolve()
  assert target.is_file(),('missing-css',href)
  page.add_style_tag(content=target.read_text('utf8'))
 for src in scripts:
  target=(p.parent/src).resolve()
  assert target.is_file(),('missing-script',src)
  page.add_script_tag(content=target.read_text('utf8'))
 return {'scripts':len(scripts),'styles':len(styles)}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width in [1440,390,360]:
  for which in ['second','study-hub']:
   page=browser.new_page(viewport={'width':width,'height':860});page.set_default_timeout(4000)
   errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
   try:
    b=setup(page,which)
    page.wait_for_function('window.N1106_LAW_REVIEW_BRIDGE?.status === "REVIEW_ONLY_HOLD"',timeout=7000)
    if which=='second':
     page.wait_for_function('window.N27_ESSAY_TEST?.count>100',timeout=7000)
     for id in TARGETS:
      page.evaluate('(id)=>window.N27_ESSAY_TEST.select(id)',id)
      page.wait_for_selector(f'.n1106-review[data-n1106-question="{id}"]',timeout=7000)
      assert page.locator('.n1106-review details').count()==3
     page.evaluate('(id)=>window.N27_ESSAY_TEST.select(id)',NEG)
     assert page.locator('.n1106-review').count()==0
     page.evaluate('(id)=>window.N27_ESSAY_TEST.select(id)',TARGETS[0])
     page.locator('#n27-timer').click()
     page.wait_for_function('!window.N1106_LAW_REVIEW_BRIDGE.displayed',timeout=2500)
     page.once('dialog',lambda d:d.accept())
     page.locator('#n27-timer').click()
     page.wait_for_selector('.n1106-review',timeout=2500)
     page.locator('[data-pane="write"]').first.evaluate('(el)=>el.click()')
     page.locator('#n27-draft').evaluate('(el,v)=>{el.value=v;el.dispatchEvent(new Event("input",{bubbles:true}));}', 'V1106 smoke '+str(width))
     assert 'V1106 smoke '+str(width) in page.locator('#n27-draft').input_value()
     assert page.evaluate('window.__mem.size')>=1
    else:
     page.wait_for_selector('.study-toolbar',timeout=7000)
     page.locator('[data-stage="essay"]').click()
     for id in [TARGETS[0],TARGETS[-1]]:
      page.locator('#search').evaluate('(el,v)=>{el.value=v;el.dispatchEvent(new Event("input",{bubbles:true}));}', id)
      page.locator(f'[data-question="{id}"]').evaluate('(el)=>el.click()')
      page.wait_for_selector(f'.n1106-review[data-n1106-question="{id}"]',timeout=7000)
      assert page.locator('.n1106-review details').count()==3
     page.locator('#search').evaluate('(el,v)=>{el.value=v;el.dispatchEvent(new Event("input",{bubbles:true}));}', NEG)
     page.locator(f'[data-question="{NEG}"]').evaluate('(el)=>el.click()')
     assert page.locator('.n1106-review').count()==0
     page.locator('#search').evaluate('(el,v)=>{el.value=v;el.dispatchEvent(new Event("input",{bubbles:true}));}', TARGETS[0])
     page.locator(f'[data-question="{TARGETS[0]}"]').evaluate('(el)=>el.click()')
     page.locator('[data-action="exam"]').first.evaluate('(el)=>el.click()')
     page.locator('[data-action="exam-start"]').evaluate('(el)=>el.click()')
     page.wait_for_function('!window.N1106_LAW_REVIEW_BRIDGE.displayed',timeout=2500)
    if page.locator('.n1106-review').count()>0:assert '최종 내용승인 0/47 HOLD' in page.locator('.n1106-review').inner_text()
    overflow=page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
    assert overflow<=2,('overflow',overflow)
    assert not errs,('pageerrors',errs[:3])
    testout(which+'_'+str(width),True,f'JScount={b["scripts"]}; overflow={overflow}; errors={len(errs)}')
   except Exception as e:
    testout(which+'_'+str(width),False,f'{type(e).__name__}: {str(e)[:380]}; JS={errs[:1]}')
   finally:page.close()
 browser.close()
summary={'schema':'nomusa-v1106-inmemory-browser-dom-regression/1','mode':'CHROMIUM_MEMORY_ONLY_NOT_HTTP','checks':report,'passed':sum(r['status']=='PASS' for r in report),'held':sum(r['status']=='HOLD' for r in report),'webStorageTest':'SHIM_ONLY','localHttp':'HOLD_BLOCKED_BY_ADMINISTRATOR','httpsPreview':'NOT_RUN','contentApproval':'0/47 HOLD'}
path=pathlib.Path('/mnt/data/V1106_DOM_GATE.json');path.write_text(json.dumps(summary,ensure_ascii=False,indent=2),'utf8');print(json.dumps(summary,ensure_ascii=False))
sys.exit(0 if summary['held']==0 else 1)
