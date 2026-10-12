r"""
Stage 1 / Step 14: plasticity-path diagnosis (Part A) and evaluation of Parts B and C.
Pre-registration: docs/stage1_step14_plasticity.md.

Part A: one SOLID185 element (1 um cube, Cu with z || [001], uMKS) for every combination of
    elastic input   : ANEL (TB,ANEL) | AELS (TB,ELAS,,,,AELS) | ORTHO (MP EX/EY/EZ, PRxy, Gxy)
    KEYOPT(2)       : 0 (full integration, B-bar) | 3 (simplified enhanced strain, production)
    TB,PLAS MISO    : T1 (one temperature, variant 1 form) | T2 (two temperatures, variant 2/3 form)
    thermal strain  : off | on (MP,ALPX + heating 25 -> 400 C)
    NLGEOM          : OFF (production) for all; ON in addition for ANEL (cp_check used ON)
Load: LS1 free heating (or nothing), LS2 elastic uniaxial pull (mechanical strain 5e-4), LS3 pull to 1e-2.
Checks (< 1 %): thermal strain = alpha*dT; E_z = sigma/eps at LS2; sigma_z at LS3 = MISO curve(EPPL,EQV)
at the current temperature (T2 curve at 400 C = 0.8 x the 25 C curve, so the table is really exercised).

Usage (repo root):
    python src\stage1\step14.py --partA          # build + run all one-element cases, evaluate, recommend
    python src\stage1\step14.py --partA --dry-run
    python src\stage1\step14.py --evalA          # re-evaluate finished cases
    python src\stage1\step14.py --partC          # evaluate Part C (needs R40, R41, R50, R57, R53, R58)
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
import stage1_pipeline as S  # noqa: E402

OUT_A = S.RESULTS / "step14_partA"
ALPHA = S.CU_ALPHA_CONST
T0, T1 = 25.0, 400.0
E_MECH_EL, E_MECH_PL = 5e-4, 1e-2
FIT = S.LUDWICK_FITS[3]                     # pad-3 Ludwick midpoint: sigma0 143, K 675, N 0.685
SCALE_T2 = 0.8                              # 400 C curve of the two-temperature table


def curve(eps_p, T, plas):
    _, s0, K, N = FIT
    f = SCALE_T2 if (plas == "T2" and T >= T1 - 1e-9) else 1.0
    return f * (s0 + K * np.power(np.maximum(eps_p, 0.0), N))


def cases():
    out = []
    for el, k, pl, th in itertools.product(("ANEL", "AELS", "ORTHO"), (0, 3), ("T1", "T2"), ("off", "on")):
        out.append(dict(el=el, k=k, plas=pl, thermal=th, nlgeom="OFF"))
    for k, pl, th in itertools.product((0, 3), ("T1", "T2"), ("off", "on")):
        out.append(dict(el="ANEL", k=k, plas=pl, thermal=th, nlgeom="ON"))
    for i, c in enumerate(out, start=1):
        c["id"] = f"A{i:02d}"
    return out


def _f(v):
    return f"{v:.10g}"


def deck(c, kbc_fix=False):
    C = np.zeros((6, 6))
    C[:3, :3] = S.C12
    np.fill_diagonal(C[:3, :3], S.C11)
    C[3, 3] = C[4, 4] = C[5, 5] = S.C44
    vals = [C[i, j] for j in range(6) for i in range(j, 6)]
    Sm = np.linalg.inv(C)
    d = [f"/TITLE,Step14 {c['id']} {c['el']} K{c['k']} {c['plas']} thermal-{c['thermal']} NLGEOM-{c['nlgeom']}",
         "/PREP7", "ET,1,SOLID185", f"KEYOPT,1,2,{c['k']}"]
    if c["el"] == "ANEL":
        d += ["TB,ANEL,1,1,,0", "TBTEMP,25"] + [f"TBDATA,{s + 1}," + ",".join(_f(v) for v in vals[s:s + 6])
                                               for s in range(0, 21, 6)]
    elif c["el"] == "AELS":
        d += ["TB,ELAS,1,1,21,AELS", "TBTEMP,25"] + [f"TBDATA,{s + 1}," + ",".join(_f(v) for v in vals[s:s + 6])
                                                    for s in range(0, 21, 6)]
    else:
        E, nu = 1.0 / Sm[0, 0], -Sm[0, 1] / Sm[0, 0]
        for lab in ("EX", "EY", "EZ"):
            d.append(f"MP,{lab},1,{_f(E)}")
        for lab in ("PRXY", "PRYZ", "PRXZ"):
            d.append(f"MP,{lab},1,{_f(nu)}")
        for lab in ("GXY", "GYZ", "GXZ"):
            d.append(f"MP,{lab},1,{_f(S.C44)}")
    if c["thermal"] == "on":
        d += [f"MP,ALPX,1,{_f(ALPHA)}", f"MP,ALPY,1,{_f(ALPHA)}", f"MP,ALPZ,1,{_f(ALPHA)}", "MP,REFT,1,25"]
    grid = S.EPS_P_GRID
    if c["plas"] == "T1":
        d += [f"TB,PLAS,1,1,{len(grid)},MISO", "TBTEMP,25"]
        d += [f"TBPT,DEFI,{_f(e)},{_f(curve(e, T0, 'T1'))}" for e in grid]
    else:
        d += [f"TB,PLAS,1,2,{len(grid)},MISO"]
        for T in (T0, T1):
            d.append(f"TBTEMP,{_f(T)}")
            d += [f"TBPT,DEFI,{_f(e)},{_f(curve(e, T, 'T2'))}" for e in grid]
    T_end = T1 if c["thermal"] == "on" else T0
    eth = ALPHA * (T_end - T0) if c["thermal"] == "on" else 0.0
    d += ["BLOCK,0,1,0,1,0,1", "ESIZE,1", "MAT,1", "TYPE,1", "VMESH,ALL", "FINISH",
          "/SOLU", "ANTYPE,STATIC", f"NLGEOM,{c['nlgeom']}", "TREF,25", "OUTRES,ALL,ALL", "AUTOTS,ON",
          "NSEL,S,LOC,X,0", "D,ALL,UX,0", "NSEL,S,LOC,Y,0", "D,ALL,UY,0", "NSEL,S,LOC,Z,0", "D,ALL,UZ,0",
          "NSEL,S,LOC,Z,1", "CM,ZTOP,NODE", "ALLSEL,ALL",
          "TIME,1", f"BFUNIF,TEMP,{_f(T_end)}", "NSUBST,2", "SOLVE",
          "TIME,2", "CMSEL,S,ZTOP", f"D,ALL,UZ,{_f(eth + E_MECH_EL)}", "ALLSEL,ALL", "NSUBST,2",
          *(["KBC,1"] if kbc_fix else []), "SOLVE",
          "TIME,3", "CMSEL,S,ZTOP", f"D,ALL,UZ,{_f(eth + E_MECH_PL)}", "ALLSEL,ALL", "NSUBST,20,200,10",
          *(["KBC,0"] if kbc_fix else []), "SOLVE",
          "FINISH", "/POST1", "RSYS,0",
          "SET,1", "NTOP_=NODE(1,1,1)", "UX1=UX(NTOP_)", "UZ1=UZ(NTOP_)",
          "SET,2", "ETABLE,SZ,S,Z", "*GET,SZ2,ELEM,1,ETAB,SZ",
          "SET,3", "ETABLE,SZ,S,Z", "ETABLE,EPQ,EPPL,EQV", "*GET,SZ3,ELEM,1,ETAB,SZ", "*GET,EP3,ELEM,1,ETAB,EPQ",
          "*CFOPEN,one_elem,txt", "*VWRITE,UX1,UZ1,SZ2,SZ3,EP3", "(5E22.13)", "*CFCLOS", "FINISH", ""]
    return "\n".join(d) + "\n"


def evaluate(c, outdir):
    out = next(iter(outdir.glob("*.out")), None)
    txt = out.read_text(errors="replace") if out else ""
    errs = []
    if "*** ERROR ***" in txt:
        after = [l.strip() for l in txt.split("*** ERROR ***", 1)[1].splitlines()[1:6] if l.strip()]
        errs = [after[0] if after else "ERROR"]
    f = outdir / "one_elem.txt"
    rec = dict(c, runs=False, correct=False, error=errs[0] if errs else "")
    if not f.exists() or "*** ERROR ***" in txt:
        return rec
    ux1, uz1, sz2, sz3, ep3 = np.loadtxt(f, ndmin=1)[:5]
    rec["runs"] = True
    T_end = T1 if c["thermal"] == "on" else T0
    eth = ALPHA * (T_end - T0) if c["thermal"] == "on" else 0.0
    Ez = 1.0 / np.linalg.inv(np.array([[S.C11, S.C12, S.C12], [S.C12, S.C11, S.C12], [S.C12, S.C12, S.C11]]))[2, 2]
    e_th = (ux1 / eth - 1) if eth > 0 else 0.0
    e_E = sz2 / E_MECH_EL / Ez - 1
    e_s = sz3 / float(curve(ep3, T_end, c["plas"])) - 1 if ep3 > 0 else float("nan")
    rec.update(thermal_err=float(e_th), Ez_err=float(e_E), flow_err=float(e_s), eppl=float(ep3), sz3=float(sz3),
               correct=bool(abs(e_th) < 0.01 and abs(e_E) < 0.01 and ep3 > 0 and abs(e_s) < 0.01))
    return rec


def recommend(rows):
    """Pre-registered selection (doc Part A): production settings = KEYOPT 3, thermal on, NLGEOM OFF."""
    ok = {(r["el"], r["k"], r["plas"], r["thermal"], r["nlgeom"]) for r in rows if r["correct"]}
    for el in ("ANEL", "AELS", "ORTHO"):
        if (el, 3, "T1", "on", "OFF") in ok:
            t2 = (el, 3, "T2", "on", "OFF") in ok
            note = ("" if el != "ORTHO" else " (needs the ESYS crystal-frame route of G3 for rotated pads)")
            return f"{el} with KEYOPT(2)=3{note}; temperature-table MISO (variants 2/3) {'works' if t2 else 'FAILS'}"
    for el in ("ANEL", "AELS", "ORTHO"):
        if (el, 0, "T1", "on", "OFF") in ok:
            return (f"NO production-setting combination works. Only with KEYOPT(2)=0: {el}. "
                    "Stop: element formulation change needs a decision.")
    return "NOTHING works with thermal strain. Stop and list options (doc Part A)."


def part_a(dry, nproc=1):
    OUT_A.mkdir(parents=True, exist_ok=True)
    rows = []
    for c in cases():
        od = OUT_A / c["id"]
        od.mkdir(exist_ok=True)
        (od / f"{c['id']}.dat").write_text(deck(c))
        if dry:
            continue
        (od / "one_elem.txt").unlink(missing_ok=True)
        info = S.run_batch(dict(id=c["id"]), od, nproc)
        r = evaluate(c, od)
        r["exit"] = info["exit_code"]
        rows.append(r)
        print(f"{c['id']} {c['el']:5} K{c['k']} {c['plas']} thermal-{c['thermal']:3} NLGEOM-{c['nlgeom']:3} "
              f"runs={r['runs']} correct={r['correct']} {r['error'][:70]}")
    if not dry:
        write_a(rows)


def write_a(rows):
    keys = ["id", "el", "k", "plas", "thermal", "nlgeom", "runs", "correct", "thermal_err", "Ez_err", "flow_err",
            "eppl", "error"]
    p = S.RESULTS / "diagnostics" / "step14_partA.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(",".join(keys) + "\n" + "".join(",".join(str(r.get(k, "")).replace(",", ";") for k in keys) + "\n"
                                                 for r in rows))
    rec = recommend(rows)
    print("PART A RECOMMENDATION:", rec)
    (S.RESULTS / "diagnostics" / "step14_partA_recommendation.txt").write_text(rec + "\n")


def eval_a():
    rows = []
    for c in cases():
        od = OUT_A / c["id"]
        if od.exists():
            rows.append(evaluate(c, od))
    for r in rows:
        print(r["id"], r["el"], r["k"], r["plas"], r["thermal"], r["nlgeom"], r["runs"], r["correct"],
              {k: round(r[k], 4) for k in ("thermal_err", "Ez_err", "flow_err") if k in r}, r["error"][:60])
    write_a(rows)


def part_c():
    def du(rid):
        f = S.RESULTS / rid / "record.json"
        return json.loads(f.read_text())["result"]["du"] if f.exists() else None
    m = {9: 6.4, 3: 4.1}
    res = {}
    for pad, el, pl in ((9, "R40", "R57"), (3, "R41", "R50")):
        e, p = du(el), du(pl)
        if e is None or p is None:
            print(f"missing {el}/{pl}"); return 1
        closed = (e - p) / (e - m[pad])
        res[pad] = closed
        print(f"{pad} um: elastic {e:.3f}  plastic {p:.3f}  measured {m[pad]}  gap closed {100 * closed:+.1f} %")
    sup = all(v >= 0.5 for v in res.values())
    print("PART C: in-plane yielding hypothesis", "SUPPORTED" if sup else "NOT SUPPORTED")
    a, b = du("R53"), du("R58")
    if a and b:
        print(f"1 um [001] cell 6w -> 9w: {a:.3f} -> {b:.3f} nm ({100 * (b / a - 1):+.2f} %); "
              f"criterion < 2 %: {'met' if abs(b / a - 1) < 0.02 else 'NOT met'}")
    return 0


# ---------------------------------------------------------------- post-hoc (deviation 1 and 2, doc section A6)
# Deviation 1: in the thermal-on cases the top-face UZ constraint is NEW in LS2, so MAPDL ramps it from 0
# (not from the free-expansion value 6.19e-3): the first substep compresses the cube by ~2.8e-3 and it yields
# in compression before being pulled.  The E_z / flow checks of those cases are therefore invalid.
# Fix: KBC,1 (step) in LS2 so the +5e-4 increment is applied from the expanded state; LS3 ramps again (KBC,0).
# Deviation 2: ANEL+PLAS failed in batch for ALL 16 settings, including the cp_check settings (A25), although
# cp_check ran the same commands successfully through PyMAPDL.  X1-X3 separate deck content from run mode.
FIX_IDS = ("A10", "A12", "A14", "A16", "A18", "A20", "A22", "A24")   # thermal-on, AELS/ORTHO, NLGEOM OFF
OUT_F = S.RESULTS / "step14_partA_fix"


def _cp_deck(case):
    sys.path.insert(0, str(HERE.parent / "validation"))
    import cp_check as CP
    mat = json.loads((S.RESULTS / "validation_cp_check" / "results.json").read_text())["ludwick_material_commands"]
    return "\n".join(CP.deck(case, mat, 0.01, 100)) + "\n"


def _pymapdl(case, od, text):
    from ansys.mapdl.core import launch_mapdl
    (od / f"{case}.dat").write_text(text)
    m = launch_mapdl(exec_file=str(S.EXE), run_location=str(od), jobname=case, nproc=1,
                     additional_switches="-smp", override=True, start_timeout=180)
    err = None
    try:
        out = m.input(str(od / f"{case}.dat"))
    except Exception as e:
        out, err = f"{type(e).__name__}: {e}", f"{type(e).__name__}: {e}"
    (od / f"{case}.out").write_text(str(out), errors="replace")
    m.exit()
    return err


def part_a_fix():
    OUT_F.mkdir(parents=True, exist_ok=True)
    byid = {c["id"]: c for c in cases()}
    rows = []
    for cid in FIX_IDS:
        c = dict(byid[cid]); c["id"] = cid + "f"
        od = OUT_F / c["id"]; od.mkdir(exist_ok=True)
        (od / f"{c['id']}.dat").write_text(deck(c, kbc_fix=True))
        (od / "one_elem.txt").unlink(missing_ok=True)
        S.run_batch(dict(id=c["id"]), od, 1)
        r = evaluate(c, od); rows.append(r)
        print(c["id"], c["el"], c["k"], c["plas"], "runs", r["runs"], "correct", r["correct"],
              {k: round(r[k], 5) for k in ("thermal_err", "Ez_err", "flow_err") if k in r})
    diag = []
    od = OUT_F / "X1"; od.mkdir(exist_ok=True)                       # cp_check deck, batch
    (od / "X1.dat").write_text(_cp_deck("X1"))
    S.run_batch(dict(id="X1"), od, 1)
    diag.append(("X1", "cp_check deck (rotated ANEL+MISO)", "batch", od / "X1.out", od / "X1.crv"))
    od = OUT_F / "X2"; od.mkdir(exist_ok=True)                       # A25 deck, PyMAPDL
    e2 = _pymapdl("X2", od, deck(byid["A25"]))
    diag.append(("X2", "A25 deck (cp_check settings, [001] ANEL)", "pymapdl", od / "X2.out", od / "one_elem.txt"))
    od = OUT_F / "X3"; od.mkdir(exist_ok=True)                       # cp_check deck, PyMAPDL (replicate)
    e3 = _pymapdl("X3", od, _cp_deck("X3"))
    diag.append(("X3", "cp_check deck (rotated ANEL+MISO)", "pymapdl", od / "X3.out", od / "X3.crv"))
    lines = ["id,deck,mode,anel_plas_error,result_file"]
    for i, d, mode, out, res in diag:
        t = out.read_text(errors="replace") if out.exists() else ""
        lines.append(f"{i},{d},{mode},{'TB,PLAS table cannot work' in t},{res.exists()}")
        print(lines[-1])
    keys = ["id", "el", "k", "plas", "thermal", "nlgeom", "runs", "correct", "thermal_err", "Ez_err", "flow_err", "eppl"]
    dg = S.RESULTS / "diagnostics"
    (dg / "step14_partA_fix.csv").write_text(",".join(keys) + "\n" + "".join(
        ",".join(str(r.get(k, "")) for k in keys) + "\n" for r in rows))
    (dg / "step14_partA_modecheck.csv").write_text("\n".join(lines) + "\n")
    # pre-registered selection rule, applied to: original thermal-off rows + fixed thermal-on rows
    orig = [evaluate(c, OUT_A / c["id"]) for c in cases() if c["id"] not in FIX_IDS and (OUT_A / c["id"]).exists()]
    fixed = [dict(r, id=r["id"][:-1]) for r in rows]
    rec = recommend(orig + fixed)
    print("PART A RECOMMENDATION (after deviation 1):", rec)
    (dg / "step14_partA_recommendation_fix.txt").write_text(rec + "\n")
    return 0


# ---------------------------------------------------------------- Part B
# B0 gate: is TB,ELAS AELS read with the same 21-constant order as TB,ANEL for a ROTATED crystal?
# One element, every node prescribed u = eps.x (uniform general strain incl. shears), elastic only.
# Check sigma_FE = D eps (all 6 components, < 1e-4 of max|sigma|) for ANEL and AELS.
B0_EPS = np.array([1e-4, -2e-4, 3e-4, 1.5e-4, -1e-4, 2.5e-4])      # x y z xy yz xz, engineering shear
OUT_B0 = S.RESULTS / "step14_partB0"


def _b0_cases():
    out = []
    for lab, hkl in (("pad3", S.sorted_hkl(S.PADS[3]["hkl"])), ("pad10", S.sorted_hkl(S.PADS[10]["hkl"])),
                     ("111", (1.0, 1.0, 1.0))):
        for el in ("ANEL", "AELS"):
            out.append(dict(id=f"B0_{lab}_{el}", hkl=hkl, el=el))
    return out


def b0_deck(c):
    D = S.rotated_D(c["hkl"], 0.0)
    vals = [D[i, j] for j in range(6) for i in range(j, 6)]
    tb = "TB,ELAS,1,1,21,AELS" if c["el"] == "AELS" else "TB,ANEL,1,1,,0"
    e = B0_EPS
    H = np.array([[e[0], e[3] / 2, e[5] / 2], [e[3] / 2, e[1], e[4] / 2], [e[5] / 2, e[4] / 2, e[2]]])
    d = [f"/TITLE,Step14 {c['id']}", "/PREP7", "ET,1,SOLID185", tb, "TBTEMP,25"]
    d += [f"TBDATA,{s + 1}," + ",".join(_f(v) for v in vals[s:s + 6]) for s in range(0, 21, 6)]
    d += ["BLOCK,0,1,0,1,0,1", "ESIZE,1", "VMESH,ALL", "FINISH", "/SOLU", "ANTYPE,STATIC"]
    for x in (0, 1):
        for y in (0, 1):
            for z in (0, 1):
                u = H @ np.array([x, y, z], float)
                d.append(f"NN_=NODE({x},{y},{z})")
                d += [f"D,NN_,{lab},{_f(v)}" for lab, v in zip(("UX", "UY", "UZ"), u)]
    d += ["SOLVE", "FINISH", "/POST1", "SET,LAST"]
    for k in ("X", "Y", "Z", "XY", "YZ", "XZ"):
        d += [f"ETABLE,S{k},S,{k}", f"*GET,S{k}_,ELEM,1,ETAB,S{k}"]
    d += ["*CFOPEN,b0,txt", "*VWRITE,SX_,SY_,SZ_,SXY_,SYZ_,SXZ_", "(6E22.13)", "*CFCLOS", "FINISH", ""]
    return "\n".join(d) + "\n"


def part_b0():
    OUT_B0.mkdir(parents=True, exist_ok=True)
    lines = ["id,el,orientation,runs,max_rel_err,pass"]
    allok = True
    for c in _b0_cases():
        od = OUT_B0 / c["id"]; od.mkdir(exist_ok=True)
        (od / f"{c['id']}.dat").write_text(b0_deck(c))
        (od / "b0.txt").unlink(missing_ok=True)
        S.run_batch(dict(id=c["id"]), od, 1)
        ref = S.rotated_D(c["hkl"], 0.0) @ B0_EPS
        if (od / "b0.txt").exists():
            fe = np.loadtxt(od / "b0.txt")[:6]
            err = float(np.max(np.abs(fe - ref)) / np.max(np.abs(ref)))
            ok = err < 1e-4
        else:
            err, ok = float("nan"), False
        allok &= ok
        lines.append(f"{c['id']},{c['el']},{c['id'].split('_')[1]},{(od / 'b0.txt').exists()},{err:.3e},{ok}")
        print(lines[-1])
    lines.append(f"GATE,,,,,{'PASS' if allok else 'FAIL'}")
    (S.RESULTS / "diagnostics" / "step14_partB0.csv").write_text("\n".join(lines) + "\n")
    print("PART B0 GATE:", "PASS" if allok else "FAIL")
    return 0 if allok else 1


def part_b():
    def rec(rid):
        f = S.RESULTS / rid / "record.json"
        return json.loads(f.read_text()) if f.exists() else None
    def u(r, tag):
        return next(x["u_center_nm"] for x in r["rows"] if x["tag"] == tag)
    r35, r60 = rec("R35"), rec("R60")
    # B2 addendum: R59 diverged in LS1 -> use R61 (same physics + LNSRCH/NEQIT) if R59 is not fully converged
    pid = next((k for k in ("R59", "R61") if rec(k) and rec(k).get("all_converged")), None)
    r59 = rec(pid) if pid else None
    r62 = rec("R62")
    if r62:
        print(f"diagnostic R62 (isotropic Hill elastic + same plasticity): all converged = {r62.get('all_converged')}")
    if not (r35 and r60):
        print("missing R35/R60"); return 1
    if r59 is None:
        print("no converged plastic run (R59, R61) -> Part B: NO VERDICT; stop and list options (doc B2)")
        (S.RESULTS / "diagnostics" / "step14_partB.txt").write_text("no converged plastic run (R59, R61): no verdict\n")
        return 1
    out = []
    g = abs(u(r60, "h400") - u(r35, "h400"))
    gate = g < 1e-3
    out.append(f"gate R60 (AELS elastic) vs R35 (ANEL elastic) at 400 C: |diff| = {g:.2e} nm -> {'PASS' if gate else 'FAIL'}")
    e, pl = u(r35, "h400"), u(r59, "h400")
    d3 = pl - e
    epmax = max(x.get("eppl_eqv_max", 0.0) or 0.0 for x in r59["rows"])
    out.append(f"plastic run used: {pid}")
    out.append(f"pad 3: elastic {e:.4f}  plastic {pl:.4f}  diff {d3:+.4f} nm  (max EPPL {epmax:.2e}; "
               f"all converged {r59.get('all_converged')})")
    out.append(f"pad 3 residual at 30 C after the cycle: elastic {u(r35, 'c030'):+.4f}  plastic {u(r59, 'c030'):+.4f} nm")
    out.append("pad 10: E_z 189.5 GPa > 130.34 GPa -> elastic by mapping rule, diff = 0 (no solve)")
    elastic = gate and abs(d3) < 0.1
    out.append("PART B RULE: " + ("|diff| < 0.1 nm for both pads -> Stage 2 uses ELASTIC Cu" if elastic else
               ("gate failed -> no verdict" if not gate else "|diff| >= 0.1 nm -> Stage 2 uses PLASTIC Cu")))
    print("\n".join(out))
    (S.RESULTS / "diagnostics" / "step14_partB.txt").write_text("\n".join(out) + "\n")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--partA", action="store_true")
    ap.add_argument("--evalA", action="store_true")
    ap.add_argument("--partC", action="store_true")
    ap.add_argument("--partA-fix", dest="partA_fix", action="store_true")
    ap.add_argument("--partB0", action="store_true")
    ap.add_argument("--partB", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.partA:
        part_a(a.dry_run)
    if a.evalA:
        eval_a()
    if a.partA_fix:
        part_a_fix()
    if a.partB0:
        return part_b0()
    if a.partB:
        return part_b()
    if a.partC:
        return part_c()
    return 0


if __name__ == "__main__":
    sys.exit(main())
