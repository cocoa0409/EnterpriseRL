# Policy-task audit — homesite_reservation_holds / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit subagent (Claude, Opus 5.5), independent of the instantiating agent; unattended run.
- Freeze time: 2026-10-04T23:35Z (written before any task GT was revealed; nothing in this section derives from a revealed GT).
- Frozen inputs:
  - `tasks/homesite_reservation_holds/homesite.extended.yaml` sha256 `8ebbffe6cc06822bd912beee0dcdad6f1c8e7d2a799f7d617250ffb058daea72` (matches MANIFEST)
  - `tasks/homesite_reservation_holds/task_tools.py` sha256 `07aaa1cb9d947164473b3fb331b657809a60de268cf77ce7d6130efb61a4898c` (matches MANIFEST)
  - `blueprint/blueprint.yaml`, `blueprint/products/homesite.yaml`, `blueprint/share_tools.py`, `blueprint/db_schema.json` (schema not needed beyond the tables the views carry).
- Fields permitted: the charter in full, the tool module in full, the scenario blueprint; for tasks only the masked views `audits/_views/policy_task/homesite_reservation_holds/{0,1}.view.json` (task_id, frozen_time, user_scenario, initial_state; sha256 a8dc35cc… / c0b12dd7…, both re-hashed and matching MANIFEST).
- Fields masked: evaluation_criteria, computations, db_closure, db_closure_matches_initial_state, design_rationale, prerequisite_closure, solvability_contract, charter_scope, required_documents; `worklog.md`; any other difficulty's tasks; any other scenario.
- Entry conditions (Step 0): gate snapshot supplied in the brief — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, TRACEABILITY NOT OK (declared expected: hidden task-tool names await the rendered KB). Masked views and hashes supplied. Entry conditions met; the TRACEABILITY failure is recorded as an open gate for the closing checklist, not re-run here.
- DSL semantics assumed (not re-derived from the gate scripts, which are outside the read domain): `DAYS(a,b)` = calendar days b−a; `MONTHS` = whole calendar months; `RND` = half-up to the stated places; `LATEST`/`SUM`/`COUNT` scoped to the reservation being written; `CFIELD(cat, field, filters)` = that field on the customer's single matching holding of the other category.

Base-copy check: lines 1–716 of the extended file are byte-identical (modulo trailing blank line) to `blueprint/products/homesite.yaml`; a YAML-level compare of every top-level key (category … policies) is equal. The base copy is verbatim.

### policy_conflict_scan

Six extended policies, two problem trees (derived from the `prerequisite` graph and the rules alone):

| Tree | Root (blocked) with target tool | Prerequisite problems with target tools and edge kind |
| --- | --- | --- |
| A | homesite_ext_extended_hold_term (extend_homesite_hold_1f65db7b, agent) | homesite_ext_activation_hold_term (activate_homesite_hold_ab3aff61, agent) — value_input; homesite_ext_extension_fee_charge (pay_hold_extension_fee_c522f05c, **user**) — state_gate |
| B | homesite_ext_reinstated_hold_term (reinstate_homesite_hold_f9d4ebfd, agent) | homesite_ext_release_premium_refund (sign_homesite_release_13bc71ff, **user**) — state_gate; homesite_ext_reinstatement_fee_charge (record_reinstatement_fee_fa042025, agent) — value_input |

Overlap scan:
- Subjects: activation `[homesite_hold_activated]`; extension fee and reinstatement fee both `[homesite_payment_received]` but disjoint by component (extension_fee vs reinstatement_fee) and by trigger state (held vs expired reservation); extended term `[homesite_hold_extended]`; release `[homesite_released, homesite_refund_issued, homesite_funds_retained]`; reinstated term `[homesite_reinstated]`. No two extended policies compute the same quantity on the same subject.
- Shared inputs read by several policies (completion day, card share of the reservation deposit, warranty owner type/status, closed purchase financing type, letter age, expiry reminders) are each defined by identical wording in each rule that uses them; no two rules define the same input differently.
- Time anchors: all "today"-anchored quantities (days to expiry, letter age at extension/reinstatement, lapse days, release date) are handling-time reads; activation's letter age is anchored on the reservation date, the others on today — stated explicitly in each rule, no conflict.
- Cross-category read boundaries: warranty (owner_type, status, ownership_start_date) and purchase (financing_type with status closed) only; read-only.
- Terminal states: activation → held; extension → held with later expiry; release → released + refund/retained rows; reinstatement → held with new expiry. Compatible.
- One latent cross-policy interaction: the extension fee's booking tier reads "the current hold expiry date", which the activation write changes, and the fee policy declares `prerequisite: []`. Where the two orders straddle a booking threshold the fee would take two values; this is judged per task (task 0) — it does not by itself make a charter defect.
- Base-vs-extended conflicts: see `override_declarations` (findings DG-1, DG-2) and `prerequisite_sentences` (DG-3).

Scope exclusivity / completeness (from the graph, before reveal): tree A = {activation, extension fee, extended term}; tree B = {release, reinstatement fee, reinstated term}. The two trees are disjoint and jointly cover all six extended policies. Whether task 0 claims A and task 1 claims B is checked per task after reveal. Base-only event types of the claim (reservation_created, lot_swapped, converted, funds_applied) carry no extended policy — observation only (the claim is a scope, not a coverage obligation).

### rule_compute_equivalence

Mechanical sweep: every `compute_basis` entry of all six policies is a verbatim substring of its policy's `rule` (whitespace-normalised); every `baseline.rule` sentence is in the `rule` (the release baseline's three sentences are present non-contiguously). Manual sweep, binding by binding:

- **activation_hold_term**: completion day (LATEST deposit row, later of it and LATEST premium-fee row when the class fee > 0) ↔ rule ✓; `start_offset` three branches ↔ the three rule tiers (tier 2's "activated that same day" is compute's `funds_completed_on >= NOW` fall-into) ✓; hold length / lender bonus / letter cut (age reservation-date-anchored, >45 → 3, >30 → 1) / card cut (component reservation_deposit only, convenience fee excluded) ✓; sum then `MN(…, max_total_hold_days)`, no rounding ✓.
- **extension_fee_charge**: four ordered steps ↔ compute; step 1 RND half-up ✓, step 2 RND half-up ✓, step 3 halve-and-ceil / 75 %-and-floor / as-is ✓ (`int()` of the 6-place cent value = floor), step 4 credit and `MX(0, …)` ✓. Tenure "whole calendar months before today" ✓; no coverage → 0 ✓. The rule sentence "a fee of zero needs no payment" has no compute counterpart (it governs whether a payment is taken, not the amount) — see DG-3.
- **extended_hold_term**: current term, extension length, early bonus (≥10 → 2, ≥5 → 1), letter cut (today-anchored, >60 → 2, >45 → 1), card cut, maximum level, maximum offset (reinstatement-fee row → completion day → 0) and `MN(sum, offset+level)` ✓. The "standard … max_total_hold_days" sentences are baseline sentences, implemented by the factor fall-throughs ✓.
- **reinstatement_fee_charge**: discount, combined (not chained) surcharge, timing 1st/2nd/≥3rd day, reminder method (none → pro rata days/window half-up; lead < notice days → halve-and-ceil; else as-is) ✓.
- **release_premium_refund**: window start = later of reserved date and completion day; inside the window (`days_after_window <= 0`) full refund ✓; loyalty/lender/grace sum capped at 100 ✓; refundable share RND ✓; forfeit 0 ext → prorate half-up, 1 ext → prorate floor, never below half, ≥2 → whole ✓. One compute-only detail: "never below half of the unadjusted forfeit" is implemented as `RND(unadjusted_forfeit / 2, 2)` (half-up) while the rule states no rounding for that half — observation O-1 (inert whenever the unadjusted forfeit has an even cent count; inert in this bundle because both trees' releases carry 0 extensions).
- **reinstated_hold_term**: base length by the latest reinstatement-fee payment method (ach/wire/certified 10, card 8, other extension_days), lapse days from end_date, add-back all / ceil-half / none by reminder lead, loyalty, card cut, letter cut (>60 → 2, >30 → 1), no cap ✓.

Result: rule ⇔ compute holds in both directions for every factor ladder (each tier a rule sentence and a branch, each branch a stated tier); only O-1.

### action_binding_and_uuids

- `(target_tool, computes)`: (activate_homesite_hold_ab3aff61, total_hold_days), (pay_hold_extension_fee_c522f05c, amount), (extend_homesite_hold_1f65db7b, total_hold_days), (record_reinstatement_fee_fa042025, amount), (sign_homesite_release_13bc71ff, premium_fee_refund), (reinstate_homesite_hold_f9d4ebfd, hold_days) — each claimed by exactly one policy ✓.
- uuid8s ab3aff61, c522f05c, 1f65db7b, fa042025, 13bc71ff, f9d4ebfd: no shared prefix/suffix, no arithmetic progression, no reuse ✓.
- Tool bodies (task_tools.py lines 44–250): every tool performs an unconditional `ctx.update`/`ctx.create`; none reads status, window, ledger or amount, none errors or hints ✓ (the tool layer judges no prerequisite).
- Docstrings: no other tool named; no sequence position stated. Each write docstring says "Afterwards the reservation shows …" describing that call's own post-state, and `extend_homesite_hold_1f65db7b` reads "Write a hold extension on a held Homesite Reservation" — observation O-2 (the word "held" restates the base state gate the root already carries; "Afterwards" refers to the call's own effect, not to another action; no consequence demonstrable).
- `pay_hold_extension_fee_c522f05c` books exactly one `extension_fee` row; base `homesite_deposit_collection` books a separate `card_convenience_fee` component for any card payment, which no task tool can write — observation O-3 (inert in both tasks: the personas pay by bank transfer).

### prerequisite_graph

| # | Blocked | Problem | kind / gate | form | policy_source verbatim in own rule | resolved_by = problem's target_tool |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | extended_hold_term | activation_hold_term | value_input / `current_term` (binding exists) | state | ✓ | ✓ activate_homesite_hold_ab3aff61 |
| E2 | extended_hold_term | extension_fee_charge | state_gate / `homesite_events.deposit_component` | state | ✓ | ✓ pay_hold_extension_fee_c522f05c |
| E3 | reinstated_hold_term | release_premium_refund | state_gate / `homesite_reservations.status` | state | ✓ | ✓ sign_homesite_release_13bc71ff |
| E4 | reinstated_hold_term | reinstatement_fee_charge | value_input / `fee_paid_by` (binding exists) | state | ✓ | ✓ record_reinstatement_fee_fa042025 |

- `prerequisite` filled on all six policies (four `[]`) ✓; every `problem` is an extended policy id of this file, none base, none self ✓; graph acyclic (two stars of depth 1) ✓; `fallback_reason` absent on all four, correctly (all state form) ✓; no authoring-viewpoint phrasing in any `prerequisite` field ✓.
- `effect` holds: E1 activation rewrites `hold_expiry_date` which `current_term` and `days_to_expiry` read; E4 the fee row's `payment_method` is what `fee_paid_by` reads; E2/E3 create exactly the waited-on ledger row / status.
- `condition` strength: E2, E3, E4 match their sentences. E1's condition adds "and its hold_expiry_date carries the hold term fixed when the hold was activated", which is the effect of the activation, not a further state the sentence names — observation O-4 (no reading changes).
- E2's gate `homesite_events.deposit_component` is a field, not an `eligibility` entry (the extended policy carries none); the gate is the rule's own sentence — acceptable, noted with O-4.

### prerequisite_sentences

Four-point test:

- **E1** "The extended hold term is fixed only after the reservation has left the pending deposit status and stands in held status." — connective *only after* ✓; record-visible state (status) in finder words ✓; no tool/id/snake_case ✓; scope = this reservation ✓. Writes of this difficulty that produce `held`: activate (pending_deposit → held) and reinstate (expired → held); only activation *leaves pending deposit* into held, so exactly one write resolves it ✓. Derivation: sentence → status is pending_deposit → the depended-on rule "When the required funds of a reservation in status pending_deposit are complete, the hold is activated …" → activation write. Single reading ✓.
- **E2** "An extension is not written until an extension fee payment for it stands on the reservation ledger." — *not … until* ✓; ledger row (payment, component extension fee) ✓; no tool ✓. Only `pay_hold_extension_fee_c522f05c` writes an `extension_fee` payment ✓. Derivation: sentence → no extension_fee payment row → fee rule "The extension fee charged for an extension is received from the buyer as one homesite_payment_received row with component extension_fee" → buyer's fee payment. Single reading for any class whose fee is above zero. "for it" is not record-distinguishable from an earlier extension's fee row (no row field ties a fee to an extension) — observation O-5 (inert: no task carries a second extension). For a fee of zero the sentence conflicts with its own policy's rule — finding DG-3.
- **E3** "A lapsed hold is not reinstated until no other reservation of the buyer stands in pending deposit or held status." — *not … until* ✓; status of the buyer's other reservations ✓; open set stated as a set of statuses ✓. Within this difficulty's tools only `sign_homesite_release_13bc71ff` moves a held reservation out of the open statuses (conversion and withdrawal carry no task tool and conversion needs a purchase agreement of another difficulty) ✓. Derivation: sentence → another reservation stands held → release rule "The buyer's signed release of a held homesite is recorded together with the refunds it triggers …" → buyer signs the release. Single reading ✓. The opening clause "Reinstatement is a courtesy for a buyer committed to a single homesite" re-motivates the same gate in other words — observation O-6 (a second wording of the dependency, but it names no state, tool or action; no consequence).
- **E4** "The reinstated hold term is fixed only after a reinstatement fee payment for the lapsed hold stands on the reservation ledger." — *only after* ✓; ledger row ✓. Only `record_reinstatement_fee_fa042025` writes a reinstatement_fee payment ✓. Derivation: sentence → no reinstatement_fee row → reinstatement-fee rule → agent takes the fee. Single reading ✓.
- Depended-on rules do not restate any of the four sentences (mechanically checked) ✓. No rule names another problem's tool or id ✓.
- Undeclared cross-problem orders: none in the extended rules. Base sentences stating cross-problem orders: `homesite_hold_extension` "Extensions are written only on a reservation whose status is held." (activation → extension) — tree A also carries its own E1 sentence, so observation O-7, not RED. The extended root rule's "An extension pushes out the hold of a held reservation" is a second mention of the held state — folded into O-7.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (finding half only; task files demonstrate consequences):

- **activation_hold_term** vs `homesite_reservation_admission`: hold-expiry sentence replaced and declared ✓; the remaining admission sentences govern creation and are untouched ✓. vs `homesite_deposit_collection`: required funds, methods, card fee, payment order, deadline — followed. **"The hold is activated on the day the deposit and premium holding fee components together reach the required funds."** — the extended ladder's first tier ("where they became complete on a day before the activation date, the hold is counted from the activation date") prices an activation on a day *after* the completion day, which this base sentence says does not happen; the sentence is not named in `overwrite` → **DG-1 (undeclared override)**.
- **extension_fee_charge** vs `homesite_hold_extension`: fee sentence replaced and declared ✓; "a fee of zero needs no payment" retained (and restated). vs `homesite_deposit_collection`: methods/caps followed; card convenience fee on a card-paid extension fee cannot be booked by the tool (O-3). vs `homesite_lot_swap`, `homesite_returned_payment`: no sentence touches the fee amount ✓.
- **extended_hold_term** vs `homesite_hold_extension`: "Each extension adds extension_days … refused if …" replaced and declared ✓; max_extensions, held-only, max_extensions = 0, prequal-refresh sentences followed (the refresh sentence's "refreshed letter's date is written with the extension" has no tool argument — inert where `extension_requires_prequal_refresh` is false, observation O-8).
- **reinstatement_fee_charge** vs `homesite_expiry_reinstatement`: fee clause replaced and declared ✓; window, count followed ✓. Other refs: no sentence governs the fee amount ✓.
- **release_premium_refund** vs `homesite_release_refund`: window sentence replaced and declared ✓; after-window percent sentence replaced and declared ✓. **"Days are counted from the day after the reservation date, and a release received on the last counted day is inside the window."** — the extended rule counts "from the day after the window start"; this base sentence is not named in `overwrite` → **DG-2 (undeclared override)**. "Inside the window the premium holding fee is refunded where premium_fee_refundable_within_window is true" → extended "refunded in full" drops the condition; every class sets it true, so no situation gives a different conclusion — observation O-9. Other refs: no sentence governs the release refund amount ✓.
- **reinstated_hold_term** vs `homesite_expiry_reinstatement`: "A reinstated hold runs extension_days …" replaced and declared ✓. vs `homesite_agg_community_premium_cap`: the extended single-hold gate (E3) makes the base clause "Reinstating an expired hold counts as opening it again" vacuous (with no other open reservation a reinstatement never meets a cap); both are necessary conditions, their conjunction is unique, no base sentence grants reinstatement — observation O-10, not RED.

### factor_ladders

| Policy | Factors (effect) | param / method | cross_difficulty | Notes |
| --- | --- | --- | --- | --- |
| activation_hold_term | hold_start (method), hold_length (param), lender_bonus (param), letter_shortening (param), card_shortening (param) | 4 / 1 | warranty, purchase | 5 factors ✓ |
| extension_fee_charge | lender_rate (param), card_surcharge (param), booking_method (**method**), homeowner_credit (param) | 3 / 1 declared, **0 honest** | purchase, warranty | DG-4 |
| extended_hold_term | length, early_bonus, letter, card, maximum_level (params), maximum_start (method) | 5 / 1 | purchase, warranty | 6 factors ✓ |
| reinstatement_fee_charge | lender_discount, card_surcharge, timing_surcharge (params), reminder_method (method) | 3 / 1 | purchase | 4 ✓ |
| release_premium_refund | loyalty, lender_bonus, grace_bonus (params), forfeit_method (method) | 3 / 1 | warranty, purchase | 4 ✓ |
| reinstated_hold_term | base_length, loyalty, card, letter (params), lapse_add_back (method) | 4 / 1 | warranty | 5 ✓ |

Structure checks over all 27 factors:
- Every ladder has 3 tiers, pairwise disjoint as stated; every fall-through equals the factor's `baseline` binding and the policy `baseline.rule` ✓; every tier is a rule sentence and a compute branch ✓; binding sets disjoint within each policy; `decides` is never `result` (reinstatement_reminder_method decides `fee_after_reminder`, which `result` copies — acceptable).
- No two tiers share a value for any class: hold_length 15/12/initial (14,10,7); extension_length 10/8/extension_days (7,5); maximum_level 23/20/max_total (28,17,12,7); loyalty 75/60/after-window pct (0,50,25); base_length 10/8/extension_days; all others distinct constants ✓.
- Method honesty:
  - activation_hold_start, extension_maximum_start: tiers pick a different anchor record (activation date / completion day / reinstatement-fee posting / reservation date) — a genuine change of how the term is counted ✓.
  - reinstatement_reminder_method: pro rata by elapsed days vs halved vs as-is — the pro-rata tier is a different algorithm ✓.
  - release_forfeit_method: prorated vs prorated-with-floor vs whole ✓.
  - reinstated_lapse_add_back: all / ceil-half / none of the lapse days — rate-shaped, but the rule reads it as anchoring the reinstated hold on the expiry date vs the reinstatement date ("nothing is added back; the reinstated hold counts only from the reinstatement date"), the same anchor shape accepted above — observation O-11.
  - **extension_booking_method**: "the total is halved and rounded up to the next cent" / "cut to fee_prompt_keep_pct percent of itself and rounded down to the cent" / "charged as it stands" — one operation (scale the same total) at 50 % / 75 % / 100 %; the only non-numeric difference is the rounding direction attached to each rate. No anchor, base or algorithm changes → **DG-4 (mislabelled method)**.
- Realness of tiers:
  - **activation_hold_length** pays a subsequent-owner Calloway homeowner `activation_resale_owner_hold_days` = 12 while "every other buyer" (strangers included) gets `initial_hold_days` = 14 on Interior and Corner homesites; **extension_maximum_level** caps original buyers at 23 and resale owners at 20 while every other buyer's maximum is `max_total_hold_days` = 28 on Interior and Corner. A loyalty tier that leaves the existing homeowner worse off than a member of the public is not a treatment a builder publishes → **DG-5 (unreal ladder, latent for Cul-de-Sac and above)**.
  - Card shortening / card surcharge factors key the hold term or a fee on how the *reservation deposit* was paid, even where the fee itself is paid by bank transfer — a chargeback-exposure rationale is available, so recorded as observation O-12, not RED.
  - release_forfeit_method's third tier ("more extensions") can only be taken on Interior/Corner reservations (max_extensions 2), which carry no premium holding fee, so it never changes a number — observation O-13.
  - Letter-age tiers above a class's own `prequal_letter_max_age_days` are unreachable for Greenbelt and above — not a defect (no tier is universal).
- Multi-source: the warranty owner-type ∧ status conjunctions sit on one record; genuinely multi-record factors are activation_hold_start (completion day = later of deposit-row and fee-row dates, compared with the activation date and the reservation date), extension_maximum_start (tier 2: no reinstatement-fee row ∧ completion after reservation date), release_grace_bonus (window start from reservation row, deposit rows and fee rows, against the release date), reinstatement_reminder_method / reinstated_lapse_add_back tier 2 (notice row vs reservation's hold expiry date). Tree A has activation_hold_start / extension_maximum_start; tree B has release_grace_bonus ✓.
- Cross-difficulty: tree A reads warranty and purchase (activation, fee, extension); tree B reads warranty and purchase (release, reinstatement fee, reinstated term) ✓.

### findings

- **DG-1 — SOURCE-POLICY RED (undeclared override).** Symptom: activation's tier 1 handles an activation later than the completion day. Root cause: base `homesite_deposit_collection` "The hold is activated on the day the deposit and premium holding fee components together reach the required funds." is not named in `homesite_ext_activation_hold_term.overwrite`, while the extended rule says "where they became complete on a day before the activation date, the hold is counted from the activation date and the activation start offset is the calendar days from the reservation date to the activation date; where they became complete on a day after the reservation date and the hold is activated that same day, the hold is counted from the completion date". Different conclusions in one situation (funds complete day d, activation written day d+1): under the base sentence the activation day is d, so tier 2 applies (offset = d − reserved date); under the extended reading tier 1 applies (offset = d+1 − reserved date). Affected: extended.yaml `homesite_ext_activation_hold_term` (overwrite, rule) vs base `homesite_deposit_collection.rule`. Bears on: **task 0** (demonstration in `0.md`).
- **DG-2 — SOURCE-POLICY RED (undeclared override, latent in this bundle).** Base `homesite_release_refund` "Days are counted from the day after the reservation date, and a release received on the last counted day is inside the window." is not named in `homesite_ext_release_premium_refund.overwrite`; the extended rule says "Days are counted from the day after the window start". Situation: reserved day r, funds complete r+1, Greenbelt (5-day window), release on r+6: base counting → day 6, outside the window (50 % refund path); extended → day 5, inside (full refund). Bears on: task 1's release (demonstrated inert in `1.md`).
- **DG-3 — SOURCE-POLICY RED (latent in this bundle).** `homesite_ext_extension_fee_charge.rule` (and base `homesite_hold_extension`) "a fee of zero needs no payment" vs `homesite_ext_extended_hold_term.rule` "An extension is not written until an extension fee payment for it stands on the reservation ledger." with `pay_hold_extension_fee_c522f05c.amount` "a positive amount". Situation: an Interior or Corner hold (extension_fee_usd 0.00) asks for an extension — the fee rule says extend with no payment; the extension rule says the extension may not be written until a payment row stands, and no positive payment is owed. No task in this bundle sits on a zero fee (task 0 is Cul-de-Sac) — bears on no task's score.
- **DG-4 — SOURCE-FACTOR RED (mislabelled method).** `homesite_ext_extension_fee_charge.factors[extension_booking_method]` is labelled `method` but its tiers apply 50 % / 75 % / 100 % to the same total; the policy then has no honest `method` factor (minimum 1). Bears on: **task 0** (its extension fee computation).
- **DG-5 — SOURCE-FACTOR RED (unreal ladder, latent for this bundle's classes).** `activation_hold_length` (12 < 14 on Interior/Corner) and `extension_maximum_level` (23 and 20 < 28 on Interior/Corner) place Calloway homeowners below the public fall-through. Bears on no task's scored value: task 0 uses both factors on a Cul-de-Sac homesite, where the ladders read 15/12/10 and 23/20/17 (ordered sensibly); task 1's policies do not use them.
- Observations O-1 … O-13 as cited above; none demonstrates a changed scored value in this bundle.

## closing_checklist

Written after both reveals (2026-10-04T23:38Z); everything above this heading was frozen before any reveal and is unchanged.

The difficulty does **not** close: neither task passes all four relationships.

| Task | Policy self-consistency | Problem tree | Factors | Unique solution | Verdict |
| --- | --- | --- | --- | --- | --- |
| 0 (`0.md`) | SOURCE-POLICY RED (DG-1) | PASS | SOURCE-FACTOR RED (DG-4) | derivation = GT; only DG-1's second reading | **RED** |
| 1 (`1.md`) | PASS (DG-2 inert) | PASS | SOURCE-FACTOR RED (T1-1, no near-miss on the release) | PASS | **RED** |

Checklist status:
- Per-task files one-to-one with tasks 0, 1, alongside this file; first revision, nothing to trace. Comparison sections carry RED, not PASS → open.
- Coverage: the six extended policies are claimed exactly once (task 0: activation, extension fee, extended term; task 1: release, reinstatement fee, reinstated term — `charter_scope` of each task matches the tree derived pre-reveal); scopes disjoint; task tools and GT closed; uuid8s independent ✓.
- Trees: each has 2 prerequisite problems, 1 value_input edge, one owner=user write (fee payment / signed release), no cycle; the difficulty graph is two disjoint stars ✓.
- Computations: every baseline self-sufficient and ≠ gold on its world; every factor bears weight (28 of 28 recomputed equal to `factor_sensitivity`) ✓; but DG-4 (fee computation without an honest method), T1-1 (release without a near-miss) and the latent DG-5 (homeowner tiers below the public fall-through on Interior/Corner) are open.
- Latent charter defects with no task consequence in this bundle, still open: DG-2 (undeclared base counting sentence on the release window), DG-3 (zero extension fee vs the fee-payment gate).
- Instantiation-stage gates: snapshot from the brief only (all OK except TRACEABILITY, declared pending the KB render); not re-run on a final form because no final form exists yet.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: erl-task-policy-audit subagent (Claude, Opus 5.5); freeze time 2026-10-05T00:12Z; written before any round-2 task JSON was opened. Revision-1 text above is untouched.
- Inputs re-hashed and matching the round-2 MANIFEST: extended.yaml `7e4daa8b24ec4a4edcf85744d7a51d705877a4e4292aab88146510fb83f92046` (changed from `8ebbffe6…`), task_tools.py `d22d01c6cd1329c1849c5a766ecc2b68f915b20a512f5b3b2a9bccc7ecd84782` (changed from `07aaa1cb…`), 0.view.json `a8dc35cc…` (unchanged), 1.view.json `6c4e4326bc017ee4863bda79e401828c663bd5f7fb95ffc2056eec74c38c9e80` (changed). Both shared inputs changed, so every charter-global section below is **re-derived in full**, not carried forward.
- Gate snapshot (orchestrator, after rework): EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; CACHE-DIFF INFO; TRACEABILITY NOT OK (deferred until the KB is published).
- contamination_disclosure: this auditor read the revision-1 task JSONs (both GTs) in round 1, so the round-2 derivations are not blind to the revision-1 scored values. Where an input is unchanged, the round-2 recomputation may coincide with remembered round-1 GT. The revision-2 task JSONs were not opened before this section and both task sections were frozen. The reworker's closure claims were received as item ids only, and each one was re-checked against the artifacts.
- Base copy: the blueprint `products/homesite.yaml` is unchanged (mtime 2026-10-04 19:44); a YAML-level compare of every base key against the extended file is equal, so the base copy is verbatim.

### What changed (charter and tools), as found by reading

- activation_hold_term: a second `overwrite` names base `homesite_deposit_collection` "The hold is activated on the day the deposit and premium holding fee components together reach the required funds." and replaces it with "The activation date is the day the activation is written, which can fall after the day the required funds became complete when the activation was not written that day." (the replacement sentence now sits in the rule). The hold length is now `initial_hold_days` + 5 (original_buyer, active) / + 2 (subsequent_owner, active) / + 0.
- extension_fee_charge: step 3 is now "taken at the extension booking rate and rounded half up to the cent" (50 / 75 / 100 %), relabelled `parameter` (`extension_booking_rate`). The homeowner credit is now a `method` factor: ≥ 36 months → `fee_monthly_credit_usd` 0.50 per whole month of ownership, rounded half up; 12–35 months → a flat 10.00; otherwise none.
- extended_hold_term: the fee prerequisite sentence now reads "Where the extension fee charged for an extension is above zero, the extension is not written until an extension fee payment for it stands on the reservation ledger." The maximum level is now `max_total_hold_days` + 6 / + 3 / + 0. The opening now reads "An extension pushes out the hold of a reservation" ("held" removed). E1's `condition` is reduced to "status … is held, reached from pending_deposit."
- release_premium_refund: a third `overwrite` names base "Days are counted from the day after the reservation date, and a release received on the last counted day is inside the window." The "where premium_fee_refundable_within_window is true; where it is false, the release is settled as one after the window" condition is restored in the rule, the baseline and the compute `result`. The half-forfeit floor now states "that half rounded half up to the cent".
- reinstated_hold_term: the "Reinstatement is a courtesy for a buyer committed to a single homesite" opening is replaced by a neutral subject sentence.
- task_tools.py: the only change is the `extend_homesite_hold_1f65db7b` docstring, which now reads "Write a hold extension on a Homesite Reservation" ("held" removed). Bodies, signatures, owners and uuid8s are unchanged.

### policy_conflict_scan (revision 2)

The tree shapes are unchanged: A = {activation, extension fee, extended term}; B = {release, reinstatement fee, reinstated term}. They are disjoint and jointly complete. The subject, input-definition, time-anchor, cross-category and terminal-state scans of revision 1 were repeated on the new text, and no new overlap was found. The fee/activation interaction note (the fee's booking tier reads the hold expiry date) still stands as a per-task check.

### rule_compute_equivalence (revision 2)

Mechanical checks: every `compute_basis` entry is verbatim in its rule; every baseline sentence is in its rule; every K-key used in compute is a declared param and every param is used.

Manual sweep of the changed bindings:
- `hold_length` and `maximum_level`: Python precedence gives `(P + K) if … else (…)`, matching the rule.
- `booking_rate_pct` / `fee_after_booking` = RND(total × rate / 100, 2), matching "rounded half up to the cent".
- `homeowner_credit` = RND(months × 0.50, 2) / 10 / 0, matching the three stated tiers.
- release `result` now gates the full refund on `P('premium_fee_refundable_within_window')`, matching the restored sentence. The half-forfeit floor RND matches the new "that half rounded half up to the cent".
- Result: rule ⇔ compute holds in both directions. **O-1 closed.**

### action_binding_and_uuids (revision 2)

The (target_tool, computes) pairs and the six uuid8s are unchanged, unique and independent. The tool bodies are unchanged and unconditional. **O-2 closed**: the extend docstring no longer restates the held state. The "Afterwards …" self-effect wording remains (no consequence). O-3 (no card-convenience-fee row for a card-paid extension fee) is kept, inert in both tasks.

### prerequisite_graph (revision 2)

E1–E4 are unchanged in problem, kind, gate, form and resolved_by. Each policy_source is verbatim in its own rule, and none is restated in the depended-on rule. The graph is acyclic and fallback_reason is correctly absent. **O-4 closed**: E1's condition now matches its sentence. E2's condition carries the "where the extension fee charged is above zero" qualifier, matching the sentence.

### prerequisite_sentences (revision 2)

- E2 "Where the extension fee charged for an extension is above zero, the extension is not written until an extension fee payment for it stands on the reservation ledger." The four-point test passes (*not … until*, a ledger row state, no tool or id). Its applicability qualifier is the depended-on policy's own output, which the reader computes from that rule. Exactly one write produces the state. For a zero fee the gate is vacuous, which agrees with "a fee of zero needs no payment". **DG-3 closed.** O-5 ("for it" is not record-distinguishable from an earlier extension's fee row) is kept, inert.
- E1, E3, E4: the sentences are unchanged and the derivations of revision 1 hold. **O-6 closed**: the "courtesy … committed to a single homesite" second wording is gone. **O-7 addressed within the extended rule**: "An extension pushes out the hold of a held reservation" is now "… of a reservation". The base `homesite_hold_extension` sentence "Extensions are written only on a reservation whose status is held." still states the order, and it cannot change. Tree A carries its own E1 sentence, so this remains an observation (O-7′).

### override_declarations (revision 2)

- **DG-1 closed.** The base activation-day sentence is now named in the overwrite, and its replacement fixes "the activation date is the day the activation is written". The revision-1 second reading (activation day = completion day) is now excluded by the rule's own text. The replacement does not collide with base `funding_deadline`, which constrains when the funds are received, not when the activation is written.
- **DG-2 closed.** The base counting sentence is named and replaced by "Days are counted from the day after the window start …".
- **O-9 closed.** The within-window refund condition is restored, so the extended rule no longer drops it.
- O-8 (refreshed-letter date has no tool argument, inert where refresh is false) and O-10 (the base premium-cap clause on reinstatement is vacuous under the E3 gate; both are necessary conditions) are kept.
- No other base sentence of any `base_policy_refs` entry is handled differently by the new text; the revision-1 sweep was repeated on the changed rules.

### factor_ladders (revision 2)

| Policy | Factors (p = parameter, m = method) | param / method | cross_difficulty |
| --- | --- | --- | --- |
| activation_hold_term | hold_start m, hold_length p, lender_bonus p, letter p, card p | 4 / 1 | warranty, purchase |
| extension_fee_charge | lender_rate p, card_surcharge p, booking_rate p, homeowner_credit **m** | 3 / 1 | purchase, warranty |
| extended_hold_term | length, early_bonus, letter, card, maximum_level p; maximum_start m | 5 / 1 | purchase, warranty |
| reinstatement_fee_charge | lender_discount, card, timing p; reminder_method m | 3 / 1 | purchase |
| release_premium_refund | loyalty, lender_bonus, grace p; forfeit_method m | 3 / 1 | warranty, purchase |
| reinstated_hold_term | base_length, loyalty, card, letter p; lapse_add_back m | 4 / 1 | warranty |

- **DG-4 closed.** `extension_booking_rate` is now honestly a parameter: one total, one rounding rule, three rates (50 / 75 / 100 %). `extension_homeowner_credit` is a genuine method:
  - Tier 1 credit grows with tenure (0.50 × whole months, rounded half up).
  - Tier 2 is a fixed 10.00.
  - Tier 3 is none.
  The tiers are distinct in outcome and monotone (36 × 0.50 = 18.00 > 10.00). Tenure-scaled loyalty credits are a treatment a builder publishes. The fee policy now has 3 parameter / 1 honest method factors.
- **DG-5 closed.** The homeowner tiers are now `initial_hold_days` + 5 / + 2 / + 0 and `max_total_hold_days` + 6 / + 3 / + 0. Every class orders original owner > resale owner > public, and no two tiers share a value (the bonuses are positive constants).
- All ladders still have 3 pairwise-disjoint tiers. The fall-through equals the factor baseline and the policy `baseline.rule` in every factor, including the new ones (booking 100 % = "charged as it stands"; credit 0 = the standard fee, which carries no credit). Every tier is a rule sentence and a compute branch, and the binding sets are disjoint.
- Kept observations: O-11 (lapse add-back is rate-shaped but anchor-read), O-12 (card factors keyed on how the deposit was paid), O-13 (the release forfeit's third tier is reachable only on classes with no premium fee). None demonstrates a changed value.

### findings (revision 2)

- Closed: DG-1, DG-2, DG-3, DG-4, DG-5. Observations O-1, O-2, O-4, O-6, O-9 are closed; O-7 is addressed in the extended rule (O-7′ remains for the base sentence).
- Kept observations (no consequence): O-3, O-5, O-7′, O-8, O-10, O-11, O-12, O-13.
- New charter-global defects: **none found**. No regression in any revision-1 PASS item of the charter-global sections.

### closing_checklist (revision 2)

Written after the revision-2 reveals (2026-10-05T00:13Z). The revision-2 charter-global sections above it were frozen before the reveals and are unchanged.

| Task | Policy self-consistency | Problem tree | Factors | Unique solution | Verdict |
| --- | --- | --- | --- | --- | --- |
| 0 (`0.md` § revision_2) | PASS (T0-1 closed) | PASS | PASS (T0-2 closed) | PASS | **PASS** |
| 1 (`1.md` § revision_2) | PASS | PASS | PASS (T1-1 closed) | PASS | **PASS** |

Checklist:
- **Audit files.** Each task has its own audit file (`0.md`, `1.md`), alongside `_difficulty.md`. Revision 1 is preserved verbatim and revision 2 is appended. Both revision-2 comparison sections carry PASS.
- **Coverage and scope.** All six extended policies are claimed exactly once: task 0 claims activation, extension fee and extended term; task 1 claims release, reinstatement fee and reinstated term. `charter_scope` matches the trees derived before the reveal. The scopes are pairwise disjoint, the task tools and GT are closed, and the uuid8s are independent and unchanged.
- **Problem trees.** Each tree has 2 prerequisite problems, 1 value_input edge and one owner=user write, with no cycle. The difficulty graph is two disjoint stars, so it is acyclic.
- **Computations.** Every computation declares a self-sufficient baseline and 4–6 factors (≥ 2 parameter, 1 honest method). Each task has a multi-source factor and a cross-difficulty factor, both seeded. Every ladder has ≥ 3 tiers stated in its rule, distinct in outcome and ordered as a builder would publish them. All 28 factors bear weight: each was recomputed, and the 28 figures equal `factor_sensitivity`. Every baseline gives a definite number different from gold. Every computation has a genuine near-miss.
- **Charter-global findings.** DG-1 through DG-5 are all closed. Only observations remain: O-3, O-5, O-7′, O-8, O-10, O-11, O-12, O-13, T0-O1, T0-O3, T1-O1, T1-O2 and T1-O3. None demonstrates a changed scored value.
- **Instantiation-stage gates.** I relied on the orchestrator's re-run on the final form; per the skill, the auditor does not run them itself. EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are OK, and CACHE-DIFF is INFO. **TRACEABILITY NOT OK remains open**, deferred until the KB is published; it must be re-run once the rendered KB exists.

Source-layer verdict for this difficulty: all four relationships PASS for tasks 0 and 1. The only open item is the deferred TRACEABILITY gate, which is outside this audit's four relationships.

### timestamp_correction (appended 2026-10-05, no verdict changes)

The freeze times in this file were estimated by the auditor instead of read from the clock. Some of them come after the reveal times, but the order of writing was correct. The clock readings that bound the writes are:
- Round 1: the audit directory was created at 2026-10-04T23:34:44Z. The charter-global section and both task frozen sections were written to disk before the first task JSON was opened; the reveal command printed 2026-10-04T23:38:21Z. The stamps "23:35Z", "23:40Z" and "23:45Z" are therefore wrong. The true freeze window is 23:34:44Z–23:38:21Z.
- Round 2: `date` printed 2026-10-05T00:11:31Z just before the revision-2 charter-global section was written. That section and both task revision-2 frozen sections were on disk before the revision-2 task JSONs were opened, and the reveal command printed 2026-10-05T00:12:59Z. The stamps "00:12Z", "00:14Z" and "00:16Z" are therefore wrong. The true freeze window is 00:11:31Z–00:12:59Z.

The freeze-before-reveal order holds in both rounds, and no derivation was edited after any reveal.
