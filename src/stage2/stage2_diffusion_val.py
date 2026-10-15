r"""Stage 2 Phase 3: surface-diffusion term validation against DM2026 (docs/stage2_diffusion_preregistration.md).

Model (fixed form, stage2_predict): h_d = s_ox*0.0022*(theta-90)*D*(1-exp(-t/tau)), tau = tau0*(D/200)^3.7*Ds(350)/Ds(T).
Calibration: 400 nm pitch (D = 250 nm bottom pad), 350 C, all anneal times there -> tau0 only (theta fixed 123 deg,
one anneal time at that point; see pre-registration 4.1).  Held-out: every other pitch x T x time std-Cu point.
Pass per point: |pred - median| <= max(1.5 nm, 25 % of median, digitization error).  VALIDATED = >= 80 % pass AND T trend
AND saturation.  fg-Cu excluded (reported separately).
Usage: python src\stage2\stage2_diffusion_val.py [--theta 123] [--Q 20.7] [--tag ""] [--data inputs/dm2026_digitized.json]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stage2_predict as P  # noqa: E402

REPO = HERE.parents[1]
OUT = REPO / "results" / "stage2"


def h_model(t_s, T_C, D_nm, tau0, theta, Q):
    ds = math.exp(-Q / P.R_GAS * (1 / (T_C + 273.15) - 1 / (350.0 + 273.15)))
    tau = tau0 * (D_nm / 200.0) ** 3.7 / ds
    return 0.0022 * (theta - 90.0) * D_nm * (1.0 - math.exp(-t_s / tau))


def calibrate(cal_pts, theta, Q):
    grid = np.logspace(0, 5, 2001)
    def sse(t0):
        return sum((h_model(p["t_h"] * 3600, p["T_C"], p["D_nm"], t0, theta, Q) - p["median_nm"]) ** 2 for p in cal_pts)
    s = np.array([sse(t) for t in grid]); i = int(np.argmin(s))
    lo, hi = grid[max(0, i - 2)], grid[min(len(grid) - 1, i + 2)]
    fine = np.linspace(lo, hi, 401); sf = np.array([sse(t) for t in fine]); j = int(np.argmin(sf))
    # identifiability: tau0 range within which the calibration residual stays below the digitization error
    tol = max(p["err_nm"] for p in cal_pts)
    ok = grid[np.sqrt(s / len(cal_pts)) <= tol]
    return float(fine[j]), float(math.sqrt(sf[j] / len(cal_pts))), (float(ok.min()), float(ok.max())) if len(ok) else None


def evaluate(data, tau0, theta, Q):
    rows = []
    for p in data["points"]:
        pred = h_model(p["t_h"] * 3600, p["T_C"], p["D_nm"], tau0, theta, Q)
        tol = max(1.5, 0.25 * p["median_nm"], p["err_nm"])
        rows.append(dict(p, pred_nm=pred, tol_nm=tol, diff_nm=pred - p["median_nm"],
                         passed=bool(abs(pred - p["median_nm"]) <= tol)))
    return rows


def trends(rows):
    std = [r for r in rows if r["cu"] == "std"]
    key = lambda r: (r["D_nm"], r["t_h"], r["history"])
    # T trend: pairs with the same (D, t, history) where the measured median rises with T -> prediction must rise too
    t_pairs = []
    for a in std:
        for b in std:
            if key(a) == key(b) and b["T_C"] > a["T_C"] and b["median_nm"] > a["median_nm"]:
                t_pairs.append(dict(D_nm=a["D_nm"], t_h=a["t_h"], T_lo=a["T_C"], T_hi=b["T_C"], meas_rise=b["median_nm"] - a["median_nm"],
                                    pred_rise=b["pred_nm"] - a["pred_nm"], ok=bool(b["pred_nm"] > a["pred_nm"])))
    t_ok = all(p["ok"] for p in t_pairs) if t_pairs else None
    # saturation: measured h(450)/h(350) at the same D, t, history; predicted ratio within +/- combined uncertainty
    sat = []
    for a in std:
        for b in std:
            if key(a) == key(b) and a["T_C"] == 350 and b["T_C"] == 450:
                Rm = b["median_nm"] / a["median_nm"]
                dR = Rm * math.sqrt((b["err_nm"] / b["median_nm"]) ** 2 + (a["err_nm"] / a["median_nm"]) ** 2)
                Rp = b["pred_nm"] / a["pred_nm"] if a["pred_nm"] > 0 else float("inf")
                sat.append(dict(D_nm=a["D_nm"], t_h=a["t_h"], R_meas=Rm, dR=dR, R_pred=Rp, ok=bool(abs(Rp - Rm) <= dR)))
    s_ok = all(s["ok"] for s in sat) if sat else None
    # size scaling (report): fixed (T, t, history), median vs D linear fit
    size = []
    groups = {}
    for r in std:
        groups.setdefault((r["T_C"], r["t_h"], r["history"]), []).append(r)
    for (T, t, hist), g in groups.items():
        if len(g) >= 3:
            D = np.array([r["D_nm"] for r in g]); m = np.array([r["median_nm"] for r in g]); pr = np.array([r["pred_nm"] for r in g])
            km, bm = np.polyfit(D, m, 1); kp, bp = np.polyfit(D, pr, 1)
            size.append(dict(T_C=T, t_h=t, history=hist, n=len(g), meas_slope_nm_per_nm=km, meas_intercept_nm=bm,
                             pred_slope_nm_per_nm=kp, pred_intercept_nm=bp))
    return dict(T_trend_pairs=t_pairs, T_trend_ok=t_ok, saturation=sat, saturation_ok=s_ok, size_scaling=size)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(REPO / "inputs" / "dm2026_digitized.json"))
    ap.add_argument("--theta", type=float, default=123.0)
    ap.add_argument("--Q", type=float, default=20.7)
    ap.add_argument("--tag", default="")
    a = ap.parse_args(argv)
    data = json.loads(Path(a.data).read_text(encoding="utf-8"))
    cal = [p for p in data["points"] if p["role"] == "calibration"]
    tau0, rms, ident = calibrate(cal, a.theta, a.Q)
    rows = evaluate(data, tau0, a.theta, a.Q)
    held = [r for r in rows if r["role"] == "held-out" and r["cu"] == "std"]
    n_pass = sum(r["passed"] for r in held)
    tr = trends(rows)
    frac = n_pass / len(held) if held else float("nan")
    verdict = "VALIDATED" if (frac >= 0.8 and tr["T_trend_ok"] and tr["saturation_ok"]) else "NOT VALIDATED"
    res = dict(settings=dict(theta=a.theta, Q_kcal=a.Q, data=str(a.data)), tau0_s=tau0, calibration_rms_nm=rms,
               tau0_identifiable_range_s=ident, calibration_points=[r for r in rows if r["role"] == "calibration"],
               held_out=held, n_held=len(held), n_pass=n_pass, frac_pass=frac, trends=tr, verdict=verdict,
               fg_cu=[r for r in rows if r["cu"] == "fg"])
    tag = f"_{a.tag}" if a.tag else ""
    json.dump(res, open(OUT / f"diffusion_validation{tag}.json", "w"), indent=1, default=float)
    lines = ["figure,pitch_nm,D_nm,cu,history,T_C,t_h,median_nm,err_nm,q25,q75,role,pred_nm,tol_nm,diff_nm,pass"]
    for r in rows:
        lines.append(f"{r['figure']},{r['pitch_nm']},{r['D_nm']},{r['cu']},{r['history']},{r['T_C']},{r['t_h']},{r['median_nm']:.2f},"
                     f"{r['err_nm']:.2f},{r.get('q25', float('nan')):.2f},{r.get('q75', float('nan')):.2f},{r['role']},{r['pred_nm']:.2f},"
                     f"{r['tol_nm']:.2f},{r['diff_nm']:+.2f},{r['passed']}")
    (OUT / f"diffusion_validation{tag}.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"tau0 = {tau0:.1f} s (calibration rms {rms:.2f} nm; identifiable range {ident}); theta {a.theta}, Q {a.Q}")
    for r in rows:
        print(f"  {r['role']:11s} {r['cu']:3s} {r['figure']:7s} p{r['pitch_nm']:3.0f} D{r['D_nm']:3.0f} {r['T_C']:3.0f}C {r['t_h']:g}h {r['history']:9s} "
              f"meas {r['median_nm']:5.2f}±{r['err_nm']:.2f} pred {r['pred_nm']:5.2f} tol {r['tol_nm']:.2f} {'PASS' if r['passed'] else 'fail'}")
    print(f"held-out std-Cu: {n_pass}/{len(held)} = {frac:.0%}; T trend {tr['T_trend_ok']}; saturation {tr['saturation_ok']}")
    for s in tr["saturation"]:
        print(f"  saturation D{s['D_nm']:.0f}: R_meas {s['R_meas']:.2f}±{s['dR']:.2f} R_pred {s['R_pred']:.2f} {'ok' if s['ok'] else 'FAIL'}")
    for s in tr["size_scaling"]:
        print(f"  size {s['T_C']:.0f}C {s['t_h']:g}h {s['history']}: meas slope {s['meas_slope_nm_per_nm']:.4f} nm/nm intercept {s['meas_intercept_nm']:+.2f}; "
              f"pred slope {s['pred_slope_nm_per_nm']:.4f} intercept {s['pred_intercept_nm']:+.2f}")
    print("VERDICT:", verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
