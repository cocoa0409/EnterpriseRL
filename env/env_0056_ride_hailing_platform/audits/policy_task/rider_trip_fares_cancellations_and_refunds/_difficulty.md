# Policy-task audit — rider_trip_fares_cancellations_and_refunds / charter-global

## charter_global_frozen

- Freeze time: 2026-10-11T11:50Z (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Auditor: erl-task-policy-audit subagent (claude-opus-5-5), independent of the instantiating agent.
- Frozen inputs (sha256 re-computed by the auditor, equal to the brief and to `.audit_views/policy_task/rider_trip_fares_cancellations_and_refunds/HASHES.txt`):
  - `tasks/rider_trip_fares_cancellations_and_refunds/trip.extended.yaml` e795ec199e8d54d725606739867a1ff7a1833f5c99488361ce85340d75a30cc5
  - `tasks/rider_trip_fares_cancellations_and_refunds/task_tools.py` 7643ac5fcd6995e8f1637056b2a98dc4eafc275598307820eb8adaee4b152522
  - views `0.view.json` f4b270c2…a9dd, `1.view.json` ca698cef…755d (match).
- Read: `blueprint/blueprint.yaml`, `blueprint/products/{trip,pass,bike,damage}.yaml` (parameters / event meanings only), `blueprint/share_tools.py`, the extended charter, `task_tools.py`, the two masked views. Not read: `tasks/*.json`, any other scenario, any sibling difficulty's tasks directory. The DSL helpers (`MONTHS`, `DAYS`, `XSUM`, `XCOUNT`, `CFIELD`, `CPARAM`) were read at their documented meaning; their implementation outside `erlbench/` was not opened.
- Masked until every task's derivation was frozen: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`.
- Entry conditions (Step 0): gate snapshot supplied with commands and last lines (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; traceability deferred to render). Masked views and hashes supplied. Entry conditions met.
- Base copy: lines 1–1328 of the extended charter equal `blueprint/products/trip.yaml` byte for byte except one trailing blank line (`diff` shows only `1328d1327 <` empty line). Verbatim.

Policy shorthand used below:

| Id | Policy | target_tool (owner) | computes | prerequisite |
|---|---|---|---|---|
| P1 | trip_ext_upfront_guarantee_correction | adjust_fare_above_guarantee_d9a21c99 (agent) | adjustment_amount | [] |
| P2 | trip_ext_dropoff_review_request | submit_dropoff_fare_review_f18c58a7 (user) | requested_amount | P1 (value_input, state) |
| P3 | trip_ext_detour_toll_return | apply_detour_toll_return_b5bdaa70 (agent) | offset_amount | [] |
| P4 | trip_ext_detour_fare_offset | book_detour_fare_offset_50a7c54a (agent) | offset_amount | [] |
| P5 | trip_ext_detour_delay_referral | refer_detour_delay_review_b094ef4b (agent) | requested_amount | [] |
| P6 | trip_ext_unpaid_fare_payment | pay_unpaid_fare_new_card_1dc475f0 (user) | payment_amount | P3, P4, P5 (all value_input, state) |

### policy_conflict_scan

- Subjects/triggers. P1 (state_due, fare charge with basis upfront standing above the guaranteed fare) and P2 (on_request, wrong drop-off claim) both act on a trip's fare charge; P1 writes a fare adjustment, P2 a fare review; no shared target. P3/P4 (state_due) both write a refund-offset settlement against the same unpaid fare charge, distinguished by reason (toll not incurred / route inefficiency); P5 (state_due) writes a route-inefficiency fare review; P6 (on_request) writes a new-payment-method settlement. Trigger regions of {P1,P2} (fare basis upfront) and {P3,P4,P5} (fare basis recalculated, no rider route change) are disjoint by fare_basis.
- Eligibility/time anchors. Every adjustment/refund inherits base `within_review_window` (30 calendar days from the charge date for every option) and `within_support_limit`. P1 says so explicitly ("The correction counts toward the support limit of the trip like every other adjustment or refund"); P3/P4 write settlement rows, which the base measure `trip_msr_trip_support_returned` ("Absolute sum of trip_fare_adjustment and trip_refund amounts on that trip_id") does not count — see finding G-2.
- Shared balance. P3 and P4 both reduce the unpaid amount of one fare charge; P4's result is capped at "the unpaid amount left on the fare charge", P3's at the toll. Neither rule fixes the P3/P4 order. When the P4 cap does not bind, the two orders give the same terminal state (checked per task).
- Cross-category read boundaries. Reads of pass (memberships, pass_events fee charges), bike (bike_plans status, bike_rides ride charges) and damage (damage_events fee charges) are reads only; no extended policy writes outside trip_charges / trip_fare_reviews / trips.
- Overwrite collisions. The base clause "An outstanding charge is settled in full by one trip_balance_settlement row for that charge" is superseded twice (P3 and P6) with two different, scope-disjoint replacements (toll return; rider payment). Compatible in scope; recorded as observation G-O3.
- Scope partition. The six extended policies split into two trees: {P1 ← P2} and {P3, P4, P5 ← P6}. With task 0 = Celeste Bramwell wrong drop-off (root P2) and task 1 = Owen Dabrowski unpaid fare (root P6), as read from the views' `user_scenario` (not from `charter_scope`), the scopes are pairwise disjoint and jointly cover all six extended policies.

### rule_compute_equivalence

Sentence-by-sentence sweep, every compute binding against `compute_basis` and back.

- P1. `fare_charged`, `fare_adjusted_before`, `recorded_member_discount`, `guarantee_discount` (RND of pct/100 × (upfront − booking fee)), `guaranteed_fare`, `makegood_rate`, `makegood_cap`, `repeat_error_multiplier`, `timeliness_factor`, `billing_error_makegood` (MN(product, cap), unrounded), `result` (RND(MN(excess + make-good, fare − adjustments))) each have a verbatim quotation and match. Two invented details: (a) `billed_above_guarantee` wraps the excess in `MX(0, …)`; no rule sentence states a zero floor on "the fare charge amount, less the fare adjustments already booked on the trip, less the guaranteed fare" (observation G-O1; never binding in task 0, which has no prior fare adjustment); (b) `membership_fees_last_year` = `XSUM('pass','pass_events', …)` over all of the customer's Pass ledger, while the rule says fee charges "booked [on] a membership" (the membership whose enrolment date is tested); identical when the rider holds one membership (both tasks) — observation G-O1.
- P2. All bindings quoted and implemented; "fare still standing" = fare charge − fare adjustments; the cap and the luggage/onward terms are as stated. No invented basis.
- P3. All bindings quoted; ratio = actual/estimated miles; tenure via MONTHS(enrolled, today); toll timeliness from the toll charge date; fee history = damage_fee_charge count in 12 months by event_date; result = RND(MN(toll × share × tenure × timeliness × fee-history + allowance, toll)). Matches.
- P4. All bindings quoted; `honoured_quote` three branches as stated; `booking_fee_return` tier 2 "otherwise" implemented as `not tier1`; `result` = RND(MN(fare − quote + MN(credits, cap), unpaid)). Matches.
- P5. All bindings quoted; matches.
- P6. Bindings quoted. **The `held_out` sentence admits two parses** (finding G-3): rule "the amount under a submitted route-inefficiency fare review on the trip multiplied by the hold-out share plus the multimodal hold-out uplift, then by the hold-out timing factor" is implemented as `(holdout_share + multimodal_holdout_uplift) * under_review * holdout_timing`, but the same charter uses "multiplied by …, plus the X" for an additive dollar term elsewhere (P2 "… then by the review timeliness factor, plus the onward-journey reimbursement and the luggage allowance"; P3 "… then by the fee-history factor, plus the fare-size allowance", where `fare_allowance_mid: 0.20` is dollars), and the baseline calls the uplift "nil", the word the charter uses for nil dollar amounts. The uplift parameters (0.25 / 0.10) carry no unit.
- Baseline rules: every sentence of every `baseline.rule` is a sentence of its policy's `rule` (checked mechanically, whitespace-normalised), and `baseline.params` names the standard keys each baseline sentence uses.
- Ladders: every tier each `factors[].ladder` names is stated in the rule and is a branch of its `decides` binding, and vice versa; no tier lives only in `compute`.

### action_binding_and_uuids

- (target_tool, computes) pairs are unique per policy (six policies, six tools).
- `subject` labels: P2 and P5 declare `subject: [trip_fare_adjustment]` while their tools write `trip_fare_reviews` rows (observation G-O4; no second business reading arises because the tool and the rule both say "fare review").
- Docstrings: no docstring names another tool, states a position in a sequence or uses before/after/first. The module docstring says amounts are "worked out beforehand" and "No tool checks eligibility, prerequisites or amounts" — not a cross-tool order (no finding).
- Tool bodies: each performs one create (+ one trips update where stated); none tests a prerequisite, an amount, a status or a balance (lines 42–58, 87–97, 130–146, 178–194, 222–231, 261–276).
- uuid8s: d9a21c99, f18c58a7, b5bdaa70, 50a7c54a, b094ef4b, 1dc475f0 — pairwise distinct, no shared prefix or suffix, no sequence, no adjacency. Pass.

### prerequisite_graph

- `prerequisite` present on all six (`[]` on P1, P3, P4, P5). Every `problem` is an extended policy id of this file, none a base policy, none self. Graph edges P2→P1, P6→P3, P6→P4, P6→P5: acyclic.
- `policy_source` of all four edges is verbatim (whitespace-normalised) in the blocked policy's own `rule` (checked mechanically).
- `form: state` on all four; no `fallback_reason`; correct.
- `gate`: `fare_still_standing` (P2 compute), `unpaid_left` ×2 and `under_review` (P6 compute) exist; `kind: value_input` matches each (each gate is a binding feeding the result).
- `resolved_by` equals the depended-on policy's `target_tool` on all four, and each such write changes the gate binding (P1 adds a trip_fare_adjustment → lowers `fare_still_standing`; P3/P4 add trip_balance_settlement rows → lower `unpaid_left`; P5 adds a submitted route_inefficiency review → raises `under_review`).
- `condition` texts restate the sentences at the same strength; no authoring-viewpoint wording ("this task", "opening").
- Pass.

### prerequisite_sentences

| Edge | Sentence (blocked rule) | Connective | Waited-on state (record words) | Writers of that state in this difficulty |
|---|---|---|---|---|
| P2→P1 | "The wrong drop-off review amount is fixed only after the trip's fare charge carries a fare adjustment entry for every part of it billed above the guaranteed fare." | only after | a fare adjustment entry on the fare charge | only `adjust_fare_above_guarantee_d9a21c99` writes `trip_fare_adjustment` |
| P6→P3 | "A payment toward an unpaid fare is not taken until the fare charge carries a refund-offset settlement entry giving toll not incurred as its reason wherever a toll was charged on a trip whose fare was recalculated without any rider route change." | not … until | refund_offset settlement, reason toll_not_incurred | only `apply_detour_toll_return_b5bdaa70` |
| P6→P4 | "The unpaid-fare payment amount is fixed only after a fare recalculated without any rider route change carries a refund-offset settlement entry giving route inefficiency as its reason." | only after | refund_offset settlement, reason route_inefficiency | only `book_detour_fare_offset_50a7c54a` |
| P6→P5 | "The unpaid-fare payment amount is not fixed before any detour delay on a trip whose fare was recalculated without a rider route change stands as a submitted fare review giving route inefficiency as its reason." | not … before | submitted fare review, reason route_inefficiency | only `refer_detour_delay_review_b094ef4b` (`submit_dropoff_fare_review_f18c58a7` writes reason wrong_dropoff_location) |

- Four-point test: ordering connective present; state named in record words without tool, performer, policy id, snake_case or row id; strength matches `condition` (P2: "every part … billed above the guaranteed fare" = closed condition, vacuous when nothing is above; P6: "wherever a toll was charged on a trip whose fare was recalculated without any rider route change" matches P3's own scope; "a fare recalculated without any rider route change" matches P4's scope since under `trip_evt_fare` such a recalculation can only come from a miles/minutes overrun; "any detour delay" matches P5's minutes-overrun scope). Pass.
- Derivations (sentence + records + depended-on rule → one resolving action): P2's sentence uses "the guaranteed fare", a term only P1's rule defines ("The guaranteed fare is the trip's upfront fare less the guarantee discount"), and only P1 books fare adjustments → book the P1 correction. P6's three sentences each name an entry kind + reason that exactly one policy's rule books (P3 "booked as a refund-offset settlement entry … giving toll not incurred as its reason"; P4 "… giving route inefficiency as its reason"; P5 "refers the detour delay … as a fare review … giving route inefficiency as its reason"). Single reading each.
- Depended-on rules (P1, P3, P4, P5) do not restate the sentences. No rule states an undeclared cross-problem order: P6's "stays unpaid … until the fare review team decides it" waits on an external decision, not on a problem of this difficulty. Pass.

### override_declarations

Sentence-by-sentence over each `base_policy_refs` entry.

- P1 vs `trip_evt_adjustments_and_refunds`: S1 (names single charge) followed; S2–S3 (review window) inherited; S4 fare_above_upfront clause **declared** superseded (replacement = P1's correction formula, verbatim in rule); route_inefficiency / wait_time_not_incurred untouched; S5–S6 (whole-charge refunds; cap on one charge) followed — result ≤ fare − adjustments; S7 support limit followed explicitly; S8 payment-method followed; S9 followed. vs `trip_evt_fare`: the discount sentence is the basis of P1's recomputed guarantee discount (5% × fare excl. booking fee) — follows. Declared, merged meaning unique.
- P2 vs `trip_evt_adjustments_and_refunds` (`overwrite: []`): base "any wrong drop-off location claim, is sent to the fare review team as a fare review for the disputed charge instead of being adjusted" — P2 follows (review filed by the rider; amount added by P2 only). No conflict.
- P3 vs `trip_evt_airport_and_tolls`: the superseded clause is the toll **charging** rule ("A toll is charged once per toll facility crossed between pickup and drop-off …"), but its replacement speaks only of detoured trips; read literally the merged text no longer states how tolls are charged on any other trip, and the base S5 "A toll or airport fee charged when the conditions above do not hold is refunded in full" is left pointing at removed conditions (observation G-O2 — no task world here turns on it). vs `trip_agg_outstanding_balance_hold`: "settled in full by one … row" declared superseded (partial refund-offset). **Undeclared:** P3 books its partial return under reason `toll_not_incurred`, which base `trip_evt_adjustments_and_refunds` (not in P3's refs) defines as a whole-charge `trip_refund` that "equals the charge less anything already returned on it". The two texts disagree on what a toll_not_incurred return amounts to. P3's own formula is more specific, so a reader computes P3's amount; recorded as observation G-O2 (consequence only as a weak second reading, see task 1).
- P4 vs `trip_evt_adjustments_and_refunds`: route_inefficiency clause declared superseded; vs `trip_agg_outstanding_balance_hold`: refund_offset clause declared superseded ("no fare adjustment entry is written"). **Not declared:** the base support-limit sentence S7 ("Support may return up to agent_adjustment_limit in total per trip (trip_msr_trip_support_returned); a request that would take the trip above it … is sent to the fare review team as a fare review for the disputed charge instead of being adjusted"). In base, a route-inefficiency return on an outstanding charge is a fare adjustment (counted by the limit) plus a refund_offset settlement; P4 replaces it with a settlement-only entry, which the measure does not count. That takes route-inefficiency corrections out of the support limit without naming S7 — the "anonymous intermediate" disguised override (finding G-2). Also a dropped branch: with the route_inefficiency clause superseded globally, the charter no longer states how a route-inefficiency correction on a **collected** fare is booked (observation G-O2; no task here has one).
- P5 vs `trip_evt_adjustments_and_refunds` (`overwrite: []`): adds a fare review referral; base S9 ("A rider who did not like the route … gets no adjustment") is not touched (the driver lengthened the route; the rider's preference is not the basis). No conflict.
- P6 vs `trip_agg_outstanding_balance_hold`: hold sentence declared superseded (held-out amount under a submitted review does not block); "settled in full by one row" declared superseded; new_payment_method clause followed. Declared, unique.

### factor_ladders

| Policy | Factor | Label | Ladder values (tier1 / tier2 / fall-through) | Multi-source? | cross_difficulty | Structural verdict |
|---|---|---|---|---|---|---|
| P1 | guarantee_discount_by_plan | parameter | pct×(upfront−bf) / **pct×(upfront−bf)** / recorded | yes (pass membership + trip option) | pass | **RED G-1a**: tiers 1 and 2 select the identical value expression (rule: "on a Wayfare Pass Plus Monthly or … Plus Annual membership it is **likewise** the plan's member discount percent of the upfront fare less the booking fee"); merging them changes nothing on any world (Student/Monthly/Annual have 0% and empty options and fall through either way). Real tiers: 2 (< 3). Also its tiers change how the discount is obtained (recomputed vs recorded) — a method under a `parameter` label. |
| P1 | makegood_rate_by_member_standing | parameter | 0.10 / 0.05 / 0.02 | yes (enrolled_date + pass_events fees) | pass | ok |
| P1 | makegood_cap_by_fare_size | parameter | 12 / 7 / 4 | no | — | ok |
| P1 | repeat_error_multiplier | method | ×2.0 / ×1.5 / ×1.0 | no | — | **RED G-1b** mislabelled: `K('repeat_multiplier_two') if … else K(…)` substitutes a number into an unchanged product |
| P1 | makegood_timeliness | parameter | 0.5 / 0.75 / 1.0 | no | — | ok |
| P2 | stranding_share | parameter | 0.45 / 0.30 / 0.20 | yes (trip miles + bike rides) | bike* | ok |
| P2 | member_review_multiplier | method | ×1.3 / ×1.15 / ×1.0 | no (one membership row) | pass | **RED G-1b** mislabelled (number into same product) |
| P2 | review_request_cap | parameter | 60 / 35 / 25 | no | — | ok |
| P2 | onward_journey_share | parameter | 1.0 / 0.5 / 0.0 | no | bike* | ok |
| P2 | luggage_allowance | parameter | 5.00 / 2.50 / 0 | yes (airport fee entry + trip airport_leg) | — | ok |
| P2 | review_timeliness | parameter | 0.7 / 0.85 / 1.0 | no | — | ok |
| P3 | detour_toll_share | parameter | 0.8 / 0.5 / 0.25 | declared yes, but see verdict | — | **RED G-1c**: the "a toll entry on the trip" part of tiers 1–2 holds of every customer who reaches this write (rule: "A trip with no toll charge … gets no detour toll return"); struck, the ladder is a single-source miles ratio |
| P3 | member_tenure_multiplier | method | ×1.15 / ×1.05 / ×1.0 | no | pass | **RED G-1b** mislabelled |
| P3 | toll_timeliness | parameter | 0.6 / 0.85 / 1.0 | no | — | ok |
| P3 | fee_history_factor | parameter | 0.7 / 0.9 / 1.0 | no | damage | ok structurally; business reality doubtful (G-O5) |
| P3 | fare_size_allowance | parameter | +0.40 / +0.20 / 0 | no | — | ok |
| P4 | honoured_quote_basis | method | upfront − plan discount on upfront / upfront / upfront − recorded | yes (membership status/options + fare-charge recorded discount) | pass | ok — genuine method |
| P4 | booking_fee_return | parameter | bf×1.0 / bf×0.5 / 0 | yes (trip minutes + fare charge) | — | ok |
| P4 | member_detour_credit | parameter | 2.00 / 1.00 / 0 | yes (membership status + pass_events fees) | pass | ok |
| P4 | multimodal_detour_credit | parameter | 1.50 / 0.75 / 0 | yes (bike plan status + bike rides) | bike* | ok structurally; business reality doubtful (G-O5) |
| P4 | detour_credit_cap | parameter | 8 / 4 / 2 | no | — | ok |
| P5 | delay_grace_minutes | parameter | 0 / 5 / 10 | no (one membership row) | pass | ok |
| P5 | delay_rate_multiplier | method | ×2.0 / ×1.5 / ×1.0 | declared via recalculated + minutes + miles | — | **RED G-1b** mislabelled; **RED G-1c** the "recalculated fare charge" part of both tiers holds of every customer reaching this write (rule: "A trip … whose fare stood at the upfront fare … has no detour delay to refer") |
| P5 | referral_timeliness | parameter | 0.7 / 0.9 / 1.0 | no | — | ok |
| P5 | referral_fee_history | parameter | 0.6 / 0.85 / 1.0 | no | damage | ok structurally; business reality doubtful (G-O5) |
| P5 | referral_cap | parameter | 20 / 12 / 6 | no | — | ok |
| P6 | holdout_share | method | 1.0 / 0.5 / 0.0 | yes (membership status + damage fees) | damage | **RED G-1b** mislabelled (share constant into the same product `(share + uplift) × under_review × timing`) |
| P6 | multimodal_holdout_uplift | parameter | 0.25 / 0.10 / 0 | yes (bike plan status + bike rides) | bike* | ok structurally; unit ambiguous (G-3); business reality doubtful (G-O5) |
| P6 | holdout_timing | parameter | 1.0 / 0.75 / 0.5 | no | — | ok |
| P6 | holdout_cap | parameter | 15 / 8 / 3 | no | — | ok |

\* `bike` is not a category any difficulty of this scenario claims (blueprint difficulties: trip, pass, damage, earnings, driver); these factors read another product's records but not another difficulty's (observation G-O6). Every task still has pass or damage factors.

Counts after the tests (factors 4–6 each; ≥2 parameter; ≥1 honest method):

| Policy | Declared (param/method) | Honest method after tests | Result |
|---|---|---|---|
| P1 | 5 (4/1) | 0 (repeat multiplier is a number; guarantee discount is a method-in-effect but a 2-tier ladder) | **RED** |
| P2 | 6 (5/1) | 0 | **RED** |
| P3 | 5 (4/1) | 0 | **RED** |
| P4 | 5 (4/1) | 1 (honoured_quote_basis) | pass |
| P5 | 5 (4/1) | 0 | **RED** |
| P6 | 4 (3/1) | 0 | **RED** |

All fall-through tiers equal their `baseline`; every baseline is the standard value the `baseline.rule` names (honest by construction — per-world weight in each task file).

### findings

- **G-1 SOURCE-FACTOR RED (bears on tasks 0 and 1).**
  - G-1a. Symptom: P1 `guarantee_discount_by_plan` ladder has two tiers selecting the same value. Root cause: All Access and Plus tiers both select "the plan's member discount percent of the upfront fare less the booking fee"; the differing percentages come from the plan parameter, not from the tier. Evidence: `trip.extended.yaml` P1 rule sentence 7 ("…it is likewise the plan's member discount percent…"), `factors[0].ladder[0].value` = `ladder[1].value` word for word; compute line `guarantee_discount` repeats the same expression in both branches. Consequence: the ladder has two real tiers, below the three-tier floor. Affected: P1 `factors[guarantee_discount_by_plan]`, rule sentence 7, compute `guarantee_discount`.
  - G-1b. Symptom: factors labelled `method` only substitute a constant into an unchanged product. Root cause/evidence: P1 `repeat_error_multiplier` (`K('repeat_multiplier_two'|'one'|'standard')`), P2 `member_review_multiplier` (`K('member_mult_*')`), P3 `member_tenure_multiplier` (`K('tenure_mult_*')`), P5 `delay_rate_multiplier` (`K('delay_mult_*')`), P6 `holdout_share` (`K('holdout_share_*')`); each enters the result as a multiplicand of the same expression. Consequence: P1, P2, P3, P5, P6 each have zero honest `method` factors (required ≥1). Affected: the five `factors[].effect` labels and the policies' factor sets.
  - G-1c. Symptom: a part of a compound tier condition holds of every customer who reaches the write. Evidence: P3 `detour_toll_share` tiers "a toll entry on the trip and …" vs P3 rule "A trip with no toll charge … gets no detour toll return"; P5 `delay_rate_multiplier` tiers "recalculated fare charge with …" vs P5 rule "A trip … whose fare stood at the upfront fare … has no detour delay to refer". Consequence: these parts restate scope; P3's factor is single-source once struck (its multi-source claim does not hold); P5's is single-record (trip minutes and miles). Affected: P3/P5 ladders and compute `detour_toll_share`, `delay_rate_multiplier`.
- **G-2 SOURCE-POLICY RED (bears on task 1).** Symptom: P4 books a route-inefficiency correction above the ride option's per-trip support limit with no fare review. Root cause: P4's overwrite turns the base route-inefficiency **fare adjustment** on an outstanding charge into a settlement-only entry ("no fare adjustment entry is written"); the base support-limit sentence of `trip_evt_adjustments_and_refunds` (in P4's own `base_policy_refs`) is not named in `overwrite`, yet the measure it rests on counts only fare adjustment and refund entries. So the limit stops applying to these corrections without being declared. Contrast P1, which says "The correction counts toward the support limit of the trip like every other adjustment or refund". Evidence: base lines 1214 and 817 (measure definition); P4 overwrite[1] `replaced_by`; Comfort `agent_adjustment_limit: 25.00` (base line 300). Consequence demonstrated in `1.md` (P4 = 29.33 > 25.00). Affected: P4 `overwrite`, rule sentence 2; base `trip_evt_adjustments_and_refunds` S7.
- **G-3 SOURCE-POLICY RED (bears on task 1).** Symptom: P6's held-out amount sentence has two parses. Root cause: "multiplied by the hold-out share plus the multimodal hold-out uplift, then by the hold-out timing factor" reads either as `(share + uplift) × amount × timing` (compute) or as `(amount × share + uplift) × timing`; the charter's own idiom ("…then by X, plus the Y allowance", "is nil", the 0.20/0.40 dollar `fare_allowance_*` params of P3) supports the additive-dollar reading, and the uplift params carry no unit. Evidence: P6 rule sentence 9 and baseline sentence 4; P2 rule sentence 3; P3 rule sentence 4 and params. Consequence demonstrated in `1.md` (11.72 vs 14.25). Affected: P6 rule sentence 9 / compute `held_out` / factor `multimodal_holdout_uplift`.

Observations (no demonstrated consequence in this difficulty's worlds):

- G-O1. P1 compute invents a zero floor on the excess (`MX(0, …)`) and sums Pass fee charges customer-wide where the rule speaks of the tested membership.
- G-O2. P3's superseded clause is the general toll-charging rule, replaced by a detour-only sentence (merged text loses the toll-charging rule for other trips; base "the conditions above" dangles). P3 reuses reason `toll_not_incurred` for a partial settlement while base `trip_evt_adjustments_and_refunds` (not in P3's refs) defines it as a whole-charge refund equal to the charge. P4 supersedes the route_inefficiency clause globally but books only on failed-to-collect fares, dropping the collected-fare branch.
- G-O3. The base clause "An outstanding charge is settled in full by one trip_balance_settlement row for that charge" is superseded by two policies (P3, P6) with two different replacements; scopes are compatible.
- G-O4. P2 and P5 declare `subject: [trip_fare_adjustment]` but write `trip_fare_reviews`.
- G-O5. Business reality doubtful, not demonstrable as RED: a rider's cleaning/damage-fee history scaling the return of a toll the driver's detour caused (P3), the referral of the driver-caused delay (P5) and the hold-out (P6); Wayfare Bikes ride frequency scaling a detour fare correction (P4) and the share of a disputed fare held from collection (P6).
- G-O6. Factors labelled `cross_difficulty: bike` read a product no difficulty of this scenario claims.
- G-O7. P3 and P4 share the unpaid balance with no fixed order. P4's unpaid cap could make the two orders differ; neither task's world reaches that cap.

## closing_checklist

Written after both reveals (2026-10-11 ~11:55Z). The charter-global section above was frozen at mtime 11:52:22Z (sha256 47e1a4c0…fe78) and is unchanged. Its in-file freeze time "11:50Z" is the true start time.

**Difficulty NOT closed.** The four relationships do not all PASS:

| Task | Policy self-consistency | Problem tree | Factors | Unique solution |
|---|---|---|---|---|
| 0 | PASS (task checks) | PASS | SOURCE-FACTOR RED (G-1a, G-1b) | PASS (GT = independent derivation: 29.88, 50.34) |
| 1 | SOURCE-POLICY RED (G-2, G-3) | PASS | SOURCE-FACTOR RED (G-1b, G-1c) | SOURCE-TASK RED (P6 11.72 vs 14.25; P4 booked vs referred, P6 34.38) |

Checklist items, for the record:
- Per-task files `0.md` and `1.md` correspond one-to-one with tasks/0.json and tasks/1.json; `_difficulty.md` sits alongside them. This is the first revision. Not every comparison section carries PASS.
- All six extended policies are covered. The scopes {P1, P2} and {P3, P4, P5, P6} are disjoint, and GT `charter_scope` agrees. Each task tool has a distinct, independently generated uuid8. Pass.
- Trees: task 0 has 1 prerequisite (1 value_input) and a user write (P2). Task 1 has 3 prerequisites (3 value_input) and a user write (P6). The difficulty-wide graph is acyclic. Pass.
- Factors: every computation declares a self-sufficient baseline that differs from gold, and 4–6 factors that all bear weight. However, P1, P2, P3, P5 and P6 have no honest `method` factor (G-1b). P1's guarantee-discount ladder has two real tiers (G-1a). Tier parts in P3 and P5 restate scope (G-1c). Fail.
- Gate re-run on the final form: not performed by this audit. The skill leaves gate runs to the coordinator, and the artifacts were not changed. The snapshot in the brief stands.

## revision_2

### charter_global_frozen (revision 2)

- Freeze: written 2026-10-11, before any revision-2 GT was read. Auditor: the same erl-task-policy-audit subagent (claude-opus-5-5).
- Inputs (sha256 re-computed, equal to the brief):
  - `trip.extended.yaml` 398264273d0801c0d33eccd937ea04ae187dcb2237cf0cb7a9068d8fd7d5204f — **changed**, so every charter-global section is re-derived in full below.
  - `task_tools.py` 7643ac5f…2522 — unchanged; action_binding_and_uuids is carried forward by reference to revision 1 on the grounds of this hash.
  - views `0.view.json` 38a37724…5a26, `1.view.json` 56c72c77…833f.
- Base copy: lines 1–1328 still equal `blueprint/products/trip.yaml` (diff shows only the trailing blank line).
- Masked until both tasks' revision-2 derivations are frozen: the same nine keys as revision 1.
- contamination_disclosure: in revision 1 this auditor read the revision-1 GT of both tasks (`evaluation_criteria`, `computations`, `prerequisite_closure`, `design_rationale`, `solvability_contract`). Its formula conventions and revision-1 figures are therefore known. The worlds and the charter have since changed, and the brief gives no revision-2 figure. The revision-2 blind derivation was worked from the new charter and views. Revision-1 knowledge can only have shaped which conventions the auditor checked, never a figure.

### policy_conflict_scan (r2)

- The same six policies, targets and owners. Trigger regions are still separated by fare basis: {P1, P2} act on upfront fares, {P3, P4, P5} on recalculated fares with no rider route change.
- P3 now excludes collected fares.
- P3 and P4 both state that their settlement entry counts toward the trip's support limit. P4 adds: "A detour fare correction that would take the support total of the trip above the ride option's support limit is sent to the fare review team as a fare review instead of being booked."
- P3/P4 still share the unpaid balance with no fixed order; P4's cap is the unpaid amount (G-O7, unchanged in the charter).
- Scope partition unchanged: {P1, P2} and {P3, P4, P5, P6} are disjoint and together cover all six policies.

### rule_compute_equivalence (r2)

- **P1.** The guarantee discount is now a single baseline sentence ("…it is that plan's member discount percent … ; otherwise it is nil") implemented by `guarantee_discount`.
  - The zero floor is now stated ("it is never below zero") and implemented as `MX(0, …)` in `result`.
  - `membership_fees_last_year` now filters on `pass_membership_id`.
  - Ride-credit deduction: `trip_credit_earned` = pass_credit_earn on this trip; `guaranteed_fare_credit` = MN(pct × (guaranteed − booking fee), per-trip cap), unrounded; the three branches match the rule.
  - Match. Observation R2-O5: the recomputed credit ignores the pass charter's min-eligible-fare, eligible-option and monthly-cap terms.
- **P2.** `onward_reimbursement` has three branches (sum as booked ≥ 5.00 / flat 3.00 / none), matching the rule. The rest is unchanged. Match.
- **P3.**
  - `attributed_toll`: ≥1.75 → whole toll; ≥1.25 → toll × (actual − estimated) / actual; else toll × 0.25. Single reading — "in proportion to the extra miles" fixes the grouping.
  - `facility_weight` reads `LATEST(toll_facility)`; the rule says "the toll facility charged on the trip", one facility (observation R2-O6 for multi-toll trips).
  - `result` = RND(MN(attributed × weight × tenure × timeliness + allowance, toll)), and the rule says "with the fare-size allowance then added in dollars". Unambiguous. Match.
- **P4.** `booking_fee_return` partial share is 0.6. The multimodal credit is removed. Match.
- **P5.**
  - `measured_delay_minutes`, three branches: ratio ≥1.40 with a toll → (Δmiles × actual minutes / actual miles); ratio ≥1.10 → MX(0, actual minutes − estimated minutes × actual miles / estimated miles); else actual − estimated minutes.
  - `minute_value_factor`: reservation-fee or reservation-waiver entries → 2.0; Priority Pickup charge or waiver entries (not reserved) → 1.5; else 1.0.
  - Match.
- **P6.**
  - The held-out sentence is now explicit: "that dollar figure is then multiplied by the fare-basis share, by the payment-history factor and by the hold-out timing factor, each a fraction with no dollar amount added". It is implemented as `MN(review × share × history × timing, cap, unpaid)`.
  - `review_amount_counted` has three branches by membership status and presence. `declined_fee_payments` counts pass_payment_decline rows in 3 months.
  - Match, single reading.
- Every `baseline.rule` sentence of the six policies is a sentence of its own rule (checked mechanically). Every ladder tier is stated in the rule and implemented in `decides`.

### action_binding_and_uuids (r2)

`task_tools.py` hash is unchanged. Carried forward from revision 1: tools unique per policy, no docstring sequencing, no tool body tests a prerequisite, uuid8s independent. `subject` mislabels on P2 and P5 persist (G-O4, left as is by the reworker).

### prerequisite_graph (r2)

- Same four edges: P2→P1; P6→P3, P6→P4, P6→P5. Acyclic.
- Each `policy_source` is verbatim in its own rule (checked mechanically).
- `form: state` on all four edges.
- Gates `fare_still_standing`, `unpaid_left` (×2) and `review_amount_counted` all exist in their policies' compute.
- `resolved_by` equals the depended-on policy's target_tool on every edge.
- Pass.

### prerequisite_sentences (r2)

- The four sentences are unchanged and still pass the four-point test, each with one writer in this difficulty (revision-1 table carried forward).
- New text checked for undeclared cross-problem order: P4's "sent to the fare review team as a fare review instead of being booked" describes P4's own above-limit outcome, not an order against another problem. No new ordering sentence. Pass.
- Observation R2-O3: in the above-limit branch the charter names no tool for the P4 fare review. P6's sentence "fixed only after a fare … carries a refund-offset settlement entry giving route inefficiency" could then never hold. Neither world reaches that branch.

### override_declarations (r2)

- **P1.** The fare_above_upfront clause is superseded; the replacement now includes "less the ride-credit deduction" and the zero floor. Declared. Every other base sentence is followed, the support limit explicitly.
- **P2.** `overwrite: []`, no conflict (unchanged).
- **P3.**
  - The toll-charging clause is superseded only up to its first ";". The replacement keeps "A toll is still charged once per toll facility crossed …", and the "on the way to the pickup" half stays in base. The merged text keeps the charging rule.
  - New sentence: "The reason toll not incurred on such a settlement entry marks the detour toll return; it is not a refund of the toll charge, which keeps its whole-charge meaning on a refund entry." This resolves the reason-code conflict with `trip_evt_adjustments_and_refunds`.
  - The settlement now "counts toward the trip's support limit as a refund of that amount would", declared inside the superseding text. **G-O2 closed.**
- **P4.**
  - The route_inefficiency clause is superseded by a text that keeps the collected-fare adjustment ("On a collected fare, a route-inefficiency fare adjustment still takes back …"), so the dropped branch is restored in text.
  - The refund_offset replacement now says "the entry counts toward the trip's support limit in place of the fare adjustment it replaces". A rule sentence sends an above-limit correction to fare review.
  - The base support-limit sentence S7 now governs P4 in the same direction it governs base adjustments. **G-2 closed at charter level.** Per-world check in `1.md`.
- **P5.** No conflict.
- **P6.** Hold sentence and "settled in full" declared superseded (unchanged). The double supersession of "settled in full by one row" by P3 and P6 persists (G-O3, compatible scopes, left as is).

### factor_ladders (r2)

| Policy | Factors (label) | Honest method | Tier/label checks |
|---|---|---|---|
| P1 | makegood_rate (param, multi-source, pass), makegood_cap (param), repeat_error_multiplier (param), makegood_timeliness (param), **ride_credit_deduction (method, pass)** | ride_credit_deduction: earned − recomputed credit / whole credit / none are three different computations | ok; guarantee_discount_by_plan removed from the factor set (now a baseline sentence) — **G-1a closed** |
| P2 | stranding_share (param, multi-source), member_review_multiplier (param, pass), review_request_cap (param), **onward_journey_basis (method)**, luggage_allowance (param), review_timeliness (param) | onward_journey_basis: sum as booked vs flat allowance vs none | ok; bike factors now `cross_difficulty: null` — **G-O6 closed** |
| P3 | **toll_attribution (method)**, facility_weight (param), member_tenure_multiplier (param, pass), toll_timeliness (param), fare_size_allowance (param) | toll_attribution: whole / proportional formula / fixed share | the "toll entry" scope condition is gone — **G-1c closed for P3**; fee_history removed |
| P4 | honoured_quote_basis (method, pass), booking_fee_return (param), member_detour_credit (param, pass), detour_credit_cap (param) | yes | ok; multimodal credit removed |
| P5 | **delay_measure (method)**, delay_grace_minutes (param, pass), minute_value_factor (param), referral_timeliness (param), referral_cap (param) | delay_measure: three different minute formulas | delay_rate_multiplier and its "recalculated" scope part removed — **G-1c closed for P5**; fee_history removed |
| P6 | **review_amount_basis (method, pass)**, fare_basis_share (param), payment_history_factor (param, pass), holdout_timing (param), holdout_cap (param) | review_amount_basis: all reviews on the trip / reviews on the unpaid charge only / none | multimodal uplift removed |

- Counts: P1 5 (4/1), P2 6 (5/1), P3 5 (4/1), P4 4 (3/1), P5 5 (4/1), P6 5 (4/1). Every policy now has 4–6 factors, ≥2 parameter and ≥1 honest method. **G-1b closed.**
- All ladders have ≥3 tiers with distinct outcomes. Every fall-through equals its baseline.
- Observations on ladder reality (judgement, not demonstrable as RED):
  - R2-O1: P3 `toll_attribution` is non-monotone. For a ratio r in [1.25, 4/3) the proportional tier gives (r−1)/r < 0.25, so a longer detour returns less toll than a shorter one (fall-through 0.25).
  - R2-O2: P5 `delay_measure` tier 2 counts the overrun beyond what the longer route "should take". That is the opposite idea from tier 1 (time spent on the extra miles) and can give 0 for a pure detour, against the rule's premise "the time a rider lost to a driver's detour".
  - R2-O4: P3 `facility_weight` falls through only for the Utah I-15 express lanes, the same kind of facility tier 2 describes ("which a rider may choose for speed"). P6 `payment_history_factor` puts the two-or-more-declines case on the fall-through and calls it "standard".
- G-O5 is closed: the cleaning-fee-history and bike-usage drivers are removed from P3–P6.

### findings (r2, charter-global, pre-reveal)

| Round-1 item | Status at charter level |
|---|---|
| G-1a | closed |
| G-1b | closed |
| G-1c | closed |
| G-2 | closed (P3 and P4 count toward the limit; above-limit corrections go to review) — world check in `1.md` |
| G-3 | closed (held-out sentence unambiguous) |
| G-O1 | closed |
| G-O2 | closed |
| G-O3 | persists (left as is) |
| G-O4 | persists (left as is) |
| G-O5 | closed |
| G-O6 | closed |
| G-O7 | charter text unchanged (P4's unpaid cap and P3/P4 order); harmless unless a world reaches the cap — world check in `1.md` |

New charter observations: R2-O1 … R2-O6 above. No new charter-global RED.

### closing_checklist (r2)

Written after both revision-2 reveals (13:42:14Z). The revision-2 charter-global section above was frozen at 13:41:16Z and is unchanged.

| Task | Policy self-consistency | Problem tree | Factors | Unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS (27.52, 51.37 = GT) |
| 1 | PASS | PASS | PASS | PASS (2.57, 19.63, 6.95, 18.43 = GT) |

- One-to-one files: `0.md` and `1.md` match tasks/0.json and tasks/1.json, with `_difficulty.md` alongside. Revision 1 text is untouched; revision 2 is appended. Every revision-2 comparison carries PASS.
- Coverage and scope: all six extended policies are covered, scopes are disjoint, and GT `charter_scope` matches. Tools and uuid8s are unchanged and pass.
- Trees: task 0 has 1 prerequisite (value_input) with user write P2. Task 1 has 3 prerequisites (all value_input) with user write P6. The difficulty graph is acyclic.
- Factors: every computation has a self-sufficient baseline different from gold and 4–6 factors (≥2 parameter, 1 honest method). Each task has a multi-source factor and a pass cross-difficulty factor. Every factor bears weight on its world against an honest baseline.
- Reworker claims: G-1a, G-1b, G-1c, G-2, G-3, G-O1, G-O2, G-O5, G-O6, T0-O1, T1-O1 and T1-O2 are verified closed. G-O7's charter text is unchanged (P4's unpaid cap, no fixed P3/P4 order); it is harmless in both worlds, so it is "not binding" rather than closed. G-O3 and G-O4 are left as is, as stated.
- New observations (no demonstrated consequence): R2-O1 … R2-O6 (§ revision_2 factor_ladders, prerequisite_sentences, rule_compute_equivalence).
- Gates: the coordinator's revision-2 snapshot (all OK, rc=0; traceability deferred) is cited; this audit did not re-run them.

**The difficulty passes the source-layer audit at revision 2.**

## revision_3

### charter_global_frozen (r3)

- Written 2026-10-11, before any revision-3 GT was read. Auditor unchanged.
- Inputs (sha256 re-computed, equal to the brief):
  - `trip.extended.yaml` 0f151ccb7a3e012281b99efd42516d075abaeb7afcc96a317934d899e93ff5d3 (changed);
  - `task_tools.py` 7643ac5f…2522 (unchanged; action_binding_and_uuids carried forward);
  - views 0 f1b0b7c1…140d and 1 43438c86…0222.
- Base copy is still verbatim.
- Extra read permitted by the brief: `docs/pass/` (published Pass KB). Only the hubs, baselines and factor documents of `pass_ext_refunded_fare_credit_forfeit` and `pass_ext_trip_credit_posting` were opened, plus the policy docs `ride_credit_spending_and_forfeiture` and `ride_credit_earning_rules`. The pass difficulty's tasks directory was not opened. The audit relies only on what those documents publish, not on the pass difficulty's own `meta.source` file.
- contamination_disclosure: revision-1 and revision-2 GT of both tasks were read in earlier rounds. The brief states task 1's scored values are unchanged. Task 1's revision-3 derivation therefore cannot count as blind for its figures; it is a re-verification. Task 0's world was re-cut and no revision-3 figure was supplied, so task 0's derivation below is blind.
- What changed in the charter: lines 1330–1529 (P1) are the only change. The file grew by 6 lines, all inside P1. P2–P6 have identical parameters, factor sets, prerequisite lists and line spans to revision 2. P1 changes:
  - `makegood_cap_standard` 4.00 → 3.00;
  - new `ledger_correction_share: 0.10`;
  - the ride-credit deduction now applies only where "the correction before the deduction … comes to less than the ledger-correction share of the eligible fare";
  - a new sentence: "A correction that, before the deduction, takes back the ledger-correction share of the eligible fare or more leaves the ride credit earned on the trip to be corrected on the Wayfare Pass membership ledger and deducts nothing from the fare adjustment, so the credit is never recovered twice."

### P1 re-check (r3) — checks 1, 2, 6, 7 and factor ladder

- Override: the overwrite `replaced_by` is unchanged and still verbatim in the rule. The new deduction gate refines the declared replacement and does not touch another base sentence. Pass.
- Rule ↔ compute:
  - `correction_before_deduction` = excess + make-good, quoting "that is the part billed above the guaranteed fare plus the billing-error make-good".
  - `eligible_fare_for_credit` = MX(0, fare − booking fee), quoting "the fare charge less the ride option's booking fee".
  - The gate `< K('ledger_correction_share') * eligible` sits on tiers 1 and 2; otherwise there is no deduction.
  - Both directions match. Baseline sentences are in the rule (checked mechanically).
- Ladder `ride_credit_deduction` (method):
  - tier 1: credit earned + benefit status + under the share → earned − recomputed credit;
  - tier 2: credit earned + other status + under the share → whole credit;
  - fall-through: nothing.
  - The three outcomes are distinct computations. The tiers are multi-source (pass_events credit, pass_memberships status, trip_charges fare). The share condition is a real business split (small corrections net the over-earned credit in cash; larger ones are corrected on the Pass ledger) and does not hold for every customer. Pass.
- Cross-difficulty coherence with the published Pass rule:
  - `docs/pass/adjusted_fare_credit_clawback_e355b0cd.json` claws back credit only where "the adjustments took back at least a tenth of the eligible fare". Under a tenth, nothing is clawed back.
  - P1 deducts only where the pre-deduction correction is under a tenth. The booked adjustment is never larger than that figure, so the Pass clawback is nothing exactly when P1 deducts.
  - Where P1 does not deduct, the booked adjustment equals the pre-deduction figure, so the Pass clawback takes over.
  - The relief factors (correction timing, frequent rider, loyalty, Wayfare Pro) only reduce a positive clawback.
  - So the credit is recovered once on either side of the threshold. **The KB-audit double-recovery is closed at charter level.**
  - Observation R3-O1: the Pass rule also claws back the whole credit where the adjusted eligible fare falls under 5.00. P1's gate does not mirror that branch. It can only arise on fares of about 5.56 or less, which no world here has.
- Prerequisite graph and sentences: unchanged. The four edges still verify (verbatim, gate exists, resolved_by matches). The new P1 sentence names the Pass ledger with no ordering connective and grounds no edge, so it is not an undeclared order. Pass.
- Factor counts: P1 still has 5 factors (4 parameter, 1 method); P2–P6 unchanged from revision 2. Pass.

### carried forward (r3)

The revision-2 conclusions for P2–P6 (override, equivalence, ladders, observations G-O3, G-O4, R2-O1 … R2-O6) are carried forward. Grounds: identical parameters, factors, prerequisites and line spans; the only diff is confined to P1.

### findings (r3, pre-reveal)

There was no round-2 RED to re-close; round 2 passed. No new charter-global RED. New observation R3-O1 (above).

### closing_checklist (r3)

Written after both revision-3 reveals (15:30:52Z).

| Task | Policy self-consistency | Problem tree | Factors | Unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS (8.55, 46.57 = GT) |
| 1 | PASS | PASS | PASS | PASS (2.57, 19.63, 6.95, 18.43 = GT, unchanged) |

- Round-2 REDs to re-close: none; round 2 passed.
- The KB-audit cross-difficulty overlap is verified closed:
  - Charter: P1's deduction gate equals the Pass clawback threshold, so the credit is recovered once on either side of it.
  - Task 0 world: the Pass forfeiture computes to nothing, and no posting or goodwill is owed.
  - Task 1 world: there is no fare adjustment entry, so the Pass hub is not triggered.
- Reworker claims verified:
  - only P1 changed (rule, compute, ladder, params);
  - task 0 world re-cut (frozen_time, membership history, credit posting at 48 h);
  - task 1 credit-earn date moved to 2026-09-10;
  - two task-0 scored values moved; task 1 unchanged.
- No regression. Revision-1 and revision-2 text is untouched; revision 3 is appended.
- Open observations (no consequence on either world):
  - G-O3 and G-O4;
  - R2-O1 … R2-O6;
  - R3-O1: the Pass whole-credit-under-5.00 branch is not mirrored in P1's gate;
  - R3-O2: P4's settlement-for-adjustment wording versus the Pass hub trigger.
- Gates: the coordinator's revision-3 snapshot (all OK including TRACEABILITY and validate_scenario VALID) is cited, not re-run.

**The difficulty passes the source-layer audit at revision 3.**
