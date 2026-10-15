r"""Stage 2 Phase 4: Lhostis relative test, recess extension (E30+).  Same contact model as E17-E24 (stage2_contact_runs._c:
2D axisymmetric, two mirrored wafers, Cu-Cu friction 0.3, isotropic Okoro plasticity, array cell 2.26 w, imec adopted
dielectric), 400 C, pads w = 0.72 and 0.40 um, h = 0.65 um.  Only the per-pad recess r changes.

Grid r = 10, 12, 14, ... nm until A_c(400 C) = 0 for each pad (E30, E31 = r 10 for 0.72 / 0.40; E32, E33 = r 12; ...),
then bisection between the last A_c > 0 and the first A_c = 0 recess to +/-0.5 nm (ids continue in execution order).
r_open = recess where A_c -> 0 (linear interpolation, stage2_report_tools definition); pre-registered ratio
r_open(0.40)/r_open(0.72) = 0.79 +/- 0.15.  One MAPDL solve at a time.

Usage: python src\stage2\stage2_lhostis_ext.py --step      # run the next needed solve(s) for both pads, then stop
       python src\stage2\stage2_lhostis_ext.py --auto      # loop until both pads are bisected to +/-0.5 nm
       python src\stage2\stage2_lhostis_ext.py --status    # table + ratio
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
import stage2_contact_runs as C  # noqa: E402
import stage2_x_runs  # noqa: E402,F401

OUT = B.RESULTS / "stage2"
STATE = OUT / "lhostis_ext_state.json"
PADS = (0.72, 0.40)
R_GRID = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 24.0, 28.0, 32.0]
TOL_NM = 0.5
FIRST_ID = 30


def state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return dict(next_id=FIRST_ID, runs=[])          # runs: [{id, w, r}]


def save(st):
    STATE.write_text(json.dumps(st, indent=1))


def ensure_registered(st):
    for r in st["runs"]:
        if r["id"] not in B.RUN_BY_ID:
            B.register([C._c(r["id"], r["w"], 0.65, r["r"], 400, f"contact Lhostis EXT w{r['w']:g} um r{r['r']:g} nm/pad T400")])


def points(w):
    """(recess_nm, Ac_hot) for every finished run of this pad, E17-E24 included."""
    pts = []
    for run in B.RUNS:
        if run.get("kind") != "contact" or abs(run["w"] - w) > 1e-6 or run["T_anneal"] != 400 or abs(run["h"] - 0.65) > 1e-6:
            continue
        rec = B.load(run["id"])
        if rec is None or not rec["check"]["all_ok"]:
            continue
        pts.append((run["recess"] * 1000.0, rec["result"]["steps"][1]["area_frac"], run["id"]))
    return sorted(pts)


def next_recess(w):
    """Next recess to solve for pad w, or None when bisected to TOL_NM."""
    pts = points(w)
    pos = [p for p in pts if p[1] > 1e-6]
    zero = [p for p in pts if p[1] <= 1e-6]
    if not zero:
        done = {p[0] for p in pts}
        for r in R_GRID:
            if r not in done:
                return r
        return None                                  # grid exhausted without A_c = 0
    r1 = zero[0][0]
    r0 = max(p[0] for p in pos if p[0] < r1) if any(p[0] < r1 for p in pos) else None
    if r0 is None:
        return None
    if r1 - r0 <= TOL_NM + 1e-9:
        return None
    return round((r0 + r1) / 2.0, 2)


def r_open(w):
    pts = points(w)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    for i in range(1, len(pts)):
        if ys[i] <= 1e-6 and ys[i - 1] > 1e-6:
            return xs[i - 1] + (xs[i] - xs[i - 1]) * ys[i - 1] / (ys[i - 1] - ys[i] + 1e-30), (xs[i - 1], xs[i])
    return float("nan"), None


def status(verbose=True):
    res = {}
    for w in PADS:
        ro, br = r_open(w)
        res[str(w)] = dict(points=[(p[0], p[1], p[2]) for p in points(w)], r_open_nm=ro, bracket_nm=br, next=next_recess(w))
        if verbose:
            print(f"w {w:.2f} um: " + ", ".join(f"r{p[0]:g}->{p[1]:.3f}({p[2]})" for p in points(w)) +
                  f" | r_open {ro:.2f} nm bracket {br} next {next_recess(w)}")
    # substitute metric (PI decision 2026-10-15, post hoc): r50 = recess at which A_c(400 C) = 0.5, linear interpolation.
    # r_open is unreachable with the spherical-cap dishing (rim recess = 0 -> rim contact at every recess, A_c ~ r^-1.2..-1.4).
    for w in PADS:
        pts = points(w); r50 = float("nan")
        for i in range(1, len(pts)):
            if pts[i][1] < 0.5 <= pts[i - 1][1]:
                x0, y0, x1, y1 = pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1]
                r50 = x0 + (x1 - x0) * (y0 - 0.5) / (y0 - y1)
        res[str(w)]["r50_nm"] = r50
    a50, b50 = res["0.4"]["r50_nm"], res["0.72"]["r50_nm"]
    if a50 == a50 and b50 == b50:
        res["ratio50_400_over_720"] = a50 / b50
        res["r50_note"] = ("reported number only, NOT a verdict (PI decision 2026-10-15, strict option): r50 was computed before "
                           "the metric choice; the pre-registered metric r_open is undefined for spherical-cap dishing")
        if verbose:
            print(f"r50 (reported, non-verdict): 0.40 um {a50:.2f} nm, 0.72 um {b50:.2f} nm, ratio {a50 / b50:.3f} "
                  f"(pre-registered band 0.79 +/- 0.15 shown for reference only)")
    a, b = res["0.4"]["r_open_nm"], res["0.72"]["r_open_nm"]
    if a == a and b == b:
        ratio = a / b
        res["ratio_400_over_720"] = ratio; res["lhostis_ratio"] = 0.79; res["tol"] = 0.15
        res["pass"] = bool(abs(ratio - 0.79) <= 0.15)
        if verbose:
            print(f"ratio r_open(0.40)/r_open(0.72) = {ratio:.3f} vs 0.79 +/- 0.15 -> {'PASS' if res['pass'] else 'FAIL'}")
    else:
        res["pass"] = "undetermined"
    json.dump(res, open(OUT / "lhostis_ext.json", "w"), indent=1, default=float)
    return res


def step(nproc):
    st = state(); ensure_registered(st)
    did = False
    for w in PADS:
        r = next_recess(w)
        if r is None:
            continue
        rid = f"E{st['next_id']}"
        st["next_id"] += 1; st["runs"].append(dict(id=rid, w=w, r=r)); save(st)
        B.register([C._c(rid, w, 0.65, r, 400, f"contact Lhostis EXT w{w:g} um r{r:g} nm/pad T400")])
        B.execute([rid], nproc)
        did = True
    return did


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", action="store_true")
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--np", dest="nproc", type=int, default=B.S.DEFAULT_NP)
    a = ap.parse_args(argv)
    st = state(); ensure_registered(st)
    if a.step:
        step(a.nproc)
    elif a.auto:
        while step(a.nproc):
            pass
    status()
    return 0


if __name__ == "__main__":
    sys.exit(main())
