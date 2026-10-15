# IEIE 2026 fall: numbers in the text and their source files

Paths are relative to the repository root. S2 = `results/stage2/`. "Report" = `docs/stage2_baseline_report_ko.md`.
Text: `src/paper/build_docx.py`. Figures: `src/paper/make_figures.py`, which reads the same files.

## Numbers in the text

| Number in the text | Source (file → key / row) |
|---|---|
| Transition size, recess sum 3/5/8 nm → 0.55/0.70/1.0 µm (measured basis) | S2 `paper_results.json` → `transition_vs_recess_um.{3,5,8}.meas` = 0.553 / 0.700 / 0.996 |
| Model 0.66 µm (b = 1) – 1.06 µm (b = 0.69) at 5 nm | `paper_results.json` → `mechanism_transition.size_where_elastic_pair_closes_model_um` = 0.656; `size_model_b069_um` = 1.056 |
| Recess sum 5 nm = 2 × 2.5 nm (IRPS 2026) | `paper_results.json` → `mechanism_transition.recess_sum_nm`; `window_summary.json` → `settings.recess` "N(2.5,0.5^2) per pad" |
| 0.54 µm 2.8 nm, 1.26 µm 10 nm (pair, 400 °C) | 2 × `validation_rev1.csv` V2 / V1 measured 1.40 / 5.00 |
| Elastic orientation width 4 % | `validation_rev1.csv` V2 "imec 0.54 um 3 orientations" 2.175–2.264 nm (4.1 %); Report §13.4 "bonded 4 %" |
| 300 nm: about 1 nm per pad (elastic) | Report §13.10 "u_el 패드당 ≈ 1 nm"; `orient_diffusion_round2.json` → `orientation_coupling_350C_1h.0.30um.u_el_median` = 0.750 |
| Cu C11/C12/C44 168.4/121.4/75.4 GPa; Hill 128 GPa, 0.345; α 16.5 ppm/K | Report §3 (model); `docs/REFERENCES.md` (Nye1985 via Ayoub2022) |
| Cell 2.26 w (2D equal area), isolated 12 w; 12 w vs 20 w 1.3 % | Report §4 (cell row), §6 |
| NYCU SiO2 59 GPa, 1.0 ppm/K, taper 18°; imec SiCN 120 GPa, 2.0 ppm/K; bound-limited | S2 `adopted_rev.json` → `nycu.{E_d,a_d,taper,bound_limited}`, `imec.{E_d,a_d,bound_limited}` |
| Anisotropy single element: 3 orientations, error < 0.01 % | `results/validation_G3_anisotropy/results.csv` (12 rows, [100]/[110]/[111], max err_disp_pct 0.000) |
| Mesh × 2 +0.02 %; 3D–2D 0.1–0.7 % | Report §4 |
| Eq. (1) 0.0022·(θ−90°)·D, D^3.7, Q 20.7 kcal/mol, τ0 60 s, s_ox 0.45 | Report §3 (model); `diffusion_validation_rev1.json` → `tau0_s` = 60, `settings.Q_kcal` = 20.7 |
| Diffusion split: train 1 point (400 nm pitch, 350 °C), test 17 | `diffusion_validation_rev1.json` → `calibration_points` (1), `n_held` = 17 |
| Fixed form 2/17 | Report §13.3 |
| Revision 1: θ_eff 113.6°, 11/17 | `diffusion_validation_rev1.json` → `settings.theta` = 113.57, `n_pass` = 11 |
| 6 failures, all under-prediction (200 °C, D ≥ 250 nm, or self-anneal) | `diffusion_validation_rev1.csv`, held-out rows with pass = False: diff_nm < 0 for all 6 |
| PPA-Cu at ≥ 250 °C 5/5 (7/7 with duplicate checks) | `diffusion_validation_rev1.csv`: held-out PPA250C, T ≥ 250 (5 rows, all True); duplicate-check rows Fig.6 std (2, True) |
| Q_eff 14–17 kcal/mol | `orient_diffusion_round2.json` → `Q_eff_exploratory.{400,500}.Q_eff_kcal` = 16.7 / 14.3 |
| Round 2: θ_eff 119°, ω_c 5°, Δω 19.5°; median 11/17; IQR 10/17 | `orient_diffusion_round2.json` → `fit`, `n_pass_median` = 11, `n_pass_iqr` = 10 |
| f = 0 pads 1.5 %; f < 0.5 pads 13 % | `orient_diffusion_round2.json` → `faceted_fraction` = 0.0153; `paper_results.json` → `fraction_pads_f_below_0p5` = 0.132 |
| Ayoub 3 µm ε′zz −1.24 × 10⁻³; measured −0.5…−2.0 × 10⁻³ | S2 `ayoub_sc_wide.csv` (SC1 eps30 = −1.2397e-3; header: thesis Fig. 2.10a −2e-3…−5e-4) |
| 300 nm heating-slope magnitude within 0.5 %, sign opposite | `ayoub_tests.json` → `V5_pad10` −4.68e-6 vs 4.66e-6; `V5_pad3` −7.26e-6 vs 7.30e-6 |
| MC 2 × 10⁵ pairs; uncertainty set b{0.60, 0.69, 0.93, 1.0} × τ0{20, 60, 100} × Q{20.7, 15}; window P ≥ 0.99 | `window_summary.json` → `settings` |
| 300 nm clean window opens at 250 °C × 2 h / 300 °C × 30 min; 350 °C 5 min | `window_summary.json` → `0.30um.clean.recipe_min_time_per_T`, `P_main` |
| 3 boundary cells hatched (clean) | `window_summary.json` → `0.30um.clean.hatched_cells` (3) |
| Clean recipe independent of b | Report §13.1 |
| Elastic 0.75 nm of total 19.9 nm (300 nm, 350 °C, 1 h) | `orient_diffusion_round2.json` → `orientation_coupling_350C_1h.0.30um.{u_el_median,total_median}` |
| Oxidised: minimum recipe 300 °C × 2 h / 350 °C × 30 min | `window_summary.json` → `0.30um.oxidised.recipe_min_time_per_T` |
| Recess allowance 7.5 / 9 / 11.5 nm (clean); 3.5–6 nm (oxidised) | `paper_results.json` → `recess_spec_sum_nm_300nm` |
| Factor ranking (300 nm clean): 9; surface 3; τ0, Q, facet, liners 2; recess, b 0 | `window_summary.json` → `0.30um.clean.factor_cells_changed` |
| Orientation width of total protrusion 11.5 nm (elastic 0.03 nm) at 300 nm | `orient_diffusion_round2.json` → `orientation_coupling_350C_1h.0.30um.{total_width_q90_q10,u_el_width_q90_q10}` |
| Open pairs 2.3–3.4 × 10⁻³ (recommended cells); 1.4 × 10⁻³ at 400 °C | `paper_results.json` → `orientation_floor_300nm.{300C_30min,250C_120min,400C_*}.P_open_facet` |
| Connection stage A_c 0.95–1.0, 317–403 MPa | Report §13.10 (E25–E28) |
| Sliding control 1.7× / 3.5×; 3.66 / 4.84 nm | `validation_rev1.csv` V4 rows (3.656 / 2.1, 4.841 / 1.4) |
| NYCU 1 µm 1.79–1.94 vs 2.1 ± 0.4 | `validation_rev1.csv` V3 |
| 0.54 µm ratio 0.61–0.69, +46 % | `validation_rev1.csv` V2 (0.25/0.408, …, 1.40/2.039) |
| 0.54 µm decision sensitivity: 2 oxidised boundary cells | Report §13.1 |
| Table 2 (train) 6.87/4.26; 1.00–4.99 vs 1.05–5.40; 4.64/6.32 vs 6.05/7.85; 2σ | `adopted_rev.json` → `nycu.residuals`, `imec.residuals` (ok = within 2σ) |
| Table 2 (test) 1.26 / 0.54 µm values, rules | `validation_rev1.csv` V1, V2 |
| Table 3 commits | `.git/logs/HEAD` (all 16 hashes present; commit messages match the parts) |

## Deviations from the draft (`docs/paper/ieie2026f_plan_and_draft_ko.md`), corrected to the source files

1. Contribution ① gave "모델 0.57–1.06 µm @5 nm". In the file, 0.57 is the b = 0.69 value at 3 nm; at 5 nm the model range is 0.66–1.06 µm.
2. §3.1 listed "1.80 µm 전 온도 통과" under the test results. 1.80 µm is a training size, so the text now reports it as a training result (Table 2).
3. §3.2 and the abstract stated "250 °C 이상 PPA-Cu 전 점과 ≤ 140 nm 패드 200 °C 10/10" (also Report §13.3).
   - From `diffusion_validation_rev1.csv`: PPA-Cu at ≥ 250 °C passes 5/5 (7/7 with duplicate checks). Pads ≤ 140 nm pass 3/4: the 140 nm pad at 200 °C fails.
   - The text uses the file counts; "10/10" was not reproduced.
4. §2.2 stated "이방성 12방위 1 % 안". The G3 file has 3 orientations (12 rows = 4 input routes × 3), with error < 0.01 %.
5. The draft said "탄성 항은 총 돌출의 ~8 %" (Report §14). The json gives 0.75 / 19.9 nm (≈ 4 %) at 300 nm, 350 °C, 1 h. The text quotes the json values.
6. The draft ranking was "기구 ≫ 확산 동역학 ≈ 방위 ≈ 라이너 > 표면 > recess·b". The file (300 nm, clean) gives surface 3 > τ0, Q, facet, liner 2. The text follows the file.
7. The draft said "최적 어닐에서도 ≈ 1.4 × 10⁻³". The file gives 1.4 × 10⁻³ at 400 °C and 2.3–3.4 × 10⁻³ at the recommended cells; both are stated.
8. The draft gave Ayoub 3 µm "−0.35…−2 × 10⁻³". The source header gives −0.9…−0.35 × 10⁻³ before anneal (Fig. 2.6) and −2…−0.5 × 10⁻³ after anneal (Fig. 2.10a). The text uses the after-anneal range.
