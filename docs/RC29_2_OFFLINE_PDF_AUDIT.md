# RC29.2 original PDF text-layer review: HOLD

Inputs: user-uploaded 2022, 2024, 2025, and 2026 question PDFs; RC27 candidate ZIP; RC17 answer reference ZIP.
Candidate count 565; normalized exact stem AND all five options on cited PDF page: 443; text mismatches: 122.
2022 125 / 70; 2023 scanned source not transcribed; 2024 120 / 86; 2025 120 / 118; 2026 200 / 169.
RC17 holds 1020 A-type answer reference rows. These are unverified reference labels, NOT official approval for scoring.
All 565 question rows require visual source comparison and official final answer confirmation.
Candidate source pool is missing 455 slots relative to all 1020 expected questions; original main's 388 rows are a separate baseline.

## Offline reproducible check
Install pymupdf. Retain exact source PDF filenames in one folder.
Run: python scripts/rc29-2-pdf-reconcile.py --rc27 PATH_TO_RC27.zip --rc17 PATH_TO_RC17.zip --src-dir PATH_TO_SOURCE_PDFS
Outputs: rc29-evidence/rc29-2-local/source-summary.json, staged-unverified-565.json, all-source-checks.csv and priority-mismatch-checks.csv.
SHA256 mismatch stops the run rather than treating a different PDF as the original.
No OCR or network is used. 2023 scanned PDFs require visual review.

## CI and release
GitHub Actions runs only a static manifest-integrity audit because the source PDFs are not in the repository.
CI cannot claim it has rechecked the PDFs. The RC29 release gate remains HOLD until all official papers, answers, visuals, and mobile testing pass.
No Vercel deploy, project setting update, main branch change or RC27 alteration permitted.
