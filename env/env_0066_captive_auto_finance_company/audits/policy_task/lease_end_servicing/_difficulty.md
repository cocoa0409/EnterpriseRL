# Policy-task audit — lease_end_servicing / charter-global

## charter_global_frozen
- freeze time: 2026-10-15T20:19Z; auditor: erl-task-policy-audit (independent auditor, round 1).
- frozen inputs (sha256 prefix, matching the coordinator brief): `tasks/lease_end_servicing/lease.extended.yaml` 8c17de935ef56219; `tasks/lease_end_servicing/task_tools.py` ca9c2b3d79f263f2; masked views `.audit_views/policy/lease_end_servicing/0.json` 2a6f18a9f442fea1, `1.json` 5d6a69c414da858b.
- read: blueprint/ (lease.yaml, db_schema.json, share_tools.py, blueprint.yaml difficulty entry), the extended charter, task_tools.py, the masked views (frozen_time, user_scenario, initial_state only), erlbench DSL semantics (CFIELD = first matching row, `skills/erl-task-instantiate/scripts/check_compute.py` l.332-334; MONTHS = whole months, day-of-month floor, l.229-235).
- masked / not read before this section was written: tasks/lease_end_servicing/tasks/*.json, worklog.md, every evaluation_criteria / computations / closure / rationale field. Nothing below is derived from a revealed GT.
- Entry conditions: gate snapshot supplied (all gates green except the expected pre-render tool-name traceability miss and the pre-render validate "documents: 0"); masked views supplied with hashes, hashes re-verified identical. Entry conditions met.
- Base copy: `diff` of the extended file's base section against `blueprint/products/lease.yaml` differs only by one trailing blank line — verbatim.

### policy_conflict_scan
Extended policies: WF `lease_ext_wear_forgiveness` (agent, post_wear_forgiveness_925a15e3, state_due, prereq []), HOLD `lease_ext_charge_off_hold` (user, pay_end_of_term_hold_a939b773, on_request, prereq WF), XM `lease_ext_excess_mileage` (agent, bill_excess_mileage_a1b25aac, state_due, prereq []), PLAN `lease_ext_end_installment_plan` (user, start_lease_end_plan_44d05a38, on_request, prereq XM).
- Subjects/events: lease_end_charge_waiver (WF), lease_end_charge (XM), lease_end_of_term_payment (HOLD, PLAN) — all inside the claimed event types.
- Eligibility/status: WF and XM restate base `bill_status` (returned / early_terminated); XM restates base `dispute_elapsed`; HOLD/PLAN post under base `payable`. Compatible.
- Time anchors: all read turn_in_date, the end_of_term_invoice notice row, and NOW. Compatible except as in F-C4 (charge-off anchor).
- Terminal states / charge-off: HOLD and PLAN each override the base charge-off sentence and each defers to the other — contradictory (finding F-C4).
- Shared quantity: HOLD.end_balance and PLAN.plan_balance are the same transaction-sum; WF writes reduce it, XM writes raise it. HOLD waits only on WF, PLAN only on XM (observation O-C3); WF reads XM's billing state with no edge (finding F-C5).
- Scope: the two tasks (by the masked worlds and personas: task 0 = HOLD root over WF; task 1 = PLAN root over XM) are disjoint and jointly cover the four extended policies. Final scope confirmation against `charter_scope` is in each task's comparison section.

### rule_compute_equivalence
Every binding of the four policies carries a compute_basis quotation that is a substring of its rule (spot-checked binding by binding); every factor ladder tier is a rule sentence and a branch of its `decides` binding, and vice versa. Rounding: WF/HOLD/XM/PLAN "rounded to the cent" = RND(...,2); XM allowances "rounded down to a whole mile" = int(). Caps/floors: WF "never more than that remaining amount" = MN(forgivable_wear, ...), MX(0); XM "never below zero" = MX(0, ...).
Gaps (members of one class, finding F-C6):
1. CFIELD first-match reads where the rule is existential ("holds an active ... contract that ..."): WF retail_date/retail_dpd, balloon_date/balloon_dpd, tenure_payments (paid_in_full retail); HOLD retail_dpd, balloon_dpd, preowned_dpd; XM retail_date, balloon_date, preowned_date/preowned_dpd, care_financing; PLAN retail_dpd, balloon_dpd, preowned_dpd, balloon_paid_count (paid_in_full balloon). With two rows of one category/status (e.g. two active retail contracts: first dated outside the window, second inside with days_past_due 0) the rule gives the loyalty tier and compute gives the fall-through or past-due tier, depending on row order.
2. WF missing_items / tire_items and XM missing_count: rule "items assessed on the turn-in inspection" (WF), "clean-return" (XM); compute sums every `lease_wear_item_assessed` excess row of the lease with no `lease_inspection_id` filter (items recorded at the advance inspection are counted; base `wear_status` permits recording them while active) and ignores `lease_wear_item_adjusted` / item_status (an item removed_on_dispute still reduces WF's forgivable amount though base `lease_msr_excess_wear_total` has already dropped it from the charge).
3. XM autopay_count: rule "of the lease's monthly payments were made through autopay_ach"; compute counts every `lease_payment` with payment_channel autopay_ach, no payment_purpose filter and no exclusion of payments later returned.
4. PLAN monthly_payments: rule "the lease's posted monthly payments"; compute counts dishonoured (returned) monthly payments.

### action_binding_and_uuids
- (target_tool, computes): (post_wear_forgiveness_925a15e3, amount) WF; (pay_end_of_term_hold_a939b773, amount) HOLD; (bill_excess_mileage_a1b25aac, amount) XM; (start_lease_end_plan_44d05a38, amount) PLAN — each claimed once. Share tools are read-only finders plus verify/transfer; no share tool writes lease_end_charge, waivers or end-of-term payments.
- uuid8s 925a15e3, a939b773, a1b25aac, 44d05a38: distinct, no shared prefix/suffix pattern, no sequence; consistent with independent generation.
- Docstrings: no other tool named, no before/after/first ordering of actions. "The lessee then sees ..." (WF, XM) describes the visible effect, not a sequence (observation only). No example values in any docstring (no gold leak).
- Tool bodies validate nothing (no status, prerequisite, eligibility or amount check); none refuses, errors or hints.
- Terminal-record overlap: HOLD and PLAN tools write identical lease_transactions rows (event_type lease_end_of_term_payment, payment_channel phone_ivr_ach, payment_purpose end_of_term_charges); "under a plan" and "received a hold payment" are not record-distinguishable (feeds F-C4).

### prerequisite_graph
- `prerequisite` filled everywhere: WF [], XM [], HOLD [WF], PLAN [XM]. Problems point at extended ids in this file, never base, never self. Graph acyclic (two disjoint single edges).
- HOLD→WF: kind value_input, gate `end_balance` (exists in HOLD compute), form state, no fallback_reason (correct), resolved_by post_wear_forgiveness_925a15e3 = WF.target_tool; effect true (waiver row is subtracted in end_balance). policy_source verbatim in HOLD.rule.
- PLAN→XM: kind value_input, gate `plan_balance` (exists), form state, resolved_by bill_excess_mileage_a1b25aac = XM.target_tool; effect true (charge row summed in plan_balance). policy_source verbatim in PLAN.rule.
- Conditions: HOLD condition adds "booked for the amount the wear forgiveness rule figures" — equal in strength to "the wear forgiveness waiver owed on it", except where WF figures 0.00 (then the sentence asks for no waiver while the condition still names a waiver row; the tool also requires a positive amount) — observation O-C1. PLAN condition ("When the miles driven exceed the mileage allowance as the excess mileage rule figures it ...") equals "every excess mileage charge owed". No authoring-viewpoint wording.

### prerequisite_sentences
- HOLD: "The hold payment is fixed only after every excess wear charge billed for the turn-in carries the wear forgiveness waiver owed on it." Connective "only after"; waits on a record-visible state (a wear-forgiveness waiver row naming the excess wear charge); no tool, id or snake_case token; strength matches condition. Exactly one write produces a wear_forgiveness waiver: WF's tool (base has no write tool; share tools read-only). Derivation: sentence -> look for an excess_wear_charge row without a wear_forgiveness waiver -> WF rule ("booked as one waiver with waiver_reason wear_forgiveness that names the excess wear charge") is the only rule producing that state -> WF figured and posted, then HOLD figured. Single reading.
- PLAN: "The first installment of a lease-end installment plan is not fixed until every excess mileage charge owed for the turn-in stands billed on the lease." Connective "not ... until"; state form; no tool/id; exactly one producer (XM's tool). Derivation: sentence -> XM rule decides whether a charge is owed and its amount -> billed -> PLAN figured. Single reading.
- Neither depended-on rule (WF, XM) restates the sentence; no rule carries a second wording. No rule states a cross-problem order that grounds no edge; but WF reads a state XM produces with no sentence at all (F-C5). Base sentence "Any security deposit is applied to the end-of-term balance first" states an order but grounds no tree (observation).

### override_declarations
WF (refs end_of_term_charges, turn_in_and_inspection, inspection_dispute): base "wear_forgiveness_cap for the tier is then waived from it ... up to the amount billed" and "When the loyalty condition is met, loyalty_wear_forgiveness_cap replaces wear_forgiveness_cap" — both declared, replaced_by verbatim in rule; status, waive-once and qualifying-account sentences followed; turn_in_and_inspection and inspection_dispute sentences followed (but see F-C6 item 2 for the adjustment-blind compute). Disposition loyalty waiver left under base (declared).
HOLD (refs end_of_term_charges, payment_posting): base charge-off sentence declared; due-date, posting, channel-fee and booking sentences followed.
XM (refs end_of_term_charges, early_termination, maturity_extensions, turn_in_and_inspection): base "Excess mileage is lease_msr_miles_over ..." , ET proration sentence and extension-growth sentence all declared; status and dispute-elapsed sentences restated. Base measure lease_msr_months_elapsed (partial month counts whole) replaced via the declared ET sentence by "whole months" (MONTHS floor) — declared.
PLAN (refs payment_posting, end_of_term_charges): due-date and charge-off sentences declared; posting sentences followed.
No undeclared override found. Merged semantics unique per policy, except the HOLD/PLAN mutual deferral (F-C4).

### factor_ladders
| policy | factor | label | ladder (values) | tiers in rule | multi-source tier | cross_difficulty |
|---|---|---|---|---|---|---|
| WF | brand_return_cap | parameter | loyalty cap / 250 / wear_forgiveness_cap | yes | tier1 (retail OR balloon) AND date AND dpd | retail (+balloon) |
| WF | punctual_addition | parameter | 150 / 75 / 0 | yes | no | — |
| WF | forgiving_scope | method | whole charge / less keys+equipment / less keys+equipment+tires | yes | inspection row vs wear items | — |
| WF | tenure_addition | parameter | 200 / 100 / 0 | yes | no | retail |
| WF | low_mileage_addition | parameter | 150 / 75 / 0 | yes | tier1 mileage-charge rows AND lease odometer | — |
| HOLD | stage_rate | parameter | .25 / .35 / .50 | yes | no | — |
| HOLD | relationship_relief | parameter | .10 / .05 / 0 | yes | tier1 retail OR balloon | retail (+balloon, preowned) |
| HOLD | returned_relief | parameter | .05 / .02 / 0 | yes | no | — |
| HOLD | hold_shape | method | TMP + rate x (bal-TMP) / whole bal / rate x bal | yes | no | — |
| XM | allowance_convention | method | by day / by whole month / standard | yes | no | — |
| XM | brand_miles | parameter | 3000 / 1500 / 0 | yes | tier1 retail OR balloon; tier2 preowned AND dpd | preowned (+retail, balloon) |
| XM | autopay_buffer | parameter | 1000 / 500 / 0 | yes | no | — |
| XM | rate_schedule | parameter | rate-.05 / rate-.02 / rate | yes | same record | — |
| XM | clean_return_miles | parameter | 1000 / 500 / 0 | yes | tier1 charges AND wear items | — |
| XM | care_holder_miles | parameter | 1000 / 500 / 0 | yes | no | care |
| PLAN | punctuality_installments | parameter | 4 / 3 / 2 | yes | no | — |
| PLAN | relationship_installments | parameter | 2 / 1 / 0 | yes | tier1 retail OR balloon | preowned (+retail, balloon) |
| PLAN | completion_installments | parameter | 2 / 1 / 0 | yes | no | — |
| PLAN | tenure_installments | parameter | 2 / 1 / 0 | yes | no | balloon |
| PLAN | first_shape | method | share+TMP / half balance / share | yes | no | — |
| PLAN | setup_fee | parameter | 0 / 15 / 35 | yes | no | — |
Counts: WF 5 (4 parameter, 1 method), HOLD 4 (3, 1), XM 6 (5, 1), PLAN 6 (5, 1) — all within 4-6, >=2 parameter, >=1 method. Every factor's baseline equals its fall-through tier and equals what `baseline.rule` states (WF: tier cap, scope less keys/equipment/tires, no additions; HOLD: standard rate x whole balance; XM: standard allowance, disclosed rate, no credits; PLAN: balance / standard installments + standard fee). Bindings of each factor disjoint; no `decides` is `result`; no factor reads another factor's output. Labels honest (method tiers change the algorithm; parameter tiers a number).
Ladder reality / distinctness — failures: F-C1 (WF brand_return_cap), F-C2 (PLAN first_shape), F-C3 (XM allowance_convention), F-C5 (WF low_mileage_addition tier boundary). Realism observations: O-C2.

### findings
**F-C1 — SOURCE-FACTOR RED (unreal ladder: two tiers one value; inverted tier).** Symptom: WF brand_return_cap tier 2 is `K('past_due_return_cap')` = 250.0 for every tier, fall-through is `P('wear_forgiveness_cap')`. Evidence: variants Tier 3 and Tier 2 `wear_forgiveness_cap: 250.0` -> tier 2 and fall-through select the same value 250.0; Tier 1 (500.0) and Tier 1+ (750.0) -> a customer who came back to the brand but is past due on the new contract gets 250.0, less than a customer who never came back (500/750). No captive publishes a return-to-brand tier that leaves the returning customer below the non-returning default. Affected: lease.extended.yaml WF params.past_due_return_cap, rule sentence "it is the past-due return-to-brand cap when ...", factors[brand_return_cap]. Tasks: no current task world sits on tier 2 or on Tier 3/2/1/1+ (task 0 is Tier 5); the defect is published to every reader of the charter.

**F-C2 — SOURCE-FACTOR RED (tier method no business would publish).** PLAN first_shape tier "after that due date but no more than the catch-up window ... it is the equal share plus one total_monthly_payment" has no cap at the balance. Demonstration on task 1's own opening world (balance 395.00, 9 installments, TMP 697.29, 10 days past the due date): first installment 395.00/9 + 697.29 = 741.18 > the 395.00 owed. Any lessee with a balance below TMP x n/(n-1) is told to pay more than the whole debt as the first installment of a plan. Affected: PLAN rule shape sentence, compute flat_add/share_coef, factors[first_shape]. Bears on task 1 (see 1.md).

**F-C3 — SOURCE-FACTOR RED (ladder tiers overlap as stated).** XM allowance_convention: "The mileage allowance of a lease turned in during a maturity extension, before its current maturity_date, runs by the day ...; the mileage allowance of a lease that ended in a pull-ahead or an early termination runs by the whole month ..." — the rule states no precedence; compute silently gives the day method priority. Reachable under base: Tier 1+ (max extension 6, pull_ahead_max_remaining_payments 4) lessee extended 6 months, turns in after 2 extension months, >90 days before the new maturity_date, with a new Kestrel contract signed in the window -> pull_ahead recorded (status returned, permitted from maturity_extended) while mid-extension. Two allowances, e.g. lease_date 2023-07-15, turn-in 2026-08-20, 12,000/yr: by day int(12000x1132/365)=37,216, by month 12000/12x37=37,000. Affected: XM rule allowance sentence, compute mileage_allowance. Task 1 is scheduled_end (not on the overlap).

**F-C4 — SOURCE-POLICY RED (mutual deferral, terminal state undefined).** HOLD.rule: "For a lease whose end-of-term balance receives a hold payment, and only for such a lease, the balance left after the hold payment is not charged off until hold_period_days calendar days after the hold payment posts; a balance under a lease-end installment plan follows the installment plan rule instead". PLAN.rule: "For a lease whose end-of-term balance is under a lease-end installment plan, and only for such a lease, ... the balance is not charged off while every installment already due has been paid; a balance that received a hold payment follows the hold payment rule instead". A balance that both received a hold payment and is under a plan is sent by each rule to the other: charged off hold_period_days after the hold posts vs never while installments are current. Aggravated by the HOLD definition ("the lessee's own payment toward an end-of-term balance that is still unpaid after the due date ..., made ... through the self-service payment line from the lessee's own bank account and booked as one end-of-term payment"), which any plan installment made after the invoice due date also satisfies, and by the two tools writing identical rows. Bears on task 1 (its enrolment payment meets the hold definition; see 1.md) — no scored value moves.

**F-C5 — SOURCE-POLICY RED (undeclared value dependency, order-dependent result; tier boundary is billing timing).** WF.rule: "it is the standard low-mileage addition when no excess mileage charge was billed and the miles driven fall short of that allowance by less than the low-mileage margin or not at all; it is nothing when an excess mileage charge was billed for the turn-in." WF's amount reads the state XM's write creates, but WF carries no prerequisite sentence and both are state_due. Demonstration (task 0's lease with turn_in_odometer 42,012 instead of 31,262): XM owes 42,000 - (36,000 + 3,000 brand + 1,000 autopay) = 2,000 mi x 0.25 = 500.00; WF before XM = min(2425, 500+75+200+75) = 850.00, WF after XM = 775.00 — two terminal states, no rule fixes the order. The tier-2 phrase "or not at all" also gives a low-mileage addition to a lessee who drove over the allowance whenever the mileage bill has not posted yet — a condition no lessor weighs. Affected: WF rule low-mileage sentence, compute mileage_charges/low_mileage_addition, WF prerequisite []. No current task world has both writes pending.

**F-C6 — SOURCE-POLICY RED (rule/compute non-equivalence; decoy guards missing).** All members listed under rule_compute_equivalence items 1-4 (CFIELD first-match on existential reads; wear-item sums without turn-in-inspection filter or dispute adjustments; autopay count without monthly-payment filter or returned-payment exclusion; posted-payment count including returned payments). In each described situation the rule and the compute reach different tiers. No current task world contains the decoy (task 0 has one returned autopay payment, but XM/PLAN are not computed there).

Observations (not grounds for rework):
- O-C1: HOLD prerequisite condition presumes a positive WF waiver; when WF figures 0.00 the sentence is satisfied with no waiver while the condition names one, and the tool documents a positive amount.
- O-C2 (realism): WF forgiving_scope forgives missing keys/equipment only when the advance inspection was >=30 days before turn-in — the customer who learned of the missing items earliest is forgiven most; XM clean_return_miles and care_holder_miles convert wear condition / service-contract holding into mileage credit; XM day-method allowance gives a mid-extension lessee less allowance than the extension months paid (task 1: 37,216 vs 38,000 after 38 paid payments); PLAN can reach 10 installments for an end-of-term bill. Each is a plausible published company schedule; noted, not red.
- O-C3: HOLD waits only for WF and PLAN only for XM although both read the same balance; in a world where the other sibling write is also pending, "as it stands" leaves the agent to decide whether to post it first.
- O-C4: Seeded openings leave a state_due write undone long after billing (task 0: no wear forgiveness 89 days after the invoice; task 1: excess mileage unbilled 40 days after the 2026-09-04 invoice that billed the disposition fee). Explicable, noted for realism.
- O-C5: XM "billed once for the turn-in as one charge" can be read as requiring a 0.00 charge when no miles are owed; WF's low-mileage tier then flips to "nothing". PLAN's prerequisite condition and the seeded billing runs (no 0.00 rows) point the other way.

## closing_checklist
Written after both reveals (2026-10-15T20:21:35Z onward). The difficulty is NOT closed:
- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; _difficulty.md alongside; first revision, nothing superseded.
- Comparison sections: task 0 — SOURCE-TASK RED (T0-1: plan first installment 700.00 < hold 712.08 for "the least you have to pay today") and SOURCE-FACTOR RED (T0-2: WF has 3 surviving factors after F-C1/F-C5); task 1 — SOURCE-FACTOR RED (T1-1: XM and PLAN each lose their only method factor to F-C3/F-C2). Both frozen derivations match GT on every scored parameter, tool, owner, order and terminal state (925.00, 712.08, 1445.32/6284, 901.77) and every factor_sensitivity / baseline_result figure.
- Coverage/scope: the four extended policies are covered; task scopes {WF, HOLD} and {XM, PLAN} pairwise disjoint; task tools closed; uuid8s independent.
- Trees: each task one prerequisite problem, one value_input edge, a user-owned root write, acyclic; whole-difficulty graph acyclic.
- Charter-wide REDs open: F-C1, F-C2, F-C3, F-C4, F-C5, F-C6 (see findings).
- Instantiation-stage gates: not re-run by this auditor (closing out a failed difficulty; the coordinator's round-1 snapshot stands as the entry record).

task0=SOURCE-TASK+SOURCE-FACTOR RED task1=SOURCE-FACTOR RED
charter=F-C1,F-C2,F-C3,F-C4,F-C5,F-C6

## revision_2
### charter_global_frozen (revision_2)
- Written 2026-10-16 (UTC) before reading the worklog "REWORK round 2 closure" section or tasks/*.json of this round. Gating: worklog tail `REWORK round 2: gates 7/7 green`. Gate snapshot: `.audit_views/policy/lease_end_servicing/snapshot_r2.txt` (all gates green; only the expected pre-render tool-name traceability miss and "documents: 0").
- Hashes: lease.extended.yaml eea1f3021cfc6ae6 (r1 8c17de935ef56219), task_tools.py 07fc4610eef8dfb9 (r1 ca9c2b3d79f263f2), views 0.json 3210811036c4afa0, 1.json d8b82ef455d1b181. Both shared inputs changed, so every charter-global section is re-derived in full below. Base copy still verbatim (diff = one trailing blank line).
- Also checked: every point of `audits/render_source/XF_recipe.md` on all four extended policies.

### policy_conflict_scan (r2)
- HOLD scope now "due date ... passed more than the hold-start day count earlier and on which no end-of-term payment has posted since that invoice was mailed"; PLAN scope "has not yet come or passed no more than the enrollment window of days earlier, and on which no end-of-term payment has posted since that invoice was mailed"; hold_start_days = enrollment_window_days = 30. Scopes are disjoint, and each rule says a balance in the other's case never enters its own. The mutual deferral of round 1 is gone.
- HOLD's balance ("invoiced end-of-term balance": charges billed on the invoice day) no longer moves with a later excess mileage charge. PLAN's balance ignores waivers ("credited to the plan's last installments"), so it no longer moves with a wear-forgiveness waiver. Siblings no longer feed the root they do not gate (round-1 O-C3 closed). WF no longer reads XM's billing state (F-C5 closed).
- New cross-policy conflict: R2-2 (below).

### rule_compute_equivalence (r2)
Script sweep: every compute_basis quote, policy_source, replaced_by and baseline.rule is verbatim in its own rule; every superseded_clause is verbatim in its base policy; binding sets equal basis sets in all four policies. Round-1 F-C6 members:
1. First-match reads: each rule now states "Wherever this rule reads a contract of another Kestrel product [or a Kestrel Care plan] in a stated status, it reads the first contract in that status that the customer's records for that product list" — rule = CFIELD. Closed as an equivalence defect (realism note O2-1).
2. Wear items: WF and XM now filter to the latest turn_in_final report (tie: first recorded, = LATEST keeps first); XM subtracts items removed on dispute; WF avoids adjusted items by widening scope (see R2-1). Closed as equivalence.
3. XM autopay: monthly_payment filter added; rule and compute both subtract every returned payment of the lease. Closed (O2-2).
4. PLAN completion: rule and compute both subtract returned payments. Closed.
No new rule/compute gap found.

### action_binding_and_uuids (r2)
Same four (target_tool, computes) pairs, same uuid8s. Docstrings: "then" removed; no ordering word (grep before/after/first/then/ahead/toward: none); no example values; each claims only effects in its body (XM amount now "positive", consistent with "no charge billed when zero"). Bodies validate nothing.

### prerequisite_graph / prerequisite_sentences (r2)
Unchanged edges and sentences (HOLD->WF, PLAN->XM, state form, verbatim in own rule, single producer each). HOLD condition now "whenever the wear forgiveness rule figures a positive amount", matching WF's "when wear forgiveness figures to zero no waiver is booked" (O-C1 closed). Acyclic.

### override_declarations (r2)
WF, HOLD, PLAN overwrites as round 1, with replaced_by texts now naming the sibling's case. New XM overwrite of base "An end-of-term invoice is mailed when charges are billed" with replaced_by "An excess mileage charge billed under this rule is added to the lease-end account without a separate end-of-term invoice and falls due end_of_term_payment_days calendar days after the day it is billed, unless the balance is enrolled in a lease-end installment plan ...". Conflict with PLAN's replaced_by: R2-2.

### factor_ladders (r2)
Counts unchanged (WF 5: 4p/1m; HOLD 4: 3p/1m; XM 6: 5p/1m; PLAN 6: 5p/1m). Round-1 ladder REDs:
- F-C1 closed: tier 2 now (wear_forgiveness_cap + loyalty_wear_forgiveness_cap)/2: Tier 5/4 250, Tier 3/2 500, Tier 1 750, Tier 1+ 1125. That is strictly between the fall-through and the loyalty cap in every tier.
- F-C2 closed: the PLAN shape is now keyed to balance size: above 2 TMP, one TMP down plus (balance - TMP)/n; at or below 1 TMP, the whole balance; otherwise balance/n. No tier exceeds the balance.
- F-C3 closed: precedence is now stated ("pull-ahead or early termination" first; "any other lease turned in during a maturity extension" by the day).
- F-C5 closed: the low-mileage tiers now read only shortfall against the allowance (high >= margin, standard > 0, nothing at or above the allowance).
- New: R2-1 (WF forgiving_scope).

### XF_recipe sweep (r2) — every point, every policy
1 assembly: one generic combination sentence per policy (WF "its cap or its scope takes the place ... every amount a schedule adds is added to the cap"; HOLD, XM, PLAN analogous). Pass.
2 order: WF replace -> add -> min/floor; HOLD reliefs before the rate is applied; XM credits added to the allowance before comparison; PLAN installments added before division, fee last. Pass.
3 independence: shared selections are plain bindings (HOLD invoice_date); final_report is used by one factor per policy; no factor reads another's output. Pass.
4 ownership: no "as another policy figures it" phrase in any rule. Pass.
5 quotes: script sweep clean. Pass.
6 ties: first-contract, latest turn_in_final (first recorded on tie), latest invoice/advance inspection are stated and match the DSL. Pass.
7 counting: WF, HOLD and XM state their DAYS/MONTHS conventions and match. PLAN does not — member R2-3.
8 branches: absent final report, zero forgiveness, zero miles charged, no invoice / out-of-scope (stated outside the rule), negative shortfall — all stated both ways. Pass.
9 base clauses: R2-2 (PLAN's restated due-date clause and XM's no-invoice due date contradict for XM charges; PLAN's replaced_by does not name XM's case retiring the same clause).
10 rounding: matches in all four. Pass.
11 tools: pass.
12 proof text: checked per task after the reveal.

### findings (r2)
**R2-1 — SOURCE-FACTOR RED (unreal ladder condition, new).** WF forgiving_scope tier 1 now reads "... at least repair_lead_days calendar days before turn_in_date or when any wear item of the lease was adjusted on an inspection dispute". The disjunct makes missing keys, missing equipment and tires forgivable whenever the lessee won an adjustment on any item. No lessor weighs a dispute outcome on one item when deciding whether unrelated missing keys are forgivable. The disjunct exists only to keep the compute from netting adjusted charges. Demonstration: no advance inspection; items: missing key 375 and a dent 175 removed on dispute (repair invoice). Without the adjustment the forgivable amount excludes the 375 key. With it, the whole charge (375) is forgivable, so the dispute win on the dent turns the key forgivable. Affected: WF rule scope sentence, compute forgivable_wear/adjusted_items, factors[forgiving_scope]. This is WF's only method factor.
**R2-2 — SOURCE-POLICY RED (XF 9, new).** PLAN replaced_by (both overwrites): "... and for every other end-of-term balance the charges are due end_of_term_payment_days calendar days after the invoice ... as the base rule states." XM rule: "An excess mileage charge billed under this rule is added to the lease-end account without a separate end-of-term invoice and falls due end_of_term_payment_days calendar days after the day it is billed". Take a lease not in a plan with an excess mileage charge billed after the invoice. PLAN's text says the charge is due 30 days after the (earlier) invoice; XM's says 30 days after billing. Two due dates, and PLAN's replaced_by does not name XM's case that retires the invoice clause. Not scored in either task.
**R2-3 — SOURCE-POLICY RED (XF 7, new).** PLAN scope "has not yet come or passed no more than the enrollment window of days earlier" states no day-count convention. HOLD states its own ("counted from the day after the due date through today") with "more than the hold-start day count". On day 30 or 31 after the due date the two scopes can leave a gap or overlap depending on the convention a reader picks for PLAN. Neither task sits near the boundary (59 and -18 days).
Observations: O2-1 "first contract ... the records list" is a DSL convention stated as policy; a customer with two active same-product contracts gets a tier by listing order (realism). O2-2 XM autopay credit subtracts every returned payment, not only returned autopay payments. O2-3 HOLD's invoiced balance subtracts "every waiver" including waivers of charges billed on other days, which are not part of it. O2-4 PLAN computes the first installment on a balance that ignores already-posted waivers (credited to the last installments). O2-5 XM charges are billed without any invoice. O2-6 (carried) WF's low-mileage allowance is never prorated, so an early-terminated lease reads as low-mileage. O2-7 the PLAN/HOLD "whole balance when at most one TMP" tiers make the "first installment" a payoff for small balances.

### round-1 RED status (r2, after reveal at 2026-10-16T00:02:20Z)
| r1 id | status | evidence |
|---|---|---|
| F-C1 | closed | halfway tier, distinct in every tier sheet |
| F-C2 | closed | shape keyed to balance; never above the balance |
| F-C3 | closed | precedence stated; counting matches MONTHS/DAYS |
| F-C4 | closed | disjoint scopes (> 30 vs <= 30 days, no payment since invoice); no mutual deferral |
| F-C5 | closed | low-mileage reads shortfall only; HOLD/PLAN balances immune to the sibling write |
| F-C6 | closed (all 4 members) | rule states first-listed read; turn-in report filter; returned payments netted in rule and compute |
| T0-1 | closed | plan out of scope at 59 days |
| T0-2 | open, new cause | R2-1 strikes WF forgiving_scope (only method factor) |
| T1-1 | closed | both method factors sound |
| O-C1, O-C5, O-T0-1, O-T1-1..3 | closed | see task files |
Worklog claims verified against the artifacts. Every claim holds, except that T0-2's "5 genuine factors" is contradicted by R2-1. The claimed XF table marks point 7 "n/a" for PLAN, but the PLAN scope does state a day count (R2-3), and point 9 "Y" is contradicted by R2-2.

## closing_checklist (r2)
- Files 0.md / 1.md / _difficulty.md carry revision_2 appended; revision_1 text untouched.
- Coverage and scope: {WF, HOLD} and {XM, PLAN} disjoint and complete; tools closed; uuid8s independent.
- Trees: one prerequisite, one value_input edge, user-owned root each; graph acyclic.
- Both frozen r2 derivations match GT on every scored value. The only differences are two non-scored half-cent figures in task 1.
- Not closed: charter REDs R2-1 (task 0 factor floor), R2-2, R2-3. Gates per snapshot_r2.txt (7/7 green, expected pre-render traceability/validate notes).

task0=SOURCE-FACTOR RED task1=PASS
charter=R2-1,R2-2,R2-3
VERDICT revision_2: task0=SOURCE-FACTOR RED task1=PASS charter=R2-1,R2-2,R2-3

## revision_3
### charter_global_frozen (revision_3)
- Written 2026-10-16 before reading the worklog "REWORK round 3 closure" section or tasks/*.json of this round. Gating line `REWORK round 3: gates 7/7 green`. Gate snapshot `.audit_views/policy/lease_end_servicing/snapshot_r3.txt` (all green; expected unlock tool-name traceability miss; validate still INVALID with documents 169).
- Hashes: lease.extended.yaml 093b905993648968 (r2 eea1f3021cfc6ae6), changed, so the charter-global sections are re-derived below. task_tools.py 07fc4610eef8dfb9, unchanged from r2, so action_binding_and_uuids (r2) is carried forward on that hash. Views 0.json 3210811036c4afa0 and 1.json d8b82ef455d1b181 are unchanged from r2.
- Changes found on disk:
  - WF: the scope factor is replaced by `forgiveness_basis` (method). Per item ($100 per excess item, capped by the charge and the total limit) when an advance inspection was performed and the turn-in report has more than 5 excess items; 50% share of the charge when no advance inspection was performed; aggregate otherwise. The baseline is now "the excess wear charge billed ..., never more than the tier's wear_forgiveness_cap".
  - All four policies: "rounded to the nearest cent with a half cent rounded up", with RND(x + half_cent_guard).
  - PLAN: its scope now states the day-count convention, and its replaced_by now names the excess-mileage charge billed without an invoice.

### re-derived checks (r3)
- Script sweep: every compute_basis quote, policy_source, replaced_by and baseline.rule is verbatim in its own rule; every superseded_clause is verbatim in base; binding sets equal basis sets. Clean.
- Prerequisite graph and sentences: unchanged (HOLD->WF, PLAN->XM, state form, single producer, acyclic).
- Overwrites: WF/HOLD/XM unchanged. PLAN replaced_by now restates the in-force due-date clause for out-of-scope balances and carves out "an excess mileage charge billed without an invoice, which falls due as the excess mileage rule states". It now agrees with XM's replaced_by. R2-2 closed.
- PLAN scope: "the days since the due date being counted from the day after the due date through today, so that a due date not yet passed counts zero days". This is the same convention HOLD states. Day 30 falls to PLAN (<= 30), day 31 to HOLD (> 30): disjoint and complete. R2-3 closed.
- WF forgiveness_basis:
  - Tiers: (a) advance inspection performed AND turn-in report > 5 excess items; (b) no advance inspection; (c) otherwise. Pairwise disjoint, three distinct methods, and the fall-through equals the baseline (forgivable_wear = wear_charge).
  - Realistic: a lessee warned at an advance inspection who still returns many excess items gets per-item limits; skipping the inspection halves forgiveness.
  - Multi-source tier (a): inspection row plus wear items.
  - The dispute disjunct is gone, and removed-on-dispute items are excluded from the count in both rule and compute. R2-1 closed.
  - Equivalence note: the rule says "each excess item is forgiven up to the per-item limit", while the compute uses MN(charge, 100 x count). These are equal because every wear_charge_schedule entry in every tier is >= 120.00 (min 120.00 on all six sheets). Observation O3-1: hidden dependency on the schedule floor.
- Factor counts: WF 5 (4p/1m), HOLD 4 (3p/1m), XM 6 (5p/1m), PLAN 6 (5p/1m). No factor reads another's output (forgiveness_basis reads wear_charge, a plain binding).
- XF_recipe sweep, all 12 points on all four policies:
  - 1 assembly: one generic sentence per policy ("its cap or its forgiveness basis takes the place ... every amount a schedule adds is added to the cap before the forgiveness basis is applied against that total limit"). Pass.
  - 2 order: stated. Pass.
  - 3 independence: pass.
  - 4 ownership: pass.
  - 5 quotes: pass.
  - 6 ties: first-listed contract, latest turn-in report (first recorded on a tie), latest invoice. Pass.
  - 7 counting: now stated in all four. Pass.
  - 8 branches: absent turn-in report counts no item; zero forgiveness books no waiver; zero miles bill nothing; out-of-scope stated. Pass.
  - 9 base clauses: pass (R2-2 closed).
  - 10 rounding: the half-up sentence matches RND(x + 1e-06, 2) in all four. Pass; round-2 O2-T1-1 closed.
  - 11 tools: unchanged, pass.
  - 12 proof text: checked per task after the reveal.
- Charter-wide REDs open at freeze: none. Observations O2-1..O2-7 carried (realism, not red) and O3-1.

### round-2 RED status (r3, after reveal 2026-10-16T01:20:52Z)
| r2 id | status |
|---|---|
| R2-1 | closed: dispute disjunct removed; new forgiveness_basis is disjoint, realistic and bears weight |
| R2-2 | closed: PLAN replaced_by names the no-invoice mileage case; matches XM |
| R2-3 | closed: PLAN scope states HOLD's day count; scopes disjoint and complete |
| O2-T0-1 / O2-T1-1 | closed |
- Regression check: every round-1 closure still holds (F-C1..F-C6, T0-1, T1-1, O-C1, O-C5); no new decoy read (excess_item_count is filtered to the turn-in report and net of removals; first-listed reads stated). Seed rows are unchanged from r2 (same view hashes) and were checked in r2.
- Worklog round-3 claims verified against the artifacts; all hold.
- Observations carried, not red: O2-1..O2-7 and O3-1.

## closing_checklist (r3)
- 0.md / 1.md / _difficulty.md each carry revision_3 appended; revisions 1 and 2 untouched.
- All four relationships PASS for both tasks. Scopes {WF, HOLD} and {XM, PLAN} disjoint and complete; tools closed; uuid8s independent.
- Each tree has one prerequisite, one value_input edge, a user-owned root, and is acyclic.
- Every computation has a self-sufficient baseline whose fall-back differs from gold (0.00 vs 900.00; 697.50 vs 717.83; 2,500.00 vs 1,468.09; 966.55 vs 826.82). Each has 4-6 factors with at least 2 parameter and 1 method, all bearing weight. Multi-source and cross-difficulty factors are present per task.
- XF_recipe: all 12 points pass on all four policies.
- Gates re-run on the final form: snapshot_r3.txt, 7/7 green (expected pre-render traceability note).

task0=PASS task1=PASS
charter=CLEAN
VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4
### charter_global_frozen (revision_4)
- Written 2026-10-16 before reading the worklog "REWORK round 4 closure" section or tasks/*.json of this round.
- Gating: `REWORK round 4: gates 7/7 green`. Gate snapshot `.audit_views/policy/lease_end_servicing/snapshot_r4.txt`: 7/7 green, with the expected pre-render traceability/validate notes.
- Input this round: the renderer stop report `audits/render_source/lease_end_servicing/render_r1.md` (4 mismatches and 1 placement note), read in full.
- Hashes: lease.extended.yaml 7e29b687e1161ed2 and task_tools.py 03a0ed5a4a388aa1 both changed. Views 0.json 3210811036c4afa0 and 1.json d8b82ef455d1b181 are unchanged.
- Self-correction: the renderer's mismatches 1-3 existed in the round-3 source and my revision_3 missed them. Revision_3's CLEAN verdict was wrong on those three points; they are recorded here as round-3 misses, and the revision_3 text is left untouched.

### renderer items, verified in the source (r4)
1. **Qualifying-account tie: closed.** The WF rule now says the qualifying account number "is the account_number of the contract that meets that cap's conditions, an active Kestrel new-vehicle retail contract taking precedence over an active Kestrel balloon contract when both meet them". Within one product, the first-listed sentence already decides. One reading in every case: loyalty cap through a balloon while the retail is past due gives the balloon; halfway cap with both in the window gives the retail.
2. **Halfway cap, rule vs docstring: closed.**
   - The rule now covers every cap tier. Loyalty and halfway caps carry the account number of the contract that meets that cap's conditions; "when the cap is the tier's wear_forgiveness_cap the qualifying account number is left empty".
   - The docstring now defers to the rule: "the qualifying account number the wear forgiveness rule names for this waiver ... or an empty string when the rule names none".
   - No second reading remains.
3. **Retirement too wide: closed.**
   - The superseded_clause is narrowed to "loyalty_wear_forgiveness_cap replaces wear_forgiveness_cap" (verbatim in base).
   - The base sentence's "When the loyalty condition is met, ... and where loyalty_disposition_waiver is true for the tier the disposition fee is waived ..." keeps its condition in force for the disposition waiver.
4. **Replacements deferring to retired clauses: closed for all three members.**
   - HOLD replaced_by now ends "... still unpaid end_of_term_charge_off_days after turn_in_date is charged off.", with no "as the base rule states".
   - PLAN (both overwrites) likewise.
   - XM invoice overwrite: "an end-of-term invoice is mailed when any other end-of-term charge is billed."
   - XM's other three replaced_by now read "every other end-of-term charge keeps the amount the base rule gives it". That defers only to unretired base clauses (the retired clauses govern the mileage quantity alone).
   - Script check: "base rule states" no longer appears in any extended rule.
5. **Placement note: closed.**
   - hold_shape now tests a factor-owned `shape_balance`, and first_shape a factor-owned `shape_plan_balance`. Each has the same expression as the standard-method `end_balance` / `plan_balance`, which stay plain bindings of the standard method.
   - The factor outputs still read the plain balance for amounts, so every value is equal to round 3.
   - Observation O4-1: the shape_balance compute_basis quote ("the part of the invoiced end-of-term balance above one total_monthly_payment when that balance exceeds ...") describes the tier rather than the binding; it is verbatim.

### re-derived checks (r4)
- Script sweep: every compute_basis quote, policy_source, replaced_by and baseline.rule is verbatim in its own rule; every superseded_clause is verbatim in base; binding sets equal basis sets. Clean.
- Prerequisite graph and sentences: unchanged (gates `end_balance` / `plan_balance` still exist as plain bindings).
- Factor counts unchanged (WF 5: 4p/1m; HOLD 4: 3p/1m; XM 6: 5p/1m; PLAN 6: 5p/1m). Ladders as round 3.
- Tools: only the qualifying_account_number docstring changed. It has no example value and no ordering word, and the body is unchanged.
- XF_recipe sweep, 12 points x 4 policies:
  - 1-8 pass.
  - 9 passes now (narrow retirements; no replaced_by defers to its own retired clause; siblings named).
  - 10 rounding passes.
  - 11 tools passes.
  - 12 proof text is checked per task after the reveal.
- Charter-wide REDs open at freeze: none. Observations O2-1..O2-7, O3-1 and O4-1 carried.

### findings (r4, after reveal 2026-10-16T04:22:22Z)
**R4-1 — XF point 12 (proof text out of sync), RED per the XF rule; no scored item affected.** All members:
1. tasks/0.json design_rationale, [Route-around, declared]: "Wear forgiveness overwrites \"wear_forgiveness_cap for the tier is then waived from it as wear_forgiveness, up to the amount billed.\" and \"When the loyalty condition is met, loyalty_wear_forgiveness_cap replaces wear_forgiveness_cap\" ...". The charter's overwrite[1].superseded_clause is now "loyalty_wear_forgiveness_cap replaces wear_forgiveness_cap" (renderer mismatch 3 fix).
2. tasks/0.json design_rationale header: "— current through rework round 3." The file carries round-4 changes.
3. tasks/1.json design_rationale header: "— current through rework round 3." Same.
No other stale statement: the scanned tracing, closure, plumbing and route-around texts in both tasks recompute and match the current charter.

### round-3 / renderer items status (r4)
| item | status |
|---|---|
| renderer 1 (qualifying-account tie) | closed (round-3 miss of this auditor) |
| renderer 2 (halfway cap rule vs docstring) | closed (round-3 miss of this auditor) |
| renderer 3 (retirement too wide) | closed in the charter (round-3 miss of this auditor); the stale quote of the old clause survives in proof text, R4-1 member 1 |
| renderer 4 (replaced_by deferring to retired clauses; 3 members) | closed |
| renderer placement note | closed |
| round-1..3 closures | no regression (values, ladders, edges, scopes, seeds unchanged; view hashes identical) |
Worklog round-4 claims hold, except the implicit claim that proof text was re-synced (R4-1).

## closing_checklist (r4)
- revision_4 appended to all three files; earlier revisions untouched.
- Both tasks PASS all four relationships. Scopes disjoint and complete. Trees: one value_input edge each, user-owned roots, acyclic. Baselines definite and different from gold. Factor counts within bounds and every factor bears weight. XF points 1-11 pass on all four policies.
- Open: R4-1 (XF 12, proof text only). Gates: snapshot_r4.txt 7/7 green.

task0=PASS task1=PASS
charter=R4-1
VERDICT revision_4: task0=PASS task1=PASS charter=R4-1

## revision_5
### charter_global_frozen (revision_5)
- Gating `REWORK round 5: gates 7/7 green`; gate snapshot `.audit_views/policy/lease_end_servicing/snapshot_r5.txt` (7/7 green, expected pre-render notes). lease.extended.yaml 7e29b687e1161ed2 and task_tools.py 03a0ed5a4a388aa1 are unchanged from snapshot_r4, as are both view hashes. Every charter-global section of revision_4 is carried forward by reference on these hashes, including the XF points 1-11 sweep on all four policies, which therefore still passes. Only XF point 12 (per-task proof text) needs re-checking.

### findings (r5, after reveal 2026-10-16T04:57:52Z)
- R4-1: CLOSED, all three members (task 0 route-around quote, both rationale headers). A scripted quote check over every non-seed field of both tasks finds no remaining stale charter quotation.
- No regression: charter, tools and views are byte-identical to round 4, and the GT scored values, sensitivities and closures are unchanged. Worklog round-5 claims hold.
- XF_recipe: points 1-11 carried by hash from revision_4 (pass on all four policies); point 12 now passes.
- Observations O2-1..O2-7, O3-1 and O4-1 carried (not red).

## closing_checklist (r5)
- revision_5 appended to all three files; earlier revisions untouched.
- Both tasks PASS all four relationships. Scopes disjoint and complete; tools closed; uuid8s independent. Trees: one value_input edge each, user-owned roots, acyclic. Baselines definite and different from gold. Factors within bounds and every factor bears weight. All 12 XF points pass.
- Gates: snapshot_r5.txt 7/7 green (expected pre-render notes).

task0=PASS task1=PASS
charter=CLEAN
VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6
### charter_global_frozen (revision_6)
- Gating: `REWORK round 6: gates 8/8 green`. Gate snapshot `.audit_views/policy/lease_end_servicing/snapshot_r6.txt`: green; validate still INVALID with documents 303, as expected.
- Input: KB auditor `audits/policy_kb/lease_end_servicing/_difficulty.md` (SRC-1, SRC-2), read in full.
- Hashes: lease.extended.yaml dd526d0db20edb32 changed (r5 7e29b687e1161ed2). task_tools.py 03a0ed5a4a388aa1 and both views (3210811036c4afa0, d8b82ef455d1b181) are unchanged.
- Self-correction: SRC-1 is the rule-vs-compute reading of what I logged in revision_2 as realism observation O2-3 ("less every waiver"). I missed that "every waiver" also covers term-fee waivers (lease_fee_waiver) that the compute ignores. Revision_5's CLEAN verdict missed this class member.

### checks (r6)
- **SRC-1: closed.**
  - HOLD rule and baseline.rule now read "less every end-of-term charge waiver, security deposit application and end-of-term payment posted on the lease, a waiver of a term fee such as a late charge not being taken off".
  - end_balance and shape_balance subtract exactly lease_end_charge_waiver, lease_security_deposit_applied and lease_end_of_term_payment, so rule = compute.
- **SRC-1 class sweep: no remaining member.** I checked every "every/any/all/each ... waiver/payment/charge/fee" phrase in all four rules against its compute:
  - PLAN: "less every end-of-term payment posted", with waivers explicitly not taken off.
  - XM: autopay monthly payments less every returned payment.
  - WF: "a late charge counting even if it was later waived" (COUNT lease_late_charge).
  - HOLD: returned count.
  - The only remaining quirk is O2-3 (realism, not a mismatch): end-of-term charge waivers of charges billed on other days are subtracted while those charges are not counted, and rule and compute agree on it.
- **SRC-2 (base glosses, BLUEPRINT-KNOWN):** WF rule adds "The tier's wear_forgiveness_cap and loyalty_wear_forgiveness_cap enter wear forgiveness only as this cap schedule assigns them; meeting the loyalty condition alone does not put the loyalty cap in place." It is consistent with the narrowed retirement and the cap ladder. It binds no quantity, so it needs no compute_basis quote.
- **Script sweep:** every compute_basis quote, policy_source, replaced_by and baseline.rule is verbatim in its own rule; superseded clauses are verbatim in base; binding sets equal basis sets.
- **Compute:** the edited balance bindings are unchanged in their expressions, so scored values are expected unchanged.
- **XF_recipe:** points 1-11 pass on all four policies (only the two sentences above changed); point 12 is checked after the reveal.
- **Charter-wide REDs open at freeze:** none.

### findings (r6, after reveal 2026-10-16T09:43:51Z)
- SRC-1: CLOSED, and its class has no remaining member. SRC-2: addressed in the extended rule (base gloss untouched, BLUEPRINT-KNOWN).
- No regression: compute, factors, edges, scopes, tools and seeds unchanged; GT values identical; proof text in sync. Worklog round-6 claims hold.
- XF_recipe: all 12 points pass on all four policies.
- Observations carried: O2-1, O2-2, O2-3 (now confirmed to be realism only, with rule and compute in agreement), O2-4..O2-7, O3-1, O4-1.

## closing_checklist (r6)
- revision_6 appended to all three files; earlier revisions untouched.
- Both tasks PASS all four relationships. Scopes disjoint and complete; trees valid; factors within bounds and all bearing weight; baselines definite and different from gold.
- Gates: snapshot_r6.txt green (traceability now passing; validate's document count rose to 303 after rendering).

task0=PASS task1=PASS
charter=CLEAN
VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
