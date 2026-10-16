# -*- coding: utf-8 -*-
r"""
Text of the IEIE 2026 fall submissions, v5.1 (scope: Cu sidewall bonded to the liner).
Source of content and numbers: docs/paper/ieie2026f_plan_and_draft_ko.md (v5.1) with
docs/paper/corrections_v4.md and docs/paper/claude_science_prompt_ko.md (v5.1 > v5 > v4.5 > v4.4 ...).
Numbers in sec. 3.3 were checked against results/stage2/v2/boundary_curves.json and
results/stage2/v2/f_omega_variants.json (docs/paper/ieie2026f_number_sources.md).

Markup: _{..} subscript, ^{..} superscript, <i>..</i> italic, [@KEY] citation (numbered by first use).
No 'pre-registration' wording (v5.1); no cell counts (v4.4); no sliding-interface results beyond the
bonded/sliding discrimination (v5); response surface instead of surrogate model.
"""

TITLE_KO = "300 nm Cu 하이브리드 본딩의 접촉 결정 요인과 공정 조건: 열탄성 돌출과 표면확산을 결합한 모델"
TITLE_KO_LINES = ["300 nm Cu 하이브리드 본딩의 접촉 결정 요인과", "공정 조건: 열탄성 돌출과 표면확산을 결합한 모델"]
TITLE_EN = ("Contact-Determining Factors and Process Conditions in 300 nm Cu Hybrid Bonding: "
            "A Model Coupling Thermo-Elastic Protrusion and Surface Diffusion")
TITLE_EN_LINES = ["Contact-Determining Factors and Process Conditions in 300 nm Cu Hybrid Bonding:",
                  "A Model Coupling Thermo-Elastic Protrusion and Surface Diffusion"]

ABSTRACT_EN = (
    "Below 1 µm, thermo-elastic protrusion of Cu hybrid-bonding pads no longer closes the CMP recess, and "
    "surface-diffusion bulge-out has to make the Cu–Cu contact. We couple an ANSYS thermo-elastic FEM built from "
    "literature properties with an analytic surface-diffusion term; the train/test split and the acceptance criteria "
    "were fixed before computation and the test data were evaluated once. For a sidewall bonded to the liner, the "
    "elastic contact limit (top + bottom elastic protrusion = 5 nm recess sum) is about 0.7 µm at 400 °C. With "
    "pad-to-pad recess and orientation scatter over the tested set of model uncertainties, 300 nm pads keep a contact "
    "probability of at least 0.99 on a clean surface at about 250 °C for 2 h and 300 °C for 30 min or longer "
    "(conditional prediction); the worst-orientation conclusion depends on the unmeasured bulge-out of pads oriented "
    "exactly along <111>.")
ABSTRACT_KO = (
    "Cu 하이브리드 본딩 패드가 1 µm 아래로 작아지면 열탄성 돌출만으로는 CMP recess를 닫지 못한다. 문헌 물성 "
    "열탄성 FEM과 표면확산 해석식을 결합하고, 학습·테스트 데이터 분할과 합격 기준을 계산 전에 고정해 세 "
    "연구그룹의 실측으로 시험하였다. 측벽 접합 조건에서 탄성 접촉 한계는 약 0.7 µm(400 °C, recess 합 5 nm)이고, "
    "300 nm 패드는 패드별 산포와 시험한 불확실성 집합에서 청정 표면 약 250 °C·2 h, 300 °C·30 min 이상이면 접촉 "
    "확률 0.99 이상을 유지한다(조건부 예측).")
KEYWORDS = "Hybrid bonding, Cu bulge-out, surface diffusion, thermo-elastic FEM, process window"

# ------------------------------------------------------------------ proceedings body
INTRO = [
    "웨이퍼 간(W2W) Cu/SiCN 하이브리드 본딩은 200 nm 피치까지 전기적 수율이 보고되었다[@VH26]. 패드가 작아지면 "
    "어닐 중 Cu의 열탄성 팽창은 1 nm 수준으로 줄고, 상·하 패드의 접촉은 표면확산에 의한 Cu 원자의 재배치"
    "(bulge-out)가 만든다[@DM23,@DM26]. 이때 설계 질문은 \"어느 recess에서 닫히는가\"에서 \"패드마다 다른 "
    "recess·결정방위 같은 통제할 수 없는 산포가 있어도 어떤 어닐·표면 조건에서 얼마나 확실히 닫히는가\"로 바뀐다.",
    "본 논문은 Cu 패드가 솟는 양을 두 기구의 합으로 본다. 열탄성 돌출 u는 Cu와 유전체·Si의 열팽창 차이로 생기고 "
    "측벽 구속에 좌우되며 식으면 되돌아간다. 표면확산 bulge-out h_{d}는 Cu 원자가 패드 중앙으로 이동해 생기며 "
    "어닐 온도·시간·표면 상태·결정방위에 의존하고 되돌아가지 않는다. 접촉 여유는 m = u_{t} + u_{b} + h_{d,t} + "
    "h_{d,b} − (r_{t} + r_{b})이고(Fig. 1a), 탄성 접촉 한계(u_{t} + u_{b} = r_{t} + r_{b})와 기여도 역전"
    "(h_{d,t} + h_{d,b} = u_{t} + u_{b})을 구분한다.",
    "선행연구는 역할이 나뉘어 있다. Ayoub 등[@AY22]은 300 nm 패드의 Laue 편차 변형률을, Lin·Chen 등[@LIN25,@CHEN25]은 "
    "in-situ AFM으로 1–9 µm 패드 돌출을, imec[@DM23,@DM26,@DM24]은 수천 개 패드의 bulge-out 분포와 방위(EBSD)를 "
    "측정했고, Cu/SiCN 패드 팽창은 FEM으로[@TSAU22], 열팽창과 표면확산의 결합은 어닐 모델로[@HOOGE24] 다루어졌다. "
    "그러나 이 관측들로 한 모델을 학습·테스트하고, 모델 가정에 따라 접촉 판정이 유지되는지 갈리는지를 패드별 "
    "산포와 함께 정량화한 연구는 없다.",
    "본 연구의 목적은 Cu 측벽이 라이너에 접합된 공정(imec·NYCU형)에서 1 µm 아래 Cu–Cu 접촉을 결정하는 요인을 "
    "구분하고, 공정 변수와 패드별 무작위 요인이 공정창을 얼마나 움직이는지를 모델 불확실성과 함께 제시하는 "
    "것이다. 문헌 물성 열탄성 FEM과 표면확산 해석식을 결합해 세 연구그룹의 실측(돌출, bulge-out 분포, Laue "
    "변형률)으로 시험했다. 학습·테스트 데이터 분할과 합격 기준은 계산 전에 고정하였고(공개 저장소 커밋 기록), "
    "테스트 데이터는 한 번만 평가하였다.",
]

S21 = ("recess r(CMP 후 Cu 윗면이 유전체 면보다 낮은 깊이, 입력), u(열탄성 돌출, 중앙 50 % 면적 평균), h_{d}"
       "(bulge-out, 패드 자기 표면 기준), ε′_{zz}(Laue 편차 탄성 변형률)를 섞지 않는다. 방위와 recess를 확률 변수로 "
       "두고 P(m ≥ 0)를 Monte Carlo로 계산하며, 방위 분포 가정을 뺀 최악 방위 여유 m_{min}도 함께 계산한다.")
S22 = ("ANSYS MAPDL로 원형 Cu 패드, 라이너, 유전체, Si 기판 등가층을 모델링했다(작은 패드는 입방 탄성텐서를 회전한 "
       "3D 이방성 Cu, 큰 다결정 패드는 2D 축대칭 Hill 등방). Cu와 Ta/TaN 라이너는 밀착된 계면이므로 측벽은 접합"
       "(절점 공유)으로 두고, 측벽 전단이 전달되지 않는 반대 극한(미끄럼)을 대조군으로 두어 실측으로 판별한다(3.1). "
       "물리 규칙·Cu 물성·경계조건·메시 규칙은 모든 시료에 같고, 유전체 E·α만 공정당 한 번 큰 패드에서 학습한다"
       "(NYCU SiO_{2} 59 GPa·1.0 ppm/K, imec SiCN 120 GPa·2.0 ppm/K).")
S23a = ("DM2024[@DM24]의 선형화를 따라 표면확산 항을 다음과 같이 둔다.")
EQ_LINES = ["h_{d} = s_{ox}·0.0022(θ_{eff} − 90°)·D·f(ω)·[1 − e^{−t/τ}],",
            "τ = τ_{0}(D/200 nm)^{3.7}·D_{s}(350 °C)/D_{s}(T)"]
S23b = ("D는 패드 지름, s_{ox}는 표면 산화 배율(청정 1, 산화 0.45[@DM23]), D_{s}(T)는 Q = 20.7 kcal/mol[@BUT73]의 "
        "아레니우스 의존이다. f(ω)는 패드 법선과 최근접 <111> 사이 각 ω의 방위 함수로({111} 근방 패드는 곡률 "
        "구동력이 작다[@DM26]), 300 nm 분포(DM2026 Fig. 3)의 q10–q90과 6.5 nm 이하 분율에 맞춘 기본 4종(V2–V5)과 "
        "다른 시료(280 nm, Fig. 5a)의 ≈ 10 % 꼬리를 반영한 비관 시나리오 2종(V6–V7)을 함께 쓴다(Fig. 3c).")
S24 = ("ASME V&V 10[@ASME]의 순서(Fig. 1b)를 따랐고, 데이터별 역할은 Table 1과 같다. 확산 항은 imec 2026 한 점"
       "(400 nm 피치, 350 °C)에서 진폭만 학습했다. 학습·테스트 데이터 분할과 합격 기준은 계산 전에 고정하였고, 테스트 "
       "데이터는 한 번만 평가하였다. 실패 후 수정은 문서화된 1회로 제한하고 같은 기준으로 판정했다.")
S31a = ("학습값은 모두 문헌 범위의 끝이었다. 테스트에서 NYCU 1 µm, imec 1.80 µm 전 온도, 1.26 µm 100–200 °C가 "
        "통과했고, 미끄럼 대조군은 1 µm에서 1.7배, 0.54 µm에서 3.5배 과대예측해 측벽은 접합으로 판별되었다(Table 2). "
        "이후 결과는 모두 이 조건이다. imec 0.54 µm는 전 온도에서 측정/모델 0.61–0.69로 과대예측했다(온도 무관; "
        "단일 기하 가설 ≤ 7 %, 라이너 15·25 nm는 u 불변).")
S31b = ("FEM 167런과 실측 19점에서 구속 계수 C = u/[(α_{Cu} − α_{Si})ΔT·h]는 종횡비의 한 함수 "
        "C = c_{0}/[1 + a(E_{d}/E_{Cu})(h/w)^{1.5}]로 모이고, 이 근사식은 미리 고정한 기준으로 미사용 형상 4개에서 "
        "±20 % 안에 들었다. recess 합 5 nm[@VHIRPS]에서 400 °C 위·아래 돌출 합이 그것을 넘는 최소 폭은 실측 기준 "
        "0.70 µm(0.54 µm 2.8 nm와 1.26 µm 10 nm 사이 log 보간), 근사식 0.76 µm다(Fig. 2). 400 °C에서 recess 합 3/8 nm → "
        "0.55/1.0 µm, recess 합 5 nm에서 350/300/250 °C → 0.90/1.14/1.62 µm다. 300 nm의 탄성 돌출은 400 °C에서도 "
        "패드당 ≈ 1 nm다. 기여도 역전 폭은 식 (1)의 외삽이 필요해 예측으로만 제시한다(250 °C 2 h 0.74 µm, 350 °C 1 h "
        "1.38 µm, 400 °C 2 h 2.45 µm).")
S32a = ("계산 전에 고정한 원래 형태는 DM2026 17점 중 2점, 진폭 θ_{eff}를 학습한 개정 1은 11점을 통과해 규칙상 검증 "
        "통과가 아니다. 실패는 200 °C·D ≥ 250 nm와 자가 어닐 Cu의 과소예측에 몰려 있고, ≥ 250 °C에서는 PPA-Cu 5/5, "
        "전체 8/9가 허용오차 안이다(Fig. 3a·b). 200 °C 2 h→4 h 증가율 1.49 ± 0.13은 지수형 동역학과 양립하고, "
        "β = 1/4 stretched exponential(상한 1.189)과는 2.3σ로 양립하지 않는다. 미사용 DM2023(불균등 패드) 시험은 "
        "0/7이어서 식 (1)의 적용 범위는 등크기 접합·≥ 250 °C다.")
S32b = ("τ_{0}는 포화된 학습점(350 °C 1 h)에서 식별되지 않아, DM2023의 \"350 °C 5분 안에 완료\" 관찰[@DM23]과 "
        "일관된 20–100 s 범위로 보고하고 양 끝을 모두 쓴다. f(ω) 6종은 모두 중앙값 11–12/17, IQR 13/17을 주지만"
        "(방위 없는 모델 IQR 0), 채택 기준에 넣지 않은 하위 분위수(q1–q5) 오차는 기본형 V3 0.49 nm, 비관형 V6 5.78 nm로 "
        "다르다. 즉 V6–V7은 같은 실측의 재현이 아니라 불확실성 평가용 시나리오다. 정확히 <111>인 패드의 bulge-out "
        "f(0)과 누적 0.1 % 아래 꼬리는 관측되지 않았다.")
S33a = ("300 nm 패드의 탄성 항은 방향 77개(학습 45, 검증 20, 면내 회전 12) 3D 해석의 다항 회귀 응답표면으로 방위를 "
        "유지했다(미사용 20방향 최대 오차 0.46 %, 미리 고정한 기준 통과; 방위 폭 5 %, [100] 최소). 이 응답표면"
        "(b ∈ {0.60, 0.69, 0.93, 1.0})과 식 (1)로 상·하 방위(구면 균일)와 recess(패드당 N(2.5, 0.5^{2}) nm[@VHIRPS])를 "
        "확률 변수로 두고 P(m ≥ 0)를 계산해, 시험한 불확실성 집합 f(ω) 6종 × b × τ_{0}{20, 60, 100 s} × Q{20.7, 13.4}의 "
        "모든 조합을 겹쳤다. 200–400 °C를 5 °C 간격, 1분–4시간을 로그 40점으로 계산해 P ≥ 0.99 경계를 온도별 최소 어닐 시간 "
        "곡선으로 그렸다(Fig. 4; 촘촘한 격자는 경계를 정밀하게 할 뿐 검증 데이터를 늘리지 않는다).")
S33b = ("탄성만으로 닫히는 조건은 없다. 청정 표면 주 설정의 경계는 30분에서 253 °C, 2시간에서 220 °C이고"
        "(250 °C 미만은 데이터 밖이며 모델이 보수적), 시험한 모든 조합에서 유지되려면 5분 342 °C, 30분 285 °C, "
        "2시간 약 250 °C(5 °C 격자 보간 248 °C) 이상이 필요하다. 이는 명시한 불확실성 집합 안의 조건부 예측이며, "
        "상·하 방위의 독립성, recess 분포, 확산식 형태까지 검증한 사양은 아니다. 산화 표면은 같은 기준에서 30분 334 °C, 2시간 295 °C로 약 40–50 °C 높다.")
S33c = ("요인의 영향은 경계 온도의 이동으로 나타냈다(2시간/30분, Fig. 6a). 확산이 없으면 400 °C까지 어떤 조건도 "
        "닫히지 않는다. τ_{0}(20↔100 s) 36/40 °C, 라이너 접촉각(107↔149°) 35/39 °C, 표면 산화 25/28 °C, 활성화"
        "에너지(13.4↔20.7 kcal/mol) 49/39 °C, f(ω) 꼬리 모양 15/16 °C, recess 평균(2.5→3.5 nm/패드) 10/12 °C, 방위 "
        "꼬리 유무 10/10 °C, recess 산포(σ 0.5→1.0 nm) 4/4 °C, 탄성 계수 b(0.60↔1.0) 3/4 °C다. 같은 요인을 최소 "
        "어닐 시간의 배수로 보면 온도와 거의 무관하다(Fig. 6b; 250 °C에서 τ_{0} ×5.0, 라이너 ×4.5, 산화 ×2.9, 꼬리 "
        "모양 ×1.9, recess 평균 ×1.6, 방위 꼬리 ×1.5, recess 산포·b ×1.2). 30분 이동이 2시간보다 큰 것은 요인이 "
        "강해져서가 아니라, 고온일수록 1 °C당 확산이 덜 빨라져 같은 시간 배수에 더 많은 °C가 들기 때문이다(아레니우스 "
        "환산). 활성화에너지만 기준 데이터(350 °C)에서 멀어질수록 커진다(320 °C ×1.4 → 220 °C ×4.7). 즉 공정창은 "
        "확산 동역학·라이너·표면이 정하고, recess와 방위 같은 패드별 무작위 요인은 경계를 수–십여 °C 옮기며 주로 "
        "수율의 하위 꼬리에 작용한다.")
S33d = ("그 꼬리의 최악 조건(방위 분포 가정 제거)은 정확히 <111>인 패드의 bulge-out f(0)이 정한다. f(0) = 0인 "
        "4종이면 최악 쌍의 여유는 탄성 단독(400 °C 30 min에서 −5.1 nm)과 같아 어떤 어닐로도 닫히지 않고, f(0) > 0인 "
        "2종(바닥값 0.25, 시그모이드)이면 최악 쌍도 2시간 기준 265–290 °C, 30분 기준 304–324 °C 이상에서 닫힌다"
        "(Fig. 4a 점선). 허용 recess(패드당, 청정)는 확률 기준 3.5–9 nm, 최악 조건 기준 0.5–0.9 nm(f(0) = 0) 또는 "
        "2.4–4.2 nm(f(0) > 0)다(Fig. 5). 상·하 방위가 같은 순위로 짝지어지면 P가 0.965까지 떨어진다(의존성 "
        "민감도).")
S33e = ("높이합 판정은 확산을 넣지 않은 기존 탄성 접촉 FEM(2D 축대칭, Cu–Cu 마찰 접촉, 등방 소성[@OKORO])의 재분석으로 "
        "점검했다. 시험한 접합 측벽·탄성 접촉 조건(300 nm, 350 °C, recess 1–4 nm/패드; 중심 공극 분율 "
        "0.00/0.06/0.32/0.47)에서 높이합 판정과 중심 공극의 닫힘 판정이 4/4 일치했다. 확산으로 표면이 변한 뒤의 "
        "접촉 면적·공극까지 검증한 것은 아니다.")
S41 = ("기여는 두 가지다. ① 탄성 접촉 한계의 정량 규칙: 선행연구가 정성적으로 보고한 \"sub-µm에서는 표면확산이 "
       "접촉을 만든다\"[@DM23,@VHIRPS]를, 두 그룹의 실측으로 학습·테스트한 열탄성 모델에서 recess 조건부 규칙"
       "(400 °C, 3/5/8 nm → 0.55/0.70/1.0 µm)과 미사용 형상으로 검증한 근사식 C(h/w)로 정량화했다. ② 요인 순위와 "
       "판정의 안정성: 측벽 접합 공정에서 공정창을 가장 크게 움직이는 것은 지배 기구와 열예산·표면·라이너이고, "
       "recess 산포와 방위는 수율의 하위 꼬리를 정한다. 방위의 탄성 효과는 5 %로 작아 Ayoub[@AY22]의 탄성 기반 "
       "recess 사양과 달리 꼬리는 확산 쪽(<111>)에서 생긴다. 열팽창과 표면확산을 결합해 recess와 어닐 조건을 다룬 "
       "Hooge 등[@HOOGE24]과 달리, 본 연구는 실측으로 학습·테스트한 모델에서 불확실성 조합별 판정의 안정성(유지 "
       "조건과 갈리는 조건)과 최악 방위 기준을 구분하고, 최악 방위의 접촉을 확정하려면 정확히 <111>인 패드의 "
       "bulge-out 측정이 필요함을 특정했다.")
S42a = ("Table 3에 모델 부분별 상태를 정리했다. 한계: (1) 0.54 µm 탄성 오차의 원인은 원 데이터(Okudur 2017"
        "[@OKU17]) 부재로 미상이다. (2) 300 nm 돌출 실측이 없어 300 nm 결과는 예측이다. (3) 확산 항은 미리 고정한 "
        "기준의 테스트를 통과하지 못했고 적용 범위는 등크기·≥ 250 °C다; 200 °C 동역학과 Cu 이력은 모델 밖이다. "
        "(4) f(0)과 누적 0.1 % 아래 꼬리는 관측되지 않았다. (5) Ayoub 300 nm 변형률[@AY22,@AYTH]은 크기는 맞으나 "
        "부호가 반대이며, 부호 규약 차이는 3 µm 시험으로 배제되었다; 원인은 열린 문제다. (6) 오버레이·크리프는 "
        "범위 밖이다.")
S42_FUT = ("후속 연구는 두 갈래다. 새 측정 없이 할 수 있는 것은 결정립 방위별 bulge-out 문헌 데이터로 f(ω) 6종 중 "
           "어긋나는 것을 제외하는 일(꼬리 모양은 경계를 15–16 °C, 시간 ×1.9 옮긴다)과, 250 °C 이하 어닐 시간별 "
           "돌출 데이터로 Q의 저온 영향을 줄이는 일이다(모든 조합 2시간 경계 248 °C가 데이터 하한 바로 위에 "
           "있다). 측정이 있어야 하는 것은 정확히 <111>인 패드의 bulge-out f(0)과 300 nm 돌출 실측이다.")
S42b = ("결론: 접합 계면에서 탄성 돌출이 recess 합 5 nm를 닫는 한계는 약 0.7 µm(400 °C)이며, 접합 측벽의 300 nm "
        "패드에서는 탄성보다 확산 모델이 접촉 판정을 좌우한다. 청정 표면 약 250 °C·2 h, 300 °C·30 min 이상은 시험한 "
        "불확실성 집합에서 접촉 확률 0.99 이상이 유지되는 조건부 예측이고, 최악 방위의 접촉은 정확히 <111>인 패드의 "
        "bulge-out에 달려 있다.")
# ------------------------------------------------------------------ figure captions (English)
FIGCAP = {
    "fig1_architecture": "Fig. 1. (a) Pad pair: recess r, thermo-elastic protrusion u and bulge-out h_{d}; contact if m ≥ 0. "
                         "(b) Evaluation order with criteria fixed in advance.",
    "fig2_transition": "Fig. 2. Elastic contact limit vs pad size: top + bottom protrusion at 400 °C (elastic: FEM, FEM × 0.69, "
                       "imec in-situ; diffusion: saturated model, dashed = extrapolated). The measured pair reaches the 5 nm "
                       "recess sum at ≈ 0.7 µm. Inset: limit vs recess sum.",
    "fig3_diffusion": "Fig. 3. Diffusion term (revision 1) vs imec 2026 bulge-out [@DM26]: (a) median and IQR; (b) size "
                      "dependence, 250 °C, 1 h; open = outside the tolerance. (c) f(ω): four base variants and two "
                      "pessimistic scenarios (*).",
    "fig4_window300": "Fig. 4. 300 nm pads: minimum anneal time for P(contact) ≥ 0.99, (a) clean, (b) oxidised surface. Band: "
                      "tested uncertainty set; circles: its boundary at 5 min, 30 min, 2 h (°C); dashed: worst orientation, "
                      "f(0) > 0; grey: outside data.",
    "fig5_recess_spec": "Fig. 5. Allowable CMP recess per pad, 300 nm, clean surface: probability (P ≥ 0.99) and "
                        "worst-orientation criteria for the six f(ω).",
    "fig6_factors": "Fig. 6. Factor effects on the 300 nm clean boundary: (a) shift of the boundary temperature (30 min, 2 h); "
                    "(b) multiplier of the minimum anneal time at 250 °C. Without surface diffusion no condition closes up "
                    "to 400 °C.",
}

# ------------------------------------------------------------------ tables (English)
T1 = ("Table 1. Datasets and their roles (train/test split fixed in advance).",
      ["Group / process", "Measurement", "Sizes", "Role"],
      [["NYCU [@LIN25,@CHEN25], Cu/SiO_{2}", "in-situ AFM u(T)", "9, 3, 1 µm", "train 9, 3; test 1"],
       ["imec [@DM23,@OKU17], Cu/SiCN", "in-situ SPM u(T), 100–400 °C", "3.06, 1.80, 1.26, 0.54 µm",
        "train 3.06, 1.80; test 1.26, 0.54"],
       ["imec DM2026 [@DM26], Cu/SiCN", "bulge-out distributions, EBSD", "115–300 nm, 200–450 °C, 1–4 h",
        "diffusion: train 1 point, test 17"],
       ["ST/Leti [@AY22,@AYTH], Cu/SiO_{2}", "Laue ε′_{zz}(T)", "0.3, 3 µm", "comparison (sign)"],
       ["imec IRPS 2026 [@VHIRPS]", "recess distribution", "—", "input N(2.5, 0.5^{2}) nm"]],
      [2.25, 2.05, 1.85, 1.75])
T2 = ("Table 2. Elastic-model train/test (array cell, bonded sidewall; u at 400 °C unless noted).",
      ["Case", "Model (nm)", "Meas. (nm)", "Rule", "Result"],
      [["NYCU 9/3 µm, 200 °C (train)", "6.87/4.26", "6.4/4.1", "2σ", "pass"],
       ["imec 1.80 µm (train)", "1.0–5.0", "1.05–5.4", "2σ", "pass"],
       ["imec 3.06 µm, 300/400 °C (train)", "4.64/6.32", "6.05/7.85", "2σ", "fail"],
       ["NYCU 1 µm, 200 °C (test)", "1.79–1.94", "2.1 ± 0.4", "overlap", "pass"],
       ["imec 1.26 µm, 100–400 °C (test)", "0.81–4.04", "0.7–5.0", "0.5 nm/15 %", "pass ≤ 200 °C"],
       ["imec 0.54 µm, 100–400 °C (test)", "0.41–2.04", "0.25–1.4", "0.4 nm", "fail (×0.61–0.69)"],
       ["sliding control, 1/0.54 µm", "3.66/4.84", "2.1/1.4", "must fail", "fails → bonded"]],
      [2.75, 1.25, 1.2, 1.15, 1.6])
T3_ROWS = [
    ["Elastic u, ≥ 1 µm, bonded", "validated", "33a8f5c"],
    ["Elastic contact limit", "0.70 µm (400 °C, 5 nm); 0.55/1.0 µm at 3/8 nm", "boundaries"],
    ["Constraint-factor fit C(h/w)", "validated, ±20 % on 4 unseen geometries", "8194e62"],
    ["Elastic u, 0.54 µm", "not validated (+46 %); liner hypothesis rejected", "2acfd92"],
    ["Crossover h_{d} = u", "prediction only, 0.74–2.45 µm", "boundaries"],
    ["Diffusion term h_{d}", "not validated (2/17, 11/17, DM2023 0/7); ≥ 250 °C PPA-Cu 5/5", "9c6bc29, db29b8e"],
    ["Orientation function f(ω)", "exploratory: 4 base + 2 pessimistic variants; f(0) unobserved", "f_omega_variants"],
    ["Orientation response surface", "validated, 20 held-out directions, max 0.46 %", "13a580f"],
    ["Height sum vs contact FEM", "agrees 4/4 (bonded, elastic contact, no diffusion)", "E25–E28"],
    ["Sidewall condition", "bonded (sliding over-predicts 1.7–3.5×)", "V4"],
    ["300 nm window", "conditional prediction (tested set): ≈ 250 °C (2 h), 285 °C (30 min)", "boundary_curves"],
]
T3 = ("Table 3. Status of each model part (criteria fixed in advance).", ["Part", "Status", "Evidence"], T3_ROWS, [2.45, 4.1, 1.4])

# ------------------------------------------------------------------ references (English, IEIE style)
REFS = {
    "VH26": "S. Van Huylenbroeck et al., \"Wafer-to-wafer hybrid bonding technology with 200nm interconnect pitch,\" in <i>Proc. IEEE ECTC</i>, 2026.",
    "DM23": "J. De Messemaeker et al., \"New Cu 'bulge-out' mechanism supporting sub-micron scaling of hybrid wafer-to-wafer bonding,\" in <i>Proc. IEEE ECTC</i>, pp. 1042–1049, 2023.",
    "DM26": "J. De Messemaeker et al., \"Understanding scaling and temperature limits in Cu bulge-out mechanism for hybrid wafer-to-wafer bonding,\" in <i>Proc. IEEE ECTC</i>, pp. 2158–2162, 2026, doi:10.1109/ECTC51846.2026.00355.",
    "HOOGE24": "J. Hooge, C. Jois, C. Netzband, and I. Son, \"Modeling of copper hybrid bonding anneal,\" in <i>Proc. IEEE 74th Electron. Compon. Technol. Conf. (ECTC)</i>, Denver, CO, USA, May 2024, pp. 1231–1235.",
    "AY22": "B. Ayoub et al., \"In-situ characterization of thermomechanical behavior of copper nano-interconnect for 3D integration,\" <i>Microelectron. Eng.</i>, vol. 261, 111809, 2022.",
    "LIN25": "H.-E. Lin et al., \"Revealing challenges of downscaling effects on Cu thermal expansion in advanced hybrid bonding using in-situ AFM,\" <i>Appl. Surf. Sci.</i>, vol. 689, 162539, 2025.",
    "CHEN25": "P.-L. Chen and C. Chen, \"Effect of dimension on thermal expansion of Cu pads in SiO_{2} vias for 3D IC fine-pitch hybrid bonding,\" in <i>Proc. IEEE 75th Electron. Compon. Technol. Conf. (ECTC)</i>, Dallas, TX, USA, May 2025, doi:10.1109/ECTC51687.2025.00329.",
    "DM24": "J. De Messemaeker et al., \"Simulation of bulge-out mechanism enabling sub-0.5 µm scaling of hybrid wafer-to-wafer bonding,\" in <i>Proc. IEEE ECTC</i>, 2024.",
    "TSAU22": "Y. W. Tsau et al., \"Simulation of Cu pad expansion in wafer-to-wafer Cu/SiCN hybrid bonding,\" <i>Microelectron. Reliab.</i>, vol. 138, Art. no. 114716, 2022, doi:10.1016/j.microrel.2022.114716.",
    "BUT73": "D. B. Butrymowicz, J. R. Manning, and M. E. Read, \"Diffusion in copper and copper alloys, Part I,\" <i>J. Phys. Chem. Ref. Data</i>, vol. 2, pp. 643–655, 1973.",
    "VHIRPS": "S. Van Huylenbroeck et al., \"Wafer to wafer hybrid bonding pitch scaling challenges (Invited),\" in <i>Proc. IEEE Int. Reliab. Phys. Symp. (IRPS)</i>, Tucson, AZ, USA, Mar. 2026, doi:10.1109/IRPS61424.2026.11499286.",
    "OKU17": "O. O. Okudur et al., \"Thermomechanical aspects of wafer-to-wafer copper-dielectric hybrid bonding for 3D integrated circuits,\" in <i>Int. Conf. Wafer Bonding</i>, Leuven, 2017.",
    "ASME": "ASME V&V 10-2019, <i>Standard for Verification and Validation in Computational Solid Mechanics</i>, ASME, 2019.",
    "AYTH": "B. Ayoub, <i>Electrical and morphological characterizations of the hybrid bonding level down to submicron pitches</i>, PhD thesis, Univ. Bordeaux, 2023.",
    "OKORO": "C. Okoro et al., \"Extraction of the appropriate material property for realistic modeling of through-silicon-vias using µ-Raman spectroscopy,\" in <i>Proc. IEEE Int. Interconnect Technol. Conf. (IITC)</i>, San Francisco, CA, USA, Jun. 2008, pp. 16–18.",
}

# ------------------------------------------------------------------ blind (written review, 4 pages): compressed body
BL_INTRO = [
    "웨이퍼 간 Cu/SiCN 하이브리드 본딩은 200 nm 피치까지 수율이 보고되었다[@VH26]. 패드가 작아지면 열탄성 돌출 u는 "
    "1 nm 수준으로 줄고 접촉은 표면확산 bulge-out h_{d}가 만든다[@DM23,@DM26]. 접촉 여유 m = u_{t} + u_{b} + h_{d,t} + "
    "h_{d,b} − (r_{t} + r_{b})(r: CMP recess)에서 탄성 접촉 한계(u_{t} + u_{b} = r_{t} + r_{b})와 기여도 역전"
    "(h_{d} = u)을 구분한다. 선행연구는 방위별 탄성[@AY22], 1–9 µm 돌출[@LIN25,@CHEN25], bulge-out 분포와 방위"
    "[@DM23,@DM26,@DM24], 열팽창–표면확산 결합 어닐 모델[@HOOGE24]로 나뉘어 있고, 실측으로 학습·테스트한 모델에서 "
    "가정에 따라 접촉 판정이 유지되는지 갈리는지를 정량화한 연구는 없다.",
    "본 연구는 Cu 측벽이 라이너에 접합된 공정에서 접촉 결정 요인을 구분하고, 공정 변수와 패드별 무작위 요인"
    "(recess 산포, 결정방위)이 공정창을 얼마나 움직이는지 모델 불확실성과 함께 제시한다. 학습·테스트 데이터 분할과 "
    "합격 기준은 계산 전에 고정하였고(기록은 채택 후 공개), 테스트 데이터는 한 번만 평가하였다.",
]
BL_S2a = ("ANSYS MAPDL로 Cu 패드·라이너·유전체·Si를 모델링했다(작은 패드 3D 이방성, 큰 패드 2D Hill 등방). 측벽은 "
          "밀착 계면이므로 접합으로 두고, 미끄럼 극한을 대조군으로 두어 실측으로 판별한다. 유전체 E·α만 공정당 한 번 큰 "
          "패드에서 학습한다. 표면확산 항은 DM2024[@DM24]의 선형화를 따른다.")
BL_S2b = ("s_{ox}는 산화 배율(청정 1, 산화 0.45[@DM23]), D_{s}(T)는 Q = 20.7 kcal/mol[@BUT73]의 아레니우스 의존, f(ω)는 "
          "최근접 <111>과의 각 ω의 방위 함수로, 300 nm 분포의 q10–q90에 맞춘 기본 4종과 다른 시료의 꼬리를 반영한 비관 "
          "시나리오 2종을 쓴다(Fig. 2c). 탄성은 큰 패드(NYCU 9·3 µm, imec "
          "1.80·3.06 µm)로 학습해 imec 1.26·0.54 µm, NYCU 1 µm, 미끄럼 대조군으로, 확산 항은 imec 2026 한 점에서 진폭만 "
          "학습해 17점과 미사용 DM2023 7점으로 테스트했다(ASME V&V 10 순서).")
BL_S31 = ("NYCU 1 µm, imec 1.80 µm, 1.26 µm 100–200 °C가 통과했고, 미끄럼 대조군은 1.7–3.5배 과대예측해 측벽은 접합으로 "
          "판별되었다(Table 1). imec 0.54 µm는 전 온도에서 측정/모델 0.61–0.69다(온도 무관). 구속 계수 C = u/[(α_{Cu} − "
          "α_{Si})ΔT·h]는 종횡비의 한 함수로 모이고, 이 근사식은 미사용 형상 4개에서 ±20 % 안에 들었다. recess 합 5 nm"
          "[@VHIRPS]를 400 °C 탄성 돌출 합이 넘는 최소 폭(탄성 접촉 한계)은 실측 기준 0.70 µm, 근사식 0.76 µm이며"
          "(Fig. 1), recess 합 3/8 nm → 0.55/1.0 µm, 350/300/250 °C → 0.90/1.14/1.62 µm다. 기여도 역전 폭(0.74–2.45 µm)은 "
          "외삽 예측이다.")
BL_S32 = ("원래 형태는 DM2026 17점 중 2점, 진폭을 학습한 개정 1은 11점을 통과해 검증 통과가 아니다. 실패는 200 °C·"
          "D ≥ 250 nm와 자가 어닐 Cu의 과소예측이고, ≥ 250 °C에서는 PPA-Cu 5/5, 전체 8/9가 허용오차 안이다(Fig. 2a·b). "
          "미사용 DM2023(불균등 패드)은 0/7이어서 적용 범위는 등크기·≥ 250 °C다. τ_{0}는 포화된 학습점에서 식별되지 않아 "
          "\"350 °C 5분 안에 완료\"[@DM23]와 일관된 20–100 s로 둔다. f(ω) 6종은 중앙값 11–12/17, IQR 13/17을 주지만 "
          "하위 분위수 오차는 기본형 V3 0.49 nm, 비관형 V6 5.78 nm로 달라 후자는 시나리오로만 쓴다. 정확히 <111>인 "
          "패드의 bulge-out f(0)은 관측되지 않았다.")
BL_S33a = ("300 nm 탄성 항은 77방향 3D 해석의 다항 회귀 응답표면으로 방위를 유지했고(최대 오차 0.46 %, 방위 폭 5 %), "
           "상·하 방위와 recess(패드당 N(2.5, 0.5^{2}) nm[@VHIRPS])를 확률 변수로, 시험한 불확실성 집합(f(ω) 6종 × b × "
           "τ_{0} × Q)의 모든 조합에서 "
           "P(m ≥ 0)를 계산했다. 200–400 °C를 5 °C 간격으로 계산한 P ≥ 0.99 경계(Fig. 3)에서 탄성만으로 닫히는 조건은 "
           "없고, 청정 표면 주 설정은 30분 253 °C·2시간 220 °C, 모든 조합 유지는 5분 342 °C, 30분 285 °C, 2시간 약 "
           "250 °C(보간 248 °C) 이상이다(250 °C 미만은 데이터 밖). 산화 표면은 30분 334 °C, 2시간 295 °C다. 이는 명시한 "
           "불확실성 집합 안의 조건부 예측이다.")
BL_S33b = ("요인별 경계 이동(2시간/30분, Fig. 4a)은 τ_{0} 36/40 °C, 라이너 35/39 °C, 산화 25/28 °C, 활성화에너지 49/39 °C, "
           "꼬리 모양 15/16 °C, recess 평균 10/12 °C, 방위 꼬리 10/10 °C, recess 산포 4/4 °C, b 3/4 °C이고, 확산이 없으면 "
           "400 °C까지 닫히지 않는다. 시간 배수(Fig. 4b)는 온도와 거의 무관하며(τ_{0} ×5.0, 라이너 ×4.5), 30분 이동이 큰 "
           "것은 아레니우스 환산 때문이다. 최악 방위는 f(0)이 정한다: f(0) = 0이면 최악 쌍은 닫히지 않고(허용 recess "
           "0.5–0.9 nm/패드), f(0) > 0이면 2시간 265–290 °C, 30분 304–324 °C 이상에서 닫힌다(2.4–4.2 nm/패드; 확률 기준 "
           "3.5–9 nm). 확산을 넣지 않은 탄성 접촉 FEM의 재분석에서, 시험한 접합 측벽 조건의 높이합 판정과 중심 공극 닫힘 "
           "판정은 4/4 일치했다.")
BL_S41 = ("기여는 ① recess 조건부 탄성 접촉 한계와 미사용 형상으로 검증한 구속 계수 근사식, ② 측벽 접합 공정의 요인 "
          "순위(지배 기구 ≫ 열예산·표면·라이너 > recess·방위)와 판정의 안정성이다. 방위의 탄성 효과는 5 %로 작아 꼬리는 "
          "확산 쪽(<111>)에서 생긴다[@AY22]. 결합 어닐 모델[@HOOGE24]과 달리 불확실성 조합별 판정의 안정성과 최악 방위 기준을 "
          "구분했고, 최악 방위의 접촉을 확정하려면 정확히 <111>인 패드의 bulge-out 측정이 필요함을 특정했다.")
BL_S42 = ("한계: 0.54 µm 오차 원인 미상, 300 nm 돌출 실측 없음(예측), 확산 항 미검증(등크기·≥ 250 °C), f(0) 미관측, "
          "Ayoub 300 nm 변형률[@AY22]은 크기는 맞으나 부호 반대(원인은 열린 문제). 결론: 접합 측벽의 300 nm 패드에서는 "
          "탄성보다 확산 모델이 접촉 판정을 좌우하며, 청정 표면 약 250 °C·2 h, 300 °C·30 min 이상은 시험한 불확실성 "
          "집합에서 접촉 확률 0.99 이상이 유지되는 조건부 예측이다.")
BL_CAP = {
    "fig2_transition": FIGCAP["fig2_transition"].replace("Fig. 2.", "Fig. 1."),
    "fig3_diffusion": FIGCAP["fig3_diffusion"].replace("Fig. 3.", "Fig. 2."),
    "fig4_window300": FIGCAP["fig4_window300"].replace("Fig. 4.", "Fig. 3."),
    "fig6_factors": FIGCAP["fig6_factors"].replace("Fig. 6.", "Fig. 4."),
}
BL_T1 = (T2[0].replace("Table 2.", "Table 1."),) + T2[1:]
BL_T2 = ("Table 2. Status of each model part (criteria fixed in advance).",
         ["Part", "Status"],
         [[r[0], r[1]] for r in T3_ROWS if not r[0].startswith(("Crossover", "Height sum"))],
         [2.7, 5.25])
