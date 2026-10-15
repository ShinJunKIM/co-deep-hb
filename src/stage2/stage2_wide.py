r"""Stage 2 round SC: Ayoub 3 um WIDE pad (thesis Table 2.1, structure A) through the Stage 1 deck builder.

Purpose (docs/stage2_round_sc_wide_pad_sign.md, pre-registered): decide the eps'_zz sign-convention question with
the 3 um pad of Ayoub's thesis (p.53-57, Figs. 2.6/2.7/2.10: eps'_zz < 0 at 30 C for 3 um pads too).

NOTHING in src/stage1 or in the existing runs is modified.  The 3 um geometry is obtained by overriding, inside
this process only and inside a context manager, the module-level geometry of s1_mesh (L_CELL, A_PAD, C_PAD, one
extra LEVELS entry, the vertical element size, the O-grid blend radius) and by adding three entries to
stage1_pipeline.PADS.  Everything is restored afterwards, and the S61 deck is rebuilt through the untouched path
and its physics hash compared with results/S61/deck_meta.json (gate; also in --dry-run).

Runs (all: elastic, circle D = 3 um, pitch 6 um, SiN cap 60 nm, Ta liner 13 nm, bonded sidewalls, adopted SiO2
59 GPa / 1.0 ppm/K, T_sf = 200 C, Ayoub thermal history):
    SC1  Hill-isotropic Cu, mesh WA                     PRIMARY (verdict)
    SC2  anisotropic Cu, pad-3 orientation  (E_z  68)   orientation bracket, report only
    SC3  anisotropic Cu, pad-10 orientation (E_z 190)   orientation bracket, report only
    SC4  Hill-isotropic Cu, mesh WB (coarser)           mesh check, report only
Usage: python src\stage2\stage2_wide.py --case SC1,SC2,SC3,SC4 [--dry-run]
       python src\stage2\stage2_wide.py --analyze      -> results/stage2/ayoub_sc_wide.csv + verdict
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as _dt
import functools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "stage1"))
import s1_mesh as MESH        # noqa: E402
import stage1_pipeline as S   # noqa: E402

REPO = HERE.parents[1]
LOG = REPO / "docs" / "stage2_exploration_log.md"
OUT = REPO / "results" / "stage2"

# ---------------------------------------------------------------- 3 um geometry (thesis Table 2.1, structure A)
W_PAD = 3.0                     # um, pad width (circle diameter)
PITCH = 6.0                     # um, "pitch twice the HBM width" (thesis p.40, CPM6) = 3 um spacing (Table 2.1)
GEOM = dict(L_CELL=PITCH, A_PAD=W_PAD / 2.0, C_PAD=PITCH / 2.0)
# lateral in-pad element count / grading; the vertical in-pad element size is decoupled (H_Z) so that the
# 0.85 um pad keeps the Stage 1 L2 resolution (0.03 um at top/bottom) instead of 2*A_PAD/n_pad = 0.125 um
LEVELS_SC = {
    "WA": dict(level=dict(n_pad=24, growth=1.25, h_max_lat=0.30, h_max_z=0.22), h_z=0.030),
    "WB": dict(level=dict(n_pad=16, growth=1.25, h_max_lat=0.40, h_max_z=0.22), h_z=0.050),
}
S_OUT = 0.999 * GEOM["C_PAD"] / GEOM["A_PAD"]    # O-grid blend ends inside the cell (wall nodes stay planar)
T_SF = 200.0
T_SF_SRC = "thesis p.55 (PDF 56): linear fit 30-350 C gives SFT 150-250 C for the 3 um grains; midpoint"
OXIDE_ADOPTED = dict(EX=59000.0, PRXY=0.17, ALPX=1.0e-6)   # as S61/S62 (oxide_used)
PADS_SC = {
    30: dict(hkl=(1, 1, 1), E_table=None, T_sf=T_SF, T_sf_src=T_SF_SRC + "; Hill isotropic Cu (hkl unused)"),
    31: dict(hkl=S.PADS[3]["hkl"], E_table=68, T_sf=T_SF, T_sf_src=T_SF_SRC + "; pad-3 orientation bracket"),
    32: dict(hkl=S.PADS[10]["hkl"], E_table=198, T_sf=T_SF, T_sf_src=T_SF_SRC + "; pad-10 orientation bracket"),
}
STEP = 23
_COMMON = dict(shape="circle", cap=True, t_liner=0.013, layers=True)
RUNS = {
    "SC1": S._run("SC1", 30, STEP, "S2-SC 3 um pad, Hill Cu, bonded, cap, Ta 13 nm, adopted SiO2, mesh WA (PRIMARY)",
                  mesh="WA", el_input="HILL", **_COMMON),
    "SC2": S._run("SC2", 31, STEP, "S2-SC 3 um pad, pad-3 orientation (E_z 68), bonded, cap, Ta 13 nm, mesh WA",
                  mesh="WA", **_COMMON),
    "SC3": S._run("SC3", 32, STEP, "S2-SC 3 um pad, pad-10 orientation (E_z 190), bonded, cap, Ta 13 nm, mesh WA",
                  mesh="WA", **_COMMON),
    "SC4": S._run("SC4", 30, STEP, "S2-SC 3 um pad, Hill Cu, mesh WB (coarser; mesh check)",
                  mesh="WB", el_input="HILL", **_COMMON),
}
S61_HASH = json.loads((REPO / "results" / "S61" / "deck_meta.json").read_text())["physics_sha256"]


@contextlib.contextmanager
def wide_geometry(mesh_key):
    """Temporarily switch s1_mesh / stage1_pipeline to the 3 um cell; restore everything on exit."""
    saved = dict(L_CELL=MESH.L_CELL, A_PAD=MESH.A_PAD, C_PAD=MESH.C_PAD,
                 vertical_axis=MESH.vertical_axis, ogrid=MESH._ogrid_map, oxide=dict(S.OXIDE))
    lv = LEVELS_SC[mesh_key]
    orig_vert, orig_ogrid = MESH.vertical_axis, MESH._ogrid_map
    n_pad_z = int(round(2.0 * GEOM["A_PAD"] / lv["h_z"]))      # vertical_axis uses h_p = 2*A_PAD/n_pad

    def vertical_axis(n_pad, growth, h_max, cap=True, t_si=MESH.T_SI, t_liner=0.0):
        return orig_vert(n_pad_z, growth, h_max, cap, t_si, t_liner)

    try:
        MESH.L_CELL, MESH.A_PAD, MESH.C_PAD = GEOM["L_CELL"], GEOM["A_PAD"], GEOM["C_PAD"]
        MESH.LEVELS[mesh_key] = lv["level"]
        MESH.vertical_axis = vertical_axis
        MESH._ogrid_map = functools.partial(orig_ogrid, s_out=S_OUT)
        for k, v in PADS_SC.items():
            assert k not in S.PADS
            S.PADS[k] = v
        S.OXIDE.update(OXIDE_ADOPTED)
        yield
    finally:
        MESH.L_CELL, MESH.A_PAD, MESH.C_PAD = saved["L_CELL"], saved["A_PAD"], saved["C_PAD"]
        MESH.LEVELS.pop(mesh_key, None)
        MESH.vertical_axis, MESH._ogrid_map = saved["vertical_axis"], saved["ogrid"]
        for k in PADS_SC:
            S.PADS.pop(k, None)
        S.OXIDE.clear(); S.OXIDE.update(saved["oxide"])


def gate_untouched_path():
    """Rebuild S61 through the unmodified builder and compare its physics hash with the stored deck."""
    sys.path.insert(0, str(HERE))
    import stage2_ayoub  # noqa: E402  (its RUNS["S61"] is the original definition)
    oxide0 = dict(S.OXIDE)
    try:
        S.OXIDE.update(OXIDE_ADOPTED)
        _, meta = S.build_deck(stage2_ayoub.RUNS["S61"])
    finally:
        S.OXIDE.clear(); S.OXIDE.update(oxide0)
    ok = meta["physics_sha256"] == S61_HASH
    print(f"[gate] S61 rebuilt through the untouched path: hash {'MATCH' if ok else 'MISMATCH'} "
          f"({meta['physics_sha256'][:12]} vs {S61_HASH[:12]}), {meta['n_nodes']} nodes")
    if not ok:
        raise SystemExit("gate failed: the untouched build path no longer reproduces S61")


def log_line(text):
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(f"- {_dt.datetime.now():%Y-%m-%d %H:%M} {text}\n")


def build(rid):
    run = RUNS[rid]
    outdir = S.RESULTS / rid
    with wide_geometry(run["mesh"]):
        text, meta = S._write_case(run, outdir)
        m = MESH.build_mesh(run["mesh"], run["shape"], run["cap"], run["sliding"], run["t_si"], run["t_liner"])
        meta["oxide_used"] = dict(S.OXIDE)
        meta["geometry_sc"] = dict(w_pad_um=W_PAD, pitch_um=PITCH, mesh=LEVELS_SC[run["mesh"]], s_out=S_OUT,
                                   n_cu_elems=int(len(m.elems[MESH.MAT_CU])),
                                   x_wall_planar=bool(np.allclose(m.nodes[np.isclose(m.nodes[:, 1], 0.0), 1], 0.0)),
                                   max_corner_angle_deg=float(MESH.element_quality(m)))
        (outdir / "deck_meta.json").write_text(json.dumps(meta, indent=1, default=float))
    return run, outdir, meta


def slope(rows, tags):
    h = {r["tag"]: r for r in rows}
    T = np.array([h[t]["T"] for t in tags]); e = np.array([h[t]["eps_dev_zz"] for t in tags])
    return float(np.polyfit(T, e, 1)[0])


TAGS_350 = ["LS0_cool_Tsf_to_30", "h100", "h150", "h200", "h250", "h300", "h350"]
TAGS_200 = ["LS0_cool_Tsf_to_30", "h100", "h150", "h200"]


def summarize(rid):
    f = S.RESULTS / rid / "record.json"
    if not f.exists():
        return None
    rec = json.loads(f.read_text())
    if not rec.get("ok"):
        return dict(id=rid, ok=False, error=rec.get("error"))
    h = {r["tag"]: r for r in rec["rows"]}
    r30 = h["LS0_cool_Tsf_to_30"]
    return dict(id=rid, ok=True, all_conv=rec["all_converged"], n_nodes=rec["n_nodes"],
                eps30=r30["eps_dev_zz"], eps350=h["h350"]["eps_dev_zz"], eps400=h["h400"]["eps_dev_zz"],
                slope350=slope(rec["rows"], TAGS_350), slope200=slope(rec["rows"], TAGS_200),
                s_x30=r30["s_x"], s_y30=r30["s_y"], s_z30=r30["s_z"],
                sz_top30=r30.get("sz_cu_top_layer"), sz_mid30=r30.get("sz_cu_mid_layer"),
                bands30=[r30.get(f"epsdev_band{q}") for q in range(1, 6)],
                u_ctr400=h["h400"]["u_center_nm"], wall_s=rec["exec"]["wall_s"], exit=rec["exec"]["exit_code"])


# measured values for the magnitude comparison (report only), Ayoub thesis
MEAS = dict(
    fig26_eps30_range=(-0.9e-3, -0.35e-3),      # Fig. 2.6, 3 um grains, 30 C before annealing (read from figure)
    fig210_eps30_range=(-2.0e-3, -0.5e-3),      # Fig. 2.10a, 3 um, 30 C after annealing, bonded and non-bonded (text p.57)
    fig27_slope_350=(2.3e-6, 4.4e-6),           # Fig. 2.7 a/b, 3 um heating 30-350 C, [001]-like / [111]-like grain (read)
    fig27_eps30=(-0.9e-3, -0.4e-3),             # Fig. 2.7 a/b, 3 um heating start
)


def analyze():
    rows = {rid: summarize(rid) for rid in RUNS}
    lines = [f"# Round SC ({_dt.date.today()}): Ayoub 3 um wide pad (thesis Table 2.1 A, pitch 6 um), bonded, cap 60 nm, "
             f"Ta 13 nm, SiO2 59 GPa/1.0 ppm, T_sf {T_SF:g} C. Convention: eps'_zz = EPEL_zz - tr/3, Cu volume average, "
             f"global frame. Measured: thesis Fig. 2.6 (30 C, before anneal) {MEAS['fig26_eps30_range']}, Fig. 2.10a "
             f"(30 C, after anneal) {MEAS['fig210_eps30_range']}, Fig. 2.7 heating slope 30-350 C {MEAS['fig27_slope_350']} 1/K.",
             "run,role,n_nodes,all_conv,eps30,eps30_Tsf150,eps30_Tsf250,eps350,slope_30_350,slope_30_200,"
             "s_x30_MPa,s_z30_MPa,sz_top30_MPa,sz_mid30_MPa,band1_bottom..band5_top(30C),u_ctr400_nm,sign30"]
    roles = dict(SC1="PRIMARY Hill WA", SC2="orientation pad-3 (E_z 68)", SC3="orientation pad-10 (E_z 190)",
                 SC4="mesh check Hill WB")
    for rid, r in rows.items():
        if r is None:
            lines.append(f"{rid},{roles[rid]},,MISSING"); continue
        if not r["ok"]:
            lines.append(f"{rid},{roles[rid]},,FAILED {r['error']}"); continue
        sc = lambda T: r["eps30"] * (T - 30.0) / (T_SF - 30.0)   # elastic: eps'(30) is linear in (T_sf - 30)
        bands = "/".join(f"{b:+.3e}" for b in r["bands30"])
        lines.append(f"{rid},{roles[rid]},{r['n_nodes']},{r['all_conv']},{r['eps30']:+.4e},{sc(150):+.4e},{sc(250):+.4e},"
                     f"{r['eps350']:+.4e},{r['slope350']:+.3e},{r['slope200']:+.3e},{r['s_x30']:.0f},{r['s_z30']:.0f},"
                     f"{r['sz_top30']:.0f},{r['sz_mid30']:.0f},{bands},{r['u_ctr400']:.3f},"
                     f"{'positive' if r['eps30'] > 0 else 'negative'}")
    # ---- pre-registered decision (docs/stage2_round_sc_wide_pad_sign.md section 3)
    p = rows.get("SC1")
    verdict = "UNDETERMINED"
    why = []
    if p and p["ok"]:
        signs = {rid: np.sign(r["eps30"]) for rid, r in rows.items() if r and r["ok"]}
        robust = all(s == signs["SC1"] for s in signs.values()) and len(signs) == len(RUNS)
        big = abs(p["eps30"]) >= 0.1e-3
        if not p["all_conv"]:
            why.append("SC1 not converged")
        elif not big:
            why.append(f"|eps'zz(30)| = {abs(p['eps30']):.2e} < 1e-4 (below the measurement uncertainty)")
        elif not robust:
            why.append(f"sign not robust across runs: {signs}")
        else:
            verdict = ("SIGN-CONVENTION REVERSAL SUPPORTED (3 um positive: both sizes opposite to Ayoub)" if p["eps30"] > 0
                       else "SIGN-CONVENTION REVERSAL REJECTED (3 um negative = Ayoub; only 300 nm is opposite)")
        if big:
            lo, hi = MEAS["fig26_eps30_range"]
            why.append(f"magnitude (report only): model {p['eps30']:+.3e} at T_sf 200 C "
                       f"[{p['eps30'] * 120 / 170:+.3e} .. {p['eps30'] * 220 / 170:+.3e} for T_sf 150..250 C] "
                       f"vs Fig. 2.6 {lo:+.1e}..{hi:+.1e} (before anneal), Fig. 2.10a -2e-3..-5e-4 (after anneal); "
                       f"slope 30-350 C model {p['slope350']:+.3e} vs Fig. 2.7 +2.3e-6..+4.4e-6 1/K")
    lines.append(f"# VERDICT: {verdict}" + ("; " + "; ".join(why) if why else ""))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ayoub_sc_wide.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return verdict


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--np", dest="nproc", type=int, default=S.DEFAULT_NP)
    a = ap.parse_args(argv)
    if a.analyze:
        analyze(); return 0
    gate_untouched_path()
    for rid in a.case.split(","):
        run, outdir, meta = build(rid)
        g = meta["geometry_sc"]
        print(f"[{rid}] {run['note']}: {meta['n_nodes']} nodes / {meta['n_elems']} elems (Cu {g['n_cu_elems']}), "
              f"T_sf {meta['T_sf']:g}, Cu {'Hill E/nu ' + str(tuple(round(v, 4) for v in meta['mat']['hill_E_nu'])) if 'hill_E_nu' in meta['mat'] else 'E_z %.1f GPa' % meta['mat']['Ez_GPa']}, "
              f"oxide {meta['oxide_used']}, wall planar {g['x_wall_planar']}, worst corner angle {g['max_corner_angle_deg']:.1f} deg, "
              f"hash {meta['physics_sha256'][:12]}")
        if a.dry_run:
            continue
        info = S.run_batch(run, outdir, a.nproc)
        rec = S.collect(run, outdir, info)
        rec["oxide_used"] = dict(OXIDE_ADOPTED)
        (outdir / "record.json").write_text(json.dumps(rec, indent=1, default=float))
        if rec.get("ok"):
            h = {r["tag"]: r for r in rec["rows"]}
            e30, e350 = h["LS0_cool_Tsf_to_30"]["eps_dev_zz"], h["h350"]["eps_dev_zz"]
            msg = (f"**{rid}** (SC) {run['note']} -> exit {info['exit_code']}, wall {info['wall_s']:.0f} s, all_conv "
                   f"{rec['all_converged']}; eps'zz 30 C {e30:+.3e}, 350 C {e350:+.3e}, slope(30-350) "
                   f"{slope(rec['rows'], TAGS_350):+.3e}; s_x/s_z(30) {h['LS0_cool_Tsf_to_30']['s_x']:.0f}/"
                   f"{h['LS0_cool_Tsf_to_30']['s_z']:.0f} MPa; u_ctr(400) {h['h400']['u_center_nm']:.2f} nm")
        else:
            msg = f"**{rid}** (SC) {run['note']} -> FAILED: {rec.get('error')}"
        print(msg); log_line(msg)
    # the gate again after the overrides have been restored
    gate_untouched_path()
    return 0


if __name__ == "__main__":
    sys.exit(main())
