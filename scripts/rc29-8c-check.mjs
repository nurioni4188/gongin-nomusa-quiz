#!/usr/bin/env node
// Verify only RC29.8C metadata and scoring lock. Source PDF is not available in public CI.
import fs from "node:fs";
const x=JSON.parse(fs.readFileSync("data/rc29-8c-2023-firstpass.json","utf8"));
const errors=[];const check=(ok,why)=>{if(!ok)errors.push(why)};
check(x.schema==="rc29-8c-2023-civil-firstpass-v1"&&x.year===2023&&x.total2023QuestionSlots===150,"scope");
check(x.previousDrafts===53&&x.newDrafts===6&&x.cumulativeDrafts===59,"drafts");
check(x.previousOCRPending===97&&x.remainingOCRPending===91,"remaining");
check(x.cumulativeDrafts+x.remainingOCRPending===x.total2023QuestionSlots,"partition");
check(x.previousHighRisk===37&&x.remainingHighRisk===31&&x.remainingNormalRisk===60,"risk");
check(x.remainingHighRisk+x.remainingNormalRisk===x.remainingOCRPending,"risk partition");
check(x.firstPassCompared.length===6&&new Set(x.firstPassCompared.map(t=>t.num)).size===6,"unique corrections");
check(x.firstPassCompared.map(t=>t.num).join(",")==="51,52,53,73,74,75","exam question numbers");
check(x.firstPassCompared.every(t=>t.page===(t.num<=53?19:26)),"paper pages");
check(/^[0-9a-f]{64}$/.test(x.originalSourceSha256)&&Object.values(x.paperPageRenders).every(h=>/^[0-9a-f]{64}$/.test(h)),"hash formats");
check(x.sourceQuality==="FIRST_PASS_VISUAL_DRAFTS_NOT_INDEPENDENTLY_VERIFIED","quality not overstated");
check(x.newDraftsSecondReviewed===0&&x.officialQuestionVerified===0&&x.scoringApproved===0,"grading gate");
check(x.browserTestsPassed===4&&x.browserViewportWidths.length===4&&!x.realAndroidDeviceTested,"browser scope");
check(!x.sourceDirectPdfInGithubCI&&!x.copyrightedSourcePdfOrQuestionTextsPubliclyCommitted,"source visibility");
check(x.releaseGate==="HOLD"&&!x.vercelDeploymentPerformed,"no deploy");
const output={schema:"rc29-8c-ci-status-v1",status:errors.length?"ERROR":"MANIFEST_INTEGRITY_PASS_RELEASE_HOLD",
firstPassDrafts:59,legacyOCRPending:91,priorityReviewCount:31,
originalPaperReopenedInCI:false,officialScoringApproved:0,releaseGate:"HOLD",errors};
fs.mkdirSync("rc29-evidence",{recursive:true});
fs.writeFileSync("rc29-evidence/rc29-8c-metadata.json",JSON.stringify(output,null,2)+"\n");
console.log(JSON.stringify(output,null,2));if(errors.length)process.exitCode=2;
