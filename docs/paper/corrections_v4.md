# 제출본 정정 목록 v4 (2026-10-16) — Claude Science용

원칙: 두 docx(`ieie2026f_proceedings_final.docx`, `ieie2026f_blind_final.docx`)를 초안 v4(`docs/paper/ieie2026f_plan_and_draft_ko.md` §1·§4·Table 3)로 다시 만든다. 아래는 현재 docx의 문단별 문제 목록(감독 감사 `docs/v2/supervision.md` §1.2 그대로)과 v4에서 추가로 바뀐 점이다.

## A. 추가로 바뀐 것 (v4)
1. 제목: "서브마이크론 Cu 하이브리드 본딩의 접촉 결정 요인과 300 nm 공정창: 열탄성 접촉 한계와 표면확산을 결합한 모델의 사전등록 검증" / "What Determines Cu–Cu Contact in Sub-Micron Hybrid Bonding: Elastic Contact Limit and a Pre-Registered Thermo-Elastic/Surface-Diffusion Process Window at 300 nm". 방위를 연구 질문의 중심에 두지 않는다: "패드마다 통제할 수 없는 무작위 요인(recess 산포, 결정방위 등)"으로 일반화하고, 방위는 "수율 하위 꼬리를 정하는 요인"으로만 쓴다.
2. 두 경계 구분: 탄성 접촉 한계 0.70 µm(400 °C, R 5 nm; 3/8 nm → 0.55/1.0 µm; 대리식 0.76 µm; 350/300/250 °C → 0.90/1.14/1.62 µm). 기여도 역전 = 외삽 예측 0.74 µm(250 °C 2 h)–2.45 µm(400 °C 2 h). 출처 `results/stage2/boundaries.json`.
3. 계면: 같은 설정 평가표(초안 Table 3, `docs/stage2_v2_consistency_preregistration.md`). E70(미끄럼 폭 효과 0.35 vs 0.15), SC5/SC6(3 µm 미끄럼 −1.27/−1.23e-3).
4. 확산: ≥ 250 °C PPA-Cu 5/5, 전체 8/9(이전 "10/10" 삭제); β = 1/4 2.3σ 배척; DM2023 0/7 → 적용 범위 등크기·≥ 250 °C.
5. 방위 꼬리: "1.4 × 10⁻³" 삭제. f(ω) 4종 집합. 확률 기준 300 nm 청정 (B) 9셀 / (C) 5셀 / (A) 0셀; 최악 방위 기준은 f(0) 의존(0 → 닫히지 않음, 허용 0.5–0.9 nm/패드; 0.25 → 300 °C 2 h·350 °C 30 min 이상, 2.4–3.6 nm/패드). 확률 기준 허용 recess 3.5–9 nm/패드. 출처 `results/stage2/v2/f_omega_variants.json`, `docs/v2/diffusion_f_omega.md`.
6. 데이지체인 상한(≈ 500 링크) 문장은 꼬리 가정 의존이므로 본문에서 빼거나 "f(ω) 꼬리 가정 시 0–9 × 10⁻³ → 체인 상한은 가정 의존"으로만.
7. 그림: Fig. 2 → `results/figures/s2_boundaries.png`(두 경계, 외삽 음영), Fig. 4 → `results/figures/v2/three_region_map_0.30um.png`, Fig. 5 → `results/figures/v2/worst_margin_0.30um.png`. 기존 `s2_mechanism_transition.png` 제목은 "elastic contact limit"으로 재생성됨.

## B. 현재 docx 문단별 수정 목록 (감독 감사 원문)

### 1.2 수정할 주장 (파일 · 현재 문구 · 바꿀 문구)

| # | 파일 | 현재 문구(인용) | 바꿀 문구 |
|---|---|---|---|
| 1 | draft L52; proceedings_final 단락 60; blind_final 단락 43 (제목) | "접촉 기구 전환과 300 nm 공정창 예측" / "Mechanism Transition and 300 nm Process-Window Prediction" | "탄성 접촉 한계와 300 nm 공정창 예측" / "Elastic Contact Limit and 300 nm Process-Window Prediction" |
| 2 | proceedings_final 단락 4 (요약) | "접촉 기구는 recess 합 5 nm에서 약 0.7 µm를 경계로 표면확산으로 넘어가고" | "접합 계면 조건에서 위·아래 탄성 돌출 합이 recess 합 5 nm를 넘는 최소 폭(탄성 접촉 한계)은 약 0.7 µm이며, 확산 돌출이 탄성 돌출을 넘는 기여도 역전 폭은 {CROSSOVER}로 예측된다" |
| 3 | draft L13 (§1 핵심 메시지 (1)) | "접합 계면 조건에서 접촉 기구는 패드 폭 ≈ 0.7 µm … 에서 열탄성→표면확산으로 넘어가고" | "접합 계면 조건에서 탄성 접촉 한계는 ≈ 0.7 µm(recess 합 5 nm; 3→8 nm에서 0.55→1.0 µm)이고, 기여도 역전은 {CROSSOVER}(예측)" |
| 4 | draft L27, L81; proceedings 단락 23; blind 단락 10 | "3.1 열탄성 모델과 기구 전환" / "0.54 µm 실패 → 기구 전환(Fig. 2)" | "3.1 열탄성 모델과 탄성 접촉 한계" |
| 5 | Fig. 2 캡션 (proceedings 단락 27, blind 단락 15) | "Mechanism transition with pad size: … crossover ≈ 0.7 µm" | "Elastic contact limit vs pad size: the elastic pair reaches the 5 nm recess sum at ≈ 0.7 µm (imec data, interpolation between 0.54 and 1.26 µm); diffusion/elastic crossover {CROSSOVER} (model prediction)" |
| 6 | draft L92; proceedings 단락 43; blind 단락 30 (결론) | "접촉은 열탄성 팽창이 아니라 표면확산이 결정하며(전환 ≈0.7 µm)" | "접합 계면 조건에서 약 0.7 µm 아래는 탄성만으로 recess 합 5 nm를 닫지 못한다(실측 0.54·1.26 µm 사이 보간). 표면확산이 탄성보다 큰 영역은 {CROSSOVER}로 예측된다(실측 검증 아님)" |
| 7 | blind 단락 3 (기여 ①) | "기구 전환 폭을 recess 조건부 규칙으로 정량화" | "탄성 접촉 한계 폭을 recess 조건부 규칙으로 정량화(3/5/8 nm → 0.55/0.70/1.0 µm)" |
| 8 | draft L13·L17(기여 2); 보고서 §15 결론 문단; `stage2_lhostis_round2_preregistration.md` §4 판정 문단 | "ST/Leti 공정은 두 독립 관찰 … 모두 이완 계면을 가리킨다(held-out 폭 규칙 통과)" / "폭 효과는 접합 모델로, 두께 효과는 이완 계면으로 설명된다" | "ST/Leti 관측은 아직 단일 계면 설정으로 함께 평가되지 않았다: 폭 효과(held-out)는 접합 설정에서, 두께 효과와 Ayoub 300 nm 부호는 이완 설정에서 나왔다. 이완 설정의 폭 효과(E70)·3 µm 부호(SC5/SC6)가 계산되기 전까지 '이완 계면'은 후보 가설이다. 미끄럼 계산은 계면 박리를 의미하지 않는다" |
| 9 | draft L13 (1), L16 기여 1 | "탄성 항은 구속 계수 C(h/w) 한 곡선으로 모든 공정·크기에 대해 ±20 %로 예측된다" | "등방(Hill) 탄성 돌출은 imec·NYCU 채택 적층의 미사용 기하 4개에서 C(h/w) 대리식이 ±20 % 안(X35–X38). 방위 대리식과는 별개" |
| 10 | draft L139 (Table 3); 보고서 §13.3·§14 | "10/10 at ≥ 250 °C, PPA-Cu" / "250 °C 이상 PPA-Cu 전부 + ≤ 140 nm 패드 200 °C는 10/10" | "개정 1: ≥ 250 °C PPA-Cu 5/5, ≥ 250 °C 전체 8/9, 200 °C·D ≤ 140 nm 1/2" (재집계: `diffusion_validation_rev1.csv`) |
| 11 | draft L13 (3), §3.4 | "대립 Cu 미접촉 하한 10⁻³–10⁻²" | "관측 분위수(≈ 1 %) 아래 꼬리 가정에 의존하는 값: 기준 f(ω) 1.4–3.4 × 10⁻³, 비관 변형 2–4 × 10⁻²(관측되지 않은 구간)" |
| 12 | `stage2_diffusion_round3_preregistration.md` §1(b), draft §3.2 마스터 커브 문장 | "Mullins 스케일링(특성 길이 ∝ (Bt)^{1/4})에 따른 stretched exponential β = 1/4" | "β = 1/4는 시간 두 배 증가율 상한 2^{1/4} = 1.189를 갖는데, DM2026 200 °C 2 h→4 h 중앙값 비는 1.48 ± 0.20(400 nm)·1.50 ± 0.18(500 nm)로 상한을 1.5σ·1.8σ 넘는다(판독 오차만 반영). t^{1/4} 길이 법칙만으로 β = 1/4를 정당화할 수 없다" |
| 13 | 보고서 §15 리뷰 행, draft §3.4 | "P ≥ 0.99 창은 <111> 꼬리 모양이 정함" | 유지하되 "f(ω)는 탐색 라운드 2(미검증); 완전 facet 분율(f = 0, 기준 1.5 %)과 lagging-tail 분율(h < 6.5 nm, 기준 8.3 %, 실측 ≈ 10 %)을 구분" 추가 |


