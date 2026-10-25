# Policy-task audit — personal_loan_servicing / charter-global

## revision_1

## charter_global_frozen
- freeze time: 2026-10-16 (audit round r1), auditor: erl-task-policy-audit subagent (independent of the instantiator)
- `tasks/personal_loan_servicing/loan.extended.yaml` sha256=2df122f1ea635f76844ded444c927e1902435ad0970351b185685efc53a611e9
- `tasks/personal_loan_servicing/task_tools.py` sha256=34db3cd15207558891889ade20fd778a6694084810359bad753d390386243780
- inputs read: blueprint.yaml (difficulty entry), blueprint/products/{loan,line,builder,hardship,pos}.yaml (only the parts named below), db_schema.json, share_tools.py, the extended charter, task_tools.py, audits/render_source/XF_recipe.md, the gate snapshot, and the DSL primitive semantics in skills/erl-task-instantiate/scripts/check_compute.py (MONTHS/DAYS/LATEST/CFIELD/X* definitions).
- masked / not read: tasks/personal_loan_servicing/tasks/*.json, worklog.md, plan.md; every masked key of the views (charter_scope, computations, db_closure*, design_rationale, evaluation_criteria, prerequisite_closure, required_documents, solvability_contract). Nothing in this section is derived from a revealed GT.
- entry conditions (Step 0): gate snapshot supplied (EXTENDED/TASK TOOL CONTRACT/REPLAY --check/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; TRACEABILITY NOT OK pre-publication, only unlock_*_discoverable_tool:tool_name misses); masked views supplied with hashes, re-hashed and matching (task_0 ec0836f0…, task_1 69f1a936…). Entry conditions met.
- base copy: lines 1–1910 of the extended charter are byte-identical to blueprint/products/loan.yaml (diff shows only the 4-line extended_policies banner).

### policy_conflict_scan
Six extended policies, each claiming one `(target_tool, computes)`:

| policy | tool (owner) | computes | prerequisite |
|---|---|---|---|
| loan_ext_refi_payoff_quote | issue_payoff_quote_88f1b45e (agent) | payoff_amount | [] |
| loan_ext_refi_application | submit_refinance_application_9ec5cb64 (user) | amount_financed | ← refi_payoff_quote (value_input, state) |
| loan_ext_late_fee | assess_late_fee_8eb98004 (agent) | amount | [] |
| loan_ext_returned_fee | assess_returned_payment_fee_e467aa52 (agent) | amount | [] |
| loan_ext_autopay_enroll | enroll_autopay_4dda8507 (user) | current_interest_rate | [] |
| loan_ext_courtesy_waiver | waive_fee_courtesy_87326602 (agent) | amount | ← late_fee, returned_fee, autopay_enroll (all value_input, state) |

- Overlapping subjects: late fee and returned-payment fee share the state fee-schedule map (identical lists in both rules and in base `state_fee_schedule_map`); both read a completed Term Extension Modification with identical 36/60-month cut points; no conflicting conclusion. The courtesy waiver reads the ledger state the late-fee and returned-fee writes leave; neither fee policy reads the other's write or the enrollment (checked by evaluation: each prerequisite's value is unchanged when the other two writes are present — see 1.md problem_chain). The payoff quote's AutoPay day-rate split and the autopay enrollment both follow base `loan_evt_autopay` ("interest for each day accrues at the rate in force that day"); no conflict.
- Time anchors: all six use frozen_time's date as the action date; whole-month counts use MONTHS() (same-day-number convention). See finding PLS-G2(g) on the unstated month-end convention.
- Cross-category read boundaries: line (refi credit, late-fee relief, returned-fee bank-event form), builder (refi credit, AutoPay step), hardship (late/returned-fee modification share, AutoPay rate base), pos (courtesy point). Every read field exists in db_schema; statuses/values read (`matured`, `completed`, `Term Extension Modification`, `paid_off` + `paid_in_full`/`paid_in_full_within_promo`, `line_late_fee_assessed`, `line_payment_returned`, `line_returned_payment_fee_assessed`) are values the owning charters produce.
- Scope partition (from the trees derived independently in 0.md / 1.md, compared with GT only after freezing): task 0 = {refi_payoff_quote, refi_application}; task 1 = {late_fee, returned_fee, autopay_enroll, courtesy_waiver}. Pairwise disjoint and jointly complete over the six extended policies.

### rule_compute_equivalence
Mechanical sweep (scratch script, deleted): every `compute_basis` quote is a verbatim substring of its policy's `rule` (0 misses); every sentence of every `baseline.rule` is in the `rule`; every `replaced_by` is in the `rule`; every `policy_source` is in the blocked rule.
Sentence-by-sentence sweep back:
- loan_ext_refi_payoff_quote: principal/fees/rate/day counts, window ladder (`q_window_days`), day-rate split incl. the stated same-date tie ("enrollment is the later record" ↔ strict `>` on the cancel branch, `>=` on the enroll branch), hold ladder incl. the stated LATEST tie ("first one recorded" ↔ DSL LATEST keeps first max), requote count (`within_months=1`, purpose filter), single rounding of interest then sum. Equivalent. Defect class member PLS-G2(e) (no exclusion of an already-returned additional-principal payment).
- loan_ext_refi_application: payoff (`quote_date=NOW`, purpose refinance), fee percent `MX(0, …)`, sizing forms, remaining installments `MONTHS(next_due, maturity)+1` ("both dates counted"), credits, rounding (cent, then ceiling to whole dollar). The stated month convention ("complete on the same day number of the later month") equals MONTHS(). Equivalent.
- loan_ext_late_fee: unpaid portion, schedule map, fee form (latest return then `>= next_due_date`, equivalent to "latest return dated on or after the due date"), shares, cap at unpaid portion, one rounding. Equivalent, except schedule_c under the fee form (rule names "the schedule's percent", schedule_c has none; compute keeps the flat amount) — observation O-6.
- loan_ext_returned_fee: schedule amount, bank-event form, shares, one rounding. NOT equivalent — PLS-G2(a), PLS-G2(f).
- loan_ext_autopay_enroll: rate base, steps, one rounding to two decimals. Equivalent (tier 2 "equalled" ↔ `>=`, the `>` side being unreachable under the hardship charter, which sets pre-plan rate = current rate ≤ base rate).
- loan_ext_courtesy_waiver: fee selection with tie rule, unpaid part, form, points, share clamp, one rounding. NOT equivalent — PLS-G2(b), PLS-G2(c), PLS-G2(d).
- Rounding placement (XF#6): every rule's rounding sentence matches its RND placement.

### action_binding_and_uuids
- Each `(target_tool, computes)` claimed once; no base policy names a target tool.
- Tool bodies (task_tools.py) perform one ctx.create (+ one ctx.update of fees_balance / AutoPay fields) with the values given; no eligibility check, no refusal, no hint (verified by reading all six bodies).
- Docstrings: no example values, no tool names, no ordering words; observation O-8 on waive_fee_courtesy_87326602's `related_txn_id` text "or by the confirmation that charged the fee".
- uuid8s 88f1b45e, 9ec5cb64, 8eb98004, e467aa52, 4dda8507, 87326602: pairwise distinct, no shared prefix/suffix, no sequence pattern; share_tools.py carries no uuid-suffixed tools. No factor id is a substring of any tool name (XF#10).
- task_tools.py imports nothing but erlbench; no datetime/time/random/uuid/secrets (XF#13); frozen_time format in both views `YYYY-MM-DD HH:MM:SS EDT`.

### prerequisite_graph
Edges: refi_application → refi_payoff_quote (gate r_payoff); courtesy_waiver → late_fee (gate c_fee_amount), → returned_fee (gate c_ret_3m), → autopay_enroll (gate c_last_enroll). Every policy fills `prerequisite`; every `problem` is an extended policy id of this file, never self or base; acyclic (depth 1, two disjoint stars); `form: state` on all four, no `fallback_reason`; every gate is a compute binding of the blocked policy; every `resolved_by` is the depended-on policy's target_tool and its tool body writes exactly the row the condition names (quote row with purpose/quote_date; late-fee line; returned-fee line with related_txn_id; enrollment servicing record with bank_account_id); kind value_input matches the gate binding in each case. No authoring-viewpoint phrasing in any prerequisite field. Condition-vs-sentence strength: see PLS-G3.

### prerequisite_sentences
1. refi_application: "The amount financed on a refinance application is fixed only after the loan being refinanced carries a refinance-purpose payoff quote dated on the application date." — connective "only after"; record-visible state (loan_payoff_quotes.quote_purpose / quote_date); no tool/id/snake_case; scope = condition. One write produces the state: issue_payoff_quote_88f1b45e with quote_purpose refinance (the only quote-writing tool; loan_ext_refi_payoff_quote is the policy whose rule describes "a refinance-purpose payoff quote"). Derivation: sentence → no such quote dated today in the records → the policy whose rule issues refinance-purpose quotes → its write. Single reading. PASS.
2. courtesy_waiver ← late_fee: "A courtesy waiver of a late fee is worked out only after the loan's ledger carries the late fee owed for every installment left unpaid past its grace period." — connective "only after", ledger state, no tool name. Single producing write: assess_late_fee_8eb98004. Scope vs condition: finding PLS-G3.
3. courtesy_waiver ← returned_fee: "A courtesy waiver amount is not fixed until the loan's ledger carries the returned-payment fee owed for every returned payment whose return code bears one." — "not … until", ledger state; single producing write assess_returned_payment_fee_e467aa52; scope = condition ("every … line … whose return code is R01…R20 has a … fee line pointing at it"). PASS (but see PLS-G2(f): the returned-fee policy can only charge the latest return).
4. courtesy_waiver ← autopay_enroll: "Where the loan's AutoPay ended through an automatic cancellation, a courtesy waiver of a late fee is fixed only once the loan's AutoPay record shows a new enrollment on a verified account." — "only once", servicing-record state (+ bank_accounts.verification_status); single producing write enroll_autopay_4dda8507; scope = condition. PASS.
- No rule restates another policy's sentence; depended-on rules are silent about the waiver/application; no rule carries a second wording, tool name or policy id; no extended rule states an ungrounded cross-problem order. Base sentence check: base `loan_evt_returned_payment` "the two fees are independent" states no order; base `loan_evt_refinance` "net proceeds must cover the payoff amount of a refinance-purpose payoff quote good through the expected funding date" is restated in the extended rule and grounds nothing beyond edge 1.

### override_declarations
Sentence-by-sentence over every `base_policy_refs` entry (conclusion per sentence; only departures listed in full):
- loan_ext_refi_payoff_quote vs loan_evt_payoff_quote: good-through, interest, payoff sentences — departed, declared (3 overwrites, self-scoped "for a refinance-purpose quote, and only for such a quote; every other …"). Per diem sentence — not scored (tool has no per-diem argument). Active-only, one-per-date-and-purpose, purpose naming, no penalty, "quote does not change the loan" — followed. vs loan_evt_autopay ("rate in force that day") — followed (day-rate split implements it). vs loan_evt_refinance, loan_evt_payment_application — followed; PLS-G2(e) is a conflict with base loan_evt_returned_payment's reversal sentence on a world where the held payment has already been returned.
- loan_ext_refi_application vs loan_pricing_and_disbursement: origination-fee sentence — departed, declared with self-scope. "The fee is withheld from the loan amount, so net proceeds equal the amount financed minus the fee" — not retired; sizing form 2 says "added on top rather than withheld"; numerically AF − fee = payoff still holds, scored AF unaffected (observation O-5). vs loan_evt_refinance "underwritten, priced and capped like any new loan (… the reduced refinance origination fee …)" — departed, declared. multi_holding, combined_exposure, underwriting — followed.
- loan_ext_late_fee vs loan_evt_late_fee: schedule sentence — departed, declared; the lead-in "applied to the unpaid portion of that installment on the assessment date" is the same base sentence and is covered by the replaced clause; grace, one-per-installment, active-only, never above unpaid portion, no pyramiding, hardship/SCRA exclusions, move-does-not-change-schedule — followed/inherited.
- loan_ext_returned_fee vs loan_evt_returned_payment: amount sentence — departed, declared. "A returned-payment fee is charged once for each returned payment …" — the extended rule adds "the fee is charged against the latest returned payment on the loan" and every factor reads the latest return; for a fee owed on a non-latest return this is an undeclared narrowing (PLS-G2(f)). Monthly cap, code list, schedule_c no-line — followed.
- loan_ext_autopay_enroll vs loan_evt_autopay: rate sentence — departed, declared with self-scope; verified account, active-only, re-enroll at any time, discount resumes on re-enrollment — followed. vs loan_cmb_hardship_and_benefits: "a Term Extension Modification is permanent"; "a plan that sets its own rate replaces the AutoPay-discounted rate while it is active" — followed (rate base reads a completed TEM only).
- loan_ext_courtesy_waiver vs loan_evt_fee_waiver: "may be waived only on one of the bases below, one waiver line per fee, for the part of the fee still unpaid" — departed (amount may be less than the unpaid part), declared. Once-per-fee, courtesy eligibility, request window, basis priority — inherited.
- No undeclared override with a scored consequence in either task world found; no anonymous intermediate, 0/1 multiplier or dropped base branch found.

### factor_ladders
Counts (labels as declared; all ladders 3 tiers incl. fall-through; each `decides` an input binding, never `result`; binding sets disjoint; every tier stated in the rule and implemented in compute; no factor binding reads another factor's binding — XF#1 checked transitively):

| policy | factors (effect) | param / method | multi-source | cross_difficulty |
|---|---|---|---|---|
| refi_payoff_quote | window_anchor_rule (m), day_rate_split (m), uncleared_payment_hold (p), requote_cushion (p) | 2 / 2 | window_anchor_rule, day_rate_split, uncleared_payment_hold | — |
| refi_application | refi_sizing_form (m), remaining_term_reduction (p), payment_record_credit (p), autopay_record_credit (p), flexline_standing_credit (p), credit_builder_credit (p) | 5 / 1 | sizing_form, payment_record, autopay_record, flexline | line, builder |
| late_fee | fee_form_by_return (m), first_late_relief (p), flexline_month_relief (p), modification_relief (p), autopay_history_relief (p) | 4 / 1 | first_late_relief, fee_form_by_return | line, hardship |
| returned_fee | bank_event_form (m), first_return_relief (p), returned_fee_modification_relief (p), return_reason_share (p) | 3 / 1 | bank_event_form, first_return_relief | line, hardship |
| autopay_enroll | modified_rate_base (m), loan_age_step (p), debit_record_step (p), credit_builder_autopay_step (p) | 3 / 1 | modified_rate_base | hardship, builder |
| courtesy_waiver | courtesy_waiver_form (m), autopay_restored_point (p), fee_load_point (p), installment_record_point (p), practicepay_point (p), return_reason_point (p) | 5 / 1 | autopay_restored_point | pos |

Per-factor structural conclusions:
- Baselines: every factor's baseline equals what its policy's `baseline.rule` states for that input, and every fall-through tier equals the baseline (window = validity days; flat current rate; nothing held; no cushion; fee withheld; full grade reduction; zero credits; standard schedule; shares 1; rate base = base rate; no steps; whole unpaid part; zero points). Every `baseline.rule` is self-sufficient (computes a definite number with no factor).
- Method labels: refi_sizing_form (withheld / add-on / no fee — three formula shapes), bank_event_form (size-split / offset / schedule), courtesy_waiver_form (minus a retained amount / times a share / whole), day_rate_split (split accrual vs flat), modified_rate_base (which contract rate the discount comes off — a real rate-of-record choice under the hardship charter), window_anchor_rule (anchor convention of the window: day before next due date / next due date / fixed count — the gate's own definition lists "the anchor the clock starts from"; observation O-1 on its one-day-offset tiers). fee_form_by_return: tier 1 is the same formula with the floor set to 0 and tier 2 the same formula on a different acting base (full scheduled installment instead of unpaid portion) — finding PLS-G1.
- Duplicate-outcome tiers: remaining_term_reduction selects 0 on all three tiers for Grades F and G (refinance_origination_fee_reduction_percent = 0.0) — observation O-2 (neither task world is F/G). Unreachable tiers by grade: refi_sizing_form tier 1 unreachable on F/G (refinance seasoning 12 months), courtesy_waiver_form tier 1 unreachable on C–G (one courtesy waiver per 12 months) — observation O-3.
- Realism (every condition and outcome): see PLS-G1 (return-code-keyed fee amounts) and observations O-3, O-4, O-7. All other conditions are ones a US online personal-loan lender plausibly weighs (AutoPay/rate changes in the accrual period, uncleared ACH funds and recent returns, prior-refinance age, remaining term, on-time and AutoPay history, relationship standing on FlexLine / Credit Builder / PracticePay, completed modification, fee load, reason a payment failed for a discretionary courtesy decision).

### findings

**PLS-G1 — SOURCE-FACTOR RED (realism / unreal ladder; XF#12 class "assessed-fee amount keyed to the NACHA return code of the bounced payment"). Bears on task 1.**
- Symptom: two assessed-fee computations change the fee by the ACH return reason of the bounced debit.
- Members (complete list): (i) loan_ext_late_fee.fee_form_by_return — rule: "when it came back for a closed, missing or invalid account (return code R02, R03 or R04), the schedule's percent of the unpaid portion is charged with no minimum …; when it came back for insufficient or uncollected funds (return code R01 or R09), the schedule's percent is taken of the full scheduled installment amount, with the schedule's minimum and maximum"; (ii) loan_ext_returned_fee.return_reason_share — rule: "a return for a closed, missing or invalid account (return code R02, R03 or R04) gives returned_fee_reason_share_account; a return on a stopped, frozen or non-transaction account (return code R08, R16 or R20) gives returned_fee_reason_share_other". (loan_ext_courtesy_waiver.return_reason_point is NOT a member: a discretionary courtesy decision weighing why the payment failed is something lenders do.)
- Root cause: a contractual late charge and a returned-payment fee are fixed by the note and the state schedule; no US installment lender sets their computation (floor, acting base, or a 0.90/0.95 multiplier) by why the debit bounced. Member (i) additionally lets a tier select the acting base — percent of the full scheduled installment where the base charter and the fall-through apply it to the unpaid portion — i.e. on a partly paid installment an NSF borrower is charged a percentage of money already paid; and its tier 1 is the fall-through formula with the floor set to 0 (a parameter, not a method).
- Demonstrated consequence: task 1 world (latest return R02) — see 1.md factor_weight: fee_form_by_return takes tier 1 (13.7435 vs 15.00 under baseline) and return_reason_share takes 0.90; both move the scored late fee / returned fee and, through the late fee, the waiver amount.
- Affected: loan.extended.yaml loan_ext_late_fee rule (fee-form sentence), factors[fee_form_by_return]; loan_ext_returned_fee rule (return-reason sentence), factors[return_reason_share].

**PLS-G2 — SOURCE-POLICY RED (rule/compute non-equivalence and missing decoy exclusions; XF#8 class). Bears on no task world (both checked); open charter-wide.**
Members (complete list), each with a scratch-world probe (copies of the task worlds; probe script deleted):
- (a) loan_ext_returned_fee.bank_event_form: rule "when a FlexLine payment debited from the same bank account was returned on the same date as the loan's returned payment and the FlexLine charged its own returned-payment fee on that date" is existential over FlexLine returns; compute reads only the latest FlexLine return/fee (`XLATEST`). Probe: task-1 world plus a later FlexLine return (2026-09-15, other account) → rule tier 1 still holds (8.58), compute falls to tier 2 → 5.16. Tier 2's "for a different bank event" is not implemented; no tie rule is stated for same-day FlexLine returns/fees.
- (b) loan_ext_courtesy_waiver.autopay_restored_point: rule "an enrollment dated on or after its latest automatic cancellation (reason bank_account_closed or consecutive_returns)"; compute takes the latest cancellation of any reason and then tests its reason. Probe: auto-cancel 09-08, enroll 09-20, borrower cancel 09-22, enroll 09-24 → rule 0.30 point (waiver 8.09), compute 0.15 (6.74). No tie rule for two cancellations on one date.
- (c) loan_ext_courtesy_waiver.practicepay_point tier 2: rule "a PracticePay plan in active status with an amount past due of 0.00" (existential; pos allows up to 3 open plans); compute `CFIELD` first active plan. Probe: two active plans (one past due, one current) → 7.19 or 7.64 depending only on row order; rule gives 7.64.
- (d) loan_ext_courtesy_waiver.return_reason_point: "the latest returned payment on the loan …" states no same-date tie rule (c_ret_code LATEST); two returns on one date with different codes give two readings.
- (e) loan_ext_refi_payoff_quote.uncleared_payment_hold: "looking only at the latest payment of type additional_principal" has no exclusion of a payment already returned; base loan_evt_returned_payment already re-adds a returned payment's principal ("its principal portion is re-added to principal"). Probe: task-0 world with the 2026-10-16 $400 payment returned 10-19 → 6804.19 (held amount added on top of restored principal) vs 6404.19.
- (f) loan_ext_returned_fee object selection: "the fee is charged against the latest returned payment on the loan" with every factor reading the latest return, against inherited base "A returned-payment fee is charged once for each returned payment whose return code is …". A fee-bearing return that is not the latest (an unfeed older return, or a later R07/R10/R29/CB return) cannot be charged with its own amount/code/bank; the courtesy edge-3 condition ("every … line … has a … fee line") then cannot be brought about by the one write.
- (g) Month-end convention unstated for "whole calendar month(s)" counts in loan_ext_refi_payoff_quote (12-month returns, one-month requotes), loan_ext_late_fee (12/1/2/36/60), loan_ext_returned_fee (12/1/36/60), loan_ext_autopay_enroll (funding→enrollment months, 24-month debits), loan_ext_courtesy_waiver (3/12/24); base `loan_evt_refinance` uses a different convention ("the last day of that month is used"). With a 31st-day anchor and a 28th–30th request date, MONTHS() and the base convention differ by one month. (loan_ext_refi_application states its convention, equal to MONTHS().)
- Neither task world contains the decoy for any member (0.md/1.md record the check).

**PLS-G3 — SOURCE-POLICY RED (prerequisite sentence broader than its condition; check 6). Bears on no task world; open charter-wide.**
- Sentence (courtesy_waiver ← late_fee): "… only after the loan's ledger carries the late fee owed for every installment left unpaid past its grace period." Condition: "loan_transactions holds a loan_late_fee_assessed line for the oldest unpaid installment (loans.next_due_date) …". loan_ext_late_fee assesses only "on the oldest unpaid installment (the loan's next due date)".
- Demonstration: a loan with two installments unpaid past grace whose oldest already carries its late fee — condition true (waiver may be worked out), sentence false (the later installment has no fee line, and the late-fee policy can never assess it), so the waiver is either computed now or never: two readings.

**Observations (no demonstrated consequence on either task world):**
- O-1 window_anchor_rule tiers 1 and 2 differ only by a one-day offset of the same anchor (XF#9 boundary; accepted as an anchor-convention method).
- O-2 remaining_term_reduction: all tiers 0 on Grades F/G.
- O-3 courtesy_waiver_form: tier 1 unreachable on Grades C–G; where reachable (A/B) it is more generous than tier 2 whenever unpaid × (1 − share) > 5.00 (e.g. a 30.00 fee with share 0.3: 25.00 waived for a waiver < 12 months ago vs 9.00 for one 12–23 months ago) — an inverted repeat-courtesy ladder. refi_sizing_form tier 1 unreachable on F/G.
- O-4 debit_record_step counts returned AutoPay debits ("returned ones included") toward a reward for AutoPay record; requote_cushion keys extra interest days on the number of refinance quotes in the last month. Both plausible-but-unusual; neither decides a tier differently in its task world.
- O-5 refi sizing form 2 "added on top rather than withheld" vs inherited "The fee is withheld from the loan amount"; scored AF unaffected.
- O-6 late-fee fee form under schedule_c names "the schedule's percent", which schedule_c lacks; compute keeps the flat fee.
- O-7 Multiplied relief shares produce assessed fees in odd cents (e.g. 8.99, 8.58); within the charter's own design, not a scored defect.
- O-8 waive_fee_courtesy_87326602 docstring: related_txn_id "as returned by the loan ledger lookup or by the confirmation that charged the fee" presupposes a fee-charging write in the same call (names no tool, no ordering word).
- O-9 RND is Python round() on floats while tools store half-up; no tie at a half cent occurs in either task world.
- O-10 With AutoPay on and the next due date 1 day away, a refinance quote's window is 0 days (good through the quote date), shorter than any funding date; the base underwriting requirement on a quote good through funding is checked at approval, not at application, so no contradiction on the application write.

## closing_checklist
Written after both reveals (2026-10-16 05:00 UTC). The difficulty does NOT close in revision_1: task 1 carries an open SOURCE-FACTOR RED and three charter-wide REDs remain open.
- Audit files: `_difficulty.md`, `0.md`, `1.md` — one per task; first revision, no older revisions.
- Per-task results: task 0 PASS on all four relationships (derivation = GT value for value: 6402.81 / 2026-10-25 / 6531); task 1 unique solution, tree and self-consistency PASS (derivation = GT: 8.99 / 8.58 / 9.19 / 8.09), factors RED (PLS-G1 demonstrated).
- Coverage and scope: six extended policies; task 0 {refi_payoff_quote, refi_application}, task 1 {late_fee, returned_fee, autopay_enroll, courtesy_waiver} — pairwise disjoint, jointly complete, matching both tasks' charter_scope; each task tool has an independent frozen uuid8.
- Trees: task 0 n=1 (1 value_input, user write = application); task 1 n=3 (3 value_input, user write = enrollment); the whole prerequisite graph is acyclic.
- Factors: every computation has 4–6 factors with ≥2 parameter / ≥1 method; each task has multi-source and cross-difficulty factors; every factor bears weight on its world with an honest baseline and a definite, different all-baseline number — but PLS-G1's two factors are unreal ladders.
- Gates: not re-run by this audit (coordinator snapshot cited in charter_global_frozen; the final-form re-run belongs to the closing round).
- Open charter-wide REDs: PLS-G1 (return-code-keyed fee amounts), PLS-G2 (XF#8 decoy/tie/first-match/month-end class, members a–g), PLS-G3 (late-fee prerequisite sentence broader than its condition).

VERDICT revision_1: task0=PASS task1=RED SOURCE-FACTOR charter=PLS-G1,PLS-G2,PLS-G3

## revision_2

## charter_global_frozen (revision_2)
- Re-audit time 2026-10-16 (after rework round 2); auditor: erl-task-policy-audit subagent. Gate: last line of worklog.md is exactly `REWORK round 2: gates 7/7 green` (only that line was read).
- Gate snapshot (`/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 2`, 2026-10-16T05:26:35): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (--check) / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK; TRACEABILITY NOT OK with 6 misses (task 0: 2, task 1: 4), all `tool_name` values of unlock calls, as expected before publication.
- Hashes: loan.extended.yaml f67991596390d146f868df7960b29dc95801da876909fdf539f1cc442b5fd0c7 (r1 2df122f1… → changed); task_tools.py 97842ce464a7d56c3a66f112580f982d4788280d3a7ebc5a70d5ecc0eb257f7a (r1 34db3cd1… → changed); views r2/task_0.json 3cb6a76f…fac8f1, r2/task_1.json e487e4b5…4d9e56. Both shared inputs changed, so every charter-global section below is re-derived in full; revision_1 text above is left untouched.
- Reworker claims read by item id only (tasks/personal_loan_servicing/rework_r2_claims.md); every claim was verified against the artifacts, never taken as evidence.
- Masked / unread until both revision_2 derivations were frozen: tasks/*/tasks/*.json, plan.md, worklog.md (except its last line).
- Base copy: lines 1–1910 still byte-identical to blueprint/products/loan.yaml.

### policy_conflict_scan (r2)
Same six policies, same tools, same prerequisite edges and owners as revision_1. Factor changes: late fee — fee_form_by_return and flexline_month_relief removed; pay_cycle_form (method, cross line) and loan_tenure_relief added. Returned fee — return_reason_share replaced by returned_fee_autopay_relief. Refinance — remaining_term_reduction replaced by remaining_term_credit (fixed points; the grade's refinance reduction is now always taken, a plain baseline quantity). Both the pay-cycle form and the bank-event form read FlexLine records but set different fees, so they don't conflict. Cross-category reads now include line status/amount_past_due/installment_due_date (late fee) and pos_transactions (courtesy point); all fields and values exist in db_schema and their charters (`pos_late_fee_assessed`, FlexLine `frozen`). Task scopes are unchanged: task 0 {refi_payoff_quote, refi_application}, task 1 {late_fee, returned_fee, autopay_enroll, courtesy_waiver}. They remain disjoint and jointly complete.

### rule_compute_equivalence (r2)
- Mechanical sweep (scratch, deleted): every compute_basis quote is in its rule, every binding has a basis and every basis key is a binding, every baseline sentence and every replaced_by is in its rule, every policy_source is in its blocked rule, no binding belongs to two factors.
- Sentence-by-sentence: payoff (window tiers incl. new "2 to validity days" and "plus the grade's late-fee grace days"; hold now `q_extra_returned == 0` ↔ "has not been returned"), refinance (term credit ladder, EXISTS for an active current Credit Builder ↔ "any one account"), returned fee (latest FlexLine return and fee, each with a stated tie rule ↔ XLATEST; tier 2 ↔ `not f_same_event`), AutoPay (debits less returned), courtesy (latest enrollment and latest cancellation of any reason, then test the reason; EXISTS for PracticePay paid-in-full; XCOUNT of PracticePay late fees; tie rules) — equivalent.
- NOT equivalent: loan_ext_late_fee under schedule_c — new finding PLS-R2-1.
- Every policy now states the month convention ("difference in calendar months, less one when the later date's day of the month is smaller"), which equals MONTHS(). Rounding placements match their sentences.

### action_binding_and_uuids (r2)
Same six tools and uuid8s (unchanged, independent, no factor id inside any tool name). Bodies still perform only their create/update. Money and rates are now stored with `round(x, 2)`, the same as RND, and the docstrings say "rounded to the cent". The waiver tool's related_txn_id now reads "as shown for that fee in the loan ledger" (O-8 closed). There are no ordering words, tool names or example values. task_tools.py imports only erlbench.

### prerequisite_graph and prerequisite_sentences (r2)
Graph unchanged (two disjoint stars, acyclic, all state-form value_input edges, gates exist, resolvers write the named rows). Sentences:
1. Refinance ← quote: unchanged, PASS.
2. Courtesy ← late fee: "… only after the loan's ledger carries the late fee owed for the oldest unpaid installment once that installment's grace period has ended." The condition names the same installment (loans.next_due_date). Scope is equal and one write produces it. PASS.
3. Courtesy ← returned fee: "… not fixed until the loan's ledger carries the returned-payment fee owed for the latest returned payment, where its return code bears one." The condition is the same object, and the returned-fee policy assesses exactly that return. PASS.
4. Courtesy ← AutoPay: unchanged, PASS.
No second wording, tool name or policy id; depended-on rules are silent.

### override_declarations (r2)
As in revision_1, plus: refinance now declares the base sentence "The fee is withheld from the loan amount, so net proceeds equal the amount financed minus the fee, and interest accrues on the full amount financed" with self-scope (O-5 closed). The returned fee now states what governs an earlier fee-bearing return ("charged at the schedule amount, unreduced"), so base "charged once for each returned payment" is no longer narrowed silently. The late fee's replaced_by restates the schedule sentence for every other fee. No undeclared override found.

### factor_ladders (r2)
| policy | factors (effect) | p / m | multi-source | cross_difficulty |
|---|---|---|---|---|
| refi_payoff_quote | window_anchor_rule (m), day_rate_split (m), uncleared_payment_hold (p), requote_cushion (p) | 2/2 | window, day_rate, hold | — |
| refi_application | refi_sizing_form (m), remaining_term_credit (p), payment_record_credit (p), autopay_record_credit (p), flexline_standing_credit (p), credit_builder_credit (p) | 5/1 | sizing, payment record, AutoPay, FlexLine | line, builder |
| late_fee | pay_cycle_form (m), first_late_relief (p), modification_relief (p), autopay_history_relief (p), loan_tenure_relief (p) | 4/1 | pay_cycle_form, first_late | line, hardship |
| returned_fee | bank_event_form (m), first_return_relief (p), returned_fee_modification_relief (p), returned_fee_autopay_relief (p) | 3/1 | bank_event, first_return | line, hardship |
| autopay_enroll | unchanged | 3/1 | modified_rate_base | hardship, builder |
| courtesy_waiver | courtesy_waiver_form (m), autopay_restored_point (p), fee_load_point (p), installment_record_point (p), practicepay_point (p), return_reason_point (p) | 5/1 | autopay_restored, practicepay | pos |
- Ladders: each has 3 tiers, each fall-through equals the baseline, and the tiers are distinct in outcome. remaining_term_credit is now distinct on every grade (0.50/0.25/0), so O-2 is closed. pay_cycle_form tiers are three formula shapes (pro-rata share, cap of two cycles at one schedule maximum, plain schedule figure). The window_anchor_rule tiers now use three different anchors (day before due date, end of grace, fixed count), so O-1 is closed. The courtesy form is monotone (share − 5.00 ≤ share ≤ whole), so O-3's inversion is closed. Tier reachability by grade (sizing tier 1 on F/G; courtesy tier 1 on C–G) follows base limits and is carried as an observation.
- Realism: no assessed-fee amount reads a return code (PLS-G1 closed; the courtesy return-reason point is a discretionary waiver weighing why a payment failed, which is realistic). New tiers are realistic: a cross-product late-charge relief in the same pay cycle, loan-tenure relief, an AutoPay-history relief counted on cleared debits, a remaining-term credit, a PracticePay standing without late fees, and a refinance window to the end of the grace period when no AutoPay debit is pending. Observations R2-O1/O4 below.
- XF#1 is still clean (no factor binding reads another factor's binding). XF#10 is clean.

### round-1 RED and observation closure (verified against the artifacts)
- PLS-G1: **closed**. fee_form_by_return and return_reason_share are gone; no fee computation reads `return_code` except the courtesy point and the waived-fee date test.
- PLS-G2: **closed**, member by member. (a) The rule now names the latest FlexLine return and fee, each with a tie rule, and tier 2 is `not f_same_event`, which equals compute. (b) The rule now names the latest enrollment and latest cancellation of any reason, then tests the reason, which equals compute. (c) EXISTS replaces first-match, and tier 2 is stated existentially. (d) The tie rule is stated. (e) `q_extra_returned` exclusion; the round-1 probe world (400 returned 10-19) now gives 6404.19, the correct value. (f) The object is stated, and earlier returns are covered. (g) The convention is stated in all six policies and equals MONTHS().
- PLS-G3: **closed** (sentence and condition both name the oldest unpaid installment).
- Observations O-1…O-10: closed or acceptably carried. O-4's AutoPay debit counts are now less returned; the requote cushion is kept and remains an observation. O-6 was "closed" with a new defect — see PLS-R2-1.

### findings (r2)
**PLS-R2-1 — SOURCE-POLICY RED (rule/compute non-equivalence in loan_ext_late_fee, introduced by the O-6 change; XF#8 class "edge branch without a matching rule tier").** It does not affect either task world (OH / PA, schedule_a); it is open charter-wide.
- Rule: "the pay-cycle form sets the late-fee figure from the schedule figure … when that FlexLine late fee was charged for a FlexLine due date no more than pay_cycle_window_days days … the late-fee figure is the schedule figure times the unpaid portion divided by the unpaid portion plus the FlexLine's amount past due; … the schedule figure or the schedule's maximum less that FlexLine late fee, whichever is smaller … Under schedule_c the schedule figure is its flat amount in every form."
- Compute: `l_form_fee = l_sched_fee if l_is_c else (…)`. For a schedule_c loan the pay-cycle form is bypassed entirely, while the rule keeps the form and only fixes the schedule figure as the flat amount. Tier 2 also needs "the schedule's maximum", which schedule_c does not have.
- Probe (task-1 world with origination_state MD, scratch, deleted): compute gives 7.46; the rule's tier-1 reading gives 10.00 × 274.87 / 330.83 × shares = 6.20. Two defensible answers for every MD/NC/WI loan whose FlexLine was charged a late fee in the same or previous cycle.
- Class sweep (complete): the only other policy with a schedule_c branch is loan_ext_returned_fee. Its schedule_c amount is 0.00 with "no fee line written", so every form yields 0 and the rule agrees. Not a member.
- Affected: loan.extended.yaml loan_ext_late_fee rule (schedule_c sentence and pay-cycle form tiers), compute `l_form_fee`, factors[pay_cycle_form].

**Observations (r2):**
- R2-O1: pay_cycle_form tier 1 is described as "the one late charge of that cycle is shared", yet the FlexLine charged its full fee and the loan charges its pro-rata share of a separate schedule figure. That makes two charges, not one shared charge. As a relief it is plausible (same pattern as bank_event_form tier 1); the rationale wording overstates it.
- R2-O2: `EXISTS('builder', status='active', amount_past_due=0.0)` matches by string ('0.0'); a seed storing 0 or "0.00" would not match. Neither world has an active Credit Builder account.
- R2-O3: task 1's seed now books returned-payment fees on the borrower's later contact days (2024-12-22, 2025-08-12) rather than on the return dates. No rule governs when a state_due fee is booked; the change makes the unbooked 2026-09-08 fee consistent with history. Real lenders usually book returned-payment fees automatically, but nothing scored depends on this.
- R2-O4: second-tier cross-product offsets (pay_cycle_form tier 2: previous-cycle FlexLine late fee caps this loan's fee within one schedule maximum; bank_event_form tier 2) are relief measures, plausible but unusual. requote_cushion (O-4) is carried.
- Carried: sizing tier 1 unreachable on F/G; courtesy form tier 1 reachable only on A/B; O-7 odd-cent fees; O-10 is closed (AutoPay-on window ≥ 1 day).

## closing_checklist (revision_2)
Written after both revision_2 reveals (2026-10-16 05:52 UTC). Both tasks PASS all four relationships; derivation equals GT value for value (task 0: 6438.42 / 2026-11-09 / 6519; task 1: 9.30 / 8.58 / 9.19 / 8.37). Every round-1 RED (PLS-G1, PLS-G2 a–g, PLS-G3) is closed and verified against the artifacts. No regression was found in either task world. Scopes are disjoint and complete; tool uuid8s are unchanged and independent; trees have n = 1 and n = 3 with all edges value_input and a user write each; the graph is acyclic; each computation has 4–6 factors (≥2 parameter, ≥1 method), each task has multi-source and cross-difficulty factors, and every factor bears weight against an honest baseline. Gates were re-run by the coordinator snapshot (7 OK; traceability unlock-name misses only).
The difficulty still does not close, because one charter-wide RED is open: **PLS-R2-1** (loan_ext_late_fee schedule_c branch of the pay-cycle form: rule vs compute, 6.20 vs 7.46 on an MD probe). It was introduced by the O-6 change and affects neither task world.

VERDICT revision_2: task0=PASS task1=PASS charter=PLS-R2-1

## revision_3

## charter_global_frozen (revision_3)
- Re-audit time 2026-10-16 (after rework round 3). Gate: worklog.md's last line is exactly `REWORK round 3: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 3` (2026-10-16T11:00:10): EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK with 6 misses, all unlock `tool_name` values (pre-publication, expected).
- Hashes vs r2:
  - loan.extended.yaml 32a518875448e2938337a9b1434ab28cb9b05bfc015734db75d1e504927aadd1 — changed, so the touched sections are re-derived.
  - task_tools.py 97842ce4…f7a — unchanged, so action_binding_and_uuids carries forward from revision_2.
  - Views r3/task_0.json 3cb6a76f…fac8f1 and r3/task_1.json e487e4b5…4d9e56 — identical to r2.
- Claims file read by item id; every claim checked against the artifacts. Base copy is still verbatim.

### re-derived sections (r3)
- What moved: rule/ladder/compute_basis/overwrite text of loan_ext_late_fee (schedule_c scoping, tier wording); loan_ext_returned_fee (tier-1 wording, schedule_c sentence); loan_ext_courtesy_waiver (returned-fee prerequisite sentence and condition); loan_ext_refi_application and loan_ext_autopay_enroll (Credit Builder reads are now a numeric CFIELD with a None guard, plus a one-active-account sentence that matches builder_agg_multi_holding, max_per_customer 1). The other compute bindings are byte-identical to r2.
- rule_compute_equivalence: the mechanical sweep is clean (quotes in rule, bindings ↔ basis, baseline and replaced_by in rule, policy_source in rule, no binding in two factors, no factor id in any tool name, no numeric value used in an equality filter). Schedule-branch probes on copies of the task-1 world:
  - Late fee: MD → 7.46 (flat 10.00 × shares; the rule now says schedule_c takes no form), CA tier 1 → 8.52, CA tier 2 → 0.00, PA → 9.30.
  - Returned fee: MD → 0.00 with no line, CA → 5.72, PA → 8.58.
  - The rule's reading equals compute on every probe.
- prerequisite_sentences: the courtesy ← returned-fee sentence ("… where its return code bears one and the loan's fee schedule charges more than 0.00 for it") and its condition (origination state not MD/NC/WI) have equal scope over the reachable domain: on schedule_a/b no form reaches 0, because the FlexLine returned fee is 15.00 on every FlexLine tier. One write produces the state. The other three edges are unchanged. Graph: PASS.
- override_declarations: the late fee's replaced_by now restates the schedule_c case; no undeclared override.
- factor_ladders: counts unchanged (refi 5p/1m, quote 2p/2m, late 4p/1m, returned 3p/1m, AutoPay 3p/1m, waiver 5p/1m). pay_cycle_form tiers are scoped to schedule_a/b, with schedule_c in the fall-through. Tiers stay distinct.

### round-2 RED and observation closure (verified)
- **PLS-R2-1: closed.** The rule, ladder and replaced_by now exclude schedule_c from the pay-cycle form, which matches the unchanged compute; tier 2 names the loan's own schedule maximum. Probes above.
- PLS-R2-1 class sweep: confirmed. Every schedule branch of the late fee and the returned fee agrees between rule and compute; the other policies have no schedule branch.
- R2-O1 closed: tier wording now describes cutting the loan's own fee, with the FlexLine fee left as charged, in both forms. R2-O2 closed: numeric compare with a None guard. R2-O3 and R2-O4 carried as observations.

### findings (r3)
**PLS-R3-1 — SOURCE-POLICY RED (XF#8 zero-result edge: a computed amount of 0.00 with no rule saying whether its line is written). Pre-existing and first found in this round. It does not affect either task world; it is open charter-wide.**
Members (complete list):
- (i) **loan_ext_late_fee, pay_cycle_form tier 2 on schedule_b.** The figure is min(schedule figure, 15.00 − FlexLine late fee), never below zero. The FlexLine late fee is 25.00 on every FlexLine tier, so on every schedule_b loan whose previous-cycle FlexLine late fee falls 16–45 days from the installment's due date the late fee is 0.00. Probe: task-1 world with origination_state CA and the FlexLine late fee for 2026-08-05 gives 0.00. On schedule_a, 30.00 − 25.00 leaves 5.00, so schedule_a is not a member.
- (ii) **loan_ext_courtesy_waiver, form tier 1 and the share clamp.** Tier 1 gives max(0, unpaid × share − 5.00), and the share is held between 0 and 1. Probe: task-1 world with a courtesy waiver 6 months back (Grade B allows two per 12 months), three fees in 3 months and no re-enrollment gives 0.00. A share clamped to 0 (base 0.30, load −0.20, reason −0.10) zeroes tier 2 too.

Why this is a RED:
- loan_ext_returned_fee states the zero case ("under schedule_c the fee is 0.00 and no fee line is written"); neither member does.
- In (i) one reading writes a 0.00 late-fee line, which then satisfies the courtesy edge-1 condition and leads to a 0.00 waiver. The other reading writes no line, which leaves the waiver unfixable forever ("worked out only after the loan's ledger carries the late fee owed …").
- In (ii) one reading writes a 0.00 courtesy waiver line, which uses up one of the grade's courtesy waivers per 12 months (base courtesy_allowance counts waivers granted) and the fee's once-only waiver (base one_waiver_per_fee). The other reading grants nothing and records nothing.
- Two defensible terminal states in each case.
- Class sweep: every other computed amount is either stated for the zero case (returned fee on schedule_c) or cannot reach 0 on the reachable domain: returned fee tiers 1/2 on schedule_a/b (≥ 2.50), late fee tier 1, quote, amount financed, AutoPay rate.
- Affected: loan.extended.yaml loan_ext_late_fee (pay-cycle tier-2 sentence, factors[pay_cycle_form]); loan_ext_courtesy_waiver (waiver-form sentence, share sentence, factors[courtesy_waiver_form]).

Observations (r3): R3-O1 — tier 2 on schedule_b always gives 0.00 (the 25.00 FlexLine fee exceeds the 15.00 maximum), so the tier is in effect a full waiver for schedule_b borrowers. That is plausible as relief, but every schedule_b loan reaching that tier has an identical outcome (realism noted, not a second answer). R2-O3 and R2-O4 carried.

## closing_checklist (revision_3)
Written after both revision_3 reveals (2026-10-16 11:02 UTC).
- Both tasks PASS all four relationships, and each derivation equals GT value for value (task 0: 6438.42 / 2026-11-09 / 6519; task 1: 9.30 / 8.58 / 9.19 / 8.37).
- PLS-R2-1 is closed, with its class swept across every schedule branch. No regression: both worlds give the same scored values as in revision_2, and every factor still bears weight.
- Scopes are disjoint and complete; uuid8s are unchanged; trees have n = 1 and n = 3 with all edges value_input and a user write each; the graph is acyclic.
- Gates: the coordinator snapshot shows 7 OK, plus traceability misses on unlock names only.
- The difficulty still does not close, because one charter-wide RED is open: **PLS-R3-1**. Two computed amounts can reach 0.00 with no stated rule on whether their line is written: the late fee's pay-cycle tier 2 on schedule_b, and the courtesy waiver's form tier 1 or zero share. This is pre-existing, first found now, and affects neither task world.

VERDICT revision_3: task0=PASS task1=PASS charter=PLS-R3-1

## revision_4

## charter_global_frozen (revision_4)
- Re-audit time 2026-10-16 (after rework round 4). Gate: worklog.md's last line is exactly `REWORK round 4: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 4`: EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK. Per the brief I did not run check_traceability myself, so the miss list is not itemised here; rounds 1–3 showed unlock `tool_name` misses only.
- Hashes:
  - loan.extended.yaml e63adb09f42f1243c0c967beba5e98f3acc749f16cef94b52b4c82878a0c97bc — changed, so re-derived.
  - task_tools.py 97842ce4…f7a — unchanged since r2; action_binding_and_uuids carried by hash.
  - Views r4/task_0.json 3cb6a76f…fac8f1 and r4/task_1.json e487e4b5…4d9e56 — unchanged since r2.
- Claims file read by item id and verified against the artifacts. Base copy is still verbatim.

### re-derived sections (r4)
- What moved:
  - Zero-case sentences in all six rules.
  - The courtesy ← late-fee and ← returned-fee prerequisite sentences and conditions ("where that … fee works out above 0.00"; conditions add "a fee that works out to 0.00 writes no line, and then nothing is waited on").
  - Courtesy compute: `c_unpaid = … if c_fee_amount != None else 0`.
  - The rest of compute is byte-identical to r3.
- Mechanical sweep: 0 issues (quotes, bindings ↔ basis, baseline / replaced_by / policy_source in rule, disjoint bindings, ladders ≥ 3 tiers, no factor id in a tool name).
- Factor counts are unchanged: quote 2m/2p, refi 1m/5p, late 1m/4p, returned 1m/3p, AutoPay 1m/3p, waiver 1m/5p.
- Prerequisite sentences: the two narrowed sentences keep exact scope with their conditions, and the zero case is now stated on both sides. One write produces each state. The graph is unchanged and acyclic. PASS.
- Zero-case claims checked:
  - Payoff: positive whenever principal > 0.
  - Refi: AF ≥ payoff in all three forms.
  - AutoPay: the lowest rate base is 5.99 (TEM floor) + discount, or a base-rate floor ≥ 7.99, against a maximum total discount of 0.50 + 0.30 = 0.80, so the rate is always > 0.
  - Late fee and returned fee: 0.00 writes no line and is not counted; every count of "fees charged" reads only written lines, so this is consistent.
  - Courtesy: 0.00 is not granted, uses no allowance and writes no line.
  - The added payoff condition "a loan with no unpaid principal is not quoted" applies only to refinance-purpose quotes and is unreachable for an active loan under base allocation (fees are paid before principal). Observation R4-O1.

### round-3 RED closure (verified)
- **PLS-R3-1: closed.**
  - Member (i): the late-fee rule states that 0.00 is not charged and writes no line. The CA tier-2 probe (0.00) now has a single reading, and the courtesy edge no longer waits on it.
  - Member (ii): a 0.00 courtesy waiver is not granted and writes no line, so the round-3 probe (0.00) has a single reading.
  - Class: the returned-fee zero case covers every form; payoff, refi and AutoPay cannot reach 0.
- R3-O1, R2-O3 and R2-O4 carried.

### findings (r4) — whole-charter sweep for remaining classes
I re-ran every XF_recipe item against all six policies:
- factor independence; assembly order; factor-only quantities; overwrite hygiene; quotes; rounding; docstrings (tools unchanged)
- decoy, absent-record, None / zero-division / negative-lag, tie, month-end, entries-vs-periods and exclusion probes
- method shape; factor ids; cross-record pairing; realism; runtime
Two classes remain. I list every member of each, and record the non-members with their reasons, so the sweep is complete.

**PLS-R4-1 — SOURCE-POLICY RED (XF#8 entries-vs-periods / exclusion class: "installment payments credited" subtracts returns of payments that were never installment payments). It affects neither task world; open charter-wide.**
- Every member counts `scheduled_installment` payments posted minus *every* `loan_payment_returned` row on the loan. Return rows carry no payment_type, so a returned additional_principal, partial_installment or payoff payment also removes one "credited installment".
- Members (complete):
  - (a) loan_ext_refi_application.payment_record_credit (`r_installments`; rule "less the number of payments returned on it"). The wording is literal here, but the condition is one no lender weighs: a bounced extra-principal payment un-credits no installment.
  - (b) loan_ext_late_fee.first_late_relief (`l_inst_12m`).
  - (c) loan_ext_returned_fee.first_return_relief (`f_inst_12m`).
  - (d) loan_ext_courtesy_waiver.installment_record_point (`c_inst`).
  - For (b)–(d) the rule's own parenthetical "installment payments credited (payments of type scheduled_installment posted less payments returned)" reads equally as "less those installment payments returned", so each has a second reading.
- Probe (copy of the task-0 world cut to exactly 12 scheduled installments with no return): r_installments 12 gives a payment-record credit of 0.50 and AF 6519. Adding one returned $250 additional-principal payment gives r_installments 11, credit 0.25 and AF 6535.
- Non-members:
  - The AutoPay counts (refi autopay_record_credit, late autopay_history_relief, returned returned_fee_autopay_relief, AutoPay debit_record_step) subtract only `payment_channel='autopay_ach'` returns, each of which reverses an AutoPay installment debit.
  - The hold's "a payment on the loan was returned" and returned-fee "no other returned payment" intentionally count any return.
- Inert in both worlds: every seeded return reverses a scheduled_installment payment (task 0: 2024-01-24, 2025-09-29; task 1: 2024-12-09, 2025-08-07, 2026-09-08).

**PLS-R4-2 — SOURCE-POLICY RED (XF#8 decoy class "LATEST read with no exclusion of a waived row": a single FlexLine fee read as a cycle marker or offset counts even after that fee was waived). It affects neither task world; open charter-wide.**
- Members (complete):
  - (a) loan_ext_late_fee.pay_cycle_form reads the latest `line_late_fee_assessed` (installment_due_date, amount) and ignores `line_fee_waived`. Tier 1's premise is "the FlexLine late fee itself stays as charged"; tier 2 holds the loan's fee "so that it and that FlexLine late fee together stay within the maximum".
  - (b) loan_ext_returned_fee.bank_event_form reads the latest `line_returned_payment_fee_assessed` (date, amount), unchanged after the fee is waived. Tier 1's premise is "the FlexLine fee itself stays as charged"; tier 2 subtracts "half that FlexLine fee".
- FlexLine waivers are a state the line charter produces (`line_fee_waived`, reasons courtesy / lender_error / bank_error_documented / unauthorized_debit). Probes (copy of the task-1 world, both FlexLine fees waived on 2026-09-17):
  - Late fee: compute 9.30 vs 11.20 under the reading that a waived fee is no longer "charged".
  - Returned fee: compute 8.58 vs 10.33.
  - Late fee, PA world with the waived FlexLine late fee in the previous cycle: compute 3.73 vs 11.20.
- Non-members: the history counts of fees "charged" (refi FlexLine credit's FlexLine late fees, late fee l_late_12m, refi r_late_24m, courtesy fee-load c_late_3m/c_ret_3m and PracticePay late-fee count). These test whether a late or returned payment occurred, the rules say "charged", and a later waiver does not undo that event, so there is a single reading. The courtesy waiver's own fee read already nets earlier waivers through `c_fee_waived`.
- Inert in both worlds: no line_fee_waived row exists in either seed.

Observations (r4): R4-O1 (the payoff zero-principal condition is unreachable for an active loan); R3-O1, R2-O3 and R2-O4 carried.

## closing_checklist (revision_4)
Written after both revision_4 reveals (2026-10-16 14:21 UTC).
- Both tasks PASS all four relationships; derivation equals GT value for value (task 0: 6438.42 / 2026-11-09 / 6519; task 1: 9.30 / 8.58 / 9.19 / 8.37).
- PLS-R3-1 is closed with its class; no regression (both worlds reproduce r3 values, and every factor bears weight). Scopes, uuid8s, trees and graph are unchanged and pass.
- Gates: 7 OK per the coordinator snapshot; traceability not itemised this round, by instruction.
- The whole-charter sweep leaves two open charter-wide classes, each listed in full with its non-members: **PLS-R4-1** (credited-installment counts subtract non-installment returns; 4 members) and **PLS-R4-2** (waived FlexLine fee still read as a cycle marker or offset; 2 members). Neither affects either task world, and no other XF class has a member.

VERDICT revision_4: task0=PASS task1=PASS charter=PLS-R4-1,PLS-R4-2

## revision_5

## charter_global_frozen (revision_5)
- Re-audit time 2026-10-16 (after rework round 5). Gate: worklog.md's last line is exactly `REWORK round 5: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 5`: EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK (pre-publication; not itemised, check_traceability not run by me per the brief).
- Hashes:
  - loan.extended.yaml 46d1155933e95a1b29fb6f9b4d30d3b4fb474d9597c5daaee50e44c58702b512 — changed, so the moved reads are re-derived.
  - task_tools.py 97842ce4…f7a — unchanged.
  - Views r5/task_0.json 3cb6a76f…fac8f1 and r5/task_1.json e487e4b5…4d9e56 — unchanged since r2.
- Claims file read by item id; the reworker's read-site table was not taken as evidence, and every read below was re-checked against rule and compute. Base copy is still verbatim.

### re-derived sections (r5)
- What moved:
  - The four installment-count sentences ("… less one for every payment returned whatever it was for"; refi "… less one for every payment returned on it, whatever it was for").
  - The AutoPay-debit definition sentence in the refi, late fee, returned fee and AutoPay rules ("any payment AutoPay took on the loan, a hardship plan payment included").
  - Net-of-waiver FlexLine reads in pay_cycle_form and bank_event_form (`l_line_late_id/_waived/_net`, `f_line_fee_id/_waived/_net`, XSUM of `line_fee_waived` by related_txn_id).
  - Courtesy unpaid part (`c_pay_n`, `c_pay_id`, `c_pay_reversed`, `c_unpaid`) plus its rule and baseline sentences.
- Rule ↔ compute on every moved read:
  - Counts: compute subtracts every `loan_payment_returned`, as now stated — equivalent.
  - AutoPay: channel `autopay_ach` posted / returned, any payment_type — equivalent.
  - Net-of-waiver: fully waived means no FlexLine fee (tier 3, schedule figure or amount); partly waived means the unwaived amount in the tier-2 offsets — equivalent.
  - Courtesy unpaid part: equivalent to its own new sentence, but see PLS-R5-1.
- Absent-record and tie checks on the new reads: an id of None gives 0 waived; XLATEST ties are first-recorded as stated.
- Factor counts and labels are unchanged. The prerequisite graph and sentences are unchanged since r4: PASS.

### round-4 RED closure (verified)
- **PLS-R4-1: closed.** All four counts now state, in one reading, the quantity compute counts. "A returned payment of any kind" as a mark on a payment record is a condition a lender plausibly weighs. The AutoPay counts carry an explicit definition equal to compute.
- **PLS-R4-2: closed.** Both FlexLine fee reads net out FlexLine waivers. The round-4 probes (both FlexLine fees fully waived) now resolve to the "no FlexLine fee" reading in rule and compute alike. History counts of fees "charged" stay as charges, which is a single reading.
- R4-O1, R3-O1, R2-O3 and R2-O4 carried.

### findings (r5) — whole-charter sweep
I re-ran the r4 whole-charter XF sweep over every moved read and every 0/1 or existence condition in all six policies. One new member was found; the class sweep follows.

**PLS-R5-1 — SOURCE-POLICY RED (the skill's disguised-override form "the 0/1 multiplier", which is also an invented mechanic under XF#12 realism). Introduced in r5 by the courtesy unpaid-part change. It affects neither task world; open charter-wide.**
- Rule and baseline: "a late fee paid through two or more fee payment lines is outside this policy's courtesy amount, which then works out to 0.00." Compute: `c_unpaid = (RND(c_fee_amount - c_fee_paid + c_pay_reversed - c_fee_waived, 2) if c_pay_n <= 1 else 0)`.
- What it does: an existence condition (count of fee payment lines ≥ 2) multiplies to zero the quantity that inherited base text fixes ("for the part of the fee still unpaid"). Under the zero rule it then turns into "not granted". The base courtesy eligibility (loan_evt_fee_waiver courtesy_allowance: on-time installments, allowance count, request window) is inherited unretired and grants the waiver. The overwrite retires only the amount sentence, so it does not name the eligibility it now removes.
- Realism: no lender denies a courtesy waiver because the fee was paid down through two payments. In this product's own domain the shape is ordinary: a payment funds part of the fee, bounces (its fee payment line is reversed, base loan_evt_returned_payment), and the borrower pays again.
- Probes (copy of the task-1 world after the three prerequisite writes):
  - Late fee 9.30, 5.00 paid then reversed, then 3.00 paid. The unpaid part per base is 6.30, so the waiver would be 6.30 × 0.90 = 5.67; compute gives 0 and the waiver is not granted.
  - Fee paid 2.00 + 2.00 with no reversal. Base gives 5.30 × 0.90 = 4.77; compute gives 0.
- Class sweep (every existence or 0/1 condition applied to a base-fixed amount, listed completely):
  - The only member is the one above.
  - Non-members:
    - Late-fee and returned-fee zero rules: the amount is computed and then not charged, so no existence condition is multiplied.
    - Returned fee on schedule_c: base itself says 0.00 with no line.
    - "with no late fee on the loan there is nothing to waive": base-consistent.
    - Payoff "a loan with no unpaid principal is not quoted" (R4-O1): a refusal condition, not a multiplier, and unreachable for an active loan.
    - Hold exclusion of a returned payment: the return already restored it, a base-consistent exclusion.
    - pay_cycle_form tier 1 "the open FlexLine still has an amount past due" and bank_event_form "not waived in full": tier conditions inside declared factors, not multipliers on a base amount.
- Affected: loan.extended.yaml loan_ext_courtesy_waiver rule (unpaid-part sentence), baseline.rule, compute `c_pay_n`/`c_unpaid`, compute_basis `c_unpaid`/`c_pay_n`.

No other XF class has a member after this sweep. Observations carried: R4-O1, R3-O1, R2-O3, R2-O4.

## closing_checklist (revision_5)
Written after both revision_5 reveals (2026-10-16 21:31 UTC).
- Derivation equals GT value for value in both tasks (task 0: 6438.42 / 2026-11-09 / 6519; task 1: 9.30 / 8.58 / 9.19 / 8.37). PLS-R4-1 and PLS-R4-2 are closed; no scored value regressed.
- The difficulty does not close:
  - Both task files carry an XF#14 stale-proof-text RED: task 0 has 1 member; task 1 has 7 members (6 tier_taken labels + 1 trace).
  - These are per-task GT-artifact defects, so they live in 0.md and 1.md. Two of task 1's members predate r5 and were missed by my r3/r4 comparisons (disclosed in 1.md).
- Open charter-wide: **PLS-R5-1** (the courtesy unpaid part is zeroed when a fee has two or more fee payment lines — a 0/1 multiplier on a base-fixed amount and an invented mechanic; introduced in r5; sole member of its class).
- Gates: 7 OK per the snapshot; traceability not itemised, by instruction.

VERDICT revision_5: task0=RED SOURCE-FACTOR task1=RED SOURCE-FACTOR charter=PLS-R5-1

## revision_6

## charter_global_frozen (revision_6)
- Re-audit time 2026-10-16 (after rework round 6). Gate: worklog.md's last line is exactly `REWORK round 6: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 6`: EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK (pre-publication, not itemised; not run by me per the brief).
- Hashes:
  - loan.extended.yaml 4b2349418d48c3a6042fdc1f74415514f74509c8eb69d898e319ee48388d4213 — changed.
  - task_tools.py 30da55a2b8320d8e394a8ca0188196b69e0587e2ee390d156207b6dc256e19dc — changed. Re-checked: the only change is the waive_fee_courtesy_87326602 docstring, "one unpaid fee" → "one fee". Bodies, signatures, owners and uuid8s are unchanged; no ordering words, tool names or example values.
  - Views r6/task_0.json and r6/task_1.json — unchanged since r2.
- Claims file read by item id. Base copy is still verbatim.

### re-derived sections (r6)
- What moved:
  - loan_ext_courtesy_waiver only: overwrite replaced_by and its rule copy, the "waivable part" sentence in the rule and baseline.rule, ladder text, compute (`c_fee_paid`, `c_pay_n`, `c_pay_id` and `c_pay_reversed` removed; `c_fees_owed = F('fees_balance')`; `c_unpaid = MX(0, MN(RND(fee - waived, 2), fees_balance))`).
  - The other five policies are byte-identical in compute to r5.
- Mechanical sweep (quotes, bindings, baseline, replaced_by, policy_source, ladders): clean. Rule ↔ compute on the waivable part: equivalent.
- The courtesy prerequisite graph and sentences are unchanged: PASS.

### round-5 RED closure (verified)
- **PLS-R5-1: closed.** The two-payment-line 0/1 multiplier is gone from rule, baseline and compute. The round-5 probes (5.00 paid then reversed + 3.00 paid; 2.00 + 2.00) now give a waivable part capped by the fees balance, not 0.

### findings (r6)
**PLS-R6-1 — SOURCE-POLICY RED (the change that closed PLS-R5-1 creates a new conflict: a courtesy waiver capped by the loan's aggregate fees balance instead of the waived fee's own balance). It affects neither task world; open charter-wide.**
- New text:
  - replaced_by: "the amount waived is the one set below, never more than the loan's fees balance". This retires the base "for the part of the fee still unpaid (a fee already paid in full is not waived; a refund of a paid fee is outside this policy)" for courtesy late-fee waivers.
  - Rule: "Its waivable part is its amount less every earlier waiver line applied to it, held to no more than the loan's fees balance … so a courtesy waiver … never refunds money already paid; … the waiver comes off the fees the loan still owes."
- Probe (copy of the task-1 world after the three prerequisite writes; the 9.30 late fee then paid in full through a fee payment line, so fees balance = the 8.58 returned fee):
  - Waivable part 8.58; courtesy waiver 7.72, recorded against the paid late fee.
  - Under the retired base clause this fee is not waived, and the blueprint's difficulty summary routes "refunding a fee that was already paid" to a human as POLICY_NOT_COVERED.
- Demonstrated conflicts, each two passages reaching different conclusions on the same world:
  - (1) Inherited base loan_evt_fee_waiver (still in force for every other basis): "one waiver line per fee, for the part of the fee still unpaid"; "Each fee can be waived at most once."
    - After the probe, the returned fee's own lines show 8.58 unpaid and unwaived, while the fees balance is 0.86.
    - A later lender_error or hardship_relief waiver of that returned fee waives 8.58 under base (the balance goes to −7.72), or at most 0.86 if the balance governs.
  - (2) The rule's own claim "never refunds money already paid" contradicts its effect. 7.72 of a paid fee's value is credited against a different fee, which is a refund of a paid fee in substance, exactly the case the base clause and the blueprint scope put outside the charter.
  - (3) Realism (XF#12): a lender waives a fee by reference to that fee's own unpaid amount. A courtesy waiver posted against a paid fee to clear another fee is not a published courtesy practice.
- Class sweep (every amount capped by a loan-level aggregate instead of the object's own balance):
  - The only member is the courtesy waivable part.
  - Non-members:
    - Payoff `q_fees = fees_balance`: the payoff's object is the whole loan.
    - Late-fee unpaid portion `MN(scheduled_payment_amount, amount_past_due)`: base-defined formula.
    - Returned fee: no balance cap.
    - Refi / AutoPay: no fee balance reads.
- Affected: loan.extended.yaml loan_ext_courtesy_waiver overwrite[0].replaced_by, the rule's waivable-part sentence, baseline.rule, compute `c_fees_owed`/`c_unpaid`.

No other XF class has a member after the whole-charter sweep (the other five policies are unchanged since r5's sweep). Observations carried: R4-O1, R3-O1, R2-O3, R2-O4.

## closing_checklist (revision_6)
Written after both revision_6 reveals (2026-10-16 23:12 UTC).
- Derivation equals GT value for value in both tasks (task 0: 6438.42 / 2026-11-09 / 6519; task 1: 9.30 / 8.58 / 9.19 / 8.37). PLS-R5-1 is closed. Every tier_taken in both tasks is now a current ladder tier. No scored value regressed.
- Task 0: PASS.
- Task 1: two XF#14 retired-term members remain. (g) is the factor trace "credited", claimed fixed in r6 but still present. (h) is the closure flip text "unpaid part", stale after the r6 rename. Details are in 1.md.
- Open charter-wide: **PLS-R6-1**. The courtesy waivable part is capped by the loan's aggregate fees balance, so a paid late fee can be "waived" by crediting another fee. This conflicts with the inherited base waiver rule for other bases on that other fee, is a paid-fee refund in substance, and is an invented mechanic. It was introduced by the PLS-R5-1 fix and is the sole member of its class.
- Gates: 7 OK per the snapshot; traceability not itemised, by instruction. My own label slip (returned_fee_autopay_relief tier) is corrected in 1.md; no figure was affected.

VERDICT revision_6: task0=PASS task1=RED SOURCE-FACTOR,SOURCE-CHAIN charter=PLS-R6-1

## revision_7

## charter_global_frozen (revision_7)
- Re-audit time 2026-10-17 (after rework round 7). Gate: worklog.md's last line is exactly `REWORK round 7: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 7`: EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK (pre-publication, not itemised; not run by me).
- Hashes: loan.extended.yaml bdba8c2f8e7052618b46e5e670ebfeb85238bebac7e935035be74e1be12cce36 (changed); task_tools.py 30da55a2…19dc (unchanged since r6); views r7/task_0.json and r7/task_1.json (unchanged since r2).
- Claims file read by item id. Base copy is still verbatim. Mechanical sweep: 0 issues.
- What moved: loan_ext_courtesy_waiver only (overwrite replaced_by and its rule copy, the unpaid-part sentence, baseline.rule, the late-fee edge effect, compute `c_fees_owed` removed and `c_unpaid = fee − earlier waivers`). The other five policies are unchanged since r5.

### PLS-R6-1 closure, and the coordinator's question on the scoped overwrite
- **PLS-R6-1: closed.** There is no fees-balance cap, so the r6 probe (a paid late fee "waived" against the returned fee) is now out of scope: a fee payment is posted against that fee, so base applies and a fee paid in full is not waived.
- **Is the scope stated exactly? The wording yes, the reach no.**
  - The replaced_by is self-naming ("for a courtesy waiver of a late fee with no fee payment posted against it, and only for such a fee").
  - It names the out-of-scope set ("every other fee, a late fee with a fee payment posted against it included").
  - It restates the base clause word for word except "bases below" → "bases of loan_evt_fee_waiver".
  - "Posted against it" is record-visible (a `loan_fee_paid` line with related_txn_id = the fee), and a payment posted and later reversed still counts as posted, which is a single reading.
  - But the in-scope set ("a late fee with no fee payment posted") is wider than the only object the policy's amount rule computes ("The fee waived is the latest late fee charged on the loan"). See PLS-R7-1.
- **Do out-of-scope fees stay under the in-force base content? Yes.** The restated clause plus the inherited loan_evt_fee_waiver sentences (bases, once per fee, courtesy eligibility, window, priority) give a definite base outcome: a courtesy waiver of the whole part still unpaid. Nothing in the extended rule reaches them. The realism of that split is PLS-R7-2(a).

### findings (r7) — whole-charter sweep
**PLS-R7-1 — SOURCE-POLICY RED (scope wider than the computed object). Introduced in r7; affects neither task world.**
- In-scope set: every late fee with no fee payment posted. Computed object: only "the latest late fee charged on the loan" (rule, baseline and compute `c_fee_*` = LATEST).
- An earlier late fee with no fee payment posted (two consecutive missed installments, the older fee unpaid and still within the waiver window) is inside the scope, so "the amount waived is the one set below". But "below" defines an amount only for the latest late fee.
- Two readings for a courtesy request on that older fee:
  - (i) No amount is defined, so the request is not covered (handed to a human, or refused).
  - (ii) The rule's sentences are applied to the older fee (its own unpaid part, its due date for the return-reason point), which compute cannot produce.
- Before r7 the scope was "a courtesy waiver of a late fee this policy sets", which coincided with the object; the r7 rewording widened it.

**PLS-R7-2 — SOURCE-POLICY RED (XF#12 realism / base conflict: treatment decided by recency or record shape alone where the business, or base, treats every qualifying record alike). Members, complete list:**
- (a) **loan_ext_courtesy_waiver scope (r7).** Whether any fee payment was posted decides between the factor-driven courtesy amount and base's whole-unpaid-part waiver. Probe arithmetic on the task-1 world: a 9.30 late fee with no payment gets 8.37 waived (borrower keeps 0.93); the same fee with a 0.01 fee payment posted gets 9.29 waived. Under a repeat courtesy fewer than 12 months back, 3.37 vs 9.29. A one-cent payment switches off every courtesy factor and gives a larger waiver, a gameable boundary no lender publishes.
- (b) **loan_ext_returned_fee object (r2).** Only the latest returned payment gets the bank-event form and relief shares; "a fee owed on any earlier fee-bearing return is charged at the schedule amount, unreduced". Probe: copy of the task-1 world with an earlier unfeed R01 return on 2026-09-03. The latest return's fee is 10.09, while the earlier return's fee is 15.00, under the same modification and AutoPay standing. Identical events are priced by recency alone. Reachable given the seed history's "fees booked at the borrower's next contact" (R2-O3).
- (c) **loan_ext_refi_payoff_quote uncleared_payment_hold (r1).** "Looking only at the latest payment of type additional_principal": an earlier additional-principal payment still inside its hold window is never held. Probe: copy of the task-0 world with 400.00 on 10-16 and 100.00 on 10-19, both online ACH. Held = 100.00 only. If the 400.00 bounces, the refinance payoff transfer falls 400.00 short of retiring the loan. A funds hold applies to every uncleared payment.
- (d) **loan_ext_refi_payoff_quote day_rate_split (r1).** "The rate each interest day carries follows the loan's latest AutoPay record": with two AutoPay changes after the paid-through date, only the latest is used. Probe: copy of the task-0 world with paid-through 10-16, cancellation 10-17, re-enrollment 10-19, current 13.99. The rule gives +1.50 rate-days (3 days at +0.50). Base loan_evt_autopay ("interest for each day accrues at the rate in force that day", in force and not retired by this policy) gives +1.00 (10-16→10-17 discounted, 10-17→10-19 full). Two passages, two quoted interests.
- Non-members (each reads the latest record as a marker of a single event, which the business does):
  - pay_cycle_form's latest FlexLine late fee; bank_event_form's latest FlexLine return and fee.
  - The courtesy points' latest AutoPay records (a status test) and latest return (the return behind the waived fee).
  - The late fee on the oldest unpaid installment (base).
  - The refinance quote dated today (one per date).
- Members (b), (c) and (d) date from earlier revisions, which I accepted; this whole-charter pass is where I first classify them.

Both affect neither task world: task 0 has one additional-principal payment in its hold window and one AutoPay change after paid-through; task 1 has one unfeed return and a waived fee with no payment. Observations carried: R4-O1, R3-O1, R2-O3, R2-O4.

## closing_checklist (revision_7)
Written after both revision_7 reveals (2026-10-17 02:00 UTC).
- Both tasks PASS all four relationships; derivation equals GT value for value (task 0: 6438.42 / 2026-11-09 / 6519; task 1: 9.30 / 8.58 / 9.19 / 8.37).
- Every tier label, edge copy and trace in both task files matches the current charter. PLS-R6-1 and the r6 XF#14 members are closed; no regression.
- Answer to the coordinator's question:
  - The scoped overwrite is stated exactly in wording, and out-of-scope fees really do stay under the in-force base content.
  - But the r7 scope is wider than the policy's computed object (PLS-R7-1).
  - The payment-posted boundary is itself an unreal, gameable split (PLS-R7-2(a)).
- Whole-charter sweep: one remaining class, PLS-R7-2, listed in full: (a) courtesy payment-posted scope, (b) returned-fee latest-return-only reductions, (c) payoff hold latest-payment-only, (d) day-rate split latest-AutoPay-record-only, which conflicts with base loan_evt_autopay. The non-members are listed. No other XF class has a member.
- Gates: 7 OK per the snapshot; traceability not itemised, by instruction.

VERDICT revision_7: task0=PASS task1=PASS charter=PLS-R7-1,PLS-R7-2

## revision_8

## charter_global_frozen (revision_8)
- Re-audit time 2026-10-17 (after rework round 8). Gate: worklog.md's last line is exactly `REWORK round 8: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 8`: EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK (pre-publication, not itemised; not run by me).
- Hashes: loan.extended.yaml e46ab684012d0a58d779c8e136a08ca7d49696fe9ff346391a3136ac044d4722 (changed); task_tools.py 30da55a2…19dc (unchanged since r6); views r8/* (unchanged since r2).
- Claims file read by item id. Base copy is still verbatim. Mechanical sweep: 0 issues.
- What moved:
  - loan_ext_refi_payoff_quote: issue scope sentence; three replaced_by now scoped to "a refinance-purpose quote this policy issues"; day-rate split rewritten with `q_cancel_after`/`q_enroll_after` and four ordered tiers.
  - loan_ext_returned_fee: self-naming scope on the latest return's fee, with the base clause restated.
  - loan_ext_courtesy_waiver: scope = the latest late fee while no fee payment has posted; boundary rationale sentence.
  - Late fee, refi application and AutoPay: unchanged.

### round-7 RED closure (verified)
- **PLS-R7-1: closed.** The courtesy scope is now "the latest late fee charged on the loan … while no fee payment has posted against it", which equals the computed object (`c_fee_*` LATEST). Earlier late fees, returned-payment fees and a latest late fee already reached by a fee payment are named as staying under the restated base clause.
- **PLS-R7-2(a): closed (now an observation, R8-O1).** The boundary is stated with its business basis: a fee payment reaches a late fee only after accrued interest and older fees are paid, and base then clears the remainder in full. The marginal inversion remains (a borrower who has paid into the fee gets the whole remainder waived, while one who has not gets the share-based amount). But reaching the fee requires paying everything ahead of it in the allocation, so this is a lenient, stated choice, not an exploitable trick.
- **PLS-R7-2(b): closed.** The returned fee has a self-naming scope with the base clause restated verbatim. The catch-up charge at the schedule amount for an earlier, uncharged bounce is a recognisable practice.
- **PLS-R7-2(d): closed.** Four ordered tiers equal base loan_evt_autopay's per-day rate in force (r7 probe: +1.00 now in both rule and base; same-date tie handled). Two or more enrollments or cancellations after paid-through are routed, by an explicit record-countable scope, to the ordinary base quote, which is in-force base content.
- **PLS-R7-2(c): NOT closed — re-raised as PLS-R8-1 below.**

### findings (r8)
**PLS-R8-1 — SOURCE-POLICY RED (a scope condition stated by reference to a rule that applies only to the latest record; continues PLS-R7-2(c)). It affects neither task world; open charter-wide.**
- Scope: "This policy issues the refinance-purpose quote of a loan … on which no additional-principal payment other than the latest one is still on hold under the hold rule below".
- Hold rule: "An additional-principal payment that could still come back is held on the quote, looking at the latest payment of type additional_principal on the loan …: when that payment was made by online ACH …". Its every tier is about "that payment", the latest.
- So whether an earlier payment "is still on hold under the hold rule" has two readings:
  - (i) The hold tests (online ACH, not returned, 12-month returns → hold days) are applied to the earlier payment.
  - (ii) The hold rule only ever holds the latest payment, so no earlier payment is ever on hold under it, the scope condition is always met, and the r7 gap stays.
- Probe (copy of the task-0 world with a second online-ACH additional-principal payment of 100.00 on 10-19; principal 5886.36, paid-through 10-19):
  - Reading (ii): this policy's quote is 6037.77, holding 100.00 only.
  - Reading (i): the 400.00 of 10-16 is still on hold, so it is an ordinary base quote of 5912.06, good through 10-30, holding nothing.
- Under reading (i), adding a second uncleared payment removes every hold (500.00 uncleared, 0.00 held), which is the non-monotone realism problem of PLS-R7-2(c) in another form. Under reading (ii) the original gap (400.00 unheld) remains. Either way the class member is open.
- Class sweep (every scope or eligibility condition phrased through another rule): this is the only member.
  - The day-rate scope counts records directly ("at most one enrollment and at most one cancellation dated after its interest paid-through date").
  - The returned-fee scope names its object directly.
  - The courtesy scope names its object directly.
  - The refi application has no scope condition.

Observations (r8): R8-O1 (courtesy payment boundary, above); R4-O1, R3-O1, R2-O3, R2-O4 carried. No other XF class has a member after the whole-charter sweep.

## closing_checklist (revision_8)
Written after both revision_8 reveals (2026-10-17 03:21 UTC).
- Both tasks PASS all four relationships; derivation equals GT value for value (task 0: 6438.42 / 2026-11-09 / 6519; task 1: 9.30 / 8.58 / 9.19 / 8.37). Every tier label, edge copy and trace matches the current charter.
- PLS-R7-1 and PLS-R7-2(a), (b) and (d) are closed; (a) is carried as observation R8-O1. No regression.
- Remaining open (charter-wide, sole member of its class): **PLS-R8-1**. The payoff issue scope tests "still on hold under the hold rule" for earlier additional-principal payments, but the hold rule is defined only for the latest payment. That gives two readings (6037.77 vs 5912.06 on the probe), and under the reading that applies the hold tests to the earlier payment, a second uncleared payment removes every hold.
- Whole-charter sweep: no other XF class has a member.
- Gates: 7 OK per the snapshot; traceability not itemised, by instruction.

VERDICT revision_8: task0=PASS task1=PASS charter=PLS-R8-1

## revision_9

## charter_global_frozen (revision_9)
- Re-audit time 2026-10-17 (after rework round 9). Gate: worklog.md's last line is exactly `REWORK round 9: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 9`: EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK (pre-publication, not itemised; not run by me).
- Hashes: loan.extended.yaml 31c2c6bdf90f5d92ff13f5e58deee3593704a764118b39acbbce6a8ac59f3ee7 (changed); task_tools.py 30da55a2…19dc (unchanged since r6); views r9/* (unchanged since r2).
- Claims file read by item id. Base copy is still verbatim. Mechanical sweep: 0 issues. Factor counts unchanged (quote mmpp, refi mppppp, late mpppp, returned mppp, AutoPay mppp, waiver mppppp).
- What moved:
  - loan_ext_refi_payoff_quote: the issue-scope sentence now uses three record counts, with new bindings `q_pt_recent`, `q_enroll_2m`, `q_cancel_2m`, `q_extra_1m`, `q_issued` and `q_ordinary_interest`, and a branch in `result`.
  - The other five policies evaluate identically to r8 on both worlds.

### PLS-R8-1 closure (verified)
- Scope sentence: "This policy issues the refinance-purpose quote of a loan whose interest paid-through date is fewer than two whole calendar months before the quote date, whose AutoPay record shows at most one enrollment and at most one cancellation dated fewer than two whole calendar months before the quote date, and which has at most one payment of type additional_principal posted fewer than one whole calendar month before the quote date; … any other loan … is issued as an ordinary payoff quote under loan_evt_payoff_quote."
- This is record-countable and equals compute (`MONTHS(pt, NOW) < 2`; COUNT within_months 2 and 1). It no longer refers to another rule's selection.
- Coverage holds inside the scope:
  - Every AutoPay change after paid-through is dated after pt, so it is fewer than 2 whole months back, so the day-rate split's latest enrollment and latest cancellation describe every change.
  - Every payment that could still be held (a hold of at most 10 days) is fewer than 1 whole month back, so the latest additional-principal payment is the only candidate.
- Out-of-scope compute equals base loan_evt_payoff_quote: good through quote date + validity days, simple interest at the current rate from paid-through, principal + interest + fees.
- The r8 probe (second extra payment on 10-19) now has one reading: out of scope, ordinary quote 5912.06.
- Class sweep: every scope or eligibility condition in the six rules names its object or counts records directly. No member remains.
- **Closed.**
- Correction to my revision_8 text: there I also said that a busier loan falling back to the ordinary quote (and so holding nothing) kept the class open on realism. In the same revision I accepted the identical XF#11 route for PLS-R7-2(d), where a busier AutoPay record falls back to the ordinary quote, as in-force base content. Applied consistently, a scope boundary that routes to in-force base content is not an invented mechanic. The non-monotone outcome at the boundary (a second extra payment in the month means the quote holds nothing, as the base quote never holds) is recorded as observation R9-O1, not a RED. revision_8's text is left as written.

### findings (r9)
- No RED. Whole-charter sweep: no member of any XF class remains.
- Observations: R9-O1 (payoff scope-boundary non-monotonicity, as above, including two AutoPay changes in two months falling to the single-rate ordinary quote); R8-O1, R4-O1, R3-O1, R2-O3 and R2-O4 carried.

## closing_checklist (revision_9)
Written after both revision_9 reveals (2026-10-17 03:34 UTC).
- Per-task files: 0.md and 1.md, one per task, each with revisions 1–9 appended and none rewritten. Every comparison section of revision_9 is PASS.
- Coverage and scope: six extended policies; task 0 {refi_payoff_quote, refi_application}, task 1 {late_fee, returned_fee, autopay_enroll, courtesy_waiver}; pairwise disjoint and jointly complete. Task tools are closed against GT; each tool's uuid8 is independent and frozen.
- Trees:
  - Task 0: n = 1, 1 value_input edge, user write = the refinance application.
  - Task 1: n = 3, 3 value_input edges, user write = the AutoPay enrollment.
  - Both acyclic; the difficulty-wide prerequisite graph is a DAG.
- Factors: 4–6 per computation with ≥2 parameter and ≥1 method; each task has multi-source and cross-difficulty factors (task 0: line, builder; task 1: line, hardship, builder, pos). Every ladder has ≥ 3 distinct tiers stated in the rule. Every factor bears weight on its world against an honest baseline, and every all-baseline result is definite and differs from gold (6012.47 / 6637; 15.00 / 15.00 / 12.49 / 9.30).
- Derivation equals GT value for value (task 0: 6438.42 / 2026-11-09 / 6519; task 1: 9.30 / 8.58 / 9.19 / 8.37). Every tier label, edge copy and trace matches the current charter.
- Every RED of revisions 1–8 is closed. No XF_recipe class has a remaining member. Observations carried: R9-O1, R8-O1, R4-O1, R3-O1, R2-O3, R2-O4.
- Gates on the final form: the coordinator snapshot (round 9) shows EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK. TRACEABILITY NOT OK is pre-publication; not itemised this round per the brief (earlier rounds: unlock tool_name misses only).

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN

## revision_10

## charter_global_frozen (revision_10)
- Re-audit time 2026-10-17 (after rework round 10, driven by the renderer's source scan audits/render_source/personal_loan_servicing/render_r1.md, items 1–7). Gate: worklog.md's last line is exactly `REWORK round 10: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 10`: EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK (pre-publication, not itemised; not run by me).
- Hashes: loan.extended.yaml 901feccafa4f5c6a83944d02b3d201076a54c7269b93db86796a350c31bb1348 (changed); task_tools.py 30da55a2…19dc (unchanged since r6); views r10/* (unchanged since r2).
- Claims file read by item id. Base copy is still verbatim.
- Mechanical checks:
  - Sweep: 0 issues (quotes, bindings ↔ basis, baseline / replaced_by / policy_source in rule).
  - New: an AST check that no factor binding reads a binding owned by another factor: 0 hits in all six policies.
- What moved:
  - All six rules: the month convention restated in each counting sentence; day-count conventions restated; ladder text "fewer than N whole months".
  - Courtesy computation restructured: `courtesy_share_standard` 0.50; `c_form_start`, `c_form_kept`; share = start + points, clamped; result = MX(0, unpaid × share − kept).
  - Courtesy `c_fee_due` moved into return_reason_point.
  - AutoPay: an active-plan-rate scope with `a_plan_rate_active`; tier 2 "equalled or was above".
  - Returned fee: `f_ret_in_12m`.
  - Refi rounding wording; "personally, by phone".

### render_r1 items 1–7: closure (verified)
1. **Point factors gated through the waiver form — closed.** Each point now adds to the courtesy share, which the standard computation uses directly ("the unpaid part times the courtesy share, which is courtesy_share_standard"). Every point bears weight with the form at its baseline (task-1 world: 5.58 / 9.30 / 6.51 / 7.44 / 7.44 vs 8.37). The AST check confirms no factor reads another factor. But the restructure leaves the form factor a value selection; see PLS-R10-1.
2. **`c_fee_due` — closed.** It is now in return_reason_point's bindings, and it is the only reader. The remaining plain single-reader bindings (schedule figure, schedule amount, base rate) are baseline quantities.
3. **AutoPay departure from base — closed.** The rule states the scope: on a loan whose active hardship plan sets its own rate, "the rate in force from the enrollment date is the plan interest rate". `result` returns `a_plan_rate_active` in that case, which restates base loan_evt_autopay and loan_cmb_hardship_and_benefits. Tier 2 now reads "equalled or was above", which equals `>=`. Observation R10-O1: an active Term Extension Modification in trial carries a plan_interest_rate, while the hardship charter says interest "accrues at the current rate during the trial months". That is a base-versus-hardship-charter tension the blueprint owns; neither world has an active plan.
4. **Negative first-return count — closed.** `- (1 if f_ret_in_12m else 0)`, with the rule saying the same. No other count subtracts.
5. **Window boundary — closed.** The first-late and first-return sentences say "fewer than 12 whole calendar months", equal to within_months. The ladder sweep is confirmed.
6. **Shared convention sentence — closed.** Each counting sentence restates the convention, and each compute_basis is re-fitted (sweep clean).
7. **Wording edges — closed.** The ceiling is stated with its keep-as-is case; "personally, by phone" matches the tool docstring ("by phone").

### findings (r10)
**PLS-R10-1 — SOURCE-FACTOR RED (XF#9 / mislabelled effect: a factor labelled `method` whose tiers only select values in one fixed formula, so its computation is left with no genuine method factor). Members, complete list:**
- (a) **loan_ext_courtesy_waiver.courtesy_waiver_form (introduced in r10).**
  - The amount is MX(0, unpaid × MN(1, MX(0, start + Σ points)) − kept) for every tier. The tiers only pick (start, kept) ∈ {(courtesy_share_base 0.30, repeat_courtesy_retained_usd 5.00), (0.30, 0), (courtesy_share_standard 0.50, 0)}.
  - Tiers 2 and 3 differ only by 0.30 vs 0.50, which is the gate's own definition of `parameter` ("the tier selects a VALUE that enters an otherwise fixed formula").
  - Before r10 the three tiers were three shapes (share less a retained amount / share / the whole unpaid part).
  - With an honest label, the courtesy computation has 0 method factors (floor ≥ 1).
- (b) **loan_ext_autopay_enroll.modified_rate_base (pre-existing since r1).**
  - The rate is RND(rate base − (discount + steps)) for every tier. The tiers only pick the rate base ∈ {TEM rate + discount, TEM rate, base rate}.
  - That is a value entering a fixed formula, and specifically the acting base, which the gate's method definition says is "never selected by a tier".
  - With an honest label, the AutoPay computation has 0 method factors.
  - I accepted this factor as a method in revisions 1–9 (as "a rate-of-record choice"). That was wrong under the gate's own definition, which I am applying consistently now; earlier revisions are left as written.
- Non-members (each tier changes how the quantity is computed):
  - refi_sizing_form: withheld / add-on / no fee — three operations.
  - pay_cycle_form: a pro-rata ratio / a min-of-cap-less-offset / identity.
  - bank_event_form: a pro-rata ratio / subtract half a fee / identity.
  - day_rate_split: flat versus piecewise two-rate accrual with tier-selected segment endpoints (a day-count convention).
  - window_anchor_rule: the window anchored on the day before the due date / the end of the grace period / no anchor. The gate's method definition lists "the anchor the clock starts from".
- Bears on task 1 (both members' computations are scored there). Task 0's computations (quote: window_anchor_rule and day_rate_split; refi: refi_sizing_form) keep genuine method factors.

No other XF class has a member. Observations: R10-O1 (above); R9-O1, R8-O1, R4-O1, R3-O1, R2-O3, R2-O4 carried.

## closing_checklist (revision_10)
Written after both revision_10 reveals (2026-10-17 13:27 UTC).
- render_r1 items 1–7 are closed in the charter, each with its class swept: the factor-dependence AST check is clean, the window phrasing and conventions are clean in the charter, and the scoped AutoPay plan-rate case restates base.
- Derivation equals GT value for value in both tasks (task 0: 6438.42 / 2026-11-09 / 6519; task 1: 9.30 / 8.58 / 9.19 / 8.37; courtesy all-baseline 4.65). Every tier label is current.
- Not closed:
  - **PLS-R10-1** (charter-wide; bears on task 1): two `method` factors whose tiers only select values in one formula. courtesy_waiver_form was introduced by the r10 restructure; modified_rate_base is pre-existing and I mis-accepted it in r1–r9. This leaves the courtesy and AutoPay computations with no genuine method factor.
  - XF#14 stale proof text: 4 members in task 0 and 5 in task 1. The r10 phrasing changes ("fewer than N whole months", "personally, by phone") were not swept into the task files' traces, tracing and necessity text.
- Gates: 7 OK per the snapshot; traceability not itemised, by instruction.

VERDICT revision_10: task0=RED SOURCE-FACTOR,SOURCE-TASK task1=RED SOURCE-FACTOR,SOURCE-TASK charter=PLS-R10-1

## revision_11

## charter_global_frozen (revision_11)
- Re-audit time 2026-10-17 (after rework round 11). Gate: worklog.md's last line is exactly `REWORK round 11: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 11`: EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK (pre-publication, not itemised; not run by me).
- Hashes: loan.extended.yaml eb80c190dbc6ce99d2a87ed2bf1efeebf7dd3f8aa9b07b15528f1b7daa6de397 (changed); task_tools.py 30da55a2…19dc (unchanged since r6); views r11/* (unchanged since r2).
- Claims file read by item id. Base copy is still verbatim. Sweep and factor-reads-factor AST check: 0 issues. Factor counts: quote mmpp, refi mppppp, late mpppp, returned mppp, AutoPay mppp, waiver mppppp.
- What moved:
  - Courtesy: the waiver form is now three operations on the unpaid part (less the keep-back, never below zero / times repeat_courtesy_fraction 0.90 / the whole unpaid part). The share is courtesy_share_base plus points, clamped. Amount = form figure × share. courtesy_share_standard was removed.
  - AutoPay: modified_rate_base is replaced by enrollment_rate_form:
    - tier 1: completed TEM → MX(floor, standard − (pre-plan − plan rate)), floor from CPARAM;
    - tier 2: an AutoPay return fewer than 3 months back → base − grade discount;
    - tier 3: standard rate.
  - Proof text in both task files.

### PLS-R10-1 closure (verified)
- (a) courtesy_waiver_form: **closed.** Subtract-and-floor, scale, and identity are three different operations. This is the same standard as bank_event_form and pay_cycle_form. The points add to a share defined in the computation document and act on the standard amount by themselves (task 1: each point's baseline moves the waiver), so render item 1 does not regress. Monotone over every reachable fee (≤ 30.00): u − 5 < 0.9u < u.
- (b) enrollment_rate_form: **closed as to the label.** Its tiers are three operations (floored subtraction of a record-derived reduction / a different discount set / standard), not a value pick into one formula. It is task 1's only AutoPay method factor and bears weight there (9.19 vs 12.19 under its baseline). But see PLS-R11-1.
- render_r1 items 1–7: no regression (factor-read AST clean; c_fee_due still in return_reason_point; windows say "fewer than"; conventions restated; plan-rate scope intact; wording edges intact).

### findings (r11)
**PLS-R11-1 — SOURCE-POLICY RED (XF#3 "no factor names another factor", the render-item-1 class: one factor's tier switches the other factors off by naming them). Introduced in r11; it does not bear on either task world's scored values; open charter-wide.**
- enrollment_rate_form tier 2: "when an AutoPay debit on the loan was returned fewer than 3 whole calendar months … before the enrollment date, **the AutoPay discount steps are withheld** and the rate in force is the loan's base interest rate less the grade's AutoPay discount alone".
- The tier names the three step factors' quantities (loan_age_step, debit_record_step, credit_builder_autopay_step) and nullifies them. The step documents ("… adds autopay_step_…") and the rate-form document cannot each stand alone: in a tier-2 world they contradict unless the form document names the steps.
- Probe (copy of the task-1 world with the completed TEM removed, so the 2026-09-08 AutoPay return puts the form on tier 2):
  - The rate is 12.49.
  - Each step factor's baseline gives 12.49, so all three step factors bear no weight in that world.
- Class sweep (every method tier that disables or names parameter factors):
  - The only member is the one above.
  - Non-members (none names another factor; each either uses the shared quantity or caps the result):
    - refi_sizing_form tier 1 ("the amount financed is the payoff to be covered" — the fee percent is simply not used).
    - The AutoPay tier-1 floor (a cap on the result).
    - The courtesy form tier 1 floor at 0, pay_cycle_form tier 2 at 0, bank_event_form tier 2 at 0 (zero edges of a figure).
- Affected: loan.extended.yaml loan_ext_autopay_enroll rule (rate-form sentence, tier 2), factors[enrollment_rate_form].ladder[1], compute `result` branch `a_rate_form == 2`.

No other XF class has a member. Observations carried: R10-O1, R9-O1, R8-O1, R4-O1, R3-O1, R2-O3, R2-O4.

**PLS-R11-2 — SOURCE-POLICY RED (XF#4 / XF#14: charter text made stale by the r11 change). Members, complete list:**
- loan_ext_autopay_enroll overwrite[0].replaced_by and its verbatim copy in the rule: "For an enrollment this policy sets, and only for such an enrollment, the rate in force from the enrollment date is **the rate base** less the AutoPay discount as set below".
- No "rate base" is set below any more. The rule now defines "the standard rate" (base rate less the grade discount and every step) and the "enrollment rate form".
- A reader of the overwrite looks for a rate base that does not exist and has two candidates: the base interest rate, or the standard rate before the form.
- Sweep of the whole charter for every quantity removed in r10/r11 ("rate base", "courtesy_share_standard", "starts from"): this sentence is the only hit.
- Task-file counterpart: tasks/1.json evaluation_criteria[6].necessity (see 1.md).

## closing_checklist (revision_11)
Written after both revision_11 reveals (2026-10-17 14:01 UTC).
- Derivation equals GT value for value: task 0 6438.42 / 2026-11-09 / 6519; task 1 9.30 / 8.58 / 9.19 / 7.53.
- PLS-R10-1 (a) and (b) are closed; r10 XF#14 members in both task files are closed; render_r1 items 1–7 do not regress.
- Open:
  - **PLS-R11-1**: enrollment_rate_form tier 2 names and switches off the step factors.
  - **PLS-R11-2**: the stale "rate base" in the AutoPay overwrite and its rule copy.
  - Task 1's stale necessity line (same term).
- Gates: 7 OK per the snapshot; traceability not itemised, by instruction.

VERDICT revision_11: task0=PASS task1=RED SOURCE-TASK charter=PLS-R11-1,PLS-R11-2

## revision_12

## charter_global_frozen (revision_12)
- Re-audit time 2026-10-17 (after rework round 12). Gate: worklog.md's last line is exactly `REWORK round 12: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 12`: EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK (pre-publication, not itemised; not run by me).
- Hashes: loan.extended.yaml 616075d9d73eca17f9a3067e9f2b7c34c69a236a74155af05c2f305019d90334 (changed); task_tools.py 30da55a2…19dc (unchanged since r6); views r12/* (unchanged since r2).
- Claims file read by item id. Base copy is still verbatim.
- Mechanical checks:
  - Sweep: 0 issues.
  - Factor-reads-factor AST check: 0.
  - Ladder-names-another-factor scan: 0.
  - Charter retired-term scan ("rate base", "courtesy_share_standard", "starts from", "withheld", "looking only at", "waivable", "fees balance", "credited", "installment debit"): 0.
- What moved: loan_ext_autopay_enroll only. The overwrite replaced_by and its rule copy are reworded; enrollment_rate_form tier 2 is now `MN(base rate, standard + autopay_return_surcharge_percent 0.25)`; the ladder text is updated.

### round-11 RED closure (verified)
- **PLS-R11-1: closed.**
  - Tier 2 no longer names or disables the step factors. It adds its own surcharge to the standard rate, capped at the base interest rate, which keeps the rate within the contract rate (XF#12).
  - The three tiers are three operations: floored reduction, capped surcharge, standard.
  - Round-11 probe (task-1 world with the TEM removed): rate 12.44. Each step's baseline gives 12.54, so every step bears weight. The rate-form baseline gives 12.19.
  - The cap binds only when the steps total 0 on a grade whose discount equals the surcharge (D–G, 0.25), so it never hides a non-zero step.
- **PLS-R11-2: closed.** The replaced_by and its rule copy now read "the rate in force from the enrollment date is the one set below from the loan's base interest rate, the grade's AutoPay discount and the AutoPay discount steps"; no "rate base" remains anywhere in the charter.
- render_r1 items 1–7 and PLS-R10-1: no regression (scans above; method shapes unchanged in the other five policies).

### findings (r12)
No RED. No member of any XF_recipe class remains. Observations carried: R10-O1, R9-O1, R8-O1, R4-O1, R3-O1, R2-O3, R2-O4.

## closing_checklist (revision_12)
Written after both revision_12 reveals (2026-10-17 14:20 UTC).
- Per-task files 0.md and 1.md, one per task, with revisions 1–12 appended and none rewritten; every revision_12 comparison is PASS.
- Coverage: six extended policies. Task 0 {refi_payoff_quote, refi_application}; task 1 {late_fee, returned_fee, autopay_enroll, courtesy_waiver}. Pairwise disjoint and jointly complete. Task tools are closed against GT, with independent frozen uuid8s.
- Trees:
  - Task 0: n = 1, 1 value_input edge, user write = refinance application.
  - Task 1: n = 3, 3 value_input edges, user write = AutoPay enrollment.
  - The difficulty-wide graph is a DAG.
- Factors:
  - Every computation has 4–6 factors, ≥ 2 parameter, and ≥ 1 genuine method (quote: window_anchor_rule, day_rate_split; refi: refi_sizing_form; late: pay_cycle_form; returned: bank_event_form; AutoPay: enrollment_rate_form; courtesy: courtesy_waiver_form).
  - Each task has multi-source and cross-difficulty factors (task 0: line, builder; task 1: line, hardship, builder, pos).
  - Every ladder has ≥ 3 distinct tiers stated in the rule. No factor reads or names another factor. Every factor bears weight against an honest baseline.
  - All-baseline results are definite and differ from gold: 6012.47 / 6637; 15.00 / 15.00 / 12.49 / 2.79.
- Derivation equals GT value for value: task 0 6438.42 / 2026-11-09 / 6519; task 1 9.30 / 8.58 / 9.19 / 7.53. Every tier label, edge copy and trace matches the current charter.
- Every RED of revisions 1–11 is closed, render_r1 items 1–7 included. No XF_recipe class has a remaining member. Observations carried: R10-O1, R9-O1, R8-O1, R4-O1, R3-O1, R2-O3, R2-O4.
- Gates on the final form (coordinator snapshot, round 12): EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK is pre-publication, not itemised per the brief.

VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN

## revision_13

## charter_global_frozen (revision_13)
- Re-audit time 2026-10-17 (proof-only round for KB-audit source note S4). Gate: worklog.md's last line is exactly `REWORK round 13: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 13`: EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE / **TRACEABILITY OK** — all eight gates green (docs published).
- Hashes:
  - loan.extended.yaml 616075d9d73eca17f9a3067e9f2b7c34c69a236a74155af05c2f305019d90334 = revision_12.
  - task_tools.py 30da55a2b8320d8e394a8ca0188196b69e0587e2ee390d156207b6dc256e19dc = revision_12.
  - Views r13/task_0.json 3cb6a76f… and r13/task_1.json e487e4b5… = revision_12.
- All charter-global sections of revision_12 carry forward by hash; nothing they rest on moved.

### S4 closure (verified)
- KB-audit source note S4 was a wrong intermediate product in task 1's late-fee trace (stated 9.2970, true 9.3024). It is now stated against the unrounded pay-cycle figure: 12.462745 × 0.90 × 0.90 × 0.95 × 0.97 = 9.3024 (true 9.30238). The same-pattern returned-fee product reads 8.5806 (true 8.58060).
- Class: a mechanical recomputation of every inline operator chain in both task files (traces, tracing, necessity, dossiers, closure, solvability text) found no other wrong figure. The two flags it raised are parser artifacts that check out by hand.
- Nothing else changed: scored arguments, expected values, baselines, factor-sensitivity figures, tier labels, edge copies and skip figures are identical to revision_12 in both tasks.

## closing_checklist (revision_13)
- Unchanged from revision_12's checklist (same charter, tools and worlds); every comparison of revision_13 is PASS.
- All eight instantiation gates are now OK on the final form, traceability included.
- No RED open; no XF_recipe class member. Observations carried: R10-O1, R9-O1, R8-O1, R4-O1, R3-O1, R2-O3, R2-O4.

VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN

## revision_14

## charter_global_frozen (revision_14)
- Re-audit time 2026-10-17 (seed-only rework for KB re-judge items S5–S10 plus a self-check of loan rows). Gate: worklog.md's last line is exactly `REWORK round 14: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 14`: all eight gates OK (EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE, TRACEABILITY).
- Hashes:
  - loan.extended.yaml 616075d9d73eca17f9a3067e9f2b7c34c69a236a74155af05c2f305019d90334 and task_tools.py 30da55a2b8320d8e394a8ca0188196b69e0587e2ee390d156207b6dc256e19dc — byte-identical to revision_13, so every charter-global section carries forward by hash.
  - Views changed: r14/task_0.json 0be027a20d2cbf9b…, r14/task_1.json 4fc2e9d668fa8692….

### seeded cross-product and own rows vs their rules (verified; sources docs/line, docs/pos, blueprint/products/{line,hardship,pos,loan}.yaml)
- **FlexLine ledgers (both tasks), S9 class.** I replayed them by script.
  - All 21 + 22 interest charges equal the average daily balance × 25.24% / 365 over the cycle (day after the prior closing through the closing, closing 25 days before the due date), to the cent.
  - Every minimum payment equals 3% of the statement balance with the 35.00 floor.
  - Draw fees are 2.5% (30.00, 22.50; 37.50, 15.00).
  - Annual fees of 39.00 fall on the first anniversary (Standard does not waive the first year: 2025-11-18; 2026-01-15).
  - Record balances, minimums, past-due amounts and next due dates equal the ledgers (task 1: 116.52 = 59.03 + 57.49 past due; task 0: 56.69, nothing past due).
  - Task 0's missed 2025-08-10 minimum is no longer paid; the catch-up 51.99 = 44.82 past due + 7.17 late fee.
- **S5, task 1 FlexLine late fee, 2026-09-16.** Unpaid 57.49 at 11 days late gives 25% = 14.37. Shares: balance tier 0.80 (about 1,967), grace payment 1.00, history 0.80, tenure 1.00 (21 months). Result 9.1968 → 9.20. Seeded 9.20.
- **S7, task 0 FlexLine late fee, 2025-08-21.** 25% × 44.82 = 11.205 → 11.20 (half-even). Shares: balance 0.80, grace 1.00, history 0.80, tenure 1.00. Result 7.168 → 7.17. Seeded 7.17.
- **S6, task 1 FlexLine returned fee, 2026-09-08.** R02 on 57.49 gives the flat 15.00. Shares: history 0.85 (only return in 24 months), late-booking 1.00, shared event 0.90 (loan return the same day, no loan fee booked that day), tenure 1.00. Result 11.475 → 11.48 (half-even). Seeded 11.48.
- **S8, task 1 PracticePay late fee, 2025-03-05, due 2025-02-22.** Level 20.00 (no earlier plan late fee). Shares: FlexLine 0.95 (active line, no line late fee or return in 12 months), personal loan 1 (loan late fee 2024-12-21 within 12 months), principal band 0.90 (1,400 left), partial payment 1 (nothing credited by assessment). Result 17.10, matching the seed; the 03-06 payment of 217.10 covers it and the plan pays to 0 on 2025-07-22.
- **S10, hardship dates.**
  - Task 0 STPD: decision 2026-01-12 + 10 acceptance days gives a last day of 01-22, so it expires 2026-01-23 (hardship_evt_acceptance).
  - Task 1 TEM: completed 2024-05-05, the day of the last trial payment.
- **Own loan rows.** Task 0's old loan late fee: 5% of 314.15 = 15.7075 → 15.71 (base schedule_a, min 15, max 30). Its current rate is 15.49, the base rate, since AutoPay ended at payoff. Task 1's installments were already verified as level payments (r1).
- **Effects on the trees and factors.**
  - Every prerequisite is still unmet at the opening.
  - Every edge and factor bears weight on both worlds.
  - Sibling writes are independent.
  - Task 0's FlexLine credit is unaffected (the line late fee is still 13 months back).
  - In task 1 the larger bounced minimum (57.49) moves the pay-cycle and bank-event ratios and hence the scored late fee, returned fee and waiver.

## closing_checklist (revision_14)
- As in revision_12/13 (same charter and tools). Both tasks PASS all four relationships on the corrected worlds; derivation equals GT value for value (task 0: 6438.42 / 2026-11-09 / 6519; task 1: 9.26 / 8.54 / 9.19 / 7.50).
- Every seeded row checked conforms to its product's rules.
- All eight gates OK. No RED open; no XF_recipe class member. Observations carried: R10-O1, R9-O1, R8-O1, R4-O1, R3-O1, R2-O3, R2-O4.

VERDICT revision_14: task0=PASS task1=PASS charter=CLEAN

## revision_15

## charter_global_frozen (revision_15)
- Re-audit time 2026-10-17 (proof-only fix of KB-confirm item S11). Gate: worklog.md's last line is exactly `REWORK round 15: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh personal_loan_servicing 15`: all eight gates OK.
- Byte-identity with revision_14:
  - loan.extended.yaml 616075d9d73eca17…
  - task_tools.py 30da55a2b8320d8e…
  - r15/task_0.json 0be027a20d2cbf9b…
  - r15/task_1.json 4fc2e9d668fa8692…
  - Every charter-global section and the revision_14 seed verification carry forward by hash.

### S11 closure (verified)
- Task 1's courtesy trace, amount tracing and dossier now state the waiver form's figure unrounded (8.334), as compute keeps it. 8.33 is only ever a rounded final result.
- The same-class instances (the pay-cycle and bank-event figure 12.405374 in late-fee and returned-fee lines) are stated unrounded.
- A mechanical sweep of both task files (every operator chain recomputed; every stated intermediate compared with its later uses) finds 0 mismatches and no precision inconsistency.
- No scored value, baseline, tier label, edge copy or skip effect moved.

## closing_checklist (revision_15)
As in revision_14. Both tasks PASS all four relationships (task 0: 6438.42 / 2026-11-09 / 6519; task 1: 9.26 / 8.54 / 9.19 / 7.50). All eight gates OK. No RED open; no XF_recipe class member. Observations carried: R10-O1, R9-O1, R8-O1, R4-O1, R3-O1, R2-O3, R2-O4.

VERDICT revision_15: task0=PASS task1=PASS charter=CLEAN
