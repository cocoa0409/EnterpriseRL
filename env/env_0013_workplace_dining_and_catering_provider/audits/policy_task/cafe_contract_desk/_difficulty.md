# Policy-task audit — cafe_contract_desk / charter-global

## charter_global_frozen

- freeze time: 2026-09-22, written **before any task's GT fields were read**.
- auditor: independent policy-task auditor (erl-task-policy-audit), no involvement in instantiation.
- freeze hashes of the shared sources:
  - `sha256 c4b3d62041e6965c519131178a828a99184b2a6202700c3e92bfff604bfc18da  tasks/cafe_contract_desk/cafe.extended.yaml`
  - `sha256 0c5daaa7c79236aa199048f819fc0ecd3189dbf286330a6a94cba435f04dbe34  tasks/cafe_contract_desk/task_tools.py`
  - both recomputed on disk and identical to the coordinator's brief.
- masked views used for every derivation (hashes recomputed, both match the brief):
  - `0.masked.json  ef69ede675c47235a42cac61eeda444bf4b6696d5ab661bcac5d9d4a47e858f8`
  - `1.masked.json  b22fbfdfdf1844eb4a124db75781a232d206c83d25aff1a6ba26cfa815b4a67f`
- **fields permitted**: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`,
  `blueprint/products/cafe.yaml` (+ `pantry.yaml` and `market.yaml` for the cross-category reads the charter
  declares), the whole of `cafe.extended.yaml` (base section, `extended_policies`, `rule`, `compute`,
  `compute_basis`, `overwrite`, `prerequisite`, `factors`, `baseline`, `inputs`), `task_tools.py`,
  `erlbench/`, and each task's `frozen_time` / `user_scenario` / `initial_state` only.
- **fields explicitly masked** and not read before the freeze: `evaluation_criteria`, `computations`
  (expected, factor_trace, factor_sensitivity, baseline_result, step/arg), `charter_scope`,
  `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`,
  `db_closure`, `db_closure_matches_initial_state`, and every earlier audit conclusion.
- contamination: none. No search whose path scope included `env/.../tasks/*.json` was run while any
  derivation was unfrozen; the only task data read was the coordinator's mechanically masked views.
- entry conditions (step 0): the brief supplies the six instantiation-stage gate commands with their
  actual output lines, all green (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE,
  GROUNDING, SCOPE), the masked views and their hashes, and the shared-source hashes.
  `check_traceability.py` is absent with a stated reason (it reads a KB that the render step has not
  yet produced). **Entry conditions complete.** The gates were cited, not re-run by this auditor.

---

### policy_conflict_scan

The difficulty's structured policy is the verbatim base section of `blueprint/products/cafe.yaml`
(lines 1–799 of the extended file; `diff` against the blueprint is empty — the base copy is
**verbatim identical**, so no base sentence has been rewritten) plus seven `extended_policies`:

| id | subject | target_tool | computes | prerequisite |
| --- | --- | --- | --- | --- |
| cafe_ext_model_change_confirmation | cafe_service_model_changed | confirm_service_model_change_fa28a84a (owner=user) | change_admin_fee_usd | [] |
| cafe_ext_management_fee_invoice | cafe_management_fee_invoiced | raise_management_fee_invoice_00d6d0cf | amount_usd | model_change_confirmation |
| cafe_ext_service_credit_settlement | cafe_service_credit_issued | issue_service_credit_9f99d1a6 | credit_amount_usd | management_fee_invoice |
| cafe_ext_late_charge_assessment | cafe_penalty_fee_posted | post_late_charge_719c9a63 | late_charge_usd | [] |
| cafe_ext_early_exit_charge | cafe_penalty_fee_posted | post_early_exit_charge_dadd74c6 | exit_charge_usd | [] |
| cafe_ext_standby_charge_assessment | cafe_penalty_fee_posted | post_standby_charge_21704194 | standby_charge_usd | [] |
| cafe_ext_closing_settlement_payment | cafe_invoice_payment_posted | settle_contract_balance_f9be2425 (owner=user) | settlement_amount_usd | late_charge, early_exit, standby |

**Overlapping subjects.** Three policies share the subject event `cafe_penalty_fee_posted`
(late charge / early exit / standby). They are separated by target tool and by the `charge_code` their
tool writes (`late_fee` / `early_termination_fee` / `standby_fee`), and none of their computations reads
a binding the others write, so the overlap creates no conflicting conclusion. The base policy
`cafe_participation_guarantee` also carries subject `cafe_penalty_fee_posted` and a live formula
(`shortfall_points * participation_shortfall_fee_per_point_usd`); it is listed in the
`base_policy_refs` of policies 4, 5 and 6 but is overwritten by none of them and claimed by no
extended policy. It governs a different charge and so is not a conflict — recorded as
**OBS-D1** below.

**Triggers / eligibility / time anchors / terminal states / cross-category reads.** `trigger` is
`state_due` for five policies and `on_request` for the service credit and the closing settlement;
`on_request` matches a customer-raised root in both tasks. Cross-category read boundaries are
declared exactly: `pantry` (history: status + pantry_ledger.amount_usd) on policy 2, `market`
(history: status + market_ledger.amount_usd) on policies 5 and 7, `[]` elsewhere, and each
declaration matches the `CFIELD`/`XSUM` calls actually made. No extended policy reads a category it
has not declared.

**Scope exclusivity and completeness of the M tasks.** Task 0's problem tree spans
{cafe_ext_service_credit_settlement, cafe_ext_management_fee_invoice,
cafe_ext_model_change_confirmation}; task 1's spans {cafe_ext_closing_settlement_payment,
cafe_ext_late_charge_assessment, cafe_ext_early_exit_charge, cafe_ext_standby_charge_assessment}.
The two sets are **pairwise disjoint** and their union is **all seven** extended policies.

---

### rule_compute_equivalence

Check 2 was run binding by binding over all seven policies: every binding of every `compute` carries a
`compute_basis` entry, and every entry is a verbatim sentence of that policy's own `rule`. The sweep
back (rule sentence → is it implemented?) found the ladders all implemented. **Three divergences**
were found where `compute` implements something the `rule` does not state, or states something
`compute` does not implement:

- **F-D1 (SOURCE-POLICY RED)** — *policy 7, `smallwares_credit_usd`: compute divides by twelve where
  the rule multiplies.* The rule's only sentence on this quantity (also its `compute_basis` entry) is
  "…half the smallwares allowance printed against the service model is credited back **for each whole
  month of the contract year still to run**…". `compute` implements
  `RND(P('smallwares_allowance_usd') * smallwares_share_pct / 100 * (12 - contract_year_elapsed_months) / 12, 2)`.
  The trailing `/ 12` appears in no sentence of the rule, of `baseline.rule` or of `compute_basis`, and
  "for each whole month still to run" is a multiplication, not a pro-ration. A reader who follows the
  rule gets twelve times the figure `compute` produces. Consequence demonstrated against task 1's world
  in `1.md` (settlement 115,231.90 under the rule vs 150,431.90 under compute — a 35,200.00 gap).
  Location: `cafe.extended.yaml` policy `cafe_ext_closing_settlement_payment`, `compute` binding
  `smallwares_credit_usd` and `compute_basis.smallwares_credit_usd`. **Bears on task 1.**

- **F-D2 (SOURCE-POLICY RED)** — *policy 2, `base_fee_usd`: an un-stated rounding step on an exact
  half-cent, with no tie-break anywhere in the charter.* The rule sentence is "…the base fee is the
  **mean** of the monthly management fee printed against the service model standing on the contract and
  the management fee most recently invoiced on the contract…" — no rounding is mentioned; `compute`
  implements `RND((P('management_fee_monthly_usd') + latest_mgmt_fee_usd) / 2, 2)`. Neither the rule,
  `compute_basis` nor `baseline.rule` states a rounding mode or a tie-break, and the only rounding
  sentence in the policy ("rounded to the nearest cent") sits on `escalated_fee_usd` and `result`.
  Consequence demonstrated against task 0's world in `0.md` (the mean falls exactly on 7,265.265;
  half-up gives 5,035.72 and the float `round()` gives 5,035.71). **Bears on task 0.**

- **OBS-D2 (observation)** — *policy 5, `highest_mgmt_fee_usd`: window dropped.* The rule and the
  `exit_fee_base_band` ladder both say "**the highest of them**", i.e. the highest of the management fee
  invoices standing **in the six months up to the day the charge is raised**; `compute` implements
  `MAX('cafe_ledger','amount_usd', charge_code='management_fee')` with no window, and
  `inputs.history` declares that aggregate with `within_months: null`. On task 1's seeded world the
  all-time maximum (18,096.00) equals the six-month maximum, so no consequence can be demonstrated on
  either seeded world; recorded as an observation, not a red light.

---

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above); no tool and no
  computed quantity is claimed twice.
- Every task tool's docstring describes one atomic write, names no other tool and states no position in
  a sequence. `raise_management_fee_invoice_00d6d0cf`'s Returns paragraph contains "…the reference
  anything **later** raised against this invoice is quoted on…" — an ordering word, but about future
  postings against an invoice number rather than about this action's place in a sequence, and it names
  no tool. Recorded as **OBS-D3**, not a red light.
- Reading every function body confirms that **no tool validates a prerequisite**: each one does
  `ctx.find` → `ctx.update` → `ctx.create` → return. None refuses, errors, warns, or branches on the
  contract's status, on the presence of another posting, or on any gate.
- uuid8s: `fa28a84a`, `00d6d0cf`, `9f99d1a6`, `719c9a63`, `dadd74c6`, `21704194`, `f9be2425`. Seven
  distinct values, no shared prefix, no shared tail, no sequence, no arithmetic relation — each looks
  independently generated and is frozen with its tool.
- **OBS-D4 (observation)** — `cafe_ext_model_change_confirmation` declares `subject: [cafe_service_model_changed]`,
  but `confirm_service_model_change_fa28a84a` writes its ledger row with
  `event_type="cafe_management_fee_invoiced"`, `charge_code="admin_fee"`. The declared subject event and
  the event the tool actually records differ. No scored quantity in either task turns on it (policy 7's
  `penalty_charges_3m` filters `cafe_penalty_fee_posted`, and every management-fee aggregate filters
  `charge_code='management_fee'`), so it is an observation.

---

### prerequisite_graph

Check 7 over the whole `prerequisite` graph.

- Every extended policy has `prerequisite` filled in; four carry `[]`, three carry edges.
- Every `problem` points at another **extended** policy id in this file, never at a base policy and
  never at itself.
- Edges: 2→1, 3→2, 7→4, 7→5, 7→6. The graph is a forest of two chains and is **acyclic**; no edge
  crosses between the two tasks' scopes, so the difficulty-wide graph stays a DAG.
- `form` is `state` on all five edges; `fallback_reason` is present on none, which is correct because
  none is `action`. The state form's priority is therefore honoured on every edge.
- `kind` is `value_input` on all five and `gate` names a real binding of the blocked policy's own
  `compute` in each case (`base_fee_usd` in policy 2; `fee_base_usd` in policy 3;
  `unsettled_balance_usd` in policy 7, three times) — never `result`.
- `resolved_by` is in each case the depended-on policy's own `target_tool`, and each named tool does
  in fact bring the `effect` about (verified against the function bodies:
  `confirm_service_model_change_fa28a84a` sets `variant_name` and
  `service_model_change_effective_date`; `raise_management_fee_invoice_00d6d0cf` creates a
  `management_fee` ledger row; the three penalty tools each create a `cafe_penalty_fee_posted` row and
  raise `receivable_balance_usd`, which is exactly what `F('receivable_balance_usd')` reads).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in
  any `prerequisite` field.
- **OBS-D5 (observation)** — the `effect` text on the 7→4 edge asserts "…the contractual charges
  counted in the three month window rise by one, **which also moves the equipment deposit returned**".
  On task 1's world the count rises from 2 to 3 and the `equipment_deposit_return_band` tier
  ("two or more…") is unchanged, so the deposit does **not** move. As general text the sentence is
  conditionally true; the falsification against task 1's world is recorded in `1.md`.
- **F-D3 (SOURCE-POLICY RED)** — three edge `condition`s are written so loosely that, read against the
  raw DB, they are satisfied at the opening. See `prerequisite_sentences` below and the per-task
  demonstrations; the 3→2 edge is fatal on task 0.

---

### prerequisite_sentences

Check 6, four-point test, edge by edge.

**Edge 2→1** — `policy_source`: *"The management fee for a billing period is not worked out before the
service model standing on the contract is the one named on the contract's approved change of service
model."*
Located verbatim in `cafe_ext_management_fee_invoice.rule` (its own rule) ✔. Ordering connective
"before" ✔. What it waits on is a record-visible state ("the service model standing on the contract is
the one named on the contract's approved change of service model"), stated in the words the tables and
finders use, with no performer and no action ✔. No tool name, policy id, snake_case token or row id ✔.
Exactly one write of this difficulty brings that state about: only
`confirm_service_model_change_fa28a84a` writes `cafe_contracts.variant_name` ✔. The derivation a reader
must make — *sentence → the contract's `variant_name` differs from the approved request's
`requested_variant_name` → which policy's rule describes putting the approved change into force
(`cafe_ext_model_change_confirmation`, "A change of service model that the client has already approved
is put into force on the day the client confirms it") → its `target_tool`* — has exactly one reading ✔.
Strength matches the `condition` ✔. **PASS.**

**Edge 3→2** — `policy_source`: *"The credit allowed is not worked out until a management fee invoiced
for the billing period the claim concerns stands on the contract's ledger."*
Verbatim in `cafe_ext_service_credit_settlement.rule` ✔; connective "until" ✔; state form, no tool name
✔; uniquely resolved by `raise_management_fee_invoice_00d6d0cf` ✔. **But the `condition` it carries** —
"a cafe_ledger row of charge_code management_fee whose service_period is the billing period the claim
concerns stands against the contract" — **is already true at the opening of task 0 for every approved
claim the computation counts.** Demonstrated in `0.md`: SOURCE-CHAIN RED.

**Edges 7→4, 7→5, 7→6** — sentences: *"The closing settlement is fixed only after the late charge owed
on the contract's overdue invoice stands on its ledger."* / *"Before the closing settlement is worked
out, the early exit charge due on the contract ending ahead of its term must stand recorded against the
contract."* / *"The closing settlement is not worked out until the standby charge owed for the months
the cafe has stood suspended stands on the contract's ledger."*
All three are verbatim in `cafe_ext_closing_settlement_payment.rule`, carry "only after" / "Before" /
"until", are in the state form, name no tool, and are each resolved by exactly one write of this
difficulty (`post_late_charge_719c9a63` is the only writer of `charge_code='late_fee'`,
`post_early_exit_charge_dadd74c6` the only writer of `early_termination_fee`,
`post_standby_charge_21704194` the only writer of `standby_fee`). The derivation has one reading in
each case. **The sentences pass**; two of the three `condition`s are under-specified about *which*
invoice / *which* suspended months, so rows of the named charge_code already stand at task 1's opening —
demonstrated and graded in `1.md`.

**No second wording, no cross-problem order beyond the declared edges.** Each dependency is stated once
and only in the blocked policy's own rule. The depended-on policies' rules do not restate it: policy 1's
rule says nothing about the management fee invoice; policy 2's rule says nothing about the credit;
policies 4, 5 and 6 say nothing about the closing settlement. No rule of any extended policy states a
cross-problem order that grounds no declared edge.

**Base rule sentences that state a cross-problem order.** `cafe_service_suspension_terms` carries "…and
the management fee itself is not raised for the same period" and `cafe_management_fee_calc` carries "on
a suspended contract the standby charge replaces the management fee for that period and the management
fee is not raised at all". Neither grounds any declared edge and neither is relied on by any task's tree,
so under check 6 these are **observations (OBS-D6)**, not red lights. They do constrain what a task may
seed; both seeded worlds are consistent with them (no management fee stands for a month that carries a
standby charge).

---

### override_declarations

Check 1's finding half, sentence by sentence against every `base_policy_refs` entry. The base copy is
verbatim identical to the blueprint, so every deviation must be declared on the extended side.

**cafe_management_fee_calc → policy 2.** Sentences 1, 2 and 3 are each named in `overwrite` and
replaced ✔. Sentence 4 ("A management fee is only invoiced while the contract stands in mobilizing,
active, suspended or in_transition_out; on a suspended contract the standby charge replaces the
management fee…") is inherited in full and is not weakened by extended. Sentence 5 (admin fee on
invoiced food cost on a cost_plus or fixed_fee basis) is inherited; extended computes only the
management fee and no tool invoices food cost, so no quantity is fought over — **OBS-D7**.

**cafe_agg_portfolio_fee_band → policy 2.** The mechanism sentence ("The band is found by counting…")
is named and replaced ✔. Its first sentence ("The management fee a client pays on each cafe contract is
discounted by a portfolio band…") is **not** named, but the `replaced_by` text says outright "…in place
of any portfolio band discount", so a reader is told no portfolio discount applies. Adequately
declared; **OBS-D8** records the un-named sentence.

**cafe_combination_pantry_interaction → policy 2.** The administration-fee exemption sentence is named
and replaced by the co-location ladder ✔. The other three sentences (micro-market subsidy pooling,
executive-dining exclusivity, exemptions stopping at the next invoice) are inherited and are not
contradicted by any extended text.

**cafe_service_model_change → policy 1.** Sentences 2 and 4 are named and replaced ✔.
Sentence 3 — *"A move to a lower ranked service model is only accepted once the cooldown printed
against the model in force has passed since the last change of service model on this contract."* — is
**inherited and not overwritten**, while policy 1's own rule handles a change within twelve months of an
earlier change by **charging the repeat change administration fee** rather than refusing it. Base says
*not accepted*; extended says *accepted at a higher fee*. This is a live contradiction for any downgrade
within the cooldown. **On task 0 the move is Limited Service Cafe (rank 2) → Full Service Cafe (rank 3),
an upgrade, so the contradiction does not bite on either seeded world** — recorded as **OBS-D9**
(observation, no demonstrable consequence), not a red light.
Sentence 5 ("From the effective day the whole parameter column of the new service model applies… and no
parameter of the old model survives the change") is inherited, and it is what makes policy 1's own
phrase "the service model **in force** on the day the client confirms" ambiguous — see **F-D4** below.
Sentence 6 (entry-gate decline) is inherited; `cafe_contracts` carries `headcount_served` but no annual
food spend, kitchen or loading-access field, so two of the four entry-gate conditions cannot be
evaluated from the records at all — **OBS-D10**.

- **F-D4 (SOURCE-POLICY RED)** — *policy 1: "the service model in force on the day the client confirms"
  does not pick out one model.* Policy 1's own first sentence puts the change "into force **on the day
  the client confirms it**", and inherited base sentence 5 says that from the effective day the whole
  parameter column of the new model applies and no parameter of the old survives. So on the confirmation
  day both the model being left and the model being moved to are "in force", and the rule nowhere says
  which. The base sentence the first `overwrite` replaces said the fee is "the administration fee printed
  against **the model being moved to**", which points the reader at the new model; `compute` reads
  `P(...)`, which is the old model. Three bindings turn on it —
  `P('service_model_change_fee_usd')`, `P('mobilization_fee_usd')` and
  `P('service_model_change_lead_days')`. Consequence demonstrated against task 0's world in `0.md`
  (8,066.07 under the old-model reading vs 20,994.73 under the new-model reading). **Bears on task 0.**

**cafe_service_credit_terms → policy 3.** Sentences 2, 5 and 6 are named and replaced ✔. Sentence 7
(ceiling allowed, balance closed) is inherited and matches `MN(...)` ✔. Sentence 1 is inherited and
consistent.
- **F-D5 (SOURCE-POLICY RED)** — *sentences 3 and 4 are an undeclared override.* Base:
  *"A service credit is allowed only when the claim reaches Larkspur Table no later than the claim window
  for the service model, counted in calendar days from the day the invoice covering the missed meal
  period was posted."* and *"Claim window days are counted as calendar days from the day after the
  invoice posting day…"* — a per-model window in **calendar days** (14/21/30/30/45/30) anchored on **the
  covering invoice's posting day**. Extended's `claim_window_basis` counts approved claims over a window
  in **months** (3 / 6 / 12) anchored on **the day the credit is worked out**. Both decide the same
  quantity — which claims count toward the credit — and neither base sentence is named in policy 3's
  `overwrite`. Base and extended are rendered into the KB together, so the agent has two live rules for
  one quantity. Consequence demonstrated against task 0's world in `0.md`. **Bears on task 0.**

**cafe_invoice_payment_terms → policies 4, 5, 7.** Policy 4 names and replaces the late-charge formula
sentence and the partial-payment sentence ✔; policy 7 names and replaces the over-payment sentence ✔.
The remaining sentences (invoices fall due N days after the invoice date; a late charge only on a
non-closed contract; one late charge per invoice per month and none while a written dispute stands;
credit hold at the past-due threshold) are inherited, and neither seeded world contradicts them.

**cafe_termination_terms → policies 5 and 7.** Policy 5 names and replaces the two early-exit-charge
sentences ✔; policy 7 names and replaces the closure-settlement sentence ✔. The inherited sentences
("Only the client may terminate…"; "Notice is handled on a contract that stands active, suspended or
already in transition out…"; the notice-period and day-counting sentences; "A proposal that never
reached countersignature closes without notice…") are not weakened by extended.
- **OBS-D11 (observation)** — policy 5's second `overwrite` names the base sentence *"Where the closure
  day falls on or after the end of the contracted term and the renewal notice was exchanged in time, no
  early exit charge falls due."* and replaces it with the **notice-relief ladder**, which governs a
  different quantity. After the replacement the charter carries no rule at all for a closure on or after
  the term end. Neither seeded world has such a closure, so no consequence is demonstrable.

**cafe_service_suspension_terms → policy 6.** Sentences 3 and 6 are named and replaced ✔.
- **F-D6 (SOURCE-POLICY RED / SOURCE-FACTOR)** — *inherited base sentence 2 and policy 6's fall-through
  tier contradict each other, undeclared.* Base: *"…a pause **shorter than the minimum suspension**
  printed against the service model **is handled as ordinary closed days rather than as a suspension**."*
  Policy 6's ladder fall-through — stated in its own rule as "…and where the suspended days counted do
  **not exceed** the shortest suspension printed against the service model, **one month of pause is
  charged**" and implemented as `else 1` — charges a full month of standby for exactly the pause base
  says is not a suspension at all. The base sentence is named in no `overwrite`. It is also the factor
  `pause_month_count_basis`'s fall-through, so the fall-through tier is a treatment the charter's own
  base rule says is not given. Task 1's world takes tier 1 (44 suspended days > the 14-day minimum), so
  no consequence is demonstrable on either seeded world; graded as a **charter-global finding with no
  per-task consequence** and carried into the closing checklist rather than into a task verdict.

---

### factor_ladders

Structure only. Thirty-four factors over seven policies; every `decides` names a compute binding that is
an input to a later binding, never `result`; every factor's `bindings` list is disjoint from every other
factor's within its policy; every ladder has exactly three tiers, pairwise disjoint as stated; and every
tier of every ladder is a sentence of its policy's own `rule` and a branch of the `decides` binding's
`compute` expression, and every branch of those expressions is a tier the rule states — no tier lives
only in `compute`, and no branch is unstated.

| policy | factors | parameter | method | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| 1 model change | 4 | 3 | 1 | change_administration_fee_band, opening_project_settlement_band, short_notice_charge_basis, account_exposure_loading_band | — |
| 2 management fee | 6 | 4 | 2 | transition_period_base_fee, settlement_record_escalation_rate, pantry_colocation_allowance, suspended_day_relief_basis, subsidy_commitment_surcharge | **pantry** |
| 3 service credit | 5 | 3 | 2 | claim_window_basis, client_closure_set_aside, credited_meal_period_basis, credit_fee_base_basis | — |
| 4 late charge | 4 | 2 | 2 | outstanding_amount_basis, overdue_clock_anchor, grace_days_band, arrears_rate_band | — |
| 5 early exit | 4 | 3 | 1 | unrun_term_exit_months, exit_fee_base_band, notice_relief_basis, continuing_outlet_allowance | **market** |
| 6 standby | 5 | 3 | 2 | suspended_day_count_basis, pause_month_count_basis, standby_rate_band, standby_fee_base_band, late_resumption_loading_band | — |
| 7 closing settlement | 6 | 4 | 2 | equipment_deposit_return_band, drawable_funding_refund_basis, opening_inventory_recovery_band, outlet_carry_over_band, smallwares_credit_band | **market** |

Every policy declares 4 to 6 factors with at least 2 `parameter` and at least 1 `method` ✔.
Per task: task 0's policies carry a multi-source factor and one `cross_difficulty: pantry` factor ✔;
task 1's carry multi-source factors and two `cross_difficulty: market` factors ✔.

**Label honesty.** Every `method` factor changes an algorithm rather than a number, and each belongs to
one of the recognised method families: `short_notice_charge_basis` and `suspended_day_relief_basis`
(scaling + day-count), `escalation_step_anchor`, `overdue_clock_anchor` and `contract_year_anchor`
(anchor), `claim_window_basis` (window), `credited_meal_period_basis`, `outstanding_amount_basis`,
`drawable_funding_refund_basis`, `suspended_day_count_basis`, `pause_month_count_basis` and
`notice_relief_basis` (day-count / candidate-order). No `method` tier names a computation rule the
charter does not state. No `parameter` factor's tiers change how the quantity is computed.

**Tier distinctness.** No two tiers of any one ladder select the same value or the same method as
stated. Five ladders can collapse on a *particular* world (e.g. `standby_fee_base_band`'s "most recently
invoiced" and "mean of the three months" coincide on task 1 at 18,096.00) but they are distinct as
stated, which is the test.

**Fall-through = baseline.** Two failures:

- **F-D7 (SOURCE-FACTOR)** — *`pause_month_count_basis` (policy 6): the fall-through is not the
  baseline.* `baseline.rule` says "the months of pause charged are those suspended days divided by
  thirty and rounded down to a whole month with a minimum of one" and the factor's declared `baseline`
  is `MX(1, int(suspended_days_counted / 30))` — agreeing with each other but **not** with the ladder's
  fall-through, "one month of pause is charged" (`else 1`). The fall-through region includes any
  contract with **no** approved suspension request and any number of suspended days, where `else 1`
  gives 1 and the baseline gives `floor(days/30)`. Task 1 takes tier 1, so no per-task consequence.
- **F-D8 (SOURCE-FACTOR RED)** — *`contract_year_anchor` (policy 7): a dishonest baseline.* The
  policy's `baseline.rule` states "The contract year elapsed is the whole months between the first day
  of the contract term and the day the settlement is worked out" — i.e. `term_months`, unreduced, which
  is also exactly the ladder's fall-through tier. The factor's declared `baseline` is
  `term_months % 12`, a different figure. Consequence demonstrated against task 1's world in `1.md`,
  where the two readings give 152,565.23 and 158,965.23, and where `baseline.rule` read on its own
  makes "the whole months of the contract year still to run" equal **−10**, so the baseline computation
  yields a negative credit. **Bears on task 1.**

**Baseline self-sufficiency.** Each policy's `baseline.rule` is a complete method and each of its
sentences is in the `rule` — with the exception noted in F-D8, and with **OBS-D12**: policy 2's
`baseline.rule` contains both "No co-location allowance, no suspended day relief and no subsidy
commitment surcharge is taken on the escalated fee" and, immediately after, "The co-location allowance
and the suspended day relief are each worked out on the escalated fee and subtracted from it…". The two
sentences read as contradicting each other; because the three fall-through rates are all nil they give
the same number, so no consequence is demonstrable.

**Condition and outcome realism.** Every tier condition names something a contract caterer can read off
its own records (an earlier model change, invoices raised in a window, payments and credits received,
suspended days, subsidy lots funded, a termination notice, whether the client also holds a pantry or a
micro market at the site) and none holds of every customer who reaches the write. The outcomes — a
repeat-change administration fee, a settled-account escalation rate, a co-location allowance for a client
who also buys a pantry programme, a retained share of the equipment deposit where contractual charges
stand — are treatments a contract dining business does publish. Two are thin:
**OBS-D13**, `short_notice_charge_basis` and `unrun_term_exit_months` both split on "whether a management
fee invoice was raised in the last two/three months", which is a proxy for "is the cafe trading" rather
than something a caterer would weigh when setting a short-notice charge or an exit term; and
**OBS-D14**, the fall-through of `pause_month_count_basis` (see F-D6/F-D7). Neither carries a
demonstrable consequence on the seeded worlds.

**Cross-difficulty evidence seeding.** Task 0 seeds `pantry_agreements` (1 row, active) and
`pantry_ledger` (15 rows); task 1 seeds `market_agreements` (1 row, active) and `market_ledger` (16
rows). The rows the `XSUM` reads are present in both. One is inconsistent with the other product's own
charter — **F-D9**, recorded under `findings` and demonstrated in `0.md`.

---

### findings

| id | verdict | one line | tasks |
| --- | --- | --- | --- |
| F-D1 | SOURCE-POLICY RED | policy 7's `smallwares_credit_usd` divides by twelve where its only rule sentence says "for each whole month still to run" — a reader following the rule gets twelve times the compute's figure | 1 |
| F-D2 | SOURCE-POLICY RED | policy 2's `base_fee_usd` applies an un-stated `RND(...,2)` to a mean, and the charter states no tie-break for a value that lands exactly on a half-cent | 0 |
| F-D3 | SOURCE-POLICY RED | three edge `condition`s ("the billing period the claim concerns", "the overdue invoice", "the suspended months") do not identify the row they require, so rows of the named charge_code already stand at the opening | 0 (fatal), 1 |
| F-D4 | SOURCE-POLICY RED | policy 1's "the service model in force on the day the client confirms" picks out neither model, and the base sentence it replaced said "the model being moved to" | 0 |
| F-D5 | SOURCE-POLICY RED | base `cafe_service_credit_terms`' calendar-day claim window anchored on the covering invoice is overridden by extended's month-window anchored on the working day, with no `overwrite` entry | 0 |
| F-D6 | SOURCE-POLICY RED (charter-global; no seeded consequence) | base "a pause shorter than the minimum suspension is handled as ordinary closed days rather than as a suspension" is contradicted, undeclared, by policy 6's fall-through "one month of pause is charged" | — |
| F-D7 | SOURCE-FACTOR (charter-global; no seeded consequence) | `pause_month_count_basis`'s fall-through (`1`) is not its baseline (`MX(1, int(days/30))`) | — |
| F-D8 | SOURCE-FACTOR RED | `contract_year_anchor`'s declared baseline `term_months % 12` is not what policy 7's `baseline.rule` states (`term_months`), and that rule read alone gives −10 months still to run | 1 |
| F-D9 | SOURCE-FACTOR RED | task 0's seeded `pantry_ledger` posts a 1,790.00 monthly `program_fee` where `pantry.yaml` prints 4,180.00 for "Full Hospitality Pantry Program" — the cross-difficulty factor reads rows that contradict that product's own charter | 0 |
| OBS-D1 | observation | base `cafe_participation_guarantee` shares the subject `cafe_penalty_fee_posted` and carries a live formula, is listed in three policies' `base_policy_refs`, and is overwritten and claimed by none | — |
| OBS-D2 | observation | policy 5's `highest_mgmt_fee_usd` drops the six-month window the rule and the ladder both state (`within_months: null`); the two agree on both seeded worlds | — |
| OBS-D3 | observation | `raise_management_fee_invoice_00d6d0cf`'s Returns text carries the ordering word "later" | — |
| OBS-D4 | observation | policy 1's declared `subject` (`cafe_service_model_changed`) is not the `event_type` its tool writes (`cafe_management_fee_invoiced`) | — |
| OBS-D5 | observation | the 7→4 edge's `effect` claims the deposit returned moves; on task 1's world it does not | 1 |
| OBS-D6 | observation | two base rules state a cross-problem order (standby replaces the management fee for a paused period) that grounds no declared edge | — |
| OBS-D7 | observation | base's admin-fee-on-food-cost sentence is inherited but no extended policy or tool invoices food cost | — |
| OBS-D8 | observation | `cafe_agg_portfolio_fee_band`'s first sentence is not named in `overwrite`, though the replacement text says "in place of any portfolio band discount" | — |
| OBS-D9 | observation | base's downgrade-cooldown sentence ("only accepted once the cooldown has passed") is inherited while policy 1 charges a repeat fee instead of refusing; neither seeded world has a downgrade | — |
| OBS-D10 | observation | base's entry-gate decline sentence cannot be evaluated: `cafe_contracts` carries no annual food spend, dedicated-kitchen or loading-access field | — |
| OBS-D11 | observation | policy 5's second `overwrite` replaces the "closure on or after term end" sentence with the notice-relief ladder, leaving that case ungoverned | — |
| OBS-D12 | observation | policy 2's `baseline.rule` states both that no allowance/relief/surcharge is taken and that they are subtracted and added | — |
| OBS-D13 | observation | two ladders split on "was a management fee invoice raised recently", a thin business condition for the quantity they decide | — |
| OBS-D14 | observation | policy 6's fall-through charges a full month of standby for a pause base says is not a suspension | — |
| OBS-D15 | observation | `credited_meal_period_basis` lists `approved_claim_days` in its `bindings` while its ladder turns on `net_claim_days`, which no factor binds | — |
| OBS-D16 | observation | policy 7's `smallwares_credit_band` states its tier values as amounts ("half the smallwares allowance") while it `decides` a percentage | — |
| OBS-D17 | observation | policy 4's `notice_days_standing` is computed and bound into `grace_days_band` but never read by any later binding; the tier is taken from `F('termination_notice_date') != ''` directly | — |

---

## closing_checklist

Written after both tasks' `source_gt_comparison` sections were on disk. **The difficulty is not closed
out: it does not pass the source-layer audit.**

| item | result |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | ✔ `0.md`, `1.md`, `_difficulty.md` |
| old revisions traceable | ✔ first revision; nothing to preserve |
| every comparison section carries a PASS | ✘ `0.md` = SOURCE-CHAIN + SOURCE-TASK + SOURCE-POLICY + SOURCE-FACTOR RED; `1.md` = SOURCE-POLICY + SOURCE-FACTOR + SOURCE-TASK RED |
| this difficulty's extended policies fully covered by the M tasks | ✔ 3 + 4 = all 7 |
| the M tasks' scopes pairwise disjoint (whole tree, root and prerequisites) | ✔ disjoint, confirmed against both `charter_scope` blocks after the reveal |
| task tools and GT closed | ✔ each task's `charter_scope.task_tools` is exactly the set its writes call |
| each task tool an independently generated, frozen uuid8 | ✔ see § `action_binding_and_uuids` |
| every tree has 1–3 prerequisite problems | ✔ task 0 has 2, task 1 has 3 |
| at least max(n−1,1) `value_input` edges | ✔ 2 of 2 and 3 of 3 |
| at least one problem resolved by an `owner=user` tool | ✔ `confirm_service_model_change_fa28a84a` (task 0), `settle_contract_balance_f9be2425` (task 1, the root) |
| no cycle, and the difficulty-wide `prerequisite` graph still a DAG | ✔ two disjoint chains, no cross-task edge |
| **the prerequisites are genuinely unmet at the opening** | ✘ task 0's only root edge is satisfied at `frozen_time` (finding 1 of `0.md`); two of task 1's three `condition`s are satisfied under their literal reading |
| every computation declares 4–6 factors, ≥2 `parameter`, ≥1 `method` | ✔ 4/6/5 and 4/4/5/6 |
| per task ≥1 multi-source and ≥1 cross-difficulty factor | ✔ task 0: pantry; task 1: market, twice |
| every ladder ≥3 tiers, stated in full in its rule, tiers distinct in outcome | ✔ all 34 factors |
| every tier's condition and outcome one that line of business actually holds | ✘ F-D6 / OBS-D13 / OBS-D14 |
| every factor bears weight on its task's world | ✔ all 34, verified by substitution and matching GT figure for figure |
| **against an honest baseline** | ✘ F-D8 (`contract_year_anchor`), F-D7 (`pause_month_count_basis`) |
| the baseline alone gives a definite number different from gold | ✔ 1650.00 / 11000.20 / 689.50 / 0.00 / 69600.00 / 13920.00 / 47026.00 — all definite, all ≠ gold (see OBS-2 in `1.md` on the 0.00) |
| cross-difficulty rows seeded and consistent with the other product's charter | ✘ F-D9: task 0's `pantry_ledger` contradicts `pantry.yaml` |
| instantiation-stage gates re-run on the final form | not run: the artifacts are unchanged since the brief's snapshot, and this audit edits nothing. The six commands in the brief remain the gates of record. |

**Per-task verdicts.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | **FAIL** (F-D2, F-D4, F-D5) | **FAIL** | **FAIL** (F-D9) | **FAIL** | SOURCE-CHAIN RED + SOURCE-TASK RED + SOURCE-POLICY RED + SOURCE-FACTOR RED |
| 1 | **FAIL** (F-D1) | PASS | **FAIL** (F-D8) | **FAIL** | SOURCE-POLICY RED + SOURCE-FACTOR RED + SOURCE-TASK RED |

Both blind derivations reproduced every gold figure exactly — three expected values, three whole
baselines and fifteen per-factor baselines on task 0; four expected values, four whole baselines and
nineteen per-factor baselines on task 1, all matching GT to the cent. No finding above is an
arithmetic disagreement with the instantiating agent, and none is attributed to a solving agent. The
failures are failures of what the artifacts assert: a prerequisite that is already satisfied, two
quantities the rule and the compute do not agree on, an undeclared override, an ambiguous reference to
"the service model in force", a baseline that is not the baseline the rule states, and a seeded
cross-difficulty ledger that contradicts its own product charter.

No artifact was edited by this audit, and no fix was designed or arranged.

---

# revision_2

Round-1 text above is left untouched. This round is a verification pass, not a blind one: GT for this
difficulty was revealed in round 1, so nothing below claims to be an independent derivation. Its job is
to check, item by item, that each round-1 RED is genuinely closed, that the rework introduced no new
defect, and that nothing that passed has regressed.

## charter_global_frozen (revision_2)

- re-audit time: 2026-09-22. Auditor unchanged.
- **Carry-forward rule applied and failed, so the charter-global section is re-derived in full:**

| source | round 1 | round 2 | |
| --- | --- | --- | --- |
| `cafe.extended.yaml` | c4b3d620…fc18da | **19edae03e7b9f02d72c82681bddb2c56719c3f5ccfde67680c4511e6cffd4aa9** | changed |
| `task_tools.py` | 0c5daaa7…f04e34 | **3aa99ca0b0c6166e10b8d51bd9eff67d18f9666b6be6cb4992fab122fa30c2bb** | changed |
| `0.masked.json` | ef69ede6…e858f8 | **20d2cb1eb31cacd16d69663399f0cd3028899069709aa56e0e61593b7be4a25a** | changed |
| `1.masked.json` | b22fbfdf…6a4b67f | **b22fbfdfdf1844eb4a124db75781a232d206c83d25aff1a6ba26cfa815b4a67f** | unchanged |

  All four recomputed on disk and identical to the coordinator's brief.
- `blueprint/products/cafe.yaml` and `pantry.yaml` hashes recorded; `diff` of the extended file's first
  799 lines against the blueprint product is **empty**, so the base copy is still verbatim identical and
  base was not touched.
- entry conditions: the brief supplies all seven gate commands with their output lines on the reworked
  form, all green. Cited, not re-run.
- contamination: this round is openly post-reveal (see the heading). No new leak path was opened; no
  search whose path scope included `tasks/*.json` was run before the verification computations were
  complete.

## round_1_findings_disposition

Each round-1 id, the route the reworker claimed, and what verification found. "Verified" means checked
against the artifact or recomputed on the world, never accepted from the brief.

### Closed and verified

| id | route claimed | what verification found |
| --- | --- | --- |
| **F-D1** (item 3) | at source | `baseline.rule` of `cafe_ext_closing_settlement_payment` now reads "…the smallwares allowance credited back is the smallwares allowance printed against the service model taken at the smallwares share **and then reduced to the proportion that the whole months of the contract year still to run bear to twelve**, rounded to the nearest cent; the whole months still to run are twelve less the contract year elapsed." The `/ 12` and the definition of "months still to run" are now both stated. Rule and `compute` agree. **CLOSED** |
| **F-D2** (item 7) | at the world and in the rule | Rule now reads "…the base fee is the mean of … and the management fee most recently invoiced on the contract, **rounded to the nearest cent**", so `RND` is licensed. Seed moved 4680.53 → **4680.52**, so the mean is (9850.00 + 4680.52)/2 = **7265.26** exactly, with no tie. Independently swept **every `RND` call site of all seven computations on both worlds**, instrumenting `RND` to flag any argument landing on an exact half-cent or where half-up and the runtime's rounding disagree: **0 sites**. The reworker's sweep claim is verified, not accepted. **CLOSED** |
| **F-D3** (items 1, 2) | rewritten prerequisite sentence | All five edge `condition`s now pin the required row by calendar month. See `problem_tree_recheck` below. **CLOSED** |
| **F-D4** (item 6) | at source | `cafe_ext_model_change_confirmation.rule` now carries "Every parameter this charge is worked out from is the one printed against **the service model the contract is moving from, that is the service model recorded on the contract immediately before the change is put into force, and no parameter of the service model being moved to enters it.**", and every tier sentence repeats "the service model the contract is moving from". The `overwrite`'s `replaced_by` was changed to match, so it no longer points at "the model being moved to". The second reading (20,994.73) is gone. **CLOSED** |
| **F-D5** (item 5) | newly declared `overwrite` | `cafe_ext_service_credit_settlement.overwrite` now has **six** entries; the two base sentences I named in round 1 — "A service credit is allowed only when the claim reaches Larkspur Table no later than the claim window…" and "Claim window days are counted as calendar days from the day after the invoice posting day…" — are each named verbatim as a `superseded_clause`. The undeclared override is gone. **CLOSED**, with a residual observation (OBS-R2, below) on what the declaration retired |
| **F-D6, F-D7** (item 9) | at source | `pause_month_count_basis` tier 2 now reads "the suspended days counted do not exceed the shortest suspension printed against the service model → **the pause is handled as ordinary closed days and no month of pause is charged**", which now *agrees* with inherited base "a pause shorter than the minimum suspension … is handled as ordinary closed days rather than as a suspension" — so no overwrite is needed and none is claimed. The **fall-through is now tier 3**, "divided by thirty and rounded down to a whole month with a minimum of one" = `MX(1, int(suspended_days_counted / 30))` = the declared `baseline` = the `baseline.rule` sentence. The three outcomes (ceiling / nil / floor-with-minimum) are distinct and the conditions partition. **BOTH CLOSED** |
| **F-D8** (item 4) | at source | `baseline.rule` now reads "The contract year elapsed is the whole months between the first day of the contract term and the day the settlement is worked out, **reduced by whole years**" — matching the declared `baseline` `term_months % 12`. The old unreduced tier is replaced by a new tier 2, "no first service day is recorded on the contract → no month of the contract year has elapsed", and the fall-through (tier 3) is now the reduced term-month figure, i.e. the baseline itself. Scrutiny the brief asked for: the three outcomes are `service_months % 12` / `0` / `term_months % 12`, distinct as stated; the conditions partition (first service day > 60 days out / no first service day / first service day within 60 days); and the **new tier is reachable on a world that can occur** — `initial_state.cafe_contracts.ff6e40bb…` in task 0 is a proposed contract with `service_commenced_date` = "". **CLOSED** |
| **F-D9** (item 8) | re-seeded to the charter figure | `pantry_ledger` `program_fee` rows are now **4180.00**, exactly `pantry.yaml`'s `program_fee_monthly_usd` for "Full Hospitality Pantry Program"; `pantry_agreements.receivable_balance_usd` moved 1790.00 → 4180.00 with them. `pantry_colocation_threshold_usd` moved 18000.00 → **45000.00**, so twelve months at 4180.00 = **50,160.00** still clears it and the tier is still `major` — and the threshold now sits inside the range the variant can produce rather than far below it. The dependent baseline figure is unchanged (see `no_scored_value_moved`). **CLOSED** |
| **OBS-D2** | at source | `cafe_ext_early_exit_charge`'s rule and the `exit_fee_base_band` ladder now say "the highest management fee **ever invoiced on the contract**", which is what `MAX('cafe_ledger','amount_usd', charge_code='management_fee')` and `inputs.history` `within_months: null` implement. The two faces agree. **CLOSED** |
| **OBS-D3** | at source | No ordering word remains in any docstring: `grep` for later/before/after/first over `task_tools.py` returns only "afterwards", which describes the post-state of the same call. **CLOSED** |
| **OBS-D5 / 1-F4** | at source | The 7→4 edge's `effect` no longer claims the deposit returned moves; it now reads "…the unsettled balance binding reads it, and the contractual charges counted in the three month window rise by one." **CLOSED** |
| **OBS-D8** | newly declared `overwrite` | `cafe_agg_portfolio_fee_band`'s first sentence ("The management fee a client pays on each cafe contract is discounted by a portfolio band…") is now named as its own `superseded_clause`. **CLOSED** |
| **OBS-D11** | at source | `cafe_ext_early_exit_charge.overwrite` now has a single entry; the mismatched one (replacing the "closure on or after term end" sentence with the notice-relief ladder) is gone, so that base sentence is inherited intact. **CLOSED** |
| **OBS-D12** | at source | Policy 2's `baseline.rule` now reads "The co-location allowance is nil, the suspended day relief is nil and the subsidy commitment surcharge is nil." followed by the arithmetic sentence — no longer self-contradictory. **CLOSED** |
| **OBS-D15** | at source | `credited_meal_period_basis.bindings` is now `[approved_claim_days, net_claim_days, credited_periods]`; the binding its ladder turns on is bound. **CLOSED** |
| **OBS-D16** | at source | `smallwares_credit_band`'s tier values now read "the smallwares share is one half / the whole / nil" — shares, matching `decides: smallwares_share_pct`. **CLOSED** |
| **OBS-D17** | at source | `notice_days_standing` is now genuinely read: `grace_days_allowed` branches on `notice_days_standing >= 0`, and the binding is defined `DAYS(F('termination_notice_date'), NOW) if F('termination_notice_date') != '' else **-1**`. The `-1` sentinel also silently fixes the round-1 edge case I noted for policy 6, where a notice given on the day of the call gave `DAYS = 0` and fell through as if no notice stood; `>= 0` now admits it and only the sentinel excludes it. Verified across all four sites that use the sentinel. **CLOSED, and an improvement beyond the item** |
| **OBS-D9** | listed as declined | Verified as effectively **closed**, not declined: `cafe_ext_model_change_confirmation.rule` now carries "The charge worked out under this rule **prices** a change of service model that the contract is permitted to make, and **decides nothing about whether a change is accepted**." That separates the extended pricing rule from base's inherited downgrade-cooldown acceptance rule, so the two no longer speak to the same question. |
| **OBS-D13** (half) | at source | `unrun_term_exit_months` tier 2 no longer splits on "no management fee invoice over those three months"; it now splits on "the cafe has been serving for twenty-four whole months or more" (`settled_site_exit_months`), which is a tenure a contract caterer does weigh when setting an exit term. **CLOSED for this factor.** The other half of OBS-D13 was also reworked, and the rework broke something else — see `new_defects`. |
| **OBS-D1 / 1-F5** | at source | Every policy now states which billing period its write is recorded against: "The charge is recorded against the billing period in which the client confirms the change." (1), "The management fee is recorded against the billing period it covers." (2), "The credit … is quoted against the billing period that invoice covers" (3), "The late charge is recorded against the billing period in which it is raised." (4), the same for 5 and 6, and "The settlement is recorded against the billing period in which it is paid." (7). The `service_period` argument is now policy-derived on all seven writes. **CLOSED** |

### Declines judged on their merits

| id | decline | verdict |
| --- | --- | --- |
| **OBS-2** | a whole-baseline of 0.00 on the late charge is a definite figure | **Accepted.** The standard asks for a definite number different from gold; 0.00 is definite, is different from 678.08, and leads a baseline reader to a determinate (wrong) conclusion — "no late charge is due" — rather than to no conclusion. |
| **OBS-3** | `standby_fee_base_band`'s tiers are distinct as stated | **Accepted.** "The management fee most recently invoiced" and "the mean of the management fees invoiced over those three months" are different rules; that they coincide at 18,096.00 on task 1 is an accident of the only two invoices in the window being equal, and the test the standard states is distinctness as stated. |
| **OBS-D1** | `cafe_participation_guarantee` governs a different charge | **Accepted.** It is still in the `base_policy_refs` of policies 4, 5 and 6 with no `overwrite`, but it computes a participation shortfall charge that no extended policy claims and no seeded world measures. No consequence is demonstrable. |
| **OBS-D4** | the tool's contract update *is* the declared event | **Accepted, and verified at source.** `blueprint/products/cafe.yaml` defines `cafe_service_model_changed` with `target: cafe_contracts`, `mutation: update` — which is exactly what `confirm_service_model_change_fa28a84a`'s `ctx.update` does. The `cafe_ledger` row it also writes is the administration fee and is correctly typed `cafe_management_fee_invoiced`. My round-1 observation was mistaken about which write carries the subject event. |
| **OBS-D10** | no such field exists and base is frozen | **Accepted.** `db_schema.json`'s `cafe_contracts` carries `headcount_served` and no column for annual food spend, dedicated kitchen or loading access, and the entry-gate sentence lives in a base policy this difficulty may not edit. The base sentence remains only partly decidable from the records; that is a scenario-level limitation, not a defect this difficulty can carry. |
| **0-F8** (partial) | the base sentence is now named in an `overwrite` | **Accepted.** `cafe_combination_pantry_interaction`'s site-scoped sentence is named as a `superseded_clause` and replaced by the client-scoped co-location ladder, which is the legal route for a deviation; and on task 0's world the pantry sits at CS-104, the same site as the cafe contract, so the site-blind reading changes nothing. |

## no_scored_value_moved (verified, not accepted)

Recomputed every figure from the reworked charter against the reworked worlds:

| | round 2 | round 1 | |
| --- | --- | --- | --- |
| 7 expected values | 8066.07 / 5035.71 / 1511.64 / 678.08 / 55283.28 / 26058.24 / 150431.90 | identical | **all SAME** |
| 7 whole baselines | 1650.0 / 11000.2 / 689.5 / 0.0 / 69600.0 / 13920.0 / 47026.0 | identical | **all SAME** |
| 34 per-factor baselines | see the per-task files | identical | **all SAME, 0 moved** |
| task 1's three edge-skip figures | 149753.82 / 95148.62 / 124373.66 | identical | **all SAME** |

No factor went dead: every one of the 34 baseline substitutions still moves its computation's result away
from gold. The claim is verified in full, including on task 0 whose world moved.

**Identifier bands held** (checked because item 8 moved the seed): phones `2015480137` / `2015097642`
(`2015…`); employee badge empty on both, correctly — both callers are client organisations, not diners;
`CA-11384` / `CA-11507` (`CA-11`+3); `CS-104`, `CS-118`, `CS-136` (`CS-1`+2); names Ashford/Delacroix and
Baird/Ellerbeck, all within A–E.

## problem_tree_recheck

All five edges now pin the required row by the calendar month of the write, so the clock fixes the period
rather than the claims or the invoices:

| edge | condition now | rows satisfying it at `frozen_time` |
| --- | --- | --- |
| 3→2 | "…management fee whose `service_period` is **the calendar month in which the credit is worked out**…" | `frozen_time` 2026-02-17 → 2026-02. Management-fee `service_period`s on the ledger: 2025-03, -04, -05, -06, -07, -08, -09, -12, 2026-01. **Zero.** |
| 2→1 | variant equals the approved request's `requested_variant_name` | "Limited Service Cafe" ≠ "Full Service Cafe". **Unmet.** |
| 7→4 | "…`late_fee` whose `service_period` is **the calendar month in which the settlement is worked out**…" | 2026-03; the two `late_fee` rows carry 2025-05 and 2025-10. **Zero.** |
| 7→5 | same shape, `early_termination_fee` | no such row for any period. **Zero.** |
| 7→6 | same shape, `standby_fee` | 2026-03; the two `standby_fee` rows carry 2025-06 and 2025-07. **Zero.** |

Round 1's fatal finding is closed at its root: the period is no longer "the billing period the claim
concerns", which the records did not fix, but the month of the write, which `frozen_time` fixes outright.
Tree shape is intact — task 0 keeps 2 prerequisite problems and 2 `value_input` edges (floor
max(2−1,1) = 1); task 1 keeps 3 and 3 (floor 2); both keep an `owner=user` write; the graph is still two
acyclic chains. Every `why_false` now argues the condition it is attached to and names the rows that do
stand, so round-1 finding 0-F7 is closed as well.

## new_defects

**F-R1 — SOURCE-FACTOR RED — `short_notice_charge_basis` is no longer a `method`, and policy 1 is left
with none. (New this round; a regression of something that passed in round 1.)**

- *Symptom*: `cafe_ext_model_change_confirmation` declares 3 `parameter` factors and 1 `method`, but
  the `method` no longer varies a method.
- *Root cause*: the rework fixed OBS-D13's thin condition on this ladder — the split is now on the site's
  reported headcount rather than on whether an invoice was raised recently, which is an improvement —
  but in rewriting the tiers it also changed tier 2's outcome from **per day** to **per whole week**.
  The two live tiers are now "one fifteenth of the change administration fee … for each whole week of the
  shortfall" and "one thirtieth of the change administration fee … for each whole week of the shortfall".
- *Evidence*: `cafe.extended.yaml` → `cafe_ext_model_change_confirmation.factors[2].ladder`, and the
  compute binding `short_notice_charge_usd`:
  `RND(change_admin_fee_usd / 15, 2) * int(notice_shortfall_days / 7)` versus
  `RND(change_admin_fee_usd / 30, 2) * int(notice_shortfall_days / 7)`. Round 1's tier 2 was
  `RND(change_admin_fee_usd / 30, 2) * notice_shortfall_days` — a genuine day-count, which is what made
  the label honest then.
- *Demonstrated consequence*: the formula is `fee / D × weeks` with `D ∈ {15, 30}`. Only the divisor
  differs; the algorithm, the unit of accrual and the rounding point are identical. That is a rate
  substituted into one formula, which is the standard's own definition of a mislabelled `method`. A
  zeroing fall-through does not rescue the label, because this charter uses zeroing fall-throughs in
  `parameter` ladders too (`opening_project_settlement_band`: "nothing is settled";
  `client_closure_set_aside`: "no claim day is set aside"). Counting only factors that survive the label
  test, `cafe_ext_model_change_confirmation` declares **0 `method` factors**, below the floor of 1 per
  computation. Note the factor still *bears weight* — its baseline gives 7,363.75 against gold 8,066.07 —
  so this is a labelling defect, not a dead factor, and no scored value moves.
- *Affected artifact*: `cafe.extended.yaml` → `cafe_ext_model_change_confirmation.factors[2]`, its three
  `rule` tier sentences and the `short_notice_charge_usd` compute binding. Bears on **task 0**.

**OBS-R1 — observation, and a correction of my own round-1 ruling — `notice_relief_basis` has the same
shape and did not change this round.** `cafe_ext_early_exit_charge.factors[2]` selects "reduced by one
fiftieth of itself for each whole week" against "reduced by one hundredth of itself for each whole week":
`charge / D × weeks`, `D ∈ {50, 100}`. By the same test that condemns F-R1 this is a rate, not a method,
and `cafe_ext_early_exit_charge` would likewise be left with 0 `method` factors. **I passed this factor in
round 1 under the scaling family and I was too lenient; the artifact is byte-identical, so this is my
error and not a reworker regression, and the reworker was never told about it.** It is recorded here as
an observation rather than re-graded as a RED so that a round-1 ruling is not rewritten after the fact —
but it should be settled alongside F-R1, because a standard applied to one and not the other is no
standard.

**OBS-R2 — observation — both tasks now declare `solvability_contract.temporal_feasibility: []`.** The
brief flagged this route for scrutiny, so it was checked rather than assumed. Declaring the override of
base's claim-window sentences legitimately retired the `claim_window` eligibility on task 0's credit
write, which now carries `base_preconditions: [(cafe_service_credit_terms, policy_scope)]` alone. Two
things make this acceptable rather than a weakening:

- The write's timing is still bound to `frozen_time`, and demonstrably so. Re-running the credit
  computation with the clock moved and everything else held: **2026-01-17 → 1,970.00**,
  **2026-02-17 → 1,511.64**, **2026-02-19 → 1,511.64**, **2026-03-17 → 1,970.00**. The scored figure is
  a function of the clock through four NOW-anchored windows, and through the new prerequisite condition,
  which is a *tighter* clock binding than the one that was retired.
- The retired gate never decided act-now/wait/refuse on this write; it decided *which claims count*,
  which is a value question, and it decided it in contradiction with the extended ladder — that was
  round-1 finding F-D5.

The residual is genuine but small and is not a red light: **no write of either task now carries a
declared time boundary**, so a later change to any window has no declared time gate to be checked
against. Task 1's `temporal_feasibility` was `[]` in round 1 as well, so only task 0's is new.

## closing_checklist (revision_2)

| item | round 1 | round 2 |
| --- | --- | --- |
| base copy verbatim; blueprint untouched | ✔ | ✔ re-diffed, empty |
| every comparison section carries a PASS | ✘ both tasks RED | ✘ both tasks carry one SOURCE-FACTOR RED (F-R1 on task 0; OBS-R1 raised but not re-graded on task 1) |
| policies fully covered, scopes pairwise disjoint | ✔ | ✔ unchanged, 3 + 4 = 7 |
| uuid8s independently generated and frozen | ✔ | ✔ all seven unchanged across the rework |
| tools judge no prerequisite | ✔ | ✔ re-read; no `if`, no raise, no status check in any of the seven bodies |
| trees: 1–3 prerequisite problems, `value_input` floor, `owner=user` write, acyclic | ✔ | ✔ unchanged |
| **prerequisites genuinely unmet at the opening** | ✘ | **✔ all five edges, zero satisfying rows** |
| 4–6 factors, ≥2 `parameter`, ≥1 `method` per computation | ✔ as declared | ✘ **as declared ✔, but 2 of 7 computations have 0 `method` that survives the label test** (F-R1, OBS-R1) |
| ladder ≥3 tiers, stated in the rule, tiers distinct in outcome | ✔ | ✔ including the two reworked ladders |
| conditions and outcomes ones the business holds | ✘ F-D6, OBS-D13, OBS-D14 | ✔ all three closed at source |
| every factor bears weight against an **honest** baseline | ✘ F-D7, F-D8 | ✔ all 34 bear weight; every fall-through now equals its declared baseline and its `baseline.rule` |
| baseline alone gives a definite number ≠ gold | ✔ | ✔ all seven unchanged |
| cross-difficulty rows seeded and consistent with the other product's charter | ✘ F-D9 | ✔ pantry reseeded to 4,180.00; market re-checked, still consistent |
| rule ↔ compute equivalence both ways | ✘ F-D1, F-D2, OBS-D2 | ✔ all three closed; a full `RND` sweep finds no remaining half-cent |
| gates re-run on the final form | n/a | cited from the brief, all green; not re-run by this auditor |

**Per-task verdicts, revision_2.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | **PASS** (F-D2, F-D4, F-D5 closed) | **PASS** (F-D3 closed) | **FAIL** — F-R1, a new mislabelled `method` | **PASS** | **SOURCE-FACTOR RED** (one item, new this round) |
| 1 | **PASS** (F-D1 closed) | **PASS** (already passing; 1-F3 closed) | **PASS** as graded, with OBS-R1 outstanding | **PASS** | **PASS, with OBS-R1 recorded** |

Nine of nine round-1 REDs are closed and verified at source or on the world; thirteen of thirteen
observations claimed closed are closed; six declines are accepted on their merits, one of them
(OBS-D4) because verification showed my round-1 observation was itself mistaken. One new defect was
introduced, F-R1, as a side effect of an otherwise correct fix, and one round-1 under-call of mine,
OBS-R1, is disclosed alongside it. No scored value moved anywhere: 7 expected values, 7 whole baselines,
34 per-factor baselines and 3 edge-skip figures all bit-identical, verified by recomputation.

No artifact was edited by this audit, and no fix was designed or arranged.

---

# revision_3

Revisions 1 and 2 are left untouched. Post-reveal verification pass, as revision 2 was.

## charter_global_frozen (revision_3)

| source | round 2 | round 3 | |
| --- | --- | --- | --- |
| `cafe.extended.yaml` | 19edae03…fd4aa9 | **fc361a8cb2a7bc447fb52a375b9afd1d57d457fc89e2c49eb2e5fba04389be12** | changed |
| `task_tools.py` | 3aa99ca0…30c2bb | **3aa99ca0b0c6166e10b8d51bd9eff67d18f9666b6be6cb4992fab122fa30c2bb** | unchanged |
| `0.masked.json` | 20d2cb1e…e4a25a | identical | unchanged |
| `1.masked.json` | b22fbfdf…6a4b67f | identical | unchanged |

All four recomputed on disk and identical to the brief. Neither world moved; the change is confined to
the charter. The extended file's first 799 lines still `diff` empty against
`blueprint/products/cafe.yaml`, so base is still frozen and verbatim. Because `task_tools.py` did not
move, the tool-contract and uuid conclusions of `revision_2` § `action_binding_and_uuids` are carried
forward by hash rather than re-derived; everything that reads `cafe.extended.yaml` is re-derived.

## round_2_item_disposition

### F-R1 — CLOSED

The round-2 defect was that `short_notice_charge_basis`'s two live tiers had collapsed to one formula at
two rates (`fee/15 × weeks` against `fee/30 × weeks`). The reworker claims it restored a procedural
distinction on the outcome side and did not relabel. Verified at source:

| | round 2 | round 3 |
| --- | --- | --- |
| tier 1 | "one fifteenth … is charged for each whole week of the shortfall" | "**the shortfall is counted in whole weeks** and one fifteenth … is charged for each of them, **a part week being left uncharged**" |
| tier 2 | "one thirtieth … is charged for each whole week of the shortfall" | "**the shortfall is counted in calendar days** and one hundred and fifth … is charged for each of them" |
| compute | `RND(fee/15,2)*int(d/7)` vs `RND(fee/30,2)*int(d/7)` | `RND(fee/15,2)*int(d/7)` vs `RND(fee/105,2)*d` |

`effect` is still `method` — the label was not changed, as claimed. The two tiers now differ in the unit
of accrual and in how a part unit is treated, not only in a constant. Both new tier sentences are
**verbatim** in the policy's own `rule` (checked by the sweep below, which flagged neither). The tiers
are also distinct in outcome on this world: 2,450.00 gives 163.33 × 4 = **653.32** under tier 1 and
23.33 × 30 = **699.90** under tier 2. The factor still bears weight (baseline 7,363.75 against gold
8,066.07) and the scored charge is unchanged. **CLOSED.**

### OBS-R1 — CLOSED

`notice_relief_basis` was changed in the same way and by the same standard, which is what I asked for
when I raised it:

| | round 2 | round 3 |
| --- | --- | --- |
| tier 1 | "reduced by one fiftieth of itself for each whole week of notice given beyond that termination notice" | "**the notice given beyond that termination notice is counted in whole weeks** and the exit charge before allowances is reduced by one fiftieth of itself for each of them, **a part week being left unrelieved**" |
| tier 2 | "reduced by one hundredth of itself for each whole week…" | "**counted in calendar days** and … reduced by **one three hundred and fiftieth** of itself for each of them" |

Both sentences verbatim in the rule. On task 1's world tier 1 gives 1,809.60 × 3 = **5,428.80** and
tier 2 would give 258.51 × 21 = 5,428.71, so the tiers are distinct in outcome there too. **CLOSED.**

### The standard itself, judged on its merits

The reworker states it as: *strip the numeric literals out of two tier sentences and ask whether the
remaining procedures are the same; if what remains is one formula at two rates, it is a `parameter`.*
That is sound and it is the skill's own test in operational form — "a factor labelled `method` whose
tiers only substitute a different number into the same formula (a rate, a fee, a threshold)" is exactly
"what remains after stripping the literals is the same procedure". I applied it to **all twelve**
`method` factors of the charter, not only the two under repair:

| factor | what remains after stripping the literals | survives |
| --- | --- | --- |
| short_notice_charge_basis | whole weeks, part discarded / calendar days | ✔ |
| escalation_step_anchor | anchored on the first service day / on the first day of the term | ✔ |
| suspended_day_relief_basis | per suspended calendar day / per whole week of them | ✔ |
| claim_window_basis | wide / medium / standard window | ✔ |
| credited_meal_period_basis | every meal period / every meal period less one in all, never below nil | ✔ |
| outstanding_amount_basis | less payments and credits / less payments only | ✔ |
| overdue_clock_anchor | from the last payment / from the last credit / from the last invoice | ✔ |
| notice_relief_basis | whole weeks, part discarded / calendar days | ✔ |
| suspended_day_count_basis | to the day service was asked back / to the day the charge is raised | ✔ |
| pause_month_count_basis | thirty-day blocks with a part month rounded up / no month charged / floor with a minimum of one | ✔ |
| contract_year_anchor | from the first service day, reduced by whole years / nil / from the term's first day, reduced by whole years | ✔ |
| drawable_funding_refund_basis | lots funded less drawn / the balance at the rollover percentage / the balance | ✔ |

**Twelve of twelve survive; none collapses to one formula at two rates.** The claim is verified, and the
standard is applied consistently — `suspended_day_relief_basis` is the mirror case that confirms it is
coherent rather than ad hoc: both its tiers use one thirtieth and it survives because the *unit* differs,
which is the same axis on which the two repaired factors were fixed.

### OBS-R2 — ACCEPTED, and the reason verified rather than taken

The reworker declines to restore a time boundary, on the ground that the only base time gate reaching a
write of this difficulty is the one the extended ladder supersedes, so reinstating it would reinstate
round-1 finding F-D5 verbatim. Checked mechanically against `blueprint/products/cafe.yaml` rather than
accepted: the base product declares exactly three `kind: time` eligibilities, and matching each one's
`applies_to` against the five subject events the extended policies claim —

| base time gate | applies_to | reaches a write here |
| --- | --- | --- |
| `cafe_mobilization_terms` / `mobilization_lead_time` | `cafe_service_commenced` | **no** |
| `cafe_termination_terms` / `notice_period` | `cafe_contract_closed` | **no** |
| `cafe_service_credit_terms` / `claim_window` | `cafe_service_credit_issued` | **yes** |

— the reason is exactly right: one gate reaches this difficulty, and it is the superseded one. Restoring
it would put back the two-live-rules-for-one-quantity conflict that was round 1's F-D5. The decline is
**accepted**; the observation stands as recorded in `revision_2`, unchanged and still not a red light.

## no_scored_value_moved (verified)

Recomputed from the round-3 charter on the unchanged worlds:

| | round 3 | round 2 | |
| --- | --- | --- | --- |
| 7 expected values | 8066.07 / 5035.71 / 1511.64 / 678.08 / 55283.28 / 26058.24 / 150431.90 | identical | **all SAME** |
| 7 whole baselines | 1650.0 / 11000.2 / 689.5 / 0.0 / 69600.0 / 13920.0 / 47026.0 | identical | **all SAME** |
| 34 per-factor baselines | — | identical | **all SAME, 0 moved** |
| task 1's 3 edge-skip figures | 149753.82 / 95148.62 / 124373.66 | identical | **all SAME** |
| `RND` half-cent sweep, all 7 computations, both worlds | **0 sites** | 0 | SAME |

All five prerequisite edges are unchanged in shape and wording, and still unmet: zero `management_fee`
rows carry `service_period` 2026-02 on task 0, and zero `late_fee`, `early_termination_fee` or
`standby_fee` rows carry `service_period` 2026-03 on task 1.

## paraphrase_sweep (re-run independently and more strictly)

The reworker reports finding a third instance of a ladder face worded differently from its rule, fixing
it, and both sweeps clean afterwards. Rather than accept the clean result I ran my own sweep over
**every ladder face of every factor** — 170 faces across 34 factors — testing each `when`, `value` and
`method` for **verbatim containment** in its policy's own normalised `rule`, and adjudicating every miss
by hand.

- **147 of 170 are verbatim.**
- **21 of the 23 misses are grammatical recasting that a ladder face necessarily performs** and carry no
  drift of meaning: the rule writes "where X, then Y" and the ladder splits it into `when: X` /
  `value: Y`, which drops a leading "where", turns "a contract whose record shows…" into "the contract's
  record shows…", or resolves an anaphor the face cannot carry on its own ("that threshold" →
  "the pantry co-location threshold"; "such claims" → "service credit claims … on the contract";
  "the two" → the two fees named). Each was read against its rule sentence and states the same condition
  or outcome. Not defects.
- **2 are genuine instances of the family the reworker was sweeping for, and remain open.** See OBS-R4.

Reverse direction re-checked as well: every branch of every `decides` binding is a tier its rule states.

## new_defects

**F-R2 — SOURCE-POLICY RED — `short_notice_charge_usd` rounds an intermediate the rule places at the
end, and on task 0 that gives two answers. Pre-existing since round 1; missed by me in rounds 1 and 2
and raised now because it is demonstrable.**

- *Symptom*: the scored change administration charge can be derived as **8,066.07** or **8,066.08** from
  the same policy.
- *Root cause*: `cafe_ext_model_change_confirmation.compute` evaluates
  `RND(change_admin_fee_usd / 15, 2) * int(notice_shortfall_days / 7)` — it rounds the per-week amount
  and then multiplies. The policy's own rule says the opposite in terms: "The change administration fee
  the contract carries, the opening project settlement and the short notice charge are added together
  first, and the loading is then applied once to that total; **the figure is rounded to the nearest cent
  at the end.**" No sentence of the `rule`, of `baseline.rule` or of
  `compute_basis.short_notice_charge_usd` states any rounding of the per-week amount, and the one
  rounding sentence the policy carries places rounding *at the end*.
- *Evidence*: `cafe.extended.yaml` → `cafe_ext_model_change_confirmation`, `compute` binding
  `short_notice_charge_usd`, and the rule's final rounding sentence. Contrast
  `cafe_ext_service_credit_settlement`, which licenses both of its roundings explicitly — "The credit
  for one meal period is the fee base taken at the credit rate **and rounded to the nearest cent**, the
  credit worked out is that figure multiplied by the credited meal periods **and rounded to the nearest
  cent**" — so the charter plainly knows how to state a per-unit rounding when it intends one.
- *Demonstrated consequence* on task 0's world: one fifteenth of 2,450.00 is 163.333…; four whole weeks
  of shortfall stand.
  - compute: 163.33 × 4 = 653.32 → subtotal 7,503.32 → × 1.075 → **8,066.07** (gold).
  - the rule read literally, rounding only at the end: 2,450.00 ÷ 15 × 4 = 653.333… → subtotal
    7,503.333… → × 1.075 = 8,066.0833… → **8,066.08**.
  A solver who follows the rule's explicit "at the end" instruction is marked wrong by one cent on a
  scored parameter. This is the same family as round-1 finding F-D2, which was graded RED, so grading it
  otherwise would be applying two standards.
- *Affected artifact*: `cafe.extended.yaml` → `cafe_ext_model_change_confirmation.compute`
  `short_notice_charge_usd`; `tasks/0.json` → the scored `change_admin_fee_usd`. **Bears on task 0.**
- *Relation to previous revisions*: the expression is byte-identical to round 1. **This is my
  under-call, not a reworker regression** — I checked the half-cent question in round 2 and did not
  check the rounding *point* against the rule's placement sentence. Disclosed here for the same reason
  OBS-R1 was disclosed in revision 2.

**OBS-R3 — observation — the round-3 move of `notice_relief_usd`'s rounding point introduced the same
shape into policy 5, latent.** The brief asked whether "same on this world" is the same as "same". It is
not, and the direction is worth recording:

| | expression | rounding |
| --- | --- | --- |
| rounds 1–2 | `RND(exit_charge_before_allowances_usd / 50 * int(…/7), 2)` | once, at the end |
| round 3 | `RND(exit_charge_before_allowances_usd / 50, 2) * int(…/7)` | per week, then multiplied |

On task 1 the two agree because 90,480.00 ÷ 50 = 1,809.60 is already exact to the cent, which is why no
scored value moved. They diverge on any world where the per-week amount is not exact: at an exit charge
of 1,000.55 over 7 weeks, rounding first gives 140.07 and rounding at the end gives 140.08. The move was
made so that "the compute says what the prose says", and the prose — "reduced by one fiftieth of itself
**for each of them**" — does read as a per-unit amount taken a number of times, so the intent is
reasonable. But policy 5's only rounding sentence is on the result ("the result is rounded to the
nearest cent and is never less than nil"), so the per-week rounding is no better licensed here than in
policy 1, and the move traded a form the rule did state for one it does not. Recorded as an observation
rather than a red light because no consequence is demonstrable on either seeded world — but it and F-R2
are one question and should be settled together, in whichever direction.

A mechanical sweep for this shape across all seven policies finds **exactly these two sites** and no
others: `short_notice_charge_usd` and `notice_relief_usd`. Every other `RND` in the charter rounds once,
at a point its rule names.

**OBS-R4 — observation — two ladder fall-through faces are still worded differently from their rule.**
My stricter sweep leaves two genuine instances of the family the reworker was hunting:

| factor | ladder face | what the rule says | phrase in the rule? |
| --- | --- | --- | --- |
| `late_resumption_loading_band` T2 | "the nil late resumption loading" | "no late resumption loading is added to the charge" | **no** |
| `outlet_carry_over_band` T2 | "the nil carry-over share" | "none of that funding is carried over to another outlet" | **no** |

The charter's own convention elsewhere is for the fall-through face to name the nil constant *and* for
the rule to use that name: `pantry_colocation_allowance` T2 says "the nil co-location rate" and the rule
says "the co-location allowance is the nil co-location rate of the escalated fee";
`subsidy_commitment_surcharge` T2 and `smallwares_credit_band` T2 likewise. These two ladders depart from
it. Both faces mean the same thing as their rule sentence and both select 0.0, so no second answer and
no missing answer follows, which is why this is an observation and not a red light — but the ladder is
what the KB renders, so the reworker's "both sweeps clean afterwards" is **not fully borne out**: two
faces of this family remain, in factors nobody raised.

## closing_checklist (revision_3)

| item | round 2 | round 3 |
| --- | --- | --- |
| base frozen, base copy verbatim | ✔ | ✔ re-diffed empty; the coordinator's `check_base_frozen` also reports 10 files verified |
| prerequisites genuinely unmet at the opening | ✔ | ✔ all five edges unchanged, zero satisfying rows |
| every factor bears weight against an honest baseline | ✔ | ✔ all 34, none dead, every fall-through still equals its declared baseline |
| ≥1 honest `method` per computation | ✘ 2 of 7 computations had none | **✔ all 7; twelve `method` factors checked against the stated standard, none collapses** |
| ladder faces stated in the rule | not swept exhaustively | ✘ **2 of 170 faces depart in wording** (OBS-R4); 147 verbatim, 21 benign recastings |
| rule ↔ compute equivalence both ways | ✔ | ✘ **2 unlicensed intermediate roundings** — F-R2 (demonstrable) and OBS-R3 (latent) |
| no scored value moved | ✔ | ✔ 7 + 7 + 34 + 3 figures bit-identical; `RND` sweep still 0 |
| gates re-run on the final form | cited | cited from the brief, all green including `check_base_frozen` |

**Per-task verdicts, revision_3.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | **FAIL** — F-R2 | **PASS** | **PASS** — F-R1 closed | **FAIL** — two answers, 8066.07 / 8066.08 | **SOURCE-POLICY RED** |
| 1 | **PASS** | **PASS** | **PASS** — OBS-R1 closed | **PASS** | **PASS**, with OBS-R3 and OBS-R4 recorded |

Both round-2 items are genuinely closed, by a standard that is sound and that I verified is applied to
all twelve `method` factors rather than only the two under repair; OBS-R2's decline is accepted with its
reason checked mechanically. One new latent defect was introduced (OBS-R3) as the side effect of an
otherwise well-intentioned change, two ladder faces of the swept family remain (OBS-R4), and one
pre-existing demonstrable defect that I missed in rounds 1 and 2 is now raised (F-R2).

No artifact was edited by this audit, and no fix was designed or arranged.

---

# revision_4

Revisions 1–3 are left untouched. Post-reveal verification pass.

## charter_global_frozen (revision_4)

| source | round 3 | round 4 | |
| --- | --- | --- | --- |
| `cafe.extended.yaml` | fc361a8c…89be12 | **be132c2e135c06a20fa6cef6beb110046453604d792efb89f695a900689a58fd** | changed |
| `task_tools.py` | 3aa99ca0…30c2bb | identical | unchanged since round 2 |
| `0.masked.json` | 20d2cb1e…e4a25a | identical | unchanged |
| `1.masked.json` | b22fbfdf…6a4b67f | identical | unchanged |

All four recomputed on disk and identical to the brief. Neither world moved. The extended file's first
799 lines still `diff` empty against `blueprint/products/cafe.yaml`. Because `task_tools.py` did not
move, the tool-contract and uuid conclusions of `revision_2` are carried forward by hash.

**"The compute is unchanged" — verified textually, not merely numerically.** The two bindings the
prose moved onto were compared string-for-string against the round-3 expressions recorded in
`revision_3`:

- `cafe_ext_model_change_confirmation` / `short_notice_charge_usd` — **identical**
- `cafe_ext_early_exit_charge` / `notice_relief_usd` — **identical**

So this round the prose moved onto the compute and the compute did not move at all, which is the
direction the brief flagged.

## round_3_item_disposition

### F-R2 — CLOSED

Round 3's defect: `compute` rounded the per-week amount while the policy's only rounding sentence said
the figure "is rounded to the nearest cent **at the end**", giving 8,066.08 against gold 8,066.07. Two
sentences changed, and both were needed:

| | round 3 | round 4 |
| --- | --- | --- |
| tier sentence | "one fifteenth of the change administration fee the contract carries is charged for each of them" | "one fifteenth of the change administration fee the contract carries, **rounded to the nearest cent**, is charged for each of them" |
| rounding sentence | "…the loading is then applied once to that total; the figure is rounded to the nearest cent **at the end**." | "…the loading is then applied once to that total; **the figure the loading leaves** is rounded to the nearest cent." |

The first licenses what `compute` does. The second removes the clause the rival reading rested on: the
rule no longer asserts that rounding happens only at the end, it names *which* figure the final rounding
applies to. `grep` over the whole charter finds "at the end" exactly once, in the frozen base copy
(`cafe_subsidy_funding_terms`, about a funding lot lapsing), and in no extended policy.

**Scrutiny point 2, checked directly.** The literal chain through the new prose, in exact decimal:
one fifteenth of 2,450.00 rounded to the nearest cent = **163.33**; charged for each of 4 whole weeks =
**653.32**; added to 2,450.00 and 4,400.00 = **7,503.32**; the loading applied once = 8,066.069; the
figure the loading leaves, rounded = **8,066.07** — the gold cent. And 8,066.08 is now
**unconstructible**: producing it requires the per-week amount to be carried unrounded, which the tier
sentence now forbids in terms. Both ladder faces carry the new wording as well as the rule, so the KB
will publish the licensed form.

### OBS-R3 — CLOSED

`cafe_ext_early_exit_charge`'s tier sentences were changed in the same direction on the same day:
"the exit charge before allowances is reduced **for each of them** by one fiftieth of itself **rounded
to the nearest cent**" (and "one three hundred and fiftieth of itself rounded to the nearest cent" on
tier 2). The word order moved so that the rounding attaches to the per-unit amount rather than to the
reduction, which is what `RND(exit_charge_before_allowances_usd / 50, 2) * weeks` does. The latent
divergence I recorded — that the round-3 move had traded a form the rule stated for one it did not — is
gone: the rule now states it.

### OBS-R4 — CLOSED

Both faces are closed by bringing the rule onto the named constant rather than by changing the face:

| factor | face | phrase now in `rule` | in `baseline.rule` |
| --- | --- | --- | --- |
| `late_resumption_loading_band` T2 | "the nil late resumption loading" | **yes** | **yes** |
| `outlet_carry_over_band` T2 | "the nil carry-over share" | **yes** | **yes** |

That is the charter's own convention elsewhere (`pantry_colocation_allowance`,
`subsidy_commitment_surcharge`, `smallwares_credit_band`), so the two departures are now in line rather
than newly invented.

### The instruments — confirmed, not assumed (scrutiny point 3)

I re-ran my own round-3 sweeps unchanged against the round-4 charter:

| sweep | round 3 | round 4 | reworker's report |
| --- | --- | --- | --- |
| ladder faces, verbatim containment | 170 checked, **23** misses | 170 checked, **21** misses | 23 → 21 ✔ agrees |
| unlicensed intermediate `RND` | 2 bindings | **0** | 4 sites / 2 bindings → 0 ✔ agrees |
| `RND` half-cent / rounding-disagreement | 0 | **0** | 0 ✔ agrees |

The reworker counts 204 faces where I count 170; the difference is exactly the 34 `when: otherwise`
faces, which both of us exempt, so the two instruments agree on both the population and the verdicts.

**The remaining 21 are the same 21, not a different 21.** Listed and compared set-wise against the
round-3 list: `change_administration_fee_band` T0/T1 when, `opening_project_settlement_band` T0 value
and T1 when, `short_notice_charge_basis` T0/T1 when, `account_exposure_loading_band` T1 when,
`transition_period_base_fee` T0 value and T1 when, `escalation_step_anchor` T1 when,
`settlement_record_escalation_rate` T0/T1 when, `pantry_colocation_allowance` T1 when,
`suspended_day_relief_basis` T1 when, `subsidy_commitment_surcharge` T1 when,
`disruption_credit_rate_band` T1 when, `client_closure_set_aside` T0/T1 value,
`credit_fee_base_basis` T1 when, `outstanding_amount_basis` T1 when,
`continuing_outlet_allowance` T1 when. That is my round-3 list minus exactly the two OBS-R4 items, and
every one of the 21 is a grammatical recasting I adjudicated benign in revision 3 — a dropped "where",
"a contract whose record shows" recast as "the contract's record shows", or an anaphor resolved because
a ladder face must stand alone. None is a drift of meaning, and none is new.

## The adopted convention, judged on its merits (scrutiny point 1)

The reworker states it as: *a per-unit price is struck to the nearest cent at the moment it is struck,
then taken the number of times the rule says; every other figure is rounded once at the point its own
rule names.*

**The rule itself is sound.** It is how a business actually publishes a per-unit price — a rate card
quotes a price to the cent and multiplies — and the charter has published exactly that shape since round
1 in `cafe_ext_service_credit_settlement`: "The credit for one meal period is the fee base taken at the
credit rate **and rounded to the nearest cent**, the credit worked out is that figure multiplied by the
credited meal periods **and rounded to the nearest cent**." So the convention is not invented to close a
finding; it is the charter's own oldest published shape, now stated at two more sites. I accept it.

**But it is not applied consistently, and that is a finding.** I tested it mechanically rather than by
inspection: for each of the seven policies I stripped every `RND` whose own `compute_basis` sentence
names no rounding — i.e. read the charter exactly as the convention says to read it — and recomputed on
the world of each write.

| policy | gold | under the convention | |
| --- | --- | --- | --- |
| model_change_confirmation | 8066.07 | **8066.07** | ✔ |
| management_fee_invoice | 5035.71 | **5035.70** | ✘ **diverges** |
| service_credit_settlement | 1511.64 | **1511.64** | ✔ |
| late_charge_assessment | 678.08 | **678.08** | ✔ |
| early_exit_charge | 55283.28 | **55283.28** | ✔ |
| standby_charge_assessment | 26058.24 | **26058.24** | ✔ |
| closing_settlement_payment | 150431.90 | **150431.90** | ✔ |

Six of seven reproduce gold under the charter's own convention. The seventh does not. See F-R3.

## no_scored_value_moved (verified)

| | round 4 | round 3 | |
| --- | --- | --- | --- |
| 7 expected values | 8066.07 / 5035.71 / 1511.64 / 678.08 / 55283.28 / 26058.24 / 150431.90 | identical | **all SAME** |
| 7 whole baselines | 1650.0 / 11000.2 / 689.5 / 0.0 / 69600.0 / 13920.0 / 47026.0 | identical | **all SAME** |
| 34 per-factor baselines | — | identical | **all SAME, 0 moved** |
| **5** edge-skip figures | task 0: 1970.0, 2963.1 · task 1: 149753.82 / 95148.62 / 124373.66 | identical | **all SAME** |
| `RND` half-cent sweep | 0 sites | 0 | SAME |

All five prerequisite edges re-verified unmet with zero satisfying rows: zero `management_fee` rows at
`service_period` 2026-02 on task 0, `variant_name` still "Limited Service Cafe" against an approved
request naming "Full Service Cafe", and zero `late_fee`, `early_termination_fee` and `standby_fee` rows
at 2026-03 on task 1.

## new_defects

**F-R3 — SOURCE-POLICY RED — `cafe_ext_management_fee_invoice` is the one policy the adopted convention
does not reach, and reading the charter as it now tells you to read it gives 5,035.70 against gold
5,035.71.**

- *Symptom*: the scored February management fee can be derived as **5,035.71** or **5,035.70** from the
  same charter, and a third reading gives **5,035.75**.
- *Root cause*: three of the policy's bindings are rounded by `compute` while their own rule sentences
  name no rounding, and the policy's single rounding sentence names a different figure —
  "the management fee invoiced is the escalated fee less those two reductions plus that surcharge,
  **rounded to the nearest cent** and never below nil". The three are
  `colocation_allowance_usd`, `suspended_day_relief_usd` and `subsidy_surcharge_usd`.
- *Evidence*, in exact decimal on task 0's world, escalated fee 7,707.71:

  | component | exact | as `compute` rounds it |
  | --- | --- | --- |
  | co-location allowance (6 %) | 462.4626 | 462.46 |
  | suspended day relief (11⁄30) | 2,826.160333… | 2,826.16 |
  | subsidy surcharge (8 %) | 616.6168 | 616.62 |

  - `compute`: 7,707.71 − 462.46 − 2,826.16 + 616.62 = **5,035.71** (gold).
  - the convention: none of the three sentences names a rounding, so each is carried exactly and the one
    rounding the rule does name is applied once — 7,707.71 − 462.4626 − 2,826.1603… + 616.6168 =
    5,035.7038… → **5,035.70**.
- *And a second inconsistency inside the same policy*: `suspended_day_relief_basis` tier 1 reads "the
  escalated fee is relieved by **one thirtieth of itself for each of those suspended calendar days**" —
  precisely the per-unit shape the convention now governs, and word-for-word the shape that was
  rewritten in policies 1 and 5 this round to strike the per-unit amount to the cent. Applied here it
  gives 7,707.71 ÷ 30 = 256.92 struck to the cent, taken 11 times = **2,826.12**, and a management fee
  of **5,035.75**. `compute` instead multiplies first and rounds once (2,826.16). So after this round the
  charter handles one sentence shape in two different ways, and the policy that keeps the old handling
  is the one whose sentence was left alone.
- *Demonstrated consequence*: three defensible values for one scored parameter — 5,035.70 under the
  convention as published, 5,035.71 under `compute`, 5,035.75 if the per-unit sentence is read the way
  the same charter now reads the other two. The cost does not stop at the management fee: it is the
  figure the service credit's `fee_base_usd` averages, so it propagates into task 0's third write.
- *Affected artifact*: `cafe.extended.yaml` → `cafe_ext_management_fee_invoice`, `compute` bindings
  `colocation_allowance_usd`, `suspended_day_relief_usd`, `subsidy_surcharge_usd`, their
  `compute_basis` sentences, and the `suspended_day_relief_basis` tier 1 sentence; `tasks/0.json` →
  the scored `amount_usd` of the step-11 write. **Bears on task 0.**
- *Relation to previous revisions*: the three `RND` wrappers are byte-identical to round 1, so this is
  not a reworker regression. It became **reachable** this round: until the convention was stated, "round
  each component" was merely unstated; now the charter tells a reader how to round, and following that
  instruction produces the wrong cent. Two of my earlier rounds swept `RND` *arguments* for half-cent
  ties and round 3 swept intermediate `RND` *placement*; neither asked whether each terminal `RND` was
  licensed by its own sentence, which is the question the newly published convention raises. Disclosed
  on the same footing as F-R2 and OBS-R1.

## closing_checklist (revision_4)

| item | round 3 | round 4 |
| --- | --- | --- |
| base frozen; base copy verbatim | ✔ | ✔ re-diffed empty; `check_base_frozen` green over 10 files |
| compute unchanged where claimed | n/a | ✔ both bindings string-identical to round 3 |
| prerequisites unmet at the opening | ✔ | ✔ all five, zero satisfying rows |
| ≥1 honest `method` per computation | ✔ | ✔ unchanged; twelve `method` factors, none collapsing |
| ladder faces stated in the rule | ✘ 2 of 170 | ✔ **0 of 170**; the 21 remaining misses are benign recastings, set-identical to round 3 |
| unlicensed intermediate rounding | ✘ 2 bindings | ✔ **0** |
| **every terminal `RND` licensed by its own sentence** | not asked | ✘ **3 bindings in 1 policy** (F-R3) |
| the rounding convention applied consistently | n/a | ✘ **6 of 7 policies** |
| every factor bears weight against an honest baseline | ✔ | ✔ all 34, none dead |
| no scored value moved | ✔ | ✔ 7 + 7 + 34 + 5 figures bit-identical |
| gates re-run on the final form | cited | cited from the brief, all green |

**Per-task verdicts, revision_4.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | **FAIL** — F-R3 | **PASS** | **PASS** | **FAIL** — 5035.70 / 5035.71 / 5035.75 | **SOURCE-POLICY RED** |
| 1 | **PASS** | **PASS** | **PASS** | **PASS** | **PASS** (third consecutive) |

All three round-3 items are genuinely closed, and closed at source rather than by relabelling: the
compute did not move and the prose came onto it. The convention adopted to close them is sound and I
accept it as something the KB may publish. The one open item is that the convention now makes a
pre-existing silence in a third policy into a reachable second answer — a finding my own earlier sweeps
did not ask for, disclosed as such.

No artifact was edited by this audit, and no fix was designed or arranged.

---

# revision_5

Revisions 1–4 are left untouched. Post-reveal verification pass.

## charter_global_frozen (revision_5)

| source | round 4 | round 5 | |
| --- | --- | --- | --- |
| `cafe.extended.yaml` | be132c2e…9a58fd | **278f69fc582590cb175fc11874c01c90736d028f9745c98d3dc7f178cc014370** | changed |
| `task_tools.py` | 3aa99ca0…30c2bb | identical | unchanged since round 2 |
| `0.masked.json` | 20d2cb1e…e4a25a | identical | unchanged |
| `1.masked.json` | b22fbfdf…6a4b67f | identical | unchanged |

All four recomputed on disk and identical to the brief. Neither world moved; the extended file's first
799 lines still `diff` empty against `blueprint/products/cafe.yaml`. `task_tools.py` unchanged, so the
tool-contract and uuid conclusions of `revision_2` carry forward by hash.

**Three computes changed**, located by string comparison against the round-4 expressions recorded in
`revision_4` rather than taken from the brief:

| policy / binding | round 4 | round 5 |
| --- | --- | --- |
| `late_charge_assessment` / `result` | `MN(RND(outstanding × rate/100 × months, 2), cap)` | `MN(RND(outstanding × rate/100, 2) × months, cap)` |
| `standby_charge_assessment` / `standby_before_loading_usd` | `RND(base × rate/100 × pause_months, 2)` | `RND(base × rate/100, 2) × pause_months` |
| `management_fee_invoice` / `suspended_day_relief_usd` | tier 2 `RND(esc × int(days/7) / 30, 2)` | tier 2 `RND(esc × int(days/7) × 7 / 30, 2)` |

Every other `RND`-bearing binding — including `short_notice_charge_usd` and `notice_relief_usd`, the two
repaired in rounds 3 and 4 — is string-identical to round 4.

## round_4_item_disposition

### F-R3 — CLOSED

**The criterion, judged on its own terms (scrutiny point 1).** The reworker states it as: a *per-unit
price* is struck once and charged as many times as a unit occurs, with no fixed whole it is a share of;
a *share of a whole* is a count taken against a fixed period, applied once, the resulting figure rounded
once. I accept it. It is the distinction a business actually draws between a rate card and a
pro-ration, it is decidable from the sentence itself rather than from the compute, and it sorts the
charter's five contested sentences the way the domain would:

| sentence | fixed whole it is a share of? | verdict |
| --- | --- | --- |
| one fifteenth of the change administration fee per whole week of shortfall | none — a shortfall can run any number of weeks | per-unit price |
| one fiftieth of the exit charge per whole week of notice beyond the notice period | none | per-unit price |
| the outstanding amount at the late charge rate **for each month charged** | none — months charged is unbounded | per-unit price |
| the standby fee base at the standby rate **for each month of pause** | none | per-unit price |
| the escalated fee relieved for suspended days, divisor thirty | **yes — a thirty-day month**, and the fee relieved is a monthly fee | share of a whole |

**The reclassification is materially implemented, not asserted (the move the brief warned about).** Had
the sentence been left as "one thirtieth of itself **for each of those suspended calendar days**" and
merely re-labelled, the finding would have been dissolved rather than fixed — the per-unit reading would
still have been available to any reader. It was rewritten instead:

> "…the escalated fee is relieved **in the share that those suspended calendar days bear to a thirty-day
> month**, the figure so obtained rounded to the nearest cent…"

There is now **no per-unit amount in the sentence at all**, so the third reading has nothing to strike.
`compute` matches it exactly — one multiplication by the share, one rounding —
`RND(escalated_fee_usd * suspended_days_ytd / K('suspended_day_divisor'), 2)`.

**Does the relief genuinely fall on the claimed side?** Yes. The divisor is not an arbitrary constant
but the thirty-day month the fee itself is quoted for, so eleven suspended days is eleven-thirtieths of
one monthly fee — one share applied once, not eleven prices charged eleven times. The argument holds.

**Does the tier still carry a real `method` distinction after the rewrite?** Yes, and it now rests on
the counting basis, as claimed:

- tier 1: the share that **those suspended calendar days** bear to a thirty-day month → 11⁄30
- tier 2: the share that **the days falling within whole weeks** of those suspended days bear to a
  thirty-day month → (⌊11/7⌋ × 7)⁄30 = 7⁄30

Both are shares of the same whole; what differs is which days are counted — the day-count family, the
same axis on which `short_notice_charge_basis` and `notice_relief_basis` were repaired in rounds 3 and 4.
The outcomes differ whenever the suspended days are not a whole number of weeks, which they are not
here. Tier 2 is not taken on either seeded world, so its sevenfold change of meaning moves no scored
figure; as a business rule, granting relief only for complete weeks of closure is one a caterer would
publish.

**Scrutiny point 2 — the criterion applied charter-wide, by me.** I re-ran my round-4 test: for each
policy, strip every `RND` whose own `compute_basis` sentence names no rounding, then recompute on the
world of that write. This is the test that found F-R3 at 6 of 7.

| policy | gold | under the criterion |
| --- | --- | --- |
| model_change_confirmation | 8066.07 | **8066.07** ✔ |
| management_fee_invoice | 5035.71 | **5035.71** ✔ |
| service_credit_settlement | 1511.64 | **1511.64** ✔ |
| late_charge_assessment | 678.08 | **678.08** ✔ |
| early_exit_charge | 55283.28 | **55283.28** ✔ |
| standby_charge_assessment | 26058.24 | **26058.24** ✔ |
| closing_settlement_payment | 150431.90 | **150431.90** ✔ |

**7 of 7**, up from 6 of 7. Nothing is stripped any more, because every `RND`-bearing binding's own
sentence now names its rounding.

**The treatment reached every silent site, not only the three named.** My binding-level sweep in round 4
found **14** bindings whose own sentence licensed no rounding — `opening_project_settlement_usd`,
`colocation_allowance_usd`, `suspended_day_relief_usd`, `subsidy_surcharge_usd`, `fee_base_usd`,
`outstanding_amount_usd`, `exit_fee_base_usd`, `exit_charge_before_allowances_usd`,
`standby_fee_base_usd`, `deposit_returned_usd`, `subsidy_refund_usd`, `inventory_recovery_usd`,
`subsidy_refunded_after_carry_over_usd`, `smallwares_credit_usd`. Re-run now: **0 of 29**. The
reworker's 14-bindings figure matches mine exactly; its "39 sites" counts each `RND` occurrence inside
tiered expressions, which is a finer granularity of the same population, and both instruments end at
zero.

**Scrutiny point 3 — the literal reading of each changed sentence, in exact decimal.**

| changed sentence | literal reading | gold |
| --- | --- | --- |
| "The late charge is the amount still outstanding taken at the late charge rate, **rounded to the nearest cent**, charged for each month charged, and held to the ceiling" | 42,380.00 × 1.6 % = **678.08** struck; × 1 month = 678.08; under the 4,800.00 cap | **678.08** ✔ |
| "The standby charge is the standby fee base taken at the standby rate, **rounded to the nearest cent**, charged for each month of pause charged, and the loading is then applied once…" | 18,096.00 × 60 % = **10,857.60** struck; × 2 months = 21,715.20; × 1.20 = **26,058.24** | **26,058.24** ✔ |
| "…relieved in the share that those suspended calendar days bear to a thirty-day month, the figure so obtained rounded to the nearest cent" | 7,707.71 × 11⁄30 = **2,826.16** | feeds 5,035.71 ✔ |

And the whole of policy 2 read literally: co-location allowance "the co-location rate taken on the
escalated fee, **rounded to the nearest cent**" = 462.46; relief = 2,826.16; surcharge "the subsidy
shortfall rate taken on the escalated fee, **rounded to the nearest cent**" = 616.62; escalated fee less
those two reductions plus that surcharge = **5,035.71** — the gold cent, from the prose alone.

**Both rivals are unconstructible, verified rather than asserted.**

- **5,035.70** required the three components to be carried unrounded. All three sentences now name their
  own rounding, so a reader cannot carry them unrounded without contradicting the text.
- **5,035.75** required reading the relief as a per-unit price struck per day. The sentence no longer
  contains a per-unit amount — it states a share of a thirty-day month — so there is nothing to strike.

## no_scored_value_moved (verified; three computes changed, so nothing carried forward)

| | round 5 | round 4 | |
| --- | --- | --- | --- |
| 7 expected values | 8066.07 / 5035.71 / 1511.64 / 678.08 / 55283.28 / 26058.24 / 150431.90 | identical | **all SAME** |
| 7 whole baselines | 1650.0 / 11000.2 / 689.5 / 0.0 / 69600.0 / 13920.0 / 47026.0 | identical | **all SAME** |
| 34 per-factor baselines | — | identical | **all SAME, 0 moved** |
| 5 edge-skip figures | task 0: 1970.0, 2963.1 · task 1: 149753.82 / 95148.62 / 124373.66 | identical | **all SAME** |
| `RND` half-cent sweep | 0 sites | 0 | SAME |

The three changed computes are value-neutral on the seeded worlds for reasons I checked rather than
assumed: the late charge's `months_charged` is 1 and the standby's per-month figure 10,857.60 is exact
to the cent, so striking before or after multiplying cannot differ; and the relief's changed tier is
tier 2, which neither world takes.

All five prerequisite edges re-verified unmet with zero satisfying rows.

## the instruments (scrutiny point 5)

| sweep | round 4 | round 5 |
| --- | --- | --- |
| ladder faces, verbatim containment | 170 checked, 21 misses | 170 checked, **21** misses |
| unlicensed rounding, binding level | 0 intermediate / 14 terminal unlicensed at round 3 | **0 of 29** |
| convention test | 6 of 7 | **7 of 7** |
| `RND` half-cent | 0 | **0** |
| `method` factors surviving the strip-the-literals test | 12 of 12 | **12 of 12** |

**The 21 are set-identical to my round-4 list**: I diffed the two normalised lists item by item and the
diff is empty. So the face that the brief says gained a rounding phrase mid-round and was then closed is
indeed closed — no new miss survives, and none of my adjudicated-benign 21 was silently swapped for a
different one.

## new_defects

**None.** Every check that found something in rounds 1–4 was re-run and is clean: the convention test
that found F-R3 now passes 7 of 7; the binding-level rounding-licence sweep that would have found it
earlier reports 0 of 29; the face sweep is unchanged at the same benign 21; the half-cent sweep is 0;
the method-label test is 12 of 12; every factor still bears weight against a baseline that equals its
own fall-through; and all five edges are still genuinely unmet.

## closing_checklist (revision_5)

| item | result |
| --- | --- |
| per-task audit files one-to-one with the tasks, `_difficulty.md` alongside; revisions 1–5 all preserved | ✔ |
| every comparison section carries a PASS | **✔ both tasks PASS at revision_5** |
| base frozen, base copy verbatim | ✔ re-diffed empty; `check_base_frozen` green over 10 files |
| extended policies fully covered; the two tasks' scopes pairwise disjoint | ✔ 3 + 4 = 7 |
| task tools and GT closed; each uuid8 independently generated and frozen | ✔ unchanged since round 2 |
| trees: 1–3 prerequisite problems, `value_input` floor, `owner=user` write, acyclic | ✔ task 0: 2 and 2; task 1: 3 and 3 |
| prerequisites genuinely unmet at the opening | ✔ all five edges, zero satisfying rows |
| 4–6 factors, ≥2 `parameter`, ≥1 honest `method` per computation | ✔ 12 `method` factors, none collapsing |
| ladders ≥3 tiers, stated in the rule, tiers distinct in outcome, conditions and outcomes ones the business holds | ✔ |
| every factor bears weight against an honest baseline; baseline alone definite and ≠ gold | ✔ 34 of 34 |
| cross-difficulty rows seeded and consistent with the other product's charter | ✔ pantry at 4,180.00; market re-checked |
| rule ↔ compute equivalence both ways, including rounding placement | ✔ 0 of 29 unlicensed; convention 7 of 7 |
| instantiation-stage gates re-run on the final form | cited from the brief, all green |

**Per-task verdicts, revision_5.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** | **PASS** | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** | **PASS** | **PASS** (fourth consecutive) |

**This difficulty passes the source-layer audit.** All four relationships hold on both tasks. Across
five rounds the audit raised nine REDs in round 1, one in round 2, one in round 3, one in round 4 and
none now; three of the later findings were my own under-calls, disclosed as such rather than presented
as regressions. Every one is closed at source, and no scored value moved in any round after the first:
7 expected values, 7 whole baselines, 34 per-factor baselines and 5 edge-skip figures have been
bit-identical since round 2.

No artifact was edited by this audit, and no fix was designed or arranged.
