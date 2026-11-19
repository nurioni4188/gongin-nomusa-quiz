---
name: nomusa-v29-2022-baseline-19year-content-gate
description: "2022년 19개 답안을 기준으로 공인노무사 2차 2007~2026년 20개년 328개 답안의 원문/근거/논증/분량 차이를 안전하게 비교하고, 미확정 항목을 우선순위별로 분류하며 검토본만 생성하는 재사용 Claude Code 프로젝트 스킬."
---

# NOMUSA V29 — 2022년 기준 나머지 19개년 내용검증

## 절대 변경 금지
- 저장소: nurioni4188/gongin-nomusa-quiz
- 브랜치: review/nomusa-auto-v1-20year-gate-20261115, Draft PR #3. PR을 main에 병합하지 않는다.
- main, RC27, RC35, Production, 기존 Vercel Preview, 기출 원문, 기존 문제 ID, localStorage 저장키, 328개 원고를 변경하지 않는다.
- 이 스킬은 **자체 검증용 작업 절차**이다. 다른 컴퓨터나 Claude Code 프로젝트 전체에 자동 설치되었다는 뜻이 아니다.
- 외부 전문가를 사칭하거나 검토일/서명/판례·학술 원전 열람 여부를 생성하지 않는다. 승인 0/328 및 HOLD 유지.

## 품질 목표 — 2022년은 최초 심사기준이지 법률·학술 완성 승인본이 아니다
- 2022년 19문항·32소문항은 V27의 6건 + V28의 13건 제한적 원전·서지·산술 주장 대조를 완료했다. 모두 전체 내용/학술 승인과 별개다.
- 2007~2026년 원고는 328개 등록, 2022 외 309개. 총 P0 19 + P1 77 + P2 35 + P3 197을 유지한다.
- 원문 공식파일 일치(328/328)와 내용정확성은 구분. 2016_p5_q2 OCR 유사도 MEDIUM 1건은 원문 교열 대기.
- 2022년과 같은 출처검증 깊이를 다른 연도에 아직 평가하지 못했으면 SAME_QUALITY_NOT_ESTABLISHED로 기록한다.

## 실행 순서
1. GitHub Draft PR #3 최신 HEAD와 V23 원장, V27/V28 부분 근거 파일의 SHA·수량을 대조한다.
2. 빠른 원장 전수 감사: python scripts/nomusa-v29-2022-baseline-review.py . --self-test ; python scripts/nomusa-v29-2022-baseline-review.py .
3. 실제 앱 표시원고 20개년 추출: python scripts/nomusa-canonical-shared-browser-gate.py . (Chromium/Playwright 설치 환경).
4. 실제 표시본문의 sourceText+detailed+compressed SHA-256과 원장 328행을 대조: python scripts/nomusa-v29-2022-baseline-review.py . --rendered
5. 출력: review-artifacts/NOMUSA_V29/NOMUSA_V29_328_CONTENT_TRIAGE.json, NOMUSA_V29_328_CONTENT_REVIEW_QUEUE.csv, NOMUSA_V29_20YEAR_DELTA_REPORT.md.
6. 상세 내용 심사는 2022 P0 19건 선행, P1 77건은 2009(11)→2012(10)·2023(10)→2008(9)·2011(9)→2007(8)·2010(8) 우선, 이후 P2 35→P3 197 순으로 배치한다.
7. 검토 대상 원문→시험 당시 적용 법조문/부칙·판결 전문→학술 원서·논문 원저→노동경제학 수식·그래프→사안포섭/독립 논증→실제 필기(25점 4장, 50점 8~10장) 순으로 검토한다.
8. 오류가 근거로 확인된 문항만 별도 검토 브랜치에서 구체적 교정안을 작성한다. 변경 전후 본문·압축 원고를 보존하고 원고 SHA, 문제 ID/배점/저장키 불변 게이트, 모바일 360/390·PC1440 회귀검증을 적용한다.
9. 검토자 실명·자격·검토일·원전 URL·독립 서면판정·고정 textSHA256 확인 전에는 어느 문항도 최종승인 처리하지 않는다.

## 우선 심사 관문
- 법률(노동법, 행정쟁송법, 민사소송법): 해당 시험일 시행 조문·부칙, 판시 법리 전문, 유사 사례의 사안포섭과 결론의 정확성.
- 인사노무관리/경영조직: 저자·저서·논문·발행연도 및 문제에서 요구한 이론 분류를 원저와 독립 비교. 서지만 존재하면 본문 내용 승인 금지.
- 노동경제: 공식 기출의 주어진 함수/숫자로 풀이 검산, 그래프 축·교점·구간 조건, 기호 해석 및 비교정태를 직접 검토.
- 분량: 글자수 500자/쪽 프록시가 아닌 실제 필기속도·장수·목차/논증 밀도를 대조. 원고가 길다는 이유로 합격 답안 인증 금지.
- 다른 연도에 2022와 같은 수준의 원전·소문항·내용 검토기록이 없으면 편집본 존재 PASS / 최종 전문검증 HOLD.

## 참고·자동화
- 최초 산출보고서: review/NOMUSA_V29_2022_BASELINE_19YEAR_DELTA_20261118.md
- 검증 원장: review/NOMUSA_V23_VALIDATION_LEDGER.json
- V27/V28 기준: review/NOMUSA_V27_2022_PRIMARY_CONTENT_CROSSCHECK_20261118.json / review/NOMUSA_V28_2022_REMAINING_13_SOURCE_CROSSCHECK_20261118.json
- 빠른 재검증 워크플로: .github/workflows/nomusa-v29-2022-19year-content-triage.yml
- CI는 읽기 전용, GitHub Actions artifacts에 진단표만 저장. 승인/배포·이메일·커밋 자동수정 금지.

## 실행 판정
- PASS는 328 ID 일치, V23 공식 기출 연결, V27/V28 2022 19건 제한적 근거, 브라우저 328 본문 SHA 일치에만 부여.
- FAIL이면 개별 사유와 파일/문항 ID를 남기고 임의 복구 금지.
- 시험 당시 전문 법리·학술·실전 필기·독립 최종승인은 모든 연도 포함 HOLD 0/328로 유지한다.
