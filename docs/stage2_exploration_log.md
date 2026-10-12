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
