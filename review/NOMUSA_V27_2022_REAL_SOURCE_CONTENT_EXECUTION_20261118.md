# NOMUSA V27 — 2022년 기출 19개 답안의 공식 판결·학술 원전 제한적 검증

기준일: **2026-11-18 한국시간**. 저장소 `nurioni4188/gongin-nomusa-quiz`, 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`.

## 검증 범위 및 결론

**기술검증 PASS / 2022년 19개 중 6개 답안의 일부 주장에 대한 공식 근거 대조 PASS / 나머지 13개 외부 원전 직접 검증 HOLD / 전문가 최종승인 HOLD (0/328).**

- 실제 Chromium 20년 328문항의 기출 원문·상세·압축답안 SHA를 기존 V23 328행 원장과 일대일 비교했고, 2022년 19개·32소문항의 식별·배점·원고 SHA 일치를 확인했다.
- 공식 출처에서 확인한 내용은 6개 문항 내 **구체적인 판례 법리·저널 서지·학술 초록 및 수식 계산**에 한정된다. 6개 답안 전체 내용 또는 19개 전수 학술 검증이 아니라는 점을 명확히 기록한다.
- 이 단계에서는 새 판례·개정법·학자·연도를 AI가 생성하지 않았으며, 원고 내용·문항 ID·수험생 저장키·앱 화면을 수정하지 않았다.

## 실제 공식·출판사 자료를 대조한 항목

| 문항 | 이번에 직접 확인한 주장과 근거 | 판정 경계 |
|---|---|---|
| `2022-admin-2` | 대법원 2019두52386(2020.2.20.)과 2021두46285(2022.7.14.)의 **구제신청 시점 구별**. [판결문 1](https://www.law.go.kr/LSW/precInfoP.do?mode=0&precSeq=226111), [판결문 2](https://law.go.kr/LSW/precInfoP.do?precSeq=232945) | 공개 법리 관련 부분 확인, 정년규정 사례포섭·시험 당시 법령 전문 검토 HOLD |
| `2022-labor1-2` | 대법원 2019다238053(2022.4.28.), 지급조건·실제 관행·퇴직자 비례 정기상여금 및 통상임금성. [법원 판결문](https://www.law.go.kr/LSW/precInfoP.do?precSeq=220865) | 판시법리 관련 문단 확인, 시험 당시 개별 법률 적용 최종심사 HOLD |
| `2022-labor2-2` | 대법원 2017도2478(2020.7.29.), 산별노조 간부 사업장 순회·시설관리권·안전목적. [국가법령정보센터 판례](https://www.law.go.kr/LSW/precInfoP.do?precSeq=226477), [대법원 판시요지](https://www.scourt.go.kr/supreme/news/NewsViewAction2.work?gubun=4&searchOption=&searchWord=&seqnum=7248) | 공식 판시요지·주요 사실 확인, 전체 판결문 문장별 대조 HOLD |
| `2022-hr-1` | Goldstein(1978) [SAGE 학술지 원전 서지·초록](https://journals.sagepub.com/doi/10.1177/001872087802000202): **Human Factors 20(2), 131–144** 및 4단계 타당도 | 초록·서지 확인. 초안 내 오래된 오기 정리와 전문 검토 HOLD |
| `2022-org-2` | [Tversky & Kahneman(1974)](https://www.science.org/doi/10.1126/science.185.4157.1124), [Staw(1976)](https://www.sciencedirect.com/science/article/pii/0030507376900052), [Nickerson(1998)](https://journals.sagepub.com/doi/10.1037/1089-2680.2.2.175), [Fischhoff(1975) 재간행](https://qualitysafety.bmj.com/content/12/4/304) 원저 서지 | 출판사 서지·공개 초록/재간행물 범위, 실험 전문·이론 적용 검증 HOLD |
| `2022-econ-2` | 2인 소득점유율 20%/80%에서 로렌츠 면적 B=0.35, 지니 G=0.30을 독립 연산해 기존 답안 값 일치 | 계산식 검사 PASS, 실제 수기 그래프·다른 해석 전문 심사 HOLD |

## 실제 확인한 수정 후보(P1)

`2022-hr-1` 현재 상세답안에는 V16.2 과거 주석에 **Human Relations**라고 잘못 쓴 부분이 그대로 남아 있으면서, 뒤의 V16.3 주석에서 **Human Factors**로 정정하고 있다. 출판사 메타데이터는 Human Factors가 맞다. 따라서 전문가 배포용 통합 원고에서는 *옛 오기 주석을 정리하고 단일 정확한 서지로 통일*하는 것이 좋다.

같은 문항의 '관리층 교육훈련 기법 여섯 가지'도 앞부분은 **액션러닝**, 후속 V16.5에서는 **경영 시뮬레이션**이 여섯째로 작성되어 있다. 모두 가능한 훈련기법이지만 시험장 암기기준 6개가 달라 혼란을 줄 수 있으므로 일관된 답안 구성으로 편집할 필요가 있다.

**이번에는 원고를 수정하지 않았다.** 후속 수정 시 본문 SHA가 달라지므로 V26 과목별 전문가 패킷 328개와 원장 연결을 갱신해야 한다.

## 실제 실행·검증

- 자동코드: `scripts/nomusa-v27-2022-primary-content-check.py`, 근거 파일: `review/NOMUSA_V27_2022_PRIMARY_CONTENT_CROSSCHECK_20261118.json`.
- [GitHub Actions #44172430945](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44172430945) **completed / success**, 2026-11-17 20:44:15~20:45:16 UTC (**약 61초**).
- [실행 아티팩트 #14368132830](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44172430945/artifacts/14368132830) — 2022년 19개 검토 상태 JSON, 원전 URL 포함 보고서 및 실제 비교 근거 JSON.
- 실제 파일 ZIP CRC 검증 PASS. 6개 답안·19개 ID·32개 소문항·328 원고 SHA 불변 검증 통과.
- 스킬: `.claude/skills/nomusa-v27-2022-real-source-claims/SKILL.md`. CI는 `.github/workflows/nomusa-v27-2022-content-check.yml`.
- `main`, Production, Preview, RC27/RC35, 문제 ID·저장키·원본 파일 및 328개 원고는 **직접 변경하지 않았음**. 검토 브랜치의 독립 근거/스킬/검증 워크플로만 추가. 자동 이메일 발송 없음.

## 다음 집중 내용검증

- 2022년 **나머지 13개 문항**에서 공식 법원 판결문/시험 당시 연혁법령/학술 저널·원전/경제학 원문 수식·그래프의 실제 검증.
- `2022-hr-1` P1 내부 서지표기·관리층 교육기법 일관성 교정 후 단일 확정본을 전문가에게 보여줄 수 있도록 SHA 갱신·패킷 재생성.
- V26 P1 77개에 대해 실제 수기 분량(50점 8~10장·25점 4장 목표)과 논증 밀도 독립 검토.
- 독립 전문가에게 검토 회신을 받기 전 최종승인 **0/328 HOLD** 유지.
