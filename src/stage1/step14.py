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


def deck(c):
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
          "TIME,2", "CMSEL,S,ZTOP", f"D,ALL,UZ,{_f(eth + E_MECH_EL)}", "ALLSEL,ALL", "NSUBST,2", "SOLVE",
          "TIME,3", "CMSEL,S,ZTOP", f"D,ALL,UZ,{_f(eth + E_MECH_PL)}", "ALLSEL,ALL", "NSUBST,20,200,10", "SOLVE",
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


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--partA", action="store_true")
    ap.add_argument("--evalA", action="store_true")
    ap.add_argument("--partC", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.partA:
        part_a(a.dry_run)
    if a.evalA:
        eval_a()
    if a.partC:
        return part_c()
    return 0


if __name__ == "__main__":
    sys.exit(main())
