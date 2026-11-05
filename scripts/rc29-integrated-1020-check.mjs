#!/usr/bin/env node
import fs from "node:fs";
const m=JSON.parse(fs.readFileSync("data/rc29-integrated-1020.json","utf8"));
const prior=JSON.parse(fs.readFileSync("data/rc29-2-source-manifest.json","utf8"));
const y23=JSON.parse(fs.readFileSync("data/rc29-8c-2023-firstpass.json","utf8"));
const v=JSON.parse(fs.readFileSync("vercel.json","utf8"));
const errors=[];const check=(b,label)=>{if(!b)errors.push(label)};
check(m.schema==="rc29-1020-source-free-coverage-v1"&&m.slots.length===1020,"scope 1020");
check(new Set(m.slots.map(r=>r.key)).size===1020,"unique IDs");
const status=m.slots.reduce((o,r)=>(o[r.status]=(o[r.status]||0)+1,o),{});
check(status.TEXT_CANDIDATE===565&&status.OCR_AND_DRAFT_UNVERIFIED===150&&status.SOURCE_MISSING===305,"status coverage");
check(m.summary.firstPass2023===59&&m.summary.unstructuredOCR2023===91&&59+91===150,"2023 status counts");
check(prior.candidateRows===565&&prior.textLayerCompleteMatches===443&&prior.textLayerMismatchRows===122,"565 source baseline");
check(y23.cumulativeDrafts===59&&y23.remainingOCRPending===91,"2023 visual baseline");
const yr={2022:[150,125,25],2023:[150,150,0],2024:[240,120,120],2025:[240,120,120],2026:[240,200,40]};
for(const [year,[all,present,missing]] of Object.entries(yr)){const x=m.slots.filter(r=>String(r.year)===year);check(x.length===all&&x.filter(r=>r.status!=="SOURCE_MISSING").length===present&&x.filter(r=>r.status==="SOURCE_MISSING").length===missing,"year "+year)}
for(const r of m.slots){check(r.key===String(r.year)+"-"+r.subject+"-"+String(r.num).padStart(3,"0"),"id "+r.key);check(r.officialVerified===false&&r.scoringApproved===false,"score guard "+r.key);check(!("question" in r)&&!("options" in r)&&!("answer" in r),"source privacy "+r.key)}
check(m.missingGroups.length===8&&m.missingGroups.reduce((a,g)=>a+g.count,0)===305,"missing groups");
check(m.summary.independentlyVerified===0&&m.summary.scoringApproved===0&&m.summary.releaseGate==="HOLD","release blocked");
check(!m.summary.vercelDeploymentPerformed&&v.git?.deploymentEnabled===false,"vercel disabled");
const out={schema:"rc29-1020-technical-ci-v1",status:errors.length?"FAIL":"PASS",slots:m.slots.length,presentCandidates:715,sourceMissing:305,officiallyVerified:0,scoringApproved:0,releaseDecision:"HOLD",sourcePDFOpenedInCI:false,errors};
fs.mkdirSync("rc29-evidence",{recursive:true});fs.writeFileSync("rc29-evidence/rc29-1020-technical-ci.json",JSON.stringify(out,null,2)+"\n");
console.log(JSON.stringify(out,null,2));if(errors.length)process.exitCode=2;
