# Policy-task audit — worker_payroll_card_servicing / charter-global

## charter_global_frozen
- revision: revision_1 (first audit of this difficulty; no older revision exists)
- freeze time: 2026-10-23 00:43 UTC (written before any task's GT was revealed)
- auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiator
- inputs and hashes (sha256, first 16 hex): `card.extended.yaml` = adc802b0d386759f, `task_tools.py` = b9894d2a0f20e886 (both match the gate snapshot `/tmp/erl0077_coord/snap_worker_payroll_card_servicing_r1.txt`); views `.audit_views/policy/worker_payroll_card_servicing/r1/0.view.json` = 62cdc6f907511e34, `1.view.json` = b1e9238a237d5944 (match)
- read: blueprint.yaml, db_schema.json, share_tools.py, products/card.yaml (base), products/access.yaml (cross-category charter, for pricing checks), the extended charter, task_tools.py, the two masked views (frozen_time, user_scenario, initial_state), `audits/render_source/XF_recipe.md`, `audits/render_source/owner_ruling.md`
- masked / not read before the freeze: tasks/*.json (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), the instantiator's plan.md and worklog.md, every other audit directory, every other env and every sibling difficulty's tasks directory
- entry conditions (Step 0): gate snapshot supplied with all 7 gates OK (EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE); masked views supplied with hashes; check_traceability deferred by the coordinator. Entry conditions complete.
- scratch: `/tmp/audit_worker_payroll_card_servicing_0077/` (evaluator `scripts/ev.py` runs each policy's own `compute` through `check_compute.build_env` on the view's initial_state; no GT is read)
- base copy: the base sections of `card.extended.yaml` (category … policies) are equal, key by key, to `blueprint/products/card.yaml` (parsed YAML comparison: all 10 keys equal).

### policy_conflict_scan
Six extended policies, each with its own subject and tool:

| policy | subject / computes | tool (owner) | trigger | claim it selects |
| --- | --- | --- | --- | --- |
| card_ext_signed_loss_claim_credit (SL) | card_provisional_credit / credit_usd | sign_card_loss_claim_statement_562d448e (user) | on_request | latest investigating phone claim with no written confirmation |
| card_ext_claim_credit_reversal (RV) | card_provisional_credit_reversal / reversal_usd | reverse_card_claim_credit_df02de93 (agent) | state_due | claim of the latest posted provisional credit (resolved, first of its loss) |
| card_ext_error_claim_final_credit (UC) | card_final_credit / credit_usd | post_card_error_claim_credit_b4851c9e (agent) | state_due | latest resolved_error_found ATM-cash-not-dispensed claim with no provisional credit |
| card_ext_withdrawn_claim_reversal (WD) | card_provisional_credit_reversal / reversal_usd | withdraw_card_claim_862dc9d0 (user) | on_request | latest investigating unauthorized claim |
| card_ext_written_cash_claim_credit (WC) | card_provisional_credit / credit_usd | post_card_cash_claim_provisional_265c4f8c (agent) | state_due | latest investigating ATM-cash claim reported in writing, no provisional credit |
| card_ext_unauthorized_cash_claim_credit (CH) | card_final_credit / credit_usd | post_card_unauthorized_claim_credit_b5638e78 (agent) | state_due | latest resolved_error_found unauthorized cash claim with no loss date and no provisional credit |

Overlaps: SL/WC share `card_provisional_credit`, RV/WD share `card_provisional_credit_reversal`, UC/CH share `card_final_credit`; each pair is separated by claim kind (phone/loss vs written ATM-cash; resolved vs withdrawn; ATM-cash vs card-in-hand unauthorized) in the rules, but NOT always in the compute selectors (see CG-8). Base clauses overwritten by several siblings: `card_evt_error_resolution` "When it cannot…" (SL, WC), "When an error is found…" (SL, UC, WC, CH), "A reversal never exceeds…" (RV, WD); `card_unauthorized_liability` "Otherwise liability…" (SL, RV, CH); `card_evt_fee_refunds` "Without any request…" (SL, UC, WC, CH). Sibling tails checked under override_declarations.
Scope: the tree each task's world yields (derived blind, see the task files) is task 0 = {UC, RV, SL}, task 1 = {WC, CH, WD}: pairwise disjoint and jointly complete over the six policies. Time anchors: frozen_time drives NOW; all windows are DAYS from record dates to NOW or between record dates. Terminal states: credit/reversal rows on card_transactions plus `written_confirmation_date` (SL) and `dispute_status=withdrawn` (WD). Cross-category reads: access only (RV, UC, WD), declared in `cross_category`.

### rule_compute_equivalence
- B5 sweep (scratch script): every `compute_basis` quote is verbatim in its own rule; every compute binding has a basis; every `policy_source`, `baseline.rule` and `replaced_by` is verbatim in its own rule.
- Rounding (B4): every rule says "rounded half up to the cent once at the end"; every `result` is `RND(… + 0.000000001, 2)` at the end only; tool bodies use `_CardLedger.cents` (Decimal, ROUND_HALF_UP, class static method). All task figures are at exact cents.
- Rule → compute gaps (rule words the compute does not implement), all charter-global, listed under CG-8:
  - SL: rule scopes "an unauthorized-transaction claim … after their card was lost or stolen" and "whose claimed transaction posted no more than error_notice_window_days calendar days after the history access date"; `s_dispute` filters only `dispute_status='investigating', notice_channel='phone', written_confirmation_date=None` (no `dispute_reason`). The 60-day clause is vacuous (history_access_date is by schema the date a history showing the transaction was first accessed, so it is never before posting).
  - RV: rule prices a reversal "once the claim it was posted on has been resolved", "after provisional_reversal_notice_business_days business days", on "an unauthorized-transaction claim priced as the first claim of its loss"; `v_dispute` = claim of the latest posted provisional credit with no status, reason, first-of-loss or business-day test, and `v_owed = v_prov` for every status other than resolved_error_found (an investigating claim's whole credit would be reversed).
  - UC: rule "carries no provisional credit"; `z_dispute` has no such test.
  - WC: rule "reported in writing", "once provisional_credit_business_days business days have passed", "which carries no provisional credit"; `q_dispute` filters only status and reason.
  - CH: rule "on a cash withdrawal", "carries no provisional credit"; `u_dispute` filters status, reason and `loss_learned_date=None` only.
  - All six: every "most recently …" selector (LATEST/XLATEST on notice_date, resolution_date, posted_date, entry_date) has no stated same-day tie rule; `CFIELD('access', …, status='active')` takes the first match while the rule speaks of "the cardholder's single active Paystride Access plan" with no rule for two active plans (RV, WD, UC), and the XSUM/XCOUNT access reads aggregate over all of the customer's plans.
- Compute → rule: no compute branch without a rule sentence; every ladder tier is a sentence of its rule and a branch of its `decides` binding.

### action_binding_and_uuids
- Each `(target_tool, computes)` is claimed by exactly one policy (six tools, six policies).
- uuid8s: 562d448e, df02de93, b4851c9e, 862dc9d0, 265c4f8c, b5638e78 — distinct, no shared prefix/suffix, no sequence; read as independently generated.
- Tool bodies: every write tool calls `ctx.create`/`ctx.update`; none validates a prerequisite (only `amount <= 0` and unknown dispute id are refused); no forbidden imports; no date maths. Docstrings carry no example values, no composite args, name no other tool; the SL docstring's "that they first reported by phone" describes the notice history, not an action order (observation O-3).
- Owner ruling (`owner_ruling.md`): SL signing the written confirmation of an oral Reg E notice = class (c)/(a) act of the holder; WD withdrawing one's own notice of error = class (c). Both accepted.

### prerequisite_graph
- `prerequisite` filled everywhere: SL → [RV state_gate], RV → [UC value_input on v_room], WD → [WC value_input on w_room, CH value_input on w_room], UC/WC/CH → []. All `problem` ids are extended policies of this file, none self, graph acyclic. Every `policy_source` verbatim in its own rule; all `form: state`, no `fallback_reason` (none needed). `gate` names: `card_transactions.credit_kind` (state field, SL), `v_room`, `w_room` (bindings that exist in the blocked compute).
- `resolved_by` vs sentence scope (CG-11): RV's sentence "A provisional credit reversal is not taken until every final credit and every overdue provisional credit owed on the account's other claims has posted." and WD's twin sentence cover every credit-posting policy of the charter (final credits: UC, CH; provisional credits: WC, SL), and each `condition` restates that full scope, but RV declares only UC and WD declares only WC and CH as resolvers. In a world where the owed credit is a card-in-hand final (CH) or a written-cash provisional (WC), RV's declared resolver cannot make its own condition hold; WD likewise for UC/SL credits. RV's sentence also covers SL's provisional credit while SL is declared to wait on RV — the declared graph hides a potential RV↔SL cycle.

### prerequisite_sentences
- SL: "The signed claim credit is fixed only after every other claim of the same loss whose provisional credit stood above what that claim was due carries its reversal." — connective "only after"; state "carries its reversal" (a provisional credit reversal row pointing to the claim's credit); no tool/id/snake token; one write brings it about (RV's reversal; WD's tool is for unresolved claims). Derivation: the reader finds the other claim of the same loss date, computes what it was due from RV's own rule, sees the credit stands above it, and finds that RV's rule prices that reversal.
- RV: "A provisional credit reversal is not taken until every final credit and every overdue provisional credit owed on the account's other claims has posted." — "not … until"; state "has posted"; no tool names. Which write brings it about depends on the kind of owed credit (UC, CH, WC or SL); in each world the claim kind singles out one policy, so the hop resolves per world (see CG-11 for the declaration side).
- WD: "A withdrawal reversal is not taken until every final credit and every overdue provisional credit owed on the account's other claims has posted." — same analysis.
- No depended-on rule restates the sentence; no rule states another cross-problem order. Base rule sentence with a cross-problem order ("A card reported lost or stolen is blocked before its replacement is ordered", card_evt_service_orders) grounds no edge here (observation).

### override_declarations
Sentence-by-sentence against `base_policy_refs` (card_evt_error_resolution, card_unauthorized_liability, card_evt_fee_refunds):
- SL: replaces the provisional-credit clause ("for a signed claim this policy prices, and only for such a claim, the provisional credit is the signed claim credit") — clean; the liability clause — tail names RV and CH siblings, clean; the "When an error is found" clause — names UC/WC/CH siblings, clean; the fee-correction clause — names all four, clean. Other base sentences (notice windows, statuses, dedup, posting only while investigating) inherited.
- RV: reversal-limit clause and liability clause, tails name WD/SL/CH; the base "When no error, or a smaller error, is found, the provisional credit or its excess is debited back" is followed (due = transfer less liability). Clean.
- UC: replaces "When an error is found …" with a text that keeps "a final credit of the error amount, less any cardholder liability" and scopes for an undispensed-cash credit only "the fees, retry cost and early pay cost it returns are returned within the credit". It does not declare that this policy reprices that credit (rebate-netted "undelivered cash amount", late-credit allowance), so the in-force restated clause still prices the undispensed-cash credit at "the error amount" (CG-9).
- WC: provisional clause, "When an error is found" clause, fee-correction clause — tails name the siblings, clean.
- CH: liability clause — tail names SL/RV siblings, clean, but the un-overwritten base sentence "The two caps apply only when the card itself was lost or stolen; when it was not, such as unauthorized use while the card is still in hand, liability is zero except for transfers that posted after that late-notice window and before the report." conflicts with CH's fall-through tier and baseline (liability up to liability_cap_timely_usd on a card-in-hand claim) — undeclared override (CG-6). "When an error is found" clause replaced by "… its final credit posts within error_correction_business_days business days and returns the fees set out here within the credit, no fee correction being booked for them; every other final credit and fee correction stays as the base rule and the other claim schedules state" — retires the whole clause with the forbidden "every other … stays as the base rule" tail and drops "a provisional credit already posted becomes final with no second credit" (C1/C4, CG-9). Fee-correction tail "within another claim credit that returns its fees" does not name the siblings (C3, CG-9).
- WD: status-gate and reversal-timing clauses (identical replaced_by, scoped to withdrawn claims) and reversal-limit clause — clean.

### factor_ladders
Declared factors (effect; decides; tiers):

| policy | factor | effect | tiers (fall-through last) | structural verdict |
| --- | --- | --- | --- | --- |
| SL | sl_transfer_basis | method | d−sur (reb≥sur) / d−reb (reb<sur) / d | one lesser-of: every tier = d − min(reb, sur) (CG-2) |
| SL | sl_liability_limit | parameter | 500 / 0 / 50 | real, multi-source (claim + transaction) |
| SL | sl_prior_liability | parameter | min(amt,50) / min(amt,500) / 0 | real |
| SL | sl_fee_return | parameter | intl+fx fee net / OON fee net / 0 | intl and OON tiers = "Paystride ATM fees on it, net" (CG-3) |
| SL | sl_day_fees | parameter | inq+dec / inq / 0 | all tiers ≡ inq+dec (CG-1) |
| SL | sl_service_allowance | parameter | 10 / 5 / 0 | distinct |
| RV | rv_transfer_basis | method | as SL | CG-2 |
| RV | rv_liability_limit | parameter | 500 / 50 / 0 | real, multi-source |
| RV | rv_carried_remainder | parameter | no-error remainder / withdrawn remainder / 0 | one method on two records, exclusive priority unreal (CG-4) |
| RV | rv_access_holdback | parameter (cross: access) | open shortfall / current early pay / 0 | realism (CG-5) |
| UC | uc_cash_basis | method | as SL | CG-2 |
| UC | uc_fee_return | parameter | as SL | CG-3 |
| UC | uc_day_fees | parameter | as SL | CG-1 |
| UC | uc_retry_cost | method | sur-left+fee / sur-left / 0 | tier 1 ≡ tier 2 (fee 0) (CG-2) |
| UC | uc_early_pay_cost | parameter (cross: access) | instant-ext fee net / NBD-bank fee net / 0 | tiers 1 and 2 identical method (CG-4) |
| UC | uc_late_allowance | parameter | 10 / 5 / 0 | distinct |
| WD | wd_fee_refunds | method | refunds on intl+fx / refund on OON / none | A6 fail: same aggregate (refund amount) under different filters; CG-3 |
| WD | wd_day_refunds | parameter | inq+dec refunds / inq refund / 0 | CG-1 |
| WD | wd_carried_remainder | parameter | as RV | CG-4 |
| WD | wd_access_holdback | parameter (cross: access) | as RV | CG-5 |
| WC | wc_cash_basis | method | as SL | CG-2 |
| WC | wc_fee_return | parameter | as SL | CG-3 |
| WC | wc_day_fees | parameter | as SL | CG-1 |
| WC | wc_overdue_allowance | parameter | 10 / 5 / 0 | distinct |
| CH | ch_transfer_basis | method | as SL | CG-2 |
| CH | ch_liability_limit | parameter | 500 / 0 / 50 | tier 1 unreachable; fall-through/baseline contradict base (CG-6) |
| CH | ch_fee_return | parameter | as SL | CG-3 |
| CH | ch_day_fees | parameter | as SL | CG-1 |
| CH | ch_late_allowance | parameter | 10 / 5 / 0 | distinct |

Bindings disjoint, `decides` never `result`, no factor reads another factor's binding (A1 table: SL `s_liability`, RV `v_liability`/`v_owed`/`v_room`, WD `w_room`, CH `u_liability` are plain assembly bindings), no factor id is a substring of a tool name (A8 sweep). Every tier is stated in the rule and implemented in `compute`.
Counts that survive the tests (CG-7): SL 3 (0 method), RV 1, UC 1, WD 0, WC 1, CH 1 — every policy is below 4 factors and has no `method` factor. Cross-difficulty factors surviving: none (rv/wd holdback struck by CG-5, uc_early_pay_cost by CG-4). Multi-source surviving: sl_liability_limit, rv_liability_limit only.

### findings
Each finding: verdict — symptom — root cause — evidence — demonstrated consequence — artifact/location — tasks it bears on. (First revision; no relation to earlier revisions.)

**CG-1 SOURCE-FACTOR RED — day-fee ladders are one formula.** sl_day_fees, uc_day_fees, wc_day_fees, ch_day_fees, wd_day_refunds. Compute (SL) `s_side: s_inquiry + s_declines if s_declines > 0 else (s_inquiry if s_inquiry > 0 else 0)`; with `s_declines = 0` the second branch returns `s_inquiry = s_inquiry + s_declines`, and the fall-through returns 0 only when both are 0, which equals `s_inquiry + s_declines`. All three tiers select "that day's balance inquiry and decline fees together" in every world (same for `z_day_fees`, `q_day_fees`, `u_day_fees`, `w_day_back`). Consequence: three tiers written for one rule vs its baseline 0; the ladder is not real (two tiers select the same value). Bears on tasks 0 and 1.

**CG-2 SOURCE-FACTOR RED — surcharge-basis "method" ladders are one lesser-of; retry ladder collapses.** sl_transfer_basis, rv_transfer_basis, uc_cash_basis, wc_cash_basis, ch_transfer_basis: tier 1 (reb ≥ sur) gives d − sur = d − min(reb, sur); tier 2 (0 < reb < sur) gives d − reb = d − min(reb, sur); fall-through (reb = 0) gives d = d − min(0, sur). The charter itself computes the same quantity for the prior claim as one expression, `s_prior_amount: … disputed_amount … - MN(SUM(…surcharge_rebate…), SUM(…atm_surcharge_usd…))`, and its rule words it as one figure ("that claim's disputed amount less the lesser of its surcharge rebate and its owner surcharge"). Every tier applies the same algorithm, so the `method` label is not honest and the ladder is one rule (A6/A7 class). uc_retry_cost: `z_retry: z_retry_left + z_retry_fee if (… z_retry_fee > 0) else (z_retry_left if z_retry_id != None else 0)` ≡ `z_retry_left + z_retry_fee` in every world. Bears on tasks 0 and 1.

**CG-3 SOURCE-FACTOR RED — network fee-return ladders are one tier written as two; wd_fee_refunds fails method shape.** sl/uc/wc/ch_fee_return select "the international ATM fee and the foreign transaction fee charged on it, less any part of them already returned" at an international ATM and "the out-of-network ATM fee charged on it, less any part of it already returned" out of network. Under card_evt_atm_and_foreign_fees an out-of-network withdrawal carries only the out-of-network fee, an international one only the international ATM and foreign transaction fees, and an in-network one none ("in_network_atm_withdrawal_fee_usd" is 0.0 on every plan and "A fee that comes to zero is not assessed"), so "the Paystride ATM fees charged on the withdrawal, less any part already returned" gives every tier's number in every world (for SL only the purchase case in the fall-through differs). wd_fee_refunds (`method`): tiers 1 and 2 are both SUMs of `card_fee_refund.amount` under different `related_txn_id` filters — the same combination of the same field (XF A6 fail), a mislabelled parameter at most, and the same one-tier-as-two collapse. Bears on tasks 0 and 1.

**CG-4 SOURCE-FACTOR RED — record-selection ladders with identical outcomes.** uc_early_pay_cost: tier 1 "that fee less any reversal of it" (instant transfer to an external debit card) and tier 2 "that fee less any reversal of it" (next-business-day transfer to a bank account) are the same method; the access charter has no instant-to-bank or NBD-to-debit-card fee and every Paystride-card fee is 0.0 (`instant_fee_paystride_card_usd`, `nbd_fee_paystride_card_usd`), so the ladder is "the early wage transfer fee booked that day, net" vs nothing. rv_carried_remainder / wd_carried_remainder: tier 1 and tier 2 both take "the unreversed part" of a provisional credit, differing only by which record is picked, with an exclusive priority (a withdrawn claim's uncollected remainder is ignored whenever a no-error claim has one) that no card program would publish — a remainder still owed is owed whichever claim left it. Bears on task 0 (uc_early_pay_cost, rv_carried_remainder) and task 1 (wd_carried_remainder).

**CG-5 SOURCE-FACTOR RED (realism) — Access hold-back on a provisional-credit reversal.** rv_access_holdback, wd_access_holdback: "the amount held back from the reversal … when the plan has card autorecovery authorized and carries an open shortfall … that open shortfall is held back; when the plan carries no open shortfall and early pay for its current pay period has been delivered to the card, that early pay is held back". Neither Regulation E, Visa rules nor any payroll-card program sets aside part of the available balance from a provisional-credit reversal; the base rule lets the reversal take the balance down to zero. Tier 1 subordinates the sponsor bank's reversal to a card autorecovery the Access charter only permits ("A card autorecovery debit may be attempted only …"); tier 2 shields early pay for no stated or industry reason. These are the only cross-difficulty factors of RV and WD. Bears on tasks 0 and 1.

**CG-6 SOURCE-POLICY + SOURCE-FACTOR RED — ch_liability_limit: unreachable tier, undeclared override of base, straw-man baseline.** Tier 1 "posted more than error_notice_window_days calendar days after the history access date and before the notice date" can never hold for the claim's own transaction, because `history_access_date` is "the date the cardholder first electronically accessed … a written history, showing the disputed transaction" (never before posting), so `DAYS(u_history, u_posted) > 60` is never true; with a history access date the ladder always yields 0, without one always 50 — at most two reachable tiers. The fall-through ("otherwise the limit is liability_cap_timely_usd") and the baseline ("less the cardholder's liability, which is the lesser of the disputed amount and liability_cap_timely_usd") charge a card-in-hand claim up to 50, contradicting the in-force base sentence of card_unauthorized_liability "The two caps apply only when the card itself was lost or stolen; when it was not, such as unauthorized use while the card is still in hand, liability is zero except for transfers that posted after that late-notice window and before the report", which CH's overwrite does not name. The baseline is a treatment no card program applies to card-in-hand unauthorized use (Reg E §1005.6 caps only apply to lost/stolen access devices). Bears on task 1.

**CG-7 SOURCE-FACTOR RED — factor-count bounds fail after the tests.** Counting only factors that survive CG-1..CG-6: SL 3 (0 method), RV 1, UC 1, WD 0, WC 1, CH 1 — each policy has fewer than 4 factors and no `method` factor; no cross-difficulty factor survives in either task; task 1 keeps no multi-source factor. Bears on tasks 0 and 1.

**CG-8 SOURCE-POLICY RED — selector rule/compute mismatches, ties and the single-plan gap (XF B1/B2/B7).** Listed under rule_compute_equivalence. Probe (scratch reasoning, no GT): a world whose latest investigating ATM-cash claim was reported in the app (or by phone) is priced by WC's compute although WC's rule prices only a claim "reported in writing"; a resolved_error_found card-in-hand ATM claim that already carries a provisional credit is priced a second (final) credit by CH's compute although CH's rule and the base ("a provisional credit already posted becomes final with no second credit") exclude it; after any later provisional credit posts on an unresolved claim, RV's compute selects that claim and reverses its whole credit. No same-day tie rule is stated for any "most recently" selector; "single active Access plan" has no rule for two active plans while CFIELD takes the first match ("first listed" route rejected by the run). Bears on task 1 (WC selector — demonstrated there) and task 0 (RV selector order-sensitivity).

**CG-9 SOURCE-POLICY RED — overwrite hygiene (XF C1/C3/C4).** (a) UC's replaced_by keeps "a final credit of the error amount, less any cardholder liability" in force for its own claims and declares only that "the fees, retry cost and early pay cost it returns are returned within the credit"; the rebate-netted "undelivered cash amount" and the late-credit allowance of UC's schedule are an undeclared repricing of that credit, leaving two clauses over one quantity. (b) CH's replaced_by of the "When an error is found" clause retires the whole clause with "every other final credit and fee correction stays as the base rule and the other claim schedules state" (C1) and drops "a provisional credit already posted becomes final with no second credit" (C4); its fee-correction tail "within another claim credit that returns its fees" does not name the siblings (C3). Bears on task 0 (UC — demonstrated there) and task 1 (CH).

**CG-10 SOURCE-POLICY RED — assembly sentences name factor quantities (XF A2).** SL: "the cardholder's liability is then the lesser of the claimed transfer and the liability limit for the signed claim less the liability already charged on the same loss …"; RV: "… due the reversed claim's transfer less the cardholder's liability on it, that liability being the lesser of the reversed claim's transfer and the liability limit behind the reversal; the reversal is … plus any remainder carried into the reversal, limited to the available balance less the amount held back from the reversal …"; UC: "the final credit for undispensed cash is the undelivered cash amount plus every amount the adjustments add"; WD: "limited to the available balance less the amount held back from the withdrawal reversal"; WC: "the undispensed cash on the written claim plus every amount the adjustments add"; CH: "the lesser of the card-in-hand claimed transfer and the liability limit on a card-in-hand claim". Each computation sentence names the quantities of its factors instead of stating the assembly generically. Bears on tasks 0 and 1.

**CG-11 SOURCE-POLICY RED — prerequisite declarations narrower than their sentences.** See prerequisite_graph: RV declares only UC and WD only WC/CH as resolvers of sentences that cover UC, CH, WC and SL credits; the declared `resolved_by` cannot make the declared `condition` hold in engaged worlds whose owed credit belongs to another policy (XF E3), and RV's sentence covering SL's provisional credit against the declared SL→RV edge leaves a cycle undeclared. Bears on task 0 (cycle reading recorded as observation O-0.1 there).

**Observations (not grounds for rework).**
- O-1 Late/overdue/service allowances (SL, UC, WC, CH) are worded as Paystride's own service guarantee; plausible, but four parallel schedules with near-identical 5/10 USD steps.
- O-2 SL's "no loss date" disjunct of tier 2 lies outside SL's own scope ("after their card was lost or stolen"); tier 2 stays reachable through its purchase disjunct.
- O-3 SL tool docstring "that they first reported by phone" contains the word "first" (history of the notice, not an action order).
- O-4 Base `card_lifecycle` blocks the card "when the cardholder … reports transactions they did not make"; whether an app-filed Reg E notice is such a report is unstated, which bears on whether later debits in both seeds could post.

## closing_checklist
Not closed: revision_1 has RED findings in both tasks and at charter level (see task files and findings above). The difficulty's instantiation gates were not re-run by this auditor (coordinator-owned, snapshot cited in charter_global_frozen).

## revision_1 verdict summary (written after both reveals; the charter-global section above is unchanged by them)
- GT values equal the blind values in both tasks (task 0: 117.74 / 55.64 / 157.55; task 1: 107.50 / 112.25 / 88.30) and every factor_sensitivity / baseline_result figure matches; the REDs are not derivation mismatches but defects of the charter and the seeds.
- task 0: SOURCE-POLICY RED (T0-1 UC repricing undeclared → second figure 111.24 / RV 49.14; T0-3 RV selector), SOURCE-FACTOR RED (T0-2), SOURCE-TASK RED (via T0-1); problem tree PASS.
- task 1: SOURCE-TASK RED (T1-1 app-reported "written" claim; T1-2 stolen-card "card-in-hand" claim; T1-3 seed rows the charters do not produce, incl. the missing 2026-10-16 payroll load explained only by a "garnishment" no record holds), SOURCE-FACTOR RED (T1-4), SOURCE-POLICY RED (CG-8 WC selector); problem tree PASS as declared.

VERDICT revision_1: task0=RED task1=RED charter=CG-1,CG-2,CG-3,CG-4,CG-5,CG-6,CG-7,CG-8,CG-9,CG-10,CG-11

## revision_2

### charter_global_frozen (revision_2)
- freeze time: 2026-10-23 before 05:04 UTC, written before any revision_2 GT was read; auditor: the same independent auditor as revision_1 (revision_1 text above left untouched).
- entry conditions: worklog last non-blank line = `REWORK round 2: gates 7/7 green` (checked); gate snapshot run by this auditor (execute-only) → `/tmp/erl0077_coord/snap_worker_payroll_card_servicing_r2.txt`: EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK. Hashes: `card.extended.yaml` 7693172af7b7a5b7, `task_tools.py` 471e4df776953225 (both changed from revision_1) → every charter-global section re-derived in full below. Views r2: `0.view.json` 0331283c32d88f1f, `1.view.json` c490276711b45958. Reworker claims read by item id only (section "REWORK round 2 claims": CG-1…CG-11, T0-1…T0-3, T1-1…T1-4); no other worklog/plan text read.
- base copy still equal to `blueprint/products/card.yaml` (parsed comparison).

### policy_conflict_scan (revision_2)
The charter was redesigned: three revision_1 policies (withdrawn-claim reversal, written-cash provisional, card-in-hand final) are gone; the six policies are now two plan-scoped families of the same lost/stolen-card claim cycle:

| policy | plan scope | subject / tool (owner) | claim selected (scope tests in compute) |
| --- | --- | --- | --- |
| card_ext_signed_loss_claim_credit (SL) | Premier, Elite | provisional / sign_card_loss_claim_statement_562d448e (user) | latest-registered investigating unauthorized Reg E phone claim, no written confirmation; loss date, no provisional, ≤ written_confirmation_window_business_days |
| card_ext_claim_credit_reversal (RV) | Premier, Elite | reversal / reverse_card_claim_credit_df02de93 (agent) | latest-registered resolved_error_found unauthorized claim; loss date, provisional with no reversal, only resolved claim of its loss |
| card_ext_error_claim_final_credit (ZC) | Premier, Elite | final / post_card_error_claim_credit_b4851c9e (agent) | latest-resolved resolved_error_found unauthorized claim; loss date, no credit, only claim of its loss, unique resolution date |
| card_ext_advantage_signed_claim_credit (TL) | Advantage | provisional / sign_card_theft_claim_form_2dc05390 (user) | as SL |
| card_ext_advantage_claim_reversal (WR) | Advantage | reversal / take_back_card_claim_excess_b240170d (agent) | as RV |
| card_ext_advantage_claim_final_credit (YC) | Advantage | final / post_card_claim_settlement_5bc5acd3 (agent) | as ZC |

The plan split makes the families disjoint (an account holds one plan); tools refuse a card on the other family's plan (scope, not a prerequisite check). Out of scope every compute returns 0 and the rule says "this policy prices nothing and the base rule applies". Blind trees: task 0 = {ZC, RV, SL} (Premier), task 1 = {YC, WR, TL} (Advantage) — disjoint and jointly complete. Cross-category: access only (RV, ZC, WR, YC early pay cost).

### rule_compute_equivalence (revision_2)
- Scripted sweep: every compute_basis quote verbatim in its rule; every binding has a basis; every policy_source, baseline.rule and replaced_by verbatim in its rule. Rounding: one RND(… + 1e-9, 2) at the end; tools keep the Decimal half-up helper.
- Business days: the compute's weekday count from the 2024-12-30 Monday anchor counts weekdays in (earlier, later], matching "counted from the day after the earlier date through the later one"; the Federal Reserve holiday list for 2025–2027 is correct (Saturday holidays such as 2026-07-04 rightly not observed). The list ends in 2027 (observation O-6).
- Scope sentences now implemented by exact tests (status, reason, path, channel, loss date, provisional/reversal/credit sums, COUNT of claims of the loss, COUNT of same-day resolutions, plan name); selectors run on `created_at`/`resolution_date` with a uniqueness test where ties matter. Round-1 CG-8 members closed.
- New mismatches (CG-13, CG-16 below): the "lost" tier of every early pay cost reads `CPARAM('access','nbd_fee_bank_usd', access_plan_id=…)` — the plan's current tier — while the rule says "the next-business-day bank fee (nbd_fee_bank_usd) of the Access tier the transfer was booked on", a tier no record stores; every `*_fees` binding sums all `card_fee` rows pointing to the transaction while the rule names only "an out-of-network ATM fee, an international ATM fee or a foreign transaction fee" and subtracts returns only for those three.

### action_binding_and_uuids (revision_2)
Six tools, each claimed by one policy; uuid8s 562d448e, df02de93, b4851c9e, 2dc05390, b240170d, 5bc5acd3 — distinct, unpatterned. Bodies: create/update in each write tool; refuse only non-positive amounts, unknown dispute, wrong plan; no prerequisite check; no forbidden imports; docstrings without example values, other tool names or order words. Owner ruling: TL signing the claim form and SL signing the statement are the holder's written confirmation of an oral Reg E notice (class (a)/(c)) — accepted.

### prerequisite_graph (revision_2)
SL → [RV state_gate `card_transactions.credit_kind`], RV → [ZC value_input `v_room`], TL → [WR state_gate], WR → [YC value_input `w_room`]; ZC, YC → []. Acyclic; every policy_source verbatim in its own rule; all state form. RV's sentence "A provisional credit reversal is not taken until every final credit owed on the account's other claims of a lost or stolen card has posted." (WR: "The excess of a provisional credit is not taken back until …") now covers final credits only, and on a Premier/Elite (Advantage) account the only tool that books a lost/stolen-card final credit is ZC's (YC's), whether the claim is schedule-priced or base-priced — round-1 CG-11 closed, the RV↔SL cycle reading gone.

### prerequisite_sentences (revision_2)
SL/TL: "The signed claim credit (claim form credit) is fixed only after every other claim of the same loss whose provisional credit stood above what that claim was due carries its reversal." — "only after", state (a reversal row), no tool/id; "what that claim was due" is defined by RV's/WR's own rule; one write (RV/WR) brings it about. RV/WR as above. No other cross-problem order in any rule.

### override_declarations (revision_2)
Sentence by sentence: SL/TL overwrite the provisional-credit clause (restated for every other claim, own scope named, sibling named) and the "When an error is found" and fee-correction clauses (restated, own scope, all siblings named); RV/WR overwrite "When no error, or a smaller error, is found…" (restated, sibling named), "When an error is found" and fee-correction clauses; RV and ZC overwrite "A fee is returned in one of two ways." with tails naming each other; ZC/YC overwrite "When an error is found" ("the final credit is the one this schedule sets out" — round-1 CG-9(a) closed) and the fee-correction clause. C1/C3/C4 sweep clean; round-1 CG-9 closed.
Not overwritten by any policy although all six list it in `base_policy_refs` and price liability: card_unauthorized_liability. Its sentences "liability is the lesser of the unauthorized amount and liability_cap_timely_usd when the cardholder reported the loss or theft within timely_loss_report_business_days business days after loss_learned_date …" and "Liability is counted once across all unauthorized transactions from the same loss or theft, applied in posting order." are departed from (CG-15), and RV's/WR's baseline "with a liability limit of zero" contradicts the first (CG-14).

### factor_ladders (revision_2)

| policy | factors (effect) | count / method | structural verdict |
| --- | --- | --- | --- |
| SL | sl_liability_limit (p), sl_prior_liability (p), sl_transaction_fees (m), sl_service_allowance (p) | 4 / 1 | sl_service_allowance tier 1 unreachable (CG-12) → 3 surviving |
| RV | vr_liability_limit (p), vr_transaction_fees (m), vr_service_allowance (p), vr_investigation_allowance (p), vr_replacement_fees (p), vr_early_pay_cost (m, cross access) | 6 / 2 | vr_liability_limit baseline ≠ fall-through (CG-14); early pay "lost" tier rule/compute mismatch (CG-13) |
| ZC | zc_liability_limit (p), zc_transaction_fees (m), zc_late_allowance (p), zc_investigation_allowance (p), zc_replacement_fees (p), zc_early_pay_cost (m, cross access) | 6 / 2 | CG-13 |
| TL | tl_liability_limit, tl_prior_liability, tl_transaction_fees (m), tl_service_allowance | 4 / 1 | tl_service_allowance unreachable tier (CG-12) → 3; CG-16 |
| WR | wr_liability_limit, wr_transaction_fees (m), wr_service_allowance, wr_early_pay_cost (m, cross) | 4 / 2 | CG-14, CG-13, CG-16 |
| YC | yc_liability_limit, yc_transaction_fees (m), yc_late_allowance, yc_investigation_allowance, yc_early_pay_cost (m, cross) | 5 / 2 | CG-13, CG-16 |

All-pairs method shape: `*_transaction_fees` — tier 1 a data sum (fees less returns), tier 2 a tariff parameter (out_of_network_atm_withdrawal_fee_usd), tier 3 nothing: passes A6. `*_early_pay_cost` — stolen: fee less reversal; lost: MN(fee, tariff) adds an operation; none: passes. Liability ladders (VZL purchase 0 / late 500 / else 50) match the base caps and Visa Zero Liability; multi-source (transaction + plan parameter, claim dates). Allowance ladders keyed to real Reg E clocks (5/10 business days for provisional credit, 1 business day for correction, 45/90 days and 10/20 business days for investigations) with company-schedule dollar steps — plausible. Replacement fee ladder (stolen: replacement + expedited; lost: replacement only) and early pay ladder (lost capped at the NBD bank fee) are plausible Paystride schedules. No factor reads another factor's binding; assembly sentences are generic ("replacements apply first, additions after them") — round-1 CG-1…CG-6, CG-10 closed. Cross-difficulty and multi-source factors present in every task's computations.

### findings (revision_2)
**CG-12 SOURCE-FACTOR RED — the signed-claim service allowances have an unreachable top tier; SL and TL fall below 4 factors.** SL/TL price a claim only when it "is signed no more than written_confirmation_window_business_days business days after its notice date" (`s_window`/`t_window`: business days to NOW ≤ 10 on every plan), while tier 1 pays allowance_high_usd for "more than investigation_business_days business days" (10 on every plan) measured on the same interval (`s_bd_open`/`t_bd_open`). Inside the policy's own scope tier 1 never fires; two tiers remain, so the factor is not a three-tier ladder and SL and TL each keep 3 factors (bound 4–6). Bears on tasks 0 and 1. (Round-1 CG-7 closed for RV, ZC, WR, YC; persists here for SL/TL.)

**CG-13 SOURCE-POLICY RED — early pay "lost" tier: rule reads the tier at booking, compute reads today's tier, no record holds the former.** Rule (RV, ZC, WR, YC): "for a card replaced as lost it counts that fee but no more than the next-business-day bank fee (nbd_fee_bank_usd) of the Access tier the transfer was booked on"; compute: `CPARAM('access', 'nbd_fee_bank_usd', access_plan_id=…_x_plan)`, the plan's current `variant_name`. access_plans keeps only the current tier and level_effective_date; access_ledger has no tier field (B6). Wherever the plan changed tier after the transfer the two readings give different numbers (demonstrated in both tasks). Members: vr_early_pay_cost, zc_early_pay_cost, wr_early_pay_cost, yc_early_pay_cost. Bears on task 0 (RV) and task 1 (YC).

**CG-14 SOURCE-FACTOR + SOURCE-POLICY RED — reversal liability baseline is not the fall-through and contradicts the base rule.** vr_liability_limit / wr_liability_limit: ladder fall-through "otherwise it is liability_cap_timely_usd", baseline `{'v_limit': '0'}` / `{'w_limit': '0'}`, and baseline.rule "… less the cardholder's liability, the lesser of the claimed transfer and the liability limit, with a liability limit of zero". The factor's fall-through tier is not its baseline, and a zero liability on a lost/stolen-card ATM claim contradicts card_unauthorized_liability (lesser of the amount and liability_cap_timely_usd for a timely report), which neither policy overwrites. Bears on tasks 0 and 1.

**CG-15 SOURCE-POLICY RED — undeclared departures from card_unauthorized_liability (Reg E timing and counted-once).** All six liability ladders time the limit by "the claim's notice date fell more than timely_loss_report_business_days business days after its loss date", but Regulation E §1005.6(b) and the in-force base sentence time it by when "the cardholder reported the loss or theft"; a later claim on a loss reported on time is charged as late. Producible world: loss learned Monday, card reported lost Tuesday (replacement order and first claim that day), a second unauthorized withdrawal noticed three weeks later → base/Reg E limit 50 (and 50 already charged on the first claim → nothing withheld), policy limit 500 → SL withholds 50 more. SL/TL also read "the liability already charged" from only "the account's most recently registered other claim … carrying the same loss date", against the base "Liability is counted once across all unauthorized transactions from the same loss or theft". No overwrite names card_unauthorized_liability. In both task worlds the loss report and the first claim share a date, so the task numbers agree with the base reading (no task consequence). Charter-global.

**CG-16 SOURCE-POLICY RED — transaction-fee selector counts fee types the rule excludes (Advantage family).** tl/wr/yc_transaction_fees: `t_fees = SUM(card_fee, related_txn_id=t_txn)` (all fee types) and returns subtracted only for out-of-network, international and foreign-transaction fees; the rule counts only "Paystride fees … charged on it (an out-of-network ATM fee, an international ATM fee or a foreign transaction fee)". On the Advantage plan a card-to-bank transfer beyond the free one carries card_to_bank_transfer_fee_usd 0.50 pointing to the transfer, so an unauthorized card-to-bank claim is credited that fee by the compute (tier 1) and nothing by the rule (not an ATM withdrawal → otherwise). Premier/Elite members (sl/vr/zc) are not producible (card-to-bank fee 0.0, never assessed) — observation. No task consequence.

**Closure of revision_1 charter findings:** CG-1 closed (day-fee ladders removed); CG-2 closed (claimed transfer is one baseline formula; retry factor removed); CG-3 closed (fee ladders replaced by a data-sum/tariff/nothing method); CG-4 closed (early pay tiers now differ by method; carried remainders removed); CG-5 closed (hold-back removed); CG-6 closed (card-in-hand policy removed; liability ladders follow the base caps); CG-7 closed for RV/ZC/WR/YC, not for SL/TL (now CG-12); CG-8 closed (selectors and scope tests match the rules; new B1 members are CG-13/CG-16); CG-9 closed; CG-10 closed; CG-11 closed.

**Observations (revision_2).** O-5 The Advantage family repeats the Premier/Elite family nearly word for word with different allowance dollars and without the replacement-fee factor — plausible as plan schedules, but heavy. O-6 The business-day holiday table stops at 2027-11-25. O-7 Ties between early pay transfers to the same destination at the same requested minute are unstated (XLATEST keeps the first). O-8 Base card_unauthorized_liability applies liability_cap_late_usd to every transfer of a late-reported loss, including transfers inside the two-business-day window (Reg E caps those at 50) — blueprint-level, inherited. O-9 Compensating a used free out-of-network withdrawal at the plan's fee (tier 2 of the transaction-fee ladders) is an unusual but defensible Paystride choice. O-10 When a later-resolved credited claim exists, ZC/YC select it and price nothing, leaving an older owed final credit to the base rule (still bookable with the same plan's tool).

### closing sweep and summary (revision_2, after the reveals)
- Every class raised in revision_1 or revision_2 re-swept over the six policies: tier-collapse / same-outcome tiers — none (transaction-fee, replacement, early-pay, liability, allowance and investigation tiers all differ in value or method); lesser-of written as a ladder — none (claimed transfer is a baseline formula); unreachable tiers — sl/tl_service_allowance only (CG-12); baselines vs fall-through — vr/wr_liability_limit only (CG-14); rule/compute selector mismatches — CG-13 (four early pay factors) and CG-16 (three Advantage fee factors), all scope selectors otherwise exact; overwrite hygiene C1–C4 — clean; assembly sentences — generic; prerequisite declarations vs sentences — consistent; owner ruling — accepted; realism of the cross-category rows and of both seeds — clean (Access fees match the tier each fee implies; card ledgers replay; no blocked-card debit); regulatory figures — Reg E caps 50/500, the 50 provisional-credit withholding limit, 5/10/20 business-day and 45/90-day clocks and Visa Zero Liability are real; the timing basis and counted-once rule depart from the base (CG-15).
- GT equals the blind compute values in both tasks; the REDs are charter defects plus their demonstrated second readings.
- Not closed: CG-12, CG-13, CG-14, CG-15, CG-16. Closed from revision_1: CG-1…CG-11 (CG-7 only partially — its SL/TL remainder is CG-12).

VERDICT revision_2: task0=RED task1=RED charter=CG-12,CG-13,CG-14,CG-15,CG-16

## revision_3

### charter_global_frozen (revision_3)
- written 2026-10-23 before any revision_3 GT was read; same auditor; revision_1/2 text untouched.
- entry: worklog last non-blank line `REWORK round 3: gates 7/7 green` (checked); snapshot run execute-only → `/tmp/erl0077_coord/snap_worker_payroll_card_servicing_r3.txt`, all 7 gates OK. Hashes: `card.extended.yaml` 089f4666c04f0d19 (changed → charter-global sections re-derived), `task_tools.py` 471e4df776953225 (unchanged since revision_2 → action_binding_and_uuids carried forward by reference to revision_2 on these grounds). Views r3: `0.view.json` 58ace9293a1c862e (seed amounts changed), `1.view.json` c490276711b45958 (identical to r2). Claims read by id only: CG-12…CG-16, R2-T0-1, R2-T0-2. Base copy still equal to products/card.yaml.

### policy_conflict_scan / rule_compute_equivalence (revision_3)
Same six plan-scoped policies and tools as revision_2; trees task 0 = {ZC, RV, SL}, task 1 = {YC, WR, TL}. Changes found: (1) every policy now defines "a claim's loss" as the account's unauthorized claims with its loss date, prices only a loss of at most two claims, and identifies the other claim as "the one whose disputed amount equals the loss's total disputed amount less this claim's and which is not this claim"; (2) the loss report is "the earlier of this claim's notice date and the other claim's"; (3) "liability already charged" (now also in RV, ZC, WR, YC) is the other claim's capped transfer when it is under investigation or resolved with an error found and posted earlier; (4) all six overwrite the card_unauthorized_liability "Otherwise …" sentence; (5) `allowance_high_business_days` = 8 for the service allowances; (6) the early-pay "lost" cap is "the tier the worker's Access plan holds on the day the credit is figured, as the plan record shows it"; (7) `*_fees` filter the three named fee types; (8) RV/WR baselines use liability_cap_timely_usd. Scripted sweep: every compute_basis quote, policy_source, baseline.rule and replaced_by verbatim in its rule; every binding has a basis; rounding unchanged.
Rule→compute: (6) and (7) now match. New mismatch (CG-17): when the two claims of a loss carry the same disputed amount, the compute's `*_o = LATEST(… disputed_amount=*_o_amt)` picks the later-registered one, which for the signed-claim schedules is the claim itself, so `*_loss_ok` fails and the result is 0, while the rule's "the one whose disputed amount equals … and which is not this claim" names the other claim and prices it (probe on the task-0 world with 91bd52d5 set to 483.50: SL compute 0).

### prerequisite_graph / prerequisite_sentences (revision_3)
Unchanged from revision_2 (edges SL→RV state_gate, RV→ZC value_input, TL→WR state_gate, WR→YC value_input; sentences verbatim, state form, single resolving write). Carried forward.

### override_declarations (revision_3)
The six new card_unauthorized_liability overwrites restate the base sentence verbatim, then scope "on a claim this schedule prices, and only on such a claim, the unauthorized amount is the claimed transfer net of any surcharge rebate, the loss counts as reported on the earliest notice date among its claims, and no transfer is charged in full", naming the sibling schedules — C1/C3/C4 clean. The counted-once base sentence is now honoured (≤ 2 claims, the earlier-posted one counted first). The declared report rule, however, departs from what it may lawfully replace (CG-15, below).

### factor_ladders (revision_3)
Factor sets as revision_2. Re-tested: sl/tl_service_allowance top tier (> 8 business days) reachable inside the ≤ 10-day window — CG-12 closed (SL, TL 4 factors, 1 method). vr/wr_liability_limit baseline = fall-through = liability_cap_timely_usd, consistent with the base — CG-14 closed. Early-pay "lost" tier rule = compute — CG-13 closed. Fee selectors filtered — CG-16 closed. Liability ladders now time the limit by the loss report; sl/tl/vr/zc/wr/yc_prior read the loss's other claim. No tier collapses, no unreachable tier, no factor reads another's binding, assembly generic; counts SL 4, RV 6, ZC 6, TL 4, WR 4, YC 5; cross-difficulty (early pay) and multi-source factors present in both tasks.

### findings (revision_3)
**CG-15 SOURCE-POLICY RED (realism F2) — not closed: the loss report date ignores the card report.** The declared override "the loss counts as reported on the earliest notice date among its claims" (all six policies) times the $50/$500 limit by claim notices only. Regulation E §1005.6(b) — and the base sentence these overwrites restate — time it by the consumer's notice of the loss or theft of the card, which these records carry as the lost/stolen replacement order (the same rules call that day the claim's "report day"). Probe on the task-0 world with the lost-card order moved to 2026-09-09 (one business day after the 2026-09-08 loss): Reg E timely → limit 50, already charged 50 → nothing withheld, credit 107.20; policy still late (report 2026-09-14) → 87.20. No consequence on either task world (card report = first claim notice in both). The counted-once member of CG-15 is closed.

**CG-17 SOURCE-POLICY RED — the "other claim" is identified by an amount identity that the compute and the rule resolve differently.** Rule (all six): "that other claim being the one whose disputed amount equals the loss's total disputed amount less this claim's and which is not this claim"; compute picks the latest-registered claim with that amount. With two equal-amount claims the compute picks the priced claim itself whenever it was registered later (always for SL/TL, whose claim is the newest), drops out of scope and prices 0, while the rule prices it against the other claim. The sentence is also a selection device rather than a published business rule (a desk identifies the loss's other claim by its loss date, not by arithmetic on amounts). No consequence on either task world (amounts differ).

**Closure of revision_2 findings:** CG-12 closed; CG-13 closed; CG-14 closed; CG-15 partly (counted-once closed, timing basis not — see above); CG-16 closed.

**Observations (revision_3).** O-11 Capping a lost-card early-pay reimbursement at the plan's current-tier NBD fee is a Paystride choice, now stated as such. O-12 Counting liability on an other claim still under investigation is consistent with Reg E's posting-order rule. O-5…O-10 of revision_2 unchanged.

### closing sweep and summary (revision_3, after the reveals)
- Every class raised in revisions 1–3 re-swept over the six policies: tier collapse / same-outcome tiers — none; lesser-of as ladder — none; unreachable tiers — none (service allowances now > 8 inside a ≤ 10-day window); baseline vs fall-through — all equal; rule/compute selectors — only CG-17 (equal-amount other claim); fee-type and tier-at-booking members — closed; overwrite hygiene C1–C4 — clean incl. the six new liability overwrites; assembly — generic; prerequisite graph/sentences — unchanged and clean; owner ruling — accepted; seeds — both ledgers replay, Access fees match tiers, no blocked-card debits, no zero rows; regulatory figures real; the Reg E timing basis remains wrong (CG-15).
- GT equals the blind values in both tasks; both tasks PASS on their own worlds; the difficulty is not closed because of the charter-level REDs CG-15 and CG-17.

## closing_checklist (revision_3)
Not closed: charter REDs CG-15, CG-17 remain. Per-task files 0.md / 1.md correspond to the tasks, revisions preserved; scopes disjoint ({ZC, RV, SL} / {YC, WR, TL}) and complete; uuid8s independent; each tree has 2 prerequisite problems, 1 value_input edge, an owner=user problem, acyclic; every computation has 4–6 factors with ≥ 2 parameter and ≥ 1 method, multi-source and cross-difficulty present per task, all bearing weight against honest baselines; gates re-run by the coordinator snapshot (r3, all OK).

VERDICT revision_3: task0=PASS task1=PASS charter=CG-15,CG-17

## revision_4

### charter_global_frozen (revision_4)
- written 2026-10-23 before any revision_4 GT was read; same auditor; earlier revisions untouched.
- entry: worklog last non-blank line `REWORK round 4: gates 7/7 green` (checked); snapshot (execute-only) → `/tmp/erl0077_coord/snap_worker_payroll_card_servicing_r4.txt`, all 7 gates OK. Hashes: `card.extended.yaml` 4262b6778df4346f (changed → charter-global re-derived), `task_tools.py` 471e4df776953225 (unchanged → action_binding_and_uuids carried forward from revision_2), views r4 `0.view.json` 58ace9293a1c862e and `1.view.json` c490276711b45958 (both identical to r3). Claims read by id only: CG-15, CG-17. Base copy equal.

### re-derivation (revision_4)
- Changes: (1) the loss is "the set of the account's unauthorized-transaction claims carrying its loss_learned_date"; (2) the loss report is "the order_date of the account's most recent card_replacement_order with order_reason lost or stolen when that date falls on or after the loss_learned_date and no later than the claim's notice_date, and otherwise … the claim's notice_date"; (3) a claim is priced only when its loss has no other claim or a claim noticed on that card report day; (4) the amount-identity sentence is gone everywhere; (5) "liability already charged" (SL, TL) is the lesser of the loss's resolved-with-error claims' total disputed amount and the cap, counted "before any claim still under investigation"; RV, ZC, WR, YC charge the full cap on their own (only resolved) claim ("it carries the loss's liability first"); (6) liability is the lesser of the disputed amount (not the net transfer) and the limit; the card_unauthorized_liability overwrites restate this.
- Scripted sweep: compute_basis, policy_source, baseline.rule and replaced_by verbatim in each rule; every binding has a basis; every factor's fall-through equals its baseline; prerequisite graph and sentences unchanged (carried forward from revision_2/3). Factor sets and counts as revision_3 (SL 4, RV 6, ZC 6, TL 4, WR 4, YC 5); no collapsed or unreachable tier; overwrites C1/C3/C4 clean; assembly generic.

### findings (revision_4)
**CG-17 closed** — the amount-identity selection is removed from all six rules and computes.

**CG-15 SOURCE-POLICY RED (realism F2) — still not closed: the "most recent" lost/stolen order is not tied to the loss.** The report day is the order_date of the account's *most recent* lost/stolen replacement order, used only when it falls between the loss date and the claim's notice. A later loss's order therefore displaces an earlier loss's own card report, and the report falls back to the claim's notice date. Probe on the task-0 world (loss A claim 01e07606 noticed 2026-08-20 on an ATM withdrawal, its card reported by the stolen order of 2026-08-10, one business day after the 2026-08-09 loss): because loss B's lost order of 2026-09-14 is more recent, ZC times the report at 2026-08-20 (late) → limit 500, credit 23.73; with that later order absent the same claim is timely → limit 50, credit 160.13. Regulation E §1005.6(b) times the cap by the loss's own notice, which here was 2026-08-10. Members: all six policies (`*_card_report` = latest lost/stolen order of the account). No consequence on the task worlds (each priced claim's own order is the latest in-window one, or the fallback coincides with it).

**CG-18 SOURCE-POLICY RED (new) — liability ordering contradicts the un-overwritten base sentence "Liability is counted once across all unauthorized transactions from the same loss or theft, applied in posting order."** The six replaced_by texts now read "liability already charged on the loss is counted on its claims resolved with an error found, at their disputed amounts, before any claim still under investigation" (SL/TL), and RV/ZC/WR/YC state that their resolved claim "carries the loss's liability first". Ordering by resolution status, not by posting date, departs from a base sentence no overwrite names. Producible world: the still-investigating claim's transfer posted before the resolved claim's — base: the earlier transfer takes the cap first; policy: the resolved one does. No consequence on the task worlds (the resolved claim posted first in both).

**Observations (revision_4).** O-13 Rules now carry schema tokens in prose ("loss_learned_date", "order_date", "card_replacement_order", "order_reason", "notice_date"); renderable, but the policy prose is less like a published schedule. O-14 Liability is now counted at the disputed amount (surcharge included), so the first claim of a loss counts 483.50/483.00 against the cap while the cardholder's net loss on it is 480.00 (rebate kept) — consistent with Reg E's "amount of unauthorized transfers".

### closing sweep and summary (revision_4, after the reveals)
- All classes raised in revisions 1–4 re-swept across the six policies: tier collapse, lesser-of ladders, unreachable tiers, baseline vs fall-through, fee-type and tier-at-booking selectors, amount-identity selection — none; overwrite hygiene C1/C3/C4 clean; assembly generic; prerequisite graph/sentences clean; owner ruling accepted; seeds unchanged and clean; regulatory figures real. Open: the report-day selector (CG-15) and the liability ordering vs the base posting-order sentence (CG-18).
- GT equals the blind values in both tasks; both tasks PASS on their worlds; the difficulty stays open on the charter REDs.

## closing_checklist (revision_4)
Not closed: CG-15, CG-18. Everything else in Step 4 holds as recorded in the revision_3 checklist (scopes, uuids, trees, factor bounds, gates r4 OK).

VERDICT revision_4: task0=PASS task1=PASS charter=CG-15,CG-18

## revision_5

### charter_global_frozen (revision_5)
- written 2026-10-23 before any revision_5 GT was read; same auditor; earlier revisions untouched.
- entry: worklog last non-blank line `REWORK round 5: gates 7/7 green` (checked); snapshot (execute-only) → `/tmp/erl0077_coord/snap_worker_payroll_card_servicing_r5.txt`, all 7 gates OK. Hashes: `card.extended.yaml` 6f9b13e5228561d3 (changed → re-derived), `task_tools.py` 471e4df776953225 (unchanged → carried forward), views r5 identical to r3/r4 (58ace9293a1c862e, c490276711b45958). Claims read by id only: CG-15, CG-18. Base copy equal.

### re-derivation (revision_5)
- Changes: (1) every policy now times the liability limit "only for an account that holds at most one replacement order for a lost card and at most one for a stolen card, exactly one of them placed on or after the loss date, and that order's date is the day the loss was reported"; outside that, the policy "prices nothing and the base rule applies" (ZC/YC also price a Visa-Zero-Liability purchase, "which carries no liability whenever the loss was reported"); (2) all six now overwrite the base sentence "Liability is counted once across all unauthorized transactions from the same loss or theft, applied in posting order", restating it and scoping "the liability already charged on the loss is counted on its claims resolved with an error found before any claim still under investigation, whatever their posting order", siblings named.
- Scripted sweep: compute_basis, policy_source, baseline.rule and replaced_by verbatim; every binding has a basis; rule scope sentences = compute scope tests (`*_liab_scope`); fall-through = baseline for every factor; factor sets and counts unchanged (SL 4, RV 6, ZC 6, TL 4, WR 4, YC 5); prerequisite graph and sentences unchanged; overwrite hygiene C1/C3/C4 clean.

### findings (revision_5)
**CG-18 closed** — the posting-order sentence is now named and replaced with a scoped, sibling-naming override.
**CG-15 closed as stated** — the policy no longer dates a loss's report from another loss's order: the revision_4 probe (loss-A ATM claim with loss B's later order present) now falls outside the scope (compute 0, base rule applies) instead of being mis-timed.

**CG-19 SOURCE-POLICY RED (new; XF B7 rejected route + realism) — pricing switched by an incidental lifetime count of replacement orders.** The scope test `*_n_lost <= 1 and *_n_stolen <= 1` counts every lost or stolen replacement order the account has ever had, including orders placed long before the loss and unrelated to it. Probe on the task-0 world with one extra lost-card order on 2026-03-20 (five months before either loss): SL and RV both fall to "prices nothing and the base rule applies" (compute 0) although the loss of 2026-09-08 and its report order of 2026-09-14 are unchanged. A cardholder's earlier, unrelated card losses decide whether Paystride's claim schedule (allowances, fee returns, replacement and early-pay costs) applies to a new claim — no card program publishes such a condition, and the run's XF B7 rejects "pricing switched by an incidental COUNT". Members: all six policies (`s_/v_/z_/t_/w_/y_liab_scope`; ZC/YC escape it only for Visa-Zero-Liability purchases). No consequence on the task worlds (each account holds exactly one lost and one stolen order).

**Observations (revision_5).** O-15 Inside the scope, a single in-window order is taken as the loss's report even if it belonged to a later loss of a card never replaced for the earlier one — an edge case of an edge case. O-13/O-14 unchanged.

### closing sweep and summary (revision_5, after the reveals)
- All classes raised in revisions 1–5 re-swept across the six policies: tier collapse, lesser-of ladders, unreachable tiers, baseline vs fall-through, fee-type / tier-at-booking / amount-identity selectors, report-day mis-dating, undeclared base departures (liability timing, counted-once, posting order) — none remain; overwrite hygiene clean; assembly generic; prerequisite graph/sentences clean; owner ruling accepted; seeds clean; regulatory figures real. Open: the incidental lifetime order count gating every schedule (CG-19).
- GT equals the blind values in both tasks; both tasks PASS on their worlds.

## closing_checklist (revision_5)
Not closed: CG-19. All other Step-4 items hold as recorded in revision_3 (gates r5 OK).

VERDICT revision_5: task0=PASS task1=PASS charter=CG-19

## revision_6

### charter_global_frozen (revision_6)
- written 2026-10-23 before any revision_6 GT was read; same auditor; earlier revisions untouched.
- entry: worklog last non-blank line `REWORK round 6: gates 7/7 green` (checked); snapshot (execute-only) → `/tmp/erl0077_coord/snap_worker_payroll_card_servicing_r6.txt`, all 7 gates OK. Hashes: `card.extended.yaml` f70644cc5224accf (changed → re-derived), `task_tools.py` 471e4df776953225 (unchanged), views r6 identical to r3–r5. Claims read by id only: CG-19, CG-15. Coordinator ruling for CG-19 applied as stated (12-month look-back with repeat-loss referral is the accepted DSL-limit route; judged on rule words == compute, realism of the referral, absence of purpose clauses).

### re-derivation (revision_6)
- Change: in all six policies the scope count now reads "replacement orders placed less than 12 whole months before today include at most one for a lost card and at most one for a stolen card, exactly one of them placed on or after the loss date …; orders placed 12 or more months before today never count, and under Paystride's program practice an account with repeated lost or stolen cards within those 12 months is referred to Paystride's card fraud review team, so this policy books nothing for its claims"; compute `COUNT(card_service_orders, within_months=12, …)` per reason, `*_lost_in`/`*_stolen_in` require an in-window order, `*_limit` timed only inside that scope. Out of scope the base liability sentence stands restated verbatim in every replaced_by.
- Rule words == compute: `within_months=12` keeps orders with whole months elapsed (MONTHS) in [0, 12) — "less than 12 whole months before today"; probes on the task-0 world with one extra lost order: 2025-10-22 (exactly 12 whole months) → not counted, SL/RV price as before; 2025-10-23 and 2026-03-20 → counted → repeated losses → SL/RV book nothing; 2025-08-01 → not counted. The latest-order read (`LATEST` over all orders) coincides with the in-window order whenever the 12-month count is 1, and is ignored when the count is 0. Inside the scope every figure is unchanged from revision_5.
- Referral: a 12-month repeat lost/stolen-card review by a card fraud team is a common issuer practice; stated as "under Paystride's program practice", no regulatory claim; no purpose clause ("so this policy books nothing" states a consequence). Sweep: compute_basis, policy_source, baseline.rule and replaced_by verbatim; every binding has a basis; fall-through = baseline; factor sets/counts unchanged (SL 4, RV 6, ZC 6, TL 4, WR 4, YC 5); prerequisite graph/sentences unchanged; overwrite hygiene clean.

### findings (revision_6)
- **CG-19 closed** under the coordinator ruling (bounded look-back, realistic referral, rule = compute at the 12-month boundary).
- **CG-15** remains closed (no policy dates a loss's report from another loss's order; the narrowed scope does not reopen it).
- No new RED. Observation O-16: the whole-month count follows MONTHS() (a 29 February order is still inside the window on 28 February a year later); "less than 12 whole months" admits that reading.

### closing sweep and summary (revision_6, after the reveals)
- Every class raised in revisions 1–6 re-swept across the six policies: factor-ladder classes (collapse, lesser-of, unreachable tiers, baseline ≠ fall-through, mislabelled method, one-tier-as-two), selector classes (fee types, tier at booking, amount identity, report-day mis-dating, incidental counts — now the accepted 12-month route), base-departure classes (liability timing, counted-once, posting order — all declared, scoped, sibling-named), overwrite hygiene C1–C4, assembly sentences, prerequisite declarations and sentences, owner ruling, seed realism (both ledgers replay, Access fees match tiers, no blocked-card debits, no zero rows), regulatory figures (Reg E 50/500 caps, 50 provisional withholding, 5/10/20 business-day and 45/90-day clocks, Visa Zero Liability) — no open member.
- GT equals the blind values in both tasks.

## closing_checklist (revision_6)
- Per-task files 0.md / 1.md correspond to tasks 0 and 1 with _difficulty.md alongside; revisions 1–6 preserved; every revision_6 comparison carries PASS.
- The six extended policies are covered; scopes {ZC, RV, SL} and {YC, WR, TL} are disjoint and complete; tools and GT closed; uuid8s 562d448e, df02de93, b4851c9e, 2dc05390, b240170d, 5bc5acd3 independent.
- Each tree has 2 prerequisite problems, 1 value_input edge, an owner=user root, no cycle; the difficulty's prerequisite graph is acyclic.
- Every computation: self-sufficient baseline, 4–6 factors (≥ 2 parameter, ≥ 1 method), ladders of 3 distinct real tiers stated in the rule; per task a multi-source and a cross-difficulty (Access early pay) factor; every factor bears weight against an honest baseline; all-baseline figures definite and different from gold.
- Instantiation gates re-run on the final form: coordinator snapshot r6, all 7 OK.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

### charter_global_frozen (revision_7)
- written 2026-10-23 before any revision_7 GT was read; same auditor; earlier revisions untouched.
- entry: worklog last non-blank line `REWORK round 7: gates 7/7 green` (checked); snapshot (execute-only) → `/tmp/erl0077_coord/snap_worker_payroll_card_servicing_r7.txt`, all 7 gates OK. Hashes: `card.extended.yaml` a6731372d7a12871 and `task_tools.py` b598d810b8089415 (both changed → charter-global sections and the tool checks re-derived), views r7 identical to r3–r6. Input added this round: `audits/render_source/worker_payroll_card_servicing/render_r1.md` (renderer findings 1–6, read in full); reworker claims read by id only.
- Disclosure on revision_6: revision_6 recorded `charter=CLEAN`, but the renderer then found six source defects in that charter. Findings 1 (floors), 3 (report-day gap and tie) and 6 (docstring claims the tool bodies did not enforce) are members of classes this audit covers (B1, B3, D1), and 2 and 5 are A4/hygiene members. The revision_6 sweep missed them. The revision_6 text is left as written; this revision records the miss.

### renderer findings 1–6, each re-checked across all six policies and six tools
1. **B1 floors (SL [0], TL [3]) — not fully closed.** The rules now state both floors: "the claimed transfer is the disputed amount less any ATM owner surcharge rebate …, never below zero" (= `MX(0, *_disputed - *_rebate)`, closed) and "the amount withheld is the lesser of that liability and liability_cap_timely_usd …; the credit is never below zero", followed in the assembly sentence by "replacements apply first, additions after them, and the credit, never below zero, is rounded half up". The method sentence floors the standard credit (transfer less withheld) *before* the adjustments add fees and the allowance, but the compute floors only once, after them: `RND(MX(0, *_transfer - *_withheld + *_fee_back + *_allow) …)`. Witness (the renderer's, in scope on the Advantage plan): transfer 37.00 (40.00 less a 3.00 rebate), withheld 40.00, free-withdrawal fee 1.95, no allowance → rule words MX(0, 37.00 − 40.00) + 1.95 = 1.95; compute MX(0, −1.05) = 0.00. ZC/YC (`MX(0, *_transfer - *_liability) + additions`) and RV/WR (`*_due = MX(0, *_transfer - *_liability) + …`) floor before the additions, exactly as their rules say — closed there. → **CG-20** below.
2. **A4 single-factor plain bindings — closed.** Scripted check: no plain binding is now used by only one factor's bindings in any policy (v_report, v_prov_date, v_resolved, v_posted, z_report, z_posted, w_report, w_prov_date, y_report, y_posted moved into their factors or now shared).
3. **B3/B1 report-day gap and tie — closed.** Report day now requires "a replacement card for a lost or stolen card"; "the replacement read is the stolen-card order when both a lost-card and a stolen-card replacement were ordered that day, and a day with two replacement orders of the same reason is no report day". The compute matches: `*_n_day_stolen` / `*_n_day_lost` counts, `*_reason` None on a same-reason duplicate, stolen preferred, and `*_order` read with that reason. Replacement and early-pay ladders cover stolen / lost / no report day. All four members (RV, ZC, WR, YC) are closed.
4. **B6 framing clause — closed.** "when the blocked card could not receive early pay" has been removed from RV, ZC, WR and YC.
5. **Dead bindings — closed.** Scripted check: every binding is read by a later binding or by `result`, in all six policies.
6. **D1 docstring vs body — closed.**
   - Both signing tools refuse unless the claim is an unauthorized claim with a loss date, its notice channel is phone and it is under investigation. The theft tool's Args now say "the claim form confirms".
   - Both reversal tools refuse unless the claim is a lost/stolen claim, resolved, and carries a provisional credit, so related_txn_id can no longer be None.
   - Both final-credit tools refuse unless the claim is a lost/stolen claim resolved with an error found.
   - These checks test the target claim's own state, not another problem's prerequisite: the tree's gates (other claims' reversals or final credits) are still unchecked by the tools. Plan checks are unchanged, and there are no forbidden imports.

### re-derivation (revision_7)
- Scripted sweep: compute_basis, policy_source, baseline.rule and replaced_by verbatim; every binding has a basis; fall-through = baseline; factor sets and counts unchanged (SL 4, RV 6, ZC 6, TL 4, WR 4, YC 5); prerequisite graph and sentences unchanged; overwrite hygiene C1/C3/C4 clean; scope (12-month look-back, referral) unchanged since revision_6.

### findings (revision_7)
**CG-20 SOURCE-POLICY RED (B1; members SL `s_` and TL `t_`) — the credit floor is placed differently in rule and compute.** The rule floors the standard credit ("the credit is never below zero") before "additions after them" and again at the end; the compute floors only after the additions. When the withheld amount exceeds the claimed transfer, the two readings differ by up to the added fees and allowance (witness above: 1.95 by the rule words against 0.00 by the compute). No consequence on the task worlds (withheld is below the transfer in both).

**Observations (revision_7).** O-17 The method sentence and the assembly sentence of SL/TL both say "never below zero"; with CG-20 fixed one of them becomes redundant.

### closing sweep and summary (revision_7, after the reveals)
- Every class raised in revisions 1–7 and every renderer class (B1 floors, A4, B3 gaps/ties, B6 framing, dead bindings, D1) re-swept across all six policies and six tools; the one open member is the SL/TL floor placement (CG-20). GT equals the blind values in both tasks.

## closing_checklist (revision_7)
Not closed: CG-20. All other Step-4 items hold as recorded in revision_6 (gates r7 OK).

VERDICT revision_7: task0=PASS task1=PASS charter=CG-20

## revision_8

### charter_global_frozen (revision_8)
- written 2026-10-23 before any revision_8 GT was read; same auditor; earlier revisions untouched.
- entry: worklog last non-blank line `REWORK round 8: gates 7/7 green` (checked); snapshot (execute-only) → `/tmp/erl0077_coord/snap_worker_payroll_card_servicing_r8.txt`, all 7 gates OK. Hashes: `card.extended.yaml` 51b0fc5d0b401977 (changed → re-derived), `task_tools.py` b598d810b8089415 (unchanged since revision_7 → the D1 tool checks of revision_7 carried forward), views r8 identical to r3–r7. Reworker claims read by id only (CG-20 plus round-7 / scored / gates notes).

### re-derivation (revision_8)
- **CG-20 closed.** SL and TL now floor the standard credit ("… the amount withheld is the lesser of that liability and liability_cap_timely_usd …; the credit is never below zero"), then add the adjustments ("replacements apply first, additions after them, and the credit is rounded half up to the cent once at the end"). The compute matches: `RND(MX(0, *_transfer - *_withheld) + *_fee_back + *_allow + 1e-9, 2)`. On the renderer's witness both give 1.95. All six policies now floor before additions, matching their rules.
- Renderer findings stay closed (scripted re-check across all six policies):
  - 1: claimed-transfer floor stated and implemented.
  - 2: no single-factor plain binding.
  - 3: the report day is limited to lost/stolen replacement orders, with the stolen-over-lost and same-reason-duplicate rules, in RV, ZC, WR and YC (SL and TL have no report day).
  - 4: no blocked-card framing clause.
  - 5: no dead binding.
  - 6: tool bodies unchanged since revision_7.
- Sweep:
  - compute_basis, policy_source, baseline.rule and replaced_by are verbatim in each rule, and every binding has a basis.
  - Every fall-through equals its baseline; factor sets and counts are unchanged (SL 4, RV 6, ZC 6, TL 4, WR 4, YC 5).
  - The scope (12-month look-back with fraud-review referral) is unchanged; the prerequisite graph and sentences are unchanged; overwrite hygiene C1/C3/C4 is clean.

### findings (revision_8)
- No RED. Observations O-5…O-17 stand (O-17 resolved: SL/TL now state the floor once).

### closing sweep and summary (revision_8, after the reveals)
- Every class raised in revisions 1–8 and every renderer class (B1 floors, A4, B3 gaps/ties, B6 framing, dead bindings, D1) re-swept across all six policies and six tools: no open member. GT equals the blind values in both tasks.

## closing_checklist (revision_8)
- Per-task files 0.md / 1.md correspond to tasks 0 and 1, _difficulty.md alongside, revisions 1–8 preserved, every revision_8 comparison PASS.
- Six extended policies covered; scopes {ZC, RV, SL} / {YC, WR, TL} disjoint and complete; tools and GT closed; uuid8s independent.
- Each tree: 2 prerequisite problems, 1 value_input edge, owner=user root, acyclic; difficulty graph acyclic.
- Every computation: self-sufficient baseline, 4–6 factors (≥ 2 parameter, ≥ 1 method), real three-tier ladders stated in the rule, multi-source and cross-difficulty factors per task, every factor bearing weight against an honest baseline, all-baseline figures definite and different from gold.
- Instantiation gates re-run on the final form: snapshot r8, all 7 OK.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

### charter_global_frozen (revision_9)
- written 2026-10-23 before any revision_9 GT was read; same auditor; earlier revisions untouched.
- entry: worklog last non-blank line `REWORK round 9: gates 7/7 green` (checked); snapshot (execute-only) → `/tmp/erl0077_coord/snap_worker_payroll_card_servicing_r9.txt`, all 7 gates OK. Hashes: `card.extended.yaml` 39637c978d99705a (changed → re-derived), `task_tools.py` b598d810b8089415 (unchanged), views r9 identical to r3–r8. Inputs added: the source items SRC-1 and SRC-2 of `audits/policy_kb/worker_payroll_card_servicing/_difficulty.md` revision_1 (read in full); reworker claims read by id only.
- Disclosure on revisions 3–8: both SRC items were open in charters I marked CLEAN or PASS. SRC-1: in revision_3 I closed CG-13 by checking rule against compute, but never checked the factor ladders' own wording. SRC-2: none of my revisions tested the wording of the signed-claim liability sentence for a second grouping. I now check every ladder's value/method text against its rule sentence (all 29 factors) and scan every arithmetic sentence for grouping ambiguity.

### SRC items and carried-over findings, re-checked across all six policies
- **SRC-1 closed.** The lost-card tier of all four early-pay ladders (vr, zc, wr, yc) now reads "the lesser of that fee and nbd_fee_bank_usd of the tier the worker's Access plan holds on the day the credit is figured". That matches the rule and `CPARAM(... access_plan_id=…)`. The old phrase "of the transfer's Access tier" occurs nowhere in the file (scripted count 0).
  - Ladder-vs-rule sweep over all 29 factors: every tier's condition and value or method agrees with its rule sentence:
    - liability limits: VZL 0 / late cap / timely cap;
    - prior liability: late cap / timely cap / 0 on the total disputed amount of claims resolved with error;
    - transaction fees: fees net of returns / free-withdrawal fee / nothing;
    - service, late and investigation allowances;
    - replacement fees: stolen / lost / none;
    - early pay: stolen / lost / nothing.
- **SRC-2 closed.** SL and TL (rule and baseline.rule) now read "the cardholder's liability is the liability limit less the liability already charged on the same loss, never below zero, or the disputed amount if that is smaller". That gives one grouping, min(disputed, max(0, limit − charged)), which is the compute's `MN(*_disputed, MX(0, *_limit - *_prior))`. The old ambiguous wording occurs nowhere in the file (scripted count 0).
  - The other four policies state liability without a subtraction ("the lesser of the disputed amount and the liability limit"), so there is no grouping question.
  - Grouping scan of every other arithmetic sentence in the six rules found no other two-grouping reading:
    - claimed transfer "less any … rebate …, never below zero";
    - due / credit "… less the cardholder's liability, never below zero" before additions;
    - reversal "limited to the available balance";
    - withheld "the lesser of that liability and liability_cap_timely_usd".
- **CG-20 and renderer findings 1–6 stay closed** (scripted re-check):
  - 1: the transfer floor is in all six computes; every result floors before additions, as its rule says.
  - 2: no single-factor plain binding.
  - 3: report days are restricted to lost/stolen orders, with the tie rules, in RV, ZC, WR and YC.
  - 4: no blocked-card framing clause.
  - 5: no dead binding.
  - 6: tools are unchanged.
- Sweep:
  - compute_basis, policy_source, baseline.rule and replaced_by are verbatim in each rule.
  - Every fall-through equals its baseline; factor sets and counts are unchanged; the 12-month scope route and the prerequisite graph and sentences are unchanged; overwrite hygiene C1/C3/C4 is clean.

### findings (revision_9)
- No RED.

### closing sweep and summary (revision_9, after the reveals)
- Every class raised in revisions 1–9, every renderer class and both KB source classes (ladder-vs-rule wording; arithmetic-sentence grouping) re-swept across all six policies, 29 factors and six tools: no open member. GT equals the blind values in both tasks.

## closing_checklist (revision_9)
All Step-4 items hold as recorded in revision_8; gates re-run on the final form (snapshot r9, all 7 OK).

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN
