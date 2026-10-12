"""Stage 2 run registry (imported by baseline.py). Groups: SV verification, A calibration, B validation,
D plasticity, E connection-stage contact. Ayoub 300 nm runs (group C) are built by stage2_ayoub.py."""
from baseline import _run, register, DATASETS

E_SIO2 = (59000.0, 68000.0, 77000.0)
A_SIO2 = (0.5e-6, 1.0e-6)
TAPER = (7.6, 12.8, 18.0)
E_SICN = (70000.0, 95000.0, 120000.0)
A_SICN = (2.0e-6, 5.2e-6)
MID_SIO2 = dict(E_d=68000.0, a_d=0.75e-6)
MID_SICN = dict(E_d=95000.0, a_d=3.6e-6)

runs = []
# ---- SV: verification (solution verification, 2D-3D consistency); mid-range parameters, not used for calibration
runs += [
    _run("SV01", "SV", "imec", 0.54, 0.6, "imec 0.54 2D Hill, cell 3w, refine 1 (verification base)", **MID_SICN),
    _run("SV02", "SV", "imec", 0.54, 0.6, "imec 0.54 2D Hill, refine 2 (mesh check)", refine=2, **MID_SICN),
    _run("SV03", "SV", "imec", 0.54, 0.6, "imec 0.54 2D Hill, cell 6w (cell check)", cell_factor=6.0, **MID_SICN),
    _run("SV04", "SV", "imec", 0.54, 0.6, "imec 0.54 3D iso Hill, cell 3w (3D-vs-2D check)", dim=3, **MID_SICN),
    _run("SV05", "SV", "imec", 3.06, 0.6, "imec 3.06 2D Hill (film-limit analytic check)", **MID_SICN),
    _run("SV06", "SV", "nycu", 1.0, 1.5, "NYCU 1 um 2D Hill, taper 7.6, Ta 50 (liner implementation check vs R42)", taper=7.6,
         **MID_SIO2),
    _run("SV07", "SV", "nycu", 1.0, 1.5, "NYCU 1 um 2D Hill, taper 7.6, NO liner (= R42 physics with E 68/a 0.75)",
         taper=7.6, t_liner=0.0, **MID_SIO2),
    _run("SV08", "SV", "imec", 0.54, 0.6, "imec 0.54 2D Hill, cell 9w (cell check)", cell_factor=9.0, **MID_SICN),
    _run("SV09", "SV", "imec", 0.54, 0.6, "imec 0.54 2D Hill, cell 12w (cell check)", cell_factor=12.0, **MID_SICN),
    _run("SV10", "SV", "imec", 0.54, 0.6, "imec 0.54 2D Hill, cell 20w (cell check)", cell_factor=20.0, **MID_SICN),
    _run("SV11", "SV", "imec", 3.06, 0.6, "imec 3.06 2D Hill, cell 6w (cell check large pad)", cell_factor=6.0, **MID_SICN),
    _run("SV12", "SV", "imec", 0.54, 0.6, "imec 0.54 3D iso Hill, cell 9w coarse far field (3D cell check)", dim=3, cell_factor=9.0, grow3d=1.4, hmax3d=0.6, **MID_SICN),
    _run("SV13", "SV", "imec", 0.54, 0.6, "imec 0.54 3D iso Hill, cell 12w coarse far field (3D cell check)", dim=3, cell_factor=12.0, grow3d=1.5, hmax3d=1.0, **MID_SICN),
]
# ---- A: calibration grids (per process)
k = 1
for w, h in ((9.0, 1.15), (3.0, 1.5)):
    for E in E_SIO2:
        for a in A_SIO2:
            for tp in TAPER:
                runs.append(_run(f"S{k:02d}", "A", "nycu", w, h, f"NYCU {w:g} um calib E{E/1000:g} a{a*1e6:g} taper{tp:g}",
                                 taper=tp, E_d=E, a_d=a))
                k += 1
for w in (3.06, 1.80):
    for E in E_SICN:
        for a in A_SICN:
            runs.append(_run(f"S{k:02d}", "A", "imec", w, 0.6, f"imec {w:g} um calib E{E/1000:g} a{a*1e6:g}", E_d=E, a_d=a))
            k += 1
assert k == 49
# S49, S50 sensitivity (filled with adopted parameters by stage2_analysis before running)
runs += [
    _run("S49", "A2", "nycu", 9.0, 0.8, "NYCU 9 um thickness 0.8 um (Table-1 volume alternative), adopted params", **MID_SIO2),
    _run("S50", "A2", "nycu", 3.0, 1.5, "NYCU 3 um Cu alpha +7 % (30-400 C mean), adopted params", cu_alpha=17.6e-6, **MID_SIO2),
]
# ---- B: held-out validation (parameters filled from the adopted calibration before running)
runs += [
    _run("S51", "B", "imec", 1.26, 0.6, "V1 imec 1.26 2D Hill bonded", **MID_SICN),
    _run("S52", "B", "imec", 0.54, 0.6, "V2 imec 0.54 2D Hill bonded", **MID_SICN),
    _run("S53", "B", "imec", 0.54, 0.6, "V2 imec 0.54 3D [001] bonded cell 6w", cu="aniso", orient="001", cell_factor=6.0, **MID_SICN),
    _run("S54", "B", "imec", 0.54, 0.6, "V2 imec 0.54 3D [101] bonded cell 6w", cu="aniso", orient="101", cell_factor=6.0, **MID_SICN),
    _run("S55", "B", "imec", 0.54, 0.6, "V2 imec 0.54 3D [111] bonded cell 6w", cu="aniso", orient="111", cell_factor=6.0, **MID_SICN),
    _run("S56", "B", "nycu", 1.0, 1.5, "V3 NYCU 1 um 3D [001] bonded cell 6w", cu="aniso", orient="001", cell_factor=6.0, **MID_SIO2),
    _run("S57", "B", "nycu", 1.0, 1.5, "V3 NYCU 1 um 3D [101] bonded cell 6w", cu="aniso", orient="101", cell_factor=6.0, **MID_SIO2),
    _run("S58", "B", "nycu", 1.0, 1.5, "V3 NYCU 1 um 3D [111] bonded cell 6w", cu="aniso", orient="111", cell_factor=6.0, **MID_SIO2),
    _run("S59", "B", "imec", 0.54, 0.6, "V4 imec 0.54 2D Hill SLIDING control", side="sliding", **MID_SICN),
    _run("S60", "B", "nycu", 1.0, 1.5, "V4 NYCU 1 um 3D [001] SLIDING control cell 6w", cu="aniso", orient="001",
         side="sliding", cell_factor=6.0, **MID_SIO2),
    # B-alt: V3 with the volume-consistent 1 um taper (7.6 deg, Lin Table 1) - documented alternative, not the committed rule
    _run("S56b", "Balt", "nycu", 1.0, 1.5, "V3-alt NYCU 1 um 3D [001] bonded, taper 7.6 (volume-consistent)", cu="aniso", orient="001", **MID_SIO2),
    _run("S57b", "Balt", "nycu", 1.0, 1.5, "V3-alt NYCU 1 um 3D [101] bonded, taper 7.6", cu="aniso", orient="101", **MID_SIO2),
    _run("S58b", "Balt", "nycu", 1.0, 1.5, "V3-alt NYCU 1 um 3D [111] bonded, taper 7.6", cu="aniso", orient="111", **MID_SIO2),
]
# ---- D: isotropic 2D plasticity (Okoro), adopted parameters
runs += [
    _run("S64", "D", "nycu", 1.0, 1.5, "D NYCU 1 um 2D Hill PLASTIC (Okoro)", plastic=True, **MID_SIO2),
    _run("S65", "D", "imec", 0.54, 0.6, "D imec 0.54 2D Hill PLASTIC (Okoro)", plastic=True, **MID_SICN),
    _run("S66", "D", "imec", 3.06, 0.6, "D imec 3.06 2D Hill PLASTIC (Okoro)", plastic=True, **MID_SICN),
]
CELL2D = 12.0
for _r in runs:
    if _r["group"] in ("A", "A2", "B", "Balt", "D"):
        if _r["dim"] == 2:
            _r["cell_factor"] = CELL2D
        else:
            _r["cell_factor"] = 12.0; _r["grow3d"] = 1.5; _r["hmax3d"] = 1.0
        _r["note"] += " cell12w"
register(runs)

# ---- E: connection-stage contact runs are registered by stage2_contact_runs (parameters fixed after calibration)

# ---- adopted calibration parameters (written by stage2_analysis --calibrate) override the MID placeholders
import json as _json
from pathlib import Path as _Path
_AD = _Path(__file__).resolve().parents[2] / "results" / "stage2" / "adopted.json"
if _AD.exists():
    _ad = _json.loads(_AD.read_text())
    for _r in runs:
        if _r["group"] in ("A2", "B", "Balt", "D") and _r["ds"] in _ad:
            _p = _ad[_r["ds"]]
            _r["E_d"], _r["a_d"] = _p["E_d"], _p["a_d"]
            if _r["ds"] == "nycu" and _r["group"] != "Balt":
                _r["taper"] = _p["taper"]
            elif _r["ds"] == "nycu":
                _r["taper"] = 7.6
            _r["note"] += " [adopted params]"

# ---- P: prediction runs (imec process, adopted params): 0.30 um and extra 0.54 um orientations for the Monte Carlo fit
_AY = {"ay3": (1.0, 0.1, 0.02), "ay6": (1.0, 0.24, 0.47), "ay1": (1.0, 0.6, 0.37), "ay4": (1.0, 0.9, 0.6), "ay5": (1.0, 0.89, 0.87)}
_P3 = dict(cell_factor=2.0)                      # revision 1: array pitch 2 w (3D square cell); 2D runs use 2.26 w
runs_P = [
    _run("S67", "P", "imec", 0.30, 0.6, "P imec 0.30 um 2D Hill bonded cell2.26w", cell_factor=2.26, **MID_SICN),
    _run("S68", "P", "imec", 0.30, 0.6, "P imec 0.30 um 3D [001] bonded", cu="aniso", orient="001", **_P3, **MID_SICN),
    _run("S69", "P", "imec", 0.30, 0.6, "P imec 0.30 um 3D [101] bonded", cu="aniso", orient="101", **_P3, **MID_SICN),
    _run("S70", "P", "imec", 0.30, 0.6, "P imec 0.30 um 3D [111] bonded", cu="aniso", orient="111", **_P3, **MID_SICN),
    _run("S71", "P", "imec", 0.30, 0.6, "P imec 0.30 um 2D Hill SLIDING (relaxed-sidewall bound) cell2.26w", side="sliding", cell_factor=2.26, **MID_SICN),
    _run("S79", "P", "imec", 0.54, 0.6, "P imec 0.54 um 2D Hill SLIDING cell2.26w (= S116, alias not run)", side="sliding", cell_factor=2.26, **MID_SICN),
    _run("S72", "P", "imec", 0.54, 0.6, "P imec 0.54 um 3D [ay3] bonded", cu="aniso", orient="ay3", **_P3, **MID_SICN),
    _run("S73", "P", "imec", 0.54, 0.6, "P imec 0.54 um 3D [ay6] bonded", cu="aniso", orient="ay6", **_P3, **MID_SICN),
    _run("S74", "P", "imec", 0.54, 0.6, "P imec 0.54 um 3D [ay1] bonded", cu="aniso", orient="ay1", **_P3, **MID_SICN),
    _run("S75", "P", "imec", 0.54, 0.6, "P imec 0.54 um 3D [ay4] bonded", cu="aniso", orient="ay4", **_P3, **MID_SICN),
    _run("S76", "P", "imec", 0.54, 0.6, "P imec 0.54 um 3D [ay5] bonded", cu="aniso", orient="ay5", **_P3, **MID_SICN),
    _run("S77", "P", "imec", 0.30, 0.6, "P imec 0.30 um 3D [ay6] bonded", cu="aniso", orient="ay6", **_P3, **MID_SICN),
    _run("S78", "P", "imec", 0.30, 0.6, "P imec 0.30 um 3D [ay4] bonded", cu="aniso", orient="ay4", **_P3, **MID_SICN),
]
if _AD.exists():
    for _r in runs_P:
        _r["E_d"], _r["a_d"] = _ad["imec"]["E_d"], _ad["imec"]["a_d"]; _r["note"] += " [adopted params]"
register(runs_P)

# ---- Revision 1 (decision 4, exploration log): array pitch instead of isolated pad for array-measured data
CELL_IMEC_2D, CELL_IMEC_3D, CELL_NYCU3 = 2.26, 2.0, 2.5     # equal-area cells for pitch 2 w (imec) and 2.2 w (Lin 3 um array)
_IM = dict(cell_factor=CELL_IMEC_2D)
runs_R = []
k = 81
for w in (3.06, 1.80):
    for E in E_SICN:
        for a in A_SICN:
            runs_R.append(_run(f"S{k}", "Ar", "imec", w, 0.6, f"REV1 imec {w:g} um calib E{E/1000:g} a{a*1e6:g} cell2.26w", E_d=E, a_d=a, **_IM)); k += 1
for E in E_SIO2:
    for a in A_SIO2:
        for tp in TAPER:
            runs_R.append(_run(f"S{k}", "Ar", "nycu", 3.0, 1.5, f"REV1 NYCU 3 um calib E{E/1000:g} a{a*1e6:g} taper{tp:g} cell2.5w",
                               taper=tp, E_d=E, a_d=a, cell_factor=CELL_NYCU3)); k += 1
assert k == 111
runs_R += [
    _run("S111", "Br", "imec", 1.26, 0.6, "REV1 V1 imec 1.26 2D Hill bonded cell2.26w", **_IM, **MID_SICN),
    _run("S112", "Br", "imec", 0.54, 0.6, "REV1 V2 imec 0.54 2D Hill bonded cell2.26w", **_IM, **MID_SICN),
    _run("S113", "Br", "imec", 0.54, 0.6, "REV1 V2 imec 0.54 3D [001] bonded cell2.0w", cu="aniso", orient="001", cell_factor=CELL_IMEC_3D, **MID_SICN),
    _run("S114", "Br", "imec", 0.54, 0.6, "REV1 V2 imec 0.54 3D [101] bonded cell2.0w", cu="aniso", orient="101", cell_factor=CELL_IMEC_3D, **MID_SICN),
    _run("S115", "Br", "imec", 0.54, 0.6, "REV1 V2 imec 0.54 3D [111] bonded cell2.0w", cu="aniso", orient="111", cell_factor=CELL_IMEC_3D, **MID_SICN),
    _run("S116", "Br", "imec", 0.54, 0.6, "REV1 V4 imec 0.54 2D Hill SLIDING cell2.26w", side="sliding", **_IM, **MID_SICN),
    _run("S117", "Br", "imec", 0.54, 0.6, "REV1 pitch sensitivity 1.7w (2D cell 1.92w)", cell_factor=1.92, **MID_SICN),
    _run("S118", "Br", "imec", 0.54, 0.6, "REV1 pitch sensitivity 3w (2D cell 3.39w)", cell_factor=3.39, **MID_SICN),
]
_ADR = _AD.parent / "adopted_rev.json"
if _ADR.exists():
    _adr = _json.loads(_ADR.read_text())
    for _r in runs_R + runs_P:
        if _r["group"] in ("Br", "P") and _r["ds"] in _adr:
            _r["E_d"], _r["a_d"] = _adr[_r["ds"]]["E_d"], _adr[_r["ds"]]["a_d"]; _r["note"] += " [adopted_rev]"
register(runs_R)
