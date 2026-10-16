r"""Stage 2 D: contact-stage process window with uncertainty (main doc section 10 procedure).

Pad pair: u_el,i = b * k(Ez_i) * (T - 25)  (FEM fit, bonded sidewall, array cell; results/stage2/predict_<size>_fit.json)
          h_d,i  = s_ox * a_liner * 0.0022 * (theta_eff - 90) * D * f(omega_i) * (1 - exp(-t/tau(D, T; tau0, Q)))
contact if u_el,1 + u_el,2 + h_d,1 + h_d,2 >= r_1 + r_2, r_i ~ N(2.5, 0.5^2) nm (IRPS 2026); orientation uniform on the sphere.
Window = cells with P_contact >= 0.99 on T {200..400} x t {5, 30, 120} min.  Main setting: b 0.69, tau0 60 s, Q 20.7,
liner Ta (theta 123), f(omega) from round 2 (exploratory).  Uncertainty set: b {0.60, 0.69, 0.93, 1.0} x tau0 {20, 60, 100}
x Q {20.7, 15} -> cells whose membership changes are hatched.  Factor ranking = cells changed when each factor is varied.
Usage: python src\stage2\stage2_window.py [--n 200000]
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stage2_predict as P  # noqa: E402
import stage2_orient_diffusion as O  # noqa: E402

REPO = HERE.parents[1]
OUT = REPO / "results" / "stage2"
FIG = REPO / "results" / "figures"
TS = (200, 250, 300, 350, 400); TMIN = (5, 30, 120)
B_GRID = (0.60, 0.69, 0.93, 1.0); TAU0_GRID = (20.0, 60.0, 100.0); Q_GRID = (20.7, 15.0)
SURF = {"clean": 1.0, "oxidised": 0.45}
LINER = {"Ta_123": 1.0, "theta107": (107 - 90) / 33.0, "theta149": (149 - 90) / 33.0}
P_WIN = 0.99
SIZES = (("0.54um", 0.54), ("0.30um", 0.30))


def kin(D_nm, T_C, t_min, tau0, Q):
    ds = math.exp(-Q / P.R_GAS * (1 / (T_C + 273.15) - 1 / 623.15))
    tau = tau0 * (D_nm / 200.0) ** 3.7 / ds
    return 1.0 - math.exp(-t_min * 60.0 / tau)


class Pairs:
    def __init__(self, n, seed, fit_coef, oc, dw, recess=(2.5, 0.5), facet=True, k_fn=None):
        rng = np.random.default_rng(seed)
        self.rng = rng
        c11, c12, c44 = 168400.0, 121400.0, 75400.0
        den = (c11 - c12) * (c11 + 2 * c12); s11, s12, s44 = (c11 + c12) / den, -c12 / den, 1 / c44
        self.k, self.f = [], []
        for _ in range(2):
            v = rng.normal(size=(n, 3)); v /= np.linalg.norm(v, axis=1)[:, None]
            l, m, nn = np.abs(v).T
            ez = 1.0 / (s11 - 2 * (s11 - s12 - s44 / 2) * (l * l * m * m + m * m * nn * nn + nn * nn * l * l)) / 1000.0
            om = np.degrees(np.arccos(np.clip(np.abs(v @ O.V111.T).max(axis=1), -1, 1)))
            self.k.append(k_fn(v) if k_fn is not None else np.polyval(fit_coef, ez))
            self.f.append(O.f_of(om, oc, dw) if facet else np.ones(n))
        self.g = rng.normal(recess[0], recess[1], n) + rng.normal(recess[0], recess[1], n)
        self.ksum = self.k[0] + self.k[1]; self.fsum = self.f[0] + self.f[1]

    def P(self, D_nm, T, t_min, b, s_ox, a_liner, theta, tau0, Q, diffusion=True):
        u = b * self.ksum * (T - 25.0)
        h = (s_ox * a_liner * 0.0022 * (theta - 90.0) * D_nm * kin(D_nm, T, t_min, tau0, Q)) * self.fsum if diffusion else 0.0
        return float(np.mean(u + h >= self.g))


def window(pairs, D, b, s_ox, a_liner, theta, tau0, Q, **kw):
    return {(T, t): pairs.P(D, T, t, b, s_ox, a_liner, theta, tau0, Q, **kw) for T in TS for t in TMIN}


def cells(w):
    return {c for c, p in w.items() if p >= P_WIN}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200_000)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    orient = json.loads((OUT / "orient_diffusion_round2.json").read_text())
    theta, oc, dw = orient["fit"]["theta_eff"], orient["fit"]["omega_c"], orient["fit"]["d_omega"]
    summary = dict(settings=dict(theta_eff=theta, omega_c=oc, d_omega=dw, main=dict(b=0.69, tau0=60, Q=20.7, liner="Ta_123"),
                                 uncertainty=dict(b=B_GRID, tau0=TAU0_GRID, Q=Q_GRID), P_window=P_WIN, recess="N(2.5,0.5^2) per pad",
                                 orientation_term="exploratory round 2 (not validated)", n=a.n))
    rows = []
    for label, size in SIZES:
        D = size * 1000.0
        coef = np.array(json.loads((OUT / f"predict_{label}_fit.json").read_text())["fit"]["coef"])
        pr = Pairs(a.n, a.seed, coef, oc, dw)
        res = dict()
        for surf, s_ox in SURF.items():
            main_w = window(pr, D, 0.69, s_ox, 1.0, theta, 60.0, 20.7)
            main_c = cells(main_w)
            # uncertainty set
            union, inter = set(), None
            for b, tau0, Q in itertools.product(B_GRID, TAU0_GRID, Q_GRID):
                w = window(pr, D, b, s_ox, 1.0, theta, tau0, Q); c = cells(w)
                union |= c; inter = c if inter is None else inter & c
                for (T, t), p in w.items():
                    rows.append(dict(size_um=size, surface=surf, liner="Ta_123", b=b, tau0_s=tau0, Q_kcal=Q, T_C=T, t_min=t, P_contact=p, in_window=p >= P_WIN))
            hatched = sorted(union - inter)
            # factor ranking (cells changed vs main, main surface setting)
            variants = {
                "mechanism: diffusion off (elastic only)": window(pr, D, 0.69, s_ox, 1.0, theta, 60.0, 20.7, diffusion=False),
                "orientation: no <111> faceting (f=1)": window(Pairs(a.n, a.seed, coef, oc, dw, facet=False), D, 0.69, s_ox, 1.0, theta, 60.0, 20.7),
                "surface: other state": window(pr, D, 0.69, SURF["oxidised" if surf == "clean" else "clean"], 1.0, theta, 60.0, 20.7),
                "liner: theta 107 (better-wetting liner)": window(pr, D, 0.69, s_ox, LINER["theta107"], theta, 60.0, 20.7),
                "liner: theta 149": window(pr, D, 0.69, s_ox, LINER["theta149"], theta, 60.0, 20.7),
                "recess spread: sigma 0.5 -> 1.0 nm": window(Pairs(a.n, a.seed, coef, oc, dw, recess=(2.5, 1.0)), D, 0.69, s_ox, 1.0, theta, 60.0, 20.7),
                "recess mean: 2.5 -> 3.5 nm": window(Pairs(a.n, a.seed, coef, oc, dw, recess=(3.5, 0.5)), D, 0.69, s_ox, 1.0, theta, 60.0, 20.7),
                "elastic factor b: 0.60 -> 1.0 (range)": None,
                "diffusion kinetics tau0 20 -> 100 s": None,
                "diffusion Q 20.7 -> 15 kcal/mol": None,
            }
            rank = {}
            for name, w in variants.items():
                if w is not None:
                    rank[name] = len(cells(w) ^ main_c)
            rank["elastic factor b: 0.60 -> 1.0 (range)"] = len(cells(window(pr, D, 0.60, s_ox, 1.0, theta, 60.0, 20.7)) ^ cells(window(pr, D, 1.0, s_ox, 1.0, theta, 60.0, 20.7)))
            rank["diffusion kinetics tau0 20 -> 100 s"] = len(cells(window(pr, D, 0.69, s_ox, 1.0, theta, 20.0, 20.7)) ^ cells(window(pr, D, 0.69, s_ox, 1.0, theta, 100.0, 20.7)))
            rank["diffusion Q 20.7 -> 15 kcal/mol"] = len(cells(window(pr, D, 0.69, s_ox, 1.0, theta, 60.0, 15.0)) ^ main_c)
            # time/temperature: the window itself (how many of the 15 cells are open)
            rank["time/temperature axis: open cells at main setting"] = len(main_c)
            # lowest T/t that opens the window (recipe)
            opened = sorted(main_c, key=lambda c: (c[0], c[1]))
            recipe = []
            for T in TS:
                ts_ok = [t for t in TMIN if (T, t) in main_c]
                if ts_ok:
                    recipe.append(f"{T} °C x {min(ts_ok)} min")
            res[surf] = dict(P_main={f"{T}C_{t}min": p for (T, t), p in main_w.items()}, window_main=sorted(main_c), window_always=sorted(inter),
                             window_any=sorted(union), hatched_cells=hatched, factor_cells_changed=rank, recipe_min_time_per_T=recipe,
                             P_faceted_pair=float(np.mean((pr.f[0] == 0) | (pr.f[1] == 0))))
        summary[label] = res
    # imec consistency check for 0.54 um: bonding anneal 350 C (after a 250 C step), recess 2-3 nm/pad -> must be inside the clean window
    w054 = summary["0.54um"]["clean"]
    imec_cells = [(350, 120), (350, 30)]
    summary["imec_check_0.54um"] = dict(condition="imec post-bond anneal 350 C (DM2023; ECTC sub-2um: 250 C then 350 C), clean activated surface, recess 2-3 nm/pad",
                                        cells=[f"{T}C_{t}min" for T, t in imec_cells],
                                        P=[w054["P_main"][f"{T}C_{t}min"] for T, t in imec_cells],
                                        consistent=all(w054["P_main"][f"{T}C_{t}min"] >= P_WIN for T, t in imec_cells))
    json.dump(summary, open(OUT / "window_summary.json", "w"), indent=1, default=float)
    keys = list(rows[0])
    (OUT / "window_rows.csv").write_text(",".join(keys) + "\n" + "".join(",".join(f"{r[k]:.4g}" if isinstance(r[k], float) else str(r[k]) for k in keys) + "\n" for r in rows))
    for label, _ in SIZES:
        for surf in SURF:
            s = summary[label][surf]
            print(f"{label} {surf}: window {len(s['window_main'])}/15 cells, always {len(s['window_always'])}, hatched {s['hatched_cells']}, "
                  f"recipe {s['recipe_min_time_per_T']}, faceted-pair fraction {s['P_faceted_pair']:.3f}")
            print("   ranking:", sorted(s["factor_cells_changed"].items(), key=lambda kv: -kv[1]))
    print("imec check:", summary["imec_check_0.54um"])
    # figures
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        for label, _ in SIZES:
            fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
            for ax, (surf, title) in zip(axs, (("clean", "main recipe: clean surface"), ("oxidised", "sensitivity: surface oxide not controlled"))):
                s = summary[label][surf]
                Pm = np.array([[s["P_main"][f"{T}C_{t}min"] for T in TS] for t in TMIN])
                im = ax.imshow(Pm, origin="lower", vmin=0, vmax=1, cmap="Blues", aspect="auto", extent=[-0.5, 4.5, -0.5, 2.5])
                for i, t in enumerate(TMIN):
                    for j, T in enumerate(TS):
                        ax.text(j, i, f"{Pm[i, j]:.2f}", ha="center", va="center", fontsize=6.5, color="w" if Pm[i, j] > 0.6 else "k")
                        if [T, t] in [list(c) for c in s["hatched_cells"]]:
                            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, hatch="///", edgecolor="#d62728", lw=1.2))
                ax.set_xticks(range(5)); ax.set_xticklabels([str(T) for T in TS]); ax.set_yticks(range(3)); ax.set_yticklabels([str(t) for t in TMIN])
                ax.set_title(title, fontsize=7.5); ax.set_xlabel("anneal T (°C)")
            axs[0].set_ylabel("anneal time (min)")
            cb = fig.colorbar(im, ax=axs, shrink=0.9); cb.set_label("P(contact): b 0.69, τ₀ 60 s, Q 20.7, Ta liner")
            fig.suptitle(f"{label}: hatched = changes within b {{0.60–1.0}} × τ₀ {{20–100 s}} × Q {{20.7, 15}}; orientation term exploratory", fontsize=7.5)
            fig.savefig(FIG / f"s2_window_{label}.png", dpi=300, bbox_inches="tight"); plt.close(fig)
        # factor ranking figure (clean surface, both sizes)
        fig, ax = plt.subplots(figsize=(7, 3.2))
        names = list(summary["0.54um"]["clean"]["factor_cells_changed"])
        names = [n for n in names if not n.startswith("time/temperature")]
        y = np.arange(len(names))
        for off, (label, _) in zip((-0.18, 0.18), SIZES):
            vals = [summary[label]["clean"]["factor_cells_changed"][n] for n in names]
            ax.barh(y + off, vals, height=0.36, label=label)
        ax.set_yticks(y); ax.set_yticklabels(names, fontsize=6.5); ax.invert_yaxis(); ax.set_xlabel("window cells changed (of 15), clean surface")
        ax.legend(fontsize=7, frameon=False); fig.tight_layout(); fig.savefig(FIG / "s2_factor_ranking.png", dpi=300); plt.close(fig)
    except Exception as exc:
        print("figure skipped:", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
