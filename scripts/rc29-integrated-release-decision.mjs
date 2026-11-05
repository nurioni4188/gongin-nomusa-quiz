#!/usr/bin/env node
import fs from "node:fs";
const m=JSON.parse(fs.readFileSync("data/rc29-integrated-1020.json","utf8"));
const technical=JSON.parse(fs.readFileSync("rc29-evidence/rc29-1020-technical-ci.json","utf8"));
const v=JSON.parse(fs.readFileSync("vercel.json","utf8"));
const hold=m.summary.releaseGate==="HOLD"&&m.summary.scoringApproved===0&&m.summary.independentlyVerified===0&&!m.summary.vercelDeploymentPerformed&&v.git?.deploymentEnabled===false;
const out={schema:"rc29-release-hold-v1",technicalCI:technical.status,releaseDecision:hold?"HOLD":"INVALID",officialExamContentApproved:false,gradingEnabled:false,previewDeploymentApproved:false,productionDeploymentApproved:false};
fs.writeFileSync("rc29-evidence/rc29-release-hold.json",JSON.stringify(out,null,2)+"\n");console.log(JSON.stringify(out,null,2));
if(!hold||technical.status!=="PASS")process.exitCode=2;
