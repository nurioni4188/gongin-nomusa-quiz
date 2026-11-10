# RC36 V2.9 · 2022–2026 법령 연혁 및 핵심조문 일괄 자동검증
기준일: 2026-11-11 (KST)

## 범위와 안전원칙
- 온누리 Vercel 기존 `gongin-nomusa-rc27-preview`의 2026-11-10 배포된 Ready Preview (`dpl_4Ysy6uYNYGHwhF9dXPvd6k7dgypj`)에 대한 **읽기 전용** 검사.
- 기존 `RC36_V29_DEPLOY_RESULT.json`과 Vercel 인증 API에서 프로젝트명·팀·프로젝트 ID·배포 URL 일치 확인 후 법령 API만 GET 호출.
- Production, GitHub main, 기존 Preview, AI 설정, 환경변수, DB **변경 없음**. 원본 문제·이미지·정답 및 사용자의 인증 토큰은 공개 GitHub에 업로드하지 않음.

## 현재 사용자 제공 실증 (조문 제1조 한정)
| 연도 | 시험일 | 연혁 후보 시행일 | MST | 구분 |
|---|---|---|---|---|
| 2022 | 2022-05-14 | 2021-11-19 | 232199 | 후보 조회됨 |
| 2023 | 2023-05-27 | 2021-11-19 | 232199 | 후보 조회됨 |
| 2024 | 2024-05-25 | 2021-11-19 | 232199 | 후보 조회됨 |
| 2025 | 2025-05-24 | 2025-02-23 | 265959 | 후보 조회됨 |
| 2026 | 2026-05-23 | 미확인 | 미확인 | HOLD |

2026-05-23 시험일은 공식 Q-Net 확인: <https://q-net.or.kr/man001.do?gId=05&gSite=L>.
이 표는 전체 법령·부칙·해당 문제 정답의 확정을 의미하지 않음.

## 생성된 비공개 배포 없는 일괄검증 패키지
- 파일: `RC36_V29_5개년_법령_핵심조문_일괄검증_배포없이.zip`; SHA-256: `0d7f6da8884698a1351209b8b0c982116b7ce9a34ce869f197bbedcf12948527`. 이 ZIP은 ChatGPT 대화 내 전달용이며 공개 저장소에 업로드하지 않음.
- 파일 구성: `RC36_V29_5YEAR_ONECLICK.cmd`, `RC36_V29_AUDIT_5YEARS.ps1`, `audit_core.cjs`, `build_report.cjs`, `test_audit.cjs`, `README_START_HERE.txt`, 현재상태 문서, 파일 SHA256 매니페스트.
- API: 보호 `/api/health` → 현행법 검색 CONTROL → 다섯 시험연도 `/api/law?action=exam&year=YYYY&query=근로기준법` (년당 1회, JO 없이 법령 본문 후보 전체 수집).
- 조문 자동 점검: `001700` 제17조, `002300` 제23조, `004300` 제43조, `007400` 제74조, `009400` 제94조 + `004302` 제43조의2. 장 제목 제외, JO 중복·부분 누락·truncation·시행일·연혁 번호 확인 및 조문 SHA256 비교.
- 생성 보고: `RC36_V29_5YEAR_REPORT.json`, `RC36_V29_5YEAR_MATRIX.csv`, `RC36_V29_5YEAR_DASHBOARD.html`. 과거 실증 파일 재사용으로 가짜 PASS가 나지 않도록 이전 증거 지움. 연속 두 건 실패 시 호출 중단.
- 개발환경 검증: 순수 판정 로직 Node 9/9 PASS, 보고서 비어있을 때 HOLD 0/5 PASS, ZIP 내용 SHA256/무결성 검사 PASS, 금지된 배포·AI·main 변경 명령 없음. **Windows 실기기/실제 보호 Preview의 5개년 일괄 API 호출은 미실행**.

## 남은 관문
- 실제 2026 연혁 후보 및 5개년 핵심조문 응답 취득: HOLD
- 법령 본문 항·호·목, 조문별 시행일, 부칙과 적용례에 대한 독립 검수: HOLD
- Q-Net 공식 최종정답 1,020문항 교차확인: HOLD
- AI 해설: `EXPLANATION_ENABLED=false`, 활성화 금지

공식 API: <https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=lsEfYdInfoGuide>.
Vercel 보호 Preview CLI: <https://vercel.com/docs/cli/curl>.
