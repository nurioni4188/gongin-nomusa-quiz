# RC36 복원·자동검증 점검 (2026-11-10 KST)

## 기준 소스
- 원본 아카이브: RC36_Nomusa_Law_AI_Explanation_FULL.zip
- SHA-256: `584a179be7e1df598d4a964ffc08bcbbbac55bba607abd0acb89b5a6e3ea10cb`
- ZIP 검사: 무결, 1,092개 엔트리
- GitHub Desktop 반영용 아카이브: RC36_GITHUB_DESKTOP_IMPORT_READY.zip; 핵심 10개 파일 원본과 바이트 일치
- **주의**: 본 GitHub 브랜치에는 전체 소스와 1,020 이미지가 아직 업로드되지 않았음. 전체 소스 GitHub 복원 완료로 판정하지 않음.

## 이번 작업에서 실행한 자동시험
| 구분 | 결과 |
|---|---|
| 1,020 문항·CSV·이미지 수량 검사 | PASS_TECHNICAL_ONLY |
| 법령/AI 서버 함수 격리 모의시험 | PASS 6/6 |
| 오프라인 학습·채점 로직 | PASS 11/11 |
| 브라우저 DOM 테스트 | PASS 15/15 |
| 반응형 디자인 1365/768/390/360 | PASS 16/16 |
| 추가 Chromium set_content 홈 화면 4규격 | PASS_RENDER_NO_OVERFLOW |
| 실제 localhost HTTP Chromium E2E | HOLD_ENVIRONMENT_BLOCKED |
| 공식 원문·최종정답 1,020개 독립 검수 | HOLD 0/1020 |
| 법령 API/OpenAI 실제 연결 | HOLD_NOT_EXECUTED |
| Vercel Preview | HOLD_PROJECT_404 |

RC36 감사 데이터 요약: 1,020개, 현행법 검색 후보 462개, 법령명 자동 미추출 558개, OCR/원본 텍스트 검토 HOLD 150개, 독립 검수된 해설 0개.

## Vercel 조회 및 안전조건
- 의도한 연결 계정: `onnuri4188@gmail.com`
- 확인된 팀: `onnuri4188gmailcoms-projects`, ID `team_9yqmbClGzw0BPGCsoS6CNXUB`
- 의도한 프로젝트: `gongin-nomusa-rc27-preview`, 아카이브 기록 ID `prj_J1hv2uJ6EzuWEcYtb6x4GYKpXV0i`
- 프로젝트명/ID 조회: 모두 404. 팀 프로젝트 목록에서도 해당 프로젝트 미확인
- 원인: 현재 접근 가능한 연결 상태에서 프로젝트 존재/접근을 확인할 수 없음 (삭제, 이전, 권한 변경 등 단정 불가)
- **GitHub main·Vercel Production·DB·공식 정답 승인 상태 변경 없음**
- `vercel.json`의 `git.deploymentEnabled=false` 유지
- `EXPLANATION_ENABLED=false` 기본 차단 유지; 실제 법령/API 키 검증 전에 변경 금지

## 후속 관문
1. 소스 ZIP을 `rc36/preview-law-ai` 브랜치 루트에 완전 업로드하되, 권리·비밀값·PNG 공개 여부 사전 확인
2. 커밋 해시/파일 수/이미지 수/무결성 및 차단 규칙 검증
3. 기존 Vercel 프로젝트 접근 복구 후 Preview 전용 배포
4. Preview API / 실제 HTTP 브라우저 E2E / 모바일 UAT 실시
5. 공식 문제·선택지·최종정답 독립 대조 완료 전 1,020개 자동채점 최종승인 금지

**검증 결론**: LOCAL_TECHNICAL_PASS / GITHUB_FULL_IMPORT_HOLD / VERCEL_PREVIEW_HOLD / OFFICIAL_ANSWER_HOLD.

## 2026-11-10 추가 실제 재검증 및 배포안전 판정
- 기존 ZIP SHA256 `584a179be7e1df598d4a964ffc08bcbbbac55bba607abd0acb89b5a6e3ea10cb` 일치. 1,092개 파일, 문제 이미지 `img/` 1,020개 확인
- 이번 실행: 채점 11/11, 서버 격리시험 6/6, DOM 15/15, 반응형 16/16 모두 PASS
- 실제 `http://127.0.0.1` Playwright는 `net::ERR_BLOCKED_BY_ADMINISTRATOR`로 HOLD. 단순 렌더링 PASS를 실제 HTTP E2E PASS로 대체하지 않음
- 사용자 Vercel 대시보드 화면에서는 기존 `gongin-nomusa-rc27-preview`의 Production이 Ready로 보임. 그러나 연결된 Vercel API에서는 이름·ID 조회 모두 404, 팀 내 프로젝트 목록에는 `comwel-ai-stt-poc`만 표시. **대시보드 존재와 연결 접근 미확인을 구별할 것**
- 공개 GitHub 브랜치에 전체 기출 문제 이미지/정답 데이터를 일괄 업로드하면 원문이 공개될 위험이 있으므로 업로드 HOLD. 현재 로컬 전체 소스는 별도 보존
- CLI Preview 전용 테스트·팀/ID/보호 설정 검증 패키지를 준비했으나, 원격 Preview 업로드는 아직 실행하지 않음
- `main`, Production, DB, AI 설명 활성화, 공식 채점 승인: 변경 없음

## 2026-11-10 Preview V2 자동화 추가 결과
- 원본 RC36 ZIP SHA-256 재확인 PASS: `584a179be7e1df598d4a964ffc08bcbbbac55bba607abd0acb89b5a6e3ea10cb`.
- Playwright Chromium 하드코딩된 Linux 실행 경로를 별도 검증용 복사본의 테스트 파일 2개에서만 호환 수정. 원본 ZIP 및 runtime source 변경하지 않음.
- 수정된 검증용 복사본 재실행: Node 서버 모의시험 6/6, 채점 11/11, DOM 15/15, 디자인 16/16 PASS. 문항·정답·PNG 1,020개 구조 검사 PASS_TECHNICAL_ONLY.
- 실 localhost Playwright는 실행환경 정책 `net::ERR_BLOCKED_BY_ADMINISTRATOR` → HOLD.
- 지정 Vercel 계정/팀의 기존 프로젝트명 및 ID 조회 재시도 모두 404, 팀 필터 목록 결과 0개 → Preview 배포 실행하지 않음.
- V2 Windows 원클릭 자동검증/Preview 전용 패키지는 원본 전체 ZIP을 동봉하여 구성했고, **읽기 전용 프로젝트 조회→정확한 ID/팀·접근 보호 확인→Preview 전용 배포** 순서로만 수행하도록 함. 잠재적으로 새 프로젝트를 만들 수 있는 `vercel link --yes` 제거.
- Windows cmd/ps1 실제 실행 및 원격 배포는 아직 검증되지 않음. GitHub 공개 저장소에 1,020문항 원본/정답 업로드 금지. main, Production, DB 변경 없음.

## 2026-11-10 V2.4 Windows UTF-8 다운로드 테스트 보정
- 사용자 Windows 실제 localhost E2E: 앞 6단계 PASS 후 `backup_download_json`에서 cp949 기본 파일 디코딩 오류로 HOLD.
- `portability_patch.py`가 ZIP 압축 해제 후 **시험 파일만** 수정하도록 확장: `tests/smoke_ui.py` JSON 다운로드 읽기 및 검사결과 쓰기 인코딩 `utf-8` 명시.
- 원본 RC36 ZIP, 채점/런타임 파일, GitHub main, 운영판 변경 없음.
- 패치 2회 연속 멱등 시험 PASS; Python 문법 PASS; 서버 모의 6/6, 채점 11/11, DOM 15/15, 화면 16/16 PASS; PATCH ZIP 무결성 PASS.
- 이 실행환경의 **real localhost HTTP E2E**는 `net::ERR_BLOCKED_BY_ADMINISTRATOR`로 HOLD. 사용자 Windows V2.4 재실행 전 8/8 PASS를 주장하지 않음.
- 기존 Vercel 프로젝트 접근 404, Preview 배포는 계속 HOLD. 공식 정답 승인 HOLD.
