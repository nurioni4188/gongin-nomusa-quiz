import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
import path from "node:path";

const html = readFileSync("second/index.html", "utf8");
const scripts = [...html.matchAll(/<script src="([^"]+)"/g)].map(match => match[1]);
const context = { window: {}, console };
const read = name => readFileSync(path.join("second", name), "utf8");
let original;

for (const script of scripts) {
  if (script === "essay-app.js") break;
  if (script === "nomusa-auto-source.js") {
    original = JSON.parse(JSON.stringify(context.window.N27_CATALOG.items));
  }
  runInNewContext(read(script), context, { filename: script });
}

assert.ok(original, "Baseline catalog was captured before historical imports");
const rows = context.window.N27_CATALOG.items;
const { historical, reconciled2013, sources } = context.window.NOMUSA_AUTO_SOURCE;
const byId = new Map(rows.map(row => [row.id, row]));
assert.equal(byId.size, rows.length, "Catalog IDs must be unique");
assert.equal(rows.length, original.length + historical.length);
assert.deepEqual([...new Set(rows.map(row => row.year))].sort(), Array.from({ length: 20 }, (_, n) => 2007 + n));
assert.equal(new Set(historical.map(q => [q.year, q.subjectCode, q.number].join("/"))).size, historical.length);

for (const row of original) {
  const current = JSON.parse(JSON.stringify(byId.get(row.id)));
  delete current.historicalSource;
  assert.deepEqual(current, row, row.id);
}
for (const q of historical) {
  assert.match(q.id, /^nomusa-auto-20(?:0[7-9]|1[0-2])-[a-z0-9]+-q[1-9]$/);
  const row = byId.get(q.id);
  assert.equal(row.approved, false);
  assert.equal(row.answerStatus, "HOLD");
  assert.equal(row.sourceOnly, false);
  if (row.studyPilot) {
    assert.ok(row.sections.length >= (q.subquestions.length || 2));
    assert.ok(row.studyPilot.evidence.every(entry => entry.url.startsWith('https://')));
  } else {
    assert.equal(row.sections.length, q.subquestions.length || 1);
  }
  for (const section of row.sections) {
    assert.ok(section.detailed.trim(), q.id);
    assert.ok(section.compressed.trim(), q.id);
  }
  assert.equal(q.page, null);
  assert.equal(q.pageStatus, "HOLD");
}
for (const entry of reconciled2013) {
  assert.equal(byId.get(entry.id).pdfPage, entry.page);
  assert.ok(entry.questions.every(q => q.page === entry.page));
}
for (const q of [...historical, ...reconciled2013.flatMap(entry => entry.questions)]) {
  assert.ok(q.lines[0] > 0 && q.lines[1] <= sources.find(source => source.year === q.year).textLines);
  assert.ok(q.points > 0, JSON.stringify([q.year, q.subject, q.number]));
  assert.equal(q.visualStatus, "HOLD");
  assert.equal(new Set(q.subquestions.map(part => part.number)).size, q.subquestions.length);
  if (q.subquestions.length) {
    assert.ok(q.subquestions.every(part => part.points > 0));
    assert.equal(q.points, q.subquestions.reduce((sum, part) => sum + part.points, 0), q.text);
  }
}
assert.match(read("essay-app.js"), /const sk='nomusa_rc27_v103_essay_records_v1'/);
assert.equal(JSON.parse(readFileSync("vercel.json", "utf8")).git.deploymentEnabled, false);
console.log(JSON.stringify({ status: "PASS", existing: original.length, added: historical.length, mapped2013: reconciled2013.length, years: 20 }));
