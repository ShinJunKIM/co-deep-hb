r"""Factor ranking for the 300 nm window (v4.3): how many of the 15 anneal recipes (T 200-400 C x t 5/30/120 min) change their
verdict (P_contact >= 0.99) when one factor is changed.  Elastic term = hkl surrogate (bonded) from the orientation study;
diffusion = consistent f(omega) variants of f_omega_variants.json (main setting: V3 ramp + scatter, b 0.69, tau0 60 s,
Q 20.7, Ta liner, clean surface, recess N(2.5, 0.5^2) per pad).  Uniform orientation is an assumption; MC counts are not data.
Output: results/stage2/v2/factor_ranking.json, results/figures/s2_factor_ranking_v4.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / "src" / "stage2"))
import f_omega_variants as F  # noqa: E402

OUT = F.OUT
REPO = HERE.parents[1]
TS = (200, 250, 300, 350, 400); TM = (5, 30, 120)


def main():
    base = json.loads((OUT / "f_omega_variants.json").read_text())
    fits = {k: v for k, v in base["fits"].items() if k in base["variants_used_for_windows"]}
    rng = np.random.default_rng(0); n = 80_000
    v1, v2 = F.directions(n, rng), F.directions(n, rng)
    om1, om2 = F.omega_of(v1), F.omega_of(v2)
    z1, z2 = rng.normal(size=n), rng.normal(size=n)
    e1, e2 = rng.normal(size=n), rng.normal(size=n)
    kb = F.hkl_k_fn("bonded"); ks = F.hkl_k_fn("sliding")
    K = dict(bonded=(kb(v1), kb(v2)), sliding=(ks(v1), ks(v2)))

    def window(variant="V3 ramp + scatter", b=0.69, tau0=60.0, Q=20.7, s_ox=1.0, liner=1.0, rm=2.5, rs=0.5, diffusion=True,
               facet=True, side="bonded"):
        fit = fits[variant]; fam = F.VARIANTS[variant][0]
        g = (rm + rs * e1) + (rm + rs * e2)
        k1, k2 = K[side]
        cells = set()
        for T in TS:
            for t in TM:
                if diffusion:
                    if facet:
                        h1 = F.h_samples(om1, z1, fam, fit["params"], fit["theta"], fit["scatter"], 300.0, T, t * 60, s_ox, tau0, Q)
                        h2 = F.h_samples(om2, z2, fam, fit["params"], fit["theta"], fit["scatter"], 300.0, T, t * 60, s_ox, tau0, Q)
                    else:   # no orientation tail: f = 1 for every pad (fine-grained Cu proxy), same amplitude and scatter
                        h1 = F.h_samples(np.full(n, 54.7), z1, fam, fit["params"], fit["theta"], fit["scatter"], 300.0, T, t * 60, s_ox, tau0, Q)
                        h2 = F.h_samples(np.full(n, 54.7), z2, fam, fit["params"], fit["theta"], fit["scatter"], 300.0, T, t * 60, s_ox, tau0, Q)
                    h = liner * (h1 + h2)
                else:
                    h = 0.0
                if np.mean(b * (k1 + k2) * (T - 25.0) + h >= g) >= 0.99:
                    cells.add((T, t))
        return cells

    def ranking(mv):
        w = lambda **kw: window(variant=mv, **kw)
        m = w()
        return m, {
            "mechanism: surface diffusion off (elastic only)": len(w(diffusion=False) ^ m),
            "anneal kinetics: tau0 20 vs 100 s": len(w(tau0=20.0) ^ w(tau0=100.0)),
            "anneal kinetics: Q 20.7 vs 13.4 kcal/mol": len(w(Q=13.4) ^ m),
            "surface: clean vs oxidised (s_ox 0.45)": len(w(s_ox=0.45) ^ m),
            "liner wetting: theta 107 vs 149 deg": len(w(liner=(107 - 90) / 33.0) ^ w(liner=(149 - 90) / 33.0)),
            "interface: bonded vs sliding sidewall (height-sum basis)": len(w(side="sliding") ^ m),
            "random: recess spread sigma 0.5 vs 1.0 nm/pad": len(w(rs=1.0) ^ m),
            "random: recess mean 2.5 vs 3.5 nm/pad": len(w(rm=3.5) ^ m),
            "random: orientation tail present vs absent (f = 1)": len(w(facet=False) ^ m),
            "elastic factor b: 0.60 vs 1.0": len(w(b=0.60) ^ w(b=1.0)),
        }
    per = {v: ranking(v) for v in fits}
    main_c = per["V3 ramp + scatter"][0]
    var_cells = [per[v][0] for v in fits]
    keys = list(next(iter(per.values()))[1])
    factors = {k: per["V3 ramp + scatter"][1][k] for k in keys}
    factor_range = {k: [min(per[v][1][k] for v in fits), max(per[v][1][k] for v in fits)] for k in keys}
    factors["orientation-tail shape: spread over 6 consistent f(omega)"] = len(set.union(*var_cells) - set.intersection(*var_cells))
    factor_range["orientation-tail shape: spread over 6 consistent f(omega)"] = [factors["orientation-tail shape: spread over 6 consistent f(omega)"]] * 2
    res = dict(main_window=sorted(main_c), n_main=len(main_c), factors=factors, factor_range_over_variants=factor_range,
               note="cells = anneal recipes (5 T x 3 t = 15) whose verdict P>=0.99 flips; interface row uses the height-sum criterion, which "
                    "agrees with contact FEM only for bonded sidewalls (E71-E74: sliding gives rim contact only)")
    json.dump(res, open(OUT / "factor_ranking.json", "w"), indent=1, default=float)
    for k, v in sorted(factors.items(), key=lambda kv: -kv[1]):
        print(f"{v:2d}  (range over f variants {factor_range[k][0]}-{factor_range[k][1]})  {k}")
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    items = sorted(factors.items(), key=lambda kv: kv[1])
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    cols = ["#d62728" if k.startswith("random") or k.startswith("orientation") else "#1f77b4" for k, _ in items]
    ax.barh(range(len(items)), [v for _, v in items], color=cols)
    for i, (k, v) in enumerate(items):
        lo, hi = factor_range[k]
        if hi > lo:
            ax.plot([lo, hi], [i, i], "k-", lw=1.2)
    ax.set_yticks(range(len(items))); ax.set_yticklabels([k for k, _ in items], fontsize=6.3)
    ax.set_xlabel("anneal recipes whose verdict flips (of 15), 300 nm, clean surface")
    ax.set_title("blue: process variables / model; red: per-pad random factors", fontsize=7)
    fig.tight_layout(); fig.savefig(REPO / "results" / "figures" / "s2_factor_ranking_v4.png", dpi=300); plt.close(fig)


if __name__ == "__main__":
    main()
