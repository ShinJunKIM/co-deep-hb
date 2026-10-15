# 2026 대한전자공학회 추계학술대회 학부생 논문경진대회 — 기획과 원고 초안

작성 2026-10-15. 제출 마감 2026-10-19(월). 두 파일 제출: (A) 프로시딩용(Double column, 1–5쪽, `논문양식.docx`), (B) 서면 심사용(4쪽, 논문지 양식 `서면 심사용 논문 양식.docx`, **저자·소속 삭제**). 1차 서면 블라인드 심사 → 2차 구두 발표. 표·그림·참고문헌은 영문.

## 0. 심사위원이 보는 것 (학회 공고·과거 사례에서 추린 것)

공고에는 배점이 없다. 블라인드 서면 심사 + 구두 발표 합산이므로 4쪽 안에서 (1) 문제가 왜 중요한지 한 문단, (2) 무엇이 새로운지 세 줄, (3) 방법의 신뢰성(검증 절차), (4) 정량 결과와 그림, (5) 한계를 숨기지 않는 태도가 읽혀야 한다. 학부생 경진대회 수상작은 대개 "작지만 끝까지 검증된 결과 + 좋은 그림 + 분명한 기여 문장"이다. 우리 강점은 **사전등록(결과를 보기 전에 기준 커밋)으로 검증한 공학 모델**이라는 점과, 반도체 패키징의 현안(200–400 nm 피치 하이브리드 본딩)을 다룬다는 점. 약점은 "검증 실패가 많다"는 인상 — 이를 "지배 기구가 바뀐다는 증거"로 재배치하는 것이 포장의 핵심이다.

## 1. 핵심 메시지 (한 문장) — 새로움이 앞에 오도록 고침

선행연구가 이미 말한 것: "sub-µm에서는 탄성 팽창이 작아 bulge-out이 접촉을 만든다"(imec DM2023/2026, IRPS 2026 리뷰), "방위에 따라 탄성 돌출이 달라지니 [111] 기준으로 recess 사양을 잡아라"(Ayoub 2022). 우리가 새로 더한 것은 그 두 주장을 **하나의 검증된 모델 안에서 정량화하고, Ayoub의 방위 결론을 뒤집은 것**이다.

**핵심 메시지.** "서로 다른 세 연구그룹의 실측으로 사전등록 검증한 열탄성–표면확산 결합 모델로 보면, 접촉 기구는 패드 폭 ≈ 0.7 µm(recess 합 5 nm 기준; recess 3→8 nm에서 0.55→1.0 µm)에서 열탄성에서 표면확산으로 넘어가고, 그 아래에서는 결정 방위의 효과가 탄성 항(폭 4 %)이 아니라 표면확산 항(<111> facet, 폭 10배)을 통해 들어온다. 따라서 300 nm에서 방위 위험은 Ayoub가 제안한 recess 사양으로는 막을 수 없고 어닐·미세구조로만 다룰 수 있으며, 그 조건을 공정창(250 °C × 2 h / 300 °C × 30 min)·CMP recess 허용 합(7.5–11.5 nm)·미접촉 쌍 하한(1.4 × 10⁻³)으로 제시한다."

세 가지 기여(서론 끝에 그대로):
1. **교차 검증된 결합 모델과 전환 규칙.** 문헌 물성만의 열탄성 FEM을 두 그룹의 돌출 실측(NYCU 1–9 µm, imec 0.54–3.06 µm)으로, 표면확산 항을 imec 2026 bulge-out 분포로, 각각 결과를 보기 전에 커밋한 기준으로 테스트했다(통과·실패 모두 보고). 그 모델이 주는 전환 규칙: 위·아래 탄성 돌출 합이 recess 합을 넘는 최소 폭은 recess 합 3/5/8 nm에서 실측 기준 0.55/0.70/1.0 µm(모델 0.57–1.06 µm @5 nm) — 선행연구의 "약 0.5 µm 피치"라는 정성 서술을 recess 조건부 수치로 바꿨다.
2. **방위 효과의 소재 재귀속.** 300 nm 접합 패드에서 탄성 항의 방위 폭은 4 %이지만, EBSD로 확인된 <111> facet을 진폭 인자 f(ω)로 넣은 확산 항은 방위 폭이 10배 이상이고 imec 분포의 폭(IQR 10/17)과 <111> 꼬리를 재조정 없이 재현한다. 즉 sub-µm에서 방위는 recess 사양(Ayoub)이 아니라 확산·미세구조 변수다.
3. **불확실도 있는 300 nm 설계값.** 방위·recess를 확률 변수로 둔 접촉 확률 공정창, CMP에 돌려주는 recess 허용 합 지도, 방위에 의한 미접촉 쌍 하한, 인자 순위(기구 ≫ 확산 동역학 ≈ 방위 ≈ 라이너 > 표면 > recess 산포·b). 탄성 모델의 0.54 µm 오차(+46 %)가 이 결론을 바꾸지 않음을 민감도 시험으로 보였다.

## 2. 논문 구성 (프로시딩 ≤ 5쪽 / 서면 심사용 4쪽)

| 절 | 내용 | 그림·표 |
|---|---|---|
| 요약 | 한국어 요약 150–200자 + 영문 제목 | — |
| I. 서론 | 피치 스케일링(200 nm, imec 2026) → 탄성 팽창 sub-nm → 접촉 기구 문제. 선행연구 역할 분담(Ayoub 변형률, Lin/Chen 돌출, imec bulge-out, Van Huylenbroeck recess·수율)과 빈 자리(세 요소를 한 공정창으로 묶어 검증한 연구 없음). 기여 3개. | Fig. 1 모델 구조·V&V 흐름 |
| II. 모델과 검증 절차 | 2.1 용어(recess/u/ε′zz/h_d)와 접촉 조건 m = u_t+u_b+h_t+h_b−(r_t+r_b). 2.2 열탄성 FEM(ANSYS, 이방성 Cu, 접합 측벽, 배열 셀, 공정별 유전체 1회 학습). 2.3 표면확산 항 h_d = s_ox·0.0022(θ_eff−90°)·D·f(ω)·[1−e^(−t/τ)], τ ∝ D^3.7/Ds(T), f(ω) facet 모델. 2.4 ASME V&V 10 순서와 사전등록(train/test 분할, 통과 기준, 커밋 해시) | Table 1 데이터와 역할 |
| III. 결과 | 3.1 탄성 모델 train/test(Table 2) + 측벽 판별 + 0.54 µm 실패 → 기구 전환(Fig. 2). 3.2 확산 항 test(Fig. 3): 고정형 2/17 → 개정 11/17, ≥250 °C 10/10, 방위 항으로 IQR 10/17. 3.3 Ayoub 변형률(3 µm 부호 일치, 300 nm 크기 일치·부호 반대 → 계면 가설 한 문장). 3.4 300 nm 공정창(Fig. 4), recess 허용 사양(Fig. 5), 인자 순위·방위 하한(Fig. 6), 연결 단계 접촉면적·압력 한 문단 | Fig. 2–6, Table 2–3 |
| IV. 한계와 결론 | 검증된 것/안 된 것/탐색 표(Table 3), 한계 6개, 결론 3줄 | Table 3 |
| 참고문헌 | 영문 15편 | — |

서면 심사용 4쪽: 위에서 Fig. 1·5·6을 빼고(Fig. 2, 3, 4와 Table 2, 3만), 서론을 절반으로, 2.2–2.3을 식 두 개와 표 하나로 압축.

## 3. 그림 목록 (Claude Science로 구현; 지금은 placeholder)

| 번호 | 내용 | 원본 데이터/그림 | 구현 메모 |
|---|---|---|---|
| Fig. 1 | (a) 패드 쌍 단면: recess r, 탄성 u, bulge-out h_d, 접촉 조건; (b) V&V 흐름: 수치 검증 → 학습(큰 패드) → 테스트(held-out) → 예측(MC) — 사전등록 커밋 표시 | 새로 그림 | 두 패널, 영문 라벨 |
| Fig. 2 | 패드 크기별 위+아래 돌출: 탄성(모델 b=1, ×0.69, imec 실측) vs 확산(≥350 °C 포화, 실측 점검 범위 ≤300 nm 실선·외삽 점선) vs recess 합 5 nm; 교차 ≈ 0.7 µm | `s2_mechanism_transition.png`, `paper_results.json` | 확산 외삽선은 0.54 µm까지만; 교차점 화살표 |
| Fig. 3 | 확산 항 vs DM2026: (a) 400/500 nm 피치 중앙값·IQR vs T/시간, (b) 크기 의존(200–500 nm 피치, 250 °C), (c) f(ω) 곡선과 facet 분율 | `s2_diffusion_fit.png`, `orient_diffusion_round2.csv` | 실패 점(200 °C 큰 패드)을 빈 기호로 |
| Fig. 4 | 300 nm 공정창: P_contact(T × t), 청정/산화 패널, 빗금 = b×τ₀×Q 불확실 | `s2_window_0.30um.png`, `window_summary.json` | 권고 셀 테두리 |
| Fig. 5 | 300 nm CMP recess 허용 합(nm) 지도(T × t) | `s2_recess_spec_0.30um.png`, `paper_results.json` | 숫자 표기 |
| Fig. 6 | (a) 인자 순위 막대(0.54/0.30 µm), (b) 방위 미접촉 쌍 하한(facet 항 유/무, 로그축) | `s2_factor_ranking.png`, `s2_orientation_floor.png` | 두 패널 |
| Table 1 | 데이터셋: 그룹/공정/측정량/크기/역할(train·test·비교) | 보고서 §2 | |
| Table 2 | 탄성 모델 train/test 결과: 크기, T, 모델, 측정, 허용, 통과 | `validation_rev1.csv`, adopted_rev.json | |
| Table 3 | 모델 부분별 상태: 검증 통과 / 실패 / 탐색, 근거 커밋 | 보고서 §14 | |

## 4. 원고 초안 — 프로시딩용 (한국어 본문, 영문 그림·표·참고문헌)

**제목(국문):** 서브마이크론 Cu 하이브리드 본딩 패드의 접촉 기구 전환과 300 nm 공정창 예측: 사전등록 검증 기반 열탄성–표면확산 모델
**Title:** Mechanism Transition and 300 nm Process-Window Prediction for Sub-Micron Cu Hybrid-Bonding Pads: A Pre-Registered Thermo-Elastic/Surface-Diffusion Model

**요약.** Cu/유전체 하이브리드 본딩의 패드 피치가 1 µm 아래로 줄면 어닐 중 Cu 열탄성 팽창이 패드당 1 nm 수준으로 작아져 CMP recess(패드당 2–3 nm)를 닫지 못한다. 본 논문은 문헌 물성만으로 구성한 ANSYS 열탄성 FEM과 표면확산 bulge-out 해석식을 결합한 모델을 ASME V&V 10-2019 순서(수치 검증–학습–테스트–예측)로 평가하되, 모든 테스트 기준을 결과를 보기 전에 공개 저장소에 커밋(사전등록)하였다. 열탄성 모델은 서로 다른 두 연구그룹의 1–3 µm 패드 돌출 실측을 nm 단위로 재현하고 측벽 계면이 접합 상태임을 판별했으나, 0.54 µm에서는 전 온도에서 +46 % 과대예측하여 연속체 탄성이 지배 기구에서 벗어남을 보였다(전환 크기 ≈ 0.7 µm). 결정 방위 의존 진폭을 갖는 표면확산 항은 imec의 115–300 nm 패드 bulge-out 분포를 250 °C 이상에서 재조정 없이 재현했고(중앙값 10/10, 분포 폭은 방위 항이 있어야 재현), 200 °C 큰 패드에서는 과소예측하여 보수적이다. 이 모델로 300 nm 패드의 접촉 확률 공정창(청정 표면 250 °C·2 h 또는 300 °C·30 min), CMP recess 허용 합(7.5–11.5 nm), <111> 방위에 의한 미접촉 쌍 하한(≈1.4 × 10⁻³)과 인자 순위를 불확실도와 함께 제시한다.

### I. 서론

웨이퍼 간(W2W) Cu/SiCN 하이브리드 본딩은 200 nm 피치까지 전기적 수율이 보고되었다[1]. 이 영역에서는 접합 후 어닐 중 Cu 패드의 열탄성 팽창이 패드 부피에 비례해 줄어 1 nm 이하가 되며, 상·하 패드의 Cu–Cu 접촉은 표면확산에 의한 Cu 원자의 재배치("bulge-out")가 만든다[2,3]. 따라서 1 µm 아래에서는 "어떤 recess에서 닫히는가"가 아니라 "어떤 어닐·표면·라이너·방위 조건에서 닫히는가"가 공정 설계 질문이 된다.

본 논문은 어닐 중 Cu 패드가 위로 솟는 양을 두 기구의 합으로 본다. (i) 열탄성 팽창 u: Cu와 유전체·Si의 열팽창 차이로 생기며 패드 부피에 비례하고, 식으면 되돌아간다. (ii) 표면확산 bulge-out h_d: 표면에너지·응력 구배를 줄이려고 Cu 원자가 패드 가장자리에서 중앙으로 이동해 생기며 어닐 온도·시간·표면 상태·결정 방위에 의존하고, 되돌아가지 않는다. 접촉 조건은 두 기구의 위·아래 합이 recess 합을 넘는 것이다. 두 기구는 패드 크기에 다르게 반응하므로, 어느 쪽이 접촉을 결정하는지가 크기에 따라 바뀐다 — 이 전환을 정량화하는 것이 본 연구의 출발점이다.

선행연구는 역할이 나뉘어 있다. Ayoub 등[4]은 300 nm 패드의 Laue 미세회절 편차 변형률과 COMSOL 해석으로 결정 방위에 따른 탄성 차이를 보였고, Lin·Chen 등[5,6]은 in-situ AFM으로 1–9 µm 패드의 돌출을 직접 쟀으며, imec[2,3,7]은 접합 후 상부 웨이퍼를 제거하고 수천 개 패드의 bulge-out 분포를 AFM·EBSD로 측정했다. 그러나 열탄성·표면확산·연결 단계를 하나의 공정창으로 묶고, 그 모델의 각 부분을 독립 실측으로 검증한 연구는 없다. 또한 기존 FEM은 벌크 물성으로 sub-µm 실측을 재현하지 못한다는 보고가 있다[8].

본 연구는 (1) 문헌 물성만으로 구성한 ANSYS 열탄성 FEM을 두 연구그룹의 돌출 실측으로 학습(train)·테스트(test)하고, (2) 표면확산 항에 결정 방위 의존 진폭을 도입하여 imec 2026 bulge-out 분포로 테스트하며, (3) 그 결과로 300 nm 패드의 공정창을 접촉 확률로 예측한다. 모든 테스트 기준(파라미터, 데이터 분할, 통과 규칙)은 결과를 보기 전에 공개 저장소에 커밋하였고, 테스트 데이터로의 재조정은 하지 않았다. 기여는 다음 세 가지다. ① 세 연구그룹의 실측으로 교차 검증한 결합 모델에서, 접촉 기구가 열탄성에서 표면확산으로 넘어가는 폭을 recess 조건부 규칙으로 정량화했다(recess 합 3/5/8 nm에서 0.55/0.70/1.0 µm). ② sub-µm에서 결정 방위의 효과는 탄성 항(폭 4 %)이 아니라 표면확산 항(<111> facet, 폭 10배)을 통해 들어오며, 이 항이 imec bulge-out 분포의 폭과 꼬리를 재조정 없이 재현함을 보였다 — 방위 위험은 Ayoub가 제안한 recess 사양이 아니라 어닐·미세구조로 다뤄야 한다. ③ 300 nm 공정창, CMP recess 허용 사양, 방위에 의한 미접촉 하한과 인자 순위를 불확실도와 함께 제시하고, 탄성 모델의 0.54 µm 오차가 이 결론을 바꾸지 않음을 보였다.

### II. 모델과 검증 절차

**2.1 용어와 접촉 조건.** recess r는 CMP 후 Cu 윗면이 유전체 면보다 낮은 깊이(공정 입력), u는 어닐 중 열탄성 돌출(모델 출력), h_d는 표면확산 bulge-out 높이(패드 자기 표면 기준), ε′zz는 Laue가 재는 편차 탄성 변형률이다. 상·하 패드가 닿는 조건은 접촉 여유 m = u_t + u_b + h_d,t + h_d,b − (r_t + r_b) ≥ 0 이며, 방위와 recess를 확률 변수로 두고 P(m ≥ 0)을 Monte Carlo로 계산한다(Fig. 1).

**2.2 열탄성 FEM.** ANSYS MAPDL(µMKS). 원형 Cu 패드, 측벽 테이퍼, Ta 라이너 링·바닥, 유전체, Si 기판등가층. 작은 패드(≤0.54 µm)는 3D SOLID185(O-grid)에 Cu 탄성상수 C11/C12/C44 = 168.4/121.4/75.4 GPa를 결정 방위로 회전한 이방성, 큰 다결정 패드는 2D 축대칭 Hill 등방(128 GPa, 0.345). α_Cu = 16.5 ppm/K. 측벽은 접합(절점 공유)을 기본으로 하고 미끄럼(법선만 구속)을 대조군으로 둔다. 셀은 배열 피치(2D 등면적 2.26 w) 또는 고립 12 w. "같은 모델"의 뜻: 물리 규칙·Cu 물성·경계조건·메시 규칙은 모든 시료에 같고, 형상·라이너·유전체 종류·피치·열이력만 시료별 입력이다. 유전체 E·α는 공정당 한 번, 큰 패드에서만 문헌 범위 안에서 학습한다(NYCU SiO2 59 GPa·1.0 ppm/K·테이퍼 18°, imec SiCN 120 GPa·2.0 ppm/K). 돌출 u는 중앙 50 % 면적 평균 − 주변 유전체 평균(AFM 정의와 동일). 수치 검증: 단위(해석해와 자릿수 일치), 이방성 12방위 1 % 안, 메시 ×2 0.02 %, 셀 수렴, 3D–2D 0.1–0.7 %.

**2.3 표면확산 항.** DM2024[7]의 선형화를 따라 패드당
h_d = s_ox · 0.0022·(θ_eff − 90°)·D · f(ω) · [1 − exp(−t/τ)], τ = τ₀ (D/200 nm)^3.7 · D_s(350 °C)/D_s(T) ... (1)
D는 패드 지름, t 어닐 시간, D_s는 Cu 표면확산계수(Q = 20.7 kcal/mol[9]), τ₀ = 60 s, s_ox는 표면 산화 배율(청정 1, 산화 0.45[2]). 방위 의존 진폭 f(ω) = clip((ω − ω_c)/Δω, 0, 1)은 패드 법선과 가장 가까운 <111> 사이 각 ω로 정의한다: fcc Cu에서 {111}이 최저 표면에너지라 <111> 패드는 평평한 면을 유지해 곡률 구동력을 잃는다[3]. Cu 표면확산계수의 방위 이방성은 (111)이 (100)보다 1.5–3배 빠른 쪽이므로[9] 꼬리는 동역학이 아니라 진폭으로 넣는다.

**2.4 검증 절차와 사전등록.** ASME V&V 10-2019 순서를 따랐다. 학습 데이터는 큰 패드(NYCU 9·3 µm[5], imec 1.80·3.06 µm[2]), 테스트는 imec 1.26·0.54 µm, NYCU 1 µm[5,6], 미끄럼 대조군(V4)이다. 확산 항은 imec 2026[3]의 400 nm 피치·350 °C 한 점에서 진폭만 학습하고 나머지 17점(피치 200–500 nm, 200–450 °C, 1–4 h)으로 테스트했다(점별 허용 max(1.5 nm, 25 %, 판독 오차), ≥80 % 통과 + 온도 경향 + 350 °C 이상 포화). 방위 항은 EBSD가 있는 500 nm 피치에서 학습하고 나머지로 테스트했다(데이터를 이미 본 뒤의 2차 탐색으로 표기). 각 규칙은 결과 계산 전에 git 커밋으로 고정했고(Table 1), 테스트 실패 시 문서화된 개정 1회만 허용했다.

### III. 결과

**3.1 열탄성 모델: 학습·테스트와 기구 전환.** Table 2에 결과를 요약했다. 학습값은 모두 문헌 범위의 끝(bound-limited)이었다. 테스트에서 NYCU 1 µm(모델 1.79–1.94 vs 실측 2.1 ± 0.4 nm)와 imec 1.26 µm 100–200 °C, 1.80 µm 전 온도는 통과했고, 미끄럼 측벽 대조군은 1 µm에서 1.7배, 0.54 µm에서 3.5배 과대예측하여 측벽이 접합 상태임이 판별되었다. 그러나 imec 0.54 µm는 100–400 °C 전 구간에서 측정/모델 비 0.61–0.69로 과대예측했다(비열적 오차; 단일 기하 가설 ≤7 %, 측정 정의 가설로도 모든 크기 동시 설명 불가). 사전 고정한 기준에 따라 탄성 모델은 0.54 µm에서 NOT VALIDATED로 동결했다. 이 결과를 recess와 함께 놓으면 기구 전환이 드러난다(Fig. 2). 절차는 다음과 같다: recess 합을 IRPS 2026 실측 평균 5 nm[10]로 고정하고, 크기별 열탄성 돌출 u를 공정 상한 400 °C에서 취해(실측: imec in-situ 0.54/1.26/1.80/3.06 µm; 모델: 같은 크기의 FEM), 위·아래 합 2u가 5 nm를 넘는 최소 크기를 log(크기) 보간으로 구한다. 실측 기준 ≈0.7 µm(0.54 µm에서 2.8 nm, 1.26 µm에서 10 nm 사이), 모델 기준 0.66 µm(b = 1)–1.06 µm(b = 0.69)이다. 그 아래에서는 공정 상한 온도에서도 탄성만으로는 접촉이 안 되며(300 nm, 400 °C: 패드당 ≈1 nm, 틈의 1/5), 실제로 200–400 nm 피치 본딩이 성립하는 것[1]은 다른 기구(표면확산)가 틈을 메운다는 뜻이다. 전환 크기는 recess 합과 어닐 온도의 함수이며(recess가 작거나 온도가 높으면 작아짐), 여기서는 그 기준 조건에서의 값이다.

**3.2 표면확산 항 테스트.** 고정형(θ = 123°, τ₀ 학습)은 17점 중 2점만 통과했다: 학습점(350 °C 1 h)이 동역학적으로 포화 상태라 진폭 오차가 τ₀로 잘못 흡수된 탓이다. 문서화된 개정 1(진폭 θ_eff 학습, τ₀ 60 s 고정)에서 θ_eff = 113.6°, 11/17 통과, 온도 경향 통과, 포화 비 경계 실패로 규칙상 NOT VALIDATED이나, 실패 6점은 모두 200 °C·D ≥ 250 nm 또는 자가 어닐 Cu의 **과소예측**이고 250 °C 이상 PPA-Cu 전 점과 ≤140 nm 패드 200 °C는 10/10 통과했다(Fig. 3). 즉 식 (1)은 250 °C 이상에서 실측과 맞고 200 °C에서는 보수적이다(측정의 2 h→4 h 증가율로 추정한 유효 활성화에너지 14–17 kcal/mol은 문헌 20.7보다 작다). 방위 항을 넣은 2차 탐색(θ_eff 119°, ω_c 5°, Δω 19.5°)은 중앙값 통과율을 바꾸지 않지만 분포 폭(IQR)을 10/17 재현했다 — 방위가 없는 모델의 IQR은 0이다.

**3.3 Ayoub 300 nm 변형률.** 같은 적층(SiN 캡, Ta 13 nm)의 접합 모델은 3 µm 패드에서 ε′zz 부호가 실측[4]과 일치했고(−1.24 × 10⁻³ vs −0.35…−2 × 10⁻³), 300 nm에서는 두 방위(E_z 68·190 GPa)의 가열 기울기 크기가 0.5 % 안에 들되 부호가 반대였다. Ayoub 시료는 다른 공정(Cu/SiO2, CMP 후 PECVD SiN 캡)이고 Cu 계면 조건이 명시돼 있지 않으므로 계면 상태 차이(캡·측벽)로 해석하되 가설로 둔다. 크기 재현은 주장하지 않는다.

**3.4 300 nm 공정창과 레시피 변수.** 탄성 항(b = 0.69, 0.54 µm 테스트 비의 범위 0.60–1.0로 반복)과 식 (1)(방위 항 포함)의 단순합으로, 상·하 방위(구면 균일)와 recess(패드당 N(2.5, 0.5²) nm[10]) 2 × 10⁵ 쌍에 대해 P_contact를 계산했다(Fig. 4). 청정 표면(표준 접합 전 세정)에서 창은 250 °C × 2 h 또는 300 °C × 30 min부터 열리고, 350 °C 이상은 5 min이면 충분하다. 불확실 집합 b × τ₀{20, 60, 100 s} × Q{20.7, 15}에서 바뀌는 셀은 경계 3개뿐이며, 권고 레시피는 b 전 범위에서 같다(탄성 항은 총 돌출의 ~8 %). 표면 산화(s_ox 0.45)는 창을 한 단계(50 °C 또는 한 시간 등급) 좁힌다. 같은 계산을 recess 평균에 대해 풀면 CMP에 돌려줄 허용 사양이 나온다(Fig. 5): 250 °C × 2 h에서 recess 합 ≤ 7.5 nm, 300 °C × 30 min에서 ≤ 9 nm, 350 °C 이상에서 ≤ 11.5 nm(산화 표면은 절반). 인자 순위(창에서 바뀌는 셀 수, Fig. 6a)는 지배 기구(확산 off: 9/15) ≫ 확산 동역학 τ₀(2) ≈ <111> facet(2) ≈ 라이너 접촉각(2) > 표면 상태(3, 산화 쪽) > recess 평균·산포(0)·b(0) 순이다. 방위는 탄성 항(폭 4 %)이 아니라 확산 항을 통해 들어오며, 총 돌출의 방위 폭은 0.30 µm에서 11 nm(탄성 0.03 nm)이다. <111> 근방 패드(f < 0.5, 전체의 13 %)는 bulge-out이 작아 최적 어닐에서도 미접촉 쌍이 ≈1.4 × 10⁻³ 남는다(Fig. 6b); 미세결정 Cu로 꼬리를 없애면 이 하한이 사라진다[3]. 접촉 후 연결 단계(2D 축대칭 Cu–Cu 마찰 접촉, 등방 소성)에서는 300 nm·350 °C·recess 1–2 nm에서 접촉면적 분율 0.95–1.0, 평균 접촉압력 317–403 MPa로 재결정의 필요조건을 만족하나 접합의 증명은 아니다.

### IV. 한계와 결론

Table 3에 모델 부분별 상태를 정리했다. 한계: (1) 0.54 µm 탄성 오차 +46 %의 원인은 원 데이터(Okudur 2017[11]) 부재로 미상이며, 결정 민감도 시험에서 산화 표면 경계 2셀만 영향을 받았다. (2) 300 nm 돌출 실측은 없어 300 nm는 예측이다(확산 항은 같은 크기에서 ≥250 °C 실측 점검). (3) 200 °C 확산 동역학과 미세구조(도금 후 어닐 유무) 변수가 모델에 없다. (4) 연결 단계 접촉 FEM은 Lhostis[12]의 패드 두께 효과를 재현하지 못한다. (5) 오버레이는 범위 밖이다[1]. (6) 크리프·장시간 계면 완화는 미결이다.
결론: 1 µm 아래에서 Cu 하이브리드 본딩의 접촉은 열탄성 팽창이 아니라 표면확산이 결정하며(전환 ≈0.7 µm), 레시피 변수는 어닐 온도·시간·표면 상태·라이너·결정 방위로 옮겨간다. 사전등록 V&V로 평가한 모델은 300 nm 패드에 대해 청정 표면 250 °C × 2 h 또는 300 °C × 30 min의 창, recess 허용 합 7.5–11.5 nm, 방위에 의한 미접촉 하한 10⁻³을 제시한다. 주장 수위는 "검증된 레시피"가 아니라 "검증 통과 범위의 탄성 모델 + 실측으로 점검한 확산 모델로 본 공정창 예측(불확실도 포함)"이다.

### References (영문)
[1] S. Van Huylenbroeck et al., "Wafer-to-Wafer Hybrid Bonding Technology with 200nm Interconnect Pitch," in *Proc. IEEE ECTC*, 2026.
[2] J. De Messemaeker et al., "New Cu 'bulge-out' mechanism supporting sub-micron scaling of hybrid wafer-to-wafer bonding," in *Proc. IEEE ECTC*, pp. 1042–1049, 2023.
[3] J. De Messemaeker et al., "Understanding scaling and temperature limits in Cu bulge-out mechanism for hybrid wafer-to-wafer bonding," in *Proc. IEEE ECTC*, pp. 2158–2162, 2026, doi:10.1109/ECTC51846.2026.00355.
[4] B. Ayoub et al., "In-situ characterization of thermomechanical behavior of copper nano-interconnect for 3D integration," *Microelectron. Eng.*, vol. 261, 111809, 2022.
[5] H.-E. Lin et al., "Revealing challenges of downscaling effects on Cu thermal expansion in advanced hybrid bonding using in-situ AFM," *Appl. Surf. Sci.*, vol. 689, 162539, 2025.
[6] P.-L. Chen et al., in *Proc. IEEE ECTC*, 2025, doi:10.1109/ECTC51687.2025.00329.
[7] J. De Messemaeker et al., "Simulation of bulge-out mechanism enabling sub-0.5 µm scaling of hybrid wafer-to-wafer bonding," in *Proc. IEEE ECTC*, 2024.
[8] Y. W. Tsau et al., *Microelectron. Reliab.*, 2022.
[9] D. B. Butrymowicz, J. R. Manning, and M. E. Read, "Diffusion in copper and copper alloys, Part I," *J. Phys. Chem. Ref. Data*, vol. 2, pp. 643–655, 1973.
[10] S. Van Huylenbroeck et al., in *Proc. IEEE IRPS*, 2026, doi:10.1109/IRPS61424.2026.11499286.
[11] O. O. Okudur et al., "Thermomechanical aspects of wafer-to-wafer copper-dielectric hybrid bonding for 3D integrated circuits," *Int. Conf. Wafer Bonding*, Leuven, 2017.
[12] S. Lhostis et al., "Contact resistivity of submicron hybrid bonding pads down to 400 nm," *J. Electron. Mater.*, vol. 53, pp. 4421–4431, 2024.
[13] ASME V&V 10-2019, *Standard for Verification and Validation in Computational Solid Mechanics*, ASME, 2019.
[14] B. Ayoub, PhD thesis, Univ. Bordeaux, 2023, HAL tel-04437757.
[15] C. Okoro et al. (Cu σ_y(T) used for the isotropic plasticity of the connection stage) — 보고서 문헌 목록 참조.

## 5. 표 초안

**Table 1 Datasets and their roles (pre-registered split).**
| Group / process | Measurement | Sizes | Role |
|---|---|---|---|
| NYCU (Lin 2025, Chen 2025), Cu/SiO2 | in-situ AFM protrusion u(T) | 9, 3, 1 µm | train (9, 3), test (1) |
| imec (DM2023 Fig. 1, Okudur 2017), Cu/SiCN | in-situ SPM u(T), 100–400 °C | 3.06, 1.80, 1.26, 0.54 µm | train (3.06, 1.80), test (1.26, 0.54) |
| imec DM2026, Cu/SiCN | post-bond AFM bulge-out distributions, EBSD | pads 115–300 nm, 200–450 °C, 1–4 h | diffusion term: train (400 nm pitch, 350 °C), test (17 points) |
| ST/Leti (Ayoub 2022, thesis), Cu/SiO2 | Laue deviatoric strain ε′zz(T) | 0.3, 3 µm | comparison (sign) |
| imec IRPS 2026 | recess distribution | — | input N(2.5, 0.5²) nm |

**Table 2 Elastic-model train/test (array cell, bonded sidewall; u at 400 °C unless noted).**
| Case | Model (nm) | Measured (nm) | Rule | Result |
|---|---|---|---|---|
| NYCU 9 / 3 µm, 200 °C (train) | 6.87 / 4.26 | 6.4 / 4.1 ± 0.4 | 2σ | pass |
| imec 1.80 µm, 100–400 °C (train) | 1.0–5.0 | 1.05–5.4 ± 0.2–0.5 | 2σ | pass |
| imec 3.06 µm 300–400 °C (train) | 4.64 / 6.32 | 6.05 / 7.85 | 2σ | fail (super-linear, inelastic) |
| NYCU 1 µm, 200 °C (test) | 1.79–1.94 | 2.1 ± 0.4 | overlap | **pass** |
| imec 1.26 µm, 100/200/300/400 °C (test) | 0.81/1.88/2.96/4.04 | 0.7/1.6/3.65/5.0 | 0.5 nm or 15 % | pass/pass/fail/fail |
| imec 0.54 µm, 100/200/300/400 °C (test) | 0.41/0.95/1.50/2.04 | 0.25/0.60/1.0/1.4 | 0.4 nm | ratio 0.61–0.69 at all T → **fail (athermal)** |
| sliding control, 1 µm / 0.54 µm (test V4) | 3.66 / 4.84 | 2.1 / 1.4 | must fail | fails → sidewall bonded |

**Table 3 Status of each model part.**
| Part | Status | Evidence (commit) |
|---|---|---|
| Elastic u, ≥ 1 µm, bonded sidewall | validated (pre-registered) | 33a8f5c → B/Br runs |
| Elastic u, 0.54 µm | not validated (+46 %, athermal); decision sensitivity OPEN (2 boundary cells, oxidised) | 2acfd92 / 5c1e819 |
| Diffusion h_d, fixed form | not validated (2/17) | 9c6bc29 / 5fa0e05 |
| Diffusion h_d, revision 1 (θ_eff) | not validated by rule (11/17); 10/10 at ≥ 250 °C, PPA-Cu | eb347c1 / 5221d33 |
| Orientation amplitude f(ω) | exploratory round 2: IQR 10/17 reproduced | 6696562 / d722e67 |
| Ayoub ε′zz | 3 µm sign agrees; 300 nm sign disagrees (interface hypothesis) | 63869bb / f7818ad |
| Connection stage contact FEM | Lhostis thickness test failed twice; ratio test undetermined | 6696562 / dced86f / 46924cc |
| 300 nm window | prediction with uncertainty | 80389d5 / 9dbd0c0 |

## 6. 서면 심사용(4쪽) 압축 지침
- 요약 150자, 서론 2문단(문제 + 기여 3개), II는 식 (1)과 접촉 조건, V&V 분할 한 문단, Table 1 생략, III는 3.1(Fig. 2) · 3.2(Fig. 3) · 3.4(Fig. 4, Table 2 축약), IV 한계 4개 + 결론. Table 3는 6행으로.
- 저자·소속·이메일·저장소 URL·"우리 연구실" 등 식별 문구 금지. 커밋 해시는 "공개 저장소에 사전등록(해시는 채택 후 공개)"으로.
