---
name: nomusa-auto
description: Integrate and verify Korean Certified Labor Attorney second-stage past exams in the NOMUSA study hub. Use when reconciling source files, historical questions, answer evidence, or study regressions.
---

# NOMUSA-AUTO V1.0

1. Confirm the repository, base branch, exact commit, and Vercel project with read-only queries. Check that Git-triggered deployments are disabled before pushing a review branch.
2. Inventory supplied files by year, round, subject and sitting. Compare duplicate uploads by SHA-256 when bytes are available. Record text matches as text matches. Flag conflicting headers and maintain source provenance.
3. Capture question and subquestion numbers, points with their basis, source page or extracted lines, and graph or formula prompts. Use HOLD for unrendered HWP pagination, unverified visual content, ambiguous subject splits, and unknown points.
4. Reconcile 2013 against its existing IDs and PDF pages. Append only older questions with stable namespaced IDs. Keep existing records and all storage key names. Keep new answer approvals false until the exam-date legal text and applicable judgments are checked.
5. Run `node scripts/verify-nomusa-auto.mjs` and `node scripts/verify-nomusa-auto-browser.mjs` from the repository root. Report browser PC and mobile results separately from source and legal evidence.
6. Submit a Draft PR against the source gate. Keep deployments pending explicit authorization. Report the actual commit SHA, coverage and HOLD reasons.
