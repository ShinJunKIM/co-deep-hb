r"""Stage 2 B: orientation-dependent surface-diffusion amplitude (exploratory round 2; docs/stage2_orient_diffusion_round2.md).

h_d(omega) = s_ox * 0.0022 * (theta_eff - 90) * D * f(omega) * (1 - exp(-t/tau(D, T))),  f = clip((omega - omega_c)/d_omega, 0, 1),
omega = angle between the pad normal and the nearest <111> direction (uniform orientation on the sphere).
Calibration (500 nm pitch, D 300, 350 C 1 h): theta_eff, omega_c, d_omega from the measured quantiles q10..q90.
Validation (no retuning, data already seen -> "exploratory round 2"): medians and IQRs of the other 17 std-Cu points.
Usage: python src\stage2\stage2_orient_diffusion.py [--n 200000]
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
sys.path.insert(0, str(HERE))
import stage2_predict as P  # noqa: E402
import stage2_diffusion_val as V  # noqa: E402

REPO = HERE.parents[1]
OUT = REPO / "results" / "stage2"
FIG = REPO / "results" / "figures"
TAU0, Q = 60.0, 20.7
QS = (0.10, 0.25, 0.50, 0.75, 0.90)
V111 = np.array([[1, 1, 1], [1, 1, -1], [1, -1, 1], [-1, 1, 1]], float) / math.sqrt(3)


def omega_random(n, rng):
    v = rng.normal(size=(n, 3)); v /= np.linalg.norm(v, axis=1)[:, None]
    c = np.abs(v @ V111.T).max(axis=1)
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def f_of(omega, omega_c, d_omega):
    if d_omega <= 1e-9:
        return (omega > omega_c).astype(float)
    return np.clip((omega - omega_c) / d_omega, 0.0, 1.0)


def kin(D_nm, T_C, t_h):
    ds = math.exp(-Q / P.R_GAS * (1 / (T_C + 273.15) - 1 / 623.15))
    tau = TAU0 * (D_nm / 200.0) ** 3.7 / ds
    return 1.0 - math.exp(-t_h * 3600.0 / tau)


def h_samples(omega, theta, oc, dw, D_nm, T_C, t_h, s_ox=1.0):
    return s_ox * 0.0022 * (theta - 90.0) * D_nm * f_of(omega, oc, dw) * kin(D_nm, T_C, t_h)


def quantiles(x):
    return np.quantile(x, QS)


def calibrate(omega, meas_q, D_nm, T_C, t_h):
    best = None
    for theta in np.arange(100.0, 160.1, 1.0):
        for oc in np.arange(5.0, 20.1, 1.0):
            for dw in np.arange(0.0, 30.1, 2.0):
                q = quantiles(h_samples(omega, theta, oc, dw, D_nm, T_C, t_h))
                sse = float(np.sum((q - meas_q) ** 2))
                if best is None or sse < best[0]:
                    best = (sse, theta, oc, dw)
    sse, theta, oc, dw = best
    # local refinement
    for theta2 in np.arange(theta - 1, theta + 1.01, 0.25):
        for oc2 in np.arange(oc - 1, oc + 1.01, 0.25):
            for dw2 in np.arange(max(0, dw - 2), dw + 2.01, 0.5):
                q = quantiles(h_samples(omega, theta2, oc2, dw2, D_nm, T_C, t_h))
                s = float(np.sum((q - meas_q) ** 2))
                if s < sse:
                    sse, theta, oc, dw = s, theta2, oc2, dw2
    return dict(theta_eff=float(theta), omega_c=float(oc), d_omega=float(dw), rms_nm=math.sqrt(sse / len(QS)))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200_000)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    rng = np.random.default_rng(a.seed)
    omega = omega_random(a.n, rng)
    data = json.loads((REPO / "inputs" / "dm2026_digitized.json").read_text(encoding="utf-8"))
    pts = [p for p in data["points"] if p["cu"] == "std" and p["role"] in ("calibration", "held-out")]
    for p in pts:   # sanitize quantiles (hidden curve segments -> nan)
        for k in ("q10", "q25", "q75", "q90"):
            v = p.get(k)
            if v is None or not np.isfinite(v) or (k in ("q10", "q25") and v > p["median_nm"]) or (k in ("q75", "q90") and v < p["median_nm"]):
                p[k] = float("nan")
    cal = next(p for p in pts if p["pitch_nm"] == 500 and p["T_C"] == 350 and p["figure"] == "Fig.3")
    meas_q = np.array([cal["q10"], cal["q25"], cal["median_nm"], cal["q75"], cal["q90"]])
    fit = calibrate(omega, meas_q, cal["D_nm"], cal["T_C"], cal["t_h"])
    th, oc, dw = fit["theta_eff"], fit["omega_c"], fit["d_omega"]
    lag_frac = float(np.mean(f_of(omega, oc, dw) == 0.0))
    print(f"calibration (500 nm, 350 C 1 h): theta_eff {th:.2f} deg, omega_c {oc:.2f} deg, d_omega {dw:.2f} deg, rms {fit['rms_nm']:.2f} nm; "
          f"faceted fraction f=0: {lag_frac:.3f} (DM2026 Fig.5a lagging tail ~0.10)")
    rows = []
    for p in pts:
        h = h_samples(omega, th, oc, dw, p["D_nm"], p["T_C"], p["t_h"])
        q = quantiles(h)
        tol_m = max(1.5, 0.25 * p["median_nm"], p["err_nm"])
        iqr_m = p["q75"] - p["q25"]; iqr_p = q[3] - q[1]
        tol_i = max(1.5, 0.5 * iqr_m) if np.isfinite(iqr_m) else float("nan")
        rows.append(dict(figure=p["figure"], pitch_nm=p["pitch_nm"], D_nm=p["D_nm"], history=p["history"], T_C=p["T_C"], t_h=p["t_h"],
                         role=("calibration" if p is cal else "validation (exploratory round 2)"),
                         meas_q10=p["q10"], meas_q25=p["q25"], meas_median=p["median_nm"], meas_q75=p["q75"], meas_q90=p["q90"],
                         pred_q10=q[0], pred_q25=q[1], pred_median=q[2], pred_q75=q[3], pred_q90=q[4],
                         pred_median_no_orient=float(s := 0.0022 * (th - 90) * p["D_nm"] * kin(p["D_nm"], p["T_C"], p["t_h"])),
                         tol_median=tol_m, pass_median=bool(abs(q[2] - p["median_nm"]) <= tol_m),
                         meas_iqr=iqr_m, pred_iqr=iqr_p, tol_iqr=tol_i,
                         pass_iqr=(bool(abs(iqr_p - iqr_m) <= tol_i) if np.isfinite(iqr_m) else None)))
    val = [r for r in rows if r["role"].startswith("validation")]
    n_med = sum(r["pass_median"] for r in val); n_iqr = sum(1 for r in val if r["pass_iqr"]); n_iqr_tot = sum(1 for r in val if r["pass_iqr"] is not None)
    # trend tests (Phase 3 definitions) on medians
    for r in rows:
        r["pred_nm"] = r["pred_median"]; r["median_nm"] = r["meas_median"]; r["cu"] = "std"; r["err_nm"] = 0.5
    tr = V.trends(rows)
    frac = n_med / len(val)
    verdict = ("consistent (exploratory round 2)" if (frac >= 0.8 and tr["T_trend_ok"] and tr["saturation_ok"]) else "inconsistent (exploratory round 2)")
    # 200 C under-prediction check and exploratory Q_eff from the 200 C 2h/4h pairs
    q_eff = {}
    for pitch in (400, 500):
        a2 = next(r for r in rows if r["figure"] == "Fig.3" and r["pitch_nm"] == pitch and r["T_C"] == 200 and r["t_h"] == 2)
        a4 = next(r for r in rows if r["figure"] == "Fig.3" and r["pitch_nm"] == pitch and r["T_C"] == 200 and r["t_h"] == 4)
        a35 = next(r for r in rows if r["figure"] == "Fig.3" and r["pitch_nm"] == pitch and r["T_C"] == 350)
        hinf = a35["meas_median"]                      # saturated amplitude (350 C, no T-dependence of amplitude assumed)
        # kinetics: m2 = hinf(1-e^{-2/tau}), m4 = hinf(1-e^{-4/tau}) -> solve tau (h) from the ratio
        r24 = a4["meas_median"] / a2["meas_median"]
        best = None
        for tau_h in np.logspace(-1, 2, 3001):
            rr = (1 - math.exp(-4 / tau_h)) / (1 - math.exp(-2 / tau_h))
            if best is None or abs(rr - r24) < best[0]:
                best = (abs(rr - r24), tau_h)
        tau200 = best[1] * 3600.0
        tau350_model = TAU0 * (a2["D_nm"] / 200.0) ** 3.7
        Q_eff = P.R_GAS * math.log(tau200 / tau350_model) / (1 / 473.15 - 1 / 623.15)
        q_eff[str(pitch)] = dict(ratio_4h_over_2h=r24, tau_200C_h=tau200 / 3600, tau_350C_model_s=tau350_model, Q_eff_kcal=Q_eff,
                                 amplitude_from_200C=a2["meas_median"] / (1 - math.exp(-7200 / tau200)), amplitude_350C_meas=hinf)
    # orientation coupling at 0.54 and 0.30 um, 350 C 1 h: elastic spread vs diffusion spread
    coupling = {}
    for label, size in (("0.54um", 0.54), ("0.30um", 0.30)):
        f = json.loads((OUT / f"predict_{label}_fit.json").read_text())["fit"]
        coef = np.array(f["coef"])
        v = rng.normal(size=(a.n, 3)); v /= np.linalg.norm(v, axis=1)[:, None]
        l, m, nn = np.abs(v).T
        c11, c12, c44 = 168400.0, 121400.0, 75400.0
        den = (c11 - c12) * (c11 + 2 * c12); s11, s12, s44 = (c11 + c12) / den, -c12 / den, 1 / c44
        ez = 1.0 / (s11 - 2 * (s11 - s12 - s44 / 2) * (l * l * m * m + m * m * nn * nn + nn * nn * l * l)) / 1000.0
        om = np.degrees(np.arccos(np.clip(np.abs(v @ V111.T).max(axis=1), -1, 1)))
        u_el = 0.69 * np.polyval(coef, ez) * (350 - 25)
        h_d = h_samples(om, th, oc, dw, size * 1000, 350, 1)
        tot = u_el + h_d
        w = lambda x: float(np.quantile(x, 0.9) - np.quantile(x, 0.1))
        coupling[label] = dict(u_el_median=float(np.median(u_el)), u_el_width_q90_q10=w(u_el), h_d_median=float(np.median(h_d)),
                               h_d_width_q90_q10=w(h_d), total_median=float(np.median(tot)), total_width_q90_q10=w(tot),
                               dominant="diffusion" if w(h_d) > w(u_el) else "elastic")
    res = dict(status="exploratory round 2", fit=fit, faceted_fraction=lag_frac, rows=rows, n_validation=len(val), n_pass_median=n_med,
               frac_pass_median=frac, n_pass_iqr=n_iqr, n_iqr_total=n_iqr_tot, trends=tr, verdict=verdict,
               under_prediction_200C=[dict(pitch=r["pitch_nm"], T_C=r["T_C"], t_h=r["t_h"], history=r["history"], meas=r["meas_median"], pred=r["pred_median"])
                                      for r in val if r["T_C"] == 200 and r["D_nm"] >= 250],
               Q_eff_exploratory=q_eff, orientation_coupling_350C_1h=coupling)
    json.dump(res, open(OUT / "orient_diffusion_round2.json", "w"), indent=1, default=float)
    keys = ["figure", "pitch_nm", "D_nm", "history", "T_C", "t_h", "role", "meas_q10", "meas_q25", "meas_median", "meas_q75", "meas_q90",
            "pred_q10", "pred_q25", "pred_median", "pred_q75", "pred_q90", "pred_median_no_orient", "tol_median", "pass_median", "meas_iqr", "pred_iqr", "pass_iqr"]
    (OUT / "orient_diffusion_round2.csv").write_text(",".join(keys) + "\n" + "".join(
        ",".join(f"{r[k]:.3g}" if isinstance(r[k], float) else str(r[k]) for k in keys) + "\n" for r in rows), encoding="utf-8")
    for r in rows:
        print(f"  {r['role'][:11]:11s} {r['figure']:6s} p{r['pitch_nm']:3d} {r['T_C']:3.0f}C {r['t_h']:g}h {r['history'][:6]:6s} med {r['meas_median']:5.2f} -> {r['pred_median']:5.2f} "
              f"{'ok' if r['pass_median'] else 'FAIL'} | IQR {r['meas_iqr']:4.1f} -> {r['pred_iqr']:4.1f} {('ok' if r['pass_iqr'] else 'FAIL') if r['pass_iqr'] is not None else 'n/a'}")
    print(f"validation medians {n_med}/{len(val)} = {frac:.0%}; IQR {n_iqr}/{n_iqr_tot}; T trend {tr['T_trend_ok']}; saturation {tr['saturation_ok']} -> {verdict}")
    print("Q_eff exploratory:", {k: round(v["Q_eff_kcal"], 1) for k, v in q_eff.items()}, "tau(200C) h:", {k: round(v["tau_200C_h"], 2) for k, v in q_eff.items()})
    print("orientation coupling:", json.dumps(coupling, indent=0, default=float)[:600])
    # figure: diffusion fit by T / size / orientation
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        fig, axs = plt.subplots(1, 3, figsize=(10, 3))
        for pitch, mk in ((400, "o"), (500, "s")):
            rr = sorted([r for r in rows if r["figure"] == "Fig.3" and r["pitch_nm"] == pitch], key=lambda r: (r["T_C"], r["t_h"]))
            x = [f"{r['T_C']:.0f}/{r['t_h']:g}h" for r in rr]
            axs[0].errorbar(range(len(rr)), [r["meas_median"] for r in rr], yerr=[[r["meas_median"] - r["meas_q25"] for r in rr], [r["meas_q75"] - r["meas_median"] for r in rr]],
                            fmt=mk, ms=4, capsize=2, label=f"meas {pitch} nm pitch")
            axs[0].plot(range(len(rr)), [r["pred_median"] for r in rr], "-", lw=1, label=f"model {pitch}")
            axs[0].set_xticks(range(len(rr))); axs[0].set_xticklabels(x, rotation=45, fontsize=6)
        axs[0].set_ylabel("Δh_max median (IQR) nm"); axs[0].set_title("T / time (Fig. 3, PPA Cu)", fontsize=8); axs[0].legend(fontsize=6, frameon=False)
        for T, mk in ((250, "o"), (200, "s")):
            rr = sorted([r for r in rows if r["history"] == "self-anneal" and r["T_C"] == T], key=lambda r: r["D_nm"])
            axs[1].errorbar([r["D_nm"] for r in rr], [r["meas_median"] for r in rr], yerr=[[r["meas_median"] - r["meas_q25"] for r in rr], [r["meas_q75"] - r["meas_median"] for r in rr]],
                            fmt=mk, ms=4, capsize=2, label=f"meas {T} °C 1 h")
            axs[1].plot([r["D_nm"] for r in rr], [r["pred_median"] for r in rr], "-", lw=1, label=f"model {T} °C")
        axs[1].set_xlabel("bottom pad D (nm)"); axs[1].set_title("size (self-annealed Cu)", fontsize=8); axs[1].legend(fontsize=6, frameon=False)
        om = np.linspace(0, 54.7, 200)
        axs[2].plot(om, f_of(om, oc, dw), "k-"); axs[2].set_xlabel("ω to nearest <111> (deg)"); axs[2].set_ylabel("f(ω)")
        axs[2].set_title(f"orientation factor: ω_c {oc:.1f}°, Δω {dw:.1f}°, faceted {lag_frac:.0%}", fontsize=8)
        fig.suptitle("exploratory round 2: orientation-dependent diffusion amplitude (θ_eff %.1f°, τ₀ 60 s, Q 20.7)" % th, fontsize=8)
        fig.tight_layout(); fig.savefig(FIG / "s2_diffusion_fit.png", dpi=300); plt.close(fig)
    except Exception as exc:
        print("figure skipped:", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
