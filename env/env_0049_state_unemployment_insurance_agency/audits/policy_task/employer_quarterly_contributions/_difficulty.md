# Policy-task audit — employer_quarterly_contributions / charter-global

## charter_global_frozen

- Scenario: `env/env_0049_state_unemployment_insurance_agency`; difficulty `employer_quarterly_contributions`; category `taxacct`; M=2.
- Frozen inputs (sha256, re-computed by the auditor and equal to the coordinator's brief):
  - `tasks/employer_quarterly_contributions/taxacct.extended.yaml` b1ca8ec7335fb5aaf0f9d03e0d64125136b6e1df7d548eaf745bf6402b263306
  - `tasks/employer_quarterly_contributions/task_tools.py` a73a267697174c0b575335a874d83ed13e777120c950a2f70c5498b2c8d2e18c
- Freeze time: 2026-10-09T04:15Z (written before any task's GT was revealed). Auditor: erl-task-policy-audit subagent (independent of the instantiator).
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/taxacct.yaml` (base copy diffed: lines 1-1171 of the extended file are byte-identical to the product charter; the only difference is one trailing blank line), `blueprint/products/appeal.yaml` and `charge.yaml` (only the variant parameters the cross-category reads touch), the extended charter, `task_tools.py`. The expression semantics of `SUM/COUNT/LATEST/CFIELD/MONTHS/DAYS/RND` were read from the evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (lines 215-390; tooling, contains no task content) — disclosed because it is outside the brief's listed read domain.
- Masked and not read: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`; `tasks/employer_quarterly_contributions/worklog.md`; the scenario `worklog.md`; any instantiator transcript; any sibling difficulty or other scenario.
- Nothing in this section is derived from a revealed GT.

Gate snapshot (from the brief, cited, not re-run): check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cache_diff, check_cross_fire all rc=0; check_traceability deferred to render; validate_scenario tasks_ok 8/8 with only pre-render "required document not found" errors. Masked-view hashes supplied (task_0.blind.json b90b97b0..., task_1.blind.json fe52478a...) and re-verified. Entry conditions: complete.

### policy_conflict_scan

The charter has 4 extended policies:

| id | trigger | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| taxacct_ext_estimated_assessment | state_due | book_estimated_assessment_54fbfb5a (agent) | assessment_amount | [] |
| taxacct_ext_credit_refund_request | on_request | request_credit_refund_f44db5b5 (user) | requested_amount | <- estimated_assessment (value_input, state) |
| taxacct_ext_late_report_penalty | state_due | assess_late_report_penalty_9b2fdf0c (agent) | penalty_amount | [] |
| taxacct_ext_penalty_relief_request | on_request | request_penalty_relief_44d7156f (user) | requested_amount | <- late_report_penalty (value_input, state) |

- Subjects: estimated -> taxacct_contribution_assessed (estimate basis only); refund -> taxacct_refund_issued; late penalty -> taxacct_penalty_assessed; relief -> taxacct_credit_adjusted. No two extended policies share a subject event or a target tool.
- Overlap estimated <-> late penalty: the late penalty's estimate charge reads estimated assessments already booked for the late report's quarter (backward-looking history), and the estimated policy acts only on still-unfiled quarters, so the two never act on the same quarter at the same moment; no conflicting conclusion.
- Overlap refund <-> relief: both are employer requests lodged on `employer_account_requests` with different `request_type`; the refund reads the balance due, the relief reads paid penalties; no shared quantity.
- Trigger/time anchors: estimated assessment trigger "still unfiled the class's estimated assessment days after its due date" (i.e. from day 60) vs the refund's prerequisite sentence "still unfiled more than the class's estimated assessment days after its due date" (from day 61). They differ only on day 60 exactly; recorded as observation O-1 below.
- Cross-category read boundaries: refund reads the employer's own `appeals` row (determination_type contribution_rate: decision_outcome, filed_date, decision_mailed_date), relief reads its own `charge_positions` (response_timeliness, response_date); both are declared in `cross_category` and `inputs.cross_category`; neither writes another category.
- Scopes: the `prerequisite` graph partitions the 4 policies into exactly two trees {estimated -> refund} and {late penalty -> relief}. With M=2 and pairwise-disjoint scopes required, the only complete partition is one tree per task. Whether the tasks' declared `charter_scope` matches is checked after reveal (closing_checklist).

### rule_compute_equivalence

Swept every compute binding against `compute_basis` and the rule, and every rule sentence back to compute.

- taxacct_ext_estimated_assessment: every binding has a verbatim basis; windows `within_months` = MONTHS(date, booking day) in [0, N) matches "counted in whole months back from the day the estimate is booked"; tier order and thresholds (1.2; count < 4; >=2/==1/0 estimates; >=2/==1/0 penalties; >=1.25 / >=1.1) match; result order and single rounding match. Invented basis: `recent_average ... else 0` (zero reports) has no rule sentence (O-2).
- taxacct_ext_credit_refund_request: all bindings carry verbatim bases; result order (sum, cushion on the sum, less hold, floor 0, times estimate factor, one rounding; allowance rounded separately) matches. `appeal_outcome` is `CFIELD('appeal', ..., determination_type='contribution_rate')`, which returns the first matching appeal row; the rule says "the employer's contribution rate appeal" (singular, undefined when there are several). `latest_report_contributions` = latest `original_report` assessment entry by entry date, while the rule says "the contributions assessed from the most recently filed original report"; on an account whose latest report replaced an estimate the original_report entry is only the top-up (O-3).
- taxacct_ext_late_report_penalty: bindings and rule match (lateness DAYS(due, filed); share tiers >90 / >30 / else; multiplier before the limit; size cap by peak count; paper charge and estimate charge after the limit; one rounding). The rule rounds twice in words ("... limited by the class's late report penalty maximum, and rounded to the cent" and "rounded to the cent once at the end"); compute rounds once (O-4). `inputs.history` declares `within_months: 34` for the penalty count, a world-specific number (the whole-liability window of one account), not a charter constant (O-5).
- taxacct_ext_penalty_relief_request: bindings match except the cooperation read. Rule: "a notice answered late with the answer received no more than the recent cooperation days before the request gives the recent cooperation share, a notice answered late with the answer received more than the recent cooperation days but no more than the older cooperation days before the request gives the older cooperation share, and no late answer within the older cooperation days gives a cooperation share of one." Compute: `late_answer_date: CFIELD('charge', 'response_date', response_timeliness='late')` — the first charge position in storage order whose timeliness is exactly `late`. Two divergences: (a) with several late answers the compute reads an arbitrary one while the rule's tiers both hold; (b) a position with `response_timeliness = late_good_cause` is "a notice answered late" in the rule's words but is never read by compute. -> Finding F-2 (SOURCE-POLICY RED, general domain). `quarter_assessed/quarter_paid` ignore credits (`taxacct_credit_adjusted`) when deciding "not yet fully paid" (O-6).

### action_binding_and_uuids

- `(target_tool, computes)` pairs are four distinct tools, each claimed by exactly one policy.
- Docstrings: no docstring names another tool or a sequence position. Two contain "until" describing the persistence of a state ("until real figures replace them"; "the credit stays on the account until the refund is issued against the request") — not an ordering between writes of this charter (O-7).
- No tool body refuses, errors or hints when a prerequisite is unresolved: `book_estimated_assessment_54fbfb5a` and `assess_late_report_penalty_9b2fdf0c` create a ledger row and add the amount to `balance_due`; the two user tools create an `employer_account_requests` row with status `received`. Nothing reads another policy's state. (Note: `assess_late_report_penalty_9b2fdf0c` does not consult the once-per-quarter dedup; not a prerequisite judgment.)
- uuid8s: 54fbfb5a, f44db5b5, 9b2fdf0c, 44d7156f — no shared prefix, no sequence, no adjacent values, none reused within this module; `share_tools.py` carries no uuid suffixes. Uniqueness against sibling difficulties' modules was not checked (read isolation).

### prerequisite_graph

- `prerequisite` present on all four policies (two `[]`).
- Edges: refund -> estimated_assessment; relief -> late_report_penalty. Both `problem` ids are extended policies of this file, neither is self, the graph is acyclic (two disjoint chains of length 1).
- `policy_source` verbatim in the blocked policy's own rule: refund — "The refundable amount is worked out only after the ledger carries an estimated assessment for every quarter whose report is still unfiled more than the class's estimated assessment days after its due date." (present verbatim); relief — "The relief share is not fixed until the ledger carries a late report penalty for every quarter whose original report was filed after its due date." (present verbatim).
- `form: state`, no `fallback_reason` on either: correct.
- `condition` restates the sentence at the same strength (both "every quarter", same day-count wording).
- `resolved_by` equals the depended-on policy's `target_tool` in both edges; `effect` holds: an estimate raises `balance_due` (lowers `credit_balance`) and adds an `estimated_assessment` entry (counted by `recent_estimates`); a late report penalty entry dated today falls inside `P('penalty_abatement_lookback_quarters') * 3` months (counted by `other_late_penalties`).
- `kind: value_input` and `gate` names a real binding of the blocked compute: `credit_balance` (refund), `other_late_penalties` (relief).
- No authoring-viewpoint phrasing ("in this task", "at the opening") in either `prerequisite` block.

### prerequisite_sentences

Four-point test:

| edge | ordering connective | waited-on state (record-visible) | no tool/id/snake_case | strength = condition |
| --- | --- | --- | --- | --- |
| refund <- estimated | "only after" | ledger carries an estimated assessment for every quarter whose report is still unfiled > estimated assessment days after due | yes | yes |
| relief <- late penalty | "not ... until" | ledger carries a late report penalty for every quarter whose original report was filed after its due date | yes | yes |

- Single write per state: among this difficulty's four task tools only `book_estimated_assessment_54fbfb5a` creates a contribution assessment with basis `estimated_assessment`, and only `assess_late_report_penalty_9b2fdf0c` creates a `late_report` penalty entry. Each hop has exactly one resolving write.
- Derivations (sentence + records + depended-on rule -> action):
  - Refund: the reader lists quarters from the liability start quarter to the last quarter whose due date has passed, finds those with no original report more than 60 days past due, checks the ledger for an `estimated_assessment` entry per such quarter; the rule that books such entries is taxacct_ext_estimated_assessment ("An estimated assessment is booked for a quarter whose quarterly contribution and wage report is still unfiled the class's estimated assessment days after its due date"); one reading.
  - Relief: the reader compares each original report's filed_date with its due_date, checks the ledger for a `late_report` penalty per late quarter; the rule that books them is taxacct_ext_late_report_penalty ("A late report penalty is owed for every quarterly contribution and wage report filed after its due date"); one reading on a world where the unpenalised late report is the latest-filed original. On a world where an older late report is unpenalised, the late-penalty rule computes only "from the original report with the latest filing date on the account", so the hop has no computable resolution (O-8).
- No second wording, tool name or other problem's id in either blocked rule; neither depended-on rule restates the sentence.
- Undeclared cross-problem orders: the relief rule's "The request is lodged by the employer and decided afterwards by the Department's tax review unit" orders the request before a decision that is not a write of this charter; it grounds no edge and creates no alternative terminal state among this charter's writes (observation O-9). The late-penalty estimate charge refers to estimates already booked for a filed report's quarter (history), not to an order between writes. No base sentence grounds an edge.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (conclusions only; consequences are demonstrated in the task files):

- taxacct_ext_estimated_assessment vs taxacct_evt_quarterly_report: s1 (activation), s2 (due date, reference day, e-filing), s3 (status gate), s4 (taxable wages definition), s6 (one original/amended) — followed or not touched. s5 ("contributions of taxable wages times the contribution rate in force for that quarter's rate year, rounded to the cent") — the estimate uses "the contribution rate on the account"; covered by the declared `replaced_by` ("times the contribution rate on the account"). On a quarter whose rate year differs from the account's rate year the two would differ; declared, so not an undeclared override (observation O-10). s7 (estimate = highest of last four reported quarters' taxable wages times the uplift) — declared in `overwrite`. Merged semantics unique.
- taxacct_ext_credit_refund_request vs taxacct_evt_payments: s1, s2 not touched; s3 ("A credit balance is applied to the next quarter due unless the employer requests a refund") followed; s4/s5 (36-month refund limit from "the payment that created the credit") inherited, not weakened; s6 ("issued ... for no more than the credit balance") declared in `overwrite`. The extended amount is below the credit balance whenever any withholding tier applies, which "no more than" permits. Merged semantics unique. Note: the inherited s4 anchors the refund window on "the payment that created the credit"; the extended rule never says which payment that is when the credit arises from a rate-reduction credit adjustment or from several payments; bears on the tool argument `credit_payment_entry_id` (examined per task).
- taxacct_ext_late_report_penalty vs taxacct_evt_penalty_interest: s1 (larger of flat and wage share, capped at maximum) declared in `overwrite`; s2 (once per quarter) followed ("booked once for the report's quarter"); interest, abatement sentences not touched. vs taxacct_evt_quarterly_report: e-filing threshold consistent with the paper charge. No undeclared override found, no anonymous intermediate, no 0/1 multiplier on a base amount, no dropped branch.
- taxacct_ext_penalty_relief_request vs taxacct_evt_penalty_interest: s4 ("abated in full, never in part, when ... prior late reports is zero ...") declared in `overwrite`; s5/s6 (window, counting) inherited and restated; s7 (interest never abated) respected. Merged semantics unique.

### factor_ladders

Effect labels are judged by the rule's own formula: a tier that only selects the number fed into an unchanged expression is a `parameter`.

**taxacct_ext_estimated_assessment** (baseline rule: recent 12-month original-report average x class uplift x account rate; self-sufficient; every sentence in the rule; params recent_report_months, estimated_assessment_wage_uplift)

| factor | label | honest? | tiers | distinct outcomes | fall-through = baseline | multi-source |
| --- | --- | --- | --- | --- | --- | --- |
| estimate_wage_basis_rule | method | yes (latest report vs 24-month average vs 12-month average: different aggregates) | 3 | yes | yes (recent_average) | no: tier 1 is one comparison; tier 2 is a conjunction over wage reports |
| estimate_history_uplift | parameter | yes | 3 | 2.0 / 1.5 / class 1.25 | yes | no |
| late_filing_addon | parameter | yes | 3 | 0.5 / 0.25 / 0 | yes | no |
| workforce_growth_factor | parameter | yes | 3 | 1.1 / 1.05 / 1 | yes | no (one report row) |

Counts: 4 factors; 3 parameter, 1 method; 0 multi-source; 0 cross-difficulty. All tiers stated in the rule and in compute.

**taxacct_ext_credit_refund_request** (baseline rule: credit balance = max(0, -balance due) rounded to the cent; self-sufficient; in the rule; params [])

| factor | label | honest? | tiers | distinct outcomes | fall-through = baseline | multi-source |
| --- | --- | --- | --- | --- | --- | --- |
| appeal_interest_allowance | parameter | yes | 3 | 0.015 / 0.0075 / 0 | yes | conjunctions/disjunction of outcome and filing-to-decision span, all fields of one appeal row (not distinct records) |
| reporting_cushion | parameter | yes | 3 | 0.2 / 0.1 / 0 | yes | no |
| contribution_hold | parameter | yes | 3 | 1.0 / 0.5 / 0 | yes | no |
| estimate_hold | method | **no**: the rule says "times the estimate hold factor"; compute `estimate_hold_factor: 0 ... 0.5 ... 1` multiplies the same expression by a number | 3 | 0 / 0.5 / 1 | yes | no |

Counts after the label test: 4 factors; 4 parameter, **0 method**; 1 cross-difficulty (appeal); multi-source only under a reading that counts fields of one row as distinct records. -> Finding F-1.

**taxacct_ext_late_report_penalty** (baseline rule: larger of flat 50 and 0.1% of total wages, limited by 250, rounded; self-sufficient; in the rule)

| factor | label | honest? | tiers | distinct outcomes | fall-through = baseline | multi-source |
| --- | --- | --- | --- | --- | --- | --- |
| lateness_wage_share | parameter | yes | 3 | 0.003 / 0.002 / 0.001 | yes | no |
| repeat_lookback_length | method | borderline: two tiers are fixed window lengths (12, 24); the third ("whole liability") counts the whole account history; all three feed one COUNT (O-11) | 3 | 12 / months+1 / 24 | yes (24) | no |
| repeat_multiplier | method | **no**: "is multiplied by the two-penalty repeat multiplier ... one-penalty repeat multiplier ... not multiplied"; compute 2.0 / 1.5 / 1 in `wage_share_amount * repeat_multiplier` | 3 | 2.0 / 1.5 / 1 | yes | no |
| employer_size_cap | parameter | yes | 3 | 1000 / 500 / 250 | yes | no |
| paper_filing_charge | parameter | yes | 3 | 200 / 100 / 0 | yes | no (one report row) |
| estimate_charge | parameter | yes | 3 | 150 / 75 / 0 | yes | yes: estimate ledger entry for the quarter AND filing date of the report |

Counts after the label test: 6 factors; 5 parameter (repeat_multiplier relabelled), 1 method (repeat_lookback_length, borderline); 1 multi-source; 0 cross-difficulty. -> Finding F-1 (mislabel).

**taxacct_ext_penalty_relief_request** (baseline rule: "The relief requested is the penalty paid for that quarter, in full, rounded to the cent."; self-sufficient; in the rule)

| factor | label | honest? | tiers | distinct outcomes | fall-through = baseline | multi-source |
| --- | --- | --- | --- | --- | --- | --- |
| late_penalty_history_share | parameter | yes | 3 | 0.5 / 0.75 / 1 | yes | no |
| estimated_assessment_share | parameter | yes | 3 | 0.7 / 0.85 / 1 | yes | no |
| quarter_payment_share | parameter | yes | 3 | 0.8 / 0.9 / 1 | yes | tier 2 yes (ledger payments and report due date); tier 1 is one comparison |
| claim_notice_cooperation_share | parameter | yes | 3 | 0.85 / 0.95 / 1 | yes | no; tiers overlap as stated when an account has two late answers in different bands (F-2) |
| request_timing_share | parameter | yes, but the condition is unreal (F-3) | 3 | 0.9 / 0.95 / 1 | yes | no |
| paper_filing_relief_factor | method | **no**: "is multiplied by the two-filing paper factor ... one-filing paper factor ... not multiplied"; compute 0.75 / 0.9 / 1 in the product | 3 | 0.75 / 0.9 / 1 | yes | yes: relieved report's channel AND count of other portal-filed reports |

Counts after the label and reality tests: 6 declared; request_timing_share struck as unreal (F-3) -> 5; 5 parameter, **0 method**; 1 multi-source; 1 cross-difficulty (charge). -> Findings F-1, F-3.

Realism notes on the remaining ladders (observations, no red light): the refund's reporting cushion and contribution hold (keeping back part of an employer's credit for a late-penalty or late-interest history) and the relief's cooperation share (a late answer to a benefit notice of claim reducing late-report-penalty relief) are not common practice, but each is a compliance-record consideration an agency could publish; recorded as O-12.

No ladder has two tiers with the same value or method. No tier rests on a field that names the tier outcome (the `response_timeliness` stamp names lateness, a component of the cooperation condition, and agrees with response_date > response_due_date where seeded — examined per task).

### findings

- **F-1 SOURCE-FACTOR RED (charter-global; mislabelled effect / no honest method factor).** Symptom: three factors labelled `method` select a scalar inside an unchanged product. Evidence: refund rule "An estimate hold then scales what is left ... times the estimate hold factor" with compute `estimate_hold_factor: 0 if recent_estimates >= 2 else (K('one_estimate_hold_factor') if recent_estimates == 1 else 1)` and `result: RND(MX(0, ...) * estimate_hold_factor, 2)`; late-penalty rule "multiplied by a repeat multiplier before any limit applies" with compute `repeat_multiplier: K('two_penalty_repeat_multiplier') ... 1` and `MN(penalty_cap, wage_share_amount * repeat_multiplier)`; relief rule "multiplied by the two-filing paper factor ... not multiplied" with compute `paper_relief_factor: K('two_filing_paper_factor') ... 1` inside the product. Consequence: taxacct_ext_credit_refund_request and taxacct_ext_penalty_relief_request each have 0 honest `method` factors (bound: at least 1 per computation); taxacct_ext_late_report_penalty keeps 1 only through the borderline repeat_lookback_length. Affected: `taxacct.extended.yaml` factors `estimate_hold` (refund), `repeat_multiplier` (late penalty), `paper_filing_relief_factor` (relief). Bears on task 0 (refund) and task 1 (relief).
- **F-2 SOURCE-POLICY RED (charter-global; rule/compute non-equivalence and overlapping tiers in the cooperation share).** Quoted above under rule_compute_equivalence. Demonstration on a constructed world: an employer with two charge positions, the first stored with response_timeliness `late` and response_date 500 days before the request, the second `late` with response_date 100 days before. Rule: "a notice answered late with the answer received no more than the recent cooperation days before the request gives the recent cooperation share" holds (second notice) -> 0.85; and the older-share tier also holds (first notice) -> 0.95; the rule picks neither uniquely, while compute reads the first row -> 0.95. Likewise a single position stored `late_good_cause` with response 100 days back: rule "a notice answered late" -> 0.85, compute -> 1. Bears on task 1 only if its world has two late answers or a late_good_cause answer (checked there). Affected: relief `compute.late_answer_date`, rule sentence on the cooperation share, factor `claim_notice_cooperation_share`.
- **F-3 SOURCE-FACTOR RED (charter-global; unreal condition).** request_timing_share grades relief by how many days after the penalty assessment the request is made inside the abatement window ("more than the late timing days give the late timing share, more than the early timing days but no more than the late timing days give the middle timing share"). A UI tax agency treats the abatement request period as a pass/fail deadline — the base charter itself says "a request on the last day is in time" — and does not reduce relief for a timely request made on day 15 rather than day 5; the condition is not one that line of business weighs for the relief amount. Bears on task 1.
- **F-4 SOURCE-FACTOR RED candidate (per task; multi-source).** Under the definition "every tier other than the fall-through a conjunction or a disjunction of two or more conditions over distinct records", the {estimated -> refund} tree has no multi-source factor: estimate_wage_basis_rule tier 1 is a single comparison; appeal_interest_allowance's conditions are fields of one appeal row; all other factors are single counts. The {late penalty -> relief} tree has two (estimate_charge, paper_filing_relief_factor). Demonstrated in task 0's file.
- Observations: O-1 day-60 wording difference between the estimate trigger and the refund prerequisite sentence; O-2 `recent_average` zero-report fallback invented; O-3 refund's appeal read takes the first contribution-rate appeal and the contribution hold reads the latest `original_report` entry rather than the report's full contributions; O-4 double rounding wording in the late-penalty rule; O-5 `inputs.history.within_months: 34` is world-specific; O-6 relief payment share ignores credits; O-7 "until" in two docstrings; O-8 late-penalty computation is defined only for the latest-filed original report, so the relief prerequisite is unresolvable on a world where an older late report lacks a penalty; O-9 "decided afterwards" in the relief rule; O-10 estimate uses the account's rate rather than the quarter's rate-year rate (declared); O-11 repeat_lookback_length method label borderline; O-12 realism of cushion/hold/cooperation ladders.

## closing_checklist

Written after both tasks' derivations were frozen (hash print 2026-10-09T04:17:13Z) and both reveals were compared. Status: **NOT CLOSED** — the factor relationship fails in both tasks, so the difficulty does not pass the source-layer audit.

- Audit files: `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` alongside; no earlier revision exists. Comparison sections: task 0 — policy PASS, chain PASS, factors SOURCE-FACTOR RED, unique solution PASS; task 1 — policy PASS, chain PASS, factors SOURCE-FACTOR RED, unique solution PASS.
- Coverage and scopes: `charter_scope` of task 0 = {taxacct_ext_estimated_assessment, taxacct_ext_credit_refund_request; book_estimated_assessment_54fbfb5a, request_credit_refund_f44db5b5}; task 1 = {taxacct_ext_late_report_penalty, taxacct_ext_penalty_relief_request; assess_late_report_penalty_9b2fdf0c, request_penalty_relief_44d7156f}. Pairwise disjoint, jointly cover all 4 extended policies and all 4 task tools (matches the partition predicted in §policy_conflict_scan). uuid8s independent within this module.
- Problem trees: each task has 1 prerequisite problem, 1 value_input edge (>= max(n-1,1) = 1), an owner=user root write, no cycle; the difficulty-wide graph is two disjoint edges, acyclic.
- Factors: every computation has a self-sufficient baseline giving a definite non-gold number (1562.00, 769.44, 78.46, 212.38) and every declared factor bears weight on its task's world. Fails: F-1 (estimate_hold, repeat_multiplier, paper_filing_relief_factor labelled `method` but scalar; refund and relief computations have 0 honest method factors), F-3 (request_timing_share unreal), F-4 (task 0 has no multi-source factor under the distinct-records reading).
- Charter-global SOURCE-POLICY RED F-2 (cooperation-share read and overlapping tiers on worlds with several or good-cause late answers) stands for the charter's general domain; neither task's world demonstrates it.
- Gates on the final form: the audited artifacts' hashes at close equal those of the brief (extended b1ca8ec7..., task_tools a73a2676..., tasks/0.json 74ee0a0f..., tasks/1.json 2437805a...), so the coordinator's gate snapshot applies to the final form unchanged; the auditor did not re-run gates (per Step 0).

## revision_2

### charter_global_frozen (revision 2)

- Inputs re-hashed by the auditor and equal to the coordinator's round-2 brief: `taxacct.extended.yaml` 9c61c088613b5038512a0acd51791869d10b51523350de89a02b2dbe736b2387 (changed from b1ca8ec7...), `task_tools.py` 9f7c924f17acc620c61dbbea1e23f769ca7b60023ef3c05265b4d8cdbc1e54b1 (changed from a73a2676...). Both shared inputs moved, so every charter-global section is re-derived in full below; round-1 text above is untouched.
- Base copy: lines 1-1171 still byte-identical to `blueprint/products/taxacct.yaml`.
- Read: the four extended policies in full, `task_tools.py` in full. Masked and unread at the time of writing: the round-2 `tasks/0.json` (b32e2c84...) and `tasks/1.json` (dbeb4071...) masked fields, both worklogs. Written 2026-10-10, before either task's round-2 GT was opened; contains nothing derived from a round-2 reveal. The auditor knows the round-1 GT (disclosed in each task file).
- Gate snapshot round 2 (cited): all gates rc=0 (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK); traceability deferred.

### policy_conflict_scan (revision 2)

Same four policies, ids, subjects, target tools, owners and computes as round 1; same two disjoint chains {estimated -> refund}, {late penalty -> relief}. Changes relevant to conflicts:
- Estimate trigger and refund prerequisite now both read "at least the class's estimated assessment days after its due date" (O-1 closed).
- The relief prerequisite now waits only on the latest-filed original report's quarter: "The relief share is not fixed until the ledger carries a late report penalty for the quarter of the original report with the latest filing date, whenever that report was filed after its due date." This matches the late-penalty rule's single computable object ("worked out from the original report with the latest filing date"), closing O-8.
- Cross-category reads now: refund -> `appeals` (decision_outcome, filed_date, decision_mailed_date) through XLATEST by decision_mailed_date; relief -> `charge_positions` (response_timeliness, response_date) through XLATEST by response_date. Declared in `cross_category` and `inputs`. No conflicting conclusion between policies found.

### rule_compute_equivalence (revision 2)

Re-swept mechanically (every `compute_basis` string tested as a whitespace-normalised substring of its rule) and by reading:
- taxacct_ext_estimated_assessment: unchanged logic. New sentence "an average taken over a window in which no original report was filed is zero" grounds `recent_average/longer_average ... else 0` (O-2 closed). Two basis strings are not contiguous substrings: `recent_report_count` (rule now continues ", and an average ..." where the basis ends with a period) and `longer_average` (two rule clauses joined). Both clauses are in the rule; punctuation/joining only (observation R2-O1).
- taxacct_ext_credit_refund_request: appeal interest allowance rewritten — "it is the class's monthly late payment interest rate times those credited-back contributions times a number of interest months, rounded to the cent, and the interest months are counted as the whole months from an interest start date to the day of the request plus one for the month in progress", start date by the most recently decided contribution rate appeal and the credited-back quarter's last contribution payment. Compute matches: `XLATEST(... date_field='decision_mailed_date', determination_type='contribution_rate')`, `credited_quarter` = latest rate_reduced_on_appeal credit, `credited_quarter_payment_date`, `interest_start_date`, `interest_months: MONTHS(start, NOW) + 1 if start != NOW else 0`, `RND(appeal_credit * P('late_payment_interest_rate_monthly') * interest_months, 2)`. Contribution hold base now "the most recent contribution assessment booked from an original report", matching `LATEST(... assessment_basis='original_report')` (O-3 closed for the rule). **Stale quote:** `compute_basis.late_payment_entries` still reads "A contribution hold is taken off as a share of the contributions assessed from the most recently filed original report: ..." — a sentence no longer in the rule (R2-O2; observation: the operative count clause "two or more late payment interest entries ..." is verbatim in the rule and both wordings give the same base on both task worlds). New sentence "The request cites the payment that created the credit: where the credit arose from contributions credited back to a quarter, it is the last contribution payment received for that quarter." states the `credit_payment_entry_id` choice (T0-O1 closed). Edge notes (observations R2-O3): `credited_quarter` takes only the latest credited quarter while `appeal_credit` sums all quarters credited within 12 months — the rule speaks of "the credited-back quarter" in the singular; `interest_start_date` uses NOW as the no-allowance sentinel, so a payment dated the request day would yield 0 months instead of 1.
- taxacct_ext_late_report_penalty: logic unchanged; the result sentence and `replaced_by` now say "with that single rounding to the cent applied to the sum rather than to any part of it" (O-4 closed); `inputs.history` no longer carries `within_months: 34` (O-5 closed).
- taxacct_ext_penalty_relief_request: timing share removed from rule, compute and result ("all five"). Cooperation now "the most recent answer ... recorded as late without good cause (answers recorded as late with good cause do not count)" with `XLATEST('charge', 'charge_positions', 'response_date', date_field='response_date', response_timeliness='late')`: one answer selected, tiers disjoint, good-cause answers excluded in both faces — round-1 F-2 closed. Payment share now "not yet fully covered by the payments and credits applied to them" with `quarter_paid + quarter_credited < quarter_assessed` (O-6 closed). New relief lookback by account standing (delinquent 36 / active with no late interest entry in 12 months 12 / otherwise 8 quarters x 3) — rule and compute agree. "decided afterwards" removed (O-9 closed).

### action_binding_and_uuids (revision 2)

Tool names, signatures, owners, bodies and uuid8s (54fbfb5a, f44db5b5, 9b2fdf0c, 44d7156f) unchanged; only docstrings edited. The two "until" phrasings are gone ("an estimate gives way to the real figures of a filed report"; "the credit remains on the account while the request is open and the refund is issued against it") — O-7 closed. No docstring names another tool or a sequence; no body judges a prerequisite.

### prerequisite_graph and prerequisite_sentences (revision 2)

- Edges unchanged in endpoints, kind (value_input), gate (credit_balance; other_late_penalties), form (state), resolved_by. Both `policy_source` strings verbatim in their own rules (mechanical check: True, True); `condition` restates each at the same strength (refund "at least"; relief "When the original report with the latest filing date ... was filed after its due date, ... carries a late report penalty entry for that report's quarter").
- Four-point test: refund "only after" + ledger state + no tool/id + same strength — pass. Relief "not ... until" + ledger state for one named quarter + no tool/id + same strength — pass. Single resolving write per state: unchanged (only `book_estimated_assessment_54fbfb5a` writes estimate-basis assessments; only `assess_late_report_penalty_9b2fdf0c` writes late_report penalties). Relief derivation now always has a computable hop (the quarter named by the sentence is the one the late-penalty rule works out). No undeclared cross-problem order remains.

### override_declarations (revision 2)

Same `overwrite` blocks; `replaced_by` of the late penalty reworded (rounding) — still names the superseded base sentence. Sentence-by-sentence conclusions of round 1 stand for all four policies. New refund content (interest at the class's monthly late payment interest rate) does not touch any base payments sentence: base taxacct_evt_penalty_interest governs interest charged to the employer, not an allowance credited to it; no undeclared override.

### factor_ladders (revision 2)

| policy | factor | label | honest? | multi-source | cross-difficulty |
| --- | --- | --- | --- | --- | --- |
| estimated | estimate_wage_basis_rule | method | yes | no | – |
| estimated | estimate_history_uplift / late_filing_addon / workforce_growth_factor | parameter | yes | no | – |
| refund | appeal_interest_allowance | method | **accepted**: tiers choose the accrual start from different records (the credited quarter's last contribution payment vs the appeal's filing date) or no accrual; not a constant substituted into one formula | yes: appeal outcome (appeals row) AND payment date vs filing date (ledger row vs appeals row) | appeal |
| refund | reporting_cushion / contribution_hold / estimate_hold | parameter | yes (estimate_hold relabelled from method — F-1 closed for it) | no | – |
| late penalty | lateness_wage_share / repeat_multiplier / employer_size_cap / paper_filing_charge / estimate_charge | parameter | yes (repeat_multiplier relabelled — F-1 closed for it) | estimate_charge yes | – |
| late penalty | repeat_lookback_length | method | borderline, kept (O-11): its whole-liability tier derives the window from registration rather than a constant | no | – |
| relief | late_penalty_history_share / estimated_assessment_share / quarter_payment_share / claim_notice_cooperation_share / paper_filing_relief_factor | parameter | yes (paper factor relabelled) | paper_filing_relief_factor yes; quarter_payment_share tier 2 only | charge |
| relief | relief_lookback_length (new) | method | **no**: its three tiers are three named constants — `K('delinquent_lookback_months')` 36, `K('clean_record_lookback_months')` 12, `P('penalty_abatement_lookback_quarters') * 3` 24 — substituted into the same `COUNT(..., within_months=relief_lookback_months, ...)`; unlike repeat_lookback_length no tier derives its window from the account's own dates | no | – |

Counts: estimated 4 (3p/1m); refund 4 (3p/1m); late penalty 6 (5p/1m borderline); relief 6 declared, honest 6p/**0m**. Every ladder has 3 pairwise-disjoint tiers with distinct outcomes, every fall-through equals its baseline, every baseline rule is verbatim in its rule (mechanical check True x4) and self-sufficient. Realism: the struck timing share is gone; the new appeal allowance (interest at the late-payment rate from the later of payment and appeal filing) and the new relief lookback by account standing are treatments an agency could publish. O-10, O-11, O-12 kept (author's reasons not read — worklog off-limits; the auditor's own round-1 assessment stands: observations).

### findings (revision 2) — status of every round-1 item

| item | round-1 class | round-2 status | evidence |
| --- | --- | --- | --- |
| F-1 (mislabelled methods) | SOURCE-FACTOR RED | **partly closed**: estimate_hold, repeat_multiplier, paper_filing_relief_factor relabelled `parameter`; refund gains an honest method (appeal_interest_allowance). **Not closed for the relief computation**: its new method factor relief_lookback_length is again a constant substituted into one formula (R2-F1) | factor_ladders above |
| F-2 (cooperation read / overlap) | SOURCE-POLICY RED | closed | XLATEST most-recent, good-cause excluded in rule and compute |
| F-3 (timing share unreal) | SOURCE-FACTOR RED | closed | factor, rule sentence, compute binding and result term removed |
| F-4 (no multi-source in the estimate/refund tree) | SOURCE-FACTOR RED (plausible) | closed | appeal_interest_allowance tiers combine an appeals-row condition with a ledger-vs-appeal date comparison |
| O-1 .. O-9 | observations | closed (O-1, O-2, O-3 rule, O-4, O-5, O-6, O-7, O-8, O-9) | sections above |
| O-10, O-11, O-12 | observations | kept | – |

New charter-global items:
- **R2-F1 SOURCE-FACTOR RED (mislabelled effect; relief computation has no honest method factor).** Rule: "The relief lookback is counted in whole months back from the day of the request by the entry dates of the penalties, and its length follows the account's standing: an account in delinquent status looks back over the delinquent lookback months, an account in active status with no late payment interest entry booked within the payment record months looks back over the clean record lookback months, and any other account looks back over the class's penalty abatement lookback quarters, counted as three months each." Compute: `relief_lookback_months: K('delinquent_lookback_months') if F('status') == 'delinquent' else (K('clean_record_lookback_months') if (...) else P('penalty_abatement_lookback_quarters') * 3)` feeding `COUNT(..., within_months=relief_lookback_months, ...)`. Each tier selects a number (36 / 12 / 24) for one window in one formula — the skill's "a different number into the same formula (a rate, a fee, a threshold)". Consequence: taxacct_ext_penalty_relief_request has 0 honest method factors (bound >= 1). Bears on task 1.
- R2-O1 basis punctuation/joining (estimated); R2-O2 stale `compute_basis.late_payment_entries` quote (refund); R2-O3 singular credited quarter and NOW sentinel (refund).

### closing_checklist (revision 2)

Written after both revision-2 derivations were frozen (hash print 2026-10-10T13:42:23Z) and both round-2 reveals were compared. Status: **NOT CLOSED** — task 1 still fails the factor relationship.

- Files: `0.md`, `1.md` each carry an appended `## revision_2` (frozen derivation, comparison, findings); round-1 text untouched in all three files.
- Task 0: PASS on all four relationships (estimate 2307.06; refund 325.00 citing 33efc05b). Task 1: policy PASS, chain PASS, unique solution PASS, factors SOURCE-FACTOR RED (R2-F1).
- Scopes: `charter_scope` unchanged — task 0 {estimated, refund; 54fbfb5a, f44db5b5}, task 1 {late penalty, relief; 9b2fdf0c, 44d7156f}; disjoint and jointly complete; uuid8s unchanged and independent.
- Trees: 1 prerequisite problem each, 1 value_input edge each, owner=user root in each, acyclic across the difficulty.
- Factors: all 20 declared factors bear weight on their worlds; baselines self-sufficient and non-gold (1562.00, 769.44, 78.46, 212.38); multi-source and cross-difficulty present in both tasks; method bound met in the estimate, refund and (borderline) late-penalty computations, failed in the relief computation.
- Round-1 RED status: F-1 partly closed (relief part open as R2-F1); F-2, F-3, F-4, T0-F1, T0-F2, T1-F2, T1-F3 closed; T1-F1 not closed. Round-1 observations O-1..O-9 and T0-O1 closed; O-10, O-11, O-12 kept. New observations R2-O1 (basis punctuation), R2-O2 (stale `compute_basis.late_payment_entries` quote), R2-O3 (singular credited quarter; NOW sentinel) — none bears on either world. No regression found.
- Gates: artifact hashes at close equal the round-2 brief (extended 9c61c088..., tools 9f7c924f..., tasks/0.json b32e2c84..., tasks/1.json dbeb4071...); the coordinator's round-2 gate snapshot applies; not re-run by the auditor.

## revision_3

### charter_global_frozen (revision 3)

- Inputs re-hashed and equal to the round-3 brief: `taxacct.extended.yaml` c3401e7491412b039f3134ee476145e04ad3f18b02fc089d1c76edb7f46dcc98 (changed from 9c61c088...), `task_tools.py` 9f7c924f... (unchanged since round 2). Base copy lines 1-1171 still byte-identical to the product charter.
- Because the charter moved, every charter-global section below is re-derived against it; the tool-module conclusions of revision 2 (§action_binding_and_uuids (revision 2)) carry forward by reference on the unchanged hash 9f7c924f....
- Written before any round-3 GT was opened (round-3 `tasks/0.json` 30375632..., `tasks/1.json` c71adf9d...); the auditor knows the round-1 and round-2 GT (disclosed per task). Worklogs not read.
- Gate snapshot round 3 (cited): all gates rc=0; traceability deferred.

### rule_compute_equivalence (revision 3)

Mechanical re-check (each `compute_basis` string as a whitespace-normalised substring of its rule): 0 non-verbatim entries in all four policies (round 2 had 3). Each `prerequisite.policy_source` verbatim in its own rule (True, True); each baseline rule's sentences are in the rule.
- Estimated assessment: `recent_report_count` basis now quotes the full sentence including ", and an average taken over a window in which no original report was filed is zero."; `longer_average` now quotes one contiguous clause — R2-O1 closed. Logic unchanged.
- Refund: rule now "An appeal interest allowance is added to the credit balance on the contributions credited back within the appeal credit months to the quarter most recently credited back because a contribution rate was reduced on appeal, the credited-back quarter: ..."; compute `credited_quarter` (latest rate_reduced_on_appeal credit) is now computed first and `appeal_credit` is filtered `quarter=credited_quarter`, so the amount base and the start date speak of the same single quarter; the no-allowance sentinel is now `None` (`interest_months: MONTHS(interest_start_date, NOW) + 1 if interest_start_date != None else 0`), so a payment dated the request day yields 1 month — R2-O3 closed. `compute_basis.late_payment_entries` now quotes the current contribution-hold sentence — R2-O2 closed.
- Late penalty: unchanged from revision 2.
- Relief: the relief lookback sentence is rewritten (below); compute adds `relief_liability_months: MONTHS(F('registered_date'), NOW)`, `last_interest_date: LATEST(... event_type='taxacct_interest_assessed')`, `relief_lookback_months: relief_liability_months + 1 if status == 'delinquent' else ((MONTHS(last_interest_date, NOW) + 1 if last_interest_date != None else relief_liability_months + 1) if (status == 'active' and late_interest_entries == 0) else P('penalty_abatement_lookback_quarters') * 3)`. Each branch matches a rule clause: "an account in delinquent status looks back over its whole liability since registration, that is one month more than its whole months of liability; an account in active status with no late payment interest entry booked within the payment record months looks back only to its most recent late payment interest entry, that is one month more than the whole months since that entry's date, or over its whole liability since registration when it has never been charged late payment interest; and any other account looks back over the class's penalty abatement lookback quarters, counted as three months each." The params `delinquent_lookback_months` and `clean_record_lookback_months` are removed. No empty promise, no invented basis found.

### policy_conflict_scan, prerequisite_graph, prerequisite_sentences, override_declarations (revision 3)

No change to policy ids, subjects, target tools, `overwrite` blocks, prerequisite edges (endpoints, kind, gate, form, policy_source, condition, resolved_by) or cross-category declarations relative to revision 2; the revision-2 conclusions of those sections stand, re-confirmed against hash c3401e74.... The refund's appeal read is still the most recently decided contribution-rate appeal; the relief's charge read is still the most recent answer recorded `late`.

### factor_ladders (revision 3)

- Estimated (4: 3p/1m), refund (4: 3p/1m, appeal_interest_allowance method, multi-source, cross-difficulty appeal) and late penalty (6: 5p/1m borderline) as in revision 2.
- Relief `relief_lookback_length` (method): tier 1 (delinquent) — the window is derived from the account's registration date (count every other penalty since registration); tier 2 (active, no late interest in 12 months) — the window runs back to the date of the account's most recent late-payment interest entry (or registration if none); tier 3 — the fixed 8 quarters x 3 = 24 months (fall-through = baseline). Two of three tiers now set the counting start from a record of the account rather than picking a constant, which is the same property on which the auditor accepted `repeat_lookback_length` as a method (O-11, borderline). Under that standard the label is accepted: the relief computation now has 6 factors, 5 parameter + 1 method. Tiers are pairwise disjoint (status delinquent / active-and-clean / anything else), distinct in outcome, stated in the rule and in compute. Realism: counting a delinquent account's whole penalty history, and giving an account clean for a year a fresh start from its last lapse, are compliance-record conventions an agency could publish.
- Counts: every computation now has 4-6 factors, >= 2 parameter and >= 1 method (two of the four methods — repeat_lookback_length and relief_lookback_length — are borderline window conventions; recorded as O-11, now covering both).

### findings (revision 3) — status of the round-2 items

| item | round-2 class | round-3 status | evidence |
| --- | --- | --- | --- |
| R2-F1 / T1-R2-F1 (relief has no honest method) | SOURCE-FACTOR RED | closed (under the same standard as repeat_lookback_length) | factor_ladders (revision 3) |
| R2-O1 basis punctuation | observation | closed | 0 non-verbatim basis strings |
| R2-O2 stale contribution-hold quote | observation | closed | basis now quotes the current sentence |
| R2-O3 singular credited quarter / NOW sentinel | observation | closed | `appeal_credit` filtered to `credited_quarter`; `None` sentinel |
| O-10, O-11, O-12 | observations | kept (O-11 now covers relief_lookback_length too) | – |

New defects: none found in the charter or the (unchanged) tool module.

### closing_checklist (revision 3)

Written after both revision-3 derivations were frozen (hash print 2026-10-10T18:36:41Z) and both round-3 reveals compared (18:36:47Z). Status: **CLOSED — the difficulty passes the source-layer audit.**

- Files: `0.md`, `1.md` each carry `## revision_3` (frozen derivation, comparison); `_difficulty.md` carries `## revision_3`; revisions 1 and 2 untouched in all three files.
- Task 0: policy PASS, chain PASS, factors PASS, unique solution PASS (2307.06; 325.00 citing 33efc05b). Task 1: policy PASS, chain PASS, factors PASS, unique solution PASS (645.76; 51.79 for 2026-Q3 citing 5d4a5120).
- Coverage and scopes: task 0 {taxacct_ext_estimated_assessment, taxacct_ext_credit_refund_request; book_estimated_assessment_54fbfb5a, request_credit_refund_f44db5b5}; task 1 {taxacct_ext_late_report_penalty, taxacct_ext_penalty_relief_request; assess_late_report_penalty_9b2fdf0c, request_penalty_relief_44d7156f}; pairwise disjoint, jointly complete; uuid8s independent and frozen.
- Problem trees: one prerequisite problem each, one value_input edge each (>= max(n-1,1)), owner=user root in each, each prerequisite unmet at the opening and load-bearing (2726.36 vs 325.00; 77.68 vs 51.79); the difficulty's prerequisite graph is two disjoint edges, acyclic.
- Factors: four computations with 4 / 4 / 6 / 6 factors, each >= 2 parameter and >= 1 method; every task has a multi-source factor (task 0 appeal_interest_allowance; task 1 estimate_charge, paper_filing_relief_factor) and a cross-difficulty factor with seeded rows consistent with their charters (appeal; charge); every ladder has 3 disjoint tiers stated in rule and compute; every factor bears weight against an honest baseline; each whole baseline gives a definite non-gold number (1562.00, 769.44, 78.46, 212.38).
- Round history: round-1 REDs F-1, F-2, F-3, F-4, T0-F1, T0-F2, T1-F1, T1-F2, T1-F3 and round-2 RED R2-F1/T1-R2-F1 closed. Observations kept: O-10 (estimate uses the account's rate; declared), O-11 (repeat_lookback_length and relief_lookback_length are window conventions accepted as methods on a borderline standard), O-12 (realism of the refund cushion/hold and relief cooperation share).
- Gates: artifact hashes at close equal the round-3 brief (extended c3401e74..., tools 9f7c924f..., tasks/0.json 30375632..., tasks/1.json c71adf9d...); the coordinator's round-3 gate snapshot (all rc=0; traceability deferred to render) applies to the final form.

## revision_4

### charter_global_frozen (revision 4)

- Shared inputs re-hashed: `taxacct.extended.yaml` c3401e7491412b039f3134ee476145e04ad3f18b02fc089d1c76edb7f46dcc98 and `task_tools.py` 9f7c924f17acc620c61dbbea1e23f769ca7b60023ef3c05265b4d8cdbc1e54b1 — both identical to revision 3. Per the re-audit rule, every charter-global section (policy_conflict_scan, rule_compute_equivalence, action_binding_and_uuids, prerequisite_graph, prerequisite_sentences, override_declarations, factor_ladders, findings) is carried forward by reference from §revision_3 (and the tool section from §revision_2), on the grounds of these two unchanged hashes. Nothing re-derived; no new charter-global finding possible from unchanged inputs.
- Written 2026-10-10 before the round-4 task files (0.json df2c25a1..., 1.json e8f21f8b...) or the policy_kb audit notes were opened.

### closing_checklist (revision 4)

Written after both revision-4 freezes (hash print 2026-10-10T20:19:41Z) and both round-4 comparisons. Status: **CLOSED — the difficulty still passes the source-layer audit.**

- Charter and tool module unchanged (c3401e74..., 9f7c924f...); charter-global conclusions of revisions 2-3 stand by reference.
- Task files changed in proof text only: in both tasks `initial_state`, `frozen_time`, `user_scenario` equal the blind views, and every scored argument, expected value, baseline_result and factor_sensitivity figure equals revision 3.
- KB-audit note (c) (tasks/0.json find_appeals necessity) closed: the new text states the allowance tier as the charter does.
- New observation R4-O1 (task 0): `evaluation_criteria[7].argument_uniqueness_tracing.quarter` still quotes the estimate rule's pre-round-2 wording ("still unfiled the class's estimated assessment days after its due date", glossed "more than ... 60") instead of the current "at least"; no consequence on any scored value (132 days satisfies both). Text fix needed; no red light. Task 1: no stale current assertion.
- Per-task verdicts: task 0 PASS (with R4-O1), task 1 PASS. Observations O-10, O-11, O-12 kept.
- Gates: the coordinator's round-4 snapshot (all rc=0, TRACEABILITY OK) applies to these hashes (tasks/0.json df2c25a1..., tasks/1.json e8f21f8b...).
