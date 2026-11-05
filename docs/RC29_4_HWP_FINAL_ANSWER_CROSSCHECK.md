# RC29.4 — 2023 Final Answer HWP Image Table Crosscheck (HOLD)

## What was actually verified
The user-provided 2023 1st-stage exam final-answer HWP (HWP5/OLE) was opened at the binary level. Its two `BIN0001.bmp` and `BIN0002.bmp` streams are raw-DEFLATE encoded BMP images. Both were extracted successfully and inspected visually. They contain six subject answer tables, each 25 rows of numbered answers: 150 answer labels. Visual transcription of the tables agrees with the pre-existing RC17 reference answer labels 150/150, discrepancy 0.

- Source HWP SHA256: `3648842dc21edad047a60f4409111c6fdf8314ed13d0556933f8499d0c2d1e74`
- Official Q-Net notice: https://www.q-net.or.kr/cst003.do?artlSeq=5211969&boardId=Q004&gId=05&gSite=L&id=cst00302
- The Q-Net notice lists the same HWP filename; the original HWP downloaded directly from Q-Net has **not** been hashed and byte-compared to the user upload. Do not claim independent authenticity check.
- Only answer-image reference values have been crosschecked, not A-booklet question text integrity or exact answer-to-booklet compatibility.

## Still blocked (2023)
- OCR draft available for 112/150 items, **not verified**. 38/150 have no OCR transcription; no new OCR was run in this step.
- No 2023 question stem + 5 choices has obtained documented visual signoff. All 150 scoring-approval statuses remain `false`.
- Original scanned question pages, formulae, tables and images must be independently reviewed, and actual Android device test must be completed.
- 2023 source HWP image-table reference is stored as `officialAnswerLabelReference` only; no `answer` or `acceptedAnswers` values are assigned to the working question bank.
- Global RC29 release gate remains **HOLD**. No Vercel CLI, API, deployment, main, RC27 or project changes.

## Deliverable not published to GitHub
Private offline evidence package `RC29_4_2023_HWP_150문항_정답교차검수.zip` contains the self-contained mobile review HTML with scanned question pages and the two extracted HWP answer images, 150-row crosswalk CSV/JSON, priority 38 OCR-missing list, browser QA and README. Original scanned page images are not copied to public GitHub.

## Reproducibility
Run `node scripts/rc29-4-answer-table-check.mjs` to validate 150 rows, six subjects, no duplicate keys, answer label range, source hash metadata and scoring HOLD policy. CI does **not** have the uploaded HWP/PDF originals; this validates the staged reference data only.
