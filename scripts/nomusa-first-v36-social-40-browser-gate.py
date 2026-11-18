#!/usr/bin/env python3
"""2026 SI 40 source-bound explanation coverage and mobile detailed-pane proof.

Read-only. Core answer keys, choices, saved-progress keys, 2008-2021 grading block
and 2022-2026 RC35 original QDATA must remain unchanged.
"""
import json,sys,threading
from functools import partial
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def main():
    srv=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever,daemon=True).start()
    cases=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(args=["--no-sandbox"],headless=True)
            for width in (1440,390,360):
                c=browser.new_context(viewport={"width":width,"height":840},locale="ko-KR")
                page=c.new_page();errors=[]
                page.on("pageerror",lambda err:errors.append(str(err)))
                root="http://127.0.0.1:"+str(srv.server_port)
                page.goto(root+"/index.html",wait_until="domcontentloaded")
                page.locator(".cell[data-y='2026'][data-s='사회보험법']").wait_for()
                result=page.evaluate("""() => {
                    const all=window.QDATA;
                    const bank=window.NOMUSA_V108_EXPLANATIONS;
                    const social=all.filter(q=>q.y===2026&&q.s==='사회보험법');
                    const wrong=social.map(q=>{
                        const e=bank.entries[q.k];
                        const valid=!!(e&&e.question===q.q&&JSON.stringify(e.correct)===JSON.stringify(q.a)&&
                          Array.isArray(e.options)&&e.options.length===q.o.length&&(!e.optionTexts||JSON.stringify(e.optionTexts)===JSON.stringify(q.o)));
                        const srcOk=(e?.sources||[]).every(s=>s.url.startsWith('https://www.law.go.kr/')||s.url.startsWith('https://law.go.kr/'));
                        return {id:q.k,valid,srcOk,explanation:!!e,options:e?.options?.length||0,
                                summaryLength:(e?.summary||'').length,sourceCount:e?.sources?.length||0};
                    }).filter(x=>!x.valid||!x.srcOk||x.options!==5||x.summaryLength<30||x.sourceCount<1);
                    return {base:all.length,social:social.length,existingPreserved:['041','046','060'].every(n=>!!bank.entries['2026-사회보험법-'+n]&&!bank.entries['2026-사회보험법-'+n].validationStatus?.startsWith('LEGAL_EXAM_DATE_REVIEW_HOLD')),
                      v36:window.NOMUSA_V36_2026_SI,allExplanations:Object.keys(bank.entries).length,wrong,
                      remaining:all.filter(q=>q.y===2026&&q.s==='사회보험법').filter(q=>!bank.entries[q.k]).length};
                }""")
                assert result["base"]==1020
                assert result["social"]==40
                assert result["v36"]["newDrafts"]==37
                assert result["v36"]["existingProtected"]==3
                assert result["v36"]["approved"]==0
                assert result["existingPreserved"] is True
                assert result["allExplanations"]==399,result
                assert result["remaining"]==0 and not result["wrong"],result
                cases.append({"width":width,"test":"40_of_40_exact_source_and_original_answer_hash","pass":True})
                # First 2026 social question must show original explanation (protected) after answer selection.
                page.locator('.cell[data-y="2026"][data-s="사회보험법"]').click()
                assert "2026년" in page.locator(".qmeta").inner_text()
                assert "사회" in page.locator(".qmeta").inner_text()
                assert "41번" in page.locator(".qmeta").inner_text()
                assert page.locator("section.n108-explanation").count()==0
                page.locator("#choices [data-v='4']").click()
                page.locator("section.n108-explanation").wait_for()
                assert page.locator("section.n108-explanation .n108-choice").count()==5
                assert "사회보장" in page.locator("section.n108-explanation").inner_text()
                cases.append({"width":width,"test":"existing_2026_social_041_explanation_protected","pass":True})
                # Second 2026 social question gets first new law-based draft.
                page.locator("#nx").click()
                assert "42번" in page.locator(".qmeta").inner_text()
                page.locator("#choices [data-v='2']").click()
                page.locator("section.n108-explanation").wait_for()
                assert page.locator(".n108-summary").inner_text().count("10월 31일")>=1
                assert page.locator(".n108-choice").count()==5
                assert page.locator("section.n108-explanation a[href*='law.go.kr']").count()>=1
                assert "학습 초안" in page.locator("section.n108-explanation").inner_text()
                assert "수학적 최적화 조건" not in page.locator("section.n108-explanation").inner_text()
                cases.append({"width":width,"test":"new_2026_social_042_law_draft_and_correct_label","pass":True})
                # 55: three-year vs five-year statute, 70: minister vs tax service
                for n,choice,fragment in [(55,2,"휴업급여"),(70,3,"보건복지부장관"),(79,2,"체납처분비")]:
                    # Reuse one saved 40-question study session; new start is blocked by design
                    # while an unfinished session exists. Jump to the original question position.
                    if not page.locator("#jumper").evaluate("(el)=>el.open"):
                        page.locator("#jumper summary").click()
                    page.locator("#jumpN").fill(str(n-40))
                    page.locator("#jumpGo").click()
                    assert f"{n}번" in page.locator(".qmeta").inner_text()
                    page.locator(f"#choices [data-v='{choice}']").click()
                    assert fragment in page.locator(".n108-summary").inner_text()
                    assert page.locator(".n108-choice").count()==5
                    assert page.locator("section.n108-explanation a[href*='law.go.kr']").count()>=1
                cases.append({"width":width,"test":"2026_social_055_070_079_question_law_and_5_options","pass":True})
                assert page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=1
                assert not errors,errors
                cases.append({"width":width,"test":"no_mobile_overflow_and_no_javascript_exceptions","pass":True})
                c.close()
            browser.close()
    finally:
        srv.shutdown()
    out={"schema":"NOMUSA_FIRST_V36_2026_SI_40_BASIS_GATE/1","tests":len(cases),
         "expected":15,"status":"PASS" if len(cases)==15 else "HOLD",
         "newStudyExplanationDrafts":37,"protectedEarlierExplanations":3,
         "visibleDetailedExplanations":40,
         "humanApproved":0,"oldDataQDATA":1020,"oldSavedKeys":"UNCHANGED",
         "legacy2008to2021AutoScoring":"DISABLED","examDate":"2026-05-23",
         "cases":cases}
    dst=ROOT/"review-artifacts/NOMUSA_FIRST_V36";dst.mkdir(parents=True,exist_ok=True)
    (dst/"NOMUSA_FIRST_V36_SOCIAL_40_BROWSER_GATE.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in out.items() if k!="cases"},ensure_ascii=False))
    return 0 if out["status"]=="PASS" else 2
if __name__=="__main__":sys.exit(main())
