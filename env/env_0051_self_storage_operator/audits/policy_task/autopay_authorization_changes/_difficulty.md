# Policy-task audit — autopay_authorization_changes / charter-global

## charter_global_frozen

- Scenario: env/env_0051_self_storage_operator; difficulty `autopay_authorization_changes`; category `autopay`; M=2.
- Freeze hashes (re-computed by the auditor, identical to the brief):
  - `tasks/autopay_authorization_changes/autopay.extended.yaml` sha256=54046803cbfabeb52ece9a13fa0a35178439fbc25cfa13d7305f73f19f1289c4
  - `tasks/autopay_authorization_changes/task_tools.py` sha256=5c2a450e7f15281e1c4bd9f14d4c623526b3291b7f4ce367e28f710f72a144e0
  - masked views `.audit_views/policy/autopay_authorization_changes/0.view.json` sha256=6646de98…8735f, `1.view.json` sha256=0886c48e…a05fa (identical to the brief)
- Freeze time: 2026-10-10T19:46Z (wall clock). Auditor: erl-task-policy-audit agent (independent of the instantiating agent).
- Fields read for this section: blueprint.yaml, db_schema.json, share_tools.py, products/autopay.yaml (base), products/unit.yaml and products/parking.yaml (parameters and the rate-increase / billing sentences only), the extended charter, task_tools.py. For the DSL semantics of `F/P/SUM/COUNT/LATEST/XSUM/XCOUNT/XLATEST/CFIELD/CPARAM/MONTHS` the auditor read the evaluator source `skills/erl-task-instantiate/scripts/check_compute.py` lines 220-400 (`build_env`, `MONTHS`) — tooling code, no task data — and used `build_env` in a scratch recomputation (/tmp/run_0051/audit_autopay_authorization_changes/recompute.py) on the masked views only.
- Masked and NOT read while writing this file: every `tasks/<i>.json` field (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, closure fields), worklog.md, any earlier audit. Nothing in this section derives from a revealed GT.

### Entry conditions (Step 0)
Gate snapshot supplied by the coordinator: check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK; check_traceability deferred (needs published KB); validate_scenario only "required document not found". Masked views and their hashes supplied. Entry conditions complete. These are qualification only, not proof.

Base copy: the first 930 lines of the extended charter are byte-identical to `blueprint/products/autopay.yaml` (diff shows only one trailing blank line before `extended_policies:`).

### policy_conflict_scan

Extended policies (5), target tools, owners:

| policy | target_tool | owner | computes | prerequisite |
| --- | --- | --- | --- | --- |
| autopay_ext_unit_draft_notice | send_unit_varying_amount_notice_30e2b3fb | agent | notified_amount | ach_catchup (value_input, state), card_catchup (state_gate, state) |
| autopay_ext_unit_ach_catchup | approve_unit_returned_draft_catchup_31270510 | user | approved_amount | [] |
| autopay_ext_unit_card_catchup | approve_card_catchup_charge_edda4662 | user | approved_amount | [] |
| autopay_ext_parking_draft_notice | send_parking_varying_amount_notice_109228c2 | agent | notified_amount | parking_ach_catchup (value_input, state) |
| autopay_ext_parking_ach_catchup | approve_parking_returned_draft_catchup_8c80cda9 | user | approved_amount | [] |

Overlap scan:
- Subjects: all five write `autopay_notice` rows of `notice_type=varying_amount_notice`. They are separated by object: unit vs parking agreement kind; the noticed due date (next draft due date) vs the oldest unpaid due date (catch-ups); bank-account vs card method. No two policies can claim the same `(autopay_id, related_due_date)` in a consistent world: the notice policies fix `related_due_date = next_draft_due_date`, the catch-ups fix it at `delinquent_since`, which is strictly earlier.
- Write-shape collision (observation O-1): every tool writes the identical row shape (`notice_type`, `notice_date`=today, `related_due_date`, `notified_amount`) to `autopay_notices`; the only difference is the salt inside `make_id`. Whether a notice was "approved by the tenant" or "sent by the care center" is not recorded on the row; the owner distinction rests entirely on the rule text and the docstrings.
- Base vs extended: see `override_declarations` — one undeclared conflict (F-1) on the timing of the ACH catch-up draft.
- Cross-category reads: unit_draft_notice / unit catch-ups read unit_rentals, unit_rate_changes, unit_ledger and unit parameters; parking policies read parking_rentals, parking_rate_changes, parking_ledger and parking parameters. No policy writes another category.
- Expected scope partition (to be confirmed against `charter_scope` after reveal): a unit tree (unit_draft_notice + unit_ach_catchup + unit_card_catchup) and a parking tree (parking_draft_notice + parking_ach_catchup). The two trees are disjoint and together cover all five extended policies.

### rule_compute_equivalence

Swept per policy, binding by binding against `compute_basis` and back against the rule. All bindings have a verbatim basis quotation; in the auditor's recomputation the bindings implement the quoted sentences, with these exceptions:

- **F-2 (SOURCE-POLICY RED, charter-global, no task world triggers it).** `first_period` in all five policies is `MONTHS(move_in_date|start_date, due) == 0`, while the rule says "when the [noticed / returned / declined] due date opens the agreement's first billing period". With the DSL `MONTHS` (whole months, minus one when the later day-of-month is smaller), a month-end anniversary makes the *second* period count as the first: move_in_date 2026-01-31, due 2026-02-28 → MONTHS=0. The unit and parking charters both say a month with no anniversary day "falls due on its last day" (unit.yaml `billing_day`, parking.yaml line 803), so 2026-02-28 is the second period's due date. Rule: later period (military discount or none). Compute: first period (greater of first_month_discount_pct, e.g. 0.5, and military). The two give different rents in that situation. Billing days in this difficulty's worlds are 15, 25 (task 0) and 20 (task 1); MONTHS is exact there, so neither task is affected.
- Observation O-2: `rescissions` counts any `increase_rescinded` row on the agreement, while the rule says "where no rescission is recorded" next to each concession/increase. The compute's reading (any rescission on the agreement voids both) is one reading of an unqualified phrase; no seeded rescission exists in either world.
- Observation O-3: concession/increase are taken from the latest row by `notice_date`; the rule speaks of "a retention concession whose effective date is on or before the noticed due date". With two concession rows the compute ignores an earlier one that is in force. Not seeded.
- Observation O-4: `settled_attempts` counts `result='ach_settled'` attempts; the rule says "settled and were returned". A settled attempt that was not returned is counted. In the seeded worlds every settled attempt for the returned due date was returned.
- Gates that are rule-only (not compute): the notice-period gate and the cap gate of the two notice policies, the active-status / NSF / no-re-presentment gates of the catch-ups. These are eligibility sentences; no compute binding is expected for them.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are five distinct pairs, each claimed by exactly one policy.
- uuid8s: 30e2b3fb, 31270510, edda4662, 109228c2, 8c80cda9 — five distinct values, no shared prefix, no sequential or adjacent pattern, no copy-with-new-tail. Pass.
- Docstrings: no tool names another tool; the only ordering-like word is "still declined after its retries" (approve_card_catchup_charge_edda4662), which describes the state of the card draft, not a position in a sequence. Pass.
- Tool bodies: each tool calls `ctx.create("autopay_notices", …)` with the caller's arguments and returns a receipt; no tool reads balances, drafts, notices or status and none refuses or hints. The module docstring says so as well. The tool layer judges no prerequisite. Pass.
- Observation O-5: the user tools take `notice_type` as an argument. The persona hand-over lines (both tasks) name "the authorization, the due date and the amount", not the notice type; the simulator has to take `varying_amount_notice` from the docstring ("which is the kind this action records").

### prerequisite_graph

- Every extended policy fills `prerequisite` (the three catch-ups are `[]`).
- Edges: unit_draft_notice → unit_ach_catchup (value_input, gate `carried_balance`, a real compute binding); unit_draft_notice → unit_card_catchup (state_gate, gate `autopay_notices.notified_amount`); parking_draft_notice → parking_ach_catchup (value_input, gate `carried_balance`). Every `problem` is an extended id in this file, none base, none self. Acyclic (depth 1).
- `policy_source` verbatim in the blocked policy's own rule: checked mechanically after whitespace normalisation — all three True.
- `form: state` on all three; no `fallback_reason` (correct for state form).
- `resolved_by` = the depended-on policy's `target_tool` on all three, and the tool's write (a varying_amount_notice on the right authorization for the oldest unpaid due date) is what `effect` says it is.
- `kind`/`gate`: value_input gates name the existing binding `carried_balance`. The state_gate names a column (`autopay_notices.notified_amount`) rather than an eligibility id; the root policy has no `eligibility` list, so its rule sentence is the gate itself (observation O-6).
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any prerequisite field.
- **F-3 (SOURCE-POLICY RED, charter-global): the `condition` of every edge differs in scope from its prerequisite sentence.**
  - unit ach edge. Sentence: "…a catch-up amount approved by the tenant for the oldest unpaid due date of every returned draft that may not be presented again." Condition: "…for every due date whose draft and re-presentment were returned." Situation: a Business Checking ACH unit authorization (`max_represents_per_entry: 2`) whose draft and first re-presentment were returned R01. Sentence: the entry may still be presented once more, so no catch-up is required. Condition: a catch-up notice is required. The ACH catch-up policy cannot give one, because it is open only where "the returned entry may not be presented again". The two give different results, and the condition's result can never be met.
  - unit card edge. Sentence: "every card draft on the tenant's other AutoPay authorizations that is still declined after its last retry". Condition: "…other card AutoPay authorizations whose **latest** due date has every attempt declined, with the last retry used". Situation: a card authorization whose 08-25 draft was declined on all retries and is still unpaid, and whose 09-25 draft was approved. Sentence: the gate waits on a catch-up for 08-25. Condition: the latest due date (09-25) is not declined, so the gate holds. The two give different results.
  - parking edge. Sentence: "every returned draft on the authorization **that may not be presented again** carries a catch-up amount…". Condition: "The parking authorization's notice history holds a varying-amount notice whose related due date is the parking agreement's delinquent_since date…" (no re-presentment qualifier). Situation: a Personal Savings parking draft returned R01 once and not yet re-presented. Sentence: nothing is waited on. Condition: a catch-up notice is required. The two give different results.
  - In both task worlds the sentence and the condition agree (task 0: Personal Checking, both attempts returned, the card's latest due date is the declined one; task 1: Personal Savings, both attempts returned). See the task files.

### prerequisite_sentences

Four-point test per edge:

1. unit ach edge: "The unit notice amount is fixed only after the notice history of the authorization shows a catch-up amount approved by the tenant for the oldest unpaid due date of every returned draft that may not be presented again."
   - (a) The own result is tied to the waited-on state by "only after". Pass.
   - (b) State form: the state is the notice history (autopay_notices) showing a catch-up amount for the oldest unpaid due date (unit_rentals.delinquent_since) on the drafts the re-presentment rule exhausts. But "approved by the tenant" names a performer and an action, and "catch-up amount" is not a table word: the row is a `varying_amount_notice` with `notified_amount`. Observation O-7 (form). No second reading follows from it, because only one policy's rule records a tenant-approved catch-up on the notice history.
   - (c) Names no tool, no policy id, no snake_case token, no row id. Pass.
   - (d) Strength and scope vs the condition: see F-3.
   - Single write: only approve_unit_returned_draft_catchup_31270510 (policy unit_ach_catchup: "the approval is recorded on the authorization's notice history as a varying-amount notice for the returned due date stating the unit catch-up amount… The returned due date is the agreement's oldest unpaid due date") produces that state. The notice policy writes only for the next draft due date. The card catch-up is restricted to card authorizations. The parking tools are restricted to parking. Unique.
   - Derivation: sentence → records (draft rows on the unit authorization: settled+returned R01/R09, re-presentments used up to `max_represents_per_entry`; `delinquent_since`) → the depended-on rule ("may approve on a recorded call a one-time catch-up draft… recorded… as a varying-amount notice for the returned due date") → resolving action: the tenant's own approval through the hand-over tool. One reading.
2. unit card edge: "No unit notice amount is fixed until every card draft on the tenant's other AutoPay authorizations that is still declined after its last retry carries a catch-up charge approved by the tenant on that authorization's notice history."
   - The connective is "until". It names no tool or id. "Approved by the tenant" is the same form observation as O-7. Only approve_card_catchup_charge_edda4662 produces the state.
   - Scope gap, observation O-8: the sentence covers any of the tenant's other card authorizations, but the card catch-up policy covers only "storage unit AutoPay draft on a card… on an authorization in active status". A tenant whose still-declined card draft is on a parking authorization, or on a card authorization that has already been suspended (2 consecutive failed due dates for Debit/Credit), meets a gate that no policy can resolve. No seeded world has this.
   - Realism observation O-9: a varying-amount notice on one agreement is withheld until the tenant approves a charge on a different agreement's card. The base varying-amount rule has no such link. It is a declared extended rule, so not a conflict, but it is an unusual procedure for a notice whose purpose is to inform.
3. parking edge: "The parking notice amount is set only once every returned draft on the authorization that may not be presented again carries a catch-up amount the tenant approved on the notice history for the parking agreement's oldest unpaid due date." The connective is "only once". The same form observation (O-7) applies. Only approve_parking_returned_draft_catchup_8c80cda9 produces the state. Single reading.
- No depended-on rule restates the blocked sentence. No rule carries a second wording, a tool name or another problem's id.
- Undeclared cross-problem orders: a scan of all five extended rules finds no ordering sentence that grounds no declared edge. The base ordering sentences ("the old one is retired when the new one is verified") ground no edge in this difficulty.

### override_declarations

Sentence-by-sentence sweep against each `base_policy_refs` entry:

- autopay_ext_unit_draft_notice / autopay_ext_parking_draft_notice (refs: varying_amount_notice, expiry_reminders, draft_amount_timing):
  - draft_amount_timing "The draft collects the agreement's full balance due on the draft date (draft_amount_basis), including past-due rent and fees": declared `overwrite`, replaced by "A [parking] draft run before its due date collects the rent charge of that due date together with the balance due on the draft date." The replacement speaks only of drafts run before the due date. Card drafts run on the due date, and for them the merged text no longer states an amount basis if the overwrite is read as global. Observation O-10: the overwrite does not state its scope. The notice policies themselves apply only where `varying_amount_notice_days > 0`, i.e. only to the Personal ACH methods, which all draft 2 days before the due date, so no scored quantity is affected.
  - draft_amount_timing "it never collects less (partial_draft_allowed)" vs varying_amount_notice "when no timely notice was sent, the draft for that due date collects only the previous draft amount": these are two base sentences in tension (observation O-11). The extended shortfall factor follows the varying-amount sentence. In both worlds the short draft is a seeded record (amount stated), so the agent reads the amount rather than choosing between the sentences.
  - draft_amount_timing cap sentence: followed ("A notice is sent only for an amount not above draft_cap_usd"; skipped_over_cap handled by the shortfall factor). Posting sentence: not touched.
  - varying_amount_notice notice-period gate and counting rule: followed ("the notice is sent only when that due date less draft_days_before_due falls at least varying_amount_notice_days calendar days after the handling date"). "States the amount to be drafted and the due date": followed. Dedup once per type per due date: inherited.
  - expiry_reminders: no sentence governs a varying-amount notice amount; nothing overridden.
- autopay_ext_unit_ach_catchup / autopay_ext_parking_ach_catchup (refs: varying_amount_notice, expiry_reminders, retry_and_suspension, returns), `overwrite: []`:
  - **F-1 (SOURCE-POLICY RED, undeclared override).** Base autopay_evt_varying_amount_notice: "For a method whose varying_amount_notice_days is above zero, a draft whose amount differs from the previous successful draft on the same authorization, for example after a rent change or because late fees are due, may be submitted only when the handling date is not earlier than the varying-amount notice date plus varying_amount_notice_days." Extended (unit): "the approval is recorded on the authorization's notice history as a varying-amount notice for the returned due date stating the unit catch-up amount, and the catch-up runs as a single entry on the next banking day." Parking says the same ("…and the catch-up runs as a single entry on the next banking day"). Same situation: a Personal Checking/Savings authorization (notice days 10), a catch-up approved and recorded as a varying-amount notice on day D for an amount that includes late fees and so differs from the previous successful draft. Base: the catch-up draft may be submitted no earlier than D+10. Extended: it is submitted on the next banking day after D. Neither `overwrite` names the base sentence. The card catch-up is not affected (Debit/Credit `varying_amount_notice_days: 0`).
  - retry_and_suspension "An ACH draft returned for insufficient or uncollected funds is presented again up to max_represents_per_entry times…; any other return is never presented again": the catch-up is a new tenant-approved entry with its own amount, not a re-presentment. Followed. "A failed or returned draft leaves the rent unpaid, so late fees and the lien or tow schedule run under the agreement's own rules": followed (the late/lien/fee factors read the posted fees).
  - returns "A return reverses the autopay payment… and the agreement's returned-payment fee rule applies": followed (returned-payment fee factor). "Each draft is returned at most once": not touched.
  - expiry_reminders: nothing overridden.
- autopay_ext_unit_card_catchup (refs: varying_amount_notice, expiry_reminders, retry_and_suspension), `overwrite: []`:
  - retry_and_suspension "A declined card draft is retried… up to max_retries_per_draft retries for the due date": the catch-up charge is a further charge for the same due date after the retries are used. Observation O-12: base does not say whether a tenant-approved one-time charge counts as a retry. No scored quantity depends on it.
  - varying_amount_notice: notice days are 0 for Debit/Credit, so the notice-period sentence does not bite. Dedup: inherited.

### factor_ladders

Declared counts (as written):

| policy | factors | parameter | method | cross_difficulty |
| --- | --- | --- | --- | --- |
| unit_draft_notice | 6 | rent_in_force, rent_discount, projected_late_fees, projected_lien_fees | past_due_carry, latest_draft_shortfall | unit ×5 |
| unit_ach_catchup | 6 | catchup_rent_discount, returned_payment_fees, returned_period_late_fees, catchup_lien_process_fees, courtesy_waived_fee | catchup_late_fee_amount | unit ×5 |
| unit_card_catchup | 4 | charge_rent_discount, declined_period_late_fees, charge_lien_process_fees | charge_late_fee_amount | unit ×4 |
| parking_draft_notice | 5 | parking_rent_in_force, parking_rent_discount, projected_parking_late_fee | parking_past_due_carry, parking_latest_draft_shortfall | parking ×4 |
| parking_ach_catchup | 6 | parking_catchup_discount, parking_returned_payment_fees, parking_charge_left_out, parking_other_fees | parking_rent_recollected, parking_catchup_late_fee | parking ×6 |

Structure checks run on every factor: `decides` is an input (never `result`) and appears among its own bindings. Bindings are pairwise disjoint within each policy (checked mechanically). Every ladder has ≥3 tiers. Every tier is stated in the rule and branched in compute. Every fall-through equals the declared `baseline`. Every `baseline.rule` sentence is in the rule (checked mechanically). `baseline.params` keys are consistent with `baseline.rule`. Multi-source: rent-in-force (rate-change row + absence of a rescission row + the enrollment's next due date), past-due carry (catch-up notice row + agreement balance) and the shortfall (draft row + rate-change rows) are conjunctions over distinct records.

Findings on ladder reality:

- **F-4 (SOURCE-FACTOR RED): the "first billing period" tier of all five rent-discount factors (rent_discount, catchup_rent_discount, charge_rent_discount, parking_rent_discount, parking_catchup_discount) can never be reached by a customer who reaches these writes.** Each of these quantities concerns a *drafted* due date. For the notices it is "the authorization's next draft due date". For the catch-ups it is the due date "whose… draft… was returned" / "still declined", identified with the oldest unpaid due date. Under the charters a drafted due date is never the first period:
  - autopay base: the covered agreement must be "in active, delinquent or moving_out status for a storage unit, or active, delinquent, termination_noticed or moving_out status for parking", so it must already be moved in or started. "The first due date drafted is the first due date that falls at least enrollment_cutoff_days_before_due calendar days after the verified date; an earlier due date is paid by the tenant directly" (cutoff ≥ 1).
  - unit charter: "the first billing period starts on the move-in date and is charged at move-in". Parking charter: "The first period is charged at start".
  - So every drafted due date is later than the verified date (≥ the enrollment date ≥ the move-in/start date), and the move-in/start due date is never drafted. The tier "when the … due date opens the agreement's first billing period" holds of no customer who reaches these writes. The move-in discount is something this line of business weighs for the move-in charge, not for an AutoPay draft or its catch-up. Each ladder therefore has two live tiers (military / none), below the three-tier floor. Per-task consequence on factor counts: see the task files. (F-2 is the compute-side counterpart: the compute can reach the tier only through the month-end MONTHS artefact.)
- **F-5 (SOURCE-FACTOR RED): latest_draft_shortfall and parking_latest_draft_shortfall write one tier as two.** Tier 1: "the latest draft … was recorded as skipped_over_cap → the whole rent charge of that draft's due date is left unpaid". Tier 2: "the latest draft's submitted amount is below the rent charge of its own due date → that rent charge less the submitted amount". The base charter fixes a skipped draft's amount: "the draft is recorded as skipped_over_cap with amount 0.00" (autopay_evt_draft_amount_timing; the event field reads "Amount drafted, USD (0.00 when skipped)"). A skipped draft therefore satisfies tier 2's condition (0.00 < rent charge), and tier 2's method gives rent charge − 0.00, the same as tier 1. The two tiers overlap as stated and select the same method and value. The ladder has two distinct outcomes (rent charge − submitted amount; nothing).
- **F-6 (SOURCE-FACTOR RED, structure; no task world triggers it): parking_charge_left_out tiers overlap as stated with different outcomes.** Tier 1: "the latest courtesy late-fee waiver on the parking agreement was credited against a late fee → the posted late fee is left out". Tier 2: "the latest billing-error correction was credited against a returned-payment fee → returned_payment_fee_usd is left out". Neither condition excludes the other. The rule ("leaves out a charge the tenant was excused from: the posted late fee where …; returned_payment_fee_usd where …; and nothing otherwise") does not say which one wins, or whether both are left out, when both records exist. Second reading: both left out. The compute takes tier 1 only. Task 1 has no billing-error correction, so no consequence there.
- Observation O-13 (labels): the same late-fee clamp (late_fee_max_usd / percentage of rent / late_fee_flat_usd) is labelled `method` in catchup_late_fee_amount, charge_late_fee_amount and parking_catchup_late_fee, and `parameter` in projected_late_fees and projected_parking_late_fee. Identical ladders cannot carry both labels honestly. Two of its three tiers select a fixed fee, which is a substituted number. The unit ACH and card catch-ups each have this clamp as their only `method` factor, so their method count rests on the contested label. Recorded as an observation, because the percentage-of-rent vs flat-fee distinction is arguably a change of method.
- Observation O-14 (baselines of nested clamps): the `baseline.rule` of the unit ACH and card catch-ups states only the contracted monthly rent and is silent on any late fee, while catchup_late_fee_amount / charge_late_fee_amount declare `late_fee_flat_usd` as baseline. That value equals the ladder's fall-through but is not stated by baseline.rule. Under all baselines together the nesting factor (period late fees) is 0, so the full fall-back number is still definite.
- Observation O-15 (returned_payment_fees, unit ACH catch-up): the policy is open only where the NSF-returned entry "may not be presented again". Every ACH variant has `ach_represent_on_nsf: true` with `max_represents_per_entry` 1 or 2, so in the ordinary case where the returned due date is the oldest unpaid one, every eligible customer has ≥2 settled-and-returned attempts. The "once" and "nothing" tiers are reachable only if an older unpaid due date was never drafted. The ladder divides customers only in such edge cases. Recorded as an observation because a reachable world exists.
- **F-7 (SOURCE-FACTOR RED, structural): every catch-up computation reconstructs the agreement's stored balance.** The unit ACH, card and parking catch-ups add the period's rent charge, the returned-payment fees, the posted late fees and lien fees, take out the waived fee and the direct payments, and add the other posted fees. That is a decomposition of the ledger aggregate `balance_due` ("identically the sum of rent_balance deltas on the ledger") whenever the current delinquency is the agreement's only debt. The stored `balance_due` then names the computation's outcome. Reading it and applying every ladder cannot be told apart by the score. The demonstration is per world (task files).
- Realism observation O-16: projected_lien_fees tier 2 asserts "because its lien notice day falls before the noticed draft". For a delinquency anchored on the latest due date (e.g. delinquent since 10-15, noticed draft 11-13, Premier lien notice +40 days = 11-24) the assertion is false and the tier projects a fee that will not have posted. Not reached in task 0, where carried=0 selects tier 1.

Counts surviving F-4/F-5/F-6 (per policy; per-task bounds are judged in the task files):
- unit_draft_notice: 6 − rent_discount − latest_draft_shortfall = 4 (3 parameter, 1 method). Within bounds.
- unit_ach_catchup: 6 − catchup_rent_discount = 5 (4 parameter, 1 method). Within bounds.
- unit_card_catchup: 4 − charge_rent_discount = **3**. Below the floor of 4.
- parking_draft_notice: 5 − parking_rent_discount − parking_latest_draft_shortfall = **3** (2 parameter, 1 method). Below the floor of 4.
- parking_ach_catchup: 6 − parking_catchup_discount − parking_charge_left_out = 4 (2 parameter, 2 method). Within bounds.

### findings

| id | class | summary | bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-POLICY RED | ACH catch-up "runs … on the next banking day" vs base varying-amount notice period (10 days for Personal ACH); `overwrite: []` | task 0 (unit ACH catch-up), task 1 (parking ACH catch-up) |
| F-2 | SOURCE-POLICY RED | `first_period` compute vs rule diverge on month-end anniversaries | none of the seeded worlds (billing days 15/25/20) |
| F-3 | SOURCE-POLICY RED | each edge's `condition` is broader or narrower than its prerequisite sentence | task 0 (both edges), task 1; same conclusion on both worlds |
| F-4 | SOURCE-FACTOR RED | first-billing-period discount tier unreachable for drafted due dates in all five discount factors | task 0 (3 factors), task 1 (2 factors) |
| F-5 | SOURCE-FACTOR RED | shortfall ladders: skipped_over_cap tier duplicates the below-rent tier | task 0, task 1 |
| F-6 | SOURCE-FACTOR RED | parking_charge_left_out tiers overlap as stated with different outcomes | task 1 (structure only; no correction seeded) |
| F-7 | SOURCE-FACTOR RED | catch-up computations reconstruct `balance_due` | task 0 (ACH and card), task 1 |
| O-1…O-16 | observations | see above | — |

## closing_checklist

Written after the reveals (2026-10-10T19:49Z). The charter-global section above was frozen before any reveal and is not edited.

- Per-task files: 0.md and 1.md, one per task, alongside this file. First revision; no older revision exists.
- Every comparison section carries a verdict. **Not every relationship passes:**
  - task 0: SOURCE-POLICY RED (F-1), SOURCE-FACTOR RED (F-4, F-5, F-7, card catch-up below 4 factors, unit seed over the rate-increase cap), SOURCE-CHAIN PASS, SOURCE-TASK PASS.
  - task 1: SOURCE-POLICY RED (F-1), SOURCE-FACTOR RED (F-4, F-5, F-6, F-7, parking notice below 4 factors), SOURCE-CHAIN PASS, SOURCE-TASK PASS.
- Coverage and scopes:
  - charter_scope task 0 = {unit_ach_catchup, unit_card_catchup, unit_draft_notice} with their three tools.
  - task 1 = {parking_ach_catchup, parking_draft_notice} with their two tools.
  - Pairwise disjoint; the union covers all 5 extended policies and all 5 task tools.
  - uuid8s independent (see `### action_binding_and_uuids`).
- Problem trees:
  - task 0 has 2 prerequisite problems, 1 value_input ≥ max(1,1), two owner=user writes.
  - task 1 has 1 prerequisite problem, 1 value_input, one owner=user write.
  - Both acyclic, and the difficulty graph is acyclic (two disjoint stars).
- Factors: not met.
  - Surviving counts are below 4 for unit_card_catchup (task 0) and parking_draft_notice (task 1).
  - Unreal ladders: F-4 in all five policies, F-5 in both notices, F-6.
  - All five catch-up and notice results bear weight against their declared baselines, and every full fall-back number (878.00, 389.00, 125.00, 526.50, 285.00) is definite and differs from gold. But the three catch-up results equal the seeded `balance_due` (F-7).
- Gates: the instantiation-stage gate snapshot is the coordinator's (all green except the deferred traceability check). This auditor did not re-run the gates, and they do not change any verdict above.
- Difficulty-level conclusion: **the difficulty does not pass the source-layer audit.** Both tasks are SOURCE-POLICY RED and SOURCE-FACTOR RED. The problem trees and the unique solutions hold: the blind derivation matched GT on every written value (489.00, 177.50, 478.20; 241.50, 304.14).

## revision_2

### charter_global_frozen (revision 2)

- Inputs (re-hashed by the auditor, identical to the coordinator's brief):
  - autopay.extended.yaml sha256=d0ec30ca34977b36a17459c775a52542d87c4b001fbd5101035008b7a3483a1a (changed). The charter-global section is therefore re-derived in full, not carried forward.
  - task_tools.py sha256=5c2a450e…44e0 (unchanged). `### action_binding_and_uuids` of revision 1 is carried forward by reference on that hash.
  - views 0.view.json sha256=59ba265e…8a73 and 1.view.json sha256=12a5ce9b…5727 (both changed).
  - The blueprint is unchanged (base copy still byte-identical to products/autopay.yaml).
- Freeze time 2026-10-10T21:18Z. Auditor: erl-task-policy-audit agent.
- Masked and not read before this section was written: every round-2 `tasks/<i>.json` field. Round-1 GT figures are in this auditor's memory from the revision-1 reveal. They concern the round-1 worlds, and every round-2 figure below was recomputed from the round-2 views and charter.
- contamination_disclosure: the round-1 reveal exposed the round-1 GT shape (tool sequence, catch-up/notice pattern) for the same charter family. This is unavoidable in a re-audit and is declared. The round-2 derivations rest only on the round-2 charter and views.
- DSL semantics: same evaluator source as revision 1. Scratch: /tmp/run_0051/audit_autopay_authorization_changes/recompute_r2.py.

Regrouped trees (from the `prerequisite` fields):
- autopay_ext_unit_draft_notice ← autopay_ext_unit_ach_catchup (value_input, carried_balance, state).
- autopay_ext_parking_draft_notice ← autopay_ext_parking_ach_catchup (value_input, carried_balance, state), and ← autopay_ext_unit_card_catchup (state_gate, autopay_notices.notified_amount, state). The card gate moved from the unit notice to the parking notice and is now restricted to the tenant's storage unit card authorizations in active status.
- Acyclic. Every `problem` is an extended id. policy_source is verbatim in the blocked rule (mechanical check, all True). There is no `fallback_reason` (all state form). `resolved_by` = each depended-on target_tool.

### Round-1 RED closure check

| item | round-1 class | revision-2 evidence | status |
| --- | --- | --- | --- |
| F-1 undeclared override (catch-up timing) | SOURCE-POLICY RED | Both ACH catch-ups now declare `overwrite` on autopay_evt_varying_amount_notice's notice-period sentence, with replaced_by "A unit/parking catch-up the tenant approves for a stated amount on a recorded call is a single entry authorized for that exact amount, so it is not held for varying_amount_notice_days and runs on the next banking day." The replaced_by sentence is verbatim in each rule. | **closed**. Residual observation R2-O1: the superseded clause is the whole general sentence while the replacement speaks only of catch-ups. Its scope is implied by the replaced_by wording (same pattern as O-10). Regular drafts keep the notice period through the notice policies' own gate. |
| F-2 MONTHS first-period artefact | SOURCE-POLICY RED | No `first_period` / `MONTHS(` binding remains in any compute. | **closed** |
| F-3 condition vs sentence scope | SOURCE-POLICY RED | unit edge: condition "returned for insufficient or uncollected funds whose due date has used max_represents_per_entry re-presentments" = sentence "returned for insufficient or uncollected funds that may not be presented again". Parking edge: the same. Card edge: condition "card AutoPay authorization … on a storage unit agreement, in active status, that has a due date whose draft attempts are all declined with max_retries_per_draft retries used" = sentence "every card draft on the tenant's storage unit AutoPay authorizations in active status that is still declined after its last retry". | **closed** |
| F-4 unreachable first-period discount tier | SOURCE-FACTOR RED | The discount factors are removed. The notices now carry `noticed_period_charge` / `parking_period_charge` (moving_out with vacate ≤ noticed due date → nothing; military → rent × (1 − pct); otherwise rent). The moving_out tier is reachable: autopay enrollment allows moving_out units and parking, and a planned vacate date between the draft date and the due date still leaves the authorization drafting. The catch-ups put the military rent charge into the baseline. | **closed** |
| F-5 shortfall ladder duplicated tier | SOURCE-FACTOR RED | Shortfall factors are removed. `latest_unpaid` is now a baseline binding (in-flight model). | **closed** |
| F-6 parking_charge_left_out overlapping tiers | SOURCE-FACTOR RED | Now `parking_charges_left_out` with four disjoint tiers (both / waiver only / correction only / none), stated in the rule and branched in compute. | **closed** |
| F-7 catch-ups reconstruct `balance_due` | SOURCE-FACTOR RED | Catch-ups now net the in-flight draft (unit/parking) or project charge-day fees and net direct payments (card). Per-world check in the task files: no catch-up equals a single stored field. | **closed** at the stamp level. Residual observation R2-O2 in the task files: the ACH catch-ups equal balance_due − in-flight amount, two records combined. |
| O-13 clamp labels | observation | All late-fee clamps are now `parameter`. | closed |
| O-16 lien-day assertion | observation | `lien_day_reached` binding added, with its sentence in the rule. | closed |
| O-2 / O-4 / O-7 / O-8 / O-10 | observations | "recorded on the agreement"; "both returned since the due date is still unpaid"; performer wording removed; card gate restricted to storage unit card authorizations in active status; overwrite replaced_by now says "A bank-account draft, which runs before its due date". | closed |
| O-3 latest concession by notice date | observation | Rule text unchanged on this point. | **not closed** (claimed closed). Still an observation; nothing seeded. |
| O-9 notice gated on another agreement's charge | observation | Narrowed to storage unit card authorizations, but the gate now holds a **parking** notice until a **storage unit** card catch-up exists. | open as an observation |
| T1-O1 undefined "month before the handling date" | observation | The parking catch-up now says "after the same calendar day of the previous month and up to the handling date". The **card catch-up** (new text) still says "in the month before the handling date" twice, for direct payments and returned-payment fees. | **partially closed**. See R2-O3 and task 0. |

### New charter-global findings (revision 2)

- **R2-F1 (SOURCE-POLICY RED, charter-global, no seeded world triggers it): the notice and catch-up policies contradict each other on whether an in-flight draft pays when a lien notice fee (unit) or tow notice fee (parking) is posted.**
  - autopay_ext_unit_ach_catchup: "where a lien notice fee is posted, the in-flight draft is refused as a partial payment, so its submitted amount is added and the catch-up covers what that draft would have paid". Parking has the same with "where a tow notice fee is posted".
  - autopay_ext_unit_draft_notice: "A payment is applied to the oldest charges first, so the in-flight draft first pays the balance due on the handling date and only what is left of it reaches its own due date's rent charge". Parking has the same, with no lien/tow exception.
  - Same situation: a unit with a lien notice fee posted against the oldest unpaid due date, past-due balance B = 600.00, in-flight draft X = 350.10 for the next due date, rent charge C = 365.85.
    - Catch-up: the draft is refused, and the catch-up = B + X = 950.10.
    - Notice: the draft pays first, so pastdue_left = 249.90, the catch-up covers it, carried = 0, and latest_unpaid = C − max(0, X − B) = 365.85.
    - Under the catch-up's own reading (the draft is refused, and 950.10 pays B and 350.10 of C), the in-flight period is short 15.75, not 365.85. Under the notice's reading the refused draft has paid 350.10 of the past due.
  - The two policies give different notice amounts for the same world. The unit charter's `partial_payment_accepted_after_lien_notice: false` and the parking charter's `partial_payment_accepted_after_tow_notice: false` back the catch-up reading, and the notices ignore it.
- **R2-F2 (SOURCE-POLICY RED, rule ≠ compute, charter-global; the seeded declines are NSF so no task world triggers it): card_rent_recollected counts only `declined_insufficient_funds`.**
  - Rule: "while fewer declined attempts than one plus max_retries_per_draft are recorded for it". Compute: `declined_attempts = COUNT(... result='declined_insufficient_funds')`.
  - Situation: a debit authorization whose due date was declined `declined_expired_card` on attempts 1–3. That is retried per base (`retry_on_decline`), not an immediate-suspend code, so the authorization is still active and eligible.
  - Rule: retries are used, so the rent charge is re-collected. Compute: declined_attempts = 0 < 3, so nothing is re-collected. The two differ by the whole rent charge.
- **R2-F3 (SOURCE-FACTOR RED): the first tier of card_rent_recollected cannot be reached by any customer who reaches the write.** The card catch-up is open only to "A tenant whose storage unit AutoPay draft on a card is still declined after max_retries_per_draft retries". The tier "nothing while a retry of the declined due date is still allowed, that is while fewer declined attempts than one plus max_retries_per_draft are recorded for it" therefore never holds under the rule. (The compute reaches it only through R2-F2.) The ladder has two live tiers. With the factor struck, the card catch-up keeps 5 factors, **all `parameter`**, which is below the 1-`method` floor. Consequence: task 0.
- **R2-F4 (SOURCE-FACTOR RED): the notice baselines are not self-sufficient.**
  - Both notice `baseline.rule`s say "The rent charge of a due date is the rent in force on that due date less military_discount_pct…" (parking: "A parking rent charge is the parking rent in force on its due date…"). "Rent in force" is defined only by the rent-in-force ladder sentence, which is the rent_in_force / parking_rent_in_force factor's ladder.
  - That factor's `baseline` (contracted rent) replaces only `noticed_rent`. `latest_rent`, the rent in force on the in-flight draft's due date, sits in no factor's bindings and keeps the full concession/increase ladder under "all baselines".
  - A reader of the computation document alone cannot compute "the rent in force" on the in-flight due date. Reading it as the contracted rent gives one fall-back; the compute's all-baseline evaluation gives another. Per-world figures are in the task files.
- R2-O4 (observation): parking in-flight netting tier 2 tests "a tow notice fee is posted on the parking agreement" at any time. The unit counterpart is scoped to the returned due date. A tow fee from an earlier, cured cycle would refuse today's draft, which the parking charter's "after the tow notice" scoping does not support. Nothing seeded.
- R2-O5 (observation): `pastdue_left` = `MX(0, balance_today - in_flight)` is not rounded, and the carry tier compares it with the catch-up at equality. On the unit world 489.00 − 350.10 evaluates to 138.89999999999998, so the ≥ test passes by float luck in the safe direction. A world whose subtraction lands just above the catch-up would flip the tier and add the lien notice fee.
- R2-O6 (observation): the notice baselines apply the military discount to the in-flight period's rent charge, but give the noticed period undiscounted ("contracted monthly rent for the noticed due date"). The same discount is baseline for one period and a factor tier (`noticed_period_charge`) for the other.
- R2-O7 (observation): direct_reversed sums every `unit_payment_reversal` in the window, not only reversals of the direct payments it nets. In task 0's world the only reversal is of the direct phone payment, so there is no divergence there.
- Carried forward unchanged and accepted with the stated reasons: O-1, O-6, O-11, O-12, O-14, O-15.

### factor_ladders (revision 2)

| policy | factors | parameter | method | surviving after R2-F3 |
| --- | --- | --- | --- | --- |
| unit_draft_notice | 5 | rent_in_force, projected_late_fees, projected_lien_fees | noticed_period_charge, past_due_carry | 5 (3p/2m) |
| unit_ach_catchup | 6 | returned_payment_fees, catchup_late_fee_amount, returned_period_late_fees, catchup_lien_process_fees, courtesy_waived_fee | in_flight_netting | 6 (5p/1m) |
| unit_card_catchup | 6 | card_returned_payment_fees, charge_late_fee_amount, declined_period_late_fees, charge_lien_process_fees, card_waived_fee | card_rent_recollected | **5 (5p/0m)** |
| parking_draft_notice | 4 | parking_rent_in_force, projected_parking_late_fee | parking_period_charge, parking_past_due_carry | 4 (2p/2m) |
| parking_ach_catchup | 6 | parking_returned_payment_fees, parking_catchup_late_fee, parking_charges_left_out, parking_other_fees | parking_rent_recollected, parking_in_flight_netting | 6 (4p/2m) |

Structure checks:
- Bindings are disjoint (mechanical). `decides` is in the bindings. Ladders have ≥3 tiers. Fall-throughs equal the baselines. Baseline sentences are in the rules. compute_basis is verbatim in the rules (mechanical: no misses).
- Ladders are distinct in outcome. No overlapping tiers remain (F-6 is closed). Multi-source tiers: rent_in_force (rate-change row + absence of a rescission + due date), past_due_carry (catch-up notice + balance + in-flight draft), in_flight_netting (draft row + lien/tow fee row).
- Realism: in-flight netting tier 2 is grounded in the unit/parking partial-payment-after-notice parameters. The moving_out period tier is grounded in move-out practice. Projected charge-day fees are grounded in the unit fee schedule.

### findings (revision 2)

| id | class | bears on |
| --- | --- | --- |
| R2-F1 | SOURCE-POLICY RED | no seeded world (no lien/tow notice fee posted in either task) |
| R2-F2 | SOURCE-POLICY RED | no seeded world (task 0's card declines are NSF) |
| R2-F3 | SOURCE-FACTOR RED | task 0 (card catch-up has no live method factor) |
| R2-F4 | SOURCE-FACTOR RED | task 0 (parking notice), task 1 (unit notice) |
| R2-O1…O7, O-3, O-9, T1-O1 residue | observations | see the task files |

### closing_checklist (revision 2)

Written after the revision-2 reveal (2026-10-10T21:20Z). The revision-2 charter-global section above was frozen first and is not edited. Revision-1 text above is untouched.

- Files: 0.md and 1.md each carry `## revision_2` with a frozen derivation, a comparison and findings. Note that task indices now hold swapped worlds (0 = Teodoro / parking tree, 1 = Marisol / unit tree).
- Round-1 RED closure:
  - Closed: F-1, F-2, F-3, F-4, F-5, F-6, F-7, T0-F1, T0-F2, T0-F3, T1-F1, T1-F2.
  - Observations: O-2, O-4, O-5, O-7, O-8, O-10, O-13 and O-16 are closed. O-3 is **not** closed, despite the claim. O-9 is narrowed but still open. T1-O1 is only partially closed: the card catch-up keeps the undefined window (R2-O3).
  - Left unchanged by the reworker and accepted as observations: O-1, O-6, O-11, O-12, O-14, O-15.
- New defects introduced by the rework:
  - **R2-F1** (SOURCE-POLICY RED, charter-global): notice vs catch-up disagree on an in-flight draft once a lien or tow notice fee is posted.
  - **R2-F2** (SOURCE-POLICY RED, charter-global): the card catch-up counts only NSF declines while its rule counts all declines.
  - **R2-F3** (SOURCE-FACTOR RED): the card catch-up's only method factor has a tier that its own eligibility rules out.
  - **R2-F4** (SOURCE-FACTOR RED): the notice baselines use "rent in force", which only a factor's ladder defines.
  - R2-F1 and R2-F2 bear on no seeded world.
- Scopes: task 0 = {parking_ach_catchup, unit_card_catchup, parking_draft_notice}; task 1 = {unit_ach_catchup, unit_draft_notice}. Pairwise disjoint, with all 5 policies and 5 tools covered.
- Trees: task 0 has n=2 (1 value_input, 1 state_gate, 2 user writes). Task 1 has n=1 (1 value_input, 1 user write). Acyclic.
- Regression check: blind derivations equal GT on every written value (45.00, 142.50, 560.64; 138.90, 827.35). Persona and tool layer have no regressions. Seeds are charter-consistent.
- Gates: as reported by the coordinator; not re-run by the auditor.
- Per-task verdict (revision 2):
  - task 0: SOURCE-POLICY PASS, SOURCE-CHAIN PASS, **SOURCE-FACTOR RED** (R2-F3, R2-F4), SOURCE-TASK PASS.
  - task 1: SOURCE-POLICY PASS, SOURCE-CHAIN PASS, **SOURCE-FACTOR RED** (R2-F4), SOURCE-TASK PASS.
- Difficulty conclusion (revision 2): **does not pass**. Both tasks are SOURCE-FACTOR RED, and the charter carries two charter-global SOURCE-POLICY REDs (R2-F1, R2-F2) that no current world triggers.

## revision_3

### charter_global_frozen (revision 3)

- Inputs (re-hashed):
  - autopay.extended.yaml sha256=c27bd90183f4b2c18c82bd24a8e6097a5d6a5d14944d8fd5226da35f27412060 (changed). The charter-global section is re-derived. A copy is kept at /tmp/run_0051/audit_autopay_authorization_changes/extended_r3.yaml for later diffs.
  - task_tools.py sha256=5c2a450e…44e0 (unchanged). The tool / uuid conclusions of revision 1 are carried forward on that hash.
  - Views 0/1 (59ba265e… / 12a5ce9b…) are unchanged since revision 2.
  - Base copy is still byte-identical to the blueprint.
- Freeze time 2026-10-10T21:45Z. Auditor: erl-task-policy-audit agent.
- No round-3 tasks/*.json opened before this section and the two per-task revision_3 freezes were written.
- contamination_disclosure: the round-2 GT for these same two worlds is known from the revision-2 reveal. Every revision-3 figure is recomputed from the revision-3 charter, so that knowledge cannot certify a revision-3 value.
- Mechanical checks:
  - policy_source is verbatim on all 3 edges.
  - compute_basis is verbatim in each rule.
  - every overwrite replaced_by is in its rule.
  - every baseline sentence is in its rule.
  - bindings are disjoint.

### Round-2 RED closure check

| item | revision-3 evidence | status |
| --- | --- | --- |
| R2-F1 (in-flight draft vs lien/tow notice) | Notices: "while its result is still empty it is in flight and counts at its submitted amount, unless a lien [tow] notice fee is posted for the current delinquency, in which case the draft is refused as a partial payment and counts as nothing". The compute sets in_flight = 0 when lien_fee_posted / tow_fee_posted (period_start = delinquency_anchor). A catch-up excess now reaches the in-flight period ("the in-flight draft and then any catch-up amount … first pay the balance due …"; compute catchup_excess). Re-running the round-2 situation (B = 600.00, X = 350.10, C = 365.85, lien notice fee posted): catch-up B + X = 950.10; notice pastdue_left = 600.00, carried 0, catchup_excess 350.10, latest_unpaid = 365.85 − 350.10 = 15.75. The two policies now agree. | **closed** |
| R2-F2 (card declines NSF-only in compute) | The rule says "declined attempts (for insufficient funds or an expired card)". The compute counts declined_insufficient_funds + declined_expired_card. | **closed** |
| R2-F3 (card_rent_recollected tier 1 unreachable) | Eligibility is now "declined for insufficient funds or an expired card … whether or not its retries are used". The "retry still allowed → nothing re-collected" tier is reachable by an eligible customer before the last retry. | **closed**. The card catch-up has 6 factors (5p/1m), all live. |
| R2-F4 (notice baseline not self-sufficient) and R2-O6 | Both notice baselines now state "the contracted monthly rent of the in-flight [parking] draft's own due date". `latest_rent` is bound to rent_in_force (baseline contracted_rent), and `latest_charge` to the period-charge factor (baseline latest_rent). The baseline text alone gives contracted rent for both periods, the in-flight draft as submitted (or nothing after a lien/tow notice fee), and the remaining past due. Computed from the text: unit world 389.00 + 138.90 + 389.00 = **916.90**; parking world 285.00 + 45.00 + 285.00 = **615.00**. These equal the compute's all-baselines evaluation, so there is one definite fall-back. Both periods are now treated alike, which also closes R2-O6. | **closed** |
| O-3 | "the most recently noticed retention concession … the most recently noticed existing-customer rate increase", which matches the XLATEST-by-notice_date compute. | closed |
| T1-O1 / R2-O3 | The card catch-up window now reads "after the same calendar day of the previous month and up to the handling date", in both places. | closed |
| R2-O4 | Tow fee checks are scoped to the current delinquency (period_start = delinquent_since / returned_due) in both parking policies. | closed |
| R2-O5 | pastdue_left, catchup_excess and latest_unpaid are rounded to the cent ("each partial figure is rounded to the cent"). | closed |
| R2-O7 | The rule now reads "net meaning less the payment reversals posted on the agreement in that same window", which matches the compute. | closed |
| R2-O1, R2-O2, O-9, O-1, O-6, O-11, O-12, O-14, O-15 | Unchanged, with the reworker's reasons. | remain observations |

### New-defect scan (revision 3)

- Changed text: the in-flight and catch-up-excess sentences of both notices; both baselines; the rent-in-force and period-charge bindings; the card catch-up eligibility, decline counting, windows and reversal netting; the tow-fee scoping. Each changed sentence was swept against compute and back. No rule tier lacks a compute branch and no compute tier lacks a rule sentence.
- Ladders: card_rent_recollected now has three live tiers. Every other ladder is unchanged in structure from revision 2 (already checked there).
- Prerequisites: the card gate's sentence and condition still say "still declined after its last retry" / "max_retries_per_draft retries used". Widening the card catch-up's eligibility does not widen the gate, and the single write for the gate is still approve_card_catchup_charge_edda4662.
- R3-O1 (observation, new): the card catch-up now admits "a storage unit AutoPay draft on a card … declined for … an expired card" and charges "the same card". The base rule (autopay_evt_expiry_reminders) says a draft on an expired card is declined as declined_expired_card. Without a recorded card update (autopay_method_update), a charge to that card would be declined again. The policy is silent on that, which may be an omission. No seeded world has an expired-card decline.
- R3-O2 (observation, new): before the last retry the card catch-up charges fees only, while the scheduled retry still runs for the original draft amount. The policy does not say whether that retry amount nets the fees already approved. No seeded world triggers it: task 0's card has used all its retries.
- No new SOURCE-POLICY or SOURCE-FACTOR red light was found.

### factor_ladders (revision 3)

| policy | factors | parameter | method | all live |
| --- | --- | --- | --- | --- |
| unit_draft_notice | 5 | rent_in_force, projected_late_fees, projected_lien_fees | noticed_period_charge, past_due_carry | yes |
| unit_ach_catchup | 6 | 5 | in_flight_netting | yes (O-15 noted) |
| unit_card_catchup | 6 | 5 | card_rent_recollected | yes |
| parking_draft_notice | 4 | parking_rent_in_force, projected_parking_late_fee | parking_period_charge, parking_past_due_carry | yes |
| parking_ach_catchup | 6 | 4 | parking_rent_recollected, parking_in_flight_netting | yes |

### closing_checklist (revision 3)

Written after the revision-3 reveal (2026-10-10T21:45Z). Earlier revisions are untouched.

- Per-task files 0.md and 1.md each carry `## revision_3` with a frozen derivation, a comparison and findings. Every comparison is PASS on all four relationships.
- Round-2 reds closed:
  - R2-F1, R2-F2, R2-F3, R2-F4.
  - T0-R2-F1, T0-R2-F2, T1-R2-F1.
  - R2-O3/T1-O1, R2-O4, R2-O5, R2-O6, R2-O7, O-3.
- No new red. New observations are R3-O1 and R3-O2. Remaining observations: R2-O1, R2-O2, O-1, O-6, O-9, O-11, O-12, O-14, O-15.
- Coverage and scope:
  - 5 extended policies and 5 tools are covered.
  - Task 0 = {parking_ach_catchup, unit_card_catchup, parking_draft_notice}; task 1 = {unit_ach_catchup, unit_draft_notice}. The two are disjoint.
  - uuid8s are independent (revision 1, tool module unchanged).
- Trees:
  - Task 0: n=2, 1 value_input, 1 state_gate, 2 owner=user writes.
  - Task 1: n=1, 1 value_input, 1 owner=user write.
  - The difficulty graph is acyclic.
- Factors:
  - Every computation has 4–6 live factors with ≥2 parameter and ≥1 method.
  - Each task has a multi-source factor (rent_in_force, past_due_carry) and cross-difficulty reads (parking/unit), with the seeded rows consistent with their charters.
  - Every factor bears weight. Every baseline is self-sufficient, with a definite fall-back different from gold: 256.50, 112.50, 615.00 (task 0); 350.10, 916.90 (task 1).
- No regression: the scored values are identical to revision 2. The blind derivation equals GT.
- Gates: the coordinator's round-3 snapshot is all green except deferred traceability. The auditor did not re-run them.
- **Difficulty conclusion (revision 3): passes the source-layer audit.** Both tasks are PASS on all four relationships, and the charter carries no open red.

## revision_4

### charter_global_frozen (revision 4)

- Inputs (re-hashed):
  - autopay.extended.yaml sha256=9c073858ee1c14880eef2b50546bd40700274c8ff0d3e55b838eba62c5483568 (changed).
  - task_tools.py sha256=285409c850755b59bc0d5e5f295a199b64511ebef6e4a23640941d77cb1acf21 (changed).
  - Views unchanged (59ba265e… / 12a5ce9b…).
  - Base copy still byte-identical.
  - Copies for later diffs: /tmp/run_0051/audit_autopay_authorization_changes/extended_r4.yaml and task_tools_r4.py.
- Freeze time 2026-10-10T22:54Z. Auditor: erl-task-policy-audit agent.
- Round-4 tasks/*.json were not opened before this section and the per-task freezes were written. The round-3 GT for these unchanged worlds is known (disclosed), and every figure was recomputed.
- I did not read the KB-doc audit files. I judge only the source change the coordinator reports.

### Diff against revision 3 (full `diff` of the charter, done mechanically)

1. **Charter: wording only, compute untouched.** The only changed lines are:
   - in autopay_ext_unit_ach_catchup and autopay_ext_parking_ach_catchup, the in-flight definition sentence in the rule;
   - its `compute_basis` quotations (latest_due, latest_result, in_flight);
   - the two `when` texts of each in-flight_netting ladder.
   - Old: "A regular [parking] draft on the authorization for a later due date whose result is still empty is in flight."
   - New: "The latest submitted [parking] draft on the authorization, the draft attempt with the latest draft date, is in flight when it is for a due date later than the returned [parking] due date and its result is still empty."
   - The compute is unchanged: `latest_* = LATEST(... date_field='draft_date', event_type='autopay_draft')`; `in_flight = latest_amount if (latest_result == '' and latest_due > returned_due) else 0`.
   - The rule now says exactly what the compute reads. The old wording ("a regular draft … for a later due date") admitted an earlier pending draft that was not the latest by draft date. That gap is closed in both directions: rule → compute and compute → rule.
   - The new sentence matches the in-flight definition the notices already used ("the draft attempt on the authorization with the latest draft date"). The only addition is the later-due-date condition, which the notice does not need. Its absence there creates no conflict: a pending re-presentment of the returned due date is netted by the notice, and the parking catch-up then re-collects no rent ("fewer settled draft attempts than one plus max_represents_per_entry"), so the two still agree.
2. **task_tools.py: one docstring sentence.** approve_card_catchup_charge_edda4662 now reads "for a rent due date whose card draft was declined for insufficient funds or an expired card, whether or not its retries are used". This matches the revision-3 card rule's eligibility. The old wording, "still declined after its retries", contradicted it.
   - Name, uuid8, signature (`autopay_id, notice_type, related_due_date, approved_amount`), owner (user), rw and body are unchanged. Checked by AST; the body lines are identical to revision 1.
   - No docstring in the module now contains an ordering word (before / after / first / then / once / until / prior). The tool layer still judges no prerequisite.
3. Mechanical re-checks on the revision-4 charter:
   - policy_source is verbatim on all three edges.
   - compute_basis is verbatim in each rule (no misses).
   - overwrite replaced_by is in each rule.
   - baseline sentences are in each rule.
   - bindings are disjoint.
   - factor counts and labels are unchanged (5/6/6/4/6; ≥2p, ≥1m each).

### Revision-3 RED closure / regression

- Revision 3 closed with no open red. Revision 4 changes no compute, ladder, prerequisite, baseline or seed, so every revision-3 closure stands as it was.
- No new defect: the two changed texts each remove a rule-vs-compute or rule-vs-docstring wording gap and introduce no second reading. The in-flight row in both worlds is the latest-dated draft, for a later due date, with an empty result, so the old and new readings select the same draft there anyway.
- Observations carried unchanged: R3-O1, R3-O2, R2-O1, R2-O2, O-1, O-6, O-9, O-11, O-12, O-14, O-15.

### closing_checklist (revision 4)

Written after the revision-4 reveal (2026-10-10T22:55Z). Earlier revisions are untouched.

- Per-task files carry `## revision_4` (frozen derivation, comparison, findings). Both tasks are PASS on all four relationships, and GT is identical to revision 3.
- Round-3 status: there was no open red. The revision-4 edits are wording only:
  - in the charter, the in-flight sentence in both catch-ups now matches their compute;
  - in the tools, the card docstring now matches the card rule. Name, uuid8, signature, owner and body are unchanged.
  - No compute, ladder, prerequisite, baseline or seed changed, and no new defect was introduced.
- Coverage and scope unchanged: 5 policies and 5 tools covered; task 0 = {parking_ach_catchup, unit_card_catchup, parking_draft_notice}, task 1 = {unit_ach_catchup, unit_draft_notice}; the graph is acyclic.
- Factors unchanged and all bear weight. Fall-backs: 256.50 / 112.50 / 615.00 and 350.10 / 916.90, each ≠ gold.
- Gates: the coordinator's round-4 snapshot is all green, including TRACEABILITY OK and validate_scenario VALID. The auditor did not re-run them.
- **Difficulty conclusion (revision 4): passes the source-layer audit.** Open items are observations only: R3-O1, R3-O2, R2-O1, R2-O2, O-1, O-6, O-9, O-11, O-12, O-14, O-15.
