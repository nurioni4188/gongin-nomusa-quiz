# V11.0.7 Source Reconciliation — Draft PR Review Gate

Date: 2026-11-14 KST. Scope: **source and deployment evidence only**. Do **not** merge or deploy.

## Requested target
- Existing repository: `nurioni4188/gongin-nomusa-quiz`.
- Existing Vercel team: `onnuri4188gmailcoms-projects`.
- Existing Vercel project: `gongin-nomusa-rc27-preview` (`prj_J1hv2uJ6EzuWEcYtb6x4GYKpXV0i`).
- No new project, no changes to `main`, Production, existing Preview, quiz IDs, saving keys, original legal answer texts.
- 47 legal draft answers stay **unapproved (0/47)**. The 18 corrections for 6 high-priority questions are **review-only**.

## Local full-source archive comparison (performed 2026-11-14)
- Reference ZIP: `NOMUSA_V1099_LEGAL_GATED_INTEGRATED_NOT_DEPLOYED.zip`
  - SHA256: `1821b25e23070712c92dcaf5f64bc3680d01d895d2b52bbcc7b624fdd0b47e32`
  - 1,184 regular files.
- V11.0.6 local candidate: `공인노무사_V1106_학습허브_읽기전용통합_전체소스_HOLD.zip`
  - SHA256: `13ee0ee12507b912ba08d55eac06a6cc2fe97e80b314cfb408a42ef1fb886bd4`
  - 1,192 regular files; ZIP CRC check PASS.
- Comparison: 1,182 unchanged, 2 modified (`study-hub/index.html`, `second/index.html`), 8 added, 0 removed.
- Added include read-only sidecar/bridge, JSON mapping, QA scripts and evidence.
- Original legal draft JS/JSON remains byte-identical to baseline. This does **not** constitute legal content approval.

## GitHub gap (HOLD_SOURCE_NOT_COMMITTED)
- Default `main`: 2 files.
- Existing recovery branch `preview/nomusa-v1097-hub-original-preserve`: 16 regular files (recovery assets), not the full V11.0.6 project.
- Git blob SHA-1 match (recovery branch vs V11.0.6 local archive): `study-hub/app.js`, `study-hub/app.css`, `study-hub/state.js`, `study-hub/brand.svg`, `study-hub/updates/explanations-v108.js` confirmed exact.
- `study-hub/index.html` intentionally differs because of V11.0.6 integration.
- **This Draft PR contains only source-integrity evidence and a gate script. It does not contain the full 1,192-file source ZIP or the 18-correction overlay.** Do not describe it as a merged or deployable app.

## Vercel gap (HOLD_NEW_PREVIEW)
- Existing project query PASS; latest existing deployment `dpl_53QvzpuUopVs3kgKyFbcbQfxPbLF` is READY (target null).
- Its deployment source tree exposes 8 regular files in `src/` and lacks the full `second/` project.
- The intended Vercel project was not present among Git-linked projects in this account's Git deployment context. Thus no automatic GitHub PR → Vercel Preview link verified.
- **No new Preview created. No new URL can be claimed.**
- Existing protected Preview remains unchanged.

## Release controls and next gate
1. Import all 1,192 files (or a verified equivalent complete source tree) into a separate review-only branch, preserving original IDs/assets; use GitHub's verified SHA and match full file inventory.
2. Run explicit CI/static/real-browser tests on that exact branch. No CI/Paid Actions use without budget verification.
3. Deploy **once** to existing project as Preview (not Production), with correct account/team and immutable commit SHA.
4. Verify page load, 47/47 answers, 18/18 proposals linked only to 6 IDs, 41 others unaffected, exam-mode hides review, mobile 360/390, saving/F5 restoration, download, expected asset coverage.
5. Status remains HOLD until the actual remote HTTPS browser E2E and legal-specific approval gates pass; no automated legal approval.

Current decision: LOCAL_SOURCE_INTEGRITY_PASS; GITHUB_FULL_INTEGRATION_HOLD; NEW_PREVIEW_HOLD; LEGAL_CONTENT_0_47_HOLD.
