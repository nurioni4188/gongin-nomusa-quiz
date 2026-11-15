#!/usr/bin/env node
// Offline gate for authored 2013/14 split answers (no deploy, no network).
// Usage: node scripts/nomusa-2013-2014-answers-gate.mjs [--write]
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';

const BASE_COMMIT = '929a2e40ee348bbb9833e7a26cd58e3479ead64e';
const PROTECTED = [
  'rc27_essay_catalog.js',
  'second/archive_2013_2021.js',
  'second/legacy_2007_2012_source_only.js',
  'second/historical-2013-2014-38.js',
  'second/legacy-181-answer-drafts-v1110.js',
  'review/NOMUSA_SECOND_2013_2014_38_AND_181_LEDGER_20261115.json',
  'review/NOMUSA_SECOND_181_AUTO_DRAFTS_V1110_20261115.json',
  'scripts/nomusa_split_38_181.py',
];
// One record per answers version so earlier batch results are preserved.
const outFile = version => `review/NOMUSA_SECOND_2013_2014_ANSWERS_${version}_GATE.json`;
const sha = text => crypto.createHash('sha256').update(text, 'utf8').digest('hex');
const errors = [];
const check = (ok, message) => { if (!ok) errors.push(message); };

const context = vm.createContext({ window: {} });
for (const file of [
  'rc27_essay_catalog.js', 'second/archive_2013_2021.js', 'second/legacy_2007_2012_source_only.js',
  'second/historical-2013-2014-38.js', 'second/legacy-181-answer-drafts-v1110.js',
  'second/historical-2013-2014-answers-v1.js',
]) vm.runInContext(fs.readFileSync(file, 'utf8'), context, { filename: file });
const w = context.window;

const catalog = w.N27_CATALOG.items;
const split = w.NOMUSA_2013_2014_SPLIT_V1.items;
const answers = w.NOMUSA_2013_2014_ANSWERS_V1;
check(catalog.length === 309, `catalog ${catalog.length} != 309`);
check(catalog.filter(r => r.sourceOnly).length === 181, '181 source-only parents changed');
check(split.length === 38, `split ${split.length} != 38`);
check(w.NOMUSA_LEGACY_181_DRAFTS.stats.target === 181, '181 draft registry target changed');
check(!Object.keys(answers.items).some(id => id in w.NOMUSA_LEGACY_181_DRAFTS.items), 'answer ID collides with 181 registry');

const splitById = new Map(split.map(r => [r.id, r]));
const report = [];
for (const [id, a] of Object.entries(answers.items)) {
  const src = splitById.get(id);
  check(Boolean(src), `${id}: not one of the 38 split IDs`);
  if (!src) continue;
  check(a.parentId === src.parentId && a.points === src.points && a.year === src.year &&
    a.subject === src.subject && a.questionNo === src.questionNo, `${id}: metadata mismatch with split source`);
  check(a.scoringApproved === false && a.verifiedForScoring === false, `${id}: scoring flag must stay false`);
  check(a.citationReview === 'HOLD', `${id}: citation review must stay HOLD`);
  check(a.sections.length >= 4 && a.sections.every(s => s.title && s.detailed.length > 80 && s.compressed.length > 20),
    `${id}: each section needs detailed and compressed text`);
  check(a.keywords333.length === 3 && a.keywords333.every(g => g.length === 3 && g.every(k => k.trim())), `${id}: 3·3·3 keywords`);
  check(a.reviewChecklist.length >= 5, `${id}: review checklist`);
  const allocated = (a.allocation || []).reduce((n, x) => n + Number(x.points), 0);
  check(allocated === a.points && a.allocation.every(x => x.part && x.sheets), `${id}: allocation ${allocated} != ${a.points}`);
  check(Array.isArray(a.citations) && a.citations.length > 0 &&
    a.citations.every(c => c.cite && ['SECONDARY_DB_MATCHED', 'HOLD'].includes(c.status)), `${id}: citations need status`);
  // Every sub-question score stated in the answer must appear in the original split text.
  for (const sub of a.subQuestions) {
    const m = sub.match(/\((\d+)점\)/);
    check(Boolean(m) && src.sourceText.replace(/\s/g, '').includes(`(${m[1]}점)`), `${id}: sub-question points "${sub}" not in source`);
  }
  const detailedChars = a.sections.reduce((n, s) => n + Array.from(s.detailed).length, 0);
  // 50 points ~ 8-10 answer sheets, 25 points ~ 4 sheets.
  const minimum = a.points === 50 ? 4000 : 2000;
  check(detailedChars >= minimum, `${id}: detailed answer ${detailedChars} chars < ${minimum}`);
  report.push({
    id, parentId: a.parentId, subject: a.subject, points: a.points,
    sourceTextSha256: sha(src.sourceText), detailedChars,
    compressedChars: a.sections.reduce((n, s) => n + Array.from(s.compressed).length, 0),
    sections: a.sections.length, allocation: a.allocation, keywords333: a.keywords333,
    citations: a.citations, references: a.academicOrLawReferences.length,
    citationReview: 'HOLD', scoringApproved: false,
  });
}
check(report.length === answers.stats.authored, 'stats.authored mismatch');

const preserved = PROTECTED.map(file => {
  let unchanged = false;
  try { execFileSync('git', ['diff', '--quiet', BASE_COMMIT, '--', file]); unchanged = true; } catch { unchanged = false; }
  check(unchanged, `${file}: changed since ${BASE_COMMIT.slice(0, 7)}`);
  return { file, unchangedSinceBase: unchanged, sha256: sha(fs.readFileSync(file, 'utf8')) };
});

const result = {
  schema: 'nomusa-2013-2014-answers-gate/1',
  version: answers.version,
  baseCommit: BASE_COMMIT,
  status: errors.length ? 'HOLD' : 'PASS',
  counts: { catalog: catalog.length, legacy181: 181, split38: split.length, authored: report.length, remaining: 38 - report.length },
  answers: report,
  preserved,
  errors,
  contentApproval: 'HOLD — case numbers and statutory text require independent check against official sources',
  scoringApproved: 0,
  deployment: 'NOT_DEPLOYED (review branch only; main, Production, RC35, existing Preview untouched)',
};
if (process.argv.includes('--write')) fs.writeFileSync(outFile(answers.version), JSON.stringify(result, null, 2) + '\n', 'utf8');
console.log(JSON.stringify(result, null, 2));
process.exit(errors.length ? 1 : 0);
