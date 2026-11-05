#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
const root=process.cwd();
const evidence=path.join(root,"rc28-evidence");
fs.mkdirSync(evidence,{recursive:true});
function load(p){
  try{return JSON.parse(fs.readFileSync(path.join(root,p),"utf8"))}
  catch(e){return {status:"MISSING",error:String(e.message||e)}}
}
const base=load("docs/rc28-baseline.json");
const audit=load("rc28-evidence/question-audit.json");
const browser=load("rc28-evidence/browser-smoke.json");
const devGuard=load("vercel.json");
const guardActive=devGuard.git?.deploymentEnabled===false;
const result={
 schema:"rc28-release-gate-v1",
 branch:"rc28/offline-ci-hold",
 baselineMainSha:base.protectedMainSha||null,
 verification:{questionAudit:audit.status,browserSmoke:browser.status,branchAutoDeploySuppressed:guardActive},
 status:audit.status==="PASS"&&browser.status==="PASS"&&guardActive?"PASS_CANDIDATE":"HOLD",
 releasePolicy:"No Vercel CLI/API calls are made by RC28 validation CI. One manual preview only AFTER all checks PASS and explicit user approval.",
 automaticVercelDeployment:false,manualPreviewAuthorized:false,productionAuthorized:false
};
fs.writeFileSync(path.join(evidence,"release-gate.json"),JSON.stringify(result,null,2)+"\n");
console.log(JSON.stringify(result,null,2));
if(result.status!=="PASS_CANDIDATE")process.exitCode=2;
