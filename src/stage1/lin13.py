r"""
Stage 1 / Step 13: reproduction of the measured Cu protrusion of Lin et al., Appl. Surf. Sci. 689 (2025) 162539.

Separate module (own meshes, decks and registry R40-R56) so that the Ayoub decks R01-R39 built by
stage1_pipeline.py are untouched. Pre-registration: docs/stage1_step13_lin_reproduction.md.

Geometry (um, uMKS units: um, MPa, 1/K):
    Si          -t_si .. 0
    SiO2 under   0    .. Z_OX          (assumed 0.5 um, Fig. 3a shows >= 0.44 um)
    pad layer   Z_OX .. Z_OX + H       (Cu frustum in SiO2; top width w, side taper theta from vertical)
Pads: 9 um / 1.15 um, 3 um / 1.5 um, 1 um / 1.5 um (Table 1). Isolated pad: cell width = 3 w (check run: 6 w).
9 and 3 um: 2D axisymmetric (PLANE182, KEYOPT(3)=1), isotropic Hill-average Cu.
1 um: 3D (SOLID185) full square cell, circular O-grid pad, anisotropic Cu (TB,ANEL, rotated to global).

u(T) = mean UZ over the central square (side w/2) of the Cu top surface - mean UZ of the SiO2 top surface at the
cell edge; du = u(200 C) - u(25 C).

Usage (repo root):
    python src\stage1\lin13.py --list
    python src\stage1\lin13.py --case R40,R41 [--dry-run] [--force]
    python src\stage1\lin13.py --case all
    python src\stage1\lin13.py --compare          # pass/fail table -> results/diagnostics/step13_lin.csv
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import s1_mesh as M          # noqa: E402  (only the grading helpers are reused)
import stage1_pipeline as S  # noqa: E402  (materials, rotation, flow curves, MAPDL runner)

REPO = S.REPO
RESULTS = S.RESULTS

# ---------------------------------------------------------------- inputs fixed by the pre-registration
TEMPS = [25.0, 50.0, 100.0, 150.0, 200.0]          # RT -> 200 C in 50 C steps (Lin Sec. 2.2); RT = 25 C
T_REF = 25.0                                        # stress-free temperature (elastic: du independent of it)
Z_OX = 0.5                                          # SiO2 under the pad (ASSUMPTION, Fig. 3a >= 0.44 um)
TAPER_DEG = 7.6                                     # from Table 1 frustum volumes of the 3 and 1 um pads
PADS_LIN = {9: dict(w=9.0, h=1.15), 3: dict(w=3.0, h=1.5), 1: dict(w=1.0, h=1.5)}
MEASURED = {9: dict(du=6.4, tol=0.4, kind="single"), 3: dict(du=4.1, lo=3.6, hi=4.9, kind="array"),
            1: dict(du=2.3, tol=0.4, kind="single")}
ORIENT = {"001": (0.0, 0.0, 1.0), "101": (1.0, 0.0, 1.0), "111": (1.0, 1.0, 1.0)}
AFM_FIELD = {9: 25.0, 3: 8.0, 1: 3.5}               # AFM scan field (Fig. 5), report-only reference


def hill_cu(T_C=25.0):
    """Isotropic Hill (VRH) Cu from Chang & Himmel (inputs/cu_elastic_constants_vs_T.csv), interpolated in T."""
    rows = S._read_csv_rows(S.CSV_ELASTIC_T)
    T = np.array([float(r["T_C"]) for r in rows])
    c11, c12, c44 = (np.array([float(r[k]) for r in rows]) for k in ("C11_GPa", "C12_GPa", "C44_GPa"))
    Tq = max(T_C, T.min())                       # table starts at 26.85 C: 25 C uses the 26.85 C row
    c11, c12, c44 = (float(np.interp(Tq, T, v)) for v in (c11, c12, c44))
    K = (c11 + 2 * c12) / 3
    Gv = (c11 - c12 + 3 * c44) / 5
    Gr = 5 * (c11 - c12) * c44 / (4 * c44 + 3 * (c11 - c12))
    G = 0.5 * (Gv + Gr)
    E = 9 * K * G / (3 * K + G)
    nu = (3 * K - 2 * G) / (2 * (3 * K + G))
    return dict(E_MPa=E * 1000.0, nu=nu, G_GPa=G, K_GPa=K, T_used=Tq, C=(c11, c12, c44))


# ---------------------------------------------------------------- registry
def _run(rid, pad, dim, note, **kw):
    d = dict(id=rid, pad=pad, dim=dim, note=note, side="bonded", cu="iso", orient=None, plastic=False,
             cell_factor=3.0, taper=TAPER_DEG, refine=1, role="primary")
    d.update(kw)
    return d


RUNS = [
    _run("R40", 9, 2, "LIN 9 um bonded, 2D axisym, iso Hill"),
    _run("R41", 3, 2, "LIN 3 um bonded, 2D axisym, iso Hill"),
    _run("R42", 1, 2, "LIN 1 um bonded, 2D axisym, iso Hill (3D-verification + taper reference)", role="check"),
    _run("R43", 1, 3, "LIN 1 um bonded, 3D, Cu [001]", cu="aniso", orient="001"),
    _run("R44", 1, 3, "LIN 1 um bonded, 3D, Cu [101]", cu="aniso", orient="101"),
    _run("R45", 1, 3, "LIN 1 um bonded, 3D, Cu [111]", cu="aniso", orient="111"),
    _run("R46", 9, 2, "LIN 9 um SLIDING control, 2D", side="sliding", role="control"),
    _run("R47", 3, 2, "LIN 3 um SLIDING control, 2D", side="sliding", role="control"),
    _run("R48", 1, 3, "LIN 1 um SLIDING control, 3D, Cu [001]", side="sliding", cu="aniso", orient="001", role="control"),
    _run("R49", 1, 3, "LIN 1 um bonded PLASTIC (Ludwick v1), 3D, Cu [001]", cu="aniso", orient="001", plastic=True,
         role="plastic"),
    _run("R50", 3, 2, "LIN 3 um bonded PLASTIC (Ludwick v1, E_Hill mapping), 2D", plastic=True, role="plastic"),
    _run("R51", 9, 2, "LIN 9 um bonded, cell x2 (6 w) and Si x2", cell_factor=6.0, role="cell"),
    _run("R52", 3, 2, "LIN 3 um bonded, cell x2", cell_factor=6.0, role="cell"),
    _run("R53", 1, 3, "LIN 1 um bonded [001], cell x2", cu="aniso", orient="001", cell_factor=6.0, role="cell"),
    _run("R54", 1, 2, "LIN 1 um bonded iso 2D, taper 18 deg (108 deg annotation) - sensitivity", taper=18.0,
         role="taper"),
    _run("R55", 1, 3, "LIN 1 um bonded iso 3D - verification vs R42 (2D)", role="check"),
    _run("R56", 3, 2, "LIN 3 um bonded 2D, mesh refined x2 - mesh check", refine=2, role="mesh"),
    # step 14 (docs/stage1_step14_plasticity.md), Part C
    _run("R57", 9, 2, "LIN 9 um bonded PLASTIC (Ludwick v1, E_Hill mapping), 2D", plastic=True, role="plastic"),
    _run("R58", 1, 3, "LIN 1 um bonded [001], cell x3 (9 w) - next cell step", cu="aniso", orient="001",
         cell_factor=9.0, role="cell"),
]
RUN_BY_ID = {r["id"]: r for r in RUNS}


def geometry(run):
    p = PADS_LIN[run["pad"]]
    w, h = p["w"], p["h"]
    A = w / 2.0
    L = run["cell_factor"] * w                  # cell width (3D) / 2 R (2D)
    t_si = L                                    # Si thickness = cell width (scaled with the cell check)
    th = math.radians(run["taper"])
    a_bot = A - h * math.tan(th)
    if a_bot <= 0.02 * A:
        raise ValueError(f"{run['id']}: taper {run['taper']} deg leaves no pad bottom")
    return dict(w=w, h=h, A=A, L=L, R=L / 2.0, t_si=t_si, zpb=Z_OX, zpt=Z_OX + h, theta=th, a_bot=a_bot)


def _radius_factor(z, g):
    """a(z)/A inside the pad layer (linear taper, wider at the top); constant below the pad bottom."""
    zc = min(max(z, g["zpb"]), g["zpt"])
    return (g["A"] - (g["zpt"] - zc) * math.tan(g["theta"])) / g["A"]


def _z_axis(g, h_p, growth=1.2):
    si = M._graded(g["t_si"], h_p, growth, max(g["t_si"] / 6, h_p))[::-1]
    ox = M._symmetric_graded(g["zpb"], h_p, growth, 4 * h_p)
    pad = M._symmetric_graded(g["h"], h_p, growth, 2.5 * h_p)
    inc = np.concatenate([si, ox, pad])
    z = np.concatenate([[-g["t_si"]], -g["t_si"] + np.cumsum(inc)])
    k_si, k_pb = len(si), len(si) + len(ox)
    k_pt = k_pb + len(pad)
    z[k_si], z[k_pb], z[k_pt] = 0.0, g["zpb"], g["zpt"]
    return z, k_si, k_pb, k_pt


# ---------------------------------------------------------------- 2D axisymmetric mesh
def mesh_2d(run):
    g = geometry(run)
    n_r = 40 * run["refine"]
    h_p = g["A"] / n_r
    xi_pad = np.linspace(0.0, g["A"], n_r + 1)
    out = M._graded(g["R"] - g["A"], h_p, 1.15, max((g["R"] - g["A"]) / 10, h_p))
    xi = np.concatenate([xi_pad, g["A"] + np.cumsum(out)]); xi[-1] = g["R"]
    z, k_si, k_pb, k_pt = _z_axis(g, min(h_p, g["h"] / 24.0))
    nr, nz = len(xi) - 1, len(z) - 1
    i_pad = n_r                                   # grid line of the sidewall
    xi_out = min(3.0 * g["A"], 0.5 * (g["A"] + g["R"]))

    def rmap(x, zz):
        k = _radius_factor(zz, g)
        if x <= g["A"]:
            return x * k
        if x >= xi_out:
            return x
        t = (x - g["A"]) / (xi_out - g["A"])
        return x * (k + (1 - k) * t)

    def nid(i, k):
        return 1 + i + (nr + 1) * k

    nodes = [(nid(i, k), rmap(xi[i], z[k]), z[k]) for k in range(nz + 1) for i in range(nr + 1)]
    nodes = np.array(nodes)
    els, mats = [], []
    for k in range(nz):
        for i in range(nr):
            els.append((nid(i, k), nid(i + 1, k), nid(i + 1, k + 1), nid(i, k + 1)))
            if k < k_si:
                mats.append(3)
            elif k < k_pb:
                mats.append(2)
            else:
                mats.append(1 if i < i_pad else 2)
    els, mats = np.array(els), np.array(mats)
    ce = []
    if run["side"] == "sliding":
        dup, nxt, new = {}, int(nodes[:, 0].max()) + 1, []
        nr_, nz_ = math.cos(g["theta"]), -math.sin(g["theta"])   # outward sidewall normal in (r, z)
        for k in range(k_pb + 1, k_pt + 1):                      # bottom rim stays shared (bonded bottom)
            n = nid(i_pad, k)
            dup[n] = nxt
            new.append((nxt, nodes[n - 1, 1], nodes[n - 1, 2]))
            ce.append((nxt, n, nr_, nz_))
            nxt += 1
        nodes = np.vstack([nodes, np.array(new)])
        cu = mats == 1
        els[cu] = np.vectorize(lambda v: dup.get(int(v), int(v)))(els[cu])
    else:
        dup = {}
    top_ids = [dup.get(nid(i, nz), nid(i, nz)) for i in range(nr + 1)]
    cu_top = [dup.get(nid(i, nz), nid(i, nz)) for i in range(i_pad + 1)]
    return dict(dim=2, g=g, nodes=nodes, els=els, mats=mats, ce=ce, top=top_ids, cu_top=set(cu_top),
                axis=[nid(0, k) for k in range(nz + 1)], outer=[nid(nr, k) for k in range(nz + 1)],
                bottom=[nid(i, 0) for i in range(nr + 1)], n_nodes=len(nodes), n_elems=len(els))


# ---------------------------------------------------------------- 3D mesh (square cell, circular pad, taper)
def mesh_3d(run):
    g = geometry(run)
    n_pad = 10 * run["refine"]
    h_p = 2 * g["A"] / n_pad
    C = g["L"] / 2.0
    outside = M._graded(C - g["A"], h_p, 1.25, max(0.22 * g["w"], h_p))
    inc = np.concatenate([outside[::-1], np.full(n_pad, h_p), outside])
    x = np.concatenate([[0.0], np.cumsum(inc)]); x[-1] = g["L"]
    i0 = len(outside); i1 = i0 + n_pad
    z, k_si, k_pb, k_pt = _z_axis(g, min(h_p, g["h"] / 24.0), growth=1.25)
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
    mats = np.where(ek < k_si, 3, np.where(ek < k_pb, 2, np.where(in_pad, 1, 2)))
    ce = []
    dup = {}
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


# ---------------------------------------------------------------- deck
def _f(v):
    return f"{v:.10g}"


def build_deck(run):
    msh = mesh_2d(run) if run["dim"] == 2 else mesh_3d(run)
    if msh["n_nodes"] > 128_000 or msh["n_elems"] > 128_000:
        raise RuntimeError(f"{run['id']}: {msh['n_nodes']} nodes exceed the Student limit")
    g = msh["g"]
    hill = hill_cu(T_REF)
    info = dict(hill=hill)
    d = [f"/TITLE,Step13 {run['id']} Lin pad {run['pad']} um {run['side']} {run['cu']} {run['orient']}",
         "/NERR,200,10000000", "/PREP7"]
    if run["dim"] == 2:
        d += ["ET,1,PLANE182", "KEYOPT,1,1,2", "KEYOPT,1,3,1        ! axisymmetric, enhanced strain"]
    else:
        d += ["ET,1,SOLID185", "KEYOPT,1,2,3"]
    # Cu
    if run["cu"] == "iso":
        d += ["! ---- MAT 1: Cu isotropic Hill average (Chang & Himmel, 26.85 C row)",
              f"MP,EX,1,{_f(hill['E_MPa'])}", f"MP,PRXY,1,{_f(hill['nu'])}"]
        Ez = hill["E_MPa"] / 1000.0
    else:
        hkl = ORIENT[run["orient"]]
        D = S.rotated_D(hkl, 0.0)
        vals = [D[i, j] for j in range(6) for i in range(j, 6)]
        d += [f"! ---- MAT 1: Cu anisotropic (paper constants), z || [{run['orient']}]", "TB,ANEL,1,1,,0", "TBTEMP,25"]
        for s_ in range(0, 21, 6):
            d.append(f"TBDATA,{s_ + 1}," + ",".join(_f(v) for v in vals[s_:s_ + 6]))
        Ez = S.Ez_check(S.sorted_hkl(hkl), 0.0) / 1000.0
    info["Ez_GPa"] = Ez
    d += [f"MP,ALPX,1,{_f(S.CU_ALPHA_CONST)}", f"MP,ALPY,1,{_f(S.CU_ALPHA_CONST)}", f"MP,ALPZ,1,{_f(S.CU_ALPHA_CONST)}"]
    d.append(f"MP,REFT,1,{_f(T_REF)}")
    if run["plastic"]:
        fc = S.flow_curve_for(None, Ez)
        if fc is None:
            raise ValueError(f"{run['id']}: E = {Ez:.1f} GPa is elastic by the mapping rule")
        info["flow_rule"] = fc["rule"]
        d.append(f"TB,PLAS,1,1,{len(S.EPS_P_GRID)},MISO")
        d.append("TBTEMP,25")
        for e, sg in zip(S.EPS_P_GRID, fc["curve"]):
            d.append(f"TBPT,DEFI,{_f(e)},{_f(sg)}")
    for m, p, name in ((2, S.OXIDE, "SiO2"), (3, S.SILICON, "Si")):
        d += [f"! ---- MAT {m}: {name}", f"MP,EX,{m},{_f(p['EX'])}", f"MP,PRXY,{m},{_f(p['PRXY'])}",
              f"MP,ALPX,{m},{_f(p['ALPX'])}", f"MP,REFT,{m},{_f(T_REF)}"]
    d.append("! ---- nodes")
    if run["dim"] == 2:
        d += [f"N,{int(r[0])},{_f(r[1])},{_f(r[2])}" for r in msh["nodes"]]
    else:
        d += [f"N,{int(r[0])},{_f(r[1])},{_f(r[2])},{_f(r[3])}" for r in msh["nodes"]]
    d += ["TYPE,1", "ESYS,0"]
    for m in (1, 2, 3):
        d.append(f"MAT,{m}")
        d += ["E," + ",".join(str(int(v)) for v in e) for e in msh["els"][msh["mats"] == m]]
    if msh["ce"]:
        d.append("! ---- frictionless sidewall, normal displacement tied (no separation)")
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
        d.append("NSUBST,10,100,5")
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
    for ls, T in enumerate(TEMPS, start=1):
        dT = T - T_REF
        d += [f"TIME,{ls}", f"BFUNIF,TEMP,{_f(T)}"]
        if run["dim"] == 2:
            d += ["CMSEL,S,WOUT", f"D,ALL,UX,{_f(S.SILICON['ALPX'] * dT * g['R'])}", "ALLSEL,ALL"]
        else:
            uw = S.SILICON["ALPX"] * dT * g["L"]
            d += ["CMSEL,S,WXP", f"D,ALL,UX,{_f(uw)}", "CMSEL,S,WYP", f"D,ALL,UY,{_f(uw)}", "ALLSEL,ALL"]
        d.append("SOLVE")
    d += ["FINISH", "/POST1", "RSYS,0"]
    top = msh["top"]
    nls = len(TEMPS)
    d += [f"NT_={len(top)}", f"*DIM,TN,ARRAY,{len(top)}", f"*DIM,TU,ARRAY,{len(top)},{nls}",
          f"*DIM,RP,ARRAY,{nls},2"]
    d += [f"TN({i})={n}" for i, n in enumerate(top, start=1)]
    comp = "UY" if run["dim"] == 2 else "UZ"
    d += [f"*DO,LS_,1,{nls}", "SET,LS_,LAST", "*DO,II_,1,NT_", f"TU(II_,LS_)={comp}(TN(II_))", "*ENDDO",
          "RP(LS_,1)=LS_"]
    if run["plastic"]:
        d += ["ESEL,S,MAT,,1", "ETABLE,EPQ,EPPL,EQV", "ESORT,ETAB,EPQ,0", "*GET,TMP_,SORT,,MAX", "RP(LS_,2)=TMP_",
              "EUSORT", "ALLSEL,ALL"]
    else:
        d += ["RP(LS_,2)=0"]
    d += ["*ENDDO", "*CFOPEN,top_disp,txt",
          "*VWRITE,TN(1)," + ",".join(f"TU(1,{c})" for c in range(1, nls + 1)), f"({nls + 1}E22.13)", "*CFCLOS",
          "*CFOPEN,hist_plastic,txt", "*VWRITE,RP(1,1),RP(1,2)", "(2E22.13)", "*CFCLOS",
          "*GET,NNODE,NODE,0,COUNT", "*GET,NELEM,ELEM,0,COUNT", "*CFOPEN,meta,txt", "*VWRITE,NNODE,NELEM",
          "(2E22.13)", "*CFCLOS", "FINISH", ""]
    text = "\n".join(d) + "\n"
    body = "\n".join(l for l in text.splitlines() if not l.startswith("/TITLE"))
    meta = dict(run=run, geometry=g, n_nodes=msh["n_nodes"], n_elems=msh["n_elems"], n_ce=len(msh["ce"]),
                temps=TEMPS, T_ref=T_REF, mat=info, physics_sha256=hashlib.sha256(body.encode()).hexdigest())
    return text, meta, msh


# ---------------------------------------------------------------- post-processing (pre-registered definition)
def u_history(run, outdir=None):
    outdir = outdir or RESULTS / run["id"]
    _, meta, msh = build_deck(run)
    A = np.loadtxt(outdir / "top_disp.txt", ndmin=2)
    ids = A[:, 0].astype(int)
    U = A[:, 1:] * 1000.0                         # um -> nm
    xyz = {int(r[0]): r[1:] for r in msh["nodes"]}
    g = msh["g"]
    s = g["w"] / 4.0                               # central square half-side (side = w/2)
    gx = np.linspace(-s, s, 201)
    GX, GY = np.meshgrid(gx, gx)
    cu = np.array([n in msh["cu_top"] for n in ids])
    out = []
    if msh["dim"] == 2:
        r = np.array([xyz[n][0] for n in ids])
        oc = np.argsort(r[cu])
        rc = r[cu][oc]
        R_ = np.hypot(GX, GY)
        i_ref = int(np.argmax(r))
        # report-only: SiO2 mean over the AFM field (square of side AFM_FIELD) outside the pad
        fh = min(AFM_FIELD[run["pad"]] / 2.0, g["R"] / math.sqrt(2.0))
        fx = np.linspace(-fh, fh, 301)
        FX, FY = np.meshgrid(fx, fx)
        FR = np.hypot(FX, FY)
        mask = FR > g["A"] * 1.02
        ro = r[~cu]; oo = np.argsort(ro)
        for c in range(U.shape[1]):
            uc = U[cu, c][oc]
            u_cu = float(np.interp(R_, rc, uc).mean())
            u_ref = float(U[i_ref, c])
            u_afm = float(np.interp(FR[mask], ro[oo], U[~cu, c][oo]).mean())
            out.append(dict(T=TEMPS[c], u_cu=u_cu, u_ref=u_ref, u=u_cu - u_ref, u_afm=u_cu - u_afm))
    else:
        from scipy.interpolate import LinearNDInterpolator
        C = msh["C"]
        P = np.array([xyz[n][:2] for n in ids]) - C
        edge = set(msh["edge"])
        ie = np.array([n in edge for n in ids])
        fh = min(AFM_FIELD[run["pad"]] / 2.0, C)
        fx = np.linspace(-fh * 0.999, fh * 0.999, 151)
        FX, FY = np.meshgrid(fx, fx)
        mask = np.hypot(FX, FY) > g["A"] * 1.05
        for c in range(U.shape[1]):
            u_cu = float(np.nanmean(LinearNDInterpolator(P[cu], U[cu, c])(GX, GY)))
            u_ref = float(U[ie, c].mean())
            u_afm = float(np.nanmean(LinearNDInterpolator(P[~cu], U[~cu, c])(FX[mask], FY[mask])))
            out.append(dict(T=TEMPS[c], u_cu=u_cu, u_ref=u_ref, u=u_cu - u_ref, u_afm=u_cu - u_afm))
    du = out[-1]["u"] - out[0]["u"]
    du_afm = out[-1]["u_afm"] - out[0]["u_afm"]
    pl = np.loadtxt(outdir / "hist_plastic.txt", ndmin=2) if (outdir / "hist_plastic.txt").exists() else None
    return dict(hist=out, du=du, du_afm_ref=du_afm, eppl_max=None if pl is None else float(pl[:, 1].max()),
                Ez=meta["mat"]["Ez_GPa"])


# ---------------------------------------------------------------- execution
def run_status(run):
    return "DONE" if (RESULTS / run["id"] / "record.json").exists() else "TODO"


def list_runs():
    print(f"{'run':4} {'pad':>4} {'dim':>3} {'side':8} {'Cu':6} {'role':8} status  note")
    for r in RUNS:
        print(f"{r['id']:4} {r['pad']:>4} {r['dim']:>3} {r['side']:8} {(r['orient'] or 'iso'):6} {r['role']:8} "
              f"{run_status(r):6}  {r['note']}")


def _check_files(outdir, rid):
    mntr = next(iter(outdir.glob("*.mntr")), None)
    lss = set()
    if mntr is not None:
        for line in mntr.read_text(errors="replace").splitlines():
            p = line.split()
            if len(p) > 6 and p[0].isdigit() and p[1].isdigit():
                lss.add(int(p[0]))
    out = next(iter(outdir.glob("*.out")), None)
    bad = []
    if out is not None:
        txt = out.read_text(errors="replace")
        bad = [pat for pat in ("SOLUTION NOT CONVERGED", "not converged", "*** ERROR ***") if pat in txt]
    return dict(load_steps=sorted(lss), all_ok=(lss == set(range(1, len(TEMPS) + 1)) and not bad), failures=bad)


def execute(ids, nproc, dry, force):
    for rid in ids:
        run = RUN_BY_ID[rid]
        outdir = RESULTS / rid
        if run_status(run) == "DONE" and not force and not dry:
            print(f"[{rid}] already done (use --force to re-run)"); continue
        text, meta, _ = build_deck(run)
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / f"{rid}.dat").write_text(text)
        (outdir / "deck_meta.json").write_text(json.dumps(meta, indent=1, default=float))
        print(f"[{rid}] {run['note']}: {meta['n_nodes']} nodes, {meta['n_elems']} elements, CE {meta['n_ce']}, "
              f"E_z = {meta['mat']['Ez_GPa']:.2f} GPa")
        if dry:
            continue
        for f in ("top_disp.txt", "hist_plastic.txt", "meta.txt"):
            (outdir / f).unlink(missing_ok=True)
        info = S.run_batch(run, outdir, nproc)
        chk = _check_files(outdir, rid)
        rec = dict(id=rid, exec=info, deck=meta, check=chk, ok=False)
        try:
            res = u_history(run, outdir)
            rec.update(ok=True, result=res)
            print(f"[{rid}] exit {info['exit_code']}, wall {info['wall_s']:.1f} s, all load steps {chk['all_ok']}; "
                  f"du(25->200) = {res['du']:.3f} nm" + (f", max eppl {res['eppl_max']:.2e}" if run["plastic"] else ""))
        except Exception as exc:
            rec["error"] = f"{type(exc).__name__}: {exc}"
            print(f"[{rid}] exit {info['exit_code']}: results not readable ({rec['error']})")
        (outdir / "record.json").write_text(json.dumps(rec, indent=1, default=float))


# ---------------------------------------------------------------- pre-registered comparison
def compare():
    res = {}
    for r in RUNS:
        f = RESULTS / r["id"] / "record.json"
        if f.exists():
            rec = json.loads(f.read_text())
            if rec.get("ok"):
                res[r["id"]] = rec["result"]
    need = ["R40", "R41", "R43", "R44", "R45", "R46", "R47", "R48"]
    miss = [i for i in need if i not in res]
    if miss:
        print("missing runs:", miss); return 1
    du = {k: v["du"] for k, v in res.items()}
    b9, b3 = du["R40"], du["R41"]
    b1 = [du["R43"], du["R44"], du["R45"]]
    p9 = abs(b9 - 6.4) <= 0.4
    p3 = 3.6 <= b3 <= 4.9
    p1 = (min(b1) <= 2.3 + 0.4) and (max(b1) >= 2.3 - 0.4)
    trend = b9 > b3 > max(b1)
    passed = p9 and p3 and p1 and trend
    s9, s3, s1 = du["R46"], du["R47"], du["R48"]
    sp = (abs(s9 - 6.4) <= 0.4) and (3.6 <= s3 <= 4.9) and (abs(s1 - 2.3) <= 0.4) and (s9 > s3 > s1)
    rows = [("9 um", "iso (Hill)", b9, s9, "6.4 +/- 0.4", p9), ("3 um", "iso (Hill)", b3, s3, "3.6-4.9", p3)]
    for rid, o in (("R43", "[001]"), ("R44", "[101]"), ("R45", "[111]")):
        rows.append(("1 um", o, du[rid], s1 if rid == "R43" else float("nan"), "2.3 +/- 0.4", p1))
    lines = ["pad,orientation,bonded_du_nm,sliding_du_nm,measured,pass_bonded"]
    print(f"{'pad':5} {'orientation':11} {'bonded':>8} {'sliding':>8}  {'measured':12} pass")
    for p, o, b, s_, m, ok in rows:
        print(f"{p:5} {o:11} {b:8.3f} {s_:8.3f}  {m:12} {ok}")
        lines.append(f"{p},{o},{b:.4f},{s_:.4f},{m},{ok}")
    print(f"size trend bonded 9 > 3 > 1: {trend}")
    print("STEP 13 PRIMARY VERDICT (bonded):", "PASS" if passed else "FAIL")
    print("sliding control:", "PASSES too -> test cannot discriminate the sidewall condition" if sp else "FAILS")
    extra = {k: res[k]["du"] for k in ("R42", "R49", "R50", "R51", "R52", "R53", "R54", "R55", "R56") if k in res}
    for k, v in extra.items():
        print(f"  report-only {k} ({RUN_BY_ID[k]['role']}): du = {v:.3f} nm  [{RUN_BY_ID[k]['note']}]")
    for a, b, lab in (("R51", "R40", "cell 9 um"), ("R52", "R41", "cell 3 um"), ("R53", "R43", "cell 1 um"),
                      ("R55", "R42", "3D vs 2D (1 um iso)"), ("R56", "R41", "mesh x2 (3 um)"),
                      ("R54", "R42", "taper 18 vs 7.6 deg (1 um iso)")):
        if a in du and b in du:
            print(f"  {lab}: {du[a]:.3f} vs {du[b]:.3f} nm -> {100 * (du[a] / du[b] - 1):+.1f} %")
    afm = {k: res[k]["du_afm_ref"] for k in need}
    print("  report-only du with SiO2 reference = AFM-field mean:", {k: round(v, 3) for k, v in afm.items()})
    out = RESULTS / "diagnostics" / "step13_lin.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines += [f"# {k},{RUN_BY_ID[k]['role']},{v:.4f}" for k, v in extra.items()]
    lines += [f"# verdict_bonded,{'PASS' if passed else 'FAIL'}", f"# trend,{trend}", f"# sliding_passes,{sp}"]
    out.write_text("\n".join(lines) + "\n")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Step 13: Lin 2025 protrusion reproduction")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--case", default=None)
    ap.add_argument("--np", dest="nproc", type=int, default=S.DEFAULT_NP)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--compare", action="store_true")
    a = ap.parse_args(argv)
    if a.list:
        list_runs(); return 0
    if a.compare:
        return compare()
    if not a.case:
        ap.error("give --list, --case or --compare")
    ids = [r["id"] for r in RUNS] if a.case == "all" else [s.strip() for s in a.case.split(",")]
    bad = [i for i in ids if i not in RUN_BY_ID]
    if bad:
        ap.error(f"unknown run ids {bad}")
    if not a.dry_run and not S.EXE.exists():
        print(f"MAPDL executable not found: {S.EXE}"); return 2
    print(f"{_dt.datetime.now():%Y-%m-%d %H:%M:%S}  runs: {ids}  np={a.nproc}  exe={S.EXE}")
    execute(ids, a.nproc, a.dry_run, a.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
