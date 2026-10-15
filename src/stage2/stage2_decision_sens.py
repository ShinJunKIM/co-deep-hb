r"""Stage 2 decision-sensitivity test (docs/stage2_decision_sensitivity.md, pre-registered): does the 0.54 um elastic
error (bias b) change the contact-stage process window, compared with the diffusion time constant tau0?

Reuses stage2_predict (h_d, ez_random, k(Ez) fits) unchanged.  No ANSYS.
Usage: python src\stage2\stage2_decision_sens.py [--n 200000] [--tau0 20,60,100] [--theta 123] [--tag ""]
Output: results/stage2/decision_sensitivity[_tag].csv (all P values) and _summary.json (windows, verdict, ranking).
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stage2_predict as P  # noqa: E402

OUT = P.OUT
TS = (200, 250, 300, 350, 400)
TMIN = (5, 30, 120)
SURF = (("clean", 1.0), ("oxidised", 0.45))
B_GRID = (0.60, 0.69, 0.93, 1.00)
P_WIN = 0.99


def windows(n, seed, tau0_grid, theta, b_grid=B_GRID):
    rng = np.random.default_rng(seed)
    cfg = json.loads((OUT / "predict_config.json").read_text())
    rows, win = [], {}
    for c in cfg:
        fit = json.loads((OUT / f"predict_{c['label']}_fit.json").read_text())["fit"]
        coef = np.array(fit["coef"])
        ez1, ez2 = P.ez_random(n, rng), P.ez_random(n, rng)
        k12 = np.polyval(coef, ez1) + np.polyval(coef, ez2)
        g = rng.normal(2.5, 0.5, n) + rng.normal(2.5, 0.5, n)
        D_nm = c["size_um"] * 1000.0
        for (surf, sox), tau0, T, t_min in itertools.product(SURF, tau0_grid, TS, TMIN):
            hd = P.h_d(t_min * 60.0, T, D_nm, theta, tau0, sox)
            for b in b_grid:
                u = b * k12 * (T - 25.0)
                p = float(np.mean(u + 2 * hd >= g))
                rows.append(dict(size_um=c["size_um"], surface=surf, tau0_s=tau0, T_C=T, t_min=t_min, b=b,
                                 h_d_per_pad_nm=hd, u_el_mean_nm=float(u.mean()), P_contact=p, in_window=p >= P_WIN))
                win[(c["size_um"], surf, tau0, b)] = win.get((c["size_um"], surf, tau0, b), set()) | ({(T, t_min)} if p >= P_WIN else set())
    return rows, win


def neighbours(T, t):
    out = []
    i, j = TS.index(T), TMIN.index(t)
    if i > 0: out.append((TS[i - 1], t))
    if i < len(TS) - 1: out.append((TS[i + 1], t))
    if j > 0: out.append((T, TMIN[j - 1]))
    if j < len(TMIN) - 1: out.append((T, TMIN[j + 1]))
    return out


def judge(win, tau0_grid, sizes, b_grid=B_GRID):
    per_grid, closed = [], True
    for size, (surf, _), tau0 in itertools.product(sizes, SURF, tau0_grid):
        ws = [win[(size, surf, tau0, b)] for b in b_grid]
        common = set.intersection(*ws); union = set.union(*ws)
        diff = sorted(union - common)
        boundary = [c for c in diff if any(nb in common for nb in neighbours(*c))]
        ok = (len(diff) == 0) or (len(diff) == 1 and len(boundary) == 1)
        closed &= ok
        per_grid.append(dict(size_um=size, surface=surf, tau0_s=tau0, window_all_b=sorted(common), differing_cells=diff,
                             boundary_cells=boundary, ok=ok,
                             window_per_b={str(b): sorted(w) for b, w in zip(b_grid, ws)}))
    # sensitivity ranking
    n_b = sum(1 for size, (surf, _), tau0, T, t in itertools.product(sizes, SURF, tau0_grid, TS, TMIN)
              if len({(T, t) in win[(size, surf, tau0, b)] for b in b_grid}) > 1)
    n_tau = sum(1 for size, (surf, _), b, T, t in itertools.product(sizes, SURF, b_grid, TS, TMIN)
                if len({(T, t) in win[(size, surf, tau0, b)] for tau0 in tau0_grid}) > 1)
    tot_b = len(sizes) * len(SURF) * len(tau0_grid) * len(TS) * len(TMIN)
    tot_tau = len(sizes) * len(SURF) * len(b_grid) * len(TS) * len(TMIN)
    return dict(verdict="CLOSED" if closed else "OPEN", per_grid=per_grid,
                ranking=dict(N_b=n_b, of_b=tot_b, frac_b=n_b / tot_b, N_tau=n_tau, of_tau=tot_tau, frac_tau=n_tau / tot_tau,
                             more_sensitive="tau0" if n_tau / tot_tau > n_b / tot_b else ("b" if n_b / tot_b > n_tau / tot_tau else "equal")))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200_000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tau0", default="20,60,100")
    ap.add_argument("--theta", type=float, default=P.THETA_TA)
    ap.add_argument("--tag", default="")
    a = ap.parse_args(argv)
    tau0_grid = tuple(float(v) for v in a.tau0.split(","))
    rows, win = windows(a.n, a.seed, tau0_grid, a.theta)
    sizes = sorted({r["size_um"] for r in rows}, reverse=True)
    res = judge(win, tau0_grid, sizes)
    res.update(settings=dict(n=a.n, seed=a.seed, tau0_grid=tau0_grid, theta=a.theta, b_grid=B_GRID, P_window=P_WIN))
    tag = f"_{a.tag}" if a.tag else ""
    keys = list(rows[0])
    (OUT / f"decision_sensitivity{tag}.csv").write_text(",".join(keys) + "\n" + "".join(
        ",".join(f"{r[k]:.4g}" if isinstance(r[k], float) else str(r[k]) for k in keys) + "\n" for r in rows))
    json.dump(res, open(OUT / f"decision_sensitivity{tag}_summary.json", "w"), indent=1, default=str)
    print("VERDICT:", res["verdict"], "| ranking:", res["ranking"])
    for g in res["per_grid"]:
        print(f"{g['size_um']:.2f} um {g['surface']:8s} tau0 {g['tau0_s']:5.0f} s: window(all b) {len(g['window_all_b'])} cells; "
              f"differ {g['differing_cells']} boundary {g['boundary_cells']} ok {g['ok']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
