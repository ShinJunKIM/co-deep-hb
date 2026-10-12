# Stage 2 기준 모델 보고서 — sub-µm Cu/dielectric 하이브리드 본딩 (0.54 µm 선택, 300 nm 예측)

작성 2026-10-13. 연구 책임 세션(Fable). 저장소 `pwqppt/co-deep-hb`. 사전등록 33a8f5c, V&V 계획 `docs/stage2_vv_plan.md`, 탐색 로그 `docs/stage2_exploration_log.md`.
용어: recess(CMP 깊이, 입력) / u(Cu 돌출, 모델 출력, nm) / ε′zz(Laue 편차 탄성 변형률). 섞지 않는다.

## 1. 목적과 구조

**질문.** Cu 패드가 1 µm 아래로 작아질 때 추가로 고려할 인자는 무엇이고, 어떤 레시피(recess, 어닐 T·시간, 라이너/계면 상태)가 최적인가.
**구조.** ASME V&V 10-2019의 순서를 따른다: (1) 코드·해 검증(verification: 메시·셀·2D/3D 일관성), (2) 보정(calibration: 보정 데이터에서만, 문헌 범위 안), (3) 검증(validation: held-out 데이터, 재조정 금지), (4) 예측(prediction: 불확실도 포함). 검증 전에 고정 파라미터와 통과 규칙을 `stage2_vv_plan.md`에 커밋했다.
**선택 크기.** 실측이 가장 많은 0.54 µm(imec 공정: in-situ u(T) 100–400 °C, bulge-out 분포, recess 분포, 접촉저항)를 기준 크기로 삼고, 300 nm는 검증된 모델의 예측으로 다룬다.
**두 단계.** (a) 접촉 단계: u_top + u_bot + h_d,top + h_d,bot ≥ r_top + r_bot. u는 ANSYS 열탄성, h_d는 표면확산 해석식. (b) 연결 단계: 접촉 후 접촉면적·압력(ANSYS 접촉 해석) → 구속저항 proxy. (b)는 저저항의 필요조건이다.

## 2. 데이터

| ID | 출처 | 역할 |
|---|---|---|
| D-imec | De Messemaeker 2023 ECTC Fig 1(Okudur 2017): 0.54/1.26/1.80/3.06 µm, 깊이 600 nm, Cu/SiCN, TaN/Ta 6 nm, 100–400 °C, 비접합 | 보정(3.06, 1.80) / 검증(1.26, 0.54) |
| D-Lin | Lin 2025 ASS: 9/3/1 µm, PECVD SiO2, Ta 50 nm, 25–200 °C | 보정(9, 3) |
| D-Chen | Chen 2025 ECTC: 1 µm 2.1 nm(8–9개 평균) | 검증(NYCU 1 µm, Lin과 한 점) |
| D-Ayoub | Ayoub 2022 MEE: 300 nm ε′zz(T), 400 °C 보유, 냉각 | 300 nm ε′zz 시험(V5·V6), H_sw |
| D-DM | De Messemaeker 2023 Fig 7–12: bulge-out 분포(230–350 °C, 5 min–2 h, 방위) | 확산항 일관성 점검 |
| D-IRPS | Van Huylenbroeck 2026 IRPS Fig 6: recess 평균 2–3 nm, ±1 nm | 예측 입력 |
| D-Lho | Lhostis 2024 JEM: ρc(d/d0, w), 400–720 nm | 연결 단계 상대 시험 |

## 3. 모델

- 기하: 원형 Cu 패드(폭 w, 깊이 h), 측벽 테이퍼, Ta 라이너 링+바닥층, 유전체 매립, Si slab(두께 = 셀 폭, 외벽에 α_Si·ΔT·L 변위, 바닥 UZ = 0). 2D 축대칭(PLANE182 enhanced strain) 또는 3D(SOLID185, O-grid 원형 패드).
- 재료: Cu C11/C12/C44 168.4/121.4/75.4 GPa(방위별 회전) 또는 Hill 등방 128.3 GPa/0.345; α_Cu 16.5 ppm/K; Si 130 GPa/0.28/2.6; Ta 186 GPa/0.34/6.5; 유전체 E·α는 공정별 보정값(§5).
- 측벽: bonded(노드 공유) 기본, sliding(법선만 구속)은 대조군.
- u 정의(모든 데이터 공통): 중앙 50 % 면적 평균 − AFM 시야 안 유전체 표면 평균(u_c50). 중심값(u_ctr)과 전체 평균(u_full)도 보고.
- 표면확산 항(ANSYS 밖): h_d = s_ox·0.0022·(θ−90°)·D·[1 − exp(−t/τ)], τ = τ₀·(D/200 nm)^3.7·Ds(350 °C)/Ds(T), Q = 20.7 kcal/mol(Butrymowicz 1973), θ = 123°(Cu/Ta), τ₀ ∈ [20, 100] s(DM2023·Tsau 2023), 산화 표면 s_ox ≈ 0.45(DM2023 Fig 10).

(이하 §4–§9는 결과 확정 후 작성)
