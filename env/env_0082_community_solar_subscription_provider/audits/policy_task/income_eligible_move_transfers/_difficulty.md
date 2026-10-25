# Policy-task audit — income_eligible_move_transfers / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-25T09:21Z (UTC), auditor: independent policy-task auditor (not the instantiator). Written before any task's GT was revealed; contains nothing derived from a revealed GT.
- Freeze hashes (re-computed with sha256sum, identical to /tmp/erl0082_coord/snaps/income_eligible_move_transfers.r1.txt):
  - `access.extended.yaml` 2cb9c1dace8fa5bb5f01a49433c4bcc13295692b3134cd18ff8dfb8641bf2c53
  - `task_tools.py` e7186b55e9037acd818d635030689303984966330a4afa4a45abf258d785c6a1
  - `blueprint/products/access.yaml` a0fd7c67945e1ae3fbb472b73e07f63455f3b157abfa5ebd85dc0bcfcbb37b09
  - views: task0 4baf64a3…1732, task1 84558110…1405 (match the snapshot).
- Entry conditions: gate snapshot supplied with commands and output lines (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK); masked views supplied with hashes. Complete.
- Read: blueprint.yaml, db_schema.json, share_tools.py (tool list), products/access.yaml (whole), products/home.yaml (Standard 10 parameters, conversion sentence), the extended charter (whole), task_tools.py (whole), the two masked views, coordinator files XF_recipe.md, realism_bar.md, owner_ruling.md, the DSL helper bodies in skills/erl-task-instantiate/scripts/check_compute.py (MONTHS/DAYS/_within/LATEST/CFIELD/XCOUNT semantics).
- Masked / not read: tasks/*.json (all fields), worklog.md, plan.md (never opened), any audits of other difficulties, any other scenario.
- Scratch (re-runnable): /tmp/audit_income_eligible_move_transfers_0082/derive.py, t0.py, t1.py, alt.py, alt1.py (evaluate the charter's own compute on the masked views plus the auditor's own predicted writes).

### base copy
`diff <(head -1915 access.extended.yaml) blueprint/products/access.yaml` differs only by the four added comment/blank lines before `extended_policies:` — the base section is verbatim.

### policy_conflict_scan
Seven extended policies, seven tools:

| policy | subject | target_tool | scope (record test) |
|---|---|---|---|
| access_ext_move_reassignment_sizing | access_allocation_reassigned | file_move_reassignment_5a7d54a1 | move transfer to a new account with empty usage_as_of_month |
| access_ext_move_settlement_payment | access_payment_received | pay_move_settlement_0f5b0288 (user) | status transfer_pending |
| access_ext_move_pending_estimate | access_charge_billed | bill_pending_estimate_ff226895 | transfer_pending, 1..estimate_basis_months actual charges |
| access_ext_move_partial_reversal_credit | access_billing_credited | credit_partial_reversal_7609dc6e | transfer_pending, reversal credited_kwh below the reversed line's |
| access_ext_move_closing_payment | access_payment_received | pay_closing_balance_ce594868 (user) | closed with moved_out_of_territory / transfer_not_completed / eligibility_lapsed |
| access_ext_move_closing_estimate | access_charge_billed | bill_closing_estimate_4dff6268 | closed at a move, 1..(estimate_basis_months−1) actual charges |
| access_ext_move_closed_reversal_credit | access_billing_credited | credit_closed_reversal_cc3dddf3 | closed at a move, partial reversal |

- Pairs on overlapping subjects (the two payments, the two estimates, the two reversal credits) are separated by status (transfer_pending vs closed) in their own rules; the rules themselves do not overlap. Their overwrite tails do (finding C-RED-4).
- Claimed scope (from the brief; the task files' charter_scope is masked): task 0 is the transfer_pending tree (reassignment ← settlement ← partial reversal credit + pending estimate), task 1 the closed-at-move tree (closing payment ← closed reversal credit + closing estimate). Read from the prerequisite graph, the two trees are disjoint and together cover all seven policies. Disjointness against the task files is checked again after the reveal.
- Claim boundary against the blueprint: see C-RED-1.
- Trigger rule (F4): the events written are access_allocation_reassigned, access_allocation_reduced (move_resize), access_payment_received, access_charge_billed, access_billing_credited. Base `triggers` of each is `[]`, so nothing lands in another category. PASS.

### rule_compute_equivalence
- A scratch sweep (normalised whitespace) finds every `compute_basis` quotation, every `baseline.rule`, every `overwrite.replaced_by` and every `prerequisite.policy_source` verbatim in its own rule (E5 PASS). Every factor binding exists in compute, and no binding is shared by two factors.
- Every ladder tier is a sentence of its rule and a branch of its `decides` binding (no tier lives only in compute).
- Defects (members listed exhaustively in **findings**): C-RED-5 (non-commuting adjustments with no stated order), C-RED-6 (rule words ≠ compute: window conventions, a rounding applied only in compute, an inherited cap missing from compute), C-RED-7 (same-day tie rules and decoy/second-record probes).
- Probes run with DSL semantics (check_compute.py): `within_months=N` keeps a row iff 0 ≤ MONTHS(row_date, NOW) < N, where MONTHS counts whole months by day of month. `LATEST` takes the strictly greatest date key, so the first row seen wins a tie. `CFIELD` takes the first match. `XCOUNT/XLATEST` read every home row of the customer that matches the exact filters.

### action_binding_and_uuids
- Each `(target_tool, computes)` is claimed by exactly one policy. uuid8s 5a7d54a1, 0f5b0288, ff226895, 7609dc6e, ce594868, 4dff6268, cc3dddf3 show no shared prefix or sequence and none is reused. PASS.
- No docstring names another tool or states a position in a sequence. Two docstrings carry temporal words that describe world state rather than tool order: "stays in transfer_pending status until the utility applies the filing" and "partly reversed once a subscription charge had priced it" (observation O-8).
- G1: no datetime/time/random/uuid/secrets imports, and the rounding helper is a class static method. G5: no factor id is a substring of a tool name. G4: no composite arguments. PASS.
- No tool refuses a call, errors or hints when a prerequisite is unresolved (no body checks status, payment or credits). PASS.
- Tool-body defects (derived values; docstring claims the body does not enforce): C-RED-15.

### prerequisite_graph
- Every policy fills `prerequisite`. The edges are:
  - reassignment → settlement (state_gate, gate access_billing.bill_date)
  - settlement → partial_reversal_credit (value_input, credits_total)
  - settlement → pending_estimate (value_input, estimate_open)
  - closing_payment → closed_reversal_credit (value_input, credits_total)
  - closing_payment → closing_estimate (value_input, estimate_open)
- Every `problem` is an extended id of this file; no self-edges; the graph is acyclic.
- Every `policy_source` is verbatim in the blocked rule, every edge is in state form with no fallback_reason, `resolved_by` equals the depended-on target_tool, and each value_input `gate` names a binding that exists in the blocked compute. The `effect` texts are true of the compute: credits_total is deducted, and estimate_open enters the open-estimate share and prepay_basis.
- `condition` against sentence: C-RED-9 (reassignment edge) and observation O-4 (closing-estimate edge).

### prerequisite_sentences
Four-point test, per edge:

1. reassignment ← settlement: "The reassignment of the share to the new account is filed only after the subscription carries a move settlement payment received on or after the move-out date the household stated."
   - Points: ordering connective "only after" ✓; a record state (a payment line dated on or after move_out_date) ✓; no tool, id or snake_case ✓.
   - Strength: the sentence is narrower than the condition → C-RED-9.
   - Resolving write: of this difficulty, only pay_move_settlement applies to a transfer_pending share (pay_closing_balance is scoped to closed shares by its rule).
   - Derivation: no payment line dated ≥ move_out_date → the settlement rule (whose rule says the household pays it itself through the portal) → the household pays the figured amount → the reassignment may be filed. Single reading in the task worlds.
2. settlement ← partial reversal credit: "…fixed only after every reversal line posted on the subscription carries its reversal-correction billing credit."
   - Points: ✓ on all four; strength equals the condition.
   - Resolving write: the transfer_pending partial-reversal rule is the only extended rule covering a transfer_pending reversal. credit_closed_reversal would write an identical line, but its rule scopes it to closed shares (O-3).
3. settlement ← pending estimate: "…not fixed until every statement month that has gone the plan's estimate waiting period after its end without a posted credit carries an estimated charge."
   - Points: ✓; strength equals the condition.
   - Resolving write: bill_pending_estimate within its scope.
   - Satisfiability: C-RED-8(c).
4. closing payment ← closed reversal credit: same as edge 2, scoped to closed shares.
5. closing payment ← closing estimate: "…every statement month before the closing…". The condition omits "before the closing" (O-4). Satisfiability: C-RED-8(c).

Further checks:
- No rule carries a second wording, tool name or problem id. The depended-on rules do not restate the sentence.
- No other cross-problem order is stated in any rule.
- One reference to a later write appears with no numeric effect: the settlement's "final statement month (the month before the reassignment takes effect)" (O-10).

### override_declarations
Sentence-by-sentence against each base_policy_refs entry (findings only):
- **reassignment_sizing**: refs transfer_at_move, agg_account_sizing, allocation_change and eligibility_tracks.
  - Declared and scoped: the resize sentence of transfer_at_move; the usage-age sentence of agg_account_sizing.
  - transfer_at_move "The reassignment is filed under the filing calendar of access_allocation_change, counted from the request's received_date, and the subscription returns to active on its effective date" is contradicted, and not declared, by the added payment gate → C-RED-3.
  - Window, account, same-utility, lapse and eligibility-follows-household sentences are followed, as are filing-calendar and company-initiated-line sentences.
- **settlement / closing payment** (overwrite []): refs payment_application, subscription_charge, benefit_basis.
  - Payment order is followed. The narrowing to ach/card in the portal does not conflict.
  - subscription_charge "The whole credit_value is priced whether the utility applied it … or banked part of it": the unbilled-statement valuation contradicts this as a realism defect (C-RED-13); it is a payment figure, not a charge, so it is not an override.
- **pending / closing estimate**: refs subscription_charge, recertification, benefit_basis.
  - The estimate clause is declared and scoped.
  - access_benefit_basis "a subscription's charges are priced only by its own plan's pricing (its savings_rate_pct …); no promotion, referral reward, second subscription, waitlist reservation or other line's plan changes that price, and benefits never stack" is contradicted, and not declared, by the four percentage haircuts on the estimated charge → C-RED-2.
  - max_consecutive_estimates is inherited (see C-RED-8(c)).
  - Sibling tails conflict → C-RED-4.
- **partial / closed reversal credit**: refs credit_correction, recertification, benefit_basis.
  - The full-amount sentence is declared and scoped.
  - The inherited "Billing credits never carry a negative amount and never exceed the line they correct" is not implemented in compute (C-RED-6).
  - Sibling tails conflict → C-RED-4.
  - The lapse pricing follows access_recertification (rate keyed on the reversed line's posting date).

### factor_ladders
Structure only — weight is per task. Every declared ladder has three tiers stated in its rule, and the tiers are disjoint by their sequential "when…; when…; otherwise" wording. Realism grades against realism_bar.md and XF:

| policy | factor | label | grade | reason |
|---|---|---|---|---|
| reassignment_sizing | record_source (home, multi-source) | method | accepted (R6-WAIVED) | a converted residential true-up as the move consumption record is plausible; pairwise: T1 vs T3 differ by input (home_reviews vs access_reviews), T2 (whole share) adds no usage input |
| | banking_cap | parameter | R6-WAIVED | a lower sizing cap for frequently banked credits is a plausible company schedule |
| | verification_age_allowance | parameter | **RED** C-RED-13 | the age of income verification has no bearing on the kW a household's usage supports |
| | share_size_allowance | parameter | **RED** C-RED-13 | a 2–4 % haircut on larger shares at a move is no sizing practice |
| | restatement_allowance | parameter | **RED** C-RED-13 | a utility reversal shrinking the share is invented |
| | conversion_allowance (home) | parameter | **RED** C-RED-13 | a recent residential conversion shrinking the share is invented |
| settlement_payment / closing_payment (identical ladders) | not_yet_due_share | parameter | **RED** C-RED-13 | 0/50/100 % of not-yet-due charges keyed on days since move-out is invented |
| | open_estimate_share | parameter | **RED** C-RED-13 | half an estimate keyed on a count of recent actuals is invented |
| | unbilled_statement_share | parameter | **RED** C-RED-13 | a share keyed on request age is invented |
| | unbilled_banked_value | method | **RED** C-RED-10/12/13 | tiers 1 and 3 differ by a constant multiple (credit/2 vs credit on tier 1's domain), so it is a parameter; it acts only through unbilled_statement_share; it contradicts base whole-credit pricing |
| | final_month_prepay_share | parameter | **RED** C-RED-13 | demanding prepayment of a final month from an income-eligible household, keyed on days since its last payment, is invented |
| | final_month_prepay_basis | method | **RED** C-RED-12 | tiers distinct (estimate / average of actuals / latest actual), but it acts only through final_month_prepay_share (T2 fails; the tier acts on no baseline quantity) |
| pending_estimate | basis_rate_restatement | method | R6-WAIVED | billed − billing_error / restated / billed: distinct inputs |
| | reversal_deduction | method | **RED** C-RED-10 | tier 1 "nothing comes off" ≡ fall-through "nothing comes off" |
| | young_share_pct | parameter | **RED** C-RED-2/13 | a new-share discount on a charge (X1) |
| | request_wait_pct | parameter | **RED** C-RED-2/13 | a goodwill cut for waiting (X2) |
| | moved_out_pct | parameter | **RED** C-RED-2/13 | invented |
| | share_band_pct | parameter | **RED** C-RED-2/13 | invented |
| partial_reversal_credit | reversed_part_rate | parameter | accepted | the lapse rate or the rate actually billed is real correction practice |
| | corrected_value_basis | method | **RED** C-RED-10 | tier 1 "rev_kwh × line_value / line_kwh" ≡ tier 2 "line_value × rev_kwh / line_kwh" (probe: 88.074 = 88.074) |
| | held_interest_rate | parameter | **RED** C-RED-13 | held-payment interest on a reversal correction is no community-solar practice; the baseline itself carries it |
| | held_days_start | method | **RED** C-RED-13 | same invented interest mechanism |
| | interest_year | parameter | **RED** C-RED-11/13 | a 360- vs 365-day year by payment method is X4; fall-through "no interest" ≠ baseline 365 |
| | restatement_lag_uplift | parameter | **RED** C-RED-13 | invented |
| closing_estimate | residential_fill (home, multi-source) | parameter | R6-WAIVED (label O-2) | filling the estimate basis from the converted plan's statements is plausible |
| | reversal_restatement | method | R6-WAIVED | sum−rev & count−1 / sum−rev / as posted: distinct |
| | young_share_pct, request_age_pct, departure_pct, share_band_pct | parameter | **RED** C-RED-2/13 | as in the pending estimate |
| closed_reversal_credit | reversed_part_rate | parameter | accepted | |
| | corrected_value_basis | method | **RED** C-RED-10 | identical tiers 1/2 |
| | held_interest_rate, held_days_start | param / method | **RED** C-RED-13 | invented interest |

Declared counts: 6/6/6/6/6/6/4 factors; every policy has ≥2 parameter and ≥1 method; the cross_difficulty factors (home) are record_source, conversion_allowance and residential_fill. Task 0 gets a multi-source + cross factor from record_source, task 1 from residential_fill.

Factors surviving the tests (C-RED-14):

| policy | surviving | count |
|---|---|---|
| reassignment | record_source, banking_cap | 2 |
| settlement | — | 0 |
| pending estimate | basis_rate_restatement | 1 |
| partial reversal | reversed_part_rate | 1 |
| closing payment | — | 0 |
| closing estimate | residential_fill, reversal_restatement | 2 |
| closed reversal | reversed_part_rate | 1 |

Every computation is below the floor of 4.

Baselines:
- Self-sufficient except closing_estimate (C-RED-11).
- Every fall-through equals its baseline except interest_year (C-RED-11).
- baseline.params agree with the baseline paragraphs (A8 PASS).
- The baselines of the reversal credits carry the invented interest (C-RED-13).

### findings
Each finding lists every member found in one pass. "Tasks" names which task files demonstrate the consequence.

**C-RED-1 SOURCE-POLICY — subjects outside the difficulty's claimed event types.** Tasks 0, 1.
- Symptom: four policies write events the blueprint does not claim for this difficulty.
- Evidence: blueprint.yaml claims `event_types: [access_transfer_requested, access_transfer_completed, access_transfer_lapsed, access_allocation_reassigned, access_allocation_reduced, access_recertified, access_charge_billed]`, and its summary says "The agent records the transfer outcome, reassignment, resize or lapse and any recertification".
- The subjects outside that claim:
  - access_payment_received: settlement_payment, closing_payment
  - access_billing_credited: partial_reversal_credit, closed_reversal_credit
- Consequence: both task roots and two of the five prerequisite problems sit outside the declared scope. The SCOPE gate does not test this.
- Affected: the `subject` of those four policies, with their tools.

**C-RED-2 SOURCE-POLICY — undeclared override of access_benefit_basis.** Tasks 0, 1.
- Base: "a subscription's charges are priced only by its own plan's pricing (its savings_rate_pct …) … and benefits never stack".
- Extended:
  - pending_estimate result `basis_average * young_pct/100 * wait_pct/100 * moved_out_pct/100 * share_pct/100`
  - closing_estimate result `… * young_pct * gap_pct * departure_pct * share_pct`
- Neither policy's overwrite names access_benefit_basis.
- Consequence: an estimated charge read under the benefit rule carries no haircuts. Task 0: 55.55 vs 46.58 (settlement 124.96 vs 111.50). Task 1: 51.91 vs 42.64 (closing payment 108.98 vs 95.08).

**C-RED-3 SOURCE-POLICY — undeclared override of access_transfer_at_move by the payment gate.**
- Base: "The reassignment is filed under the filing calendar of access_allocation_change, counted from the request's received_date".
- Extended: "filed only after the subscription carries a move settlement payment received on or after the move-out date".
- The reassignment's overwrite names only the resize sentence.
- Consequence:
  - For a qualifying transfer whose household has not paid, base files the reassignment and extended never does. Neither base lapse condition ("different utility" / "no qualifying new account … within the window") then applies, so the share sits in transfer_pending with no rule that ends it.
  - Task 0: under base the write set is the reassignment alone, without the three settlement writes.

**C-RED-4 SOURCE-POLICY — sibling overwrites retiring the same base clause each send the sibling's case back to base (XF E3).** Tasks 0, 1.
- Members:
  - (a) pending_estimate replaced_by "…every other estimate remains under the base rule…": covers task 1's closed share → base estimate 56.92 vs closing rule 42.64.
  - (b) closing_estimate replaced_by "…every other estimate remains under the base rule…": covers task 0's transfer_pending share → base estimate 63.50 vs pending rule 46.58.
  - (c) partial_reversal_credit replaced_by "…every other reversal remains under the base rule…": covers task 1 → full charge 63.61 vs 22.45.
  - (d) closed_reversal_credit replaced_by "…every other reversal remains under the base rule…": covers task 0 → full charge 79.38 vs 34.28.
- Demonstrated: settlement 91.78 vs 111.50 (task 0); closing payment 75.34 vs 95.08 (task 1).

**C-RED-5 SOURCE-POLICY — non-commuting adjustments with no stated order (XF A3).**
- Members:
  - (a) pending_estimate: "Each adjustment below changes the basis sum or sets a percentage" fixes no order between basis_rate_restatement, which REPLACES the basis sum ("the basis sum is the restated sum"), and reversal_deduction, which SUBTRACTS from it. Task 0: restate then deduct → 46.58; deduct then restate → 55.63 (settlement 125.08).
  - (b) closing_estimate: residential_fill's "the estimate basis lacks (estimate_basis_months less the basis count)" does not say whether the count is taken before or after reversal_restatement's "the basis count falls by one". Compute takes it before. This differs whenever the reversal month was re-posted (tier 1); task 1 is on tier 2, so there is no task consequence.

**C-RED-6 SOURCE-POLICY — rule words ≠ compute at edges (XF B5/C3).**
- Members:
  - (a) settlement and closing_payment: "invoiced in the last two whole calendar months" is computed as `within_months=2`, i.e. MONTHS(bill_date, NOW) < 2.
    - A bill dated 2026-08-10 with NOW 2026-10-20 falls in August (a whole calendar month) but MONTHS = 2, so it is excluded.
    - A bill dated 2026-10-05 is in no whole calendar month but MONTHS = 0, so it is counted.
    - The tier flips between 100/50/0 %.
  - (b) Month conventions are left unstated where compute uses MONTHS / within_months, all in reassignment_sizing:
    - "posted in the last twelve whole months" (banking)
    - "posted in the last three whole months … three to eleven whole months before" (restatement)
    - "fewer than six whole calendar months … six to eleven" (conversion)
    - "more than record_max_age_months whole calendar months" (record_source)
  - (c) partial and closed reversal credit: "differs by more than one cent from the reversed line's credit_value multiplied by (100 minus savings_rate_pct) and divided by 100" is computed against RND(…, 2). Probe: line 88.21, charge 70.58 — the rule gives |70.58−70.568| = 0.012 > 0.01 (off-plan tier); compute gives |70.58−70.57| = 0.01, not > 0.01 (plan tier).
  - (d) partial and closed reversal credit: the inherited base cap "never exceed the line they correct" has no MN in compute. Probe: 699 kWh reversed of 700, charge 70.56, interest 8 %/yr for 70 days on a 360-day year → correction 71.56 > 70.56.

**C-RED-7 SOURCE-POLICY — missing tie rules and failed decoy / second-record probes (XF C1/C2).**
- No same-day tie rule for LATEST:
  - settlement and closing_payment: latest_credit_id, latest_credit_value/banked, latest_estimate, latest_actual, last_pay_date
  - pending and closing estimate: latest_posted_id/value
  - partial and closed reversal: pay_date and pay_method (two payments on one day by different methods flip interest_year)
- Decoy: closing_estimate res_statements and res_latest_value filter home_credits by utility_account_id, while the rule says "that plan carries … the converted residential plan's home_credit_posted line". Another residential plan's credits on the same account (e.g. an earlier plan closed by subscriber_cancellation) are counted by compute and excluded by the rule.
- Second record: reassignment res_sub, res_contract_kw and res_closed_date take the first CFIELD match. Two converted residential plans on one account (different projects) leave the rule unresolved, while compute takes whichever row comes first.

**C-RED-8 SOURCE-CHAIN — prerequisites not satisfiable in every engaged world (XF F1/F2).**
- Members:
  - (a) Settlement figure 0.00. The baseline alone yields 0.00 in both task worlds, and any fully paid household with move-out today gets 0.00. No payment > 0.00 can then be recorded (schema `amount` is "greater than 0.00"; the tool says the same), so "carries a move settlement payment" can never hold and the reassignment is never filed. There is no de minimis carve-out.
  - (b) A household calling before its stated move-out date — the blueprint's "people about to move" — cannot have a payment "received on or after the move-out date". The reassignment must wait for the calendar (a real-world wait).
  - (c) Estimate gates (settlement and closing_payment): with two consecutive statement months past the wait without credits, base "no more than max_consecutive_estimates estimates may be billed in a row" (= 1 on every Access plan) bars the second estimate. "Every statement month … carries an estimated charge" is then unreachable, and the root is never fixed.

**C-RED-9 SOURCE-POLICY — prerequisite sentence narrower than its condition.**
- The reassignment edge sentence requires "a move settlement payment received on or after the move-out date". The condition (and gate access_billing.bill_date) accepts "an access_payment_received line whose bill_date is on or after the subscription's move_out_date".
- A producible world: a portal payment of an old invoice made after move-out. The condition holds, so the edge is already satisfied at the opening, while the sentence does not, so the reader still waits. Two readings.

**C-RED-10 SOURCE-FACTOR — duplicate or constant-multiple tiers.**
- reversal_deduction: tier 1 ≡ fall-through.
- corrected_value_basis, in both reversal credits: tier 1 ≡ tier 2.
- unbilled_banked_value, in both payments: tier 1 vs tier 3 differ only by a constant multiplier on tier 1's domain (credit/2 vs credit). This is a parameter labelled method.

**C-RED-11 SOURCE-FACTOR — dishonest or incoherent baselines.**
- interest_year: fall-through "otherwise no interest" ≠ baseline year_days 365, and tier 2 (ach/card → 365) equals the baseline.
- closing_estimate baseline.rule ("multiplied by (100 minus the rate in force on the estimate date)") does not define the rate in force. Its definition sits outside baseline.rule, so the computation document alone gives 56.92 or 47.43 in task 1.

**C-RED-12 SOURCE-FACTOR — factors acting only through another factor's tier (XF A1/A6 T2).**
- unbilled_banked_value (both payments) moves the result only when unbilled_statement_share ≠ 0.
- final_month_prepay_basis (both payments) moves it only when final_month_prepay_share ≠ 0.
- Both factors' quantities are absent from the baseline, so the coordinator's T2 waiver does not apply.

**C-RED-13 SOURCE-FACTOR — unreal ladders (realism bar; every member is listed in factor_ladders).**
- Invented mechanisms or X-kinds:
  - 4 reassignment allowances
  - all 6 factors of each payment policy (12), with the not-yet-due, open-estimate, unbilled-statement and final-month-prepayment components they price
  - 4 percentage haircuts in each estimate policy (8)
  - the held-payment interest in both reversal credits: the baseline sentence plus 4 + 2 factors
- Contradiction with the charter's own pricing: unbilled_banked_value values a statement at credit−banked(+banked/2), while base prices "The whole credit_value … whether … banked".
- closing_payment's "final statement month (the month before the closing date)" is, for a share closed at a move, a month already posted and billed — task 1 shows it collected a second time.

**C-RED-14 SOURCE-FACTOR — factor floor after the tests.** Surviving counts 2/0/1/1/0/2/1 (factor_ladders), all below 4. Tasks 0, 1.

**C-RED-15 SOURCE-POLICY — tool bodies (skill rule; XF G3).**
- (a) file_move_reassignment_5a7d54a1 computes `removed = allocation_kw − kept` and writes it as the move_resize kW, a derived value.
- (b) pay_move_settlement_0f5b0288 and pay_closing_balance_ce594868 set `billing_month=today[:7]`, where the schema meaning is "statement month the line belongs to" — a body-chosen field.
- (c) All 7 docstrings claim "greater than 0.00" for kw/amount; no body enforces it.
- (d) The bill_*_estimate docstrings say access_credit_id "is passed as an empty string", but the body writes whatever is passed.
- Members total 11 (1 + 2 + 7 + 2 counted per tool).

**Observations (not grounds for rework)**
- O-1: R6-WAIVED / accepted factors: record_source, banking_cap, basis_rate_restatement, residential_fill, reversal_restatement, and reversed_part_rate ×2.
- O-2: residential_fill is labelled parameter though its tiers bring a home input into the basis. The tier outcomes are counts, so the label is defensible.
- O-3: bill_pending_estimate / bill_closing_estimate and credit_partial_reversal / credit_closed_reversal write identical lines with no status test. The hop is resolved only by the rules' scopes.
- O-4: the closing-estimate edge condition omits "before the closing".
- O-5: settlement's "past-due balance" collides with the name of base measure access_msr_past_due_balance (per-line unpaid amounts, fees included, never negative). The extended rule spells out its own figure, so the reading is unique.
- O-6: "when the share kept would be below min_allocation_kw the transfer is not completed" has no computed branch and no tool. Claimed access_transfer_requested/completed/lapsed/recertified have no extended policy.
- O-7: the reassignment tool writes access_allocation_reassigned standalone, while in base it is a trigger of access_transfer_completed. The future completion may emit a second line.
- O-8: docstring temporal words "until" and "once" (world state, not tool order).
- O-9: the user pay tools enumerate `check`, though the rule says "by ach or card through the portal".
- O-10: settlement's prepayment month refers to "the month before the reassignment takes effect" — a later write — with no numeric effect.
- O-11: reversed_part_rate tier 2 presumes an uncorrected charge billed off plan, a world in which base access_evt_credit_correction makes a billing_error credit owed (owed-write class). No task world reaches that tier.
- O-12: the schema says move_out_date and pending_utility_account_id are "empty when no transfer is pending", yet base access_transfer_lapsed does not clear them, and closing_payment's not_yet_due ladder reads move_out_date on a closed share.

## closing_checklist
Written after both reveals (2026-10-25T09:3xZ). The difficulty does **not** close.
- Per-task files: 0.md and 1.md correspond one-to-one with tasks 0 and 1, and _difficulty.md sits alongside them. This is revision_1, so there are no older revisions.
- Comparison sections: both carry RED, not PASS.
- Scopes, from charter_scope:
  - task 0 = {reassignment_sizing, settlement_payment, pending_estimate, partial_reversal_credit}
  - task 1 = {closing_payment, closing_estimate, closed_reversal_credit}
  - Pairwise disjoint and jointly covering all 7 extended policies ✓. Tools are disjoint per task ✓. uuid8s independent ✓.
- Trees: task 0 has n = 3 with 2 value_input edges; task 1 has n = 2 with 2. Each has one owner=user write, and the difficulty-wide graph is acyclic ✓. The gates are unsatisfiable in engaged worlds (C-RED-8) ✗.
- Factors: declared 4–6 per computation, each bearing weight on its task world (T1 all ✓; GT figures match the auditor's figure for figure). After realism, ladder and A1 tests every computation has fewer than 4 surviving factors (C-RED-13/14) ✗.
- Instantiation gates: not re-run, because no final form exists (the artifacts must be reworked). The round-1 snapshot gates were all OK, which qualified the difficulty for this manual audit only.

VERDICT revision_1: task0=RED task1=RED charter=C-RED-1,C-RED-2,C-RED-3,C-RED-4,C-RED-5,C-RED-6,C-RED-7,C-RED-8,C-RED-9,C-RED-10,C-RED-11,C-RED-12,C-RED-13,C-RED-14,C-RED-15
