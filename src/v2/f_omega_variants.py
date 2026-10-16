r"""v2 diffusion orientation-function study (exploratory: DM2026 already seen).

1) f(omega) variants fitted at the 500 nm pitch / 350 C / 1 h point (quantiles q1..q90 + tail fraction range),
2) held-out medians/IQR on the 17 DM2026 std-Cu points for each variant,
3) beta (stretched-exponential) doubling-ratio check against the 200 C 2 h / 4 h medians,
4) contact probability (uniform orientation = ASSUMPTION) vs worst-orientation minimum margin (orientation-distribution
   free), three-region maps over the uncertainty set b x tau0 x Q x variants, pair-dependence sensitivity.

The elastic coefficient per orientation sample is a switchable function k_fn(v) (default: the existing Ez quadratic fit
results/stage2/predict_<size>_fit.json); the parent replaces it with the hkl surrogate later.
Monte Carlo sample counts are numerical resolution, not data.
Usage: python src\v2\f_omega_variants.py [--n 100000]
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src" / "stage2"))
import stage2_diffusion_val as V  # noqa: E402

OUT = REPO / "results" / "stage2" / "v2"; OUT.mkdir(parents=True, exist_ok=True)
FIG = REPO / "results" / "figures" / "v2"; FIG.mkdir(parents=True, exist_ok=True)
R_GAS = 1.987e-3
V111 = np.array([[1, 1, 1], [1, 1, -1], [1, -1, 1], [-1, 1, 1]], float) / math.sqrt(3)
C11, C12, C44 = 168400.0, 121400.0, 75400.0
QS_FIT = np.array([0.01, 0.02, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90])
W_Q = np.array([0.5, 0.5, 0.5, 1, 1, 1, 1, 1])   # low-tail quantiles (1-5 %) weighted half: few pads, larger reading error
TS = (200, 250, 300, 350, 400); TMIN = (5, 30, 120)
SURF = {"clean": 1.0, "oxidised": 0.45}
B_GRID = (0.60, 0.69, 0.93, 1.0); TAU0_GRID = (20.0, 60.0, 100.0); Q_GRID = (20.7, 13.4)
P_WIN = 0.99


# ------------------------------------------------------------------ orientation helpers
def directions(n, rng):
    v = rng.normal(size=(n, 3)); return v / np.linalg.norm(v, axis=1)[:, None]


def omega_of(v):
    return np.degrees(np.arccos(np.clip(np.abs(v @ V111.T).max(axis=1), -1, 1)))


def ez_of(v):
    l, m, n = np.abs(v).T
    den = (C11 - C12) * (C11 + 2 * C12); s11, s12, s44 = (C11 + C12) / den, -C12 / den, 1 / C44
    return 1.0 / (s11 - 2 * (s11 - s12 - s44 / 2) * (l * l * m * m + m * m * n * n + n * n * l * l)) / 1000.0


def k_ez_fit(label):
    coef = np.array(json.loads((REPO / "results" / "stage2" / f"predict_{label}_fit.json").read_text())["fit"]["coef"])
    return lambda v: np.polyval(coef, ez_of(v))          # nm/K per pad (array cell, bonded) -- PLACEHOLDER for hkl surrogate


# ------------------------------------------------------------------ f(omega) families
def f_ramp(om, p):            # p = (omega_c, d_omega)
    oc, dw = p
    return (om > oc).astype(float) if dw <= 1e-9 else np.clip((om - oc) / dw, 0, 1)


def f_floor(om, p):           # p = (f_min, omega_c, d_omega): faceted pads still bulge a little
    fm, oc, dw = p
    return fm + (1 - fm) * f_ramp(om, (oc, dw))


def f_sigmoid(om, p):         # p = (omega_50, width)
    o5, s = p
    return 1.0 / (1.0 + np.exp(-(om - o5) / max(s, 1e-6)))


TAIL_FIG3 = (0.025, 0.05)    # fraction below 6.5 nm, DM2026 Fig 3, 500 nm pitch 350 C 1 h (low quantiles: 2 % -> 4.3 nm, 3 % -> 6.4 nm)
TAIL_FIG5 = (0.08, 0.12)     # DM2026 Fig 5a target array (280 nm pad, 350 C), ~10 %
VARIANTS = {   # name: (family, initial params, param bounds or None=fixed, use scatter, tail target range)
    "V1 ramp (round 2, fixed)": (f_ramp, (5.0, 19.5), None, False, TAIL_FIG3),
    "V2 step facet + scatter": (f_ramp, (8.0, 0.0), ((1, 14), (0, 0)), True, TAIL_FIG3),
    "V3 ramp + scatter": (f_ramp, (6.0, 8.0), ((0, 12), (3, 25)), True, TAIL_FIG3),
    "V4 floor 0.25 + scatter": (f_floor, (0.25, 8.0, 4.0), ((0.25, 0.25), (0, 14), (0, 15)), True, TAIL_FIG3),
    "V5 sigmoid": (f_sigmoid, (14.0, 6.0), ((4, 30), (1, 15)), False, TAIL_FIG3),
    "V6 step facet, Fig5a tail": (f_ramp, (12.8, 0.0), ((9, 16), (0, 0)), True, TAIL_FIG5),
    "V7 ramp, Fig5a tail": (f_ramp, (10.0, 10.0), ((5, 16), (2, 25)), True, TAIL_FIG5),
}


def kin(D_nm, T_C, t_s, tau0=60.0, Q=20.7, beta=1.0):
    tau = tau0 * (D_nm / 200.0) ** 3.7 * math.exp(Q / R_GAS * (1 / (T_C + 273.15) - 1 / 623.15))
    return 1.0 - math.exp(-(t_s / tau) ** beta)


def h_samples(om, z, fam, p, theta, sig, D, T, t_s, s_ox=1.0, tau0=60.0, Q=20.7):
    """per-pad bulge-out samples; z = standard normals for the orientation-independent lognormal scatter."""
    sc = np.exp(sig * z - 0.5 * sig * sig) if sig > 0 else 1.0
    return s_ox * 0.0022 * (theta - 90.0) * D * fam(om, p) * sc * kin(D, T, t_s, tau0, Q)


# ------------------------------------------------------------------ data
def load():
    data = json.loads((REPO / "inputs" / "dm2026_digitized.json").read_text(encoding="utf-8"))
    pts = [p for p in data["points"] if p["cu"] == "std" and p["role"] in ("calibration", "held-out")]
    for p in pts:
        for k in ("q10", "q25", "q75", "q90"):
            v = p.get(k)
            if v is None or not np.isfinite(v) or (k in ("q10", "q25") and v > p["median_nm"]) or (k in ("q75", "q90") and v < p["median_nm"]):
                p[k] = float("nan")
    tail = json.loads((OUT / "dm2026_tail_readout.json").read_text())
    cal = next(p for p in pts if p["pitch_nm"] == 500 and p["T_C"] == 350 and p["figure"] == "Fig.3")
    lq = tail["500nm"]["low_quantiles"]
    meas_q = np.array([lq["0.01"], lq["0.02"], lq["0.05"], cal["q10"], cal["q25"], cal["median_nm"], cal["q75"], cal["q90"]])
    return pts, cal, meas_q, tail


def fit_variant(name, om, z, meas_q, tail_rng=None):
    fam, p0, bounds, use_sc, tail_rng = VARIANTS[name]
    D, T, t = 300.0, 350, 3600.0
    best = None
    thetas = np.arange(105.0, 150.1, 1.0)
    sigs = (0.0,) if not use_sc else np.arange(0.0, 0.61, 0.05)
    if bounds is None:
        grids = [p0]
    else:
        axes = [np.linspace(lo, hi, 9) if hi > lo else np.array([lo]) for lo, hi in bounds]
        grids = list(itertools.product(*axes))
    for p in grids:
        fv = fam(om, p)
        for sig in sigs:
            sc = np.exp(sig * z - 0.5 * sig * sig) if sig > 0 else 1.0
            base = 0.0022 * D * fv * sc * kin(D, T, t)
            qb = np.quantile(base, QS_FIT); bs = np.sort(base)
            for th in thetas:
                q = (th - 90.0) * qb
                frac = float(np.searchsorted(bs, 6.5 / (th - 90.0)) / len(bs))
                pen = 0.0 if tail_rng[0] <= frac <= tail_rng[1] else 1.0e4 * min(abs(frac - tail_rng[0]), abs(frac - tail_rng[1]))
                sse = float(np.sum(((q - meas_q) * W_Q) ** 2)) + pen
                if best is None or sse < best[0]:
                    best = (sse, tuple(float(x) for x in p), float(sig), float(th), q, frac)
    sse, p, sig, th, q, frac = best
    hi = QS_FIT >= 0.10
    return dict(params=p, scatter=sig, theta=th, rms=float(np.sqrt(np.mean((q[hi] - meas_q[hi]) ** 2))),
                rms_low_tail=float(np.sqrt(np.mean((q[~hi] - meas_q[~hi]) ** 2))), q_pred=q.tolist(), tail_frac=frac, tail_target=list(tail_rng))


def evaluate_heldout(name, fit, om, z, pts):
    fam = VARIANTS[name][0]
    rows = []
    for p in pts:
        h = h_samples(om, z, fam, fit["params"], fit["theta"], fit["scatter"], p["D_nm"], p["T_C"], p["t_h"] * 3600)
        q25, q50, q75 = np.quantile(h, [0.25, 0.5, 0.75])
        tol = max(1.5, 0.25 * p["median_nm"], p["err_nm"])
        iqr_m = p["q75"] - p["q25"]
        rows.append(dict(figure=p["figure"], pitch_nm=p["pitch_nm"], D_nm=p["D_nm"], T_C=p["T_C"], t_h=p["t_h"], history=p["history"],
                         role=p["role"], cu="std", median_nm=p["median_nm"], err_nm=p["err_nm"], pred_nm=float(q50),
                         pass_median=bool(abs(q50 - p["median_nm"]) <= tol),
                         pass_iqr=(bool(abs((q75 - q25) - iqr_m) <= max(1.5, 0.5 * iqr_m)) if np.isfinite(iqr_m) else None)))
    ho = [r for r in rows if r["role"] == "held-out"]
    tr = V.trends(rows)
    r = lambda pit: next(x for x in rows if x["figure"] == "Fig.3" and x["pitch_nm"] == pit and x["T_C"] == 200 and x["t_h"] == 4)["pred_nm"] / \
        next(x for x in rows if x["figure"] == "Fig.3" and x["pitch_nm"] == pit and x["T_C"] == 200 and x["t_h"] == 2)["pred_nm"]
    by_hist = {}
    for hname in ("PPA250C", "self-anneal"):
        sub = [x for x in ho if x["history"] == hname]
        by_hist[hname] = f"{sum(x['pass_median'] for x in sub)}/{len(sub)}"
    return dict(median_pass=f"{sum(x['pass_median'] for x in ho)}/{len(ho)}",
                iqr_pass=f"{sum(1 for x in ho if x['pass_iqr'])}/{sum(1 for x in ho if x['pass_iqr'] is not None)}",
                T_trend=tr["T_trend_ok"], saturation=tr["saturation_ok"], ratio_4h_2h_pred={"400": r(400), "500": r(500)},
                by_history=by_hist, rows=rows)


# ------------------------------------------------------------------ beta check
def beta_check(pts):
    out = {}
    ratios, sigs = [], []
    for pit in (400, 500):
        a2 = next(p for p in pts if p["figure"] == "Fig.3" and p["pitch_nm"] == pit and p["T_C"] == 200 and p["t_h"] == 2)
        a4 = next(p for p in pts if p["figure"] == "Fig.3" and p["pitch_nm"] == pit and p["T_C"] == 200 and p["t_h"] == 4)
        R = a4["median_nm"] / a2["median_nm"]
        s = R * math.sqrt((a4["err_nm"] / a4["median_nm"]) ** 2 + (a2["err_nm"] / a2["median_nm"]) ** 2)
        ratios.append(R); sigs.append(s)
        out[str(pit)] = dict(m2=a2["median_nm"], m4=a4["median_nm"], ratio=R, sigma=s, beta_min_central=math.log2(R),
                             beta_min_1sigma=math.log2(max(R - s, 1.0)), beta_min_2sigma=math.log2(max(R - 2 * s, 1.0)),
                             sigma_above_beta025_bound=(R - 2 ** 0.25) / s, sigma_vs_beta1_bound=(R - 2.0) / s)
    w = 1 / np.array(sigs) ** 2
    Rm = float(np.sum(w * np.array(ratios)) / np.sum(w)); sm = float(1 / math.sqrt(np.sum(w)))
    out["combined"] = dict(ratio=Rm, sigma=sm, sigma_above_beta025_bound=(Rm - 2 ** 0.25) / sm, beta_min_central=math.log2(Rm),
                           beta_min_2sigma=math.log2(max(Rm - 2 * sm, 1.0)),
                           note="digitization error only; wafer-to-wafer and pad-sampling scatter of the medians not included; the 2^beta bound is the small-t limit (g < bound for all t)")
    return out


# ------------------------------------------------------------------ windows
_CACHE = {}


def worst_margin(dirs, k_fn, fam, p, theta, sig, D, T, t_s, s_ox, b, tau0, Q, R_sum, z_q=None):
    """Orientation-distribution-free minimum margin: both pads at the orientation that minimises u + h.
    scatter (if any) taken at its lower quantile z_q (default 1st percentile of the lognormal), stated as such."""
    key = (id(dirs), id(k_fn))
    if key not in _CACHE:
        _CACHE[key] = (k_fn(dirs), omega_of(dirs))
    kd, omd = _CACHE[key]
    fkey = (id(dirs), fam.__name__, tuple(p))
    if fkey not in _CACHE:
        _CACHE[fkey] = fam(omd, p)
    u = b * kd * (T - 25.0)
    sc = math.exp(sig * (z_q if z_q is not None else -2.326) - 0.5 * sig * sig) if sig > 0 else 1.0
    h = s_ox * 0.0022 * (theta - 90.0) * D * _CACHE[fkey] * sc * kin(D, T, t_s, tau0, Q)
    tot = u + h
    i = int(np.argmin(tot))
    return float(2 * tot[i] - R_sum), float(2 * u.min() - R_sum), float(omd[i])


def hkl_k_fn(side="bonded"):
    """Accepted orientation surrogate k(x, y) [nm/K per pad], x = k/h, y = l/h of the sorted direction (300 nm, imec stack)."""
    import json as _json
    study = _json.loads((OUT / "orientation_study.json").read_text())
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import orient_window as _OW
    k_fn, _ = _OW.make_k_fn(study, side)
    return k_fn


def run_windows(size_label, size_um, variants_fit, n, seed, k_fn=None):
    """k_fn(v): per-pad elastic coefficient (nm/K) for unit direction vectors v (N, 3); default = Ez quadratic fit (placeholder)."""
    rng = np.random.default_rng(seed)
    k_fn = k_fn or k_ez_fit(size_label)
    D = size_um * 1000.0
    v1, v2 = directions(n, rng), directions(n, rng)
    om1, om2 = omega_of(v1), omega_of(v2)
    k1, k2 = k_fn(v1), k_fn(v2)
    z1, z2 = rng.normal(size=n), rng.normal(size=n)
    g = rng.normal(2.5, 0.5, n) + rng.normal(2.5, 0.5, n)
    R_q99 = 5.0 + 2.326 * math.sqrt(2) * 0.5
    grid_dirs = directions(200_000, np.random.default_rng(seed + 7))
    grid_dirs = np.vstack([grid_dirs, np.array([[1, 1, 1], [0, 0, 1], [1, 0, 1]], float) / np.array([[math.sqrt(3)], [1], [math.sqrt(2)]])])
    res = dict(size_um=size_um, R_q99_sum=R_q99, surfaces={})
    for surf, s_ox in SURF.items():
        cell = {}
        for T in TS:
            for tm in TMIN:
                P_el = {b: float(np.mean(b * (k1 + k2) * (T - 25.0) >= g)) for b in B_GRID}
                combos = []
                for vname, fit in variants_fit.items():
                    fam = VARIANTS[vname][0]
                    for b, tau0, Q in itertools.product(B_GRID, TAU0_GRID, Q_GRID):
                        h1 = h_samples(om1, z1, fam, fit["params"], fit["theta"], fit["scatter"], D, T, tm * 60, s_ox, tau0, Q)
                        h2 = h_samples(om2, z2, fam, fit["params"], fit["theta"], fit["scatter"], D, T, tm * 60, s_ox, tau0, Q)
                        P = float(np.mean(b * (k1 + k2) * (T - 25.0) + h1 + h2 >= g))
                        mm, mel, om_w = worst_margin(grid_dirs, k_fn, fam, fit["params"], fit["theta"], fit["scatter"], D, T, tm * 60,
                                                     s_ox, b, tau0, Q, R_q99)
                        combos.append(dict(variant=vname, b=b, tau0=tau0, Q=Q, P=P, m_min_q99=mm, m_el_q99=mel, worst_omega=om_w))
                main = [c for c in combos if c["b"] == 0.69 and c["tau0"] == 60.0 and c["Q"] == 20.7]
                Ps = [c["P"] for c in combos]; Ms = [c["m_min_q99"] for c in combos]
                el_closes = all(P_el[b] >= P_WIN for b in B_GRID)
                if el_closes:
                    region = "1 elastic alone closes"
                elif all(p >= P_WIN for p in Ps):  # noqa
                    region = "2 needs diffusion, closes for all (probability)"
                elif not any(p >= P_WIN for p in Ps):
                    region = "4 does not close for any combination"
                else:
                    region = "3 undetermined (depends on variant/b/tau0/Q)"
                worst_region = ("closes in worst orientation for all combos" if all(m >= 0 for m in Ms) else
                                ("fails in worst orientation for all combos" if not any(m >= 0 for m in Ms) else "worst-orientation undetermined"))
                cell[f"{T}C_{tm}min"] = dict(P_elastic=P_el, region=region, worst_region=worst_region,
                                             P_main_by_variant={c["variant"]: c["P"] for c in main},
                                             m_min_main_by_variant={c["variant"]: c["m_min_q99"] for c in main},
                                             P_range=[min(Ps), max(Ps)], m_min_range=[min(Ms), max(Ms)],
                                             worst_omega_main={c["variant"]: c["worst_omega"] for c in main})
        res["surfaces"][surf] = cell
    # fixed-recess grid (per pad 1..8 nm): allowable per-pad recess at main setting, probability vs worst orientation
    allow = {}
    for vname, fit in variants_fit.items():
        fam = VARIANTS[vname][0]
        allow[vname] = {}
        for T, tm in ((250, 120), (300, 30), (350, 30), (400, 30)):
            h1 = h_samples(om1, z1, fam, fit["params"], fit["theta"], fit["scatter"], D, T, tm * 60, 1.0, 60.0, 20.7)
            h2 = h_samples(om2, z2, fam, fit["params"], fit["theta"], fit["scatter"], D, T, tm * 60, 1.0, 60.0, 20.7)
            tot = 0.69 * (k1 + k2) * (T - 25.0) + h1 + h2
            r_prob = max([r for r in np.arange(0.5, 15.01, 0.5) if np.mean(tot >= 2 * r) >= P_WIN], default=0.0)
            mm, _, _ = worst_margin(grid_dirs, k_fn, fam, fit["params"], fit["theta"], fit["scatter"], D, T, tm * 60, 1.0, 0.69, 60.0, 20.7, 0.0)
            allow[vname][f"{T}C_{tm}min"] = dict(r_per_pad_prob99=float(r_prob), r_per_pad_worst=max(0.0, mm / 2.0))
    res["allowable_recess_clean"] = allow
    # pair-dependence sensitivity (main setting, V1): independent vs same-rank vs opposite-rank pairing of total protrusion
    pv = next(iter(variants_fit)); fam = VARIANTS[pv][0]; fit = variants_fit[pv]
    pair = {}
    for T, tm in ((250, 120), (300, 30), (350, 30)):
        h1 = h_samples(om1, z1, fam, fit["params"], fit["theta"], fit["scatter"], D, T, tm * 60, 1.0, 60.0, 20.7)
        t1 = 0.69 * k1 * (T - 25.0) + h1
        s = np.sort(t1)
        pair[f"{T}C_{tm}min"] = dict(independent=float(np.mean(t1 + np.random.default_rng(1).permutation(t1) >= g)),
                                    same_rank=float(np.mean(2 * s >= np.sort(g))), opposite_rank=float(np.mean(s + s[::-1] >= np.sort(g))))
    res["pair_dependence_sensitivity_clean"] = dict(variant=pv, cells=pair)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=100_000); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--ezfit", action="store_true", help="use the Ez quadratic fit for 300 nm (comparison run)"); ap.add_argument("--tag", default="")
    a = ap.parse_args(argv)
    rng = np.random.default_rng(a.seed)
    pts, cal, meas_q, tail = load()
    tail_rng = (TAIL_FIG3, TAIL_FIG5)
    om = omega_of(directions(a.n, rng)); z = rng.normal(size=a.n)
    fits = {}
    for name in VARIANTS:
        fits[name] = fit_variant(name, om, z, meas_q)
        fam = VARIANTS[name][0]
        fv = fam(om, fits[name]["params"])
        fits[name].update(frac_f0=float(np.mean(fv <= 1e-9)), frac_f_lt_half=float(np.mean(fv < 0.5)),
                          consistent=bool(fits[name]["rms"] <= 1.0 and fits[name]["tail_target"][0] <= fits[name]["tail_frac"] <= fits[name]["tail_target"][1]))
        ev = evaluate_heldout(name, fits[name], om, z, pts)
        fits[name]["heldout"] = {k: v for k, v in ev.items() if k != "rows"}
        fits[name]["heldout_rows"] = ev["rows"]
        print(f"{name:26s} params {fits[name]['params']} scatter {fits[name]['scatter']:.2f} theta {fits[name]['theta']:.0f} rms {fits[name]['rms']:.2f}/{fits[name]['rms_low_tail']:.2f} "
              f"tail<6.5 {fits[name]['tail_frac']:.3f} f=0 {fits[name]['frac_f0']:.3f} f<0.5 {fits[name]['frac_f_lt_half']:.3f} consistent {fits[name]['consistent']} | "
              f"held-out med {ev['median_pass']} IQR {ev['iqr_pass']} T {ev['T_trend']} sat {ev['saturation']} 4h/2h {ev['ratio_4h_2h_pred']['400']:.2f}/{ev['ratio_4h_2h_pred']['500']:.2f} hist {ev['by_history']}")
    beta = beta_check(pts)
    print("beta check:", json.dumps(beta["combined"]))
    use = {k: v for k, v in fits.items() if v["consistent"]} or fits
    win = {}
    for label, size in (("0.30um", 0.30), ("0.54um", 0.54)):
        # option (a), 2026-10-16: 300 nm elastic term = hkl surrogate from the 154-run orientation study (bonded sidewall,
        # results/stage2/v2/orientation_study.json, pre-registered acceptance passed); 0.54 um keeps the Ez fit (no hkl study)
        kf = hkl_k_fn("bonded") if (label == "0.30um" and not a.ezfit) else None
        win[label] = run_windows(label, size, use, max(20_000, a.n // 2), a.seed, k_fn=kf)
    json.dump(dict(status="exploratory (DM2026 data already seen); uniform orientation is an assumption; MC sample counts are not data",
                   tail_readout=tail, tail_fraction_range_used=tail_rng, fits={k: {kk: vv for kk, vv in v.items() if kk != "heldout_rows"} for k, v in fits.items()},
                   variants_used_for_windows=list(use), beta_check=beta, windows=win), open(OUT / f"f_omega_variants{a.tag}.json", "w"), indent=1, default=float)
    for label in win:
        for surf in SURF:
            regs = {}
            for c, d in win[label]["surfaces"][surf].items():
                regs.setdefault(d["region"], []).append(c)
            print(label, surf, {k: len(v) for k, v in regs.items()})
    if not a.ezfit:
        figures(fits, meas_q, om, z, win)
    return 0


def figures(fits, meas_q, om, z, win):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from scipy.stats import norm
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
    w = np.linspace(0, 54.74, 300)
    for name, fit in fits.items():
        fam = VARIANTS[name][0]
        axs[0].plot(w, fam(w, fit["params"]), label=name + ("" if fit["consistent"] else " (inconsistent)"))
        h = h_samples(om, z, fam, fit["params"], fit["theta"], fit["scatter"], 300.0, 350, 3600)
        hs = np.sort(h); pp = (np.arange(len(hs)) + 0.5) / len(hs); sel = slice(None, None, max(1, len(hs) // 2000))
        axs[1].plot(hs[sel], norm.ppf(pp[sel]), lw=1)
    axs[1].plot(meas_q, norm.ppf(QS_FIT), "ks", ms=4, label="DM2026 Fig. 3 (500 nm pitch, 350 °C 1 h)")
    axs[1].axvline(6.5, color="gray", lw=0.8, ls=":")
    axs[0].set_xlabel("ω to nearest <111> (deg)"); axs[0].set_ylabel("f(ω)"); axs[0].legend(fontsize=6, frameon=False)
    axs[1].set_xlabel("bulge-out per pad (nm)"); axs[1].set_ylabel("probit"); axs[1].set_ylim(-3.2, 2.5)
    yt = [0.001, 0.01, 0.1, 0.5, 0.9, 0.99]; axs[1].set_yticks(norm.ppf(yt)); axs[1].set_yticklabels([f"{100 * y:g}" for y in yt])
    axs[1].axhspan(-3.2, norm.ppf(0.005), color="0.9"); axs[1].text(1, norm.ppf(0.002), "unobserved (< lowest plotted point)", fontsize=6)
    axs[1].legend(fontsize=6, frameon=False, loc="lower right")
    fig.tight_layout(); fig.savefig(FIG / "f_omega_variants.png", dpi=300); plt.close(fig)
    cmap = {"1": "#2c7bb6", "2": "#abd9e9", "3": "#fdae61", "4": "#d7191c"}
    for label in ("0.30um",):
        fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.0), sharey=True)
        for ax, surf in zip(axs, SURF):
            cells = win[label]["surfaces"][surf]
            for i, tm in enumerate(TMIN):
                for j, T in enumerate(TS):
                    d = cells[f"{T}C_{tm}min"]
                    ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color=cmap[d["region"][0]]))
                    ax.text(j, i, f"{d['P_range'][0]:.2f}–{d['P_range'][1]:.2f}", ha="center", va="center", fontsize=5.5)
            ax.set_xlim(-0.5, 4.5); ax.set_ylim(-0.5, 2.5)
            ax.set_xticks(range(5)); ax.set_xticklabels([str(T) for T in TS]); ax.set_yticks(range(3)); ax.set_yticklabels([str(t) for t in TMIN])
            ax.set_title(f"{label}, {surf}", fontsize=8); ax.set_xlabel("anneal T (°C)")
        axs[0].set_ylabel("anneal time (min)")
        handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in cmap.values()]
        fig.legend(handles, ["elastic alone closes", "needs diffusion, closes for all", "undetermined", "does not close"], fontsize=6.5,
                   frameon=False, loc="lower center", ncol=4)
        fig.suptitle("three-region map (P ≥ 0.99 over b × τ₀ × Q × f-variants; numbers = P range; uniform orientation assumed)", fontsize=7.5)
        fig.tight_layout(rect=(0, 0.07, 1, 0.94)); fig.savefig(FIG / f"three_region_map_{label}.png", dpi=300); plt.close(fig)
        fig, ax = plt.subplots(figsize=(5.6, 3.0))
        cells = win[label]["surfaces"]["clean"]
        xs = [f"{T}/{tm}" for tm in TMIN for T in TS]
        for vname in next(iter(cells.values()))["m_min_main_by_variant"]:
            ax.plot(range(len(xs)), [cells[f"{T}C_{tm}min"]["m_min_main_by_variant"][vname] for tm in TMIN for T in TS], "o-", ms=3, label=vname)
        ax.axhline(0, color="k", lw=0.8); ax.set_xticks(range(len(xs))); ax.set_xticklabels(xs, rotation=60, fontsize=6)
        ax.set_ylabel("worst-orientation margin m_min (nm)\n(recess sum q99 = 6.6 nm)"); ax.set_xlabel("anneal T (°C) / time (min)")
        ax.legend(fontsize=6, frameon=False); ax.set_title(f"{label} clean: orientation-distribution-free margin (b 0.69, τ₀ 60 s, Q 20.7)", fontsize=7.5)
        fig.tight_layout(); fig.savefig(FIG / f"worst_margin_{label}.png", dpi=300); plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
