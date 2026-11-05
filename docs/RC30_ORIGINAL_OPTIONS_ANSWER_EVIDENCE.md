# RC30 — Full 1,020 original/choices/final-answer-only validation

Private ZIP: RC30_1020문항_원본선택지정답_검증전용패키지.zip (~63MB). Windows entry point run_verify_only.cmd; no PowerShell signing change and no UI modifications.

Question-source verification technical buckets: 715 exact normalized same-source-page text candidates; 123 same-page mismatch/review; 2023 150 scanned OCR/first-pass pending; 32 present-source-PDF but choices/formulas not automatically structured. 897 have a nonempty stem and five options. Source PDF files physically present, missing 0. These statuses differ from another RC29 batch's text-layer extraction/figure-risk metrics; both reports are preserved.

All 1,020 A-form answer references mapped to original local PDF/HWP source SHA. 2022 150; 2023 HWP image reference 150 (previous); 2024 HWP embedded image first-pass 240; 2025 PDF first-pass 240; 2026 PDF first-pass 240. Compared 565 legacy reference answer labels and obtained 565 agreements, 0 disagreements; 305 had no prior legacy answer candidate. Multiple answer slots 2022 民法 51/72, 2024 労働法(2)43 and 2025 民法26 preserved in private ledger, NOT uploaded publicly.

Independently certified original question text+choices 0. Independently certified A-form official final answer 0. Public GitHub metadata CI only checks totals, cannot access originals, cannot certify truth of first-pass visual transcription, and must keep grading and release HOLD.

Correct next use: inspect issues queue, perform actual independent PDF/HWP image double review and issue signoffs separately before any grading unlock. Vercel deployment not performed; main and RC27 remain intact.
