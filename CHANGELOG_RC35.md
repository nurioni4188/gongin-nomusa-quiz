# RC35 — Warm Light Study (2026-11-06)

## 화면 개선
- 기본 테마를 밝은 아이보리(#f7f6f2), 종이톤 카드(#fffefc) 및 안정적인 남색·세이지그린 포인트로 변경.
- 다크 테마는 사용자 수동 선택 시에만 사용; 기존 브라우저의 저장된 테마 선택은 존중.
- PC 좌측 사이드바, 모바일 2줄 메뉴와 학습 통계 카드, 진행률 링의 밝은 배색.
- 원문 시험 이미지는 흰 종이 배경 유지; 선택지/정답/오답 가독성 강화.
- 오답노트에 현재 오답·누적 오답·별표 요약과 복습 목록 배치.
- 검색/통계/백업 구조는 기존 유지, 모바일 360/390px 가로 넘침 방지 점검.
- 서비스워커 캐시 버전을 rc35로 갱신하여 기존 rc34 자산과 충돌 방지.

## 안전한 개발 범위
- `data.js`, `ANSWER_SECOND_READ_1020.csv`, 이미지 1,020개 **바이트 변경 없음**.
- 채점·실전 타이머·진행 저장/복원·오답목록·JSON 백업 로직 변경 없음.
- 원본 기출 PDF/HWP와 공식 최종정답의 독립 대조는 HOLD.
- 기존 RC33/RC34 보호 Preview 및 Production은 변경하지 않았음.

## 자동검증
- `python scripts/check_integrity.py` — 1,020문항, CSV, PNG 내부 일치성.
- `node tests/logic_smoke.js` — 11개 로직 검사.
- `python tests/browser_dom_ui.py` — Chromium DOM 기능검증 15개.
- `python tests/design_rc35.py` — 1365/768/390/360px 디자인 검증 16개.
- `python tests/smoke_ui.py` — 로컬 HTTP 실화면 검증(실행 제한 환경에서는 HOLD).
- `scripts/run_all_checks.ps1`는 실제 HTTP 검증 HOLD 시 성공으로 표시하지 않음.

## 배포 정책
- `scripts/deploy_preview_only.ps1`는 기존 SSO 보호 프로젝트만 대상으로 하며, 테스트 통과 후 Vercel Preview로만 배포. Production 전환 금지.
