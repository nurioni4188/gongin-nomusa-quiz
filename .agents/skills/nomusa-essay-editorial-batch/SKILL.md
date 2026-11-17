---
name: nomusa-essay-editorial-batch
description: "공인노무사 2차 기출 연도별 상세·압축답안의 중복 점검, 배점 비례 분량 설계, Chromium 실제 표시본 원고 추출 및 검토용 Markdown/JSON 동시 생성. 기존 RC27/RC35·main·Production 보존."
---
# NOMUSA Essay Editorial Batch — 재사용 가능한 검토용 스킬

## 사용 시점
- 사용자가 "2023년과 2025년 한꺼번에 답안 정리", "연도별 상세·압축답안 편집", "소문항 분량 검사", "새 연도를 2022년 방식으로 완성"을 요청할 때.
- 이 스킬은 **저장소에 있는 스킬 설명서**다. ChatGPT 플랫폼에 전역 스킬로 설치되었다는 의미가 아니다.

## 기준과 불변조건
- 저장소: `nurioni4188/gongin-nomusa-quiz`.
- 기존 작업 브랜치: `review/nomusa-auto-v1-20year-gate-20261115`.
- 2022년 V16.8 원고 생성·Chromium 검증이 기준.
- Vercel 기존 프로젝트 `gongin-nomusa-rc27-preview`; **이 스킬은 배포하지 않는다**.
- `main`, Production, RC27/RC35, 원장 PDF/HWP, 문제 ID, 배점, 학습저장키, 기존 배포 불변. 사용자가 승인하지 않은 새 프로젝트·서버·DB·AI 채점 금지.

## 편집 작업 단계
1. 지정 연도의 원본 `rc27_essay_catalog.js`를 직접 읽는다. 존재하지 않는 기출이나 정답 근거를 창작하지 않는다.
2. 원장 `N27_CATALOG.items`의 ID·연도·과목·대문항·소문항 배점 합계를 확인한다. 공식 소문항의 `물음 n` / `대문제 n`만 센다. 장문 답안 내부 목차를 새로운 소문항으로 세지 않는다.
3. 해당 연도 기존 심화답안과 overlay를 로드한 실제 `NOMUSA_CANONICAL_SELECTION_V1.items`를 기준으로 한다. 원장 또는 오래된 요약문만으로 최종 표시원고를 추측하지 않는다.
4. 기존 상세·압축답안을 변경 전 스냅샷으로 보존한다. **완전히 같은 180자 이상의 긴 문단만** 중복 삭제한다. 유사하지만 법리나 사안포섭이 다른 문장 자동 삭제 금지. 내용이 누락되면 HOLD.
5. 50점 8~10장, 25점 4장을 기준으로 소문항 배점 비례 목표 장수를 산출한다. 목표 장수와 실제 수기 필기 가능성은 다르다.
6. 부족한 논증만 추가할 때는 기출 사실과 검증 가능한 시험일 법령·판례·학술 원전으로 작성한다. 학설·저자·연도·사건번호를 창작하지 않는다. 검증되지 않은 문단은 출처 또는 최종 승인 HOLD.
7. 상세답안·압축답안·원장 전사·소문항 배점 목표를 실제 Chromium 화면의 최종 투영 데이터에서 추출하고 Markdown·JSON·감사 manifest를 생성한다.
8. 중복 ID=0, 원장배점 합 일치, 상세·압축 누락 0, 변경 전 답안 보존, 최종 자동채점 승인 false, 가로넘침·자동저장·새로고침 복원 회귀검증 확인.
9. 1440/390/360px Chromium에서 검증하고, Actions 아티팩트로 제공한다. PDF 시각대조·시험일 시행법령 전체 대조·실제 손글씨 분량·전문가 독립승인은 **별도 게이트**다.
10. 완료 보고는 **편집용 통합원고 생성 PASS**와 **법률·학술 최종 승인 HOLD**를 분리한다. 승인되지 않은 답안을 공식 완성으로 표기하지 않는다.

## 현행 실행 파이프라인
- 원장 편집 overlay: `second/nomusa-v168-2022-editorial-19x32.js` (2022).
- 2023/2025 overlay: `second/nomusa-v169-2023-2025-editorial-38x69.js`.
- 공통 추출기: `scripts/nomusa_editorial_batch.py` 의 `export_editorial_years(page,root,(2023,2025))`.
- 브라우저 시험: `scripts/nomusa-canonical-shared-browser-gate.py`.
- 기존 GitHub 검토 전용 Actions: `.github/workflows/nomusa-canonical-e2e.yml`.
- 검토본: Actions `nomusa-2023-2025-38x69-editorial-candidates` 아티팩트 안의 연도별 `*_editorial_candidate.md`, `*_rendered_review.json`, 통합 `*_editorial_manifest.json`.
- 각 새 연도에 대해 반드시 원장 문항 수/소문항 수를 먼저 재산출해 overlay와 스크립트의 연도별 기준에 추가한다. 2023은 19/32, 2025는 19/37. **미검증 연도에 그대로 동일한 숫자를 복사하지 않는다.**

## 완료 기준
- 소스 작성·모의 검사는 최종 검증이 아니다.
- Actions 전체 SUCCESS 및 artifact 실제 확인까지 되어야 **원고 생성 PASS**라고 표기한다.
- 500자/장 기계 환산을 수기 4장/8~10장 PASS로 표시하지 않는다.
- 모든 판례·학술 원전 전문과 기출 PDF 인쇄면 대조, 필기시간, 독립 검토 승인 완료 전에는 법리·학술 '최종 완성'은 HOLD.
- GitHub `main`과 기존 Vercel 배포의 전후 SHA/URL을 확인한다. Preview 배포는 별도 승인 필요.

## 예시 지시문
> NOMUSA Essay Editorial Batch 스킬에 따라 기존 검토 브랜치를 보존하고 2023·2025년 기출원장과 최신 상세·압축답안을 대조해, 38개 대문항/69개 소문항의 검토용 원고를 한 번에 생성하라. 중복·누락·배점·분량 목표를 검사하고 실제 Chromium 세 화면 크기에서 회귀검증하라. GitHub Actions Markdown/JSON 아티팩트를 반환하고 미검증 법령·학술·수기분량을 HOLD로 구분하라. Production과 기존 Preview를 절대로 수정하지 마라.

## V17 — 나머지 17개 연도 전수 배치(2007~2021, 2024, 2026)
- 2022·2023·2025 편집후보본은 변경하지 않고 17개 연도의 기존 학습 답안을 정리한다.
- `second/nomusa-canonical-selection-v1.js`의 328개 우선 선택 레코드를 기준으로 연도별 등록 ID를 세고, 그중 제외 3개년 57개를 뺀 **271개**를 처리한다.
- 2007~2012는 레거시 원장, 2013~2018·2021은 기존 parent와 child의 이중 카운트 금지, 2024·2026은 원래 소문항 ID가 분리되어 있으므로 그 자체를 채점 단위로 유지한다.
- 역사적 소문항 개별 배점이 직접 확인되지 않으면 전체 등록문항 배점을 단일 단위로 기록하고 `splitVerified=false`로 표시한다. **임의 소문항 분할 금지**.
- 재사용 overlay: `second/nomusa-v17-remaining-17years-editorial.js`
- 기존 배치 추출기 함수 `scripts/nomusa_editorial_batch.py::export_remaining_years`
- GitHub Actions는 17개 연도별 Markdown+JSON 및 종합 audit manifest를 `nomusa-remaining-17years-editorial-candidates` 아티팩트로 묶는다.
- manifest에 연도별 등록건수, 미검증 소문항 수, 원문 누락/초안 누락, 승인 HOLD를 기록한다. 원문이 빠진 연도를 성공 완료로 보고해서는 안 된다.
- 271개 항목의 등록·추출은 **기존 학습원고 편집 및 출력**이며, 271개 답안의 학술·법리·시험장 필기분량 신규 승인이나 새 모범답안 작성 완료와 동일하지 않다.
- 신규 연도 확대 시 먼저 실제 year/count/score를 검증하고, 코드의 연도별 예상값을 갱신한 후 Chromium 1440·390·360px 회귀검사를 다시 수행한다.
