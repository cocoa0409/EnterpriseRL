# Policy-task audit — hospital_account_billing / charter-global

## revision_1

## charter_global_frozen
- Frozen: 2026-10-20 14:18 UTC (written before any task GT was revealed). Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiating agent.
- Freeze hashes (sha256, first 12): `encounter.extended.yaml` eb37e581bd73, `task_tools.py` 628f4918fc24, base `blueprint/products/encounter.yaml` 075330ee128a. They match the coordinator's gate snapshot.
- Entry evidence (Step 0): the gate snapshot came with the brief. EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Traceability runs after rendering. Masked views are `.audit_views/policy/hospital_account_billing/r1/{0,1}.view.json`. Their hashes match the brief (ca5c599b1b35ecc0, c75cee57cf513f6b). Entry conditions are complete.
- Read for this section: blueprint.yaml, db_schema.json, products/encounter.yaml (base), products/claim.yaml and products/estimate.yaml (owning charters of the cross-read records), the extended charter, task_tools.py, audits/render_source/XF_recipe.md, and the DSL primitives in skills/erl-task-instantiate/scripts/check_compute.py (semantics only).
- Masked and not read: everything in tasks/*.json except through the views, worklog.md, /tmp/*_0073/.
- Base copy check: lines 1-995 of the extended file are byte-identical to products/encounter.yaml. The only difference is the extended header comment.
- Mechanical sweeps (scratch script, /tmp/audit_0073_policy): every `compute_basis` quote, every `policy_source`, every `baseline.rule` and every `replaced_by` is a verbatim substring of its own policy's rule. Every `superseded_clause` is a verbatim sentence of the named base rule.

### policy_conflict_scan
Charter content: six extended policies.
- p1 = encounter_ext_noncovered_discount
- p2 = encounter_ext_insured_payoff
- p3 = encounter_ext_terminated_coverage_discount
- p4 = encounter_ext_charge_correction
- p5 = encounter_ext_service_recovery_courtesy
- p6 = encounter_ext_selfpay_payoff

Overlapping subjects:
- p1 and p3 both post `UNINSURED_DISCOUNT` adjustments. They are separated by the source posting's `liability_source`: p1 handles NONCOVERED_SERVICE on an insured account, p3 handles COVERAGE_TERMINATED on an account corrected to SELF_PAY. Each of their sibling overwrites of the same base clause names the other's case as outside it (XF 16 holds).
- p2 and p6 both post `PROMPT_PAY_DISCOUNT` and a patient payment. They are separated by financial_class (p2: anything but SELF_PAY; p6: SELF_PAY). Each excludes the sibling's case by name. Together they cover every account, so the retired base clause has no out-of-scope residue.
- p4 posts CHARGE_CORRECTION_ADJUSTMENT and p5 posts SERVICE_RECOVERY_COURTESY. Neither overlaps another policy.

Triggers, time anchors and terminal states:
- p2 and p6 inherit the base prompt-pay window, minimum balance, channel, FAP and payment-plan exclusions, which are not overwritten.
- p5 inherits the base once-per-patient-per-calendar-year limit ("Only one courtesy adjustment is allowed per patient per calendar year across all accounts."), which is not overwritten.
- Conflicts found are listed under findings: C1 (prerequisite gates against p1/p4/p5 scopes and against base S5/base insured-credit/base per-year limit), C4 (p4 against base encounter_late_charges) and C5 (p4's package tier).

Cross-category read boundaries:
- p1 reads claim (PR-204 remit_date, the PRIMARY claim's prior_auth_number and adjudication_date) and estimate (issued_date).
- p2 reads claim (submitted/adjudication dates, payer_clean_claim_days, correction rows) and estimate (estimate_total_usd, issued_date, scheduled_service_date, variance_review_pct).
- p3 reads claim (variant, denial_carc, group_number, denial_date).
- All read fields exist in db_schema. CPARAM payer_clean_claim_days (claim, 30 for every class) and variance_review_pct (estimate, Insured variant 15.0) exist.
- Cross-charter tension: see O4.

Scope exclusivity and completeness: from the prerequisite graph, the charter splits into two components, {p1→p2} and {p3→p4→p5→p6}. With M=2 and one tree per task, the two scopes are disjoint and together cover all six policies. The claimed scopes are masked. This structural reading is confirmed per task in each task file.

### rule_compute_equivalence
Every quantity, window, tier, branch, cap and rounding point has a verbatim `compute_basis` quote, and compute invents no basis of its own. Same-day ties are stated wherever a LATEST is taken: p1 twice, p2 paperless, p3, p4, p5 inquiry, p6 channel. The DSL's LATEST keeps the first row in file order on equal keys (check_compute.py LATEST uses `key > best`). Month counts: none (no MONTHS used). Every factor ladder tier is a rule sentence and a branch of its `decides` binding, and the reverse also holds.

Exceptions:
- **Rule and compute disagree on absent or second records (C2, C3).**
  - p2 `ins_estimate_credit` with an empty `scheduled_service_date`: `ins_est_issued > ins_est_service` is a string comparison against '', which is True, so compute gives the $25 late-estimate credit. The rule only says "when that estimate's issued_date is after its scheduled_service_date", which cannot be evaluated against an empty date and falls to "otherwise … nothing".
  - p1 and p2 read "the account's PRIMARY claim" through CFIELD, which takes the first row in file order. The rule gives no selector when a rebilled account carries two PRIMARY claims.
- **Rounding (observation O3).** Every rule says "rounded half-up". RND is Python `round(float(x), n)`, which can differ from half-up on a binary-float cent tie. This is framework-wide. No figure of either task falls on a tie (checked per task).

### action_binding_and_uuids
- Each `(target_tool, computes)` pair is claimed by exactly one policy: p1 post_noncovered_line_discount_93cdc726, p2 pay_insured_balance_in_full_a10a8aeb, p3 post_terminated_coverage_discount_f939a41d, p4 post_charge_correction_adjustment_10e5aff9, p5 post_service_recovery_courtesy_69e36558, p6 pay_self_pay_balance_in_full_3917aa11. All use `computes: amount`.
- uuid8s: 93cdc726, a10a8aeb, f939a41d, 10e5aff9, 69e36558, 3917aa11. None is reused, and none shares a prefix or forms a sequence.
- Tool bodies: each body only creates and updates rows. None checks eligibility, order or any prerequisite. Every write tool calls ctx.create/update itself.
- Imports: no datetime/time/random/uuid/secrets imports.
- Factor ids: none is a substring of a tool name.
- Docstrings: no example values and no composite arguments. No docstring names another tool.
- XF 23: the events written (encounter_adjustment_posted, encounter_payment_posted, the encounter_closed status update) all have base `triggers: []`.
- Observations: O5 (the word "follows" in the p4 docstring) and O6 (encounter_closed is outside the claimed event_types).

### prerequisite_graph
- `prerequisite` is filled for every policy: p1 [], p3 [].
- Edges:
  - E1: p1 → p2, gate ins_balance
  - E2: p3 → p4, gate cr_netted_pct
  - E3: p4 → p5, gate cc_start
  - E4: p5 → p6, gate sp_balance
- All four edges are `kind: value_input`, `form: state`, with no fallback_reason. Every gate is a binding that exists in the blocked policy's compute. `resolved_by` equals the depended-on policy's target_tool.
- The graph is acyclic: two chains, no cross-task reference.
- Every policy_source is verbatim in the blocked rule.
- **Conditions are broader than the depended-on policy can satisfy (C1).** The four `condition` texts are universal ("every … posting/credit …"), and so are the sentences. C1 lists where each cannot be met.
- E3 `effect` ("cc_start moves from service_recovery_courtesy_max_usd to error_share of the corrected error") describes only the ≥ large_error_usd tier. Below that threshold the start moves to small_error_usd (observation O7).

### prerequisite_sentences
Four-point test on each edge:
1. Ordering connective: "fixed only after", "not fixed until", "not fixed until", "fixed only after".
2. State in record words: NONCOVERED_SERVICE posting + UNINSURED_DISCOUNT; SELF_PAY_FINAL_BILL/COVERAGE_TERMINATED posting + UNINSURED_DISCOUNT; charge credit + CHARGE_CORRECTION_ADJUSTMENT; corrected charge credit + SERVICE_RECOVERY_COURTESY.
3. No tool name, policy id or snake_case token appears.
4. Strength: see C1.

Single resolving write per state-form edge:
- E1: the state "a NONCOVERED_SERVICE posting carries its uninsured discount" is produced only by p1's write. p3's tool body is identical, but p3's rule excludes NONCOVERED_SERVICE postings by name, so the reader reaches p1 alone.
- E2 for a COVERAGE_TERMINATED posting: p3 alone. For a SELF_PAY_FINAL_BILL posting no write of this difficulty exists; the base trigger posts it.
- E3: p4 alone.
- E4: p5 alone.

Derivations a reader follows:
- p2's sentence → the records show an undiscounted NONCOVERED_SERVICE posting → the rule that prices it is p1 → post p1, then figure p2.
- p6's sentence → a corrected charge credit without a courtesy → p5's rule. p5's sentence → a charge credit without a correction → p4's rule. p4's sentence → a COVERAGE_TERMINATED posting without a discount → p3's rule.

Other checks:
- No rule carries a second wording of its dependency, and no depended-on rule restates the sentence.
- Docstrings are silent about sequence (but see O5).
- No base sentence grounds an edge.
- p6's replaced_by/rule phrase "on the balance remaining after the uninsured discount" states an order toward the uninsured discount that grounds no declared edge. It is transitively implied by E2→E3→E4 in the only tree that contains p6, so no two admissible orders exist (observation O8).

### override_declarations
Checked sentence by sentence against every `base_policy_refs` entry.

**p1** (scored: the UNINSURED_DISCOUNT amount on a NONCOVERED_SERVICE posting)
- encounter_uninsured_discount:
  - S1 "applies only when … SELF_PAY at final bill": overwritten, declared.
  - S2 (SELF_PAY_FINAL_BILL percents): followed. It does not govern NONCOVERED_SERVICE postings.
  - S3 "On an insured account … receives the same uninsured_discount_pct …": overwritten, declared. The base value would be uninsured_discount_pct × amount.
  - S4 half-up rounding: followed.
  - S5 package: no conflict on insured accounts.
  - S6 FAP: untouched.
- The other refs (prompt-pay, dispute, courtesy, rebill) are untouched by p1. Clean.

**p2** (scored: the payment amount)
- encounter_prompt_pay_discount:
  - P1 single full payment: followed.
  - P2/P3 window and counting: in force.
  - P4 "The discount is prompt_pay_discount_pct of …": overwritten, declared, scoped to non-SELF_PAY.
  - P5 exclusions: in force.
  - P6 partial/once: in force.
- encounter_agg_payment_application (designated payment, card cap): followed.
- encounter_small_balance_and_courtesy: not reached.
- encounter_final_bill_and_liability: followed.
- Clean.

**p3** (scored: the UNINSURED_DISCOUNT amount on a COVERAGE_TERMINATED posting)
- encounter_uninsured_discount S1: overwritten, declared. S2's percent split (elective / other) is carried.
- encounter_coverage_update_rebill "Coverage reported as terminated … posts as COVERAGE_TERMINATED liability": followed.
- Clean.

**p4** (scored: the CHARGE_CORRECTION_ADJUSTMENT amount)
- encounter_charge_dispute_and_correction correction sentence: overwritten, declared. Its other sentences (window, authority, once per reason) are about the credit, not the correction, and are followed.
- **Undeclared conflict with encounter_late_charges (C4).** That policy is not in p4's base_policy_refs. The finding is recorded here because it is a conflict on the scored quantity.
- encounter_uninsured_discount S5 package: see C5.

**p5** (scored: the SERVICE_RECOVERY_COURTESY amount)
- Both overwrites are declared.
- The per-calendar-year sentence is in force and not overwritten. It bears on E4 (C1).
- The small-balance sentence is followed.

**p6** (scored: the payment amount)
- The prompt-pay P4 overwrite is declared and scoped to SELF_PAY.
- The other prompt-pay sentences are in force.
- On base P6 "A partial payment never earns a partial discount": p6's `earlier_payments` raises the payoff percent because of earlier partial payments. These are not literally the same quantity, so there is no override finding. It is recorded under C7 realism.

### factor_ladders
Declared counts:

| policy | factors | parameter / method | multi-source | cross-difficulty |
| --- | --- | --- | --- | --- |
| p1 | 6 | 5 / 1 (noncoverage_notice_lag) | site_of_service, authorization_on_record (tier 2) | noncoverage_notice_lag (claim), authorization_on_record (claim + estimate) |
| p2 | 6 | 5 / 1 (estimate_variance_relief) | claim_lag_allowance, estimate_variance_relief | claim_lag_allowance (claim), estimate_variance_relief (estimate) |
| p3 | 6 | 5 / 1 (observation_day_rate) | arrival_through_emergency, observation_day_rate | lost_plan_type (claim), coverage_loss_notice (claim) |
| p4 | 4 | 3 / 1 (credit_age) | dispute_resolution_path | none |
| p5 | 4 | 3 / 1 (corrected_error_size) | hold_and_dispute | none |
| p6 | 5 | 4 / 1 (window_days_left) | none | none |

Structure checks:
- Every ladder has 3 tiers including the fall-through, and they are disjoint as stated.
- Every fall-through equals the policy baseline: '0' for additive factors, cr_std_pct for p4 netted, the courtesy max for p5 start.
- Every `decides` binding is an input, never `result`. Binding sets are disjoint.
- Every tier is stated in the rule and implemented in compute.
- XF 14 method structural test passes for all six method factors. Each pairs an input-reading tier (linear in lag/age/days left, proportional to excess/error, per-diem floor) with a flat tier and a nothing tier, and no tier is identically 0 over its domain.
- XF A1: no factor reads another factor's binding. Shared reads are plain bindings or baseline bindings (td_std_pct, cr_credit, cr_source).
- XF A3: the assembly sentence is generic and fixes the order.

Defects in structure and realism:
- **XF A4 gating (C6).** p5's three dollar factors can move the result only when corrected_error_size is off its fall-through.
- **Unreal ladders (C7)**, 12 members.
- **Counts after strikes (C8).**
- Label note (O2): p4 netted_discount_on_file is labelled parameter but its tier 2 is a ledger ratio. Its value enters the formula as a percent, so this is not recorded as a mislabel.

Realism review of the ladders that pass:
- p1 noncovered_size_band, deductible_burden. The IRS 2026 self-only HDHP minimum deductible is $1,700, which is correct.
- p2 days_to_pay_schedule, liability_size_band.
- p3 arrival_through_emergency, coverage_loss_band, observation_day_rate. A self-pay per-diem for observation hours is a real pricing device.
- p4 netted_discount_on_file. Netting the discount actually applied, and treating a package price as fixed, is what base intends.
- p5 corrected_error_size, hold_and_dispute, error_duration. Severity-scaled service recovery is plausible as Riverbend's own schedule.
- p6 gross_standing_band, statement_recency, window_days_left.

Borderline, kept as observations (O1): p2 paperless_allowance, p6 self_pay_e_statement, p2 check_in_payment_allowance, p1 site_of_service.

### findings

**C1 — SOURCE-POLICY RED: prerequisite sentences and conditions are universal over records the depended-on policy never serves.**

Symptom: each state-form gate demands that "every" record carry a write which the depended-on policy, or an in-force base sentence, withholds from some records. On those records the blocked policy can never be fixed.

Root cause: the sentences and conditions are written over all records of a kind, not over the records the depended-on policy serves.

Members:
- **E1 (p2).** Sentence: "The insured payoff amount is fixed only after every non-covered-service liability posting on the account carries its uninsured discount."
  - p1: "a NONCOVERED_SERVICE liability posting receives an uninsured discount only on patient classes whose uninsured_discount_on_noncovered_insured is true". The flag is false for Outpatient Surgery, Observation Stay and Inpatient Admission.
  - Situation: a COMMERCIAL Outpatient Surgery account with a NONCOVERED_SERVICE posting, whose patient pays in full inside 45 days.
  - p2 reading: the payoff is never fixed (no solution). The other reading prices it anyway, against the sentence.
- **E2 (p4).** Sentence: "The charge-correction amount is not fixed until every self-pay or coverage-terminated liability posting on the account carries its uninsured discount."
  - Base S5: "An account priced under a Riverbend self-pay package receives the PACKAGE_PRICE_ADJUSTMENT instead and never the uninsured discount."
  - On a package account the SELF_PAY_FINAL_BILL posting never carries one, so p4 is never fixed. Yet p4's own first tier ("When the account carries a PACKAGE_PRICE_ADJUSTMENT, the netted discount percent is 100") exists only for such accounts and is unreachable.
  - No write of this difficulty produces the waited-on state for a SELF_PAY_FINAL_BILL posting; the base system trigger does.
- **E3 (p5).** Sentence: "The courtesy is not fixed until every charge credit on the account carries its charge-correction adjustment."
  - Base: "On an insured account the credit produces a corrected claim to the payer and no patient-balance adjustment until the payer re-adjudicates."
  - p4: "an insured account is outside this sentence".
  - p5 owes a courtesy on any account with "a billing error already corrected on the account", insured accounts included. On an insured account with a charge credit, the courtesy can never be fixed.
- **E4 (p6).** Sentence: "The self-pay payoff amount is fixed only after the account carries the service-recovery courtesy owed for each billing error corrected on it." Condition: every corrected charge credit is the source of a SERVICE_RECOVERY_COURTESY.
  - p5: "One SERVICE_RECOVERY_COURTESY adjustment is owed on an account".
  - Base, in force: "Only one courtesy adjustment is allowed per patient per calendar year across all accounts."
  - Situation 1, an account with two corrected credits: the gate wants two courtesies and p5/base allow one. Either a second courtesy is posted in breach of base, or the payoff is never fixed.
  - Situation 2, a patient whose year's courtesy was already used on another account: p5 owes none, and the condition is unsatisfiable. The condition is strengthened beyond the sentence's "owed".

Consequence on the audited worlds: none of E1-E4 changes task 0 or task 1. Task 0 is on the Diagnostic tier (flag true). Task 1 has no package, a SELF_PAY account, one credit and no 2026 courtesy. Each task file confirms this against its own world.

Bears on: task 0 (E1), task 1 (E2, E3, E4).

**C2 — SOURCE-POLICY RED: a second record of the kind the rule prices has no unique answer.**

Members:
- (a) p1 prices "the amount of the account's most recent NONCOVERED_SERVICE liability posting", while its first sentence makes the discount owed on each posting and E1 requires "every" posting to carry one.
  - Situation: two undiscounted NONCOVERED_SERVICE postings, for example after a replacement claim.
  - The older posting is owed a discount but the rule gives it the newer posting's amount, or none.
- (b) p3: the same shape on COVERAGE_TERMINATED postings, which E2 requires to be "every" discounted.
- (c) p4 "A charge credit posted on a SELF_PAY account … is owed one CHARGE_CORRECTION_ADJUSTMENT", priced from "the account's most recent charge credit". With two uncorrected credits, the older one has no figure of its own. E3 requires "every charge credit".
- (d) p5 "it posts with the corrected charge credit as its source": with two corrected credits the source is not unique.
- (e) p1 `authorization_on_record` and p2 `claim_lag_allowance` read "the account's PRIMARY claim". A rebilled account (encounter_coverage_update_rebill, or claim CO-109 BILL_CORRECT_PAYER) carries two PRIMARY claims. Compute takes the first row in file order; the rule names no selector.

Consequence on the audited worlds: none. Each world has one posting of each kind, one credit and one PRIMARY claim on the account.

Bears on: task 0 (a, e), task 1 (b, c, d).

**C3 — SOURCE-POLICY RED: absent records and fields.**
- (a) p2 estimate credit with an empty scheduled_service_date: compute gives $25 and the rule gives nothing (see rule_compute_equivalence).
- (b) p5 owes a courtesy for "a statement sent during an active billing hold" but "posts with the corrected charge credit as its source". An account with only the hold-statement failure has no charge credit, so the write has no defined source.

Consequence on the audited worlds: none for (a), since task 0's estimate is scheduled. For (b), task 1's failure is a corrected credit. Task 0 is discussed in 0.md: its claim-level member-ID correction is not a charge credit.

Bears on: task 0 (a, b), task 1 (b).

**C4 — SOURCE-POLICY RED: undeclared conflict between p4 and encounter_late_charges.**
- Base: "A late charge that posts after the window is credited in full with LATE_CHARGE_PAST_WINDOW and is never billed to the patient or the payer."
- p4: "A charge credit posted on a SELF_PAY account already billed to the patient is owed one CHARGE_CORRECTION_ADJUSTMENT".
- Situation: a SELF_PAY account billed, then a late charge credited past the window. Base leaves the patient balance untouched, because the charge was never in the SELF_PAY_FINAL_BILL. p4 lowers the balance by a correction for a charge the patient never owed.
- No overwrite names the base sentence, and encounter_late_charges is not in p4's base_policy_refs.
- Consequence on the audited worlds: none. Task 1's credit is DUPLICATE_CHARGE.
- Bears on: task 1 (structural only).

**C5 — SOURCE-POLICY RED: p4 package tier contradicts its own rationale (XF 12).**
- Passage A: "When the account carries a PACKAGE_PRICE_ADJUSTMENT, the netted discount percent is 100, because a package price does not move with the charges".
- Passage B: "every adjustment stated in percentage points is then added to the correction percent … every adjustment stated in dollars is then added to that figure".
- Situation: a package account with a DUPLICATE_CHARGE credit aged 50 days.
  - Reading A: the correction is 0.00, because the package does not move.
  - Reading B: correction = credit × (2 + dispute points)% + $10.
- The tier is also unreachable through E2 (C1).
- Bears on: task 1 (structural only; no package).

**C6 — SOURCE-FACTOR RED (XF A4): p5's dollar factors are gated through corrected_error_size.**
- `result: MN(cc_ceiling, cc_start + cc_hold_usd + cc_duration_usd + cc_report_usd)`. The fall-through of corrected_error_size is `P('service_recovery_courtesy_max_usd')`, which is ≥ cc_ceiling.
- So whenever corrected_error_size is on its fall-through, hold_and_dispute, error_duration and report_promptness can never change the courtesy. They carry weight only through another factor's tier.
- On task 1's world they do carry weight. Task 1's file shows this, and the structural defect stands regardless.
- Bears on: task 1.

**C7 — SOURCE-FACTOR RED: unreal ladders.** Each member names a condition no US nonprofit hospital's patient financial services weighs for that quantity, or an outcome no such hospital publishes.
- p1 statement_allowance and p3 coverage_loss_statements: the discount percent grows with the number of summary statements issued, which rewards non-payment. No hospital ties a discount to the statement count.
- p1 noncoverage_notice_lag: a per-day dollar credit for how long the payer took to release a non-covered amount. Payer processing time is not a patient discount input. This is an invented servicing allowance.
- p1 authorization_on_record: a prior-auth reference raising a non-covered discount is not a pricing input. Its tier-1 part "has an adjudication date" also holds for every account that reaches this write, because a NONCOVERED_SERVICE posting exists only after adjudication.
- p2 claim_lag_allowance: the patient's prompt-pay percent varies with claim turnaround and Riverbend's correction filings. That is compensation, which base routes through the capped courtesy.
- p3 lost_plan_type: the uninsured discount varies with which kind of plan the patient lost. Its tier-1 part "denial_carc is PR-27" also restates scope, because claim.yaml maps PR-27 to the COVERAGE_TERMINATED release that creates every posting this write prices.
- p3 coverage_loss_notice: more discount the longer the payer took to deny. Not weighed by any hospital.
- p4 dispute_resolution_path, credit_age, credit_reason_allowance: each adds points or dollars above the net credited amount. The correction then removes more than the corrected charge net of discount. That is uncapped compensation outside the in-force base courtesy cap ("up to service_recovery_courtesy_max_usd", "one … per calendar year").
- p5 report_promptness: a larger courtesy for calling sooner after the first statement is not a service-recovery criterion.
- p6 earlier_payments: earlier partial payments raise the payoff discount. This is not a prompt-pay criterion, and it is in tension with base "A partial payment never earns a partial discount".

Bears on: task 0 (p1, p2 members), task 1 (p3-p6 members).

**C8 — SOURCE-FACTOR RED: counts after the C7 strikes.**
- p1: 3 surviving (size, site, deductible). No surviving `method` factor.
- p3: 3 surviving (arrival, band, observation_day_rate).
- p4: 1 surviving (netted). No `method` factor.
- p5: 3 surviving (corrected_error_size, hold_and_dispute, error_duration). These are also gated (C6).
- p2 keeps 5 (2+ parameter, 1 method) and p6 keeps 4. Both are within bounds.
- Cross-difficulty factors surviving: p2 estimate_variance_relief only. p1's two and p3's two are struck. The task 1 consequence is in 1.md.
- Bears on: task 0 (p1), task 1 (p3, p4, p5, cross-difficulty).

### observations (not grounds for rework)
- **O1 (realism, borderline).**
  - p2 paperless_allowance and p6 self_pay_e_statement (a payoff discount by statement delivery channel).
  - p2 check_in_payment_allowance (payoff points for earlier point-of-service payments).
  - p1 site_of_service: the "rendered at" campus is read from the account's facility, since lines carry no facility field. Larger discount at the freestanding center.
  - Each is plausible as Riverbend's own schedule but unusual.
- **O2.** p4 netted_discount_on_file is labelled `parameter` but its tier 2 is a ledger ratio (see factor_ladders).
- **O3.** RND is Python round, against "half-up" in the rules. Framework-wide; no tie in either task.
- **O4 (cross-charter).** estimate.yaml says the Insured Patient Out-of-Pocket Estimate "does not limit what the patient may be billed" and makes variance a review trigger. p2's estimate_variance_relief credits half the excess over the tolerance. This is not a cap, so it is not recorded as a contradiction.
- **O5.** The p4 tool docstring says "the patient-balance correction that follows a charge credit". "follows" relates two records; it is not a tool sequence.
- **O6.** p2 and p6 list `encounter_closed` as a subject, and the pay tools close the account, but `encounter_closed` is not in the difficulty's claimed event_types. This is blueprint-level; SCOPE OK was reported.
- **O7.** The E3 `effect` text covers only the ≥ large_error_usd tier.
- **O8.** p6's "on the balance remaining after the uninsured discount" states an order with no declared edge, but it is transitively forced by E2-E4.

## post_reveal_addendum
Written after both task derivations were frozen and revealed (2026-10-20 14:21 UTC). The pre-reveal sections above are unchanged.

**C9 — SOURCE-POLICY RED: E4's sentence and its declared condition define "billing error corrected" differently.**
- This charter-level defect was recognised only at comparison time, while checking task 1's prerequisite_closure. It could have been seen pre-reveal and is recorded here rather than inserted above.
- E4 sentence: "… the service-recovery courtesy owed for each billing error corrected on it". On its face, and per base "(a billing error already corrected on the account …)", it covers a charge credit as soon as the line is credited.
- E4 condition: covers only "encounter_charge_credited [rows] and a CHARGE_CORRECTION_ADJUSTMENT sourced to it", matching p5's own term "The corrected error is the total of the account's CHARGE_CORRECTION_ADJUSTMENT adjustments".
- On any account where a credit exists without its correction, the condition is vacuously true while the sentence is false. The two readings give different payoffs. Demonstrated on task 1 (1.md finding 1: 1600.56 vs 7781.91 or 2118.79).
- Check 7: the condition is weakened relative to the sentence's natural reading.
- Bears on: task 1.

## closing_checklist
Not closed. Step 4 requires all four relationships to PASS on both tasks, and they do not.

| item | status |
| --- | --- |
| per-task files | 0.md and 1.md correspond one-to-one with the tasks; this is the first revision |
| scopes | disjoint and complete: task 0 {p1, p2}, task 1 {p3, p4, p5, p6}, matching each charter_scope |
| uuid8s | independent |
| trees | DAG |
| customer write | present in each tree |
| value_input floor | met as declared |
| factor sensitivities | every one reproduced figure for figure |

Open REDs:
- Charter: C1-C9.
- Task 0: SOURCE-FACTOR (p1 below four real factors with no real method; p2 claim_lag_allowance unreal).
- Task 1: SOURCE-CHAIN and SOURCE-TASK (E4 vacuous at the opening), and SOURCE-FACTOR (p3, p4, p5 below four real factors; p4 no real method; no surviving cross-difficulty factor; p5 gating; p6 earlier_payments unreal).

Gate re-run on a final form: not applicable until rework.

VERDICT revision_1: task0=RED task1=RED charter=C1,C2,C3,C4,C5,C6,C7,C8,C9

## revision_2

## charter_global_frozen (revision_2)
- Frozen 2026-10-20 ~19:15 UTC (between the 19:08 start and the 19:18 reveal; corrected in revision_3 from a mis-estimated "~19:30"), before this round's task GT or worklog.md was read. Auditor: the same independent policy-task auditor.
- Hashes: `encounter.extended.yaml` 87dc1486238c, `task_tools.py` a2b46649d62a. Both changed since revision_1, so every charter-global section below is re-derived, not carried forward. Base `encounter.yaml` 075330ee128a is unchanged, and lines 1-995 of the extended file are still byte-identical to it.
- Entry evidence: the gate snapshot is in the brief (7/7 OK, coordinator run 2026-10-20T19:00:39, replay --check). Views r2/0.view.json (922f166fa7b24ee4) and r2/1.view.json (57f227121c653e25) match the brief.
- **This round is not blind.** I know the revision_1 gold, my revision_1 findings and the reworker's closed-item list. The new material was derived from the charter and the r2 views before anything masked was read: the new policy encounter_ext_observation_rate_discount (p7), all replaced ladders, and the task 1 tree.
- Mechanical sweep (scratch /tmp/audit_0073_policy): every `compute_basis` quote, policy_source, baseline.rule and replaced_by is verbatim in its own rule. Every superseded_clause is verbatim in the named base rule. Every compute binding has a basis.

### charter content (revision_2)
- p1 encounter_ext_noncovered_discount: prices the total NONCOVERED_SERVICE amount as one adjustment sourced to the most recent posting. Factors: size, site, deductible_burden (method), estimate_surprise (estimate), near_eligibility (assist), covered_visit_addon.
- p2 encounter_ext_insured_payoff: claim_lag_allowance is replaced by noncovered_share. Cross-difficulty is estimate only.
- p3 encounter_ext_terminated_coverage_discount: arrival, band, coverage_loss_near_eligibility (assist), catastrophic_share (method, assist), other_coverage_losses (claim).
- **p7 encounter_ext_observation_rate_discount (new), tool post_observation_rate_discount_cc1ec28d, owner agent.** Factors: campus_day_rate, observation_day_count (method), long_stay_rate, procedure_carveout. Overwrites base uninsured S1 and S2.
- p5 encounter_ext_service_recovery_courtesy: re-scoped. The courtesy is owed where summary statements went out while COVERAGE_TERMINATED postings were undiscounted, and is sourced to the most recent such posting. Prerequisites E3a (p3) and E3b (p7). Factors: corrected_error_size (method), error_duration, misstated_statements, hold_and_dispute.
- p6 encounter_ext_selfpay_payoff: prerequisite E4 (p5) now carries the per-year exception. Factors: gross, recency, window (method), e-statement, registration_payment, collection_stage.
- encounter_ext_charge_correction and its tool are removed.
- Graph:
  - E1: p1 → p2
  - E3a: p3 → p5
  - E3b: p7 → p5
  - E4: p5 → p6
  - Acyclic. Every edge is value_input and state form. Gates are bindings of the blocked compute. resolved_by equals the target_tool.

### policy_conflict_scan / override_declarations (revision_2)
- Sibling overwrites of base S1 ("applies only when … SELF_PAY at final bill"):
  - p1 names COVERAGE_TERMINATED postings and the observation-rate discount as outside it.
  - p3 names NONCOVERED_SERVICE postings and the observation-rate discount.
  - p7 names NONCOVERED_SERVICE and COVERAGE_TERMINATED postings.
  - XF 16 holds.
- p7 overwrites S2 ("posted once per SELF_PAY_FINAL_BILL liability …"). It restates S2 in full and adds the scoped further discount. Declared.
- **Undeclared conflict, base S5 (C14).** p7 is not reconciled with base S5 "An account priced under a Riverbend self-pay package receives the PACKAGE_PRICE_ADJUSTMENT instead and never the uninsured discount."
  - p7's rule grants an UNINSURED_DISCOUNT "On a hospital account whose financial_class is SELF_PAY and which carries observation-hour charge lines" and excludes no package account.
  - Situation: a SELF_PAY account priced under the Maternity & Delivery package that carries a 0762 line. S5 says no uninsured discount. p7 says one is owed.
  - No overwrite names S5.
- p5:
  - Its replaced_by restates the base discretionary courtesy for every other account and the base no-prompt-pay-combination for other courtesies (XF 16 holds).
  - The per-calendar-year sentence is in force, and p6's sentence honours it.
- p2 and p6 prompt-pay overwrites are unchanged and scoped (XF 16 holds). p6's O8 phrase is gone.
- With encounter_ext_charge_correction removed, the base dispute/correction sentence is back in force with no extended conflict. Neither r2 world carries a charge credit.

### rule_compute_equivalence (revision_2)
- Every new ladder is a rule sentence and a branch of its binding, and every branch is a tier the rule states.
- Edge inputs that are now stated:
  - p1: no NC posting, no estimate, no denied case
  - p2 and p1: empty scheduled_service_date (closes C3(a))
  - p3: income 0.00, a posting naming no claim
  - p7: empty service_end_date, no 0762 line
  - p6: no first_statement_date
- **Open members:**
  - C3': a negative balance on p5.
  - C3'': a 0.00 result on p7.
  - C12: p5's rule names "the account's most recent COVERAGE_TERMINATED posting" as the courtesy source with no tie rule of its own. p3 states the tie for its own source; p5 states none.
- XF 9 observation O11: p7 procedure_carveout says "Separately billed procedure lines". Compute counts every posted 0350/0480 line, including a later-credited one. Neither world has such a credit.
- O3 (RND vs half-up) stands. No r2 gold figure falls on a cent tie.

### action_binding_and_uuids (revision_2)
- Six (target_tool, computes) pairs, each claimed once.
- New uuid8 cc1ec28d is independent of 93cdc726, a10a8aeb, f939a41d, 69e36558 and 3917aa11. The removed tool's uuid 10e5aff9 is not reused.
- Bodies only create and update rows, with no checks. No datetime/random imports. No factor id is a substring of a tool name. Docstrings carry no example values and no sequence words. The p7 docstring says "pointing back to the observation-hour charge line it is figured on".
- O5 is moot (tool removed). O6 (encounter_closed outside the claimed event_types) stands.

### prerequisite_sentences / prerequisite_graph (revision_2)
- **E1:** "The insured payoff amount is fixed only after the account's most recent non-covered-service liability posting carries the uninsured discount for the account's non-covered amount, on a patient class that grants that discount." It is scoped to granting classes and to one posting, and the condition matches. C1-E1 and C2(a) are closed for the opening world.
- **E3a:** "The courtesy is not fixed until the account's most recent coverage-terminated liability posting carries its uninsured discount." p5's owed scope requires COVERAGE_TERMINATED postings on an account corrected to SELF_PAY, so the gate is satisfiable through p3. The only writer is p3.
- **E3b:** "The courtesy is not fixed until the account's most recent observation-hour charge line carries its observation-rate discount, where observation hours were billed." The only writer is p7. Open member C1': see findings.
- **E4:** "The self-pay payoff amount is fixed only after an account whose summary statements went out while its coverage-terminated postings carried no uninsured discount carries the service-recovery courtesy owed for that, unless the patient's courtesy for the calendar year was already used." It handles the per-year limit and a single courtesy. The condition tests the earliest SUMMARY_STATEMENT against the first UNINSURED_DISCOUNT on such a posting, so it is not vacuous when undiscounted postings stand. C1-E4 and C9 are closed.
- Four-point test: every sentence has a connective, names record-visible states, and carries no tool, id or snake_case token. No second wording, and no depended-on rule restates a sentence.
- Parallel edges E3a and E3b: p3 reads nothing p7 writes, and the reverse also holds. Both orders give the same terminal state.
- **Open member C2' (a later record of the priced kind):**
  - p1 posts "one UNINSURED_DISCOUNT adjustment, sourced to the account's most recent NONCOVERED_SERVICE liability posting". If a further NONCOVERED_SERVICE posting arrives after that discount (a replacement-claim remittance), E1 requires the new most recent posting to carry a discount, while p1 allows the account one adjustment. The payoff is either never fixed or needs a second adjustment p1 does not allow.
  - The same shape applies to p3 under E3a, and to p7 under E3b for a late 0762 charge.

### factor_ladders (revision_2)
Declared counts:

| policy | factors | parameter / method | multi-source | cross-difficulty |
| --- | --- | --- | --- | --- |
| p1 | 6 | 5 / 1 | site, estimate_surprise, covered_visit_addon | estimate_surprise (estimate), near_eligibility (assist) |
| p2 | 6 | 5 / 1 | estimate_variance_relief | estimate_variance_relief (estimate) |
| p3 | 5 | 4 / 1 | arrival, catastrophic_share | near (assist), catastrophic (assist), other_coverage_losses (claim) |
| p7 | 4 | 3 / 1 | observation_day_count; campus and carveout only by a vacuous conjunct (C11) | none |
| p5 | 4 | 3 / 1 | hold_and_dispute | none |
| p6 | 6 | 5 / 1 | none | none |

Structure checks:
- XF 14 method tests pass:
  - p1 deductible: per $250, capped / flat / none
  - p3 catastrophic: net minus 20% of income, floored / flat / none
  - p7 day count: ceil(hours/24) / 1 / plain dates
  - p5 error size: 0.5% of error / flat / standard
  - p6 window: linear / flat / none
  - p2 estimate: unchanged
- XF A1/A2: no factor reads another factor. near and catastrophic both read the first denied case through their own bindings, and each states its own selection.
- XF A3: the assembly sentences are generic and fix the order. p7's replaces days, then adds per-day dollars to the rate, then figures once, then adds flat dollars.
- C6 is closed. The p5 baseline is now standard_courtesy_share × maximum, below the ceiling, so the dollar factors move the courtesy from the fall-through.

Realism of the replaced ladders. These read as real Riverbend schedules:
- p1 deductible_burden; estimate_surprise tier 1; covered_visit_addon
- p2 noncovered_share (O10, borderline)
- p3 catastrophic_share (an income-share cap is a real hardship device), arrival, band
- p7 campus day rates (tertiary vs critical-access Chilton), long-stay per-diem step-down, hour-based day count, procedure carve-out (procedure time is excluded from observation hours)
- p5 misstated_statements, error_duration, error size
- p6 collection_stage, registration_payment (O1)
- p3 other_coverage_losses is borderline (O9): the count of other PR-27 releases stands in for the extent of the loss.

Federal and program figures:
- The assist seeds use the 2025 HHS guideline: $15,650 for one person and $21,150 for two, which reproduce 425.0% and 450.0%. That guideline is current for January-2026 applications.
- The assist charter's hardship rule makes ASSETS_ABOVE_LIMIT a denial reason after a qualifying-debt pass, so "assets" scoring above "income" is coherent.

Defects:
- **C10, C11, C13, C15** — see findings.

### findings (revision_2, pre-reveal)
Round-1 items:
- **Closed:** C1-E1/E2/E3/E4, C2(a)-(e), C3(a)(b), C4, C5, C6, C7 (all 12 members removed), C8 as stated in round 1, C9.
- **New members of round-1 classes:** C1', C2', C3', C3''.
- **New defects:** C10-C15.

**C1' — SOURCE-POLICY RED (C1 class): the E3b gate cannot be met when the observation-rate discount is 0.00.**
- p7 can figure 0.00, for example a 10-hour Lakeshore stay at $920 of 0762 charges with no 0350/0480 line: (920 − 1250 × 1) floored at 0, × 0.5, + 0 = 0.00.
- E3b then requires the 0762 line to "carry its observation-rate discount". db_schema `amount` is a "positive magnitude", and the tool docstring asks for "a positive amount". No posting can carry 0.00, so p5 is never fixed, and through E4 neither is p6.
- p7's rule says nothing about a 0.00 result. Its only absent case is "an account with no such line".
- Bears on: task 1 (structural; its p7 figure is positive).

**C2' — SOURCE-POLICY RED (C2 class): a later record of the priced kind.**
- See prerequisite_sentences. Members: p1/E1, p3/E3a, p7/E3b.
- Bears on: task 0 (p1) and task 1 (p3, p7), structurally. Neither world has a later posting.

**C3' — SOURCE-POLICY RED (XF 6, credit in a negative balance): p5 can owe a negative courtesy.**
- "The courtesy ceiling is the smaller of service_recovery_courtesy_max_usd and the account's patient_balance", and the courtesy is "never more than the courtesy ceiling".
- On an owed account carrying a credit balance, for example a patient who paid the undiscounted bill before p3 posted, the ceiling and the courtesy are negative. Compute MN gives a negative figure, and no rule sentence covers it.
- Bears on: task 1 (structural).

**C3'' — merged into C1'.** It is the 0.00 member of the same absent-result class.

**C10 — SOURCE-FACTOR RED (realism of a condition): the "first recorded" denied assistance case.**
- p1 near_eligibility, p3 coverage_loss_near_eligibility and p3 catastrophic_share all read "the patient's first recorded assistance case in denied status". Compute is CFIELD, the first row in file order.
- No hospital weighs a patient's oldest denial over the current one. The assist charter opens a case per application.
- Situation: a patient denied in 2024 (INCOME) and again in 2026-03 (ASSETS_ABOVE_LIMIT, so qualifying medical debt was proven).
  - p1/p3 near tiers: no points, because the first recorded case is older than 365 days.
  - catastrophic_share: caps the loss against 2024 income.
  - A real near-miss or catastrophic relief would read the 2026 determination.
- "First recorded" (earliest) and file order also differ whenever seeds are not date-ordered.
- Counting: struck. p1 drops to 5 surviving (still ≥ 4 with a method). **p3 drops to 3 surviving (arrival, band, other_coverage_losses) with no method**, because catastrophic_share is its only method.
- Bears on: task 0 (p1) and task 1 (p3).

**C11 — SOURCE-FACTOR RED (a conjunct that restates scope).** Each member's conjunct holds for every account that reaches the write:
- p7 campus_day_rate "AND observation-hour lines posted". p7 is written only "On a hospital account … which carries observation-hour charge lines".
- p7 procedure_carveout "AND observation-hour charges", same scope.
- p1 estimate_surprise tier 2 "and the non-covered amount is above 0.00". p1's write exists only where a NONCOVERED_SERVICE posting does.
Consequences:
- These conjuncts are what make campus_day_rate and procedure_carveout count as multi-source.
- Counting: struck. **p7 drops to 2 surviving (observation_day_count, long_stay_rate).** p1 drops to 4 surviving once C10 is also applied (size, site, deductible, addon), still with a method.
- Bears on: task 0 (p1, tier not taken) and task 1 (p7).

**C12 — SOURCE-POLICY RED (XF 7): no tie rule for p5's source.**
- p5's courtesy source "the account's most recent COVERAGE_TERMINATED posting" has no same-day tie rule in p5's rule.
- With two COVERAGE_TERMINATED postings on one day, the source is not unique. p3 states "of two posted on the same day, the one recorded first" for its own write only.
- Bears on: task 1 (structural; one posting).

**C13 — SOURCE-FACTOR RED (XF 13 overlap): p7 observation_day_count tiers 1 and 2 overlap as stated.**
- Tier 1: "for an account carrying an emergency department level charge line … whose observation hours exceed 24 times the plain day difference".
- Tier 2: "for a stay whose service_end_date equals its service_start_date and that carries observation hours".
- Both hold for a same-day ED observation stay, where any hours > 0 = 24 × 0. No precedence is stated.
- Both give 1 day while hours ≤ 24, but the ladder is not disjoint as stated.
- Bears on: task 1 (structural; it takes tier 1 on a 2-day stay).

**C15 — SOURCE-FACTOR RED (XF 13): fall-through tiers that no account reaching the write can take.**
- **p6 collection_stage.** p6 applies only "inside the prompt-pay window" (30 or 45 days from the first SUMMARY_STATEMENT, statements every 30 days). Every payoff therefore sees 1 or 2 summary statements.
  - The fall-through ("at or after the final-notice stage, or with no summary statement") is unreachable.
  - The tier-2 bound "fewer than summary_statements_before_final_notice" (3 or 4) always holds.
  - The ladder has two live tiers.
- **p5 corrected_error_size.** The owed courtesy is fixed only after E3a, so "the account's most recent coverage-terminated liability posting carries its uninsured discount" with a positive amount, and the corrected error is > 0.
  - The fall-through "with no corrected error the starting amount stays at the standard courtesy" is unreachable for every courtesy this rule prices.
  - The baseline (standard courtesy) is a figure no such customer receives.
- Counting: struck. p6 drops to 5 surviving (still within bounds). **p5 drops to 3 surviving** (duration, misstated statements, hold and dispute) with no method.
- Bears on: task 1.

**C14 — SOURCE-POLICY RED: undeclared conflict between p7 and base S5 (package accounts).** See override_declarations. Bears on: task 1 (structural; no package).

Surviving counts after C10/C11/C15:

| policy | surviving | method |
| --- | --- | --- |
| p1 | 4 | ✓ |
| p2 | 6 | ✓ |
| p3 | 3 | ✗ |
| p7 | 2 | ✓ |
| p5 | 3 | ✗ |
| p6 | 5 | ✓ |

Observations: O1 (paperless / registration-payment allowances), O3, O4 (insured-estimate relief vs the estimate charter), O6, O9, O10, O11. O2, O5, O7 and O8 are moot or closed.

## post_reveal_addendum (revision_2)
Reveal at 2026-10-20 19:18 UTC.
- Both tasks' gold (6 writes, 6 expected values, 6 baselines, 31 factor-sensitivity figures, all skip figures) equals the auditor's pre-reveal derivation.
- The worklog's item-by-item claims for C1-C9 and the task items agree with the closures recorded in §findings (revision_2, pre-reveal).
- No charter finding was added at reveal time.
- One verdict was reconsidered, not driven by GT: task 0's factors were changed from PASS to RED, for consistency with revision_1's treatment of a scored figure resting on a struck ladder (0.md §source_gt_comparison revision_2).

## closing_checklist (revision_2)
Not closed.

| item | status |
| --- | --- |
| per-task files | one per task, revisions preserved |
| scopes | disjoint and complete: task 0 {p1, p2}; task 1 {p3, p7, p5, p6} |
| uuid8s | independent, frozen |
| trees | acyclic, with customer writes |
| value_input floors | met |
| all factors | bear weight on their worlds |

Open:
- Charter: C1', C2', C3', C10, C11, C12, C13, C14, C15.
- Task 0: SOURCE-FACTOR (C10, C11 contributions).
- Task 1: SOURCE-FACTOR (p3 3/no method, p7 2, p5 3/no method; C15 on p6).

Gates were not re-run by the auditor.

VERDICT revision_2: task0=RED task1=RED charter=C1',C2',C3',C10,C11,C12,C13,C14,C15

## revision_3

## charter_global_frozen (revision_3)
- Frozen 2026-10-20 ~22:16 UTC (between the 22:14 start and the 22:17 reveal), before this round's task GT or worklog was read. Auditor: unchanged.
- Hashes:
  - `encounter.extended.yaml` c3d85e1c9b63: changed, so every touched section is re-derived.
  - `task_tools.py` a2b46649d62a: unchanged since revision_2, so §action_binding_and_uuids (revision_2) is carried forward by reference.
  - The r3 views are byte-identical to r2 (922f166fa7b24ee4 and 57f227121c653e25), so both worlds are unchanged.
  - Base copy still identical.
  - Gate snapshot: 7/7 OK (2026-10-20T22:11:11).
- **This round is not blind.** I know the revision_2 gold and the reworker's item list. The touched levers were derived from the charter first.
- Mechanical sweep: every `compute_basis` quote, policy_source, baseline.rule and replaced_by is verbatim in its rule. Every superseded_clause is verbatim in base. Every binding has a basis.

### What changed, and closure of each round-2 RED
- **C1' (0.00 observation-rate discount): closed.**
  - p7 now holds its figure at a floor: "The observation-rate discount so figured is never less than obs_floor_pct percent of the observation-hour charges". It is therefore positive whenever 0762 charges exist.
  - A package account is excluded both from p7 and from the E3b gate ("… billed on an account not priced under a self-pay package"), with a matching condition.
- **C2' (later posting): closed.**
  - p1, p3 and p7 each now say the account receives the one adjustment once, and that a later posting "receives no further" discount. p1 states this verbatim; p3 and p7 carry the same once-sentences.
  - E1, E3a and E3b now wait on a discount standing against *one of* the account's postings, and the conditions say "one of".
- **C3' (negative courtesy): closed.**
  - p5: "never below 0.00: an account whose patient_balance is 0.00 or less … is owed no courtesy". Compute is `MX(0, …)`.
  - E4 carries "or the account's patient balance is 0.00 or less" in both the sentence and the condition.
- **C10 ("first recorded" denied case): closed.**
  - p1 and p3 read "the patient's most recent assistance determination (… latest determination_date; of two determined on the same day, the one recorded first; a case not yet determined is not a determination)".
  - Compute uses XLATEST on assistance_cases by determination_date, a separate status binding, and a guarded income binding for catastrophic_share.
  - Undetermined cases store `''` and sort lowest, so they are never selected over a determination (checked against the r3 rows).
  - near and catastrophic each keep their own bindings (A1 holds).
- **C11 (scope-restating conjuncts): closed.**
  - campus_day_rate now turns on the facility and an ED level line, which divides observation placements.
  - procedure_carveout and estimate_surprise tier 2 have dropped the conjunct.
- **C12 (tie rule for p5's source): closed.** The tie is now stated in p5's own rule.
- **C13 (day-count overlap): closed.** Tier 1 now requires "service_end_date is after its service_start_date", which is disjoint from tier 2's same-day stay.
- **C14 (p7 vs base S5): closed.** p7's rule, both replaced_by texts and compute (`0 if ob_package > 0`) exclude package-priced accounts. This is consistent with base S5.
- **C15 (unreachable fall-throughs): closed.**
  - p6 collection_stage is struck and replaced by standing_balance_band, a band on the account ledger balance (liabilities − adjustments − payments + refunds). Its fall-through (< 500) is reachable above the prompt-pay minimum.
  - p5 corrected_error_size is re-cut (≥ 5000 proportional / 500-5000 flat 25 / < 500 standard), so the fall-through is reachable for small coverage losses. Account 2642eb98's 127.30 is an example.
  - p5 misstated_statements is re-cut (3+ / 2 / a single statement). Every owed account has at least one statement, so the fall-through is reachable.

### XF recipe on the touched policies (p1, p2 sentence, p3, p5, p6, p7)
- A1-A5: no factor reads another factor. The floor reads only the baseline charges. The assembly sentences are generic, and p7's fixes "held at its floor" before flat dollars. No rule defines a quantity as another policy figures it.
- B6-B13: edge inputs are stated in rule and compute (no determination, an undetermined case, package, balance ≤ 0, empty end date, no 0762 line). Ties are stated. No MONTHS. Filters match the rules. Rounding placement matches the rule (O3 framework note stands). Ladders are disjoint with no gaps.
- C14 (method test): p7 day count; p5 error size (proportional / flat / standard); p3 catastrophic. All pass.
- D15-D17: overwrites retire only conflicting clauses. Siblings name each other. p7's replaced_by restates S2 in full.
- E18-E24: tools unchanged. No 0.00 write remains.
- F25-F27: worlds unchanged. The revision_2 seed checks stand.

**Realism of the new levers:**
- p7 floor (a minimum self-pay discount on observation hours, a Riverbend schedule): real.
- p6 standing_balance_band (balance-size tier on the prompt-pay percent): real. It is the same quantity as patient_balance.
- p5 re-cut tiers: real.
- p7 campus rate applying only to ED-placed observation: borderline, **O12**. A per-diem campus differential limited to ED placements is unusual but plausible as Riverbend's own.

### Regression check (untouched elements)
- p2 factors are unchanged. Only its E1 wording moved to "one of" and stays scoped to granting classes.
- No new cross-category read beyond assist cases.
- Graph unchanged: E1 p1→p2; E3a p3→p5; E3b p7→p5; E4 p5→p6. Acyclic. All edges value_input.
- Observations O1, O3, O4, O6, O9, O10 and O11 stand. O12 is new.

### Factor counts (revision_3)

| policy | factors | multi-source / cross-difficulty |
| --- | --- | --- |
| p1 | 6 (method deductible) | estimate_surprise and near_eligibility cross |
| p2 | 6 (method estimate) | estimate cross |
| p3 | 5 (method catastrophic) | near and catastrophic (assist), other losses (claim) |
| p7 | 4 (method day count) | campus and day count are genuinely multi-source |
| p5 | 4 (method error size) | |
| p6 | 6 (method window) | |

All factors pass the realism and structure tests (O12 is borderline).

### findings (revision_3, pre-reveal)
- All nine round-2 charter REDs are closed (above). No new charter RED found.

## post_reveal_addendum (revision_3)
- Reveal at 22:17 UTC by the reveal script's clock, after all revision_3 sections were written.
- Gold in both tasks equals the auditor's derivation: 6 writes, 6 expected values, 6 baselines, 31 factor-sensitivity figures, all skip figures.
- The worklog round-3 claims agree with the closures above.
- Nothing was added or reconsidered after the reveal.

## closing_checklist (revision_3)
- Per-task files 0.md and 1.md correspond to the tasks, and revisions 1-3 are preserved. Every comparison section of revision_3 carries PASS.
- All six extended policies are covered. Scopes are disjoint and complete: task 0 {p1, p2}; task 1 {p3, p7, p5, p6}. Task tools and GT are closed. The uuid8s (93cdc726, a10a8aeb, f939a41d, cc1ec28d, 69e36558, 3917aa11) are independent and frozen.
- Trees:

  | task | prerequisites | value_input edges | customer write |
  | --- | --- | --- | --- |
  | 0 | 1 | 1 | yes |
  | 1 | 3 | 3 | yes |

  The difficulty graph is acyclic.
- Every computation has a self-sufficient baseline and 4-6 factors with ≥ 2 parameter and 1 method:

  | policy | factors |
  | --- | --- |
  | p1 | 6 |
  | p2 | 6 |
  | p3 | 5 |
  | p7 | 4 |
  | p5 | 4 |
  | p6 | 6 |

  Each task has multi-source and cross-difficulty factors. Every ladder has ≥ 3 reachable, disjoint tiers stated in its rule. Every factor bears weight against an honest baseline, and each baseline-alone figure differs from gold.
- Gates on the final form: the coordinator's 7/7 OK run (2026-10-20T22:11:11, replay --check) on these hashes. The auditor did not run gates.
- Open observations, not grounds for rework: O1, O3, O4, O6, O9, O10, O11, O12.

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

## charter_global_frozen (revision_4)
Entry evidence:
- The gated chain passed: the worklog tail reads `REWORK round 4: gates 7/7 green`.
- `/tmp/erl0073_coord/snapshot.sh hospital_account_billing 4`, run 2026-10-21T01:42:47, reported:
  - views r4/0.view.json 922f166fa7b24ee4 and r4/1.view.json 57f227121c653e25, the same masked keys, byte-identical to r2/r3 (worlds unchanged);
  - EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK;
  - sha256: encounter.extended.yaml a3ac4c93239f, task_tools.py d4522c0bfe57, tasks/0.json 7cc86253347e, tasks/1.json 717081752f9f.
- No gate was red on entry.

Freeze and scope:
- This section was written before the r4 task JSONs were read. Not blind: the round-4 items come from audits/render_source/hospital_account_billing/render_r1.md (read in full) and from the worklog's round-4 section.
- Base copy is still identical.
- Mechanical sweep: every quote, policy_source, baseline.rule and replaced_by is verbatim. Every superseded clause is verbatim in base. Every binding has a basis.
- Factor rosters are unchanged from revision_3. The touched policies are p1 (near_eligibility), p3 (coverage_loss_near_eligibility, catastrophic_share), p7 (observation_day_count), and all six tool bodies.

### Honest note on revision_3
All three renderer items are members of classes I had passed:
- **Mismatch 1.** In revisions 2 and 3 I recorded p7's "(0 when service_end_date is empty)" as a stated edge. I did not test it against the same-day branch `ob_plain_days == 0 and ob_hours > 0`, which returned 1 day on an empty end date. This was a rule-vs-compute miss (XF B6) that I passed.
- **Note 3.** In revision_3 I checked that the seeds store empty dates as `''` and recorded no finding. A producible world that stores null would have selected an undetermined case. This was a latent absent-record member that I passed.
- **Note 2.** I passed the six tool docstrings' "stored rounded half-up to the cent" claim as accurate (XF 21), but the bodies used Python `round`.

### Closure of the round-4 items
- **Mismatch 1: closed (rule = compute).**
  - The same-day tier now requires a recorded end date in both the rule and compute: "for a stay whose service_end_date is recorded and equals its service_start_date … otherwise, including a stay with no service_end_date yet (0 plain days), they stay at the plain day difference". Compute: `1 if (F('service_end_date') and ob_plain_days == 0 and ob_hours > 0)`.
  - The ladder is reworded to match, and the tiers stay disjoint.
  - The class sweep is clean: every other empty-date branch is stated and guarded (first_statement_date in p2/p5/p6, estimate dates in p1/p2, the latest summary in p6, assist dates in p1/p3).
  - **The open-stay case the fix now prices is a new defect: see C16.**
- **Note 2: closed.**
  - All six tools now store `amt = _Ledger.cents(amount)`. The static helper computes `sign * int(abs(x) * 100 + 0.5 + 1e-9) / 100`, which is half-up away from zero. It has no imports, and as a class static method it is not exposed as a tool.
  - Docstrings are unchanged and now true.
  - Every gold amount is stored unchanged: 340.67, 898.64, 6881.20, 487.00, 71.84 and 1591.74 were checked against the float products.
  - No other docstring makes a rounding claim. The balance lines subtract two cent values and claim nothing.
- **Note 3: closed.**
  - Every determination read is now status-filtered: denials are read with `XLATEST(…, status='denied')`, and awards are the `MX` of the status-filtered XLATESTs for approved, expired and revoked.
  - near_eligibility in p1 and p3 applies only when the latest denial date is strictly later than the latest award date. The rule says a same-day award counts as later, and the first-recorded of two same-day denials counts, which XLATEST keeps on ties.
  - submitted, pending_documents and withdrawn cases are never read. That covers null or empty dates and a reopened reconsideration carrying an old date.
  - catastrophic_share now credits only when the most recent determination is a denial, read with its own bindings (td_cat_date, td_cat_award_date). A1 independence holds.
  - The assist charter confirms that expired and revoked arise only from approved cases (approved→expired at award_end_date; approved→revoked), so they carry a real determination date. Treating them as determinations is correct.
  - Realism of the narrowed catastrophic share (income cap read from a denied application only; an approved patient receives charity instead): real.

### XF recipe on the touched policies (p1, p3, p7, tools)
- A1-A5: no factor reads another factor. p3 states each selection once per factor. Assembly is unchanged.
- B6-B13: absent cases are stated and guarded (no determination, an undetermined case, a same-day award, same-day denials, an open stay). Ties are stated. Filters carry exactly the stated statuses. Ladders are disjoint.
- C14 (method test): day count and catastrophic still pass.
- D15-D17: overwrites are unchanged.
- E18-E24: no forbidden imports; the helper is a class static method; docstrings carry no examples and no false claims; no 0.00 writes.
- F25-F27: worlds unchanged.

**One new member: C16 below.**

### findings (revision_4, pre-reveal)
**C16 — SOURCE-POLICY RED: p7 prices an open, unbilled observation stay as zero observation days, against the base final-bill rule.**
- p7's scope is "a hospital account whose financial_class is SELF_PAY, which carries observation-hour charge lines (revenue code 0762) and which is not priced under a Riverbend self-pay package". It has no status or final-bill requirement. db_schema: service_end_date is "empty while the encounter or series is still open".
- The round-4 wording, matched by compute, gives such a stay 0 observation days. The discount is then the whole observation-hour charges times the net factor (plus the carve-out), which is the largest figure the rule can produce.
- Base encounter_final_bill_and_liability, not overwritten, says: "Charges accrue on a pending_billing account until the final bill drops … the whole net gross charges post as one SELF_PAY_FINAL_BILL liability and the uninsured discount follows."
- Situation: a SELF_PAY observation patient still in the bed, account pending_billing, service_end_date empty, a 24-hour 0762 line of 2,208.00 posted, no liability, patient_balance 0.00.
  - Base: no uninsured discount until the final bill.
  - p7: one is owed now, (2208 − 1250 × 0) × 0.5 = 1104.00 plus any carve-out, which turns the balance into a −1104.00 credit.
- No overwrite names the final-bill sentence. No real hospital prices an unfinished observation stay at zero days.
- Bears on: task 1 (structural only; its stay closed 07-04 and was final-billed 07-08).

All round-3 closures stand. Nothing else regressed: rosters, gates, graph and the p2/p5/p6 text are untouched apart from what was listed.

## post_reveal_addendum (revision_4)
- Gold in both tasks is unchanged and equals the auditor's derivation, figure for figure.
- Nothing was added or reconsidered after the reveal.

## closing_checklist (revision_4)
- Not closed. One charter RED is open: C16.
- Everything else in the revision_3 checklist stands on the round-4 hashes (a3ac4c93239f / d4522c0bfe57): coverage, disjoint scopes, independent uuid8s, trees, factor counts and weight, and the 7/7 gates from snapshot 2026-10-21T01:42:47.
- Open observations, not grounds for rework: O1, O3, O4, O6, O9, O10, O11, O12. O3 is now narrowed: the tool layer stores amounts half-up, and only the DSL's RND remains Python round, with no tie in either task.

VERDICT revision_4: task0=PASS task1=PASS charter=C16

## revision_5

## charter_global_frozen (revision_5)
Entry evidence:
- The worklog tail reads `REWORK round 5: gates 7/7 green`.
- `/tmp/erl0073_coord/snapshot.sh hospital_account_billing 5`, run 2026-10-21T02:19:07, reported:
  - views r5/0.view.json 922f166fa7b24ee4 and r5/1.view.json 57f227121c653e25, the same masked keys, identical to r2-r4 (worlds unchanged);
  - EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK;
  - sha256: encounter.extended.yaml f701977c54dd (changed), task_tools.py d4522c0bfe57 (unchanged since revision_4), tasks/0.json eb9a8a4effe8, tasks/1.json f5bba00cb82e.
- No gate was red on entry.

Freeze and scope:
- Written before the r5 task JSONs were read. Not blind: the worklog round-5 section was read.
- Base copy is still identical.
- Mechanical sweep: every quote, policy_source, baseline.rule and replaced_by is verbatim. Every superseded clause is verbatim in base. Every binding has a basis.
- Rosters are unchanged: 6 / 6 / 5 / 4 / 4 / 6 factors.
- Spot checks confirm the earlier closures are intact: status-filtered determination reads (8 `status='denied'` reads), `_Ledger.cents` in all six tools, the E4 zero-balance exception, the observation floor 5.0, and the courtesy re-cut (0.2 share, 5000 threshold).

### C16 closure
**Closed.** p7's scope sentence now requires the final bill: "whose final bill has dropped (final_bill_date and service_end_date both recorded; as with every uninsured discount, none is owed while the stay is open or the account is still pending_billing)".
- Compute has a plain scope binding, `ob_billed = 1 if (F('final_bill_date') and F('service_end_date')) else 0`, and `result` returns 0 outside scope. This is not a factor, and no factor reads it.
- Both overwrite restatements carry the same scope, so S2 and the S1 sibling naming still agree (XF 16).
- The courtesy's E3b sentence now reads "where observation hours were billed on a final-billed account not priced under a self-pay package", and its condition adds "whose final_bill_date and service_end_date are recorded". An out-of-scope stay can neither block the courtesy nor need a 0.00 write (XF 24).
- db_schema: final_bill_date is "empty while pending_billing", which is consistent with the parenthetical.
- The round-4 "no service_end_date yet" clause is removed from the day-count sentence and ladder. The same-day compute guard remains and agrees with the rule.

**Class sweep (a discount owed before the final bill), independently re-checked:**
- p1 needs a NONCOVERED_SERVICE posting, which exists only after a payer adjudicates a billed claim.
- p3 needs COVERAGE_TERMINATED postings on an account "corrected to SELF_PAY after its final bill".
- p5's owed courtesy needs issued summary statements.
- p2 and p6 need a payment inside a window counted from first_statement_date.
- The base SELF_PAY_FINAL_BILL discount is a system trigger at final bill.
- No other member exists.

### XF recipe on the touched policies (p7, p5 E3b)
- A1-A5: the scope binding is plain and stated once, no factor reads another, and the assembly is unchanged.
- B6-B13: open stay, unbilled account, package, empty end date and same-day stay are each stated and guarded. Ties are stated. Tiers are disjoint (day count: end after start / recorded same-day / otherwise). Rounding placement is unchanged.
- C14 (method test): the day count still passes.
- D15-D17: both p7 restatements are scoped. p7 names the NONCOVERED_SERVICE and COVERAGE_TERMINATED siblings, and p1 and p3 name the observation-rate discount.
- E18-E24: tools are byte-identical to revision_4.
- F25-F27: worlds unchanged.

**Observation O13 (not a RED).** The baseline sentence keeps "(0 when service_end_date is empty)". Within p7's scope an end date is always recorded, so the parenthetical now describes an out-of-scope input. Rule and compute still agree on it (`ob_plain_days` is 0), so neither relationship moves. I name it here so a renderer scan does not treat it as an unconsidered member.

### findings (revision_5, pre-reveal)
- C16 is closed. No new charter RED, and nothing regressed.

## post_reveal_addendum (revision_5)
- Gold in both tasks is unchanged and equals the auditor's derivation, figure for figure.
- Nothing was added or reconsidered after the reveal.

## closing_checklist (revision_5)
- Per-task files 0.md and 1.md correspond to the tasks, revisions 1-5 are preserved, and every revision_5 comparison is PASS.
- Coverage: all six extended policies. Scopes are disjoint and complete: task 0 {p1, p2}; task 1 {p3, p7, p5, p6}.
- Task tools and GT are closed. The uuid8s are independent and frozen.
- Trees:

  | task | prerequisites | value_input edges | customer write |
  | --- | --- | --- | --- |
  | 0 | 1 | 1 | yes |
  | 1 | 3 | 3 | yes |

  The difficulty graph is acyclic.
- Every computation has a self-sufficient baseline and 4-6 real factors with ≥ 2 parameter and 1 method. Each task has multi-source and cross-difficulty factors. Every ladder has ≥ 3 reachable, disjoint tiers stated in its rule. Every factor bears weight, and each baseline-alone figure differs from gold.
- Gates on the final form: snapshot 2026-10-21T02:19:07, 7/7 OK (extended f701977c54dd, tools d4522c0bfe57).
- Open observations, not grounds for rework: O1, O3 (DSL RND only), O4, O6, O9, O10, O11, O12, O13.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

## charter_global_frozen (revision_6)
Entry evidence:
- The worklog tail reads `REWORK round 6: gates 7/7 green`.
- `/tmp/erl0073_coord/snapshot.sh hospital_account_billing 6`, run 2026-10-21T19:30:43, reported:
  - views r6/0.view.json 922f166fa7b24ee4 and r6/1.view.json 57f227121c653e25, identical to r2-r5 (worlds unchanged);
  - EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK;
  - sha256: encounter.extended.yaml 825cea73c913 (changed), task_tools.py d4522c0bfe57 (unchanged), tasks/0.json 14488954015e, tasks/1.json af3ac0804b44.
- No gate was red on entry.

Freeze and scope:
- Written before the r6 task JSONs were read. Not blind.
- Source items read: src-1 and src-2 lines of audits/policy_kb/hospital_account_billing/_difficulty.md, and the worklog round-6 section. audits/runtime_context/ was not read.
- Mechanical sweep: every quote, policy_source, baseline.rule and replaced_by is verbatim. Every superseded clause is verbatim in base. Every binding has a basis. Base copy identical. Rosters are 6/6/5/4/4/6, unchanged.

### Honest note on revisions 3-5
Both src items are members of the C1 class (a sentence broader than its condition) that I passed:
- **E1 (revision_3 wording).** In revision_3 I recorded E1 ("… stands against one of the account's non-covered-service liability postings, on a patient class that grants that discount") as "scoped to granting classes … condition matches". I did not test an insured account of a granting class with no NON-COVERED posting. Read literally, the sentence holds that account's payoff unfixed forever.
- **The two courtesy sentences.** I read them as vacuous on accounts outside their record kinds (revision_2: "on an account without COVERAGE_TERMINATED postings there's no most recent such posting → vacuous"). That is a generous reading. Read literally, they omit the SELF_PAY and coverage-terminated limits their conditions carry, and so they also block the discretionary courtesy "on every other account".

### src-1 / src-2 closure, and a sweep of every prerequisite sentence
Each sentence is compared with its condition below. All four keep state form, an ordering connective, and no tool, policy id, snake_case or code token (token scan empty). Each is verbatim in its own rule and nowhere else.

| edge | sentence (round 6) | condition | verdict |
| --- | --- | --- | --- |
| E1 p2←p1 | "On an account that carries a non-covered-service liability posting and whose patient class grants the uninsured discount on such postings, the insured payoff amount is fixed only after an uninsured discount stands against one of those postings." | class flag true AND carries a NONCOVERED_SERVICE posting; an UNINSURED_DISCOUNT sourced to one of them | equal scope ✓; satisfiable through p1, whose scope is the same record test ✓ |
| E3a p5←p3 | "On a self-pay account that carries coverage-terminated liability postings, the courtesy is not fixed until an uninsured discount stands against one of those postings." | SELF_PAY AND carries COVERAGE_TERMINATED postings; a discount on one of them | equal ✓; p3 owes on exactly these accounts (COVERAGE_TERMINATED implies corrected after final bill) ✓; a discretionary courtesy elsewhere falls outside ✓ |
| E3b p5←p7 | "On a self-pay account whose stay has ended and whose final bill has dropped, that carries observation-hour charge lines and that is not priced under a self-pay package, the courtesy is not fixed until an observation-rate discount stands against one of those lines." | SELF_PAY, final_bill_date and service_end_date recorded, 0762 lines, no PACKAGE_PRICE_ADJUSTMENT; a discount on one of those lines | equal ✓; this is exactly p7's scope (C16 closure), and p7's floor makes it positive ✓ |
| E4 p6←p5 | "… a self-pay account that carries coverage-terminated liability postings, and whose first summary statement went out before any of them carried an uninsured discount, carries the service-recovery courtesy owed for that, unless the patient's courtesy for the calendar year was already used or the account's patient balance is 0.00 or less." | SELF_PAY, COVERAGE_TERMINATED postings, earliest SUMMARY before the first discount on such a posting (or none); courtesy sourced to one of them; per-year and balance exceptions | equal ✓, including the no-discount case. The "already used" wording covers the condition's "on another account" (a courtesy on this account satisfies the gate). It matches p5's owed scope ✓ |

- **Undeclared-order sweep.** A sentence scan for ordering words outside the four sentences finds only date comparisons inside a policy's own quantities ("immediately before the payment", estimate and determination dates, coverage terminated "before the date of service"). There is no cross-problem order.
- **Nothing regressed.** Conditions and compute are unchanged. The C16 scope, status-filtered determination reads, half-up tool storage, observation floor and courtesy re-cut are intact. Tools are byte-identical.

### findings (revision_6, pre-reveal)
- src-1 and src-2 are closed, and the class sweep is complete (all four sentences).
- No new RED.
- KB note for the coordinator (outside this audit's write domain): the published encounter documents carry the old sentences, as the worklog itself states.

## post_reveal_addendum (revision_6)
- Gold in both tasks is unchanged and equals the auditor's derivation.
- The task files carry the round-6 sentences verbatim.
- Nothing was added after the reveal.

## closing_checklist (revision_6)
- The revision_5 checklist stands on the round-6 hashes (extended 825cea73c913, tools d4522c0bfe57; snapshot 2026-10-21T19:30:43, 7/7 OK).
- All four prerequisite sentences now state exactly their conditions' scope.
- Open observations, not grounds for rework: O1, O3, O4, O6, O9-O13.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

## charter_global_frozen (revision_7)
Entry evidence:
- The worklog tail reads `REWORK round 7: gates 7/7 green`.
- `/tmp/erl0073_coord/snapshot.sh hospital_account_billing 7`, run 2026-10-22T01:06:37, reported:
  - view r7/0.view.json 7538ad4cacbc9263 (changed: task 0 re-seeded);
  - view r7/1.view.json 57f227121c653e25 (unchanged);
  - EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK;
  - sha256: encounter.extended.yaml **825cea73c913** and task_tools.py **d4522c0bfe57**, both unchanged as required. tasks/0.json 01c03088b711 (changed), tasks/1.json af3ac0804b44 (unchanged since revision_6).

Freeze and scope:
- Charter and tools are unchanged, so every charter-global section of revision_6 is carried forward by reference on those two hashes.
- Read this round: the src-3, src-4 and src-5 lines of audits/policy_kb/hospital_account_billing/_difficulty.md; docs/assist, docs/estimate and docs/claim (the sections on the re-seeded rows). audits/runtime_context/ was not read.
- **This round is not blind.** Task 0's world changed. I derived it on the new world against the unchanged policy before reading tasks/0.json.

### Honest note on src-3
In revision_2 I recorded fc43a6e1 (liquid assets 31,500.00 > 25,000.00, with no qualifying debt) as a *near-miss* resolved by `denial_reason`. I did not test whether the published assist rule uniquely yields INCOME_ABOVE_LIMIT. Both §4.6 clauses applied:
- "above 400 percent without qualifying medical debt → income above limit";
- "a hardship applicant over the asset limit → assets above limit".

The seed was therefore ambiguous against its owning charter (XF 25). This was a seed-realism member that I passed.

### Re-seeded rows checked against the published docs
- **Assist case fc43a6e1 (src-3).**
  - liquid_assets_usd changes 31,500.00 → 18,750.00, which is at or below the Medical Hardship liquid asset limit of 25,000.00 (docs/assist medical_hardship_thresholds_and_asset_test). The asset clause no longer applies.
  - The case has OUTSIDE_MEDICAL_BILLS accepted, so per docs/assist documentation_of_riverbend_charges_for_medical_hardship ("for every other application, including one with an outside medical bills document accepted, the qualifying medical debt … exceeds that same percent of annual household income") the test is 1,040.00 against 20% × 95,175.00 = 19,035.00. It fails, so the only reason is "income above limit".
  - INCOME_ABOVE_LIMIT is now unique ✓. FPL 450.0% = 95,175 / 21,150, the 2025 HHS guideline for 2 persons, still holds.
  - The bank statement document is accepted, so the asset figure is documented ✓.
- **Estimate b9a956ef (src-4).**
  - The new version 2 (issued 2026-08-24, the day of service, total 1,026.00) has lines 72148 996.00 and 75571 30.00, both CONVENING_FACILITY Grand Chute, posted 2026-08-24.
  - docs/estimate estimate_revisions_and_expiry: "Change made on the day of service → new version furnished that day" ✓. "Only the latest version furnished before the service is the estimate compared with the bill" — v2 is furnished on the service day ✓.
  - estimate_content_and_expected_charges: a line is recorded once per version, provider role and code, so the v2 lines are re-recorded ✓, and the total is the sum of v2 lines ✓. One estimate per scheduled service, with a change being a new version ✓.
  - The CT line's 30.00 is an insured "contracted rate applied to remaining deductible, coinsurance and copay" figure. No per-code contracted rate is published, so 30.00 is plausible (a 20% coinsurance share of a ~150 contracted rate for a calcium score) but not reproducible. **Observation O14.**
- **Claim 0d58098f (src-5).**
  - front_end_reject_reason changes NONE → INVALID_MEMBER_ID, with frequency code '1' kept.
  - docs/claim denial_and_rejection_routing: "every front-end rejection [is] fixed on the claim and resubmitted; a corrected member ID … taken exactly as printed on the patient's current insurance card".
  - docs/claim timely_filing_rule: "A front-end rejected submission never counts as received". So the corrected submission is an original (1), not a replacement (7) ✓.
  - The 2025 member ID SHP11368120 against the 2026 card's SHP11402937 explains the rejection ✓.

### findings (revision_7, pre-reveal)
- src-3, src-4 and src-5 are closed.
- Charter unchanged; no charter RED.
- Task 1 is untouched (view and task JSON hashes unchanged since revision_6).

## post_reveal_addendum (revision_7)
- Task 0 gold equals the auditor's new-world derivation, including the payoff move to 915.89.
- Task 1 is unchanged.
- Nothing was added after the reveal.

## closing_checklist (revision_7)
- The revision_6 checklist stands on charter 825cea73c913 / tools d4522c0bfe57, with tasks/0.json 01c03088b711 and tasks/1.json af3ac0804b44.
- Snapshot 2026-10-22T01:06:37: 7/7 OK.
- Every re-seeded row is consistent with its owning charter's published docs.
- Open observations, not grounds for rework: O1, O3, O4, O6, O9-O14.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN
