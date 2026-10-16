r"""v2: process window with the orientation-resolved elastic term (R-O7 of docs/v2_orientation_preregistration.md).

Replaces the Ez quadratic fit by the accepted hkl surrogate k(x, y) (x = k/h, y = l/h of the sorted direction) from
results/stage2/v2/orientation_study.json, separately for the bonded and the sliding sidewall, and reruns
f_omega_variants.run_windows (probability window, three-region map, worst-orientation margin, allowable recess) for
300 nm.  Compares cell regions with the Ez-fit baseline (results/stage2/v2/f_omega_variants.json).
In-plane rotation is NOT an input here unless R-O2 failed; then an angle-induced relative spread is reported.
Usage (worktree root): python src\v2\orient_window.py [--n 60000]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(REPO / "src" / "stage2"))
import f_omega_variants as F  # noqa: E402

OUT = REPO / "results" / "stage2" / "v2"


def design(x, y, order):
    cols = [np.ones_like(x)]
    for p in range(1, order + 1):
        for i in range(p + 1):
            cols.append(x ** (p - i) * y ** i)
    return np.column_stack(cols)


def make_k_fn(study, side):
    o = study[side]
    sur = o["surrogates"]
    name = next((n for n in ("poly2", "poly3") if sur.get(n, {}).get("accept")), None)
    if name is None:   # pre-registered order: poly2 -> poly3 -> piecewise linear; fall back to linear interpolation on T+H
        from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
        pts = [(q["x"], q["y"], q["k"]) for q in o["rows"] if q["k"] is not None and q["set"] in ("T", "H")]
        P = np.array([(a, b) for a, b, _ in pts]); K = np.array([c for _, _, c in pts])
        lin = LinearNDInterpolator(P, K); near = NearestNDInterpolator(P, K)

        def k_fn(v):
            s = -np.sort(-np.abs(v), axis=1); x = s[:, 1] / s[:, 0]; y = s[:, 2] / s[:, 0]
            z = lin(np.column_stack([x, y])); bad = ~np.isfinite(z); z[bad] = near(np.column_stack([x, y]))[bad]
            return z
        return k_fn, "pwlinear"
    order = 2 if name == "poly2" else 3
    c = np.array(sur[name]["coef"])

    def k_fn(v):
        s = -np.sort(-np.abs(v), axis=1); x = s[:, 1] / s[:, 0]; y = s[:, 2] / s[:, 0]
        return design(x, y, order) @ c
    return k_fn, name


def regions(win):
    out = {}
    for surf, cells in win["surfaces"].items():
        out[surf] = {c: d["region"] for c, d in cells.items()}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=60_000); ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    study = json.loads((OUT / "orientation_study.json").read_text())
    base = json.loads((OUT / "f_omega_variants.json").read_text())
    fits = {k: v for k, v in base["fits"].items() if k in base["variants_used_for_windows"]}
    res = dict(status="exploratory window recomputation; uniform orientation assumed; MC counts are not data", sides={})
    base_reg = regions(base["windows"]["0.30um"])
    for side in ("bonded", "sliding"):
        if "surrogates" not in study.get(side, {}):
            continue
        k_fn, used = make_k_fn(study, side)
        win = F.run_windows("0.30um", 0.30, fits, a.n, a.seed, k_fn=k_fn)
        reg = regions(win)
        diff = {surf: sorted(c for c in reg[surf] if reg[surf][c] != base_reg[surf].get(c)) for surf in reg}
        res["sides"][side] = dict(surrogate=used, windows=win, regions=reg, cells_changed_vs_Ez_fit=diff,
                                  region_counts={surf: {r: sum(1 for v in reg[surf].values() if v == r) for r in set(reg[surf].values())} for surf in reg})
        print(side, used, "region counts", res["sides"][side]["region_counts"], "changed vs Ez fit", {s: len(v) for s, v in diff.items()})
    json.dump(res, open(OUT / "orient_window.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
