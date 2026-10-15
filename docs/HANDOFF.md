# HANDOFF — run status (updated 2026-10-09)

**This file records run status only.** Design decisions (criteria, model choices, scope) are owned by
the main planning document. If a decision seems to have changed, flag it to the project lead; do not
write it here.

## Session-start routine (a new chat reads these, in this order)

1. **Main planning document** (all design decisions):
   https://claude.ai/code/artifact/94558db6-f844-4507-a2ad-f1d335461aeb
   If the chat cannot open the link, the lead attaches or pastes the document.
2. **This file**, `docs/HANDOFF.md`, for run status and next commands.
3. **The repository** on the PC in use: `$HOME\co-deep-hb` (this PC: `C:\Users\USER\co-deep-hb`),
   remote `https://github.com/pwqppt/co-deep-hb.git`.
   - In Claude Science, request host access to that folder.
   - Then `git pull` and read `docs/CHANGELOG.md` (latest entries) and `docs/RUNLIST.md`.
4. Execution rule: ANSYS cannot run inside the app.
   - Every run is handed to the lead as **one** paste-ready PowerShell block (with the `cd`),
     together with the expected runtime and the files it creates.
   - The lead runs it on a PC with ANSYS and reports back.

## Run status

| Run / gate | What | Status | Key numbers (end of heating, 400 °C) |
|---|---|---|---|
| G0 | MAPDL connectivity from the app | done — runs only natively | `docs/history/G0_mapdl_connectivity_report.md` |
| G1 | Cu bar thermal expansion, units | PASS | ΔL 6.1875 µm, σ −680.625 MPa (exact) — `results/validation_G1_cu_bar/` |
| G3 | anisotropic Cu + orientation | PASS (12/12) | `results/validation_G3_anisotropy/` |
| cp_check | ANEL + MISO (Ludwick) syntax | done | `results/validation_cp_check/` |
| R01 | pad 10 elastic, cap, bonded | done | u 2.083 nm, ε′zz −0.585e-3, Cu σz −261 MPa |
| R24 | DIAG: no cap, bonded | done | u 2.817 nm, ε′zz −0.492e-3 |
| R25 | DIAG: cap, sliding (fixed build) | done | u 2.539 nm, ε′zz −0.478e-3, Cu σz −227 MPa |
| R26 | DIAG: no cap, sliding (fixed build) | done; equilibrium acceptance **PASS** | u 6.093 nm, ε′zz +0.327e-3, Cu σz ≈ 0, pad lengthening 5.649 nm |
| R27 | LAT paper-literal: circle, no cap, bonded, no liner | done | ε′zz 30/400 +1.143/−0.569e-3 (opposite sign to measured/Ayoub FEM), u 2.572 nm |
| R28 | LAT R26 + circle | done | ε′zz −0.677/+0.337e-3, gap closed 4 % |
| R29 | LAT R26 + Ta liner 10 nm | done | ε′zz −0.700/+0.348e-3, gap closed 8 % |
| R30 | LAT R26 + Ta liner 25 nm | done | ε′zz −0.755/+0.376e-3, gap closed 18 % |
| R31 | ORI pad 4 elastic, R26 config | done | Δε′zz 1.078 vs Fig2c 2.363 (r 0.456, FAIL) |
| R32 | ORI pad 5 elastic, R26 config | done | Δε′zz 0.989 vs Fig2c 1.854 (r 0.534, pass) |
| R33 | ORI pad 7 elastic, R26 config | done | Δε′zz 1.105 vs Fig2c 2.406 (r 0.459, FAIL) |
| R34 | ORI pad 9 elastic, R26 config | done | Δε′zz 1.103 vs Fig2c 1.854 (r 0.595, FAIL) |
| R35 | SIGN pad 3 elastic, paper-literal (R27 config) | done | Test A: 1.26 × (−FEM) at all T → FAIL |
| R36 | SIGN pad 4 elastic, paper-literal (R27 config) | done | Δ −1.801 vs −2.363 (r 0.762, fail) |
| R37 | SIGN pad 5 elastic, paper-literal (R27 config) | done | Δ −1.716 vs −1.854 (r 0.926, pass) |
| R38 | SIGN pad 7 elastic, paper-literal (R27 config) | done | Δ −1.824 vs −2.406 (r 0.758, fail) |
| R39 | SIGN pad 9 elastic, paper-literal (R27 config) | done | Δ −1.828 vs −1.854 (r 0.986; cons. fail) |
| R02–R07, R10–R23 | see `docs/RUNLIST.md` | not run | — |
| R08 | pad 10 plastic = elastic | no solve needed (deck identical to R01) | — |
| R09 | Cu CTE(T) variant | blocked: needs `inputs/cu_cte_vs_T.csv` (NIST) | — |

**Pending analysis (not yet done):** compare R01 (bonded) and the fixed R25 (sliding, cap kept)
against measured pad 10 ε′zz on heating 30–350 °C. Report both; do not pick.

## Next commands

Restructure regression check R01/R26: **ALL MATCH** (2026-10-09); first commit/push: command issued, completion not yet confirmed.
Step 10 done: pre-registered stopping rule TRIGGERED (best combination 33–44 % < 50 %). Lateral-factor search stopped.
Step 11 (orientation test, pre-registered in docs/stage1_step11_orientation_test.md): R31–R34 done; **verdict FAIL** (pads 9, 7, 4) → Option B not justified, stopped. Without pad 9 (secondary): within tolerance.
Open: author question (docs/stage1_summary_for_PI_ko.md); Option B awaiting PI decision (docs/stage1_optionB_assessment.md) — not run.
Previously: the restructure regression check (R01 and R26 from the repo layout must
reproduce the numbers above exactly), then the first commit and push. See `docs/GIT_SETUP.md`.

## Open issues (run level)

- MAPDL `.out` files are ~13 MB, mostly the echo of 100k N/E lines. Wrapping the mesh block in
  `/NOPR` … `/GOPR` would shrink them, but it changes the deck text, so it is deferred to an explicit
  decision.
- The pipeline records `cnvg_flag_raw` from `*GET,…,SOLU,CNVG`, but that flag is 0 for linear solves.
  The verdict uses `.mntr` and the `.out` failure strings instead.
- `.rst` files are not in git; R01 and R25 `.rst` are kept on PC 1 only (in the old chat workspace).
- Modelling-level open items are tracked in `docs/stage1_model_spec.md` §B11 and the planning
  document.

## Session-end routine (when a gate passes or the lead says "wrap up")

1. Update this file: run status, next commands, open issues.
2. Add a `docs/CHANGELOG.md` entry: what changed and why. Bugs get what was wrong, how it was found,
   and how it was fixed.
3. Give the lead one commit + push block:
   ```
   cd "$HOME\co-deep-hb"; git add -A; git status --short; git commit -m "<summary>"; git push
   ```
4. At a model freeze (e.g. the end of Stage 1), tag it:
   ```
   cd "$HOME\co-deep-hb"; git tag -a v1.0 -m "Stage 1 model freeze"; git push origin v1.0
   ```


**Step 12 (2026-10-11):** sign-convention hypothesis H_sign, pre-registered in docs/stage1_step12_sign_hypothesis.md; R35–R39 done; **H_sign NOT supported** (Test A FAIL: pad 3 model = 1.26 × −FEM; Test B FAIL: pads 4, 7, 9).
**Working copy moved:** the repo now lives at `$HOME\co-deep-hb` (the chat-workspace copy was deleted by an automatic workspace cleanup on 2026-10-11; GitHub was intact).

**Step 13 (2026-10-12):** Lin 2025 protrusion reproduction, pre-registered in docs/stage1_step13_lin_reproduction.md; R40–R56 done (results commit c33ec12): **bonded FAIL** (9 µm 7.36 vs 6.4; 3 µm 5.55 vs 3.6–4.9) but 1 µm passes (2.23–2.59 vs 2.3 ± 0.4) and the trend holds; the sliding control fails (1 µm 5.93) → sidewall = bonded is discriminated. R49 (3D plastic) did not solve: TB,PLAS + TB,ANEL error — check before R05–R07. Still owed: further 1 µm cell enlargement (+5.3 % at ×2). Open issue kept: absolute ε′zz mismatch with Ayoub (Steps 10–12).

**Step 14 (2026-10-12):** pre-registered in docs/stage1_step14_plasticity.md. Part A A01–A32, Part C R57 and R58 pending; Part B R59 is built after Part A.
**Step 14 status:** Part C done (NOT SUPPORTED) and R58 converged. Part A first run is done, but the thermal-on checks were invalid (test-deck ramp). Pending: `step14.py --partA-fix`, then the Part A recommendation, then Part B (R59).
**Step 14 status (update):** Part A is done, with recommendation AELS + KEYOPT(2)=3. Part B is pre-registered; pending runs: `step14.py --partB0`, then `stage1_pipeline.py --case R60,R59`, then `step14.py --partB`. Use `el_input="AELS"` for all future plastic runs (ANEL+PLAS stops in batch).
**Step 14 status (update 2):** B0 and R60 gates PASS; R59 diverged (LS1). Pending: `stage1_pipeline.py --case R61,R62`, then `step14.py --partB` (decision tree in doc B2).
**Step 14/15 status:** R61 was stopped, so Part B has no verdict. Step 15 is pre-registered; pending: `lin13.py --case R63,...,R71`, then agent analysis.
**Status 2026-10-13 (handover):** R61 was killed by the user at 01:48, after about 78 min at t = 0.249 of LS1 (projected 1-2 days). Since then no solve is running: r61.out has stopped updating. Step 14 Part B: B0 and R60 gates PASS; R59 diverged; R62 never ran. Part B has NO VERDICT. Step 15 (R63-R71, 1 um orientation contact) is pre-registered but PARKED and not run. Next: Stage 2 baseline plan (user prompt). Registry IDs in use: R01-R71 (do not modify).

**Stage 2 round SC (2026-10-15):** Ayoub 3 um wide-pad sign test, pre-registered in docs/stage2_round_sc_wide_pad_sign.md (63869bb) before SC1-SC4; driver src/stage2/stage2_wide.py (Stage 1 builder untouched, S61 hash gate MATCH). SC1 (Hill, primary) eps'zz(30 C) = -1.240e-3; SC2/SC3 (pad-3 / pad-10 orientation) -1.831e-3 / -0.896e-3; SC4 (coarser mesh) -1.237e-3. All converged, 0 errors. **Verdict: sign-convention reversal REJECTED** (3 um negative like Ayoub; only 300 nm opposite). Magnitude inside thesis Fig. 2.10a range, slope 1.7-3.2x the Fig. 2.7 heating slope (elastic vs measured plateau). results/stage2/ayoub_sc_wide.csv. No model or prior conclusion changed; the paper-argument wording on the sign convention is for the PI to revise. Author reply (sent 2026-10-14) still pending. Note: .venv was recreated on this PC (README recipe) because it was missing.

**Stage 2 Phases 1-4 (2026-10-15):** Phase 0 pushed (63869bb, f7818ad). Phase 1 decision sensitivity (pre-reg 2acfd92): **OPEN** by the letter (0.54 um oxidised tau0 60 s: 2 boundary cells move with b), tau0 7x more sensitive than b -> 0.54 um error cause = required task. Phase 2 docs done (paper argument, report §13, REFERENCES). Phase 3 diffusion validation (pre-reg 9c6bc29; DM2026 digitized to inputs/dm2026_digitized.json): fixed form NOT VALIDATED (2/17); revision 1 (eb347c1, theta_eff 113.6 deg, tau0 60 s) 11/17, still NOT VALIDATED; rule 9 -> recommend orientation-dependent diffusion term next. Phase 4: E17-E24 exit 1 = transient plastic divergence recovered (not a setup error); extension runs E30+ (src/stage2/stage2_lhostis_ext.py --auto) in progress, results in results/stage2/lhostis_ext.json.
**Phase 4 verdict (2026-10-15, corrected):** **UNDETERMINED** — the pre-registered metric r_open (A_c -> 0) is undefined for the spherical-cap dishing (rim recess 0 -> rim contact at every recess). r50 ratio 0.67 (8.3 / 12.3 nm) is a reported, non-verdict number computed before the metric choice. Phase 1 stays OPEN (clean surface = main recipe, oxidised = sensitivity case; b-dependent cells hatched in s2_process_window_*.png). Extension grid runs to r = 32 nm in the background (results/stage2/lhostis_ext.json; commit E-run files when the loop ends).

**End-to-end A–E (2026-10-15):** A Lhostis grid done (UNDETERMINED). B orientation-dependent diffusion amplitude (exploratory round 2): theta_eff 119 deg, omega_c 5 deg, d_omega 19.5 deg; medians 11/17, IQR 10/17; diffusion term dominates orientation spread. C Lhostis TEM thickness test: FAIL (pre-reg), FAIL (revision 1 yield x3). D windows: 0.54 um clean 300 °C x 30 min (imec 350 C check consistent), 300 nm clean 250 °C x 120 min / 300 °C x 30 min; hatched uncertainty in results/figures/s2_window_*.png; factor ranking s2_factor_ranking.png. Report §13.8–§14 final. Open: 0.54 um cause (no source data), 300 nm sign, 200 C diffusion kinetics, connection-stage thickness effect, overlay, R61.

**Agent rounds (2026-10-16):** 7 forks + 3 pre-registered run sets. Connection round 2 E64-E69: width rule PASS (held-out), thickness rule PASS with sliding interfaces -> ST/Leti relaxed-interface hypothesis consistent with Ayoub sign + Lhostis thickness. Diffusion round 3 (DM2023 held-out): 0/7, revision 4/7 (exploratory) -> equal-pad term does not transfer to cavity/pad <= 0.5. X2: liner diagnostic rejected (u unchanged), surrogate C(h/w) test 4/4 within 20 %. Review response: window governed by <111> tail shape; claims conditional on bonded interfaces. Master curve Q_eff 13.4; yield bridge chain ceiling ~500 links. Report §15, paper draft §1 v3, Claude Science prompt updated. Claude Science figures already in docs/paper/figures/ (untracked here; owned by that session).

