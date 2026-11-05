#!/usr/bin/env node
import fs from "node:fs";
const m=JSON.parse(fs.readFileSync("data/rc29-7-firstpass-manifest.json","utf8"));
const errors=[]; const ok=(v,name)=>{if(!v)errors.push(name)};
ok(m.year===2023 && m.totalSlots===150,"scope");
ok(m.originalOCRTextPresent===112 && m.originalOCRBlank===38,"OCR baseline");
ok(m.priorDrafts===22 && m.newDrafts===17 && m.totalDrafts===39,"draft increments");
ok(m.originalBlanksFilledWithFirstPassDraft===38 && m.remainingBlanks===0,"draft coverage");
ok(m.legacyOCRPendingVisualReview===111 && m.replacedCorruptOCR===1,"unverified OCR count");
ok(m.totalDrafts + m.legacyOCRPendingVisualReview===150,"all 150 unverified slots");
ok(m.newDraftLocations.length===17 && new Set(m.newDraftLocations.map(x=>x[0]+"|"+x[1])).size===17,"new keys");
const count={}; for(const row of m.newDraftLocations){count[row[0]]=(count[row[0]]||0)+1;ok(Number.isInteger(row[2])&&row[2]>=1&&row[2]<=41,"page bounds");}
ok(count["민법"]===8&&count["사회보험법"]===4&&count["경영학개론"]===3&&count["경제학원론"]===2,"subjects");
ok(Object.values(m.sourcePdfSha256).every(s=>/^[a-f0-9]{64}$/.test(s)),"source hash format");
ok(m.actualScoringApproved===0&&m.visualDraftsSecondReviewed===0,"no premature scoring");
ok(m.offlineChromiumScreens===4&&m.offlineChromiumPassed===4&&!m.realAndroidTested,"chromium only");
ok(!m.githubActionsSourcePDFCheck && !m.fullQuestionsPubliclyCommitted && !m.sourcePDFsCommitted,"source handling");
ok(m.releaseGate==="HOLD"&&!m.vercelDeployPerformed,"deployment guard");
const out={schema:"rc29-7-ci-metadata-v1",status:errors.length?"ERROR":"METADATA_PASS_RELEASE_HOLD",
firstPassDrafts:39,remainingDraftBlanks:0,legacyOCRToReview:111,officiallyVerifiedForScoring:0,
PDFsReopenedInGithubActions:false,release:"HOLD",errors};
fs.mkdirSync("rc29-evidence",{recursive:true});
fs.writeFileSync("rc29-evidence/rc29-7-draft-coverage.json",JSON.stringify(out,null,2)+"\n");
console.log(JSON.stringify(out,null,2));if(errors.length)process.exitCode=2;
