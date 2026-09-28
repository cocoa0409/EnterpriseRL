# Policy-task audit — member_cost_sharing_and_renewal / charter-global

## charter_global_frozen

- Freeze time: 2026-09-24T18:07:31Z (file mtime; round 1). Auditor: independent audit agent (erl-task-policy-audit), not the author of the artifacts.
- Frozen inputs:
  - `tasks/member_cost_sharing_and_renewal/plan.extended.yaml`: sha256 `2105a00d9ac958971d91f9e9d7fe9b993499b83237b00b10dfc8f9b0cf02172c`. Matches the brief.
  - `tasks/member_cost_sharing_and_renewal/task_tools.py`: sha256 `7c4adf96924f37cf40f530d3b2aca3d87c0787fb9618cd1155f8a6cee0b5ccd0`. Matches the brief.
  - `blueprint/blueprint.yaml`, `blueprint/products/plan.yaml` (plus the other product charters, read only as cross-category holding/ledger contracts), `blueprint/db_schema.json` (structure).
  - The erlbench DSL evaluator: `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, `MONTHS`, `_within`, `RND`) and `erlbench/scoring.py`. The scoring compares the final DB hashes exactly.
- Permitted fields: the charter (base + `extended_policies`), the tool contracts and bodies, and the masked views (`frozen_time`, `user_scenario`, `initial_state`) for the per-task files only.
- Masked, unread at the time of writing: every task JSON under `tasks/member_cost_sharing_and_renewal/tasks/`, `worklog.md` of this difficulty, all `__pycache__`, `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure` and `db_closure*`.
- Entry conditions (Step 0): the brief supplies the gate snapshot. `check_extended`, `check_task_tools`, `replay_tasks`, `check_solvability`, `check_compute`, `check_grounding` and `check_cross_fire` all returned rc=0. `check_traceability` is deferred to after the KB is published, as the brief states. It also supplies the masked views with their hashes, which I re-verified (0.json `60cb47c1…`, 1.json `fc22dabd…`). The input is complete.
- This section was written from the charter, the schema and the tool contracts alone. It contains nothing derived from a revealed GT.

### policy_conflict_scan

- **Base copy.** The base copy is verbatim. A structural diff shows every top-level key of `products/plan.yaml` identical in `plan.extended.yaml`: category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures and all 17 base policies.
- **Extended policies (7).**

  | Extended policy | Subject | Target tool | Owner | Computes |
  | --- | --- | --- | --- | --- |
  | plan_ext_over_cap_refund | plan_cost_share_refund | book_over_cap_refund_b068d625 | agent | refund_amount |
  | plan_ext_past_due_premium_payment | plan_premium_paid | pay_past_due_premium_fdc43b6b | user | payment_amount |
  | plan_ext_own_pcp_visit_rerating | plan_claim_adjusted | book_own_pcp_visit_rerating_ea94b99c | agent | reversal_amount |
  | plan_ext_office_visit_preventive_rerating | plan_claim_adjusted | book_office_visit_rerating_0e97c2c0 | agent | reversal_amount |
  | plan_ext_lockout_balance_payment | plan_premium_paid | pay_lockout_premium_balance_44198c5a | user | payment_amount |
  | plan_ext_therapy_course_rerating | plan_claim_adjusted | book_therapy_course_rerating_7ffa3e71 | agent | reversal_amount |
  | plan_ext_ambulance_transport_rerating | plan_claim_adjusted | book_ambulance_transport_rerating_8b982fa6 | agent | reversal_amount |
- **Overlapping subjects.**
  - Four policies share `plan_claim_adjusted`. Their claim sets are disjoint by construction:
    - own-PCP re-rating: `service_category=specialist_visit` billed by the current or previous PCP NPI.
    - office re-rating: `pcp_visit` visits from the PCP visit log.
    - therapy course re-rating: `outpatient_hospital` billed by the servicing NPI of the approved rehabilitation authorization.
    - ambulance re-rating: `service_category=ambulance`.

    No claim category is claimed by two of them. The only overlap is a PCP-billed claim logged in `pcp_visits` whose category is `specialist_visit`. The office rule restricts itself to "bill under the primary care visit copay category", so the overlap is excluded.
  - Two policies share `plan_premium_paid`. past-due premium payment applies to an open membership ("the most recently billed coverage month once that month's due date has passed"). Lockout balance payment applies to a membership that ended for non-payment ("to re-enroll in the category while the lockout runs"). The triggers are disjoint by membership status.
- **Time anchors.** Every window is "N months counted back from the review date, the review month included" (over-cap, lockout, re-ratings) or "N months before the review date" (rewards). The clock is `frozen_time`. The DSL convention is examined under rule_compute_equivalence.
- **Cross-category read boundaries.** Every `cross_category` entry names only reads of holdings/ledgers the product charters define: auth `auth_authorizations`, care `care_enrollments`/`care_activities`, rx `rx_fills`, ride `ride_benefits`/`ride_trips`, pcp `pcp_assignments`/`pcp_visits`. No policy writes outside `plan_*`, and every tool body writes only `plan_claims`, `plan_premiums` or `plan_memberships.premium_balance`.
- **Scope exclusivity and completeness.** The `prerequisite` graph has exactly two weakly connected components:
  - A = {over_cap_refund (root) ← past_due_premium_payment, own_pcp_visit_rerating, office_visit_preventive_rerating}.
  - B = {lockout_balance_payment (root) ← therapy_course_rerating, ambulance_transport_rerating}.

  With M=2 and one tree per task, the two scopes are disjoint and jointly cover all 7 extended policies. That assignment is only possible if task 0 holds tree A and task 1 holds tree B. Each task file confirms this from its own `user_scenario`.

### rule_compute_equivalence

I checked every binding's `compute_basis` quotation against the `rule` text. Each tier the `factors[].ladder` names is a sentence of its rule and a branch of its `decides` binding, and conversely. I found no tier present in only one face. Divergences found:

1. **Rounding convention (all 7 policies; `RND`).** The rules say "rounded to the cent" and name no mode. The tool Args say "rounded half up to the cent" (for example `refund_amount`). The compute `RND` is Python `round(float(x), 2)` on a binary float. At an exact half-cent tie the two disagree whenever the float lies just below the tie. The decimal value 602.775 is an example: `round(602.775, 2)` = 602.77, while half-up gives 602.78.
   - Whether this has a consequence depends on the world, and it is demonstrated in `0.md`.
   - The charter finding is that the rule's rounding point and mode ("rounded to the cent", read with the tool's "half up") are not what `RND` implements on tie values. See findings F2.
2. **Window counting convention (every `within_months`).**
   - The rule reads "the number of months … counted back from the review date, the review month included". Its natural reading is calendar months: the review month plus the N−1 preceding months, starting on the 1st.
   - The DSL `_within` keeps a date d when `0 <= MONTHS(d, NOW) < N`. `MONTHS` subtracts one when NOW's day-of-month is below d's. That is a rolling window starting the day after NOW−N months.
   - Rows dated between (NOW−N months, +1 day) and the 1st of the calendar start month are counted by the compute and not by the calendar reading.
   - `months_since_start: MONTHS(coverage_start_date, NOW)+1` ("the whole months from the coverage start month through the review month, both counted") undercounts by one when the coverage-start day-of-month exceeds NOW's day-of-month. The same applies to `cur_since_effective` / `cur_from` / `start_back`, which are driven by `effective_date` / `start_date`.
   - Whether this has a consequence is world-specific. Each task file checks the gap rows. See findings F3.
3. **Batch membership versus log-wide counts (own-PCP re-rating).**
   - The rule: "A batch visit the primary care visit record logs as a telehealth follow-up re-rates …" and "A batch visit the record logs as the initial health appointment re-rates …".
   - The compute: `tele_visits: XCOUNT('pcp','pcp_visits', within_months=rwin, visit_type='follow_up', visit_mode='telehealth')` and `iha_visits: XCOUNT(… visit_type='initial_health_appointment')`. Both count every such logged visit of the customer in the window, whether or not its claim is in the batch.
   - A telehealth follow-up or IHA billed under `pcp_visit`, or by a non-batch provider, would still be subtracted from the batch at the tier copay.
   - This is an observation in this difficulty: task 0 is the only task that claims this policy, and both of its logged visits are batch claims (see `0.md`). See findings F7.
4. **Office re-rating vaccine factor.** The rule: "An office visit on a day the pharmacy benefit shows a vaccine dispensed …". The compute: `vaccine_days: XCOUNT(rx_fills … copay_exempt_class='vaccines')`. It counts vaccine fills without checking that an office visit falls on that day. This is an observation. Task 0's vaccine day (2026-06-16) does coincide with a PCP office visit.
5. **Two sentences whose own wording contradicts their compute.**
   - over-cap: "the member copays on medical claims whose service date falls in the counting window". `medical_net` is membership-scoped (`SUM('plan_claims', …)` filters on the target `membership_id`). A member with an earlier membership in the window would see only one of them counted. This is checked per task. In task 0 the earlier membership is Children's Medicaid, whose claims all carry 0.00 copay, so it has no effect.
   - Otherwise the sweep back found no compute basis invented beyond its rule.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (table above). The seven target tools are pairwise distinct.
- **Docstrings.** No docstring states a sequence position, names another tool, or uses an ordering connective about another action. I grepped for before/after/first/then/once/until/prior. The only hits are "rounded half up to the cent before it is passed" (argument formatting) and "at once" (immediacy of the receipt). Neither is an ordering between actions.
- **Tool bodies.** Every tool performs one create (plus the one `premium_balance` update for the two payment tools), judges no eligibility, raises on nothing business-related and returns no hint. In particular:
  - `pay_past_due_premium` sets `premium_balance = max(0, balance − billed(coverage_month))` "whatever amount was paid".
  - `pay_lockout_premium_balance` sets `premium_balance = 0.0` unconditionally.
  - The re-rating tools copy `service_date`, `service_category`, `provider_npi` and `cost_share_period` from the named claim and stamp `booked_date = today`.
- **UUID8s.** The tails are b068d625, fdc43b6b, ea94b99c, 0e97c2c0, 44198c5a, 7ffa3e71 and 8b982fa6. None is reused, none shares a prefix or suffix with another, and none is sequential or adjacent. They are consistent with independent generation.

### prerequisite_graph

- `prerequisite` is filled on all 7 policies. It is `[]` on the five leaves: past_due, own_pcp, office, therapy, ambulance.
- **Edges.**

  | Edge | kind | gate | form | resolved_by |
  | --- | --- | --- | --- | --- |
  | over_cap → past_due_premium_payment | value_input | premium_counted | state | pay_past_due_premium_fdc43b6b |
  | over_cap → own_pcp_visit_rerating | value_input | medical_net | state | book_own_pcp_visit_rerating_ea94b99c |
  | over_cap → office_visit_preventive_rerating | value_input | medical_net | state | book_office_visit_rerating_0e97c2c0 |
  | lockout → therapy_course_rerating | value_input | credit_offset | state | book_therapy_course_rerating_7ffa3e71 |
  | lockout → ambulance_transport_rerating | value_input | credit_offset | state | book_ambulance_transport_rerating_8b982fa6 |
- Every `problem` is another extended policy id in this file, never a base policy and never self. The graph is acyclic: two stars of depth 1.
- Every `gate` binding exists in the blocked policy's compute (`premium_counted`, `medical_net`, `credit_offset`). Each `resolved_by` is the depended-on policy's `target_tool`.
- **Effects are real.**
  - The payment tool zeroes `premium_balance` and adds a `plan_premium_paid` row dated today. This moves `premium_counted` from tier "paid less balance" to tier "paid".
  - The re-rating tools add a `plan_claim_adjusted` row with a negative cost share. The row keeps the original `service_date`, so it enters `medical_net`, and it has `booked_date` = today, so it enters the lockout `reversals_booked`.
- Every edge's `policy_source` is quoted verbatim from its own blocked rule (located below). All five are `form: state` with no `fallback_reason`, as required. The `condition` texts are no stronger or weaker than the sentences (see below).
- **Phrasing.** No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` block.

### prerequisite_sentences

The four-point test on each edge sentence:

| Edge | Sentence (verbatim, own rule) | Connective | Waited-on state (record-visible) | Tool/id/snake_case | Strength vs condition |
| --- | --- | --- | --- | --- | --- |
| over_cap ← past_due | "On a membership that is still open, the over-cap refund is fixed only after the premium balance on the membership stands at zero." | only after | membership premium balance = 0 | none | same (balance 0.00) |
| over_cap ← own_pcp | "The over-cap refund is fixed only after the visits the member's own primary care provider billed under the specialist visit copay in the counting window carry their re-rating adjustment entry." | only after | an adjustment entry on those specialist-copay PCP visits | none | same (one entry against those visits) |
| over_cap ← office | "The over-cap refund is not worked out until the office visits the member's primary care providers billed under the primary care visit copay in the counting window carry their preventive re-rating adjustment entry." | not … until | an adjustment entry on those PCP office visits | none | same |
| lockout ← therapy | "The lockout balance is not accepted until the visits of the member's approved therapy course carry their course re-rating adjustment entry." | not … until | an adjustment entry on the approved course's visits | none | same |
| lockout ← ambulance | "The lockout balance is fixed only after the ambulance claims under review carry their ambulance re-rating adjustment entry." | only after | an adjustment entry on the ambulance claims under review | none | same |

- **Exactly one write per state.**
  - Premium balance zero on an *open* membership: only `pay_past_due_premium` brings it about. `pay_lockout_premium_balance` also zeroes the balance, but its policy is for "a membership that ended", so the sentence's "still open" excludes it. No waiver tool exists in this difficulty.
  - Each "… adjustment entry" state names the kind of visits/claims, and exactly one re-rating policy's rule describes an entry on those visits: specialist-copay PCP visits → own-PCP re-rating; PCP office visits under the primary care copay → office re-rating; approved therapy course → course re-rating; ambulance claims → ambulance re-rating. There is one reading.
- **Derivation from sentence + records + depended-on rule.**
  - Balance: `plan_memberships.premium_balance` > 0 → the past-due policy "The family's phone payment is made for the most recently billed coverage month once that month's due date has passed, and it settles that month alone." → the family's payment (owner=user).
  - Specialist-copay PCP visits: the claim ledger holds paid `specialist_visit` claims with `provider_npi` = the assignment's `provider_npi`, and there is no adjustment row → the own-PCP rule "The re-rating is booked as one adjustment entry that names the most recently serviced claim of the batch …".
  - Office, therapy and ambulance follow the same way from their own rules' final "booked as one adjustment entry …" sentences.
- **No second wording.** No blocked rule carries a second wording of an edge, a tool name, or another policy id. No depended-on rule restates the sentence.
- **Undeclared orders.** No rule states a cross-problem order that grounds no declared edge. The base rules carry no cross-problem order sentence on which a tree rests.
- **Observation (wording scope).**
  - The over_cap ← own_pcp sentence says "the member's own primary care provider" (singular, current) and "in the counting window". The own-PCP batch, under its first tier, also holds the *previous* (superseded) provider's visits, over the *re-rating* window of 12 months.
  - For a category with a 3-month counting window, the sentence's visit set (3 months) is narrower than the batch (12 months).
  - The sentence still names the state unambiguously (an adjustment entry on those visits), so this is not a second reading of *which write*. It is recorded as an observation.

### override_declarations

I checked each `base_policy_refs` entry sentence by sentence.

**plan_ext_over_cap_refund** (refs plan_evt_cost_share_cap, plan_evt_copay, plan_evt_premium):

| Base sentence | Treatment |
| --- | --- |
| cap S1 "Total member cost sharing in one cap period may not exceed … on file on the first day of the period, rounded to the cent." | Declared superseded → "monthly household income on file × cap-period months × cap percent / 100". The factors further vary cap percent and cap months inside the rule. Declared. |
| cap S2 "Cost sharing counted toward the cap is plan_msr_period_cost_share …" | Declared superseded → rolling counting window. The counted total also adds premium (new quantity), which falls under the superseded counting clause. |
| cap S3 "Once the cap is reached, later claims … no copay." | Not the scored quantity. Followed. |
| cap S4 (refund of the crossing claim's excess, booked_date order) | Declared superseded → one entry against the most recently booked copay claim. |
| cap S5 "refunded at most once per cap period …" | Followed (dedup inherited). |
| cap S6 "due within cost_share_refund_days … the cap never carries over from one period to the next." | Not named. The rolling window mixes two base periods. For a CHIP member (calendar-year base period) the window includes the prior year's copays while the refund carries the current period. The declared window replacement governs the counted total, so the merged reading is unique. Observation F9. |
| copay "… never larger than the room left under the member's aggregate cap" | Booking-time rule. Not the scored quantity. |
| premium sentences | Not about cost-share counting. No conflict. |

**plan_ext_past_due_premium_payment** (ref plan_evt_premium):
- Declared superseded: oldest-month-first application → "most recently billed coverage month … settles that month alone".
- "billed … at the ladder row whose income band contains income_pct_fpl" governs billing, not the payment amount. The month-rate tiers are consistent with it and with plan_evt_income_change (no higher band during continuous eligibility).
- **Observation F5.** "the continuous eligibility that began with the coverage start date" narrows base plan_continuous_eligibility ("from the coverage start date or the latest renewal approval, whichever is later"). That base policy is not in base_policy_refs. It matters only where a renewal approval exists.
- **Observation F6.** The payment amount can be below the billed amount and still "settles that month". Base plan_evt_premium_waiver says "A waiver always covers the whole billed amount of the month, never part of it". A reward-reduced payment is not a waiver, so there is no demonstrable conflict.

**plan_ext_own_pcp_visit_rerating / plan_ext_office_visit_preventive_rerating / plan_ext_therapy_course_rerating / plan_ext_ambulance_transport_rerating** (refs plan_evt_claim_adjustment, plan_evt_copay):
- **Declared** (each of the four): claim_adjustment S1 (whole reversal of one original claim → one batch entry against the most recent claim of the batch) and the adjustment-reason sentence (→ reason none).
- **Followed:** claim_adjustment "Only an original claim whose adjudication_status is paid can be adjusted". Every batch is "paid" claims, and the named claim is a paid booked claim. Also followed: "no later than claim_adjustment_window_days (365) after the original claim's booked date", since every batch window is ≤ 12 months.
- **Undeclared:** claim_adjustment "An original claim is adjusted at most once, so no adjustment is booked when a plan_claim_adjusted row already references its claim number". The batch entry names one claim but reverses copay on others. Per world, no pre-existing adjustment references a named claim (checked per task).
- **Undeclared — plan_evt_copay** (cited by all four, named by none). Two base sentences govern the copay a paid claim carries:
  - "Each paid claim is assessed the copay the member's category sets for the claim's service_category, once per claim".
  - "Preventive, family planning and true-emergency claims carry no copay in any category."

  The four re-rating rules set the copay a paid claim is re-rated to at amounts that are neither the category's schedule for any service category nor zero for preventive care:
  - own-PCP: medical-home $2.00, health-home $0.00, telehealth follow-up $0.00/$1.00, IHA $0.00/$1.00, against a CHIP primary care copay of $5.00.
  - office: telehealth well-child $1.00/$2.50, same-day sick $0.00/$2.50, vaccine visit $0.00/$1.00, coordinated follow-up $0.00/$1.00. Under the schedule factor, in-person well-child visits beyond the one counted "keep the copay booked on it".
  - therapy: rehab $2.00, speech $1.00, extension $0.00/$1.00, minus the transport and care-plan credits.
  - ambulance: stretcher $0.00, wheelchair $5.00, minus the discharge, distance and care-tier credits.

  Most sharply, the office rule re-rates a *well-child visit the log records as a telehealth visit*, which by its own premise the visit record shows to be preventive care, at a nonzero copay. Base says preventive care carries none "in any category". This is **SOURCE-POLICY RED F1**. Each task file demonstrates the second answer on its own world.

**plan_ext_lockout_balance_payment** (refs plan_evt_premium, plan_evt_cost_share_cap):
- Declared: oldest-first application → one payment settling every billed month; "re-enroll … only by paying the past-due balance in full" → the lockout balance formula with offsets and reliefs.
- Not in refs but touched: plan_evt_premium_waiver "Waiver and payment are mutually exclusive for one coverage month". Owed months exclude waived months, so this is consistent.
- The cap policy's refund sentences are read, not changed (offsets count booked refunds).

### factor_ladders

This covers structure only. Whether each factor bears weight is in the task files.

**plan_ext_over_cap_refund** — 6 factors (parameter 4, method 2).

| Factor | Label | Tiers | Multi-source | Cross-difficulty |
| --- | --- | --- | --- | --- |
| cap_percent_by_income_and_authorized_care | parameter | 3 | income AND auth | auth |
| cap_months_by_coverage_span | method | 3 | single | — |
| counted_premium_by_premium_standing | method | 3 | category bills AND balance | — |
| admission_relief_credit | parameter | 3 | stays AND care episode | — (care is not a difficulty) |
| medication_relief_credit | parameter | 3 | refills AND rejects | rx |
| travel_relief_credit | parameter | 3 | trips AND LOS | ride |

- Tier values are pairwise distinct: 2.5/4.0/cat 5.0; 150/75/0; 60/30/0; 50/25/0. The methods are distinct.
- Every tier is in the rule and in the `decides` binding. The baseline.rule is self-sufficient: window, counted total without premium, cap at category percent × period months, refund, never below zero. Every factor's fall-through equals the baseline.
- **Realism observations.**
  - The low-income band top of 185% FPL divides customers only in CHIP Kids (148–235) and Pregnancy Care (≤200). For categories with an income limit ≤138/100 it holds of every customer. Task-level check.
  - The counted premium tier "premiums paid … less that outstanding balance" is an unusual netting. On an open membership it is unreachable at the gold moment, because the prerequisite zeroes the balance. Observation F8.

**plan_ext_past_due_premium_payment** — 6 factors (parameter 4, method 2).

| Factor | Label | Tiers | Multi-source | Cross-difficulty |
| --- | --- | --- | --- | --- |
| month_rate_under_continuous_eligibility | method | 3 | CE AND bill>paid (AND income) | — |
| well_child_reward | parameter | 3 | visits AND practice | pcp |
| refill_reward | parameter | 3 | fills AND rejects | rx |
| care_reward | parameter | 3 | episode AND reached | — |
| steady_payer_reward | parameter | 3 | count AND channel mix | — |
| reward_stacking | method | 3 | practice AND episode | — |

- The values are distinct.
- The month_rate "method" tiers select a source value (last paid / constant band-one / billed). Tier 2 is a constant, so the label is borderline but acceptable, since each tier selects a different derivation.
- The baseline.rule ("month rate is the amount billed … With no Healthy Kids reward earned, the reward total is zero") is self-sufficient.
- **Observation.** The steady-payer ladder's channel-mix condition (portal ≥ phone) is a weak business discriminator, though paperless/autopay discounts exist in the trade.

**plan_ext_own_pcp_visit_rerating** — 4 factors (parameter 3, method 1).

| Factor | Label | Tiers | Multi-source | Cross-difficulty |
| --- | --- | --- | --- | --- |
| batch_scope_by_assignment_history | method | 3 | superseded AND member_selected | pcp |
| rerated_copay_by_practice_type | parameter | 3 | single | pcp |
| telehealth_followup_copay | parameter | 3 | logged AND practice | pcp |
| initial_appointment_copay | parameter | 3 | logged AND days | pcp |

- **Observation F10.** The IHA ladder's tier 1 ($0.00) and its fall-through (practice_copay) select the same value when the practice is a Health Home Lead Provider ($0.00). The fall-through only applies when no IHA is logged, so the value is inert, but the ladder is not distinct in all worlds.
- The baseline.rule is self-sufficient: batch over the whole window, re-rated at the category PCP copay.

**plan_ext_office_visit_preventive_rerating** — 6 factors (parameter 4, method 2).

| Factor | Label | Tiers | Cross-difficulty |
| --- | --- | --- | --- |
| visit_log_scope_by_assignment_history | method | 3 | pcp |
| well_child_schedule | method | 3 | — |
| telehealth_well_child_copay | parameter | 3 | pcp |
| same_day_sick_visit_copay | parameter | 3 | pcp |
| immunization_visit_copay | parameter | 3 | rx |
| coordinated_followup_copay | parameter | 3 | — |

- Multi-source: schedule (no episode AND superseded), telehealth, same-day, vaccine and follow-up.
- **SOURCE-FACTOR realism, bound up with F1.**
  - The telehealth well-child tiers ($1.00 medical-home / $2.50 other) put a copay on well-child (preventive) care. No CHIP/Medicaid plan publishes that, since well-baby/well-child care is cost-sharing-exempt, and base plan_evt_copay says so for this charter.
  - The vaccine-visit other-practice tier ($1.00) is the same kind of outcome.
  - The schedule factor's fall-through ("one in-person well-child visit in the window counts"; the others "keep the copay booked on it") charges a copay on further well-child visits.
  - These are recorded under F1. The consequence is demonstrated in `0.md`.

**plan_ext_lockout_balance_payment** — 5 factors (parameter 3, method 2).

| Factor | Label | Tiers as stated | Cross-difficulty |
| --- | --- | --- | --- |
| void_bill_by_termination | method | 3 | — |
| lockout_month_rate_by_income_band | parameter | 3 | — |
| credit_offset_on_lockout | method | 3 | — |
| medical_need_relief | parameter | 3 | auth |
| first_default_relief | parameter | 3 | — |

**SOURCE-FACTOR RED F4 (unreal ladder).** This write is reachable only for a membership that ended for premium non-payment:
- Its own rule: "The lockout balance is what the family pays … to re-enroll in the category while the lockout runs". The lockout exists only after non-payment termination, per base plan_evt_premium "After a premium_nonpayment termination the family may re-enroll in the category within premium_lockout_days only by paying the past-due balance in full". The tool docstring says "a CHIP membership that ended for unpaid premiums".

Therefore:
- void_bill tier 2 "ended for any other reason" is satisfied by no customer who reaches this write.
- credit_offset's conjunct "ended for premium non-payment", taken on its own, holds of every customer who reaches this write. Its fall-through "otherwise nothing is offset", which is the factor's baseline `credit_offset: '0'`, is a tier no customer at this write can be on. The baseline is therefore a straw man, a treatment the business never applies to anyone paying a lockout balance.

Counting only tiers that pass: void_bill has 2 reachable tiers and credit_offset has 2. Both fall below the three-tier floor, which leaves the policy with **0 surviving `method` factors** (floor 1) and 3 factors in all (floor 4). The demonstration against task 1's world is in `1.md`.

**plan_ext_therapy_course_rerating** — 6 factors (parameter 5, method 1).

| Factor | Label | Tiers | Cross-difficulty |
| --- | --- | --- | --- |
| course_scope_by_authorization_dates | method | 3 | auth |
| course_visit_copay_by_discipline | parameter | 3 | auth |
| course_intake_visits | parameter | 3 | auth |
| extension_visit_copay | parameter | 3 | auth |
| therapy_transport_credit | parameter | 3 | ride |
| therapy_care_plan_credit | parameter | 3 | — |

- The values are distinct.
- **Observation.** The intake factor's fall-through "where no approved course exists" coincides with the situation in which the course batch cannot be defined at all (no servicing NPI). Its fall-through is therefore reachable only where the policy has no object.

**plan_ext_ambulance_transport_rerating** — 5 factors (parameter 4, method 1).

| Factor | Label | Tiers | Cross-difficulty |
| --- | --- | --- | --- |
| ambulance_review_reach | method | 3 | ride |
| ambulance_copay_by_level_of_service | parameter | 3 | ride |
| discharge_transport_credit | parameter | 3 | ride |
| long_distance_transport_credit | parameter | 3 | ride |
| care_tier_transport_credit | parameter | 3 | — |

- The review-reach "method" tiers select a window length (12/6/3 months). That is a number in the same formula, so the `method` label is borderline, but a different look-back scope is accepted as a method in this charter's other policies too. Recorded as observation F11.
- The baseline.rule ("with a review of the base review months, each batch transport keeps the category's ambulance copay") gives a definite reversal of 0.00 where every booked ambulance copay equals the category copay.

**Per-task totals** (confirmed in the task files):
- Tree A (task 0) reads auth, rx, ride and pcp through its factors, with multi-source factors present.
- Tree B (task 1) reads auth (medical_need_relief, course factors) and ride (transport and ambulance factors), with multi-source factors present.

### findings

- **F1 — SOURCE-POLICY RED (undeclared override of plan_evt_copay).**
  - Symptom: four re-rating policies cite `plan_evt_copay` in `base_policy_refs` but name none of its sentences in `overwrite`. Their rules re-rate paid claims to copays other than "the copay the member's category sets for the claim's service_category", and the office rule charges copays on well-child and immunization care, which base says "carry no copay in any category".
  - Root cause: the factor tiers override base copay semantics without an overwrite entry.
  - Evidence: plan.extended.yaml, the `overwrite` lists of plan_ext_own_pcp_visit_rerating / office_visit_preventive_rerating / therapy_course_rerating / ambulance_transport_rerating, which name only plan_evt_claim_adjustment sentences. Base plan_evt_copay rule, sentences 1–2.
  - Bears on: task 0 (own-PCP, office), task 1 (therapy, ambulance). The consequence is demonstrated in each task file.
- **F2 — rounding mode (rule/compute).** "rounded to the cent" (rule) + "rounded half up" (tool Args) versus `RND` = binary-float `round`. The consequence exists only on exact half-cent ties. Bears on any task whose intermediate lands on a tie: demonstrated in `0.md` (cap 602.775).
- **F3 — window counting convention (rule/compute).** Calendar-month reading versus the DSL's rolling `MONTHS`, for `within_months` and `MONTHS(start)+1`. An observation unless a task world has rows in the gap. Checked per task.
- **F4 — SOURCE-FACTOR RED (unreal lockout ladders).** Detailed under factor_ladders. Bears on task 1.
- **F5 — observation.** past-due continuous eligibility is anchored only at the coverage start date.
- **F6 — observation.** A reward-reduced payment settles the month.
- **F7 — observation.** own-PCP tele/IHA counts are log-wide rather than batch-limited.
- **F8 — observation.** The counted-premium "paid less balance" tier.
- **F9 — observation.** "the cap never carries over" is not named against the rolling window.
- **F10 — observation.** The IHA ladder's tier/fall-through value coincide for a health-home practice.
- **F11 — observation.** ambulance_review_reach's `method` label (a window length).
- **Observation — the "is adjusted at most once" base sentence is not named.** Per world, no named claim already carries an adjustment.

## closing_checklist

Written after both reveals (2026-09-24T18:12:05Z). **The difficulty does not close in round 1.**

| Item | Status |
| --- | --- |
| Per-task files | `0.md` and `1.md` correspond one-to-one with tasks/0.json and tasks/1.json, alongside this file. No older revision exists. **Not every comparison section carries a PASS.** |
| Coverage and scope | All 7 extended policies are covered. The scopes are disjoint: task 0 = {over_cap, past_due, own_pcp, office}, task 1 = {lockout, therapy, ambulance}; this equals `charter_scope` of each task. Task tools and GT are closed. Every uuid8 is independent (§action_binding_and_uuids). |
| Problem trees | Task 0 has 3 prerequisites and 3 value_input edges. Task 1 has 2 prerequisites and 2 value_input edges. Each has an owner=user problem (the past-due payment; the lockout payment). Both are acyclic, and the difficulty graph is acyclic. **PASS**, with the task-1 caveat that the therapy node's object rests on a contradicted auth row. |
| Factors | Task 0: every factor bears weight and every baseline is definite and differs from gold. **FAIL** in task 1: the F4 unreal lockout ladders (0 surviving method factors), and gold tiers resting on the care/auth seed rows that contradict their charters. |
| Unique solution | **FAIL** in task 0: the refund depends on an unstated rounding mode at an exact half-cent tie (265.97 by the policy's half-up reading vs 265.98 in GT). Task 1: my derivation equals GT. |
| Policy self-consistency | **FAIL:** F1, an undeclared override of base plan_evt_copay by all four re-rating policies, demonstrated in both tasks. |
| Gate re-run | Not re-run by the auditor. The audited artifacts are unchanged (the hashes of plan.extended.yaml and task_tools.py match the brief), and the brief's gate snapshot stands. |

**Per-task verdicts:**
- Task 0: SOURCE-POLICY RED + SOURCE-TASK RED.
- Task 1: SOURCE-POLICY RED + SOURCE-FACTOR RED.

## revision_2

### charter_global_frozen (revision_2)

- Freeze: written at the mtime of this append, round 2. The auditor is the same independent agent.
- **Inputs re-hashed.**
  - `plan.extended.yaml`: `edc90362e118dd9864c1db6328e12ebef6c255fd7261d364c85964974749e649`. Changed since round 1 (`2105a00d…`), so every charter-global section is re-derived below.
  - `task_tools.py`: `7c4adf96…5ccd0`. Unchanged, so §action_binding_and_uuids is carried forward by reference on that hash.
- The base copy is still verbatim: a structural diff of the base keys shows none differing from `blueprint/products/plan.yaml`.
- **contamination_disclosure (round 2).**
  - This auditor revealed the round-1 GT of both tasks in round 1 (see `0.md` / `1.md` §source_gt_comparison). The round-1 values it knows are 265.98, 36.00, 29.00, 13.75, 73.50, 28.50 and 98.00.
  - The round-2 task JSONs, the worklog and the rework notes were not read before the round-2 per-task freezes.
  - Since both worlds changed, the round-2 derivations are recomputed from the round-2 masked views. Round-1 knowledge can only bias toward round-1 values, and any coincidence is flagged where it occurs.
- Nothing below is derived from a round-2 GT.

### Re-derived charter-global checks (revision_2)

- **policy_conflict_scan.** Subjects, target tools, owners and the two prerequisite components are unchanged from round 1:
  - A = {over_cap ← past_due, own_pcp, office}.
  - B = {lockout ← therapy, ambulance}.

  The claim-category partition among the four re-ratings still holds. The office rule now re-rates sick and follow-up visits under `pcp_visit` and returns copay on well-child visits, still only on `pcp_visit` claims of the PCPs. No new overlapping subject.
- **rule_compute_equivalence.** Every `compute_basis` entry is a verbatim substring of its rule. The only binding without its own basis is over-cap `counted_total`, whose rule sentence is "The counted total is …"; this is the same as round 1. Changes checked:
  - *Rounding (round-1 F2).*
    - Every rule now reads "rounded half up to the cent".
    - Every `RND` adds `K('half_up_guard')` = 1e-06 before `round(…, 2)`.
    - All rounded quantities are non-negative (`MX(0, …)`) or positive products of cent/percent values, so a +1e-6 guard implements half-up at the half-cent ties that can arise: `round(602.775 + 1e-6, 2)` = 602.78.
    - The guard is an implementation constant, not a business basis. **F2 closed.**
  - *Window convention (round-1 F3).* Every window sentence now says "a date counting when it lies fewer than that many whole months before the review date", which is exactly `_within`'s `0 <= MONTHS(d, NOW) < N`. The start-anchored spans ("one more than the whole months elapsed since …", "less those dated within the whole months elapsed since the end date") are exactly `MONTHS(x, NOW)+1` and `MONTHS(end, NOW)`. **F3 closed in the rule/compute.**
    - Residual observation R2-O1: the `factors[].ladder` text of `cap_months_by_coverage_span` still reads "whole months from the coverage start month through the review month, both counted". That is the old calendar wording and differs from its own rule when the coverage-start day-of-month exceeds the review day. Ladder metadata only; the rule and the compute agree.
  - *Own-PCP telehealth/IHA (round-1 F7).* The rule now reads "For each telehealth follow-up [initial health appointment] the current assignment's visit log records in the window, one batch visit re-rates …". The compute filters `pcp_assignment_id=cur_aid`, so the two agree. **F7 closed.**
    - Residual observation R2-O2: `iha_gap_days` takes `XLATEST(… visit_type='initial_health_appointment')` without the `cur_aid` filter. A superseded assignment's later IHA would be dated wrongly. Checked per world.
  - *Office.* Well-child copay return: the rule says "every well-child visit any of the member's primary care visit logs records in the window", and the compute says `well_visits × office_copay`, where `office_copay` is the category PCP copay. The rule says "returns … the copay booked on" each visit, so the two agree only while each logged well visit was booked at the category PCP copay.
    - Residual observation R2-O3: the same-day, vaccine-day and medication-check factors key on the latest well-child / vaccine / refill day with no window, and count sick visits on that day with no window. The rule states them that way too, so there is no mismatch, but a re-rated visit could lie outside the office window. Checked per world.
  - *Past-due continuous eligibility (round-1 F5).*
    - The rule now anchors on the fewer of the months since coverage start and the months since "the start of the current eligibility period … the redetermination months that end on the renewal due date".
    - `ce_months_run = MN(MONTHS(start, NOW), redetermination − 1 − MONTHS(NOW, renewal_due))` implements the months elapsed since the period start (renewal_due − 12 months + 1 day) up to day-of-month edge effects.
    - plan_continuous_eligibility is now in `base_policy_refs`. Base anchors on "the latest renewal approval", which no record carries, so the extended rule states the record-visible anchor. **F5 closed** as far as the charter goes; the edge behaviour is checked per world.
  - *Past-due reward credit (round-1 F6).* The rule now says "The Healthy Kids reward total is a credit … it is not a waiver, and the payment settles the month." **F6 closed.**
  - *Over-cap "never carries over" (round-1 F9).* Now declared superseded: "cost sharing dated outside the counting window never counts toward the cap". **F9 closed.**
  - *Therapy.* The course authorization is now "approved on a request received in the therapy window, whether it is still approved or has since expired". The compute (`course_approved` over approved+expired, `ther_npi = CFIELD(variant rehab)` with no status filter) agrees.
    - Residual observation R2-O4: `CFIELD` returns the first rehabilitation authorization of any status. A member with two rehab authorizations (for example an older denied one) could be read on the wrong row. Checked per world.
- **action_binding_and_uuids.** Carried forward: the task_tools.py hash is unchanged and each `(target_tool, computes)` is still claimed by exactly one policy.
- **prerequisite_graph / prerequisite_sentences.** The five edges, their `policy_source` sentences (each verbatim in its own rule, as re-verified), kinds, gates, forms and `resolved_by` are unchanged from round 1. The gates `premium_counted`, `medical_net` and `credit_offset` still exist. The round-1 conclusions stand by the same derivation, including the wording-scope observation on the over_cap ← own_pcp sentence.
- **override_declarations (round-1 F1).**
  - own-PCP, therapy and ambulance now each declare plan_evt_copay S1 superseded: "A re-rated … carries the re-rated copay this rule sets in place of the copay the category schedule sets for its service category".
  - The office policy declares it for "a re-rated sick or follow-up visit".
  - The office rule no longer charges any copay on well-child care. Every well-child visit's copay is returned "because well-child care is preventive care and carries no copay", which is consistent with base S2 "Preventive … claims carry no copay in any category".
  - The remaining office re-rates (telehealth sick, same-day sick, vaccine-day sick, medication check, coordinated follow-up) apply to sick or follow-up visits, which are not preventive claims, and fall under the declared S1 replacement.
  - The own-PCP late initial health appointment re-rates at 1.00. An initial health appointment is a visit billed under the specialist copay, re-rated under the declared S1 replacement. Whether an IHA is "preventive" under base S2 is not stated by any base sentence (its formula keys on `service_category='preventive'`), so no second reading can be demonstrated. Observation R2-O5.
  - **F1 closed.**
- **factor_ladders (re-derived).**

  | Policy | Factors | Parameter / method | Notes |
  | --- | --- | --- | --- |
  | over_cap | 6 | 4 / 2 | Ladders unchanged except the rounding/window wording. |
  | past_due | 6 | 4 / 2 | month_rate tier 1 now reads the CE-run measure. |
  | own_pcp | 4 | 3 / 1 | health_home 0.50 ≠ IHA tier 0.00, **F10 closed**. |
  | office | 6 | 5 / 1 | See below. |
  | lockout | 5 | 3 / 2 | See below. |
  | therapy | 6 | 5 / 1 | See below. |
  | ambulance | 5 | 4 / 1 | Discharge and care-tier credits now read "episode enrolled in the twelve months". F11 unchanged (observation). |

  - Office factors: telehealth_sick_log_scope (method), telehealth_sick_visit_copay, same_day_sick_visit_copay, vaccine_day_sick_visit_copay (cross rx), medication_check_visit_copay (cross rx), coordinated_followup_copay. All values are pairwise distinct per ladder. The old well_child_schedule and telehealth-well-child tiers are removed.
  - Lockout (**round-1 F4**):
    - void_bill tiers: latest bill for a post-termination month posted *before* termination, so that bill alone is void; posted *on or after* termination, so every bill posted on or after is void; otherwise all owed. All three are reachable among non-payment terminations and none restates the policy scope.
    - credit_offset tiers: reversals AND refund, so both are offset; reversals AND no refund, so reversals only; otherwise (no reversal), nothing is offset. The fall-through is reachable for a lockout payer with no copay correction, for example one with no approved therapy course and no ambulance claim, where the prerequisite sentences are vacuous. Its baseline `'0'` equals that fall-through.
    - medical_need_relief now reads "enrolled in a care management episode in the counting window" and "approved … whether still approved or since expired".
    - **F4 closed.** The ladders are now three reachable, distinct tiers each. Business plausibility is ordinary: bills issued after coverage ended are void, and credits are netted when a copay correction was made.
  - Therapy: extension and care-plan credits now read "enrolled in a care management episode during the therapy window". Intake now reads request origin: "a course a provider requested … any other course, such as one carried over from a previous plan or approved on a retroactive request, keeps no intake visit". That is a real business distinction, and the fall-through is now reachable with an object.
- **findings (revision_2, charter-global).**
  - F1, F2, F3, F4, F5, F6, F7, F9 and F10 are closed, on the evidence above.
  - F8 and F11, the "adjusted at most once" observation and the over_cap ← own_pcp wording observation are unchanged observations.
  - New observations: R2-O1 (stale cap-months ladder text), R2-O2 (IHA date read without the assignment filter), R2-O3 (unwindowed same-day / vaccine-day / refill-day keys), R2-O4 (`CFIELD` picks the first rehab authorization of any status) and R2-O5 (IHA preventive status is not stated by base). None is demonstrable against the charter alone; each is checked on the task worlds.

### closing_checklist (revision_2)

Written after both round-2 reveals (2026-09-24T18:29:47Z).

| Item | Status |
| --- | --- |
| Per-task files | `0.md` and `1.md` correspond one-to-one with the tasks. Each carries its round-1 text untouched and appends a `revision_2` with a frozen section, a comparison and findings. Both revision_2 comparisons carry **PASS**. |
| Coverage and scopes | All 7 extended policies are covered. Scopes are disjoint and equal each task's `charter_scope`: task 0 has {over_cap, past_due, own_pcp, office}; task 1 has {lockout, therapy, ambulance}. The task tools are unchanged; their uuid8s are independent. |
| Problem trees | Task 0: 3 prerequisites, 3 value_input edges, an owner=user leaf. Task 1: 2 prerequisites, 2 value_input edges, an owner=user root. Both trees are acyclic, and so is the difficulty graph. The cross-task re-ratings evaluate to 0.00 in the other world (verified). |
| Factors | Every computation declares 4–6 factors with at least 2 `parameter` and at least 1 `method`. Every ladder has three reachable, distinct tiers stated in its rule. Every factor bears weight against an honest baseline, and every all-baseline number is definite and differs from gold. Both tasks have multi-source and cross-difficulty factors on seeded rows that are consistent with their charters. |
| Round-1 REDs | F1, F2 (SOURCE-TASK rounding), F4 and the task-1 seed contradiction are all closed. |
| Round-1 observations | F3, F5, F6, F7, F9 and F10 are closed. F8, F11, "adjusted at most once", the wording-scope observation and the persona-conditional observation are recorded unchanged. |
| New observations | R2-O1 through R2-O5, none with a consequence in either world. |
| Gates | The coordinator's round-2 snapshot shows all 7 instantiation gates green on the final form, with `check_traceability` deferred. The auditor did not re-run them. |

**Difficulty verdict (revision_2): PASS.** Policy self-consistency, the problem tree, factor weight and the unique solution all hold for both tasks.
