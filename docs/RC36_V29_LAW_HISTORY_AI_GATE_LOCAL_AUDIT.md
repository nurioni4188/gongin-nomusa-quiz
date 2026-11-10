# RC36 V2.9 법령 연혁·AI 검증 관문: 로컬 구현 기록
날짜: 2026-11-10 (KST)

## 범위
- 사용자 요청 3건: 법령 본문 항·호·목/가지번호 보존과 PARTIAL_TEXT 분류; 2022–2026년 1차 시험일 시행법 조회; 독립검증 문제만 AI 검토초안 생성.
- 기존 RC36 V2.8 Preview 및 RC27 Production 불변. GitHub main 불변.
- V2.9 전체 소스와 패치 파일은 ChatGPT 대화 내 비공개 산출물로 보관. 공개 저장소에는 문제 원문·PNG·정답 CSV·전체 ZIP 업로드 금지.

## 개발 내용
- 법령 본문 파서: 조문번호와 가지번호로 6자리 JO 조문코드; 항·호·목 계층; PARTIAL_TEXT / SECTION_HEADING / DELETED / TEXT_PRESENT_REVIEW.
- 시험일: 2022-05-14, 2023-05-27, 2024-05-25, 2025-05-24, 2026-05-23.
- 검색: `target=eflaw` 연혁 검색 후 시험일 이전 공포·시행본을 식별, 법령 `MST` + 해당 `efYd`를 조합해 본문 조회. `ID`는 과거 시행일 조회에 사용하지 않음. 중복 일련번호/연혁 누락/법령명·시행일 불일치 시 HOLD.
- AI 해설: `EXPLANATION_ENABLED=false` 유지. `api/_data/verified_evidence.json` 비어 있음 (독립검증 0/1020). Q-Net 공식 정답 파일 SHA256 및 독립 검수, 문제 원문 해시, 역사적 법령 본문/조문 SHA256, 검토자 인증 토큰이 없으면 모델 호출 차단.
- UI: 현행 법령 / 시험 당시 법령 조회 버튼 분리, 로고 RC36 V2.9 표시.

## 시험 기록
- Node API 모의 시험 14/14 PASS
- 기존 채점 11/11 PASS
- 기본 브라우저 15/15 PASS
- 디자인/반응형 16/16 PASS
- 잠정 결과 UI 16/16 PASS
- V2.9 법령 버튼 UI 20/20 PASS (360/390/768/1365px)
- 소스 해시 1,065건, PNG 1,020개 ZIP 무결성 PASS

## HOLD
- 실제 배포된 V2.9 없음. 이전 V2.8 Preview Ready 보존.
- 실시간 eflaw 연혁 조회 및 원문 XML/JSON의 항·호·목 완전성 미실증. 현재 모의응답 기준 구현 PASS만 기록.
- Q-Net 공식 정답 독립검증 0건, AI 호출 0회. 독립 검수 전 정답·시행법·AI 해설 승인 불가.
- 브라우저 API 보안·호출 제한 추가 검토 필요.

## 공식 가이드
- 시행일 본문: https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=lsEfYdInfoGuide
- 시행일 목록: https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=lsEfYdListGuide
- 조항호목: https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=lsEfYdJoListGuide
- 공공데이터포털: https://www.data.go.kr/data/15000115/openapi.do

## 2026-11-10: 기존 온누리 Vercel Preview 원클릭 배포·연혁 API 실증 준비
- Vercel MCP 읽기 권한 재조회: 기존 온누리 프로젝트/배포 모두 404. 브라우저 및 사용자 CLI에서 확인한 프로젝트 존재와 구별. 연결에서 직접 배포 미수행.
- 단일 압축 해제 산출물(비공개): `RC36_V29_ONNURI_PREVIEW_원클릭배포_연혁5개년검증.zip` (약 30.4 MB), SHA256 `70e2ed41a9d2a6e362e8674093c5498415f16ece609f7e51debe4ecadeeb23c2`, ZIP 무결성 PASS, 이미지 1,020개, 정적 소스 해시 1,066개 PASS.
- Windows 배포기: `RC36_V29_PREVIEW_ONLY.cmd`, Vercel CLI 58.5.1 고정; 사용자 소유 기존 프로젝트 ID `prj_J1hv2uJ6EzuWEcYtb6x4GYKpXV0i` 및 팀 `team_9yqmbClGzw0BPGCsoS6CNXUB`의 REST 응답 ID·이름·소유팀과 Preview 보호 설정 확인 후 `vercel deploy --target=preview`만 허용. 과거 V2.8에서 문제였던 사람이 읽는 `vercel project inspect` 텍스트 기반 ID 중복검사 제거. 재실행 방지를 위해 배포 요청 **전에** `attemptStarted=true`를 디스크에 기록함.
- Ready 후 Vercel CLI의 보호된 배포용 `vercel curl`을 사용해 Preview `/api/health` 및 시험일 기준 근로기준법 조회 2022~2026년 5건 `/api/law?action=exam&year=YYYY&query=근로기준법&jo=000100` 자동 시험 설계. 인증 보호 해제/키 출력 없음. 연혁 조회 실패는 **Preview Ready와 별개로 HOLD**. AI 설명은 명시적 `EXPLANATION_ENABLED=false`.
- 이번 실행환경 오프라인 재검증: server/history/AI-gate 14/14, scoring 11/11, UI law controls 20/20, 1,020문항 integrity 0 errors; zip source manifest PASS.
- **실제 Windows 실행 미실시**, V2.9 Preview URL 미생성, 연혁 API 라이브 응답 미확인; 과거 V2.8 Preview 유지. 새 배포 시도 뒤 오류면 결과 JSON과 Vercel Deployments를 확인하고 절대 중복 요청하지 말 것.
- 공식 API 규격 근거: https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=lsEfYdListGuide ; https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=lsEfYdInfoGuide ; 인증된 Preview 검증 문서: https://vercel.com/docs/cli/curl

## V2.9 Windows Node REPL 실행기 핫픽스 (2026-11-10)
- Windows 사용자 출력: 1,066 소스 및 1,020 이미지·문항 무결성 PASS 다음 `CHECK: V2.9 law and AI-gate mocks`에서 `Welcome to Node.js v24.18.0. >` 대화형 실행 모드 진입.
- 원인: `RC36_V29_PREVIEW_ONLY.ps1`의 `Run-Test` 및 `Run-Vercel`에서 PowerShell 자동 변수 `$args`를 인수 매개변수 이름으로 사용해 외부 실행명령 인수가 비어버림. V2.8 정상 실행기의 `$arguments` 방식과 비교해 확인.
- 변경: 두 함수 매개변수를 `$arguments`로 바꾸고 `node --test` 및 `npx.cmd vercel ...` 호출에 스플랫 전달. 전달 인수가 0개면 즉시 HOLD. 기타 원본 V2.9 소스 및 게이트 무변경.
- 원본 실행기 SHA256 `472dc7c2933ddea684b8f3c07c88113f29db71ff1e7a6549933c57d5bf33e5f6`; 교체 실행기 SHA256 `45c1781bc9d3f6fc015906eb0aca7c4987e01c4ad4bab01390a5b44feaadf7ce`. 파일 diff는 함수 인수 이름과 2개 누락 검사뿐임.
- 비공개 산출물 `RC36_V29_NODE_REPL_오류수정_원클릭패치.zip` SHA256 `b45e87898cd55a2f71e245ba23c9d29648753ecbc484d3f7ac11933fb59adba5` (약 8 KB). 한 번 압축 풀고 `RC36_V29_FIX_AND_CONTINUE.cmd` 실행. 파일은 정확히 한 개의 기존 V2.9 폴더만 찾아 원본 SHA 확인 후 백업·교체; `attemptStarted=true`이거나 결과 JSON 오류/중복 폴더면 중단.
- 오프라인 확인: Node 법령·AI 시험 14/14 PASS, Python 패치 반복적용/원본 해시/배포이력 재시도 차단 모의시험 PASS, ZIP 내부 무결성 PASS. **Windows 최종 실행은 미검증**, **V2.9 Preview 미배포**, 법령 연혁 실제 API HOLD, 공식정답 독립검증 HOLD, AI disabled 유지.

## 2026-11-10 23:26 KST V2.9 Preview READY / 연혁 API 사후검증 HOLD
- Windows 실제 배포 결과(사용자 제공 `RC36_V29_DEPLOY_RESULT.json`): `PASS_PREVIEW_READY_HISTORY_HOLD`; `sourceVerified=true`, `remotePreflight=true`, `protectionVerified=true`, `attemptStarted=true`, `previewReady=true`. 배포된 URL: `https://gongin-nomusa-rc27-preview-m0v8o5fdh.vercel.app`, 배포 ID `dpl_4Ysy6uYNYGHwhF9dXPvd6k7dgypj`. 배포 후 브라우저/API 실증은 별도.
- 원본 자동검증: 소스/문항 1,020, 도메인 테스트, 1365/768/390/360 로컬 HTTP E2E 모두 PASS. 공식 정답 독립검증은 false, AI 활성화 false, Production 변경 false, Git main 변경 false.
- **연혁법령 0/5 HOLD**: `message: HOLD: Vercel CLI failed: curl`; 배포 후 `vercel curl` 실행이 실패했고 실제 연혁 API 응답은 단 한 건도 수집하지 못함. 기존 Ready Preview를 다시 배포하지 말 것.
- 사후검증 코드 점검: 기존 `RC36_V29_PREVIEW_ONLY.ps1`은 `vercel curl https://<hostname>/api/health --scope ...`로 전체 URL을 사용했음. 공식 문서에서는 특정 배포 요청에 `vercel curl /api/health --deployment https://<hostname> --scope ...` 사용. 이 차이는 실패 원인 후보이며, 원래 오류 stderr가 없으므로 확정할 수 없음. <https://vercel.com/docs/cli/curl>.
- 비공개 검증 전용 ZIP `RC36_V29_배포없이_5개년_연혁API_검증전용.zip` 생성 (약 5KB, SHA256 `3e5a6c0bc305357f207d748d572fd204bc8a5dc1be1df54062502432a295cebb`). 배포완료 결과와 정확한 팀/프로젝트/배포 URL 검증 후 Vercel CLI 읽기 전용 API·인증된 `curl`만 호출. 5개년 후보 응답은 연도별 요약만 `RC36_V29_HISTORY_ONLY_RESULT.json`에 기록. 배포·Production·GitHub·API 키·AI 호출·보호 설정 변경 기능 없음. Windows 실기기 실행 및 실제 연혁 조회 결과는 현재 미확인.
- 사후검증 파일이 생성되더라도 `PASS_HISTORY_CANDIDATES_5_OF_5`는 독립검증된 시험법/공식 정답에 대한 승인 의미가 아님. 본문·부칙·적용례 및 공식 Q-Net 정답 검수는 HOLD.
