# -*- coding: utf-8 -*-
r"""
Text of the IEIE 2026 fall submissions, v6 structure (2026-10-16, user direction):
  II = method in full (contact condition, FEM, diffusion term, probability/process-condition procedure, validation);
  III = dry listing of results (tables carry the numbers); IV = interpretation, contribution, limits, conclusion.
Scope: Cu sidewall bonded to the liner (v5). No 'pre-registration' wording (v5.1), no cell counts (v4.4),
tested-uncertainty-set wording and narrowed contact-FEM claim (reviewer notes 2026-10-16), Hooge 2024 added.
Numbers: docs/paper/ieie2026f_plan_and_draft_ko.md (v5.1), results/stage2/v2/boundary_curves.json,
results/stage2/v2/f_omega_variants.json, results/stage2/diffusion_validation_rev1.csv, boundaries.json.

Markup: _{..} sub, ^{..} sup, <i>..</i> italic, [@KEY] citation (numbered by first use per document),
[[FIG:key]] -> "(Fig. n)" or removed if the figure is not in that version, [[FIGN:key]] -> "Fig. n",
[[TAB:key]] -> "Table n". Paragraph tags: "P" both versions, "PP" proceedings only, "PB" blind only.
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
    "literature properties with an analytic surface-diffusion term. The train/test split and the acceptance criteria "
    "were fixed before computation, and the test data were used once. For a sidewall bonded to the liner, the "
    "elastic contact limit, at which the top + bottom elastic protrusion equals a 5 nm recess sum, is about 0.7 µm at "
    "400 °C. Over the tested set of model uncertainties and with pad-to-pad recess and orientation scatter, 300 nm "
    "pads are predicted to keep a contact probability of at least 0.99 on a clean surface at about 250 °C for 2 h and "
    "at 300 °C for 30 min or longer. The worst-orientation conclusion depends on the unmeasured bulge-out of pads "
    "oriented exactly along <111>.")
ABSTRACT_KO = (
    "Cu 하이브리드 본딩 패드가 1 µm 아래로 작아지면 열탄성 돌출만으로는 CMP recess를 닫지 못한다. 문헌 물성 "
    "열탄성 FEM과 표면확산 해석식을 결합하고, 학습·테스트 데이터 분할과 합격 기준을 계산 전에 고정해 세 연구그룹의 "
    "실측으로 시험하였다. 측벽이 접합된 조건에서 탄성 접촉 한계는 400 °C, recess 합 5 nm에서 약 0.7 µm이다. "
    "300 nm 패드는 시험한 불확실성 집합과 패드별 산포에서 청정 표면 약 250 °C·2 h, 300 °C·30 min 이상이면 접촉 "
    "확률 0.99 이상을 유지하는 것으로 예측된다.")
ABSTRACT_EN_B = (
    "Below 1 µm, thermo-elastic protrusion of Cu hybrid-bonding pads no longer closes the CMP recess. We couple a "
    "thermo-elastic FEM with an analytic surface-diffusion term, fixing the train/test split and acceptance criteria "
    "before computation. For a sidewall bonded to the liner, the elastic contact limit is about 0.7 µm at 400 °C for a "
    "5 nm recess sum. Over the tested uncertainty set, 300 nm pads keep a contact probability of at least 0.99 on a "
    "clean surface at about 250 °C for 2 h and 300 °C for 30 min or longer; the worst case depends on the unmeasured "
    "bulge-out of exactly <111>-oriented pads.")
KEYWORDS = "Hybrid bonding, Cu bulge-out, surface diffusion, thermo-elastic FEM, process window"

# ------------------------------------------------------------------ body (shared, tagged)
# ("H1", title) chapter; ("H2", title) section; ("P"/"PP"/"PB", text); ("EQ", lines); ("PC", text after equation)
# ("FIG", key) / ("TAB", key) placed where they belong; builders skip floats a version does not carry.
BODY = [
    ("H1", "서론"),
    ("P", "웨이퍼 간 Cu/SiCN 하이브리드 본딩은 200 nm 피치까지 전기적 수율이 보고되었다[@VH26]. 패드가 작아지면 어닐 "
          "중 Cu의 열탄성 돌출은 1 nm 수준으로 줄어 CMP recess를 닫지 못하고, 상·하 패드의 접촉은 표면확산에 의한 "
          "bulge-out이 만든다[@DM23,@DM26]. 선행연구는 300 nm 패드의 Laue 변형률[@AY22], 1–9 µm 패드의 in-situ "
          "돌출[@LIN25,@CHEN25], 수천 개 패드의 bulge-out 분포와 결정방위[@DM23,@DM26,@DM24], {{P:Cu/SiCN 패드 팽창 "
          "해석[@TSAU22], }}열팽창과 표면확산을 결합한 어닐 모델[@HOOGE24]로 나뉘어 있다. 그러나 이 관측들로 한 모델을 "
          "학습·테스트하고, 모델 가정이 바뀔 때 접촉 판정이 유지되는지를 패드별 산포와 함께 정량화한 연구는 없다."),
    ("P", "본 연구는 Cu 측벽이 라이너에 접합된 공정에서 300 nm 패드의 접촉을 결정하는 요인을 구분하고, 어닐 온도·시간, "
          "표면 상태, 라이너 같은 공정 변수와 recess 산포, 결정방위 같은 패드별 무작위 요인이 접촉 가능한 어닐 조건을 "
          "얼마나 움직이는지 제시한다. 이를 위해 문헌 물성 열탄성 FEM과 표면확산 해석식을 결합한 모델을 세 연구그룹의 "
          "실측으로 학습·테스트하고, 그 모델로 접촉 가능한 어닐 조건과 요인별 영향을 계산했다."),

    ("H1", "연구 방법"),
    # ---------------- proceedings: full method
    ("H2P", "접촉 조건"),
    ("PP", "상·하 패드의 접촉 여유 m을 식 [[EQ:m]]로 정의한다[[FIG:schem]]."),
    ("EQP", ("m", "m = u_{t} + u_{b} + h_{d,t} + h_{d,b} − (r_{t} + r_{b})")),
    ("PCP", "r은 CMP recess, u는 Cu와 유전체·Si의 열팽창 차이에 의한 열탄성 돌출, h_{d}는 표면에너지를 줄이려는 Cu "
            "원자의 이동이 만드는 bulge-out이다. u는 냉각 시 되돌아가고 h_{d}는 남는다. 위·아래 탄성 돌출의 합이 recess "
            "합과 같아지는 패드 폭을 탄성 접촉 한계, 확산 돌출이 탄성 돌출과 같아지는 폭을 기여도 역전이라 한다. 네 양은 "
            "서로 다른 기준면을 가지므로 섞어 쓰지 않는다."),
    ("H2P", "열탄성 FEM"),
    ("PP", "ANSYS MAPDL로 Cu 패드, Ta/TaN 라이너, 유전체, Si 기판을 배열 단위 셀로 모델링했다. 큰 다결정 패드는 2D 축대칭 "
           "Hill 등방 Cu로, 300 nm 단결정 패드는 입방 탄성텐서를 결정 방향으로 회전한 3D 이방성 Cu로 계산했다. Cu 측벽은 "
           "라이너와 밀착된 계면이므로 접합으로 두고, 측벽 전단이 전달되지 않는 미끄럼 극한을 대조군으로 함께 계산해 "
           "실측으로 판별했다. 물성, 경계조건, 메시 규칙은 모든 시료에 같고, 유전체의 E와 α만 공정마다 한 번 큰 패드에서 "
           "학습했다. 300 nm 패드의 방위 의존성은 77방향의 3D 해석(학습 45, 검증 20, 면내 회전 12)으로 만든 2차 다항 회귀 "
           "응답표면으로 나타냈다. 패드 크기에 따른 탄성 돌출은 구속 계수 C를 식 [[EQ:c]]로 정의하고, 종횡비 h/w에 대한 "
           "근사식 [[EQ:cfit]]로 정리했다."),
    ("EQP", ("c", "C = u / [(α_{Cu} − α_{Si})·ΔT·h]")),
    ("EQP", ("cfit", "C = c_{0} / [1 + a·(E_{d}/E_{Cu})·(h/w)^{1.5}]")),
    ("FIGP", "schem"),
    ("H2P", "표면확산 항"),
    ("PP", "표면확산 돌출은 DM2024[@DM24]의 선형화를 따라 식 [[EQ:hd]], [[EQ:tau]]로 둔다."),
    ("EQP", ("hd", "h_{d} = s_{ox}·0.0022(θ_{eff} − 90°)D·f(ω)[1 − e^{−t/τ}]")),
    ("EQP", ("tau", "τ = τ_{0}·(D/200 nm)^{3.7}·D_{s}(350 °C)/D_{s}(T)")),
    ("PCP", "D는 패드 지름, s_{ox}는 표면 산화 배율로 청정 표면 1, 산화 표면 0.45[@DM23]이며, D_{s}(T)는 활성화에너지 "
            "Q = 20.7 kcal/mol[@BUT73]의 아레니우스 의존을 따른다. 진폭 θ_{eff}는 imec 2026 데이터의 한 점에서 학습했다. "
            "τ_{0}는 포화된 학습점에서 식별되지 않으므로 350 °C에서 5분 안에 완료된다는 관찰[@DM23]과 일관된 20–100 s를 "
            "범위로 둔다. f(ω)는 패드 법선과 최근접 <111> 사이 각 ω의 방위 함수다. 300 nm 분포의 q10–q90과 6.5 nm 이하 "
            "분율에 맞춘 기본 4종과, 다른 시료에서 관찰된 약 10 % 꼬리를 반영한 비관 시나리오 2종을 함께 쓴다[[FIG:diff]]."),
    ("H2P", "접촉 확률과 공정 조건"),
    ("PP", "상·하 패드의 방위는 구면 균일, recess는 패드당 N(2.5, 0.5^{2}) nm[@VHIRPS]로 두고 Monte Carlo로 P(m ≥ 0)를 "
           "계산한다. 불확실성 집합은 f(ω) 6종, 탄성 계수 b ∈ {0.60, 0.69, 0.93, 1.0}, τ_{0} ∈ {20, 60, 100 s}, "
           "Q ∈ {20.7, 13.4 kcal/mol}의 모든 조합이다. 200–400 °C를 5 °C 간격, 1분–4시간을 로그 간격 40점으로 계산해 "
           "P ≥ 0.99를 만족하는 최소 어닐 시간의 경계를 구하고, 방위 분포 가정을 뺀 최악 방위 여유 m_{min}도 함께 "
           "계산한다. 요인의 영향은 한 요인만 바꿨을 때 경계 온도가 움직인 양과 최소 어닐 시간의 배수로 나타낸다."),
    ("H2P", "검증 절차"),
    ("PP", "ASME V&V 10[@ASME]의 순서에 따라 수치 검증, 학습, 테스트, 예측을 차례로 수행했고, 데이터별 역할은 "
           "[[TAB:data]]과 같다. 탄성 모델은 큰 패드로 학습한 뒤 작은 패드와 미끄럼 대조군으로, 확산 항은 DM2026 17점과 "
           "학습에 쓰지 않은 DM2023 7점으로 테스트했다. 학습·테스트 데이터 분할과 합격 기준은 계산 전에 고정하였고, "
           "테스트 데이터는 한 번만 평가하였다. 테스트 실패 뒤 모델 수정은 한 번으로 제한하고 같은 기준으로 다시 "
           "판정했다."),
    # ---------------- blind: condensed method
    ("H2B", "접촉 조건과 모델"),
    ("PB", "상·하 패드의 접촉 여유 m을 식 [[EQ:m]]로 정의한다[[FIG:schem]]. r은 CMP recess, u는 열탄성 돌출, h_{d}는 "
           "표면확산 bulge-out이며, 위·아래 탄성 돌출의 합이 recess 합과 같아지는 패드 폭을 탄성 접촉 한계라 한다."),
    ("EQB", ("m", "m = u_{t} + u_{b} + h_{d,t} + h_{d,b} − (r_{t} + r_{b})")),
    ("PB", "u는 ANSYS MAPDL 배열 단위 셀로 계산했다. 300 nm 패드는 3D 이방성 Cu, 큰 패드는 2D 등방 Cu이고, Cu 측벽은 "
           "라이너에 접합된 것으로 두되 미끄럼 극한을 대조군으로 계산해 실측으로 판별했다. 300 nm 패드의 방위 의존성은 "
           "77방향 해석의 다항 회귀 응답표면으로 나타냈다. h_{d}는 DM2024[@DM24]의 선형화를 따라 식 [[EQ:hd]], [[EQ:tau]]로 "
           "둔다."),
    ("EQB", ("hd", "h_{d} = s_{ox}·0.0022(θ_{eff} − 90°)D·f(ω)[1 − e^{−t/τ}]")),
    ("EQB", ("tau", "τ = τ_{0}·(D/200 nm)^{3.7}·D_{s}(350 °C)/D_{s}(T)")),
    ("PCB", "s_{ox}는 표면 산화 배율, D_{s}(T)는 Q = 20.7 kcal/mol의 아레니우스 의존이며, f(ω)는 최근접 <111>과의 "
            "각 ω에 따른 방위 함수로 실측 분포에 맞춘 기본 4종과 비관 시나리오 2종을 쓴다."),
    ("FIGB", "schem"),
    ("H2B", "공정 조건 계산과 검증"),
    ("PB", "패드별 방위와 recess[@VHIRPS]를 확률 변수로 두고 Monte Carlo로 접촉 확률 P(m ≥ 0)를 계산한다. f(ω), 탄성 계수 b, "
           "τ_{0}, Q의 모든 조합을 불확실성 집합으로 두고, 200–400 °C에서 P ≥ 0.99를 만족하는 최소 어닐 시간의 경계를 "
           "구한다. 방위 분포 가정을 뺀 최악 방위 기준도 함께 계산하고, 요인의 영향은 한 요인만 바꿨을 때 경계 온도의 "
           "이동과 최소 어닐 시간의 배수로 나타낸다. 탄성 모델은 큰 패드로 학습해 작은 패드로, 확산 항은 imec 2026의 한 점으로 학습해 나머지 17점과 DM2023 "
           "7점으로 테스트했다([[TAB:data]]). 학습·테스트 데이터 분할과 합격 기준은 계산 전에 고정하였고, 테스트 데이터는 "
           "한 번만 평가하였다."),
    ("TAB", "data"),

    ("H1", "결과"),
    ("H2", "탄성 모델과 탄성 접촉 한계"),
    ("P", "[[TAB:res]]는 테스트 결과다. 접합 측벽 조건의 테스트에서 NYCU 1 µm는 실측과 일치했고, imec 1.26 µm는 "
          "200 °C 이하에서만 맞았으며, 0.54 µm는 온도와 무관하게 과대예측했다. {{P:미끄럼 대조군은 실측을 1.7–3.5배 넘게 예측해, 두 공정의 측벽은 접합으로 판별되었다. }}이 "
          "위·아래 탄성 돌출이 recess 합 5 nm를 닫는 최소 폭은 400 °C의 실측 기준 0.70 µm이며, 구속 계수 근사식으로 보면 "
          "온도가 낮아질수록 넓어져 250 °C에서 1.62 µm가 된다[[FIG:limit]]. {{P: 300 nm 패드의 탄성 돌출은 패드당 약 1 nm에 그친다.}}"),
    ("PP", "같은 비교에서 확산 돌출이 탄성 돌출을 넘는 폭은 어닐 조건에 따라 0.74–2.45 µm로 예측되지만, 300 nm 밖의 외삽이다."),
    ("TAB", "res"),
    ("FIG", "limit"),
    ("H2", "표면확산 항"),
    ("P", "확산 항은 미리 고정한 기준을 통과하지 못했다. 다만 실패는 200 °C의 큰 패드와 자가 어닐 Cu에 몰려 있고, 250 °C "
          "이상의 PPA-Cu는 모두 허용오차 안에 들었다[[FIG:diff]].{{P: 불균등 패드인 DM2023에는 맞지 않았다.}} 이에 따라 이후 공정 "
          "조건은 등크기 패드와 250 °C 이상에서만 해석한다."),
    ("PP", "f(ω) 비관 시나리오는 중앙값과 IQR 판정은 같지만 하위 분위수를 기본형보다 크게 벗어나, 불확실성 평가에만 쓴다."),
    ("FIG", "diff"),
    ("H2", "300 nm 공정 조건"),
    ("P", "[[FIGN:win]]는 접촉 확률 0.99를 만족하는 최소 어닐 시간을 온도에 대해 나타낸다. 곡선 위쪽이 접촉 영역이고, 띠는 "
          "불확실성 집합 전체의 범위다. 탄성만으로 닫히는 조건은 없었다. 띠의 위쪽 끝, 즉 모든 조합에서 접촉하는 경계는 청정 "
          "표면에서 2시간 약 250 °C, 30분 285 °C이며, 표면이 산화되면 약 40–50 °C 높아진다. 방위 분포 가정을 뺀 최악 방위 "
          "경계(점선)는 <111> 패드가 조금이라도 솟는 f(0) > 0 시나리오에서만 생긴다."),
    ("PP", "같은 조건에서 허용되는 recess는 확률 기준이 최악 방위 기준보다 수 배 크다[[FIG:rec]]."),
    ("FIG", "win"),
    ("FIG", "rec"),
    ("H2", "요인별 영향"),
    ("P", "[[FIGN:fac]]a는 한 요인만 바꿨을 때 경계 온도의 이동을, [[FIGN:fac]]b는 같은 변화를 최소 어닐 시간의 배수로 "
          "나타낸다. 확산 동역학(Q, τ_{0}), 라이너 접촉각, 표면 산화가 25–49 °C로 가장 크고, recess와 방위 같은 패드별 요인은 "
          "4–16 °C다. 확산 항을 빼면 400 °C까지 어떤 조건도 닫히지 않는다.{{P: 확산을 넣지 않은 접촉 FEM[@OKORO]에서는 "
          "높이합 판정과 중심 공극의 닫힘이 4/4 일치했다.}}"),
    ("FIG", "fac"),

    ("H1", "결론 및 의의"),
    ("P", "결과는 300 nm 접합 패드의 접촉이 탄성이 아니라 확산 항으로 정해진다는 것을 보여 준다. 탄성 접촉 한계가 약 0.7 µm"
          "이므로, 그보다 작은 패드에서 탄성 돌출은 recess를 보정하는 정도에 머문다. 선행연구가 정성적으로 보고한 sub-µm 접촉 "
          "문제[@DM23,@VHIRPS]를 실측으로 학습·테스트한 모델에서 recess와 온도에 따른 규칙으로 정량화한 것이 첫째 기여다."),
    ("P", "공정 조건은 열예산을 정하는 확산 동역학, 라이너, 표면 상태가 주로 정하고, 패드별 무작위 요인은 수율의 하위 꼬리에 "
          "작용한다. 요인의 효과는 시간 배수로는 거의 일정한데, 30분 경계가 2시간보다 많이 움직이는 것은 고온일수록 1 °C당 "
          "확산 속도 증가가 작아지는 아레니우스 관계 때문이다.{{P: 활성화에너지만은 기준 데이터에서 멀어질수록 영향이 커지므로 "
          "250 °C 아래 조건은 주장하지 않는다.}} 방위의 탄성 효과는 5 %로 작아, 방위 차이로 recess 사양을 정한 Ayoub[@AY22]과 "
          "달리 방위는 <111> 근방의 확산 꼬리를 통해 작용한다. 열팽창과 표면확산을 결합한 어닐 모델[@HOOGE24]에 더해, 시험한 "
          "불확실성 조합에서 판정이 유지되는 조건과 갈리는 조건, 그리고 최악 방위 기준을 구분한 것이 둘째 기여다."),
    ("PP", "모델 부분별 상태는 [[TAB:status]]과 같다."),
    ("TAB", "status"),
    ("P", "한계는 다음과 같다. 0.54 µm 탄성 오차의 원인은 원 데이터{{P:[@OKU17]}}가 없어 알 수 없고, 300 nm 돌출 실측이 없어 "
          "300 nm 결과는 예측이다. 확산 항의 적용 범위는 등크기 패드와 250 °C 이상이다. Ayoub 300 nm 변형률"
          "{{P:[@AY22,@AYTH]}}{{B:[@AY22]}}은 크기는 맞으나 부호가 반대이며 원인은 열린 문제다. 공정 조건은 명시한 불확실성 "
          "집합 안의 조건부 예측이며, 상·하 방위의 독립성과 확산식 형태까지 검증한 것은 아니다."),
    ("PP", "후속 연구로는 결정립 방위별 bulge-out 문헌 데이터로 f(ω) 시나리오를 줄이는 일과, 250 °C 이하 어닐 시간별 "
           "돌출 데이터로 Q의 영향을 줄이는 일이 있다. 정확히 <111>인 패드의 bulge-out과 300 nm 돌출은 측정이 필요하다."),
    ("P", "따라서 300 nm 접합 패드의 어닐 조건은 탄성 돌출이 아니라 확산 동역학과 표면·라이너 상태를 기준으로 정해야 "
          "하며, 청정 표면 약 250 °C·2시간 또는 300 °C·30분 이상이 시험한 불확실성 집합에서 접촉 확률 0.99 이상을 유지하는 "
          "조건이다. 최악 방위까지 보증하려면 정확히 <111>인 패드의 bulge-out을 측정하는 것이 다음 단계다."),
]

# figures carried by each version (order of appearance defines numbering)
FIGS_P = ["schem", "limit", "diff", "win", "rec", "fac"]
FIGS_B = ["schem", "win", "fac"]
FIGFILE = {"schem": "fig1_architecture", "limit": "fig2_transition", "diff": "fig3_diffusion",
           "win": "fig4_window300", "rec": "fig5_recess_spec", "fac": "fig6_factors"}
TABS_P = ["data", "res", "status"]
TABS_B = ["data", "res"]

FIGCAP = {
    "schem": "(a) Pad pair: recess r, thermo-elastic protrusion u and bulge-out h_{d}; contact if m ≥ 0. "
             "(b) Evaluation order with criteria fixed in advance.",
    "limit": "Elastic contact limit vs pad size: top + bottom protrusion at 400 °C (elastic: FEM, FEM × 0.69, imec "
             "in-situ; diffusion: saturated model, dashed = extrapolated). The measured pair reaches the 5 nm recess "
             "sum at ≈ 0.7 µm. Inset: limit vs recess sum.",
    "diff": "Diffusion term (revision 1) vs imec 2026 bulge-out [@DM26]: (a) median and IQR; (b) size dependence, "
            "250 °C, 1 h; open = outside the tolerance. (c) f(ω): four base variants and two pessimistic scenarios (*).",
    "win": "300 nm pads: minimum anneal time for P(contact) ≥ 0.99, (a) clean, (b) oxidised surface. Band: tested "
           "uncertainty set; circles: its boundary at 5 min, 30 min, 2 h (°C); dashed: worst orientation, f(0) > 0; "
           "grey: outside data.",
    "rec": "Allowable CMP recess per pad, 300 nm, clean surface: probability (P ≥ 0.99) and worst-orientation criteria "
           "for the six f(ω).",
    "fac": "Factor effects on the 300 nm clean boundary: (a) shift of the boundary temperature (30 min, 2 h); "
           "(b) multiplier of the minimum anneal time at 250 °C. Without surface diffusion no condition closes up to "
           "400 °C.",
}

TABLES = {
    "data": ("Datasets and their roles.",
             ["Group / process", "Measurement", "Sizes", "Role"],
             [["NYCU [@LIN25,@CHEN25], Cu/SiO_{2}", "in-situ AFM u(T)", "9, 3, 1 µm", "train 9, 3; test 1"],
              ["imec {{P:[@DM23,@OKU17]}}{{B:[@DM23]}}, Cu/SiCN", "in-situ SPM u(T)", "3.06, 1.80, 1.26, 0.54 µm",
               "train 3.06, 1.80; test 1.26, 0.54"],
              ["imec DM2026 [@DM26], Cu/SiCN", "bulge-out distributions", "115–300 nm, 200–450 °C",
               "train 1 point; test 17"],
              ["imec DM2023 [@DM23]", "bulge-out, unequal pads", "—", "test 7"],
              ["ST/Leti [@AY22], Cu/SiO_{2}", "Laue ε′_{zz}(T)", "0.3, 3 µm", "comparison"],
              ["imec IRPS 2026 [@VHIRPS]", "recess distribution", "—", "input"]],
             [2.25, 2.0, 1.95, 1.75]),
    "res": ("Test results.",
            ["Item", "Result"],
            [["Elastic test: NYCU 1 µm; imec 1.26 µm at 100–200 °C", "pass"],
             ["Elastic test: imec 1.26 µm at 300–400 °C; imec 0.54 µm", "fail; 0.54 µm meas./model 0.61–0.69"],
             ["Sliding sidewall control, 1 / 0.54 µm", "over-predicts 1.7× / 3.5× → bonded"],
             ["Constraint-factor fit C(h/w), 4 unseen geometries", "within ±20 %"],
             ["Elastic contact limit at 400 °C, recess sum 3 / 5 / 8 nm", "0.55 / 0.70 / 1.0 µm"],
             ["Diffusion, DM2026 17 points: original / revision 1", "2/17 / 11/17; ≥ 250 °C PPA-Cu 5/5"],
             ["Diffusion, DM2023 7 points", "0/7"],
             ["Orientation response surface, 20 held-out directions", "max. error 0.46 %"],
             ["Height sum vs contact FEM without diffusion, bonded", "4/4 agree"]],
            [4.6, 3.35]),
    "status": ("Status of each model part.",
               ["Part", "Status"],
               [["Elastic u, ≥ 1 µm, bonded sidewall", "validated"],
                ["Elastic u, 0.54 µm", "not validated (+46 %); liner hypothesis rejected"],
                ["Constraint-factor fit C(h/w)", "validated on 4 unseen geometries"],
                ["Elastic contact limit", "from measured data, 400 °C"],
                ["Contribution crossover h_{d} = u", "prediction only, 0.74–2.45 µm"],
                ["Diffusion term h_{d}", "not validated; scope equal pads, ≥ 250 °C"],
                ["Orientation function f(ω)", "exploratory: 4 base + 2 pessimistic; f(0) unobserved"],
                ["Orientation response surface, 300 nm", "validated on 20 held-out directions"],
                ["300 nm process conditions", "conditional prediction over the tested set"]],
               [3.3, 4.65]),
}

REFS = {
    "VH26": "S. Van Huylenbroeck et al., \"Wafer-to-wafer hybrid bonding technology with 200nm interconnect pitch,\" in <i>Proc. IEEE ECTC</i>, 2026.",
    "DM23": "J. De Messemaeker et al., \"New Cu 'bulge-out' mechanism supporting sub-micron scaling of hybrid wafer-to-wafer bonding,\" in <i>Proc. IEEE ECTC</i>, pp. 1042–1049, 2023.",
    "DM26": "J. De Messemaeker et al., \"Understanding scaling and temperature limits in Cu bulge-out mechanism for hybrid wafer-to-wafer bonding,\" in <i>Proc. IEEE ECTC</i>, pp. 2158–2162, 2026, doi:10.1109/ECTC51846.2026.00355.",
    "AY22": "B. Ayoub et al., \"In-situ characterization of thermomechanical behavior of copper nano-interconnect for 3D integration,\" <i>Microelectron. Eng.</i>, vol. 261, 111809, 2022.",
    "LIN25": "H.-E. Lin et al., \"Revealing challenges of downscaling effects on Cu thermal expansion in advanced hybrid bonding using in-situ AFM,\" <i>Appl. Surf. Sci.</i>, vol. 689, 162539, 2025.",
    "CHEN25": "P.-L. Chen and C. Chen, \"Effect of dimension on thermal expansion of Cu pads in SiO_{2} vias for 3D IC fine-pitch hybrid bonding,\" in <i>Proc. IEEE 75th Electron. Compon. Technol. Conf. (ECTC)</i>, Dallas, TX, USA, May 2025, doi:10.1109/ECTC51687.2025.00329.",
    "DM24": "J. De Messemaeker et al., \"Simulation of bulge-out mechanism enabling sub-0.5 µm scaling of hybrid wafer-to-wafer bonding,\" in <i>Proc. IEEE ECTC</i>, 2024.",
    "TSAU22": "Y. W. Tsau et al., \"Simulation of Cu pad expansion in wafer-to-wafer Cu/SiCN hybrid bonding,\" <i>Microelectron. Reliab.</i>, vol. 138, Art. no. 114716, 2022, doi:10.1016/j.microrel.2022.114716.",
    "HOOGE24": "J. Hooge, C. Jois, C. Netzband, and I. Son, \"Modeling of copper hybrid bonding anneal,\" in <i>Proc. IEEE 74th Electron. Compon. Technol. Conf. (ECTC)</i>, Denver, CO, USA, May 2024, pp. 1231–1235.",
    "BUT73": "D. B. Butrymowicz, J. R. Manning, and M. E. Read, \"Diffusion in copper and copper alloys, Part I,\" <i>J. Phys. Chem. Ref. Data</i>, vol. 2, pp. 643–655, 1973.",
    "VHIRPS": "S. Van Huylenbroeck et al., \"Wafer to wafer hybrid bonding pitch scaling challenges (Invited),\" in <i>Proc. IEEE Int. Reliab. Phys. Symp. (IRPS)</i>, Tucson, AZ, USA, Mar. 2026, doi:10.1109/IRPS61424.2026.11499286.",
    "OKU17": "O. O. Okudur et al., \"Thermomechanical aspects of wafer-to-wafer copper-dielectric hybrid bonding for 3D integrated circuits,\" in <i>Int. Conf. Wafer Bonding</i>, Leuven, 2017.",
    "ASME": "ASME V&V 10-2019, <i>Standard for Verification and Validation in Computational Solid Mechanics</i>, ASME, 2019.",
    "AYTH": "B. Ayoub, <i>Electrical and morphological characterizations of the hybrid bonding level down to submicron pitches</i>, PhD thesis, Univ. Bordeaux, 2023.",
    "OKORO": "C. Okoro et al., \"Extraction of the appropriate material property for realistic modeling of through-silicon-vias using µ-Raman spectroscopy,\" in <i>Proc. IEEE Int. Interconnect Technol. Conf. (IITC)</i>, San Francisco, CA, USA, Jun. 2008, pp. 16–18.",
}
