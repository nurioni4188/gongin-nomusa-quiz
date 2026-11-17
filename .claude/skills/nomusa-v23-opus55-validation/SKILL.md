---
name: nomusa-v23-opus55-validation
description: 2007~2026년 공인노무사 2차 328개 답안의 독립 출처·원전·배점·법령·판례·학술·수식 검증을 Claude Opus 5.5에서 자동 실행하고 증빙을 GitHub 검토 브랜치에 남기는 스킬. 사용자 승인 없는 전문가 최종승인·Preview/Production 배포 금지.
---

# NOMUSA V23 — Claude Opus 5.5 원전 검증 및 전문가 심사준비

## Invocation
"/nomusa-v23-opus55-validation"
또는 "GitHub review/NOMUSA_V23_CLAUDE_OPUS55_HANDOFF.md를 읽고 V23 전체 328개 답안을 자동검증해."

## 첫 실행 시 반드시 할 일
1. 현재 git remote가 `nurioni4188/gongin-nomusa-quiz`인지 확인.
2. GitHub의 기존 `review/nomusa-auto-v1-20year-gate-20261115`를 가져와 HEAD/원격 일치와 작업 상태를 확인. 정확한 최신 SHA는 매번 원격에서 확인한다. `main`, Production, RC27, RC35는 수정하지 않는다.
3. `review/NOMUSA_V23_CLAUDE_OPUS55_HANDOFF.md`를 읽는다.
4. V22 현황 `review/NOMUSA_V22_SOURCE_EXPERT_GATE_EXECUTION_20261117.md` 및 V21 `review/NOMUSA_V21_APPROVAL_EXECUTION_RECORD_20261117.md`와 기존 `.agents/skills/nomusa-v22-primary-source-expert-gate/SKILL.md`를 읽는다.
5. 재실행 전에 기존 워크플로의 PASS를 공식 내용승인으로 잘못 해석하지 않는다. SHA와 날짜를 검증하며 같은 조사를 반복하지 않는다.

## 검증 엔진 (기존 도구 재사용)
- `scripts/nomusa-canonical-shared-browser-gate.py`: 실제 Chromium PC 1440px/모바일 390px·360px. 브라우저 원고 20년/328개·저장/복원/E2E 확인.
- `scripts/nomusa-essay-quality-v19.py`: 본문/배점/분량 프록시 등 구조.
- `scripts/nomusa-essay-approval-v21.py`: 전체 328개 승인원장/2022년 19×32/77개 500자쪽 프록시/본문 SHA.
- `scripts/nomusa-v22-original-expert-packets.py`: 원전 PDF 후보·SHA·2022년 19개 문항 심사패킷·PDF 페이지 이미지.
- `.github/workflows/nomusa-v22-primary-expert-packets.yml`: GitHub Actions 실행 및 artifact 게시.
- 테스트 오류는 최초로 재현한 후 필요한 범위만 수정, 각 수정 후 회귀검증.

## 과목별 원전 검증 (AI가 잘할 수 있는 검토 / 확정불가 경계)
- 공통: Q-Net 2차 기출문제 실제 첨부 PDF/HWP 원문/쪽수/그래프/소문항/배점 출처 대조. 저장소 PDF 후보가 존재하는 사실은 공식 파일 해시 일치가 아니다.
- 법률 3계열: 시험일에 효력이 있던 법령·부칙/대법원 공식 판결서의 선고일·사건번호·핵심 법리·원전 인용부·사안포섭. 시험 이후 변경법/판결은 시대적 주석으로 분리.
- 인사노무·조직: 학자·저서·논문·발행 연도·연구조건을 KCI/출판기관 공식 원전에서 확인. 원전 미조회 또는 초록만 확인한 항목은 전문확인 HOLD.
- 노동경제학: 기출 원문 숫자/제약식/도함수/극값/경계해/비교정태/그래프를 독립 수식 재계산하고 검산 결과와 반례를 기록.
- 학술적 이견, 쟁점·배점 누락, 법령 시점 오류, 허구 판례/연도 등을 발견하면 ID별 오류/근거 URL/수정안으로 기록. 확인하지 못한 것을 PASS로 표기하지 않는다.
- Claude 단독 자기검사는 "AI 사전검증"에 불과하다. 독립 검토자와 실제 원전증빙을 가정하거나 만들지 말 것.

## 328개 우선순위와 정합성
- 2022년 P0 19개·32소문항, 기존 소스 7개 PDF와 19개 텍스트 후보 맞춤. V22에서 공식 4건 판시요지 대조, 전체 판결문과 원전 적용 검증 HOLD.
- 2022년 이외 77개 글자수 프록시 우선심사(2022년과 중첩 시 P0 먼저). 50점 29/25점 48; 500자/쪽 가정과 실제 손글씨 장수는 구별.
- V22 원전 분류: 2022 19개 높은 텍스트 일치 / 그 밖에 PDF 후보 존재 209 / 2021년 두 일차 미해결 6 / 2007~2012년 HWP 파일 바이너리 미확인 94.
- 과목별 내용의 최종 전문가 승인은 0/328. 원본 확보/전문가 의견 부재인 항목은 자동 검증만으로 승격 불가.

## 작업 단위
- 2022년 19개부터 고위험 검증 규칙을 검수하고, 이후 309개를 7과목 × 연도 묶음으로 병렬 분석(각기 독립 evidence JSON). 실제 탐색이 가능한 실행환경이라면 공식 원전을 자동 조회하고 URL, 문서명, 선고/발행일, 실제 적용 조문, 공식 원본 SHA를 기록.
- 검증 결과는 문항 ID와 현재 상세·압축 원고의 `textSHA256`에 연결. 수정 시 해시 변동을 인지하여 재검증.
- 경제학/법률/학술의 검증 조건을 구분하고 같은 결론을 여러 모델이 반복해도 독립 전문가 승인 처리 금지.
- 가능한 범위에서 기존 리뷰 브랜치에 데이터/심사패킷/검증 스크립트만 commit + Draft PR #3에 기록. 직접 `main` push, merge, Production/Preview 배포, 신규 프로젝트, DB, AI 자동채점 금지.
- 실제 브라우저 E2E 및 GitHub Actions 재실행; log/run URL/commit SHA와 artifact를 보고. CI 비용 예산 부족이면 더 많은 작업을 예약/반복하지 않고 로컬 검증과 HOLD 보고.

## 보고서 및 회복가능 작업 기록
- `review/NOMUSA_V23_VALIDATION_LEDGER.json` (내용 확인마다 ID·원문출처·판례/학술/계산 근거·검증 수준/결과·참조일·본문 SHA)
- `review/NOMUSA_V23_OPEN_ISSUES.md` (원본 누락, 판례 충돌, 불확실한 값, 전문심사 요청)
- `review/NOMUSA_V23_CLAUDE_RUN_LOG.md` (Git SHA, 명령·실패/수정 내역, 실제 소요시간·Actions run URL)
- 새 변경을 수행하는 경우 기존 스킬 `.claude/skills/nomusa-v23-opus55-validation/SKILL.md`도 사용법/재현 경로에 맞춰 갱신한다.
- 사용량·컨텍스트 종료 시에도 미해결 내용과 다음 정확한 명령을 작업 로그에 저장한다. 예약 자동 실행이 아닌 이상 완료 약속/백그라운드 진행이라고 표현하지 않는다.

## V23 1차 실행 결과와 재현 경로 (2026-11-17, 실제 실행)
- 상태 요약: Q-Net 공식 첨부 **328/328 바이트 동일**, 문항·배점 대조 328 통과(요지문항 30건은 원문 교체 필요), 판례 100개 중 97 law.go.kr 확인·선고일 불일치 0, 계산 39체인 불일치 0, **전문가 승인 0/328**. 상세: `review/NOMUSA_V23_CLAUDE_RUN_LOG.md`, `review/NOMUSA_V23_OPEN_ISSUES.md`.
- 네트워크: 기본 환경은 Q-Net/law.go.kr 차단. 개인 환경 `gongin-nomusa-quiz`(허용 www.q-net.or.kr, www.law.go.kr, scourt 3개, www.kci.go.kr)에서 실행. glaw.scourt.go.kr은 502.
- 로컬 의존성: `pip install pymupdf==1.26.7 olefile cryptography sympy==1.13.3 playwright==<로컬 Chromium과 맞는 버전>`; OCR은 `apt-get install tesseract-ocr tesseract-ocr-kor` (OCR 결과는 캐시에 커밋되어 CI는 OCR 불필요).
- 재현 순서:
  1. `python scripts/nomusa-canonical-shared-browser-gate.py .` → V19 → V21 → V22 (기존 그대로; review-artifacts 생성)
  2. `python scripts/nomusa-v23-qnet-official-fetch.py /tmp/qnet --manifest review/NOMUSA_V23_QNET_OFFICIAL_MANIFEST.json` (공식 첨부, 게시물 artlSeq는 스크립트 `POSTS`)
  3. OCR 캐시 보충이 필요할 때만: `scripts/nomusa_v23_source_text.py`의 `source_text(path, cache)` (OMP_THREAD_LIMIT=1, 200dpi)
  4. 판례 신규 인용: `scripts/nomusa_v23_case_lookup.py`의 `lookup_all(cases, Path('review/NOMUSA_V23_CASE_LOOKUP_CACHE.json'))` (evtNo→evtNm→bdyText 순, 전원합의체 표기 포함 파싱)
  5. `python scripts/nomusa-v23-validation-ledger.py .` → `review/NOMUSA_V23_VALIDATION_LEDGER.json` + `review-artifacts/NOMUSA_V23_{LEDGER.csv,ISSUES.json,SUBJECT_PACKETS/}`
  6. CI: `.github/workflows/nomusa-v23-opus55-validation.yml` (runs-on **ubuntu-24.04**; ubuntu-latest=26.04에서는 Playwright 1.56 설치 실패). 원장 재현성·승인 불변식(전문가 0, FINAL HOLD)을 검사.
- 수동 판단 기록: `review/NOMUSA_V23_MANUAL_REVIEW.json` (요지문항 30건 공식 OCR 판독, 2022 경제 검산, 학술 AI 사전점검). 수동 판단은 AI 사전검증이며 전문가 승인이 아님.
- 함정(실제 겪은 오류): 2013 PDF 텍스트층은 글자 순서가 섞여 8-gram이 실패 → 한글만 n-gram 사용, 배점은 OCR로 확인. 2007~2012 HWP는 '배포용 문서'라 BodyText가 아닌 ViewText 복호화 필요. 숫자 검산기는 천단위 쉼표·½·변수계수(240−2E)를 오탐하므로 변수 인접 구간 제외. 문항 본문에 "요지/원문 전문은 PDF 참조"가 있으면 원문 아님.
- 원고 수정 시: 문제 ID·저장키 유지, `sourceText/detailed/compressed` 변경 → `textSHA256` 변경 → V21/V22/V23 재실행. 기존 서면승인이 있으면 잠금 해제 후 재심사.

## 최종 판정
- PASS_TECHNICAL / VERIFIED_PRIMARY_SOURCE / REVIEW_CANDIDATE / HOLD_MISSING_SOURCE / HOLD_TIME_EFFECT / HOLD_EXPERT_APPROVAL / HOLD_HANDWRITING을 분리한다.
- 독립 전문가 검토자·자격·검토일·원전·서면승인/실제 필기실측이 없다면 **FINAL_APPROVAL=HOLD**, 전문가승인 0/328.
- `main`, 기존 Preview, Production, 앱 ID/저장키, 공식 원본 파일은 불변이며 기존 Draft PR 이외 새 배포가 없어야 한다.

## 판례 미검색 3건 교차확인 추가 게이트 (2026-11-17)

- 국가법령정보센터 기존 검색 캐시가 미검색인 3건에 대한 **별도 출처 검토결과**는 `review/NOMUSA_V23_CASE_3_CORROBORATION_20261117.json`에 보존한다.
- `2012다81609`는 대법원 후속판결 공식 자료에서 2014-12-24 인용 확인; `2011두7526`는 한국노동연구원 노동판례리뷰에서 2011-05-26 확인(법원 원판결 미열람); `2024구합76393`은 서울행정법원 공식 게시물로 사건 확인, 2025-08-21 선고일은 비법원 자료 확인에 그쳐 공식 PDF 대조 HOLD.
- 재검증 명령: `python3 scripts/nomusa-v23-case-corroboration-gate.py .`.
- 검증 전용 워크플로 `.github/workflows/nomusa-v23-case-corroboration.yml`은 기존 V23 원장 328건과 문항 SHA, 3사건·5회 인용, 승인 0/328을 검증한다.
- 기존 `review/NOMUSA_V23_CASE_LOOKUP_CACHE.json`의 `NOT_FOUND_ON_LAW_GO_KR_SEARCH`는 **당시 검색 결과**이므로 다른 공식·연구기관 자료를 얻었다는 이유로 `FOUND_ON_LAW_GO_KR`로 허위 변경하지 않는다.
- 독립 전문가·원판결 전문·학술·역사법령·수기실측이 없는 상태에서 `FINAL_APPROVAL=HOLD` 유지. 판례 원본 인용만으로 답안 학술 승인하지 않는다.
