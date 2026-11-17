#!/usr/bin/env python3
"""NOMUSA FIRST V32 — reuse prior Q-Net evidence, UI/no-scoring browser gate.

Does not infer professional or independent-human approval from OCR, image matching,
source URL, visual PDF page navigation, or successful browser tests.
"""
import json
import sys
import threading
from collections import Counter
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def check_source_evidence():
    v61 = json.loads((ROOT/"review/NOMUSA_FIRST_V61_ANSWER_AUDIT_20261115.json").read_text())
    v71 = json.loads((ROOT/"review/NOMUSA_FIRST_V71_OFFICIAL_QNET_14PAGE_600CELL_FINAL_GATE_20261115.json").read_text())
    v62 = json.loads((ROOT/"review/NOMUSA_FIRST_V62_SCAN_RECHECK_20261115.json").read_text())
    v70 = json.loads((ROOT/"review/NOMUSA_FIRST_V70_QNET_44_PAGE_OCR_AND_ANSWERS_20261115.json").read_text())
    assert v61["records"] == v61["pendingApproval"] == 3400
    assert v61["uniqueIds"] == 3400
    assert v61["sourceLinks"]["records"] == 900
    assert v61["sourceLinks"]["counts"] == {
        "TEXT_AND_FIVE_MARKERS":300,
        "OCR_PAGE_CANDIDATE":556,
        "BOOKLET_LINKED_PAGE_HOLD":44,
    }
    assert v71["visualQuestionPages"]["officialQNetPdfPageLocationVisuallyConfirmed"] == 14
    assert v71["visualQuestionPages"]["printPageNumberVerified"] == 0
    assert v71["answerTableCells"]["segmentedOfficialPdfCells"] == 600
    assert v71["answerTableCells"]["visuallyInspectedSpecialCells"] == 4
    assert v71["answerTableCells"]["perQuestionScoringApproved"] == 0
    assert len(v62["bookletRecheck"]["newVisualPages"]) == 3
    assert v70["hold44"]["targets"] == 44
    assert v70["answerTable"]["totalIndependentApprovedAnswerKeys"] == 0
    return {"candidateAnswerRecords":3400, "QNetDocumentLinked":900,
            "pdfTextMarkers":300,"ocrPageCandidates":556,"bookletPageHold":44,
            "QNetGridImageCompared":600,"specialGridCellsVisuallyCompared":4,
            "visualQuestionPageV71":14,"visualQuestionPageV62":3,
            "independentScoringApproved":0}


def main():
    base = check_source_evidence()
    server = ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    tests=[]
    try:
        with sync_playwright() as tool:
            browser=tool.chromium.launch(headless=True,args=["--no-sandbox"])
            for width in (1440,390,360):
                context=browser.new_context(viewport={"width":width,"height":840})
                page=context.new_page()
                errors=[]
                page.on("pageerror",lambda error:errors.append(str(error)))
                root=f"http://127.0.0.1:{server.server_port}"
                page.goto(root+"/study-hub/first-legacy-answers.html",wait_until="domcontentloaded")
                page.wait_for_function("!!window.NOMUSA_FIRST_V32_STATUS && document.querySelectorAll('#rows tr').length > 0")
                counts=page.evaluate("""() => {
                    const a=window.NOMUSA_FIRST_V32_STATUS;
                    const sources=window.NOMUSA_FIRST_V61_SOURCES.records;
                    const ids=Object.keys(sources);
                    const stages=ids.map(id=>a.classify(id));
                    const c=(field,value)=>stages.filter(v=>v[field]===value).length;
                    return {total:ids.length,
                        originalText:c('sourceKind','PDF_TEXT_FIVE_MARKERS'),
                        originalOCR:c('sourceKind','PDF_OCR_CANDIDATE'),
                        confirmedV62:c('sourceKind','PDF_PAGE_VISUAL_V62'),
                        confirmedV71:c('sourceKind','PDF_PAGE_VISUAL_V71'),
                        year2020to2021Matched:ids.filter(id=>/legacy1-(2020|2021)-/.test(id)).filter(id=>a.classify(id).answerKind.includes('GRID_')).length,
                        unapproved:stages.filter(v=>!v.scoringApproved&&!v.fullAnswerKeyHumanApproved).length,
                        imageSpecial:c('answerKind','GRID_2021_SPECIAL_VISUALLY_CHECKED'),
                        fullQuestionVisual:stages.filter(v=>v.exactQuestionVisuallyProofread).length,
                        noteCount:document.querySelectorAll('p.notice').length,
                        rulesCount:document.querySelectorAll('.evidence-key').length};
                }""")
                assert counts["total"]==900,counts
                assert counts["confirmedV62"]==3 and counts["confirmedV71"]==14,counts
                assert counts["year2020to2021Matched"]==600,counts
                assert counts["unapproved"]==900 and counts["fullQuestionVisual"]==0,counts
                assert counts["imageSpecial"]==4,counts
                assert counts["noteCount"]==counts["rulesCount"]==1,counts
                assert counts["originalText"]+counts["originalOCR"]+counts["confirmedV62"]+counts["confirmedV71"] <= 900
                tests.append({"viewport":width,"test":"900-index-and-stage-counts","status":"PASS","counts":counts})
                # Unique V71 page, no automatic scoring despite primary-source page reference
                page.locator("#year").select_option("2020")
                page.locator("#type").select_option("A")
                page.locator("#subject").select_option("민법")
                page.locator("#number").fill("72")
                row=page.locator("#rows tr")
                assert row.count()==1
                rowtext=row.inner_text()
                assert "PDF 24쪽" in rowtext and "인쇄 쪽수·전체 지문 검증 HOLD" in rowtext
                assert "PDF 문항번호 시각확인" in rowtext and "정답표 이미지 자동대조" in rowtext
                assert row.locator("a").count()==2
                assert not row.locator("td").last.inner_text().count("정답 승인 HOLD")
                tests.append({"viewport":width,"test":"2020-72-confirmed-page-not-scoring","status":"PASS"})
                # 2021 special multi/all-credit cells manually image checked but still not scoring approved
                page.locator("#year").select_option("2021")
                page.locator("#type").select_option("B")
                page.locator("#subject").select_option("노동법Ⅱ")
                page.locator("#number").fill("26")
                row=page.locator("#rows tr")
                assert row.count()==1
                assert "정답표 특수셀 시각대조" in row.inner_text()
                assert row.locator("td").count()==7
                tests.append({"viewport":width,"test":"2021-special-grid-unapproved","status":"PASS"})
                # 2014 source PDF text layer is linked, not legally or human confirmed answers
                page.locator("#year").select_option("2014")
                page.locator("#type").select_option("A")
                page.locator("#subject").select_option("노동법Ⅰ")
                page.locator("#number").fill("1")
                row=page.locator("#rows tr")
                assert row.count()==1
                assert "PDF 텍스트 위치 연결" in row.inner_text()
                assert "정답 PDF 연결·추가검증" in row.inner_text()
                tests.append({"viewport":width,"test":"2014-original-layer-candidate","status":"PASS"})
                # Mobile cards prevent horizontal scroll; source links and form values intact.
                assert not errors, errors
                overflow=page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
                assert overflow<=1,(width,overflow)
                if width<=390: assert row.evaluate("e=>getComputedStyle(e).display")=="block"
                tests.append({"viewport":width,"test":"mobile-card-no-horizontal-overflow","status":"PASS"})
                context.close()

            # Cross-screen regression: 2008 cannot be scored, and one feedback at a time.
            context=browser.new_context(viewport={"width":390,"height":844})
            page=context.new_page()
            errors=[]
            page.on("pageerror",lambda error:errors.append(str(error)))
            page.goto(root+"/index.html",wait_until="domcontentloaded")
            page.wait_for_selector("#cYear")
            assert page.evaluate("window.QDATA.length")==1020
            assert page.locator("a[href='study-hub/first-legacy-answers.html']").count()>=1
            page.get_by_role("button",name="2008 · 17회 A형",exact=True).click()
            page.get_by_role("button",name="연습 · 바로 채점",exact=True).click()
            pre=page.locator(".fb.info").all_inner_texts()
            assert len(pre)==1, json.dumps({"pre":pre,"qmeta":page.locator(".qmeta").all_inner_texts(),
                  "before":page.locator("#app").inner_text()[:550]},ensure_ascii=False)
            page.locator("#choices [data-v='1']").click()
            post=page.locator(".fb.info").all_inner_texts()
            assert len(post)==1, json.dumps({"post":post,"qmeta":page.locator(".qmeta").all_inner_texts(),
                  "after":page.locator("#app").inner_text()[:650]},ensure_ascii=False)
            assert page.locator(".fb.ok,.fb.bad").count()==0
            assert page.locator("section.n108-explanation").count()==0
            assert page.locator("#app").inner_text().count("정답 근거 독립 검토 HOLD")==1
            assert page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=1
            assert not errors, errors
            tests.append({"viewport":390,"test":"one-hold-message-ungraded-answer-and-no-scoring","status":"PASS"})
            page.goto(root+"/study-hub/index.html",wait_until="domcontentloaded")
            page.wait_for_selector(".year-grid")
            assert page.locator("a[href='first-legacy-answers.html']").count()==1
            assert page.locator("body > div[role='note']").count()==0
            tests.append({"viewport":390,"test":"hub-removes-duplicate-banner-with-one-entry-link","status":"PASS"})
            context.close()
            browser.close()
    finally:
        server.shutdown()
    result={"schema":"NOMUSA_FIRST_V32_STATUS_UI_GATE/1",
            "status":"PASS_UI_NO_SCORING_PROMOTION" if len(tests)==14 else "HOLD_CHECK_COUNT",
            "expected":14,"passed":len(tests),"tests":tests,"evidence":base,
            "noAnswerKeyMutation":True,
            "noOriginalQuestionIdOrStorageKeyChange":True,
            "legacyScoring":"DISABLED","existing2022to2026Scoring":"UNMODIFIED",
            "expertApproval":"HOLD_0_OF_3400","release":"PREVIEW_ONLY"}
    out=ROOT/"review-artifacts/NOMUSA_FIRST_V32"
    out.mkdir(parents=True,exist_ok=True)
    (out/"NOMUSA_FIRST_V32_UI_SOURCE_STATUS_GATE.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="tests"},ensure_ascii=False))
    return 0 if result["status"]=="PASS_UI_NO_SCORING_PROMOTION" else 1


if __name__=="__main__":
    sys.exit(main())