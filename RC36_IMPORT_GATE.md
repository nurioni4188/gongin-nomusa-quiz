# RC36 Preview law/AI — import gate

Status: **HOLD_SOURCE_IMPORT**. This branch was created from `rc29/question-bank-validation` as an isolated staging branch. It is **not** RC36 and must not be deployed as RC36 until the complete source is imported and verified.

## Required source

- Archive: `RC36_Nomusa_Law_AI_Explanation_FULL.zip`
- SHA-256: `584a179be7e1df598d4a964ffc08bcbbbac55bba607abd0acb89b5a6e3ea10cb`
- Archive root: `nomusa-quiz-web/`
- Files in archive: 1,092
- Required runtime files: `index.html`, `data.js`, `img/`, `api/health.js`, `api/law.js`, `api/explain.js`, `api/_lib/core.cjs`, `api/_data/questions.json`, `package.json`, `vercel.json`.

## Deployment gates

1. Import the **entire** contents of `nomusa-quiz-web/` at the repository root on this branch only.
2. Verify answer bank size 1,020, source asset and file hashes, offline regression tests, and absence of secrets or tokens.
3. Keep `EXPLANATION_ENABLED=false`; no automatic acceptance of AI explanations.
4. Keep Vercel Git auto-deployment disabled until source import and Production isolation are verified.
5. Connect existing Vercel project `gongin-nomusa-rc27-preview` only after isolating its Production branch; avoid deploying GitHub `main` accidentally.
6. Target Preview only. Do not alter `main`, Production, database, or official answer flags.

As of 2026-11-07: GitHub branch creation PASS; full source import HOLD; Git connection HOLD; Preview deployment HOLD.
