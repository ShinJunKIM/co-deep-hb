r"""EXPLORATORY (agent fork, 2026-10-16): candidate surface-diffusion kinetics forms compared on the DM2026 held-out set.
Nothing here is a validation result; all 17 held-out points were already seen in Phase 3.  Each candidate has ONE calibrated
parameter (the amplitude at the 400 nm pitch / 350 C / 1 h point); every other constant is fixed a priori from literature.

Candidates
  R1  revision 1 form: g = 1 - exp(-t/tau), Q = 20.7 kcal/mol (Bonzel-Gjostein range 17-22, Butrymowicz 1973 p.8), tau0 = 60 s
  C1  same kinetics, Q = 13 kcal/mol (Melmed et al., field-emission, 50-171 C; Butrymowicz p.9 -- the only low-T Cu surface value)
  C2  Mullins-type stretched kinetics g = 1 - exp(-(t/tau)^beta), beta = 1/4 (surface-diffusion length ~ (B t)^1/4), Q = 20.7
  C2b same with beta = 1/2 (sensitivity)
  C3  beta = 1/4 and Q = 13 (both literature-fixed)
tau = tau0 (D/200 nm)^3.7 Ds(350)/Ds(T) in all cases (DM2024 D^3.7; the exponent 3.7 ~ 4 is itself the Mullins scaling).
Usage: python src\agents\diffusion_round3.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "src" / "stage2"))
import stage2_diffusion_val as V  # noqa: E402
import stage2_orient_diffusion as O  # noqa: E402

R_GAS = 1.987e-3
OUT = REPO / "docs" / "agents"
CANDS = {
    "R1 exp, Q20.7": dict(beta=1.0, Q=20.7),
    "C1 exp, Q13": dict(beta=1.0, Q=13.0),
    "C2 beta1/4, Q20.7": dict(beta=0.25, Q=20.7),
    "C2b beta1/2, Q20.7": dict(beta=0.5, Q=20.7),
    "C3 beta1/4, Q13": dict(beta=0.25, Q=13.0),
}
TAU0 = 60.0
OMEGA_C, D_OMEGA = 5.0, 19.5     # round-2 shape, fixed


def g_of(t_s, D_nm, T_C, beta, Q, tau0=TAU0):
    ds = math.exp(-Q / R_GAS * (1 / (T_C + 273.15) - 1 / 623.15))
    tau = tau0 * (D_nm / 200.0) ** 3.7 / ds
    return 1.0 - math.exp(-(t_s / tau) ** beta)


def load_points():
    data = json.loads((REPO / "inputs" / "dm2026_digitized.json").read_text(encoding="utf-8"))
    pts = [p for p in data["points"] if p["cu"] == "std" and p["role"] in ("calibration", "held-out")]
    for p in pts:
        for k in ("q10", "q25", "q75", "q90"):
            v = p.get(k)
            if v is None or not np.isfinite(v) or (k in ("q10", "q25") and v > p["median_nm"]) or (k in ("q75", "q90") and v < p["median_nm"]):
                p[k] = float("nan")
    return pts


def evaluate(pts, cal, beta, Q, omega, verbose=False):
    f = O.f_of(omega, OMEGA_C, D_OMEGA); fmed = float(np.median(f))
    g_cal = g_of(cal["t_h"] * 3600, cal["D_nm"], cal["T_C"], beta, Q)
    A = cal["median_nm"] / (fmed * cal["D_nm"] * g_cal)          # amplitude per nm of D (= 0.0022*(theta_eff-90))
    theta_eff = 90 + A / 0.0022
    rows = []
    for p in pts:
        g = g_of(p["t_h"] * 3600, p["D_nm"], p["T_C"], beta, Q)
        h = A * p["D_nm"] * g * f
        q25, med, q75 = np.quantile(h, [0.25, 0.5, 0.75])
        tol = max(1.5, 0.25 * p["median_nm"], p["err_nm"])
        iqr_m = p["q75"] - p["q25"]
        rows.append(dict(p, pred_nm=float(med), tol=tol, passed=bool(abs(med - p["median_nm"]) <= tol),
                         pred_iqr=float(q75 - q25), meas_iqr=float(iqr_m),
                         pass_iqr=(bool(abs((q75 - q25) - iqr_m) <= max(1.5, 0.5 * iqr_m)) if np.isfinite(iqr_m) else None),
                         is_cal=(p is cal)))
    held = [r for r in rows if not r["is_cal"]]
    tr = V.trends(rows)
    n_pass = sum(r["passed"] for r in held); n_iqr = sum(1 for r in held if r["pass_iqr"]); n_iqr_t = sum(1 for r in held if r["pass_iqr"] is not None)
    # diagnostics on the measured facts (held-out, report only): 200 C 4h/2h ratio and 200 C size slope (self-annealed, 1 h)
    diag = {}
    for pitch in (400, 500):
        a2 = next(r for r in rows if r["figure"] == "Fig.3" and r["pitch_nm"] == pitch and r["T_C"] == 200 and r["t_h"] == 2)
        a4 = next(r for r in rows if r["figure"] == "Fig.3" and r["pitch_nm"] == pitch and r["T_C"] == 200 and r["t_h"] == 4)
        diag[f"ratio_4h_2h_{pitch}"] = dict(meas=a4["median_nm"] / a2["median_nm"], pred=a4["pred_nm"] / a2["pred_nm"])
    s200 = sorted([r for r in rows if r["history"] == "self-anneal" and r["T_C"] == 200], key=lambda r: r["D_nm"])
    if len(s200) >= 3:
        D = np.array([r["D_nm"] for r in s200]); diag["slope_200C_1h_nm_per_nm"] = dict(
            meas=float(np.polyfit(D, [r["median_nm"] for r in s200], 1)[0]), pred=float(np.polyfit(D, [r["pred_nm"] for r in s200], 1)[0]))
    return dict(theta_eff=theta_eff, A=A, n_pass=n_pass, n_held=len(held), frac=n_pass / len(held), n_iqr=n_iqr, n_iqr_t=n_iqr_t,
                T_trend=tr["T_trend_ok"], saturation=tr["saturation_ok"],
                sat=[(s["D_nm"], round(s["R_meas"], 2), round(s["dR"], 2), round(s["R_pred"], 2)) for s in tr["saturation"]],
                verdict_by_rule=("would pass" if (n_pass / len(held) >= 0.8 and tr["T_trend_ok"] and tr["saturation_ok"]) else "fails rule"),
                diag=diag, rows=rows)


def main():
    rng = np.random.default_rng(0); omega = O.omega_random(200_000, rng)
    pts = load_points()
    cal = next(p for p in pts if p["role"] == "calibration")
    results = {}
    print("EXPLORATORY comparison (calibration = 400 nm pitch, 350 C 1 h only; 17 held-out std-Cu points already seen in Phase 3)")
    print(f"{'candidate':22s} {'theta_eff':>9s} {'medians':>8s} {'IQR':>6s} {'Ttrend':>6s} {'sat':>5s}  sat ratios (D, meas±dR, pred)      4h/2h meas->pred (400/500)   200C size slope meas->pred")
    for name, c in CANDS.items():
        r = evaluate(pts, cal, c["beta"], c["Q"], omega)
        results[name] = {k: v for k, v in r.items() if k != "rows"}
        results[name]["rows"] = [{k: v for k, v in row.items() if k in ("figure", "pitch_nm", "D_nm", "history", "T_C", "t_h", "median_nm", "pred_nm", "tol", "passed", "meas_iqr", "pred_iqr", "pass_iqr")} for row in r["rows"]]
        d = r["diag"]
        print(f"{name:22s} {r['theta_eff']:9.1f} {r['n_pass']:5d}/{r['n_held']:<2d} {r['n_iqr']:3d}/{r['n_iqr_t']:<2d} {str(r['T_trend']):>6s} {str(r['saturation']):>5s}  "
              f"{[(s[0], f'{s[1]}±{s[2]}', s[3]) for s in r['sat'][:2]]}  "
              f"{d['ratio_4h_2h_400']['meas']:.2f}->{d['ratio_4h_2h_400']['pred']:.2f} / {d['ratio_4h_2h_500']['meas']:.2f}->{d['ratio_4h_2h_500']['pred']:.2f}   "
              f"{d.get('slope_200C_1h_nm_per_nm', {}).get('meas', float('nan')):+.4f}->{d.get('slope_200C_1h_nm_per_nm', {}).get('pred', float('nan')):+.4f}")
    # per-point table for R1 and the best candidate by medians
    best = max(CANDS, key=lambda n: (results[n]["n_pass"], results[n]["n_iqr"]))
    print(f"\nbest by medians: {best}\nper-point (meas -> R1 | best):")
    for a, b in zip(results["R1 exp, Q20.7"]["rows"], results[best]["rows"]):
        print(f"  {a['figure']:6s} p{a['pitch_nm']:3d} {a['T_C']:3.0f}C {a['t_h']:g}h {a['history'][:4]:4s} meas {a['median_nm']:5.2f} -> {a['pred_nm']:5.2f} {'ok' if a['passed'] else 'x '} | "
              f"{b['pred_nm']:5.2f} {'ok' if b['passed'] else 'x '}   IQR {a['meas_iqr']:4.1f} -> {a['pred_iqr']:4.1f} | {b['pred_iqr']:4.1f}")
    # leave-one-condition-out: recalibrate on each PPA-Cu Fig.3 point, evaluate the others
    loco = {}
    for name in ("R1 exp, Q20.7", best):
        c = CANDS[name]; fr = []
        for calp in [p for p in pts if p["figure"] == "Fig.3"]:
            r = evaluate(pts, calp, c["beta"], c["Q"], omega)
            fr.append((f"{calp['pitch_nm']}/{calp['T_C']}C/{calp['t_h']}h", r["frac"], r["theta_eff"], r["saturation"]))
        loco[name] = fr
        fracs = [x[1] for x in fr]
        print(f"\nLOCO {name}: held-out pass fraction over 10 calibration choices: min {min(fracs):.2f} median {np.median(fracs):.2f} max {max(fracs):.2f}")
        for x in fr: print(f"   cal {x[0]:16s} pass {x[1]:.2f} theta_eff {x[2]:6.1f} sat {x[3]}")
    json.dump(dict(status="EXPLORATORY (agent fork); not a validation", candidates=results, best_by_medians=best, loco=loco,
                   omega_shape=dict(omega_c=OMEGA_C, d_omega=D_OMEGA), tau0=TAU0),
              open(OUT / "diffusion_round3_results.json", "w"), indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
