# Policy-task audit — retail_payment_servicing / charter-global

## charter_global_frozen
- Freeze time: 2026-10-15T20:22:55Z (round 1; file mtime, before any reveal). Auditor: independent erl-task-policy-audit agent (not the instantiator).
- Frozen inputs (sha256 prefix, re-verified at start, all equal to the coordinator brief):
  - `tasks/retail_payment_servicing/retail.extended.yaml` 3182fe520712e4ad
  - `tasks/retail_payment_servicing/task_tools.py` 107fcfa36abed133
  - masked views `.audit_views/policy/retail_payment_servicing/0.json` a394a1b72ce14fcd, `1.json` 6c2aead2aebe2a67
- Permitted: blueprint/ (blueprint.yaml, db_schema.json, share_tools.py, products/retail.yaml + lease.yaml/care.yaml for cross-category row checks), the extended charter, task_tools.py, the masked views (frozen_time, user_scenario, initial_state), erlbench/ and the instantiate skill's `check_compute.py` DSL (only to re-run the charter's own compute on the masked worlds).
- Masked / not opened before every task file was frozen: `tasks/retail_payment_servicing/tasks/*.json`, `tasks/retail_payment_servicing/worklog.md`, evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure. No recursive search touched `tasks/`.
- Entry conditions (Step 0): gate snapshot supplied (snapshot_r1.txt): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE green; traceability misses only unlock tool-name provenance and validate INVALID only for `documents: 0` — both pre-render, as the brief states. Masked views with hashes supplied. Entry conditions met.
- Base copy: lines 1–2607 of the extended charter are byte-identical to `blueprint/products/retail.yaml` (`diff` empty).

### policy_conflict_scan
Seven extended policies, all `category: retail`:

| id | subject / computes | target_tool (owner) | prerequisite edges |
| --- | --- | --- | --- |
| retail_ext_returned_installment_late_charge (RLC) | retail_late_charge / late_charge_amount | assess_returned_installment_late_charge_34170c70 (agent) | [] |
| retail_ext_arrears_payment (ARR) | retail_payment / payment_amount | post_arrears_payment_6321a7ae (agent) | ← RLC value_input state |
| retail_ext_good_faith_payment (GFP) | retail_payment / payment_amount | submit_extension_good_faith_payment_c7575c9b (user) | ← RLC value_input state |
| retail_ext_extension_grant (EXT) | retail_extension / extension_fee | grant_retail_extension_6a93006b (agent) | ← RLC state_gate state; ← ARR value_input state; ← GFP value_input action |
| retail_ext_unpaid_installment_late_charge (ULC) | retail_late_charge / late_charge_amount | assess_unpaid_installment_late_charge_51bb28dc (agent) | [] |
| retail_ext_late_posted_installment_late_charge (LPC) | retail_late_charge / late_charge_amount | assess_late_posted_installment_late_charge_04190f4f (agent) | [] |
| retail_ext_catch_up_payment (CUP) | retail_payment / payment_amount | submit_catch_up_payment_af77047e (user) | ← ULC value_input state; ← LPC value_input state |

- Overlapping subjects. Three policies share `retail_late_charge`; each overwrite partitions late charges into re-opened by a return (RLC) / left unpaid past grace and not re-opened, next-due installment (ULC) / satisfied by a payment posted after grace (LPC) / everything else under base. The three `replaced_by` texts name one another's cases consistently. One hypothetical overlap: an installment re-opened by a return and then re-paid after grace fits both "re-opened by a returned payment" (RLC overwrite) and "a payment posted after the grace period has since satisfied" (LPC overwrite). Neither task's world has such an installment (O-10).
- Three policies share `retail_payment` / `payment_amount`, split by purpose and channel: ARR (agent, phone_agent_ach, other past-due installments when the oldest is being extended), GFP (customer, phone_ivr_ach, good-faith toward an extension), CUP (customer, phone_ivr_ach, bring the contract fully up to date). The scopes are disjoint as written.
- Triggers, eligibility, time anchors: every policy inherits the base status, grace, dedup and posting conditions it cites. No policy drops a base eligibility. Time anchors are frozen_time (NOW) plus the contract dates. The 12/24/2/1/3-month windows use the DSL `0 <= MONTHS(txn_date, NOW) < n`, which matches the base measure "the 12 calendar months ending on today's date, inclusive", and for n=1 matches "after the same day of the previous calendar month".
- Cross-category reads: lease (status + lease_transactions) in all seven policies; care (status, financed_account_number) in ULC and LPC. All are read-only. Fleet and floorplan are not read.
- Terminal states: payment tools create one retail_payment row and set last_payment_date. Late-charge tools create one retail_late_charge row and add the charge to fees_due_balance. The extension tool creates a retail_extension row, moves next_due_date and maturity_date, raises extensions_used_lifetime, sets last_extension_date and adds the fee to fees_due_balance. See O-1 for the payment-allocation gap.
- Task scopes: task 0 = {RLC, ARR, GFP, EXT} (root EXT); task 1 = {ULC, LPC, CUP} (root CUP). The two scopes are pairwise disjoint and together cover all 7 policies.

### rule_compute_equivalence
Mechanical sweep (scratch script; each `policy_source`, `compute_basis` quote, `baseline.rule` sentence and overwrite `replaced_by` checked for verbatim presence in its own `rule`). All present. Every base `superseded_clause` is verbatim in the base copy. Manual sweep per policy:
- RLC: LATEST returned amount. The tenure rate ladder reads payments_made_count (`>= 18/12`) and the 12-month late-charge count. First-return relief reads the all-time returned count and extensions_used_lifetime and selects halve+floor, ×3/4+floor or keep. The cap is MN(company max, contract max). The lessee deduction uses EXISTS active lease + XCOUNT 12-month lease payments/late charges. Return lag = DAYS(next_due_date, latest return date). Order: rate → method → cap → deductions, floor 0, to the cent. The rule states each element, the compute implements each, and the compute adds nothing.
- ARR: past_due − monthly. Share ladder 70/85/100. Lessee points 10/5/0. Exposure = MONTHS(NOW, maturity) ≥ 36 with Tier 4/5 → 5, other → 2.5. Fee carry: whole / MN(fees, company max) / 0. The share is combined once and rounded, then fees are added, floor 0. Two-way: OK.
- GFP: risk 75/60/ext pct (tier 2 is the XOR, as the rule states). Lessee 10/5. Tenure = MONTHS(first_payment_date, NOW) ≥ 18/12 → 5/2.5. Hardship from ledger extension / due-date-change counts. Early-life = MONTHS(contract_date, NOW) < 24 → 5 (Tier 4/5) / 2.5. Per diem RND(pb·apr/100/365, 2). Cover days: > 30 → dpd−30; > 10 → int((dpd−10)/2); else 0. Assembly as stated. Two-way: OK.
- EXT: recent payments = SUM retail_payment within 1 month. Fee method int(fee/2) / int(fee·3/4) / fee. History reduction (≤1 late → 5; ≤2 → 2.5). Lessee 5/2.5. First-extension 3/1.5. Result is 0 when extension_fee_permitted is false. Two-way: OK.
- ULC: portion = MN(past_due, monthly). Rate ladder on the 24-month returned count. Lessee, effort (1-month payments vs half of monthly), schedule, care (financed_account_number = account_number) and graduated (days beyond grace 1–7 / 8–14) adjustments. Cap last. Two-way: OK.
- LPC: rate ladder on the 24-month returned count. Lessee, care, unchanged-terms and seasoned (MONTHS(contract_date, NOW) ≥ 24 with Tier 1+/1/2) adjustments. Mail float = mail_check payments within 2 months × autopay flag. Cap last. Two-way: OK.
- CUP: fee settlement (late charge within 1 month × autopay flag). Repeat pull (12-month late count ≥ 2 and not autopay → 50; ≥ 1 → 25). Lease pull (lease late within 3 months → 20; within 12 → 10). Interest = per diem × beyond-grace days (≥ 5 → all; 1–4 → 1). Assembly as stated. Two-way: OK.
- Every `factors[].ladder` tier is a rule sentence and a branch of its `decides` binding, and vice versa. No tier lives only in compute.
No SOURCE-POLICY finding from check 2.

### action_binding_and_uuids
- Each `(target_tool, computes)` is claimed by exactly one policy (7 distinct tools).
- Docstrings carry no ordering word in the sequence sense. A grep for before/after/first/then/once/prior/until hits only "following ones" (installments within one extension), "next due date" (a field) and "once its grace period has run out" (scope wording, not sequence). Docstrings name no other tool and contain no example values, so no docstring gold leak was found.
- uuid8s: 6a93006b, c7575c9b, 6321a7ae, af77047e, 34170c70, 51bb28dc, 04190f4f. They are pairwise unrelated, with no shared prefix or tail and no sequence.
- The tools judge nothing. Every body is find-contract → create row → update fields, with no eligibility check, no refusal and no hint.
- Business readings. The good-faith and catch-up tools have identical effects (phone_ivr_ach installment payment). They are told apart only by docstring purpose and policy scope, which is the stated reason for the GFP action-form fallback (below). Unique.

### prerequisite_graph
Edges: ARR←RLC, GFP←RLC, EXT←RLC, EXT←ARR, EXT←GFP, CUP←ULC, CUP←LPC. Every `problem` is an extended id other than the policy itself. The graph is acyclic: RLC → {ARR, GFP} → EXT, and {ULC, LPC} → CUP. Every policy fills `prerequisite` ([] for RLC/ULC/LPC). Every `policy_source` is verbatim in its own rule. `form`/`fallback_reason` are consistent: only EXT←GFP is action form, and it carries a reason. Every `resolved_by` equals the depended-on policy's target_tool. `value_input` gates name real bindings: fee_carry (ARR), risk_pct (GFP), method_fee (EXT ×2), fee_settlement (CUP ×2). The `state_gate` EXT←RLC names `retail_transactions.installment_due_date` (a ledger field, not an eligibility id; see O-4). No authoring-viewpoint wording ("in this task", "at the opening") appears. The `effect` texts state one world's tier move as if it were general (O-3).

### prerequisite_sentences
Four-point test per edge (connective / waited-on object in declared form / no tool, id or snake_case token / strength = condition):

| edge | sentence (own rule) | connective | form OK | tokens | strength vs condition |
| --- | --- | --- | --- | --- | --- |
| ARR←RLC | "The arrears payment amount is worked out only once the late charge owed on an installment that a returned payment has re-opened stands on the contract." | only once | state | none | equal |
| GFP←RLC | "The good-faith amount is figured only after every installment that a returned payment has re-opened and whose grace period has ended carries its late charge on the contract." | only after | state | none | equal ("every" in both) |
| EXT←RLC | "The extension is not granted until every installment that a returned payment re-opened and whose grace period has ended shows its late charge in the contract's ledger." | not … until | state | none | **broader**: condition says "For the installment re-opened…" (CG-2) |
| EXT←ARR | "The extension is granted only after an arrears payment taken by phone by a Kestrel agent has posted on the contract since its most recent installment due date." | only after | state, but names a performer (O-2) | none | equal |
| EXT←GFP | "The extension fee is fixed only after the customer has made the good-faith payment toward the extension." | only after | action + fallback | none | equal |
| CUP←ULC | "The catch-up amount is fixed only after every installment left unpaid past its grace period, other than one re-opened by a returned payment, carries its late charge on the contract." | only after | state | none | **broader**: condition says "The installment the contract's next due date shows…" (CG-2) |
| CUP←LPC | "The catch-up amount is not fixed until the installment whose payment posted after its grace period ended shows its late charge in the contract's ledger." | not … until | state | none | equal |

- One write per state-form edge (derivation). "A late charge on an installment a returned payment re-opened" leads to the only rule that figures such a charge: RLC ("This policy figures the late charge assessed on an installment that a returned payment has re-opened"). ULC's overwrite excludes re-opened installments, and LPC requires the installment to be satisfied. "A payment taken by phone by a Kestrel agent" leads to ARR, the only agent-taken phone payment; GFP and CUP are customer IVR payments. "Left unpaid past its grace period, other than one re-opened" leads to ULC. "Whose payment posted after its grace period" leads to LPC. Each hop has a single reading.
- Fallback test, EXT←GFP: the good-faith row (retail_payment / phone_ivr_ach / installment) is field-for-field the same kind as the catch-up row, so no record-visible state singles out the good-faith write. The fallback is justified.
- No depended-on rule restates the dependent's sentence. No rule names a tool or policy id. No undeclared cross-problem order appears in an extended rule.
- One base sentence states a cross-problem order: retail_extensions "Before the extension is granted, a good-faith payment of at least … must have posted since the most recent installment due date". EXT carries its own action-form sentence, so no tree rests on the base sentence → observation O-12.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry.
- RLC vs retail_late_charges. The status, grace, counting and one-per-installment sentences are followed. The amount sentence is overwritten (declared). The "min unpaid / deferred / paid in full within grace" exclusion sentence is not overwritten, so it is inherited. Its clause "an installment that was paid in full within the grace period" literally matches a re-opened installment whose payment posted inside grace and was later dishonoured. The base returned-payment rule's own sentence "A returned payment re-opens the installment it had paid; late charges on that installment follow the late charge rule" resolves this toward assessing, so no second defensible answer → class member noted under CG-1 as observation O-13.
- ULC vs retail_late_charges. The amount sentence is overwritten (declared). The portion is re-defined as MN(past_due, monthly) inside the declared replaced clause. The rule inherits status, grace, minimum unpaid and one-per-installment explicitly. No undeclared conflict.
- LPC vs retail_late_charges. The amount sentence is overwritten (declared). LPC's inheritance list deliberately omits "the minimum unpaid portion" (ULC lists it) and adds an undeclared re-anchoring: "the installment counts as unpaid at the end of the grace period in the full amount of one monthly_payment". The base sentence "No late charge is assessed when the unpaid portion is less than late_charge_min_unpaid_amount", with retail_msr_unpaid_installment_portion measured "as of the assessment date", is not named in any overwrite. **CG-1** (0/1-multiplier form).
- ARR vs retail_payment_posting / retail_reinstatement_and_redemption (`overwrite: []`). Posting sentences are followed (payable status, cutoff, allocation cited, channel fee 0.00 for phone_agent_ach). The reinstatement rule's scope ("After repossession and until the sale") never reaches an active contract, so no sentence is followed or contradicted (O-8).
- GFP vs retail_payment_posting / retail_reinstatement_and_redemption / retail_extensions. The base good-faith sentence is overwritten in GFP (declared, merged meaning unique: the payment must reach the figured amount and still post since the most recent installment due date). Posting is followed (phone_ivr_ach fee 0.00).
- EXT vs retail_extensions. The fee sentence is overwritten (declared). Status, counts, blackout, relationship, signed agreement, interval, per-request maximum, schedule move, "late charges already assessed remain due, and no late charge is assessed on a deferred installment" are all followed.
- CUP vs retail_payment_posting / retail_reinstatement_and_redemption (`overwrite: []`). Posting is followed. Reinstatement is out of scope as for ARR. The catch-up amount (past due + pull-ahead + fees + interest) is not a reinstatement amount, because the contract is active.
- No author note calls a base output a "wrong value".

### factor_ladders
| policy | factor | effect | tiers (values) | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| RLC | lrf_tenure_rate | parameter | 3.0 / 4.0 / pct(5) | yes (counter AND ledger count) | — |
| RLC | lrf_first_return_relief | method | ½ floor / ¾ floor / cent | yes (returned count AND extension counter) | — |
| RLC | lrf_lessee_deduction | parameter | 3.0 / 1.5 / 0 | yes (lease status AND lease ledger) | lease |
| RLC | lrf_lapsed_grace | parameter | 2.0 / 1.0 / 0 | no (single date diff) | — |
| ARR | cuf_arrears_share | parameter | 70 / 85 / 100 | yes | — |
| ARR | cuf_lessee_share | parameter | 10 / 5 / 0 | yes | lease |
| ARR | cuf_exposure | parameter | 5 / 2.5 / 0 | yes (months AND tier) | — |
| ARR | cuf_fee_carry | method | whole / capped / none | yes (returned count AND fees) | — |
| GFP | gff_delinquency_risk | parameter | 75 / 60 / ext pct | yes | — |
| GFP | gff_lessee_points | parameter | 10 / 5 / 0 | yes | lease |
| GFP | gff_tenure_points | parameter | 5 / 2.5 / 0 | no | — |
| GFP | gff_first_hardship | parameter | 5 / 2.5 / 0 | yes (two ledger counts) | — |
| GFP | gff_early_life | parameter | 5 / 2.5 / 0 | yes (tier AND age) | — |
| GFP | gff_overdue_interest | method | dpd−30 / ½(dpd−10) floor / 0 days | no | — |
| EXT | xf_fee_method | method | ½ floor / ¾ floor / as is | no | — |
| EXT | xf_history_reduction | parameter | 5 / 2.5 / 0 | yes | — |
| EXT | xf_lessee_reduction | parameter | 5 / 2.5 / 0 | yes | lease |
| EXT | xf_first_extension | parameter | 3 / 1.5 / 0 | yes | — |
| ULC | ucf_unpaid_rate | parameter | 3.5 / 4.25 / pct | yes | — |
| ULC | ucf_lessee_points | parameter | 0.5 / 0.25 / 0 | yes | lease |
| ULC | ucf_partial_effort | parameter | 0.5 / 0.25 / 0 | no | — |
| ULC | ucf_clean_schedule | parameter | 0.5 / 0.25 / 0 | yes | — |
| ULC | ucf_care_plan | parameter | 0.5 / 0.25 / 0 | yes (status AND financed acct) | — (care is no difficulty) |
| ULC | ucf_graduated | method | ½ floor / ¾ floor / cent | no | — |
| LPC | lpf_posted_rate | parameter | 3.0 / 4.0 / pct | yes | — |
| LPC | lpf_lessee_points | parameter | 0.4 / 0.2 / 0 | yes | lease |
| LPC | lpf_care_holder | parameter | 0.5 / 0.25 / 0 | yes | — |
| LPC | lpf_unchanged_terms | parameter | 0.5 / 0.25 / 0 | yes | — |
| LPC | lpf_seasoned | parameter | 0.5 / 0.25 / 0 | yes | — |
| LPC | lpf_mail_float | method | ½ floor / ¾ floor / cent | yes (mail-check count AND autopay) | — |
| CUP | cpf_fee_settlement | method | whole / capped / none | yes (recent late charge AND autopay) | — |
| CUP | cpf_repeat_pull | parameter | 50 / 25 / 0 | tier1 yes, tier2 single | — |
| CUP | cpf_lease_pull | parameter | 20 / 10 / 0 | no (one ledger, two windows) | lease |
| CUP | cpf_overdue_interest | method | all days / 1 day / none | no | — |

- Counts. RLC 4 (3P/1M), ARR 4 (3P/1M), GFP 6 (5P/1M), EXT 4 (3P/1M), ULC 6 (5P/1M), LPC 6 (5P/1M), CUP 4 (2P/2M). All are within 4–6 with ≥ 2 parameter and ≥ 1 method. Each ladder has 3 pairwise-disjoint tiers. No two tiers share a value or method (GFP fall-through ext pct is 50/25/0 by tier and never equals 75 or 60). Each `decides` is an input, never `result`. Binding sets are disjoint within each policy. No factor reads another factor's binding. Every fall-through equals the policy baseline. Every `baseline.rule` sentence is in the rule, is self-sufficient and names its `params` keys.
- Task coverage. Task 0's policies carry multi-source factors and a lease cross-difficulty factor (RLC/ARR/GFP/EXT). Task 1's carry multi-source factors and lease cross-difficulty factors (ULC/LPC/CUP).
- Label honesty. Method tiers 1 and 2 of lrf_first_return_relief, xf_fee_method, ucf_graduated and lpf_mail_float differ only by a multiplier (½ vs ¾). The algorithmic difference from the fall-through is the whole-dollar floor, so the labels pass, as noted in O-6.
- Realism (US captive auto finance / company schedule). All fall-throughs are the standard treatment: 5% capped late charge, full tier extension fee, 100% of the other past due, the tier good-faith percentage, past due as the catch-up amount. Payment-history tiers, relationship (lessee) concessions, first-hardship/first-return courtesies, seasoning, mail float and graduated lateness are things a captive's written courtesy schedule can weigh. Weak points, recorded as observations: O-5 (GFP tenure-off vs early-life-on read the same seasoning dimension with opposite signs), O-7 (late-charge rate reduced for holding a Kestrel Care service contract, ULC/LPC), O-9 (ARR "less one monthly_payment" ignores 2-installment deferrals on Tiers 2–1+).

### findings
- **CG-1 SOURCE-POLICY RED — undeclared override of a base late-charge exclusion (0/1-multiplier form).**
  - Symptom: LPC charges a late charge on an installment fully satisfied before the assessment date.
  - Root cause: the base sentence "No late charge is assessed when the unpaid portion is less than late_charge_min_unpaid_amount, on an installment deferred by an extension, or on an installment that was paid in full within the grace period." evaluates the portion by `retail_msr_unpaid_installment_portion` = "monthly_payment less the payment amounts applied to that installment, as of the assessment date". LPC's rule instead declares "the installment counts as unpaid at the end of the grace period in the full amount of one monthly_payment". It omits the minimum-unpaid clause from its inherited list, while ULC keeps it. LPC's overwrite names only the amount sentence.
  - Evidence: retail.extended.yaml lines 1564–1567 (base) vs 3510 and 3483–3487 (LPC).
  - Demonstrated consequence: task 1, see `1.md` §findings.
  - Class (all members): (a) LPC × min-unpaid exclusion — RED; (b) RLC × "paid in full within the grace period" exclusion — observation O-13, resolved by the base returned-payment re-open sentence. No other extended policy touches a base exclusion sentence.
  - Bears on: task 1 (a); task 0 (b, observation only).
- **CG-2 SOURCE-POLICY RED (charter-wide, no consequence on either task world) — prerequisite sentence broader than its condition and than the resolving policy's reach.**
  - Members:
    - EXT←RLC: sentence "every installment that a returned payment re-opened…" vs condition "For the installment re-opened by a returned payment…". RLC can only figure the charge for "the installment the contract's next due date shows".
    - CUP←ULC: sentence "every installment left unpaid past its grace period, other than one re-opened…" vs condition "The installment the contract's next due date shows, left unpaid past its grace period…". ULC figures only the next-due installment.
    - Related member with sentence = condition but the same reach gap: GFP←RLC ("every installment that a returned payment has re-opened…"; RLC covers only the next-due one).
  - Demonstration on a constructed situation: a contract with two installments unpaid past grace and none re-opened. The CUP sentence makes the catch-up wait on two late charges, while the condition (and ULC's reach) supplies one. The second charge falls to "any other late charge remains under the base rule". The catch-up then differs in fee_settlement and in the 12-month late count (repeat pull 25% vs 50%).
  - Neither task's world has a second such installment, so tasks 0 and 1 carry no consequence.
- Observations (not grounds for rework unless the coordinator chooses):
  - O-1: the payment tools post a bare retail_payment row. They write no interest/principal/fees split, no retail_fee_payment, and no change to principal_balance, past_due_amount, days_past_due or fees_due_balance. The posting rule each payment policy invokes ("applied in the contract's allocation order") would allocate the payment.
    - On task 0, the base formula `fees_applied = min(fees, max(0, amount − max(interest, installments_due)))` with installments_due 1292.08 gives fees_applied 0 for the 545.83 arrears payment, so ARR's "carries the whole fees_due_balance" never reaches fees.
    - Under true allocation, ARR before GFP would lower principal_balance to about 20858.42 → per diem 7.42 → good-faith 454.40, vs 454.49 in GFP-first order. On the executable world (tools as written) both orders give 454.49, so the solution is unique.
  - O-2: EXT←ARR is declared state form but names a performer ("taken by phone by a Kestrel agent"). The record-visible state is `payment_channel = phone_agent_ach`. The hop still resolves uniquely.
  - O-3: `effect` texts on ARR←RLC, GFP←RLC, EXT←ARR and EXT←GFP assert a particular tier move ("from the first to the second step", "from the three-quarters step to the halved step"). This holds only for worlds like task 0's and is stated as general text.
  - O-4: EXT←RLC is a `state_gate` whose `gate` is a ledger field, not an eligibility id. Its real rationale is the base sentence "no late charge is assessed on a deferred installment".
  - O-5: GFP tenure points (≥ 18 months since first payment, −5) and early-life points (< 24 months since contract date, +5 on Tier 4/5) cancel exactly for Tier 4/5 contracts 18–23 months old.
  - O-6: method tiers ½ vs ¾ differ only by a multiplier, in four factors (listed above).
  - O-7: ucf_care_plan and lpf_care_holder price a late charge on whether a vehicle service contract was bought and where it was financed. This is weakly grounded in real practice, though accepted as company schedule.
  - O-8: ARR, GFP and CUP cite retail_reinstatement_and_redemption, whose scope never reaches an active contract.
  - O-9: ARR's "less one monthly_payment" assumes a 1-installment deferral, but Tiers 2–1+ allow 2 per request.
  - O-10: hypothetical RLC/LPC overlap on a re-opened-then-late-repaid installment.
  - O-11: the seed ledgers' interest/principal splits follow monthly amortization, not the daily simple-interest accrual the posting rule states. Balances reconcile to the ledgers. No factor reads the splits.
  - O-12: base cross-problem order sentence (good-faith before extension); not load-bearing.
  - O-13: see CG-1(b).

## closing_checklist
Written after both reveals (2026-10-15T20:24:31Z). Nothing above this heading was derived from GT.
- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json, alongside this file. This is round 1, so there are no older revisions.
- Coverage and scope: the 7 extended policies are fully covered. Task scopes {RLC, ARR, GFP, EXT} and {ULC, LPC, CUP} are disjoint and match both tasks' `charter_scope`. Task tools and GT are closed. uuid8s are independent.
- Trees: task 0 has 3 prerequisite problems and 4 value_input edges; task 1 has 2 and 2. Each tree contains a customer-owned write (GFP; CUP). Both are acyclic, and the union graph is acyclic.
- Factors: every computation has a self-sufficient baseline and 4–6 factors with ≥ 2 parameter and ≥ 1 method. Each task has multi-source and lease cross-difficulty factors. Every factor bears weight on its world, and every baseline is definite and ≠ gold. GT factor_sensitivity and baseline_result match the auditor's recomputation figure for figure.
- **The difficulty does not close.**
  - Charter-wide REDs: CG-1 (demonstrated on task 1) and CG-2 (latent, no task consequence).
  - Task 1 additionally carries F2 (SOURCE-FACTOR RED: the lease holding row is not producible by the lease charter).
  - Task 0 PASSES all four relationships.
- Gate re-run on the final form: not performed. The auditor runs no gates and edits nothing; the round-1 snapshot (snapshot_r1.txt) is the gate evidence.

task0=PASS task1=SOURCE-POLICY RED+SOURCE-FACTOR RED
charter=CG-1,CG-2

## revision_2

### charter_global_frozen (round 2)
- Re-audit after rework round 2. Gating line `REWORK round 2: gates 8/8 green` was confirmed (tail of the difficulty worklog).
- Gate snapshot: `.audit_views/policy/retail_payment_servicing/snapshot_r2.txt` (2026-10-15T20:55:45Z). All gates are green. Traceability misses are only unlock tool-name provenance, and validate INVALID is only `documents: 0`; both are pre-render.
- New hashes: charter 68942a9f3f0439bc (r1 3182fe520712e4ad), task_tools af3b4e90eed19ec1 (r1 107fcfa36abed133), views 0.json 9de058c0bd5499f6, 1.json a4d408333a7d0b79.
- Both shared inputs changed, so every charter-global section below is re-derived in full. The round-1 text above is left untouched.
- Base copy (lines 1–2607) is still byte-identical to blueprint/products/retail.yaml.
- Masked until both round-2 task derivations are on disk: tasks/*.json and the worklog's "REWORK round 2 closure" section. This section was written from the charter, tools, schema and masked views only.

### changes found (charter and tools, round 1 → round 2)
- RLC: one sentence added: "A re-opened installment is not an installment paid in full within the grace period: the reversal restores the amounts the dishonoured payment had applied, so the installment is again unpaid in the re-opened amount, and the minimum unpaid portion is compared with that amount." Compute, factors and overwrite are unchanged.
- ARR:
  - New overwrite of the base allocation sentence. The payment is recorded on its posting day, and the nightly posting cycle applies the allocation order. The same text appears in GFP and CUP.
  - Prerequisite sentence and condition narrowed to "the installment the contract's next due date shows".
  - other past due = past_due_amount − monthly_payment × requested_installments of the most recent completed extension agreement (new binding `deferred_count`, LATEST over retail_requests).
  - Fee-carry wording changed to "includes an amount equal to".
  - `effect` text generalised.
- GFP:
  - Allocation overwrite added.
  - Prerequisite narrowed to the next-due installment.
  - gff_early_life is replaced by gff_long_term: contract length = MONTHS(contract_date, maturity_date) ≥ long_term_months (60) → +7 on Tier 4/5, +2.5 on other tiers, else 0.
- EXT:
  - EXT←RLC sentence narrowed to "the installment it defers".
  - EXT←ARR sentence is now "…only after a payment through the agent-assisted phone ACH channel has posted…" (no performer).
  - Effects generalised.
  - Compute is unchanged.
- ULC: unchanged.
- LPC:
  - Overwrite 1 adds "and that no returned payment re-opened".
  - New overwrite 2 names the base exclusion sentence "No late charge is assessed when the unpaid portion is less than late_charge_min_unpaid_amount, on an installment deferred by an extension, or on an installment that was paid in full within the grace period." Its replaced_by sets, for late-posted installments not re-opened, the portion that stood at grace end; for every other installment, including one re-opened by a returned payment, it keeps the base exclusion with the portion "as of the assessment date".
  - Rule adds "Since no payment reached the installment within its grace period, the portion that stood when the grace period ended is one full monthly_payment."
- CUP: allocation overwrite added; the CUP←ULC sentence and condition narrowed to the next-due installment; fee wording changed to "includes an amount equal to".
- task_tools: the three payment docstrings now state "the split of the payment across interest, principal and fees is applied by the nightly posting cycle, not by this call". Bodies, signatures and uuid8s are unchanged.

### re-derived checks (round 2)
- rule_compute_equivalence: the mechanical sweep passes. Every policy_source, compute_basis quote, baseline sentence and overwrite replaced_by is verbatim in its own rule, and every superseded_clause is verbatim in its base policy. The new bindings `deferred_count`, `contract_length_months` and `term_points` have quotations and implement them. No tier lives only in compute.
- action_binding_and_uuids: unchanged. One (tool, computes) per policy. The only ordering word in the docstrings is "later" (calendar month later, a date move). "Nightly posting cycle" names a system batch, not another tool. uuid8s are unchanged and independent.
- prerequisite_graph: the same 7 edges, acyclic. Every resolved_by equals the target_tool and every gate names a real binding. EXT←RLC still names a ledger field as its gate (O-4 stands, observation).
- prerequisite_sentences: all seven pass the four-point test. Sentence scope now equals the condition on every edge. EXT←ARR is a clean state form (`phone_agent_ach` is singled out by "agent-assisted phone ACH channel"; only ARR writes it). The EXT←GFP fallback is still justified (good-faith and catch-up rows are still identical).
- override_declarations: LPC × min-unpaid is now declared (CG-1(a) closed). The allocation sentence is declared in ARR, GFP and CUP with mutually consistent scopes, giving one merged meaning: allocation runs at the nightly cycle, so no in-call field changes. That matches the tools and closes O-1. New conflict: **CG-3** (below).
- factor_ladders:
  - GFP still has 6 factors (5P/1M). gff_long_term is multi-source (tier AND contract length), its values 7 / 2.5 / 0 are distinct, its fall-through is the baseline, and it is stated in the rule. Realism: a longer original term carries a higher good-faith demand, which is plausible as a company schedule.
  - O-5 (tenure vs early-life cancelling) is gone: tenure −5 and long-term +7 do not cancel.
  - All other ladders are unchanged from round 1.
  - Factor counts per policy are unchanged: RLC 4, ARR 4, GFP 6, EXT 4, ULC 6, LPC 6, CUP 4.

### round-1 finding status
- CG-1 (LPC undeclared min-unpaid override): **closed**. Overwrite 2 names the base sentence verbatim, and the replaced_by is in the rule. The class member CG-1(b)/O-13 (RLC × "paid in full within grace") is settled by the new RLC sentence, consistent with the base returned-payment rule. But see CG-3 for the residual min-unpaid half of that sentence.
- CG-2 (sentence broader than condition / resolving reach): **closed** for every member (EXT←RLC, CUP←ULC, GFP←RLC; ARR←RLC aligned too). Every sentence now scopes to the next-due / deferred installment, which equals both its condition and RLC's or ULC's reach.
- Observations:
  - O-1 closed (allocation declared to the nightly cycle; tools say so).
  - O-2 closed. O-3 closed. O-5 closed.
  - O-9 closed (deferred_count). O-10 closed (LPC excludes re-opened). O-13 closed.
  - O-4, O-6, O-7, O-8, O-11, O-12 stand as observations.

### new findings (round 2)
- **CG-3 SOURCE-POLICY RED — the two extended texts that now speak about the minimum-unpaid test for a re-opened installment contradict each other (the CG-1 class, residual member).**
  - Symptom: RLC and LPC give different minimum-unpaid tests for the same re-opened installment.
  - Passage A, RLC rule: "…so the installment is again unpaid in the re-opened amount, and the minimum unpaid portion is compared with that amount." The re-opened amount is "the amount of the most recent returned payment recorded on the contract", i.e. the whole dishonoured payment, including any fee portion it carried.
  - Passage B, LPC overwrite 2 replaced_by (also in LPC's rule): "for every other installment, including … one re-opened by a returned payment, no late charge is assessed when the unpaid portion as of the assessment date is less than late_charge_min_unpaid_amount". This is the base measure `retail_msr_unpaid_installment_portion` = monthly_payment less the amounts applied to that installment.
  - RLC names no base sentence for this comparison.
  - Situation: an installment of 646.04 is paid 640.00 plus a 20.00 payment, which the posting rule applies 6.04 to the installment and 13.96 to fees due. The 20.00 payment is returned.
    - Under A: re-opened amount 20.00 ≥ 10.00, so a late charge is assessable on that installment. RLC then figures it from the 20.00 base, and a late-charge row is booked against that due date even where the figured amount rounds down to 0.00.
    - Under B: portion 6.04 < 10.00, so no late charge is assessed.
  - Different conclusions in the same situation.
  - Neither task's world reaches it: task 0's returned payment is 646.04 with no fee portion, so both readings give 646.04 ≥ 10.
  - Charter-wide only. Affected: RLC rule sentence 4; LPC overwrite 2 / rule.
- Observation O-14: ARR's new `deferred_count` is a LATEST read over retail_requests (most recent completed extension_agreement). The rule names the selection ("the most recent completed signed extension agreement"), so the read is unambiguous. Task 0 seeds only one request, so the read has no decoy row on that world.

### closing_checklist (revision_2, after reveal 2026-10-15T20:59:58Z)
- The round-2 per-task sections are appended to 0.md and 1.md, and round-1 text is untouched. Both task comparisons are PASS.
- Coverage and scope are unchanged: 7 policies, disjoint scopes, independent uuid8s.
- Trees: 3 and 2 prerequisite problems; 4 and 2 value_input edges; user writes GFP and CUP; the union graph is acyclic.
- Factors: every computation has 4–6 factors, all bearing weight. The GT factor_sensitivity matches the recompute figure for figure. Each task has multi-source factors and lease cross-difficulty factors. Lease, care, pre-owned and balloon seed rows are now consistent with their charters.
- Reworker claims (worklog "REWORK round 2 closure") were verified item by item.
  - CG-1(a), CG-2, F2, O-1/2/3/5/9/10/13, and task-0 minor items 1–5 are closed on disk.
  - O-4/6/7/8/11/12 are kept as observations.
  - Residual stale proof text (observation only):
    - task 0 computations[ARR].factor_trace "booked at step 8";
    - task 1 design_rationale receipt-time phrase.
- Open: **CG-3** (charter-wide SOURCE-POLICY RED, residual member of the CG-1 class). RLC's new sentence "…the minimum unpaid portion is compared with that amount" (the whole returned payment) contradicts LPC overwrite 2's "including … one re-opened by a returned payment, … the unpaid portion as of the assessment date". It is demonstrated on a constructed world where the returned payment carried a fee portion, and reaches neither task.
- Gates: the coordinator's round-2 snapshot (snapshot_r2.txt) is all green apart from the expected pre-render items. The auditor ran no gates beyond snapshot.sh, as the brief directs.

task0=PASS task1=PASS
charter=CG-3
VERDICT revision_2: task0=PASS task1=PASS charter=CG-3

## revision_3

### charter_global_frozen (round 3)
- Gating line `REWORK round 3: gates 8/8 green` confirmed.
- Gate snapshot: `.audit_views/policy/retail_payment_servicing/snapshot_r3.txt` (2026-10-15T22:22:25Z). All gates are green apart from the expected pre-render traceability (unlock tool_name) and validate (`documents: 0`) items.
- Hashes:
  - charter eb028b9db9f2999c (r2 68942a9f3f0439bc), changed;
  - task_tools ac12a91b1d641727 (r2 af3b4e90eed19ec1), changed;
  - views 0.json 9de058c0bd5499f6 and 1.json a4d408333a7d0b79, **unchanged from r2**, so the task worlds and the r2 seed checks carry forward on hash grounds.
- Charter and tools changed, so every charter-global check is re-derived in full below. The base copy is still byte-identical.
- Masked until both round-3 task sections were on disk: the worklog "REWORK round 3 closure" and tasks/*.json.
- New this round (coordinator brief): every point of `audits/render_source/XF_recipe.md` is checked on every extended policy, and any member is a charter RED.

### changes found (r2 → r3)
- RLC:
  - "re-opened amount" redefined as the unpaid portion of the next-due installment as of the assessment date. Compute: `RND(past_due − monthly × int((past_due − 0.01)/monthly), 2)`.
  - The minimum-unpaid sentence now compares that amount.
  - "returns recorded on the same date share that date" added; counting-convention sentences added.
  - Overwrite tail now reads "…remains under the base rule and is not figured under this policy".
- ARR:
  - tie sentence for the LATEST agreement read;
  - "applies only where a completed signed extension agreement is on the contract";
  - assembly sentence now "any amount a schedule below includes is then added";
  - convention sentence added.
- GFP: interest-cover rounding sentence; assembly "any amount a schedule below adds"; convention sentences.
- EXT: convention sentence.
- ULC:
  - the minimum-unpaid and deferred exclusions are restated;
  - the unpaid portion is redefined the same way as RLC's;
  - convention sentences.
- LPC: convention sentence.
- CUP: binding `interest_carried`; assembly "that figure and every other amount a schedule below adds"; convention sentences.
- task_tools: "toward" removed from the payment docstrings ("for an extension", "on the past-due installments"). Bodies and uuid8s are unchanged.

### re-derived standard checks (round 3)
- Verbatim sweep (scratch script): for all 7 policies, every policy_source, compute_basis quote, baseline sentence and replaced_by is in its own rule, every superseded_clause is in its base policy, and every compute binding has a basis.
- Recompute on the unchanged views gives the same values as r2:
  - task 0: 4.00 / 545.83 / 467.41 / 4.00;
  - task 1: 5.00 / 4.00 / 1056.10.
- RLC's new re-opened amount on task 0: int(1292.07/646.04) = 1, so 646.04, which equals the r2 value. ULC's portion on task 1: int(590.81/690.82) = 0, so 590.82.
- Factor sensitivities, baselines and skip-edge runs are identical to r2.
- Prerequisite graph and sentences are unchanged from r2 (all pass). Tools are checks-free.

### round-2 RED status
- **CG-3: closed.** RLC's minimum-unpaid comparison now uses "the unpaid portion, as of the assessment date, of the installment the contract's next due date shows". That is the measure LPC overwrite 2 prescribes for re-opened installments, so the two texts agree. The constructed $20 fee-portion world now gives no charge under both texts: the portion is 6.04.
- Nothing closed in r1/r2 has regressed: CG-1, CG-2, F2 and the r2 observations are all re-checked on disk.

### XF_recipe sweep (every point × every extended policy)
| pt | RLC | ARR | GFP | EXT | ULC | LPC | CUP |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 assembly | **member** | **member** (×2) | **member** | ok | ok | ok | **member** (×2) |
| 2 non-commuting order | ok | ok | ok | ok | ok | ok | ok |
| 3 independence | ok | see pt 1 | ok | ok | ok | ok | see pt 1 |
| 4 ownership | ok | see pt 1 | ok | ok | ok | ok | ok |
| 5 quotes | ok | ok | ok | ok | ok | ok | ok |
| 6 ties | ok | ok | n/a | n/a | n/a | n/a | n/a |
| 7 counting | ok | ok | ok | ok | ok | ok | ok |
| 8 branches | ok | ok | ok | ok | ok | ok | ok |
| 9 base clauses | **member** | **member** | **member** | ok | **member** | **member** (ovw 1) | **member** |
| 10 rounding | ok | ok | ok | ok | ok | ok | ok |
| 11 tools | ok (all 7 docstrings) | | | | | | |
| 12 proof text | checked per task after reveal | | | | | | |

Notes on the "ok" cells:
- pt 2: every policy's combination sentence fixes the non-commuting steps. RLC: rate → method → cap → deductions. ULC and LPC: combined rate → method → cap. GFP: combined percentage → round → add. EXT: method → reductions. ARR and CUP: combine → round → add.
- pt 6: LATEST reads are only RLC's return date (tie: same date) and ARR's agreement (tie: first recorded = DSL LATEST keeps the first row).
- pt 7: the MONTHS/DAYS convention sentences match `MONTHS()`/`DAYS()` exactly, including negative day counts and the `0 ≤ m < N` window.
- pt 8:
  - The absent agreement (ARR) is stated as out of scope.
  - Negative lag (RLC) and days beyond grace ≤ 0 (ULC/CUP) fall into the stated "every other case".
  - Zero amounts are covered by the floor-at-zero sentences.
  - "Not figured / not posted under this policy" states the out-of-scope cases as outside the tool.
  - The minimum-unpaid and deferred exclusions are act/refuse eligibility conditions (like grace and status), not compute branches.
- pt 10: every RND matches its rounding sentence.
- pt 11: all 7 docstrings claim only what their bodies do. They carry no example values, and no before/after/ahead of/toward wording.

**CG-4 SOURCE-POLICY RED (XF pt 1/3/4) — assembly or factor sentences that combine, or contribute against, factor quantities rather than a baseline-defined quantity.**

All members:
1. RLC: "…and last any amount a schedule below deducts is subtracted". The computation sentence refers to the factor schedules (the recipe's "the amounts from the schedules below…" form).
2. ARR: "any amount a schedule below includes is then added" (same form).
3. ARR: cuf_lessee_share ("…points are taken off the arrears share") and cuf_exposure ("…points are added to the arrears share") contribute against "the arrears share". That quantity is defined only by cuf_arrears_share ("the share … starts at share_long_pct … in every other case it starts at 100 percent"). ARR's baseline ("The arrears payment amount is the other past-due amount, rounded to the cent") defines no share. The assembly sentence "the share adjustments are first combined into one share" combines the three factors' quantities.
4. GFP: "any amount a schedule below adds is then added" (same form as 1).
5. CUP: "that figure and every other amount a schedule below adds are then added…" (same form as 1).
6. CUP: cpf_lease_pull says "a **further** lessee_pull_pct_recent percent … is pulled ahead". Its meaning is stated relative to cpf_repeat_pull, and the baseline defines no pull-ahead. The load-bearing sentence "the pull-ahead percentages are first combined into one percentage, which is applied once … and rounded" names exactly those two factors' quantities. The combination is non-commuting (it is rounded once).

Not members:
- ULC, LPC and EXT: the combination sentences name only generic kinds ("the rate adjustments", "any change of method", "every reduction") against a baseline quantity (late_charge_pct, extension_fee).
- GFP's percentage adjustments: GFP's baseline defines extension_good_faith_pct percent.

**CG-5 SOURCE-POLICY RED (XF pt 9) — scoped overwrites whose replaced_by defers out-of-scope cases to the very base clause the overwrite retires, instead of restating its in-force content.**

All members:
1. RLC overwrite of "The late charge is late_charge_pct_of_unpaid_installment percent of retail_msr_unpaid_installment_portion, capped…": "…and any other late charge remains under the base rule and is not figured under this policy".
2. ULC overwrite of the same clause: same tail.
3. LPC overwrite 1 of the same clause: same tail. None of the three restates "late_charge_pct_of_unpaid_installment percent of retail_msr_unpaid_installment_portion, capped at the lower of…" for the out-of-scope late charges (e.g. a past-due installment other than the next-due one).
4. ARR overwrite of the allocation clause "Each payment is applied in payment_allocation_order: …": "…and every other payment remains under the base rule and is not posted under this policy".
5. GFP overwrite 2 (the same allocation clause): same tail.
6. CUP overwrite of the same allocation clause: same tail. None restates the base's immediate allocation for other payments.

Counter-example in the same charter, which complies: LPC overwrite 2 restates the whole minimum-unpaid clause "for every other installment".

Not members: EXT's fee overwrite and GFP overwrite 1. Their scopes cover every case the retired clause governed (every extension requires the signed agreement EXT names, and the good-faith clause concerns only good-faith payments), so no out-of-scope remainder exists.

Observation O-15: the day-count convention sentence sits in the standard-method part of RLC, GFP, ULC and CUP, although only one factor per policy counts days (lrf_lapsed_grace, gff_overdue_interest, ucf_graduated, cpf_overdue_interest). It is a convention, not a quantity, so it is not counted under pt 4.

Neither CG-4 nor CG-5 changes a scored value on either task world. Both are charter-wide. They bear on rendering: computation documents that would reference factor schedules, and base documents whose retired clause has no restated text.

### revision_3 post-reveal note and closing (reveal 2026-10-15T22:26:39Z: worklog r3 closure + tasks/*.json)
- **Correction to CG-4.** This comes from my own re-reading of the recipe against its source lessons, not from any revealed value. The frozen text above is left as written.
  - Members 1, 2, 4 and 5 are **withdrawn**. "Any amount a schedule below deducts / includes / adds" is a single generic combination sentence that names no factor's quantity, which is what recipe pt 1 asks for. It differs from the recipe's bad form ("points from the four schedules below are added"), which counts and assembles named schedules.
  - **CG-4 stands with two members:**
    - (3) ARR: "the arrears share" is defined only by cuf_arrears_share. cuf_lessee_share and cuf_exposure contribute against it, and "the share adjustments are first combined into one share" combines those three factor quantities. ARR's baseline defines no share.
    - (6) CUP: "the pull-ahead percentages are first combined into one percentage" names the quantities of exactly cpf_repeat_pull and cpf_lease_pull, and cpf_lease_pull is worded as "a further … percent". CUP's baseline (past_due_amount) defines no pull-ahead. The combination is load-bearing, because it is rounded once.
- CG-5 stands as frozen (6 members).
- Reworker claims (worklog "REWORK round 3 closure") verified on disk:
  - CG-3 fix and its class sweep: ULC now uses the same as-of-assessment measure, and the exclusions are stated in its own rule.
  - Tie sentences, convention sentences, and the docstring "toward" removals.
  - The task-0 factor_trace now says "step 10".
  - The task-1 rationale no longer asserts a receipt time.
  - The worklog's XF table marks pt 1 as fixed for ARR and CUP and pt 9 as satisfied for all seven policies. I disagree with both as recorded in CG-4 (two members) and CG-5.
- Pt 12 proof text: task GT values, factor_trace and closure figures equal the recompute. Step numbers agree with evaluation_criteria (task 0: 10/12/14/16; task 1: 9/11/13; "Step 5" refers to the worklog procedure). Persona timing is unchanged from r2 and consistent.
- **Difficulty not closed:** charter-wide CG-4 and CG-5 remain. Both tasks PASS all four relationships on their worlds. No scored value changed in r3.

task0=PASS task1=PASS
charter=CG-4,CG-5
VERDICT revision_3: task0=PASS task1=PASS charter=CG-4,CG-5

## revision_4

### charter_global_frozen (round 4)
- Gating line `REWORK round 4: gates 8/8 green` confirmed.
- Gate snapshot: `.audit_views/policy/retail_payment_servicing/snapshot_r4.txt` (2026-10-15T23:45:35Z). All gates are green apart from the expected pre-render traceability (unlock tool_name) and validate (`documents: 0`) items.
- Hashes:
  - charter a5ce474b47808514 (r3 eb028b9db9f2999c), changed;
  - task_tools ac12a91b1d641727, unchanged;
  - views 0.json 9de058c0bd5499f6 and 1.json a4d408333a7d0b79, unchanged.
- Carried forward on hash grounds: the tools section (pt 11) and the task worlds / seed checks.
- Re-derived in full: the charter. Base copy byte-identical. XF_recipe.md unchanged since r3 (mtime 22:17Z).
- Masked at freeze: the worklog r4 closure and tasks/*.json.

### round-3 RED status (verified on the charter, before the claims were read)
- **CG-4: closed.**
  - ARR's baseline now defines the quantity: "The arrears share is standard_share_pct percent, and the arrears payment amount is the arrears share of the other past-due amount, rounded to the cent" (standard_share_pct = 100).
  - cuf_arrears_share now *replaces* that share. Its fall-through is K('standard_share_pct'), which equals its baseline.
  - The lessee and exposure points adjust the baseline-defined share.
  - The assembly sentence is generic and fixes the non-commuting order: "any replacement of the arrears share comes first, then every addition to it or deduction from it, giving one share …".
  - CUP's baseline now defines "the pull-ahead share is standard_pull_pct percent" (0), and both pull factors add points to it. "A further" is gone. The combination sentence is generic ("every addition to the pull-ahead share is first combined with it into one share …").
- **CG-5: closed.** All six members now restate the retired clause for out-of-scope cases:
  - the three late-charge amount overwrites: "…any other late charge is late_charge_pct_of_unpaid_installment percent of retail_msr_unpaid_installment_portion, capped at the lower of late_charge_company_max and the contract's recorded late_charge_max_amount, and is not figured under this policy";
  - the three allocation overwrites: "…every other payment is applied in payment_allocation_order when it posts, first to simple interest … any remainder to principal, and is not posted under this policy".
  - Each replaced_by is verbatim in its own rule.
- No regression:
  - Verbatim sweep: all 7 policies OK. Every policy_source, compute_basis quote, baseline sentence and replaced_by is in its rule; every superseded_clause is in its base; every binding has a basis.
  - Factor counts are unchanged (4 / 4 / 6 / 4 / 6 / 6 / 4; each has a parameter and a method factor).
  - The recompute on the unchanged views equals r3 for every value, sensitivity and baseline:
    - task 0: 4.00 / 545.83 / 467.41 / 4.00;
    - task 1: 5.00 / 4.00 / 1056.10, with skips 878.40 / 879.40.
  - The ARR all-baseline result is still 646.04 (100% × 646.04) and the CUP all-baseline result is still 590.82 (0% pull).

### XF_recipe sweep (round 4; every point × every policy)
| pt | RLC | ARR | GFP | EXT | ULC | LPC | CUP |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 assembly | ok | ok (share defined in the baseline) | ok | ok | ok | ok | ok (pull-ahead share defined in the baseline) |
| 2 non-commuting order | ok | ok (replacement → additions/deductions → apply + round → add) | ok | ok | ok | ok | ok |
| 3 independence | ok | ok | ok | ok | ok | ok | ok |
| 4 ownership | ok | ok | ok | ok | ok | ok | ok |
| 5 quotes | ok (sweep) | ok | ok | ok | ok | ok | ok |
| 6 ties | ok | ok | n/a | n/a | n/a | n/a | n/a |
| 7 counting | ok | ok | ok | ok | ok | ok | ok |
| 8 branches | ok | ok | ok | ok | ok | ok | ok |
| 9 base clauses | ok (tail restates) | ok | ok | ok | ok | ok | ok |
| 10 rounding | ok | ok | ok | ok | ok | ok | ok |
| 11 tools | ok (unchanged since r3) | | | | | | |
| 12 proof text | ok (both tasks) | | | | | | |

- Notes on pt 4: the arrears share and the pull-ahead share are each used by the baseline and by ≥ 2 factors, so they belong to the standard method. CUP's standard_pull_pct = 0 states truthfully that no pull-ahead applies by default, and the all-baseline result is still 590.82.
- Unedited policies: spot-checked against r3 (RLC, GFP, EXT, ULC and LPC still carry their r3 sentences). The only r4 edits are ARR, CUP, the six overwrite tails and proof text, which matches the worklog claims.
- Observations O-4, O-6, O-7, O-8, O-11, O-12, O-14 and O-15 stand (not grounds for rework).

### closing_checklist (revision_4, after reveal 2026-10-15T23:46:42Z)
- Per-task files have revision_4 appended. Both comparisons are PASS, and the r1–r3 text is untouched.
- Coverage: 7 policies, disjoint scopes, independent uuid8s.
- Trees: 3 and 2 prerequisite problems; 4 and 2 value_input edges; user writes GFP and CUP; acyclic.
- Factors: every computation has 4–6 factors with ≥ 2 parameter and ≥ 1 method. Each task has multi-source and lease cross-difficulty factors. Every factor bears weight. Every baseline is definite and ≠ gold. GT sensitivities equal the recompute.
- Charter-wide REDs CG-1 … CG-5: all closed. XF recipe: no member on any policy.
- Gates: snapshot_r4.txt is green apart from the expected pre-render items.
- **Difficulty closes at the policy-task source layer.**

task0=PASS task1=PASS
charter=CLEAN
VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

### charter_global_frozen (round 5)
- Gating line `REWORK round 5: gates 9/9 green` confirmed.
- Gate snapshot: `.audit_views/policy/retail_payment_servicing/snapshot_r5.txt` (2026-10-16T05:18:47Z). All gates are green, and TRACEABILITY is now OK (KB rendered).
- validate INVALID: 7 errors, all "required document not found", none for retail_payment_servicing (checked by listing validate_scenario's errors). They belong to other difficulties.
- Hashes:
  - charter 6751df5c00e8f851 (r4 a5ce474b47808514), changed;
  - task_tools 3c034a983b00db9a (r4 ac12a91b1d641727), changed;
  - views 0.json 9de058c0bd5499f6 and 1.json a4d408333a7d0b79, unchanged.
- Base copy byte-identical. XF_recipe.md unchanged since r3.
- Input this round: the KB auditor's source-side items in `audits/policy_kb/retail_payment_servicing/_difficulty.md`: SRC-1, SRC-2, and note N-4. My r4 verdict was PASS/CLEAN, so no policy-task RED was open.
- Masked at freeze: the worklog r5 closure and tasks/*.json.

### KB-auditor source items (verified on disk)
- **SRC-1 (payment tools posted "today" regardless of the cutoff rule): closed.**
  - The three payment tools now write `txn_date` and `last_payment_date` = `_PostingDay.posting_date(ctx.now())`.
  - That is today when the payment is received before 20:00 Central on a business day, and otherwise the next business day.
  - Business days exclude weekends and the 11 US federal holidays, with Sat → Fri and Sun → Mon observance. A New Year falling on Saturday is caught through the following year's set.
  - Probes run on the helper:
    - task 0 and task 1 frozen times → same day;
    - 2026-10-22 21:00 EDT (20:00 CT) → 10-23;
    - Fri 21:30 EDT → Mon;
    - Thanksgiving → next day;
    - 2026-12-31 22:00 EST → 2027-01-04;
    - 2027-12-30 21:30 EST → 2028-01-03 (observed New Year on Fri 12-31);
    - 2026-07-03 (observed July 4) → 07-06;
    - Columbus Day and Veterans Day → next day.
  - The docstrings state exactly this effect ("on its posting day, which is today when … earlier than 8:00 p.m. Central Time on a business day and otherwise the next business day …"). They claim nothing the body does not do and carry no example values. 8:00 p.m. is every tier's payment_cutoff_time_ct, the effect the body implements.
  - No sequence wording. Owners are unchanged (good-faith and catch-up are user; arrears is agent). uuid8s are unchanged.
- **SRC-2 (good-faith 0.00 branch against the grant's prerequisite): closed.**
  - GFP's replaced_by (in its rule) now keeps the base anchor: "…in place of extension_good_faith_pct percent of monthly_payment; before the extension is granted, a good-faith payment of at least that amount must still have posted since the most recent installment due date, and where the good-faith amount figured below is 0.00 no good-faith payment is required."
  - EXT's action-form sentence and condition are scoped to the positive case: "The extension fee is fixed only after the customer has made the good-faith payment toward the extension, wherever the good-faith amount for the extension is above 0.00." / condition "Where the good-faith amount for the extension is above 0.00, …".
  - The 0.00 branch is now waived in both texts. The four-point test passes ("only after"; action form with its fallback reason unchanged and still justified; strength = condition).
- **Observation O-16 (new; consequence not demonstrable, so not RED).** The restored anchor means the depended-on rule (GFP) now also states the cross-problem order "before the extension is granted, a good-faith payment … must still have posted". The skill prefers that the depended-on rule not restate the dependency. Both texts give the same order in every situation (GFP before EXT), and the declared edge rests on EXT's own sentence, so no second reading arises. The restatement is what XF pt 9 requires (restating the in-force part of the retired base clause).

### No regression
- Verbatim sweep: all 7 policies OK. Factor counts 4 / 4 / 6 / 4 / 6 / 6 / 4.
- Recompute on the unchanged views equals r4 for every value, sensitivity and baseline:
  - task 0: 4.00 / 545.83 / 467.41 / 4.00;
  - task 1: 5.00 / 4.00 / 1056.10.
- Both frozen times post the payments the same day, so the tool change moves no gold field.
- CG-1 … CG-5 remain closed. The arrears and pull-ahead shares are still defined in the baseline. The six overwrite tails still restate their clauses.

### XF_recipe sweep (round 5)
- Pts 1–7 and 10: unchanged policies, plus GFP and EXT re-read after their edits: all ok.
- Pt 8: the good-faith 0.00 branch is now stated consistently in both GFP and EXT.
- Pt 9: GFP overwrite 1 restates the anchor and names its scope; all 9 overwrites ok.
- Pt 11: the payment docstrings match the new bodies.
- Pt 12: checked per task after the reveal.
- No member on any policy.
- Latent observation O-17: a call after the cutoff posts a payment dated the next business day. "Has posted … since" (EXT←ARR) and the 1-month recent-payments window would then not see it until that day, i.e. a real wait. This follows the rule and is reachable by neither task (Mon and Thu, 10:20 EDT).

### closing_checklist (revision_5, after reveal 2026-10-16T05:20:53Z)
- Worklog "REWORK round 5 closure" claims verified on disk: SRC-1 (tools and helper), SRC-2 (GFP replaced_by + EXT sentence/condition + task-0 closure re-copied), N-4 (task-1 read text). The kept placement-only note and N-3 (outside this tree) remain unrouted, consistent with the KB auditor.
- Both tasks PASS all four relationships. Values, sensitivities and baselines are unchanged.
- Charter-wide REDs: none. CG-1 … CG-5 stay closed. XF recipe: no member on any of the 7 policies.
- Observations O-16 and O-17 were added this round; neither is grounds for rework. O-4, O-6, O-7, O-8, O-11, O-12, O-14 and O-15 stand.
- Gates: snapshot_r5.txt is green, including traceability. The remaining validate errors are other difficulties' "required document" items.
- **The difficulty closes at the policy-task source layer.**

task0=PASS task1=PASS
charter=CLEAN
VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN
