#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";
import { gzipSync } from "node:zlib";
import { runInNewContext } from "node:vm";

const [output, ...sources] = process.argv.slice(2);
const seen = new Set();
const rows = sources.flatMap(source => {
  const window = {};
  runInNewContext(readFileSync(source, "utf8"), { window }, { timeout: 3000 });
  const [bank] = Object.values(window);
  if (!Array.isArray(bank)) throw new Error(`Invalid bank ${source}`);
  return bank.map(q => {
    if (!/^legacy1-20\d{2}-A-[a-z0-9]+-\d{3}$/.test(q.k) || seen.has(q.k) ||
        q.o.length !== 5 || !q.a.length || q.a.some(n => !Number.isInteger(n) || n < 1 || n > 5)) {
      throw new Error(`Invalid or repeated question ${q.k}`);
    }
    seen.add(q.k);
    return q;
  });
});
const compressed = gzipSync(JSON.stringify(rows), { level: 9 }).toString("base64");
writeFileSync(output, `window.NOMUSA_FIRST_BATCH_PACK = "${compressed}";\n`);
console.log(JSON.stringify({ count: rows.length, years: [...new Set(rows.map(q => q.y))] }));
