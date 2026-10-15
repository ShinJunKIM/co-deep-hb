r"""Stage 2 connection-stage round 2 (docs/stage2_lhostis_round2_preregistration.md): E64-E69.
Metric V = (r_in/A)^2 (centre-void area fraction at 400 C). Rule A (width, held-out, bonded): V(0.11,0.22,2) >= V(0.36,0.22,2)+0.10.
Rule B (thickness, sliding sidewall): at r0 2 and 4 nm, V(0.22) >= V(0.65)+0.10 and V(0.65, r0 2) <= 0.05.
Usage: python src\stage2\stage2_lhostis_r2.py --run | --judge
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
import stage2_contact_runs as C  # noqa: E402
import stage2_x_runs  # noqa: E402,F401
import stage2_lhostis_tem as L1  # noqa: E402  (registers E52-E63; SIO2 constants)

OUT = B.RESULTS / "stage2"


def _mk(rid, w, h, r_nm, note, **kw):
    run = C._c(rid, w, h, r_nm, 400, note)
    run.update(diel="SiO2", t_liner=0.013, afm_field=3.5, **L1.SIO2); run.update(kw)
    return run


RUNS = [
    _mk("E64", 0.11, 0.22, 2.0, "contact Lhostis R2 width rule w0.11 um h0.22 r2 nm T400 SiO2 bonded"),
    _mk("E65", 0.11, 0.22, 2.0, "contact Lhostis R2 width rule w0.11 um h0.22 r2 nm T400 SiO2 bonded yield x3", yield_scale=3.0),
    _mk("E66", 0.36, 0.65, 2.0, "contact Lhostis R2 thickness rule SLIDING w0.36 h0.65 r2 nm T400 SiO2", side="sliding"),
    _mk("E67", 0.36, 0.22, 2.0, "contact Lhostis R2 thickness rule SLIDING w0.36 h0.22 r2 nm T400 SiO2", side="sliding"),
    _mk("E68", 0.36, 0.65, 4.0, "contact Lhostis R2 thickness rule SLIDING w0.36 h0.65 r4 nm T400 SiO2", side="sliding"),
    _mk("E69", 0.36, 0.22, 4.0, "contact Lhostis R2 thickness rule SLIDING w0.36 h0.22 r4 nm T400 SiO2", side="sliding"),
]
B.register([r for r in RUNS if r["id"] not in B.RUN_BY_ID])


def void_fraction(rid):
    """V = (r_in/A)^2 from the hot load step: r_in = inner radius of the contact ring (status >= 2)."""
    rec = B.load(rid)
    if rec is None:
        return None
    run = B.RUN_BY_ID[rid]; A = run["w"] / 2.0
    hot = rec["result"]["steps"][1]
    r_in = hot["r_contact_um"][0] if hot["area_frac"] > 0 else A
    return dict(V=min(1.0, (r_in / A) ** 2), Ac=hot["area_frac"], r_in=r_in, A=A)


def judge():
    V = {rid: void_fraction(rid) for rid in ["E55"] + [r["id"] for r in RUNS]}
    res = dict(V={k: v for k, v in V.items() if v})
    a_ok = None
    if V["E64"] and V["E55"]:
        a_ok = bool(V["E64"]["V"] >= V["E55"]["V"] + 0.10)
        res["rule_A_width"] = dict(V_011=V["E64"]["V"], V_036=V["E55"]["V"], passed=a_ok, x3_V=V["E65"]["V"] if V["E65"] else None)
    b_ok = None
    if all(V[k] for k in ("E66", "E67", "E68", "E69")):
        sep2 = V["E67"]["V"] - V["E66"]["V"]; sep4 = V["E69"]["V"] - V["E68"]["V"]
        b_ok = bool(sep2 >= 0.10 and sep4 >= 0.10 and V["E66"]["V"] <= 0.05)
        res["rule_B_thickness_sliding"] = dict(sep_r2=sep2, sep_r4=sep4, V_thick_r2=V["E66"]["V"], passed=b_ok,
                                               r4_only=bool(sep4 >= 0.10 and V["E66"]["V"] <= 0.05))
    res["verdict"] = ("A PASS & B PASS" if (a_ok and b_ok) else f"A {'PASS' if a_ok else 'FAIL'} & B {'PASS' if b_ok else 'FAIL'}") if (a_ok is not None and b_ok is not None) else "incomplete"
    json.dump(res, open(OUT / "lhostis_round2.json", "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--run", action="store_true"); ap.add_argument("--judge", action="store_true")
    ap.add_argument("--np", dest="nproc", type=int, default=B.S.DEFAULT_NP)
    a = ap.parse_args(argv)
    if a.run:
        B.execute([r["id"] for r in RUNS], a.nproc)
    judge()
    return 0


if __name__ == "__main__":
    sys.exit(main())
