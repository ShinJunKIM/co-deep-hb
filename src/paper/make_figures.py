r"""
IEIE 2026 fall undergraduate paper: Figs 1-6 (English labels, PNG 600 dpi + SVG).
Data come ONLY from repository result files (see SOURCES below); nothing is recomputed except
plot geometry and the analytic f(omega) curve drawn with the fitted parameters.

Usage (repo root):  python src\paper\make_figures.py      -> docs/paper/figures/fig*.png|svg
Single-column width 8.0 cm (template column); smallest font 7 pt.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
S2 = ROOT / "results" / "stage2"
OUT = ROOT / "docs" / "paper" / "figures"
SOURCES = {
    "fig1": ["schematic (no data)"],
    "fig2": ["results/stage2/paper_results.json (mechanism_transition, transition_vs_recess_um)",
             "results/stage2/adopted_rev.json (imec train residuals 1.80/3.06 um, 400 C)",
             "results/stage2/validation_rev1.csv (V1/V2: 1.26/0.54 um, 400 C)"],
    "fig3": ["results/stage2/orient_diffusion_round2.csv", "results/stage2/orient_diffusion_round2.json (fit, faceted_fraction)",
             "results/stage2/paper_results.json (fraction_pads_f_below_0p5)"],
    "fig4": ["results/stage2/window_summary.json ['0.30um'] clean/oxidised P_main, hatched_cells"],
    "fig5": ["results/stage2/paper_results.json (recess_spec_sum_nm_300nm)"],
    "fig6": ["results/stage2/window_summary.json (factor_cells_changed, clean, 0.54/0.30 um; settings.n)",
             "results/stage2/paper_results.json (orientation_floor_300nm)"],
}
W = 8.0 / 2.54                      # single column width (in)
BLUE, ORANGE, SKY, GREEN, GREY, BLACK = "#0072B2", "#E69F00", "#56B4E9", "#009E73", "#7F7F7F", "#000000"
plt.rcParams.update({
    "font.family": "Arial", "font.size": 7, "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "xtick.minor.size": 1.5, "ytick.minor.size": 1.5, "lines.linewidth": 1.0,
    "axes.spines.top": False, "axes.spines.right": False, "svg.fonttype": "none", "pdf.fonttype": 42,
    "legend.frameon": False, "axes.titlelocation": "left",
})
TEMPS = [200, 250, 300, 350, 400]
TIMES = [5, 30, 120]


def jload(name):
    return json.loads((S2 / name).read_text(encoding="utf-8"))


def letter(ax, s, x=-0.02, y=1.02):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=9, fontweight="bold", ha="right", va="bottom")


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.png", dpi=600)
    fig.savefig(OUT / f"{name}.svg")
    return fig


# ------------------------------------------------------------------ Fig 1 (schematic)
def fig1():
    fig = plt.figure(figsize=(W, 2.55))
    ax = fig.add_axes([0.0, 0.0, 0.47, 0.93]); ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.add_patch(Rectangle((0.3, 0.6), 9.4, 3.6, fc="#DDDDDD", ec="k", lw=0.5))
    ax.add_patch(Rectangle((3.0, 0.6), 4.0, 3.2, fc="#E8A86A", ec="k", lw=0.5))
    xs = np.linspace(3.0, 7.0, 60); dome_b = 3.8 + 0.55 * (1 - ((xs - 5) / 2) ** 2)
    ax.add_patch(Polygon(np.c_[np.r_[xs, 7.0, 3.0], np.r_[dome_b, 3.8, 3.8]], fc="#F3C89A", ec="k", lw=0.5))
    ax.add_patch(Rectangle((0.3, 5.8), 9.4, 3.6, fc="#DDDDDD", ec="k", lw=0.5))
    ax.add_patch(Rectangle((3.0, 6.2), 4.0, 3.2, fc="#E8A86A", ec="k", lw=0.5))
    dome_t = 6.2 - 0.55 * (1 - ((xs - 5) / 2) ** 2)
    ax.add_patch(Polygon(np.c_[np.r_[xs, 7.0, 3.0], np.r_[dome_t, 6.2, 6.2]], fc="#F3C89A", ec="k", lw=0.5))
    ax.plot([0.3, 9.7], [5.0, 5.0], color=GREY, lw=0.6, ls=(0, (3, 2)))
    ax.text(9.6, 5.12, "bond interface", fontsize=7, color=GREY, va="bottom", ha="right")
    ax.text(1.6, 2.4, "dielectric", fontsize=7, ha="center", rotation=90, va="center")
    ax.text(5.0, 1.6, "Cu", fontsize=7, ha="center")
    ax.text(5.0, 7.8, "Cu", fontsize=7, ha="center")

    def dim(x, y0, y1, lab, side=1):
        ax.annotate("", xy=(x, y1), xytext=(x, y0), arrowprops=dict(arrowstyle="<->", lw=0.6, shrinkA=0, shrinkB=0))
        ax.text(x + 0.25 * side, (y0 + y1) / 2, lab, fontsize=7, va="center", ha="left" if side > 0 else "right")
    dim(7.4, 3.8, 4.2, "$r_b$")
    dim(5.0, 3.8, 4.35, "")
    ax.text(5.0, 3.35, "$u_b+h_{d,b}$", fontsize=7, ha="center", va="center")
    dim(1.0, 4.35, 5.65, "", side=-1)
    ax.text(1.25, 4.62, "gap", fontsize=7, va="center", ha="left")
    ax.text(5.0, 9.6, "contact if $m \\geq 0$", fontsize=7, ha="center", va="bottom")
    letter(ax, "a", x=0.06, y=0.97)
    bx = fig.add_axes([0.52, 0.0, 0.48, 0.93]); bx.set_xlim(0, 10); bx.set_ylim(0, 10); bx.axis("off")
    steps = [("Verification", "units, mesh, cell, 3D vs 2D"), ("Train (large pads)", "dielectric E, α in literature range"),
             ("Test (held-out)", "rules committed first"), ("Prediction (Monte Carlo)", "300 nm window, recess spec")]
    ys = [8.75, 6.45, 3.55, 1.25]
    for (t, sub), y in zip(steps, ys):
        test = "Test" in t
        bx.add_patch(FancyBboxPatch((0.4, y - 0.85), 9.2, 1.7, boxstyle="round,pad=0.02,rounding_size=0.3",
                                    fc="white", ec=BLUE if test else "k", lw=1.0 if test else 0.6))
        bx.text(5.0, y + 0.36, t, fontsize=7, ha="center", va="center", fontweight="bold")
        bx.text(5.0, y - 0.40, sub, fontsize=7, ha="center", va="center")
    for y0, y1 in zip(ys[:-1], ys[1:]):
        bx.annotate("", xy=(5.0, y1 + 0.87), xytext=(5.0, y0 - 0.87), arrowprops=dict(arrowstyle="-|>", lw=0.6, color="k"))
    bx.plot([0.2, 9.8], [5.0, 5.0], color=BLUE, lw=0.8, ls=(0, (4, 2)))
    bx.text(9.8, 5.06, "pre-registered", fontsize=7, color=BLUE, ha="right", va="bottom")
    letter(bx, "b", x=0.04, y=0.97)
    return save(fig, "fig1_architecture")


# ------------------------------------------------------------------ Fig 2
def fig2():
    pr = jload("paper_results.json"); ad = jload("adopted_rev.json")
    mt = pr["mechanism_transition"]
    rows = list(csv.DictReader(open(S2 / "validation_rev1.csv", encoding="utf-8")))

    def v(item):
        r = next(r for r in rows if r["item"].startswith(item)); return float(r["model"]), float(r["measured"])
    m126, e126 = v("imec 1.26 um @400 C"); m054, e054 = v("imec 0.54 um Hill @400 C")
    res = {(r["w"], r["T"]): r for r in ad["imec"]["residuals"]}
    w = np.array([0.54, 1.26, 1.80, 3.06])
    meas = np.array([e054, e126, res[(1.8, 400)]["meas"], res[(3.06, 400)]["meas"]])
    model = np.array([m054, m126, res[(1.8, 400)]["model"], res[(3.06, 400)]["model"]])
    hs = {float(k): v_ for k, v_ in mt["h_sat_per_pad_nm"].items()}
    d_ok = np.array(sorted(k for k in hs if k <= 0.30)); d_ex = np.array(sorted(k for k in hs if 0.30 <= k <= 0.54))
    g = mt["recess_sum_nm"]
    fig, ax = plt.subplots(figsize=(W, 2.75))
    fig.subplots_adjust(left=0.14, right=0.97, bottom=0.15, top=0.97)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.plot(d_ok, [2 * hs[k] for k in d_ok], color=ORANGE, lw=1.4, label="diffusion, saturated (model)")
    ax.plot(d_ex, [2 * hs[k] for k in d_ex], color=ORANGE, lw=1.4, ls=(0, (3, 2)))
    ax.text(0.43, 2 * hs[0.43 if 0.43 in hs else 0.54] * 0.42, "extrapolated", color=ORANGE, fontsize=7, ha="center", rotation=18)
    ax.plot(w, 2 * model, "-", color=BLUE, marker="s", ms=3, mfc="white", mew=0.8, label="elastic FEM ($b$ = 1)")
    ax.plot(w, 2 * 0.69 * model, ":", color=BLUE, lw=1.0, label="elastic FEM × 0.69")
    ax.plot(w, 2 * meas, "-o", color=BLACK, ms=3.5, lw=0.6, label="elastic, imec in-situ")
    ax.axhline(g, color=GREY, lw=0.8, ls="--")
    ax.text(3.4, g * 0.93, f"recess sum {g:g} nm", color=GREY, fontsize=7, ha="right", va="top")
    xc = mt["size_measured_um"]
    ax.annotate(f"≈ {xc:.1f} µm", xy=(xc, g), xytext=(xc, g * 0.36), fontsize=7, ha="center",
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color=BLACK))
    ax.set_xlim(0.1, 3.6); ax.set_ylim(1.0, 300)
    from matplotlib.ticker import NullFormatter
    ax.xaxis.set_minor_formatter(NullFormatter()); ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xticks([0.1, 0.3, 1, 3]); ax.set_xticklabels(["0.1", "0.3", "1", "3"])
    ax.set_yticks([1, 10, 100]); ax.set_yticklabels(["1", "10", "100"])
    ax.set_xlabel("Pad width (µm)"); ax.set_ylabel("Top + bottom protrusion at 400 °C (nm)")
    ax.legend(loc="upper left", handlelength=1.8, borderaxespad=0.2)
    tv = pr["transition_vs_recess_um"]
    gs = sorted(tv, key=float)
    ins = fig.add_axes([0.73, 0.64, 0.23, 0.28])
    for key, col, ls, lab in (("meas", BLACK, "-", "imec"), ("model", BLUE, "-", "$b$ = 1"), ("model_b069", BLUE, ":", "× 0.69")):
        pts = [(float(k), tv[k][key]) for k in gs if tv[k][key] is not None and np.isfinite(tv[k][key])]
        ins.plot([p[0] for p in pts], [p[1] for p in pts], ls, color=col, marker="o" if key == "meas" else None, ms=2.2, lw=0.9, label=lab)
    ins.set_xlim(2.5, 10.5); ins.set_ylim(0.4, 2.6); ins.set_xticks([3, 5, 8, 10])
    ins.set_xlabel("Recess sum (nm)", fontsize=7, labelpad=1); ins.set_ylabel("Transition (µm)", fontsize=7, labelpad=1)
    ins.tick_params(labelsize=7, pad=1)
    ins.legend(fontsize=7, loc="upper left", handlelength=1.2, borderaxespad=0.1, labelspacing=0.15)
    return save(fig, "fig2_transition")


# ------------------------------------------------------------------ Fig 3
def fig3():
    rows = list(csv.DictReader(open(S2 / "orient_diffusion_round2.csv", encoding="utf-8")))
    od = jload("orient_diffusion_round2.json"); pr = jload("paper_results.json")

    def f(r, k):
        return float(r[k]) if r[k] not in ("", "nan", "NaN") else np.nan
    fig = plt.figure(figsize=(W, 4.3))
    a = fig.add_axes([0.13, 0.595, 0.85, 0.355])
    conds = [(200, 2), (200, 4), (250, 2), (350, 1), (450, 1)]
    for pitch, col, dx, D in ((400, BLACK, -0.14, 250), (500, GREY, 0.10, 300)):
        for i, (T, t) in enumerate(conds):
            r = next(r for r in rows if r["figure"] == "Fig.3" and int(r["pitch_nm"]) == pitch and int(r["T_C"]) == T
                     and float(r["t_h"]) == t)
            med, q25, q75 = f(r, "meas_median"), f(r, "meas_q25"), f(r, "meas_q75")
            a.errorbar(i + dx, med, yerr=[[med - q25], [q75 - med]], fmt="o", color=col, ms=3.2, lw=0.7, capsize=1.5,
                       label=f"imec, D = {D} nm" if i == 0 else None)
            ok = r["pass_median"] == "True"; cal = r["role"] == "calibration"
            a.plot(i + dx + 0.08, f(r, "pred_median"), marker="*" if cal else "D", ms=5 if cal else 3.0, color=ORANGE,
                   mfc=ORANGE if ok else "white", mew=0.8, ls="none")
    a.plot([], [], "D", color=ORANGE, ms=3, label="model (pass)")
    a.plot([], [], "D", color=ORANGE, mfc="white", mew=0.8, ms=3, label="model (fail)")
    a.plot([], [], "*", color=ORANGE, ms=5, label="model (calibration)")
    a.set_xticks(range(len(conds))); a.set_xticklabels([f"{T} °C, {t} h" for T, t in conds])
    a.set_xlim(-0.5, len(conds) - 0.5)
    a.set_ylabel("Bulge-out Δ$h_{max}$ (nm)"); a.set_ylim(0, 28)
    h, l = a.get_legend_handles_labels(); hd = dict(zip(l, h))
    k1 = [k for k in l if k.startswith("imec")]; k2 = [k for k in l if k.startswith("model")]
    lg = a.legend([hd[k] for k in k1], k1, loc="upper left", handlelength=1.0, borderaxespad=0.1, handletextpad=0.3)
    a.add_artist(lg)
    a.legend([hd[k] for k in k2], k2, loc="upper left", bbox_to_anchor=(0.40, 1.0), handlelength=1.0, borderaxespad=0.1, handletextpad=0.3)
    letter(a, "a", x=-0.09)
    b = fig.add_axes([0.15, 0.11, 0.32, 0.32])
    sel = sorted([r for r in rows if int(r["T_C"]) == 250 and float(r["t_h"]) == 1 and r["history"] == "self-anneal"],
                 key=lambda r: int(r["D_nm"]))
    D = np.array([int(r["D_nm"]) for r in sel])
    med = np.array([f(r, "meas_median") for r in sel]); q25 = np.array([f(r, "meas_q25") for r in sel])
    q75 = np.array([f(r, "meas_q75") for r in sel])
    b.errorbar(D, med, yerr=[med - q25, q75 - med], fmt="o", color=BLACK, ms=3.2, lw=0.7, capsize=1.5)
    for r in sel:
        ok = r["pass_median"] == "True"
        b.plot(int(r["D_nm"]) + 7, f(r, "pred_median"), "D", color=ORANGE, mfc=ORANGE if ok else "white", mew=0.8, ms=3.0)
    b.set_xlabel("Pad diameter D (nm)"); b.set_ylabel("Δ$h_{max}$ (nm)")
    b.set_xlim(90, 330); b.set_ylim(0, 16); b.set_xticks([100, 200, 300]); b.set_yticks([0, 5, 10, 15])
    b.set_title("250 °C, 1 h", fontsize=7, pad=2)
    letter(b, "b", x=-0.24)
    c = fig.add_axes([0.63, 0.11, 0.35, 0.32])
    fit = od["fit"]; wc, dw = fit["omega_c"], fit["d_omega"]
    om = np.linspace(0, 54.74, 400); fo = np.clip((om - wc) / dw, 0, 1)
    c.plot(om, fo, color=ORANGE, lw=1.3)
    c.axvspan(0, wc, color=ORANGE, alpha=0.18, lw=0)
    c.text(13, 0.02, f"$f$ = 0: {100 * od['faceted_fraction']:.1f} % of pads", fontsize=7, va="bottom")
    c.text(27, 0.50, f"$f$ < 0.5:\n{100 * pr['fraction_pads_f_below_0p5']:.0f} % of pads", fontsize=7, va="center")
    c.set_xlabel("ω to nearest <111> (°)"); c.set_ylabel("Amplitude factor $f$(ω)")
    c.set_xlim(0, 55); c.set_ylim(-0.03, 1.08); c.set_xticks([0, 15, 30, 45])
    c.set_title(f"ω$_c$ = {wc:g}°, Δω = {dw:g}°", fontsize=7, pad=2)
    letter(c, "c", x=-0.24)
    return save(fig, "fig3_diffusion")


# ------------------------------------------------------------------ Fig 4 / Fig 5 heat grids
def _grid(ax, vals, fmt, hatched=(), boxed=(), vmin=0.0, vmax=1.0, cmap="Blues", classes=None):
    Z = np.array([[vals[f"{T}C_{t}min"] for t in TIMES] for T in TEMPS])
    if classes is not None:   # discrete classes: list of (lower bound, colour), ascending
        from matplotlib.colors import ListedColormap, BoundaryNorm
        bounds = [c[0] for c in classes] + [np.inf]
        ax.imshow(Z, cmap=ListedColormap([c[1] for c in classes]), norm=BoundaryNorm(bounds, len(classes)),
                  origin="lower", aspect="auto")
        vmin, vmax = 0.0, 10.0   # keeps all cell text black
    else:
        ax.imshow(Z, cmap=cmap, vmin=vmin, vmax=vmax, origin="lower", aspect="auto")
    for i, T in enumerate(TEMPS):
        for j, t in enumerate(TIMES):
            z = Z[i, j]; frac = (z - vmin) / (vmax - vmin)
            ax.text(j, i, fmt(z), ha="center", va="center", fontsize=7, color="white" if frac > 0.6 else "black")
            if (T, t) in hatched:
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, hatch="///", ec="#9A9A9A", lw=0))
                ax.text(j, i, fmt(z), ha="center", va="center", fontsize=7, color="black",
                        bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.85))
            if (T, t) in boxed:
                ax.add_patch(Rectangle((j - 0.45, i - 0.45), 0.9, 0.9, fill=False, ec=ORANGE, lw=1.6))
    ax.set_xticks(range(3)); ax.set_xticklabels([f"{t}" for t in TIMES])
    ax.set_yticks(range(5)); ax.set_yticklabels([f"{T}" for T in TEMPS])
    ax.set_xlabel("Anneal time (min)")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)


def _pfmt(z):
    if z >= 0.95:
        return f"{np.floor(z * 1000) / 1000:.3f}"   # truncate so a value < 0.99 never prints as 0.99
    if z >= 0.005:
        return f"{z:.2f}"
    return "0"


def fig4():
    ws = jload("window_summary.json")["0.30um"]
    fig, axs = plt.subplots(1, 2, figsize=(W, 2.8), sharey=True)
    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.33, top=0.90, wspace=0.08)
    for ax, key, title in ((axs[0], "clean", "Clean surface"), (axs[1], "oxidised", "Oxidised surface")):
        d = ws[key]; hat = {tuple(x) for x in d["hatched_cells"]}
        boxed = {(250, 120), (300, 30)} if key == "clean" else set()
        _grid(ax, d["P_main"], _pfmt, hatched=hat, boxed=boxed,
              classes=[(-1.0, "#FFFFFF"), (0.5, "#DEEBF7"), (0.99, "#6BAED6")])
        ax.set_title(title, fontsize=8, pad=3)
    axs[0].set_ylabel("Anneal temperature (°C)")
    fig.text(0.02, 0.10, "Cell: P(contact). Shading: ≥ 0.99 (window), 0.5–0.99, < 0.5.", fontsize=7, ha="left", va="bottom")
    fig.text(0.02, 0.02, "Hatched: changes within b × τ$_0$ × Q.  Orange box: recommended.", fontsize=7, ha="left", va="bottom")
    return save(fig, "fig4_window300")


def fig5():
    rs = jload("paper_results.json")["recess_spec_sum_nm_300nm"]
    fig, axs = plt.subplots(1, 2, figsize=(W, 2.6), sharey=True)
    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.24, top=0.89, wspace=0.08)
    vmax = max(max(rs["clean"].values()), max(rs["oxidised"].values()))
    for ax, key, title in ((axs[0], "clean", "Clean surface"), (axs[1], "oxidised", "Oxidised surface")):
        _grid(ax, rs[key], lambda z: f"{z:g}", vmin=0.0, vmax=vmax, cmap="Greens")
        ax.set_title(title, fontsize=8, pad=3)
    axs[0].set_ylabel("Anneal temperature (°C)")
    fig.text(0.02, 0.02, "Cell value: allowable recess sum $r_t+r_b$ (nm) for P ≥ 0.99", fontsize=7,
             ha="left", va="bottom")
    return save(fig, "fig5_recess_spec")


# ------------------------------------------------------------------ Fig 6
SHORT = {"mechanism: diffusion off (elastic only)": "diffusion off",
         "orientation: no <111> faceting (f=1)": "no <111> facet (f = 1)",
         "surface: other state": "surface state",
         "liner: theta 107 (better-wetting liner)": "liner θ = 107°",
         "liner: theta 149": "liner θ = 149°",
         "recess spread: sigma 0.5 -> 1.0 nm": "recess σ 0.5 → 1 nm",
         "recess mean: 2.5 -> 3.5 nm": "recess mean +1 nm",
         "elastic factor b: 0.60 -> 1.0 (range)": "elastic factor b",
         "diffusion kinetics tau0 20 -> 100 s": "kinetics τ$_0$ 20 → 100 s",
         "diffusion Q 20.7 -> 15 kcal/mol": "kinetics Q 20.7 → 15"}


def fig6():
    ws = jload("window_summary.json"); pr = jload("paper_results.json")
    fc54, fc30 = ws["0.54um"]["clean"]["factor_cells_changed"], ws["0.30um"]["clean"]["factor_cells_changed"]
    base = "time/temperature axis: open cells at main setting"
    names = sorted([k for k in fc30 if k != base], key=lambda k: (fc30[k], fc54[k]))
    fig = plt.figure(figsize=(W, 4.0))
    a = fig.add_axes([0.47, 0.55, 0.50, 0.40])
    y = np.arange(len(names))
    a.barh(y + 0.19, [fc30[k] for k in names], height=0.36, color=BLUE, label="0.30 µm")
    a.barh(y - 0.19, [fc54[k] for k in names], height=0.36, color=SKY, label="0.54 µm")
    for yy, k in zip(y, names):
        for val, off in ((fc30[k], 0.19), (fc54[k], -0.19)):
            if val == 0:
                a.plot(0.06, yy + off, "|", color=GREY, ms=3)
    a.set_yticks(y); a.set_yticklabels([SHORT.get(k, k) for k in names])
    a.set_xlabel("Window cells changed (of 15)")
    a.set_xlim(0, 10); a.legend(loc="lower right")
    letter(a, "a", x=-0.76)
    of = pr["orientation_floor_300nm"]; n = ws["settings"]["n"]
    cells = [(T, t) for T in TEMPS for t in TIMES if T >= 250]
    b = fig.add_axes([0.17, 0.15, 0.80, 0.27])
    x = np.arange(len(cells)); floor = 1.0 / n
    pf = [of[f"{T}C_{t}min"]["P_open_facet"] for T, t in cells]
    pn = [of[f"{T}C_{t}min"]["P_open_no_facet"] for T, t in cells]
    b.plot(x, pf, "o", color=ORANGE, ms=3.5, label="with <111> facet term")
    b.plot(x, [p if p > 0 else floor for p in pn], "v", color=GREEN, ms=3.5, mfc="white", mew=0.8,
           label=f"no facet term (0 of {n // 1000}k drawn at 1/n)")
    b.axhline(floor, color=GREY, lw=0.5, ls=":")
    b.set_yscale("log"); b.set_ylim(floor * 0.5, 2.0)
    b.set_yticks([1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1])
    b.set_yticklabels(["10$^{-5}$", "10$^{-4}$", "10$^{-3}$", "10$^{-2}$", "0.1", "1"])
    b.set_xticks(x); b.set_xticklabels([f"{T}\n{t}" for T, t in cells])
    b.set_xlabel("Anneal T (°C) / time (min), 300 nm pads"); b.set_ylabel("Open pairs")
    b.legend(loc="upper right", handlelength=1.0, borderaxespad=0.1)
    letter(b, "b", x=-0.06)
    return save(fig, "fig6_factors")


FIGS = {"fig1_architecture": fig1, "fig2_transition": fig2, "fig3_diffusion": fig3,
        "fig4_window300": fig4, "fig5_recess_spec": fig5, "fig6_factors": fig6}

if __name__ == "__main__":
    for name, fn in FIGS.items():
        plt.close(fn()); print("ok", name)
    (OUT / "SOURCES.json").write_text(json.dumps(SOURCES, indent=1), encoding="utf-8")
