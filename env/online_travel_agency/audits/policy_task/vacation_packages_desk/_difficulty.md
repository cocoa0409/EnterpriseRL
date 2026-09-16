# Policy-task audit — vacation_packages_desk / charter-global

## charter_global_frozen

| item | value |
| --- | --- |
| extended charter | `env/online_travel_agency/tasks/vacation_packages_desk/bundle.extended.yaml` sha256 `7f1999dda15428e9107f85fb6d8d2353bd139b83f228ba4be0a189b945f190c5` |
| tool module | `env/online_travel_agency/tasks/vacation_packages_desk/task_tools.py` sha256 `5444f81bdd2ed918268acfd56653f372d4e3faabed45b7fb2c5c65f4ab7e4994` |
| freeze time (charter-global section) | 2026-09-16 12:40 UTC |
| auditor | independent source-layer auditor, revision 1 |
| entry condition | instantiation gates supplied verbatim with the brief and all green (EXTENDED / TASK-TOOL-CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE). `check_traceability.py` correctly deferred to the KB stage. Entry condition accepted; a machine green light is a qualification to enter, not a proof of correctness. |

Fields permitted while this section was written: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`,
`blueprint/share_tools.py`, `blueprint/products/bundle.yaml` (this category's base charter),
`blueprint/products/club.yaml` (read only to check that the cross-difficulty factors' tiers rest on
values that product's own charter publishes), the whole of `bundle.extended.yaml`, the whole of
`task_tools.py`.

Fields explicitly masked while this section was written: **every** task file field other than
`frozen_time`, `user_scenario`, `initial_state` — i.e. `evaluation_criteria`, `computations`,
`charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`,
`prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`. Nothing in this section is
derived from a revealed GT field; it was written before either task's GT was opened.

### policy_conflict_scan

Base section of `bundle.extended.yaml` verified **byte-equivalent** to `blueprint/products/bundle.yaml`
for every shared key (`category`, `display_name`, `binding`, `lifecycle`, `accounts`,
`parameter_schema`, `variants`, `events`, `measures`, `policies`) by structural comparison. The base
copy has not been rewritten.

Extended policies and their claims:

| policy | subject | computes | target_tool | trigger |
| --- | --- | --- | --- | --- |
| `bundle_ext_operator_surcharge_pricing` | `bundle_component_charge` | `surcharge_amount_usd` | `price_package_surcharge_8a2d0e07` | state_due |
| `bundle_ext_balance_settlement` | `bundle_final_payment_charge` | `balance_due_usd` | `settle_package_balance_32304520` | on_request |
| `bundle_ext_party_amendment_charge` | `bundle_penalty_charge` | `amendment_charge_usd` | `withhold_amendment_charge_5474525c` | state_due |
| `bundle_ext_places_given_up` | `bundle_party_amend` | `revised_package_price_usd` | `confirm_places_given_up_54f63279` | on_request |

Overlapping subjects, triggers, eligibility, time anchors, action parameters, terminal states,
cross-category read boundaries:

- No two extended policies share a `computes` name or a `target_tool`; the four subjects are four
  distinct event families. No overlap to reconcile between extended policies themselves.
- Inherited base eligibility that still binds each extended subject (none is named in any
  `overwrite`, so all are inherited in full):
  `bundle_payment_schedule.price_guarantee_elapsed` (time) binds `bundle_final_payment_charge`;
  `bundle_components.package_live` (state, allowed `deposit_held|confirmed|travelling`) binds
  `bundle_component_charge`; `bundle_amendment.change_request_approved` (authorization) binds
  `bundle_party_amend`; `bundle_cancellation.places_given_up_stated` (caller_fact) binds
  `bundle_cancel`/`bundle_predeposit_cancel` only and therefore does **not** formally reach
  `bundle_ext_places_given_up`, which routes a partial give-up through `bundle_party_amend`.
- Cross-category reads: all four extended policies declare `club` and only `club`. Every read is a
  `CPARAM`/`CFIELD`/`XCOUNT` against `club_memberships` / `club_points_entries`, and every parameter
  read (`package_discount_pct`, `agency_service_fee_waiver`, `waived_change_fees_per_year`) is a real
  published parameter of `blueprint/products/club.yaml`. Read boundary is consistent; nothing writes
  to another category.
- Task scope exclusivity: task 0 claims `{bundle_ext_balance_settlement,
  bundle_ext_operator_surcharge_pricing}` and task 1 claims `{bundle_ext_places_given_up,
  bundle_ext_party_amendment_charge}` (derived independently from each task's world and persona, not
  from `charter_scope`). The two scopes are pairwise disjoint and jointly cover all four extended
  policies; each scope spans one whole problem tree (root + its single prerequisite problem).
- Conflicts **between base and extended** are real and are recorded in `override_declarations` below.

### rule_compute_equivalence

Check 2 run over all four extended policies. Every `compute` binding carries a `compute_basis` entry
whose text is a verbatim sentence or clause of that policy's own `rule`; every quantity, window,
filter, tier, branch, cross-category read, acting base, grouping, cap/floor, rounding mode and
rounding point that the `rule` promises has an implementing binding. The sweep back found the
following, none of which is a numeric divergence on either task's world but all of which are
recorded:

1. **`bundle_ext_places_given_up.occupancy_adjustment` implements a basis the rule never states.**
   Rule: "Where the rooms or cabins shown on the package record leave a traveller occupying one alone
   once the places given up are taken away…". Compute: `2 * F('rooms_or_cabins') - (heads_before - 1) > 0`.
   The factor **two travellers per room or cabin** appears in no sentence of this rule, of the
   baseline, or of any base policy; `bundle_agg_party_pricing` in fact contemplates a third adult and
   a child sharing one room, i.e. three. A reader cannot derive the compute's occupancy basis from the
   rule. Observation (the two readings agree on task 1's world; see `1.md`).
2. **Rule condition "whose tier carries a package discount" is implemented as "an active membership
   exists".** `bundle_ext_operator_surcharge_pricing.borne_rate` and
   `bundle_ext_party_amendment_charge.waiver_credit` branch on `club_tier_package_pct != None` /
   `club_waivers_granted != None`, not on the value being above nil. A Wanderlane Blue member
   (`package_discount_pct: 0`, `waived_change_fees_per_year: 0`) falls into the rule's fall-through
   tier but into the compute's first or second tier. Numerically inert (0 % and a 0-grant both
   reduce to the fall-through value), so an observation, not a red light.
3. **`bundle_ext_balance_settlement.club_discount_pct` and
   `bundle_ext_places_given_up.club_rate` have no compute branch for the rule's fall-through.**
   Both rules state a fall-through ("the package discount applied to the quoted price is nil" /
   "the club rate … is the whole of them and nothing more") that is reached when the traveller holds
   no active membership. The compute reaches `DAYS(CFIELD('club', …, status='active'), …)` before any
   guard, so on a world with no active membership the binding raises rather than taking the
   fall-through. Neither task's world exercises it. Observation.
4. `bundle_ext_operator_surcharge_pricing.compute_basis['club_active']` quotes the *second* tier
   sentence of the loyalty ladder rather than a sentence about membership status, and
   `compute_basis['payment_lines']` / `['notice_lines']` / `['component_lines']` likewise quote the
   ladder's second tier. Every quoted string is a verbatim clause of the same rule and every tier of
   every ladder is quoted somewhere in the policy's `compute_basis`, so the two-way correspondence
   holds; the pairing is loose rather than lossy. Observation.

Ladder-level equivalence (every tier named in `factors[].ladder` is a sentence of the `rule` and a
branch of the `decides` binding, and every branch of each `decides` binding is a tier the rule
states) was checked tier by tier for all eighteen factors and holds. No tier lives only in `compute`,
and no tier is promised by the rule and absent from `compute`.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: four distinct tools, four distinct computed names, each claimed by
  exactly one policy. No policy adds a confirmation, review, wait or procedure outside itself.
- Tool bodies (`task_tools.py`): every function is a single `ctx.create` or `ctx.update` with no
  branch, no lookup and no rejection. No tool judges eligibility or a prerequisite. Verified by
  reading all four bodies.
- uuid8 check, tool by tool: `8a2d0e07`, `32304520`, `5474525c`, `54f63279`. All four are distinct,
  none is a tail-variant of another, none is sequential or adjacent, and none looks derived from a
  common seed. `5474525c` and `54f63279` share their first two characters and `32304520` happens to
  contain only decimal digits; both are within ordinary chance for independently drawn hex and the
  remaining characters are unrelated. PASS, with the coincidence noted.
- Docstring sequence discipline: no docstring names another tool, states a position in a sequence, or
  carries before/after/first. `withhold_amendment_charge_5474525c`'s `source_entry_id` says "the
  payment line **already standing** on the package"; this refers to a record, not to another tool's
  call, and is the weakest wording in the module. Observation only.

### prerequisite_graph

Check 7 over the whole graph.

| blocked policy | problem | kind | gate | form | resolved_by | acyclic |
| --- | --- | --- | --- | --- | --- | --- |
| `bundle_ext_balance_settlement` | `bundle_ext_operator_surcharge_pricing` | value_input | `charges_on_ledger` | state | `price_package_surcharge_8a2d0e07` | yes |
| `bundle_ext_places_given_up` | `bundle_ext_party_amendment_charge` | value_input | `withheld_charges` | state | `withhold_amendment_charge_5474525c` | yes |

- `prerequisite` is filled in on all four policies (`[]` on
  `bundle_ext_operator_surcharge_pricing` and `bundle_ext_party_amendment_charge`).
- Both `problem` values point at another extended policy id **in this file**; neither points at a base
  policy or at itself. The whole graph is two disjoint edges — acyclic, and no cycle is created across
  the two tasks.
- Both `policy_source` strings are verbatim locatable in the **blocked** policy's own `rule`
  (`bundle_ext_balance_settlement` sentence 2; `bundle_ext_places_given_up` sentence 2).
- `form: state` on both, and `fallback_reason` is absent on both — correct, since it is required
  exactly on action-form edges. No action-form edge exists in this charter, so the state form's
  priority is honoured everywhere and there is no fallback to test.
- `condition` is neither strengthened nor weakened relative to the sentence: "carries a surcharge line
  answering every surcharge the operator has notified" → "carries a surcharge line answering every
  surcharge notice standing against the package"; "carries the amendment charge owed for the change to
  the travelling party" → "carries an amendment charge answering the change to the travelling party".
- `resolved_by` is the depended-on policy's own `target_tool` in both cases, and each tool genuinely
  produces the state `effect` describes: `price_package_surcharge_8a2d0e07` creates a
  `bundle_component_charge` row (`charge_category: fuel_surcharge`) that enters
  `SUM(… event_type='bundle_component_charge')`, i.e. `charges_on_ledger`;
  `withhold_amendment_charge_5474525c` creates a `bundle_penalty_charge` row
  (`charge_category: amendment_fee`) that enters `SUM(… event_type='bundle_penalty_charge')`, i.e.
  `withheld_charges`.
- `kind: value_input` matches `gate` in both cases: `charges_on_ledger` and `withheld_charges` are
  real binding names in the blocked policy's own `compute`, not eligibility gates.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears
  anywhere in either `prerequisite` block.

PASS.

### prerequisite_sentences

Check 6, four-point test on each of the two edges.

**Edge A — `bundle_ext_balance_settlement` waits on `bundle_ext_operator_surcharge_pricing`.**
Sentence: *"The balance is worked out only after the package ledger carries a surcharge line
answering every surcharge the operator has notified against the package."*
(i) It joins this policy's own result ("the balance is worked out") to what it waits on with the
ordering connective **"only after"**. (ii) What it waits on is a record-visible state — "the package
ledger carries a surcharge line" — named in the words the tables and the finders use
(`bundle_ledger_entries`, "surcharge line", "operator notice"), with no action, performer or tool:
state form, correctly declared. (iii) It names no tool, no policy id, no snake_case token and no row
id. (iv) Its strength matches `condition` exactly (every notice standing, not some).
*One write brings the state about*: of this difficulty's four tools only
`price_package_surcharge_8a2d0e07` creates a ledger line that answers an operator surcharge notice
(`charge_category: fuel_surcharge`, `reason_code: surcharge_notice`);
`settle_package_balance_32304520` creates a `final_payment` line, `withhold_amendment_charge_5474525c`
a `penalty_charge` line, and `confirm_places_given_up_54f63279` writes no ledger line at all. The hop
resolves uniquely.
*Derivation in one reading*: the sentence says the balance waits on a surcharge line answering every
notified surcharge → the records show an operator notice advising a surcharge and no ledger line
answering it → the only policy whose own rule describes pricing a notified surcharge onto the ledger
is `bundle_ext_operator_surcharge_pricing` ("A surcharge notified by the operator is priced onto the
package ledger as one line for the whole party") → its result is the write that must come first. No
second reading is available.
*No second wording*: `bundle_ext_balance_settlement`'s rule says nothing else about this dependency —
no tool name, no other policy's id, no repeated statement. `bundle_ext_operator_surcharge_pricing`'s
own rule does **not** restate the sentence.

**Edge B — `bundle_ext_places_given_up` waits on `bundle_ext_party_amendment_charge`.**
Sentence: *"The price the package carries for the party actually travelling is fixed only after the
ledger carries the amendment charge owed for the change to the travelling party."*
(i) Ordering connective **"only after"**, joining this policy's own result (the price the package
carries) to what it waits on. (ii) Record-visible state — "the ledger carries the amendment charge
owed for the change to the travelling party" — in table words, no performer, no tool: state form,
correctly declared. (iii) No tool, policy id, snake_case token or row id. (iv) Strength matches
`condition`.
*One write brings the state about*: only `withhold_amendment_charge_5474525c` creates a
`bundle_penalty_charge` / `amendment_fee` line. Unique.
*Derivation in one reading*: the sentence says the revised price waits on the amendment charge owed
for this change → the only policy whose own rule describes building that charge is
`bundle_ext_party_amendment_charge` ("The amendment charge withheld for a change to the travelling
party is built from the product's administration charge and the travellers it is charged for") → its
result is the write that must come first.
*No second wording*: no restatement in either rule.
*Discoverability caveat*: the state as worded — "the ledger carries the amendment charge" — is
distinguished from an amendment charge already standing for an **earlier** change only by reading
dates against the change request. Task 1's world contains exactly such an earlier line; the
demonstration and the row paths are in `1.md` under `problem_chain`. Recorded there as an
observation, not here.

**Cross-problem orders stated in a rule that ground no declared edge.** One candidate found:
`bundle_ext_party_amendment_charge`'s closing sentence *"The charge is withheld against the payment
line that settled the balance of the package, and against no other."* This names a **record** (a
payment line) rather than another problem's result, and carries no ordering connective over another
policy's result, so it is not an undeclared dependency on the face of it; in both tasks of this
difficulty the line it names is already seeded. Recorded as an observation.

No **base** rule sentence is relied on to ground either edge: both `policy_source` strings are
sentences of the extended rules.

PASS, with the two observations above.

### override_declarations

Check 1's **finding half**, run once, sentence by sentence against every entry of every extended
policy's `base_policy_refs`. Declared overrides first:

| policy | overwrite entries | verdict |
| --- | --- | --- |
| `bundle_ext_operator_surcharge_pricing` | 1, against `bundle_evt_supplier_notice`'s "Several notices about the same package are not added together; the last notice standing before departure decides what is owed and what may be refused." | declared correctly; the base sentence is named verbatim and the replacement is unique |
| `bundle_ext_balance_settlement` | `[]` | see F-1, F-2, F-3 |
| `bundle_ext_party_amendment_charge` | `[]` | see F-4, F-5 |
| `bundle_ext_places_given_up` | `[]` | see F-6, F-7 |

Undeclared deviations found. Each is a base sentence that the cited extended policy handles
differently for a quantity that ultimately gets scored, with nothing naming it in that policy's
`overwrite`. Consequences are demonstrated in the task files, never here.

**F-1 — instalment split.** `bundle_payment_schedule` (cited by `bundle_ext_balance_settlement`):
*"A product that allows instalments splits the balance into its own number of equal instalments
falling due at equal intervals between the deposit and the final-payment date, and the last
instalment is adjusted for rounding."* Extended: *"the figure taken now is instead the outstanding
amount divided by the product's number of instalments less those already taken."* Base fixes every
instalment at balance ÷ N; extended re-divides whatever is still outstanding by the instalments that
remain. The two agree only where the instalments already taken were each exactly balance ÷ N. Bears
on **task 0**.

**F-2 — agency service fee.** `bundle_booking_terms` (cited by `bundle_ext_balance_settlement`):
*"The agency service fee is charged per traveller when the deposit is taken and is never returned."*
Extended carries the fee into the **balance** where no fee line stands, and waives it altogether
where the club tier waives it. Base states it is charged at deposit and says nothing that permits a
club tier to remove it. Bears on **task 0** (the recovery branch is taken there; the waiver branch is
not).

**F-3 — club tier claw-back at balance.** `bundle_club_and_corporate_interaction` (cited by
`bundle_ext_balance_settlement`): *"the club tier held on the deposit date decides the package
discount applied to the price"* and *"Where the member's tier changes between deposit and departure,
the discount applied at deposit stands and is neither topped up nor clawed back."* Extended halves
the discount where the membership's `status_expiry_date` falls on or before departure — a reduction
decided by what happens between deposit and departure. Bears on **task 0** only in principle: task 0's
membership expires after departure, so the halving branch is not taken there and no consequence is
demonstrable on either task's world. Recorded as a finding without a demonstrated consequence.

**F-4 — name-change rate and the travellers it multiplies.** `bundle_amendment` (cited by
`bundle_ext_party_amendment_charge`): *"A member of the party may be replaced only up to the product's
name-change deadline before departure, against the product's name-change charge per traveller
replaced."* Extended selects the name-change charge from the **existence of an approved name-change
request** and multiplies it by the **travellers charged** (the adults, or the adults and children, on
the record) rather than by the travellers replaced; and its first tier prices a change falling *at or
inside* the deadline, which base permits no member to be replaced within at all. Together with
`bundle_agg_party_pricing`'s *"Where the party shrinks after booking the remaining travellers are
re-priced at the occupancy they are left with, and the re-pricing is charged as an amendment rather
than absorbed"*, base gives the amendment administration charge for a shrink where extended gives a
share of the name-change charge. Bears on **task 1**.

**F-5 — the cancellation ladder on places given up.** `bundle_cancellation` (cited by
`bundle_ext_party_amendment_charge`, and governing the same event family `bundle_penalty_charge`):
*"Where some but not all of the party give up their places, the ladder is applied to those places
alone and the travellers who remain are re-priced at the occupancy they are left with."* and *"The
product's administration charge is withheld per traveller on every cancellation whatever the ladder
says."* Extended prices a partial give-up as an amendment and withholds no ladder penalty at all,
declaring nothing superseded. Bears on **task 1**.

**F-6 — club tier claw-back at re-pricing.** `bundle_club_and_corporate_interaction` (cited by
`bundle_ext_places_given_up`), same two sentences as F-3. Extended halves the package discount where
the membership's `tier_review_date` falls on or before departure. Bears on **task 1**.

**F-7 — single supplement on a discounted traveller.** `bundle_agg_party_pricing` (cited by
`bundle_ext_places_given_up`): *"A traveller occupying a room or cabin alone carries the product's
single supplement, a third adult sharing takes its third-adult discount, and a child within the
product's child age takes its child discount; **the supplement and the discounts never apply to the
same traveller at once**."* Extended's `occupancy_adjustment` adds the single supplement from the
rooms-versus-heads arithmetic alone, with no test of whether the traveller left alone is one who
already carries a discount. Bears on **task 1**.

**F-8 — surcharge cap versus the party's right to refuse.** `bundle_evt_supplier_notice` (cited by
`bundle_ext_operator_surcharge_pricing`): *"A surcharge at or below the product's threshold share of
the package price must be paid, and a surcharge above it entitles the party to cancel with nothing
withheld or to accept a comparable alternative."* Extended converts this into a **cap**: the surcharge
priced is "held at no more than the product's threshold share of the package price". Base does not
reduce a surcharge above the threshold; it gives the party a right. The `overwrite` block names only
the *"Several notices…"* sentence, not this one. On task 0's world the cap does not bind
(2 269.80 × 0.94 = 2 133.61 against a cap of 2 291.20), so no consequence is demonstrable on either
task. Recorded as a finding without a demonstrated consequence.

**F-9 — surcharge timing relative to the price-guarantee term.** Same base policy: *"A surcharge may
be added after booking only on a product that allows it, only after the product's price-guarantee
term has run out, and only where the party is notified at least the product's notice days before
departure."* The extended policy tests none of these three and declares none superseded. Whether the
base clause is violated on task 0's world turns on whether "added" means *notified* or *priced*; the
two readings and their figures are set out in `0.md`. Recorded as a finding; graded there as an
observation because the base sentence itself admits two readings.

**F-10 — "the two are never both taken".** `bundle_booking_terms` (cited by
`bundle_ext_balance_settlement`): *"The deposit is the product's flat amount per traveller, or its
share of the package price where the product takes a share; the two are never both taken."* Four of
the six products (All-Inclusive Resort, Escorted Tour, Ocean Cruise, Luxury Collection) publish a
non-zero `deposit_per_person_usd` **and** a non-zero `deposit_pct`, so the base sentence does not by
itself say what a product's standard deposit is. Extended's "the product's standard deposit **for the
deposit lines it was taken in**" points at the per-line flat amount and so resolves it, but only
implicitly. Bears on **task 0**; graded there.

Base provisions **not** hit by any of the above and inherited in full, confirmed sentence by
sentence: `bundle_agg_multi_holding` (whole), `bundle_booking_terms` sentences 1–2 and 5 (sale
window, party-size and group thresholds, quotation holds no allocation),
`bundle_payment_schedule` sentences 1–3 and 5–7 (due date, price-guarantee gate and its counting
rule, pay-in-full-at-booking, currency markup as each payment is taken, non-payment),
`bundle_components` (whole, including the `package_live` state gate), `bundle_refund_settlement`
(whole; no extended policy touches payouts), `bundle_credit` (whole), `bundle_travel_period` (whole),
`bundle_amendment`'s change-request authorization, and `bundle_evt_supplier_notice`'s materiality and
significant-change clauses.

### factor_ladders

Charter-global structure only. Whether a factor bears weight is a fact about one world and lives in
the task files under `factor_weight`.

| policy | factors | parameter | method | ≥3 disjoint tiers each | every tier in the `rule` and in `compute` | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| `bundle_ext_operator_surcharge_pricing` | 4 | 3 | 1 | yes | yes | 2 × `club` |
| `bundle_ext_balance_settlement` | 5 | 4 | 1 | yes | yes | 2 × `club` |
| `bundle_ext_party_amendment_charge` | 4 | 3 | 1 | yes | yes | 1 × `club` |
| `bundle_ext_places_given_up` | 5 | 3 | 2 | yes | yes | 1 × `club` |

Every policy declares between four and six factors, at least two labelled `parameter` and at least one
labelled `method`. Every ladder has exactly three tiers, the fall-through counted, and the tiers are
pairwise disjoint **as stated** (each pair of leading tiers is separated by a complementary clause —
"advises a surcharge above nil" / "no earlier notice … advises a surcharge above nil"; "at least one
package accrual" / "no package accrual"; "shows children travelling" / "shows no children
travelling"; "more than the frequent-traveller threshold" / "exactly the frequent-traveller
threshold"; "falls after the departure date" / "falls on or before"; "falls short of" / "meets or
exceeds"; "waives" / "does not waive"; "at least one instalment has already been taken" / "no
instalment has yet been taken"; "every payment" / "some but not all"; "at or inside the deadline" /
"more than the deadline"; "carries a child discount line and shows children" / "carries a third-adult
discount line and shows no children"; "more than one amendment or name-change charge" / "exactly
one"; "fewer waivers used than granted" / "as many or more"; "leave a traveller occupying one alone" /
"leave no traveller occupying one alone"; "stands at confirmed" / "stands at deposit held"; "has run
out" / "has not yet run out"). Every tier's value or method is drawn from the charter — a variant
parameter, a `params` constant published on the policy, or a club-charter parameter — and no tier
names a computation rule the charter nowhere states.

Multi-source tiers (every tier beyond the fall-through a conjunction over distinct records):
`notice_selection_rule` (two distinct notice rows), `club_tier_rate_concession` (membership row +
points rows), `party_head_basis` (ledger row + package record), `frequent_traveller_loyalty_rate`
(points rows + membership row), `club_package_discount` (membership row + package record),
`agency_service_fee_recovery` (ledger + membership), `change_request_admin_rate` (change-request row +
package record), `travellers_charged_basis` (ledger + package record), `repeat_amendment_loading`
(ledger + package record), `club_change_fee_waiver` (membership + points rows),
`per_place_price_basis` (ledger + package record), `withheld_charge_carry` (ledger + package record),
`club_repricing_rate` (membership + package record), `price_guarantee_repricing` (package record +
ledger). Each task therefore has several multi-source factors, well above the floor of one.

Cross-difficulty: six of the eighteen factors decide their tier from the `club` difficulty's records —
two in each of the two tasks' computations, above the floor of one per task. The categories read are
`club` only.

Label honesty, factor by factor:

- Honest `method` labels: `notice_selection_rule` (selects **which** notice row is the source — a
  candidate-order rule, not a number), `instalment_split_method` (selects whether the outstanding
  amount is divided, and by what divisor — the algorithm changes), `travellers_charged_basis`
  (selects **which heads** are aggregated), `per_place_price_basis` (selects both the numerator —
  price alone or price plus components — and the denominator).
- **Questionable `method` label**: `bundle_ext_places_given_up.withheld_charge_carry`. Its three tiers
  are "carried in full", "carried at the part-paid share", "nothing carried" — a 1 / 0.5 / 0
  multiplier applied to one fixed quantity, which is the shape the skill calls a `parameter`. No
  count is breached by re-labelling it (`bundle_ext_places_given_up` would still hold 1 `method` and
  4 `parameter`), so this is an **observation**, not a red light.
- Every `parameter` label was checked to substitute a number into an unchanged formula; none changes
  an algorithm.

`decides` targets: all eighteen point at an **input** binding (`notified_rate`, `borne_rate`,
`head_basis`, `loyalty_rate`, `club_discount_pct`, `deposit_shortfall_due`, `service_fee_due`,
`instalment_due`, `loading_rate`, `admin_rate`, `travellers_charged`, `history_rate`,
`waiver_credit`, `per_place_price`, `occupancy_adjustment`, `carried_charges`, `club_rate`,
`repricing_rate`), never at `result`. Binding sets are disjoint within each policy.

Baselines: each of the four policies declares a `baseline.rule` that is a strict subset of the
sentences of its own `rule` (verified sentence by sentence) with every factor's fall-through
substituted, and each factor's `baseline` binding is the fall-through value that `baseline.rule`
states for that input. `baseline.params` names `surcharge_threshold_pct` /  (none) /
`amendment_admin_fee_per_person_usd` / (none); the two empty lists are correct — those baselines use
only package-record fields and product parameters already named in the surviving sentences.
Whether each baseline yields a **definite number different from gold** on a given world is a per-task
fact and is settled in the task files.

### findings

Charter-global findings, each naming the tasks whose files carry the demonstration.

| id | verdict | subject | bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-POLICY RED (undeclared override) | `bundle_payment_schedule` equal-instalment split vs extended remaining-instalment split | task 0 |
| F-2 | observation | `bundle_booking_terms` agency service fee charged at deposit vs recovered in the balance / waived by tier | task 0 |
| F-3 | finding, no demonstrated consequence | `bundle_club_and_corporate_interaction` no-claw-back vs expiring-tier halving | task 0 (branch not taken) |
| F-4 | SOURCE-POLICY RED (undeclared override) | `bundle_amendment` name-change charge *per traveller replaced* vs extended rate × travellers charged, and pricing a change inside the deadline base forbids | task 1 |
| F-5 | SOURCE-POLICY RED (undeclared override) | `bundle_cancellation` ladder on places given up vs extended charging no ladder | task 1 |
| F-6 | SOURCE-POLICY RED (undeclared override) | `bundle_club_and_corporate_interaction` no-claw-back vs review-pending halving | task 1 |
| F-7 | SOURCE-POLICY RED (undeclared override) | `bundle_agg_party_pricing` "the supplement and the discounts never apply to the same traveller at once" vs unconditional single supplement | task 1 |
| F-8 | finding, no demonstrated consequence | `bundle_evt_supplier_notice` right-to-refuse above the threshold vs extended cap at the threshold | task 0 (cap does not bind) |
| F-9 | observation | `bundle_evt_supplier_notice` surcharge only after the price-guarantee term has run out; extended tests nothing | task 0 |
| F-10 | observation | `bundle_booking_terms` "the two are never both taken" against variants that publish both | task 0 |
| F-11 | observation | `occupancy_adjustment` implements a two-per-cabin basis no sentence states | task 1 |
| F-12 | observation | rule "whose tier carries a package discount" implemented as "an active membership exists" | both |
| F-13 | observation | club branches have no compute path for the rule's own fall-through (no active membership) | both |
| F-14 | observation | `withheld_charge_carry` labelled `method` but tiers are a 1 / 0.5 / 0 multiplier | task 1 |
| F-15 | observation | `bundle_ext_party_amendment_charge`'s closing sentence names the balance-settling payment line, an implicit ordering that grounds no declared edge | both (line seeded in each) |
| F-16 | observation | uuid8s `5474525c` and `54f63279` share a two-character prefix; no evidence of derivation | — |

## closing_checklist

Written after both tasks' reveals. This is the one difficulty-level conclusion reached **after** the
GT was opened, so it sits below the charter-global section, which stays pre-reveal by construction.

**The difficulty does not close.** Two of the four relationships fail on at least one task.

| item | result |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside | yes — `0.md`, `1.md`, `_difficulty.md` in `env/online_travel_agency/audits/policy_task/vacation_packages_desk/` |
| old revisions traceable | revision 1; no prior revision existed |
| every comparison section carries a PASS | **no** — `0.md` records SOURCE-POLICY RED + SOURCE-CHAIN RED; `1.md` records four SOURCE-POLICY REDs |
| this difficulty's extended policies fully covered | yes — task 0 claims `bundle_ext_operator_surcharge_pricing` + `bundle_ext_balance_settlement`, task 1 claims `bundle_ext_party_amendment_charge` + `bundle_ext_places_given_up`; 4 of 4 |
| the M task scopes pairwise disjoint, each spanning a whole tree | yes — disjoint in policies and in tools; each scope is one root plus its one prerequisite problem |
| task tools and GT closed | yes — four tools, four `(target_tool, computes)` claims, four gold writes; replay closure 18 of 18 rows on both tasks |
| each task tool uses an independently generated, frozen uuid8 | yes — `8a2d0e07`, `32304520`, `5474525c`, `54f63279`, distinct and non-derived (see `action_binding_and_uuids`) |
| every tree has 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` problem, no cycle | yes — each tree: n = 1, one `value_input` edge, root resolved by an `owner=user` tool (`settle_package_balance_32304520`, `confirm_places_given_up_54f63279`) |
| the whole difficulty's `prerequisite` edges are a DAG with no cross-task cycle | yes — two disjoint edges |
| every computation declares a self-sufficient baseline and 4–6 factors (≥2 `parameter`, ≥1 `method`; ≥1 multi-source and ≥1 cross-difficulty per task) | yes — 4 / 5 / 4 / 5 factors; per-task multi-source 9 of 9 and cross-difficulty 4 (task 0) and 2 (task 1) |
| every ladder ≥3 tiers stated in full in its rule | yes — eighteen ladders, three tiers each, every tier a sentence of its own rule and a branch of its `decides` binding |
| every factor proved to bear weight against an honest baseline, baseline alone giving a definite number different from gold | yes — all eighteen move their scored figure; whole-baseline fall-backs 0.00 / 19 014.61 / 260.00 / 23 610.00, all definite and all different from gold. *Observation*: task 0's computation A falls back to **0.00**, so the baseline document yields "no surcharge payable" rather than a mis-sized figure |
| instantiation-stage gates re-run once on the final form | yes — re-run 2026-09-16 13:02 UTC from the repository root with `DIFF=env/online_travel_agency/tasks/vacation_packages_desk`: EXTENDED OK; TASK TOOL CONTRACT OK (4 tools); REPLAY OK (0.json 10 acts, 1.json 12 acts, det True, nonvac True, 0 errs, closure 18/18 both, match True); SOLVABILITY OK; COMPUTE OK (branches 29 / 24, steps 10 / 12, suite means 26.50 and 11.00, history_rows_max 13); GROUNDING OK; SCOPE OK. Identical to the entry snapshot — no artifact was touched by this audit |

### per-task verdicts

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **SOURCE-POLICY RED** (0-1) | **SOURCE-CHAIN RED** (0-2) | PASS | **FAIL** (consequence of 0-1) |
| 1 | **SOURCE-POLICY RED** ×4 (1-1 … 1-4) | PASS | PASS | **FAIL** (consequence of 1-1 … 1-4) |

Both independent derivations reproduced every scored parameter, every tier, every baseline figure and
the whole write order exactly (`0.md` and `1.md`, `source_gt_comparison`). The failures are not
disagreements with GT: they are base sentences that stand un-superseded in the same documents and
reach different figures, plus one figure in a closure proof that the world does not carry. None is
attributable to a solving agent, and no fix is proposed here.

---

## revision_2

Re-audit round 2, 2026-09-16 13:20 UTC. Revision 1 above is untouched.

### re_derivation_basis

Both shared inputs moved since round 1, so the charter-global section is **re-derived in full** rather
than carried forward by reference.

| artifact | round 1 | round 2 |
| --- | --- | --- |
| `bundle.extended.yaml` | `7f1999dda15428e9107f85fb6d8d2353bd139b83f228ba4be0a189b945f190c5` | `5b21112bdd877ec9a64d6f79703ab6c9cd5b3017b5bd3f93ea8b8dea8ff76fe7` |
| `task_tools.py` | `5444f81bdd2ed918268acfd56653f372d4e3faabed45b7fb2c5c65f4ab7e4994` | `51ab33b15ee65394b4de567dc16ca4d3c3f7df3260ae4941fa673f945bbddb4a` |

This round is **not blind and does not pretend to be**: round 1's GT is already in context. Its object
is narrower — whether each round-1 red light is genuinely closed rather than reworded, whether the
rework introduced anything new, and whether anything already sound regressed.

### what changed in the charter

- **`overwrite` blocks grew from 1 entry across the four policies to 13**: 2 / 4 / 4 / 3. All 13
  entries were checked mechanically: every `superseded_clause` is a **verbatim substring of the named
  base policy's `rule`**, and every `replaced_by` is a **verbatim substring of the declaring extended
  policy's own `rule`**. No entry names a clause that is not there, and none points at a replacement
  the rule does not carry.
- **Three new rule sentences** were added to carry the replacements:
  `bundle_ext_balance_settlement` — "The product's standard deposit for a deposit line is the
  product's flat deposit amount for one traveller, and a product that publishes both a flat amount per
  traveller and a share of the package price takes the flat amount.";
  `bundle_ext_party_amendment_charge` — "A change to the travelling party that the operations desk has
  approved is charged as an amendment under this rule whether a member is replaced or a place is
  simply given up, and the administration charge per traveller is the one this rule fixes and no
  other." and "Where places are given up under a change to the travelling party that the operations
  desk has approved, no cancellation ladder is read and no cancellation penalty or cancellation
  administration charge is withheld.";
  `bundle_ext_places_given_up` — "The occupancy adjustment is charged on the room or cabin left
  under-occupied, whatever discounts the travellers remaining in it carry."
- **`bundle_ext_places_given_up`'s occupancy ladder now states its basis**: "the rooms or cabins shown
  on the package record, **each counted as holding two travellers**".
- **`bundle_ext_places_given_up`'s prerequisite sentence was rewritten**: "…only after the ledger
  carries **an amendment charge posted since the operations desk approved the change to the travelling
  party**", and `condition` follows it.
- **Compute guards**: every club branch that read "whose tier carries a package discount" now also
  tests the percentage above nil (`club_tier_package_pct > 0`, `club_package_pct > 0`,
  `club_waivers_granted > 0`), and every `CFIELD` date read now falls back to a package-record date
  (`or F('quoted_date')`, `or F('departure_date')`) so the rule's own fall-through is reachable
  without raising.
- **`withheld_charge_carry` relabelled** `method` → `parameter`.
- **The customer's own tool was renamed** `confirm_places_given_up_54f63279` →
  `confirm_places_given_up_9aa48f75`; no reference to the old name survives anywhere under
  `env/online_travel_agency/`.

Re-checked and still holding after the rework: the base section of `bundle.extended.yaml` is
byte-equivalent to `blueprint/products/bundle.yaml` on all ten shared keys; the four
`(target_tool, computes)` claims are still one-to-one; the four tool bodies are still a single
`ctx.create` or `ctx.update` with no read, branch or rejection; the `prerequisite` graph is still two
disjoint `value_input` edges with `form: state`, no `fallback_reason`, `resolved_by` equal to the
depended-on `target_tool`, and `gate` naming a real binding of the blocked policy's compute; the four
task scopes are still pairwise disjoint and jointly complete.

### item_by_item_closure

`•` verified closed · `◦` not closed.

| id | round-1 substance | how it was addressed | verified |
| --- | --- | --- | --- |
| **0-1** | SOURCE-POLICY RED: base "equal instalments" vs extended remaining-instalment split, undeclared | `bundle_ext_balance_settlement.overwrite` now names the base sentence verbatim and points at the extended sentence replacing it | • closed. The whole base sentence is retired, its timing clause ("at equal intervals between the deposit and the final-payment date") included, so nothing of the 7 122.49 reading survives. Merged semantics unique |
| **0-2** | SOURCE-CHAIN RED: closure asserted an outstanding amount of 17 640.35 | figure corrected | • closed. Now reads **17 126.55**, which is what re-running `gross_outstanding` on the skipped world gives, and 17 126.55 ÷ 2 × 1.03 = 8 820.17 reproduces the closure's own final figure |
| **0-3** | observation: `amount_paid_usd` quoted as 8 895.00; deletion sensitivity quoted as 103.52 | both corrected | • closed. Now 6 031.00 (matches the seed row) and 52.53 (matches my replay: 9 918.98 → 9 866.45) |
| **0-4** | observation: a seeded instalment posted inside the price-guarantee term | world moved | • closed. The instalments now post 2026-09-03 and 2026-09-12, both after the term closes on 2026-09-02 |
| **0-5** | observation: charter-global findings not biting on task 0 | constituents addressed separately | • closed, see F-8 / F-9 / F-10 |
| **0-6** | observation: persona said "nothing there has changed since she booked" beside a seeded substitution notice | persona reworded | • closed. She now says "she has asked for nothing to be altered at her end" — a statement about her own conduct that cannot be read against an operator record |
| **1-1** | SOURCE-POLICY RED: club claw-back at re-pricing | two `overwrite` entries retiring both base sentences | • closed. Both "the club tier held on the deposit date decides…" and "…neither topped up nor clawed back" are named; the extended ladder stands alone |
| **1-2** | SOURCE-POLICY RED: single supplement on a discounted traveller | `overwrite` + a new rule sentence **and** a world change | • closed twice over. The base clause is retired and the rule states the replacement; independently, `2cbabc9f…` (`child_discount`) moved to `room_sequence: 1` while `eb3194f9…` (`third_adult_discount`) stays at `room_sequence: 2`, so the traveller left alone is now the undiscounted second adult and the two readings agree on the records alone |
| **1-3** | SOURCE-POLICY RED: name-change rate from the request's type, multiplied by the wrong travellers | two `overwrite` entries + a new rule sentence | • closed. `bundle_amendment`'s "per traveller replaced" sentence and `bundle_agg_party_pricing`'s "charged as an amendment" clause are both retired, and the replacement says the charge "is the one this rule fixes and no other" |
| **1-4** | SOURCE-POLICY RED: cancellation ladder on places given up neither applied nor superseded | two `overwrite` entries + a new rule sentence | • closed. Both `bundle_cancellation` clauses are named, and the replacement says outright that "no cancellation ladder is read and no cancellation penalty or cancellation administration charge is withheld". The `solvability_contract` precondition that previously paraphrased around the ladder now states the supersession explicitly |
| **1-5** | observation: "concerns a shore excursion" / "fifteen months back" | world and prose corrected | • closed. `0e812504…` now carries `charge_category: excursion_component`; every live claim reads "fourteen months". The old wordings survive only inside the REVISIONS paragraph describing the correction |
| **1-6** | observation: the prerequisite state distinguished from a standing line only by date work the rule never asked for | prerequisite sentence rewritten | • closed. The sentence now carries the date test itself — "posted since the operations desk approved the change to the travelling party" — and the approval date stands on `bundle_change_requests.decided_at` |
| **1-7** | observation: `withheld_charge_carry` labelled `method` | relabelled `parameter` | • closed. `bundle_ext_places_given_up` now holds 1 `method` and 4 `parameter`, inside every bound |
| **1-8** | observation: two-per-cabin basis lived only in `compute` | stated in the rule | • closed |
| **F-2** | agency service fee charged at deposit vs recovered in the balance | `overwrite` against `bundle_booking_terms` | • closed. Minor looseness noted below (N-5) |
| **F-3** | club claw-back at balance | `overwrite` against the "neither topped up nor clawed back" sentence only | • closed, and the narrowness is correct: the balance ladder still keys off the deposit date, so base's "the club tier held on the deposit date decides…" agrees with it and did not need retiring |
| **F-5** | cancellation ladder | see 1-4 | • closed |
| **F-8** | threshold cap vs the party's right to refuse | `overwrite` against `bundle_evt_supplier_notice` | • closed as a consistency matter. The declaration removes the party's cancel-free right and replaces it with a cap; that is a business-design choice the audit does not second-guess, and the merged semantics are unique |
| **F-9** | surcharge notified inside the price-guarantee term | world moved | • closed. The notice now posts 2026-09-04, after the term closes on 2026-09-02, so **both** readings of base's "a surcharge may be added … only after the product's price-guarantee term has run out" permit it. The notice still precedes the 2026-09-09 substitution notice, so the selection factor is untouched |
| **F-10** | "the two are never both taken" against variants publishing both | `overwrite` + a new rule sentence naming the flat amount | • closed decisively |
| **F-11** | occupancy basis unstated | see 1-8 | • closed |
| **F-12** | "whose tier carries a package discount" implemented as "a membership exists" | `> 0` guards added to all four club branches | • closed. A Wanderlane Blue member now falls into the rule's own fall-through in the compute too |
| **F-13** | no compute path for the rule's fall-through with no active membership | `or F('quoted_date')` / `or F('departure_date')` fallbacks | • closed. I re-ran all four computations with `club_memberships` and `club_points_entries` removed: each returns a definite number and none raises. See N-3 for the figures the dossier records |
| **F-14** | `withheld_charge_carry` label | see 1-7 | • closed |
| **F-15** | the closing sentence "…withheld against the payment line that settled the balance of the package, and against no other" as an implicit ordering | **the rule sentence is unchanged**; the tool docstring's "already standing" is unchanged | ◦ **not closed — and did not need to be.** Its *second* half is closed: the seeded earlier amendment line `6b595586…` now carries `source_entry_id: b1210238-…` (the balance payment line) instead of a deposit line, so the world no longer contradicts the sentence. The observation itself stands exactly as recorded in revision 1: the sentence names a record rather than another problem's result, the line it names is seeded in both tasks, and no consequence is demonstrable. Recorded here only because it was claimed closed while nothing about it moved |
| **F-16** | `5474525c` and `54f63279` sharing a two-character prefix | fourth tool renamed | • closed. `8a2d0e07`, `32304520`, `5474525c`, `9aa48f75` — distinct, no shared prefix, none sequential or tail-derived; the rename propagated to `charter_scope`, `required_documents`, `evaluation_criteria` and `prerequisite_closure.tools_do_not_block`, and no reference to the old name survives |

**25 of 26 claimed items verified closed. F-15 was never closed and was never consequential; the
claim is unsupported, the underlying observation is unchanged.**

### no_regression_scan

The rework moved seeded rows in both worlds as well as policy text, so every derivation was re-run
from scratch on the reworked charter and the reworked worlds.

| quantity | round 1 | round 2 | moved? |
| --- | --- | --- | --- |
| task 0 `surcharge_amount_usd` | 2 133.61 | 2 133.61 | no |
| task 0 `balance_due_usd` | 9 918.98 | 9 918.98 | no |
| task 0 skip-prerequisite balance | 8 820.17 | 8 820.17 | no |
| task 0 whole-baselines | 0.00 / 19 014.61 | 0.00 / 19 014.61 | no |
| task 0 nine per-factor baselines | — | identical to round 1, cent for cent | no |
| task 1 `amendment_charge_usd` | 296.80 | 296.80 | no |
| task 1 `revised_package_price_usd` | 28 844.51 | 28 844.51 | no |
| task 1 skip-prerequisite revised price | 28 547.71 | 28 547.71 | no |
| task 1 whole-baselines | 260.00 / 23 610.00 | 260.00 / 23 610.00 | no |
| task 1 nine per-factor baselines | — | identical to round 1, cent for cent | no |

The reworker's claim that every scored value is unchanged is **verified**, independently and binding
by binding, not accepted on assertion.

Structural checks re-run on the reworked form and still green: factor counts 4 / 5 / 4 / 5, each with
≥2 `parameter` and ≥1 `method`; eighteen ladders of three pairwise-disjoint tiers, every tier a
sentence of its own rule and a branch of its `decides` binding; six cross-difficulty factors, all
reading `club`, two in each task's computations; every tier taken unchanged; every near-miss record
still present and still excluded (or included) by the rule alone. Both prerequisite sentences still
pass the four-point test, and each is still brought about by exactly one write of this difficulty.

One point deserves recording rather than a red light: the rewritten prerequisite sentence for
`bundle_ext_places_given_up` names a performer inside its anchor clause — "since **the operations
desk** approved the change to the travelling party". The state it waits on is still the ledger line,
and the anchor is a record (`bundle_change_requests.request_status` / `.decided_at`) that base
`bundle_amendment`'s own gate describes in the identical words ("the operations desk has already
recorded an approved change request against this package"), so the wording is charter-standard and
the state form holds.

### new_findings (revision 2)

None is a red light: each is a false or stale assertion in proof prose whose conclusion still holds,
and none moves a scored value, an eligibility or a tier. They are recorded because they were
introduced by this rework.

- **N-1 — `tasks/0.json → prerequisite_closure.no_user_hint` quotes a persona sentence that no longer
  exists.** It still says her statements about the booking include "that nothing about the resort or
  the rooms has changed since she booked", which is precisely the wording finding 0-6 caused to be
  replaced by "she has asked for nothing to be altered at her end". The conclusion the field supports
  — that the persona hints at no prerequisite — holds *a fortiori* under the new wording, so the
  defect is confined to the quotation. Bears on task 0.
- **N-2 — `tasks/0.json → design_rationale`, BASE-INVARIANT CARD, contradicts the same file's
  OVERWRITE paragraph.** It still reads: "bundle_payment_schedule's instalment and currency-markup
  sentences, **which the extended balance policy refines rather than replaces**." The OVERWRITE
  paragraph two paragraphs later, and `bundle_ext_balance_settlement.overwrite` itself, now retire the
  instalment sentence outright. This is the exact sentence-shape whose earlier form ("contradicts no
  sentence of it") was the aggravating evidence for finding 0-1; the charter is now unambiguous, but
  the dossier still carries the withdrawn claim in a second place. Bears on task 0.
- **N-3 — `tasks/0.json → design_rationale`, REVISIONS note (7), records no-club figures taken on the
  opening world rather than at handling time.** It states that all four computations, re-evaluated
  with the club rows removed, "return a definite number (2291.20, 9262.67, 436.80, 28978.48)". I
  reproduce 2 291.20 and 436.80 exactly; the other two are the values those computations take **before
  their prerequisite write**. Evaluated at their own handling moments on the same club-less
  counterfactual, the balance is **10 442.63** and the revised price **29 415.28**. The claim's
  substance — that the fall-through is reachable and yields a definite number rather than an error —
  is true, and I verified it independently, which is why this is an observation. Bears on task 0.
- **N-4 — `tasks/1.json → prerequisite_closure.order_uniqueness` paraphrases the superseded
  prerequisite wording.** It says the rule "states that the price for the party actually travelling is
  fixed only after the ledger carries **the amendment charge owed for the change**"; the rule now
  reads "an amendment charge **posted since the operations desk approved the change to the travelling
  party**". It is a paraphrase rather than a quotation and the substance is preserved, so this is the
  mildest of the four. Bears on task 1.
- **N-5 — `replaced_by` sometimes quotes one tier of the ladder that replaces a base sentence.** In
  `bundle_ext_balance_settlement`'s agency-service-fee and club-discount entries, and in
  `bundle_ext_operator_surcharge_pricing`'s threshold entry, the `superseded_clause` is named in whole
  but `replaced_by` points at only one tier of the multi-tier ladder that takes its place. The merged
  semantics are still unique, because the base sentence is retired in whole and the extended rule
  carries the full ladder; but a reader reconstructing the merge from the `overwrite` entry alone does
  not see the other branch. Charter-global; bears on both tasks only as a legibility matter.

### revision_2 verdicts

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** | **PASS** |

All six round-1 red lights are closed at their root — five by declaring the override that was missing,
one by correcting a figure — and none by rewording a defect into a new name. No scored value moved.
Five new observations are on record, all in proof prose and none consequential.

### closing_checklist (revision 2)

The difficulty **closes** at revision 2. Re-checking revision 1's list against the reworked form:

- per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside; revision 1 is
  preserved intact in all three files and revision 2 is appended below it;
- all four extended policies covered; the two task scopes pairwise disjoint and each spanning one
  whole tree;
- task tools and GT closed; four uuid8s, now with no shared prefix, independently generated and frozen
  (`8a2d0e07`, `32304520`, `5474525c`, `9aa48f75`);
- each tree: n = 1 prerequisite problem, one `value_input` edge (floor max(n−1,1) = 1), root resolved
  by an `owner=user` tool, no cycle; the difficulty's two edges remain a DAG;
- every computation declares a self-sufficient baseline and 4–6 factors (≥2 `parameter`, ≥1 `method`;
  per task ≥1 multi-source and ≥1 cross-difficulty); every ladder of three tiers stated in full in its
  rule; every factor re-proved to bear weight on the reworked world, with whole-baseline fall-backs
  0.00 / 19 014.61 / 260.00 / 23 610.00, each definite and each different from gold;
- instantiation-stage gates re-run once on the reworked final form, 2026-09-16 13:24 UTC: EXTENDED OK;
  TASK TOOL CONTRACT OK (4 tools); REPLAY OK (10 / 12 acts, det True, nonvac True, 0 errs, closure
  18/18 both, match True); SOLVABILITY OK; COMPUTE OK (branches 29 / 24, steps 10 / 12, suite means
  26.50 and 11.00, history_rows_max 13); GROUNDING OK; SCOPE OK — identical to the coordinator's
  snapshot, and no artifact was touched by this audit.
