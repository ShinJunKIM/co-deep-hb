r"""
Stage 2 baseline model: parametrized Cu pad in dielectric on Si (uMKS: um, MPa, 1/K).

Pre-registration: docs/stage2_baseline_preregistration.md (commit 33a8f5c); V&V plan: docs/stage2_vv_plan.md.
Run IDs: S-series (contact stage) and E-series (connection stage). R-decks (R01-R71) are never touched.

Contact-stage model (2D axisymmetric PLANE182 or 3D SOLID185, as lin13.py but parametrized):
    Si (-t_si .. 0) / dielectric under the pad (0 .. z_ox) / pad layer (z_ox .. z_ox + h)
    Cu frustum (top width w, taper from vertical), liner ring + liner bottom layer (MAT 5), dielectric (MAT 2).
    Sidewall: bonded (shared nodes) or sliding (normal tie only, control).
    Cu: isotropic Hill (elastic or isotropic plastic, Okoro 2008 sigma_y(T)) or anisotropic (TB,ANEL, elastic).
u definitions (nm, change from the first temperature):
    u_c50  = mean UZ over the central 50 % of the pad area - mean UZ of the non-Cu top surface in the AFM field  [PRIMARY]
    u_ctr  = centre UZ - cell-edge UZ (Step 13 definition)
    u_full = full pad mean - AFM field reference
Connection-stage model (2D axisymmetric): two mirrored wafers, dielectric-dielectric shared nodes, Cu-Cu frictional
    contact (CONTA172/TARGE169), spherical-cap dishing r0 on each pad, heating 25 -> T_anneal -> 25.

Usage: python src\stage2\baseline.py --list | --case S01,S02 | --group A | --dry-run
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "stage1"))
import s1_mesh as M          # noqa: E402  (grading helpers)
import stage1_pipeline as S  # noqa: E402  (Cu constants, rotation, batch runner)
import lin13 as L13          # noqa: E402  (hill_cu, ORIENT)

REPO = S.REPO
RESULTS = S.RESULTS
LOG = REPO / "docs" / "stage2_exploration_log.md"
T_REF = 25.0
SI = S.SILICON
TA = dict(EX=186000.0, PRXY=0.34, ALPX=6.5e-6)            # Zhmurkin 1997 Table I

# dielectric candidates (pre-registration 4.2)
DIEL = {
    "SiO2": dict(PRXY=0.17),      # E, ALPX set per run
    "SiCN": dict(PRXY=0.20),
}
DATASETS = {
    "nycu": dict(diel="SiO2", t_liner=0.050, z_ox=0.5, temps=[25.0, 50.0, 100.0, 150.0, 200.0]),
    "imec": dict(diel="SiCN", t_liner=0.006, z_ox=0.5, temps=[25.0, 100.0, 200.0, 300.0, 400.0]),
}
AFM_FIELD = {"nycu": {9.0: 25.0, 3.0: 8.0, 1.0: 3.5, 2.5: 8.0, 4.0: 12.0, 5.0: 15.0}, "imec": 8.0}


# ---------------------------------------------------------------- run definitions
def _run(rid, group, ds, w, h, note, **kw):
    d = DATASETS[ds]
    r = dict(id=rid, group=group, ds=ds, w=float(w), h=float(h), note=note, dim=2, cu="iso", orient=None,
             side="bonded", plastic=False, cell_factor=3.0, taper=0.0, refine=1, z_ox=d["z_ox"],
             t_liner=d["t_liner"], diel=d["diel"], E_d=None, a_d=None, temps=list(d["temps"]),
             cu_alpha=S.CU_ALPHA_CONST, afm_field=None)
    r.update(kw)
    if r["afm_field"] is None:
        f = AFM_FIELD[ds]
        r["afm_field"] = f[r["w"]] if isinstance(f, dict) else f
    if r["cu"] == "aniso":
        r["dim"] = 3
    return r


RUNS: list[dict] = []
RUN_BY_ID: dict[str, dict] = {}


def register(runs):
    for r in runs:
        if r["id"] in RUN_BY_ID:
            raise ValueError(f"duplicate run id {r['id']}")
        RUNS.append(r); RUN_BY_ID[r["id"]] = r
    return runs


# ---------------------------------------------------------------- geometry and meshes (adapted from lin13.py)
def geometry(run):
    w, h = run["w"], run["h"]
    A = w / 2.0
    L = run["cell_factor"] * w
    th = math.radians(run["taper"])
    a_bot = A - h * math.tan(th)
    if a_bot <= 0.02 * A:          # same threshold as lin13.py (R54 precedent: 1 um at 18 deg)
        raise ValueError(f"{run['id']}: taper {run['taper']} deg leaves no pad bottom")
    return dict(w=w, h=h, A=A, L=L, R=L / 2.0, t_si=L, zpb=run["z_ox"], zpt=run["z_ox"] + h, theta=th,
                a_bot=a_bot, t_l=run["t_liner"])


def _radius_factor(z, g):
    zc = min(max(z, g["zpb"]), g["zpt"])
    return (g["A"] - (g["zpt"] - zc) * math.tan(g["theta"])) / g["A"]


def _z_axis(g, h_p, growth=1.2):
    si = M._graded(g["t_si"], h_p, growth, max(g["t_si"] / 6, h_p))[::-1]
    t_l = g["t_l"]
    ox = M._symmetric_graded(g["zpb"] - t_l, h_p, growth, 4 * h_p)
    pad = M._symmetric_graded(g["h"], h_p, growth, 2.5 * h_p)
    parts = [si, ox] + ([np.array([t_l])] if t_l > 0 else []) + [pad]
    inc = np.concatenate(parts)
    z = np.concatenate([[-g["t_si"]], -g["t_si"] + np.cumsum(inc)])
    k_si = len(si)
    k_lb = k_si + len(ox)                       # liner bottom layer starts here (if any)
    k_pb = k_lb + (1 if t_l > 0 else 0)         # pad bottom
    k_pt = k_pb + len(pad)
    z[k_si], z[k_pb], z[k_pt] = 0.0, g["zpb"], g["zpt"]
    if t_l > 0:
        z[k_lb] = g["zpb"] - t_l
    return z, k_si, k_lb, k_pb, k_pt


def mesh_2d(run):
    g = geometry(run)
    n_r = 40 * run["refine"]
    h_p = g["A"] / n_r
    t_l = g["t_l"]
    xi_pad = np.linspace(0.0, g["A"], n_r + 1)
    out = M._graded(g["R"] - g["A"] - t_l, min(h_p, 3 * t_l) if t_l > 0 else h_p, 1.15, max((g["R"] - g["A"]) / 10, h_p))
    parts = [xi_pad] + ([np.array([g["A"] + t_l])] if t_l > 0 else []) + [g["A"] + t_l + np.cumsum(out)]
    xi = np.concatenate(parts); xi[-1] = g["R"]
    z, k_si, k_lb, k_pb, k_pt = _z_axis(g, min(h_p, g["h"] / 24.0))
    nr, nz = len(xi) - 1, len(z) - 1
    i_pad = n_r
    i_lin = n_r + 1 if t_l > 0 else n_r
    x_in = g["A"] + t_l
    xi_out = min(3.0 * g["A"], 0.5 * (x_in + g["R"]))

    def rmap(x, zz):
        k = _radius_factor(zz, g)
        if x <= x_in:
            return x * k
        if x >= xi_out:
            return x
        t = (x - x_in) / (xi_out - x_in)
        return x * (k + (1 - k) * t)

    def nid(i, k):
        return 1 + i + (nr + 1) * k

    nodes = np.array([(nid(i, k), rmap(xi[i], z[k]), z[k]) for k in range(nz + 1) for i in range(nr + 1)])
    els, mats = [], []
    for k in range(nz):
        for i in range(nr):
            els.append((nid(i, k), nid(i + 1, k), nid(i + 1, k + 1), nid(i, k + 1)))
            if k < k_si:
                mats.append(3)
            elif k < k_lb:
                mats.append(2)
            elif k < k_pb:                      # liner bottom layer
                mats.append(5 if i < i_lin else 2)
            else:
                mats.append(1 if i < i_pad else (5 if i < i_lin else 2))
    els, mats = np.array(els), np.array(mats)
    ce, dup = [], {}
    if run["side"] == "sliding":
        nxt, new = int(nodes[:, 0].max()) + 1, []
        nr_, nz_ = math.cos(g["theta"]), -math.sin(g["theta"])
        for k in range(k_pb + 1, k_pt + 1):
            n = nid(i_pad, k)
            dup[n] = nxt
            new.append((nxt, nodes[n - 1, 1], nodes[n - 1, 2]))
            ce.append((nxt, n, nr_, nz_))
            nxt += 1
        nodes = np.vstack([nodes, np.array(new)])
        cu = mats == 1
        els[cu] = np.vectorize(lambda v: dup.get(int(v), int(v)))(els[cu])
    top_ids = [dup.get(nid(i, nz), nid(i, nz)) for i in range(nr + 1)]
    cu_top = [dup.get(nid(i, nz), nid(i, nz)) for i in range(i_pad + 1)]
    return dict(dim=2, g=g, nodes=nodes, els=els, mats=mats, ce=ce, top=top_ids, cu_top=set(cu_top),
                n_nodes=len(nodes), n_elems=len(els), nr=nr, nz=nz, i_pad=i_pad, xi=xi, z=z,
                k=dict(k_si=k_si, k_lb=k_lb, k_pb=k_pb, k_pt=k_pt), nid=nid)


def mesh_3d(run):
    g = geometry(run)
    n_pad = 10 * run["refine"]
    h_p = 2 * g["A"] / n_pad
    C = g["L"] / 2.0
    t_l = g["t_l"]
    grad = M._graded(C - g["A"] - t_l, min(h_p, 3 * t_l) if t_l > 0 else h_p, run.get("grow3d", 1.25),
                     max(run.get("hmax3d", 0.22) * g["w"], h_p))
    outside = np.concatenate([[t_l], grad]) if t_l > 0 else grad
    inc = np.concatenate([outside[::-1], np.full(n_pad, h_p), outside])
    x = np.concatenate([[0.0], np.cumsum(inc)]); x[-1] = g["L"]
    i0 = len(outside); i1 = i0 + n_pad
    z, k_si, k_lb, k_pb, k_pt = _z_axis(g, min(h_p, g["h"] / 24.0), growth=run.get("grow3d", 1.25))
    nx = len(x) - 1; nz = len(z) - 1
    X0, Y0 = np.meshgrid(x, x, indexing="ij")
    u, v = (X0 - C) / g["A"], (Y0 - C) / g["A"]
    s = np.maximum(np.abs(u), np.abs(v))
    with np.errstate(invalid="ignore", divide="ignore"):
        su, sv = np.where(s > 0, u / s, 0.0), np.where(s > 0, v / s, 0.0)
        rr = np.hypot(su, sv)
        cu_, cv_ = np.where(rr > 0, su / rr, 0.0), np.where(rr > 0, sv / rr, 0.0)
    s_out = min(3.0, 0.999 * C / g["A"])
    t_in = np.clip((s - 0.5) / 0.5, 0.0, 1.0)
    t_out = np.clip((s - 1.0) / (s_out - 1.0), 0.0, 1.0)
    wgt = np.where(s <= 1.0, t_in, 1.0 - t_out)
    du = s * ((1 - wgt) * su + wgt * cu_)
    dv = s * ((1 - wgt) * sv + wgt * cv_)

    def nid(i, j, k):
        return 1 + i + (nx + 1) * (j + (nx + 1) * k)

    rows = []
    for k in range(nz + 1):
        kf = _radius_factor(z[k], g)
        blend = np.where(s <= 1.0, kf, np.where(s >= s_out, 1.0, kf + (1 - kf) * (s - 1.0) / (s_out - 1.0)))
        Xk = C + g["A"] * du * blend
        Yk = C + g["A"] * dv * blend
        for j in range(nx + 1):
            for i in range(nx + 1):
                rows.append((nid(i, j, k), Xk[i, j], Yk[i, j], z[k]))
    nodes = np.array(rows)
    ei, ej, ek = np.meshgrid(np.arange(nx), np.arange(nx), np.arange(nz), indexing="ij")
    ei, ej, ek = ei.ravel(), ej.ravel(), ek.ravel()
    conn = np.column_stack([nid(ei, ej, ek), nid(ei + 1, ej, ek), nid(ei + 1, ej + 1, ek), nid(ei, ej + 1, ek),
                            nid(ei, ej, ek + 1), nid(ei + 1, ej, ek + 1), nid(ei + 1, ej + 1, ek + 1),
                            nid(ei, ej + 1, ek + 1)])
    in_pad = (ei >= i0) & (ei < i1) & (ej >= i0) & (ej < i1)
    il0, il1 = (i0 - 1, i1 + 1) if t_l > 0 else (i0, i1)
    in_ring = (ei >= il0) & (ei < il1) & (ej >= il0) & (ej < il1) & ~in_pad
    pad_layer = ek >= k_pb
    liner_layer = (ek >= k_lb) & (ek < k_pb)
    mats = np.full(ei.shape, 2)
    mats[ek < k_si] = 3
    mats[pad_layer & in_pad] = 1
    if t_l > 0:
        mats[pad_layer & in_ring] = 5
        mats[liner_layer & (in_pad | in_ring)] = 5
    ce, dup = [], {}
    if run["side"] == "sliding":
        nxt, new = int(nodes[:, 0].max()) + 1, []
        ct, st = math.cos(g["theta"]), math.sin(g["theta"])
        for k in range(k_pb + 1, k_pt + 1):
            for i in range(i0, i1 + 1):
                for j in range(i0, i1 + 1):
                    if not (i in (i0, i1) or j in (i0, i1)):
                        continue
                    n = nid(i, j, k)
                    xx, yy = nodes[n - 1, 1] - C, nodes[n - 1, 2] - C
                    r_ = math.hypot(xx, yy)
                    dup[n] = nxt
                    new.append((nxt, nodes[n - 1, 1], nodes[n - 1, 2], nodes[n - 1, 3]))
                    ce.append((nxt, n, ct * xx / r_, ct * yy / r_, -st))
                    nxt += 1
        nodes = np.vstack([nodes, np.array(new)])
        cu = mats == 1
        conn[cu] = np.vectorize(lambda q: dup.get(int(q), int(q)))(conn[cu])
    top = [dup.get(nid(i, j, nz), nid(i, j, nz)) for j in range(nx + 1) for i in range(nx + 1)]
    cu_top = {dup.get(nid(i, j, nz), nid(i, j, nz)) for i in range(i0, i1 + 1) for j in range(i0, i1 + 1)}
    edge = [nid(i, j, nz) for j in range(nx + 1) for i in range(nx + 1) if i in (0, nx) or j in (0, nx)]
    return dict(dim=3, g=g, nodes=nodes, els=conn, mats=mats, ce=ce, top=top, cu_top=cu_top, edge=edge,
                n_nodes=len(nodes), n_elems=len(conn), C=C, k=dict(k_si=k_si, k_pb=k_pb, k_pt=k_pt, nz=nz))


# ---------------------------------------------------------------- materials and deck
def _f(v):
    return f"{v:.10g}"


def okoro_curve(T_C, scale=1.0):
    """Isotropic polycrystalline Cu flow curve (Okoro 2008 / Tsau 2022 Eq. 1): sigma = (193 - 0.185 T)(1 + eps_p^0.3), MPa.
    scale > 1: size-effect sensitivity (sub-um Cu yields higher than bulk films)."""
    s0 = scale * (193.0 - 0.185 * T_C)
    return [(e, s0 * (1.0 + e ** 0.3)) for e in S.EPS_P_GRID]


def material_lines(run, hill):
    d, info = [], {}
    if run["cu"] == "iso" and run.get("cu_T", False):
        temps = [25.0, 100.0, 200.0, 300.0, 400.0]
        hs = [L13.hill_cu(T) for T in temps]
        d += ["! ---- MAT 1: Cu isotropic Hill average, T-dependent (Chang & Himmel)", "MPTEMP",
              "MPTEMP,1," + ",".join(_f(T) for T in temps),
              "MPDATA,EX,1,1," + ",".join(_f(h["E_MPa"]) for h in hs), "MPDATA,PRXY,1,1," + ",".join(_f(h["nu"]) for h in hs), "MPTEMP"]
        info["Ez_GPa"] = hill["E_MPa"] / 1000.0; info["cu_T"] = [h["E_MPa"] for h in hs]
    elif run["cu"] == "iso":
        d += ["! ---- MAT 1: Cu isotropic Hill average", f"MP,EX,1,{_f(hill['E_MPa'])}", f"MP,PRXY,1,{_f(hill['nu'])}"]
        info["Ez_GPa"] = hill["E_MPa"] / 1000.0
    else:
        hkl = L13.ORIENT[run["orient"]]
        D = S.rotated_D(hkl, 0.0)
        vals = [D[i, j] for j in range(6) for i in range(j, 6)]
        d += [f"! ---- MAT 1: Cu anisotropic (paper constants), z || [{run['orient']}]", "TB,ANEL,1,1,,0", "TBTEMP,25"]
        for s_ in range(0, 21, 6):
            d.append(f"TBDATA,{s_ + 1}," + ",".join(_f(v) for v in vals[s_:s_ + 6]))
        info["Ez_GPa"] = S.Ez_check(S.sorted_hkl(hkl), 0.0) / 1000.0
    a = run["cu_alpha"]
    aip = run.get("cu_alpha_ip")
    if aip is None:
        d += [f"MP,ALPX,1,{_f(a)}", f"MP,ALPY,1,{_f(a)}", f"MP,ALPZ,1,{_f(a)}", f"MP,REFT,1,{_f(T_REF)}"]
    elif run["dim"] == 2:   # axisymmetric: X radial, Y axial (vertical), Z hoop
        d += [f"MP,ALPX,1,{_f(aip)}", f"MP,ALPY,1,{_f(a)}", f"MP,ALPZ,1,{_f(aip)}", f"MP,REFT,1,{_f(T_REF)}"]
    else:
        d += [f"MP,ALPX,1,{_f(aip)}", f"MP,ALPY,1,{_f(aip)}", f"MP,ALPZ,1,{_f(a)}", f"MP,REFT,1,{_f(T_REF)}"]
    if run["plastic"]:
        if run["cu"] != "iso":
            raise ValueError("plasticity only with isotropic Cu (pre-registration B5)")
        temps = sorted({25.0, 100.0, 200.0, 300.0, 400.0} | {float(t) for t in run["temps"]})
        d.append(f"TB,PLAS,1,{len(temps)},{len(S.EPS_P_GRID)},MISO")
        for T in temps:
            d.append(f"TBTEMP,{_f(T)}")
            for e, sg in okoro_curve(T, run.get("yield_scale", 1.0)):
                d.append(f"TBPT,DEFI,{_f(e)},{_f(sg)}")
        info["plastic"] = f"Okoro 2008 isotropic, T-dependent, scale {run.get('yield_scale', 1.0)}"
    E_d, a_d = run["E_d"], run["a_d"]
    nu_d = DIEL[run["diel"]]["PRXY"]
    d += [f"! ---- MAT 2: {run['diel']}", f"MP,EX,2,{_f(E_d)}", f"MP,PRXY,2,{_f(nu_d)}", f"MP,ALPX,2,{_f(a_d)}",
          f"MP,REFT,2,{_f(T_REF)}",
          "! ---- MAT 3: Si", f"MP,EX,3,{_f(SI['EX'])}", f"MP,PRXY,3,{_f(SI['PRXY'])}", f"MP,ALPX,3,{_f(SI['ALPX'])}",
          f"MP,REFT,3,{_f(T_REF)}",
          "! ---- MAT 5: Ta liner", f"MP,EX,5,{_f(run.get('E_liner', TA['EX']))}", f"MP,PRXY,5,{_f(TA['PRXY'])}", f"MP,ALPX,5,{_f(TA['ALPX'])}",
          f"MP,REFT,5,{_f(T_REF)}"]
    info.update(E_d=E_d, a_d=a_d, nu_d=nu_d, t_liner=run["t_liner"])
    return d, info


def build_deck(run):
    msh = mesh_2d(run) if run["dim"] == 2 else mesh_3d(run)
    if msh["n_nodes"] > 128_000 or msh["n_elems"] > 128_000:
        raise RuntimeError(f"{run['id']}: {msh['n_nodes']} nodes exceed the Student limit")
    g = msh["g"]
    hill = L13.hill_cu(T_REF)
    d = [f"/TITLE,Stage2 {run['id']} {run['ds']} w{run['w']} {run['side']} {run['cu']} {run['orient']}",
         "/NERR,200,10000000", "/PREP7"]
    if run["dim"] == 2:
        d += ["ET,1,PLANE182", "KEYOPT,1,1,2", "KEYOPT,1,3,1"]
    else:
        d += ["ET,1,SOLID185", "KEYOPT,1,2,3"]
    ml, info = material_lines(run, hill)
    d += ml
    d.append("! ---- nodes")
    if run["dim"] == 2:
        d += [f"N,{int(r[0])},{_f(r[1])},{_f(r[2])}" for r in msh["nodes"]]
    else:
        d += [f"N,{int(r[0])},{_f(r[1])},{_f(r[2])},{_f(r[3])}" for r in msh["nodes"]]
    d += ["TYPE,1", "ESYS,0"]
    for m in (1, 2, 3, 5):
        sel = msh["els"][msh["mats"] == m]
        if len(sel) == 0:
            continue
        d.append(f"MAT,{m}")
        d += ["E," + ",".join(str(int(v)) for v in e) for e in sel]
    if msh["ce"]:
        d.append("! ---- sliding sidewall: normal displacement tied")
        for q, c in enumerate(msh["ce"], start=1):
            if run["dim"] == 2:
                ncu, nox, a_r, a_z = c
                terms = [(ncu, "UX", a_r), (ncu, "UY", a_z), (nox, "UX", -a_r), (nox, "UY", -a_z)]
            else:
                ncu, nox, a_x, a_y, a_z = c
                terms = [(ncu, "UX", a_x), (ncu, "UY", a_y), (ncu, "UZ", a_z),
                         (nox, "UX", -a_x), (nox, "UY", -a_y), (nox, "UZ", -a_z)]
            terms = [t for t in terms if abs(t[2]) > 1e-12]
            d.append(f"CE,{q},0," + ",".join(f"{n},{lab},{_f(cf)}" for n, lab, cf in terms[:3]))
            if len(terms) > 3:
                d.append(f"CE,{q},," + ",".join(f"{n},{lab},{_f(cf)}" for n, lab, cf in terms[3:]))
    eps = 1e-6
    d += ["ALLSEL,ALL", "FINISH", "/SOLU", "ANTYPE,STATIC", "NLGEOM,OFF", f"TREF,{_f(T_REF)}",
          "OUTRES,ERASE", "OUTRES,ALL,LAST", "AUTOTS,ON", "KBC,0"]
    if run["plastic"]:
        d += ["NSUBST,10,200,5", "LNSRCH,ON", "NEQIT,50"]
    if run["dim"] == 2:
        d += [f"NSEL,S,LOC,X,{-eps},{eps}", "D,ALL,UX,0",
              f"NSEL,S,LOC,Y,{_f(-g['t_si'] - eps)},{_f(-g['t_si'] + eps)}", "D,ALL,UY,0",
              f"NSEL,S,LOC,X,{_f(g['R'] - eps)},{_f(g['R'] + eps)}", "CM,WOUT,NODE", "ALLSEL,ALL"]
    else:
        L = g["L"]
        d += [f"NSEL,S,LOC,X,{-eps},{eps}", "D,ALL,UX,0", f"NSEL,S,LOC,Y,{-eps},{eps}", "D,ALL,UY,0",
              f"NSEL,S,LOC,Z,{_f(-g['t_si'] - eps)},{_f(-g['t_si'] + eps)}", "D,ALL,UZ,0",
              f"NSEL,S,LOC,X,{_f(L - eps)},{_f(L + eps)}", "CM,WXP,NODE",
              f"NSEL,S,LOC,Y,{_f(L - eps)},{_f(L + eps)}", "CM,WYP,NODE", "ALLSEL,ALL"]
    temps = run["temps"]
    for ls, T in enumerate(temps, start=1):
        dT = T - T_REF
        d += [f"TIME,{ls}", f"BFUNIF,TEMP,{_f(T)}"]
        if run["dim"] == 2:
            d += ["CMSEL,S,WOUT", f"D,ALL,UX,{_f(SI['ALPX'] * dT * g['R'])}", "ALLSEL,ALL"]
        else:
            uw = SI["ALPX"] * dT * g["L"]
            d += ["CMSEL,S,WXP", f"D,ALL,UX,{_f(uw)}", "CMSEL,S,WYP", f"D,ALL,UY,{_f(uw)}", "ALLSEL,ALL"]
        d.append("SOLVE")
    d += ["FINISH", "/POST1", "RSYS,0"]
    top = msh["top"]
    nls = len(temps)
    d += [f"NT_={len(top)}", f"*DIM,TN,ARRAY,{len(top)}", f"*DIM,TU,ARRAY,{len(top)},{nls}", f"*DIM,RP,ARRAY,{nls},3"]
    d += [f"TN({i})={n}" for i, n in enumerate(top, start=1)]
    comp = "UY" if run["dim"] == 2 else "UZ"
    d += [f"*DO,LS_,1,{nls}", "SET,LS_,LAST", "*DO,II_,1,NT_", f"TU(II_,LS_)={comp}(TN(II_))", "*ENDDO", "RP(LS_,1)=LS_",
          "ESEL,S,MAT,,1", "ETABLE,SEQ,S,EQV", "ESORT,ETAB,SEQ,0", "*GET,TMP_,SORT,,MAX", "RP(LS_,3)=TMP_", "EUSORT"]
    if run["plastic"]:
        d += ["ETABLE,EPQ,EPPL,EQV", "ESORT,ETAB,EPQ,0", "*GET,TMP_,SORT,,MAX", "RP(LS_,2)=TMP_", "EUSORT"]
    else:
        d += ["RP(LS_,2)=0"]
    d += ["ALLSEL,ALL", "*ENDDO", "*CFOPEN,top_disp,txt",
          "*VWRITE,TN(1)," + ",".join(f"TU(1,{c})" for c in range(1, nls + 1)), f"({nls + 1}E22.13)", "*CFCLOS",
          "*CFOPEN,hist_plastic,txt", "*VWRITE,RP(1,1),RP(1,2),RP(1,3)", "(3E22.13)", "*CFCLOS",
          "*GET,NNODE,NODE,0,COUNT", "*GET,NELEM,ELEM,0,COUNT", "*CFOPEN,meta,txt", "*VWRITE,NNODE,NELEM",
          "(2E22.13)", "*CFCLOS", "FINISH", ""]
    text = "\n".join(d) + "\n"
    body = "\n".join(l for l in text.splitlines() if not l.startswith("/TITLE"))
    meta = dict(run=run, geometry=g, n_nodes=msh["n_nodes"], n_elems=msh["n_elems"], n_ce=len(msh["ce"]),
                temps=temps, T_ref=T_REF, mat=info, physics_sha256=hashlib.sha256(body.encode()).hexdigest())
    return text, meta, msh


# ---------------------------------------------------------------- post-processing
def u_history(run, outdir=None):
    outdir = outdir or RESULTS / run["id"]
    _, meta, msh = build_deck(run)
    A_ = np.loadtxt(outdir / "top_disp.txt", ndmin=2)
    ids = A_[:, 0].astype(int)
    U = A_[:, 1:] * 1000.0
    xyz = {int(r[0]): r[1:] for r in msh["nodes"]}
    g = msh["g"]
    cu = np.array([n in msh["cu_top"] for n in ids])
    rc50 = g["A"] / math.sqrt(2.0)                      # central 50 % of the pad area
    fh = run["afm_field"] / 2.0
    out = []
    if msh["dim"] == 2:
        r = np.array([xyz[n][0] for n in ids])
        oc = np.argsort(r[cu]); rc = r[cu][oc]
        oo = np.argsort(r[~cu]); ro = r[~cu][oo]
        i_ref = int(np.argmax(r))
        rq = np.linspace(0, rc50, 400); wq = rq                       # area weights 2 pi r dr
        rf = np.linspace(0, rc, 400) if False else np.linspace(0, g["A"], 400)
        fx = np.linspace(-min(fh, g["R"] / math.sqrt(2.0)), min(fh, g["R"] / math.sqrt(2.0)), 301)
        FX, FY = np.meshgrid(fx, fx); FR = np.hypot(FX, FY)
        mask = FR > g["A"] * 1.001
        for c in range(U.shape[1]):
            uc = U[cu, c][oc]
            uo = U[~cu, c][oo]
            u_c50 = float(np.sum(np.interp(rq, rc, uc) * wq) / np.sum(wq))
            u_full = float(np.sum(np.interp(rf, rc, uc) * rf) / np.sum(rf))
            u_ctr = float(uc[0])
            u_ref_edge = float(U[i_ref, c])
            u_ref_afm = float(np.interp(FR[mask], ro, uo).mean())
            out.append(dict(T=run["temps"][c], u_c50=u_c50 - u_ref_afm, u_ctr=u_ctr - u_ref_edge,
                            u_full=u_full - u_ref_afm, u_ctr_afm=u_ctr - u_ref_afm, ref_afm=u_ref_afm, ref_edge=u_ref_edge))
    else:
        from scipy.interpolate import LinearNDInterpolator
        C = msh["C"]
        P = np.array([xyz[n][:2] for n in ids]) - C
        edge = set(msh["edge"]); ie = np.array([n in edge for n in ids])
        gx = np.linspace(-rc50, rc50, 161); GX, GY = np.meshgrid(gx, gx); m50 = np.hypot(GX, GY) <= rc50
        gf = np.linspace(-g["A"], g["A"], 201); GFX, GFY = np.meshgrid(gf, gf); mfull = np.hypot(GFX, GFY) <= g["A"]
        fh2 = min(fh, C * 0.999)
        fx = np.linspace(-fh2, fh2, 151); FX, FY = np.meshgrid(fx, fx); mask = np.hypot(FX, FY) > g["A"] * 1.02
        for c in range(U.shape[1]):
            fcu = LinearNDInterpolator(P[cu], U[cu, c])
            fox = LinearNDInterpolator(P[~cu], U[~cu, c])
            u_c50 = float(np.nanmean(fcu(GX[m50], GY[m50])))
            u_full = float(np.nanmean(fcu(GFX[mfull], GFY[mfull])))
            u_ctr = float(fcu(0.0, 0.0))
            u_ref_edge = float(U[ie, c].mean())
            u_ref_afm = float(np.nanmean(fox(FX[mask], FY[mask])))
            out.append(dict(T=run["temps"][c], u_c50=u_c50 - u_ref_afm, u_ctr=u_ctr - u_ref_edge,
                            u_full=u_full - u_ref_afm, u_ctr_afm=u_ctr - u_ref_afm, ref_afm=u_ref_afm, ref_edge=u_ref_edge))
    base = out[0]
    for o in out:
        for k in ("u_c50", "u_ctr", "u_full", "u_ctr_afm"):
            o["d" + k] = o[k] - base[k]
    pl = np.loadtxt(outdir / "hist_plastic.txt", ndmin=2)
    return dict(hist=out, du_c50=out[-1]["du_c50"], du_ctr=out[-1]["du_ctr"], du_full=out[-1]["du_full"],
                eppl_max=float(pl[:, 1].max()), seqv_max=float(pl[:, 2].max()), Ez=meta["mat"]["Ez_GPa"])


def _check_files(outdir, nls):
    mntr = next(iter(outdir.glob("*.mntr")), None)
    lss = set()
    if mntr is not None:
        for line in mntr.read_text(errors="replace").splitlines():
            p = line.split()
            if len(p) > 6 and p[0].isdigit() and p[1].isdigit():
                lss.add(int(p[0]))
    out = next(iter(outdir.glob("*.out")), None)
    bad, n_err, completed = [], 0, False
    if out is not None:
        txt = out.read_text(errors="replace")
        bad = [pat for pat in ("SOLUTION NOT CONVERGED", "Solution not converged", "Run terminated") if pat in txt]
        n_err = txt.count("*** ERROR ***")           # transient iteration errors (bisected) are counted, not fatal
        completed = "RUN COMPLETED" in txt
    return dict(load_steps=sorted(lss), all_ok=(lss == set(range(1, nls + 1)) and not bad and completed), failures=bad,
                n_error_messages=n_err, run_completed=completed)


def log_line(text):
    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(f"- {_dt.datetime.now():%Y-%m-%d %H:%M} {text}\n")


def run_status(run):
    return "DONE" if (RESULTS / run["id"] / "record.json").exists() else "TODO"


def execute(ids, nproc=S.DEFAULT_NP, dry=False, force=False):
    for rid in ids:
        run = RUN_BY_ID[rid]
        outdir = RESULTS / rid
        if run_status(run) == "DONE" and not force and not dry:
            print(f"[{rid}] already done"); continue
        if run.get("kind") == "contact":
            text, meta = build_contact_deck(run)
        else:
            text, meta, _ = build_deck(run)
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / f"{rid}.dat").write_text(text)
        (outdir / "deck_meta.json").write_text(json.dumps(meta, indent=1, default=float))
        print(f"[{rid}] {run['note']}: {meta['n_nodes']} nodes, {meta['n_elems']} elems")
        if dry:
            continue
        for f in ("top_disp.txt", "hist_plastic.txt", "meta.txt", "contact.txt"):
            (outdir / f).unlink(missing_ok=True)
        info = S.run_batch(run, outdir, nproc)
        nls = len(run["temps"])
        chk = _check_files(outdir, nls)
        rec = dict(id=rid, exec=info, deck=meta, check=chk, ok=False)
        try:
            res = contact_result(run, outdir) if run.get("kind") == "contact" else u_history(run, outdir)
            rec.update(ok=True, result=res)
            if run.get("kind") == "contact":
                msg = f"exit {info['exit_code']}, wall {info['wall_s']:.0f} s, LS ok {chk['all_ok']}; " + \
                      "; ".join(f"T{r['T']:g}: Ac/A={r['area_frac']:.3f} p={r['p_mean_MPa']:.0f}MPa" for r in res["steps"])
            else:
                msg = (f"exit {info['exit_code']}, wall {info['wall_s']:.0f} s, LS ok {chk['all_ok']}; "
                       f"du_c50 {res['du_c50']:.3f} | du_ctr {res['du_ctr']:.3f} | du_full {res['du_full']:.3f} nm"
                       + (f", eppl_max {res['eppl_max']:.2e}" if run["plastic"] else ""))
        except Exception as exc:
            rec["error"] = f"{type(exc).__name__}: {exc}"
            msg = f"exit {info['exit_code']}: results not readable ({rec['error']})"
        print(f"[{rid}] {msg}")
        (outdir / "record.json").write_text(json.dumps(rec, indent=1, default=float))
        log_line(f"**{rid}** ({run['group']}) {run['note']} -> {msg}")


def load(rid):
    f = RESULTS / rid / "record.json"
    if not f.exists():
        return None
    rec = json.loads(f.read_text())
    return rec if rec.get("ok") else None


# ---------------------------------------------------------------- connection stage: two-wafer contact deck
def build_contact_deck(run):
    """2D axisymmetric, two mirrored wafers; dielectric faces share nodes; Cu-Cu frictional contact.
    Dishing: spherical cap of depth r0 at the pad centre, zero at the pad edge (Lhostis Fig 10 definition)."""
    base = dict(run)            # side "bonded" (default) or "sliding" (round-2 Lhostis test: relaxed sidewall, both wafers)
    msh = mesh_2d(base)
    ce_bot = msh["ce"]          # (dup_cu_node, dielectric_node, n_r, n_z) sidewall normal ties; empty when bonded
    g = msh["g"]; nodes = msh["nodes"].copy(); els = msh["els"]; mats = msh["mats"]
    nr, nz, i_pad, nid = msh["nr"], msh["nz"], msh["i_pad"], msh["nid"]
    k_pb, k_pt = msh["k"]["k_pb"], msh["k"]["k_pt"]
    r0 = run["recess"]                                    # um, per pad
    # depress the Cu column nodes linearly with height fraction
    for k in range(k_pb + 1, k_pt + 1):
        fr = (nodes[nid(0, k) - 1, 2] - g["zpb"]) / g["h"]
        for i in range(i_pad + 1):
            n = nid(i, k)
            x = nodes[n - 1, 1]
            xa = x / (g["A"] * _radius_factor(nodes[n - 1, 2], g))
            nodes[n - 1, 2] -= r0 * max(0.0, 1.0 - xa * xa) * fr
    N0 = int(nodes[:, 0].max())
    zb = g["zpt"]
    # top wafer: mirror; shared nodes for the non-Cu surface (i > i_pad, k = nz)
    top_map = {}
    new_nodes = []
    for k in range(nz + 1):
        for i in range(nr + 1):
            n = nid(i, k)
            if k == nz and i > i_pad:
                top_map[n] = n
            else:
                m = N0 + n
                top_map[n] = m
                new_nodes.append((m, nodes[n - 1, 1], 2 * zb - nodes[n - 1, 2]))
    for (nd, n, nr_, nz_) in ce_bot:              # mirror the duplicated (sliding) Cu sidewall nodes as well
        m = N0 + nd; top_map[nd] = m
        new_nodes.append((m, nodes[nd - 1, 1], 2 * zb - nodes[nd - 1, 2]))
    all_nodes = np.vstack([nodes, np.array(new_nodes)])
    els_top = np.array([[top_map[int(v)] for v in e[::-1]] for e in els])
    mats_top = np.where(mats == 1, 6, mats)
    hill = L13.hill_cu(T_REF)
    d = [f"/TITLE,Stage2 {run['id']} contact w{run['w']} r0 {r0 * 1000:g} nm T {run['T_anneal']}", "/NERR,200,10000000",
         "/PREP7", "ET,1,PLANE182", f"KEYOPT,1,1,{run.get('keyopt1', 2)}", "KEYOPT,1,3,1", "ET,2,TARGE169", "ET,3,CONTA172",
         f"KEYOPT,3,2,{run.get('keyopt2', 0)}", "KEYOPT,3,5,0", "KEYOPT,3,9,0", "KEYOPT,3,10,2", "KEYOPT,3,12,0", "R,1",
         f"RMODIF,1,3,{_f(run.get('fkn', 1.0))}"]
    ml, info = material_lines(run, hill)
    d += ml
    d += ["! ---- MAT 6: top-wafer Cu (same as MAT 1)", f"MP,EX,6,{_f(hill['E_MPa'])}", f"MP,PRXY,6,{_f(hill['nu'])}",
          f"MP,ALPX,6,{_f(run['cu_alpha'])}", f"MP,REFT,6,{_f(T_REF)}", f"MP,MU,6,{_f(run.get('mu', 0.3))}"]
    if run["plastic"]:
        temps = sorted({25.0, 100.0, 200.0, 300.0, 400.0, float(run["T_anneal"])})
        d.append(f"TB,PLAS,6,{len(temps)},{len(S.EPS_P_GRID)},MISO")
        for T in temps:
            d.append(f"TBTEMP,{_f(T)}")
            for e, sg in okoro_curve(T, run.get("yield_scale", 1.0)):
                d.append(f"TBPT,DEFI,{_f(e)},{_f(sg)}")
    d.append("! ---- nodes")
    d += [f"N,{int(r[0])},{_f(r[1])},{_f(r[2])}" for r in all_nodes]
    d += ["TYPE,1", "ESYS,0", "REAL,1"]
    for m in (1, 2, 3, 5):
        sel = els[mats == m]
        if len(sel):
            d.append(f"MAT,{m}"); d += ["E," + ",".join(str(int(v)) for v in e) for e in sel]
    for m in (6, 2, 3, 5):
        sel = els_top[mats_top == m]
        if len(sel):
            d.append(f"MAT,{m}"); d += ["E," + ",".join(str(int(v)) for v in e) for e in sel]
    dup_map = {n: nd for (nd, n, _, _) in ce_bot}
    bot_cu = [dup_map.get(nid(i, nz), nid(i, nz)) for i in range(i_pad + 1)]
    top_cu = [top_map[n] for n in bot_cu]
    if ce_bot:
        d.append("! ---- sliding sidewall (both wafers): Cu-side duplicate tied to the dielectric node by the normal displacement only")
        q = 0
        for (nd, n, nr_, nz_) in ce_bot:
            for (a, b, nzs) in ((nd, n, nz_), (top_map[nd], top_map[n], -nz_)):
                q += 1
                terms = [(a, "UX", nr_), (a, "UY", nzs), (b, "UX", -nr_), (b, "UY", -nzs)]
                terms = [tm for tm in terms if abs(tm[2]) > 1e-12]
                d.append(f"CE,{q},0," + ",".join(f"{nn},{lab},{_f(cf)}" for nn, lab, cf in terms[:3]))
                if len(terms) > 3:
                    d.append(f"CE,{q},," + ",".join(f"{nn},{lab},{_f(cf)}" for nn, lab, cf in terms[3:]))
    d += ["! ---- contact pair: target = bottom Cu top surface, contact = top Cu surface", "ESEL,S,MAT,,1", "NSEL,NONE"]
    d += [f"NSEL,A,NODE,,{n}" for n in bot_cu]
    d += ["TYPE,2", "REAL,1", "MAT,1", "ESURF", "ALLSEL,ALL", "ESEL,S,MAT,,6", "NSEL,NONE"]
    d += [f"NSEL,A,NODE,,{n}" for n in top_cu]
    d += ["TYPE,3", "REAL,1", "MAT,6", "ESURF", "ALLSEL,ALL"]
    eps = 1e-6
    ztop = 2 * zb + g["t_si"]
    d += ["FINISH", "/SOLU", "ANTYPE,STATIC", "NLGEOM,OFF", f"TREF,{_f(T_REF)}", "OUTRES,ERASE", "OUTRES,ALL,LAST",
          "AUTOTS,ON", "KBC,0", f"NSUBST,{run.get('nsub', 10)},200,{max(1, run.get('nsub', 10) // 2)}", "LNSRCH,ON", "NEQIT,50", "CNCHECK,AUTO",
          f"NSEL,S,LOC,X,{-eps},{eps}", "D,ALL,UX,0",
          f"NSEL,S,LOC,Y,{_f(-g['t_si'] - eps)},{_f(-g['t_si'] + eps)}", "D,ALL,UY,0",
          f"NSEL,S,LOC,X,{_f(g['R'] - eps)},{_f(g['R'] + eps)}", "CM,WOUT,NODE", "ALLSEL,ALL"]
    temps = run["temps"]
    for ls, T in enumerate(temps, start=1):
        dT = T - T_REF
        d += [f"TIME,{ls}", f"BFUNIF,TEMP,{_f(T)}", "CMSEL,S,WOUT", f"D,ALL,UX,{_f(SI['ALPX'] * dT * g['R'])}",
              "ALLSEL,ALL", "SOLVE"]
    nls = len(temps)
    d += ["FINISH", "/POST1", "RSYS,0", "ESEL,S,TYPE,,3", "*GET,EMIN_,ELEM,0,NUM,MIN", "*GET,EMAX_,ELEM,0,NUM,MAX",
          "NC_=EMAX_-EMIN_+1", f"*DIM,CT,ARRAY,NC_,{3 + 3 * nls}",
          "*VGET,CT(1,1),ELEM,EMIN_,ELIST", "*VGET,CT(1,2),ELEM,EMIN_,NODE,1", "*VGET,CT(1,3),ELEM,EMIN_,NODE,2",
          f"*DIM,RP,ARRAY,{nls},2"]
    for ls in range(1, nls + 1):
        c = 3 + 3 * (ls - 1)
        d += [f"SET,{ls},LAST", "ETABLE,CST,CONT,STAT", "ETABLE,CPR,CONT,PRES", "ETABLE,CGP,CONT,GAP",
              f"*VGET,CT(1,{c + 1}),ELEM,EMIN_,ETAB,CST", f"*VGET,CT(1,{c + 2}),ELEM,EMIN_,ETAB,CPR", f"*VGET,CT(1,{c + 3}),ELEM,EMIN_,ETAB,CGP"]
    d += ["*CFOPEN,contact,txt", "*VWRITE," + ",".join(f"CT(1,{j})" for j in range(1, 4 + 3 * nls)),
          f"({3 + 3 * nls}E20.11)", "*CFCLOS", "ALLSEL,ALL"]
    # Cu top-surface displacements of both pads (for u at contact)
    d += [f"NT_={len(bot_cu)}", f"*DIM,TN,ARRAY,{len(bot_cu)}", f"*DIM,TU,ARRAY,{len(bot_cu)},{2 * nls}"]
    d += [f"TN({i})={n}" for i, n in enumerate(bot_cu, start=1)]
    d += [f"*DIM,TM,ARRAY,{len(top_cu)}"] + [f"TM({i})={n}" for i, n in enumerate(top_cu, start=1)]
    d += [f"*DO,LS_,1,{nls}", "SET,LS_,LAST", "*DO,II_,1,NT_", "TU(II_,2*LS_-1)=UY(TN(II_))", "TU(II_,2*LS_)=UY(TM(II_))",
          "*ENDDO", "RP(LS_,1)=LS_", "ESEL,S,MAT,,1", "ESEL,A,MAT,,6"]
    if run["plastic"]:
        d += ["ETABLE,EPQ,EPPL,EQV", "ESORT,ETAB,EPQ,0", "*GET,TMP_,SORT,,MAX", "RP(LS_,2)=TMP_", "EUSORT"]
    else:
        d += ["RP(LS_,2)=0"]
    d += ["ALLSEL,ALL", "*ENDDO", "*CFOPEN,top_disp,txt",
          "*VWRITE,TN(1)," + ",".join(f"TU(1,{c})" for c in range(1, 2 * nls + 1)), f"({2 * nls + 1}E22.13)", "*CFCLOS",
          "*CFOPEN,hist_plastic,txt", "*VWRITE,RP(1,1),RP(1,2)", "(2E22.13)", "*CFCLOS",
          "*GET,NNODE,NODE,0,COUNT", "*GET,NELEM,ELEM,0,COUNT", "*CFOPEN,meta,txt", "*VWRITE,NNODE,NELEM",
          "(2E22.13)", "*CFCLOS", "FINISH", ""]
    text = "\n".join(d) + "\n"
    body = "\n".join(l for l in text.splitlines() if not l.startswith("/TITLE"))
    meta = dict(run=run, geometry=g, n_nodes=len(all_nodes), n_elems=2 * len(els), temps=temps, T_ref=T_REF, mat=info,
                node_xy={int(r[0]): [float(r[1]), float(r[2])] for r in all_nodes if int(r[0]) in set(bot_cu) | set(top_cu)},
                physics_sha256=hashlib.sha256(body.encode()).hexdigest())
    return text, meta


def contact_result(run, outdir):
    meta = json.loads((outdir / "deck_meta.json").read_text())
    xy = {int(k): v for k, v in meta["node_xy"].items()}
    CT = np.loadtxt(outdir / "contact.txt", ndmin=2)
    nls = len(run["temps"])
    g = meta["geometry"]
    A_pad = math.pi * g["A"] ** 2
    steps = []
    for ls in range(nls):
        c = 3 + 3 * ls
        n1, n2 = CT[:, 1].astype(int), CT[:, 2].astype(int)
        x1 = np.array([xy[n][0] for n in n1]); x2 = np.array([xy[n][0] for n in n2])
        xm = 0.5 * (x1 + x2); dl = np.abs(x2 - x1)
        dA = 2 * math.pi * xm * dl
        stat, pres, gap = CT[:, c], CT[:, c + 1], CT[:, c + 2]
        inc = stat >= 2
        Ac = float(dA[inc].sum())
        pm = float((pres[inc] * dA[inc]).sum() / Ac) if Ac > 0 else 0.0
        # radius extent of the contact zone
        rmax = float(xm[inc].max()) if inc.any() else 0.0
        rmin = float(xm[inc].min()) if inc.any() else 0.0
        steps.append(dict(T=run["temps"][ls], area_frac=Ac / A_pad, p_mean_MPa=pm, p_max_MPa=float(pres.max()),
                          r_contact_um=[rmin, rmax], gap_centre_nm=float(gap[np.argmin(xm)]) * 1000.0,
                          n_contact_elems=int(inc.sum())))
    pl = np.loadtxt(outdir / "hist_plastic.txt", ndmin=2)
    return dict(steps=steps, eppl_max=float(pl[:, 1].max()), A_pad_um2=A_pad)


# ---------------------------------------------------------------- CLI
def list_runs():
    for r in RUNS:
        print(f"{r['id']:5} {r['group']:3} {r['ds']:5} w={r['w']:<5g} h={r['h']:<5g} {r['dim']}D {r['cu']:5} "
              f"{str(r['orient']):5} {r['side']:7} {'pl' if r['plastic'] else 'el'} {run_status(r):5} {r['note']}")


def main(argv=None):
    sys.modules.setdefault("baseline", sys.modules[__name__])   # registry must fill THIS module instance
    import stage2_runs  # noqa: F401  registers runs
    import stage2_contact_runs  # noqa: F401
    import stage2_x_runs  # noqa: F401
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--case", default=None)
    ap.add_argument("--group", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--np", dest="nproc", type=int, default=S.DEFAULT_NP)
    a = ap.parse_args(argv)
    if a.list:
        list_runs(); return 0
    ids = []
    if a.case:
        ids = [s.strip() for s in a.case.split(",")]
    if a.group:
        ids += [r["id"] for r in RUNS if r["group"] in a.group.split(",")]
    if not ids:
        ap.error("--case or --group")
    print(f"{_dt.datetime.now():%Y-%m-%d %H:%M:%S} runs {ids}")
    execute(ids, a.nproc, a.dry_run, a.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
