# RC34 Focus Study — 디자인 개편 기록

RC33 기술검증본 기반 UI 개선. 기존 채점·저장·정답·이미지 데이터 변경 없음.

## 화면
- 데스크톱 좌측 세로 사이드바, 태블릿 가로 메뉴, 360·390px 모바일 2단 상단 메뉴
- 독자적인 다크 블루 Focus Study UI, 라이트 모드 전환 제공
- 학습 진행률 링, 3개 통계 카드, 설정 패널, 5개년×6과목 학습지도
- 문제풀이의 원문 이미지/글자 보기, 답안 버튼, 실전 제출 흐름 유지
- 테마 버튼 첫 클릭 반전 동작 개선, 선택지의 button 요소/aria-pressed 적용
- 키보드 포커스 링, 모바일 최소 터치 크기, reduced-motion 지원

## 기존 데이터 보존 및 검증
- RC33 data.js, ANSWER_SECOND_READ_1020.csv, 1,020개 PNG 바이트 동일
- Node 로직회귀 11/11 PASS
- Chromium JS-injected DOM 기능 15/15 PASS (HTTP/SSO 대체 불가)
- RC34 독립 반응형 디자인·경로·테마 E2E 16/16 PASS
- 기술적 무결성 1,020/1,020 PASS; Q-Net 원문/최종정답 독립검증 HOLD

## 배포 정책
- RC34은 ZIP 소스 패키지와 브라우저 시안 생성까지만 수행
- Preview 배포 스크립트는 기존 보호된 Vercel 프로젝트만 대상이며 SSO 검증 실패 시 중단
- Production 배포 금지, 실제 HTTPS/보호인증/실기기 Human UAT 미완료 시 승인 HOLD
- `.vercelignore`는 로컬 테스트 증빙, 소스 실행 스크립트, 독립 대조 CSV를 배포 제외
