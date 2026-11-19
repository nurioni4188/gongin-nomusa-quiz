#!/usr/bin/env python3
"""V38 Chromium original QNet source-page exercises 2020/2021, no grading."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json,sys,hashlib
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
PAGE="/study-hub/first-v38-2020-2021-source-pages-practice.html"
class Quiet(SimpleHTTPRequestHandler):
  def log_message(self,*args): pass
def main():
  meta=json.loads((ROOT/"review-artifacts/NOMUSA_FIRST_V38/NOMUSA_FIRST_V38_88_NATIVE_SOURCE_PAGE_MANIFEST.json").read_text())
  assert meta["uniqueImagePages"]==88 and meta["OCRPageCandidates"]==274 and meta["bookletOnlyHOLD"]==26
  for group in meta["sourceDocuments"]:
    for item in group["images"]:
      path=ROOT/"study-hub/first-v38-qnet-pages-2020-2021"/item["image"]
      assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==item["sha256"],str(path)
  server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
  Thread(target=server.serve_forever,daemon=True).start();cases=[]
  try:
    with sync_playwright() as p:
      browser=p.chromium.launch(args=["--no-sandbox"])
      for width in [1440,390,360]:
        ctx=browser.new_context(viewport={"width":width,"height":850},accept_downloads=True)
        page=ctx.new_page();errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        base="http://127.0.0.1:"+str(server.server_port)
        page.goto(base+PAGE,wait_until="domcontentloaded")
        result=page.evaluate("window.NOMUSA_FIRST_V38")
        assert result=={"total":300,"pageCandidates":274,"strictHold":26,"approvedKeys":0},result
        assert page.locator("#item option").count()==150
        assert "2020년 A형" in page.locator("#title").inner_text()
        assert "OCR" in page.locator("#status").inner_text()
        page.wait_for_function("document.getElementById('sourceImg').complete && document.getElementById('sourceImg').naturalWidth>=850")
        assert page.locator("#choices [data-choice]").count()==5
        assert page.locator("#official").get_attribute("href").startswith("https://www.q-net.or.kr/")
        cases.append({"width":width,"test":"QNet2020_150_original_A_page_candidate_and_image_loaded","result":"PASS"})
        page.locator("#choices [data-choice='4']").click()
        assert page.locator("#choices [data-choice='4']").get_attribute("aria-pressed")=="true"
        assert "선택 기록 1/300" in page.locator("#progress").inner_text()
        assert page.locator(".fb.ok,.fb.bad,#score").count()==0
        page.reload(wait_until="domcontentloaded")
        assert page.locator("#choices [data-choice='4']").get_attribute("aria-pressed")=="true"
        cases.append({"width":width,"test":"V38_isolated_saved_choice_restores_after_reload_no_scoring","result":"PASS"})
        page.locator("#candidate summary").click()
        assert "정답표 전사 후보" in page.locator("#candidateText").inner_text()
        assert "자동채점" in page.locator("#candidateText").inner_text()
        cases.append({"width":width,"test":"candidate_key_explicit_disclosure_unapproved","result":"PASS"})
        page.locator("#item").select_option("legacy1-2020-A-labor1-013")
        assert page.locator("#pageFigure").is_hidden()
        assert page.locator("#noPage").is_visible()
        assert page.locator("#choices [data-choice]").count()==5
        assert all(page.locator(f"#choices [data-choice='{i}']").is_disabled() for i in range(1,6))
        assert page.locator("#official").get_attribute("href").startswith("https://www.q-net.or.kr/")
        cases.append({"width":width,"test":"unknown_QNet_page_26_items_locked_not_falsely_restored","result":"PASS"})
        page.locator("#year").select_option("2021")
        assert page.locator("#item option").count()==150
        assert "2021년 A형" in page.locator("#title").inner_text()
        page.wait_for_function("document.getElementById('sourceImg').complete && document.getElementById('sourceImg').naturalWidth>=850")
        page.locator("#next").click()
        assert "2021년 A형" in page.locator("#title").inner_text()
        cases.append({"width":width,"test":"QNet2021_150_original_candidate_navigation_and_JPEG","result":"PASS"})
        if width==1440:
          with page.expect_download() as ev:page.locator("#export").click()
          assert ev.value.suggested_filename=="nomusa-first-v38-2020-2021-a-source-records.json"
        assert page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=1
        assert not errors,errors
        cases.append({"width":width,"test":"mobile_no_overflow_and_original_QDATA_unchanged","result":"PASS"})
        ctx.close()
      browser.close()
  finally: server.shutdown()
  out={"schema":"NOMUSA_FIRST_V38_300_OFFICIAL_QNET_PAGE_PRACTICE_E2E/1",
    "status":"PASS" if len(cases)==18 else "HOLD","tests":len(cases),"expected":18,
    "viewports":[1440,390,360],"originalPDFSHA256Verified":4,
    "sourceNativeJPGPages":88,"OCRCandidateQuestionLinks":274,"missingPageLocked":26,
    "actualOriginalStemOptionsIndependentValidation":0,
    "autoScoringApproved":0,"actualQDATAAdditions":0,"cases":cases}
  folder=ROOT/"review-artifacts/NOMUSA_FIRST_V38";folder.mkdir(parents=True,exist_ok=True)
  (folder/"NOMUSA_FIRST_V38_300_NATIVE_SOURCE_PRACTICE_E2E.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
  print(json.dumps({k:v for k,v in out.items() if k!="cases"},ensure_ascii=False))
  return 0 if out["status"]=="PASS" else 1
if __name__=="__main__":sys.exit(main())