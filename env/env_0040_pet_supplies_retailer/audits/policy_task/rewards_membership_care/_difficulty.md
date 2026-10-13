# Policy-task audit — rewards_membership_care / charter-global

## charter_global_frozen

- Scenario: `env/env_0040_pet_supplies_retailer`; difficulty `rewards_membership_care`; category `member`; M = 2.
- Auditor: independent erl-task-policy-audit agent (did not write any audited artifact). Revision 0, no earlier audit exists.
- Freeze time of this section: 2026-10-06T06:06:41Z (file write time) (written before any task's GT was revealed; contains nothing derived from a revealed GT).
- Freeze hashes (re-checked with sha256sum, both equal to the orchestrator brief):
  - `tasks/rewards_membership_care/member.extended.yaml` b9b17c2a7a2a581133ee179556300a8837559f744ee402fb62c8e45ec8e88a33
  - `tasks/rewards_membership_care/task_tools.py` 656afc4d577ce1e0e027123160e47b413cbba908604f827141c4aee7ea6df97c
  - masked views `task_0.view.json` 692e497e…c6a4, `task_1.view.json` f9a0d36f…0e95 (equal to the brief).
- Fields permitted for this section: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml of this scenario), `member.extended.yaml`, `task_tools.py`, `erlbench/` and the gate scripts' evaluator semantics (`skills/erl-task-instantiate/scripts/check_compute.py` — read only for the MONTHS/DAYS/within_months definitions).
- Fields masked: all of `tasks/rewards_membership_care/tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), the scenario `worklog.md`, any earlier audit. None was opened.
- Entry conditions (Step 0): gate snapshot supplied (`/tmp/e40views/policy_task/rewards_membership_care/gate_snapshot.txt`): check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all print OK / exit 0; check_traceability deferred until the KB is published (stated by the orchestrator). Masked views built and hashed. Entry conditions met; the deferred traceability gate is recorded, not run by this audit.
- Base-copy check: `diff <(head -1533 member.extended.yaml) blueprint/products/member.yaml` → identical (BASE_VERBATIM).

Policy ids used below: P1 `member_ext_missed_autoship_earning` (post_missing_points_02f0bcb5, agent), P2 `member_ext_earned_tier_bonus` (apply_earned_tier_ebf561a6, agent), P3 `member_ext_plus_annual_first_fee` (buy_plus_tier_1a1727fb, **user**), P4 `member_ext_overdue_annual_fee` (reinstate_plus_tier_c2894e52, agent), P5 `member_ext_return_certificate_reissue` (reissue_returned_certificate_0ad7eee8, agent), P6 `member_ext_refund_points_reversal` (reverse_refund_points_2db3868c, agent), P7 `member_ext_premier_upgrade_charge` (upgrade_plus_tier_d51b9d82, **user**).

### policy_conflict_scan

- Overlapping subjects: `member_tier_change` is the subject of P2 (spend upgrade, free tier), P3 (buy Plus Annual from a free tier) and P7 (Plus Annual → Premier). Their triggers are disjoint by the tier held (free tier earned by spend / free tier buying / Plus Annual holder), and each sets a different `last_change_reason` in its tool (spend_upgrade / plus_purchase / plus_upgrade). `member_fee_charge` is the subject of P3 and P7 and is also written by P4's tool; the three charges are distinguished by trigger (purchase from free tier / upgrade / past-due collection). No pair reaches incompatible conclusions on one subject in one situation.
- The same base clause of `member_plus_billing` ("A paid tier charges membership_fee_usd on each next_billing_date while auto_renew is true;") is named as `superseded_clause` by three policies (P3, P4, P7) with three different `replaced_by` texts. Each replacement is scoped to its own charge, so none of the two tasks gets two answers from it; but the ordinary renewal charge on `next_billing_date` — the only charge that clause literally governs — is left with three replacements none of which is about it (observation O-1).
- Time anchors: P4 anchors on the declined-fee entry date (= the day the membership went past due, base `member_fee_declined` meaning); base grace (`past_due_grace_days`) still gates reinstatement and is not touched. P5 anchors on the certificate's last usable day and the refund date; P6 on the line's earning date, the refund date and the latest declined-fee entry; P7 on the latest fee's charge date and billing period start. No conflict found.
- Cross-category read boundaries (scenario-level KB is one merged corpus — `erlbench/loader.py` docstring: "All difficulties' tools and KB documents are merged into one registry and one corpus"):
  - `blueprint/products/autoship.yaml` policy `autoship_evt_rewards_earn`: "Each charged Autoship shipment earns Pals Rewards points on its merchandise subtotal after the Autoship discount at the member's base earn rate multiplied by points_multiplier; shipping, surcharges and packaging fees never earn." P1 posts, as the earning entry of that same shipment, the standard points **plus** apology/milestone/streak/bundle bonuses scaled by a lateness method. P1's `overwrite` declares the member base earn sentence only; the autoship base sentence governing the same quantity is not overridden anywhere in this charter (finding F-3).
  - `blueprint/products/order.yaml` policy `order_evt_rewards`: "A cancelled, refunded or credited line reverses the points it earned in proportion." P6 books the reversal of a refunded order line by a method/fault-share/allowance computation; P6's `overwrite` declares only the member base sentence of `member_evt_points_reverse`; the order base sentence on the same quantity stands (finding F-3).
- Claimed scope vs blueprint claim: blueprint.yaml claims for this difficulty event_types `[member_enroll, member_tier_change, member_bonus_points, member_certificate_reissue, member_cancel_request, member_cancel_withdraw, member_fee_refund, member_reinstate, member_close]`. P1's subject `member_points_earn`, P6's subject `member_points_reverse`, and the `member_fee_charge` subject of P3/P7 are not in that list (P4's tool also writes `member_fee_charge`). Cross-difficulty disjointness is outside this skill; recorded as observation O-2.
- Task scopes (derived from the charter and the two worlds before any reveal; see each task file): task 0 = {P1, P2, P3}, task 1 = {P4, P5, P6, P7}. Pairwise disjoint and jointly complete over the 7 extended policies.

### rule_compute_equivalence

Every compute binding of P1–P7 has a verbatim `compute_basis` quotation that is a sentence of its rule (checked by reading each binding against its rule). Every factor ladder tier is a sentence of the rule and a branch of its `decides` binding, and every branch of each `decides` binding is a tier the rule states. Points where compute invents a basis or the rule promises more than compute implements:

1. P1 `program_multiplier: CPARAM('autoship', 'points_multiplier', status='active')` — rule: "the points_multiplier of the Autoship program the shipment belongs to". Compute reads the first *active* Autoship holding, not the holding the shipment belongs to (status filter invented; wrong object when the customer holds several programs or the shipment's subscription is no longer active). Observation O-3 (no consequence on task 0: one active subscription, which is the shipment's).
2. P1 `salon_visits_left: CFIELD('groom','visits_remaining', status='active')` — first active pass vs rule "an active grooming pass with at least bundle_visits_left visits remaining" (any pass). Observation O-3 (task 0 has one pass).
3. P1 rule "A shipment that already carries a points earning on the ledger earns nothing further." has no compute counterpart (it is an eligibility gate, not part of the amount). Observation.
4. P5 `cert_last_day: LATEST('member_events','certificate_expires_on', event_type='member_certificate_issue')` and `refund_date: XLATEST(order refund)` read the *latest* certificate and the *latest* refund of the customer, while the rule reads "the certificate being reissued" and "the refund date of the return". P6 `line_points/line_spend/line_earn_date` read the latest order-line earning, while the rule reads "that order line". P6 `basis_points` tests only the latest fee charge date against the window "no membership fee charged from that entry's date through the refund date". Observation O-3 (both task-1 worlds have a single matching object; no consequence there).
5. P3 `ship_fees_12m` counts `order_fee_charge` rows with fee_kind shipping, rule says "charged a ship-to-home shipping fee on at least ship_fee_high_count orders" (orders, ship-to-home). P3/P4/P7 salon bindings read the customer's latest completed visit across all passes vs "an active grooming pass whose latest completed visit". Observation O-3.
6. P3 `after_credit: MX(0, standard_fee - return_credit)` adds an intermediate floor not stated in the rule; the final floor makes the two readings coincide (a negative intermediate times (1-rate) minus flats is still ≤ 0). No consequence.
7. Rounding points, caps and counting conventions otherwise match their quoted sentences (P1 round-down then cap last; P2 integer sum; P3/P4/P7 round to cent last; P5 integer days; P6 two caps last).

Window convention (evaluator, `check_compute.py` `_within`): a row is "in the last N months" when `MONTHS(row_date, NOW) < N` with MONTHS counting whole months; neither task world has a row on a window boundary, so a reader using calendar subtraction reaches the same counts.

### action_binding_and_uuids

- `(target_tool, computes)`: (post_missing_points_02f0bcb5, points) P1; (apply_earned_tier_ebf561a6, upgrade_bonus_points) P2; (buy_plus_tier_1a1727fb, first_charge_usd) P3; (reinstate_plus_tier_c2894e52, overdue_fee_usd) P4; (reissue_returned_certificate_0ad7eee8, validity_days) P5; (reverse_refund_points_2db3868c, points) P6; (upgrade_plus_tier_d51b9d82, upgrade_charge_usd) P7. Each claimed by exactly one policy.
- Tool bodies: every function books the passed value; none reads a prerequisite state, refuses, errors or hints (task_tools.py lines 21–367). No confirmation/review/wait procedure is added.
- Docstrings: no tool names another tool; no docstring places its action in a sequence. "Afterwards the customer sees …" (every tool) describes the outcome view, and "pay its first fee today" (buy_plus_tier) names the first-term fee; neither is a cross-action ordering word (observation O-4 only).
- Generic docstrings: `post_missing_points_02f0bcb5` and `reverse_refund_points_2db3868c` accept any program (`source_category` enum of eight programs) while P1/P6 cover only Autoship shipments / retail order lines — the tool surface is wider than its policy; no task consequence.
- uuid8s: 02f0bcb5, ebf561a6, 1a1727fb, c2894e52, 0ad7eee8, 2db3868c, d51b9d82 — no shared prefix, tail, sequence or adjacency; consistent with independent generation. PASS.

### prerequisite_graph

Edges (blocked ← depended-on): P2 ← P1 (value_input, gate net_spend_12m); P3 ← P2 (value_input, gate loyalty_rate); P5 ← P4 (state_gate, member_memberships.status); P6 ← P5 (state_gate, member_events.original_event_id); P7 ← P4 (value_input, term_fee); P7 ← P6 (value_input, net_spend_12m). P1 and P4 carry `prerequisite: []`.

- Every policy has the field; every `problem` is an extended policy id of this file, never itself, never a base id. Graph acyclic (topological orders P1→P2→P3 and P4→P5→P6→P7).
- Every `policy_source` is a verbatim, single occurrence in its own policy's rule (script check: `policy_source in rule` True, count 1, for all six edges); no other policy's rule restates it.
- All six edges are `form: state`, none carries `fallback_reason` — consistent.
- `resolved_by` equals the depended-on policy's `target_tool` on all six edges.
- `kind`/`gate`: the four value_input gates name bindings that exist in the blocked compute (net_spend_12m in P2 and P7, loyalty_rate in P3, term_fee in P7). P5's state_gate points at the real base eligibility `certificate_status` (status active/pending_downgrade). P6's state_gate names a column (`member_events.original_event_id`) rather than an eligibility of `member_evt_points_reverse`; the gate exists only through P6's own prerequisite sentence (observation O-5).
- `effect` texts are general (no "in this task / at the opening" phrasing). P2←P1's effect describes only the 12-month spend and latest-earning date; it omits that the posting can also be what makes the next free tier earned under `member_tier_qualification` (observation; its consequence is demonstrated in task 0's file).
- PASS at graph level.

### prerequisite_sentences

Four-point test on each edge's sentence (ordering connective / record-visible state / no tool, id or snake_case / strength equals `condition`):

| edge | sentence | connective | state named | strength vs condition | single resolving write of this difficulty |
|---|---|---|---|---|---|
| P2←P1 | "The earned-tier upgrade bonus is not posted until the rewards ledger carries a points earning for every charged Autoship shipment of the last 12 months." | not … until | ledger earning per charged shipment, 12 months | equal | post_missing_points (P1). But P1's rule posts only for "a customer's most recent charged Autoship shipment"; a world in which an older shipment of the 12 months lacks its earning has a state no policy of this charter can bring about (observation O-6; not the case in task 0) |
| P3←P2 | "The first-term Plus Annual fee is fixed only after the membership carries the free tier that its qualifying spend has earned." | only after | the free tier held vs the tier earned by qualifying spend | equal | apply_earned_tier (P2); buy/upgrade set paid tiers |
| P5←P4 | "A certificate used on a returned order is not reissued until the membership has left the past-due status." | not … until | membership status | equal | reinstate_plus_tier (P4) — the only agent/user write moving past_due→active |
| P6←P5 | "Points on a returned order line are taken back only after the rewards ledger carries the reissue of every certificate used on that order." | only after | certificate-reissue entry for each certificate used | equal | reissue_returned_certificate (P5); no courtesy-reissue tool exists |
| P7←P4 | "The upgrade charge is fixed only after every billing period the membership has started carries a charged membership fee." | only after | fee charge per started billing period | equal | reinstate_plus_tier (P4) |
| P7←P6 | "The upgrade charge is not fixed until every order line refunded in the last 12 months carries its points reversal on the rewards ledger." | not … until | reversal entry per refunded line, 12 months | equal | reverse_refund_points (P6) |

- No rule names a tool, a policy id, a snake_case token or a row id in its prerequisite sentence; the depended-on rules do not restate the sentences.
- Written derivations (sentence + records + depended-on rule → resolving action), single reading each: "points earning for every charged Autoship shipment" → the only rule that books an earning for a charged Autoship shipment is P1's ("a care agent posts the missed-earning points for that shipment"); "carries the free tier that its qualifying spend has earned" → the only rule that applies an earned free tier is P2's; "left the past-due status" → base lifecycle `past_due → active by agent` = P4's collection ("which reinstates the paid tier"); "the reissue of every certificate used on that order" → P5's rule ("a care agent reissues that certificate"); "every billing period … carries a charged membership fee" → P4 ("collects the overdue fee for the billing period whose fee was declined"); "every order line refunded … carries its points reversal" → P6 ("a care agent books the reversal").
- Undeclared cross-problem orders in rules: none in the extended rules. The `order of these steps is fixed` sentences (P3, P4, P6, P7) order computation steps inside one policy, not problems. Base `member_account_closure` ("a paid tier is cancelled first") states a cross-problem order but grounds no edge of this charter (observation).
- Whether each edge's state is genuinely unmet at a task's opening is a per-task fact (see task files) — in particular task 0's P3←P2 edge.
- Charter-global verdict for check 6: PASS (with O-6).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry; the criterion is the quantity finally scored.

- P1 vs `member_evt_points_earn`: the points formula sentence is declared superseded. Inherited and untouched: status gate at purchase, no retroactive earning before enrollment, excluded categories, membership fees not earning, "One purchase record earns once". Rate source "of the tier the membership holds" (at posting) vs base (unspecified tier) — no conflict. Declared. Cross-category: autoship base earn sentence on the same quantity not declared (F-3).
- P2 vs `member_evt_bonus_points`: declared superseded clause "Enrollment bonuses and tier-upgrade bonuses post with the enrollment or the spend upgrade that earns them." is replaced only by a sentence about the earned-tier bonus — the enrollment-bonus half of the sentence is dropped from that policy (dropped-branch form). The enrollment bonus survives in `member_enrollment_and_trials` ("The enrollment_bonus_points of the tier joined are posted once, on the first enrollment of that tier."), which no extended policy overrides and no task tool can book (buy/upgrade tools post no bonus; apply_earned_tier books only kind tier_upgrade). Finding F-4.
- P2 vs `member_tier_qualification`: base "A membership moves up … within tier_upgrade_effective_days once member_msr_spend_current_year reaches that tier's qualifying_spend_threshold_usd" (schema: "calendar days after the qualifying purchase within which a free-tier upgrade takes effect") vs P2 "applies that earned tier effective the day it is applied" — the effective date differs from base when the qualifying purchase is older than 1 day; not named in `overwrite` (undeclared). The tool fixes `tier_effective_on` to today, and no scored quantity of either task reads the new tier's effective date, so no second scored answer is demonstrable — observation O-7. P2 vs `member_enrollment_and_trials`, `member_plus_cancellation`, `member_shipping_benefit`: no governed quantity touched.
- P3 vs `member_plus_billing`/`member_enrollment_and_trials`: the first-term fee amount (base: membership_fee_usd, trial rules) is replaced by the credit/rate chain; declared through the billing sentence. Trial semantics kept ("charged nothing on the purchase date" ⊂ base trial). The base enrollment-bonus sentence still applies to a first Plus Annual enrollment (F-4).
- P4 vs `member_plus_billing`: overdue amount declared via the billing sentence. Base "Paying the overdue fee reinstates the paid tier for the same term dates" vs P4 "reinstates the paid tier for the term that billing period opened" — read literally against the past-due record (whose plus_term_start/end are the expired prior term) these differ; the tool fixes the new term, so no scored second answer — observation O-8. Base grace window and "No late fee is ever charged" inherited.
- P5 vs `member_evt_certificates`: on-return reissue sentence declared superseded; status gate, dedup, "no cash value" inherited.
- P6 vs `member_evt_points_reverse`: proportional-reversal sentence declared superseded; balance floor and "Certificates already issued are not cancelled" inherited (the caps implement the floor). Cross-category order base sentence on the same quantity not declared (F-3).
- P7 vs `member_enrollment_and_trials`: unused-fee credit sentence declared; vs `member_plus_billing` declared. Base perk-credit grant (`member_perk_credits`) consistent with the tool's `perk_credit_usd`. Enrollment bonus of a first Premier enrollment: F-4.
- No anonymous intermediate factor or 0/1 multiplier found outside the declared clauses.

### factor_ladders

| policy | factor | label | decides | tiers | distinct outcomes | multi-source | cross_difficulty |
|---|---|---|---|---|---|---|---|
| P1 | missed_earning_apology | parameter | apology_bonus | 3 | 150/75/0 | yes (enrolled_on on membership + member_events count) | — |
| P1 | subscription_milestone | parameter | milestone_bonus | 3 | 100/50/0 | no | autoship |
| P1 | autoship_streak | parameter | streak_bonus | 3 | 100/40/0 | no | autoship |
| P1 | salon_bundle | parameter | bundle_bonus | 3 | 80/40/0 | no (status and visits on one pass row) | groom |
| P1 | late_posting_adjustment | method | late_adjusted | 3 | ×1.25 round down / +50 / as is | no | — |
| P2 | upgrade_bonus_method | **method** | method_bonus | 3 | ⌊std/2⌋ / std×2 / std | no | — |
| P2 | over_achievement | parameter | spend_bonus | 3 | 250/100/0 | no | — |
| P2 | fast_track | parameter | speed_bonus | 3 | 200/100/0 | no (tier_effective_on + latest earning: two rows) — tiers are single-threshold | — |
| P2 | cross_program | parameter | cross_bonus | 3 | 150/60/0 | yes (autoship events + groom pass) | autoship |
| P2 | membership_tenure | parameter | tenure_bonus | 3 | 100/50/0 | no | — |
| P3 | returning_member_credit | method | return_credit | 3 | 6-month sum / latest fee / none | no | — |
| P3 | plus_loyalty_rate | parameter | loyalty_rate | 4 | .20/.12/.08/0 | no (tier and enrolled_on on one membership row) | — |
| P3 | autoship_credit | parameter | bundle_credit | 3 | 4/2/0 | no | autoship |
| P3 | shipping_fee_credit | parameter | ship_credit | 3 | 3/1.5/0 | no | order |
| P3 | plus_spend_credit | parameter | spend_credit | 3 | 5/2.5/0 | no | — |
| P3 | salon_credit | parameter | salon_credit | 3 | 3/1.5/0 | yes (groom pass status + groom visit event) | groom |
| P4 | past_due_adjustment | method | withheld_fee | 3 | fee×(365−d)/365 / fee×(360−d)/360 / fee | no | — |
| P4 | renewal_loyalty_rate | parameter | renew_rate | 3 | .10/.05/0 | yes (fee-charge events + enrolled_on) | — |
| P4 | first_decline_courtesy | parameter | decline_courtesy | 3 | 2/1/0 | no | — |
| P4 | autoship_courtesy | parameter | autoship_courtesy | 3 | 2/1/0 | no | autoship |
| P4 | salon_courtesy | parameter | salon_courtesy | 3 | 2/1/0 | yes | groom |
| P4 | spend_courtesy | parameter | spend_courtesy | 3 | 3/1.5/0 | no | — |
| P5 | reissue_anchor | method | method_validity | 3 | std+days left / std+days since expiry / std | partly (tier 2: certificate row + order refund row) | order |
| P5 | fault_extension | parameter | fault_ext | 3 | 10/5/0 | no (reason and date on one refund row) | order |
| P5 | reissue_tenure | parameter | tenure_ext | 3 | 6/3/0 | no | — |
| P5 | redeemer_extension | parameter | redeem_ext | 3 | 6/3/0 | no | — |
| P5 | autoship_extension | parameter | autoship_ext | 3 | 4/2/0 | no | autoship |
| P6 | reversal_basis | method | basis_points | 3 | refunded$×8 / refunded$×tier rate / proportional | yes (declined/fee entries + refund row; earning row + membership) | — |
| P6 | return_fault_share | parameter | fault_share | 3 | .5/.75/1 | partly (refund row + earning row) | order |
| P6 | reversal_tenure_allowance | parameter | tenure_keep | 3 | 40/20/0 | no | — |
| P6 | reversal_spend_allowance | parameter | spend_keep | 3 | 30/15/0 | no | — |
| P6 | reversal_age_allowance | parameter | age_keep | 3 | 20/10/0 | no | — |
| P6 | reversal_autoship_allowance | parameter | autoship_keep | 3 | 25/10/0 | no | autoship |
| P7 | unused_term_credit | method | term_credit | 3 | fee×unused/(charge→end) / whole fee / fee×unused/term | yes (fee row's charge date vs its period start; membership term) | — |
| P7 | premier_loyalty_rate | parameter | prem_rate | 3 | .10/.05/0 | yes | — |
| P7 | premier_spend_allowance | parameter | spend_allow | 3 | 12/6/0 | no | — |
| P7 | premier_salon_allowance | parameter | salon_allow | 3 | 10/5/0 | yes | groom |
| P7 | premier_autoship_allowance | parameter | ship_allow | 3 | 8/4/0 | no | autoship |
| P7 | premier_redeemer_allowance | parameter | cert_allow | 3 | 3/1.5/0 | no | — |

Structure checks:
- Counts: P1 5 (4 parameter, 1 method); P2 5 (4/1); P3 6 (5/1); P4 6 (5/1); P5 5 (4/1); P6 6 (5/1); P7 6 (5/1). All within 4–6 as declared.
- Binding sets disjoint within each policy; every `decides` is an input, never `result`.
- Every ladder has ≥ 3 pairwise-disjoint tiers, each stated in the rule (condition + value/method) and implemented in compute; every fall-through equals the policy's `baseline` (0 bonus/credit/allowance/extension, rate 0, share 1, "as it stands", "standard … unchanged/alone", "unadjusted", standard credit/reversal). No two tiers of one ladder carry the same number.
- Baselines: each `baseline.rule` is a set of sentences of the rule, names its params, and yields a definite number without any factor (P1 standard points with cap; P2 standard bonus; P3 59.00 or 0 in trial; P4 membership_fee_usd; P5 certificate_validity_days; P6 proportional reversal with the two caps; P7 premier fee less standard unused-term credit).
- **Label honesty — F-1 (SOURCE-FACTOR RED, charter-global finding):** P2 `upgrade_bonus_method` is labelled `method`, but its three tiers are one formula with a substituted multiplier: "half of that standard bonus, rounded down" = ⌊std × 0.5⌋, "twice that standard bonus" = std × 2, "that standard bonus unchanged" = std × 1. They change a number (a rate on the standard bonus), not how the bonus is computed — the exact shape the skill names as a mislabelled effect. Struck as a method factor, P2's computation has 0 honest `method` factors (bound ≥ 1). Bears on task 0 (demonstrated there).
- Partial numeric-substitution tiers inside otherwise genuine method ladders (observation O-9): P4 `past_due_adjustment` tiers 1 and 2 are the same expression fee × (N − d)/N with N = 365 vs N = 360 (the "30/360 basis" as the rule defines it uses actual past-due days, so only the constant differs); P6 `reversal_basis` tiers 1 and 2 are the same expression ⌊refunded$ × rate⌋ with rate 8 vs the tier's base_points_per_usd; P7 `unused_term_credit` tiers 1 and 3 are fee × unused / D with different denominators. Each of these ladders still contains at least two genuinely different algorithms (prorate vs collect unadjusted; per-dollar vs proportional; whole fee vs proration), so the method label survives; recorded, not red.
- Conditions/outcomes that no customer reaching the write meets: P4 `first_decline_courtesy` fall-through "none or more than two" — "none" cannot hold for a past-due membership (its own declined entry is always within 24 months); the ladder still divides customers by 1 / 2 / >2. P3 `returning_member_credit` fall-through "more than return_lapsed_days days, or no membership fee ever charged" coincides exactly with the free-trial condition (no fee in 365 days ⇒ charged 0.00), so the fall-through can never produce a non-zero fee. Observations O-10.
- Industry realism: the ladders are synthetic (e.g. a salon-pass "bundle" bonus on a missed Autoship earning, Autoship/salon courtesies on an overdue fee) but none selects a treatment no loyalty programme could publish; no realism RED.
- Per-task multi-source / cross-difficulty minimum: task 0 (P1–P3): multi-source P1 apology, P2 cross_program, P3 salon_credit; cross-difficulty autoship/groom/order. Task 1 (P4–P7): multi-source P4 renewal_loyalty_rate, P6 reversal_basis, P7 premier_loyalty_rate; cross-difficulty autoship/groom/order. Both satisfied structurally; seeding is checked per task.

### findings

- **F-1 SOURCE-FACTOR RED — P2 `upgrade_bonus_method` mislabelled `method`.** Symptom: the only method factor of the earned-tier computation substitutes a multiplier. Root cause: tiers "half … rounded down / twice / unchanged" are ⌊std×r⌋ with r ∈ {0.5, 2, 1}. Evidence: member.extended.yaml P2 rule sentence "The earned-tier upgrade bonus is produced by one of three methods: … receives half of that standard bonus, rounded down …; … receives twice that standard bonus; any other membership receives that standard bonus unchanged." and compute `method_bonus: int(standard_bonus / 2) if … else (standard_bonus * 2 if … else standard_bonus)`. Consequence: P2's computation carries 0 honest method factors (< 1). Affected: P2 `factors[upgrade_bonus_method]`, `effect: method`. Bears on task 0.
- **F-3 SOURCE-POLICY RED — cross-category base clauses on P1's and P6's scored quantity are not overridden.** Symptom: the KB corpus (merged across categories) carries `autoship_evt_rewards_earn` ("Each charged Autoship shipment earns Pals Rewards points on its merchandise subtotal after the Autoship discount at the member's base earn rate multiplied by points_multiplier") and `order_evt_rewards` ("A cancelled, refunded or credited line reverses the points it earned in proportion.") next to P1/P6, which compute the same entries differently. Root cause: P1/P6 `overwrite` can only name member base clauses; the sibling-category clauses governing the same ledger entry remain in force. Consequence demonstrated per task: task 0 (P1: 1367 vs scored chain value) and task 1 (P6: proportional 1019 → balance floor 845 vs P6 value). Affected: P1, P6 overwrite/base_policy_refs; blueprint/products/autoship.yaml `autoship_evt_rewards_earn`, blueprint/products/order.yaml `order_evt_rewards`. Caveat: the KB is not yet published (traceability gate deferred); the finding rests on these base charters being rendered into the shared corpus, which the loader's single-corpus design implies.
- **F-4 observation — enrollment bonus of a first paid-tier enrollment has no booking path.** `member_enrollment_and_trials` (inherited, not overridden) posts `enrollment_bonus_points` "on the first enrollment of that tier"; P2's overwrite removed the enrollment half of the bonus-posting sentence from `member_evt_bonus_points`; no task tool books a `member_bonus_points` row of kind enrollment. Both seeds show the precedent (task 0: enrollment bonus 500 on 2025-11-03, the Plus Monthly purchase; task 1: 1000 on 2024-09-15, the Plus Annual purchase). On task 0 (first Plus Annual, 1000) and task 1 (first Premier, 1500) an agent reading the base sentence finds a bonus due that no tool can write; it changes no scored parameter, so not red.
- O-1 three replacements of one base billing sentence; O-2 subjects outside the blueprint claim; O-3 compute object selection by "latest"/"first active" instead of the rule's specific object; O-4 docstring "Afterwards"/"first"; O-5 P6 state_gate names a column; O-6 P2←P1 state broader than P1 can resolve; O-7 P2 effective date vs base tier_upgrade_effective_days (undeclared, no scored consequence); O-8 P4 term dates vs base "same term dates"; O-9 partial numeric-substitution method tiers; O-10 unreachable fall-through parts.

Per-task conclusions (problem tree, factor weight, unique solution) live only in `task_0.md` and `task_1.md`.

## closing_checklist

Written after both reveals (2026-10-06T06:09Z); the charter-global section above is unchanged by them.

- Per-task files `task_0.md`, `task_1.md` correspond one-to-one with tasks/0.json and tasks/1.json; this file sits alongside; revision 0, no older revision.
- Coverage and scopes: task 0 {P1, P2, P3}, task 1 {P4, P5, P6, P7} — pairwise disjoint, jointly complete over the seven extended policies; GT tools closed per task; uuid8s independent.
- Trees: task 0 — 2 prerequisite problems, 2 value_input edges, user write P3, acyclic, but the root's prerequisite state already holds at the opening (SOURCE-CHAIN RED). Task 1 — 3 prerequisite problems, 2 value_input edges, user write P7, acyclic. Difficulty-wide graph acyclic.
- Factors: every factor of both tasks bears weight against an honest baseline with a definite fall-back different from gold; P2's computation lacks an honest method factor (F-1).
- Gates: not re-run by this audit (the skill audits; the orchestrator owns gate runs); check_traceability still deferred until KB publication.
- **The difficulty does not close.** Open REDs: F-1 (SOURCE-FACTOR, task 0), F-3 (SOURCE-POLICY cross-category, tasks 0 and 1), T0-1/T0-5 (SOURCE-CHAIN, task 0), T0-2 (SOURCE-TASK, task 0).

## revision_2

### charter_global_frozen (revision 2)

- Written before any round-2 task JSON was opened (the revision_2 sections of all three files were on disk by 2026-10-06T09:50Z; round-2 GT was revealed at 09:50:22Z). Auditor: the same independent audit agent as revision 0.
- Hashes re-checked: `member.extended.yaml` 2d6b4d81448b7f5eb08984e7b7fe59f672ab2fd4233f823f0e9cd88f1f088a70, `task_tools.py` f8889f064fb0c02fb41cbf3a89d7d8038fcd75f6bbb3cb0a949e99a6e2506c3e. **Both changed**, so every charter-global section is re-derived in full below; nothing is carried forward by reference. The `blueprint/` files are unchanged (mtimes 2026-10-06T04:34Z, before round 1), and the base copy is still identical (`diff` of the first 1533 lines against blueprint/products/member.yaml → BASE_VERBATIM).
- Gate snapshot r2 (`/tmp/e40views/policy_task/rewards_membership_care/gate_snapshot_r2.txt`): all 7 gates OK / exit 0; check_traceability deferred. Entry conditions met.
- Masked: tasks/0.json and 1.json (round-2 content), the worklog. contamination_disclosure: the auditor read the **round-1** GT of both tasks during revision 0, by protocol after the round-1 freeze. Policy shape and the round-1 figures are therefore known. The round-2 derivations are recomputed from the round-2 charter and the round-2 views, and every number below comes from that recomputation (`/tmp/e40audit_scripts/calc_r2.py`).

### policy_conflict_scan (r2)

- Subjects and triggers: same structure as revision 0. P2, P3 and P7 share `member_tier_change`, with disjoint triggers (spend upgrade / buying from a free tier / Annual → Premier). P6 now governs the reversal for a **cancelled grooming pass** ("When a grooming pass that earned points is cancelled and its unused visits are refunded, a care agent books the points reversal of the pass purchase"), not a retail order line.
- Cross-category read boundaries (finding F-3, re-checked):
  - Autoship: `autoship_evt_rewards_earn` says the shipment earns "at the member's base earn rate multiplied by points_multiplier". P1 now states which rate that is in the missed-earning case: "the missed-earning rate is the member's base earn rate that the Autoship program's own earning rule multiplies by points_multiplier, stated in points per qualifying dollar". It declares this through `overwrite` of the member base earn sentence. The autoship clause leaves the rate to the member programme, and the member charter's declared extended rule now fills it, so the two texts no longer fix different numbers for one entry. **Closed.** The closure rests on P1 claiming the meaning of a term in another category's rule (observation O-11).
  - Order: P6 no longer covers order lines. The order-line reversal of the round-1 conflict is seeded in task 1 as a proportional reversal (1019 points, consistent with `order_evt_rewards`). For a grooming pass, `groom_evt_rewards` says only that "refunds and fees for late cancellation never earn"; `groom_pass_refund` triggers no member event (groom.yaml lines 701–713). No sibling-category clause governs a pass refund's reversal, and the member base clause is declared superseded. **Closed.**
- Repeated replacement of one base billing sentence (O-1): unchanged. P3, P4 and P7 each supersede "A paid tier charges membership_fee_usd on each next_billing_date while auto_renew is true;".
- Claimed scope vs blueprint (O-2): unchanged. `member_points_earn` (P1), `member_points_reverse` (P6) and `member_fee_charge` are outside the blueprint claim.
- Task scopes derived before the reveal: task 0 = {P1, P2, P3}, task 1 = {P4, P5, P6, P7}. Disjoint and jointly complete.

### rule_compute_equivalence (r2)

- Every `compute_basis` value is a verbatim substring of its own rule, and every binding has a basis (script check). Every ladder tier is a rule sentence and a branch of its `decides` binding.
- P1: the multiplier is now read from the shipment's own subscription (`ship_subscription` → `CPARAM(..., autoship_id=ship_subscription)`), matching "the Autoship program the shipment belongs to". The P1 part of O-3 is closed, and the salon-bundle binding has been removed. The tier rate uses the 12-month net spend exactly as the rule sentence states. Rounding is down to a whole point (`int(RND(...,6))`), and the cap is applied last.
- P2: the three method tiers are implemented as stated (`MX(0, standard_bonus - upgrade_points_24m)`; `standard_bonus + int(MX(0, net_spend_12m - tier_threshold))`; `standard_bonus`).
- P4: `activity_courtesy` counts `member_points_earn` rows over 12 months, as the rule says ("points-earning entries dated on the ledger in the last 12 months").
- P6: the pass is selected by `CFIELD('groom','groom_pass_id', status='cancelled')`, i.e. the first cancelled pass. The rule says "a grooming pass that … is cancelled", so with several cancelled passes the compute picks one arbitrarily (O-3 persists for P6). The tier-1 basis test still checks only the latest fee date (O-3). P5 still reads the latest-issued certificate and the latest order refund (O-3 persists).
- P7: `certs_12m` counts issue + reissue rows, matching "certificates issued or reissued".
- P3 is unchanged apart from now relying on the base enrollment-bonus sentence for the tool's new argument (see override_declarations).

### action_binding_and_uuids (r2)

- `(target_tool, computes)` pairs are unique, and the uuid8s are unchanged and independent.
- `buy_plus_tier_1a1727fb` and `upgrade_plus_tier_d51b9d82` gained an `enrollment_bonus_points` argument and book a `member_bonus_points` row of kind enrollment when it is > 0. No extended policy claims this value. It is fixed by the base sentence "The enrollment_bonus_points of the tier joined are posted once, on the first enrollment of that tier." together with P2's restored clause "Enrollment bonuses post with the enrollment that earns them". It is single-valued per tier.
- Tool bodies still check nothing. The docstrings name no other tool and carry no ordering word beyond "Afterwards" (O-4 unchanged).

### prerequisite_graph (r2)

Edges: P2 ← P1 (value_input, net_spend_12m); P3 ← P2 (value_input, loyalty_rate); P5 ← P4 (state_gate, status); P7 ← P4 (value_input, term_fee); P7 ← P6 (value_input, net_spend_12m); **P7 ← P5 (value_input, certs_12m — new)**. P6 now has `prerequisite: []`. The old P6 ← P5 state gate is gone, which makes O-5 moot.
- Acyclic. Every `policy_source` occurs verbatim exactly once in its own rule and is restated in no other rule. All edges are form state with no fallback. Every `resolved_by` equals the depended-on policy's `target_tool`. Each value_input gate names a binding of the blocked compute (`certs_12m` exists in P7). No authoring-viewpoint phrasing. PASS.

### prerequisite_sentences (r2)

| edge | sentence | finding |
|---|---|---|
| P2←P1 | "The earned-tier upgrade bonus is not posted until the rewards ledger carries a points earning for the most recent charged Autoship shipment." | Scope now equals P1's own scope ("most recent charged Autoship shipment"). **O-6 closed.** Single resolving write: P1 |
| P3←P2 | unchanged | single resolving write: P2 |
| P5←P4 | unchanged | single resolving write: P4 |
| P7←P4 | unchanged | single resolving write: P4 |
| P7←P6 | "The upgrade charge is not fixed until every purchase refunded in the last 12 months carries its points reversal on the rewards ledger." | The sentence is **open** ("every purchase refunded"), while `condition` names a closed set ("every order_return_refund and groom_pass_refund"), so the sentence is broader than the condition. Only P6's write (grooming-pass reversal) belongs to this charter. An order-line, Autoship-claim or pharmacy refund lacking its reversal would satisfy the sentence's state through no policy here. In task 1 the only other refund in 12 months (the cat-tree order line) already carries its reversal, so no consequence can be demonstrated. **Observation O-12** (same family as the closed O-6) |
| P7←P5 | "The upgrade charge is fixed only after the rewards ledger carries a reissue of every certificate used on an order returned in the last 12 months." | ordering connective, state form, no tool/id. Single resolving write: P5. PASS |

No rule names a tool, a policy id or a row id, and no undeclared cross-problem order was found. PASS (with O-12).

### override_declarations (r2)

- P1: the member base earn sentence is declared superseded and `replaced_by` is a sentence of P1's rule. Autoship cross-category: see the conflict scan (closed).
- P2: (a) the bonus sentence is declared again, and `replaced_by` now **keeps** the enrollment half ("Enrollment bonuses post with the enrollment that earns them, and the earned-tier upgrade bonus …"), so the dropped branch of F-4 is repaired. (b) The new declaration supersedes "A membership moves up to Pals Rewards Insider or Pals Rewards VIP within tier_upgrade_effective_days" (a verbatim base substring) with P2's "applies that earned tier effective the day it is applied". **O-7 closed.**
- P4: the new declaration supersedes "Paying the overdue fee reinstates the paid tier for the same term dates;" (a verbatim base substring) with "reinstates the paid tier for the term that billing period opened". **O-8 closed.**
- P5, P7: unchanged and declared. P6: the member base reversal sentence is declared superseded, and no sibling clause applies to pass refunds.
- F-4: the enrollment bonus now has a booking path in both customer tools and a surviving rule sentence. **Closed.** One residual reading point is recorded in task 1's file (whether a Premier upgrade counts as "the first enrollment of that tier").

### factor_ladders (r2)

| policy | factor | label | tiers (value or method) | label honest | multi-source | cross_difficulty |
|---|---|---|---|---|---|---|
| P1 | missed_earning_tier_rate | parameter | 12 / 10 / base rate of the tier held | yes | yes (membership tier + ledger spend) | — |
| P1 | missed_earning_apology | parameter | +1.0 / +0.5 / 0 per $ | yes | yes | — |
| P1 | subscription_milestone | parameter | +1.0 / +0.5 / 0 | yes | no | autoship |
| P1 | autoship_streak | parameter | +1.0 / +0.4 / 0 | yes | no | autoship |
| P1 | late_posting_adjustment | method | ×1.25 / +0.5 / as is | yes (multiply vs add vs none) | no | — |
| P2 | upgrade_bonus_method | method | std − Σ 24-month tier-upgrade points (floor 0) / std + ⌊12-month spend − threshold⌋ / std | **yes**: subtracting an aggregate of past bonuses vs adding a spend-overshoot amount vs unchanged. These are three different computations, not one multiplier | no | — |
| P2 | over_achievement, fast_track, cross_program, membership_tenure | parameter | 250/100/0; 200/100/0; 150/60/0; 100/50/0 (ratio high now 1.4) | yes | cross_program yes | autoship (cross_program) |
| P3 | (unchanged six factors) | — | as revision 0 | as revision 0 | salon_credit | autoship, order, groom |
| P4 | past_due_adjustment, renewal_loyalty_rate, first_decline_courtesy, autoship_courtesy, salon_courtesy | as revision 0 | as revision 0 | O-9 persists on past_due tiers 1/2 | renewal, salon | autoship, groom |
| P4 | activity_courtesy (replaces spend_courtesy) | parameter | 3.00 / 1.50 / 0 at 15 / 8 earning entries | yes | no | — |
| P5 | (unchanged five factors) | — | as revision 0 | — | partly | order, autoship |
| P6 | reversal_basis | method | ⌊refund$ × 8⌋ / ⌊refund$ × tier rate⌋ / standard proportional | O-9 persists (tiers 1/2 same form) | yes | — |
| P6 | visit_usage_share | parameter | 0.5 / 0.75 / 1 by visits used (≥2 / 1 / 0) | yes | no (pass + its refund row) | groom |
| P6 | reversal_tenure/spend/age/autoship allowances | parameter | 40/20/0; 30/15/0; 20/10/0; 25/10/0 | yes | no | autoship (last) |
| P7 | as revision 0; redeemer now counts issued + reissued, thresholds 5/3 | — | — | yes | premier_loyalty_rate, salon | groom, autoship |

- Counts: P1 5 (4 parameter + 1 method), P2 5 (4+1), P3 6 (5+1), P4 6 (5+1), P5 5 (4+1), P6 6 (5+1), P7 6 (5+1). Every ladder has 3 or more disjoint tiers stated in the rule. Every fall-through equals the baseline. Baselines are self-sufficient: P1 = standard rate × multiplier with cap; P6 = proportional standard reversal with caps.
- P1 tier-rate ladder: for any one customer the tiers yield different values (Member: 12/10/8; Insider: 12/–/10). The fall-through reuses the held tier's own rate, which is what the business would publish ("post at the tier you hold unless your spend has earned a higher one"). PASS.
- P6 visit-usage share realism: the pass refund already deducts used visits at the single-visit price, and the share reduces the reversal further. This is generous but publishable; no RED.
- **F-1 closed:** P2's method factor now selects three different computations.
- Per-task minimums: task 0 multi-source = P1 tier_rate/apology, P2 cross_program, P3 salon_credit; task 1 multi-source = P4 renewal, P6 basis, P7 loyalty. Cross-difficulty factors exist in both tasks.

### findings (r2, charter-global)

- F-1 (SOURCE-FACTOR RED): **closed**.
- F-3 (SOURCE-POLICY RED, cross-category): **closed** for both the autoship and the order clause (O-11 records the definitional basis of the autoship closure).
- F-4 (observation): **closed**.
- O-3: partly closed (P1 closed; P5 latest certificate/refund, P6 first cancelled pass and latest-fee test, P3/P4/P7 latest-visit and fee-row counts persist). O-5: moot (edge removed). O-6: closed. O-7: closed. O-8: closed.
- O-1, O-2, O-4, O-9, O-10: unchanged, as the reworker stated.
- New observations: O-11 (P1 claims the meaning of the autoship rule's "member's base earn rate"); O-12 (P7←P6 sentence open vs closed condition; only grooming-pass refunds have a resolving write).
- No new charter-global RED.

### closing_checklist (revision 2)

Written after the round-2 reveal (2026-10-06T09:50:22Z); the revision-2 charter-global sections above were on disk before it.

- Files: `_difficulty.md`, `task_0.md`, `task_1.md`. Each holds revision 0 untouched and an appended `revision_2`. They correspond one-to-one with tasks/0.json and tasks/1.json.
- Coverage and scopes: task 0 {P1, P2, P3}, task 1 {P4, P5, P6, P7}. Disjoint and complete. Tools closed per task; uuid8s independent and frozen.
- Trees:
  - Task 0: 2 prerequisite problems, 2 value_input edges, user write P3, every edge unmet at the opening.
  - Task 1: 3 prerequisite problems, 3 value_input edges plus 1 state gate, user write P7, every edge unmet at the opening.
  - The difficulty-wide graph is acyclic.
- Factors: every computation has 4–6 factors (≥ 2 parameter, ≥ 1 honest method). Every factor bears weight against an honest baseline. Every fall-back differs from gold (1367, 500, 59.00, 59.00, 45, 845, 79.86 against 2478, 600, 31.41, 41.77, 78, 811, 42.51).
- Gates: the orchestrator's r2 snapshot shows all 7 green. This audit did not re-run them, and check_traceability remains deferred until KB publication.
- Round-1 item closure:

| item | class | status |
|---|---|---|
| F-1 / T0-3 | SOURCE-FACTOR RED | closed |
| T0-1 | SOURCE-CHAIN RED | closed |
| T0-2 | SOURCE-TASK RED | closed |
| T0-5 | SOURCE-CHAIN RED (proof assertion) | closed |
| F-3 / T0-4 | SOURCE-POLICY RED (autoship) | closed (O-11) |
| F-3 / T1-1 | SOURCE-POLICY RED (order) | closed (task 1 tree restructured onto a grooming-pass refund) |
| F-4 | observation | closed |
| O-3 | observation | partly closed (P1 fixed; P5/P6/P3/P4/P7 object selection persists) |
| O-5 | observation | moot (edge removed) |
| O-6 | observation | closed |
| O-7 | observation | closed |
| O-8 | observation | closed |
| persona hints (both tasks) | observation | closed |
| O-1, O-2, O-4, O-9, O-10 | observation | unchanged (as stated) |
| O-11, O-12, T1-O2 | new observations | open, no demonstrable consequence |

- **All four relationships PASS for both tasks; the difficulty closes at the source layer (revision 2).** The outstanding items are observations only.
