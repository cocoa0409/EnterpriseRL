# Policy-task audit — premium_billing_and_grace / task 0

## revision_1

## source_derivation_frozen
- Frozen 2026-10-18T03:35Z by the independent policy auditor, before any GT field of either task was read. Inputs: masked view `.audit_views/policy/premium_billing_and_grace/r1/task_0.json` (sha256 a15744447e91953ffd995dbfed1f9db7278d4801d1c40d332edee968e26885c5), charter sha256 24a5e811…fbdc, task_tools.py sha256 87aa55fb…107f. Masked fields not read: evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*.
- contamination_disclosure: none. tasks/0.json, plan.md and worklog.md were not opened and no grep ran over tasks/.
- Charter-global conclusions are cited from `audits/policy_task/premium_billing_and_grace/_difficulty.md` (cited as `_difficulty.md#<heading>/<finding>`). They are not restated here.

### policy_self_consistency (this task only)
- Handling time: VTC is evaluated on the opening world at 2026-09-22. GCP is evaluated after the VTC credit row exists (dated 2026-09-22, product_line vision). Of GCP's reads, only `cred_all` sees that row, so no later write is computed early.
- Real-world waits: none. Every fact consumed is either a seeded row or the VTC credit booked earlier in the same call. The $20 bank transfer of 2026-09-16 is held under g_hold, but the gold path adds it back instead of waiting for it to clear, so no wait is required. The grace period ends 2026-10-02 (due date 2026-09-01 + 31 days), so the payment is in time.
- Charter-global findings that bear on this task, with consequences on this world:
  - `_difficulty.md#findings/C1` (sibling overwrites). VTC's own replaced_by sends every other termination credit to the base rule, and REC's replaced_by says the vision-unit credit "remains under the base rule". A reader who follows REC's sentence books the vision credit under base termination_unearned: premium billed for the whole months after June. July is already credited (the base distinguish_by key product_line+credit_reason+coverage_month blocks a second 2026-07 credit), so the reader books Aug–Oct at the 36.28 vision premium = **108.84**, against the VTC reading of **57.11**. The grace-cure payment then becomes **180.39** instead of **232.12**. Two defensible answers.
  - `_difficulty.md#findings/C4` (held transfer). Under base payment application the booked $20 grace-cure transfer is applied like any received payment, so held_amt = 0 and the payment is **212.12**. Under GCP g_hold it is **232.12**.
  - `_difficulty.md#findings/C6`(ii). Substituting vtc_prior's baseline (0) in the compute gives 93.06. Read by the rule's words, "the termination credits … already deducted above" are then none, so the interest base runs over 2 paid months (int 1.07) and the credit is 93.60; the booking args become 2026-07 / 4 months. The sensitivity of vtc_prior has no single value.
  - `_difficulty.md#findings/C9` (booking args have no compute): this task's scored `coverage_month` / `months_covered` for the VTC credit rest only on the prose sentence "whose first coverage month is the first month billed after the termination month that no termination credit already deducted above covers".
  - C2, C3, C5, C7 (g_next part), C10 and C11 move no value on this world. g_next takes tier 1 on an AutoPay account, where T1 and T2 differ by $1.00. The P-d decoy (C10-i) is absent here.

### problem_chain
- Root: the customer asks to pay by card today, herself, whatever brings the account out of grace (persona lines "you want to pay, today, by card, whatever Cascade needs from you to bring the account out of the grace period" / "You want to make that card payment yourself"). Policy: GCP (individual-market AutoPay account `33e3ddd3…`, status grace_period, in-person payment). Owner user: `submit_grace_cure_payment_5521c4c8`.
- GCP rule's prerequisite sentence (state form): the ledger must carry vision-line termination credits covering every month billed after the termination month of each voluntarily terminated subscriber vision unit.
- Opening world: subscriber vision enrollment `e7c24dcd…` (Select 130, family, voluntary, termination 2026-06-30). Months billed after June run through the coverage month of the invoice issued last (`b2dc4f8e…`, 2026-09-11, coverage 2026-10): Jul, Aug, Sep, Oct. The only vision credit is `0e1bc999…` (2026-07-24, coverage 2026-07, 1 month, 35.95), so Aug–Oct are uncovered and the state is **false at the opening**. The resolving policy is the one whose rule books termination credits on the vision line: VTC → `book_vision_term_credit_956578a0` (owner agent).
- VTC has `prerequisite: []`. Tree: {GCP ← VTC}, one prerequisite problem, edge kind value_input (the credit enters `cred_all` in `past_due`). max(n−1,1)=1 is satisfied. One owner=user write (the root). No cycle. Topological order: VTC credit, then GCP payment.
- Load-bearing check: skip the VTC write and GCP evaluates to **289.23**; with it, **232.12**.
- Tools: both bodies only create a ledger row and lower balance_due. Neither checks status, grace or the existence of the credit (task_tools.py lines 105–123, 142–159).
- Persona raises only the root. It mentions the vision plan only if the representative brings it up, and agrees to a correction only if the representative explains one is needed. It names no prerequisite and closes at the card confirmation.

### task_independent_derivation
Act now (grace not ended; individual account; customer authorises a card payment and executes it herself).

**Step 1 — VTC credit (agent), handling time = opening world, 2026-09-22.**
- Unit: `e7c24dcd…`. The only subscriber + voluntary row (decoy `555f3204…` is subscriber but application_withdrawn). Filed premium Select 130 family = 36.28. vt_billed = 4 (Jul–Oct). Tenure = MONTHS(2025-11-01, 2026-06-30)+1 = 8.
- vtc_month (AutoPay, `autopay_discount_monthly`=1.00, regular eft drafts within 12 m exist, e.g. `ad96fde7…` 2026-08-01): 36.28 − 1.00/plan_units. plan_units = 2 + 1 active rider (`99429870…`; `1da95e2f…` is cancelled) = 3, so 35.946667.
- vtc_offset T1 (8 months, 1–12): benefits on services from the effective month on = PAID 60+60+51.5+130+60+60 − reversal `d1d0a7f5…` 60 = 361.50. This exceeds 36.28×8 = 290.24, so the offset is **71.26**. Near-miss: the reversed original `2bb98ca4…` still carries remark PAID and is cancelled out only by the reversal sentence.
- vtc_prior T1: credits booked no more whole months before the credit date than the termination date (since_term 3): `0e1bc999…` (MONTHS 1), so **35.95**. prior_months 1.
- vtc_int: days 2026-06-30 → 2026-09-22 = 84, which falls in (30, 90], so 10 %. Base = 36.28 × (MONTHS(06-30, paid-through 08-31)=2 − 1) × (84−30)/365 = 5.367452, giving interest **0.536745**.
- vtc_recover: confirmed voluntary-termination request `9d9f298d…` created 2026-06-08, lead 22 days ≥ invoice_lead_days 20, and 4 ≥ 3 months billed, so **20.00**. Near-miss: application_withdrawal request `595dd7a2…` (confirmed) is excluded by type.
- credit_core = MX(0, 35.946667×4 − 71.26 − 35.95) = 36.576667. **credit_amount = 57.11**, coverage_month **2026-08**, months_covered **3**, billing_account_id `33e3ddd3-a93e-4cdd-8d41-16e36afb4d64`.

**Step 2 — GCP payment (user), handling time = after step 1.**
- past_due: invoices 2356.32 + returned 156.34 − payments 2219.98 − credits (35.95+57.11) − future invoice 156.34 (coverage 2026-10 not begun) = **43.28**.
- g_next T1: eft return `eddfa9ef…` on 2026-09-11 is on/after grace start 2026-09-01 and the last invoice is for a future month, so add 156.34.
- g_disc T2: AutoPay discount 1.00 and grace-cure payment `12ce7f58…` 2026-09-16 on/after grace start, so 1.00. T1 is not taken: only 1 eft return in 12 m.
- g_fee T2: exactly 1 return in 12 m, so the last fee `2b8031f1…` = 25.00.
- g_relief T2: opened 2022-06-14, giving 51 whole months (36–59); 1 return in 24 m; fee dated 2026-09-11 is on/after grace start. Relief = 50 % × 25.00 = 12.50.
- g_hold T1: eft return 11 days before ≤ 60, so the hold is 10 days. Latest grace-cure eft transfer `12ce7f58…` is 6 days old (< 10), so held 20.00.
- g_tol T2: subscriber active dental `523d3eea…` effective 2022-07-01, giving 50 months (36–59), so 1.00.
- result = RND(MX(0, 43.28 + 156.34 + 1.00 + 25.00 + 20.00 − 12.50 − 1.00)) = **232.12**, owner user, by card, billing_account_id `33e3ddd3-a93e-4cdd-8d41-16e36afb4d64`. Opening-world contrast (no VTC credit): **289.23**.
- Terminal state: two new ledger rows (vision credit 57.11; card grace-cure payment 232.12), balance_due 281.73 − 57.11 − 232.12 = −7.50. Grace → active is the base system transition, not a scored write.
- Read set: find_customers / verify identity, find_billing_accounts, find_billing_transactions, find_vision_plans, find_vision_claims, find_vision_coverage_requests, find_ortho_riders, find_dental_plans. All are reachable by customer_id / billing_account_id. Persona facts (the $20 transfer on 09-16, the vision plan cancelled in June) agree with the DB.

### factor_weight
VTC (gold 57.11; baseline.rule alone = 36.28 × 4 = **145.12**, definite and ≠ gold):
| factor | label honest | tier taken (rows) | baseline input | value under baseline | weight |
|---|---|---|---|---|---|
| vtc_month | parameter ✓ | T1 AutoPay (variant param + eft drafts) | 36.28 (= baseline.rule's filed premium) | 58.45 | ✓ |
| vtc_offset | method ✓ | T1 (vision_plans e7c24dcd dates + 7 vision_claims) — cross-difficulty vision | 0 (baseline has no offset) | 128.37 | ✓ |
| vtc_prior | parameter ✓ | T1 (`0e1bc999…`) | 0 | 93.06 (words-reading 93.60, C6) | ✓ |
| vtc_int | parameter ✓ | T2 (84 days) | 0 | 56.58 | ✓ |
| vtc_recover | parameter ✓ | T1 (vision request `9d9f298d…` + 4 billed months) — cross-difficulty vision | 0 | 37.11 | ✓ |
GCP (gold 232.12; baseline.rule alone = past_due = **43.28**, definite and ≠ gold):
| factor | label | tier taken (rows) | baseline | value under baseline | weight |
|---|---|---|---|---|---|
| g_next | method (passes on AutoPay only, C7) | T1 (`eddfa9ef…`, `b2dc4f8e…`) | 0 | 75.78 | ✓ |
| g_disc | parameter ✓ | T2 (`12ce7f58…`) | 0 | 231.12 | ✓ |
| g_fee | parameter ✓ | T2 (`2b8031f1…`) | 0 | 207.12 | ✓ |
| g_relief | parameter ✓ | T2 (opened_date, 1 return/24 m, fee date) | 0 | 244.62 | ✓ |
| g_hold | parameter ✓ | T1 (`eddfa9ef…`, `12ce7f58…`) | 0 | 212.12 | ✓ |
| g_tol | parameter (unreal ladder, C8-i) | T2 (dental `523d3eea…`) — cross-difficulty dental | 0 | 233.12 | ✓ but RED |
- No stamp field names any tier outcome; every tier rests on aggregates or dates.
- Near-miss per computation: VTC has the withdrawn vision application `555f3204…`, the application_withdrawal request and the reversed-but-PAID claim. GCP has the regular eft drafts (counted by neither cures_12 nor the hold), the 2026-09-01 regular draft that was later returned, and the cancelled rider for plan_units.
- Counts: VTC 5 factors (4 parameter, 1 method); GCP 6 (5 parameter, 1 method). The task has multi-source factors (vtc_offset, g_relief) and cross-difficulty factors (vtc_offset, vtc_recover → vision; g_tol → dental). Seeded cross rows exist: vision_plans, vision_claims, vision_coverage_requests, dental_plans, ortho_riders. If g_tol is struck (C8-i), GCP keeps 5 factors and its single method g_next.
- Seed realism of the cross-difficulty evidence (XF-12): all 7 vision claims are `in_network_private_practice` with `provider_agreement_id` null and no provider agreement seeded. The schema reads "empty for a non-participating provider", and the vision charter prices in-network claims against the provider's agreement. These are the rows vtc_offset reads (finding T0-F4).

## findings
- **T0-F1 SOURCE-POLICY RED** — `_difficulty.md#findings/C1` demonstrated on this world: vision credit 108.84 (base reading) vs 57.11; grace-cure 180.39 vs 232.12. Location: VTC/REC overwrite replaced_by; scored VTC credit_amount and GCP payment_amount.
- **T0-F2 SOURCE-POLICY RED** — `_difficulty.md#findings/C4`: the base-applied $20 transfer gives 212.12 vs 232.12. Location: GCP rule g_hold sentence; GCP payment_amount.
- **T0-F3 SOURCE-FACTOR RED** — `_difficulty.md#findings/C8`(i): gold includes g_tol −1.00 from a tolerance tiered on dental tenure and deducted from the quoted cure amount, which is not a carrier practice. Location: GCP rule "A shortfall is tolerated for long-standing dental members…"; factor g_tol.
- **T0-F4 SOURCE-FACTOR RED (XF-12)** — cross-difficulty evidence rows the vision charter cannot produce: 7 in-network vision claims with no provider agreement (`c3e26bfb…`, `55cf180a…`, `e2bc1963…`, `38308cc5…`, `039bd6f2…`, `2bb98ca4…`, `d1d0a7f5…`). They decide vtc_offset (71.26 of the gold credit).
- **T0-F5 SOURCE-FACTOR RED** — `_difficulty.md#findings/C6`(ii): vtc_prior's sensitivity is 93.06 by compute and 93.60 by the rule's words; the booked args move with it.
- **T0-F6 SOURCE-POLICY RED** — `_difficulty.md#findings/C9`: the VTC credit's coverage_month and months_covered are scored from prose with no compute binding.
- Observation T0-O1: the prior vision credit `0e1bc999…` (2026-07-24) covers July only, although the August invoice had been issued on 2026-07-12. That is an under-credit no rule of the charter produces, seeded as the vtc_prior evidence.
- Observation T0-O2: VTC defines "the vision plan unit" as the subscriber's single enrollment, while the vision charter defines the plan unit as all the subscriber's enrollments on the account. Reading benefits as the subscriber's own enrollment only would give offset 0 (credit 128.37). The literal time-window wording favours the household reading used above.
- Observation T0-O3 (realism): g_next T1 makes the not-yet-due October premium part of the "grace-cure" amount, and g_hold asks the holder to pay again an in-flight $20. Both are defensible pragmatics but stricter than the base cure sentence.
- Relation to previous revisions: first revision.

## source_gt_comparison
- Revealed 2026-10-18T03:31Z (UTC clock of the reveal command), after both task files and the `_difficulty.md` charter section were on disk. Freeze hashes before the reveal: `_difficulty.md` 7265aecc…df43, `task_0.md` 2add2fcc…77a9, `task_1.md` 4c62dcf6…72c.
- Need / authorisation / timing: same. The customer pays by card herself today. GT ends on `call_user_discoverable_tool submit_grace_cure_payment_5521c4c8`, preceded by unlock.
- Read set: same tables (find_customers, verify_customer_identity, find_billing_accounts, find_billing_transactions, find_vision_plans, find_vision_coverage_requests, find_vision_claims, find_ortho_riders, find_dental_plans).
- Now/wait/refuse: act now, same.
- VTC write: GT `book_vision_term_credit_956578a0` (agent) {billing_account_id 33e3ddd3…, coverage_month 2026-08, months_covered 3, credit_amount 57.11}. Mine: identical, value for value.
- GCP write: GT user {billing_account_id 33e3ddd3…, payment_amount 232.12}. Mine 232.12. Same.
- Order: GT unlock/call VTC (step 9) before the user payment (step 12). Mine: same.
- Problem tree vs `prerequisite_closure`: root billing_ext_grace_cure_payment = mine. Edge → billing_ext_vision_term_credit, kind value_input, gate past_due, form state, resolved_by book_vision_term_credit_956578a0 = mine. why_false names e7c24dcd termination 2026-06-30 voluntary, invoices 2026-07..10, the only credit covering 2026-07: same rows and same months. edge_load_bearing 289.23 = mine 289.23. resolution_order [VTC, GCP] = mine.
- factor_sensitivity vs my factor_weight, figure for figure: vtc_month 58.45=58.45, vtc_offset 128.37=128.37, vtc_prior 93.06=93.06 (compute-substitution figure; the rule-words figure 93.60 is my C6 finding), vtc_int 56.58=56.58, vtc_recover 37.11=37.11. g_next 75.78=75.78, g_disc 231.12=231.12, g_fee 207.12=207.12, g_relief 244.62=244.62, g_hold 212.12=212.12, g_tol 233.12=233.12. baseline_result VTC 145.12=145.12, GCP 43.28=43.28.
- Closest alternative candidates and their exclusion: 289.23 (credit skipped) is excluded by the prerequisite sentence. 145.12 (standard credit) is excluded by the five VTC factor sentences. 281.73 (balance) is excluded by the GCP past-due definition and its factors. The C1 base reading (108.84 / 180.39) and the C4 base reading (212.12) are **not** excluded by any policy text; that is exactly the RED.
- design_rationale check (XF-13): its statements of figures (289.23, 145.12, 57.11, 232.12, the 2026-07-only credit) match my recomputation. No stale figure found.
- Verdict for task 0: **SOURCE-POLICY RED** (T0-F1, T0-F2, T0-F6) + **SOURCE-FACTOR RED** (T0-F3, T0-F4, T0-F5). The problem tree holds (SOURCE-CHAIN PASS). The independent derivation lands on GT exactly, but the charter also admits the second readings in T0-F1/T0-F2, so unique solution is not established.

---

## revision_2

## source_derivation_frozen (revision_2)
- Frozen by 2026-10-18T06:35Z (hash taken at the reveal, 06:35:41Z), before any round-2 GT field was read. Inputs: r2 masked view sha256 379e0805…b77c, charter sha256 051f6139…abd9, task_tools.py sha256 b19f12af…8b34 (from the snapshot I ran; see `_difficulty.md#revision_2`).
- contamination_disclosure: I read the round-1 GT of this task after the revision_1 freeze (recorded there). The round-2 world and charter differ (arrangement, ledger rows, vision claims, VTC/GCP factors), so no round-1 figure carries over; every figure below is recomputed from the r2 view and the r2 charter. tasks/0.json was not opened in round 2 before this freeze.
- World changes vs r1 (diff of the two views): account now Cascade Individual Direct Bill Monthly, payment_method check, balance 332.68; new rows — 2026-09-15 eft grace-cure payment 60.00, returned 2026-09-18 with a 25.00 fee; 2026-09-19 check grace-cure payment 20.00; the r1 20.00 transfer removed; prior vision credit now 10.00 dated 2026-07-08 (coverage 2026-07, 1 month); all vision claims now out-of-network (PAID_OON_REIMBURSEMENT, Select 130 OON schedule exam 45 / single vision 30 / frame 65) plus three Mateo services in March 2026. The persona adds the 60.00 online payment that bounced, the 20.00 check, the removal of automatic draft and the out-of-network receipts.

### policy_self_consistency (this task only, r2)
- Handling time: VTC on the opening world 2026-09-22; GCP after the VTC credit (its only read of that row is cred_all). No waits: the 20.00 check is held and added back, not waited for; grace ends 2026-10-02.
- Seed realism re-checked: two returns of eft/card payments within 12 months (2026-09-11 draft, 2026-09-18 transfer) reach the AutoPay arrangement's autopay_returns_before_removal 2, so the move to Direct Bill (autopay_removal_fallback) and the check payment are charter-producible; fees 25.00 each within the cap of 2; invoices through 2026-10 still carry the −1.00 AutoPay discount they were billed with. The prior 10.00 vision credit is exactly what VTC yields on 2026-07-08 (scratch replay on the ledger as of that date: 1 month billed, offset 79.76 floors the core at 0, recover_short 10.00, posted against 2026-07, 1 month). OON claims need no provider agreement.
- Charter-global r2 findings bearing on this world: C12 (g_fee T1 taken, 50.00 in gold; vtc_feeback T2 taken, 25.00 in gold), C10-r2 (b) (vtc_feeback adds the arrangement's fee whether or not booked; here a fee was booked, so no value moves). C13 and C9-r2 (i) do not move this world (the months were in fact billed on AutoPay; automatic draft was in fact removed). C10-r2 (a) does not move it (the latest held payment is the unreturned check).

### problem_chain (r2)
- Root GCP (user `submit_grace_cure_payment_5521c4c8`), from the same persona goal. Prerequisite sentence (state): a vision-line termination credit posted against the coverage month of the invoice issued last (`b2dc4f8e…`, 2026-10), since the subscriber unit `e7c24dcd…` ended 2026-06-30 by voluntary termination before that month. Opening: the only vision credit `0e1bc999…` is posted against 2026-07 → **false**. Resolver: VTC (`book_vision_term_credit_956578a0`, agent).
- Tree {GCP ← VTC}, value_input via cred_all; one user write; no cycle. Load-bearing: without the credit 342.18, with it 242.62. Tools validate nothing. Persona raises only the root; the vision plan and payments come up only on the agent's questions.

### task_independent_derivation (r2)
VTC (agent, opening world): unit Select 130 family 36.28; months billed after June 4 (Jul–Oct); tenure 8; vtc_month T1 (12 regular eft drafts in 12 m, 1 returned draft that paid a month) = 36.28 − 1.00/3 = 35.946667; offset T1: benefits in the unit window (effective month through termination) = 45+45+30+65+45+45+45+30+65 − reversal 45 = 370.00 > 290.24 → 79.76; vtc_prior T1 = 10.00 (months already credited 1); interest T2: 84 days, base 36.28 × (2 − 1) × 54/365 → 0.536745; recover T1 (unit's own request 2026-06-08, lead 22 ≥ 20; 4 months) = 20.00; feeback T2 (one draft that paid a month returned since June: `eddfa9ef…`; the 2026-09-18 transfer return paid no month) = 25.00. Credit = RND(MX(0, 143.786667 − 79.76 − 10.00) + 0.536745 + 20 + 25) = **99.56**, posted against **2026-10**, months_covered **3** (4 − 1), account `33e3ddd3…`.
GCP (user, after VTC): past_due = 2356.32 + returns 216.34 − payments 2279.98 − credits 109.56 − future invoice 156.34 = 26.78; g_next T1 (draft returned 2026-09-11 ≥ grace start; Oct not begun) 156.34; g_disc T1 (two eft returns in 12 m, regular drafts collected, Direct Bill carries no AutoPay discount) 2.00; g_fee T1 (two returns) fees since grace start 50.00; g_relief T2 (opened 51 months; no return in the 24 months before grace; last fee 2026-09-18 in grace) 12.50; g_hold T1 (return 4 days ago ≤ 60 → 10 days; latest held candidate = check 2026-09-19, 3 days < 10) 20.00. Payment = RND(26.78 + 156.34 + 2 + 50 + 20 − 12.50) = **242.62**, by card. Opening-world contrast 342.18. Terminal balance 332.68 − 99.56 − 242.62 = −9.50.

### factor_weight (r2)
VTC (baseline.rule alone 36.28 × 4 = 145.12 ≠ 99.56): vtc_month → 100.90; vtc_offset → 179.32; vtc_prior → 109.56; vtc_int → 99.03; vtc_recover → 79.56; vtc_feeback → 74.56. All bear weight; cross-difficulty vision: vtc_offset (claims), vtc_recover (request). Multi-source: vtc_offset, vtc_month.
GCP (baseline 26.78 ≠ 242.62): g_next → 86.28; g_disc → 240.62; g_fee → 192.62; g_relief → 255.12; g_hold → 222.62. All bear weight.
Near-misses: withdrawn vision application `555f3204…` and its request; reversed-but-PAID_OON claim; the returned 60.00 transfer (excluded from "draft that paid a month" and not the held payment). No outcome stamps. Counts: VTC 6 (5/1), GCP 5 (4/1); task carries multi-source and cross-difficulty (vision) factors. If C12 strikes g_fee and vtc_feeback, VTC keeps 5 and GCP 4 — bounds still met.

## findings (r2)
- T0-F1 CLOSED (C1). T0-F2 CLOSED (C4 declared). T0-F3 CLOSED (g_tol removed). T0-F4 CLOSED (claims are OON, priced on the Select 130 OON schedule). T0-F5 CLOSED (months already credited is a plain quantity; vtc_prior sensitivity single-valued 109.56). T0-F6 CLOSED (post_month / book_months compute). T0-O1 CLOSED (prior credit reproducible). T0-O2 remains an observation (benefits are customer-wide inside the unit window). T0-O3 remains an observation.
- **T0-R2-F1 SOURCE-FACTOR RED** — `_difficulty.md#findings (r2)/C12` on this world: gold carries g_fee 50.00 and vtc_feeback 25.00 from ladders whose tiers are one rule (g_fee T1/T2/T3 all equal "fees booked since the grace start" on their domains; vtc_feeback is n × fee).
- Observation T0-R2-O1 (realism): vtc_feeback states the returned draft "is caused by Cascade's billing error"; the persona attributes the bounce to moving her paycheck away from the old account, and no record shows the overbilled 36.28 caused it.

## source_gt_comparison (revision_2)
- Revealed 2026-10-18T06:35:41Z after all three revision_2 sections were on disk (sha256 at reveal: `_difficulty.md` f600f16f…0efa, `task_0.md` f99d9109…56ce, `task_1.md` 5d97a72e…cbcc).
- VTC write: GT {33e3ddd3…, coverage_month 2026-10, months_covered 3, credit_amount 99.56} = mine. GCP write: GT user payment_amount 242.62 = mine. Order VTC → GCP = mine; read set identical.
- prerequisite_closure: root GCP, edge → VTC value_input / past_due / state = mine; resolution_order = mine; edge_load_bearing 342.18 (past_due 126.34 without the credit) = mine.
- factor_sensitivity figure for figure: vtc_month 100.90, vtc_offset 179.32, vtc_prior 109.56, vtc_int 99.03, vtc_recover 79.56, vtc_feeback 74.56; g_next 86.28, g_disc 240.62, g_fee 192.62, g_relief 255.12, g_hold 222.62 — all equal. baseline_result 145.12 / 26.78 equal.
- Closest alternatives (credit skipped 342.18; standard credit 145.12; balance 332.68) excluded by the prerequisite sentence and the factor sentences; no second reading of a policy sentence found in round 2 (C1/C4 closed).
- Verdict task 0 (r2): SOURCE-POLICY PASS, SOURCE-CHAIN PASS, unique solution PASS; **SOURCE-FACTOR RED** (T0-R2-F1: C12 members g_fee and vtc_feeback carry 75.00 of gold).
- Disclosure: after the reveal the only edit to this file's revision_2 frozen section was correcting its "Frozen" timestamp line (it had been pre-written as a later minute); no derived figure or finding was changed, so the reveal-time hash above differs from the current file by that line only.

---

## revision_3

## source_derivation_frozen (revision_3)
- Frozen 2026-10-18T12:38Z, before any round-3 GT field was read. View r3 sha256 379e0805…b77c (identical to r2); charter sha256 54d70546…b22b; tools b19f12af…8b34.
- contamination_disclosure: round-1 and round-2 GT of this task were read after their freezes. The world is unchanged since r2, but VTC changed (vtc_window added, vtc_feeback removed) and GCP's g_fee / held-payment rules changed, so the figures below are recomputed from the r3 charter; tasks/0.json not opened in round 3 before this freeze.

### per-task checks (r3)
- Handling time, no waits, problem tree: as revision_2 (root GCP ← VTC, state false at the opening — only a 2026-07 vision credit; load-bearing: opening 342.18 vs 303.56). Tools validate nothing; persona unchanged and still raises only the root.
- r3 charter findings on this world: C3-r3 and C12-r3 not applicable (no DTC/REC/RNP); C10-r3 does not move this world (the latest held candidate is the unreturned 09-19 check; the 09-15 transfer is returned, matched by amount 60.00 and date 09-18, and correctly skipped).

### task_independent_derivation (r3)
- VTC (opening world, account in grace): vtc_month T1 (Direct Bill carries no discount and cannot draft, yet 12 regular drafts were collected in 12 months → months billed on AutoPay) 36.28 − 1.00/3 = 35.946667; vtc_window T2 (account in a grace period) = MONTHS(2026-06-30, 2026-09-22) + 1 = 3 (Jul–Sep; October not yet begun); offset T1 79.76; vtc_prior 10.00; interest T2 0.536745; recover T1 20.00. Credit = RND(MX(0, 35.946667×3 − 79.76 − 10.00) + 0.536745 + 20.00) = **38.62**, posted against **2026-10**, months_covered **2** (3 − 1).
- GCP (after VTC): past_due 2356.32 + 216.34 − 2279.98 − (10.00 + 38.62) − 156.34 = 87.72; g_next T1 156.34; g_disc T1 (two eft returns in 12 m; account left AutoPay) 2.00; g_fee T1 (left AutoPay → fees of 12 months) 50.00; g_relief T2 12.50; g_hold T1 → held check 20.00. Payment = RND(87.72 + 156.34 + 2 + 50 + 20 − 12.50) = **303.56**.

### factor_weight (r3)
- VTC (baseline 145.12 ≠ 38.62): vtc_month → 39.62; vtc_window → 74.56; vtc_offset → 118.38; vtc_prior → 48.62; vtc_int → 38.08; vtc_recover → 18.62. GCP (baseline 87.72 ≠ 303.56): g_next → 147.22; g_disc → 301.56; g_fee → 253.56; g_relief → 316.06; g_hold → 283.56. All bear weight; ladders distinct and reachable; cross-difficulty vision (vtc_offset, vtc_recover); multi-source present. Counts VTC 6 (4/2), GCP 5 (4/1).

## findings (r3)
- T0-R2-F1 CLOSED (vtc_feeback removed; g_fee's new ladder is a real three-way split by how the account pays).
- T0-R2-O1 CLOSED (the fee give-back is gone).
- Observation T0-R3-O1 (realism, not a red): on this world GCP's g_next collects the October invoice in full, vision premium 36.28 for the cancelled plan included, while VTC's grace tier leaves October uncredited "once it begins". Each rule is coherent on its own, but the holder is asked today for premium Cascade's own rules will credit back next month.

## source_gt_comparison (revision_3)
- Revealed 2026-10-18T12:38:05Z after all three revision_3 sections were on disk (sha256 at reveal: `_difficulty.md` 0dab310a…521f, `task_0.md` e9e55736…94b0, `task_1.md` d7000437…d5a3).
- VTC: GT {33e3ddd3…, 2026-10, 2, 38.62} = mine. GCP: GT user 303.56 = mine. Order, owners, read set unchanged and equal.
- prerequisite_closure: same edge; resolution_order equal; load-bearing 342.18 (past_due 126.34) equal.
- factor_sensitivity: vtc_month 39.62, vtc_window 74.56, vtc_offset 118.38, vtc_prior 48.62, vtc_int 38.08, vtc_recover 18.62; g_next 147.22, g_disc 301.56, g_fee 253.56, g_relief 316.06, g_hold 283.56 — all equal; baselines 145.12 / 87.72 equal.
- Verdict task 0 (r3): SOURCE-POLICY PASS, SOURCE-CHAIN PASS, SOURCE-FACTOR PASS, unique solution PASS → **PASS** (charter-only items C3-r3, C10-r3 do not move this world; T0-R3-O1 is an observation).

---

## revision_4

## source_derivation_frozen (revision_4)
- Frozen by 2026-10-18T13:16Z, before any round-4 GT field was read; view r4 379e0805…b77c (unchanged world), charter 6c768f34…51c4.
- contamination_disclosure: earlier rounds' GT read after their freezes; VTC changed (begun-month standard, vtc_window T2), so the figures below are recomputed.
- Problem tree, handling time, no waits, tools, persona: as revision_2/3 (state false at the opening; load-bearing 342.18 vs 267.62).
- VTC: vtc_month T1 35.946667; vtc_window T2 (in grace; draft `eddfa9ef…` returned 2026-09-11 ≥ grace start) = all 4 billed months (Jul–Oct); offset 79.76; prior 10.00; interest 0.536745; recover 20.00 → **74.56**, posted against **2026-10**, months_covered **3**.
- GCP: past_due 2356.32 + 216.34 − 2279.98 − (10.00 + 74.56) − 156.34 = 51.78; g_next 156.34; g_disc 2.00; g_fee 50.00; g_relief 12.50; held check 20.00 (the 09-15 transfer is named by return `f06aa705…` and set aside) → **267.62**.
- factor_weight: VTC (baseline.rule alone 36.28 × 3 begun months = 108.84 ≠ 74.56): vtc_month 75.90, vtc_window 38.62, vtc_offset 154.32, vtc_prior 84.56, vtc_int 74.03, vtc_recover 54.56. GCP (baseline 51.78): g_next 111.28, g_disc 265.62, g_fee 217.62, g_relief 280.12, g_hold 247.62. All bear weight; ladders real and reachable.
- T0-R3-O1 CLOSED: the October premium GCP collects is now the month VTC credits.
- r4 charter item C3-r4 does not bear on this task.

## source_gt_comparison (revision_4)
- Revealed 2026-10-18T13:16:46Z after all revision_4 sections were on disk (sha256 at reveal: `_difficulty.md` e731785b…992e, `task_0.md` 3cd5219f…4447, `task_1.md` 9ed53074…223d; the only pre-reveal edit after writing was replacing a placeholder freeze time in this file).
- VTC GT {33e3ddd3…, 2026-10, 3, 74.56} = mine; GCP GT user 267.62 = mine; order, owners, read set equal; closure edge, resolution order and load-bearing 342.18 equal.
- factor_sensitivity: vtc_month 75.90, vtc_window 38.62, vtc_offset 154.32, vtc_prior 84.56, vtc_int 74.03, vtc_recover 54.56; g_next 111.28, g_disc 265.62, g_fee 217.62, g_relief 280.12, g_hold 247.62 — all equal; baselines 108.84 / 51.78 equal.
- Verdict task 0 (r4): **PASS** on all four relationships.

---

## revision_5

## source_derivation_frozen (revision_5)
- Frozen before any round-5 GT field was read; view unchanged (379e0805…b77c); VTC and GCP unchanged from r4 (charter diff), so revision_4's derivation carries forward on that diff. Replay on the r5 charter: VTC **74.56** (2026-10, 3), GCP **267.62**; sensitivities identical to revision_4 (vtc_month 75.90 … g_hold 247.62). contamination_disclosure: earlier GT read after earlier freezes; replay done from the r5 charter.

## source_gt_comparison (revision_5)
- Revealed 2026-10-19T07:17:07Z after all revision_5 sections were on disk (sha256 at reveal: `_difficulty.md` 5e5c1b95…ab1, `task_0.md` d9d1dea3…793, `task_1.md` c276bd76…c3c).
- VTC {33e3ddd3…, 2026-10, 3, 74.56}, GCP user 267.62, every sensitivity, baselines 108.84 / 51.78 and load-bearing 342.18 equal to mine.
- Verdict task 0 (r5): **PASS**.

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
- Frozen before any round-11 GT field was read. Inputs: r11 view sha256 852c7a55…dac9; charter 50297dc0…19e5; tools b19f12af…8b34. contamination_disclosure: earlier rounds' GT read after their freezes; this world changed (frames, rider dates, invoice/payment amounts), so every figure below is recomputed blind from the r11 view.
- Seed checks: ledger reconciles (invoices + returns + fees − payments − credits = 332.68 = balance_due); invoices price exactly the plans in force each month (dental family 107.66, vision from 2025-11, rider from 2026-01, −1.00 AutoPay); the prior 10.00 vision credit of 2026-07-08 is still exactly what VTC yields on that date (replay: 10.00, posted 2026-07, 1 month); persona unchanged and consistent.
- Problem tree: unchanged (vision credit posted against 2026-10 absent at the opening; tools validate nothing; persona raises only the root). Load-bearing: opening 342.18 vs 317.62.
- VTC: unit Select 130 family 36.28; vtc_month T1 35.946667; vtc_window T2 (draft returned in grace) 4; offset T1: unit benefits 45+45+30+90+45+45+45+30+90 − 45 = 420.00 > 290.24 → 129.76; prior 10.00; interest 0.536745; recover 20.00; v_other 0. Credit = RND(MX(0, 143.786667 − 129.76 − 10.00) + 0.536745 + 20.00) = **24.56**, posted against **2026-10**, months_covered **3**.
- GCP: past_due 101.78; g_next 156.34; g_disc 2.00; g_fee 50.00; g_relief 12.50; held check 20.00 → **317.62**.
- factor_weight: VTC (all-baseline 108.84 ≠ 24.56): vtc_month 25.90, vtc_window 20.54, vtc_offset 154.32, vtc_prior 34.56, vtc_int 24.03, vtc_recover 4.56. GCP (baseline 101.78): g_next 161.28, g_disc 315.62, g_fee 267.62, g_relief 330.12, g_hold 297.62. All bear weight; tiers unchanged in kind.

## source_gt_comparison (revision_11)
- Revealed 2026-10-20T06:19:12Z after all revision_11 sections were on disk (sha256 at reveal: `_difficulty.md` aed23c5d…5129, `task_0.md` afe73f64…ba61d, `task_1.md` ea4509d7…38ec).
- VTC {33e3ddd3…, 2026-10, 3, 24.56}, GCP user 317.62, every sensitivity (25.90 / 20.54 / 154.32 / 34.56 / 24.03 / 4.56; 161.28 / 315.62 / 267.62 / 330.12 / 297.62), baselines 108.84 / 101.78 and load-bearing 342.18 — all equal to mine.
- Stale-text sweep (XF-13) over the revealed proof fields: no superseded figure of earlier worlds (74.56, 120.06, 2025-06-01, 65.00 frame amounts …) remains; the 267.62 that remains is the correct r11 g_fee sensitivity; the offset trace states 420.00 / 129.76.
- Verdict (r11): **PASS**.
