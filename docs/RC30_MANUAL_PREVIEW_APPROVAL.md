# RC30 수동 Preview 승인 요청서 — 현재 HOLD

## 기준선
- 저장소 nurioni4188/gongin-nomusa-quiz
- RC29 브랜치 rc29/question-bank-validation
- 운영 main 기준 9ea46fc9134c55a4312241b55a82b237e86ed4a8
- RC27 기준 배포 dpl_C3UoeToNVQeZEymcMCsrtKj5ygFu

## 필수 관문
- [ ] 2022~2026 A형 원문·최종정답 1,020문항 100% 실물 대조
- [ ] 보기 5개, 문제번호·원문 수식·표·첨부 이미지·출처페이지 점검
- [ ] 복수정답·정답 변경·무효 문항 처리
- [ ] 공식답과 화면정답 자동채점 테스트 정확도 100%
- [ ] 누락 0, 중복 0, 과목별 범위외 번호 0, 원문 손상 0
- [ ] PC 1365 / tablet 768 / mobile 390·360 Playwright PASS
- [ ] Android 실기기 수동검수 별도 수행
- [ ] CI 최종 승인관문 PASS_CANDIDATE
- [ ] 사용자 명시적인 수동 Preview 1회 승인

## 금지
Vercel Preview/Production, 프로젝트 변경/삭제, main 변경, RC27 수정, 자동배포 설정 변경은 본 RC29 개발 범위에서 금지.
