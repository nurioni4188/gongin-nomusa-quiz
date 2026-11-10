# RC36 V2.8 — 모바일 결과·통계 잠정판정 정합성 검사 (2026-11-10)
기준: 이전 RC36 V2.7 전체 소스, `rc36/preview-law-ai` 브랜치. **GitHub 공개 저장소에는 문제 이미지/정답 CSV를 업로드하지 않음.**

## 변경 (별도 비공개 소스 ZIP)
- 시험 결과: '후보답안 일치 수 / 잠정 환산점수' 표기. '과락 면함 / 과락 기준 미만'이라는 합격·과락 확정 문구 제거.
- 연습/실전 과목 결과: '후보 일치 / 잠정 점수'로 수정.
- 통계: '정답/정답률' → '후보 일치/일치율'; '통계·잠정' 표시.
- 복습: '현재 후보 불일치', '복습할 문항' 등 잠정판정 문구로 변경.
- SW 캐시 버전: `nomusa-rc36-v28`으로 증가.

## 실제 수행한 검증
| 관문 | 결과 |
|---|---|
| RC36 서버 모의 함수 | PASS 6/6 |
| 채점 회귀 (전체 문항 로딩 포함) | PASS 11/11 |
| 기존 브라우저 DOM 회귀 | PASS 15/15 |
| PC/태블릿/모바일 CSS | PASS 16/16 |
| V2.7 법령·해설 차단/모바일 UI 회귀 | PASS 16/16 |
| V2.8 시험 결과/통계/복습/기록 불변성 (360,390,768,1365px) | PASS 16/16 |
| 무결성 | PASS 1,020문항·1,020이미지 및 SHA-256 manifest 1,046/1,046 |
| V2.7 대비 데이터/API/프로젝트 설정 변경 | 0건 |
| 공식 원문·정답 독립 검수 | HOLD 0/1,020 |
| 실제 법령 API·Windows 실기기 / 원격 Preview V2.8 | HOLD / 미실행 |

## 원격 상태 및 제한
- 기존 CLI 배포 RC36 Preview URL: `https://gongin-nomusa-rc27-preview-jn2cnfe5p.vercel.app` (기존 배포 보존).
- ChatGPT의 지정 Vercel 연결에서 프로젝트 `prj_J1hv2uJ6EzuWEcYtb6x4GYKpXV0i` 및 배포 URL 읽기 전용 조회는 다시 404. 따라서 **V2.8 새 Preview 배포는 실행하지 않음**.
- 전체 V2.8 소스는 비공개 대화 산출물에만 보관함. 공개 저장소의 `main`, Vercel Production, 기존 Preview, DB·법령/AI API 환경변수와 공식 채점 승인상태 변경 없음.

## 안전한 다음 관문
1. 기존 Vercel 계정으로 실제 프로젝트 연결 복구 후 Preview 전용 새 배포.
2. 배포된 URL에서 원문 이미지, 후보 정답·잠정 점수, PWA 캐시, 데이터 백업, 법령 API 설정 및 모바일 360/390 실제 접속 검증.
3. Q-Net 정답 독립 검수 전까지 '공식 채점 승인' 및 AI 해설 활성화 금지.

## 2026-11-10 V2.8 기존 프로젝트 Preview 실행 준비
- V2.8 비공개 전체 소스 ZIP SHA-256 확인: `4f6fa3b476270dc0c54eefdbee29444f75cb9141dba7a1c2adc54a6246b1637b` / ZIP 무결성 PASS.
- 동일 파일을 이번 세션에서 재실행: 서버 모의 6/6, 채점 11/11, 1,020문항 무결성 0 errors, V2.8 잠정판정 UI (360/390/768/1365px) 16/16 PASS.
- 기존 프로젝트 `prj_J1hv2uJ6EzuWEcYtb6x4GYKpXV0i`, 팀 `team_9yqmbClGzw0BPGCsoS6CNXUB`에 대해 Vercel MCP: 프로젝트 GET 404, 배포목록 GET 403. 사용자의 대시보드에는 기존 Preview Ready가 확인됨. 연결 접근과 프로젝트 존재를 혼동하지 말 것.
- 직접 배포는 수행하지 못함. 대신 **원본 V2.8 ZIP이 포함된 단일 Windows CLI 실행패키지**를 생성 (기존 계정/프로젝트 정확 일치 및 Preview 보호 확인 후에만 배포, CLI Project Inspect, 자동시험, POST-deploy Ready 검사; GET failure/권한 에러 시 HOLD). 패키지명 `RC36_V28_기존프로젝트_Preview_자동배포_안전패키지.zip`.
- **사용자 Windows 실기기에서 신규 실행파일을 돌린 결과는 없음**. 따라서 V2.8 Preview READY로 표기하지 않음. 이전 V2.5 Preview 그대로 보존.
- GitHub 공개 repo에 원문/이미지/전체 ZIP 업로드 금지; main, Production, DB 무변경; 공식 정답 독립검수/AI 해설/법령 실제 API HOLD.

## V2.8 단일 압축 해제 버전: 소스 ZIP 누락 오류 개선
- 기존 Windows 실행 로그: `HOLD: V2.8 source ZIP is missing beside this runner.` 해당 단계에서 신규 배포 미시도.
- 기존 패키지를 검사한 결과 원본 ZIP은 있었지만 실행기와 같은 폴더에서만 찾는 방식 때문에 불완전 압축 해제/부분 이동에 취약함.
- 수정: 내부 중첩 ZIP을 **0개**로 제거하고 `RC36_V28_ONECLICK/nomusa-quiz-web/` 전체 소스 및 `RC36_V28_PREVIEW_ONLY.cmd`가 함께 추출되도록 평탄화.
- 소스 파일 정적 SHA-256 **1,061개 PASS**, PNG **1,020개 PASS**, ZIP 무결성 PASS. 가변 생성 파일 `audit/rc36_1020_audit.json`은 정적 해시 대상에서만 제외하고 파일 보존. 자동감사 실행 뒤 반복 검증도 PASS.
- 오프라인 회귀: 서버 6/6, 채점 11/11, DOM 15/15, 디자인 16/16, V2.8 UI 16/16, 문항 정합성 PASS. localhost HTTP 시험은 현 컨테이너 환경 정책으로 HOLD.
- 산출물: `RC36_V28_FLAT_ONECLICK_FIXED.zip` (대화의 비공개 다운로드 파일; 공개 GitHub에 기출 원본 미업로드). 실제 Windows 실행 및 Preview 배포는 미실행이므로 READY로 표기하지 않음.
- 고정 대상: 온누리 Vercel 팀·기존 프로젝트의 **Preview만**. RC27 Production, GitHub main, DB 변경 없음.

## 2026-11-10 V2.8.1 CLI 프로젝트 출력 검사 오류 수정
- 사용자의 Windows CLI 실제 실행에서 `HOLD: CLI project inspect did not show expected ID`. V2.8 실행기 순서상, 이 메시지는 이미 실행된 Vercel `/v9/projects/{id}` API의 프로젝트 ID·명칭·팀 일치 검사 및 Preview 보호 설정 검사를 통과한 뒤 발생함. **배포 요청 전 HOLD**, 신규 Preview 없음.
- 원인: 사람용 `vercel project inspect` 텍스트 출력에 프로젝트 ID가 반드시 들어 있어야 한다고 잘못 가정한 중복 검사. API 검사와 달리 버전/출력 스트림에 영향을 받음.
- V2.8.1 수정: `$cliInspect=Run-Vercel @('project','inspect',...)` 및 해당 텍스트 기반 Gate만 삭제. 인증된 Vercel REST API의 **프로젝트 ID·이름·팀** 일치 검증과 보호 설정 Gate는 그대로 유지.
- 원본 런처 SHA256 `d92245e6a7fe874112d3edeeb16667b768c577850b6d9579585deb0ead227e1d`, 패치 런처 SHA256 `23f12cd915bc760fd2eb8bda80c3d18db88c72683546c5a841a28ee79f11adb8`.
- 소형 ZIP `RC36_V281_CLI_프로젝트확인_원클릭수정.zip`은 사용자 PC의 기존 `Downloads/RC36_V28_FLAT_ONECLICK_FIXED/RC36_V28_ONECLICK` 폴더 한 곳만 검색하고 기존 실행 결과의 `attemptStarted=true`를 먼저 차단한 뒤 런처만 백업·교체하도록 구성. 실제 Windows 실행은 아직 미확인.
- 정적 Gate 유지 검사 및 ZIP 무결성 PASS. 소스·기출 이미지·정답·GitHub main·Production·DB 무변경. 이번 세션에서 새 Vercel Preview 요청하지 않음.
