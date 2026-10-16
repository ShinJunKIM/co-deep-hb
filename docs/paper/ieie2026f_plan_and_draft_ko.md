# 2026 대한전자공학회 추계학술대회 학부생 논문경진대회 — 기획과 원고 초안

작성 2026-10-15. 제출 마감 2026-10-19(월). 두 파일 제출: (A) 프로시딩용(Double column, 1–5쪽, `논문양식.docx`), (B) 서면 심사용(4쪽, 논문지 양식 `서면 심사용 논문 양식.docx`, **저자·소속 삭제**). 1차 서면 블라인드 심사 → 2차 구두 발표. 표·그림·참고문헌은 영문.

## 0. 심사위원이 보는 것 (학회 공고·과거 사례에서 추린 것)

공고에는 배점이 없다. 블라인드 서면 심사 + 구두 발표 합산이므로 4쪽 안에서 (1) 문제가 왜 중요한지 한 문단, (2) 무엇이 새로운지 세 줄, (3) 방법의 신뢰성(검증 절차), (4) 정량 결과와 그림, (5) 한계를 숨기지 않는 태도가 읽혀야 한다. 학부생 경진대회 수상작은 대개 "작지만 끝까지 검증된 결과 + 좋은 그림 + 분명한 기여 문장"이다. 우리 강점은 **사전등록(결과를 보기 전에 기준 커밋)으로 검증한 공학 모델**이라는 점과, 반도체 패키징의 현안(200–400 nm 피치 하이브리드 본딩)을 다룬다는 점. 약점은 "검증 실패가 많다"는 인상 — 이를 "지배 기구가 바뀐다는 증거"로 재배치하는 것이 포장의 핵심이다.

## 1. 핵심 메시지 — v4 (2026-10-16, 정합성 라운드 후; 10/19 제출본 기준)

**연구 질문.** 1 µm 아래에서 Cu–Cu 접촉은 무엇이 결정하는가? 공정 변수(어닐 온도·시간, 표면 상태, 라이너, 계면 상태)와 패드마다 통제할 수 없는 무작위 요인(recess 산포, 결정방위 등)은 공정창을 각각 얼마나 움직이며, 그 판정은 모델 불확실성 아래에서 어디까지 안정한가?

**핵심 메시지.** "문헌 물성 열탄성 FEM과 실측으로 점검한 표면확산 항을 사전등록 V&V로 시험하면, 300 nm 패드의 어닐 조건은 (A) 탄성만으로 접촉, (B) 확산이 있어야 접촉하며 모든 모델 불확실성에서 유지, (C) 모델·꼬리 가정에 따라 판정이 갈림의 세 영역으로 나뉜다. 접합 계면에서 (A)는 비어 있고(탄성 접촉 한계 ≈ 0.7 µm), 청정 표면 250 °C·2 h, 300 °C ≥ 30 min, ≥ 350 °C는 (B)다. 다만 이것은 균일 방위 확률 기준이며, 방위 분포 가정을 빼고 최악 방위로 보면 결론은 측정되지 않은 한 값 — 정확히 <111>인 패드의 bulge-out f(0) — 에 달려 있다."

**두 경계를 구분한다.**
- 탄성 접촉 한계: u_t + u_b = r_t + r_b. 400 °C·recess 합 5 nm에서 imec 실측 기준 ≈ 0.70 µm(3/8 nm → 0.55/1.0 µm). 지금까지 "기구 전환"이라 부른 0.7 µm는 이것이다.
- 기여도 역전: h_t + h_b = u_t + u_b. 확산 진폭(∝ D)과 동역학(τ ∝ D^3.7)이 경쟁해 어닐 조건에 따라 0.74 µm(250 °C 2 h)–2.45 µm(400 °C 2 h)로 예측되지만, 확산 데이터는 D ≤ 300 nm뿐이므로 **외삽 예측**이다. 300 nm에서는 어느 확산 형태로도 확산 돌출이 탄성의 약 20배다(350 °C 1 h: 쌍 31–33 vs 1.6 nm).

**기여 세 가지(서론 끝).**
1. **탄성 접촉 한계의 정량 규칙과 대리식.** 두 그룹(NYCU·imec) 돌출 실측으로 학습·테스트한 열탄성 FEM에서, 탄성 접촉 한계를 recess 조건부 규칙으로 제시했다(400 °C, 3/5/8 nm → 0.55/0.70/1.0 µm). 등방(Hill) 탄성 돌출은 구속 계수 대리식 C(h/w)가 imec·NYCU 적층의 미사용 기하 4개에서 ±20 % 안에 들었다(사전등록). 0.54 µm 실측(측정/모델 0.61–0.69, 전 온도)은 이 곡선 밖의 고립점이며, 라이너 두께 가설까지 시험해 탄성 기하 인자로는 설명되지 않음을 보였다.
2. **계면 조건을 하나의 설정으로 평가.** ST/Leti 공정의 네 정성 관측(Ayoub 3 µm·300 nm 변형률 부호, Lhostis 폭·두께 효과)을 같은 설정으로 평가하면 "측벽 미끄럼 + 캡 하중 비전달"만 넷을 모두 만족하고 접합은 둘을 실패한다. imec·NYCU 돌출은 같은 미끄럼 설정에서 1.7–3.5배 과대예측해 접합을 요구한다. 따라서 Cu–라이너 측벽 계면 상태는 공정별 입력이며, ST/Leti의 이완은 정성 관측 넷과 일관한 **후보 가설**이다(패드 10 기울기 40 % 과소 등 정량 불일치는 남음).
3. **패드별 무작위 요인을 포함한 공정창: 확률 기준과 최악 조건 기준.** 패드마다 다른 recess와 결정방위를 확률 변수로 두고, DM2026 분포의 판독 가능한 범위(누적 ≥ 0.5 %)와 일관된 방위 함수 f(ω) 6종 × 탄성 계수 b × 확산 동역학 τ₀·Q의 모든 조합에서 유지되는 경계는 청정 표면 기준 2시간 248 °C, 30분 285 °C, 5분 342 °C 이상이다. 요인별 경계 온도 이동으로 보면 공정창을 가장 크게 움직이는 것은 지배 기구(확산 유무)와 확산 동역학·라이너·표면(20–40 °C)·계면 상태(14–19 °C)이고, recess 평균과 방위 꼬리는 약 10 °C, recess 산포는 약 4 °C이며, recess 산포와 방위는 주로 **수율의 하위 꼬리**(천 쌍 중 몇 쌍이 끝까지 안 닿는가)를 정한다. 방위 분포 가정을 뺀 최악 조건 기준에서는 정확히 <111>인 패드의 bulge-out f(0)이 결론을 정한다(0 → 어떤 어닐로도 최악 쌍 불충분, 허용 recess 0.5–0.9 nm/패드; f(0) > 0 → 2시간 265–290 °C 또는 30분 304–324 °C 이상, 2.4–4.2 nm/패드). 확률 기준 허용 recess는 3.5–9 nm/패드다.

**주장하지 않는 것.** 기구 역전의 실측 검증, Ayoub 300 nm 변형률 크기 재현, 확산 항 검증 통과(사전등록 시험 3회 모두 NOT VALIDATED, 적용 범위 = 등크기 패드·≥ 250 °C), 관측 범위 아래 꼬리·f(0), "검증된 레시피".

## 2. 논문 구성 (프로시딩 ≤ 5쪽 / 서면 심사용 4쪽)

| 절 | 내용 | 그림·표 |
|---|---|---|
| 요약 | 한국어 요약 150–200자 + 영문 제목 | — |
| I. 서론(필요성·목적) | 피치 스케일링(200 nm, imec 2026) → 탄성 팽창 sub-nm → 접촉 기구 문제. 선행연구 역할 분담(Ayoub 변형률, Lin/Chen 돌출, imec bulge-out, Van Huylenbroeck recess·수율)과 빈 자리(세 요소를 한 공정창으로 묶어 검증한 연구 없음). 기여 3개. | Fig. 1 모델 구조·V&V 흐름 |
| II. 모델과 검증 절차 | 2.1 용어(recess/u/ε′zz/h_d)와 접촉 조건 m = u_t+u_b+h_t+h_b−(r_t+r_b). 2.2 열탄성 FEM(ANSYS, 이방성 Cu, 접합 측벽, 배열 셀, 공정별 유전체 1회 학습). 2.3 표면확산 항 h_d = s_ox·0.0022(θ_eff−90°)·D·f(ω)·[1−e^(−t/τ)], τ ∝ D^3.7/Ds(T), f(ω) facet 모델. 2.4 ASME V&V 10 순서와 사전등록(train/test 분할, 통과 기준, 커밋 해시) | Table 1 데이터와 역할 |
| III. 결과 | 3.1 탄성 모델 train/test(Table 2) + 측벽 판별 + 0.54 µm 실패 → 탄성 접촉 한계(Fig. 2). 3.2 확산 항 test(Fig. 3): 고정형 2/17 → 개정 11/17, ≥250 °C 10/10, 방위 항으로 IQR 10/17. 3.3 Ayoub 변형률(3 µm 부호 일치, 300 nm 크기 일치·부호 반대 → 계면 가설 한 문장). 3.4 300 nm 공정창(Fig. 4), recess 허용 사양(Fig. 5), 인자 순위·방위 하한(Fig. 6), 연결 단계 접촉면적·압력 한 문단 | Fig. 2–6, Table 2–3 |
| IV. 한계와 결론 | 검증된 것/안 된 것/탐색 표(Table 3), 한계 6개, 결론 3줄 | Table 3 |
| 참고문헌 | 영문 15편 | — |

서면 심사용 4쪽: 위에서 Fig. 1·5·6을 빼고(Fig. 2, 3, 4와 Table 2, 3만), 서론을 절반으로, 2.2–2.3을 식 두 개와 표 하나로 압축.

## 3. 그림 목록 (Claude Science로 구현; 지금은 placeholder)

| 번호 | 내용 | 원본 데이터/그림 | 구현 메모 |
|---|---|---|---|
| Fig. 1 | (a) 패드 쌍 단면: recess r, 탄성 u, bulge-out h_d, 접촉 조건; (b) V&V 흐름: 수치 검증 → 학습(큰 패드) → 테스트(held-out) → 예측(MC) — 사전등록 커밋 표시 | 새로 그림 | 두 패널, 영문 라벨 |
| Fig. 2 | 패드 크기별 위+아래 돌출: 탄성(모델 b=1, ×0.69, imec 실측) vs 확산(≥350 °C 포화, 실측 점검 범위 ≤300 nm 실선·외삽 점선) vs recess 합 5 nm; 교차 ≈ 0.7 µm | `s2_mechanism_transition.png`, `paper_results.json` | 확산 외삽선은 0.54 µm까지만; 교차점 화살표 |
| Fig. 3 | 확산 항 vs DM2026: (a) 400/500 nm 피치 중앙값·IQR vs T/시간, (b) 크기 의존(200–500 nm 피치, 250 °C), (c) f(ω) 곡선과 facet 분율 | `s2_diffusion_fit.png`, `orient_diffusion_round2.csv` | 실패 점(200 °C 큰 패드)을 빈 기호로 |
| Fig. 4 | 300 nm 공정창 경계: 온도(200–400 °C, 5 °C 간격)별 최소 어닐 시간, 청정/산화 패널, 주 설정 곡선 + 모든 조합 불확실 띠 + 최악 방위(f(0) > 0) 곡선, 250 °C 미만 회색(데이터 밖) | `s2_boundary_curves_300nm.png`, `results/stage2/v2/boundary_curves.json` | 곡선 |
| Fig. 5 | 300 nm CMP recess 허용 합(nm) 지도(T × t) | `s2_recess_spec_0.30um.png`, `paper_results.json` | 숫자 표기 |
| Fig. 6 | 요인별 경계 온도 이동(°C, 30분·2시간), 공정 변수/패드별 무작위 요인 색 구분 | `s2_factor_shift_300nm.png`, `boundary_curves.json` | 막대 |
| Fig. 2(b) 후보 | 구속 계수 C vs h/w: FEM 167런 + 실측 19점 + 대리식, 0.54 µm 이탈 표시 | `results/figures/agents/constraint_factor.png`, `src/agents/scaling_collapse.py` | 사전등록 데이터 재배치 + X35–X38 통과점 |
| Fig. 3(d) 후보 | 마스터 커브: h/(aD) vs t_eff(Q_eff 13.4), 등가 규칙 표 | `results/figures/agents/master_curve.png` | 사후 분석 표기 |
| Fig. 6(c) 후보 | 체인 수율 Y(N) vs 링크 수, 대립 Cu/fg-Cu, 문헌 점 | `results/figures/agents/yield_vs_chain_length.png` | 탐색 예측 표기 |
| Table 1 | 데이터셋: 그룹/공정/측정량/크기/역할(train·test·비교) | 보고서 §2 | |
| Table 2 | 탄성 모델 train/test 결과: 크기, T, 모델, 측정, 허용, 통과 | `validation_rev1.csv`, adopted_rev.json | |
| Table 3 | 모델 부분별 상태: 검증 통과 / 실패 / 탐색, 근거 커밋 | 보고서 §14 | |

## 4. 원고 초안 — 프로시딩용 (한국어 본문, 영문 그림·표·참고문헌) — v4

**제목(국문):** 서브마이크론 Cu 하이브리드 본딩의 접촉 결정 요인과 300 nm 공정창: 열탄성 접촉 한계와 표면확산을 결합한 모델의 사전등록 검증
**Title:** What Determines Cu–Cu Contact in Sub-Micron Hybrid Bonding: Elastic Contact Limit and a Pre-Registered Thermo-Elastic/Surface-Diffusion Process Window at 300 nm

**요약.** Cu/유전체 하이브리드 본딩에서 패드가 작아지면 어닐 중 열탄성 돌출만으로는 CMP recess를 닫지 못하고 표면확산 bulge-out이 접촉을 만든다. 본 논문은 문헌 물성으로 구성한 ANSYS 열탄성 FEM과 표면확산 해석식을 결합하고, ASME V&V 10 순서로 모든 테스트 기준을 결과 계산 전에 공개 저장소에 커밋하여 평가하였다. 접합 계면에서 위·아래 탄성 돌출 합이 recess 합 5 nm를 넘는 최소 패드 폭(탄성 접촉 한계)은 400 °C에서 약 0.7 µm이며, 등방 탄성 돌출의 구속 계수 대리식은 미사용 형상 4개에서 ±20 % 안에 들었다. ST/Leti 공정의 정성 관측 넷은 측벽 미끄럼·캡 하중 비전달 설정에서만 모두 일관되어, 계면 상태를 공정별 입력으로 두어야 함을 보였다. 패드별 recess·방위 산포와 모델 불확실성 전체에서, 300 nm 패드는 청정 표면 250 °C·2 h, 300 °C·30 min 이상에서 접촉 확률 0.99 이상을 유지하나, 최악 방위 기준의 결론은 측정되지 않은 <111> 패드의 bulge-out에 의존한다.

### I. 서론

웨이퍼 간(W2W) Cu/SiCN 하이브리드 본딩은 200 nm 피치까지 전기적 수율이 보고되었다[1]. 패드가 작아지면 어닐 중 Cu의 열탄성 팽창은 1 nm 수준으로 줄고, 상·하 패드의 접촉은 표면확산에 의한 Cu 원자의 재배치(bulge-out)가 만든다[2,3]. 이때 공정 설계 질문은 "어느 recess에서 닫히는가"에서 "어떤 어닐·표면·계면 조건에서, 패드마다 다른 recess·결정방위 같은 통제할 수 없는 산포가 있어도 얼마나 확실히 닫히는가"로 바뀐다.

본 논문은 어닐 중 Cu 패드가 솟는 양을 두 기구의 합으로 본다. (i) 열탄성 돌출 u: Cu와 유전체·Si의 열팽창 차이로 생기며 측벽 구속에 크게 좌우되고, 식으면 되돌아간다. (ii) 표면확산 bulge-out h_d: 표면에너지 구배를 줄이려 Cu 원자가 패드 중앙으로 이동해 생기며 어닐 온도·시간·표면 상태·결정 방위에 의존하고, 되돌아가지 않는다. 접촉 여유는 m = u_t + u_b + h_d,t + h_d,b − (r_t + r_b)이며, 두 경계를 구분한다: 탄성 접촉 한계(u_t + u_b = r_t + r_b)와 기여도 역전(h_d,t + h_d,b = u_t + u_b).

선행연구는 역할이 나뉘어 있다. Ayoub 등[4]은 300 nm 패드의 Laue 편차 변형률로 방위에 따른 탄성 차이를, Lin·Chen 등[5,6]은 in-situ AFM으로 1–9 µm 패드 돌출을, imec[2,3,7]은 수천 개 패드의 bulge-out 분포와 방위(EBSD)를 측정했다. Lhostis 등[12]은 같은 ST/Leti 계열 공정에서 패드 폭·두께에 따른 계면 닫힘을 HRTEM으로 보였다. 그러나 이 관측들을 하나의 모델 설정으로 함께 평가하고, 접촉을 정하는 요인들의 상대적 크기와 패드별 산포 아래 판정의 안정성을 정량화한 연구는 없다.

본 연구의 목적은 1 µm 아래 Cu–Cu 접촉을 결정하는 요인을 정량적으로 구분하고, 공정 변수와 패드별 무작위 요인이 공정창을 얼마나 움직이는지를 모델 불확실성과 함께 제시하는 것이다. 이를 위해 문헌 물성만으로 구성한 열탄성 FEM과 표면확산 해석식을 결합하고, 서로 다른 세 연구그룹의 실측(돌출, bulge-out 분포, Laue 변형률, HRTEM 계면 관찰)으로 시험하였다. 모든 시험 기준은 결과를 계산하기 전에 공개 저장소에 고정하였다. 2장에서 모델과 검증 절차를, 3장에서 탄성 모델·확산 항·계면 조건·300 nm 공정창의 결과를, 4장에서 기여와 한계를 논의한다.

### II. 모델과 검증 절차

**2.1 용어와 접촉 조건.** recess r(CMP 후 Cu 윗면이 유전체 면보다 낮은 깊이, 입력), u(열탄성 돌출, 중앙 50 % 면적 평균 − 주변 유전체), h_d(bulge-out, 패드 자기 표면 기준), ε′zz(Laue 편차 탄성 변형률)를 섞지 않는다. 방위와 recess를 확률 변수로 두고 P(m ≥ 0)를 Monte Carlo로 계산하며(표본 수는 수치 해상도이지 데이터가 아니다), 방위 분포 가정을 뺀 최악 방위 최소 여유 m_min도 함께 계산한다.

**2.2 열탄성 FEM.** ANSYS MAPDL. 원형 Cu 패드, 라이너 링·바닥층, 유전체, Si 기판등가층. 작은 패드는 3D(입방 탄성텐서를 결정 방향으로 회전한 이방성 Cu), 큰 다결정 패드는 2D 축대칭 Hill 등방. 계면 조건 두 가지: 접합(절점 공유)과 미끄럼(Cu 측벽 절점을 복제해 라이너와 법선 변위만 묶음 — 접선 무마찰·무분리; 라이너–유전체는 항상 접합). 미끄럼은 측벽 전단 비전달 경계조건이며 박리·손상을 모사한 것이 아니다. 같은 물리 규칙·Cu 물성·경계조건·메시 규칙을 모든 시료에 쓰고, 형상·라이너·유전체·피치·열이력만 시료별 입력이다. 유전체 E·α는 공정당 한 번, 큰 패드에서만 학습한다(NYCU SiO2 59 GPa·1.0 ppm/K, imec SiCN 120 GPa·2.0 ppm/K).

**2.3 표면확산 항.** DM2024[7]의 선형화를 따라 h_d = s_ox·0.0022(θ_eff − 90°)·D·f(ω)·[1 − exp(−t/τ)], τ = τ₀(D/200 nm)^3.7·D_s(350 °C)/D_s(T) ... (1). D 패드 지름, s_ox 표면 산화 배율(청정 1, 산화 0.45[2]), f(ω)는 패드 법선과 최근접 <111> 사이 각 ω의 방위 함수다({111}이 최저 표면에너지라 <111> 근방 패드는 곡률 구동력이 작다[3]). f(ω)는 관측 분포와 일관된 6종(계단, 완만 경사, 바닥값 0.25, 시그모이드, Fig. 5a형 계단·경사)을 함께 쓴다.

**2.4 검증 절차와 사전등록.** 학습은 큰 패드(NYCU 9·3 µm, imec 1.80·3.06 µm), 테스트는 imec 1.26·0.54 µm, NYCU 1 µm, 미끄럼 대조군이다. 확산 항은 imec 2026 400 nm 피치·350 °C 한 점에서 진폭만 학습하고 나머지 17점으로, 이후 미사용 DM2023 7점으로 테스트했다. 계면 조건은 ST/Leti 관측 넷을 같은 설정으로 평가하는 규칙을 먼저 고정했다. 모든 규칙은 계산 전 git 커밋으로 고정했고, 테스트 실패 시 문서화된 개정 1회만 허용했다(Table 1).

### III. 결과

**3.1 탄성 모델과 탄성 접촉 한계.** 학습값은 모두 문헌 범위의 끝이었다. 테스트에서 NYCU 1 µm(모델 1.79–1.94 vs 실측 2.1 ± 0.4 nm), imec 1.80 µm 전 온도, 1.26 µm 100–200 °C가 통과했고, 미끄럼 대조군은 1 µm에서 1.7배, 0.54 µm에서 3.5배 과대예측해 이 두 공정의 측벽은 접합으로 판별되었다(Table 2). imec 0.54 µm는 100–400 °C 전 구간에서 측정/모델 0.61–0.69로 과대예측했다(온도 무관; 단일 기하 가설 ≤ 7 %, 라이너 15·25 nm는 u 불변). FEM 167런과 실측 19점은 구속 계수 C = u/[(α_Cu − α_Si)ΔT·h]가 종횡비의 한 함수 C = c₀/[1 + a(E_d/E_Cu)(h/w)^1.5]로 모이고, 이 대리식은 사전등록한 미사용 형상 4개에서 ±20 % 안에 들었다(Hill 등방, imec·NYCU 적층). 0.54 µm 실측만 곡선 밖에 있다. recess 합 5 nm[10]로 고정하고 400 °C 돌출의 위·아래 합이 그것을 넘는 최소 폭을 구하면 실측 기준 0.70 µm(0.54 µm 2.8 nm와 1.26 µm 10 nm 사이의 log 보간), 대리식 기준 0.76 µm이다(Fig. 2). 이 한계는 recess와 온도의 함수다: 400 °C에서 recess 합 3/8 nm → 0.55/1.0 µm, recess 합 5 nm에서 350/300/250 °C → 0.90/1.14/1.62 µm(대리식). 300 nm에서 탄성 돌출은 400 °C에서도 패드당 ≈ 1 nm로 recess 합의 1/5이다. 기여도 역전 폭은 식 (1)을 300 nm 밖으로 외삽해야 하므로 예측으로만 제시한다: 250 °C 2 h 0.74 µm, 350 °C 1 h 1.38 µm, 400 °C 2 h 2.45 µm.

**3.2 표면확산 항: 시험 결과와 적용 범위.** 사전등록 고정형은 DM2026 17점 중 2점, 진폭 θ_eff를 학습한 개정 1은 11점을 통과해 규칙상 NOT VALIDATED이다. 실패는 200 °C·D ≥ 250 nm와 자가 어닐 Cu의 과소예측에 몰려 있고, ≥ 250 °C에서는 PPA-Cu 5/5, 전체 8/9가 허용오차 안이다(Fig. 3). 시간 의존: 200 °C 2 h→4 h 증가율 1.49 ± 0.13은 지수형 동역학과 양립하고, stretched exponential(β = 1/4; 두 배 증가율 상한 1.189)과는 2.3σ로 양립하지 않는다. 사후 분석에서 PPA-Cu 10점은 유효 활성화에너지 13.4 kcal/mol(문헌 저온값 13과 일치)로 한 곡선에 모였다. 이 형태를 고정해 미사용 DM2023(cavity/pad ≤ 0.5)으로 시험한 라운드 3는 0/7이었다: 등크기 패드 항은 불균등 구조로 전이되지 않는다. 따라서 식 (1)의 적용 범위는 등크기 접합·≥ 250 °C다. 방위: DM2026 분포의 판독 가능한 범위(누적 ≥ 0.5 %; 300 nm 패드 Fig. 3에서 6.5 nm 이하 3–4 %, 280 nm 패드 Fig. 5a에서 ≈ 10 %)와 일관된 f(ω) 4종은 모두 중앙값 11/17, IQR 13/17을 주며(방위 없는 모델 IQR 0), 몸통 폭 일부는 방위와 무관한 산포가 맡아야 한다. 정확히 <111>인 패드의 bulge-out f(0)과 누적 0.1 % 아래 꼬리는 관측되지 않았다.

**3.3 계면 조건: 같은 설정으로 본 ST/Leti 관측.** Ayoub 3 µm 부호는 접합·미끄럼(캡 유무) 모두 일치한다(−1.23 … −1.27 × 10⁻³). Ayoub 300 nm 부호는 측벽 미끄럼에 캡까지 하중을 전달하지 않을 때만 맞는다(접합 캡을 두면 측벽 미끄럼만으로는 반대 부호). Lhostis 폭 효과(110 nm 폭의 중심 공극이 360 nm보다 큼)는 접합(공극 분율 0.62 vs 0.10)과 미끄럼(0.35 vs 0.15) 모두 재현되고, 두께 효과(650 nm 닫힘·220 nm 공극)는 미끄럼에서만 나온다(접합은 공극 분율 차 ≤ 0.13). 따라서 네 관측을 모두 만족하는 설정은 "측벽 미끄럼 + 캡 하중 비전달" 하나이고 접합은 둘을 실패한다(Table 3). 정량으로는 패드 10의 가열 기울기가 40 % 작고 방위 비(0.41 vs 0.64)가 맞지 않으며, 두께 규칙은 기록을 본 뒤 설계됐다. imec·NYCU 돌출은 같은 미끄럼 설정에서 1.7–3.5배 과대예측한다. 계면 상태는 공정별 입력이며 ST/Leti 이완은 후보 가설이다.

**3.4 300 nm 공정창과 요인별 영향.** 탄성 항은 결정방위 정보를 끝까지 유지했다: 300 nm 패드에 대해 방향 77개(학습 45, 검증 20, 면내 회전 12) × 계면 2종 = 154개 3D ANSYS 해석으로 방향 2자유도 다항 회귀 응답표면(대리모델)을 만들고, 학습에 쓰지 않은 20방향에서 검증했다(접합: 2차식 최대 오차 0.46 %, 0.006 nm; 사전등록 기준 통과). 면내 회전 영향은 0.2 % 이하, 같은 E_z를 갖는 다른 방향의 차이는 0.34 % 이하로, 이 형상에서는 E_z 하나로 줄여도 정보 손실이 거의 없었다(공정창 판정 변화 0). 접합 계면에서 탄성 돌출의 방위 폭은 5 %([100]이 최소)다. 이 대리모델(탄성 계수 b ∈ {0.60, 0.69, 0.93, 1.0})과 식 (1)의 단순합으로, 상·하 방위(구면 균일 가정)와 recess(패드당 N(2.5, 0.5²) nm[10])를 확률 변수로 두고 P(m ≥ 0)를 계산했으며, 판독 범위와 일관된 f(ω) 6종 × b × τ₀{20, 60, 100 s} × Q{20.7, 13.4}의 모든 조합을 겹쳤다(Fig. 4). 온도 200–400 °C를 5 °C 간격, 시간 1분–4시간을 로그 간격 40점으로 계산해 P ≥ 0.99 경계를 '온도별 최소 어닐 시간' 곡선으로 그렸다(Fig. 4; 촘촘한 격자는 경계를 정밀하게 할 뿐 검증 데이터를 늘리지는 않는다). 탄성만으로 닫히는 조건은 없다. 청정 표면 주 설정의 경계는 30분에서 253 °C, 2시간에서 220 °C이고(250 °C 미만은 데이터 밖이며 모델이 보수적), 모든 불확실성 조합에서 유지되려면 5분 342 °C, 30분 285 °C, 2시간 248 °C 이상이 필요하다. 산화 표면은 같은 기준에서 30분 334 °C, 2시간 295 °C로 약 40–50 °C 높다. 요인의 영향은 경계 온도의 이동으로 나타냈다(2시간 / 30분 기준, Fig. 6): 확산이 없으면 400 °C까지 어떤 조건도 닫히지 않는다. 확산 속도 상수 τ₀(20↔100 s) 31/40 °C, 라이너 접촉각(107↔149°) 35/39 °C, 표면 산화 25/28 °C, 활성화에너지(13.4↔20.7 kcal/mol) 20/39 °C, 측벽 계면 상태(접합↔미끄럼) 14/19 °C, 방위 꼬리의 모양(f(ω) 6종) 15/16 °C, recess 평균(2.5→3.5 nm/패드) 10/12 °C, 방위 꼬리의 유무 10/10 °C, recess 산포(σ 0.5→1.0 nm) 4/4 °C, 탄성 계수 b(0.60↔1.0) 3/4 °C. 즉 공정창은 열예산을 정하는 확산 동역학·라이너·표면이 주로 정하고, recess와 방위 같은 패드별 무작위 요인은 경계를 수–십여 °C 옮기며 주로 수율의 하위 꼬리에 작용한다. 그 꼬리의 최악 조건(방위 분포 가정 제거)은 정확히 <111>인 패드의 bulge-out f(0)이 정한다: f(0) = 0인 4종이면 최악 쌍의 여유는 탄성 단독(400 °C 30 min에서 −5.1 nm)과 같아 어떤 어닐로도 닫히지 않고, f(0) > 0인 2종(바닥값 0.25, 시그모이드)이면 최악 쌍도 2시간 기준 265–290 °C, 30분 기준 304–324 °C 이상에서 닫힌다. 허용 recess(패드당, 청정)는 확률 기준 3.5–9 nm, 최악 조건 기준 0.5–0.9 nm(f(0) = 0) 또는 2.4–4.2 nm(f(0) > 0)다(Fig. 5). 상·하 방위가 같은 순위로 짝지어지면 P가 0.965까지 떨어진다(의존성 민감도). 높이합 판정의 타당성은 접촉 FEM(2D 축대칭, Cu–Cu 마찰 접촉, 등방 소성)으로 점검했다: 접합 계면 300 nm·350 °C에서 높이합 예측과 FEM 중심 공극 분율(recess 1–4 nm/패드: 0.00/0.06/0.32/0.47)이 4/4 일치했다(기존 기록 재분석). 접합 계면에서는 Cu 표면이 돔형으로 솟아 중심 높이가 닫힘을 정한다. 반대로 미끄럼 계면에서는 Cu가 플러그처럼 통째로 올라 가장자리만 닿고 중심 공극이 남아(사전등록 시험 2/4 일치) 높이합 판정이 낙관적이므로, 미끄럼 계면의 공정창은 가장자리 접촉 기준으로만 해석한다.

### IV. 고찰 및 결론

**4.1 기여.** 본 연구가 선행연구에 더한 것은 세 가지다. ① **탄성 접촉 한계의 정량 규칙.** 선행연구는 "sub-µm에서는 탄성 팽창이 작아 표면확산이 접촉을 만든다"고 정성적으로 보고했다[2,10]. 본 연구는 두 그룹의 돌출 실측으로 학습·테스트한 열탄성 모델에서 그 경계를 recess 조건부 규칙으로 제시했고(400 °C, recess 합 3/5/8 nm → 0.55/0.70/1.0 µm), 등방 탄성 대리식 C(h/w)를 미사용 형상으로 검증했다. ② **계면 조건을 하나의 설정으로 평가.** 선행연구들은 서로 다른 공정의 관측을 각자의 모델로 해석했다[4,12]. 같은 설정으로 ST/Leti 관측 넷을 평가하면 측벽 미끄럼·캡 하중 비전달 설정만 모두와 일관하고, imec·NYCU 돌출은 접합을 요구한다 — 계면 상태는 공정별 입력이며 공정창 해석에서 먼저 정해야 할 변수다. ③ **요인 순위와 판정의 안정성.** 공정창을 가장 크게 움직이는 것은 지배 기구와 열예산·표면·라이너·계면 상태이고, recess 산포와 결정방위 같은 패드별 무작위 요인은 수율의 하위 꼬리를 정한다. Ayoub[4]가 방위의 탄성 차이로 recess 사양을 제안한 것과 달리, 접합 패드에서 방위의 탄성 효과는 4–5 %로 작고 꼬리는 확산 쪽(<111>)에서 생긴다. 모델 불확실성 전체에서 유지되는 레시피(청정 표면 250 °C·2 h, 300 °C ≥ 30 min)와 가정에 따라 갈리는 레시피를 구분해, 판정을 확정하려면 무엇을 측정해야 하는지(정확히 <111>인 패드의 bulge-out)를 특정했다.

**4.2 한계와 결론.** 
Table 3에 모델 부분별 상태를 정리했다. 한계: (1) 0.54 µm 탄성 오차의 원인은 원 데이터(Okudur 2017[11]) 부재로 미상이다. (2) 300 nm 돌출 실측이 없어 300 nm 결과는 예측이다. (3) 확산 항은 사전등록 시험을 통과하지 못했고 적용 범위는 등크기·≥ 250 °C다; 200 °C 동역학과 Cu 이력은 모델 밖이다. (4) f(0)과 누적 0.1 % 아래 꼬리는 관측되지 않았다. (5) ST/Leti 계면 이완은 정성 관측 넷과 일관한 후보 가설이며 정량 불일치가 남는다. (6) 오버레이·크리프는 범위 밖이다.
결론: 접합 계면에서 위·아래 탄성 돌출이 recess 합 5 nm를 닫는 한계는 약 0.7 µm(400 °C)이며, 300 nm에서 접촉은 표면확산에 의존한다. 청정 표면 250 °C·2 h, 300 °C·30 min 이상은 패드별 산포와 모든 모델 불확실성에서 접촉 확률 0.99 이상을 유지한다. 공정창을 가장 크게 움직이는 것은 열예산·표면·라이너·계면 상태이며, recess 산포와 방위는 수율의 하위 꼬리를 정한다. 그 꼬리의 최악 조건 보증은 정확히 <111>인 패드의 bulge-out 측정에 달려 있다. 주장 수위는 "검증 통과 범위의 탄성 모델 + 실측으로 점검한 확산 모델로 본 공정창 예측(불확실도 포함)"이다.

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

**Table 3 Status of each model part (and the same-setting interface matrix).**
| Part | Status | Evidence (commit) |
|---|---|---|
| Elastic u, ≥ 1 µm, bonded sidewall | validated (pre-registered) | 33a8f5c → B/Br runs |
| Elastic contact limit (u_t+u_b = R) | 0.70 µm at 400 °C, R 5 nm (imec data); 0.55/1.0 µm at R 3/8 nm | paper_results.json, boundaries.json |
| Isotropic elastic surrogate C(h/w) | validated on 4 unseen geometries within 20 % (pre-registered) | 8194e62 → round_x2.json |
| Elastic u, 0.54 µm | not validated (+46 %, athermal); liner hypothesis rejected | 2acfd92 / X30–X34 |
| Contribution crossover (h = u) | prediction only (extrapolated, 0.74–2.45 µm by anneal) | boundaries.json |
| Diffusion h_d | not validated (2/17, 11/17, DM2023 0/7); ≥ 250 °C PPA-Cu 5/5; scope equal-pad, ≥ 250 °C | 9c6bc29 / eb347c1 / db29b8e |
| Orientation function f(ω) | exploratory: 6 variants consistent with readable quantiles; f(0) unobserved | docs/v2/diffusion_f_omega.md |
| Elastic orientation surrogate (300 nm) | validated on 20 held-out directions (pre-registered): bonded quadratic max 0.46 %, sliding cubic max 1.35 %; in-plane ≤ 0.2 %; Ez loss ≤ 1.1 % | 13a580f / c7e2eb4 |
| Height-sum criterion vs contact FEM | bonded 4/4 (existing records), sliding 2/4 (pre-registered, rim contact only) | 4beb028 / 372e328 |
| ST/Leti interface | bonded 2/4 qualitative observations; sliding + non-load-bearing cap 4/4; quantitative mismatch (pad 10 slope 0.60) | 83bf8e3 / a1f4668 |
| imec/NYCU interface | bonded required (sliding 1.7–3.5× over-prediction) | V4 |
| 300 nm window | prediction: 9 cells robust, 5 undetermined (probability); worst orientation set by f(0) | window_summary.json, f_omega_variants.json |

## 6. 서면 심사용(4쪽) 압축 지침
- 요약 150자, 서론 2문단(문제 + 기여 3개), II는 식 (1)과 접촉 조건, V&V 분할 한 문단, Table 1 생략, III는 3.1(Fig. 2) · 3.2(Fig. 3) · 3.4(Fig. 4, Table 2 축약), IV 한계 4개 + 결론. Table 3는 6행으로.
- 저자·소속·이메일·저장소 URL·"우리 연구실" 등 식별 문구 금지. 커밋 해시는 "공개 저장소에 사전등록(해시는 채택 후 공개)"으로.
