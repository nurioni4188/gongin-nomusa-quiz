# RC28: 검증 PASS 전에는 Vercel 배포 금지

## 보존·권한
- GitHub \`main\` / 운영 프로젝트 / RC27 기준본의 변경 금지.
- \`rc28/offline-ci-hold\` 브랜치에서만 검증용 코드 추가.
- 루트 \`vercel.json\`의 \`git.deploymentEnabled:false\`는 **개발 브랜치의 자동배포 차단 안전장치**. Vercel 프로젝트의 live Settings/API는 수정하지 않음.
- 실 배포/Production 승인 기능은 구현하지 않음. 이 브랜치를 \`main\`으로 병합하지 말 것.

## 실행
1. Node.js 22 이상 및 Python 3.11 이상 설치.
2. \`node scripts/rc28-audit.mjs --strict\`  (현재 공식 정답/원문 정보 누락이므로 **HOLD가 정상적인 안전 판정**).
3. \`python -m pip install playwright==1.56.0\` 및 \`python -m playwright install chromium\`
4. \`python scripts/rc28-browser.py\` (오프라인 file:// Chromium; desktop/tablet/Android 화면 시뮬레이션).
5. \`node scripts/rc28-gate.mjs\` — 모든 항목 PASS일 때만 PASS_CANDIDATE, 그 외 HOLD.
6. 생성되는 \`rc28-evidence/*.json\`과 스크린샷을 확인. 개인 정보/인증 자료는 저장하지 않음.

## 승인 관문
- 2022~2026 기출 목표 문항(1,020) 충족.
- 모든 문항 정답이 공식 최종정답 대조된 0..4 정수이고, 중복/빈 선지/원문 출처 누락/임시 해설 없음.
- PC·태블릿·Android 너비 390/360의 퀴즈 흐름 및 가로넘침 검사 PASS.
- 승인 후보 PASS_CANDIDATE가 되어도 자동 배포하지 않는다. 실제 Preview 1회는 사용자가 별도로 승인한 후 **수동** 진행한다.
- 실기기 Android 시험/원문 대조는 Chromium 에뮬레이션·구조검사와 별개로 사람이 확인해야 한다.

## GitHub Actions 비용 절감
- \`rc28/offline-ci-hold\` 브랜치의 관련 파일 변경 시만 실행, 동일 브랜치 동시실행 취소.
- Vercel CLI/API 및 모든 배포용 자격증명 미사용.
- 소스 데이터가 불완전한 현재는 의도적으로 HOLD이며 운영/RC27 릴리스 금지.
