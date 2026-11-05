# RC29 2022–2026 305 extra PDF question stems & five-choice ingestion

The user supplied **seven** exam PDFs, including an additional 2022 management reference. Six previously missing source PDFs were inspected locally and matched exactly the expected 305 question ID slots: 2022 economics 25; 2024 labor law(1)/(2) 80 and economics 40; 2025 labor law(1)/(2) 80 and economics 40; 2026 economics 40.

All 305 question identifiers, question stems and five option markers were extracted locally from the PDFs with pdfplumber. The private ZIP contains full texts, the six original PDF bytes, 1020 integrated review JSON, offline responsive review HTML, PDF page preview JPGs, and Windows UTF-8 one-shot rerun script.

**Known blockers**: 47 economics questions contain PDF private-use font glyphs for equations, so some extracted expressions are unreadable and MUST be visually checked against source page images. Two 2025 economics questions span PDF pages. 2025 labor law(1) Q5 has an article clause marker ① within its stem distinct from answer option ①. The 2023 existing 59 first-pass drafts + 91 raw OCR candidates still require independent verification. Official A-type final answer verification and scoring approval remain 0.

Public repository contains only source-free `data/rc29-current-1020-source-state.json`, integrity checker and audit documentation. The original historical `data/rc29-integrated-1020.json` that once listed 305 sources as missing is intentionally retained as an immutable historical snapshot; it is now superseded by the current-state file.

Tests run **locally on private user-provided PDF bytes**, not in GitHub CI: 14/14 contract checks, 4/4 Chromium PC/tablet/mobile viewport simulations, original PDF SHA256 checks, ZIP integrity PASS. GitHub Actions only checks manifest metadata, NOT the PDF text itself; its technical CI PASS does not certify official exam answer accuracy.

Vercel deployments forbidden; main and RC27 unchanged. **HOLD scoring / Preview / Production.**

Private artifact title: `RC29_2022-2026_1020문항_305원본추가_통합검수.zip`.
