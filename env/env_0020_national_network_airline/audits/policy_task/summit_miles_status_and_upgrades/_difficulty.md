# Policy-task audit — summit_miles_status_and_upgrades / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), round 1. I did not author these artifacts.
- Freeze time: 2026-09-24T18:05Z. Written before any task's GT was revealed. No content below comes from a masked field.
- Frozen inputs:
  - `tasks/summit_miles_status_and_upgrades/loyalty.extended.yaml` sha256 `c21489f9342c0e810d84609a72d650dbd1d6e00fca27dd0f83da8394a8189977`
  - `tasks/summit_miles_status_and_upgrades/task_tools.py` sha256 `7f2524f62984069085c399851f110ab3e0d5f9f20535b1908318be8f6f20ba2b`
  - Blueprint read: `blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/loyalty.yaml`, and the variant parameters of `products/ticket.yaml` (premium_cabin_bonus_percent, status_credit_percent, segment_length_threshold_miles, complimentary_upgrade_eligible) plus `products/companion.yaml` issue sources. I also read `erlbench/` and the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (read only).
- Fields I was allowed to read: the charter, the tool contracts, and the masked views (`task_index`, `frozen_time`, `user_scenario`, `initial_state`).
- Fields that stayed masked: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, the `db_closure*` fields, `worklog.md` (both), and the existing audits of other difficulties.
- Entry conditions: the gate snapshot came with the brief. check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire all returned rc=0. check_traceability is deferred to the render stage by design. The masked views came with their hashes, and I re-verified all four source and view hashes on disk. The input is complete.
- Base copy: `loyalty.extended.yaml` minus `extended_policies` is key-by-key equal to `blueprint/products/loyalty.yaml` (checked with a Python dict comparison: category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies are all equal).

### policy_conflict_scan

The charter has 8 extended policies. Each one owns a distinct `(target_tool, computes)`:

| policy | trigger | target_tool (owner) | computes | prerequisite edges |
|---|---|---|---|---|
| loyalty_ext_retro_credit_miles | state_due | post_retro_credit_03268362 (agent) | miles | — |
| loyalty_ext_retro_segment_qualifying_dollars | state_due | post_segment_qualifying_dollars_d0ee7d28 (agent) | qualifying_dollars | → retro_credit_miles (value_input, state) |
| loyalty_ext_tier_requalification | state_due | record_tier_requalification_84e40849 (agent) | new_tier | → retro_segment_qd (value_input, state) |
| loyalty_ext_reinstatement_fee | on_request | reinstate_expired_miles_d28241c8 (**user**) | fee_usd | → tier_requalification (vi, state); → retro_credit_miles (vi, state) |
| loyalty_ext_choice_bonus_miles | state_due | post_choice_bonus_miles_029b6e8c (agent) | miles | — |
| loyalty_ext_miles_upgrade_charge | state_due | post_miles_upgrade_charge_7f00044a (agent) | fee_usd | — |
| loyalty_ext_choice_upgrade_certificates | state_due | issue_choice_upgrade_certificates_458899d3 (agent) | certificate_count | — |
| loyalty_ext_upgrade_topup_purchase | on_request | buy_miles_4af9ade8 (**user**) | purchase_amount_usd | → choice_bonus (vi, state); → miles_upgrade_charge (vi, state); → choice_upgrade_certificates (state_gate, state) |

- Overlapping subjects and events. Several extended policies share an event type with a base policy:
  - loyalty_mqd_accrual: base loyalty_flight_earning, base loyalty_retro_credit_claims, and ext QD.
  - loyalty_bonus_credit: base loyalty_choice_benefits, base loyalty_goodwill_and_bonus, and ext bonus.
  - loyalty_award_redemption: base loyalty_award_redemptions and ext upgrade charge.
  - loyalty_miles_purchase: base loyalty_miles_purchases and ext top-up.
  - loyalty_certificate_issue: base loyalty_choice_benefits and ext certificates.
  - loyalty_tier_change: base loyalty_tier_qualification and ext tier.
  - loyalty_miles_reinstatement: base loyalty_miles_reinstatement_rules and ext fee.

  In every case the extended rule settles one quantity. The base sentence that settled the same quantity is named in `overwrite` (see override_declarations). Every other base provision on the same event (eligibility, windows, dedup, annual caps, status gates) is inherited unchanged. I found no pair of extended policies that settles the same quantity.
- Triggers and eligibility. The base gates live in base `eligibility` and apply unchanged:
  - retro window, flown-coupon name match and credited-once
  - redeem_active
  - reinstatement window and reinstate-once
  - purchase_open_membership and the annual purchase cap
  - selections_remaining
  - upgradeable_brand

  No extended rule weakens any of them.
- Time anchors. Every extended clock is either NOW (frozen_time) or a date carried on a record: the forfeiture activity_date, the coupon flight_date, the selection activity_date, the clearance request_date, the enrolled_date, or the companion issue_date. None conflicts with a base time anchor.
- Cross-category read boundaries:
  - ticket: brand, route_type, booking_channel, base_fare, payment_form, the coupons' cabin_flown and flight_date, and the ticket_services seat and bag amounts.
  - companion: the card-anniversary certificate's variant and issue_date.
  - club: variant and status.
  - pass: variant and status.

  Every one of these is read-only, and each is declared in `cross_category`.
- Terminal states. Each tool performs exactly one posting. The base terminal-state provisions agree with the tool effects:
  - The retro credit and the purchase make a dormant or enrolled membership active.
  - Reinstatement leaves the status and last_activity_date unchanged (base: reinstatement "does not itself count as qualifying activity").
  - The bonus credit does not touch last_activity_date (base: choice bonus miles "do not count as qualifying activity").
  - The retro credit explicitly posts no qualifying dollars (docstring), so the only writer of loyalty_mqd_accrual in this difficulty is post_segment_qualifying_dollars.
- Scope exclusivity and completeness. `charter_scope` is masked, so I reached this from my own blind tree derivations; the post-reveal comparison is in the task files. The 8 policies split into two disjoint components of the prerequisite graph:
  - {retro_credit_miles, retro_segment_qd, tier_requalification, reinstatement_fee}, rooted at reinstatement_fee.
  - {choice_bonus_miles, miles_upgrade_charge, choice_upgrade_certificates, upgrade_topup_purchase}, rooted at upgrade_topup_purchase.

  Two tasks over two disjoint trees are mutually exclusive, and together they cover all 8 policies.

### rule_compute_equivalence

For every binding of every extended policy, `compute_basis` quotes a verbatim span of the policy's own `rule`. Checked by script: every `compute_basis` value is a substring of the whitespace-normalised rule, and every sentence of every `baseline.rule` is a sentence of the rule. I then swept each rule back sentence by sentence:

- **retro_credit_miles**:
  - Base miles: `int(fare*P+0.5)` = "rounded to the nearest whole mile with halves rounded up".
  - Cabin bonus: `CPARAM(premium_cabin_bonus_percent)` for First or PE, else 0; half-up rounding.
  - Long-haul bonus: 1500/500/0 by route_type.
  - Returning bonus: DAYS(latest inactivity forfeiture, flight_date). 0..90 gives ceil-to-hundred of 25% of the base miles; 91..365 gives a flat 1000; anything else gives 0.
  - Booking bonus: app 10% / web 5%, floored.
  - Lounge bonus: premium club 1 mile/$, standard club 0.5 mile/$, floored.
  - Result: the plain sum.

  Every tier and every rounding rule is in both faces. "The retro credit carries no qualifying dollars itself" is implemented by the tool (qualifying_dollars=0.0). No gaps.
- **retro_segment_qd**:
  - The segment is read from the latest loyalty_retro_credit.
  - Share: status_credit_percent+25 for First or PE, status_credit_percent for Basic, 100 otherwise.
  - Returning treatment: int(share×1.5), int(share×1.25), or unchanged.
  - Route bonus: 150/60/0.
  - Card bonus: payment_form=credit_card AND the certificate family AND age<12 months.
  - The two bonuses are added after the treatment and are never multiplied.

  Everything matches.
- **tier_requalification**:
  - Tenure: MONTHS//12 against 10 and 5 years.
  - Card headstart.
  - Pass credit.
  - Premium-cabin credit: XCOUNT over coupons with cabin_flown first or PE in the last 12 months.
  - Ancillary credit: seat purchases plus bag charges over 12 months.
  - Thresholds, then `MX(reached, P(qualifying_dollars_threshold))` = "never falls below the tier already held by this count".
  - Chairman kept.

  One gap: "valid through the last day of month tier_validity_end_month of the year tier_validity_year_offset years after the qualification year" is a rule sentence that no binding implements. It fixes the tool's `tier_valid_through` argument, which `computes` does not name. The date is fully determined by base tier parameters, so I record this as an observation and not an empty promise.
- **reinstatement_fee**: band, prompt share (floor for 50%, ceiling for 75%), returning reduction, elite reduction with validity, card reduction, repeat surcharge, and `MX(0, …)` before the surcharge. Everything matches.
- **choice_bonus_miles**: late-posting treatment (ceil to the thousand ×1.25, ceil to the hundred ×1.1), card bonus, flight-accrual count over 12 months, tenure. Everything matches.
- **miles_upgrade_charge**:
  - Latest miles clearance, and the brand share.
  - Distance: ×2 above twice the threshold; ceil(×1.5) above the threshold.
  - Card reduction, timing reduction (DAYS clearance→flight), lounge reduction, `MX(0, …)`.

  "its miles are the base miles upgrade cost for that segment's length" fixes the tool's `miles` argument and has no binding (it is not in `computes`). Same observation as the tier validity date.
- **choice_upgrade_certificates**: late issue (×1.5 ceil, or +1), card, First-coupon count, lounge, certificate-redeem count. Everything matches. "the batch expires certificate_validity_months calendar months after the day it is issued" fixes the tool's expiry argument, which is not computed (observation).
- **upgrade_topup_purchase**:
  - Trip = the latest miles request ticket.
  - (requests − clearances) × the per-segment miles cost from MAX segment_miles against the threshold.
  - Minus the balance, rounded up to the increment, floored at the minimum.
  - Elite price with validity, repeat-buyer treatment, lounge reduction, cabin reduction, then (100 − card − pass)%.

  Everything matches.

No compute binding invents a basis the rule lacks, and no factor tier is missing from either face. Result: PASS, with three observations about tool arguments that the rule fixes but `computes` does not cover (tier_valid_through, the upgrade charge `miles`, certificate_expiry_date).

### action_binding_and_uuids

- Each of the 8 `(target_tool, computes)` pairs is claimed by exactly one policy.
- Tool bodies (`task_tools.py`): every tool performs one `ctx.create` and/or `ctx.update` with the values supplied. None calls a validator, refuses, raises or hints. The tool layer checks no prerequisite and no eligibility.
- Docstrings:
  - None names another tool.
  - None states a position in a sequence.
  - The ordering-like words present are "The member afterwards sees …" (post_retro_credit, post_segment_qualifying_dollars), "1 for the first segment" (an ordinal), and "active once it posts". These describe what the member views or the receipt semantics, not an order between actions (observation).
- uuid8s: 03268362, d0ee7d28, 84e40849, d28241c8, 029b6e8c, 7f00044a, 458899d3, 4af9ade8. All eight are distinct. They share no common prefix, suffix or sequence pattern, and none is a copy of another with a different tail. Result: PASS.

### prerequisite_graph

- `prerequisite` is filled in for all 8 policies (`[]` on retro_credit_miles, choice_bonus_miles, miles_upgrade_charge and choice_upgrade_certificates).
- Every `problem` is an extended policy id in this file. None points at a base policy or at itself.
- Graph: qd→retro; tier→qd; reinst→tier; reinst→retro; topup→bonus; topup→charge; topup→certs. It is acyclic, with two components.
- Every `policy_source` is verbatim in the blocked policy's own `rule` (checked by script against the normalised text).
- Every edge has `form: state`, and no `fallback_reason` is present, which is correct for state form.
- `resolved_by` equals the depended-on policy's `target_tool` on all 7 edges.
- `kind` and `gate`:
  - The value_input gates segment_fare, posted_qd, held_tier, credited_after_forfeiture and member_balance (twice) are all real compute bindings of the blocked policy.
  - The one state_gate (topup→certs) names `gate: loyalty_activity.event_type`. That is a field, not an eligibility id; the extended top-up policy has no eligibility entry of its own. The gate exists only as a rule sentence (observation).
- `condition` and `effect` wording: I found no authoring-viewpoint phrasing ("in this task", "at the opening"). Each condition matches the strength of its sentence (see below).

Result: PASS, with one observation.

### prerequisite_sentences

For each edge I applied the four-point test and checked that exactly one write brings about the waited-on state.

1. **qd → retro_credit_miles**. The sentence: "Qualifying dollars for a flown Crestline segment of a ticket that names no Summit membership are posted only after the membership's activity carries the retro credit entry for that segment, whose eligible fare they are computed on."
   - Connective: "only after".
   - State: "the membership's activity carries the retro credit entry for that segment", in the finder's words (loyalty activity, retro credit).
   - It names no tool, no id and no snake_case token. Its strength matches the condition (same ticket and segment).
   - Unique writer: post_retro_credit is the only tool that creates `loyalty_retro_credit`.
   - Derivation: the reader sees no retro credit entry for the uncredited coupon, finds that the retro-credit-miles rule is the one whose write "is credited by one retro credit entry", and performs it first.
2. **tier → qd**. The sentence: "The tier is not set until every Crestline segment the member flew in the calendar year carries its qualifying-dollar entry on the membership's activity."
   - Connective: "not … until".
   - State: every flown segment of the year carries a qualifying-dollar entry.
   - Unique writer: post_segment_qualifying_dollars is the only writer of `loyalty_mqd_accrual`, since the retro credit tool posts none by contract.
   - Scope ("every … in the calendar year") matches the condition.
3. **reinst → tier**. The sentence: "The reinstatement fee is fixed only after the membership's tier is up to date with the qualifying dollars of every Crestline segment the member flew in the calendar year."
   - Connective: "only after".
   - State: "the membership's tier is up to date with…". This is a record-visible state (tier on the membership against posted qualifying dollars), although deciding it requires the reader to evaluate the extended tier rule.
   - Unique writer: record_tier_requalification is the only tier writer.
   - Single reading: only if the reader uses the extended (overriding) tier rule. The base qualification sentence is superseded by a declared overwrite, so the reading is unique.
4. **reinst → retro**. The sentence: "The reinstatement fee is not fixed until every flown coupon of a ticket in the member's name carries a flight accrual or retro credit entry on the membership's activity."
   - Unique writer: no tool in the difficulty writes `loyalty_flight_accrual`, so post_retro_credit is the only writer.
5. **topup → bonus**. The sentence: "…worked out only after every choice selection of bonus miles on the membership carries its bonus credit." Unique writer: post_choice_bonus_miles.
6. **topup → charge**. The sentence: "…not worked out until every miles upgrade that has cleared on the membership carries its miles charge on the membership's activity." Unique writer: post_miles_upgrade_charge, the only writer of upgrade-kind `loyalty_award_redemption`.
7. **topup → certs**. The sentence: "A top-up purchase is recorded only after every choice selection of upgrade certificates on the membership carries its certificate issue." Unique writer: issue_choice_upgrade_certificates.

Other checks:

- No rule carries a second wording of any of these dependencies, and none names a tool or another policy id.
- The depended-on rules do not restate the sentences. The retro-credit rule's last sentence ("The retro credit carries no qualifying dollars itself; they are posted as their own entry for the credited segment") mentions the qualifying-dollar posting without an ordering connective, so it is not a second wording of edge 1 (observation).
- Undeclared cross-problem orders in extended rules: none found.
- Base rules that state a cross-problem order:
  - loyalty_account_closure: "those must be cancelled first".
  - loyalty_enrollment: "flights taken before enrolled_date are credited only through a retro-credit claim".

  Neither grounds an edge of this difficulty's trees (observation).

Result: PASS.

### override_declarations

I checked each extended policy sentence by sentence against its `base_policy_refs`.

- **retro_credit_miles**, against loyalty_retro_credit_claims, loyalty_flight_earning and loyalty_inactivity_expiry.
  - Overwrite names "The retro credit earns exactly what the flight would have earned on its flight_date under the flight-earning rule, at the tier held on that date". That covers two changes:
    - the tier date moves from flight_date to "the day the credit posts";
    - the flight-earning premium-cabin bonus is replaced by the extended five-addition sum, with a no-bonus standard.

    Both changes fall inside the named clause, so they are declared.
  - Inherited unchanged and not contradicted: retro window, min days, name match, credited-once, and the rule that award, companion and voucher-paid tickets earn nothing.
  - "rounded to the nearest whole mile" (base) against "halves rounded up" (ext) is a refinement, not a conflict.
- **retro_segment_qd**.
  - Overwrite names the flight-earning qualifying-dollar sentence ("eligible_fare_usd times … status_credit_percent … rounded to the cent"). Declared.
  - Not overwritten and still in force: base retro claims "posts qualifying dollars to the current calendar year only when the flight_date falls in the current calendar year". The extended rule is silent about it and does not contradict it; it matters only for a prior-year flight.
- **tier_requalification**.
  - Overwrite names "A member qualifies for a tier when qualifying_dollars_ytd reaches that tier's qualifying_dollars_threshold within one calendar year". Declared.
  - Inherited: immediate effect with tier_basis earned, the validity formula, soft landing at year end, challenges, and "never set lower before tier_valid_through". The extended "never falls below the tier already held by this count" is consistent with that last provision.
- **reinstatement_fee**.
  - Overwrite names the base fee clause ("for a fee from reinstatement_fee_ladder chosen by the number of miles reinstated…"). Declared.
  - Inherited: in full, once, the 180-day window, the latest inactivity forfeiture only, never on closure, and not counting as activity.
- **choice_bonus_miles**. Overwrite names "bonus_miles, which credits choice_bonus_miles_per_selection miles". Declared. The base goodwill and bonus provisions (a recorded bonus_reason, not activity) are inherited and honoured by the tool.
- **miles_upgrade_charge**.
  - Overwrite names "plus miles_upgrade_copay_usd per segment". Declared.
  - Inherited: the miles cost by segment length.
  - Inherited from award_redemptions: "Miles can be redeemed only from a membership whose status is active" and "The mile_balance must cover the full award price … miles cannot go negative". The extended rule is silent about both, and they remain binding on the charge's miles. This matters only if a task's balance does not cover the charge.
- **choice_upgrade_certificates**. Overwrite names "upgrade_certificates, which issues choice_upgrade_certificates_per_selection Summit Upgrade Certificates". Declared. The 12-month expiry is inherited and restated.
- **upgrade_topup_purchase**. Overwrite names "at miles_purchase_price_per_1000_usd for each thousand miles". Declared. Inherited: the 1000-mile increment, the 2000-mile minimum, the open-membership status gate, and the 150,000 annual cap.

Disguised forms checked:

- Anonymous intermediate: none. Every altered quantity is named in its overwrite.
- 0/1 multiplier: none.
- Dropped branch: base flight earning applies premium_cabin_bonus_percent to every fare brand. The extended cabin ladder applies it only to First and Premium Economy and zeroes the rest. For the current ticket charter this drops nothing, because every other brand has premium_cabin_bonus_percent 0 in `products/ticket.yaml`.

No author note calls a base output "wrong". Result: no undeclared override found.

### factor_ladders

Structure only. Weight is judged per task.

| policy | factors (effect, cross_difficulty) | P / M | multi-source factors (tier = conjunction over distinct records) |
|---|---|---|---|
| retro_credit_miles | retro_cabin_bonus (P, ticket), retro_long_haul_bonus (P, ticket), retro_returning_member_bonus (M, —), retro_booking_bonus (P, ticket), retro_lounge_bonus (P, club) | 4 / 1 | none strictly; returning is one relational condition over two records (forfeiture entry, coupon flight_date); lounge is a conjunction on one club record |
| retro_segment_qd | qualifying_share (P, ticket), returning_member_qualifying_treatment (M, —), route_qualifying_bonus (P, ticket), card_qualifying_bonus (P, companion) | 3 / 1 | **card_qualifying_bonus**: ticket.payment_form AND companion variant AND companion issue_date (ticket record + companion record) |
| tier_requalification | tenure_treatment (M, —), card_headstart (P, companion), pass_status_credit (P, pass), premium_cabin_status_credit (P, ticket), ancillary_status_credit (P, ticket) | 4 / 1 | none (each conjunction is on one record) |
| reinstatement_fee | forfeiture_band (P), prompt_request_treatment (M), returning_flyer_reduction (P), elite_reduction (P), card_reduction (P, companion), repeat_surcharge (P) | 5 / 1 | **returning_flyer_reduction**: retro or accrual entry dated after the forfeiture AND the holding's qualifying_dollars_ytd |
| choice_bonus_miles | late_posting_treatment (M), bonus_card_bonus (P, companion), flown_segment_bonus (P), tenure_bonus (P) | 3 / 1 | none |
| miles_upgrade_charge | copay_share (P, ticket), distance_treatment (M, ticket), card_copay_reduction (P, companion), clearance_timing_reduction (P, ticket), lounge_copay_reduction (P, club) | 4 / 1 | none strictly; distance (request segment_miles against the ticket-charter threshold) and timing (clearance date against coupon flight_date) are each one relational condition over two records |
| choice_upgrade_certificates | late_issue_treatment (M), card_certificate_award (P, companion), premium_flyer_award (P, ticket), lounge_certificate_award (P, club), certificate_user_award (P) | 4 / 1 | none |
| upgrade_topup_purchase | elite_purchase_price (P), repeat_buyer_treatment (M), lounge_price_reduction (P, club), upgrade_cabin_reduction (P), card_purchase_discount (P, companion), subscription_purchase_discount (P, pass) | 5 / 1 | none |

Checks run on every ladder:

- **Counts**: 4 to 6 factors per policy; at least 2 P and 1 M by label.
- **Bindings**: disjoint within each policy; `decides` is always an input and never `result`.
- **Tier counts and disjointness**: every ladder has 3 tiers as stated, pairwise disjoint.
- **Every tier is stated in the rule and implemented in compute**: yes, for all 8 policies.
- **Distinct outcomes**: no two tiers of one ladder share a value. The ticket charter gives premium_cabin_bonus_percent First 50 / PE 25 / others 0, and status_credit_percent Basic 50 / others 100. So:
  - retro_cabin_bonus is 50 / 25 / 0;
  - qualifying_share is 125 (First or PE) / 50 / 100.

  All distinct.
- **Fall-through equals the baseline**: true for every factor.
- **Honest labels**: see findings F-1 (method labels) and F-2 (the vacuous fall-through of upgrade_cabin_reduction).
- **Cross-difficulty reads** (difficulties: ticket, credit, loyalty, companion, business):
  - retro_credit_miles: ticket
  - retro_segment_qd: ticket, companion
  - tier_requalification: ticket, companion
  - reinstatement_fee: companion
  - choice_bonus_miles: companion
  - miles_upgrade_charge: ticket, companion
  - choice_upgrade_certificates: ticket, companion
  - upgrade_topup_purchase: companion

  `club` and `pass` are declared as `cross_difficulty` values, but no difficulty claims them. They are cross-category, not cross-difficulty. Every task still has a ticket or companion factor (observation).
- **Real-business sense**: the ladders are loyalty-programme treatments: cabin and route bonuses, welcome-back bonuses, channel promotions, card-holder perks, tenure, lounge and subscription perks, repeat-buyer discounts, reinstatement prompt-request discounts and repeat surcharges. Each is a plausible published treatment, and each fall-through ("no bonus", "standard price", "first band") is the ordinary customer's treatment. The exception is F-2.

### findings

**F-1 — method factors whose tiers only change a rate** (SOURCE-FACTOR RED where the computation's only method factor is one of these; see per-task files). Affects both tasks.

- Symptom: six of the eight `method` factors pick a multiplier or percentage for the same quantity. The tiers change only the number, sometimes with a different rounding mode:

  | factor | tier 1 | tier 2 | fall-through |
  |---|---|---|---|
  | returning_member_qualifying_treatment | floor(share×1.5) | floor(share×1.25) | share |
  | tenure_treatment | floor(qd×1.1) | floor(qd×1.05) | qd |
  | prompt_request_treatment | floor(band×50%) | ceil(band×75%) | band |
  | late_posting_treatment | ceil1000(m×1.25) | ceil100(m×1.1) | m |
  | distance_treatment | copay×2 | ceil(copay×1.5) | copay |
  | repeat_buyer_treatment | floor(price×0.9) | round2(price×0.95) | price |

  The base, the operation (a proportional scale) and the business meaning (an uplift or discount rate) are the same in all three tiers. Only the rate changes, plus a rounding mode picked per tier. The skill names this exactly: "a factor labelled `method` whose tiers only substitute a different number into the same formula (a rate…)".
- Contrast: two method factors do change the algorithm.
  - retro_returning_member_bonus: a percentage of base miles rounded up to the hundred, against a flat 1000.
  - late_issue_treatment: a multiplicative ×1.5, against an additive +1 certificate.
- Root cause: the method dimension is carried by a scaling rate. Rounding variation is used to make the tiers look like different procedures.
- Evidence: loyalty.extended.yaml, `factors[].ladder` and the matching rule sentences of retro_segment_qd, tier_requalification, reinstatement_fee, choice_bonus_miles, miles_upgrade_charge and upgrade_topup_purchase.
- Consequence: if these labels are counted honestly as `parameter`, these computations have 0 method factors and fall below the "at least 1 `method`" floor:
  - QD, tier and reinstatement (task 0);
  - choice bonus, upgrade charge and top-up (task 1).

  In QD and tenure, tiers 1 and 2 are literally one expression with a different constant. That is the cleanest case.
- Affected: the `factors[].effect` of those six factors.
- Relation to previous revisions: first audit.

**F-2 — upgrade_cabin_reduction has an unreachable fall-through** (SOURCE-FACTOR RED). Affects task 1.

- Symptom: the ladder is First → 1.50 / Premium Economy → 0.75 / "a trip with no waitlisted request takes nothing off". The fall-through can never hold for a customer who reaches this write:
  - The policy's scope is "A member whose miles do not cover the waitlisted miles upgrades of an upcoming trip".
  - "The trip covered is the ticket of the latest waitlisted miles upgrade request".
  - When no uncleared request remains, miles_needed is 0 and "nothing is bought", so no purchase write exists.
  - `db_schema.json` `loyalty_upgrades.target_cabin` is enum `["premium_economy", "first"]`, so every request selects tier 1 or tier 2.
- Consequence: the ladder has two reachable tiers, below the three-tier minimum. Its fall-through and baseline (0) is a treatment no customer in the policy's scope can receive, which is the straw-man baseline in another form. The top-up keeps 5 other factors, so its factor count stays inside the bounds, but this ladder does not count as a factor.
- Affected: loyalty_ext_upgrade_topup_purchase, factor `upgrade_cabin_reduction` and the rule sentence "…and a trip with no waitlisted request takes nothing off".

**F-3 — only task 0 has a multi-source factor** (SOURCE-FACTOR RED for task 1).

- The strict definition is: every non-fall-through tier is a conjunction or disjunction of two or more conditions over distinct records.
- Task 0's computations meet it through card_qualifying_bonus and returning_flyer_reduction.
- Task 1's four computations (choice_bonus_miles, miles_upgrade_charge, choice_upgrade_certificates, upgrade_topup_purchase) have no such factor:
  - Every compound tier (card: product AND issue age; lounge and pass: product AND status; elite: tier AND validity) is a conjunction over one record.
  - distance_treatment and clearance_timing_reduction do read two records (upgrade request and ticket charter; clearance and flown coupon), but each tier is one relational condition, not a conjunction of conditions.
- The gate reported this as satisfied, presumably counting evidence tags. The demonstration is on record in task 1's file.
- Affected: the four task-1 policies' factor sets.

**Observations** (not grounds for rework):

- O-1: three tool arguments are fixed by rule sentences but computed by no binding: `tier_valid_through`, the upgrade charge `miles`, and `certificate_expiry_date`.
- O-2: the state_gate `gate: loyalty_activity.event_type` names a field, not an eligibility id.
- O-3: docstrings use "afterwards" and "first" in non-sequencing senses.
- O-4: `cross_difficulty: club` and `cross_difficulty: pass` name categories that no difficulty claims.
- O-5: base rules carry cross-problem orders (closure "cancelled first", enrollment retro claims) that ground no edge here.
- O-6: the event model says a choice selection triggers its certificate issue or bonus credit, and a miles clearance triggers its redemption. The trees rest on seeded worlds where those triggered entries are absent. That is legitimate as an unmet state, but it runs against the event triggers.
- O-7: the retro-credit rule's sentence "they are posted as their own entry for the credited segment" refers to the depended-on relationship without an ordering connective.

## closing_checklist

Written after both reveals. The difficulty **does not close**: both tasks are SOURCE-FACTOR RED.

- Per-task files 0.md and 1.md correspond one-to-one with tasks 0 and 1, and sit beside this file. This is round 1; there are no older revisions. Both comparison sections are on disk. Neither carries a full PASS.
- Coverage and exclusivity: task 0 claims {retro_credit_miles, retro_segment_qd, tier_requalification, reinstatement_fee} and task 1 claims {choice_bonus_miles, miles_upgrade_charge, choice_upgrade_certificates, upgrade_topup_purchase}. `charter_scope` agrees. The two sets are pairwise disjoint and together cover all 8 policies. The task tools and GT are closed. Every uuid8 is independent.
- Trees: each has 3 prerequisite problems.
  - Task 0 has 4 value_input edges; task 1 has 2 value_input edges and 1 state_gate.
  - Each has one owner=user tool (reinstate_expired_miles, buy_miles).
  - Both are acyclic, and the whole graph across the difficulty is acyclic.
  - Every edge is unmet at frozen_time and bears weight.
- Factors: every declared factor bears weight on its task's world against an honest baseline, and every all-baselines figure is definite and differs from gold. Failing items:
  - F-1: six rate ladders labelled `method`, leaving the QD, tier and reinstatement computations (task 0) and the bonus, charge and top-up computations (task 1) without an honest method factor.
  - F-2: upgrade_cabin_reduction's vacuous fall-through (task 1).
  - F-3: no multi-source factor in task 1 under the definition's letter.
- Unique solution: PASS on both tasks. The GT matches the blind derivation item for item.
- Re-running the instantiation gates on the final form belongs to the coordinator. This audit did not run gates (per the brief). The snapshot supplied was all green, with check_traceability deferred.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: the same independent auditor as round 1. Freeze time: 2026-09-24T18:15Z onward. This section was written before any round-2 task JSON was opened.
- Inputs changed since round 1, so every charter-global section below is re-derived:
  - `loyalty.extended.yaml`: sha256 `237aee20e876c4059a055d43efabef1f78c1814201faaed50370f1590e9e242e` (round 1: `c21489f9…9977`)
  - `task_tools.py`: sha256 `d7a4c54b321724c8faec0e8ace70b43cb6bd97cb474e64b623cb43eb88de5e32` (round 1: `7f2524f6…ba2b`)
- Masked views:
  - r2 task_0: `97510caf…454d`. This equals r1 byte for byte, which I verified with a JSON comparison.
  - r2 task_1: `228c6908…0f45`. Only `user_scenario` changed. `frozen_time` and `initial_state` are identical to r1, verified the same way.
- Gate snapshot: the brief reports all gates green in round 2 (rc=0), with traceability deferred. The input is complete.
- Base copy: still key-by-key equal to `blueprint/products/loyalty.yaml`.
- contamination_disclosure (applies to both task files):
  - I legitimately saw the round-1 GT of both tasks at the round-1 reveal.
  - Both worlds are unchanged. Every round-2 ladder change keeps the tier each task takes: the QD returning near tier, tenure ≥ 10, prompt 31–90 days, late posting > 180, distance 1× to 2×, and repeat-buyer exactly one. The replacement factor on task 1 takes the First tier at 16 days.
  - My revision-2 derivations are therefore a mechanical re-evaluation of the new charter on the unchanged worlds. They cannot be blind to the round-1 gold values, and I do not present them as blind evidence.

### policy_conflict_scan (revision 2)

- The 8 policies, their `(target_tool, computes)` pairs, subjects, triggers and prerequisite edges are unchanged from revision 1.
- The ladder changes (below) alter no subject, trigger, eligibility gate, time anchor or terminal state.
- One new cross-category read: the top-up now reads ticket `next_departure_at`. It is declared in `cross_category` and in `compute_basis`.
- Scope exclusivity and completeness are unchanged: two disjoint trees covering all 8 policies.
- No conflict found.

### rule_compute_equivalence (revision 2)

- Scripted checks:
  - every `compute_basis` value is verbatim in its rule;
  - every `baseline.rule` sentence is in its rule;
  - every `K()` key a compute uses is declared in `params`, and every declared param is used. The removed params (returning_far_multiplier, mid_tenure_multiplier, prompt_near_share_percent, late_near_multiplier, very_long_multiplier, repeat_buyer_share) are referenced nowhere.
- Sentence-by-sentence sweep of the six rewritten ladder sentences and the new departure-cabin sentence against their compute bindings: each tier's condition and method or value is identical in both faces.
- Pre-existing observation, not a regression: the top-up binding `miles_short` has no `compute_basis` entry of its own. Its sentence ("The miles short are those costs added together less the membership's mile balance") is quoted under `miles_needed` and `member_balance`. I missed this in round 1.
- Observation O-1 stands, unchanged: tier_valid_through, the charge miles and the certificate expiry are fixed by rule sentences but produced by no binding.

### action_binding_and_uuids (revision 2)

- The 8 tool function bodies are statement-for-statement identical to round 1 (compared with `ast.unparse`). The owners, parameters and all 8 uuid8s are also unchanged, and each `(target_tool, computes)` pair is still claimed once.
- Docstring changes:
  - "The member afterwards sees" became "The member sees".
  - "1 for the first segment" became "1 for segment one".
  - Return-value phrasing changed: "after the credit" became "including the credit" / "net of the miles redeemed".
  - The new_tier enum glosses were re-worded: "entry-level elite tier", "the elite tier above Silver/Gold".
- An ordering-word grep over the file (before, after, afterwards, first, then, once, until, prior, later) now returns nothing.
- No docstring names another tool or states a sequence.
- The tool contract changes introduce nothing new. **O-3 is closed.**

### prerequisite_graph and prerequisite_sentences (revision 2)

- The 7 edges are unchanged: same problems, kinds, forms, gates and conditions.
- Each `policy_source` is still verbatim in its blocked rule (re-checked by script), and each `resolved_by` is still the target tool of the depended-on policy.
- The graph is acyclic.
- Each state-form edge still has exactly one writer, because the tool bodies are unchanged.
- The four-point tests and single-reading derivations of revision 1 carry over unchanged.
- **O-2** (state_gate `gate` names a field), **O-5** and **O-7** stand, recorded with no change as the reworker states.

### override_declarations (revision 2)

- The overwrite entries are unchanged. Their `replaced_by` wording still describes the whole replaced quantity.
- The rewritten tiers change the replaced quantities only inside their already-declared overrides:
  - qualifying dollars: flight-earning QD sentence
  - tier count: base qualification sentence
  - reinstatement fee: base fee clause
  - bonus miles: base choice bonus clause
  - co-pay: base co-pay clause
  - purchase price: base price clause

No undeclared override was introduced.

### factor_ladders (revision 2)

Only the changed factors are listed. The rest are unchanged from revision 1.

| factor | tier 1 | tier 2 | fall-through | algorithm genuinely changes? |
|---|---|---|---|---|
| returning_member_qualifying_treatment (QD) | floor(share×1.5) (0–90 days) | share + $250 flat (91–365) | share | yes: scale vs flat addition |
| tenure_treatment (tier) | floor(qd×1.1) (≥10 years) | qd + $200 flat (5–9 years) | qd | yes |
| prompt_request_treatment (reinstatement) | first-band fee $150 regardless of band (≤30 days) | ceil(band×75%) (31–90) | band | yes: flat replacement vs percentage |
| late_posting_treatment (bonus) | ceil1000(m×1.25) (>180 days) | m + 1000 flat (31–180) | m | yes |
| distance_treatment (charge) | copay + $40 flat (>2× threshold) | ceil(copay×1.5) (1×–2×) | copay | yes |
| repeat_buyer_treatment (top-up) | elite − $3 flat (≥2 purchases) | round2(elite×0.95) (exactly 1) | elite | yes |
| departure_cabin_reduction (top-up, replaces upgrade_cabin_reduction), parameter, cross_difficulty ticket | $1.50/1000 (departs ≤21 days AND request First) | $0.75/1000 (≤21 days AND Premium Economy) | 0 (departs >21 days) | n/a (parameter) |

- **F-1 closure (label honesty).** Every one of the six method ladders now pairs a proportional tier with a flat tier (or a flat replacement), so each label is honest. F-1 is closed as a labelling defect.
- **Realism test** (does every tier give what the business actually gives in that situation). Three of the restructured ladders fail it over a real part of their own domain. The flat tier and the proportional tier cross over, so the tier the business means to reward more (sooner, longer-tenured, prompter) gives a worse result than the lesser tier:
  - **prompt_request_treatment**: for any first-band forfeiture (1–30,000 miles; the band is inclusive, per the rule):
    - a request within 30 days pays $150;
    - a request 31–90 days after pays ceil(150×75%) = $113;
    - a later request pays $150.

    The "prompt" tier, which exists to reward prompt requests, gives no reduction at all to exactly those customers. It also selects the same fee as the fall-through, while a customer who waited longer is charged less. No airline publishes a prompt-request treatment that charges a prompt requester more than a later one.
  - **returning_member_qualifying_treatment**: for share qualifying dollars below $500 (a domestic Main Cabin segment under $500 of base fare), a segment flown within 90 days of the forfeiture earns floor(share×1.5), which is less than the share + $250 earned by a segment flown 91–365 days after. Example: share $300 gives $450 in the near tier against $550 in the far tier. The member who returns sooner is credited less.
  - **tenure_treatment**: for posted qualifying dollars below $2000, a member of 10 or more years counts floor(qd×1.1), which is less than qd + $200 for a member of 5–9 years. Example: $1000 gives $1100 against $1200. The longer-tenured member is counted lower.
- The other three restructured ladders pass. Their crossover lies outside the quantity's own domain:
  - late_posting: selection miles are only 20000/25000/30000 (charter `choice_bonus_miles_per_selection` for the eligible tiers), so ×1.25 always beats +1000.
  - distance: the largest shared co-pay is $75 (Member/Silver/Gold at 100%), so the long tier adds ceil(37.5) = 38, which stays at or below the very-long tier's $40.
  - repeat_buyer: 5% of at most $35 is at most $1.75, which is below $3.
- **Replacement factor departure_cabin_reduction**:
  - Every tier is stated in the rule and in compute.
  - The fall-through (a trip departing more than 21 days after the purchase) is reachable for customers in the policy's scope, whose trips are merely "upcoming".
  - Tiers 1 and 2 are conjunctions over two distinct records: the ticket's `next_departure_at` and the loyalty_upgrades request's `target_cabin`. **The factor is genuinely multi-source.**
  - The cabin part divides customers into First and Premium Economy. The time part divides them into near and far departures.
  - Values are distinct: 1.50 / 0.75 / 0.
  - Realism: a close-in top-up price concession for an imminent premium upgrade is a plausible published promotion, and the fall-through (no concession) is the ordinary price.
  - **F-2 is closed**: the old vacuous ladder is gone. **F-3 is closed** for task 1, which now has a multi-source factor under the definition's letter.
- **O-4 is closed**: the `club` and `pass` factors now carry `cross_difficulty: null`. The cross-difficulty factors are ticket and companion, and each task still has one.

### findings (revision 2)

- **F-1 — closed** as a labelling defect: all six method ladders now change the algorithm.
- **F-2 — closed**: replaced by departure_cabin_reduction, whose fall-through is reachable.
- **F-3 — closed**: departure_cabin_reduction is a conjunction over the ticket record and the upgrade-request record.
- **F-4 (new, introduced by the rework) — SOURCE-FACTOR RED: unreal ladders, with tiers that invert over their own domain.**
  - Affects prompt_request_treatment, returning_member_qualifying_treatment and tenure_treatment. All three are in task 0's computations; none is in task 1's.
  - Symptom: the arithmetic above. A prompter, sooner-returning or longer-tenured customer receives a worse result than the lesser tier. For first-band forfeitures, the prompt tier and the fall-through also select the same fee.
  - Root cause: each ladder was rebuilt by turning one proportional tier into a flat amount without bounding the crossover. The new flat tier beats the proportional tier over part of the quantity's range.
  - Evidence: the rule sentences quoted in the table above; the params prompt_far_share_percent 75, first_band_fee_usd 150, returning_near_multiplier 1.5, returning_far_bonus_usd 250, long_tenure_multiplier 1.1, mid_tenure_credit_usd 200; and the reinstatement band bounds 1–30000.
  - Consequence: each ladder carries a tier treatment that no loyalty business would publish for customers in that situation. That is the skill's "a tier's value or method … is a treatment that business would not publish for customers in that situation". For prompt_request_treatment, "no two tiers … select the same value" also fails for every first-band forfeiture.
  - Affected: loyalty.extended.yaml, the rule sentences and `factors[].ladder` of loyalty_ext_reinstatement_fee, loyalty_ext_retro_segment_qualifying_dollars and loyalty_ext_tier_requalification.
- **Observations**:
  - O-1, O-2, O-5, O-6 and O-7 stand, recorded with no change.
  - O-3 and O-4 are closed.
  - New observation O-8: `miles_short` has no `compute_basis` entry of its own (pre-existing; see rule_compute_equivalence).
  - New observation O-9: under distance_treatment, a Diamond or Chairman member (standard co-pay $0) pays the flat $40 on a very long segment and $0 on a long one. That is plausible as a flat surcharge, but it cuts into that tier's no-co-pay benefit.

### closing_checklist (revision 2)

Written after both round-2 reveals. The difficulty **still does not close**: task 0 is SOURCE-FACTOR RED on F-4, which the rework introduced; task 1 PASSES.

- Files: 0.md, 1.md and this file each carry revision_1 unchanged plus an appended revision_2.
- Coverage and exclusivity are unchanged: the two disjoint 4-policy scopes cover all 8 policies, and `charter_scope` agrees. Task tools, owners and uuid8s are unchanged; the tool bodies are identical, and only the docstrings were reworded.
- Trees are unchanged:
  - Each has 3 prerequisite problems and value_input edges at or above the floor (4 in task 0, 2 in task 1).
  - Each has an owner=user root.
  - The graph is acyclic, every edge is unmet at the opening, and every edge bears weight.
- Factors:
  - Round-1 F-1, F-2 and F-3 are closed.
  - Every factor bears weight against an honest baseline on its own world, and each all-baselines figure is definite and differs from gold.
  - Remaining: F-4. The prompt_request_treatment, returning_member_qualifying_treatment and tenure_treatment ladders invert over part of their domain (task 0).
- Unique solution: PASS on both tasks. The revision-2 GT matches the re-evaluation item for item.
- Gates: the coordinator re-ran them in round 2, all green. This audit ran none.

## revision_3

### charter_global_frozen (revision 3)

- Frozen from 2026-09-24T18:22Z. This section was written before any round-3 task JSON was opened.
- Inputs:
  - `loyalty.extended.yaml`: sha256 `ed24d40c8f5a21cfe3433c20ec8ebaed9f5e048726c233b5e7837ae305001b01`. Changed from round 2 (`237aee20…242e`), so the charter-global sections below are re-derived.
  - `task_tools.py`: sha256 `d7a4c54b…5e32`, unchanged since round 2. The revision-2 "action_binding_and_uuids" section is carried forward by reference on the strength of that unchanged hash.
  - Views: r3 task_0 is `97510caf…454d` and r3 task_1 is `228c6908…0f45`. Both are unchanged from r2, so the worlds and the persona are unchanged.
- Gate snapshot: all green in round 3 per the brief (traceability deferred). The input is complete.
- Base copy: still key-by-key equal to `blueprint/products/loyalty.yaml`.
- **contamination_disclosure** (two items):
  1. As in revision 2, I know the round-1 and round-2 GT of both tasks, and the worlds are unchanged. The revision-3 derivations are a mechanical re-evaluation of the new charter, not blind evidence.
  2. **An isolation breach, recorded honestly.** My helper scripts `t0.py` and `t1.py` lived in this session's scratchpad directory, which lies under `/tmp/claude-1000/-home-ubuntu-github-enterprise-rl/`. Between rounds, another agent's files with the same names overwrote them. When I re-ran them this round, they printed computations of a **different difficulty's** tasks: ticket-charter extended policies (change fee, bag charges, same-day change, seat refund, paid upgrade) with their evaluated values.
     - I did not open those files deliberately, and I did not use their output.
     - I re-ran all of my own evaluations inline, with no files, directly from this difficulty's charter and r3 views.
     - The output concerns another difficulty. It contains nothing about this difficulty's GT and does not affect any conclusion here. It is still a read outside my permitted domain, so I record it.

### policy_conflict_scan (revision 3)

- Only four factor ladders changed, plus one new `compute_basis` entry. The subjects, triggers, targets, prerequisite edges, eligibility, time anchors, terminal states and cross-category reads are unchanged from revision 2.
- Scopes: the same two disjoint 4-policy trees cover all 8 policies.
- No conflict.

### rule_compute_equivalence (revision 3)

- Scripted re-checks:
  - every `compute_basis` value is verbatim in its rule;
  - every `baseline.rule` sentence is in its rule;
  - every compute binding now has a `compute_basis` entry. `miles_short` quotes "The miles short are those costs added together less the membership's mile balance; when the balance covers them nothing is bought".
  - every `K()` key is declared and every declared param is used. New params: returning_near_minimum_usd 500, long_tenure_minimum_usd 250, prompt_near_fee_usd 50. first_band_fee_usd is still used by the band.
- The four rewritten rule sentences match their compute bindings:
  - QD: `MX(int(share×1.5), share+500)` / `share+250` / share
  - tenure: `MX(int(qd×1.1), qd+250)` / `qd+200` / qd
  - prompt: 50 / ceil(band×75%) / band
  - distance: `copay + MN(40, copay)` / ceil(copay×1.5) / copay
- **O-8 is closed.** O-1 stands, unchanged.

### prerequisite_graph and prerequisite_sentences (revision 3)

- Unchanged. The 7 edges keep their `policy_source` verbatim in the blocked rules (re-checked by script).
- The graph is acyclic, and each state-form edge still has a single writer (the tool bodies are unchanged).
- O-2, O-5 and O-7 stand, unchanged.

### override_declarations (revision 3)

- The overwrite entries are unchanged.
- The rewritten tiers change the replaced quantities only inside the already-declared overrides (QD, tier count, reinstatement fee, co-pay).
- No undeclared override.

### factor_ladders (revision 3)

The four rebuilt ladders:

| factor | tier 1 | tier 2 | fall-through |
|---|---|---|---|
| returning_member_qualifying_treatment | greater of floor(share×1.5) and share + $500 (0–90 days) | share + $250 (91–365) | share |
| tenure_treatment | greater of floor(qd×1.1) and qd + $250 (≥10 years) | qd + $200 (5–9 years) | qd |
| prompt_request_treatment | flat $50, band set aside (≤30 days) | ceil(band×75%) (31–90) | band |
| distance_treatment | copay + min($40, copay) (>2× threshold) | ceil(copay×1.5) (1×–2×) | copay |

**Ordering over the whole range.** Checked exhaustively:

- QD: every share from $0 to $10,000 in 1-cent steps gives tier 1 > tier 2 > fall-through, since tier 1 ≥ share+500 > share+250 > share. No inversion.
- Tenure: posted qualifying dollars from $0 to $50,000 give tier 1 ≥ qd+250 > qd+200 > qd. No inversion.
- Prompt: the three bands give 50 < 113 < 150, 50 < 188 < 250 and 50 < 300 < 400. The prompt tier is now always the cheapest, and it never equals the fall-through.
- Distance: every shared co-pay the charter can produce (copay 75/50/0 × share 50/75/100%, i.e. 0, 25, 37.5, 50, 56.25, 75) gives very-long ≥ long ≥ unchanged: 50 ≥ 38, 75 ≥ 57, 90 ≥ 75, 96.25 ≥ 85, 115 ≥ 113. At a shared co-pay of 0 (Diamond, Chairman) all three give 0, because the cap removes the round-2 $40 charge.
- **F-4 is closed.**

**Label honesty.**

- The "greater of" constructions (QD, tenure) combine a proportional and a flat amount in tier 1, a flat addition in tier 2, and the identity in the fall-through. Those are three distinct procedures, so the `method` label is honest. So are the prompt ladder (flat fee, percentage, unchanged) and the distance ladder (capped flat addition, scale, unchanged).
- On task 0's world the proportional branch is the one that binds (2692 against 2295; 3224 against 3181.75). The flat floor therefore never masquerades as a different quantity on the scored path.

**Realism.**

- A welcome-back uplift of "50% or at least $500", a long-tenure count of "10% or at least $250", a flat fast-track fee for requests within 30 days, and a long-haul surcharge capped at the co-pay are all publishable loyalty-programme treatments.
- Each ladder is now ordered in the direction the business intends: sooner, longer, prompter and longer-distance customers are treated accordingly.
- No tier's condition holds for every customer who reaches the write, and each fall-through is the ordinary treatment.

**O-9 is closed.** A zero-co-pay tier is no longer surcharged on a very-long segment. The change does not touch task 1: its segment is 1199 miles, in the long tier, and the charge is unchanged.

The other ladders (late posting, repeat buyer, departure-cabin, retro returning bonus, late issue) are byte-for-byte as in revision 2 and pass as recorded there.

### findings (revision 3)

- **F-4 — closed.**
- **O-8 and O-9 — closed.**
- O-1, O-2, O-5, O-6 and O-7 stand, unchanged.
- **New observation O-10.** When the prompt tier applies (a request within 30 days), the band is set aside, so on such a world the forfeiture_band factor cannot bear weight. This is inherent to a flat-fee tier. It does not bear on task 0, whose request is 69 days after the forfeiture.
- No new defect.

### closing_checklist (revision 3)

Written after both round-3 reveals. **Both tasks PASS on all four relationships, and the difficulty passes the source-layer audit.**

- **Files**: 0.md, 1.md and this file each carry revisions 1 and 2 unchanged, plus an appended revision_3. Every revision-3 comparison section carries a PASS.
- **Coverage and exclusivity**: the scopes {retro_credit_miles, retro_segment_qd, tier_requalification, reinstatement_fee} and {choice_bonus_miles, miles_upgrade_charge, choice_upgrade_certificates, upgrade_topup_purchase} are pairwise disjoint and together cover all 8 extended policies. Each scope spans its whole tree.
- **Task tools and GT are closed.** Each task tool keeps its independently generated, frozen uuid8 (03268362, d0ee7d28, 84e40849, d28241c8, 029b6e8c, 7f00044a, 458899d3, 4af9ade8).
- **Trees**:
  - Each has 3 prerequisite problems.
  - value_input edges: 4 in task 0 and 2 in task 1, against a floor of 2.
  - Each has an owner=user root (reinstate_expired_miles, buy_miles).
  - No cycle, either within a tree or across the difficulty's graph.
  - Every edge is unmet at frozen_time and bears weight.
- **Factors**:
  - Every computation declares a self-sufficient baseline and 4–6 factors, with at least 2 `parameter` and 1 honest `method`.
  - Every ladder has three disjoint tiers stated in full in its rule. The tiers are distinct in outcome, ordered where the business intends an order, and realistic in both condition and outcome.
  - Each task has at least 1 multi-source factor:
    - task 0: card_qualifying_bonus and returning_flyer_reduction
    - task 1: departure_cabin_reduction
  - Each task has at least 1 cross-difficulty factor (ticket and companion rows, seeded).
  - Every factor bears weight on its own world against an honest baseline, and each all-baselines figure is definite and differs from gold.
- **Unique solution**: PASS on both tasks. The GT matches the re-evaluation item for item.
- **Gates**: the coordinator re-ran this difficulty's instantiation-stage gates on the final form (round 3), all green with traceability deferred. This audit ran none, per the brief.
- **Observations still open** (none is grounds for rework): O-1, O-2, O-5, O-6, O-7, O-10; task 0 O-A, O-B, O-C; task 1 O-C, O-D.
- **Contamination record**: the revision-2 and revision-3 derivations are not blind, because the round-1 GT is known and the worlds are unchanged. Separately, the round-3 scratchpad collision exposed another difficulty's authoring computations. Both are disclosed above; neither changes a conclusion here.

## revision_4

### charter_global_frozen (revision 4)

- Frozen 2026-09-24T18:35Z, before any round-4 task JSON was opened.
- Inputs:
  - `loyalty.extended.yaml`: sha256 `ed24d40c…1b01`, unchanged since round 3.
  - `task_tools.py`: sha256 `d7a4c54b…5e32`, unchanged since round 2.
- Both shared inputs are byte-identical to the round that produced the current charter-global sections, so these are **carried forward by reference, not re-derived**, on the strength of those two hashes:
  - revision_3: policy_conflict_scan, rule_compute_equivalence, prerequisite_graph and prerequisite_sentences, override_declarations, factor_ladders, findings.
  - revision_2: action_binding_and_uuids.
- Views:
  - r4 task_0: `f952c6d3…3808`, changed. Handled in 0.md revision_4.
  - r4 task_1: `228c6908…0f45`, unchanged since r2.
- Gates: all green in round 4, plus `ID MERGE OK` (per the brief).
- Scratch discipline: all scratch work this round is confined to `/tmp/claude-1000/erl_coord_env0020/work/d3_auditor/` (isomorph.py, fk.py, eval_t0_r4.py, idmap_r3_r4.json). I did not use the shared session scratchpad.
- Cross-task identifier check within this difficulty: the r4 task_0 row ids and the task_1 row ids do not intersect (44 against task 1's ids; intersection empty).
- contamination_disclosure: unchanged from revision 3. I know the prior GT and did not use it; the round-3 scratchpad collision is already disclosed. There was no new contact this round.

### closing_checklist (revision 4)

Written after the round-4 reveal of task 0. **Both tasks PASS, and the difficulty still passes the source-layer audit.** The revision-3 checklist stands in full, with these round-4 confirmations:

- Task 0's world is a consistent, injective renaming of all 44 row ids. Rows, fields and values are identical, foreign keys are intact, and every proof field and GT argument references the new ids (0.md revision_4).
- The row ids of the two tasks do not intersect.
- The charter and tool hashes are unchanged, so every charter-global conclusion and every uuid8 of revision 3 holds as written.
- The coordinator re-ran the gates in round 4, all green, including ID MERGE OK. This audit ran none.
- Open observations are unchanged from revision 3.

## revision_5

### charter_global_frozen (revision 5)

- Frozen from 2026-09-24T19:45Z. This section was written before any round-5 task JSON was opened.
- Inputs:
  - `loyalty.extended.yaml`: sha256 `f6d1fca22c580a8f7b6d460e6a88340218ba76eb3f6ce46f5dbc9ea40d21b008`. Changed from round 4 (`ed24d40c…1b01`), so the charter-global sections below are re-derived. A copy of this revision is saved at `/tmp/claude-1000/erl_coord_env0020/work/d3_auditor/loyalty.extended.r5.yaml` for byte-level diffs in later rounds.
  - `task_tools.py`: `d7a4c54b…5e32`, unchanged since round 2. The revision-2 action_binding_and_uuids section is carried forward on that hash.
  - Views: r5 task_0 `f952c6d3…3808` and r5 task_1 `228c6908…0f45`, both unchanged since round 4.
- Also read, as the coordinator directed: the render agent's report `/tmp/claude-1000/erl_coord_env0020/slm/loyalty_render_r2_source_layer_miss.md` (SLM-1, SLM-2, SLM-3). It contains no task GT.
- Gates: all green in round 5, per the brief. The base copy is still key-by-key equal to `blueprint/products/loyalty.yaml`.
- Scratch: all scratch work is in `/tmp/claude-1000/erl_coord_env0020/work/d3_auditor/` (r5_checks.py, eval_t0_r5.py, eval_t1_r5.py).
- contamination_disclosure: unchanged. The prior GT is known and the worlds are unchanged, so this is a re-evaluation, not blind evidence. There was no new contact.

### What changed, and whether "compute, params and `when` are byte-identical" holds

- I kept no byte copy of the round-4 file, so I cannot byte-diff it. What I checked instead:
  - Every compute expression of the four touched policies is textually identical to the expressions recorded in revisions 1–3 (including `reduced_fee = MX(0, prompt_fee − returning − elite − card)`, `result = RND(reduced_fee + repeat_surcharge, 2)`, the charge `result = RND(MX(0, distance_copay − card − timing − lounge), 2)`, and the top-up `result = RND(miles/1000 × net × (100 − card% − pass%)/100, 2)`).
  - All params are the ones recorded in revision 3.
  - Every ladder `when` text matches revision 3.
  - Inline re-evaluation on both worlds reproduces every gold, sensitivity, all-baselines, skip and opening figure of revision 4, figure for figure.
- The changes are confined to rule sentences, `baseline.rule`, the ladder `value`/`method` texts, `compute_basis` quotations, and two overwrite entries.

### rule_compute_equivalence (revision 5), the SLM-1 closure check

Scripted checks (`r5_checks.py`):

- every `compute_basis` value is verbatim in its rule;
- every `baseline.rule` sentence is in its rule;
- every binding has a basis;
- every `K()` key is declared and every declared param is used.

I then compared the new wording, sentence by sentence, against the unchanged compute:

**loyalty_ext_reinstatement_fee**
- "The band fee follows the miles … set a band fee of … keep the band fee of first_band_fee_usd" matches `banded_fee`.
- The prompt-request treatment now "sets the fee to pay from the band fee, before any amount is taken off it or added to it". It is flat 50 / ceil(75% of the band fee) / band fee, which matches `prompt_fee`.
- Each of the three reductions "is taken off the fee to pay and never takes it below zero". This is a per-reduction floor, where compute has a single floor on the sum. The two are equal: every reduction is non-negative (30/60, 50/100, 20/40 or 0), so taking them off one at a time with a floor after each gives max(0, p − r₁ − r₂ − r₃) in any order. Once the fee reaches 0, a further non-negative subtraction keeps it at 0.
- The repeat surcharge "is added to the fee to pay once every amount taken off it has been taken off, and it is never itself reduced". That matches `result = reduced_fee + repeat_surcharge`.
- Result: equivalent.

**loyalty_ext_retro_segment_qualifying_dollars**
- The baseline now defines the share qualifying dollars: eligible fare × share %, rounded to the cent, with the share % at standard_qd_share_percent. That matches `share_qd`.
- "The standard qualifying-dollar posting is the share qualifying dollars, with no bonus added" gives 1436.00, equal to the all-baselines figure.
- The returning treatment "decides what the posting counts in place of the share qualifying dollars". That matches `treated_qd`.
- The route bonus is "a flat amount added to the qualifying dollars the segment posts". That matches `+ route_qd_bonus`.
- The card bonus is "a percent of the share qualifying dollars, rounded to the cent and added". That matches `RND(share_qd × pct/100, 2)` on the untreated share.
- The old sentence "never multiplied by it" is gone. The new wording carries the same content, because the card bonus is expressly a percent of the share and the route bonus is flat.
- Result: equivalent.

**loyalty_ext_miles_upgrade_charge**
- The baseline defines the shared co-pay as miles_upgrade_copay_usd × the share %, with the share % at standard_copay_share_percent, and the co-pay to charge as the shared co-pay. That gives 50.00, equal to the all-baselines figure.
- The distance treatment "sets the co-pay to charge from the shared co-pay, before any amount is taken off it", which matches `distance_copay`.
- The per-reduction floors equal the single `MX(0, …)`, by the same non-negativity argument as the reinstatement fee.
- Result: equivalent, with one wording regression recorded as observation O-11 below.

**loyalty_ext_upgrade_topup_purchase**
- The baseline defines the tier price as miles_purchase_price_per_1000_usd, the net price as the tier price, and the price as miles bought in thousands × net price, rounded to the cent. That gives 700.00, equal to the all-baselines figure.
- The repeat-buyer treatment "sets the net price per thousand from the tier price per thousand, before any amount per thousand is taken off it", which matches `buyer_price`.
- The lounge and departure-cabin reductions are "taken off the net price per thousand", which matches `net_price_per_1000`.
- The card and subscription percentages are "added together and taken off the price once, before the price is rounded to the cent", which matches `(100 − card − pass)/100` inside the single `RND`.
- Result: equivalent.

Summary: every new base and assembly statement agrees exactly with the unchanged compute. **SLM-1 is closed at the source layer.** Each factor sentence now names the amount it acts on and when it applies, and each `baseline.rule` defines every intermediate the ladders act on (share qualifying dollars, shared co-pay, band fee, tier price per thousand). Honesty of the baselines: `baseline.rule` alone gives 1436.00, 150.00, 50.00 and 700.00. Each is definite and equals the all-baselines compute figure. None equals gold.

**O-11 (new observation; not RED).** The distance tier-1 wording in the rule changed:
- Round 3: "has the flat very_long_surcharge_usd, capped at the shared co-pay itself, added to its shared co-pay". The cap unambiguously applies to the surcharge.
- Round 5: "sets it at the shared co-pay plus the flat very_long_surcharge_usd, capped at the shared co-pay itself".

With the comma, "capped at the shared co-pay itself" can attach to the whole sum. That second reading gives s, making tier 1 equal to the fall-through. Compute (`s + MN(40, s)`) and the ladder method text ("plus the flat very_long_surcharge_usd capped at the shared co-pay") both support the first reading, and the second reading makes the tier pointless. No task world sits on the very-long tier (task 1 is at 1199 miles, the long tier), so no scored value depends on it. I record it as a wording regression without a demonstrable consequence.

### override_declarations (revision 5), the SLM-2 closure check

**QD re-target**
- `loyalty_ext_retro_segment_qualifying_dollars.overwrite[0]` no longer retires loyalty_flight_earning's qualifying-dollar sentence. It now retires loyalty_retro_credit_claims' "The retro credit earns exactly what the flight would have earned on its flight_date under the flight-earning rule, at the tier held on that date". That clause is verbatim in the base rule, and loyalty_retro_credit_claims is in this policy's `base_policy_refs`.
- The replacement is "The qualifying dollars a retro-credited segment posts, in place of what the flight would have earned, are worked from its share qualifying dollars by the rules below and rounded to the cent". It is a rule sentence.
- Legality: loyalty_ext_retro_credit_miles still retires the same clause for the miles. The clause governs both quantities a retro claim earns (base loyalty_retro_credit_claims has subject loyalty_retro_credit and loyalty_mqd_accrual): miles through the retro-miles replacement, qualifying dollars through this replacement. The two replacements settle disjoint quantities, so the merged semantics are unique.
- Coverage: together the two replacements cover everything the retired clause covered. "at the tier held on that date" bears only on miles, and the retro-miles replacement covers it.
- The flight-earning qualifying-dollar sentence is now inherited unchanged. It governs flown coupons "on a ticket that names the membership", so it cannot reach a retro-credited segment, whose ticket names none. There is no residual conflict.
- The base retro-claims clause on prior-year flights ("posts qualifying dollars to the current calendar year only when the flight_date falls in the current calendar year") is still inherited, as before.
- The scope of the retirement now equals the scope of the replacement. **Closed.**

**Top-up**
- `loyalty_ext_upgrade_topup_purchase.overwrite[0]` still retires "at miles_purchase_price_per_1000_usd for each thousand miles". Its replacement now reads "A top-up purchase is priced from the miles bought and the net price per thousand by the rules below and rounded to the cent, and a purchase that covers no waitlisted miles upgrade is priced at miles_purchase_price_per_1000_usd for each thousand miles, outside this rule". It is a rule sentence.
- Every purchase the retired clause priced is now priced by the replacement: top-ups by the rules, all other purchases at the base price. The coverage is complete, and the non-top-up price is unchanged.
- The replacement is consistent with the seeded historical purchase in task 1 (2d286b69: 5000 miles for 175.00 at 35 per 1000). **Closed.**

**SLM-3**: the base `parameter_schema` description is frozen base text. It must stay verbatim, and the base copy is equal to the blueprint. It is logged as known and has no source-layer consequence here.

**Result**: no undeclared override. Each overwrite names a verbatim base clause of a referenced policy, and each replacement is a rule sentence.

### prerequisite_graph and prerequisite_sentences (revision 5)

- All 7 `policy_source` sentences are byte-identical to the verbatim sentences recorded in revision 1, and each is still in its blocked rule.
- Edges, kinds, forms, conditions and `resolved_by` are unchanged. The graph is acyclic, and each edge still has a single writer.
- No other rule sentence acquired an ordering between problems. The new "before any amount is taken off it" and "once every amount taken off it has been taken off" phrases order steps within one policy's own computation, not between problems.
- **No prerequisite sentence changed.**

### policy_conflict_scan (revision 5)

- Subjects, triggers, targets, eligibility, time anchors, terminal states and cross-category reads are unchanged.
- Scopes are unchanged: two disjoint 4-policy trees covering all 8 policies.
- No conflict.

### factor_ladders (revision 5)

- `when` conditions, compute and params are unchanged. The tiers, their outcomes, the ordering proofs of revision 3, the method-label honesty, the multi-source structure and the cross-difficulty reads are therefore unchanged.
- The rewritten `value`/`method` texts name the same outcomes as compute, and now also the amount each acts on:
  - "a band fee of …"
  - "taken off the fee to pay, never taking it below zero"
  - "added … once every amount taken off it has been taken off"
  - "a qualifying share percent of …"
  - "a tier price per thousand of …"
  - "percent of the price, added to every other percentage discount and taken off the price once, before rounding to the cent"
- No tier's realism, label or weight moved (see the task files).
- Observation O-10 stands. O-11 is new. O-12 is new: two extended policies now name the same base clause in `overwrite`. That is legal here because they replace disjoint quantities, and I record it only for the KB render.

### findings (revision 5)

- SLM-1: closed. SLM-2: closed on both overwrites. SLM-3: known, frozen base text.
- No new defect.
- New observations: O-11 (the distance tier-1 cap wording can be read two ways; no task consequence) and O-12 (a shared superseded clause).
- O-1, O-2, O-5, O-6, O-7 and O-10 stand.

### closing_checklist (revision 5)

Written after both round-5 reveals. **Both tasks PASS, and the difficulty still passes the source-layer audit.**

- SLM-1 is closed: every base and assembly statement agrees with the unchanged compute, including per-reduction floors against a single floor on a sum of non-negative reductions.
- SLM-2 is closed on both overwrites: the QD overwrite re-target is legal and fully covered, and the top-up replacement covers every purchase. SLM-3 is known, frozen base text.
- No prerequisite sentence changed. No factor's tier, label, realism or weight changed, and every factor still bears weight against an honest baseline, whose text now gives the all-baselines figure on its own.
- Scopes, trees, tools, uuid8s and the id consistency of revision 4 are unchanged.
- The coordinator re-ran the gates in round 5, all green. This audit ran none.
- Open observations (none is grounds for rework):
  - charter: O-1, O-2, O-5, O-6, O-7, O-10, **O-11**, **O-12**
  - task 0: O-A, O-B, O-C, **O-D**
  - task 1: O-C, O-D
