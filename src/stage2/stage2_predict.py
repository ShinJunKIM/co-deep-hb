r"""Stage 2 prediction: contact-stage process window = elastic u (FEM, orientation random) + analytic surface-diffusion
term h_d (pre-registration 3.3) versus top + bottom recess (IRPS 2026 distribution). Monte Carlo over orientation
and recess. Outputs results/stage2/predict_*.csv/json and results/figures/s2_*.png.

Usage: python src\stage2\stage2_predict.py [--size 0.54,0.30] [--n 200000]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "stage1"))
import baseline as B  # noqa: E402
sys.modules.setdefault("baseline", B)
import stage2_runs  # noqa: E402,F401
import stage1_pipeline as S  # noqa: E402

OUT = B.RESULTS / "stage2"; OUT.mkdir(parents=True, exist_ok=True)
FIG = B.RESULTS / "figures"; FIG.mkdir(parents=True, exist_ok=True)
R_GAS = 1.987e-3   # kcal/mol/K

# ---------------------------------------------------------------- surface-diffusion term (pre-registration 3.3, fixed)
Q_KCAL = 20.7                  # Butrymowicz 1973 (Bonzel-Gjostein)
THETA_TA = 123.0               # Cu/Ta contact angle (DM2024)
TAU0_RANGE = (20.0, 100.0)     # s, for D = 200 nm at 350 C
THETA_RANGE = (107.0, 149.0)
S_OX = (0.3, 0.6)              # oxidised-surface factor (switch)


def h_inf(D_nm, theta=THETA_TA):
    """Complete-diffusion centre extension (nm), linearised DM2024 Fig 8b/10a: 0.0022*(theta-90)*D."""
    return 0.0022 * (theta - 90.0) * D_nm


def Ds_ratio(T_C, T_ref_C=350.0, Q=Q_KCAL):
    return math.exp(-Q / R_GAS * (1 / (T_C + 273.15) - 1 / (T_ref_C + 273.15)))


def tau(D_nm, T_C, tau0=60.0):
    return tau0 * (D_nm / 200.0) ** 3.7 / Ds_ratio(T_C)


def h_d(t_s, T_C, D_nm, theta=THETA_TA, tau0=60.0, s_ox=1.0):
    return s_ox * h_inf(D_nm, theta) * (1.0 - math.exp(-t_s / tau(D_nm, T_C, tau0)))


def diffusion_checks():
    """Pre-registered consistency checks 3.4 against DM2023 pad-into-cavity timing."""
    rows = []
    for tau0 in (TAU0_RANGE[0], 60.0, TAU0_RANGE[1]):
        tc_300 = 3 * tau(300, 350, tau0)
        f230 = 1 - math.exp(-7200 / tau(300, 230, tau0))
        rows.append(dict(tau0_s=tau0, t_complete_300nm_350C_s=tc_300, within_5min=tc_300 <= 300,
                         completion_230C_2h=f230, DM2023_ratio_230_350=12 / 28))
    json.dump(rows, open(OUT / "diffusion_checks.json", "w"), indent=1)
    return rows


# ---------------------------------------------------------------- elastic u model from FEM runs: u(Ez, T)
def ez_random(n, rng):
    v = rng.normal(size=(n, 3)); v /= np.linalg.norm(v, axis=1)[:, None]
    l, m, nn = np.abs(v).T
    c11, c12, c44 = S.C11, S.C12, S.C44
    den = (c11 - c12) * (c11 + 2 * c12)
    s11, s12, s44 = (c11 + c12) / den, -c12 / den, 1 / c44
    g = l * l * m * m + m * m * nn * nn + nn * nn * l * l
    return 1.0 / (s11 - 2 * (s11 - s12 - s44 / 2) * g) / 1000.0


def u_model_from_runs(run_ids, key="du_c50"):
    """Fit u(T) = k(Ez) * (T - 25) with k quadratic in Ez from anisotropic runs (elastic: u linear in T)."""
    pts = []
    for rid in run_ids:
        r = B.load(rid)
        if r is None:
            continue
        res = r["result"]
        Ts = np.array([h["T"] for h in res["hist"]]); us = np.array([h["d" + key[2:]] for h in res["hist"]])
        k = float(np.polyfit(Ts - 25.0, us, 1)[0])            # nm/K
        pts.append((res["Ez"], k, rid))
    pts.sort()
    ez = np.array([p[0] for p in pts]); k = np.array([p[1] for p in pts])
    deg = 2 if len(pts) >= 4 else (1 if len(pts) >= 2 else 0)
    coef = np.polyfit(ez, k, deg)
    return dict(coef=coef.tolist(), points=[dict(Ez=float(e), k_nm_per_K=float(kk), run=rid) for e, kk, rid in pts], deg=deg)


def predict(size_um, runs_aniso, run_hill, n=200_000, seed=0, label=""):
    """Process window for one pad size: P(contact) over orientation x recess for T, t and interface states."""
    rng = np.random.default_rng(seed)
    fit = u_model_from_runs(runs_aniso)
    coef = np.array(fit["coef"])
    rh = B.load(run_hill)
    k_hill = None
    if rh:
        res = rh["result"]; Ts = np.array([h["T"] for h in res["hist"]]); us = np.array([h["du_c50"] for h in res["hist"]])
        k_hill = float(np.polyfit(Ts - 25.0, us, 1)[0])
    ez1, ez2 = ez_random(n, rng), ez_random(n, rng)
    k1, k2 = np.polyval(coef, ez1), np.polyval(coef, ez2)
    D_nm = size_um * 1000.0
    rows = []
    recess_mu, recess_sd = 2.5, 0.5                      # IRPS 2026 Fig 6 (per pad, nm)
    for sidewall in ("bonded",):
        for surf, sox in (("clean", 1.0), ("oxidised", 0.45)):
            for T in (200, 250, 300, 350, 400):
                for t_min in (5, 30, 120):
                    for theta in (107.0, 123.0, 149.0):
                        hd = h_d(t_min * 60.0, T, D_nm, theta, 60.0, sox)
                        hd_lo = h_d(t_min * 60.0, T, D_nm, theta, TAU0_RANGE[1], sox)
                        hd_hi = h_d(t_min * 60.0, T, D_nm, theta, TAU0_RANGE[0], sox)
                        u_el = (k1 + k2) * (T - 25.0)
                        for g_mean in (None, 2.0, 4.0, 6.0, 8.0):
                            if g_mean is None:
                                g = rng.normal(recess_mu, recess_sd, n) + rng.normal(recess_mu, recess_sd, n)
                                gl = "IRPS N(2.5,0.5)x2"
                            else:
                                g = np.full(n, g_mean); gl = f"{g_mean:g}"
                            P = float(np.mean(u_el + 2 * hd >= g))
                            P_el = float(np.mean(u_el >= g))
                            P_lo = float(np.mean(u_el + 2 * hd_lo >= g))
                            P_hi = float(np.mean(u_el + 2 * hd_hi >= g))
                            rows.append(dict(size_um=size_um, sidewall=sidewall, surface=surf, T_C=T, t_min=t_min, theta=theta,
                                             recess_sum=gl, h_d_per_pad_nm=hd, u_el_mean_nm=float(u_el.mean()),
                                             u_el_p1_nm=float(np.quantile(u_el, 0.01)), P_contact=P, P_elastic_only=P_el,
                                             P_tau0_100=P_lo, P_tau0_20=P_hi))
    keys = list(rows[0])
    (OUT / f"predict_{label or size_um}.csv").write_text(",".join(keys) + "\n" + "".join(
        ",".join(f"{r[k]:.4g}" if isinstance(r[k], float) else str(r[k]) for k in keys) + "\n" for r in rows))
    json.dump(dict(size_um=size_um, fit=fit, k_hill=k_hill), open(OUT / f"predict_{label or size_um}_fit.json", "w"), indent=1)
    return rows, fit


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200_000)
    a = ap.parse_args(argv)
    print(json.dumps(diffusion_checks(), indent=1))
    cfg = json.loads((OUT / "predict_config.json").read_text())
    for c in cfg:
        rows, fit = predict(c["size_um"], c["aniso_runs"], c["hill_run"], a.n, label=c["label"])
        print(c["label"], "fit", fit["points"], "rows", len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
