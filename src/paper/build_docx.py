r"""
Build the two IEIE 2026 fall submissions from the official templates:
  docs/paper/ieie2026f_proceedings_final.docx  (proceedings, double column, <= 5 pages, authors "[저자 기입]")
  docs/paper/ieie2026f_blind_final.docx        (written review, journal template, exactly 4 pages, no identifiers)
Every number in the text is taken from repository files (see docs/paper/ieie2026f_number_sources.md).
Figures: docs/paper/figures/*.png (src/paper/make_figures.py).

Usage (repo root): python src\paper\build_docx.py
Page count: run src\paper\paper_pagecount.ps1 natively (Word COM is not available in the agent sandbox).
"""
from __future__ import annotations

import copy
import re
import shutil
import zipfile
from pathlib import Path

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parents[2]
TPL = ROOT / "docs" / "paper" / "templates"
FIG = ROOT / "docs" / "paper" / "figures"
OUT_P = ROOT / "docs" / "paper" / "ieie2026f_proceedings_final.docx"
OUT_B = ROOT / "docs" / "paper" / "ieie2026f_blind_final.docx"
COLW = Cm(7.95)

TITLE_KO = "서브마이크론 Cu 하이브리드 본딩 패드의 접촉 기구 전환과 300 nm 공정창 예측: 사전등록 검증 기반 열탄성–표면확산 모델"
TITLE_KO_LINES = ["서브마이크론 Cu 하이브리드 본딩 패드의 접촉 기구 전환과", "300 nm 공정창 예측: 사전등록 검증 기반 열탄성–표면확산 모델"]
TITLE_EN_LINES = ["Mechanism Transition and 300 nm Process-Window Prediction for Sub-Micron Cu",
                  "Hybrid-Bonding Pads: A Pre-Registered Thermo-Elastic/Surface-Diffusion Model"]

ABSTRACT_KO = ("패드 피치가 1 µm 아래로 줄면 Cu 열탄성 팽창만으로는 CMP recess를 닫지 못한다. 문헌 물성 열탄성 FEM과 표면확산 "
               "bulge-out 식을 결합한 모델을 세 연구그룹 실측으로 사전등록 시험한 결과, 접촉 기구는 recess 합 5 nm에서 약 0.7 µm를 "
               "경계로 표면확산으로 넘어가고 방위 효과는 확산 항으로 들어온다. 300 nm 패드의 공정창, recess 허용 합 7.5–11.5 nm, "
               "미접촉 쌍 하한을 불확실도와 함께 예측하였다.")
ABSTRACT_EN = ("Below 1 µm pitch, thermo-elastic expansion of Cu pads cannot close the CMP recess. A thermo-elastic FEM built "
               "from literature properties was combined with a surface-diffusion bulge-out term and tested, with pre-registered "
               "rules, against measurements of three research groups. The contact mechanism changes from thermo-elastic to "
               "surface diffusion at about 0.7 µm for a 5 nm recess sum, and below it the crystal orientation acts through the "
               "diffusion term rather than the elastic term. For 300 nm pads the model predicts a process window, an allowable "
               "recess sum of 7.5–11.5 nm and an open-pair floor, with uncertainty.")
KEYWORDS = "Hybrid bonding, Cu bulge-out, surface diffusion, pre-registration, process window"

# ------------------------------------------------------------------ body text (proceedings)
# markup: _{x} subscript, ^{x} superscript; citations [n] are superscripted automatically.
INTRO = [
    "웨이퍼 간(W2W) Cu/SiCN 하이브리드 본딩은 200 nm 피치까지 전기적 수율이 보고되었다[1]. 이 영역에서는 접합 후 어닐 중 Cu "
    "패드의 열탄성 팽창이 패드 부피에 비례해 줄어 1 nm 이하가 되며, 상·하 패드의 Cu–Cu 접촉은 표면확산에 의한 Cu 원자의 "
    "재배치(bulge-out)가 만든다[2,3]. 따라서 1 µm 아래에서는 \"어떤 recess에서 닫히는가\"가 아니라 \"어떤 어닐·표면·라이너·"
    "방위 조건에서 닫히는가\"가 공정 설계 질문이 된다.",
    "본 논문은 어닐 중 Cu 패드가 솟는 양을 두 기구의 합으로 본다. (i) 열탄성 돌출 u는 Cu와 유전체·Si의 열팽창 차이로 생기며 "
    "패드 부피에 비례하고 식으면 되돌아간다. (ii) 표면확산 bulge-out h_{d}는 표면에너지를 줄이려는 Cu 원자의 이동으로 생기며 "
    "어닐 온도·시간·표면 상태·결정 방위에 의존하고 되돌아가지 않는다. 접촉 조건은 두 기구의 위·아래 합이 recess 합을 넘는 "
    "것이다(Fig. 1a). 두 기구는 패드 크기에 다르게 반응하므로 접촉을 결정하는 기구가 크기에 따라 바뀐다.",
    "선행연구는 역할이 나뉘어 있다. Ayoub 등[4]은 300 nm 패드의 Laue 편차 변형률로 방위에 따른 탄성 차이를 보였고, "
    "Lin·Chen 등[5,6]은 in-situ AFM으로 1–9 µm 패드의 돌출을 쟀으며, imec[2,3,7]은 접합 후 상부 웨이퍼를 제거해 수천 개 "
    "패드의 bulge-out 분포를 AFM·EBSD로 측정했다. 그러나 열탄성·표면확산을 하나의 공정창으로 묶고 각 부분을 독립 실측으로 "
    "시험한 연구는 없으며, 벌크 물성 FEM은 sub-µm 실측을 재현하지 못한다는 보고가 있다[8].",
    "본 연구의 기여는 세 가지다. ① 세 연구그룹의 실측으로 교차 시험한 결합 모델에서, 접촉 기구가 열탄성에서 표면확산으로 "
    "넘어가는 폭을 recess 조건부 규칙으로 정량화했다(recess 합 3/5/8 nm에서 실측 기준 0.55/0.70/1.0 µm, 5 nm에서 모델 "
    "0.66–1.06 µm). ② sub-µm에서 결정 방위의 효과는 탄성 항(폭 4 %)이 아니라 표면확산 항(<111> facet)을 통해 들어오며, "
    "이 항이 imec bulge-out 분포의 폭과 <111> 꼬리를 재조정 없이 재현함을 보였다. 즉 방위 위험은 Ayoub가 제안한 [111] 기준 "
    "recess 사양이 아니라 어닐·텍스처로 다뤄야 한다. ③ 300 nm 공정창, CMP recess 허용 합, 방위에 의한 미접촉 쌍 하한과 "
    "인자 순위를 불확실도와 함께 제시하고, 탄성 모델의 0.54 µm 오차가 이 결론을 거의 바꾸지 않음을 보였다.",
]
S21 = ("recess r은 CMP 후 Cu 윗면이 유전체 면보다 낮은 깊이(공정 입력), u는 어닐 중 열탄성 돌출(모델 출력), h_{d}는 표면확산 "
       "bulge-out 높이(패드 자기 표면 기준), ε′_{zz}는 Laue가 재는 편차 탄성 변형률이며 서로 섞지 않는다. 상·하 패드의 접촉 "
       "여유는 m = u_{t} + u_{b} + h_{d,t} + h_{d,b} − (r_{t} + r_{b})이고, 방위와 recess를 확률 변수로 두어 P(m ≥ 0)을 "
       "Monte Carlo로 계산한다.")
S22 = ("ANSYS MAPDL(µMKS)로 원형 Cu 패드, 측벽 테이퍼, Ta 라이너, 유전체, Si 기판 등가층을 모델링했다. 3D SOLID185 모델은 "
       "Cu 탄성상수 C_{11}/C_{12}/C_{44} = 168.4/121.4/75.4 GPa를 결정 방위로 회전한 이방성으로, 큰 다결정 패드는 2D 축대칭 "
       "Hill 등방(128 GPa, 0.345)으로 두고 α_{Cu} = 16.5 ppm/K이다. 측벽은 접합(절점 공유)을 기본으로 하고 미끄럼(법선만 구속)을 "
       "대조군으로 둔다. 물리 규칙·Cu 물성·경계조건·메시 규칙은 모든 시료에 "
       "같고 형상·라이너·유전체·피치·열이력만 시료별 입력이다. 유전체 E·α는 공정당 한 번, 큰 패드에서만 문헌 범위 안에서 학습했다"
       "(NYCU SiO_{2} 59 GPa·1.0 ppm/K·테이퍼 18°, imec SiCN 120 GPa·2.0 ppm/K; 모두 범위 끝). u는 중앙 50 % 면적 평균에서 "
       "주변 유전체 평균을 뺀 값(AFM 정의와 동일)이다. 수치 검증: 이방성 단일요소 3방위 오차 < 0.01 %, 메시 ×2 +0.02 %, "
       "3D–2D 0.1–0.7 %, 셀 12 w(20 w 대비 1.3 %).")
S23a = "DM2024[7]의 선형화를 따라 패드당 확산 높이를 다음과 같이 둔다."
EQ1 = "h_{d} = s_{ox}·0.0022(θ_{eff} − 90°)·D·f(ω)·[1 − e^{−t/τ}],  τ = τ_{0}(D/200 nm)^{3.7}·D_{s}(350 °C)/D_{s}(T)"
EQ_LINES = ["h_{d} = s_{ox}·0.0022(θ_{eff} − 90°)·D·f(ω)·[1 − e^{−t/τ}],", "τ = τ_{0}(D/200 nm)^{3.7}·D_{s}(350 °C)/D_{s}(T)"]
S23b = ("D는 패드 지름, t는 어닐 시간, D_{s}는 Cu 표면확산계수(Q = 20.7 kcal/mol[9]), τ_{0} = 60 s, s_{ox}는 표면 산화 배율(청정 1, "
        "산화 0.45[2])이다. 방위 진폭 f(ω) = clip((ω − ω_{c})/Δω, 0, 1)은 패드 법선과 가장 가까운 <111> 사이의 각 ω로 정의한다. "
        "fcc Cu에서 {111}이 최저 표면에너지라 <111> 패드는 평평한 면을 유지해 곡률 구동력을 잃는다[3]. Cu 표면확산계수의 "
        "방위 이방성은 오히려 (111)이 1.5–3배 빠른 쪽이므로[9] 꼬리는 동역학이 아니라 진폭으로 넣었다.")
S24 = ("ASME V&V 10-2019[13]의 순서(수치 검증–학습–테스트–예측, Fig. 1b)를 따랐다. 탄성 모델의 학습 데이터는 큰 패드(NYCU 9·3 µm[5], "
       "imec 1.80·3.06 µm[2]), 테스트는 imec 1.26·0.54 µm, NYCU 1 µm[5,6](같은 그룹이므로 한 점), 미끄럼 측벽 대조군이다(Table 1). "
       "확산 항은 imec 2026[3]의 400 nm 피치·350 °C 한 점에서 진폭만 학습하고 나머지 17점(피치 200–500 nm, 200–450 °C, 1–4 h)으로 "
       "테스트했다(점별 허용 max(1.5 nm, 25 %, 판독 오차), 80 % 이상 통과 + 온도 경향 + 350 °C 이상 포화). 방위 항은 EBSD가 있는 "
       "500 nm 피치에서 학습했으며, 데이터를 본 뒤의 탐색(2차 라운드)으로 표기한다. 각 규칙은 결과 계산 전에 공개 저장소에 git 커밋으로 "
       "고정했고 테스트 실패 시 문서화된 개정 1회만 허용했다.")
S31 = ("Table 2에 결과를 요약했다. 학습값은 모두 문헌 범위의 끝에 걸렸고(bound-limited), imec 3.06 µm는 300–400 °C에서 측정의 "
       "초선형 증가를 따라가지 못해 학습 단계에서 실패로 기록했다. 테스트에서 NYCU 1 µm(모델 1.79–1.94 nm, 실측 2.1 ± 0.4 nm)와 "
       "imec 1.26·0.54 µm의 100–200 °C는 통과했고, 1.26 µm 300–400 °C는 과소예측으로 실패했다. 미끄럼 측벽 대조군은 1 µm에서 1.7배, "
       "0.54 µm에서 3.5배 과대예측하여 측벽이 접합 상태임이 판별되었다. 그러나 imec 0.54 µm는 100–400 °C 전 구간에서 측정/모델 비 "
       "0.61–0.69로 과대예측했고(400 °C에서 +46 %), 사전 기준에 따라 0.54 µm 탄성 모델은 NOT VALIDATED로 동결했다. 이 결과를 recess와 "
       "함께 놓으면 기구 전환이 드러난다(Fig. 2). recess 합을 IRPS 2026 실측 평균 5 nm[10]로 고정하고, 크기별 열탄성 돌출을 공정 상한 "
       "400 °C에서 취해 위·아래 합 2u가 5 nm를 넘는 최소 크기를 log(크기) 보간으로 구했다. 실측 기준 0.70 µm, 모델 기준 0.66 µm(b = 1)–1.06 µm(b = 0.69)이다. 그 아래에서는 400 °C에서도 탄성만으로 접촉이 안 되며"
       "(300 nm: 패드당 ≈ 1 nm), 200–400 nm 피치 본딩이 실제로 성립하는 것[1]은 표면확산이 틈을 메운다는 뜻이다. 전환 크기는 recess 합의 "
       "함수이다(Fig. 2 인셋).")
S32 = ("고정형(θ = 123°, τ_{0} 학습)은 17점 중 2점만 통과했다. 학습점(350 °C 1 h)이 포화 상태라 진폭 오차가 τ_{0}로 흡수된 탓이다. "
       "문서화된 개정 1(θ_{eff} 학습, τ_{0} = 60 s 고정)에서 θ_{eff} = 113.6°, 11/17 통과, 온도 경향 통과, 포화 비 경계 실패로 규칙상 "
       "NOT VALIDATED이다. 실패 6점은 모두 과소예측이며 200 °C의 D ≥ 250 nm 패드 또는 자가 어닐(self-anneal) Cu였고, 250 °C 이상 "
       "PPA-Cu 테스트 점은 5/5(중복 점검 포함 7/7) 통과했다(Fig. 3a). 즉 식 (1)은 250 °C 이상에서 실측과 맞고 200 °C에서는 보수적이다. "
       "측정의 2 h → 4 h 증가율로 추정한 유효 활성화에너지는 14–17 kcal/mol로 문헌값 20.7보다 작다. 방위 항을 넣은 2차 탐색"
       "(θ_{eff} 119°, ω_{c} 5°, Δω 19.5°)은 중앙값 통과율(11/17)을 바꾸지 않지만 분포 폭(IQR)을 10/17 재현했다. 방위가 없는 모델의 "
       "IQR은 0이다(Fig. 3c: f = 0인 패드 1.5 %, f < 0.5인 패드 13 %).")
S33 = ("같은 적층(SiN 캡, Ta 13 nm)의 접합 모델은 3 µm 패드에서 ε′_{zz}(30 °C) = −1.24 × 10^{−3}으로 실측 범위(어닐 후 −0.5…−2.0 × 10^{−3})[4,14]"
       "와 부호가 일치했고, 300 nm에서는 두 방위(E_{z} 68·190 GPa)의 가열 기울기 크기가 0.5 % 안에 들었으나 부호가 반대였다. Ayoub 시료는 "
       "다른 공정(Cu/SiO_{2}, CMP 후 PECVD SiN 캡)이고 Cu 계면 조건이 명시돼 있지 않으므로 계면 상태 차이(캡·측벽)로 해석하되 가설로 "
       "둔다. 300 nm 크기 재현은 주장하지 않으며, 미끄럼 측벽은 상한 시나리오로만 쓴다.")
S34 = ("탄성 항(b = 0.69; 0.54 µm 테스트 비 범위 0.60–1.0로 반복)과 식 (1)(방위 항 포함)의 단순합으로, 상·하 방위(구면 균일)와 recess"
       "(패드당 N(2.5, 0.5²) nm[10]) 2 × 10^{5} 쌍에 대해 P_{contact}를 계산했다(Fig. 4). 청정 표면에서 창(P ≥ 0.99)은 250 °C × 2 h 또는 "
       "300 °C × 30 min부터 열리고 350 °C 이상은 5 min이면 충분하다. 불확실 집합 b × τ_{0}{20, 60, 100 s} × Q{20.7, 15}에서 바뀌는 셀은 "
       "경계 3개뿐이며 청정 표면 권고 레시피는 b 전 범위에서 같다. 탄성 항은 300 nm·350 °C·1 h에서 총 돌출 중앙값 19.9 nm 중 0.75 nm이다. "
       "표면 산화(s_{ox} 0.45)는 최소 레시피를 300 °C × 2 h 또는 350 °C × 30 min으로 늦춘다. 같은 계산을 recess 평균에 대해 풀면 CMP에 "
       "돌려줄 허용 합이 나온다(Fig. 5): 청정 표면 250 °C × 2 h에서 7.5 nm, 300 °C × 30 min에서 9 nm, 350 °C × 2 h와 400 °C에서 11.5 nm"
       "(산화 표면은 3.5–6 nm). 인자 순위(창에서 바뀌는 셀 수, 300 nm·청정, Fig. 6a)는 지배 기구(확산 off: 9/15) ≫ 표면 상태(3) > "
       "확산 동역학 τ_{0}·Q, <111> facet, 라이너 접촉각(각 2) > recess 평균·산포와 b(0) 순이다. 방위는 탄성 항이 아니라 확산 항을 통해 "
       "들어오며, 총 돌출의 방위 폭(q90 − q10)은 300 nm에서 11.5 nm(탄성 0.03 nm)이다. <111> 근방 패드는 bulge-out이 작아 권고 셀에서 "
       "미접촉 쌍이 2.3–3.4 × 10^{−3}, 400 °C에서도 1.4 × 10^{−3} 남는다(Fig. 6b). facet 항을 끈 경우(미세결정 Cu 대용)에는 이 하한이 "
       "사라진다[3]. 접촉 후 연결 단계(2D 축대칭 Cu–Cu 마찰 접촉, 등방 소성[15])에서는 300 nm·350 °C·recess 1–2 nm에서 접촉면적 분율 "
       "0.95–1.0, 평균 접촉압력 317–403 MPa로 재결정의 필요조건을 만족하나 접합의 증명은 아니다.")
S4a = ("Table 3에 모델 부분별 상태를 정리했다. 한계: (1) 0.54 µm 탄성 오차 +46 %의 원인은 원 데이터(Okudur 2017[11]) 부재로 미상이며, "
       "결정 민감도 시험에서는 산화 표면 경계 2셀만 영향을 받았다. (2) 300 nm 돌출 실측은 없어 300 nm는 예측이다(확산 항은 같은 크기에서 "
       "250 °C 이상 실측 점검; 0.54 µm 확산 창은 외삽). (3) 200 °C 확산 동역학과 결정립 수·도금 후 어닐 이력은 모델 밖이다. (4) 연결 단계 "
       "접촉 FEM은 Lhostis[12]의 패드 두께 효과를 재현하지 못한다. (5) 오버레이는 범위 밖이다[1]. (6) 크리프·장시간 계면 완화는 미결이다.")
S4b = ("결론적으로 1 µm 아래에서 Cu 하이브리드 본딩의 접촉은 열탄성 팽창이 아니라 표면확산이 결정하며(recess 합 5 nm에서 전환 ≈ 0.7 µm), "
       "레시피 변수는 어닐 온도·시간·표면 상태·라이너·결정 방위(<111> 텍스처 분율)로 옮겨간다. 주장 수위는 \"검증된 레시피\"가 아니라 "
       "\"검증 통과 범위의 탄성 모델과 실측으로 점검한 확산 모델로 본 공정창 예측(불확실도 포함)\"이다. 향후 표면확산을 FEM 안에 넣어 "
       "방위별 표면에너지 γ(ω)로 f(ω)를 대체하고, 미세결정 Cu 실측을 보정점으로 한 다음 사전등록을 수행한다.")

REFS = [
    "S. Van Huylenbroeck et al., \"Wafer-to-wafer hybrid bonding technology with 200nm interconnect pitch,\" in <i>Proc. IEEE ECTC</i>, 2026.",
    "J. De Messemaeker et al., \"New Cu 'bulge-out' mechanism supporting sub-micron scaling of hybrid wafer-to-wafer bonding,\" in <i>Proc. IEEE ECTC</i>, pp. 1042–1049, 2023.",
    "J. De Messemaeker et al., \"Understanding scaling and temperature limits in Cu bulge-out mechanism for hybrid wafer-to-wafer bonding,\" in <i>Proc. IEEE ECTC</i>, pp. 2158–2162, 2026, doi:10.1109/ECTC51846.2026.00355.",
    "B. Ayoub et al., \"In-situ characterization of thermomechanical behavior of copper nano-interconnect for 3D integration,\" <i>Microelectron. Eng.</i>, vol. 261, 111809, 2022.",
    "H.-E. Lin et al., \"Revealing challenges of downscaling effects on Cu thermal expansion in advanced hybrid bonding using in-situ AFM,\" <i>Appl. Surf. Sci.</i>, vol. 689, 162539, 2025.",
    "P.-L. Chen and C. Chen, \"Effect of dimension on thermal expansion of Cu pads in SiO_{2} vias for 3D IC fine-pitch hybrid bonding,\" in <i>Proc. IEEE 75th Electron. Compon. Technol. Conf. (ECTC)</i>, Dallas, TX, USA, May 2025, doi:10.1109/ECTC51687.2025.00329.",
    "J. De Messemaeker, K. Van Sever, Y. W. Tsau, B. Zhang, K. Croes, and E. Beyne, \"Simulation of bulge-out mechanism enabling sub-0.5 µm scaling of hybrid wafer-to-wafer bonding,\" in <i>Proc. IEEE ECTC</i>, 2024.",
    "Y. W. Tsau, J. De Messemaeker, A. Salahouelhadj, M. Gonzalez, L. Witters, B. Zhang, M. Seefeldt, E. Beyne, and I. De Wolf, \"Simulation of Cu pad expansion in wafer-to-wafer Cu/SiCN hybrid bonding,\" <i>Microelectron. Reliab.</i>, vol. 138, Art. no. 114716, 2022, doi:10.1016/j.microrel.2022.114716.",
    "D. B. Butrymowicz, J. R. Manning, and M. E. Read, \"Diffusion in copper and copper alloys, Part I,\" <i>J. Phys. Chem. Ref. Data</i>, vol. 2, pp. 643–655, 1973.",
    "S. Van Huylenbroeck et al., \"Wafer to wafer hybrid bonding pitch scaling challenges (Invited),\" in <i>Proc. IEEE Int. Reliab. Phys. Symp. (IRPS)</i>, Tucson, AZ, USA, Mar. 2026, doi:10.1109/IRPS61424.2026.11499286.",
    "O. O. Okudur et al., \"Thermomechanical aspects of wafer-to-wafer copper-dielectric hybrid bonding for 3D integrated circuits,\" in <i>Int. Conf. Wafer Bonding</i>, Leuven, 2017.",
    "S. Lhostis et al., \"Contact resistivity of submicron hybrid bonding pads down to 400 nm,\" <i>J. Electron. Mater.</i>, vol. 53, pp. 4421–4431, 2024.",
    "ASME V&V 10-2019, <i>Standard for Verification and Validation in Computational Solid Mechanics</i>, ASME, 2019.",
    "B. Ayoub, <i>Electrical and morphological characterizations of the hybrid bonding level down to submicron pitches</i>, PhD thesis, Univ. Bordeaux, 2023.",
    "C. Okoro, Y. Yang, B. Vandevelde, B. Swinnen, D. Vandepitte, B. Verlinden, and I. De Wolf, \"Extraction of the appropriate material property for realistic modeling of through-silicon-vias using µ-Raman spectroscopy,\" in <i>Proc. IEEE Int. Interconnect Technol. Conf. (IITC)</i>, San Francisco, CA, USA, Jun. 2008, pp. 16–18.",
]

FIGCAP = {
    "fig1_architecture": "Fig. 1. (a) Pad pair with recess r, thermo-elastic protrusion u and surface-diffusion bulge-out h_{d}; contact when m = u_{t} + u_{b} + h_{d,t} + h_{d,b} − (r_{t} + r_{b}) ≥ 0. (b) Pre-registered V&V workflow (verification → train → test → prediction).",
    "fig2_transition": "Fig. 2. Mechanism transition with pad size: top + bottom elastic protrusion at 400 °C (FEM, FEM × 0.69, imec measurement) versus the saturated diffusion bulge-out (checked for D ≤ 300 nm; dashed = extrapolation) and the IRPS 2026 recess sum of 5 nm; crossover ≈ 0.7 µm. Inset: transition size versus recess sum.",
    "fig3_diffusion": "Fig. 3. Surface-diffusion term (with orientation factor, exploratory round 2) versus imec 2026 bulge-out distributions: (a) 400/500 nm pitch medians and IQR versus anneal T and time (open = failed point), (b) size dependence at 250 °C, 1 h (200–500 nm pitch), (c) orientation factor f(ω) and the faceted fraction.",
    "fig4_window300": "Fig. 4. 300 nm pads: contact-probability process window over anneal T × time for a clean surface (main) and an oxidised surface (sensitivity); hatched cells change within the uncertainty set b × τ_{0} × Q; boxes mark the recommended cells.",
    "fig5_recess_spec": "Fig. 5. 300 nm pads: allowable CMP recess sum (top + bottom, nm) for P(contact) ≥ 0.99 for each anneal T × time (σ = 0.5 nm per pad).",
    "fig6_factors": "Fig. 6. (a) Factor ranking: number of window cells (of 15, clean surface) changed when each factor is varied, 0.30 and 0.54 µm. (b) Open-pair fraction at 300 nm with the <111> facet term versus without it (fine-grained-Cu proxy); zero counts are drawn at 1/n.",
}

T1 = ("Table 1. Datasets and their roles (pre-registered split).",
      ["Group / process", "Measurement", "Sizes", "Role"],
      [["NYCU [5,6], Cu/SiO2", "in-situ AFM u(T), 25–200 °C", "9, 3, 1 µm", "train 9, 3; test 1"],
       ["imec [2,11], Cu/SiCN", "in-situ SPM u(T), 100–400 °C", "3.06, 1.80, 1.26, 0.54 µm", "train 3.06, 1.80; test 1.26, 0.54"],
       ["imec 2026 [3], Cu/SiCN", "post-bond AFM Δh_max distributions, EBSD", "D 115–300 nm, 200–450 °C, 1–4 h", "diffusion: train 1, test 17"],
       ["ST/Leti [4,14], Cu/SiO2", "Laue ε′zz(T)", "0.3, 3 µm", "comparison (sign)"],
       ["imec IRPS 2026 [10]", "recess distribution", "≤ 1 µm", "input N(2.5, 0.5²) nm/pad"]],
      [2.0, 2.2, 1.9, 1.85])
T2 = ("Table 2. Elastic-model train/test (array cell, bonded sidewall).",
      ["Case", "Model (nm)", "Measured (nm)", "Rule", "Result"],
      [["NYCU 9 / 3 µm, 200 °C (train)", "6.87 / 4.26", "6.4 / 4.1 ± 0.4", "2σ", "pass"],
       ["imec 1.80 µm, 100–400 °C (train)", "1.00–4.99", "1.05–5.40", "2σ", "pass"],
       ["imec 3.06 µm, 300 / 400 °C (train)", "4.64 / 6.32", "6.05 / 7.85", "2σ", "fail"],
       ["NYCU 1 µm, 3 orientations, 200 °C", "1.79–1.94", "2.1 ± 0.4", "overlap", "pass"],
       ["imec 1.26 µm, 100/200/300/400 °C", "0.81/1.88/2.96/4.04", "0.70/1.60/3.65/5.00", "0.5 nm or 15 %", "P/P/F/F"],
       ["imec 0.54 µm, 100/200/300/400 °C", "0.41/0.95/1.50/2.04", "0.25/0.60/1.00/1.40", "0.4 nm", "P/P/F/F"],
       ["sliding control, 1 / 0.54 µm", "3.66 / 4.84", "2.1 / 1.4", "must fail", "fails"]],
      [2.65, 1.45, 1.55, 1.15, 0.9])
T3_ROWS = [
    ["Elastic u, bonded: NYCU 1 µm; imec 1.26, 0.54 µm at 100–200 °C", "validated (pre-registered)", "33a8f5c"],
    ["Elastic u, imec 0.54 µm at 300–400 °C (and 1.26 µm)", "not validated (+46 % at 0.54 µm); decision sensitivity OPEN (2 oxidised boundary cells)", "2acfd92 / 5c1e819"],
    ["Diffusion h_d, fixed form", "not validated (2/17)", "9c6bc29 / 5fa0e05"],
    ["Diffusion h_d, revision 1 (θ_eff)", "not validated by rule (11/17); 5/5 PPA-Cu at ≥ 250 °C", "eb347c1 / 5221d33"],
    ["Orientation amplitude f(ω)", "exploratory round 2: IQR 10/17", "6696562 / d722e67"],
    ["Ayoub ε′zz", "3 µm sign agrees; 300 nm sign disagrees (interface hypothesis)", "63869bb / f7818ad"],
    ["Connection-stage contact FEM", "Lhostis thickness test failed twice", "6696562 / dced86f / 46924cc"],
    ["300 nm window", "prediction with uncertainty", "80389d5 / 9dbd0c0"],
]
T3 = ("Table 3. Status of each model part.", ["Part", "Status", "Evidence (commit)"], T3_ROWS, [2.8, 3.45, 1.7])
T3_BLIND = ("Table 3. Status of each model part (rules pre-registered in a public repository; identifiers disclosed after review).",
            ["Part", "Status"], [r[:2] for r in T3_ROWS if not r[0].startswith(("Connection", "Diffusion h_d, fixed"))],
            [3.4, 4.55])

# ------------------------------------------------------------------ helpers
_MARK = re.compile(r"(_\{[^}]*\}|\^\{[^}]*\}|\[\d{1,2}(?:[,–-]\d{1,2})*\]|<i>.*?</i>)")


def _runs(text):
    """yield (text, kind) where kind in {'', 'sub', 'sup', 'cite', 'i'}"""
    pos = 0
    for m in _MARK.finditer(text):
        if m.start() > pos:
            yield text[pos:m.start()], ""
        t = m.group(0)
        if t.startswith("_{"):
            yield t[2:-1], "sub"
        elif t.startswith("^{"):
            yield t[2:-1], "sup"
        elif t.startswith("<i>"):
            yield t[3:-4], "i"
        else:
            yield t, "cite"
        pos = m.end()
    if pos < len(text):
        yield text[pos:], ""


def _font(run, name, size=None, bold=None, east=None):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi"):
        rf.set(qn(a), name)
    rf.set(qn("w:eastAsia"), east or name)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold


def fill(par, text, font, size=None, east=None, bold=None, cite=True):
    for t, kind in _runs(text):
        if kind == "cite" and not cite:
            kind = ""
        r = par.add_run(t)
        _font(r, font, size, bold, east)
        if kind in ("sub",):
            r.font.subscript = True
        if kind in ("sup", "cite"):
            r.font.superscript = True
        if kind == "i":
            r.font.italic = True
    return par


def clear_after(body, keep_upto_el):
    """remove every body child after keep_upto_el except the final sectPr"""
    seen = False
    for el in list(body.iterchildren()):
        if el is keep_upto_el:
            seen = True; continue
        if seen and el.tag != qn("w:sectPr"):
            body.remove(el)


def set_cell_borders(cell, top=None, bottom=None):
    tcPr = cell._tc.get_or_add_tcPr()
    b = OxmlElement("w:tcBorders")
    for side, val in (("top", top), ("bottom", bottom), ("left", None), ("right", None)):
        e = OxmlElement(f"w:{side}")
        if val:
            e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(val)); e.set(qn("w:color"), "000000")
        else:
            e.set(qn("w:val"), "nil")
        b.append(e)
    tcPr.append(b)


def add_table(doc, spec, font="Times New Roman", size=7.0, before=None):
    cap, head, rows, widths = spec
    t = doc.add_table(rows=1 + len(rows), cols=len(head))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tblPr = t._tbl.tblPr
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
    mar = OxmlElement("w:tblCellMar")
    for side in ("left", "right"):
        e = OxmlElement(f"w:{side}"); e.set(qn("w:w"), "45"); e.set(qn("w:type"), "dxa"); mar.append(e)
    tblPr.append(mar)
    for ri, row in enumerate([head] + rows):
        for ci, val in enumerate(row):
            c = t.cell(ri, ci); c.width = Cm(widths[ci])
            p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            fill(p, val, font, size, bold=(ri == 0), cite=True)
            set_cell_borders(c, top=8 if ri == 0 else (4 if ri == 1 else None),
                             bottom=8 if ri == len(rows) else None)
    return t


# ------------------------------------------------------------------ proceedings
def build_proceedings():
    d = docx.Document(str(TPL / "논문양식.docx"))
    body = d.element.body
    t_title, t_auth = d.tables[0], d.tables[1]
    # title
    ps = [p for c in t_title._cells for p in c.paragraphs if p.text.strip()]
    for p, line in zip(ps, TITLE_KO_LINES):
        for r in p.runs[1:]:
            r._element.getparent().remove(r._element)
        p.runs[0].text = line; p.runs[0].font.size = Pt(15)
    # authors / English title (placeholders)
    for c in t_auth._cells:
        for p in c.paragraphs:
            tx = p.text
            if not tx.strip():
                continue
            new = None
            if tx.strip().startswith("***,"):
                new = "[저자 기입]"
            elif "소속" in tx:
                new = "[소속 기입]"
            elif tx.strip().startswith("e-mail"):
                new = "e-mail : [기입]"
            elif tx.startswith("Implementation"):
                new = TITLE_EN_LINES[0]
            elif tx.startswith("Using"):
                new = TITLE_EN_LINES[1]
            elif "and" in tx and "***" in tx:
                new = "[Author names]"
            elif "University" in tx:
                new = "[Affiliation]"
            if new is not None:
                for r in p.runs[1:]:
                    r._element.getparent().remove(r._element)
                p.runs[0].text = new
                if new in TITLE_EN_LINES:
                    p.runs[0].font.size = Pt(11)
    # body: keep up to the section-break paragraph
    sect_p = next(el for el in body.iterchildren() if el.tag == qn("w:p") and el.find(".//" + qn("w:sectPr")) is not None)
    clear_after(body, sect_p)
    F, FS = "HY신명조", 9

    def para(text, size=FS, align="both", bold=None, indent=True, after=0, before=0):
        p = d.add_paragraph(style="바탕글")
        pf = p.paragraph_format; pf.line_spacing = 1.2; pf.space_after = Pt(after); pf.space_before = Pt(before)
        p.alignment = {"both": WD_ALIGN_PARAGRAPH.JUSTIFY, "center": WD_ALIGN_PARAGRAPH.CENTER,
                       "left": WD_ALIGN_PARAGRAPH.LEFT}[align]
        if indent:
            pf.first_line_indent = Pt(9)
        fill(p, text, "Times New Roman", size, east=F, bold=bold)
        return p

    def head(text):
        return para(text, size=12, align="center", indent=False, before=6, after=3)

    def sub(text, lead):
        p = para("", indent=True)
        fill(p, lead + " ", "Times New Roman", FS, east=F, bold=True)
        fill(p, text, "Times New Roman", FS, east=F)
        return p

    def figure(name):
        p = d.add_paragraph(style="바탕글"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4); p.paragraph_format.line_spacing = 1.0
        p.add_run().add_picture(str(FIG / f"{name}.png"), width=COLW)
        c = para(FIGCAP[name], size=8, align="both", indent=False, after=4)
        c.paragraph_format.line_spacing = 1.0
        return c

    def table(spec):
        c = para(spec[0], size=8, align="center", indent=False, before=4, after=1)
        c.paragraph_format.keep_with_next = True
        add_table(d, spec)
        para("", size=4, indent=False)

    head("요  약")
    para(ABSTRACT_KO)
    head("I. 서론")
    for t in INTRO:
        para(t)
    figure("fig1_architecture")
    head("II. 모델과 검증 절차")
    sub(S21, "2.1 용어와 접촉 조건.")
    sub(S22, "2.2 열탄성 FEM.")
    sub(S23a, "2.3 표면확산 항.")
    for k_, line in enumerate(EQ_LINES):
        eq = para("", indent=False, align="left")
        eq.paragraph_format.tab_stops.add_tab_stop(COLW - Cm(0.1), WD_TAB_ALIGNMENT.RIGHT)
        fill(eq, "    " + line + ("\t(1)" if k_ == 0 else ""), "Times New Roman", 9, east=F)
    para(S23b)
    sub(S24, "2.4 검증 절차와 사전등록.")
    table(T1)
    head("III. 결과")
    sub(S31, "3.1 열탄성 모델과 기구 전환.")
    table(T2)
    figure("fig2_transition")
    sub(S32, "3.2 표면확산 항 테스트.")
    figure("fig3_diffusion")
    sub(S33, "3.3 Ayoub 300 nm 변형률.")
    sub(S34, "3.4 300 nm 공정창과 레시피 변수.")
    figure("fig4_window300")
    figure("fig5_recess_spec")
    figure("fig6_factors")
    head("IV. 한계와 결론")
    para(S4a)
    table(T3)
    para(S4b)
    head("참고문헌")
    for i, r in enumerate(REFS, 1):
        p = d.add_paragraph(style="바탕글")
        pf = p.paragraph_format; pf.line_spacing = 1.0; pf.left_indent = Pt(13); pf.first_line_indent = Pt(-13)
        fill(p, f"[{i}] ", "Times New Roman", 7.5, east=F, cite=False)
        fill(p, r, "Times New Roman", 7.5, east=F, cite=False)
    d.core_properties.author = ""; d.core_properties.last_modified_by = ""; d.core_properties.title = ""
    d.core_properties.comments = ""
    d.save(str(OUT_P))
    _scrub_app(OUT_P)


# ------------------------------------------------------------------ blind (journal template)
BL_INTRO = [
    "웨이퍼 간 Cu/SiCN 하이브리드 본딩은 200 nm 피치까지 수율이 보고되었다[1]. 이 영역에서 어닐 중 Cu 패드의 열탄성 돌출 u는 "
    "패드당 1 nm 이하로 작아지고, 상·하 패드의 접촉은 표면확산 bulge-out h_{d}가 만든다[2,3]. 본 논문은 접촉 여유 "
    "m = u_{t} + u_{b} + h_{d,t} + h_{d,b} − (r_{t} + r_{b}) ≥ 0(r: CMP recess)으로 두 기구를 분해한다. 선행연구는 방위별 탄성"
    "(Ayoub[4]), 1–9 µm 돌출(Lin·Chen[5,6]), bulge-out 분포(imec[2,3])로 나뉘어 있고, 둘을 한 공정창으로 묶어 독립 실측으로 시험한 "
    "연구는 없다.",
    "기여는 세 가지다. ① 세 연구그룹 실측으로 교차 시험한 결합 모델에서 기구 전환 폭을 recess 조건부 규칙으로 정량화했다(recess 합 "
    "3/5/8 nm에서 0.55/0.70/1.0 µm). ② sub-µm에서 방위 효과는 탄성 항(폭 4 %)이 아니라 표면확산 항(<111> facet)을 통해 들어오며, "
    "이 항이 imec 분포의 폭과 꼬리를 재조정 없이 재현한다. 따라서 방위 위험은 Ayoub의 [111] 기준 recess 사양이 아니라 어닐·텍스처로 "
    "다뤄야 한다. ③ 300 nm 공정창, recess 허용 합, 미접촉 쌍 하한과 인자 순위를 불확실도와 함께 제시한다.",
]
BL_S2a = ("열탄성 u는 ANSYS FEM(이방성 Cu C_{11}/C_{12}/C_{44} = 168.4/121.4/75.4 GPa, α_{Cu} = 16.5 ppm/K, 접합 측벽, 배열 셀)으로 "
          "계산하고, 유전체 E·α만 공정당 한 번 큰 패드에서 문헌 범위 안에서 학습했다. 확산 항은 DM2024[7]의 선형화를 따른다.")
BL_S2b = ("여기서 Q = 20.7 kcal/mol[9], τ_{0} = 60 s, s_{ox}는 산화 배율(청정 1, 산화 0.45), f(ω) = clip((ω − ω_{c})/Δω, 0, 1)은 "
          "패드 법선과 가장 가까운 <111> 사이 각 ω의 진폭 인자다({111} facet은 곡률 구동력을 잃는다[3]). ASME V&V 10[13] 순서(수치 "
          "검증–학습–테스트–예측)를 따랐고, 탄성은 NYCU 9·3 µm와 imec 1.80·3.06 µm로 학습해 imec 1.26·0.54 µm, NYCU 1 µm, 미끄럼 측벽 "
          "대조군으로 테스트했다. 확산 항은 imec 2026[3]의 한 점(400 nm 피치, 350 °C)으로 진폭만 학습하고 17점으로 테스트했다. 모든 규칙은 "
          "결과 계산 전에 공개 저장소에 사전등록하였다(채택 후 공개).")
BL_S31 = ("Table 2처럼 NYCU 1 µm와 imec 1.26·0.54 µm의 100–200 °C는 통과했고, 미끄럼 측벽은 1 µm에서 1.7배, 0.54 µm에서 3.5배 과대예측해 "
          "측벽이 접합 상태임이 판별됐다. 그러나 0.54 µm는 전 온도에서 측정/모델 비 0.61–0.69로 과대예측해(400 °C +46 %) NOT VALIDATED로 "
          "동결했다. recess 합 5 nm[10]에서 400 °C 위·아래 탄성 돌출이 recess 합을 넘는 최소 크기는 실측 기준 0.70 µm, 모델 0.66–1.06 µm이다"
          "(Fig. 2). 그 아래에서는 탄성만으로 접촉이 안 된다(300 nm: 패드당 ≈ 1 nm).")
BL_S32 = ("고정형 확산 항은 2/17, 문서화된 개정 1(θ_{eff} = 113.6°)은 11/17 통과로 규칙상 NOT VALIDATED이다. 실패 6점은 모두 과소예측"
          "(200 °C의 D ≥ 250 nm 또는 자가 어닐 Cu)이고 250 °C 이상 PPA-Cu는 5/5 통과해, 식은 250 °C 이상에서 맞고 200 °C에서 보수적이다. "
          "방위 항을 넣은 2차 탐색(θ_{eff} 119°, ω_{c} 5°, Δω 19.5°)은 분포 폭(IQR)을 10/17 재현했다(Fig. 3; 방위 없는 모델의 IQR은 0).")
BL_S33 = ("Ayoub 변형률[4]과 비교하면 3 µm에서 ε′_{zz} 부호가 일치했고, 300 nm에서는 가열 기울기 크기가 0.5 % 안에 들되 부호가 반대였다. "
          "다른 공정·시료이므로 계면 상태 차이로 보되 가설로 두며, 300 nm 크기 재현은 주장하지 않는다.")
BL_S34 = ("상·하 방위(구면 균일)와 recess(패드당 N(2.5, 0.5²) nm) 2 × 10^{5} 쌍으로 P_{contact}를 계산하면(Fig. 4), 청정 표면 창(P ≥ 0.99)은 "
          "250 °C × 2 h 또는 300 °C × 30 min부터 열리고, 불확실 집합 b × τ_{0} × Q에서 바뀌는 셀은 경계 3개다. 산화 표면은 최소 레시피를 "
          "300 °C × 2 h로 늦춘다. recess 허용 합은 청정 표면 7.5 nm(250 °C × 2 h)–11.5 nm(400 °C)이다. 인자 순위는 지배 기구(9/15) ≫ "
          "표면 상태(3) > 확산 동역학·<111> facet·라이너(각 2) > recess·b(0)이다. 총 돌출의 방위 폭은 300 nm에서 11.5 nm(탄성 0.03 nm)이며, "
          "<111> 근방 패드 때문에 권고 셀에서 미접촉 쌍 2.3–3.4 × 10^{−3}, 400 °C에서도 1.4 × 10^{−3}이 남는다.")
BL_S4 = ("한계: 0.54 µm 탄성 오차의 원인은 원 데이터 부재로 미상이고(결정 민감도 시험에서 산화 경계 2셀만 영향), 300 nm 돌출 실측은 없어 "
         "300 nm는 예측이며, 200 °C 확산 동역학과 결정립 수·도금 후 어닐 이력은 모델 밖이고, 연결 단계 접촉 FEM은 두께 효과 시험에 "
         "실패했다(Table 3). 결론: 1 µm 아래에서 접촉은 표면확산이 결정하며(전환 ≈ 0.7 µm), 레시피 변수는 어닐 온도·시간·표면·라이너·"
         "방위(<111> 텍스처)로 옮겨간다. 주장 수위는 \"검증 통과 범위의 탄성 모델과 실측으로 점검한 확산 모델로 본 공정창 예측"
         "(불확실도 포함)\"이다.")
BL_T2 = ("Table 2. Elastic-model test (bonded sidewall).",
         ["Case", "Model (nm)", "Measured (nm)", "Result"],
         [["NYCU 1 µm, 200 °C", "1.79–1.94", "2.1 ± 0.4", "pass"],
          ["imec 1.26 µm, 100–400 °C", "0.81/1.88/2.96/4.04", "0.70/1.60/3.65/5.00", "P/P/F/F"],
          ["imec 0.54 µm, 100–400 °C", "0.41/0.95/1.50/2.04", "0.25/0.60/1.00/1.40", "P/P/F/F"],
          ["sliding, 1 / 0.54 µm", "3.66 / 4.84", "2.1 / 1.4", "fails (must)"]],
         [2.35, 2.05, 2.05, 1.5])


# ------------------------------------------------------------------ shared body (both submissions identical except authors)
ORDER = [1, 2, 3, 4, 5, 6, 7, 9, 10]              # REFS indices in order of first citation in the shared body (ASME [13] dropped for length)
REMAP = {old: new for new, old in enumerate(ORDER, 1)}


def rc(text):
    return re.sub(r"\[(\d{1,2}(?:[,–-]\d{1,2})*)\]", lambda m: "[" + ",".join(
        str(REMAP[int(x)]) for x in re.split(r"[,–-]", m.group(1))) + "]", text)


def _renum(text):
    for a, b in (("Table 2처럼", "Table 1처럼"), ("(Table 3)", "(Table 2)"), ("(Fig. 2)", "(Fig. 1)"), ("(Fig. 3;", "(Fig. 2;"),
                 ("(Fig. 4)", "(Fig. 3)")):
        text = text.replace(a, b)
    return text


CAP = {"fig2_transition": FIGCAP["fig2_transition"].replace("Fig. 2.", "Fig. 1."),
       "fig3_diffusion": FIGCAP["fig3_diffusion"].replace("Fig. 3.", "Fig. 2."),
       "fig4_window300": FIGCAP["fig4_window300"].replace("Fig. 4.", "Fig. 3."),
       "fig5_recess_spec": FIGCAP["fig5_recess_spec"].replace("Fig. 5.", "Fig. 4."),
       "fig6_factors": FIGCAP["fig6_factors"].replace("Fig. 6.", "Fig. 5.")}
TAB1 = (BL_T2[0].replace("Table 2.", "Table 1."),) + BL_T2[1:]
TAB2_B = (T3_BLIND[0].replace("Table 3.", "Table 2."),) + T3_BLIND[1:]
TAB2_P = ("Table 2. Status of each model part.", ["Part", "Status", "Commit"],
          [r for r in T3_ROWS if not r[0].startswith(("Connection", "Diffusion h_d, fixed"))], [2.6, 3.75, 1.6])
S34_SHARED = BL_S34.replace("recess 허용 합은 청정 표면 7.5 nm(250 °C × 2 h)–11.5 nm(400 °C)이다.",
                            "recess 허용 합은 청정 표면 7.5 nm(250 °C × 2 h)–11.5 nm(400 °C), 산화 표면 3.5–6 nm이다(Fig. 4).") \
                   .replace("인자 순위는 지배 기구(9/15)", "인자 순위(Fig. 5a)는 지배 기구(9/15)") \
                   .replace("1.4 × 10^{−3}이 남는다.", "1.4 × 10^{−3}이 남는다(Fig. 5b).")


def shared_body():
    """sequence of (kind, payload) used by both builders"""
    B = [("h1", "Ⅰ. 서  론")] + [("p", rc(t)) for t in BL_INTRO]
    B += [("h1", "Ⅱ. 모델과 검증 절차"), ("p", rc(BL_S2a)), ("eq", EQ1), ("p", rc(BL_S2b.replace("ASME V&V 10[13]", "ASME V&V 10-2019")))]
    B += [("h1", "Ⅲ. 결  과"), ("h2", "1. 열탄성 모델과 기구 전환"), ("p", rc(_renum(BL_S31))), ("tab", "T1"),
          ("fig", "fig2_transition"), ("h2", "2. 표면확산 항 테스트"), ("p", rc(_renum(BL_S32))), ("fig", "fig3_diffusion"),
          ("h2", "3. Ayoub 변형률과 300 nm 공정창"), ("p", rc(BL_S33)), ("p", rc(_renum(S34_SHARED))),
          ("fig", "fig4_window300"), ("fig", "fig5_recess_spec"), ("fig", "fig6_factors")]
    B += [("h1", "Ⅳ. 한계와 결론"), ("p", rc(_renum(BL_S4))), ("tab", "T2"), ("h1", "REFERENCES")]
    short = {7: REFS[6].replace("J. De Messemaeker, K. Van Sever, Y. W. Tsau, B. Zhang, K. Croes, and E. Beyne,", "J. De Messemaeker et al.,")}
    B += [("ref", f"[{n}] " + short.get(o, REFS[o - 1])) for n, o in enumerate(ORDER, 1)]
    return B


def _single_column_break(doc, after_el):
    """insert a paragraph carrying a one-column sectPr after after_el; make the final section continuous"""
    final = doc.element.body.find(qn("w:sectPr"))
    sp = copy.deepcopy(final)
    cols = sp.find(qn("w:cols"))
    if cols is not None:
        for a in list(cols.attrib):
            del cols.attrib[a]
        cols.set(qn("w:space"), "425")
    p = OxmlElement("w:p"); ppr = OxmlElement("w:pPr"); ppr.append(sp); p.append(ppr)
    after_el.addnext(p)
    t = final.find(qn("w:type"))
    if t is None:
        t = OxmlElement("w:type"); final.insert(0, t)
    t.set(qn("w:val"), "continuous")
    return p


def build_blind():
    d = docx.Document(str(TPL / "서면 심사용 논문 양식.docx"))
    body = d.element.body
    hdr = d.tables[0]

    def set_text(p, text, cite=False):
        for r in list(p.runs):
            r._element.getparent().remove(r._element)
        fill(p, text, "Times New Roman", None, east="한양신명조", cite=cite)
    seen_body, done, done_flags = 0, set(), set()
    for c in hdr._cells:
        if id(c._tc) in done:
            continue
        done.add(id(c._tc))
        for p in list(c.paragraphs):
            n = p.style.name; tx = p.text.strip()
            if n == "논문번호":
                if "label" not in done_flags:
                    set_text(p, "학부생 논문경진대회 서면 심사용"); done_flags.add("label")
                else:
                    set_text(p, "")
            elif n == "한글제목":
                set_text(p, TITLE_KO)
            elif n == "영문제목":
                set_text(p, "(" + " ".join(TITLE_EN_LINES) + ")")
            elif n == "요약본문":
                seen_body += 1
                set_text(p, ABSTRACT_KO if seen_body == 1 else ABSTRACT_EN)
            elif "Keywords" in tx:
                set_text(p, "      Keywords : " + KEYWORDS)
    # header table: not floating, no repeated header rows; title block in its own one-column section
    tblPr = hdr._tbl.tblPr
    for e in tblPr.findall(qn("w:tblpPr")):
        tblPr.remove(e)
    for trPr in hdr._tbl.iter(qn("w:trPr")):
        for e in trPr.findall(qn("w:tblHeader")):
            trPr.remove(e)
    for tr in list(hdr._tbl.findall(qn("w:tr")))[1:]:          # drop trailing rows that are now empty
        if not "".join(t.text or "" for t in tr.iter(qn("w:t"))).strip():
            hdr._tbl.remove(tr)
    clear_after(body, hdr._tbl)
    _single_column_break(d, hdr._tbl)

    def p_(style, text, cite=True):
        p = d.add_paragraph(style=style)
        fill(p, text, "Times New Roman", None, east="한양신명조", cite=cite)
        if style == "Body Text":
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        return p
    for kind, x in shared_body():
        if kind == "h1":
            p_("각 장 제목", x)
        elif kind == "h2":
            p_("각 절 제목", x)
        elif kind == "p":
            p_("Body Text", x)
        elif kind == "eq":
            for k_, line in enumerate(EQ_LINES):
                eq = d.add_paragraph(style="수식번호")
                eq.paragraph_format.tab_stops.add_tab_stop(COLW - Cm(0.1), WD_TAB_ALIGNMENT.RIGHT)
                fill(eq, line + ("\t(1)" if k_ == 0 else ""), "Times New Roman", 9, east="한양신명조")
        elif kind == "fig":
            p = d.add_paragraph(style="Body Text"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Pt(0); p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(str(FIG / f"{x}.png"), width=COLW)
            c = p_("그림/표 제목", CAP[x]); c.paragraph_format.space_after = Pt(6)
        elif kind == "tab":
            spec = TAB1 if x == "T1" else TAB2_B
            c = p_("그림/표 제목", spec[0]); c.paragraph_format.keep_with_next = True
            t = add_table(d, spec, size=7.0); _no_split(t)
            sp = d.add_paragraph(style="Body Text"); sp.paragraph_format.line_spacing = 0.6
        elif kind == "ref":
            p_("참고문헌내용", x, cite=False)
    cp = d.core_properties
    for k in ("author", "last_modified_by", "title", "subject", "keywords", "comments", "category"):
        setattr(cp, k, "")
    d.save(str(OUT_B))
    _scrub_app(OUT_B)


def _no_split(t):
    """keep table rows together (cantSplit + keep_with_next on all but last row)"""
    rows = t.rows
    for i, row in enumerate(rows):
        trPr = row._tr.get_or_add_trPr()
        e = OxmlElement("w:cantSplit"); trPr.append(e)
        if i < len(rows) - 1:
            for c in row.cells:
                for p in c.paragraphs:
                    p.paragraph_format.keep_with_next = True


def _scrub_app(path):
    """blank Company/Manager in docProps/app.xml (identifying metadata)"""
    tmp = path.with_suffix(".tmp")
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/app.xml":
                s = data.decode("utf-8")
                s = re.sub(r"<Company>.*?</Company>", "<Company></Company>", s, flags=re.S)
                s = re.sub(r"<Manager>.*?</Manager>", "<Manager></Manager>", s, flags=re.S)
                data = s.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(str(tmp), str(path))


if __name__ == "__main__":
    build_proceedings(); print("ok", OUT_P.name)
    build_blind(); print("ok", OUT_B.name)
