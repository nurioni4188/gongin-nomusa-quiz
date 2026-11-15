#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { createContext, runInContext } from 'node:vm';

const root = resolve(process.argv[2] ?? '.');
const sandbox = createContext({ window: {} });
const layers = [
  'legacy-first-answer-review.js',
  'legacy-first-v2-staged.js',
  'legacy-first-v4-2014-2021-review.js',
  'legacy-first-v5-correction.js',
];
for (const layer of layers) {
  runInContext(readFileSync(resolve(root, 'study-hub', layer), 'utf8'), sandbox, {
    filename: layer,
    timeout: 4000,
  });
}

const { NOMUSA_FIRST_LEGACY_V4: v4, NOMUSA_FIRST_LEGACY_V5: v5 } = sandbox.window;
const key = ({ year, type, subject, questionNo }) => [year, type, subject, questionNo].join('|');
const records = new Map(v5.records.map((row) => [key(row), row]));
const report = {
  records: v5.records.length,
  uniqueKeys: records.size,
  uniqueIds: new Set(v5.records.map(({ id }) => id)).size,
  pendingApproval: v5.records.filter((row) =>
    (row.approval ?? row.validation ?? row.status)?.includes('HOLD')).length,
  groups: {},
  issues: [],
};

for (const [id, row] of records) {
  const group = [row.year, row.type, row.subject].join('|');
  (report.groups[group] ??= []).push(row.questionNo);
  if (!/^[AB]$/.test(row.type) || !Number.isInteger(row.questionNo) ||
      row.questionNo < 1 || row.questionNo > 125 ||
      !/^legacy1-\d{4}-[AB]-[a-z0-9]+-\d{3}$/.test(row.id)) {
    report.issues.push({ id, issue: 'INVALID_RECORD_IDENTITY' });
  }
  if (!Array.isArray(row.answers) || !row.answers.length ||
      row.answers.some((choice) => !Number.isInteger(choice) || choice < 1 || choice > 5) ||
      new Set(row.answers).size !== row.answers.length) {
    report.issues.push({ id, issue: 'INVALID_ANSWER_VALUES' });
  }
}

const subjects = ['노동법Ⅰ', '노동법Ⅱ', '민법', '사회보험법', '경제학원론', '경영학개론'];
for (const year of [2014, 2020, 2021]) {
  for (const type of ['A', 'B']) {
    for (const [index, subject] of subjects.entries()) {
      const group = [year, type, subject].join('|');
      const numbers = report.groups[group] ?? [];
      const start = 1 + 25 * Math.min(index, 4);
      const missing = Array.from({ length: 25 }, (_, offset) => start + offset)
        .filter((number) => !numbers.includes(number));
      if (missing.length || numbers.length !== 25) {
        report.issues.push({ group, missing, actual: numbers.length });
      }
    }
  }
}

const rechecks = readFileSync(
  resolve(root, 'review/NOMUSA_FIRST_V5_127_SOURCE_RECHECK_20261115.csv'), 'utf8',
).trim().split(/\r?\n/).slice(1);
const recheckKeys = new Set();
report.recheckTypes = {};
for (const line of rechecks) {
  const fields = [...line.matchAll(/(?:^|,)(?:"([^"]*)"|([^",]*))(?=,|$)/g)]
    .map((match) => match[1] ?? match[2]);
  if (fields.length !== 12) {
    report.issues.push({ issue: 'UNSUPPORTED_RECHECK_CSV_ROW' });
    continue;
  }
  const [year, type, subject, number, , , , , expected, technique] = fields;
  const id = [year, type, subject, number].join('|');
  if (recheckKeys.has(id)) report.issues.push({ id, issue: 'DUPLICATE_RECHECK' });
  recheckKeys.add(id);
  report.recheckTypes[technique] = (report.recheckTypes[technique] ?? 0) + 1;
  if (records.get(id)?.answers.join(',') !== expected) {
    report.issues.push({ id, issue: 'RECHECK_LEDGER_MISMATCH', expected, actual: records.get(id)?.answers });
  }
}
report.rechecks = recheckKeys.size;
report.changedAnswersFromV4 = v4.records.flatMap((row) => {
  const current = records.get(key(row));
  return row.answers.join('/') === current?.answers.join('/') ? [] : [
    { id: row.id, before: row.answers, after: current?.answers ?? null },
  ];
});
report.multiAnswerRecords = v5.records.filter((row) => row.answers.length > 1)
  .map(({ id, answers }) => ({ id, answers }));
report.groups = Object.fromEntries(Object.entries(report.groups)
  .map(([group, numbers]) => [group, numbers.length]));
runInContext(readFileSync(resolve(root, 'study-hub/legacy-first-v61-sources.js'), 'utf8'), sandbox);
const sources = sandbox.window.NOMUSA_FIRST_V61_SOURCES;
const sourceRows = new Map(v5.records.filter(({ year }) => [2014, 2020, 2021].includes(year))
  .map((row) => [row.id, row]));
for (const [id, item] of Object.entries(sources.records)) {
  const row = sourceRows.get(id);
  sourceRows.delete(id);
  const doc = sources.documents[item.source];
  const answer = sources.answerDocuments[item.answerSource];
  const expectedAnswer = row && `${row.year}-${row.year === 2014 ? row.type : 'AB'}`;
  if (!row || doc?.year !== row.year || doc?.form !== row.type ||
      (row.subject === '경제학원론' && doc.elective !== 'economics') ||
      (row.subject === '경영학개론' && doc.elective !== 'management') ||
      item.answerSource !== expectedAnswer || !answer ||
      item.answerPdfPage !== row.sourcePage ||
      (item.pdfPage != null && (item.pdfPage < 1 || item.pdfPage > doc.pdfPages))) {
    report.issues.push({ id, issue: 'SOURCE_JOIN_MISMATCH' });
  }
}
for (const id of sourceRows.keys()) report.issues.push({ id, issue: 'MISSING_SOURCE_JOIN' });
report.sourceLinks = {
  records: Object.keys(sources.records).length,
  booklets: Object.keys(sources.documents).length,
  answerPdfs: Object.keys(sources.answerDocuments).length,
  counts: sources.counts,
};
report.status = report.records === 3400 && report.uniqueIds === 3400 &&
  report.uniqueKeys === 3400 && report.rechecks === 127 &&
  report.pendingApproval === 3400 && !report.issues.length ? 'PASS_INTERNAL_CONSISTENCY' : 'HOLD';
console.log(JSON.stringify(report, null, 2));
if (report.status === 'HOLD') process.exitCode = 2;
