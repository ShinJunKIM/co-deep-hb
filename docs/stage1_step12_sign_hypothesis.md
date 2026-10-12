# Stage 1 · Step 12 — Sign-convention hypothesis H_sign (pre-registered 2026-10-11, BEFORE R35–R39)

**Observation (user).** R27 (paper-literal: circular pad, no cap, bonded sidewalls, no liner) gives ε′zz(T) ≈ −(0.93…0.98) × Ayoub's own elastic FEM curve for pad 10, at every temperature: +1.143 vs −1.181 at 30 °C and −0.569 vs +0.613 at 400 °C.
Ayoub's thesis (see §5) confirms that his FEM is Cu + SiO2 + Si only, with symmetric sides and a fixed bottom, i.e. the R27 configuration.

**H_sign.** Ayoub reports ε′zz, both measured and FEM, with the opposite sign to ours (ours: ε′zz = EPEL_zz − tr(EPEL)/3, Cu volume average, global frame).

**Why the earlier "coincidence" verdict is re-tested.**
- That verdict rested on R01 (cap + bonded) and on the observation that our own post-processing is internally consistent (R26 has the opposite sign).
- Neither excludes a sign difference between *our* convention and *Ayoub's*.
- R27 is Ayoub's own model, so the mirror between R27 and his FEM must be explained.

## 1. Runs (registry step 12; pad 10 = R27, already solved)
| Run | pad | E_z (GPa) | T_sf (°C) | configuration |
|---|---|---|---|---|
| R35 | 3 | 68.04 | 275 (own) | as R27, elastic |
| R36 | 4 | 169.39 | 277 | as R27, elastic |
| R37 | 5 | 188.35 | 277 | as R27, elastic |
| R38 | 7 | 164.64 | 277 | as R27, elastic |
| R39 | 9 | 164.18 | 277 | as R27, elastic |

- Decks differ from R27 only in the rotated Cu stiffness (TBDATA) and the title.
- R35 also differs in T_sf, which changes TREF/REFT and the α_Si wall displacements.
- R01–R34 decks are unchanged: all physics hashes were re-checked.
- Nothing else in the model is changed.

## 2. Pre-registered criteria (evaluated by `src/tools/step12_hsign_compare.py`)
**Test A (decisive): R35 vs −(Ayoub's pad-3 elastic FEM curve, Fig. 3b red).**
- The red curve was digitized at 30 / 100 / 400 °C (−1.416 / −1.017 / +0.726e-3). It is linear: the line fit leaves −0.004e-3 at 100 °C. Between 150 and 350 °C it is hidden under the plastic curve, so the line is used there.
- Where |FEM| ≥ 0.3e-3: 0.90 ≤ model/(−FEM) ≤ 1.10.
- Near the zero crossing (250 and 300 °C): |model + FEM| ≤ 0.10e-3, about one error bar.
- **H_sign passes Test A only if every heating temperature from 30 to 400 °C passes.**

**Test B: pads 4, 5, 7, 9, 10. Model Δε′zz (30 °C → 400 °C after the 2 h hold) vs −(Fig. 2c Δ).**
- r_p = Δ_model / (−Δ_meas); tol_p = max(10 %, err_p/Δ_meas,p).
- B-consistency (the Step 11 rule): |r_p/r̄ − 1| ≤ tol_p for all five pads.
- B-absolute (H_sign implies no calibration): |r_p − 1| ≤ tol_p for all five pads.

**Decision.**
- H_sign is **supported** if A passes and B-absolute passes.
- If A passes but B fails, the sign explains Ayoub's FEM but not the orientation data.
- If A fails, H_sign is not supported.

**Secondary, report only: offset-free orientation check.** q = [model(pad 3)/model(pad 10)] / [FEM(pad 3)/FEM(pad 10)] at 30 °C and 400 °C. This removes any common offset between our R27 and Ayoub's model, such as SiO2 E 70 vs 72 GPa, pad 0.32 vs 0.30 µm or in-plane Euler angles (§5).

## 3. Pre-registered predictions (analytic, written before the runs)
**Model used.** A bonded pillar with two constraints:
- laterally, a Cu column in a hole of stiffness K;
- axially, Cu total strain tied to an effective matrix expansion α_m,z.
K = 59.6 GPa and α_m,z = 9.07 ppm/K are fixed by matching R27's Cu σlat = 197.7 and σz = 454.5 MPa at 30 °C. The model then reproduces R27's ε′zz(30) = 1.147 vs 1.143 (FEM).

**Test A, pad 3.** σlat 206, σz 296 MPa at 30 °C (σz/σlat = 1.44, against 2.30 for pad 10).

| T (°C) | 30 | 100 | 150 | 200 | 250 | 300 | 350 | 400 |
|---|---|---|---|---|---|---|---|---|
| model (pred.) | +1.247 | +0.891 | +0.636 | +0.382 | +0.127 | −0.127 | −0.382 | −0.636 |
| −FEM | +1.419 | +1.013 | +0.724 | +0.434 | +0.144 | −0.146 | −0.436 | −0.725 |
| ratio / check | 0.879 | 0.879 | 0.879 | 0.880 | 0.017 ✓ | 0.019 ✓ | 0.877 | 0.877 |

- **Predicted: Test A FAIL by a small margin** (ratio 0.88 against the 0.90 bound).
- The analytic model has matched FEM to within about 2–5 % before, so the outcome is **genuinely uncertain**.
- Predicted q = 1.087 / 1.199 = **0.91**.

**What Test A can and cannot discriminate (stated before the runs).**
- In a bonded pillar the Cu elastic strain is largely set by geometry, so ε′zz depends only weakly on orientation. The predicted pad3/pad10 ratio is 1.09.
- Ayoub's elastic FEM has pad3/pad10 = 1.20 at 30 °C and 1.18 at 400 °C.
- A σz = 0 (sliding/free) model would give 2.52 (Step 11 analytic).
- So Ayoub's FEM already has the *weak orientation dependence of a bonded model*, which supports "Ayoub's FEM = our bonded model with the opposite sign".
- Test A cannot separate two variants of this:
  - **(i) H_sign proper:** measurement and FEM are both sign-flipped.
  - **(ii) FEM-only:** only Ayoub's FEM post-processing differs, and his FEM-measurement agreement is the same σz ≈ 2σlat mirror we found for R01.
- Test B (against −measured) is what tests (i).

**Test B (predicted).**
| pad | Δ_model (pred.) | −Δ_meas | r | r/r̄ − 1 | tol | cons. | abs. |
|---|---|---|---|---|---|---|---|
| 10 (R27) | −1.718 | −1.806 | 0.951 | +10.8 % | 11.0 % | pass | pass |
| 4 | −1.746 | −2.363 | 0.739 | −13.9 % | 10.0 % | **fail** | **fail** |
| 5 | −1.719 | −1.854 | 0.927 | +8.1 % | 11.1 % | pass | pass |
| 7 | −1.752 | −2.406 | 0.728 | −15.1 % | 10.0 % | **fail** | **fail** |
| 9 | −1.753 | −1.854 | 0.945 | +10.2 % | 10.8 % | pass | pass |

- **Predicted: Test B FAIL** on both rules, from pads 4 and 7.
- Structural reason: pads 7 and 9 have almost identical elastic responses in *every* model we have (bonded: 1.752 / 1.753; σz = 0: 1.105 / 1.103 from FEM in Step 11).
- Their measured Δ differ by 30 % (2.41 vs 1.85).
- No elastic, orientation-only model of either sign can pass Test B unless pad 9's Table 1 hkl is wrong.

## 4. Physical-consistency check on H_sign (i) — report only, no run
- Thesis p.53 (PDF p.54) states that at 30 °C a negative ε′zz is observed "for all pads whatever their size". Thesis Fig. 2.10 shows −0.5…−2e-3 for **3 µm-wide** pads as well.
- A 3 µm-wide, ~0.85 µm-thick pad with a free top is close to a film. After cooling below T_sf its stress is in-plane tension with σz ≈ 0, which gives ε′zz < 0 **in our convention**.
- Under H_sign (i) the 3 µm pads would have ε′zz > 0 in our convention, i.e. σz > σlat in a flat pad. That is implausible.
- This argues against (i) and for (ii). It could be tested with one wide-pad R27-type run, but that is **not proposed now**.

## 5. Literature search on the sign and frame definition
**Ayoub thesis** (B. Ayoub, PhD thesis, Univ. Bordeaux (IMS), defended 4 May 2023, HAL tel-04437757; printed page numbers, with PDF page = printed + 1).
- **No explicit sign or frame definition of ε′zz** for the measurement or for the FEM post-processing was found. A keyword search for deviatoric / LaueTools / sign / convention / frame / tension found none.
- p.48: Laue gives the deviatoric part relative to a theoretical or experimental reference, with a relative precision of 1e-4.
- pp.50–52: data were analysed with LaueTools (calibration on Si at every temperature, then peaksearch, Indexrefine, buildsummary, plotmap). LaueNN was used for orientation only.
- p.52: the quantity studied is the deviatoric strain "perpendicular to the pad surface (i.e., Z direction)".
- p.53: ε′zz < 0 at 30 °C for all pads (0.32 and 3 µm).
- p.57: suggests σzz = 0 at the free surface as a route from deviatoric to full strain. Not used.
- pp.58–60, Fig. 2.11 and Table 2.2: the COMSOL model is Cu + SiO2 + 750 µm Si, symmetric BCs, fixed bottom.
  - SiO2 **E = 70 GPa**; ours is 72.
  - Pad **0.32 µm** wide; ours is 0.30.
  - Cu rotation from the **Euler angles of each pad**; ours uses an in-plane angle of 0°.
  - Elastic Cu CTE 16.5 ppm/K; T_sf "deduced for each single pad from the experimental curves".
  - p.60: only heating is simulated.
- **None of these differences can flip a sign.** They are listed and not changed, as instructed.

**LaueTools** (J.-S. Micha, "NOTES on LaueTools indexing, strain refinement and simulation", ESRF BM32).
- p.1: "P is the deformation full tensor of the reciprocal space which is the opposite of the deformation full tensor of the real space."
- pp.2–3: in `crystalparameters.py` the strain is derived from **direct**-lattice parameters: fullstrain = ½(T + Tᵀ) − Id with A = T·A0, and deviatoric = full − tr/3·Id. Sample-frame tensors are obtained by rotating ±40° about Y.
- So a documented mechanism for a sign flip exists: using the reciprocal-space tensor, or a sample/lab-frame mix-up. But the documented LaueTools output is real-space.
- LaueTools 3.2.11 release notes: sample-frame strain was corrected for **non-orthogonal** cells only. Cubic Cu is not affected.
- **Nothing found states which tensor Ayoub used.** This becomes a question for the authors.

## 6. Outcome (added after R35–R39; sections 1–5 unchanged; pre-registration committed in 23fb7b1 before the runs)
All five runs exit 0 and converged, global frame, 49000 nodes.

**Test A — FAIL.** R35 is the mirror of Ayoub's pad-3 FEM in shape, but **26 % too large** at every temperature.
| T (°C) | 30 | 100 | 150 | 200 | 250 | 300 | 350 | 400 |
|---|---|---|---|---|---|---|---|---|
| R35 | +1.786 | +1.276 | +0.911 | +0.547 | +0.182 | −0.182 | −0.547 | −0.911 |
| −FEM | +1.419 | +1.013 | +0.724 | +0.434 | +0.144 | −0.146 | −0.436 | −0.725 |
| ratio / check | 1.259 | 1.259 | 1.260 | 1.261 | 0.038 ✓ | 0.037 ✓ | 1.255 | 1.257 |

- Pad 10 under the same comparison gives 0.93–0.97.
- Offset-free q = 1.30 (30 °C) and 1.35 (400 °C), against the predicted 0.91. Our bonded model has a stronger orientation dependence (pad3/pad10 = 1.56–1.60) than Ayoub's FEM (1.18–1.20).
- The pad-10 mirror therefore does **not** repeat for a pad with a different stress ratio (R35: σz/σlat = 1.60 at 30 °C; pad 10: 2.30).
- The listed model differences (SiO2 E 70 vs 72 GPa, width 0.32 vs 0.30 µm, in-plane Euler angle with an axisymmetric pad) are each expected to change ε′zz by a few percent, not 26 %. This is an expectation, not tested.
- **Prediction check:** the analytic bonded-pillar model predicted 0.88. It under-estimated R35 by 30 % (1.247 vs 1.786). The verdict matches the prediction (FAIL), but for the opposite reason: too large rather than too small.

**Test B — FAIL** (consistency and absolute), as predicted.
| pad | run | Δ_model | −Δ_meas | r | r/r̄ − 1 | tol | cons. | abs. |
|---|---|---|---|---|---|---|---|---|
| 10 | R27 | −1.712 | −1.806 | 0.948 | +8.2 % | 11.0 % | pass | pass |
| 4 | R36 | −1.801 | −2.363 | 0.762 | −13.0 % | 10.0 % | fail | fail |
| 5 | R37 | −1.716 | −1.854 | 0.926 | +5.7 % | 11.1 % | pass | pass |
| 7 | R38 | −1.824 | −2.406 | 0.758 | −13.5 % | 10.0 % | fail | fail |
| 9 | R39 | −1.828 | −1.854 | 0.986 | +12.6 % | 10.8 % | fail | pass |

- Pads 7 and 9 again give the same model Δ (−1.824 / −1.828), while the measured values differ by 30 %.

**Decision (pre-registered rule): H_sign is NOT supported.**
- Ayoub's FEM is not reproduced by our paper-literal model with a sign flip. The R27/pad-10 mirror is the same kind of coincidence as R01.
- The sign/frame question remains open, together with the boundary-condition question, for the authors.
