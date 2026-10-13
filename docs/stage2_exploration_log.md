# Stage 2 탐색 로그 (모든 런과 결정, 이유 포함)

규칙(PI, 2026-10-13): 보정은 보정 데이터에서만; held-out 비교 전에 `docs/stage2_vv_plan.md`(고정 파라미터·통과 규칙) 커밋; ANSYS는 한 번에 하나; 모든 런·결정을 여기에 적는다. 구조는 ASME V&V 10-2019(검증 → 보정 → 검증(validation) → 예측) 순서.
사전등록: `docs/stage2_baseline_preregistration.md` (33a8f5c). 코드: `src/stage2/baseline.py`, `stage2_runs.py`.
런 기록은 `results/<ID>/record.json`. u 정의: u_c50(중앙 50 % 면적 평균 − AFM 시야 유전체 평균, 주), u_ctr(중심 − 셀 가장자리), u_full(패드 전체 평균 − 시야).

## 0. 크기 선택 (PI 지시)
- 실측이 가장 많은 크기는 **0.5–0.6 µm**다: imec 0.54 µm u(T) 100–400 °C(DM2023 Fig 1), imec bulge-out 분포(하부 패드 400–600 nm), IRPS 2026 recess 분포(250–700 nm 피치), Lhostis 2024 ρc(400–720 nm). 따라서 "선택 크기" = **0.54 µm(imec 공정)**이고 300 nm는 검증된 모델의 예측이다. NYCU 1 µm와 Ayoub 300 nm는 보조 검증.

## 1. 검증(verification) — SV 그룹
- SV01 기준(0.54 µm 2D, 셀 3w, 40 요소/반경), SV02 메시 ×2, SV03 셀 6w, SV04 3D 등방(2D 대비), SV05 3.06 µm film-limit 해석 비교, SV06/SV07 라이너 50 nm 유무(R42와 같은 물리 + 중간 유전체값).
- 통과 기준(사전): 메시 ×2 Δ < 2 %, 셀 6w Δ < 2 %, 3D−2D < 3 %, film-limit은 FEM이 u_film의 0.85–1.05 안(Step 13: 9 µm에서 FEM > film 1.0 nm는 기판 탄성 때문).

## 2. 런 로그 (자동 기록)
- 2026-10-13 02:19 **SV01** (SV) imec 0.54 2D Hill, cell 3w, refine 1 (verification base) -> exit 0, wall 18 s, LS ok True; du_c50 2.054 | du_ctr 2.610 | du_full 1.793 nm
- 2026-10-13 02:20 **SV02** (SV) imec 0.54 2D Hill, refine 2 (mesh check) -> exit 0, wall 21 s, LS ok True; du_c50 2.055 | du_ctr 2.610 | du_full 1.794 nm
- 2026-10-13 02:20 **SV03** (SV) imec 0.54 2D Hill, cell 6w (cell check) -> exit 0, wall 18 s, LS ok True; du_c50 2.442 | du_ctr 2.814 | du_full 2.182 nm
- 2026-10-13 02:20 **SV05** (SV) imec 3.06 2D Hill (film-limit analytic check) -> exit 0, wall 18 s, LS ok True; du_c50 6.008 | du_ctr 6.728 | du_full 5.280 nm
- 2026-10-13 02:20 **SV06** (SV) NYCU 1 um 2D Hill, taper 7.6, Ta 50 (liner implementation check vs R42) -> exit 0, wall 18 s, LS ok True; du_c50 1.982 | du_ctr 2.522 | du_full 1.730 nm
- 2026-10-13 02:21 **SV07** (SV) NYCU 1 um 2D Hill, taper 7.6, NO liner (= R42 physics with E 68/a 0.75) -> exit 0, wall 18 s, LS ok True; du_c50 1.959 | du_ctr 2.469 | du_full 1.722 nm
- 2026-10-13 02:21 **SV04** (SV) imec 0.54 3D iso Hill, cell 3w (3D-vs-2D check) -> exit 0, wall 40 s, LS ok True; du_c50 2.271 | du_ctr 2.676 | du_full 2.007 nm
- 2026-10-13 02:22 **SV08** (SV) imec 0.54 2D Hill, cell 9w (cell check) -> exit 0, wall 18 s, LS ok True; du_c50 2.542 | du_ctr 2.834 | du_full 2.283 nm
- 2026-10-13 02:23 **SV09** (SV) imec 0.54 2D Hill, cell 12w (cell check) -> exit 0, wall 18 s, LS ok True; du_c50 2.582 | du_ctr 2.838 | du_full 2.323 nm
- 2026-10-13 02:23 **SV10** (SV) imec 0.54 2D Hill, cell 20w (cell check) -> exit 0, wall 19 s, LS ok True; du_c50 2.617 | du_ctr 2.840 | du_full 2.358 nm
- 2026-10-13 02:23 **SV11** (SV) imec 3.06 2D Hill, cell 6w (cell check large pad) -> exit 0, wall 18 s, LS ok True; du_c50 6.116 | du_ctr 6.732 | du_full 5.391 nm

### 결정 1 (02:25) — 셀 크기
- 0.54 µm 2D 셀 수렴(du_c50 / du_ctr, nm): 3w 2.054/2.610, 6w 2.442/2.814, 9w 2.542/2.834, 12w 2.582/2.838, 20w 2.617/2.840. du_ctr는 9w에서 수렴(< 0.2 %). du_c50은 AFM 시야(±4 µm) 기준면이 셀에 잘려서 셀과 함께 커지며 12w→20w +1.3 %(< 2 %).
- 이유: bonded 측벽이 패드 주변 유전체 표면을 끌어올리므로, 작은 셀은 기준면이 올라간 영역만 포함해 u를 과소평가한다. 메시 ×2는 0.05 %.
- 결정: 모든 2D 런은 셀 12w(2D라 비용 없음). 3D는 12w + 성긴 원거리 격자(grow 1.5, h_max 1.0 w)로 노드 한도 안에 둔다. 3D−2D 비교는 같은 셀(SV13 vs SV09)로 다시 판정한다. SV01–SV04(3w)는 검증 기록으로만 남긴다.
- 2026-10-13 02:24 **SV12** (SV) imec 0.54 3D iso Hill, cell 9w coarse far field (3D cell check) -> exit 0, wall 49 s, LS ok True; du_c50 2.579 | du_ctr 2.838 | du_full 2.317 nm
- 2026-10-13 02:25 **SV13** (SV) imec 0.54 3D iso Hill, cell 12w coarse far field (3D cell check) -> exit 0, wall 44 s, LS ok True; du_c50 2.599 | du_ctr 2.840 | du_full 2.336 nm
- 2026-10-13 02:26 **S01** (A) NYCU 9 um calib E59 a0.5 taper7.6 cell12w -> exit 0, wall 19 s, LS ok True; du_c50 7.105 | du_ctr 7.599 | du_full 6.223 nm
- 2026-10-13 02:26 **S02** (A) NYCU 9 um calib E59 a0.5 taper12.8 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 7.065 | du_ctr 7.572 | du_full 6.136 nm
- 2026-10-13 02:26 **S03** (A) NYCU 9 um calib E59 a0.5 taper18 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 7.020 | du_ctr 7.544 | du_full 6.042 nm

### 검증(verification) 요약 (02:30, SV01–SV13; 표 `results/stage2/verification.csv`)
- 메시 ×2: +0.02 % (통과). 셀: 12w→20w +1.3 % (du_c50), du_ctr +0.1 % (통과, 12w 채택). 3D 등방 vs 2D(같은 셀 12w, 3D는 성긴 원거리 격자): du_c50 +0.7 %, du_ctr +0.1 % (통과). 3.06 µm 셀 6w vs 3w: 보고.
- film-limit 해석 점검(3.06 µm, 완전 구속 박막 식 5.32 nm)에 대해 FEM du_ctr 6.73(+26 %)으로 사전 띠(−15…+5 %)를 벗어난다. Step 13의 R40(9 µm, +16 %)과 같은 방향이며 메시·셀·3D 모두 수렴하므로 코드 오류가 아니라 모델 형태(패드 주변 유전체·기판의 탄성 변형이 박막 식에 없음)의 차이로 기록한다. 보정에 영향 없음(보정은 FEM 값으로 한다).
- 라이너 50 nm(1 µm, 2D): u +1.2 %. 작다. 유지.
- 2026-10-13 02:27 **S04** (A) NYCU 9 um calib E59 a1 taper7.6 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 6.950 | du_ctr 7.436 | du_full 6.083 nm
- 2026-10-13 02:27 **S05** (A) NYCU 9 um calib E59 a1 taper12.8 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 6.911 | du_ctr 7.410 | du_full 5.998 nm
- 2026-10-13 02:27 **S06** (A) NYCU 9 um calib E59 a1 taper18 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 6.867 | du_ctr 7.382 | du_full 5.906 nm
- 2026-10-13 02:27 **S07** (A) NYCU 9 um calib E68 a0.5 taper7.6 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 7.151 | du_ctr 7.639 | du_full 6.281 nm
- 2026-10-13 02:28 **S08** (A) NYCU 9 um calib E68 a0.5 taper12.8 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 7.114 | du_ctr 7.614 | du_full 6.195 nm
- 2026-10-13 02:28 **S09** (A) NYCU 9 um calib E68 a0.5 taper18 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 7.072 | du_ctr 7.587 | du_full 6.102 nm
- 2026-10-13 02:28 **S10** (A) NYCU 9 um calib E68 a1 taper7.6 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 6.995 | du_ctr 7.474 | du_full 6.140 nm
- 2026-10-13 02:29 **S11** (A) NYCU 9 um calib E68 a1 taper12.8 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 6.958 | du_ctr 7.449 | du_full 6.055 nm
- 2026-10-13 02:29 **S12** (A) NYCU 9 um calib E68 a1 taper18 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 6.917 | du_ctr 7.423 | du_full 5.965 nm
- 2026-10-13 02:29 **S13** (A) NYCU 9 um calib E77 a0.5 taper7.6 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 7.187 | du_ctr 7.670 | du_full 6.327 nm
- 2026-10-13 02:30 **S14** (A) NYCU 9 um calib E77 a0.5 taper12.8 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 7.152 | du_ctr 7.645 | du_full 6.242 nm
- 2026-10-13 02:30 **S15** (A) NYCU 9 um calib E77 a0.5 taper18 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 7.113 | du_ctr 7.620 | du_full 6.149 nm
- 2026-10-13 02:30 **S16** (A) NYCU 9 um calib E77 a1 taper7.6 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 7.028 | du_ctr 7.502 | du_full 6.184 nm
- 2026-10-13 02:30 **S17** (A) NYCU 9 um calib E77 a1 taper12.8 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 6.994 | du_ctr 7.478 | du_full 6.101 nm
- 2026-10-13 02:31 **S18** (A) NYCU 9 um calib E77 a1 taper18 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 6.955 | du_ctr 7.453 | du_full 6.010 nm
- 2026-10-13 02:31 **S19** (A) NYCU 3 um calib E59 a0.5 taper7.6 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 5.047 | du_ctr 5.888 | du_full 4.434 nm
- 2026-10-13 02:31 **S20** (A) NYCU 3 um calib E59 a0.5 taper12.8 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 4.881 | du_ctr 5.682 | du_full 4.246 nm
- 2026-10-13 02:32 **S21** (A) NYCU 3 um calib E59 a0.5 taper18 cell12w -> exit 0, wall 19 s, LS ok True; du_c50 4.697 | du_ctr 5.461 | du_full 4.043 nm
- 2026-10-13 02:32 **S22** (A) NYCU 3 um calib E59 a1 taper7.6 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 4.918 | du_ctr 5.741 | du_full 4.318 nm
- 2026-10-13 02:32 **S23** (A) NYCU 3 um calib E59 a1 taper12.8 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 4.756 | du_ctr 5.539 | du_full 4.135 nm
- 2026-10-13 02:33 **S24** (A) NYCU 3 um calib E59 a1 taper18 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 4.577 | du_ctr 5.324 | du_full 3.938 nm
- 2026-10-13 02:33 **S25** (A) NYCU 3 um calib E68 a0.5 taper7.6 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 5.115 | du_ctr 5.981 | du_full 4.472 nm
- 2026-10-13 02:33 **S26** (A) NYCU 3 um calib E68 a0.5 taper12.8 cell12w -> exit 0, wall 19 s, LS ok True; du_c50 4.944 | du_ctr 5.774 | du_full 4.277 nm
- 2026-10-13 02:34 **S27** (A) NYCU 3 um calib E68 a0.5 taper18 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 4.755 | du_ctr 5.552 | du_full 4.068 nm
- 2026-10-13 02:34 **S28** (A) NYCU 3 um calib E68 a1 taper7.6 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 4.987 | du_ctr 5.835 | du_full 4.358 nm
- 2026-10-13 02:34 **S29** (A) NYCU 3 um calib E68 a1 taper12.8 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 4.821 | du_ctr 5.632 | du_full 4.169 nm
- 2026-10-13 02:34 **S30** (A) NYCU 3 um calib E68 a1 taper18 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 4.637 | du_ctr 5.415 | du_full 3.966 nm
- 2026-10-13 02:35 **S31** (A) NYCU 3 um calib E77 a0.5 taper7.6 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 5.174 | du_ctr 6.062 | du_full 4.503 nm
- 2026-10-13 02:35 **S32** (A) NYCU 3 um calib E77 a0.5 taper12.8 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 5.000 | du_ctr 5.855 | du_full 4.305 nm
- 2026-10-13 02:35 **S33** (A) NYCU 3 um calib E77 a0.5 taper18 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 4.807 | du_ctr 5.632 | du_full 4.091 nm
- 2026-10-13 02:36 **S34** (A) NYCU 3 um calib E77 a1 taper7.6 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 5.048 | du_ctr 5.917 | du_full 4.391 nm
- 2026-10-13 02:36 **S35** (A) NYCU 3 um calib E77 a1 taper12.8 cell12w -> exit 0, wall 19 s, LS ok True; du_c50 4.878 | du_ctr 5.714 | du_full 4.198 nm
- 2026-10-13 02:36 **S36** (A) NYCU 3 um calib E77 a1 taper18 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 4.691 | du_ctr 5.496 | du_full 3.990 nm
- 2026-10-13 02:37 **S37** (A) imec 3.06 um calib E70 a2 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 6.506 | du_ctr 7.199 | du_full 5.727 nm
- 2026-10-13 02:37 **S38** (A) imec 3.06 um calib E70 a5.2 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 5.452 | du_ctr 6.055 | du_full 4.780 nm
- 2026-10-13 02:37 **S39** (A) imec 3.06 um calib E95 a2 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 6.654 | du_ctr 7.319 | du_full 5.870 nm
- 2026-10-13 02:37 **S40** (A) imec 3.06 um calib E95 a5.2 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 5.573 | du_ctr 6.140 | du_full 4.908 nm
- 2026-10-13 02:38 **S41** (A) imec 3.06 um calib E120 a2 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 6.747 | du_ctr 7.389 | du_full 5.959 nm
- 2026-10-13 02:38 **S42** (A) imec 3.06 um calib E120 a5.2 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 5.639 | du_ctr 6.172 | du_full 4.979 nm
- 2026-10-13 02:38 **S43** (A) imec 1.8 um calib E70 a2 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 5.404 | du_ctr 5.947 | du_full 4.792 nm
- 2026-10-13 02:39 **S44** (A) imec 1.8 um calib E70 a5.2 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 4.483 | du_ctr 4.951 | du_full 3.964 nm
- 2026-10-13 02:39 **S45** (A) imec 1.8 um calib E95 a2 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 5.586 | du_ctr 6.137 | du_full 4.927 nm
- 2026-10-13 02:39 **S46** (A) imec 1.8 um calib E95 a5.2 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 4.660 | du_ctr 5.127 | du_full 4.104 nm
- 2026-10-13 02:40 **S47** (A) imec 1.8 um calib E120 a2 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 5.715 | du_ctr 6.268 | du_full 5.018 nm
- 2026-10-13 02:40 **S48** (A) imec 1.8 um calib E120 a5.2 cell12w -> exit 0, wall 18 s, LS ok True; du_c50 4.780 | du_ctr 5.242 | du_full 4.194 nm
- 2026-10-13 02:41 **E29** (E) contact 0.54 um r2 T300 ELASTIC reference -> exit 0: results not readable (KeyError: np.int64(4235))

### 보정(calibration) 결과 (02:45; `results/stage2/calibration_grid.csv`, `adopted.json`)
- **NYCU**: 최소 J = 2.79 at E_SiO2 59 GPa, α_SiO2 1.0 ppm/K, 테이퍼 18° — **세 파라미터 모두 범위 끝(bound-limited)**. 9 µm 6.87(측정 6.4 ± 0.4), 3 µm 4.58(4.1 ± 0.4): 둘 다 2σ 안 → 보정 통과. 모델이 두 큰 패드를 여전히 +7…+12 % 과대예측하는 경향이고, 범위를 넓히지 않는다(규칙). E_SiO2 민감도는 작다(59→77 GPa: +1.3 %).
- **imec**: 최소 J = 17.4 at E_SiCN 95 GPa, α_SiCN 2.0 ppm/K(α는 경계). E_SiCN은 식별되지 않는다(70/95/120 GPa에서 J 18.5/17.4/17.6). 1.80 µm 4점 모두 2σ 안. **3.06 µm는 200 °C 과대(3.11 vs 2.70), 300·400 °C 과소(4.88 vs 6.05, 6.65 vs 7.85) → 보정 실패 기록.** 측정 곡선이 200 °C 이후 초선형(100→200 °C +1.15 nm, 200→300 °C +3.35 nm)이라 선형 탄성 모델이 따라갈 수 없다. 이는 큰 패드의 비탄성(소성: Step 14 C에서 소성이 큰 패드의 u를 키움)으로 보이며, 소성 런 S66(3.06 µm, Okoro 등방, 파라미터 고정)으로 확인한다(보정이 아님).
- 결정 2: 최소 J 조합을 채택(사전 규칙). 보정 실패는 기록하되 범위를 넓히거나 다른 파라미터를 추가하지 않는다. 개정 1회 권리는 검증 결과를 본 뒤 쓴다.

### 결정 3 (02:50) — V3의 테이퍼
- 채택 테이퍼 18°를 1 µm 패드(h 1.5 µm)에 적용하면 바닥 반경 13 nm(거의 원뿔)로 Lin Table 1의 1 µm 부피(0.77 µm³ → 7.6°)와 모순된다. 그래도 커밋된 규칙대로 V3 1차 판정은 18°(S56–S58; 바닥 임계를 lin13과 같은 0.02A로 완화해 생성)로 한다. 부피 일관 7.6°(S56b–S58b)는 **문서화된 대안**으로 함께 보고하되 판정에 쓰지 않는다. 이유: 테이퍼가 범위 끝에 걸린 것은 다른 모델 오차를 흡수한 신호이므로 두 값을 모두 보여야 한다.
- 2026-10-13 02:43 **S51** (B) V1 imec 1.26 2D Hill bonded cell12w [adopted params] -> exit 0, wall 18 s, LS ok True; du_c50 4.761 | du_ctr 5.219 | du_full 4.219 nm
- 2026-10-13 02:43 **S52** (B) V2 imec 0.54 2D Hill bonded cell12w [adopted params] -> exit 0, wall 18 s, LS ok True; du_c50 2.832 | du_ctr 3.112 | du_full 2.550 nm
- 2026-10-13 02:44 **S59** (B) V4 imec 0.54 2D Hill SLIDING control cell12w [adopted params] -> exit 0, wall 18 s, LS ok True; du_c50 4.776 | du_ctr 4.809 | du_full 4.767 nm
- 2026-10-13 02:44 **S49** (A2) NYCU 9 um thickness 0.8 um (Table-1 volume alternative), adopted params cell12w [adopted params] -> exit 0, wall 18 s, LS ok True; du_c50 5.250 | du_ctr 5.524 | du_full 4.586 nm
- 2026-10-13 02:44 **S50** (A2) NYCU 3 um Cu alpha +7 % (30-400 C mean), adopted params cell12w [adopted params] -> exit 0, wall 18 s, LS ok True; du_c50 4.908 | du_ctr 5.710 | du_full 4.220 nm
- 2026-10-13 02:45 **S53** (B) V2 imec 0.54 3D [001] bonded cell 6w cell12w [adopted params] -> exit 0, wall 43 s, LS ok True; du_c50 2.826 | du_ctr 3.081 | du_full 2.556 nm
- 2026-10-13 02:46 **S54** (B) V2 imec 0.54 3D [101] bonded cell 6w cell12w [adopted params] -> exit 0, wall 44 s, LS ok True; du_c50 2.863 | du_ctr 3.126 | du_full 2.571 nm
- 2026-10-13 02:47 **S55** (B) V2 imec 0.54 3D [111] bonded cell 6w cell12w [adopted params] -> exit 0, wall 43 s, LS ok True; du_c50 2.864 | du_ctr 3.118 | du_full 2.570 nm
- 2026-10-13 02:47 **S56** (B) V3 NYCU 1 um 3D [001] bonded cell 6w cell12w [adopted params] -> exit 0, wall 34 s, LS ok True; du_c50 1.785 | du_ctr 2.078 | du_full 1.565 nm
- 2026-10-13 02:48 **S57** (B) V3 NYCU 1 um 3D [101] bonded cell 6w cell12w [adopted params] -> exit 0, wall 34 s, LS ok True; du_c50 1.888 | du_ctr 2.228 | du_full 1.627 nm
- 2026-10-13 02:48 **S58** (B) V3 NYCU 1 um 3D [111] bonded cell 6w cell12w [adopted params] -> exit 0, wall 34 s, LS ok True; du_c50 1.940 | du_ctr 2.317 | du_full 1.655 nm
- 2026-10-13 02:49 **S60** (B) V4 NYCU 1 um 3D [001] SLIDING control cell 6w cell12w [adopted params] -> exit 0, wall 35 s, LS ok True; du_c50 3.656 | du_ctr 3.708 | du_full 3.630 nm
- 2026-10-13 02:49 **S56b** (Balt) V3-alt NYCU 1 um 3D [001] bonded, taper 7.6 (volume-consistent) cell12w [adopted params] -> exit 0, wall 35 s, LS ok True; du_c50 2.098 | du_ctr 2.533 | du_full 1.886 nm
- 2026-10-13 02:50 **S57b** (Balt) V3-alt NYCU 1 um 3D [101] bonded, taper 7.6 cell12w [adopted params] -> exit 0, wall 34 s, LS ok True; du_c50 2.301 | du_ctr 2.783 | du_full 2.045 nm
- 2026-10-13 02:51 **S58b** (Balt) V3-alt NYCU 1 um 3D [111] bonded, taper 7.6 cell12w [adopted params] -> exit 0, wall 34 s, LS ok True; du_c50 2.403 | du_ctr 2.916 | du_full 2.119 nm
- 2026-10-13 02:51 **S64** (D) D NYCU 1 um 2D Hill PLASTIC (Okoro) cell12w [adopted params] -> exit 0, wall 35 s, LS ok True; du_c50 1.871 | du_ctr 2.166 | du_full 1.628 nm, eppl_max 2.80e-03
- 2026-10-13 02:52 **S65** (D) D imec 0.54 2D Hill PLASTIC (Okoro) cell12w [adopted params] -> exit 0, wall 35 s, LS ok True; du_c50 4.786 | du_ctr 5.111 | du_full 4.305 nm, eppl_max 1.48e-01
- 2026-10-13 02:52 **S66** (D) D imec 3.06 2D Hill PLASTIC (Okoro) cell12w [adopted params] -> exit 0, wall 27 s, LS ok True; du_c50 8.727 | du_ctr 8.713 | du_full 7.670 nm, eppl_max 2.61e-02
- 2026-10-13 02:53 **E29** (E) contact 0.54 um r2 T300 ELASTIC reference -> exit 0, wall 44 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=0.438 p=679MPa; T25: Ac/A=0.000 p=0MPa

### 검증(validation) 결과 1차 (03:00; 커밋된 규칙 그대로; `results/stage2/validation.csv`)
- V1 imec 1.26 µm: 100/300/400 °C 통과, **200 °C 실패**(모델 2.22 vs 측정 1.60; 측정 곡선이 200→300 °C에서 초선형). 3/4.
- V2 imec 0.54 µm: **실패**. Hill 2.83 nm @400 °C vs 측정 1.40 ± 0.5 (+100 %); 3방위 2.83–2.86(방위 의존 1 %). 200·300 °C도 실패.
- V3 NYCU 1 µm(테이퍼 18°): 1.79–1.94 vs 2.1 ± 0.4 → **통과**. 대안 7.6°: 2.10–2.40 → 통과.
- V4: sliding 대조군 0.54 µm 4.78(측정 1.4), 1 µm 3.66(측정 2.1) → 둘 다 실패 → 측벽 bonded가 판별됨.
- **VERDICT 1차: NOT VALIDATED** (V2 실패, V1 1점 실패).
- 소성(D, Okoro 등방, 파라미터 고정): 0.54 µm 소성 4.79 vs 탄성 2.83(+69 %, εp,max 0.15) — 작은 패드에서 벌크 항복응력 소성은 u를 **키워** 측정과 더 멀어진다. 3.06 µm 소성 8.73 vs 탄성 6.65 vs 측정 7.85 — 큰 패드의 초선형은 소성 방향과 일치. 1 µm NYCU 소성 1.87 vs 탄성(3D [101]) 1.89: 영향 없음.
- 접촉 시험 E29(탄성, r 2 nm/패드, 300 °C): 접촉면적비 0.44, 평균 압력 679 MPa(탄성이라 상한), 냉각 후 0. 덱·후처리 정상.

### 결정 4 (03:05) — 단 한 번의 문서화된 개정: "고립 패드" → "실험 구조의 배열 피치"
- 근거(모델 외부 사실): imec Fig 1의 패드는 배열 시험 구조에서 측정됐다(DM2023 §II: 200/500 nm → 850 nm 피치, 300/600 nm → 1200 nm 피치, 즉 **피치 ≈ 2 w**; Kim 2020/IRPS: 하부 패드 Cu 밀도 25 % → 정사각 격자 피치 1.77 w). Lin 3 µm 어레이도 3×3, 피치 ≈ 2.2 w(Fig 12). 우리 셀 12w는 "고립 패드 + 먼 기준면"이다. bonded 측벽은 이웃 유전체 표면을 끌어올리므로(셀 수렴 연구: 3w에서 −20 %), 배열에서는 AFM 기준면(패드 사이 유전체)이 함께 올라가 측정 u가 작아진다. 이것은 조정 파라미터가 아니라 **실험 조건(피치)의 반영**이다.
- 개정 내용: imec 데이터(보정 3.06/1.80, 검증 1.26/0.54) 모두 셀 = 피치 2 w(2D 등면적 원통 셀: 2.26 w; 3D 정사각 셀 2.0 w, 평벽 = 주기 대칭). NYCU 3 µm 어레이(4.1 nm)는 셀 2.5 w(피치 2.2 w 등면적). NYCU 9 µm·1 µm는 고립(12w) 유지. 기준면 = 셀 안 유전체 표면 평균(= 배열 안 AFM 기준면).
- 재보정 → 재검증을 같은 규칙으로 다시 하고 **두 결과를 모두 보고**한다. 피치 가정(2 w)의 민감도로 1.7 w와 3 w도 돌린다(보고용).
- 소성은 채택하지 않는다: 벌크 항복(Okoro)은 0.54 µm를 더 과대예측하고, sub-µm Cu의 항복은 벌크보다 훨씬 높다(Tsau 2022 §3.1 인용: 수백 nm Cu 항복은 1.28 MPa보다 2자릿수 큼; Ayoub 0.32 µm 패드 σy 140–190 MPa는 bonded 모서리 응력 577 MPa보다 낮지만 체적평균 응력 130 MPa보다 높음). 큰 패드(≥ 3 µm)의 초선형은 소성으로 설명 가능함을 보고에 적는다.
- 2026-10-13 02:56 **S81** (Ar) REV1 imec 3.06 um calib E70 a2 cell2.26w -> exit 0, wall 18 s, LS ok True; du_c50 6.096 | du_ctr 7.172 | du_full 5.309 nm
- 2026-10-13 02:56 **S82** (Ar) REV1 imec 3.06 um calib E70 a5.2 cell2.26w -> exit 0, wall 18 s, LS ok True; du_c50 5.104 | du_ctr 6.031 | du_full 4.426 nm
- 2026-10-13 02:57 **S83** (Ar) REV1 imec 3.06 um calib E95 a2 cell2.26w -> exit 0, wall 18 s, LS ok True; du_c50 6.235 | du_ctr 7.280 | du_full 5.445 nm
- 2026-10-13 02:57 **S84** (Ar) REV1 imec 3.06 um calib E95 a5.2 cell2.26w -> exit 0, wall 18 s, LS ok True; du_c50 5.221 | du_ctr 6.106 | du_full 4.550 nm
- 2026-10-13 02:57 **S85** (Ar) REV1 imec 3.06 um calib E120 a2 cell2.26w -> exit 0, wall 19 s, LS ok True; du_c50 6.323 | du_ctr 7.337 | du_full 5.530 nm
- 2026-10-13 02:58 **S86** (Ar) REV1 imec 3.06 um calib E120 a5.2 cell2.26w -> exit 0, wall 18 s, LS ok True; du_c50 5.287 | du_ctr 6.129 | du_full 4.623 nm
- 2026-10-13 02:58 **S87** (Ar) REV1 imec 1.8 um calib E70 a2 cell2.26w -> exit 0, wall 18 s, LS ok True; du_c50 4.668 | du_ctr 5.827 | du_full 4.050 nm
- 2026-10-13 02:58 **S88** (Ar) REV1 imec 1.8 um calib E70 a5.2 cell2.26w -> exit 0, wall 18 s, LS ok True; du_c50 3.864 | du_ctr 4.846 | du_full 3.339 nm
- 2026-10-13 02:59 **S89** (Ar) REV1 imec 1.8 um calib E95 a2 cell2.26w -> exit 0, wall 18 s, LS ok True; du_c50 4.856 | du_ctr 5.996 | du_full 4.190 nm
- 2026-10-13 02:59 **S90** (Ar) REV1 imec 1.8 um calib E95 a5.2 cell2.26w -> exit 0, wall 18 s, LS ok True; du_c50 4.048 | du_ctr 5.007 | du_full 3.486 nm
- 2026-10-13 02:59 **S91** (Ar) REV1 imec 1.8 um calib E120 a2 cell2.26w -> exit 0, wall 18 s, LS ok True; du_c50 4.989 | du_ctr 6.107 | du_full 4.286 nm
- 2026-10-13 02:59 **S92** (Ar) REV1 imec 1.8 um calib E120 a5.2 cell2.26w -> exit 0, wall 18 s, LS ok True; du_c50 4.178 | du_ctr 5.108 | du_full 3.587 nm
- 2026-10-13 03:00 **S93** (Ar) REV1 NYCU 3 um calib E59 a0.5 taper7.6 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.601 | du_ctr 5.763 | du_full 3.984 nm
- 2026-10-13 03:00 **S94** (Ar) REV1 NYCU 3 um calib E59 a0.5 taper12.8 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.498 | du_ctr 5.586 | du_full 3.860 nm
- 2026-10-13 03:00 **S95** (Ar) REV1 NYCU 3 um calib E59 a0.5 taper18 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.374 | du_ctr 5.392 | du_full 3.717 nm
- 2026-10-13 03:01 **S96** (Ar) REV1 NYCU 3 um calib E59 a1 taper7.6 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.484 | du_ctr 5.618 | du_full 3.880 nm
- 2026-10-13 03:01 **S97** (Ar) REV1 NYCU 3 um calib E59 a1 taper12.8 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.383 | du_ctr 5.446 | du_full 3.760 nm
- 2026-10-13 03:01 **S98** (Ar) REV1 NYCU 3 um calib E59 a1 taper18 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.263 | du_ctr 5.257 | du_full 3.621 nm
- 2026-10-13 03:02 **S99** (Ar) REV1 NYCU 3 um calib E68 a0.5 taper7.6 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.679 | du_ctr 5.849 | du_full 4.032 nm
- 2026-10-13 03:02 **S100** (Ar) REV1 NYCU 3 um calib E68 a0.5 taper12.8 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.571 | du_ctr 5.672 | du_full 3.900 nm
- 2026-10-13 03:02 **S101** (Ar) REV1 NYCU 3 um calib E68 a0.5 taper18 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.441 | du_ctr 5.476 | du_full 3.750 nm
- 2026-10-13 03:02 **S102** (Ar) REV1 NYCU 3 um calib E68 a1 taper7.6 cell2.5w -> exit 0, wall 19 s, LS ok True; du_c50 4.563 | du_ctr 5.706 | du_full 3.929 nm
- 2026-10-13 03:03 **S103** (Ar) REV1 NYCU 3 um calib E68 a1 taper12.8 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.458 | du_ctr 5.532 | du_full 3.801 nm
- 2026-10-13 03:03 **S104** (Ar) REV1 NYCU 3 um calib E68 a1 taper18 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.331 | du_ctr 5.341 | du_full 3.655 nm
- 2026-10-13 03:03 **S105** (Ar) REV1 NYCU 3 um calib E77 a0.5 taper7.6 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.749 | du_ctr 5.925 | du_full 4.073 nm
- 2026-10-13 03:04 **S106** (Ar) REV1 NYCU 3 um calib E77 a0.5 taper12.8 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.636 | du_ctr 5.747 | du_full 3.935 nm
- 2026-10-13 03:04 **S107** (Ar) REV1 NYCU 3 um calib E77 a0.5 taper18 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.500 | du_ctr 5.550 | du_full 3.778 nm
- 2026-10-13 03:04 **S108** (Ar) REV1 NYCU 3 um calib E77 a1 taper7.6 cell2.5w -> exit 0, wall 19 s, LS ok True; du_c50 4.634 | du_ctr 5.782 | du_full 3.972 nm
- 2026-10-13 03:05 **S109** (Ar) REV1 NYCU 3 um calib E77 a1 taper12.8 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.524 | du_ctr 5.609 | du_full 3.838 nm
- 2026-10-13 03:05 **S110** (Ar) REV1 NYCU 3 um calib E77 a1 taper18 cell2.5w -> exit 0, wall 18 s, LS ok True; du_c50 4.391 | du_ctr 5.416 | du_full 3.685 nm
- 2026-10-13 03:06 **S111** (Br) REV1 V1 imec 1.26 2D Hill bonded cell2.26w [adopted_rev] -> exit 0, wall 18 s, LS ok True; du_c50 4.037 | du_ctr 5.110 | du_full 3.440 nm

### 개정 1 재보정 (03:15; `results/stage2/calibration_grid_Ar.csv`, `adopted_rev.json`)
- NYCU(9 µm 고립 12w 재사용 + 3 µm 배열 셀 2.5w): 채택 불변 E 59 / α 1.0 / 테이퍼 18°(모두 경계), J 1.53. 3 µm 4.26 vs 4.1 ± 0.4(개선, 고립 셀 4.58).
- imec(셀 2.26w): 채택 **E_SiCN 120 GPa(경계), α_SiCN 2.0(경계)**, J 23.2. 1.80 µm 4점 통과(5.0 vs 5.4 @400). 3.06 µm 300·400 °C 과소(4.64/6.05, 6.32/7.85) → 보정 실패 유지(초선형 측정). E가 경계에 걸린 이유: 배열 셀에서는 유전체가 뻣뻣할수록 u가 커져(이웃 구속이 Poisson 밀어올림을 키움) 큰 패드의 과소를 줄이려는 방향. 범위를 넓히지 않는다.
- 코드 사고 기록: 패치 실수로 `adopted.json`·`calibration_grid.csv`가 잠시 덮어써졌고 git에서 복원했다(b33b106 상태). 개정 결과는 `_rev`/`_Ar` 파일에만 쓴다.
- 2026-10-13 03:07 **S112** (Br) REV1 V2 imec 0.54 2D Hill bonded cell2.26w [adopted_rev] -> exit 0, wall 18 s, LS ok True; du_c50 2.039 | du_ctr 2.697 | du_full 1.725 nm
- 2026-10-13 03:07 **S113** (Br) REV1 V2 imec 0.54 3D [001] bonded cell2.0w [adopted_rev] -> exit 0, wall 30 s, LS ok True; du_c50 2.264 | du_ctr 2.786 | du_full 1.956 nm
- 2026-10-13 03:08 **S114** (Br) REV1 V2 imec 0.54 3D [101] bonded cell2.0w [adopted_rev] -> exit 0, wall 30 s, LS ok True; du_c50 2.200 | du_ctr 2.695 | du_full 1.884 nm
- 2026-10-13 03:08 **S115** (Br) REV1 V2 imec 0.54 3D [111] bonded cell2.0w [adopted_rev] -> exit 0, wall 31 s, LS ok True; du_c50 2.175 | du_ctr 2.652 | du_full 1.859 nm
- 2026-10-13 03:08 **S116** (Br) REV1 V4 imec 0.54 2D Hill SLIDING cell2.26w [adopted_rev] -> exit 0, wall 18 s, LS ok True; du_c50 4.841 | du_ctr 4.874 | du_full 4.836 nm
- 2026-10-13 03:09 **S117** (Br) REV1 pitch sensitivity 1.7w (2D cell 1.92w) [adopted_rev] -> exit 0, wall 18 s, LS ok True; du_c50 1.838 | du_ctr 2.490 | du_full 1.530 nm
- 2026-10-13 03:09 **S118** (Br) REV1 pitch sensitivity 3w (2D cell 3.39w) [adopted_rev] -> exit 0, wall 18 s, LS ok True; du_c50 2.410 | du_ctr 2.996 | du_full 2.095 nm

### 검증(validation) 결과 2차 — 개정 1 (03:25; `results/stage2/validation_rev1.csv`)
- V1 imec 1.26 µm: 100/200 °C 통과, **300/400 °C 실패**(2.96/3.65, 4.04/5.00 → 이번엔 과소). 2/4.
- V2 imec 0.54 µm: 100/200 °C 통과(0.41/0.25, 0.95/0.60), **300/400 °C 실패**(1.50/1.00, 2.04/1.40). 3방위 2.18–2.26 @400. 전체 평균 정의(du_full)로는 1.73.
- V3·V4 불변(통과, 판별 성립). **VERDICT 2차: NOT VALIDATED.**
- 피치 민감도(0.54 µm, 400 °C): 1.7 w 1.84, 2 w 2.04, 3 w 2.41, 고립 2.83 nm. 측정 1.40은 피치 1.7 w보다도 작다.
- 해석: 개정 1은 과대예측을 2.0배 → 1.46배로 줄였지만 측정의 크기 의존(0.54→1.26 µm ×3.6, 1.26→1.80 ×1.08)은 탄성 연속체 모델(×2.0, ×1.24)로 재현되지 않는다. 특히 측정은 1.26 µm 이상에서 300 °C 이후 초선형(비탄성)이고 0.54 µm는 선형(탄성)이다. 즉 "작은 패드 = 탄성이지만 모델보다 작음, 큰 패드 = 비탄성 추가". 남은 후보: (i) 실제 Cu CD가 설계보다 작음(IRPS Fig 18, 수치 없음), (ii) 소형 패드의 Cu/liner 계면 또는 다결정 효과, (iii) 측정 기준면 정의 차이. 이 중 어느 것도 문헌 수치로 고정할 수 없으므로 더 이상 조정하지 않는다(개정 1회 소진).
- 결정 5: 예측 단계는 **모델 편향 계수**를 명시해 쓴다. 0.54 µm에서 b = u_meas/u_model(개정 1, 400 °C) = 1.40/2.04 = 0.69(범위 0.60–0.93: 측정 ±0.5 반영). 300 nm 예측 u = u_model(0.30)·b, 불확실 구간을 함께 보고한다(ASME V&V 10: 검증 영역 밖 사용 시 모델 불확실도를 명시).
- 2026-10-13 03:13 **S67** (P) P imec 0.30 um 2D Hill bonded cell2.26w [adopted params] [adopted_rev] -> exit 0, wall 18 s, LS ok True; du_c50 1.152 | du_ctr 1.533 | du_full 0.975 nm
- 2026-10-13 03:14 **S68** (P) P imec 0.30 um 3D [001] bonded [adopted params] [adopted_rev] -> exit 0, wall 25 s, LS ok True; du_c50 1.224 | du_ctr 1.505 | du_full 1.057 nm

### Ayoub 300 nm 시험 결과 (03:30; S61–S63; `results/stage2/ayoub_tests.csv`)
- V5(가열 기울기 dε′zz/dT, 30–350 °C; bonded, 캡 60 nm, Ta 13 nm, SiO2 59 GPa/1.0 ppm): 패드 10 모델 **−4.683e-6** vs 측정 **+4.660e-6**; 패드 3 모델 **−7.264e-6** vs 측정 **+7.300e-6**. 부호는 반대, **크기는 두 패드 모두 0.5 % 안**. 규칙(부호 일치)으로는 FAIL(사전 예측대로).
- V6(Δε′zz vs E_z 순위상관): bonded +1.00(측정은 음), sliding −0.90(부호 일치). ε′zz 부호를 뒤집으면 bonded가 −1.00으로 일치.
- 해석(새 발견): Step 12는 H_sign을 **Ayoub의 FEM 곡선**과 비교해 기각했다(1.26배). 여기서는 **측정값**과 비교했고, 실제 적층(캡+라이너)을 넣은 bonded 모델이 두 패드의 측정 기울기 크기를 0.5 %로 맞춘다. E_z 68과 190 GPa 두 패드가 동시에 0.5 %로 맞는 것은 우연이기 어렵다. 즉 "측정 ε′zz의 부호 규약이 우리와 반대"라면 bonded 모델은 Ayoub 가열 데이터를 정량 재현한다. 저자 확인 없이는 확정하지 않는다(Step 12 §5: 논문·학위논문에 부호 정의 없음; LaueTools는 역격자 변형이 실공간의 반대라고 적음). 보고서에는 두 해석을 병기한다.
- H_sw S2: Δ_sw = ε′(sliding) − ε′(bonded) @400 °C = +1.75e-3, 측정 보유 증가 +0.65e-3 → 우리 부호로는 "일관"(부호 같고 크기 충분). **부호가 뒤집힌 경우** 측정 보유 변화는 −0.65e-3이 되어 Δ_sw와 반대 → H_sw 기각. 결론은 부호 규약에 걸려 있다 → "미결, 부호 확인이 선결".
- 냉각 가지 중첩(보고용): 완전 완화 후 재구속 가정의 오프셋 +0.82e-3(일정) vs 측정 +0.28/+0.25/+0.06e-3 → 예측대로 맞지 않음(냉각 중 완화가 계속되는 속도론 필요).
- u(300 nm, 30→400 °C, bonded, 캡·라이너): 패드 10 1.87 nm, 패드 3 1.32 nm; 패드 3 sliding(캡 없음) 7.38 nm.
- 2026-10-13 03:14 **S69** (P) P imec 0.30 um 3D [101] bonded [adopted params] [adopted_rev] -> exit 0, wall 27 s, LS ok True; du_c50 1.258 | du_ctr 1.550 | du_full 1.075 nm
- 2026-10-13 03:15 **S70** (P) P imec 0.30 um 3D [111] bonded [adopted params] [adopted_rev] -> exit 0, wall 27 s, LS ok True; du_c50 1.287 | du_ctr 1.588 | du_full 1.094 nm
- 2026-10-13 03:15 **S71** (P) P imec 0.30 um 2D Hill SLIDING (relaxed-sidewall bound) cell2.26w [adopted params] [adopted_rev] -> exit 0, wall 18 s, LS ok True; du_c50 4.691 | du_ctr 4.711 | du_full 4.688 nm
- 2026-10-13 03:15 **S79** (P) P imec 0.54 um 2D Hill SLIDING cell2.26w (= S116, alias not run) [adopted params] [adopted_rev] -> exit 0, wall 18 s, LS ok True; du_c50 4.841 | du_ctr 4.874 | du_full 4.836 nm
- 2026-10-13 03:16 **S72** (P) P imec 0.54 um 3D [ay3] bonded [adopted params] [adopted_rev] -> exit 0, wall 31 s, LS ok True; du_c50 2.263 | du_ctr 2.786 | du_full 1.955 nm
- 2026-10-13 03:16 **S73** (P) P imec 0.54 um 3D [ay6] bonded [adopted params] [adopted_rev] -> exit 0, wall 30 s, LS ok True; du_c50 2.234 | du_ctr 2.751 | du_full 1.915 nm
- 2026-10-13 03:17 **S74** (P) P imec 0.54 um 3D [ay1] bonded [adopted params] [adopted_rev] -> exit 0, wall 30 s, LS ok True; du_c50 2.212 | du_ctr 2.716 | du_full 1.892 nm
- 2026-10-13 03:17 **S75** (P) P imec 0.54 um 3D [ay4] bonded [adopted params] [adopted_rev] -> exit 0, wall 30 s, LS ok True; du_c50 2.184 | du_ctr 2.668 | du_full 1.867 nm
- 2026-10-13 03:18 **S76** (P) P imec 0.54 um 3D [ay5] bonded [adopted params] [adopted_rev] -> exit 0, wall 30 s, LS ok True; du_c50 2.176 | du_ctr 2.654 | du_full 1.861 nm
- 2026-10-13 03:18 **S77** (P) P imec 0.30 um 3D [ay6] bonded [adopted params] [adopted_rev] -> exit 0, wall 25 s, LS ok True; du_c50 1.249 | du_ctr 1.539 | du_full 1.071 nm
- 2026-10-13 03:19 **S78** (P) P imec 0.30 um 3D [ay4] bonded [adopted params] [adopted_rev] -> exit 0, wall 26 s, LS ok True; du_c50 1.280 | du_ctr 1.579 | du_full 1.089 nm
- 2026-10-13 03:19 **E01** (E) contact 0.54 um r1 nm/pad T250 -> exit 0, wall 38 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T250: Ac/A=1.000 p=226MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:20 **E02** (E) contact 0.54 um r1 nm/pad T300 -> exit 0, wall 40 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=1.000 p=335MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:21 **E03** (E) contact 0.54 um r1 nm/pad T350 -> exit 0, wall 47 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T350: Ac/A=1.000 p=439MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:22 **E04** (E) contact 0.54 um r1 nm/pad T400 -> exit 0, wall 43 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=1.000 p=540MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:22 **E05** (E) contact 0.54 um r2 nm/pad T250 -> exit 0, wall 41 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T250: Ac/A=0.669 p=208MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:23 **E06** (E) contact 0.54 um r2 nm/pad T300 -> exit 1, wall 59 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=1.000 p=246MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:24 **E07** (E) contact 0.54 um r2 nm/pad T350 -> exit 1, wall 58 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T350: Ac/A=1.000 p=349MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:25 **E08** (E) contact 0.54 um r2 nm/pad T400 -> exit 1, wall 62 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=1.000 p=458MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:26 **E09** (E) contact 0.54 um r3 nm/pad T250 -> exit 1, wall 49 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T250: Ac/A=0.438 p=237MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:27 **E10** (E) contact 0.54 um r3 nm/pad T300 -> exit 1, wall 67 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=0.724 p=278MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:28 **E11** (E) contact 0.54 um r3 nm/pad T350 -> exit 1, wall 75 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T350: Ac/A=1.000 p=296MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:30 **E12** (E) contact 0.54 um r3 nm/pad T400 -> exit 1, wall 89 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=1.000 p=402MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:31 **E13** (E) contact 0.54 um r4 nm/pad T250 -> exit 1, wall 59 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T250: Ac/A=0.319 p=251MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:32 **E14** (E) contact 0.54 um r4 nm/pad T300 -> exit 1, wall 86 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=0.544 p=294MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:34 **E15** (E) contact 0.54 um r4 nm/pad T350 -> exit 1, wall 79 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T350: Ac/A=0.819 p=322MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:35 **E16** (E) contact 0.54 um r4 nm/pad T400 -> exit 1, wall 99 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=1.000 p=360MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:36 **E17** (E) contact Lhostis w0.72 um r2 nm/pad T400 -> exit 1, wall 53 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=1.000 p=477MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:38 **E18** (E) contact Lhostis w0.72 um r4 nm/pad T400 -> exit 1, wall 84 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=1.000 p=385MPa; T25: Ac/A=0.000 p=0MPa

### 접촉 런 판정 기준 수정 (03:45)
- E06 이후 "LS ok False"는 `*** ERROR ***`(UY > 1e6: 소성 반복 중 일시 발산)을 치명으로 센 탓이다. 실제로는 MAPDL이 이분법으로 하중 증분을 줄여 같은 substep을 다시 수렴시켰고(e14.out: LS2 substep 5 NOT COMPLETED → COMPLETED), 모든 하중단계가 완료됐다(RUN COMPLETED). 기준을 "하중단계 완료 + 비수렴/종료 메시지 없음 + RUN COMPLETED"로 바꾸고 ERROR 개수는 따로 기록한다. 재해석 없이 record.json의 check 필드만 다시 수집한다.
- 함께 기록: 접촉 후 Cu 소성 변형률이 MISO 표 범위(εp 0.2)를 넘는 적분점이 많다(E14: 38k점). Okoro 벌크 항복(400 °C에서 119 MPa)은 sub-µm Cu에 과소하다(§5.3). 접촉압력은 σy(T) 수준으로 포화하므로 "압력 ≈ 항복응력(하한)"으로 해석한다.
- 2026-10-13 03:39 **E19** (E) contact Lhostis w0.72 um r6 nm/pad T400 -> exit 1, wall 73 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.984 p=335MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:40 **E20** (E) contact Lhostis w0.72 um r8 nm/pad T400 -> exit 1, wall 99 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.774 p=342MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:42 **E21** (E) contact Lhostis w0.4 um r2 nm/pad T400 -> exit 1, wall 81 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=1.000 p=442MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:44 **E22** (E) contact Lhostis w0.4 um r4 nm/pad T400 -> exit 1, wall 125 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.910 p=352MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:47 **E23** (E) contact Lhostis w0.4 um r6 nm/pad T400 -> exit 1, wall 165 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.669 p=346MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:50 **E24** (E) contact Lhostis w0.4 um r8 nm/pad T400 -> exit 1, wall 182 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.510 p=330MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:51 **E25** (E) contact 0.30 um r1 nm/pad T350 -> exit 0, wall 73 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T350: Ac/A=1.000 p=403MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:53 **E26** (E) contact 0.30 um r2 nm/pad T350 -> exit 1, wall 103 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T350: Ac/A=0.949 p=312MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:56 **E27** (E) contact 0.30 um r3 nm/pad T350 -> exit 1, wall 212 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T350: Ac/A=0.698 p=319MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 03:59 **E28** (E) contact 0.30 um r4 nm/pad T350 -> exit 1, wall 157 s, LS ok False; T25: Ac/A=0.000 p=0MPa; T350: Ac/A=0.544 p=317MPa; T25: Ac/A=0.000 p=0MPa

### 연결 단계(접촉) 결과 (04:05; E01-E29; contact_summary.csv, lhostis_test.json)
- 29런 모두 전 하중단계 수렴(E26-E28은 MAPDL exit 1이나 RUN COMPLETED; 일시 발산은 이분법으로 해소).
- 0.54 um, 등방 소성, 배열 셀, 편향 보정 전 u: A_c/A at T. r 1 nm: 250 C부터 1.0. r 2: 0.67(250) -> 1.0(>=300). r 3: 0.44/0.72/1.0/1.0. r 4: 0.32/0.54/0.82/1.0 (250/300/350/400 C).
- 평균 접촉압력 210-540 MPa(소성 포화, T와 함께 증가). 탄성 기준 E29는 679 MPa(상한). 냉각 후 접촉면적 0(마찰 접촉만, 접합 미모델).
- Lhostis 상대 시험: 400 C에서 r 2-8 nm 격자 안에서 A_c가 0에 이르지 않음(720 nm: 1.0/1.0/0.98/0.77, 400 nm: 1.0/0.91/0.67/0.51) -> 사전등록 지표 r_open 미결정. 정성적으로 작은 패드가 recess에 더 민감(Lhostis beta(w) 경향과 같은 방향).
- 0.30 um @350 C: r 1/2/3/4 -> 1.0/0.95/0.70/0.54.
- 해석 주의: 접촉 FEM의 탄성 u는 편향 보정 전(모델/측정 1.46)이므로, 모델 recess r은 실제 recess 약 0.69 r에 해당한다.

## 3. 라운드 X — 한계 점검·보완·수치 조건 테스트 (사후 탐색; 검증 판정은 바꾸지 않음)
- X1 접촉 수치 조건(기준 E06: 0.54 um, r 2 nm, 300 C): 메시 x2, 페널티 vs 증강 라그랑지, FKN 0.1/10, 마찰 0.1/0.5, PLANE182 완전적분, substep 40. 판정: A_c, p_mean 변화 < 5 %이면 견고.
- X3 접촉 단계 항복 크기효과: Okoro x2, x3 (sub-um Cu 항복 상승 문헌 방향).
- X2 0.54 um 과대예측 가설(각각 하나씩, 문헌 범위 밖은 '진단'으로 표기): 유효 CD 0.50/0.46 um(피치 1.08 um 고정), 깊이 0.5 um, 유전체 SiO2 벌크, 라이너 E/10(약한 계면 대리), Cu 강성 T 의존(Chang & Himmel), 테이퍼 5 deg. 1.80 um 대조(X19, X20)로 '작은 패드만 줄이는 인자'인지 구분.
- 2026-10-13 09:39 **X01** (X) X1 contact refine x2 (80 el/radius) -> exit 1, wall 224 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=0.999 p=274MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 09:40 **X02** (X) X1 contact penalty method (KEYOPT(2)=1) -> exit 1, wall 62 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=1.000 p=246MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 09:41 **X03** (X) X1 contact FKN 0.1 -> exit 0, wall 53 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=1.000 p=210MPa; T25: Ac/A=0.049 p=62MPa
- 2026-10-13 09:42 **X04** (X) X1 contact FKN 10 -> exit 0, wall 46 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=1.000 p=299MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 09:43 **X05** (X) X1 contact friction 0.1 -> exit 1, wall 59 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=1.000 p=245MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 09:44 **X06** (X) X1 contact friction 0.5 -> exit 1, wall 58 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=1.000 p=245MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 09:44 **X07** (X) X1 PLANE182 full integration (KEYOPT(1)=0) -> exit 0, wall 40 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=1.000 p=245MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 09:46 **X08** (X) X1 substeps 40 min -> exit 0, wall 91 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=1.000 p=251MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 09:47 **X09** (X) X3 yield x2 (sub-um size effect) -> exit 0, wall 39 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=0.578 p=272MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 09:47 **X10** (X) X3 yield x3 -> exit 0, wall 39 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=0.510 p=281MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 09:48 **X11** (X) X3 yield x3, r 4 nm, 350 C -> exit 0, wall 38 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T350: Ac/A=0.277 p=339MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-13 09:48 **X12** (X) X2 effective CD 0.50 um, pitch 1.08 um -> exit 0, wall 18 s, LS ok True; du_c50 1.976 | du_ctr 2.588 | du_full 1.683 nm
- 2026-10-13 09:49 **X13** (X) X2 effective CD 0.46 um, pitch 1.08 um -> exit 0, wall 18 s, LS ok True; du_c50 1.902 | du_ctr 2.464 | du_full 1.630 nm
- 2026-10-13 09:49 **X14** (X) X2 pad depth 0.5 um -> exit 0, wall 18 s, LS ok True; du_c50 2.007 | du_ctr 2.643 | du_full 1.699 nm
- 2026-10-13 09:49 **X15** (X) X2 dielectric = SiO2 bulk (72 GPa, 0.5 ppm) instead of SiCN -> exit 0, wall 18 s, LS ok True; du_c50 2.030 | du_ctr 2.741 | du_full 1.763 nm
- 2026-10-13 09:49 **X16** (X) X2 compliant liner (Ta E/10 = 18.6 GPa, weak-interface proxy) -> exit 0, wall 18 s, LS ok True; du_c50 2.090 | du_ctr 2.690 | du_full 1.814 nm
- 2026-10-13 09:50 **X17** (X) X2 T-dependent Cu stiffness (Chang & Himmel Hill E(T)) -> exit 0, wall 18 s, LS ok True; du_c50 2.127 | du_ctr 2.800 | du_full 1.784 nm
- 2026-10-13 09:50 **X18** (X) X2 taper 5 deg (TEM-like, wider top) -> exit 0, wall 18 s, LS ok True; du_c50 1.979 | du_ctr 2.587 | du_full 1.657 nm
- 2026-10-13 09:50 **X19** (X) X2 control: 1.80 um with T-dependent Cu stiffness -> exit 0, wall 18 s, LS ok True; du_c50 5.125 | du_ctr 6.228 | du_full 4.389 nm
- 2026-10-13 09:51 **X20** (X) X2 control: 1.80 um dielectric = SiO2 bulk -> exit 0, wall 18 s, LS ok True; du_c50 5.098 | du_ctr 6.352 | du_full 4.427 nm

### 라운드 X 결과 (09:55; X01-X20)
- X1 수치 견고성(기준 E06: A_c 1.000, p 246 MPa): 메시 x2 A_c 0.999 / p 274; 페널티 1.000/246; FKN 0.1 -> 1.000/210, FKN 10 -> 1.000/299; 마찰 0.1/0.5 -> 245/245; 완전적분 245; substep 40 -> 251. 결론: 접촉면적은 조건에 둔감(< 0.1 %), 평균 접촉압력은 접촉강성(FKN)과 메시에 +/-20 % 민감 -> 압력은 '약 +/-20 %'로 보고. 기본 설정(증강 라그랑지, FKN 1, 40 요소/반경) 유지.
- X3 항복 크기효과: 항복 x2 -> A_c 1.00 -> 0.58, x3 -> 0.51 (r 2 nm, 300 C); r 4 nm 350 C에서 x3 -> 0.28(기준 0.82). 결론: 연결 단계의 접촉면적은 sub-um Cu 항복응력(미지, 벌크의 1-3배)에 강하게 의존. 보고서의 A_c 표는 '벌크 항복 = 상한' 으로 표기하고 x3 값을 하한으로 병기.
- X2 0.54 um 과대예측 가설(u_c50 @400 C, 기준 2.039): CD 0.50 -> 1.976(-3 %), CD 0.46 -> 1.902(-7 %), 깊이 0.5 -> 2.007(-2 %), SiO2 벌크 -> 2.030(0 %), 약한 라이너 -> 2.090(+3 %), Cu E(T) -> 2.127(+4 %), 테이퍼 5 deg -> 1.979(-3 %). 1.80 um 대조: E(T) 5.125(+3 %), SiO2 5.098(+2 %). 결론: 어떤 단일 기하·재료 가설도 +46 %를 설명하지 못한다(최대 7 %). 남는 설명은 측정 정의(기준면·평균 영역·열드리프트) 또는 연속체 밖 효과(계면 미끄럼의 반대 방향은 아님: sliding은 u를 키움). 더 조정하지 않는다.
- 보완 방법 결정: (1) 접촉 단계 u는 0.54 um 측정값(선형 0.0038 nm/K)을 직접 쓰고 모델은 크기·방위 비율에만 쓴다(편향 계수 b, 이미 적용). (2) 연결 단계는 항복 x1(상한)과 x3(하한) 두 값으로 보고. (3) 압력은 +/-20 %.

### 라운드 Y: Ayoub 전 패드 거울상 시험 (16:35; SA1,SA2,SA4,SA5,SA6 완료; SA7은 시스템 메모리 부족으로 16:14 작업 중단, SA9 미실행 - 사용자 지시 전 재시작 안 함)
- 캡 60 nm + Ta 13 nm + SiO2 59/1.0 bonded 탄성 모델의 Delta eps'zz(30->400 C 가열)와 측정 Fig 2c(400 C 2 h 보유 후)의 비 r_p = (-Delta_model)/Delta_meas: 패드 10 0.959, 5 0.937, 4 0.769(단단한 패드); 2 0.866, 1 0.764, 6 0.792, 3 0.726(무른 패드). 전부 양수. 사전 선언 규칙(양수 & 단단한 패드 0.75-1.25) 충족 -> '부호 반전과 일관'.
- 해석: 측정 Delta에는 2 h 보유 중 증가(크리프/완화; E < 130 GPa에서 큼)가 포함되므로 무른 패드의 비가 0.73-0.79로 낮은 것은 예상 방향. 단단한 패드 5·10은 0.94-0.96. 즉 '부호 반전 + 탄성 bonded 모델 + 보유 중 비탄성 증가'로 10 패드 그림이 설명된다. 저자 확인은 여전히 필요.
