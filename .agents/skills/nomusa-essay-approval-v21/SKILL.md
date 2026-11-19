---
name: nomusa-essay-approval-v21
description: "공인노무사 2차 2007~2026년 328개 답안의 자동 근거 사전심사, 2022년 19개/32소문항 심사파일럿, 77개 분량위험, 검토증빙, 독립승인 관문 및 실행시간 기록. 전문가 승인 자동 부여 금지."
---
# NOMUSA V21 — 모범답안 최종내용승인 근거검증·심사 자동화

## 호출
"V21 스킬로 공인노무사 2차 328개 답안의 원문·배점·판례·학술·수식 근거 검증 우선순위와 2022년 19개 승인심사 자료를 생성하고 GitHub 검토 브랜치에서 자동검증해 주세요."

**GitHub 저장소 내부의 스킬이며 ChatGPT 서비스 전역에 설치한 것은 아니다.**

## 기준 및 보존
- Repository: nurioni4188/gongin-nomusa-quiz.
- Branch: review/nomusa-auto-v1-20year-gate-20261115, 기존 Draft PR #3 사용.
- 2007~2026 20개년 328개 등록답안; V20 심화초안 88개(50점 32·25점 56), 2022년 19개·32소문항, V18 점수증빙 26개, V20 분량 프록시 위험 77개.
- main·Production·기존 Preview·RC27/RC35·기출 PDF·문항 ID·수험생 저장키 불변.
- 신규 프로젝트, 무단 배포, PR 병합, 자동채점, 무인 최종승인 금지.
- 판례번호·원전·논문·저자·연도·전문검토자·검토일·AI 교차검증 실행결과 등을 임의 생성하지 않는다.

## 단계 A — 전체 328개 일괄 자동 사전심사
1. GitHub Actions NOMUSA V21 workflow로 실제 Chromium PC 1440px·모바일 390px·360px를 실행해 20개년 브라우저 최종원고를 재추출한다.
2. 기존 scripts/nomusa-essay-quality-v19.py로 328개·20개년·점수증빙 26개·프록시 검토대상을 구조검증한다.
3. scripts/nomusa-essay-approval-v21.py로 문항 ID 고유성, 원문·상세·압축, 소문항 배점합, V20 심화 88개, 2022년 19개·32소문항, 코드상 허위 scoringApproved, SHA256 본문지문, 원전 확인 필요 문구와 판례·법조문 토큰을 검사한다.
4. P0는 2022년 전체 19개, P1은 다른 연도 분량 위험, P2는 근거 확인 문구, P3는 나머지. P0/P1이 겹친 문항은 우선순위 한 건으로 표시한다.
5. 법조문 번호나 판례 사건번호를 자동 발견한 것만으로 원전 존재·진위·시험일 적용성을 검증했다고 선언하지 않는다.

## 단계 B — 과목별 실제 근거 교차검증 지침
- 노동법·행정쟁송·민소: 공식 기출원문 PDF와 배점/쪽·표를 먼저 확인한 뒤 해당 시험일의 법률·시행령·부칙·판례 원전 및 사실관계 사안포섭을 검토한다.
- 노동경제학: 원문 수치로 변수·단위·목적함수·일차조건·이차조건·경계해·그래프를 독립 계산한다.
- 인사·조직: 학자·저서·논문·연도·모형 작동조건·비판과 구체 적용을 학술 원전으로 검토한다.
- 두 AI 모델이 실제 실행되고 독립 대조한 기록이 없는 한 crossModelReview는 NOT_RUN으로 표시한다. AI 합의는 전문가 최종 승인 대신할 수 없다.
- 법령·학술·수식 검증의 확정적 근거 없는 문항은 HOLD. 원본과 현행법의 시행시점 차이를 혼동하지 않는다.

## 단계 C — 실제 생성 결과
- review-artifacts/NOMUSA_V21_328_APPROVAL_TRIAGE.json — 328개 개별 문항, 이력지문, 체크리스트·위험코드.
- review-artifacts/NOMUSA_V21_328_APPROVAL_LEDGER.csv — 전체 승인원장.
- review-artifacts/NOMUSA_V21_77_PRIORITY_AND_PILOT_QUEUE.csv — 2022 기준연도 + 위험 77개 합집합.
- review-artifacts/NOMUSA_V21_2022_PILOT_19X32.md — 2022년 19개/32소문항 전문심사패킷.
- review-artifacts/NOMUSA_V21_AUTOMATED_PREAPPROVAL_REPORT.md — 기술 PASS/내용승인 HOLD 결과.
- review-artifacts/NOMUSA_V21_RUNTIME.json — 추정 아닌 실제 실행시간.
- GitHub Actions artifact로 재현가능하게 제공. CI는 검토 브랜치에서만 실행하고 본문·Source IDs/운영판을 쓰지 않는다.

## 단계 D — 독립 전문검토자의 최종승인 관문
모든 문항을 다음 조건과 함께 증빙한 경우만 외부의 독립승인 대상으로 상정한다:
1. 검토 문항 ID 및 승인대상 textSHA256와 최신 원고 본문 일치.
2. 공식 문제지 PDF의 쪽수·배점·소문항·표/그래프 원전 대조.
3. 법령·판례(시험일 기준) 또는 학술 저자·논문·연도 및 수식·그래프의 근거 확인.
4. 50점 8~10장, 25점 4장, 15점 3장, 10점 이하 2장의 실제 손글씨 분량 실측.
5. 실명·독립성·검토자격·검토일·근거 URL·개별승인 의견과 수정이력.
6. 최종승인 뒤 원고 SHA가 바뀌면 해당 승인 폐기·재심사.

**서면 검토자료가 없는 행은 반드시 HOLD_INDEPENDENT_CONTENT_APPROVAL. 현재 자동배치에서 독립승인 0/328.**

## 완료 확인과 스킬 관리
- 성공: PASS_AUTOMATED_PRECHECK_FINAL_APPROVAL_HOLD (자동 사전심사 통과, 최종승인 아님).
- 원전·경제모형·필기분량·독립 전문검토가 미완료면 각각 HOLD 유지.
- Actions run ID·SHA·결과 파일·자동검증 실제 소요시간을 보고한다. 검증 불가능한 예상 소요시간을 완료 실적으로 표현하지 않는다.
- 후속 보강/배치 자동화 완료 시 .agents/skills/nomusa-essay-approval-v21/SKILL.md를 해당 버전의 증빙과 함께 갱신하고 기존 main/Production은 보존한다.
