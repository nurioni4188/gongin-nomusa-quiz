---
name: nomusa-auto-v1
description: Safely intake and validate 2007-2026 Korean certified labor attorney exam source material for the existing RC27 study hub. Never deploy without approval.
---
# NOMUSA-AUTO V1.0 — 20-year second-stage integration

## Scope and immutable baseline
- Repository: `nurioni4188/gongin-nomusa-quiz`.
- Baseline branch: `preview/nomusa-v1107-source-gate-20261114`; baseline commit `966f59e205c406f33ebe3c4c70e4ebb2db88dab9`.
- Vercel: team `onnuri4188gmailcoms-projects`; project `gongin-nomusa-rc27-preview`.
- Preserve main, Production, existing Preview, RC27/RC35 screens, `index.html`, `second/index.html`, `study-hub/`, `review/`, `scripts/`, all original question IDs and storage keys.
- This is a repository workflow skill file, **not** a globally installed ChatGPT skill. Only claim installed/activated when separately verified.

## Mandatory order
1. Verify linked account, repository, target branch HEAD, and exact Vercel project. Stop if any mismatch.
2. Ingest uploaded 2007-2012 HWP5 originals with raw SHA-256 and format metadata. Store original files only in a separate, user-approved source branch; never claim the raw upload is already in GitHub.
3. Keep every source's year, subject, question number, subquestion number, point value, page, table/formula/graph reference, original filename and SHA. Use status `UNVERIFIED_SOURCE` unless line-by-line checked.
4. Handle 2013 as a boundary year: compare SHA and content against existing `source_pdf/2013/2013_second_full_original.pdf`. Reuse the original record if matching; never insert duplicate IDs.
5. Assign new IDs only in separate namespace `legacy2-{year}-{subjectSlug}-q{number}-s{subnumber}`. Do not renumber or rewrite any preexisting IDs or localStorage keys; collision = HOLD.
6. Build detailed and compressed answer drafts separately from the source records. Label law/judgment citations by **exam date** and keep unverified answers `HOLD`, not 'approved'.
7. Link validated question data into existing `second/` and `study-hub/` interfaces through additive code only. Preserve detailed answer → compressed answer → user writing → compare/review, progress, autosave, refresh restoration and JSON export/import.
8. Run `node scripts/v1107-source-gate.mjs .` and `node scripts/nomusa-auto-v1-20year-gate.mjs .`. A `HOLD` means not release-ready; do not interpret static PASS as content or browser PASS.
9. Run real browser PC and mobile 360/390 px E2E: load, choose year and subject, write answer, autosave, reload/restore, move between questions, review flag, export/import JSON, exam mode; inspect console errors, ID and storage-key migration.
10. Changes may go only to an isolated review branch and a **Draft PR** against the baseline preview branch. Do not merge without explicit user approval.
11. Preview deployment is prohibited until a separate approval; then deploy once to the EXISTING Vercel project and run real HTTPS E2E. Production and main require another explicit user approval.

## Audit
- Source ledger: `review/NOMUSA_AUTO_V1_20YEAR_SOURCE_MANIFEST.json`.
- Gate: `scripts/nomusa-auto-v1-20year-gate.mjs`.
- Report separately: source received, extracted, per-question mapped, validated, UI-integrated, browser E2E, PR, Preview, main, Production.
- Never report '20-year complete' from files alone. Stop with a concrete HOLD reason when blocked.
