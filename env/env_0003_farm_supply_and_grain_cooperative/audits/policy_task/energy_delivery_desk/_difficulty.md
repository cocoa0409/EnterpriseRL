# Policy-task audit — energy_delivery_desk / charter-global

## charter_global_frozen

- freeze time: 2026-09-18T09:14Z (pre-reveal; nothing below this heading is derived from any revealed GT field)
- auditor: independent policy-task auditor (did not write these artifacts)
- frozen inputs and their hashes (sha256[:16]):
  - `env/env_0003_farm_supply_and_grain_cooperative/tasks/energy_delivery_desk/energy.extended.yaml` = `3b3b4e6878f41596`
  - `env/env_0003_farm_supply_and_grain_cooperative/tasks/energy_delivery_desk/task_tools.py` = `88bb62f34b07e353`
- fields permitted: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`,
  `blueprint/products/energy.yaml` (and the cross-category charters `grain.yaml`, `agronomy.yaml` for the
  cross-category reads only), the whole of `energy.extended.yaml` (base section + `extended_policies`:
  `rule`, `compute`, `compute_basis`, `overwrite`, `prerequisite`, `factors`, `baseline`, `inputs`),
  the whole of `task_tools.py`, and per task only `frozen_time` / `user_scenario` / `initial_state`
  through the orchestrator's masked views
  (`masked/r1/energy_delivery_desk/0.json` sha256[:16] `ba402ad8cee3e5e8`,
   `masked/r1/energy_delivery_desk/1.json` sha256[:16] `c4fe51488779c218`).
- fields explicitly masked and unread until both tasks were frozen: `evaluation_criteria`, `computations`,
  `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`,
  `db_closure`, `db_closure_matches_initial_state`.
- entry conditions (Step 0): the brief carried the instantiation-stage gate snapshot with its actual output
  lines (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding,
  check_cross_fire — all green, run by the orchestrator at 2026-09-18T09:06), the masked views with their
  hashes and the view division. `check_traceability` was deliberately not run (needs the step-3 KB).
  **Entry conditions complete.** The gates were not re-run by this auditor. A green gate is the qualification
  to enter this audit, not a proof of correctness.

### policy_conflict_scan

Scope of the scan: the 10 base policies of `products/energy.yaml` (copied verbatim into
`energy.extended.yaml` lines 700–1029 — `diff` against the blueprint shows no difference other than a
trailing blank line, so the base copy is verbatim compatible) together with the 7 extended policies.

Subjects / target tools / computed quantities (each `(target_tool, computes)` pair claimed once — see
`action_binding_and_uuids`):

| policy | subject | computes | target_tool |
| --- | --- | --- | --- |
| energy_ext_protection_floor_credit | energy_price_protection_credited | protection_credit_usd | record_price_protection_credit_43e8349b |
| energy_ext_budget_year_reconciliation | energy_budget_installment_billed | reconciliation_amount_usd | bill_budget_plan_reconciliation_cfd56d13 |
| energy_ext_account_clearance_payment | energy_payment_posted | payment_amount_usd | post_energy_account_clearing_payment_6fe49ac6 |
| energy_ext_prebuy_booking_credit | energy_contract_gallons_booked | booked_gallons | lodge_contract_gallon_booking_8fcb503b |
| energy_ext_contract_price_of_record | energy_account_updated | contract_price_per_gallon | update_contract_price_of_record_9db7726a |
| energy_ext_undrawn_gallons_disposition | energy_contract_gallons_drawn | undrawn_settlement_usd | settle_undrawn_contract_gallons_1dbcf678 |
| energy_ext_closure_settlement | energy_account_closed | closing_balance_usd | close_energy_account_7515982f |

Scopes of the M tasks (derived from the prerequisite graph, not from any masked field): the graph has two
components — `{energy_ext_account_clearance_payment → energy_ext_protection_floor_credit,
energy_ext_budget_year_reconciliation}` and `{energy_ext_closure_settlement →
energy_ext_undrawn_gallons_disposition → energy_ext_contract_price_of_record →
energy_ext_prebuy_booking_credit}`. The two components are **pairwise disjoint** and **jointly complete**
(3 + 4 = all 7 extended policies). No policy appears in both.

Conflicts found across overlapping subjects (see `findings` F1–F5 for the full write-ups). Summary:

- **energy_pricing (base) vs energy_ext_protection_floor_credit** — both fix "the posted price for the
  product"; base says rack + *the programme's margin*, the extended policy says rack of record + *the margin
  allowed on the account* (the programme's margin less a volume relief). `energy_pricing` is not in that
  policy's `base_policy_refs`, so the deviation cannot even be declared there. **CONFLICT (F1).**
- **energy_payments_and_arrears (base) vs energy_ext_account_clearance_payment** — base fixes both the late
  charge ("the programme's late charge once") and the arrears rate ("then the programme's monthly service
  charge"); the extended policy gives both different values through its `lapsed_plan_late_charge` and
  `secured_arrears_rate` ladders, and its `overwrite` names only the *due-date* sentence. **CONFLICT (F2, F3).**
- **energy_contract_gallons_program (base) vs energy_ext_undrawn_gallons_disposition** — base: "A member who
  wants out of a booking before the gallons are drawn pays the programme's cancellation charge per gallon
  cancelled"; the extended policy applies the programme's charge *less* a relief, and its `overwrite` names
  only the unused-gallons-treatment sentence. **CONFLICT (F4).**
- **energy_lifecycle_progression (base) vs energy_ext_closure_settlement** — base: "A member closes an account
  of their own accord with nothing owing" (and `params.closure_requires: [zero_balance, ...]`); the extended
  policy computes a closing balance and the `owner=user` close tool writes it onto the account as what is
  owed. `overwrite: []`. **CONFLICT (F5).**
- Time anchors: base `energy_payments_and_arrears` anchors the due date on the invoice date; the extended
  clearance policy re-anchors it on the most recent payment posted. **Declared** in that policy's `overwrite`
  — no conflict.
- Triggers / eligibility / objects / cross-category read boundaries: `trigger` is `state_due` on five
  policies and `on_request` on the two the customer asks for; each policy's `cross_category` block matches
  the categories its `compute` reads (`grain` for policies 1–3, `agronomy` for policies 4–7) and matches
  `inputs.cross_category`; no policy reads a category it does not declare. No conflict.
- Terminal states: the only lifecycle-moving write is `close_energy_account_7515982f`
  (active → closed), which base `lifecycle.transitions` allows `by: user`. Consistent apart from F5.

### rule_compute_equivalence

Check 2 was run sentence by sentence over all seven extended policies, in both directions. Every quantity,
window, filter, tier, branch, cross-category read, acting base, cap/floor, rounding mode and rounding point
in each `rule` has a verbatim `compute_basis` quotation and a restricted expression in `compute`; and every
`compute` binding is covered by a `compute_basis` quotation drawn from its own `rule`. The sweep back found
no binding whose basis is absent from the rule.

Two systematic defects:

- **O1 (observation) — compute's final `else` is broader than the rule's third tier in six ladders.** In
  `rack_of_record_anchor`, `account_margin_relief`, `prior_protection_offset` (energy_ext_protection_floor_credit),
  `prior_use_measure` (energy_ext_prebuy_booking_credit), `lapsed_plan_late_charge`
  (energy_ext_account_clearance_payment) and `volume_price_adjustment` (energy_ext_contract_price_of_record)
  the three tiers the `rule` states do not exhaust the space, while the `compute` conditional ends in an
  unconditional `else`. Example, `account_margin_relief`: the rule's tiers are
  "reach the high-volume gallons **and** the gallons drawn reach the volume drawdown gallons",
  "reach the mid-volume gallons and fall under the high-volume gallons", "fall under the mid-volume gallons";
  a member at 2 000 gallons taken with 400 gallons drawn satisfies none of the three, while
  `posted_margin`'s `else` silently gives them the programme's margin. The rule therefore makes no promise
  in that region and `compute` supplies a basis of its own there. **Neither task's world lands in any of
  these regions** (task 0 takes tier 1 of all three of its gapped ladders; task 1 takes tier 1 of both of
  its), so no consequence is demonstrable on this difficulty and this is recorded as an observation, not a
  red light. The one exception where a consequence *is* demonstrable is F6 below.
- **O2 (observation) — `baseline.params` naming keys the baseline rule does not use.**
  `energy_ext_budget_year_reconciliation.baseline.params` lists `finance_charge_monthly_pct`, but its
  baseline rule says "The rate the difference bears is nothing", so no rate parameter is read.
  `energy_ext_contract_price_of_record.baseline.params` lists `price_protection_fee_per_gallon_usd` and
  `posted_price_margin_per_gallon_usd`, but its baseline rule says "Nothing is loaded onto the average for
  downside protection" and arrives at the posted price of record from "the price billed on the most recent
  stop the member called in", never from a margin. In both cases the baseline rule still yields a definite
  number, so no consequence follows; recorded as an observation.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair in the table above is claimed by exactly one policy; no tool is shared
  and no computed quantity is claimed twice. PASS.
- Subjects, base refs, target tool, docstring and terminal state admit one business reading per policy; no
  confirmation, review, wait or procedure outside the policy is added by any docstring. PASS.
- No docstring states an action's position in a sequence, names another tool, or carries an ordering word.
  The only occurrences of "then" are "from then on" in
  `lodge_contract_gallon_booking_8fcb503b` and `update_contract_price_of_record_9db7726a`, both describing
  the state of the account *after* that one write, not an order between writes. `post_energy_account_
  clearing_payment_6fe49ac6`'s "the oldest energy invoice standing unpaid" names an allocation rule inside
  the same write, not a sequence. PASS.
- uuid8s: `43e8349b`, `cfd56d13`, `6fe49ac6`, `8fcb503b`, `9db7726a`, `1dbcf678`, `7515982f`. All seven are
  distinct, none shares a prefix or a tail with another, none is a sequence number or an adjacent value of
  another, and none looks batch-derived from a common stem. PASS.
- Tool-layer neutrality (bears on check "the tool layer judging the prerequisite"): every function body in
  `task_tools.py` is a bare `ctx.find` + `ctx.create`/`ctx.update` + a confirmation string. None raises,
  refuses, branches on a policy condition, or emits a hint. PASS.

### prerequisite_graph

Five edges, all `kind: value_input`, all `form: state` (no `fallback_reason` present or needed):

| blocked policy | problem (depended on) | gate | resolved_by | acyclic |
| --- | --- | --- | --- | --- |
| energy_ext_account_clearance_payment | energy_ext_protection_floor_credit | `credits_allowed` | record_price_protection_credit_43e8349b | yes |
| energy_ext_account_clearance_payment | energy_ext_budget_year_reconciliation | `instalments_billed` | bill_budget_plan_reconciliation_cfd56d13 | yes |
| energy_ext_contract_price_of_record | energy_ext_prebuy_booking_credit | `booked_gal` | lodge_contract_gallon_booking_8fcb503b | yes |
| energy_ext_undrawn_gallons_disposition | energy_ext_contract_price_of_record | `settlement_price` | update_contract_price_of_record_9db7726a | yes |
| energy_ext_closure_settlement | energy_ext_undrawn_gallons_disposition | `amount_standing_d` | settle_undrawn_contract_gallons_1dbcf678 | yes |

- `prerequisite` is filled in on all seven policies (`[]` on the four that have none). PASS.
- Every `problem` points at another extended policy id in this file; none points at a base policy or at
  itself. PASS.
- The whole graph is a DAG (two disjoint trees, no back edge, no cross-task edge). PASS.
- Every `gate` names a binding that genuinely exists in the blocked policy's `compute`
  (`credits_allowed`, `instalments_billed`, `booked_gal`, `settlement_price`, `amount_standing_d` are all
  present), and `kind: value_input` matches: each gate is a value that enters the blocked computation, not
  an eligibility flag. PASS.
- `resolved_by` is in every case the depended-on policy's own `target_tool`, and each named tool genuinely
  changes the gate binding's value (verified by running the blocked policy's `compute` with and without the
  depended-on write on each task's world — the per-task files carry the figures). PASS.
- `condition` is neither strengthened nor weakened relative to the `policy_source` sentence, with one
  wording slip recorded as **O3 (observation)**: on edge
  `energy_ext_account_clearance_payment ← energy_ext_protection_floor_credit` the `condition` adds
  "for the period being measured", which the `policy_source` sentence does not carry; the sentence as
  written ("carries the downside protection credit owed on every pre-buy booking whose protected floor stood
  above the posted price") would already be satisfied by any earlier credit line on such a booking.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears anywhere
  in any `prerequisite` block. PASS.

### prerequisite_sentences

Four-point test on each of the five `policy_source` sentences. All five are verbatim locatable in the
**blocked** policy's own `rule` (confirmed by exact substring match against the rule text).

1. `energy_ext_account_clearance_payment`: "The amount that clears the account is fixed only after the
   account carries the downside protection credit owed on every pre-buy booking whose protected floor stood
   above the posted price."
   — ordering connective "only after"; what it waits on is a record-visible state ("the account carries the
   downside protection credit …") in the words the energy account activity uses, with no performer and no
   tool; no tool name, policy id, snake_case token or row id; strength matches the edge (see O3).
   **Derivation to a single reading:** the only write in this difficulty that puts an
   `energy_price_protection_credited` line on an energy account is
   `record_price_protection_credit_43e8349b`, which `energy_ext_protection_floor_credit` owns; no other
   policy's `subject` or tool produces that state. One reading. PASS.
2. `energy_ext_account_clearance_payment`: "Before the amount that clears the account is worked out, the
   account must carry the true-up entry owed for every budget plan year that has passed its reconciliation
   date." — "Before"; state form; the only write producing a true-up line among the instalments is
   `bill_budget_plan_reconciliation_cfd56d13`. One reading. PASS.
3. `energy_ext_contract_price_of_record`: "The contracted price of record is written only after the gallons
   standing to the member's credit take in every signed pre-buy request registered with the energy desk."
   — "only after"; state form (booked gallons standing to the member's credit); the only write that credits
   booked gallons is `lodge_contract_gallon_booking_8fcb503b`. One reading. PASS.
4. `energy_ext_undrawn_gallons_disposition`: "The money applied against a booking on the gallons standing
   undrawn is worked out only after the account's contracted price of record stands at a price worked out
   from the bookings the account carries." — "only after"; state form (the contracted price carried on the
   account); the only write that rewrites it is `update_contract_price_of_record_9db7726a`. One reading. PASS.
5. `energy_ext_closure_settlement`: "The balance the account closes at is fixed only after the account
   carries, for every booking whose gallons stand undrawn, the money applied against it when those gallons
   are released." — "only after"; state form; the only write that applies money against a booking on
   released gallons is `settle_undrawn_contract_gallons_1dbcf678`. One reading. PASS.
   (Whether that state is *unmet at the opening* is a per-task question and is answered in `1.md`.)

- The state form is used on all five edges; no `fallback_reason` appears anywhere, correctly.
- No rule carries a second wording of the same dependency, another problem's tool name, another policy id,
  or an aggregated chain. Each depended-on policy's own rule does **not** restate the sentence (checked:
  `energy_ext_protection_floor_credit`, `energy_ext_budget_year_reconciliation`,
  `energy_ext_prebuy_booking_credit`, `energy_ext_contract_price_of_record` and
  `energy_ext_undrawn_gallons_disposition` carry no sentence about what waits on them). PASS.
- Cross-problem orders stated in a rule but grounding no declared edge: none found in the extended rules.
  One **base** rule sentence states a cross-problem order — `energy_lifecycle_progression`: "where contracted
  gallons stand undrawn they are dealt with under the programme's unused gallons treatment before the
  account can close". Because `energy_ext_closure_settlement`'s own rule carries its own prerequisite
  sentence (#5 above), this is recorded as **O4 (observation)**, not a red light.

### override_declarations

Check 1, once over all seven extended policies, sentence by sentence against each `base_policy_refs` entry.
Findings only; the consequence of each is demonstrated in the task file named.

| extended policy | base ref | base sentences followed | base sentences handled differently | declared in `overwrite`? |
| --- | --- | --- | --- | --- |
| energy_ext_protection_floor_credit | energy_price_protection | one-way only; credit attaches to the booking and is applied to the account; nothing credited where the posted price stands at or above the floor; fee not returned | "Where the posted price … falls below the programme's floor percentage … on the gallons still undrawn, measured on the last trading day of the month" | **yes** (that whole sentence is the `superseded_clause`) |
| energy_ext_protection_floor_credit | *energy_pricing (not listed as a base ref at all)* | — | "the price is the day's rack for the product plus the programme's margin" — the policy uses the programme's margin **less a volume relief** | **no — F1** |
| energy_ext_budget_year_reconciliation | energy_budget_plan | plan year / months / reconciliation date from the programme; fuel still billed at the price of the day; leaving mid-year bills the whole balance | "At reconciliation a member who has underpaid is billed the difference in one sum and a member who has overpaid is credited it …" | **yes** |
| energy_ext_account_clearance_payment | energy_payments_and_arrears | payment methods; allocation oldest invoice first; grain-settlement transfer | (a) "An energy invoice falls due the programme's terms in calendar days after the invoice date …" | **yes** |
| " | " | — | (b) "carries the programme's late charge once" — the policy gives 45.00 / 30.00 / the programme's charge by ladder | **no — F2** |
| " | " | — | (c) "and then the programme's monthly service charge for as long as it stands unpaid" — the policy applies the programme's charge **less a relief** | **no — F3** |
| energy_ext_account_clearance_payment | energy_agg_across_accounts | combined-balance and per-account scoping both honoured (every aggregate is scoped to the one `energy_account_id`) | none | n/a |
| energy_ext_prebuy_booking_credit | energy_contract_gallons_program | booking window; signed request registered before the gallons are credited; money taken at the booking | "A booking must reach the programme's minimum gallons and may not exceed the programme's ceiling as a share of the gallons the member took in the previous twelve months" | **yes** |
| energy_ext_contract_price_of_record | energy_account_maintenance | account live for update; route/tank/schedule rules untouched | "The contracted price on the account is written from the booking and is never edited on its own." | **yes** |
| energy_ext_undrawn_gallons_disposition | energy_contract_gallons_program | (a) "Gallons unused at the programme's expiry date are dealt with as the programme's treatment says …" | — | **yes** |
| " | " | — | (b) "A member who wants out of a booking before the gallons are drawn pays the programme's cancellation charge per gallon cancelled" — the policy applies the programme's charge **less a relief** | **no — F4** |
| energy_ext_undrawn_gallons_disposition | energy_pricing | drawdown scoped to the account and the product; oldest booking first (only one booking arises) | none | n/a |
| energy_ext_closure_settlement | energy_lifecycle_progression | member-owned tank not pulled; closed account terminal; undrawn gallons dealt with before closure | "A member closes an account of their own accord with **nothing owing**, no contracted gallons standing undrawn and no budget plan in mid-year" (and `params.closure_requires: [zero_balance, …]`) | **no — `overwrite: []` — F5** |

Disguised forms specifically looked for: **anonymous intermediate factor** — F1/F3/F4 are exactly this shape
(the deviation lives in an intermediate — `posted_margin`, `arrears_rate`, `cancellation_rate` — with no new
parameter name); **0/1 multiplier** — none found (`drawdown_share` and `fee_share` are declared shares of the
extended policy's own quantity, not existence flags zeroing a base amount); **dropped branch** — none found.
No author note calls a base output a "wrong value".

### factor_ladders

Structure only. Per policy: factor count, effect labels, `decides` binding, binding disjointness, tier count,
tier distinctness, and whether the `rule` states the whole ladder.

| policy | factors | parameter | method | multi-source tiers | cross_difficulty | all `decides` are inputs (never `result`) | bindings disjoint | every tier in the `rule` and in `compute` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| energy_ext_protection_floor_credit | 5 | 3 | 2 | `protected_floor_share`, `account_margin_relief`, `rack_of_record_anchor`, `prior_protection_offset`, `undrawn_holdback_basis` | grain (`protected_floor_share`) | yes | yes | yes |
| energy_ext_budget_year_reconciliation | 6 | 4 | 2 | `plan_year_window`, `drawdown_recognition`, `fee_recognition`, `plan_collection_basis`, `trueup_settlement_allowance`, `late_trueup_rate_relief` | grain (`trueup_settlement_allowance`) | yes | yes | yes |
| energy_ext_account_clearance_payment | 4 | 3 | 1 | `arrears_month_count_basis`, `secured_arrears_rate`, `lapsed_plan_late_charge`, `long_standing_settlement_allowance` | grain (`secured_arrears_rate`) | yes | yes | yes |
| energy_ext_prebuy_booking_credit | 6 | 3 | 3 | `prior_use_window`, `input_ceiling_share`, `seasonal_use_allowance`, `request_standing_share`, `lot_rounding_rule` | agronomy (`input_ceiling_share`) | yes | yes | yes |
| energy_ext_contract_price_of_record | 5 | 4 | 1 | `protection_price_loading`, `volume_price_adjustment`, `whole_farm_price_adjustment`, `booking_standing_loading`, `market_truing_rule` | agronomy (`whole_farm_price_adjustment`) | yes | yes | yes |
| energy_ext_undrawn_gallons_disposition | 6 | 4 | 2 | `settled_gallons_basis`, `settlement_price_basis`, `cancellation_charge_relief`, `handling_deduction_rate`, `protection_fee_refund`, `settlement_admin_charge` | agronomy (`cancellation_charge_relief`) | yes | yes | yes |
| energy_ext_closure_settlement | 4 | 2 | 2 | `closing_service_rate`, `closing_charge_base`, `closing_month_count`, `closing_member_allowance` | agronomy (`closing_service_rate`) | yes | yes | yes |

- Every ladder has exactly three tiers, the fall-through counted; every declared tier is a sentence of that
  policy's own `rule` and a branch of the `decides` binding in `compute`, and every branch of those bindings
  is a tier the rule states (with the third-tier breadth mismatch of **O1** above). No tier lives only in
  `compute`, and none lives only in the rule.
- Every fall-through tier's outcome equals the policy's `baseline` entry for that binding (checked
  expression by expression: e.g. `undrawn_holdback_basis` fall-through "nothing is held back" ↔
  `holdback_gallons: "0.0"`; `settlement_admin_charge` fall-through "the short member administration charge"
  ↔ `admin_charge: "K('short_member_admin_usd')"`).
- Label honesty: every `method` factor genuinely changes the algorithm (a window length, a grossing-up rule,
  a rounding lot, a day-count convention, a truing rule, a charge base), and every `parameter` factor
  substitutes a number into an unchanged formula. No mislabels found. Every `method` tier names a rule the
  charter states (window lengths, `minimum_delivery_gallons`, lot sizes, thirty-day months, the posted price
  of record — all charter-sourced). PASS.
- Counts against the bounds: every policy declares 4–6 factors with ≥2 `parameter` and ≥1 `method`. PASS.
- Per-task floors (at least one multi-source and at least one `cross_difficulty` over the task's
  computations) hold for both trees: task 0's three policies carry three grain-reading factors and several
  multi-source ladders; task 1's four policies carry four agronomy-reading factors. PASS.
- **F6 (SOURCE-FACTOR RED) — `rack_of_record_anchor` is an unreal ladder** (see `findings`).
- Tier distinctness in outcome: no two tiers of any ladder select the same value or method **as written**.
  (Whether two tiers collapse to the same *number* on a particular world is a per-task fact and is recorded
  in that task's `factor_weight` — see `1.md` F8.)

### findings

**F1 — SOURCE-POLICY RED — undeclared override of the posted-price formula.**
- symptom: the same quantity, "the posted price for the product", is fixed twice with different values.
- root cause: `energy_ext_protection_floor_credit`'s `account_margin_relief` ladder replaces the programme's
  posted-price margin with a reduced margin, and `energy_pricing` — the base policy that defines the posted
  price — is not even listed in that policy's `base_policy_refs`, so no `overwrite` declares it.
- evidence: base `energy_pricing.rule` (products/energy.yaml): "Where the programme prices at the posted
  price, the price is the day's rack for the product plus the programme's margin, taken on the day the fuel
  was pumped and not the day the invoice was cut." Extended rule: "The margin allowed on the account is the
  programme's posted price margin. … Where the gallons taken on the account over the twelve months ending on
  the handling date reach the high-volume gallons and the gallons drawn against bookings reach the volume
  drawdown gallons, the margin allowed on the account is the programme's posted price margin reduced by the
  high-volume relief." `energy.extended.yaml` `base_policy_refs: [energy_price_protection]`,
  `overwrite` names only the floor sentence.
- consequence: demonstrated on task 0 in `0.md` (`policy_self_consistency`).
- affected artifact: `energy.extended.yaml` → `energy_ext_protection_floor_credit` (`base_policy_refs`,
  `overwrite`, `rule` paragraph 4, `compute.posted_margin`); bears on **task 0**.

**F2 — SOURCE-POLICY RED — undeclared override of the late charge.**
- symptom: the late charge on an overdue energy account has two values in the same situation.
- root cause: `energy_ext_account_clearance_payment`'s `lapsed_plan_late_charge` ladder substitutes
  `lapsed_plan_late_charge_usd` (45.00) / `short_plan_late_charge_usd` (30.00) for the programme's late
  charge; the policy's `overwrite` names only the due-date sentence of `energy_payments_and_arrears`.
- evidence: base `energy_payments_and_arrears.rule`: "An invoice still unpaid after the programme's grace
  period, counted in whole calendar days from the due date, carries the programme's late charge once …";
  `variants[Contract Gallon Pre-Buy Account].late_fee_usd: 15.00`. Extended
  `params.short_plan_late_charge_usd: 30.00`; `overwrite[0].superseded_clause` = "An energy invoice falls due
  the programme's terms in calendar days after the invoice date, a payment landing on the due date itself
  still being on time." — the late-charge sentence is not named.
- consequence: demonstrated on task 0 in `0.md` (`policy_self_consistency`).
- affected artifact: `energy.extended.yaml` → `energy_ext_account_clearance_payment` (`overwrite`, `rule`
  paragraph 4, `compute.late_charge`); bears on **task 0**.

**F3 — SOURCE-POLICY RED — undeclared override of the monthly service charge on arrears.**
- symptom: the rate the arrears bear has two values in the same situation.
- root cause: `secured_arrears_rate` substitutes the programme's monthly service charge *less* a relief;
  the same `overwrite` omission as F2.
- evidence: base `energy_payments_and_arrears.rule`: "… and then the programme's monthly service charge for
  as long as it stands unpaid." `variants[Contract Gallon Pre-Buy Account].finance_charge_monthly_pct: 1.50`.
  Extended `params.secured_rate_relief_pct: 0.35`, `compute.arrears_rate`.
- consequence: demonstrated on task 0 in `0.md` (`policy_self_consistency`).
- affected artifact: `energy.extended.yaml` → `energy_ext_account_clearance_payment` (`overwrite`, `rule`
  paragraph 3, `compute.arrears_rate`); bears on **task 0**.

**F4 — SOURCE-POLICY RED — undeclared override of the cancellation charge per gallon.**
- symptom: the per-gallon cancellation charge on an undrawn booking has two values in the same situation.
- root cause: `energy_ext_undrawn_gallons_disposition`'s `cancellation_charge_relief` ladder applies the
  programme's charge less `active_member_relief` / `part_member_relief`; the policy's `overwrite` names only
  the unused-gallons-treatment sentence of `energy_contract_gallons_program`.
- evidence: base `energy_contract_gallons_program.rule`: "A member who wants out of a booking before the
  gallons are drawn pays the programme's cancellation charge per gallon cancelled …";
  `variants[Bulk Farm Fuel Delivery Account].contract_cancellation_fee_per_gallon_usd: 0.1000`. Extended
  `params.active_member_relief: 0.0400`, `compute.cancellation_rate`;
  `overwrite[0].superseded_clause` = the "Gallons unused at the programme's expiry date …" sentence only.
- consequence: demonstrated on task 1 in `1.md` (`policy_self_consistency`).
- affected artifact: `energy.extended.yaml` → `energy_ext_undrawn_gallons_disposition` (`overwrite`, `rule`
  paragraph 4, `compute.cancellation_rate`); bears on **task 1**.

**F5 — SOURCE-POLICY RED — undeclared override of the member-closure eligibility ("nothing owing").**
- symptom: base forbids a member-initiated closure while anything is owed; the extended policy's whole
  purpose is to compute a balance the account closes at and write it onto the account as what is owed, and
  it declares no override at all.
- root cause: `energy_ext_closure_settlement.overwrite: []`.
- evidence: base `energy_lifecycle_progression.rule`: "A member closes an account of their own accord with
  nothing owing, no contracted gallons standing undrawn and no budget plan in mid-year"; base
  `params.closure_requires: [zero_balance, zero_undrawn_contract_gallons, no_budget_plan_in_mid_year]`.
  Extended rule: "The balance the account closes at is the amount standing plus the closing charge less the
  closing allowance, rounded to two decimal places, and never falls below nothing." Tool
  `close_energy_account_7515982f` is `owner="user"` (the member's own act) and writes
  `account_balance=round(float(closing_balance_usd), 2)`.
- consequence: demonstrated on task 1 in `1.md` (`policy_self_consistency`) — under base the only defensible
  answer is that the account cannot be closed on this call.
- affected artifact: `energy.extended.yaml` → `energy_ext_closure_settlement` (`overwrite`, `rule`);
  `task_tools.py` → `close_energy_account_7515982f`; bears on **task 1**.

**F6 — SOURCE-FACTOR RED — `rack_of_record_anchor` is an unreal ladder: one conjunct holds of every
customer who reaches this write, and the third tier is satisfiable by no such customer.**
- symptom: the ladder's route conjunct divides no customers, and the tier the `baseline` is drawn from can
  never fire as the rule states it.
- root cause: the ladder conditions on `scheduled_route_days`, a programme-level constant, inside a policy
  whose write only ever arises on a programme that carries downside protection.
- evidence: `energy_ext_protection_floor_credit.factors[rack_of_record_anchor].ladder` tier 1 —
  "two or more stops the member called in were billed on the account in the three months ending on the
  handling date **and the tank stands on a route the truck runs on a fixed cycle**"; tier 3 —
  "two or more such stops were billed in that window **and the tank stands on a route the truck runs only on
  request**". In the catalogue, `price_protection_enabled: true` holds only for the Contract Gallon Pre-Buy
  Account (`scheduled_route_days: every_21_days`) and the Bulk Farm Fuel Delivery Account
  (`every_14_days`); the only programme with `scheduled_route_days: on_request_only` is the Will-Call Propane
  Account, whose `price_protection_enabled: false` and `price_protection_floor_pct: 0.0` make
  `credit_per_gallon` nothing, so base `energy_price_protection` ("Where the posted price stays at or above
  the floor nothing is credited") writes no credit line at all.
- demonstrated consequence: the route conjunct restates the policy's scope rather than dividing its
  customers, so the ladder is in truth two tiers; and the fall-through tier — from which the factor's
  `baseline` (`RND(last_will_call_price - P('posted_price_margin_per_gallon_usd'), 4)`) is taken — is
  reachable in `compute` only through the unconditional `else`, on the case "fewer than two will-call stops
  **and** gallons booked under the programme's minimum", which the `rule` nowhere states (this is the one
  instance of O1 with a demonstrable consequence).
- affected artifact: `energy.extended.yaml` → `energy_ext_protection_floor_credit`
  (`rule` paragraph 5, `factors[rack_of_record_anchor]`, `compute.rack_of_record`); bears on **task 0**.

**O1 / O2 / O3 / O4 (observations)** — set out under `rule_compute_equivalence`, `prerequisite_graph` and
`prerequisite_sentences` above.

**O5 (observation) — a programme sold pre-buy gallons whose price basis never uses them.** The Bulk Farm
Fuel Delivery Account carries `contract_gallons_minimum: 2500`, a booking window, price protection and a
cancellation charge, yet its `price_basis` is `rack_plus_margin_on_the_delivery_day`, not
`contracted_price_until_gallons_exhausted_then_posted_price`. Base `energy_pricing` therefore never prices a
gallon on that programme at the contracted price, so the "contracted price of record"
`energy_ext_contract_price_of_record` writes onto such an account governs nothing until the gallons are
settled out under `energy_ext_undrawn_gallons_disposition`. This is a blueprint-level oddity carried into
this difficulty's base copy; it changes no number on either task and is recorded as an observation.
Affected artifact: `blueprint/products/energy.yaml` `variants[Bulk Farm Fuel Delivery Account].price_basis`;
bears on **task 1**.

**O6 (observation) — a fall-through outcome that adds a month of interest for inactivity.**
`energy_ext_closure_settlement.factors[closing_month_count]` tier 2 charges "the whole months since the
account was last paid **and one month more**" where no stop was billed in the last three months. Charging an
extra month of service charge because the member bought no fuel is an unusual treatment to publish; it is
not one this auditor can show no cooperative applies, so it is recorded as an observation rather than a red
light. Affected artifact: `energy_ext_closure_settlement` (`rule` paragraph 4,
`factors[closing_month_count]`); bears on **task 1**.

## closing_checklist

Written after both tasks' `source_gt_comparison` sections were on disk (2026-09-18T09:36Z). This section is
the only part of this file derived after the reveal.

**The difficulty does NOT close out.** Step 4 requires every comparison section to carry a PASS on all four
relationships; neither does.

| # | Step 4 item | result |
| --- | --- | --- |
| 1 | per-task audit files correspond one-to-one with the tasks; `_difficulty.md` alongside; old revisions traceable; every comparison carries a PASS | **FAIL** — `0.md` and `1.md` exist one-to-one with `tasks/0.json` and `tasks/1.json` and this is revision 1 (no prior revision to preserve), but `0.md` carries SOURCE-POLICY RED (F1/F2/F3), SOURCE-FACTOR RED (F6) and a consequent SOURCE-TASK RED, and `1.md` carries SOURCE-POLICY RED (F4/F5), SOURCE-CHAIN RED (C1) and SOURCE-TASK RED (T1) |
| 2 | extended policies fully covered; the M tasks' scopes pairwise disjoint (each spanning its whole tree); task tools and GT closed; each task tool an independently generated, frozen uuid8 | **PASS** — task 0 claims {protection floor credit, budget year reconciliation, account clearance payment}, task 1 claims {prebuy booking credit, contract price of record, undrawn gallons disposition, closure settlement}; 3 + 4 = all 7, disjoint, each scope exactly its own component of the prerequisite graph; 7 task tools, one per policy, none shared; uuid8s as verified in § action_binding_and_uuids |
| 3 | every task's tree has one to three prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 problem resolved by an `owner=user` tool, no cycle; the difficulty's edges together still a DAG | **PARTIAL** — counts and owners hold (task 0: n = 2, 2 `value_input`, root tool `owner=user`; task 1: n = 3, 3 `value_input`, two `owner=user` writes; no cycle, no cross-task edge, the whole graph a DAG) — **but task 1's root edge is vacuously satisfied at frozen_time (C1), so that tree does not in fact impose three prerequisite problems on a reader who starts from the root** |
| 4 | every computation declares a self-sufficient baseline and 4–6 factors (2 `parameter`, 1 `method`; per task ≥1 multi-source and ≥1 cross-difficulty), every ladder ≥3 tiers stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones that line of business actually holds, every factor proved to bear weight against an honest baseline, and the baseline alone giving a definite number different from gold | **PARTIAL** — all thirty-six declared factors across the seven policies bear weight on their own task's world against honest baselines, and all seven whole-baseline fall-backs are definite and differ from gold (196.30, −850.35, 3707.13; 5742.0, 2.98, 15369.0, 2878.74) — **but F6: `rack_of_record_anchor`'s route conjunct holds of every customer who can reach that write and its third tier is satisfiable by none of them**, and O1: six ladders state a third tier narrower than `compute`'s `else` |
| 5 | this difficulty's instantiation-stage gates re-run once on the final form | **NOT RUN** — the artifacts were not changed by this audit (the audit's write domain is `audits/policy_task/energy_delivery_desk/` only) and the brief's gate snapshot of 2026-09-18T09:06 stands as the entry condition. The gates are for the party that reworks the artifacts to re-run on the final form; this auditor neither re-ran them nor arranged a fix. |

**Difficulty-level verdict:** policy self-consistency **RED** (F1–F5), problem tree **RED** on task 1 (C1),
factors **RED** on task 0 (F6), unique solution **RED** on both. Source-layer audit **not passed**.

---

## revision_2

Re-audit of round 1. Revision 1 above is left untouched.

### re_derivation_grounds

Both shared inputs moved, so **every charter-global section is re-derived in full**; none is carried
forward by reference.

| input | round 1 | round 2 | re-derived? |
| --- | --- | --- | --- |
| `energy.extended.yaml` | `3b3b4e6878f41596` | `9221f48584d7a3d8` | yes — all sections |
| `task_tools.py` | `88bb62f34b07e353` | `d06a6d6cbb874e26` | yes — `action_binding_and_uuids` in particular, a tool's contract text having changed (O8) |
| `blueprint/products/energy.yaml` | (unhashed in r1) | `05c03f298fb1cb8f` | verified unchanged in substance: `diff` of `energy.extended.yaml` lines 1–1029 against it is empty, so the base copy is still verbatim, and all four base sentences round 1 quoted are still present in the blueprint — no base sentence was deleted to make a conflict disappear |
| masked view task 0 | `ba402ad8cee3e5e8` | `409de0787607653c` | `frozen_time` and `initial_state` byte-identical to round 1; only `user_scenario` changed (O7) |
| masked view task 1 | `c4fe51488779c218` | `cf99ebb2af93d5f9` | `frozen_time` and `initial_state` byte-identical to round 1; only `user_scenario` changed (O9) |

Round 2 is a verification pass, not a blind derivation: this auditor has already seen this difficulty's GT.
Every figure below is this auditor's own recomputation on the **revision-2** charter, run independently and
then compared against the revision-2 task files.

Entry conditions: the difficulty-wide gate block of 2026-09-18T09:47 came with the brief and is green
(`check_traceability` still deferred to step 3). Gates were not re-run by this auditor.

### policy_conflict_scan (re-derived)

Structure is unchanged: 10 base policies, 7 extended policies, the same 7 `(target_tool, computes)` pairs,
the same two disjoint, jointly complete task scopes (3 + 4 = 7). Every conflict round 1 recorded is now
**declared**. `overwrite` entries went from 7 to 10:

| round-1 finding | round-2 state | verified how |
| --- | --- | --- |
| **F1** | **CLOSED** — `energy_ext_protection_floor_credit.base_policy_refs` is now `[energy_price_protection, energy_pricing]`, and a first `overwrite` entry names base `energy_pricing`'s "Where the programme prices at the posted price, the price is the day's rack for the product plus the programme's margin, taken on the day the fuel was pumped and not the day the invoice was cut.", replaced by "The posted price is the rack of record plus the margin allowed on the account, taken to four decimal places." | `superseded_clause` confirmed a verbatim substring of `energy_pricing.rule`; `replaced_by` confirmed a verbatim sentence of the extended rule, which then defines "the margin allowed on the account" through the `account_margin_relief` ladder |
| **F2 + F3** | **CLOSED** — one `overwrite` entry supersedes the single base sentence that carried both departures: "An invoice still unpaid after the programme's grace period, counted in whole calendar days from the due date, carries the programme's late charge once and then the programme's monthly service charge for as long as it stands unpaid.", replaced by the extended policy's own service-charge and late-charge sentences | verbatim both ways. The reworker's claim that base `energy_payments_and_arrears.eligibility[late_charge_after_grace]` retires with that sentence is **verified**: that eligibility's `condition` is character-for-character the superseded sentence (checked by normalised string equality), so it carries no provision the override leaves standing |
| **F4** | **CLOSED** — a second `overwrite` on `energy_ext_undrawn_gallons_disposition` names base `energy_contract_gallons_program`'s "A member who wants out of a booking before the gallons are drawn pays the programme's cancellation charge per gallon cancelled, and where the posted price has risen above the contracted price the cooperative does not pay the member the difference to release them." | verbatim; see **N1** for a residue |
| **F5** | **CLOSED** — `energy_ext_closure_settlement.overwrite` is no longer `[]`; it names base `energy_lifecycle_progression`'s "A member closes an account of their own accord with nothing owing, no contracted gallons standing undrawn and no budget plan in mid-year; where contracted gallons stand undrawn they are dealt with under the programme's unused gallons treatment before the account can close.", replaced by "A member closes an account of their own accord whatever stands on it, and the balance the account closes at is written onto the account as what is owed and follows the member rather than being extinguished." | verbatim both ways; that replacement sentence is now the second sentence of the extended rule. See **N1**, and **O4 CLOSED** below |

No new overlapping-subject conflict was found. Triggers, eligibility, time anchors, objects, cross-category
read boundaries and terminal states were re-swept and carry no conflict beyond those declared.

### rule_compute_equivalence (re-derived)

- **O1 CLOSED.** All six ladders round 1 named now end in a residual tier that matches `compute`'s
  unconditional `else` exactly: `rack_of_record_anchor`, `account_margin_relief` and
  `prior_protection_offset` (energy_ext_protection_floor_credit), `lapsed_plan_late_charge`
  (energy_ext_account_clearance_payment), `prior_use_measure` (energy_ext_prebuy_booking_credit) and
  `volume_price_adjustment` (energy_ext_contract_price_of_record) each read "In every other case …" in the
  `rule` and "in every other case" in the `ladder`. All 36 ladders across the seven policies were re-checked
  tier by tier for partition; **every one now partitions its space**, and no new gap was introduced.
  Each of the five rewritten fall-through tiers still states exactly what its `baseline` expression encodes
  (verified expression by expression, e.g. `lapsed_plan_late_charge` → "the programme's late charge where the
  days overdue stand beyond the programme's grace period, and nothing where they do not" ↔
  `(P('late_fee_usd') if days_overdue > P('late_fee_grace_days') else 0.0)`).
- **O2 CLOSED.** `energy_ext_budget_year_reconciliation.baseline.params` is now `['plan_window_months']`
  (`finance_charge_monthly_pct` removed, its baseline rule saying "The rate the difference bears is
  nothing"), and `energy_ext_contract_price_of_record.baseline.params` is now `[]`, which is honest: that
  baseline rule reads no catalogue parameter, arriving at the posted price of record from "the price billed
  on the most recent stop the member called in". See **N4**.
- Every quantity, window, filter, tier, branch, cross-category read, acting base, cap/floor and rounding
  convention in each `rule` still has a verbatim `compute_basis` quotation and a restricted expression, and
  the sweep back found no binding whose basis is absent from its rule. One new rule sentence carries no
  `compute_basis` entry by design — see **N3**.

### action_binding_and_uuids (re-derived; `task_tools.py` changed)

- The seven uuid8s are **unchanged and unreused**: `43e8349b`, `cfd56d13`, `6fe49ac6`, `8fcb503b`,
  `9db7726a`, `1dbcf678`, `7515982f`. Still distinct, no shared prefix or tail, no sequence, not
  batch-derived. Freezing a uuid8 across a rework is the correct behaviour.
- Owners unchanged: three `owner="user"` (clearing payment, booking, closure), four `owner="agent"`.
- **Tool-layer neutrality re-verified on the new file** by parsing each function: every body is
  `Assign*/Expr/Return` (or `Expr/Return` for the two `ctx.update` tools) with **zero** `raise`, `assert` or
  `if` statements. No tool validates or hints at a prerequisite.
- **Docstring silence re-verified on the new text**: no docstring names another tool, and the only
  ordering-shaped words are "the next statement for the account" and "from then on", both describing the
  state of the account after that single write. No `before` / `after` / `first` / `prior to`.
- **O8 CLOSED.** `post_energy_account_clearing_payment_6fe49ac6` now reads "applied to the
  **earliest-dated** energy invoice standing unpaid on it", and its `invoice_number` Arg adds "which is the
  one standing unpaid on the account with the earliest date on it". The by-date / by-number ambiguity is
  gone, and the convention the contract now states is the one GT applies (`EI-440712`, 2025-11-12).
- Each `(target_tool, computes)` still claimed by exactly one policy. PASS.

### prerequisite_graph (re-derived)

Same five edges, same `problem` targets, same gates (`credits_allowed`, `instalments_billed`, `booked_gal`,
`settlement_price`, `amount_standing_d`), all `kind: value_input`, all `form: state`, no `fallback_reason`
anywhere (correctly), still a DAG of two disjoint components with no cross-task edge. Every `policy_source`
re-checked as a verbatim substring of the **blocked** policy's own `rule` — all five pass. Every
`resolved_by` is still the depended-on policy's `target_tool`.

Two `policy_source` sentences were rewritten this round; both are re-tested in full below.

### prerequisite_sentences (re-derived)

- **O3 CLOSED.** The `energy_ext_account_clearance_payment ← energy_ext_protection_floor_credit` edge now
  reads "The amount that clears the account is fixed only after the account carries, on every pre-buy
  booking whose protected floor stood above the posted price, a downside protection credit **dated in the
  month the amount is worked out**", and the `condition` mirrors it. Sentence and condition now carry the
  same strength and scope; the round-1 mismatch (the condition adding "for the period being measured" where
  the sentence did not) is gone. The old wording is no longer anywhere in the rule, so no second wording of
  the dependency exists. Four-point test: "only after"; record-visible state; no tool, policy id or code
  token; scope matches. Exactly one write dates a protection credit into the current month —
  `record_price_protection_credit_43e8349b`, which stamps `delivery_date=ctx.now()[:10]`.
- The `energy_ext_closure_settlement ← energy_ext_undrawn_gallons_disposition` sentence was rewritten for
  C1 and is re-tested in `1.md` § revision_2, where its world matters.
- The other three sentences are unchanged in text and pass the four-point test as in revision 1.
- No rule restates another's dependency; no depended-on rule carries the blocked rule's sentence (verified).
- **O4 CLOSED.** The base sentence that stated a cross-problem order — `energy_lifecycle_progression`'s
  "where contracted gallons stand undrawn they are dealt with under the programme's unused gallons
  treatment before the account can close" — is part of the sentence `energy_ext_closure_settlement` now
  supersedes, so no base rule sentence grounds a cross-problem order in this difficulty any longer.

### override_declarations (re-derived)

Sentence by sentence against each `base_policy_refs` entry, the round-2 position is: **every base sentence
whose quantity this charter handles differently is now named in the declaring policy's `overwrite`.** The
four undeclared overrides of revision 1 (F1, F2/F3, F4, F5) are closed; no new undeclared override was
found. `base_policy_refs` gained `energy_pricing` on `energy_ext_protection_floor_credit`; every other
policy's refs are unchanged and every non-superseded base provision is still inherited in full.

### factor_ladders (re-derived)

Counts are unchanged and still inside the bounds: 5 / 6 / 4 / 6 / 5 / 6 / 4 factors, each policy with ≥2
`parameter` and ≥1 `method`; 36 factors in all, every ladder three tiers.

- **F6 CLOSED.** `rack_of_record_anchor`'s route conjunct is gone. The ladder now reads: (1) "two or more
  stops the member called in were billed on the account in the three months ending on the handling date" →
  the average of those prices less the margin; (2) "no stop the member called in was billed in that window
  and the gallons booked on the account reach the programme's minimum pre-buy gallons" → the booked price
  less the margin; (3) "in every other case" → the most recent such stop's price less the margin.
  `compute.rack_of_record` matches branch for branch (`>= K('multi_stop_count')` / `< 1 and booked >= min` /
  `else`). **All three tiers are now reachable by a real account** — tier 3 fires on exactly one called-in
  stop in the window, or on none where the booking is under the programme's minimum — and no conjunct holds
  of every customer who reaches this write. The `baseline` is now drawn from the residual tier, which is
  reachable. The three methods remain distinct.
- Every fall-through tier still equals its policy's `baseline` entry for that binding; every label is still
  honest; every `method` tier still names a rule the charter states.
- **N5 (observation):** the F6 rewrite makes `rack_of_record_anchor` tier 1 a single condition, so that
  factor is no longer multi-source. The per-task floor is unaffected — task 0 still carries
  `protected_floor_share`, `prior_protection_offset` and `undrawn_holdback_basis` as multi-source factors,
  and task 1 still carries `input_ceiling_share` and `cancellation_charge_relief`. Both tasks still carry a
  `cross_difficulty` factor (grain for task 0, agronomy for task 1) reading seeded rows.

### findings (revision 2)

**F1, F2, F3, F4, F5, F6 — CLOSED**, each verified above against the artifacts rather than against the
reworker's account. **O1, O2, O3, O4, O6, O7, O8, O9 — CLOSED** (O6, O7, O9 verified in the task files).
**O5 — NO CHANGE, correctly**: the Bulk Farm Fuel Delivery Account still carries pre-buy gallons, a booking
window, price protection and a cancellation charge while its `price_basis` is
`rack_plus_margin_on_the_delivery_day`; this lives in `blueprint/products/energy.yaml`, which the base copy
must reproduce verbatim, and it changes no number on either task. Still an observation.

Four new observations, none of them a red light:

**N1 (observation) — two `overwrite` entries supersede more than their `replaced_by` restates.**
- `energy_ext_undrawn_gallons_disposition`'s second entry supersedes the whole base sentence, whose second
  half reads "and where the posted price has risen above the contracted price the cooperative does not pay
  the member the difference to release them". Neither the `replaced_by` nor the extended rule restates it
  (confirmed: the phrase "does not pay the member the difference" appears nowhere in that policy's rule).
  The blueprint's own difficulty summary lists "whether to release a member from a booking when the market
  has moved against them" as a `POLICY_NOT_COVERED` handoff, and that refusal's stated basis is the half now
  superseded.
- `energy_ext_closure_settlement`'s entry supersedes a sentence that also carried "no contracted gallons
  standing undrawn and no budget plan in mid-year". The undrawn-gallons ordering is deliberately re-supplied
  by that policy's own prerequisite sentence (this is the C1 fix), but the mid-year budget-plan closure bar
  is now restated nowhere.
- Why this is an observation and not a red light: a declared supersession is scoped to the extended policy
  that declares it, so it is arguable the base sentence still governs the situations those extended policies
  do not reach; and neither loss can be demonstrated to change a number or a terminal state on either
  task's world — no task raises a market-moved release, and task 1's account is a Bulk Farm Fuel Delivery
  Account with `budget_plan_enabled: false` and `budget_monthly_amount: 0.0`, so the mid-year bar could not
  bite. Affected artifact: `energy.extended.yaml` →
  `energy_ext_undrawn_gallons_disposition.overwrite[1]`, `energy_ext_closure_settlement.overwrite[0]`.
  Bears on: task 1 (no consequence), and on the scenario's declared handoff coverage.

**N2 (observation) — base structured fields that encode a superseded sentence were not refreshed.**
`energy_payments_and_arrears.eligibility[late_charge_after_grace].condition` is character-for-character the
sentence `energy_ext_account_clearance_payment.overwrite[1]` supersedes, and
`energy_lifecycle_progression.params.closure_requires` still reads
`['zero_balance', 'zero_undrawn_contract_gallons', 'no_budget_plan_in_mid_year']`, encoding the sentence
`energy_ext_closure_settlement.overwrite[0]` supersedes. Neither structured field is itself named in any
`overwrite`; each retires only by the reader's inference that it restates the superseded sentence. This is
recorded as an observation and not as a residual F5 because check 1 operates at the granularity of the
sentences of the cited base policy, the sentence in each case **is** named, and the `params` / `eligibility`
entries are the machine encoding of that same sentence rather than independent provisions — and because
neither can be changed inside this difficulty's artifacts, the base copy being required to reproduce
`blueprint/products/energy.yaml` verbatim. Affected artifact: `blueprint/products/energy.yaml` →
`policies[energy_payments_and_arrears].eligibility[0].condition`,
`policies[energy_lifecycle_progression].params.closure_requires`. Bears on tasks 0 and 1.

**N3 (observation, not a defect) — the new booking-price sentence has no `compute_basis` entry.**
`energy_ext_prebuy_booking_credit.rule` now carries "The price the booked gallons are credited at is the
price billed on the most recent stop the member called in on or before the day the signed request was
registered." It fixes a **tool argument** (`lodge_contract_gallon_booking_8fcb503b.price_per_gallon`), not a
binding of that policy's `computes` quantity (`booked_gallons`), so it correctly has no `compute_basis`
quotation and no compute binding. It is not an empty promise: the sentence is what `evaluation_criteria`
step 8 scores against, and it resolves uniquely on task 1's world (verified in `1.md` § revision_2).

**N4 (observation) — `energy_ext_contract_price_of_record.baseline.params` is now the empty list.** Honest
(its baseline rule reads no catalogue parameter) but it now conveys nothing about which defaults the
computation document should print. No consequence: the baseline still yields a definite number, 2.98 on
task 1's world, different from gold.

**N5 (observation)** — set out under `factor_ladders` above.

### closing_checklist (revision 2)

Written after both tasks' `source_gt_comparison` (revision 2) sections were on disk, 2026-09-18T09:55Z.

**The difficulty closes out.**

| # | Step 4 item | result |
| --- | --- | --- |
| 1 | per-task audit files one-to-one with the tasks; `_difficulty.md` alongside; old revisions traceable; every comparison carries a PASS | **PASS** — `0.md` and `1.md` match `tasks/0.json` and `tasks/1.json`; revision 1 is preserved verbatim in all three files with revision 2 appended below it, and neither frozen round-1 derivation was rewritten to accommodate what round 2 knows; both revision-2 comparisons carry PASS on all four relationships |
| 2 | extended policies fully covered; scopes pairwise disjoint (each spanning its whole tree); task tools and GT closed; each tool an independently generated, frozen uuid8 | **PASS** — 3 + 4 = all 7, disjoint, each scope exactly one component of the prerequisite graph; 7 tools, one per policy; the seven uuid8s are unchanged from revision 1 (correctly frozen across the rework), distinct, unreused and not batch-derived |
| 3 | every task's tree has 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 problem resolved by an `owner=user` tool, no cycle; the difficulty's edges together still a DAG | **PASS** — task 0: n = 2, 2 `value_input`, root tool `owner=user`; task 1: n = 3, 3 `value_input`, two `owner=user` writes; no cycle, no cross-task edge, the whole graph a DAG. **C1 closed**: task 1's root edge is now false at frozen_time on a registered signed request that exists, so the tree genuinely imposes three prerequisite problems on a reader starting from the root |
| 4 | every computation a self-sufficient baseline and 4–6 factors (2 `parameter`, 1 `method`; per task ≥1 multi-source and ≥1 cross-difficulty), every ladder ≥3 tiers stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones that line of business actually holds, every factor bearing weight against an honest baseline, the baseline alone giving a definite number different from gold | **PASS** — 36 factors across 7 policies, every one recomputed as bearing weight on its own task's world; all seven whole-baseline fall-backs definite and different from gold (196.30, −850.35, 3707.13; 5742.0, 2.98, 15369.0, 2878.74); **O1 closed** — all 36 ladders now partition their space, their residual tier matching `compute`'s `else`; **F6 closed** — no ladder now carries a conjunct that holds of every customer who reaches its write, and every tier of every ladder is reachable by a real account |
| 5 | this difficulty's instantiation-stage gates re-run once on the final form | **PASS (cited, not run here)** — the orchestrator's difficulty-wide block of 2026-09-18T09:47 is green on the final artifacts (`9221f48584d7a3d8` / `d06a6d6cbb874e26`). This auditor did not re-run them and did not touch the artifacts; `check_traceability` remains deferred to step 3 |

**Difficulty-level verdict, revision 2: policy self-consistency PASS + problem tree holds PASS + factors
bear weight PASS + unique solution PASS, on both tasks. The source-layer audit is passed.**

Outstanding items are five observations, none of which is grounds for rework: **N1**, **N2**, **N3**,
**N4**, **N5** (revision 2) and **O5** (revision 1, unchanged and agreed). N2 and O5 live in
`blueprint/products/energy.yaml`, which this difficulty's base copy must reproduce verbatim and which is
therefore not fixable inside this difficulty's artifacts.

---

## revision_3

Re-audit of round 2. Revisions 1 and 2 above are left untouched.

The occasion is not a finding of this audit: the published KB was audited blind at the render layer and
returned KB-RUNTIME RED on task 0, the root lying in the source. That is a standard this auditor's own view
does not by itself impose — with the `compute` binding visible, prose that names a quantity ambiguously
still looks determinate. Revision 3 therefore closes the reported items **and** re-runs check 2 under the
stricter question: *would this rule entail this binding to a reader who cannot see the binding?*

### re_derivation_grounds

| input | round 2 | round 3 | treatment |
| --- | --- | --- | --- |
| `energy.extended.yaml` | `9221f48584d7a3d8` | `cd7e53bc04a9322a` | **changed — every charter-global section re-derived in full** |
| `task_tools.py` | `d06a6d6cbb874e26` | `d06a6d6cbb874e26` | **unchanged — `action_binding_and_uuids` is carried forward by reference on those two hashes as the grounds**, and was not re-derived |
| `blueprint/products/energy.yaml` | `05c03f298fb1cb8f` | `05c03f298fb1cb8f` | unchanged; base copy re-verified verbatim (`diff` of extended lines 1–1029 against it is empty) |
| masked view task 0 | `409de0787607653c` | `409de0787607653c` | **world unchanged** — `frozen_time`, `user_scenario` and `initial_state` all identical |
| masked view task 1 | `cf99ebb2af93d5f9` | `cf99ebb2af93d5f9` | world unchanged |
| task file 0 | `1fe95f7b680e2747` | `a1cd642bfe0e4183` | six scored fields moved — `0.md` § revision_3 re-derives that task in full |
| task file 1 | `8ca6cb471164d6b5` | `68cedf1b230cb18a` | wording only; verified figure by figure in `1.md` § revision_3 |

Entry conditions: the difficulty-wide gate block of 2026-09-18T12:47 came with the brief and is green.
`replay_tasks.py` was not run, as instructed; `check_traceability` belongs to the render loop. Gates were
not re-run by this auditor. Verification pass, not a blind derivation.

### policy_conflict_scan (re-derived)

Unchanged in substance: 10 base policies, 7 extended policies, the same 7 `(target_tool, computes)` pairs,
the same two disjoint and jointly complete scopes. All ten `overwrite` entries re-checked mechanically —
every `superseded_clause` is still a verbatim substring of the cited base rule and every `replaced_by` a
verbatim sentence of the extended rule that declares it. No conflict is left undeclared and no new
overlapping-subject conflict was introduced by the round-3 rewrites.

### rule_compute_equivalence (re-derived, under the runtime-determinacy question)

All 36 ladders re-checked: every tier condition that is not the residual "in every other case" is still a
verbatim sentence of its own rule, every residual still matches `compute`'s unconditional `else`, and every
fall-through still equals its `baseline` expression. No gap reopened.

**The reported items:**

- **P1 — CLOSED, and closed the right way round.** The reworker moved the **binding**, not the prose's
  meaning: `last_gauge_after` (`tank_percent_after`) became `last_gauge_before` (`tank_percent_before`),
  and the sentence was sharpened to "less the gauge reading the driver took on arriving at the most recent
  stop, **before any fuel was pumped**". Its reasoning is **verified independently on the artifacts and the
  records**, and it holds:
  1. *The business meaning settles it.* The tier's own purpose, stated in the same sentence, is "the gallons
     the automatic schedule will take at the next stop". Base `energy_delivery_scheduling` says a keep-full
     truck "comes when the degree-day model or a gauge reading puts the tank at or below the programme's
     trigger percentage, and it fills to the programme's fill-to percentage" — so what a fill takes is
     fill-to less **where the truck finds the tank**, which is the arrival reading. The after-pumping
     reading measures nothing the next fill will take.
  2. *The reductio checks out on the records.* On every stop the automatic schedule made on task 0's
     account, `tank_percent_after` is 80.0 — exactly
     `variants[Contract Gallon Pre-Buy Account].keep_full_fill_to_percent`. Under the old binding the tier's
     value on such a stop is `1000 × (80.0 − 80.0)/100 = 0`: a hold-back of nothing, for a ladder whose
     condition is "the tank stands on the automatic keep-full schedule". The old binding made the tier a
     no-op for precisely the population it is written for.
  3. *Magnitude.* Under the new binding the hold-back is 360.0 gallons on a 1 000-gallon tank found at 44 %
     and filled to 80 % — 36 % of the tank. Under the old one it was 60.0 gallons, 6 %, and that only
     because the single most recent stop happens to carry an atypical `tank_percent_after` of 74.0 while
     every other stop on the account reads 80.0.
  The corroboration offered — that a blind render-layer auditor reached the same figures — is **not**
  treated here as evidence: that report is outside this audit's read domain, and agreement between two
  readers is not proof. What stands behind the verdict is this auditor's own recomputation of task 0 from
  the revision-3 charter, in `0.md` § revision_3.
- **P2 — CLOSED.** `energy_ext_closure_settlement`'s baseline rule said "less the money applied against
  those bookings **when gallons standing undrawn were released**" while `released_d` sums **every**
  `energy_contract_gallons_drawn` row, release or ordinary contract fill. It now reads "less the money
  applied against those bookings, **whether on a fill drawn against them or on a release of gallons standing
  undrawn**", which is what the binding does. The `closing_charge_base` ladder already said "money has been
  applied against a booking" with no "released", matching `released_count_d`; it is consistent with the
  clarified baseline.
  The decision to leave the **prerequisite sentence** alone is verified as correct, not as an omission: that
  sentence gates on "the money applied against a booking **when gallons standing undrawn were released**" —
  the release entry specifically — and widening it to cover ordinary fill drawdowns would have made the edge
  satisfiable by a contract fill that answers no pre-buy request. The gate and the sum are different
  quantities and are now worded differently on purpose.
- **P3 — CLOSED, and verified binding by binding.** Four policies use the notion and each now defines it
  once in its own rule, in identical words: "A will-call stop is one the records show the member called in,
  and not one run to the automatic keep-full schedule, run as an emergency, run after hours or made to fill
  against a booking." That definition names the other four members of
  `energy_deliveries.delivery_type` exactly, so a reader without the compute reaches the same filter.
  **The over-narrowing risk was checked and is absent:** every compute binding over `energy_delivery_made`
  in policies 1, 4, 5 and 6 was matched against its `compute_basis` sentence — all 8 bindings that carry
  `delivery_type='will_call'` have a basis sentence saying "will-call stop", and all 10 that carry no
  delivery-type filter have a basis sentence saying plain "stops" (notably
  `energy_ext_undrawn_gallons_disposition.last_stop_gallons` and `stops_3m_e`, and
  `energy_ext_protection_floor_credit.stops_12m`, which must stay unfiltered). No sentence was narrowed
  where its binding was not, or widened where its binding was. Policies 2, 3 and 7 use the notion nowhere
  and define it nowhere, correctly.
- **Runtime openness (ii) — CLOSED, and it was a live one.** "a payment reached the cooperative by bank
  transfer" admitted two sums because `energy_contract_gallons_booked` rows also carry `payment_method` and
  `payment_reference` — and on task 0's world the booking row
  `43472743-bc36-46e5-a984-c2460afbb1d6` carries `payment_method: ach` and 3 576.00. Read to include it,
  `transfer_money_year` would have been 600.00 + 3 576.00 = 4 176.00 and the plan's collection 6 871.00
  instead of 3 295.00 — a different reconciliation. All three tiers now read "a payment **posted on the
  account** reached the cooperative by bank transfer", which pins the row family the binding filters on
  (`event_type='energy_payment_posted'`). Compute unchanged; no figure moved, because the binding was
  always the narrow one.

**The same question asked of the rest of the charter.** Three further places were found where a rule names a
quantity the records carry in more than one form; **all three are inert on these worlds, and each is
recorded below as an observation rather than a red light because no second number exists on either task.**

- **N6 — two date fields per ledger row.** Every `energy_deliveries` row carries `delivery_date` and
  `posted_date`, and the charter's own event definitions distinguish them ("the date the payment was
  received" vs "the date the payment was posted to the energy account"). The bindings choose deliberately
  and inconsistently — `energy_ext_budget_year_reconciliation` reads `posted_date` for
  `fuel_posted_year`, `drawdown_money_year` and `fees_year` but `delivery_date` for `gallons_year`,
  `instalments_year` and `drafts_year`; `energy_ext_account_clearance_payment` reads `posted_date` for the
  amount standing and `delivery_date` for `last_payment_date` — while the prose says only "billed",
  "taken", "posted on the account" and "last paid". One phrase pulls the other way from its binding:
  "the date of the most recent payment **posted on the account**" is bound to `delivery_date`.
  **Inert:** `delivery_date == posted_date` on all 41 rows of task 0's world and all 18 of task 1's
  (checked row by row), so no reading produces a second number. That inertness is a property of the seeds,
  not of the prose.
- **N7 — two date fields on a request row.** `energy_orders` carries `requested_date` ("the date the member
  asked the work to happen on") and `received_at` ("moment the energy desk registered the request"), and
  both `energy_ext_prebuy_booking_credit` and `energy_ext_contract_price_of_record` speak of the request
  having "stood **registered**", which points at `received_at`, while the bindings read `requested_date`.
  The round-2 T1 price sentence ("on or before the day the signed request was registered") inherits this.
  **Inert:** on task 1's world the one request carries `requested_date: 2025-11-20` and
  `received_at: 2025-11-20 09:12:00 CST` — the same day — so both readings give 2.9800 and 11 months.
- **N8 — "the bookings standing on the account".** `energy_ext_contract_price_of_record`'s weighted average
  is bound to every `energy_contract_gallons_booked` row, while "standing" could be read as the bookings
  with gallons still undrawn. **Inert:** task 1's account carries exactly one booking, so the two readings
  coincide.

### action_binding_and_uuids (carried forward by reference)

`task_tools.py` is unchanged at `d06a6d6cbb874e26`, the hash that revision 2 verified in full. That hash is
the grounds for carrying this section forward without re-deriving it: the seven frozen uuid8s, the owners,
the empty-of-judgement bodies, the docstrings' silence about sequence and the one-policy-per-`(target_tool,
computes)` claim all stand as recorded in `_difficulty.md` § revision_2 → `action_binding_and_uuids`. No
round-3 change touches the tool module.

### prerequisite_graph and prerequisite_sentences (re-derived)

Same five edges, same targets, gates, kinds and forms; still a DAG of two disjoint components. All five
`policy_source` sentences re-checked as verbatim substrings of the **blocked** policy's own rule after the
round-3 rewrites — all pass. `energy_ext_closure_settlement`'s sentence is unchanged from revision 2 and
was deliberately not touched by P2; the reasoning is verified above. No rule carries a second wording of a
dependency, and no depended-on rule restates one.

### factor_ladders (re-derived)

36 factors, counts unchanged and inside the bounds on every policy (5 / 6 / 4 / 6 / 5 / 6 / 4, each with ≥2
`parameter` and ≥1 `method`), every ladder three tiers, every tier condition present in its own rule, every
residual matching `compute`'s `else`, every fall-through equal to its `baseline`, every label honest, every
`method` tier naming a rule the charter states.

`undrawn_holdback_basis` was re-examined in full after P1: its `bindings` list correctly tracks the binding
change (`last_gauge_after` → `last_gauge_before`); its three tiers still partition
(keep-full ∧ ≥3 stops / keep-full ∧ <3 stops / not keep-full); its three methods remain distinct as methods
and, on task 0's world, distinct in value (360.0 / 300.0 / 0.0); tier 1 is still multi-source (the
enrolment field **and** the twelve-month stop count, over distinct records); and the baseline is still the
residual tier. Per-task multi-source and cross-difficulty floors are unaffected.

### findings (revision 3)

**P1, P2, P3 and runtime openness (ii) — CLOSED**, each verified against the artifacts and the records
rather than against the reworker's account. **F1–F6, C1, T1 and O1–O9 — remain closed**; nothing that
revision 2 passed has regressed. **N1–N5 (revision 2) and O5 (revision 1)** stand unchanged as
observations. **D2** was not assessed: the brief assigns it to the re-render as a document-side item, and
the published KB is outside this audit's read domain.

Three new observations, **N6**, **N7** and **N8**, are set out under `rule_compute_equivalence` above. None
is a red light: each names a phrase that a reader without the binding could read two ways, and in each case
the seeded world makes both readings give the same number, so no second answer exists to demonstrate. They
are recorded because they are the same shape as P1, and because their inertness rests on the seeds rather
than on the prose — a different world would make any of them live.

### closing_checklist (revision 3)

Written after both tasks' `source_gt_comparison` (revision 3) sections were on disk, 2026-09-18T12:29Z.

**The difficulty closes out again.**

| # | Step 4 item | result |
| --- | --- | --- |
| 1 | per-task files one-to-one with the tasks; `_difficulty.md` alongside; old revisions traceable; every comparison carries a PASS | **PASS** — revisions 1, 2 and 3 are stacked in all three files with no earlier text rewritten; both revision-3 comparisons carry PASS on all four relationships |
| 2 | extended policies fully covered; scopes pairwise disjoint; task tools and GT closed; each tool an independently generated, frozen uuid8 | **PASS** — 3 + 4 = all 7, disjoint; 7 tools, one per policy; `task_tools.py` unchanged at `d06a6d6cbb874e26`, so the uuid8 conclusion is carried forward on that hash |
| 3 | every task's tree 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle; the difficulty's edges a DAG | **PASS** — task 0: n = 2, 2 `value_input`; task 1: n = 3, 3 `value_input`; both roots still blocked at frozen_time, P2 having deliberately left the root sentence of task 1's tree untouched |
| 4 | every computation a self-sufficient baseline and 4–6 factors (2 `parameter`, 1 `method`; per task ≥1 multi-source and ≥1 cross-difficulty), ladders ≥3 tiers stated in full, tiers distinct, conditions and outcomes ones the business holds, every factor bearing weight against an honest baseline, the baseline alone definite and different from gold | **PASS** — 36 factors, every one recomputed as bearing weight on its own task's world; all seven whole-baseline fall-backs definite and different from gold (196.30, −850.35, **3783.05**; 5742.0, 2.98, 15369.0, 2878.74). The P1 fix **strengthened** this item: `undrawn_holdback_basis` now moves task 0's scored credit by 88.45 instead of 14.74, and computation A's gap between the computation document's answer and gold widened |
| 5 | this difficulty's instantiation-stage gates re-run once on the final form | **PASS (cited, not run here)** — the orchestrator's block of 2026-09-18T12:47 is green on `cd7e53bc04a9322a` / `d06a6d6cbb874e26`. `replay_tasks.py` was not run by this auditor, as instructed, and `check_traceability` is re-run by the render loop after the energy KB is re-rendered |

**Difficulty-level verdict, revision 3: policy self-consistency PASS + problem tree holds PASS + factors
bear weight PASS + unique solution PASS, on both tasks. The source-layer audit is passed.**

Outstanding items are observations only: **N6**, **N7**, **N8** (revision 3), **N1**–**N5** (revision 2)
and **O5** (revision 1). **D2** is not assessed here — the brief assigns it to the re-render as a
document-side item, and the published KB is outside this audit's read domain.

**One note for the next round of this difficulty, arising from the occasion rather than from the items.**
The defect the render layer caught was invisible to a reader holding the `compute`, and this audit had
passed it twice. Check 2 as this auditor now runs it asks not only "is every quantity in the rule
implemented by a binding, and every binding grounded in a sentence" but "**would this sentence pick out this
binding for a reader who cannot see it**". The sweep under that question over the whole charter found
exactly three surviving candidates — N6, N7 and N8 — and each is inert only because the seeds make its two
readings coincide. A future task on a world where a payment's `posted_date` differs from its
`delivery_date`, where a request's `received_at` falls on a different day from its `requested_date`, or
where an account carries more than one booking, would make one of them live.
