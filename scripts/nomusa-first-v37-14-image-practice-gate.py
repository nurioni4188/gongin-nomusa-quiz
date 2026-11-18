#!/usr/bin/env python3
"""NOMUSA V37 original-QNet JPEG 14-item choice-practice.
Checks mobile image, candidate-key disclosure, isolated progress storage, no grading.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from pathlib import Path
import json,sys
from playwright.sync_api import sync_playwright
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
PAGE="/study-hub/first-v37-native14-practice.html"
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def main():
    source=json.loads((ROOT/"review/NOMUSA_FIRST_V35_14_NATIVE_QNET_SOURCE_PROOF_20261118.json").read_text())
    assert source["originalCrops"]==14 and source["actualQDATAImported"]==0
    srv=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
    Thread(target=srv.serve_forever,daemon=True).start()
    tests=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(args=["--no-sandbox"],headless=True)
            for width in (1440,390,360):
                ctx=browser.new_context(viewport={"width":width,"height":840},locale="ko-KR",accept_downloads=True)
                page=ctx.new_page();errors=[]
                page.on("pageerror",lambda e:errors.append(str(e)))
                origin=f"http://127.0.0.1:{srv.server_port}"
                page.goto(origin+PAGE,wait_until="domcontentloaded")
                assert page.locator("#item option").count()==14
                assert "2017년 A형" in page.locator("#questionTitle").inner_text()
                assert "채점" in page.locator(".notice").inner_text()
                assert page.locator("#choices [data-choice]").count()==5
                page.wait_for_function("document.getElementById('sourceImg').complete && document.getElementById('sourceImg').naturalWidth>=600")
                assert page.locator("#sourceImg").get_attribute("src").endswith("legacy1-2017-A-civil-052.jpg")
                assert page.locator("#official").get_attribute("href").startswith("https://www.q-net.or.kr/")
                tests.append({"width":width,"case":"exact_14_QNet_crop_source_and_5_selectable_choices","status":"PASS"})
                page.locator("#choices [data-choice='2']").click()
                assert "선택기록 1 / 14" in page.locator("#progress").inner_text()
                assert page.locator("#choices [data-choice='2']").get_attribute("aria-pressed")=="true"
                assert page.locator(".fb.ok,.fb.bad,#score,[data-scoring-approved]").count()==0
                page.reload(wait_until="domcontentloaded")
                assert page.locator("#choices [data-choice='2']").get_attribute("aria-pressed")=="true"
                assert "선택기록 1 / 14" in page.locator("#progress").inner_text()
                tests.append({"width":width,"case":"isolated_local_storage_refresh_restores_ungraded_choice","status":"PASS"})
                page.locator("#flag").click()
                assert "복습 1" in page.locator("#progress").inner_text()
                page.locator("#candidate summary").click()
                assert "전사 후보" in page.locator("#candidateText").inner_text()
                assert page.locator("#candidateText").inner_text().find("자동채점하지 않습니다")>=0
                assert page.locator(".fb.ok,.fb.bad,#score").count()==0
                tests.append({"width":width,"case":"explicit_candidate_reveal_not_auto_scoring","status":"PASS"})
                page.locator("#year").select_option("2019")
                assert page.locator("#item option").count()==8
                assert "2019년 A형" in page.locator("#questionTitle").inner_text()
                page.locator("#next").click()
                assert "2019년 A형" in page.locator("#questionTitle").inner_text()
                assert page.locator("#item").input_value().startswith("legacy1-2019")
                tests.append({"width":width,"case":"2019_eight_items_source_image_navigation","status":"PASS"})
                assert page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=1
                assert not errors,errors
                if width==1440:
                    with page.expect_download() as outcome:
                        page.locator("#export").click()
                    assert outcome.value.suggested_filename=="nomusa-first-v37-14-review-progress.json"
                tests.append({"width":width,"case":"mobile_overflow_free_progress_export_no_JS_error","status":"PASS"})
                ctx.close()
            browser.close()
    finally:
        srv.shutdown()
    result={"schema":"NOMUSA_FIRST_V37_UNGRADED_SOURCE_IMAGE_14_E2E/1",
            "status":"PASS" if len(tests)==15 else "HOLD","tests":len(tests),"expected":15,
            "originalQNetImageItems":14,"originalImageRecords":source["originalCrops"],
            "newMainQDATA":0,"independentExpertApproval":0,
            "candidateKeysAutoGraded":0,"isolatedLocalStorageKey":"nomusa1-v37-native14-choice-review-v1",
            "viewports":[1440,390,360],"cases":tests}
    dst=ROOT/"review-artifacts/NOMUSA_FIRST_V37";dst.mkdir(parents=True,exist_ok=True)
    (dst/"NOMUSA_FIRST_V37_14_UNGRADED_E2E.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="cases"},ensure_ascii=False))
    return 0 if result["status"]=="PASS" else 1
if __name__=="__main__":sys.exit(main())