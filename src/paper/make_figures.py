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
    "fig3": ["results/stage2/diffusion_validation_rev1.csv (revision 1: median_nm, q25, q75, pred_nm, pass, role)",
             "results/stage2/v2/f_omega_variants.json (variants_used_for_windows, fits[*].params)"],
    "fig4": ["results/stage2/v2/boundary_curves.json (T, surfaces.clean/oxidised main, band_min, band_max, T_at_*min.robust; "
             "worst_orientation V4/V5 boundary)"],
    "fig5": ["results/stage2/v2/f_omega_variants.json (windows['0.30um'].allowable_recess_clean: r_per_pad_prob99, r_per_pad_worst)"],
    "fig6": ["results/stage2/v2/boundary_curves.json (factor_shift_C: 30min, 120min, time_ratio_250C; "
             "interface and mechanism entries excluded)"],
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
             ("Test (held-out)", "evaluated once"), ("Prediction (Monte Carlo)", "300 nm window, recess spec")]
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
    bx.text(9.8, 5.06, "criteria fixed in advance", fontsize=7, color=BLUE, ha="right", va="bottom")
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
    ins.set_xlabel("Recess sum (nm)", fontsize=7, labelpad=1); ins.set_ylabel("Elastic limit (µm)", fontsize=7, labelpad=1)
    ins.tick_params(labelsize=7, pad=1)
    ins.legend(fontsize=7, loc="upper left", handlelength=1.2, borderaxespad=0.1, labelspacing=0.15)
    return save(fig, "fig2_transition")


# ------------------------------------------------------------------ Fig 3
F_OMEGA = {   # family and fitted parameters of the six f(omega) variants (src/v2/f_omega_variants.py, fits[...]["params"])
    "V2 step facet + scatter": "ramp", "V3 ramp + scatter": "ramp", "V4 floor 0.25 + scatter": "floor",
    "V5 sigmoid": "sigmoid", "V6 step facet, Fig5a tail": "ramp", "V7 ramp, Fig5a tail": "ramp"}
F_LABEL = {"V2 step facet + scatter": "V2 step", "V3 ramp + scatter": "V3 ramp", "V4 floor 0.25 + scatter": "V4 floor",
           "V5 sigmoid": "V5 sigmoid", "V6 step facet, Fig5a tail": "V6 step*", "V7 ramp, Fig5a tail": "V7 ramp*"}
F_COL = {"V2 step facet + scatter": GREY, "V3 ramp + scatter": BLACK, "V4 floor 0.25 + scatter": ORANGE,
         "V5 sigmoid": BLUE, "V6 step facet, Fig5a tail": SKY, "V7 ramp, Fig5a tail": GREEN}


def f_omega(fam, om, p):
    def ramp(o, q):
        oc, dw = q
        return (o > oc).astype(float) if dw <= 1e-9 else np.clip((o - oc) / dw, 0, 1)
    if fam == "ramp":
        return ramp(om, p)
    if fam == "floor":
        return p[0] + (1 - p[0]) * ramp(om, p[1:])
    return 1.0 / (1.0 + np.exp(-(om - p[0]) / max(p[1], 1e-6)))


def fig3():
    rows = list(csv.DictReader(open(S2 / "diffusion_validation_rev1.csv", encoding="utf-8")))
    fv = jload("v2/f_omega_variants.json")

    def f(r, k):
        return float(r[k]) if r[k] not in ("", "nan", "NaN") else np.nan
    fig = plt.figure(figsize=(W, 4.2))
    a = fig.add_axes([0.13, 0.60, 0.85, 0.35])
    conds = [(200, 2), (200, 4), (250, 2), (350, 1), (450, 1)]
    for pitch, col, dx, D in ((400, BLACK, -0.14, 250), (500, GREY, 0.10, 300)):
        for i, (T, t) in enumerate(conds):
            r = next(r for r in rows if r["figure"] == "Fig.3" and int(r["pitch_nm"]) == pitch and int(r["T_C"]) == T
                     and float(r["t_h"]) == t)
            med, q25, q75 = f(r, "median_nm"), f(r, "q25"), f(r, "q75")
            a.errorbar(i + dx, med, yerr=[[med - q25], [q75 - med]], fmt="o", color=col, ms=3.2, lw=0.7, capsize=1.5,
                       label=f"imec, D = {D} nm" if i == 0 else None)
            ok = r["pass"] == "True"; cal = r["role"] == "calibration"
            a.plot(i + dx + 0.08, f(r, "pred_nm"), marker="*" if cal else "D", ms=5 if cal else 3.0, color=ORANGE,
                   mfc=ORANGE if (ok or cal) else "white", mew=0.8, ls="none")
    a.plot([], [], "D", color=ORANGE, ms=3, label="model, pass")
    a.plot([], [], "D", color=ORANGE, mfc="white", mew=0.8, ms=3, label="model, fail")
    a.plot([], [], "*", color=ORANGE, ms=5, label="model, training point")
    a.set_xticks(range(len(conds))); a.set_xticklabels([f"{T} °C, {t} h" for T, t in conds])
    a.set_xlim(-0.5, len(conds) - 0.5)
    a.set_ylabel("Bulge-out Δ$h_{max}$ (nm)"); a.set_ylim(0, 26)
    h, l = a.get_legend_handles_labels(); hd = dict(zip(l, h))
    k1 = [k for k in l if k.startswith("imec")]; k2 = [k for k in l if k.startswith("model")]
    lg = a.legend([hd[k] for k in k1], k1, loc="upper left", handlelength=1.0, borderaxespad=0.1, handletextpad=0.3)
    a.add_artist(lg)
    a.legend([hd[k] for k in k2], k2, loc="upper left", bbox_to_anchor=(0.40, 1.0), handlelength=1.0, borderaxespad=0.1,
             handletextpad=0.3)
    letter(a, "a", x=-0.09)
    b = fig.add_axes([0.15, 0.10, 0.31, 0.33])
    sel = sorted([r for r in rows if int(r["T_C"]) == 250 and float(r["t_h"]) == 1 and r["history"] == "self-anneal"
                  and r["cu"] == "std" and r["role"] == "held-out"], key=lambda r: int(r["D_nm"]))
    D = np.array([int(r["D_nm"]) for r in sel])
    med = np.array([f(r, "median_nm") for r in sel]); q25 = np.array([f(r, "q25") for r in sel])
    q75 = np.array([f(r, "q75") for r in sel])
    b.errorbar(D, med, yerr=[med - q25, q75 - med], fmt="o", color=BLACK, ms=3.2, lw=0.7, capsize=1.5)
    for r in sel:
        ok = r["pass"] == "True"
        b.plot(int(r["D_nm"]) + 7, f(r, "pred_nm"), "D", color=ORANGE, mfc=ORANGE if ok else "white", mew=0.8, ms=3.0)
    b.set_xlabel("Pad diameter D (nm)"); b.set_ylabel("Δ$h_{max}$ (nm)")
    b.set_xlim(90, 330); b.set_ylim(0, 16); b.set_xticks([100, 200, 300]); b.set_yticks([0, 5, 10, 15])
    b.set_title("250 °C, 1 h", fontsize=7, pad=2)
    letter(b, "b", x=-0.24)
    c = fig.add_axes([0.62, 0.10, 0.36, 0.33])
    om = np.linspace(0, 54.74, 600)
    for name in fv["variants_used_for_windows"]:
        p = fv["fits"][name]["params"]
        c.plot(om, f_omega(F_OMEGA[name], om, p), color=F_COL[name], lw=1.0, label=F_LABEL[name])
    c.set_xlabel("ω to nearest <111> (°)"); c.set_ylabel("Amplitude factor $f$(ω)")
    c.set_xlim(0, 55); c.set_ylim(-0.03, 1.08); c.set_xticks([0, 15, 30, 45])
    c.legend(loc="lower right", fontsize=7, handlelength=1.0, handletextpad=0.3, borderaxespad=0.0, labelspacing=0.1)
    c.set_title("six $f$(ω) variants", fontsize=7, pad=2)
    letter(c, "c", x=-0.24)
    return save(fig, "fig3_diffusion")


# ------------------------------------------------------------------ Fig 4 (boundary curves, JSON only)
def _clip_top(v, top):
    a = np.array(v, dtype=float)
    return np.where(np.isfinite(a), a, top)


def fig4():
    bc = jload("v2/boundary_curves.json")
    T = np.array(bc["T"]); top = 1e4
    fig, axs = plt.subplots(1, 2, figsize=(W, 2.45), sharey=True)
    fig.subplots_adjust(left=0.13, right=0.97, bottom=0.17, top=0.80, wspace=0.07)
    for ax, key, title in ((axs[0], "clean", "Clean surface"), (axs[1], "oxidised", "Oxidised surface")):
        s = bc["surfaces"][key]
        lo = np.array(s["band_min"], float); hi = _clip_top(s["band_max"], top)
        ok = np.isfinite(lo)
        ax.fill_between(T[ok], lo[ok], hi[ok], color=SKY, alpha=0.35, lw=0, label="all model combinations")
        ax.plot(T, hi, color=BLUE, lw=0.8)
        ax.plot(T, np.array(s["main"], float), color=BLACK, lw=1.2, label="main setting")
        if key == "clean":
            for name, col, lab in (("V4 floor 0.25 + scatter", ORANGE, "worst orient., V4"),
                                   ("V5 sigmoid", GREEN, "worst orient., V5")):
                wo = bc["worst_orientation"][name]
                ax.plot(T, np.array(wo["boundary"], float), color=col, lw=0.9, ls=(0, (3, 1.5)), label=lab)
        for tm, kk in ((5, "T_at_5min"), (30, "T_at_30min"), (120, "T_at_120min")):
            Tr = s[kk]["robust"]
            if Tr is not None and np.isfinite(Tr):
                ax.plot(Tr, tm, "o", color=BLUE, ms=2.8, mfc="white", mew=0.8, zorder=5)
                ax.text(Tr - 2, tm * 1.12, f"{Tr:.0f}", fontsize=7, color=BLUE, ha="right", va="bottom")
        ax.axvspan(200, 250, color="#E6E6E6", lw=0, zorder=0)
        ax.text(225, 1.25, "outside\ndata", fontsize=7, color=GREY, ha="center", va="bottom")
        ax.set_xlim(200, 400); ax.set_yscale("log"); ax.set_ylim(1, 240)
        ax.set_xticks([200, 300, 400] if key == "clean" else [300, 400]); ax.set_xticks([250, 350], minor=True)
        ax.set_title(title, fontsize=7, pad=2)
        ax.set_xlabel("Anneal T (°C)")
    axs[0].set_yticks([1, 5, 30, 120]); axs[0].set_yticklabels(["1", "5", "30", "120"])
    from matplotlib.ticker import NullFormatter
    axs[0].yaxis.set_minor_formatter(NullFormatter())
    axs[0].set_ylabel("Min. anneal time for P ≥ 0.99 (min)")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, fontsize=7, handlelength=1.6, borderaxespad=0.1, labelspacing=0.15,
               columnspacing=1.0, bbox_to_anchor=(0.55, 1.0))
    letter(axs[0], "a", x=-0.02); letter(axs[1], "b", x=-0.02)
    return save(fig, "fig4_window300")


# ------------------------------------------------------------------ Fig 5 (allowable recess per pad)
RECIPES = [("250C_120min", "250 °C\n2 h"), ("300C_30min", "300 °C\n30 min"), ("350C_30min", "350 °C\n30 min"),
           ("400C_30min", "400 °C\n30 min")]


def fig5():
    fv = jload("v2/f_omega_variants.json")
    ar = fv["windows"]["0.30um"]["allowable_recess_clean"]
    fig, ax = plt.subplots(figsize=(W, 2.15))
    fig.subplots_adjust(left=0.13, right=0.985, bottom=0.22, top=0.97)
    x = np.arange(len(RECIPES))
    groups = (("probability (P ≥ 0.99)", "r_per_pad_prob99", lambda k: True, BLUE, "o", -0.22),
              ("worst orientation, $f$(0) > 0", "r_per_pad_worst", lambda k: k.startswith(("V4", "V5")), ORANGE, "s", 0.0),
              ("worst orientation, $f$(0) = 0", "r_per_pad_worst", lambda k: not k.startswith(("V4", "V5")), GREY, "v", 0.22))
    for lab, key, sel, col, mk, dx in groups:
        for i, (rk, _) in enumerate(RECIPES):
            vals = [ar[k][rk][key] for k in ar if sel(k)]
            ax.plot([i + dx, i + dx], [min(vals), max(vals)], color=col, lw=2.2, alpha=0.45, solid_capstyle="butt")
            ax.plot([i + dx] * len(vals), vals, mk, color=col, ms=2.6, mfc="white" if mk != "o" else col, mew=0.7,
                    label=lab if i == 0 else None)
    ax.set_xticks(x); ax.set_xticklabels([r[1] for r in RECIPES])
    ax.set_xlim(-0.5, len(RECIPES) - 0.5); ax.set_ylim(0, 10)
    ax.set_ylabel("Allowable recess per pad (nm)")
    ax.legend(loc="upper left", handlelength=1.0, borderaxespad=0.1, labelspacing=0.2)
    return save(fig, "fig5_recess_spec")


# ------------------------------------------------------------------ Fig 6 (factor shifts, JSON only)
F6 = [("anneal kinetics: Q 20.7 vs 13.4 kcal/mol", "activation energy $Q$"),
      ("anneal kinetics: tau0 100 vs 20 s", "rate constant τ$_0$"),
      ("liner wetting: theta 107 vs 149 deg", "liner contact angle"),
      ("surface: oxidised (s_ox 0.45) vs clean", "surface oxide"),
      ("orientation-tail shape: spread over 6 f(omega)", "tail shape, $f$(ω)"),
      ("random: recess mean 3.5 vs 2.5 nm/pad", "recess mean"),
      ("random: orientation tail present vs absent (f = 1)", "orientation tail"),
      ("random: recess spread sigma 1.0 vs 0.5 nm/pad", "recess spread σ"),
      ("elastic factor b: 0.60 vs 1.0", "elastic factor $b$")]


def fig6():
    fs = jload("v2/boundary_curves.json")["factor_shift_C"]
    keys = sorted([k for k, _ in F6], key=lambda k: -fs[k]["120min"])
    lab = dict(F6)
    fig = plt.figure(figsize=(W, 2.55))
    a = fig.add_axes([0.335, 0.17, 0.39, 0.76]); b = fig.add_axes([0.75, 0.17, 0.21, 0.76], sharey=a)
    y = np.arange(len(keys))[::-1]
    a.barh(y + 0.19, [fs[k]["30min"] for k in keys], height=0.36, color=SKY, label="30 min")
    a.barh(y - 0.19, [fs[k]["120min"] for k in keys], height=0.36, color=BLUE, label="2 h")
    a.set_yticks(y); a.set_yticklabels([lab[k] for k in keys])
    a.set_xlim(0, 52); a.set_xticks([0, 20, 40])
    a.set_xlabel("Boundary shift (°C)")
    a.legend(loc="lower right", handlelength=1.0, borderaxespad=0.1)
    r = [fs[k]["time_ratio_250C"] for k in keys]
    b.barh(y, r, height=0.5, color=GREY, left=0)
    b.set_xscale("log"); b.set_xlim(1, 9); b.set_xticks([1, 2, 5]); b.set_xticklabels(["1", "2", "5"])
    from matplotlib.ticker import NullFormatter
    b.xaxis.set_minor_formatter(NullFormatter())
    for yy, v in zip(y, r):
        b.text(v * 1.04, yy, f"×{v:.1f}", fontsize=7, va="center", ha="left")
    b.tick_params(axis="y", labelleft=False, length=0)
    b.set_xlabel("Time ratio, 250 °C")
    letter(a, "a", x=-0.02); letter(b, "b", x=-0.02)
    return save(fig, "fig6_factors")


FIGS = {"fig1_architecture": fig1, "fig2_transition": fig2, "fig3_diffusion": fig3,
        "fig4_window300": fig4, "fig5_recess_spec": fig5, "fig6_factors": fig6}

if __name__ == "__main__":
    for name, fn in FIGS.items():
        plt.close(fn()); print("ok", name)
    (OUT / "SOURCES.json").write_text(json.dumps(SOURCES, indent=1), encoding="utf-8")
