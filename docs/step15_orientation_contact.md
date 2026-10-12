# Step 15 — Orientation-aware contact check for a 1 µm Cu pad (pre-registered BEFORE R63–R71)

**Status (2026-10-13): PARKED, not run.** The user paused this step. R63-R71 exist in the lin13.py registry but have never been solved. src/stage2/s15_contact.py has been tested only on mock data.


**Why now.** A short paper is due this week. Step 14 Part B (300 nm plasticity) has no verdict: R61 was stopped by the user, with a projected 1–2 days of run time. This step answers the research question with the **validated** Lin 2025 model (1 µm pad, bonded sidewall: Step 13 pass, cell converged in R58). The answer is restricted to elastic Cu.

## Runs (`lin13.py`, appended; R40–R58 decks unchanged, byte-compared)
- **Setup:** 1 µm pad, 1.5 µm Cu, bonded sidewall, 3D, cell 6 w; Δu from 25 to 200 °C (as in Step 13).
- **R63–R70:** anisotropic Cu, z ∥ the following orientations:

| run | orientation | E_z (GPa) |
|---|---|---|
| R63 | [001] | 66.7 |
| R64 | [101] | 130.3 |
| R65 | [111] | 191.1 |
| R66 | Ayoub pad 3 | 68.0 |
| R67 | Ayoub pad 6 | 102.3 |
| R68 | Ayoub pad 1 | 127.3 |
| R69 | Ayoub pad 4 | 169.4 |
| R70 | Ayoub pad 5 | 188.3 |

- R63 is physically identical to R53. It serves as a determinism check: it must equal R53 within 1e-6 nm.
- **R71:** isotropic Hill Cu ("average Cu").

## Analysis (agent, from record.json; script `src/stage2/s15_contact.py`)
1. **Fit.** Fit Δu(E_z) quadratically to R63–R70 and report R² and the maximum residual. In the elastic model Δu is linear in ΔT, so the per-pad rate is k = Δu/175 nm/K.
2. **Contact.** Two pads face to face with total recess g (top + bottom). Contact at anneal temperature T if (k_top + k_bot)·(T − 25) ≥ g.
3. **Average-Cu design.** T_avg = 25 + g/(2 k_Hill), with k_Hill from R71.
4. **Monte Carlo.** 200 000 pad pairs; independent, uniformly random orientations (no texture); seed 0. Recess g = g0·(1 + ε) with ε ~ N(0, cv), cv ∈ {0, 0.1, 0.2}.
5. **Outputs:**
   - P(contact | T_avg);
   - T99 and T99.9 (temperatures giving 99 % and 99.9 % contact);
   - worst-orientation-pair temperature T_worst;
   - for g0 ∈ {3, 5, 8} nm: a P(contact) vs T curve and a contact-probability map over (T, g0).
6. **Hypothesis (H15).** T_avg does **not** guarantee contact: P(contact | T_avg) < 99 % for every cv.
7. **Secondary result.** The anneal-temperature overshoot (T99 − T_avg) needed to reach 99 %.

**Predictions.**
- P(contact | T_avg) ≈ 50 % (T_avg sits near the median of the pair rate).
- The k spread is about ±8 % (Step 13: 2.23–2.59 nm), so T99 − 25 ≈ 1.05–1.10 × (T_avg − 25) at cv = 0.
- The recess spread (cv) dominates over orientation once cv ≥ 0.1.

## Limitations (stated in the paper)
- Elastic Cu only. 300 nm plasticity is unresolved; R35 peak von Mises is about 4 × σ0. For large pads, plasticity *raises* Δu (Step 14 C), so elastic is likely conservative there.
- Lin geometry (1 µm × 1.5 µm), not 300 nm.
- Linear extrapolation above 200 °C.
- Random texture only.
- The recess distribution is assumed, not measured.
- Large-pad over-prediction (9 and 3 µm) remains unexplained.
