r"""Yield bridge (exploratory): per-pair open probability p_open from the Stage 2 Monte Carlo -> daisy-chain yield Y(N) = (1-p)^N,
compared with literature chain yields, inverted to the implied p_open, plus a minimal overlay model.
No ANSYS. Reuses stage2_window (Pairs, kinetics) and stage2_orient_diffusion (f(omega)).
Usage: python src\agents\yield_bridge.py
Outputs: results/stage2/agents/yield_bridge.json, results/figures/agents/yield_vs_chain_length.png
"""
from __future__ import annotations

import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "stage2"))
import stage2_window as W  # noqa: E402

REPO = HERE.parents[1]
OUT = REPO / "results" / "stage2" / "agents"; OUT.mkdir(parents=True, exist_ok=True)
FIG = REPO / "results" / "figures" / "agents"; FIG.mkdir(parents=True, exist_ok=True)

CELLS = [(250, 120), (300, 30), (350, 30), (400, 30)]
N_GRID = np.logspace(0, 6, 61)

# literature chain yields (local papers; see docs/agents/yield_bridge.md for citations)
LIT = [
    dict(src="imec IEDM 2017 (Scalable sub-2um), 360/720 nm pads, 1.08/1.44 um pitch, 25 % Cu density, anneal 250 then 350 C",
         N=70000, Y=0.45, pad_nm=360, note="longest serial links ~70,000: ~45 % yield; loss varies centre-to-edge (CMP blamed)"),
    dict(src="imec ECTC (Novel Cu/SiCN topography), 270/540 nm pads, 1.08 um pitch, 70,866 links", N=70866, Y=0.925, pad_nm=270,
         note="'90-95 % yield from 5 um to 1 um pitch'; 34,200 chains; x10-resistance outliers excluded"),
    dict(src="imec IEDM 2017, 180/540 nm pads, 0.72 um pitch", N=1, Y=0.50, pad_nm=180,
         note="'50 % yield of contacts' with overlay tolerance 180 nm below the 250 nm overlay accuracy (overlay blamed)"),
]


def p_open_table(n=400_000, seed=0):
    orient = json.loads((REPO / "results/stage2/orient_diffusion_round2.json").read_text())
    th, oc, dw = orient["fit"]["theta_eff"], orient["fit"]["omega_c"], orient["fit"]["d_omega"]
    coef = np.array(json.loads((REPO / "results/stage2/predict_0.30um_fit.json").read_text())["fit"]["coef"])
    pr_f = W.Pairs(n, seed, coef, oc, dw); pr_1 = W.Pairs(n, seed, coef, oc, dw, facet=False)
    rows = []
    for surf, s_ox in W.SURF.items():
        for T, t in CELLS:
            p_main = 1 - pr_f.P(300.0, T, t, 0.69, s_ox, 1.0, th, 60.0, 20.7)
            p_nof = 1 - pr_1.P(300.0, T, t, 0.69, s_ox, 1.0, th, 60.0, 20.7)
            band = [1 - pr_f.P(300.0, T, t, b, s_ox, 1.0, th, tau0, Q) for b, tau0, Q in itertools.product(W.B_GRID, W.TAU0_GRID, W.Q_GRID)]
            rows.append(dict(surface=surf, T_C=T, t_min=t, p_open_facet=p_main, p_open_nofacet=p_nof, p_open_band=(min(band), max(band))))
    return rows


def rayleigh_sigma_from_max(M, frac):
    """overlay vector |delta| ~ Rayleigh(sigma); P(|delta| < M) = frac -> sigma."""
    return M / math.sqrt(-2 * math.log(1 - frac))


def overlay_open(D_nm, sigma, crit):
    """P(pair open by overlay) = P(|delta| > crit*D) for Rayleigh overlay."""
    return math.exp(-(crit * D_nm) ** 2 / (2 * sigma ** 2))


def main():
    rows = p_open_table()
    res = dict(status="exploratory (orientation term round 2, not validated); independence of links assumed; no overlay/corrosion in p_open",
               p_open=rows)
    # literature inversion
    inv = []
    for L in LIT:
        p = 1 - L["Y"] ** (1.0 / L["N"]) if L["N"] > 1 else 1 - L["Y"]
        inv.append(dict(L, p_open_implied=p))
    res["literature_inversion"] = inv
    # chain-length ceiling: N at which Y = 0.5 for the facet floor
    for r in rows:
        r["N_half_yield_facet"] = (math.log(0.5) / math.log(1 - r["p_open_facet"])) if r["p_open_facet"] > 0 else float("inf")
        r["N_half_yield_nofacet"] = (math.log(0.5) / math.log(1 - r["p_open_nofacet"])) if r["p_open_nofacet"] > 0 else float("inf")
    # overlay model: equal pads; open if |delta| > crit * D (crit 1.0 = no overlap at all; 0.5 = overlap area < ~40 %)
    ov = []
    for label, M, frac in (("2017 bonder (250 nm overlay accuracy)", 250.0, 0.995), ("ECTC 2025 300 nm pitch (<25 nm for 95 % dies)", 25.0, 0.95),
                           ("ECTC 2026 200 nm pitch (<40 nm for 100 % dies)", 40.0, 0.995)):
        sig = rayleigh_sigma_from_max(M, frac)
        for D in (115.0, 180.0, 300.0):
            ov.append(dict(overlay=label, sigma_nm=sig, D_nm=D, p_open_crit1=overlay_open(D, sig, 1.0), p_open_crit0p5=overlay_open(D, sig, 0.5),
                           mean_overlap_delta_over_D=float(np.mean(np.random.default_rng(0).rayleigh(sig, 200000)) / D)))
    res["overlay_model"] = ov
    json.dump(res, open(OUT / "yield_bridge.json", "w"), indent=1, default=float)
    for r in rows:
        print(f"{r['surface']:8s} {r['T_C']}C/{r['t_min']}min  p_open facet {r['p_open_facet']:.2e} (band {r['p_open_band'][0]:.1e}-{r['p_open_band'][1]:.1e}) "
              f"no-facet {r['p_open_nofacet']:.1e}  N(Y=0.5) facet {r['N_half_yield_facet']:.0f} / no-facet {r['N_half_yield_nofacet']:.0f}")
    for L in inv:
        print(f"lit: N {L['N']:6d} Y {L['Y']:.2f} -> p_open {L['p_open_implied']:.2e}  [{L['src'][:60]}]")
    for o in ov:
        print(f"overlay {o['overlay'][:28]:28s} sigma {o['sigma_nm']:5.1f} nm D {o['D_nm']:.0f}: P(open, no overlap) {o['p_open_crit1']:.1e}, P(|d|>D/2) {o['p_open_crit0p5']:.1e}, <d>/D {o['mean_overlap_delta_over_D']:.2f}")
    # figure
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    for r in rows:
        if r["surface"] != "clean": continue
        p = r["p_open_facet"]; lab = f"{r['T_C']} °C / {r['t_min']} min, facet term (p={p:.1e})"
        ax.plot(N_GRID, (1 - p) ** N_GRID, "-", lw=1.2, label=lab)
    ax.plot(N_GRID, np.ones_like(N_GRID), "k--", lw=1, label="no <111> tail (fg-Cu proxy): p = 0")
    # band for 300 C 30 min
    r = next(r for r in rows if r["surface"] == "clean" and r["T_C"] == 300)
    ax.fill_between(N_GRID, (1 - r["p_open_band"][1]) ** N_GRID, (1 - max(r["p_open_band"][0], 1e-9)) ** N_GRID, color="gray", alpha=0.2, label="300 °C/30 min uncertainty band")
    for L in inv:
        if L["N"] > 1: ax.plot([L["N"]], [L["Y"]], "ks", ms=5); ax.annotate(L["src"][:22], (L["N"], L["Y"]), fontsize=5.5, xytext=(-90, 6), textcoords="offset points")
    ax.set_xscale("log"); ax.set_xlabel("daisy-chain length N (links)"); ax.set_ylabel("chain yield Y = (1 − p_open)^N")
    ax.set_ylim(0, 1.05); ax.legend(fontsize=5.5, frameon=False, loc="lower left")
    ax.set_title("300 nm pads, clean surface: orientation-set open-pair floor → chain-length ceiling (exploratory)", fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "yield_vs_chain_length.png", dpi=300); plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
