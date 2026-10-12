r"""
Step 15: orientation-aware Cu-Cu contact check (pre-registration: docs/step15_orientation_contact.md).

Inputs : results/R63..R71/record.json (lin13, 1 um pad, bonded, elastic, du from 25 to 200 C)
Outputs: results/diagnostics/step15_contact.csv / step15_contact.json
         results/figures/s15_du_vs_Ez.png, s15_pcontact_vs_T.png, s15_pcontact_map.png
Usage  : python src\stage2\s15_contact.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "stage1"))
import stage1_pipeline as S  # noqa: E402  (paper elastic constants, closed-form E_z)
import lin13 as L13          # noqa: E402  (orientation table)

RES = ROOT / "results"
DT_LIN = 200.0 - 25.0
T0 = 25.0
ORI_RUNS = ["R63", "R64", "R65", "R66", "R67", "R68", "R69", "R70"]
N_MC, SEED = 200_000, 0
G0S = (3.0, 5.0, 8.0)
CVS = (0.0, 0.1, 0.2)


def du(rid):
    return json.loads((RES / rid / "record.json").read_text())["result"]["du"]


def ez_of(hkl):
    return S.Ez_closed_form(hkl) / 1000.0


def ez_random(n, rng):
    v = rng.normal(size=(n, 3))
    v /= np.linalg.norm(v, axis=1)[:, None]
    l, m, nn = np.abs(v).T
    c11, c12, c44 = S.C11, S.C12, S.C44
    den = (c11 - c12) * (c11 + 2 * c12)
    s11, s12, s44 = (c11 + c12) / den, -c12 / den, 1 / c44
    g = l * l * m * m + m * m * nn * nn + nn * nn * l * l
    return 1.0 / (s11 - 2 * (s11 - s12 - s44 / 2) * g) / 1000.0


def main():
    det = abs(du("R63") - du("R53"))
    ez = np.array([ez_of(L13.ORIENT[L13.RUN_BY_ID[r]["orient"]]) for r in ORI_RUNS])
    d = np.array([du(r) for r in ORI_RUNS])
    coef = np.polyfit(ez, d, 2)
    fit = np.polyval(coef, ez)
    r2 = 1 - np.sum((d - fit) ** 2) / np.sum((d - d.mean()) ** 2)
    k_hill = du("R71") / DT_LIN
    rng = np.random.default_rng(SEED)
    k1 = np.polyval(coef, ez_random(N_MC, rng)) / DT_LIN
    k2 = np.polyval(coef, ez_random(N_MC, rng)) / DT_LIN
    ksum = k1 + k2
    k_lo = min(np.polyval(coef, np.linspace(66.69, 191.15, 400))) / DT_LIN
    rows = []
    curves = {}
    for g0 in G0S:
        T_avg = T0 + g0 / (2 * k_hill)
        T_worst = T0 + g0 / (2 * k_lo)
        for cv in CVS:
            eps = rng.normal(0.0, cv, N_MC) if cv > 0 else np.zeros(N_MC)
            T_req = T0 + g0 * (1 + eps) / ksum           # temperature at which this pair closes
            P_avg = float(np.mean(T_req <= T_avg))
            T99, T999 = (float(np.quantile(T_req, q)) for q in (0.99, 0.999))
            rows.append(dict(g0_nm=g0, cv=cv, T_avg=T_avg, P_contact_at_T_avg=P_avg, T99=T99, T999=T999,
                             T_worst_orientation=float(T_worst), overshoot99_K=T99 - T_avg,
                             overshoot99_rel=(T99 - T0) / (T_avg - T0)))
            curves[(g0, cv)] = np.sort(T_req)
    out = dict(determinism_R63_vs_R53_nm=det, Ez=ez.tolist(), du=d.tolist(), fit_coef=coef.tolist(), fit_R2=r2,
               fit_max_resid_nm=float(np.max(np.abs(d - fit))), du_hill=du("R71"), k_hill_nm_per_K=k_hill,
               k_pad_range_nm_per_K=[float(k1.min()), float(k1.max())], k_lo=k_lo, rows=rows,
               H15_supported=all(r["P_contact_at_T_avg"] < 0.99 for r in rows))
    dg = RES / "diagnostics"
    dg.mkdir(parents=True, exist_ok=True)
    (dg / "step15_contact.json").write_text(json.dumps(out, indent=1))
    keys = list(rows[0])
    (dg / "step15_contact.csv").write_text(",".join(keys) + "\n" + "".join(
        ",".join(f"{r[k]:.6g}" for k in keys) + "\n" for r in rows))
    figures(ez, d, coef, k_hill, curves, ksum, rng)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print({k: round(v, 3) for k, v in r.items()})
    print("H15 (T_avg does not guarantee contact):", "SUPPORTED" if out["H15_supported"] else "NOT SUPPORTED")


def figures(ez, d, coef, k_hill, curves, ksum, rng):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    fd = RES / "figures"
    fd.mkdir(parents=True, exist_ok=True)
    # 1: du vs E_z
    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    x = np.linspace(60, 195, 200)
    ax.axhspan(2.3 - 0.4, 2.3 + 0.4, color="0.88", lw=0, label="Lin 2025, 1 µm (2.3 ± 0.4 nm)")
    ax.plot(x, np.polyval(coef, x), color="C0", lw=1.2, label="quadratic fit")
    ax.plot(ez, d, "o", color="C0", ms=4, label="FEA, anisotropic Cu")
    ax.axhline(k_hill * DT_LIN, color="C3", ls="--", lw=1, label="FEA, isotropic Hill Cu")
    ax.set_xlabel("Out-of-plane modulus $E_z$ (GPa)")
    ax.set_ylabel("Protrusion Δu, 25→200 °C (nm)")
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    fig.tight_layout(); fig.savefig(fd / "s15_du_vs_Ez.png", dpi=300); plt.close(fig)
    # 2: P(contact) vs T for g0 = 5 nm
    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    g0 = 5.0
    for cv, c in zip(CVS, ("C0", "C1", "C2")):
        Ts = curves[(g0, cv)]
        ax.plot(Ts, np.arange(1, len(Ts) + 1) / len(Ts), color=c, lw=1.2, label=f"recess CV = {cv:.0%}")
    T_avg = T0 + g0 / (2 * k_hill)
    ax.axvline(T_avg, color="k", ls="--", lw=0.8)
    ax.text(T_avg, 0.05, " $T_{avg}$", fontsize=7)
    ax.axhline(0.99, color="0.5", ls=":", lw=0.8)
    ax.set_xlabel("Anneal temperature (°C)")
    ax.set_ylabel("P(contact)")
    ax.set_title(f"Total recess $g_0$ = {g0:g} nm", fontsize=8)
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout(); fig.savefig(fd / "s15_pcontact_vs_T.png", dpi=300); plt.close(fig)
    # 3: P(contact) map over (T, g0), cv = 0.1
    Tg = np.linspace(100, 450, 141)
    gg = np.linspace(1, 10, 91)
    eps = rng.normal(0.0, 0.1, ksum.size)
    sub = slice(0, 20000)
    P = np.array([[np.mean(ksum[sub] * (T - T0) >= g * (1 + eps[sub])) for T in Tg] for g in gg])
    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    cs = ax.contourf(Tg, gg, P, levels=[0, 0.01, 0.5, 0.9, 0.99, 0.999, 1.0001], cmap="Blues")
    ax.plot(T0 + gg / (2 * k_hill), gg, "k--", lw=0.8, label="$T_{avg}$ (average-Cu design)")
    cb = fig.colorbar(cs, ax=ax)
    cb.set_label("P(contact)")
    ax.set_xlabel("Anneal temperature (°C)")
    ax.set_ylabel("Total recess $g_0$ (nm)")
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    fig.tight_layout(); fig.savefig(fd / "s15_pcontact_map.png", dpi=300); plt.close(fig)


if __name__ == "__main__":
    main()
