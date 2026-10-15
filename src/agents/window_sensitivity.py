r"""Response to the adversarial review (docs/agents/review_adversarial.md), items 1-3: window / open-pair floor / ranking
sensitivity to (a) the faceted fraction (omega_c 5 deg -> 1.5 %, 12.8 deg -> 10 %), (b) the diffusion model used
(revision 1 without orientation, theta_eff 113.6; round 2 with orientation, theta_eff 119), (c) recess N(2.0, 1.0^2).
Also prints the relaxed-interface elastic upper bound (SD10N/SD3N) against the recess sum.  No ANSYS.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "stage2"))
import stage2_window as W  # noqa: E402

REPO = HERE.parents[1]; OUT = REPO / "results" / "stage2"
coef = np.array(json.loads((OUT / "predict_0.30um_fit.json").read_text())["fit"]["coef"])
N = 200_000


def run(label, theta, oc, dw, facet=True, recess=(2.5, 0.5), s_ox=1.0):
    pr = W.Pairs(N, 0, coef, oc, dw, recess=recess, facet=facet)
    w = W.window(pr, 300.0, 0.69, s_ox, 1.0, theta, 60.0, 20.7); c = W.cells(w)
    floor = {k: 1 - w[k] for k in ((250, 120), (300, 30), (350, 30), (400, 30))}
    rank_mech = len(W.cells(W.window(pr, 300.0, 0.69, s_ox, 1.0, theta, 60.0, 20.7, diffusion=False)) ^ c)
    print(f"{label:52s} window {len(c):2d}/15  open-pair floor: " + " ".join(f"{T}C/{t}m {v:.1e}" for (T, t), v in floor.items())
          + f"  | mech cells {rank_mech}")
    return c, floor


res = {}
res["round2 (theta 119, oc 5, dw 19.5; faceted 1.5 %)"] = run("round2 theta119 oc5 dw19.5 (faceted 1.5 %)", 119.0, 5.0, 19.5)
res["round2 oc 12.8 (faceted 10 %)"] = run("round2 theta119 oc12.8 dw19.5 (faceted 10 %)", 119.0, 12.8, 19.5)
res["round2 oc 12.8 dw 10"] = run("round2 theta119 oc12.8 dw10 (faceted 10 %, sharper)", 119.0, 12.8, 10.0)
res["revision1 (theta 113.6, no orientation)"] = run("revision1 theta113.6 no orientation", 113.6, 5.0, 19.5, facet=False)
res["round2 no facet (fg-Cu proxy)"] = run("round2 theta119 f=1 (fg-Cu proxy)", 119.0, 5.0, 19.5, facet=False)
res["round2 recess N(2.0,1.0)"] = run("round2 oc5, recess N(2.0, 1.0^2)", 119.0, 5.0, 19.5, recess=(2.0, 1.0))
res["round2 oc12.8 recess N(2.0,1.0)"] = run("round2 oc12.8, recess N(2.0, 1.0^2)", 119.0, 12.8, 19.5, recess=(2.0, 1.0))
res["round2 oxidised"] = run("round2 oc5 oxidised", 119.0, 5.0, 19.5, s_ox=0.45)
res["round2 oc12.8 oxidised"] = run("round2 oc12.8 oxidised", 119.0, 12.8, 19.5, s_ox=0.45)
base = res["round2 (theta 119, oc 5, dw 19.5; faceted 1.5 %)"][0]
for k, (c, f) in res.items():
    print(f"  {k:45s} cells differing from base: {sorted(c ^ base)}")
# relaxed-interface elastic upper bound (SD10N / SD3N, 400 C, per pad)
for rid in ("SD10N", "SD3N", "S61", "S62"):
    r = json.loads((REPO / "results" / rid / "record.json").read_text()); h = {x["tag"]: x for x in r["rows"]}
    print(f"{rid}: u_center(400 C) {h['h400']['u_center_nm']:.2f} nm per pad -> pair {2 * h['h400']['u_center_nm']:.1f} nm vs recess sum 5 nm")
json.dump({k: dict(window=sorted(c), floor={f'{T}C_{t}min': v for (T, t), v in f.items()}) for k, (c, f) in res.items()},
          open(OUT / "window_sensitivity_review.json", "w"), indent=1, default=float)
