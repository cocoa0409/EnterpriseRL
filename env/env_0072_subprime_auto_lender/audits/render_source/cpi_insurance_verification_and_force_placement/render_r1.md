# Render round 1 — cpi (Collateral Protection Insurance): STOP, source findings

Source: env/env_0072_subprime_auto_lender/tasks/cpi_insurance_verification_and_force_placement/cpi.extended.yaml
(+ task_tools.py beside it). Gate line read: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN`.
I scanned the source against XF_recipe.md and the render skill's criteria before writing anything. The findings below are
mismatches that no rendering can carry faithfully, so no document was written and nothing exists under docs/cpi/ or
.doc_render_staging/cpi/. Line numbers refer to cpi.extended.yaml.

## R1. The replacement gap is owned by one factor but is the quantity all three grace allowances act on (XF A.1/A.2/A.5; rule vs compute)
- Where: cpi_ext_closing_month_refund `compute` cm_gap (l.1537), factor `cm_plan_grace.bindings: [cm_gap, cm_plan, cm_gplan]`
  (l.1604-1610), `result` (l.1548). The same pattern applies to cpi_ext_closing_period_refund: cp_gap (l.1979),
  `cp_plan_grace.bindings` (l.2046-2052) and `result` (l.1990).
- The compute reads `result: RND(cm_amt * (... (cm_cover + MN(cm_gap, cm_gplan + cm_gstate + cm_gyear) + cm_post) ...) / cm_days, 2)`.
  So the state allowance (cm_gstate) and the model-year allowance (cm_gyear) count only through cm_gap, and cm_gap is a
  binding of a different factor, cm_plan_grace. Read literally, the state and year grace factors depend on a quantity that
  another factor owns.
- The rule text places that quantity in the standard method. baseline.rule (l.1662) says "For the closing-month refund, a
  replacement gap is the run of days strictly between the spans of two reaching proofs that do not overlap, and its first
  days count as covered, as many as the sum of every replacement-grace allowance this rule states." cm_gap's compute_basis
  (l.1573) quotes that baseline sentence. The computation document cannot cover cm_gap, because it is a factor binding. The
  plan-grace document would then be the only home of a definition that the state-grace and year-grace documents also need.
- Needed: make cm_gap / cp_gap a plain (non-factor) binding, stated once in the rule, and keep only cm_plan / cm_gplan
  (cp_plan / cp_gplan) as the plan-grace factor's bindings.

## R2. Plain bindings that only the covered-days factor uses, one with a factor sentence as its compute_basis (XF A.5; rule vs compute)
- Where: cm_ov (l.1533) has compute_basis (l.1569) "When an accepted insurer-feed proof and an accepted uploaded proof both
  reach the covered stretch, the closing-month refund's covered days are the days inside either span, a day inside both
  counted once." That sentence is tier 1 of factor cm_cover_rule (l.1592-1593) and does not appear in baseline.rule.
  cm_ov is nevertheless a non-factor binding, so the computation document would have to cover it. The same applies to cp_ov
  (l.1975, basis l.2011).
- cm_a_n / cm_b_n (l.1531-1532) and cp_a_n / cp_b_n (l.1973-1974) are also plain bindings. Only the cm_cover_rule /
  cp_cover_rule tiers read them (union tier and single-span tier). The standard covered-days count uses cm_le / cp_le,
  cm_start and cm_closed and never reads them.
- Needed: move cm_ov, cm_a_n and cm_b_n into cm_cover_rule's bindings, and cp_ov, cp_a_n and cp_b_n into cp_cover_rule's.
  Alternatively, state the span day-count and overlap in the standard method in a way the standard method actually uses.

## R3. The standard covered-days sentence defers to a base clause that its own overwrite retires, and is inaccurate for the closing-period charge (XF D.21, A.6)
- Where: closing-month baseline.rule (l.1661-1662) says "As the standard method, the closing-month refund's covered days are
  counted as the base refund rule counts an accepted proof's days: the days of the period from the policy_effective_date of
  the reaching proof with the latest effective date (...) through the closed_date, both ends counted." Closing-period
  baseline.rule (l.2103-2104) has the same sentence.
- The same policies' overwrites (l.1463-1464, l.1913-1914) retire exactly that base clause: "When accepted proof starts
  after the CPI coverage effective date, each unrefunded charge is refunded for the days of its billing period on or after
  the proof's policy_effective_date ...".
- The claim is also not literally true for the closing-period charge. The base clause counts from the proof effective date
  through the period end. The closing-period sentence counts through the closed_date and adds the post-closing days
  separately.
- Needed: drop "counted as the base refund rule counts an accepted proof's days:" and keep the explicit definition.

## R4. Unscoped retirement of "An accepted proof always updates the policy details on file" leaves accepted re-reviews on open records undefined (XF D.19, undefined edge)
- Where: the overwrites of cpi_ext_feed_proof_rereview (l.1053-1055), cpi_ext_upload_proof_rereview (l.1287-1289) and
  cpi_ext_fax_proof_rereview (l.1682-1684). Each retires the base clause "An accepted proof always updates the policy
  details on file". Each replaced_by covers only closed records: "On a closed tracking record, ... an accepted re-review on
  a closed record never changes the record's status, never updates the policy details on file and mails no notice."
- The "Outside this rule ..." sentence (l.1058 etc.) restates the base content only for "an accepted first review".
- The rules also have a reach-date tier for a record that is not closed: "the contract's repossession_date when the record
  is not closed while the contract is repossessed" (feed l.1089, upload l.1314, fax l.1718; factor tier 2 at l.1235 etc.).
  A repossessed contract's record "stays open but is not billed" (base l.1010) and can be force_placed.
- For an accepted re-review on such an open record, three things now conflict:
  - The policy-details update is retired and nothing replaces it.
  - The in-force base clause "on a record in pending_verification, lapse_notice or force_placed status it also returns the
    record to compliant, and on a force_placed record that return cancels the placed coverage ... a cancellation notice is
    mailed" still applies.
  - The re-review tools' docstrings and bodies leave "status, plan, premium total and policy-on-file details ... as they
    are".
  So the corpus would teach a state change that the rule's own tool contradicts, and would leave the policy-details update
  undefined for this case.
- Needed: a replaced_by that names its own scope and states the open-record outcome. Either accepted re-reviews on open
  records also leave status and policy details unchanged, with the base status-return clause retired for them, or the base
  content is restated for them.

## R5. A rule and replaced_by sentence names a sibling policy's factor quantity (coordinator: rule sentence naming factor quantities)
- Where: cpi_ext_upload_proof_rereview rule (l.1315) and overwrite replaced_by (l.1295): "In a re-review, an uploaded binder
  is held to the reach test with no expiry buffer, because a binder is temporary by nature, and its comprehensive ceiling
  takes no loan-to-value allowance."
- "loan-to-value allowance" is a declared factor quantity of the feed and fax policies (feed_ltv_allow / fax_ltv_allow), not
  of this policy. No upload document can carry it without describing a factor of another policy, or, in the computation
  document, signalling that ceiling allowances exist.
- This replaced_by retires the expiration-date clause, but its last clause is about the deductible ceiling, which is
  unrelated to the retired clause.
- Needed: delete ", and its comprehensive ceiling takes no loan-to-value allowance" from both places. The compute
  (`ul_comp > P('borrower_max_deductible_usd') + ul_age_allow`) already fixes the ceiling.

## R6 (lower severity). "binder_accepted" part of a retired clause is not restated for out-of-scope cases (XF D.19)
- Where: the feed overwrite (l.1062-1064) and fax overwrite (l.1691-1693) retire "A binder is accepted only when
  binder_accepted is true and the binder period is no longer than binder_max_days." The out-of-scope restatement ("Outside
  this rule ... acceptance requires ... a binder period no longer than binder_max_days") never restates the
  "binder_accepted is true" condition.
- After the base document marks the clause no longer in force, no in-force sentence carries it.
- Needed: add "binder_accepted is true and" to the outside-rule restatement, or scope the retired clause.

## R7 (lower severity). Unstated ordering key for "most recent capitalised premium charge"
- Where: closing-month rule/baseline (l.1483) and closing-period rule/baseline (l.1933): "The charge the closing-month
  refund refunds is the most recent capitalised premium charge on the record ...".
- The compute picks the charge by latest billing_period_start (`LATEST(..., date_field='billing_period_start', ...)`,
  l.1514/l.1956), not by billing date. A re-billed held premium for an earlier period carries a later billing date.
- Needed: say "the capitalised premium charge with the latest billing_period_start".

## Note (not a stop reason)
- cpi_ext_closing_period_refund has `trigger: state_due` (l.1919). Its target tool `mail_closing_period_refund_6483f0cd` is
  owner=user, and its docstring opens "The borrower requests ...". Worth a coordinator check that the trigger and the
  customer-run tool agree.
