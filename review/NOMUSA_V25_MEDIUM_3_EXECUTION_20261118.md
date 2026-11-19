# NOMUSA V25 — 3개 MEDIUM 원전대조 및 민사소송법 2문항 교정 검증 결과

**검증일(한국시간): 2026-11-18.** 저장소 `nurioni4188/gongin-nomusa-quiz`, 대상 검토 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`, Draft PR #3 미병합.

## 최종 판정

- **PASS** — 기출 PDF 원본 페이지 AI 시각 교차검토 3개, 원문 전사 오류 정정 2개, 기존 정확한 원문 보존 1개.
- **PASS** — Chromium PC 1440px / 모바일 390·360px 실사용 저장복원 E2E, 기존 V19/V21/V22/V23 검증원장 전체 재계산, 328문항 고유 ID 보존, 새 전사문 2개만 본문 SHA 변경·326개 전체 본문 SHA 불변.
- **PASS** — V23 원장 재생성 `sourceVerifiedQuestion=328`, Q-Net 공식 원본 첨부파일 해시 비교 내역 **328/328(이전 V23 증빙 재사용)**, 원문 요지문항 0.
- 기계적 일치도: **기존 HIGH 325/MEDIUM 3 → 최신 HIGH 327/MEDIUM 1**.
- **HOLD** — 독립적인 사람의 글자별 교열, 시험 당시 법령·판례 전문·학술원전·실전 수기분량 및 독립 전문가 최종 서면승인 **0/328**.

## 원본 이미지별 검증

| 문항ID | 공식 PDF 페이지 | 이미지 대조 및 실제 변경 | 기존 자동 일치도 / 현재 |
|---|---|---|---|
| `2016_p5_q2` 경영조직론 25점 | `source_pdf/2016/2016_second_full_original.pdf` p.7 | 기존 V24 전사 `...학습과정 그리고 학습의 주요 원리...`는 원본과 일치. Tesseract의 `그러고` OCR 오독 때문에 자동 일치도 MEDIUM 0.80. **sourceText 수정 없음** | MEDIUM → MEDIUM (AI 시각대조 설명 증빙) |
| `2019_p4_q3` 민사소송법 25점 | `source_pdf/2019/2019_p4_civil_procedure.pdf` p.1 | `【문제 3】 공동소송참가에 관하여 설명하시오. (25점)`으로 교정. 구 OCR 붙여쓰기 및 시험지 하단 문구 혼입 제거. 이전 전사 `sourceTextBeforeV25` 보존 | MEDIUM → HIGH |
| `2020_p7_q3` 민사소송법 25점 | `source_pdf/2020/2020_p7_civil_procedure.pdf` p.1 | `【문제 3】 유사필수적 공동소송에 관하여 설명하시오. (25점)`으로 교정. 구 OCR 붙여쓰기 및 시험지 하단 문구 혼입 제거. 이전 전사 보존 | MEDIUM → HIGH |

근거 URL·공식 원전 PDF SHA256·AI 원전 이미지 확인 범위: `review/NOMUSA_V25_MEDIUM_3_PRIMARY_PAGE_CROSSCHECK_20261118.json`.

## 실행 및 재현 증빙

- 원문 PDF 이미지 생성: GitHub Actions [run 44159068617](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44159068617), [원본 이미지 아티팩트 14362367155](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44159068617/artifacts/14362367155).
- **최종 원문·앱 회귀검증 성공**: [GitHub Actions run 44161596035](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44161596035), `completed/success`, 실행 2026-11-17 19:43:12~19:45:31 UTC(**약 139초**). V23 원장 부분 재계산은 **22.479초**.
- 최종 아티팩트: [14364131025](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44161596035/artifacts/14364131025), 전사교정 3건 증빙·두 문항 전/후 SHA·전체 328 답안 재검증.
- 검토 브랜치 자동 ledger 커밋 확인: 성공 후 PR #3 HEAD `3aaec604c0ad288b971008f7abc5fd14a06045ff`(본 보고서 작성 전), `main` HEAD `9ea46fc9134c55a4312241b55a82b237e86ed4a8` 불변.
- 자동 실행 전 실패 원인 및 교정: V25 초기 CI에서 원시 2019/2020 카탈로그 배점이 **0/미지정**이고 실효 배점은 V18 `verifiedPointsV18`에서 25점으로 확정되는 구조를 새 사전검사가 잘못 해석. 기존 점수원장 원시 구조를 변경하지 않고, **원본 PDF의 (25점)** 레이블을 확인하는 V25 preflight와 V18/V23의 공식 배점 회귀검증을 분리하여 성공. 과거 실패 실행은 이력으로 보존한다.
- 검증 코드 `scripts/nomusa-v25-medium-source-images.py`, `scripts/nomusa-v25-browser-source-smoke.py`, `scripts/nomusa-v25-medium-source-gate.py`와 공식 이미지 증빙을 `.github/workflows/nomusa-v25-medium-source-gate.yml`로 재현 가능.
- V25 적용 소스: `second/nomusa-v25-apply-medium-source-3.js`. 두 UI 로더 `second/index.html`, `study-hub/index.html`에서 V24 이후 불러온다. 독립 Claude Code 스킬 `.claude/skills/nomusa-v25-three-medium-pdf-proofread/SKILL.md`.

## 승인을 남긴 항목

**MEDIUM 1건은 실제 인쇄 원문 불일치가 아닌 OCR `그리고/그러고` 오인식이며, AI가 PDF 이미지로 확인했다는 증빙만 보관한다.** 사람의 원전 글자별 검수·법령·판례 전문 확인·학술원전 확인·손글씨 실측이 완료되었다고 선언하지 않는다. 독립 전문가 서면승인 0/328, `FINAL_APPROVAL=HOLD`.

GitHub `main`, RC27/RC35, Vercel Preview/Production, 공식 PDF, 저장키 및 상세·압축답안은 변경하지 않았다. 이메일 발송·새 Preview·PR 병합 없음.

## 다음 작업

**30개 V24 전사문에 대한 인간 독립 글자별 교열** 및 법령·판례·학술 원전 검증. 특히 자동 MEDIUM 1건인 `2016_p5_q2`는 PDF 이미지에 따른 AI 시각 증거를 전문가가 재확인하도록 한다. 나머지 원고 328개에 대한 최종 승인 여부는 독립 검토자의 근거/검토일/자격/서면의견 확보 후에만 문항별 결정한다.
