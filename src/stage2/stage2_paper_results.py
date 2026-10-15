r"""Paper-grade derived results (no ANSYS): (1) mechanism transition vs pad size, (2) allowable-recess specification map for
300 nm, (3) orientation yield-risk floor.  Inputs: existing fits and MC machinery (stage2_window, stage2_orient_diffusion).
Outputs: results/stage2/paper_results.json, figures s2_mechanism_transition.png, s2_recess_spec_0.30um.png, s2_orientation_floor.png
Usage: python src\stage2\stage2_paper_results.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stage2_window as W  # noqa: E402
import stage2_orient_diffusion as O  # noqa: E402

REPO = HERE.parents[1]
OUT = REPO / "results" / "stage2"
FIG = REPO / "results" / "figures"
RECESS_SUM = 5.0   # nm, IRPS 2026: 2.5 nm per pad x 2

# ---- (1) mechanism transition: elastic u per pad (model, array cell, b = 1 and 0.69) at 400 C vs size; h_d amplitude (saturated)
# model elastic u at 400 C (array cell, Hill; results of the Stage 2 baseline, report §12.1) and measurements
U_EL = {0.30: dict(model=1.22, meas=None, src="S68 (3D [001], prediction)"),
        0.54: dict(model=2.04, meas=1.40, src="S112 / DM2023 Fig 1"),
        1.26: dict(model=4.04, meas=5.00, src="validation_rev1 / DM2023"),
        1.80: dict(model=4.99, meas=5.40, src="calibration / DM2023"),
        3.06: dict(model=6.32, meas=7.85, src="calibration / DM2023")}


def main():
    orient = json.loads((OUT / "orient_diffusion_round2.json").read_text())
    th, oc, dw = orient["fit"]["theta_eff"], orient["fit"]["omega_c"], orient["fit"]["d_omega"]
    rng = np.random.default_rng(0)
    om = O.omega_random(400_000, rng); fbar = float(np.mean(O.f_of(om, oc, dw)))
    sizes = np.array(sorted(U_EL))
    u_model = np.array([U_EL[s]["model"] for s in sizes]); u_meas = np.array([U_EL[s]["meas"] if U_EL[s]["meas"] else np.nan for s in sizes])
    # size at which 2*u_el (pair) equals the recess sum: interpolate in log(size)
    def crossing(u):
        x = np.log(sizes[np.isfinite(u)]); y = 2 * u[np.isfinite(u)] - RECESS_SUM
        for i in range(len(x) - 1):
            if y[i] < 0 <= y[i + 1]:
                return float(np.exp(x[i] + (x[i + 1] - x[i]) * (-y[i]) / (y[i + 1] - y[i])))
        return float("nan")
    D_el_model = crossing(u_model); D_el_model_b = crossing(0.69 * u_model); D_el_meas = crossing(u_meas)
    # diffusion amplitude per pad at saturation (>= 350 C, 1 h): 0.0022 (theta-90) D fbar; verified range D <= 300 nm
    Dgrid = np.array([0.115, 0.14, 0.25, 0.30, 0.54, 1.0, 1.26, 1.80, 3.06])
    h_sat = 0.0022 * (th - 90) * Dgrid * 1000 * fbar
    mech = dict(recess_sum_nm=RECESS_SUM, size_where_elastic_pair_closes_model_um=D_el_model, size_model_b069_um=D_el_model_b,
                size_measured_um=D_el_meas, fbar=fbar, h_sat_per_pad_nm={f"{d:g}": float(h) for d, h in zip(Dgrid, h_sat)},
                note="h_d scaling with D is measurement-checked only for D <= 300 nm (DM2026); larger sizes are extrapolation")
    # ---- (2) allowable recess specification map, 300 nm clean, main setting: max recess sum with P >= 0.99
    coef = np.array(json.loads((OUT / "predict_0.30um_fit.json").read_text())["fit"]["coef"])
    spec = {}
    for surf, s_ox in W.SURF.items():
        spec[surf] = {}
        for T in W.TS:
            for t in W.TMIN:
                best = 0.0
                for mean in np.arange(0.5, 15.01, 0.25):       # per pad mean; sigma fixed 0.5 nm
                    pr = W.Pairs(60_000, 0, coef, oc, dw, recess=(mean, 0.5))
                    if pr.P(300.0, T, t, 0.69, s_ox, 1.0, th, 60.0, 20.7) >= 0.99:
                        best = float(2 * mean)
                    else:
                        break
                spec[surf][f"{T}C_{t}min"] = best
    # ---- (3) orientation yield-risk floor at 300 nm: P(no contact) at each cell with facet model vs f = 1 (fg-Cu-like)
    pr_f = W.Pairs(400_000, 0, coef, oc, dw); pr_1 = W.Pairs(400_000, 0, coef, oc, dw, facet=False)
    floor = {}
    for T in W.TS:
        for t in W.TMIN:
            p_f = pr_f.P(300.0, T, t, 0.69, 1.0, 1.0, th, 60.0, 20.7); p_1 = pr_1.P(300.0, T, t, 0.69, 1.0, 1.0, th, 60.0, 20.7)
            floor[f"{T}C_{t}min"] = dict(P_open_facet=1 - p_f, P_open_no_facet=1 - p_1)
    frac_low = float(np.mean(O.f_of(om, oc, dw) < 0.5))
    res = dict(mechanism_transition=mech, recess_spec_sum_nm_300nm=spec, orientation_floor_300nm=floor,
               fraction_pads_f_below_0p5=frac_low, settings=dict(theta_eff=th, omega_c=oc, d_omega=dw, b=0.69, tau0=60, Q=20.7))
    json.dump(res, open(OUT / "paper_results.json", "w"), indent=1, default=float)
    print("mechanism:", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in mech.items() if k != "h_sat_per_pad_nm"})
    print("h_sat per pad:", {k: round(v, 1) for k, v in mech["h_sat_per_pad_nm"].items()})
    for surf in spec:
        print(surf, "allowable recess sum (nm):", spec[surf])
    print("orientation floor (P_open facet / no facet):", {k: (round(v["P_open_facet"], 4), round(v["P_open_no_facet"], 4)) for k, v in floor.items() if v["P_open_facet"] < 0.5})
    print("fraction of pads with f < 0.5:", round(frac_low, 3))
    # ---- figures
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    ax.plot(sizes, 2 * u_model, "o-", color="#1f77b4", ms=4, label="elastic pair, model (b = 1)")
    ax.plot(sizes, 2 * 0.69 * u_model, "o--", color="#1f77b4", ms=3, mfc="none", label="elastic pair, model × 0.69")
    ax.plot(sizes, 2 * u_meas, "ks", ms=4, label="elastic pair, measured (imec)")
    ax.plot(Dgrid[Dgrid <= 0.3], 2 * h_sat[Dgrid <= 0.3], "^-", color="#d62728", ms=4, label="diffusion pair, ≥350 °C sat. (checked)")
    ax.plot(Dgrid[Dgrid >= 0.3], 2 * h_sat[Dgrid >= 0.3], "^:", color="#d62728", ms=3, mfc="none", label="diffusion pair (extrapolated)")
    ax.axhline(RECESS_SUM, color="gray", lw=1); ax.text(0.12, RECESS_SUM + 0.3, "recess sum 5 nm (IRPS 2026)", fontsize=6.5, color="gray")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("pad width (µm)"); ax.set_ylabel("top + bottom protrusion at 400 °C (nm)")
    ax.set_xticks([0.1, 0.3, 0.54, 1, 3]); ax.set_xticklabels(["0.1", "0.3", "0.54", "1", "3"]); ax.minorticks_off()
    ax.legend(fontsize=5.5, frameon=False, loc="lower right"); ax.set_title("mechanism transition: elastic closes the recess only above ≈ %.1f µm" % D_el_meas, fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "s2_mechanism_transition.png", dpi=300); plt.close(fig)
    fig, axs = plt.subplots(1, 2, figsize=(7, 2.9), sharey=True)
    for ax, surf, title in zip(axs, ("clean", "oxidised"), ("clean surface (main)", "surface oxide not controlled")):
        M = np.array([[spec[surf][f"{T}C_{t}min"] for T in W.TS] for t in W.TMIN])
        im = ax.imshow(M, origin="lower", vmin=0, vmax=30, cmap="Greens", aspect="auto", extent=[-0.5, 4.5, -0.5, 2.5])
        for i, t in enumerate(W.TMIN):
            for j, T in enumerate(W.TS):
                ax.text(j, i, f"{M[i, j]:.0f}" if M[i, j] > 0 else "–", ha="center", va="center", fontsize=7, color="w" if M[i, j] > 15 else "k")
        ax.set_xticks(range(5)); ax.set_xticklabels([str(T) for T in W.TS]); ax.set_yticks(range(3)); ax.set_yticklabels([str(t) for t in W.TMIN])
        ax.set_title(title, fontsize=8); ax.set_xlabel("anneal T (°C)")
    axs[0].set_ylabel("anneal time (min)")
    cb = fig.colorbar(im, ax=axs, shrink=0.9); cb.set_label("allowable recess sum for P(contact) ≥ 0.99 (nm)")
    fig.suptitle("300 nm pads: CMP recess specification returned by the model (σ 0.5 nm/pad; – = no contact even at 1 nm)", fontsize=7.5)
    fig.savefig(FIG / "s2_recess_spec_0.30um.png", dpi=300, bbox_inches="tight"); plt.close(fig)
    fig, ax = plt.subplots(figsize=(4.2, 2.8))
    cells = [f"{T}C_{t}min" for t in (30, 120) for T in W.TS]
    x = np.arange(len(cells))
    ax.bar(x - 0.18, [max(floor[c]["P_open_facet"], 1e-5) for c in cells], 0.36, label="large-grain Cu (<111> facet term)")
    ax.bar(x + 0.18, [max(floor[c]["P_open_no_facet"], 1e-5) for c in cells], 0.36, label="no facet tail (fine-grained Cu proxy)")
    ax.set_yscale("log"); ax.set_ylabel("P(pair not in contact)"); ax.set_xticks(x); ax.set_xticklabels([c.replace("C_", " °C\n") for c in cells], fontsize=6)
    ax.axhline(0.01, color="gray", lw=0.8, ls="--"); ax.legend(fontsize=6, frameon=False); ax.set_title("300 nm: orientation sets the open-pair floor", fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "s2_orientation_floor.png", dpi=300); plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
