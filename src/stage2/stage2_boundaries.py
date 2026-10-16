r"""Two boundaries versus pad width (model prediction, not a measured transition):
  (1) elastic contact limit:     u_t + u_b = R            (R = recess sum, 5 nm IRPS 2026; also 3 / 8 nm)
  (2) contribution crossover:    h_t + h_b = u_t + u_b    (surface diffusion equals thermo-elastic protrusion)
Elastic u(w, T): imec stack (SiCN 120 GPa, 2.0 ppm/K, h 0.6 um, array cell), from the pre-registered surrogate
C = c0 / [1 + a (E_d/E_Cu) (h/w)^1.5] (c0 1.95, a 2.2; X35-X38 within 20 %) and, for comparison, the imec measurement
(0.54-3.06 um, 400 C) and the FEM points.  Diffusion h_d(D, T, t): two forms that both describe DM2026 (D <= 300 nm)
but extrapolate differently: A = revision 1 (theta_eff 113.6, tau0 60 s, Q 20.7, tau ~ D^3.7, exponential);
B = master-curve fit (a 0.0546, tau0 0.16 h, Q 13.4, n 0.19).  Above D = 300 nm both are extrapolations.
Output: results/stage2/boundaries.json, results/figures/s2_boundaries.png
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "results" / "stage2"; FIG = REPO / "results" / "figures"
R_GAS = 1.987e-3
DALPHA = 16.5e-6 - 2.6e-6
H = 0.6
ED_ECU = 120.0 / 128.3
MEAS = {0.54: 1.40, 1.26: 5.00, 1.80: 5.40, 3.06: 7.85}      # imec in-situ, 400 C, per pad
FEM = {0.30: 1.22, 0.54: 2.04, 1.26: 4.04, 1.80: 4.99, 3.06: 6.32}


def u_el(w, T, c0=1.95, a=2.2):
    C = c0 / (1 + a * ED_ECU * (H / w) ** 1.5)
    return C * DALPHA * (T - 25.0) * H * 1000.0


def h_A(D_um, T, t_h):
    D = D_um * 1000.0
    tau = 60.0 * (D / 200.0) ** 3.7 * math.exp(20.7 / R_GAS * (1 / (T + 273.15) - 1 / 623.15))
    return 0.0022 * (113.6 - 90.0) * D * (1 - math.exp(-t_h * 3600.0 / tau))


def h_B(D_um, T, t_h):
    D = D_um * 1000.0
    tau = 0.16 * 3600.0 * (200.0 / D) ** -0.19 * math.exp(13.4 / R_GAS * (1 / (T + 273.15) - 1 / 623.15))
    return 0.0546 * D * (1 - math.exp(-t_h * 3600.0 / tau))


def crossing(f, lo=0.1, hi=10.0):
    ws = np.logspace(math.log10(lo), math.log10(hi), 2000); v = np.array([f(w) for w in ws])
    idx = np.where(np.sign(v[:-1]) != np.sign(v[1:]))[0]
    return [float(ws[i]) for i in idx]


def main():
    res = dict(note="model predictions; measured elastic points only at 0.54-3.06 um; diffusion data only D <= 300 nm (equal pads)")
    lim = {}
    for R in (3.0, 5.0, 8.0):
        for T in (250, 300, 350, 400):
            lim[f"R{R:g}_T{T}"] = crossing(lambda w: 2 * u_el(w, T) - R)
    # measured-based elastic limit at 400 C (log interpolation between measured sizes)
    ws = np.array(sorted(MEAS)); us = np.array([MEAS[w] for w in ws])
    meas_lim = {}
    for R in (3.0, 5.0, 8.0):
        y = 2 * us - R; i = np.where((y[:-1] < 0) & (y[1:] >= 0))[0]
        meas_lim[f"R{R:g}"] = float(np.exp(np.log(ws[i[0]]) + (np.log(ws[i[0] + 1]) - np.log(ws[i[0]])) * (-y[i[0]]) / (y[i[0] + 1] - y[i[0]]))) if len(i) else None
    res["elastic_limit_surrogate_um"] = lim; res["elastic_limit_measured_400C_um"] = meas_lim
    cross = {}
    for T, t in ((250, 2.0), (300, 0.5), (350, 1.0), (400, 2.0)):
        cross[f"{T}C_{t:g}h"] = dict(A_rev1=crossing(lambda w: h_A(w, T, t) - u_el(w, T)), B_master=crossing(lambda w: h_B(w, T, t) - u_el(w, T)))
    res["crossover_um"] = cross
    sizes = [0.115, 0.14, 0.25, 0.30, 0.54, 1.0, 1.26, 1.8, 3.06, 5.0]
    res["table_350C_1h"] = {f"{w:g}": dict(u_pair=2 * u_el(w, 350), hA_pair=2 * h_A(w, 350, 1), hB_pair=2 * h_B(w, 350, 1)) for w in sizes}
    json.dump(res, open(OUT / "boundaries.json", "w"), indent=1, default=float)
    print("elastic limit (surrogate):", {k: [round(v, 2) for v in vs] for k, vs in lim.items()})
    print("elastic limit (imec measured, 400 C):", {k: (round(v, 2) if v else v) for k, v in meas_lim.items()})
    print("crossover:", {k: {m: [round(v, 2) for v in vs] for m, vs in d.items()} for k, d in cross.items()})
    for w, d in res["table_350C_1h"].items():
        print(f"  w {w:>5} um: 2u {d['u_pair']:.2f}  2h_A {d['hA_pair']:.2f}  2h_B {d['hB_pair']:.2f} nm")
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    w = np.logspace(-1, math.log10(5), 300)
    fig, ax = plt.subplots(figsize=(4.4, 3.1))
    ax.plot(w, [2 * u_el(x, 400) for x in w], "-", color="#1f77b4", label="elastic pair, 400 °C (surrogate C(h/w))")
    ax.plot(list(MEAS), [2 * v for v in MEAS.values()], "ks", ms=4, label="elastic pair, imec measured 400 °C")
    for T, t, ls in ((350, 1.0, "-"), (250, 2.0, "--")):
        ax.plot(w, [2 * h_A(x, T, t) for x in w], ls, color="#d62728", lw=1.2, label=f"diffusion pair A (rev. 1), {T} °C {t:g} h")
        ax.plot(w, [2 * h_B(x, T, t) for x in w], ls, color="#ff7f0e", lw=1.2, label=f"diffusion pair B (master curve), {T} °C {t:g} h")
    ax.axhline(5, color="gray", lw=1); ax.text(0.11, 5.4, "recess sum 5 nm", fontsize=6, color="gray")
    ax.axvspan(0.3, 5, color="0.92", zorder=0); ax.text(0.33, 0.25, "diffusion: extrapolated (no data > 300 nm)", fontsize=5.5, color="0.4")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(0.2, 500); ax.set_xlabel("pad width (µm)"); ax.set_ylabel("top + bottom (nm)")
    ax.legend(fontsize=5, frameon=False, loc="upper left"); fig.tight_layout(); fig.savefig(FIG / "s2_boundaries.png", dpi=300); plt.close(fig)


if __name__ == "__main__":
    main()
