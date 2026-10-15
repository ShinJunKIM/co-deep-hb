r"""Master-curve fork (exploratory; data already seen): thermal-budget equivalence for DM2026 bulge-out.

Model: h(D, T, t) = a * D * [1 - exp(-t_eff / tau0)],   t_eff = t * exp(-Q/R (1/T - 1/T_ref)) * (200 nm / D)^n,  T_ref = 350 C.
Fit (a, Q, n, tau0) on PPA-Cu (Fig. 3, 10 points) by error-weighted least squares; evaluate the collapse on all std-Cu points;
self-annealed Cu gets an optional amplitude multiplier m_sa (fit separately, reported only).
Usage: python src\agents\master_curve.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "results" / "figures" / "agents"; OUT.mkdir(parents=True, exist_ok=True)
DOC = REPO / "docs" / "agents"; DOC.mkdir(parents=True, exist_ok=True)
R = 1.987e-3; TREF = 623.15


def load():
    d = json.loads((REPO / "inputs" / "dm2026_digitized.json").read_text(encoding="utf-8"))
    pts = [p for p in d["points"] if p["role"] != "duplicate-check"]
    std = [p for p in pts if p["cu"] == "std"]; fg = [p for p in pts if p["cu"] == "fg"]
    return std, fg


def t_eff(p, Q, n):
    return p["t_h"] * math.exp(-Q / R * (1 / (p["T_C"] + 273.15) - 1 / TREF)) * (200.0 / p["D_nm"]) ** n


def model(p, a, Q, n, tau0, m=1.0, beta=0.0):
    amp = a * p["D_nm"] * m * (1 + beta * (p["T_C"] - 350.0))
    return amp * (1 - math.exp(-t_eff(p, Q, n) / tau0))


def fit(points, fixed=None, beta_free=False):
    fixed = fixed or {}
    names = [k for k in ("a", "Q", "n", "tau0") if k not in fixed] + (["beta"] if beta_free else [])
    x0 = dict(a=0.055, Q=15.0, n=2.0, tau0=0.5, beta=0.0)
    bounds_lo = dict(a=0.01, Q=1.0, n=0.0, tau0=0.01, beta=-0.01); bounds_hi = dict(a=0.2, Q=40.0, n=6.0, tau0=50.0, beta=0.01)

    def unpack(x):
        prm = dict(fixed); prm.update({k: v for k, v in zip(names, x)}); prm.setdefault("beta", 0.0)
        return prm

    def resid(x):
        prm = unpack(x)
        return [(model(p, prm["a"], prm["Q"], prm["n"], prm["tau0"], beta=prm["beta"]) - p["median_nm"]) / max(p["err_nm"], 0.3) for p in points]

    best = None
    for Q0 in (8.0, 15.0, 22.0):
        for n0 in (1.0, 3.7):
            for tau0 in (0.2, 1.0, 5.0):
                x0d = dict(x0, Q=Q0, n=n0, tau0=tau0)
                r = least_squares(resid, [x0d[k] for k in names], bounds=([bounds_lo[k] for k in names], [bounds_hi[k] for k in names]))
                if best is None or r.cost < best.cost:
                    best = r
    prm = unpack(best.x)
    rms = math.sqrt(np.mean([(model(p, prm["a"], prm["Q"], prm["n"], prm["tau0"], beta=prm["beta"]) - p["median_nm"]) ** 2 for p in points]))
    return prm, rms, best


def bootstrap(points, nb=300, seed=0, fixed=None):
    rng = np.random.default_rng(seed); out = []
    for _ in range(nb):
        pts = [dict(p, median_nm=p["median_nm"] + rng.normal(0, p["err_nm"])) for p in points]
        prm, _, _ = fit(pts, fixed=fixed); out.append([prm["a"], prm["Q"], prm["n"], prm["tau0"]])
    out = np.array(out)
    return {k: (float(np.percentile(out[:, i], 16)), float(np.percentile(out[:, i], 84))) for i, k in enumerate(("a", "Q", "n", "tau0"))}


def main():
    std, fg = load()
    ppa = [p for p in std if p["history"] == "PPA250C"]; sa = [p for p in std if p["history"] == "self-anneal"]
    res = {}
    # ---- 1. free fit on PPA-Cu
    prm, rms, _ = fit(ppa); ci = bootstrap(ppa, nb=200)
    res["fit_free_PPA"] = dict(prm=prm, rms_nm=rms, ci68=ci, n_points=len(ppa), mean_err=float(np.mean([p["err_nm"] for p in ppa])))
    # ---- 2. constrained fits for comparison
    prm_pre, rms_pre, _ = fit(ppa, fixed=dict(Q=20.7, n=3.7)); res["fit_Q20.7_n3.7_PPA"] = dict(prm=prm_pre, rms_nm=rms_pre)
    prm_n, rms_n, _ = fit(ppa, fixed=dict(n=3.7)); res["fit_n3.7_PPA"] = dict(prm=prm_n, rms_nm=rms_n)
    prm_b, rms_b, _ = fit(ppa, beta_free=True); res["fit_free_beta_PPA"] = dict(prm=prm_b, rms_nm=rms_b)
    # ---- 3. evaluate on self-annealed Cu with PPA parameters, and with an amplitude multiplier
    def eval_pts(pts, prm, m=1.0):
        rows = []
        for p in pts:
            h = model(p, prm["a"], prm["Q"], prm["n"], prm["tau0"], m=m, beta=prm.get("beta", 0.0))
            tol = max(1.5, 0.25 * p["median_nm"], p["err_nm"])
            rows.append(dict(fig=p["figure"], D=p["D_nm"], T=p["T_C"], t=p["t_h"], hist=p["history"], meas=p["median_nm"], pred=h,
                             g=1 - math.exp(-t_eff(p, prm["Q"], prm["n"]) / prm["tau0"]), teff_h=t_eff(p, prm["Q"], prm["n"]), ok=abs(h - p["median_nm"]) <= tol))
        return rows
    rows_ppa = eval_pts(ppa, prm); rows_sa = eval_pts(sa, prm)
    ms = np.linspace(0.8, 2.5, 171)
    m_best = float(ms[np.argmin([sum(((model(p, prm["a"], prm["Q"], prm["n"], prm["tau0"], m=m) - p["median_nm"]) / p["err_nm"]) ** 2 for p in sa) for m in ms])])
    rows_sa_m = eval_pts(sa, prm, m=m_best)
    res["self_anneal"] = dict(m_best=m_best, pass_with_PPA_params=sum(r["ok"] for r in rows_sa), pass_with_m=sum(r["ok"] for r in rows_sa_m), n=len(sa))
    res["rows"] = dict(ppa=rows_ppa, sa=rows_sa, sa_m=rows_sa_m)
    # ---- 4. equivalence rule: time at T2 equivalent to 350 C x 1 h (same D), kinetics-only
    Q = prm["Q"]
    def t_equiv(T2, T1=350.0, t1=1.0):
        return t1 * math.exp(Q / R * (1 / (T2 + 273.15) - 1 / (T1 + 273.15)))
    res["equivalence_350C_1h"] = {f"{T}C": t_equiv(T) for T in (200, 225, 250, 275, 300, 325, 400, 450)}
    res["equivalence_Q20.7"] = {f"{T}C": 1.0 * math.exp(20.7 / R * (1 / (T + 273.15) - 1 / TREF)) for T in (200, 250, 300)}
    # time to reach 90 % of saturation at D = 300 and 115 nm
    res["t90_h"] = {f"D{D}_{T}C": -math.log(0.1) * prm["tau0"] / (math.exp(-Q / R * (1 / (T + 273.15) - 1 / TREF)) * (200.0 / D) ** prm["n"])
                    for D in (115, 300) for T in (200, 250, 300, 350)}
    # ---- 5. fg-Cu: equivalent delta-T at fixed time with std parameters (if below saturation), else amplitude ratio
    fgrows = []
    for p in fg:
        hist_m = 1.0 if p["history"] == "PPA250C" else m_best
        h_std = model(p, prm["a"], prm["Q"], prm["n"], prm["tau0"], m=hist_m)
        amp = prm["a"] * p["D_nm"] * hist_m
        dT = None
        if p["median_nm"] < 0.98 * amp:
            lo, hi = p["T_C"] - 200, p["T_C"] + 300
            for _ in range(60):
                mid = 0.5 * (lo + hi); q = dict(p, T_C=mid)
                if model(q, prm["a"], prm["Q"], prm["n"], prm["tau0"], m=hist_m) < p["median_nm"]: lo = mid
                else: hi = mid
            dT = 0.5 * (lo + hi) - p["T_C"]
        fgrows.append(dict(fig=p["figure"], D=p["D_nm"], T=p["T_C"], t=p["t_h"], hist=p["history"], h_fg=p["median_nm"], h_std_model=h_std,
                           shift_nm=p["median_nm"] - h_std, amp_ratio=p["median_nm"] / amp, equiv_dT_C=dT))
    res["fg_cu"] = fgrows
    # ---- 6. saturation check
    sat = {}
    for D, fig in ((250, "Fig.3"), (300, "Fig.3")):
        p350 = next(p for p in ppa if p["D_nm"] == D and p["T_C"] == 350); p450 = next(p for p in ppa if p["D_nm"] == D and p["T_C"] == 450)
        g350 = 1 - math.exp(-t_eff(p350, Q, prm["n"]) / prm["tau0"]); g450 = 1 - math.exp(-t_eff(p450, Q, prm["n"]) / prm["tau0"])
        sat[f"D{D}"] = dict(R_meas=p450["median_nm"] / p350["median_nm"], R_kinetic=g450 / g350, g350=g350, g450=g450,
                           R_with_beta=(model(p450, prm_b["a"], prm_b["Q"], prm_b["n"], prm_b["tau0"], beta=prm_b["beta"]) /
                                        model(p350, prm_b["a"], prm_b["Q"], prm_b["n"], prm_b["tau0"], beta=prm_b["beta"])))
    res["saturation"] = sat
    json.dump(res, open(DOC / "master_curve_results.json", "w"), indent=1, default=float)
    # ---- print
    print("free fit (PPA):", {k: round(v, 4) for k, v in prm.items()}, "rms", round(rms, 2), "nm; mean err", round(res["fit_free_PPA"]["mean_err"], 2), "; CI68", {k: tuple(round(x, 2) for x in v) for k, v in ci.items()})
    print("Q=20.7,n=3.7 fit:", {k: round(v, 4) for k, v in prm_pre.items()}, "rms", round(rms_pre, 2))
    print("n=3.7 fit:", {k: round(v, 4) for k, v in prm_n.items()}, "rms", round(rms_n, 2))
    print("beta-free fit:", {k: round(v, 5) for k, v in prm_b.items()}, "rms", round(rms_b, 2))
    for r in rows_ppa: print(f"  PPA D{r['D']} {r['T']}C {r['t']}h meas {r['meas']:.1f} pred {r['pred']:.1f} g {r['g']:.2f} {'ok' if r['ok'] else 'FAIL'}")
    for r, r2 in zip(rows_sa, rows_sa_m): print(f"  SA  D{r['D']} {r['T']}C {r['t']}h meas {r['meas']:.1f} pred {r['pred']:.1f} ({'ok' if r['ok'] else 'FAIL'}) | with m={m_best:.2f}: {r2['pred']:.1f} ({'ok' if r2['ok'] else 'FAIL'})")
    print("equivalence (= 350 C x 1 h):", {k: round(v, 2) for k, v in res["equivalence_350C_1h"].items()}, "| with Q 20.7:", {k: round(v, 1) for k, v in res["equivalence_Q20.7"].items()})
    print("t90 (h):", {k: round(v, 2) for k, v in res["t90_h"].items()})
    for r in fgrows: print(f"  fg D{r['D']} {r['T']}C {r['hist'][:4]} h_fg {r['h_fg']:.1f} std-model {r['h_std_model']:.1f} shift {r['shift_nm']:+.1f} amp ratio {r['amp_ratio']:.2f} equiv dT {r['equiv_dT_C'] if r['equiv_dT_C'] is None else round(r['equiv_dT_C'], 0)}")
    print("saturation:", {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in sat.items()})
    # ---- figure: collapse
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
    ax = axs[0]
    for pts, mk, lab, m in ((ppa, "o", "PPA-Cu (fit set)", 1.0), (sa, "s", f"self-annealed Cu (×{m_best:.2f})", m_best)):
        x = [t_eff(p, prm["Q"], prm["n"]) for p in pts]; y = [p["median_nm"] / (prm["a"] * p["D_nm"] * m) for p in pts]
        yerr = [p["err_nm"] / (prm["a"] * p["D_nm"] * m) for p in pts]
        ax.errorbar(x, y, yerr=yerr, fmt=mk, ms=4, capsize=2, label=lab)
    xx = np.logspace(-2.5, 1.5, 200); ax.plot(xx, 1 - np.exp(-xx / prm["tau0"]), "k-", lw=1, label="1 − exp(−t_eff/τ₀)")
    ax.set_xscale("log"); ax.set_xlabel("effective time t_eff (h at 350 °C, 200 nm)"); ax.set_ylabel("h / h_sat(D)")
    ax.set_title(f"master curve: Q_eff {prm['Q']:.1f} kcal/mol, n {prm['n']:.1f}, τ₀ {prm['tau0']:.2f} h (exploratory)", fontsize=8); ax.legend(fontsize=6.5, frameon=False)
    ax = axs[1]
    Ts = np.linspace(200, 450, 100)
    for t1, lab in ((1.0, "≡ 350 °C × 1 h"), (0.5, "≡ 350 °C × 30 min")):
        ax.plot(Ts, [t1 * math.exp(Q / R * (1 / (T + 273.15) - 1 / TREF)) for T in Ts], label=f"fit Q_eff {Q:.1f}: {lab}")
    ax.plot(Ts, [math.exp(20.7 / R * (1 / (T + 273.15) - 1 / TREF)) for T in Ts], "k--", lw=1, label="Butrymowicz Q 20.7: ≡ 350 °C × 1 h")
    ax.set_yscale("log"); ax.set_xlabel("anneal T (°C)"); ax.set_ylabel("equivalent time (h)"); ax.set_ylim(0.05, 100)
    ax.axhline(2, color="gray", lw=0.6); ax.axhline(4, color="gray", lw=0.6); ax.set_title("thermal-budget equivalence rule", fontsize=8); ax.legend(fontsize=6, frameon=False)
    fig.tight_layout(); fig.savefig(OUT / "master_curve.png", dpi=300); plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
