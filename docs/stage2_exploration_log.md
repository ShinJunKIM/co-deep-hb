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
