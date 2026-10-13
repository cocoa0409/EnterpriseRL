# Policy-task audit — prime_enrollment_fees_and_pcm / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1. Frozen 2026-10-11T13:13Z (sha256 `18579b3e…650b` recorded at 13:16Z), before any task's GT was revealed.
- Frozen inputs (hashes re-computed by the auditor and equal to the coordinator's brief):
  - `tasks/prime_enrollment_fees_and_pcm/prime.extended.yaml` sha256 `3c4b41c345eace73c3a1d3bb36b4da46ad823ee957ffa607828a6b5d9c1a1ea1`
  - `tasks/prime_enrollment_fees_and_pcm/task_tools.py` sha256 `f9731c3d38aa26c44389737641880653383bc491e1ec0b021131c4a0429ca78d`
- Read for this section: `blueprint/blueprint.yaml` (scope only), `blueprint/products/prime.yaml`, `blueprint/products/appeal.yaml` (Enrollment Reinstatement Review variant and the reinstatement decision rule), `blueprint/db_schema.json`, `blueprint/share_tools.py`, the extended charter, `task_tools.py`, the masked views `.audit_views/policy/prime_enrollment_fees_and_pcm/{0,1}.view.json` (frozen_time / user_scenario / initial_state only), and the DSL implementation in `skills/erl-task-instantiate/scripts/check_compute.py` (used only to know what each compute primitive returns).
- Masked and not read when this section was written: every `tasks/*.json`, the difficulty's worklog, the scenario `worklog.md`, all GT / evaluation_criteria / computations / closure / rationale fields. Nothing in this section is derived from a revealed GT.
- Entry conditions (Step 0): the coordinator supplied the gate snapshot (check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cache_diff INFO, check_cross_fire SCOPE OK, check_traceability deferred), the masked views with sha256 (0.view `c092216a…a9`, 1.view `2208ff94…b4`, both re-verified) and the charter/tool hashes. Entry conditions complete. A green gate is taken only as the qualification to audit.
- Scratch (re-checkable): `/tmp/erl55_audit_prime/replay.py`, `t0.py`, `t1.py`, `chk.py` replay the auditor's own derived writes through the real task tools and evaluate each policy's compute and factor-baseline substitutions with the gate's own DSL.

### policy_conflict_scan

Base section: lines 1-1239 of the extended file are byte-identical to `blueprint/products/prime.yaml` (`diff` shows only the trailing newline before `extended_policies:`).

Eight extended policies, all on the enrollment-fee account (`prime_fee_ledger`) of a fee-bearing Prime enrollment:

| policy | subject / computes | target_tool (owner) | prerequisite edges |
| --- | --- | --- | --- |
| prime_ext_reinstatement_catch_up | prime_fee_charge / amount | post_catch_up_installment_4baf2609 (agent) | [] |
| prime_ext_duplicate_payment_refund | prime_fee_refund / amount | refund_duplicate_payment_360f0d4a (agent) | [] |
| prime_ext_current_installment_payment | prime_fee_payment / amount | pay_current_installment_by_bank_draft_694809d0 (user) | [] |
| prime_ext_draft_on_file_method | prime_fee_payment / amount | run_draft_on_file_method_99529347 (agent) | catch_up (value_input, state), duplicate_refund (value_input, action), current_installment_payment (value_input, state) |
| prime_ext_unused_month_credit | prime_fee_credit / amount | post_unused_month_credit_3ad1a050 (agent) | [] |
| prime_ext_ended_enrollment_refund | prime_fee_refund / amount | refund_credit_balance_12944b90 (agent) | unused_month_credit (value_input, state) |
| prime_ext_first_installment_supplement | prime_fee_charge / amount | post_first_installment_supplement_bc87e2fc (agent) | [] |
| prime_ext_initial_payment | prime_fee_payment / amount | pay_first_installment_by_bank_draft_5f63627f (user) | first_installment_supplement (value_input, state), ended_enrollment_refund (state_gate, state) |

Overlapping subjects: two policies post `prime_fee_charge` (catch-up, supplement), two post `prime_fee_refund` (duplicate refund, ended-enrollment refund), three post `prime_fee_payment` (current installment, draft on file, initial payment). Each pair is separated by its rule's scope sentence (restored months after a reinstatement vs months a first installment owes; a payment posted more than once vs the credit balance of an ended enrollment; a beneficiary-authorised one-time bank draft toward an installment vs the region's draft through the method on file vs the initial payment toward a first installment) and by a distinct tool. In the two task worlds no write of one policy falls within another policy's scope (checked in each task file). Triggers, time anchors and terminal states do not collide; no extended policy changes `prime_enrollments.status`.

Cross-category reads: catch-up reads appeal (`appeal_cases`, `appeal_case_documents`, the variant's `decision_deadline`) and select (`select_fee_ledger`); unused-month credit and first-installment supplement read select. Read-only, through declared `cross_category` entries.

Claimed scope of the two tasks (as visible from the policy graph; to be compared with `charter_scope` after reveal): task 0 = {draft_on_file (root), catch_up, duplicate_payment_refund, current_installment_payment}; task 1 = {initial_payment (root), first_installment_supplement, ended_enrollment_refund, unused_month_credit}. Pairwise disjoint, jointly complete over the eight extended policies. Observation: the difficulty name and the coordinator's claimed event-type list mention PCM, access-waiver, transfer, OHI and setup-update events, but no extended policy touches them; the claim is wider than the charter.

### rule_compute_equivalence

Mechanical pass (`chk.py`): every `compute_basis` entry of all eight policies is a verbatim substring of its policy's `rule`; every sentence of every `baseline.rule` is a sentence of the `rule`; every ladder tier is stated in rule prose. Sentence-by-sentence sweep back, findings:

1. **`*_ind_seen` omits annual installments (all eight policies).** Rule (identical in all eight fee-level ladders): "the enrollment's fee arrangement is individual and the account carries installments charged at the individual share of their frequency". Compute (e.g. `cu_ind_seen`, `dr_ind_seen`, `mp_ind_seen`, `dd_ind_seen`, `cr_ind_seen`, `rf_ind_seen`, `su_ind_seen`, `rp_ind_seen`) counts only `installment_frequency='monthly'` at 1/12 and `'quarterly'` at 1/4. An individual-arrangement account billed annually at 390.12 (the individual share of an annual installment) satisfies the rule and fails the compute: rule -> individual fee, compute -> family fee. → finding G3.
2. **Catch-up "already carries an installment charge" counts only charges that *begin* inside the span.** Rule: "a quarterly charge counting for the three months of its quarter and an annual charge for the twelve months of its year". Compute `cu_billed_from/after` counts a quarterly charge ×3 when its `coverage_period_start` lies in [first, now] and ignores one that begins before the catch-up's first month. With first = May and a quarterly charge Apr-Jun on the account, rule: May and June already carry a charge; compute: 0 months. → finding G8 (no task consequence: task 0's account is monthly).
3. **Month windows are day-adjusted.** `within_months` uses `MONTHS(date, NOW)`, which subtracts one when the day of `date` exceeds today's day. "Posted from the month ... through the month before the current one" (duplicate refund) and "coverage period beginning in that month" (catch-up) are calendar-month statements; a row posted or beginning on the 20th of last month is counted by compute as current month. Neither task world has a row dated later in a month than the 14th inside a window edge (all coverage starts are the 1st except the new task-1 charge 2026-08-24, which falls inside the window either way), so no task consequence. Observation.
4. `prime_ext_ended_enrollment_refund` installment-value ladder: rule "Where the account's installments carry a recorded frequency ... where none of them carries a recorded frequency ... otherwise ..." does not say whether "carry" means all or any; compute takes "any" (`rf_nm + rf_nq + rf_na > 0`), so the fall-through executes only with zero installment charges. Every `prime_fee_charge` carries annual/quarterly/monthly (base event `prime_fee_charge`: "installment_frequency: annual, quarterly or monthly"; db_schema: `not_applicable` only "on payments, credits and refunds"). See G7.
5. No other quantity, window, filter, branch, cap/floor or rounding point was found in one face and missing from the other.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (8 tools, 8 policies, all `computes: amount`).
- uuid8 tails: 4baf2609, 360f0d4a, 694809d0, 99529347, 3ad1a050, 12944b90, bc87e2fc, 5f63627f — no shared prefix, no sequence, no adjacency; independent and frozen.
- Docstrings: no tool names another tool; no docstring places its action in a sequence ("then" in each docstring describes the tool's own effect). Observation: `refund_credit_balance_12944b90.related_fee_entry_id` says "read from the fee-account lookup ... or from the receipt of the credit's posting", and `pay_first_installment_by_bank_draft_5f63627f.related_fee_entry_id` says "or from the receipt of that charge's posting" — each mentions that a posting may have happened earlier in the call. No ordering word, no tool name; recorded as an observation only.
- Tool bodies: none checks eligibility, prerequisite state, amount or order; every tool writes one ledger row and moves `fee_balance_due` by the amount. The tool layer judges no prerequisite.

### prerequisite_graph

- `prerequisite` filled on all eight policies (`[]` on five). Every `problem` points at another extended policy id; none at a base policy or itself. Graph: draft <- {catch_up, duplicate_refund, current_installment_payment}; ended_refund <- unused_credit; initial_payment <- {supplement, ended_refund}. Acyclic; two components.
- Every `policy_source` is verbatim in its own policy's `rule` and is not restated in the depended-on rule (`chk.py`).
- `form`: five `state`, one `action` (duplicate refund) with `fallback_reason`; `fallback_reason` present exactly on the action edge.
- `resolved_by` equals the depended-on policy's `target_tool` on all six edges.
- `kind`/`gate`: value_input gates `dd_target`, `dd_adjust`, `dd_adjust`, `rf_open`, `rp_owed` are real bindings of the blocked compute; the state_gate edge names `prime_enrollments.fee_balance_due`, a real field.
- `condition` vs `policy_source` strength: see G9 (two edges whose condition is narrower than the sentence). No authoring-viewpoint phrasing ("in this task", "at the opening") in any prerequisite field.

### prerequisite_sentences

Four-point test, per edge:

| edge | sentence (own rule) | connective | waited-on | names tool/id? | strength vs condition |
| --- | --- | --- | --- | --- | --- |
| draft <- catch_up | "A draft toward a back-billed installment is made only after every month from the month after the old paid-through date recorded on the enrollment's reinstatement review to the month before the current one lies inside the coverage period of an installment charge on the account." | only after | state: coverage of installment charges | no | equal |
| draft <- duplicate_refund | "No draft is made on an account until the region has refunded the duplicate payment found on it." | until | action, business words | no | condition is the duplicate policy's own result; see note |
| draft <- current_installment_payment | "The region does not draw a back-billed installment until the installment of the current month stands paid in full." | until | state: paid in full | no | equal (condition nets refunds; "paid in full" read the same way) |
| ended_refund <- unused_credit | "The refund of an ended enrollment's credit balance is fixed only after every month of its last paid installment that a following TRICARE Select enrollment also billed, or that falls after the month containing the disenrollment date, stands credited." | only after | state: months credited | no | condition narrower (G9) |
| initial_payment <- supplement | "An initial payment toward a new enrollment is figured only after the enrollment's installment charges cover every month from the month containing its effective date through the end of the last installment period its first installment owes." | only after | state: coverage | no | condition narrower (G9) |
| initial_payment <- ended_refund | "An initial payment toward a new Prime enrollment is not taken until every Prime enrollment the beneficiary ended earlier in the same plan year shows a fee balance of zero." | not ... until | state: fee balance | no | equal |

Single-resolver test for state-form edges:
- "coverage of installment charges" (draft <- catch_up; initial_payment <- supplement): two writes of this difficulty create `prime_fee_charge` rows (catch-up, supplement). They are separated by scope: the catch-up rule bills "months of its restored coverage that carry no installment charge" of an enrollment an Enrollment Reinstatement Review brought back; the supplement rule bills "every month its first installment owes" of an enrollment whose first installment charge falls short. The sentence of each edge names the span by the matching anchor (old paid-through date on the reinstatement review / effective date and first installment), so one reading. Holds.
- "current month's installment paid in full": writable by the beneficiary's one-time bank draft (current_installment_payment) or the region's draft on file (the blocked root itself, scoped to an amount the beneficiary asked to be drawn). Single reading in task 0's world (see 0.md).
- "months stand credited": only `post_unused_month_credit_3ad1a050` writes `prime_fee_credit`. Holds.
- "fee balance of zero" on an ended enrollment: moved up by the two refund tools and down by the credit tool; the duplicate refund is scoped to "an installment ... paid more than once", the ended-enrollment refund to "the credit balance left on the fee account of a TRICARE Prime enrollment that has ended". Single reading in task 1's world (see 1.md).

Action-form fallback (duplicate refund): the stated reason — an earlier partial refund can already stand against the duplicate payment, so a refund row is not proof the duplicate was dealt with — is real in task 0's world (a 2.00 refund already stands against the 50.00 payment). A state wording would have to restate the duplicate computation. Fallback accepted. Observation: the same pre-existing 2.00 refund lets a reader argue the action ("has refunded the duplicate payment") already happened; the duplicate policy itself leaves 40.49 still to refund in that world, which rules this out.

Base rule sentences stating a cross-problem order ("A fee-bearing enrollment is activated only after its first installment charge has a payment posted against it"; "Installments are charged only on ... applied or active") ground no edge of either tree. Observation only.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (findings only; consequences are demonstrated per task):

- **prime_enrollment_fee_schedule** (refs: catch_up, supplement, initial_payment; the fee-level ladders of all eight policies govern the same quantity): "The family owes annual_fee_individual while exactly one family member is enrolled in Prime and annual_fee_family while two or more are" is followed by none of the eight extended rules and is overwritten by none. Each extended rule's fee level is: individual fee only when "the enrollment's fee arrangement is individual and the account carries installments charged at the individual share of their frequency"; "otherwise ... the annual family fee". For an individual-arrangement enrollment of a one-member family whose account carries no such installment (a new enrollment before its first charge; an annual payer, see G3), base gives 1/12 of 390.12 = 32.51 per month and every extended rule gives 1/12 of 780.24 = 65.02. Undeclared override → finding G2. "Installments cover calendar quarters ... due on the first day of the period" — overwritten by catch_up (declared). "For an enrollment that starts mid-period, the first installment covers ..." — overwritten by supplement (declared). "monthly installment is one twelfth ... quarterly installment is one quarter ... rounded to the cent" — followed.
- **prime_fee_payment_methods** (refs: duplicate_refund, current_installment_payment, draft, initial_payment): "A payment is applied to the oldest unpaid installment first and never to a future period while an earlier installment is open" — overwritten by current_installment_payment, draft and initial_payment (declared); the duplicate refund applies no payment. Method sentences followed (EFT and recurring card are monthly methods).
- **prime_nonpayment_disenrollment**, **prime_reinstatement** (refs: catch_up, current_installment_payment, draft, initial_payment): no sentence handled differently. Observation: the catch-up's late-decision tier ("the region bearing the later months its late decision held open") and proof-of-payment tier leave restored months unbilled although `prime_reinstatement` restores "the same fee arrangement"; no base sentence states that every restored month is billed, so this is not an override.
- **prime_fee_proration_credit** (refs: duplicate_refund, unused_credit, ended_refund): "the month in which the disenrollment date falls is never credited" and "once per installment and reason" — overwritten by unused_credit (declared). "credited back, at one twelfth of the annual fee per month" — the unused-credit baseline sentence "The credit returns the installment's amount for the share of its coverage days that fall after the disenrollment date" handles the same quantity differently and is not named in `overwrite`; it is reached only on the credit-measure fall-through, which no installment can take (G7), so no world reaches the conflict. Observation. "A credit that leaves the account with a credit balance is refunded through the method of the original payment within fee_refund_issue_days" — overwritten by duplicate_refund (declared; the `replaced_by` text concerns the shortfall hold-back, not the method or timing); ended_refund (`overwrite: []`) follows it (credit balance refunded through the method of the paid installment's latest payment).
- **prime_agg_multi_holding** (refs: unused_credit, supplement): followed.

### factor_ladders

Declared factors (label as declared; "struck" = fails a structural test below and does not count):

| policy | factor | label | ladder test result |
| --- | --- | --- | --- |
| catch_up | catch_up_monthly_rate | parameter | struck (G1) |
| | catch_up_first_month | method | struck (G4) |
| | catch_up_last_month | method | struck (G4) |
| | catch_up_months_already_charged | parameter | struck (G5) |
| | catch_up_months_billed_by_select | parameter | struck (G5); cross_difficulty select |
| duplicate_refund | duplicate_value_fee_level | parameter | struck (G1) |
| | duplicate_value_share | method | holds (label: divisor 12/4/1 is a number, observation G10) |
| | duplicate_payment_returned | method | holds |
| | duplicate_earlier_refunds | parameter | struck (G5) |
| | duplicate_shortfall_held_back | parameter | struck (G5) |
| current_installment_payment | one_time_payment_installment | method | holds |
| | one_time_payment_fee_level | parameter | struck (G1) |
| | one_time_payment_share | method | holds (G10 label observation) |
| | one_time_payment_received | parameter | struck (G5) |
| | one_time_payment_owed_again | parameter | struck (G5) |
| draft | draft_installment | method | holds |
| | draft_limit_fee_level | parameter | struck (G1) |
| | draft_regular_installment | method | holds (G10 label observation) |
| | draft_limit_by_method | method | holds (G10: tiers 1 and 2 are the same cap formula with multiplier 1 vs 2); multi-source |
| | draft_excess_elsewhere | parameter | holds |
| unused_credit | credit_months_counted | method | holds; multi-source; cross_difficulty select |
| | credit_monthly_rate | parameter | struck (G1) |
| | credit_measure | method | struck (G7) |
| | credit_already_posted | parameter | struck (G5) |
| ended_refund | refund_credits_left | parameter | struck (G5) |
| | refund_installment_fee_level | parameter | struck (G1) |
| | refund_installment_value | method | struck (G7) |
| | refund_payment_difference | parameter | struck (G5) |
| supplement | supplement_last_month | method | holds |
| | supplement_monthly_rate | parameter | struck (G1) |
| | supplement_select_offset | parameter | holds; multi-source; cross_difficulty select |
| | supplement_already_charged | parameter | struck (G5) |
| initial_payment | initial_charges_settled | method | holds |
| | initial_received | parameter | struck (G5; also G6) |
| | initial_owed_again | parameter | struck (G5) |
| | initial_months_ahead | parameter | holds; multi-source |
| | initial_ahead_rate | parameter | struck (G1) |

Counts that survive, as declared labels (bounds: 4-6 factors, ≥2 parameter, ≥1 method):

| policy | surviving | parameter | method | within bounds |
| --- | --- | --- | --- | --- |
| catch_up | 0 | 0 | 0 | no |
| duplicate_refund | 2 | 0 | 2 | no |
| current_installment_payment | 2 | 0 | 2 | no |
| draft | 4 | 1 | 3 | no (parameter < 2 as declared; with the G10 labels made honest it would be 3 parameter / 1 method) |
| unused_credit | 1 | 0 | 1 | no |
| ended_refund | 0 | 0 | 0 | no |
| supplement | 2 | 1 | 1 | no |
| initial_payment | 2 | 1 | 1 | no |

Every declared factor has disjoint bindings, a `decides` that is an input rather than `result`, three tiers stated in the rule and implemented in compute, and a baseline equal to its fall-through tier. Per task, cross_difficulty factors exist (task 0: catch_up first/last on appeal, months_billed_by_select on select — all struck; task 1: credit_months_counted and supplement_select_offset on select — both hold). Whether each factor bears weight is decided in each task's `factor_weight`.

### findings

**G1 — SOURCE-FACTOR RED: the "tier is fee-exempt" rung of every fee-level ladder is unreachable at every write of this charter (all 8 policies; bears on tasks 0 and 1).**
- Symptom: catch_up_monthly_rate, duplicate_value_fee_level, one_time_payment_fee_level, draft_limit_fee_level, credit_monthly_rate, refund_installment_fee_level, supplement_monthly_rate and initial_ahead_rate each have "the tier is fee-exempt -> 0" as their first rung, and their second rung begins "the tier is not fee-exempt, ...".
- Root cause: every one of the eight rules is scoped to the fee account of a fee-bearing enrollment, and the base charter makes fee-bearing and fee-exempt mutually exclusive: "Enrollment fees are owed only by tiers whose fee_exempt is false ... and are billed once per sponsor family to the fee-bearing enrollment" (prime_enrollment_fee_schedule); `fee_coverage_type`: "individual or family fee, or not_applicable for fee-exempt tiers" (event prime_enroll). The catch-up is further scoped to enrollments "that an Enrollment Reinstatement Review brought back after a nonpayment disenrollment", and fee-exempt tiers have `nonpayment_grace_days: 0` and `reinstatement_request_window_days: 0`.
- Demonstrated consequence: the part "the tier is not fee-exempt" holds of every customer who reaches any of these writes, and the "fee-exempt" rung holds of none, so each ladder has two reachable rungs. Under the factor relationship ("a ladder of at least three pairwise-disjoint tiers ... every condition a tier states ... is one that line of business actually weighs ... and not one that holds of every customer who reaches this write") all eight are struck; see the count table.
- Affected: `extended_policies[*].factors[<fee-level>]`, the matching rule sentences ("Where the tier is fee-exempt, ...").

**G2 — SOURCE-POLICY RED (charter level, no consequence in either task world): undeclared override of the base fee level; the fee-level fall-through is not what the business charges a one-member family.**
- Evidence: base `prime_enrollment_fee_schedule`: "The family owes annual_fee_individual while exactly one family member is enrolled in Prime and annual_fee_family while two or more are". Extended (e.g. catch_up rule): "where the tier is not fee-exempt, the enrollment's fee arrangement is individual and the account already carries installments charged at the individual share of their frequency, the catch-up's monthly rate is one twelfth of the tier's annual individual fee ...; otherwise it is one twelfth of the annual family fee". No `overwrite` entry names the base sentence.
- Same situation, two conclusions: Retiree Group A, one enrolled member, arrangement individual, no individual-share monthly/quarterly charge on the account (a brand-new enrollment before its first charge, or an annual payer under G3): base 32.51 per month, extended 65.02 per month.
- Demonstrated consequence in the tasks: none — both task worlds' accounts carry individual-share charges (see 0.md, 1.md). The ladder side of the same defect (a fall-through that bills the family fee to an individual arrangement) is a reason G1's factors are struck even before G1.

**G3 — SOURCE-POLICY RED (charter level, no task consequence): rule/compute mismatch in `*_ind_seen` (all 8 policies).** See rule_compute_equivalence item 1. An individual annual payer with a 390.12 annual charge: rule -> individual fee, compute -> family fee. Neither task world has an annual charge.

**G4 — SOURCE-FACTOR RED: the catch-up's first-month and last-month ladders turn on conditions that hold of every customer who reaches the catch-up write (task 0).**
- Evidence: catch_up rule scope: "the catch-up installment of a fee-bearing TRICARE Prime enrollment that an Enrollment Reinstatement Review brought back after a nonpayment disenrollment". Base `prime_reinstatement`: "A nonpayment disenrollment is reversed only through an Enrollment Reinstatement Review. The enrollment is reinstated only when an Enrollment Reinstatement Review case for this enrollment is decided overturned ...". Appeal charter (blueprint/products/appeal.yaml, reinstatement rule): "A reinstatement is decided overturned only when a statement of good cause is on file for the case." (also `required_documents: [statement_of_good_cause]`).
- catch_up_first_month rungs: (1) "decided overturned with a statement of good cause in its case file and no proof of payment", (2) "decided overturned with proof of payment in its case file", (3) otherwise -> "starts with the month the review was decided" (= baseline). "Decided overturned" and "statement of good cause in its case file" hold of every customer at this write; the fall-through (a review not decided overturned) holds of none. Two reachable rungs, split only on proof of payment.
- catch_up_last_month rungs: (1) "decided overturned no later than its decision deadline", (2) "decided overturned after that deadline", (3) otherwise -> "runs through the month the review was decided" (= baseline). "Decided overturned" holds of every customer; the fall-through holds of none. Two reachable rungs.
- Consequence: both factors are struck; the baseline both encode ("bills the month in which the reinstatement review was decided") is a treatment no customer in the catch-up's scope can receive. Affected: `prime_ext_reinstatement_catch_up.factors[catch_up_first_month, catch_up_last_month]`, `baseline.rule`.

**G5 — SOURCE-FACTOR RED: eleven ladders are one arithmetic step written as three rungs (tasks 0 and 1).** In each, applying the middle rung's value in the other rungs' situations gives exactly the value (or the same scored result) those rungs select, so the rungs do not select distinct values or methods:
- catch_up_months_already_charged, catch_up_months_billed_by_select: "all ... left out / those months are left out / no month is left out" is the single method "leave out the months that carry a charge" (all = those when every month carries one; none = those when none does).
- duplicate_earlier_refunds: "the whole excess / the refunds already issued / 0": with no refund the refunds issued are 0; with refunds ≥ excess, taking the refunds gives `MX(0, excess - refunds) = 0`, the same left-over as taking the whole excess.
- duplicate_shortfall_held_back: "all that is left / the shortfall / 0": with shortfall ≥ left, holding back the shortfall gives `MX(0, left - shortfall) = 0`, the same result as holding back all that is left.
- one_time_payment_received, initial_received: "what it is owed / what was posted / 0": with nothing posted, what was posted is 0.
- one_time_payment_owed_again, initial_owed_again: "what counts as received / the refund / 0": with no refund, the refund is 0.
- credit_already_posted, supplement_already_charged: "the figure / what was posted / 0": nothing posted gives 0; posted ≥ figure gives `MX(0, figure - posted) = 0` either way.
- refund_credits_left: "0 / credits less refunds / all the credits": with no refund, credits less refunds = all the credits.
- refund_payment_difference: "excess added / shortfall taken off / 0": all three rungs are the signed difference payments − installment values (0 when they are equal).
- Consequence: each is struck under "two tiers of one ladder selecting the same value or method". Affected: the eleven `factors` entries and their rule sentences.

**G6 — SOURCE-FACTOR RED: dishonest baseline on initial_received (task 1).** `prime_ext_initial_payment.baseline.rule`: "An initial payment settles the installment charge posted most recently on the enrollment's account and pays what that charge still lacks after the payments posted on the account, rounded to the cent." The baseline rule therefore nets the payments posted on the account; the factor's `baseline: {rp_received: '0'}` ignores them. The value of `rp_received` read from baseline.rule is the payments posted (capped at the amount owed) — the factor's own second rung. Demonstration of the consequence on task 1's world is in 1.md.

**G7 — SOURCE-FACTOR RED: ladders whose fall-through no installment can reach (task 1).**
- credit_measure: rungs "quarterly or annual / monthly / otherwise -> day share (= baseline)". Every `prime_fee_charge` is annual, quarterly or monthly (base event; db_schema `not_applicable` only on payments, credits, refunds), so the fall-through and its day-share method reach no customer. Two reachable rungs.
- refund_installment_value: rungs "installments carry a recorded frequency / none carries one / otherwise -> whole annual fee each (= baseline)". Every charge carries a recorded frequency, so rung 2 and the fall-through reach no customer. One reachable rung.
- Both struck.

**G8 — SOURCE-POLICY RED (charter level, no task consequence): catch-up month count, rule vs compute for quarterly/annual charges.** See rule_compute_equivalence item 2.

**G9 — SOURCE-POLICY RED (charter level, no task consequence): two prerequisite conditions narrower than their sentences.**
- initial_payment <- supplement: sentence "through the end of the last installment period its first installment owes"; condition "through the end of the installment period containing its application date". For an application received inside the effective date's installment period twenty or more days after the effective date, the supplement rule's first installment "runs through the end of the installment period that follows": the sentence requires charges through the following period, the condition only through the current one.
- ended_refund <- unused_credit: sentence "every month of its last paid installment that a following TRICARE Select enrollment also billed"; condition "that the beneficiary's TRICARE Select first installment also billed". Where a later Select installment also overlaps the last paid Prime installment (e.g. an annual Prime installment), the sentence requires those months credited, the condition does not — and the unused-credit rule only counts the Select charge "beginning on the Select effective date", so under the sentence the edge could never be resolved.
- In both task worlds the two readings coincide (shown in 1.md).

**G10 — Observation: method labels on number substitutions.** duplicate_value_share, one_time_payment_share, draft_regular_installment select a divisor (12, 4, 1) inside one formula; draft_limit_by_method's rungs 1 and 2 are the cap `k × regular installment` with k = 1 and k = 2. These are `parameter` effects labelled `method`. They matter to the counts only for the draft (see table).

**G11 — Observation: fee level read off the `fee_coverage_type` field.** All fee-level ladders select the individual rung partly from `prime_enrollments.fee_coverage_type == 'individual'`, a field that names the outcome, where base decides the fee from the number of family members enrolled. Subsumed by G1/G2.

## closing_checklist

Written 2026-10-11 after both tasks' reveals (the section above is unchanged since its pre-reveal freeze). Audited artifacts unchanged during the audit: `prime.extended.yaml` `3c4b41c3…a1ea1`, `task_tools.py` `f9731c3d…ca78d`, `tasks/0.json` `279b82dc…aa76`, `tasks/1.json` `81b44d84…a388`.

| item | status |
| --- | --- |
| per-task files 0.md, 1.md, one per task, alongside this file; each has a frozen derivation then a comparison | yes (first revision; no older revision exists) |
| every comparison section carries PASS on all four relationships | **no** — task 0: SOURCE-CHAIN RED (0-C1, proof text), SOURCE-FACTOR RED (0-F1); task 1: SOURCE-FACTOR RED (1-F1, 1-F2) |
| charter self-consistent | **no** — charter-level SOURCE-POLICY REDs G2 (undeclared fee-level override), G3 (`*_ind_seen` vs rule), G8 (catch-up quarterly/annual counting), G9 (two prerequisite conditions narrower than their sentences); none has a consequence on either task's world |
| extended policies fully covered; scopes pairwise disjoint | yes — task 0 {draft, catch_up, duplicate_refund, current_installment_payment}, task 1 {initial_payment, supplement, ended_refund, unused_credit}; `charter_scope` of each equals the auditor's partition |
| task tools and GT closed; uuid8s independent and frozen | yes |
| each tree: 1-3 prerequisite problems, ≥ max(n−1,1) value_input, ≥1 owner=user write, acyclic; whole-difficulty graph acyclic | yes (task 0: 3 problems, 3 value_input, user write current payment; task 1: 3 problems, 2 value_input, user write root) |
| every computation: self-sufficient baseline, 4-6 surviving factors (≥2 parameter, ≥1 method), ≥1 multi-source and ≥1 cross-difficulty per task, each bearing weight against an honest baseline | **no** — surviving counts 0/2/2/4 (task 0) and 1/0/2/2 (task 1); task 0 has no surviving cross-difficulty factor; initial_received's declared baseline contradicts `baseline.rule` |
| unique solution | yes for both tasks (auditor's blind derivation equals GT on every scored argument) |
| instantiation gates re-run on the final form | not re-run by the auditor (the brief's snapshot is cited; artifacts are byte-unchanged since that snapshot) |

**The difficulty does not pass the source-layer audit**: policy self-consistency fails at charter level (no task consequence), the factor relationship fails in both tasks, the problem-tree relationship carries one proof-text red in task 0; the unique-solution relationship passes in both.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: same independent auditor, re-audit round 2. Written before any round-2 task file (`tasks/*.json`, mtime 20:29) or the difficulty's new `worklog.md` was opened.
- Inputs re-hashed by the auditor, equal to the coordinator's brief: `prime.extended.yaml` `62e4e2b42764b497dfcfb1bfdce3d40f6df2eed8a31ca701e1e9a8f0e3cd5892` (**changed** since revision 1 → every charter-global section is re-derived in full below), `task_tools.py` `f9731c3d…ca78d` (unchanged → § action_binding_and_uuids carried forward by reference: tools, docstrings, uuid8s and bodies are byte-identical), views 0 `871c907b…bf9c`, 1 `437447ea…ea74`. Base section (lines 1-1239) still byte-identical to `blueprint/products/prime.yaml`.
- contamination_disclosure: the auditor read the round-1 `tasks/*.json` GT during revision 1 (recorded there). The round-2 worlds are re-seeded and the charter rewritten; nothing below uses a round-1 GT value, and no round-2 GT has been seen.
- Method: the same scratch harness, re-pointed at the new files (`/tmp/erl55_audit_prime/chk.py`, `r2_t0.py`, `r2_t1.py`).

### policy_conflict_scan (revision 2)

Same eight policy ids, tools, owners and subjects. Scope changes: `prime_ext_duplicate_payment_refund` is now limited to an enrollment "whose status is applied or active"; `prime_ext_ended_enrollment_refund` now also returns a duplicate payment on an ended enrollment. The two refund policies are therefore separated by enrollment status (no overlap). The fee level in every policy is now a plain rule ("The annual fee of the enrollment's fee arrangement is the tier's annual individual fee for an individual arrangement and its annual family fee for a family arrangement"), not a factor. Graph changes: draft <- current_installment_payment is now `state_gate` (gate `prime_fee_ledger.amount`); the draft <- catch-up sentence and both G9 conditions are reworded. Scope partition unchanged and still disjoint/complete: task 0 {draft, catch_up, duplicate_refund, current_installment_payment}, task 1 {initial_payment, supplement, ended_refund, unused_credit}.

### rule_compute_equivalence (revision 2)

Mechanical: every `compute_basis` entry is verbatim in its rule; every `baseline.rule` sentence is in its rule (`chk.py`, no exception printed). Sweep-back findings:
- **N1** — `one_time_payment_received` / `initial_received`. Rules: "Where payments stand against the settled installment, they count as received; where none does, the payments posted on the account since the month the installment fell due that name no installment count as received; otherwise the proration credits standing on the account count as received." and "Where payments posted on the account name an installment charge, those payments count as received; where none does, the payments posted on the account that name no installment count as received; otherwise the proration credits ...". Rung 2's condition ("where none does") is the full complement of rung 1, so in the rule the fall-through describes no case; compute takes rung 2 only when `mp_unapplied > 0` / `rp_unapplied > 0` and otherwise counts the credits. Same situation, two answers: no payment against the installment, no unapplied payment, a 30.00 proration credit on the account — rule: received 0.00; compute: 30.00.
- **N4** — supplement effective month: rule "otherwise that month counts at the monthly rate times its days from the effective date through the last day of the coverage period of the installment charge beginning on the effective date, over 30"; compute `RND(su_m * MN(30, su_eff_days) / 30, 2)` caps the days at 30. For a first charge covering 31 days (e.g. an initial-eligibility enrollment effective 2026-07-01): rule 32.51 × 31/30 = 33.59, compute 32.51.
- G8 (revision 1) is closed: the catch-up now says "that no monthly installment charge on the account begins in", which is what `cu_charged_n` counts. G3 is closed (no `*_ind_seen`). The day-adjusted `MONTHS` window artefact (revision-1 observation) persists; neither round-2 world has a row it moves.

### action_binding_and_uuids (revision 2)

Carried forward from revision 1 (task_tools.py unchanged, hash above). Each `(target_tool, computes)` still claimed by exactly one policy.

### prerequisite_graph (revision 2)

All six edges: `policy_source` verbatim in the blocked rule and absent from the depended-on rule; `resolved_by` = depended-on `target_tool`; acyclic; `fallback_reason` only on the action edge. Kinds: task 0 tree catch_up (value_input `dd_target`), duplicate_refund (value_input `dd_off`), current_installment_payment (state_gate, gate `prime_fee_ledger.amount` — observation: a ledger column, not an eligibility gate of the draft policy, which declares none); task 1 tree unchanged in kinds. Value-input floors: task 0 has 2 of 3 (= max(3−1,1)); task 1 has 2 of 3.

### prerequisite_sentences (revision 2)

| edge | sentence | test |
| --- | --- | --- |
| draft <- catch_up | "A draft toward a back-billed installment is made only after an installment charge on the account has a coverage period that reaches the month before the current month." | "only after"; state; no tool/id; condition "includes the month before the current month" — same strength. Writers of a charge reaching that month: catch-up (bills through the month before the current month) and, in principle, the supplement (scoped to a first installment). Single reading by scope. |
| draft <- duplicate_refund | unchanged (action form, fallback accepted as in revision 1) | condition now "brings the excess on that installment down to what the region keeps on the account" — the duplicate policy's own result |
| draft <- current_installment_payment | unchanged sentence | state_gate; "until"; condition matches |
| ended_refund <- unused_credit | "... every month of its last paid installment that a following TRICARE Select enrollment's coverage reaches, or that falls after the month containing the disenrollment date, stands credited." | condition now reads Select coverage from the enrollment's effective month through its disenrollment month, which is what the credit rule reads — **G9(b) closed** |
| initial <- supplement | "... through the last month its first installment owes." | condition identical in scope — **G9(a) closed** |
| initial <- ended_refund | unchanged | unchanged |

### override_declarations (revision 2)

- prime_enrollment_fee_schedule: the fee level is now the arrangement's fee in every policy; for an individual (one-member) arrangement this is base's "annual_fee_individual while exactly one family member is enrolled". **G2 closed.** The supplement's superseded clause still covers the whole base first-installment sentence including "(counted as a whole month)", so the new effective-month valuation is declared.
- prime_fee_proration_credit: unused_credit declares both overrides; its new "switch month" rung (crediting the disenrollment month when Select took effect within 15 days) lies inside the declared replacement. The baseline sentence "credits each at one twelfth of the installment's charge" handles monthly/quarterly installments differently from base ("one twelfth of the annual fee per month"); the merged rule reaches base's figure through the month-value rungs, so no world reaches a conflict (observation). duplicate_refund's declared replacement now concerns the amount kept on the account.
- prime_fee_payment_methods / prime_nonpayment_disenrollment / prime_reinstatement / prime_agg_multi_holding: no undeclared change found. ended_refund (`overwrite: []`) now also refunds a duplicate payment; base has no sentence on duplicate payments, so no override.

### factor_ladders (revision 2)

| policy | factor | label | ladder test |
| --- | --- | --- | --- |
| catch_up | catch_up_first_month | method | holds (proof of payment / medical records without proof / otherwise filing month; observation N7 on the fall-through's business sense) |
| | catch_up_months_region_bears | parameter | holds |
| | catch_up_select_coverage | method | holds; multi-source (Select enrollment dates × catch-up span × ledger) |
| | catch_up_select_share | parameter | holds (Select Retiree tiers allow annual, so the 1/12 fall-through is reachable) |
| | catch_up_billing_shape | method | holds |
| duplicate_refund | duplicate_installment | method | **struck (N6)** |
| | duplicate_value_share | parameter | holds |
| | duplicate_payment_returned | method | holds |
| | duplicate_what_comes_off | parameter | **struck (N6, N3)** |
| | duplicate_amount_kept | parameter | holds; multi-source (method field × ledger) |
| current_installment_payment | one_time_payment_installment | method | holds |
| | one_time_payment_share | parameter | holds |
| | one_time_payment_received | parameter | **struck (N1)** |
| | one_time_payment_lapse_window | method | holds (label observation N5) |
| | one_time_payment_months_ahead | parameter | holds; multi-source |
| draft | draft_installment | method | holds |
| | draft_regular_installment | parameter | holds |
| | draft_limit_by_method | parameter | holds; multi-source |
| | draft_history_window | method | holds (label observation N5) |
| | draft_excess_elsewhere | parameter | holds |
| unused_credit | credit_months_counted | method | holds; multi-source, cross select |
| | credit_month_value | parameter | holds |
| | credit_switch_month_value | parameter | holds; cross select |
| | credit_what_comes_off | parameter | holds |
| ended_refund | refund_duplicate_installment | method | holds (ended enrollments can carry credits) |
| | refund_installment_value | parameter | holds (G7 closed) |
| | refund_duplicate_returned | method | holds |
| | refund_what_comes_off | parameter | **struck (N3)** |
| supplement | supplement_last_month | method | holds |
| | supplement_effective_month_value | parameter | holds (N4 is a rule/compute finding, not a ladder one) |
| | supplement_select_coverage | method | holds |
| | supplement_select_share | parameter | holds |
| | supplement_billing_shape | method | **struck (N2)** |
| initial_payment | initial_charges_settled | method | holds |
| | initial_received | parameter | **struck (N1)** |
| | initial_months_ahead | parameter | holds |
| | initial_ahead_value | parameter | holds |

Surviving counts (bounds 4-6, ≥2 parameter, ≥1 method): catch_up 5 (2p/3m) ok; duplicate_refund **3** (2p/1m) fails; current_installment_payment 4 (2p/2m) ok; draft 5 (3p/2m) ok; unused_credit 4 (3p/1m) ok; ended_refund **3** (1p/2m) fails; supplement 4 (2p/2m) ok; initial_payment **3** (3p/1m) fails. Cross-difficulty per task: task 0 catch_up (appeal, select), lapse/history windows (appeal); task 1 credit and supplement (select).

### findings (revision 2)

Closure of revision-1 charter findings: **G1 closed** (no fee-exempt rungs; fee level is no longer a factor). **G2 closed.** **G3 closed.** **G4 closed** (first-month ladder no longer turns on "decided overturned" or the good-cause statement; region-bears ladder has three reachable, distinct rungs). **G5 closed** (no ladder is a min/max clamp in three rungs). **G6 closed** (initial baseline.rule now nets "the proration credits standing on the account", which is the factor's baseline — but see N1). **G7 closed** (credit_measure removed; refund_installment_value's rungs are monthly/quarterly/annual). **G8 closed.** **G9 closed.** **G10 closed** (share and cap factors relabelled `parameter`). **G11 closed** (fee level not a factor).

New:

**N1 — SOURCE-POLICY RED + SOURCE-FACTOR RED: the "received" ladders of the current-installment payment and the initial payment have a fall-through the rule makes unreachable, and compute disagrees with the rule (tasks 0 and 1).** Evidence and the two answers: § rule_compute_equivalence. Consequence: both factors struck (the baseline they encode, "the proration credits standing on the account", is a rung the rule never selects). Task-level consequence in 0.md / 1.md.

**N2 — SOURCE-FACTOR RED: supplement_billing_shape's fall-through (= the policy baseline) subtracts the year's charges twice (task 1).** Rule: "otherwise the first installment is the plan year's annual fee less the installment charges on the account whose coverage begins in the current plan year" and "The supplement is the first installment so figured less the installment charges already posted on the account". For an annual arrangement (the fall-through's situation) whose first charge X was posted this plan year, the supplement is A − X − X; no business bills an annual first installment by deducting the same charge twice. Demonstrated on task 1's world in 1.md (the baseline gives 390.12 − 32.51 − 32.51 = 325.10). Struck; supplement still has 4 surviving factors.

**N3 — SOURCE-FACTOR RED: the "what comes off" fall-through of both duplicate ladders takes unrelated refunds off a duplicate payment's excess (tasks 0 and 1).** Rules: duplicate refund "otherwise the refunds issued on the account in the current plan year come off"; ended refund "otherwise the refunds issued on the account in the current plan year come off". In that situation no refund was issued against the returned payment and no credit stands against its installment, so every refund the rung takes off was issued for something else — another installment's overpayment, or a proration credit. In the ended-enrollment refund the same refund is then counted twice: "credits left to return" already nets "the refunds issued on it other than refunds against the payment returned as a duplicate". Demonstrated on each world in 0.md and 1.md (task 1: the fall-through leaves the ended enrollment with an unrefunded credit balance of 65.02, defeating the policy's own purpose). Struck in both policies.

**N4 — SOURCE-POLICY RED (charter level): supplement effective-month day share, rule vs compute** (§ rule_compute_equivalence). No consequence in task 1 (a QLE enrollment takes the whole-month rung).

**N5 — Observation: label.** one_time_payment_lapse_window and draft_history_window are labelled `method` but select a starting month (a number) inside one counting formula. No count consequence (each policy keeps ≥1 method without them).

**N6 — SOURCE-FACTOR RED: duplicate-refund rungs about proration credits can never apply in that policy's scope (task 0).** The duplicate refund is scoped to an enrollment "whose status is applied or active". Base `prime_fee_proration_credit`: a credit arises "When a fee-bearing enrollment ends for a reason listed in fee_credit_eligible_reasons" (the reasons — beneficiary_disenrollment, loss_of_eligibility, region_transfer, death_of_beneficiary — all end the enrollment), and a nonpayment disenrollment, the only one reversed into `active` by reinstatement, "earns no credit". So duplicate_installment rung 2 ("none does but proration credits stand on the account") and duplicate_what_comes_off rung 2 ("none were but proration credits stand against the refunded installment") hold of no customer at this write; each ladder has two reachable rungs. Both struck (the ended-enrollment twins are not affected: ended enrollments do carry credits).

**N7 — Observation: catch-up first-month fall-through.** "otherwise it starts with the month the review was filed, the region bearing the months before the beneficiary came forward" forgives every month between the old paid-through date and the filing month for any good cause other than one documented with medical records, while base `prime_reinstatement` restores the enrollment "from the day after the old paid-through date with no gap ... and the same fee arrangement". No base sentence states that every restored month is billed, so this is recorded as a business-sense observation only.

## closing_checklist (revision 2)

(written after the round-2 reveal; see below)

Written after the round-2 reveal (charter section above unchanged since its 20:48Z freeze). Artifacts byte-unchanged during the audit (`prime.extended.yaml` `62e4e2b4…5892`, `task_tools.py` `f9731c3d…ca78d`).

| item | status |
| --- | --- |
| per-task files carry a frozen revision_2 derivation then a comparison; revision-1 text untouched | yes |
| unique solution (blind derivation = GT on every argument, both tasks) | yes |
| scopes disjoint and complete; tools/uuid8s | yes (unchanged) |
| trees: 1-3 prerequisites, value_input floor, owner=user write, acyclic | yes (both tasks: 3 prerequisites, 2 value_input, one user write) |
| proof text recomputes | yes (0-C1, 0-P1, 1-F3 closed) |
| charter self-consistent | **no** — N1 (received ladders: rule vs compute), N4 (supplement day share: rule vs compute); neither changes a value in either task world |
| every computation keeps 4-6 surviving factors | **no** — duplicate_refund 3 (N6, N3), ended_refund 3 (N3), initial_payment 3 (N1); supplement keeps 4 but its baseline is N2's double deduction |
| gates re-run on final form | not re-run by the auditor (coordinator snapshot cited; artifacts unchanged since) |

Revision-1 RED closure: G1, G2, G3, G4, G5, G6, G7, G8, G9, G10, G11, 0-C1, 0-P1, O1, 1-F2, 1-F3 — closed. 0-F1, 1-F1 — not closed in substance (re-opened as 0-F2, 1-F4 on new causes). New in revision 2: N1, N2, N3, N4, N6 (RED); N5, N7 (observations). No regression in the problem-tree or unique-solution relationships.

**The difficulty does not yet pass the source-layer audit**: the factor relationship fails in both tasks and the charter carries two rule/compute disagreements.

## revision_3

### charter_global_frozen (revision 3)

- Written before the round-3 `tasks/*.json` (mtime 22:43) and the difficulty `worklog.md` (22:42) were opened.
- Re-hashed, equal to the brief: `prime.extended.yaml` `97c18b4c5089db761f3fcb480146a45f87aa22c8d627d5714a5e07a203167b63` (changed → charter sections re-derived), `task_tools.py` `9e813f811e39aa63a5fd19a037e942986bad13f8eaf05c29a0a2975293a92e01` (changed → action binding re-checked), view 0 `871c907b…bf9c` (unchanged), view 1 `0fc04aaa…d198` (re-seeded). Base section still byte-identical to `blueprint/products/prime.yaml`.
- contamination_disclosure: revision-1 and revision-2 GT were read in those rounds. Task 0's world is unchanged since revision 2, so its round-2 GT values are known to the auditor; see 0.md revision_3.
- Harness: `/tmp/erl55_audit_prime/chk.py`, `r3_t0.py`, `r3_t1.py`.

### delta and re-derivation (revision 3)

What changed (read in full): duplicate refund (rung 2 of `duplicate_installment` now "none does but the largest single payment on the account exceeds the charge of the installment it was posted against"; `duplicate_what_comes_off` removed — "Refunds already issued against the payment the duplicate refund returns come off its excess" is now a plain rule; new `duplicate_kept_installment_value` monthly/quarterly/annual by the latest-coverage charge); current-installment payment (`one_time_payment_received` rung 2 now "none does but payments that name no installment were posted ...", fall-through 0; lapse window relabelled `parameter`); draft (history window relabelled `parameter`); ended refund (`refund_what_comes_off` fall-through now 0); supplement (effective-month day share now "the lesser of 30 and its days"; `supplement_billing_shape` replaced by `supplement_charges_counted`: posted after the application date → every charge / application before the effective date → the charge beginning on the effective date / otherwise → charges posted on the application date); initial payment (`initial_received` rung 2 and fall-through as in the current payment). Catch-up and unused credit unchanged in substance.

Mechanical: every `compute_basis` entry verbatim in its rule, every `baseline.rule` sentence in its rule, every `policy_source` verbatim in its own rule and absent from the depended-on rule, `resolved_by` = target tool on all six edges, graph acyclic (`chk.py`). Prerequisite sentences, conditions and kinds unchanged from revision 2 (§ prerequisite_sentences there stands). Override sweep: no new conflict; the supplement's declared superseded clause still covers the changed first-installment valuation.

Tool module: the only change moves the balance write out of the `_Account` helper into each tool body (`new_balance` returns a figure, the tool calls `ctx.update`); signatures, owners, uuid8s, effects and docstrings' sequence-silence are unchanged; no body judges eligibility, order or amount (`if enr:` only guards a missing enrollment row).

Rule/compute: `one_time_payment_received` and `initial_received` now say in the rule what compute does (rung 2 needs unnamed payments to exist; fall-through 0) — **N1's rule/compute half closed**. Supplement day share now capped in the rule — **N4 closed**. No new rule/compute disagreement found in the changed policies.

### factor_ladders (revision 3)

Changed or re-examined ladders:
| policy | factor | test |
| --- | --- | --- |
| duplicate_refund | duplicate_installment | holds (rung 2 reachable on an active account: one payment larger than its installment) — **N6 closed** |
| | duplicate_kept_installment_value | holds |
| | duplicate_amount_kept | holds |
| current_installment_payment | one_time_payment_received | **struck (N8)** |
| | one_time_payment_lapse_window | holds, label now honest — **N5 closed** |
| draft | draft_history_window | holds, label honest |
| | draft_excess_elsewhere | **struck (N9; missed in revisions 1-2, disclosed)** |
| ended_refund | refund_what_comes_off | **struck (N9)** — N3's unrelated-refund fall-through is gone (**N3 closed**) |
| supplement | supplement_charges_counted | holds (three distinct counted sets) — **N2 closed** (no double deduction remains) |
| initial_payment | initial_received | **struck (N8)** |

Surviving counts: catch_up 5 (2p/3m); duplicate_refund 5 (3p/2m); current_installment_payment 4 (3p/1m); draft 4 (3p/1m); unused_credit 4 (3p/1m); ended_refund **3** (1p/2m); supplement 5 (2p/3m); initial_payment **3** (2p/1m).

### findings (revision 3)

Closed: **N1** (rule/compute half; the ladder half recurs as N8), **N2**, **N3**, **N4**, **N5**, **N6**. Open: **N7** (observation, unchanged).

**N8 — SOURCE-FACTOR RED: the two "received" ladders select one method in all three rungs (tasks 0 and 1).** `one_time_payment_received`: "Where payments stand against the settled installment, they count as received; where none does but payments that name no installment were posted on the account since the month the installment fell due, those payments count as received; otherwise nothing counts as received." `initial_received`: "Where payments posted on the account name an installment charge, those payments count as received; where none does but payments that name no installment were posted on the account, those payments count as received; otherwise nothing counts as received." Rungs 1 and 2 both select "the payments posted count as received" (over two subsets of the same payments), and the fall-through is that method on a world with no such payment (nothing posted → nothing received). This is revision 1's G5 shape ("with nothing posted, what was posted is 0"). Both struck.

**N9 — SOURCE-FACTOR RED: "take off A, else B, else nothing" ladders whose fall-through is the earlier rungs' own value (tasks 0 and 1).** `refund_what_comes_off`: "Where refunds were already issued against the payment returned as a duplicate, they come off its excess; where none were but proration credits stand against that installment, those credits come off; otherwise nothing comes off." `draft_excess_elsewhere`: "... that excess comes off ...; where no such excess stands but proration credits stand on the account, those credits come off; otherwise nothing comes off." The fall-through is reached only when both named quantities are absent, and there it selects exactly what either earlier rung would take off on that world — nothing; it adds no third treatment, the same reason revision 1 struck `one_time_payment_owed_again` ("with no refund, the refund is 0"). Both struck. **Auditor disclosure:** `draft_excess_elsewhere` had this shape in revisions 1 and 2 and was passed there; that was a miss under the test this audit applied to G5, recorded here rather than rewritten into the older revisions.

## closing_checklist (revision 3)

(written after the round-3 reveal; see below)

Written after the round-3 reveal; the revision-3 charter section above is unchanged since its 22:50:42Z freeze. Artifacts byte-unchanged during the audit (`prime.extended.yaml` `97c18b4c…7b63`, `task_tools.py` `9e813f81…2e01`).

| item | status |
| --- | --- |
| revision_3 sections appended; older revisions untouched | yes |
| unique solution (both tasks: derivation = GT on every argument) | yes |
| scopes disjoint/complete; tools and uuid8s; tools judge nothing | yes |
| trees (3 prerequisites each, 2 value_input, one owner=user write, acyclic) | yes |
| charter self-consistent (rule/compute, overrides, prerequisite sentences) | yes — N1 (rule/compute half) and N4 closed; no new disagreement |
| proof text recomputes | yes |
| every declared factor has a real ladder | **no** — N8 (two received ladders), N9 (refund_what_comes_off; draft_excess_elsewhere, an auditor miss in revisions 1-2) |
| every computation keeps 4-6 surviving factors | **no** — ended_refund 3, initial_payment 3; all others 4-5 |
| gates re-run on final form | not re-run by the auditor (coordinator snapshot cited) |

Round-2 RED closure: N1, N2, N3, N4, N5, N6, 0-F2 closed; 1-F4 partly closed (supplement) and re-opened as 1-F5; N7 open as observation. New: N8, N9 (SOURCE-FACTOR). No regression in the policy, problem-tree or unique-solution relationships.

**The difficulty does not yet pass the source-layer audit**: SOURCE-FACTOR fails in both tasks (task 0 on two unreal ladders within the count bound; task 1 below the count bound in two computations).

## revision_4

### charter_global_frozen (revision 4)

- Written before the round-4 `tasks/*.json` (mtime 2026-10-12 00:26) and the difficulty `worklog.md` were opened.
- Re-hashed, equal to the brief: `prime.extended.yaml` `a16692f8c9a1a9863ac116cfbd5d04fa296c0950bce3983981fa9d8dbf4024a5` (changed → re-derived; a copy is kept at `/tmp/erl55_audit_prime/prime.extended.r4.yaml` for the next diff), `task_tools.py` `9e813f81…2e01` (unchanged → revision-3 action-binding conclusion carried forward), view 0 `871c907b…bf9c` (unchanged), view 1 `37a6b92f…ad26` (re-seeded). Base section byte-identical to `blueprint/products/prime.yaml`.
- contamination_disclosure: GT of rounds 1-3 was read in those rounds; task 0's world has not changed since round 2.

### delta (revision 4)

- current_installment_payment: `one_time_payment_received` removed ("The payments standing against the settled installment count as received" is now a plain rule); new `one_time_payment_ahead_value` (an installment paid ahead is valued like the installment the method on file last collected: monthly 1/12 / quarterly 1/4 / otherwise the whole fee).
- draft: `draft_excess_elsewhere` removed (the excess now plainly "comes off"; the proration-credit rung is gone); new `draft_history_end` (the history runs through the month before the current month for a monthly arrangement / the last month of the previous calendar quarter for a quarterly one / "through December of the previous plan year otherwise"); the baseline sentence is now "draws that installment's whole open amount ... less the payments posted on the account since the first month of the current plan year against its other installments net of the refunds posted since then, never below zero".
- unused_credit: `credit_months_counted` is now a `parameter` choosing the first counted month (installment's first month / the disenrollment month / the month after it); `credit_what_comes_off` relabelled `method`.
- ended_refund: `refund_what_comes_off` removed (refunds against the returned payment come off — plain rule); new `refund_history_window` ("The credits and refunds weighed for the credits left to return are those posted from a starting month: where the enrollment took effect before the current plan year and ended in it, the first month of the current plan year; where it took effect and ended in the same plan year, the month containing its effective date; otherwise every entry on the account counts").
- initial_payment: `initial_received` removed ("The payments posted on the account count as received" — plain); new `initial_method_start` (QLE → the month after the application month; open season → the first month of the plan year it took effect; otherwise the effective month), feeding a months-ahead ladder that now also requires "the method has not yet started".
- catch_up, duplicate_refund, supplement: no substantive change found.

Mechanical (`chk.py`): compute_basis verbatim; baseline sentences in the rule; six `policy_source` sentences verbatim, not restated, `resolved_by` = target tool; acyclic; prerequisite sentences and conditions unchanged from revision 2. Rule/compute: the new plain rules and ladders match their bindings (`mp_received = mp_paid_on`, `dd_off = MX(0, dd_excess)`, `rf_win`, `rp_start_m`, `rp_received` = all payments).

### factor_ladders (revision 4)

| policy | factor | test |
| --- | --- | --- |
| current_installment_payment | one_time_payment_ahead_value | holds |
| draft | draft_history_end | holds as a ladder; see N10 for the baseline it composes |
| unused_credit | credit_months_counted | holds (three distinct first months) |
| | credit_what_comes_off | holds (credits / refunds / shortfall — three distinct quantities) |
| ended_refund | refund_history_window | **struck (N12)** |
| initial_payment | initial_method_start | holds |
| | initial_months_ahead | holds |
Charter-wide sweep for N8/N9 shapes: no remaining ladder has a fall-through equal to an earlier rung's value on its own situation (amount_kept 2/1/0 by method, months_ahead, switch-month value, region-bears, effective-month value and credit_what_comes_off all select distinct treatments).

Surviving counts: catch_up 5; duplicate_refund 5; current_installment_payment 5 (4p/1m); draft 5 (4p/1m); unused_credit 4 (3p/1m); ended_refund **3** (1p/2m); supplement 5; initial_payment 4 (3p/1m).

### findings (revision 4)

Closed: **N8** (both received ladders replaced by plain rules), **N9** (both "A, else B, else nothing" ladders removed). Open: **N7** (observation).

**N10 — SOURCE-FACTOR RED: the draft's baseline is a straw man, and its two window fall-throughs compose an inverted history (task 0).** baseline.rule: "The region's draft is toward the installment whose coverage period begins latest and draws that installment's whole open amount, its charge less the payments posted against it, less the payments posted on the account since the first month of the current plan year against its other installments net of the refunds posted since then, never below zero". Every payment that paid another installment this year is subtracted from the draft, with nothing set against it, so any customer who paid January-September on time can never be drawn for October (open 32.51 less nine paid installments → 0.00). The ladders behind it: `draft_history_window` fall-through ("the first month of the current plan year") and `draft_history_end` fall-through ("through December of the previous plan year") give a history that ends before it starts; for an annual-arrangement customer (the fall-through's own situation) any payment made this year toward an earlier year's installment is then treated as an excess and taken off the draft. No business draws that way. On task 0's world see 0.md.

**N11 — SOURCE-POLICY RED (charter level): the ended-enrollment refund can leave a credit balance unrefunded, against base.** Base `prime_fee_proration_credit` (not overwritten; `overwrite: []`): "A credit that leaves the account with a credit balance is refunded through the method of the original payment within fee_refund_issue_days." Extended: "The credits left to return are the proration credits posted on the account less the refunds issued on it other than refunds against the payment returned as a duplicate", so a refund of any other overpayment is subtracted from the credits. Same situation, two answers: task 1's world with the enrollment's window on its fall-through ("every entry on the account counts") — the account's credit balance after the April credit is 132.51 (fee_balance_due -132.51); base refunds 132.51; the extended rule subtracts the 2025-08-12 refund of a separate 2025 duplicate (`ccb4043c`, 97.53) from the credits and refunds 100.00, leaving 32.51 of credit balance — and leaving the initial payment's gate ("shows a fee balance of zero") unmet by the very write that is supposed to meet it. In task 1's actual world the plan-year window excludes that refund, so no consequence on the scored value.

**N12 — SOURCE-FACTOR RED: `refund_history_window` weighs a condition no business weighs for a credit-balance refund (task 1).** Its rungs choose the first month from which credits and refunds are counted by plan-year boundaries of the enrollment ("took effect before the current plan year and ended in it" / "took effect and ended in the same plan year" / otherwise every entry). Proration credits arise only when an enrollment ends (base: "When a fee-bearing enrollment ends ..."), so every credit of an ended enrollment is posted at or after its end and every rung counts the same credits; the rungs differ only in which refunds of other overpayments N11's rule subtracts. A credit balance is refunded whole whatever plan year the enrollment began in. Struck; the ended refund keeps 3 factors.

## closing_checklist (revision 4)

(written after the round-4 reveal; see below)

Written after the round-4 reveal; the revision-4 charter section above is unchanged since its 00:31:09Z freeze. Artifacts byte-unchanged during the audit.

| item | status |
| --- | --- |
| revision_4 sections appended; older revisions untouched | yes |
| unique solution (derivation = GT on every argument, both tasks) | yes |
| scopes, tools, uuid8s, tools judge nothing | yes |
| trees (3 prerequisites, 2 value_input, one user write, acyclic) | yes |
| charter self-consistent | **no** — N11 (ended refund can leave a credit balance unrefunded, against base; no consequence in task 1's world) |
| proof text recomputes | yes |
| every declared factor has a real ladder; every baseline a real method | **no** — N12 (refund_history_window), N10 (draft baseline / inverted window) |
| every computation keeps 4-6 surviving factors | **no** — ended_refund 3; all others 4-5 |
| gates re-run on final form | not re-run by the auditor (coordinator snapshot cited) |

Round-3 RED closure: N8, N9, 0-F3 closed; 1-F5 half closed (initial payment) and re-opened for the ended refund as 1-F6; N7 open (observation). New: N10, N12 (SOURCE-FACTOR), N11 (SOURCE-POLICY, charter level). No regression in the problem-tree or unique-solution relationships.

**The difficulty does not yet pass the source-layer audit.**

## revision_5

### charter_global_frozen (revision 5)

- Written before the round-5 `tasks/*.json` (mtime 2026-10-12 02:27) and the difficulty `worklog.md` were opened.
- Re-hashed, equal to the brief: `prime.extended.yaml` `82f0331389170370fc95fa027f4515f5e609e50f5e8a044002444a86d48c6efd` (changed; diffed policy by policy against the kept revision-4 copy; revision-5 copy kept at `/tmp/erl55_audit_prime/prime.extended.r5.yaml`), `task_tools.py` `60738d7d50f4c45551c622ee77b00a4869a7aba9ea5053890e3642060851fb7b` (changed), view 0 `871c907b…bf9c` (unchanged), view 1 `5728c214…cdb2` (re-seeded). Base section byte-identical to `blueprint/products/prime.yaml`.
- contamination_disclosure: GT of rounds 1-4 read in those rounds; task 0's world unchanged since round 2.

### delta and re-derivation (revision 5)

Policy-by-policy diff against revision 4: catch_up, current_installment_payment, unused_credit, supplement unchanged. `prime_ext_duplicate_payment_refund`: rule scope now "an installment other than the first installment". `prime_ext_ended_enrollment_refund` **removed**. **New** `prime_ext_first_installment_duplicate_refund` (target `refund_first_installment_duplicate_7d2e91c4`, agent; scope "the first installment of a new fee-bearing TRICARE Prime enrollment has been paid more than once"; 4 factors: value_share p, payment_returned m, kept_value p, amount_kept p; declared overwrite of base "A credit that leaves the account with a credit balance is refunded ..."). `prime_ext_draft_on_file_method`: history end is now a plain rule by arrangement; the start's plan-year anchor is "the plan year in which the history ends"; the excess that comes off is "less what the region keeps on the account for the next installment"; factor `draft_history_end` replaced by `draft_amount_kept` (allotment 2 / card or EFT 1 / otherwise 0); baseline now "less the whole excess of the account history running from the first month of the plan year in which the history ends, with nothing kept". `prime_ext_initial_payment`: the ended-refund gate sentence is replaced by two sentences — "An initial payment toward a new enrollment is figured only after its first installment carries no payments beyond its value other than what the region keeps on the account for the installments that follow." (value_input, resolved by the new refund tool) and "An initial payment toward a new Prime enrollment is not taken until every month of the last paid installment of a Prime enrollment the beneficiary ended earlier in the same plan year that a following TRICARE Select enrollment's coverage reaches, or that falls after the month containing its disenrollment date, stands credited." (state_gate, resolved by the unused-month credit).

Mechanical (`chk.py` on the new file): compute_basis verbatim; baseline sentences in rule; six edges' `policy_source` verbatim in the blocked rule, not restated, `resolved_by` = target tool; graph acyclic (task 1 tree is now a fan: initial <- supplement, <- first-installment duplicate refund, <- unused credit).

Prerequisite sentences (new ones): "figured only after ... carries no payments beyond its value other than what the region keeps ..." — "only after", record-visible state (payments vs value, with the keep rule the duplicate policies state), no tool/id; condition matches; single writer: the first-installment refund (the other duplicate policy now excludes the first installment). "not taken until every month ... stands credited" — "not ... until", state; condition matches the credit rule's Select reading; single writer: the credit tool. Scope partition: task 0 {draft, catch_up, duplicate_refund, current_installment_payment}, task 1 {initial_payment, supplement, first_installment_duplicate_refund, unused_credit} — disjoint and complete over the eight extended policies.

Tool module: `refund_credit_balance_12944b90` removed; `refund_first_installment_duplicate_7d2e91c4` added (uuid8 independent; docstring names no other tool and states no order; body writes one refund row against the named payment, copies its method, moves the balance; judges nothing). Every `(target_tool, computes)` claimed once.

Override sweep: the base sentence "A credit that leaves the account with a credit balance is refunded through the method of the original payment within fee_refund_issue_days" is now superseded by both duplicate-refund policies (declared), each replacing it with a keep-installments rule about duplicate excess. No extended policy now settles the refund of a proration-credit balance on an ended enrollment (observation O-r5a below).

### factor_ladders (revision 5)

| policy | factor | test |
| --- | --- | --- |
| draft | draft_amount_kept | holds (2 / 1 / 0 by method on file; distinct) |
| | draft_history_window | holds (start anchored to the history's own plan year — no inverted window) |
| first_installment_duplicate_refund | first_duplicate_value_share | holds |
| | first_duplicate_payment_returned | holds |
| | first_duplicate_kept_value | holds |
| | first_duplicate_amount_kept | holds |
Surviving counts: catch_up 5; duplicate_refund 5; current_installment_payment 5; draft 5 (4p/1m); unused_credit 4; first_installment_duplicate_refund 4 (3p/1m); supplement 5; initial_payment 4. Draft baseline: open amount less the whole account excess since January with nothing kept — a real (if harsh) accounting method that yields a definite number.

### findings (revision 5)

Closed: **N10** (no inverted history; baseline nets payments against charges), **N11** and **N12** (the ended-enrollment refund and its window factor are removed). Open: **N7** (observation).

No new SOURCE-POLICY, SOURCE-CHAIN or SOURCE-FACTOR defect found in the charter.

**O-r5a — Observation: the ended enrollment's proration-credit balance has no settling write in this difficulty.** After task 1's credit the old enrollment stands at -32.51. Base's refund-within-30-days sentence is superseded (declared) by the two duplicate-refund policies, both scoped to duplicate payments on applied/active enrollments, and no task tool refunds a proration credit. Because the customer asks only to pay up the new enrollment and no rule makes that refund a prerequisite of anything in the tree, it is outside the scored solution; it is not a red light under the four relationships. The persona line "or to the card you paid with" now points at no gold action (passive, triggered only if the agent says so).

Written after the round-5 reveal; the revision-5 charter section above is unchanged since its 02:31:56Z freeze. Artifacts byte-unchanged during the audit (`prime.extended.yaml` `82f03313…6efd`, `task_tools.py` `60738d7d…fb7b`).

| item | status |
| --- | --- |
| per-task files 0.md, 1.md alongside this file; revisions 1-5 appended in order, older text untouched; every revision's comparison carries a verdict | yes |
| extended policies fully covered; task scopes (whole trees) pairwise disjoint | yes — task 0 {draft, catch_up, duplicate_refund, current_installment_payment}; task 1 {initial_payment, supplement, first_installment_duplicate_refund, unused_credit} |
| task tools and GT closed; each task tool's uuid8 independent and frozen | yes (8 tools, each claimed once; `7d2e91c4` new and independent) |
| each tree: 1-3 prerequisite problems, ≥ max(n−1,1) value_input, ≥1 owner=user write, acyclic; whole graph acyclic | yes (task 0: 3 / 2 vi / user current payment; task 1: 3 / 2 vi / user initial payment) |
| every computation: self-sufficient baseline giving a definite number ≠ gold; 4-6 factors with real ladders (≥2 parameter, ≥1 method); per task ≥1 multi-source and ≥1 cross-difficulty; every factor bears weight | yes (counts 5/5/5/5 and 4/4/5/4; all factors bear weight on their worlds) |
| charter self-consistent (overrides declared, rule = compute, prerequisite sentences single-reading) | yes |
| unique solution (blind derivation = GT on every argument) | yes, both tasks (task 0's world unchanged since round 2 — disclosed) |
| instantiation gates on the final form | coordinator's round-5 snapshot cited (all green; traceability deferred until the KB is rendered); not re-run by the auditor |

Round-4 RED closure: N10, N11, N12, 0-F4, 1-F6 closed. Open observations: N7 (catch-up fall-through start), O-r5a (unrefunded proration-credit balance on task 1's old enrollment). No new RED; no regression.

**All four relationships pass for both tasks: the difficulty passes the source-layer audit as of revision 5.**

## revision_6

### charter_global_frozen (revision 6)

- Written before the round-6 `tasks/*.json` (mtime 2026-10-12 04:29) and the difficulty `worklog.md` were opened.
- Re-hashed, equal to the brief: `prime.extended.yaml` `9e03b0f0cd71c7d03a8eb79ae942e8f0ecf1174c52159589a1b2be153d73dd33` (changed; diffed against the kept revision-5 copy; revision-6 copy at `/tmp/erl55_audit_prime/prime.extended.r6.yaml`), `task_tools.py` `60738d7d…fb7b` (unchanged → revision-5 action-binding conclusion carried forward), views 0 `871c907b…bf9c` and 1 `5728c214…cdb2` (both unchanged since revision 5). Base section byte-identical to `blueprint/products/prime.yaml`.
- contamination_disclosure: both worlds are unchanged since revision 5 and their revision-5 GT is known to the auditor; this round is a charter re-derivation plus a recomputation on the unchanged worlds, not a blind task derivation.
- **Auditor disclosure:** the five renderer items were present in the charter the auditor passed at revision 5 (and, for most, earlier): (1) duplicate refunds — rule "refunds already issued against the payment the duplicate refund returns" vs compute summing refunds against the latest payment; (2) initial payment — "no installment covers a month after the current month" vs compute testing the latest coverage *start*; (3) Select enrollment without a disenrollment date — compute capped at the current month, no rule sentence; (5) supplement baseline — effective-month days "from the effective date" with no end day and an unstated 30-day fallback; (6) draft — rule excluded the drafted installment's charge always, compute only when it differed from the latest-coverage installment. Revision 5's "No new SOURCE-POLICY ... defect found in the charter" was wrong on these five; it is not rewritten, and this revision records the misses.

### delta (revision 6) — verification of the five fixes

| item | rule now | compute now | verdict |
| --- | --- | --- | --- |
| (1) duplicate refunds (both policies) | "less the refunds already issued against that latest payment"; "is posted against the latest payment posted against the refunded installment and goes back through that payment's method"; "Refunds already issued against the latest payment posted against the refunded installment come off its excess" (first-installment policy: same, "against the first installment charge") | `dr_ref_ret` / `rf_ref_ret` = refunds with `related_fee_entry_id = *_late_id` (the latest payment) | equal; the posting target and method are now defined when earlier payments are returned |
| (2) initial payment ahead | "no installment on the account covers a month after the current month" (unchanged) | `rp_last_end` = latest `coverage_period_end`; `rp_billed_ahead` = its month > now | equal (a charge beginning this month and ending later now counts as covering a later month) |
| (3) Select with no disenrollment date (catch-up, credit, supplement) | "or, where the Select enrollment has no disenrollment date, when it falls after the month containing the Select effective date" / "or every month from its effective month on where it has no disenrollment date"; touched only by the effective or disenrollment month | `*_s_hi = 99999` when no disenrollment date (no end month to touch; whole months run to the span's end) | equal; credit-edge `condition` updated to match |
| (5) supplement effective-month days | "its days from the effective date through the last day of the coverage period of the installment charge beginning on the effective date, 30 where no such charge stands" (baseline and rung) | `su_eff_days = DAYS(eff, first_end) + 1`, else 30; `MN(30, ·)` | equal |
| (6) draft excess | "other than the drafted installment" | `dd_chg_w` subtracts the drafted installment's in-window charge unconditionally | equal |

Recomputation on the unchanged worlds (`r3_t0.py`, `r5_t1.py` against the new charter): every scored value and every factor-baseline figure is unchanged (task 0: 113.54 / 17.98 / 45.02 / 65.02; task 1: 32.51 / 24.98 / 16.01 / 48.52; load-bearing figures unchanged). Mechanical checks (`chk.py`): compute_basis verbatim, baseline sentences in rule, six edges verbatim and resolved by their target tools, acyclic. No ladder changed; factor counts and the revision-5 ladder conclusions stand.

### charter-wide sweep for the same shapes (revision 6)

Every binding of the eight policies was read against its rule sentence for: open-ended or null inputs, "latest" by which date, interval endpoints, conditional exclusions, scope clauses, and calendar-month windows. Findings:

**N13 — SOURCE-POLICY RED (charter level, no task consequence): calendar-month windows are evaluated with a day-adjusted month difference to today.** Every `within_months=` window (catch-up month counts and quarter/year sums by `coverage_period_start`; draft `dd_pay_w`/`dd_ref_w` by `posted_date` and `dd_chg_w`; current payment lapse `mp_coll`; initial payment `rp_win_all`, `rp_eff_only`, `rp_started`) counts a row in month m only when `MONTHS(row_date, NOW)` falls in range, and `MONTHS` subtracts one when the row's day of month exceeds today's. The rules speak of calendar months ("from that starting month", "begins in the month containing the effective date", "since a starting month"). Demonstrated (`/tmp/erl55_audit_prime/r6_hyp.py`): (A) task 1's world with the application on 2026-08-10 (before the 2026-08-24 effective date): rule — the initial payment settles the charge beginning in August, 32.51; compute `rp_owed` = 0.00. (B) task 0's world plus a recurring-card payment posted 2026-03-20 (before the April lapse window): rule — the card has not collected since April, one installment ahead, 45.02; compute counts the March payment as inside the window and gives 12.51. In both task worlds no row sits on the wrong side of a window edge (all values recompute to the rule's figures). Revision 1 recorded this artefact as an observation without demonstrating it; that was an under-call.

**N14 — SOURCE-POLICY RED (charter level, no task consequence): the duplicate refund's scope exclusion is not applied when choosing the installment.** Rule: "This policy settles the refund owed when an installment other than the first installment ... has been paid more than once", then "Where a payment made through a method other than the enrollment's payment arrangement stands on the account, the duplicate refund concerns the installment against which the largest such payment stands ...". Compute `dr_inst` selects over every installment, the first included. Same situation, two answers: an active account whose largest other-method payment stands on its first installment and which also carries a duplicate on a later installment — rule: the policy concerns the later installment (the first installment belongs to `prime_ext_first_installment_duplicate_refund`); compute: refunds against the first installment, overlapping the other policy. Task 0's first installment (January 2020) is not on the ledger.

Observations: `LATEST(..., amount=max)` breaks ties between equal largest payments by posting date, which no rule states; `CFIELD('select', …)` reads one Select enrollment where the rules say "the beneficiary's TRICARE Select enrollment" (singular) — neither reaches a task world. The one-time payment's ahead value falls to "the whole annual fee" when the method on file never collected (the fall-through's literal reach).

### findings (revision 6)

The five renderer items are closed. New: N13, N14 (SOURCE-POLICY RED, charter level; no scored value in either task moves). Open observations: N7, O-r5a.

## closing_checklist (revision 6)

(written after the round-6 reveal; see below)

Written after reading the round-6 task files; the revision-6 charter section above is unchanged since 04:45:47Z. Artifacts byte-unchanged during the audit.

| item | status |
| --- | --- |
| revision_6 appended; older revisions untouched | yes |
| the five renderer items fixed in rule and compute | yes (table above) |
| no scored value or factor sensitivity moved | yes — both tasks' `computations` and gold arguments equal revision 5 and the recomputation |
| task-level relationships (tree, factors, unique solution) | unchanged from revision 5: PASS for both tasks |
| charter self-consistent (rule = compute everywhere) | **no** — N13 (day-adjusted month windows) and N14 (duplicate-refund scope not applied in selection); neither reaches a task world |
| gates | coordinator snapshot cited (all green, traceability OK); not re-run by the auditor |

Both tasks pass all four relationships on their own worlds. The difficulty's charter still carries two SOURCE-POLICY REDs (N13, N14) with demonstrated two-answer situations outside the task worlds; the documents rendered from this charter will state the calendar-month and first-installment-exclusion rules that the compute does not follow in those situations. **Charter-level SOURCE-POLICY RED open; task-level PASS.**

## revision_7

### charter_global_frozen (revision 7)

- Written before the round-7 `tasks/*.json` (mtime 2026-10-12 05:25) and the difficulty `worklog.md` were opened.
- Re-hashed, equal to the brief: `prime.extended.yaml` `f4988ce50c88ac6314fea7efab4d1b5da5126d1d447ff65344cdb45f34b0394a` (changed; diffed against the kept revision-6 copy; revision-7 copy at `/tmp/erl55_audit_prime/prime.extended.r7.yaml`), `task_tools.py` `60738d7d…fb7b` (unchanged), views 0 and 1 unchanged since revision 5. Base section byte-identical to `blueprint/products/prime.yaml`.
- contamination_disclosure: both worlds and their GT known since revision 5; this round re-derives the charter and recomputes on the unchanged worlds.

### delta and verification (revision 7)

**N13 (month windows).**
- Current payment lapse and initial-payment "method started": now calendar-exact (`MONTHS(epoch, last collection date) >= start month`). Re-running revision 6's hypothetical B (card payment posted 2026-03-20, window from April): compute 0 collections → 45.02, the rule's figure.
- Initial payment settlement: rule restated as computed — "settles every installment charge on the account" (late application) / "the installment charge whose coverage period begins on the effective date" (application before the effective date); compute sums exactly those. Hypothetical A (application 2026-08-10): compute 32.51, the rule's figure.
- Catch-up and draft charge windows: new rule sentence "Every installment charge on the account begins on the first day of the period it covers, except a first installment, which begins on the enrollment's effective date; a charge begins in the month containing that day." For day-1 starts the `within_months` bucket is exact; the first installment's month is corrected in every binding (`cu_fi_*`, `dd_fi_*`: the true month added, the day-adjusted bucket removed). Hypothetical H1 (`r7_hyp.py`: task 0's April charge turned into a first installment beginning 2026-04-15): catch-up 113.54, as the rule gives. The invariant is grounded in base (`prime_enrollment_fee_schedule`: installments "are due on the first day of the period they cover"; first installment from "the month containing the enrollment effective date") and in the tools the charter names (catch-up and supplement coverage start on the first day of a month). The reworker's untested case — a non-first installment beginning mid-month — is excluded by that rule sentence. Observation only: a seed row violating it would be mis-bucketed silently.
- Catch-up annual shape: rule now "whose coverage begins in the current plan year on or before today", matching the window (future-starting charges excluded).
- Draft payments and refunds: rule now states the rolling look-back the compute uses: "what was posted after the date that falls as many months before today as there are calendar months from its starting month through the current month - on the same day of the month as today, or on the last day of that month where it is shorter - through today". The auditor checked this against `within_months` on posted dates: a row is counted when `MONTHS(posted, today) < k`, which holds exactly when it was posted after the same-day date k months back (last day of a shorter month) and not after today. Rule = compute.
- **N13 closed.**

**N14 (duplicate-refund scope).** Rule: "it does not settle a duplicate on the first installment charge ..."; "Where the installment so chosen is the first installment charge, this policy refunds nothing."; compute `result = 0` when `dr_inst` is the first installment charge (hypothetical H2: 0). Rule = compute. **N14 closed as a rule/compute item; see N15.**

**Observations addressed:** tie-break stated ("Of equally large payments the one posted latest is taken"); one-time payment ahead value falls back to the settled installment where the method never collected (rule and compute). The Select reading still takes one Select enrollment (`CFIELD`) where the rules say "the beneficiary's TRICARE Select enrollment" — unchanged observation.

Recomputation on the unchanged worlds: task 0 113.54 / 17.98 / 45.02 / 65.02, task 1 32.51 / 24.98 / 16.01 / 48.52; every factor-baseline and load-bearing figure equal to revision 6. Mechanical checks pass (compute_basis verbatim, baseline sentences in rule, six edges verbatim and resolved by their target tools, acyclic). Ladders unchanged except wording/bindings of `one_time_payment_ahead_value`, `one_time_payment_months_ahead`, `initial_charges_settled`, `initial_method_start`; each still has three distinct rungs; counts unchanged.

### charter-wide sweep (revision 7)

Remaining `within_months` uses: catch-up (coverage starts, covered by the day-1 sentence plus the first-installment correction) and draft (coverage starts likewise; payments/refunds by the stated look-back). No other window, null-bound, endpoint or conditional-exclusion mismatch found.

**N15 — SOURCE-POLICY RED (charter level, no task consequence): on an account whose largest other-method payment stands on its first installment, the draft waits on a duplicate refund that no policy will make.** Passages: draft — "No draft is made on an account until the region has refunded the duplicate payment found on it."; duplicate refund — "Where the installment so chosen is the first installment charge, this policy refunds nothing."; the first-installment policy settles only "the first installment of a new fee-bearing TRICARE Prime enrollment". Situation (H2, `r7_hyp.py`): task 0's account plus a 2020 first-installment charge carrying a 200.00 EFT payment — the duplicate policy chooses that installment and refunds 0.00 (rule and compute agree), the April 75.00 duplicate is never refunded, and the first-installment policy does not reach a 2020 enrollment. Two readings of the draft's gate then stand: (a) a 0.00 refund posted under the duplicate policy satisfies "has refunded the duplicate payment found on it" and the draft proceeds; (b) the duplicate found (April) is never refunded, so no draft is ever made. The reworker flagged this trade-off; under the self-consistency relationship it is a two-answer situation, recorded as RED with no consequence in either task world (task 0 has no first-installment charge on its ledger; task 1's root is not the draft).

Observation O-r7b: the draft's payment look-back now starts mid-month before the history's starting month while its charge window starts on that month's first day, so a payment posted in that half-month against an earlier installment is weighed as excess with no charge set against it. The rule states this explicitly (rule = compute); it is recorded as a business-sense observation. No row of task 0 falls in that half-month (2026-03-15..31).

### findings (revision 7)

Closed: **N13**, **N14**. New: **N15** (SOURCE-POLICY RED, charter level). Open observations: N7, O-r5a, O-r7b, the single-Select reading.

## closing_checklist (revision 7)

(written after the round-7 task files are read; see below)

Written after reading the round-7 task files; the revision-7 charter section is unchanged since 05:49:46Z. Artifacts byte-unchanged during the audit.

| item | status |
| --- | --- |
| revision_7 appended; older revisions untouched | yes |
| round-6 REDs N13, N14 closed (rule = compute; hypotheticals A, B, H1, H2 recompute to the rule) | yes |
| no scored value or factor sensitivity moved | yes |
| task-level relationships | PASS for both tasks (unchanged since revision 5) |
| charter self-consistent | **no** — N15 (draft gate vs a duplicate the charter will not refund, two readings; no task consequence) |
| gates | coordinator snapshot cited (all green); not re-run by the auditor |

**Task level: PASS for both tasks. Charter level: one SOURCE-POLICY RED open (N15).**

## revision_8

### charter_global_frozen (revision 8)

- Written before the round-8 `tasks/*.json` (mtime 2026-10-12 06:10) and the difficulty `worklog.md` were opened.
- Re-hashed, equal to the brief: `prime.extended.yaml` `fa6615d6f10ed5259649ffc39497e3c4ce7159fd2f9541e909f8c4b4b7ccafb4` (changed; diffed against the kept revision-7 copy; revision-8 copy at `/tmp/erl55_audit_prime/prime.extended.r8.yaml`), `task_tools.py` `60738d7d…fb7b` (unchanged), views 0 and 1 unchanged since revision 5. Base section byte-identical to `blueprint/products/prime.yaml`.
- contamination_disclosure: as in revisions 6-7 (recomputation on unchanged worlds).

### delta and verification (revision 8)

Changed: the two duplicate-refund policies and the draft's duplicate-refund prerequisite. Everything else byte-equal to revision 7.

1. Draft sentence (rule and `policy_source`): "No draft is made on an account until the region has made the duplicate refund owed on it, wherever that refund comes to more than nothing."; condition: "Where the duplicate refund the duplicate-refund rule figures on the account's records comes to more than nothing, a prime_fee_refund row of that amount stands against the latest payment on the installment it concerns, after which the rule figures nothing."; fallback reason restated. Four-point test: "until", action named in business words, no tool/id; the "wherever ... more than nothing" clause states when nothing is awaited.
2. Both duplicate policies: "Refunds already issued against the latest payment posted against the refunded installment come off both the payment the duplicate refund returns and its excess"; compute `MX(0, MN(pick − refunded, excess − refunded − kept))`. Stability checked (`r8_hyp.py`, H2'): a 167.49 refund owed becomes 0.00 once posted against the latest payment.
3. Scope split by plan year: the general policy refuses only "the first installment charge ... of an enrollment that took effect in the current plan year"; the first-installment policy "refunds nothing" where "the enrollment took effect before the current plan year". Compute: `dr_new_first`, `rf_old`. Rule = compute.

**N15** — the revision-7 situation (H2: a 2020 first installment carrying the account's largest other-method payment): the general policy now concerns that installment; with a single payment on it the refund owed is 0.00, so by the draft's own clause nothing is awaited and the draft proceeds — one reading; with two payments (H2') it refunds 167.49 and then figures nothing. **N15 closed** (single reading of the draft gate in that situation). Observation O-r8a: in both H2 variants the April 75.00 duplicate is never the installment chosen, so it is never refunded under this charter while the larger first-installment payment stands (the reworker states this).

Recomputation on the unchanged worlds: task 0 113.54 / 17.98 / 45.02 / 65.02 (duplicate: min(75.00 − 2.00, 52.49 − 2.00 − 32.51) = 17.98), task 1 32.51 / 24.98 / 16.01 / 48.52; load-bearing figures unchanged; one factor baseline moved — `duplicate_payment_returned` 10.00 → 8.00 (baseline pick min(75.00, 10.00) less the 2.00 refunded against the latest payment), still ≠ 17.98. Revision-6/7 hypotheticals A, B, H1 still recompute to the rule. Mechanical checks pass.

### sweep (revision 8)

**N16 — SOURCE-POLICY RED (charter level, no task consequence): the draft's duplicate-refund gate covers a refund its declared resolver and condition do not.** Sentence: "until the region has made the duplicate refund owed on it". Two policies settle duplicate refunds on an applied/active account: the general one (`refund_duplicate_payment_360f0d4a`) and, for the first installment of an enrollment that took effect in the current plan year, `prime_ext_first_installment_duplicate_refund` (`refund_first_installment_duplicate_7d2e91c4`). The declared edge names only the general policy (`problem`, `resolved_by`), and its condition reads "the duplicate refund the duplicate-refund rule figures". Demonstrated on task 1's world (new enrollment `de31d535`, recurring card on file, first installment `2489efda` paid 20.00 + 70.00), if a draft on file were asked for: the general rule figures 0 (it refuses that first installment); the first-installment rule figures 24.98. Reading (a), the general rule and the declared condition: nothing awaited, draft 7.53. Reading (b), the sentence: the refund owed on the account is 24.98, so it is made first, draft 32.51 (`r8_hyp.py`). Two defensible answers in the same situation. **Auditor disclosure:** the same gap existed from revision 5, when the first-installment policy was introduced, under the earlier wording "until the region has refunded the duplicate payment found on it"; revisions 5-7 missed it.

## closing_checklist (revision 8)

(written after the round-8 task files are read; see below)

Written after reading the round-8 task files; the revision-8 charter section is unchanged since 06:14:36Z. Artifacts byte-unchanged during the audit.

| item | status |
| --- | --- |
| revision_8 appended; older revisions untouched | yes |
| round-7 RED N15 closed (single reading of the draft gate; refunds stable once made; plan-year split rule = compute) | yes |
| scored values unchanged; one factor baseline 10.00 → 8.00, still bearing weight; task files match | yes |
| task-level relationships | PASS for both tasks |
| charter self-consistent | **no** — N16 (draft's duplicate-refund gate vs the first-installment policy; two answers 7.53 / 32.51 on task 1's records for a draft; missed in revisions 5-7) |
| gates | coordinator snapshot cited (all green; scenario VALID); not re-run by the auditor |

**Task level: PASS for both tasks. Charter level: one SOURCE-POLICY RED open (N16).** Open observations: N7, O-r5a, O-r7b, O-r8a, single-Select reading.

## revision_9

### charter_global_frozen (revision 9)

- Written before the round-9 `tasks/*.json` (mtime 2026-10-12 06:39) and the difficulty `worklog.md` were opened.
- Re-hashed, equal to the brief: `prime.extended.yaml` `cc9db2705bcd6c1b2f1b4346008c7e9065e4bc0cd032d7feb8fe87e0938b75ce` (changed; diffed against the kept revision-8 copy; copy at `/tmp/erl55_audit_prime/prime.extended.r9.yaml`), `task_tools.py` unchanged, views 0 and 1 unchanged since revision 5. Base section byte-identical.
- contamination_disclosure: as in revisions 6-8 (recomputation on unchanged worlds).

### delta and verification (revision 9)

Changed: one scope sentence per policy (rule) and a matching guard returning 0 (compute) — catch-up ("no catch-up is charged on an enrollment that took effect in the current plan year"), one-time payment ("settles no payment toward an enrollment that took effect in the current plan year"), draft ("draws nothing on an enrollment that took effect in the current plan year"), supplement ("no supplement is charged on an enrollment that took effect before the current plan year"), initial payment ("settles nothing toward an enrollment that took effect before the current plan year"); plus `dr_late_amt` / `rf_late_amt` defaulting to 0 where no payment stands (the rules' "smaller of the latest payment and the earlier payments together" is then nothing — consistent). Each guard tests the enrollment's effective month against January of the current plan year, as the sentence says. Unused credit and the two duplicate policies keep their revision-8 scopes. Mechanical checks pass.

Single-writer re-check of every edge under the split: draft (prior-year enrollments only) <- catch-up — the only charge writer for a prior-year enrollment (the supplement now refuses it); draft <- duplicate refund — the general policy (the first-installment policy refunds nothing on a prior-year enrollment); draft <- current installment paid in full — the one-time payment (the initial payment refuses prior-year enrollments); initial payment (current-year only) <- supplement, <- first-installment duplicate refund (the general policy refuses a current-year first installment), <- unused credit (sole credit writer). Every edge has one possible writer.

**N16** — re-running revision 8's demonstration (`r8_hyp.py`) on task 1's records: a draft on the new current-year enrollment now draws 0.00 whether or not the 24.98 first-installment refund is made — one answer. **N16 closed.**

Recomputation on the unchanged worlds: task 0 113.54 / 17.98 / 45.02 / 65.02; task 1 32.51 / 24.98 / 16.01 / 48.52; factor baselines and load-bearing figures equal to revision 8. Hypotheticals A, B, H2, H2' recompute to their rules; H1 (revision 7, built by moving task 0's effective date to 2026-04-15) now falls under the catch-up's current-year exclusion and gives 0.00, which is what the new rule states.

### sweep (revision 9)

No rule/compute disagreement, two-reading prerequisite or ladder defect found. Observations:
- **O-r9a** — every enrollment that took effect in the current plan year, including every open-season election effective January 1, has no one-time payment and no draft on file for any installment after its first until the plan year turns; only the initial payment (first installment) applies. A customer asking to pay such a later installment has no policy to settle it. Stated in the rules; outside both tasks.
- **O-r9b** — the reworker's flagged trade-off: a current-year enrollment disenrolled for nonpayment and reinstated within the same plan year gets no catch-up; its restored months stay unbilled (same family as N7; no base sentence requires every restored month to be billed).
- The catch-up and credit computes still fail on accounts outside their own scope (e.g. no reinstatement review / no Select enrollment); the rules exclude those accounts, so this is a robustness observation.
- O-r8a (the April duplicate in H2/H2' never chosen) unchanged.

### findings (revision 9)

Closed: **N16**. No new RED. Open observations: N7, O-r5a, O-r7b, O-r8a, O-r9a, O-r9b, single-Select reading, out-of-scope compute failures.

## closing_checklist (revision 9)

(written after the round-9 task files are read; see below)

Written after reading the round-9 task files; the revision-9 charter section is unchanged since it was written. Artifacts byte-unchanged during the audit.

| item | status |
| --- | --- |
| revision_9 appended; older revisions untouched | yes |
| round-8 RED N16 closed (one answer for a draft on a current-year enrollment; every edge has one possible writer) | yes |
| no scored value or factor sensitivity moved; task files match | yes |
| task-level relationships | PASS for both tasks |
| charter self-consistent (rule = compute, overrides declared, prerequisite sentences single-reading) | yes — no open SOURCE-POLICY RED |
| gates | coordinator snapshot cited (all green; scenario VALID); not re-run by the auditor |

**All four relationships pass for both tasks and no charter-level RED remains open: the difficulty passes the source-layer audit as of revision 9.** Open observations (not grounds for rework under this skill): N7, O-r5a, O-r7b, O-r8a, O-r9a, O-r9b, the single-Select reading, out-of-scope compute failures.
