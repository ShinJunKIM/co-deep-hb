r"""Render docs/stage2_vv_plan.md from the verification table and the adopted calibration (results/stage2/).
Run AFTER --verify and --calibrate and BEFORE any held-out comparison; commit the output."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "stage1"))
import baseline as B  # noqa: E402

OUT = B.RESULTS / "stage2"
DOC = B.REPO / "docs" / "stage2_vv_plan.md"


def main():
    ad = json.loads((OUT / "adopted.json").read_text())
    ver = (OUT / "verification.csv").read_text().strip().splitlines()
    grid = (OUT / "calibration_grid.csv").read_text().strip().splitlines()
    ny, im = ad["nycu"], ad["imec"]
    L = []
    L.append("# Stage 2 V&V 계획 — 고정 파라미터와 통과 규칙 (held-out 비교 전 커밋)\n")
    L.append("ASME V&V 10-2019 순서: 검증(verification) → 보정(calibration) → 검증(validation) → 예측. 이 문서는 보정이 끝난 시점의 **고정값**과 "
             "held-out 통과 규칙을 기록한다. 이 커밋 이후 보정 파라미터는 바꾸지 않는다. 검증 실패 시 한 번의 문서화된 개정만 허용(이유를 먼저 커밋).\n")
    L.append("## 1. 검증(verification) 결과\n")
    L.append("| 점검 | 기준 | 시험 | 차이 % | 한계 % | 통과 |\n|---|---|---|---|---|---|")
    for row in ver[1:]:
        p = row.split(",")
        L.append("| " + " | ".join(p[:6]) + " |")
    L.append("\n채택: 2D 셀 12w(모든 런), 3D 셀 12w + 성긴 원거리 격자, 패드 반경당 40 요소(2D)/10 요소(3D). "
             "film-limit 편차(+26 %)는 모델 형태(기판·유전체 탄성)이며 Step 13 R40과 같다.\n")
    L.append("## 2. 보정(calibration) — 보정 데이터에서만, 문헌 범위 격자 안에서만\n")
    L.append("u 정의: " + ad.get("u_key", "du_c50") + " (중앙 50 % 면적 평균 − AFM 시야 유전체 평균). 목적함수 J = Σ[(u_model − u_meas)/σ]².\n")
    L.append("### NYCU 공정 (Lin 9 µm 6.4 ± 0.4, 3 µm 4.1 ± 0.4 nm @200 °C)\n")
    L.append(f"- 채택: **E_SiO2 = {ny['E_d']/1000:g} GPa, α_SiO2 = {ny['a_d']*1e6:g} ppm/K, 테이퍼 = {ny['taper']:g}°**, J = {ny['J']:.2f}. "
             f"경계값(bound-limited): {ny['bound_limited'] or '없음'}. Ta 50 nm 고정.")
    for r in ny["residuals"]:
        L.append(f"  - {r['w']:g} µm @{r['T']:g} °C: 모델 {r['model']:.2f} / 측정 {r['meas']:.2f} ± {r['sigma']:.1f} nm → {'OK' if r['ok'] else '2σ 밖'}")
    L.append(f"- 보정 통과(모든 점 2σ 안): **{ny['pass']}**\n")
    L.append("### imec 공정 (DM2023 Fig 1: 3.06, 1.80 µm @100/200/300/400 °C)\n")
    L.append(f"- 채택: **E_SiCN = {im['E_d']/1000:g} GPa, α_SiCN = {im['a_d']*1e6:g} ppm/K**, J = {im['J']:.2f}. "
             f"경계값(bound-limited): {im['bound_limited'] or '없음'}. TaN/Ta 6 nm, 테이퍼 0° 고정.")
    for r in im["residuals"]:
        L.append(f"  - {r['w']:g} µm @{r['T']:g} °C: 모델 {r['model']:.2f} / 측정 {r['meas']:.2f} ± {r['sigma']:.1f} nm → {'OK' if r['ok'] else '2σ 밖'}")
    L.append(f"- 보정 통과: **{im['pass']}**\n")
    L.append("### 격자 전체 (J 오름차순; `results/stage2/calibration_grid.csv`)\n")
    L.append("```\n" + "\n".join(grid[:40]) + ("\n..." if len(grid) > 40 else "") + "\n```\n")
    L.append("## 3. 고정 상수 (조정 금지)\n")
    L.append("Cu C11/C12/C44 168.4/121.4/75.4 GPa; Cu α 16.5 ppm/K; Hill 128.3 GPa/0.345; Si 130/0.28/2.6; Ta 186/0.34/6.5; 라이너 NYCU 50, imec 6, ST 13 nm; "
             "확산 Q 20.7 kcal/mol, θ 123°; 다결정 소성 Okoro σy = (193 − 0.185T)(1 + εp^0.3) MPa; ρ_i 5e-11 Ω·cm².\n")
    L.append("## 4. Held-out 검증 세트와 통과 규칙 (이 커밋으로 고정)\n")
    L.append("| V | 데이터 | 모델 런 | 규칙 |\n|---|---|---|---|")
    L.append("| V1 | imec 1.26 µm u(100/200/300/400) | S51 (2D Hill, imec 채택값) | 4점 모두 \\|Δ\\| ≤ 0.5 nm 또는 ≤ 15 % |")
    L.append("| V2 | imec 0.54 µm u(100/200/300/400) | S52 (2D Hill), S53–S55 (3D [001]/[101]/[111]) | Hill 4점 \\|Δ\\| ≤ 0.4 nm; 3방위 범위가 측정 ±0.3 nm와 겹침 |")
    L.append("| V3 | NYCU 1 µm 2.1 ± 0.4 nm @200 °C (Chen 평균; Lin 2.3 보조) | S56–S58 (3D, NYCU 채택값, Ta 50, 테이퍼 채택값) | 3방위 범위가 2.1 ± 0.4와 겹침 |")
    L.append("| V4 | 판별 | S59 (0.54 sliding), S60 (1 µm [001] sliding) | sliding이 V2 또는 V3에서 실패(\\|Δ\\| > 0.4 nm) |")
    L.append("| V5 | Ayoub 패드 3·10 가열 기울기 | S61, S62 (3D 300 nm, 캡, Ta 13, NYCU SiO2 채택값) | 부호 일치 + ±25 % (사전 예측 FAIL) |")
    L.append("| V6 | Ayoub Δε′zz vs E_z 순위상관 | 기존 R27/R35–39, R26/R31–34 | 음의 상관 부호 |")
    L.append("| H_sw S2 | Ayoub 패드 3 400 °C 보유 +0.65e-3 | S63 − R35 | 부호 일치 & 크기 충분 → 일관 |")
    L.append("| E | Lhostis β(w) 개회로 dishing 비 0.79 | E17–E24 | r_open(400)/r_open(720) ∈ 0.79 ± 0.15 |")
    L.append("\n**VALIDATED = V1–V4 전부 통과.** 실패하면 기록하고, 한 번의 개정(이유 선커밋) 후 두 결과를 모두 보고한다.\n")
    L.append("## 5. 사전 예측 (보정 직후, 검증 런 전)\n")
    L.append(f"- V2 0.54 µm: 보정 전 중간값에서 du_c50 2.58 nm @400 °C(SV09) vs 측정 1.40 ± 0.5 → **FAIL 예상**(탄성 bonded 모델의 과대예측). "
             f"V1 1.26 µm: 경계선. V3: 통과 예상. V4: sliding 실패 예상(판별 성립). V5: FAIL 예상.\n")
    DOC.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(DOC)


if __name__ == "__main__":
    main()
