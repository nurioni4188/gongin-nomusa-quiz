# RC28 Vercel 변경 제안 (미적용)

- 조회 기준: 2026-11-05, 소스: \`nurioni4188/gongin-nomusa-quiz\`.
- 운영 \`main\` SHA: \`9ea46fc9134c55a4312241b55a82b237e86ed4a8\`.
- 운영 프로젝트 26회, RC27 1회, ibup 1회, 6r1q 1회 배포 기록 조회.
- ibup·6r1q는 같은 저장소의 같은 커밋을 import한 중복 *후보*다. 삭제 금지.
- RC27 독립 프로젝트의 기존 Production 배포/도메인과 운영 프로젝트의 Production 도메인은 변경 금지.

## 운영 환경 적용 전 검토할 변경

1. Vercel Project Settings > Git에서 각 프로젝트의 Connected Git Repository, Production Branch 및 자동배포 관련 설정을 사람이 재확인.
2. 운영/중복 프로젝트의 자동배포 중단 범위·기존 도메인 영향 평가 후 별도 승인.
3. 승인 시에만 운영 저장소의 루트 \`vercel.json\` 또는 Vercel 설정에 \`git.deploymentEnabled: false\`를 적용. RC28 개발 브랜치의 동일 설정은 **해당 브랜치의 자동배포 방지용 안전장치**이며 \`main\`에 병합해서는 안 된다.
4. RC28 PASS 이후 같은 소스 커밋에 대해 수동 Preview를 딱 한 번 실행. Production은 별도 사람 승인 없이는 금지.

## 중복 판정 보강 필요

- 프로젝트별 연결 Git 원격 URL/저장소 ID, 브랜치, Root Directory, 환경변수 키 목록(값 제외), 도메인 사용 현황 확인.
- 교차 프로젝트의 빌드 산출물 해시/배포별 SHA 대조. 현재는 동일 *소스 커밋*만 증명되며 동일 산출물/완전한 중복은 미확정.

## 주의

이 문서는 제안서이며 프로젝트 설정 변경, 삭제, Git 연결 해제, 실제 Vercel 배포를 실행하지 않는다.
