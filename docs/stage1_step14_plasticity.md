# Stage 1 · Step 14 — Plasticity-path diagnosis and large-pad plasticity check (pre-registered BEFORE any run)

**Status.** Pre-registration; no Step 14 run made. The Step 13 verdict (FAIL) stays as recorded, and nothing here changes it.
**Code.**
- `src/stage1/step14.py`: Part A one-element cases, Part A recommendation, Part C evaluation.
- `src/stage1/lin13.py`: Part C runs R57 and R58 are **appended** to the registry. R40–R56 decks are unchanged (physics hashes re-checked).
- `stage1_pipeline.py` and `s1_mesh.py` are not modified, so R01–R49 decks are unchanged.

## Part A — which input combination works (no physics conclusions)
**A1. History (from the repo).**
| run | elastic input | TB,PLAS form | element | thermal strain | NLGEOM | result |
|---|---|---|---|---|---|---|
| `validation_cp_check` (ANEL+MISO, 4 orientations) | TB,ANEL, prerotated | **one temperature** (`TB,PLAS,1,1,n,MISO` + `TBTEMP,25`) | SOLID185 **KEYOPT(2)=0** (default) | **off** (displacement load only, no ALPX) | ON | **completed**, yield error ≤ 0.43 % |
| R05–R07 (Stage 1 plastic, pads 3/6/1/2) | TB,ANEL | variant ① one temperature; ②/③ 8-temperature table | KEYOPT(2)=3 | on | OFF | **never run** |
| R49 (Lin 1 µm [001] plastic) | TB,ANEL | **one temperature** (`TB,PLAS,1,1,19,MISO` + `TBTEMP,25`) | **KEYOPT(2)=3** | **on** (MP,ALPX + MP,REFT) | **OFF** | **failed**: "The TB,PLAS table cannot work with the TB,ANEL table for material 1." |

- R49 already used the one-temperature form, so the "table" in the message is **not** the temperature table.
- R49 and the working cp_check differ in three settings: KEYOPT(2) (3 vs 0), thermal strain (on vs off) and NLGEOM (OFF vs ON).

**A2. Documentation.**
- The v261 *Material Reference* is behind the Ansys Help login and could not be retrieved here. **No exact v261 quote is available.**
- Public v242 pages found:
  - Material Reference §3.3, *Anisotropic Elasticity*: "Anisotropic elastic capability (**TB**,ANEL or **TB**,ELAS,,,,AELS/AELF) is available with current-technology plane and solid elements."
  - Command Reference, TB, ANEL: "This material model is not supported for use with the coefficient of thermal expansion (**TB**,CTE)." We use MP,ALPX, not TB,CTE.
- The "Material Model Combinations" table (which plasticity models may be combined with ANEL) was **not retrieved**. **Action for the user:** check Ansys Help v261 → Material Reference → *Material Model Combinations* and paste the ANEL row.
- Documented alternatives tested below:
  - TB,ELAS,,,,**AELS** (the second anisotropic-elastic input form named in §3.3);
  - **ORTHO**: cubic Cu as orthotropic MP constants (EX = EY = EZ, PRXY, GXY) with isotropic thermal expansion and von Mises MISO. For rotated pads this requires the ESYS crystal-frame route that was validated for elasticity in G3.

**A3. Test matrix (32 one-element cases, A01–A32).**
- Setup: SOLID185 1 µm cube, Cu z ∥ [001], µMKS units, roller BCs on x = 0, y = 0, z = 0.
- Elastic input {ANEL, AELS, ORTHO} × KEYOPT(2) {0, 3} × TB,PLAS {T1 = one temperature, T2 = two-temperature table (25 °C and 400 °C, the 400 °C curve = 0.8 × the 25 °C curve)} × thermal {off, on}, all at NLGEOM OFF. That is 24 cases.
- Plus the 8 ANEL cases at NLGEOM ON (cp_check setting).
- Load steps:
  - LS1: free heating 25 → 400 °C (thermal on), or no load (thermal off);
  - LS2: uniaxial pull to mechanical strain 5e-4 (elastic);
  - LS3: pull to 1e-2 (plastic).
- MISO curve: pad-3 Ludwick midpoint (σ0 143, K 675, N 0.685 MPa).

**A4. Analytic checks** (all < 1 % for "correct"):
- LS1 thermal strain = α·ΔT = 16.5e-6 × 375 = 6.1875e-3;
- LS2 σz/ε = E[001] = 66.69 GPa;
- LS3 σz = MISO curve at the computed EPPL,EQV, at the current temperature (T2 cases use the 400 °C curve when heated).

**A5. Output and pre-registered selection rule.**
- Output: `results/diagnostics/step14_partA.csv` (combination → runs? / correct?) and `step14_partA_recommendation.txt`.
- Production settings = KEYOPT(2) = 3, thermal on, NLGEOM OFF.
- **Recommendation = the first of ANEL → AELS → ORTHO that is correct at production settings with the T1 form.**
  - Report whether the T2 form also works; variants ②/③ need it.
- If none works at production settings but one works with KEYOPT(2) = 0, **stop**: changing the element formulation needs the user's decision.
- If nothing works with thermal strain, **stop and list options**. The agent does not pick.

**A prediction** (written before the runs):
- ANEL and AELS fail with KEYOPT(2) = 3 and work with KEYOPT(2) = 0, including with thermal strain.
- ORTHO works in all cases.
- Expected recommendation: ORTHO with KEYOPT(2) = 3, using the ESYS crystal-frame route for rotated pads. Confidence is low: this is a guess based only on the cp_check vs R49 difference.

## Part B — 300 nm plasticity threshold (only if Part A gives a recommendation)
- **Configuration:** paper-literal bonded, no cap, circle (R27 configuration). Heating per the Ayoub history (load step 0 from T_sf to 30 °C, then to 400 °C). Δu = G4b u_center from 30 to 400 °C, end of heating.

| pad | elastic | plastic |
|---|---|---|
| 3 (E_z 68.0, T_sf 275) | R35 (done) | **R59**: Ludwick variant ① (pad-3 curve, T-independent) with the Part-A input; deck built after Part A |
| 10 (E_z 189.5, T_sf 277) | R27 (done) | E_z > 130.34 GPa, so elastic by the mapping rule. The plastic deck is identical to R27 (R08 precedent): **no solve**, Δ = 0 by rule |

- **Rule (pre-registered):** if |Δu_plastic − Δu_elastic| < 0.1 nm for both pads, Stage 2 uses elastic Cu. Otherwise it uses plastic Cu.
- **Prediction:** R35's volume-averaged stress at 30 °C (σlat 218, σz 348 MPa) gives von Mises ≈ 130 MPa, below σ0 = 143 MPa. At 400 °C it is about half that. Yielding is therefore only local, and |Δu| < 0.1 nm is predicted, i.e. **elastic** for Stage 2.

## Part C — large-pad plasticity (explanatory only)
- R57: 9 µm, bonded, 2D, isotropic Hill Cu, Ludwick variant ① through the computed-E mapping. E_Hill = 128.3 GPa gives a pointwise interpolation between pads 1 and 2. Same geometry and assumptions as Step 13; **no tuning**.
- 3 µm: **already solved as R50** (Step 13 report-only, same settings). It is reused, not re-run.
- **Hypothesis SUPPORTED** if the plastic Δu closes ≥ 50 % of the gap to the measurement for **both** pads, i.e. (Δu_el − Δu_pl)/(Δu_el − measured) ≥ 0.5 with measured 6.4 and 4.1 nm. Otherwise NOT SUPPORTED, and the large-pad miss is recorded as unexplained. Geometry uncertainty (taper −17 %) remains the other candidate.
- **Disclosure:** the 3 µm number is already known. R50 = 5.58 nm vs elastic R41 = 5.55 nm, so the gap closed is −2 %. Under the rule above, Part C **cannot be SUPPORTED** whatever R57 gives. R57 is still run for the record.
- **Physics prediction (why plasticity is expected to *increase*, not decrease, Δu on heating):**
  - Model a film-like pad on heating as in-plane compression with free top, and an in-plane total strain fixed by the substrate.
  - Plastic flow at constant volume gives ε_p,zz = −2 ε_p,xx > 0.
  - Then ε_zz − αΔT = 2ν/(1−ν)·ε_m + ε_p,xx·(2ν/(1−ν) − 2). With ν = 0.345 the bracket is −0.94 and ε_p,xx < 0.
  - So **compressive in-plane yielding raises the protrusion.** This holds for any T_sf under isotropic hardening.
  - Prediction: R57 Δu ≥ R40 Δu (gap closed ≤ 0) → **NOT SUPPORTED**.
- **Pending 1 µm cell check (elastic):** R58 = 1 µm [001] bonded, cell 9 w (next step after 6 w; 104 040 nodes). The criterion is still < 2 % change vs R53 (6 w). If it is not met, the cell effect is reported as an open uncertainty of the 1 µm result.

## Deliverables and order
1. Commit this document **before** any run (hash reported).
2. Run Part A (A01–A32), R57, R58, then the Part A and Part C evaluation.
3. Commit the results.
4. Build R59 only if Part A gives a recommendation, then run, evaluate Part B, commit.
5. Tables for A, B, C and a Korean summary in docs/stage1_summary_for_PI_ko.md.

---
## Results (after the pre-registration commit 29d587a; run commit 58a6c10)

### A. One-element matrix: first run (`results/diagnostics/step14_partA.csv`)

| group | cases | runs? | analytic checks |
|---|---|---|---|
| ANEL, every setting (K0/K3 × T1/T2 × thermal off/on × NLGEOM OFF/ON) | 16 | **no**: "The TB,PLAS table cannot work with the TB,ANEL table for material 1." (step-data check, before solving) | — |
| AELS and ORTHO, thermal off | 8 | yes | all pass (E_z 66.69 GPa within 1e-8, flow stress within 1e-6) |
| AELS and ORTHO, thermal on | 8 | yes | thermal strain passes; E_z **+127 %** (T1) / +211 % (T2), flow stress +1.6 % / +2.6 % → "not correct" |

- The pre-registered rule returned "NOTHING works with thermal strain → stop".
- **The A prediction was wrong for ANEL.** ANEL fails at *every* setting, including the exact cp_check settings (A25). The three-setting explanation (KEYOPT(2), thermal, NLGEOM) is refuted.

**A6. Deviations (post hoc, disclosed; nothing in the pre-registered rules changed)**

1. **The thermal-on failures are a test-deck error, not an ANSYS result.**
   - The top-face UZ constraint is first applied in LS2. MAPDL ramps a *new* constraint from 0, not from the free-expansion value.
   - So the first LS2 substep pushes the expanded cube (UZ 6.19e-3) back to 3.3e-3. That is a compressive mechanical strain of about −2.8e-3, i.e. a stress of about −190 MPa, beyond σ0 = 143 MPa. The cube yields in compression before it is pulled.
   - This gives the observed numbers: LS2 σ = 75.7 MPa instead of 33.3 MPa, the same in AELS and ORTHO; the error is larger for T2 because its 400 °C curve is lower.
   - Fix: KBC,1 (step) in LS2 only; LS3 ramps from the previous value. Re-run as A10f–A24f (`--partA-fix`); the original decks are kept unchanged.
   - The pre-registered selection rule is then applied to {thermal-off rows of the first run + the fixed thermal-on rows}.
2. **Run mode vs deck content for ANEL.** cp_check ran the same ANEL + TB,PLAS MISO commands successfully through PyMAPDL (interactive), while all batch decks fail. Three diagnostics (`step14_partA_modecheck.csv`) separate the two:
   - X1: the cp_check deck in batch;
   - X2: the A25 deck through PyMAPDL;
   - X3: the cp_check deck through PyMAPDL (replication).
   - This is diagnostic only. It does not change the selection rule, which looks only at the production path (batch).

### C. Large pads (`step14.py --partC`)

| pad | elastic Δu (nm) | plastic Δu (nm) | measured | gap closed |
|---|---|---|---|---|
| 9 µm | 7.361 (R40) | **7.599 (R57)** | 6.4 | **−24.7 %** |
| 3 µm | 5.552 (R41) | 5.582 (R50) | 4.1 | −2.1 % |

- **NOT SUPPORTED, as predicted.** In-plane yielding makes the over-prediction *larger*, not smaller: R57 max εp = 1.6e-3 at 200 °C (constant-volume flow pushes the top up).
- The large-pad miss stays unexplained by plasticity. The remaining candidates are geometry (taper sensitivity −17 %) and the Si/SiO2 constraint.

**1 µm cell check.** R53 (6 w) 2.346 nm → R58 (9 w) 2.355 nm, a **+0.39 %** change. The < 2 % criterion is **met**. The converged 1 µm [001] value is 2.35 nm, which passes against 2.3 ± 0.4 nm.

### A (final, commit 1eb83c2): `step14_partA_fix.csv`, `step14_partA_modecheck.csv`

| case | input | KEYOPT(2) | MISO | thermal | αΔT err | E_z err | flow err |
|---|---|---|---|---|---|---|---|
| A10f / A14f | AELS | 0 / 3 | T1 | on | 2e-13 | 5e-9 | −7e-7 |
| A12f / A16f | AELS | 0 / 3 | T2 | on | 2e-13 | 5e-9 | −2.3e-4 |
| A18f / A22f | ORTHO | 0 / 3 | T1 | on | 2e-13 | 5e-9 | −7e-7 |
| A20f / A24f | ORTHO | 0 / 3 | T2 | on | 2e-13 | 5e-9 | −2.3e-4 |

- With the LS2 load fixed, every thermal-on case passes all three checks.
- **Pre-registered recommendation: AELS (TB,ELAS,,,,AELS) with KEYOPT(2)=3.** The two-temperature table (variants ②/③) also works.
- AELS takes the same 21-constant prerotated matrix, so the ESYS route is not needed.

**Run-mode check (X1–X3).**

| id | deck | mode | ANEL+PLAS error printed | result file |
|---|---|---|---|---|
| X1 | cp_check | batch | yes | no (stops) |
| X2 | A25 | PyMAPDL | yes | **yes** |
| X3 | cp_check | PyMAPDL | yes | **yes** |

- **The rejection is the same in both modes.** In batch the step-data error stops the run. In an interactive (PyMAPDL) session the same ERROR is printed but the solve continues.
- The earlier cp_check "ANEL + MISO pass" was therefore obtained **through an ERROR that the interactive session did not stop on**. Its numbers are close to AELS (X2 flow stress −0.07 % vs A09), but they come from an unsupported combination. The cp_check Ludwick result is **superseded** by Part A AELS.
- Consequence: every registry plastic run with the default ANEL input (R05–R07, R09–R17, R19, R21, R23) would stop in batch. Plastic runs must use `el_input="AELS"` under new run IDs; the old decks stay unchanged.
- The A prediction (ANEL fails only at KEYOPT(2)=3; ORTHO works) was **wrong** for ANEL and **right** for ORTHO.

## Part B addendum (pre-registered before R59/R60 and the B0 runs; the addendum commit hash is in git)

- **Input:** the Part A recommendation, `el_input="AELS"`.
  - New, non-default parameter in `stage1_pipeline.material_block`. The default "ANEL" leaves all R01–R39 decks byte-identical (checked: 38 decks equal; R09 is not buildable without NIST data, as before).
- **Gate B0** (`step14.py --partB0`): AELS must read the *rotated* 21 constants in the same order as ANEL.
  - Setup: one element, all nodes prescribed u = ε·x with a general strain (all six components non-zero), elastic only.
  - Orientations: pad 3, pad 10, [111]; each with ANEL and AELS.
  - Pass if |σ_FE − D·ε| / max|D·ε| < 1e-4 for all 6 cases.
- **Gate R60:** pad 3 elastic, paper-literal, AELS. The decks differ from R35 only in the TB line (checked). Required: |u_center(400) R60 − R35| < 1e-3 nm.
- **R59:** pad 3, plastic variant ① (pad-3 Ludwick curve, T-independent), paper-literal (circle, no cap, bonded), AELS, same history as R35.
- **Rule (unchanged):** Δ = u_center(h400)[R59] − u_center(h400)[R35].
  - Pad 10 has Δ = 0 by the mapping rule.
  - If both gates pass and |Δ| < 0.1 nm → Stage 2 uses elastic Cu. If |Δ| ≥ 0.1 nm → plastic Cu. If either gate fails → no verdict.
  - Reported in addition, not ruled on: max εp, and the residual u at 30 °C after the cycle.
- **Prediction (unchanged):** |Δ| < 0.1 nm, i.e. elastic Cu for Stage 2.
