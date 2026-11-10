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
