# Policy-task audit — copay_assistance_and_discount_cards / charter-global

## charter_global_frozen

- Scenario: `env/env_0021_retail_pharmacy_chain`, difficulty `copay_assistance_and_discount_cards`, M = 2, revision 1 (no earlier audit of this difficulty existed; `audits/policy_task/` held only sibling difficulties' folders, which were not opened).
- Freeze time: 2026-09-24T18:57Z (written before any task's GT was revealed; nothing below is derived from `evaluation_criteria`, `computations` or any other masked field).
- Auditor: independent policy-task auditor subagent (Claude Opus 5.5); not the instantiation agent; its transcript and scratch material were not read.
- Frozen inputs (sha256, recomputed by the auditor, equal to the brief):
  - `tasks/copay_assistance_and_discount_cards/copay.extended.yaml` = `138b5d03677b08ca87d3c1260d441decf4d312a983076ac59688829b2dfd328e`
  - `tasks/copay_assistance_and_discount_cards/task_tools.py` = `31c033715c2062ff465dd22e66ea3cbe68bc975037d95166fd783df44d027913`
  - masked view task0 = `7e14b438eeb96f77703519366b0c5b63ebefa5613b93064f30d7f972f965384b`, task1 = `5571b6f109b5b7f8806fd9905ef10f08621a0b64840e6c005005df4991f0d84c` (each holds only `task_index`, `frozen_time`, `user_scenario`, `initial_state`).
- Permitted reads: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/copay.yaml`, the extended charter, `task_tools.py`, the two masked views. For the meaning of the restricted compute language (MONTHS/DAYS/XLATEST/CFIELD/`within_months` scoping) the evaluator definitions in `skills/erl-task-instantiate/scripts/check_compute.py` lines 220-400 were read; that file carries no task data and no GT (disclosed here because it sits outside the listed read domain).
- Masked until every task's derivation was frozen: all of `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`; no `tasks/*.json` file was opened or placed in any search domain before the freeze.
- Entry conditions (Step 0): the brief supplies the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0 with their OK lines; check_traceability deferred until the KB is published) and the masked views with hashes. Entry conditions are complete; the auditor did not re-run the gates.

### policy_conflict_scan

Structure of the difficulty's policy surface: the verbatim base section (`copay.extended.yaml` lines 1-1079, byte-identical to `blueprint/products/copay.yaml` apart from one trailing blank line; `diff` shows only `1078a1079 >`) plus seven extended policies forming two disjoint prerequisite trees:

| Tree | Root (agent write) | Prerequisite chain | Tools (owner) |
| --- | --- | --- | --- |
| A (club) | `copay_ext_club_cash_price` | <- `copay_ext_club_renewal_fee` <- `copay_ext_duplicate_fee_refund` | `apply_club_cash_price_c625f91d` (agent) <- `pay_club_renewal_fee_425b5cbe` (user) <- `refund_club_membership_fee_7fa4dd89` (agent) |
| B (copay card) | `copay_ext_card_counter_benefit` | <- `copay_ext_card_period_opening` <- `copay_ext_card_period_closeout` <- `copay_ext_card_paid_fill_reimbursement` | `apply_copay_card_benefit_5e8b0a9f` (agent) <- `open_program_benefit_period_c8eb05d0` (agent) <- `close_program_benefit_period_88a9291d` (agent) <- `submit_copay_card_reimbursement_c6a4b4a1` (user) |

Overlap scan across the seven policies:
- Subjects: tree A writes `copay_discount_applied`, `copay_membership_fee_charged`, `copay_membership_fee_refunded` on a Kestrel Rx Savings Club enrollment; tree B writes `copay_benefit_applied` (two policies: counter benefit for a fill waiting for pickup, reimbursement for a fill already paid in full — disjoint by the fill's state), `copay_benefit_period_closed`, `copay_benefit_period_opened` on a Manufacturer Copay Card. The two `copay_benefit_applied` policies are separated by their own scope sentences ("whose fill is waiting for pickup" vs "a fill ... that the patient already paid in full, the program not having been applied at the counter"); no fill can satisfy both.
- Shared quantities: "fee charges standing" is read by three tree-A policies (club price member-years points, renewal loyalty points, refund courtesy rate) with one definition each ("every fee charge booked less every fee charge refunded"); the three evaluate at different handling times, which the prerequisite edges order. "Benefit dollars left" is defined identically in reimbursement, closeout, opening and counter ("credits of its period-opening entries and benefit reversals less its benefit entries and closing entries"). No two policies reach different conclusions on the same subject at the same moment.
- Time anchors: every "fewer than 12 whole months before today" window is anchored on frozen_time; the refund's courtesy days/months anchor on the second charge's date; reimbursement tenure anchors opened_date -> fill date; opening tenure anchors opened_date -> today. No conflicting anchors.
- Cross-category read boundaries: reads only (rx, coverage, rewards, refill); no extended policy writes outside `copay_enrollments` / `copay_activity` (confirmed in `task_tools.py`).
- Terminal states: tree A leaves the club active with one charge for the current term, the duplicate refunded and one `copay_discount_applied` row; tree B leaves the card active, old period closed, new calendar-year period opened and a counter benefit on the waiting fill. Compatible.
- Scope exclusivity/completeness (pre-reveal expectation, confirmed or refuted at reveal in each task file): the persona of task 0 raises the tree-A root and the persona of task 1 the tree-B root; the two trees share no policy and no tool, so the claimed scopes can be mutually exclusive and jointly cover all seven extended policies.

### rule_compute_equivalence

Check 2, policy by policy. Every compute binding carries a verbatim `compute_basis` quotation located in its own `rule`; sweep back from rule to compute:

- `copay_ext_club_cash_price`: fill_usual/fill_days (`XLATEST ... payment_basis='cash'`) <-> "the patient pay that the fill ledger shows on the patient's latest cash fill"; pickups_12m (`XCOUNT ... within_months=12, event_type='rx_pickup'`, evaluator window `0 <= MONTHS(d, NOW) < 12`) <-> "dated fewer than 12 whole months before today"; generic_rate / member_years_pts / supply_pts ladders <-> the three tier sentences; discounted_price (one combined percentage, one rounding) <-> "first added into one total percentage ... reduced once"; finished_price (90-day programs -2.00, other active program x0.98 rounded, none unchanged) <-> the refill sentence; result (floor 3.00 / cap usual) <-> "The minimum cash price and the usual-price limit are applied to the finished price". Rule sentence "a value-list generic keeps its fixed value price" has no compute branch (it is a scope exclusion) and no record anywhere in `db_schema.json` identifies Kestrel Value Generics membership — see O-3.
- `copay_ext_club_renewal_fee`: every binding quoted; `last_terminated_close = CFIELD('coverage','closed_date', status='terminated')` returns the first terminated record, while the rule says "latest terminated coverage record" — equal only when one terminated record exists (O-4).
- `copay_ext_duplicate_fee_refund`: `second_charge_amount/second_charge_date = LATEST(... copay_membership_fee_charged)` picks the latest charge on the membership, while the rule says "the later-dated of the two charges" of the doubly charged term — equal only while no later term has been charged (O-5). All ladder bindings quoted.
- `copay_ext_card_paid_fill_reimbursement`: all bindings quoted; ordering "first limited ... then taken off ... finally held" implemented as `MX(0, MN(left, MN(pay, limit) - min - withhold))`.
- `copay_ext_card_period_closeout`: all bindings quoted; `close_deductible_12m` sums every paid claim of the customer, rule says "the patient's paid claims" — consistent.
- `copay_ext_card_period_opening`: all bindings quoted; order "plan tier -> term rule rounded -> absorption -> + adherence + tenure" implemented in that order.
- `copay_ext_card_counter_benefit`: all bindings quoted; `counter_plan` is the linked coverage's class, the rule speaks of "a Commercial High-Deductible Health Plan claim" — the claim's plan and the linked plan coincide whenever the card pays after its linked coverage.
- Rounding: every rule says "rounded to the cent half up"; the evaluator's `RND` is Python `round(float, 2)` (not half-up on exact ties). No exact half-cent tie arises on either task's handling-time world (checked in each task file), so this is recorded as O-6 only.
- Factor ladders vs rule: every tier named in each `factors[].ladder` is a sentence of its `rule` and a branch of its `decides` binding, and every branch of those bindings is a stated tier (checked for all 34 factors). No tier lives only in compute.

Result: no rule/compute contradiction with a demonstrable consequence; observations O-3..O-6.

### action_binding_and_uuids

- Seven `(target_tool, computes)` pairs, each claimed by exactly one policy: `apply_club_cash_price_c625f91d/patient_pay_after_usd`, `pay_club_renewal_fee_425b5cbe/amount_usd`, `refund_club_membership_fee_7fa4dd89/amount_usd`, `submit_copay_card_reimbursement_c6a4b4a1/amount_usd`, `close_program_benefit_period_88a9291d/amount_usd`, `open_program_benefit_period_c8eb05d0/amount_usd`, `apply_copay_card_benefit_5e8b0a9f/amount_usd`.
- uuid8 tails `c625f91d, 425b5cbe, 7fa4dd89, c6a4b4a1, 5e8b0a9f, 88a9291d, c8eb05d0`: pairwise distinct, no shared prefix or run, no sequential pattern; consistent with independent generation.
- Docstrings name no other tool and state no position among this difficulty's writes. `apply_copay_card_benefit_5e8b0a9f` says "to bill the patient's copay card after the insurance claim of a fill that has not been paid yet" — an ordering word, but about insurance adjudication (the base stacking order), not about any problem of the tree (O-7). `open_program_benefit_period_c8eb05d0` "to start the program's next benefit period" refers to the period, not to another write.
- No tool body validates a business gate or a prerequisite: every function checks only that the referenced enrollment / fill / claim exists, then books the figures it is given (lines 36-53, 77-91, 117-130, 158-177, 205-224, 246-259, 284-298). Tool layer is prerequisite-blind.
- Subjects/terminal states: each tool writes exactly the event type its policy's `subject` names (`copay_discount_applied`, `copay_membership_fee_charged` with fee_type `annual_renewal`, `copay_membership_fee_refunded`, `copay_benefit_applied` x2, `copay_benefit_period_closed`, `copay_benefit_period_opened`).

### prerequisite_graph

Check 7:
- Every extended policy fills `prerequisite` (`[]` for `copay_ext_duplicate_fee_refund` and `copay_ext_card_paid_fill_reimbursement`).
- Edges: club_cash_price -> club_renewal_fee; club_renewal_fee -> duplicate_fee_refund; card_period_closeout -> card_paid_fill_reimbursement; card_period_opening -> card_period_closeout; card_counter_benefit -> card_period_opening. Every `problem` is an extended id in this file, none is a base id or self. Graph is two chains, acyclic.
- `policy_source` of each edge is verbatim in its own policy's `rule` (club: rule sentence 2; renewal: sentence 2; closeout: sentence 2; opening: sentence 2; counter: sentence 2).
- `form`: four `state`, one `action` (closeout) carrying `fallback_reason`; no state edge carries a fallback.
- `kind` all `value_input`; `gate` names a real compute binding in each policy (`fee_charges_standing`, `renewal_charges_standing`, `close_dollars_left`, `carried_balance`, `counter_dollars_left`).
- `resolved_by` equals the depended-on policy's `target_tool` in all five edges, and the tool body produces the state or value named in `effect` (fee charge +1; refund row naming the charge; benefit row debiting dollars; closing row debiting dollars; opening row crediting dollars and moving `benefit_period_start`).
- `condition` vs sentence strength: club — "fee charge ... whose benefit_period_start equals the enrollment's current benefit_period_start" = "a fee charge for the membership term in which the fill date falls" (the priced fill is the latest cash fill, dated in the current term); renewal — "every ... later of two charges carrying the same benefit_period_start has a refund" = "every second fee charge booked for one earlier membership term carries its refund"; closeout — "every rx_fills entry of the card's prescription dated inside the closing period with payment_basis insurance has a copay_benefit_applied entry" = "every fill of that period paid in full without the program"; opening — closing entry for the period before; counter — opening entry for the calendar year of the claim date and `benefit_period_start` showing it. None strengthened or weakened.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") in any `prerequisite` or `rule`.

Result: PASS.

### prerequisite_sentences

Check 6, per edge (four-point test; single writer; derivation):

1. club_cash_price <- renewal_fee (state): "A club price for a fill is fixed only after the membership fees account carries a fee charge for the membership term in which the fill date falls." Connective "only after"; waited-on thing is a record-visible state (a fee charge row for the term) in finder words ("membership fees charged"); no tool, id or snake_case; strength equals condition. Writers of `copay_membership_fee_charged` in this difficulty: only `pay_club_renewal_fee_425b5cbe`. Derivation: sentence -> the club's `copay_activity` shows no fee charge whose term is the current one -> the only policy whose rule produces a fee charge for "the membership term the membership is in when the automatic renewal charge ... could not be collected" is the renewal-fee policy -> its target tool. Single reading.
2. renewal_fee <- duplicate_fee_refund (state): "The renewal fee for a membership term is not fixed until every second fee charge booked for one earlier membership term carries its refund on the membership fees account." Connective "not ... until"; state = a refund row naming the second charge; single writer of refunds: `refund_club_membership_fee_7fa4dd89`; the duplicate-refund policy's own rule describes exactly that write ("the later-dated of the two charges is the second charge, and it is refunded as a duplicate charge"). Single reading.
3. card_period_opening <- closeout (state): "A new benefit period is not credited until the budget account carries the closing entry of the period before it." Single writer of closing entries: `close_program_benefit_period_88a9291d`. Single reading.
4. card_counter_benefit <- opening (state): "A counter benefit on a claim is fixed only after the budget account carries the opening entry of the benefit period the claim date falls in." Single writer of opening entries: `open_program_benefit_period_c8eb05d0` (the base `copay_activated` trigger also opens a period, but only at activation of a pending enrollment, which an active card is not). Single reading.
5. card_period_closeout <- reimbursement (action): "The closing entry of a benefit period is booked only after the patient has claimed reimbursement for every fill of that period paid in full without the program." Connective "only after"; action named in business words; no tool/id. Fallback test: the stated reason is that a benefit entry on the fill "is also left by a benefit applied at the counter". The counter-benefit policy's own scope is a fill "waiting for pickup", so on a fill already picked up and paid the state "every fill of that period settled by insurance alone carries a benefit entry" can only be brought about by the reimbursement; the fallback is therefore not strictly needed (O-8, observation, as the skill directs).

No rule restates another problem's sentence; no depended-on rule mentions its dependant; no rule states a cross-problem order that grounds no declared edge (the club rule's "A membership whose renewal fee cannot be collected still expires once the renewal grace days pass without a renewal fee charge for the new term" is an expiry rule, not an order between writes). No base sentence is used to ground an edge.

Result: PASS (observation O-8).

### override_declarations

Check 1, sentence by sentence against each `base_policy_refs` entry.

`copay_ext_club_cash_price` (refs stacking, discount_pricing, activation_and_term):
- discount_pricing: "only while ... active status, and only to a fill that is not billed to insurance" — followed. Value-list sentence — followed ("a value-list generic keeps its fixed value price"). "Any other generic ... generic_discount_pct ... brand ... brand_discount_pct" — handled differently for generics; declared (overwrite 1). "never below minimum_cash_price_usd and never above the usual price" — followed. Specialty exclusion, vaccine, household sentences — not touched, inherited.
- activation_and_term: "where that charge cannot be collected, program prices are still honored for renewal_grace_days and the membership then expires" — handled differently; declared (overwrite 2). Other sentences untouched.
- stacking: one program per fill, lowest priority, cash_price_table on cash fills — followed.

`copay_ext_club_renewal_fee` (refs membership_fees, activation_and_term):
- membership_fees S1 "A paid membership charges enrollment_fee_usd at activation and at each renewal, once per term." — declared (overwrite 1). The replacement text speaks only of reducing "the enrollment fee" by points; the superseded sentence's "at activation" and "once per term" content is left without a restatement (O-9).
- **activation_and_term: "A membership whose auto_renew is true renews at expiration for another membership_term_months and charges enrollment_fee_usd again as an annual_renewal" — governs the same scored quantity (the annual_renewal fee for the term) and fixes it at enrollment_fee_usd; the renewal-fee policy sets a different amount and its `overwrite` does not name this sentence (the club-price policy's overwrite supersedes only the clause after the semicolon). Undeclared override -> F-1.**
- membership_fees other sentences (refund window, refund once, duplicate) — not the renewal-fee quantity.

`copay_ext_duplicate_fee_refund` (ref membership_fees):
- S2 (window + no-use eligibility) — declared (overwrite 1), replaced by "refunded as a duplicate charge whatever the fee refund window and whatever discounted fills followed it".
- S3 "A fee is refunded at most once." — followed ("A refund is booked once for a second charge").
- **S4 "A fee outside the window, or after a discounted fill, is not refunded, and cancelling the membership then only stops the next renewal." — decides the same question (is this charge refunded) the opposite way for a duplicate charge followed by discounted fills, and is not named in `overwrite`. Base S5 "A fee charged twice for the same term is refunded as duplicate_charge whatever the window" exempts only the window, not the discounted fills. Undeclared override -> F-2.**
- S5 — followed (refund_reason duplicate_charge).
- Amount: base formula `amount_usd: enrollment_fee_usd` and S2's "refunded in full"; the extended amount (charge + courtesy credit) replaces S2, which is declared.

`copay_ext_card_paid_fill_reimbursement` (refs stacking, benefit_application):
- benefit_application S1 active — followed; S2 paid claim, drug, <= max_days_supply — followed; S3 amount — declared; S4 fill-count cap — inherited; S5 once per fill — inherited; S6 retro window "and the patient is refunded the benefit amount" — followed (the withholding reduces the amount, which is the declared S3 quantity); S7 reversal — untouched.
- stacking: secondary_claim after paid claim — followed.

`copay_ext_card_period_closeout` (ref benefit_period): S2 "A period's dollars belong to that period only ... never carried" — declared. S3 open only when active, S4 opened and closed once each — followed.

`copay_ext_card_period_opening` (ref benefit_period): S1 "opens a benefit period ... crediting annual_benefit_max_usd" — declared. S2 is superseded by the closeout policy (carry-forward), which the opening policy reads as "the carry-forward"; S3/S4 followed.

`copay_ext_card_counter_benefit` (refs stacking, benefit_application): S3 amount — declared; all other sentences followed as for the reimbursement. Stacking "to the patient pay that claim assigned" names the object; the counter policy's benefit base is part of the declared amount sentence.

Anonymous intermediates / 0-1 multipliers / dropped branches: none found beyond F-1, F-2. The dropped "at activation" branch of membership_fees S1 (O-9) touches no task write of this difficulty.

### factor_ladders

Per policy (label as declared; honesty verdict by the auditor):

| Policy | Factor | Label | Tiers | Multi-source | cross_difficulty | Auditor verdict |
| --- | --- | --- | --- | --- | --- | --- |
| club_cash_price | generic_rate_by_rewards_and_pickups | parameter | 35 / 30 / P(25) | yes (rewards membership AND rx pickups) | rewards (not a difficulty category; the rx half is) | honest |
| | member_years_points | parameter | 6 / 4 / 0 | no | — | honest |
| | days_supply_points | parameter | 3 / 1 / 0 | no | rx | honest |
| | refill_program_finish | method | -2.00 flat / x0.98 rounded / unchanged | no | refill (not a difficulty category) | honest method (subtract vs multiply vs identity) |
| club_renewal_fee | renewal_loyalty_points | parameter | 15 / 10 / 0 | no | — | honest |
| | renewal_rewards_level_points | parameter | 10 / 5 / 0 | no | rewards | honest |
| | renewal_coverage_points | parameter | 10 / 5 / 0 | tier 1 two conditions on coverage records | coverage | honest |
| | renewal_pickup_points | parameter | 5 / 2 / 0 | no | rx | honest |
| | club_savings_guarantee | method | subtract whole shortfall / subtract half shortfall (rounded) / subtract nothing | no | — | **mislabelled: every tier is `reduced_fee - k x (fee - savings)` with k in {1, 0.5, 0}; only the fraction changes (F-3)** |
| duplicate_fee_refund | courtesy_credit_method | method | months x rate held to limit / flat 2.00 / none | no | — | honest method |
| | courtesy_month_count | method | whole+1 / whole-1 / whole | no | — | **mislabelled: `whole_months + k`, k in {+1, -1, 0} (F-4)** |
| | courtesy_rate_by_standing_charges | parameter | 0.30 / 0.28 / 0.25 | no | — | honest |
| | courtesy_limit_by_rewards_level | parameter | 6 / 4 / 3 | no | rewards | honest |
| card_paid_fill_reimbursement | reimbursement_limit_by_plan_and_cadence | parameter | 1000 / 900 / P(800) | yes (linked plan AND rx refills) | coverage | honest |
| | standing_benefit_allowance | parameter | 150 / 75 / 0 | no | — | honest |
| | program_tenure_allowance | parameter | 50 / 25 / 0 | no | — | honest |
| | days_supply_coverage_of_limit | method | limit x3 / x2 / x1 | no | rx | **mislabelled: `limit x k`, k in {3, 2, 1} (F-5)** |
| | reimbursement_minimum_pay | parameter | 10 / 7.50 / P(5) | no | coverage | honest |
| | late_claim_withholding | parameter | 40 / 20 / 0 | no | — | honest |
| card_period_closeout | carry_forward_share | parameter | 30% / 15% / 0 | no | — | honest |
| | carry_forward_limit | parameter | 1000 / 600 / 400 | yes (linked plan AND claims' deductible) | coverage | honest |
| | closing_period_length | method | x months/12 rounded / nothing / whole | no | — | honest method (proration vs none vs whole) |
| | expiry_horizon_share | parameter | half / none / all | no | — | honest |
| card_period_opening | annual_maximum_by_plan | parameter | 12000 / 10800 / P(9600) | yes (plan AND claims' deductible) | coverage | honest |
| | card_term_rule | method | half / x months/12 / whole | no | — | honest method (fixed fraction vs proration vs whole) |
| | carry_forward_absorption | method | quarter of carry / all of carry / nothing | no | — | **mislabelled (`carry x k`, k in {0.25, 1}) and the fall-through is not a distinct treatment: its condition is carry = 0, where tier 2's "take all of it" also takes 0 (F-6)** |
| | adherence_credit_by_entries | parameter | 600 / 300 / 0 | no | — | honest |
| | opening_tenure_credit | parameter | 200 / 100 / 0 | no | — | honest |
| card_counter_benefit | deductible_benefit_base | method | pay - 0.5 x ded / pay - ded / pay | no | coverage | **mislabelled (`pay - k x ded`, k in {0.5, 1, 0}) and the fall-through is not a distinct treatment: its condition is ded = 0, where either other tier also yields the whole pay (F-7)** |
| | counter_limit_by_deductible | parameter | 2500 / 1500 / P(800) | yes (linked plan AND the claim's deductible) | coverage | honest |
| | counter_minimum_pay_by_plan | parameter | 0 / 10 / P(5) | no | coverage | honest |
| | cadence_allowance_by_refills | parameter | 100 / 50 / 0 | no | rx | honest |
| | new_year_allowance_by_claim_date | parameter | 300 / 150 / 0 | no | coverage | honest |
| | renewal_allowance_by_approval | parameter | 100 / 50 / 0 | no | coverage | honest |

Structural checks for every factor: 3 tiers, pairwise disjoint as stated; `decides` is an input binding, never `result`; bindings disjoint across factors of the same policy; every tier stated in the rule (condition and value/method) and implemented in the `decides` binding; every fall-through equals the factor's `baseline`.

Counts after the honesty test (a mislabelled `method` is counted as the `parameter` it is; F-6 and F-7 ladders collapse to two real tiers and are struck):

| Policy | Factors declared | param / method declared | Surviving factors | Surviving param / method | Floor (4-6; >=2 / >=1) |
| --- | --- | --- | --- | --- | --- |
| club_cash_price | 4 | 3 / 1 | 4 | 3 / 1 | met |
| club_renewal_fee | 5 | 4 / 1 | 5 | 5 / **0** | **method floor missed (F-3)** |
| duplicate_fee_refund | 4 | 2 / 2 | 4 | 3 / 1 | met |
| card_paid_fill_reimbursement | 6 | 5 / 1 | 6 | 6 / **0** | **method floor missed (F-5)** |
| card_period_closeout | 4 | 3 / 1 | 4 | 3 / 1 | met |
| card_period_opening | 5 | 3 / 2 | 4 | 3 / 1 | met |
| card_counter_benefit | 6 | 5 / 1 | 5 | 5 / **0** | **method floor missed (F-7)** |

Baseline honesty (structure): every `baseline.rule` is a sentence of its `rule` and names the `baseline.params` it uses. In two policies (duplicate_fee_refund and card_period_closeout) the baseline switches a whole branch off ("no courtesy credit", "keeping no carry-forward"), so the baselines of the nested factors under that branch (courtesy months/rate/limit; carry limit, period length, expiry share) are their fall-through tiers rather than anything `baseline.rule` states; this makes the whole-baseline number definite but leaves those factors' individual baselines outside `baseline.rule` (O-10).

Ladder realism (conditions and outcomes that line of business holds): observations only — O-11 lists the ladders whose conditions a retail pharmacy or manufacturer program would not weigh for that quantity (courtesy month count by discounted-fill usage; copay-card counter allowance by prior-authorization recency; "small carry-forward absorbed whole, large one only a quarter"; card late-claim withholding inside its own retro window). None is demonstrated to the RED bar here beyond F-4/F-6/F-7.

Cross-difficulty coverage (per tree): tree A reads rx (`days_supply_points`, `renewal_pickup_points`, the pickup half of `generic_rate_by_rewards_and_pickups`) and coverage (`renewal_coverage_points`); tree B reads coverage and rx. The `cross_difficulty: rewards` / `refill` labels name categories that belong to no difficulty of `blueprint.yaml` (difficulties claim rx, coverage, copay, vax, delivery) — O-12; each tree still has rx/coverage factors.

### findings

- **F-1 — SOURCE-POLICY RED (undeclared override), bears on task 0.** Symptom: two clauses fix the annual renewal fee of a club term. Base `copay_activation_and_term` (listed in the renewal-fee policy's `base_policy_refs`): "A membership whose auto_renew is true renews at expiration for another membership_term_months and charges enrollment_fee_usd again as an annual_renewal". Extended `copay_ext_club_renewal_fee` rule: "The standard renewal fee is the program's enrollment fee ... The loyalty points, the rewards-level points, the coverage points and the pickup points are first added into one total percentage, and the enrollment fee is reduced once by that total percentage ... finished by the club savings guarantee". Root cause: the policy's `overwrite` names only `copay_evt_membership_fees` S1; the parallel activation_and_term sentence is not named (the club-price policy supersedes only the grace clause after its semicolon). The tool the policy binds books `fee_type="annual_renewal"` and its docstring calls the amount "the renewal fee that the automatic renewal could not collect". Consequence: a second reading prices the renewal at enrollment_fee_usd (20.00); demonstrated against task 0's world in `0.md`. Affected: `copay.extended.yaml` `copay_ext_club_renewal_fee.overwrite`; base `copay_activation_and_term` rule.
- **F-2 — SOURCE-POLICY RED (undeclared override), bears on task 0.** Base `copay_evt_membership_fees`: "A fee outside the window, or after a discounted fill, is not refunded" and "A fee charged twice for the same term is refunded as duplicate_charge whatever the window" (window only). Extended `copay_ext_duplicate_fee_refund`: "it is refunded as a duplicate charge whatever the fee refund window and whatever discounted fills followed it". The overwrite names only the eligibility sentence ("A fee is refunded in full only when ..."), not the "is not refunded" sentence. Consequence (demonstrated in `0.md`): where discounted fills followed the duplicate, the base sentence withholds the refund and the whole tree-A chain moves. Affected: `copay_ext_duplicate_fee_refund.overwrite`.
- **F-3 — SOURCE-FACTOR RED (mislabelled effect -> method floor), bears on task 0.** `club_savings_guarantee` tiers are one formula `reduced_fee - k x (last_fee - savings)` with k = 1, 0.5 (rounded), 0: a substituted fraction, i.e. a parameter. It is the renewal-fee computation's only `method` factor, so that computation has 0 honest method factors. Affected: `copay_ext_club_renewal_fee.factors[club_savings_guarantee]`.
- **F-4 — SOURCE-FACTOR RED (mislabelled effect), bears on task 0.** `courtesy_month_count` tiers are `whole_months_stood + k`, k = +1, -1, 0 (rule: "so the courtesy months are the whole months plus one ... less one ... the whole months"). Counts survive (3 parameter / 1 method via `courtesy_credit_method`). Affected: `copay_ext_duplicate_fee_refund.factors[courtesy_month_count]`.
- **F-5 — SOURCE-FACTOR RED (mislabelled effect -> method floor), bears on task 1.** `days_supply_coverage_of_limit` tiers are `limit x k`, k = 3, 2, 1 ("gets three times the limit ... twice the limit ... the limit once"); it is the reimbursement computation's only method factor. Affected: `copay_ext_card_paid_fill_reimbursement.factors[days_supply_coverage_of_limit]`.
- **F-6 — SOURCE-FACTOR RED (unreal ladder / mislabelled), bears on task 1.** `carry_forward_absorption`: tier 1 takes 0.25 x carry, tier 2 takes 1 x carry, fall-through ("no carry-forward takes nothing off") applies only when carry = 0, where tier 2's "takes all of it off" also takes 0.00 — one tier written as two; the remaining two tiers differ only in the fraction. Opening still meets its floors through `card_term_rule`. Affected: `copay_ext_card_period_opening.factors[carry_forward_absorption]`.
- **F-7 — SOURCE-FACTOR RED (unreal ladder / mislabelled -> method floor), bears on task 1.** `deductible_benefit_base`: tiers give pay - 0.5 x ded, pay - ded, and (fall-through, ded = 0) pay — on the fall-through's own domain both other tiers also give the whole pay, so the ladder has two real tiers, and those differ only in the coefficient on the deductible. It is the counter-benefit computation's only method factor. Affected: `copay_ext_card_counter_benefit.factors[deductible_benefit_base]`.

Observations (no demonstrated consequence; not grounds for rework on their own):
- O-3 Kestrel Value Generics membership is referenced by base and by the club-price rule but no table or field in `db_schema.json` records it; an agent cannot prove a generic is (or is not) on the list. Seeded club history prices every generic by percentage.
- O-4 renewal-fee `last_terminated_close` uses first terminated coverage (CFIELD) vs rule's "latest".
- O-5 duplicate-refund `second_charge_*` uses the latest charge on the membership vs the rule's "later-dated of the two charges" of the doubly charged term.
- O-6 compute `RND` is not half-up on exact ties; rule says half up.
- O-7 counter-benefit tool docstring carries "after the insurance claim" (base adjudication order, not a tree order).
- O-8 closeout action-form fallback is not strictly needed (a record-visible state singles out the reimbursement, see prerequisite_sentences item 5).
- O-9 renewal-fee overwrite supersedes the whole of membership_fees S1 ("at activation and at each renewal, once per term") while its replacement restates only the reduced renewal amount.
- O-10 nested factors whose individual baselines are fall-through tiers `baseline.rule` never states (refund courtesy months/rate/limit; closeout limit/period/expiry).
- O-11 ladder-realism doubts listed above.
- O-12 `cross_difficulty` labels `rewards`/`refill` name categories that are not difficulties.

## closing_status (post-reveal, revision 1)

Written after both tasks' `source_gt_comparison`; the charter-global section above was frozen before any reveal and is unchanged.

The difficulty does **not** close: Step 4's closing checklist requires all four relationships to PASS for every task, and they do not.

| Task | Policy self-consistency | Problem tree | Factors | Unique solution | File |
| --- | --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (F-1, F-2) | PASS | SOURCE-FACTOR RED (F-3, F-4) | GT = blind derivation under the extended rules | `0.md` |
| 1 | PASS | PASS | SOURCE-FACTOR RED (F-5, F-6, F-7) | PASS | `1.md` |

Checklist items that do hold (recorded for the next revision):
- Audit files correspond one-to-one with tasks 0 and 1; `_difficulty.md` sits alongside; no earlier revision existed.
- Scopes: task 0 claims {duplicate_fee_refund, club_renewal_fee, club_cash_price} with their 3 tools; task 1 claims {card_paid_fill_reimbursement, card_period_closeout, card_period_opening, card_counter_benefit} with their 4 tools (`charter_scope` of each task); pairwise disjoint, union = all 7 extended policies and all 7 task tools; uuid8s independent (§ action_binding_and_uuids).
- Trees: task 0 has 2 prerequisite problems / 2 value_input edges / one user write; task 1 has 3 / 3 / one user write; the difficulty-wide graph is two disjoint chains, acyclic.
- Every declared factor of every computation bears weight on its task's world and every whole baseline gives a definite number different from gold (both task files).
- Gate re-run on the final form: not performed by this auditor (the artifacts were not changed by this audit; the brief's snapshot is the current state).

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2 of the same difficulty, same auditor. Written before any round-2 task file was opened; nothing below derives from a round-2 GT field. Revision 1 text above is left untouched.
- Inputs (sha256 recomputed, equal to the coordinator's brief): `copay.extended.yaml` = `7533133b645e3573c3ed64e5195c5a0d711c5c9ab5c699842e7c737b74b8c943` (round 1: `138b5d03...328e`, **changed**); `task_tools.py` = `87ef0f13a8c79d1e89556a44a24c62874b28889c7b6214b48c0c12430f4292b5` (round 1: `31c03371...7913`, **changed**); r2 views task0 `7e14b438...384b`, task1 `5571b6f1...984c` (identical to round 1: seeds did not move).
- Because both shared inputs changed, every charter-global section is re-derived in full below (not carried forward).
- Gate snapshot (coordinator, after rework): check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0 with their OK lines. Entry conditions complete.
- Base section: `diff` of `blueprint/products/copay.yaml` against lines 1-1079 of the charter still shows only the trailing blank line (`1078a1079 >`); base copy verbatim.
- Masked until both round-2 task derivations are frozen: all GT fields of `tasks/0.json` and `tasks/1.json` (as in round 1). Contamination: none. The reworker's claims (item ids only) are treated as claims, not evidence.

### what changed (auditor's reading of the round-2 charter and tools against the round-1 text quoted in revision 1)

- `task_tools.py`: only the docstring of `apply_copay_card_benefit_5e8b0a9f` changed ("to bill the patient's copay card on the patient pay of a paid insurance claim for a fill that the patient has not picked up and paid yet"); every function body, signature, owner and uuid8 is unchanged.
- `copay_ext_club_cash_price`: content unchanged (YAML re-flowed only).
- `copay_ext_club_renewal_fee`: second `overwrite` entry added naming `copay_activation_and_term` "A membership whose auto_renew is true renews at expiration for another membership_term_months and charges enrollment_fee_usd again as an annual_renewal", replaced by "A membership whose auto-renewal is on renews at expiration for another membership term, and the fee charged for that renewal is the renewal fee this policy sets." Two rule sentences added ("A paid membership still charges the program's enrollment fee in full at activation, and a fee is charged once per membership term." and the replacement sentence). Savings-guarantee middle tier changed from "half of the shortfall ... is taken off" to "the reduced renewal fee is multiplied by 0.90 and rounded to the cent half up" (param `guarantee_multiplier: 0.9`; compute `RND(reduced_fee * K('guarantee_multiplier'), 2)`).
- `copay_ext_duplicate_fee_refund`: second `overwrite` entry added naming "A fee outside the window, or after a discounted fill, is not refunded, and cancelling the membership then only stops the next renewal."; rule sentence added "A fee charge that is not a second charge for its term is not refunded under this policy, and such a charge is still not refunded outside the fee refund window or after a discounted fill, cancelling the membership then only stopping the next renewal."; `courtesy_month_count` relabelled `parameter`.
- `copay_ext_card_paid_fill_reimbursement`: `days_supply_coverage_of_limit` relabelled `parameter`; `late_claim_withholding` replaced by method `late_claim_handling` (>90 days: amount so far x 0.95 rounded; 31-90: flat 20.00 withheld; <=30: unchanged), now applied after the minimum pay; overwrite `replaced_by` and final ordering sentence updated to match.
- `copay_ext_card_period_closeout`: prerequisite sentence rewritten in state form ("The closing entry of a benefit period is booked only after every fill of the card's prescription dated inside that period and settled by insurance alone carries a benefit entry on the program."), `form: state`, no `fallback_reason`.
- `copay_ext_card_period_opening`: `carry_forward_absorption` rewritten as a `parameter` ladder on the linked plan (Commercial HDHP a quarter / Commercial Copay Plan half / any other plan nothing).
- `copay_ext_card_counter_benefit`: `deductible_benefit_base` replaced by parameter `deductible_left_out_by_plan` (HDHP half the deductible left out / Commercial Copay Plan whole deductible left out / any other plan whole patient pay); `new_year_allowance_by_claim_date` relabelled `method` with its middle tier changed from a flat 150.00 to "5 percent of the limited benefit less the counter minimum pay, rounded to the cent half up".

### policy_conflict_scan (revision 2)

Same two disjoint trees and the same seven `(target_tool, computes)` pairs as revision 1. Overlap scan re-run on the new text: the added renewal sentence ("the fee charged for that renewal is the renewal fee this policy sets") and the rule's scope sentence ("the renewal fee a ... member pays in person ... when the automatic renewal charge ... could not be collected") now both describe the renewal charge; they agree on the amount (this policy's fee) and differ only in how wide the scope is stated (O-13). The duplicate-refund policy is the only one writing refunds; the renewal-fee policy the only one writing fee charges; the club-price policy the only one writing discount rows; tree B unchanged in its write partition. No two policies reach different conclusions on one subject at one moment.

### rule_compute_equivalence (revision 2)

Re-swept every changed binding: renewal `guaranteed_fee` (three tiers match the rule: whole shortfall subtracted / `RND(reduced_fee x 0.90)` / unchanged); reimbursement `reimb_before_late = MN(pay, limit) - min_pay`, `reimb_after_late` (x 0.95 rounded / -20.00 / unchanged), `result = RND(MX(0, MN(left, after_late)))` — matches the rule's order sentence and the overwrite's `replaced_by`; opening `carry_absorbed` (plan-keyed quarter / half / 0) matches; counter `counter_base` (plan-keyed) and `new_year_allowance` (300 flat / `RND((MN(base, limit) - min_pay) x 0.05)` / 0) match. Removed params (`carry_large`, `withhold_late`, `new_year_late`) are no longer referenced. Every factor tier is a rule sentence and a branch of its binding. Unchanged observations O-4, O-5, O-6 still apply (the reworker left them open). Result: PASS.

### action_binding_and_uuids (revision 2)

Unchanged pairs and uuid8s (`c625f91d, 425b5cbe, 7fa4dd89, c6a4b4a1, 5e8b0a9f, 88a9291d, c8eb05d0`). No docstring now carries an ordering word or names another tool: the counter-benefit docstring's "after the insurance claim" is gone (**O-7 closed**). Tool bodies still check only record existence. PASS.

### prerequisite_graph (revision 2)

Same five edges, acyclic; every `policy_source` verbatim in its own rule; all `value_input`, gates exist in compute; `resolved_by` = the depended-on `target_tool`. The closeout edge is now `form: state` with no `fallback_reason` (consistent). PASS.

### prerequisite_sentences (revision 2)

Edges 1-4 unchanged (PASS as in revision 1). Edge 5 (closeout <- reimbursement), now state form: "only after" connective; waited-on state = a benefit entry on every insurance-only fill of the period, named in ledger words; no tool/id; strength equals `condition`. Writers of `copay_benefit_applied`: two tools, but the counter-benefit policy's own scope is "a paid insurance claim ... whose fill is waiting for pickup; the claim is the latest paid insurance claim of the card's prescription", which a fill already settled and picked up inside an ended period never satisfies; the only policy whose rule writes a benefit entry on such a fill is the reimbursement ("a fill of the card's prescription that the patient already paid in full, the program not having been applied at the counter"). Single reading, so the state form holds and **O-8 is closed**. PASS.

### override_declarations (revision 2)

- `copay_ext_club_renewal_fee`: membership_fees S1 declared (as before); activation_and_term "renews ... and charges enrollment_fee_usd again as an annual_renewal" now declared, its replacement sentence present in the rule. The clause after that sentence's semicolon remains superseded by the club-price policy; the two replacements are compatible (renewal charged at this policy's fee; grace-period expiry without that charge). No remaining base sentence sets the annual_renewal amount (the base `formula: amount_usd: enrollment_fee_usd` is not a policy sentence and is replaced by S1's declaration). S1's "at activation" and "once per term" content is now restated in the rule (**O-9 closed**). **F-1 closed.**
- `copay_ext_duplicate_fee_refund`: S2 and S4 both declared; S3 "at most once" followed; S5 "refunded as duplicate_charge whatever the window" followed and widened by the declared text. No remaining base sentence withholds a duplicate's refund after discounted fills. **F-2 closed.** New side-effect: S2 (the positive window refund of an ordinary fee) is now superseded as a whole while the rule restates only its negative half for ordinary charges; an ordinary charge asked back inside the window with no discounted fill has no surviving sentence granting the refund (O-14, dropped branch; bears on no task of this difficulty, both trees refund only a duplicate).
- Tree-B policies: only the amount sentences, which were already declared; `replaced_by` texts updated to the new orders. No undeclared override found.

### factor_ladders (revision 2)

Changed or relabelled factors only (every other row of the revision-1 table stands as it was):

| Policy | Factor | Label | Tiers | Auditor verdict |
| --- | --- | --- | --- | --- |
| club_renewal_fee | club_savings_guarantee | method | subtract the whole shortfall / multiply by 0.90 rounded / unchanged | honest method (subtraction vs multiplication vs identity); tiers distinct — **F-3 closed** |
| duplicate_fee_refund | courtesy_month_count | parameter | whole +1 / -1 / +0 | honest label — **F-4 closed** |
| card_paid_fill_reimbursement | days_supply_coverage_of_limit | parameter | x3 / x2 / x1 | honest label |
| | late_claim_handling | method | x 0.95 rounded / flat -20.00 / unchanged | honest method (proportional vs flat vs none) — **F-5 closed** |
| card_period_opening | carry_forward_absorption | parameter | HDHP 0.25 / Copay Plan 0.50 / other 0 of the carry-forward | honest label; three distinct outcomes on three plan classes, fall-through reachable (e.g. Workers' Compensation linked coverage) — **F-6 closed**; the factor reads the linked coverage record yet is labelled `cross_difficulty: null` (O-12 widened) |
| card_counter_benefit | deductible_left_out_by_plan | parameter | HDHP pay - 0.5 x ded / Copay Plan pay - ded / other pay | honest label; tiers now keyed on plan class, no vacuous fall-through |
| | new_year_allowance_by_claim_date | method | flat 300.00 / 5 % of (limited benefit - minimum pay) rounded / nothing | honest method (flat vs proportional vs none) — **F-7 closed** |

Counts after the honesty test: club_cash_price 4 (3 p / 1 m); club_renewal_fee 5 (4 / 1); duplicate_fee_refund 4 (3 / 1); card_paid_fill_reimbursement 6 (5 / 1); card_period_closeout 4 (3 / 1); card_period_opening 5 (4 / 1); card_counter_benefit 6 (5 / 1). All within 4-6, >=2 parameter, >=1 method. Multi-source per tree unchanged (tree A: generic_rate_by_rewards_and_pickups; tree B: reimbursement limit, carry-forward limit, annual maximum, counter limit). Every fall-through equals its factor's `baseline`. O-10 and O-11 (left open by the reworker) still stand; O-11's "small carry-forward absorbed whole" item is moot after the rewrite, the rest remain.

### findings (revision 2, charter-global)

- F-1, F-2 (SOURCE-POLICY): closed, see override_declarations (revision 2).
- F-3, F-4, F-5, F-6, F-7 (SOURCE-FACTOR): closed, see factor_ladders (revision 2).
- O-7, O-8, O-9: closed. O-3, O-4, O-5, O-6, O-10, O-11, O-12: still open (observations; O-12 widened to `carry_forward_absorption`).
- New observations: **O-13** — the added renewal sentence makes this policy's reduced fee the charge of every auto-renewal, while the seeded club ledger of task 0 carries full 20.00 auto-renewal charges for 2024-09-15 and 2025-09-15 and the rule's scope sentence still speaks only of the in-person fee after an uncollected charge; no scored value reads a historical charge except "the fee most recently charged" (20.00 either way), so no consequence is demonstrated. **O-14** — dropped positive branch of base S2 for ordinary within-window refunds (see override_declarations); no task of this difficulty touches it.
- No new RED found at charter level.

### closing_checklist (revision 2, post-reveal)

Written after both tasks' revision-2 `source_gt_comparison`; the revision-2 charter-global sections above were frozen before the reveal.

| Task | Policy | Tree | Factors | Unique solution | Overall |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

- Audit files `0.md`, `1.md` correspond one-to-one with the tasks; `_difficulty.md` alongside; revision 1 preserved verbatim, revision 2 appended in each file; every revision-2 comparison carries a PASS.
- The seven extended policies are fully covered; scopes pairwise disjoint (task 0: duplicate refund, renewal fee, club price; task 1: reimbursement, closeout, opening, counter benefit), each spanning its whole tree; task tools and GT closed; each of the seven task tools has an independent, frozen uuid8.
- Trees: task 0 has 2 prerequisite problems with 2 value_input edges, task 1 has 3 with 3; each has one `owner=user` write handed over by the agent; the difficulty-wide prerequisite graph is two disjoint chains, acyclic.
- Every computation declares a self-sufficient baseline and 4-6 factors with >=2 parameter and >=1 honest method; per task >=1 multi-source and >=1 cross-difficulty factor reading seeded rows; every ladder has three distinct tiers stated in its rule; every factor bears weight on its task's world, and each whole baseline gives a definite number different from gold.
- Instantiation-stage gates on the final form: the coordinator's post-rework snapshot (all seven rc=0 with their OK lines) is the re-run on the final form; this audit changed no artifact, so it was not re-run by the auditor.
- Open observations carried (not grounds for rework on their own): O-3, O-4, O-5, O-6, O-10, O-11, O-12, O-13, O-14.

The difficulty passes the source-layer policy-task audit at revision 2.
