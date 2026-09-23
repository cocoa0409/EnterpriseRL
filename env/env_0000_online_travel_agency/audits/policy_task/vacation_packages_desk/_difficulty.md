# Policy-task audit — vacation_packages_desk / charter-global

## charter_global_frozen

- `env/env_0000_online_travel_agency/tasks/vacation_packages_desk/bundle.extended.yaml` — sha256 `11e17ac21b84ebac89aa78a828887c4be343dd3d9c41391fbe73fc82e2655369` (sha256/16 `11e17ac21b84ebac`), 164062 bytes
- `env/env_0000_online_travel_agency/tasks/vacation_packages_desk/task_tools.py` — sha256 `944e8ae99f8c1e2e8f105a853d88006bda48353d6f73bf28a7126804c1707f08` (sha256/16 `944e8ae99f8c1e2e`), 11248 bytes
- Freeze time: 2026-09-17 (session clock), written before any task's `evaluation_criteria` / `computations` were read.
- Auditor: independent source-layer auditor (erl-task-policy-audit), not the agent that wrote these artifacts.
- Fields permitted here: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/bundle.yaml` and `blueprint/products/club.yaml` (for `CPARAM` tier values only), the whole of `bundle.extended.yaml`, the whole of `task_tools.py`.
- Fields explicitly masked and not read while this section was written: for both tasks, `charter_scope`, `computations`, `db_closure`, `db_closure_matches_initial_state`, `design_rationale`, `evaluation_criteria`, `prerequisite_closure`, `required_documents`, `solvability_contract`. Nothing in this section is derived from a revealed GT.
- Entry conditions (Step 0): the coordinator supplied the instantiation-stage gate snapshot with the actual output lines — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK — and the two masked task views with their hashes (`62c9fba10bcdc112`, `77eb93fdfaf748bc`) constructed by whitelist (`frozen_time`, `user_scenario`, `initial_state` only). Entry conditions are complete. `check_traceability.py` is correctly absent at this stage. The gates are the qualification to audit, not a proof of correctness.

### policy_conflict_scan

The charter carries 11 base policies and 4 extended policies. Overlapping-subject scan:

| Extended policy | trigger | subject | computes | target_tool |
| --- | --- | --- | --- | --- |
| `bundle_ext_package_amendment_charge` | state_due | bundle_penalty_charge | amendment_charge_usd | charge_package_amendment_6b64f72d |
| `bundle_ext_balance_instalment_call` | on_request | bundle_final_payment_charge | instalment_amount_usd | settle_package_instalment_b6602c09 |
| `bundle_ext_cancellation_penalty_withholding` | state_due | bundle_penalty_charge | cancellation_penalty_usd | withhold_cancellation_penalty_6c06e997 |
| `bundle_ext_cancellation_refund_payout` | on_request | bundle_refund_payout | refund_amount_usd | release_package_refund_313c063d |

Two policies share the subject `bundle_penalty_charge` (`..._package_amendment_charge` and `..._cancellation_penalty_withholding`). They do **not** conflict: they compute different quantities (`amendment_charge_usd` / `cancellation_penalty_usd`), bind different tools, and their triggering situations are disjoint on the record — the amendment charge "answers a change the operations desk has already approved against that package" (`bundle_change_requests.request_status = approved`), the cancellation penalty is "worked out on a cancelled vacation package" and reads `F('cancelled_at')`, which is empty on a live package. The ledger rows they write are distinguished by `charge_category` (`amendment_fee` vs `cancellation_penalty`), and every downstream aggregate that must tell them apart filters on `charge_category` (`amendments_charged`, `amendment_lines`). No two policies reach different conclusions on one quantity.

Time anchors are consistent and non-overlapping: `DAYS(NOW, final_payment_due_date)` (amendment staging), `DAYS(cancelled_at, departure_date)` (cancellation share), `DAYS(final_payment_due_date, cancelled_at)` (administration charge), `DAYS(latest notice posted_date, cancelled_at)` (advice window). Every use is `DAYS(a, b) = b − a` in calendar days, and each policy's `compute_basis` quotes a rule sentence whose sign matches the branch taken.

Cross-category read boundaries: `club` is read by all four (`CPARAM` for `package_discount_pct` / `waived_change_fees_per_year`, `XCOUNT` over `club_points_entries`); `care` is read by `..._balance_instalment_call` alone, as an `EXISTS` on `linked_bundle_package_id`. No policy writes to another category. Declared `cross_category` blocks match the `compute` bindings in every case.

Terminal states: each tool appends exactly one ledger row and changes no package status; no two policies claim the same terminal field.

**Task scopes** (derived from the charter and the two masked worlds, not from `charter_scope`):

- task 0 tree = { `bundle_ext_balance_instalment_call` (root), `bundle_ext_package_amendment_charge` (prerequisite) }
- task 1 tree = { `bundle_ext_cancellation_refund_payout` (root), `bundle_ext_cancellation_penalty_withholding` (prerequisite) }

Pairwise disjoint, and jointly they cover all four extended policies. No policy is claimed twice; none is uncovered.

### rule_compute_equivalence

Check 2 was run sentence by sentence over all four extended policies, in both directions.

**Forward (every quantity has a verbatim `compute_basis` quotation and a restricted implementation).** Every binding in each of the four `compute` blocks carries a `compute_basis` entry, and every such entry is a verbatim substring of that policy's own `rule`. Windows (`within_months=12`, `within_months=36`), filters (`event_type`, `charge_category`, `reason_code`, `accrual_source`, `points_kind`, `currency_charged`, `request_status`, `request_type`), acting bases (package price / money paid in / reduced withholding), grouping (per traveller vs once for the package), the order of operations (`charge_before_softening`, `price_after_concessions`, `outstanding_amount`, `settlement_before_markup`) and the rounding convention (`RND(..., 2)` once, at the end) each have a quoted sentence. Each policy carries an explicit ordering sentence — e.g. `bundle_ext_cancellation_penalty_withholding`: "The cancellation share acts on the penalised value alone, the deposit is ring-fenced out of the figure that share gives before anything is added, the administration charge is added to what is left of it, and the loyalty relief acts last on that sum." — and the `compute` chain implements exactly that order.

**Backward (compute invents no basis; the rule makes no empty promise).** Two residues, neither of them a red light:

1. `bundle_ext_cancellation_penalty_withholding.rule` calls the four ladder shares **the product's** — "the product's standing cancellation share", "the product's near-departure share", "the product's inside-six-weeks share", "the product's inside-three-months share" — but `compute` binds them to charter-level policy constants `K('standing_cancellation_share_pct')=10`, `K('near_departure_share_pct')=90`, `K('inside_six_weeks_share_pct')=55`, `K('inside_three_months_share_pct')=30`, which are the same for all six variants. The charter does carry a genuine per-product ladder of exactly these four bands — `parameter_schema.cancellation_ladder_pct` ("Cancellation penalty as a share of the package price by how far ahead of departure…"), instantiated per variant with keys `90_or_more_days`, `89_to_43_days`, `42_to_15_days`, `14_or_fewer_days` — and the base policy `bundle_cancellation` binds it (`params.per_tier.<variant>.cancellation_ladder_pct: =cancellation_ladder_pct`). See `findings` F-1.
2. `bundle_ext_balance_instalment_call.rule` says "The priced package value the call is worked out on is the package price recorded on the package **for the party travelling**." The trailing phrase maps to no operation in `compute` (`priced_package_value` starts from `F('package_price_usd')` unmodified); the party-travelling divisor appears only in `per_person_price`. Wording residue with no consequence on either world — recorded as observation F-4.

**Factor ladders inside the equivalence.** For every one of the 18 declared factors, each tier named in `factors[].ladder` is a sentence of the `rule` and a branch of the `decides` binding, and each branch of that binding is a tier the rule states. No tier lives only in `compute`, and no rule sentence describes a tier the binding does not produce. Fall-through tiers are carried by the policy's baseline sentence ("The amendment charge payable is that starting amount taken once and in full…", "The figure the ladder gives stands as it is.", "Nothing is withheld as an administration charge.", "Nothing is added back to what is returned as a goodwill gesture.", "Nothing is retained for the currency the party elected to be charged in.", "The instalment called is the whole of what the package still owes…").

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy (table above); no tool is bound twice and no `computes` name is reused. Each policy's subject, `base_policy_refs`, target tool, docstring and terminal state admit one business reading; no policy adds a confirmation, review, wait or procedure outside itself.

`task_tools.py` holds exactly four tools:

| tool | uuid8 | owner |
| --- | --- | --- |
| `charge_package_amendment_6b64f72d` | 6b64f72d | agent |
| `settle_package_instalment_b6602c09` | b6602c09 | user |
| `withhold_cancellation_penalty_6c06e997` | 6c06e997 | agent |
| `release_package_refund_313c063d` | 313c063d | user |

The four uuid8s are pairwise distinct, share no prefix, show no sequence and are not derivable from one another or from a common stem; each is frozen into its function name, into the `prerequisite[].resolved_by` that names it and into the policy `target_tool`. PASS.

Docstring sequence check: no docstring names another tool, states a position in a sequence, or carries `before`, `after`, `first` or `prior to`. `withhold_cancellation_penalty_6c06e997` says "on a cancelled vacation package" (a record state, part of its own scope, not an ordering) and "so that it is no longer money the party can have back" (a statement of this write's own ledger effect). `settle_package_instalment_b6602c09` says "the money now called" — "now" is not relative to another tool. PASS.

Tool bodies were read in full: each performs one `ctx.find` for the owning `customer_id` and one `ctx.create` of a ledger row. None inspects a prerequisite, refuses a call, errors on state, or returns a hint. PASS.

### prerequisite_graph

Check 7 over the whole graph. Every one of the four extended policies fills in `prerequisite` (`[]` on `..._package_amendment_charge` and `..._cancellation_penalty_withholding`, one edge each on the other two).

| blocked policy | problem | kind | gate | form | resolved_by | acyclic |
| --- | --- | --- | --- | --- | --- | --- |
| `bundle_ext_balance_instalment_call` | `bundle_ext_package_amendment_charge` | value_input | `charges_standing` | state | `charge_package_amendment_6b64f72d` | yes |
| `bundle_ext_cancellation_refund_payout` | `bundle_ext_cancellation_penalty_withholding` | value_input | `withheld_standing` | state | `withhold_cancellation_penalty_6c06e997` | yes |

- Every `problem` points at another extended policy id present in this file; neither points at a base policy or at itself. The graph is two disjoint single edges — acyclic, and no cross-task reference creates a cycle.
- Each `policy_source` is verbatim locatable in the **blocked** policy's own `rule` (quoted in `prerequisite_sentences` below).
- `form: state` on both; `fallback_reason` is absent on both, which is exactly right — it is required only on action-form edges, and neither edge is action form.
- `condition` is neither strengthened nor weakened relative to the sentence: "the package ledger carries an amendment charge for every change the operations desk has approved against the package" against "…only after the package ledger carries the amendment charge owed for every change the operations desk has approved against the package"; "the package ledger carries the cancellation penalty withheld for the places the party gave up" against "…settled only after its ledger carries the cancellation penalty withheld for the places the party gave up".
- `resolved_by` is in each case the depended-on policy's own `target_tool`, and the tool genuinely makes the gate hold: `charge_package_amendment_6b64f72d` writes `event_type='bundle_penalty_charge', charge_category='amendment_fee'`, which is inside `charges_standing`'s `SUM(... event_type='bundle_penalty_charge')`; `withhold_cancellation_penalty_6c06e997` writes `event_type='bundle_penalty_charge', charge_category='cancellation_penalty'`, which is inside `withheld_standing`'s `SUM(... event_type='bundle_penalty_charge')`. Both `effect` statements are accurate.
- `kind: value_input` matches `gate` in both cases: `charges_standing` and `withheld_standing` are real binding names in the blocked policy's `compute`, each feeding the scored result.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears anywhere in either `prerequisite` block.

PASS.

### prerequisite_sentences

Check 6, edge by edge.

**Edge 1 — `bundle_ext_balance_instalment_call` waits on `bundle_ext_package_amendment_charge`.**
Sentence, verbatim from `bundle_ext_balance_instalment_call.rule` (second sentence): *"The instalment called on a package is fixed only after the package ledger carries the amendment charge owed for every change the operations desk has approved against the package."*
Four-point test: (a) it joins **this** policy's own result ("the instalment called on a package is fixed") to what it waits on with the explicit ordering connective **only after**; (b) what it waits on is a record-visible state — "the package ledger carries the amendment charge owed…" — named in the words the tables and finders use (`bundle_ledger_entries`, `bundle_change_requests`, `request_status: approved`), with no action, performer or tool; (c) it names no tool, no policy id, no snake_case token and no row id; (d) it is exactly as strong and as wide as the edge's `condition`, which restates it with no closure added.
The one write of this difficulty that brings that state about: `charge_package_amendment_6b64f72d`, the `target_tool` of `bundle_ext_package_amendment_charge`, whose own rule is the only rule in the charter describing an amendment charge entered against a package. The other agent write, `withhold_cancellation_penalty_6c06e997`, lands a *cancellation penalty* (`charge_category='cancellation_penalty'`), which its policy's rule describes as the money a party forfeits for giving up their places — not an amendment charge, and available only "on a cancelled vacation package". No second candidate; the hop resolves in one reading.
Derivation a reader performs: sentence → "the ledger must carry the amendment charge owed for every approved change" → read `bundle_change_requests` for this package and `bundle_ledger_entries` for lines charged as an amendment, a name change or a date change → find an approved change with no matching charge → find the policy whose rule prices "the amendment charge owed on a vacation package [that] answers a change the operations desk has already approved against that package" → its `target_tool`. One reading.

**Edge 2 — `bundle_ext_cancellation_refund_payout` waits on `bundle_ext_cancellation_penalty_withholding`.**
Sentence, verbatim from `bundle_ext_cancellation_refund_payout.rule` (second sentence): *"The money returned on a cancelled package is settled only after its ledger carries the cancellation penalty withheld for the places the party gave up."*
Four-point test: (a) this policy's own result ("the money returned on a cancelled package is settled") joined by **only after**; (b) record-visible state, "its ledger carries the cancellation penalty withheld for the places the party gave up", in table words, no performer; (c) no tool, policy id, snake_case token or row id; (d) same strength and scope as `condition`.
The one write bringing it about: `withhold_cancellation_penalty_6c06e997`. `charge_package_amendment_6b64f72d` writes `charge_category='amendment_fee'` under the reason `party_amendment`, which no rule in the charter describes as a cancellation penalty. One reading.

**No second wording, no tool name, no other problem's id in either rule.** Neither `rule` contains a snake_case token, a tool name or a second sentence about the same dependency.
**The depended-on rules do not restate the sentence:** `bundle_ext_package_amendment_charge.rule` says nothing about instalments or the balance call; `bundle_ext_cancellation_penalty_withholding.rule` says nothing about a refund or a payout. Verified by reading both rules in full.
**State-form priority:** both edges are state form, so no `fallback_reason` is owed and none is present. Nothing to test.
**Cross-problem order grounding no edge:** the only other ordering-flavoured sentence in an extended rule is `bundle_ext_package_amendment_charge`'s "…answers a change the operations desk has **already approved** against that package". That waits on `bundle_change_requests.request_status = approved`, which is the *base* eligibility gate `bundle_amendment.change_request_approved` (kind: authorization) and not another extended problem — no extended policy in this charter writes a change request, and no task tree rests on it as an edge. It is a seeded eligibility, correctly not declared as a prerequisite edge.

PASS.

### override_declarations

Check 1's finding half, run sentence by sentence over every entry in every extended policy's `base_policy_refs`. Where a task's own world is needed to show what a residue costs, the demonstration is in that task's file; here only the findings.

**`bundle_ext_package_amendment_charge`** — refs `bundle_cancellation`, `bundle_amendment`, `bundle_agg_party_pricing`; two `overwrite` entries, both against `bundle_amendment`.

- base `bundle_amendment`: "A member of the party may be replaced only up to the product's name-change deadline before departure, against the product's name-change charge per traveller replaced." — **declared superseded** (verbatim match), replaced by the name-change starting amount read "against every traveller the approved replacement requests standing on the package concern". Merged semantics unique.
- base: "Any other amendment carries the product's administration charge per traveller, and correcting the contact address or contact number is free and carries none." — **declared superseded** (verbatim match). The `replaced_by` keeps the per-traveller administration charge as the fall-through starting amount but drops the contact-correction carve-out. The carve-out is not reinstated anywhere. See observation F-3.
- base: "A change to the travelling party or the departure date is made only when the operations desk has already recorded an approved change request against this package." — followed, not overridden (the extended rule's first sentence and the `latest_approved_change` binding both require `request_status='approved'`).
- base: "The departure date may be moved only on a product that allows it, within its ceiling on the number of moves, against its date-change charge per traveller…" — followed for the quantity that is scored (the date-change tier uses `P('date_change_fee_per_person_usd') * party_travelling`). The "re-priced at the product's price for the new dates" half governs the package price, which this policy does not compute.
- base: "An amendment requested after the balance has fallen due is priced as a cancellation and a rebooking, because the suppliers have already been paid." — the extended rule gives this an operative meaning (`amendment_stage_addition` tier 1: the cancellation administration charge per traveller) using the same reason wording. Base states no number, so there is no quantity to conflict on; not an override. Not taken on either world.
- base: "Substituting one component of the itinerary for another carries the product's component change charge…" — followed (`P('component_change_fee_usd')`, read once for the package).
- base: "A product that allows no date change refuses the move outright rather than charging for it…" — inherited untouched; does not bear on either world (Flex has `date_change_allowed: true`).
- base `bundle_cancellation`: no sentence governs an amendment charge; the extended policy borrows only `cancellation_admin_fee_per_person_usd` as a staging addition, which base nowhere forbids.
- base `bundle_agg_party_pricing`: "every per-person amount is read against the party actually travelling and never against the party first quoted" — followed (`party_travelling = F('party_adults') + F('party_children')`).

**`bundle_ext_balance_instalment_call`** — refs `bundle_payment_schedule`, `bundle_club_and_corporate_interaction`, `bundle_agg_party_pricing`, `bundle_components`; two `overwrite` entries.

- base `bundle_payment_schedule`: "A product that allows instalments splits the balance into its own number of equal instalments falling due at equal intervals between the deposit and the final-payment date, and the last instalment is adjusted for rounding." — **declared superseded** (verbatim match), replaced by "what the package still owes divided by the number of instalments the product allows less those already taken". The declaration covers the whole sentence, so the "equal intervals" timing falls with it; the extended policy's `on_request` trigger is therefore not in conflict. Merged semantics unique.
- base `bundle_club_and_corporate_interaction`: "the club tier held on the deposit date decides the package discount applied to the price" — **declared superseded** (verbatim match), replaced by the two-tier club concession rate reading the active card. But the same policy's companion sentence — "Where the member's tier changes between deposit and departure, the discount applied at deposit stands and is neither topped up nor clawed back." — is **not named in any `overwrite`**, and it states the same deposit-date rule in other words, while `compute` reads `CPARAM('club', 'package_discount_pct', status='active')`, i.e. the tier standing now. See finding F-2.
- base `bundle_payment_schedule`: "The balance falls due the product's final-payment distance before departure…" — followed; consistent with the seeded `final_payment_due_date` on both packages.
- base: "The balance is taken only when frozen time is not before the moment the operator took the party's deposit… plus the price-guarantee term" (eligibility `price_guarantee_elapsed`) — inherited in full and not weakened.
- base: "Where the party elects to be charged in a currency other than the operator's own, the product's conversion markup is added to each payment as it is taken." — inherited in full; the extended policy adds no markup, which is correct only where the payment is in the operator's own currency. Not weakened; bears on task 0 only, demonstrated there.
- base: "A package booked closer to departure than the final-payment distance is paid in full at booking, and no deposit is taken separately." / "A missed instalment is pursued once before the package is cancelled…" — inherited; neither governs a scored quantity here.
- base `bundle_booking_terms` (reached through `bundle_payment_schedule`'s subject, and directly relevant to the deposit-difference tier): "A reduced promotional deposit may be taken only on a product that allows it, and the difference to the standard deposit falls due with the balance rather than being written off." — followed; `instalment_deposit_difference` collects that difference with the call. The extended tier 2 splits the difference across two calls, which base neither requires nor forbids (the instalments *are* the balance). No conflict on the scored quantity.
- base `bundle_agg_party_pricing`: "a third adult sharing takes its third-adult discount, and a child within the product's child age takes its child discount; the supplement and the discounts never apply to the same traveller at once" — followed (`sharing_third_adults = MX(0, adults − 2 × rooms)`, children counted separately, no single supplement applied). "A traveller who has booked more than the frequent-traveller threshold of packages in the last thirty-six months is offered the loyalty concession within the desk's authority and no other", with `params.frequent_traveller_threshold_36m: 3` — followed exactly: `K('frequent_package_threshold_36m') = 3`.
- base `bundle_components`: governs what a component charge covers; the extended policy only sums existing component lines. No conflict.

**`bundle_ext_cancellation_penalty_withholding`** — refs `bundle_cancellation`, `bundle_payment_schedule`, `bundle_agg_party_pricing`; three `overwrite` entries, all against `bundle_cancellation`.

- base: "The penalty is read off the product's cancellation ladder by how many whole days lie between the cancellation and the departure date, applied to the package price of the places being given up." — **declared superseded** (verbatim match). The `replaced_by` addresses only the penalised value, and the extended rule then re-states the day bands itself while attributing the four shares to "the product". See finding F-1.
- base: "The deposit is returned only on a product whose deposit is refundable, and on every other product it is forfeited in full even where the ladder would otherwise return more." — **declared superseded** (verbatim match), replaced by the ring-fence. Merged semantics unique: `P('deposit_refundable')` still gates the ring-fence, so the non-refundable case still forfeits.
- base: "The product's administration charge is withheld per traveller on every cancellation whatever the ladder says, and the agency service fee is never returned." — **declared superseded** (verbatim match), replaced by the three-tier administration charge whose fall-through is "Nothing is withheld as an administration charge." The declaration takes the whole sentence, and with it the clause "the agency service fee is never returned", which no extended policy reinstates. See observation F-5.
- base: "Only the party may cancel their own package, and the cancellation is confirmed by the lead traveller rather than performed on their behalf." / eligibility `places_given_up_stated` (applies_to `bundle_cancel`, `bundle_predeposit_cancel`) — inherited in full; neither applies to `bundle_penalty_charge`, so the penalty write carries no caller-fact gate.
- base: "A cancellation made because a surcharge exceeded the product's threshold is free of penalty, and so is a cancellation made because the operator itself changed the itinerary significantly." — inherited in full and **not** weakened by this policy. It bears on task 1's world; demonstrated there.
- base: "Where some but not all of the party give up their places, the ladder is applied to those places alone…" — inherited; bears only on a partial cancellation.
- base `bundle_payment_schedule` / `bundle_agg_party_pricing`: only the final-payment-date anchor and the party-travelling count are borrowed; both are followed.

**`bundle_ext_cancellation_refund_payout`** — refs `bundle_refund_settlement`, `bundle_cancellation`, `bundle_credit`, `bundle_club_and_corporate_interaction`; one `overwrite` entry.

- base `bundle_refund_settlement`: "Each payout is raised against the original ledger line it reverses, so a package with a deposit and several instalments settles as several payouts." — **declared superseded** (verbatim match), replaced by one payout against the package as a whole. Merged semantics unique.
- base: "A payout line is raised only while the package record stands at cancelled or completed." (eligibility `package_settled`) — inherited in full.
- base: "An approved refund settles in the form the product prescribes: money to the card, or a future travel credit voucher, never both and never a mixture." — inherited; the tool raises a `bundle_refund_payout`, correct only where the product's `refund_form` is `original_payment`. Bears on task 1's world; demonstrated there.
- base: "A payout may never exceed the amount that original line actually collected, and the sum of a package's payouts may never exceed the amount paid on it." — the first half is tied to the superseded per-line settlement and is moot once one payout is raised for the package; the aggregate cap is inherited and not weakened. Bears on task 1's world; demonstrated there.
- base: "The settlement takes the product's processing time, counted in business days from the day the refund was approved…" — inherited. It governs when the money reaches the card, not when the payout line is raised; the tool's own effect is the raising of the line. No real-world wait is created. Checked against `bundle_ext_cancellation_refund_payout`'s rule, which speaks only of the money being "settled as one payout against the package as a whole".
- base `bundle_credit`: "A future travel credit is issued for the value the cancelled package still carried…" and "A product whose credit validity term is zero issues no voucher at all" — inherited; this policy issues no voucher, which is consistent wherever `refund_form` is `original_payment`.
- base `bundle_cancellation`: its penalty sentences are governed by the sibling extended policy; this one only sums the resulting ledger lines.
- base `bundle_club_and_corporate_interaction`: "the club tier held on the deposit date decides the package discount applied to the price" — this policy declares **no** override against it and uses `CPARAM('club', 'package_discount_pct', status='active')`. The base sentence governs "the package discount applied to the price"; the goodwill gesture is a share of the reduced withholding added back to a refund, not a discount applied to a price, so the base sentence does not govern this quantity. Not an override. Recorded for completeness in F-2.

No **anonymous intermediate factor**, **0/1 multiplier** or **dropped branch** was found: every intermediate in all four chains carries a quoted rule sentence; the only share-style multipliers (`payable_share`, `withheld_share`, `markup_share`, `goodwill_rate`, `loyalty_relief_applied_pct`) are each declared as a factor with a stated ladder and a fall-through that matches the policy's baseline; and every branch each base policy declares is either produced by the extended selector or explicitly superseded. No author note calls a base output a "wrong value" or "the algorithm to avoid".

### factor_ladders

Structure only. 18 factors over 4 policies.

| policy | factor | effect | decides | tiers | multi-source tiers (non-fall-through) | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| amendment | `amendment_starting_amount_basis` | method | starting_amount | 4 | no | — |
| amendment | `amendment_stage_addition` | parameter | stage_addition | 3 | tier 2 (due date **and** ledger instalment) | — |
| amendment | `amendment_repeat_multiple` | parameter | repeat_multiple | 3 | no | — |
| amendment | `amendment_club_waiver_share` | parameter | payable_share | 3 | tiers 1, 2 (club card tier **and** club ledger waivers) | club |
| instalment | `instalment_priced_package_value` | method | priced_package_value | 3 | tiers 1, 2 (party **and** rooms **and** ledger discount lines) | — |
| instalment | `instalment_club_concession_rate` | parameter | club_concession_pct | 3 | tiers 1, 2 (club card **and** care policy) | club |
| instalment | `instalment_loyalty_concession_rate` | parameter | loyalty_concession_rate | 3 | no | club |
| instalment | `instalment_deposit_difference` | parameter | deposit_difference_called | 3 | tiers 1, 2 (product promo flag **and** ledger deposit lines) | — |
| instalment | `instalment_split_basis` | method | instalment_called | 3 | tiers 1, 2 (product plan flag **and** ledger instalment count) | — |
| penalty | `cancellation_share_ladder` | parameter | cancellation_share_pct | 4 | no | — |
| penalty | `penalised_value_basis` | method | penalised_value | 3 | tiers 1, 2 (ledger intake **and** package price **and** component lines) | — |
| penalty | `deposit_ring_fence` | method | ladder_after_deposit | 3 | tiers 1, 2 (product refundable flag **and** deposit vs ladder) | — |
| penalty | `cancellation_administration_charge` | parameter | administration_withheld | 3 | tier 2 (cancellation date **and** ledger instalment) | — |
| penalty | `frequent_traveller_penalty_relief` | parameter | loyalty_relief_applied_pct | 3 | no | club |
| refund | `returnable_intake_basis` | method | returnable_intake | 3 | tier 1 (product refundable flag **and** component lines) | — |
| refund | `operator_advice_withholding_share` | parameter | withheld_share | 3 | tier 2 (no significant notice **and** an ordinary notice **and** its date vs cancelled_at) | — |
| refund | `club_goodwill_gesture` | parameter | goodwill_rate | 3 | tiers 1, 2 (club card tier **and** package ledger amendment lines) | club |
| refund | `currency_markup_retention` | parameter | markup_share | 3 | no | — |

Counts per policy: amendment 4 (1 method, 3 parameter); instalment 5 (2 method, 3 parameter); penalty 5 (2 method, 3 parameter); refund 4 (1 method, 3 parameter). Every policy is inside 4–6 with at least 2 `parameter` and at least 1 `method`. Per task (trees above): task 0 has two multi-source factors and two `cross_difficulty: club` factors; task 1 has three multi-source factors and two `cross_difficulty: club` factors. Both floors met.

**Bindings disjoint.** Within each policy the four or five `bindings` sets are pairwise disjoint; verified name by name (e.g. `instalments_taken` appears in `instalment_split_basis` only, and `deposit_collected` in `instalment_deposit_difference` only). No factor's `decides` is `result`; each is an intermediate feeding `result`.

**At least three tiers, pairwise disjoint as stated.** Every ladder has 3 tiers (4 for `amendment_starting_amount_basis` and `cancellation_share_ladder`), fall-through counted. Disjointness holds as written: the day bands ≤14 / 15–42 / 43–89 / otherwise partition the line; `deposit_refundable` true/false separates `returnable_intake_basis` tiers 1 and 2 and `deposit_ring_fence` tiers 1 and 2; "reaches the package price" / "falls short of the package price" separates `penalised_value_basis`; "fewer rooms or cabins than adults" / "at least as many" separates `instalment_priced_package_value`; "already carries at least one instalment" / "carries no instalment" separates `instalment_split_basis`; "every … in a currency other than the operator's own" / "some but not all" separates `currency_markup_retention`; "no waived change fee used" / "at least one … but fewer than the tier grants" separates `amendment_club_waiver_share`; "more than twice the threshold" / "more than the threshold but no more than twice" separates both loyalty ladders.

**No two tiers of one ladder select the same value or method.** Checked for all 18: the four starting-amount methods differ in both the product charge and the count basis (per approved replacement / per traveller / once for the package); 2 ≠ 1.5 ≠ 1; 0 ≠ 0.5 ≠ 1; 90 ≠ 55 ≠ 30 ≠ 10; whole ≠ half ≠ nothing throughout; "reduced by the deposit" ≠ "nothing withheld at all" ≠ "stands as it is"; "divided by the instalments allowed less those taken" ≠ "divided by the instalments allowed" ≠ "the whole called in one payment"; "price less child and third-adult discounts" ≠ "price less child discount" ≠ "the price as recorded". The single structural caveat is `amendment_stage_addition`, whose tier 1 ("per traveller") and tier 2 ("once for the package") coincide numerically on a party of one; they are distinct as computations, and both tasks' parties are larger than one.

**Every condition and every outcome is one that line of business actually holds.** Judged against ordinary package-holiday practice: escalating amendment charges for repeat changes; pricing a change after the balance date as a cancellation-and-rebooking; an annual allowance of waived change fees by loyalty tier, halved once partly used; a cancellation ladder by days to departure; capping the penalised value at monies actually paid where the party has not paid in full; ring-fencing a refundable deposit; an administration charge that hardens once the file has been worked through; a loyalty relief on penalties for frequent bookers; collecting a low-deposit shortfall with the balance; splitting the remaining balance across the instalments still to run; waiving or halving withheld penalties where the operator itself changed the itinerary, with a supplier cancellation counted as significant and a component substitution not; retaining a non-recoverable FX markup on a refund paid over in a foreign currency; and a club goodwill gesture reduced where the party has already had the file amended. No tier states a condition that holds of every customer who reaches its write, and no fall-through publishes a treatment no such business would apply — each fall-through is the plain standard case (the administration charge, the standing share, the full withholding, no concession, no retention, the balance called in one payment).

**Labels honest.** Each `method` factor changes the algorithm, not a number: `amendment_starting_amount_basis` changes which charge and what it is read against; `instalment_priced_package_value` changes which deductions enter the base; `instalment_split_basis` changes whether and by what the outstanding figure is divided; `penalised_value_basis` changes which quantity the share acts on; `deposit_ring_fence` changes whether a subtraction, a zeroing or an identity applies; `returnable_intake_basis` changes which ledger lines make up the intake. Each `parameter` factor substitutes a rate, a count basis or a money amount into an unchanged formula. No `method` tier names a computation rule the charter does not state.

**Baselines.** Each policy's `baseline.rule` is a subset of its own `rule` sentences and is self-sufficient: a reader computes a definite number from it and the records without any factor. `baseline.params` names `amendment_admin_fee_per_person_usd` (amendment), `[]` (instalment), `standing_cancellation_share_pct` (penalty), `[]` (refund) — in each case exactly the default keys the baseline rule uses. Every factor's fall-through tier is that baseline: `starting_amount = admin fee × travellers`, `stage_addition = 0`, `repeat_multiple = 1`, `payable_share = 1`, `priced_package_value = package price`, `club_concession_pct = 0`, `loyalty_concession_rate = 0`, `deposit_difference_called = 0`, `instalment_called = outstanding_amount`, `cancellation_share_pct = standing share`, `penalised_value = package price`, `ladder_after_deposit = ladder_amount`, `administration_withheld = 0`, `loyalty_relief_applied_pct = 0`, `returnable_intake = money_paid_in`, `withheld_share = 1`, `goodwill_rate = 0`, `markup_share = 0`. No straw man: none is a zero where the baseline rule states a figure, and none is the correct value under another name. Whether each bears weight is a fact about one world and lives in each task's `factor_weight`.

### findings

**F-1 — observation (charter-global; bears on task 1).** *The four cancellation ladder shares are written as the product's and computed as the desk's.*
- Symptom: `bundle_ext_cancellation_penalty_withholding.rule` says "The cancellation share taken on the penalised value is **the product's** standing cancellation share… the cancellation share is instead **the product's** near-departure share… **the product's** inside-six-weeks share… **the product's** inside-three-months share", while `compute` binds `cancellation_share_pct` to `K('near_departure_share_pct')`, `K('inside_six_weeks_share_pct')`, `K('inside_three_months_share_pct')`, `K('standing_cancellation_share_pct')` — policy constants that are identical across all six variants.
- Root cause: the ladder was lifted into the policy's own `params` block while the rule kept attributing it to the product, and the base clause that bound the genuine product parameter was declared superseded by an entry whose `replaced_by` speaks only about the penalised value.
- Evidence: charter `params: {standing_cancellation_share_pct: 10, near_departure_share_pct: 90, inside_six_weeks_share_pct: 55, inside_three_months_share_pct: 30}`; `parameter_schema.cancellation_ladder_pct`; `variants[].parameters.cancellation_ladder_pct` — Value 25/50/75/100, Flex 15/35/60/100, All-Inclusive 20/45/70/100, Escorted 25/55/80/100, Ocean Cruise 30/60/85/100, Luxury Collection 10/30/55/90; base `bundle_cancellation.params.per_tier.<variant>.cancellation_ladder_pct: =cancellation_ladder_pct`; `overwrite[0].superseded_clause` = "The penalty is read off the product's cancellation ladder by how many whole days lie between the cancellation and the departure date, applied to the package price of the places being given up."
- Consequence: **none demonstrable on this difficulty's worlds.** The only task that reaches this policy is task 1, whose package is a Luxury Collection Package, and the four `K` values (10 / 90 / 55 / 30) are exactly that variant's `cancellation_ladder_pct` (`90_or_more_days: 10`, `14_or_fewer_days: 90`, `42_to_15_days: 55`, `89_to_43_days: 30`). Both readings give 30 % at 58 days, so no second answer exists in the audited world. Latent only: on a Flex package at 58 days the two readings would give 30 % and 35 % — 7 779.00 against 9 075.50 before the ring-fence.
- Affected artifact: `env/env_0000_online_travel_agency/tasks/vacation_packages_desk/bundle.extended.yaml`, `bundle_ext_cancellation_penalty_withholding` — `params`, `rule` (the four "the product's … share" sentences), `compute.cancellation_share_pct`, `overwrite[0]`, and `factors[cancellation_share_ladder].ladder` which repeats the same attribution.
- Relation to previous revisions: first revision.

**F-2 — observation (charter-global; bears on task 0).** *A companion sentence of a superseded base clause is left standing and says the opposite of the extended reading.*
- Symptom: `bundle_ext_balance_instalment_call.overwrite[1]` names "the club tier held on the deposit date decides the package discount applied to the price" as superseded, but the same base policy's next-but-one sentence — "Where the member's tier changes between deposit and departure, the discount applied at deposit stands and is neither topped up nor clawed back." — is named in no `overwrite` and is therefore inherited in full, while `compute.club_package_rate` reads `CPARAM('club', 'package_discount_pct', status='active')`, the tier standing at handling time.
- Root cause: the override was declared against one sentence of a two-sentence rule; the sentence-by-sentence sweep stopped at the clause that carried the phrase being replaced.
- Evidence: base `bundle_club_and_corporate_interaction.rule`, both sentences; `bundle_ext_balance_instalment_call.overwrite[1]`; `bundle_ext_balance_instalment_call.compute.club_package_rate`.
- Consequence: **none demonstrable on this difficulty's worlds.** On task 0 the club card is `Wanderlane Platinum` with `tier_effective_date: 2026-01-01`, and the deposit was taken `2026-04-25` — the tier standing on the deposit date and the tier standing now are the same card, so both readings give `package_discount_pct = 5`. The demonstration is in `0.md` / `factor_weight`. Latent only: on a world where the card's `tier_effective_date` falls after `deposit_taken_at`, the inherited sentence and the extended rule would name different tiers with no way to reconcile them. Note for completeness that `bundle_ext_cancellation_refund_payout` reads the same `CPARAM` while declaring no override against this base policy — that is not an override, because the base sentence governs "the package discount applied to the price" and the goodwill gesture is a share of the reduced withholding added back to a refund, a different quantity.
- Affected artifact: `bundle.extended.yaml`, `bundle_ext_balance_instalment_call.overwrite`, and base `bundle_club_and_corporate_interaction.rule`.
- Relation to previous revisions: first revision.

**F-3 — observation (charter-global; bears on neither task's scored value).** *A base carve-out disappears with the sentence that carried it.*
- Symptom: `bundle_ext_package_amendment_charge.overwrite[1]` supersedes "Any other amendment carries the product's administration charge per traveller, and correcting the contact address or contact number is free and carries none." The `replaced_by` keeps the administration charge as the fall-through starting amount and reinstates no free-of-charge case, so a contact correction now falls through to `P('amendment_admin_fee_per_person_usd') × party_travelling`.
- Evidence: base `bundle_amendment.rule`; `bundle_ext_package_amendment_charge.overwrite[1]`, `rule` (second sentence), `compute.starting_amount`.
- Consequence: none on either world — task 0's latest approved change is a `name_change` (tier 1), and no `bundle_change_requests` row of either task is a contact correction. Declared, so not an undeclared override; recorded because the merged semantics lost a base provision that nothing replaces.
- Affected artifact: `bundle.extended.yaml`, `bundle_ext_package_amendment_charge.overwrite[1]`.
- Relation to previous revisions: first revision.

**F-4 — observation (charter-global).** *A rule phrase with no operation behind it.*
- Symptom: `bundle_ext_balance_instalment_call.rule`: "The priced package value the call is worked out on is the package price recorded on the package **for the party travelling**." `compute.priced_package_value` reads `F('package_price_usd')` with no party-travelling operation; the divisor by travellers lives in `per_person_price`, a different binding with a different quoted sentence.
- Evidence: `bundle_ext_balance_instalment_call.rule`, `compute.priced_package_value`, `compute_basis.priced_package_value`, `factors[instalment_priced_package_value].baseline`.
- Consequence: none — the phrase adds no branch and changes no number; the fall-through tier and the baseline both read the recorded price unchanged. A reader could momentarily look for a per-party adjustment that is not there.
- Affected artifact: `bundle.extended.yaml`, `bundle_ext_balance_instalment_call.rule`.
- Relation to previous revisions: first revision.

**F-5 — observation (charter-global; bears on task 1).** *"The agency service fee is never returned" is superseded as a rider and nowhere reinstated.*
- Symptom: `bundle_ext_cancellation_penalty_withholding.overwrite[2]` supersedes the whole base sentence "The product's administration charge is withheld per traveller on every cancellation whatever the ladder says, and the agency service fee is never returned." The rider about the agency service fee is not restated anywhere in the charter, while `bundle_ext_cancellation_refund_payout.returnable_intake` tier 1 adds "every deposit, every instalment and those components" — and an agency service fee is posted as a `bundle_component_charge` (`charge_category: agency_service_fee`).
- Evidence: base `bundle_cancellation.rule`; base `bundle_booking_terms.rule` ("The agency service fee is charged per traveller when the deposit is taken and is never returned."); `bundle_ext_cancellation_penalty_withholding.overwrite[2]`; `bundle_ext_cancellation_refund_payout.compute.components_charged` and `.returnable_intake`.
- Consequence: **none demonstrable on task 1's world.** The Luxury Collection Package carries `agency_service_fee_per_person_usd: 0.0`, and task 1's ledger holds one component line only — a `room_upgrade` of 1 330.00 — so no agency service fee is returned. Note that the identical sentence also stands in `bundle_booking_terms`, which no `overwrite` touches, so the provision survives there; that is why this is an observation rather than a lost provision. Latent only: on a Flex or Value package with agency service fee lines, the superseded rider and the surviving one would have to be reconciled by the reader.
- Affected artifact: `bundle.extended.yaml`, `bundle_ext_cancellation_penalty_withholding.overwrite[2]` and `bundle_ext_cancellation_refund_payout.compute.returnable_intake`.
- Relation to previous revisions: first revision.

No charter-global `SOURCE-POLICY RED`. Checks 1 (finding half), 2, 3, 6 and 7 and the structural half of the factors relationship all PASS.

## closing_checklist

Written after both tasks' `source_gt_comparison` sections. This section is post-reveal by construction and sits below the charter-global section, which stays pre-reveal.

**The difficulty does not close.** The four substantive relationships hold on both tasks, but five `SOURCE-FACTOR RED` findings stand open against the proof the two task files submit for the factors relationship. They are listed at the end of this section.

- **Per-task audit files correspond one-to-one with the tasks.** `0.md` and `1.md` sit alongside this file in `env/env_0000_online_travel_agency/audits/policy_task/vacation_packages_desk/`, matching `tasks/0.json` and `tasks/1.json`. This is revision 1; there is no older revision to preserve. Both comparison sections carry a verdict, and neither carries a clean PASS — see below.
- **Extended policies fully covered, task scopes pairwise disjoint.** Task 0 claims `bundle_ext_balance_instalment_call` (root) with `bundle_ext_package_amendment_charge` (prerequisite); task 1 claims `bundle_ext_cancellation_refund_payout` (root) with `bundle_ext_cancellation_penalty_withholding` (prerequisite). Each scope spans the whole problem tree — root and prerequisite together. The two scopes share no policy and together cover all four. Confirmed against `charter_scope` at the reveal: identical to the scopes derived independently. Task tools and GT are closed: four tools, two per task, each bound to exactly one policy, each called exactly once in its task's gold sequence.
- **Each task tool uses an independently generated, frozen uuid8.** `6b64f72d`, `b6602c09`, `6c06e997`, `313c063d` — pairwise distinct, no shared prefix, no sequence, not batch-derived. See `action_binding_and_uuids`.
- **Problem trees.** Each task has one prerequisite problem (inside the 1-to-3 band), one `value_input` edge against a floor of `max(n − 1, 1) = 1`, and one problem resolved by an `owner=user` tool — `settle_package_instalment_b6602c09` in task 0, `release_package_refund_313c063d` in task 1, both the root problem and both handed over passively by the persona. Neither tree has a cycle. Across the difficulty the four `prerequisite` edges form two disjoint single edges, so the whole-difficulty graph is a DAG and no cross-task reference creates a cycle.
- **Computations.** Four computations, each with a self-sufficient baseline giving a definite number different from gold (140.00 / 101.25; 6 685.05 / 2 032.76; 2 460.00 / 5 702.63; 18 897.37 / 22 929.10). Factor counts 4, 5, 5, 4 — all inside 4–6, each with at least 2 `parameter` and 1 `method`. Every ladder has at least three tiers stated in full in its own `rule`, tiers distinct in outcome, with conditions and outcomes that line of business actually holds. Each task carries at least one multi-source factor and at least one `cross_difficulty: club` factor whose other-product holding and ledger rows are seeded and charter-consistent. Every one of the 18 factors was proved to bear weight on its own task's world against an honest baseline, by the auditor's own substitution runs; all 18 recomputed baseline figures match `computations[].factor_sensitivity` and all four whole-baseline figures match `computations[].baseline_result`, figure for figure.
- **Instantiation-stage gates re-run once on the final form**, from the repository root, after the audit:

```
check_extended.py       EXTENDED OK        (extended_policies=4, cross-cat=4, task_tools=4, tasks=2, no_handoff=True)
check_task_tools.py     TASK TOOL CONTRACT OK   (4 tools)
replay_tasks.py         REPLAY OK          0.json 12 acts / 26 rows match; 1.json 11 acts / 21 rows match
check_solvability.py    SOLVABILITY OK     K=2 identity preamble; 0.json 3 base gates / 12 seed rows; 1.json 2 / 9
check_compute.py        COMPUTE OK         branches mean 24.00, steps mean 11.50, history_rows_max 16, branches_max 25
check_grounding.py      GROUNDING OK       0.json 4 id attrs / 2 answers / 2 writes / 12 cond; 1.json 4 / 2 / 2 / 9
check_cross_fire.py     SCOPE OK           policies=4, hard-fails=0
```

All seven green, unchanged from the entry snapshot — as expected, since the audit edited no artifact and since the open findings live in prose the gates do not read.

**Open findings blocking the close.** All five are of one kind and one root cause: a sentence of `design_rationale` that asserts a figure for a named perturbation, where recomputing that perturbation gives a different figure. In every instance the figure quoted is a single-factor **baseline substitution** figure pressed into service as a **row-deletion** or **all-cross-category-off** figure, which is a different world.

| finding | file | sentence | figure asserted | figure on recomputation |
| --- | --- | --- | --- | --- |
| T0-1 | `0.md` | "Remove the child and the priced package value jumps from 7286.40 to 7524.00" | 7 524.00 | 7 920.00 (instalment 2 231.28) |
| T0-2 | `0.md` | "without it the club concession halves and the call moves to 2154.20" | 2 154.20 | 2 093.48 |
| T0-3 | `0.md` | "Forcing every cross-category read off moves the instalment to 2178.82" | 2 178.82 | 2 178.48, or 2 212.23 under the other reading |
| T1-1 | `1.md` | "Delete them and the penalty rises from 5702.63 to 7642.63" | 7 642.63 | 6 673.60 |
| T1-2 | `1.md` | "Forcing every cross-category read off moves the penalty to 5879.00 and the payout to 22732.50" | 22 732.50 alongside 5 879.00 | 22 645.64 |

**What is not in doubt.** Every scored value, every `factor_sensitivity` figure, every `baseline_result` and every `edge_load_bearing` figure in both task files was recomputed independently by this audit and agrees exactly. The conclusions the five sentences were written to support — that those seed rows and those cross-category reads bear weight — all hold under correct recomputation. The defect is confined to the narrative proof, and it is reported here rather than repaired: this audit edited no artifact and arranges no fix.

**Verdict.** Policy self-consistency **PASS** (both tasks). Problem tree holds **PASS** (both tasks). Unique solution **PASS** (both tasks). Factors bear weight — the relationship holds on both worlds, but the proof submitted for it carries five false world-assertions, recorded as `SOURCE-FACTOR RED`. The difficulty therefore does not pass the source-layer audit in this revision.

---

## revision_2

Round-2 re-audit. Revision 1 above is left exactly as written; nothing in it has been rewritten to accommodate the rework.

### re_derivation_basis

| artifact | round 1 | round 2 | consequence under the re-audit rule |
| --- | --- | --- | --- |
| `bundle.extended.yaml` | `11e17ac21b84ebac`, 164062 B | `2611eabf0d1c23a7`, 164868 B | **moved** → every charter-global section re-derived in full |
| `task_tools.py` | `944e8ae99f8c1e2e`, 11248 B | `944e8ae99f8c1e2e`, 11248 B | unchanged |
| `0.masked.json` | `62c9fba10bcdc112` | `62c9fba10bcdc112` | task 0's world unchanged |
| `1.masked.json` | `77eb93fdfaf748bc` | `77eb93fdfaf748bc` | task 1's world unchanged |

Both rebuilt views were checked against the live task files rather than taken on trust: for each task, the whitelist `{frozen_time, user_scenario, initial_state}` extracted from `tasks/<id>.json` compares **equal** to the view file, and the view files hash to the two values the brief quotes. The two task files themselves have moved (proof prose only — see `0.md` and `1.md` revision_2).

**Freezing.** A blind re-derivation is not available in round 2 and is not claimed: GT was revealed at the end of round 1. What round 2 verifies is different in kind and is stated as such — verbatim correspondence inside the artifacts, and recomputation of every asserted figure from the records. Round 1's blind derivations stand untouched on disk and are the only blind evidence in this report. The reworker's own figures and reasoning were withheld from this audit by the coordinator and were not consulted; every verdict below rests on the artifacts.

### what did not move (regression sweep)

Verified mechanically against the round-2 file, not against the reworker's account:

- **The base copy is still verbatim from the blueprint.** All 10 non-`extended_policies` top-level sections of `bundle.extended.yaml` compare **equal** to `env/env_0000_online_travel_agency/blueprint/products/bundle.yaml`, and all 11 base policies compare equal object for object. The two narrowed `superseded_clause` strings (F-3, F-5) were obtained by quoting less of the base sentence, **not** by editing the base sentence — the failure mode that would have made an override look declared by moving the goalposts. `extended_policies` remains the only added top-level key.
- **The computational core is byte-identical to round 1.** All four `params` blocks; every `compute` binding of all four policies; all 18 factors' `id`, `effect`, `decides`, `baseline` and `cross_difficulty`; every ladder's tier count (4/3/3/3, 3/3/3/3/3, 4/3/3/3/3, 3/3/3/3); both `baseline.params` lists; and both `prerequisite` blocks including their `policy_source`, `condition`, `gate`, `form`, `resolved_by` and `effect` strings.
- **Tool module unchanged**, so the four uuid8s `6b64f72d`, `b6602c09`, `6c06e997`, `313c063d` are the frozen round-1 values — still pairwise distinct, no shared prefix, no sequence, not batch-derived — and no function body judges a prerequisite. Re-read to confirm rather than carried on the hash alone.
- **Gold re-derives unchanged** under the round-2 charter: 101.25 and 2 032.76 on task 0, 5 702.63 and 22 929.10 on task 1, recomputed from the round-2 `rule`/`compute` and the unchanged worlds. Every `expected`, `baseline_result`, `factor_sensitivity` figure, step index, owner and argument in both task files is identical to round 1.
- **All seven instantiation gates re-run green** on the round-2 form: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (12/26/26 and 11/21/21, both matching), SOLVABILITY OK, COMPUTE OK (branches 24.00, steps 11.50, history_rows_max 16, branches_max 25), GROUNDING OK, SCOPE OK — identical figures to round 1.

The reworker's claim that the charter edits are declaration- and prose-only, and that every gold value is byte-identical, is therefore **verified** — with one exception, which is that a prose edit was left half-finished (R2-1 below).

### policy_conflict_scan (re-derived)

Unchanged in substance from revision 1. The same four extended policies, the same triggers, subjects, `computes` and target tools; the two policies sharing the subject `bundle_penalty_charge` are still separated by `charge_category` and by disjoint triggering states. Time anchors, cross-category read boundaries and terminal states are as revision 1 records them. Task scopes remain pairwise disjoint and jointly complete. One structural change: `bundle_ext_cancellation_refund_payout.base_policy_refs` now carries a fifth entry, `bundle_evt_supplier_notice` — see T1-3 in `1.md`.

### rule_compute_equivalence (re-derived)

Re-run mechanically over the round-2 file. Every sentence of every `compute_basis` entry, and every sentence of every `baseline.rule`, was tested for verbatim presence in its own policy's `rule`. **One fails**, and it is new in this round:

- `bundle_ext_cancellation_penalty_withholding.compute_basis.cancellation_share_pct` contains the sentence *"Where between fifteen and forty-two days lie between them, the cancellation share is instead the inside-six-weeks share of the desk's cancellation schedule."* — which appears nowhere in that policy's `rule`. The rule's corresponding sentence reads *"Where between fifteen and forty-two days lie between them, the cancellation share is instead **the product's inside-six-weeks share**."* See finding **R2-1**.

All other `compute_basis` sentences, all `baseline.rule` sentences, both `prerequisite.policy_source` sentences and all nine `overwrite.superseded_clause` strings (against their named base rules) and `replaced_by` strings (against their own extended rules) are verbatim. Every `P('…')` name used in any `compute` expression exists in `parameter_schema`.

### action_binding_and_uuids (re-derived)

Each `(target_tool, computes)` pair still claimed by exactly one policy; four tools, four uuid8s, all independently generated and frozen; no docstring names another tool, states a position in a sequence, or carries an ordering word. PASS, unchanged.

### prerequisite_graph (re-derived)

Both `prerequisite` blocks are byte-identical to round 1: two edges, both `value_input`, both `form: state` with no `fallback_reason` owed, gates `charges_standing` and `withheld_standing` both real bindings of their blocked policy's `compute`, `resolved_by` in each case the depended-on policy's `target_tool`, every `problem` pointing at another extended policy in this file, the whole graph two disjoint edges and therefore acyclic. No authoring-viewpoint phrasing. PASS, unchanged.

### prerequisite_sentences (re-derived)

Both `policy_source` sentences are still verbatim in their blocked policy's own `rule` — re-checked against the edited rules, since a prose edit is exactly what could have broken them. Both still pass the four-point test; both are still state form with exactly one write of this difficulty bringing the waited-on state about; neither depended-on rule restates the sentence; no rule carries a second wording, a tool name or another problem's id. PASS, unchanged.

### override_declarations (re-derived)

Nine `overwrite` entries in round 2 against six in round 1. Sentence-by-sentence sweep re-run over every `base_policy_refs` entry of all four policies.

| entry | base policy | change since round 1 | verdict |
| --- | --- | --- | --- |
| amendment [0] | `bundle_amendment` | unchanged | declared, merged semantics unique |
| amendment [1] | `bundle_amendment` | **narrowed** to "Any other amendment carries the product's administration charge per traveller" | closes F-3 |
| instalment [0] | `bundle_payment_schedule` | unchanged | declared |
| instalment [1] | `bundle_club_and_corporate_interaction` | **new** — supersedes "Where the member's tier changes between deposit and departure, the discount applied at deposit stands and is neither topped up nor clawed back." | closes F-2 |
| instalment [2] | `bundle_club_and_corporate_interaction` | was [1]; text unchanged | declared |
| penalty [0] | `bundle_cancellation` | **split** — now supersedes only "The penalty is read off the product's cancellation ladder by how many whole days lie between the cancellation and the departure date", replaced by "The cancellation share taken on the penalised value is the standing share of the desk's cancellation schedule." | addresses F-1, but see R2-1 |
| penalty [1] | `bundle_cancellation` | **new** — supersedes "applied to the package price of the places being given up" | the other half of the split; declared |
| penalty [2] | `bundle_cancellation` | unchanged (deposit forfeiture) | declared |
| penalty [3] | `bundle_cancellation` | **narrowed** to "The product's administration charge is withheld per traveller on every cancellation whatever the ladder says" | closes F-5 |
| refund [0] | `bundle_refund_settlement` | unchanged | declared |

Every `superseded_clause` is a verbatim substring of its named base policy's `rule`; every `replaced_by` is a sentence of its own extended `rule`. Narrowing a `superseded_clause` is the right instrument here — it keeps the base copy untouched and hands the surviving remainder back to base — and in both narrowing cases the surviving remainder was checked for a **new** conflict with the extended rule:

- **F-3, the contact-correction carve-out.** Base's surviving "correcting the contact address or contact number is free and carries none" now stands against an extended fall-through that charges the administration charge per traveller. This is not a conflict on any reachable record: `db_schema.json`, `bundle_change_requests.request_type`, is an enum of `name_change`, `date_change`, `component_substitution`, `refund_review`, `surcharge_dispute` — there is no contact-correction request type, so a contact correction can never be "the latest change request approved against the package" and the fall-through can never be reached by that case. The fall-through is reachable only through `refund_review` or `surcharge_dispute`, for which base's superseded clause and the extended replacement prescribe the same treatment. **Clean.**
- **F-5, the agency service fee rider.** Base's surviving ", and the agency service fee is never returned" now stands in force against `bundle_ext_cancellation_refund_payout.returnable_intake`, whose first tier returns "every deposit, every instalment and those components" — and an agency service fee is posted as a `bundle_component_charge`. On task 1's world there is nothing to return (Luxury `agency_service_fee_per_person_usd: 0.0`, and the one component line is a `room_upgrade` of 1 330.00), so no consequence is demonstrable. This is the same latent tension revision 1 recorded under F-5, which noted that the identical rider also stands untouched in `bundle_booking_terms`; it is neither worsened nor created by the fix, and it stays an observation at the same force.

No anonymous intermediate factor, 0/1 multiplier or dropped branch. No author note calls a base output a wrong value.

### factor_ladders (re-derived)

Structure identical to revision 1 — 18 factors, counts 4/5/5/4, each policy with at least 2 `parameter` and 1 `method`, bindings pairwise disjoint within each policy, no `decides` equal to `result`, every ladder at least three tiers and pairwise disjoint as stated, no two tiers of one ladder sharing a value or method, every label honest, every condition and outcome one that line of business holds, each task carrying at least one multi-source and at least one `cross_difficulty: club` factor. Every tier of every ladder is stated in its policy's `rule` and implemented in `compute`, **with the single exception recorded as R2-1**: within `cancellation_share_ladder`, the values of tiers 1, 3 and the fall-through appear in the rule word for word ("the near-departure share of the desk's cancellation schedule", "the inside-three-months share of the desk's cancellation schedule", "the standing share of the desk's cancellation schedule"), while tier 2's value, "the inside-six-weeks share of the desk's cancellation schedule", does not — the rule attributes that one share to the product.

### findings (revision 2)

**Round-1 charter-global findings, verdict by item.**

| item | round-1 symptom | round-2 verdict |
| --- | --- | --- |
| **F-1** | the four cancellation shares written as "the product's" while `compute` binds desk constants | **NOT CLOSED** — three of four attributions corrected, the fourth left as "the product's inside-six-weeks share"; and the half-finished edit has introduced R2-1 |
| **F-2** | the un-superseded companion sentence of `bundle_club_and_corporate_interaction` | **CLOSED** — new `overwrite` entry names that sentence verbatim and replaces it with the club-concession sentence |
| **F-3** | the contact-correction carve-out lost with the sentence that carried it | **CLOSED** — `superseded_clause` narrowed to the first clause; base copy untouched; no new conflict, because no contact-correction request type exists in the schema |
| **F-4** | the rule phrase "for the party travelling" with no operation behind it | **CLOSED** — the phrase is gone from both `rule` and `baseline.rule`; the sentence now reads "The priced package value the call is worked out on is the package price recorded on the package." |
| **F-5** | "the agency service fee is never returned" superseded as collateral | **CLOSED** — `superseded_clause` narrowed so the rider survives in base; the residual tension with `returnable_intake` is the same observation revision 1 recorded, unchanged in force |

**R2-1 — observation, and F-1 carried forward.** *A find-and-replace that missed one occurrence, leaving the rule, the `compute_basis` and the factor ladder disagreeing about the same tier.*

- Symptom: `bundle_ext_cancellation_penalty_withholding` now describes its cancellation shares in three places, and they no longer agree for the 15-to-42-day tier.
  - `rule`: "Where between fifteen and forty-two days lie between them, the cancellation share is instead **the product's inside-six-weeks share**."
  - `compute_basis.cancellation_share_pct`: "…the cancellation share is instead **the inside-six-weeks share of the desk's cancellation schedule**."
  - `factors[cancellation_share_ladder].ladder[1].value`: "**the inside-six-weeks share of the desk's cancellation schedule**".
- Root cause: the F-1 rework rewrote the attribution of the standing, near-departure and inside-three-months shares from the product to the desk in the `rule`, and rewrote all four in the `compute_basis` and the ladder, but left the inside-six-weeks sentence of the `rule` untouched.
- Evidence: the three strings above, quoted from the round-2 file; and the mechanical sweep in `rule_compute_equivalence`, in which this is the only `compute_basis` sentence of the whole charter that is not verbatim in its own rule. The asymmetry is visible inside the one ladder: tiers 1, 3 and the fall-through are literal in the rule, tier 2 is not.
- Demonstrated consequence: **none on task 1's world, the only world that reaches this policy.** The customer sits 58 days out, on tier 3, so tier 2 is not taken; and the two readings of tier 2 agree numerically for this variant in any case, the Luxury Collection Package's `cancellation_ladder_pct.42_to_15_days` being 55 and `K('inside_six_weeks_share_pct')` being 55. Recorded as an observation on that ground, per the Core-constraints rule that what cannot be demonstrated is an observation. The latent consequence is now sharper than F-1's was, because the disagreement is internal to the artifact rather than between the artifact and a reader's expectation: a reader of the rule alone is sent to `cancellation_ladder_pct` for one tier and to the desk's schedule for the other three, and on five of the six variants those differ for that tier (Value 75, Flex 60, All-Inclusive 70, Escorted 80, Ocean Cruise 85, against the desk's 55). It also bears directly on the render stage, which carries rule sentences verbatim into the hub while the computation document is built from the `compute_basis`: the two documents would publish different sources for the same tier.
- Affected artifact and location: `env/env_0000_online_travel_agency/tasks/vacation_packages_desk/bundle.extended.yaml`, `bundle_ext_cancellation_penalty_withholding` — the inside-six-weeks sentence of `rule`, against `compute_basis.cancellation_share_pct` and `factors[cancellation_share_ladder].ladder[1].value`.
- Relation to previous revisions: F-1 of revision 1 is **not closed**; its scope has narrowed from four sentences to one, and the partial fix has created the internal three-way divergence, which revision 1 did not have (there, all four sentences agreed with each other and the disagreement was with the parameter schema alone).

## closing_checklist — revision 2

**The difficulty still does not close.**

- Per-task audit files still correspond one-to-one with the tasks; revision 1 is preserved intact in all three files and revision 2 is appended below it.
- Every round-1 `SOURCE-FACTOR RED` against the task files — T0-1, T0-2, T0-3, T0-4, T1-1, T1-2 — is **closed and independently re-verified by recomputation**; see `0.md` and `1.md` revision_2. T1-3 and T1-5 are closed or standing with an accurate recorded reason. Four of the five charter-global findings are closed.
- **Open:** F-1 (carried forward, narrowed to one sentence) and its consequence R2-1, both charter-global and both recorded above; and R2-2, a false assertion in task 1's proof prose about that same sentence, recorded in `1.md`.
- Scopes, trees, factor counts, `value_input` floors, `owner=user` writes, acyclicity, baselines and every factor's weight are as revision 1 established them and are unchanged: the computational core did not move, and neither did either world.
- Instantiation-stage gates re-run on the round-2 form: all seven green, figures identical to round 1.

**Verdict.** Policy self-consistency **PASS with one open observation** (R2-1 / F-1: an internal three-way divergence with no demonstrable consequence on the audited world, and a latent one on five of six variants and at the render stage). Problem tree holds **PASS**. Factors bear weight **PASS** — the proof defects that blocked revision 1 are repaired and re-verified. Unique solution **PASS**. The rework is sound in everything it touched except that one unfinished sentence.

---

## revision_3

Round-3 re-audit. Revisions 1 and 2 above are left exactly as written.

### re_derivation_basis

| artifact | round 2 | round 3 | consequence |
| --- | --- | --- | --- |
| `bundle.extended.yaml` | `2611eabf0d1c23a7`, 164868 B | `2b42c571d9fcbcde`, 164898 B (+30) | **moved** → charter-global sections re-derived in full |
| `task_tools.py` | `944e8ae99f8c1e2e` | `944e8ae99f8c1e2e` | unchanged |
| `0.masked.json` | `62c9fba10bcdc112` | `62c9fba10bcdc112` | task 0's world unchanged |
| `1.masked.json` | `77eb93fdfaf748bc` | `77eb93fdfaf748bc` | task 1's world unchanged |
| `tasks/0.json` | `6ca0ce86780ea729`, 138095 B | `3386ce253906590d`, **138095 B** | moved at identical length — see R3-1 |
| `tasks/1.json` | `e1f4da14925aea32`, 125746 B | `890ae9780872e33e`, 128686 B (+2940) | moved, as expected for the R2-2 fix and its log entry |

Both rebuilt views were again checked against the live task files rather than taken on trust: for each task the whitelist `{frozen_time, user_scenario, initial_state}` extracted from `tasks/<id>.json` compares **equal** to the view file. Freezing position is as recorded in revision 2: no blind re-derivation is available or claimed after round 1, and round 1's blind derivations stand untouched. The reworker's figures and reasoning were withheld and were not consulted; everything below was checked against the artifacts.

### R2-1 — CLOSED, verified mechanically

The one unconverted sentence is converted. `bundle_ext_cancellation_penalty_withholding.rule` now reads, for the 15-to-42-day tier, *"…the cancellation share is instead the inside-six-weeks share of the desk's cancellation schedule."* The string "the product's inside-six-weeks share" no longer occurs anywhere in that rule. All four shares — standing, near-departure, inside-six-weeks, inside-three-months — now carry the desk attribution in the `rule`, in `compute_basis.cancellation_share_pct` and in `factors[cancellation_share_ladder].ladder` alike, and the three faces agree tier for tier.

The only "the product's" phrases left in that rule are the two administration-charge sentences, and those are correct: they bind `P('cancellation_admin_fee_per_person_usd')`, a real entry of `parameter_schema` instantiated per variant. Every `P('…')` name used in any `compute` expression of the charter exists in `parameter_schema`.

**The mechanical sweep now returns zero misses across the whole charter** — the reworker's claim on this point is verified, not accepted. Re-run over all four extended policies: every sentence of every `compute_basis` entry is verbatim in its own policy's `rule`; every sentence of every `baseline.rule` is verbatim in its own `rule`; both `prerequisite.policy_source` sentences are verbatim in their blocked policy's own `rule`; all ten `overwrite.superseded_clause` strings are verbatim spans of their named base policy's `rule` and all ten `replaced_by` strings are sentences of their own extended `rule`; and all four `cancellation_share_ladder` tier values are verbatim in the rule. **MISSES: 0.**

With this, **F-1 of revision 1 is closed for all four shares**, three rounds after it was raised.

### what did not move (regression sweep)

- **The base copy is still verbatim from the blueprint.** All 10 non-`extended_policies` top-level sections of `bundle.extended.yaml` compare equal to `env/env_0000_online_travel_agency/blueprint/products/bundle.yaml`; `extended_policies` remains the only added key. The narrowed `superseded_clause` strings from round 2 still resolve as verbatim spans of the unedited base rules.
- **The computational core is unchanged.** A canonical hash taken over, for each extended policy, its `params`, every `compute` binding, `prerequisite`, `base_policy_refs`, `baseline.params`, `target_tool`, `computes`, `trigger`, every factor's `(id, effect, decides, baseline, cross_difficulty, ladder)` and every `overwrite` triple, comes to `94e088abefd4b639`, over the same shape recorded in revision 2: params 3/4/8/4, compute bindings 14/21/14/20, factors 4/5/5/4, overwrite entries 2/3/4/1, `base_policy_refs` 3/4/3/5. Nothing in the calculation moved.
- **Tool module unchanged**; the four uuid8s `6b64f72d`, `b6602c09`, `6c06e997`, `313c063d` are the frozen round-1 values, still pairwise distinct and not batch-derived, and no function body judges a prerequisite.
- **Gold re-derives unchanged** from the round-3 charter and the unchanged worlds: 101.25 and 2 032.76 on task 0, 5 702.63 and 22 929.10 on task 1. In both task files every `expected`, every `baseline_result`, all nine `factor_sensitivity` figures apiece, every `evaluation_criteria` step with its owner and arguments, and the whole of `prerequisite_closure` are byte-identical to rounds 1 and 2. Every intermediate quoted in `argument_uniqueness_tracing` is still present and still correct.
- **All seven instantiation gates re-run green** on the round-3 form: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

**On "the charter diff is exactly one field".** Everything checkable agrees with it: the base copy is verbatim, the computational core hash is unchanged, the sweep is clean, and the +30-byte delta is what converting "the product's inside-six-weeks share" (35 characters) to "the inside-six-weeks share of the desk's cancellation schedule" (61 characters) costs once the folded block is re-wrapped. The claim is therefore **corroborated on every face this audit can inspect**, but it is not proven at byte level: round-2 bytes were not retained by this audit, so a second, compensating edit elsewhere in the prose cannot be excluded by differencing. It can be excluded for anything that bears on a relationship, because each of those faces was re-derived above.

### charter-global sections (re-derived)

`policy_conflict_scan`, `action_binding_and_uuids`, `prerequisite_graph`, `prerequisite_sentences` and `factor_ladders` are as revision 2 re-derived them, with the single exception that `factor_ladders`' one recorded defect is gone: every tier of every one of the 18 ladders is now stated in its policy's `rule` with its condition and its value or method, and implemented in `compute`, with no exception. `rule_compute_equivalence` passes in both directions with zero misses. `override_declarations`: ten entries, unchanged from round 2 in text and effect, each verbatim against base and against its own extended rule.

### findings (revision 3)

**Round-2 findings, verdict by item.**

| item | round-2 symptom | round-3 verdict |
| --- | --- | --- |
| **R2-1** (and **F-1**) | rule / `compute_basis` / ladder disagreeing on the inside-six-weeks tier; the one `compute_basis` sentence in the charter not verbatim in its rule | **CLOSED** — converted; sweep returns zero misses; F-1 closed for all four shares |
| **R2-2** | task 1's proof prose certifying that the rule named all four shares as the desk's, which was false of the fourth | **CLOSED** — see `1.md` revision_3; the claim is now true and, as rewritten, checkable against the artifact |

**R3-1 — observation.** *Both task files moved, against a claim that one did; task 0's change could not be localized.*

- Symptom: the rework states the task-side diff is prose in one file only. `tasks/1.json` moved as expected (125 746 → 128 686 bytes, carrying the R2-2 rewrite and an `r5` log entry). But `tasks/0.json` also moved — sha256/16 `6ca0ce86780ea729` → `3386ce253906590d` — **at exactly the same length, 138 095 bytes both rounds**, which is the signature of an equal-length in-place substitution. Both files carry the same mtime, `2026-09-17 08:19:55`.
- Evidence and what was done about it: task 0 was re-verified against every substantive property this audit has ever established — the two gold values, both `baseline_result` figures, all nine `factor_sensitivity` figures, all twelve `evaluation_criteria` steps with owners and arguments, `charter_scope`, `required_documents`, `prerequisite_closure` in full including the 1 999.01 load-bearing figure, `db_closure_matches_initial_state`, and every numeric and date assertion in `design_rationale` (7 920.00, 1 980.00, 2 117.28, 142.00, 2 231.28, 2 243.42, 800.00, 2 187.95, 202.50, 2 093.48, 2 154.20, 44 days, 2 178.48, 2 212.23, 2 295.80, 140.00, 150.00, 56.25, 67.50, 6 685.05, 2 057.04, 1 871.42, 6 098.27, 33.75, and the dates and row ids they hang on). All hold. The task-0 revision log still ends at `r4 (round 2, …)` with no round-3 entry.
- Demonstrated consequence: **none found.** No substantive difference could be detected; the change, whatever it is, does not touch a scored value, a factor figure, a closure field or any assertion about the world that this audit can test.
- Why it is recorded anyway: a claim about which files were touched is exactly the kind of claim the coordinator instructed this audit to verify rather than accept, and it did not hold. Localizing it would need the round-2 bytes, which this audit did not retain — a gap in this auditor's own method, noted here so the next round can keep a copy before the rework.
- Affected artifact: `env/env_0000_online_travel_agency/tasks/vacation_packages_desk/tasks/0.json`.

**R3-2 — observation.** *An authoring placeholder left in both dossiers' problem-tree cards.*

- Symptom: both task files' `design_rationale` write the four-point test as "(2) the **XX** side is a record-visible state - an amendment charge standing on the package ledger…" (task 0) and "…- a cancellation penalty…" (task 1). "XX" is an authoring token with no referent.
- Consequence: none. It sits in `design_rationale`, not in the `prerequisite` field where authoring-viewpoint phrasing is a red light, and it asserts nothing about the world, so no relationship turns on it. It has been present since round 1 and was not introduced by any rework.
- Recorded because it is a token no reader of the finished dossier can resolve, and because revision 1 did not catch it — this is a correction to this audit's own coverage, not a new defect in the artifact.
- Affected artifact: `tasks/0.json` and `tasks/1.json`, `design_rationale`, problem-tree card.

**R3-3 — observation, and a correction to this audit's own record.** *Two counts stated in revision 2 are wrong.*

- Symptom: `## revision_2` / `override_declarations` opens "Nine `overwrite` entries in round 2 against six in round 1." Both figures are wrong. The table that immediately follows it lists **ten** rows, which is correct: amendment 2, instalment 3, penalty 4, refund 1. And revision 1's own `override_declarations` records two, two, three and one for the same four policies, which is **eight**, not six.
- Root cause: a miscount in the summary sentence of revision 2, written over a table that is itself correct.
- Consequence: none on any verdict — every entry was checked individually in revision 2 and again here, and the per-entry verdicts stand. The correct sentence is "Ten `overwrite` entries in round 2 against eight in round 1."
- Recorded here rather than by editing revision 2, which the re-audit rule requires be left untouched. An audit that red-lights false figures in another agent's proof owes the same treatment to its own.

## closing_checklist — revision 3

**The difficulty closes at the source layer.**

- The per-task audit files correspond one-to-one with the tasks; `_difficulty.md` sits alongside them; revisions 1, 2 and 3 are all preserved intact and in order in each file; every comparison section carries a verdict, and at revision 3 every one of them is a PASS.
- **Every finding of every round is closed or carries a recorded reason.** Round 1: T0-1, T0-2, T0-3, T0-4, T1-1, T1-2 closed and recomputed in round 2; T1-3 closed; T1-5 standing with an accurate reason; F-2, F-3, F-4, F-5 closed in round 2; **F-1 closed in round 3**. Round 2: R2-1 and R2-2 closed in round 3. Open at the end of round 3: nothing that demonstrates a consequence — R3-1, R3-2, R3-3 and the two latent observations carried from earlier rounds (F-5's residual tension between base's surviving agency-service-fee rider and `returnable_intake`, which no world here exercises; and T1-5's confirmatory `care` read).
- This difficulty's four extended policies are fully covered; the two task scopes are pairwise disjoint and each spans a whole problem tree, root and prerequisite together; task tools and GT are closed; each task tool carries an independently generated, frozen uuid8.
- Every task's problem tree has one prerequisite problem, one `value_input` edge against a floor of `max(n − 1, 1) = 1`, one problem resolved by an `owner=user` tool, and no cycle; the difficulty's edges together remain a DAG with no cross-task cycle.
- Every computation of every task declares a self-sufficient baseline giving a definite number different from gold (140.00, 6 685.05, 2 460.00, 18 897.37), and four to six factors — 4/5/5/4, each with at least 2 `parameter` and 1 `method`, each task carrying at least one multi-source and at least one `cross_difficulty: club` factor whose other-product rows are seeded and charter-consistent. Every ladder has at least three tiers stated in full in its own rule, distinct in outcome, with conditions and outcomes that line of business actually holds. All 18 factors were proved to bear weight on their own task's world against an honest baseline, by this audit's own substitution runs, and all 18 figures match `factor_sensitivity`.
- Instantiation-stage gates re-run once on the final form: all seven green.

**Verdict.** Policy self-consistency **PASS**. The problem tree holds **PASS**. Factors bear weight **PASS**. Unique solution **PASS**. All four relationships hold on both tasks with evidence on record, and **this difficulty passes the source-layer audit.** The render stage inherits a charter whose rule, quoted basis and factor ladders agree tier for tier on every one of the 18 ladders.
