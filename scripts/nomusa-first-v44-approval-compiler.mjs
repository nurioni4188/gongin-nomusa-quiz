#!/usr/bin/env node
/**
 * V44 fail-closed importer.
 * Inputs: 103+686 V43/V46 source queues, source-controlled explicitly reviewed
 * approval manifest, original PDF/answer SHA evidence, and existing 3400-key ledger.
 * OCR, image presence, or an official answer candidate ALONE can never approve.
 * Only complete, independently reviewed source + official key + explanation items
 * become new source-bounded learning questions, staged under review branch only.
 */
import {readFileSync, writeFileSync, existsSync, mkdirSync} from "node:fs";
import {resolve, dirname} from "node:path";
import {createHash} from "node:crypto";
import {runInNewContext} from "node:vm";
const ROOT=resolve(process.argv[2]||".");
const read=p=>JSON.parse(readFileSync(resolve(ROOT,p),"utf8"));
const sha=p=>createHash("sha256").update(readFileSync(resolve(ROOT,p))).digest("hex");
const assert=(condition,message)=>{if(!condition)throw Error("HOLD_V44_"+message)};
const reviewed=read("review/NOMUSA_FIRST_V44_VERIFIED_APPROVALS.json");
const v43=read("review-artifacts/NOMUSA_FIRST_V43/NOMUSA_FIRST_V43_SOURCE_REVIEW.json");
const v46=read("review-artifacts/NOMUSA_FIRST_V46/NOMUSA_FIRST_V46_SOURCE_REVIEW.json");
const v34=read("review-artifacts/NOMUSA_FIRST_V34/NOMUSA_FIRST_V34_791_SOURCE_TARGETS.json");
const six=read("review-artifacts/NOMUSA_FIRST_V42_OFFICIAL/six-source-sha-manifest.json");
assert(reviewed.schema==="NOMUSA_FIRST_V44_EXPLICIT_SOURCE_APPROVALS/1","APPROVAL_SCHEMA");
assert(Array.isArray(reviewed.approvals),"APPROVAL_ARRAY");
assert(v43.targetCount===103 && v43.rows.length===103,"V43_103");
assert(v46.targetCount===686 && v46.rows.length===686,"V46_686");
assert(v34.summary.totalTargets===791,"V34_791");
assert(six.officialSHA256Validated===6 && six.pdfs.length===6,"SIX_OFFICIAL_PDFS_SHA");
const allowed=new Map([...v43.rows,...v46.rows].map(x=>[x.id,x]));
assert(allowed.size===789,"UNIQUE_789_NO_DUPLICATES");
const legacy=new Set(v34.rows.map(x=>x.id));
assert(legacy.size===791,"BASE_LEGACY_791");
const pilot=new Set(["legacy1-2020-A-management-101","legacy1-2021-A-management-110"]);
assert([...pilot].every(id=>legacy.has(id)&&!allowed.has(id)),"TWO_PILOT_PRESERVED");
assert([...allowed.keys()].every(id=>legacy.has(id)),"NO_EXTRA_TARGETS");
const proofContext={window:{}};
for(const f of ["study-hub/legacy-first-answer-review.js",
"study-hub/legacy-first-v2-staged.js",
"study-hub/legacy-first-v4-2014-2021-review.js",
"study-hub/legacy-first-v5-correction.js",
"study-hub/legacy-first-v61-sources.js"]){
  runInNewContext(readFileSync(resolve(ROOT,f),"utf8"),proofContext,{filename:f,timeout:15000});
}
const keys=new Map(proofContext.window.NOMUSA_FIRST_LEGACY_V5.records
  .filter(q=>q.type==="A").map(q=>[q.id,Array.from(q.answers)]));
const answerSources=proofContext.window.NOMUSA_FIRST_V61_SOURCES.answerDocuments;
const pdfSources=new Map(six.pdfs.map(x=>[x.sha256,x]));
const old2013plus=read("review/NOMUSA_FIRST_V41_103_CROP_SHA_20261118.json");
assert(old2013plus.files.length===103,"V41_ASSETS_103");
const imgHash=new Map(old2013plus.files.map(x=>[x.id,x.jpegSHA256]));
const repairs=read("review/NOMUSA_FIRST_V42_FOUR_MANUAL_CROP_REPAIRS_20261118.json");
for(const row of repairs.records)imgHash.set(row.id,row.sha256);
const ids=new Set(), imported=[],explanations={};
const legal=new Set(["노동법(1)","노동법(2)","민법","사회보험법"]);
const subjects={"labor1":"노동법(1)","labor2":"노동법(2)",
  "civil":"민법","social":"사회보험법","economics":"경제학원론",
  "management":"경영학개론"};
const long=s=>typeof s==="string"&&s.trim().length>=12;
const safeUri=s=>{try{let u=new URL(s);return u.protocol==="https:" &&
 ["q-net.or.kr","www.q-net.or.kr","law.go.kr","www.law.go.kr",
  "openstax.org","www.openstax.org","doi.org","www.doi.org",
  "pubmed.ncbi.nlm.nih.gov","scholar.google.com","hbr.org","www.hbr.org",
  "garfield.library.upenn.edu"].includes(u.hostname)}catch{return false}};
for(const entry of reviewed.approvals){
 const id=entry?.id;
 assert(typeof id==="string"&&!ids.has(id)&&allowed.has(id),"UNKNOWN_DUPLICATE_ID_"+id);
 ids.add(id);
 const record=allowed.get(id);
 const match=/^legacy1-(20\d{2})-A-(labor1|labor2|civil|social|economics|management)-(\d{3})$/.exec(id);
 assert(!!match,"BAD_ID_"+id);
 const official=match[1]+"-AB";
 const originalSource=record.originalSourceImage;
 assert(!!originalSource && originalSource.origin!=="V40_UNTRIAGED_NUMBER_ANCHOR_HOLD","IMAGE_NOT_VISUALLY_TRIAGED_"+id);
 const image=entry.image;
 assert(typeof image==="string"&&/^review\/first-v4[12]-[\w-]+\/legacy1-20\d{2}-A-[\w-]+-\d{3}\.jpg$/.test(image),"IMAGE_PATH_"+id);
 assert(existsSync(resolve(ROOT,image)) && sha(image)===entry.imageSHA256 && imgHash.get(id)===entry.imageSHA256,
  "CROP_SHA_NOT_FROM_V41_V42_"+id);
 assert(entry.sourcePdfSHA256===originalSource.officialPdfSHA256 &&
        pdfSources.has(entry.sourcePdfSHA256),"QNET_OFFICIAL_SOURCE_SHA_"+id);
 const keyDoc=answerSources[official];
 assert(!!keyDoc && pdfSources.has(keyDoc.sha256) &&
 entry.officialAnswerPdfSHA256===keyDoc.sha256 &&
 entry.officialAnswerPage===(Number(match[1])===2020?1:1),
 "OFFICIAL_ANSWER_SHEET_SHA_"+id);
 assert(entry.sourcePdfPage===originalSource.pdfPage &&
 Number.isInteger(entry.sourcePdfPage),"ORIGINAL_NUMBER_AND_PAGE_"+id);
 const options=entry.options,correct=entry.correct;
 assert(long(entry.question)&&Array.isArray(options)&&options.length===5 &&
  options.every(z=>typeof z==='string'&&z.trim().length>=2) && new Set(options).size===5,"FULL_STEM_FIVE_DISTINCT_OPTIONS_"+id);
 assert(Array.isArray(correct)&&correct.length>=1&&correct.length<=5&&
 correct.every(x=>Number.isInteger(x)&&x>=1&&x<=5)&&
 JSON.stringify([...correct].sort())===JSON.stringify([...keys.get(id)].sort()),
 "OFFICIAL_KEY_V5_MISMATCH_"+id);
 const flags=entry.visualReview||{};
 assert(["fullStem","fiveOptions","equationsAndGraphics","cropBoundary","correctExamForm",
         "sourcePageManuallyCompared"].every(x=>flags[x]===true),
 "SOURCE_PAGE_VISUAL_CROSSCHECK_REQUIRED_"+id);
 assert(entry.manualOfficialKeyComparison===true && entry.manualAnswerGridCell===correct.join(",") &&
        long(entry.answerGridExplanation),"FINAL_KEY_CELL_VISUAL_CROSSCHECK_REQUIRED_"+id);
 const authors=entry.reviewer||{};
 assert(typeof authors.primaryReviewer==='string'&&authors.primaryReviewer.trim().length>=2&&typeof authors.independentReviewer==='string'&&authors.independentReviewer.trim().length>=2&&
 authors.primaryReviewer!==authors.independentReviewer &&
 /^\d{4}-\d\d-\d\d$/.test(authors.reviewDate||"") &&
 long(authors.reviewEvidence),"TWO_REVIEWER_SIGNOFF_MISSING_"+id);
 assert(entry.approvedForLearningScoring===true,"FINAL_REVIEW_EXPLICIT_APPROVAL_REQUIRED_"+id);
 const ex=entry.explanation||{};
 assert(long(ex.summary)&&long(ex.mnemonic)&&Array.isArray(ex.options)&&ex.options.length===5 &&
   ex.options.every(long) && Array.isArray(ex.sources)&&ex.sources.length>0 &&
   ex.sources.every(s=>long(s.title)&&safeUri(s.url)&&long(s.basis)),
   "FIVE_OPTION_EXPLANATIONS_AND_SOURCES_REQUIRED_"+id);
 if(legal.has(subjects[match[2]])){
   assert(entry.examDateLegalReview?.examVersionMatched===true &&
   long(entry.examDateLegalReview.lawArticles)&&
   long(entry.examDateLegalReview.amendmentProvisions) &&
   long(entry.examDateLegalReview.legalReasoning) &&
   /^\d{4}-\d\d-\d\d$/.test(entry.examDateLegalReview.examDate||""),
   "LAW_EXAM_DATE_AMENDMENTS_NOT_VERIFIED_"+id);
 }else{
   assert(long(entry.academicReview?.title)&&
    Number.isInteger(entry.academicReview.publicationYear)&&
    long(entry.academicReview.theoryOrCalculationProof) &&
    entry.academicReview.formulasVerified===true,
    "ACADEMIC_OR_MATH_PROOF_REQUIRED_"+id);
 }
 const [_,year,code,questionNo]=match;
 const q={
   k:id,y:Number(year),r:Number(year)-1991,form:"A",
   s:subjects[code],n:Number(questionNo),q:entry.question.trim(),
   o:options,a:correct,t:true,
   sourceUrl:record.officialQuestionSource?.split("#")[0],
   pg:[entry.sourcePdfPage],answerSourceUrl:keyDoc.notice,
   sourceReviewStatus:"V44_VERIFIED_FULL_ORIGINAL_OFFICIAL_FINAL_KEY_AND_EXPLANATION",
   sourcePDFSHA256:entry.sourcePdfSHA256,
   finalAnswerPDFSHA256:entry.officialAnswerPdfSHA256,
   paperHtml:'<figure style="margin:0"><img src="'+image+
    '" style="display:block;width:100%;height:auto" alt="Q-Net '+year+
    ' A형 '+Number(questionNo)+'번 공식 문제지 원문 이미지">'+
    '<figcaption>한국산업인력공단 Q-Net 원본 · V44 이중 원문 대조</figcaption></figure>'
 };
 imported.push(q);
 explanations[id]={
   question:q.q,correct:[...correct],optionTexts:[...options],
   summary:ex.summary,options:ex.options,mnemonic:ex.mnemonic,
   sources:ex.sources,validationStatus:"PASS_QNET_ORIGINAL_FINAL_KEY_THEORY_CHECKED",
   qualityFlags:["OFFICIAL_FULL_TEXT_AND_FIVE_OPTIONS_APPROVED",
    "SOURCE_IMAGE_HASH_VALIDATED","OFFICIAL_FINAL_ANSWER_GRID_HUMAN_CHECKED",
    "EXPLANATION_SOURCES_CHECKED","TWO_REVIEWER_APPROVAL"]
 };
}
assert(imported.length<=103,"BATCH_LIMIT_103");
const dest=resolve(ROOT,"study-hub/first-v44-approved.js");
const header="/* V44 generated from verified approval manifest only. NEVER OCR auto-approved. */\n";
let module=header+"(function(){'use strict';\n"+
"const rows="+JSON.stringify(imported)+";\n"+
"const explanations="+JSON.stringify(explanations)+";\n"+
"const bank=window.NOMUSA_V108_EXPLANATIONS;\n"+
"if(!bank||!bank.entries)throw Error('V44_REQUIRES_EXPLANATION_BANK');\n"+
"for(const [id,ex] of Object.entries(explanations)){if(bank.entries[id])throw Error('V44_EXPLANATION_DUPLICATE_'+id);bank.entries[id]=Object.freeze(ex)}\n"+
"window.NOMUSA_FIRST_V44_APPROVED=Object.freeze(rows.map(x=>Object.freeze(x)));\n"+
"window.NOMUSA_FIRST_V44_SCORING_IDS=Object.freeze(rows.map(x=>x.k));\n"+
"window.NOMUSA_FIRST_V44_GATE=Object.freeze({verified:rows.length,reviewRequired:789-rows.length,source:'V43_V46_MANIFEST_WITH_DOUBLE_REVIEWER',noOCRPromotions:true});\n"+
"})();\n";
writeFileSync(dest,module,"utf8");
const out=resolve(ROOT,"review-artifacts/NOMUSA_FIRST_V44");
mkdirSync(out,{recursive:true});
writeFileSync(resolve(out,"NOMUSA_FIRST_V44_PROMOTION_GATE.json"),
 JSON.stringify({schema:"NOMUSA_FIRST_V44_PROMOTION_GATE/1",
  status:"PASS_VERIFICATION_ENGINE_WITH_"+imported.length+"_APPROVED_ITEMS",
  initialBaseBank:2281,initialMissing:789,
  actualNewVerifiableApprovals:imported.length,
  expectedBankTotal:2281+imported.length,
  remainingUnapprovedOriginals:789-imported.length,
  approvedIDs:imported.map(q=>q.k),unapprovedCandidatesHeld:789-imported.length,
  pilotV42StillApproved:2,mainAndProduction:"UNMODIFIED",preview:"NOT_DEPLOYED"},null,2)+"\n");
console.log(JSON.stringify({status:"PASS_SAFE_APPROVAL_GATE",
  verified:imported.length,remaining:789-imported.length,
  totalExistingPlusApproved:2281+imported.length,sourceScript:"study-hub/first-v44-approved.js"}));
