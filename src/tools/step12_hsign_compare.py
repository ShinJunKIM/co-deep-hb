"""Step 12: test of the sign-convention hypothesis H_sign (docs/stage1_step12_sign_hypothesis.md).

H_sign: Ayoub reports eps'_zz (measured and FEM) with the opposite sign to ours.

Test A (decisive): R35 (pad 3, paper-literal elastic) vs -(Ayoub's pad-3 elastic FEM curve).
    |FEM| >= 0.3e-3 :  0.90 <= model / (-FEM) <= 1.10
    |FEM| <  0.3e-3 :  |model + FEM| <= 0.10e-3
    PASS iff every heating temperature 30..400 C passes.
Test B: model delta(30 C -> 400 C after 2 h) for pads 4, 5, 7, 9, 10 (R36..R39, R27) vs -(Fig. 2c delta).
    r_p = d_model / (-d_meas);  tol_p = max(0.10, err_p / d_meas)
    B-consistency (Step 11 rule): |r_p / mean(r) - 1| <= tol_p for all five
    B-absolute (no calibration):  |r_p - 1| <= tol_p for all five

Usage (repo root):  python src\\tools\\step12_hsign_compare.py
Writes results/diagnostics/step12_testA_pad3.csv and step12_testB.csv.
"""
import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
RUNS_B = {10: "R27", 4: "R36", 5: "R37", 7: "R38", 9: "R39"}


def load(rid):
    f = REPO / "results" / rid / "record.json"
    if not f.exists():
        raise SystemExit(f"{rid}: {f} missing - run it first")
    return {r["ls"]: r for r in json.loads(f.read_text(encoding="utf-8"))["rows"]}


def test_a():
    dig = json.loads((REPO / "inputs/ayoub2022_eps_dev_digitized.json").read_text(encoding="utf-8"))
    fem = {int(k): v for k, v in dig["pad3"]["paper_fem_elastic"].items()}
    Tk = np.array(sorted(fem)); Fk = np.array([fem[t] for t in Tk])
    line = np.polyfit(Tk, Fk, 1)                       # FEM elastic curve is linear (digitized at 30, 100, 400 C)
    by = load("R35")
    rows, ok = [], True
    for ls in range(0, 8):
        r = by[ls]; T = r["T"]; m = r["eps_dev_zz"] * 1e3; f = float(np.polyval(line, T))
        if abs(f) >= 0.3:
            ratio = m / (-f); p = 0.90 <= ratio <= 1.10; crit = f"ratio {ratio:.3f}"
        else:
            ratio = np.nan; p = abs(m + f) <= 0.10; crit = f"|model+FEM| {abs(m + f):.3f}"
        ok &= p
        rows.append((T, m, -f, ratio, p, crit))
    out = REPO / "results/diagnostics/step12_testA_pad3.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("T_C,model_epsdev_1e-3,minus_AyoubFEM_1e-3,ratio,pass\n" +
                   "".join(f"{T:g},{m:.4f},{f:.4f},{q:.4f},{p}\n" for T, m, f, q, p, _ in rows), encoding="utf-8")
    print("TEST A  pad 3 (R35) vs -(Ayoub elastic FEM); FEM line fit residual at 100 C =",
          f"{fem[100] - np.polyval(line, 100):+.3f}e-3")
    for T, m, f, q, p, c in rows:
        print(f"  {T:5.0f} C  model {m:+.3f}  -FEM {f:+.3f}  {c:<22} {'pass' if p else 'FAIL'}")
    print("TEST A VERDICT:", "PASS" if ok else "FAIL")
    return ok


def test_b():
    fig2 = json.loads((REPO / "inputs/ayoub2022_fig2ac_digitized.json").read_text(encoding="utf-8"))
    meas = {d["pad"]: d for d in fig2["fig2c_delta_30_400h"]}
    rows = []
    for pad, rid in RUNS_B.items():
        by = load(rid)
        d = (by[8]["eps_dev_zz"] - by[0]["eps_dev_zz"]) * 1e3
        m = meas[pad]
        rows.append(dict(pad=pad, run=rid, d_model=d, minus_d_meas=-m["value"], err=m["err"],
                         ratio=d / (-m["value"]), tol=max(0.10, m["err"] / m["value"])))
    rbar = np.mean([r["ratio"] for r in rows])
    for r in rows:
        r["dev"] = r["ratio"] / rbar - 1
        r["pass_cons"] = abs(r["dev"]) <= r["tol"]
        r["pass_abs"] = abs(r["ratio"] - 1) <= r["tol"]
    out = REPO / "results/diagnostics/step12_testB.csv"
    keys = list(rows[0].keys())
    out.write_text(",".join(keys) + "\n" + "".join(
        ",".join(f"{r[k]:.5g}" if isinstance(r[k], float) else str(r[k]) for k in keys) + "\n" for r in rows), encoding="utf-8")
    print("TEST B  model delta vs -(Fig 2c delta)")
    for r in rows:
        print(f"  pad {r['pad']:>2} {r['run']}  model {r['d_model']:+.3f}  -meas {r['minus_d_meas']:+.3f}  r {r['ratio']:.3f}"
              f"  dev {r['dev']:+.3f}  tol {r['tol']:.3f}  cons {'pass' if r['pass_cons'] else 'FAIL'}"
              f"  abs {'pass' if r['pass_abs'] else 'FAIL'}")
    cons = all(r["pass_cons"] for r in rows); ab = all(r["pass_abs"] for r in rows)
    print(f"TEST B VERDICT: consistency {'PASS' if cons else 'FAIL'}, absolute {'PASS' if ab else 'FAIL'} (mean r = {rbar:.3f})")
    return cons, ab


if __name__ == "__main__":
    a = test_a()
    b = test_b()
    print("H_sign:", "SUPPORTED (A pass, B absolute pass)" if a and b[1] else
          "NOT SUPPORTED by A" if not a else "A pass, B fails -> sign may explain Ayoub's FEM but not the orientation data")
