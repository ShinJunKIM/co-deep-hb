r"""Fine-grid process window for 300 nm pads (v4.4): minimum anneal time vs temperature for P_contact >= 0.99, with the
uncertainty band over all model combinations, the worst-orientation boundary, and factor effects expressed as a shift of
the boundary temperature (deg C) at fixed time.

Grid: T 200-400 C in 5 C steps (41) x t 1 min - 4 h, 40 log-spaced points (interpolated in log t for the boundary).
Elastic term: hkl orientation surrogate (bonded, 154-run study).  Diffusion: the 6 f(omega) variants consistent with the
readable DM2026 quantiles (f_omega_variants.json).  Uncertainty set: 6 variants x b {0.60, 0.69, 0.93, 1.0} x tau0 {20, 60,
100 s} x Q {20.7, 13.4}.  Main setting: V3 ramp + scatter, b 0.69, tau0 60 s, Q 20.7, Ta liner, clean surface, recess
N(2.5, 0.5^2) per pad.  A finer grid gives a more precise boundary, not more validation data: diffusion is checked against
data at 250-450 C (equal pads); below 250 C the model under-predicts (conservative).  Uniform orientation is an assumption;
MC sample counts are numerical resolution, not data.
Output: results/stage2/v2/boundary_curves.json, results/figures/s2_boundary_curves_300nm.png, s2_factor_shift_300nm.png
"""
from __future__ import annotations

import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(REPO / "src" / "stage2"))
import f_omega_variants as F  # noqa: E402

OUT = F.OUT
FIG = REPO / "results" / "figures"
TG = np.arange(100.0, 400.1, 5.0)    # computed from 100 C only so that boundaries just below 200 C are not clamped at the grid edge
                                     # (v4.4 had 200 C: the 2 h shifts of tau0 and Q were clamped). Below 250 C = outside data; no recipe claim.
TMIN = np.logspace(0, math.log10(240.0), 40)             # minutes
D = 300.0
P_WIN = 0.99
MAIN = dict(variant="V3 ramp + scatter", b=0.69, tau0=60.0, Q=20.7, s_ox=1.0, liner=1.0, rm=2.5, rs=0.5, side="bonded", facet=True)


def kin_grid(tau0, Q):
    """kin[T_i, t_j] for D = 300 nm."""
    tau = tau0 * (D / 200.0) ** 3.7 * np.exp(Q / F.R_GAS * (1 / (TG[:, None] + 273.15) - 1 / 623.15))
    return 1.0 - np.exp(-(TMIN[None, :] * 60.0) / tau)


def main():
    base = json.loads((OUT / "f_omega_variants.json").read_text())
    fits = {k: v for k, v in base["fits"].items() if k in base["variants_used_for_windows"]}
    rng = np.random.default_rng(0); n = 50_000
    v1, v2 = F.directions(n, rng), F.directions(n, rng)
    om1, om2 = F.omega_of(v1), F.omega_of(v2)
    z1, z2 = rng.normal(size=n), rng.normal(size=n)
    e1, e2 = rng.normal(size=n), rng.normal(size=n)
    kfn = {"bonded": F.hkl_k_fn("bonded"), "sliding": F.hkl_k_fn("sliding")}
    K = {s: kfn[s](v1) + kfn[s](v2) for s in kfn}
    # per-pad bulge-out amplitude at kin = 1 (orientation and scatter dependent), per variant; facet=False -> f = 1
    AMP = {}
    for name, fit in fits.items():
        fam = F.VARIANTS[name][0]
        for facet in (True, False):
            o1 = om1 if facet else np.full(n, 54.74); o2 = om2 if facet else np.full(n, 54.74)
            a1 = F.h_samples(o1, z1, fam, fit["params"], fit["theta"], fit["scatter"], D, 350.0, 1e12)
            a2 = F.h_samples(o2, z2, fam, fit["params"], fit["theta"], fit["scatter"], D, 350.0, 1e12)
            AMP[(name, facet)] = a1 + a2                # pair amplitude at kin -> 1, aligned with the same pads' elastic K
    KIN = {(tau0, Q): kin_grid(tau0, Q) for tau0, Q in itertools.product(F.TAU0_GRID, F.Q_GRID)}

    def P_grid(variant, b, tau0, Q, s_ox=1.0, liner=1.0, rm=2.5, rs=0.5, side="bonded", facet=True, diffusion=True):
        """P[T_i, t_j] = mean over pairs of [b K (T-25) + s_ox liner A kin >= R]; computed on the joint samples."""
        A = AMP[(variant, facet)] if diffusion else np.zeros(n)
        R = (rm + rs * e1) + (rm + rs * e2)
        Ksd = K[side]
        kin = KIN.get((tau0, Q)); kin = kin if kin is not None else kin_grid(tau0, Q)
        P = np.empty((len(TG), len(TMIN)))
        Ap = A
        for i, T in enumerate(TG):
            el = b * Ksd * (T - 25.0) - R                  # (n,)
            for j in range(len(TMIN)):
                P[i, j] = np.mean(el + s_ox * liner * Ap * kin[i, j] >= 0.0)
        return P

    def t_boundary(P):
        """minimum time (min) for P >= 0.99 at each T (log interpolation); inf if never within 4 h."""
        out = np.full(len(TG), np.inf)
        for i in range(len(TG)):
            ok = np.where(P[i] >= P_WIN)[0]
            if len(ok) == 0:
                continue
            j = ok[0]
            if j == 0:
                out[i] = TMIN[0]; continue
            p0, p1 = P[i, j - 1], P[i, j]
            f = (P_WIN - p0) / (p1 - p0) if p1 > p0 else 1.0
            out[i] = 10 ** (math.log10(TMIN[j - 1]) + f * (math.log10(TMIN[j]) - math.log10(TMIN[j - 1])))
        return out

    def T_at(tb, t_fixed):
        """lowest T whose minimum time <= t_fixed (linear interpolation in T); nan if none."""
        ok = np.where(tb <= t_fixed)[0]
        if len(ok) == 0:
            return float("nan")
        i = ok[0]
        if i == 0:
            return float(TG[0])
        # interpolate in log time between T[i-1] (tb > t) and T[i] (tb <= t)
        a, b_ = tb[i - 1], tb[i]
        if not np.isfinite(a):
            return float(TG[i])
        f = (math.log10(a) - math.log10(t_fixed)) / (math.log10(a) - math.log10(b_))
        return float(TG[i - 1] + f * (TG[i] - TG[i - 1]))

    res = dict(status=__doc__.split("Output:")[0].strip(), T=TG.tolist(), t_min=TMIN.tolist(), surfaces={})
    combos = list(itertools.product(fits, F.B_GRID, F.TAU0_GRID, F.Q_GRID))
    for surf, s_ox in F.SURF.items():
        tbs = {}
        for (v, b, tau0, Q) in combos:
            tbs[(v, b, tau0, Q)] = t_boundary(P_grid(v, b, tau0, Q, s_ox=s_ox))
        allc = np.array(list(tbs.values()))
        main_tb = tbs[(MAIN["variant"], MAIN["b"], MAIN["tau0"], MAIN["Q"])]
        res["surfaces"][surf] = dict(main=main_tb.tolist(), band_min=allc.min(axis=0).tolist(), band_max=allc.max(axis=0).tolist(),
                                     T_at_30min=dict(main=T_at(main_tb, 30), robust=T_at(allc.max(axis=0), 30), optimistic=T_at(allc.min(axis=0), 30)),
                                     T_at_120min=dict(main=T_at(main_tb, 120), robust=T_at(allc.max(axis=0), 120), optimistic=T_at(allc.min(axis=0), 120)),
                                     T_at_5min=dict(main=T_at(main_tb, 5), robust=T_at(allc.max(axis=0), 5), optimistic=T_at(allc.min(axis=0), 5)))
        print(f"{surf}: boundary T (C) at 5/30/120 min  main {res['surfaces'][surf]['T_at_5min']['main']:.0f}/{res['surfaces'][surf]['T_at_30min']['main']:.0f}/"
              f"{res['surfaces'][surf]['T_at_120min']['main']:.0f}; robust (all combos) {res['surfaces'][surf]['T_at_5min']['robust']:.0f}/"
              f"{res['surfaces'][surf]['T_at_30min']['robust']:.0f}/{res['surfaces'][surf]['T_at_120min']['robust']:.0f}; optimistic "
              f"{res['surfaces'][surf]['T_at_5min']['optimistic']:.0f}/{res['surfaces'][surf]['T_at_30min']['optimistic']:.0f}/{res['surfaces'][surf]['T_at_120min']['optimistic']:.0f}")
    # factor effects: shift of the boundary temperature at 30 min and 2 h relative to the main setting (clean)
    m = MAIN
    base_tb = t_boundary(P_grid(m["variant"], m["b"], m["tau0"], m["Q"]))
    def shift(tb_a, tb_b=None):
        tb_b = base_tb if tb_b is None else tb_b
        out = {f"{tf}min": (T_at(tb_a, tf) - T_at(tb_b, tf)) for tf in (30, 120)}
        # same factor as a multiplier of the minimum anneal time at fixed T (worse / better); constant in T for factors that
        # rescale the kinetics, T-dependent for Q (pivot at the 350 C reference)
        for Tq in (220.0, 250.0, 285.0, 320.0):
            i = int(np.argmin(abs(TG - Tq)))
            out[f"time_ratio_{Tq:.0f}C"] = float(tb_a[i] / tb_b[i]) if np.isfinite(tb_a[i]) and np.isfinite(tb_b[i]) else float("inf")
        return out
    var_tb = {v: t_boundary(P_grid(v, m["b"], m["tau0"], m["Q"])) for v in fits}
    fac = {
        "mechanism: surface diffusion off (elastic only)": {f"{tf}min": (float("inf") if math.isnan(T_at(t_boundary(P_grid(m['variant'], m['b'], m['tau0'], m['Q'], diffusion=False)), tf)) else 0.0) for tf in (30, 120)},
        "anneal kinetics: tau0 100 vs 20 s": shift(t_boundary(P_grid(m["variant"], m["b"], 100.0, m["Q"])), t_boundary(P_grid(m["variant"], m["b"], 20.0, m["Q"]))),
        "anneal kinetics: Q 20.7 vs 13.4 kcal/mol": shift(base_tb, t_boundary(P_grid(m["variant"], m["b"], m["tau0"], 13.4))),
        "surface: oxidised (s_ox 0.45) vs clean": shift(t_boundary(P_grid(m["variant"], m["b"], m["tau0"], m["Q"], s_ox=0.45))),
        "liner wetting: theta 107 vs 149 deg": shift(t_boundary(P_grid(m["variant"], m["b"], m["tau0"], m["Q"], liner=(107 - 90) / 33.0)),
                                                     t_boundary(P_grid(m["variant"], m["b"], m["tau0"], m["Q"], liner=(149 - 90) / 33.0))),
        "interface: bonded vs sliding sidewall (height-sum basis)": shift(base_tb, t_boundary(P_grid(m["variant"], m["b"], m["tau0"], m["Q"], side="sliding"))),
        "random: recess spread sigma 1.0 vs 0.5 nm/pad": shift(t_boundary(P_grid(m["variant"], m["b"], m["tau0"], m["Q"], rs=1.0))),
        "random: recess mean 3.5 vs 2.5 nm/pad": shift(t_boundary(P_grid(m["variant"], m["b"], m["tau0"], m["Q"], rm=3.5))),
        "random: orientation tail present vs absent (f = 1)": shift(base_tb, t_boundary(P_grid(m["variant"], m["b"], m["tau0"], m["Q"], facet=False))),
        "orientation-tail shape: spread over 6 f(omega)": {f"{tf}min": (np.nanmax([T_at(v, tf) for v in var_tb.values()]) - np.nanmin([T_at(v, tf) for v in var_tb.values()])) for tf in (30, 120)},
        "elastic factor b: 0.60 vs 1.0": shift(t_boundary(P_grid(m["variant"], 0.60, m["tau0"], m["Q"])), t_boundary(P_grid(m["variant"], 1.0, m["tau0"], m["Q"]))),
    }
    ts = fac["orientation-tail shape: spread over 6 f(omega)"]
    for Tq in (220.0, 250.0, 285.0, 320.0):     # slowest / fastest variant at fixed T
        i = int(np.argmin(abs(TG - Tq))); col = np.array([v[i] for v in var_tb.values()])
        ts[f"time_ratio_{Tq:.0f}C"] = float(col.max() / col.min()) if np.all(np.isfinite(col)) else float("inf")
    # the same factors evaluated for every variant as main -> range of the shift
    res["factor_shift_C"] = fac
    res["base_T_at"] = {f"{tf}min": T_at(base_tb, tf) for tf in (5, 30, 120)}
    for k, v in fac.items():
        print(f"  {k:58s} dT(30 min) {v['30min']:+6.1f} C   dT(2 h) {v['120min']:+6.1f} C")
    # worst-orientation boundary (variants with f(0) > 0 only; f(0) = 0 variants never close the worst pair)
    grid_dirs = F.directions(100_000, np.random.default_rng(7))
    worst = {}
    for name, fit in fits.items():
        fam = F.VARIANTS[name][0]
        f0 = float(fam(np.array([0.0]), fit["params"])[0])
        if f0 <= 1e-9:
            worst[name] = dict(f0=f0, boundary=None); continue
        tb = np.full(len(TG), np.inf)
        for i, T in enumerate(TG):
            for j, tm in enumerate(TMIN):
                mm, _, _ = F.worst_margin(grid_dirs, kfn["bonded"], fam, fit["params"], fit["theta"], fit["scatter"], D, T, tm * 60.0, 1.0,
                                          m["b"], m["tau0"], m["Q"], 5.0 + 2.326 * math.sqrt(2) * 0.5)
                if mm >= 0:
                    tb[i] = tm; break
        worst[name] = dict(f0=f0, boundary=tb.tolist(), T_at_30min=T_at(tb, 30), T_at_120min=T_at(tb, 120))
        print(f"  worst-orientation boundary {name}: f(0) {f0:.2f}, T at 30 min {worst[name]['T_at_30min']:.0f} C, at 2 h {worst[name]['T_at_120min']:.0f} C")
    res["worst_orientation"] = worst
    json.dump(res, open(OUT / "boundary_curves.json", "w"), indent=1, default=lambda x: None if (isinstance(x, float) and not math.isfinite(x)) else float(x))
    # figures
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; import matplotlib.ticker
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.1), sharey=True)
    for ax, surf, title in zip(axs, ("clean", "oxidised"), ("clean surface", "surface oxide not controlled (s_ox 0.45)")):
        s = res["surfaces"][surf]
        lo = np.array(s["band_min"]); hi = np.array(s["band_max"]); mn = np.array(s["main"])
        ax.fill_betweenx(TMIN, 0, 0, alpha=0)
        ax.fill_between(TG, np.where(np.isfinite(lo), lo, 300), np.where(np.isfinite(hi), hi, 300), color="#9ecae1", alpha=0.6,
                        label="uncertainty band (6 f(ω) × b × τ₀ × Q)")
        ax.plot(TG, np.where(np.isfinite(mn), mn, np.nan), "k-", lw=1.4, label="main setting")
        if surf == "clean":
            for name, w in worst.items():
                if w["boundary"] is not None:
                    tb = np.array(w["boundary"], float)
                    ax.plot(TG, np.where(np.isfinite(tb), tb, np.nan), "--", lw=1.0, label=f"worst orientation, {name.split(' ')[0]} (f(0) {w['f0']:.2f})")
        ax.axvspan(200, 250, color="0.92", zorder=0); ax.text(202, 1.3, "below data (conservative)", fontsize=5.5, color="0.4")
        ax.set_yscale("log"); ax.set_ylim(1, 240); ax.set_xlim(200, 400); ax.set_xlabel("anneal T (°C)"); ax.set_title(title, fontsize=8)
        ax.legend(fontsize=5.2, frameon=False, loc="upper right")
    axs[0].set_ylabel("min. anneal time, P(contact) ≥ 0.99 (min)", fontsize=7)
    fig.suptitle("300 nm pads, bonded sidewall: boundary of the contact window (above/right of curve = contact)", fontsize=7.5)
    fig.tight_layout(); fig.savefig(FIG / "s2_boundary_curves_300nm.png", dpi=300); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    # interface row omitted from the figure: paper scope is bonded sidewalls (draft v5); it stays in the JSON
    items = [(k, v["30min"], v["120min"], v["time_ratio_250C"]) for k, v in fac.items() if not k.startswith(("mechanism", "interface"))]
    items.sort(key=lambda r: -abs(np.nan_to_num(r[2])))
    y = np.arange(len(items))
    plt.close(fig); fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.3), sharey=True, gridspec_kw=dict(width_ratios=[1.5, 1]))
    ax2.barh(y, [r[3] for r in items], 0.5, color="0.45"); ax2.axvline(1, color="k", lw=0.6)
    for yy, r in zip(y, items):
        ax2.text(r[3] * 1.03, yy, f"×{r[3]:.1f}", va="center", fontsize=5.5)
    ax2.set_xscale("log"); ax2.set_xlim(0.9, 7); ax2.set_xticks([1, 2, 3, 5]); ax2.set_xticklabels(["1", "2", "3", "5"], fontsize=6.5)
    ax2.xaxis.set_minor_locator(matplotlib.ticker.NullLocator()); ax2.set_xlabel("× minimum anneal time at fixed T (250 °C)", fontsize=6.5)
    ax2.set_title("same factors in time units", fontsize=7)
    ax.barh(y - 0.18, [abs(np.nan_to_num(r[1])) for r in items], 0.36, label="at 30 min")
    ax.barh(y + 0.18, [abs(np.nan_to_num(r[2])) for r in items], 0.36, label="at 2 h")
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in items], fontsize=6.2); ax.invert_yaxis()
    ax.set_xlabel("shift of the boundary temperature (°C), 300 nm, clean", fontsize=6.5); ax.tick_params(axis="x", labelsize=6.5)
    ax.set_title("surface diffusion off: no closure at any T ≤ 400 °C (not shown)", fontsize=7); ax.tick_params(axis="y", labelsize=6.2)
    ax.legend(fontsize=6.5, frameon=False); fig.tight_layout(); fig.savefig(FIG / "s2_factor_shift_300nm.png", dpi=300); plt.close(fig)


if __name__ == "__main__":
    main()
