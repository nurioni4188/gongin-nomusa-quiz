#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
const dir=path.join(process.cwd(),"rc29-evidence");fs.mkdirSync(dir,{recursive:true});
const read=name=>{try{return JSON.parse(fs.readFileSync(path.join(dir,name),"utf8"))}catch{return {status:"MISSING"}}};
const audit=read("question-audit.json"),browser=read("browser-test.json");
const v=JSON.parse(fs.readFileSync("vercel.json","utf8"));
const guard=v.git?.deploymentEnabled===false;
const gate={
 schema:"rc29-preview-gate-v1",
 scopeTarget:1020,
 checks:{yearlyScope:audit.expectedSlots===1020,officialAnswerReview:audit.verifiedUnique===1020,
  sourceQuality:audit.status,browserEmulation:browser.status,autoDeploymentDisabledInBranch:guard},
 status:audit.expectedSlots===1020&&audit.verifiedUnique===1020&&audit.status==="PASS"&&
  browser.status==="PASS"&&guard?"PASS_CANDIDATE":"HOLD",
 deploymentPerformed:false,productionApproved:false,manualPreviewApproved:false,
 policy:"Even PASS_CANDIDATE requires separate human approval for one manual Preview; never deploy automatically."
};
fs.writeFileSync(path.join(dir,"preview-approval-gate.json"),JSON.stringify(gate,null,2)+"\n");
console.log(JSON.stringify(gate,null,2));
if(gate.status!=="PASS_CANDIDATE")process.exitCode=2;
