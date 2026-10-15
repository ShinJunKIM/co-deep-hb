r"""Connection-stage fork: thickness-sensitive metrics from existing contact records (no solves).
Reads results/E*/contact.txt, top_disp.txt, deck_meta.json. Hot step = load step 2 (T_anneal).
Metrics at the hot step: A_c (status>=2 area fraction), r_in (innermost closed radius), r_out, void area fraction (r_in/A)^2,
centre gap where valid (status>0), Cu top-surface displacement of bottom/top pad at centre and rim (hot minus initial, nm),
pad-centre expansion relative to the dielectric reference (outermost top node), mean pressure.
Usage: python src\agents\connection_metrics.py [E52,E53,...]  -> prints table, writes results/stage2/agents_connection_metrics.csv
"""
import json, math, sys
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parents[2]; RES = REPO / "results"

def metrics(rid):
    d = RES / rid
    if not (d / "contact.txt").exists() or not (d / "deck_meta.json").exists():
        return None
    m = json.loads((d / "deck_meta.json").read_text()); xy = {int(k): v for k, v in m["node_xy"].items()}
    run, g = m["run"], m["geometry"]; A = g["A"]; nls = len(run["temps"]); hot = 1
    ct = np.loadtxt(d / "contact.txt", ndmin=2)
    n1, n2 = ct[:, 1].astype(int), ct[:, 2].astype(int)
    x1 = np.array([xy[n][0] for n in n1]); x2 = np.array([xy[n][0] for n in n2]); xm = 0.5 * (x1 + x2); dl = np.abs(x2 - x1)
    dA = 2 * math.pi * xm * dl; c = 3 + 3 * hot
    st, pr, gp = ct[:, c], ct[:, c + 1], ct[:, c + 2]
    inc = st >= 2
    Ac = float(dA[inc].sum() / (math.pi * A * A))
    r_in = float(xm[inc].min()) if inc.any() else float("nan"); r_out = float(xm[inc].max()) if inc.any() else float("nan")
    void = (r_in / A) ** 2 if inc.any() else 1.0
    # centre gap: valid only if status > 0 (within pinball); report nan otherwise
    i0 = int(np.argmin(xm)); gap_c = float(gp[i0] * 1000) if st[i0] > 0 else float("nan")
    # largest open gap along the radius (valid elements only)
    valid = st > 0
    gap_max_open = float(-gp[valid & ~inc].min() * 1000) if (valid & ~inc).any() else 0.0
    pm = float((pr[inc] * dA[inc]).sum() / dA[inc].sum()) if inc.any() else 0.0
    # top-surface displacements: rows = bottom-pad top nodes; cols: id, (UY_bot, UY_top) per ls
    td = np.loadtxt(d / "top_disp.txt", ndmin=2)
    nodes = td[:, 0].astype(int); xs = np.array([xy[n][0] for n in nodes]); o = np.argsort(xs); xs = xs[o]
    ub = td[o, 1 + 2 * hot] - td[o, 1]; ut = td[o, 2 + 2 * hot] - td[o, 2]     # hot minus initial (um)
    # pad region = x <= A; dielectric reference = outermost node (x = R)
    pad = xs <= A * 1.0001
    u_c_b, u_c_t = float(ub[0] * 1000), float(-ut[0] * 1000)           # top pad moves -y when expanding toward the interface
    u_rim_b = float(ub[pad][-1] * 1000); u_ref_b = float(ub[-1] * 1000)
    return dict(id=rid, w=run["w"], h=run["h"], r0_nm=run["recess"] * 1000, T=run["T_anneal"], diel=run.get("diel"),
                ys=run.get("yield_scale", 1.0), Ac=Ac, r_in_um=r_in, r_in_over_A=r_in / A if inc.any() else float("nan"),
                void_frac=void, r_out_over_A=r_out / A if inc.any() else float("nan"), gap_centre_nm=gap_c,
                gap_max_open_nm=gap_max_open, p_mean_MPa=pm, u_centre_bot_nm=u_c_b, u_centre_top_nm=u_c_t,
                u_rim_bot_nm=u_rim_b, u_ref_diel_nm=u_ref_b, u_centre_rel_diel_nm=u_c_b - u_ref_b, n_closed=int(inc.sum()), n_el=len(st))

def main(ids):
    rows = [r for r in (metrics(i) for i in ids) if r]
    keys = list(rows[0])
    out = RES / "stage2" / "agents_connection_metrics.csv"
    out.write_text(",".join(keys) + "\n" + "".join(",".join(f"{r[k]:.4g}" if isinstance(r[k], float) else str(r[k]) for k in keys) + "\n" for r in rows))
    for r in rows:
        print(f"{r['id']:4s} w{r['w']:.2f} h{r['h']:.2f} r0 {r['r0_nm']:4.0f} ys{r['ys']:.0f} | Ac {r['Ac']:.3f} r_in/A {r['r_in_over_A']:.2f} void {r['void_frac']:.2f} "
              f"gap_c {r['gap_centre_nm']:6.2f} gapmax {r['gap_max_open_nm']:5.2f} | u_c bot/top {r['u_centre_bot_nm']:5.2f}/{r['u_centre_top_nm']:5.2f} rim {r['u_rim_bot_nm']:5.2f} diel {r['u_ref_diel_nm']:5.2f} -> u_c-rel {r['u_centre_rel_diel_nm']:5.2f} | p {r['p_mean_MPa']:4.0f}")
    return rows

if __name__ == "__main__":
    ids = sys.argv[1].split(",") if len(sys.argv) > 1 else [f"E{i:02d}" for i in range(1, 64)]
    main(ids)
