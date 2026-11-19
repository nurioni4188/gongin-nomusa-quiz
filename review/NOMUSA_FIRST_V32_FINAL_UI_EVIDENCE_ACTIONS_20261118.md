# NOMUSA FIRST V32 — 기존 답안 근거단계/UI 중복정리 최종검증

2026-11-18 KST · 기존 검토 브랜치 · Draft PR #3

## 정답 채점 범위와 주의
- 2008~2021년 문제풀이 편입 1,259개: 복습/선택 저장 가능, 채점 승인되지 않은 정답의 자동채점 차단 유지.
- 기존 2022~2026년 1차 1,020문항: 종전 RC35 채점과 저장·복원 유지.
- 과거 정답 후보 3,400건, 독립 채점승인 **0/3,400**.
- Q-Net PDF 연결 인덱스 900건: 기존 텍스트/선택지 300, OCR 후보 556, PDF 개별 페이지 원장 HOLD 44.
- V62 3건·V71 14건 일부 PDF 문항번호/위치 시각확인. 원본 시험지 전체 지문·수식·인쇄쪽수 검수와 독립 승인 별개.
- 2020~2021 공식 정답표 600셀 이미지 대조(자동 596, 예외 직접 시각확인 4), 채점승인 아님.

## 실제 UI 변경
- 과거 정답조회 `study-hub/first-legacy-answers.html`: 전체 HOLD 일괄 표시 대신 Q-Net PDF 위치/시각확인 및 정답표 이미지 근거단계별 2줄 표기, 모바일 360/390px 카드.
- 학습 홈 `index.html`: 과거 연도 반복 HOLD 타일을 **선택 기록**으로, 퀴즈 전·후 동일 안내를 동시에 중복하지 않도록 처리. 정답 강조/오답 판정/성적 계산 로직은 계속 미승인 문항 제외.
- `study-hub/index.html`과 `study-hub/app.js`: 3,400건 배너 중복 제거, 검증페이지 링크 1개.
- `study-hub/first-v32-proof-status.js`: 900 Q-Net 문항 연결에서 원전/정답/승인 3층으로 표시(승인 필드 false).
- `scripts/nomusa-first-v32-status-ui-gate.py`: 17개 직접 검증, 1440/390/360px 수평스크롤 0.

## CI 최종 상태
- [GitHub Actions #44203425389](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44203425389) **completed/success**, 커밋 `2f99d2354e5144016990dfb8d0d095de0b03cc19`.
- V32 17/17 (기존 900개 원문 연결·600 이미지 정답표 대조·중복 제거·1차 채점 차단·모바일)
- V71 공식 원전 42/42
- V61 과거 3,400 후보 및 900 공식 PDF 연결 원장 내부정합성 PASS
- 1차 RC35 및 과거 공식 정답 검토 6 브라우저 E2E PASS (PC1440·모바일390/360 저장·복원·채점 미승인 차단)
- 최신 2007~2026 2차 canonical+학습 허브 328개 답안 3화면 E2E PASS
- 실제 검증 산출물 [Artifact 14381828637](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44203425389/artifacts/14381828637).
- 구형 V6 테스트는 과거 2차 학습단위 309개를 고정해 현재 377 단위에서 실패했으므로, **1차 전용 `--first-only` 6회 테스트 + 최신 2차 canonical**로 역할을 구분했다. 기존 V6의 기본 테스트/채점 로직은 변경하지 않았다.

## 배포관문
- 원본 1차 정답·Q-Net 다운로드 파일·문제 ID·저장키·2차 답안 원고 **변경 없음**.
- `main` 및 Production 유지. Draft PR #3 미병합.
- GitHub Actions PASS는 기능·상태/해시 검증일 뿐, 과거 정답 독립서명 또는 공식 승인 아님.
- 새 Vercel 배포 대상은 기존 `gongin-nomusa-rc27-preview` 프로젝트의 Preview 한정. 인증된 원격 브라우저 실사용은 별도 HOLD.
