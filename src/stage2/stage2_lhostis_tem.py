r"""Stage 2 C: Lhostis 2024 TEM thickness test (docs/stage2_lhostis_tem_preregistration.md), runs E52-E57.
Same contact model as E01-E51 (stage2_contact_runs._c); inputs: w 0.36 um, h 0.65 / 0.22 um, SiO2 (NYCU adopted
E 59 GPa, alpha 1.0 ppm/K), Ta liner 13 nm, 400 C, dishing r = 2/4/6 nm per pad.
Usage: python src\stage2\stage2_lhostis_tem.py --run | --judge
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
SIO2 = dict(E_d=59000.0, a_d=1.0e-6)          # results/stage2/adopted_rev.json "nycu"
RUNS = []
k = 52
for h in (0.65, 0.22):
    for r_nm in (2.0, 4.0, 6.0):
        run = C._c(f"E{k}", 0.36, h, r_nm, 400, f"contact Lhostis TEM w0.36 um h{h:g} um r{r_nm:g} nm/pad T400 SiO2")
        run.update(diel="SiO2", t_liner=0.013, afm_field=3.5, **SIO2)
        RUNS.append(run); k += 1
# revision 1 (pre-registration section 5, reason committed before running): sub-um Cu yield x3 (round X size effect)
RUNS_REV = []
k = 58
for h in (0.65, 0.22):
    for r_nm in (2.0, 4.0, 6.0):
        run = C._c(f"E{k}", 0.36, h, r_nm, 400, f"contact Lhostis TEM REV1 yield x3 w0.36 um h{h:g} um r{r_nm:g} nm/pad T400 SiO2")
        run.update(diel="SiO2", t_liner=0.013, afm_field=3.5, yield_scale=3.0, **SIO2)
        RUNS_REV.append(run); k += 1
B.register([r for r in RUNS + RUNS_REV if r["id"] not in B.RUN_BY_ID])


def judge(runs=None, tag=""):
    runs = runs or RUNS
    ac = {}
    for r in runs:
        rec = B.load(r["id"])
        if rec is None:
            continue
        ac[(r["h"], r["recess"] * 1000)] = rec["result"]["steps"][1]["area_frac"]
    sep = {rr: (ac.get((0.65, rr)), ac.get((0.22, rr))) for rr in (2.0, 4.0, 6.0)}
    cond_i = all(a is not None and b is not None and b <= a - 0.30 for a, b in sep.values())
    cond_ii = ac.get((0.65, 4.0)) is not None and ac[(0.65, 4.0)] >= 0.90
    verdict = "PASS" if (cond_i and cond_ii) else ("thickness direction consistent, closure unconfirmed" if cond_i else
                                                   ("closure ok, thickness effect insufficient" if cond_ii else "FAIL"))
    res = dict(Ac=({f"h{h}_r{rr}": v for (h, rr), v in ac.items()}), separation={str(rr): (a, b, None if (a is None or b is None) else a - b) for rr, (a, b) in sep.items()},
               cond_i_separation_ge_0p30_all_r=bool(cond_i), cond_ii_thick_r4_ge_0p90=bool(cond_ii), verdict=verdict,
               void_fraction_thin_r4=None if ac.get((0.22, 4.0)) is None else 1 - ac[(0.22, 4.0)])
    json.dump(res, open(OUT / f"lhostis_tem_test{tag}.json", "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--run-rev", action="store_true", help="revision 1: yield x3 (E58-E63)")
    ap.add_argument("--judge", action="store_true")
    ap.add_argument("--np", dest="nproc", type=int, default=B.S.DEFAULT_NP)
    a = ap.parse_args(argv)
    if a.run:
        B.execute([r["id"] for r in RUNS], a.nproc)
    if a.run_rev:
        B.execute([r["id"] for r in RUNS_REV], a.nproc)
    if a.judge or a.run or a.run_rev:
        judge()
        judge(RUNS_REV, "_rev1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
