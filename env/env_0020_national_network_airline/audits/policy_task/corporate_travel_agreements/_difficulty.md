# Policy-task audit — corporate_travel_agreements / charter-global

## charter_global_frozen

- Revision: 1 (first audit of this difficulty; no earlier revision exists under this directory).
- Freeze time: 2026-09-24T17:28:47Z. Auditor: erl-task-policy-audit subagent (Claude Opus 5.5). The auditor did not write these artifacts.
- Frozen inputs (sha256, re-checked against the coordinator brief before reading):
  - `env/env_0020_national_network_airline/tasks/corporate_travel_agreements/business.extended.yaml` = `bd0d2adb7b7e75789c0a0d4386fac468d36cc8a1d1989d8ff4cc978b6a2ba953`
  - `env/env_0020_national_network_airline/tasks/corporate_travel_agreements/task_tools.py` = `d41d36901e9c2c2d5c1aaf4d212c4c8e90e30c7383faf2a3d437da84f4375c4c`
  - masked views `task_0.masked.json` = `70941d7b…06312b9`, `task_1.masked.json` = `691776b7…45cce2e` (under `/tmp/claude-1000/erl_coord_env0020/views/corporate_travel_agreements/r1/`)
- Fields read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/business.yaml`, the extended charter, `task_tools.py`, and the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (read only for `_within`, `MONTHS`, `DAYS`, `CFIELD`, `XSUM`/`XCOUNT` scoping).
- Fields masked and not read: `tasks/{0,1}.json` (every field), `worklog.md` (difficulty and scenario level), the shared authoring scratchpad. Nothing in this section is derived from any revealed GT.
- Entry conditions (Step 0): the brief carries the gate snapshot — `check_extended` (EXTENDED OK), `check_task_tools` (TASK TOOL CONTRACT OK), `replay_tasks` (REPLAY OK), `check_solvability` (SOLVABILITY OK), `check_compute` (COMPUTE OK), `check_grounding` (GROUNDING OK), `check_cross_fire` (SCOPE OK), all rc=0 — plus the masked-view hashes and the masked field list. `check_traceability` is deferred by design to the render stage. Input complete; the auditor ran no gate.

DSL conventions the audit relies on (from `check_compute.py`): `within_months=N` keeps a row when `0 <= MONTHS(row_date, NOW) < N`, where `MONTHS` counts whole calendar months (a later day-of-month in the start date takes one month off); rows dated in the future are excluded and rows dated on NOW are included. `CFIELD('ticket', …)` returns the first ticket held by the company's own `customer_id` that matches the filters. `XSUM`/`XCOUNT` read ticket-ledger rows whose `customer_id` is the company or whose ticket is held by the company.

### policy_conflict_scan

The base section of `business.extended.yaml` is verbatim `blueprint/products/business.yaml`. Every base key compares equal after parse, and a line diff shows only the two header comment lines and the appended `extended_policies` block. The extended section has seven policies:

| Policy | Subject event | target_tool (owner) | computes | Base refs |
| --- | --- | --- | --- | --- |
| business_ext_overdue_invoice_late_fee | business_late_fee | assess_invoice_late_fee_9e8e2547 (agent) | amount | business_billing |
| business_ext_card_paid_ticket_points | business_points_accrual | post_card_ticket_points_2b97bc4a (agent) | points | business_points_earning, business_negotiated_benefits |
| business_ext_gold_status_award_price | business_points_redemption | redeem_gold_status_award_92a33401 (user) | points | business_points_redemptions |
| business_ext_retro_claim_points | business_points_accrual | claim_retro_segment_points_a26ae9c7 (agent) | points | business_points_earning, business_negotiated_benefits |
| business_ext_enrollment_bonus_late_credit | business_bonus_points | credit_enrollment_bonus_fc1a1a80 (agent) | points | business_points_earning |
| business_ext_spend_milestone_bonus | business_bonus_points | credit_milestone_bonus_a908f78d (agent) | points | business_points_earning |
| business_ext_domestic_award_price | business_points_redemption | redeem_domestic_award_ffdd59aa (user) | points | business_points_redemptions |

Overlapping subjects, and how each overlap is separated:
- **business_points_accrual (card-paid points vs retro claim):** the object sets are disjoint by rule. The card-paid rule covers "a flown segment of a ticket booked under the agreement whose fare was paid by card". The retro rule covers "one flown segment of a ticket the company booked without the agreement". A ticket either carries the agreement as `corporate_account_id` or does not, so no segment falls under both. Both inherit the base `segment_once` dedup.
- **business_bonus_points (enrollment vs milestone):** these are different bonus grounds, distinguished by `bonus_reason` and `agreement_year_start` in the event's `distinguish_by`. Their triggers differ (flown spend since approval against the enrollment-bonus spend; agreement-year spend against the spend milestone).
- **business_points_redemption (Gold status award vs domestic award):** the two award objects are different (a `status_award` Summit Gold award and an `award_ticket` domestic Main Cabin round trip). Both inherit the base eligibility (travel-manager or arranger request, active-roster beneficiary, agreement active, balance covers the award). The Gold award also inherits the per-year status-award cap and the no-downgrade clause.

Across the seven policies, eligibility, triggers, time anchors (every date anchor is the write date, `approved_date` or `agreement_end_date`), action parameters and terminal states reach no incompatible conclusion on a shared subject. Cross-category reads go only to `ticket` (`ticket_holdings` fields and `ticket_transactions`), and each policy's `cross_category` declares them.

Scope exclusivity and completeness (derived blind from the prerequisite graph and the subjects; `charter_scope` is masked): the graph splits into two components, {gold ← late fee, gold ← card-paid points} and {domestic award ← milestone ← retro claim, domestic award ← enrollment bonus}. Those are 3 + 4 = 7 policies, pairwise disjoint and together covering every extended policy. With M = 2, each component is one task's scope. That the task-to-component mapping matches the claimed `charter_scope` is checked at reveal.

### rule_compute_equivalence

Every compute binding of all seven policies has a `compute_basis` quotation that appears verbatim as a sentence of that policy's `rule`. Every tier named in `factors[].ladder` is stated in the rule prose (its condition and its value or method) and is a branch of the `decides` binding. Every branch of each `decides` binding is a tier the rule states. The windows are 12 months everywhere (3 months for milestone momentum) and are named in the rule. Rounding points match: "rounded to the cent once at the end", "rounded down to the whole point", "rounded to the nearest whole point once", "rounded up to the next whole price step", and so on each correspond to `RND(…,2)`, `int()`, `int(RND(…,0))` and a ceiling `//` step. The caps and floors (`MX(min_fee, settled)`, and "nothing when the spend has not reached") match the rule.

Gaps the sweep found: places where compute and prose can part company on some world. None is reached by either task's world, and each task file checks that on its own world:

1. **Late fee — "due date has passed" vs `within_months` on `due_date`.** The rule reads "every invoice charge whose due date has passed". The compute's `SUM(... within_months=600, date_field='due_date')` also keeps a charge due on the fee date itself (`MONTHS = 0`). The two diverge only for an invoice due exactly on the fee date.
2. **Card-paid points — which card-paid ticket.** The rule speaks of "the card-paid ticket" whose points entry is missing. The compute's `CFIELD('ticket', …, corporate_account_id=HID, payment_form='credit_card')` takes the first card-paid ticket on the agreement, whether or not it is already credited. The two diverge on any world with more than one card-paid agreement ticket. The retro policy has the same shape: `CFIELD(…, corporate_account_id=None)` takes the first company ticket without the agreement.
3. **Milestone and domestic award — "current agreement year" vs `within_months = pace + 1`.** For `milestone_segments`, `milestone_redeemed` and `award_tickets_this_year`, the rule says "in the current agreement year" or "within the months the agreement year has run". The compute window `0 <= MONTHS(d, NOW) <= pace` can reach up to about a month before the latest anniversary. In the first agreement year no row precedes approval, so the two readings coincide there.
4. **Domestic award — recency with no redemption on file.** The ladder's fall-through reads "fewer days, or no redemption on file", and the compute returns `0` days when `LATEST` is empty. The rule prose states only "fewer days set the listed-price percentage" and says nothing about an agreement with no earlier redemption. That sub-case lives in `factors`/`compute` and not in the rule.

### action_binding_and_uuids

- `(target_tool, computes)`: seven distinct pairs, each claimed by exactly one policy. No base policy has a `target_tool`.
- Tool docstrings (`task_tools.py`) describe each write's single business effect in the terms of its own subject. None names another tool, states a position in a sequence, or uses an ordering word about another action. The only "after" and "first" tokens are "balance … after the entry" in the Returns blocks and "1 for the first segment". No tool body reads a policy condition, rejects a call, or hints at a prerequisite. Each body creates its row(s) and updates the holding's aggregate, and that is all.
- The uuid8s are `9e8e2547`, `2b97bc4a`, `92a33401`, `a26ae9c7`, `fc1a1a80`, `a908f78d` and `ffdd59aa`. No two share a prefix or tail, none is a sequence or an adjacent value, and nothing suggests they were batch-derived. Each appears to have been generated independently.

### prerequisite_graph

| Blocked policy | → problem | kind | gate binding (exists in compute) | form | policy_source verbatim in own rule | resolved_by = depended-on target_tool |
| --- | --- | --- | --- | --- | --- | --- |
| gold_status_award_price | overdue_invoice_late_fee | value_input | late_fees_for_gold (yes) | state | yes | yes |
| gold_status_award_price | card_paid_ticket_points | value_input | points_earned_for_gold (yes) | state | yes | yes |
| spend_milestone_bonus | retro_claim_points | value_input | milestone_year_spend (yes) | state | yes | yes |
| domestic_award_price | spend_milestone_bonus | value_input | award_earned_points (yes) | state | yes | yes |
| domestic_award_price | enrollment_bonus_late_credit | value_input | award_earned_points (yes) | state | yes | yes |

- `prerequisite` is filled in on all seven policies, as `[]` on the four leaves. Every `problem` names an extended policy id in this file, never a base policy and never the policy itself. The graph is acyclic (checked mechanically).
- Every edge has `form: state` and none carries a `fallback_reason`, which is consistent.
- Each `condition` matches its sentence in scope and strength:
  - Gold / late fee: "every invoice … that stands unpaid past its due date" ↔ "charge plus late fees exceeds its payments after its due date".
  - Gold / card points: "every flown segment of a ticket booked under the agreement and paid by card" ↔ "`corporate_account_id` is the agreement and `payment_form` is `credit_card`".
  - Milestone / retro: "a ticket the company booked without the agreement that is still inside the claim window" ↔ "company-held ticket with no `corporate_account_id`, flown within … `retroactive_points_window_days`".
  - Domestic / milestone: "every agreement year whose spend has reached the tier's spend milestone".
  - Domestic / enrollment: "once the agreement's flown spend since approval has reached the tier's enrollment-bonus spend".
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` entry.
- Each `effect` sentence is general text using "can" or a tier move. Whether an effect holds on a given world is judged in the task files.

### prerequisite_sentences

Four-point test on each sentence:

1. "A Summit Gold status award is priced only after every invoice of the agreement that stands unpaid past its due date carries a late fee entry." It uses an ordering connective ("only after"). It waits on a record-visible state (a late-fee entry on each unpaid past-due invoice) named in table words. It names no tool, id, snake_case token or row id. Its scope matches the condition.
2. "A Summit Gold status award is not priced until every flown segment of a ticket booked under the agreement and paid by card carries its points entry." It uses "not … until", waits on a state (a points entry per such segment), has no tool or id, and has matching scope.
3. "A spend-milestone bonus is fixed only after every flown segment of a ticket the company booked without the agreement that is still inside the claim window carries its points entry." It uses "only after", waits on a state, has no tool or id, and has matching scope. "Inside the claim window" is the base retro window.
4. "A domestic Main Cabin round-trip award is not priced until the points account carries the spend-milestone bonus of every agreement year whose spend has reached the tier's spend milestone." It uses "not … until", waits on a state, has no tool or id, and states the set openly ("every agreement year whose …").
5. "A domestic Main Cabin round-trip award is priced only after the points account carries the enrollment bonus once the agreement's flown spend since approval has reached the tier's enrollment-bonus spend." It uses "only after", waits on a state, has no tool or id, and has matching scope.

For each state-form edge, the writes of this difficulty that bring the state about, and the derivation a reader makes:

- (1) Only `business_late_fee` rows satisfy "carries a late fee entry", and only the late-fee policy writes them. A payment could also take an invoice out of "unpaid". `business_invoice_payment` is in the difficulty's claimed event types, but no task tool writes it and no extended policy has it as a subject. **One write.**
  - Derivation: the sentence leads to the invoice entries, which show the invoices past due and unpaid. The late-fee rule says "a late fee is charged once on each invoice … still unpaid after its due date", and that write is the one that resolves the edge.
- (2) Two tools create `business_points_accrual` rows: card-paid points and the retro claim. The retro rule is confined to "a ticket the company booked without the agreement". The card-paid ticket carries the agreement, so only the card-paid policy's rule describes the write. **One reading.**
- (3) Same pair of tools, with the opposite exclusion. The card-paid rule is confined to tickets "booked under the agreement", so only the retro rule applies to a ticket without `corporate_account_id`. **One reading.**
- (4) Only the milestone policy writes `business_bonus_points` with the milestone ground. The enrollment bonus is a different ground. **One write.**
- (5) Only the enrollment policy writes the enrollment-bonus entry. **One write.**

No rule carries a second wording of any dependency, a tool name or another problem's id (a mechanical scan found no snake_case token in any extended rule, and no rule contains another policy's id or tool). No depended-on rule restates the blocked policy's sentence: the late-fee, card-paid, retro and enrollment rules are silent about the awards, and the milestone rule is silent about the domestic award. No extended rule states a cross-problem order beyond these five sentences.

Base rules that state cross-problem orders:
- `business_billing`: "a suspended agreement returns to active once every overdue invoice and its late fee are paid in full".
- `business_agg_traveler_rosters`: "must be removed there by that company before being added here".

Neither grounds an edge in these trees, and neither involves a policy of this charter's extended section. Observation only.

### override_declarations

Findings only. Each task file shows whether a finding changes the answer on its own world.

- **overdue_invoice_late_fee vs business_billing.** Base sentences on invoice permission, active/under_review invoicing, credit limit, terms, suspension, payment application, reinstatement and termination are all followed and not overwritten. The late-fee sentence "charged one late fee of late_payment_fee_percent percent of its unpaid amount, at least late_payment_fee_min_usd, rounded to the cent" is overwritten, and the declared `superseded_clause` covers the quantity (the per-invoice "its unpaid amount" becomes the agreement-wide unpaid amount past due), the rate and the rounding. The "one late fee" and the minimum are kept.
  - The `replaced_by` text names the intermediate ("The fee before tenure is …") rather than the fee finally charged. The rule's own last sentence ("The late fee charged is the larger of the settled fee and the tier's minimum late fee") closes that gap, and the merged semantics are unique. Observation.
- **card_paid_ticket_points vs business_points_earning.** The declared superseded clause is "Points are the segment's eligible spend times points_per_dollar of the tier held on the flight date, rounded down to the whole point". The same base sentence goes on: "…where eligible spend is the base fare share of the segment after the negotiated discount and excluding taxes". That part is not superseded and stays in force.
  - The extended rule sets eligible spend to "the base fare recorded on the card-paid ticket", the whole ticket and not the segment's share. On a card-paid ticket with more than one segment this is an **undeclared override** of the eligible-spend clause. The base clause gives base_fare ÷ segments, and the extended rule gives the whole base fare for each segment.
  - Neither task's world has such a ticket (task 0's card-paid ticket is one-way with one segment; task 1 has no card-paid ticket due), so no task can demonstrate a consequence. **Recorded as a latent finding (observation), not a red light.**
  - "Tier held on the flight date" versus the current tier: equal on every world here. Every other earning sentence (tour code, roster, accrual only while active or under review, segment once, spend added) is followed.
- **gold_status_award_price vs business_points_redemptions.** The declared superseded clause is "Summit Gold for status_award_points_summit_gold". Requester, beneficiary, active agreement, validity months, no downgrade, the per-year cap, balance cover and no combination with miles are all inherited and not weakened. No undeclared override.
- **retro_claim_points vs business_points_earning and business_negotiated_benefits.** The same partial clause is superseded. The extended claim spend is the per-segment share (base fare ÷ 2 for a round trip) after the negotiated discount booking under the agreement would have applied, which is consistent with the base eligible-spend clause that remains in force. The retro window is inherited.
  - The claim-share tier for "a ticket booked through a channel outside the tier's eligible booking channels" credits 50%. The base allows a claim for an "eligible ticket booked without the agreement", and `business_negotiated_benefits` makes channel eligibility part of counting under the agreement. Whether an outside-channel ticket is an "eligible ticket" is not settled by either text. Latent: neither task's claimed ticket is outside-channel. Observation.
- **enrollment_bonus_late_credit vs business_points_earning.** The declared superseded clause is "The enrollment bonus of enrollment_bonus_points is credited once when the agreement's flown spend since approval first reaches enrollment_bonus_min_flown_spend_usd". Crediting once and the approval-date tie are kept.
  - On tiers whose `enrollment_bonus_points` is 0 (Corporate Preferred, Premier, Strategic), the extended allowances (coupon and award allowances, then the long-late ×1.25) would credit a positive "enrollment bonus" where the base grants none. The override is declared, so this is not undeclared, but it is a large change of meaning on those tiers. Neither task is on those tiers. Observation.
- **spend_milestone_bonus vs business_points_earning.** The declared superseded clause is "the milestone bonus of spend_milestone_bonus_points is credited once per agreement year when the agreement year's spend first reaches spend_milestone_usd of the tier then held". "Once per agreement year" is kept.
- **domestic_award_price vs business_points_redemptions.** The declared superseded clause is "Award tickets cost award_points_domestic_main_round_trip". The rest is inherited.

No anonymous intermediate factor or 0/1 multiplier was found. One gate, "nothing when the spend has not reached", appears in both bonus policies, but it restates the base existence condition rather than zeroing a figure the base fixes. No dropped branch was found. No author language calls a base output wrong.

### factor_ladders

Per policy, the factors with their effect labels, the binding each decides, and the tiers of each ladder. Every ladder has three pairwise-disjoint tiers, the fall-through included, and every tier is stated in the rule prose and implemented in `compute`.

| Policy | Factors (effect → decides) | parameter / method / multi-source / cross-difficulty (reads) |
| --- | --- | --- |
| overdue_invoice_late_fee | late_fee_record_rate (parameter → starting_fee_rate: 2.5 / 2.0 / tier %) · credit_use_addition (parameter: 0.5 / 0.25 / 0) · payment_gap_addition (parameter: 0.5 / 0.25 / 0) · invoiced_flying_share (parameter: 60 / 80 / 100) · tenure_settlement (method: ÷2 floor-dollar / ×0.75 ceil-dollar / as computed to the cent) | 4 / 1 / 0 / 1 (ticket_transactions) |
| card_paid_ticket_points | fare_brand_earning (method: ×2 / +250 / as-is) · route_class_uplift (parameter: 20 / 10 / 0) · posting_delay_uplift (parameter: 20 / 10 / 0) · segment_activity_uplift (parameter: 12 / 6 / 0) · spend_standing_uplift (parameter: 10 / 5 / 0) | 4 / 1 / 0 / 4 (ticket_holdings, ticket_transactions) |
| gold_status_award_price | payment_record_percent (125 / 110 / 100) · network_percent (85 / 92 / 100; fares **and** coupons) · repeat_award_percent (130 / 115 / 100) · earning_percent (94 / 97 / 100) · gold_tenure_allowance (300 / 150 / 0) · remaining_term_charge (method: 50% ceil-100 / pro-rata months ceil-100 / in full) | 5 / 1 / 1 (network) / 1 (ticket_transactions) |
| retro_claim_points | claim_discount (P intl / P dom / 0; brand **and** route) · claim_milestone_approach (10 / 5 / 0) · claim_fare_volume (8 / 4 / 0) · claim_channel_share (50 / 90 / 100) · claim_lag_settlement (method: ÷2 floor / ×0.75 ceil / as-is) | 4 / 1 / 1 (discount) / 4 (ticket_holdings, ticket_transactions) |
| enrollment_bonus_late_credit | late_bonus_spend_uplift (20 / 10 / 0) · late_bonus_fare_uplift (10 / 5 / 0) · late_bonus_coupon_allowance (500 / 300 / 0) · late_bonus_award_allowance (300 / 150 / 0), where each tier is lateness **and** a measure · late_bonus_settlement (method: ×1.25 ceil-100 / ×1.1 floor-50 / as-is) | 4 / 1 / 4 / 2 (ticket_transactions) |
| spend_milestone_bonus | milestone_pace (40 / 15 / 0) · premium_cabin_share (20 / 10 / 0) · milestone_segments (10 / 5 / 0) · milestone_momentum (10 / 5 / 0) · milestone_redemption_allowance (250 / 100 / 0) · agreement_year_settlement (method: ×2 floor-100 / ×1.5 ceil-100 / as-is) | 5 / 1 / 0 / 1 (ticket_transactions) |
| domestic_award_price | award_earning (88 / 94 / 100) · award_coupons (92 / 96 / 100) · award_repeat (110 / 105 / 100) · award_milestone (95 / 98 / 100) · award_recency (97 / 99 / 100) · award_balance_charge (method: 90% floor-50 / −100 / as-is) | 5 / 1 / 0 / 1 (ticket_transactions) |

- Each policy has 5 or 6 factors (within 4–6), at least 2 `parameter` and exactly 1 `method`. Each factor's `bindings` are disjoint from every other factor's, and each `decides` is an input binding and never `result`.
- Per task: the gold/late-fee/card-points scope carries a multi-source factor (gold network) and cross-difficulty factors. The domestic/milestone/enrollment/retro scope carries multi-source factors (retro discount, the four enrollment conjunctions) and cross-difficulty factors. Both minimums are met in each scope.
- Each policy's `baseline.rule` is made of sentences of its `rule` (checked mechanically), gives a definite number from the records with no factor applied, and its `params` are the parameters it names. Every factor's fall-through is that baseline's input: the tier late-payment percentage, zero additions, the whole share, the fee as computed, the standard points, full price, and the listed price.

**Tier distinctness.** On the agreement tiers these tasks use (Corporate Select for the gold scope, Business Connect Plus for the domestic scope), no two tiers of any ladder select the same value or method. Latent degeneracies on other agreement tiers (observations; neither task is on them):
- Under Crestline Business Connect, the retro `claim_discount` ladder collapses: all three tiers give 0 (both discount percentages are 0 and the eligible-brand list is empty).
- Under Business Connect, the card-paid `spend_standing_uplift` top tier ("at or above the tier's annual spend threshold" = 0) holds for every agreement.
- On Corporate Preferred and above (enrollment bonus 0), the enrollment uplifts are inert and only the allowances act.

**Honest labels.** fare_brand_earning (multiply vs add vs none), remaining_term_charge (share vs pro-rata vs full) and award_balance_charge (percentage-and-floor vs subtraction vs none) change the algorithm. Four `method` factors (tenure_settlement, claim_lag_settlement, late_bonus_settlement, agreement_year_settlement) are hybrids: each tier applies a different scale factor **and** a different rounding direction or granularity. Because the rounding rule itself differs by tier, they are accepted as `method`. Observation. Every method tier names a rule stated in the policy's own `rule`. No `parameter` factor changes the algorithm.

**Realism (conditions and outcomes).** Every ladder condition is a record aggregate an airline corporate desk could weigh: payment history, credit use, days since payment, invoiced or flown volume, tenure, fare brand, route class, cabin mix, spend pace, redemption history, points balance and remaining term. The fall-throughs are the published standard prices, rates and points. The following are unusual but not demonstrably unreal, so they are recorded as observations rather than failures:
- the posting-delay uplift, where points rise with the airline's own lateness, read as goodwill for a late correction;
- the retro claim's milestone-approach uplift;
- milestone pace measured at the credit date rather than at the date the milestone was reached;
- the milestone redemption allowance, where redeeming points adds bonus points;
- the domestic-award repeat surcharge and rich-balance discount.

None of these conditions holds for every customer who reaches the write.

### findings

No charter-global `SOURCE-POLICY RED`: every conflict found either is declared or has no demonstrable consequence on any task world of this difficulty. Observations, with the tasks each bears on:

- **O-1** (tasks 0): card-paid eligible spend is the whole ticket base fare, which leaves the unsuperseded base clause "base fare share of the segment" in conflict on multi-segment card-paid tickets. Latent undeclared override. See `override_declarations`.
- **O-2** (task 0): late fee "due date has passed" vs `MONTHS = 0` inclusion of an invoice due on the fee date. See `rule_compute_equivalence` item 1.
- **O-3** (tasks 0, 1): `CFIELD` selects the first card-paid (or first non-agreement) company ticket rather than the uncredited one. See item 2.
- **O-4** (task 1): the `pace + 1` month window vs "current agreement year" for segments, redemptions and award tickets. See item 3.
- **O-5** (task 1): recency with no redemption on file is stated only in `factors`/`compute`. See item 4.
- **O-6** (task 1): whether an outside-channel ticket may be claimed retroactively. See `override_declarations`.
- **O-7** (tasks 0, 1): "window before the redemption / posting date" leaves open whether an entry dated on that same day counts. The gold earning and record windows and the domestic earning window must count same-day prerequisite entries for the edges to bear weight. The DSL includes them (`MONTHS = 0`), and the blocked rules' own "priced only after … carries …" sentences only make sense if they count. Recorded as an observation on the wording.
- **O-8** (all): hybrid `method` labels; latent ladder degeneracies on agreement tiers no task uses; unusual but defensible ladder conditions. See `factor_ladders`.
- **O-9** (task 0): `business_invoice_payment` is a claimed event type with no task tool, which is why the late-fee write is the only write that resolves edge (1).

## closing_checklist

Written after both reveals (2026-09-24T17:32:59Z). The sections above were frozen before any reveal and are left untouched.

**Status: NOT CLOSED.** Task 1 carries a `SOURCE-CHAIN RED`: a false deletion assertion in its `design_rationale` (see `1.md` → `findings` F-1). A difficulty closes only when every task's four relationships PASS.

The Step 4 checklist is still recorded for reference:

- **Audit files.** `0.md` and `1.md` correspond one-to-one to tasks 0 and 1, with `_difficulty.md` alongside. This is revision 1, so there are no older revisions. Comparison results:
  - `0.md`: PASS.
  - `1.md`: SOURCE-CHAIN RED (F-1). This item is not met.
- **Coverage and scope.**
  - The seven extended policies are fully covered: task 0 `charter_scope` = {late fee, card-paid points, gold}, task 1 = {retro claim, enrollment, milestone, domestic award}.
  - Each scope spans its whole problem tree, and the two scopes are pairwise disjoint.
  - The revealed scopes equal the blind component split in `policy_conflict_scan`.
  - Task tools and GT are closed: every gold write uses its policy's `target_tool`, and `db_closure_matches_initial_state` is true for both tasks.
  - uuid8s are independent (`action_binding_and_uuids`).
- **Problem trees.**
  - Task 0: 2 prerequisite problems, 2 value_input edges, user-owned root.
  - Task 1: 3 prerequisite problems, 3 value_input edges, user-owned root.
  - The difficulty-wide graph is acyclic and no edge crosses tasks. Every edge bears weight at its dependent.
- **Factors.**
  - Every computation declares 5–6 factors (≥2 `parameter`, 1 `method`) and a self-sufficient baseline.
  - Each task has at least one multi-source factor and at least one cross-difficulty factor.
  - Every factor bears weight against an honest baseline on its task's world. Each baseline-alone number is definite and differs from gold, with figures matching `computations` exactly.
- **Gates.** The instantiation-stage gates were not re-run by this auditor, by design. The snapshot in the brief (all OK) is the input qualification. A re-run on the final form belongs to closing and is outstanding until the difficulty can close.

**Per-task verdicts:**

| Task | Verdict |
| --- | --- |
| 0 | PASS: policy self-consistency, problem tree, factors, unique solution. |
| 1 | SOURCE-CHAIN RED (F-1). Policy self-consistency, factors and unique solution PASS. The scored solution matches the blind derivation on every value. |

## revision_2

### charter_global_frozen (revision 2)

- Freeze time: 2026-09-24T18:10:49Z. Auditor: erl-task-policy-audit subagent (Claude Opus 5.5).
- **The extended yaml changed**, so every charter-global section is re-derived in full below.
  - Extended yaml: sha256 `d9c458712b7e0eec174ad5b9a1695d21178d842b967d8f2b1f0a1bf70009f179`; round 1 was `bd0d2adb…a953`.
  - `task_tools.py`: sha256 `d41d36901e9c2c2d5c1aaf4d212c4c8e90e30c7383faf2a3d437da84f4375c4c`, unchanged.
  - The base section is still verbatim `blueprint/products/business.yaml`: every key compares equal, and `extended_policies` is the only addition.
- **Masked views:** `r2/task_0.masked.json` `70941d7b…` and `r2/task_1.masked.json` `691776b7…`, the same hashes as round 1, so the seeds are unchanged.
- **Gates:** the coordinator's round-2 snapshot reports all green (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE; traceability deferred). The auditor ran none of them.
- **Not read before this section and the per-task revision_2 freezes:** the round-2 `tasks/{0,1}.json` and `worklog.md`.
- **contamination_disclosure (revision 2):**
  - The auditor saw the round-1 GT of both tasks at the round-1 reveal (`0.md` and `1.md`, `source_gt_comparison`). The seeds are unchanged, so no round-2 derivation can be blind in the strict sense.
  - The round-1 blind derivations (frozen at 17:30:49Z and 17:31Z, before any reveal) remain the blind evidence.
  - Round 2 recomputes both worlds mechanically under the new charter, with the same write sequence derived in round 1. It asks one question: does any compute change move any figure? Nothing below rests on a round-2 GT field.
- **Round-1 old text is left untouched above this heading.**

### What changed in the charter (verified on disk, not taken from the reworker's list)

The round-1 file is not kept on disk; the `env/` scenario is untracked. So each change is established by comparing the current text with the round-1 text as quoted in the round-1 sections above.

| Round-1 item | Current text | Status |
| --- | --- | --- |
| O-1 card-paid eligible spend = whole ticket fare | Rule: "The card-paid segment's eligible spend is its equal share of the base fare recorded on the card-paid ticket … the whole base fare for a one-way ticket and half of it for a round trip." Compute adds `card_ticket_trip` and divides by `card_round_trip_segments` (2) or `card_one_way_segments` (1). The unsuperseded base clause "base fare share of the segment" now agrees. | **Closed.** No undeclared override remains. |
| O-2 "due date has passed" vs `MONTHS = 0` inclusion | Rule and baseline now read "every invoice charge whose due date falls on or before the fee date", which matches the compute. | **Closed** as a rule/compute gap. See new observation N-2. |
| O-4 `pace + 1` window vs "current agreement year" | The milestone rule now states "counted as the points accrual entries dated fewer whole calendar months before the credit date than the milestone pace plus one", and likewise for redemptions. The domestic award rule states "…dated fewer whole calendar months before the redemption date than the whole months that agreement year has run plus one". Prose now states the compute's convention exactly. | **Closed.** |
| O-5 recency with no redemption on file | Domestic award rule: "and fewer days, or no earlier redemption on file, set the listed-price percentage". | **Closed.** |
| O-6 outside-channel retro claim | Retro rule and baseline add "a ticket booked through a channel outside the tier's eligible booking channels may still be claimed, at the outside-channel claim share". The extended reading is now explicit. The base `business_points_earning` "eligible ticket" is not named in `overwrite`, so whether this broadens the base is still not declared. | **Changed; remains a latent observation.** No task's claimed ticket is outside-channel. |
| O-7 same-day entries in windows "before" the date | Late-fee, card-paid, gold, retro-volume, enrollment-fare, milestone-momentum and domestic-earning windows now read "up to and including the fee / posting / redemption / claim / credit date". The enrollment coupon window and the milestone premium-share window keep their round-1 wording, but no same-day coupon exists or is written. | **Closed** for every window a prerequisite write feeds. |
| Enrollment bonus on zero-bonus tiers | `overwrite.replaced_by` and the rule's last sentence now read "…and nothing when it has not or when the tier carries no enrollment-bonus points". The compute `result` adds `and enroll_standard_bonus > 0`. This matches the base (0 points on Corporate Preferred and above). | **Closed.** See new observation N-1. |
| task 1 O-a, edge effect vs carrier | The milestone→retro edge now has `gate: milestone_segments` (it was `milestone_year_spend`). Its `effect` names both the spend and the segment count and the tiers each "can" move. The gate binding now exists (`milestone_segments`) and is the channel that bears weight on task 1. | **Closed.** |
| O-3, O-8, O-9 | Not changed, as the reworker says. | Recorded as before. |

### Re-derived charter-global sections

- **policy_conflict_scan**
  - Subjects, targets, owners, `computes` and base refs are unchanged for all seven policies, and the round-1 overlap analysis holds.
  - Card-paid points vs retro claim: the object sets are disjoint by "booked under / without the agreement".
  - Enrollment vs milestone: the bonus grounds differ.
  - Gold vs domestic award: the award objects differ.
  - The scope split is unchanged: {gold ← late fee, gold ← card-paid} and {domestic ← milestone ← retro, domestic ← enrollment}.
- **rule_compute_equivalence**
  - A mechanical sweep ran over all seven policies. Every compute binding has a `compute_basis` entry, every entry is a verbatim sentence of the rule, and no entry is orphaned.
  - Each factor ladder is stated in the rule and implemented in its `decides` binding.
  - New bindings: `card_ticket_trip` (quoted by the new equal-share sentence) and the enrollment `result` gate (quoted by the new last sentence).
  - Round-1 gaps 1, 3 and 4 are closed (O-2, O-4, O-5 above). Gap 2 (`CFIELD` first match, O-3) remains latent and unchanged.
- **action_binding_and_uuids**
  - `task_tools.py` is byte-identical to round 1, so the round-1 conclusion carries forward on its hash: seven unique `(target_tool, computes)` pairs, no sequencing language, no prerequisite checks in the bodies, independent uuid8s.
  - No `target_tool` changed.
- **prerequisite_graph**
  - Five edges, all state-form value_input, none with a `fallback_reason`. Each `policy_source` is verbatim in its own rule. Each `resolved_by` equals the depended-on policy's `target_tool`. Each gate binding exists; `milestone_segments` is the new one.
  - The graph is acyclic, and the conditions are unchanged from round 1.
- **prerequisite_sentences**
  - The five sentences are byte-identical to round 1, so the round-1 four-point test and the one-write derivations stand. No rule gained a tool name, snake_case token or another policy's id (mechanical scan).
  - One qualification applies to sentence 5 (domestic ← enrollment) on the tiers with zero enrollment-bonus points; see N-1.
- **override_declarations**
  - The round-1 conclusions stand, with O-1 now closed: the card-paid eligible spend agrees with the unsuperseded base clause.
  - The enrollment `replaced_by` now also covers the zero-points tiers.
  - The retro outside-channel reading is still not declared against the base "eligible ticket" (O-6, latent).
  - No other base sentence is newly handled differently.
- **factor_ladders**
  - Factor counts and labels are unchanged (5/5/6/5/5/6/6; ≥2 `parameter` and 1 `method` each). Every ladder value is unchanged.
  - Baseline rules remain sentences of their rules. The card-paid and retro baselines were extended by the new equal-share and outside-channel sentences, and each still gives a definite number.
  - The round-1 realism and labelling observations (O-8) stand. The enrollment inertness on zero-bonus tiers is now moot, because the result is 0 there.

### New observations (latent; no task world reaches them)

- **N-1, enrollment "nothing" vs the domestic-award enrollment sentence on zero-bonus tiers.**
  - On Corporate Preferred, Premier and Strategic (`enrollment_bonus_points` 0), the enrollment rule now credits "nothing".
  - The domestic award rule still says "priced only after the points account carries the enrollment bonus once the agreement's flown spend since approval has reached the tier's enrollment-bonus spend". Its `condition` requires "a `business_bonus_points` entry with `bonus_reason` enrollment_bonus".
  - On such a tier the text supports three readings:
    - (a) book a zero-point enrollment entry;
    - (b) no entry is ever booked, so the domestic award is never priced;
    - (c) the sentence is vacuous.
  - Both tasks are on tiers with positive enrollment points (task 1: Business Connect Plus, 2500), and task 0's tree has no enrollment edge. No consequence can be demonstrated, so this is an observation.
  - Introduced by this round's rework.
- **N-2, late-fee "unpaid amount past due" now includes a charge due on the fee date.** The rule's opening sentence charges a fee only on invoices "still unpaid after its due date". The resolution of O-2 counts an invoice due on the fee date in the amount, although that invoice earns no fee of its own. The text is now definitional and unambiguous, and task 0 has no invoice due on its fee date. Observation.

### findings (revision 2)

No charter-global `SOURCE-POLICY RED`.

| Status | Items |
| --- | --- |
| Closed | O-1, O-2, O-4, O-5, O-7, the enrollment zero-tier item, O-a |
| Latent, unchanged | O-3, O-6, O-8, O-9 |
| New latent observations | N-1, N-2 |

### closing_checklist (revision 2)

Written after the round-2 reveal at 2026-09-24T18:11:22Z. The revision-2 charter-global section above was frozen before that reveal.

**Status: CLOSED. Both tasks PASS all four relationships in revision 2.**

- **Audit files:**
  - `0.md` and `1.md` correspond one-to-one to tasks 0 and 1, with `_difficulty.md` alongside.
  - Each file carries the untouched round-1 text followed by `## revision_2`.
  - Every revision-2 comparison section carries a PASS.
- **Round-1 red lights:**
  - The only one was task 1 F-1 (SOURCE-CHAIN RED). It is closed, and the closure was verified against `tasks/1.json` on disk (`1.md` → `revision_2`).
  - Every claim on the coordinator's list was checked against the artifacts on disk rather than taken from the list. The changes the reworker reported are all present, as the table under `revision_2` shows. The items reported as unchanged (O-3, O-8, O-9, the personas and the seeds) are unchanged.
- **Coverage and scope:**
  - The seven extended policies are fully covered.
  - The `charter_scope` split is unchanged and pairwise disjoint, and each scope spans its whole tree.
  - Task tools are byte-identical, and each uuid8 is independent.
  - GT is closed: `db_closure_matches_initial_state` is true for both tasks.
- **Problem trees:**
  - Task 0: 2 prerequisites and 2 value_input edges.
  - Task 1: 3 prerequisites and 3 value_input edges.
  - Each tree has a user-owned root and no cycle, the difficulty-wide graph is acyclic, and every edge bears weight at its own dependent. These were recomputed under the round-2 charter.
- **Factors:**
  - Every computation has 5 or 6 factors, with at least 2 `parameter` and 1 `method`.
  - Each task has at least 1 multi-source factor and at least 1 cross-difficulty factor.
  - Every factor bears weight against an honest baseline.
  - Each baseline-alone number is definite and differs from gold.
  - All figures are identical to `computations` in both tasks.
- **Regressions and new defects (none red):**
  - **R-1** (`0.md`): task 0's step-12 `spend_usd` trace quotes the superseded card-paid sentence, and the step-10 trace paraphrases the old late-fee wording. The values are unaffected.
  - **N-1** and **N-2**: latent charter observations introduced by the enrollment and O-2 rework. No task world reaches them.
  - The compute changes for O-1 (the equal per-segment share) and for the zero-bonus enrollment gate move no figure on either world. The rework introduced no new rule/compute gap: the sweep shows every basis verbatim and none missing.
- **Gates:** the coordinator's round-2 re-run on the final form reports all green (traceability deferred). The auditor did not run them.

**Per-task verdicts (revision 2):**

| Task | Verdict |
| --- | --- |
| 0 | PASS: policy self-consistency, problem tree, factors, unique solution |
| 1 | PASS: F-1 closed; policy self-consistency, problem tree, factors, unique solution |
