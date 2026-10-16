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
- 2026-10-13 16:42 **X21** (X) X2 worst-plausible combo: CD 0.46, depth 0.5, taper 5, pitch 0.918 um -> exit 0, wall 20 s, LS ok True; du_c50 1.682 | du_ctr 2.200 | du_full 1.408 nm

### 크기별 오차(b 보정 없음)와 540 nm 측정 방식 적용 (16:50; `results/stage2/x_measurement_definition_054.csv`, X21)
- 오차(모델 c50 / 측정, 400 C): 고립 셀 3.06 -15 %, 1.80 +3 %, 1.26 -5 %, 0.54 +102 %; 배열 셀 -19 / -8 / -19 / +46 %. 200 C(배열): +9 / -5 / +18 / +59 %. NYCU 200 C: 9 um +7 %, 3 um +4 %, 1 um -15..-8 %. 결론: 1.26 um까지는 +/-20 % 안이고 0.54 um에서만 오차가 급증한다(크기가 작아질수록 커진다기보다 0.54 um에서 불연속).
- 540 nm 모델 표면: Cu 중심 5.20, 가장자리 3.85 nm; 유전체는 패드 옆 3.22 -> 먼 곳 2.50 nm. 즉 '어디를 기준면으로, 어디까지 평균하는가'에 따라 모델 u가 1.26-2.70 nm로 바뀐다. 전체 패드 평균 / 인접 유전체 기준이면 1.39 nm(-1 %), 전체 패드 / 시야 평균 1.58(+13 %), 사전등록 정의(중앙 50 % / 시야) 1.90(+36 %, 셀 2.26w 런의 값). AFM 탐침 반경 10-50 nm 팽창(dilation)은 2 % 미만.
- X21 최악 조합(CD 0.46, 깊이 0.5, 테이퍼 5 deg, 피치 0.918 um): c50 1.68(+20 %), 전체 평균 1.41(+1 %).
- 해석: 0.54 um의 +46 %는 대부분 측정 정의(평균 영역·기준면)로 흡수될 수 있고, 나머지는 기하 불확실성 안에 있다. 그러나 이는 사후 분석이므로 검증 판정(NOT VALIDATED)은 바꾸지 않는다. imec에 '평균 팽창'의 정의(평균 영역, 기준면 위치)를 확인하는 것이 선결.
- 2026-10-13 16:55 **X22** (Z) Z imec 3.06 um array cell PLASTIC Okoro x1 -> exit 0, wall 24 s, LS ok True; du_c50 8.747 | du_ctr 8.854 | du_full 7.681 nm, eppl_max 3.59e-02
- 2026-10-13 16:56 **X23** (Z) Z imec 1.8 um array cell PLASTIC Okoro x1 -> exit 0, wall 24 s, LS ok True; du_c50 8.407 | du_ctr 9.778 | du_full 7.042 nm, eppl_max 6.86e-02
- 2026-10-13 16:56 **X24** (Z) Z imec 1.26 um array cell PLASTIC Okoro x1 -> exit 0, wall 25 s, LS ok True; du_c50 7.906 | du_ctr 9.551 | du_full 6.629 nm, eppl_max 1.07e-01
- 2026-10-13 16:57 **X25** (Z) Z imec 0.54 um array cell PLASTIC Okoro x1 -> exit 0, wall 30 s, LS ok True; du_c50 5.834 | du_ctr 6.417 | du_full 5.160 nm, eppl_max 2.52e-01
- 2026-10-13 16:57 **X26** (Z) Z imec 3.06 um array cell PLASTIC Okoro x3 -> exit 0, wall 24 s, LS ok True; du_c50 7.157 | du_ctr 7.941 | du_full 6.140 nm, eppl_max 5.84e-03
- 2026-10-13 16:57 **X27** (Z) Z imec 1.26 um array cell PLASTIC Okoro x3 -> exit 0, wall 25 s, LS ok True; du_c50 4.684 | du_ctr 6.131 | du_full 3.876 nm, eppl_max 8.26e-03
- 2026-10-13 16:58 **X28** (Z) Z imec 0.54 um array cell PLASTIC Okoro x3 -> exit 0, wall 30 s, LS ok True; du_c50 2.151 | du_ctr 2.751 | du_full 1.849 nm, eppl_max 1.53e-02
- 2026-10-13 16:59 **X29** (Z) Z imec 1.8 um array cell PLASTIC Okoro x3 -> exit 0, wall 24 s, LS ok True; du_c50 5.833 | du_ctr 7.305 | du_full 4.828 nm, eppl_max 6.83e-03

### 라운드 Z: 한 가지 설정으로 imec 네 크기 동시 재현 시험 (17:10; X22-X29; 배열 셀, 채택 SiCN, 등방 소성)
- 400 C 오차(c50/시야): 탄성 -23/-12/-24/+36 % (3.06/1.80/1.26/0.54 um); Okoro x1 +10/+53/+56/+313 %(기각); Okoro x3(항복 RT 579 MPa, sub-um Cu 문헌 범위 300-600 MPa) -12/+3/-11/+44 %.
- 추출 정의를 '전체 패드/인접 유전체'로 바꾸면 x3에서 -48/-39/-45/+10 %: 작은 패드는 맞고 큰 패드는 크게 틀린다. 즉 어떤 (모델 x 정의) 조합도 네 크기를 동시에 +/-20 % 안에 넣지 못한다. 측정의 크기 의존이 모델보다 가파르다는 사실은 정의 선택과 무관하게 남는다.
- 현재 최선의 단일 설정: 배열 셀 + 등방 소성 x3 + c50/시야 -> 1.26-3.06 um +/-12 %, 0.54 um +44 %. 이것은 사후 선택이므로 '개정 2 후보'로만 기록(PI 승인 필요; 항복응력은 문헌 범위에서 고정해야 함).
- 2026-10-13 18:21 **W01** (W) W in-plane relaxation 100% (0.54 um), alpha_ip 2.00 ppm -> exit 0, wall 18 s, LS ok True; du_c50 1.385 | du_ctr 1.817 | du_full 1.176 nm
- 2026-10-13 18:21 **W02** (W) W in-plane relaxation 50% (0.54 um), alpha_ip 9.25 ppm -> exit 0, wall 18 s, LS ok True; du_c50 1.712 | du_ctr 2.257 | du_full 1.450 nm
- 2026-10-13 18:21 **W03** (W) W in-plane relaxation 25% (0.54 um), alpha_ip 12.88 ppm -> exit 0, wall 18 s, LS ok True; du_c50 1.876 | du_ctr 2.477 | du_full 1.588 nm
- 2026-10-13 18:22 **W04** (W) W in-plane relaxation 100% (1.26 um), alpha_ip 2.00 ppm -> exit 0, wall 18 s, LS ok True; du_c50 2.336 | du_ctr 2.819 | du_full 2.018 nm
- 2026-10-13 18:22 **W05** (W) W in-plane relaxation 50% (1.26 um), alpha_ip 9.25 ppm -> exit 0, wall 18 s, LS ok True; du_c50 3.187 | du_ctr 3.965 | du_full 2.729 nm
- 2026-10-13 18:22 **W06** (W) W in-plane relaxation 100% (1.8 um), alpha_ip 2.00 ppm -> exit 0, wall 18 s, LS ok True; du_c50 2.634 | du_ctr 3.023 | du_full 2.314 nm
- 2026-10-13 18:23 **W07** (W) W in-plane relaxation 50% (1.8 um), alpha_ip 9.25 ppm -> exit 0, wall 18 s, LS ok True; du_c50 3.812 | du_ctr 4.565 | du_full 3.300 nm
- 2026-10-13 18:23 **W08** (W) W in-plane relaxation 100% (3.06 um), alpha_ip 2.00 ppm -> exit 0, wall 18 s, LS ok True; du_c50 2.915 | du_ctr 3.146 | du_full 2.647 nm
- 2026-10-13 18:23 **W09** (W) W in-plane relaxation 50% (3.06 um), alpha_ip 9.25 ppm -> exit 0, wall 18 s, LS ok True; du_c50 4.619 | du_ctr 5.242 | du_full 4.088 nm
- 2026-10-13 18:25 **W10** (W) W 0.54 um full in-plane relaxation + plastic Okoro x3 -> exit 0, wall 30 s, LS ok True; du_c50 1.405 | du_ctr 1.827 | du_full 1.189 nm, eppl_max 2.10e-03
- 2026-10-13 18:25 **W11** (W) W 1.26 um 25% in-plane relaxation + plastic Okoro x3 -> exit 0, wall 26 s, LS ok True; du_c50 3.777 | du_ctr 4.827 | du_full 3.194 nm, eppl_max 5.61e-03
- 2026-10-13 18:25 **W12** (W) W 0.30 um full in-plane relaxation (prediction) -> exit 0, wall 22 s, LS ok True; du_c50 0.808 | du_ctr 1.077 | du_full 0.686 nm
- 2026-10-13 18:26 **W13** (W) W 0.54 um full in-plane relaxation, 3D [001] -> exit 0, wall 34 s, LS ok True; du_c50 1.219 | du_ctr 1.496 | du_full 1.055 nm

### 라운드 W: 면내 응력 완화로 540 nm 재현 (W01-W13) — 핵심 결과
- 가설: 작은 패드는 보유 중 확산 크리프(결정립계·계면)로 면내 압축응력이 풀린다. 면내 응력이 없으면 Poisson 밀어올림이 사라져 u가 줄어든다. ANSYS 대리 모델: Cu 면내 CTE를 유전체 값(2.0 ppm)까지 낮추고 수직 CTE(16.5 ppm)는 유지. 완화율 f = (16.5 - alpha_ip)/14.5.
- 540 nm, 400 C: f = 0 -> 2.04 (+46 %), 0.25 -> 1.88 (+34 %), 0.5 -> 1.71 (+22 %), **f = 1 -> 1.385 (-1 %)**. 소성(x3) 포함 시 1.405 (0 %).
- 같은 완화를 큰 패드에 적용하면 크게 과소: 1.26 um -53 %, 1.80 um -51 %, 3.06 um -63 % (f = 1). 즉 완화는 크기 의존이어야 한다.
- **단일 모델(등방 소성 Okoro x3 + 1 um 이하에서만 면내 완화 완료)로 네 크기 동시 재현: 3.06 -12 %, 1.80 +3 %, 1.26 -11 %, 0.54 0 %.**
- 시간 상수 일관성: 확산 완화 tau ~ D^n (n = 3 Coble, 3.7 표면확산/DM2024). 0.54 um가 단계당 보유(~10-15 분) 안에 완화되면 1.26 um는 2-4 시간 필요 -> 완화되지 않음. 측정의 크기 의존과 부호·크기가 모두 맞는다. imec의 전이(0.5 um 이하 확산 지배)와 같은 방향.
- 300 nm 예측(면내 완화 적용): u(400 C) 0.81 nm (완화 없을 때 1.27). 3D [001] 0.54 um 완화 1.22 vs 2D 1.385.
- 지위: 사후(post-hoc) 발견. 검증 판정(NOT VALIDATED)은 바꾸지 않는다. 개정 2로 사전등록하려면 완화율을 자유 파라미터가 아니라 tau(D, T)에서 유도해야 한다(제안: Coble 크리프 계수를 문헌에서 고정).
- 2026-10-13 18:51 **W14** (W) W 0.54 um full relaxation, 3D [101] -> exit 0, wall 30 s, LS ok True; du_c50 1.583 | du_ctr 1.925 | du_full 1.359 nm
- 2026-10-13 18:52 **W15** (W) W 0.54 um full relaxation, 3D [111] -> exit 0, wall 30 s, LS ok True; du_c50 1.700 | du_ctr 2.051 | du_full 1.459 nm
- 2026-10-13 18:52 **W16** (W) W 0.30 um full relaxation, 3D [001] -> exit 0, wall 26 s, LS ok True; du_c50 0.673 | du_ctr 0.828 | du_full 0.585 nm
- 2026-10-13 18:53 **W17** (W) W 0.30 um full relaxation, 3D [111] -> exit 0, wall 26 s, LS ok True; du_c50 1.056 | du_ctr 1.301 | du_full 0.900 nm

### 라운드 W 후속: 면내 완화가 방위 효과를 키운다 (W13-W17) — 결론이 뒤집힘
- u(400 C, nm) 방위별: 0.54 um 완화 없음 [001] 2.264 / [101] 2.200 / [111] 2.175 (폭 4 %, 순서 [111] < [001]); **완화 적용 [001] 1.219 / [101] 1.583 / [111] 1.700 (폭 33 %, 비 1.39, 순서 [001] < [111])**. 0.30 um: 완화 없음 폭 5 %, 완화 적용 [001] 0.673 / [111] 1.056 (폭 44 %, 비 1.57).
- 이유: 방위는 두 경로로 들어온다. (a) 면내 구속응력에 대한 Poisson 밀어올림 — 무른 [001]이 크다. (b) 측벽 전단 끌림에 대한 저항 — 단단한 [111]이 크다. 완화 없는 모델에서는 둘이 상쇄되어 4 %처럼 보였다. 면내 응력이 풀리면 (a)가 사라지고 (b)만 남아 폭이 33-44 %로 커지고 순서가 뒤집힌다.
- 즉 **"방위 효과가 작다"는 것은 측정을 재현하지 못하는 모델의 산물**이었다. 측정을 재현하는 모델(완화 포함)에서는 방위가 최대 1.6배 차이를 만든다.
- 교차 확인: 완화 모델의 무작위 방위 평균(Hill 등방) 1.385 nm = 측정 평균 1.40 nm. 개별 패드 폭 1.22-1.70 nm(+/-17 %)는 패드 간 산포 예측이고, imec이 EBSD로 bulge-out 산포를 방위 산포로 귀속시킨 것과 같은 방향이다.
- 공정창 함의: 최악 방위가 recess 한계를 정한다. 0.30 um에서 [001] 0.67 nm vs [111] 1.06 nm -> 최악 기준 0.67 nm. 방위는 무시할 수 없고, 오히려 sub-um에서 더 중요해진다.
- 2026-10-13 19:53 **W18** (W) W 0.54 um SLIDING + full in-plane relaxation -> exit 0, wall 18 s, LS ok True; du_c50 3.175 | du_ctr 3.197 | du_full 3.171 nm
- 2026-10-13 19:54 **W19** (W) W 0.54 um SLIDING, no relaxation (reference) -> exit 0, wall 18 s, LS ok True; du_c50 4.841 | du_ctr 4.874 | du_full 4.836 nm

### 부호 문제 자체 점검 (W18, W19 + 구현 검증) — "우리 잘못인가"에 대한 답
1. 구현은 정확하다. 저장된 성분에서 eps'zz = epel_z - (epel_x+epel_y+epel_z)/3를 재계산한 값이 저장값과 **차이 0**(S61, S62, S63). Laue가 재는 양(격자=탄성 변형률)과 우리가 쓰는 양(EPEL)이 같고, 좌표계도 시료 프레임(z = 패드 법선)으로 일치한다.
2. 그러나 **단순 규약 문제라고 단정할 수 없다.** 부호는 응력 상태가 정한다. 면내 인장 + 수직 자유 -> eps'zz < 0; 수직 구속 우세 -> eps'zz > 0. 우리 bonded 모델은 30 C에서 sigma_z 514 / sigma_lat 256 MPa(패드 10)로 수직 우세라 양수가 된다.
3. 두 모델 모두 크기는 측정에 가깝다: bonded |model|/|meas| 0.96-0.97(부호 반대), sliding 0.89(부호 일치).
4. **결정 시험**: 측벽을 sliding으로 풀면 부호는 맞지만 돌출이 맞지 않는다. 0.54 um 400 C: sliding 4.84(+246 %), sliding + 면내 완화 3.18(+127 %), **bonded + 면내 완화 1.385(-1 %)**, 측정 1.40. 1 um NYCU도 sliding 3.66 vs 측정 2.1.
5. 결론: 돌출 데이터(두 그룹, 네 크기)는 bonded를 요구하고, bonded는 표준 실공간 편차변형 정의에서 eps'zz > 0을 준다. 측정은 음수다. 어떤 단일 물리 모델도 둘을 동시에 만족시키지 못한다. 따라서 가장 경제적인 설명은 **발표된 eps'zz가 반대 부호 규약(예: 역격자 변형 텐서; LaueTools 문서가 실공간의 음수라고 명시)** 이라는 것이다. 저자 확인으로 판별된다.

### 오차막대 재판독 (2026-10-14; DM2023 Fig 1 600 dpi)
- 0.54 um 점들의 오차막대는 약 +/-0.1(100-200 C), +/-0.15(300 C), +/-0.2 nm(400 C)로 작다. 사전등록에서 가정한 +/-0.5보다 작다. 3.06 um 300 C는 +/-0.8, 1.26 um 300 C는 +/-1.0으로 크다.
- 결과: 0.54 um 모델 2.04 vs 1.40 +/- 0.2 -> 3 sigma. V2 실패 판정은 측정 불확실도로 구제되지 않는다. 0.54 um 점들은 직선 위에 정확히 놓이고(탄성적), 1.26·3.06 um은 300 C 이상에서 직선 위로 벗어난다(비탄성).
- 면내 완화 대리 모델(W 라운드)에 대한 주의: Cu 면내 CTE를 낮추는 방식은 체적 보존을 깨는 현상학적 대리다. 실제 메커니즘(면내 응력을 낮추되 재료를 상면으로 보내지 않는 과정)을 아직 특정하지 못했다. 개정 2에 쓰려면 메커니즘과 시간 상수를 문헌에서 고정해야 한다. 그 전까지는 '효과적 면내 구속 감소'로만 부른다.

### 0.54 um 잔차의 온도 프로파일 (2026-10-14; 런 없음, 기존 S112/W01/W10 재분석)
- S112(접합, 완화 없음) 측정/모델 비: 100 C 0.61, 200 C 0.63, 300 C 0.67, 400 C 0.69. 네 온도에서 거의 같다.
- W01(면내 완화): 0.90/0.93/0.98/1.01. 완화는 CTE 변경이므로 모든 온도에 즉시 적용된 결과다.
- 결론: 0.54 um의 과대예측은 100 C에서 이미 존재한다. 열활성 확산(Ds 비 350->100 C 약 1e-5)으로는 100-200 C에서 완화가 일어날 수 없다. 따라서 체크포인트 12의 계획("확산 시간 상수에서 완화를 유도")은 데이터 자체가 배제한다. 완화가 실재라면 비열적(athermal)이고 영구적인 크기 의존 인자여야 한다. 논증 F1의 "시간 상수에서 나온다"는 서술은 철회한다.
- 측정 정의 가설 재검: '전체 패드 평균 / 인접 유전체 링' 정의는 0.54 um을 -2 %로 맞추지만 같은 정의가 1.26-3.06 um을 -45...-56 %로 망친다. 단일 정의로는 설명 불가.
- 따라서 0.54 um 재현(W01/W10)은 현재 '유효 면내 구속 감소(메커니즘 미상, 비열적)'로만 서술한다.

### 결정: 라운드 SB (300 nm 변형률로 완화 모델을 독립 검증)
- 이유: 완화 모델이 실재라면 D^3.7 논리로 300 nm에서는 더 완전해야 한다. 면내 응력이 0이면 sigma_z(측벽 전단 끌림, 압축)만 남아 eps'_zz = (1+nu)/E*(2 s_z - s_x - s_y)/3 < 0, 즉 측정 부호가 나온다. 크기까지 맞으면 완화 모델이 0.54 um u와 300 nm eps'_zz 부호를 동시에 설명한다. 크기가 틀리면(접합 모델은 0.5 % 일치) 완화 모델은 300 nm에서 기각되고 부호 규약 설명이 남는다. 어느 쪽이든 결론을 바꾸므로 2런 가치가 있다.
- 구현: stage1_pipeline.material_block에 alpha_ip 옵션 추가(기본 None, S61 deck dry-run 재생성해 변경 없음 확인). SB10(pad 10, E_z 190), SB3(pad 3, E_z 68), S61/S62와 같은 스택·산화물(59 GPa, 1 ppm), alpha_ip = 1 ppm.
- 2026-10-14 **SB10** (SB) pad 10 E_z 190, in-plane relaxation -> exit 0, wall 85 s, all_conv True; eps'zz 30 C +1.704e-3, 350 C -5.035e-4, slope(30-350) -6.897e-6; s_x/s_z(350) -2/-114 MPa; u_ctr(400) 1.85 nm
- 2026-10-14 **SB3** (SB) pad 3 E_z 68, in-plane relaxation -> exit 0, wall 88 s, all_conv True; eps'zz 30 C +2.619e-3, 350 C -8.019e-4, slope -1.069e-5; s_x/s_z(350) -10/-68 MPa; u_ctr(400) 1.03 nm

### 라운드 SB 결과 (results/stage2/ayoub_sb_relaxation.csv)
- 예상과 달리 완화 모델은 부호를 바꾸지 않는다. 면내 응력이 0이 되면(s_x -2 MPa) 수직 응력만 남는데, 30 C에서 s_z가 인장(냉각 시 Cu가 수직으로 더 수축하려는 것을 측벽이 붙잡음)이라 eps'zz > 0이고 가열하면 감소한다. 접합 모델과 같은 부호다.
- 크기: 30 C 값 +42/+41 %, 기울기 +48/+46 % 과대(두 패드 모두). 접합 모델은 3-4 % / 0.5 %.
- 판정: **면내 완화 모델은 300 nm 변형률에서 기각된다.** 부호 규약이 어느 쪽이든 결론은 같다(규약이 뒤집힌 것이면 접합 모델이 정확하고 완화 모델이 45 % 틀림; 규약이 그대로면 둘 다 부호가 틀리고 미끄럼 모델만 부호가 맞음). D^3.7 논리라면 300 nm에서 완화가 가장 완전해야 하므로, 이 기각은 0.54 um 완화 설명 자체를 약화시킨다.
- 따라서 W 라운드의 0.54 um 재현(0 %)은 '독립 데이터로 지지되지 않는 유효 보정'으로 격하한다. 논증 F1은 철회하고, F2(방위 효과 33-44 %)는 완화 모델 전제이므로 조건부로 격하한다. 접합 모델 기준 방위 폭은 4 %다.
- 참고: 미끄럼 모델(S63)은 변형률 부호·크기(-8...-11 %)를 맞추지만 돌출을 3.5배 과대예측한다(1 um NYCU, 0.54 um imec 모두). 변형률 한 종류로는 측벽 조건을 판별할 수 없고, 돌출이 판별한다.
- 2026-10-15 16:09 **SC1** (SC) S2-SC 3 um pad, Hill Cu, bonded, cap, Ta 13 nm, adopted SiO2, mesh WA (PRIMARY) -> exit 0, wall 184 s, all_conv True; eps'zz 30 C -1.240e-03, 350 C +1.094e-03, slope(30-350) +7.292e-06; s_x/s_z(30) 227/51 MPa; u_ctr(400) 8.26 nm
- 2026-10-15 16:12 **SC2** (SC) S2-SC 3 um pad, pad-3 orientation (E_z 68), bonded, cap, Ta 13 nm, mesh WA -> exit 0, wall 181 s, all_conv True; eps'zz 30 C -1.831e-03, 350 C +1.616e-03, slope(30-350) +1.077e-05; s_x/s_z(30) 187/55 MPa; u_ctr(400) 9.64 nm
- 2026-10-15 16:15 **SC3** (SC) S2-SC 3 um pad, pad-10 orientation (E_z 190), bonded, cap, Ta 13 nm, mesh WA -> exit 0, wall 179 s, all_conv True; eps'zz 30 C -8.960e-04, 350 C +7.905e-04, slope(30-350) +5.270e-06; s_x/s_z(30) 247/49 MPa; u_ctr(400) 7.47 nm
- 2026-10-15 16:17 **SC4** (SC) S2-SC 3 um pad, Hill Cu, mesh WB (coarser; mesh check) -> exit 0, wall 108 s, all_conv True; eps'zz 30 C -1.237e-03, 350 C +1.092e-03, slope(30-350) +7.279e-06; s_x/s_z(30) 227/52 MPa; u_ctr(400) 8.27 nm

### 라운드 SC 결과: 3 µm 넓은 패드 부호 판정 (2026-10-15; 사전등록 docs/stage2_round_sc_wide_pad_sign.md, 커밋 63869bb; results/stage2/ayoub_sc_wide.csv)
- 구성: 학위논문 Table 2.1 구조 A(폭 3 µm, 간격 3 µm, 피치 6 µm), S61/S62와 같은 적층(접합, SiN 캡 60 nm, Ta 13 nm, SiO2 59 GPa/1.0 ppm, 두께 0.85 µm), 원형 패드(가정), Hill 등방 Cu(논문 p.52: 3 µm 패드는 ~9 결정립·지배 방위 없음), T_sf 200 °C(p.55: 3 µm SFT 150–250 °C). 기존 코드 무수정(프로세스 내 기하 덮어쓰기 + S61 해시 게이트 MATCH).
- SC1(1차) ε′zz(30 °C) **−1.240e-3**, SC2(패드 3 방위) −1.831e-3, SC3(패드 10 방위) −0.896e-3, SC4(성긴 메시) −1.237e-3 (메시 차 0.2 %). 전부 음수, 전부 수렴, ERROR 0.
- **판정: 규약 반전 기각.** 3 µm는 Ayoub(Fig. 2.6/2.10 음수)와 같은 부호, 300 nm만 반대. 응력 상태 σx 227 / σz 51 MPa(박막), 300 nm는 σz 514 / σlat 256(기둥). 두 크기의 부호 차이는 우리 모델 안에서 응력 상태가 바뀌어 생긴 것이고, 측정은 두 크기 모두 음수다.
- 크기(보고만): −1.24e-3는 Fig. 2.10(a) −0.5…−2e-3 범위 안, Fig. 2.6 −0.35…−0.9e-3보다 1.4–3.5배 큼(T_sf 150 환산 −0.88e-3). 기울기 +7.3e-6 /K vs Fig. 2.7 +2.3…+4.4e-6(측정은 250 °C 이상 정체 = 소성). 방위 괄호 −0.90…−1.83e-3, +5.3e-6…+1.08e-5 /K.
- 함의: "발표 ε′zz 부호 규약이 반대"라는 경제적 설명(W18/W19 점검 §5, 커밋 983be82)은 3 µm 데이터가 배제한다. 300 nm 부호 불일치는 미해결 한계로 남는다(미끄럼은 부호를 맞추나 돌출을 3.5배 과대예측). 모델·기존 결론은 바꾸지 않았다; 논증 수정은 PI 결정.

### Phase 1: 결정 민감도 시험 (2026-10-15; 규칙 커밋 2acfd92 → 계산; docs/stage2_decision_sensitivity.md, results/stage2/decision_sensitivity.csv)
- 격자 T×t×표면×크기 60셀 × b {0.60, 0.69, 0.93, 1.00} × τ₀ {20, 60, 100} s, θ 123°, IRPS recess, MC 2e5. 창 = P ≥ 0.99.
- **판정 OPEN**(문자 그대로): 0.54 µm·산화·τ₀ 60 s 격자에서 경계 셀 2개가 b에 따라 바뀜((250 °C, 120 min): b 1.0에서만 창; (350 °C, 5 min): b ≥ 0.69). 그 외 τ₀ 100 s (300 °C, 30 min) b 1.0만; 0.30 µm 청정 τ₀ 20 s (250 °C, 5 min) b ≥ 0.93. 11/12 격자는 조건 만족.
- 순위: N_b 4/180 (2.2 %) vs N_τ 37/240 (15.4 %) → τ₀가 7배 더 민감. 청정 표면 권고 레시피는 b 무관; 산화 표면 레시피만 b = 1일 때 한 단계 느슨해짐. b < 1은 보수적.
- 결정: 0.54 µm 오차 원인 규명을 필수 과제로 등록(보고서 §10에 반영). Phase 3 검증 τ₀로 재계산 예정.

### Phase 3 결정(값 읽기 전): θ_eff 보정 여부 (2026-10-15)
- DM2026 Fig. 2 범례: 200 °C 2 h / 200 °C 4 h / 250 °C 2 h / 350 °C 1 h / 450 °C 1 h. 보정점(400 nm 피치, 350 °C)의 어닐 시간은 1 h 하나 → 규칙 1에 따라 **τ₀만 보정, θ_eff 미보정(123° 고정)**. 데이터 분류와 비교량(Δh_max 중앙값)은 사전등록 §4.1에 기록. 디지타이징은 이 커밋 뒤에 시작.
- 2026-10-15 19:56 **E30** (E) contact Lhostis EXT w0.72 um r10 nm/pad T400 -> exit 1, wall 115 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.640 p=332MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 19:59 **E31** (E) contact Lhostis EXT w0.4 um r10 nm/pad T400 -> exit 1, wall 211 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.438 p=288MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 20:01 **E32** (E) contact Lhostis EXT w0.72 um r12 nm/pad T400 -> exit 1, wall 111 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.510 p=327MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 20:04 **E33** (E) contact Lhostis EXT w0.4 um r12 nm/pad T400 -> exit 1, wall 185 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.360 p=268MPa; T25: Ac/A=0.000 p=0MPa

### Phase 3 결과 1차 (2026-10-15; 사전등록 모델; results/stage2/diffusion_validation.csv)
- DM2026 디지타이징 29점(inputs/dm2026_digitized.json; 600 dpi, 색 분류, 눈금 보정, 오차 0.3–1.1 nm; fg-Cu 이동량이 논문 표기 +4/+6/+2 nm와 일치해 자체 점검 통과).
- τ₀ 보정(400 nm·350 °C 1 h) = 1259 s → held-out 2/17, 포화 실패, T 경향 통과 → **NOT VALIDATED**. 원인: 보정점이 포화 상태라 τ₀ 미식별, 진폭 오차(18.2 vs 13.0 nm)가 τ₀로 흡수돼 저온 예측 붕괴.
- 개정 1 결정(재실행 전 커밋): 보정 파라미터를 θ_eff로 바꾸고 τ₀ = 60 s 고정. 예상: 통과율 55–65 %, 여전히 NOT VALIDATED 가능성 높음(200 °C 250·300 nm 패드 과소). 사전등록 §6.
- 2026-10-15 20:06 **E34** (E) contact Lhostis EXT w0.72 um r14 nm/pad T400 -> exit 1, wall 103 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.438 p=311MPa; T25: Ac/A=0.000 p=0MPa

### Phase 3 결과 2차 — 개정 1 (2026-10-15; results/stage2/diffusion_validation_rev1.csv)
- θ_eff = 113.6°(τ₀ 60 s 고정) → held-out **11/17(65 %)**, T 경향 통과, 포화 실패(D250 R_pred 1.00 vs 1.13 ± 0.11) → **NOT VALIDATED(개정 후에도)**, 예상대로. 실패 6점은 모두 과소예측: 200 °C의 D ≥ 250 nm(PPA 500 nm 2 h/4 h; 자가 어닐 250·300 nm)와 자가 어닐 300 nm 250 °C. 250 °C 이상 PPA-Cu 전부 + ≤ 140 nm 패드 200 °C는 10/10 통과.
- 해석: Butrymowicz Q(20.7 kcal/mol)·D^3.7 동역학이 200 °C에서 너무 느림(측정 2 h→4 h 증가율로 τ(200 °C) ≈ 3 h → Q_eff ≈ 8 kcal/mol); 미세구조(PPA vs 자가 어닐) 변수 부재; 350→450 °C +13 %(400 nm)는 진폭의 약한 T 의존. 다음 사전등록 과제로 기록, 지금 조정 안 함.
- Phase 1 재계산(보고용, θ_eff 113.6°): 여전히 OPEN, τ₀ 민감도 17.9 % vs b 2.8 %; 권고 레시피는 τ₀ 60 s에서 유지. decision_sensitivity_rev1_*.
- 2026-10-15 20:08 **E35** (E) contact Lhostis EXT w0.4 um r14 nm/pad T400 -> exit 1, wall 140 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.277 p=278MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 20:10 **E36** (E) contact Lhostis EXT w0.72 um r16 nm/pad T400 -> exit 1, wall 107 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.360 p=313MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 20:13 **E37** (E) contact Lhostis EXT w0.4 um r16 nm/pad T400 -> exit 1, wall 147 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.234 p=269MPa; T25: Ac/A=0.000 p=0MPa

### Phase 2 문서 정리 (2026-10-15; 커밋 참조)
- stage2_paper_argument_ko.md / stage2_baseline_report_ko.md: (a) Ayoub "규약 반전 = 경제적 설명" 삭제 → "3 µm 부호 일치(SC1–SC4), 300 nm 부호 불일치(미해결), 크기 재현 주장 없음; 미끄럼 = 상한 시나리오; 원인 가설은 가설로만". (b) 결과 표 10개에 '사전등록/사후' 열 추가(사후: 항복 ×3, 면내 완화, 방위 폭 33–44 %; 기준 모델 4 %). (c) "같은 모델" 정의·약점(공정 내 검증, Hill vs 단결정 근사 이유). (d) b는 {0.60, 0.69, 0.93}+1.0 구간, 300 nm 성립 주장 없음, b<1 보수적(Phase 1 인용). (e) Okudur 2017 원 출처·미상 항목. (f) DM2026·Van Huylenbroeck ECTC 2026 참고문헌(REFERENCES.md). (g) 오버레이 범위 밖 문단(§13.6). (h) R61: 다른 PC에서 실행 중; 끝나면 step14 --partB, 아니면 대체 근거로 한계 보고(§10).
### Phase 3 규칙 9: 방위 (2026-10-15)
- Fig. 5(a) 디지타이징: 전체 중앙값 ≈ 16.0 nm; <111> 근방(하위 ≈ 10 %, < 6.5 nm) 중앙값 ≈ 4.0 vs 나머지 ≈ 16.5 nm → 차이 12.5 nm > 불확실도·> 30 % → **다음 사전등록에 방위 의존 확산 항 권고**(지금 미추가).
### Phase 4 진행 (2026-10-15)
- E17–E24 exit 1 진단: 소성 반복 중 일시 발산 ERROR(UX > 1e6) 후 이분법 복구, 전 하중단계 완료·RUN COMPLETED → MAPDL이 ERROR 존재 시 종료 코드 1 반환. 설정 오류 아님, 수정 없음.
- 확장 런(같은 모델, r 10 → 2 nm 간격): E30/E31 r10 (0.640/0.438), E32/E33 r12 (0.510/0.360), E34/E35 r14 (0.438/0.277), E36 r16 0.72 µm 0.360 … 진행 중(A_c = 0 후 ±0.5 nm 이분법).
- 2026-10-15 20:14 **E38** (E) contact Lhostis EXT w0.72 um r18 nm/pad T400 -> exit 1, wall 97 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.319 p=297MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 20:16 **E39** (E) contact Lhostis EXT w0.4 um r18 nm/pad T400 -> exit 1, wall 133 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.234 p=222MPa; T25: Ac/A=0.000 p=0MPa

### Phase 4 판정 (2026-10-15; PI 결정)
- r_open(A_c → 0)은 구면 캡 dishing(림 recess 0)에서 도달 불가(A_c ∝ r^−1.2…−1.4; A_c 0.05는 외삽 50–86 nm). PI 결정: **r50(A_c = 0.5)으로 대체, 사후 지표로 표기**; 격자(r ≤ 32 nm)는 끝까지 진행(보고용).
- r50: 0.72 µm 12.3 nm, 0.40 µm 8.3 nm → 비 **0.67**, 0.79 ± 0.15 안 → **PASS(사후)**. lhostis_ext.json.
- 2026-10-15 20:18 **E40** (E) contact Lhostis EXT w0.72 um r20 nm/pad T400 -> exit 1, wall 103 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.277 p=294MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 20:19 **E41** (E) contact Lhostis EXT w0.4 um r20 nm/pad T400 -> exit 1: results not readable (FileNotFoundError: C:\Users\USER\co-deep-hb\results\E41\contact.txt not found.)
- 2026-10-15 20:21 **E42** (E) contact Lhostis EXT w0.72 um r24 nm/pad T400 -> exit 1, wall 87 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.234 p=261MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 20:22 **E43** (E) contact Lhostis EXT w0.4 um r20 nm/pad T400 -> exit 1: results not readable (FileNotFoundError: C:\Users\USER\co-deep-hb\results\E43\contact.txt not found.)
- 2026-10-15 20:24 **E44** (E) contact Lhostis EXT w0.72 um r28 nm/pad T400 -> exit 1, wall 72 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.190 p=241MPa; T25: Ac/A=0.000 p=0MPa

### PI 결정 반영 (2026-10-15, 커밋 fd3139f 정정)
- Phase 1: OPEN 유지, 규칙 완화·산화 사례 삭제 없음. 보고 문장: "공정창은 0.54 µm 산화 표면 경계(τ₀ 60 s에서 셀 2개)를 제외하면 b에 무관; 0.54 µm 오차 원인은 Okudur 2017 부재로 미해결." 주 레시피 = 청정 표면, 산화 표면 = 민감도 사례(둘 다 모든 표 유지). 그림 s2_process_window_{0.54,0.3}um.png에 b 의존 셀 빗금(불확실 구간).
- Phase 4: **엄격 옵션 → UNDETERMINED**(r_open이 구면 캡 dishing에서 정의되지 않음). r50 비 0.67은 지표 선택 전에 계산된 보고용 수치이며 판정이 아니다. fd3139f의 "PASS(사후)" 표기는 이 커밋으로 철회.
- 2026-10-15 20:25 **E45** (E) contact Lhostis EXT w0.4 um r20 nm/pad T400 -> exit 1: results not readable (FileNotFoundError: C:\Users\USER\co-deep-hb\results\E45\contact.txt not found.)
- 2026-10-15 20:26 **E46** (E) contact Lhostis EXT w0.72 um r32 nm/pad T400 -> exit 1, wall 68 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.144 p=276MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 20:28 **E47** (E) contact Lhostis EXT w0.4 um r20 nm/pad T400 -> exit 1: results not readable (FileNotFoundError: C:\Users\USER\co-deep-hb\results\E47\contact.txt not found.)
- 2026-10-15 20:30 **E48** (E) contact Lhostis EXT w0.4 um r20 nm/pad T400 -> exit 1, wall 147 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.190 p=243MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 20:32 **E49** (E) contact Lhostis EXT w0.4 um r24 nm/pad T400 -> exit 1, wall 108 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.144 p=251MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 20:34 **E50** (E) contact Lhostis EXT w0.4 um r28 nm/pad T400 -> exit 1, wall 91 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.144 p=187MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 20:35 **E51** (E) contact Lhostis EXT w0.4 um r32 nm/pad T400 -> exit 1, wall 83 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.098 p=235MPa; T25: Ac/A=0.000 p=0MPa

### A. Lhostis 확장 격자 종료 (2026-10-15 20:5x; E30–E51)
- 0.72 µm: r 10/12/14/16/18/20/24/28/32 nm → A_c 0.640/0.510/0.438/0.360/0.319/0.277/0.234/0.190/0.144. 0.40 µm: 0.438/0.360/0.277/0.234/0.234/0.190/0.144/0.144/0.098. A_c = 0 미도달(림 접촉), 판정 UNDETERMINED 유지. r50 0.67은 보고용.
- R61: 이 PC에는 종료된 실행의 잔여 파일만 있고 다른 PC의 결과는 git에 없음 → 한계로 유지(대체 근거: imec 0.54 µm 선형 u(T), Lin 3 µm 잔류 0.1 nm, 보고서 §5.3).
- 2026-10-15 20:41 **E52** (E) contact Lhostis TEM w0.36 um h0.65 um r2 nm/pad T400 SiO2 -> exit 1, wall 93 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.924 p=281MPa; T25: Ac/A=0.000 p=0MPa

### B. 방위 의존 확산 항 (탐색 라운드 2; 규칙 6696562 → 계산; orient_diffusion_round2.*)
- 보정(500 nm·350 °C 분위수): θ_eff 120.0°, ω_c -3.5°, Δω 36.5°, facet 분율 0.0%. 검증 중앙값 12/17, IQR 13/17, T 경향 ok, 포화 fail → 불일치(규칙). 새 결과 = 분포 폭·lagging tail 재현. 200 °C 과소는 그대로(Q_eff 탐색 17–14 kcal/mol, 미세구조). 방위 산포: 확산 항 지배(0.54 µm 폭 15 vs 0.04 nm; 0.30 µm 11 vs 0.03 nm).
- 2026-10-15 20:43 **E53** (E) contact Lhostis TEM w0.36 um h0.65 um r4 nm/pad T400 SiO2 -> exit 1, wall 115 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.510 p=307MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 21:14 **E54** (E) contact Lhostis TEM w0.36 um h0.65 um r6 nm/pad T400 SiO2 -> exit 1, wall 1860 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.360 p=298MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 21:15 **E55** (E) contact Lhostis TEM w0.36 um h0.22 um r2 nm/pad T400 SiO2 -> exit 1, wall 46 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.910 p=241MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 21:16 **E56** (E) contact Lhostis TEM w0.36 um h0.22 um r4 nm/pad T400 SiO2 -> exit 1, wall 75 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.399 p=301MPa; T25: Ac/A=0.000 p=0MPa

### B 정정 (2026-10-15): 보정 루프 버그 → 범위 안 재계산
- bf3f792의 수치(ω_c −3.5°, Δω 36.5°, 12/17, 13/17)는 정밀화 루프가 범위 밖으로 흘러나간 버그 결과라 무효. 고정 후: θ_eff 119.0°, ω_c 5.0°, Δω 19.5°, facet 분율 1.5%; 중앙값 11/17, IQR 10/17, T 경향 ok, 포화 fail → 불일치(탐색 라운드 2). 결론(분포 폭 재현, 저온 중앙값 미개선, 확산 항이 방위 산포 지배)은 그대로.

### D. 공정창 예측 (2026-10-15; src/stage2/stage2_window.py; window_summary.json, s2_window_*.png, s2_factor_ranking.png)
- 모델 동결: 탄성 u_el(bonded, 배열 셀, b 0.69 ± 범위) + 확산 h_d(θ_eff 119°, f(ω) 탐색 라운드 2, τ₀ 60 s, Q 20.7) 단순합; recess N(2.5, 0.5²)/패드; 방위 구면 균일. 불확실 집합 b×τ₀×Q(24조합) → 바뀌는 셀 빗금.
- 0.54 µm 청정: 창 7/15(항상 6), 최소 레시피 300 °C x 30 min; 빗금 [[200, 120], [250, 30], [250, 120], [300, 5], [300, 30], [350, 5]]. imec 점검(350 °C 청정, recess 2–3 nm): P [0.99933, 0.99887] → 일관 → 300 nm 예측 진행.
- 0.54 µm 산화: 창 6/15, 최소 300 °C x 120 min.
- 0.30 µm 청정: 창 9/15(항상 9), 최소 250 °C x 120 min 또는 300 °C x 30 min; 빗금 [[200, 120], [250, 30], [300, 5]]. 산화: 창 6/15, 최소 300 °C x 120 min.
- 인자 순위(청정, 바뀌는 셀 수 0.54/0.30 µm): 기구(확산 off) 7/9 > τ₀ 3/2 ≈ 방위 facet 2/2 ≈ 라이너 θ 1–2/2 ≈ b 2/0 > 표면 1/3, recess 평균 1/0, recess σ 1/0, Q 1/2. 산화 표면에서는 라이너·recess 평균이 3–6셀로 커짐.
- 2026-10-15 21:17 **E57** (E) contact Lhostis TEM w0.36 um h0.22 um r6 nm/pad T400 SiO2 -> exit 1, wall 51 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.234 p=316MPa; T25: Ac/A=0.000 p=0MPa

### C. Lhostis TEM 두께 시험 (2026-10-15; E52–E57; 규칙 6696562)
- A_c(400 °C) h 0.65 / 0.22: r 2 → 0.92/0.91, r 4 → 0.51/0.40, r 6 → 0.36/0.23. (i) 분리 0.01–0.13 < 0.30 실패, (ii) 0.51 < 0.90 실패 → **FAIL**. 원인: A_c가 림 영역·벌크 소성에 지배돼 두께 무감.
- 개정 1(재실행 전 커밋): 항복 ×3(E58–E63). 예상: 여전히 FAIL 가능성 높음.
- 2026-10-15 21:20 **E58** (E) contact Lhostis TEM REV1 yield x3 w0.36 um h0.65 um r2 nm/pad T400 SiO2 -> exit 0, wall 48 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.399 p=552MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 21:20 **E59** (E) contact Lhostis TEM REV1 yield x3 w0.36 um h0.65 um r4 nm/pad T400 SiO2 -> exit 0, wall 48 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.190 p=656MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 21:21 **E60** (E) contact Lhostis TEM REV1 yield x3 w0.36 um h0.65 um r6 nm/pad T400 SiO2 -> exit 0, wall 51 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.098 p=916MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 21:22 **E61** (E) contact Lhostis TEM REV1 yield x3 w0.36 um h0.22 um r2 nm/pad T400 SiO2 -> exit 0, wall 37 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.319 p=530MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 21:23 **E62** (E) contact Lhostis TEM REV1 yield x3 w0.36 um h0.22 um r4 nm/pad T400 SiO2 -> exit 0, wall 38 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.144 p=637MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-15 21:23 **E63** (E) contact Lhostis TEM REV1 yield x3 w0.36 um h0.22 um r6 nm/pad T400 SiO2 -> exit 0, wall 39 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.098 p=768MPa; T25: Ac/A=0.000 p=0MPa

### C 개정 1 결과 (2026-10-15; E58–E63 항복 ×3)
- A_c h 0.65/0.22: r 2 → 0.40/0.32, r 4 → 0.19/0.14, r 6 → 0.10/0.10 → **FAIL**(예상대로). 연결 단계 두께 효과는 모델 한계로 보고.
### E. 최종 문서 (2026-10-15)
- 보고서 §13.8–§14(B·C·D 결과, 검증 상태 요약표, 주장 수위), 논증 문서 체크포인트 21–23, HANDOFF, CHANGELOG 갱신. 그림: s2_diffusion_fit.png, s2_window_0.54um/0.30um.png, s2_factor_ranking.png, s2_process_window_*.png, s2_size_scaling.png.
- 2026-10-15 22:27 **SD10** (SD) S2-SD pad 10 elastic, circle, cap, Ta 13 nm, adopted SiO2, SLIDING sidewall -> exit 0, wall 84 s, all_conv True; eps'zz 30 C +9.367e-04 (meas -1.197e-03, ratio -0.783), slope 30-350 -3.792e-06 (meas +4.660e-06, ratio -0.814); s_x/s_z(30) 252/461 MPa; u_ctr(400) 2.26 nm
- 2026-10-15 22:28 **SD3** (SD) S2-SD pad 3 elastic, circle, cap, Ta 13 nm, adopted SiO2, SLIDING sidewall -> exit 0, wall 86 s, all_conv True; eps'zz 30 C +1.525e-03 (meas -1.851e-03, ratio -0.824), slope 30-350 -6.224e-06 (meas +7.300e-06, ratio -0.853); s_x/s_z(30) 262/372 MPa; u_ctr(400) 1.69 nm
- 2026-10-15 22:30 **SD10N** (SD) S2-SD pad 10 elastic, circle, NO cap, Ta 13 nm, adopted SiO2, SLIDING sidewall -> exit 0, wall 81 s, all_conv True; eps'zz 30 C -6.935e-04 (meas -1.197e-03, ratio 0.579), slope 30-350 +2.808e-06 (meas +4.660e-06, ratio 0.603); s_x/s_z(30) 155/-0 MPa; u_ctr(400) 5.86 nm
- 2026-10-15 22:32 **SD3N** (SD) S2-SD pad 3 elastic, circle, NO cap, Ta 13 nm, adopted SiO2, SLIDING sidewall -> exit 0, wall 80 s, all_conv True; eps'zz 30 C -1.684e-03 (meas -1.851e-03, ratio 0.910), slope 30-350 +6.872e-06 (meas +7.300e-06, ratio 0.941); s_x/s_z(30) 121/-0 MPa; u_ctr(400) 7.18 nm

### 라운드 SD 해석 (2026-10-15; 사후; SD10/SD3/SD10N/SD3N)
- 측벽 미끄럼만(캡 접합 유지): 부호 여전히 반대(비 −0.78/−0.82) — 캡이 상면 둘레를 묶어 σz 461 MPa 유지. 캡 비전달 + 미끄럼: 부호 일치, 패드 3 0.91/0.94, 패드 10 0.58/0.60; 방위 비 0.41(측정 0.64, 접합 모델 거울상 0.64).
- 결론: "계면 상태 차이" 가설은 캡·측벽 둘 다 이완이어야 성립하고, 패드 10 크기·방위 비는 남는다. 보고서 §7·논증 문서에 반영(가설로만).
- 2026-10-16 00:28 **E64** (E) contact Lhostis R2 width rule w0.11 um h0.22 r2 nm T400 SiO2 bonded -> exit 1, wall 245 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.399 p=336MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-16 00:29 **E65** (E) contact Lhostis R2 width rule w0.11 um h0.22 r2 nm T400 SiO2 bonded yield x3 -> exit 0, wall 68 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.098 p=1565MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-16 00:30 **E66** (E) contact Lhostis R2 thickness rule SLIDING w0.36 h0.65 r2 nm T400 SiO2 -> exit 0, wall 71 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=1.000 p=414MPa; T25: Ac/A=0.000 p=0MPa

### 확산 항 라운드 3 (2026-10-16; 사전등록 db29b8e → DM2023 Fig. 7·9 디지타이징; inputs/dm2023_digitized.json)
- 사전등록 규칙(진폭 D = cavity): **0/7 NOT VALIDATED**(예측 2–4배 과소; 5 min = 2 h 포화는 램프 46 min 때문). 개정 1(진폭 D = pad, 이유 선커밋): **4/7 NOT VALIDATED**. 결론: 등크기(cavity/pad ≥ 0.7) 확산 항은 불균등(≤ 0.5) 구조로 전이되지 않음 → 공정창 적용 범위를 등크기 접합으로 한정(한계 명세). 모델·창 불변.
- 2026-10-16 00:31 **E67** (E) contact Lhostis R2 thickness rule SLIDING w0.36 h0.22 r2 nm T400 SiO2 -> exit 0, wall 52 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.859 p=292MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-16 00:33 **E68** (E) contact Lhostis R2 thickness rule SLIDING w0.36 h0.65 r4 nm T400 SiO2 -> exit 1, wall 129 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.774 p=430MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-16 00:34 **E69** (E) contact Lhostis R2 thickness rule SLIDING w0.36 h0.22 r4 nm T400 SiO2 -> exit 0, wall 49 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.474 p=340MPa; T25: Ac/A=0.000 p=0MPa

### 연결 단계 라운드 2 결과 (2026-10-16; E64–E69; 규칙 4b2a45e)
- 규칙 A(폭, held-out, 접합): V(0.11 µm) 0.62 vs V(0.36) 0.10 → **PASS**. 규칙 B(두께, 미끄럼): 650 nm V 0.000/0.24, 220 nm 0.15/0.54 (r0 2/4) → **PASS**. 판정 A&B PASS: Lhostis 폭 효과 = 접합 모델, 두께 효과 = 이완 계면 → ST/Leti 계면 이완 가설이 Ayoub 부호와 Lhostis 두께 두 관찰과 일관; 계면 상태는 공정 입력.
- 2026-10-16 00:35 **X30** (XL) XL liner 15 nm, 0.54 um array cell -> exit 0, wall 18 s, LS ok True; du_c50 2.046 | du_ctr 2.712 | du_full 1.732 nm
- 2026-10-16 00:36 **X31** (XL) XL liner 25 nm, 0.54 um array cell -> exit 0, wall 18 s, LS ok True; du_c50 2.055 | du_ctr 2.726 | du_full 1.741 nm
- 2026-10-16 00:36 **X32** (XL) XL liner 25 nm, 1.80 um array cell (control) -> exit 0, wall 18 s, LS ok True; du_c50 5.021 | du_ctr 6.154 | du_full 4.318 nm
- 2026-10-16 00:36 **X33** (XL) XL liner 25 nm, 1.26 um array cell (control) -> exit 0, wall 18 s, LS ok True; du_c50 4.066 | du_ctr 5.156 | du_full 3.467 nm
- 2026-10-16 00:37 **X34** (XL) XL liner 25 nm + pitch 1.7 w (2D 1.92 w), 0.54 um -> exit 0, wall 21 s, LS ok True; du_c50 1.849 | du_ctr 2.508 | du_full 1.541 nm
- 2026-10-16 00:37 **X35** (XS) XS surrogate test w0.90 h0.60 array 2.26w -> exit 0, wall 18 s, LS ok True; du_c50 3.169 | du_ctr 4.109 | du_full 2.687 nm
- 2026-10-16 00:37 **X36** (XS) XS surrogate test w0.40 h0.60 array 2.26w -> exit 0, wall 18 s, LS ok True; du_c50 1.530 | du_ctr 2.033 | du_full 1.294 nm
- 2026-10-16 00:38 **X37** (XS) XS surrogate test w0.54 h0.30 array 2.26w -> exit 0, wall 22 s, LS ok True; du_c50 1.820 | du_ctr 2.334 | du_full 1.547 nm
- 2026-10-16 00:38 **X38** (XS) XS surrogate test NYCU w1.0 h0.6 isolated 12w taper 18 -> exit 0, wall 18 s, LS ok True; du_c50 1.687 | du_ctr 1.934 | du_full 1.457 nm

### 라운드 X2 결과 (2026-10-16; X30–X38; 규칙 8194e62)
- 라이너 15/25 nm: u 0.54 µm 2.055 vs 2.039 nm → 효과 없음, 가설 **기각**(설명 몫 -0.02). 대리식 C(h/w): 4/4 ±20 % **통과**(C 1.01/0.49/1.16/1.16 vs 0.92/0.41/1.05/1.38).
- 2026-10-16 14:42 **VB001** (V2) V2 T 0.30 um 3D (1,0,0) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.224 | du_ctr 1.505 | du_full 1.057 nm
- 2026-10-16 14:43 **VB002** (V2) V2 T 0.30 um 3D (1,0.125,0) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.226 | du_ctr 1.507 | du_full 1.058 nm
- 2026-10-16 14:43 **VB003** (V2) V2 T 0.30 um 3D (1,0.125,0.125) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.227 | du_ctr 1.509 | du_full 1.059 nm
- 2026-10-16 14:44 **VB004** (V2) V2 T 0.30 um 3D (1,0.25,0) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.230 | du_ctr 1.513 | du_full 1.060 nm
- 2026-10-16 14:44 **VB005** (V2) V2 T 0.30 um 3D (1,0.25,0.125) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.231 | du_ctr 1.515 | du_full 1.061 nm
- 2026-10-16 14:45 **VB006** (V2) V2 T 0.30 um 3D (1,0.25,0.25) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.236 | du_ctr 1.522 | du_full 1.064 nm
- 2026-10-16 14:45 **VB007** (V2) V2 T 0.30 um 3D (1,0.375,0) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.236 | du_ctr 1.522 | du_full 1.064 nm
- 2026-10-16 14:45 **VB008** (V2) V2 T 0.30 um 3D (1,0.375,0.125) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.238 | du_ctr 1.525 | du_full 1.065 nm
- 2026-10-16 14:46 **VB009** (V2) V2 T 0.30 um 3D (1,0.375,0.25) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.243 | du_ctr 1.532 | du_full 1.068 nm
- 2026-10-16 14:46 **VB010** (V2) V2 T 0.30 um 3D (1,0.375,0.375) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.251 | du_ctr 1.542 | du_full 1.072 nm
- 2026-10-16 14:47 **VB011** (V2) V2 T 0.30 um 3D (1,0.5,0) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.244 | du_ctr 1.532 | du_full 1.068 nm
- 2026-10-16 14:47 **VB012** (V2) V2 T 0.30 um 3D (1,0.5,0.125) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.246 | du_ctr 1.535 | du_full 1.069 nm
- 2026-10-16 14:48 **VB013** (V2) V2 T 0.30 um 3D (1,0.5,0.25) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.251 | du_ctr 1.543 | du_full 1.072 nm
- 2026-10-16 14:48 **VB014** (V2) V2 T 0.30 um 3D (1,0.5,0.375) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.258 | du_ctr 1.552 | du_full 1.076 nm
- 2026-10-16 14:49 **VB015** (V2) V2 T 0.30 um 3D (1,0.5,0.5) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.266 | du_ctr 1.562 | du_full 1.081 nm
- 2026-10-16 14:49 **VB016** (V2) V2 T 0.30 um 3D (1,0.625,0) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.250 | du_ctr 1.541 | du_full 1.071 nm
- 2026-10-16 14:49 **VB017** (V2) V2 T 0.30 um 3D (1,0.625,0.125) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.252 | du_ctr 1.544 | du_full 1.072 nm
- 2026-10-16 14:50 **VB018** (V2) V2 T 0.30 um 3D (1,0.625,0.25) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.257 | du_ctr 1.551 | du_full 1.075 nm
- 2026-10-16 14:50 **VB019** (V2) V2 T 0.30 um 3D (1,0.625,0.375) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.264 | du_ctr 1.560 | du_full 1.080 nm
- 2026-10-16 14:51 **VB020** (V2) V2 T 0.30 um 3D (1,0.625,0.5) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.271 | du_ctr 1.569 | du_full 1.084 nm
- 2026-10-16 14:51 **VB021** (V2) V2 T 0.30 um 3D (1,0.625,0.625) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.277 | du_ctr 1.576 | du_full 1.087 nm
- 2026-10-16 14:52 **VB022** (V2) V2 T 0.30 um 3D (1,0.75,0) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.255 | du_ctr 1.547 | du_full 1.074 nm
- 2026-10-16 14:52 **VB023** (V2) V2 T 0.30 um 3D (1,0.75,0.125) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.256 | du_ctr 1.549 | du_full 1.075 nm
- 2026-10-16 14:53 **VB024** (V2) V2 T 0.30 um 3D (1,0.75,0.25) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.261 | du_ctr 1.555 | du_full 1.078 nm
- 2026-10-16 14:53 **VB025** (V2) V2 T 0.30 um 3D (1,0.75,0.375) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.268 | du_ctr 1.564 | du_full 1.082 nm
- 2026-10-16 14:54 **VB026** (V2) V2 T 0.30 um 3D (1,0.75,0.5) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.274 | du_ctr 1.572 | du_full 1.086 nm
- 2026-10-16 14:54 **VB027** (V2) V2 T 0.30 um 3D (1,0.75,0.625) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.280 | du_ctr 1.579 | du_full 1.089 nm
- 2026-10-16 14:54 **VB028** (V2) V2 T 0.30 um 3D (1,0.75,0.75) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.283 | du_ctr 1.583 | du_full 1.091 nm
- 2026-10-16 14:55 **VB029** (V2) V2 T 0.30 um 3D (1,0.875,0) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.257 | du_ctr 1.549 | du_full 1.075 nm
- 2026-10-16 14:55 **VB030** (V2) V2 T 0.30 um 3D (1,0.875,0.125) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.259 | du_ctr 1.551 | du_full 1.076 nm
- 2026-10-16 14:56 **VB031** (V2) V2 T 0.30 um 3D (1,0.875,0.25) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.263 | du_ctr 1.557 | du_full 1.079 nm
- 2026-10-16 14:56 **VB032** (V2) V2 T 0.30 um 3D (1,0.875,0.375) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.269 | du_ctr 1.565 | du_full 1.082 nm
- 2026-10-16 14:57 **VB033** (V2) V2 T 0.30 um 3D (1,0.875,0.5) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.275 | du_ctr 1.573 | du_full 1.087 nm
- 2026-10-16 14:57 **VB034** (V2) V2 T 0.30 um 3D (1,0.875,0.625) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.281 | du_ctr 1.580 | du_full 1.090 nm
- 2026-10-16 14:58 **VB035** (V2) V2 T 0.30 um 3D (1,0.875,0.75) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.285 | du_ctr 1.585 | du_full 1.092 nm
- 2026-10-16 14:58 **VB036** (V2) V2 T 0.30 um 3D (1,0.875,0.875) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.286 | du_ctr 1.587 | du_full 1.093 nm
- 2026-10-16 14:58 **VB037** (V2) V2 T 0.30 um 3D (1,1,0) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.258 | du_ctr 1.550 | du_full 1.075 nm
- 2026-10-16 14:59 **VB038** (V2) V2 T 0.30 um 3D (1,1,0.125) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.259 | du_ctr 1.552 | du_full 1.076 nm
- 2026-10-16 14:59 **VB039** (V2) V2 T 0.30 um 3D (1,1,0.25) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.263 | du_ctr 1.557 | du_full 1.079 nm
- 2026-10-16 15:00 **VB040** (V2) V2 T 0.30 um 3D (1,1,0.375) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.269 | du_ctr 1.564 | du_full 1.082 nm
- 2026-10-16 15:00 **VB041** (V2) V2 T 0.30 um 3D (1,1,0.5) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.275 | du_ctr 1.572 | du_full 1.086 nm
- 2026-10-16 15:01 **VB042** (V2) V2 T 0.30 um 3D (1,1,0.625) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.280 | du_ctr 1.579 | du_full 1.089 nm
- 2026-10-16 15:01 **VB043** (V2) V2 T 0.30 um 3D (1,1,0.75) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.284 | du_ctr 1.584 | du_full 1.092 nm
- 2026-10-16 15:02 **VB044** (V2) V2 T 0.30 um 3D (1,1,0.875) ang 0 bonded -> exit 0, wall 26 s, LS ok True; du_c50 1.287 | du_ctr 1.587 | du_full 1.094 nm
- 2026-10-16 15:02 **VB045** (V2) V2 T 0.30 um 3D (1,1,1) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.287 | du_ctr 1.588 | du_full 1.094 nm
- 2026-10-16 15:02 **VB046** (V2) V2 H 0.30 um 3D (1,0.5567,0.3451) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.259 | du_ctr 1.554 | du_full 1.077 nm
- 2026-10-16 15:03 **VB047** (V2) V2 H 0.30 um 3D (1,0.55,0.1993) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.251 | du_ctr 1.543 | du_full 1.072 nm
- 2026-10-16 15:03 **VB048** (V2) V2 H 0.30 um 3D (1,0.8259,0.6875) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.283 | du_ctr 1.582 | du_full 1.091 nm
- 2026-10-16 15:04 **VB049** (V2) V2 H 0.30 um 3D (1,0.9398,0.4987) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.275 | du_ctr 1.573 | du_full 1.086 nm
- 2026-10-16 15:04 **VB050** (V2) V2 H 0.30 um 3D (1,0.4871,0.42) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.260 | du_ctr 1.555 | du_full 1.078 nm
- 2026-10-16 15:05 **VB051** (V2) V2 H 0.30 um 3D (1,0.8055,0.0746) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.257 | du_ctr 1.549 | du_full 1.075 nm
- 2026-10-16 15:05 **VB052** (V2) V2 H 0.30 um 3D (1,0.6931,0.527) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.275 | du_ctr 1.573 | du_full 1.086 nm
- 2026-10-16 15:06 **VB053** (V2) V2 H 0.30 um 3D (1,0.6794,0.165) ang 0 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.256 | du_ctr 1.548 | du_full 1.074 nm
- 2026-10-16 15:06 **VB054** (V2) V2 H 0.30 um 3D (1,0.97,0.95) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.287 | du_ctr 1.588 | du_full 1.094 nm
- 2026-10-16 15:07 **VB055** (V2) V2 H 0.30 um 3D (1,0.95,0.9) ang 0 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.287 | du_ctr 1.587 | du_full 1.094 nm
- 2026-10-16 15:07 **VB056** (V2) V2 H 0.30 um 3D (1,0.93,0.8) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.286 | du_ctr 1.586 | du_full 1.093 nm
- 2026-10-16 15:08 **VB057** (V2) V2 H 0.30 um 3D (1,0.98,0.7) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.283 | du_ctr 1.582 | du_full 1.091 nm
- 2026-10-16 15:08 **VB058** (V2) V2 H 0.30 um 3D (1,0.2361,0) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.229 | du_ctr 1.512 | du_full 1.060 nm
- 2026-10-16 15:09 **VB059** (V2) V2 H 0.30 um 3D (1,0.1657,0.1657) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.229 | du_ctr 1.512 | du_full 1.060 nm
- 2026-10-16 15:09 **VB060** (V2) V2 H 0.30 um 3D (1,0.3564,0) ang 0 bonded -> exit 0, wall 27 s, LS ok True; du_c50 1.235 | du_ctr 1.521 | du_full 1.063 nm
- 2026-10-16 15:09 **VB061** (V2) V2 H 0.30 um 3D (1,0.2472,0.2472) ang 0 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.236 | du_ctr 1.522 | du_full 1.064 nm
- 2026-10-16 15:10 **VB062** (V2) V2 H 0.30 um 3D (1,0.4745,0) ang 0 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.242 | du_ctr 1.530 | du_full 1.067 nm
- 2026-10-16 15:10 **VB063** (V2) V2 H 0.30 um 3D (1,0.3226,0.3226) ang 0 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.244 | du_ctr 1.533 | du_full 1.068 nm
- 2026-10-16 15:11 **VB064** (V2) V2 H 0.30 um 3D (1,0.618,0) ang 0 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.250 | du_ctr 1.541 | du_full 1.071 nm
- 2026-10-16 15:11 **VB065** (V2) V2 H 0.30 um 3D (1,0.4028,0.4028) ang 0 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.254 | du_ctr 1.547 | du_full 1.074 nm
- 2026-10-16 15:12 **VB066** (V2) V2 R 0.30 um 3D (1,0,0) ang 22.5 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.226 | du_ctr 1.508 | du_full 1.058 nm
- 2026-10-16 15:12 **VB067** (V2) V2 R 0.30 um 3D (1,0,0) ang 45 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.227 | du_ctr 1.512 | du_full 1.058 nm
- 2026-10-16 15:13 **VB068** (V2) V2 R 0.30 um 3D (1,0.5,0) ang 22.5 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.244 | du_ctr 1.534 | du_full 1.068 nm
- 2026-10-16 15:13 **VB069** (V2) V2 R 0.30 um 3D (1,0.5,0) ang 45 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.245 | du_ctr 1.537 | du_full 1.067 nm
- 2026-10-16 15:14 **VB070** (V2) V2 R 0.30 um 3D (1,1,0) ang 22.5 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.258 | du_ctr 1.551 | du_full 1.075 nm
- 2026-10-16 15:14 **VB071** (V2) V2 R 0.30 um 3D (1,1,0) ang 45 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.259 | du_ctr 1.552 | du_full 1.075 nm
- 2026-10-16 15:15 **VB072** (V2) V2 R 0.30 um 3D (1,0.5,0.25) ang 22.5 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.252 | du_ctr 1.545 | du_full 1.072 nm
- 2026-10-16 15:15 **VB073** (V2) V2 R 0.30 um 3D (1,0.5,0.25) ang 45 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.252 | du_ctr 1.546 | du_full 1.072 nm
- 2026-10-16 15:16 **VB074** (V2) V2 R 0.30 um 3D (1,1,0.5) ang 22.5 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.275 | du_ctr 1.573 | du_full 1.086 nm
- 2026-10-16 15:16 **VB075** (V2) V2 R 0.30 um 3D (1,1,0.5) ang 45 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.275 | du_ctr 1.574 | du_full 1.086 nm
- 2026-10-16 15:17 **VB076** (V2) V2 R 0.30 um 3D (1,1,1) ang 22.5 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.287 | du_ctr 1.588 | du_full 1.094 nm
- 2026-10-16 15:17 **VB077** (V2) V2 R 0.30 um 3D (1,1,1) ang 45 bonded -> exit 0, wall 28 s, LS ok True; du_c50 1.287 | du_ctr 1.588 | du_full 1.094 nm
- 2026-10-16 15:18 **VS001** (V2) V2 T 0.30 um 3D (1,0,0) ang 0 sliding -> exit 0, wall 28 s, LS ok True; du_c50 5.841 | du_ctr 5.854 | du_full 5.836 nm
- 2026-10-16 15:18 **VS002** (V2) V2 T 0.30 um 3D (1,0.125,0) ang 0 sliding -> exit 0, wall 28 s, LS ok True; du_c50 5.779 | du_ctr 5.793 | du_full 5.774 nm
- 2026-10-16 15:19 **VS003** (V2) V2 T 0.30 um 3D (1,0.125,0.125) ang 0 sliding -> exit 0, wall 28 s, LS ok True; du_c50 5.719 | du_ctr 5.733 | du_full 5.714 nm
- 2026-10-16 15:19 **VS004** (V2) V2 T 0.30 um 3D (1,0.25,0) ang 0 sliding -> exit 0, wall 28 s, LS ok True; du_c50 5.605 | du_ctr 5.618 | du_full 5.601 nm
- 2026-10-16 15:20 **VS005** (V2) V2 T 0.30 um 3D (1,0.25,0.125) ang 0 sliding -> exit 0, wall 31 s, LS ok True; du_c50 5.550 | du_ctr 5.563 | du_full 5.545 nm
- 2026-10-16 15:20 **VS006** (V2) V2 T 0.30 um 3D (1,0.25,0.25) ang 0 sliding -> exit 0, wall 28 s, LS ok True; du_c50 5.393 | du_ctr 5.406 | du_full 5.388 nm
- 2026-10-16 15:21 **VS007** (V2) V2 T 0.30 um 3D (1,0.375,0) ang 0 sliding -> exit 0, wall 29 s, LS ok True; du_c50 5.351 | du_ctr 5.362 | du_full 5.348 nm
- 2026-10-16 15:21 **VS008** (V2) V2 T 0.30 um 3D (1,0.375,0.125) ang 0 sliding -> exit 0, wall 29 s, LS ok True; du_c50 5.303 | du_ctr 5.313 | du_full 5.300 nm
- 2026-10-16 15:22 **VS009** (V2) V2 T 0.30 um 3D (1,0.375,0.25) ang 0 sliding -> exit 0, wall 28 s, LS ok True; du_c50 5.167 | du_ctr 5.177 | du_full 5.163 nm
- 2026-10-16 15:22 **VS010** (V2) V2 T 0.30 um 3D (1,0.375,0.375) ang 0 sliding -> exit 0, wall 29 s, LS ok True; du_c50 4.972 | du_ctr 4.982 | du_full 4.969 nm
- 2026-10-16 15:23 **VS011** (V2) V2 T 0.30 um 3D (1,0.5,0) ang 0 sliding -> exit 0, wall 29 s, LS ok True; du_c50 5.068 | du_ctr 5.074 | du_full 5.069 nm
- 2026-10-16 15:23 **VS012** (V2) V2 T 0.30 um 3D (1,0.5,0.125) ang 0 sliding -> exit 0, wall 28 s, LS ok True; du_c50 5.028 | du_ctr 5.034 | du_full 5.028 nm
- 2026-10-16 15:24 **VS013** (V2) V2 T 0.30 um 3D (1,0.5,0.25) ang 0 sliding -> exit 0, wall 29 s, LS ok True; du_c50 4.917 | du_ctr 4.924 | du_full 4.916 nm
- 2026-10-16 15:24 **VS014** (V2) V2 T 0.30 um 3D (1,0.5,0.375) ang 0 sliding -> exit 0, wall 29 s, LS ok True; du_c50 4.758 | du_ctr 4.766 | du_full 4.757 nm
- 2026-10-16 15:25 **VS015** (V2) V2 T 0.30 um 3D (1,0.5,0.5) ang 0 sliding -> exit 0, wall 29 s, LS ok True; du_c50 4.586 | du_ctr 4.594 | du_full 4.585 nm
- 2026-10-16 15:25 **VS016** (V2) V2 T 0.30 um 3D (1,0.625,0) ang 0 sliding -> exit 0, wall 29 s, LS ok True; du_c50 4.812 | du_ctr 4.812 | du_full 4.816 nm
- 2026-10-16 15:26 **VS017** (V2) V2 T 0.30 um 3D (1,0.625,0.125) ang 0 sliding -> exit 0, wall 29 s, LS ok True; du_c50 4.780 | du_ctr 4.782 | du_full 4.784 nm
- 2026-10-16 15:26 **VS018** (V2) V2 T 0.30 um 3D (1,0.625,0.25) ang 0 sliding -> exit 0, wall 30 s, LS ok True; du_c50 4.693 | du_ctr 4.696 | du_full 4.696 nm
- 2026-10-16 15:27 **VS019** (V2) V2 T 0.30 um 3D (1,0.625,0.375) ang 0 sliding -> exit 0, wall 29 s, LS ok True; du_c50 4.568 | du_ctr 4.574 | du_full 4.570 nm
- 2026-10-16 15:27 **VS020** (V2) V2 T 0.30 um 3D (1,0.625,0.5) ang 0 sliding -> exit 0, wall 31 s, LS ok True; du_c50 4.433 | du_ctr 4.440 | du_full 4.433 nm
- 2026-10-16 15:28 **VS021** (V2) V2 T 0.30 um 3D (1,0.625,0.625) ang 0 sliding -> exit 0, wall 31 s, LS ok True; du_c50 4.313 | du_ctr 4.321 | du_full 4.312 nm
- 2026-10-16 15:28 **VS022** (V2) V2 T 0.30 um 3D (1,0.75,0) ang 0 sliding -> exit 0, wall 30 s, LS ok True; du_c50 4.623 | du_ctr 4.620 | du_full 4.630 nm
- 2026-10-16 15:29 **VS023** (V2) V2 T 0.30 um 3D (1,0.75,0.125) ang 0 sliding -> exit 0, wall 30 s, LS ok True; du_c50 4.599 | du_ctr 4.597 | du_full 4.605 nm
- 2026-10-16 15:29 **VS024** (V2) V2 T 0.30 um 3D (1,0.75,0.25) ang 0 sliding -> exit 0, wall 31 s, LS ok True; du_c50 4.531 | du_ctr 4.531 | du_full 4.535 nm
- 2026-10-16 15:30 **VS025** (V2) V2 T 0.30 um 3D (1,0.75,0.375) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.433 | du_ctr 4.436 | du_full 4.435 nm
- 2026-10-16 15:31 **VS026** (V2) V2 T 0.30 um 3D (1,0.75,0.5) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.325 | du_ctr 4.331 | du_full 4.326 nm
- 2026-10-16 15:32 **VS027** (V2) V2 T 0.30 um 3D (1,0.75,0.625) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.228 | du_ctr 4.237 | du_full 4.227 nm
- 2026-10-16 15:33 **VS028** (V2) V2 T 0.30 um 3D (1,0.75,0.75) ang 0 sliding -> exit 0, wall 55 s, LS ok True; du_c50 4.158 | du_ctr 4.168 | du_full 4.156 nm
- 2026-10-16 15:34 **VS029** (V2) V2 T 0.30 um 3D (1,0.875,0) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.517 | du_ctr 4.513 | du_full 4.526 nm
- 2026-10-16 15:35 **VS030** (V2) V2 T 0.30 um 3D (1,0.875,0.125) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.498 | du_ctr 4.494 | du_full 4.505 nm
- 2026-10-16 15:36 **VS031** (V2) V2 T 0.30 um 3D (1,0.875,0.25) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.442 | du_ctr 4.441 | du_full 4.448 nm
- 2026-10-16 15:37 **VS032** (V2) V2 T 0.30 um 3D (1,0.875,0.375) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.361 | du_ctr 4.364 | du_full 4.365 nm
- 2026-10-16 15:38 **VS033** (V2) V2 T 0.30 um 3D (1,0.875,0.5) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.271 | du_ctr 4.277 | du_full 4.272 nm
- 2026-10-16 15:39 **VS034** (V2) V2 T 0.30 um 3D (1,0.875,0.625) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.187 | du_ctr 4.195 | du_full 4.186 nm
- 2026-10-16 15:40 **VS035** (V2) V2 T 0.30 um 3D (1,0.875,0.75) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.123 | du_ctr 4.134 | du_full 4.121 nm
- 2026-10-16 15:41 **VS036** (V2) V2 T 0.30 um 3D (1,0.875,0.875) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.088 | du_ctr 4.100 | du_full 4.086 nm
- 2026-10-16 15:42 **VS037** (V2) V2 T 0.30 um 3D (1,1,0) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.486 | du_ctr 4.481 | du_full 4.495 nm
- 2026-10-16 15:43 **VS038** (V2) V2 T 0.30 um 3D (1,1,0.125) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.469 | du_ctr 4.465 | du_full 4.477 nm
- 2026-10-16 15:44 **VS039** (V2) V2 T 0.30 um 3D (1,1,0.25) ang 0 sliding -> exit 0, wall 56 s, LS ok True; du_c50 4.421 | du_ctr 4.419 | du_full 4.427 nm
- 2026-10-16 15:45 **VS040** (V2) V2 T 0.30 um 3D (1,1,0.375) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.350 | du_ctr 4.352 | du_full 4.355 nm
- 2026-10-16 15:46 **VS041** (V2) V2 T 0.30 um 3D (1,1,0.5) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.269 | du_ctr 4.274 | du_full 4.271 nm
- 2026-10-16 15:47 **VS042** (V2) V2 T 0.30 um 3D (1,1,0.625) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.190 | du_ctr 4.198 | du_full 4.190 nm
- 2026-10-16 15:48 **VS043** (V2) V2 T 0.30 um 3D (1,1,0.75) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.126 | du_ctr 4.136 | du_full 4.124 nm
- 2026-10-16 15:49 **VS044** (V2) V2 T 0.30 um 3D (1,1,0.875) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.085 | du_ctr 4.097 | du_full 4.082 nm
- 2026-10-16 15:50 **VS045** (V2) V2 T 0.30 um 3D (1,1,1) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.071 | du_ctr 4.083 | du_full 4.068 nm
- 2026-10-16 15:51 **VS046** (V2) V2 H 0.30 um 3D (1,0.5567,0.3451) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.703 | du_ctr 4.710 | du_full 4.704 nm
- 2026-10-16 15:52 **VS047** (V2) V2 H 0.30 um 3D (1,0.55,0.1993) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.870 | du_ctr 4.874 | du_full 4.871 nm
- 2026-10-16 15:53 **VS048** (V2) V2 H 0.30 um 3D (1,0.8259,0.6875) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.161 | du_ctr 4.171 | du_full 4.160 nm
- 2026-10-16 15:54 **VS049** (V2) V2 H 0.30 um 3D (1,0.9398,0.4987) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.265 | du_ctr 4.270 | du_full 4.266 nm
- 2026-10-16 15:55 **VS050** (V2) V2 H 0.30 um 3D (1,0.4871,0.42) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.716 | du_ctr 4.724 | du_full 4.715 nm
- 2026-10-16 15:56 **VS051** (V2) V2 H 0.30 um 3D (1,0.8055,0.0746) ang 0 sliding -> exit 0, wall 56 s, LS ok True; du_c50 4.558 | du_ctr 4.555 | du_full 4.566 nm
- 2026-10-16 15:57 **VS052** (V2) V2 H 0.30 um 3D (1,0.6931,0.527) ang 0 sliding -> exit 0, wall 55 s, LS ok True; du_c50 4.343 | du_ctr 4.350 | du_full 4.343 nm
- 2026-10-16 15:58 **VS053** (V2) V2 H 0.30 um 3D (1,0.6794,0.165) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.672 | du_ctr 4.672 | du_full 4.676 nm
- 2026-10-16 15:58 **VS054** (V2) V2 H 0.30 um 3D (1,0.97,0.95) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.073 | du_ctr 4.085 | du_full 4.070 nm
- 2026-10-16 15:59 **VS055** (V2) V2 H 0.30 um 3D (1,0.95,0.9) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.078 | du_ctr 4.090 | du_full 4.075 nm
- 2026-10-16 16:00 **VS056** (V2) V2 H 0.30 um 3D (1,0.93,0.8) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.102 | du_ctr 4.113 | du_full 4.099 nm
- 2026-10-16 16:01 **VS057** (V2) V2 H 0.30 um 3D (1,0.98,0.7) ang 0 sliding -> exit 0, wall 56 s, LS ok True; du_c50 4.146 | du_ctr 4.155 | du_full 4.145 nm
- 2026-10-16 16:02 **VS058** (V2) V2 H 0.30 um 3D (1,0.2361,0) ang 0 sliding -> exit 0, wall 56 s, LS ok True; du_c50 5.629 | du_ctr 5.643 | du_full 5.625 nm
- 2026-10-16 16:03 **VS059** (V2) V2 H 0.30 um 3D (1,0.1657,0.1657) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 5.631 | du_ctr 5.645 | du_full 5.626 nm
- 2026-10-16 16:04 **VS060** (V2) V2 H 0.30 um 3D (1,0.3564,0) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 5.392 | du_ctr 5.404 | du_full 5.389 nm
- 2026-10-16 16:05 **VS061** (V2) V2 H 0.30 um 3D (1,0.2472,0.2472) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 5.402 | du_ctr 5.415 | du_full 5.397 nm
- 2026-10-16 16:06 **VS062** (V2) V2 H 0.30 um 3D (1,0.4745,0) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 5.126 | du_ctr 5.132 | du_full 5.125 nm
- 2026-10-16 16:07 **VS063** (V2) V2 H 0.30 um 3D (1,0.3226,0.3226) ang 0 sliding -> exit 0, wall 57 s, LS ok True; du_c50 5.151 | du_ctr 5.162 | du_full 5.148 nm
- 2026-10-16 16:08 **VS064** (V2) V2 H 0.30 um 3D (1,0.618,0) ang 0 sliding -> exit 0, wall 56 s, LS ok True; du_c50 4.824 | du_ctr 4.825 | du_full 4.829 nm
- 2026-10-16 16:09 **VS065** (V2) V2 H 0.30 um 3D (1,0.4028,0.4028) ang 0 sliding -> exit 0, wall 56 s, LS ok True; du_c50 4.879 | du_ctr 4.888 | du_full 4.877 nm
- 2026-10-16 16:10 **VS066** (V2) V2 R 0.30 um 3D (1,0,0) ang 22.5 sliding -> exit 0, wall 57 s, LS ok True; du_c50 5.841 | du_ctr 5.855 | du_full 5.836 nm
- 2026-10-16 16:11 **VS067** (V2) V2 R 0.30 um 3D (1,0,0) ang 45 sliding -> exit 0, wall 57 s, LS ok True; du_c50 5.841 | du_ctr 5.857 | du_full 5.836 nm
- 2026-10-16 16:12 **VS068** (V2) V2 R 0.30 um 3D (1,0.5,0) ang 22.5 sliding -> exit 0, wall 56 s, LS ok True; du_c50 5.069 | du_ctr 5.076 | du_full 5.069 nm
- 2026-10-16 16:13 **VS069** (V2) V2 R 0.30 um 3D (1,0.5,0) ang 45 sliding -> exit 0, wall 56 s, LS ok True; du_c50 5.070 | du_ctr 5.079 | du_full 5.070 nm
- 2026-10-16 16:14 **VS070** (V2) V2 R 0.30 um 3D (1,1,0) ang 22.5 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.489 | du_ctr 4.485 | du_full 4.497 nm
- 2026-10-16 16:15 **VS071** (V2) V2 R 0.30 um 3D (1,1,0) ang 45 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.492 | du_ctr 4.490 | du_full 4.499 nm
- 2026-10-16 16:16 **VS072** (V2) V2 R 0.30 um 3D (1,0.5,0.25) ang 22.5 sliding -> exit 0, wall 56 s, LS ok True; du_c50 4.916 | du_ctr 4.925 | du_full 4.916 nm
- 2026-10-16 16:17 **VS073** (V2) V2 R 0.30 um 3D (1,0.5,0.25) ang 45 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.918 | du_ctr 4.927 | du_full 4.917 nm
- 2026-10-16 16:18 **VS074** (V2) V2 R 0.30 um 3D (1,1,0.5) ang 22.5 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.270 | du_ctr 4.276 | du_full 4.272 nm
- 2026-10-16 16:19 **VS075** (V2) V2 R 0.30 um 3D (1,1,0.5) ang 45 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.271 | du_ctr 4.278 | du_full 4.273 nm
- 2026-10-16 16:20 **VS076** (V2) V2 R 0.30 um 3D (1,1,1) ang 22.5 sliding -> exit 0, wall 56 s, LS ok True; du_c50 4.071 | du_ctr 4.083 | du_full 4.068 nm
- 2026-10-16 16:21 **VS077** (V2) V2 R 0.30 um 3D (1,1,1) ang 45 sliding -> exit 0, wall 57 s, LS ok True; du_c50 4.071 | du_ctr 4.083 | du_full 4.068 nm
- 2026-10-16 14:35 **E70** (E) contact Lhostis width rule under SLIDING w0.11 um h0.22 r2 nm T400 SiO2 -> exit 1, wall 319 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T400: Ac/A=0.669 p=435MPa; T25: Ac/A=0.669 p=435MPa
- 2026-10-16 14:38 **SC5** (SC) S2-SC 3 um pad, Hill Cu, SLIDING sidewall, bonded cap, Ta 13 nm, mesh WA -> exit 0, wall 183 s, all_conv True; eps'zz 30 C -1.269e-03, 350 C +1.119e-03, slope(30-350) +7.463e-06; s_x/s_z(30) 225/44 MPa; u_ctr(400) 8.28 nm
- 2026-10-16 14:41 **SC6** (SC) S2-SC 3 um pad, Hill Cu, SLIDING sidewall, NO cap, Ta 13 nm, mesh WA -> exit 0, wall 177 s, all_conv True; eps'zz 30 C -1.230e-03, 350 C +1.085e-03, slope(30-350) +7.236e-06; s_x/s_z(30) 175/0 MPa; u_ctr(400) 9.13 nm

### 정합성 라운드 (2026-10-16; 규칙 83bf8e3)
- E70(미끄럼 폭 효과) V 0.35 vs 0.15 → 통과; SC5/SC6(3 µm 미끄럼) −1.27/−1.23e-3 → 부호 일치. 같은 설정 평가: 접합 2/4, 미끄럼+접합 캡 2/4, 미끄럼+캡 비전달 4/4(정성). 두 경계 분리(탄성 접촉 한계 0.70 µm vs 기여도 역전 0.74–2.45 µm 외삽 예측). f(ω) 4종·β 배척(2.3σ)·확률 vs 최악 방위 창(docs/v2). 논문 초안 v4, corrections_v4.md. 방위 전수 계산은 브랜치 v2-orientation.
- 2026-10-16 16:30 **E71** (E) contact v2 boundary SLIDING 0.30 um r2 nm T250 -> exit 0, wall 95 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T250: Ac/A=0.698 p=439MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-16 16:32 **E72** (E) contact v2 boundary SLIDING 0.30 um r3 nm T250 -> exit 1, wall 121 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T250: Ac/A=0.544 p=483MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-16 16:35 **E73** (E) contact v2 boundary SLIDING 0.30 um r3 nm T300 -> exit 1, wall 175 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=0.750 p=461MPa; T25: Ac/A=0.000 p=0MPa
- 2026-10-16 16:37 **E74** (E) contact v2 boundary SLIDING 0.30 um r4 nm T300 -> exit 1, wall 114 s, LS ok True; T25: Ac/A=0.000 p=0MPa; T300: Ac/A=0.640 p=458MPa; T25: Ac/A=0.000 p=0MPa
