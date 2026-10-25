# Policy-task audit — membership_fees_and_benefits / charter-global

## charter_global_frozen

- Freeze time: 2026-10-23T20:55Z (written before either task's GT was revealed). Auditor: independent policy-task auditor (erl-task-policy-audit), revision_1.
- Frozen inputs (sha256, matching the coordinator snapshot `/tmp/erl0080_coord/snaps/membership_fees_and_benefits.r1.txt`):
  - `tasks/membership_fees_and_benefits/membership.extended.yaml` 3dbd3c57aa1ca3cf1001a0633f306b7aec0f792e09f692808cd114574234e4eb
  - `tasks/membership_fees_and_benefits/task_tools.py` 9f7f950c278347122f36db2fc9df9b47225660fc49ef627637067deabfff0e9b
  - masked views task0 7562cd87…4161e7, task1 ea7d945d…4bd5 (keep only frozen_time, user_scenario, initial_state).
- Entry conditions (Step 0): gate snapshot supplied with commands and output lines — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; masked views and hashes supplied. Entry conditions met. Traceability deferred by the coordinator.
- Read: blueprint (blueprint.yaml not needed beyond products), `db_schema.json`, `share_tools.py` signatures, `products/membership.yaml` (diff), `products/order.yaml`, `products/card.yaml` (cited sections), the extended charter, `task_tools.py`, the two masked views, `audits/render_source/XF_recipe.md`, `audits/render_source/owner_ruling.md`, and the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (build_env).
- Masked and NOT read before the freeze: `tasks/*.json`, `worklog.md`, `plan.md` (never read), every evaluation_criteria / computations / design_rationale / charter_scope / required_documents / solvability_contract / prerequisite_closure field. No recursive search touched `tasks/`.
- Scratch (re-checkable): `/tmp/erl0080_pa_membership/derive.py`, `task0.py`, `task1.py` evaluate each extended policy's `compute` with the gate's own DSL on the masked view's `initial_state` plus the auditor's own derived writes (made with the real task tools).

Base-section check: `diff <(head -n 1327 membership.extended.yaml) blueprint/products/membership.yaml` differs only by one trailing blank line — the base copy is verbatim.

### policy_conflict_scan

Seven extended policies, two trees:

| tree | root (owner) | prerequisite problems (kind) |
| --- | --- | --- |
| consumer annual | membership_ext_annual_cancel_refund → `confirm_annual_membership_cancellation_fe7f482c` (user) | membership_ext_consumer_cash_earning (value_input → bonus_net), membership_ext_consumer_return_reversal (value_input → bonus_net) |
| business | membership_ext_business_closure_refund → `confirm_business_membership_closure_a0a2c96c` (user) | membership_ext_business_cash_earning, membership_ext_business_return_reversal, membership_ext_unreturned_refund_reversal (all value_input → business_rate_cash) |

The two trees partition the seven policies (pairwise exclusive, jointly complete) — to be confirmed against `charter_scope` after the reveal.

Overlaps found:
1. **Immediate cancellation of a Northgate+ Business membership paid by external card** is claimed by two policies with different results: membership_ext_annual_cancel_refund's rule/replaced_by says "every other immediate cancellation keeps the base measure, in which …", while membership_ext_business_closure_refund's rule says such a cancellation "is worked out under this Business closure schedule". See finding PT-R1.
2. **A line refunded without a return (or returned) before its Northgate Cash earning is posted** is reduced twice: the earning schedules' kept-units basis already subtracts the refunded/returned merchandise from the earning basis, and the reversal schedules (unreturned "on any membership"; consumer return reversal "every return … against a line that earned") then reverse Cash on the same refund. Only the Business closure's prerequisite sentences carve the reduced-basis earnings out; no schedule's own rule does, and the consumer side has no carve-out at all. See PT-R3.
3. Base `membership_evt_fee_refund` "A refund never exceeds the fee it refers to, and benefits already used are never billed back." stays in force (not in either superseded_clause) while both refund schedules take amounts from the refund because benefits were used. See PT-R2.
4. Base `membership_evt_cash_earn` "a line earns only if the membership is not canceled on the fulfilment date" stays in force for Business (only the first sentence and the cap sentence are superseded), while the Business payment-hold rate gives a canceled membership a zero base rate to which the additive points are still added. See PT-R7.
5. Earning (consumer vs Business), return reversal (consumer vs Business), refund-without-return reversal: scoped by tier / by return-vs-refund record tests — no other overlap. Cross-category reads are read-only (order, card); no task tool writes an event whose base `triggers` land in another category (fee refunds are written with payment_method_type external_card, so `card:card_post_credit` does not fire; cash earn/reverse have `triggers: []`).

### rule_compute_equivalence

Sweep: every `compute_basis` quotation was checked against its own rule with whitespace normalised (scratch one-liner in this audit's transcript). All quotes are verbatim except the folded-hyphen artifacts of PT-R13. Every factor ladder tier appears as a rule sentence and as a branch of its `decides` binding; no tier lives only in compute.

Probe table (decoy / absent / second record) — mismatches are findings, matches are listed so the sweep is visible:

| policy · binding | probe | rule says | compute does | verdict |
| --- | --- | --- | --- | --- |
| both earnings · order_ref | two fulfilled orders share the latest fulfilled date | no tie rule ("the member's order that has the latest fulfilled date") | XLATEST keeps the first-recorded | PT-R5 |
| both earnings · line_ref | two lines on the order, same date | "the line recorded first" | XLATEST keeps first | match |
| both earnings · excluded lines | gift_cards / prescriptions / alcohol | rewards_excluded_purchases | three categories listed; the other excluded types have no `item_category` value in db_schema | match on reachable domain |
| consumer earning · canceled | canceled_date ≤ fulfilled | earns nothing | 0 | match |
| consumer earning · no fulfilled order | absent | — | 0 (tool refuses 0) | match |
| consumer/Business reversal · return_ref | two returns same latest date | "the one recorded first" | first kept | match |
| reversals · earning_ref | returned line never earned | earning that points to the line | earned 0 → result 0 | match |
| annual · settled_fees | Monthly→Annual plan change leaves monthly fee_charge rows | "settled annual fees" | COUNT of every fee_charge row | PT-R6(a) |
| annual/Business · recent_use_value | use before the charge date inside the month | "benefit uses dated within the one whole calendar month before the cancellation date" | within_months=1 | match (realism note O-3) |
| annual · active_card_tier | second card | card charter: one Northgate Card account at a time (card.yaml l.857) | CFIELD first active | match |
| Business earning · cap window | earning dated between "12 months before the posting day" and "12 months before today" | window anchored at the posting day | within_months=12 anchored at NOW | PT-R6(b) |
| Business earning · hold vs canceled | lapsed membership (hold, never settled, canceled) fulfilled after canceled_date | both tiers' conditions true, no precedence | hold tier first | PT-R7 |
| unreturned · return_ref | two damaged refunds on the same latest date | tie rule only between a damaged and a never-received refund | XLATEST keeps first | PT-R5 |
| unreturned · events_12m | an order_canceled / unclaimed_pickup / fee_refund refund in window | rule "the only refund without a return"; ladder "the only one of its kind" | counts every order_refund_charge row | PT-R6(c) |
| Business closure · hold_credit | days from 2026-05-15 to 2026-05-20 | "each day from that period's start to the date the fee settled" (no boundary) | DAYS() = 5 (end-exclusive) | PT-R8 |
| annual/Business · Cash recovery | grouping | "the Cash earned less the Cash reversed …, less the tier's rewards_earn_rate_pct percent of the earning bases less the reversal bases" | (E−R) − r%·(EB−RB) | PT-R9 |
| all within_months=12 reads | row dated after today; row 12 months back | "within the twelve whole calendar months before" | 0 ≤ MONTHS(d, NOW) < 12 | match |

Compute invents no basis beyond these; the rule makes no empty promise except where noted.

### action_binding_and_uuids

- Seven `(target_tool, computes)` pairs, each claimed by exactly one policy: post_member_cash_earning_0c0d8435, reverse_member_return_cash_50b9758d, confirm_annual_membership_cancellation_fe7f482c, post_business_cash_earning_affdfb03, reverse_business_return_cash_4d4108b5, reverse_unreturned_refund_cash_522719bc, confirm_business_membership_closure_a0a2c96c.
- uuid8 tails are pairwise distinct with no shared prefix/suffix or sequence pattern. No factor id is a substring of a tool name (scripted check).
- No banned substring (datetime/time/random/uuid/secrets) in task_tools.py; rounding helper is a class static method using Decimal ROUND_HALF_UP; every write tool calls ctx.create/ctx.update in its own body; bodies enforce the docstring formats (YYYY-MM-DD, positive two-decimal amounts, enum refund_basis, membership reference). No docstring example values.
- No tool body judges a prerequisite (the confirm tools do not look at earnings or reversals; the earn/reverse tools do not look at the cancellation).
- Observation: docstrings use "after" descriptively ("balance after the posting", "the cancellation falls after that window") — not a position in a sequence.
- owner=user tools are the two cancellation confirmations, legitimate under owner_ruling (a).

### prerequisite_graph

- Every extended policy has `prerequisite` filled (five `[]`, annual 2 edges, Business closure 3 edges); every `problem` is an extended policy id of this file; graph acyclic (depth 1).
- Each `policy_source` is verbatim in its own rule (scripted check); `form: state` on all five edges, no `fallback_reason` (correct); `kind: value_input` with `gate` bindings `bonus_net` / `business_rate_cash` that exist in the compute; `resolved_by` = the depended-on policy's `target_tool`; `condition` restates the sentence at the same strength (Business conditions encode "posted on the line's full net amount" as basis_amount_usd = line amount_usd). No authoring-viewpoint wording.

### prerequisite_sentences

| edge | sentence (connective) | waited state | the one write that brings it about | derivation |
| --- | --- | --- | --- | --- |
| annual ← consumer earning | "The refund is fixed only after the membership's ledger carries a Northgate Cash earning for every line …" (only after) | earning row per earning line of a fulfilled-status order | consumer earning (Business earning is scoped to Business) | sentence → find a line without an earning → consumer earning rule computes it |
| annual ← consumer reversal | "The refund is not fixed until every return … has its Cash reversal …" (not until) | reversal row per return on an earning line | consumer return reversal | sentence → find the unreversed return → consumer reversal rule |
| Business ← Business earning | "… worked out only after every line … has its earning …" | as above | Business earning | idem |
| Business ← Business reversal | "… not worked out until each return … against a line whose … earning was posted on the line's full net amount carries its reversal …" | as above | Business return reversal | idem |
| Business ← unreturned | "Before the Business refund is worked out, each refund made without a return … must carry its reversal …" | as above | refund-without-return reversal | idem |

All five pass the four-point test (connective, record-visible state in table words, no tool/policy id/row id, scope matches the condition). No second wording, no tool name in any rule, no restatement in the depended-on rules, docstrings silent about sequence. No extended rule states an undeclared cross-problem order. Base rules that state cross-problem orders (e.g. membership_trial "the first fee is charged under membership_evt_fee_charge") ground no edge — observation only.

But the waits are not satisfiable by their resolvers in every engaged world — PT-R4 — and the consumer sentences lack the reduced-basis carve-out that the Business ones carry — PT-R3.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- **membership_evt_cash_earn** (consumer earning, Business earning): S1 "earned … at rewards_earn_rate_pct of the eligible net merchandise amount …" — superseded by both (tier-scoped, siblings named) ✓; S2 rounding/posting date — followed ✓; S3 "Lines … in rewards_excluded_purchases never earn, and a line earns only if the membership is not canceled on the fulfilment date" — followed by consumer; **contradicted without declaration by Business** (PT-R7); S4 annual cap — superseded by Business with a restatement for every other membership ✓; S5 "A price adjustment granted after fulfilment does not change Northgate Cash already earned." — followed ✓; S6 posting/rounding parameters ✓. The consumer and Business replaced_by scope "the Northgate Cash posted for a fulfilled Northgate order line" covers every line while each schedule settles one selected line (PT-R4).
- **membership_evt_cash_reverse** (consumer, Business, unreturned): S1 proportional reversal — superseded by all three, scopes disjoint and naming each other ✓; S2 "Each return record reverses cash at most once and points to the earning it reverses" ✓; S3 negative balance ✓; S4 even exchange / price adjustment ✓; S5 parameters ✓. Observation O-5: the unreturned overwrite retires a clause written about returns ("returned for a refund") for refunds without a return.
- **membership_evt_fee_refund** (annual, Business closure): S1 one fee charge, credited to its method ✓; S2 once per charge ✓; S3 most recent settled charge ✓; S4 full-refund window (counting rule) ✓ consistent; S5 benefit-use condition and proration — superseded by both; **the annual replaced_by tail "every other immediate cancellation keeps the base measure" does not exclude the Business sibling, and the Business tail misstates the Annual case and restates no base measure for out-of-scope cancellations** (PT-R1); S6 monthly/free no refund ✓; S7 billing error ✓ (n/a); S8 "A refund never exceeds the fee it refers to, and benefits already used are never billed back." — **not superseded, contradicted by streaming partner month, benefit-usage withholding and the Cash recoveries** (PT-R2); S9 parameter sentence ✓.
- **membership_cancellation** (annual, Business closure): member's own decision recorded in membership_requests and confirmed ✓ (tools write a confirmed cancel_immediately request); active-status gate ✓; refund evaluated under membership_evt_fee_refund — handled through that policy's overwrite ✓.
- Disguised forms: no anonymous intermediate, no 0/1 multiplier, no dropped branch found beyond the above.

### factor_ladders

| policy | factor | label | ladder (tiers incl. fall-through) | multi-source | cross_difficulty | structural verdict |
| --- | --- | --- | --- | --- | --- | --- |
| consumer earning | delivery_program_points | parameter | 3 (1.0 / 0.5 / 0) | yes (order program AND membership tier) | order | ok |
| | tenure_points | parameter | 3 | no | — | ok |
| | kept_units_basis | method | 4 | — | order | **fails A7** (PT-R11) |
| | category_points | parameter | 3 | no | order | ok |
| | card_points | parameter | 3 | yes (line tender AND card variant/status) | card | ok |
| consumer reversal | closing_return_share | method | 3 | yes (units AND price-adjustment row) | order | ok |
| | reason_relief, tenure_relief, first_return_relief | parameter | 3 each | no | order / — / order | ok |
| annual refund | money_back | method | 3 | yes (charge date AND benefit-use rows) | — | ok |
| | recovery_share | parameter | 3 | no | — | ok (rule≠compute PT-R6a) |
| | streaming_partner_month | parameter | 3 | yes (activation date vs charge date AND 12-month window) | — | ok |
| | cardholder_courtesy | parameter | 3 | yes (card variant AND status) | card | ok |
| Business earning | payment_hold_rate | parameter | 3 | yes | — | **tiers overlap** (PT-R7) |
| | volume_points, business_card_points, pickup_points, business_tenure_points | parameter | 3 each | card: yes | order / card / order / — | ok |
| | business_kept_units | method | 4 | — | order | **fails A7** (PT-R11) |
| Business reversal | business_closing_share | method | 3 | yes | order | ok |
| | business_reason_relief, business_tenure_relief, business_count_relief, business_volume_relief, bulk_line_relief | parameter | 3 each | no | order / — / order / order / order | ok |
| unreturned | unreturned_closing_share | method | 3 | yes | order | ok |
| | unreturned_reason_relief | parameter | 3 written, **2 reachable** | no | order | **fails** (PT-R12) |
| | unreturned_tenure_relief, unreturned_count_relief, unreturned_volume_relief | parameter | 3 each | no | — / order / order | ok |
| Business closure | business_money_back | method | 3 | yes | — | ok |
| | volume_recovery_share, hold_day_credit, business_cardholder_courtesy, benefit_usage_withholding, loyalty_credit | parameter | 3 each | card: yes | order / — / card / — / — | ok (hold-day boundary PT-R8) |

Pairwise method tables (distinguishing input per pair):
- money_back / business_money_back: T1 whole fee · T2 max(prorated, fee − recent use value) · T3 prorated. T1–T3: months_left (prorated < fee whenever months_left < term_months); T1–T2: recent_use_value > 0; T2–T3: fee − recent use value > prorated. Distinct.
- closing shares (three schedules): T1 earned − already reversed · T2 earned × units/line units · T3 earned × refunded/basis. T1–T3: a price adjustment (refunded ≠ basis) or a prior reversal; T2–T3: units ratio vs amount ratio after a price adjustment; T1–T2: the closing unit vs a partial unit. Distinct.
- kept_units_basis / business_kept_units: T1 net − R · T2 net − M · T3 net − R − M · T4 net, with R = Σ order_refund_charge.amount_usd and M = Σ order_return_line.amount_usd on the line (both ≥ 0). Under each tier's own condition the omitted term is 0, so every tier equals the single closed form net − R − M; R and M are aggregates of the same field (XF A7: one input whatever the filter). Distinct methods: 2 (net; net less one aggregate). Fails.

Counts per policy (before striking): consumer earning 5 (4 parameter / 1 method), consumer reversal 4 (3/1), annual 4 (3/1), Business earning 6 (5/1), Business reversal 6 (5/1), unreturned 5 (4/1), Business closure 6 (5/1). After striking the factors that fail: consumer earning 4/0 method, Business earning 5/0 method (both below the method floor), unreturned 3 parameter + 1 method = 4 (still within bounds). Per task: tree consumer has multi-source and cross-difficulty (order, card) factors; tree Business has multi-source and cross-difficulty (order, card) factors.

Realism notes (observations, not demonstrated as "no such business would publish"): O-1 hold_day_credit halves the credit when only one attempt was declined although the suspended days are the same; O-2 the Cash recoveries and the money-back deduction look back over a window that reaches into the previous paid term (bonus Cash and benefit uses already paid for by the earlier fee); O-3 the money-back recent-use deduction can include benefit uses dated before the charge being refunded; O-4 Business benefit-usage withholding counts uses that tied with the universal order-threshold free shipping (the member received no value from the membership on those orders).

### findings

Each RED below names the tasks whose files demonstrate it.

- **PT-R1 SOURCE-POLICY (XF C16) — sibling overwrites contradict on Business cancellations.** Symptom: annual rule/replaced_by "every other immediate cancellation keeps the base measure, in which a cancellation inside the full refund window with no benefit use since the charge refunds the whole fee …, and otherwise … the fee times the unused whole months divided by term_months, rounded down …" covers a Northgate+ Business external-card cancellation, which the Business closure rule claims ("For the immediate cancellation of a Northgate+ Business membership whose most recent settled annual fee was charged to an external card, and only for such a cancellation, the refund is worked out under this Business closure schedule"). Also the Business tail "the immediate cancellation of a Northgate+ Annual membership is worked out under the annual cancellation schedule" is false for an Annual membership whose fee was charged to a Northgate Card (the annual schedule scopes it out), and the Business replaced_by restates no in-force base measure for out-of-scope cancellations. Affected: both refund policies' rule + overwrite. Bears on task1.
- **PT-R2 SOURCE-POLICY (check 1 / XF C17) — undeclared override of "benefits already used are never billed back".** Base membership_evt_fee_refund S8 is in force; annual "Streaming partner month … is taken from the refund", Business "Benefit-usage withholding … is taken from the Business refund", and both Cash recoveries reduce the refund because a benefit was used. Neither superseded_clause names S8. Bears on task0 and task1.
- **PT-R3 SOURCE-POLICY — double reduction of one refunded/returned amount.** Consumer and Business kept-units bases ("the earning basis is the net amount less the amounts so refunded" / "less the merchandise refunded on those returns") remove the refund from an earning posted after it; the unreturned schedule ("For a line … refunded without a return because the item was damaged on arrival or never received, on any membership … the Northgate Cash reversed is worked out under this … schedule") and the consumer return reversal then reverse Cash on that same refund (earned × refunded / basis, where the basis already excludes it). Only the Business closure's prerequisite sentences restrict the waits to earnings "posted on the line's full net amount"; no reversal schedule and no consumer sentence carries that restriction. Bears on task0 (second terminal state).
- **PT-R4 SOURCE-POLICY (XF D20 / C19) — resolvers settle one record, waits and scopes say "every".** Consumer/Business earning settle only "the line recorded first on the member's order that has the latest fulfilled date"; consumer/Business reversal only "the most recent return"; unreturned only "the most recent refund …". Their replaced_by retire the base clause for every line/return/refund of the scope, and the waiting sentences demand an entry for "every line" / "every return" / "each refund". Probe: a fulfilled line on an older order without an earning (or an older unreversed return) — the wait is engaged, no rule computes the missing entry (the base clause is retired, the schedule selects a different record), so the refund can never be "fixed". Task worlds are each seeded with exactly the selected record missing, so no task-level consequence; charter-level RED.
- **PT-R5 SOURCE-POLICY (XF B10) — missing tie rules.** (a) Both earnings: two fulfilled orders on the latest fulfilled date — the rule names no order; compute keeps the first-recorded. (b) Unreturned: two damaged-on-arrival (or two never-received) refunds on the latest date — the rule's tie clause only orders a damaged refund before a never-received one. Charter-level.
- **PT-R6 SOURCE-POLICY (XF B10/A8) — rule ≠ compute on reachable records.** (a) Annual recovery_share "settled annual fees" vs `COUNT('membership_events', event_type='membership_fee_charge')` — after a Monthly→Annual plan change (allowed by membership_plan_change) monthly fee rows are counted (e.g. 11 monthly + 1 annual: rule → otherwise tier, takes all; compute → third tier, takes 0.0). (b) Business earning cap "earned on the membership in the twelve whole calendar months before the posting day" vs `within_months=12` anchored at today — an earning dated 12 months before today but within 12 months before the posting day is dropped by compute. (c) Unreturned count: the ladder says "the only one of its kind", the rule "the only refund without a return", compute counts every order_refund_charge row (order_canceled, unclaimed_pickup, fee_refund included). Charter-level; no task world has such rows.
- **PT-R7 SOURCE-POLICY + SOURCE-FACTOR (XF A8, C17) — Business payment-hold rate.** Tiers "the billing period starting on the membership's payment hold date carries a declined attempt and the order's fulfilled date falls on or after that payment hold date and before the date the fee of that billing period settled" and "the membership is canceled on the fulfilled date" overlap on a lapsed membership (hold never settled, canceled_date before the fulfilled date) with values 1.0 vs 0 and no precedence (compute takes the first). The canceled tier sets only the base rate to zero, so volume/card/pickup/tenure points still earn Cash on a canceled membership, against the in-force base sentence "a line earns only if the membership is not canceled on the fulfilment date". Charter-level.
- **PT-R8 SOURCE-POLICY (XF B10 date boundary) — hold-day count.** "each day from that period's start to the date the fee settled is credited at the fee divided by days_in_year" states no inclusive/exclusive convention; compute `DAYS(held_period, charged_on)` is end-exclusive. Bears on task1.
- **PT-R9 SOURCE-POLICY (XF B12) — two groupings in the Cash recovery sentence** of both refund policies ("…, less the tier's rewards_earn_rate_pct percent of the earning bases less the reversal bases in that period" / "less rewards_base_rate_pct percent, the Northgate Rewards rate, of the earning bases less the reversal bases"). Readings: r%·(EB − RB) (compute) or r%·EB − RB. Bears on task0 and task1.
- **PT-R10 SOURCE-POLICY (XF A3/A4) — "one month's share of the fee" lives in one factor's sentence and is read by others.** Annual: defined in "Streaming partner month: … one month's share of the fee, the fee divided by term_months, …", used undefined by "Cardholder courtesy: … one month's share of the fee times courtesy_share_high …". Business: defined in "Business cardholder courtesy …", used undefined by "Benefit-usage withholding" and "Loyalty credit". A factor document rendered alone (no document references another) leaves the quantity undefined. Charter-level (rule text only; compute recomputes fee/term_months inline).
- **PT-R11 SOURCE-FACTOR (XF A7) — kept-units ladders are one formula.** See the pairwise table above: four tiers ≡ net − R − M, two distinct methods. With them struck, the consumer earning and the Business earning have no `method` factor. Bears on task0 (consumer earning) and task1 (Business earning).
- **PT-R12 SOURCE-FACTOR — unreturned_reason_relief fall-through is unreachable, baseline is a straw man.** The schedule settles only "the most recent refund without a return … made because the item was damaged on arrival or never received", so "any other refund adds nothing" (and the factor baseline `reason_fraction: 0`) applies to no refund this write can reach; the ladder has two reachable tiers. Bears on task1.
- **PT-R13 SOURCE-POLICY (XF B13, mechanical) — quotes not verbatim.** The unreturned rule reads "…, the damaged-on- arrival refund; …" (folded hyphen + space) while seven compute_basis quotes (damaged_ref, damaged_on, missing_ref, missing_on, return_ref, line_ref, earning_ref) read "damaged-on-arrival"; the Business return reversal overwrite replaced_by reads "refund- without-return" while its rule reads "refund-without-return". No semantic consequence; text fix only.

Observations: O-1…O-4 (realism, above); O-5 (unreturned overwrite retires a returns clause); O-6 "net amounts of the lines" in the Business reversal, unreturned and Business closure volume tiers is defined only in the earning policies (no task world changes tier under a net-of-refunds reading: task1 4342.83 vs 3484.52, both mid); O-7 the Business earning's volume tier and every "before today" window key the earning on the posting day rather than the line's own fulfilled date (no tier change on task1: 4314.33 at 2026-05-18 vs 4342.83 today); O-8 base cross-problem order sentences (membership_trial, membership_cancellation "A trial is canceled under membership_trial") ground no edge.

## closing_checklist

Written after both reveals (nothing above this heading was changed after them). The difficulty does not close in revision_1:
- Per-task files 0.md and 1.md correspond to tasks/0.json and tasks/1.json; both comparison sections are RED (GT equals the frozen derivation on every argument and every factor figure, but the charter admits other defensible answers and two computations lack a valid method factor).
- Scopes: charter_scope task0 = {consumer earning, consumer return reversal, annual refund} + their three tools; task1 = {Business earning, Business return reversal, refund-without-return reversal, Business closure} + their four tools — pairwise disjoint and jointly complete over the seven extended policies; uuid8s independent.
- Problem trees: task0 n = 2 (2 value_input), task1 n = 3 (3 value_input), each root an owner=user confirmation, acyclic, every edge load-bearing and unmet at the opening — PASS.
- Factors: PT-R11 (both earning computations without a valid method factor) and PT-R12 fail; every other factor bears weight against an honest baseline with a definite fall-back different from gold.
- Instantiation gates not re-run by this auditor (coordinator snapshot r1 cited).
- Open charter-level REDs: PT-R1 … PT-R13 (see § findings).

VERDICT revision_1: task0=RED task1=RED charter=PT-R1,PT-R2,PT-R3,PT-R4,PT-R5,PT-R6,PT-R7,PT-R8,PT-R9,PT-R10,PT-R11,PT-R12,PT-R13

## revision_2

### charter_global_frozen (revision_2)
- Freeze time 2026-10-23T21:15Z, same auditor. Snapshot executed `/tmp/erl0080_coord/snapshot.sh membership_fees_and_benefits 2` (2026-10-23T21:10:29Z): masked views unchanged (task0 7562cd87…4161e7, task1 ea7d945d…4bd5); `membership.extended.yaml` **7714518233fbc5e3aa703334ef0ffdcd893148d9dddfc0397b81cc2a41d23c50** (changed from 3dbd3c57…); `task_tools.py` 9f7f950c… (unchanged); blueprint products unchanged; gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Base section still verbatim (diff = trailing blank line only).
- Because the charter hash changed, every charter-global section is re-derived below; the tool module is unchanged, so `action_binding_and_uuids` is carried forward by reference (hash 9f7f950c…) except where the new scopes change the policy-to-tool claims (PT-R16).
- Inputs read: `rework_claims_r2.md` (claims by item id), the new charter (copy at `/tmp/erl0080_pa_membership/r2/ext.yaml`), `worklog.md` last line only ("REWORK round 2: gates 7/7 green"). tasks/*.json not read before this section and the per-task revision_2 freezes. Recompute: `/tmp/erl0080_pa_membership/task0.py`, `task1.py` (re-run on the new charter), probes `/tmp/erl0080_pa_membership/r2/probes.py`.

### status of each round-1 RED

| id | claim | verdict r2 | evidence |
| --- | --- | --- | --- |
| PT-R1 | closed | **closed** | annual tail "…the immediate cancellation of a Northgate+ Business membership whose most recent settled annual fee was charged to an external card is worked out under the Business closure schedule, and every other immediate cancellation keeps the base measure…"; Business tail names the Annual external-card case; base measure restated in both. |
| PT-R2 | closed | **not closed — recurs as a sibling-tail conflict (XF C16)** | both policies now retire "A refund never exceeds the fee it refers to, and benefits already used are never billed back." for their own cancellations, but each replaced_by ends "for every other cancellation a refund never exceeds the fee it refers to, and benefits already used are never billed back" without excluding the sibling that retires the same sentence. The annual text therefore keeps the sentence in force for a Business closure cancellation and the Business text keeps it in force for an Annual external-card cancellation. |
| PT-R3 | closed (class) | **closed** for the double reduction (every reversal rule: "…reverses nothing, because that earning already leaves out the units returned or refunded"; compute guard `earned_basis < line_net_amount`; consumer wait narrowed to full-net earnings). Task0's refund-without-return reversal now evaluates to 0 and the tool refuses 0 (`task0.py` "WITH EXTRA UNRETURNED": Error, refund stays 91.86). The record test chosen has its own defect → PT-R14 (new). |
| PT-R4 | closed | **closed** for satisfiability (every non-selected line/return/refund keeps a restated base measure). New ownership defect of those restated measures → PT-R16 (new). |
| PT-R5 | closed | **closed** (earnings: "…and when several such orders share that date, on the one of them recorded first"; unreturned: "among refunds of one kind on that date, the one recorded first"). Probes P1 (two orders fulfilled 2026-10-06 → first-recorded b8bbf791) and P2b (two never-received refunds same date → first-recorded 1e145ea7) match the rule. |
| PT-R6 (a)(b)(c) | closed | **closed**: (a) `fee_type='annual_fee'` — probe P4 (monthly decoy row) → 2; (b) cap sentence now "…before today, the day the earning is booked…" = compute; (c) count filtered to the two reasons, rule and ladder say so — probe P6b (order_canceled decoy) → 1. |
| PT-R7 | closed | **closed**: hold tier requires "the membership is not canceled on the fulfilled date"; canceled → "the line earns nothing at all" (`excluded_line` includes canceled). Probe P8 (lapsed, canceled 2026-05-17, fulfilled 2026-05-18) → base_rate 0, result 0. Tiers disjoint. |
| PT-R8 | closed | **closed**: "each day counted from that period's start date through the day before the fee settled" = DAYS() end-exclusive (5 days on task1). |
| PT-R9 | closed | **closed**: recovery split into single-reading sentences ("The member-bonus Cash is the net Cash minus the base-rate Cash. The net Cash is … The base-rate Cash is … of the net basis. The net basis is …"), same in the Business policy and both baseline.rule texts. |
| PT-R10 | closed | **closed**: annual courtesy, Business usage withholding and loyalty credit each define "one month's share of the fee, the fee divided by term_months". |
| PT-R11 | closed | **closed under the XF A7 pairwise test**: T1 net×(bought−refunded)/bought (quantity input + rounding), T2 net − returned merchandise (amount aggregate), T3 both, T4 net — every pair has a distinguishing input (quantity vs amount; return rows; refund rows). Observation O-9: the four tiers are still restrictions of one closed form RND(net×(B−U)/B) − M (the omitted term is zero under each tier's own condition). |
| PT-R12 | closed | **closed**: tiers damaged on arrival (0.2) / never received on a Ship to Home, Same-Day or Large-Item order (0.1) / never received on any other order (0, = baseline) — the third tier is reachable (order charter: missing items on Order Pickup / Drive Up orders are refunded with reason item_not_received within 2 days), so the baseline is a real treatment. |
| PT-R13 | closed | **closed**: whitespace-normalised sweep — every compute_basis quote, replaced_by, baseline sentence and policy_source is verbatim in its rule; no "x- y" fold artifacts remain. |

### re-derived charter-global checks (changed policies)

- policy_conflict_scan: earning siblings and reversal siblings now name each other's settled records; refund siblings name each other in overwrite[0] but not in overwrite[1] (PT-R2). Scopes of the two trees still partition the seven policies.
- rule_compute_equivalence: verbatim sweep passes; probes P1, P2b, P4, P6b, P8 match; new mismatches PT-R14 (P3) and PT-R15 (P5, P6, P7).
- prerequisite_graph / prerequisite_sentences: five edges unchanged except the annual E2 sentence ("…against a line whose Northgate Cash earning was posted on the line's full net amount…"), verbatim in the rule, condition at the same strength (basis_amount_usd = line amount_usd). Single-reading derivation holds on both task worlds; PT-R16 bears on the "exactly one write" requirement only for non-selected records.
- override_declarations: membership_evt_fee_refund S8 now declared by both refund policies (sibling tail defect PT-R2); everything else as round 1 with PT-R1/R4/R7 resolved.
- factor_ladders: counts per policy unchanged (consumer earning 4 parameter + 1 method, consumer reversal 3+1, annual 3+1, Business earning 5+1, Business reversal 5+1, unreturned 4+1, closure 5+1); every ladder ≥ 3 reachable tiers, distinct outcomes; multi-source and cross-difficulty factors present in both trees. Realism observations O-1…O-4 kept (reworker disputes; no "no such business would publish" demonstration).

### findings (revision_2)

- **PT-R2 SOURCE-POLICY RED (reopened, XF C16).** Annual overwrite[1] / rule: "For a cancellation this annual cancellation schedule handles, … ; for every other cancellation a refund never exceeds the fee it refers to, and benefits already used are never billed back." Business overwrite[1] / rule: the mirror text. Neither excludes the sibling's cancellations by name, so each policy keeps the retired sentence in force for the other's case. Bears on task0 and task1.
- **PT-R14 SOURCE-POLICY RED (new, XF B10/B14).** The PT-R3 record test "a line whose Northgate Cash earning was posted on a basis below the line's net amount reverses nothing, because that earning already leaves out the units returned or refunded" also catches an earning posted under the restated base measure, whose basis is "the amount actually paid for the line after item promotions, price adjustments already granted at the time of fulfilment and the Northgate Card discount" — below the line's net amount whenever a price adjustment preceded fulfilment, although nothing was left out for returned units. Probe P3 (scratch copy of task0: line 100.00 ordered 2026-09-01, price drop 10.00 on 2026-09-05, fulfilled 2026-09-08, base-measure earning 0.90 on 90.00, whole line returned 2026-10-15 as the most recent return): consumer schedule → 0, the explanatory clause is false, and the member keeps all Cash on a fully returned line. Same text in the three reversal rules and in the three restated base measures. Charter-level (no task world has such an earning).
- **PT-R15 SOURCE-POLICY RED (new to the report, pre-existing in revision_1; XF B10 absent record).** (a) Consumer and Business earning: with no fulfilled-status order the compute raises TypeError in `excluded_or_closed` / `excluded_line` (`'<=' between str and None`; probe P5) — the revision_1 probe table row "consumer earning · no fulfilled order → 0 (tool refuses 0)" was wrong and is corrected here. (b) All three reversal schedules: when the selected return/refund's line has no earning and the units fall short without a price adjustment, `earned * refunded_merch / earned_basis` divides by zero before the result guard; the rules state no outcome for "no earning points to the line". Probes: task0 opening world, refund-without-return schedule (wipes line not yet earned) → ZeroDivisionError (P6); a partial return of a never-earned alcohol line as the most recent return → ZeroDivisionError (P7). Charter-level; gold never evaluates these states.
- **PT-R16 SOURCE-POLICY RED (new, check 6 / check 3).** The PT-R4 restatements give the same base-measure entry to several policies with different target tools: "every other fulfilled Northgate order line of a membership holder keeps the base measure" is stated by both earning policies (post_member_cash_earning_0c0d8435 and post_business_cash_earning_affdfb03), and "every other return or refund keeps the base measure …" by all three reversal policies (reverse_member_return_cash_50b9758d, reverse_business_return_cash_4d4108b5, reverse_unreturned_refund_cash_522719bc). In a world where a non-selected line lacks its earning, the annual wait "…a Northgate Cash earning for every line…" is brought about by either earning write — two candidate writes for one hop. Not engaged on either task world.
- Observations: O-1…O-5, O-7, O-8 carried (reworker's dispute noted); O-6 closed for the volume sentences but "the line's net amount" in the consumer return reversal rule and the annual wait sentence is still defined only in the earning policies; O-9 (PT-R11 closed form, above).

### closing_checklist (revision_2)
Not closed: PT-R2, PT-R14, PT-R15, PT-R16 open; per-task results in 0.md / 1.md § revision_2. Gates per the round-2 snapshot (7/7 green); not re-run by the auditor.

VERDICT revision_2: task0=RED task1=RED charter=PT-R2,PT-R14,PT-R15,PT-R16

## revision_3

### charter_global_frozen (revision_3)
- Freeze 2026-10-24T13:20Z, same auditor. Snapshot executed `/tmp/erl0080_coord/snapshot.sh membership_fees_and_benefits 3` (2026-10-24T13:16:52Z): masked views unchanged (task0 7562cd87…4161e7, task1 ea7d945d…4bd5); `membership.extended.yaml` **9ded6000b0a25dab33ca4275bfdb2a268351261ca3fff441cba679d29bcbfeab**; `task_tools.py` **e55b2956b58b52aac76572b1a7bb134c665a0ea32b9fbc66bd5d3b6d9eae23db** (both changed); blueprint products unchanged; gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Base section verbatim.
- Both shared inputs changed → every charter-global section re-derived, `action_binding_and_uuids` included. Read: `rework_claims_r3.md`, the charter (copy `/tmp/erl0080_pa_membership/r2/ext_r3.yaml`), `task_tools.py` in full, `worklog.md` last line ("REWORK round 3: gates 7/7 green"). tasks/*.json not read before this section and the per-task revision_3 freezes. Recompute: `task0.py`, `task1.py`, `r2/probes.py` (re-run), new `r2/probe_r3.py`.

### status of each revision_2 RED

| id | verdict r3 | evidence |
| --- | --- | --- |
| PT-R2 | **closed** | both overwrite[1] tails now read "for every cancellation that neither this annual cancellation schedule nor the Business closure schedule handles …" / "…neither this Business closure schedule nor the annual cancellation schedule handles …"; exhaustive sibling-tail sweep: both refunds' overwrite[0] ("every immediate cancellation that neither … handles"), both earnings ("every fulfilled Northgate order line that neither the consumer nor the Business earning schedule settles"), all three reversals ("every return or refund that none of the consumer return, Business return and refund-without-return reversal schedules settles"); the Business cap tail has no sibling. No member of the class remains. |
| PT-R14 | **closed; withdrawn as demonstrated** | the reworker's premise holds: order charter `order_price_adjustment` (order.yaml l.870–871) "No adjustment is made on units already returned or on an order not yet fulfilled, which instead is charged the price at fulfilment" — my revision_2 probe world (price drop before fulfilment) is not a state the order charter produces, so the revision_2 demonstration was invalid (auditor error, recorded here). The re-keyed test ("A return reverses nothing when the earning's basis_amount_usd already equals the line's kept-units basis …") also reverses on that world (P3 → 0.81). The re-key opens PT-R17 (below). |
| PT-R15 | **closed** | earnings: "when the member has no Northgate order in fulfilled status, nothing is posted" + `order_ref == None` guard (P5 → 0); reversals: "when no such return is recorded or no earning points to that line, nothing is reversed" + `earning_rate` zero branch + `earned <= 0` guard (P6 opening world → no error, P7 never-earned alcohol line → 0); refunds: "When the membership carries no settled annual fee charge, nothing is refunded" + None-safe dates. |
| PT-R16 | **closed** | every scope is one exact record test stated in the rule and in the waiting sentence; records outside it "stay under the base … rule, which no schedule of this charter prices or posts"; the five earn/reverse tools refuse records outside their test and the wrong tier (probe: earning on the 2025-11-20 vacuum line → "Error: the line is not the earliest-recorded line …"; reversal of a no-longer-most-recent return → "Error: the record is not the member's most recent return …"). One writer per record. |
| O-6 remainder | closed | each reversal and refund rule defines "A line's net amount is the amount charged for the line after item promotions and the Northgate Card discount." |

### re-derived charter-global checks (revision_3)
- Verbatim sweep (compute_basis, replaced_by, baseline sentences, policy_source): all pass; no fold artifacts; no factor id inside a tool name; no banned imports in task_tools.py.
- Probes on every changed read: ties P1 (two orders fulfilled the same latest date → first-recorded, rule and `_Scope.latest` agree), P2/P2b (same-day same-reason refunds → first-recorded), decoys P4 (monthly fee row → 2), P6/P6b (order_canceled refund → 1), lapse P8 (→ 0), absent P5/P6/P7 (no crash, 0), second record P17 (below).
- Tools (re-derived): bodies call ctx.create/update themselves; the confirm tools are unchanged and judge no prerequisite; the earn/reverse tools now check tier, the selected record and that the earning id belongs to the referenced line — scope and reference checks of their own policy, not of the root's waits. Docstring Returns texts describe every new refusal; no ordering words about other actions. uuid8s unchanged, independent. Observation O-11: the refusal texts restate each schedule's record selector, so an agent that picks the wrong record is told the selection rule by the environment.
- Prerequisite graph and sentences: five edges, state form, verbatim, connectives intact; each waiting sentence now names exactly the record its resolver settles (single writer, satisfiable). Edge conditions match.
- Factors: counts unchanged (consumer earning 4 parameter + 1 method, consumer reversal 3+1, annual 3+1, Business earning 5+1, Business reversal 5+1, unreturned 4+1, closure 5+1); closing-share baselines now `earning_rate * refunded_merch` (same number when an earning exists). Ladders as revision_2.

### findings (revision_3)
- **PT-R17 SOURCE-POLICY RED (new; introduced by the PT-R14 re-key).** The waits and the schedules now use different record tests for when a reversal is owed. Waits (annual E2, Business E2, Business E3): owed only "when it is against a line whose Northgate Cash earning was posted on the line's full net amount". Schedules (all three reversal rules): owed unless "the earning's basis_amount_usd already equals the line's kept-units basis … less the merchandise refunded on every return of the line". An earning posted on a kept-units basis before a later return or refund satisfies neither: the wait does not require the reversal, the schedule prices one. Probe P17 (`r2/probe_r3.py`, task0 copy): wipes earning 0.78 on 20.88 (after the 10.44 never-received refund), then a 1-unit return of 10.44 on 2026-10-15 (most recent return) → consumer schedule 0.35 (kept-units basis now 10.44 ≠ 20.88); the annual refund is 91.46 without that reversal and 91.59 with it — both defensible. Members: annual cancellation E2 vs consumer return reversal; Business closure E2 vs Business return reversal; Business closure E3 vs refund-without-return reversal. Charter-level: neither task world contains such a record (task0's only return is on a full-net earning; task1's monitor return and coffee-maker refund are on full-net earnings; the printer refund is not the selected refund).
- Observations: O-1…O-5, O-7, O-8 carried (reworker's dispute noted); O-9 kept; O-11 new (above); O-12 the coarse scopes leave older unreversed returns and older unearned lines "under the base … rule, which no schedule of this charter prices or posts" — consistent and stated, but such Cash entries are owed by the base rule and can never be written in this charter (P17 world: the mixer return is no longer the most recent return, so its reversal can no longer be posted); O-13 compute picks the selected line with XLATEST by line event_date while the rule and `_Scope.priced_line` take the first-recorded line — identical whenever an order's lines share one date, which is how the order charter posts them.

### closing_checklist (revision_3)
Not closed at charter level: PT-R17 open. Per-task results in 0.md / 1.md § revision_3. Gates per the round-3 snapshot (7/7 green), not re-run by the auditor.

VERDICT revision_3: task0=PASS task1=PASS charter=PT-R17

## revision_4

### charter_global_frozen (revision_4)
- Freeze 2026-10-24T13:42Z, same auditor. Snapshot executed `/tmp/erl0080_coord/snapshot.sh membership_fees_and_benefits 4` (2026-10-24T13:41:39Z): masked views unchanged (task0 7562cd87…4161e7, task1 ea7d945d…4bd5); `membership.extended.yaml` **5d2eaec76a15c9fa7ec880b08e50731949508ab4e49677c03e0afc9a2c300ec4** (changed); `task_tools.py` e55b2956… (unchanged since revision_3); blueprint products unchanged; gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Base section verbatim.
- Read: `rework_claims_r4.md`, `diff` of the revision_3 charter copy against the new one (`/tmp/erl0080_pa_membership/r2/ext_r3.yaml` vs `ext_r4.yaml`), `worklog.md` last line ("REWORK round 4: gates 7/7 green"). tasks/*.json not read before this section and the per-task freezes.
- Scope of change (from the diff): only the owed-reversal sentence of the three reversal rules (and their compute_basis quotes) and the waiting sentences annual prerequisite[1], Business prerequisite[1] and [2] (rule, policy_source, condition). No compute, factor, ladder, baseline, overwrite or tool change. Sections not touched by the diff (action_binding_and_uuids with the unchanged tool module, factor_ladders, override_declarations) are carried forward from revision_3 on the strength of the two hashes and the diff; the touched ones are re-derived below.

### status of the revision_3 RED
| id | verdict r4 | evidence |
| --- | --- | --- |
| PT-R17 | **closed (whole class)** | one test clause — "the earning basis recorded on the Northgate Cash earning that points to its line differs from that line's kept-units basis, which is the line's net amount times the units bought less every unit refunded without a return on the line, divided by the units bought and rounded half up to the cent, less the merchandise refunded on every return of the line" — occurs verbatim once in each reversal rule's owed-reversal sentence and in all three waiting sentences (scripted count: consumer reversal 1, Business reversal 1, unreturned 1, annual rule 1 = prerequisite[1], Business closure rule 2 = prerequisite[1] and [2]); "full net amount" no longer occurs in any rule. All three pairs (annual E2 / consumer return reversal, Business E2 / Business return reversal, Business E3 / refund-without-return reversal) now owe a reversal on the same records. Probe P17 re-run: the 1-unit return after the kept-units wipes earning is now both priced (0.35) and waited on, so the refund has the single value 91.59. |

### re-derived checks on the changed text
- rule_compute_equivalence: the schedules' compute (`ABS(earned_basis - kept_units_basis_now) < 0.005` → 0, `earned <= 0` → 0) implements "differs … otherwise nothing is reversed" and "no earning points to that line, nothing is reversed"; compute_basis quotes verbatim; probes P1, P2/P2b, P3, P4, P5, P6/P6b, P7, P8, P17 re-run — all match the rules.
- prerequisite_sentences / graph: each changed sentence keeps its connective ("is not fixed until", "is not worked out until", "Before … must"), names record-visible state in table words, no tool or id, single writer per waited record (tools refuse others). Conditions encode the same test at the same strength (RND(line amount_usd × (quantity − refunded quantity)/quantity, 2) − returned amount_usd). Absent earning: the waiting clause presupposes "the Northgate Cash earning that points to its line", so a line without an earning is not waited on, matching the schedules' "no earning points to that line, nothing is reversed". On both task worlds every waited record is engaged and false at the opening: mixer return 2faf4e07 (basis 399.99 vs kept-units 30.00), monitor return cc520a87 (1086.36 vs 834.17), coffee-maker refund c7793dee (189.99 vs 0.00).
- XF sweep on the changed policies: A (factors untouched), B (rule = compute, verbatim, single reading, no fold artifacts), C (overwrites untouched), D (edges engaged, unmet, satisfiable, single writer), E (tools unchanged), F (seeds unchanged) — no member of any class found.

### findings (revision_4)
- No RED remains at charter level. Observations carried: O-1…O-5, O-7, O-8 (reworker disputes), O-9, O-11, O-12, O-13.

### closing_checklist (revision_4)
- Per-task files 0.md and 1.md correspond to tasks/0.json and tasks/1.json; old revisions kept above; both revision_4 comparisons PASS (see those files).
- Scopes: task0 {consumer earning, consumer return reversal, annual refund} + 3 tools; task1 {Business earning, Business return reversal, refund-without-return reversal, Business closure} + 4 tools — pairwise disjoint, jointly complete; uuid8s independent and frozen.
- Trees: task0 n = 2 (2 value_input), task1 n = 3 (3 value_input); each root an owner=user confirmation (owner ruling (a)); acyclic; every edge unmet at the opening and load-bearing; no tool judges a prerequisite.
- Factors: every computation 4–6 factors with ≥ 2 parameter and 1 method; multi-source and cross-difficulty (order, card) factors in both trees; every factor bears weight against an honest baseline; each baseline gives a definite number different from gold.
- Gates: round-4 snapshot 7/7 green (coordinator-run; not re-run by the auditor).

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

### charter_global_frozen (revision_5)
- Freeze 2026-10-24T23:10Z, same auditor. Snapshot executed `/tmp/erl0080_coord/snapshot.sh membership_fees_and_benefits 5` (2026-10-24T23:08:01Z): masked views unchanged (task0 7562cd87…4161e7, task1 ea7d945d…4bd5); `membership.extended.yaml` **b1ccc410639dbb92b85106d14882d7860549cf6b70d3fdc0dd79d841da89984b**; `task_tools.py` **08128eccff498a3d37ef3ae3612e9301fdb55410605f4efc4e5d8a6a9c7d5911** (both changed); blueprint products unchanged; gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Base section verbatim.
- Read: `rework_claims_r5.md`; the KB-audit items src1/src2 (`audits/policy_kb/membership_fees_and_benefits/_difficulty.md` lines 17–18, this difficulty's own KB audit); diffs of the revision_4 copies against the new charter and tool module (`/tmp/erl0080_pa_membership/r2/ext_r4.yaml`/`ext_r5.yaml`, `tt_r4.py`/`tt_r5.py`); `worklog.md` last line ("REWORK round 5: gates 7/7 green"). tasks/*.json not read before this section and the per-task freezes.
- Scope of change: Business earning hold-tier sentence and ladder tier 1; a posting test sentence in both earning rules; the earning waits (annual prerequisite[0], Business prerequisite[0]); "When the refund comes to zero, …" in both refund rules and baselines; the two confirmation tools accept 0.00 and then book the request and closure with no refund entry (docstrings updated). No compute, factor value, overwrite or other tool change. Untouched sections carried forward from revision_4 on the diff.

### status of the KB-surfaced source items
| id | verdict r5 | evidence |
| --- | --- | --- |
| src1 (hold tier silent on an unsettled held fee) | **closed as to the silence; new wording defect PT-R18** | the tier now reads "… falls on or after that payment hold date and before the date the fee of that billing period settled, or while that fee has not yet settled …"; probe src1a (held fee removed, membership on payment hold, printer fulfilled 2026-05-18) → hold rate 1.0, result 9.31, as the rule intends. See PT-R18 for the attachment of "or while". |
| src2 (zero-amount class) | **closed (all members)** | (a) both refund rules and baselines: "When the refund comes to zero, the cancellation is still recorded and confirmed, and no refund entry is booked."; both confirmation tools accept 0.00 (probe on task0 copy: "… request mrq_… confirmed, refund none of 0.00 USD, no refund entry booked …", holding canceled, one confirmed request, no membership_fee_refund row; −0.01 refused), so the schema's "positive" amount_usd is respected. (b) both earning rules: "An earning is posted for the line this … schedule settles only when …; otherwise nothing is posted" with the same test stated in the matching waits (Business adds "the Northgate Cash earned on the membership in the twelve whole calendar months before today is below the tier's annual Northgate Cash limit", defined as rewards_annual_earn_cap_usd in both Business rules). Probes: cap reached (500.00) → 0, wait not engaged; 0.12 consumer line (3.75 % → 0.0045) → 0, wait not engaged. No other zero-amount write in the charter (the three reversal tools: a zero reversal is "nothing is reversed" and engages no wait since revision_4). |
| PT-R17 (revision_3) | still closed | P17 re-run → 0.35 priced and waited; refund single value 91.59. |

### re-derived checks on the changed text
- Verbatim sweep (compute_basis, replaced_by, baseline sentences, policy_source): pass; no fold artifacts; no banned imports; tool bodies call ctx.create/update themselves and enforce the new docstring (0.00 or positive, two decimals, no refund row at 0.00).
- Probes re-run: P1, P2/P2b, P3, P4, P5, P6/P6b, P7, P8, P17, src1a/src1b, cap, tiny line — all match compute; rule matches compute except PT-R18.
- Waits: the two earning waits now carry the posting test word for word with the earning rules; on both task worlds they name the same line as before and are false at the opening (wipes line earns 0.78 ≥ 0.01; printer line earns 9.31, twelve-month Cash 114.38 < 500.00).
- Observation O-16 (pre-existing, DSL): with a cap remainder of 0.02 the Business compute returns 0.019999999999981810 (`MN(raw_earning, MX(0, cap - cash_12m))` is not rounded); within the 1e-6 tolerance and the tool takes 0.02, so no scored consequence.

### findings (revision_5)
- **PT-R18 SOURCE-POLICY RED (new, wording of the src1 fix; XF A8/B12 class).** Rule sentence and ladder tier 1 of payment_hold_rate: "the order's fulfilled date falls on or after that payment hold date and before the date the fee of that billing period settled, or while that fee has not yet settled". The "or while …" branch can attach to "before the date … settled" (compute: on/after the hold date AND (before settlement OR unsettled)) or stand alone (any fulfilled date while the held fee is unsettled, including one before the hold date). Probe src1b (task1 copy: held fee unsettled, membership on payment hold, latest fulfilled order on 2026-05-10, before the 2026-05-15 hold date): compute → base rate 2.0, earning 11.85; the stand-alone reading → hold rate 1.0, earning 9.31. Charter-level: on task1's world the order was fulfilled after the hold date and the fee settled on 2026-05-20, so both readings give 9.31.
- Observations carried: O-1…O-5, O-7, O-8, O-9, O-11…O-14; new O-16 (above).

### closing_checklist (revision_5)
Not closed at charter level: PT-R18 open. Per-task results in 0.md / 1.md § revision_5. Gates per the round-5 snapshot (7/7 green), not re-run by the auditor.

VERDICT revision_5: task0=PASS task1=PASS charter=PT-R18

## revision_6

### charter_global_frozen (revision_6)
- Freeze 2026-10-24T23:28Z, same auditor. Snapshot executed `/tmp/erl0080_coord/snapshot.sh membership_fees_and_benefits 6` (2026-10-24T23:27:53Z): masked views unchanged (task0 7562cd87…4161e7, task1 ea7d945d…4bd5); `membership.extended.yaml` **32dbad134f91f7fbf3702e36988fbae9916b117305096adb0462dfd3d4cb2249** (changed); `task_tools.py` 08128ecc… (unchanged, byte-identical to the revision_5 copy); blueprint products unchanged; gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Base section verbatim.
- Read: `rework_claims_r6.md`; diff of the revision_5 charter copy against the new one (`/tmp/erl0080_pa_membership/r2/ext_r5.yaml` / `ext_r6.yaml`); `worklog.md` last line ("REWORK round 6: gates 7/7 green"). tasks/*.json not read before this section and the per-task freezes.
- Scope of change: only the Business earning's payment-hold sentence, its three compute_basis quotes (held_period_settled, held_declines, base_rate) and payment_hold_rate ladder tier 1. Compute, every other policy, the tools and the seeds are unchanged; all other sections carried forward from revision_5 on the diff and the tool hash.

### status of the revision_5 RED
| id | verdict r6 | evidence |
| --- | --- | --- |
| PT-R18 | **closed** | the condition is now a definition with one reading: "an order is held when it was fulfilled on or after the membership's payment hold date, the billing period starting on that payment hold date carries a declined attempt, and the fee of that billing period settled after the fulfilled date or has not yet settled", followed by "When the membership is not canceled on the fulfilled date and the order is held, the Business base rate is hold_rate_pct …"; the ladder tier mirrors it. The "or" now sits inside the settlement condition only, so the on-or-after-the-hold-date requirement binds every held order. Matches compute `(canceled_date or '9999-12-31') > fulfilled_on and held_declines > 0 and payment_hold_date <= fulfilled_on and fulfilled_on < (held_period_settled or '9999-12-31')`. |

### probes on the changed read (task1 copies, `r2/probe_r5.py`)
- src1a: held fee unsettled, membership on payment hold, fulfilled 2026-05-18 (after the hold date) → held, rate 1.0, earning 9.31.
- src1b: held fee unsettled, latest order fulfilled 2026-05-10 (before the 2026-05-15 hold date) → not held, rate 2.0, earning 11.85 — the rule now gives the same.
- Same-day tie: fee settled on the fulfilled date 2026-05-18 → "settled after the fulfilled date" false → rate 2.0, earning 12.69 (rule and compute agree).
- Decoy: a declined attempt in an older billing period (2025-05-15) → not counted (the test reads the period starting on the payment hold date) → 1.0, 9.31.
- Absent / lapse: P5 (no fulfilled order → 0) and P8 (lapsed and canceled → 0) re-run, unchanged.
- XF sweep on the changed policy: A (factor structure unchanged; ladder ≥ 3 disjoint tiers, the canceled tier excluded from the held tier explicitly), B (rule = compute on every probe, verbatim quotes, single reading), C/D/E/F unchanged — no member of any class found. Verbatim sweep of every policy passes.

### findings (revision_6)
- No RED remains at charter level. Observations carried: O-1…O-5, O-7, O-8, O-9, O-11…O-14, O-16.

### closing_checklist (revision_6)
- Per-task files 0.md and 1.md correspond to tasks/0.json and tasks/1.json; all old revisions kept; revision_6 comparisons below in those files.
- Scopes pairwise disjoint and jointly complete over the seven extended policies; uuid8s independent and frozen.
- Trees: task0 n = 2, task1 n = 3, all edges value_input, unmet at the opening and load-bearing; roots are owner=user confirmations under owner ruling (a); no tool judges a prerequisite; acyclic.
- Factors: 4–6 per computation, ≥ 2 parameter and 1 method each, multi-source and cross-difficulty (order, card) factors in both trees, every factor bears weight against an honest baseline with a definite fall-back different from gold.
- Gates: round-6 snapshot 7/7 green (coordinator-run; not re-run by the auditor).

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

### charter_global_frozen (revision_7)
- Freeze 2026-10-24T23:45Z, same auditor. Snapshot executed `/tmp/erl0080_coord/snapshot.sh membership_fees_and_benefits 7` (2026-10-24T23:44:16Z): masked views unchanged (task0 7562cd87…4161e7, task1 ea7d945d…4bd5); `membership.extended.yaml` 32dbad13… (**unchanged**, byte-identical to the revision_6 copy); `task_tools.py` **c46346f5c2168b6e6fc9b93cd649849640384d379931fa0b01bbaf4f96aa32f1** (changed); blueprint products unchanged; gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Read: `rework_claims_r7.md`; `audits/render_source/membership_fees_and_benefits/render_r2.md` (renderer STOP: the two confirmation docstrings said every call books a refund entry and declared one receipt, while the 0.00 path books none and returns a second receipt); diff of the revision_6 tool copy against the new one; `worklog.md` last line ("REWORK round 7: gates 7/7 green").
- Charter unchanged → every charter section carried forward from revision_6 by hash. Tool module: only the docstrings of confirm_annual_membership_cancellation_fe7f482c and confirm_business_membership_closure_a0a2c96c changed; an AST comparison with docstrings stripped shows every function body and signature identical to revision_6 (`bodies identical: True`).

### status of the renderer-surfaced item
| item | verdict r7 | evidence |
| --- | --- | --- |
| confirmation docstrings vs bodies at a 0.00 refund | **closed** | each opening now says the call "records the … request as confirmed and closes the membership today …. When the refund is above 0.00 the call also books one refund entry …; when the refund is 0.00 it books no refund entry."; Returns declares both receipts word for word, matching the body's two return strings (scripted literal check). Probe (task0 copy): 0.00 → "… refund none of 0.00 USD, no refund entry booked against fee cac6b543-…, status canceled.", holding canceled, one confirmed request, no refund row; −0.01 refused with the declared error. |
| same-class sweep, other five tools | **no defect** | every success return string of the earn/reverse tools appears in its docstring's declared receipt; refusals are covered by each "Error:" sentence (checked in revision_3, bodies unchanged since). XF E24 (docstring claims no effect the body lacks, body enforces what the docstring declares) holds for all seven tools; no concrete example values; no ordering words about other actions. |

### re-checks
- Task worlds re-run with the new module: refunds 91.86 (task0) and 34.58 (task1), every earn/reverse write as before; no gold call takes the 0.00 path.
- XF E22–E26 on the changed module: no banned substrings, write tools call ctx.create/update in their own bodies, no composed arguments, written events trigger nothing in another category (refund rows external_card only; none at 0.00).

### findings (revision_7)
- No RED. Observations carried: O-1…O-5, O-7, O-8, O-9, O-11…O-14, O-16.

### closing_checklist (revision_7)
- As revision_6, with the tool module now c46346f5…; both task comparisons PASS (0.md / 1.md § revision_7). Gates per the round-7 snapshot (7/7 green), not re-run by the auditor.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN
