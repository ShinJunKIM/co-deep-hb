# 실행 스크립트 (v4 정합성 라운드 + v2 방위 연구)

ANSYS는 한 번에 하나만 돈다. 각 스크립트는 이미 끝난 런(`results/<ID>/record.json` 존재)을 건너뛴다. 실행 전 다른 MAPDL 작업이 없는지 확인(`Get-Process ANSYS* -ErrorAction SilentlyContinue`).

## A. 제출본 정합성 라운드 (main 브랜치, 작업 경로 `$HOME\co-deep-hb`)

```powershell
cd "$HOME\co-deep-hb"; git pull
.\.venv\Scripts\python.exe src\stage2\stage2_lhostis_r2.py --run      # E70 (E64-E69는 완료돼 있으면 건너뜀) -> results\stage2\lhostis_round2.json
.\.venv\Scripts\python.exe src\stage2\stage2_wide.py --case SC5,SC6    # 3 um, 미끄럼 + 접합 캡 / 미끄럼 + 캡 없음 -> results\SC5, SC6\record.json
.\.venv\Scripts\python.exe src\stage2\stage2_boundaries.py             # ANSYS 없음: 두 경계 -> results\stage2\boundaries.json, results\figures\s2_boundaries.png
.\.venv\Scripts\python.exe src\v2\f_omega_variants.py                  # ANSYS 없음: f(omega) 변형·beta 점검·세 영역 지도·최악 방위 -> results\stage2\v2\f_omega_variants.json
```

| 단계 | 산출물 | 확인 방법 | 시간: 사전 추정(기존 로그) | 실측 |
|---|---|---|---|---|
| E70 | `results/E70/record.json` | `stage2_lhostis_r2.py --judge` 출력의 E70 V(0.35 기대 아님 — 규칙: V ≥ 0.25) | 1–4 min(E64 245 s, E67 52 s) | 319 s |
| SC5 / SC6 | `results/SC5|SC6/record.json` | `rows[0].eps_dev_zz` < 0이면 Ayoub 3 µm 부호 일치 | ≈ 3 min 각(SC1 184 s) | 183 s / 177 s |
| 두 경계 | `boundaries.json`, 그림 | 출력의 elastic limit / crossover | 수 초 | 수 초 |
| f(ω) | `f_omega_variants.json`, `results/figures/v2/*.png` | 출력의 region counts, beta check | 수 분 | ≈ 5 min |

판정 기록: `docs/stage2_v2_consistency_preregistration.md` 결과 절, `docs/v2/diffusion_f_omega.md`.

## B. 후속 연구 v2 (브랜치 `v2-orientation`, 작업 경로 `$HOME\co-deep-hb-v2`)

```powershell
cd "$HOME\co-deep-hb"; git fetch
if (-not (Test-Path ..\co-deep-hb-v2)) { git worktree add ..\co-deep-hb-v2 v2-orientation }
cd "$HOME\co-deep-hb-v2"; git pull
$py = "$HOME\co-deep-hb\.venv\Scripts\python.exe"
& $py src\stage2\stage2_v2_orient.py --list                              # 154 런 목록(VB = 접합, VS = 미끄럼)
& $py src\stage2\stage2_v2_orient.py --run --side bonded                 # VB001-VB077
& $py src\stage2\stage2_v2_orient.py --run --side sliding                # VS001-VS077
& $py src\stage2\stage2_v2_orient.py --analyze                           # -> results\stage2\v2\orientation_study.json, results\figures\v2\orientation_surface_0.30um.png
& $py src\v2\orient_window.py                                            # 대리모델로 공정창 재계산 -> results\stage2\v2\orient_window.json
& $py -c "import sys; sys.path[:0]=['src/stage2','src/stage1']; import stage2_v2_orient as V, baseline as B; B.execute([r['id'] for r in V.CONTACT], 4)"   # E71-E74 접촉 경계
```

| 단계 | 산출물 | 확인 방법 | 시간: 사전 추정 | 실측 |
|---|---|---|---|---|
| VB 77런 | `results/VB0xx/record.json` | `--analyze` 출력의 surrogates·same-Ez·in-plane | 25–30 s/런(S68 25 s) → ≈ 35 min | 평균 27 s(26–28) |
| VS 77런 | `results/VS0xx/record.json` | 같음 | 30–60 s/런(미끄럼 3D 실측 없음) | 평균 48 s(28–57) |
| orient_window | `orient_window.json` | region counts, E_z 적합 대비 바뀐 셀 | 수 분 | ≈ 5 min |
| E71–E74 | `results/E7x/record.json` | 중심 공극 분율 V ≤ 0.05 = 닫힘(`docs/v2_contact_boundary_preregistration.md`) | 1–6 min/런 | 결과 절 참조 |

판정 기록: `docs/v2_orientation_preregistration.md` §6, `docs/v2_contact_boundary_preregistration.md` 결과 절.
