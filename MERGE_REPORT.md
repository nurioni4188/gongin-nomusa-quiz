# 공인노무사 RC35 + V10.5 통합검증 및 기존 Preview 배포지시서

기준일: 2026-11-13 (KST)

## 산출물
- 압축파일: `공인노무사_RC35_V105_14개년_1차2차_통합Preview_20261113.zip`
- 배포 디렉터리: ZIP 내부 `site/` (반드시 `site/index.html`이 사이트의 기본 `/` 경로로 연결되도록 배포)
- 1차: **RC35 Warm Light Study** 유지, 2022~2026 총 1,020문항
- 2차: `/second/`, **V10.5 2013~2026 14개년**, 215학습 단위 (답안 초안 128 + 원문 연습 87)
- 원본 PDF: 43개 (`/source_pdf/...`)

## 수행/검증한 작업
1. `RC35_nomusa_Warm_Light_Study_source.zip`을 바탕으로 1차 파일(`data.js`, 원본 PNG 1,020개, `sw.js`, 아이콘 및 매니페스트) SHA-256 원본 일치를 확인. 원본 `index.html`의 기존 앱 스크립트는 변경하지 않고 상단 메뉴 **2차 논술** 링크 및 해당 링크 스타일만 삽입.
2. `공인노무사_RC27_2차_14개년_실사용검증보강_20261112(2).zip`에서 2차 전용 JavaScript, CSS, 원본 PDF 43개를 분리하여 통합. 기존 RC27 1차 기본화면으로 덮어쓰지 않음.
3. 정적·브라우저 메모리 시험: RC35 1,020문항 및 V10.5 215학습 단위 모두 PC 1440/768, 모바일 390/360에서 렌더링 PASS, 가로 넘침 0px, JS pageerror 0건.
4. 임시저장→브라우저 메모리 상태 복원·즐겨찾기·실전 답안 숨김/해제·JSON 백업 다운로드를 **메모리 저장소 모의시험**으로 PASS.
5. 로컬 HTTP 자산 확인: 기본 `/` 및 `/second/`, 핵심 JS/CSS HTTP 200, 원본 PDF 43/43 HEAD 200.
6. 실제 HTTP-origin Chromium 탐색 및 file:// 직접 탐색: 시험환경 `ERR_BLOCKED_BY_ADMINISTRATOR` → HOLD. **원격 Preview에서의 저장지속성·PC/모바일 E2E 통과를 주장하지 않음.**
7. Vercel 프로젝트 `gongin-nomusa-rc27-preview` 기존 계정 `onnuri4188@gmail.com`, 팀 `onnuri4188gmailcoms-projects` 확인. **이 통합본 신규 배포는 실행하지 않음.**

## 보호 정책 및 승인 상태
- GitHub `main` / Production / 기존 배포: 변경하지 않음.
- 1차 공식 문항·정답 승인 및 2차 답안의 법령·판례·학술 승인: 기존 HOLD를 승계함.
- 2차 해설은 학습용 검토 초안이며, 공식 모범답안·검증 완료로 표기하지 않음.
- 기존 1차 localStorage 저장 키 및 2차 V10.5 저장 키는 서로 분리. 다른 Preview 도메인에서 발생한 저장기록은 자동 이전되지 않음.

## ChatGPT Work 실행 지시문

이 대화에 생성된 `공인노무사_RC35_V105_14개년_1차2차_통합Preview_20261113.zip`을 사용하세요. ZIP 속 `site/`를 배포 루트로 설정하고, **새 프로젝트를 생성하지 말고** Vercel 연결 `onnuri4188@gmail.com` / 팀 `onnuri4188gmailcoms-projects` / 기존 프로젝트 `gongin-nomusa-rc27-preview` (`prj_J1hv2uJ6EzuWEcYtb6x4GYKpXV0i`)에 **Preview만** 새로 배포하세요. GitHub main, Production, 기존 Preview URL·별칭, 사이트 DB 및 원본 PDF는 변경하지 마세요.

배포 후 다음을 자동검증하세요: `/` 페이지 제목이 `RC35 · Warm Light Study`이고 1차 데이터 1,020개가 살아 있는지, **2차 논술** 버튼이 `/second/`로 이동하는지, 2013~2026의 14개 연도와 215개 학습 항목이 표시되는지, 2013·2025 PDF를 포함한 43개 PDF가 HTTP 200인지, 미승인 답안이 검증 완료로 오표기되지 않는지 확인하세요. 1440/768/390/360px에서 가로 넘침·브라우저 오류를 검사하고, 실제 배포 URL에서 답안 입력→새로고침→복원, 즐겨찾기, 20분 실전 잠금/해제, JSON 내보내기·가져오기를 시험하세요. 성공한 항목만 PASS, 수행되지 못한 항목은 HOLD로 기록하세요. 최종 Preview 새 주소와 PASS/HOLD 표를 보고하세요. PowerShell이나 수동 ZIP 작업을 사용자에게 요청하지 마세요.
