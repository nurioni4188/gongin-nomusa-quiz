# RC36 V2.7 — 모바일 정답 검증 상태·법령 조회 안내 개선
기준일: 2026-11-10 KST
브랜치: rc36/preview-law-ai (기존 Production/main 불변)

## 수정된 내용
- 문제 풀이 화면의 '최종정답'을 '정답표 대조 후보'로 변경하여 독립 검수 전임을 명확히 표시
- 풀이 피드백을 '후보답안 일치/불일치'로 표시, 통계도 후보답안 기준 안내
- 현재 법령 조회 API의 설정 누락·법령명 추출 실패·응답 오류를 한국어 메시지로 표시
- `sw.js` cache version `nomusa-rc36-v27`로 증가
- Windows 테스트: Playwright Chromium 탐색·UTF-8 백업 읽기 보완
- 기존 체크섬 manifest 갱신 (1,046개 체크섬 목록, 전체 일치)

## 검증
| 항목 | 결과 |
|---|---|
| ZIP 내부 1,020문항/CSV/PNG | 기술검사 PASS (기존 자료 불변) |
| RC36 서버 모의시험 | 6/6 PASS |
| 채점 회귀 | 11/11 PASS |
| 브라우저 DOM | 15/15 PASS |
| PC/태블릿/모바일 디자인 | 16/16 PASS |
| V2.7 UI (360,390,768,1365): 법령 성공·누락, AI 차단, 화면 넘침 | 16/16 PASS |
| localhost HTTP E2E (이 실행환경) | HOLD: net::ERR_BLOCKED_BY_ADMINISTRATOR |
| 실제 Vercel Preview V2.7 배포 | **미실행**, 기존 RC36 Preview 보존 |
| 실제 국가법령정보센터 API | **미실행** (인증 정보 없음) |
| Q-Net 원문/답안 독립 검수 | **HOLD 0/1020** |

## 산출물/보안
- 대화 산출물: RC36_V2_7_모바일정답표시개선_FULL_SOURCE.zip / RC36_V2_7_정답표시_기능검증_PATCH_ONLY.zip
- 패치는 웹 표시 파일 `index.html`, `sw.js`와 검증 테스트 및 체크섬만 변경. `data.js`, `img/`, `api/`, `ANSWER_SECOND_READ_1020.csv`, `vercel.json`은 변경 없음.
- 기출 이미지 포함 전체 ZIP을 **공개 GitHub에 업로드하지 않음**; 이 문서는 검증기록만 포함합니다.
- Production, GitHub main, DB, 승인 정답 상태, 기존 Preview URL 변경 없음.

## 다음 게이트
- Windows에서 별도 폴더에 전체 소스 추출 후 `RUN_ALL_V27_TESTS.cmd` 실행 및 localhost E2E PASS 확인
- 기존 프로젝트 `prj_J1hv2uJ6EzuWEcYtb6x4GYKpXV0i` 에서 Preview 전용 배포 및 실제 모바일 점검
- `/api/health` 서버 함수 확인; `/api/law`의 실제 OC 설정/응답 점검 (현재법령/출제당시법 구분)
- 검증 없는 AI 해설 활성화/공식 채점 승인 금지
