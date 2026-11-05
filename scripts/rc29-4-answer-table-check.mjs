#!/usr/bin/env node
import fs from "node:fs";
const d=JSON.parse(fs.readFileSync("data/rc29-4-2023-answer-table-reference.json","utf8"));
const problems=[];const check=(b,m)=>{if(!b)problems.push(m)};
check(d.records.length===150,"must have 150 final table rows");
check(d.year===2023&&d.schema==="rc29-4-2023-hwp-table-reference-v1","source schema");
check(d.userUploadSha256==="3648842dc21edad047a60f4409111c6fdf8314ed13d0556933f8499d0c2d1e74","2023 user HWP sha");
check(d.imageStreams.join(",")==="BIN0001.bmp,BIN0002.bmp","image streams");
const keys=new Set();
const counts={};
for(const r of d.records){
 const key=r.year+"|"+r.subject+"|"+r.num;
 check(!keys.has(key),"duplicate key "+key);
 keys.add(key);
 check(r.year===2023&&r.booklet==="A","year/booklet "+key);
 check(Number.isInteger(r.officialAnswerLabelReference)&&r.officialAnswerLabelReference>=1&&r.officialAnswerLabelReference<=5,"label "+key);
 check(!("answer" in r)&&!("acceptedAnswers" in r)&&r.scoringApproved===false,"scoring allowed "+key);
 check(r.verificationStatus==="HWP_IMAGE_REFERENCE_MATCHED_QUESTION_UNVERIFIED","unsafe status "+key);
 counts[r.subject]=(counts[r.subject]||0)+1;
}
check(Object.keys(counts).length===6&&Object.values(counts).every(x=>x===25),"six subjects x25");
check(d.rc17PreviousReferenceAgreement===150&&d.conflictsWithRc17===0,"visual reference mismatch");
check(d.questionStemsAndFiveOptionsApproved===0&&d.liveScoringApproved===0&&d.finalReleaseGate==="HOLD","premature launch");
check(d.sourceAuthenticity==="TITLE_MATCHES_QNET_OFFICIAL_LISTING_NOT_DIRECT_DOWNLOAD_SHA_MATCH","source proof overstated");
const out={schema:"rc29-4-ci-reference-integrity-v1",
 status:problems.length?"ERROR":"REFERENCE_STRUCTURE_PASS_RELEASE_HOLD",
 recordCount:d.records.length,subjectCounts:counts,rc17ReferenceAgreement:150,
 ciReadOriginalHwp:false,ciVisuallyReviewedOriginalPaper:false,liveScoringApproved:0,
 qnetOriginalHwpShaIndependentlyValidated:false,release:"HOLD",errors:problems,
 explanation:"CI verifies stored reference rows and protective flags only. Original HWP/PDF not stored in GitHub."};
fs.mkdirSync("rc29-evidence",{recursive:true});
fs.writeFileSync("rc29-evidence/rc29-4-answer-table-structure.json",JSON.stringify(out,null,2)+"\n");
console.log(JSON.stringify(out,null,2));
if(problems.length)process.exitCode=2;
