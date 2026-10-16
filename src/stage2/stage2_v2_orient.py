r"""v2 orientation study (docs/v2_orientation_preregistration.md): 300 nm imec pads, 3D anisotropic Cu, array cell 2.0 w,
adopted SiCN (E 120 GPa, alpha 2.0 ppm/K), TaN/Ta 6 nm, elastic; bonded (VB) and sliding (VS) sidewall.

Direction = sorted (1, x, y), 1 >= x >= y >= 0 (cubic fundamental triangle); in-plane angle about the pad normal (deg).
Sets: T = 45-point training grid (x, y in steps of 1/8), H = 20 held-out directions (8 random interior, 4 near [111],
8 = 4 same-E_z pairs on two different edges), R = in-plane rotation test (6 directions x 22.5 / 45 deg).
Observable per run: k = du_c50 / (T - 25) [nm/K] (linear elastic, constant properties -> exactly proportional).

Usage (from the worktree root):  python src\stage2\stage2_v2_orient.py --list | --run [--set T,H,R] [--side bonded,sliding]
                                 python src\stage2\stage2_v2_orient.py --analyze
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
import stage2_contact_runs  # noqa: E402,F401
import stage2_x_runs  # noqa: E402,F401
import stage1_pipeline as S  # noqa: E402

REPO = HERE.parents[1]
OUT = REPO / "results" / "stage2" / "v2"; OUT.mkdir(parents=True, exist_ok=True)
FIG = REPO / "results" / "figures" / "v2"; FIG.mkdir(parents=True, exist_ok=True)
AD = json.loads((REPO / "results" / "stage2" / "adopted_rev.json").read_text())["imec"]
BASE = dict(cu="aniso", cell_factor=2.0, E_d=AD["E_d"], a_d=AD["a_d"])


def gamma(x, y):
    n2 = 1 + x * x + y * y
    return (x * x + y * y + x * x * y * y) / n2 ** 2


def ez(x, y):
    return S.Ez_closed_form((1.0, x, y)) / 1000.0


def _solve_edge(G, edge):
    """point on an edge with gamma = G: edge 'y0' -> (x, 0); 'diag' -> (x, x)."""
    lo, hi = 0.0, 1.0
    f = (lambda x: gamma(x, 0.0)) if edge == "y0" else (lambda x: gamma(x, x))
    for _ in range(80):
        m = 0.5 * (lo + hi)
        lo, hi = (m, hi) if f(m) < G else (lo, m)
    x = 0.5 * (lo + hi)
    return (x, 0.0) if edge == "y0" else (x, x)


def direction_sets():
    T = [(i / 8, j / 8) for i in range(9) for j in range(i + 1)]
    rng = np.random.default_rng(20261016)
    H = []
    while len(H) < 8:                                   # random interior, area-uniform in the triangle
        a, b = rng.random(2)
        x, y = max(a, b), min(a, b)
        if 0.05 < y < x - 0.05 and x < 0.95 and all(abs(x - p[0]) > 0.04 or abs(y - p[1]) > 0.04 for p in T):
            H.append((round(x, 4), round(y, 4)))
    H += [(0.97, 0.95), (0.95, 0.90), (0.93, 0.80), (0.98, 0.70)]   # near [111]
    for G in (0.05, 0.10, 0.15, 0.20):                  # same-E_z pairs on two different edges
        H.append(tuple(round(v, 5) for v in _solve_edge(G, "y0")))
        H.append(tuple(round(v, 5) for v in _solve_edge(G, "diag")))
    R = [((0.0, 0.0), a) for a in (22.5, 45.0)] + [((0.5, 0.0), a) for a in (22.5, 45.0)] + \
        [((1.0, 0.0), a) for a in (22.5, 45.0)] + [((0.5, 0.25), a) for a in (22.5, 45.0)] + \
        [((1.0, 0.5), a) for a in (22.5, 45.0)] + [((1.0, 1.0), a) for a in (22.5, 45.0)]
    return T, H, R


def make_runs():
    T, H, R = direction_sets()
    runs = []
    for side, pre in (("bonded", "VB"), ("sliding", "VS")):
        n = 0
        for set_name, items in (("T", [(d, 0.0) for d in T]), ("H", [(d, 0.0) for d in H]), ("R", R)):
            for (x, y), ang in items:
                n += 1
                rid = f"{pre}{n:03d}"
                note = f"V2 {set_name} 0.30 um 3D (1,{x:.4g},{y:.4g}) ang {ang:g} {side}"
                r = B._run(rid, "V2", "imec", 0.30, 0.6, note, orient=(1.0, float(x), float(y)), cu_angle=float(ang),
                           side=side, **BASE)
                r.update(v2_set=set_name, v2_x=float(x), v2_y=float(y))
                runs.append(r)
    return runs


RUNS = make_runs()
B.register([r for r in RUNS if r["id"] not in B.RUN_BY_ID])

# contact-boundary check (docs/v2_contact_boundary_preregistration.md): sliding sidewall, 0.30 um, imec stack
import stage2_contact_runs as _C  # noqa: E402
CONTACT = []
for _rid, _r, _T in (("E71", 2.0, 250), ("E72", 3.0, 250), ("E73", 3.0, 300), ("E74", 4.0, 300)):
    _run_c = _C._c(_rid, 0.30, 0.6, _r, _T, f"contact v2 boundary SLIDING 0.30 um r{_r:g} nm T{_T}")
    _run_c.update(side="sliding"); CONTACT.append(_run_c)
B.register([r for r in CONTACT if r["id"] not in B.RUN_BY_ID])


def k_of(rid):
    rec = B.load(rid)
    if rec is None:
        return None
    h = rec["result"]["hist"]
    T = np.array([e["T"] for e in h]); u = np.array([e["du_c50"] for e in h])
    k = float(np.polyfit(T - 25.0, u, 1)[0])
    lin = float(np.max(np.abs(u - k * (T - 25.0))))
    return dict(k=k, u400=float(u[-1]), lin_dev_nm=lin, wall_s=rec["exec"]["wall_s"])


# ------------------------------------------------------------------ surrogate
def design(x, y, order):
    x = np.atleast_1d(x); y = np.atleast_1d(y)
    cols = [np.ones_like(x)]
    for p in range(1, order + 1):
        for i in range(p + 1):
            cols.append(x ** (p - i) * y ** i)
    return np.column_stack(cols)


def fit_poly(X, Y, K, order):
    A = design(X, Y, order); c, *_ = np.linalg.lstsq(A, K, rcond=None)
    return c


def pred_poly(c, x, y, order):
    return design(x, y, order) @ c


def tri_grid(n=201):
    xs = np.linspace(0, 1, n); pts = [(x, y) for x in xs for y in xs if y <= x + 1e-12]
    return np.array(pts)


def analyze():
    res = {}
    for side, pre in (("bonded", "VB"), ("sliding", "VS")):
        rows = []
        for r in RUNS:
            if not r["id"].startswith(pre):
                continue
            kk = k_of(r["id"])
            rows.append(dict(id=r["id"], set=r["v2_set"], x=r["v2_x"], y=r["v2_y"], ang=r.get("cu_angle", 0.0),
                             Ez=ez(r["v2_x"], r["v2_y"]), **(kk or dict(k=None))))
        done = [q for q in rows if q["k"] is not None]
        tr = [q for q in done if q["set"] == "T"]; ho = [q for q in done if q["set"] == "H"]; ro = [q for q in done if q["set"] == "R"]
        out = dict(n_done=len(done), n_total=len(rows))
        if len(tr) < 10:
            res[side] = out; continue
        K = np.array([q["k"] for q in tr]); X = np.array([q["x"] for q in tr]); Y = np.array([q["y"] for q in tr])
        kmean = float(K.mean())
        out["train_spread_rel"] = float((K.max() - K.min()) / kmean)
        out["train_k_min"] = dict(k=float(K.min()), at=[float(X[K.argmin()]), float(Y[K.argmin()])])
        out["train_k_max"] = dict(k=float(K.max()), at=[float(X[K.argmax()]), float(Y[K.argmax()])])
        out["max_linearity_dev_nm"] = float(max(q["lin_dev_nm"] for q in done))
        # Ez-only reduction (quadratic in Ez) on the training set
        Ez_tr = np.array([q["Ez"] for q in tr]); cz = np.polyfit(Ez_tr, K, 2)
        out["ez_fit_train_rms_rel"] = float(np.sqrt(np.mean((np.polyval(cz, Ez_tr) - K) ** 2)) / kmean)
        g = tri_grid()
        surr = {}
        for order in (2, 3):
            c = fit_poly(X, Y, K, order)
            info = dict(train_rms_rel=float(np.sqrt(np.mean((pred_poly(c, X, Y, order) - K) ** 2)) / kmean))
            if ho:
                Kh = np.array([q["k"] for q in ho]); Ph = pred_poly(c, np.array([q["x"] for q in ho]), np.array([q["y"] for q in ho]), order)
                err = Ph - Kh
                info.update(ho_mean_abs_rel=float(np.mean(np.abs(err)) / kmean), ho_max_abs_rel=float(np.max(np.abs(err)) / kmean),
                            ho_max_abs_u400_nm=float(np.max(np.abs(err)) * 375.0),
                            ez_ho_max_abs_rel=float(np.max(np.abs(np.polyval(cz, np.array([q["Ez"] for q in ho])) - Kh)) / kmean))
            Pg = pred_poly(c, g[:, 0], g[:, 1], order)
            info.update(surface_min=dict(k=float(Pg.min()), at=[float(g[Pg.argmin(), 0]), float(g[Pg.argmin(), 1])]),
                        surface_max=dict(k=float(Pg.max()), at=[float(g[Pg.argmax(), 0]), float(g[Pg.argmax(), 1])]))
            info["coef"] = c.tolist(); surr[f"poly{order}"] = info
        # piecewise-linear interpolation (Delaunay) on the training set
        try:
            from scipy.interpolate import LinearNDInterpolator
            lin = LinearNDInterpolator(np.column_stack([X, Y]), K)
            if ho:
                Ph = lin(np.array([[q["x"], q["y"]] for q in ho])); err = Ph - np.array([q["k"] for q in ho])
                surr["pwlinear"] = dict(ho_mean_abs_rel=float(np.nanmean(np.abs(err)) / kmean), ho_max_abs_rel=float(np.nanmax(np.abs(err)) / kmean),
                                        ho_max_abs_u400_nm=float(np.nanmax(np.abs(err)) * 375.0))
        except Exception as exc:  # noqa: BLE001
            surr["pwlinear"] = dict(error=str(exc))
        out["surrogates"] = surr
        # pre-registered acceptance (R-O3): max |err| <= 5 % of mean k AND <= 0.1 nm in u(400 C) per pad
        for name in ("poly2", "poly3", "pwlinear"):
            s = surr.get(name, {})
            if "ho_max_abs_rel" in s:
                s["accept"] = bool(s["ho_max_abs_rel"] <= 0.05 and s["ho_max_abs_u400_nm"] <= 0.1)
        # same-E_z pairs (last 8 of H) and in-plane rotation
        pairs = [q for q in ho if abs(q["y"]) < 1e-9 or abs(q["x"] - q["y"]) < 1e-9][-8:]
        pr = []
        for i in range(0, len(pairs) - 1, 2):
            a_, b_ = pairs[i], pairs[i + 1]
            pr.append(dict(Ez=[a_["Ez"], b_["Ez"]], k=[a_["k"], b_["k"]], rel_diff=(b_["k"] - a_["k"]) / (0.5 * (a_["k"] + b_["k"]))))
        out["same_Ez_pairs"] = pr
        rot = []
        for (x0, y0) in sorted({(q["x"], q["y"]) for q in ro}):
            base = next((q for q in tr if abs(q["x"] - x0) < 1e-9 and abs(q["y"] - y0) < 1e-9), None)
            ks = ([base["k"]] if base else []) + [q["k"] for q in ro if abs(q["x"] - x0) < 1e-9 and abs(q["y"] - y0) < 1e-9]
            rot.append(dict(dir=[x0, y0], k=ks, rel_range=float((max(ks) - min(ks)) / np.mean(ks)) if len(ks) > 1 else None))
        out["inplane_rotation"] = rot
        # stability: refit poly2/3 on T+H and compare the surface minimum
        if ho:
            XA = np.concatenate([X, [q["x"] for q in ho]]); YA = np.concatenate([Y, [q["y"] for q in ho]]); KA = np.concatenate([K, [q["k"] for q in ho]])
            for order in (2, 3):
                cA = fit_poly(XA, YA, KA, order); PgA = pred_poly(cA, g[:, 0], g[:, 1], order)
                out[f"refit_all_poly{order}_surface_min"] = dict(k=float(PgA.min()), at=[float(g[PgA.argmin(), 0]), float(g[PgA.argmin(), 1])],
                                                                 coef=cA.tolist())
            out["observed_min_all"] = float(min(KA))
        out["rows"] = rows
        res[side] = out
    json.dump(res, open(OUT / "orientation_study.json", "w"), indent=1, default=float)
    for side in res:
        o = res[side]
        print(f"== {side}: {o['n_done']}/{o['n_total']} runs")
        if "surrogates" in o:
            print(f"   train spread {o['train_spread_rel']:.3%}, k_min {o['train_k_min']}, k_max {o['train_k_max']}, Ez-fit rms {o['ez_fit_train_rms_rel']:.3%}, linearity dev {o['max_linearity_dev_nm']:.2e} nm")
            for n_, s in o["surrogates"].items():
                print("   ", n_, {k: (round(v, 5) if isinstance(v, float) else v) for k, v in s.items() if k != "coef"})
            print("    same-Ez pairs:", [round(p["rel_diff"], 4) for p in o["same_Ez_pairs"]])
            print("    in-plane:", [(p["dir"], None if p["rel_range"] is None else round(p["rel_range"], 4)) for p in o["inplane_rotation"]])
    return res


def figure(res):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for ax, side in zip(axs, ("bonded", "sliding")):
        o = res.get(side, {})
        if "surrogates" not in o:
            continue
        g = tri_grid(121); c = np.array(o["surrogates"]["poly3"]["coef"]); P = pred_poly(c, g[:, 0], g[:, 1], 3) * 375.0
        sc = ax.tricontourf(g[:, 0], g[:, 1], P, 20, cmap="viridis")
        tr = [q for q in o["rows"] if q["k"] is not None and q["set"] == "T"]; ho = [q for q in o["rows"] if q["k"] is not None and q["set"] == "H"]
        ax.plot([q["x"] for q in tr], [q["y"] for q in tr], "w.", ms=3); ax.plot([q["x"] for q in ho], [q["y"] for q in ho], "r^", ms=3)
        ax.set_xlabel("k/h"); ax.set_ylabel("l/h"); ax.set_title(f"{side}: u(400 °C) per pad (nm), cubic surrogate", fontsize=7.5)
        fig.colorbar(sc, ax=ax, shrink=0.85)
    fig.tight_layout(); fig.savefig(FIG / "orientation_surface_0.30um.png", dpi=300); plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true"); ap.add_argument("--run", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--set", default="T,H,R"); ap.add_argument("--side", default="bonded,sliding")
    ap.add_argument("--np", dest="nproc", type=int, default=S.DEFAULT_NP)
    a = ap.parse_args(argv)
    sets = a.set.split(","); sides = a.side.split(",")
    sel = [r for r in RUNS if r["v2_set"] in sets and r["side"] in sides]
    if a.list:
        for r in sel:
            print(r["id"], r["v2_set"], r["side"], (1, r["v2_x"], r["v2_y"]), r.get("cu_angle", 0.0), f"Ez {ez(r['v2_x'], r['v2_y']):.1f}")
        print(len(sel), "runs")
    if a.run:
        B.execute([r["id"] for r in sel], a.nproc)
    if a.analyze:
        res = analyze(); figure(res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
