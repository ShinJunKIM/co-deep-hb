"""Connection-stage (E group) contact runs: two mirrored wafers, equal aligned circular pads, 2D axisymmetric.
Parameters (dielectric E/alpha) are the adopted imec values if results/stage2/adopted.json exists.
Registered on import by baseline.main / stage2_analysis (after stage2_runs)."""
import json
from pathlib import Path

from baseline import _run, register, RUN_BY_ID

_AD = Path(__file__).resolve().parents[2] / "results" / "stage2" / "adopted.json"
_ad = json.loads(_AD.read_text()) if _AD.exists() else {}
_P = dict(E_d=_ad.get("imec", {}).get("E_d", 95000.0), a_d=_ad.get("imec", {}).get("a_d", 3.6e-6))


def _c(rid, w, h, recess_nm, T, note, plastic=True, mu=0.3):
    return _run(rid, "E", "imec", w, h, note, kind="contact", recess=recess_nm / 1000.0, T_anneal=float(T),
                temps=[25.0, float(T), 25.0], plastic=plastic, cell_factor=12.0, mu=mu, **_P)


runs = []
k = 1
# E01-E16: 0.54 um (chosen size), h 0.6 um, per-pad recess r (gap 2r), T
for r_nm in (1.0, 2.0, 3.0, 4.0):
    for T in (250, 300, 350, 400):
        runs.append(_c(f"E{k:02d}", 0.54, 0.6, r_nm, T, f"contact 0.54 um r{r_nm:g} nm/pad T{T}")); k += 1
# E17-E24: Lhostis relative test, w 720 / 400 nm, h 650 nm, 400 C
for w in (0.72, 0.40):
    for r_nm in (2.0, 4.0, 6.0, 8.0):
        runs.append(_c(f"E{k:02d}", w, 0.65, r_nm, 400, f"contact Lhostis w{w:g} um r{r_nm:g} nm/pad T400")); k += 1
# E25-E28: 0.30 um prediction, h 0.6, r 1/2/3/4 at 350 C
for r_nm in (1.0, 2.0, 3.0, 4.0):
    runs.append(_c(f"E{k:02d}", 0.30, 0.6, r_nm, 350, f"contact 0.30 um r{r_nm:g} nm/pad T350")); k += 1
# E29: elastic reference for E06 (0.54 um, r 2, T 300) to show the plasticity effect on contact pressure
runs.append(_c("E29", 0.54, 0.6, 2.0, 300, "contact 0.54 um r2 T300 ELASTIC reference", plastic=False))
register([r for r in runs if r["id"] not in RUN_BY_ID])
