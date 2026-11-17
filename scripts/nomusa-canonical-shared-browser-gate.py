#!/usr/bin/env python3
"""Non-deploying Chromium gate for unified 2007–2026 second-stage drafts.

Run against an existing local full review-branch checkout:
python scripts/nomusa-canonical-shared-browser-gate.py [repository_root]

Never changes GitHub, Vercel, main, Production, or old saved user records.
All storage tests use disposable browser contexts.
"""
from __future__ import annotations
import json, sys, threading, traceback
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
REQUIRED = [
    "second/index.html", "study-hub/index.html", "study-hub/app.js",
    "second/essay-app.js", "second/nomusa-canonical-selection-v1.js",
    "rc27_essay_catalog.js"
]
missing = [x for x in REQUIRED if not (ROOT / x).is_file()]
if missing:
    print(json.dumps({"status":"HOLD_FULL_SOURCE","missing":missing},ensure_ascii=False))
    sys.exit(2)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print(json.dumps({"status":"HOLD_PLAYWRIGHT_MISSING"},ensure_ascii=False))
    sys.exit(2)

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

srv = ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT)))
threading.Thread(target=srv.serve_forever,daemon=True).start()
BASE = "http://127.0.0.1:%d" % srv.server_port
RESULTS = []
IDENTIFIERS = [
    "legacy2-2007-hrm-q1", "legacy2-2008-hrm-q2",
    "2013_p1_q1", "2014_p4_q1", "2017_p3_q1",
    "2022-org-2", "2024-인사노무관리론|1|1", "2025-org-1",
    "2026-경영조직론|1|1", "2026-경영조직론|1|2",
    "legacy2-2007-administrative-q1", "2022-econ-2", "2023-labor2-2",
    "2025-civil-3", "2026-노동경제학|3|2",
]
KEY = "nomusa_rc27_v103_essay_records_v1"

def capture(page):
    errors = []
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.on("response",lambda resp: errors.append("HTTP_%d: %s" % (resp.status,resp.url))
            if resp.status >= 400 and resp.url.endswith((".js",".css")) else None)
    return errors

def inventory(page):
    return page.evaluate("""() => {
      const c=window.NOMUSA_CANONICAL_SELECTION_V1, rows=window.N27_CATALOG?.items||[];
      return {status:c?.status,gate:c?.gate,
         batch:(()=>{const q=window.NOMUSA_20YEAR_QUALITY_BATCH_V1;return q&&{schema:q.schema,changed:q.changed,candidateCount:q.candidateCount,totalCatalog:q.totalCatalog,counts:q.counts,hold:q.contentApproval,storageKeyChanged:q.storageKeyChanged,status:q.status,idParity:q.rows.length===Object.keys(c.items).length,regressionNoShrink:q.rows.every(x=>x.currentChars>=x.existingChars)};})(),
         thin:(()=>{const q=window.NOMUSA_THIN_ENRICHMENT_V2;return q&&{schema:q.schema,authored:q.authored,targets:q.targets,remainingOtherHold:q.remainingOtherHold,remainingPointsHold:q.remainingPointsHold,contentApproval:q.contentApproval,sourceCatalogChanged:q.sourceCatalogChanged,storageKeyChanged:q.storageKeyChanged,uniqueIds:new Set(q.rows.map(x=>x.id)).size===q.rows.length,changed:q.rows.every(x=>x.newDetailChars>x.oldDetailChars&&x.newCompactChars>x.oldCompactChars),preserved:q.rows.every(x=>Boolean(c.items[x.id]?.beforeThinV2Compressed))};})(),
         v3:(()=>{const q=window.NOMUSA_20YEAR_V3_GATE,a=window.NOMUSA_V3_SOURCE_POINTS_AUDIT;return q&&a&&{schema:q.schema,count:q.v3Manuscripts,candidates:q.candidates,baselineV2:q.previousV2IssueDrafts,audit:a.total,points:a.unverifiedNumeric,possible:a.parentCandidatesResolvedFromExtractedText,verified:a.verifiedAgainstOriginalPDF,changedRaw:q.rawCatalogAndStoredKeysChanged,approval:q.contentApproval,priorPreserved:q.rows.every(x=>Boolean(c.items[x.id]?.priorDetailedV3)&&Boolean(c.items[x.id]?.priorCompressedV3))};})(),
         v4:(()=>{const a=window.NOMUSA_V4_DEEPENING,p=window.NOMUSA_V4_PDF_SCORE_AUDIT;return a&&p&&{schema:a.schema,targets:a.targets,authored:a.authored,total:a.allCandidates,cat:a.allCatalogue,sourceScored:p.matchedScoreMarkers,pdfs:p.pdfDocumentsInspected,half50:p.score50Count,half25:p.score25Count,externalHash:p.qnetOriginalAttachmentHashVerified,originalPointsChanged:a.originalCatalogModified,saveKeysChanged:a.originalStorageKeysModified,approval:a.independentContentApproval,uniqueIds:new Set(a.rows.map(x=>x.id)).size===a.rows.length,grow:a.rows.every(x=>x.newDetailLength>x.previousDetailLength+150&&x.oldAnswerPreserved&&x.existingCompressedPreserved),originalsPreserved:a.rows.every(x=>!!c.items[x.id]?.previousDetailedV4&&c.items[x.id]?.previousCompressedV4===(c.items[x.id]?.compressedBeforeV8||c.items[x.id]?.compressedBeforeV7||c.items[x.id]?.compressedBeforeV6||c.items[x.id]?.compressedBeforeV5||c.items[x.id]?.compressed)),econ2025:c.items['2025-econ-2']?.detailed?.includes('Δw=15')};})(),
         v5:(()=>{const m=window.NOMUSA_V5_MANUSCRIPT_GATE;return m&&{schema:m.schema,completed:m.fullyRewrittenQuestionManuscripts,remaining:m.notYetRewrittenInThisPass,all:m.originalRepresentativeCandidates,original:m.originalExercises,legalApproved:m.contentApprovalsIssued,pages:m.all50PointPageTargetsCertified,originalChanged:m.originalCatalogModified,keysChanged:m.studyKeysChanged,hold:m.finalStatus,saved:m.rows.every(r=>Boolean(c.items[r.id]?.detailedBeforeV5)&&Boolean(c.items[r.id]?.compressedBeforeV5)),count:new Set(m.rows.map(r=>r.id)).size,question2023:c.items['2023-econ-1']?.detailed?.includes('59.4 증가'),question2025:c.items['2025-econ-2']?.detailed?.includes('Δw=15')};})(),
         v6:(()=>{const g=window.NOMUSA_V6_MANUSCRIPT_GATE,m=window.NOMUSA_V6_MANUSCRIPTS||{};return g&&{schema:g.schema,total:g.v6NewManuscripts,remaining:g.remainingInFocusedSet,focused:g.currentlyRewrittenInFocusedSet,fifty:g.fiftyPointV6,twentyfive:g.twentyFivePointV6,candidates:g.candidates,exercise:g.exercises,approval:g.officialFinalContentApprovals,pages:g.target8to10PagesVerified,raw:g.modifiedCatalog,keys:g.modifiedKeys,writing:g.modifiedStoredAnswers,unique:new Set(g.rows.map(x=>x.id)).size===g.rows.length,restored:g.rows.every(x=>c.items[x.id]?.detailedBeforeV6&&c.items[x.id]?.compressedBeforeV6),economic:c.items['2025-econ-1']?.detailed?.includes('2812.5'),labor:c.items['2022-labor1-1']?.detailed?.includes('2017다226605'),manuscriptCount:Object.keys(m).length};})(),
         v7:(()=>{const g=window.NOMUSA_V7_MANUSCRIPT_GATE,m=window.NOMUSA_V7_MANUSCRIPTS||{};return g&&{schema:g.schema,added:g.v7NewManuscripts,complete:g.totalRewrittenInFocusedSet,remaining:g.remainingInFocusedSet,all:g.candidates,points:g.v7FiftyPoint,source:g.exercises,old:g.rows.every(x=>!!c.items[x.id]?.detailedBeforeV7&&!!c.items[x.id]?.compressedBeforeV7),legalApproved:g.finalApprovalCount,raw:g.originalCatalogChanged,keys:g.storageKeysChanged,saved:g.existingStoredAnswersChanged,pages:g.handwriting8to10PageVerified,unique:new Set(g.rows.map(x=>x.id)).size===g.rows.length,ids:g.rows.map(x=>x.id),manuscripts:Object.keys(m).length,sourceCase:c.items['2022-labor2-1']?.detailed?.includes('2015도1927'),sourceCivil:c.items['2023-civil-1']?.detailed?.includes('2021다275741'),sourceAdmin:c.items['2023-admin-1']?.detailed?.includes('98무37')};})(),
         v8:(()=>{const g=window.NOMUSA_V8_QUALITY_GATE,c=window.NOMUSA_CANONICAL_SELECTION_V1,p=window.NOMUSA_V8_PDF_2023_LABOR1_Q1;return g&&{schema:g.schema,total:g.focusedTotal,added:g.newManuscripts,rewritten:g.focusedRewritten,remaining:g.focusedOutstanding,legacy:g.earlierSourceOnlyItems,candidates:g.representativeCandidates,catalog:g.catalogCount,approval:g.finalOfficialContentApprovals,pages:g.paper8to10PagesProven,original:g.originalDocumentsChanged,ids:g.canonicalIDsChanged,keys:g.storageKeysChanged,sourceHash:p?.sha256,sourcePage:p?.page,sourcePoints:p?.subquestions?.map(q=>q.points).join(','),unique:new Set(g.rows.map(r=>r.id)).size===g.rows.length,old:g.rows.every(r=>!!c.items[r.id]?.detailedBeforeV8&&!!c.items[r.id]?.compressedBeforeV8),score:g.scoreCounts,topics:{'2023_labor':c.items['2023-labor1-1']?.detailed?.includes('25점'), '2023_economics':c.items['2023-econ-3']?.detailed?.includes('2.5억원'), '2024_economics':c.items['2024-노동경제학|3|1']?.detailed?.includes('625'),'2026_economics':c.items['2026-노동경제학|3|1']?.detailed?.includes('0.25')}};})(),
         v9:(()=>{const g=window.NOMUSA_V9_QUALITY_GATE,c=window.NOMUSA_CANONICAL_SELECTION_V1,m=window.NOMUSA_V9_MANUSCRIPTS||{};return g&&{schema:g.schema,all:g.v8FocusedManuscripts,updated:g.v9Deepened,pending:g.remainingFocusedNeedingIndividualReview,exercises:g.sourceQuestions,candidates:g.representativeCandidates,approvals:g.finalContentApprovals,scoreUnchanged:g.originalPointsChanged,idsUnchanged:g.originalCatalogChanged,keysUnchanged:g.originalStorageKeysChanged,pages:g.handwritingPageTargetReached,unique:new Set(g.rows.map(x=>x.id)).size===4,restored:g.rows.every(x=>c.items[x.id]?.detailedBeforeV9&&c.items[x.id]?.compressedBeforeV9&&c.items[x.id]?.detailedBeforeV9.length===x.priorDetailedChars&&c.items[x.id]?.compressedBeforeV9.length===x.priorCompactChars),expanded:g.rows.every(x=>x.revisedDetailedChars>x.priorDetailedChars+200&&x.revisedCompactChars>x.priorCompactChars),confirmed:g.rows.every(x=>x.precedentUrls.length>=1),caseIds:Object.keys(m).sort().join('|'),contentChecks:{wage:c.items['2022-labor1-2']?.detailed?.includes('2019다238053')&&c.items['2022-labor1-2']?.detailed?.includes('통상임금에 해당'),retire:c.items['2022-admin-2']?.detailed?.includes('2019두52386'),disciplinary:c.items['2023-labor1-1']?.detailed?.includes('2006다48069'),insurance:c.items['2023-admin-3']?.detailed?.includes('2016다221658')}};})(),
         v10:(()=>{const g=window.NOMUSA_V10_QUALITY_GATE,c=window.NOMUSA_CANONICAL_SELECTION_V1;return g&&{schema:g.schema,count:g.v10Rewritten,candidates:g.representativeCandidates,exercises:g.sourceQuestions,approvals:g.finalContentApprovals,pages:g.handwritingPageTargetReached,ids:g.originalCatalogChanged,points:g.originalPointsChanged,keys:g.originalStorageKeysChanged,unique:new Set(g.rows.map(x=>x.id)).size===12,restored:g.rows.every(x=>c.items[x.id]?.detailedBeforeV10?.length===x.priorDetailedChars&&c.items[x.id]?.compressedBeforeV10?.length===x.priorCompactChars),v9Kept:['2022-labor1-2','2022-admin-2','2023-labor1-1','2023-admin-3'].every(id=>!!c.items[id]?.detailedBeforeV9),contentChecks:{renewal:c.items['2024-노동법1|1|1']?.detailed?.includes('2014두45765'),transfer:c.items['2024-노동법1|1|2']?.detailed?.includes('2010다41089'),interim:c.items['2024-노동법1|2|0']?.detailed?.includes('1,260만 원'),carmaster:c.items['2024-노동법2|1|1']?.detailed?.includes('2019두33712'),fairRep:c.items['2024-노동법2|2|0']?.detailed?.includes('2017다263192'),doctor:c.items['2026-노동법1|1|1']?.detailed?.includes('2021도11675'),division:c.items['2026-노동법1|2|0']?.detailed?.includes('2016두64876'),committee:c.items['2026-노동법2|1|1']?.detailed?.includes('2023두61370'),appraisal:c.items['2026-노동법2|1|2']?.detailed?.includes('2017두37031')}};})(),
         v11:(()=>{const g=window.NOMUSA_V11_QUALITY_GATE,c=window.NOMUSA_CANONICAL_SELECTION_V1;return g&&{schema:g.schema,count:g.v11Rewritten,candidates:g.representativeCandidates,exercises:g.sourceQuestions,approvals:g.finalContentApprovals,pages:g.handwritingPageTargetReached,ids:g.originalCatalogChanged,points:g.originalPointsChanged,keys:g.originalStorageKeysChanged,unique:new Set(g.rows.map(x=>x.id)).size===17,restored:g.rows.every(x=>c.items[x.id]?.detailedBeforeV11?.length===x.priorDetailedChars&&c.items[x.id]?.compressedBeforeV11?.length===x.priorCompactChars),v10Kept:Object.keys(window.NOMUSA_V10_MANUSCRIPTS||{}).every(id=>!!c.items[id]?.detailedBeforeV10),contentChecks:{childcare:c.items['2024-행정쟁송법|1|1']?.detailed?.includes('2018두47264'),partial:c.items['2024-행정쟁송법|1|2']?.detailed?.includes('98두2270'),notice:c.items['2024-행정쟁송법|3|0']?.detailed?.includes('2004두619'),rivals:c.items['2026-행정쟁송법|1|1']?.detailed?.includes('2009두8359'),ruling:c.items['2026-행정쟁송법|1|2']?.detailed?.includes('2015두45045'),pension:c.items['2026-행정쟁송법|3|1']?.detailed?.includes('2004두244'),service:c.items['2024-민사소송법|3|0']?.detailed?.includes('2014다54366'),heirs:c.items['2026-민사소송법|1|1']?.detailed?.includes('2007다22859'),change:c.items['2026-민사소송법|2|0']?.detailed?.includes('2014다31721')}};})(),
         yearCount:new Set(rows.map(x=>x.year)).size,
         firstCount:window.QDATA?.length||null,
         legacyCount:window.NOMUSA_LEGACY_181_DRAFTS?.stats?.target||null,
         drafts:Object.fromEntries(%s.map(id=>[id, c?.items?.[id] ?
           {detailed:c.items[id].detailed,compressed:c.items[id].compressed,
            renderable:c.items[id].renderable}:null]))};
    }""" % json.dumps(IDENTIFIERS,ensure_ascii=False))

def check_inventory(inv):
    gate=inv["gate"]
    assert inv["status"]=="DRAFT_SOURCE_READY",inv
    assert gate["catalogCount"]==377,gate
    assert gate["candidateCount"]==328 and gate["renderable"]==328,gate
    assert gate["uniqueIds"] is True
    assert not gate["missingIds"] and not gate["unexpectedIds"] and not gate["notRenderable"],gate
    assert len(gate["originalParentIds"])==49
    assert inv["yearCount"]==20 and inv["legacyCount"]==181
    batch=inv["batch"]
    assert batch and batch["schema"]=="nomusa-20year-quality-batch/1",batch
    assert batch["totalCatalog"]==377 and batch["candidateCount"]==328,batch
    assert batch["changed"]>=200 and sum(batch["counts"].values())==328,batch
    assert batch["counts"]["HOLD_POINTS_UNKNOWN"]==26,batch
    assert batch["hold"]=="HOLD" and batch["storageKeyChanged"] is False,batch
    assert batch["idParity"] is True and batch["regressionNoShrink"] is True,batch
    assert all(x and x["renderable"] for x in inv["drafts"].values())
    v11=inv["v11"]
    assert v11 and v11["schema"]=="nomusa-20year-essay-admin-civil-depth/11",v11
    assert v11["count"]==17 and v11["candidates"]==328 and v11["exercises"]==377,v11
    assert v11["approvals"]==0 and v11["pages"] is False,v11
    assert v11["ids"] is False and v11["points"] is False and v11["keys"] is False,v11
    assert v11["unique"] is True and v11["restored"] is True and v11["v10Kept"] is True,v11
    assert all(v11["contentChecks"].values()),v11
    v10=inv["v10"]
    assert v10 and v10["schema"]=="nomusa-20year-essay-labor-depth/10",v10
    assert v10["count"]==12 and v10["candidates"]==328 and v10["exercises"]==377,v10
    assert v10["approvals"]==0 and v10["pages"] is False,v10
    assert v10["ids"] is False and v10["points"] is False and v10["keys"] is False,v10
    assert v10["unique"] is True and v10["restored"] is True and v10["v9Kept"] is True,v10
    assert all(v10["contentChecks"].values()),v10
    v9=inv["v9"]
    assert v9 and v9["schema"]=="nomusa-20year-essay-legal-depth/9",v9
    assert v9["all"]==57 and v9["updated"]==4 and v9["pending"]==53,v9
    assert v9["exercises"]==377 and v9["candidates"]==328 and v9["approvals"]==0,v9
    assert v9["scoreUnchanged"] is False and v9["idsUnchanged"] is False and v9["keysUnchanged"] is False,v9
    assert v9["pages"] is False and v9["unique"] is True and v9["restored"] is True,v9
    assert v9["expanded"] is True and v9["confirmed"] is True,v9
    assert all(v9["contentChecks"].values()),v9

    v8=inv["v8"]
    assert v8 and v8["schema"]=="nomusa-20year-essay-quality-batch/8",v8
    assert v8["total"]==57 and v8["added"]==38 and v8["rewritten"]==57 and v8["remaining"]==0,v8
    assert v8["legacy"]==10 and v8["candidates"]==328 and v8["catalog"]==377,v8
    assert v8["approval"]==0 and v8["pages"] is False,v8
    assert v8["original"] is False and v8["ids"] is False and v8["keys"] is False,v8
    assert v8["sourceHash"]=="9fb544e9e6bed6d314a9d151474e23d009c7f6bd82ea01c6ec4d342486fdfa7d",v8
    assert v8["sourcePage"]==2 and v8["sourcePoints"]=="25,25",v8
    assert v8["unique"] is True and v8["old"] is True,v8
    assert all(v8["topics"].values()),v8

    v7=inv["v7"]
    assert v7 and v7["schema"]=="nomusa-20year-essay-manuscript/7",v7
    assert v7["added"]==5 and v7["complete"]==19 and v7["remaining"]==38,v7
    assert v7["all"]==328 and v7["points"]==5 and v7["source"]==377,v7
    assert v7["old"] is True and v7["legalApproved"]==0 and v7["pages"] is False,v7
    assert v7["raw"] is False and v7["keys"] is False and v7["saved"] is False,v7
    assert v7["unique"] is True and v7["manuscripts"]==5,v7
    assert v7["sourceCase"] is True and v7["sourceCivil"] is True and v7["sourceAdmin"] is True,v7

    v6=inv["v6"]
    assert v6 and v6["schema"]=="nomusa-20year-essay-manuscript/6",v6
    assert v6["total"]==9 and v6["remaining"]==43 and v6["focused"]==14,v6
    assert v6["fifty"]==7 and v6["twentyfive"]==2,v6
    assert v6["candidates"]==328 and v6["exercise"]==377,v6
    assert v6["approval"]==0 and v6["pages"] is False,v6
    assert v6["raw"] is False and v6["keys"] is False and v6["writing"] is False,v6
    assert v6["unique"] is True and v6["restored"] is True,v6
    assert v6["economic"] is True and v6["labor"] is True and v6["manuscriptCount"]==9,v6

    v5=inv["v5"]
    assert v5 and v5["schema"]=="nomusa-answer-manuscript/5",v5
    assert v5["completed"]==5 and v5["remaining"]==52 and v5["count"]==5,v5
    assert v5["all"]==328 and v5["original"]==377,v5
    assert v5["legalApproved"]==0 and v5["pages"] is False,v5
    assert v5["originalChanged"] is False and v5["keysChanged"] is False,v5
    assert v5["saved"] is True and v5["question2023"] is True and v5["question2025"] is True,v5

    v4=inv["v4"]
    assert v4 and v4["schema"]=="nomusa-20year-57-deepening/4",v4
    assert v4["targets"]==57 and v4["authored"]==57,v4
    assert v4["total"]==328 and v4["cat"]==377,v4
    assert v4["sourceScored"]==26 and v4["pdfs"]==10,v4
    assert v4["half50"]==10 and v4["half25"]==16,v4
    assert v4["externalHash"] is False,v4
    assert v4["originalPointsChanged"] is False and v4["saveKeysChanged"] is False,v4
    assert v4["approval"]=="HOLD" and v4["uniqueIds"] is True,v4
    assert v4["grow"] is True and v4["originalsPreserved"] is True,v4
    assert v4["econ2025"] is True,v4

    v3=inv["v3"]
    assert v3 and v3["schema"]=="nomusa-20year-writing-gate/3",v3
    assert v3["count"]==7 and v3["candidates"]==328,v3
    assert v3["baselineV2"]==61 and v3["audit"]==29,v3
    assert v3["points"]==26 and v3["possible"]==26,v3
    assert v3["verified"]==0 and v3["changedRaw"] is False,v3
    assert v3["approval"]=="HOLD" and v3["priorPreserved"] is True,v3

    thin=inv["thin"]
    assert thin and thin["schema"]=="nomusa-20year-thin-issue-enrichment/2",thin
    assert thin["targets"]==61 and thin["authored"]==61,thin
    assert thin["remainingOtherHold"]==29 and thin["remainingPointsHold"]==26,thin
    assert thin["contentApproval"]=="HOLD" and thin["storageKeyChanged"] is False,thin
    assert thin["sourceCatalogChanged"] is False,thin
    assert thin["uniqueIds"] is True and thin["changed"] is True and thin["preserved"] is True,thin

    # Question-specific content regression: 2026 organizational bargaining, 12 points.
    # Four comparison axes must be substantive, not a one-paragraph placeholder.
    compressed_2026 = inv["drafts"]["2026-경영조직론|1|1"]["compressed"]
    assert len(compressed_2026) >= 1100, "2026_12PT_COMPACT_STILL_TOO_SHORT"
    assert all(term in compressed_2026 for term in ("지향 목표", "정보공유 수준", "관계의 지속가능성", "분배구조")), "2026_FOUR_AXES_MISSING"
    assert "학술근거:" in compressed_2026, "2026_ACADEMIC_CITATION_MISSING"
    # Regression for literal \\n tokens previously visible in the 2026 compact answer.
    assert "\\n" not in inv["drafts"]["2026-경영조직론|1|1"]["compressed"], "LITERAL_NEWLINE_TOKENS_LEAKED"

def overflow(page,width):
    data=page.evaluate("""() => ({w:document.documentElement.scrollWidth,
      viewport:document.documentElement.clientWidth})""")
    assert data["w"]<=max(width,data["viewport"])+2,data

def choose_hub(page,id):
    year=id[:4]
    page.locator('[data-year="%s"]'%year).first.click()
    if page.viewport_size["width"]<701:
        toggle=page.locator('[data-action="list-toggle"]')
        if toggle.count() and toggle.is_visible():toggle.click()
    page.locator('[data-question="%s"]'%id).first.click()
    page.locator('[data-trace="4"]').first.click()

def check_viewports(browser,width):
    ctx=browser.new_context(viewport={"width":width,"height":880},accept_downloads=True)
    second=ctx.new_page()
    hub=ctx.new_page()
    errorsSecond=capture(second);errorsHub=capture(hub)
    try:
        second.goto(BASE+"/second/",wait_until="domcontentloaded")
        hub.goto(BASE+"/study-hub/#home",wait_until="domcontentloaded")
        second.wait_for_function("window.N27_ESSAY_TEST && window.NOMUSA_CANONICAL_SELECTION_V1?.gate",timeout=15000)
        hub.wait_for_function("window.HubState && window.NOMUSA_CANONICAL_SELECTION_V1?.gate",timeout=15000)
        a,b=inventory(second),inventory(hub)
        if not a.get("v4") or not b.get("v4"):
            raise AssertionError("V4_INITIALIZATION_DIAGNOSTIC "+json.dumps({
              "secondErrors":errorsSecond,"hubErrors":errorsHub,
              "secondData":second.evaluate("""() => ({
                pointAudit:!!window.NOMUSA_V4_PDF_SCORE_AUDIT,
                pointCount:window.NOMUSA_V4_PDF_SCORE_AUDIT?.total||null,
                deepDraftCount:Object.keys(window.NOMUSA_V4_DEEP_DRAFTS||{}).length,
                finalData:!!window.NOMUSA_V4_DEEPENING
              })"""),
              "hubData":hub.evaluate("""() => ({
                pointAudit:!!window.NOMUSA_V4_PDF_SCORE_AUDIT,
                pointCount:window.NOMUSA_V4_PDF_SCORE_AUDIT?.total||null,
                deepDraftCount:Object.keys(window.NOMUSA_V4_DEEP_DRAFTS||{}).length,
                finalData:!!window.NOMUSA_V4_DEEPENING
              })""")
            },ensure_ascii=False))
        check_inventory(a);check_inventory(b)
        for id in IDENTIFIERS:
            assert a["drafts"][id]==b["drafts"][id],id
        overflow(second,width);overflow(hub,width)
        RESULTS.append({"name":"identical_catalog_and_drafts_%s"%width,"status":"PASS",
          "catalog":377,"candidates":328,"ids":len(IDENTIFIERS)})

        # Actual DOM across detailed, compressed, compare, and writing panes.
        id="2025-org-1"
        second.evaluate("id=>window.N27_ESSAY_TEST.select(id)",id)
        second.locator('[data-pane="detail"]').first.click()
        assert second.locator('.nomusa-canonical-draft[data-canonical-id="2025-org-1"]').count()==1
        second.locator('[data-pane="compact"]').first.click()
        assert second.locator('[data-canonical-id="2025-org-1"]').count()>=1
        second.locator('[data-pane="write"]').first.click()
        note="공인노무사 교차화면 검증 %spx"%width
        second.locator('[data-v1090-tab="editor"]').first.click()
        second.locator("#v1090-editor").fill(note)
        second.wait_for_function("([key,id,note]) => JSON.parse(localStorage.getItem(key)||'{}').drafts?.[id]===note",
          arg=[KEY,id,note])

        # Reload the already open hub tab to read the saved draft from the shared key.
        hub.reload(wait_until="domcontentloaded")
        hub.wait_for_function("window.HubState && window.NOMUSA_CANONICAL_SELECTION_V1?.gate",timeout=15000)
        choose_hub(hub,id)
        hub.locator('[data-pane="detail"]').first.click()
        assert hub.locator('.nomusa-canonical-draft[data-canonical-id="2025-org-1"]').count()==1
        hub.locator('[data-pane="compressed"]').first.click()
        assert hub.locator('.nomusa-canonical-compact[data-canonical-id="2025-org-1"]').count()==1
        hub.locator('[data-pane="write"]').first.click()
        assert hub.locator("#draft").input_value()==note
        hub.locator("#draft").fill(note+" / 허브 보강")
        hub.wait_for_function("([key,id,note])=>JSON.parse(localStorage.getItem(key)||'{}').drafts?.[id]===note",
          arg=[KEY,id,note+" / 허브 보강"])

        second.reload(wait_until="domcontentloaded")
        second.wait_for_function("window.N27_ESSAY_TEST",timeout=15000)
        second.evaluate("id=>window.N27_ESSAY_TEST.select(id)",id)
        second.locator('[data-pane="write"]').first.click()
        assert second.locator("#v1090-editor").input_value()==note+" / 허브 보강"
        second.locator('[data-pane="compare"]').first.click()
        assert second.locator('[data-canonical-id="2025-org-1"]').count()>=1
        hub.locator('[data-pane="compare"]').first.click()
        assert hub.locator('[data-canonical-id="2025-org-1"]').count()>=1
        # V10: 2026 공정대표의무(상벌위원회) 문항의 상세·압축·암기·작성 탭 및 기존 기록 보존.
        vid="2026-노동법2|1|1"
        before=second.evaluate("key=>localStorage.getItem(key)",KEY)
        second.evaluate("id=>window.N27_ESSAY_TEST.select(id)",vid)
        second.locator('[data-pane="detail"]').first.click()
        assert "2023두61370" in second.locator('.nomusa-canonical-draft').first.inner_text()
        second.locator('[data-pane="compact"]').first.click()
        assert "2023두61370" in second.locator('[data-canonical-id="%s"]'%vid).first.inner_text()
        second.locator('[data-pane="memory"]').first.click()
        assert second.locator('.n107-memory-card').count()>=1
        prior=json.loads(before or "{}").get("drafts",{})
        after=json.loads(second.evaluate("key=>localStorage.getItem(key)",KEY) or "{}").get("drafts",{})
        assert all(after.get(k)==v for k,v in prior.items()),"V10_EXISTING_RECORD_CHANGED"
        hub.goto(BASE+"/study-hub/#home",wait_until="domcontentloaded")
        hub.reload(wait_until="domcontentloaded")
        hub.wait_for_function("window.HubState && window.NOMUSA_CANONICAL_SELECTION_V1?.gate",timeout=15000)
        hub.locator('[data-year="2026"]').first.click()
        if hub.viewport_size["width"]<701:
            toggle=hub.locator('[data-action="list-toggle"]')
            if toggle.count() and toggle.is_visible():toggle.click()
        sel=hub.locator('#filter-subject')
        if sel.count():
            opts=sel.evaluate("e=>[...e.options].map(o=>o.value)")
            sel.select_option("노동법" if "노동법" in opts else opts[0])
        for _ in range(4):  # 2026 essay list can exceed one 30-item page
            if hub.locator('[data-question="%s"]'%vid).count():break
            nxt=hub.locator('[data-action="list-next"]:not([disabled])')
            if not nxt.count():break
            nxt.first.click()
        hub.locator('[data-question="%s"]'%vid).first.click()
        hub.locator('[data-trace="4"]').first.click()
        hub.locator('[data-pane="detail"]').first.click()
        assert "2023두61370" in hub.locator('.nomusa-canonical-draft').first.inner_text()
        overflow(second,width);overflow(hub,width)
        RESULTS.append({"name":"v10_labor_detail_compact_memory_%s"%width,"status":"PASS"})
        # V11: 2026 행정쟁송법 재결 기속력 문항의 상세·압축·암기·작성 탭 및 기존 기록 보존.
        vid="2026-행정쟁송법|1|2"
        before=second.evaluate("key=>localStorage.getItem(key)",KEY)
        second.evaluate("id=>window.N27_ESSAY_TEST.select(id)",vid)
        second.locator('[data-pane="detail"]').first.click()
        assert "2015두45045" in second.locator('.nomusa-canonical-draft').first.inner_text()
        second.locator('[data-pane="compact"]').first.click()
        assert "2015두45045" in second.locator('[data-canonical-id="%s"]'%vid).first.inner_text()
        second.locator('[data-pane="memory"]').first.click()
        assert second.locator('.n107-memory-card').count()>=1
        prior=json.loads(before or "{}").get("drafts",{})
        after=json.loads(second.evaluate("key=>localStorage.getItem(key)",KEY) or "{}").get("drafts",{})
        assert all(after.get(k)==v for k,v in prior.items()),"V11_EXISTING_RECORD_CHANGED"
        hub.goto(BASE+"/study-hub/#home",wait_until="domcontentloaded")
        hub.reload(wait_until="domcontentloaded")
        hub.wait_for_function("window.HubState && window.NOMUSA_CANONICAL_SELECTION_V1?.gate",timeout=15000)
        hub.locator('[data-year="2026"]').first.click()
        if hub.viewport_size["width"]<701:
            toggle=hub.locator('[data-action="list-toggle"]')
            if toggle.count() and toggle.is_visible():toggle.click()
        sel=hub.locator('#filter-subject')
        if sel.count():
            opts=sel.evaluate("e=>[...e.options].map(o=>o.value)")
            sel.select_option("행정쟁송법" if "행정쟁송법" in opts else opts[0])
        for _ in range(4):  # 2026 essay list can exceed one 30-item page
            if hub.locator('[data-question="%s"]'%vid).count():break
            nxt=hub.locator('[data-action="list-next"]:not([disabled])')
            if not nxt.count():break
            nxt.first.click()
        hub.locator('[data-question="%s"]'%vid).first.click()
        hub.locator('[data-trace="4"]').first.click()
        hub.locator('[data-pane="detail"]').first.click()
        assert "2015두45045" in hub.locator('.nomusa-canonical-draft').first.inner_text()
        overflow(second,width);overflow(hub,width)
        RESULTS.append({"name":"v11_admin_detail_compact_memory_%s"%width,"status":"PASS"})
        overflow(second,width);overflow(hub,width)
        assert not errorsSecond and not errorsHub,(errorsSecond,errorsHub)
        RESULTS.append({"name":"save_reload_crosspage_detail_compact_compare_%s"%width,"status":"PASS"})
    finally:
        ctx.close()

try:
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,args=["--no-sandbox"])
        for width in (1440,390,360):
            try:check_viewports(browser,width)
            except Exception:
                RESULTS.append({"name":"viewport_%s"%width,"status":"HOLD","error":traceback.format_exc()[-2200:]})
        browser.close()
finally:
    srv.shutdown()
status="PASS" if RESULTS and all(x["status"]=="PASS" for x in RESULTS) else "HOLD"
print(json.dumps({"schema":"nomusa-canonical-shared-browser-gate/1",
  "status":status,"verifiedCode":"local checkout only","browser":"Chromium",
  "main":"UNCHANGED","production":"UNCHANGED","preview":"NOT_DEPLOYED",
  "results":RESULTS},ensure_ascii=False,indent=2))
sys.exit(0 if status=="PASS" else 2)
