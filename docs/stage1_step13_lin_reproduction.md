# Stage 1 · Step 13 — Reproduction of measured Cu protrusion, Lin et al. 2025 (pre-registered BEFORE any run)

**Status.** Pre-registration. No Step 13 run has been made. Commit this file before R40–R56 are solved.

**Context.**
- Step 12 is closed (H_sign not supported). The absolute ε′zz mismatch with Ayoub stays an **open issue**; no more runs on it now.
- New validation structure: the constraint and geometry physics is validated against **measured** protrusion u (Lin 2025). The orientation effect is validated later against Ayoub (relative trend only).
- Model philosophy as R27: bonded Cu/SiO2 sidewall, no cap, no liner. **No parameter is tuned to Lin's data. A failure is recorded as a failure.**

**Source.** H.-E. Lin et al., *Revealing challenges of downscaling effects on Cu thermal expansion in advanced hybrid bonding using in-situ AFM*, Appl. Surf. Sci. 689 (2025) 162539, doi:10.1016/j.apsusc.2025.162539. Page numbers refer to the journal PDF.

## 1. Data used (from the paper)
| item | value | where |
|---|---|---|
| structure | damascene Cu in PECVD SiO2 on a 12″ Si wafer; Ta adhesion layer + Cu seed; ECP; two-step CMP; circular pads | p.2, Sec. 2.1 |
| pads (width / thickness) | 9 / 1.15, 3 / 1.5, 1 / 1.5 µm; AR 0.13 / 0.5 / 1.5; frustum volumes 50.93 / 9.25 / 0.77 µm³; grain 3.5 / 2.5 / 0.9 µm | p.2, Table 1 |
| taper | "angle of ~108° with the SiO2 sidewall" (lateral etching); volumes "approximated as frustums of a cone" | p.3, Sec. 3.1, Fig. 3 |
| measurement | in-situ tapping AFM; same location; RT → 200 °C in 50 °C steps; ~15 min hold per step; SiO2 surface set to 0; Cu height = average over a square region inside the pad | p.3, Sec. 2.2; p.4 |
| expansion u(200) − u(RT) | 9 µm **6.4 nm**, 3 µm **3.7 nm**, 1 µm **2.3 nm** (slopes 0.36 / 0.22 / 0.13 Å/°C) | p.1 abstract; p.5, Fig. 8 |
| 3 µm array (9 pads) | **4.1 ± 0.4 nm**, range 3.6–4.9 nm; no correlation with E_eff (R² = 0.003) | p.8, Table 4, Fig. 12 |
| orientation | 9 and 3 µm polycrystalline, random texture; 1 µm ≈ single grain, orientation not given | p.3–4, Fig. 4 |
| prior FEM in the paper | Eq. (1), α_sim = 0.027 ln V + 0.1377 Å/°C, from an earlier FEM (their ref. 16), matches the 3 and 1 µm pads and under-predicts 9 µm by ~40 % | p.6–7, Table 2, Fig. 10 |

## 2. Geometry read from Fig. 3 (FIB-SEM) and assumptions
- **Taper — read, but the sources conflict.** Fixed choice: **θ = 7.6° from vertical** (wider at the top). This is the value that reproduces the Table 1 frustum volumes of the 3 µm and 1 µm pads; both give 7.6°.
  - Fig. 3(c), measured on the image: top ≈ 1.08 µm, bottom ≈ 0.57 µm over ≈ 1.43 µm, i.e. ≈ 10°. This is consistent with 7.6° within the reading error.
  - The annotated "~108°" would mean 18°, which leaves a 1 µm pad with a 0.03 µm bottom and contradicts the 0.77 µm³ volume.
  - The 9 µm volume (50.93 µm³) cannot be reproduced by any taper (a cylinder gives 73.2 µm³); it is treated as a typo, and the same 7.6° is used.
- **SiO2 under the pad — unreadable** (the image is cropped). Fig. 3(a) shows ≥ 0.44 µm of SiO2 below the 9 µm pad. ASSUMPTION: **0.5 µm**.
  - It sits under both the Cu and the reference SiO2 surface, so it enters du only through the bottom constraint, which is expected to be second order.
- **Ta thickness — unreadable** (not resolved in Fig. 3). ASSUMPTION: **omitted**, as in R27.
  - Expected effect < ~5 % for a 1 µm pad: R30 showed +15 % lateral stress for 25 nm Ta on a 0.3 µm pad, and 25 nm is 8 % of that pad's radius but only 2.5 % of a 1 µm pad's.
- **Most uncertain parameter, and the one sensitivity case: the taper.** R54 = 1 µm, iso 2D, θ = 18° (the literal 108° annotation) vs R42 (7.6°).
- **Cell** (Lin gives no pitch; isolated pads):
  - cell width = **3 w** (2D outer radius 1.5 w; 3D square cell 3 w), Si thickness = cell width;
  - outer wall with the Si in-plane displacement α_Si·ΔT·(distance), bottom UZ = 0 (same substrate treatment as R01–R39);
  - **check:** cell and Si ×2 (R51–R53). Pre-registered: if du changes > 2 %, the ×2 result replaces the primary value for pass/fail and the change is reported.
- **Materials** (unchanged from R01–R39):
  - SiO2 72 GPa / 0.17 / 0.5 ppm/K; Si 130 GPa / 0.28 / 2.6 ppm/K; Cu α = 16.5 ppm/K constant.
  - Polycrystalline Cu: isotropic **Hill average** of Chang & Himmel at 300 K (C11/C12/C44 = 170.0/122.5/75.8 GPa) → **E = 128.3 GPa, ν = 0.3454**, constant in T.
  - Single-crystal Cu (1 µm): paper constants 168.4/121.4/75.4 GPa, rotated so that z ∥ [001], [101], [111] (E_z 66.7 / 130.3 / 191.2 GPa). In-plane angle 0°.
- **Temperatures:** 25 (RT, assumed), 50, 100, 150, 200 °C. T_ref = 25 °C. For elastic runs du does not depend on T_ref. Holds are not modelled (no creep).

## 3. Model and output definitions
- 9 and 3 µm: **2D axisymmetric** (PLANE182, enhanced strain), 40 elements across the pad radius.
- 1 µm: **3D** (SOLID185), full square cell, circular O-grid pad (10 elements across), taper by z-dependent radial mapping.
- Bonded = shared nodes on all Cu interfaces.
- Sliding (control) = Cu copies of the sidewall nodes tied to SiO2 by the **normal** displacement only. The tapered normal is (cos θ e_r, −sin θ e_z). The bottom rim stays bonded.
- **u(T)** = mean UZ over the central square of side w/2 on the Cu top (2D: the axisymmetric field integrated over the square) − mean UZ of the SiO2 top surface at the cell edge (2D: r = R; 3D: all edge nodes). **du = u(200) − u(25).**
  - Report only: the SiO2 reference taken as the mean over the AFM field (Fig. 5: 25 / 8 / 3.5 µm), because Lin sets the SiO2 in the image to 0.
- Elastic is PRIMARY.
  - Plastic is report-only: Ludwick variant ① with the computed-E mapping rule of Steps 1–12. [001] → pad-3 curve; Hill E = 128.3 GPa → interpolation between pads 1 and 2. T_sf = 25 °C (ASSUMPTION).
- Code: `src/stage1/lin13.py`, a separate module with its own meshes, decks and registry. **stage1_pipeline.py and s1_mesh.py are not modified, so R01–R39 decks are unchanged.**

## 4. Runs
| Run | pad | model | Cu | sidewall | role |
|---|---|---|---|---|---|
| R40 | 9 µm | 2D | Hill | bonded | **primary** |
| R41 | 3 µm | 2D | Hill | bonded | **primary** |
| R43 / R44 / R45 | 1 µm | 3D | [001] / [101] / [111] | bonded | **primary** |
| R46 / R47 | 9 / 3 µm | 2D | Hill | sliding | control |
| R48 | 1 µm | 3D | [001] | sliding | control |
| R49 / R50 | 1 µm [001] 3D / 3 µm 2D | | | bonded, plastic | report only |
| R51 / R52 / R53 | 9 / 3 / 1 µm [001] | | | bonded, cell ×2 | cell check (< 2 %) |
| R54 | 1 µm 2D Hill | taper 18° | | bonded | taper sensitivity (vs R42) |
| R42 / R55 | 1 µm Hill, 2D / 3D | | | bonded | 3D-vs-2D verification (same physics, expect < 3 %) |
| R56 | 3 µm 2D | mesh ×2 | | bonded | mesh check (expect < 2 %) |

All are within the Student limit (largest: R53, 52 022 nodes).

## 5. Pass criteria (bonded, primary) — fixed now
1. 3 µm: du within the measured array range **3.6–4.9 nm**.
2. 9 µm: |du − 6.4| ≤ **0.4 nm**.
3. 1 µm: the range over the 3 orientations overlaps **2.3 ± 0.4 nm**.
4. Size trend: du(9) > du(3) > du(1) for every 1 µm orientation.
5. **PASS = 1–4 all true.**

**Discrimination.** Report whether the sliding control FAILS. If both bonded and sliding pass, state that the test cannot discriminate the sidewall condition. The verdict is printed by `python src\stage1\lin13.py --compare` → `results/diagnostics/step13_lin.csv`.

## 6. Pre-registered analytic predictions (written before any run)
**Bounds** (ΔT = 175 K, Hill ν = 0.345; Δα relative to the SiO2 surface):
- Thin-film limit, i.e. Cu in-plane strain locked to Si: α_v = α_Cu + 2ν/(1−ν)(α_Cu − α_Si) = 31.17 ppm/K. The SiO2 surface moves with α_ox + 2ν_ox/(1−ν_ox)(α_ox − α_Si) = −0.36 ppm/K. **du_film = h · 31.53e-6 · ΔT.**
- Free column (no lateral constraint): **du_free = h · (α_Cu + 0.36e-6) · ΔT.**

**Interpolation used for the bonded and sliding estimates** (chosen a priori):
- Bonded: f(AR) = du/du_film = (1 − e^(−x))/x with x = AR/AR0. AR0 = 0.663 is fixed by our own FEM family R27/R35–R39 at AR 2.83 (bonded, interpolated to E = 128 GPa → f = 0.231).
- Sliding: f_s = 1 − (1 − 0.615)·AR/2.83, anchored on R28 (sliding, circle, AR 2.83 → f = 0.615).
- **Warning:** a similar analytic bonded-pillar model under-predicted R35 by 30 %, so these predictions carry roughly ±30 %.

| pad | AR | du_film | du_free | **bonded (pred.)** | **sliding (pred.)** | measured | bonded predicted verdict |
|---|---|---|---|---|---|---|---|
| 9 µm | 0.13 | 6.35 | 3.39 | **5.77** | 6.24 | 6.4 ± 0.4 | FAIL (−0.63, marginal) |
| 3 µm | 0.50 | 8.28 | 4.43 | **5.81** | 7.71 | 3.6–4.9 | FAIL (too large) |
| 1 µm | 1.50 | 8.28 | 4.43 | **3.28** | 6.59 | 2.3 ± 0.4 | FAIL (too large) |

**Predicted overall: FAIL.**
- The size trend is also predicted to fail marginally (5.77 vs 5.81).
- The sliding control is predicted to fail clearly on 3 and 1 µm, so the test should **discriminate** the sidewall condition.

**Which pad is decisive.**
- **The 1 µm pad.** Its bonded vs sliding separation (≈3.3 nm) is ~8× the tolerance. The measured 2.3 nm is *below the free-column value* 4.43 nm, so only a sidewall that drags the Cu down can reproduce it.
- The 3 µm pad is the second discriminator.
- The 9 µm pad is film-like, so the sidewall condition hardly matters there. It tests the materials and thin-film physics instead. Its measured 6.4 nm already exceeds the elastic constant-α film bound of 6.35 nm, so a bonded elastic model can at best just reach the band (≥ 6.0 nm needs f ≥ 0.945).
- A 9 µm failure would therefore point to α_Cu(T): a NIST-type α rising to ~18 ppm/K by 200 °C would lift the bound by ~5 %. Plasticity or grain effects are less likely there. **α_Cu is not changed here.**

**Literature prior pointing the other way.** Lin's Eq. (1), from an earlier FEM (their ref. 16, model details not given here), matches 3 and 1 µm. So a bonded elastic FEM can reach the measured values. Our crude interpolation may be the weak link, not the bonded model.

## 7. Outcome (added after R40–R56; sections 1–6 unchanged; pre-registration commit f96a007, results commit c33ec12)
All runs exit 0 with every load step completed, except **R49** (report only; see below).

| pad | orientation | bonded du (nm) | sliding du (nm) | measured (nm) | bonded pass |
|---|---|---|---|---|---|
| 9 µm | iso (Hill) | **7.36** (R40) | 7.37 (R46) | 6.4 ± 0.4 | **FAIL** (+0.96) |
| 3 µm | iso (Hill) | **5.55** (R41) | 6.61 (R47) | 3.6–4.9 | **FAIL** (+0.65 above range; +35 % vs 4.1) |
| 1 µm | [001] | **2.23** (R43); 2.35 with cell ×2 (R53) | 5.93 (R48) | 2.3 ± 0.4 | pass |
| 1 µm | [101] | 2.47 (R44) | — | 2.3 ± 0.4 | pass |
| 1 µm | [111] | 2.59 (R45) | — | 2.3 ± 0.4 | pass |

- **Size trend 9 > 3 > 1: true.**
- **PRIMARY VERDICT (bonded): FAIL.** The 9 and 3 µm pads are over-predicted; the 1 µm pad and the trend pass.
- **Sliding control FAILS** on 3 µm (6.61) and on 1 µm (5.93, i.e. 2.6× the measurement), so the test **discriminates** the sidewall condition.
  - Only the bonded sidewall reproduces the 1 µm pad.
  - At 9 µm the two conditions are identical (7.36 / 7.37): film-like, sidewall-insensitive, as predicted.

**Checks**
- Cell ×2:
  - 9 µm −0.3 % and 3 µm +1.0 % (both < 2 %);
  - **1 µm [001] +5.3 % (> 2 %)**. Pre-registered rule applied: the ×2 value 2.35 nm replaces R43 for pass/fail, and the verdict is unchanged.
  - [101] and [111] were not re-run at ×2. With the same +5 % they would be ≈ 2.60 / 2.73, still overlapping 2.3 ± 0.4.
  - A further enlargement of the 1 µm cell is still owed.
- 3D vs 2D, same isotropic 1 µm pad (R55 vs R42): 2.42 vs 2.38 nm, +1.9 %. This verifies the 3D tapered mesh.
  - The 3D O-grid has 272 shape warnings: corner elements of the pad circle, up to 174°. This is the same O-grid as R27/R28, and its effect on du is within this +1.9 %.
- Mesh ×2, 3 µm (R56 vs R41): 5.551 vs 5.552 nm, 0.0 %.
- Taper 18° vs 7.6°, 1 µm iso (R54 vs R42): 1.98 vs 2.38 nm, −17 %.
- SiO2 reference = AFM-field mean (report only): 7.19 / 5.06 / 2.08–2.43 nm. 9 and 3 µm still fail.
- Plastic (report only):
  - R50, 3 µm: 5.58 nm (+0.5 %), max ε_p 2.5e-3.
  - **R49, 1 µm [001], did not solve.** MAPDL: "The TB,PLAS table cannot work with the TB,ANEL table for material 1." See the note below.

**Comparison with the pre-registered predictions**
- Bonded predictions were 5.77 / 5.81 / 3.28; FEM gives 7.36 / 5.55 / 2.23–2.59.
- The 9 µm pad exceeds my "thin-film bound" (6.35 nm) by 1.0 nm. That bound assumed a rigid substrate.
  - Decomposition at 200 °C: Cu centre +19.56 nm vs SiO2 edge +11.97 nm. The film estimate for the Cu column is 18.52 nm.
  - The extra ≈ 1 nm comes from local elastic deformation of the Si/SiO2 under the compressed Cu pad. It is stable under cell and Si ×2 (−0.3 %), so it is a property of the elastic model, not a boundary artefact.
  - The bound was therefore wrong, not the FEM.
- The interpolation model was off by +28 % / −5 % / about −25 % for 9 / 3 / 1 µm. It is not reliable for prediction (consistent with Step 12).

**Reading (no tuning done).**
- The bonded elastic model with literature properties reproduces the small, constraint-dominated pad (1 µm). The sliding model does not.
- The model over-predicts the larger pads by 15 % (9 µm) and 35 % (3 µm, vs the array mean 4.1).
- Lin's own Eq. (1) FEM had the opposite problem at 9 µm (40 % *under*-prediction), so the large-pad behaviour is not settled in the literature either.
- Unstated or uncertain inputs that act mainly on the larger pads (not tested, listed only):
  - real α_Cu(T) and E(T);
  - PECVD SiO2 modulus/CTE and its thickness under the pad (0.5 µm assumed);
  - Ta;
  - polycrystal grain-boundary or plastic relaxation (R50 shows little in Ludwick v1);
  - the AFM square-region size.

**Note — R49 failure affects later plastic work.**
- Our 3D decks combine TB,ANEL + TB,PLAS (MISO) on SOLID185 with KEYOPT(2) = 3 (simplified enhanced strain) and thermal strain.
- The earlier cp_check, which passed, used the same TB,ANEL + MISO with default SOLID185 (KEYOPT(2) = 0) and mechanical loading only.
- **The Stage 1 plastic runs R05–R07 use the same ANEL + MISO + KEYOPT(2) = 3 + thermal combination and may fail the same way.**
- A one-element diagnostic (KEYOPT(2) = 0 vs 3, with and without ALPX) is needed before any plastic run. Not run yet.
