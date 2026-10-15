r"""Scaling-collapse fork: dimensionless constraint factor C = u / ((alpha_Cu - alpha_Si) * dT * h) for every Stage 2 FEM
protrusion run and every measured point (NYCU, imec).  No ANSYS.  Exploratory (new plot of pre-registered data).
Usage: python src\agents\scaling_collapse.py
Outputs: results/figures/agents/constraint_factor.png, results/stage2/agents/scaling_collapse.json/.csv
"""
from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "results" / "stage2" / "agents"; OUT.mkdir(parents=True, exist_ok=True)
FIG = REPO / "results" / "figures" / "agents"; FIG.mkdir(parents=True, exist_ok=True)
A_CU, A_SI = 16.5e-6, 2.6e-6
DA = A_CU - A_SI
E_CU = 128.3e3   # Hill, MPa

MEAS = {  # (ds, w): {T: (u, sigma)}; pad heights per dataset facts
    ("imec", 3.06): {100: (1.55, 0.2), 200: (2.70, 0.2), 300: (6.05, 0.5), 400: (7.85, 0.5)},
    ("imec", 1.80): {100: (1.05, 0.2), 200: (2.45, 0.2), 300: (4.20, 0.5), 400: (5.40, 0.5)},
    ("imec", 1.26): {100: (0.70, 0.2), 200: (1.60, 0.2), 300: (3.65, 0.5), 400: (5.00, 0.5)},
    ("imec", 0.54): {100: (0.25, 0.2), 200: (0.60, 0.2), 300: (1.00, 0.5), 400: (1.40, 0.5)},
    ("nycu", 9.0): {200: (6.4, 0.4)}, ("nycu", 3.0): {200: (4.1, 0.4)}, ("nycu", 1.0): {200: (2.1, 0.4)},
}
H_MEAS = {("imec", 3.06): 0.6, ("imec", 1.80): 0.6, ("imec", 1.26): 0.6, ("imec", 0.54): 0.6, ("nycu", 9.0): 1.15, ("nycu", 3.0): 1.5, ("nycu", 1.0): 1.5}
# adopted-model run for each measured point (revision 1 array cells for imec, NYCU adopted; 1 um = mean of 3D orientations)
MODEL_RUN = {("imec", 3.06): ["S91"], ("imec", 1.80): ["S85"], ("imec", 1.26): ["S111"], ("imec", 0.54): ["S112"],
             ("nycu", 9.0): ["S06"], ("nycu", 3.0): ["S98"], ("nycu", 1.0): ["S56", "S57", "S58"]}


def C_of(u_nm, T, h_um):
    return u_nm / (DA * (T - 25.0) * h_um * 1000.0)


def load_runs():
    rows = []
    for f in sorted(glob.glob(str(REPO / "results" / "[SWX]*" / "record.json"))):
        try:
            r = json.loads(Path(f).read_text())
        except Exception:
            continue
        if not r.get("ok"):
            continue
        d = r.get("deck", {}); run = d.get("run", d) if isinstance(d, dict) else {}
        res = r.get("result", {}); h = res.get("hist")
        if not h or run.get("kind") == "contact" or "w" not in run:
            continue
        last = h[-1]
        rows.append(dict(id=os.path.basename(os.path.dirname(f)), group=run.get("group"), ds=run.get("ds"), w=run["w"], h=run["h"],
                         cell=run.get("cell_factor"), side=run.get("side"), diel=run.get("diel"), E_d=run.get("E_d"), a_d=run.get("a_d"),
                         t_liner=run.get("t_liner"), taper=run.get("taper"), cu=run.get("cu"), orient=run.get("orient"),
                         plastic=bool(run.get("plastic")), yscale=run.get("yield_scale"), aip=run.get("cu_alpha_ip"), dim=run.get("dim"),
                         T=last["T"], du=last.get("du_c50"), note=run.get("note", "")))
    for r in rows:
        r["hw"] = r["h"] / r["w"]; r["C"] = C_of(r["du"], r["T"], r["h"])
        r["Ed_Ecu"] = (r["E_d"] or 0) / E_CU
        r["kind"] = ("relax" if r["aip"] else ("plastic" if r["plastic"] else "elastic"))
    return rows


def main():
    rows = load_runs()
    byid = {r["id"]: r for r in rows}
    # ---- measured C and model C per measured point
    pts = []
    for (ds, w), tv in MEAS.items():
        h = H_MEAS[(ds, w)]
        mods = [byid[i] for i in MODEL_RUN[(ds, w)] if i in byid]
        for T, (u, s) in tv.items():
            # model du at this T from hist of the adopted run(s)
            um = []
            for rid in MODEL_RUN[(ds, w)]:
                rec = json.loads((REPO / "results" / rid / "record.json").read_text())
                hh = {x["T"]: x["du_c50"] for x in rec["result"]["hist"]}
                if T in hh: um.append(hh[T])
            if not um:
                continue
            um = float(np.mean(um))
            pts.append(dict(ds=ds, w=w, h=h, hw=h / w, T=T, u_meas=u, sig=s, u_model=um, C_meas=C_of(u, T, h), C_model=C_of(um, T, h),
                            ratio=u / um, ratio_sig=s / um, runs=MODEL_RUN[(ds, w)]))
    # ---- universality of the FEM: elastic bonded runs, C vs h/w, by dielectric stiffness class
    el = [r for r in rows if r["kind"] == "elastic" and r["side"] == "bonded" and r["dim"] == 2 and r["taper"] in (0.0, 18.0)]
    # fit C = c0 / (1 + a * (E_d/E_Cu) * (h/w)^m) on adopted-stack runs (cell >= 12w isolated and array separately)
    def fit(sub):
        X = np.array([[r["hw"], r["Ed_Ecu"]] for r in sub]); y = np.array([r["C"] for r in sub])
        best = None
        for c0 in np.linspace(0.6, 2.5, 39):
            for a in np.linspace(0.2, 20, 100):
                for m in np.linspace(0.3, 2.0, 35):
                    pred = c0 / (1 + a * X[:, 1] * X[:, 0] ** m)
                    s = float(np.mean((pred - y) ** 2))
                    if best is None or s < best[0]:
                        best = (s, c0, a, m)
        return dict(rms=np.sqrt(best[0]), c0=best[1], a=best[2], m=best[3], n=len(sub))
    iso = [r for r in el if r["cell"] >= 12 and r["t_liner"] in (0.006, 0.05)]
    arr = [r for r in el if r["cell"] < 4]
    fit_iso = fit(iso) if len(iso) >= 6 else None
    fit_arr = fit(arr) if len(arr) >= 6 else None
    # ---- ratio trend vs h/w (measured/model)
    hw = np.array([p["hw"] for p in pts]); ratio = np.array([p["ratio"] for p in pts]); sig = np.array([p["ratio_sig"] for p in pts])
    wts = 1 / sig ** 2
    A = np.vstack([np.log(hw), np.ones_like(hw)]).T
    W = np.sqrt(wts)[:, None]
    coef, *_ = np.linalg.lstsq(A * W, ratio * W[:, 0], rcond=None)
    slope, icpt = coef
    # without 0.54
    m54 = np.array([p["w"] != 0.54 for p in pts])
    coef2, *_ = np.linalg.lstsq((A * W)[m54], (ratio * W[:, 0])[m54], rcond=None)
    # per-size mean ratio
    per_size = {}
    for p in pts:
        per_size.setdefault((p["ds"], p["w"]), []).append(p["ratio"])
    per_size = {f"{k[0]} {k[1]:g}um": dict(hw=H_MEAS[k] / k[1], ratio_mean=float(np.mean(v)), n=len(v)) for k, v in per_size.items()}
    # ---- pitch / cell dependence and sliding ratio
    pitch = {r["id"]: dict(cell=r["cell"], C=r["C"], du=r["du"]) for r in rows if r["id"] in ("S117", "S112", "S118", "S52", "S113", "S53")}
    slide = {}
    for r in rows:
        if r["side"] == "sliding" and r["kind"] == "elastic":
            mate = [q for q in rows if q["side"] == "bonded" and q["kind"] == "elastic" and q["ds"] == r["ds"] and q["w"] == r["w"] and q["h"] == r["h"]
                    and q["cell"] == r["cell"] and q["E_d"] == r["E_d"] and q["a_d"] == r["a_d"] and q["cu"] == r["cu"] and q["orient"] == r["orient"] and q["taper"] == r["taper"]]
            if mate:
                slide[r["id"]] = dict(w=r["w"], hw=r["hw"], C_slide=r["C"], C_bond=mate[0]["C"], ratio=r["C"] / mate[0]["C"], mate=mate[0]["id"])
    res = dict(points=pts, per_size_ratio=per_size, ratio_fit_all=dict(slope_per_ln_hw=float(slope), intercept=float(icpt)),
               ratio_fit_without_054=dict(slope_per_ln_hw=float(coef2[0]), intercept=float(coef2[1])),
               fem_fit_isolated=fit_iso, fem_fit_array=fit_arr, pitch_runs=pitch, sliding_vs_bonded=slide,
               n_runs=len(rows), formula="C = u/((alpha_Cu-alpha_Si)*(T-25)*h); alpha_Cu 16.5, alpha_Si 2.6 ppm/K")
    json.dump(res, open(OUT / "scaling_collapse.json", "w"), indent=1, default=float)
    keys = ["id", "group", "ds", "w", "h", "hw", "cell", "side", "diel", "E_d", "a_d", "t_liner", "taper", "cu", "orient", "kind", "yscale", "dim", "T", "du", "C"]
    (OUT / "scaling_collapse_runs.csv").write_text(",".join(keys) + "\n" + "".join(",".join(f"{r[k]:.4g}" if isinstance(r[k], float) else str(r[k]) for k in keys) + "\n" for r in rows))
    print("runs", len(rows), "| measured points", len(pts))
    for p in pts:
        print(f"  {p['ds']} {p['w']:g} um h/w {p['hw']:.2f} T{p['T']:.0f}: C_meas {p['C_meas']:.3f} C_model {p['C_model']:.3f} ratio {p['ratio']:.2f}±{p['ratio_sig']:.2f}")
    print("per-size ratio:", per_size)
    print("ratio vs ln(h/w) slope all:", round(slope, 3), "without 0.54:", round(float(coef2[0]), 3))
    print("FEM fit isolated:", fit_iso); print("FEM fit array:", fit_arr)
    print("pitch:", pitch); print("sliding/bonded:", slide)
    # ---- figure
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(8.6, 3.4))
    ax = axs[0]
    col = {"nycu": "#1f77b4", "imec": "#d62728"}; mk = {"bonded": "o", "sliding": "^"}
    for kind, alpha in (("elastic", 0.85), ("plastic", 0.35), ("relax", 0.2)):
        for r in rows:
            if r["kind"] != kind: continue
            ax.scatter(r["hw"], r["C"], s=10 + 6 * np.log10(max(r["cell"], 1.1)), c=col[r["ds"]], marker=mk.get(r["side"], "s"), alpha=alpha, lw=0, zorder=2 if kind == "elastic" else 1)
    for p in pts:
        ax.errorbar(p["hw"], p["C_meas"], yerr=p["sig"] / (DA * (p["T"] - 25) * p["h"] * 1000), fmt="k*", ms=9, capsize=2, zorder=5)
    hwx = np.logspace(-1.3, 0.3, 100)
    for f_, lab, ls in ((fit_iso, "FEM fit, isolated cell", "-"), (fit_arr, "FEM fit, array cell", "--")):
        if f_:
            for edc, c in ((59e3 / E_CU, "#1f77b4"), (120e3 / E_CU, "#d62728")):
                ax.plot(hwx, f_["c0"] / (1 + f_["a"] * edc * hwx ** f_["m"]), ls, color=c, lw=1, alpha=0.7)
    ax.set_xscale("log"); ax.set_xlabel("aspect ratio h/w"); ax.set_ylabel("constraint factor C = u / ((α_Cu−α_Si)·ΔT·h)")
    ax.set_title("FEM runs (blue NYCU SiO2, red imec SiCN; ○ bonded △ sliding; size ∝ cell) and measurements (★)", fontsize=7)
    ax = axs[1]
    for p in pts:
        ax.errorbar(p["hw"], p["ratio"], yerr=p["ratio_sig"], fmt="o" if p["ds"] == "imec" else "s", color=col[p["ds"]], ms=5, capsize=2)
        if p["w"] == 0.54: ax.annotate(f"0.54 µm {p['T']:.0f}°C", (p["hw"], p["ratio"]), fontsize=5.5, xytext=(4, 2), textcoords="offset points")
    ax.axhline(1, color="gray", lw=0.8); ax.plot(hwx, slope * np.log(hwx) + icpt, "k:", lw=1, label=f"fit all: {slope:+.2f}·ln(h/w)+{icpt:.2f}")
    ax.plot(hwx, coef2[0] * np.log(hwx) + coef2[1], "k--", lw=1, label=f"fit w/o 0.54: {coef2[0]:+.2f}·ln(h/w)+{coef2[1]:.2f}")
    ax.set_xscale("log"); ax.set_xlabel("aspect ratio h/w"); ax.set_ylabel("measured / model (adopted elastic model)"); ax.legend(fontsize=6, frameon=False)
    ax.set_title("the 0.54 µm pad is the only h/w > 1 case and the only strong outlier", fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "constraint_factor.png", dpi=300); plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
