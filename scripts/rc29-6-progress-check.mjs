#!/usr/bin/env node
import fs from "node:fs";
const data=JSON.parse(fs.readFileSync("data/rc29-6-progress.json","utf8"));
const problems=[];function assert(cond,label){if(!cond)problems.push(label)}
assert(data.expectedQuestionSlots===150&&data.sourceYear===2023,"2023 expected slots");
assert(data.originalOCREntriesWithText===112&&data.originalOCRBlankSlots===38,"original OCR baseline");
assert(data.priorFirstPassDrafts===9&&data.newFirstPassDrafts===13,"first-pass delta");
assert(data.totalFirstPassDrafts===data.priorFirstPassDrafts+data.newFirstPassDrafts,"new+prior draft count");
assert(data.newlyRestoredOriginallyBlankCount===21,"originally empty now drafted");
assert(data.replacedOriginallyNonblankCorruptedOCR===1,"Q2 corrupt OCR replacement");
assert(data.remainingBlankSlots===data.originalOCRBlankSlots-data.newlyRestoredOriginallyBlankCount,"blank count");
assert(data.legacyOCRStillPendingVisualCheck===data.originalOCREntriesWithText-data.replacedOriginallyNonblankCorruptedOCR,"OCR unverified pending count");
assert(data.legacyOCRStillPendingVisualCheck+data.remainingBlankSlots+data.totalFirstPassDrafts===data.expectedQuestionSlots,"partition exactly 150");
assert(data.newDrafts.reduce((n,r)=>n+r.nums.length,0)===13,"new draft total");
assert(data.newDrafts.every(r=>r.pages.length===r.nums.length&&r.pages.every(p=>Number.isInteger(p)&&p>=1&&p<=39)),"source pages");
assert(data.historicalOCRHeuristicTriage.reviewFirst+data.historicalOCRHeuristicTriage.normalReview===111,"legacy OCR review queue");
assert(data.historicalOCRHeuristicTriage.likelyCorruptionTokenFlagCount===45&&data.historicalOCRHeuristicTriage.veryShortTextFlagCount===6,"legacy OCR quality heuristic baseline");
assert(/^[a-f0-9]{64}$/.test(data.sourcePdfSha256),"source sha256 format");
assert(data.officialQuestionVerifications===0&&data.independentSecondReviewerSignoffs===0&&data.zeroOfficialGradingApproval,"NO premature verified data");
assert(data.offlineMobileTest.status==="PASS"&&!data.offlineMobileTest.realAndroidDeviceTested,"simulation vs real mobile");
assert(data.githubCITestingScope.startsWith("Manifest consistency only"),"must not exaggerate CI");
assert(data.releaseGate==="HOLD"&&data.previewAuthorized===false&&data.productionAuthorized===false&&data.vercelDeployRequested===false,"release protection");
const result={schema:"rc29-6-ci-metadata-check-v1",status:problems.length?"ERROR":"DRAFT_PROGRESS_METADATA_PASS_RELEASE_HOLD",
 drafts:data.totalFirstPassDrafts,untranscribed:data.remainingBlankSlots,ocrStillUnverified:data.legacyOCRStillPendingVisualCheck,
 officiallyVerifiedForScoring:0,originalSourcePDFReopenedInCI:false,localBrowserSimulationTestClaim:data.offlineMobileTest.status,
 manualAndroidRealDeviceTested:false,release:"HOLD",problems};
fs.mkdirSync("rc29-evidence",{recursive:true});
fs.writeFileSync("rc29-evidence/rc29-6-draft-metadata.json",JSON.stringify(result,null,2)+"\n");
console.log(JSON.stringify(result,null,2));
if(problems.length)process.exitCode=2;