# Policy-task audit — premium_billing_and_grace / task 1

## revision_1

## source_derivation_frozen
- Frozen 2026-10-18T03:42Z by the independent policy auditor, before any GT field of either task was read. Inputs: masked view `.audit_views/policy/premium_billing_and_grace/r1/task_1.json` (sha256 e3b13defdc4259c5420d0af726ff21a908730b8a09232be41a832ac6d347f420), charter sha256 24a5e811…fbdc, task_tools.py sha256 87aa55fb…107f. Masked fields not read: evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*.
- contamination_disclosure: none. tasks/1.json, plan.md and worklog.md were not opened and no grep ran over tasks/.
- Charter-global conclusions are cited from `audits/policy_task/premium_billing_and_grace/_difficulty.md`.

### policy_self_consistency (this task only)
- Handling time: DTC and REC are evaluated on the opening world at 2026-11-24. RNP is evaluated after both credits are booked. DTC reads only dental_ppo-line credits and REC only ortho_rider-line credits, so the two writes do not interact: DTC = 171.99 before and after REC, and REC = 46.28 before and after DTC (scratch replay). The parallel edges commute.
- Real-world waits: none. The renewal invoice exists (issued 2026-11-17), and the vision application (2026-11-10, effective 2027-01-01) is a seeded record.
- Charter-global findings that bear on this task, with consequences on this world:
  - `_difficulty.md#findings/C1`. VTC's replaced_by puts every non-vision termination credit, rider credits included, "under the base rule". The base reading credits the rider premium billed for whole months after August through the last month billed. That is Sep 2026–Dec 2027, less the already-credited 2026-09 (its distinguish_by key blocks a second 2026-09 credit): 15 × 12.096 (12.60 billed at the 4 % prepay discount) = **181.44**, against the REC reading of **46.28**. The renewal payment then becomes **840.64** instead of **975.80**.
  - `_difficulty.md#findings/C2`. Under base invoicing the added vision plan is priced at its recorded coverage tier (family, Select 150 = 43.28), giving 12 × 43.28 × 0.96 = 498.59. The renewal payment is then **1152.17**, against **975.80** under r_vtier (member_spouse 27.97).
  - `_difficulty.md#findings/C6`(i). r_vtier's weight here exists only because r_vstart sits on T1 (12 months). With r_vstart at its fall-through, r_vtier's sensitivity would be 0. (iii) Substituting dtc_dup's baseline gives 220.23 in the compute; read by the words ("the plan-change difference credits deducted above" are then none) the lag base runs over 4 months, giving interest 3.03 and a credit of 220.99. The booking args move to 2026-09 / 4 months.
  - `_difficulty.md#findings/C7`. dtc_window T2 is inert, so DTC keeps no honest method factor. r_vstart (T1≡T2) and r_giveback (method-shape FAIL) both fail, so RNP keeps no honest method factor.
  - `_difficulty.md#findings/C8`. Gold carries dtc_recover 25.00 and rc_recover 10.00 from conditions that do not separate erroneous from routine billing (iii). r_giveback T2 charges the standing 5.77 credit now to refund it later (iv). dtc_basis / rc_basis have an unreal T2 (ii, not taken here).
  - `_difficulty.md#findings/C9`: the DTC and REC credits' coverage_month / months_covered are scored from prose only.
  - C3, C4, C5, C10 and C11 move no value on this world. C3 is masked because the seeded renewal invoice is stale (O-T1-1).

### problem_chain
- Root: "you want to pay next year now, by card, yourself … you want the payment you make today to cover that [vision plan] too … You would like the agent to work out the right amount for next year." Policy: RNP (Annual Prepay account `946e939c…`, in-person payment for the coming prepaid year). Owner user: `submit_renewal_payment_53926ce3`.
- RNP's two prerequisite sentences (state form):
  - Dental: the ledger must carry dental-line plan-change difference credits covering every prepaid month after the termination of each LOE dependent. Gabriel `d4d159f4…` ended 2026-08-31 (loss_of_eligibility); paid-through is 2026-12-31, so Sep–Dec are prepaid. The only dental credit `f5f735e9…` covers 2026-09 (1 month), so the state is **false at the opening**. Resolver: the policy booking plan-change difference credits on the dental line, DTC → `book_dental_tier_credit_2a6e4a9b` (agent).
  - Rider: the ledger must carry rider-line termination credits covering every prepaid month after each ended rider. Rider `2b9dff86…` was terminated 2026-08-31 (base_plan_ended). The only rider credit `039e4e32…` covers 2026-09, so the state is **false at the opening**. Resolver: REC → `book_rider_end_credit_fb22198c` (agent). The cancelled rider `261b5f8d…` (application withdrawn, never billed) is not "ended" under REC's "status is terminated".
- Tree: {RNP ← DTC, RNP ← REC}. n=2, both edges value_input (the credits enter `bal`), max(n−1,1)=1 satisfied. One owner=user write. No cycle. Order: DTC and REC in either order, then RNP.
- Load-bearing: with both credits **975.80**; skipping DTC **1147.79**; skipping REC **1022.08**; opening world **1194.07**.
- Tools validate nothing (task_tools.py lines 182–200, 223–241, 260–277).
- Persona raises only the root and the vision coverage the customer wants included. Gabriel, the rider and refunds come up only if the agent asks. No prerequisite is named; the persona closes at the card confirmation.

### task_independent_derivation
Act now (renewal invoice issued, card payment by the holder herself).

**DTC credit (agent), handling time = opening world, 2026-11-24.**
- Departed dependent Gabriel (tier family). Subscriber active `0756d14e…` Plus 1500 member_spouse; recorded tier change 2026-10-01. Tier difference 131.17 − 80.92 = 50.25.
- dtc_basis T1: prepay 4 %, and the 12-month invoice `d9049c83…` (2026-11-17) is within 12 m, so 48.24. Near-miss: invoice `a27aec9b…` (2025-11-17) is exactly 12 whole months back and excluded.
- dtc_window T1: the tier change comes MONTHS(2026-08-31, 2026-10-01) = 1 month after the end, so months = MONTHS(2026-08-31, 2026-12-31) = 4. T2 is not taken; tier-change request `0fcc8429…` is withdrawn (near-miss).
- dtc_dup T1: `f5f735e9…` (48.24) counts (MONTHS 2 ≤ 2); 1 month covered.
- dtc_int: 85 days, which falls in (30, 90], so 10 % × 50.25 × (4−1) × 55/365 = 2.271575.
- dtc_recover: the last invoice was issued 78 days after the end (≥ 60), so 25.00.
- core = 48.24×4 − 48.24 = 144.72. **credit_amount = 171.99**, coverage_month **2026-10**, months_covered **3**.

**REC credit (agent), handling time = opening world.**
- Rider Family 1500 = 12.60.
- rc_months T1: prepay account with a 12-month invoice in 12 m, so MONTHS(2026-08-31, 2026-12-31) = 4. The baseline would count 16, through Dec 2027.
- rc_basis T1: 12.60 × 0.96 = 12.096.
- rc_dup T1: `039e4e32…` 12.10.
- rc_recover: 78 days ≥ 60, so 10.00.
- core = 12.096×4 − 12.10 = 36.284. **credit_amount = 46.28**, coverage_month **2026-10**, months_covered **3**.

**RNP payment (user), after both credits.**
- bal = 4968.69 − 3312.46 − (5.77 + 48.24 + 12.10 + 171.99 + 46.28) = 1371.85.
- r_dental T1 = 12 × 50.25 × 0.96 = 578.88.
- r_rider T1 = 12 × 12.60 × 0.96 = 145.152.
- r_vstart T1: the subscriber's applied vision `08852f82…` starts 2027-01-01 = renewal start, so 12.
- r_vtier T1: elected family, no child applied, spouse `c1a26c05…` applied, so Select 150 member_spouse 27.97.
- r_giveback T2: no billing_requests on record; overpayment credit `fadf8d04…` 5.77.
- result = RND(MX(0, 1371.85 − 578.88 − 145.152 + 12×27.97×0.96 + 5.77)) = **975.80**, by card, billing_account_id `946e939c-d506-45ce-ae99-9205fc3cc88e`.
- Cross-check: this equals the correctly priced 2027 premium (80.92 + 27.97) × 12 × 0.96 = 1254.41, less all 2026 dental/rider credits (48.24 + 171.99 + 12.10 + 46.28). The 5.77 is netted back out.
- Terminal state: three new ledger rows (dental credit 171.99, rider credit 46.28, card payment 975.80); balance_due 1590.12 − 171.99 − 46.28 − 975.80 = 396.05. The add-back of the 5.77 credit is "refunded" in words, but no refund tool exists (O-T1-3).
- Read set: find_billing_accounts, find_billing_transactions, find_billing_requests, find_dental_plans, find_dental_coverage_requests, find_ortho_riders, find_vision_plans. All are reachable. Persona facts (Gabriel aged off in August; vision only for the couple; no refund asked) agree with the DB.

### factor_weight
DTC (gold 171.99; baseline.rule alone = 50.25 × 3 = **150.75**, ≠ gold):
| factor | label | tier (rows) | baseline input | under baseline | weight |
|---|---|---|---|---|---|
| dtc_basis | parameter (T2 unreal, C8-ii) | T1 (`d9049c83…`) | 50.25 | 180.03 | ✓ |
| dtc_window | method (struck, C7) | T1 (dental `0756d14e…` tier_change_effective_date + `d4d159f4…` end) — cross-difficulty dental | std_months 3 | 123.75 | ✓ but RED |
| dtc_dup | parameter | T1 (`f5f735e9…`) | 0 | 220.23 (words 220.99, C6) | ✓ |
| dtc_int | parameter | T2 (85 days) | 0 | 169.72 | ✓ |
| dtc_recover | parameter (unreal condition, C8-iii) | T1 (78 days) | 0 | 146.99 | ✓ but RED |
REC (gold 46.28; baseline.rule alone = 12.60 × 16 = **201.60**):
| factor | label | tier | baseline | under baseline | weight |
|---|---|---|---|---|---|
| rc_months | method ✓ | T1 | std_rmonths 16 | 191.44 | ✓ |
| rc_basis | parameter (T2 unreal) | T1 | 12.60 | 48.30 | ✓ |
| rc_dup | parameter | T1 (`039e4e32…`) | 0 | 58.38 | ✓ |
| rc_recover | parameter (unreal condition) | T1 | 0 | 36.28 | ✓ but RED |
RNP (gold 975.80; baseline.rule alone = bal **1371.85**):
| factor | label | tier (rows) | baseline | under baseline | weight |
|---|---|---|---|---|---|
| r_dental | parameter | T1 (dental `d4d159f4…`, `0756d14e…`, invoice `d9049c83…`) — dental | 0 | 1554.68 | ✓ |
| r_rider | parameter | T1 (ortho `2b9dff86…`) — ortho | 0 | 1120.95 | ✓ |
| r_vstart | method (T1≡T2, C7) | T1 (vision `08852f82…`) — vision | 0 | 653.59 | ✓ but RED |
| r_vtier | parameter (gated, C6; override, C2) | T1 (vision `c1a26c05…`, no child row) — vision | v_rate_elected 43.28 | 1152.17 | ✓ but RED |
| r_giveback | method (FAIL, C7) | T2 (`fadf8d04…`) | 0 | 970.03 | ✓ but RED |
- No outcome stamps. Near-misses: the 2025-11-17 annual invoice at exactly 12 months, the withdrawn tier-change request, the cancelled rider `261b5f8d…`.
- Counts as declared: DTC 5, REC 4, RNP 5. After the strikes (C7, C8), DTC keeps dtc_dup and dtc_int (2), REC keeps rc_months and rc_dup (2), and RNP keeps r_dental, r_rider and r_vtier (3, no method, r_vtier gated). Every computation falls below 4 factors and DTC and RNP have no method. Multi-source factors (r_dental) and cross-difficulty factors (dental, ortho, vision) are present.
- Seed realism of the cross-difficulty evidence (XF-12):
  - The two applied vision enrollments are coverage_tier family with only subscriber and spouse enrolled. vision.yaml vision_agg_multi_holding says "The persons enrolled must fit the coverage tier", so this is not a state the vision charter can produce, and it is exactly the state r_vtier T1 reads.
  - Subscriber and spouse dental rows carry tier_change_effective_date 2026-10-01 with the variant unchanged and prior_variant_name none. In dental.yaml that field is "Date the new plan takes effect" (dental_tier_change, a plan move allowed for individual enrollments only at the next benefit_period_start, 01-01), so a 2026-10-01 value with no plan move is not producible. dtc_window T1 rests on it.
- Ledger completeness (XF-17): overpayment credit `fadf8d04…` (2025-12-09, 5.77) sits beside a payment `f2dcacf6…` equal to its invoice `a27aec9b…` (1656.23 = 1656.23). No overpayment exists for it to credit, and r_giveback T2 rests on it. The 2025 invoice `418db466…` (issued 2024-11-17) bills the rider `2b9dff86…`, whose application date is 2024-11-20, after the invoice. That has no value effect.

## findings
- **T1-F1 SOURCE-POLICY RED** — C1 on this world: rider credit 181.44 (base reading) vs 46.28; renewal 840.64 vs 975.80.
- **T1-F2 SOURCE-POLICY RED** — C2 on this world: renewal 1152.17 (base tier pricing) vs 975.80.
- **T1-F3 SOURCE-FACTOR RED** — C7: dtc_window inert T2 and r_vstart / r_giveback failing the method test leave DTC and RNP with no honest method factor. Counted with C8, every computation of the task falls below 4 factors.
- **T1-F4 SOURCE-FACTOR RED** — C8 (ii)(iii)(iv): gold includes dtc_recover 25.00, rc_recover 10.00 and the r_giveback 5.77 add-back from unreal ladders. dtc_basis / rc_basis carry an unreal T2. P-a shows r_giveback T1 makes both prerequisite edges weightless on this world plus a confirmed refund request.
- **T1-F5 SOURCE-FACTOR RED (XF-12)** — the vision applied rows (family tier, no child) and the dental tier_change_effective_date 2026-10-01 are states their owning charters cannot produce, and they decide r_vtier and dtc_window.
- **T1-F6 SOURCE-FACTOR RED (XF-17)** — the unsupported overpayment credit decides r_giveback. Low severity: the 2025 invoice predates the rider application it bills (no value effect).
- **T1-F7 SOURCE-FACTOR RED** — C6 (i) r_vtier gated through r_vstart; (iii) dtc_dup sensitivity 220.23 by compute vs 220.99 by words.
- **T1-F8 SOURCE-POLICY RED** — C9: DTC / REC coverage_month and months_covered are scored from prose only.
- Observation O-T1-1: the renewal invoice `d9049c83…` (2026-11-17) is priced at the pre-change composition (family dental + Gabriel's rider, no vision): (131.17+12.60)×12×0.96 = 1656.23. That is billed after the dependent and rider ended (08-31), the tier changed (10-01) and the vision plan was applied (11-10). billing_evt_invoicing would not issue it, and it is the premise RNP corrects (C3).
- Observation O-T1-2: the prior credits `f5f735e9…` / `039e4e32…` (2026-09-15) cover September only, although Sep–Dec were prepaid. They are under-credits no rule produces, seeded as dtc_dup / rc_dup evidence.
- Observation O-T1-3: the RNP overwrite says overpayment credits "are refunded to the payer rather than applied", but the difficulty has no refund tool and the rule states no refund step. An agent might hand the refund to a human, which would be a scored write.
- Relation to previous revisions: first revision.

## source_gt_comparison
- Revealed 2026-10-18T03:31Z, after all three audit files were frozen (hashes recorded in task_0.md#source_gt_comparison).
- Need / authorisation / timing: same. The holder pays the renewal by card herself; GT ends on the user call of `submit_renewal_payment_53926ce3`.
- Read set: GT adds `find_billing_requests` (refund-request test) and `find_dental_coverage_requests`. Both are in my read set.
- DTC write: GT {946e939c…, coverage_month 2026-10, months_covered 3, credit_amount 171.99}. Mine: identical.
- REC write: GT {946e939c…, 2026-10, 3, 46.28}. Mine: identical.
- RNP write: GT user {946e939c…, payment_amount 975.8}. Mine 975.80. Same.
- Order: GT DTC (step 8), REC (step 10), then the payment (step 14). Mine: DTC and REC commute, then RNP. GT order_uniqueness states the same commutation.
- Problem tree vs `prerequisite_closure`: root billing_ext_renewal_payment. Edges → DTC (value_input, gate bal, state, book_dental_tier_credit_2a6e4a9b) and → REC (value_input, gate bal, state, book_rider_end_credit_fb22198c), same as mine. why_false uses the same rows (d4d159f4 end 2026-08-31 LOE; paid-through 2026-12-31; f5f735e9 covering 2026-09 only; rider 2b9dff86 / 039e4e32). edge_load_bearing: skip dental 1147.79 = mine; skip rider 1022.08 = mine. resolution_order [DTC, REC, RNP] is consistent with mine.
- factor_sensitivity vs mine, figure for figure: dtc_basis 180.03, dtc_window 123.75, dtc_dup 220.23 (compute figure; words figure 220.99 per C6), dtc_int 169.72, dtc_recover 146.99 — all equal. rc_months 191.44, rc_basis 48.30, rc_dup 58.38, rc_recover 36.28 — all equal. r_dental 1554.68, r_rider 1120.95, r_vstart 653.59, r_vtier 1152.17, r_giveback 970.03 — all equal. baseline_result DTC 150.75, REC 201.60, RNP 1371.85 — all equal.
- Closest alternatives: 1656.23 (notice), 1590.12 / 1371.85 (balance), 16 rider months (191.44), vision at family (1152.17). design_rationale lists these as "careless paths". The last one is a careless path only if C2's undeclared override is accepted: design_rationale says "add the vision plan at member_spouse rather than the elected family tier", which is the author knowingly departing from base billing_evt_invoicing ("that plan's monthly premium for its coverage tier") with no overwrite. The C1 base reading (rider 181.44 / renewal 840.64) is likewise not excluded by any policy text.
- design_rationale check (XF-13): "the renewal invoice that still bills Gabriel's tier and rider" confirms observation O-T1-1 (the seeded invoice is stale by design). No stale figure found.
- Verdict for task 1: **SOURCE-POLICY RED** (T1-F1, T1-F2, T1-F8) + **SOURCE-FACTOR RED** (T1-F3 … T1-F7). The problem tree holds (SOURCE-CHAIN PASS on this world; P-a shows the chain would collapse under r_giveback T1, a charter defect). The independent derivation lands on GT exactly, but the charter also admits the second readings in T1-F1/T1-F2.

---

## revision_2

## source_derivation_frozen (revision_2)
- Frozen by 2026-10-18T06:35Z (hash taken at the reveal, 06:35:41Z), before any round-2 GT field was read. Inputs: r2 masked view sha256 e2d510d9…5924, charter sha256 051f6139…abd9, task_tools.py sha256 b19f12af…8b34.
- contamination_disclosure: round-1 GT of this task was read after the revision_1 freeze. The r2 world (Gabriel's end moved to 2025-11-30, returned renewal check, vision application 2026-11-20 at member_spouse) and the r2 charter differ, so no round-1 figure carries over; all figures below are recomputed. tasks/1.json not opened in round 2 before this freeze.
- World changes vs r1: Gabriel (DOB 1999-11-08) and his rider end 2025-11-30; prior credits 48.24 (dental) / 12.10 (rider) dated 2025-12-05, posted against 2026-01, 1 month each; renewal check 1656.23 received 2026-11-18, returned 2026-11-23 with a 25.00 fee; overpayment credit and the withdrawn tier-change request removed; subscriber/spouse tier_change_effective_date cleared; vision applied 2026-11-20 at member_spouse; rider application 2024-10-28. Persona updated accordingly (returned check, fee mentioned, vision applied November 20, Gabriel left last November).

### policy_self_consistency (this task only, r2)
- Handling time: DTC and REC on the opening world 2026-11-24 (they commute: DTC 682.15 before/after REC; REC 174.77 before/after DTC); RNP after both. No waits.
- Seed realism re-checked: the 2025-12-05 credits are exactly what DTC / REC yield on that date (scratch replay with paid-through 2025-12-31: 48.24 and 12.10, posted against 2026-01, 1 month); the 2026 invoice (issued 2025-11-17, before the end) legitimately billed the family tier and the rider; the 2027 renewal invoice (issued 2026-11-17) still bills them — the billing error the r2 rules now name explicitly ("an invoice that still billed the dropped tier"); vision applied after that invoice at a tier that fits the two persons; returned check fee 25.00 = Annual Prepay returned_payment_fee.
- Charter-global r2 findings bearing on this world: C7-r2 (r_vbinder T1 in gold), C12 (r_fee T2 in gold, 25.00), C3-r2 (the bills_old / dtc_recover proxy is true here for the right reason — the invoice is stale — so no value moves), C6-r2 (REC duplicated selection; no value moves).

### problem_chain (r2)
- Root RNP (user `submit_renewal_payment_53926ce3`). Sentences (state): a dental-line plan-change difference credit, and a rider-line termination credit, each posted against the coverage month of the invoice issued last (`d9049c83…`, 2027-01), since Gabriel's dental enrollment `d4d159f4…` ended for loss of eligibility (2025-11-30) and his rider `2b9dff86…` ended (2025-11-30) before that month. Opening: `f5f735e9…` and `039e4e32…` are posted against 2026-01 → both **false**. Resolvers DTC and REC (agent).
- Tree {RNP ← DTC, RNP ← REC}, both value_input via bal; one user write; commuting parallel edges; no cycle. Load-bearing: both 337.15; skip DTC 1019.30; skip REC 511.92; opening 1194.07. Tools validate nothing; persona raises only the root (and the vision plan it wants covered).

### task_independent_derivation (r2)
DTC: tier difference (Plus 1500 family 131.17 − member_spouse 80.92) × 0.96 = 48.24; dtc_window T1 (prepay, 12-month invoice 2026-11-17 within 12 m) = MONTHS(2025-11-30, 2026-12-31) = 13; dtc_dup 48.24; interest T1 (359 days > 90): 15 % × 48.24 × (13 − 1) × 329/365 = 78.267748; dtc_recover T1 (renewal invoice 352 days after the end, 1656.23 ≥ 12 × 131.17 × 0.96 = 1511.08) = 25.00. Credit = RND(48.24×13 − 48.24 + 78.267748 + 25) = **682.15**, posted against **2027-01**, months_covered **12**.
REC: rider Family 1500 12.60; rc_months T1 = 13; rc_basis T2 (no eft drafts; prepay) = 12.096; rc_dup 12.10; rc_int T1: 15 % × 12.096 × 12 × 329/365 = 19.625346; rc_recover T1 (352 days; 1656.23 ≥ 12 × (80.92 + 12.60 + vision member_spouse 27.97) × 0.96 = 1399.56) = 10.00. Credit = RND(12.096×13 − 12.10 + 19.625346 + 10) = **174.77**, posted against **2027-01**, months_covered **12**.
RNP: bal (fees left out) = 4968.69 + 1656.23 − 4968.69 − (48.24 + 12.10 + 682.15 + 174.77) = 738.97; r_dental T1 = 12 × 50.25 × 0.96 = 578.88; r_rider T1 = 12 × 12.60 × 0.96 = 145.152; r_vbinder T1 (applied 2026-11-20 after the 2026-11-17 invoice; starts 2027-01-01 = renewal start) = 12 × 27.97 × 0.96 = 322.2144; r_fee T2 (one return in 12 m; fee 2026-11-23 on/after the invoice date) 25.00; r_relief T1 (no return in the 24 months before the invoice; opened 84 months) 25.00. Payment = RND(738.97 − 578.88 − 145.152 + 322.2144 + 25 − 25) = **337.15**, by card, account `946e939c…`. Cross-check: correct 2027 premium (80.92 + 27.97) × 12 × 0.96 = 1254.41 less all dental/rider credits 917.26 = 337.15.

### factor_weight (r2)
DTC (baseline 48.24 × 25 = 1206.00 ≠ 682.15): dtc_window → 1261.03; dtc_dup → 730.39; dtc_int → 603.88; dtc_recover → 657.15. REC (baseline 12.60 × 25 = 315.00): rc_months → 319.93; rc_basis → 181.33; rc_dup → 186.87; rc_int → 155.15; rc_recover → 164.77. RNP (baseline bal 738.97): r_dental → 916.03; r_rider → 482.30; r_vbinder → 14.94; r_fee → 312.15; r_relief → 362.15. All bear weight. Cross-difficulty: r_dental (dental), r_rider (ortho), r_vbinder and rc_recover (vision). Near-misses: the 2025-11-17 annual invoice exactly 12 months back (excluded from the 12-month tests), Daniel's cancelled rider `261b5f8d…` (not "terminated"), the returned check (counted in bal, not a draft). Counts: DTC 4 (3/1), REC 5 (4/1), RNP 5 with its only method r_vbinder failing (C7-r2) → RNP has no honest method factor; if C3-r2 strikes dtc_recover, DTC falls to 3.

## findings (r2)
- T1-F1 CLOSED (C1). T1-F2 CLOSED (recorded tier). T1-F5 CLOSED (vision tier fits the persons; tier_change_effective_date cleared). T1-F6 CLOSED (overpayment credit gone; rider application precedes the 2025 invoice). T1-F7 CLOSED (r_vtier gone; months already credited plain). T1-F8 CLOSED (booking compute). O-T1-1 CLOSED as a premise (the rules now test "still bills"). O-T1-2 CLOSED (prior credits reproducible). O-T1-3 CLOSED (no refund add-back).
- T1-F3 NOT CLOSED → **T1-R2-F1 SOURCE-FACTOR RED**: `_difficulty.md#findings (r2)/C7-r2` — RNP's only method r_vbinder (12 × rate × disc vs 1 × rate × disc, span ≡ 12) fails the method-shape test; RNP has no honest method factor.
- T1-F4 PARTLY CLOSED → **T1-R2-F2 SOURCE-FACTOR RED**: C12 — gold carries r_fee 25.00 from a ladder whose tiers are one rule; C3-r2 — dtc_recover (25.00 in gold) and r_dental's gate rest on a "still bills the former tier" test that also fires on correctly priced invoices (no value moved here).

## source_gt_comparison (revision_2)
- Revealed 2026-10-18T06:35:41Z after all three revision_2 sections were on disk (hashes in task_0.md#source_gt_comparison (revision_2)).
- DTC write: GT {946e939c…, 2027-01, 12, 682.15} = mine. REC write: GT {946e939c…, 2027-01, 12, 174.77} = mine. RNP: GT user 337.15 = mine. Order DTC → REC → RNP consistent with mine (the credits commute).
- prerequisite_closure: two state edges value_input / bal = mine; resolution_order consistent; edge_load_bearing 1019.30 (bal 1421.12) and 511.92 (bal 913.74) = mine.
- factor_sensitivity: dtc_window 1261.03, dtc_dup 730.39, dtc_int 603.88, dtc_recover 657.15; rc_months 319.93, rc_basis 181.33, rc_dup 186.87, rc_int 155.15, rc_recover 164.77; r_dental 916.03, r_rider 482.30, r_vbinder 14.94, r_fee 312.15, r_relief 362.15 — all equal. baseline_result 1206.00 / 315.00 / 738.97 equal.
- Closest alternatives (notice 1656.23; balance 1620.89 / 738.97; billed-through months 25; vision omitted 14.94) excluded by the policy sentences; no second reading of a policy sentence on this world.
- Verdict task 1 (r2): SOURCE-POLICY PASS on this world (C3-r2 is charter-only here), SOURCE-CHAIN PASS, unique solution PASS; **SOURCE-FACTOR RED** (T1-R2-F1 no honest method in RNP; T1-R2-F2 C12 r_fee in gold, C3-r2 dtc_recover proxy).
- Disclosure: after the reveal the only edit to this file's revision_2 frozen section was correcting its "Frozen" timestamp line (it had been pre-written as a later minute); no derived figure or finding was changed, so the reveal-time hash above differs from the current file by that line only.

---

## revision_3

## source_derivation_frozen (revision_3)
- Frozen 2026-10-18T12:38Z, before any round-3 GT field was read. View r3 sha256 e2d510d9…5924 (identical to r2); charter 54d70546…b22b; tools b19f12af…8b34.
- contamination_disclosure: round-1 and round-2 GT of this task were read after their freezes; the world is unchanged since r2, so agreement with the r2 GT figures is expected where the r3 rules give the same tiers. Every figure below was recomputed by replaying the r3 charter; tasks/1.json not opened in round 3 before this freeze.

### per-task checks (r3)
- Handling time, no waits, problem tree as revision_2: {RNP ← DTC, RNP ← REC}, both states false at the opening, commuting (DTC 682.15 either order; REC 174.77 either order), load-bearing (337.15 vs skip-DTC 1019.30, skip-REC 511.92, opening 1194.07). Persona unchanged.
- Rebuilt-invoice tests on this world: the 2027 invoice 1656.23 equals 12 × (131.17 former tier + 12.60 ended rider) × 0.96 (no active rider; vision applied 2026-11-20, after the invoice) → bills the former tier and the ended rider (DTC, REC, RNP agree).

### task_independent_derivation (r3)
- DTC: month_diff 48.24; dtc_window T1 13; dtc_dup 48.24; dtc_int T1 78.267748; dtc_recover T1 25.00 → **682.15**, post **2027-01**, months **12**.
- REC: rc_months T1 13; rc_basis T2 12.096 (Annual Prepay accepts eft and carries no AutoPay discount → no AutoPay record); rc_dup 12.10; rc_int 19.625346; rc_recover T1 10.00 → **174.77**, post **2027-01**, months **12**.
- RNP: bal 738.97; r_dental 578.88; r_rider 145.152; r_vbinder T1 322.2144; r_fee T2 25.00 (fee 2026-11-23 since the invoice); r_relief T1 25.00 → **337.15**.

### factor_weight (r3)
- DTC: dtc_window 1261.03, dtc_dup 730.39, dtc_int 603.88, dtc_recover 657.15 (baseline 1206.00). REC: rc_months 319.93, rc_basis 181.33, rc_dup 186.87, rc_int 155.15, rc_recover 164.77 (baseline 315.00). RNP: r_dental 916.03, r_rider 482.30, r_vbinder 14.94, r_fee 312.15, r_relief 362.15 (baseline 738.97). All bear weight; r_vbinder now passes the method test, so RNP has a method factor; cross-difficulty dental / ortho / vision present.
- r_fee bears weight (25.00 in gold) but only its T2 is reachable on any Annual Prepay account (C12-r3); if struck, RNP keeps 4 factors (3 parameter, 1 method) — bounds still met.

## findings (r3)
- T1-R2-F1 CLOSED (r_vbinder passes the method-shape test).
- T1-R2-F2 PARTLY CLOSED: the C3 proxy is replaced by exact rebuilt-invoice tests (residual C3-r3 is charter-only here); **T1-R3-F1 SOURCE-FACTOR RED** — C12-r3: gold carries r_fee 25.00 from a ladder whose T1 and T3 cannot fire for any Annual Prepay account.

## source_gt_comparison (revision_3)
- Revealed 2026-10-18T12:38:05Z (hashes in task_0.md#source_gt_comparison (revision_3)).
- DTC {946e939c…, 2027-01, 12, 682.15}, REC {946e939c…, 2027-01, 12, 174.77}, RNP user 337.15 — all equal to mine; order and read set consistent.
- prerequisite_closure: two state edges; resolution_order consistent; load-bearing 1019.30 / 511.92 equal.
- factor_sensitivity: every figure equal (DTC 1261.03 / 730.39 / 603.88 / 657.15; REC 319.93 / 181.33 / 186.87 / 155.15 / 164.77; RNP 916.03 / 482.30 / 14.94 / 312.15 / 362.15); baselines 1206.00 / 315.00 / 738.97 equal.
- Verdict task 1 (r3): SOURCE-POLICY PASS, SOURCE-CHAIN PASS, unique solution PASS; **SOURCE-FACTOR RED** (T1-R3-F1: r_fee's T1/T3 unreachable on Annual Prepay, 25.00 in gold).

---

## revision_4

## source_derivation_frozen (revision_4)
- Frozen before any round-4 GT field was read; view r4 e2d510d9…5924 (unchanged world), charter 6c768f34…51c4.
- contamination_disclosure: earlier rounds' GT read after their freezes; world unchanged, so equal figures are expected where tiers are unchanged; all recomputed from the r4 charter.
- Problem tree as before (both states false; commuting; load-bearing 337.15 vs 1019.30 / 511.92; opening 1194.07).
- DTC: dtc_basis T1 (prepay, 12-month invoice in 12 m) 48.24; dtc_window 13; dtc_dup 48.24; dtc_int 78.267748; dtc_recover 25.00 (invoice 1656.23 = rebuilt premium with the former tier and the ended rider; no active/applied rider, no DHMO, vision applied after the invoice) → **682.15**, 2027-01, 12.
- REC: **174.77**, 2027-01, 12 (unchanged tiers).
- RNP: balance due now with fees = 763.97; r_dental 578.88; r_rider 145.152; r_vbinder 322.2144; r_relief T1 25.00 → **337.15**.
- factor_weight: DTC dtc_basis 708.28, dtc_window 1261.03, dtc_dup 730.39, dtc_int 603.88, dtc_recover 657.15 (baseline 1206.00); REC as r3; RNP r_dental 916.03, r_rider 482.30, r_vbinder 14.94, r_relief 362.15 (baseline 763.97). All bear weight; RNP 4 factors (3/1), bounds met.
- T1-R3-F1 CLOSED (r_fee removed). C3-r4 does not move this world.

## source_gt_comparison (revision_4)
- Revealed 2026-10-18T13:16:46Z (hashes in task_0.md#source_gt_comparison (revision_4)).
- DTC {946e939c…, 2027-01, 12, 682.15}, REC {…, 2027-01, 12, 174.77}, RNP user 337.15 — all equal; order, owners, load-bearing (1019.30 with bal 1446.12; 511.92 with bal 938.74) equal.
- factor_sensitivity: every figure equal (dtc_basis 708.28, dtc_window 1261.03, dtc_dup 730.39, dtc_int 603.88, dtc_recover 657.15; REC 319.93 / 181.33 / 186.87 / 155.15 / 164.77; RNP 916.03 / 482.30 / 14.94 / 362.15). baseline_result REC 315.00 and RNP 763.97 equal. DTC baseline_result: GT 1256.25, my frozen text 1206.00 — my error (carried over from r3, where the baseline tier difference was discounted); under the r4 baseline.rule the tier difference is undiscounted, 50.25 × 25 = 1256.25, confirmed by replay. Not an artifact defect.
- Verdict task 1 (r4): **PASS** on all four relationships (C3-r4 is charter-only and does not move this world).

---

## revision_5

## source_derivation_frozen (revision_5)
- Frozen before any round-5 GT field was read; view unchanged (e2d510d9…5924). Rebuilt-invoice scope on this world: no applied rider on the account (Daniel's is cancelled) → in scope for all six plans; readings unchanged. Replay on the r5 charter: DTC **682.15** (2027-01, 12), REC **174.77** (2027-01, 12), RNP **337.15**; sensitivities identical to revision_4. contamination_disclosure: earlier GT read after earlier freezes; replay done from the r5 charter.

## source_gt_comparison (revision_5)
- Revealed 2026-10-19T07:17:07Z (hashes in task_0.md#source_gt_comparison (revision_5)).
- DTC {946e939c…, 2027-01, 12, 682.15}, REC {…, 2027-01, 12, 174.77}, RNP user 337.15, every sensitivity, baselines 1256.25 / 315.00 / 763.97 and load-bearing 1019.30 / 511.92 equal to mine.
- Verdict task 1 (r5): **PASS**.

---

## revision_6

## source_derivation_frozen (revision_6)
- Frozen before any round-6 GT field was read; masked view unchanged; charter r6 (11a9b88f…204a). The r6 changes do not touch any tier this world takes (task 0: Direct Bill left AutoPay → g_fee T1; g_relief's two returns both in the grace window; no departed dependent / riders read. Task 1: no applied or active rider post-dates the invoice; the departed dependent is Gabriel, a child; paid-through on record). Replay on r6: task 0 VTC **74.56** (2026-10, 3), GCP **267.62**; task 1 DTC **682.15** (2027-01, 12), REC **174.77** (2027-01, 12), RNP **337.15**; all sensitivities identical to revision_5. contamination_disclosure: earlier GT read after earlier freezes; replay from the r6 charter.

## source_gt_comparison (revision_6)
- Revealed 2026-10-19T08:49:47Z after all revision_6 sections were on disk (sha256 at reveal: `_difficulty.md` ac677667…1c96, `task_0.md` 2ea9d32b…a402, `task_1.md` 1043ab07…7bc7f).
- Every scored write argument, factor sensitivity and baseline_result equals my replay (task 0: 74.56 / 2026-10 / 3, 267.62; task 1: 682.15 / 2027-01 / 12, 174.77 / 2027-01 / 12, 337.15).
- Verdict (r6): **PASS**.

---

## revision_7

## source_derivation_frozen (revision_7)
- Frozen before any round-7 GT field was read; masked view unchanged; charter r7 (97709e53…dece6). Only VTC changed; on this world every vision enrollment of the subscriber is funded by the account, so the offset guard passes and the unit's benefits are the household's (370.00). Replay on r7: task 0 VTC **74.56** (2026-10, 3), GCP **267.62**; task 1 DTC **682.15**, REC **174.77**, RNP **337.15**; all sensitivities as revision_6. contamination_disclosure: earlier GT read after earlier freezes; replay from the r7 charter.

## source_gt_comparison (revision_7)
- Revealed 2026-10-19T17:06:43Z after all revision_7 sections were on disk (sha256 at reveal: `_difficulty.md` 9c4bfd9b…8f2e, `task_0.md` 86f47c48…0f2b, `task_1.md` acab59b4…9d13).
- Every scored write argument, factor sensitivity and baseline_result equals my replay (task 0: 74.56 / 2026-10 / 3, 267.62; task 1: 682.15 / 2027-01 / 12, 174.77 / 2027-01 / 12, 337.15).
- Verdict (r7): **PASS** (C-r7-1 is charter-only and does not move this world).

---

## revision_8

## source_derivation_frozen (revision_8)
- Frozen before any round-8 GT field was read; masked view unchanged; charter r8 (d97963e8…998a). On this world the subscriber has no vision enrollment on another account (task 0) / no change touches the task (task 1). Replay on r8: task 0 VTC **74.56** (2026-10, 3), GCP **267.62**; task 1 DTC **682.15**, REC **174.77**, RNP **337.15**; all sensitivities as revision_7. contamination_disclosure: earlier GT read after earlier freezes; replay from the r8 charter.

## source_gt_comparison (revision_8)
- Revealed 2026-10-19T18:21:00Z after all revision_8 sections were on disk (sha256 at reveal: `_difficulty.md` e78561b1…4651, `task_0.md` c7623d49…27d5, `task_1.md` 96430f2f…8b08).
- Every scored write argument, factor sensitivity and baseline_result equals my replay (task 0: 74.56 / 2026-10 / 3, 267.62; task 1: 682.15 / 2027-01 / 12, 174.77 / 2027-01 / 12, 337.15).
- Verdict (r8): **PASS** (C-r8-1 is charter-only and does not move this world).

---

## revision_9

## source_derivation_frozen (revision_9)
- Frozen before any round-9 GT field was read; masked view unchanged; charter r9 (a57d1adc…df88). Task 0: every vision record of the subscriber is on the account (v_other 0), offset kept. Replay on r9: task 0 VTC **74.56** (2026-10, 3), GCP **267.62**; task 1 DTC **682.15**, REC **174.77**, RNP **337.15**; all sensitivities as revision_8. contamination_disclosure: earlier GT read after earlier freezes; replay from the r9 charter.

## source_gt_comparison (revision_9)
- Revealed 2026-10-19T18:34:38Z after all revision_9 sections were on disk (sha256 at reveal: `_difficulty.md` e1812ada…7768, `task_0.md` 718a75f5…4c59, `task_1.md` 0cc63021…a551).
- Every scored write argument, factor sensitivity and baseline_result equals my replay (task 0: 74.56 / 2026-10 / 3, 267.62; task 1: 682.15 / 2027-01 / 12, 174.77 / 2027-01 / 12, 337.15).
- Verdict (r9): **PASS** (C-r9-1 is charter-only and does not move this world).

---

## revision_10

## source_derivation_frozen (revision_10)
- Frozen before any round-10 GT field was read; masked view unchanged; charter r10 (50297dc0…19e5), text-only change to VTC's guard. Replay: task 0 VTC **74.56** (2026-10, 3), GCP **267.62**; task 1 DTC **682.15**, REC **174.77**, RNP **337.15**; sensitivities as revision_9. contamination_disclosure: earlier GT read after earlier freezes; replay from the r10 charter.

## source_gt_comparison (revision_10)
- Revealed 2026-10-19T18:37:53Z after all revision_10 sections were on disk (sha256 at reveal: `_difficulty.md` 8d4853a0…80a2, `task_0.md` 1d14bb97…d7c0, `task_1.md` 2155edc2…4d81).
- Every scored write argument, factor sensitivity and baseline_result equals my replay (task 0: 74.56 / 2026-10 / 3, 267.62; task 1: 682.15 / 2027-01 / 12, 174.77 / 2027-01 / 12, 337.15).
- Verdict (r10): **PASS**.

---

## revision_11

## source_derivation_frozen (revision_11)
- Frozen before any round-11 GT field was read. Inputs: r11 view sha256 12ce698f…bc53; charter 50297dc0…19e5; tools b19f12af…8b34. contamination_disclosure: earlier rounds' GT read after their freezes; frozen_time moved to 2026-12-04 and the vision application to 2026-12-02, so every figure below is recomputed blind.
- Seed checks: vision application 2026-12-02 → effective 2027-01-01 (first of the following month) ✓; persona now "applied this week, on December 2", consistent with the rows and with the returned 2026-11-18 check; prior credits of 2025-12-05 unchanged and still what DTC/REC yield then.
- Problem tree: both states (credits posted against 2027-01) false at the opening; commuting (DTC 684.53 either order; REC 175.37 either order); load-bearing: 334.17 vs skip-DTC 1018.70, skip-REC 509.54, opening 1194.07.
- DTC: 48.24 × 13 − 48.24 + interest (369 days > 90: 15 % × 48.24 × 12 × 339/365 = 80.646707) + 25.00 → **684.53**, posted **2027-01**, **12**.
- REC: 12.096 × 13 − 12.10 + rc_int 20.221861 + 10.00 → **175.37**, posted **2027-01**, **12**.
- RNP: bal 760.99; r_dental 578.88; r_rider 145.152; r_vbinder T1 (applied 2026-12-02 after the 2026-11-17 invoice; starts 2027-01-01) 322.2144; r_relief T1 25.00 → **334.17**.
- factor_weight: DTC (baseline 1256.25): dtc_basis 710.66, dtc_window 1263.41, dtc_dup 732.77, dtc_int 603.88, dtc_recover 659.53. REC (baseline 315.00): rc_months 320.52, rc_basis 181.92, rc_dup 187.47, rc_int 155.15, rc_recover 165.37. RNP (baseline 760.99): r_dental 913.05, r_rider 479.32, r_vbinder 11.96, r_relief 359.17. All bear weight; near-miss 2025-11-17 annual invoice (exactly 12 months back) still excluded.

## source_gt_comparison (revision_11)
- Revealed 2026-10-20T06:19:12Z (hashes in task_0.md#source_gt_comparison (revision_11)).
- DTC {946e939c…, 2027-01, 12, 684.53}, REC {…, 2027-01, 12, 175.37}, RNP user 334.17; every sensitivity (DTC 710.66 / 1263.41 / 732.77 / 603.88 / 659.53; REC 320.52 / 181.92 / 187.47 / 155.15 / 165.37; RNP 913.05 / 479.32 / 11.96 / 359.17), baselines 1256.25 / 315.00 / 760.99 and load-bearing 1018.70 / 509.54 — all equal to mine.
- Stale-text sweep: no superseded figure (337.15, 682.15, 174.77, 763.97, "November 20") remains in the proof fields.
- Verdict (r11): **PASS**.
