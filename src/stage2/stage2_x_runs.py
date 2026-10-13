"""Group X (post-hoc exploration, NOT validation): numerical-setting robustness of the contact model (X1),
physical hypotheses for the 0.54 um over-prediction (X2), yield size effect in the contact stage (X3)."""
import json
from pathlib import Path
from baseline import _run, register, RUN_BY_ID

_ADR = Path(__file__).resolve().parents[2] / "results" / "stage2" / "adopted_rev.json"
_ad = json.loads(_ADR.read_text())["imec"]
IM = dict(E_d=_ad["E_d"], a_d=_ad["a_d"])


def c(rid, note, w=0.54, h=0.6, r_nm=2.0, T=300, **kw):
    d = dict(kind="contact", recess=r_nm / 1000.0, T_anneal=float(T), temps=[25.0, float(T), 25.0], plastic=True,
             cell_factor=2.26, mu=0.3)
    d.update(kw)
    return _run(rid, "X", "imec", w, h, note, **IM, **d)


runs = [
    # X1 numerical robustness, baseline = E06 (0.54 um, r 2 nm, 300 C)
    c("X01", "X1 contact refine x2 (80 el/radius)", refine=2),
    c("X02", "X1 contact penalty method (KEYOPT(2)=1)", keyopt2=1),
    c("X03", "X1 contact FKN 0.1", fkn=0.1),
    c("X04", "X1 contact FKN 10", fkn=10.0),
    c("X05", "X1 contact friction 0.1", mu=0.1),
    c("X06", "X1 contact friction 0.5", mu=0.5),
    c("X07", "X1 PLANE182 full integration (KEYOPT(1)=0)", keyopt1=0),
    c("X08", "X1 substeps 40 min", nsub=40),
    # X3 yield size effect in the contact stage
    c("X09", "X3 yield x2 (sub-um size effect)", yield_scale=2.0),
    c("X10", "X3 yield x3", yield_scale=3.0),
    c("X11", "X3 yield x3, r 4 nm, 350 C", r_nm=4.0, T=350, yield_scale=3.0),
    # X2 physical hypotheses for the 0.54 um over-prediction (array cell 2.26 w = pitch 1.08 um kept absolute)
    _run("X12", "X", "imec", 0.50, 0.6, "X2 effective CD 0.50 um, pitch 1.08 um", cell_factor=2.26 * 0.54 / 0.50, **IM),
    _run("X13", "X", "imec", 0.46, 0.6, "X2 effective CD 0.46 um, pitch 1.08 um", cell_factor=2.26 * 0.54 / 0.46, **IM),
    _run("X14", "X", "imec", 0.54, 0.5, "X2 pad depth 0.5 um", cell_factor=2.26, **IM),
    _run("X15", "X", "imec", 0.54, 0.6, "X2 dielectric = SiO2 bulk (72 GPa, 0.5 ppm) instead of SiCN", cell_factor=2.26,
         diel="SiO2", E_d=72000.0, a_d=0.5e-6),
    _run("X16", "X", "imec", 0.54, 0.6, "X2 compliant liner (Ta E/10 = 18.6 GPa, weak-interface proxy)", cell_factor=2.26,
         E_liner=18600.0, **IM),
    _run("X17", "X", "imec", 0.54, 0.6, "X2 T-dependent Cu stiffness (Chang & Himmel Hill E(T))", cell_factor=2.26, cu_T=True, **IM),
    _run("X18", "X", "imec", 0.54, 0.6, "X2 taper 5 deg (TEM-like, wider top)", cell_factor=2.26, taper=5.0, **IM),
    _run("X19", "X", "imec", 1.80, 0.6, "X2 control: 1.80 um with T-dependent Cu stiffness", cell_factor=2.26, cu_T=True, **IM),
    _run("X20", "X", "imec", 1.80, 0.6, "X2 control: 1.80 um dielectric = SiO2 bulk", cell_factor=2.26, diel="SiO2", E_d=72000.0, a_d=0.5e-6),
]

# X21: worst-plausible combination for the 0.54 um pad (one run): CD 0.46 um, depth 0.5 um, taper 5 deg, pitch 1.7 w (0.918 um)
_pitch = 1.7 * 0.54
runs.append(_run("X21", "X", "imec", 0.46, 0.5, "X2 worst-plausible combo: CD 0.46, depth 0.5, taper 5, pitch 0.918 um",
                 cell_factor=1.128 * _pitch / 0.46, taper=5.0, **IM))
register([r for r in runs if r["id"] not in RUN_BY_ID])

# Z: one consistent setup for all four imec sizes: array cell 2.26 w, adopted SiCN, isotropic plasticity (Okoro x1 and x3)
for _w, _k in ((3.06, 22), (1.80, 23), (1.26, 24), (0.54, 25)):
    runs.append(_run(f"X{_k}", "Z", "imec", _w, 0.6, f"Z imec {_w:g} um array cell PLASTIC Okoro x1", cell_factor=2.26, plastic=True, **IM))
for _w, _k in ((3.06, 26), (1.26, 27), (0.54, 28)):
    runs.append(_run(f"X{_k}", "Z", "imec", _w, 0.6, f"Z imec {_w:g} um array cell PLASTIC Okoro x3", cell_factor=2.26, plastic=True,
                     yield_scale=3.0, **IM))
register([r for r in runs if r["id"] not in RUN_BY_ID])

runs.append(_run("X29", "Z", "imec", 1.80, 0.6, "Z imec 1.8 um array cell PLASTIC Okoro x3", cell_factor=2.26, plastic=True, yield_scale=3.0, **IM))
register([r for r in runs if r["id"] not in RUN_BY_ID])

# W: in-plane stress-relaxation proxy (grain-boundary / interface diffusional creep during the hold).
# Cu in-plane CTE is set between the full Cu value (16.5 ppm, no relaxation) and the dielectric value (no in-plane
# mismatch stress, full relaxation). Vertical CTE unchanged. Tests whether a size-dependent relaxation can
# reproduce the measured size dependence (small pads relax faster: diffusion length ~ pad size).
A_CU, A_D = 16.5e-6, 2.0e-6
runs_W = []
for i, (w, frac) in enumerate([(0.54, 1.0), (0.54, 0.5), (0.54, 0.25), (1.26, 1.0), (1.26, 0.5),
                               (1.80, 1.0), (1.80, 0.5), (3.06, 1.0), (3.06, 0.5)]):
    aip = A_CU - frac * (A_CU - A_D)
    runs_W.append(_run(f"W{i + 1:02d}", "W", "imec", w, 0.6,
                       f"W in-plane relaxation {frac:.0%} ({w:g} um), alpha_ip {aip * 1e6:.2f} ppm",
                       cell_factor=2.26, cu_alpha_ip=aip, **IM))
register([r for r in runs_W if r["id"] not in RUN_BY_ID])

# W10+: combination of the two size-opposed mechanisms (plasticity raises u on large pads, in-plane relaxation lowers it
# on small pads), and the 200 C check for the small pad.
runs_W2 = [
    _run("W10", "W", "imec", 0.54, 0.6, "W 0.54 um full in-plane relaxation + plastic Okoro x3", cell_factor=2.26,
         cu_alpha_ip=2.0e-6, plastic=True, yield_scale=3.0, **IM),
    _run("W11", "W", "imec", 1.26, 0.6, "W 1.26 um 25% in-plane relaxation + plastic Okoro x3", cell_factor=2.26,
         cu_alpha_ip=16.5e-6 - 0.25 * 14.5e-6, plastic=True, yield_scale=3.0, **IM),
    _run("W12", "W", "imec", 0.30, 0.6, "W 0.30 um full in-plane relaxation (prediction)", cell_factor=2.26,
         cu_alpha_ip=2.0e-6, **IM),
    _run("W13", "W", "imec", 0.54, 0.6, "W 0.54 um full in-plane relaxation, 3D [001]", cu="aniso", orient="001",
         cell_factor=2.0, cu_alpha_ip=2.0e-6, **IM),
]
register([r for r in runs_W2 if r["id"] not in RUN_BY_ID])

# W14+: does in-plane relaxation remove the orientation dependence? (orientation enters only through the elastic
# response to in-plane constraint stress; Cu CTE is isotropic in a cubic crystal)
runs_W3 = [
    _run("W14", "W", "imec", 0.54, 0.6, "W 0.54 um full relaxation, 3D [101]", cu="aniso", orient="101",
         cell_factor=2.0, cu_alpha_ip=2.0e-6, **IM),
    _run("W15", "W", "imec", 0.54, 0.6, "W 0.54 um full relaxation, 3D [111]", cu="aniso", orient="111",
         cell_factor=2.0, cu_alpha_ip=2.0e-6, **IM),
    _run("W16", "W", "imec", 0.30, 0.6, "W 0.30 um full relaxation, 3D [001]", cu="aniso", orient="001",
         cell_factor=2.0, cu_alpha_ip=2.0e-6, **IM),
    _run("W17", "W", "imec", 0.30, 0.6, "W 0.30 um full relaxation, 3D [111]", cu="aniso", orient="111",
         cell_factor=2.0, cu_alpha_ip=2.0e-6, **IM),
]
register([r for r in runs_W3 if r["id"] not in RUN_BY_ID])
