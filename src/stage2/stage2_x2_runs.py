r"""Round X2 (docs/stage2_round_x2_preregistration.md): liner-ring diagnostic X30-X34 and constraint-factor surrogate test X35-X38.
Elastic, 2D axisymmetric, Hill Cu, bonded sidewall. Usage: python src\stage2\stage2_x2_runs.py --run | --judge
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "stage1"))
import baseline as B  # noqa: E402
sys.modules.setdefault("baseline", B)
import stage2_runs  # noqa: E402,F401
import stage2_contact_runs  # noqa: E402,F401
import stage2_x_runs as X  # noqa: E402

OUT = B.RESULTS / "stage2"
IM = X.IM
NY = json.loads((OUT / "adopted_rev.json").read_text())["nycu"]
ALPHA = 16.5e-6 - 2.6e-6

RUNS = [
    B._run("X30", "XL", "imec", 0.54, 0.6, "XL liner 15 nm, 0.54 um array cell", cell_factor=2.26, t_liner=0.015, **IM),
    B._run("X31", "XL", "imec", 0.54, 0.6, "XL liner 25 nm, 0.54 um array cell", cell_factor=2.26, t_liner=0.025, **IM),
    B._run("X32", "XL", "imec", 1.80, 0.6, "XL liner 25 nm, 1.80 um array cell (control)", cell_factor=2.26, t_liner=0.025, **IM),
    B._run("X33", "XL", "imec", 1.26, 0.6, "XL liner 25 nm, 1.26 um array cell (control)", cell_factor=2.26, t_liner=0.025, **IM),
    B._run("X34", "XL", "imec", 0.54, 0.6, "XL liner 25 nm + pitch 1.7 w (2D 1.92 w), 0.54 um", cell_factor=1.92, t_liner=0.025, **IM),
    B._run("X35", "XS", "imec", 0.90, 0.6, "XS surrogate test w0.90 h0.60 array 2.26w", cell_factor=2.26, afm_field=8.0, **IM),
    B._run("X36", "XS", "imec", 0.40, 0.6, "XS surrogate test w0.40 h0.60 array 2.26w", cell_factor=2.26, afm_field=8.0, **IM),
    B._run("X37", "XS", "imec", 0.54, 0.3, "XS surrogate test w0.54 h0.30 array 2.26w", cell_factor=2.26, afm_field=8.0, **IM),
    B._run("X38", "XS", "nycu", 1.0, 0.6, "XS surrogate test NYCU w1.0 h0.6 isolated 12w taper 18", cell_factor=12.0, taper=NY["taper"],
           E_d=NY["E_d"], a_d=NY["a_d"], afm_field=3.5),
]
B.register([r for r in RUNS if r["id"] not in B.RUN_BY_ID])
PRED_C = {"X35": 0.92, "X36": 0.41, "X37": 1.05, "X38": 1.38}
PRED_U = {"X30": (1.80, 1.90), "X31": (1.65, 1.80), "X32": (4.85, 4.95), "X33": (3.90, 4.00), "X34": (1.50, 1.65)}


def u_hot(rid):
    rec = B.load(rid)
    if rec is None:
        return None
    h = rec["result"]["hist"]; return float(h[-1]["du_c50"]), float(h[-1]["T"])


def judge():
    res = {}
    for rid in PRED_U:
        v = u_hot(rid); res[rid] = dict(u_400=None if v is None else v[0], predicted=PRED_U[rid])
    s112 = B.load("S112"); u112 = float(s112["result"]["hist"][-1]["du_c50"]) if s112 else 2.039
    if res["X31"]["u_400"] and res["X32"]["u_400"]:
        r1 = (res["X31"]["u_400"] / u112 - 1 <= -0.10) and (res["X32"]["u_400"] / 4.99 - 1 >= -0.05)
        share = (u112 - res["X31"]["u_400"]) / (u112 - 1.40)
        res["R1_size_selective"] = bool(r1); res["R2_share"] = share
        res["R2_verdict"] = "major candidate" if share >= 0.8 else ("partial" if share >= 0.3 else "rejected")
    if res["X34"]["u_400"]:
        res["R3_combo_within_25pct"] = bool(1.05 <= res["X34"]["u_400"] <= 1.75)
    for rid, c_pred in PRED_C.items():
        v = u_hot(rid)
        if v is None:
            res[rid] = dict(C=None, predicted=c_pred); continue
        u, T = v; run = B.RUN_BY_ID[rid]; C = u / (ALPHA * (T - 25.0) * run["h"] * 1000.0)
        res[rid] = dict(u=u, T=T, C=C, predicted=c_pred, within_20pct=bool(abs(C / c_pred - 1) <= 0.20))
    xs = [res[r].get("within_20pct") for r in PRED_C]
    res["surrogate_verdict"] = "usable (all within 20 %)" if all(x is True for x in xs) else ("not all within 20 %" if all(x is not None for x in xs) else "incomplete")
    json.dump(res, open(OUT / "round_x2.json", "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--run", action="store_true"); ap.add_argument("--judge", action="store_true")
    ap.add_argument("--np", dest="nproc", type=int, default=B.S.DEFAULT_NP)
    a = ap.parse_args(argv)
    if a.run:
        B.execute([r["id"] for r in RUNS], a.nproc)
    judge()
    return 0


if __name__ == "__main__":
    sys.exit(main())
