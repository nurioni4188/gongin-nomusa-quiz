#!/usr/bin/env python3
"""V33 local Chromium evidence-only navigation test for missing first-stage years.
No source guesses, IDs added, auto-scoring, storage changes, or deployment.
"""
import json
import sys
import threading
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]).resolve()
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def test():
    srv=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever,daemon=True).start()
    result=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
            base="http://127.0.0.1:"+str(srv.server_port)
            missing=[2013,2016,2018,2020,2021]
            for width in [1440,390,360]:
                ctx=browser.new_context(viewport={"width":width,"height":860})
                page=ctx.new_page();errors=[]
                page.on("pageerror",lambda err:errors.append(str(err)))
                page.goto(base+"/index.html",wait_until="domcontentloaded")
                page.locator("#cYear").wait_for()
                assert page.evaluate("window.QDATA.length")==1020
                assert page.evaluate("window.NOMUSA_FIRST_V33_COVERAGE.missingYears.length")==5
                assert page.locator("#cYear a").count()==0
                for year in missing:
                    link=f"study-hub/first-legacy-answers.html?year={year}&type=A"
                    assert page.locator(f'a[href="{link}"]').count()==1,("missing-home-link",width,year)
                assert page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=1
                result.append({"width":width,"name":"home-five-year-navigation","status":"PASS"})
                # All five missing years are existing read-only answer candidates only.
                for year in missing:
                    page.goto(base+f"/study-hub/first-legacy-answers.html?year={year}&type=A",wait_until="domcontentloaded")
                    page.locator("#rows tr").first.wait_for()
                    assert page.locator("#year").input_value()==str(year)
                    assert page.locator("#type").input_value()=="A"
                    assert page.locator("#rows tr").count()==150,("year-count",year,page.locator("#rows tr").count())
                    assert "원문 문제풀이 미편입" in page.locator("#state").inner_text()
                    assert "자동채점 불가" in page.locator("#state").inner_text()
                    if year in [2020,2021]:
                        assert page.locator("#rows tr").first.locator("a").count()==2
                        assert "Q-Net" in page.locator(".notice").inner_text()
                        pdfurl=page.locator("#rows tr").first.locator("a").first.get_attribute("href")
                        assert pdfurl.startswith("https://www.q-net.or.kr/"),pdfurl
                    elif year==2018:
                        assert page.locator("#rows tr").first.locator("a").count()==1
                        assert "artlSeq=5203291" in page.locator("#rows tr").first.locator("a").get_attribute("href")
                    else:
                        assert page.locator("#rows tr").first.locator("a").count()==0
                    if year==2016:
                        page.locator("#subject").select_option("경제학원론")
                        assert page.locator("#rows tr").count()==25
                        assert "artlSeq=5183001" in page.locator("#rows tr").first.locator("a").get_attribute("href")
                        page.locator("#subject").select_option("")
                    assert page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=1
                    result.append({"width":width,"name":f"read-only-existing-{year}-A-150","status":"PASS"})
                page.goto(base+"/study-hub/first-legacy-answers.html?year=2021&type=B",wait_until="domcontentloaded")
                assert page.locator("#year").input_value()=="2021"
                assert page.locator("#type").input_value()=="B"
                assert page.locator("#rows tr").count()==150
                assert "원문 문제풀이 미편입" in page.locator("#state").inner_text()
                result.append({"width":width,"name":"B-form-year-deep-link-150","status":"PASS"})
                page.goto(base+"/study-hub/index.html#home",wait_until="domcontentloaded")
                page.locator(".year-grid").first.wait_for()
                for year in missing:
                    assert page.locator(f'a[href="first-legacy-answers.html?year={year}&type=A"]').count()==1
                assert "2,279문항" in page.locator("#main").inner_text()
                assert page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=1
                result.append({"width":width,"name":"unified-hub-links-all-five-missing","status":"PASS"})
                assert "2010년" not in page.locator("a[href='first-legacy-answers.html?year=2010&type=A']").all_inner_texts()
                assert page.locator(".year-grid").count()>=2
                result.append({"width":width,"name":"partial-years-remain-not-falsely-complete","status":"PASS"})
                assert not errors,errors
                ctx.close()
            browser.close()
    finally:
        srv.shutdown()
    expected=27
    status="PASS" if len(result)==expected and all(x["status"]=="PASS" for x in result) else "HOLD"
    outcome={"schema":"NOMUSA_FIRST_V33_MISSING_YEAR_COVERAGE_BROWSER/1",
      "status":status,"tests":len(result),"expected":expected,
      "viewports":[1440,390,360],"cases":result,
      "originalScoringUnchanged":True,"unapprovedScoringDisabled":True,
      "sourceOnlyCandidatesNotPromoted":1500,"actualNewRenderedQuestions":0}
    out=ROOT/"review-artifacts/NOMUSA_FIRST_V33"
    out.mkdir(parents=True,exist_ok=True)
    (out/"NOMUSA_FIRST_V33_27_BROWSER_YEAR_NAVIGATION.json").write_text(
       json.dumps(outcome,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in outcome.items() if k!="cases"},ensure_ascii=False))
    return 0 if status=="PASS" else 2

if __name__=="__main__":
    sys.exit(test())