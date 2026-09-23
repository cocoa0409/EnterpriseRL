# Policy-task audit — car_rental_desk / charter-global

## charter_global_frozen

- auditor: independent source-layer auditor (not the instantiating agent)
- freeze time (charter-global section): 2026-09-16, written **before any task's GT fields were read**
- frozen inputs and their hashes, verified against the brief by `sha256sum`:
  - `env/env_0000_online_travel_agency/tasks/car_rental_desk/drive.extended.yaml` — `4876de238d2bf457ca35a7edcfc4605f7076fa8a415392f78782b28d2654cc29`
  - `env/env_0000_online_travel_agency/tasks/car_rental_desk/task_tools.py` — `b28e8776f3789a0f59a9fcd501f1256668a0a872c6215e456b75099d219a0690`
- also read in full (the view division permits them): `env/env_0000_online_travel_agency/blueprint/blueprint.yaml`,
  `env/env_0000_online_travel_agency/blueprint/db_schema.json`, `env/env_0000_online_travel_agency/blueprint/share_tools.py`,
  `env/env_0000_online_travel_agency/blueprint/products/drive.yaml`, and — only for the parameter tables that
  `CPARAM('club',…)` / `CPARAM('care',…)` resolve against — `products/club.yaml` and `products/care.yaml`.
- fields explicitly masked while this section was written: every task file's `evaluation_criteria`,
  `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`,
  `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`. The task files were read only
  through the coordinator's masked views (`frozen_time`, `user_scenario`, `initial_state`), whose
  sha256 were verified as `1dad8ca…f403f2` (0.json) and `086b9c4…64fce8875` (1.json).
- **Nothing in this section is derived from a revealed GT field.** No task's GT was read until both
  `0.md` and `1.md` carried a frozen `source_derivation_frozen`.
- entry conditions: the instantiation-stage gates were re-run by the coordinator and supplied verbatim
  with the brief — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK. They are cited, not re-run here. `check_traceability.py` is properly deferred to the KB stage.
  No input was missing. A green gate is the qualification to enter this audit, not a proof of correctness.

### policy_conflict_scan

The base section of `drive.extended.yaml` was diffed key-by-key against
`blueprint/products/drive.yaml` (parsed YAML, deep compare): **the base copy is verbatim identical** —
the only extra top-level key is `extended_policies`. So the base surface carries no rewrite.

Overlapping subjects across the merged policy set:

| subject event | policies that reach it | compatible? |
| --- | --- | --- |
| `drive_cancellation_charge` | base `drive_cancellation`, ext `drive_ext_cancellation_charge` | **NO** on the ladder clause — but that clause is *declared* in `overwrite` (see `override_declarations`) |
| `drive_refund_payout` | base `drive_refund_settlement`, ext `drive_ext_cancellation_refund` | **NO** on two base sentences, *undeclared* (see `override_declarations`) |
| `drive_damage_charge` | base `drive_damage_and_recharges`, ext `drive_ext_damage_recharge`, ext `drive_ext_recharge_dispute` | **NO** on the administration-charge sentence, *undeclared* (see `override_declarations`) |
| `drive_rate_charge` | base `drive_agg_rental_history`, base `drive_club_and_corporate_interaction` | compatible (one governs referral authority, the other discount/points) |
| `drive_book` / `drive_confirm` | base `drive_agg_multi_holding`, `drive_booking_terms`, `drive_prepayment` | compatible; disjoint quantities |

Time anchors: `drive_cancellation.inside_free_cancellation` anchors on `drive_rentals.confirmed_at`
in `elapsed_hours`, boundary inclusive; `drive_damage_and_recharges.inside_damage_window` anchors on
`drive_rentals.returned_at` in `calendar_days` from the day after the return date, boundary inclusive.
Both are single-anchored and internally consistent — **except** that the duration the first one consumes
is named and glossed as a *pickup*-relative term (finding F-3).

Cross-category read boundaries declared: `drive_ext_cancellation_charge` → `club`;
`drive_ext_cancellation_refund` → `club`; `drive_ext_damage_recharge` → `club`, `care`;
`drive_ext_recharge_dispute` → `care`. Each declared category is actually read by that policy's
`compute` (`CPARAM`/`EXISTS`/`XCOUNT`), and no `compute` reads a category the policy does not declare.
No policy reads `air`, `stay`, `bundle` or `biz`; none is declared. Consistent.

Terminal states: each extended policy's target tool writes exactly one row and changes no status.
No extended policy claims a lifecycle transition, so no terminal-state conflict with `lifecycle` exists.

**Scope exclusivity and joint completeness of the M tasks.** Derived from the two worlds and the
policy surface alone (not from `charter_scope`, which was masked):

- task 0's tree = { root `drive_ext_cancellation_refund`, prerequisite `drive_ext_cancellation_charge` }
- task 1's tree = { root `drive_ext_recharge_dispute`, prerequisite `drive_ext_damage_recharge` }

The two sets are **pairwise disjoint** and **jointly cover all four** extended policies. No extended
policy is claimed twice and none is orphaned.

### rule_compute_equivalence

Check 2 was run binding by binding over all four extended policies (64 `compute` bindings in total).
Every binding carries a `compute_basis` entry, and every `compute_basis` entry is a verbatim substring
of that policy's own `rule` (checked by string containment, not by paraphrase). Every quantity, window,
filter, tier, branch, cross-category read, acting base, cap/floor and rounding convention named in a
`rule` is implemented by exactly one restricted expression, and the sweep back finds no expression
without a rule sentence. Specifically:

- rounding: all four policies round **once, on the final figure** (`RND(…, 2)` as the outermost call in
  `result`), and each says so in its `rule`. No intermediate rounding appears in any binding.
- caps/floors: `drive_ext_cancellation_refund.result` = `RND(MN(MX(…,0.0), settled_in_advance_total),2)`
  ↔ "it is never less than nothing and never more than the money settled in advance" ✓;
  `drive_ext_damage_recharge.borne_after_protection` = `MX(…,0.0)` ↔ "never less than nothing" ✓;
  `drive_ext_recharge_dispute.after_insurance` and `.result` ↔ two "never less than nothing" sentences ✓.
- day-count conventions: `DAYS(F('cancelled_at'), F('pickup_at'))`, `DAYS(F('booked_date'), F('cancelled_at'))`,
  `DAYS(F('returned_at'), assessment_decided_on)` each have a "the … days are the calendar days from …
  to …" sentence in the rule ✓.
- history windows: `XCOUNT('care','care_claims', within_months=24, …)` ↔ "in the last twenty-four months" ✓.
  All other aggregates are unwindowed and their rules say "on the rental" (the DSL scopes `SUM`/`COUNT`/
  `MAX`/`LATEST` to the target holding's primary key, which is exactly "on the rental").

**One divergence found** — see finding **F-4**: `drive_ext_cancellation_refund.goodwill_put_back`'s
second branch is implemented as `supplier_messages >= 1` while the `rule` states that tier as
"Where the supplier has sent **one** message about the rental". Rule and compute therefore part company
on a world with two or more supplier messages and no club rental discount: the rule sends that world to
its fall-through ("Nothing is put back"), the compute sends it to the 25 % branch.

### action_binding_and_uuids

| policy | `computes` | `target_tool` | owner | claimed by another policy? |
| --- | --- | --- | --- | --- |
| `drive_ext_cancellation_charge` | `cancellation_charge_usd` | `confirm_cancellation_charge_358c6472` | user | no |
| `drive_ext_cancellation_refund` | `refund_amount_usd` | `post_cancellation_refund_344e0f66` | agent | no |
| `drive_ext_damage_recharge` | `damage_recharge_usd` | `post_damage_recharge_2d59c35f` | agent | no |
| `drive_ext_recharge_dispute` | `disputed_amount_usd` | `raise_recharge_dispute_65c619e1` | user | no |

Each `(target_tool, computes)` pair is claimed by exactly one policy. Each tool's function body in
`task_tools.py` performs one `ctx.create` with the arguments as given and makes **no** eligibility,
ordering or entitlement judgement — verified by reading all four bodies end to end; there is no `if`,
no raise, no lookup of another row, and no branch on any prerequisite.

uuid8s: `358c6472`, `344e0f66`, `2d59c35f`, `65c619e1`. All four are distinct; no two share a prefix
of even two characters; none is a digit-sequence neighbour of another; there is no common stem with a
varied tail and no visible batch derivation. Independently generated and frozen. ✓

Docstrings: none names another tool, none carries a policy id or a snake_case token, and none states a
position in a sequence. The two phrases that mention time — `post_cancellation_refund_344e0f66`'s
"the earlier payment line being reversed" and `post_damage_recharge_2d59c35f`'s "the damage the rental
desk has assessed" — both point at a **record already on file**, not at another problem's write, so
neither leaks an ordering. ✓

### prerequisite_graph

Check 7 over the whole graph. Four policies, `prerequisite` filled in on all four:

| blocked policy | `problem` | `kind` | `gate` | `form` | `resolved_by` | acyclic |
| --- | --- | --- | --- | --- | --- | --- |
| `drive_ext_cancellation_charge` | *(none — `[]`)* | — | — | — | — | ✓ |
| `drive_ext_cancellation_refund` | `drive_ext_cancellation_charge` | `value_input` | `withheld_on_ledger` | `state` | `confirm_cancellation_charge_358c6472` | ✓ |
| `drive_ext_damage_recharge` | *(none — `[]`)* | — | — | — | — | ✓ |
| `drive_ext_recharge_dispute` | `drive_ext_damage_recharge` | `value_input` | `recharge_on_ledger` | `state` | `post_damage_recharge_2d59c35f` | ✓ |

- Every `problem` names another **extended** policy id in this file; neither points at a base policy
  and neither points at itself.
- The graph is two disjoint single edges — **acyclic**, and no cross-task reference exists that could
  close a cycle at the difficulty level.
- `resolved_by` is in both cases exactly the depended-on policy's own `target_tool`. ✓
- `kind: value_input` in both cases, and `gate` names a **binding that genuinely exists** in the blocked
  policy's `compute`: `withheld_on_ledger: SUM('drive_rental_entries','amount_usd', charge_category='cancellation_fee')`
  and `recharge_on_ledger: SUM('drive_rental_entries','amount_usd', charge_category='damage_charge')`. ✓
  Both are ledger sums scoped by the DSL to the target rental, so before the depended-on write they read
  0.0 and after it they read the amount that write booked — which is exactly what each edge's `effect`
  claims. The `effect` text is therefore a true assertion about the world and not a design note.
- `form: state` on both; `fallback_reason` is **absent on both**, which is correct — it is required
  exactly on action-form edges and neither edge is action-form.
- `condition` on each edge ("the rental's ledger carries a cancellation charge line standing against the
  rental being settled" / "the rental's ledger carries a damage recharge line standing against the rental
  under dispute") is neither stronger nor weaker than the state the `policy_source` sentence names — each
  simply renders the same ledger state in the words the tables use.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in
  either `prerequisite` block.

### prerequisite_sentences

Check 6, both edges, against the four-point test.

**Edge A — `drive_ext_cancellation_refund` → `drive_ext_cancellation_charge`.**
`policy_source`: *"The amount returned to the card that paid is worked out only after the rental's ledger
carries the charge withheld for the rental being given up."*

1. *Verbatim in the blocked policy's own rule?* Yes — it is the first sentence of
   `drive_ext_cancellation_refund.rule`, character for character.
2. *Ordering connective joining this policy's own result to what it waits on?* "only after" ✓; the subject
   is "the amount returned", which is this policy's own result ✓.
3. *Declared form honoured?* `state`. What it waits on is *"the rental's ledger carries the charge withheld
   for the rental being given up"* — a record-visible state, named in the words the tables and the ledger
   finder use ("the rental's ledger", "the charge withheld"). No performer, no action verb applied to an
   agent, no tool, no policy id, no snake_case token, no row id. ✓ State form, correctly declared, and the
   state form is the preferred form, so no `fallback_reason` is needed or given. ✓
4. *Strength and scope match the `condition`?* The sentence names a closed, singular state ("the charge
   withheld for the rental being given up"); the condition names the same closed state. Neither broader
   nor narrower. ✓

*One write brings that state about.* Across this difficulty's four task tools, only
`confirm_cancellation_charge_358c6472` writes a `drive_rental_entries` row with
`event_type="drive_cancellation_charge"` / `charge_category="cancellation_fee"`. `post_cancellation_refund_344e0f66`
writes `refund_payout`, `post_damage_recharge_2d59c35f` writes `damage_charge`, and
`raise_recharge_dispute_65c619e1` writes to `drive_damage_reviews` and not to the ledger at all. The
reader's hop is therefore unique. ✓

*Derivation, as the reader must make it:* the sentence says the returned amount waits on a withheld
charge standing on the rental's ledger → the renter queries the rental's ledger and finds no such line →
the reader asks which policy's own rule describes a charge withheld when a rental is given up →
`drive_ext_cancellation_charge`'s rule opens *"When a renter gives up a rental, the charge withheld is
worked out … and is withheld from that money rather than billed separately"* → that policy's own result
is the line the refund is waiting for → its `target_tool` is the write. **One reading only.**

*Nothing else about the dependency is written.* `drive_ext_cancellation_refund.rule` states the hop once
and never again: it names no tool, no policy id, no route, and no aggregated chain. The depended-on
policy's rule (`drive_ext_cancellation_charge`) does **not** restate the sentence and never mentions the
refund. ✓

**Edge B — `drive_ext_recharge_dispute` → `drive_ext_damage_recharge`.**
`policy_source`: *"The amount a renter may put in dispute is fixed only once the ledger carries the entry
for the damage the rental desk has approved against the rental."*

1. *Verbatim?* Yes — the first sentence of `drive_ext_recharge_dispute.rule`. ✓
2. *Ordering connective + own result?* "only once" ✓; subject "the amount a renter may put in dispute" ✓.
3. *Form?* `state`. What it waits on — *"the ledger carries the entry for the damage the rental desk has
   approved against the rental"* — is a record-visible state in table words. No tool, no performer, no id. ✓
4. *Strength/scope?* Closed and singular on both sides. ✓

*One write brings that state about:* only `post_damage_recharge_2d59c35f` creates a
`charge_category="damage_charge"` ledger row. ✓

*Derivation:* the sentence says the disputable amount waits on a damage entry standing on the ledger →
the ledger carries none for this rental → the reader asks which policy's own rule describes an amount
recharged for damage the rental desk has approved → `drive_ext_damage_recharge`'s rule opens *"The amount
recharged to a renter for damage the rental desk has approved against the rental is built from …"* →
its `target_tool` is the write. **One reading only.** ✓

*Nothing else:* `drive_ext_recharge_dispute.rule` names no tool and no policy id, and
`drive_ext_damage_recharge.rule` never mentions a dispute. ✓

**Undeclared cross-problem orders.** Sweeping every base and extended `rule` for an ordering connective
that joins two *problems* of this difficulty: the only candidate outside the two declared edges is the
base sentence in `drive_damage_and_recharges` — *"A renter who disputes a recharge is referred to a review,
and the disputed amount stays on the ledger until the review decides it."* This does not state an order
between two extended problems (no policy here performs the review's decision), and the dispute policy
carries its own prerequisite sentence, so per the skill's rule this is at most an **observation** (O-5)
and not a red light. No other rule states a cross-problem order.

### override_declarations

Check 1's **finding half**, run sentence by sentence over each `base_policy_refs` entry of each extended
policy. Consequences are demonstrated in the task files, not here.

**`drive_ext_cancellation_charge`** (refs `drive_cancellation`, `drive_prepayment`), `overwrite` = 1 entry.

| base sentence | extended treatment | declared? |
| --- | --- | --- |
| "Only the renter may cancel their own confirmed rental, and the cancellation is confirmed by the renter rather than performed on their behalf." | followed — `target_tool` is `owner="user"` | n/a |
| "A cancellation is handled free of charge only when frozen time is not after … confirmed … plus the free-cancellation term …" | **never mentioned** by the extended rule; the extended share applies unconditionally | **not declared** — see F-3 for why this is live only through the parameter gloss |
| "Inside the free-cancellation term nothing is withheld on any rate class and the prepayment is returned in full." | same | same |
| "Outside it the charge is read off the rate class's cancellation ladder …; where the ladder yields nothing the class's flat cancellation charge applies instead, and the two are never added." | replaced by the notice-band share | **DECLARED** ✓ (`superseded_clause` quotes it exactly; `replaced_by` = "The share of the basis that the notice band sets is eighty per cent.") |
| "A class that returns nothing withholds the whole prepayment, and the agency service fee is not returned on any class." | first half inert (no class here returns nothing under the extended share); **second half is contradicted by `drive_ext_cancellation_refund`, not by this policy** | see F-1 |
| "A cancellation made because the supplier itself cannot provide the vehicle is free on every class, whatever the ladder says." | the extended charge has **no** supplier-unavailability branch at all | **not declared** — F-2 |
| "A cancellation after the scheduled collection time has passed is not a cancellation but a no-show …" | not touched; inherited | n/a |
| `drive_prepayment`: "Where the renter later cancels, the prepayment is the money the cancellation charge is withheld from." | followed — the tool's `source_entry_id` points at the prepayment line | n/a |

**`drive_ext_cancellation_refund`** (refs `drive_refund_settlement`, `drive_cancellation`, `drive_prepayment`),
`overwrite` = `[]`.

| base sentence | extended treatment | declared? |
| --- | --- | --- |
| "An approved refund settles to the original form of payment and in no other form …" | followed | n/a |
| "A payout line is raised only while the rental record stands at cancelled, no show or returned." | inherited eligibility | n/a |
| "The settlement takes the rate class's processing time …" | not a scored quantity here | n/a |
| "Each payout is raised against the original ledger line it reverses, so a rental with several lines settles as several payouts and never as one lump sum." | the extended computes **one** net figure booked against **one** `source_entry_id` | **not declared** — F-5 |
| "A payout may never exceed the amount that original line actually collected, and the sum of a rental's payouts may never exceed its ledger total." | the extended caps at `settled_in_advance_total` (the **sum** of prepayment lines), not at the single line it is booked against | **not declared** — F-5 |
| `drive_cancellation`: "**the agency service fee is not returned on any class**" | the extended's `retained_service_element` first tier returns it in full ("nothing is retained") whenever the club tier carries the fee waiver | **NOT DECLARED — F-1** |

**`drive_ext_damage_recharge`** (refs `drive_damage_and_recharges`, `drive_agg_rental_history`),
`overwrite` = `[]`.

| base sentence | extended treatment | declared? |
| --- | --- | --- |
| "Damage discovered at return or afterwards is recharged … up to the rate class's waiver excess where the waiver was carried, and in full where it was not." | the extended always starts from `P('cdw_excess_usd')`, whether or not a waiver was carried, and then applies a loading and an uplift to it | **not declared** — F-6 |
| "A recharge is raised only while the rental record stands at picked up or returned." | inherited | n/a |
| "Damage is recharged only when the rental desk has already recorded an approved damage assessment against this rental." | inherited; the extended reads that same review for `assessment_decided_on` | n/a |
| "Damage found after the vehicle was handed back is recharged only when frozen time is not after … returned … plus the damage reporting window …" | inherited | n/a |
| "**The class's damage administration charge is added once per incident and never once per damaged part.**" | the extended's `admin_element` ladder produces `0.0` on one tier and `P('damage_admin_fee_usd') * 1.5` on another | **NOT DECLARED — F-2 (see below, this is the second red)** |
| "Tolls and traffic fines … Excessive soiling and smoking …" | not in this policy's scope | n/a |
| `drive_agg_rental_history`: "The renter's own history across rentals decides two things **and nothing else** …" | the extended makes a claims record decide a 10 %/25 % loading on the recharged amount | see O-2 (the extended reads *care* claims, not rentals) |

**`drive_ext_recharge_dispute`** (refs `drive_damage_and_recharges`, `drive_agg_rental_history`),
`overwrite` = `[]`. Sentence sweep: "A renter who disputes a recharge is referred to a review, and the
disputed amount stays on the ledger until the review decides it" is **followed** exactly (the tool creates
a `submitted`/undecided review and changes no charge). "The class's damage administration charge is added
once per incident" is *read back* by `disputable_base` as a subtraction, which is consistent with the
recharge line carrying it. `drive_agg_rental_history` contributes nothing this policy computes. No
undeclared conflict found in this policy.

### factor_ladders

Structure only. Whether a factor bears weight is a fact about one world and lives in that task's file.

| policy | factor | effect | `decides` | tiers | every tier in the `rule`? | in `compute`? | tiers pairwise disjoint *as stated*? | multi-source | `cross_difficulty` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `drive_ext_cancellation_charge` | `notice_band` | parameter | `notice_band_pct` | 3 | ✓ | ✓ | ✓ (≥14 / 3–13 / else) | no | — |
| | `charge_basis_measure` | **method** | `charge_basis` | 3 | ✓ | ✓ | ✓ (items / no items / nothing settled) | **yes** | — |
| | `member_relief` | parameter | `member_relief_pct` | 3 | ✓ | ✓ | ordered (tier 2 ⊃ tier 1) — O-1 | **yes** | **club** |
| | `value_band` | parameter | `value_multiple` | 3 | ✓ | ✓ | ordered (>90 ⊂ >60) — O-1 | no | — |
| | `holding_period_element` | parameter | `holding_element` | 3 | ✓ | ✓ | ordered (≥30 ⊂ ≥7) — O-1 | no | — |
| `drive_ext_cancellation_refund` | `settlement_measure` | **method** | `returnable_settlement` | 3 | ✓ | ✓ | ✓ (non-USD / USD & >1 payment / else) | borderline (one record set) | — |
| | `withholding_measure` | **method** | `withheld_applied` | 3 | ✓ | ✓ | ordered (both can hold) — O-1 | no | — |
| | `service_element` | parameter | `retained_service_element` | 3 | ✓ | ✓ | ordered (Platinum+ satisfies both) — O-1 | **yes** | **club** |
| | `supplier_message_goodwill` | parameter | `goodwill_put_back` | 3 | ✓ | **✗ tier 2 differs — F-4** | ✓ as stated (>1 / exactly 1 / else) | tier 1 yes, tier 2 no | — |
| | `optional_items_kept` | parameter | `items_kept` | 3 | ✓ | ✓ | ✓ (on booking day / after booking day) | **yes** | — |
| `drive_ext_damage_recharge` | `excess_borne_relief` | parameter | `excess_borne` | 3 | ✓ | ✓ | ✓ (CDW & discount / CDW & no discount / else) | **yes** | **club** |
| | `protection_deduction` | **method** | `protection_offset` | 3 | ✓ | ✓ | ✓ (both / CDW only / else) | **yes** | — |
| | `report_promptness` | parameter | `report_share_pct` | 3 | ✓ | ✓ | ordered (day 0 ⊂ ≤8) — O-1 | no | — |
| | `claim_record_loading` | parameter | `history_loading_pct` | 3 | ✓ | ✓ | ordered (>2 ⊂ ≥1) — O-1 | **yes** | **care** |
| | `vehicle_value_uplift` | parameter | `vehicle_uplift_pct` | 3 | ✓ | ✓ | ordered (>75 ⊂ >45) — O-1 | no | — |
| | `administration_element` | parameter | `admin_element` | 3 | ✓ | ✓ | class-dependent overlap — O-1, and tier 1 is unreachable — O-3 | no | — |
| `drive_ext_recharge_dispute` | `challenge_scope` | **method** | `disputable_base` | 3 | ✓ | ✓ | ordered (both can hold) — O-1 | no | — |
| | `protection_answered` | parameter | `insured_part` | 3 | ✓ | ✓ | ✓ (limit ≥ base & deductible / limit < base) | borderline (one record) | **care** |
| | `assessment_timing_share` | parameter | `window_share_pct` | 3 | ✓ | ✓ | ordered (>2w ⊂ >w) — O-1 | no | — |
| | `cleaning_challenged` | parameter | `cleaning_element` | 3 | ✓ | ✓ | ordered (tier 2 ⊃ tier 1) — O-1 | **yes** | — |
| | `fuel_challenged` | parameter | `fuel_element` | 3 | ✓ | ✓ | ✓ (no declined fuel dispute / one declined) | **yes** | — |

Counts per policy, against the bounds (4–6 factors; ≥2 `parameter`; ≥1 `method`):

| policy | factors | `parameter` | `method` | multi-source | `cross_difficulty` |
| --- | --- | --- | --- | --- | --- |
| `drive_ext_cancellation_charge` | 5 ✓ | 4 ✓ | 1 ✓ | 2 | club |
| `drive_ext_cancellation_refund` | 5 ✓ | 3 ✓ | 2 ✓ | 3 | club |
| `drive_ext_damage_recharge` | 6 ✓ | 5 ✓ | 1 ✓ | 3 | club, care |
| `drive_ext_recharge_dispute` | 5 ✓ | 4 ✓ | 1 ✓ | 2 | care |

All within bounds. **Label honesty:** the four `method` factors each substitute a *different algorithm*
for the quantity — `charge_basis_measure` changes which ledger rows compose the basis;
`settlement_measure` changes whether the whole, the discounted whole or the largest single payment is
taken; `withholding_measure` changes which ledger read supplies the withheld amount;
`protection_deduction` changes which products' paid amounts are subtracted; `challenge_scope` changes
whether the sum, the largest line or the sum-less-admin is the base. None of them merely swaps a rate or
a threshold. The `parameter` factors all substitute a number (a percentage, a multiple, a dollar figure)
into an unchanged formula. **Every label is honest.** Every `method` tier names a rule the charter states
(each is a verbatim sentence of the owning policy's `rule`).

**Baselines.** All four `baseline.rule` blocks were checked sentence by sentence against the owning
policy's `rule`: **every sentence of every baseline appears verbatim in the rule**, each baseline names
only its own default key in `baseline.params`, each factor's fall-through tier equals the baseline's
value for that input, and each baseline yields a **definite** number from the rule and the records alone
with no factor applied. Per-world fall-back numbers and the comparison against gold are in the task files.

**Per-task factor obligations** (≥1 multi-source and ≥1 `cross_difficulty` over the task's computations):
task 0's two policies contribute 5 multi-source factors and 2 `cross_difficulty` factors (both `club`);
task 1's two policies contribute 5 multi-source factors and 3 `cross_difficulty` factors (`club`, `care`,
`care`). Both satisfied structurally; see O-4 on the `club` reading for task 0.

### findings

Charter-global findings. Each names the tasks it bears on; the consequence against a world is demonstrated
in that task's file.

---

**F-1 — `SOURCE-POLICY RED`. Undeclared override: the agency service fee is returned to a club member,
against a base sentence that says it is never returned.**

- **Symptom.** `drive_ext_cancellation_refund` retains **nothing** for the agency service fee when the
  renter's club tier carries the fee waiver, so the fee that base says is never returned comes back.
- **Root cause.** `drive_ext_cancellation_refund.overwrite` is `[]` while `base_policy_refs` includes
  `drive_cancellation`, whose sentence the extended rule handles differently. The override is real and
  legal in substance; it was never **declared**, so both clauses stand in force and are rendered into the
  documents together.
- **Evidence (verbatim, both passages).**
  - base, `drive.extended.yaml:drive_cancellation.rule`: *"A class that returns nothing withholds the
    whole prepayment, and **the agency service fee is not returned on any class**."*
  - extended, `drive.extended.yaml:drive_ext_cancellation_refund.rule`: *"The service element the desk
    retains is the rate class's agency service fee. **Where the renter holds an active club membership
    whose tier carries the waiver of the agency service fee and money has been settled in advance on the
    rental nothing is retained**, and where the renter holds an active club membership whose tier carries
    a car rental discount and money has been settled in advance on the rental the fee is retained less
    that tier's car rental discount."*
  - `compute`: `retained_service_element: 0.0 if (fee_waiver_carried == True and settled_in_advance_total > 0) else …`
  - `drive_ext_cancellation_refund.overwrite: []`
- **Demonstrated consequence.** Task 0 — two defensible figures for the single scored payout. Demonstrated
  against task 0's world in `0.md` § `policy_self_consistency`.
- **Affected artifact.** `env/env_0000_online_travel_agency/tasks/car_rental_desk/drive.extended.yaml`,
  `extended_policies[1] drive_ext_cancellation_refund` — `overwrite`, `rule`, `compute.retained_service_element`,
  and the `service_element` factor. **Bears on: task 0.**

---

**F-2 — `SOURCE-POLICY RED`. Undeclared override: the damage administration charge is multiplied, against
a base sentence that fixes it at once per incident.**

- **Symptom.** `drive_ext_damage_recharge` adds the rate class's damage administration charge at 1.5× on
  one tier, and adds nothing at all on another, while base fixes it at once per incident.
- **Root cause.** `drive_ext_damage_recharge.overwrite` is `[]` while `base_policy_refs` includes
  `drive_damage_and_recharges`. This is the "anonymous intermediate factor" pattern: the deviation is
  carried by a multiplier (`reopened_admin_multiple: 1.5`) applied to an existing base quantity, with no
  new parameter name on the money and no `overwrite` entry naming the base sentence.
- **Evidence (verbatim, both passages).**
  - base, `drive_damage_and_recharges.rule`: *"**The class's damage administration charge is added once
    per incident and never once per damaged part.**"*
  - extended, `drive_ext_damage_recharge.rule`: *"The rate class's damage administration charge is then
    added once. Where the days to decision are beyond the rate class's damage reporting window **no
    administration charge is added**, and where the damage was decided within the prompt report days and
    a review already stands declined against the rental **the administration charge is added at the
    reopened administration multiple**."*
  - `compute`: `admin_element: 0.0 if days_to_decision > P('damage_report_window_days') else (P('damage_admin_fee_usd') * K('reopened_admin_multiple') if (days_to_decision <= K('prompt_report_days') and declined_reviews >= 1) else P('damage_admin_fee_usd'))`
  - `drive_ext_damage_recharge.overwrite: []`
- **Demonstrated consequence.** Task 1 — two defensible figures for the scored recharge, which then
  propagate into the scored dispute amount. Demonstrated against task 1's world in `1.md`.
- **Affected artifact.** `drive.extended.yaml`, `extended_policies[2] drive_ext_damage_recharge` —
  `overwrite`, `rule`, `compute.admin_element`, and the `administration_element` factor.
  **Bears on: task 1** (and, through the prerequisite edge, task 1's dispute computation).

---

**F-3 — `SOURCE-POLICY RED`. The free-cancellation term's declared meaning and the rule that consumes it
disagree about the anchor.**

- **Symptom.** `free_cancellation_hours_before_pickup` is glossed as a term measured backwards from
  collection; `drive_cancellation` measures it forwards from confirmation. The two readings put the same
  cancellation on opposite sides of the free window.
- **Root cause.** A parameter's declared meaning in `parameter_schema` was not brought into line with the
  `temporal_basis` of the only rule that consumes it. Both passages are in force in the merged policy and
  are rendered into the documents together.
- **Evidence (verbatim, both passages).**
  - `drive.extended.yaml:parameter_schema`: *"free_cancellation_hours_before_pickup: **Hours before
    collection** by which a cancellation carries no charge."*
  - `drive.extended.yaml:drive_cancellation.rule`: *"A cancellation is handled free of charge only when
    frozen time is not after **the moment the supplier confirmed the renter's booking plus** the
    free-cancellation term of the rate class booked."* — and `eligibility[inside_free_cancellation].temporal_basis`:
    `anchor_event: the moment the supplier confirmed the renter's booking`, `anchor_source: drive_rentals.confirmed_at`,
    `duration_source: variants.free_cancellation_hours_before_pickup`, `unit: elapsed_hours`.
- **Demonstrated consequence.** Task 0 — under the gloss the cancellation is inside the free window and
  **nothing is withheld**; under the rule it is outside and a charge is withheld. Two figures for the
  scored charge and two for the scored payout. Demonstrated in `0.md`.
- **Note for the reviewer.** The rule sentence and its `temporal_basis` are explicit and self-contained,
  so a reader who works from the rule alone reaches one answer. The defect is that the charter also
  publishes a contradictory statement of what the parameter means, and the KB renders both.
- **Affected artifact.** `drive.extended.yaml` — `parameter_schema.free_cancellation_hours_before_pickup`
  vs `policies[drive_cancellation].rule` / `.eligibility[inside_free_cancellation].temporal_basis`.
  **Bears on: task 0.**

---

**F-4 — `SOURCE-POLICY` (observation-level here; see the task files for whether it bites).
`goodwill_put_back`'s second tier: rule and compute state different conditions.**

- **Symptom.** The rule's second tier is "the supplier has sent **one** message"; the compute's second
  branch is `supplier_messages >= 1`.
- **Root cause.** Check-2 inequivalence in one branch of one binding: the compute's branch is strictly
  wider than the rule's tier, and the rule's fall-through therefore covers a world the compute sends to
  the 25 % branch.
- **Evidence.**
  - rule: *"Nothing is put back for messages the supplier has sent about the rental. Where the supplier
    has sent more than one message about the rental and the renter holds an active club membership
    carrying a car rental discount the whole of what is treated as withheld is put back, and **where the
    supplier has sent one message** about the rental the single message share of what is treated as
    withheld is put back."*
  - compute: `goodwill_put_back: withheld_applied if (supplier_messages > 1 and club_rental_discount_pct > 0) else (withheld_applied * K('single_message_share_pct') / 100.0 **if supplier_messages >= 1** else 0.0)`
- **Divergent world.** Two or more supplier notices on the rental **and** no active club rental discount:
  the rule puts back nothing, the compute puts back 25 % of what is withheld.
- **Consequence.** Neither task's world is that world (task 0 carries exactly one notice; task 1's
  computations do not use this binding), so no red light is raised against either task. Recorded here so
  it is not lost. **Bears on: neither task's score; task 0's `factor_weight` records the agreement.**

---

**F-5 — `SOURCE-POLICY` observation. Two base sentences of `drive_refund_settlement` are handled
differently by `drive_ext_cancellation_refund` with `overwrite: []`.**

- base: *"Each payout is raised against the original ledger line it reverses, so a rental with several
  lines settles as several payouts and never as one lump sum."* and *"A payout may never exceed the amount
  that original line actually collected …"*
- extended: one net figure, booked by `post_cancellation_refund_344e0f66` against one `source_entry_id`,
  capped at `settled_in_advance_total` (the **sum** of prepayment lines, not the single line reversed).
- **Why observation and not red:** in both of this difficulty's worlds the rental carries exactly one
  prepayment line, so "the sum of the prepayment lines" and "the amount that line collected" coincide,
  and no second payout is required by any money the extended formula actually returns. The conflict is
  real in the charter but has no demonstrable consequence on either scored solution. It would become a red
  on any world with two prepayment lines — which is exactly the world `settlement_measure`'s second tier
  is written for. **Bears on: neither task's score; noted for tasks 0.**

---

**F-6 — `SOURCE-POLICY` observation. The extended damage basis ignores whether the waiver was carried.**

- base, `drive_damage_and_recharges.rule`: *"Damage discovered at return or afterwards is recharged to the
  renter **up to the rate class's waiver excess where the waiver was carried, and in full where it was
  not**."*
- extended, `drive_ext_damage_recharge`: `excess_borne` always starts from `P('cdw_excess_usd')`, and the
  ladder's fall-through is that same figure — there is no "in full" branch and no input carrying the
  actual cost of the damage.
- **Why observation and not red:** task 1's rental **did** carry a waiver (a `collision_damage_waiver`
  ledger line stands on it), so base's "where the waiver was carried" limb is the live one and the
  extended figure sits under the excess. On a world with no waiver, base demands a quantity the extended
  policy has no input for — but no task of this difficulty presents that world, so no second number can be
  demonstrated. `overwrite: []` leaves it undeclared. **Bears on: task 1 (latent).**

---

**O-1 — observation. Ladders are ordered, not pairwise disjoint as stated.** Eleven of the twenty-one
factors have tiers that overlap when read as free-standing conditions (for example `report_promptness`'s
"decided on the day the vehicle came back" is a sub-case of "decided within the prompt report days"), and
are resolved only by the order in which the `compute` tests them. The `rule` prose is written in the same
order — baseline sentence first, then successive "Where …" overrides — so the first-match reading is the
only one under which the baseline sentence is ever true, and no second number can be derived from the
overlap. Recorded as the charter's convention, not as a red light.

**O-2 — observation. `drive_agg_rental_history`'s "and nothing else" versus the claims loading.** Base:
*"The renter's own history across rentals decides two things and nothing else: whether a discretionary
waiver is within the desk's authority, and whether the supplier network requires a manual review …"*
`drive_ext_damage_recharge.claim_record_loading` makes a claims record decide a 10 %/25 % loading on a
recharged amount. The extended reads **care** claims (`XCOUNT('care','care_claims', …, claim_type='rental_damage')`),
not rentals, so it arguably falls outside base's "history across rentals" — but the extended's own rule
sentence says only *"the renter's own record of rental damage claims"* without saying where they were
filed, and this difficulty also publishes a drive-side measure of the same name (`drive_msr_damage_claims_24m`,
"count of `drive_damage_charge` rows … in the last 24 months"). A reader can take either. No red light:
in task 1's world both readings return the same count and therefore the same tier (shown in `1.md`).

**O-3 — observation. `administration_element`'s first tier is unreachable given the base gate.** The tier
"the days to decision are beyond the rate class's damage reporting window" can only be taken when the
approved assessment was decided after the window closed; but `drive_damage_and_recharges.inside_damage_window`
already forbids the recharge when frozen time is past `returned_at + damage_report_window_days`, and the
decision necessarily precedes frozen time. The tier is therefore a dropped branch in practice. It does not
cost either task a number, since neither task takes it.

**O-4 — observation. `club` is a category, not a difficulty.** `blueprint.yaml:difficulties` names five
difficulties over the categories `air`, `stay`, `care`, `drive`, `bundle`. `club` (and `biz`) have product
charters and seeded holdings but no difficulty of their own. Task 1 reads `care`, which **is** another
difficulty (`travel_protection_desk`). Task 0's only two `cross_difficulty` factors read `club`; under the
charter's own definition of the field ("another category's holding or ledger") they qualify and the gate
accepts them, and the `club_memberships` row is genuinely seeded, but under a strict reading of "another
**difficulty's** seeded records" task 0 has none. Recorded so the distinction is on the record.

**O-5 — observation. A base rule states an order that grounds no declared edge.**
`drive_damage_and_recharges.rule`: *"A renter who disputes a recharge is referred to a review, and the
disputed amount stays on the ledger until the review decides it."* It carries an ordering connective
("until"), but it orders a dispute against a *review decision*, which no policy of this difficulty writes,
so it grounds no edge and no task's tree rests on it. `drive_ext_recharge_dispute` carries its own
prerequisite sentence, so this is an observation rather than a red light.

**O-6 — observation. `drive_ext_recharge_dispute.subject` does not name the record its tool writes.**
`subject: [drive_damage_charge]`, but `raise_recharge_dispute_65c619e1` writes a `drive_damage_reviews`
row — the intake table — and posts no ledger line. The difficulty's claimed `event_types` in
`blueprint.yaml` carry no review-creation event, so there is no event family the subject could have named
instead. No consequence on any scored value.

## closing_checklist

Written after both tasks' reveals. **This difficulty does not close out.** Step 4's checklist is
recorded in full, item by item, with the two items that fail marked as such.

| item | status |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks (`0.md`, `1.md`), `_difficulty.md` alongside them | ✓ |
| old revisions traceable | ✓ — this is revision 1; the directory held no prior audit |
| every comparison section carries a PASS | **✗** — `0.md` and `1.md` each carry `SOURCE-POLICY RED` on policy self-consistency; the other three relationships PASS in both |
| this difficulty's extended policies fully covered | ✓ — `drive_ext_cancellation_charge`, `drive_ext_cancellation_refund` (task 0), `drive_ext_damage_recharge`, `drive_ext_recharge_dispute` (task 1); all four claimed, none twice |
| the M tasks' scopes pairwise disjoint, each spanning its whole tree | ✓ — `{charge, refund}` ∩ `{recharge, dispute}` = ∅; each scope is exactly its root plus its one prerequisite problem |
| task tools and GT closed | ✓ — REPLAY `clos = init` on both tasks (10/10 and 28/28), `match: True`, `db_closure_matches_initial_state: true` |
| each task tool uses an independently generated, frozen uuid8 | ✓ — `358c6472`, `344e0f66`, `2d59c35f`, `65c619e1`; distinct, no shared stem, no sequence |
| every tree has 1–3 prerequisite problems | ✓ — one each |
| ≥ `max(n−1, 1)` `value_input` edges | ✓ — one `value_input` edge each, floor 1 |
| ≥ 1 problem resolved by an `owner=user` tool | ✓ — task 0's prerequisite (`confirm_cancellation_charge_358c6472`), task 1's root (`raise_recharge_dispute_65c619e1`) |
| no cycle, including across tasks | ✓ — two disjoint single edges; the difficulty-level `prerequisite` graph is a DAG |
| every computation declares a self-sufficient baseline | ✓ — four baselines, each sentence of each present verbatim in its policy's `rule`, each giving a definite number (`351.86`, `0.00`, `807.50`, `541.80`), all four different from gold |
| 4–6 factors per computation, ≥2 `parameter` and ≥1 `method` | ✓ — 5(4p/1m), 5(3p/2m), 6(5p/1m), 5(4p/1m) |
| ≥1 multi-source and ≥1 cross-difficulty factor per task | ✓ — task 0: 5 multi-source, 2 cross (`club`, `club`); task 1: 5 multi-source, 3 cross (`club`, `care`, `care`). See O-4 on `club` being a category without a difficulty of its own |
| every ladder ≥3 tiers, stated in full in its rule | ✓ — all 21 ladders have three tiers; every tier is a sentence of the owning policy's `rule`. One tier's **compute** widens its rule condition — F-4 |
| every factor proved to bear weight against an honest baseline | ✓ — all 21 factors; auditor's recomputed sensitivities agree with `factor_sensitivity` figure for figure in both task files |
| instantiation-stage gates re-run once on the final form | ✓ — see below |

**Gate re-run on the final form** (artifacts unchanged by this audit; `drive.extended.yaml` and
`task_tools.py` still hash to `4876de2…` and `b28e877…`). From the repository root with
`DIFF=env/env_0000_online_travel_agency/tasks/car_rental_desk`:

```
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK            0.json 9 acts  det=True nonvac=True errs=0 clos=init=10 match=True
                     1.json 12 acts det=True nonvac=True errs=0 clos=init=28 match=True
SOLVABILITY OK
COMPUTE OK           suite means branches=29.50 steps=10.50; history_rows_max=14 branches_max=33
GROUNDING OK
SCOPE OK
```

**Disclosure: the mandated gate re-run rewrote the two task files.** `replay_tasks.py` carries an
unconditional write-back (`skills/erl-task-instantiate/scripts/replay_tasks.py:303`) that re-serialises
each task file to move `db_closure` / `db_closure_matches_initial_state` next to `initial_state`. Running
it therefore changed the byte hash of `tasks/0.json` and `tasks/1.json` after the reveal. Two points, both
verified:

- **No semantic change.** Parsed as JSON, the files before and after a run are **deep-equal**
  (`before == after` is `True` for both), and the top-level key order is unchanged. The only difference is
  the serialisation order of the keys **inside** `db_closure`.
- **The blind audit is unaffected.** Both task files were read at exactly the hashes the brief named —
  `c0c76c5002655ac27e28532f04d08cec9403294b74a019be7bb7d4b5d656ff43` (0.json) and
  `ae8c428b774910850ef5b4a9d15f0080d2280c41a8db3debfe512f2d3ae93744` (1.json), confirmed by `sha256sum`
  at the moment of the reveal — and the rewrite happened afterwards. Nothing was edited by hand by this
  audit; the audit's own write domain
  (`env/env_0000_online_travel_agency/audits/policy_task/car_rental_desk/`) was not exceeded, and
  `drive.extended.yaml` and `task_tools.py` still hash to `4876de2…` and `b28e877…`.

**O-7 — observation (harness, outside the four relationships).** That write-back is **not idempotent**:
`closure` is a Python `set`, so its iteration order varies between interpreter runs and every invocation
of the gate produces a different byte hash for the same semantic content. Three consecutive runs gave
`c0c76c5…` → `42f1b78…` → `5d4d48a…` for 0.json. Any workflow that pins a task file by hash — including
this audit's own masked-view protocol — will see spurious drift after each gate run. Recorded for the
harness owner; it changes none of the four relationships.

All seven green — which is exactly the point `_difficulty.md` § `charter_global_frozen` makes about
machine gates: they prove structure, references and parsability, and they did **not** catch either
undeclared override, because both deviations are carried inside prose and a multiplier rather than by a
new parameter name or a broken reference.

**Verdict for the difficulty.** The source-layer audit **does not pass**. Three of the four relationships
hold in both tasks — the problem tree holds, every factor bears weight, and the policy uniquely entails
the scored solution under the extended reading. Policy self-consistency fails, on three charter-global
defects whose consequences are demonstrated against both worlds:

| finding | kind | tasks affected | second figure it opens |
| --- | --- | --- | --- |
| **F-1** agency service fee returned against an inherited base sentence, `overwrite: []` | `SOURCE-POLICY RED` | 0 | payout `328.09` instead of `341.04` |
| **F-2** damage administration charge multiplied against an inherited base sentence, `overwrite: []` | `SOURCE-POLICY RED` | 1 | recharge `855.50` instead of `903.00`, dispute `445.05` instead of `464.05` |
| **F-3** the free-cancellation term's declared meaning contradicts the rule that consumes it | `SOURCE-POLICY RED` | 0 | charge `0.00` and payout `424.44` instead of `111.20` and `341.04` |

Plus the observations F-4, F-5, F-6 and O-1 … O-6, none of which moves a scored value on either world.

No artifact was edited by this audit, and no fix is designed or arranged here.

---

# revision_2 — re-audit of the reworked form (charter-global)

*Revision 1 above is left exactly as written. Nothing in it has been altered to accommodate the new form.*

## charter_global_frozen (revision 2)

- auditor: the same independent source-layer auditor. **This round is not blind and does not pretend to
  be** — round 1's GT was already seen, so the derivation below is a re-derivation with knowledge of the
  previous answer. Its purpose is narrower: to test whether each round-1 RED is genuinely closed rather
  than reworded, whether the rework introduced anything new, and whether anything already sound regressed.
- re-audit time: 2026-09-16.
- input movement, checked by hash before anything else was read:

| artifact | revision 1 | revision 2 | moved? |
| --- | --- | --- | --- |
| `drive.extended.yaml` | `4876de238d2bf457…2d654cc29` | `e8d856f196df35e0…29dc12f7` | **CHANGED** |
| `task_tools.py` | `b28e8776f3789a0f…99d219a0690` | `b28e8776f3789a0f…99d219a0690` | unchanged |
| masked view `0.json` | `1dad8ca794eed9ca…c746cff403f2` | `2d35dd8a5d3ea1ac…8fbfa811c7ad` | **CHANGED** |
| masked view `1.json` | `086b9c4956f0da19…cdc64fce8875` | `3337dee9c723bb3a…792b4915815a` | **CHANGED** |

All four verified locally by `sha256sum` against the brief; all four agree. Per the skill's re-derivation
rule, **`action_binding_and_uuids` is carried forward by reference**: `task_tools.py` is byte-identical,
so the tool contracts, docstrings and the four uuid8s (`358c6472`, `344e0f66`, `2d59c35f`, `65c619e1`)
stand as revision 1 found them, and the two hashes above are the grounds. Every other charter-global
section is **re-derived in full**, because `drive.extended.yaml` moved.

- gates: re-run by the coordinator on the reworked form and supplied verbatim; all seven green. The two
  numbers that moved are consistent with the rework — `0.json` now replays 10 acts (was 9) with
  `clos = init = 11` (was 10), and its `xfac` is 3 (was 2). Cited, not re-run here.

### revision_2 / policy_conflict_scan

Base copy re-checked: the base section of `drive.extended.yaml` is still **verbatim identical** to
`blueprint/products/drive.yaml` (parsed-YAML deep compare, zero differing keys; only `extended_policies`
is extra). The blueprint was not touched, so every base sentence revision 1 quoted is still in force
word for word.

Overlapping subjects, re-scanned. The three round-1 conflicts on `drive_refund_payout` and
`drive_damage_charge` are now **declared** rather than silent (next section). The subject map is
otherwise as revision 1 recorded it, with one carried-forward note: `drive_ext_damage_recharge` and
`drive_ext_recharge_dispute` still both declare `subject: [drive_damage_charge]` (O-6, answered with no
change — assessed below).

Scope exclusivity re-derived from the two worlds: task 0 = {`drive_ext_cancellation_refund` root,
`drive_ext_cancellation_charge` prerequisite}; task 1 = {`drive_ext_recharge_dispute` root,
`drive_ext_damage_recharge` prerequisite}. Still **pairwise disjoint and jointly complete**. No regression.

### revision_2 / override_declarations — the four undeclared overrides

`overwrite` has gone from 1 entry across the charter to **6**. Every one was checked mechanically for
verbatim fidelity on both sides — `superseded_clause` must appear verbatim in the **named base policy's**
rule, and `replaced_by` verbatim in the **extended policy's own** rule:

| policy | base policy | superseded clause verbatim in base? | replacement verbatim in extended rule? |
| --- | --- | --- | --- |
| `drive_ext_cancellation_charge` | `drive_cancellation` | ✓ | ✓ |
| `drive_ext_cancellation_refund` | `drive_cancellation` | ✓ | ✓ |
| `drive_ext_cancellation_refund` | `drive_refund_settlement` | ✓ | ✓ |
| `drive_ext_cancellation_refund` | `drive_refund_settlement` | ✓ | ✓ |
| `drive_ext_damage_recharge` | `drive_damage_and_recharges` | ✓ | ✓ |
| `drive_ext_damage_recharge` | `drive_damage_and_recharges` | ✓ | ✓ |

**Six for six.** These are real declarations naming the real base sentences, not paraphrases.

- **F-1 — CLOSED.** `drive_ext_cancellation_refund.overwrite` now carries
  `base_policy: drive_cancellation`, `superseded_clause: "the agency service fee is not returned on any
  class"`, replaced by the club-waiver sentences. The base clause is named exactly as revision 1 quoted
  it. The override is now legal *and* declared, so no competing clause survives to give a second figure.
  Consequence re-tested on task 0's world in `0.md` § revision_2.
- **F-2 — CLOSED.** `drive_ext_damage_recharge.overwrite` carries
  `superseded_clause: "The class's damage administration charge is added once per incident and never once
  per damaged part."`, replaced by the whole of the new administration paragraph — which covers both the
  reopened multiple *and* the new per-approved-assessment tier. Declared at the right granularity.
- **F-5 — CLOSED.** Two entries against `drive_refund_settlement`: the "several payouts and never as one
  lump sum" sentence, replaced by *"The amount returned is raised as one payout against the money the
  renter settled in advance, whatever the number of payments that money came in"* (a new sentence, now in
  the extended rule); and the per-line cap clause, replaced by the settled-in-advance cap. The second
  limb of that base sentence — *"the sum of a rental's payouts may never exceed its ledger total"* — is
  **not** superseded and is correctly left inherited; task 0 satisfies it (`341.04 ≤ 601.71`).
- **F-6 — CLOSED.** `superseded_clause: "Damage discovered at return or afterwards is recharged to the
  renter up to the rate class's waiver excess where the waiver was carried, and in full where it was
  not."`, replaced by *"The excess the renter bears is the rate class's waiver excess."* The "in full
  where it was not carried" limb that the extended policy had no input for is now explicitly retired
  rather than silently ignored.

Sentence-by-sentence sweep of the **new** sentences, hunting for a conflict the rework itself created:

| new sentence | base sentence it touches | verdict |
| --- | --- | --- |
| "The money settled in advance on a rental is the total of the advance payments taken on it, and it carries what was paid for the rental days, what was paid for any optional items bought in advance and the rate class's agency service fee." (both cancellation policies) | `drive_prepayment`: "The prepayment covers the rental days, the statutory charges and the protection products bought in advance, and never the deposit hold." | compatible — base's list is inclusive and its only exclusion ("never the deposit hold") is respected. But see **R2-O-3**: it collides with `accounts[rental_charges].meaning` |
| "The free-cancellation term … runs in whole elapsed hours from the moment the supplier confirmed the renter's booking, and not backwards from the scheduled collection moment" | `drive_cancellation`: "The free-cancellation term is counted in whole elapsed hours from the confirmation moment …" | **agrees verbatim in substance** — same anchor, same unit. No override needed |
| "; a rental given up inside that term has nothing withheld" | `drive_cancellation`: "Inside the free-cancellation term nothing is withheld on any rate class **and the prepayment is returned in full**." | first limb agrees; second limb unaddressed — **R2-O-2** |
| "…a rental **given up** inside that term…" | `drive_cancellation`: "A cancellation is handled free of charge only when **frozen time** is not after …" | different clock basis — **R2-O-2** |
| "Where more than one damage assessment stands approved against the rental the administration charge is added once for each approved assessment" | `drive_damage_and_recharges`: "added once per incident and never once per damaged part" | **consonant** with base (one per incident, not per part) and covered by the declared overwrite anyway |
| "Where more than one of the cases stated here fits a rental, the case stated earliest in this rule applies to that rental and the others do not." (all four policies) | none | new, and it resolves O-1 |

### revision_2 / rule_compute_equivalence

Re-run binding by binding over all four policies (75 bindings). Every `compute_basis` entry was tested
by string containment against its own policy's `rule`.

- **F-4 — CLOSED.** `goodwill_put_back`'s second branch now reads
  `supplier_messages == 1` (was `>= 1`), which matches the rule's "where the supplier has sent **one**
  message". The world revision 1 identified as divergent — two or more messages falling through the
  first tier — now goes to the rule's fall-through in both faces. Tiers are disjoint as stated (`> 1`
  versus `== 1`).
- **R2-O-1 — a new, smaller gap of the same kind.** Both goodwill tiers now read *"and the renter holds
  no travel protection policy in force **over the rental period**"*, and the `cross_category` note
  repeats the qualifier. The compute is `protection_in_force: EXISTS('care', status='in_force')` — a bare
  status test. **No binding reads `trip_start_date`, `trip_end_date` or `pickup_at`/`dropoff_at` for this
  purpose**, so "over the rental period" is stated in the rule and implemented nowhere. Divergent world:
  a renter with an in-force annual policy whose cover does not span the rental — the rule says no policy
  is in force over the rental period and puts value back; the compute says `EXISTS` is true and puts
  nothing back. Neither task's world contains an in-force policy at all, so no second number is
  demonstrable on either; recorded as an observation, exactly as F-4 was before it bit.
- **O-1 — CLOSED.** Revision 1 recorded eleven ladders whose tiers overlap when read as free-standing
  conditions, resolved only by the order the `compute` tests them, and accepted the first-match reading
  as the charter's convention. All four rules now close with *"Where more than one of the cases stated
  here fits a rental, the case stated earliest in this rule applies to that rental and the others do
  not."* The convention is now normative text a reader can apply, not a convention an auditor had to
  infer. (It is absent from the four `baseline.rule` blocks, correctly — a baseline states one value per
  input and has no competing cases.)
- **O-2 — CLOSED.** `drive_ext_damage_recharge`'s rule now says *"the renter's own record of rental
  damage claims **filed on their travel protection policies**"* in the opening sentence and in both
  ladder tiers, and the baseline sentence carries the same wording. The ambiguity revision 1 recorded —
  whether the claims meant were `care_claims` or this charter's own `drive_msr_damage_claims_24m` — is
  removed from the rule itself rather than left to the `cross_category` note.
- **O-3 — CLOSED, and genuinely so.** The unreachable tier is gone. `admin_element` is now
  `P('damage_admin_fee_usd') * approved_assessments if approved_assessments > 1 else (… * 1.5 if (prompt
  and declined) else …)`. Reachability: the tier needs two approved `damage_assessment` reviews on one
  rental, which nothing forbids — base's `damage_assessment_approved` gate requires **at least** one, and
  `drive_damage_reviews` has no uniqueness constraint per rental. Contrast the retired tier, which
  required a decision later than a window base's `inside_damage_window` gate had already closed. It is
  also base-consonant (one charge per approved assessment = once per incident, never once per damaged
  part) and covered by the declared overwrite regardless. Not a rewording.

**Two corrections to revision 1, disclosed rather than quietly restated.** Re-running the containment
check mechanically this round shows two claims in revision 1 § `rule_compute_equivalence` were
overstated. Both were equally true of the round-1 charter, so neither is a regression and neither is a
new defect — but revision 1 asserted a clean result it did not have, and that assertion is part of this
audit's own proof:

1. Revision 1 said "Every binding carries a `compute_basis` entry". It does not:
   `drive_ext_cancellation_charge` has 15 bindings and no `compute_basis` entry for `share_amount`,
   `after_relief` or `after_value`. All three are unnamed arithmetic steps whose semantics come from rule
   sentences that *are* quoted elsewhere ("the share is reduced by that tier's car rental discount",
   "The reduced share is then taken at the rental's own value multiple", and the `result` entry that
   combines them), and the other three policies do name their equivalents. No invented basis; a
   presentational gap, recorded as **R2-O-4**.
2. Revision 1 said every `compute_basis` entry "is a verbatim substring of that policy's own `rule`
   (checked by string containment)". One is not: `drive_ext_cancellation_refund.compute_basis.result` is
   `"it is never less than nothing and never more than the money settled in advance. The figure is
   rounded to two decimal places once, on the final figure."` — a stitch of two rule fragments that are
   not adjacent. Both fragments were re-tested individually this round and **each is verbatim in the
   rule**; the entry quotes nothing the rule does not say. Recorded as **R2-O-4**.

### revision_2 / prerequisite_graph and prerequisite_sentences

Re-derived in full against the moved charter. **Nothing regressed.**

- Both edges are intact and unchanged: refund → charge (`value_input`, gate `withheld_on_ledger`, form
  `state`, resolved by `confirm_cancellation_charge_358c6472`) and dispute → recharge (`value_input`,
  gate `recharge_on_ledger`, form `state`, resolved by `post_damage_recharge_2d59c35f`).
- Each `policy_source` is still verbatim in the **blocked** policy's own rule (re-tested by containment),
  still the opening sentence of that rule, and still absent from the depended-on policy's rule.
- Both gates are still real bindings of their blocked policy's `compute`.
- `form: state` on both, `fallback_reason` absent on both — correct, since neither is action-form.
- Acyclic; two disjoint single edges; no cross-task reference.
- The four-point test and the one-write-brings-the-state-about derivation from revision 1 §
  `prerequisite_sentences` still hold word for word — the rules gained sentences but neither prerequisite
  sentence was touched, and no new sentence names another problem's tool, a route or an aggregated chain.
- The new tie-break sentence is general text about this rule's own cases and states no cross-problem
  order, so it grounds no undeclared edge.

### revision_2 / factor_ladders

Structure re-derived. Counts per policy are unchanged (5 / 5 / 6 / 5; `parameter` 4/3/5/4, `method`
1/2/1/1), every ladder still has three tiers, and every tier is still a sentence of its policy's rule.
Two factors changed substance:

| factor | change | effect |
| --- | --- | --- |
| `supplier_message_goodwill` | tier conditions gained "and the renter holds no travel protection policy in force over the rental period"; `cross_difficulty` `null` → **`care`**; compute `>= 1` → `== 1` | closes F-4; intended to close O-4 for task 0 — **see R2-RED-1** |
| `administration_element` | first tier replaced (unreachable window tier → per-approved-assessment tier) | closes O-3 |

`drive_ext_cancellation_refund` now declares `cross_category: [club (branch), care (existence)]` with a
matching note, and `inputs.cross_category: [club, care]`. The declaration is structurally correct and the
gate accepts it. **Whether the world carries it is a per-world fact and is where it fails — R2-RED-1.**

All four baselines re-checked: every sentence of every `baseline.rule` is still verbatim in its policy's
rule (8 / 7 / 11 / 8 sentences, zero misses), `baseline.params` unchanged, each factor's fall-through
tier still equals the baseline value.

### revision_2 / findings

**R2-RED-1 — `SOURCE-FACTOR RED`. O-4 is not closed: the cross-difficulty evidence added to task 0 is
inert, and ablating it changes nothing.**

- **Symptom.** The rework added a `cross_difficulty: care` limb to `supplier_message_goodwill` and seeded
  a `care_policies` row in task 0's world. Deleting that row — indeed deleting the whole `care_policies`
  table from task 0's `initial_state` — leaves **every scored value identical**.
- **Root cause.** The seeded policy is `Trip Basics Standard` with `status: "expired"`, and the binding
  is `protection_in_force: EXISTS('care', status='in_force')`. `EXISTS` filters the holding table by
  `status='in_force'`, so the expired row is invisible to it and the read returns `False` — the same
  `False` an empty `care` table returns. The tier is therefore selected by `supplier_messages == 1`, a
  fact of this category's own ledger, with the `care` conjunct holding vacuously.
- **Evidence (re-checkable, run with the harness's own evaluator,
  `skills/erl-task-instantiate/scripts/check_compute.py:build_env`/`eval_compute`).** Ablation table for
  task 0, everything else replayed unchanged:

  | world | `cancellation_charge_usd` | `refund_amount_usd` |
  | --- | --- | --- |
  | as seeded | `111.20` | `341.04` |
  | `care_policies` table removed entirely | `111.20` | **`341.04` — identical** |
  | `club_memberships` table removed | `115.65` | `328.09` (both move) |
  | the seeded care policy set to `in_force` | `111.20` | `313.24` (moves) |

  The contrast is the finding: club evidence moves both figures; care evidence moves neither.
  `initial_state.care_policies.7ef9d876-935d-4ca4-8c6d-6fb0f4b98794.status` = `"expired"`.
- **Demonstrated consequence.** Task 0 still has no factor whose tier is decided by another
  **difficulty's** seeded records. The score cannot distinguish an agent that queried `find_care_policies`
  from one that never looked at the `care` product at all; the read is unobservable to scoring. This is
  the shape revision 1's O-4 asked the rework to remedy, and the remedy does not reach it. The task's
  remaining `cross_difficulty` factors, `member_relief` and `service_element`, both read `club` — a
  category with no difficulty of its own in `blueprint.yaml`, which is precisely what O-4 recorded.
- **The author's own account concedes the ablation.** `tasks/0.json:design_rationale`: *"It is the
  cross-difficulty evidence the goodwill element rests on: no policy of hers is in force over the October
  rental period, which is the condition the goodwill ladder tests. **Remove it and the tier still holds
  but the evidence the agent must read to establish it is gone.**"* The second clause is a claim about
  what a diligent agent ought to read, not about the tier resting on seeded records, and nothing in the
  scored solution can observe it.
- **What is genuinely gained, stated fairly.** The expired policy is a real **near-miss**: an agent that
  reads `find_care_policies`, sees a policy and skips the status filter takes the fall-through tier and
  scores `313.24` instead of `341.04`. That has value. But a near-miss and load-bearing cross-difficulty
  evidence are separate requirements, and a near-miss cannot stand in for the one that is missing.
- **The hinge a reviewer may take differently.** Under the charter's own definition of the field —
  `check_extended.py` treats `cross_difficulty` as "another **category's** holding or ledger" — task 0
  satisfied the requirement in round 1 already, through `club`, and this finding is then an unclosed
  observation rather than a red. Under the skill's wording ("another **difficulty's** records", and the
  closing requirement that the rows a cross-difficulty factor reads be seeded and bear on the tier), it is
  a red. The demonstration above is the same either way; the severity turns on that reading, and it is
  recorded so a reviewer can weigh it rather than take the label on trust.
- **Affected artifact.** `drive.extended.yaml` §
  `extended_policies[1] drive_ext_cancellation_refund.factors[supplier_message_goodwill]` and
  `.compute.protection_in_force`; `tasks/0.json:initial_state.care_policies` (the `status` value);
  `tasks/0.json:evaluation_criteria[5]` (the `find_care_policies` read node).
- **Relation to previous revisions.** New in revision 2. It arises from the attempt to close revision 1's
  O-4 and did not exist in round 1, where task 0 carried no `care` factor at all.

---

**R2-O-1 — observation. "over the rental period" is stated in the rule and implemented nowhere.**
Recorded in § `revision_2 / rule_compute_equivalence` above. `drive_ext_cancellation_refund`'s goodwill
tiers and its `cross_category[care].note` both carry the qualifier; `protection_in_force` is a bare
`EXISTS('care', status='in_force')`. Inert on both worlds (neither renter holds an in-force policy whose
period could differ from its status). It is the same species as the F-4 gap this rework closed, reappearing
one clause further on.

**R2-O-2 — observation. Two residual divergences in the sentence that closed F-3.** The coordinator asked
this round to test whether the new free-cancellation sentence diverges from base anywhere. It does, twice,
and neither divergence is demonstrable on either world:

1. *Clock basis.* Base: *"A cancellation is handled free of charge only when **frozen time** is not after
   the moment the supplier confirmed the renter's booking plus the free-cancellation term …"* New
   sentence: *"a rental **given up** inside that term has nothing withheld."* Base tests the handling
   moment; the extended tests the moment the rental was given up. They coincide whenever the cancellation
   is performed in the conversation, and part company for a rental cancelled earlier and handled later —
   which is exactly task 0's shape (`cancelled_at` 2026-09-23, `frozen_time` 2026-09-24). On task 0 both
   readings fall outside the term (`free_cancellation_hours_before_pickup: 0` for `Pay Now Standard
   Rate`, so the term closes at `confirmed_at`), so no second number arises. Task 1 has no cancellation.
2. *A dropped limb.* Base (c) is *"Inside the free-cancellation term nothing is withheld on any rate class
   **and the prepayment is returned in full**."* The charge policy now states the first limb; the refund
   policy still says nothing about the free window, and on a free-window cancellation its formula would
   return the settlement less the retained service element — not "in full" on any tier where the fee is
   retained. Inert on both worlds for the same reason as (1).

Because neither can be shown to produce a second figure on a world this difficulty presents, neither is
a red light. They are recorded because the reasoning that closed F-3 — "the new sentence agrees with base
and so needs no `overwrite`" — is exactly true of the anchor and the unit, and not quite true of the clock
basis or of base's second limb.

**R2-O-3 — observation. The 0-4 fix is true of the world but collides with the account definition.** The
new sentence *"The money settled in advance on a rental is the total of the advance payments taken on it,
and it carries what was paid for the rental days, what was paid for any optional items bought in advance
and the rate class's agency service fee"* is **arithmetically true of task 0's seed**, and that is worth
recording: the rate alone for six days on `Pay Now Standard Rate` at `DENC1` is four weekdays at `46.75`
plus two weekend days at `39.00` = `265.00`, and `265.00 + 161.88` (child seat + satnav) `+ 12.95`
(agency service fee) = **`439.83`**, the prepayment exactly. So `charge_basis = 439.83 − 161.88 − 12.95 =
265.00` really is "the rate alone", and revision 1's observation 0-4 — that the formula subtracted items
from a base that never contained them — is answered on its merits.

What the sentence collides with is `accounts`: `drive.extended.yaml:accounts[rental_charges].meaning`
says *"rental days, **prepayments**, **optional items**, statutory charges, fuel, recharges and penalties
**credit the account**"* — prepayments and optional items as separate credits. The seed follows the
account, not the new sentence: `charges_total_usd` is `601.71` = `439.83 + 83.94 + 77.94`, so the `161.88`
is counted once inside the prepayment and once again as its own lines, and the renter's net charged total
is `161.88` more than the money actually taken. No second scored number follows — the rule's first clause
("the total of the advance payments taken on it") pins `settled_in_advance_total` to the
`drive_prepay_charge` family and therefore to `439.83`, and both computations read only that — so this is
an observation, not a red. The incoherence revision 1 recorded has moved from the formula into the
relation between the new sentence and the account, rather than being removed.

**R2-O-4 — observation, and a correction to this audit's own revision 1.** Two claims in revision 1 §
`rule_compute_equivalence` were overstated; both are set out in full in § `revision_2 /
rule_compute_equivalence` above (three unnamed arithmetic intermediates carry no `compute_basis` entry in
`drive_ext_cancellation_charge`; one `compute_basis` entry in `drive_ext_cancellation_refund` is a stitch
of two non-adjacent — but individually verbatim — rule fragments). Both were equally true of the round-1
charter, so neither is a regression and neither is a defect the rework introduced. They are recorded here
because concealing a weak step in this audit's own proof would be worse than the weakness.

**Items answered with no change — the argument assessed, not the assertion accepted.**

- **0-3** (the refund baseline collapses to `0.00` on task 0's world). Re-verified: the baseline is
  unchanged, still self-sufficient, still yields a **definite** number, and still differs from gold
  (`0.00` vs `341.04`). It therefore satisfies the requirement as the skill words it, and revision 1
  recorded it as an observation rather than a red for exactly that reason. Declining to change it is a
  legitimate outcome; the observation stands unremedied by choice, and revision 1's note that
  `withholding_measure`'s fall-through cancels the whole settlement is still the accurate description.
- **O-6 / 1-6** (`drive_ext_recharge_dispute.subject: [drive_damage_charge]` does not name
  `drive_damage_reviews`, the table its tool writes). Re-verified unchanged. The underlying fact remains
  true and remains without consequence: `blueprint.yaml`'s claimed `event_types` for this difficulty carry
  no review-creation event the subject could name instead, so there is no available correct value, and no
  scored value or eligibility turns on it. Observation stands.
- **O-5** (`drive_damage_and_recharges`'s "until the review decides it" states an order that grounds no
  declared edge). Re-verified unchanged. It still orders a dispute against a review decision that no
  policy of this difficulty writes, and `drive_ext_recharge_dispute` still carries its own prerequisite
  sentence, so the skill's own rule keeps it an observation rather than a red.
- **O-7** (`replay_tasks.py`'s non-idempotent write-back). Confirmed referred outward by the coordinator;
  outside this audit's write domain and outside the four relationships. No action here.

### revision_2 / status of every revision-1 item

| item | revision 1 | revision 2 verdict | basis |
| --- | --- | --- | --- |
| **F-1 / 0-1** | `SOURCE-POLICY RED` | **CLOSED** | override declared verbatim against the named base clause; second figure no longer defensible |
| **F-2 / 1-1** | `SOURCE-POLICY RED` | **CLOSED** | override declared verbatim, covering both the 1.5× multiple and the new tier |
| **F-3 / 0-2** | `SOURCE-POLICY RED` | **CLOSED** as a red; residual observation | new rule sentence names and rejects the backwards-from-collection reading; the `parameter_schema` gloss is still literally false but can no longer ground a defensible second reading. Divergence hunt: **R2-O-2** |
| **F-4 / 0-5** | observation | **CLOSED** | compute `== 1` matches the rule's "one message"; new smaller gap **R2-O-1** |
| **F-5 / 0-6** | observation | **CLOSED** | two declared overwrites; the un-superseded limb correctly left inherited |
| **F-6 / 1-3** | observation | **CLOSED** | declared overwrite retires the "in full where it was not" limb |
| **O-1** | observation | **CLOSED** | tie-break sentence in all four rules |
| **O-2 / 1-4** | observation | **CLOSED** | "filed on their travel protection policies" now in the rule and the baseline |
| **O-3 / 1-5** | observation | **CLOSED** | tier replaced with a reachable, base-consonant one; reachability argued from the absence of any per-rental uniqueness constraint |
| **O-4** | observation | **NOT CLOSED → R2-RED-1** | ablation: removing task 0's whole `care_policies` table changes no scored value |
| **O-5** | observation | unchanged, argued — **stands** | fact re-verified; still no demonstrable consequence |
| **O-6 / 1-6** | observation | unchanged, argued — **stands** | fact re-verified; no correct alternative value exists |
| **O-7** | observation | referred outward | harness owner |
| **0-3** | observation | unchanged, argued — **stands** | baseline still definite and ≠ gold |
| **0-4** | observation | **CLOSED** on its merits; **R2-O-3** on what the fix collides with | `265.00 + 161.88 + 12.95 = 439.83` verified |
| **1-2** | observation | **CLOSED** | persona re-dated; see `1.md` § revision_2 |

## closing_checklist (revision 2)

**This difficulty still does not close out**, on one finding rather than three.

Re-verified item by item on the reworked form: the three audit files still correspond one-to-one with the
tasks and revision 1 is preserved intact above; all four extended policies are covered with pairwise
disjoint scopes; task tools and GT are closed (`clos = init` at 11/11 and 28/28, `match: True`,
`db_closure_matches_initial_state: true` on both); the four uuid8s are unchanged and carried forward by
hash; each tree still has one prerequisite problem, one `value_input` edge, one `owner=user` write, and no
cycle; all four baselines remain self-sufficient, verbatim-grounded and different from gold
(`351.86`, `0.00`, `807.50`, `541.80` — unchanged); all 21 factors still bear weight, with every
sensitivity figure re-computed and identical to revision 1; and the gates are green on the final form.

**Scored values, independently re-derived this round with the harness's own evaluator — all four
unchanged, confirming the reworker's claim:**

| task | parameter | revision 1 | revision 2 | edge-skip figure |
| --- | --- | --- | --- | --- |
| 0 | `cancellation_charge_usd` | `111.20` | `111.20` | — |
| 0 | `refund_amount_usd` | `341.04` | `341.04` | `424.44` (unchanged) |
| 1 | `damage_recharge_usd` | `903.00` | `903.00` | — |
| 1 | `disputed_amount_usd` | `464.05` | `464.05` | `140.85` (unchanged) |

All 21 factor-sensitivity figures and both whole-baseline figures per task also re-computed identically.
**Nothing regressed.**

| relationship | task 0 | task 1 |
| --- | --- | --- |
| Policy self-consistency | **PASS** (was RED ×2) | **PASS** (was RED) |
| The problem tree holds | PASS | PASS |
| Factors bear weight | **`SOURCE-FACTOR RED`** (R2-RED-1) | PASS |
| Policy ↔ task unique solution | PASS | PASS |

**Task 1 passes all four relationships.** Task 0 fails one: every round-1 red against it is genuinely
closed, and the single outstanding item is the one the rework introduced while trying to close an
observation. No artifact was edited by this audit, and no fix is designed or arranged.

---

# revision_3 — re-audit of the reworked form (charter-global)

*Revisions 1 and 2 above are left exactly as written.*

## charter_global_frozen (revision 3)

- auditor: the same independent source-layer auditor. **Not blind**, and not presented as blind — this
  round verifies closure, regression and novelty.
- re-audit time: 2026-09-16.

| artifact | revision 2 | revision 3 | moved? |
| --- | --- | --- | --- |
| `drive.extended.yaml` | `e8d856f196df35e0…29dc12f7` | `5387f5f4d5f41f92…0fd04508` | **CHANGED** |
| `task_tools.py` | `b28e8776…` | `b28e8776…` | unchanged since round 1 |
| masked view `0.json` | `2d35dd8a…` | `e9c087ebc2c5ad68…8ca0ec35` | **CHANGED** |
| masked view `1.json` | `3337dee9…` | `3337dee9c723bb3a…4915815a` | **unchanged** |

All four verified locally by `sha256sum` against the brief; all four agree. `action_binding_and_uuids`
is again **carried forward by reference** on the unchanged `task_tools.py` hash. Every other
charter-global section is re-derived, because the charter moved. **Task 1's derivation is re-derived
rather than carried forward** despite its world being byte-identical, for the reason the brief gives: its
figures rest on rules that were edited.

Gates: supplied verbatim by the coordinator, all seven green. `0.json` now closes at `clos = init = 12`
(was 11) and `brch` 28 (was 27), consistent with the added `care_policies` row and the three new
bindings. Cited as the entry qualification only — as revision 2 recorded, the gate was green on the
inert-limb question in both directions, so it is not evidence on the RED.

### revision_3 / R2-RED-1 — the ablation, run here

Revision 2's red was that task 0's declared `cross_difficulty: care` limb was inert: the binding was
`EXISTS('care', status='in_force')`, the seeded policy was `expired`, and the read returned the same
`False` an empty `care` table returns. The reworker's diagnosis — a negative test inert in both
directions — is itself checkable, and it checks out: `EXISTS` on a status no seeded row carried could
only ever return `False`, so no seeding of that table could have moved it.

The factor is now built on a **positive** test read from the policy's own dates:

```
cover_starts_by_days     = DAYS(CFIELD('care','trip_start_date', status='issued') or F('dropoff_at'), F('pickup_at'))
cover_runs_to_days       = DAYS(F('dropoff_at'), CFIELD('care','trip_end_date', status='issued') or F('pickup_at'))
protection_covers_rental = cover_starts_by_days >= 0 and cover_runs_to_days >= 0
```

**The ablation that settles it is the one run here**, with `check_compute.py`'s own evaluator, on the
reworked world, with the prerequisite write replayed between the steps in every row:

| world | `refund_amount_usd` | moves? |
| --- | --- | --- |
| as seeded | **`341.04`** | — |
| `care_policies` table removed entirely | `313.24` | **✓** |
| `care_policies` present but empty | `313.24` | **✓** |
| only the expired near-miss remains (issued policy deleted) | `313.24` | **✓** |
| the issued policy's status set to `quoted` | `313.24` | **✓** |
| its `trip_start_date` moved to `2026-10-09` (after collection) | `313.24` | **✓** |
| its `trip_end_date` moved to `2026-10-11` (before booked return) | `313.24` | **✓** |
| only the issued policy remains (expired near-miss deleted) | `341.04` | — (correct: a near-miss must be inert) |
| `club_memberships` removed | `328.09` | **✓** club still load-bearing |

**Seven perturbations of the `care` evidence, six of which move the scored payout** — the status, each
of the two dates, and the row's existence each carry the tier independently. The reworker reported four;
there are more, and the two extra ones (the empty-table case and the `quoted`-status case) are the ones
that distinguish a genuine positive read from another inert test. **R2-RED-1 is genuinely closed.**

### revision_3 / the `or` fallbacks, tested rather than reasoned about

The coordinator asked for satisfaction that each fallback **fails** rather than passing or raising. Both
fallbacks substitute the wrong end of the rental — `dropoff_at` where a trip start is wanted, `pickup_at`
where a trip end is wanted — so each comparison is evaluated against a span that runs backwards. Traced
values, all four no-match worlds:

| world | `cover_starts_by_days` | `cover_runs_to_days` | `protection_covers_rental` | raised? |
| --- | --- | --- | --- | --- |
| as seeded (trip `2026-10-05`→`2026-10-15`, rental `10-07`→`10-13`) | `2` | `2` | `True` | no |
| no `care` table at all | `-6` | `-6` | `False` | **no** |
| `care` table present but empty | `-6` | `-6` | `False` | **no** |
| only the expired near-miss | `-6` | `-6` | `False` | **no** |
| issued policy with a blank `trip_start_date` | `-6` | `2` | `False` | **no** |

`-6` is exactly the rental's own span reversed (`DAYS('2026-10-13','2026-10-07')`). Every no-match world
fails the `>= 0` test, none passes it, and none raises — including the blank-field case, where `CFIELD`
returns `""` and the `or` still falls through because an empty string is falsy. The fallback is
constructed to fail, not merely to avoid an exception.

### revision_3 / the seeded `issued` status is charter-correct

Checked against the `care` charter rather than taken on trust.
`blueprint/products/care.yaml:lifecycle.transitions` gives `quoted -> issued` — *"The premium is paid and
the certificate of insurance is issued"* — and `issued -> in_force` — *"The insured journey begins and
every benefit comes into force."* The seeded policy declares a trip starting `2026-10-05`; `frozen_time`
is `2026-09-24`, so the journey has **not** begun and the policy must stand at `issued` and not at
`in_force`. `care_coverage_term` confirms the status is not vacuous cover — *"Cancellation cover runs from
the moment the certificate is issued"* — so an issued-but-not-incepted policy genuinely answers
something, which is what the rule's own rationale clause leans on. The status was not chosen to make the
test pass; it is the only status the `care` charter permits this policy at this moment. The contrast is
task 1, whose `TripGuard Plus` is seeded `in_force` with a trip running `2026-08-08`→`2026-09-02` around
a `frozen_time` of `2026-08-24` — also the only charter-correct status there. Both tasks are consistent
with the same lifecycle.

### revision_3 / R2-O-4 — the sentence move, and what it might have broken

Both parts were acted on. Re-run mechanically across all four policies:

| policy | bindings | bindings with no `compute_basis` entry | entries not verbatim in their own rule |
| --- | --- | --- | --- |
| `drive_ext_cancellation_charge` | 15 | **0** (was 3) | **0** |
| `drive_ext_cancellation_refund` | 22 | **0** | **0** (was 1) |
| `drive_ext_damage_recharge` | 22 | **0** | **0** |
| `drive_ext_recharge_dispute` | 18 | **0** | **0** |

`share_amount`, `after_relief` and `after_value` now carry entries, and
`drive_ext_cancellation_refund.compute_basis.result` is now a contiguous quotation —
`"and it is never less than nothing and never more than the money settled in advance. The figure is
rounded to two decimal places once, on the final figure."` — verbatim in the rule, because the rounding
sentence was moved up to sit immediately after the formula sentence.

**The collateral check the coordinator asked for.** Moving a sentence inside a rule can silently break
any other quotation that spans or abuts it, and three kinds of quotation do:

- **All seven `overwrite` entries** re-tested — each `superseded_clause` verbatim in the **named base
  policy's** rule and each `replaced_by` verbatim in the **extended policy's own** rule: **7 for 7**. The
  F-5 entry the reworker singled out (`replaced_by: "it is never less than nothing and never more than
  the money settled in advance"`) still matches, and so does its companion against
  `Each payout is raised against the original ledger line it reverses…`.
- **All four `baseline.rule` blocks** re-tested sentence by sentence against their policy's rule:
  8 / 7 / 11 / 8 sentences, **zero misses**. The refund baseline's closing sentence is the one that moved,
  and it is still present.
- **Every `compute_basis` entry**, as tabulated above: zero non-verbatim.

Nothing broke.

### revision_3 / R2-O-3 — the sentence about what a payment covers

Revision 2's observation was that the sentence asserted the prepayment "carries what was paid for any
optional items", while `accounts[rental_charges].meaning` lists *"rental days, **prepayments**, **optional
items** … credit the account"* — i.e. as separate credits — and the seed followed the account. The
sentence now reads:

> *"The money settled in advance on a rental is the total of the advance payments taken on it; **each such
> payment is taken to cover** the rental days booked, the optional items bought in advance and the rate
> class's agency service fee, **and the ledger records both the payment and the separate lines for the
> items that payment covers**."*

The added clause states the recording convention the account prescribes instead of implying one that
contradicted it, so the two passages no longer reach different conclusions about the same quantity. The
first clause still pins `settled_in_advance_total` to the `drive_prepay_charge` family, and the coverage
claim remains arithmetically true of task 0's seed (`265.00 + 161.88 + 12.95 = 439.83`, verified again
this round). **Closed as the contradiction it was** — rewritten to agree with the account rather than
merely reworded.

*Residual, recorded and not red-lighted:* the account still counts the `161.88` twice against cash, so
`charges_total_usd` (`601.71`) exceeds the money actually taken (`439.83`). No binding of any of the four
policies reads `charges_total_usd` — verified by scanning all 77 compute expressions — so no scored value
depends on it, and none of the four relationships reaches it. It is a world-modelling artifact of the
two-line recording the charter now states on purpose.

### revision_3 / R2-O-1, R2-O-2 — the remaining round-2 observations

- **R2-O-1 — CLOSED.** The unimplemented qualifier is gone. The rule no longer says "in force over the
  rental period"; it says *"stands issued over a declared trip that begins no later than the collection
  moment and ends no earlier than the booked return"*, and each limb is now a binding: `status='issued'`,
  `DAYS(trip_start, pickup_at) >= 0`, `DAYS(dropoff_at, trip_end) >= 0`. Both "no later than" and "no
  earlier than" are inclusive in the rule and inclusive in the compute (`>= 0` admits equality). Rule and
  compute say the same thing, and the `cross_category[care].note` and the factor's `ladder` carry the same
  wording. The check-2 gap that revision 2 recorded is removed rather than moved on.
- **R2-O-2 limb 1 (clock basis) — CLOSED.** The charge policy's sentence now reads *"… **where frozen
  time is not after** that confirmation moment plus the term nothing is withheld, and the charge worked
  out here is the one that arises **where frozen time is past it**."* That is base `drive_cancellation`'s
  own clock (`temporal_basis.clock: frozen_time`), not the moment the rental was given up. The divergence
  is removed at its source.
- **R2-O-2 limb 2 (base's dropped "returned in full" limb) — CLOSED, and closed the right way.** The
  refund policy now states the free-window case for itself — *"Where a rental was given up while frozen
  time was not after the moment the supplier confirmed it plus the free-cancellation term of the rate
  class booked, its ledger carries no charge for being given up, so nothing is taken off on that account
  and the money settled in advance is returned apart from the service element the desk retains."* That
  still differs from base's *"the prepayment is returned in full"*, and **a fourth `overwrite` entry now
  declares exactly that clause superseded**, verbatim on both sides. The divergence was not argued away;
  it was declared. `drive_ext_cancellation_refund.overwrite` now carries four entries and the charter
  carries seven.

### revision_3 / regression sweep

Everything revisions 1 and 2 established was re-tested on the moved charter:

| item | status |
| --- | --- |
| base section verbatim identical to `blueprint/products/drive.yaml` | ✓ zero differing keys |
| tie-break sentence (closed O-1) present in all four rules | ✓ 4/4 |
| O-2 wording (*"filed on their travel protection policies"*) still in the recharge rule | ✓ |
| O-3 tier (*"more than one damage assessment stands approved …"*) still present and implemented | ✓ |
| both prerequisite edges: `policy_source` verbatim in the blocked rule, `state` form, no `fallback_reason`, gate a real binding, not restated in the depended-on rule | ✓ both |
| acyclic, two disjoint single edges | ✓ |
| factor counts per policy (5/5/6/5; ≥2 `parameter`, ≥1 `method`) | ✓ unchanged |
| `cross_difficulty` declarations | club / club+care / club+care / care — unchanged |
| all four baselines self-sufficient, verbatim-grounded, ≠ gold | ✓ `351.86`, `0.00`, `807.50`, `541.80` |
| all 21 factor sensitivities | ✓ **identical to revisions 1 and 2, figure for figure** |
| all four scored values, both edge-skip figures | ✓ identical |

The one ladder that changed substance improved: `supplier_message_goodwill`'s **second** tier is now a
conjunction over distinct records too (*"one message"* + the care cover test), where in revision 2 it was
a single condition. The factor is multi-source on both non-fallthrough tiers.

### revision_3 / findings

**R3-O-1 — observation. `CFIELD` resolves to one holding, and the factor now depends on which.**
`CFIELD('care', field, status='issued')` returns `hs[0]` — the first matching holding in dictionary order
— so with two `issued` `care` policies for one customer the dates read would be arbitrary. Task 0 seeds
exactly one `issued` policy (the other is `expired`), so the read is unambiguous here and no task of this
difficulty presents the ambiguous world. Recorded as latent: the round-2 defect was a cross-category read
that could not discriminate, and this is the neighbouring shape — a read that discriminates but whose
subject is chosen by dictionary order rather than by the rule.

**R3-O-2 — observation, carried forward and still open.** `parameter_schema.free_cancellation_hours_before_pickup`
is **unchanged** and still reads *"Hours before collection by which a cancellation carries no charge."* —
still literally false about the parameter its own rules consume. Revision 2 recorded this as the residual
of F-3's closure and the reworker did not claim it closed. It produces no second defensible number, now
less than ever: both extended rules state the confirmation anchor outright, one of them naming and
rejecting the backwards-from-collection reading. Observation, not a red, and it will be rendered into the
KB alongside the rules that contradict it.

**R3-O-3 — note on this audit's own method, not on the artifacts.** A containment test run this round
reports that 13 of the ladders' `when` strings are not verbatim substrings of their rule. Inspection shows
this is the test being stricter than the requirement: a `when` restates its rule condition with the
subject spelled out (*"fourteen or more whole days of notice were given **between the rental being given
up and the scheduled collection**"* against the rule's *"Where fourteen or more whole days of notice were
given the share is twenty per cent"*, whose measurement the preceding sentence defines). Every tier's
condition and its value are stated in the rule, which is what checks 2 and `factor_ladders` require.
Recorded so the mechanical output is not mistaken for a finding in a later round.

**Items unchanged and argued again — re-verified, not re-accepted on assertion.**

- **0-3** (the refund baseline collapses to `0.00` on task 0's world): re-computed this round — still
  `0.00`, still definite, still self-sufficient, every sentence still verbatim in the rule, still
  different from gold. Meets the requirement as the skill words it; the observation stands unremedied by
  choice, as it has since revision 1.
- **O-5** (`drive_damage_and_recharges`'s *"until the review decides it"*): the base section is verbatim
  identical to the blueprint, so the sentence is unchanged. It still orders a dispute against a review
  decision no policy of this difficulty writes, and the dispute policy still carries its own prerequisite
  sentence, so the skill's own rule keeps it an observation.
- **O-6 / 1-6** (`drive_ext_recharge_dispute.subject: [drive_damage_charge]`): re-verified unchanged. No
  review-creation event exists in this difficulty's claimed `event_types` for the subject to name instead,
  so there is still no correct alternative value, and no scored value or eligibility turns on it.
- **O-7** (`replay_tasks.py`'s non-idempotent write-back): referred outward, confirmed logged. This round
  the gates were run by the coordinator and not re-run here, so no write-back occurred and the charter and
  task-file hashes stand exactly as the brief states them.

**No new defect was found.** Every charter change this round was tested against both worlds: the seven
overwrite declarations, the three new bindings, the two rewritten sentences, the moved sentence and the
three added `compute_basis` entries. None introduces a conflict, an unimplemented promise, an
undiscoverable dependency or an inert factor, and none moves a scored value.

### revision_3 / status of every open item

| item | revision 2 | revision 3 verdict | basis |
| --- | --- | --- | --- |
| **R2-RED-1 / 0-8** | `SOURCE-FACTOR RED` | **CLOSED** | seven ablations run here; six move the payout; the tier now rests on the seeded `care` row's status and both of its dates |
| **R2-O-1 / 0-9** | observation | **CLOSED** | "over the rental period" replaced by two implemented date conditions |
| **R2-O-2** limb 1 | observation | **CLOSED** | charge rule now keys on `frozen time`, matching base's `temporal_basis` |
| **R2-O-2** limb 2 | observation | **CLOSED** | refund rule states the free-window case and a fourth `overwrite` declares base's *"the prepayment is returned in full"* superseded |
| **R2-O-3** | observation | **CLOSED**; residual noted | sentence rewritten to endorse the account's two-line recording; no binding reads `charges_total_usd` |
| **R2-O-4** | observation | **CLOSED**, both parts | 0 missing and 0 non-verbatim `compute_basis` entries across all four policies; the move broke none of the 7 overwrites or 4 baselines |
| **F-3 residual (gloss)** | observation | open — **R3-O-2** | `parameter_schema` unchanged; no second number derivable |
| **0-3**, **O-5**, **O-6** | observations | unchanged, argued — **stand** | facts re-verified; still no demonstrable consequence |
| **O-7** | observation | referred outward | harness owner |
| everything closed in revision 2 | closed | **no regression** | structural sweep and all 21 sensitivities identical |

## closing_checklist (revision 3)

**This difficulty closes out.** All four relationships hold in both tasks.

| item | status |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks; `_difficulty.md` alongside | ✓ |
| old revisions traceable | ✓ revisions 1, 2 and 3 appended in order, none rewritten |
| every comparison section carries a PASS | ✓ both tasks, all four relationships |
| extended policies fully covered; task scopes pairwise disjoint, each spanning its whole tree | ✓ {charge, refund} ∩ {recharge, dispute} = ∅ |
| task tools and GT closed | ✓ `clos = init` at 12/12 and 28/28, `match: True`, `db_closure_matches_initial_state: true` |
| each task tool an independently generated, frozen uuid8 | ✓ `358c6472`, `344e0f66`, `2d59c35f`, `65c619e1` — `task_tools.py` unchanged since round 1, carried forward on its hash |
| every tree: 1–3 prerequisite problems, ≥ `max(n−1,1)` `value_input` edges, ≥1 `owner=user` write, no cycle | ✓ one prerequisite problem, one `value_input` edge, one customer write each |
| difficulty-wide `prerequisite` graph acyclic | ✓ two disjoint single edges |
| every computation: self-sufficient baseline, 4–6 factors (2 `parameter`, 1 `method`), ladders ≥3 tiers stated in the rule | ✓ 5/5/6/5 |
| per task ≥1 multi-source and ≥1 cross-difficulty factor | ✓ task 0 now reads `care` load-bearingly as well as `club`; task 1 reads `care` in both computations |
| every factor bears weight against an honest baseline; baseline alone definite and ≠ gold | ✓ all 21, re-computed this round |
| instantiation-stage gates re-run on the final form | ✓ by the coordinator, all seven green |

**Scored values across all three rounds — stable throughout:**

| task | parameter | rev 1 | rev 2 | rev 3 |
| --- | --- | --- | --- | --- |
| 0 | `cancellation_charge_usd` | `111.20` | `111.20` | **`111.20`** |
| 0 | `refund_amount_usd` | `341.04` | `341.04` | **`341.04`** |
| 1 | `damage_recharge_usd` | `903.00` | `903.00` | **`903.00`** |
| 1 | `disputed_amount_usd` | `464.05` | `464.05` | **`464.05`** |

Edge-skip figures (`424.44`, `140.85`), whole-baseline figures (`351.86`, `0.00`, `807.50`, `541.80`) and
all 21 factor sensitivities are likewise unchanged across all three rounds.

| relationship | task 0 | task 1 |
| --- | --- | --- |
| Policy self-consistency | **PASS** | **PASS** |
| The problem tree holds | **PASS** | **PASS** |
| Factors bear weight | **PASS** (was `SOURCE-FACTOR RED`) | **PASS** |
| Policy ↔ task unique solution | **PASS** | **PASS** |

Four REDs were raised across three rounds — F-1, F-2, F-3 in round 1, R2-RED-1 in round 2 — and all four
are now closed on their merits, each verified by re-derivation or ablation rather than by reading the
reworker's account. Six observations remain open by argued choice or by referral (R3-O-2, 0-3, O-5, O-6,
O-7, and the R2-O-3 residual); none is demonstrable against either world and none bears on the four
relationships. No artifact was edited by this audit at any round, and no fix was designed or arranged.

---

# revision_4 — re-audit of the regenerated form (charter-global)

**Why this revision re-derives rather than carries forward.** This round's shared inputs both moved against the
round that produced revision 1 (freeze time 2026-09-16):

| input | revision 1 | revision 2 |
| --- | --- | --- |
| `drive.extended.yaml` sha256/16 | `4876de238d2bf457` (revision 1; revisions 2-3 re-audited reworked forms of it) | `ea0f49895303d4ac` |
| `task_tools.py` sha256/16 | `b28e8776f3789a0f` | `6180432be1a7d058` |

Because both changed, every charter-global and per-task section below was re-derived in full rather than carried
forward by reference, per this audit's re-derivation rule.

**Independence from revisions 1-3.** The text of revisions 1, 2 and 3 above is left untouched. Their conclusions were **not read**
until after both tasks' `source_derivation_frozen` sections of this revision were on disk and the GT had been
revealed — the prior revision's files had been removed from the working tree before this round began and were
recovered from git only at the close, so no earlier blind answer, verdict or figure could enter this round's
derivation. No sentence of any earlier revision has been rewritten to accommodate this round's GT. Because the
artifacts were regenerated rather than patched, this round's findings are numbered independently (D-*, T0-*, T1-*)
and are not continuations of the earlier rounds' item numbers.

### charter_global_frozen

- freeze time: 2026-09-17 (session clock), written **before any task's GT was revealed**.
- auditor: independent source-layer auditor (not the instantiating agent).
- freeze hashes (sha256/16):
  - `env/env_0000_online_travel_agency/tasks/car_rental_desk/drive.extended.yaml` = `ea0f49895303d4ac`
  - `env/env_0000_online_travel_agency/tasks/car_rental_desk/task_tools.py` = `6180432be1a7d058`
- fields permitted while this section was written: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`,
  `blueprint/products/*.yaml`, `blueprint/share_tools.py`, the whole of `drive.extended.yaml`, the whole of
  `task_tools.py`, and each task's `frozen_time` / `user_scenario` / `initial_state` through the masked views
  (`0.masked.json` sha256/16 `a168f043977092c4`, `1.masked.json` sha256/16 `a95fac174ab4ebe1`).
- fields explicitly masked and not read while this section was written: `evaluation_criteria`, `computations`,
  `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`,
  `db_closure`, `db_closure_matches_initial_state`. No `contamination_disclosure` — nothing derived from a
  revealed GT was written into this section.
- entry conditions (Step 0): the brief carried the instantiation-stage gate snapshot with its actual output
  lines (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK)
  and the two masked-view hashes, which reproduce on disk. Entry conditions are **complete**. `check_traceability.py`
  is correctly absent at this stage. A machine green light is the qualification to enter this audit, not a proof.

#### policy_conflict_scan

The base section of `drive.extended.yaml` is **byte-identical** to `blueprint/products/drive.yaml` (verified by
key-by-key canonical-JSON diff: `DIFFS: []`, with `extended_policies` the only added top-level key). The base copy
has not been rewritten.

Four extended policies, claiming four disjoint subjects and four disjoint target tools:

| policy | trigger | subject | computes | target_tool | owner |
| --- | --- | --- | --- | --- | --- |
| `drive_ext_additional_driver_charge` | state_due | drive_extras_charge | additional_driver_charge_usd | charge_additional_driver_79b211ed | agent |
| `drive_ext_release_charge` | on_request | drive_cancellation_charge | release_charge_usd | release_rental_booking_4b632ce9 | user |
| `drive_ext_included_mileage_grant` | state_due | drive_mileage_grant | miles_granted | grant_included_mileage_444a2a24 | agent |
| `drive_ext_return_settlement` | on_request | drive_return, drive_extras_charge | excess_mileage_charge_usd | close_rental_return_9b1c513c | user |

Overlapping subjects: `drive_extras_charge` is named by both `drive_ext_additional_driver_charge` and
`drive_ext_return_settlement`. They do **not** collide: the first computes `additional_driver_charge_usd` and writes
`charge_category="additional_driver"`; the second computes `excess_mileage_charge_usd` and writes
`charge_category="excess_mileage"`. Different quantities, different ledger categories, different trigger
(`state_due` vs `on_request`), and they live in different tasks' scopes. No conflict.

Time anchors: `drive_ext_release_charge` anchors on `NOW` against `drive_rentals.pickup_at`;
`drive_ext_return_settlement` anchors on `drive_rentals.dropoff_at` and `drive_rentals.pickup_at` /
`picked_up_at`; `drive_ext_additional_driver_charge` anchors on `booked_date` -> `pickup_at`. No two policies
measure the same span from different anchors.

Cross-category read boundaries: `air` (release charge, branch), `club` (additional driver — history; release
charge — branch; return settlement — history), `bundle` (mileage grant — branch). Each is declared in the owning
policy's `cross_category` block with `reads` and a `note`. No policy reads a category it does not declare.

Terminal states: `release_rental_booking_4b632ce9` moves `confirmed -> cancelled`;
`close_rental_return_9b1c513c` moves `picked_up -> returned`. Both are declared transitions in
`lifecycle.transitions`. The two agent tools mutate no status. No two policies write the same status field.

Task scopes: task 0 claims `{drive_ext_release_charge (root), drive_ext_additional_driver_charge (prerequisite)}`;
task 1 claims `{drive_ext_return_settlement (root), drive_ext_included_mileage_grant (prerequisite)}`. Scopes span
whole problem trees, are **pairwise disjoint** and **jointly complete** over the four extended policies.

#### rule_compute_equivalence

Check 2 was run mechanically and then read back sentence by sentence. Result for all four policies:

- every binding in `compute` has a `compute_basis` entry, and every `compute_basis` key is a real binding
  (no orphans in either direction);
- every `compute_basis` value is a **verbatim substring** of that policy's own `rule` after whitespace
  normalisation (0 failures across all four policies);
- every `baseline.rule` sentence is verbatim inside the policy `rule`;
- every `factors[].decides` names a real binding;
- every factor tier is stated in the `rule` with both its condition and its value/method — no tier lives only in
  `compute`, and no branch of a `decides` binding is missing from the rule. The ladders' `method:` strings are
  subject-reworded paraphrases of the rule sentence they name (e.g. ladder `the fee is charged for the first
  fourteen days and for no day beyond them` for rule `an agreement booking fourteen or more rental days is charged
  for the first fourteen days and for no day beyond them`); the tier itself is present in the rule in full, so
  this is a wording difference and not a missing tier;
- rounding is stated once per policy and implemented once: `RND(..., 2)` at `result` only for the three money
  policies, `int(RND(..., 0))` at `result` for the mileage grant, each matching the rule's "rounded to two decimal
  places only at the end and never at an intermediate step" / "taken as whole miles at the end and at no
  intermediate step". The one interior `RND` is `returned_items_total` in `drive_ext_release_charge`, which
  implements the separately stated "the part equipment return share of those lines is returned and taken out".

No empty promise was found in a rule, and `compute` invents no basis of its own — **with the exception recorded
as finding D-3 below**, which is a conflict between a rule sentence and the DB schema rather than between
`rule` and `compute`.

#### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). No pair is shared.
- Each policy's subject, `base_policy_refs`, target tool, tool docstring and terminal state admit one business
  reading; no confirmation step, review, wait or procedure outside the policy is added by a docstring.
- uuid8s: `79b211ed`, `4b632ce9`, `444a2a24`, `9b1c513c`. All four are 8 hex characters, pairwise distinct, share
  no common prefix, are not sequential, and are not adjacent values or a common stem with a changed tail. Each is
  frozen with its tool in `task_tools.py` and appears as that policy's `target_tool` in the charter.
- Tool bodies were read in full. None of the four reads, tests or branches on any prerequisite state: each does
  `ctx.find` for the `customer_id`, `ctx.create` one `drive_rental_entries` row, and (for the two `owner=user`
  tools) one `ctx.update` of the status. There is no refusal path, no error path and no hint. **The tool layer
  judges no prerequisite** — see finding D-6 for the one docstring wording issue.

#### prerequisite_graph

Two edges in the whole difficulty, both `kind: value_input`, both `form: state`:

| blocked policy | depends on | kind | gate | resolved_by | acyclic |
| --- | --- | --- | --- | --- | --- |
| `drive_ext_release_charge` | `drive_ext_additional_driver_charge` | value_input | `chargeable_base` | `charge_additional_driver_79b211ed` | yes |
| `drive_ext_return_settlement` | `drive_ext_included_mileage_grant` | value_input | `excess_miles_raw` | `grant_included_mileage_444a2a24` | yes |

- `prerequisite` is filled in on all four policies (`[]` on the two depended-on ones).
- Each `problem` points at another **extended** policy id in this file; neither points at a base policy nor at
  itself; the graph is two disjoint single edges and therefore acyclic, with no cross-task reference.
- `form` is `state` on both, and `fallback_reason` is absent on both — correct, since it is required exactly on
  action-form edges. The state form has priority and is honoured on both edges.
- `gate` names a real binding in the blocked policy's own `compute` in both cases (`chargeable_base` in
  `drive_ext_release_charge`; `excess_miles_raw` in `drive_ext_return_settlement`), so `kind: value_input` matches.
- `resolved_by` is in both cases exactly the depended-on policy's `target_tool`.
- `condition` in both cases restates the state the prerequisite sentence names, at the same strength — neither
  strengthened (no threshold, amount or date added) nor weakened.
- `effect` is a true statement in both cases; the per-task files carry the recomputation that proves it.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears anywhere in
  either `prerequisite` block.

#### prerequisite_sentences

Edge A — `drive_ext_release_charge` waits on `drive_ext_additional_driver_charge`.
`policy_source`: *"The release charge is fixed only after the rental's ledger carries the additional driver charge
owed for the drivers named on the agreement."*
Four-point test: (1) it is the second sentence of `drive_ext_release_charge`'s **own** `rule`, verbatim; (2) the
ordering connective is **"only after"**, joining this policy's own result ("the release charge is fixed") to what
it waits on; (3) what it waits on is a **record-visible state** — "the rental's ledger carries the additional
driver charge" — in the words the ledger table uses, with no performer, no action and no tool; (4) it names no
tool, no policy id, no snake_case token and no row id. Scope matches the edge's `condition` exactly.
State-form resolution: exactly one write of this difficulty brings that state about —
`charge_additional_driver_79b211ed` is the only tool in `task_tools.py` that creates a row with
`charge_category="additional_driver"`; the other three create `cancellation_fee`, `mileage_grant` and
`excess_mileage`. The reader's derivation is therefore single-reading: *the sentence names a ledger line for the
additional driver charge -> the records show no such line on this rental -> the only policy whose own rule
describes raising that charge is `drive_ext_additional_driver_charge`, whose rule opens "The additional driver
charge on an agreement is the rate class's additional driver fee for each named driver beyond the free count
carried by the rate class" -> that policy's write is the resolving action.*
The depended-on rule does **not** restate the sentence, and `drive_ext_release_charge`'s rule carries no second
wording of the dependency, no tool name and no other problem's id.

Edge B — `drive_ext_return_settlement` waits on `drive_ext_included_mileage_grant`.
`policy_source`: *"The excess mileage settled at return is worked out only after the included allowance owed for
the rental stands granted on it."*
Four-point test: (1) verbatim second sentence of `drive_ext_return_settlement`'s **own** `rule`; (2) connective
**"only after"**; (3) state form — "the included allowance owed for the rental stands granted on it" — a
record-visible state, no performer, no tool; (4) no tool, policy id, snake_case token or row id. Scope matches the
`condition`.
State-form resolution: `grant_included_mileage_444a2a24` is the only tool that creates an
`event_type="drive_mileage_grant"` row, so exactly one write brings the state about. Derivation:
*the sentence names a granted included allowance standing on the rental -> the records show no mileage-grant row ->
the only policy whose own rule describes placing it is `drive_ext_included_mileage_grant` ("The included mileage
granted on a rental is the rate class's included miles for each booked rental day, placed on the rental in one
grant covering the whole rental") -> that policy's write is the resolving action.*
The depended-on rule does not restate the sentence.

Cross-problem orders in a rule that ground no declared edge: none found in any of the four extended rules. The
only ordering words in the four rules besides the two prerequisite sentences are intra-computation ("applied once
to that product rather than to any earlier step", "at the end and at no intermediate step", "the two reliefs act
one after the other"), which state the order of steps inside one quantity and name no other problem.

Docstring silence about sequence: see finding D-6 — all four docstrings carry the phrase "before this call" in an
`Args` entry. It refers to a **read** lookup for the id, names no other problem's write tool and grounds no tree
edge, so it is recorded as an observation and not a red.

Base rules stating a cross-problem order: `drive_mileage` base states *"Every other class grants its included
miles for each booked rental day at collection"* and *"At return the miles actually driven are taken off the
allowance in one movement"*, which do order granting before return. Neither grounds edge B — edge B is grounded by
`drive_ext_return_settlement`'s own extended prerequisite sentence, which is present — so this is recorded as an
observation (D-7), not a red.

#### override_declarations

Check 1's finding half, run sentence by sentence over each `base_policy_refs` entry of all four extended policies.
The consequence of each finding on a particular world lives in that task's file.

**`drive_ext_additional_driver_charge`** — refs `drive_rate_and_extras`, `drive_club_and_corporate_interaction`.
`overwrite` names one clause of `drive_rate_and_extras`: *"Additional drivers beyond the class's free count are
charged per driver per rental day, and a driver never named on the agreement is not insured at all."* The
replacement restates the per-driver-per-day charge and adds the rounding. The extended policy then layers five
ladders onto it (free count, charged days, fee per day, naming relief, driver weighting), each of which changes
the scored quantity relative to the plain base sentence. The base sentence that fixes the quantity ("charged per
driver per rental day") **is** the one named, so the layering is inside the declared override. The second half of
the base sentence (an unnamed driver is not insured) is a liability statement extended does not touch — inherited
in full. `drive_club_and_corporate_interaction` is cited for the club-tier free-driver ladder; its base sentence
*"the club tier held on the collection date decides the discount applied to the rental rate and whether a vehicle
class upgrade is offered, and the rate class's own terms decide everything else"* governs the **rental rate
discount and upgrade**, a different quantity from the additional driver free count, so extended handles no
quantity that sentence governs and `overwrite` correctly omits it. No undeclared override found.

**`drive_ext_release_charge`** — refs `drive_cancellation`. Sentence by sentence:
1. *"Only the renter may cancel their own confirmed rental, and the cancellation is confirmed by the renter rather
   than performed on their behalf."* — inherited; honoured by `release_rental_booking_4b632ce9` being `owner="user"`.
2. *"A cancellation is handled free of charge only when frozen time is not after the moment the supplier confirmed
   the renter's booking plus the free-cancellation term of the rate class booked."* + the counting sentence —
   inherited in full; the extended rule's own scope ("outside the rate class's free-cancellation term") sits on top
   of it. See finding **D-2**.
3. *"Inside the free-cancellation term nothing is withheld on any rate class and the prepayment is returned in
   full."* — inherited; extended never applies inside the term.
4. *"Outside it the charge is read off the rate class's cancellation ladder ... and the two are never added."* —
   **named in `overwrite` and replaced** by the distant/near/standard notice-share ladder. The basis the share acts
   on (`chargeable_base`, three methods) is new, but the base rule prose fixes no basis for this quantity; the only
   base statement of a basis is the `parameter_schema` gloss *"cancellation_ladder_pct: Cancellation charge as a
   share of the rental total"*, which travels with the superseded ladder clause. Inside the declared override.
5. *"A class that returns nothing withholds the whole prepayment, and the agency service fee is not returned on any
   class."* — **not** named in `overwrite`. Extended's `chargeable_base` tier 1 takes the agency service fee **out**
   of the money the share acts on, stating its own reason: *"because that fee is not returned and is not withheld
   from twice"*. Both faces agree that the fee stays with the agency and is not returned to the renter; extended
   only declines to withhold it twice. Reaching a conclusion on this sentence: extended **follows** it. Not an
   undeclared override.
6. *"A cancellation made because the supplier itself cannot provide the vehicle is free on every class, whatever the
   ladder says."* — inherited; no supplier-unavailability notice is in either task's world.
7. *"A cancellation after the scheduled collection time has passed is not a cancellation but a no-show."* —
   inherited; an eligibility extended does not weaken.

**`drive_ext_included_mileage_grant`** — refs `drive_mileage`. `overwrite` names *"Every other class grants its
included miles for each booked rental day at collection, in one grant covering the whole rental rather than day by
day."* The extended rule keeps the one-grant shape and layers the granted-day, per-day-miles, taper, airport,
touring-equipment and driver ladders onto it. The base sentence that fixes the quantity is the one named. The
unnamed base sentence *"A rate class with unlimited mileage grants no allowance and charges for no mile however far
the vehicle is driven"* is inherited and not weakened. No undeclared override found in this policy.

**`drive_ext_return_settlement`** — refs `drive_mileage`, `drive_rate_and_extras`,
`drive_club_and_corporate_interaction`. Two overwrites are declared (the excess-rate sentence of `drive_mileage`,
and the club-tier sentence of `drive_club_and_corporate_interaction`). Sentence by sentence against `drive_mileage`
the following base sentence is **handled differently and is named in no `overwrite`**:

> *"At return the miles actually driven are taken off the allowance in one movement, measured by the difference
> between the odometer readings recorded at collection and at return."*

This sentence fixes `miles driven` — the very quantity the extended factor `odometer_reading_basis` decides by a
three-way method (latest row alone / row less late-collection allowance / rows added together). `overwrite` names
only *"Miles driven beyond the allowance are charged at the class's excess rate per mile, rounded to the whole
mile, and a rental that returns under its allowance is refunded nothing for the miles unused."*, which fixes the
**rate**, not the **miles**. This is an **undeclared override** and is recorded as finding **D-3**, which is the
same defect as the schema conflict described there; task 1's file carries the demonstrated consequence.
The `drive_rate_and_extras` ref carries no sentence governing excess mileage, and the
`drive_club_and_corporate_interaction` sentence is named and replaced.

#### factor_ladders

Structure only. Whether a factor bears weight on a world is in that task's `factor_weight`.

| policy | factor | effect | decides | tiers | multi-source beyond fall-through | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| additional_driver_charge | club_free_driver_allowance | parameter | free_driver_count | 3 | yes (club holding tier + club ledger 12m sum) | club |
| additional_driver_charge | charged_day_length_basis | method | charged_days | 3 | no (single span) | — |
| additional_driver_charge | waiver_backed_driver_fee | parameter | fee_per_day | 3 | yes (ledger CDW count + rental vehicle_class) | — |
| additional_driver_charge | advance_naming_relief | parameter | advance_relief_pct | 3 | partial (both conjuncts on drive_rentals) | — |
| additional_driver_charge | multi_driver_weighting | method | driver_weight_total | 3 | no | — |
| release_charge | notice_band_share | parameter | withheld_share_pct | 3 | no | — |
| release_charge | withheld_money_basis | method | chargeable_base | 3 | yes (two disjoint ledger filters) | — |
| release_charge | linked_disruption_relief | parameter | disruption_relief_pct | 3 | partial (two fields of one air row) | air |
| release_charge | membership_release_relief | parameter | member_relief_pct | 3 | partial (two fields of one club row) | club |
| release_charge | uncollected_equipment_return | method | returned_items_total | 3 | yes (ledger equipment lines + rental pickup_at vs NOW) | — |
| included_mileage_grant | granted_day_basis | method | granted_days | 3 | yes (ledger lines + drive_rentals.rental_days) | — |
| included_mileage_grant | package_touring_allowance | parameter | included_miles_per_day | 3 | partial (two fields of one bundle row) | bundle |
| included_mileage_grant | day_total_taper | method | base_allowance | 3 | no | — |
| included_mileage_grant | airport_transfer_allowance | parameter | airport_allowance | 3 | yes (ledger surcharge line + rental branch codes) | — |
| included_mileage_grant | touring_equipment_allowance | parameter | touring_allowance | 3 | yes (two distinct ledger categories) | — |
| included_mileage_grant | named_driver_allowance | parameter | driver_allowance | 3 | yes (ledger driver lines + granted_days) | — |
| return_settlement | overage_rate_band | parameter | excess_rate | 3 | no | — |
| return_settlement | grace_miles_carried | parameter | grace_miles | 3 | yes (damage lines + rental-rate lines, distinct filters) | — |
| return_settlement | odometer_reading_basis | method | miles_driven | 3 | yes (ledger reading rows + rental pickup_at vs picked_up_at) | — |
| return_settlement | late_reading_admin | parameter | overage_admin | 3 | yes (ledger reading date + rental dropoff_at) | — |
| return_settlement | club_driving_relief | parameter | club_relief_pct | 3 | yes (club holding tier + club ledger 24m count) | club |

Counts per policy: 5 / 5 / 6 / 5 factors — all within 4..6. Parameter/method split: 3+2, 3+2, 4+2, 4+1 — every
policy carries at least 2 `parameter` and at least 1 `method`.
Per task: task 0's two computations carry multi-source factors (`club_free_driver_allowance`,
`waiver_backed_driver_fee`, `withheld_money_basis`, `uncollected_equipment_return`) and cross-difficulty factors
reading `club` and `air`; task 1's carry multi-source factors (`granted_day_basis`, `airport_transfer_allowance`,
`touring_equipment_allowance`, `named_driver_allowance`, `grace_miles_carried`, `odometer_reading_basis`,
`late_reading_admin`, `club_driving_relief`) and cross-difficulty factors reading `bundle` and `club`. Both floors
are met.

Binding-set disjointness: checked mechanically per policy — **no binding appears in two factors' `bindings`** in
any of the four policies. Every `decides` is an input binding, never `result`.

Tier disjointness and distinctness of outcome, ladder by ladder: each of the 21 ladders has three pairwise-disjoint
tiers as stated (the third is always the fall-through), and no two tiers of one ladder select the same value or the
same method. The three cases worth naming explicitly:
- `withheld_money_basis` tier 1 (`ledger less the agency service fee`) and tier 3 (`the whole ledger`) select
  **different methods**; they coincide in value only on a rental with no agency service fee, which is a property of
  a world and not of the ladder.
- `charged_day_length_basis` tier 3 (`every booked rental day`) coincides in value with tier 2 only at exactly
  7 booked days; the methods differ.
- `overage_rate_band` fall-through is `P('excess_mileage_fee_per_mile_usd')`, which varies by rate class
  (0.22..0.32, and 0.00 on the two unlimited-mileage classes); on `Corporate Negotiated Drive Rate` it equals the
  heavy tier's 0.22, so on that one class tiers 1 and 3 select the same value. Neither task books that class.
  Recorded as observation D-8.

Conditions and outcomes against what the line of business actually does: the ladders read on club standing and
qualifying points, length of hire, whether a damage waiver was bought for the whole hire and what class of vehicle,
how far ahead the drivers were named, how many drivers, how much notice a cancellation gives, whether equipment was
sold and can be taken back, whether the linked flight collapsed and in what form its value returned, how long the
membership has run, what holiday the hire belongs to, whether the car was collected at an airport and dropped
elsewhere, whether touring equipment was sold, how large the overage is, whether the reading was taken after the
booked return, and how much the member actually drives with the programme. Each of these is something a car rental
desk genuinely weighs for the quantity its ladder decides, and none of them holds of every customer who reaches the
write. Each tier's outcome — reduced free-driver counts, tapered charged days, a lower additional-driver fee where
a waiver already stands, advance-naming relief, notice-banded withholding, disruption and membership relief,
touring mileage allowances, banded excess rates that fall as the overage grows, a one-off administration charge on a
late reading — is a treatment such a business publishes. No straw-man fall-through was found: every fall-through is
either the rate class's own published parameter or "nothing added / nothing relieved", both of which are what the
class's own terms give an ordinary customer.

One conjunct was examined specifically and found to be real, not a restatement of scope: `advance_naming_relief`'s
*"and carrying no corporate programme reference"* — corporate rentals exist in this charter
(`Corporate Negotiated Drive Rate`, `drive_rentals.corporate_program_id`), so the conjunct genuinely divides
customers rather than holding of all of them.

#### findings

**D-1 — observation (charter-global finding; figures demonstrated per task).**
*Verdict revised after the reveal, and the revision is recorded rather than hidden: this finding was written
pre-reveal as a SOURCE-TASK RED and is downgraded to an observation on the grounds given at the end of the entry.
The evidence and both figures stand unchanged.*
`drive_rentals.charges_total_usd` contradicts the ledger it is defined to equal, in every seeded rental of this
difficulty.
- *Symptom*: the same quantity — "the money standing on the rental's ledger" — has two different values in the
  world at once.
- *Root cause*: the seed sets `charges_total_usd` to a figure that is not the sum of the rental's
  `drive_rental_entries.amount_usd`, while `db_schema.json` declares the two **identically** equal.
- *Evidence*: `blueprint/db_schema.json`, `drive_rentals.charges_total_usd`: *"net amount charged to the renter for
  this rental; **identically the sum of the rental_charges account deltas**, charges positive and payouts
  negative"*; `blueprint/products/drive.yaml`, `binding.quantity_fields`: `{"charges_total_usd": "rental_charges"}`.
  Recomputation from `initial_state`:

  | task | rental | `charges_total_usd` | sum of ledger `amount_usd` |
  | --- | --- | --- | --- |
  | 0 | `12a9dc68…` (target) | 432.25 | **562.15** |
  | 0 | `1f698a91…` | 331.00 | **501.95** |
  | 1 | `be4c3ce8…` (target) | 707.45 | **1292.17** |

- *Demonstrated consequence*: task 0's scored quantity is taken from `chargeable_base`, whose rule sentence is
  *"the share acts on the money standing on the ledger with the agency service fee left out of it"*. A reader who
  takes that money from the field the schema promises is that sum reaches a different number. Figures in
  `0.md` / `factor_weight` and `task_independent_derivation`.
- *Why observation and not red (post-reveal)*: the policy surface names the rows it means without ambiguity —
  `compute.chargeable_base` is built from `SUM('drive_rental_entries','amount_usd', …)`, `inputs.history` names
  `table: drive_rental_entries`, and the rule says *"the money standing on the rental's **ledger**"*, the ledger
  being `binding.event_tables = [drive_rental_entries]`. A stale holding total is a cache diagnostic, which this
  audit's charter excludes from red-lighting, and task 0's `design_rationale` declares it deliberate: *"read the
  rental's own ledger rather than the cached total on the holding, which is deliberately stale"*. What remains
  reportable, and is not a cache diagnostic, is the **schema wording**: `db_schema.json` states the relation as an
  identity, with no "cached", "as at last posting" or "may lag" anywhere in the schema, the `accounts` block or
  `binding.quantity_fields`, so as written the world breaks a declared invariant three times over. See also
  finding **D-11**, where the same field is certified consistent in task 1 and is not.
- *Affected artifact*: `env/env_0000_online_travel_agency/tasks/car_rental_desk/tasks/0.json` and `1.json`,
  `initial_state.drive_rentals[*].charges_total_usd`; the invariant lives in
  `env/env_0000_online_travel_agency/blueprint/db_schema.json`. Bears on **task 0** (figures in `0.md` / T0-1) and
  **task 1** (read by no computation there; see D-11).
- *Relation to previous revisions*: first revision of this audit; verdict revised within this revision as noted
  above.

**D-2 — observation (charter-global; two readings demonstrated in `0.md`).**
The free-cancellation term has two anchors in the charter.
- *Symptom*: whether task 0's caller is inside or outside the free-cancellation term depends on which passage is
  read.
- *Evidence*: `parameter_schema` (base, verbatim in the extended charter):
  *"free_cancellation_hours_before_pickup: Hours before collection by which a cancellation carries no charge."*
  versus `drive_cancellation.rule`: *"A cancellation is handled free of charge only when frozen time is not after
  the moment the supplier confirmed the renter's booking plus the free-cancellation term of the rate class
  booked."*, with the parameter's own name saying `…_before_pickup`.
- *Why observation and not red*: `drive_cancellation.eligibility[0].temporal_basis` settles it unambiguously —
  `anchor_source: drive_rentals.confirmed_at`, `duration_source: variants.free_cancellation_hours_before_pickup`,
  `relation: not_after`, `unit: elapsed_hours`. A reader of the structured policy has one reading. The tension is
  between a normative rule and a glossary line that repeats the parameter's misleading name.
- *Affected artifact*: `blueprint/products/drive.yaml` `parameter_schema.free_cancellation_hours_before_pickup`
  (and its verbatim copy in `drive.extended.yaml`). Bears on **task 0**.
- *Relation to previous revisions*: this is **R3-O-2 / the F-3 residual, open since revision 1 and now in its
  fourth round**, on regenerated artifacts. Revision 3 argued it down partly on the ground that *"both extended
  rules state the confirmation anchor outright, one of them naming and rejecting the backwards-from-collection
  reading"*. **That mitigation is gone in this form**: the only occurrence of "confirm" in
  `drive_ext_release_charge.rule` is the phrase *"a **confirmed** rental"*, which names the rental's status, not
  the anchor; no extended rule of this charter states the confirmation moment, names the parameter's counting
  basis, or rejects the backwards-from-collection reading. The gloss is unchanged and still literally false about
  the parameter its own rules consume. It stays an observation because base's `drive_cancellation.rule` and its
  `eligibility[0].temporal_basis` still settle the reading for anyone working from the structured policy — but it
  is now carried into the KB with nothing adjacent to contradict it, which is a matter for the KB-document audit
  of this difficulty.


**D-3 — SOURCE-POLICY RED (charter-global finding; consequence demonstrated in `1.md`).**
`drive_ext_return_settlement` reads the mileage ledger as cumulative odometer readings, while the DB schema, the
holding's own quantity field and an unsuperseded base sentence all define those rows as per-row deltas.
- *Symptom*: "the miles driven" has two values on task 1's world, and the rental record's own allowance balance
  agrees with the one the policy does not use.
- *Root cause*: the `odometer_reading_basis` ladder's first tier treats the latest `drive_mileage_use` row as a
  whole-hire reading containing the earlier ones, but the field it reads is declared a movement, and no `overwrite`
  names the base sentence that fixes the quantity.
- *Evidence*, three passages that reach different conclusions in the same situation:
  1. `drive.extended.yaml`, `drive_ext_return_settlement.rule`: *"where two or more readings stand against the
     rental, the latest reading alone gives the miles driven and the earlier readings are taken as interim readings
     already inside it"* (implemented as `miles_driven: latest_use if use_rows >= 2 else …`).
  2. `db_schema.json`, `drive_rental_entries.miles_delta`: *"whole number of miles, negative when miles are
     consumed"*, *"**movement** of the included mileage allowance recorded by this row"*; and
     `drive_rentals.mileage_allowance_remaining`: *"included mileage still unused; **identically the sum of the
     mileage_allowance account deltas**, grants positive and miles driven negative"*.
  3. `blueprint/products/drive.yaml`, `drive_mileage.rule`: *"At return the miles actually driven are taken off the
     allowance in one movement, measured by the difference between the odometer readings recorded at collection and
     at return."* — a base sentence fixing the same quantity, named in **no** `overwrite` of
     `drive_ext_return_settlement` (whose two overwrites name the excess-rate sentence and the club-tier sentence).
     This is simultaneously the **undeclared override** of check 1.
- *Demonstrated consequence*: on task 1's world the two readings give different miles driven and a different scored
  settlement. Figures in `1.md` / `task_independent_derivation` and `factor_weight`.
- *Affected artifact*: `drive.extended.yaml`, `drive_ext_return_settlement.rule` /
  `compute.miles_driven` / `factors[odometer_reading_basis]` / `overwrite`; and
  `tasks/1.json` `initial_state.drive_rentals[be4c3ce8…].mileage_allowance_remaining`. Bears on **task 1**.
- *Relation to previous revisions*: first revision.

**D-4 — SOURCE-FACTOR RED (charter-global finding; consequence demonstrated in `0.md`).**
`club_memberships.qualifying_points_pts` stamps the exact aggregate the `club_free_driver_allowance` ladder asks
the reader to compute, and is itself inconsistent with the identity the schema declares for it.
- *Symptom*: the tier can be read off a field instead of computed from the rule's twelve-month window, and the two
  routes cannot be told apart by the score.
- *Evidence*: `db_schema.json`, `club_memberships.qualifying_points_pts`: *"tier-qualifying points counted in the
  current qualifying period; **identically the sum of the qualifying_points account deltas**"*. In task 0 the
  seeded value is **6800**, while the sum of that membership's qualifying deltas is **11700**
  (3200 + 2100 + 1500 + 4900) and the sum over the current qualifying period (`tier_effective_date`
  2026-03-01 onward) is **3600**. 6800 is neither; it is exactly the rule's rolling-twelve-month figure
  `XSUM(..., within_months=12) = 6800`.
- *Demonstrated consequence*: in `0.md` / `factor_weight` — an agent that never applies the twelve-month window and
  simply reads the field lands on the same tier and the same scored number, and the computation's near-miss row is
  neutralised in the same stroke.
- *Affected artifact*: `tasks/0.json` `initial_state.club_memberships[429792c1…].qualifying_points_pts`; the
  invariant in `db_schema.json`. The same field is inconsistent in task 1 (31400 seeded vs 9400 summed) but stamps
  nothing that task's ladders read, so there it is only the invariant breach (D-1's sibling), not a stamp.
- *Relation to previous revisions*: first revision.

**D-5 — observation (charter-global).** `drive_ext_return_settlement.factors[overage_rate_band].bindings` is
`[grant_total, excess_rate]`. `grant_total` is the mileage grant sum — the binding the prerequisite edge feeds —
and plays no part in deciding `excess_rate`, which is decided by `chargeable_miles`; `chargeable_miles` appears in
no factor's `bindings` at all. Disjointness still holds and substitution is driven by `baseline`, not by
`bindings`, so no scored consequence follows. Affected artifact: `drive.extended.yaml`,
`drive_ext_return_settlement.factors[0].bindings`.

**D-6 — observation (charter-global).** Every `Args` entry for `drive_rental_id` in all four tools carries
*"read it from the rental record returned by the car rental lookup before this call."* The word "before" is an
ordering word in a docstring. It orders a **read** that every one of the four tools needs equally, names no other
tool, and grounds no tree edge, so no consequence follows. Affected artifact:
`env/env_0000_online_travel_agency/tasks/car_rental_desk/task_tools.py`, all four docstrings.

**D-7 — observation (charter-global).** `drive_mileage` (base) states *"Every other class grants its included miles
for each booked rental day **at collection**"*, which orders the grant before the return. Edge B does not rest on
it — `drive_ext_return_settlement` carries its own prerequisite sentence — so this is an observation and not the
red that a base-grounded edge would be. Affected artifact: `blueprint/products/drive.yaml`, `drive_mileage.rule`.

**D-8 — observation (charter-global).** `overage_rate_band`'s fall-through
`P('excess_mileage_fee_per_mile_usd')` equals its heavy tier's `K('heavy_overage_rate_usd') = 0.22` on
`Corporate Negotiated Drive Rate`, so on that one rate class two tiers of the ladder select the same value.
Neither task books that class, so no consequence is demonstrable here. Affected artifact:
`drive.extended.yaml`, `drive_ext_return_settlement.factors[overage_rate_band]` against
`variants[Corporate Negotiated Drive Rate].parameters.excess_mileage_fee_per_mile_usd`.

**D-9 — observation (charter-global).** `lifecycle.transitions` declares `picked_up -> returned` as
`"by": "system"`, while `drive_ext_return_settlement.target_tool` (`close_rental_return_9b1c513c`) is
`owner="user"`; the blueprint's own difficulty summary likewise names only cancellation as the renter's own act
(*"the agent prices and posts ledger lines, **settles fuel and mileage** … while **cancelling** a confirmed rental
is the renter's own act and is confirmed by them"*). The `drive_return` event's `meaning` — *"The renter returns
the vehicle and the agreement is closed off"* — makes `owner="user"` defensible, and task 1's persona settles the
authorisation explicitly, so no second scored answer follows. Affected artifact:
`blueprint/products/drive.yaml` `lifecycle.transitions`, `blueprint/blueprint.yaml` lines 177-219, against
`task_tools.py` `close_rental_return_9b1c513c`.

**D-10 — observation (charter-global).** The `drive_return` event declares a trigger raising a
`drive_mileage_use` line (`charge_category: mileage_use`), but `close_rental_return_9b1c513c` raises only an
`excess_mileage` extras line and no mileage-use row, so the terminal state omits a line the charter's event grammar
says a return raises. No scored value depends on it. Affected artifact: `blueprint/products/drive.yaml`
`events[drive_return].triggers` against `task_tools.py` `close_rental_return_9b1c513c`.

**D-11 — SOURCE-TASK RED (charter-global finding; consequence demonstrated in `1.md` / T1-2).**
*Added after the reveal, because it rests on `design_rationale`, a masked field. It is recorded here rather than
inside the pre-reveal section above, which stays pre-reveal by construction.*
The two tasks certify the same seeded field in opposite terms, and one of the two certifications is false.
- *Symptom*: task 1's worklog discharges its cache check with a sentence that recomputation contradicts.
- *Evidence*: `tasks/1.json` `design_rationale`: *"Cache: charges_total_usd stands at 707.45, which is the
  ledger's own sum of the money lines at the opening"*. The 23 ledger rows of that rental sum to **1292.17**; the
  two `drive_mileage_use` rows carry `amount_usd = 0.00`, so "the money lines" accounts for none of the 584.72 gap.
  Task 0's worklog calls the same field on its own rental *"deliberately stale"*, which is true there
  (432.25 against 562.15).
- *Demonstrated consequence*: the artifact's own proof for this relationship is false; no scored parameter moves,
  since the same sentence's second clause (*"no compute reads it"*) is correct for task 1. Recorded per this
  audit's rule that a `design_rationale` sentence asserting what the world is like is part of the proof and is
  verified word for word.
- *Affected artifact*: `tasks/1.json` `design_rationale` (STEP 3, `Cache:`), against that task's
  `initial_state.drive_rental_entries` and `initial_state.drive_rentals[be4c3ce8…].charges_total_usd`. Bears on
  **task 1**.
- *Relation to previous revisions*: first revision.

### closing_checklist

Written after both tasks' `source_derivation_frozen` and `source_gt_comparison` were on disk.

- **Audit files correspond one-to-one with the tasks.** `0.md` and `1.md` sit alongside this file in
  `env/env_0000_online_travel_agency/audits/policy_task/car_rental_desk/`. This is revision 1; no earlier revision exists
  in this directory, so nothing has been overwritten. Each task file carries a `source_derivation_frozen` frozen
  before any reveal, a `source_gt_comparison`, and per-task findings, and each cites this file by path and heading
  for every charter-global conclusion instead of restating it.
- **Every comparison section carries a verdict.** Task 0: PASS on policy self-consistency, problem tree and unique
  solution; **SOURCE-FACTOR RED** on factors bearing weight (T0-3). Task 1: PASS on problem tree and factors;
  **SOURCE-POLICY RED** (T1-1) and **SOURCE-TASK RED** (T1-1, T1-2) otherwise. **This difficulty therefore does
  not pass the source-layer audit**: the four relationships do not hold together.
- **Extended policies fully covered, scopes pairwise disjoint.** Four extended policies; task 0 claims
  `{drive_ext_release_charge, drive_ext_additional_driver_charge}` and task 1
  `{drive_ext_included_mileage_grant, drive_ext_return_settlement}`, each scope spanning its whole problem tree
  (root plus its one prerequisite problem). Disjoint and jointly complete. Confirmed against the revealed
  `charter_scope` of both tasks after the freeze.
- **Task tools and GT are closed.** Four tools, one per policy, each appearing as exactly one policy's
  `target_tool` and in exactly one task's `charter_scope.task_tools`. Every gold write is one of those four; no
  gold action calls a tool the charter does not bind.
- **uuid8s independently generated and frozen.** `79b211ed`, `4b632ce9`, `444a2a24`, `9b1c513c` — pairwise
  distinct, no shared prefix, not sequential, not a common stem with a changed tail.
- **Problem trees.** Each task's tree has **1** prerequisite problem (within 1..3), **1** `value_input` edge
  (≥ max(n − 1, 1) = 1), at least one problem resolved by an `owner=user` tool (the root in both cases:
  `release_rental_booking_4b632ce9`, `close_rental_return_9b1c513c`), and no cycle. The `prerequisite` edges of the
  whole difficulty form two disjoint single edges — a directed acyclic graph, with no cycle created by any
  cross-task reference. Both edges were independently shown to bear weight (task 0: 103.37 vs 77.11; task 1:
  150.30 vs 601.74).
- **Computations, baselines and factors.** Four computations, each with a self-sufficient `baseline` whose rule
  sentences are all in the policy `rule` and which yields a definite number different from gold
  (360.00 vs 102.96; 665.11 vs 103.37; 1050 vs 2280; 524.90 vs 150.30). Factor counts 5 / 5 / 6 / 5, all within
  4..6, each with at least 2 `parameter` and 1 `method`; every ladder has three pairwise-disjoint tiers stated in
  full in its own `rule`; no two tiers of any ladder select the same value or method on either task's rate class
  (the one class where they would is observation D-8, and neither task books it); every condition and outcome is
  one a car rental desk actually holds. All 21 factors were independently recomputed against their baselines on
  their own task's handling-time world and **all 21 move the scored value**, matching the artifacts' own
  `factor_sensitivity` figure for figure (22 of 22 figures, counting both `baseline_result`s per task).
  The one factor defect is not arithmetic: T0-3, where a seeded summary field stamps the tier
  `club_free_driver_allowance` selects.
- **Instantiation-stage gates re-run on the final form** (repository root, after this audit; no artifact was
  edited by it):
  - `check_extended.py` → EXTENDED OK
  - `check_task_tools.py` → TASK TOOL CONTRACT OK
  - `replay_tasks.py` → REPLAY OK (0.json 11 acts / 59 closure rows; 1.json 11 acts / 33 closure rows)
  - `check_solvability.py` → SOLVABILITY OK
  - `check_compute.py` → COMPUTE OK (branches mean 28.00, steps mean 11.00, history_rows_max 52, branches_max 29)
  - `check_grounding.py` → GROUNDING OK
  - `check_cross_fire.py` → SCOPE OK
  All seven reproduce the brief's snapshot exactly. They remain the qualification to enter this audit, not a proof
  of the three reds above, none of which is structural.

**Outstanding for rework (reported only; this audit designs no fix and edits no artifact):**
T0-3 (SOURCE-FACTOR RED), T1-1 (SOURCE-POLICY RED with a unique-solution consequence), T1-2 (SOURCE-TASK RED).
Observations on record: D-1, D-2, D-5, D-6, D-7, D-8, D-9, D-10, T0-1, T0-2, T0-4, T1-3, T1-4, T1-5.

---

# revision_5 — re-audit round 2 of the reworked form (charter-global)

## re_derivation (revision 5)

- freeze time: 2026-09-17 (session clock), written **before any task's GT was read this round**.
- auditor: the same independent source-layer auditor that produced revision 4.
- **Nothing is carried forward by reference.** All four of this round's shared inputs moved, so every section below
  was re-derived in full from the artifacts:

| input | revision 4 | revision 5 |
| --- | --- | --- |
| `drive.extended.yaml` sha256/16 | `ea0f49895303d4ac` | `c108776c0406568f` (151190 bytes) |
| `task_tools.py` sha256/16 | `6180432be1a7d058` | `8802dc85ea69c12c` (10547 bytes) |
| `0.masked.json` sha256/16 | `a168f043977092c4` | `d901f85b46360a7d` |
| `1.masked.json` sha256/16 | `a95fac174ab4ebe1` | `1710583517b78838` |

  All four reproduce on disk. The coordinator reports `git diff env/env_0000_online_travel_agency/blueprint/` is empty, and this
  audit re-verified it directly: the base section of `drive.extended.yaml` is still **byte-identical** to
  `blueprint/products/drive.yaml` by canonical-JSON key diff (`DIFFS: []`).
- entry conditions (Step 0): the brief carried the re-run gate snapshot (all seven green) and both rebuilt
  view hashes. Complete.
- **carry-over disclosure.** This is a re-audit, so revision 4's revealed gold is already known to this auditor and
  a second round cannot be blind in the sense revision 4's first section was. Two things limit what that can hide,
  and both are stated rather than assumed: (a) every figure below was produced by evaluating the policy's own
  `compute` bindings against the rebuilt world, mechanically, before any GT of this round was opened; (b) task 1's
  scored settlement **changed** this round, and this audit derived **115.65** from the artifacts without knowing
  the new value — the coordinator disclosed only that it had changed, not to what. Task 0's two values came out
  unchanged from revision 4, which is a fact about the rework, not evidence of independence, and is marked as such
  in that task's file. The reworker's own figures and reasoning were withheld from the brief by design and were
  not read.
- **The reworker's claims were not accepted.** Each item below is decided against the artifacts.

### revision_5 / policy_conflict_scan

Four extended policies, unchanged in identity, subject, trigger, target tool and computed quantity from revision 4;
`charge_additional_driver_79b211ed` / `additional_driver_charge_usd`, `release_rental_booking_4b632ce9` /
`release_charge_usd`, `grant_included_mileage_444a2a24` / `miles_granted`, `close_rental_return_9b1c513c` /
`excess_mileage_charge_usd`. Each `(target_tool, computes)` pair is still claimed by exactly one policy. The
`drive_extras_charge` subject is still shared by the additional-driver and return-settlement policies and still
does not collide: different `charge_category` (`additional_driver` vs `excess_mileage`), different quantity,
different trigger, different task. Task scopes remain pairwise disjoint and jointly complete.

uuid8s `79b211ed`, `4b632ce9`, `444a2a24`, `9b1c513c` are unchanged — correct, since the tools were retained rather
than replaced — and remain pairwise distinct, non-sequential and without a shared stem.

Tool bodies were re-read in full. All four still do `ctx.find` → `ctx.create` one ledger row (plus one
`ctx.update` of `status` on the two `owner=user` tools) with **no** conditional, no refusal path, no error and no
hint. The tool layer still judges no prerequisite.

### revision_5 / rule_compute_equivalence

Re-run mechanically over all four policies: **0 issues**.
- every `compute` binding has a `compute_basis` entry and every `compute_basis` key is a real binding;
- every `compute_basis` value is a verbatim substring of its own policy's `rule`;
- every `baseline.rule` is verbatim inside the `rule`;
- **every `overwrite.replaced_by` text is verbatim inside the `rule`** (checked this round because a new overwrite
  was added — all six across the charter pass);
- no factor's `bindings` overlap another's, in any of the four policies.

### revision_5 / override_declarations

Re-swept sentence by sentence over all four cited base policies. Superseded versus inherited:

- **`drive_mileage`** — now **three** of its seven sentences are named in an `overwrite` (was two). The addition is
  exactly the sentence revision 4 red-lighted as an undeclared override: *"At return the miles actually driven are
  taken off the allowance in one movement, measured by the difference between the odometer readings recorded at
  collection and at return."* It is now `drive_ext_return_settlement.overwrite[1].superseded_clause`, verbatim.
  Inherited and not weakened: the unlimited-mileage sentence, the caller-fact odometer sentence, the extension
  sentence, and the no-reading/supplier-measurement sentence.
- **`drive_cancellation`** — one sentence superseded (the ladder clause), unchanged from revision 4. The
  agency-service-fee sentence is still inherited and still **followed** rather than overridden, on the same
  reasoning recorded in revision 4's `### override_declarations`.
- **`drive_rate_and_extras`** — one sentence superseded (the additional-driver clause), unchanged.
- **`drive_club_and_corporate_interaction`** — one sentence superseded (the club-tier clause), unchanged.

One inherited sentence is recorded as an observation below (R5-O-3): `drive_mileage`'s *"Where the rental is
extended, the allowance grows by the class's included miles for each additional day, granted at the moment the
extension is agreed."*

### revision_5 / prerequisite_graph and prerequisite_sentences

Both edges are unchanged in shape and both prerequisite sentences are unchanged in wording:

| blocked | depends on | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| `drive_ext_release_charge` | `drive_ext_additional_driver_charge` | value_input | `chargeable_base` | state | `charge_additional_driver_79b211ed` |
| `drive_ext_return_settlement` | `drive_ext_included_mileage_grant` | value_input | `excess_miles_raw` | state | `grant_included_mileage_444a2a24` |

Re-tested rather than carried forward: both `policy_source` sentences are still verbatim in the blocked policy's
own `rule`; both carry the ordering connective *"only after"*; both name a record-visible state in table words with
no performer and no tool; neither names a tool, policy id, snake_case token or row id; `form` is `state` on both
with no `fallback_reason`, correctly. Exactly one write of this difficulty still brings each waited-on state about
(`additional_driver` category; `drive_mileage_grant` event type) — re-checked against the reworked
`task_tools.py`. Neither depended-on rule restates its dependant's sentence. No rule of the charter states a
cross-problem order that grounds no declared edge. The graph is still two disjoint single edges, acyclic.

### revision_5 / factor_ladders

Counts are unchanged: 5 / 5 / 6 / 5 factors, all within 4..6; parameter/method splits 3+2, 3+2, 4+2, 4+1, so every
policy still carries ≥ 2 `parameter` and ≥ 1 `method`. Every ladder still has three tiers stated in full in its own
`rule`, and every fall-through tier is still the factor's declared `baseline`.

Two structural changes this round, both inside `drive_ext_return_settlement`:
- `odometer_reading_basis` is **replaced** by `driven_mileage_basis` (`method`, decides `miles_driven`), rebuilt so
  that every tier reads the ledger rows as per-row movements and **adds them together**, with a new first tier for
  a rental carrying no movement at all. This is the substance of the T1-1 fix and is assessed in that task's file.
- `overage_rate_band.bindings` gains `chargeable_miles`, the binding that actually decides `excess_rate`. It still
  also carries `grant_total`, which does not — see R5-O-1.

Parameter change: `heavy_overage_rate_usd` moves `0.22 → 0.20`. This closes revision 4's D-8: the heavy tier no
longer coincides with `Corporate Negotiated Drive Rate`'s own `excess_mileage_fee_per_mile_usd` of 0.22. Checked
across all six classes against both banded rates (0.20 heavy, 0.26 light): the published per-mile rates are 0.32,
0.29, 0.25, 0.00, 0.00 and 0.22, so no class now makes two tiers of that ladder select the same value. (The two
0.00 classes carry `unlimited_mileage: true`, which base excludes from this policy entirely.)

One new ladder-shape observation is recorded below as **R5-O-2** (`driven_mileage_basis` tiers 1 and 2 overlap as
stated), and it is a **regression** against revision 4's ladder, which was pairwise disjoint as stated.

### revision_5 / findings

Reached after both tasks' re-derivations were frozen and their GT revealed. Each item was decided against the
artifacts; the reworker's figures and reasoning were withheld by design and were not read.

**Status of every revision-4 item**

| item | revision 4 | revision 5 verdict | basis |
| --- | --- | --- | --- |
| **T0-3** | `SOURCE-FACTOR RED` | **CLOSED** | the stamp (5700) and the rule's twelve-month figure (6800) now fall on **different tiers**, scoring 137.28 against 102.96; the field satisfies both clauses of its declared identity; the near-miss row was re-signed to `−1100` so that applying the window is what carries the customer over the threshold. Demonstrated in `0.md` / `### the revision-4 items, re-tested on this world` |
| **T1-1** | `SOURCE-POLICY RED` + unique-solution consequence | **CLOSED** on all three faces | the base miles sentence is now named verbatim in a second `overwrite`; the ladder reads rows as per-row movements and adds them, so rule, `miles_delta` and `mileage_allowance_remaining` all start from 2940; and the second seeded movement is now `−1790` so the world no longer asserts the opposite. Demonstrated in `1.md` / `### T1-1 re-tested` |
| **T1-2 / D-11** | `SOURCE-TASK RED` | **CLOSED** | the false certification is gone and its replacement was verified clause by clause against the seed (1292.17, −2940, 9400, 9020) |
| **D-1 / T0-1** | observation | **CLOSED** on the seeded world; residual recorded as R5-O-4 | every `charges_total_usd` and `mileage_allowance_remaining` in both tasks now equals its own ledger |
| **T0-2** | observation | **CLOSED** | the closure's evidence path now cites a ledger row that exists and bears on the claim |
| **D-5** | observation | **partly closed**; residual R5-O-1 | `chargeable_miles` added to `overage_rate_band.bindings`; `grant_total` still declared there and still decides nothing |
| **D-6** | observation | **CLOSED** | no ordering word left in any of the four docstrings |
| **D-8** | observation | **CLOSED** | `heavy_overage_rate_usd` 0.22 → 0.20; checked across all six rate classes |
| **T1-5** | observation | **CLOSED** | both club summary fields satisfy their declared identities |
| **D-2 / T0-4** | observation, mitigation missing | **mitigation restored**; the base gloss stands by the coordinator's recorded decision | `drive_ext_release_charge.rule` now carries *"The free-cancellation term this scope refers to runs forward from the moment the supplier confirmed the renter's booking, and never backwards from the scheduled collection moment."* — it names the anchor **and** rejects the reading the gloss invites, which is more than the revision-3 wording did |
| **D-7** | observation | accepted by the coordinator | `drive_mileage`'s at-collection ordering still grounds no edge; both edges rest on their blocked policy's own prerequisite sentence |
| **D-9 / T1-3** | observation | accepted by the coordinator | unchanged |
| **D-10 / T1-4** | observation | accepted by the coordinator | unchanged |

**Every revision-4 RED is closed on its merits.** Each was verified by re-derivation on the reworked world and by
reading the changed rule, override, schema identity and seeded rows — not by reading the reworker's account.

**New items this round.** Three, all observations, none bearing on the four relationships:
- **R5-O-1** (`1.md`) — `overage_rate_band.bindings` still carries `grant_total`, which decides nothing about
  `excess_rate`. Residual of D-5.
- **R5-O-2** (`1.md`) — **the one regression found.** The rebuilt `driven_mileage_basis` ladder's tiers 1 and 2
  overlap as stated (no movement / late collection), where revision 4's ladder was pairwise disjoint as stated. The
  prose cascade and the compute's evaluation order both give one answer, and no world in this difficulty triggers
  the overlap, so no consequence is demonstrable and it is an observation.
- **R5-O-3** (`1.md`) — `drive_mileage`'s extension sentence is inherited while the grant policy folds extra days
  into its single grant. Pre-existing, **not** introduced by this rework, and not raised in revision 4; reported
  now in honesty. The amount is governed by an already-declared override, so no second value is derivable.
- **R5-O-4** (`0.md`) — after this task's own writes, the holding's cached total lags the ledger rows by exactly
  the prerequisite line, because no task tool in this framework aggregates a history into a derived value.
  Structural to the tool contract, disclosed openly in the worklog, and excluded from red-lighting as a cache
  diagnostic.

## closing_checklist (revision 5)

**This difficulty closes out.** All four relationships hold in both tasks.

| item | status |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks; `_difficulty.md` alongside | ✓ |
| old revisions traceable | ✓ revisions 1–5 appended in order; **no earlier revision's text was rewritten**, including revision 4's stale task-1 figures, which stand as recorded |
| every comparison section carries a verdict | ✓ both tasks, all four relationships **PASS** this round |
| extended policies fully covered; task scopes pairwise disjoint, each spanning its whole tree | ✓ {release, additional driver} ∩ {grant, settlement} = ∅ |
| task tools and GT closed | ✓ `clos = init` at 61/61 and 33/33, `match: True` |
| each task tool an independently generated, frozen uuid8 | ✓ `79b211ed`, `4b632ce9`, `444a2a24`, `9b1c513c` — retained with their tools, pairwise distinct, non-sequential, no shared stem |
| every tree: 1–3 prerequisite problems, ≥ `max(n−1,1)` `value_input` edges, ≥ 1 `owner=user` write, no cycle | ✓ one prerequisite problem, one `value_input` edge, one customer write each |
| difficulty-wide `prerequisite` graph acyclic | ✓ two disjoint single edges |
| every computation: self-sufficient baseline, 4–6 factors (≥ 2 `parameter`, ≥ 1 `method`), ladders ≥ 3 tiers stated in the rule | ✓ 5 / 5 / 6 / 5 |
| per task ≥ 1 multi-source and ≥ 1 cross-difficulty factor | ✓ task 0 reads `club` and `air`; task 1 reads `bundle` and `club`, all seeded and all charter-consistent |
| every factor bears weight against an honest baseline; baseline alone definite and ≠ gold | ✓ all 21, recomputed this round |
| instantiation-stage gates re-run on the final form | ✓ re-run by this audit from the repository root: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK |

**Scored values across the two rounds of this run:**

| task | parameter | revision 4 | revision 5 |
| --- | --- | --- | --- |
| 0 | `additional_driver_charge_usd` | `102.96` | **`102.96`** |
| 0 | `release_charge_usd` | `103.37` | **`103.37`** |
| 1 | `miles_granted` | `2280` | **`2280`** |
| 1 | `excess_mileage_charge_usd` | `150.30` | **`115.65`** — moved by design, as the T1-1 fix required |

| relationship | task 0 | task 1 |
| --- | --- | --- |
| Policy self-consistency | **PASS** | **PASS** (was `SOURCE-POLICY RED`) |
| The problem tree holds | **PASS** | **PASS** |
| Factors bear weight | **PASS** (was `SOURCE-FACTOR RED`) | **PASS** |
| Policy ↔ task unique solution | **PASS** | **PASS** (was `SOURCE-TASK RED`) |

Three REDs were raised in revision 4 — T0-3, T1-1 and T1-2 — and all three are closed on their merits, each
verified by re-derivation on the reworked world rather than by reading the reworker's account. Four observations
remain open: R5-O-1, R5-O-2 (the one regression, with no demonstrable consequence), R5-O-3 and R5-O-4, together
with the base gloss the coordinator has recorded as a known issue and the three items it accepted with reasoning
(D-7, D-9/T1-3, D-10/T1-4). None bears on the four relationships. No artifact was edited by this audit at any
round, and no fix was designed or arranged.
