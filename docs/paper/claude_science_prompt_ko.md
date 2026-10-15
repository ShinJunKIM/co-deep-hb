# Claude Science 전달 프롬프트 — IEIE 2026 추계 학부생 논문경진대회 원고·그림 제작

(아래 블록을 그대로 전달. 저장소 `pwqppt/co-deep-hb` 최신 main에 접근 권한을 함께 줄 것.)

---

## 역할과 목표
너는 이 연구의 논문 제작 담당이다. 저장소 `co-deep-hb`(main)에 있는 결과 파일과 문서만을 근거로, 2026 대한전자공학회 추계학술대회 **학부생 논문경진대회** 제출물 두 개와 그림 6장을 만든다. 마감 2026-10-19. 목표는 1차 서면(블라인드) 통과와 수상이다. 숫자·주장은 저장소 파일에서만 가져오고, 없는 숫자는 만들지 않는다. 불확실하면 "[확인 필요]"로 표시한다.

## 2026-10-16 갱신 — 추가 결과(반드시 반영)
- 초안 §1이 v3로 바뀌었다(핵심 메시지 네 결론: 전환 규칙+대리식, 계면 상태 = 공정 입력, <111> 꼬리가 창을 정함, Q_eff 13·적용 범위). `docs/stage2_baseline_report_ko.md` §15와 `docs/agents/*.md`, `results/stage2/{round_x2.json, lhostis_round2.json, diffusion_round3.json, window_sensitivity_review.json, agents/*.json}`을 읽어라.
- 추가 그림 후보: Fig. 2(b) 구속 계수 C(h/w)(`results/figures/agents/constraint_factor.png`, X35–X38 통과점 포함), Fig. 3(d) 마스터 커브(`master_curve.png`), Fig. 6(c) 체인 수율(`yield_vs_chain_length.png`), 연결 단계 두께·폭 효과 표(라운드 2). 쪽수 안에서 Fig. 2(b)와 라운드 2 표를 우선.
- 문장 규칙 추가: "탄성만으로는 못 닫는다"에는 "접합 계면 조건에서"를 붙인다. "≥250 °C 10/10"은 개정 1 수치, 방위 모델은 8/10. 확산 항 적용 범위 "등크기 패드(cavity/pad ≥ 0.7), ≥ 250 °C"; DM2023 held-out 0/7 실패를 한계로 명시. 라이너 가설 기각(X30–X34). 대리식 ±20 % 통과(X35–X38, 사전등록). 계면 상태 가설은 "세 관찰과 일관"까지만.

## 반드시 먼저 읽을 파일 (순서대로)
1. `docs/paper/ieie2026f_plan_and_draft_ko.md` — 기획, 핵심 메시지, 기여 3개, 절 구성, 그림·표 목록, 전문 초안, 참고문헌. **이 문서의 §1 핵심 메시지와 기여 3개를 그대로 쓴다.**
2. `docs/stage2_baseline_report_ko.md` §13–§14 — 결과와 모델 부분별 검증 상태(검증 통과/실패/탐색 등급).
3. 수치 원본: `results/stage2/paper_results.json`(기구 전환 크기, recess 허용 사양, 방위 하한, transition_vs_recess), `results/stage2/window_summary.json`(공정창·빗금 셀·인자 순위), `results/stage2/orient_diffusion_round2.json/.csv`(확산 항 적합·검증 점), `results/stage2/validation_rev1.csv`와 `results/stage2/adopted_rev.json`(탄성 학습·테스트), `inputs/dm2026_digitized.json`(DM2026 판독값과 오차), `results/stage2/diffusion_validation_rev1.csv`.
4. 양식(저장소 `docs/paper/templates/`): `논문양식.docx`(프로시딩, Double column 1–5쪽), `서면 심사용 논문 양식.docx`(논문지 양식 4쪽, 저자·소속 삭제), `논문 경진대회 안내.txt`. 현재 초안 docx: `docs/paper/ieie2026f_proceedings_draft.docx`, `docs/paper/ieie2026f_blind_review_draft.docx`(placeholder 포함; 네가 완성본으로 대체한다).
5. 참고문헌 상세: `docs/REFERENCES.md`.

## 산출물
A. `ieie2026f_proceedings_final.docx` — 프로시딩용. 한국어 본문, 영문 제목·그림·표·참고문헌. 4–5쪽. 저자란은 "[저자 기입]"으로 비워 둔다.
B. `ieie2026f_blind_final.docx` — 서면 심사용. **정확히 4쪽**. 저자·소속·이메일·저장소 URL·커밋 해시·"우리 연구실" 등 식별 가능한 문구 금지("공개 저장소에 사전등록(채택 후 공개)"으로 표기).
C. 그림 6장(PNG 600 dpi + SVG), 영문 라벨, 단 폭 8.2 cm에서 글자 7 pt 이상 읽히게. 파일명 `fig1_architecture`, `fig2_transition`, `fig3_diffusion`, `fig4_window300`, `fig5_recess_spec`, `fig6_factors`.
D. 체크리스트 보고: 쪽수, 모든 숫자의 출처 파일, 식별 문구 검사 결과, 그림별 데이터 출처.

## 심사위원이 10초 안에 읽어야 하는 것 (글의 우선순위)
1. 문제: 1 µm 아래에서 열탄성 팽창(패드당 ≈ 1 nm)으로는 CMP recess 합(≈ 5 nm)을 못 닫는다.
2. 새로움 한 줄: **세 연구그룹 실측으로 사전등록 검증한 열탄성–표면확산 결합 모델**로 (a) 접촉 기구 전환 폭을 recess 조건부 규칙으로 정량화하고(recess 합 3/5/8 nm → 0.55/0.70/1.0 µm), (b) sub-µm에서 결정 방위의 효과가 탄성 항(4 %)이 아니라 표면확산 항(<111> facet, 폭 10배)을 통해 들어옴을 보여 Ayoub의 [111] 기준 recess 사양을 정정하고, (c) 300 nm 공정창·CMP recess 허용 합·방위 미접촉 하한·인자 순위를 불확실도와 함께 준다.
3. 신뢰성: ASME V&V 10 순서, 결과 보기 전 기준 커밋, 실패도 보고(Table 3).
4. 한계를 숨기지 않음: 0.54 µm +46 %(원인 미상), 확산 항은 ≥ 250 °C에서만 실측 일치(200 °C 과소 = 보수적), 방위 항은 탐색 등급, 300 nm 돌출 실측 없음.

## 주장 수위 규칙 (위반 금지)
- "검증된 레시피"라고 쓰지 않는다. "검증 통과 범위의 탄성 모델 + 실측으로 점검한 확산 모델로 본 공정창 예측(불확실도 포함)".
- 등급을 표와 본문에서 구분: **검증 통과(사전등록)** / **검증 실패** / **탐색(exploratory round 2)** / **예측**. Table 3 형식 유지.
- Ayoub 300 nm Laue 변형률: "3 µm 부호 일치, 300 nm는 기울기 크기 일치·부호 반대, 다른 공정·시료라 계면 상태 차이로 본다(가설)". **크기 재현을 주장하지 않는다.** 미끄럼 측벽은 상한 시나리오.
- 0.54 µm는 기준 크기가 아니라 "탄성 모델이 틀리기 시작하는 참고점". 300 nm가 확산 항이 실측 점검된 크기(DM2026 500 nm 피치 바닥 패드 = 300 nm).
- 방위 ↔ 확산 관계의 **존재**는 imec 실측(DM2026 EBSD)이 보인 것이고, 우리는 그것을 f(ω) 항으로 만들어 분포 폭을 재현하고 공정창에 연결했다 — 발견한 것처럼 쓰지 않는다.
- "미세구조"라는 말은 "텍스처(<111> 분율)·결정립 수"로 풀어 쓰고, 결정립 수·도금 후 어닐 이력은 모델 밖(한계)임을 명시.
- 확산 항 h_d ∝ D는 D ≤ 300 nm에서만 실측 점검; 0.54 µm 확산 창은 외삽이라고 쓴다.

## 절 구성 (프로시딩; 서면용은 괄호의 압축 지침)
요약 150–200자 / I. 서론: 문제 1문단 → **두 기구 분해 관점(열탄성 u + 표면확산 h_d, 접촉 조건 m = u_t+u_b+h_d,t+h_d,b−(r_t+r_b) ≥ 0)** 1문단 → 선행연구 역할 분담과 빈 자리 1문단 → 기여 3개 / II. 모델과 검증 절차: 2.1 용어(recess·u·ε′zz·h_d 섞지 않기) 2.2 열탄성 FEM 2.3 식 (1)과 f(ω) 2.4 V&V·사전등록(Table 1) / III. 결과: 3.1 탄성 학습·테스트(Table 2)·측벽 판별·0.54 µm 실패 → 기구 전환(Fig. 2, 전환 규칙의 계산 절차 명시) 3.2 확산 항 테스트(Fig. 3) 3.3 Ayoub 한 문단 3.4 300 nm 창(Fig. 4)·recess 사양(Fig. 5)·인자 순위와 방위 하한(Fig. 6)·연결 단계 한 문단 / IV. 한계와 결론(Table 3, 향후 연구 2줄: 표면 확산을 FEM 안에 넣어 γ(ω)로 f(ω) 대체; fg-Cu 실측을 보정점으로 한 다음 사전등록) / References 영문. (서면용 4쪽: Fig. 1·5·6과 Table 1 생략, 서론 절반, 2.2–2.3을 식 하나와 표 하나로.)

## 그림 사양 (데이터 출처 고정)
- Fig. 1 (새로 작도): (a) 패드 쌍 단면 — recess r, u, h_d, 접촉 여유 m; (b) V&V 흐름 — 수치 검증 → 학습(큰 패드) → 테스트(held-out) → 예측(MC), "기준 커밋" 표시.
- Fig. 2: `paper_results.json` mechanism_transition + transition_vs_recess; 데이터 점: 탄성 실측(imec 0.54/1.26/1.80/3.06 µm, 400 °C: 1.40/5.00/5.40/7.85 nm ×2), 모델(2.04/4.04/4.99/6.32 ×2, ×0.69 점선), 확산 포화 진폭(≤ 300 nm 실선, 0.54 µm까지 점선 "외삽"), recess 합 5 nm 수평선, 교차 ≈ 0.7 µm 화살표. 인셋: 전환 폭 vs recess 합(3→10 nm).
- Fig. 3: `orient_diffusion_round2.csv`: (a) Fig. 3 400/500 nm 피치 중앙값+IQR(실측) vs 모델 중앙값, 조건별; 실패 점은 빈 기호; (b) 250 °C 1 h 크기 의존(115/140/250/300 nm); (c) f(ω) 곡선(ω_c 5°, Δω 19.5°)과 facet 분율.
- Fig. 4: `window_summary.json` "0.30um" clean/oxidised P_contact 격자, hatched_cells 빗금, 권고 셀(250 °C×120 min, 300 °C×30 min) 테두리.
- Fig. 5: `paper_results.json` recess_spec_sum_nm_300nm clean/oxidised 격자(nm 숫자 표기).
- Fig. 6: (a) `window_summary.json` factor_cells_changed(0.54/0.30 µm, clean) 막대; (b) `paper_results.json` orientation_floor_300nm P_open facet vs no-facet 로그 막대.
- 모든 그림: 영문, 색각 안전 팔레트, 단위 표기, 캡션은 초안 §3 표의 영문 캡션 사용.

## 표
Table 1 Datasets and roles, Table 2 Elastic train/test, Table 3 Model-part status — 초안 §5의 내용을 영문으로, 숫자는 원본 파일과 대조.

## 참고문헌
초안 §4 References 15편을 IEIE 양식(영문; 논문지명 이탤릭; 본문 인용 [n] 윗첨자)으로. [15] Okoro와 [8] Tsau의 완전한 서지는 `docs/REFERENCES.md`·보고서에 없으면 "[확인 필요]" 표시.

## 금지
- 저장소에 없는 수치·실험·그림 생성, 선행연구 결과를 우리 결과처럼 쓰기, "검증됨" 등급 상향, 블라인드본에 식별 문구.

## 마지막 보고 형식
1) 두 docx 쪽수(Word 기준), 2) 그림 6장 파일명과 데이터 출처, 3) 본문 모든 수치의 출처 파일 표, 4) 식별 문구 검사 결과, 5) "[확인 필요]" 목록.
---
