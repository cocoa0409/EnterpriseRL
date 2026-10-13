# Policy-task audit — host_payouts / charter-global

## charter_global_frozen

- Frozen: 2026-10-07T19:19:38Z (file mtime at freeze), auditor: erl-task-policy-audit (independent auditor; did not write the artifacts), revision r1.
- Freeze hashes (sha256, recomputed by the auditor, equal to the brief's SHA256SUMS):
  - `tasks/host_payouts/payout.extended.yaml` = `7d37d2725df367734d4b44958e3b3136aed590ab09fedccba39c2622a7ffa733`
  - `tasks/host_payouts/task_tools.py` = `44ee71a565333fd842bdb96c2da763fb3cae307717b04d7d28295ae4d7e59558`
- Fields used: `blueprint/blueprint.yaml`, `blueprint/products/payout.yaml` (and spot reads of `host.yaml`, `protect.yaml`, `rewards.yaml` for cross-product consistency), `blueprint/share_tools.py`, the extended charter, `task_tools.py`, the masked views `/tmp/erl45_views/r1/host_payouts/task_{0,1}.view.json` (frozen_time, user_scenario, initial_state only).
- Fields masked and NOT read while this section was written: every `tasks/host_payouts/tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), `tasks/host_payouts/worklog.md`, the scenario `worklog.md`, and every earlier audit. No recursive search was run over `tasks/` or the scenario root.
- Nothing in this section is derived from a revealed GT; it is built from the charter, the schema and the tool contracts alone.

### entry_conditions (Step 0)

- Gate snapshot supplied with the brief (`/tmp/erl45_views/r1/host_payouts/gate_snapshot.txt`): check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cache_diff INFO, check_cross_fire SCOPE OK, check_traceability NOT OK (expected before KB rendering; re-run after step 3 per the brief).
- Masked views supplied with hashes; `sha256sum` of `task_0.view.json` = `0af4343d440512fe9ccf4c90256745b295a6bc66a48e9b1dac849c76ad5fcf2a`, `task_1.view.json` = `c2ea86639c557b8eaf8735877c79d6077d8d10ab1a3c2092717a43afc1406d4b`, as listed in SHA256SUMS — both verified OK.
- Base copy: lines 1–945 of `payout.extended.yaml` are byte-identical to `blueprint/products/payout.yaml` (`diff` empty); `extended_policies:` starts at line 947.
- Entry conditions satisfied; no "incomplete input" finding.

### policy_conflict_scan

Extended policies (5), each with its own target tool:

| policy | trigger | subject | target_tool (owner) | prerequisite |
| --- | --- | --- | --- | --- |
| payout_ext_conversion_fee | state_due | payout_fee_charged (cross_currency_fee) | book_conversion_fee_3c5b00cd (agent) | [] |
| payout_ext_on_request_payout | on_request | payout_sent | send_on_request_payout_d225f921 (user) | conversion_fee (value_input, state form) |
| payout_ext_return_charge | state_due | payout_fee_charged (returned_payout_fee) | book_return_charge_692b7e7b (agent) | [] |
| payout_ext_transfer_fee | state_due | payout_fee_charged (transfer_fee) | book_transfer_fee_e67ff494 (agent) | [] |
| payout_ext_returned_resend | on_request | payout_sent | confirm_payout_resend_90576149 (user) | return_charge, transfer_fee (both value_input, state form) |

- Overlapping subjects: three `payout_fee_charged` policies are separated by `fee_type` (cross_currency_fee / returned_payout_fee / transfer_fee) and by source record (a transfer vs a return record); two `payout_sent` policies are separated by trigger object (an active method's whole balance on request vs the held balance of a method reactivated after a return, naming that return). No two policies decide the same quantity.
- Triggers / time anchors: conversion fee due on the transfer's settlement day; transfer fee due on the settlement day or, for a transfer returned before it settles, on the day of the return; return charge due on the day of the return. These are mutually compatible: a transfer returned before settlement owes a transfer fee and a return charge and no conversion fee ("a transfer returned before it settles carries no conversion fee").
- Eligibility: both payout policies restate the base `payout_evt_transfer` conditions (active method, account not suspended, new-method period passed) — compatible with base.
- Terminal states: each write adds one ledger row; none changes method status.
- Cross-category read boundaries: reads of host (tier, superhost_since, opened_date, business_name, assessments, cancellations), protect (active level, reimbursements paid), listing (quality reviews) and rewards (active level) are read-only; none writes another category.
- Claimed scopes (derived blind from the prerequisite graph, to be confirmed against `charter_scope` at reveal): tree A = {on_request_payout ← conversion_fee}; tree B = {returned_resend ← return_charge, transfer_fee}. The two trees are disjoint and jointly cover all five extended policies.

### rule_compute_equivalence (check 2)

Swept every `compute` binding against its `compute_basis` quotation and back against the rule, policy by policy.

- payout_ext_conversion_fee: every binding has a verbatim basis; the three loyalty discounts are additive and applied once (`conv_discounted`), the settlement ladder is the only rounding (`conv_settled_fee`), the cap applies to the percentage charge alone (`conv_pct_charge`), zero-pct / USD give no fee (`result`). Two implementation approximations (observation O-1): (a) the rule anchors the volume window, the Superhost months, the method months and the account months on "the settlement day", while compute anchors them on `NOW` (the booking day); (b) the rule computes on "the transfer it names", while `conv_amount` is the `LATEST` payout_sent. The two faces coincide whenever the fee is booked on its settlement day for the latest transfer (true on task 0's world, see `0.md`); they diverge for a fee booked late or for an earlier transfer.
- payout_ext_on_request_payout: balance in/out, fresh earnings and claim reimbursements of the request date, the three-tier fresh share, response bonus, claim share, claim multiplier, float ladder and the final `RND(MX(0,…),2)` each match a quoted sentence. `onreq_stays` reads the assessment's `stays_12m`, which `host.yaml` defines as completed stays in the lookback — matches "its completed stays". Observation O-6: the rule says the payout "is rounded half up to the cent once, at the end" while float tier 2 rounds the float itself; not contradictory in effect, never exercised by the tasks.
- payout_ext_return_charge: base by latest return reason, correspondent charge on the latest return's amount, prompt re-verification credit by `DAYS(return date, verified_date)` with "not since the return" mapping to negative days → 0, floor at 0.00, courtesy share by host tier, tenure settlement as the only rounding, `result` 0 on a 0.00-fee rail — all quoted and implemented.
- payout_ext_transfer_fee: percentage part with cap, fixed share by count + business_name, surcharge only on a fixed-fee rail, two additive discounts, outcome settlement as the only rounding — all quoted and implemented; "a transfer fee that works out to 0.00 is not booked" is honoured by the GT shape (no write when result is 0). Same `LATEST` approximation as O-1(b) for `xfee_id/xfee_amount/xfee_sent_date`.
- payout_ext_returned_resend: held balance, return-history reserve with the re-sent return excluded (`resend_returns - 1`), host-initiated cancellations in 12 months, listing quality outcomes in 3 months, additive holdbacks on the held balance, float by method age, final rounding — all quoted and implemented.
- Every `factors[].ladder` tier is a sentence of its rule and a branch of its `decides` binding, and every branch is a stated tier (checked for all 25 factors). No tier lives only in compute.

Conclusion: no SOURCE-POLICY RED from check 2; O-1 and O-6 recorded as observations.

### action_binding_and_uuids (check 3)

- Each `(target_tool, computes=amount)` pair is claimed by exactly one policy (five distinct tools).
- Tool bodies (`task_tools.py`) only `ctx.find` the method for `customer_id` and `ctx.create` one `payout_transactions` row with the given arguments; no eligibility test, no error branch, no hint, no aggregation. No docstring names another tool or carries an ordering word about another action ("whatever stays in the balance waits for the next scheduled run" describes the balance, not a tool sequence).
- uuid8 tails: `3c5b00cd`, `d225f921`, `692b7e7b`, `e67ff494`, `90576149` — pairwise distinct, no common prefix, no sequential or adjacent pattern; consistent with independent generation.
- Owners: the two transfers (`send_on_request_payout_d225f921`, `confirm_payout_resend_90576149`) are `owner="user"` and their docstrings frame them as the host's in-app confirmation, matching both rules ("only when the host confirms it in person in the host app"); the three fee bookings are `owner="agent"`.

PASS.

### prerequisite_graph (check 7)

- `prerequisite` present on all five policies (`[]` on conversion_fee, return_charge, transfer_fee).
- Edges: on_request_payout → conversion_fee; returned_resend → return_charge; returned_resend → transfer_fee. Every `problem` is an extended policy id of this file, none is base, none is self; the graph is acyclic (depth 1, two components).
- `policy_source` of all three edges is verbatim in the blocked policy's own `rule` (whitespace-normalised substring test).
- `form: state` on all three; no `fallback_reason` (correct for state form).
- `kind: value_input` on all three; `gate` names `onreq_balance` / `resend_balance`, both real compute bindings into which the depended-on fee enters (ledger SUM of `payout_fee_charged`).
- `resolved_by` equals the depended-on policy's `target_tool` on all three.
- `condition` vs the sentence it must restate:
  - returned_resend → return_charge: "…has a payout_fee_charged row with fee_type returned_payout_fee whose source_event_id names it, on a rail whose returned_payout_fee_usd is above 0.00" — matches the sentence plus the return-charge rule's "A rail whose returned_payout_fee_usd is 0.00 carries no return charge at all". (See O-2 for the 0.00-charge-on-a-fee-rail corner.)
  - returned_resend → transfer_fee: "…when that fee works out above 0.00" — matches "a transfer fee that works out to 0.00 is not booked".
  - on_request_payout → conversion_fee: **strengthened** — see finding CG-1.
- No authoring-viewpoint phrasing in `prerequisite` fields.

### prerequisite_sentences (check 6)

1. on_request_payout: "An on-request payout is fixed only after every conversion fee falling due on the method's transfers by the request date stands on the method's ledger."
   - Ordering connective "only after" joins the policy's own result ("is fixed") to a waited-on state; the state ("every conversion fee falling due … stands on the method's ledger") is record-visible (`payout_fee_charged` rows naming each transfer) and names no action, performer or tool; no snake_case token, policy id or row id; scope "every … falling due … by the request date" matches the edge.
   - Exactly one write of this difficulty brings a conversion fee onto the ledger: `payout_ext_conversion_fee` ("carries one conversion fee, booked as a cross_currency_fee against that method and naming the transfer it belongs to"). Base `payout_evt_transfer` also describes a cross_currency_fee but has no tool.
   - Derivation: sentence → look for transfers on the method whose settlement day (`processing_business_days` after sending, per the conversion rule) is on or before today and that lack a conversion fee row → the conversion-fee rule says such a transfer "carries one conversion fee … booked once per transfer" → book it. Single reading.
   - The conversion-fee rule does not restate the sentence or mention the on-request payout.
2. returned_resend: "A re-send is not made until the return charge for the returned transfer stands on the method's ledger."
   - "not until"; state = a return charge row naming the return record; record-visible; no tool; exactly one write (`payout_ext_return_charge`, "booked as a returned_payout_fee against the method it was returned to and naming the return record"). The return-charge rule does not restate it.
3. returned_resend: "The re-send amount is fixed only after the returned transfer's own transfer fee stands on the method's ledger."
   - "only after"; state = a transfer_fee row naming the returned payout_sent; exactly one write (`payout_ext_transfer_fee`). The transfer-fee rule does not restate it.
- The resend rule's opening clause "Once a method on hold after a returned transfer has been reactivated" states an order relative to the base lifecycle transition `on_hold → active` (by agent), which has no extended policy and no task tool; it is an eligibility state of the root, not an undeclared problem edge (no extended policy produces it). Recorded only as context; it must hold at the opening of any task using this policy.
- No rule of the charter states another cross-problem order that grounds no declared edge (swept all five rules and the base rules they cite).

PASS except CG-1 (condition strength, check 7).

### override_declarations (check 1, finding half)

Sentence-by-sentence against each `base_policy_refs` entry:

`payout_evt_transfer`
- "Released earnings and credits are transferred to their method after withholding and deductions, in USD or in the method's payout_currency …" — replaced for on-request payout and re-send (both declare it, replaced by the balance-less-holdbacks definition); followed by the three fee policies.
- "A transfer is sent only to an active payout method." / "No transfer is sent while … suspended." / new-method period sentence — followed and restated by both payout policies.
- min / max sentence — not touched; inherited.
- "Each transfer is charged the rail's fee_pct … plus fee_fixed_usd as one transfer_fee" — replaced by transfer_fee (declared).
- "…when the payout currency is not USD, cross_currency_fee_pct (cut to cross_currency_fee_cap_usd where above 0.00) as a separate cross_currency_fee" — replaced by conversion_fee (declared).
- "fees are rounded per fee_rounding and taken from the balance" — replaced by conversion_fee, return_charge and transfer_fee (each declared).
- arrival / cutoff sentence — followed (used to place the settlement day).

`payout_evt_returns_and_reactivation`
- "…and the rail's returned_payout_fee_usd (where above 0.00) is charged once as a returned_payout_fee" — replaced by return_charge (declared).
- "On reactivation the held balance is transferred at the next run." — replaced by returned_resend (declared).
- Return → balance and hold; dormant hold; "A method on hold receives nothing; releases due to it … wait in its balance when it is itself the default"; reactivation only on a later verified_date — followed.

Each declared `superseded_clause` is verbatim in the named base rule and each `replaced_by` is verbatim in the extended rule. No undeclared override found; none of the three disguised forms (anonymous intermediate, 0/1 multiplier, dropped branch) appears: every extra term (handling charge, correspondent charge, surcharge, discounts, credits, holdbacks) acts on a quantity whose base clause is named in `overwrite`. Observation O-3: each `replaced_by` describes only one of the several modifications the extended rule makes to the superseded quantity; the full replacement lives in the extended rule, so the merged semantics stay unique.

### factor_ladders

| policy | factor | effect | decides | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| conversion_fee | conv_volume_corridor_rate | parameter | conv_rate | 3 (1.25 / 1.50 / rail pct) | yes (method payout_currency + transfer ledger) | – |
| | conv_small_transfer_handling | parameter | conv_handling | 3 (0.99 / 0.49 / 0) | no | – |
| | conv_superhost_discount | parameter | conv_superhost_disc | 3 (25 / 10 / 0) | no (one host-account row) | host |
| | conv_rewards_discount | parameter | conv_rewards_disc | 3 (10 / 5 / 0) | no | null (rewards has no difficulty) |
| | conv_long_held_method_discount | parameter | conv_method_disc | 3 (10 / 5 / 0) | no | – |
| | conv_account_age_settlement | method | conv_settled_fee | 3 (½ floor / ¾ ceil / 1 half-up) | no | host |
| on_request_payout | onreq_fresh_earnings_share | parameter | onreq_fresh_share | 3 (90 / 80 / 60) | no (one assessment row) | host |
| | onreq_responsiveness_bonus | parameter | onreq_response_bonus | 3 (10 / 5 / 0) | no | host |
| | onreq_claim_advance_share | parameter | onreq_claim_share | 3 (100 / 50 / 0) | no | protect |
| | onreq_claim_history | parameter | onreq_claim_mult | 3 (0.60 / 0.80 / 1) | no | protect |
| | onreq_float_rule | method | onreq_float | 3 (largest fee / 1 % of pre-float / flat 50) | no | – |
| return_charge | ret_reason_base | parameter | ret_base | 3 (20 / 30 / rail fee) | no | – |
| | ret_correspondent_charge | parameter | ret_intermediary | 3 (6 / 10 / 0) | yes (method currency + return row amount) | – |
| | ret_prompt_reverification_credit | parameter | ret_prompt_credit | 3 (5 / 2.50 / 0) | yes (return row date + method verified_date) | – |
| | ret_segment_courtesy | parameter | ret_share | 3 (0 / 50 / 100) | no | host |
| | ret_account_age_settlement | method | ret_settled | 3 (½ floor / ¾ ceil / 1 half-up) | no | host |
| transfer_fee | xfee_payout_frequency_share | parameter | xfee_fixed_share | 3 (60 / 80 / 100) | yes (ledger count + host business_name) | host |
| | xfee_large_transfer_surcharge | parameter | xfee_surcharge | 3 (7.40 / 3.20 / 0) | partly (rail parameter + ledger amount) | – |
| | xfee_earnings_volume_discount | parameter | xfee_volume_disc | 3 (25 / 10 / 0) | no | – |
| | xfee_hostcover_discount | parameter | xfee_cover_disc | 3 (10 / 5 / 0) | no | protect |
| | xfee_outcome_settlement | method | xfee_settled_fee | 3 (½ half-up / 1 ceil-dollar / 1 half-up) | yes (sent row + return row) | – |
| returned_resend | resend_return_history_reserve | parameter | resend_reserve_pct | 3 (40 / 20 / 0) | no | – |
| | resend_reliability_holdback | parameter | resend_reliability_pct | 3 (6 / 3 / 0) | no | host |
| | resend_listing_quality_holdback | parameter | resend_quality_pct | 3 (5 / 2 / 0) | no | listing |
| | resend_float_rule | method | resend_float | 3 (largest fee / 1 % of pre-float / flat 100) | no | – |

Structure checks:
- Counts per policy: conversion 6 (5 p + 1 m), on-request 5 (4 p + 1 m), return charge 5 (4 p + 1 m), transfer fee 5 (4 p + 1 m), re-send 4 (3 p + 1 m) — all within 4–6, ≥ 2 parameter, ≥ 1 method.
- Binding sets pairwise disjoint within each policy; every `decides` is an intermediate, never `result`.
- Every ladder has three tiers, pairwise disjoint as stated, every tier stated in the rule with its condition and its value/method, every tier implemented in compute; every fall-through equals the policy baseline (`baseline` bindings equal what `baseline.rule` states for that input: rail pct, no handling, no discounts, half-up settlement; std share 60 %, no bonus, no claim advance, ×1, float 50; rail return fee, no correspondent, no credit, whole charge, half-up; full fixed fee, no surcharge, no discounts, half-up; no holdbacks, float 100).
- Baseline self-sufficiency: each `baseline.rule` is a sentence (or two) of its rule and gives a definite number from the records with no factor applied.
- Per tree (task): tree A (conversion + on-request) carries a multi-source factor (`conv_volume_corridor_rate`) and cross-difficulty factors on host and protect; tree B (return charge + transfer fee + re-send) carries multi-source factors (`ret_correspondent_charge`, `ret_prompt_reverification_credit`, `xfee_payout_frequency_share`, `xfee_outcome_settlement`) and cross-difficulty factors on host, protect and listing.
- Label honesty: every `parameter` factor substitutes a number. The four `method` factors: the two float rules genuinely switch algorithm (largest fee ever / percentage of pre-float / flat amount). The two account-age settlements and the outcome settlement switch a multiplier **and a rounding direction**; their `method` label rests on that rounding variation — see CG-2 and CG-3.
- Realism of conditions and outcomes: see findings CG-2, CG-3 (RED) and O-5 (observations).

### findings

**CG-1 — SOURCE-POLICY RED (check 7: `condition` strengthened beyond its prerequisite sentence).** Bears on task 0 (its only edge).
- Symptom: the declared `condition` of the edge `payout_ext_on_request_payout → payout_ext_conversion_fee` demands a cross_currency_fee row in situations where the charter says no conversion fee is owed.
- Root cause: the condition keys only on "when the method's payout_currency is not USD" and on "every payout_sent row … whose settlement day … is on or before the request date", dropping two exclusions the conversion-fee rule states.
- Evidence (verbatim): condition — "Every payout_sent row of the method whose settlement day (processing_business_days business days after its posted_date) is on or before the request date has a payout_fee_charged row with fee_type cross_currency_fee whose source_event_id names it, when the method's payout_currency is not USD." Conversion rule — "Where the rail's cross_currency_fee_pct is 0.00, or the method is paid in USD, no conversion fee is owed at all." and "a transfer returned before it settles carries no conversion fee." Variants: International Wire Transfer and Western Union Cash Pickup have `cross_currency_fee_pct: 0.00` and support MXN/CAD/EUR/GBP.
- Demonstrated consequence: situation — an International Wire Transfer method paid in MXN (e.g. the method `5be66a75-…` of task 1's world) with a settled transfer. Policy sentence + conversion rule: no conversion fee falls due, so "every conversion fee falling due … stands on the ledger" is vacuously true and an on-request payout may be fixed. Condition: no cross_currency_fee row exists for that transfer, so the prerequisite reads unmet — and it can never be met, since the rule forbids the fee. Same divergence for a PayPal CAD transfer returned before settlement. Two conclusions in one situation.
- Affected artifact: `payout.extended.yaml`, `extended_policies[payout_ext_on_request_payout].prerequisite[0].condition`. On task 0's world (PayPal CAD, `cross_currency_fee_pct` 2.00, no returns) the two readings coincide — consequence on that task's scored solution: none (see `0.md`).
- Relation to previous revisions: first audit round.

**CG-2 — SOURCE-FACTOR RED (unreal ladder; method label resting on it): account-age "settlement" by rounding direction.** Bears on task 0 (`conv_account_age_settlement`) and task 1 (`ret_account_age_settlement`).
- Symptom: the two `method` factors select, by the age of the host account, both a multiplier and a rounding direction: "an account open at least conv_tenure_halving_months months pays half of the discounted conversion fee, rounded down to the cent; an account open at least conv_tenure_quarter_months but fewer than conv_tenure_halving_months months pays three quarters of the discounted conversion fee, rounded up to the cent; any other account pays the discounted conversion fee rounded half up to the cent" (identical shape in the return-charge rule with ret_tenure_* keys).
- Root cause: the only part of these ladders that changes *how* the quantity is computed is the rounding direction, and that direction is keyed to customer tenure. The charter's own convention for every rail is `fee_rounding: nearest cent, half up` (all six variants). No payout business publishes a rounding direction that depends on how long the customer's account has been open, and the middle tier — a 25 % loyalty reduction — then rounds against the very customer it rewards. With the charter's single rounding convention, the three tiers are the multipliers 0.50 / 0.75 / 1.00: a `parameter`, not a `method`.
- Demonstrated consequence: the named tier outcomes ("three quarters …, rounded up to the cent" for 36–59-month accounts; "half …, rounded down to the cent" for 60+-month accounts) are treatments no payout business would publish; the `method` count of the conversion-fee and return-charge computations (1 each) rests solely on these factors, so with the unreal rounding variation removed each of those two computations has 0 honest `method` factors (bound: ≥ 1).
- Affected artifact: `payout.extended.yaml` — `payout_ext_conversion_fee` rule (last sentences), `factors[conv_account_age_settlement]`, `compute.conv_settled_fee`; `payout_ext_return_charge` rule, `factors[ret_account_age_settlement]`, `compute.ret_settled`; both `overwrite[1]` entries.
- Relation to previous revisions: first audit round.

**CG-3 — SOURCE-FACTOR RED (unreal ladder): transfer-fee outcome settlement.** Bears on task 1 (`xfee_outcome_settlement`).
- Symptom: tier 2 — "a transfer returned later than xfee_quick_return_days calendar days after it was sent pays the discounted transfer fee in full, rounded up to the next whole dollar"; tier 3 — "a transfer that settled pays the discounted transfer fee rounded half up to the cent".
- Root cause: tiers 2 and 3 charge the same full fee and differ only by an invented rounding rule (ceiling to the whole dollar vs half-up to the cent). No rail or platform publishes a whole-dollar round-up of a transfer fee as its treatment of a transfer that came back late; the charter's own `fee_rounding` is "nearest cent, half up" on every rail.
- Demonstrated consequence: named tier outcome ("the discounted transfer fee in full, rounded up to the next whole dollar") is not a treatment that line of business publishes; and tiers 2 and 3 select the same value up to that invented rounding, so the ladder's three distinct outcomes rest on it.
- Affected artifact: `payout.extended.yaml` — `payout_ext_transfer_fee` rule (settlement sentence), `overwrite[1].replaced_by`, `factors[xfee_outcome_settlement]`, `compute.xfee_settled_fee`.
- Relation to previous revisions: first audit round.

Observations (no demonstrable consequence on either task; not grounds for rework):
- **O-1** rule/compute anchor approximations (conversion fee: settlement day vs `NOW`; conversion and transfer fee: "the transfer it names" vs `LATEST` payout_sent). They coincide on both task worlds; they diverge for a fee booked after its settlement day or for a transfer that is not the latest.
- **O-2** A return charge can compute to 0.00 on a rail whose `returned_payout_fee_usd` is above 0.00 (Professional Host Plus / Enterprise Partner courtesy tier `ret_courtesy_top_pct: 0`, or a credit exceeding base + correspondent charge). Unlike the transfer-fee rule ("a transfer fee that works out to 0.00 is not booked"), the return-charge rule says only that the return "carries one return charge, booked …", and `book_return_charge_692b7e7b` takes "a positive USD amount". For such hosts the re-send's prerequisite sentence ("…until the return charge … stands on the method's ledger") has no defined resolution. Neither task's world reaches it (task 1 is Professional Host, 50 %).
- **O-3** Each `overwrite[].replaced_by` describes only one of several modifications to the superseded quantity (e.g. the conversion fee's handling charge and three discounts are not in its `replaced_by`); the full replacement is in the extended rule, so the merged semantics stay unique.
- **O-4** "the host's active HostCover plan" is singular while a host may hold several active plans at different levels (`CFIELD('protect','variant_name',status='active')` returns one). Not decisive on either world (task 0: one plan; task 1: three plans, all HostCover Premier).
- **O-5** Realism, below the RED bar: a guest-loyalty Rewards tier discounting a host's FX fee (the Rewards charter describes guest benefits only); a discount on the FX fee for the age of the payout method; a halving of the transfer fee for a transfer returned within 10 days; a tenure halving of the conversion fee and return charge stacked on other discounts. Each is conceivable as a platform perk, so none is demonstrated as a treatment no business would publish.
- **O-6** On-request rule: "rounded half up to the cent once, at the end" vs float tier 2 "rounded half up to the cent" — a second rounding on one tier; never exercised.
- **O-7** Authoring-viewpoint phrase in two rules that render to the KB: "so the amount worked out here is the amount the host confirms" (on-request payout, re-send).
- **O-8** Blueprint claims event types (`payout_earnings_released`, `payout_tax_withheld`, `payout_deduction_applied`, `payout_adjustment_credited`, `payout_hold_released`, `payout_method_reactivated`, `payout_routing_updated`, `payout_method_removed`) that no task tool of this difficulty writes; this skill's coverage criterion is the extended policies, all five of which are covered.
- **O-9** Base-internal wording: `payout_agg_routing` "A method that is not active receives no release; its share goes to the default method instead" vs `payout_evt_returns_and_reactivation` "releases due to it go to the default method, or wait in its balance when it is itself the default". Base text, not this difficulty's extension; task 1's ledger follows the second reading and the re-send reads the ledger as booked, so no consequence.

## closing_checklist

Written 2026-10-07 after both reveals; nothing above this heading was changed by the reveals (the only post-reveal edit above is the correction of the `Frozen:` timestamp to the file's actual mtime).

The difficulty does **not** close: the four relationships do not all PASS.

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 (`0.md`) | SOURCE-POLICY RED (CG-1, charter; no scored consequence) | PASS | SOURCE-FACTOR RED (CG-2) | PASS | RED |
| 1 (`1.md`) | PASS | PASS | SOURCE-FACTOR RED (CG-2, CG-3, false sensitivity figure 2.92 vs 2.93) | PASS | RED |

Step 4 items, status:
- Per-task files correspond one-to-one with tasks 0 and 1, `_difficulty.md` alongside; first revision; every comparison section is present — but not every comparison carries a PASS.
- Extended policies fully covered (task 0: conversion_fee, on_request_payout; task 1: return_charge, transfer_fee, returned_resend — matches both `charter_scope` fields); scopes pairwise disjoint across whole trees; task tools and GT closed (each GT write uses its policy's tool); uuid8s independent (§ action_binding_and_uuids). — holds.
- Trees: task 0 has 1 prerequisite problem and 1 value_input edge; task 1 has 2 prerequisite problems and 2 value_input edges; each has its root as the `owner=user` write; no cycle, and the difficulty-wide graph is acyclic. — holds.
- Computations: every computation declares a self-sufficient baseline giving a definite number ≠ gold (13.21 / 557.93 / 25.00 / 15.00 / 22,257.38) and 4–6 factors, each bearing weight on its world; per task ≥ 1 multi-source and ≥ 1 cross-difficulty factor. — **fails** on ladder realism and honest `method` count: CG-2 (conversion fee, return charge) and CG-3 (transfer fee).
- Prerequisite declarations: CG-1 (strengthened `condition` on the on-request edge) — **fails**.
- Re-run of the instantiation-stage gates on a final form: not applicable — no final form exists while the REDs above stand; the gate snapshot audited is the one supplied in the brief.

## revision_2

### charter_global_frozen (r2)

- Re-audit round 2, started 2026-10-07T21:29Z; this section written and frozen 2026-10-07T21:32Z, before any round-2 GT reveal. Auditor: erl-task-policy-audit (same independent auditor as round 1).
- Shared-input hashes: `payout.extended.yaml` = `b019cbefb592b599bd59f6800f5dea1c42c18085f1def5f59a2b00625fe6b4f0` (**changed** from r1 `7d37d272…`) → every charter-global section is re-derived in full below; `task_tools.py` = `44ee71a565333fd842bdb96c2da763fb3cae307717b04d7d28295ae4d7e59558` (unchanged) → § action_binding_and_uuids is carried forward by reference.
- Views: `/tmp/erl45_views/r2/host_payouts/task_0.view.json` `31c82540…a0ba`, `task_1.view.json` `265a15d7…80a4` — both verified against the brief.
- Entry conditions: gate snapshot supplied (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, TRACEABILITY NOT OK — expected before rendering). Base copy: lines 1–945 still byte-identical to `blueprint/products/payout.yaml`.
- Prior exposure disclosure: the auditor read the round-1 GT of both tasks in round 1 (figures recorded in `0.md` / `1.md` round-1 sections). No round-2 task JSON, worklog or rationale has been opened. The round-1 extended text used for the diff below was the auditor's own round-1 tool output, not any task file.
- What changed in the charter (diff r1 → r2, extended section): conversion fee — `conv_account_age_settlement` (method) and `conv_long_held_method_discount` removed; new `conv_volume_window` (method) and `conv_account_tenure_discount` (parameter); single half-up rounding at the end; "it is booked on that day … every count of months below runs to that settlement day"; second `overwrite` dropped. On-request — `onreq_response_bonus_mid_pts` 5 → 4; float tier 2 no longer rounds; "so the amount worked out here" → "the amount the host confirms is the amount set out below"; edge `condition` rewritten. Return charge — `ret_account_age_settlement` removed; correspondent charge now `ret_correspondent_handling` (method: 0.10 % lifting charge on returns ≥ 5,000 / flat 6.00 on returns ≥ 1,000 / none), no longer currency-keyed; "a return charge that works out to 0.00 is not booked"; single half-up rounding; second `overwrite` dropped. Transfer fee — outcome tier 2 becomes "in full with a trace charge of xfee_trace_charge_usd (12.00)"; single half-up rounding; `xfee_cover_top_pct` 10 → 11; second `overwrite` dropped. Re-send — new `resend_conversion_buffer` (parameter: 1.40 % / 1.00 % / 0 of the returned amount by currency); float tier 2 no longer rounds; return-charge edge `condition` adds "when that charge works out above 0.00".

### policy_conflict_scan (r2)

Same five policies, tools and triggers as r1; the new clauses introduce no overlap: the re-send's conversion buffer is a holdback inside the re-send amount, not a fee row, so it does not collide with the conversion-fee policy (which books `cross_currency_fee` rows only on non-zero-pct rails). Scopes (derived blind): tree A {on_request ← conversion_fee}, tree B {resend ← return_charge, transfer_fee}; disjoint, jointly complete.

### rule_compute_equivalence (r2)

- Conversion fee: `conv_method_months` / `conv_window` / `conv_volume` implement "The volume window follows how long the method has been on file … a transfer falls in the window when it was sent less than that many whole months before the settlement day"; `conv_tenure_disc` implements the long-standing account discount; `result = RND(conv_discounted, 2)` implements "rounded half up to the cent once, at the end". O-1(a) is closed by the rule's own stipulation "it is booked on that day … every count of months below runs to that settlement day" (booking day = settlement day = `NOW`). O-1(b) is unchanged: `conv_amount` / `xfee_*` still read the `LATEST` payout_sent for "the transfer it names" (coincides on both worlds).
- On-request: float tier 2 compute now unrounded, matching the rule (O-6 closed).
- Return charge: `ret_correspondent` implements the three-way size rule; `result` returns 0 on a 0.00 charge, matching "a return charge that works out to 0.00 is not booked" (O-2 closed at the policy level).
- Transfer fee: `xfee_outcome_fee` implements half / full + 12.00 / as it stands; `result = RND(…, 2)`.
- Re-send: `resend_returned_amt` = sum of returns on the latest return date ("the amount the returned transfer booked back to the method" — same `LATEST` approximation as O-1(b)); `resend_buffer_pct` by currency; float tier 2 unrounded.
- Every ladder tier of all 25 factors is a rule sentence and a branch of its `decides` binding, and vice versa; every `K()` key is a declared param and every param appears in its rule. PASS.

### action_binding_and_uuids (r2)

Carried forward from r1 by reference: `task_tools.py` hash unchanged (`44ee71a5…`), and the five `target_tool` bindings are unchanged. PASS.

### prerequisite_graph (r2)

Edges, kinds, gates, forms, `resolved_by` unchanged; all three `policy_source` sentences verbatim in their rules (re-tested). Conditions:
- on_request → conversion_fee: now "…whose settlement day … is on or before the request date, and which was not returned before that day, has a payout_fee_charged row with fee_type cross_currency_fee … — required only when the method's payout_currency is not USD and its rail's cross_currency_fee_pct is above 0.00; on any other method no conversion fee falls due and the condition holds as it stands." This matches the sentence read with the conversion rule's "A transfer returned before it settles carries no conversion fee" and "Where the rail's cross_currency_fee_pct is 0.00, or the method is paid in USD, no conversion fee is owed at all." **CG-1 closed.**
- resend → return_charge: adds "when that charge works out above 0.00", matching the new "a return charge that works out to 0.00 is not booked" in the same way the transfer-fee edge already did in r1. Observation O-R2-1: for both edges the prerequisite sentence itself ("…until the return charge … stands on the method's ledger" / "…only after the returned transfer's own transfer fee stands on the method's ledger") is literally unsatisfiable when the charge is 0.00 and therefore not booked; the reader must combine it with the "not booked" clause. Same reading the auditor accepted for the transfer-fee edge in r1; no task world reaches it.
PASS.

### prerequisite_sentences (r2)

Unchanged sentences; four-point test, single resolving write and derivation as in r1 § prerequisite_sentences (re-checked against the r2 rules; the depended-on rules still do not restate them; no new cross-problem order in any rule). PASS.

### override_declarations (r2)

Each policy now declares only the base clause it changes in substance: conversion fee — the cross_currency_fee clause; on-request and re-send — "Released earnings and credits are transferred …" and (re-send) "On reactivation the held balance is transferred at the next run."; return charge — the returned_payout_fee clause; transfer fee — the transfer_fee clause. The r1 declarations of "fees are rounded per fee_rounding and taken from the balance" were dropped, and correctly so: every extended fee now rounds once, half up to the cent, which is the base `fee_rounding: nearest cent, half up`. No undeclared override; O-3 (partial `replaced_by` texts) unchanged.

### factor_ladders (r2)

| policy | factors (effect) | counts p / m | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| conversion_fee | conv_volume_window (method), conv_volume_corridor_rate (p), conv_small_transfer_handling (p), conv_superhost_discount (p), conv_rewards_discount (p), conv_account_tenure_discount (p) | 5 / 1 declared | corridor rate | host (Superhost, tenure) |
| on_request_payout | unchanged five (4 p / 1 m) | 4 / 1 | none | host, protect |
| return_charge | ret_reason_base (p), ret_correspondent_handling (method), ret_prompt_reverification_credit (p), ret_segment_courtesy (p) | 3 / 1 | prompt credit (return row date + method verified_date) | host |
| transfer_fee | unchanged ids; outcome tier 2 now full + trace charge | 4 / 1 | frequency share, outcome | host, protect |
| returned_resend | + resend_conversion_buffer (p) | 4 / 1 | none | host, listing |

All ladders have three pairwise-disjoint tiers stated in the rule; fall-throughs equal baselines; bindings disjoint; every `baseline.rule` sentence is in its rule.

Re-examination of the round-1 RED ladders and of the new ones:
- CG-2 (tenure-keyed rounding): both `*_account_age_settlement` factors are gone; every fee now rounds once, half up, as the charter's `fee_rounding` states. The tenure idea survives in the conversion fee as a plain parameter discount (15 / 8 / 0 %) — a loyalty discount a platform could publish. **CG-2 closed.**
- CG-3 (whole-dollar round-up): tier 2 is now "the discounted transfer fee … in full with a trace charge of 12.00" for a transfer "traced and recalled through the correspondent banks"; recall/trace charges on late-returned wires are real-world practice, and the three tiers now differ in operation (halve / add a charge / leave as is) and in value. **CG-3 closed.**
- `ret_correspondent_handling` (new method): proportional lifting charge (0.10 % of the returned amount) vs flat correspondent charge vs none — a genuine change of formula (proportional vs fixed), and lifting charges on large returned wires are real practice. Honest.
- `resend_conversion_buffer` (new parameter): an FX buffer by payout currency on a re-sent cross-border amount — real practice; honest parameter.
- **`conv_volume_window` (new method) — mislabelled; see finding CG-4.**

### findings (r2)

**CG-4 — SOURCE-FACTOR RED (mislabelled effect): `conv_volume_window` is a parameter labelled `method`.** Bears on task 0.
- Symptom: the conversion fee's only `method` factor selects "conversion volume is measured over the conv_window_long_months (12) / conv_window_mid_months (6) / conv_window_std_months (3) whole months before the settlement day" by how long the method has been on file.
- Root cause: all three tiers run the same computation — the sum of the method's transfers sent less than N whole months before the settlement day — and differ only in the number N substituted into it (`SUM(…, within_months=conv_window, …)`). A tier that "only substitutes a different number into the same formula (a rate, a fee, a threshold)" is a `parameter`; a lookback length is exactly such a number. (Secondary: volume-tier pricing in payments is measured over a fixed published period; keying the period's length to the age of the payout method is not a treatment a provider publishes — recorded as supporting context, not as the ground of the RED.)
- Demonstrated consequence: with this label corrected the conversion-fee computation has 6 parameter factors and 0 `method` factors (bound ≥ 1). The factor does bear weight on task 0 (see `0.md` revision_2), so the defect is the label, not decoration.
- Affected: `payout.extended.yaml` `payout_ext_conversion_fee.factors[conv_volume_window].effect` (and the computation's method count).
- Relation to r1: new in r2; it replaces CG-2 as the reason the conversion fee lacks an honest `method` factor.

Round-1 charter findings status: CG-1 closed; CG-2 closed (replaced by CG-4 for the conversion fee's method count; closed outright for the return charge, whose new method factor is honest); CG-3 closed. Observations: O-1 (a) closed / (b) unchanged; O-2 closed; O-3 unchanged; O-4 unchanged; O-5 partly addressed (method-age FX discount and tenure halving gone; Rewards guest-tier FX discount and half transfer fee on a quick return remain — still below the RED bar); O-6 closed; O-7 changed — the phrase is now "the amount the host confirms is the amount set out below", which still refers to the document's own layout ("below") but no longer to the author's working; observation only; O-8, O-9 unchanged. New: O-R2-1 (above).

### closing_checklist (r2)

Written 2026-10-07 after both r2 reveals (21:33:26Z); the r2 charter-global sections above were frozen before them.

| task | policy self-consistency | problem tree | factors | unique solution | r2 verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS (CG-1 closed) | PASS | SOURCE-FACTOR RED (CG-4) | PASS | RED |
| 1 | PASS | PASS | PASS (CG-2, CG-3, false figure closed) | PASS | PASS |

- Round-1 REDs: CG-1 closed; CG-2 closed (return charge outright; conversion fee's tenure rounding gone, but see CG-4); CG-3 closed; task-1 false sensitivity figure closed.
- Reworker claims verified: changed — CG-1 ✓, CG-2 ✓, CG-3 ✓, false figure ✓, O-1 partly (a closed, b unchanged), O-2 ✓, O-5 partly, O-6 ✓, O-7 changed but still document-relative ("set out below"), O-T0-1 ✓, O-T0-2 ✓, O-T0-3 ✓, O-T1-1 ✓, O-T1-3 ✓; no change claimed — O-3, O-4, O-8, O-9, O-T1-2 confirmed unchanged.
- New in r2: CG-4 (SOURCE-FACTOR RED, task 0); observations O-R2-1, O-R2-2.
- Coverage, scope disjointness, tool closure, uuids, tree shapes (1 and 2 prerequisite problems, all value_input, user-owned roots), acyclicity: hold.
- Difficulty does **not** close: CG-4 stands. Gate re-run on a final form: not applicable until it is resolved; the audited gate snapshot is the coordinator's r2 snapshot.

## revision_3

### charter_global_frozen (r3)

- Re-audit round 3, started 2026-10-07T21:46Z; this section frozen 2026-10-07T21:47:38Z, before any round-3 GT reveal. Same auditor.
- Hashes: `payout.extended.yaml` = `c23f9f56c3b47de8eff269510d071d1efea5d325c4016b3314bc67b2690f2420` (**changed** from r2 `b019cbef…`) → charter-global sections re-derived; `task_tools.py` `44ee71a5…e7d59558` unchanged → § action_binding_and_uuids carried forward. Views: task 0 `03e7b3fb…a49036a8` (changed), task 1 `265a15d7…80a4` (**unchanged** from r2). Gate snapshot supplied (all OK except TRACEABILITY, expected). Base copy still byte-identical to `blueprint/products/payout.yaml`.
- Prior exposure: the auditor has read the r1 and r2 GT of both tasks (recorded in earlier revisions). No r3 task JSON or worklog opened before this freeze.
- Diff r2 → r3 (extended section): **conversion fee only** in substance — `conv_volume_window` (method) removed and the volume window fixed at `conv_volume_window_months: 12`; the small-transfer handling parameter replaced by `conv_charge_structure` (method): below 250.00 a flat 4.00 replaces the percentage charge; 250.00–999.99 the greater of the capped percentage charge and a 9.00 minimum; 1,000.00 or more the capped percentage charge as it stands; `conv_long_held_method_discount` (10 / 5 / 0 %) reinstated, so four additive loyalty discounts. On-request and re-send — wording only: "the amount the host confirms is the amount this rule gives" (O-7). Return charge, transfer fee, prerequisite fields, edges, conditions: unchanged.

### rule_compute_equivalence (r3)

Conversion fee: `conv_volume` sums transfers "sent to the method less than conv_volume_window_months whole months before the settlement day"; `conv_charge` implements the three-way size rule; `conv_method_disc` implements the long-held method discount; `conv_discounted` = charge × (100 − four discounts) / 100; `result` rounds half up once. Every tier of all factors is a rule sentence and a compute branch and vice versa; every `K()` key declared, every param used and stated. Other policies unchanged from r2. O-1(a) still closed by "it is booked on that day … every count of months below runs to that settlement day"; O-1(b) unchanged. PASS.

### prerequisite_graph / prerequisite_sentences / override_declarations (r3)

Unchanged from r2 (texts identical; all three `policy_source` sentences re-tested verbatim; the on-request edge condition still matches sentence + conversion rule — CG-1 stays closed; the sole conversion `overwrite` names the cross_currency_fee clause and its `replaced_by` is verbatim in the r3 rule). PASS.

### factor_ladders (r3)

Conversion fee: `conv_volume_corridor_rate` (p, multi-source), `conv_charge_structure` (**method**), `conv_superhost_discount` (p, host), `conv_rewards_discount` (p), `conv_long_held_method_discount` (p), `conv_account_tenure_discount` (p, host) — 5 p / 1 m, bindings disjoint, three tiers each, fall-throughs = baseline (rail pct; percentage charge as it stands; no discounts).
- `conv_charge_structure` label: flat amount in place of the percentage / maximum of the percentage and a minimum / the percentage alone — three different formulas (constant, floor-max, proportional), not one formula with a substituted number. Honest `method`.
- Realism: flat fees on very small conversions and a minimum charge on mid-size ones are standard FX/remittance pricing; the 4.00 → 9.00 step at 250.00 is an upward band step, as in published tiered fee tables. Long-held method discount returns as a parameter (O-5 remainder, below the RED bar as in r1).
Other four policies: unchanged from r2 (`ret_correspondent_handling`, `xfee_outcome_settlement`, both float rules remain honest methods).

### findings (r3)

- **CG-4 closed**: the mislabelled `conv_volume_window` is gone; the conversion fee's method slot is now `conv_charge_structure`, an honest method.
- CG-1, CG-2, CG-3: remain closed (texts unchanged since r2 for the parts concerned; the reinstated method discount is a plain parameter).
- O-7 closed ("the amount this rule gives" refers to the rule itself, no layout or authoring reference).
- No new charter-global defect found. Observations carried unchanged: O-1(b), O-3, O-4, O-5 remainder (Rewards guest-tier FX discount, method-age FX discount, half transfer fee on quick return), O-8, O-9, O-R2-1, O-R2-2.

### closing_checklist (r3)

Written 2026-10-07 after the r3 reveals (21:48:12Z); the r3 charter-global sections above were frozen before them.

| task | policy self-consistency | problem tree | factors | unique solution | r3 verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS (CG-4 closed) | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS | PASS |

- Per-task files `0.md`, `1.md` correspond one-to-one with tasks 0 and 1, `_difficulty.md` alongside; revisions r1, r2, r3 preserved in order; every r3 comparison carries a PASS.
- Extended policies fully covered (task 0: conversion_fee, on_request_payout; task 1: return_charge, transfer_fee, returned_resend — matches both `charter_scope`s); scopes disjoint across whole trees; task tools and GT closed; uuid8s independent and frozen (tools unchanged since r1).
- Trees: task 0 — 1 prerequisite problem, 1 value_input edge; task 1 — 2 prerequisite problems, 2 value_input edges; both roots `owner=user`; difficulty-wide graph acyclic.
- Computations: every computation has a self-sufficient baseline giving a definite number ≠ gold (13.19, 556.65, 25.00, 15.00, 22,254.31) and 4–6 factors with ≥ 2 parameter and ≥ 1 honest method; every ladder three tiers, stated in full in its rule, distinct in outcome, with conditions and outcomes that payout businesses actually use; every factor bears weight on its world; per task ≥ 1 multi-source and ≥ 1 cross-difficulty factor with seeded rows.
- Round-by-round RED ledger: r1 CG-1, CG-2, CG-3, task-1 false figure → closed in r2; r2 CG-4 → closed in r3. Open observations (not grounds for rework): O-1(b), O-3, O-4, O-5 remainder, O-8, O-9, O-R2-1, O-R2-2, O-T1-2.
- Gates on the final form: the coordinator's r3 snapshot on this exact charter (`c23f9f56…`) and tools (`44ee71a5…`) — EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; CACHE-DIFF informational; TRACEABILITY NOT OK pending the KB render (step 3), to be re-run after rendering per the coordinator.

**The host_payouts difficulty passes the source-layer audit at revision_3.**
