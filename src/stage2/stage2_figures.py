r"""Stage 2 figures -> results/figures/s2_*.png
1 validation_u_vs_T: imec u(T) measured vs model (isolated-cell round 1 and array-cell revision 1)
2 size_scaling: u(400 C) vs pad width, measured vs model rounds, + NYCU 1 um
3 contact_map: P(contact) over (T, recess sum) for 0.54 and 0.30 um (clean / oxidised surface)
4 contact_stage_fem: contact area fraction and mean pressure vs recess and T (E group)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "stage1"))
import baseline as B  # noqa: E402
sys.modules.setdefault("baseline", B)
import stage2_runs  # noqa: E402,F401
import stage2_contact_runs  # noqa: E402,F401
import stage2_analysis as A  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FIG = B.RESULTS / "figures"; FIG.mkdir(parents=True, exist_ok=True)
OUT = B.RESULTS / "stage2"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
C = {"meas": "k", "r1": "#1f77b4", "rev": "#d62728", "slide": "#7f7f7f"}


def hist(rid, key="du_c50"):
    r = B.load(rid)
    if r is None:
        return None, None
    h = r["result"]["hist"]
    return np.array([x["T"] for x in h]), np.array([x[key] for x in h])


def fig_validation():
    sizes = [(3.06, "S45", "S85"), (1.80, "S47", "S91"), (1.26, "S51", "S111"), (0.54, "S52", "S112")]
    # S45/S47: round-1 adopted (E95,a2.0) runs = S37+? find by params
    def find(group, w, E, a):
        for r in B.RUNS:
            if r["group"] == group and r["ds"] == "imec" and abs(r["w"] - w) < 1e-6 and r["E_d"] == E and r["a_d"] == a:
                return r["id"]
    ad1 = json.loads((OUT / "adopted.json").read_text())["imec"]; adr = json.loads((OUT / "adopted_rev.json").read_text())["imec"]
    fig, axs = plt.subplots(1, 4, figsize=(10, 2.8), sharey=False)
    for ax, (w, _, _) in zip(axs, sizes):
        m = A.MEAS["imec"][w]
        Ts = sorted(m); ax.errorbar(Ts, [m[T][0] for T in Ts], yerr=[m[T][1] for T in Ts], fmt="o", color=C["meas"], ms=4, label="measured (DM2023 Fig 1)")
        r1 = find("A", w, ad1["E_d"], ad1["a_d"]) if w >= 1.5 else {1.26: "S51", 0.54: "S52"}[w]
        rv = find("Ar", w, adr["E_d"], adr["a_d"]) if w >= 1.5 else {1.26: "S111", 0.54: "S112"}[w]
        for rid, col, lab in ((r1, C["r1"], "model, isolated pad (round 1)"), (rv, C["rev"], "model, array pitch 2w (rev 1)")):
            T, u = hist(rid)
            if T is not None:
                ax.plot(T, u, "-", color=col, lw=1.3, label=lab)
        if w == 0.54:
            T, u = hist("S116")
            if T is not None:
                ax.plot(T, u, "--", color=C["slide"], lw=1, label="sliding sidewall (control)")
        ax.set_title(f"{w:g} µm pad ({'calibration' if w >= 1.5 else 'held-out'})", fontsize=9)
        ax.set_xlabel("T (°C)"); ax.set_xlim(0, 420)
    axs[0].set_ylabel("u = Δheight Cu − dielectric (nm)")
    axs[-1].legend(frameon=False, fontsize=6.5, loc="upper left")
    fig.tight_layout(); fig.savefig(FIG / "s2_validation_u_vs_T.png", dpi=300); plt.close(fig)


def fig_size_scaling():
    ad1 = json.loads((OUT / "adopted.json").read_text())["imec"]; adr = json.loads((OUT / "adopted_rev.json").read_text())["imec"]
    def find(group, w, E, a):
        for r in B.RUNS:
            if r["group"] == group and r["ds"] == "imec" and abs(r["w"] - w) < 1e-6 and r["E_d"] == E and r["a_d"] == a:
                return r["id"]
    ws = [0.54, 1.26, 1.80, 3.06]
    meas = [A.MEAS["imec"][w][400][0] for w in ws]; err = [A.MEAS["imec"][w][400][1] for w in ws]
    r1 = [hist(find("A", w, ad1["E_d"], ad1["a_d"]) if w >= 1.5 else {1.26: "S51", 0.54: "S52"}[w])[1] for w in ws]
    rv = [hist(find("Ar", w, adr["E_d"], adr["a_d"]) if w >= 1.5 else {1.26: "S111", 0.54: "S112"}[w])[1] for w in ws]
    fig, ax = plt.subplots(figsize=(3.6, 2.8))
    ax.errorbar(ws, meas, yerr=err, fmt="o", color=C["meas"], ms=4, label="measured, 400 °C")
    ax.plot(ws, [u[-1] if u is not None else np.nan for u in r1], "s-", color=C["r1"], ms=3, lw=1, label="model, isolated (round 1)")
    ax.plot(ws, [u[-1] if u is not None else np.nan for u in rv], "^-", color=C["rev"], ms=3, lw=1, label="model, array 2w (rev 1)")
    p30 = hist("S67")[1]
    if p30 is not None:
        ax.plot([0.30], [p30[-1]], "^", color=C["rev"], ms=5, mfc="none", label="prediction 0.30 µm")
    ax.set_xscale("log"); ax.set_xlabel("pad width (µm)"); ax.set_ylabel("u at 400 °C (nm)")
    ax.set_xticks([0.3, 0.54, 1.26, 1.8, 3.06]); ax.set_xticklabels(["0.3", "0.54", "1.26", "1.8", "3.06"]); ax.minorticks_off()
    ax.legend(frameon=False, fontsize=6.5); fig.tight_layout(); fig.savefig(FIG / "s2_size_scaling.png", dpi=300); plt.close(fig)


def fig_contact_map():
    import csv
    for label in ("0.54um", "0.30um"):
        f = OUT / f"predict_{label}.csv"
        if not f.exists():
            continue
        rows = list(csv.DictReader(open(f)))
        fig, axs = plt.subplots(1, 2, figsize=(7, 2.9), sharey=True)
        for ax, surf in zip(axs, ("clean", "oxidised")):
            Ts = sorted({int(r["T_C"]) for r in rows}); gs = ["2", "4", "6", "8"]
            M = np.array([[float(next(r["P_contact"] for r in rows if int(r["T_C"]) == T and r["surface"] == surf and r["t_min"] == "30"
                                      and r["theta"] == "123" and r["recess_sum"] == g)) for T in Ts] for g in gs])
            Mel = np.array([[float(next(r["P_elastic_only"] for r in rows if int(r["T_C"]) == T and r["surface"] == surf and r["t_min"] == "30"
                                        and r["theta"] == "123" and r["recess_sum"] == g)) for T in Ts] for g in gs])
            im = ax.imshow(M, origin="lower", vmin=0, vmax=1, cmap="Blues", aspect="auto",
                           extent=[Ts[0] - 25, Ts[-1] + 25, 1, 9])
            for i, g in enumerate(gs):
                for j, T in enumerate(Ts):
                    ax.text(T, 2 + 2 * i, f"{M[i, j]:.2f}\n({Mel[i, j]:.2f})", ha="center", va="center", fontsize=6,
                            color="w" if M[i, j] > 0.6 else "k")
            ax.set_title(f"{label}, {surf} surface, 30 min, θ 123°", fontsize=8); ax.set_xlabel("anneal T (°C)")
            ax.set_yticks([2, 4, 6, 8])
        axs[0].set_ylabel("recess top+bottom (nm)")
        cb = fig.colorbar(im, ax=axs, shrink=0.9); cb.set_label("P(contact)  (elastic-only in parentheses)")
        fig.savefig(FIG / f"s2_contact_map_{label}.png", dpi=300, bbox_inches="tight"); plt.close(fig)


def fig_contact_fem():
    import csv
    f = OUT / "contact_summary.csv"
    if not f.exists():
        return
    rows = [r for r in csv.DictReader(open(f)) if r["status"] == "ok" and abs(float(r["w"]) - 0.54) < 1e-6 and r["plastic"] == "True"]
    if not rows:
        return
    fig, axs = plt.subplots(1, 2, figsize=(7, 2.8))
    for T in sorted({int(float(r["T"])) for r in rows}):
        rr = sorted([r for r in rows if int(float(r["T"])) == T], key=lambda r: float(r["recess_nm"]))
        x = [float(r["recess_nm"]) for r in rr]
        axs[0].plot(x, [float(r["Ac_hot"]) for r in rr], "o-", ms=3, label=f"{T} °C")
        axs[1].plot(x, [float(r["p_hot_MPa"]) for r in rr], "o-", ms=3, label=f"{T} °C")
    axs[0].set_xlabel("recess per pad (nm)"); axs[0].set_ylabel("contact area fraction at T"); axs[0].legend(frameon=False, fontsize=7)
    axs[1].set_xlabel("recess per pad (nm)"); axs[1].set_ylabel("mean contact pressure (MPa)")
    fig.suptitle("0.54 µm pads, 2D axisymmetric Cu–Cu contact, isotropic plastic Cu", fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "s2_contact_fem_054.png", dpi=300); plt.close(fig)


if __name__ == "__main__":
    for fn in (fig_validation, fig_size_scaling, fig_contact_map, fig_contact_fem):
        try:
            fn(); print("ok", fn.__name__)
        except Exception as exc:
            print("skip", fn.__name__, type(exc).__name__, exc)
