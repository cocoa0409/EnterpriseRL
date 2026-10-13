# Policy-task audit — independent_living_billing_and_move_out / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (Claude agent, round 1); not the instantiating agent.
- Freeze time: 2026-10-05T09:07Z, written before any task's GT was revealed. Nothing in this section is derived from a revealed field.
- Frozen inputs (sha256, identical in the masked view directory and in `tasks/independent_living_billing_and_move_out/`):
  - `independent.extended.yaml` 69a676f9556703f0cc783f699f2ed41cdb0043a20158970157ce97c8e8aefb45
  - `task_tools.py` 4745b87971b6a009dcb32c2e334478af865e15d0e82975e67f08941ada0df62e
- Base copy: lines 1-1613 of `independent.extended.yaml` are byte-identical to `blueprint/products/independent.yaml` (diff shows only one trailing blank line).
- Fields read: blueprint (`blueprint.yaml`, `share_tools.py`, `products/independent.yaml`, `products/entrance.yaml` and `products/assisted.yaml` for the cross-category parameters), the extended charter and the tool module, and the masked task views (`frozen_time`, `user_scenario`, `initial_state`).
- Fields masked and not read: everything in `tasks/*.json` other than the three view fields (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`), and the scenario worklog.
- Entry conditions (Step 0): the brief supplied the gate snapshot (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred because the KB is not published yet) and the masked views with their MANIFEST hashes. I re-hashed the four view files and they match the MANIFEST. Input is complete.

### policy_conflict_scan

Extended policies (5), each with one target tool:

| policy | subject / computes | target tool (owner) | prerequisite |
| --- | --- | --- | --- |
| independent_ext_annual_increase_fee | independent_rate_adjust / monthly_service_fee | record_annual_increase_315a2923 (agent) | [] |
| independent_ext_period_late_fee | independent_late_fee_charge / late_fee_amount | assess_late_fee_72eb1d9b (agent) | [] |
| independent_ext_advance_payment | independent_payment / amount | make_advance_payment_0a0cd4e1 (user) | late fee (value_input), annual increase (value_input) |
| independent_ext_final_month_charge | independent_monthly_fee_charge / amount | post_final_month_charge_713925f6 (agent) | [] |
| independent_ext_closing_payment | independent_payment / amount | make_closing_payment_d2bd6461 (user) | final month charge (value_input) |

Overlaps checked:
- **The two payment policies share `independent_payment`** but have disjoint triggers. Advance payment covers "A resident of a continuing residency". Closing payment covers "A residency under a notice of termination ... before the apartment is surrendered". A notice_given residency is not continuing, so at most one of them applies to any residency.
- **Annual increase and final month charge.** The final month rule's "The monthly fee applied to the days of the final month follows any increase recorded on the residency" reads the result of the increase write but declares no edge to it. Take a world where an increase notice for the first day of the final month has run its notice period but is not yet recorded. Final month then has two values: recorded first, every day is billed at the new fee; not recorded, every day is billed at the old fee. Neither audited world has this. In task 1 the increase is already recorded (`proposed_monthly_service_fee` is empty and `rate_effective_date` is 2026-11-01). Recorded as an observation (O-3).
- **Late fee and annual increase.** These are the two parallel prerequisites of the advance and do not interact. The late fee compute reads only ledger rows and never `monthly_service_fee`. The increase compute reads the latest full-month base charge and the returned-payment count, and neither changes when a late fee is posted. Either order gives the same values.
- **Event-type claim.** Every subject event (independent_rate_adjust, independent_late_fee_charge, independent_payment, independent_monthly_fee_charge) is in the difficulty's claimed `event_types` in `blueprint.yaml`.
- **Scopes of the M=2 tasks.** These are read from the worlds only; `charter_scope` is masked. The task 0 world (active residency, payment returned, increase notice pending) holds the advance-payment tree: advance, late fee and annual increase. The task 1 world (notice_given residency, active AL residency) holds the closing-payment tree: closing and final month. The two trees are disjoint and together cover all five extended policies. This is confirmed against `charter_scope` after the reveal, in the task files.

### rule_compute_equivalence

Every `compute_basis` quotation is a verbatim substring of its policy's `rule` (mechanical check, all 5 policies). Every `baseline.rule` sentence is in the `rule`. Sentence-by-sentence sweep:

- **annual_increase_fee.** Equivalent. `billed_fee_before` is the latest full_month base_fee charge. `contract_ceiling_pct` takes the lifecare/fee_for_service branch only when the occupied EFA names this residency (`plan_residency == HID`), as the rule says. The relief ladders, ceiling rounding and clamp all match the rule.
- **period_late_fee.** One divergence (F-4).
  - The rule's tier 1 is "where a payment posted within the one month ending on the day of assessment was returned by the bank within that month". The compute `month_returns` sums every `independent_payment_return` posted within the month, whenever the returned payment was posted. Take a payment posted before the month window and returned inside it. The rule leaves the case on tier 2 or the fall-through; the compute puts it on tier 1 and adds the returned amount to the past-due amount.
  - Everything else is equivalent: period charges (one-time fees carry no billing_period), escalation, residence and plan reliefs floored at 0, the returned-fee credit, and the daily charge counted as DAYS(posted, now) − grace.
- **advance_payment.** One divergence for quantities of 3 or more (F-3).
  - The rule says "Rented storage units are billed ... at storage_unit_monthly_fee per unit, the number of units being the quantity on the latest storage unit charge: a household renting two storage units adds storage_unit_monthly_fee twice". Parking is worded the same way.
  - The compute is `2 * P(...) if storage_on_latest_charge >= 2`, and the factor ladder says "two or more". For a latest quantity of 3 the rule's "per unit" gives 3 × fee and the compute gives 2 × fee. The rule states no "two or more" tier. Pets cannot reach 3 because `max_pets` ≤ 2.
  - The open-balance composition and the three-way advance matches the rule.
- **final_month_charge.** Equivalent.
  - `period_end_offset` lets a transfer_assisted notice pair with an active memory residency, and the reverse. The rule's "a move to a Larkspur assisted living or memory care residence and ... assisted living or memory care residency is active" is equally loose, so they agree.
  - `fee_end_offset`, `gross_charge` (offset == 1 means the first day of the final month), the three courtesies and the single reduction all match the rule.
- **closing_payment.** Same quantity-of-3 divergence as the advance for storage and parking (F-3). The cleaning share, ledger balance and three-way settlement match the rule.

### action_binding_and_uuids

- **(target_tool, computes) pairs.** The five pairs are distinct. The two `amount` computations on `independent_payment` go to different tools with disjoint triggers.
- **uuid8 suffixes.** 315a2923, 72eb1d9b, 0a0cd4e1, 713925f6, d2bd6461. They share no prefix, are not sequential and are not reused. No sign of batch derivation.
- **Docstrings.**
  - None names another tool, states a position in a sequence, or uses before/after/first.
  - `make_closing_payment_d2bd6461` says the balance falls "showing a credit for charges still to post". That describes the outcome, not an order (observation O-5).
- **Tool bodies.**
  - Every body is an unconditional write: `ctx.create` / `ctx.update` with the passed values, plus an `account_balance` delta.
  - None checks status, dates or the existence of any other row. **No tool judges a prerequisite.**
  - `post_final_month_charge_713925f6` derives `service_from_date` = first of the month of `service_to_date`, `days_billed` = the day number, and `charge_basis` = prorated_move_out.

### prerequisite_graph

- **Field present everywhere.** Every extended policy carries `prerequisite`; the three non-root policies use `[]`.
- **Edges.**
  - advance → period_late_fee (value_input, gate `open_balance`)
  - advance → annual_increase_fee (value_input, gate `coming_fee`)
  - closing → final_month_charge (value_input, gate `ledger_balance`)
- **Targets.** Every target is an extended policy id in this file, never a base policy and never itself. The graph is acyclic: two disjoint trees of depth 1.
- **policy_source.** Every `policy_source` is a verbatim sentence of the blocked policy's own rule (mechanical check). No depended-on rule restates it.
- **form.** All edges are `form: state` with no `fallback_reason`, as required.
- **resolved_by.** Each equals the depended-on policy's `target_tool`.
- **Gates.** `open_balance`, `coming_fee` and `ledger_balance` are real bindings of the blocked compute.
- **effect.** Each effect holds on the tool semantics:
  - a late fee row raises the ledger sum that `open_balance` reads;
  - the increase write replaces the `monthly_service_fee` that `coming_fee` reads;
  - the final-month row raises the ledger sum that `ledger_balance` reads.
- **Authoring-viewpoint wording.** No "in this task / at the opening" phrasing appears in the prerequisite text.
- **`condition` strength against the sentence:** see F-1 and F-2 under `prerequisite_sentences`.

### prerequisite_sentences

Four-point test, per edge:

1. advance ← late fee: "The advance amount is worked out only after the ledger carries a late fee entry for every billing period whose grace period has ended while its monthly fees remained past due."
   - It has an ordering connective ("only after").
   - It names a record-visible state: a late fee entry on the ledger for a period.
   - It names no tool, id or snake_case token.
   - **Strength:** the sentence is broader than the declared `condition`, which adds "still past due at or above late_fee_min_past_due" (F-1).
   - Only `assess_late_fee_72eb1d9b` writes late fee entries, so the hop resolves uniquely.
   - Derivation: no late fee row for a period that is past due after grace → independent_ext_period_late_fee is the policy whose result is a late fee entry → assess it.
2. advance ← annual increase: "The advance amount is not worked out until the residency record shows, as its fee in effect, the fee taking effect on the first day of the coming month under any annual increase whose notice period has already run."
   - It has an ordering connective ("not ... until").
   - It names a state: the fee in effect on the residency record (`monthly_service_fee` / `rate_effective_date`).
   - It names no tool or id.
   - Its strength matches the condition.
   - Only `record_annual_increase_315a2923` replaces `monthly_service_fee` among this difficulty's writes.
   - Derivation: the record shows the old fee while a mailed notice for the 1st of the coming month has run → independent_ext_annual_increase_fee is the policy that sets the fee recorded for that increase → record it.
3. closing ← final month: "The closing amount is worked out only after the ledger carries a monthly fee charge for the final month running from its first day through the date the residency's fees end."
   - It has an ordering connective and names a state (a ledger monthly fee charge row with its span).
   - It names no tool or id.
   - **Strength:** the sentence is broader than the condition, which adds "wherever that fee end date falls after the last day already billed" (F-2).
   - Only `post_final_month_charge_713925f6` writes a monthly fee charge, so the hop resolves uniquely.
   - Derivation: no charge for the month after the last month billed, running to the fee end date → independent_ext_final_month_charge posts exactly that row → post it.

Other checks:
- No rule carries a second wording of any edge, and no depended-on rule restates a sentence.
- No base rule sentence grounds an edge.
- Undeclared cross-problem order: final_month ← annual_increase is read through "follows any increase recorded" with no ordering connective. It is latent and does not occur in either world (O-3).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry.

**annual_increase_fee vs independent_rate_adjustment.**
- Declared: "the fee recorded ... is the proposed fee from that notice" → clamp. Also declared: the max_annual_increase_pct cap sentence (first clause only) → ceiling after reliefs.
- Followed, and not hit by the overwrite: once a year with the effective month; notice mailing; the notice-period gate; the guarantee; live status; "at most one increase in any 12-month period" (the second clause of the superseded sentence survives); the prorated_rate_change difference; published base fees.
- The extended rule's first sentence restates the superseded base clause as its baseline sentence. Its later "Where ..." sentences refine it. Read whole, the merged reading is unique (O-1).

**period_late_fee vs independent_late_fee.**
- Declared: the msr_period_past_due clause → payments within one month; "greater of late_fee_flat and late_fee_pct percent" → greater of flat and the late fee percentage.
- The returned-fee credit and the daily charge then modify the "greater" amount. The `replaced_by` text does not mention them, but the base sentence they displace is named. Declared (O-2).
- Followed: due day and grace; the grace-end gate; the minimum; one per period; live status; goodwill waiver; no late fee on late/community/one-time fees.

**advance_payment vs payments_and_returns / monthly_billing / service_fees** (`overwrite: []`).
- Followed: one-time ACH is an accepted method; one instrument posted once; oldest-first application; the certified-funds restriction still binds, inherited; payment on active/notice_given/vacated.
- The coming statement follows monthly billing: the base fee plus the second person fee while double.
- Pets are per pet without proration. Storage is charged where it is not included or a second unit is rented. Parking is charged beyond the included spaces.
- **Conflict for quantity ≥ 3** (F-3): the base charges per unit; the extended compute caps at 2 × fee. It is undeclared because `overwrite` is [].

**final_month_charge vs monthly_billing / fee_end_and_proration.**
- Declared: actual-days proration → `proration_basis_days`.
- **Undeclared narrowing** (F-5). The base says "After a notice stating a move to a Larkspur assisted living or memory care residence ... the fee end date is the later of the vacate date and the notice date plus internal_transfer_notice_days". Base `independent_move_out_notice` sets the transfer notice period "when the notice states a move to a Larkspur assisted living or memory care residence". The extended adds "and the customer's Larkspur assisted living or memory care residency is active", and otherwise applies move_out_notice_days. The overwrite names no sentence of `independent_fee_end_and_proration`.
- Base death branch: the extended ladder has no tier for a resident who dies while under notice. Base has two applicable clauses there itself (resident notice and death), so no unique base conclusion is displaced. Observation O-4.
- Second person fee: the base says it ends on the same fee end date. No extended policy posts the final month's second person fee and the closing amount omits it. Latent for double occupancy (O-4).
- Courtesies reduce the charge. The displaced base proration sentence is named, so this is declared.

**closing_payment vs payments_and_returns / final_statement / service_fees.**
- Declared: "The carpet_cleaning fee of the apartment type is charged once when the apartment is vacated" → "The share of the move-out carpet cleaning fee in the closing amount follows where the resident is moving".
- **The declared replacement leaves the merged semantics non-unique** (F-6). The `independent_vacate` event still triggers a `carpet_cleaning` service fee charge. Base `independent_final_statement` lists "the carpet cleaning fee". The extended rule itself says "the carpet_cleaning_fee of the apartment type that the final statement will carry when the apartment is vacated". So what the vacate posts for an AL transfer has two readings: (a) the full carpet_cleaning_fee, which leaves the closing payment short by the other half; (b) the share, because the only base sentence fixing the vacate-time amount was superseded by a share rule.
- Followed: one-time ACH; credit balance refunds only after vacate; close at zero balances; no write-off.

### factor_ladders

Counts are per computation: parameter / method / multi-source / cross_difficulty.

**annual_increase_fee: 4 factors.**
- contract_ceiling (parameter, cross: entrance, multi-source: occupied EFA status + plan + names this residency).
- residence_relief (parameter).
- standing_relief (parameter).
- fee_selection (method; the clamp picks the ceiling, the prior fee or the notice).
- Every ladder has 3 tiers, disjoint, with distinct values. All are stated in the rule and in compute. Values come from `params` and `P()`.
- Business reality: CCRC contract caps, loyalty relief and good-standing relief are plausible.
- 3 param / 1 method / 1 multi-source / 1 cross.

**period_late_fee: 6 factors.**
- past_due_reckoning (method).
- repeat_lateness (parameter).
- residence_length (parameter).
- entrance_plan_terms (parameter, cross: entrance).
- returned_fee_credit (parameter, multi-source: return count AND autopay payment).
- daily_late_charge (method).
- **daily_late_charge is not a real ladder** (F-7). Base `independent_late_fee` says "The grace period ends at the end of the day equal to the posting date of the monthly fee charge plus payment_grace_days calendar days, and a late fee may be assessed only on a later date". The extended daily charge counts days from that same grace end to the day of assessment. So at every permitted assessment at least one day has run. The tier condition "at least one day" holds of every customer who reaches this write. The fall-through "where no day has run, there is none" is reachable by none, so its baseline (0) is a treatment no assessed customer receives. Struck as a factor.
- Remaining: 5 factors, 4 param / 1 method / ≥1 multi-source / 1 cross. Bounds still met.
- past_due_reckoning: on each tier's own domain, the three tiers equal the single expression charges − (payments − returns) − credits. The tiers differ formally (which terms enter), so it is kept, with an observation (O-6).

**advance_payment: 4 factors.**
- open_balance_first (method).
- registered_pets, rented_storage, rented_parking (parameter).
- All are 3-tier and stated in the rule, except that the "two or more" wording lives only in compute and the factor ladder (F-3).
- open_balance_first has the same signed-sum collapse as past_due_reckoning (O-6). Its tier can be read off `independent_residencies.account_balance`, which by the charter's `accounts` definition is the same quantity. That is the authoritative account field rather than an outcome stamp, so it is an observation (O-7).
- No cross factor in this computation. The task-level cross requirement is carried by the other computations of the same tree.
- 3 param / 1 method.

**final_month_charge: 6 factors.**
- notice_period_end (method, cross: assisted, multi-source: notice reason + care residency status).
- surrender_floor (method).
- recorded_increase_span (method).
- standing_courtesy (parameter, multi-source: late fees AND returns).
- autopay_courtesy (parameter).
- care_transition_courtesy (parameter, cross: assisted).
- **notice_period_end** (F-8):
  - Tier 2 is "the residency ends by a discharge for nonpayment and a discharge notice date is recorded". `termination_reason` nonpayment_discharge is written only by `independent_end_without_notice` (active → vacated), and base `billing_on_live_residency` forbids posting a monthly fee charge on a vacated residency. Tier 2 is therefore unreachable at this write, leaving 2 live tiers.
  - The tiers also only substitute a day count into "notice date + N" (N = internal_transfer_notice_days / 0 / move_out_notice_days), so the `method` label is not honest.
  - Struck.
- **surrender_floor** (F-8):
  - Tier 1 "a vacate date is recorded" needs status vacated, where billing is forbidden.
  - The fall-through "no ... intended vacate date" cannot occur under a standing notice, because base `independent_move_out_notice` says "the desk registers the notice request with the intended vacate date the resident states".
  - So tier 2's condition holds of every customer who reaches this write. Struck.
- recorded_increase_span: tier 1 against the fall-through only swaps the fee, while tier 2 changes the algorithm (a split span). The label is kept, with an observation (O-8).
- After striking: 4 factors, 3 param / 1 method / ≥1 multi-source / 1 cross. Bounds still met.

**closing_payment: 5 factors.**
- transfer_cleaning_share (parameter, cross: assisted, multi-source: notice reason + care residency status).
- final_month_pets, final_month_storage, final_month_parking (parameter).
- ledger_settlement (method).
- The quantity-of-3 divergence affects storage and parking (F-3).
- The business reality of the assisted-transfer tier depends on the F-6 reading. Under reading (a) the "50 % share" is not a discount the business gives; it is a closing payment that knowingly leaves half the fee owed.
- 4 param / 1 method / 1 multi-source / 1 cross.

### findings

| id | class | finding | bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-POLICY RED (latent) | Advance ← late-fee sentence is broader than its condition. Take a period that is past due after grace by less than late_fee_min_past_due (100.00). The sentence demands a late fee entry. Base/extended late fee rules: "No late fee is assessed when the past-due amount of the billing period is below late_fee_min_past_due". So the advance can never be worked out. The ext late fee also only assesses "the billing period of the latest monthly fee charge", so two unassessed periods cannot both be satisfied. | task 0 tree. Its world has only 2026-12 past due (5147.40), so there is no consequence there |
| F-2 | SOURCE-POLICY RED (latent) | Closing ← final-month sentence is broader than its condition. Where the fee end date falls inside an already-billed month, final month rule: "No final month's base fee charge is posted when the fee end date falls on or before the last day already billed". The closing sentence then waits forever on a charge "running from its first day through the date the residency's fees end". | task 1 tree. Its fee end (2026-11-09) is after the last billed day (2026-10-31), so there is no consequence there |
| F-3 | SOURCE-POLICY RED (latent) | Rule "per unit" (storage/parking) vs compute `2 * fee if qty >= 2`, in both the advance and the closing. They differ at qty ≥ 3 (for example 3 storage units: 135.00 vs 90.00). The base service_fees charges per unit, and the advance overwrite is []. | tasks 0 and 1; both worlds have qty 1, so there is no consequence |
| F-4 | SOURCE-POLICY RED (latent) | Late fee tier 1 (rule: return of "a payment posted within the one month") vs compute `month_returns` (any return posted within the month). | task 0; its only return (12-05) is of a 12-01 payment, both inside the window, so there is no consequence |
| F-5 | SOURCE-POLICY RED (latent) | Undeclared narrowing of the base transfer fee-end clause to "residency is active". Example: an AL residency in pending_admission with a transfer_assisted notice gives base notice + 7 and ext notice + 30. | task 1; its AL residency is active, so the readings agree |
| F-6 | SOURCE-POLICY RED (latent for the scored write) | The carpet_cleaning overwrite leaves the vacate-time charge with two readings, (a) full or (b) share. | task 1; the scored closing amount is the same under both. The divergence is after the task's last write |
| F-7 | SOURCE-FACTOR RED | daily_late_charge: fall-through unreachable, "at least one day" holds of every assessed customer, baseline 0 is a straw man | task 0 (late fee computation) |
| F-8 | SOURCE-FACTOR RED | notice_period_end: tier 2 unreachable at this write, and mislabelled `method`. surrender_floor: only tier 2 is reachable | task 1 (final month computation) |
| O-1..O-8 | observations | O-1 the extended rule opens with the superseded base clause as its baseline; O-2 incomplete `replaced_by` text for the late fee; O-3 latent final-month/increase order; O-4 death and second-person-fee branches absent from final month/closing; O-5 closing docstring describes the outcome; O-6 signed-sum ladders (past_due_reckoning, open_balance_first, ledger_settlement); O-7 account_balance mirrors the open balance; O-8 recorded_increase_span tier 1 vs fall-through is a fee swap | — |

## closing_checklist

Written after both reveals (2026-10-05T09:11Z (approx.)). The difficulty **does not close** in round 1, because not all four relationships PASS.

- **Audit files.**
  - Present: `0.md`, `1.md` and this file, one per task. Round 1, no older revisions.
  - Both comparisons carry their verdicts. Unique solution and problem tree are PASS in both. Factors are SOURCE-FACTOR RED in both (F-7 on task 0, F-8 on task 1).
- **Policy coverage and scope.**
  - The five extended policies are fully covered: task 0 holds {period_late_fee, annual_increase_fee, advance_payment} and task 1 holds {final_month_charge, closing_payment}.
  - The scopes are pairwise disjoint, confirmed against `charter_scope`.
  - Task tools and GT are closed. Each tool's uuid8 is independent.
- **Problem trees.**
  - Task 0: 2 prerequisites, both value_input.
  - Task 1: 1 prerequisite, value_input.
  - Each root is an owner=user tool. The difficulty graph is acyclic: two disjoint depth-1 trees.
- **Factors.** The bounds hold even after striking the F-7 and F-8 factors:
  - late fee: 5 left
  - final month: 4 left
  - every other computation: 4–5
  - Baselines alone give definite numbers ≠ gold: 0, 4279.39, 5195.61, 2513.07, 185.00.
  - The ladder-reality test fails for daily_late_charge, notice_period_end and surrender_floor.
- **Charter-global SOURCE-POLICY REDs.** F-1 to F-6 stand. All are latent on the two audited worlds.
- **Gates.** This difficulty's gates were not re-run on a final form. No final form exists yet, because the difficulty does not pass.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: same independent auditor, round 2.
- Written before the round-2 task JSONs were opened. Nothing in this section is derived from a round-2 GT field.
- Inputs:
  - `independent.extended.yaml` 3520656a60c6d00cb328bfa9e92467e25e1c6e35ebcbdeaf1496a3139b755c89 (**changed** from round 1's 69a676f9…). It matches the copy in `tasks/independent_living_billing_and_move_out/`.
  - `task_tools.py` 4745b87971b6a009dcb32c2e334478af865e15d0e82975e67f08941ada0df62e (unchanged).
  - Task views unchanged: 3c1abe57… and aa024c92…. The view MANIFEST was re-hashed and matches.
- Base copy: lines 1–1613 are still identical to `blueprint/products/independent.yaml` (diff shows only the trailing blank line).
- Because the charter changed, every charter-global section is **re-derived in full** below. The round-1 text above is preserved untouched.
- Entry conditions: the coordinator supplied the round-2 gate snapshot (all OK; traceability deferred) and the rebuilt views with their hashes.

**Charter delta read off the new file:**
1. **Advance ← late-fee sentence** now reads: "The advance amount is worked out only after the ledger carries a late fee entry for the billing period of the latest monthly fee charge whenever that period's grace period has ended with a past-due amount at or above the minimum that draws a late fee."
2. **Late fee tier 1** now reads "where a returned payment was posted within the one month ending on the day of assessment".
3. **New `daily_charge_free_days: 5`.** The daily-charge tiers are now: ≥15 days → cap; more than 5 and fewer than 15 → per day; 5 or fewer → none.
4. **Advance and closing quantity ladders**: "two or more ... once for each", with compute `qty * fee` for qty ≥ 2.
5. **Final month:**
   - A second overwrite supersedes base `independent_fee_end_and_proration` sentence 3 (the transfer fee-end clause).
   - New `memory_transfer_notice_days: 0`.
   - The notice period now follows the notice's stated move (memory 0 / assisted internal_transfer_notice_days / other move_out_notice_days), with no "active" condition.
   - The surrender floor moved into the baseline sentence ("the later of the vacate date, or before the apartment is surrendered the intended vacate date ..., and the notice date plus move_out_notice_days").
   - Factors are now notice_period (parameter), recorded_increase_span (method), new residence_courtesy (parameter: ≥60 months 2.0, 12–59 months 1.0, <12 none), standing_courtesy (tier 2 reworded as "one late fee and no returned payment, or one returned payment and no late fee"; same domain as before), autopay_courtesy and care_transition_courtesy.
   - `cross_category` is now assisted only.
6. **Closing:**
   - The overwrite's `replaced_by` is now "The move-out carpet cleaning fee charged when the apartment is vacated follows where the resident is moving, and the closing amount carries that same fee".
   - The rule now states that the vacate-time charge itself is the share.
   - The prerequisite sentence now carries "wherever the residency's fees end after the last day already billed".
7. Annual increase: unchanged.

### policy_conflict_scan (revision 2)

- The trigger split between advance and closing is unchanged: continuing residency against a standing notice.
- **Late fee and annual increase** still commute: neither compute reads the other's write.
- **Final month and a pending increase** (O-3) are unchanged and remain a latent observation.
- **Scopes** are read from the worlds: task 0 = {late fee, increase, advance}, task 1 = {final month, closing}. They are disjoint and jointly complete.

### rule_compute_equivalence (revision 2)

Mechanical check:
- Every `compute_basis` value is a verbatim substring of its rule, and every basis key is a compute binding.
- Every `baseline.rule` sentence is in its rule.
- Every factor `decides` names a binding.

Sweep:
- **Late fee.** Tier 1 now quotes "a returned payment was posted within the one month", which equals `month_returns > 0`. **F-4 closed.** The daily charge `days_after_grace > K('daily_charge_free_days')` matches "more than daily_charge_free_days days", and ≤ 5 gives none.
- **Advance and closing.** "two or more ... once for each" equals `qty * fee if qty >= 2`. **F-3 closed.**
- **Final month.**
  - `notice_period_days` takes transfer_memory → K(0), transfer_assisted → P(internal), else P(move_out), as the rule says.
  - `fee_end_offset = MX(DAYS(last, vacate or intended), period_end)` matches the new fee-end sentence.
  - `residence_courtesy_pct` matches its sentence.
  - `standing_courtesy_pct` (1 + 0 or 0 + 1) matches the reworded tier.
  - The four-way courtesy sum matches "The four courtesy percentages are added". Equivalent.
- **Closing.** `cleaning_part` matches its sentence. Equivalent.
- **Annual increase.** Unchanged and equivalent.

### action_binding_and_uuids (revision 2)

- The tool module is unchanged (same hash). The round-1 conclusions stand: five distinct (target_tool, computes) pairs, independent uuid8s, no ordering words in docstrings, and no tool judges a prerequisite.

### prerequisite_graph (revision 2)

- Same three edges, all value_input and state form.
- Each `policy_source` is verbatim in its own rule. No depended-on rule restates it.
- `resolved_by` equals the depended-on target tool. The gates `open_balance`, `coming_fee` and `ledger_balance` are compute bindings.
- The graph is acyclic.
- **Advance ← late fee** `condition` now reads "for the billing period of the latest independent_monthly_fee_charge whenever that period's grace period has ended with its past-due amount, as the late fee rule reckons it, at or above late_fee_min_past_due". This is the same strength and scope as the new sentence.
- **Closing ← final month** `condition` is unchanged and now matches the sentence's added "wherever" clause.

### prerequisite_sentences (revision 2)

1. **Advance ← late fee.**
   - It has an ordering connective ("only after") and names a state: a late fee entry for a named period.
   - It names no tool or id.
   - **Its strength now matches the condition.** It names the single period the late fee policy assesses ("the billing period of the latest monthly fee charge") and the minimum ("at or above the minimum that draws a late fee").
   - A period below the minimum no longer blocks the advance, and earlier periods are no longer demanded.
   - Unique resolver: assess_late_fee. **F-1 closed.**
2. **Advance ← increase.** Unchanged, and still passes.
3. **Closing ← final month.**
   - The sentence now carries "wherever the residency's fees end after the last day already billed". Where fees end inside a billed month, nothing is waited on, which matches the final-month rule's "No final month's base fee charge is posted when ...".
   - Unique resolver: post_final_month_charge. **F-2 closed.**

### override_declarations (revision 2)

**Annual increase and late fee.**
- Unchanged from round 1. Declared.
- The late fee's new free-days tier does not displace any base sentence.

**Advance** (`overwrite: []`).
- Per-unit storage and parking now agree with base `independent_service_fees` "per billing month ... for each space beyond". **F-3's undeclared cap is gone.**

**Final month.**
- **The declared second overwrite of base `independent_fee_end_and_proration` sentence 3 closes F-5.** The extended no longer narrows the transfer clause to an "active" residency, and its deviation (memory 0 days) is declared.
- **New finding N-2 (regression of the rework).** The superseded base sentence governed two subjects: "After a notice stating a move to a Larkspur assisted living or memory care residence, **and for an internal transfer recorded without notice**, the fee end date is **the later of the vacate date and** the notice date plus internal_transfer_notice_days calendar days."
  - The `replaced_by` speaks only of "The notice period added to the notice date follows the move the notice states".
  - After the merge, the base fee-end policy (`independent_fee_end_and_proration`, subject `independent_vacate`, `independent_end_without_notice` and the move_out_proration `independent_credit`) has lost two things:
    - (i) any fee-end rule for an internal transfer recorded without notice (`independent_end_without_notice`, transfer_assisted / transfer_memory);
    - (ii) the "later of the vacate date" floor for transfer notices.
  - The extended final-month policy carries its own floor, but only for its own charge.
  - Demonstration. Situation: an AL transfer notice dated 10-01 and an actual vacate on 10-20.
    - Merged base fee end: 10-01 + 7 = 10-08. No floor survives in the base, because the resident-notice floor sentence covers "After a resident notice" only.
    - Round-1 base and the extended final-month rule: the later of 10-20 and 10-08 = 10-20.
    - So two passages give two fee end dates for the same residency. For an internal transfer recorded without notice, no surviving sentence gives a fee end date at all.
  - Latent: neither audited world is a vacate-time or no-notice transfer. Recorded as **SOURCE-POLICY RED (latent)**.
- **N-1 (observation).** Base `independent_move_out_notice` (not in this policy's `base_policy_refs`) still says "The notice period is move_out_notice_days for a resident leaving Larkspur and internal_transfer_notice_days when the notice states a move to a Larkspur assisted living or memory care residence". The extended says a memory-care notice "adds memory_transfer_notice_days" (0).
  - The base sentence goes on "but fees still run as set by the fee end policy", so the fee end, which is the scored quantity, is governed by the declared override.
  - The two "notice period" wordings differ only for memory transfers. No scored consequence is demonstrable, so it is an observation.

**Closing.**
- The `replaced_by` now states that the vacate-time carpet charge itself follows the move ("is charged ... percent").
- The closing amount carries "that same fee", and the closing rule says the fee is "charged once when the apartment is vacated and carried on the final statement".
- The vacate event's carpet_cleaning charge, the final statement and the closing amount now share one quantity. **The merged reading is unique. F-6 closed.**

### factor_ladders (revision 2)

**Annual increase.** Unchanged: 4 factors, 3 param / 1 method, cross entrance, multi-source contract_ceiling. Pass.

**Late fee.** 6 factors.
- **daily_late_charge** is now three reachable tiers.
  - Base assessment is allowed from the first day after grace. Days 1–5 → none, 6–14 → per day, ≥15 → cap.
  - The values are distinct. The baseline (0) is the real treatment for a fee assessed within 5 days of grace end.
  - "Grace-plus-free-days" daily charges are common in residential billing. **F-7 closed.**
- Other factors are unchanged: 4 param / 2 method, cross entrance, multi-source returned_fee_credit.

**Advance.** 4 factors.
- The quantity ladders now give n × fee, fee and 0. The values are distinct, so the round-1 O-6 note about the signed-sum shape still applies as an observation.
- 3 param / 1 method.

**Final month.** 6 factors.
- **notice_period** (parameter): memory 0 / assisted 7 (14 Cottage) / other 30 (60 Cottage).
  - All three tiers are reachable under a standing notice, because `notice_record` writes resident_notice, transfer_assisted or transfer_memory.
  - The values are distinct and the label is honest.
  - Business reality: an immediate move to a secured memory suite versus a short internal-transfer notice is plausible.
- **surrender_floor is no longer a factor.** The single live case now sits in the baseline sentence, which is where a scope condition belongs.
- **F-8 closed.**
- residence_courtesy (parameter): 60+ / 12–59 / <12. Reachable, distinct, plausible.
- recorded_increase_span, standing_courtesy, autopay_courtesy and care_transition_courtesy are as in round 1.
- Totals: 5 param / 1 method / multi-source (standing_courtesy: late fees AND returns) / cross assisted (care_transition_courtesy). `notice_period` reads only the IL notice's stated move, so `cross_difficulty: null` is right.

**Closing.**
- 5 factors: 4 param / 1 method, cross assisted, multi-source transfer_cleaning_share.
- Under the closed F-6, the 50 % / 0 % share is a real move-out discount, so the earlier business-reality reservation is withdrawn.

### findings (revision 2)

| id | round-1 class | round-2 status |
| --- | --- | --- |
| F-1 | SOURCE-POLICY RED (latent) | **closed**: sentence and condition both name the latest period and the minimum |
| F-2 | SOURCE-POLICY RED (latent) | **closed**: the "wherever ... after the last day already billed" clause was added |
| F-3 | SOURCE-POLICY RED (latent) | **closed**: per-unit ladders; rule = compute = base |
| F-4 | SOURCE-POLICY RED (latent) | **closed**: rule tier 1 = `month_returns > 0` |
| F-5 | SOURCE-POLICY RED (latent) | **closed**: "active" narrowing removed; the memory deviation is declared |
| F-6 | SOURCE-POLICY RED (latent) | **closed**: the vacate charge and the closing amount share the declared share |
| F-7 | SOURCE-FACTOR RED | **closed**: free-days tier makes the fall-through reachable |
| F-8 | SOURCE-FACTOR RED | **closed**: notice_period is a reachable, honest parameter; surrender_floor removed as a factor |
| **N-2** | — | **new SOURCE-POLICY RED (latent), introduced by the F-5 rework.** The superseded base fee-end sentence also carried the internal-transfer-without-notice branch and the vacate-date floor for transfers, and the replacement restores neither (see `override_declarations (revision 2)`). Bears on task 1's policy (final month) only latently: task 1's charge is computed by the extended rule, which keeps its own floor |
| N-1 | — | observation: the base move_out_notice "notice period" for memory transfers (internal_transfer_notice_days) differs from the extended's memory_transfer_notice_days 0; fees follow the fee-end override |
| O-1, O-2, O-3, O-4, O-5, O-6, O-7 | observations | unchanged in substance; they remain observations (O-4 second person fee and O-3 pending increase are latent; O-5/O-7 tools and account field unchanged) |

### closing_checklist (revision 2)

Written after both round-2 reveals. Round-2 GT: `0.json` 259fce2a…, `1.json` b6f7439d….

- **Round-1 REDs.** All of F-1 to F-8 are verified **closed**. Evidence is under `revision_2` above and in each task file's `revision_2`.
- **Regressions.**
  - Task 0: every scored and per-factor value is unchanged.
  - Task 1: values changed only through the declared new residence_courtesy factor (1148.26 and 1375.76, verified against the task JSON and equal to my blind round-2 derivation).
  - The trees, edges, owners and order are unchanged.
- **New defect.** **N-2** is a latent SOURCE-POLICY RED: the second overwrite on `independent_fee_end_and_proration` drops the internal-transfer-without-notice branch and the vacate-date floor for transfers.
  - It has no consequence on either audited world.
  - It is still a defect of the shared charter: two passages give different fee end dates for a transfer notice followed by a later vacate (base merged: notice + 7; extended final month: the later of vacate and notice + 7), and no fee end at all for an internal transfer recorded without notice.
  - New observations: N-1, and R2-O1 (a stale tier label in task 0's `factor_sensitivity`).
- **Files.** `0.md`, `1.md` and `_difficulty.md` each carry an appended `revision_2`. The round-1 text is untouched.
- **Coverage and structure.**
  - Coverage, disjoint scopes, tool closure and the uuid8s are unchanged and hold.
  - Trees: task 0 n = 2, task 1 n = 1, all value_input, user roots, acyclic.
  - Factors: every computation has 4–6 real factors with ≥2 parameter and ≥1 method. Each task has a multi-source factor and a cross-difficulty factor. Every factor bears weight against an honest baseline, and every whole-baseline number differs from gold.
- **Difficulty status.** It **does not close** while N-2 stands, because charter-global policy self-consistency is not PASS. Every per-task relationship other than that latent charter defect is PASS.
- **Gates.** Not re-run by me. The coordinator's round-2 snapshot is all OK.

## revision_3

### charter_global_frozen (revision 3)

- Auditor: same independent auditor, round 3. Written before the round-3 task JSONs were opened.
- Inputs:
  - `independent.extended.yaml` 718e11f71cf99a81e3931c95f2aeb41783fce48e4f460f0f27f3f91a9a11a810 (**changed** from round 2's 3520656a…). It matches the copy in the tasks directory, and `sha256sum -c` against the view MANIFEST passes.
  - `task_tools.py` 4745b879… (unchanged).
  - Task views 3c1abe57… / aa024c92… (unchanged).
- Base copy: still identical to `blueprint/products/independent.yaml` (only the trailing blank line differs).
- Because the charter changed, the charter-global sections are re-checked below. The round-1 and round-2 text is preserved.

**Delta.** The file grew by 6 lines, all inside `independent_ext_final_month_charge`. The other four policies keep their round-2 start lines and lengths, and their round-2 changes are still present (free days, "once for each", the returned-payment tier 1, the "wherever" clause, the vacate-time cleaning share).

The final-month changes:
1. `base_policy_refs` now includes `independent_move_out_notice`.
2. `overwrite[1]` (`independent_fee_end_and_proration`): `replaced_by` is now "For a notice stating a move to a Larkspur assisted living or memory care residence, and for an internal transfer to either recorded without notice, the fee end date is the later of the vacate date and the notice date plus the notice period that move carries." The same sentence is added to the rule.
3. New `overwrite[2]` (`independent_move_out_notice`) supersedes "The notice period is move_out_notice_days for a resident leaving Larkspur and internal_transfer_notice_days when the notice states a move to a Larkspur assisted living or memory care residence". It is replaced by the extended notice-period sentence (memory memory_transfer_notice_days / assisted internal_transfer_notice_days / other move_out_notice_days).
4. Compute, factors, params and baseline are unchanged from round 2. `compute_basis.period_end_offset` now quotes the new sentence.

**Mechanical check (all five policies):**
- Every `compute_basis` is verbatim in its rule and is a compute key.
- Every baseline sentence is in its rule.
- Every superseded clause is verbatim in its base policy, and that base policy is in `base_policy_refs`.
- Every `replaced_by` is verbatim in the extended rule.
- Every `policy_source` is verbatim in its own rule.

### N-2 and N-1 re-check

**N-2: closed.**
- The merged base fee-end sentence again covers both subjects: transfer notices, and "an internal transfer to either recorded without notice". It also again carries "the later of the vacate date and ...".
- Round-2 demonstration situation: an AL transfer notice on 10-01, vacated 10-20. Merged base gives the later of 10-20 and 10-01 + 7, which is 10-20. The extended final month gives the later of 10-20 and 10-08, also 10-20. The two now agree.
- Internal transfer without notice: fee end = later(vacate, notice_date + 7) for AL, or + 0 for memory ("the notice period that move carries", read off the extended notice-period sentence). That is a definite answer.

**N-1: closed (declared).**
- The base move_out_notice notice-period sentence is now superseded by declaration, so the memory-transfer notice period (0) has a single merged value.
- The base sentence's surviving tail, "the intended vacate date may be earlier than the end of the notice period, but fees still run as set by the fee end policy", is compatible.
- move_out_notice's notice period gates no write in this difficulty.

### Regression scan (revision 3)

- **Conflict scan, action binding and uuids, prerequisite graph, prerequisite sentences.** Unchanged from round 2, because no edge, tool or prerequisite text changed. They still pass.
- **rule_compute_equivalence.** The final month's compute is unchanged. The new sentence is equivalent to `fee_end_offset = MX(DAYS(last, vacate or intended), notice_offset + notice_period_days)` once the rule's earlier sentence "the later of the vacate date, or before the apartment is surrendered the intended vacate date stated on the notice, and ..." supplies the pre-surrender substitute for "the vacate date".
- **Observation R3-O1 (new).**
  - The new sentence ("For a notice stating a move to ... the fee end date is the later of the vacate date and the notice date plus the notice period that move carries") does not itself repeat the "before the apartment is surrendered the intended vacate date" substitution.
  - A reader who takes it as the specific rule for transfer notices, and treats the missing vacate date as empty, would get a fee end of notice + period. On task 1's world that is 2026-10-27, which means no charge and a closing amount of 227.50.
  - That reading is excluded by the same rule's earlier general sentence, which explicitly fixes the fee end "before the apartment is surrendered" and is not limited to non-transfer notices. The policy's own trigger also settles the account before surrender, so the projected date is the point of the computation.
  - The dominant reading is unique and agrees with compute, so this is not a RED. It is flagged because a KB rendering that separates the two sentences could make the second reading look defensible.
- **factor_ladders.** Unchanged from round 2: final month has 6 factors (5 param / 1 method), all tiers reachable and distinct. The other computations are unchanged. Pass.

### findings (revision 3)

| id | round-2 class | round-3 status |
| --- | --- | --- |
| N-2 | SOURCE-POLICY RED (latent) | **closed**: the without-notice branch and the vacate-date floor are restored in the declared replacement |
| N-1 | observation | **closed**: declared supersession of the base move_out_notice notice-period sentence |
| F-1…F-8 | closed in round 2 | **still closed**: no regression |
| R3-O1 | — | new observation: the new transfer fee-end sentence omits the pre-surrender substitute stated in the general fee-end sentence; the dominant reading is unique |

### closing_checklist (revision 3)

Written after both round-3 reveals. GT: `0.json` 3e0349b8…, `1.json` fc857f38….

- **Audit files.** `0.md`, `1.md` and `_difficulty.md` each carry `revision_3`. Rounds 1 and 2 are untouched. Both comparison sections carry PASS.
- **Coverage, scope and tools.**
  - All five extended policies are covered: task 0 has {late fee, increase, advance}, task 1 has {final month, closing}.
  - The scopes (whole trees) are pairwise disjoint.
  - Task tools and GT are closed, and the five uuid8s are independent and unchanged.
- **Trees.**
  - Task 0: 2 prerequisites, 2 value_input.
  - Task 1: 1 prerequisite, 1 value_input.
  - Both roots are owner=user tools. The difficulty-wide graph is acyclic.
- **Computations.** Every computation has a self-sufficient baseline and 4–6 factors with ≥2 parameter and ≥1 method:
  - annual increase 4
  - late fee 6
  - advance 4
  - final month 6
  - closing 5

  Every ladder has ≥3 reachable, distinct tiers stated in its rule. Each task has a multi-source factor and a cross-difficulty factor (entrance; assisted), with the other product's rows seeded.
- **Factor weight.** Every factor bears weight on its task's world. Whole-baseline numbers 0, 4279.39, 5195.61, 2513.07 and 185.00 all differ from gold.
- **REDs.** F-1 to F-8 and N-2 are closed, with no regression.
- **Open observations** (not grounds for rework):
  - O-1 to O-7
  - O-9
  - R3-O1: the transfer fee-end sentence omits the pre-surrender substitute; worth watching at the KB render stage.
- **Gates.** Not re-run by me; that is a coordinator step. The coordinator's round-3 snapshot is all OK, with traceability deferred until the KB is published.
- **Difficulty status.** **PASS** on the source-layer audit: policy self-consistency, problem tree, factor weight and unique solution all hold for both tasks.
