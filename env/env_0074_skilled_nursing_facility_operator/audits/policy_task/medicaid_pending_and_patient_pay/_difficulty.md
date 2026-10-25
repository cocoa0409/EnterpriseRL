# Policy-task audit — medicaid_pending_and_patient_pay / charter-global

## revision_1

## charter_global_frozen
- Freeze time: 2026-10-22T05:17Z (written before any task GT field was opened). Auditor: independent erl-task-policy-audit agent (did not author the artifacts).
- Hashes verified on disk at audit start (match the coordinator brief):
  - `tasks/medicaid_pending_and_patient_pay/medicaid.extended.yaml` sha256 01cdfc0e76068af8f0f47840db3f2bb2e403668f12f8984743dad8f767c06ecc
  - `tasks/medicaid_pending_and_patient_pay/task_tools.py` sha256 ee482bb5ee18e7d41bdbcd0026495481862322e877781b0f7cf8624e1c0496a8
  - masked views task0 52d9acc3…7f51, task1 b3a53fe2…96ec (both match).
- Read: blueprint.yaml, products/medicaid.yaml (base copy diffed — byte-identical to the extended file's base section), the relevant parts of products/medicare.yaml, private.yaml, bedhold.yaml, trust.yaml, db_schema.json, share_tools.py (tool list), the extended charter, task_tools.py, audits/render_source/XF_recipe.md, the two masked views, the gate snapshot.
- Not read before the freeze: tasks/*.json, tasks/…/worklog.md, plan.md, any other audits/ file, any other scenario.
- Entry conditions: gate snapshot present (7 gates rc=0, check_traceability deferred), masked views + hashes present. Entry conditions met.
- Everything below is derived from the charter, schema, tool module and XF recipe only.

### policy_conflict_scan
Five extended policies:

| id | subject / computes | target_tool (owner) | scope | prerequisite |
|---|---|---|---|---|
| medicaid_ext_actual_month_cost_cap (P1) | adjustment.amount (cost_of_care_cap) | post_cost_of_care_reduction_89ef8a19 (agent) | actual_notice charge of the calendar month before NOW | [] |
| medicaid_ext_estimate_month_trueup (P2) | adjustment.amount (trueup_decrease) | post_trueup_decrease_6ec57e06 (agent) | latest estimated_pending month on an approved case | [] |
| medicaid_ext_eligible_advance_payment (P3) | payment.amount | pay_patient_pay_advance_e93eb0b7 (user) | advance on an approved case | P1, P2 (value_input, state form) |
| medicaid_ext_pending_estimate_cost_cap (P4) | adjustment.amount (cost_of_care_cap) | post_pending_cost_of_care_reduction_7ee4a52a (agent) | estimated_pending charge of the month before NOW on a pending case | [] |
| medicaid_ext_pending_advance_payment (P5) | payment.amount | pay_pending_patient_pay_advance_fe3c809e (user) | advance on a pending case | P4 (value_input, state form) |

- Overlapping subjects: P1, P2, P4 all write `medicaid_patient_pay_adjustment` and all three retire the same base sentence "patient pay never exceeds the month's cost of care." Their scopes are disjoint by charge basis (actual_notice vs estimated_pending) and case status (approved vs pending); each sibling `replaced_by` names the other two cases (XF C.17 satisfied). P3 / P5 are disjoint by case status (approved vs pending).
- Cross-category reads: medicare (P1, P2, P4, P5), bedhold (P1, P2, P4), private (P2, P4), trust (P3, P5). All read-only.
- Terminal states: adjustments and an unallocated ACH payment; no status transitions. No conflicting terminal states between policies.
- Expected scope partition (to be confirmed against `charter_scope` after reveal): one tree {P3 ← P1, P2} on an approved case, one tree {P5 ← P4} on a pending case — jointly complete and pairwise disjoint.
- Base/extended conflicts that are NOT declared are listed under `override_declarations` (F-02, F-03, F-04).

### rule_compute_equivalence
- Every `compute_basis` quotation is verbatim in its own rule (scripted sweep, 0 misses; XF B.9 PASS). Every baseline-rule sentence is in the rule. Every `replaced_by` is in the rule; every `superseded_clause` is verbatim in the base policy.
- Bindings without a basis are date plumbing only (month_index, first-day strings, now_index).
- Rounding (XF B.10): P1/P2/P4 round each product then add, and floor/round the result — matches the rule. P3 matches. **P5: `interest_counted` applies `RND(interest_three_months / 3, 2)` at an intermediate point; the rule states no rounding for "one third of the interest credited in those three months"** (only the final "never below zero, rounded half up to the cent"). Member of XF B.10 → F-12. (Because every other term is whole cents and a third of a whole-cent sum is never exactly half a cent, the mismatch cannot move a final figure; it is reported because the recipe makes every member RED.)
- Edge branches (XF B.11 / A.8):
  - P3 `coming_patient_pay` third tier "the amount billed on the latest actual-notice charge": the absent record (an approved case with no actual_notice charge yet and a notice effective on or before the coming month) is not stated in the rule; compute returns `latest_actual_amount or 0` = 0. → F-11.
  - Same-day ties of LATEST / XLATEST reads (P2 `estimate_month`, `estimate_charge_id`, `notice_patient_pay`; P3 `latest_actual_month`/`latest_actual_amount`/`latest_estimate_amount`, `latest_payee_benefit`, `latest_pension_deposit`; P5 `latest_interest`, `latest_pension`, `latest_payee`) — no rule states which row a tie keeps; P2's "latest month billed as an estimate" is ordered by entry_date in compute, while the rule's words also admit "latest service month". → F-11.
  - First-match CFIELD reads with possible second records (XF B.12): `CFIELD('medicare', …)` (one coverage episode per skilled admission — a resident can hold several), `CFIELD('private','admission_date')`, `CFIELD('trust', …)`; no rule states which coverage/agreement/account is read. → F-11.
  - Negative lag (XF B.11): P2/P4 `remaining_days` has no floor; see F-09 for a producible world where it goes negative.
- Factor-ladder ↔ rule: every tier named in `factors[].ladder` is a rule sentence and a compute branch; no compute-only tier found. But P3's `amount_kept_for_resident` first tier is stated differently in rule and compute: rule "the routed benefit is a pension" (an outcome of the benefit_routed factor); compute `kept_pension_recent > 0` (a pension deposit in two months, no standing-authorization test). → F-07.

### action_binding_and_uuids
- Five `(target_tool, computes)` pairs, each claimed once. uuid8s 89ef8a19, 6ec57e06, e93eb0b7, 7ee4a52a, fe3c809e — distinct, no shared prefix/suffix/sequence. No factor id is a substring of any tool name (XF D.20 PASS). No composite string args (D.21 PASS). Each write tool calls ctx.create/ctx.update in its own body; `_Ledger` is a static helper class (D.22 PASS). No forbidden import or substring (D.23 PASS). Events written: medicaid_patient_pay_adjustment, medicaid_patient_pay_payment — both `triggers: []` (D.25 PASS). Tools validate no prerequisite (bodies read only the case row for the customer id and balance).
- XF D.19 members (docstrings carrying ordering words / claiming an effect the body lacks) → F-13:
  - `post_trueup_decrease_6ec57e06` docstring: "recording a reduction with reason trueup_decrease" — the body records whatever `adjustment_reason` the caller passes (any of five values); the claimed fixed-reason effect is not in the body.
  - Ordering words: all three adjustment tools' `adjustment_reason` descriptions ("…lowered to the actual patient pay of the month **once** eligibility is approved", "a **later** County Assistance Office notice", "**earlier** than the eligibility start date"); both pay tools ("ahead of that month's bill" / "ahead of that estimate's bill", "**not yet** applied"). None names another tool or a problem of this difficulty.
- No docstring carries a concrete example value (D.19 example half PASS).

### prerequisite_graph
- Every policy has `prerequisite` (P1, P2, P4 `[]`). Edges: P3→P1, P3→P2, P5→P4; every `problem` is an extended policy id of this file; acyclic.
- `policy_source` verbatim in the blocked rule: P3 edge 1 "The advance is fixed only after the actual charge of the last closed month stands at no more than that month's cost of care." (present); P3 edge 2 "The advance is not fixed until the latest month billed as an estimate stands reconciled to the actual patient pay of that month." (present); P5 "The advance toward a coming pending month is worked out only after the estimate of the last closed month stands at no more than that month's cost of care." (present).
- `form: state` everywhere, no `fallback_reason` (correct). `kind: value_input`; `gate` names `balance_carried` / `pending_balance_carried`, both real bindings; `resolved_by` = the depended-on policy's target_tool; the reduction lowers the patient pay balance which those bindings read — effect real.
- `condition` vs sentence: the conditions name the reduction reason (cost_of_care_cap / trueup_decrease) where the sentence names only the state ("stands at no more than", "stands reconciled") — a narrowing to the one write that produces the state, not a change of strength. Accepted.
- P5 edge `effect` text "turning it into a fresh credit that the advance subtracts" asserts a world-specific outcome (true only where the balance was already paid down); recorded as observation O-03.

### prerequisite_sentences
- All three sentences pass the four-point test: ordering connective (only after / not until / only after); a record-visible state (net actual charge of the last closed month vs its cost of care; latest estimate month's net estimate vs its actual patient pay; last closed month's net estimate vs its cost of care); no tool, policy id, snake_case token or row id; strength matches the condition.
- One write brings each state about: P1's cost_of_care_cap reduction (only policy reducing an actual_notice charge of the last closed month on an approved case); P2's trueup_decrease (only policy reconciling the latest estimate month); P4's cost_of_care_cap reduction on a pending case's last-month estimate. No second candidate write in this difficulty.
- Derivation a reader performs: sentence → "that month's cost of care" → the only rule that defines the cost of care of an actual-billed / reconciled estimate / pending estimate month is P1 / P2 / P4 respectively → their reduction write. Single reading.
- No second wording, no tool name, no other problem's id in any rule; depended-on rules do not restate the sentences; no docstring states sequence (ordering-word members listed under F-13 do not concern this graph).
- Cross-problem orders in rules that ground no edge: P3/P5 "it is applied, oldest service month first, when the coming month is billed" — refers to base billing, not to a problem of this difficulty; observation O-04.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry:

- **medicaid_evt_patient_pay_actual** (refs of P1, P2, P4): "billed the patient pay amount on the notice … actual_notice" followed; "a redetermined amount … applies from the first day of the month the notice names" followed (P2's notice_patient_pay, P3's coming PP); **"In a month of admission, discharge or death, patient pay is the lesser of the monthly patient pay and the days in the center times the Medicaid daily rate, with charge basis partial_month, and any amount already billed above that is reduced with reason cost_of_care_cap"** — NOT retired by any overwrite, yet P2 (and P4 by its admission factor) define the actual patient pay of a month of admission differently (P2: lesser of notice PP and a cost with Part A, leave and pre-admission days taken out). Undeclared override → F-02. "patient pay never exceeds the month's cost of care" retired by P1/P2/P4 with sibling exclusions (declared). "Patient pay is unchanged for a month with Medicaid reserved bed days" followed. Trueup sentences: "where it is lower … trueup_decrease" retired by P2 (declared); `replaced_by` ends "every other reconciliation remains under the base rule" (defers to the clause it retires, but its opening restates the generic content — observation O-05). "Estimates … before the eligibility start date … not_eligible_month" inherited. Hospice credit, payment in full, adjust-once inherited.
- **medicaid_evt_pending_estimate** (refs of P2, P4, P5): P5 retires only the fragment "gross monthly income less the personal needs allowance, less health insurance premiums the resident pays," but its replacement formula for the advance ("income + interest counted − PNA − premiums counted − allowance deducted") also departs from the un-retired fragments "less the protected VA pension amount for the VA tier, and less the … allowance on the worksheet when the tier applies it": the VA deduction is dropped for the advance, and the allowance fragment stays in force beside the factor that re-implements it. Undeclared → F-03.
- **medicaid_evt_payments / medicaid_agg_case_balances** (refs of P3, P5): base "A patient pay credit balance is refunded within the refund days, to the resident or representative, or to the estate after a death." P3 and P5 (`overwrite: []` on these refs) instead subtract a credit from the advance whenever a reduction was posted within the refund days — the credit is applied to the coming month rather than refunded. Undeclared → F-04.
- **medicaid_case_maintenance**: followed (tier follows allowances; HMA months; zero-balance close).

### factor_ladders
Counts as declared: P1 4 (2 method, 2 parameter); P2 5 (3 m, 2 p); P3 4 (2 m, 2 p); P4 5 (3 m, 2 p); P5 5 (3 m: interest, funds, balance; 2 p: allowance, premiums). Mechanical transitive scan: no factor binding reads another factor's binding (A.1 compute side PASS); no `result` assembled inside a factor binding.

Pairwise shape table (XF A.7: any aggregate of one field counts as one input whatever its filter/window; constant multipliers ignored; a "nothing" tier fails where another tier is 0 on its whole domain):

| factor | tiers | failing pair(s) | verdict |
|---|---|---|---|
| P1 part_a_days_without_cost / P2 stay_days_taken_out / P4 pending_stay_days | T1 full+uncert, T2 full, T3 uncert, T4 0 | T2 vs T3 (both a sum of medicare_ledger.day_count, filter only); T4 vs T1/T2/T3 (each is 0 on T4's domain, since T4 is "full = 0 and uncert = 0") | FAIL — the four tiers are one formula, full + uncert, gated by "> 0" tests on its own summands |
| P1 held_leave_days / P2 leave_days_taken_out / P4 pending_leave_days | T1 all hold days, T2 private hold days, T3 0 | T1 vs T2 (sum of bedhold_ledger.day_count, filter only); T3 vs T2 (T2 = 0 on T3's domain) | FAIL |
| P2 admission_or_closing_days | T1 pre+post, T2 pre, T3 post, T4 0 | none (different date fields) | PASS (A.7) |
| P4 pending_admission_days | same as P2 | T1 and T3 need the case's closing date inside the month; P4 covers only pending cases, and a pending case cannot carry a closed_date (closed is reachable only from application_preparing/denied/fair_hearing/eligible) | FAIL — 2 reachable tiers |
| P3 benefit_routed_to_patient_pay | T1 latest SSA payee deposit, T2 latest pension deposit, T3 0 | T1 vs T2 (LATEST trust_ledger.amount, filter only) | FAIL — a parameter labelled method |
| P3 case_balance_carried / P5 pending_balance_carried_in | T1 add balance (owed), T2 add balance (credit), T3 0 | T1 vs T2 — identical expression (`case_balance`) | FAIL — two tiers select the same method |
| P5 pending_interest_counted | T1 latest interest credit, T2 3-month sum / 3, T3 0 | T1 vs T2 (aggregates of trust_ledger.amount, multiplier ignored); T3 vs T2 (0 on T3's domain) | FAIL — parameter labelled method |
| P5 pending_funds_applied | T1 latest pension, T2 latest SSA payee benefit, T3 0 | T1 vs T2 (LATEST trust_ledger.amount, filter only) | FAIL |

Valid method factors after the shape test: P1 0, P2 1 (admission_or_closing_days), P3 0, P4 0, P5 0 → F-05.

Parameter ladders:
- coinsurance_year_price / coinsurance_figure_by_year / pending_coinsurance_figure: 2026 → 217.00, 2025 → 209.50 (match medicare.yaml coinsurance_rate_by_year and the real CMS figures); fall-through "any other year → the Medicaid daily rate on the case", multiplied by the Medigap share percent. No business prices a Medicare coinsurance day at the Medicaid per diem (e.g. a 2027 or 2024 coinsurance day at 25 % or 50 % of the Medicaid rate); the Medicare SNF coinsurance is a federal figure per year. Unreal fall-through value → F-06.
- medigap_share / coinsurance_percent_by_plan / pending_coinsurance_percent: K/L → the Medicare tier's resident share (50 / 25), C/D/F/G/M/N → 0, otherwise 100 — real Medigap SNF-coinsurance coverage. PASS.
- coming_month_patient_pay (P3): tier 1 value is `F('patient_pay_amount')`, the recorded CAO patient pay — exactly what the in-force base sentence "each eligible month is billed the patient pay amount on the County Assistance Office notice in effect for that month … applies from the first day of the month the notice names" already gives. Baseline "the amount billed on the latest actual-notice charge" is a figure no reader of the base rule would choose once a new notice names the coming month. XF E.28 ("a factor already embedded in a recorded … patient pay is not load-bearing") → F-08.
- amount_kept_for_resident (P3): values PNA+VA protected / PNA / 0 are the real PA PNA ($45) and VA $90 protected amount. But (a) rule tier 1 condition "the routed benefit is a pension" reads the outcome of benefit_routed_to_patient_pay (XF A.1/A.5); (b) T2 fails (A.6): with benefit_routed at its baseline 0, `funds_part = MX(0, 0 − kept) = 0` for every tier, so this factor can never move the result on its own; (c) its selections (`kept_tier`, `kept_pension_recent`) duplicate `account_tier` / `pension_deposits_recent` of another factor instead of one plain binding (A.2). → F-07.
- pending_allowance_deducted (P5): values are the recorded worksheet allowances; the un-retired base fragment "less the … allowance on the worksheet when the tier applies it" already deducts them, so the baseline 0 is a straw man against an in-force base clause (see F-03) → F-08.
- pending_premiums_counted (P5): QMB → premiums less the 2026 Part B standard premium (202.90, real); Medicare not QMB and no health insurance card forwarded → Part B only; otherwise case premiums. Conditions are ones a business office weighs (verification). PASS structurally.
- Conditions that no business weighs: the leave ladders' tier 1 "privately paid held days **and** Part A days booked for the month → every held day (including Medicaid reserved days) is dropped": whether a Medicaid reserved day is a Medicaid day is made to depend on whether some *other* held day of the month was privately paid. With Part A days booked and only Medicaid-reserved held days, the reserved days stay Medicaid days (tier 3); add one privately paid day and they are dropped — although the stated reason ("a hold during a Medicare skilled stay is never a Medicaid reserved day") does not depend on the private day. → part of F-05/F-06 realism (F-06).
- Admission factor (P2, P4) reads `private_agreements.admission_date`, whose schema meaning is "date private-pay residence began" (private_admission: "the resident arrives and private-pay billing starts"); the facility admission is `customers.original_admission_date`. For the background's typical path (Part A stay, then private pay), the days before the private admission date are Part A days already taken out by the stay factor or priced as coinsurance days → double removal, `remaining_days` negative → F-09.
- Multi-source / cross-difficulty: every policy has at least one multi-source factor (e.g. stay/leave conjunctions, account tier + deposit recency) and at least one cross-difficulty factor (medicare / bedhold / private / trust). Structure PASS (subject to the strike-outs above).
- Assembly sentences (XF A.3): every policy's assembly sentence names factor quantities — P1 "dropped days … coinsurance day price times the coinsurance share percent", P2/P4 "days taken out … daily coinsurance figure times the month's coinsurance percent", P3 "less the benefit the resident's funds account routes … net of the amount kept for the resident … adjusted by the case balance carried", P5 "plus the interest counted as income … less the premiums counted and less the allowance deducted" and "less the funds the resident's funds account applies … adjusted by the pending case balance carried". → F-10.

### findings
(Charter-global; each lists the tasks whose files carry the per-world demonstration. "RED" = SOURCE-POLICY / SOURCE-FACTOR as noted; XF members are RED per the coordinator brief.)

- **F-01 SOURCE-FACTOR RED (realism, XF E.27/E.29) — patient pay capped at a cost of care that counts the resident's own Medicare coinsurance share, which the Medicare product bills to the resident separately.** P1/P2/P4 price each coinsurance day at "coinsurance × the resident's Medigap share", so a month whose only non-dropped days are coinsurance days ends with patient pay = the resident's coinsurance share; the Medicare charter (non-QMB tiers) bills that same share to the resident on medicare_ledger (liable_party resident). The resident pays the share twice. Under Pennsylvania MA the resident's patient pay is applied toward the coinsurance a dual-eligible owes; it is not collected in addition to it. Bears on task0 (Sep, Oct) and task1 (Oct).
- **F-02 SOURCE-POLICY RED (undeclared override, XF C.16/C.18)** — base partial-month sentence (quoted above) vs P2's actual patient pay of the reconciled estimate month; both apply to a month of admission billed as an estimate on an approved case. Bears on task0.
- **F-03 SOURCE-POLICY RED (undeclared override, XF C.16/C.18)** — P5's advance estimate drops the base VA protected-pension deduction (VA tier: base gives income − 45 − premiums − 90; P5 gives income − 45 − premiums counted, a 90.00 difference) and re-implements the un-retired allowance fragment as a factor with a 0 baseline. Charter-level demonstration only (task1 is HMA tier: the allowance readings coincide).
- **F-04 SOURCE-POLICY RED (undeclared override, XF C.16/C.18)** — credit subtracted from the advance (P3/P5 third ladder tier 2) vs base "A patient pay credit balance is refunded within the refund days". Same world, two advances (credit netted vs not). Bears on task1 (credit tier taken); task0 takes the owed tier.
- **F-05 SOURCE-FACTOR RED (XF A.7; ladder reality / method honesty)** — table above: valid method factors P1 0, P3 0, P4 0, P5 0; ladders with fewer than three distinct tiers (stay/part_a, leave, P4 admission, both balance-carried). Bears on both tasks.
- **F-06 SOURCE-FACTOR RED (realism, XF E.27)** — coinsurance-price fall-through at the Medicaid daily rate (all three cost policies); leave-ladder compound condition making Medicaid reserved days depend on an unrelated private day. Bears on both tasks (ladder declared on their computations).
- **F-07 SOURCE-FACTOR RED (XF A.1/A.2/A.5/A.6)** — amount_kept_for_resident: gated through benefit_routed in the rule, T2 impossible, duplicated selections. Bears on task0.
- **F-08 SOURCE-FACTOR RED (XF E.28 / straw-man baseline)** — coming_month_patient_pay (task0) and pending_allowance_deducted (task1): the tier value is a recorded CAO/worksheet amount that an in-force base sentence already applies.
- **F-09 SOURCE-POLICY RED (XF B.11/B.13, realism)** — admission factor keyed on the private-pay start date; producible world (Part A from day 6 to day 25, private agreement admission on day 26, pending case): stay takes out 20, admission takes out 25 → remaining_days = 31 − 20 − 25 = −14 → cost negative → the reduction exceeds the estimate it reduces. Not exercised by either task world (private admission = facility admission in both).
- **F-10 RED (XF A.3)** — assembly sentences name factor quantities, all five policies.
- **F-11 RED (XF A.8/B.11/B.12)** — unstated absent-record branch (P3 coming PP), unstated LATEST tie rules, unstated first-match choice among several Medicare episodes / agreements / accounts. Not exercised by either task world.
- **F-12 RED (XF B.10)** — P5 intermediate rounding of the interest third not stated in the rule (no score consequence possible).
- **F-13 RED (XF D.19)** — trueup tool docstring claims a fixed reason the body does not enforce; ordering words in all five docstrings.
- Observations: O-01 seeded `medicaid_patient_pay_charge` estimated_pending amounts in both worlds are not reproducible by the base estimate formula from the records (see task files — promoted to RED there where it moves a scored read); O-02 receipts render floats (e.g. a balance of -387.2) where the docstring says "two decimals", and bodies accept non-positive amounts the docstring forbids (no gold amount is affected); O-03 P5 edge `effect` wording is world-specific; O-04 "applied … when the coming month is billed" orders against base billing, no edge; O-05 P2 overwrite 1 `replaced_by` defers to "the base rule" it retires; O-06 neither world seeds the base-mandated Medicaid-pending accrual for its pending month(s) (pending_receivable untouched by any scored read); O-07 bed-hold charges are posted on the return date, base bedhold says they are billed on the statement day of the following month (no scored read).

## closing_checklist (post-reveal, 2026-10-22T05:2xZ)
- Per-task files 0.md, 1.md correspond one-to-one with tasks/0.json, tasks/1.json; this is revision_1 (no earlier revision exists).
- Scopes (charter_scope): task 0 = {P1, P2, P3} + their three tools; task 1 = {P4, P5} + their two tools — pairwise disjoint and jointly complete over the five extended policies, matching § policy_conflict_scan. uuid8s independent (§ action_binding_and_uuids).
- Problem trees: task 0 n=2, 2 value_input, owner=user root, acyclic; task 1 n=1, 1 value_input, owner=user root, acyclic; difficulty graph acyclic. Both independent derivations reproduce GT exactly (every scored value, tool, owner, order; every factor_sensitivity and baseline_result figure).
- Factors: NOT closed — F-05/F-06/F-07/F-08 leave no computation of either task with ≥ 4 surviving factors, and P1, P3, P4, P5 with no valid method factor.
- Unique solution: NOT closed — F-02 (task 0) and F-04 (task 1) each give a second defensible scored value.
- Realism: NOT closed — F-01 (resident coinsurance share collected twice) in both tasks.
- Post-reveal note on `_difficulty.md` O-01: the task files downgrade the estimate-reproducibility point to an observation (a producible history with an unrecorded premium update gives the same rows, and the policies read the billed amount); the pre-reveal sentence above "promoted to RED there" is superseded by that disclosure.
- Gates: not re-run by this audit (coordinator snapshot 2026-10-22T05:03:14, all rc=0). The difficulty does not pass the source-layer audit.

VERDICT revision_1: task0=RED:T0-1,T0-2,T0-3 task1=RED:T1-1,T1-2,T1-3 charter=F-01,F-02,F-03,F-04,F-05,F-06,F-07,F-08,F-09,F-10,F-11,F-12,F-13

## revision_2

### entry (2026-10-22T10:0xZ)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh medicaid_pending_and_patient_pay 2` → "== snapshot medicaid_pending_and_patient_pay round 2 at 2026-10-22T10:02:17"; [check_extended] rc=0 :: EXTENDED OK; [check_task_tools] rc=0 :: TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 :: REPLAY OK; [check_solvability] rc=0 :: SOLVABILITY OK; [check_compute] rc=0 :: COMPUTE OK; [check_grounding] rc=0 :: GROUNDING OK; [check_cross_fire] rc=0 :: SCOPE OK.
- Hashes: task_tools.py 711c350ad51d7f8c2fc152ca4d0f0c2a0b96ae4412332f78cff103b6051f62ee; medicaid.extended.yaml db7dd2812019b4d2ca07dcc226e3550e3bc1fe5a9adb73a30044af9b78d96735; task0.view dde9d2de…ae8b; task1.view 19ac1eff…ba91. Both sources changed since revision_1 → every charter-global section re-derived below.
- contamination_disclosure: GT of both tasks was seen in revision_1; for this round the worklog "REWORK round 2" section (claims, probe table, T1/T2 table with figures) was read **before** the per-task recomputation, as permitted by the coordinator. The round-2 per-task derivations are therefore re-checks, not blind answers. tasks/*.json GT fields were opened only after the recomputation (they agree, see task files).
- Base section still byte-identical to blueprint/products/medicaid.yaml.

### rule_compute_equivalence / XF B.9–B.13 (re-derived)
- Scripted sweep: every compute_basis quote, baseline sentence, `replaced_by` and `policy_source` verbatim in its own rule; every `superseded_clause` verbatim in its base policy (0 misses). Rounding sentences match RND placement in all five policies (P5 interest third now stated — F-12 closed).
- New/changed reads — decoy and absent-record check (all members):
  1. `declined_leave_start` / `declined_return` / `released_on` / `released_return` (P1, P2, P4): the rule keys the declined and released holds to "the first reservation in status declined [released] that the resident's bed-hold records list". Decoy: an older declined hold of another month listed before this month's declined hold → this month's unheld days are counted as Medicaid days (the reworker's own probe shows the reconciliation moving to 1958.54). A second declined hold inside the same month is never read. Storage order is not a criterion any business uses. → R2-F-11.
  2. `departure_on` (P2, P4): `CFIELD('bedhold','leave_start_date', end_reason='hospital_discharged_elsewhere')` is a first match; the rule states no choice among several such reservations (a resident readmitted after an earlier discharge elsewhere carries an older one). → R2-F-11.
  3. `booking_coverage` / `skilled_admission` (P2, P4): when a month holds two coverage episodes (a readmission after a new qualifying stay — "one coverage episode per skilled admission"), the latest episode's coverage start is mid-month and every day before it is taken out as "days before the admission", including the first episode's Part A days already taken out or priced as coinsurance days → double removal. Example: episode A days 21–100 on the 1st–10th, hospital 11th–14th, episode B from the 15th (coverage start = qualifying discharge): stay_days_out = 14, coinsurance days 10 → the same 10 days are removed twice. → R2-F-09.
  4. `held_day_limit` (P1, P2, P4): the limit is set by the tier of the reservation behind the month's latest booking and applied to every held day of the month. Decoys: (a) a Medicare-stay private hold early in the month and a Medicaid hospital reserved bed later → the privately paid days (charged to the resident by the bed-hold product) count as Medicaid days up to the 15-day limit; (b) a therapeutic reserved bed whose calendar-year allowance was mostly used earlier in the year → the bed-hold product books the excess days `resident_private`, but this policy counts all of them up to the full yearly allowance; (c) per-hospitalization limit compared with this month's days only, ignoring the same hospitalization's days in the previous month. The ledger's `day_payer` already records which held days are payer-reserved; the rule ignores it. → R2-F-06.
  5. `latest_booked_coinsurance` (P5): rule "the daily coinsurance most recently booked on that coverage" (the active coverage); compute has no coverage filter. Only reached for coming months outside 2025/2026. → R2-F-11.
  6. `coinsurance_day_price` third tier (P1, P2, P4) "otherwise (no Medicare coverage booked Part A days for the month) → the Medicaid daily rate": in that domain no Part A day is booked, so coinsurance days are 0 and the tier's value can never reach the cost of care. The ladder has two operative tiers. → R2-F-05.
  7. Overlapping schedules (P2, P4): a reservation that ended because the hospital discharged the resident elsewhere contributes its held days to the held-day schedule (taken out beyond the limit, or counted as Medicaid days within it) and the same days to the departure schedule (taken out from the leave start). A private hold of 5 days ending in a discharge elsewhere on the 20th removes 5 + 12 = 17 days for 12 days away. → R2-F-09.
  8. Admission detection (P2, P4): the only admission the stay schedule sees is a Medicare skilled admission (coverage start equal to the qualifying discharge). P2/P4 now retire the base partial-month clause for estimate months of admission, so a month of admission without a Medicare skilled stay keeps every pre-admission day as a Medicaid day. Example: pending case, resident admitted on the 29th with no Part A, estimate 1073.70, MA rate 279.84: P4 cost 31 × 279.84 → reduction 0.00; the retired base clause would give days in the center 3 × 279.84 = 839.52 → reduction 234.18. `customers.original_admission_date` holds the admission. → R2-F-09.
- Tie rules now stated where read (LATEST by service month; payee tie resolved by MX). Absent coming-month charge stated (F-11 part closed).

### override_declarations (re-derived)
- P2 and P4 retire the base partial-month sentence with sibling-naming `replaced_by` (closes F-02 for P2/P4). P2 overwrite 1 now restates the base reconciliation for other months (O-05 closed).
- **P1 does not retire it, yet a month of discharge or death can be the actual-billed month P1 reviews**: base "In a month of admission, discharge or death, patient pay is the lesser of the monthly patient pay and the days in the center times the Medicaid daily rate, with charge basis partial_month, and any amount already billed above that is reduced with reason cost_of_care_cap" vs P1 (cost of an actual-billed month = every calendar day less P1's schedules, with no departure schedule). Same situation (eligible case, October billed actual_notice 2245.90 on the 1st, resident discharged on 5 October, no Part A): base → 2245.90 − 4 × 287.36 = 1096.46; P1 → 31 × 287.36 > charge → 0.00. P1's own `replaced_by` ("partial-month charges … remain under the base rule") does not resolve it — the charge is actual_notice, not partial_month. → R2-F-02 (P1 member).
- P5 retires the whole base estimate clause for the advance only and restates it for billed estimates; standard keeps VA and tier allowance (F-03 closed). P3 and P5 retire the refund clause for a fresh credit, sibling-named (F-04 closed; C.17 satisfied).

### factor_ladders (re-derived)
| policy | factor | label | A.7 / ladder | notes |
|---|---|---|---|---|
| P1/P2/P4 | *_coinsurance_day_price | parameter | 3rd tier vacuous (item 6) | FAIL — 2 operative tiers |
| P1/P2/P4 | *_part_a_days_out | method | T2 vs T3 same field (medicare_ledger.day_count, filter only); T4 "none" is 0 where T1/T2/T3 are 0 | FAIL (unchanged from revision_1; the worklog records it as "residual A.7 risk") |
| P1/P2/P4 | *_held_day_limit | parameter | 3 operative tiers (4th vacuous) | realism FAIL (item 4) |
| P1/P2/P4 | *_unheld_leave_days | method | PASS (declined vs released spans are different fields) | decoy FAIL (item 1) |
| P2/P4 | *_days_outside_stay | method | PASS | double count (items 3, 7), admission gap (item 8) |
| P3 | approved_payee_benefit_applied | method | PASS (MX adds an operation; "nothing" nonzero elsewhere) | |
| P3 | approved_authorized_pension | parameter | PASS | |
| P3 | approved_amount_kept | parameter | PASS; T2 now possible (benefit in the standard) | |
| P3 | approved_balance_carried | method | PASS (credit tier adds MN cap on a non-factor binding) | |
| P5 | pending_projected_coinsurance | method | PASS (month days vs days left; incurred-medical-expense deduction under 42 CFR 435.725(c)(4)(ii) is a real rule) | |
| P5 | pending_premiums_counted | parameter | PASS | |
| P5 | pending_interest_counted | parameter (relabelled) | PASS | |
| P5 | pending_funds_applied | parameter (relabelled) | PASS | tier 2 realism, below |
| P5 | pending_balance_carried_in | method | PASS on shape | **A.1 FAIL**: its credit tier caps at `pending_estimate`, which is assembled from pending_projected_coinsurance, pending_premiums_counted and pending_interest_counted (mechanical transitive scan) |
- A.2: P3 selects the funds account tier twice — `pension_tier` (approved_authorized_pension) and `kept_tier` (approved_amount_kept), both `CFIELD('trust','variant_name', status='active')` — instead of one plain binding. (The worklog states "selections not duplicated".)
- A.3: P1/P2/P4 assembly sentences are now generic (PASS). P3 "it chooses the benefit applied, adds funds the account applies under a standing authorization, keeps an amount back for the resident, or carries the case balance; the funds the account applies, net of what it keeps back …" and P5 "it deducts the resident's own Medicare coinsurance, sets the premiums counted, adds the interest counted as income, subtracts the funds the resident's funds account applies, or carries the pending case balance" (also P5 overwrite 1 `replaced_by` "the changes the schedules below make for the resident's own Medicare coinsurance, the premiums counted and the interest counted") still name factor quantities.
- Realism (E.27), not raised in revision_1 (missed by this auditor, present then): P5 pending_funds_applied tier 2 applies "the whole latest benefit received" of a non-Medicaid representative-payee account to an estimate that already deducted the personal needs allowance, so the allowance the estimate leaves the resident is taken as patient pay (contrast P3, which keeps the allowance in a payee account). Example: benefit 1783.50, estimate 1200.00 → funds applied 1783.50 exceed the estimate by 583.50 including the 45.00 allowance.
- Counts after strike-outs: P1 4 declared → coinsurance price (vacuous tier) and part_a (A.7) struck, held_day_limit realism-struck → 1 survives (< 4). P2 5 → 2–3 survive. P4 5 → 2–3 survive. P3 4 survive (structure PASS apart from A.2/A.3). P5 5 survive on shape; balance factor fails A.1.

### action_binding_and_uuids / docstrings (re-derived)
- uuid8s unchanged and distinct; no factor id ⊂ tool name; no forbidden imports; each write tool creates/updates in its body; bodies now enforce positive half-up cents and render two-decimal strings (O-02 closed). No ordering word, no other tool, no example value in any docstring; the trueup docstring now says "with the reason given" (F-13 closed).

### prerequisite_graph / sentences (re-derived)
- Unchanged sentences, all verbatim in their blocked rules; state form; gates exist; acyclic; `effect` texts now generic (O-03 closed). PASS.

### revision_1 → revision_2 status
| id | status |
|---|---|
| F-01 | closed (non-QMB coinsurance days priced 0; resident share only in the Medicare ledger and, for the pending advance, as an incurred-medical-expense deduction) |
| F-02 | open — closed for P2/P4; P1 member (discharge/death month) |
| F-03 | closed |
| F-04 | closed |
| F-05 | open — part_a_days_out (P1, P2, P4) unchanged; coinsurance_day_price vacuous tier (P1, P2, P4) |
| F-06 | open in a new form — held-day limit (P1, P2, P4); year fall-through and leave compound condition removed |
| F-07 | partly open — A.2 duplicated tier selection in P3; A.1/A.5/A.6 closed |
| F-08 | closed |
| F-09 | open in a new form — private-pay date removed; double counts (items 3, 7) and admission gap (item 8) |
| F-10 | open — P3, P5 |
| F-11 | open — items 1, 2, 5 |
| F-12 | closed |
| F-13 | closed |

### findings (revision_2, charter-global; full member lists)
- **R2-F-02 SOURCE-POLICY RED (XF C.16/C.18)** — members: P1 vs base partial-month sentence (discharge/death month billed actual_notice).
- **R2-F-05 SOURCE-FACTOR RED (XF A.7/A.8)** — members: actual_part_a_days_out, reconciled_part_a_days_out, pending_part_a_days_out (A.7); actual_coinsurance_day_price, reconciled_coinsurance_day_price, pending_coinsurance_day_price (vacuous third tier).
- **R2-F-06 SOURCE-FACTOR RED (XF E.27/E.29, realism)** — members: actual_held_day_limit, reconciled_held_day_limit, pending_held_day_limit (latest-booking tier governs every held day; ignores day_payer, prior-month and year-to-date usage); pending_funds_applied tier 2 (allowance absorbed into patient pay).
- **R2-F-07 RED (XF A.1/A.2)** — members: pending_balance_carried_in reads three factors through `pending_estimate` (A.1); P3 `pension_tier` / `kept_tier` duplicated selection (A.2).
- **R2-F-09 SOURCE-POLICY RED (XF B.11/B.13, realism)** — members: P2/P4 admission taken from the latest episode in a two-episode month (double removal); P2/P4 discharge-elsewhere reservation counted by both the held-day and departure schedules (double removal); P2/P4 non-Medicare admissions undetected after the base partial-month clause was retired.
- **R2-F-10 RED (XF A.3)** — members: P3 assembly sentence; P5 assembly sentence; P5 overwrite 1 `replaced_by`.
- **R2-F-11 RED (XF B.11/B.12)** — members: declined/released hold keyed to list order (P1, P2, P4); departure first match unstated (P2, P4); P5 latest booked coinsurance not restricted to the active coverage.
- Observations: O-06 (no pending accrual seeded for pending months) persists; P3 framing clause "a second deposit in a month is a correction or back payment smaller than the month's benefit" asserts a fact no record holds (MX makes the figure order-safe, no consequence); P3 VA-tier payee keeps PNA + 90 from the Social Security benefit although the protected VA amount is not paid into that account (shifts who pays, not how much).

## closing_checklist (revision_2)
- Files 0.md, 1.md carry revision_2; scopes unchanged (task 0 = P1, P2, P3; task 1 = P4, P5), disjoint and complete; trees: task 0 n=2 (2 value_input), task 1 n=1 (1 value_input), owner=user roots, acyclic; both re-derivations equal GT on every scored value and every factor_sensitivity figure.
- Not closed: R2-F-02, R2-F-05, R2-F-06, R2-F-07, R2-F-09, R2-F-10, R2-F-11. Gates as in the snapshot above (all OK).

VERDICT revision_2: task0=RED:T0-R2-1,T0-R2-2 task1=RED:T1-R2-1,T1-R2-2 charter=R2-F-02,R2-F-05,R2-F-06,R2-F-07,R2-F-09,R2-F-10,R2-F-11

## revision_3

### entry (2026-10-22T15:1xZ)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh medicaid_pending_and_patient_pay 3` → "== snapshot medicaid_pending_and_patient_pay round 3 at 2026-10-22T15:05:40"; [check_extended] rc=0 :: EXTENDED OK; [check_task_tools] rc=0 :: TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 :: REPLAY OK; [check_solvability] rc=0 :: SOLVABILITY OK; [check_compute] rc=0 :: COMPUTE OK; [check_grounding] rc=0 :: GROUNDING OK; [check_cross_fire] rc=0 :: SCOPE OK.
- Hashes: task_tools.py 711c350ad51d7f8c2fc152ca4d0f0c2a0b96ae4412332f78cff103b6051f62ee (unchanged since revision_2 → § action_binding_and_uuids / docstrings of revision_2 carried forward); medicaid.extended.yaml 06ac7223e95f573ce37c33aa9d3b2ff14b56eeaf39442fc3b74394a196820a60 (changed → re-derived); task0.view 2202436b…6fae; task1.view 653d587c…0590.
- contamination_disclosure: GT seen in revisions 1–2; the worklog "REWORK round 3" section (claims, T1/T2 table with gold figures, probe table) read before recomputation. Per-task figures below are re-checks, not blind answers.
- Base section byte-identical to blueprint/products/medicaid.yaml.

### sweeps (re-derived)
- Every compute_basis quote, baseline sentence, `replaced_by`, `policy_source` verbatim in its rule; every `superseded_clause` verbatim in its base policy; every gate binding exists (0 misses). Transitive factor-read scan: no factor binding reads another factor's binding in any policy (A.1 PASS; P5 credit cap now on the plain `base_estimate`). A.2: P3 reads the funds account once (`funds_tier`, `funds_authorization`, "The resident's funds account is the resident's account in status active") — PASS. A.3: all five assembly sentences generic ("Each schedule … says where that figure enters") and P5 overwrite 1 `replaced_by` "the base estimate figure as the schedules below change it" — PASS. B.10 rounding sentences match. Tie rule stated in P1/P2/P4 ("Where two records share the latest date a schedule reads by, the one posted first is read"). Trust parameter `medicaid_pna_retained` and bed-hold parameter `resident_pays_all_held_days` exist in their charters.
- Decoy / absent-record check of new or changed reads:
  - P2/P4 census identity (accrual days + booked held days − reversals + latest declined span + latest released span + pre-admission days + days after a discharged-elsewhere bed's last held day = calendar days, one reservation): a second declined/released leave, a second hold, a non-Medicare admission, a missing accrual or a double-counted day breaks the identity and sends the month to the base cost (days in the center × rate, partial-month clause restated). Decoys checked: older declined leave of another month (reads latest → this month's leave unread → identity fails → base), two-episode month (admission days overlap Part A days? — no: the identity counts census days, Part A days are in-center days, so a double removal of admission + Part A days is NOT caught; see R3-F-09 item c), absent return date (span to month end). PASS for the members the identity covers.
  - P1 scope (`one_hold`, no ended coverage after the month), `ended_coverage` (latest last covered date, tie stated), SNF ABN latest by delivery on that coverage, `appeal_last_covered` (coverage in status under_appeal): absent records handled by stated fall-throughs.
  - P5 `latest_booked_coinsurance` now on the active coverage — R2 item 5 closed.
- The identity does not include Part A days, lapsed-certification days, appeal days or (P1) days after coverage; overlaps among those and the held/away schedules are listed under R3-F-09.

### override_declarations (re-derived)
- P1, P2, P4 retire "patient pay never exceeds the month's cost of care." with one identical sibling-naming `replaced_by` (C.15/C.17 PASS). P2/P4 retire the partial-month clause for months their review prices and restate it verbatim for every other month (PASS). P3/P5 refund overwrites unchanged (PASS). P5 estimate overwrite (PASS).
- **P1 contradicts itself on the partial-month clause** (it does not retire that clause; it restates and widens it): "A month of admission, discharge or death stays under the partial-month rule … ; a leave on which no bed is held ends the stay and the return from it is a readmission, so the month the resident leaves without a held bed and the month the resident comes back are such months." and then "The actual-month review posts no reduction for a month that carries a patient pay charge with charge basis partial_month or in which the case closed on the resident's discharge or death. The actual-month review prices any other month it covers where …". A month with an unheld leave (or a discharge whose case is still open at the review — closing waits for zero balances under medicaid_case_maintenance) carries an actual_notice charge, no partial_month charge and no closing in the month, so it is both "under the partial-month rule" and "priced" by P1. Same situation, two answers: October, actual 2245.90, MA rate 287.36, Part A days 1–20 on 1–20 Oct, coinsurance days 21–25 Oct billed to resident/Medigap, coverage ended 25 Oct with the SNF ABN on time, declined hospital leave 26–29 Oct, back 30 Oct, no holds → P1 cost 6 × 287.36 = 1724.16 → reduction 521.74; partial-month rule: days in the center 27 × 287.36 = 7758.72 ≥ patient pay → no reduction. P1 also has no schedule for unheld days, so the leave days are priced as Medicaid days. → R3-F-02 (round-2 R2-F-02 not closed).

### factor_ladders (re-derived)
| policy | factor | label | test | verdict |
|---|---|---|---|---|
| P1/P2/P4 | *_coinsurance_day_price | parameter | 3 operative values (0 / MA rate / booked rate), PA crossover cap is a real rule | PASS (R2 vacuous tier closed) |
| P1/P2/P4 | *_part_a_days_out | parameter (relabelled from method) | tiers = lapsed + appeal-days, lapsed, appeal-days, 0: on each tier's domain every tier equals `lapsed_certification_days + (appeal pending ? appeal_days_after : 0)`; the four tiers are one additive formula gated by "> 0 / present" tests on its own summands; the tiers differ in which inputs enter (a method difference), so the new label is also not honest | FAIL (R2-F-05 not closed for this member) |
| P1 | actual_unbillable_days_after_coverage (new) | method | shape PASS (last-covered span vs first-non-covered-to-delivery span) | realism FAIL (below) |
| P1/P2/P4 | *_privately_held_days (new) | method | leave-start span vs private-start span vs none; uses the bed-hold tier parameter and the hold's own dates | PASS (R2-F-06 held-limit member closed) |
| P2/P4 | *_unheld_leave_days, *_days_outside_stay | method | PASS (latest-by-date reads guarded by the identity) | PASS |
| P3 | payee_benefit_applied / authorized_pension / amount_kept / balance_carried | m / p / p / m | PASS; amount_kept now keeps PNA plus tier allowances the payee pays out (real) and no VA amount | PASS |
| P5 | projected_coinsurance / premiums / interest / funds_applied / balance_carried_in | m / p / p / p / m | PASS; funds tier 2 now benefit less PNA (R2-F-06 member closed) | PASS |
- Realism of actual_unbillable_days_after_coverage: it takes out of an approved case's Medical Assistance cost of care the days after Part A ended "that the resident may not be billed for" when no SNF ABN (or a late one) is on file. The SNF ABN governs whether the center may bill the beneficiary privately for extended care Medicare is not expected to cover (medicare_evt_snfabn: "Before extended care that Medicare is not expected to cover is billed to the resident …"); it does not govern Medical Assistance coverage of nursing-facility days for an eligible resident, and patient pay is the resident's income contribution toward those MA days, not a private bill for extended care. Under this factor a dual-eligible resident whose Part A ended mid-month with no ABN on file (the normal case when Medical Assistance takes over) has every remaining day of the month removed from the cost of care. → R3-F-06.
- Counts after strike-outs: P1 4 declared → part_a and unbillable struck → 2 (< 4). P2 5 → 4. P4 5 → 4. P3 4. P5 5.

### revision_2 → revision_3 status
| id | status |
|---|---|
| R2-F-02 | open (P1 self-contradiction, above) |
| R2-F-05 | partly closed — coinsurance vacuous tier closed; part_a_days_out (×3) open |
| R2-F-06 | closed for held-day limit and P5 funds tier 2; new realism member: P1 unbillable days (R3-F-06) |
| R2-F-07 | closed (A.1, A.2) |
| R2-F-09 | partly closed — discharge-elsewhere overlap fixed (days after last held day), two-episode/non-Medicare admissions sent to base by the identity; overlaps outside the identity remain (R3-F-09) |
| R2-F-10 | closed |
| R2-F-11 | closed (latest-by-date reads with stated ties, decoys break the identity → base; P5 coverage filter) |

### findings (revision_3, charter-global; full member lists)
- **R3-F-02 SOURCE-POLICY RED (self-contradiction / C.16)** — members: P1 for (a) a month the resident left without a held bed, (b) the month the resident came back from such a leave, (c) a month of discharge or death whose case was not closed inside that month. Not exercised by task 0's October.
- **R3-F-05 SOURCE-FACTOR RED (ladder not real / label)** — members: actual_part_a_days_out, reconciled_part_a_days_out, pending_part_a_days_out.
- **R3-F-06 SOURCE-FACTOR RED (realism, XF E.27)** — member: actual_unbillable_days_after_coverage (moves task 0's scored values).
- **R3-F-09 SOURCE-POLICY RED (double removal outside the census identity, XF B.11)** — members: (a) P1/P2/P4 appeal days "after that last covered date" also taken out as privately held days, unheld leave days (P2/P4) or days after a discharged-elsewhere bed (P2/P4) when those fall after the appealed last covered date; (b) P1 days after an ended coverage also taken out as privately held days (e.g. coverage ended 10 Oct with no ABN, Medicaid reserved bed 15–31 Oct with private extension from 30 Oct → 30–31 Oct removed twice); (c) P2/P4 a two-episode month where the latest episode's skilled admission falls after Part A days of the first episode: the pre-admission span counts those Part A days, which the standard pricing already takes out or prices — the identity counts census days only, so it does not catch it. Not exercised by either task world.
- Observations: task 0 September books Sep 24–30 as benefit days 21–25 although Sep 18 (benefit-band 1–20) was reversed as uncertified on the same posting date; under medicare_agg_benefit_period ("net covered days booked earlier … plus one") Sep 24 can read as benefit day 20 — the medicare charter does not say whether a later reversal renumbers; affects P2's coinsurance/full-coverage split (5/19 vs 4/20) but not P2's scored 2245.90 (cost stays 0.00 either way, coinsurance price 0). Pending accruals now seeded (O-06 closed); task 0 accrual counts Part A days at the private rate, as the base accrual sentence literally requires.

## closing_checklist (revision_3)
- Scopes unchanged and disjoint; trees hold (task 0 n=2, 2 value_input; task 1 n=1, 1 value_input; owner=user roots; acyclic); re-checks equal GT on every scored value and every factor_sensitivity figure (task files).
- Not closed: R3-F-02, R3-F-05, R3-F-06, R3-F-09. Gates OK per snapshot.

VERDICT revision_3: task0=RED:T0-R3-1,T0-R3-2 task1=RED:T1-R3-1 charter=R3-F-02,R3-F-05,R3-F-06,R3-F-09

## revision_4

### entry (2026-10-22T17:4xZ)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh medicaid_pending_and_patient_pay 4` → "== snapshot medicaid_pending_and_patient_pay round 4 at 2026-10-22T17:39:41"; [check_extended] rc=0 :: EXTENDED OK; [check_task_tools] rc=0 :: TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 :: REPLAY OK; [check_solvability] rc=0 :: SOLVABILITY OK; [check_compute] rc=0 :: COMPUTE OK; [check_grounding] rc=0 :: GROUNDING OK; [check_cross_fire] rc=0 :: SCOPE OK.
- Hashes: task_tools.py 72f24f95890feaca721f2051461adcfd103161258ad704c03a32b024f91aa04c; medicaid.extended.yaml 7903dadb3d6ee252796d83572c5d5bd9c37118308c875d5010b7b6084e5f48ac; task0.view 92c820a4…5ef7; task1.view 98b926a0…4f2e. Both sources changed → re-derived.
- contamination_disclosure: GT seen in revisions 1–3; worklog "REWORK round 4" (claims, T1/T2 table with gold, probes) read before recomputation. Re-checks, not blind answers.
- Coordinator ruling applied: half-up rounding computed as RND(x + 0.000000001, 2) on non-negative values is DSL-KNOWN (not RED).
- Base section byte-identical to blueprint/products/medicaid.yaml.

### sweeps and XF recipe (re-derived, all five policies)
- B.9/C: compute_basis quotes, baseline sentences, `replaced_by`, `superseded_clause`, `policy_source` verbatim; gates exist (0 misses). C.15/C.17: cost-clause `replaced_by` identical across P1/P2/P4, partial-month `replaced_by` identical across P2/P4.
- A.1 transitive scan: no factor binding reads another factor's binding (PASS). A.2 (P3 single funds-account selection) PASS. A.3 generic assembly sentences PASS. A.4 order stated (P3/P5 "combined first … after that"; P1 hospice share after day removal). A.7 method tiers: actual_days_after_coverage (ABN first non-covered date vs under-appeal last covered date), *_declined_hold_days (declined leave start vs ran-out end date), *_released_hold_days (release date vs unpaid/maximum private-hold end date), *_days_outside_stay, P3/P5 methods — distinct inputs; "none" tiers non-zero for the other formulas on their domains (unclipped spans) — PASS. Parameters (coinsurance price; hospice share start; privately held start; P3/P5 parameters) select distinct values — PASS.
- B.10/B.11/B.12: ties stated ("the one posted first"); P1 unheld days counted for every declined/released/expired reservation exactly (day-string counts; leaves of one resident are disjoint); P2/P4 latest-by-date reads guarded by the census identity plus "the month's Part A days were all booked by the resident's coverage with the latest coverage start" (closes R3-F-09 c). P5 coverage reads on the active coverage.
- D (tools): uuid8s unchanged; no factor id ⊂ tool name; imports `decimal` and `erlbench` only (no time/datetime/random/uuid/secrets substring); bodies round with exact Decimal half-up, refuse non-positive amounts, render two decimals; docstrings carry no ordering word, no other tool, no example value. PASS.
- E (realism): actual_days_after_coverage now takes out only days the resident pays under an SNF ABN option 1/2 (medicare_evt_snfabn: "the resident pays") or days Medicare is still deciding under a timely expedited review; no-notice and option-3 days stay Medicaid days (R3-F-06 closed). actual_hospice_share_start prices hospice days at the tier's room-and-board share (95 % of the NF rate, 42 USC 1396a(a)(13)(B); base `hospice_patient_pay_credit`) — real. Lapsed-certification days in the standard (provider-liable under the medicare base) — real.
- T1/T2: every factor of both worlds moves its score alone (task files); T2 worlds in the worklog checked against the formulas (each named factor leaves its fall-through with others at baseline and moves the result) — PASS.

### decoy / absent-record check of new or changed reads
- P1 unheld days: decoys of other months, unreturned leaves, several leaves in the month — counted exactly (PASS).
- P1 settled-partial test (`month_settled_partial`): partial_month charge, cost_of_care_cap already posted, case closed on discharge/death, latest-ended coverage ended on discharge/hospital transfer/death, discharged-elsewhere bed in the month. **Absent-record member left**: a discharge or death recorded on the resident's funds account (trust_accounts.conveyance_trigger_date / conveyance_reason "discharged" or "deceased" — "discharge date or date of death that started conveyance") while the case is still open (closing waits for zero balances), with no Medicare coverage ending and no bed hold that month. P1 prices such a month although its own rule keeps "a month of admission, discharge or death … under the partial-month rule". Example: October actual 2245.90, MA rate 287.36, no Part A, discharged home 5 October (conveyance_trigger_date 2026-10-05, reason discharged), case open: P1 cost 31 × 287.36 → no reduction; partial-month rule 4 × 287.36 = 1149.44 → reduction 1096.46. → R4-F-02 (residual of R3-F-02).
- P1 hospice share: `hospice_days = MN(hospice_share_days, medicaid_days)` prices the first-counted Medicaid days at the hospice share, which is exact only when every day taken out falls before the election. The scope guards keep held days and the after-coverage span before the election, but not days away with no bed held (nor lapsed-certification or Part A days) after it. Example: hospice elected 10 October, coverage ended 5 October (days 1–5 resident-billed coinsurance, price 0), declined hospital leave 20–27 October (back 28 October): Medicaid days 18, hospice share days 22 → all 18 priced at 95 % (4913.86); actual composition is 4 full days (6–9 Oct) + 14 hospice days = 4971.33 — cost understated by 57.47; with a charge of 4950.00 the reduction would be 36.14 instead of 0.00. → R4-F-09.
- P2/P4: decoys (later or second declined/released/ran-out/private-ended record, second coverage episode, absent accrual) break the identity or the bookings test → base; PASS.

### revision_3 → revision_4 status
| id | status |
|---|---|
| R3-F-02 | partly closed — unheld-leave months no longer called partial months; discharge/death records read; residual: discharge/death recorded only on the funds account (R4-F-02) |
| R3-F-05 | closed (part_a_days_out removed; lapsed days in the standard) |
| R3-F-06 | closed |
| R3-F-09 | closed for (a) (b) (c); new member in the hospice share (R4-F-09) |

### findings (revision_4, charter-global; full member lists)
- **R4-F-02 SOURCE-POLICY RED (self-contradiction / C.16)** — member: P1 settled-partial test does not read a discharge or death recorded on the funds account (conveyance trigger), so such a month is priced instead of being left to the partial-month rule P1 restates. Not exercised by task 0.
- **R4-F-09 SOURCE-POLICY RED (B.11 overlap)** — member: P1 hospice room-and-board share applied to `MN(hospice share days, Medicaid days)` with no guard against days away with no bed held (or lapsed-certification / Part A days) falling after the hospice election. Not exercised by task 0 (all removed October days precede 25 October).
- Observation carried: September benefit-day numbering after a same-day uncertified reversal (medicare charter silent); P2's scored value is 0.00-cost either way.

## closing_checklist (revision_4)
- Scopes unchanged and disjoint; trees hold; re-checks equal GT on every scored value and every factor_sensitivity figure. Task 1's policies (P4, P5) carry no open member. Open: R4-F-02, R4-F-09 (both on P1, task 0's policy). Gates OK.

VERDICT revision_4: task0=RED:T0-R4-1 task1=PASS charter=R4-F-02,R4-F-09

## revision_5

### entry (2026-10-22T17:5xZ)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh medicaid_pending_and_patient_pay 5` → "== snapshot medicaid_pending_and_patient_pay round 5 at 2026-10-22T17:46:10"; [check_extended] rc=0 :: EXTENDED OK; [check_task_tools] rc=0 :: TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 :: REPLAY OK; [check_solvability] rc=0 :: SOLVABILITY OK; [check_compute] rc=0 :: COMPUTE OK; [check_grounding] rc=0 :: GROUNDING OK; [check_cross_fire] rc=0 :: SCOPE OK.
- Hashes: task_tools.py 72f24f95890feaca721f2051461adcfd103161258ad704c03a32b024f91aa04c (unchanged → revision_4 tool conclusions carried forward); medicaid.extended.yaml d63e4efdb69205a6ed9edfd5e82228c7ff6ec61c875dc86d1b7107f2695a66e5 (changed); task0.view 92c820a4…5ef7 and task1.view 98b926a0…4f2e (unchanged → revision_4 per-task derivations carried forward, re-checked against the new P1 guards below).
- contamination_disclosure: worklog "REWORK round 5" read before this check; GT seen in earlier rounds.
- Per-policy fingerprints recorded this round for later carry-forward (sha256 of the sorted policy object, first 12): P1 7f9b92d81090, P2 9c65da2af9a5, P3 f9fe67c9913d, P4 aebfe6f23fbe, P5 165630009f3c. The reworker reports only P1 changed; P2–P5 re-swept (below) and their gold/sensitivity figures are unchanged.

### sweeps and XF recipe
- All five policies: compute_basis quotes, baseline sentences, `replaced_by`, `superseded_clause` verbatim; overwrites unchanged in shape; transitive factor-read scan clean (A.1); factor counts 4/5/4/5/5. Rounding per the coordinator ruling (DSL-KNOWN). Remaining XF points as revision_4 (PASS).
- P1 changes: (1) settled-partial test now also reads the funds account's conveyance trigger (`XLATEST('trust','trust_accounts','conveyance_trigger_date', …, conveyance_reason='discharged'|'deceased')`) — trust added to cross_category; (2) a month with a hospice election inside it is priced only where the month's latest Part A `to_date` is before the election, no day away with no bed held falls in the month, the ABN first non-covered date is before the election and an appealed last covered date leaves its span starting before the election. With those guards every day the schedules take out precedes the election, so `MN(hospice share days, Medicaid days)` is exact; an election before the month makes every Medicaid day a hospice day (also exact). **R4-F-09 closed.**
- Task 0 October re-checked under the new guards: latest Part A to_date 2026-10-23 < 2026-10-25 election, no unheld day, ABN first non-covered 2026-10-24 < election, no appeal, no conveyance → priced, 334.96 unchanged. GT figures in tasks/0.json and tasks/1.json unchanged (334.96 / 2245.90 / 231.64; 1073.70 / 177.38; every factor_sensitivity figure as revision_4).

### decoy / absent-record check of the new read
- Conveyance read: the rule says "in which the resident's funds account records the resident's discharge or death as the start of conveyance" (any account); the compute keeps only the latest trigger date per reason. Decoy: resident discharged 5 October (account 1 conveyance, reason discharged), readmitted 20 October with a new funds account, discharged again 2 November (account 2 conveyance) — at the November review of October the latest "discharged" trigger is 2 November, so October is not recognised as a month of discharge and P1 prices it. The same latest-record-only pattern recognises a month of discharge in two older reads of the same test: `discharged_elsewhere_last_held` (rule: "a held bed's last held day fell where the hospital discharged the resident elsewhere" — any bed; compute: latest end date only) and `coverage_left_center` (rule and compute: only the coverage with the latest last covered date — an earlier episode ended on discharge in the month is ignored when a readmission episode ends later, and the month then falls to P1's base fallback, which counts the days after the discharge as days in the center). In each case P1 computes its own figure for a month its own restated partial-month rule governs, and the two figures can differ. Example (conveyance member): October actual_notice charge 5600.00 (patient pay of a resident with income near the cost of care), MA rate 287.36, discharged home 5 October (account 1 conveyance, reason discharged), readmitted 20 October on a new Medicare episode that ends with a second discharge on 2 November (account 2 conveyance); at the review on 9 November P1 does not see October as settled (latest discharged trigger is 2 November) and, the new episode's last covered date being after October, falls to its base fallback: (31 − 0 held − 0 unheld) × 287.36 = 8908.16 → no reduction; the partial-month rule P1 restates gives days in the center 4 + 12 = 16 × 287.36 = 4597.76 → reduction 1002.24. → R5-F-02.

### revision_4 → revision_5 status
| id | status |
|---|---|
| R4-F-02 | partly closed — funds-account conveyance now read; residual: latest-record-only recognition of a month of discharge (R5-F-02) |
| R4-F-09 | closed |

### findings (revision_5)
- **R5-F-02 RED (XF B.12 decoy, residual of R4-F-02)** — members (all in P1's settled-partial test): `conveyance_discharged_on` / `conveyance_deceased_on` (latest trigger per reason, rule says any account); `discharged_elsewhere_last_held` (latest end date, rule says any held bed); `coverage_left_center` (latest-ended coverage only, so an earlier episode ending on discharge inside the month is not seen). Not exercised by task 0 (one funds account with no conveyance, one coverage, no discharged-elsewhere reservation).

## closing_checklist (revision_5)
- Scopes, trees and GT agreement as revision_4. Task 1 (P4, P5): no open member. Open: R5-F-02 (P1). Gates OK.

VERDICT revision_5: task0=RED:T0-R5-1 task1=PASS charter=R5-F-02

## revision_6

### entry (2026-10-22T18:1xZ)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh medicaid_pending_and_patient_pay 6` → "== snapshot medicaid_pending_and_patient_pay round 6 at 2026-10-22T18:07:32"; [check_extended] rc=0 :: EXTENDED OK; [check_task_tools] rc=0 :: TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 :: REPLAY OK; [check_solvability] rc=0 :: SOLVABILITY OK; [check_compute] rc=0 :: COMPUTE OK; [check_grounding] rc=0 :: GROUNDING OK; [check_cross_fire] rc=0 :: SCOPE OK.
- Hashes: task_tools.py 72f24f95…a04c (unchanged); medicaid.extended.yaml a7b484d226b28f69bf02f879292910f221088c3ae3d6778cf51a26683b962dae (changed); task0.view 92c820a4…5ef7 and task1.view 98b926a0…4f2e (unchanged).
- Per-policy fingerprints: P1 f7b9b0ceb143 (changed from 7f9b92d81090); P2 9c65da2af9a5, P3 f9fe67c9913d, P4 aebfe6f23fbe, P5 165630009f3c — identical to revision_5, so their revision_4/5 conclusions carry forward by fingerprint.
- contamination_disclosure: worklog "REWORK round 6" read before this check; GT seen in earlier rounds.

### P1 change and checks
- New scope sentence (rule): "The actual-month review covers a resident who holds exactly one funds account and exactly one Medicare coverage episode, each counted in every status, and no bed-hold reservation that ended because the hospital discharged the resident elsewhere; for any other resident it posts no reduction, and the partial-month rule and the base rule on the month's cost of care apply as restated above." Compute: `resident_covered = funds_account_count == 1 and coverage_episode_count == 1 and discharged_elsewhere_count == 0`, counts summed over every status of trust_accounts (5 statuses) and medicare_coverages (7 statuses) — complete enumerations per db_schema; exact XCOUNT on end_reason. Coarse exact record test (XF F.31); no purpose clause; restated base clauses present (C.15).
- Inside the scope the settled-partial reads are single-record: one funds account (conveyance trigger per reason), one coverage episode (ended coverage); the discharged-elsewhere read is dropped (none in scope). The R5-F-02 decoys (second account with an in-month conveyance, readmission episode, second discharged-elsewhere reservation) now take the resident out of scope, where P1 posts nothing and the restated base rules govern. Absent records: no funds account or no coverage episode → out of scope (stated "exactly one"). **R5-F-02 closed.**
- Sweeps on P1: compute_basis quotes, baseline sentences, `replaced_by`/`superseded_clause` verbatim; every binding has a basis; transitive factor-read scan clean; cross_category medicare/bedhold/trust. Factor set unchanged (coinsurance price, hospice share start, privately held start — parameters; days after coverage — method); A.7/T2 conclusions of revision_4/5 hold (the reworker's T2 worlds are task-0 copies with one account and one episode, so in scope).
- Task 0 world: one funds account (d74bfc32…, active), one coverage episode (c93e594f…, coverage_ended), no discharged-elsewhere reservation → in scope; October re-check 334.96, P2 2245.90, P3 231.64; tasks/0.json and tasks/1.json writes and every factor_sensitivity figure unchanged (334.96 / 2245.90 / 231.64; 1073.70 / 177.38).

### XF recipe (all five policies)
- A (1–8), B (9–14), C (15–18), D (19–26), E (27–30), F (31–32): no open member. Rounding per the coordinator ruling (DSL-KNOWN).

### revision_5 → revision_6 status
| id | status |
|---|---|
| R5-F-02 | closed (single-account / single-episode / no-discharged-elsewhere scope) |

## closing_checklist (revision_6)
- Per-task files 0.md and 1.md carry revisions 1–6; old revisions untouched.
- Extended policies fully covered; scopes disjoint (task 0: P1, P2, P3 and their three tools; task 1: P4, P5 and their two tools); task tools closed, uuid8s independent and frozen.
- Problem trees: task 0 n=2 (2 value_input, owner=user root), task 1 n=1 (1 value_input, owner=user root); difficulty graph acyclic; every edge load-bearing and false at the opening.
- Factors: P1 4 (3 parameter, 1 method), P2 5 (2 p, 3 m), P3 4 (2 p, 2 m), P4 5 (2 p, 3 m), P5 5 (3 p, 2 m); each task has multi-source and cross-difficulty factors; every factor moves its task's score against an honest baseline and the baseline alone gives a definite non-gold number (task files).
- Unique solution: re-checks equal GT on every scored value, owner and order.
- Gates re-run on the final form by the coordinator snapshot above: 7/7 OK.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

### entry (2026-10-22T22:1xZ)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh medicaid_pending_and_patient_pay 7` → "== snapshot medicaid_pending_and_patient_pay round 7 at 2026-10-22T22:06:39"; [check_extended] rc=0 :: EXTENDED OK; [check_task_tools] rc=0 :: TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 :: REPLAY OK; [check_solvability] rc=0 :: SOLVABILITY OK; [check_compute] rc=0 :: COMPUTE OK; [check_grounding] rc=0 :: GROUNDING OK; [check_cross_fire] rc=0 :: SCOPE OK.
- Hashes: task_tools.py 72f24f95…a04c (unchanged); medicaid.extended.yaml 25f69f273aa63e70039f24c1d89ba91afc6fac1db2b23e2da954d14dcb9d5406 (changed); task0.view 92c820a4…5ef7, task1.view 98b926a0…4f2e (unchanged).
- Fingerprints: P1 c53650b2572f, P2 746cb1ae1454, P3 bf429dff33e9, P4 a327e55cff0b, P5 22cb4ea313c4 — all five changed since revision_6 → each re-swept.
- Read: audits/render_source/medicaid_pending_and_patient_pay/render_r1.md in full; worklog "REWORK round 7" (disclosed). GT seen in earlier rounds; tasks/*.json writes and every factor_sensitivity figure re-read and unchanged (334.96 / 2245.90 / 231.64; 1073.70 / 177.38).

### renderer items
| item | check | status |
|---|---|---|
| M1 P5 pending_funds_applied floor | rule "the latest benefit received less the personal needs allowance, never below zero"; ladder tier 2 "… less P('personal_needs_allowance_monthly'), never below zero"; compute `MX(0, latest_payee − PNA)` | closed |
| M2 P1 hospice share inside-month branch | rule "where the case is on that tier and the hospice election date falls inside the month" = ladder tier 2 = compute `on_hospice_tier and …` | closed |
| S1 P5 grouping | "100 less the larger of 20 and the total of the benefit days already used … (… prior skilled nursing days in the period, none where not recorded, plus its covered days used) and the days from the first day of the current month to the first day of the coming month, never below zero" = `MX(0, 100 − MX(20, used + DAYS(...)))` | closed |
| S2 tie sentences P3, P5 | P3 "Where two records share the latest date a schedule reads by, the one posted first is read."; P5 same sentence inside its opening paragraph | closed |
| S3 P2/P4 unpaid vs maximum tie | rule "Where a hold that ended unpaid and one that ended at its maximum share the latest end date, the one that ended unpaid is read" = compute choice | closed |
| S4 P3 coming patient pay edges | rule "…, or nothing where the case carries no estimate charge either; a current notice with no effective date recorded counts as taking effect after the first day of the coming month" = compute (`or 0`, `or '9999-12-31'`) | closed |

### class sweeps (all five policies)
- Floors/caps (M1 class): every MX/MN in each compute listed and matched to a rule phrase — P1 privately held span (clipped to the month), unheld days and base days in the center ("never fewer than zero"), Medicaid days ("never fewer than zero such days"), hospice days ("never more than the days from that first day to the month's end"), result ("never below zero"); P2/P4 spans clipped "of the month", Medicaid days, lesser-of actual patient pay, result; P3 payee MX (larger of), funds total ("never below zero"), credit cap ("never more than the patient pay the coming month will carry"), result; P5 estimate floor, funds tier 2 (M1), days-left floor, credit cap on the base estimate, result. No unstated floor or cap found.
- Branch conditions (M2 class): every ladder tier's condition compared with its rule branch and compute branch for all 23 factors; the round-7 status gates are stated in rule and computed (P2 eligible, P3 eligible, P4 pending, P5 pending — "any other status gives nothing / reduces nothing / reduction is zero"). No tier condition present in one face and absent from another found.
- Ties and absent records (S2–S4 classes): tie sentence present in all five rules; P2/P4 unpaid-vs-maximum tie stated; absent-record defaults stated — P2 notice with no effective date, P3 no actual or estimate charge, P3 allowance not recorded, P5 figures not recorded (zero), P5 no requested eligibility date ("from the coming month"), P5 no booked coinsurance ("nothing where none was booked"), P5 prior SNF days not recorded ("none").
- Sweeps: compute_basis quotes, baseline sentences, `replaced_by`/`superseded_clause`, prerequisite sentences verbatim; every binding has a basis; transitive factor-read scan clean; factor sets and labels unchanged (P1 3p/1m, P2 2p/3m, P3 2p/2m, P4 2p/3m, P5 3p/2m). XF recipe A–F: no open member. Rounding per the coordinator ruling (DSL-KNOWN).
- T1/T2: the status gates hold in both worlds (task 0 eligible, task 1 pending) and in the reworker's T2 scratch copies; every T1 figure unchanged (task files, revision_4).

## closing_checklist (revision_7)
- As revision_6; all renderer items closed with their classes; gates 7/7 OK on the final form.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

### entry (2026-10-23T06:2xZ)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh medicaid_pending_and_patient_pay 8` → "== snapshot medicaid_pending_and_patient_pay round 8 at 2026-10-23T06:20:34"; [check_extended] rc=0 :: EXTENDED OK; [check_task_tools] rc=0 :: TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 :: REPLAY OK; [check_solvability] rc=0 :: SOLVABILITY OK; [check_compute] rc=0 :: COMPUTE OK; [check_grounding] rc=0 :: GROUNDING OK; [check_cross_fire] rc=0 :: SCOPE OK.
- Hashes: task_tools.py 72f24f95…a04c (unchanged); medicaid.extended.yaml 07b3e89055ff4c727a4ad6bc213def6df68c6b53df7631873981fe1a1131ac67 (changed); task0.view 92c820a4…5ef7, task1.view 98b926a0…4f2e (unchanged).
- Fingerprints: P1 c53650b2572f, P2 746cb1ae1454, P4 a327e55cff0b unchanged since revision_7 (carried forward); P3 aa84ce27749a and P5 7c15107bdc33 changed → re-swept.
- Read: audits/policy_kb/medicaid_pending_and_patient_pay/_kb_verdict.md (revision_1); worklog "REWORK round 8" (disclosed). GT seen earlier; tasks/*.json writes and every factor_sensitivity figure unchanged (334.96 / 2245.90 / 231.64; 1073.70 / 177.38).

### SRC-3 and its class
- P5 refund overwrite (`replaced_by` and rule): "that credit is instead applied to the coming month up to the base estimate figure" = factor pending_balance_carried_in "the credit is subtracted, but never more than the base estimate figure" = compute `MN(0 − case_balance, base_estimate)`. Closed. (The cap is also the realistic one: the coming pending month will be billed the base estimate, which the credit is applied against.)
- Class sweep — every overwrite or rule phrase stating a cap on the same quantity as a factor: P3 refund overwrite now "up to the patient pay the coming month will carry" = approved_balance_carried "never more than the patient pay the coming month will carry" = `MN(0 − case_balance, coming_patient_pay)`; P1/P2/P4 overwrites state no cap. Sibling `replaced_by` sentences of P3/P5 still name each other's case (C.17). No other member.
- Sweeps on P3/P5: compute_basis quotes, baseline sentences, `replaced_by`/`superseded_clause`, prerequisite sentences verbatim; transitive factor-read scan clean; factor sets unchanged. XF recipe A–F on P3/P5: no open member. Rounding per ruling.
- Other KB-verdict source items: SRC-1, SRC-2, SRC-4 concern where rendered text lives (placement), not a rule/compute or realism defect — not policy-side REDs. SRC-5: approved_amount_kept reads the trust tier parameter `medicaid_pna_retained` from the trust charter (blueprint/products/trust.yaml, Medicaid tiers true); the policy-side source is consistent — publication of that product's document is a KB-side matter. KB-1…KB-4 are renderer-side.

## closing_checklist (revision_8)
- As revision_7; SRC-3 closed with its class; nothing regressed (P1/P2/P4 fingerprints unchanged, scored values unchanged); gates 7/7 OK.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

### entry (2026-10-23T11:0xZ)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh medicaid_pending_and_patient_pay 9` → "== snapshot medicaid_pending_and_patient_pay round 9 at 2026-10-23T10:52:33"; [check_extended] rc=0 :: EXTENDED OK; [check_task_tools] rc=0 :: TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 :: REPLAY OK; [check_solvability] rc=0 :: SOLVABILITY OK; [check_compute] rc=0 :: COMPUTE OK; [check_grounding] rc=0 :: GROUNDING OK; [check_cross_fire] rc=0 :: SCOPE OK.
- Hashes: task_tools.py 72f24f95…a04c (unchanged); medicaid.extended.yaml 3b655b1fbfb5c46ffe52efd326c63183e484e000217cf3666eee1dee41871254; task0.view f3c00a15b8794bf5e76643496626bc97e9282dbe455e26163f63b43aa415bc86; task1.view bdd3ec08c55a920c809f703bb8ed18c71a65dcd48de8a9e9e840057f83d83adb (both worlds changed).
- Fingerprints: P1 c53650b2572f, P2 746cb1ae1454, P4 a327e55cff0b, P5 7c15107bdc33 unchanged since revision_8; P3 13e9bf2eed3a changed (only `rep_payee_transfer_day` dropped from its baseline params — no rule or compute change).
- Read: audits/policy_kb/medicaid_pending_and_patient_pay/_kb_verdict.md revision_3 (SEED-1…6, SRC-6); worklog "REWORK round 9" (disclosed); docs/trust (standing patient pay transfer, transfer computation, statement and resource-notice terms) to re-price seeded trust rows. GT seen in earlier rounds; tasks/*.json opened after the re-derivation below.

### seeded cross-product rows re-priced (both worlds)
- Task 0 Medicare: September days 1–20 on 3–23 Sep (18 Sep reversed as uncertified, posted 10-01, after the 09-30 charges); days 21–25 on 24, 25, 28, 29, 30 Sep (away 26 and 27 Sep, two midnights, back by the third day → one episode, SEED-1); coinsurance 5 × 217.00 × 25 % = 271.25 / 813.75 and payments; October days 25–45 on 1–23 Oct less 8–9 Oct (21) → 1139.25 / 3417.75; ABN option 1 for 24 Oct; covered days 45. Consistent with the booking-time numbering (SEED-3).
- Task 0 bed-hold: declined 15 Sep (back 16 Sep); Medicare-stay hold 26 Sep released 26 Sep (back 28 Sep), 1 held day booked 09-28 (the day the leave ends, SEED-5), charged 398.00 on 10-03 and paid; 8–9 Oct hold booked 10-10, charged 796.00 on 11-03.
- Task 0 trust: transfer 1954.50 on the October charge's due day 10-10 (charge 2245.90 less the 291.40 ACH naming it, within available 1999.50 less 45.00) mirrored as the rep_payee_transfer payment of 10-10; October interest ADB (2 × 216.00 + 7 × 1999.50 + 22 × 45.00)/31 = 497.37 → (497.37 − 50.00) × 0.4 % × 31/365 = 0.15; resource-limit notices 10-03 (1999.50) and 11-03 (2044.65), both at or above the Medicaid-tier notice level 1800.00 (SEED-6); balance 2108.85; November transfer due 11-10, after the frozen time (SEED-2).
- Task 1 Medicare: prior SNF days 47; October days 48–70 on 6–31 Oct less 22, 26, 27 Oct (23); reversal 20–21 Oct and its 217.00 adjustments posted 11-02 after the 10-31 charges (SEED-4); 23 × 217.00 × 50 % = 2495.50 each; covered 21; balance 4557.00. Accrual 23 days × 398.00 = 9154.00.
- Task 1 bed-hold: declined 22 Oct (back 23 Oct); Medicare-stay hold 26 Oct released 26 Oct (back 28 Oct), 1 day booked 10-28, charged 398.00 on 11-03.
- Task 1 trust: family check 1180.00, interest 0.28 ((913.55 − 100.00) × 0.4 % × 31/365), pension 388.00 on 11-01, no transfer before 11-10; balance 1568.28; non-Medicaid tier, no resource notice owed. Medicaid ledger: October ACH 1073.70 on 10-12, the daughter's 250.00 check on 11-03 toward November (persona updated to match).
- All rows match the published product rules. SEED-1…SEED-6 closed. SRC-6 (medicaid base "representative payee transfer day" vs trust base standing transfer "on the charge's due day") is a conflict between two frozen base charters — coordinator ruling BLUEPRINT-KNOWN; no extended rule states a transfer day (P3 dropped the parameter from its baseline list).

### gold re-derived (moved for both advances)
- Task 0: P1 October unchanged → 334.96 (in scope; election 25 Oct; latest Part A to_date 23 Oct; ABN first non-covered 24 Oct). P2 September: full-coverage 19, lapsed 1, coinsurance 5 (price 0), held 1 (26 Sep), declined 1 (15 Sep), released 1 (27 Sep), pre-admission 2; identity 25 + 1 + 1 + 1 + 2 = 30 ✓ → Medicaid days 0 → 2245.90. P3: coming 2229.70; funds MX(64.20, 1783.50) + 216.00 − 45.00 = 1954.50; case balance 6737.70 − (1954.50 + 291.40) = 4491.80 → after the two reductions 1910.94 owed (the November charge net of the October credit) → **2186.14**. Skip P1 → 2521.10; skip P2 → 4432.04.
- Task 1: P4 October: coinsurance 21 (price 0), lapsed 2, held 1, declined 1, released 1 (27 Oct), pre-admission 5; identity 23 + 1 + 1 + 1 + 5 = 31 ✓ → 1073.70. P5: days used 47 + 21 = 68 (+30) → 2 left → 217.00; estimate 953.38; funds 388.00; case balance 2147.40 − 1323.70 = 823.70 → after P4 −250.00 (credit from today's reduction, below the base-estimate cap) → **315.38**. Skip P4 → 1389.08.
- T1 (each factor alone at baseline): P2 1160.90 / 1958.54 / 1958.54 / 1958.54 / 1671.18; P3 3905.44 / 2402.14 / 2141.14 / 275.20 (standard 2165.50); P4 0.00 / 793.86 / 793.86 / 793.86 / 0.00; P5 532.38 / 218.98 / 315.10 / 703.38 / 565.38 (standard 1073.70); P1 as revision_4. All bear; T2 per the reworker's scratch worlds (charges raised to 12000.00 for P1/P4) consistent with the formulas.
- tasks/0.json and tasks/1.json: writes 334.96 / 2245.90 / 2186.14 and 1073.70 / 315.38, and every factor_sensitivity figure, equal the re-derivation.

### checks on the moved values
- Owed cross-product writes: the November standing transfers fall due 11-10 (after the frozen time); the published trust transfer tool writes no Medicaid payment, so no tool can move a scored read mid-conversation (E.30 PASS). Following the published transfer computation after the gold advance: task 0's 11-10 transfer nets the advance as a credit reaching the November charge (payments not naming it 4432.04 + reductions 334.96 + reconciliation 2245.90 − other charges 4491.80 = 2521.10 ≥ 2245.90) → 0.00, and the 12-10 transfer pays December less the 275.20 left of the advance; task 1's December transfer pays the base estimate less the 565.38 credit. Nothing is collected twice.
- Observation O-R9-1 (no RED): in task 0 the November benefit already received into the payee account stays there (the advance pays November from the son's side while the funds-account figure is attributed to December), so the account carries about one month's benefit above the 1800.00 notice level until the following transfers; the P3 rule gives this figure uniquely ("where the case's patient pay balance is owed, that balance is added").
- Sweeps: P3 change limited to its baseline parameter list; compute_basis quotes, baseline sentences, `replaced_by`/`superseded_clause`, prerequisite sentences verbatim in all five policies; transitive factor-read scan clean. XF recipe A–F: no open member. Rounding per ruling.

## closing_checklist (revision_9)
- Every routed item (SEED-1…SEED-6) closed; seeded cross-product rows match the published medicare, bed-hold and trust rules; moved gold re-derived and equal to GT; trees, factors and uniqueness hold; P1/P2/P4/P5 unchanged; gates 7/7 OK.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN
