# Policy-task audit — shopper_payouts_and_cashouts / charter-global

## charter_global_frozen

- Freeze time: 2026-09-25T04:15:27Z (revision 1). Auditor: independent erl-task-policy-audit agent (Claude). I did not write any of the audited artifacts.
- Inputs and hashes (they match the brief):
  - `tasks/shopper_payouts_and_cashouts/payout.extended.yaml` sha256 `02df4d001562a27b820b2d0cdfafcdc77c6b2bfa00628ee311b62290f87ba2f3`
  - `tasks/shopper_payouts_and_cashouts/task_tools.py` sha256 `bf83deb19a8f0d0a9b13f6fe9e87ad428404fe714e3d4e72e0449455ac9c2e4d`
  - `blueprint/blueprint.yaml`, `blueprint/products/payout.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, plus `blueprint/products/batch.yaml` (read only for `weekly_pay_cutoff` and finalization).
- Fields I was allowed to read: the charter (base and extended), the tool contracts and bodies, and the schema. The masked views (`frozen_time`, `user_scenario`, `initial_state`) were used only for the per-task files.
- Fields masked and not read when this section was written: every `tasks/*.json` field other than the three view fields (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`), the instantiator's `worklog.md` in the tasks directory, the scenario `worklog.md`, and every other audit directory. Every search was limited to named files; no recursive search touched `tasks/`.
- This section holds nothing derived from a revealed GT.
- Entry conditions (Step 0): the gate snapshot came with the brief. `check_extended`, `check_task_tools`, `replay_tasks`, `check_solvability`, `check_compute`, `check_grounding` and `check_cross_fire` all returned rc=0. `check_traceability` was deferred because the KB is not yet published. The masked views and their hashes came with the brief, and I re-verified the hashes: `task_0.view.json` 910e7369…, `task_1.view.json` f2aad132…. Input is complete. The deferred traceability gate is noted, not treated as missing input.
- The base section of the extended file is verbatim identical to `blueprint/products/payout.yaml`. I compared the parsed YAML key by key: `category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures` and `policies` are all equal.

### policy_conflict_scan

The charter has 8 extended policies, one tool each, with no shared `(target_tool, computes)`:

| policy | target_tool (owner) | computes | subject | prerequisite |
|---|---|---|---|---|
| payout_ext_returned_resend | resend_returned_transfer_f902fe69 (agent) | resend_usd | weekly_deposit, transfer_returned | [] |
| payout_ext_sweep_catchup | send_catchup_deposit_164755b4 (agent) | amount_usd | weekly_deposit | returned_resend (value_input, state) |
| payout_ext_card_plan_exit | move_off_card_plan_7a80b851 (agent) | settlement_usd | plan_changed, cashback_paid | [] |
| payout_ext_debit_cashout | cash_out_to_debit_card_0246d821 (user) | amount_usd | instant_cashout, fee | card_plan_exit (value_input, state); sweep_catchup (value_input, state) |
| payout_ext_statement_cashback | pay_statement_cashback_5d281cc6 (agent) | amount_usd | cashback_paid | [] |
| payout_ext_closing_cashback | settle_closing_cashback_4e373fbf (agent) | amount_usd | cashback_paid | statement_cashback (value_input, state) |
| payout_ext_card_cashout | cash_out_to_card_075a5c73 (user) | amount_usd | instant_cashout, fee | [] |
| payout_ext_closure_disbursement | close_payout_account_ca79a9a7 (user) | final_disbursement_usd | account_closed, weekly_deposit | card_cashout (value_input, action); closing_cashback (state_gate, action) |

- **Overlapping subjects.**
  - Three tools book `payout_weekly_deposit` rows: re-send, catch-up and final disbursement. They are distinct in business words (a "re-send deposit" pointing to a returned entry, a "catch-up deposit" carrying a period end, a "final disbursement" at closing) and in fields (`source_event_id` against `payout_period_end`).
  - Three tools book `payout_cashback_paid` rows: card-plan exit, statement payment and closing settlement. Their triggers are distinct: a move off the card, a due statement month, and a closing with a month not yet due.
  - Two tools book `payout_instant_cashout` plus a fee row: the debit cashout (plan on record Instant Cashout) and the card cashout (Everyday Pay Card plans). Their plan scopes are disjoint.
  - No two policies decide the same scored quantity in the same situation.
- **Triggers, eligibility, time anchors and terminal states.**
  - Every extended policy inherits the base `status = active` gate: instant cashout I1, plan change, weekly deposit S2, cashback C5 and closure X1.
  - None of them relaxes it.
  - Every "last N months" window is anchored on "the day of" that write. No policy uses another policy's clock.
- **Cross-category read boundaries.** These match `cross_category`: shopper level, violation points, activation and level-evaluation dates, and one-star ratings; batch status, pay components, tips, reversals and tip reductions; membership plan and status. This agrees with the green `check_extended` line ("cross-category reads declared exactly").
- **Scope exclusivity and completeness.** The `prerequisite` graph has exactly two connected components:
  - {debit_cashout, card_plan_exit, sweep_catchup, returned_resend}
  - {closure_disbursement, card_cashout, closing_cashback, statement_cashback}
  - With M=2 and one tree per task, the two trees are pairwise disjoint and together cover all 8 policies. The per-task files confirm from each world which tree the task's root selects.
- **Conflicts found in this scan.** Two statement-order conflicts, F-C2 and F-C3 under **findings**, where one policy's prerequisite sentence and the depended-on policy's own rule reach different conclusions in a situation the charter itself names. No other conflict was found.

### rule_compute_equivalence

I swept each of the 8 policies both ways: every `compute_basis` quotation is found verbatim in the policy's own `rule` (checked by script after whitespace normalisation), and every `compute` binding has a basis. The rule-to-compute sweep, policy by policy:

- **returned_resend.**
  - latest returned entry (`LATEST`) ✓; the amount still to re-send nets earlier re-sends through `source_event_id` ✓.
  - The destination window runs from `destination_changed_at`, or from `opened_date` when never replaced ✓. Whole months since verification ✓.
  - Limit ladder 100/150/whole ✓. Standing multiplier 1.5/1.25/1 with the level and base-pay count conjoined ✓. `drawn = MN(outstanding, limit×mult)` ✓.
  - Set-off window: 3 months when there are ≥2 returns; 1 month when there is exactly 1 return and the shopper is below Diamond (`lvl_rank <= 5`); else 0 ✓.
  - Clawback 20/10/0 ✓; conduct 25/10/0 ✓; `MX(0, …)`, rounded once ✓.
  - `RND(dest_limit * limit_mult, 2)` rounds an intermediate. The rule says "rounded to the cent only on that final figure". The two agree on any limit × multiplier that is a whole cent, which all declared constants are (100/150 × 1.5/1.25). No consequence.
- **sweep_catchup.**
  - The unfinalized batch is `batch.status == completed` ✓. Its credits come from the payout ledger and its tips from `batch_tip_posted` ✓.
  - Leave-behind ladder ✓; returned part ret_remainder, with returns ≥2 → whole, ==1 and ≤Gold → half, else 0 ✓; limit 200/300/whole ✓; tip-reduction buffer 15/7.50/0 ✓; conduct 30/12/0 ✓; `MN(limit, bal) − …`, `MX(0)` ✓.
  - **Mismatch (observation).** `held` (Silver tier: `RND(unfin_tips + (unfin_credits - unfin_tips) / 2, 2)`) and `kept` (`RND(ret_remainder / 2, 2)`) round an intermediate, while the rule says "rounded to the cent only on that final figure". The two differ by one cent whenever the halved figure has an odd cent. The per-task file shows whether a world triggers it (T0 does not: 46.90/2 = 23.45).
- **card_plan_exit.**
  - Latest statement month with earned entries ✓; the three categories ✓; `last_paid` ("unless a payment already carries that month") ✓; `older_unpaid` ✓.
  - Exit cap ladder 60/40/plan cap ✓; category-scope ladder ✓; fuel boost 1.25/1.1/1 and auto boost 1.5/1.2/1, each rounded before the cap (stated) ✓.
  - Share 0.5/0.8/1, running from `plan_changed_date` or `opened_date` (stated) ✓; tenure 0.10/0.05/0 ✓; rounded once ✓.
- **debit_cashout.**
  - Tip hold 0 / half (rounded, stated) / all ✓; fee 0 / half of plan fee (rounded, stated) / plan fee ✓.
  - Return reserve 40/20/0 ✓; debit buffer 15/7.50/0 ✓; conduct 20/8/0 ✓; new-destination hold 50/25/0 ✓.
  - `MN(per-transaction max, daily max − today, bal − … − fee)`, `MX(0)` ✓.
- **statement_cashback.**
  - earned − paid − latest month while waiting (`DAYS(latest_booked, NOW) < cashback_payment_day − 1`) ✓. Member boost 1.1/1.05/1, rounded (stated) ✓.
  - Cap 100/75/plan cap ✓; make-good 5% of the capped figure (rounded, stated) / 2.00 / 0 ✓; tenure kicker 2.50/1.00/0 ✓; long-haul credit 3.00/1.50/0 ✓.
  - **Invented basis (observation).** `last_payment_days` falls back to `F('opened_date')` when no earlier payment exists. The rule ("where the latest earlier cashback payment was made 45 or more days before") says nothing about that case.
- **closing_cashback.**
  - Latest month ✓; "a month that already carries a payment settles nothing" ✓; EV counted 2 / 1.5 / 1 (rounded, stated) ✓; cap at the card plan's cap ✓.
  - Share 1.0/0.75/0.5 ✓; card-tenure bonus 0.05/0.02/0 from `plan_changed_date` or `opened_date` (stated) ✓; thank-you 3.00/1.50/0 and 0 when there is nothing to settle ✓.
- **card_cashout.**
  - Tip release (all / half, rounded, stated / none) ✓; clawback 30/15/0 ✓; conduct 40/15/0 ✓; debit buffer 20/10/0 ✓; new-level reserve 25/10/0 ✓; limits ✓.
  - **Invented basis (observation).** `level_days` falls back to `opened_date` when `level_evaluated_date` is empty, and the rule does not state it.
- **closure_disbursement.**
  - Hold ladder ✓; clawback 40/20/0, conduct 50/20/0, debit 25/12.50/0, rating 20/10/0 ✓; reserve scaling 0.5/0.75/1 ✓; `MX(0, bal − hold − reserves)` ✓.
  - **Mismatch (observation).** `closing_hold` Silver/Gold tier and `reserves = RND((…)*reserve_mult, 2)` round intermediates. The rule says "rounded to the cent only on that final figure".
- **All 8 policies (observation).** The `lvl_rank` binding (level name to ordinal) has no `compute_basis` entry. The rule relies on the charter's shopper ladder ("at … level or above"), which is a legitimate reading, but the binding carries no quotation.
- **Ladder–rule–compute correspondence.** Every tier named in `factors[].ladder` is a sentence of the rule and a branch of the `decides` binding, and vice versa. I found no tier present in one face and absent from the other.

### action_binding_and_uuids

- The 8 `(target_tool, computes)` pairs are distinct, and each tool is claimed by exactly one policy.
- **Tool bodies.** Every tool body is a plain write: it looks up the account, rounds the given figure, creates a row, and updates the balance, cashback balance, variant or status.
  - No body validates status, eligibility, prerequisite, amount or plan.
  - No body returns an error or a hint.
  - The tool layer therefore judges no prerequisite (`task_tools.py`, all 8 bodies).
- **Docstrings.** No docstring names another tool or states a sequence position. The only near-ordering phrases (observations):
  - `settle_closing_cashback_4e373fbf`: "for an account that is being closed". The progressive form hints that the settlement precedes the closure.
  - `close_payout_account_ca79a9a7`: "clears the card cashback balance, since unpaid cashback lapses with the account". This restates the base lapse clause, which `payout_ext_closing_cashback` overrides for the latest undue month. The text stays true of whatever the closing settlement did not pay.
- **uuid8s.** f902fe69, 164755b4, 7a80b851, 0246d821, 5d281cc6, 4e373fbf, 075a5c73, ca79a9a7. All are distinct. None shares a prefix or suffix, and none is sequential or looks batch-derived. PASS.
- **Business reading.** Each tool has only one business reading.
  - Note on `move_off_card_plan_7a80b851`: its `new_variant_name` enum text maps Instant Cashout to "the shopper now receives payouts to an external debit card", which is how the destination kind selects the plan. This is consistent with the rule sentence "The move itself goes to the plan whose payout destination is the kind of destination the shopper now receives payouts to".

### prerequisite_graph

Check 7:

- `prerequisite` is filled everywhere. It is `[]` for returned_resend, card_plan_exit, statement_cashback and card_cashout.
- Every `problem` points at an extended policy id of this file. None points at a base policy or at itself.
- Edges: debit→{card_plan_exit, sweep_catchup}; sweep_catchup→returned_resend; closure→{card_cashout, closing_cashback}; closing_cashback→statement_cashback. **Acyclic.**
- Every `policy_source` is verbatim in its own policy's `rule` (checked by script).
- `form`: `fallback_reason` is present exactly on the two `action` edges (closure→card_cashout and closure→closing_cashback).
- `resolved_by` equals the depended-on policy's `target_tool` on all 6 edges. Each tool body makes the `effect` hold:
  - re-send: a `payout_weekly_deposit` row with `source_event_id`, balance down;
  - catch-up: a deposit row with `payout_period_end`, balance down;
  - move: `variant_name`;
  - statement: a `payout_cashback_paid` row dated today;
  - card cashout: an instant-cashout row, balance down;
  - closing settlement: a `payout_cashback_paid` row.
- `kind`/`gate`: every `value_input` gate names a binding that exists in its policy's compute (`ret_remainder`, `fee`, `bal`, `payments_3m`, `bal`).
  - **Observation.** closure→closing_cashback is declared `kind: state_gate` with `gate: payout_events.statement_month`. That is a field, not an eligibility gate: `payout_ext_closure_disbursement` declares no eligibility entry, and base `payout_evt_closure` has only `not_negative`. `state_gate` does not point at a real gate. No value or terminal consequence, because the edge's weight rests on the closure being withheld until the settlement row exists.
- Mismatches between `condition` and the sentence:
  - sweep_catchup→returned_resend: the sentence says "every returned-transfer entry", the condition says "the latest payout_transfer_returned row". This is **F-C2**.
  - debit→sweep_catchup: the sentence says "while the account was not active", the condition says "while the account was frozen". The sentence is broader (it also covers `pending_verification`). Observation.
  - closure→card_cashout: the sentence adds a quantity ("the account's cashable balance") that the condition ("a payout_instant_cashout row dated the day of closing, booked while the account is on its card plan") does not carry. Observation F-C7.
- **Authoring-viewpoint text (observation).** In debit→card_plan_exit, the `effect` reads "so the fee binding for a Gold shopper with no recent cashout becomes half of that fee instead of half of a card plan's zero fee". That is one tier of one world written into the general text.

### prerequisite_sentences

Check 6, edge by edge:

1. **sweep_catchup ← returned_resend (state).** "A catch-up deposit is fixed only after every returned-transfer entry on the account has a re-send deposit pointing to it."
   - Four-point test: the ordering connective is "only after" ✓; the state is record-visible (a re-send deposit points at the returned entry, i.e. `source_event_id`) in business words ✓; no tool, id or snake_case ✓.
   - **Scope:** the sentence says "every" returned entry, but the depended-on rule says "The re-send answers the latest returned-transfer entry on the account" and the condition says "latest". It is broader than the condition. See **F-C2**.
   - Exactly one write brings the state about: only `resend_returned_transfer` writes a deposit that points to a returned entry ✓.
   - Derivation: the sentence plus a returned entry with no re-send, read against re-send's rule ("once a new destination is on file … and the account is active again, the returned amount is sent again at once … points to the returned-transfer entry it answers"), leads to the re-send write. There is one reading when the account has a single returned entry.
   - The depended-on rule does not restate the sentence ✓.
2. **debit_cashout ← card_plan_exit (state).** "An instant cashout to an external debit card is worked out only after the account's payout plan on record is Instant Cashout."
   - Connective "only after" ✓; state is `variant_name` in plan words ✓; no tool or id ✓.
   - Exactly one write sets `variant_name` to Instant Cashout: `move_off_card_plan`. The shared tools have no plan write (`share_tools.py`: only reads, `verify_customer_identity` and `transfer_to_human_agent`) ✓.
   - Derivation: the card-plan exit rule "When an account moves off the Everyday Pay Card plans to a plan without a card … The move itself goes to the plan whose payout destination is the kind of destination the shopper now receives payouts to" is the only rule that changes the plan. It applies from a card plan. From a non-card plan no write of this charter reaches Instant Cashout, so for the edge to be resolvable the task world must start on a card plan (checked per task).
3. **debit_cashout ← sweep_catchup (state).** "An instant cashout is not worked out until the account carries a catch-up deposit for every weekly deposit day that passed while the account was not active."
   - Connective "not … until" ✓; state is a catch-up deposit on the account ✓; no tool or id ✓.
   - "for every weekly deposit day" could be read as one deposit per day, but the catch-up rule says "a single catch-up deposit … covering every earnings period those days would have swept". This resolves it. Observation.
   - One write: `send_catchup_deposit`. The re-send deposit carries no period end and is a "re-send deposit", not a catch-up ✓.
4. **closing_cashback ← statement_cashback (state).** "The closing cashback settlement is fixed only after every statement month whose payment day has passed carries a cashback payment."
   - Connective "only after" ✓; state is a record-visible cashback payment carrying the month (`statement_month`) ✓.
   - Which write: the statement payment rule "pays … for every statement month whose payment day has come, and it carries the earliest such month". The move-off settlement carries the latest month with earned entries, and the closing settlement carries the latest month whose day has not come. So for a single passed-and-unpaid month, exactly one write (the statement payment) makes it carry a payment ✓.
   - With two or more such months the statement payment carries only the earliest, and no write of the charter can make the later one "carry a cashback payment". See **F-C3**.
5. **closure_disbursement ← card_cashout (action).** "On a card plan, the final card load is fixed only after the shopper has cashed out the account's cashable balance to the Everyday Pay Card that day."
   - Connective "only after" ✓; the action is in business words ✓; no tool or id ✓.
   - `fallback_reason` tested: it claims no record-visible state singles out a card cashout. But a debit cashout is only worked out once the plan on record is Instant Cashout (debit_cashout's own prerequisite sentence). So on an account whose plan on record is an Everyday Pay Card plan, "an instant cashout entry dated the day of closing" can only be a card cashout, and the edge's own `condition` uses exactly that state. **The fallback is unjustified (observation, F-C7).** The state is "the account carries an instant cashout entry dated the day of closing while its plan on record is an Everyday Pay Card plan".
   - The phrase "the account's cashable balance" names a charter measure (`payout_msr_cashable_balance`). The card cashout's own rule computes a different amount. Observation F-C7; T1 gives the figures.
6. **closure_disbursement ← closing_cashback (action).** "A card-plan account is not closed until the closing cashback settlement has been paid onto the card."
   - Connective "not … until" ✓; action in business words ✓.
   - `fallback_reason`: both the closing settlement and the statement payment book a `payout_cashback_paid` row. When the latest month is no longer waiting, a statement payment also covers it (carrying an earlier month). A state such as "the latest month carries a payment" therefore does not single out the closing write cleanly. The fallback is **justified**.

Other checks:

- **No second wording, tool name or problem id** appears in any rule for any edge ✓.
- **Undeclared cross-problem orders in rules.**
  - returned_resend: "Once a new destination is on file after a transfer came back and the account is active again".
  - sweep_catchup: "sent once the account is active again".
  - Both order the write after states brought about by base acts: the shopper's destination change, and the agent's freeze lift (payout_evt_freezes). This difficulty ships no tool for either act and declares no edge for them.
  - They are not orders between two problems of this charter, so they are recorded as observation **F-C8**. The per-task file checks whether both states already hold at the opening. If they do not, the task has no solution.
- **Base rule sentences stating cross-problem order** (for example payout_evt_freezes "transfer_returned is resolved once a new destination has been recorded after frozen_date") ground no edge of this charter ✓.

### override_declarations

Check 1, the findings half. I went sentence by sentence over each `base_policy_refs` entry.

- **returned_resend** (refs payout_evt_weekly_deposit, payout_evt_freezes).
  - freezes, "A returned amount is sent again in the next weekly sweep …": **declared** and replaced.
  - freezes, the other sentences (credit back and freeze; lift only when the cause is resolved; transfer_returned resolved once a new destination is recorded after frozen_date; destination-change count, confirmation and cooldown; fraud-review target): followed, since the re-send rule requires the new destination and active status.
  - weekly_deposit S1–S5 govern the weekly sweep. The re-send is "its own re-send deposit … instead of waiting for the next weekly sweep", which the declared replacement covers. S2 ("only while the account is active") is followed. No undeclared override.
- **sweep_catchup** (refs weekly_deposit).
  - S1 (weekday, balance to the previous cutoff, minimum, carry-over): **declared**.
  - S3 (unfinalized tips stay behind): **declared**, and replaced by "less every credit of the batch that is completed but not yet finalized".
  - S2 (active only; each period swept once): followed, since the catch-up is one deposit covering the missed periods.
  - S4 and S5: arrival timing and sweep applicability, not scored. No undeclared override.
- **card_plan_exit** (refs payout_plan_eligibility, payout_evt_cashback).
  - Cashback C4 (paid on the payment day if at least the minimum) and C2 (monthly cap and cap order): **declared**.
  - C1 (earned per month and category), C3 (refund reversal), C5 ("each month paid once, only while active"), C6 (card spend): followed. The latest month must carry no payment, and older unpaid cashback is added once.
  - Plan eligibility: "allowed only while active, at most plan_changes_per_30d, only to a plan whose min_shopper_level the shopper meets" is inherited and restated ("allowed only while the account is active"). The verification-window and level-following sentences do not govern this quantity. No undeclared override.
- **debit_cashout** (refs payout_evt_instant_cashout, payout_evt_earnings_ledger).
  - I5 (fee, including the first-cashout waiver): **declared**.
  - Ledger tip sentence (tip credits count toward cashable only once finalized): **declared**.
  - I1 (active plans with cashout available) and I3 (new-account hold): inherited.
  - I2 ("at least instant_cashout_min_usd, at most … max_per_transaction and at most payout_msr_cashable_balance; per-day count and daily total"): **not overwritten** for this policy. The per-transaction and daily limits are restated in the rule. The cap "at most payout_msr_cashable_balance" remains in force, and its measure is defined in base `measures` through the very tip clause that was overwritten. Whether it binds is world-dependent. Observation; the per-task file tests it (T0: non-binding).
  - I4 (destination-change cooldown): inherited; the per-task file tests it.
- **statement_cashback** (refs payout_evt_cashback).
  - C2: **declared**. The replacement caps what remains, which may be several months' total, at one cap.
  - C4 (payment day, minimum, carry-over): followed. Months whose day has come are paid, and amounts under 1.00 would still carry.
  - C5 ("each month paid once"): followed in amount (earned − paid), but a multi-month payment carries only the earliest month's label. This underlies F-C3.
  - C1, C3, C6: followed. No undeclared override.
- **closing_cashback** (refs payout_evt_cashback).
  - C5 lapse clause: **declared**.
  - C2 per-month cap at the plan cap: followed.
  - C4 payment-day timing: under base, a month not yet due at a closing never reaches its payment day because C5 lapses it. The declared lapse replacement covers settlement at closing. No undeclared override.
- **card_cashout** (refs instant_cashout, earnings_ledger).
  - I2 first clause (min, max per transaction, cashable cap): **declared**.
  - Ledger tip clause: **declared**.
  - I2 per-day count, I1, I3, I4: inherited. I5: followed ("card plans book its fee entry at 0.00"). No undeclared override.
- **closure_disbursement** (refs payout_evt_closure, weekly_deposit).
  - X1 (agent registers, shopper confirms): **declared**.
  - X3 (disbursement method and time, cashback lapse): **declared**.
  - X2 (negative balance blocks closure) and X4 (frozen accounts closed only by the review team): inherited.
  - Weekly-deposit S1 and S3 govern the sweep, not the final disbursement. No undeclared override.
- **Disguised forms.**
  - No anonymous intermediate factor.
  - No 0/1 multiplier on a base-fixed quantity. `closing_thanks = 0 if month_capped == 0` is stated in the rule.
  - No dropped branch.
  - No author note calls base output a "wrong value".
  - Result: **no undeclared override found in the charter.**
- **Pattern observation.** Each rule contains its `baseline` sentences verbatim together with the factor sentences that modify them. For example, returned_resend says "sent in full … with nothing set off or kept back" and later "debits booked on the account are set off first". Read literally, the two contradict inside one rule. The skill contract requires the baseline sentences to be in the rule, and the later sentences state the adjusted figure explicitly ("The re-send is the amount drawn less the set-off …"), so the merged reading is unique. Observation only.

### factor_ladders

Structure only. Whether each factor bears weight is decided per task.

| policy | factors (effect / cross_difficulty) | declared P / M | honest method after test | multi-source factors (tiers ≥2 conditions on distinct records) |
|---|---|---|---|---|
| returned_resend | new_destination_resend_limit (P/–), resend_limit_standing_multiplier (M/batch), resend_debit_setoff_window (M/–), resend_clawback_reserve (P/batch), resend_conduct_hold (P/shopper) | 3 / 2 | **0** | standing_multiplier (level on the shopper account and base-pay count in batch events). destination_limit's two conditions are fields of the same payout row, so it does not qualify |
| sweep_catchup | unfinalized_batch_leave_behind (M/batch), returned_part_sweep_treatment (M/–), catchup_new_destination_limit (P/–), catchup_tip_reduction_buffer (P/batch), catchup_conduct_buffer (P/shopper) | 3 / 2 | **0** | leave_behind (level and base-pay count); returned_part tier 2 (return count on payout events and level on the shopper account) |
| card_plan_exit | exit_cap_by_level (P/batch), exit_cap_category_scope (M/membership), exit_early_share (P/–), exit_fuel_boost (P/batch), exit_auto_boost (P/batch), exit_tenure_bonus (P/shopper) | 5 / 1 | 1 | exit_cap (level and base pays); early_share (plan_changed_date on the account and cashback payments on payout events) |
| debit_cashout | unfinalized_tip_hold (M/batch), debit_cashout_fee (P/–), cashout_return_reserve (P/–), cashout_debit_buffer (P/–), cashout_conduct_hold (P/shopper), cashout_new_destination_hold (P/–) | 5 / 1 | **0** | tip_hold (level and tip reductions); fee (level and instant cashouts on payout events) |
| statement_cashback | statement_member_booster (P/membership), statement_cap_by_level (P/batch), statement_late_make_good (M/–), statement_tenure_kicker (P/shopper), statement_long_haul_credit (P/batch) | 4 / 1 | 1 | cap (level and base pays); make_good (last payment on payout events and level) |
| closing_cashback | closing_ev_counting (M/membership), closing_share_by_record (P/–), closing_card_tenure_bonus (P/–), closing_thank_you (P/batch) | 3 / 1 | **0** | share (payment count and level) |
| card_cashout | card_tip_release (M/batch), card_clawback_reserve (P/batch), card_conduct_reserve (P/shopper), card_debit_buffer (P/–), card_new_level_reserve (P/shopper) | 4 / 1 | **0** | tip_release (level and tip reductions); new_level (level_evaluated_date and level, both on the shopper account, so not distinct records) |
| closure_disbursement | closing_unfinalized_hold (M/batch), closing_clawback_reserve (P/batch), closing_conduct_reserve (P/shopper), closing_debit_reserve (P/–), closing_rating_reserve (P/shopper), closing_reserve_scaling (M/shopper) | 4 / 2 | **0** | unfinalized_hold (level and base pays); reserve_scaling (activation date and level, same shopper row, so not distinct) |

Structural results:

- **Counts.** Every policy declares 4–6 factors, each ladder has exactly 3 tiers (the fall-through included), and each has ≥2 declared `parameter` and ≥1 declared `method`.
- **Tiers.** Every tier is stated in the rule with its condition and value and implemented in the `decides` binding. Every fall-through tier equals the factor's `baseline` and matches the `baseline.rule`. `decides` is an input, never `result`. The binding sets are disjoint within each policy. Every tier value is a declared `params` constant or a plan parameter (`P(…)`) of the charter.
- **Label honesty fails for 9 of the 11 declared `method` factors (F-C1).** The `compute` expression of each shows its three tiers select one formula with a different scalar:
  - resend_limit_standing_multiplier: `limit_mult` ∈ {1.5, 1.25, 1} multiplies the same `dest_limit`. That is a rate.
  - resend_debit_setoff_window: `SUM(earnings debits within N months)` with N ∈ {3, 1} or empty. That is a window-length threshold substituted into one aggregate.
  - unfinalized_batch_leave_behind: `held = unfin_tips + α·(unfin_credits − unfin_tips)` with α ∈ {0, ½, 1}. The compute writes the middle tier literally as `unfin_tips + (unfin_credits - unfin_tips) / 2`.
  - returned_part_sweep_treatment: `kept = ret_remainder × {1, ½, 0}`.
  - unfinalized_tip_hold: `held_tips = unfin_tips × {0, ½, 1}`.
  - closing_ev_counting: `ev_counted = ev × {2, 1.5, 1}`.
  - card_tip_release: `tips_not_released = unfin_tips × {0, ½, 1}`.
  - closing_unfinalized_hold: `closing_hold = unfin_tips + α·(unfin_credits − unfin_tips)`, α ∈ {0, ½, 1}.
  - closing_reserve_scaling: `reserves = (sum) × {0.5, 0.75, 1}`.
  - The charter itself models the same choice (hold unfinalized tips or not) as a Boolean *parameter*, `tips_cashout_after_finalization` (payout.yaml `parameter_schema`).
  - Only two declared methods change the algorithm:
    - exit_cap_category_scope changes which terms sit inside the `MN(…, cap)`.
    - statement_late_make_good switches between a proportional term (`capped × 0.05`) and a flat 2.00.
  - Result: counting only honest methods, **6 of 8 policies have 0 `method` factors**. The two exceptions are card_plan_exit and statement_cashback.
- **Ladder reality.**
  - **F-C4.** exit_cap_by_level tier values coincide with, or undercut, the fall-through for the plans the charter's own level-following rule assigns. `card_tier_follows_level: true`, and "Card plans … move to the card plan matching the shopper's new level on each level evaluation", with plan caps Blue 25 / Gold 40 / Platinum 60 / Diamond 100.
    - A Platinum-level shopper on Everyday Pay Card Platinum gets 60.00 on tier 1 and 60.00 on the fall-through: two tiers select the same value.
    - A Diamond-level shopper on Card Diamond gets 60.00 on tier 1 against 100.00 on the fall-through.
    - A Gold-level shopper on Card Platinum gets 40.00 on tier 2 against 60.00 on the fall-through.
    - So "busier" shoppers get a lower cap than idle ones. The same holds for statement_cap_by_level tier 1 (Diamond, ≥20 base pays) at 100.00, which equals the Card Diamond cap.
    - These are world-conditional. They bite only when the task's shopper and plan fall into those pairs. The per-task files test this.
  - **Other ladders.** Every fall-through is a treatment the business would plausibly publish. Other tier values are distinct.
  - **Observation F-C9 (not demonstrated as unreal).** Several conditions are ones a payout business rarely weighs for the quantity:
    - violation-point "conduct" holds on re-sends, catch-ups, cashouts and closure;
    - a one-star-rating reserve on the final disbursement;
    - a grocery membership doubling EV-charging cashback at closing;
    - a Cartwise+ membership re-scoping the card-exit cap.
- **Counts over each tree** (the task files confirm per world):
  - Tree {debit, exit, catch-up, re-send}: multi-source factors present (debit fee, exit cap, early share, standing multiplier, leave-behind). cross_difficulty factors read batch, shopper and membership.
  - Tree {closure, card cashout, closing, statement}: multi-source present (statement cap, make-good, closing share, card tip release, closure hold). cross_difficulty reads batch, shopper and membership.

### findings

**F-C1 — SOURCE-FACTOR RED (charter structure; bears on task 0 and task 1).**

- **Symptom:** 9 of 11 factors labelled `method` only substitute a scalar into one fixed formula.
- **Root cause:** ladders written as "all / half / none", "×1.5 / ×1.25 / ×1" or "window 3m / 1m / none" were labelled `method`.
- **Evidence:** the `compute` expressions quoted under factor_ladders (extended yaml lines 1045, 1050, 1262, 1267, 1751, 2189, 2362, 2590 and 2600). The charter itself models the same choice as a Boolean parameter, `tips_cashout_after_finalization`.
- **Demonstrated consequence:** after the label test, returned_resend, sweep_catchup, debit_cashout, closing_cashback, card_cashout and closure_disbursement each have 0 honest `method` factors, below the floor of 1 per computation.
- **Affected:** `payout.extended.yaml` → `extended_policies[*].factors[*].effect` of the nine factors, and the ladders' `method:` texts.
- **Task bearing:** task 0 (returned_resend, sweep_catchup, debit_cashout) and task 1 (card_cashout, closing_cashback, closure_disbursement).

**F-C2 — SOURCE-POLICY RED (charter; bears on task 0, no value consequence in its world).**

- **Symptom:** the sweep_catchup prerequisite sentence is broader than both the depended-on rule and the edge condition.
- **Evidence:**
  - sweep_catchup rule: "A catch-up deposit is fixed only after every returned-transfer entry on the account has a re-send deposit pointing to it."
  - returned_resend rule: "The re-send answers the latest returned-transfer entry on the account, and the amount still to re-send is that entry's amount less every re-send deposit already pointing to it."
  - The condition: "The latest payout_transfer_returned row of the account has at least one payout_weekly_deposit row whose source_event_id is that row's id."
  - sweep_catchup's own ladder names a world with more than one return: "an account with two or more returned-transfer entries in the last 12 months keeps that whole part on the balance for a later re-send".
- **Demonstrated consequence:** take an account with two returned entries, the older one with no re-send. The catch-up sentence withholds the catch-up until the older entry has a re-send. The re-send rule only ever answers the latest entry, so no write of the charter produces one. The catch-up is never fixed (no solution), while the declared condition, after one re-send of the latest entry, says it is resolved.
- **Affected:** `payout_ext_sweep_catchup.rule` and `.prerequisite[0].policy_source`/`condition`; `payout_ext_returned_resend.rule`.

**F-C3 — SOURCE-POLICY RED (charter; bears on task 1, no value consequence in its world).**

- **Symptom:** a multi-month statement payment carries only the earliest month, while the closing prerequisite requires every passed month to carry a payment.
- **Evidence:**
  - statement_cashback rule: "A statement payment pays onto the card the cashback earned and not yet paid for every statement month whose payment day has come, and it carries the earliest such month."
  - closing_cashback rule: "The closing cashback settlement is fixed only after every statement month whose payment day has passed carries a cashback payment."
  - The tool books one row with one `statement_month` (`pay_statement_cashback_5d281cc6`).
- **Demonstrated consequence:** take a card account at closing with two passed, unpaid months M1 < M2. The statement payment pays both under M1. M2 then carries no payment. A second statement payment computes earned − paid = 0 and has nothing to pay; the closing settlement carries the latest undue month; the move-off carries the latest earned month. The closing settlement is never fixed, so the closure (withheld "until the closing cashback settlement has been paid") has no solution. Read by amount, the statement rule says M2 is paid.
- **Affected:** `payout_ext_statement_cashback.rule`, `payout_ext_closing_cashback.rule` and `.prerequisite[0]`.

**F-C4 — observation (world-conditional SOURCE-FACTOR shape).**

- The exit_cap_by_level and statement_cap_by_level tier values equal or undercut the fall-through plan cap for level/plan pairs the level-following rule produces. Figures are under factor_ladders.
- Task 0 (Gold shopper on Card Blue: 40 against 25) and task 1 (Platinum shopper on Card Platinum under statement tier 2: 75 against 60) do not sit on a colliding pair. The per-task files confirm this.

**F-C5 — observation (check 2).**

- Intermediate roundings contradict "rounded to the cent only on that final figure": sweep_catchup `held` (Silver tier) and `kept`, and closure `closing_hold` (Silver/Gold tier) and `reserves`.
- Invented fall-backs: statement `last_payment_days`, and card cashout `level_days`, fall back to `opened_date`.
- `lvl_rank` has no basis quotation.
- The per-task files show no consequence in either world.

**F-C6 — observation (check 6/7).**

- The debit←catch-up sentence says "not active", the condition says "frozen".
- "for every weekly deposit day" against a single catch-up deposit.
- The closure→closing_cashback `state_gate` points at a field, not a gate.
- The debit←exit `effect` carries tier- and world-specific wording.

**F-C7 — observation (check 6).**

- The closure←card_cashout action-form fallback is unjustified. The singling-out state is: an instant cashout entry dated the closing day while the plan on record is an Everyday Pay Card plan.
- The sentence's phrase "the account's cashable balance" names the charter measure `payout_msr_cashable_balance`, which is not the amount the card cashout rule computes. The task 1 file quantifies the alternative reading.

**F-C8 — observation (undeclared order to base acts with no tool).**

- The returned_resend and sweep_catchup rules gate on "a new destination … on file" and "the account is active again".
- Both are brought about by base acts (the shopper's destination change and the agent's freeze lift) for which this difficulty has no tool and declares no edge.
- The per-task file checks that both hold at the opening.

**F-C9 — observation (ladder realism).** The violation-point conduct holds, the rating reserve, the membership-driven EV doubling and the cap re-scoping are unusual for a payout business. They are not demonstrated as unreal.

**F-C10 — observation (docstrings).**

- `settle_closing_cashback`: "for an account that is being closed".
- `close_payout_account`: "since unpaid cashback lapses with the account".

## closing_checklist

Written after both reveals (first reveal 2026-09-25T04:20:47Z). Everything above this heading was written at 04:17:42Z, before any reveal.

**Status: the difficulty is NOT closed.** Both tasks carry SOURCE-FACTOR RED (F-C1), so the Step 4 close-out does not apply. Here is where each item stands:

- **Files.** The per-task files `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, with this file alongside them. This is revision 1, so there are no older revisions. Each comparison section carries a verdict, and neither is PASS on all four relationships.
- **Scopes.**
  - GT `charter_scope` of task 0 is {card_plan_exit, returned_resend, sweep_catchup, debit_cashout}.
  - Task 1's is {statement_cashback, closing_cashback, card_cashout, closure_disbursement}.
  - They are pairwise disjoint, cover all 8 extended policies, and equal the two components of the prerequisite graph.
  - Task tools and GT are closed. Each tool's uuid8 is independent: PASS.
- **Trees.** Each has 3 prerequisite problems.
  - Task 0: 3 value_input edges; the owner=user write is the debit cashout.
  - Task 1: 2 value_input edges and 1 state_gate; the owner=user writes are the card cashout and the closure.
  - Both trees are acyclic, and the difficulty-wide graph is acyclic.
  - Every edge is unmet at the opening and bears weight: PASS.
- **Factors.**
  - Every computation declares 4–6 factors with 3-tier ladders stated in full in its rule. Each has an honest baseline that alone gives a definite figure different from gold, and every factor bears weight on its world: PASS.
  - **But the honest `method` count is 0 for 6 of 8 computations (F-C1): FAIL.**
  - Ladder-realism observations (F-C4, F-C9) are open. They do not bite in these two worlds.
- **Policy.**
  - F-C2 (the "every" returned entry against the latest) and F-C3 (the multi-month statement payment against "every passed month carries a payment") are charter-level SOURCE-POLICY REDs. Neither has a value consequence in the two current worlds.
  - Observations F-C5 to F-C8 and F-C10 are open.
- **Gates.** The instantiation-stage gates were not re-run on a final form: no final form exists, since this audit edits nothing. The snapshot supplied with the brief was all green, with `check_traceability` deferred.

Per-task verdicts:

| task | SOURCE-POLICY | SOURCE-CHAIN | SOURCE-FACTOR | SOURCE-TASK |
|---|---|---|---|---|
| 0 | PASS on its world (charter RED F-C2 cited, no consequence) | PASS | **RED** (F-C1) | PASS (derivation equals GT on all four writes) |
| 1 | PASS on its world (charter RED F-C3 cited, no consequence) | PASS | **RED** (F-C1) | PASS (derivation equals GT on all four writes) |

## revision_2

### charter_global_frozen (revision 2)

- Written 2026-09-25 at about 04:38Z, before any round-2 reveal. Auditor: the same independent auditor as round 1.
- Inputs:
  - `payout.extended.yaml` sha256 6aefbb7e61698e387fd109eb03e7e4ccd1acb4e99eebaa356d5aca375bd2b1d9 (changed);
  - `task_tools.py` sha256 10c084aec459e1db58b0604ac31d3dbfc6bccbb4c047e69dc21c4a63a5ff058f (changed);
  - `blueprint/products/payout.yaml` 4110b2d8… (unchanged; the base copy in the extended file is still verbatim identical in all 10 top-level keys).
- Both shared inputs changed, so every charter-global section is **re-derived in full**. None is carried forward.
- Masked and unread at this point: `tasks/0.json`, `tasks/1.json` (except the view fields) and both worklogs. The round-1 text above is untouched.
- Entry conditions:
  - The round-2 gate snapshot came with the brief: all 7 rc=0, `check_traceability` deferred.
  - Views r2: `task_0.view.json` 6d929f9b…, `task_1.view.json` bf51da8e…. I re-verified both hashes.
  - Input complete.

### policy_conflict_scan (revision 2)

- The structure is unchanged: 8 extended policies, 8 tools with owners unchanged, and the same 6 prerequisite edges forming the same two components. Scopes are pairwise disjoint and together complete.
- Two edges changed:
  - closure→card_cashout is now **state** form: "On a card plan, the final card load is fixed only after the account carries an instant cashout dated the day of closing."
  - closing→statement now reads: "The closing cashback settlement is fixed only after the cashback payments on the account cover all the cashback earned in statement months whose payment day has passed."
- Overlapping subjects and the inherited `active` gates are unchanged. The re-send, catch-up and final-disbursement rows are still distinct by business words and fields.
- **New conflict:** F-R2-1 (below).

### rule_compute_equivalence (revision 2)

- The two-way sweep was re-run by script:
  - every `compute_basis` quotation is verbatim in its rule;
  - no binding lacks a basis (`lvl_rank` now quotes the new level-order sentence "Shopper levels rank upward in the order …");
  - every `K()` is declared and used;
  - every `decides` is a compute binding.
- Round-1 mismatches:
  - The intermediate roundings are now stated in the rules:
    - returned_resend: "the scaled limit being rounded to the cent";
    - sweep_catchup: `held` "the sum rounded to the cent", `kept` "rounded to the cent";
    - closure: `closing_hold` "the sum rounded to the cent", `reserves` "the scaled sum is rounded to the cent";
    - exit and statement caps: "a raised cap is rounded to the cent";
    - debit `new_dest_hold`, "rounded to the cent";
    - closing thank-you, "rounded to the cent".
  - The fallbacks are now stated:
    - statement: "the days being counted from the account's opening date when it has no earlier cashback payment";
    - card cashout: "(or, when the contractor account carries none, the payout account's opening)".
  - **F-C5 closed.**
- Each changed or added tier appears in both the rule and its `decides` binding:
  - re-send `setoff` uses `MAX` / `LATEST` of earnings debits;
  - catch-up `dep_limit` uses `MAX` weekly deposit / `K('catchup_limit_recent')` / `bal`, with the tier order swapped consistently in rule and compute;
  - debit `new_dest_hold` is `RND(bal × 0.1)` / 50.00 / 0;
  - closing `closing_thanks` is `RND(shared × 0.05)` / 1.50 / 0;
  - card `debit_buffer` uses `MAX` earnings debit when there are ≥2 debits in 3 months (the threshold changed from 3 to 2), 10.00 when exactly 1, else 0;
  - closure `closing_clawback` uses `XMAX` reversal when there are ≥2 in 12 months, 20.00 when exactly 1, else 0.

### action_binding_and_uuids (revision 2)

- The 8 `(target_tool, computes)` pairs and uuid8s are unchanged and distinct.
- No function body contains a conditional, error or hint. A grep for `if`/`raise`/`Error`/`else` over `task_tools.py` returns nothing.
- Docstrings:
  - `settle_closing_cashback_4e373fbf` now reads "for a card-plan payout account"; the progressive "being closed" is gone.
  - `close_payout_account_ca79a9a7` now "sets the card cashback balance shown on the closed account to 0.00", without restating the lapse clause.
  - No docstring carries an ordering word or another tool's name. **F-C10 closed.**

### prerequisite_graph (revision 2)

- The graph is acyclic with the same edges. Every `policy_source` is verbatim in its own rule. Every value_input gate is a compute binding.
- `fallback_reason` is now present only on closure→closing_cashback, the one remaining action edge ✓.
- Conditions against sentences:
  - sweep_catchup→returned_resend: the sentence now reads "the latest returned-transfer entry", matching the condition and the re-send rule.
  - debit→sweep_catchup: the sentence reads "covering the weekly deposit days that passed while the account was not active", and the condition says "not active" ✓.
  - The debit→card_plan_exit `effect` is now generic ✓.
- **Still open (observation):** closure→closing_cashback is `state_gate` with `gate: payout_accounts.cashback_balance_usd`. That is a field, not an eligibility gate of the policy, which still declares none. The field was replaced but the defect has the same shape. **The F-C6 gate item is not closed.** No value consequence.

### prerequisite_sentences (revision 2)

1. **sweep_catchup ← returned_resend (state).** "A catch-up deposit is fixed only after the latest returned-transfer entry on the account has a re-send deposit pointing to it."
   - Four-point test ✓. One write brings the state about (the re-send) ✓.
   - The scope now equals the condition and the re-send rule ("The re-send answers the latest returned-transfer entry"). With two or more returns, the catch-up's own tier ("keeps that whole part on the balance for a later re-send") is consistent. **F-C2 closed.**
2. **debit ← card_plan_exit (state).** Unchanged ✓.
3. **debit ← sweep_catchup (state).** Reworded ✓ ("covering the weekly deposit days"), which agrees with "a single catch-up deposit".
4. **closing ← statement (state).** "…fixed only after the cashback payments on the account cover all the cashback earned in statement months whose payment day has passed."
   - The multi-month labelling problem of F-C3 is gone, because the test is now by amount, not by `statement_month` label. **F-C3 closed as stated.**
   - The amount-based wording opens **F-C2-shaped F-R2-1** (below).
5. **closure ← card_cashout (state).** "On a card plan, the final card load is fixed only after the account carries an instant cashout dated the day of closing."
   - Four-point test ✓. Exactly one write can bring it about on a card plan: the debit cashout requires the plan on record to be Instant Cashout.
   - The quantity phrase "the account's cashable balance" is gone. **F-C7 closed.**
6. **closure ← closing_cashback (action).** Unchanged. The fallback is still justified.

Other checks:

- No rule carries a second wording, a tool name or a problem id.
- F-C8: the re-send and catch-up rules still gate on "a new destination is on file" and "the account is active again", which are base acts with no tool in this difficulty. **Unchanged, and still an observation.** The claim "recorded in proofs" concerns GT prose and is checked at reveal.

### override_declarations (revision 2)

- The sentence-by-sentence sweep was re-run against each `base_policy_refs`. The overwrites and base refs are unchanged, and the new tiers stay inside already-declared replacements:
  - re-send set-off;
  - catch-up limit;
  - debit hold;
  - exit and statement cap multipliers, which sit inside the declared C2 replacements whose `replaced_by` text was updated to match;
  - closing thank-you;
  - card debit buffer;
  - closure clawback.
- **No undeclared override.**
- One interaction is relevant to F-R2-1: base payout_evt_cashback C5, "Each statement month is paid once", remains inherited by statement_cashback, whose only overwrite is C2.

### factor_ladders (revision 2)

| policy | factors (effect) | P / M after label test | new method factor honest? |
|---|---|---|---|
| returned_resend | dest limit (P), standing multiplier (P, relabelled), **setoff choice (M)**, clawback (P), conduct (P) | 4 / 1 | yes: `MAX(debits ever)` against `LATEST(debit)` against none selects a different aggregate, not a scalar |
| sweep_catchup | leave-behind (P, relabelled), returned part (P, relabelled), **new-destination limit (M)**, tip buffer (P), conduct (P) | 4 / 1 | yes: `MAX(weekly deposit ever)` against a constant 200.00 against no limit; the limit is computed by a different rule |
| card_plan_exit | exit cap (P, now 1.5× / 1.25× / 1× plan cap), category scope (M), share (P), fuel (P), auto (P), tenure (P) | 5 / 1 | unchanged ✓ |
| debit_cashout | tip hold (P, relabelled), fee (P), return reserve (P), debit buffer (P), conduct (P), **new-destination hold (M)** | 5 / 1 | yes: `bal × 0.10` against a flat 50.00 against 0 (proportional against flat) |
| statement_cashback | booster (P), cap (P, now 1.5× / 1.25× / 1× plan cap), make-good (M), tenure (P), long-haul (P) | 4 / 1 | unchanged ✓ |
| closing_cashback | EV counting (P, relabelled), share (P), card tenure (P), **thank-you (M)** | 3 / 1 | yes: `shared × 0.05` against a flat 1.50 against 0 |
| card_cashout | tip release (P, relabelled), clawback (P), conduct (P), **debit buffer (M)**, new-level (P) | 4 / 1 | yes: `MAX(debit ever)` against a flat 10.00 against 0 |
| closure_disbursement | hold (P, relabelled), **clawback (M)**, conduct (P), debit (P), rating (P), scaling (P, relabelled) | 5 / 1 | yes: `XMAX(reversal)` against a flat 20.00 against 0 |

- **Counts and labels.**
  - Every policy has 4–6 factors, ≥2 honest `parameter` and ≥1 honest `method`.
  - Every relabelled factor is now honestly `parameter` (a scalar coefficient).
  - All ladders have 3 tiers, stated in the rule and in compute, with the fall-through equal to the baseline.
  - **F-C1 closed structurally.** Weight is checked per task.
- **F-C4.**
  - The exit cap and the statement cap are now a multiple of the plan's own cap (1.5 / 1.25 / 1). The tiers can never coincide with or undercut the fall-through for any plan.
  - **F-C4 closed.**
- **Realism of the new method tiers.**
  - Two new tiers take the "largest … ever booked" entry: the largest earnings debit for the set-off and the card debit buffer, and the largest weekly deposit for the catch-up. The rules read these without a window. This is plausible as a worst-case hold, but "largest weekly deposit" reads a row family that also stores re-send deposits and the final disbursement (all `payout_weekly_deposit`).
  - A tier is world-conditionally ambiguous whenever a re-send or a returned deposit is the largest. The per-task files check this.
  - Tier-value coincidence is possible when the largest debit equals a flat value (for example the card buffer's 10.00). It is world-conditional.
  - **F-C9 (conduct holds, rating reserve, EV doubling):** kept, observation.

### findings (revision 2)

**Per-item status of the round-1 findings:**

| item | status | evidence |
|---|---|---|
| F-C1 SOURCE-FACTOR RED | **closed** (charter) | relabels plus one honest method per policy (table above); per-task weight in `0.md` and `1.md` rev 2 |
| F-C2 SOURCE-POLICY RED | **closed** | sentence now "the latest returned-transfer entry" |
| F-C3 SOURCE-POLICY RED | **closed as stated**, but see new F-R2-1 | the label test was replaced by an amount test |
| F-C4 obs | closed | cap tiers are multiples of the plan cap |
| F-C5 obs | closed | roundings and fallbacks stated; `lvl_rank` basis added |
| F-C6 obs | **partly**: wording items closed; the `state_gate` still points at a field (`payout_accounts.cashback_balance_usd`) | prerequisite_graph above |
| F-C7 obs | closed | state form; quantity phrase removed |
| F-C8 obs | open (unchanged in charter) | rules unchanged |
| F-C9 obs | open (kept) | — |
| F-C10 obs | closed | docstrings reworded |

**New: F-R2-1 — SOURCE-POLICY RED (charter; bears on task 1, no value consequence in its world).**

- **Symptom:** the closing settlement's new prerequisite state can be made unreachable by the statement payment's own cap.
- **Evidence:**
  - closing_cashback rule: "The closing cashback settlement is fixed only after the cashback payments on the account cover all the cashback earned in statement months whose payment day has passed."
  - statement_cashback rule: "caps what remains at the monthly cashback cap of the card plan", with the cap ladder at most 1.5× the plan cap.
  - Inherited base C5 (not overwritten by statement_cashback): "Each statement month is paid once".
- **Demonstrated consequence.** Take a card account at closing whose passed, unpaid month earned more than the one statement payment carries after capping. Task 1's own month 2026-08 is such a month: it earned 71.40 against Card Platinum's cap of 60.00. The statement payment is then below the earned amount, and "cover all" stays false.
  - A second statement payment would carry the same month again, which base C5 forbids.
  - No other write (closing settlement, move-off) books a payment toward a passed month's earning.
  - The closing settlement is never fixed, so the closure has no solution.
  - With task 1's figures on the statement cap's fall-through tier (cap 60.00): payment = 60.00 + 3.00 + 2.50 + 1.50 = 67.00, and payments total 65.50 + 67.00 = 132.50 < 136.90 earned in the passed months.
  - The amount wording therefore reaches a different conclusion ("not covered, wait") from the statement rule ("that month is paid").
  - On task 1's scored path (cap tier 2 = 75.00, payment 82.75) the payments total 148.25 ≥ 136.90, so there is no consequence for its gold.
- **Affected:** `payout_ext_closing_cashback.rule` and `.prerequisite[0].policy_source`/`condition`; `payout_ext_statement_cashback.rule` (cap, no statement of what happens to the capped-off excess).

**New: F-R2-2 — observation.** The "largest … ever booked" tiers carry no window, and "weekly deposit" in the catch-up limit reads a row family shared with re-send and final deposits. This is world-conditional. It is checked per task (task 0: the largest is a genuine sweep of 226.10, above both the 208.00 returned deposit and the re-send).

### closing_checklist (revision 2)

Written after the round-2 reveals (04:39:47Z). Everything above in revision_2 was frozen at 04:38:41Z.

- **Per-task verdicts:**
  - Task 0: PASS on all four relationships.
  - Task 1: PASS on all four relationships.
  - GT equals my independent derivation on every write, every scored figure and every factor figure.
- **Files:** `0.md` and `1.md` carry revision_2 below the untouched round-1 text, and this file sits alongside them.
- **Scopes:** disjoint and complete (the GT `charter_scope` equals the two graph components). The uuid8s are independent and frozen.
- **Trees:** each has 3 prerequisites, ≥2 value_input edges and an owner=user write. The graph is acyclic difficulty-wide. Every edge is unmet at the opening and bears weight.
- **Factors:** every computation has 4–6 factors with ≥2 honest parameter and ≥1 honest method factors. Every factor bears weight against an honest baseline, and each baseline alone gives a figure different from gold.
- **Difficulty status: NOT closed**, because of a charter-level policy defect: **F-R2-1 (SOURCE-POLICY RED).** The closing prerequisite requires payments that "cover all the cashback earned in statement months whose payment day has passed", while the statement payment is capped and base C5 forbids paying a month twice. The prerequisite is unreachable whenever the capped statement payment falls short. Neither current world has a value consequence.
- **Open observations:** F-C6 (the state_gate field), F-C8, F-C9, F-R2-2, and the task-1 finalization timing.
- **Gates:** not re-run by me (the audit edits nothing). The orchestrator's round-2 snapshot shows 7/7 green, with `check_traceability` deferred.

## revision_3

### charter_global_frozen (revision 3)

- Written at about 04:47Z, before any round-3 reveal.
- Inputs:
  - `payout.extended.yaml` sha256 0024ab6a1f12f6b68e1f309ecbfec46a52c637e6082e57a5a3e1d224361e3a0b (**changed**);
  - `task_tools.py` 10c084ae… (**unchanged** from revision 2);
  - `blueprint/products/payout.yaml` 4110b2d8… (unchanged; the base copy is still verbatim identical).
- Views r3: `task_0` 9e9505bd…, `task_1` 7e9c3b33…. I re-verified both hashes.
- The gate snapshot (7/7 rc=0, traceability deferred) came with the brief.
- The charter changed, so the charter sections are re-derived. The tool module did not, so **action_binding_and_uuids is carried forward from revision_2 by reference** (tools hash 10c084ae… equal in both rounds).
- The round-1 and round-2 texts are untouched.

**What changed.** I compared every policy's rule, factors and edges against revision 2 and checked the two views against my round-2 view files.

- `payout_ext_statement_cashback` rule and baseline:
  - it now says "carries the **latest** such month";
  - it adds "whatever the cap leaves unpaid of those months lapses with the payment".
- `payout_ext_closing_cashback` prerequisite sentence and condition now read: "fixed only after the latest statement month whose payment day has passed carries a cashback payment".
- `payout_ext_sweep_catchup` limit wording now reads "largest single weekly sweep deposit … re-send deposits (those pointing to a returned-transfer entry) not counted", and the compute filter is now `source_event_id=None`.
- The other 5 policies are unchanged in rule, factors and edges.
- Seed: only `accepted_at` and `shopping_started_at` of the near-miss finalized batch moved in each world (T0 3fd282c8 to 08:05; T1 5cbab988 to 08:05). The persona and `frozen_time` are unchanged.

### re-derived sections (revision 3)

- **Script re-sweep over all 8 policies:**
  - every basis quotation is in its rule, with no missing basis;
  - every `K()` is declared and used;
  - every baseline sentence is in its rule;
  - every `replaced_by` is in its rule;
  - every `policy_source` is verbatim in its own rule.
- **Graph:** unchanged and acyclic.
- **Factor ladders** are as in revision 2 and pass. Each policy has 4–6 factors, ≥2 honest parameter and 1 honest method. The catch-up method now excludes re-sends explicitly.
- **Prerequisite sentence 4 (closing ← statement, state).**
  - It passes the four-point test, and its scope equals the condition.
  - Exactly one write makes "the latest passed month carries a cashback payment" true: the statement payment, which "carries the latest such month". The closing settlement carries the latest *undue* month, and the move-off is not in the closing tree.
  - A multi-month or capped statement payment now satisfies the state in one write.
  - **F-R2-1 closed.**
- **F-R2-2.** Re-sends are excluded. Returned sweep deposits still count, which is a reading the rule states ("every weekly sweep deposit … ever booked"). **Closed.**
- **Override sweep.**
  - The new lapse clause concerns the capped-off part of a statement payment. Base C2 caps a month's total, so an unpaid excess over the cap is consistent with base. No base sentence says the excess carries (C4's carry-over is for amounts under the minimum).
  - **No undeclared override.**

### findings (revision 3)

| item | status | evidence |
|---|---|---|
| F-R2-1 SOURCE-POLICY RED | **closed** | closing sentence and statement label now both "latest"; one write makes the state true in every multi-month or capped case |
| F-R2-2 obs | **closed** | re-send deposits excluded in rule and compute |
| F-C6 obs (`state_gate` points at `payout_accounts.cashback_balance_usd`) | **not closed** (kept as observation) | unchanged |
| F-C8 obs | not closed (kept) | unchanged |
| F-C9 obs | not closed (kept) | unchanged |
| earlier items F-C1…F-C5, F-C7, F-C10 | still closed, no regression | re-sweep above |

**New: F-R3-1 — SOURCE-POLICY RED (charter, latent; no consequence in either task world).**

- **Symptom:** the new lapse clause has no record behind it, and another rule reads the lapsed amount as still unpaid.
- **Evidence:**
  - Statement rule: "whatever the cap leaves unpaid of those months lapses with the payment".
  - No compute binding and no write implements the lapse. `pay_statement_cashback_5d281cc6` books only the paid amount and lowers `cashback_balance_usd` by that amount only.
  - The statement's own compute (`due_total = earned_all − paid_all − waiting`) and card_plan_exit's rule "adds any older earned cashback that no payment has carried" (`older_unpaid = earned_all − latest − paid_all + last_paid`) both read the lapsed part as still earned and unpaid.
- **Demonstrated consequence.** Use task 1's figures with the statement cap on its fall-through tier:
  - The payment is 67.00, and the cap leaves 18.54 of the boosted 78.54 unpaid, which the statement rule says has lapsed.
  - If that account later moved off the card, the exit rule's older earned cashback that no payment carried is 190.50 − 53.60 − 132.50 + 0 = 4.40, added to the settlement.
  - The statement rule says that money is gone. Its own compute would also re-pay it at the next statement payment.
  - So two rules of the charter reach different conclusions on the same world.
- **Bearing on the tasks:** none. Task 0's past months were paid in full with no capped payment. In task 1 the capped 75.00 covers the months' 71.40, so nothing of the months lapses, and no later write in task 1's tree reads unpaid older cashback.
- **Affected:** `payout_ext_statement_cashback.rule` and `baseline.rule` (the lapse clause), against `payout_ext_card_plan_exit.rule` (older unpaid) and the statement's own compute.

**Charter verdict (revision 3):** one latent charter SOURCE-POLICY RED (F-R3-1). Everything else passes or is an observation.

### closing_checklist (revision 3)

Written after the round-3 reveal (04:45:22Z).

- **Per-task verdicts:** task 0 PASS and task 1 PASS on all four relationships. GT equals my derivation on every write and on every factor and baseline figure.
- **Scopes:** disjoint and complete.
- **Uuid8s:** unchanged and independent.
- **Trees:** each has 3 prerequisites, ≥2 value_input edges and an owner=user write. The graph is acyclic.
- **Factors:** every computation has 4–6 factors, ≥2 honest parameter and ≥1 honest method, and every factor bears weight.
- **Charter verdict: NOT closed.**
  - F-R3-1 (SOURCE-POLICY RED, latent): the new statement lapse clause is recorded by no write. The statement compute and card_plan_exit's "older earned cashback that no payment has carried" still read the lapsed amount as unpaid. There is no consequence in either current task world.
  - Open observations: F-C6 (state_gate points at a field), F-C8 and F-C9.
- **Gates:** not re-run by me. The orchestrator's round-3 snapshot shows 7/7 green, with traceability deferred.

## revision_4

### charter_global_frozen (revision 4)

- Written at about 04:55Z, before any round-4 reveal.
- Inputs:
  - `payout.extended.yaml` sha256 f0b60f52c55efe8a297b28c52a5159b8616d97f2e85f2cc1fc17a22f976cace2 (**changed**);
  - `task_tools.py` 10c084ae… (**unchanged**);
  - views r4 identical to r3 (9e9505bd… and 7e9c3b33…, re-verified);
  - `payout.yaml` unchanged (the base copy is still verbatim).
- The gate snapshot (7/7 green, traceability deferred) came with the brief.
- **Carried forward by reference** (the tool hash is unchanged): action_binding_and_uuids, including that no tool body judges anything.

**What changed.** Only three policies changed; the other five are unchanged in rule length, factors and edges.

- `payout_ext_statement_cashback`:
  - the lapse clause is gone;
  - "the card's cashback still to be paid" is now defined as the card cashback balance shown on the account, capped by earned − paid and floored at 0;
  - the capped-off excess "stays in that balance and falls due on the next payment day";
  - a minimum-payment test was added ("owed only when the cashback due, before any booster …, is at least the card plan's minimum"; baseline params add `cashback_min_payment_usd`);
  - compute adds `cash_bal`, `owed`, and `result … if owed else 0`.
- `payout_ext_card_plan_exit`: "older cashback" now reads the same balance (`older_unpaid = MX(0, cash_bal − latest month if unpaid)`).
- `payout_ext_closing_cashback`: the edge to statement_cashback is now **action form**. "The closing cashback settlement is fixed only after the statement payment owed for the months whose payment day has passed, where one is owed, has been made," with a `fallback_reason`.

### re-derived checks (revision 4)

- **Script re-sweep over all 8 policies:**
  - every basis quotation is in its rule, with none missing;
  - `K()` is declared and used;
  - baseline sentences are in the rule;
  - `replaced_by` is in the rule;
  - every `policy_source` is verbatim.
- **Graph:** acyclic. The edges are unchanged, apart from the closing edge's form.
- **The redefined quantity against the tool bodies** (`task_tools.py` unchanged; bodies read directly):
  - `pay_statement_cashback_5d281cc6` and `settle_closing_cashback_4e373fbf` set `cashback_balance_usd = max(0, balance − amount)`. The whole booked amount, bonuses included, lowers the balance, which matches "every cashback payment booked …, bonuses included, lowers it … never falls below zero".
  - `move_off_card_plan_7a80b851` and `close_payout_account_ca79a9a7` set it to 0.0, which matches "cleared when the card's cashback lapses".
  - No task tool books an earning. Earnings are seeded, and "every cashback earning raises it" is borne out: in both seeds the balance equals earned − paid (task 0: 74.60 = 129.10 − 54.50; task 1: 125.00 = 190.50 − 65.50).
  - **The rule, compute and tool effects agree.**
- **Rules that read the redefined quantity:**
  - statement `due_total` (compute `cash_bal`);
  - exit `older_unpaid`.
  - Closing reads earned rows of the latest month only; closure and the others do not read it.
  - The "capped-off excess stays and falls due on the next payment day" is now what both readers compute. **F-R3-1 closed**: no rule treats an amount as lapsed while another reads it as unpaid.
- **Overrides:**
  - the minimum test restates base C4 ("when it is at least cashback_min_payment_usd; smaller amounts carry over"), which is not overwritten by statement_cashback, so this is consistent;
  - "carries the latest such month" and base C5 "each statement month is paid once": a later payment of carried-over excess carries the next due month;
  - **no undeclared override.**
- **The new action-form edge (check 6).**
  - Four-point test: the connective is "only after" ✓; the action is in business words ✓; no tool name or id ✓; the scope ("where one is owed") equals the condition ✓.
  - `fallback_reason` tested:
    - The candidate state "the latest passed month carries a payment" is unreachable when nothing is owed.
    - The candidate state "the balance less the waiting month is below the minimum" is unreachable in one write when the cap binds, because the excess stays in the balance by the statement's own rule.
    - I found no record-visible state that singles out exactly the statement payment in every case. **The fallback is justified.**
  - Derivation: the sentence plus the balance, the waiting month and the minimum (statement rule) → owed or not → the statement payment. One reading.
- **Observations kept:**
  - F-C6: the closure→closing `state_gate` still points at the field `payout_accounts.cashback_balance_usd`, and the closure declares no eligibility;
  - F-C8 (base acts with no tool);
  - F-C9 (realism of the holds).
- **New observation F-R4-1.** Payments lower the balance with their bonuses included, so a statement payment above the due amount eats into the next month's still-to-be-paid balance (task 1 after W1: balance 42.25 against September's earned 53.60). The closing settlement and the exit's month part are nevertheless computed from the month's earned rows, not from that balance. Both rules state their own base explicitly, so no second answer is demonstrated. In task 1 no rule reads the balance after W1: the closing uses earned rows, and the closure clears the balance.

### findings (revision 4)

| item | status |
|---|---|
| F-R3-1 SOURCE-POLICY RED | **closed** |
| new closing←statement action edge | passes check 6/7; fallback justified |
| F-C6 | not closed (observation) |
| F-C8 | not closed (observation) |
| F-C9 | not closed (observation) |
| F-R4-1 | new, observation |
| earlier closed items | still closed, no regression |

**Charter verdict (revision 4): no SOURCE-POLICY, SOURCE-CHAIN, SOURCE-FACTOR or SOURCE-TASK RED at charter level.**

### closing_checklist (revision 4)

Written after the reveal at 04:53:24Z.

- **Per-task verdicts:** task 0 PASS and task 1 PASS on all four relationships. GT equals my derivation on every write, factor and baseline figure.
- **Scopes:** disjoint and complete.
- **Uuid8s:** independent.
- **Trees:** each has 3 prerequisites, ≥2 value_input edges and an owner=user write. The graph is acyclic.
- **Factors:** every computation has 4–6 factors, ≥2 honest parameter and ≥1 honest method; every factor bears weight; every baseline is honest and differs from gold.
- **Charter verdict: no open RED**, so the four relationships hold for the difficulty.
- **Open observations** (not grounds for rework): F-C6 (state_gate points at a field), F-C8 (base acts with no tool), F-C9 (realism of the holds), F-R4-1 (payment bonuses lower the next month's still-to-be-paid balance while closing and exit read earned rows).
- **Gates:** not re-run by me. The round-4 orchestrator snapshot shows 7/7 green; `check_traceability` is deferred until the KB is published.
- **Status:** the difficulty passes the source-layer audit, pending the deferred traceability gate.
