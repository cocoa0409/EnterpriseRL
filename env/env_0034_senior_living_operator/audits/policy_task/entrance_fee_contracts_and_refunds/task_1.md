# Policy-task audit — entrance_fee_contracts_and_refunds / task 1

## revision_1

## source_derivation_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit). Round 1.
- Freeze time: 2026-10-05T09:25Z. Written before any task JSON of this difficulty was opened, and before task 0's GT was revealed: both derivations were frozen before the first reveal.
- Inputs and hashes: view `audits/_views/policy_task/entrance_fee_contracts_and_refunds/task_1.view.json` sha256 62bf8370ff0afd5b3a652551014be3f3cfcda25f4de3ff94c6b3b3add1ce12f4; `entrance.extended.yaml` c593bac6…3cc3339; `task_tools.py` 04a31a9c…a4e3336 (re-hashed, matching the MANIFEST).
- Fields permitted: `frozen_time`, `user_scenario`, `initial_state` (view), the extended charter, the task tool module, `blueprint/` (including `products/independent.yaml` for CPARAM `post_death_fee_days`), `erlbench/`, and the DSL primitives in `check_compute.py`. Fields masked: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`, and the worklog.
- contamination_disclosure: none.
- Recomputation: the same temporary /tmp script as task 0 (charter `compute` over the view's `initial_state` plus simulated tool effects), cross-checked by hand. Removed after the audit.

### policy_self_consistency (this task only)

- Charter-global conclusions are cited from `_difficulty.md` § policy_conflict_scan, § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences, § override_declarations, § factor_ladders, § findings.
- F-1: no consequence on this world. The plan is LifeCare Declining Balance with percentages 34.6 / 38.5, so the "0.0 plan → 0.00" base clause is not engaged.
- F-3 bears on this world through the seed. The ledger carries months 1-18 at 5,752.00 (2.0 % of 287,600.00, the plan rate) and months 19-23 (2025-08-20 … 2025-12-20) at 4,314.00 (1.5 %). Base S3 gives 2.0 % for every month and the extended rule's step-down speaks only of the final period. These rows are produced only by reading B of F-3 and contradict the plan rate of the base charter. Their consequence for this task is F-T1-2 below. The scored refund reads the ledger as it stands, and no policy or tool corrects past amortization, so they do not create a second scored refund.
- F-4: no collision on this world (plan rate 2.0 ≠ 1.5 ≠ 1.0).
- Handling time (each write evaluated after its own prerequisites, before itself):
  - final amortization on the opening world;
  - annual letter on the opening world or after the amortization (identical, 26,140.59 — it reads no amortization);
  - closing-year letter after the amortization (and after the annual letter, which it does not read);
  - estate release after all three.
- No real-world waits:
  - letters of administration are on file at the opening (`estate_documents_date` 2026-12-28);
  - the refund was due 2026-03-21 and is past due;
  - the agreement is already `refund_scheduled`;
  - all three prerequisite writes are agent records on the call, at the January 2027 letter run (frozen 2027-01-25), and the release is signed by the personal representative on the call.

### problem_chain

Walked from the root:

- Root: the executor wants "the estate's refund from his entrance fee contract to be paid out" → `entrance_ext_estate_refund_release` (owner = user, `release_estate_refund_4b5e42b1`).
- Root rule prerequisite sentences:
  1. "An estate refund is not released until the agreement's ledger carries an amortization entry for every month of occupancy that began on or before the termination date."
     - False at the opening. Occupancy 2024-02-20 and termination 2026-01-20, so month 24 begins 2026-01-20, on the termination date. The ledger's amortization rows stop at month 23 (`6a7458a0…`, 2025-12-20).
     - Resolved by `entrance_ext_final_period_amortization` ("A month of occupancy that began on or before the termination date and carries no amortization entry when the agreement terminates is amortized after the termination") via `book_final_period_amortization_cad149c9`.
     - Kind value_input: the entry lowers `refundable_amount`.
  2. "An estate refund is released only after the agreement's ledger carries the tax letter for the tax year in which the agreement terminated."
     - False. The tax letters on the ledger are tax_year 2023 (`2e806010…`) and 2024 (`ac30b805…`); there is none for 2026.
     - Resolved by `entrance_ext_closing_year_tax_letter` (the annual rule excludes the termination year) via `issue_closing_year_tax_letter_050bd78c`.
     - Kind state_gate.
- Closing-year letter's own sentences:
  1. The same amortization state, also false → final amortization. Kind value_input: it raises `amortization_in_year` 0.00 → 191.73 and the amortization entry count 23 → 24.
  2. "The tax letter for the year in which an agreement terminated is not issued until the agreement's ledger carries a tax letter for every earlier tax year in which entrance fee or independent living monthly fees were paid."
     - Earlier paid years are 2023 (deposit 2023-11-28), 2024 and 2025 (IL payments). There is no letter for 2025, so the state is false.
     - Resolved by `entrance_ext_annual_tax_letter`, whose tax year is "the year after the latest tax letter on the agreement's ledger" = 2025, via `issue_annual_tax_letter_ce10c97a`. Kind state_gate.
- final_period_amortization and annual_tax_letter carry no prerequisite sentence. Final amortization's eligibility holds (an unamortized month started on or before termination). The annual letter's holds: a January run, and the 2025 letter was missed in January 2026.
- Derived tree:
  - Nodes: release (root, user), final amortization (agent), closing letter (agent), annual letter (agent). n = 3 prerequisite problems.
  - Edges: release→amortization (value_input), release→closing (state_gate), closing→amortization (value_input), closing→annual (state_gate).
  - value_input edges = 2 ≥ max(3−1,1) = 2. Acyclic. Owner=user write: the root.
- Topological order: {final amortization, annual letter} (either order) → closing letter → release.
- Load-bearing runs:
  - Skip the final amortization: the closing letter is 1,308.49 instead of 1,385.18 (entrance share 0, entrance percentage 37.0 instead of 40.0), and the release is 151,658.08 instead of 151,465.50. Both value edges bear weight.
  - Skip the closing letter or the annual letter: the gated write's value is unchanged. These are state_gate edges whose sentence forbids the write, and the tree's value floor is met by the two value edges.
- Parallel edges: amortization and annual letter share no balance, cap or key. The annual letter reads only deposit/balance payments and other categories, and the amortization reads no tax letter. Both orders give the same terminal state; verified, the annual letter is 26,140.59 in both.
- No-wait: shown above.
- Tools do not judge prerequisites. The bodies of `book_final_period_amortization_cad149c9`, `issue_annual_tax_letter_ce10c97a`, `issue_closing_year_tax_letter_050bd78c` and `release_estate_refund_4b5e42b1` only read the agreement row for the balance/customer and write; none has a branch on status, letters or amortization.
- Customer raises only the root problem. The persona names no prerequisite. Her only reference to work is passive and conditional: "If the agent says some entries or paperwork on the account have to be completed or corrected before the refund can be released, say that is fine and they should go ahead". She asks nothing outside the charter and closes after the check number.
- Isomorphic to the charter's declared edges 2-5 (`_difficulty.md` § prerequisite_graph).

### task_independent_derivation

- Need/authorisation/timing: the caller, Allison Whitfield Brandt (representative on file, "the executor of his estate"), wants the estate refund paid out now by check to the estate at the address on file (`c/o Allison Brandt, 2207 Sorrel Creek Court, Apex, NC 27523`). She consents to the agent completing entries, and signs the release herself when handed the step. Identity is established with the decedent's DOB 1937-09-14 + SSN last4 7861 (profile e462fa1d…). Clear and unique.
- Now / wait / refuse: act now.
  - The agreement `ea7a091e-791d-4d44-9d64-cd344fe3adc5` is refund_scheduled, payee estate, letters on file 2026-12-28.
  - The plan is LifeCare Declining Balance, not contingent on re-occupancy, so the refund was due 60 days after 2026-01-20 = 2026-03-21.
  - No refund payment row exists. The IL residency `d6472373…` account balance is 0.00, and there is no AL/MC residency, refurbishment or offset.
- Step 1 — final-period amortization (opening world):
  - Last amortized month start 2025-12-20; DAYS to termination 2026-01-20 = 31, −30 = 1.
  - Vacate 2026-02-02 is not before termination, and the termination reason is death, so the death date counts: 2 days.
  - Share 2/30. 23 entries → step 1.5 %. Death + vacated 13 days after → reduction 0.5, so 1.0 %.
  - 287,600 × 1.0 % × 2/30 = 191.7333; cap 150,990.00 → **191.73**. amortization_month 24, month_start_date 2026-01-20.
- Step 2 — annual letter, tax_year **2025**:
  - The latest letter was issued 2025-01-24, 24 whole months before 2027-01-25 (≥ 23), so this is a missed-run letter reading entries 13-24 whole months back (2024-12-26 … 2025-12-25).
  - Entrance fee received 0.00.
  - IL payments: 12 × 4,325.12 + 4,360.12 (certified check 2025-05-09) = 56,261.56. A return in the window (4,325.12, 2025-05-06) plus a returned-payment fee of 35.00 → 51,901.44 counted.
  - Recovery nights 14 (respite `2144679c…`, Post-Hospital Recovery Stay) and 12 base-fee charges → 41.0 %, giving 21,279.5904.
  - Care-stay share 1.0 × (5,572.00 − early-departure credit 796.00) = 4,776.00.
  - Medication setup add-on 85.00 × 1.0 = 85.00.
  - Total **26,140.59**.
- Step 3 — closing-year letter, tax_year **2026** (after step 1):
  - Termination in the closing year (12 whole months back).
  - Entrance amount = retention in year 0.00 + amortization in year 191.73; 24 entries → 40.0 %, giving 76.692.
  - IL: proration credit present → charges 9,080.00 − credit 4,053.57 = 5,026.43.
  - The paired residency ended on death → post_death_fee_days 14 (independent charter, One-Bedroom) × 4,540.00/30 = 2,118.67, leaving 2,907.76.
  - 2 base-fee charges (≤ 3) → 45.0 %, giving 1,308.492.
  - Total **1,385.18**.
- Step 4 — estate release (after steps 1-3):
  - Refundable amount 287,600.00 − (11,504.00 + 125,297.73) = 150,798.27.
  - Letters received 282 days after the due date (≥ 180) → interest from 10 days after receipt: DAYS(2026-12-28, 2027-01-25) − 10 = 18, plus the payment day for an estate whose letters arrived late = 19.
  - Brookfield 8.0 % + outstanding step 0.5 (310 days past due, ≥ 270) = 8.5 %. Day count /365: 150,798.27 × 8.5 % × 19/365 = 667.2307 → 667.23.
  - Release **151,465.50**.
  - Root on the opening world: 151,658.08 (refundable 150,990.00, interest 668.08). The later figure is right because the release waits for the final amortization.
- Write sequence (scored writes):
  1. `verify_customer_identity`(customer_id e462fa1d-439f-468d-a5c4-9ba538539d3a, date_of_birth 1937-09-14, ssn_last4 7861) — agent.
  2. `book_final_period_amortization_cad149c9`(entrance_agreement_id ea7a091e-791d-4d44-9d64-cd344fe3adc5, amortization_month 24, month_start_date 2026-01-20, amortization_amount 191.73) — agent.
  3. `issue_annual_tax_letter_ce10c97a`(ea7a091e…, tax_year "2025", medical_expense_amount 26140.59) — agent. Interchangeable with 2.
  4. `issue_closing_year_tax_letter_050bd78c`(ea7a091e…, tax_year "2026", medical_expense_amount 1385.18) — agent.
  5. `release_estate_refund_4b5e42b1`(ea7a091e…, refund_amount 151465.50) — **user** (personal representative), handed over by the agent.
- Terminal state:
  - Ledger + amortization month 24 (2026-01-20, 191.73), tax letters 2025 (26,140.59) and 2026 (1,385.18), estate refund 151,465.50 (check).
  - Agreement closed 2027-01-25, refundable_balance −667.23 (the declared delay-interest overdraw).
- Closest alternatives excluded:
  - Issuing only a 2026 letter — the closing rule's second sentence requires the 2025 letter.
  - Reading the 2025 letter on the 1-12 window — excluded by the missed-run tier.
  - Counting to the vacate date (DAYS(2025-12-20, 2026-02-02) = 44 − 30 = 14 days → half share → 1,438.00) — excluded because the vacate date is after termination.
  - Interest from the due date (311 counted days → 161,719.78) — excluded by tier 1 (letters 282 days late).
  - Subtracting the IL credit-balance refund `Check 10442` 4,053.57 — not an entry "on the agreement's ledger".

### factor_weight

Recomputed by substituting each factor's `baseline` bindings on the handling-time world of its write.

Final amortization, gold-blind 191.73; whole-baseline (baseline.rule: full month at 2.0 %) **5,752.00** ≠ gold.

| factor | effect | tier / records | baseline | result | weight |
| --- | --- | --- | --- | --- | --- |
| final_month_share | method | tier 1: 2 days → 2/30 | full month | 2,876.00 | yes |
| final_month_count_end | method; multi-source; cross independent | tier 2: termination_reason death, IL `d6472373…` vacate 2026-02-02 not before | to termination date (1 day) | 95.87 | yes |
| amortization_step_rate | parameter | tier 2: 23 amortization rows → 1.5 | plan 2.0 | 287.60 | yes, but a stamp agrees (F-T1-2) |
| estate_surrender_reduction | parameter; multi-source; cross independent | tier 1: death + vacated 13 days after → 0.5 | 0 | 287.60 | yes |

- Near-miss: IL vacate date 2026-02-02 (a careless reader counts to it; the rule excludes it because it is not before termination).

Annual letter, gold-blind 26,140.59; whole-baseline (baseline.rule: 1-12 window, plan percentages) **3,495.80** ≠ gold.

| factor | effect | tier / records | baseline | result | weight |
| --- | --- | --- | --- | --- | --- |
| letter_window | method | tier 1: last letter `ac30b805…` 24 months back → 13-24 | 1-12 window | 3,495.80 | yes |
| settlement_basis | method; cross independent | tier 1: return 2025-05-06 + fee 35.00 | all payments | 27,928.24 | yes |
| post_acute_monthly_pct | parameter; multi-source; cross | tier 1: 14 recovery nights + 12 base-fee charges → 41.0 | 38.5 | 24,843.05 | yes, but struck as unreal (F-5) |
| care_stay_share | parameter; cross respite | tier 1: recovery nights → 1.0 | 0 | 21,364.59 | yes |
| stay_charges_basis | method; cross respite | tier 1: early-departure credit `5f3c6dbc…` 796.00 | charges in full | 26,936.59 | yes |
| stay_addon_share | parameter; cross respite | tier 1: medication_setup `4ba54986…` 85.00 → 1.0 | 0 | 26,055.59 | yes |

- Near-misses: respite_payment rows 2,786.00 / 2,075.00; IL rows of 2024-12 and 2026-01 outside the missed-run window; IL credit-balance refund 4,053.57.

Closing-year letter, gold-blind 1,385.18; whole-baseline (baseline.rule: fee received in year at 34.6 % + IL payments at 38.5 %) **3,495.80** ≠ gold.

| factor | effect | tier / records | baseline | result | weight |
| --- | --- | --- | --- | --- | --- |
| closing_entrance_basis | method; multi-source | tier 1: death, termination 2026-01-20 in year → 191.73 | fee received in year (0) | 1,308.49 | yes |
| closing_entrance_pct | parameter | tier 1: 24 entries → 40.0 | 34.6 | 1,374.83 | yes, but struck (F-5) |
| closing_il_basis | method; cross independent | tier 1: proration credit 4,053.57 (2026-02-20) | payments 9,080.00 | 3,209.29 | yes |
| post_residency_deduction | parameter; cross independent | tier 1: IL termination_reason death → 14 days | 0 | 2,338.59 | yes |
| closing_il_pct | parameter; cross independent | tier 1: 2 base-fee charges → 45.0 | 38.5 | 1,196.18 | yes, but struck (F-5) |

- Near-misses: IL credit-balance refund `Check 10442`; amortization 2025-12-20 just outside the year.
- Survivors after F-5: 3 factors / 1 parameter — **below the 4 / 2 floor** (F-T1-1).

Estate release, gold-blind 151,465.50; whole-baseline (baseline.rule: refundable amount) **150,798.27** ≠ gold.

| factor | effect | tier / records | baseline | result | weight |
| --- | --- | --- | --- | --- | --- |
| delay_interest_start | method | tier 1: letters 282 days after due → from letters + 10 | from due date | 161,719.78 | yes |
| interest_day_inclusion | method (realism borderline, O-15) | tier 1: estate, letters late → +1 | as they run (18) | 151,430.38 | yes |
| campus_statutory_rate | parameter; multi-source | tier 1: Brookfield, past due → 8.0 | 0 | 150,837.52 | yes |
| outstanding_step | parameter | tier 1: 310 days past due → 0.5 | 0 | 151,426.25 | yes |
| delay_interest_day_count | method | tier 1: Brookfield /365 | /360 | 151,474.77 | yes |

- Near-miss: no tier-level near-miss record found. The closest is the IL credit-balance refund row, which bears on `refundable_amount`, not on a tier (observation; the "no near-miss" test has no demonstration form in the core table).

Task-level: multi-source factors are present (final_month_count_end, estate_surrender_reduction, campus_statutory_rate), and cross-difficulty factors with seeded rows are present: independent residency `d6472373…` + 55 ledger rows; respite stay `cc941947…` + 5 ledger rows. The seeded respite rows are consistent with their own charter (14 nights × 398.00 = 5,572.00; credit 2 nights × 398.00 = 796.00).

## findings

- **F-T1-1 SOURCE-FACTOR RED** (pre-reveal):
  - Symptom: the closing-year computation does not carry four real factors and two real `parameter` factors.
  - Root cause: `_difficulty.md` F-5 strikes closing_entrance_pct and closing_il_pct as unreal ladders. A CCRC's medical-expense percentage is a plan-wide allocation, not a function of the resident's own tenure or months lived. The annual letter's post_acute_monthly_pct is struck the same way (the annual computation keeps 5 / 2 and stays within bounds).
  - Evidence: rule sentences "The percentage applied to that entrance fee amount rises with the months of occupancy amortized over the whole agreement…" and "The percentage applied to the independent living amount follows how much of the closing year was lived…". On this world they move the letter from 1,374.83 / 1,196.18 to 1,385.18.
  - Demonstrated consequence: survivors are closing_entrance_basis (method), closing_il_basis (method), post_residency_deduction (parameter) — 3 factors, 1 parameter.
  - Affected: `entrance_ext_closing_year_tax_letter` factors/rule; the scored `medical_expense_amount` of `issue_closing_year_tax_letter_050bd78c` (and, for post_acute_monthly_pct, of `issue_annual_tax_letter_ce10c97a`).
- **F-T1-2 SOURCE-FACTOR RED** (pre-reveal):
  - Symptom: the amortization step tier can be read off the seed without the rule.
  - Root cause: the seed amortizes months 19-23 (`4e9ce012…`, `6d1f0bf3…`, `9a88fa73…`, `dc6d1713…`, `6a7458a0…`) at 4,314.00 = 1.5 % of 287,600.00, the very value tier 2 of amortization_step_rate selects for the final month. The charter gives no basis for those rows: the base plan rate is 2.0 %, and the extended step-down applies to "the final period" (charter F-3).
  - Demonstrated consequence: an agent that reads "the rate this agreement currently amortizes at" from the latest row (4,314.00 / 287,600.00 = 1.5 %) and never applies the 18/36-month ladder selects 1.5. That is the same as the rule, so the final amortization is 191.73 under both, and the score cannot tell the two readings apart. Under the honest plan-rate baseline the result would be 287.60.
  - Affected: task 1 `initial_state.entrance_ledger` months 19-23; factor `amortization_step_rate`.
- Observations:
  - F-1 and F-4 have no consequence on this world.
  - interest_day_inclusion realism is borderline (O-15).
  - No tier-level near-miss in the estate computation.
  - The seeded agreement `refundable_balance` 150,990.00 agrees with its ledger (287,600.00 − 11,504.00 − 18 × 5,752.00 − 5 × 4,314.00). It therefore inherits the F-3 rows: under reading A of F-3 it would be 143,800.00. No policy or tool restates past amortization, and every scored formula reads the ledger, so the scored refund is unique.

Frozen blind verdict (pre-reveal):
- Policy self-consistency PASS for this task. The charter REDs F-1/F-2 have no consequence here. F-3's consequence is carried into F-T1-2.
- Problem tree PASS.
- Factors **SOURCE-FACTOR RED** (F-T1-1, F-T1-2).
- Unique solution PASS: 191.73 / 2025: 26,140.59 / 2026: 1,385.18 / 151,465.50.

## source_gt_comparison

Reveal time 2026-10-05T09:14Z, after both task files' frozen sections were on disk (hashes recorded in task_0.md § source_gt_comparison). Read: `tasks/entrance_fee_contracts_and_refunds/tasks/1.json` (all masked fields).

| item | blind | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | executor wants the estate refund paid now by check; consents to the agent's entries; signs the release | request_alignment and step 15 owner user | same |
| now / wait / refuse | act now | act now | same |
| identity | verify e462fa1d…, DOB 1937-09-14, SSN 7861 | step 2, same | same |
| object | agreement ea7a091e… | same | same |
| read set | customer, agreement, entrance ledger, IL residencies, IL ledger, respite ledger | the same plus `find_respite_stays` | same in substance |
| write: final amortization | month 24, 2026-01-20, 191.73 | step 9: 24, "2026-01-20", 191.73 | same |
| write: annual letter | tax_year "2025", 26140.59 | step 11: "2025", 26140.59 | same |
| write: closing letter | tax_year "2026", 1385.18 | step 13: "2026", 1385.18 | same |
| write: release (user) | 151465.50 | step 15: 151465.5 | same |
| order | {amortization, annual} → closing → release; amortization/annual commute | resolution_order [amortization, annual, closing, release]; order_uniqueness says they commute | same |
| terminal | closed, balance −667.23; ledger + month 24, letters 2025/2026, refund | same by replay | same |

Problem tree vs `prerequisite_closure`, value by value:
- release → final amortization, value_input `refundable_amount`, skipped 151,658.08 (GT 151,658.08);
- release → closing letter, state_gate, skipped "refund figure itself is unchanged" (blind: unchanged);
- closing → final amortization, value_input `amortization_in_year`, skipped 1,308.49 with 37.0 % (GT 1,308.49, 37.0 percent);
- closing → annual letter, state_gate, closing amount unchanged (same);
- why-false rows: month 23 latest at 2025-12-20, letters for 2023/2024 only (same rows).

`factor_weight` vs `computations`, figure by figure (all equal):
- final amortization: 191.73 [2876.0, 95.87, 287.6, 287.6], baseline_result 5752.0;
- annual letter: 26140.59 [3495.8, 27928.24, 24843.05, 21364.59, 26936.59, 26055.59], baseline_result 3495.8;
- closing letter: 1385.18 [1308.49, 1374.83, 3209.29, 2338.59, 1196.18], baseline_result 3495.8;
- estate release: 151465.5 [161719.78, 151430.38, 150837.52, 151426.25, 151474.77], baseline_result 150798.27.
- Tiers taken: identical for all 20 factors.

Proof-field assertions checked word for word (Step 3):
- `solvability_contract.seed_consistency[22]`-`[26]` assert, under `policy_id: entrance_occupancy_and_amortization` (the **base** policy), that months 19-23 are "4314.00 = 287,600.00 x 1.5 / 100 (18 or more months already amortized under the step-down)". Items [4]-[21] likewise justify 5,752.00 as "(fewer than 18 months already amortized under the step-down)". `design_rationale` says "History consistency: months 19-23 were booked at 1.5% (4,314.00) under the same step-down."
- These assertions are false against the charter. The base policy cited fixes "amortization_pct_per_month percent of the entrance fee" = 2.0 for LifeCare Declining Balance in every month. The only step-down in the charter is the extended rule's "The monthly amortization percentage of the final period steps down…", which governs the final period of a terminated agreement, not months booked while occupied. This confirms F-T1-2 and the charter-level F-3: the seed was built on reading B of the dropped branch.
- Every other world assertion recomputes, e.g. "refundable_balance 150,990.00 = 287,600.00 − 11,504.00 − 18 x 5,752.00 − 5 x 4,314.00", 282 / 310 days, interest 667.23, post-death 2,118.67.

Closest candidates excluded by policy/world evidence: see the frozen section. GT names the same near-misses for the final amortization (vacate date) and the annual letter (respite payments, certified-check repayment). It names none for the closing letter or the estate release; the blind observation for the estate release stands.

Verdict, task 1:
- Policy self-consistency **PASS** for this task's scored solution. Charter F-3's consequence is carried by F-T1-2.
- Problem tree **PASS**.
- Factors **SOURCE-FACTOR RED** (F-T1-1, F-T1-2).
- Unique solution **PASS** (blind = GT on every argument).

## findings (post-reveal addendum)

- F-T1-2 is reinforced by the reveal. The seed's months 19-23 are justified in `solvability_contract.seed_consistency[22..26]` by a step-down the cited base policy does not contain. The assertion is false word for word, and it is the proof the artifact submits for the rows that leak the step tier.
  - Affected: task 1 `initial_state.entrance_ledger` rows 4e9ce012…, 6d1f0bf3…, 9a88fa73…, dc6d1713…, 6a7458a0…; `solvability_contract.seed_consistency[22..26]` (and the "step-down" glosses in [4..21]); `design_rationale` "History consistency" sentence; `agreement.refundable_balance` 150,990.00 derived from them.
- F-T1-1 unchanged by the reveal. GT's factor_sensitivity confirms each struck factor moves the number, but moving the number does not make the ladder a treatment the business applies.
- Relation to previous revisions: first revision.

## revision_2

### source_derivation_frozen (revision_2)

- Freeze time 2026-10-05T10:00Z (wall clock), before the round-2 task JSONs were opened.
- Inputs: `task_1.view.json` c403a4adecf17a4e9cc5001c9629b0e3a4217aa46b26aa040e23195c88598a05 (changed); `entrance.extended.yaml` 056b1ff6…a599cb (changed); `task_tools.py` unchanged.
- Fields permitted and masked are as in revision_1.
- contamination_disclosure: the round-1 GT of this task is known to the auditor. The brief states only that the scored values changed. The values below come from the round-2 charter's compute over the round-2 view, each checked by hand. The round-1 GT was not used, and the round-2 numbers differ from it on three of the four scored arguments.
- Recomputation: a temporary /tmp script (removed), as in round 1.

### world delta found by the auditor (round-1 view → round-2 view)

- `entrance_ledger` months 19-23 (4e9ce012…, 6d1f0bf3…, 9a88fa73…, dc6d1713…, 6a7458a0…) are now 5,752.00 each, i.e. 2.0 %, the plan rate.
- `entrance_agreements[ea7a091e…].refundable_balance` is now 143800 = 287,600.00 − 11,504.00 − 23 × 5,752.00.
- `respite_ledger`:
  - The second payment of the September 2025 stay is now `fde33cb4…` 2,075.00 on 2025-10-03, payer_type ltc_insurer, method insurer_eft (round 1: a resident check on 2025-09-20).
  - New stay `e573c2f3…` (Post-Hospital Recovery Stay, 2026-01-06 → 2026-01-16) with nightly charge `3ff13f1b…` 10 nights / 3,980.00 (2026-01-06), add-on `b4f8367c…` medication_setup 85.00 (2026-01-06), resident payment `538e3925…` 2,786.00 (2026-01-06) and insurer payment `33a0e8fe…` 1,279.00 (2026-01-28).
  - Both stays balance: 5,572 + 85 − 796 = 2,786 + 2,075; 3,980 + 85 = 2,786 + 1,279.
- Persona:
  - The expected figure is now "a little over a hundred and forty thousand dollars", matching 143,800.00.
  - Only if asked, she mentions a second rehab stay "in early January 2026 after a fall" and that "his long-term care insurance paid part of both".
  - Everything else is unchanged.

### policy_self_consistency (revision_2, this task)

- Cites `_difficulty.md` § revision_2.
- The seed now agrees with the charter. Months 1-23 are at the plan rate 2.0 %, which the round-2 rule gives for "Every month of occupancy … except the final period of a terminated agreement".
- The 0.0-plan gate is not engaged (LifeCare Declining Balance: 34.6 / 38.5).
- Handling time and no-wait are as in revision_1. All respite rows of both stays predate the opening, and the insurer payments are posted (2025-10-03, 2026-01-28), so none is pending.

### problem_chain (revision_2)

- The tree is unchanged: release (user) ← final amortization (value_input `refundable_amount`), ← closing letter (state_gate); closing letter ← final amortization (value_input `amortization_in_year`), ← annual letter (state_gate). n = 3, two value_input edges, acyclic.
- Why-false rows are unchanged: month 24, which began 2026-01-20, has no entry; there are no letters for 2025 or 2026.
- Load-bearing runs:
  - Without the final amortization, the closing letter is 3,820.49 instead of 3,886.83 (amortization_in_year 0.00 instead of 191.73), and the release is 144,436.27 instead of 144,243.69.
- Parallel edges: the annual letter is 22,768.05 on both the opening and the post-amortization world, so the two orders commute.
- Tools do not judge.
- The persona raises only the root. The new care-stay/insurance lines are answer-only-if-asked facts, not prerequisites.

### task_independent_derivation (revision_2)

- Step 1 — final amortization:
  - Last start 2025-12-20; 31 − 30 = 1 day, + the death date counted = 2 days → share 2/30.
  - 23 entries → plan 2.0 × 0.75 = 1.5 %; surrender reduction 0.5 (vacated 13 days after death) → 1.0 %.
  - 287,600 × 1.0 % × 2/30 = **191.73**; month 24, dated 2026-01-20.
- Step 2 — annual letter, tax_year **2025**:
  - Missed-run window, 13-24 months (2024-12-26 … 2025-12-25).
  - Entrance fee 0.00.
  - IL payments 56,261.56 net of the return 4,325.12 and its fee 35.00 = 51,901.44; × 38.5 % (plan) = 19,982.0544.
  - Care stays in the window: the September recovery stay, 14 nights → share 1.0. Charges 5,572.00 (no Trial Stay), net of the early-departure credit 796.00 = 4,776.00, then the insurer paid 2,075.00 (2025-10-03) → borne 2,701.00.
  - The January 2026 stay (posted 2026-01-06, 12 months back) and its insurer payment (2026-01-28, 11 months back) fall outside the window.
  - Medication add-on 85.00 × 1.0.
  - Total = 19,982.0544 + 2,701.00 + 85.00 = **22,768.05**.
- Step 3 — closing-year letter, tax_year **2026** (window 2025-12-26 … 2026-12-25, after step 1):
  - Entrance amount = retention 0.00 + amortization in year 191.73 → × 34.6 % = 66.33858.
  - IL: charges 9,080.00 − proration 4,053.57 = 5,026.43 − post-death 14 × 4,540/30 = 2,118.67 → 2,907.76 × 38.5 % = 1,119.4876.
  - Care: the January 2026 recovery stay, 10 nights → share 1.0. Charges 3,980.00 − insurer 1,279.00 = 2,701.00 (no early-departure credit).
  - Total = **3,886.83**.
- Step 4 — release:
  - Refundable 287,600.00 − (11,504.00 + 23 × 5,752.00 + 191.73) = 143,608.27.
  - Interest at Brookfield (8.0 % + 0.5 % step, 310 days past due), from letters + 10 days, 18 + 1 = 19 days, /365: 143,608.27 × 8.5 % × 19/365 = 635.4174 → 635.42.
  - Release **144,243.69**. On the opening world it would be 144,436.27.
- Write sequence:
  1. verify (e462fa1d…, 1937-09-14, 7861);
  2. `book_final_period_amortization_cad149c9`(ea7a091e…, 24, 2026-01-20, 191.73);
  3. `issue_annual_tax_letter_ce10c97a`(ea7a091e…, "2025", 22768.05) — interchangeable with 2;
  4. `issue_closing_year_tax_letter_050bd78c`(ea7a091e…, "2026", 3886.83);
  5. `release_estate_refund_4b5e42b1`(ea7a091e…, 144243.69) — user.
- Terminal: closed 2027-01-25, refundable_balance 143,800.00 − 191.73 − 144,243.69 = −635.42.
- Closest alternatives excluded:
  - Reading the 2025 letter on the 1-12 window — tier 1 applies, giving 6,281.80.
  - Not netting the insurer → 24,843.05 — excluded by the stay_payer tier.
  - Counting the January 2026 stay in the 2025 letter — it lies outside the window.
  - In the closing letter, netting the 2025 insurer payment 2,075.00 or the 2025 early-departure credit — both lie outside the closing year.

### factor_weight (revision_2)

Figures are the result with that factor's baseline substituted, on the handling-time world.

Final amortization 191.73; whole baseline 5,752.00.
- final_month_share 2,876.00; final_month_count_end 95.87; amortization_step_rate 287.60; estate_surrender_reduction 287.60. All bear weight.
- Stamp check (round-1 F-T1-2): the latest amortization row is now 5,752.00 = 2.0 %, the fall-through value, not the tier value 1.5. Reading the rate off the ledger now gives 287.60 ≠ 191.73, so the rule and the stamp can be told apart. **F-T1-2 closed.**
- Near-miss: vacate date 2026-02-02.

Annual letter 22,768.05; whole baseline 3,495.80.
- letter_window (M) 6,281.80; settlement_basis (M, independent) 24,446.70; stay_payer_basis (M, respite) 24,843.05; care_stay_share (P, respite) 20,067.05; stay_charges_basis (M, respite) 23,564.05; stay_addon_share (P, respite) 22,683.05. All bear weight. 6 factors: 2 P / 4 M.
- Near-misses: the January 2026 stay rows and insurer payment, just outside the window; the resident payments (payer resident_or_family, not insurer).

Closing letter 3,886.83; whole baseline 3,495.80.
- closing_entrance_basis (M) 3,820.49; closing_il_basis (M, independent) 5,447.45; post_residency_deduction (P, independent) 4,702.51; closing_care_share (P, respite) 1,185.83; closing_stay_payer (M, respite) 5,165.83. All bear weight. 5 factors: 2 P / 3 M, all real (`_difficulty.md` § revision_2 factor_ladders). **F-T1-1 closed.**
- Near-misses: the September 2025 stay, its insurer payment (2025-10-03) and its early-departure credit, all outside the closing year; the IL credit-balance refund.

Estate release 144,243.69; whole baseline 143,608.27.
- delay_interest_start 154,009.05; interest_day_inclusion 144,210.24; campus_statutory_rate 143,645.65; outstanding_step 144,206.31; delay_interest_day_count 144,252.51. All bear weight.
- Still no tier-level near-miss (observation as in revision_1).

Task level:
- Multi-source factors: final_month_count_end, estate_surrender_reduction, campus_statutory_rate, closing_entrance_basis.
- Cross-difficulty factors whose rows are seeded: independent (residency d6472373… + ledger) and respite (stays cc941947…, e573c2f3… + 9 ledger rows).
- The seeded respite rows are consistent with the respite charter: 398.00 × 14 = 5,572.00; 398.00 × 10 = 3,980.00; insurer payments allowed.

Frozen verdict (pre-reveal, revision_2): policy self-consistency PASS; problem tree PASS; factors PASS (F-T1-1, F-T1-2 closed); unique solution PASS — 191.73 / 22,768.05 / 3,886.83 / 144,243.69.

### source_gt_comparison (revision_2)

- Reveal time 2026-10-05T10:01Z, after the revision_2 freeze (hashes in task_0.md § source_gt_comparison (revision_2)).
- Read `tasks/…/tasks/1.json` (sha256 fe48825a…d4fd).

| item | blind (rev 2) | GT (rev 2) | same? |
| --- | --- | --- | --- |
| identity | verify e462fa1d…, 1937-09-14, 7861 | same | same |
| final amortization | 24, 2026-01-20, 191.73 | 24, "2026-01-20", 191.73 | same |
| annual letter | "2025", 22768.05 | "2025", 22768.05 | same |
| closing letter | "2026", 3886.83 | "2026", 3886.83 | same |
| release (user) | 144243.69 | 144243.69 | same |
| order | {amortization, annual} → closing → release | [amortization, annual, closing, release] | same |
| scope | the four post-termination policies | `charter_scope` the same four | same |

- Closure, value by value:
  - release ← amortization skipped 144,436.27 (GT 144,436.27, interest 636.27);
  - closing ← amortization skipped 3,820.49 (GT 3,820.49);
  - both state_gate edges leave their amounts unchanged (same).
- Factor sensitivities, figure by figure (all equal):
  - final amortization: 2876.0 / 95.87 / 287.6 / 287.6, baseline 5752.0;
  - annual letter: 6281.8 / 24446.7 / 24843.05 / 20067.05 / 23564.05 / 22683.05, baseline 3495.8;
  - closing letter: 3820.49 / 5447.45 / 4702.51 / 1185.83 / 5165.83, baseline 3495.8;
  - estate release: 154009.05 / 144210.24 / 143645.65 / 144206.31 / 144252.51, baseline 143608.27.
- Tiers taken identical.
- Proof-field assertions re-checked (Step 3):
  - `solvability_contract.seed_consistency` now justifies every amortization row month 1-23 as "5,752.00 = amortization_pct_per_month 2.0 percent of 287,600.00 … (base entrance_occupancy_and_amortization; the extended scaling applies only to the final period of a terminated agreement)". This is true against the round-2 charter, and the round-1 false assertion is gone.
  - The agreement row check states refundable_balance from the ledger and recomputes to 143,800.00.
  - `design_rationale` figures (insurer EFT 2,075.00 and 1,279.00, the January 2026 stay, 10 nights / 3,980.00) match the view.
  - `db_closure_matches_initial_state` = true.
- Verdict (revision_2, task 1): policy self-consistency **PASS**; problem tree **PASS**; factors **PASS**; unique solution **PASS**. **PASS.**

### findings (revision_2)

- **F-T1-1 closed.**
  - Evidence: closing_entrance_pct and closing_il_pct are removed, and the closing computation now has 5 real factors with 2 `parameter` (post_residency_deduction, closing_care_share). post_acute_monthly_pct is removed from the annual letter, which keeps 6 factors with 2 `parameter`.
  - Each of the new factors (stay_payer_basis, closing_care_share, closing_stay_payer) bears weight on this world: 24,843.05 / 1,185.83 / 5,165.83 vs gold.
- **F-T1-2 closed.**
  - Evidence: months 19-23 are reseeded at 5,752.00 (plan 2.0 %), consistent with the round-2 rule.
  - The latest row now encodes the fall-through value 2.0, not the tier value 1.5, so reading it off the ledger gives 287.60 ≠ 191.73.
  - The seed_consistency assertions are corrected.
- No new defect on this world. O-16 (closing_stay_payer insurer-over-credit priority) is not engaged: the 2026 stay has an insurer payment and no early-departure credit. O-17 has a single reading. O-18 is wording only. The estate-release near-miss observation stands.
- Regression check: the problem tree, edge kinds, identity, the amortization value 191.73, the tax years and the persona structure are unchanged.
  - The changed scored values (annual 26,140.59 → 22,768.05; closing 1,385.18 → 3,886.83; release 151,465.50 → 144,243.69) follow from the declared charter and seed rework.
  - Each is reproduced independently from the round-2 charter and view.
- Relation to revision_1: SOURCE-FACTOR RED → PASS.
