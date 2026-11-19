# NOMUSA V17 — 2007~2026년 20개년 편집용 통합답안 전체 배치 (2026-11-17)

## 실행 범위
- 기존 2022·2023·2025년 편집후보 19+19+19=57개 유지.
- 나머지 **17개 연도·271개** 기존 canonical 답안을 상세·압축으로 모두 정리.
- **20개년 등록 답안 328개**, 연도별 Markdown 20개·JSON 20개를 포함한 완성형 학습자료 패키지 생성.
- 원본과 현재 표시본 보존. 180자 이상 완전 동일한 긴 문단만 자동 중복 제거. 서로 다른 법리·논증을 비슷하다는 이유로 합치지 않음.
- 사용자 스킬: `.agents/skills/nomusa-essay-editorial-batch/SKILL.md` 업데이트. 추가 스크립트 `second/nomusa-v17-remaining-17years-editorial.js`, 공통 추출기 `scripts/nomusa_editorial_batch.py`.
- 출력: 연도별 원문 전사·상세/압축답안, 기출 원장 배점·분량 목표·출처 상태. 원장 구조가 다른 레거시 parent와 개별 소문항 ID를 구분.

## Chromium 실제 실행 및 파일 증빙
- 검증 실행: https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44037657929
- 검증된 코드 SHA: `57b406451a5f995edcc662dfb85e94cd08cf6fa2`
- GitHub Actions conclusion **SUCCESS**, 실제 Chromium PC1440·Mobile390·Mobile360 통합 학습 UI 회귀검사.
- GitHub Actions artifact: `nomusa-remaining-17years-editorial-candidates`, ID `14307862428`, 약 1.3MB ZIP. 연도별 Markdown 17개·JSON 17개·검증 manifest 1개, 총 35개 파일.
- 2022 artifact: `nomusa-2022-19x32-editorial-candidate`; 2023·2025 artifact: `nomusa-2023-2025-38x69-editorial-candidates`, 동일 실행에서 확인.
- 원본 실행의 내용증거: `nomusa_remaining_17years_editorial_manifest.json`에서 **총 271개 등록 문항의 답안 출력, 누락 텍스트 없음**, 문제 항목 26건은 2019·2020년 원장 배점 미확정임을 확인.

## 연도별 수량 (나머지 17개년)
| 연도 | 답안 | 검증 문제 |
|---|---:|---|
| 2007 | 13 | 배점 미확정 0 |
| 2008 | 14 | 0 |
| 2009 | 14 | 0 |
| 2010 | 17 | 0 |
| 2011 | 17 | 0 |
| 2012 | 19 | 0 |
| 2013 | 19 | 0 |
| 2014 | 19 | 0 |
| 2015 | 6 | 0 |
| 2016 | 6 | 0 |
| 2017 | 6 | 0 |
| 2018 | 6 | 0 |
| 2019 | 19 | **13 — 원장 배점 확인 필요** |
| 2020 | 19 | **13 — 원장 배점 확인 필요** |
| 2021 | 6 | 0 |
| 2024 | 34 | 0 (개별 소문항 ID로 배점 확인) |
| 2026 | 37 | 0 (개별 소문항 ID로 배점 확인) |
| 합계 | **271** | **26** |

2019·2020년 등록 소스 중 26개는 명시적으로 `POINTS_UNVERIFIED`로 처리하고, **배점·장수 목표를 창작하지 않았다**. 나머지 레거시 원고는 하나의 배점단위로 출력했으며, 과거 복합 기출문항의 원본 소문항별 분할이 검증된 것으로 표기하지 않았다. 2024년 34개와 2026년 37개는 각각 이미 분리된 개별 점수 문항 ID로 등록되어 있고 정확히 구분해 출력했다.

## 최종 검증 판정
- **PASS**: 전 연도 등록원고의 편집용 원고 및 JSON 328개 레코드 보존·출력 / Chromium 실제 웹앱 표시본 / Github Actions 성공 / 원고의 기존 ID와 상세·압축 보존 / 신규 Vercel 배포 없음.
- **HOLD**: 2019·2020 원장 배점 26개 / 과거 복합 기출 소문항 배점·원본 PDF 이미지 전수 대조 / 시험 당시 시행법·판례 원문 / 학술 원전 / 50점 8~10장·25점 4장 실제 수기시험 분량 / 독립 전문가 최종 내용승인.
- 이번 성과는 **'20개년 최종 편집후보본 전수 생성'**이지 **'20개년 법리·학술 최종 검증 완료'**가 아님. 정확히 구분하여 관리.
- GitHub `main`, RC27/RC35, 기존 Preview 및 Vercel Production 유지. 새 프로젝트·서버·DB·AI 채점·배포 없음.

## 재실행
스킬 `.agents/skills/nomusa-essay-editorial-batch/SKILL.md`와 `.github/workflows/nomusa-canonical-e2e.yml` 기준으로 기존 검토 브랜치에서만 수정·검사. 사용자 승인 전 운영 반영 금지.
