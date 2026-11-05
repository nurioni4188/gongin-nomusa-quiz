# RC30 V2 1,020 original source + five choices + A-form answers source-page correction

Public metadata only; original exam PDFs, answer images, and transcribed stems/options remain **private in the conversation package**, not in the public GitHub repo.

Previous `SOURCE_MISSING` 32 is a **misleading state name**: local PDF originals exist for every year/subject, and the second independent PDF text-layer *parser* has located 32/32 numbered question page anchors. Of these 32, all five circled option markers can be extracted in a first-pass candidate, but 12 contain private-use math glyphs and none has a human visual review signoff. Record `SOURCE_PDF_PAGE_LOCATED_TEXT_DRAFT_UNVERIFIED`, never `VERIFIED_OFFICIAL_FINAL`.

Unchanged baseline slots: PDF same-page textual 715; text mismatches 123; year-2023 scan/OCR 150; previously unparsed 32. Distinct source PDF files: 13; 1,020 local answer source file hashes match prior references; **0 question or answer independent signoffs, 0 score unlocks**.

Private output bundle `RC30_V2_1020문항_원본선택지정답_일괄재검증.zip` (~2.8MB) contains 1,020 source/answer ledger, 305 priority-review queue, 32 page map, 32 extracted first-pass options, 21 JPEG source-page previews, offline review HTML, a Python verifier and Windows .cmd launcher. The 32 page map in GitHub is source-free metadata only.

QA nuance: comparison to a different PDF text extraction method may produce false negatives around line order, circled markers quoted within a question stem, and text-layer math glyphs. These are review signals, not proven errors. Never certify official text on a pure string match.

UI frozen; GitHub main and RC27 unchanged; Vercel deployment forbidden. Technical CI PASS is a metadata check, whereas official booklets/answers and actual grading release remain HOLD.
