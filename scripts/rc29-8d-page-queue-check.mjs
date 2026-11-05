#!/usr/bin/env node
import fs from "node:fs";
const x=JSON.parse(fs.readFileSync("data/rc29-8d-source-page-queue.json","utf8"));
const errors=[];const ok=(b,n)=>{if(!b)errors.push(n)};
ok(x.year===2023&&x.highRiskQueue===31&&x.distinctPageHints===23&&x.pageHintsInBounds===31,"page queue");
ok(x.individuallyQuestionLocationConfirmed===1&&x.confirmedKey==="2023-노동법(1)-024","only one visually confirmed");
ok(x.individuallyQuestionTextAndOptionsApproved===0&&x.officialScoringApproved===0,"no source approval");
ok(x.firstPassDrafts===59&&x.legacyOCRReviewPending===91&&x.highRiskReviewPending===31&&x.normalRiskReviewPending===60,"baseline");
ok(x.firstPassDrafts+x.legacyOCRReviewPending===150&&x.highRiskReviewPending+x.normalRiskReviewPending===91,"partition");
ok(!x.githubCIOriginalPdfAvailable&&!x.publicRepoCopyrightSourceUploaded,"public CI source absent");
ok(x.releaseGate==="HOLD"&&!x.vercelDeployed,"no deploy");
const out={schema:"rc29-8d-metadata-ci-v1",status:errors.length?"ERROR":"METADATA_PASS_RELEASE_HOLD",pageHintsInBounds:31,sourcePageImagesPreparedPrivately:23,questionLocationConfirmed:1,questionContentApproved:0,officialScoringApproved:0,releaseGate:"HOLD",errors};
fs.mkdirSync("rc29-evidence",{recursive:true});fs.writeFileSync("rc29-evidence/rc29-8d-page-queue.json",JSON.stringify(out,null,2)+"\n");console.log(JSON.stringify(out,null,2));if(errors.length)process.exitCode=2;
