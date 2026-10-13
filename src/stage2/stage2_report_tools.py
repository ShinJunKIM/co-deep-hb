r"""Stage 2 report tools: Ayoub V5/V6 + H_sw test (group C), contact-stage summary and Lhostis relative test (group E),
figures. Usage: python src\stage2\stage2_report_tools.py --ayoub | --contact | --figures"""
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
import stage2_contact_runs  # noqa: E402,F401
import stage1_pipeline as S  # noqa: E402

OUT = B.RESULTS / "stage2"; OUT.mkdir(parents=True, exist_ok=True)
FIG = B.RESULTS / "figures"; FIG.mkdir(parents=True, exist_ok=True)


def s1(rid):
    f = B.RESULTS / rid / "record.json"
    if not f.exists():
        return None
    r = json.loads(f.read_text())
    return r if r.get("ok") else None


def rows_by_tag(rec):
    return {r["tag"]: r for r in rec["rows"]}


# ---------------------------------------------------------------- Ayoub 300 nm: V5 slope, V6 rank correlation, H_sw S2
def ayoub():
    meas = json.loads((S.INPUTS / "ayoub2022_eps_dev_digitized.json").read_text())
    out = {}
    lines = ["test,item,model,measured,rule,pass"]
    # V5: heating slope 30-350 C
    def slope_model(rid):
        rec = s1(rid)
        if rec is None:
            return None
        h = rows_by_tag(rec)
        tags = ["LS0_cool_Tsf_to_30", "h100", "h150", "h200", "h250", "h300", "h350"]
        T = np.array([h[t]["T"] for t in tags]); e = np.array([h[t]["eps_dev_zz"] for t in tags])
        return float(np.polyfit(T, e, 1)[0])
    for rid, pad, sm in (("S61", 10, 4.66e-6), ("S62", 3, 7.3e-6)):
        k = slope_model(rid)
        if k is None:
            lines.append(f"V5,pad {pad} slope,,{sm:.3e},sign + 25 %,MISSING"); continue
        ok = (np.sign(k) == np.sign(sm)) and abs(k / sm - 1) <= 0.25
        out[f"V5_pad{pad}"] = dict(model=k, meas=sm, ok=bool(ok))
        lines.append(f"V5,pad {pad} heating slope 30-350 C (1/K),{k:.3e},{sm:.3e},sign + 25 %,{ok}")
    # V6: Delta eps'zz(30->400 C 2h) rank correlation with E_z, bonded (R27,R35-39) and sliding (R26,R31-34)
    try:
        fig2 = json.loads((S.INPUTS / "ayoub2022_fig2ac_digitized.json").read_text())
    except Exception:
        fig2 = None
    for label, ids in (("bonded", {"R27": 10, "R35": 3, "R36": 4, "R37": 5, "R38": 7, "R39": 9}),
                       ("sliding", {"R26": 10, "R31": 4, "R32": 5, "R33": 7, "R34": 9})):
        xs, ys = [], []
        for rid, pad in ids.items():
            rec = s1(rid)
            if rec is None:
                continue
            h = rows_by_tag(rec)
            d = h["h400"]["eps_dev_zz"] - h["LS0_cool_Tsf_to_30"]["eps_dev_zz"]
            xs.append(rec["deck"]["mat"]["Ez_GPa"]); ys.append(d)
        if len(xs) >= 4:
            from scipy.stats import spearmanr
            rho = spearmanr(xs, ys).correlation
            out[f"V6_{label}"] = dict(rho=float(rho), n=len(xs))
            lines.append(f"V6,{label} rank corr(Delta eps'zz model; E_z),{rho:+.2f},measured: negative,sign,{rho < 0}")
    # H_sw S2: Delta_sw = eps(400) sliding - bonded for pad 3 (S63 - R35) vs measured hold increase +0.65e-3
    r35, s63 = s1("R35"), s1("S63")
    if r35 and s63:
        e_b = rows_by_tag(r35)["h400"]["eps_dev_zz"]; e_s = rows_by_tag(s63)["h400"]["eps_dev_zz"]
        d_sw = e_s - e_b; d_hold = 0.65e-3
        same = np.sign(d_sw) == np.sign(d_hold); enough = abs(d_sw) >= abs(d_hold)
        verdict = "consistent" if (same and enough) else ("rejected" if not same else "partial")
        out["Hsw_S2"] = dict(eps_bonded_400=e_b, eps_sliding_400=e_s, delta_sw=d_sw, delta_hold=d_hold, verdict=verdict)
        lines.append(f"H_sw S2,pad 3: eps'zz(400) sliding - bonded,{d_sw:.3e},{d_hold:.3e} (hold 40->120 min),same sign & |d_sw|>=|d_hold|,{verdict}")
        # cooling-branch superposition for pad 10 (elastic, no new run): R26(400) + [R24(T) - R24(400)]
        r24, r26 = s1("R24"), s1("R26")
        if r24 and r26:
            h24, h26 = rows_by_tag(r24), rows_by_tag(r26)
            for tag, Tm, em, eh in (("c300", 300, 0.380e-3, 0.102e-3), ("c200", 200, -0.118e-3, -0.367e-3), ("c030", 30, -1.14e-3, -1.197e-3)):
                pred = h26["h400"]["eps_dev_zz"] + (h24[tag]["eps_dev_zz"] - h24["h400"]["eps_dev_zz"])
                lines.append(f"H_sw cooling (report only),pad 10 {Tm} C: superposition offset vs bonded heating,"
                             f"{pred - h24[tag]['eps_dev_zz']:+.3e},{em - eh:+.3e} (meas cool - heat),report,")
    (OUT / "ayoub_tests.csv").write_text("\n".join(lines) + "\n")
    json.dump(out, open(OUT / "ayoub_tests.json", "w"), indent=1)
    print("\n".join(lines))
    return out


# ---------------------------------------------------------------- contact stage summary and Lhostis relative test
def contact():
    rows = []
    for r in B.RUNS:
        if r.get("kind") != "contact":
            continue
        rec = B.load(r["id"])
        if rec is None:
            rows.append(dict(id=r["id"], w=r["w"], h=r["h"], recess_nm=r["recess"] * 1000, T=r["T_anneal"], status="missing")); continue
        st = rec["result"]["steps"]
        hot, cold = st[1], st[2]
        rows.append(dict(id=r["id"], w=r["w"], h=r["h"], recess_nm=r["recess"] * 1000, T=r["T_anneal"], plastic=r["plastic"],
                         status="ok" if rec["check"]["all_ok"] else "not converged",
                         Ac_hot=hot["area_frac"], p_hot_MPa=hot["p_mean_MPa"], pmax_hot=hot["p_max_MPa"],
                         gap_centre_hot_nm=hot["gap_centre_nm"], Ac_cold=cold["area_frac"], p_cold_MPa=cold["p_mean_MPa"],
                         eppl_max=rec["result"]["eppl_max"], wall_s=rec["exec"]["wall_s"]))
    keys = ["id", "w", "h", "recess_nm", "T", "plastic", "status", "Ac_hot", "p_hot_MPa", "pmax_hot", "gap_centre_hot_nm",
            "Ac_cold", "p_cold_MPa", "eppl_max", "wall_s"]
    (OUT / "contact_summary.csv").write_text(",".join(keys) + "\n" + "".join(
        ",".join(f"{r.get(k, ''):.4g}" if isinstance(r.get(k), float) else str(r.get(k, "")) for k in keys) + "\n" for r in rows))
    # Lhostis relative test: r_open = recess at which Ac_hot -> 0 (linear interpolation in recess), w 0.72 vs 0.40
    res = {}
    for w in (0.72, 0.40):
        pts = sorted([(r["recess_nm"], r["Ac_hot"]) for r in rows if r.get("status") == "ok" and abs(r["w"] - w) < 1e-6 and r["T"] == 400])
        if len(pts) >= 2:
            xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts])
            # first recess where Ac = 0, interpolated from the last positive point
            if (ys <= 1e-6).any() and (ys > 1e-6).any():
                i = int(np.argmax(ys <= 1e-6))
                x0, y0, x1, y1 = xs[i - 1], ys[i - 1], xs[i], ys[i]
                r_open = x0 + (x1 - x0) * y0 / (y0 - y1 + 1e-30)
            else:
                r_open = float("nan") if (ys > 1e-6).all() else xs[0]
            # exploratory (post hoc, not pre-registered): recess at which Ac = 0.5, linear interpolation inside the grid
            r50 = float("nan")
            if (ys >= 0.5).any() and (ys < 0.5).any():
                i = int(np.argmax(ys < 0.5)); x0, y0, x1, y1 = xs[i - 1], ys[i - 1], xs[i], ys[i]
                r50 = x0 + (x1 - x0) * (y0 - 0.5) / (y0 - y1)
            res[w] = dict(points=pts, r_open_nm=float(r_open), r50_nm=r50)
    if 0.72 in res and 0.40 in res and np.isfinite(res[0.72]["r50_nm"]) and np.isfinite(res[0.40]["r50_nm"]):
        res["ratio50_400_over_720_exploratory"] = res[0.40]["r50_nm"] / res[0.72]["r50_nm"]
    if 0.72 in res and 0.40 in res and np.isfinite(res[0.72]["r_open_nm"]) and np.isfinite(res[0.40]["r_open_nm"]):
        ratio = res[0.40]["r_open_nm"] / res[0.72]["r_open_nm"]
        res["ratio_400_over_720"] = ratio; res["lhostis_ratio"] = 0.79; res["pass"] = abs(ratio - 0.79) <= 0.15
    if "pass" not in res:
        res["pass"] = "undetermined (A_c did not reach 0 inside the recess grid 2-8 nm; pre-registered metric r_open not available)"
    json.dump(res, open(OUT / "lhostis_test.json", "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
    return rows, res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ayoub", action="store_true")
    ap.add_argument("--contact", action="store_true")
    ap.add_argument("--mirror10", action="store_true")
    a = ap.parse_args(argv)
    if a.mirror10:
        mirror10()
    if a.ayoub:
        ayoub()
    if a.contact:
        contact()
    return 0



# ---------------------------------------------------------------- round Y: 10-pad mirror-image test (realistic stack)
def mirror10():
    """Post-hoc test of the sign-convention hypothesis on all pads with the cap + Ta 13 nm stack:
    r_p = (-Delta_model) / Delta_meas with Delta = eps'zz(400 C end of heating) - eps'zz(30 C); measured Fig 2c includes the
    2 h hold (creep for soft pads), so r_p < 1 is expected for E_z < 130 GPa. Consistent-with-flip rule (pre-declared here):
    all r_p > 0 and stiff pads (E_z > 130 GPa) within 0.75-1.25."""
    fig2 = json.loads((S.INPUTS / "ayoub2022_fig2ac_digitized.json").read_text())
    meas = {d["pad"]: (d["value"] * 1e-3, d["err"] * 1e-3) for d in fig2["fig2c_delta_30_400h"]}
    ids = {10: "S61", 3: "S62", 1: "SA1", 2: "SA2", 4: "SA4", 5: "SA5", 6: "SA6", 7: "SA7", 9: "SA9"}
    lines = ["pad,Ez_GPa,delta_model,delta_meas,err,ratio_neg_model_over_meas,stiff"]
    rows = []
    for pad, rid in sorted(ids.items()):
        rec = s1(rid)
        if rec is None or pad not in meas:
            continue
        h = rows_by_tag(rec)
        dm = h["h400"]["eps_dev_zz"] - h["LS0_cool_Tsf_to_30"]["eps_dev_zz"]
        ez = rec["deck"]["mat"]["Ez_GPa"]
        r = (-dm) / meas[pad][0]
        rows.append((pad, ez, dm, meas[pad][0], meas[pad][1], r, ez > 130.34))
        lines.append(f"{pad},{ez:.1f},{dm:.4e},{meas[pad][0]:.4e},{meas[pad][1]:.1e},{r:.3f},{ez > 130.34}")
    if rows:
        stiff = [r for r in rows if r[6]]
        ok = all(r[5] > 0 for r in rows) and all(0.75 <= r[5] <= 1.25 for r in stiff)
        lines.append(f"# rule: all ratios > 0 and stiff pads within 0.75-1.25 -> consistent_with_sign_flip={ok}")
        lines.append(f"# stiff-pad ratios: {[round(r[5], 3) for r in stiff]}; soft-pad ratios: {[round(r[5], 3) for r in rows if not r[6]]}")
    (OUT / "ayoub_mirror10.csv").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))

if __name__ == "__main__":
    sys.exit(main())
