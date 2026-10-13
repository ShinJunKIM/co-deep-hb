r"""Stage 2 group C: Ayoub 300 nm runs through the Stage 1 deck builder (stage1_pipeline.py, unchanged).

S61  pad 10 elastic, circle, SiN cap 60 nm, Ta liner 13 nm, dielectric = adopted NYCU SiO2 values   (V5)
S62  pad 3  elastic, same configuration                                                              (V5)
S63  pad 3  elastic, circle, NO cap, SLIDING, no liner, Stage-1 defaults (= R35 with sliding)        (H_sw S2)
Usage: python src\stage2\stage2_ayoub.py --case S61,S62,S63 [--E 68000 --a 0.75e-6] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "stage1"))
import stage1_pipeline as S  # noqa: E402

RUNS = {
    "S61": S._run("S61", 10, 20, "S2-C pad 10 elastic, circle, cap, Ta 13 nm, adopted SiO2", shape="circle", cap=True,
                  t_liner=0.013, layers=True),
    "S62": S._run("S62", 3, 20, "S2-C pad 3 elastic, circle, cap, Ta 13 nm, adopted SiO2", shape="circle", cap=True,
                  t_liner=0.013, layers=True),
    "S63": S._run("S63", 3, 20, "S2-C pad 3 elastic, circle, no cap, SLIDING (R35 sliding counterpart)", shape="circle",
                  cap=False, sliding=True, layers=True),
}
# round X/Y: the remaining elastic pads with the realistic stack (cap + Ta 13 nm), to test the mirror-image finding on all pads
for _p in (1, 2, 4, 5, 6, 7, 9):
    RUNS[f"SA{_p}"] = S._run(f"SA{_p}", _p, 21, f"S2-Y pad {_p} elastic, circle, cap, Ta 13 nm, adopted SiO2", shape="circle",
                             cap=True, t_liner=0.013, layers=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--E", type=float, default=None, help="SiO2 E (MPa) for S61/S62")
    ap.add_argument("--a", type=float, default=None, help="SiO2 alpha (1/K) for S61/S62")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--np", dest="nproc", type=int, default=S.DEFAULT_NP)
    a = ap.parse_args(argv)
    for rid in a.case.split(","):
        run = RUNS[rid]
        oxide0 = dict(S.OXIDE)
        if rid != "S63" and a.E is not None:
            S.OXIDE["EX"] = a.E
        if rid != "S63" and a.a is not None:
            S.OXIDE["ALPX"] = a.a
        outdir = S.RESULTS / rid
        text, meta = S._write_case(run, outdir)
        meta["oxide_used"] = dict(S.OXIDE)
        (outdir / "deck_meta.json").write_text(json.dumps(meta, indent=1, default=float))
        print(f"[{rid}] {run['note']}: {meta['n_nodes']} nodes, E_z {meta['mat']['Ez_GPa']:.2f}, oxide {S.OXIDE}")
        if not a.dry_run:
            info = S.run_batch(run, outdir, a.nproc)
            rec = S.collect(run, outdir, info)
            rec["oxide_used"] = dict(S.OXIDE)
            (outdir / "record.json").write_text(json.dumps(rec, indent=1, default=float))
            if rec.get("ok"):
                h = {r["tag"]: r for r in rec["rows"]}
                print(f"[{rid}] exit {info['exit_code']} wall {info['wall_s']:.0f} s all_conv {rec['all_converged']}; "
                      f"eps_dev_zz h030/h350/h400 = {h['LS0_cool_Tsf_to_30']['eps_dev_zz']:.4e}/{h['h350']['eps_dev_zz']:.4e}/"
                      f"{h['h400']['eps_dev_zz']:.4e}; u_center(h400) {h['h400']['u_center_nm']:.3f} nm")
            else:
                print(f"[{rid}] FAILED: {rec.get('error')}")
        S.OXIDE.update(oxide0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
