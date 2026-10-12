r"""Stage 2 analysis: verification table, per-process calibration (grid, J), held-out validation, diffusion term,
contact-stage Monte Carlo. Outputs in results/stage2/.

Usage: python src\stage2\stage2_analysis.py --verify | --calibrate | --validate | --predict
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
import stage1_pipeline as S  # noqa: E402

OUT = B.RESULTS / "stage2"
OUT.mkdir(parents=True, exist_ok=True)
ADOPTED = OUT / "adopted.json"

# ---------------------------------------------------------------- measured data (pre-registration 2)
MEAS = {
    "imec": {  # pad w (um): {T: (u_nm, sigma_nm)}  marker readings of DM2023 Fig 1 (RT reference)
        3.06: {100: (1.55, 0.2), 200: (2.70, 0.2), 300: (6.05, 0.5), 400: (7.85, 0.5)},
        1.80: {100: (1.05, 0.2), 200: (2.45, 0.2), 300: (4.20, 0.5), 400: (5.40, 0.5)},
        1.26: {100: (0.70, 0.2), 200: (1.60, 0.2), 300: (3.65, 0.5), 400: (5.00, 0.5)},
        0.54: {100: (0.25, 0.2), 200: (0.60, 0.2), 300: (1.00, 0.5), 400: (1.40, 0.5)},
    },
    "nycu": {9.0: {200: (6.4, 0.4)}, 3.0: {200: (4.1, 0.4)}, 1.0: {200: (2.1, 0.4)}},   # 1 um = Chen 2025 mean (B3)
}
U_KEY = "du_c50"      # primary definition (pre-registration 2.1); du_ctr and du_full reported alongside


def res(rid):
    r = B.load(rid)
    return None if r is None else r["result"]


def u_at(rid, T, key=U_KEY):
    r = res(rid)
    if r is None:
        return None
    for h in r["hist"]:
        if abs(h["T"] - T) < 1e-6:
            return h["d" + key[1:]] if key.startswith("du") else h[key]
    return None


# ---------------------------------------------------------------- verification
def verify():
    rows = []
    def g(rid, key=U_KEY):
        r = res(rid); return None if r is None else r[key]
    b = g("SV01")
    rows.append(("mesh x2 (SV02 vs SV01)", b, g("SV02"), 2.0))
    rows.append(("cell 6w (SV03 vs SV01)", b, g("SV03"), 2.0))
    rows.append(("3D iso vs 2D (SV04 vs SV01)", b, g("SV04"), 3.0))
    lines = ["check,base_nm,test_nm,diff_pct,limit_pct,pass"]
    for name, x, y, lim in rows:
        if x is None or y is None:
            lines.append(f"{name},,,,{lim},MISSING"); continue
        d = 100 * (y / x - 1)
        lines.append(f"{name},{x:.4f},{y:.4f},{d:+.2f},{lim},{abs(d) <= lim}")
    # film-limit analytic check (3.06 um, h 0.6, SiCN mid params): u_film = h*[a_Cu + 2nu/(1-nu)(a_Cu - a_Si)]*dT - diel surface
    r5 = res("SV05")
    if r5 is not None:
        run = B.RUN_BY_ID["SV05"]; nu = 0.3454; a_cu, a_si = run["cu_alpha"], S.SILICON["ALPX"]
        nud = B.DIEL[run["diel"]]["PRXY"]; a_d = run["a_d"]
        dT = 375.0
        u_cu = run["h"] * (a_cu + 2 * nu / (1 - nu) * (a_cu - a_si)) * dT * 1000
        u_d = (run["z_ox"] + run["h"]) * (a_d + 2 * nud / (1 - nud) * (a_d - a_si)) * dT * 1000
        u_film = u_cu - u_d
        ratio = r5["du_ctr"] / u_film
        lines.append(f"film-limit 3.06 um (SV05 du_ctr / u_film),{u_film:.3f},{r5['du_ctr']:.3f},{100*(ratio-1):+.1f},[-15 +5],{0.85 <= ratio <= 1.05}")
    r6, r7 = res("SV06"), res("SV07")
    if r6 and r7:
        lines.append(f"liner 50 nm effect 1 um (SV06 vs SV07),{r7['du_c50']:.4f},{r6['du_c50']:.4f},{100*(r6['du_c50']/r7['du_c50']-1):+.2f},report,")
    (OUT / "verification.csv").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


# ---------------------------------------------------------------- calibration
def calibrate(key=U_KEY):
    out = {}
    tables = []
    for ds in ("nycu", "imec"):
        rows = []
        for r in B.RUNS:
            if r["group"] != "A" or r["ds"] != ds:
                continue
            rr = res(r["id"])
            if rr is None:
                continue
            rows.append((r, rr))
        # group by parameter combination
        combos = {}
        for r, rr in rows:
            kcombo = (r["E_d"], r["a_d"], r["taper"]) if ds == "nycu" else (r["E_d"], r["a_d"])
            combos.setdefault(kcombo, []).append((r, rr))
        best = None
        for kc, items in combos.items():
            J, n, parts = 0.0, 0, []
            for r, rr in items:
                for T, (um, sg) in MEAS[ds][r["w"]].items():
                    if T not in r["temps"]:
                        continue
                    um_model = u_at(r["id"], T, key)
                    J += ((um_model - um) / sg) ** 2; n += 1
                    parts.append((r["w"], T, um_model, um, sg))
            if n == 0:
                continue
            tables.append((ds, kc, J, n, parts))
            if best is None or J < best[1]:
                best = (kc, J, parts, [r["id"] for r, _ in items])
        kc, J, parts, ids = best
        bounds = {}
        if ds == "nycu":
            E, a, tp = kc
            bounds = dict(E=E in (59000.0, 77000.0), a=a in (0.5e-6, 1.0e-6), taper=tp in (7.6, 18.0))
            out[ds] = dict(E_d=E, a_d=a, taper=tp, J=J, runs=ids,
                           bound_limited=[k for k, v in bounds.items() if v],
                           residuals=[dict(w=w, T=T, model=m, meas=um, sigma=sg, ok=abs(m - um) <= 2 * sg) for w, T, m, um, sg in parts])
        else:
            E, a = kc
            bounds = dict(E=E in (70000.0, 120000.0), a=a in (2.0e-6, 5.2e-6))
            out[ds] = dict(E_d=E, a_d=a, J=J, runs=ids, bound_limited=[k for k, v in bounds.items() if v],
                           residuals=[dict(w=w, T=T, model=m, meas=um, sigma=sg, ok=abs(m - um) <= 2 * sg) for w, T, m, um, sg in parts])
        out[ds]["pass"] = all(x["ok"] for x in out[ds]["residuals"])
    # full table
    lines = ["process,E_MPa,alpha,taper,J,n,points(model/meas)"]
    for ds, kc, J, n, parts in sorted(tables, key=lambda t: (t[0], t[2])):
        kcs = ",".join(f"{v:g}" for v in kc) + ("" if ds == "nycu" else ",")
        pts = " | ".join(f"{w:g}um@{T:g}:{m:.2f}/{um:.2f}" for w, T, m, um, sg in parts)
        lines.append(f"{ds},{kcs},{J:.3f},{n},{pts}")
    (OUT / "calibration_grid.csv").write_text("\n".join(lines) + "\n")
    out["u_key"] = key
    ADOPTED.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return out


# ---------------------------------------------------------------- validation (held-out)
def validate():
    ad = json.loads(ADOPTED.read_text())
    lines = ["test,item,model,measured,tol,pass"]
    verdict = {}
    # V1 imec 1.26
    ok1 = True
    for T, (um, sg) in MEAS["imec"][1.26].items():
        m = u_at("S51", T)
        p = m is not None and (abs(m - um) <= 0.5 or abs(m / um - 1) <= 0.15)
        ok1 &= bool(p)
        lines.append(f"V1,imec 1.26 um @{T:g} C,{m},{um},0.5 nm or 15 %,{p}")
    verdict["V1"] = ok1
    # V2 imec 0.54 Hill + 3 orientations
    ok2 = True
    for T, (um, sg) in MEAS["imec"][0.54].items():
        m = u_at("S52", T)
        p = m is not None and abs(m - um) <= 0.4
        ok2 &= bool(p)
        lines.append(f"V2,imec 0.54 um Hill @{T:g} C,{m},{um},0.4 nm,{p}")
    ori = [u_at(r, 400) for r in ("S53", "S54", "S55")]
    if all(o is not None for o in ori):
        um = MEAS["imec"][0.54][400][0]
        p = min(ori) <= um + 0.3 and max(ori) >= um - 0.3
        ok2 &= bool(p)
        lines.append(f"V2,imec 0.54 um 3 orientations @400 C range,{min(ori):.3f}-{max(ori):.3f},{um},+/-0.3 overlap,{p}")
    verdict["V2"] = ok2
    # V3 NYCU 1 um
    ori = [u_at(r, 200) for r in ("S56", "S57", "S58")]
    if all(o is not None for o in ori):
        um, sg = MEAS["nycu"][1.0][200]
        p = min(ori) <= um + sg and max(ori) >= um - sg
        verdict["V3"] = bool(p)
        lines.append(f"V3,NYCU 1 um 3 orientations @200 C range,{min(ori):.3f}-{max(ori):.3f},{um},+/-{sg} overlap,{p}")
    # V4 sliding controls must fail
    s59 = u_at("S59", 400); s60 = u_at("S60", 200)
    f59 = s59 is not None and abs(s59 - MEAS["imec"][0.54][400][0]) > 0.4
    f60 = s60 is not None and abs(s60 - MEAS["nycu"][1.0][200][0]) > 0.4
    verdict["V4"] = bool(f59 or f60)
    lines.append(f"V4,imec 0.54 sliding @400 C (must fail),{s59},{MEAS['imec'][0.54][400][0]},0.4 nm,fails={f59}")
    lines.append(f"V4,NYCU 1 um [001] sliding @200 C (must fail),{s60},{MEAS['nycu'][1.0][200][0]},0.4 nm,fails={f60}")
    validated = all(verdict.get(k, False) for k in ("V1", "V2", "V3", "V4"))
    lines.append(f"VERDICT,baseline VALIDATED (V1-V4),{validated},,,")
    (OUT / "validation.csv").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    json.dump(dict(verdict=verdict, validated=validated), open(OUT / "validation.json", "w"), indent=1)
    return verdict


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--key", default=U_KEY)
    a = ap.parse_args(argv)
    if a.verify:
        verify()
    if a.calibrate:
        calibrate(a.key)
    if a.validate:
        validate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
