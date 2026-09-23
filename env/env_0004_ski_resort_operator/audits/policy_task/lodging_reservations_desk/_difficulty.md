# Policy-task audit — lodging_reservations_desk / charter-global

## charter_global_frozen

- Auditor: independent source-layer auditor (erl-task-policy-audit), single pass over M=2.
- Freeze time of this section: 2026-09-17, written **before any task's GT fields were read**.
- Freeze hashes (sha256, first 16 hex, of the masked-view copies supplied by the coordinator, verified by the auditor with `sha256sum`):
  - `lodging.extended.yaml` — `77389c0b6e7c12bb`
  - `task_tools.py` — `843389fdabdcbf91`
  - `tasks/0.json` (masked) — `2461652bc7e8657c`
  - `tasks/1.json` (masked) — `6472376a9c846086`
- Fields permitted for this section: the whole of `env/env_0004_ski_resort_operator/blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml), the whole of `lodging.extended.yaml` (base section + `extended_policies`), the whole of `task_tools.py`, and `erlbench/`.
- Fields explicitly masked while this section was written: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state` of both tasks. The coordinator constructed the masked views by whitelist (`frozen_time`, `user_scenario`, `initial_state` only); the auditor read task files only from
  `/tmp/claude-10250/-mnt-moonfs-wangzhaoji-m4-github-enterprise-rl/1dfabe41-064c-4be8-afd1-06653cea788e/scratchpad/masked_views_coordinator/lodging_reservations_desk/tasks/` until both per-task derivations were on disk.
- Entry condition: the instantiation-stage gate snapshot came with the brief (EXTENDED / TASK-TOOL-CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; TRACEABILITY not runnable before the render step, by construction). The auditor did not re-run them at entry and does not treat the green light as proof of correctness.

### policy_conflict_scan

Complete structured policy in force for category `lodging`: 10 base policies (`lodging_agg_multi_holding`, `lodging_agg_household_stay_pricing`, `lodging_booking_terms`, `lodging_deposit_terms`, `lodging_rate_and_fees`, `lodging_stay_operations`, `lodging_modification`, `lodging_cancellation`, `lodging_checkout_settlement`, `lodging_closure`) verbatim-copied from `blueprint/products/lodging.yaml`, plus 6 extended policies.

Base copy is verbatim identical to the blueprint product: every top-level key of `blueprint/products/lodging.yaml` (`category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies`) compares equal to the copy in `lodging.extended.yaml` under a canonical JSON dump; the only key the extended file adds is `extended_policies`. Script-verified, 0 differences.

| Extended policy | subject | computes | target_tool | trigger |
| --- | --- | --- | --- | --- |
| `lodging_ext_stay_rate_posting` | lodging_room_charge | room_charge_amount_usd | `post_stay_room_charge_ee3504ba` | state_due |
| `lodging_ext_reservation_deposit` | lodging_deposit_charge | deposit_amount_usd | `authorise_reservation_deposit_3e63cb2f` | state_due |
| `lodging_ext_stay_resort_charge` | lodging_resort_fee | resort_charge_amount_usd | `post_stay_resort_charge_f79fa34a` | state_due |
| `lodging_ext_departure_service_charge` | lodging_incidental_charge | service_charge_amount_usd | `post_departure_service_charge_1468621e` | state_due |
| `lodging_ext_early_departure_charge` | lodging_fee_charge | retained_amount_usd | `post_early_departure_charge_bb461064` | state_due |
| `lodging_ext_departure_settlement` | lodging_payment | settlement_amount_usd | `settle_departure_folio_07fd1088` | state_due |

Overlapping-subject scan: the six extended policies carry six pairwise-distinct `subject` event types and six pairwise-distinct `computes` names, so no two extended policies decide the same quantity. Eligibility inherited from base does not collide: `deposit_chargeable_state` (held/deposit_pending/confirmed) applies only to `lodging_deposit_charge`; `resort_fee_stay_state` (checked_in/checked_out) only to `lodging_resort_fee`; `fee_bearing_reservation_state` only to `lodging_fee_charge`; `deposit_apply_state` only to `lodging_deposit_apply`. No two of them govern one write.

Time anchors: `deposit_due_period` anchors on `lodging_holdings.booked_date` (calendar days forward), `change_notice_deadline` and `free_cancellation_deadline` anchor on `lodging_holdings.arrival_date` (calendar days back), `incidental_release_window` anchors on `lodging_holdings.checked_out_at` (business days forward). Four distinct anchors, no two governing the same decision. One deviation is recorded at **F-7** below.

Cross-category read boundaries declared by the extended charter: `passes`, `lessons`, `rentals`, `insure`, `dining`, `tickets` — six, matching the EXTENDED gate line (`cross-cat=6`). All six are read as `branch` or `existence` only; no extended policy writes into another category.

Claimed task scopes (from the task tools each policy binds and the `prerequisite` graph, not from the masked `charter_scope`): the graph has exactly two weakly-connected components —
- `{lodging_ext_stay_rate_posting -> lodging_ext_reservation_deposit}` (deposit is the sink), and
- `{lodging_ext_stay_resort_charge, lodging_ext_departure_service_charge, lodging_ext_early_departure_charge} -> lodging_ext_departure_settlement` (settlement is the sink).

The two components are disjoint and together cover all 6 extended policies, so the two tasks' scopes are mutually exclusive and jointly complete **provided** each task claims exactly one component. That is confirmed per task in the task files.

### rule_compute_equivalence

Check 2 was run binding by binding over all six policies: **128 `compute` bindings, 128 `compute_basis` entries**, one per binding. Every `compute_basis` string was located **verbatim** in that policy's own `rule` (exact substring match after whitespace normalisation; script-verified, 0 misses) — no basis sentence is invented. In the other direction, every tier declared under `factors[].ladder` corresponds to a sentence of the `rule` and to a branch of the `decides` binding, for all 29 declared factors; four tier `when` strings are exact restatements rather than character-identical copies of the rule clause and were checked by hand (`passholder_reduction` tiers 1–2, `straddling_window_pricing` tiers 1–2, `passholder_parking_rate` tier 2, `nights_given_up_basis` tier 2) — each names the same condition the rule names, so the equivalence holds in both directions.

Quantities, windows, filters, tiers, acting bases, caps/floors and rounding all carry a quotation. Rounding is uniform: every policy rounds once at the end with `RND(..., 2)` and states it ("carried at full precision … rounded to the nearest cent once, at the end").

Three gaps were found where `compute` restricts or re-bases what the `rule` states. They are set out as findings **F-5**, **F-6**, **F-7**.

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy (table above); no pair repeats.

uuid8 tails, read individually off `task_tools.py`:

| tool | uuid8 |
| --- | --- |
| `post_stay_room_charge_` | `ee3504ba` |
| `authorise_reservation_deposit_` | `3e63cb2f` |
| `post_stay_resort_charge_` | `f79fa34a` |
| `post_departure_service_charge_` | `1468621e` |
| `post_early_departure_charge_` | `bb461064` |
| `settle_departure_folio_` | `07fd1088` |

All six are distinct; no shared prefix of 2 or more hex characters across the set; no pair differs only in a tail character; no arithmetic or lexical sequence; none reused from another tool in this bundle. PASS.

Docstrings: none names another tool, none states a business step's position in a sequence, none adds a confirmation, review or wait. One phrase recurs and is recorded as an observation at **F-9**.

Function bodies: each of the six tools does `ctx.find("lodging_holdings", lodging_id=...)`, computes `round(amount, 2)`, writes one `lodging_folio` row and updates one holding field. **No tool reads a status, checks a date, tests whether another entry already stands on the folio, raises, or returns a hint.** The tool layer therefore judges no prerequisite and no eligibility. PASS (this is the function-body citation the per-task files refer to).

### prerequisite_graph

Check 7 over the whole graph.

- All six policies carry a `prerequisite` key; four are `[]` (`lodging_ext_stay_rate_posting`, `lodging_ext_stay_resort_charge`, `lodging_ext_departure_service_charge`, `lodging_ext_early_departure_charge`).
- Four edges in all:

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| `lodging_ext_reservation_deposit` | `lodging_ext_stay_rate_posting` | value_input | `posted_room_rate` | state | `post_stay_room_charge_ee3504ba` |
| `lodging_ext_departure_settlement` | `lodging_ext_early_departure_charge` | value_input | `outstanding` | state | `post_early_departure_charge_bb461064` |
| `lodging_ext_departure_settlement` | `lodging_ext_departure_service_charge` | value_input | `outstanding` | state | `post_departure_service_charge_1468621e` |
| `lodging_ext_departure_settlement` | `lodging_ext_stay_resort_charge` | value_input | `outstanding` | state | `post_stay_resort_charge_f79fa34a` |

- Every `problem` names another extended policy id **in this file**; none names a base policy; none is self-referential. The graph is acyclic (two chains of depth 1, no back-edge).
- `form` is `state` on all four; `fallback_reason` is absent on all four, which is exactly right for the state form. No action-form edge exists, so the state form's priority is honoured everywhere by construction.
- `gate` matches `kind`: all four are `value_input`, and each `gate` names a binding that genuinely exists in the blocked policy's `compute` — `posted_room_rate` is `compute[0]` of `lodging_ext_reservation_deposit`; `outstanding` is `compute[2]` of `lodging_ext_departure_settlement`. Neither is `result`. PASS.
- `resolved_by` is the depended-on policy's own `target_tool` in all four cases, and each named tool genuinely creates the `lodging_folio` row the `effect` describes: `post_stay_room_charge_ee3504ba` creates `event_type="lodging_room_charge", charge_category="room_rate"`, which is precisely the row `SUM('lodging_folio','amount_usd', event_type='lodging_room_charge', charge_category='room_rate')` reads; the three settlement tools create `lodging_fee_charge`, `lodging_incidental_charge` and `lodging_resort_fee` rows, all four of which `folio_charges` sums. PASS.
- `condition` wording matches what the sentence carries, neither strengthened nor weakened, on all four edges (checked one by one in `prerequisite_sentences` below).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in any `prerequisite` field. PASS.

### prerequisite_sentences

Check 6, edge by edge, four-point test.

**E1 — `lodging_ext_reservation_deposit` ← `lodging_ext_stay_rate_posting`**
`policy_source`: *"The deposit asked for is fixed only after the folio carries the room rate posted for every night of the stay."*
1. Verbatim in the **blocked** policy's own `rule` (sentence 4 of `lodging_ext_reservation_deposit.rule`). ✓
2. Ordering connective: **"only after"**, joining this policy's own result ("the deposit asked for") to what it waits on. ✓
3. Declared `form: state`; what it waits on is *"the folio carries the room rate posted for every night of the stay"* — a record-visible state in the words the folio table and `find_lodging_folio_entries` use, with no performer and no tool. ✓
4. Names no tool, no policy id, no snake_case token, no row id. ✓
Strength/scope: the `condition` — *"The folio of the reservation carries a room rate entry covering every night of the stay"* — is the same fact, neither broader nor narrower. ✓
Single writer of the waited-on state: exactly one write in this difficulty creates a folio entry that "carries the room rate posted", namely `post_stay_room_charge_ee3504ba` (the only tool writing `event_type="lodging_room_charge"`). `settle_departure_folio_07fd1088` writes `charge_category="room_rate"` but under `event_type="lodging_payment"`, which is a payment and not a room rate posted. ✓
Derivation (single reading): the sentence says the deposit waits on a folio that carries the room rate for every night → the records show whether such an entry stands → the only policy whose own rule describes posting that entry is `lodging_ext_stay_rate_posting` ("The room rate for a stay is worked out night by night and posted to the folio as a single entry covering every night of the stay") → its `target_tool` is the resolving action. One reading only.
No second wording, no tool name, no other policy's id anywhere in `lodging_ext_reservation_deposit.rule`; `lodging_ext_stay_rate_posting.rule` does **not** restate the sentence. ✓

**E2 — `lodging_ext_departure_settlement` ← `lodging_ext_early_departure_charge`**
`policy_source`: *"The amount collected at departure is fixed only after the folio carries the room rate retained for the nights of the stay the party gave up."* — in the blocked rule ✓; "only after" ✓; state form, record-visible ✓; no tool/id/token ✓; `condition` is the same scope ✓. Single writer: only `post_early_departure_charge_bb461064` writes `event_type="lodging_fee_charge", charge_category="cancellation_fee"`, and only `lodging_ext_early_departure_charge.rule` describes "the room rate retained … for the nights of the stay the party gave up". ✓

**E3 — `lodging_ext_departure_settlement` ← `lodging_ext_departure_service_charge`**
`policy_source`: *"It is worked out only once the folio carries the departure services charge the stay owes for servicing the unit and for its nightly extras."* — in the blocked rule ✓; "only once" ✓; state form ✓; no tool/id ✓; scope matches ✓. Single writer: `post_departure_service_charge_1468621e` (the only tool writing `charge_category="cleaning_fee"`), described only by `lodging_ext_departure_service_charge.rule`. ✓

**E4 — `lodging_ext_departure_settlement` ← `lodging_ext_stay_resort_charge`**
`policy_source`: *"Before it is worked out, the folio must carry the resort charge owed for the nights of the stay."* — in the blocked rule ✓; "Before" ✓; state form ✓; no tool/id ✓; scope matches ✓. Single writer: `post_stay_resort_charge_f79fa34a` (the only tool writing `event_type="lodging_resort_fee"`), described only by `lodging_ext_stay_resort_charge.rule`. ✓

Three sentences in one rule, one waited-on state each, three distinct writes — the reader resolves each hop separately and the order among the three is left to the records, as required.

Cross-problem orders stated in a rule that ground no declared edge: none found. The ordering language elsewhere in the six rules is intra-policy sequencing of the steps of one computation ("The passholder reduction is taken first … next … third … last"; "reduced in a fixed order: first … then … then … and last"), which states no order between problems. One base sentence states a cross-problem order (`lodging_deposit_terms`: "A reservation becomes firm only once the deposit has cleared") but no task's tree rests on it and the extended charter never grounds an edge on it — recorded as an observation only, at **F-10**.

### override_declarations

Check 1's **finding half**, sentence by sentence over each `base_policy_refs` entry of all six extended policies. Each affected task's file demonstrates the consequence against its own world.

`lodging_ext_stay_rate_posting` (refs `lodging_agg_household_stay_pricing`, `lodging_rate_and_fees`), 5 `overwrite` entries:
- rate_and_fees s1 "The room rate is posted night by night rather than as one figure for the stay…" → **declared** (#1).
- rate_and_fees s2 "A night falling inside the published holiday window takes the holiday rate… judged on the night occupied and never on the arrival date." → **declared** (#2).
- rate_and_fees s3 **"Guests beyond the unit type's standard occupancy add the extra person charge to each night they stay."** → extended's `extra_person_nightly` ladder charges `P('extra_person_nightly_usd') * K('family_extra_person_pct')/100` (60 %) or `* K('full_house_extra_person_pct')/100` (125 %) on two of its three tiers. **NOT declared.** → **F-1**.
- rate_and_fees s4–s7 and agg s1/s5/s6 govern other quantities; extended follows them.
- agg s2 "The season passholder reduction is taken first, on the evidence of a pass held by the household standing in the active state on the arrival date." → **declared** (#3).
- agg s3 "The advance booking reduction is taken next where the reservation was recorded at least the unit type's advance period before arrival." → **declared** (#4).
- agg s4 "The length-of-stay reduction is taken last where the stay reaches the unit type's threshold in nights." → **declared** (#5); the new fourth (package) reduction is admitted by that replacement ("taken third", leaving the last slot open) and is not treated as a further undeclared override.

`lodging_ext_reservation_deposit` (refs `lodging_deposit_terms`, `lodging_rate_and_fees`, `lodging_stay_operations`), 1 `overwrite` entry:
- deposit_terms s2 "The deposit is the unit type's share of the room rate for the whole stay, worked out on the rate after every reduction and rounded to the cent." → **declared**. Because the whole sentence is named, both the share and the base it is taken on are released, so the `share_pct` ladder (20 % / 27.5 % / the unit type's share) is covered by the declaration.
- deposit_terms s1/s3/s4/s5/s6/s7 → inherited, extended follows them.
- **stay_operations s2 "The incidental hold is taken at check-in against the lead guest's own payment method and is not taken against a third party's card."** → extended's rule collects the incidental hold **with the deposit, in advance of arrival**: "the whole of the unit type's incidental hold is collected with it in advance against incidentals", and the amount enters the scored figure through `incidental_prepay`. **NOT declared.** → **F-2**.
- rate_and_fees: extended reads `resort_fee_nightly_usd` into the deposit *basis* on the holiday tier without posting a resort charge; no base sentence is contradicted.

`lodging_ext_stay_resort_charge` (refs `lodging_rate_and_fees`, `lodging_agg_household_stay_pricing`), 1 `overwrite` entry:
- rate_and_fees s4 "The nightly resort charge is posted for every night occupied and is not reduced by any discount, because it pays for services the party has whether or not they use them." → **declared**, and the declaration covers both the nights basis and the member/part-member shares (it is exactly the "not reduced by any discount" clause). The holiday supplement raises rather than reduces the charge and the superseded sentence is gone, so it is not treated as a further undeclared override.
- rate_and_fees s5 "The resort charge is posted only while the reservation stands in the checked_in or checked_out state." → inherited, not weakened.

`lodging_ext_departure_service_charge` (refs `lodging_stay_operations`, `lodging_rate_and_fees`), **`overwrite: []`**:
- **rate_and_fees s6 "The housekeeping charge is posted once on departure and the parking charge nightly for spaces beyond those included."** → extended's `housekeeping_amount` ladder posts `P('cleaning_fee_usd') * K('deep_clean_share')` (1.5×) or `* K('extended_clean_share')` (1.25×) on two of three tiers, and adds a further `turnover_element` of `P('cleaning_fee_usd') * K('full_turnover_share')` (0.3×) or `* K('half_turnover_share')` (0.15×) per guest beyond standard occupancy; its `parking_nightly` ladder takes `P('parking_nightly_usd') * (1 - K('passholder_parking_share'))` (0.75×) on its first tier. **Neither is declared.** → **F-3**.
- stay_operations s4 "Charges the party raises around the mountain are posted to the folio as they arise, each against the outlet it arose at" → extended adds a 12 %/18 % service charge on the in-room-dining charges standing on the folio. Base neither provides nor forbids it; no base sentence reaches a different conclusion on a quantity base fixes, so this is new ground, not an override. Recorded as an observation at **F-11**.
- stay_operations s6 "Housekeeping runs at the unit type's frequency, and a party asking for more is charged for the extra visits." → extended's shares are not "extra visits", but this sentence fixes no amount; not counted as a conflict.

`lodging_ext_early_departure_charge` (refs `lodging_modification`, `lodging_rate_and_fees`, `lodging_cancellation`), 1 `overwrite` entry:
- rate_and_fees s8 "A night the party leaves early is still charged where the departure falls inside the cancellation terms of the stay." → **declared**.
- cancellation s4 "After the deadline the unit type's late cancellation nights of room rate are retained, worked out at the rate of the first nights of the stay, and the remainder comes back." → extended's `retained_nightly` tier 1 prices at the **nightly average of the room rate standing on the folio**, not "the rate of the first nights of the stay". Not declared; recorded at **F-7** together with the anchor change, because the two are the same undeclared reuse of base machinery.
- modification s2 "A change is accepted only when it is recorded on or before the unit type's change deadline, which is its change notice period counted back in calendar days from the **arrival date**." → extended reuses `change_notice_days` but counts it back from the **departure date** ("raised more than the unit type's change notice period in calendar days before the departure date on the reservation"). Not declared → **F-7**.
- modification s4 "Each change carries the unit type's change fee, whatever the direction of the change." → extended posts no change fee for an early departure; recorded as an observation at **F-12**.
- modification s9 "A fee is posted to a folio only while the reservation stands in the deposit_pending, confirmed, checked_in, checked_out, cancelled or no_show state." → inherited, not weakened.

`lodging_ext_departure_settlement` (ref `lodging_checkout_settlement`), 1 `overwrite` entry:
- checkout_settlement s2 "The deposit already taken is applied against the folio first, then any lodging credit the household holds, and the remainder is taken from the payment method on file." → **declared**; the four-step order replaces it and the merged semantics are unique.
- checkout_settlement s1/s3/s4/s5/s6/s7 → inherited, extended follows them (the deposit-larger-than-folio case is restated identically in extended's first `deposit_set_against` tier).

No **anonymous intermediate factor**, **0/1 multiplier** or **dropped branch** was found beyond what F-1 to F-3 already name. No rule, `compute_basis` or note calls a base output a "wrong value" or an "algorithm to avoid".

### factor_ladders

Structure only. 29 declared factors over 6 policies.

| policy | factors | parameter | method | ladder tiers | multi-source | cross_difficulty declared |
| --- | --- | --- | --- | --- | --- | --- |
| `lodging_ext_stay_rate_posting` | 6 | 5 | 1 | 3,3,3,3,3,3 | `passholder_reduction`, `package_reduction` | passes, lessons |
| `lodging_ext_reservation_deposit` | 4 | 3 | 1 | 3,3,3,3 | `protected_deposit_share`, `incidental_prepay_share` | insure, dining |
| `lodging_ext_stay_resort_charge` | 4 | 3 | 1 | 3,3,3,3 | `member_resort_nightly` | passes |
| `lodging_ext_departure_service_charge` | 5 | 4 | 1 | 3,3,3,3,3 | `in_room_dining_service_share`, `passholder_parking_rate` (tier 1) | passes, dining |
| `lodging_ext_early_departure_charge` | 6 | 4 | 2 | 3,3,3,3,3,3 | `retained_nightly_rate`, `protection_claim_retention` (tier 1) | passes, insure |
| `lodging_ext_departure_settlement` | 4 | 3 | 1 | 3,3,3,**4** | `disputed_charges_held_back`, `dining_plan_met_charges`, `resort_credit_draw` | passes (also reads dining, tickets) |

Counts are inside the bounds everywhere: 4–6 factors per policy, ≥2 `parameter`, ≥1 `method`, every ladder ≥3 tiers counting the fall-through.

Binding-set disjointness: within each policy the `bindings` lists are pairwise disjoint — script-verified, no binding name appears under two factors of one policy. Every `decides` names an **input** of `result`, never `result` itself.

Every tier's condition and every tier's value/method was located in the owning `rule` (see `rule_compute_equivalence` for the four restatements checked by hand) and as a branch of the `decides` binding in `compute`; no tier lives only in `compute`, and no branch of a `decides` binding lacks a tier.

Business realism of conditions and outcomes: a season pass on the household account, a dining plan, a school booking, a rental agreement, a protection plan and its claim decision, a dog in the unit, a party filling the unit's maximum occupancy, parking beyond what is included, a folio dispute standing with the desk, a departure recorded earlier than the booked one — all are things a mountain lodging operator actually weighs for these quantities, and none of them holds of every customer who reaches the write. The fall-through outcomes are in every case the published tariff itself (the unit type's nightly rate, its deposit share, its resort charge, its housekeeping charge, its parking charge, its extra-person charge), which is what such a business gives an ordinary guest. No straw-man default was found.

Two structural defects were found and are carried as findings: **F-4** (a tier written as two) and **F-8** (a mislabelled `method`). Whether each factor **bears weight** is a fact about one world and is decided in each task's `factor_weight`.

### findings

Ordered; each names the tasks it bears on. Consequences against a particular world are demonstrated in the named task's file, not here.

---

**F-1 — SOURCE-POLICY RED (undeclared override): the extra-person charge multiplier.** Bears on **task 0**.

- *Symptom.* Base and extended reach different amounts for the same quantity — what a guest beyond the standard occupancy adds to each night — and `lodging_ext_stay_rate_posting.overwrite` does not name the base sentence.
- *Root cause.* The author added an `occupancy_charge_rate` ladder over `P('extra_person_nightly_usd')` without declaring that it replaces base's flat charge.
- *Evidence.* Base `lodging_rate_and_fees.rule`: *"Guests beyond the unit type's standard occupancy add the extra person charge to each night they stay."* Extended `lodging_ext_stay_rate_posting.rule`: *"Where the party is larger than the unit type's standard occupancy and carries children as well as adults, each guest beyond the standard occupancy is charged at the family share of the unit type's extra person nightly charge for every night of the stay."* `compute.extra_person_nightly` = `P('extra_person_nightly_usd') * K('family_extra_person_pct') / 100` with `params.family_extra_person_pct = 60.0`. `overwrite` carries 5 entries, none of which names the base sentence.
- *Demonstrated consequence.* See `0.md` § `policy_self_consistency`: on task 0's world the base sentence and the extended sentence give two different scored values for `room_charge_amount_usd`.
- *Affected artifact.* `env/env_0004_ski_resort_operator/tasks/lodging_reservations_desk/lodging.extended.yaml`, `extended_policies[0].overwrite` (missing entry), `extended_policies[0].rule` (last three sentences), `extended_policies[0].compute.extra_person_nightly`.

---

**F-2 — SOURCE-POLICY RED (undeclared override): when the incidental hold is taken.** Bears on **task 0**.

- *Symptom.* Base says the incidental hold is taken **at check-in**; extended collects it **with the deposit, in advance**, and the amount enters the scored deposit figure. `lodging_ext_reservation_deposit.overwrite` names only the deposit-amount sentence of `lodging_deposit_terms` and says nothing about `lodging_stay_operations`.
- *Root cause.* `lodging_stay_operations` is listed in `base_policy_refs` but its incidental-hold sentence was never swept.
- *Evidence.* Base `lodging_stay_operations.rule`: *"The incidental hold is taken at check-in against the lead guest's own payment method and is not taken against a third party's card."* Extended `lodging_ext_reservation_deposit.rule`: *"The unit type's deposit share of that amount is taken, and the whole of the unit type's incidental hold is collected with it in advance against incidentals."* `compute.result` = `RND(share_amount + incidental_prepay - advance_credit, 2)`; `base_policy_refs` = `["lodging_deposit_terms", "lodging_rate_and_fees", "lodging_stay_operations"]`; `overwrite` has 1 entry, `base_policy: lodging_deposit_terms`.
- *Demonstrated consequence.* See `0.md` § `policy_self_consistency`: the base reading and the extended reading give two different scored values for `deposit_amount_usd`.
- *Affected artifact.* `lodging.extended.yaml`, `extended_policies[1].overwrite` (missing entry), `extended_policies[1].rule` (sentence 2), `extended_policies[1].compute.incidental_prepay` / `.result`.

---

**F-3 — SOURCE-POLICY RED (undeclared override): the housekeeping and parking amounts.** Bears on **task 1**.

- *Symptom.* `lodging_ext_departure_service_charge` carries `overwrite: []`, yet it multiplies base's housekeeping charge by 1.5 or 1.25, adds a further 0.3× or 0.15× of it per extra guest, and takes base's nightly parking charge at 0.75× for a passholder.
- *Root cause.* An empty `overwrite` list was left in place while three ladders were written over quantities base fixes by name.
- *Evidence.* Base `lodging_rate_and_fees.rule`: *"The housekeeping charge is posted once on departure and the parking charge nightly for spaces beyond those included."* (`params.per_tier[*].cleaning_fee_usd`, `.parking_nightly_usd` are base's own). Extended `lodging_ext_departure_service_charge.rule`: *"Where the reservation records one or more dogs, or the folio shows the party occupied at least that threshold in nights, but not both, the extended clean share of that charge is taken."* and *"Where the reservation asks for more parking spaces than the unit type includes and a season pass stands active for the season of the stay on the household account, that nightly charge is taken less the passholder parking share."* `params`: `deep_clean_share: 1.5`, `extended_clean_share: 1.25`, `passholder_parking_share: 0.25`, `full_turnover_share: 0.3`, `half_turnover_share: 0.15`. `overwrite: []`.
- *Demonstrated consequence.* See `1.md` § `policy_self_consistency`: on task 1's world each undeclared deviation gives a different scored value for `service_charge_amount_usd`.
- *Affected artifact.* `lodging.extended.yaml`, `extended_policies[3].overwrite` (empty), `extended_policies[3].rule`, `extended_policies[3].compute.housekeeping_amount` / `.parking_nightly` / `.turnover_element`.

---

**F-4 — SOURCE-FACTOR RED (unreal ladder): `payments_already_collected` has a tier written as two.** Bears on **task 0** (structure only; the tier taken there is tier 2, so the scored figure does not move).

- *Symptom.* The ladder's second and third tiers select the same outcome in every world the third tier can apply to.
- *Root cause.* The third tier restates the second tier evaluated at zero instead of dividing customers differently.
- *Evidence.* `extended_policies[1].factors[3].ladder`: tier 2 `when: "the folio carries payments already collected against the stay totalling less than the share worked out"`, `value: "paid_to_date"`; tier 3 `when: "otherwise"`, `value: "0"`. `compute.advance_credit` = `share_amount if paid_to_date >= share_amount else (paid_to_date if paid_to_date > 0 else 0)`. The only world tier 3 reaches is `paid_to_date == 0`; there tier 2's value `paid_to_date` **is** `0`, i.e. exactly tier 3's value, and tier 2's stated condition ("totalling less than the share worked out") already covers it. Two tiers, one outcome.
- *Demonstrated consequence.* The ladder has two real tiers, not three, so it is below the three-tier floor the charter claims for it.
- *Affected artifact.* `lodging.extended.yaml`, `extended_policies[1].factors[3].ladder`, `extended_policies[1].rule` (last three sentences), `extended_policies[1].compute.advance_credit`.

---

**F-5 — SOURCE-POLICY RED (rule/compute equivalence): the settlement rule states no status for the credit pots, the compute requires one.** Bears on **task 1**.

- *Symptom.* `compute` filters the season-pass credit by `status='active'` and the ticket credit by `status='in_use'`; neither filter has any quotation in the rule, and the rule's own ladder states the condition without a status.
- *Root cause.* A status filter was written into `compute` and never carried back into the `rule`, so the prose admits a reading the compute rejects.
- *Evidence.* `extended_policies[5].rule`: *"Where the household holds resort credit standing on a season pass record for the season of the stay and credit standing on a ticket order for that season as well, the credit on the pass record is drawn first and only what it does not cover is drawn from the ticket order."* — no status anywhere in the four sentences of that ladder, and no status in `factors[3].ladder[*].when`. `compute.pass_credit_amount` = `CFIELD('passes', 'pass_credit_usd', status='active', season_code=F('season_code')) or 0`; `compute.ticket_credit_amount` = `CFIELD('tickets', 'ticket_credit_usd', status='in_use', season_code=F('season_code')) or 0`. `compute_basis.pass_credit_amount` quotes *"Where the household holds resort credit standing on a season pass record for that season and none standing on a ticket order, the credit on the pass record is drawn."* — a sentence that says nothing about `active`. Contrast the same charter's other pass reads, which do state it: `extended_policies[2].rule` *"Where a season pass stands active for the season of the stay on the household account…"*.
- *Demonstrated consequence.* See `1.md` § `policy_self_consistency`: the rule as written and the compute give two different scored values for `settlement_amount_usd`.
- *Affected artifact.* `lodging.extended.yaml`, `extended_policies[5].rule` (the resort-credit ladder), `extended_policies[5].compute.pass_credit_amount` / `.ticket_credit_amount`, `extended_policies[5].factors[3].ladder`.

---

**F-6 — observation (rule/compute equivalence): the resort holiday supplement is judged over nights that are not the nights being charged.** Bears on **task 1** (no consequence there).

- *Symptom.* The rule tests "the nights **being charged**"; the compute counts holiday nights over the nights the **reservation covers**.
- *Evidence.* `extended_policies[2].rule`: *"Where every night being charged falls inside the unit type's published holiday window, the holiday share of the nightly charge is added to it for each night charged."* `compute.nights_in_holiday` = `MX(0, MN(nights_covered, DAYS(F('arrival_date'), P('holiday_window_end')) + 1) - MX(0, DAYS(F('arrival_date'), P('holiday_window_start'))))` — keyed to `nights_covered`, not to `charged_nights`; `compute.every_charged_night_in_holiday` = `nights_in_holiday >= charged_nights`. Where the arrival night falls **before** the holiday window, the first charged nights are outside it while `nights_in_holiday >= charged_nights` can still hold, so the compute would report "every charged night in the window" for a stay whose charged nights are largely outside it.
- *Why an observation and not a red light.* Task 1's arrival (2026-12-26) is inside the window, so the compute and the rule agree there and no consequence can be demonstrated on either task's world.
- *Affected artifact.* `lodging.extended.yaml`, `extended_policies[2].compute.nights_in_holiday` / `.every_charged_night_in_holiday` / `.some_charged_night_in_holiday`.

---

**F-7 — observation (undeclared reuse of base machinery in the early-departure policy).** Bears on **task 1** (no consequence there).

- *Symptom.* Two provisions of base are reused with a changed anchor and a changed rate basis, and neither change is declared in `overwrite`.
- *Evidence.* (a) Base `lodging_modification.rule` + its `change_notice_deadline.temporal_basis`: `anchor_event: "the arrival date"`, `anchor_source: "lodging_holdings.arrival_date"`, `duration_source: "variants.change_notice_days"`. Extended `lodging_ext_early_departure_charge.rule`: *"…was raised more than the unit type's change notice period in calendar days before the departure date on the reservation…"*; `compute.notice_lead_days` = `DAYS(notice_date, F('departure_date'))`. (b) Base `lodging_cancellation.rule`: *"After the deadline the unit type's late cancellation nights of room rate are retained, worked out at the rate of the first nights of the stay…"*; extended tier 1 prices at the nightly **average** of the posted room rate (`compute.retained_nightly` = `posted_room_rate_a / MX(1, posted_room_nights_a)`). `overwrite` carries one entry, against `lodging_rate_and_fees` only.
- *Why an observation and not a red light.* On task 1's world neither divergence changes the scored figure: the request was raised after arrival, so both anchors land on the same tier; and every posted room-rate entry is 476.10, so the nightly average equals the rate of the first night. Recorded because the deviation is real and undeclared, not because it can be shown to cost this suite a number.
- *Affected artifact.* `lodging.extended.yaml`, `extended_policies[4].overwrite`, `extended_policies[4].rule`, `extended_policies[4].compute.notice_lead_days` / `.retained_nightly`.

---

**F-8 — SOURCE-FACTOR RED (mislabelled effect): `protection_claim_retention` is a `parameter` declared as a `method`.** Bears on **task 1**.

- *Symptom.* A factor labelled `method` whose three tiers only substitute a different number into one unchanged formula.
- *Root cause.* The label was set from the prose ("what is charged") rather than from what the tiers do to the algorithm.
- *Evidence.* `extended_policies[4].factors[5]`: `"effect": "method"`, `"decides": "retention_share"`. `compute.retention_share` = `K('allowed_claim_retention_share') if … else (K('open_claim_retention_share') if … else 1)` with `params.allowed_claim_retention_share = 0.0`, `params.open_claim_retention_share = 0.5`. `compute.result` = `RND((retained_with_window + occupancy_retained) * retention_share, 2)` — the same expression on every tier; only the multiplier 0.0 / 0.5 / 1 changes. Contrast the same policy's genuine method, `nights_given_up_basis`, whose tiers select three different counting rules.
- *Demonstrated consequence.* Struck out as a method, `lodging_ext_early_departure_charge` declares 5 `parameter` factors and 1 `method`; the policy still meets the floor through `nights_given_up_basis`, so the count survives, but the declared `method` count (2) is not what the charter has, and a reader told this is a method looks for an algorithm the charter never varies.
- *Affected artifact.* `lodging.extended.yaml`, `extended_policies[4].factors[5].effect`.

---

**F-9 — observation: an ordering word in every tool's `lodging_id` Arg.** Bears on both tasks (no consequence).

- *Evidence.* `task_tools.py`, four agent tools: *"read it from the reservation record returned by the lodging reservation lookup **before the call**"*; two user tools: *"it is read from the reservation record the desk has on screen and given to the household **before the call**"*.
- *Why an observation.* The phrase carries the ordering word "before", but it states where a **parameter value** comes from, not the position of a business act in a sequence, and it names no tool (the "lodging reservation lookup" is a generic description). It discloses no prerequisite and no order between problems.
- *Affected artifact.* `task_tools.py`, the `lodging_id` Args entry of all six tools.

---

**F-10 — observation: a base sentence stating a cross-problem order that grounds no edge.** Bears on neither task's tree.

- *Evidence.* Base `lodging_deposit_terms.rule`: *"A reservation becomes firm only once the deposit has cleared."* — an ordering sentence between the deposit and the confirmation. No extended policy declares an edge on it, and no task's tree rests on it (no task claims `lodging_confirm`). Per check 6 a base sentence may not ground an edge; none does, so it is recorded here only.
- *Affected artifact.* `lodging.extended.yaml`, base `policies[3].rule`.

---

**F-11 — observation: the in-room-dining service charge is new ground, not an override.** Bears on **task 1**.

- *Evidence.* `extended_policies[3].rule`: *"Where the folio carries incidental charges raised at the in-room dining outlet for the stay and no dining plan stands active for that season, the standard service share of those charges is added."* (`standard_service_share: 0.18`). No base sentence of `lodging_stay_operations` or `lodging_rate_and_fees` fixes a service charge on folio incidentals, so base reaches no conflicting conclusion; the element is added rather than substituted. Recorded because the element is invisible to a reader of base alone, which is a render-stage concern rather than a policy conflict.
- *Affected artifact.* `lodging.extended.yaml`, `extended_policies[3].rule`, `.compute.dining_service_charge`.

---

**F-12 — observation: base's change fee is not posted on an early departure.** Bears on **task 1**.

- *Evidence.* Base `lodging_modification.rule`: *"Each change carries the unit type's change fee, whatever the direction of the change."* (`change_fee_usd` = 45.00 for Slopeside Studio). Task 1's world carries a `date_change` request standing `accepted_pending_confirmation`, and no extended policy posts a change fee. Whether the early departure is "a change" in base's sense is not settled by any sentence of the charter; the extended early-departure policy treats it as a departure rather than as a modification.
- *Why an observation.* It could add a write, not a second value for a scored parameter, and the charter's silence is genuine rather than contradictory.
- *Affected artifact.* `lodging.extended.yaml`, base `policies[6].rule`; `extended_policies[4]`.

---

**F-13 — observation: the settlement rule's "every charge standing on the folio" is wider than the compute's four event types.** Bears on **task 1** (no consequence).

- *Evidence.* `extended_policies[5].rule`: *"…what is still to be collected on it: every charge standing on the folio less every payment already collected against it…"*. `compute.folio_charges` sums exactly four event types — `lodging_room_charge`, `lodging_resort_fee`, `lodging_incidental_charge`, `lodging_fee_charge` — and excludes `lodging_deposit_charge`, whose rows carry `charge_category: "deposit"` in the folio table.
- *Why an observation.* The same rule then says the deposit "is **set against** what is left", which treats the deposit as a credit and makes counting it as a charge incoherent; a careful reader lands on the compute's reading. Recorded because "every charge" is, on its face, wider than four event types.
- *Affected artifact.* `lodging.extended.yaml`, `extended_policies[5].rule` (sentence 1), `.compute.folio_charges`.

## closing_checklist

Written after both tasks' `source_gt_comparison` sections were on disk. **The difficulty does not close.** The checklist is recorded in full so that what holds is separated from what does not.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | **holds** — `0.md`, `1.md`, `_difficulty.md` in `env/env_0004_ski_resort_operator/audits/policy_task/lodging_reservations_desk/` |
| old revisions traceable | **holds** — this is revision 1; no prior audit of this difficulty exists, nothing was rewritten |
| every comparison section carries a PASS | **does not hold** — `0.md` § `source_gt_comparison` carries SOURCE-POLICY RED, SOURCE-CHAIN RED and SOURCE-FACTOR RED; `1.md` carries SOURCE-POLICY RED and SOURCE-FACTOR RED |
| this difficulty's extended policies fully covered, task scopes pairwise disjoint | **holds** — task 0 claims `{lodging_ext_stay_rate_posting, lodging_ext_reservation_deposit}`, task 1 claims the other four; each scope spans its whole tree (root plus every prerequisite problem); 6 of 6 covered, intersection empty |
| task tools and GT closed | **holds** — 6 tools, each bound to exactly one policy, each called by exactly one task; the REPLAY gate reports `clos == init` and `match == True` on both tasks |
| each task tool uses an independently generated, frozen uuid8 | **holds** — see § `action_binding_and_uuids` |
| every tree has 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle | **holds** — task 0: 1 problem, 1 `value_input` (floor 1), user write `authorise_reservation_deposit_3e63cb2f`; task 1: 3 problems, 3 `value_input` (floor 2), user write `settle_departure_folio_07fd1088` |
| the `prerequisite` edges of the whole difficulty form a DAG, with no cycle created by cross-task references | **holds** — four edges, two components, depth 1 each, no edge crosses between the components |
| every computation declares 4–6 factors with ≥2 `parameter` and ≥1 `method`, ladders of ≥3 tiers stated in full in the rule | **as declared, holds** (§ `factor_ladders`); **in substance it does not** for `lodging_ext_early_departure_charge`, which after F-8 and `1.md` T1-1 is left with five `parameter` factors and no genuine `method`, and for `lodging_ext_reservation_deposit`'s `payments_already_collected`, whose third tier is its second restated (F-4) |
| per task ≥1 multi-source and ≥1 cross-difficulty factor | **holds** — task 0: 4 multi-source, 4 cross-difficulty (`passes`, `lessons`, `rentals`, `insure`, `dining`, all seeded); task 1: 8 multi-source, 4 cross-difficulty (`passes`, `dining`, `insure`, `tickets`, all seeded) |
| tiers distinct in outcome; conditions and outcomes ones the line of business actually holds | **does not hold in one place** — F-4; otherwise holds |
| every factor proved to bear weight against an honest baseline, the baseline alone giving a definite number different from gold | **does not hold** — `1.md` T1-1: `nights_given_up_basis` leaves the scored value unchanged when its baseline is taken as `baseline.rule` states it, and the declared `baseline_result` of 0.00 is not the 2116.00 that `baseline.rule` gives on that world. The other 28 factors do bear weight, with whole-baseline numbers 7133.00 / 989.09 (task 0) and 72.00 / 304.00 / 3299.45 (task 1), each definite and different from gold |
| no tier read off a stamp | **does not hold** — `0.md` T0-1: `lodging_holdings.rate_plan = "peak"` names and agrees with the `straddling_window_pricing` tier |
| proof fields assert only what the world produces | **does not hold** — `0.md` T0-2: `prerequisite_closure.edge_load_bearing` states −250.00 where the world gives 250.00 |
| instantiation-stage gates re-run on the final form | **done, all green** (below) |

**Gate re-run on the final form**, from the repository root, `T = env/env_0004_ski_resort_operator/tasks/lodging_reservations_desk`:

```
.venv/bin/python skills/erl-task-instantiate/scripts/check_extended.py    $T   -> EXTENDED OK
.venv/bin/python skills/erl-task-instantiate/scripts/check_task_tools.py  $T   -> TASK TOOL CONTRACT OK
.venv/bin/python skills/erl-task-instantiate/scripts/replay_tasks.py      $T --check
                                   0.json 13 acts det=True nonvac=True errs=0 clos=17 init=17 match=True
                                   1.json 17 acts det=True nonvac=True errs=0 clos=27 init=27 match=True   -> REPLAY OK
.venv/bin/python skills/erl-task-instantiate/scripts/check_solvability.py $T   -> SOLVABILITY OK
.venv/bin/python skills/erl-task-instantiate/scripts/check_compute.py     $T   -> COMPUTE OK (branches 40/77, steps 13/17)
.venv/bin/python skills/erl-task-instantiate/scripts/check_grounding.py   $T   -> GROUNDING OK
.venv/bin/python skills/erl-task-instantiate/scripts/check_cross_fire.py  $T   -> SCOPE OK
```

`replay_tasks.py` was run with `--check`, so no `db_closure` was written back. The gates are green on the same artifacts that carry the findings above, which is the point of the manual audit: scripts prove structure, references and parsability, and none of the eight defects recorded here is a structural one.

**Difficulty verdict.**

| relationship | task 0 | task 1 |
| --- | --- | --- |
| policy self-consistency | **SOURCE-POLICY RED** (F-1, F-2) | **SOURCE-POLICY RED** (F-3, F-5) |
| the problem tree holds | **SOURCE-CHAIN RED** (T0-2; the tree itself is sound) | **PASS** |
| factors bear weight | **SOURCE-FACTOR RED** (T0-1) | **SOURCE-FACTOR RED** (T1-1, with F-8) |
| unique solution | **PASS** | **PASS** |

Both tasks' scored solutions were reproduced blind, figure for figure — every `expected`, every `baseline_result`, every `factor_sensitivity` entry and every `edge_load_bearing` figure but one — so the suite is solvable and its arithmetic is sound. What fails is the relationship layer: two quantities each admit a second defensible reading the charter never resolves (F-1/F-2 on task 0, F-3/F-5 on task 1), one tier is legible off the seed rather than off the rule (T0-1), one factor's weight is manufactured by a straw-man baseline and leaves its computation without a genuine `method` (T1-1 with F-8), one ladder has a tier written as two (F-4), and one proof field asserts a figure the world does not produce (T0-2).

---

# revision_2

Re-audit round 2 of the same difficulty. Revision 1 above is left exactly as written, including the parts this round supersedes.

## charter_global_frozen (revision 2)

- Auditor: the same independent source-layer auditor. This round is **not blind**: round 1's GT has been seen, so the round-2 derivation is a re-derivation and is judged as such. What it is not is a check against the reworked record — every figure below was recomputed from the policy and the world before any round-2 GT field was read.
- Freeze time of this section: 2026-09-17, written **before any round-2 GT field of either task was read**.
- Freeze hashes, verified by the auditor with `sha256sum` against the rebuilt masked view:

| artifact | revision 1 | revision 2 | |
| --- | --- | --- | --- |
| `lodging.extended.yaml` | `77389c0b6e7c12bb` | `10b77a068f7f5f36` | **changed** |
| `task_tools.py` | `843389fdabdcbf91` | `604959686270553b` | **changed** |
| `tasks/0.json` (masked) | `2461652bc7e8657c` | `3292f6419bae96cb` | **changed** |
| `tasks/1.json` (masked) | `6472376a9c846086` | `6472376a9c846086` | unchanged |

Both shared inputs moved, so **every charter-global section is re-derived in full** below rather than carried forward by reference. Task 1's masked world is byte-identical to round 1's, but its policy is not, so its per-task sections are re-derived too.

- Fields permitted and fields masked: as revision 1. The auditor read the task files only from the rebuilt masked root until both revision-2 per-task derivations were on disk.
- Entry condition: the coordinator supplied the re-run gate snapshot (EXTENDED / TASK-TOOL-CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; TRACEABILITY unchanged pre-render). The COMPUTE line is unchanged from round 1 in every count (`0.json comps=2 fact=10 xfac=4 hist=3 brch=40 step=13`, `1.json comps=4 fact=19 xfac=7 hist=36 brch=77 step=17`), which is consistent with a rework that changed values and wording without changing shape.

### policy_conflict_scan (revision 2)

**Base section: unchanged and still verbatim.** Every top-level key of `blueprint/products/lodging.yaml` — `category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies` — compares equal under a canonical JSON dump to the copy in the reworked `lodging.extended.yaml`, and equal to the round-1 copy. Script-verified, 0 differences. The rework did not rewrite base, which is the first thing that could have gone wrong and did not. The seven variant tariffs are byte-identical to round 1's as well, so no figure moved because a published parameter was quietly retuned.

**Extended section: what moved.**

| policy | `overwrite` | other changed keys |
| --- | --- | --- |
| `lodging_ext_stay_rate_posting` | 5 → **6** | none |
| `lodging_ext_reservation_deposit` | 1 → **2** | `rule`, `compute_basis`, `factors` |
| `lodging_ext_stay_resort_charge` | 1 → 1 | `rule`, `compute`, `compute_basis`, `factors` |
| `lodging_ext_departure_service_charge` | **0 → 1** | `rule`, `compute_basis` |
| `lodging_ext_early_departure_charge` | 1 → **2** | `rule`, `compute`, `compute_basis`, `params`, `factors` |
| `lodging_ext_departure_settlement` | 1 → **2** | `rule`, `compute_basis`, `baseline`, `factors` |

Fourteen `overwrite` entries in all, which matches the reworker's claim.

The rest of the scan reaches the same conclusions as revision 1 § `policy_conflict_scan` and is re-derived here rather than cited: six pairwise-distinct `subject` event types and six pairwise-distinct `computes` names, so no two extended policies decide the same quantity; the inherited base eligibility gates (`deposit_chargeable_state`, `resort_fee_stay_state`, `fee_bearing_reservation_state`, `deposit_apply_state`) each govern one write and none collides; four distinct time anchors; six declared cross-category reads, all `branch` or `existence`. The `prerequisite` graph still has exactly two weakly-connected components, `{rate posting → deposit}` and `{resort, services, retention} → settlement`, disjoint and jointly covering all six policies.

**One time anchor changed, and it is an improvement.** Revision 1 recorded at F-7 that `lodging_ext_early_departure_charge` reused base's per-tier `change_notice_days` against a different anchor. The reworked policy declares its own flat charter constant `params.early_departure_notice_days = 7` and its rule now reads *"more than the early departure notice period in calendar days before the departure date"*. Base's parameter is no longer read by that compute. The charter therefore now carries five anchors, all distinct and each owned by the policy that uses it. One loose end remains inside the factor ladder — see **G-1** below.

### rule_compute_equivalence (revision 2)

Re-run binding by binding over all six reworked policies: **128 `compute` bindings, 128 `compute_basis` entries**, one per binding, with `set(compute_basis) == set(compute)` in every policy. Every `compute_basis` string is located **verbatim** in that policy's own `rule` after whitespace normalisation — script-verified, 0 misses. No basis sentence is invented and no rule sentence is left without an implementation.

`baseline.rule` was swept the same way for the first time this round: every sentence of every policy's `baseline.rule` is a sentence of that policy's `rule` (0 misses across six policies), and every key in `baseline.params` is a real parameter of the seven variants (0 unknown keys).

Both round-1 equivalence gaps are closed at the source:

- **F-6 closed.** `lodging_ext_stay_resort_charge` previously tested "the nights **being charged**" in the rule while the compute counted holiday nights over the nights the reservation covers. The rework renamed and re-based both faces so they agree: the rule now reads *"Where every night **the reservation covers** falls inside the unit type's published holiday window…"* and the compute now binds `every_night_in_holiday = nights_in_holiday >= nights_covered` and `some_night_in_holiday = nights_in_holiday > 0`, replacing `every_charged_night_in_holiday` / `some_charged_night_in_holiday`. The factor's `bindings` list and all three ladder tiers were updated to match. Rule, ladder and compute now say the same thing in the same terms, and the counter-example revision 1 constructed (an arrival before the window) no longer separates them.
- **F-5 closed.** `lodging_ext_departure_settlement` previously stated no state for the credit pots while the compute filtered `status='active'` and `status='in_use'`. The rework adds the governing sentence to the rule — *"Credit counts only where the record carrying it is itself live: a season pass record standing active for the season of the stay, or a ticket order standing in use for that season."* — and restates all three non-fall-through tiers with the state in them, in both the `rule` and `factors[3].ladder`. The compute is unchanged, which is the right direction of travel: the prose was brought to the implementation rather than the implementation loosened.
- **F-13 closed.** The settlement rule's *"every charge standing on the folio"* is now *"every room rate, resort, incidental and fee charge standing on the folio"*, matching the compute's four `SUM` terms exactly, and a new sentence settles the deposit's status outright: *"A deposit standing against the reservation is not one of those charges: it is money already held, and it is set against what is left rather than counted as something owed."* Both sentences are carried into `baseline.rule`, so a reader of the computation document alone gets the same scope.

**Ladder tiers against the rules.** Twenty-nine factors, 92 non-fall-through tiers. Seven tier `when` strings are not character-identical substrings of their rule; six of them are the same restatements checked by hand in revision 1 (`passholder_reduction` ×2, `straddling_window_pricing` ×2, `passholder_parking_rate` tier 2, `nights_given_up_basis` tier 2), each naming the condition the rule names. The seventh is new and is a defect the rework introduced — **G-1**.

### action_binding_and_uuids (revision 2)

Each `(target_tool, computes)` pair is still claimed by exactly one policy. The six uuid8s are **unchanged and correctly so** — they are frozen with their tools and must not be regenerated across a rework: `ee3504ba`, `3e63cb2f`, `f79fa34a`, `1468621e`, `bb461064`, `07fd1088`. All distinct, no shared 2-hex prefix, no pair differing in one tail character, no sequence.

Tool **bodies** are byte-identical to round 1: each is `ctx.find` / `round` / `ctx.make_id` / `ctx.create("lodging_folio", …)` / `ctx.update("lodging_holdings", …)` / `return`. **No tool reads a status, compares a date, tests whether another entry stands on the folio, raises, or returns a hint.** The tool layer still judges no prerequisite and no eligibility, so nothing regressed there.

**F-9 closed.** The phrase *"read it from the reservation record returned by the lodging reservation lookup **before the call**"*, present in all six `lodging_id` Args in round 1, is gone. A grep for `before | after | first | then | prior to | next` across the module now returns four hits, all of the form *"the reservation's folio balance **after** the posting"* inside the `Returns:` block — a description of the state the returned sentence reports, not an ordering instruction and not a reference to another act. No docstring names another tool or states a position in a sequence.

### prerequisite_graph (revision 2)

The `prerequisite` field of all six policies is **byte-identical to round 1** (script-compared). Re-verified in full against the reworked rules rather than carried forward:

- four edges, all `kind: value_input`, all `form: state`, no `fallback_reason` on any (correct for the state form, and the state form's priority is honoured everywhere because no action-form edge exists);
- every `problem` names another extended policy id in this file; none is a base policy; none self-refers; the graph is acyclic (two depth-1 chains, no edge between the components);
- each `gate` still names a real binding of the blocked policy's `compute` and not `result` — `posted_room_rate` is `compute[0]` of the deposit, `outstanding` is `compute[2]` of the settlement (script-verified against the reworked `compute` lists, since both policies' computes could have moved);
- each `resolved_by` is still the depended-on policy's own `target_tool`, and each named tool still creates the row the `effect` describes;
- each `policy_source` is still verbatim locatable in the **blocked** policy's own reworked `rule` (4 of 4), and is still absent from the depended-on policy's rule (0 of 4 restate it) — this mattered this round because five of the six rules were edited;
- no authoring-viewpoint phrasing anywhere in the field.

### prerequisite_sentences (revision 2)

The four sentences are unchanged and each was re-tested against its reworked rule.

**E1** — `lodging_ext_reservation_deposit` ← `lodging_ext_stay_rate_posting`: *"The deposit asked for is fixed only after the folio carries the room rate posted for every night of the stay."* Still in the blocked rule; "only after"; state form, record-visible, no performer, no tool, no id; `condition` the same scope. Still exactly one write of this difficulty brings the state about (`post_stay_room_charge_ee3504ba`, the only tool writing `event_type="lodging_room_charge"`; the settlement tool's `charge_category="room_rate"` row is a `lodging_payment` and is not a room rate posted). Single reading preserved.

**E2 / E3 / E4** — the settlement's three sentences (*"only after"* the retained room rate, *"only once"* the departure services charge, *"Before it is worked out"* the resort charge). Each still in the blocked rule, each still a record-visible state, each still brought about by exactly one tool (`lodging_fee_charge`, `charge_category="cleaning_fee"`, `lodging_resort_fee` respectively). The settlement's rule gained three sentences this round (the enumerated charge scope, the deposit exclusion, the late-settlement sentence) and **none of them states a cross-problem order**, so the three declared edges remain the only dependency language in it.

Cross-problem orders in a rule that ground no declared edge: none. Two new sentences were checked specifically because they could have introduced one and do not —
- `lodging_ext_early_departure_charge`: *"A party that leaves before the departure date on the reservation has not changed the reservation, so no change fee arises from the early departure."* The word "before" here relates the party's departure to a **date**, not one problem's result to another's, and it asserts that a charge does **not** arise. No edge.
- `lodging_ext_departure_settlement`: *"Where the folio was not settled before the party left the mountain, it is settled when the household next takes it up, on the same basis."* Again a relation between an act and a date, restating base's superseded timing rather than ordering two problems. No edge.

**F-10 disposition reviewed and accepted.** Base `lodging_deposit_terms.rule` still contains *"A reservation becomes firm only once the deposit has cleared."*, a cross-problem order in a base sentence. The reworker left it. That is right on both counts the skill allows: base may not be rewritten, and no task's tree rests on the sentence (no task claims `lodging_confirm`). It remains an observation and requires nothing.

### override_declarations (revision 2)

The full sweep was re-run sentence by sentence against every `base_policy_refs` entry of all six policies, and each of the fourteen `overwrite` entries was verified mechanically on three points: its `superseded_clause` appears verbatim in the named base policy's `rule`, its `replaced_by` appears verbatim in the extended policy's own `rule`, and the named base policy is in that extended policy's `base_policy_refs`. **14 of 14 pass all three; 0 problems.**

| # | policy | base | supersedes | status |
| --- | --- | --- | --- | --- |
| 1 | stay_rate_posting | rate_and_fees | night-by-night posting grain | carried from r1 |
| 2 | stay_rate_posting | rate_and_fees | the per-night window reading | carried from r1 |
| 3 | stay_rate_posting | agg_household_stay_pricing | passholder reduction on the arrival date | carried from r1 |
| 4 | stay_rate_posting | agg_household_stay_pricing | advance booking reduction | carried from r1 |
| 5 | stay_rate_posting | agg_household_stay_pricing | length-of-stay reduction taken last | carried from r1 |
| **6** | stay_rate_posting | rate_and_fees | *"Guests beyond the unit type's standard occupancy add the extra person charge to each night they stay."* | **new — closes F-1** |
| 7 | reservation_deposit | deposit_terms | the deposit as the unit type's share of the room rate | carried from r1 |
| **8** | reservation_deposit | stay_operations | *"The incidental hold is taken at check-in against the lead guest's own payment method and is not taken against a third party's card."* | **new — closes F-2** |
| 9 | stay_resort_charge | rate_and_fees | the resort charge not reduced by any discount | carried from r1 |
| **10** | departure_service_charge | rate_and_fees | *"The housekeeping charge is posted once on departure and the parking charge nightly for spaces beyond those included."* | **new — closes F-3; `overwrite` is no longer empty** |
| 11 | early_departure_charge | rate_and_fees | a night left early still charged | carried from r1 |
| **12** | early_departure_charge | cancellation | *"After the deadline the unit type's late cancellation nights of room rate are retained, worked out at the rate of the first nights of the stay, and the remainder comes back."* | **new — closes F-7(b)** |
| 13 | departure_settlement | checkout_settlement | deposit first, then credit, then the payment method | carried from r1 |
| **14** | departure_settlement | checkout_settlement | *"The folio is presented on departure and settled before the party leaves the mountain."* | **new — closes F-13/T1-4** |

Entry 10's `replaced_by` is worth quoting because it is the one that had to carry the most: *"The unit type's housekeeping charge and its nightly parking charge are the figures this charge starts from, and each of them is varied by what the records of the stay show, with a turnover charge added on top of the housekeeping charge for a party larger than the unit sleeps as standard."* It names all three of the deviations revision 1 found undeclared — the housekeeping multiplier, the parking discount and the turnover element — so a reader of the merged policy is told that base's flat figures are starting points and not the answer.

Round-1 F-7(a) — the reuse of base's per-tier `change_notice_days` against a departure-date anchor — is closed differently and correctly: not by declaring an override, but by the extended policy ceasing to read base's parameter at all (`K('early_departure_notice_days')`). That is the stronger fix, because it leaves base's own deadline untouched for the modification policy that owns it.

**Re-sweep for anything still undeclared.** Working through each base sentence of each `base_policy_refs` entry once more against the reworked extended rules, no further conflict was found. Three places were examined closely and each is genuinely clear:

- the **turnover element** (`0.3` / `0.15 × cleaning_fee_usd` per guest beyond standard occupancy) — base's housekeeping sentence is now superseded by entry 10, which names the turnover charge explicitly, so base fixes nothing it contradicts; base `lodging_stay_operations`' *"a party asking for more is charged for the extra visits"* fixes no figure;
- the **in-room-dining service charge** (12 % / 18 %) — no base sentence fixes a service charge on folio incidentals, so this is added ground, not a substitution. **F-11's disposition is therefore right**: it is not an override and needs no `overwrite` entry;
- the **allowance semantics** of `late_cancellation_fee_nights` in the early-departure policy — the parameter now means *nights forgiven* there while base uses it as *nights retained*. Base's sentence carrying that meaning is entry 12's `superseded_clause`, so the re-purposing is declared. Recorded as an observation at **G-2** because the same parameter is still used in its capping sense two sentences later in the same rule.

**`design_rationale` was part of the round-1 finding and is checked against the artifact after the reveal**, in each task's `source_gt_comparison`; it is a task file and cannot be read here without breaking the freeze.

### factor_ladders (revision 2)

Twenty-nine factors over six policies, re-derived in full.

| policy | factors | parameter | method | tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| `lodging_ext_stay_rate_posting` | 6 | 5 | 1 | 3,3,3,3,3,3 | passes, lessons |
| `lodging_ext_reservation_deposit` | 4 | 3 | 1 | 3,3,3,3 | insure, dining |
| `lodging_ext_stay_resort_charge` | 4 | 3 | 1 | 3,3,3,3 | passes |
| `lodging_ext_departure_service_charge` | 5 | 4 | 1 | 3,3,3,3,3 | passes, dining |
| `lodging_ext_early_departure_charge` | 6 | **5** | **1** | 3,3,3,3,3,3 | passes, insure |
| `lodging_ext_departure_settlement` | 4 | 3 | 1 | 3,3,3,4 | dining, passes |

Every policy is inside 4–6 factors with ≥2 `parameter` and ≥1 `method`, every ladder ≥3 tiers counting the fall-through, binding sets pairwise disjoint within each policy (script-verified, no name under two factors), and no `decides` is `result`.

**F-8 closed.** `lodging_ext_early_departure_charge.factors[5]` (`protection_claim_retention`) is relabelled `"effect": "method"` → `"effect": "parameter"`, and its three tiers now carry `value` keys (`K('allowed_claim_retention_share')`, `K('open_claim_retention_share')`, `1`) in place of the prose `method` strings. That is the honest label: the tiers substitute a multiplier into the unchanged expression `RND((retained_with_window + occupancy_retained) * retention_share, 2)`. The policy's count moves from a declared 4/2 to a real 5/1, and the surviving `method`, `nights_given_up_basis`, is genuine — its three tiers select three different counting rules for the nights given up, not three numbers.

**F-4 closed.** `lodging_ext_reservation_deposit.factors[3]` (`payments_already_collected`): tier 2's condition is now *"the folio carries **one or more** payments already collected against the stay totalling less than the share worked out"*, in both the rule and the ladder. The tiers are now disjoint **as stated** — tier 2 requires at least one payment, so the fall-through's domain (`paid_to_date == 0`) is outside it — and their outcomes differ on their own domains, tier 2 selecting a strictly positive `paid_to_date` and the fall-through selecting 0. The `compute` was already `paid_to_date > 0` and did not need to move. Three real tiers where round 1 had two.

**Honest baselines.** Every factor's `baseline` is checked against its own `baseline.rule` this round, not only against its fall-through tier:

- 28 of 29 factors have a `baseline` that is literally their fall-through tier's value or method, as in round 1;
- the twenty-ninth, `nights_given_up_basis`, is the one round 1 red-lighted, and its baseline is now `MX(0, nights_covered_a - folio_nights_consumed_a) if departure_recorded_a else 0` — a transcription of **both** clauses of its `baseline.rule` (*"…less the nights the folio shows consumed where a departure is recorded on the reservation, and where no departure is recorded on the reservation no night of the stay counts as given up"*), where round 1 carried only the second clause. It is now what the baseline rule states **for whatever input it is given**, which is what an honest baseline must be. That its fall-through tier is narrower than its baseline is a consequence of `baseline.rule` itself being two-branched, and is recorded as a benign observation at **G-3**.

**Business realism of conditions and outcomes**, re-judged on the reworked ladders. The one ladder whose outcomes changed is `notice_retained_nights`, whose middle tier moved from a cap (`MN(nights_given_up, late_cancellation_fee_nights)`) to an allowance (`MX(0, nights_given_up - late_cancellation_fee_nights)`), with the rule spelling out why: *"the notice earning the household that allowance"*. Both shapes are monotone in the notice given — more notice, less retained — and an allowance of forgiven nights for a household that told the desk is a treatment a lodging operator does publish. The other 28 ladders are unchanged in outcome and were re-judged as in revision 1.

### findings (revision 2)

Round-1 findings are dispositioned item by item in `## revision_2_disposition` below. New findings are prefixed **G-**.

---

**G-1 — SOURCE-POLICY observation (rule ↔ ladder), introduced by the rework: `notice_retained_nights` tier 1 still names a period the rule no longer states.**

- *Symptom.* The factor ladder's first tier names *"the unit type's change notice period"*; the `rule` and the `compute_basis` behind the same branch name *"the early departure notice period"*, and the `compute` reads `K('early_departure_notice_days')`. The ladder's second tier says *"raised within **that** period"* and so inherits the same referent.
- *Root cause.* The fix for F-7(a) changed the `rule`, the `compute` and the `params`, but the `factors[1].ladder[*].when` strings were left at their round-1 wording. The `value` of tier 2 **was** updated in the same object (cap → allowance), so the ladder was edited — the condition strings were simply not carried along.
- *Evidence.*
  - `lodging.extended.yaml` → `extended_policies[4].factors[1].ladder[0].when`: *"a request about the stay stands accepted at the desk and was raised more than **the unit type's change notice period** in calendar days before the departure date on the reservation"*.
  - `extended_policies[4].rule`: *"Where a request about the stay stands accepted at the desk and was raised more than **the early departure notice period** in calendar days before the departure date on the reservation, no night is retained."*
  - `extended_policies[4].compute_basis.retained_nights` quotes the rule's wording, not the ladder's.
  - `extended_policies[4].compute.retained_nights` = `0 if (notice_requests > 0 and notice_lead_days > K('early_departure_notice_days')) else (MX(0, nights_given_up - P('late_cancellation_fee_nights')) if (notice_requests > 0 and notice_lead_days <= K('early_departure_notice_days')) else nights_given_up)`.
  - `extended_policies[4].params.early_departure_notice_days = 7`, a flat charter constant; `variants[*].parameters.change_notice_days` is per tier — 3, 7, 10, 10, 14, 21, 30 across the seven unit types.
- *Why this is not a red light on this suite.* The two periods pick out different numbers for five of the seven unit types, but the only task that reaches this factor is task 1 on a **Slopeside Studio**, whose `change_notice_days` is 7 — the same as `early_departure_notice_days`. Both readings put the request (raised 4 calendar days before the departure date) on the same tier, so no second scored value can be demonstrated on either task's world, and the skill's threshold is not met. It is recorded here, and named in `1.md` § `policy_self_consistency`, because the divergence is real in the artifact and would bite the moment a task used any other unit type: on a Mountain Lodge Suite the ladder would read 14 days and the rule 7.
- *Affected artifact and location.* `env/env_0004_ski_resort_operator/tasks/lodging_reservations_desk/lodging.extended.yaml` → `extended_policies[4].factors[1].ladder[0].when` and `[1].when`.
- *Relation to previous revisions.* New in revision 2; it is the residue of the fix for revision 1's F-7(a), which is itself closed.

---

**G-2 — observation: `late_cancellation_fee_nights` carries two senses inside one reworked rule.**

- *Evidence.* `extended_policies[4].rule`, two sentences apart: *"…the nights retained are the nights given up **less** the unit type's late cancellation nights, and never fewer than none, the notice earning the household that allowance."* and *"Where the folio carries an occupancy charge posted for the stay and the nights retained number the unit type's late cancellation nights **or fewer**, the unit type's extra person charge is retained for each guest beyond its standard occupancy for each night retained."* The first uses the parameter as an allowance subtracted from the nights given up; the second uses it as a threshold the retained nights are measured against. Base `lodging_cancellation` uses it in a third sense — the number of nights retained — in the sentence `overwrite` entry 12 supersedes.
- *Why an observation.* Each sentence states its own arithmetic in full and `compute` implements each exactly, so a reader reaches one answer; the base sense is formally released by entry 12. No second defensible value follows. Recorded because one parameter doing three jobs across a supersession boundary is the kind of thing that makes a reader reach for the wrong one.
- *Affected artifact.* `lodging.extended.yaml` → `extended_policies[4].rule`, `.compute.retained_nights` / `.occupancy_retained`; base `policies[7].rule`.

---

**G-3 — observation: `nights_given_up_basis`'s baseline is broader than its fall-through tier, and correctly so.**

- *Evidence.* `extended_policies[4].factors[0]`: the fall-through tier is *"otherwise → no night of the stay counts as given up"*, while `baseline` is `MX(0, nights_covered_a - folio_nights_consumed_a) if departure_recorded_a else 0`. `baseline.rule` carries both branches in one sentence.
- *Why an observation and not a finding.* The rule of thumb that a factor's fall-through tier **is** its baseline holds only where `baseline.rule` states one thing for the input; here it states two, conditioned on the same fact the ladder's tiers turn on. Revision 1 red-lighted the previous baseline precisely for picking the narrower branch, so the broader binding is the correct reading of *"each factor's `baseline` is exactly what the baseline states for that input"*. Recorded so that a later reader does not "simplify" it back to `0`.
- *Affected artifact.* `lodging.extended.yaml` → `extended_policies[4].factors[0].baseline`, `.baseline.rule`.

## revision_2_disposition

Every round-1 finding, taken one at a time: closed, or not, with the artifact that decides it. Written after both tasks' revision-2 comparisons were on disk.

| round-1 finding | class | verdict | decided by |
| --- | --- | --- | --- |
| **F-1 / T0-3** undeclared override, extra-person charge | SOURCE-POLICY RED | **CLOSED** | `overwrite` entry 6, verbatim both sides; `tasks/0.json` `design_rationale`'s *"inherited untouched"* claim struck |
| **F-2 / T0-4** undeclared override, incidental hold at check-in | SOURCE-POLICY RED | **CLOSED** | `overwrite` entry 8, verbatim both sides; rationale no longer calls `lodging_stay_operations` input lineage |
| **F-3 / T1-2** undeclared override, housekeeping and parking | SOURCE-POLICY RED | **CLOSED** | `overwrite` entry 10 replaces `[]`; its `replaced_by` names the multiplier, the discount and the turnover element; rationale's *"without fixing any figure"* struck |
| **F-4 / T0-6** tier written as two | SOURCE-FACTOR RED | **CLOSED** | *"one or more payments"* in rule and ladder; three disjoint tiers with distinct outcomes |
| **F-5 / T1-3** rule states no status for the credit pots | SOURCE-POLICY RED | **CLOSED** | the *"Credit counts only where the record carrying it is itself live"* sentence plus the state in all three tiers; the 1256.27 reading loses its basis |
| **F-6** supplement judged over the wrong span | observation | **CLOSED** | rule, ladder, bindings and compute re-based on "the nights the reservation covers" |
| **F-7** undeclared reuse of base machinery | observation | **CLOSED, both halves** | (a) `K('early_departure_notice_days')` replaces `P('change_notice_days')`; (b) `overwrite` entry 12. Residue at **G-1** |
| **F-8** mislabelled `method` | SOURCE-FACTOR RED | **CLOSED** | `protection_claim_retention` → `parameter`, tiers carry `value` keys |
| **F-9** ordering word in every tool Arg | observation | **CLOSED** | *"before the call"* removed from all six `lodging_id` Args; the four surviving hits are *"the folio balance after the posting"* in `Returns:` |
| **F-10** base sentence stating a cross-problem order | observation | **not changed — correct** | base may not be rewritten and no task's tree rests on it |
| **F-11** in-room dining service charge as new ground | observation | **not changed — correct** | no base sentence fixes a service charge on folio incidentals, so nothing is superseded |
| **F-12** base's change fee on an early departure | observation | **CLOSED** | *"A party that leaves before the departure date … has not changed the reservation, so no change fee arises"* |
| **F-13 / T1-4** "every charge"; settled before leaving | observations | **CLOSED** | charge scope enumerated and the deposit excluded, in `rule` and `baseline.rule`; `overwrite` entry 14 for the timing sentence |
| **T0-1** tier read off a stamp | SOURCE-FACTOR RED | **CLOSED** | the world was re-dated: stamp 5589.55, rule 4062.89, night-by-night 4635.39, and gold's `rate_plan` (`base`) differs from the stamped field (`peak`) |
| **T0-2** closure figure the world does not produce | SOURCE-CHAIN RED | **CLOSED** | −250.00 → 250.00, with the tier-1 reasoning stated and the figure recomputed by the build harness; verified three ways in `0.md` |
| **T0-5** "two teenagers" against `children = 2` | observation | **CLOSED** | persona now says *"three adults and two children"* |
| **T1-1** straw-man baseline; factor inert against the honest one | SOURCE-FACTOR RED | **CLOSED** | baseline corrected to both clauses of `baseline.rule`; the cap redesigned as an allowance so the factor bears weight structurally (927.69 against gold 630.12) |
| **T1-5** `retained_nightly_rate` labelled `parameter` | observation | **not changed — correct** | revision 1 recorded it as explicitly not a red light; all three tiers yield one rate into the same expression |

**All eight round-1 red lights are closed.** Five were closed by declaration (F-1, F-2, F-3, F-5, and F-7's second half), one by correcting a figure at its source (T0-2), one by moving the world (T0-1), and two by redesigning a ladder (F-4, and T1-1 with F-8). None was closed by rewording a defect into a new name: in every case the auditor re-derived the consequence the round-1 finding demonstrated and found it gone from the world, not merely unstated.

The three dispositions the reworker left in place — F-10, F-11, T1-5 — were each re-judged against the skill's own criteria and are right.

## closing_checklist (revision 2)

Supersedes the revision-1 checklist for the reworked artifacts. Revision 1's checklist is left in place as the record of what was true then.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | holds |
| old revisions traceable | holds — revision 1 is untouched in all three files; revision 2 is appended under its own heading in each |
| every comparison section carries a PASS | **`1.md` yes; `0.md` no** — task 0 § `source_gt_comparison (revision 2)` carries one SOURCE-FACTOR RED (**T0-7**) |
| extended policies fully covered, task scopes pairwise disjoint, each spanning its whole tree | holds — unchanged from revision 1 and re-verified |
| task tools and GT closed; each tool an independently generated, frozen uuid8 | holds — the six uuid8s are unchanged, which is correct across a rework |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle; the difficulty's edges a DAG | holds — the `prerequisite` field is byte-identical to revision 1 and was re-verified against the reworked rules |
| every computation: 4–6 factors, ≥2 `parameter`, ≥1 `method`, ladders ≥3 tiers stated in full in the rule, tiers distinct in outcome, conditions and outcomes ones the business holds | **holds** — including `lodging_ext_early_departure_charge`, which revision 1 left with no genuine `method`, and `payments_already_collected`, whose third tier was a restatement of its second |
| per task ≥1 multi-source and ≥1 cross-difficulty factor, on seeded rows | holds — task 0: 4 and 4; task 1: 9 and 4 |
| every factor bears weight against an honest baseline, the baseline alone giving a definite number different from gold | **holds** — 29 of 29. Whole baselines: 7335.00 / 855.50 (task 0) and 72.00 / 304.00 / 2116.00 / 3597.01 (task 1) |
| no tier read off a stamp | **holds** — task 0's stamp now separates all three readings by the score; task 1 never had one |
| proof fields assert only what the world produces | **does not hold** — **T0-7**: one `tier_taken` field names the tier the old world took. Every other assertion in both files was recomputed and matches, including all 29 sensitivities, all 6 whole baselines and all 4 `edge_load_bearing` figures |
| instantiation-stage gates re-run on the final form | done, all green (below) |

**Gate re-run on the reworked form**, from the repository root, `T = env/env_0004_ski_resort_operator/tasks/lodging_reservations_desk`:

```
check_extended.py    $T  -> EXTENDED OK        check_task_tools.py $T -> TASK TOOL CONTRACT OK
replay_tasks.py      $T --check                0.json 13 acts clos=17/17 match=True ; 1.json 17 acts clos=27/27 match=True  -> REPLAY OK
check_solvability.py $T  -> SOLVABILITY OK     check_compute.py    $T -> COMPUTE OK (0.json brch=40 step=13 ; 1.json brch=77 step=17)
check_grounding.py   $T  -> GROUNDING OK       check_cross_fire.py $T -> SCOPE OK
```

`replay_tasks.py` was run with `--check`, so no `db_closure` was written back. The COMPUTE counts are unchanged from revision 1 in every column, which is what a rework that moved values and wording without moving shape should produce.

**Difficulty verdict (revision 2).**

| relationship | task 0 | task 1 |
| --- | --- | --- |
| policy self-consistency | **PASS** (was SOURCE-POLICY RED) | **PASS** (was SOURCE-POLICY RED) |
| the problem tree holds | **PASS** (was SOURCE-CHAIN RED) | **PASS** |
| factors bear weight | **SOURCE-FACTOR RED** — T0-7 (was SOURCE-FACTOR RED — T0-1) | **PASS** (was SOURCE-FACTOR RED) |
| unique solution | **PASS** | **PASS** |

The rework is substantially sound. All eight round-1 red lights are genuinely closed, six round-1 observations are closed with them, the three dispositions left in place are right, and nothing that passed in revision 1 regressed: both trees, both personas, all four tool-body checks, the base copy, the uuid8s and the whole unique-solution layer are intact, and every one of the 29 factor sensitivities, 6 whole baselines and 4 edge figures was re-derived and matched.

What the difficulty does not yet close on is one leftover string. `tasks/0.json` → `computations[0].factor_sensitivity[4].tier_taken` still names the tier the **old** seven-night world took, on the very factor whose world was re-dated to close T0-1; three other fields of the same task state the tier correctly, so the record contradicts itself and the machine-readable face is the one that is wrong (**T0-7**). Two observations of the same class sit beside it — a second `tier_taken` carrying its ladder's pre-rework wording (**T0-8**) and a factor ladder whose condition strings were not renamed with their rule (**G-1**, demonstrated as **T1-7**) — and together they point at one mechanism rather than three mistakes: `factors[].ladder[*].when`, and the `tier_taken` fields copied from it, are not regenerated when the ladder or the world moves.

---

# revision_3

Re-audit round 3. Revisions 1 and 2 above are left exactly as written.

## charter_global_frozen (revision 3)

- Auditor: the same independent source-layer auditor. Not blind; rounds 1 and 2 GT have been seen. Every figure below was recomputed before any round-3 GT field was read.
- Freeze time of this section: 2026-09-17, **before any round-3 GT field of either task was read**.

| artifact | r1 | r2 | r3 | |
| --- | --- | --- | --- | --- |
| `lodging.extended.yaml` | `77389c0b6e7c12bb` | `10b77a068f7f5f36` | `24e0fcc37b9d68aa` | **changed** |
| `task_tools.py` | `843389fdabdcbf91` | `604959686270553b` | `604959686270553b` | unchanged |
| `tasks/0.json` (masked) | `2461652bc7e8657c` | `3292f6419bae96cb` | `3292f6419bae96cb` | unchanged |
| `tasks/1.json` (masked) | `6472376a9c846086` | `6472376a9c846086` | `6472376a9c846086` | unchanged |

Per the skill's re-derivation rule, the charter moved so the charter-global sections are re-derived in full; `task_tools.py` and **both masked worlds are byte-identical to round 2**, so the tool-module conclusions are carried forward on the strength of the identical hash and each task's world-facing derivation is re-run rather than re-invented.

### what moved, and what provably did not

Diffing the round-2 and round-3 charters key by key over all six extended policies:

| key | identical r2 → r3 |
| --- | --- |
| `compute` | **yes, all six** |
| `params`, `baseline`, `prerequisite`, `overwrite`, `target_tool`, `computes`, `subject`, `base_policy_refs`, `trigger`, `cross_category`, `inputs` | **yes, all six** |
| base section (`policies`) and `variants` | **yes** — base still verbatim, the seven tariffs untouched |
| `factors` | changed in 3 policies — **six ladder `when` strings, nothing else** |
| `rule` | changed in 1 policy — **one sentence added** |
| `compute_basis` | changed in 1 policy — **one entry extended to quote that sentence** |

Because `compute` and both worlds are byte-identical, **no computed value can have moved**, and none did: re-running the auditor's own numeric harness against the round-3 charter reproduces every round-2 figure exactly (task 0: 4062.89, 867.29, baselines 7335.00 and 855.50, all ten sensitivities, the 250.00 edge figure; task 1: 42.00, 450.59, 630.12, 1953.83, baselines 72.00 / 304.00 / 2116.00 / 3597.01, all nineteen sensitivities, the edge figures 1911.83 / 1503.24 / 1323.71, and the same settlement under all six permutations). This is a documentary-face-only change, as claimed.

### the six ladder strings

Each replaced a restatement with the rule's own clause, verbatim:

| policy / factor | tier | was | now |
| --- | --- | --- | --- |
| `stay_rate_posting` / `passholder_reduction` | 1 | *"…stands on the household account **and** is registered to the guest named as the lead guest…"* | *"a season pass standing active for the season of the stay is registered to the guest named as the lead guest on the reservation"* |
| " / " | 2 | *"…stands on the household account **and** is registered to someone other…"* | *"…stands on the household account **but** is registered to someone other than the lead guest"* |
| `stay_rate_posting` / `straddling_window_pricing` | 1 | *"the stay straddles two published rate windows **and** more than half of its nights…"* | *"more than half of the nights of the stay fall inside the higher priced of the two windows it straddles"* |
| " / " | 2 | *"…**and** half or fewer of its nights…"* | *"half or fewer of the nights of the stay fall inside the higher priced of the two windows it straddles"* |
| `departure_service_charge` / `passholder_parking_rate` | 2 | *"…no more **parking** spaces than the unit type includes"* | *"…no more spaces than the unit type includes"* |
| `early_departure_charge` / `notice_retained_nights` | 1 | *"…more than **the unit type's change notice period**…"* | *"…more than **the early departure notice period**…"* |

No semantic drift in any of the six. The dropped *"stands on the household account"* is redundant because every cross-category read is scoped to the household account by construction; *"and"* → *"but"* is the rule's own connective; the dropped *"the stay straddles two published rate windows and"* is carried by the surviving *"the two windows it straddles"*, which presupposes the straddle the compute guards with; *"parking spaces"* → *"spaces"* is the rule's wording for the same quantity. The sixth is the substantive one: it retires the stale referent revision 2 recorded as **G-1**, and now agrees with the `rule`, the `compute_basis` and the compute's `K('early_departure_notice_days')`.

### the added rule sentence, and whether it is normatively inert

One sentence was added to `lodging_ext_early_departure_charge.rule`, between its two existing nights-given-up sentences:

> *"Where a departure is recorded on the reservation and the folio shows a night consumed for every night from the arrival date to that departure, the nights given up are counted as the nights the reservation covers less the nights the folio shows consumed."*

and `compute_basis.nights_given_up` was extended from quoting one sentence to quoting that one as well. This is a change to published normative text made to satisfy a quotation property, so it was checked the same way the `settled_ratio` re-cut was on a sibling difficulty: by domain, by implementation and by outcome.

**By domain, it is entailed by a sentence the rule already carried.** The rule's second sentence states, unrestricted over departed reservations: *"The nights given up are counted as the nights the reservation covers less the nights the folio shows consumed **where a departure is recorded on the reservation**, and where no departure is recorded on the reservation no night of the stay counts as given up."* The rule's fifth sentence carves out one sub-case: *"Where a departure is recorded … and the folio shows **fewer** nights consumed than the nights from the arrival date to that departure, the nights given up are counted as the nights the reservation covers less the nights from the arrival date to the recorded departure…"*. The new sentence governs exactly the residue — departure recorded **and not** fewer-consumed — and prescribes exactly what the second sentence already prescribed there, *covered less consumed*. Writing out the three domains: S2 = {departure recorded}, S5 = {departure recorded ∧ consumed < to-departure}, S_new = S2 \ S5, and on S_new both S2 and S_new give the same count. **Nothing is added, no condition is new, no parameter is introduced, no branch is created.**

**By implementation, it matches the compute branch that was already there.** `compute.nights_given_up` is byte-identical to round 2: `MX(0, nights_covered_a - nights_to_departure_a) if (departure_recorded_a and folio_nights_consumed_a < nights_to_departure_a) else (MX(0, nights_covered_a - folio_nights_consumed_a) if departure_recorded_a else 0)`. Its second arm is `MX(0, covered − consumed)` under `departure_recorded_a`, which is the new sentence word for word. The sentence therefore closes a two-way-equivalence gap rather than opening one: the middle tier of `nights_given_up_basis` previously had a compute branch and a ladder entry but no sentence of its own.

**By outcome, nothing moved.** `compute`, `params`, `baseline` and both worlds are byte-identical, and the numeric re-run above reproduces every figure, including the 2116.00 whole baseline of that very computation — `baseline.rule` was not touched and still carries only the second sentence, so the baseline a reader of the computation document alone computes is unchanged.

**By conflict, none is created.** The sentence agrees with the rule's second sentence and is disjoint from its fifth; it contradicts no base provision (base fixes no nights-given-up count, and the relevant base sentence is `overwrite` entry 11); and it states no cross-problem order, so it grounds no undeclared dependency. Recorded as an observation at **H-2** only because a rule that says a thing twice is worth noting, not because it says anything new.

### the sweep, run independently

Three properties, over all 29 factors and both tasks. The auditor ran its own rather than accepting the reported counts.

**1. Every non-fall-through ladder condition is a verbatim clause of its own policy's `rule`.** 59 non-fall-through tiers across 29 factors; **0 misses** (round 2: 7 misses). Script-verified by whitespace-normalised substring match.

**2. Every `decides` binding is a ternary chain whose fork count is exactly one less than its ladder's tier count**, so tiers and compute branches stand in an order-preserving bijection and the fall-through is the final `else`. Checked by parsing each binding with `ast` and walking the `IfExp` chain: 28 factors have 2 forks against 3 tiers, and `resort_credit_draw` has 3 forks against 4 tiers. **29 of 29, no mismatch.**

**3. The tier the ladder selects is the branch the compute takes, on the handling-time world.** The auditor built its own derivation: parse the `decides` binding into its ordered tests, evaluate the bindings in declared order in the environment `skills/erl-task-instantiate/scripts/check_compute.py::build_env` constructs — the gates' own environment — for that computation's handling-time world, take the first test that fires, and read that tier's `when`. Closing the loop, for every factor whose selected tier declares an evaluable value, that value was compared against the value the compute actually produced for the binding: **22 of 22 evaluable tiers match exactly** (the remaining 7 are method tiers or tiers whose value is stated in prose, where there is no expression to evaluate).

**The handling-time world is not the seed world, and task 0 proves it.** For `lodging_ext_reservation_deposit` the two worlds select **different tiers** on two of its four factors:

| factor | tier on the seed world | tier on the handling-time world |
| --- | --- | --- |
| `protected_deposit_share` | **1** — *"…the benefit remaining on it reaches the room rate standing on the folio"* (3600.00 ≥ 0.00, because nothing is posted yet) | **2** — *"…falls short of the room rate standing on the folio"* (3600.00 < 4062.89) |
| `payments_already_collected` | **1** — *"…totalling the deposit share worked out or more"* (500.00 ≥ 0.00) | **2** — *"…one or more payments … totalling less than the share worked out"* (500.00 < 1117.29475) |

So this difficulty carries a live discriminator: a harness that evaluated on the seed world would report tier 1 for both, and one that evaluates after the prerequisite write reports tier 2 for both. Which one the record shows is checked against this table in `0.md` § `source_gt_comparison (revision 3)`. (Task 1's settlement does not discriminate — its four tiers are the same on either world — so task 0 is where the property is testable at all.)

### charter re-sweep (revision 3)

Re-run in full on the round-3 charter, independently of the reworker's report:

| property | result |
| --- | --- |
| base section and `variants` verbatim against `blueprint/products/lodging.yaml` | **0 differences** |
| `overwrite` entries: `superseded_clause` verbatim in the named base rule, `replaced_by` verbatim in the extended rule, base policy in `base_policy_refs` | **14 of 14 pass all three; 0 problems** |
| `compute_basis` entries verbatim in their own rule; one per binding | **128 entries, 128 bindings, 0 misses** |
| every sentence of every `baseline.rule` present in its `rule`; every `baseline.params` key a real variant parameter | **0 misses, 0 unknown keys** |
| every `prerequisite.policy_source` verbatim in the **blocked** policy's rule and absent from the depended-on policy's rule | **4 of 4 / 4 of 4** |
| factor counts, labels, tier counts | 6/4/4/5/6/4 factors; every policy ≥2 `parameter` and ≥1 `method`; every ladder ≥3 tiers |
| `prerequisite` graph | byte-identical to revisions 1 and 2; two depth-1 components, acyclic, gates are real non-`result` bindings, `resolved_by` are the depended-on tools |
| tool module | byte-identical to round 2 — same six uuid8s, same bodies, no tool reads a status, compares a date, tests a prior entry, raises or hints |

### findings (revision 3)

**H-1 — observation: `compute_basis.nights_given_up` quotes its first two tiers and not its fall-through.**

- *Evidence.* `extended_policies[4].compute_basis.nights_given_up` now quotes the fewer-consumed sentence and the newly added every-night-consumed sentence — tiers 1 and 2 of `nights_given_up_basis`. The fall-through, *"where no departure is recorded on the reservation no night of the stay counts as given up"*, lives in the rule's second sentence and is not part of that quotation.
- *Why an observation.* The sweep exempts fall-through tiers by construction (`when: "otherwise"` quotes nothing), the sentence is in the `rule` and in `baseline.rule`, and the compute's final `else 0` implements it. No reader is left without the branch. Recorded only because the quotation now covers two of three branches where the natural completion would cover three.
- *Affected artifact.* `lodging.extended.yaml` → `extended_policies[4].compute_basis.nights_given_up`.

---

**H-2 — observation: the early-departure rule now states in two places what it states in one.**

- *Evidence.* The added sentence (quoted in full above) is entailed by the rule's own second sentence restricted to the complement of its fifth. Three checks — domain, implementation, outcome — are set out under § *the added rule sentence*; all three say it adds nothing.
- *Why an observation and not a finding.* The redundancy buys a real property: the middle tier of `nights_given_up_basis` now has a sentence of its own, so the ladder is quotable end to end and the two-way equivalence between rule and compute is complete for that binding. A rule that repeats itself is a legibility cost, not a correctness one, and the alternative — leaving one ladder tier unquotable — was the defect this round exists to close.
- *Affected artifact.* `lodging.extended.yaml` → `extended_policies[4].rule` (the sentence beginning *"Where a departure is recorded on the reservation and the folio shows a night consumed for every night…"*).

## revision_3_disposition

Every round-2 finding, one at a time.

| round-2 finding | class | verdict | decided by |
| --- | --- | --- | --- |
| **T0-7** `straddling_window_pricing.tier_taken` naming tier 1 on a world that takes tier 2 | SOURCE-FACTOR RED | **CLOSED** | the field now carries tier 2's `when`, itself now a verbatim rule clause; verified not by reading the field but by an independent 29-factor sweep that derives the tier from the compute — **0 mismatches** |
| **T0-8** `payments_already_collected.tier_taken` carrying its ladder's pre-rework wording | observation | **CLOSED** | the field now carries the current ladder's *"one or more payments"* clause |
| **G-1 / T1-7** `notice_retained_nights` ladder naming a period the rule no longer states | observation | **CLOSED** | tier 1 rewritten to *"the early departure notice period"*, agreeing with rule, `compute_basis` and `K('early_departure_notice_days')`; tier 2's *"that period"* now resolves correctly |
| **T0-9** `rate_plan.meaning`'s first clause | observation | **not changed — correct** | the schema is in `blueprint/`, outside a task-stage rework's write domain, and no scored value turns on it; the record handles the divergence in `argument_uniqueness_tracing` |
| **G-2** `late_cancellation_fee_nights` in two senses | observation | **not changed — correct** | each sentence states its own arithmetic and `compute` implements each; removing the doubling would mean renaming a variant parameter in `blueprint/`, which is out of bounds |
| **G-3** `nights_given_up_basis` baseline broader than its fall-through | observation | **not changed — correct** | `baseline.rule` is two-branched; narrowing the baseline is precisely what revision 1 red-lighted as T1-1. Round 3 strengthens the case by giving each of the three branches its own sentence |
| **T1-8** two baselines meeting at 927.69 | observation | **not changed — correct** | two distinct substitutions coinciding; each still moves the scored value away from gold, and no route to 927.69 reaches 630.12 |

**The one round-2 red light is closed, and closed at the mechanism this audit named.** Revision 2 recorded that T0-7, T0-8 and G-1 were not three mistakes but one: `factors[].ladder[*].when`, and the `tier_taken` fields copied from it, were not regenerated when the ladder or the world moved. The rework answers at that level — `tier_taken` is no longer transcribed anywhere in this difficulty but derived, and the ladder strings themselves were brought to their rules — and it went beyond the three named instances to all seven restatements in the charter.

**What the auditor verified, independently of the reworker's report.**

| property | auditor's own result |
| --- | --- |
| non-fall-through ladder conditions verbatim in their own rule | **59 tiers, 0 misses** (round 2: 7 misses) |
| `decides` binding is a ternary chain with fork count + 1 = tier count | **29 of 29** |
| `tier_taken` equals the derived tier's `when`, on the handling-time world | **29 of 29, 0 mismatches** |
| selected tier's declared value equals the value the compute produced | **22 of 22 evaluable tiers** (7 are method or prose tiers) |
| no `tier_taken` equals the seed-world tier where the two differ | **0 such cases**, and two live discriminators exist on task 0's deposit |
| `factor_trace` ordinal claims | **29 lines swept, 0 mismatches** |
| `design_rationale` *"Tier taken: the Nth"* claims | **22 claims, 0 mismatches** |
| `overwrite` entries verbatim on both sides and in `base_policy_refs` | **14 of 14** |
| `compute_basis` verbatim in its own rule, one per binding | **128 entries, 128 bindings, 0 misses** |
| `baseline.rule` sentences in rule; `baseline.params` real | **0 misses, 0 unknown keys** |
| prerequisite sentences verbatim in the blocked rule, absent from the depended-on rule | **4 of 4 / 4 of 4** |
| base section and `variants` verbatim against the blueprint product | **0 differences** |
| every scored value, baseline, sensitivity and edge figure unchanged from revision 2 | **confirmed by numeric re-run**, not by reading the record |

The reworker's *"3 mismatches before"* is a claim about a superseded artifact. This auditor found **2** by inspection in revision 2 (T0-7 and T0-8) and did not sweep all 29 then, so a third of the same class is plausible; it is neither confirmed nor refuted by anything readable now, and is recorded as unverified rather than accepted. The *"0 after"* is verified.

**The one change to normative text was checked and is inert.** A sentence was added to `lodging_ext_early_departure_charge.rule` so that the middle tier of `nights_given_up_basis` would have a clause of its own to quote. It is entailed by a sentence the rule already carried, restricted to the complement of another; it matches a compute branch that already existed and is byte-identical; and it moved no figure, including the 2116.00 whole baseline of its own computation. The full argument, by domain, by implementation and by outcome, is in § `revision_3` / *the added rule sentence*. It is recorded as observation **H-2**, with **H-1** noting that the extended `compute_basis` quotation covers two of the three branches.

## closing_checklist (revision 3)

Supersedes the revision-2 checklist. Revisions 1 and 2 keep theirs as the record of what was true then.

| item | state |
| --- | --- |
| per-task audit files one-to-one with the tasks, `_difficulty.md` alongside | holds |
| old revisions traceable | holds — revisions 1 and 2 untouched in all three files; revision 3 appended under its own heading |
| **every comparison section carries a PASS** | **holds — for the first time.** `0.md` and `1.md` § `source_gt_comparison (revision 3)` both PASS all four relationships |
| extended policies fully covered, task scopes pairwise disjoint, each spanning its whole tree | holds |
| task tools and GT closed; each tool an independently generated, frozen uuid8 | holds — module byte-identical to round 2, same six uuid8s |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle; the difficulty's edges a DAG | holds — `prerequisite` byte-identical across all three rounds, re-verified against the round-3 rules |
| every computation: 4–6 factors, ≥2 `parameter`, ≥1 `method`, ladders ≥3 tiers stated in full in the rule, tiers distinct in outcome, conditions and outcomes ones the business holds | holds — and every non-fall-through tier is now a **verbatim** clause of its own rule, which was not true in revisions 1 or 2 |
| per task ≥1 multi-source and ≥1 cross-difficulty factor, on seeded rows | holds — task 0: 4 and 4; task 1: 9 and 4 |
| every factor bears weight against an honest baseline, the baseline alone giving a definite number different from gold | holds — 29 of 29; whole baselines 7335.00 / 855.50 and 72.00 / 304.00 / 2116.00 / 3597.01 |
| no tier read off a stamp | holds — task 0's stamp separates all three readings by the score |
| **proof fields assert only what the world produces** | **holds** — 29 of 29 `tier_taken`, 29 `factor_trace` ordinals, 22 rationale tier claims, 29 sensitivities, 6 whole baselines and 4 edge figures all re-derived and matched |
| instantiation-stage gates re-run on the final form | done, all green (below) |

**Gate re-run on the round-3 form**, from the repository root, `T = env/env_0004_ski_resort_operator/tasks/lodging_reservations_desk`:

```
check_extended.py    $T  -> EXTENDED OK        check_task_tools.py $T -> TASK TOOL CONTRACT OK
replay_tasks.py      $T --check                0.json 13 acts clos=17/17 match=True ; 1.json 17 acts clos=27/27 match=True  -> REPLAY OK
check_solvability.py $T  -> SOLVABILITY OK     check_compute.py    $T -> COMPUTE OK
check_grounding.py   $T  -> GROUNDING OK       check_cross_fire.py $T -> SCOPE OK
```

COMPUTE's counts are identical to revision 2 in every column — `0.json comps=2 fact=10 xfac=4 hist=3 brch=40 step=13`, `1.json comps=4 fact=19 xfac=7 hist=36 brch=77 step=17` — which is what a documentary-face-only fix should produce. `replay_tasks.py` was run with `--check`, so no `db_closure` was written back.

**Difficulty verdict (revision 3).**

| relationship | task 0 | task 1 |
| --- | --- | --- |
| policy self-consistency | **PASS** | **PASS** |
| the problem tree holds | **PASS** | **PASS** |
| factors bear weight | **PASS** (was SOURCE-FACTOR RED) | **PASS** |
| unique solution | **PASS** | **PASS** |

**This difficulty passes the source-layer audit.** All four relationships hold on both tasks: the structured policy is self-consistent with all fourteen overrides declared verbatim on both sides; every prerequisite is stated by a prerequisite sentence in the blocked policy's own rule, in the state form; the customer raises only the root problem while the prerequisites the policy imposes are genuinely unmet at the opening; each tree is derivable from the policy and the world alone, has a customer's own write, and has every edge load-bearing; every computation rests on a self-sufficient baseline and four to six factors that bear weight against honest baselines, with at least one multi-source and one cross-difficulty factor per task; and the policy uniquely entails the scored solution, which the auditor reproduced figure for figure.

Three rounds, and the shape of the repair is worth recording. Round 1 found eight red lights, six of them defects of the charter's *declarations* rather than its arithmetic — the numbers were right from the start, and every one of the 29 sensitivities the auditor recomputed matched at every round. Round 2 closed all eight but left one class of documentary drift behind, where a string is copied rather than derived. Round 3 closed that class at its mechanism rather than at its three instances, and the closure is verifiable: a tier is now something the record derives from the compute on the handling-time world, and an auditor can rebuild that derivation from scratch and get the same answer 29 times out of 29.

What remains on file is five observations, none of which can be shown to cost either task a value: **T0-9** and **G-2**, both of which would require editing `blueprint/`, which is out of a task-stage rework's write domain; **G-3**, where the disposition is correct and the alternative would reopen a closed red light; **T1-8**, a benign coincidence between two baselines; and **H-1**/**H-2**, the legibility price of making one ladder tier quotable. None is grounds for rework.

---

# revision_4

Re-audit round 4. This round is a **step-2 fallback from the render layer**, not a continuation of revision 3's verdict. Revisions 1 to 3 are left exactly as written.

## charter_global_frozen (revision 4)

- Freeze time: 2026-09-17, **before any round-4 GT field of either task was read**.

| artifact | r3 | r4 | |
| --- | --- | --- | --- |
| `lodging.extended.yaml` | `24e0fcc37b9d68aa` | `42de099c9740f8d5` | **changed** |
| `task_tools.py` | `604959686270553b` | `604959686270553b` | unchanged |
| `tasks/0.json` (masked) | `3292f6419bae96cb` | `3292f6419bae96cb` | unchanged |
| `tasks/1.json` (masked) | `6472376a9c846086` | `6472376a9c846086` | unchanged |

Inputs this round additionally include the render-layer reports, `env/env_0004_ski_resort_operator/audits/policy_kb/lodging_reservations_desk/1.md` and `audits/runtime_context/lodging_reservations_desk/1.md`. The published corpus itself is **not** judged here: it was rendered before this change and the product re-renders after this verdict.

### what came back, and why it is mine

The KB audit's blind derivation — documents and record reads only — reproduced this difficulty's problem tree, all nineteen factor tiers, every intermediate, the tool sequence and the owners, and then landed one cent high on two scored values: `retained_amount_usd` **630.13** against 630.12, and `settlement_amount_usd` **1953.84** against 1953.83, the second being pure propagation of the first.

The cause is not a translation fault. `runtime_context/…/1.md` line 445 and `policy_kb/…/1.md` line 146 both say so: *"The corpus says what the source says — 'rounded to the nearest cent once, at the end' — and the source pins no tie rule either; the documents entail exactly what the policy entails."* The retained amount is exactly **630.125**, a half-cent; *"the nearest cent"* has two equally near answers there; the scored value was whatever `RND` — `round(float(x), 2)`, Python's round-half-to-even — happened to produce. Half-up was equally supported by every sentence in force. So the source did not uniquely entail its own scored value, and the defect is in my domain, not the renderer's.

### what changed in the charter

Diffing r3 → r4 key by key over all six extended policies:

| key | r3 → r4 |
| --- | --- |
| `compute`, `params`, `factors`, `overwrite`, `prerequisite`, `baseline.params`, `target_tool`, `computes`, `subject`, `base_policy_refs`, `trigger`, `cross_category`, `inputs` | **identical, all six** |
| base section (`policies`) and `variants` | **identical** — base still verbatim, the seven tariffs untouched |
| `rule` | changed in **all six** |
| `baseline` (its `rule` only) | changed in **all six** |
| `compute_basis` | changed in **all six**, in the `result` entry only |

In every one of the eighteen changed strings the delta is **exactly one sentence and nothing else** — verified by removing the sentence and re-normalising whitespace, which reproduces the r3 text character for character in all eighteen:

> *"An amount that falls exactly halfway between two cents is rounded to the cent whose last digit is even, which is the convention the collective's finance office settles every folio on."*

One canonical wording, identical in all eighteen placements. In each `rule` and each `baseline.rule` it sits immediately after that policy's existing rounding sentence (*"…rounded to the nearest cent once, at the end"*), so the two travel together into whatever document renders them.

### the invariant, checked policy by policy

The fix is an invariant, not two repairs, and a single policy missing it would reopen the defect somewhere no task looks. Each of the six policies calls `RND` exactly once, in its `result` binding; for each, the tie sentence must appear in the `rule`, in the `baseline.rule` its computation document renders from, and in the `compute_basis` of the binding that rounds.

| policy | binding that rounds | in `rule` | in `baseline.rule` | in `compute_basis` of that binding |
| --- | --- | --- | --- | --- |
| `lodging_ext_stay_rate_posting` | `result` | ✓ | ✓ | ✓ |
| `lodging_ext_reservation_deposit` | `result` | ✓ | ✓ | ✓ |
| `lodging_ext_stay_resort_charge` | `result` | ✓ | ✓ | ✓ |
| `lodging_ext_departure_service_charge` | `result` | ✓ | ✓ | ✓ |
| `lodging_ext_early_departure_charge` | `result` | ✓ | ✓ | ✓ |
| `lodging_ext_departure_settlement` | `result` | ✓ | ✓ | ✓ |

**6 of 6 policies, 3 of 3 places, 0 gaps.** No policy rounds without publishing the tie rule, and no policy publishes it in fewer than all three places. The auditor enumerated the rounding policies from the `compute` expressions themselves (every binding whose source contains `RND(`) rather than from any list, so a seventh rounding site would have been found had one existed.

### does the sentence entail what `RND` does — including negatives and other ties?

The sentence must be *equivalent to* the implementation, not merely consistent with the two figures at hand. Tested by evaluating the published rule — round the amount's exact value half-to-even, via `Decimal(x).quantize(Decimal('0.01'), ROUND_HALF_EVEN)` — against `round(x, 2)` across a spread of tie and near-tie cases:

| amount | exact value | a true half-cent? | the sentence gives | `RND` gives | agree |
| --- | --- | --- | --- | --- | --- |
| 630.125 | 630.125 | yes | 630.12 | 630.12 | ✓ |
| 595.125 | 595.125 | yes | 595.12 | 595.12 | ✓ |
| 0.375 | 0.375 | yes | 0.38 | 0.38 | ✓ |
| 0.125 / 0.625 | exact | yes | 0.12 / 0.62 | 0.12 / 0.62 | ✓ |
| **−0.125** | −0.125 | yes | **−0.12** | **−0.12** | ✓ |
| **−630.125** | −630.125 | yes | **−630.12** | **−630.12** | ✓ |
| 0.135 / −0.135 | 0.13500000000000000888 / − | no | 0.14 / −0.14 | 0.14 / −0.14 | ✓ |
| 1.005, 2.675, 8.845, 1234.565, 0.615, 0.005 | not exactly halfway in binary | no | 1.00, 2.67, 8.85, 1234.57, 0.61, 0.01 | same | ✓ |

**Agreement on every case tested, including both negative ties.** The sentence works for negatives because it names the *even last digit* rather than a direction: at −0.125 the two candidate cents are −0.12 and −0.13, and −0.12 is the even one, which is what `RND` returns. A sentence phrased as "rounded up" or "away from zero" would have parted company with the implementation on the negative side; this one does not.

One residual is recorded at **J-1**: the sentence is a statement in decimal arithmetic while `RND` operates on a binary float, so for an amount whose printed decimal ends in a mill of 5 but whose stored value is not exactly halfway (2.675 is the classic), a reader reasoning in exact decimals from published figures would call it a tie and apply the even-cent rule, while `RND` sees a value below or above the midpoint. Both land on the same answer in every case above, and the sweep below shows no such amount is reachable on either task — but the gap is real in principle and is narrower than, not the same as, the defect being closed.

### the rounding sweep, run independently

The auditor enumerated every rounded evaluation the two tasks can reach and classified each one. The domain: for each of the six computations, its gold evaluation plus one evaluation per declared factor with that factor's `baseline` substituted plus the all-baseline evaluation — and each of those again on every edge-skip counterfactual the closure fields exercise (task 0's prerequisite skipped; task 1's three prerequisites skipped singly and together). For each, the argument handed to `RND` was captured before rounding and tested for an exact half-cent on its true value.

| | |
| --- | --- |
| rounded evaluations swept | **71** |
| policies that round without publishing the tie rule | **0** |
| evaluations landing on an **exact** half-cent | **2** |
| evaluations where the published sentence disagrees with `RND` | **0** |

The two ties, both in `lodging_ext_early_departure_charge` on task 1:

| evaluation | pre-round | half-to-even (published) | half-up | `RND` |
| --- | --- | --- | --- | --- |
| **gold** `result` | **630.125** | **630.12** | 630.13 | 630.12 |
| `result` with `occupancy_retention` at its baseline | **595.125** | **595.12** | 595.13 | 595.12 |

**Task 0 rounds twice and hits no tie** — confirmed, not assumed: its two evaluations and all twelve of its counterfactuals come out clear of a half-cent.

**The second instance was live, and no audit had exercised it.** 595.125 is the figure behind `computations[2].factor_sensitivity[4].baseline_result` — a recorded counterfactual of the `occupancy_retention` factor. Under the r3 charter that figure was exactly as unpinned as 630.125: a reader checking that factor's counterfactual from the documents could reach 595.13 and conclude the recorded sensitivity was wrong. The runtime audit derived the gold path and never had cause to compute it. So the change closes a defect the render layer did not catch, in the same policy, by the same mechanism — which is what distinguishes fixing the class from fixing the instance.

The reworker reports 88 evaluations and 6 ties where this audit finds 71 and 2. The **tie values agree exactly** — 630.125 and 595.125, nothing else — and the divergence count is 0 either way. The counts differ because of what is counted: the early-departure computation reads none of the other two writes (proved by the commutation check in revision 2), so it yields the same 630.125 in the gold world and in each world where another prerequisite is skipped; counting instances gives three of each tie and counting distinct evaluations gives one. Neither count is wrong and the substance is identical.

### does the `baseline.rule` addition disturb the baseline?

Two things had to be checked and both hold.

**The baseline's silence about variation is intact.** The tie sentence names no factor, no tier, no condition, no parameter and no record: it contains no conditional connective (*where*, *unless*), none of the words the ladders turn on (pass, plan, season, window, night, guest, dog, parking, dining, claim, deposit, credit, reduction, supplement, allowance), and no factor id. It is a convention on arithmetic, applying to the baseline computation exactly as it applies to the full one, and it tells a reader nothing about which tier anyone is on. `baseline.params` is byte-identical in all six policies, so the default keys the baseline names are unchanged.

**No fall-back figure moved.** `compute` is byte-identical, so no baseline number *can* move, and none does: re-running the auditor's numeric harness against the round-4 charter reproduces every whole baseline — **7335.00 / 855.50** (task 0) and **72.00 / 304.00 / 2116.00 / 3597.01** (task 1) — and every one of the 29 per-factor sensitivities, including the 595.12 whose tie this change pins.

### charter re-sweep (revision 4)

Re-run in full on the round-4 charter:

| property | result |
| --- | --- |
| base section and `variants` verbatim against `blueprint/products/lodging.yaml` | **0 differences** |
| non-fall-through ladder conditions verbatim in their own rule | **59 tiers, 0 misses** |
| `decides` bindings are ternary chains with fork count + 1 = tier count | **29 of 29** |
| `compute_basis` verbatim in its own rule, one per binding | **128 entries, 128 bindings, 0 misses** |
| `overwrite`: `superseded_clause` verbatim in base, `replaced_by` verbatim in the extended rule, base policy in `base_policy_refs` | **14 of 14, 0 problems** |
| every `baseline.rule` sentence present in its `rule`; `baseline.params` keys real | **0 misses, 0 unknown** |
| prerequisite sentences verbatim in the blocked rule | **4 of 4** |
| `prerequisite` graph | byte-identical across all four rounds |
| tool module | byte-identical to rounds 2 and 3 — same six uuid8s, same bodies, judges nothing |
| every scored value, baseline, sensitivity and edge figure | **unchanged from revisions 2 and 3**, confirmed by numeric re-run |

### a limit of this audit's method, recorded plainly

Rounds 1 to 3 judged the unique-solution relationship PASS on both tasks, and on task 1 that judgement was wrong: the visible materials admitted 630.13 as readily as 630.12. It is worth being exact about why this audit did not find it, because part of the reason is structural and part of it is not.

**The structural part.** This audit derives by evaluating the policy's own `compute` expressions in the gates' own environment. `RND` *is* the tie convention — the convention lives in the evaluator, not in any sentence. So a tie cannot present itself to this method as an ambiguity: the auditor asks the compute for a number, gets 630.12, and finds it matches gold. Every conclusion this method reaches about "does the policy entail the scored value" is really "does the compute produce the scored value", and for anything the compute settles silently the two questions come apart. A derivation that works from prose alone, as the render-layer audit's does, is the only kind that can see two readings where the implementation sees one. That asymmetry is not a fault of either audit; it is the reason the two layers exist.

**The part that is not structural.** The skill's check 2 names the things that must carry a verbatim quotation, and **"rounding mode" is on that list, separately from "rounding point"**. Across three rounds this auditor verified that `compute_basis.result` quoted *"the entry posted to the folio is rounded to the nearest cent once, at the end"* and recorded rounding as covered. That sentence pins the *point* (once, at the end) and the *precision* (the cent). It does not pin the *mode*. The checklist asked the question and the answer was available from the charter alone; the auditor read the item too quickly and treated the quotation's presence as the whole of it.

**What would have caught it, cheaply, from the source layer alone.** Exactly the sweep run above: enumerate the rounded evaluations both tasks can reach and test each for an exact half-cent. It needs nothing but the charter and the two worlds, it takes one pass, and it would have surfaced 630.125 **and** 595.125 in round 1. It was not run in rounds 1 to 3. It is recorded here as the check that should have accompanied every reading of a rounding sentence, and it is the reason this round can state a positive result rather than merely confirm someone else's.

### findings (revision 4)

**J-1 — observation: the published tie rule is a decimal statement and `RND` operates on a binary float.**

- *Evidence.* The sentence speaks of an amount that *"falls exactly halfway between two cents"*. `RND` is `round(float(x), 2)`, which rounds the float's stored value half-to-even. For amounts whose decimal form ends in a mill of 5 but whose stored value is not exactly halfway — 2.675 is stored as 2.67499999999999982236, 8.845 as 8.84500000000000063948 — a reader working in exact decimal arithmetic from published figures would call it a tie and apply the even-cent rule, reaching 2.68, while `RND` sees a value below the midpoint and returns 2.67.
- *Why an observation and not a finding.* It cannot be demonstrated on either task: the sweep over all 71 reachable rounded evaluations found **0** cases where the published sentence and `RND` part company, and the only two exact ties, 630.125 and 595.125, are dyadic and land identically under both. The gap is also strictly narrower than the defect being closed — before this change every tie was ambiguous, and now only a non-representable pseudo-tie could be, and none occurs.
- *Affected artifact.* `lodging.extended.yaml` → the tie sentence as it stands in all six `rule` and six `baseline.rule` strings, against `erlbench`'s `RND`.

## revision_4_disposition

| item | origin | verdict | decided by |
| --- | --- | --- | --- |
| **K2 / P5** — no tie rule pinned for *"rounded to the nearest cent"*; 630.125 admits 630.12 and 630.13, and the settlement 1953.83 and 1953.84 | render-layer `KB-RUNTIME RED`, substance in the source | **CLOSED** | the tie sentence in `rule`, `baseline.rule` and `compute_basis.result` of **all six** rounding policies; verified by an independent 71-evaluation sweep and by testing the sentence against `RND` on 15 tie and near-tie cases including two negatives |
| the same defect at **595.125**, in a recorded sensitivity field, never exercised by any audit | found by this round's sweep | **CLOSED by the same sentence** | `computations[2].factor_sensitivity[4].baseline_result`; the second exact half-cent the sweep found, in the same policy |
| **T0-9**, **G-2**, **G-3**, **T1-8**, **H-1**, **H-2** | revisions 2 and 3 | **carried forward unchanged, dispositions still correct** | re-judged against the round-4 charter; T0-9 and G-2 would require editing `blueprint/`, G-3's alternative would reopen T1-1, and T1-8, H-1 and H-2 cost no value |
| every round-1 to round-3 red light | revisions 1 to 3 | **still closed** | re-verified on the round-4 charter: 14/14 `overwrite`, 59/59 ladder clauses verbatim, 29/29 fork counts, 29/29 `tier_taken`, 0 seed-world tiers, `prerequisite` byte-identical, tool module byte-identical |

**What was verified independently, rather than accepted.**

| property | this audit's own result |
| --- | --- |
| policies whose `compute` calls `RND` | **6 of 6**, one `RND` each, in `result` |
| of those, publishing the tie rule in `rule` / `baseline.rule` / `compute_basis` of the rounding binding | **6 / 6 / 6 — 0 gaps** |
| the eighteen changed strings' delta | **exactly the one sentence**, r3 text reproduced character for character on removal, in all eighteen |
| the sentence agrees with `RND` across tie and near-tie cases, negatives included | **15 of 15**, including −0.125 → −0.12 and −630.125 → −630.12 |
| rounded evaluations swept (gold + 29 factor baselines + all-baselines, on gold worlds and every edge-skip counterfactual) | **71** |
| of those, landing on an exact half-cent | **2** — 630.125 and 595.125, both in `lodging_ext_early_departure_charge` on task 1; **task 0 hits none** |
| of those, where the published sentence disagrees with `RND` | **0** |
| `baseline.rule` addition disturbing the baseline's silence about variation | **no** — no conditional connective, no ladder word, no factor id, no parameter; `baseline.params` byte-identical |
| whole-baseline figures | **unchanged** — 7335.00 / 855.50 and 72.00 / 304.00 / 2116.00 / 3597.01 |
| every scored value, sensitivity and edge figure | **unchanged**, confirmed by numeric re-run and then by the record |
| ladder/tier derivation sweep re-run on the round-4 charter | **29 of 29, 0 mismatches**; 20 `factor_trace` ordinals and 22 rationale tier claims, 0 mismatches |

The reworker reports 88 evaluations and 6 ties where this audit finds 71 and 2. The **tie values agree exactly** and the divergence count is 0 either way; the counts differ only in whether repeated evaluations of an unaffected computation are counted as instances or once. Nothing turns on it.

## closing_checklist (revision 4)

Supersedes revision 3's. Earlier checklists stand as the record of what was true then.

| item | state |
| --- | --- |
| per-task audit files one-to-one with the tasks, `_difficulty.md` alongside | holds |
| old revisions traceable | holds — revisions 1 to 3 untouched in all three files |
| every comparison section carries a PASS | holds — `0.md` and `1.md` § `source_gt_comparison (revision 4)` both PASS all four relationships |
| extended policies covered, scopes pairwise disjoint, each spanning its whole tree | holds |
| task tools and GT closed; frozen uuid8s | holds — module byte-identical to rounds 2 and 3 |
| trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle, DAG | holds — `prerequisite` byte-identical across four rounds |
| computations: 4–6 factors, ≥2 `parameter`, ≥1 `method`, ladders ≥3 tiers stated verbatim in the rule, tiers distinct, conditions and outcomes ones the business holds | holds |
| per task ≥1 multi-source and ≥1 cross-difficulty factor on seeded rows | holds |
| every factor bears weight against an honest baseline, the baseline alone giving a definite number different from gold | holds — 29 of 29 |
| no tier read off a stamp | holds |
| proof fields assert only what the world produces | holds — 29 `tier_taken`, 20 ordinals, 22 rationale claims, 29 sensitivities, 6 whole baselines, 4 edge figures, all re-derived and matched |
| **every scored value uniquely entailed by the text, not by the evaluator** | **holds — new this round.** The rounding mode is now pinned wherever the charter rounds, and the sweep shows the two reachable ties both resolve as the text says |
| instantiation-stage gates re-run on the final form | done, all green — and **TRACEABILITY now OK** (`0.json` 16 copied 0 missing; `1.json` 22 copied 0 missing), since the KB is published |

```
check_extended.py $T -> EXTENDED OK   ·   check_task_tools.py $T -> TASK TOOL CONTRACT OK
replay_tasks.py   $T --check   0.json 13 acts clos=17/17 match=True ; 1.json 17 acts clos=27/27 match=True -> REPLAY OK
check_solvability.py -> SOLVABILITY OK   ·   check_compute.py -> COMPUTE OK (counts identical to revisions 2 and 3 in every column)
check_grounding.py -> GROUNDING OK   ·   check_cross_fire.py -> SCOPE OK   ·   check_traceability.py -> TRACEABILITY OK
```

`replay_tasks.py` was run with `--check`; no `db_closure` was written back. The published corpus was **not** judged against this charter — it was rendered before the change and re-renders after this verdict.

**Difficulty verdict (revision 4).**

| relationship | task 0 | task 1 |
| --- | --- | --- |
| policy self-consistency | **PASS** | **PASS** |
| the problem tree holds | **PASS** | **PASS** |
| factors bear weight | **PASS** | **PASS** |
| unique solution | **PASS** | **PASS** |

**This difficulty passes the source-layer audit, and the unique-solution relationship now passes on a basis it did not have in rounds 1 to 3.** Every scored value is entailed by sentences in force rather than by the evaluator's silent conventions: the rounding mode is published wherever the charter rounds, it is the same sentence in every one of eighteen placements, it entails what `RND` does for negatives as well as positives, and the only two amounts in this difficulty that reach a tie both resolve as the published text says. A second instance of the same defect, at 595.125 in a recorded counterfactual, was closed with the first without ever having been exercised.

**A limit of this audit's method is recorded in § `revision_4` / *a limit of this audit's method, recorded plainly*, and should be read as part of this verdict.** In short: this audit derives by running the policy's `compute`, so a convention that lives in the evaluator rather than in a sentence cannot present itself here as an ambiguity — that part is structural, and it is why the render layer exists. But the skill's check 2 names *rounding mode* separately from *rounding point*, and across three rounds this auditor verified the latter and recorded rounding as covered. The question was on the list and the answer was available from the charter alone. The sweep that settles it needs only the charter and the two worlds, takes one pass, and is now on record; it was not run in rounds 1 to 3, and it should accompany every reading of a rounding sentence.

**A procedural defect of this round is disclosed in `1.md` § `source_derivation_frozen (revision 4)`**: comparison assertions for task 0 were written before the round-4 record was read and before task 1's derivation was frozen. They were verified immediately afterwards and all held, so the recorded content is sound; the order in which it was produced was not.

---

# revision_5

Re-audit round 5. A second step-2 fallback from the render layer. Revisions 1 to 4 are left exactly as written.

## charter_global_frozen (revision 5)

- Freeze time: 2026-09-17, **before any round-5 GT field of either task was read**. This round the freeze order was kept: both tasks' revision-5 derivations were on disk before the record was opened. Revision 4 recorded a breach of that discipline in `1.md`; it was not repeated.
- Freeze hashes: `lodging.extended.yaml` **`ec1082e403f851aa`** (r4 `42de099c9740f8d5`) — changed; `task_tools.py` `604959686270553b`, masked `tasks/0.json` `3292f6419bae96cb`, masked `tasks/1.json` `6472376a9c846086` — all three **unchanged**.
- Inputs again include the render-layer reports. The published corpus is the round-3 render and is now behind the charter on three sentences; it is not judged here.

### why the source was touched again

Round 4 reported P1–P4 and deliberately left them, on the reasoning that editing rendered prose from the source side would leave the charter and the corpus disagreeing. P1, P2 and P3 are defects in the **charter's own rule text**, so closing them at the render layer moved the corpus away from the charter and drew two `BIJECTION RED`s. The routing was the error; the defects were correctly identified. They come back here because here is where they live.

That is worth recording as a lesson about this audit's own output as much as about the pipeline: round 4 named three sentence-level defects in the charter and then declined to say that the charter was where they had to be fixed. The finding was right and the disposition was not.

### what changed

Diffing r4 → r5 key by key over all six extended policies: `compute`, `params`, `overwrite`, `prerequisite`, `baseline.params`, `target_tool`, `computes`, `subject`, `base_policy_refs`, `trigger`, `cross_category`, `inputs` are **identical in all six**; the base section and the seven variant tariffs are **identical**. Three policies changed, in `rule`, `compute_basis` and (once) `baseline.rule` and `factors`:

| item | policy | what moved |
| --- | --- | --- |
| **R-1 / P2** | `lodging_ext_reservation_deposit` | the allowance tier's tail, in `rule` and `compute_basis[advance_credit]` |
| **R-2 / P3** | `lodging_ext_early_departure_charge` | ten occurrences of "a request about the stay" → "a request to change the dates of the stay": three `rule` sentences, four `compute_basis` entries, two ladder `when` strings |
| **P1** | `lodging_ext_departure_service_charge` | "The four elements are added together" → "The elements of the charge are added together", in `rule`, `baseline.rule` and `compute_basis[result]` |
| **550.375** | `lodging_ext_early_departure_charge` | one clause appended to the nightly-rate paragraph, in `rule` and `compute_basis[retained_nightly]` |

All four superseded wordings are at **0 occurrences** in the charter — verified by counting `nothing further is asked for`, `a request about the stay`, `no request about the stay` and `The four elements` across the whole extended section.

**Nothing that decides a number moved**, so no scored value can have moved, and none did: re-running the numeric harness against the round-5 charter reproduces 4062.89 / 867.29 / 42.00 / 450.59 / 630.12 / 1953.83, the whole baselines 7335.00 / 855.50 / 72.00 / 304.00 / **2116.00** / 3597.01, all 29 sensitivities and the edge figures 250.00 and 1911.83 / 1503.24 / 1323.71.

### R-1: is the replacement true of the compute on every branch, not just the untriggered one?

The tier is `advance_credit`'s first: `paid_to_date >= share_amount` → `advance_credit = share_amount`. Since `result = RND(share_amount + incidental_prepay - advance_credit, 2)`, on that tier **`result` reduces to `incidental_prepay`** identically.

- The **old** tail, *"the whole of that share is taken off and nothing further is asked for"*, asserts `result == 0`. That is true only where `incidental_prepay` is itself nil — the first of its three tiers, both a dining plan and a rental agreement held. On the other two tiers it asserts 0 where the policy asks for half the unit type's incidental hold, or the whole of it. **False on two branches of three.** That is P2, and it was a sentence claiming a nil outcome of the whole amount while the amount was not nil.
- The **new** tail, *"…the whole of that share is taken off, and the incidental hold collected in advance is still asked for"*, asserts that what survives the allowance is exactly the prepay the ladder settled. `result == incidental_prepay` on **all three** prepay tiers, the nil one included — where the prepay is nil, nothing survives and nothing is asked for, which the sentence also permits. **True on every branch.**

The ladder itself is untouched: `payments_already_collected` keeps its three `value` expressions (`share_amount`, `paid_to_date`, `0`), its `baseline`, its `bindings` and its `decides`. The three tiers remain pairwise disjoint and exhaustive as stated — tier 1 requires paid ≥ share, tier 2 requires at least one payment **and** paid < share, the fall-through is no payment at all.

One wording note is recorded as an observation at **L-1**: *"the incidental hold collected in advance"* takes its referent from the prepay sentences two sentences earlier, and a reader could in principle read it as the unit type's full hold rather than the share those sentences settled. The tier is unreachable on the only task that claims this policy, so no consequence can be demonstrated.

### R-2: did the narrowing change which requests any other binding counts?

**No.** Exactly three bindings in the whole charter read `lodging_requests`, and the auditor enumerated them from the `compute` expressions rather than from any list:

| policy | binding | expression filter | its basis sentence now |
| --- | --- | --- | --- |
| `lodging_ext_early_departure_charge` | `notice_requests` | `request_type='date_change', outcome='accepted_pending_confirmation'` | *"Where no request **to change the dates of** the stay stands accepted at the desk…"* |
| `lodging_ext_early_departure_charge` | `notice_date` | same | *"Where a request **to change the dates of** the stay stands accepted…"* |
| `lodging_ext_departure_settlement` | `dispute_requests` | `request_type='folio_dispute', outcome='accepted_pending_confirmation'` | *"Where no **folio dispute** about the stay stands accepted at the desk, nothing is held back."* — **unchanged; `lodging_ext_departure_settlement` has an empty diff this round** |

The compute always filtered `request_type='date_change'`; it was the prose that was wider. The narrowing brings the prose to the expression in the two places where they disagreed and touches nothing else. The folio dispute is still read where it belongs, by the settlement's `disputed_charges_held_back` factor, whose wording was already specific and was not edited.

**The old wording admitted a real second reading, and the demonstration is on task 1's own records.** That reservation carries three `lodging_requests` rows: a `date_change` standing accepted (2026-12-29), a `folio_dispute` standing accepted (2027-01-04), and a withdrawn `date_change` (2026-11-20). Read as the charter now reads, `notice_requests = 1`, `notice_date = 2026-12-29`, `notice_lead_days = 4`. Read as *"a request about the stay"* literally admitted, `notice_requests = 2` and `LATEST` returns the **folio dispute**, giving `notice_lead_days = −2`. Both fall in the same tier (−2 and 4 are each within the seven-day period), so the scored 630.12 is unchanged — but a reader following the old sentence reached the right number through the wrong record, and on a world where the dispute were raised earlier the two would part company. That is what R-2 removes.

### the 550.375 clause

Appended to the nightly-rate paragraph of `lodging_ext_early_departure_charge.rule` and to `compute_basis[retained_nightly]`, with the delta being exactly the clause in both:

> *"A nightly rate worked out under any of those three readings is a working figure and not an amount posted to a folio: it is carried at full precision, is never rounded on its own, and reaches the cent only through the amount the entry is posted at."*

**True of the compute.** `retained_nightly` is `posted_room_rate_a / MX(1, posted_room_nights_a)` or a published rate less the passholder reduction or the published rate itself — and **no branch of it is rounded**: the policy's only `RND` is in `result`, which the round-4 sweep established and which still holds. So the clause states what the expression does rather than adding a step.

**It does not disturb the baseline.** It was added to the `rule` and to one `compute_basis` entry and **not** to `baseline.rule` — `lodging_ext_early_departure_charge.baseline` is byte-identical to round 4, so the computation document's baseline still says exactly what it said, still names the same four `baseline.params`, and still yields **2116.00** on task 1's world. The requirement runs one way (every `baseline.rule` sentence must appear in the `rule`) and is satisfied.

### the sweeps, run independently

Two properties were re-derived rather than accepted, with the auditor's own scripts.

**Domain sweep.** Every equality filter in every `compute` expression was extracted with a regular expression and paired with the basis sentence for its binding; a filter narrows the domain, so the basis must name that narrowing in words. This auditor's enumeration finds **57** equality filters across the six policies where the reworker reports 97 — a difference of granularity in what is counted as a filter, not of substance. On the round-5 charter: **0 gaps.** Three apparent gaps in the first pass were artefacts of this auditor's own required-word list — a compound `event_type='lodging_room_charge', charge_category='extra_person'` is named in prose as *"the occupancy charge"* rather than as *"room rate"*, and *"resort, incidental and fee charge"* shares its noun — and resolve on inspection; the list was corrected and the sweep reports clean.

**The self-test is the part that matters, and it holds.** A sweep that passes because it looks for today's text proves nothing. Restoring round 1's *"a request about the stay"* wording to the four `compute_basis` entries and re-running reports **exactly two gaps — `notice_requests` and `notice_date`** — and no others. So the sweep detects R-2 when R-2 is reintroduced, and detects it in precisely the two places where the expression and the prose disagreed. That is the distinguishing evidence the coordinator asked for, and this auditor reproduced it independently rather than reading the reworker's output.

**Nil-claim sweep.** Every ladder tier whose stated outcome is nil was enumerated — twenty of them across the six policies — and each was checked against what its own binding does. In every case the tier claims nil **of its own binding**: a reduction percentage, a supplement share, a prepay, a credit, a count of nights, a parking rate multiplied by zero spaces. The only tier that claimed nil of the **whole amount** was the deposit allowance tail, and it no longer does. **0 tiers claiming a nil outcome of an amount that is not nil.**

### charter re-sweep (revision 5)

| property | result |
| --- | --- |
| base section and `variants` verbatim against the blueprint product | **0 differences** |
| non-fall-through ladder conditions verbatim in their own rule | **59 tiers, 0 misses** |
| `compute_basis` verbatim in its own rule, one per binding | **128 entries, 0 misses** |
| `overwrite` entries verbatim on both sides and in `base_policy_refs` | **14 of 14, 0 problems** |
| `baseline.rule` sentences present in the rule; `baseline.params` real | **0 misses, 0 unknown** |
| prerequisite sentences verbatim in the blocked rule | **4 of 4** |
| factor counts and labels | 6/4/4/5/6/4, every policy ≥2 `parameter` and ≥1 `method` |
| **round-4's tie-rule invariant** | **intact — 6 of 6 policies, 3 of 3 places, 0 gaps** |
| `prerequisite` graph, tool module | byte-identical across all five rounds |

### findings (revision 5)

**L-1 — observation: the referent of "the incidental hold collected in advance".**

- *Evidence.* `lodging_ext_reservation_deposit.rule`: *"…the whole of that share is taken off, and the incidental hold collected in advance is still asked for."* The phrase takes its referent from the prepay ladder two sentences earlier, where *"the known household share of the unit type's incidental hold is collected in advance against incidentals"* and *"the whole of the unit type's incidental hold is collected in advance"* are the two non-nil outcomes. A reader could in principle take *"the incidental hold"* as the unit type's published hold rather than as the share the ladder settled, which on the half tier would be 500.00 where the policy asks 250.00.
- *Why an observation.* The definite article points back at what the preceding sentences established as collected in advance, which is the ladder's outcome; and the tier is unreachable on task 0, the only task claiming this policy, where `paid_to_date` of 500.00 is below the share of 1117.29475 and the second tier applies. No second value can be demonstrated on either world. Recorded because the sentence that replaced a false one now leans on an antecedent rather than restating the quantity.
- *Affected artifact.* `lodging.extended.yaml` → `extended_policies[1].rule`, `.compute_basis.advance_credit`.

**J-1** (the decimal/binary gap in the published tie rule) is carried forward from revision 4 unchanged; nothing this round touches it.

## revision_5_disposition

| item | origin | verdict | decided by |
| --- | --- | --- | --- |
| **R-1 / P2** — the deposit allowance tier's tail claimed a nil outcome of the whole amount | render layer, substance in the charter | **CLOSED** | the replacement is true of the compute on **all three** branches of the surviving prepay ladder, where the old tail was false on two of three; the ladder's values, baseline, bindings, `decides` and disjointness are untouched |
| **R-2 / P3** — "a request about the stay" was wider than the expression's `request_type='date_change'` | render layer, substance in the charter | **CLOSED** | ten occurrences narrowed across two ladder conditions, three rule sentences and four basis entries; exactly three bindings in the charter read `lodging_requests` and the third, the settlement's folio dispute, is untouched (empty diff) |
| **P1** — "The four elements" against a charge that sums five | render layer | **CLOSED** | "The elements of the charge", in `rule`, `baseline.rule` and `compute_basis[result]`; which elements are named is unchanged |
| **550.375** — an unrounded working rate readable as a posted amount | render layer | **CLOSED** | the clause is true of the compute (`retained_nightly` is never rounded; the policy's only `RND` is in `result`) and is **not** in `baseline.rule`, which is byte-identical |
| **J-1**, **L-1**, **T0-9**, **G-2**, **G-3**, **T1-8**, **H-1**, **H-2** | revisions 2 to 5 | **carried forward, dispositions correct** | none costs either task a value; two would require editing `blueprint/` |

**Verified independently rather than accepted.**

| property | this audit's result |
| --- | --- |
| keys that decide a number (`compute`, `params`, `overwrite`, `prerequisite`, `baseline.params`, and the rest) | **identical in all six policies**; base section and variants identical |
| the four superseded wordings, counted across the whole charter | **0 occurrences each** |
| R-1's replacement true of the compute on every branch of its tier | **yes** — `result` reduces to `incidental_prepay` there, and the sentence names exactly that, the nil prepay tier included |
| bindings reading `lodging_requests` | **3**, enumerated from the expressions: two narrowed to match their `date_change` filter, one (`folio_dispute`) untouched |
| the second reading R-2 removes, demonstrated on task 1's rows | old prose → `notice_date` = the **folio dispute**, lead days **−2** instead of 4; same tier, so 630.12 unchanged, but through the wrong record |
| the 550.375 clause against the compute | **true** — `retained_nightly` unrounded on all three branches; `baseline.rule` byte-identical, 2116.00 unchanged |
| **domain sweep** | **57 equality filters, 0 gaps** (this auditor's enumeration; the reworker counts 97 — granularity, not substance). Three first-pass gaps were artefacts of this auditor's own word list and resolve on inspection |
| **domain sweep self-test** | **restoring round 1's wording reports exactly 2 gaps — `notice_requests` and `notice_date` — and no others.** The sweep detects R-2 when reintroduced, so it is not passing by looking for today's text |
| **nil-claim sweep** | **20 nil-claiming tiers, every one claiming nil of its own binding; 0 claiming it of an amount that is not nil** |
| round-4 tie invariant | **intact — 6 of 6 policies, 3 of 3 places, 0 gaps**; the same two dyadic ties, 0 clause/`RND` divergences |
| derivation sweep | **29 of 29 `tier_taken`**, 29 of 29 fork counts, 0 seed-world tiers, 20 ordinals and 22 rationale claims clean |
| every scored value, baseline, sensitivity, edge figure, world and persona | **unchanged**, by numeric re-run and then by the record |

The reworker's `1 mismatch before the rebuild, 0 after` is confirmed and is the derivation working: `tier_taken` is read off the current ladder, so narrowing the ladder moved `computations[2].factor_sensitivity[1].tier_taken`, and the rebuild carried it.

## closing_checklist (revision 5)

Supersedes revision 4's; earlier checklists stand as the record of what was true then.

| item | state |
| --- | --- |
| per-task files one-to-one, `_difficulty.md` alongside; revisions 1–4 untouched | holds |
| **freeze order kept this round** | holds — both derivations on disk before the record was opened, correcting the breach disclosed in revision 4 |
| every comparison section carries a PASS | holds — both tasks, all four relationships |
| scopes, trees, `owner=user` writes, DAG | holds — `prerequisite` byte-identical across five rounds |
| factors: counts, labels, ≥3 tiers verbatim in the rule, distinct outcomes | holds — 59 tiers, 0 misses |
| every factor bears weight against an honest baseline | holds — 29 of 29 |
| no tier read off a stamp | holds |
| proof fields assert only what the world produces | holds — 29 `tier_taken`, 20 ordinals, 22 rationale claims, 29 sensitivities, 6 baselines, 4 edge figures |
| every scored value entailed by the text rather than the evaluator | holds — the tie invariant survives this round intact |
| **every rule and basis sentence's domain matches the expression beside it** | **holds — new this round.** 57 filters, 0 gaps, with a self-test that fires on R-2 when it is reintroduced |
| gates re-run on the final form | all green, TRACEABILITY OK, COMPUTE counts identical to revisions 2–4 in every column |

**Difficulty verdict (revision 5): all four relationships PASS on both tasks.**

This difficulty passes the source-layer audit. Across five rounds the arithmetic never moved — every one of the 29 sensitivities and 6 whole baselines has been identical since revision 2, and every scored value since the world was last re-dated in revision 2. What moved, each round, was the text's grip on that arithmetic: declarations (rounds 1–2), a tier derived rather than transcribed (round 3), a rounding mode pinned rather than left to the evaluator (round 4), and now a sentence's domain matched to the expression it describes (round 5). The pattern is worth naming: every defect this difficulty has had was a sentence that was true of the world but not of the policy, or true of the policy but not of every branch. None was a wrong number.

**Two limits of this audit's method are now on record and should be read with this verdict.** Revision 4 recorded the first: this audit derives by running the policy's own `compute`, so a convention living in the evaluator rather than in a sentence cannot present itself here as an ambiguity, and the checklist item that would have caught it — *rounding mode*, named separately from *rounding point* — was read too quickly. Round 5 adds the second, and it is the same shape: a sentence whose **domain** is wider than the filter beside it produces the right number for the wrong reason, and an audit that checks *"does the compute give gold"* will never see it. Both are cases where the compute is right and the prose is not, and both were found by an auditor working from prose alone. The domain sweep and the rounding sweep are now written down, need only the charter and the two worlds, and are the checks that close that gap from this side.

**A disposition error of this audit is also on record.** Round 4 identified P1–P3 as defects in the charter's own rule text and then declined to change them, reasoning that a source-side edit would leave the corpus disagreeing with the charter. The reasoning inverted the dependency: the corpus is rendered **from** the charter, so a charter defect closed in the corpus is what makes the two disagree — which is what happened, and what the two `BIJECTION RED`s were. The finding was right; the disposition was wrong, and it cost a render cycle.
