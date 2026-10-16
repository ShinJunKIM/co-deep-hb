# IEIE 2026f paper (v6): numbers in the text vs result files

Generated 2026-10-16 from the repository files. Text numbers come from docs/paper/ieie2026f_plan_and_draft_ko.md (v5.1) and are rounded as shown.

| Quantity | Text | File value | Source (results/stage2/) |
|---|---|---|---|
| Boundary, all combinations, clean, 2 h (≈250 °C; Fig. label 248) | 248 | 248.0 | v2/boundary_curves.json surfaces.clean.T_at_120min.robust |
| Boundary, all combinations, clean, 30 min | 285 | 285.3 | … T_at_30min.robust |
| Boundary, all combinations, clean, 5 min | 342 | 342.3 | … T_at_5min.robust |
| Boundary, main setting, clean, 30 min / 2 h | 253 / 220 | 253.0 / 219.6 | … .main |
| Boundary, all combinations, oxidised, 30 min / 2 h | 334 / 295 | 333.9 / 294.5 | surfaces.oxidised |
| Worst orientation, f(0)>0, 2 h | 265–290 | 264.7–289.8 | worst_orientation V5, V4 |
| Worst orientation, f(0)>0, 30 min | 304–324 | 304.0–324.0 | worst_orientation V5, V4 |
| Factor shifts 2 h/30 min: process group range | 25–49 | 25.1–48.8 | factor_shift_C Q, tau0, liner, surface |
| Factor shifts: pad-to-pad group range | 4–16 | 3.5–16.4 | factor_shift_C random*, orientation-tail |
| Time ratio 250 °C: tau0 / liner / oxide / recess σ / b | 5.0/4.5/2.9/1.2/1.2 | 5.0/4.5/2.9/1.2/1.2 | factor_shift_C *.time_ratio_250C |
| Q time ratio 320 → 220 °C (draft; not used in v6 text) | 1.4 → 4.7 | 1.3 → 4.7 | factor_shift_C Q |
| Elastic contact limit 400 °C, recess 3/5/8 nm (measured) | 0.55/0.70/1.0 | 0.55/0.70/1.00 | boundaries.json elastic_limit_measured_400C_um |
| Elastic limit, fit, 5 nm, 400/350/300/250 °C | 0.76/0.90/1.14/1.62 | 0.76/0.90/1.14/1.62 | boundaries.json elastic_limit_surrogate_um |
| Crossover (prediction) 250 °C 2 h … 400 °C 2 h | 0.74–2.45 | 0.74–2.45 | boundaries.json crossover_um |
| Diffusion rev. 1: held-out pass; ≥250 °C PPA; ≥250 °C all | 11/17; 5/5; 8/9 | 11/17; 5/5; 8/9 | diffusion_validation_rev1.csv |
| f(ω) lower-tail error V3 / V6 (nm) | 0.49 / 5.78 | 0.49 / 5.78 | f_omega_variants.json fits.*.rms_low_tail |
| Allowable recess per pad: probability; worst f(0)=0; worst f(0)>0 | 3.5–9; 0.5–0.9; 2.4–4.2 | 3.5–9; 0.53–0.89; 2.36–4.23 | f_omega_variants.json windows['0.30um'].allowable_recess_clean |

Draft numbers not recomputed here (taken from the draft and earlier verified reports): elastic test ratios 0.61–0.69, sliding 1.7–3.5×, ±20 % on 4 geometries, response surface 0.46 %, height sum 4/4, medians 11–12/17 and IQR 13/17 (f_omega_variants.json heldout), 1.49 ± 0.13 and 2.3σ (beta_check).

Deviations from the draft: '1.80 µm' is described as a training size only; 'all model uncertainties' became 'tested uncertainty set'; 248 °C is written as about 250 °C (5 °C grid); f(ω) split into 4 base + 2 pessimistic variants; the contact-FEM agreement is restricted to the tested bonded, no-diffusion case; Hooge et al. (ECTC 2024) added.
