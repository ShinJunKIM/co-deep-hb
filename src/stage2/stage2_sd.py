r"""Stage 2 round SD (exploratory, post hoc): Ayoub 300 nm pads with the REALISTIC stack (SiN cap 60 nm, Ta 13 nm, adopted
SiO2 59 GPa / 1.0 ppm/K) and SLIDING sidewalls, i.e. S61/S62 with sliding=True.  Question: does a sliding sidewall reproduce
the measured heating slope sign AND magnitude for both orientations (pad 10, E_z 190; pad 3, E_z 68)?
Usage: python src\stage2\stage2_sd.py --case SD10,SD3 [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "stage1")); sys.path.insert(0, str(HERE))
import stage1_pipeline as S  # noqa: E402

REPO = HERE.parents[1]
LOG = REPO / "docs" / "stage2_exploration_log.md"
OXIDE = dict(EX=59000.0, PRXY=0.17, ALPX=1.0e-6)
MEAS = {10: dict(eps30=-1.197e-3, slope=4.660e-6), 3: dict(eps30=-1.851e-3, slope=7.300e-6)}   # Ayoub 2022 digitized
RUNS = {
    "SD10": S._run("SD10", 10, 24, "S2-SD pad 10 elastic, circle, cap, Ta 13 nm, adopted SiO2, SLIDING sidewall", shape="circle",
                   cap=True, sliding=True, t_liner=0.013, layers=True),
    "SD3": S._run("SD3", 3, 24, "S2-SD pad 3 elastic, circle, cap, Ta 13 nm, adopted SiO2, SLIDING sidewall", shape="circle",
                  cap=True, sliding=True, t_liner=0.013, layers=True),
    # cap non-load-bearing (removed) + sliding sidewall, same liner and oxide: "all Cu interfaces relaxed" scenario
    "SD10N": S._run("SD10N", 10, 24, "S2-SD pad 10 elastic, circle, NO cap, Ta 13 nm, adopted SiO2, SLIDING sidewall", shape="circle",
                    cap=False, sliding=True, t_liner=0.013, layers=True),
    "SD3N": S._run("SD3N", 3, 24, "S2-SD pad 3 elastic, circle, NO cap, Ta 13 nm, adopted SiO2, SLIDING sidewall", shape="circle",
                   cap=False, sliding=True, t_liner=0.013, layers=True),
}
TAGS = ["LS0_cool_Tsf_to_30", "h100", "h150", "h200", "h250", "h300", "h350"]


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--case", required=True); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--np", dest="nproc", type=int, default=S.DEFAULT_NP)
    a = ap.parse_args(argv)
    oxide0 = dict(S.OXIDE); S.OXIDE.update(OXIDE)
    try:
        for rid in a.case.split(","):
            run = RUNS[rid]; outdir = S.RESULTS / rid
            text, meta = S._write_case(run, outdir); meta["oxide_used"] = dict(S.OXIDE)
            (outdir / "deck_meta.json").write_text(json.dumps(meta, indent=1, default=float))
            print(f"[{rid}] {meta['n_nodes']} nodes, E_z {meta['mat']['Ez_GPa']:.1f}, n_ce {meta['n_ce']}")
            if a.dry_run:
                continue
            info = S.run_batch(run, outdir, a.nproc); rec = S.collect(run, outdir, info); rec["oxide_used"] = dict(S.OXIDE)
            (outdir / "record.json").write_text(json.dumps(rec, indent=1, default=float))
            if rec.get("ok"):
                h = {r["tag"]: r for r in rec["rows"]}
                T = np.array([h[t]["T"] for t in TAGS]); e = np.array([h[t]["eps_dev_zz"] for t in TAGS])
                k = float(np.polyfit(T, e, 1)[0]); m = MEAS[run["pad"]]
                msg = (f"**{rid}** (SD) {run['note']} -> exit {info['exit_code']}, wall {info['wall_s']:.0f} s, all_conv {rec['all_converged']}; "
                       f"eps'zz 30 C {e[0]:+.3e} (meas {m['eps30']:+.3e}, ratio {e[0] / m['eps30']:.3f}), slope 30-350 {k:+.3e} "
                       f"(meas {m['slope']:+.3e}, ratio {k / m['slope']:.3f}); s_x/s_z(30) {h['LS0_cool_Tsf_to_30']['s_x']:.0f}/{h['LS0_cool_Tsf_to_30']['s_z']:.0f} MPa; "
                       f"u_ctr(400) {h['h400']['u_center_nm']:.2f} nm")
            else:
                msg = f"**{rid}** (SD) FAILED: {rec.get('error')}"
            print(msg)
            with open(LOG, "a", encoding="utf-8") as fh:
                fh.write(f"- {_dt.datetime.now():%Y-%m-%d %H:%M} {msg}\n")
    finally:
        S.OXIDE.clear(); S.OXIDE.update(oxide0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
