# Policy-task audit — loyalty_points_and_elite_status / charter-global

## charter_global_frozen

- Freeze time: 2026-10-05T11:21:53Z (revision 1). Auditor: independent audit agent (erl-task-policy-audit). It is not the agent that wrote these artifacts.
- Frozen inputs (sha256, recomputed by the auditor; they match `/tmp/env0036_views/loyalty_points_and_elite_status/HASHES.txt`):
  - `tasks/loyalty_points_and_elite_status/loyalty.extended.yaml`: `1ee0097fea4b016f5d6aad820d65bce2e0fc3ac65dd94fb71371d703b1bad023`
  - `tasks/loyalty_points_and_elite_status/task_tools.py`: `99421265c2ce44066cc0dcadc1333c221e4c21539ca82d39804335cb240e5e6a`
- Fields read for this section: the extended charter (base section and `extended_policies`), `task_tools.py`, `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/loyalty.yaml`, and the rate-plan parameters and policy text of `blueprint/products/booking.yaml` / `folio.yaml` / `certificate.yaml`. Those last three were read only for cross-category parameters the compute reads (`package_supplement_per_night_usd`, `earns_*`, `relocation_compensation_eligible`) and for sentences that mention points. The DSL semantics (`MONTHS`, `DAYS`, `within_months`, `CFIELD`, `LATEST`, `XLATEST`) were read from `skills/erl-task-instantiate/scripts/check_compute.py`.
- Explicitly masked and unread when this section was written: everything in `tasks/*.json` outside the orchestrator's masked views (`evaluation_criteria`, `computations`, `prerequisite_closure`, `charter_scope`, `required_documents`, `solvability_contract`, `design_rationale`, db_closure). No recursive search touched `tasks/`. This section contains nothing derived from a revealed GT.
- Entry conditions (Step 0): the gate snapshot `/tmp/env0036_views/loyalty_points_and_elite_status/GATES.txt` shows EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK and SCOPE OK, with their commands. The masked views and hashes are in `HASHES.txt`. `check_traceability` is deferred to the render stage, as the brief says. The inputs are complete.
- Base copy: lines 1–1525 of the extended charter are byte-identical to `blueprint/products/loyalty.yaml` (`diff` shows only one trailing blank line). Every top-level key (`category` … `policies`) compares equal after YAML parsing, and the only added key is `extended_policies`.

### policy_conflict_scan

There are eight extended policies, grouped into two problem trees by the `prerequisite` graph:

| Tree | Root (target tool, owner) | Prerequisite problems (target tool, owner) |
| --- | --- | --- |
| T-transfer | `loyalty_ext_largest_points_transfer` (`give_points_to_member_c374aed0`, user) | `loyalty_ext_relocation_compensation` (`post_relocation_compensation_5afb8ff3`, agent); `loyalty_ext_late_award_cancellation_redeposit` (`return_award_cancellation_points_76b4b6d2`, agent); `loyalty_ext_award_stay_night_credits` (`post_award_stay_night_credits_8b07b6a3`, agent) |
| T-purchase | `loyalty_ext_largest_points_purchase` (`buy_points_b3668dab`, user) | `loyalty_ext_stay_elite_bonus` (`post_stay_elite_bonus_1ee6f132`, agent); `loyalty_ext_stay_welcome_points` (`post_stay_welcome_points_0494e852`, agent); `loyalty_ext_corrected_stay_reversal` (`reverse_corrected_stay_points_b6469913`, agent) |

- **Subjects and triggers.** No two extended policies share a `(subject, computes, target_tool)`. Three policies use `loyalty_points_bonus` (relocation, welcome, and the base promotion/card policy), but each is pinned to its own `earning_source` (`relocation_compensation`, `welcome_amenity`) and its own tool. Two policies post to `loyalty_points_earn`: the base `loyalty_stay_earning` and the extended elite bonus, which is limited to the `stay_elite_bonus` component. The two roots are `on_request` and the six prerequisites are `state_due`.
- **Eligibility and time anchors.** Each extended policy restates the base `member_active` gate and the dedup gate of its base. Purchase and transfer move the base's calendar-year caps (`loyalty_msr_purchased_ytd`, `loyalty_msr_transferred_out_ytd`) onto a 12-month window, and both moves are declared in `overwrite`. Every "twelve months before the handling date" uses the same sentence ("transactions posted after the same day number twelve months earlier, up to and including the handling date"). That sentence matches `within_months` (`0 <= MONTHS(posted_date, NOW) < n`). Every tenure ladder is in whole calendar months to the handling date (`MONTHS(enrolled_date, NOW)`).
- **Cross-category read boundaries.** The cross-category reads are booking (night credits, relocation, redeposit, elite bonus, welcome, reversal) and folio (welcome, reversal). Each is declared in `cross_category` with the fields it reads. `CFIELD` / `XLATEST` are scoped to the member's own `customer_id` (`check_compute.build_env._cross` / `_xrows`), which matches the "member's reservation" / "member's folios" wording of the rules.
- **Terminal states.** Each prerequisite tool creates one `loyalty_transactions` row and moves `points_balance`, or for the night credits `elite_night_credits`. The two user tools create the transfer pair and the purchase row. No two policies write the same terminal field with different values.
- **Scope exclusivity and completeness (charter-side).** The two trees are disjoint and together cover all eight extended policies. Whether each task claims exactly one tree is settled in the task files against each world.
- Cross-policy findings from this scan: CG-1, CG-2 and CG-6 (base sentences or parameters that fight an extended quantity), CG-3 (an edge sentence broader than its condition), CG-13 and CG-14 (parallel edges whose order no rule pins). All are under `findings`.

### rule_compute_equivalence

Check 2 was run over all eight extended policies, binding by binding, against `compute_basis` and the `rule`.

- **Night credits** (`loyalty_ext_award_stay_night_credits`): the `award_stay`, `nights_stayed`, tier crediting (`//2`; `n*1+1`; `n*1`), length (≥7 → 2, 4–6 → 1), card (Premier / standard with ≥6 `cobrand_spend` bonus rows in 12 months), tenure (≥240 / 120–239) and `result` sum each have a verbatim basis, and the compute matches. `length_nights` duplicates `nights_stayed` so that the factor bindings stay disjoint. That is not an invented basis.
- **Relocation**: the units (`booked_nights` for Platinum+ with ≥2 nights; 2 for Silver/Gold with ≥3 nights; else 1), uplift (brand_website/mobile_app 20; call_center/property_direct 10), brand, lead (booked→arrival ≥60 / 14–59), tenure, value (nightly_rate×nights ≥1000 / 500–<1000) and `int(P*units*(100+uplift)/100) + supplements` ("rounded down to a whole point") are all quoted and implemented.
- **Late redeposit**: the object (cancelled, else no_show), `deducted` (redemptions less prior redeposits), `late`, points nights / charged points nights, the three night-value methods, the retained share, the notice reduction (from the date of `cancelled_at` to arrival; 0 for a no-show), the activity reduction, the `MX(0, …)` floor, the `//100` rounding and the `MN(deducted, …)` cap are all quoted and implemented.
- **Transfer**: the transferable balance (with the two hold periods), the allowance tier, the allowance-used methods, the remaining allowance floor and the increment rounding are quoted and implemented. One gap (observation CG-8): the rule sentence "the recipient's receipts in the calendar year, counted with loyalty_msr_received_ytd and including this transfer, may not exceed points_transfer_in_annual_cap of the recipient's tier" limits the largest transfer, but the compute does not implement it. It is an empty promise of the compute, with a consequence only when the recipient's year-to-date receipts plus the result exceed 500,000.
- **Elite bonus**: the bonus stay (`LATEST` stay_base), the posted base, the brand rate, the plan-dependent base (Corporate/Group `MN(posted, int(rate*nights*ppu))`; B&B `posted - int(supp*nights*ppu)`), the four add-ons, the 100 % cap and `//100` are quoted and implemented.
- **Welcome**: the stay, the amount (select-service vs full-service), the units, the brand / on-property spend (breakfast + F&B + spa incidentals less adjustments on those codes) / frequency (count of `stay_nights` credits in 12 months) / card (sum of `cobrand_spend` points ≥ 20,000) supplements and the zero-amount guard are quoted and implemented.
- **Reversal**: the corrected folio (`XLATEST` over all `folio_adjustment` rows, any charge code, as "the latest adjustment posted on the member's folios" says), the removed spend (room, breakfast, F&B, spa adjustments), the hotel-error split, the credited rate / ratio (4 dp), base removed / bonus removed, the late reduction (`> 90`, `> 30`), the goodwill waiver (Platinum+ ≥ 50; Gold/Platinum 25–49), the tenure waiver and `MX(0, …)` are quoted and implemented.
- **Purchase**: the stay points (all `loyalty_points_earn` plus welcome less reversals, 12 months), the allowance base, the qualifying spend and its supplement, the cap after the supplement, the remaining allowance, the order price, the activity / tenure discounts and `RND(.,2)` are quoted and implemented.
- Every `factors[].ladder` tier is a sentence of its `rule` and a branch of its `decides` binding, and the reverse also holds. No tier lives only in `compute`.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one extended policy (eight tools, eight policies, `computes` points / nights / purchase_amount_usd). No base policy names a task tool.
- The eight uuid8s are `8b07b6a3`, `5afb8ff3`, `76b4b6d2`, `c374aed0`, `1ee6f132`, `0494e852`, `b6469913`, `b3668dab`. They are pairwise distinct, share no prefix or suffix, and show no sequence or adjacency. Each appears on exactly one tool.
- Docstrings: no docstring names another tool, states a position in a sequence, or uses an ordering connective about another action. "once the … is added/taken off" describes the tool's own returned balance, and "before tax" describes the price. Function bodies judge no eligibility and compute nothing. Each body only finds the membership, creates the row(s) with the values passed in, and adds or subtracts. There is no refusal, error or hint branch tied to any prerequisite state (`task_tools.py` lines 17–388).
- Owners: `give_points_to_member_c374aed0` and `buy_points_b3668dab` are `owner="user"`, matching the rules "made by the sender personally" and "made by the member personally". The other six are `owner="agent"`.

### prerequisite_graph

Check 7:

| # | Blocked policy | `problem` | kind / gate | form | `policy_source` locatable verbatim in the blocked rule | `resolved_by` = depended-on `target_tool` | effect real |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | transfer | relocation | value_input / `balance` | state | yes (rule sentence 3) | yes | yes: the tool adds the points to `points_balance`, which `balance = F('points_balance')` reads |
| E2 | transfer | late redeposit | value_input / `balance` | state | yes (sentence 4) | yes | yes: same mechanism |
| E3 | transfer | night credits | value_input / `net_nights_12m` | state | yes (sentence 5) | yes | yes: the tool creates a `loyalty_night_credit` row dated today, which the `SUM(... within_months=12 ...)` reads |
| E4 | purchase | elite bonus | value_input / `stay_points_12m` | state | yes (sentence 3) | yes | yes: the `loyalty_points_earn` row dated today enters the sum |
| E5 | purchase | welcome | value_input / `stay_points_12m` | state | yes (sentence 4) | yes | yes: the `welcome_amenity` bonus row enters the sum |
| E6 | purchase | reversal | value_input / `stay_points_12m` | state | yes (sentence 5) | yes | yes: the reversal row is subtracted from the stay points and its `eligible_spend_usd` from the qualifying spend |

- Every extended policy has `prerequisite` filled in (`[]` on the six prerequisite policies). Every `problem` is an extended policy id of this file, never a base policy and never itself. There is no `fallback_reason`, as there should not be on state-form edges.
- The graph is two stars, root ← three leaves, with no leaf-to-leaf edge, so it is acyclic.
- Conditions: E1, E2, E3 and E6 state the same handling-time check as their sentences. E4 adds "on a plan with earns_elite_bonus_points true". This is equivalent on the charter's domain, because the only plan with `earns_elite_bonus_points: false` (Reward Night Rate) also has `earns_base_points: false`. E5's condition is narrower than its sentence; see CG-3.
- No prerequisite text uses authoring-viewpoint phrasing.

### prerequisite_sentences

Check 6, the four-point test for each edge:

- **E1** "The largest transfer is worked out only after the points balance carries a relocation compensation transaction for every relocated reservation attached to the membership."
  - Connective: "only after".
  - Waited-on state: record-visible (a bonus row of source relocation_compensation naming each relocated reservation). No tool, id or snake_case token.
  - Scope: "every relocated reservation attached to the membership" matches the condition.
  - The only write that creates such a row is `post_relocation_compensation_5afb8ff3`, reached through the relocation rule ("posted with earning_source relocation_compensation and the relocated reservation's reference").
  - Single reading: yes.
- **E2** "The largest transfer is not worked out until every cancelled or no-show Reward Night Rate reservation attached to the membership carries an award redeposit transaction naming its redemption."
  - Connective: "not … until".
  - Waited-on state: record-visible.
  - The only write that creates it is `return_award_cancellation_points_76b4b6d2` (the redeposit rule's "one award_redeposit transaction naming the redemption they return").
  - Single reading: yes.
- **E3** "The transfer allowance is set only once the account carries a night-credit transaction for every checked-out Reward Night Rate stay attached to the membership."
  - Connective: "only once".
  - The only write is `post_award_stay_night_credits_8b07b6a3` ("one stay_nights transaction naming the stay").
  - Single reading: yes.
- **E4** "The purchase allowance is fixed only after every stay credited at an elite tier whose base points stand on the account carries its elite bonus transaction."
  - The only write is `post_stay_elite_bonus_1ee6f132`.
  - Single reading: yes.
- **E5** "The purchase allowance is not fixed until every elite stay whose base points stand on the account carries its welcome points transaction."
  - The only write is `post_stay_welcome_points_0494e852`.
  - The scope is broader than the condition and broader than anything that write can produce: **CG-3**.
- **E6** "The purchase allowance is fixed only once every credited stay whose folio carries an eligible-spend adjustment posted after its base points carries a stay credit reversal naming its base points transaction."
  - The only write is `reverse_corrected_stay_points_b6469913`.
  - Single reading: yes.
- None of the six sentences recurs in any other rule. No depended-on rule restates the sentence that waits on it, and no rule carries a second wording of any dependency.
- No base sentence grounds an edge.
- Rules were swept for cross-problem orders that ground no declared edge. Two candidates hold on the charter's domain but no rule pins them (CG-13, CG-14). Neither has a consequence in these two worlds (shown in the task files).
- One more charter-level observation (CG-7). The prerequisite sentences quantify over every record ("every relocated reservation", "every checked-out Reward Night Rate stay", "every stay … whose base points stand"). The resolving rules each name one object: "The award stay concerned is the member's checked-out Reward Night Rate reservation…", "The stay concerned is the stay of the latest base points transaction on the account", and "The corrected stay is the stay of the folio that carries the latest adjustment…". Where a world has two unresolved records of one kind, the hop cannot be completed under the resolving rule's own selector. Each task file checks this for its own world.

### override_declarations

Check 1, sentence by sentence against each `base_policy_refs` entry. Each sentence is marked F (followed or inherited unchanged), D (handled differently and declared in `overwrite`) or U (handled differently and undeclared).

- `loyalty_ext_award_stay_night_credits`, refs `loyalty_night_credits` and `loyalty_missing_stay_credit`:
  - loyalty_night_credits sentence 1 ("A completed stay … posts elite_night_credit_per_stay_night … Reward Night Rate stays count."): D.
  - Overlapping rooms: F (inherited).
  - Card anniversary: unrelated.
  - Active only: F.
  - At most once: F.
  - **"When the nights credited for a stay exceed the nights stayed, the excess is reversed against that stay's night-credit transaction."**: **U**. The extended amount is nights stayed plus a top-tier credit, length credits, card credits and tenure credits, so by design it exceeds the nights stayed for every stay that earns any extra. This base sentence remains in force and orders the excess taken back. See **CG-1**.
  - Year-end reset: unrelated.
  - loyalty_missing_stay_credit:
    - Window, own profile and retro-enrolment: F (inherited gates).
    - "The stay earns exactly what loyalty_stay_earning and loyalty_night_credits would have posted at check-out … and is posted with today's date": **U** as to the evaluation moment. The extended rule evaluates card transactions "in the twelve months before the handling date" and tenure "by the handling date". See **CG-6**.
    - Already credited: F.
- `loyalty_ext_relocation_compensation`, refs `loyalty_relocation_compensation`, `loyalty_welcome_amenity` and `loyalty_promotion_and_card_points`:
  - Relocation sentence 1: D.
  - "only for a reservation whose status is relocated": F.
  - Guarantee / `relocation_compensation_eligible`: F.
  - "once per relocated reservation, whatever the number of nights …": D (the author superseded "whatever the number of nights" because the units scale with nights).
  - The welcome and promotion refs govern other sources and are not touched.
- `loyalty_ext_late_award_cancellation_redeposit`, ref `loyalty_award_redemption`:
  - Chart, earliest-night awards, fifth-night saving, deduction at booking, active / suspended and top-off sentences: F.
  - "on a cancellation recorded after_deadline or a no-show under the first_night_points basis, everything except the price of the first night is returned …": D.
  - "When a change adds points nights …": unrelated.
  - "never exceed the points it deducted": F.
  - The extended rule drops the "under the first_night_points basis" qualifier. The Reward Night Rate's `late_cancellation_penalty_basis` and `no_show_penalty_basis` are both `first_night_points` (booking.yaml), so on this charter's domain the dropped qualifier selects nothing new.
- `loyalty_ext_largest_points_transfer`, ref `loyalty_transfer_rules`:
  - The cap sentence: D.
  - Every other sentence (own decision, increment / no fee / irrevocable, both active and balance cover, 30-day age with its counting sentence, one transfer per recipient per day, mirrored arrival): F.
- `loyalty_ext_stay_elite_bonus`, refs `loyalty_stay_earning` and `loyalty_missing_stay_credit`:
  - The bonus-formula sentence (including "when elite_bonus_on_incidentals is true it is applied to all base points"): D. This also covers the plan-dependent base and the add-ons.
  - Plan / channel conditions, eligible spend, base points, "tier is the variant_name … when tier_effective_date is on or before the check-out date", "When the tier took effect after the check-out date … the elite bonus is left to Ashbury Rewards member services", the room cap, active only and once per component: F (inherited).
  - The missing-stay "at check-out" sentence: as for night credits, CG-6.
- `loyalty_ext_stay_welcome_points`, refs `loyalty_welcome_amenity`, `loyalty_relocation_compensation` and `loyalty_promotion_and_card_points`:
  - Welcome sentence 1 ("once per stay … when the folio is settled"): F.
  - The amount sentence: D.
  - Reward-night, OTA, tier-unreadable, once and active sentences: F.
  - **The base parameter `welcome_amenity_once_per_stay: true` of every tier, whose declared meaning is "Whether welcome points are given once per stay regardless of the number of nights (boolean)"**: **U**. The extended welcome units multiply the amount by a nights-dependent count ("one welcome unit for every two nights stayed"; "one welcome unit plus one more for every four nights stayed"). The relocation policy shows that the author superseded the matching "whatever the number of nights" wording there, but nothing names this parameter. See **CG-2**.
- `loyalty_ext_corrected_stay_reversal`, ref `loyalty_stay_credit_reversal`:
  - Sentence 1: F.
  - The points-reversed sentence: D.
  - "only when the stay has an earning transaction", "Corrections that do not touch eligible spend … reverse nothing" and "posted even … below zero; a negative balance blocks redemptions and transfers": F.
- `loyalty_ext_largest_points_purchase`, ref `loyalty_purchase_rules`:
  - The price sentence: D (the increment survives as "rounded down to a multiple of the tier's points purchase increment").
  - The cap sentence: D.
  - Own account, 30-day age with its counting sentence, one purchase per day, non-refundable and active only: F.

Declared overrides (D) leave a unique merged semantics in every case checked. The disguised forms were checked as follows. The 0/1 multiplier and dropped-branch forms are absent. The night-credit excess sentence (CG-1) is an anonymous cap on the same quantity.

### factor_ladders

Structure only. Whether each factor bears weight is decided per world in the task files.

| Policy | Factor | Effect | Tiers (fall-through last) | Multi-source (tiers over ≥2 distinct records) | Cross-difficulty decides tier | Ladder real / label honest |
| --- | --- | --- | --- | --- | --- | --- |
| night credits | award_stay_tier_crediting | method | Member/Silver: n//2; Titanium/Ambassador: n+1; else n | no (tier only) | declared booking, but the tier is selected by the membership tier alone; booking supplies only n (obs. CG-9) | real; method honest (n//2 vs n+1 vs n) |
| | award_stay_length_credits | parameter | ≥7: 2; 4–6: 1; else 0 | no | yes (booking actual dates) | real |
| | award_stay_card_credits | parameter | Premier & ≥6 card txns: 2; card & ≥6: 1; else 0 | **yes** (membership card + transactions) | no | real |
| | award_stay_tenure_credits | parameter | ≥240 mo: 2; 120–239: 1; else 0 | no | no | real |
| relocation | relocation_compensation_units | method | Plat+ & ≥2 nights: nights; Silver/Gold & ≥3: 2; else 1 | **yes** (membership tier + booking nights) | yes | real; "method" is borderline because the tiers select a count of units (obs. CG-11) |
| | relocation_direct_booking_uplift | parameter | web/app 20; call centre / hotel 10; else 0 | no | yes | real |
| | relocation_brand_supplement | parameter | Reserve/Resort 5000; Grand/Hotel 2500; else 0 | no | yes | real |
| | relocation_advance_booking_supplement | parameter | ≥60 d 5000; 14–59 2500; else 0 | no | yes | real |
| | relocation_tenure_supplement | parameter | ≥240 7500; 120–239 5000; else 0 | no | no | real |
| | relocation_booking_value_supplement | parameter | ≥1000 7500; 500–<1000 2500; else 0 | no | yes | real |
| late redeposit | award_night_value | method | certificate nights → 0; ≥5 points nights on a fifth-night tier → deducted // points nights; else deducted // charged nights | **yes** (booking nights + tier) | yes | real; method honest |
| | award_retained_share | parameter | Ambassador 0; Plat/Titanium & ≥50 net nights 50; else 100 | **yes** | no | real |
| | award_notice_reduction | parameter | ≥2 d 20; 1 d 10; else 0 | no | yes | real |
| | award_activity_reduction | parameter | ≥5 15; 2–4 5; else 0 | no | no | real |
| transfer | transfer_allowance_tier | parameter | Titanium/Ambassador & ≥75 net nights 300,000; Platinum & ≥50 200,000; else the tier cap (100,000) | **yes** | no | **unreal: CG-4** |
| | received_points_hold | parameter | Plat+ & ≥120 mo 3; Plat+ & 60–119 6; else 12 | no (tier and enrolment date both on the membership row) | no | real |
| | purchased_points_hold | parameter | Titanium/Ambassador 0; Gold/Platinum 1; else 3 | no | no | real |
| | transfer_allowance_used | method | Titanium/Ambassador: sent − received; Gold/Platinum & ≥120 mo: sent − 25,000; else sent | no | no | real; method honest |
| elite bonus | elite_bonus_base_by_rate_plan | method | Corporate/Group: room-night base points capped at posted base; B&B: posted − package base; else posted | no | yes (booking plan) | real |
| | elite_bonus_card_addon | parameter | 10 / 5 / 0 | **yes** | no | real |
| | elite_bonus_length_addon | parameter | 10 / 5 / 0 | no | yes | real |
| | elite_bonus_engagement_addon | parameter | 10 / 5 / 0 | no | no | real |
| | elite_bonus_tenure_addon | parameter | 10 / 5 / 0 | no | no | real |
| welcome | welcome_units_by_tier_and_nights | method | Plat+ & ≥2 nights: n//2; Silver/Gold & ≥4: 1 + n//4; else 1 | **yes** | yes | real as a ladder, but it collides with base parameter semantics (CG-2) |
| | welcome_brand_supplement | parameter | 500 / 250 / 0 | no | yes | real |
| | welcome_onproperty_spend_supplement | parameter | ≥300: 500; 100–<300: 250; else 0 | no | yes (folio) | real |
| | welcome_frequency_supplement | parameter | ≥10 stays: 500; 5–9: 250; else 0 | no | no | real |
| | welcome_card_supplement | parameter | Premier & ≥20,000 card points 500; card & ≥20,000 250; else 0 | **yes** | no | real |
| reversal | reversal_bonus_bearing_spend | method | all hotel-error → 0; mixed & Gold+ → other spend; else whole | **yes** (folio + tier) | yes (folio) | real |
| | reversal_late_correction_reduction | parameter | >90 d 50; 31–90 25; else 0 | no | yes (booking checkout) | real |
| | reversal_goodwill_waiver | parameter | Plat+ & ≥50 net nights 2000; Gold/Plat & 25–49 1000; else 0 | **yes** | no | **unreal: CG-5** |
| | reversal_tenure_waiver | parameter | ≥120 mo 1000; 36–119 500; else 0 | no | no | real |
| purchase | purchase_allowance_base | method | <24 mo: stay points; ≥24 mo & Member/Silver/Gold: stay points + 10,000; else the cap | no (account age and tier on the same row) | no | real |
| | purchase_spend_supplement | parameter | ≥10,000: 10,000; 5,000–9,999.99: 5,000; else 0 | no | no | real |
| | purchase_order_price | parameter | ≥50,000: 11.50; 20,000–49,999: 12.00; else 12.50 | no | no | real |
| | purchase_activity_discount | parameter | ≥3: 0.75; 1–2: 0.25; else 0 | no | no | real |
| | purchase_tenure_discount | parameter | ≥120 mo: 0.75; 36–119: 0.25; else 0 | no | no | real |

Counts per policy (declared → surviving the structural tests):

| Policy | Declared factors | Surviving factors | Parameter / method (surviving) |
| --- | --- | --- | --- |
| night credits | 4 (3 param, 1 method) | 4 | 3 / 1 |
| relocation | 6 (5 param, 1 method) | 6 | 5 / 1 |
| late redeposit | 4 (3 param, 1 method) | 4 | 3 / 1 |
| transfer | 4 (3 param, 1 method) | **3** after CG-4 strikes transfer_allowance_tier | 2 / 1 |
| elite bonus | 5 (4 param, 1 method) | 5 | 4 / 1 |
| welcome | 5 (4 param, 1 method) | 5 | 4 / 1 |
| reversal | 4 (3 param, 1 method) | **3** after CG-5 strikes reversal_goodwill_waiver | 2 / 1 |
| purchase | 5 (4 param, 1 method) | 5 | 4 / 1 |

- Every declared factor's `decides` is an input binding, never `result`. Binding sets are disjoint within each policy. Every ladder has three pairwise-disjoint tiers. No two tiers of one ladder select the same value or method. Every fall-through equals that factor's `baseline`, and every policy's `baseline.rule` is a set of sentences of its `rule` from which a definite number follows with no factor applied.
- Multi-source factors by tree. T-transfer: card credits, units, night value, retained share, and transfer allowance (struck). T-purchase: card add-on, welcome units, welcome card supplement, bonus-bearing spend, and goodwill waiver (struck). Each tree keeps at least one multi-source factor after striking.
- Cross-difficulty factors by tree. T-transfer: booking (length, units, uplift, brand, lead, value, night value, notice). T-purchase: booking (plan base, length add-on, welcome units, welcome brand, late reduction) and folio (on-property spend, bonus-bearing spend).

### findings

Each finding states its verdict, symptom, root cause, evidence and the tasks it bears on. Where a consequence is specific to one world, it is demonstrated in that task's file, never here.

**CG-1 — SOURCE-POLICY RED (undeclared override). Bears on the task claiming `loyalty_ext_award_stay_night_credits`.**
- Symptom: two sentences in force govern how many night credits stand for one award stay.
- Root cause: `overwrite` of `loyalty_ext_award_stay_night_credits` replaces only the first sentence of `loyalty_night_credits` and leaves "When the nights credited for a stay exceed the nights stayed, the excess is reversed against that stay's night-credit transaction." in force.
- Evidence: the extended rule says "a member at Ashbury Rewards Titanium Elite or Ashbury Rewards Ambassador Elite receives the tier's night credit for each night stayed plus one further credit for the award stay … The night credits posted for an award stay are the credits for the nights stayed plus the length credits, the card credits and the tenure credits of the award stay". In any situation where an extra credit applies, the first passage posts more credits than nights stayed, and the second takes the excess back to the nights stayed.
- Affected: the extended charter, `loyalty_ext_award_stay_night_credits.overwrite`, against base `loyalty_night_credits` rule sentence 6.

**CG-2 — SOURCE-POLICY RED (undeclared override of a base parameter's declared semantics). Bears on the task claiming `loyalty_ext_stay_welcome_points`.**
- Symptom: two clauses settle the welcome amount for a multi-night stay differently.
- Evidence: `parameter_schema.welcome_amenity_once_per_stay` reads "Whether welcome points are given once per stay regardless of the number of nights (boolean)", and the value is `true` on every variant. The extended rule says "The welcome points of the stay are the welcome amount times the welcome units … a member at Ashbury Rewards Platinum Elite, Titanium Elite or Ambassador Elite with two or more nights stayed receives one welcome unit for every two nights stayed …; a member at Ashbury Rewards Silver Elite or Gold Elite with four or more nights stayed receives one welcome unit plus one more for every four nights stayed".
- In the same situation (a Gold member, 4 nights, full-service hotel), the parameter gives the welcome amount once (500 before supplements) and the extended rule gives it twice (1,000 before supplements).
- Root cause: the extended `overwrite` names only the base amount sentence. The author's own relocation overwrite shows the "whatever the number of nights" wording was recognised as conflicting there.
- Affected: `loyalty_ext_stay_welcome_points.overwrite`, against `variants[*].parameters.welcome_amenity_once_per_stay`.

**CG-3 — SOURCE-POLICY RED (prerequisite sentence broader than its condition and than what the depended-on write can produce). Bears on the task whose tree contains E5.**
- Evidence:
  - E5 `policy_source`: "every elite stay whose base points stand on the account carries its welcome points transaction".
  - E5 `condition`: "credited while the tier's welcome amount was above zero and not booked through an online travel agency".
  - The sentence, which is what the agent reads, includes stays credited at Ashbury Rewards Silver Elite, whose `welcome_amenity_points` and `welcome_amenity_points_select_service` are 0 ("a tier whose welcome amount is zero receives nothing"; the tool requires positive points).
  - It also includes stays whose tier "cannot be read from the records" (tier_effective_date after check-out), for which "the welcome points are left to Ashbury Rewards member services".
  - It also includes every stay other than the latest, while the welcome rule's object is only "the stay of the latest base points transaction on the account".
- For such a stay the sentence's state can never be brought about by any write of this difficulty. Read as written, the purchase allowance is never fixed, and the root cannot be solved. Read as the condition, the stay is excluded.
- Affected: `loyalty_ext_largest_points_purchase.prerequisite[1]` (`policy_source` vs `condition`) and the rule sentence it quotes.

**CG-4 — SOURCE-FACTOR RED (unreal ladder). Bears on the task claiming `loyalty_ext_largest_points_transfer`.**
- Evidence: `transfer_allowance_tier` reads "a member at Ashbury Rewards Titanium Elite or Ambassador Elite with at least seventy-five such night credits has a transfer allowance of three hundred thousand points; a member at Ashbury Rewards Platinum Elite with at least fifty such night credits has a transfer allowance of two hundred thousand points; any other member has the points transfer out annual cap of the tier".
- A Titanium or Ambassador Elite member with 50–74 net night credits falls through to the standard 100,000 cap, while a Platinum Elite member with the same 50–74 credits receives 200,000.
- No hotel loyalty programme publishes a smaller transfer allowance for its higher tier at identical engagement. The fall-through's treatment of those customers is not what such a business gives them.
- The factor is struck, and the transfer computation keeps 3 surviving factors, below the floor of 4.
- Affected: `loyalty_ext_largest_points_transfer` rule sentence on the transfer allowance, and `factors[transfer_allowance_tier].ladder`.

**CG-5 — SOURCE-FACTOR RED (unreal ladder). Bears on the task claiming `loyalty_ext_corrected_stay_reversal`.**
- Evidence: `reversal_goodwill_waiver` reads "A member at Ashbury Rewards Platinum Elite or higher whose elite night credits … are at least fifty has the first two thousand points … waived; a member at Ashbury Rewards Gold Elite or Platinum Elite with twenty-five to forty-nine such night credits has the first one thousand points waived; any other member has no goodwill waiver."
- A Gold Elite member with 50 or more net night credits falls through to no waiver, while the same Gold member with 25–49 credits has 1,000 points waived.
- The goodwill relief falls as engagement rises within one tier, which is not a treatment such a business publishes.
- The factor is struck, and the reversal computation keeps 3 surviving factors, below the floor of 4.
- Affected: the `loyalty_ext_corrected_stay_reversal` goodwill sentence and `factors[reversal_goodwill_waiver].ladder`.

**CG-6 — observation (undeclared evaluation moment).**
- Base `loyalty_missing_stay_credit`: "The stay earns exactly what loyalty_stay_earning and loyalty_night_credits would have posted at check-out". The extended night-credit and elite-bonus rules evaluate card transactions, net night credits and tenure "by / in the twelve months before the handling date". Nothing in either `overwrite` names the base sentence.
- The consequence exists only where a tier flips between check-out and the handling date. Each task file recomputes at the check-out date.

**CG-7 — observation (singular resolving selectors under universally quantified prerequisite sentences).** This finding is listed under `prerequisite_sentences`. It becomes a consequence only where a world has two unresolved records of one kind. It is checked in each task file and bites in task 1 through CG-3.

**CG-8 — observation (rule constraint without compute).** The recipient's calendar-year receipts cap limits the largest transfer in the rule but is not implemented in the transfer compute.

**CG-9 — observation (cross-difficulty label).** `award_stay_tier_crediting` is labelled `cross_difficulty: booking`, but its tier is selected by the membership tier alone. The night credits policy still has a genuine cross-difficulty factor (`award_stay_length_credits`).

**CG-10 — observation (another category's charter).** `booking.yaml` `booking_no_show` says "Under first_night_points no cash is charged: the points or Free Night Award of the first night are retained and the rest of the redemption is returned", and `booking_late_cancellation_penalty` says the same but defers "the rest" to "the Ashbury Rewards and Free Night Award rules". The extended redeposit retains only a share of a night value. The booking charter is not one of this audit's four artifacts, so this is recorded for the KB audit only.

**CG-11 — observation.** The `relocation_compensation_units` tiers select a count of units (nights / 2 / 1), which reads close to a `parameter`. It is accepted as `method` because the count switches between per-night and per-reservation counting.

**CG-13 — observation (unpinned order between parallel edges E4 and E6).** The reversal reads the corrected stay's "posted elite bonus" (credited bonus ratio), and E4 posts an elite bonus. Where the corrected stay is the stay the elite-bonus rule selects, the two orders give two reversal amounts, and no rule pins the order. Each task file checks this for its own world.

**CG-14 — observation (unpinned order between parallel edges E2 and E3).** The redeposit's retained share reads "the elite night credits posted in the twelve months before the handling date", which E3's write raises. Where those credits cross 50 for a Platinum or Titanium member, the two orders give two redeposits, and no rule pins the order. Each task file checks this for its own world.

**CG-12 — observation.** Base `loyalty_elite_qualification` upgrades "on the day loyalty_msr_nights_ytd first reaches" a threshold. A night-credit posting that crossed a threshold would change the tier that later tier-dependent values read. Each task file checks this for its own world.

## closing_checklist

Written after both reveals (2026-10-05T11:27:37Z). The charter-global section above was written before any reveal. Its stated freeze time of 11:21:53Z is when the section was started; the file was written at 11:24:24Z, and its pre-reveal sha256 is `6ad9197d…8ccc`. Nothing above this heading was changed after the reveal.

**The difficulty does not close.** Both tasks carry REDs, so the closing conditions of Step 4 are not met. Each item's status:

- **Audit files.** `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, and `_difficulty.md` sits alongside them. This is revision 1, so there is no older revision. Neither comparison section carries a PASS:
  - task 0: SOURCE-POLICY RED (CG-1) + SOURCE-FACTOR RED (CG-4);
  - task 1: SOURCE-POLICY RED (CG-3, CG-2) + SOURCE-FACTOR RED (CG-5).
- **Coverage and scope.** Task 0's `charter_scope` is {transfer, night credits, relocation, redeposit} with its four tools, and task 1's is {purchase, elite bonus, welcome, reversal} with its four tools. The scopes are pairwise disjoint, jointly cover the eight extended policies, and each spans its whole tree. Task tools and GT are closed. Each uuid8 is independent (`#action_binding_and_uuids`).
- **Trees.** Each tree has 3 prerequisite problems, 3 value_input edges (floor 2), a user-owned root and no cycle. Over the difficulty the graph is two disjoint stars, still a DAG. Task 1's E5 sentence fails its scope test (CG-3).
- **Factors.** Every computation declares a self-sufficient baseline and 4–6 factors. Every declared factor bears weight on its task's world, and every full baseline differs from gold. But the transfer computation (CG-4) and the reversal computation (CG-5) each keep only 3 valid factors after one unreal ladder is struck, below the floor of 4.
- **Gates.** The instantiation gates were not re-run on a final form, because the difficulty does not close. The auditor relies on the orchestrator's snapshot `/tmp/env0036_views/loyalty_points_and_elite_status/GATES.txt` (all seven OK) and does not run the gates itself.

**Open findings to carry into the next revision.**

| Finding | Bears on | Verdict |
| --- | --- | --- |
| CG-1 | task 0 | SOURCE-POLICY |
| CG-2 | task 1 | SOURCE-POLICY |
| CG-3 | task 1 | SOURCE-POLICY |
| CG-4 | task 0 | SOURCE-FACTOR |
| CG-5 | task 1 | SOURCE-FACTOR |

The observations (CG-6 to CG-14 and the `design_rationale` count errors) are recorded in the task files and are not grounds for rework.

## revision_2

### charter_global_frozen (revision 2)

- Started 2026-10-05T15:34Z. Auditor: the same independent audit agent. This is a re-audit after rework; the revision-1 text above is left untouched.
- Hashes:
  - `loyalty.extended.yaml`: `f8505449ae01442f9322dbfb5a84b11ef53e215802af810645da060c3b15e1a3`. **It changed** from `1ee0097f…bad023`, so every charter-global section is re-derived in full below.
  - `task_tools.py`: `99421265…5e6a`, unchanged.
  - Blueprint files: unchanged (mtimes 08:30–08:50Z, before revision 1).
  - The masked views `task_0.view.json` `ce8203ee…6eaa5d60` and `task_1.view.json` `da6d1b2b…6af903` are unchanged.
- The gate snapshot `/tmp/env0036_views/loyalty_points_and_elite_status/GATES.txt` (re-run after rework) shows all seven gates OK. It cites them and does not replace this audit.
- Masked while this section was written: the reworked `tasks/0.json` / `tasks/1.json` (mtime 15:31Z) in full. Their revision-1 GT was seen in round 1, so the revision-2 per-task derivations are not blind to the revision-1 GT; each task file discloses this. The reworker's claims were received as item ids only, and no author note was used as evidence. Nothing in this section derives from a revision-2 GT.
- Base copy: lines 1–1525 are again byte-identical to `blueprint/products/loyalty.yaml`. The base parameter `welcome_amenity_once_per_stay` and the base `loyalty_night_credits` excess sentence are unchanged in the base.

### What changed in the extended charter (found by re-reading every extended policy: rule, overwrite, params, compute, compute_basis, factors, baseline, prerequisite, cross_category, inputs)

| Policy | Change |
| --- | --- |
| `loyalty_ext_award_stay_night_credits` | A second `overwrite` entry supersedes the base sentence "When the nights credited for a stay exceed the nights stayed, the excess is reversed against that stay's night-credit transaction." Its `replaced_by` is "The top-tier, length, card and tenure credits of an award stay are credits the award stay is owed and are never an excess over its nights stayed; only night credits posted for an award stay beyond the total this rule gives it are reversed against its night-credit transaction." The same sentence is added to the rule. `award_stay_tier_crediting.cross_difficulty` goes from `booking` to `null`. Compute, params and the other factors are unchanged. |
| `loyalty_ext_stay_welcome_points` | A new first `overwrite` entry supersedes base welcome sentence 1 ("Elite members receive welcome points once per stay, posted with earning_source welcome_amenity when the folio is settled."). Its `replaced_by` is "…one welcome_amenity transaction per stay naming the stay…; that one posting may carry the welcome amount more than once, so the tier parameter welcome_amenity_once_per_stay is read as one welcome posting per stay and no longer as one welcome amount regardless of the number of nights." The rule's first sentence is replaced by it. Compute, factors and params are unchanged. |
| `loyalty_ext_largest_points_transfer` | The transfer-allowance sentence, its compute binding, its `compute_basis` and the ladder's second tier now read "a member at Ashbury Rewards Platinum Elite with at least fifty such night credits, **or at Ashbury Rewards Titanium Elite or Ambassador Elite with fifty to seventy-four such night credits**, has a transfer allowance of two hundred thousand points". The compute adds `or (top_tier and net_nights_12m >= 50 and net_nights_12m < 75)`. Nothing else changed. |
| `loyalty_ext_corrected_stay_reversal` | The goodwill sentence, compute, basis and ladder's second tier now read "a member at Ashbury Rewards Gold Elite with at least twenty-five such night credits, or at Ashbury Rewards Platinum Elite or higher with twenty-five to forty-nine, has the first one thousand points waived". The compute's Gold branch drops the `< 50` bound. Nothing else changed. |
| `loyalty_ext_largest_points_purchase` | E5's rule sentence and `policy_source` now read "The purchase allowance is not fixed until the stay of the latest base points transaction on the account carries its welcome points transaction whenever the tier in effect by that stay's check-out date gives it a welcome amount above zero." The `condition` now reads "The booking_reservations row named by the latest stay_base loyalty_transactions row of the membership, when loyalty_memberships.tier_effective_date is on or before its actual_check_out_date, the tier's welcome amount for its brand is above zero and it was not booked through an online travel agency, has a … welcome_amenity [row] naming it." Nothing else changed. |
| Relocation, late redeposit, elite bonus | No change (rule, compute, factors, params and prerequisite compared binding by binding with revision 1). |

### policy_conflict_scan (revision 2)

- This is the revision-1 scan re-run on the reworked text. The two trees and their membership are unchanged, they are disjoint, and they jointly cover the eight extended policies.
- Each subject, trigger, eligibility gate, time anchor, cross-category read and terminal state is as in revision 1.
- The base sentences that fought an extended quantity in revision 1 are now declared: CG-1 by the night-credit overwrite, CG-2 by the welcome overwrite.
- New observation **R2-O1**. The superseded base excess sentence speaks of every stay ("When the nights credited for a stay exceed …"), but its replacement speaks only of award stays. Read literally, the merged charter no longer states the excess-reversal rule for paid stays. No policy or task of this difficulty posts paid-stay night credits, so there is no consequence here. This is recorded for the cross-difficulty and KB audits.

### rule_compute_equivalence (revision 2)

- **Transfer allowance.**
  - Rule: Titanium/Ambassador with ≥ 75 → 300,000; Platinum with ≥ 50, or Titanium/Ambassador with 50–74 → 200,000; else the cap.
  - Compute: `300000 if top_tier and n>=75 else (200000 if (Platinum and n>=50) or (top_tier and 50<=n<75) else cap)`.
  - `compute_basis` quotes the new sentence verbatim, and the ladder tiers match. Equivalent.
- **Goodwill waiver.**
  - Rule: Platinum+ with ≥ 50 → 2,000; Gold with ≥ 25, or Platinum+ with 25–49 → 1,000; else 0.
  - Compute: `2000 if Plat+ and n>=50 else (1000 if (Gold and n>=25) or (Plat+ and 25<=n<50) else 0)`.
  - Basis and ladder match. Equivalent.
- **The two new descriptive sentences** (the night-credit excess clarification and the welcome "one posting" sentence) state no computed quantity of these policies' `computes`. They promise nothing the compute must implement: the night-credit sentence governs a later reversal event that no policy of this difficulty posts.
- All other bindings are unchanged and equivalent, as found in revision 1 (`#rule_compute_equivalence`). CG-8 stands unchanged: the recipient-cap sentence is still not implemented in the transfer compute.

### action_binding_and_uuids (revision 2)

`task_tools.py` is unchanged (same hash). The eight `(target_tool, computes)` pairs are unchanged and each is claimed once. The revision-1 conclusion holds as written: unique bindings, eight independent uuid8s, docstrings silent about order, and tools that judge nothing.

### prerequisite_graph (revision 2)

| Edge | `problem` | kind / gate | form | Quotable / resolved_by / effect |
| --- | --- | --- | --- | --- |
| E1 | relocation | value_input / `balance` | state | unchanged, pass |
| E2 | late redeposit | value_input / `balance` | state | unchanged, pass |
| E3 | night credits | value_input / `net_nights_12m` | state | unchanged, pass |
| E4 | elite bonus | value_input / `stay_points_12m` | state | unchanged, pass |
| E5 | welcome | value_input / `stay_points_12m` | state | new `policy_source` located verbatim in the purchase rule (its fourth sentence); `resolved_by` `post_stay_welcome_points_0494e852` is the welcome policy's target tool; its effect (a `welcome_amenity` row entering `stay_points_12m`) is real |
| E6 | reversal | value_input / `stay_points_12m` | state | unchanged, pass |

- The graph is still two stars and acyclic. There is no `fallback_reason` on any edge.
- E5's new condition states the same handling-time check as its sentence:
  - "the tier in effect by that stay's check-out date" corresponds to `tier_effective_date` on or before `actual_check_out_date`;
  - "a welcome amount above zero" corresponds to "the tier's welcome amount for its brand is above zero";
  - the added "not booked through an online travel agency" excludes nothing on this charter's domain, because no plan earns base points on OTA bookings (`ota_booking_earns: false` on every plan).
- Neither the conditions nor the effects contain any authoring-viewpoint phrasing.

### prerequisite_sentences (revision 2)

- **E5 (new)**, four-point test:
  - (1) connective "not … until";
  - (2) the waited-on state is record-visible: the latest stay_base row's stay carries a welcome_amenity row, guarded by the record-visible tier test `tier_effective_date` ≤ check-out with a non-zero welcome amount;
  - (3) no tool, policy id, row id or snake_case token;
  - (4) the strength and scope equal the condition, which is singular and conditional.
- The only write that creates a welcome_amenity row is `post_stay_welcome_points_0494e852`. Derivation: E5 plus the ledger (latest stay_base row) plus the welcome rule ("The stay concerned is the stay of the latest base points transaction on the account", "one welcome_amenity transaction per stay naming the stay") leads to that posting, in a single reading.
- The welcome rule does not restate E5, and no other rule restates it.
- **The CG-3 scope defect is closed at charter level.** The sentence now covers only the one stay the welcome rule can act on, and only when its tier is readable and pays welcome. Stays whose tier cannot be read and zero-welcome tiers fall outside it by its own words.
- E1–E4 and E6 are unchanged and pass as in revision 1.
- CG-7 now concerns only E1–E4 and E6 (E5 is singular), and it is an observation as before.
- The cross-problem orders CG-13 and CG-14 are unchanged (no rule pins them), and both remain observations.

### override_declarations (revision 2)

Sentence by sentence against each `base_policy_refs` entry, as in revision 1. The changes:

- `loyalty_night_credits` sentence 6 (excess reversal): now **D**, declared. Merged semantics for an award stay: the extended total (nights credits + top-tier + length + card + tenure) is the stay's owed total, and only credits beyond that total are reversed. That is unique.
  - Task 0's world: 11 credits are the owed total, so nothing is reversed. The revision-1 second reading (net 6) is excluded by the declared replacement's own words: "are never an excess over its nights stayed".
  - **CG-1 is closed.**
- Base welcome sentence 1 together with the base parameter `welcome_amenity_once_per_stay` ("once per stay regardless of the number of nights"): now **D**. The replacement keeps one posting per stay and declares in so many words that the parameter "is read as one welcome posting per stay and no longer as one welcome amount regardless of the number of nights".
  - Merged semantics: one transaction carrying amount × units. That is unique.
  - The revision-1 reading of "amount once" is excluded by the declaration.
  - **CG-2 is closed.**
  - Observation **R2-O2**: the verbatim base `parameter_schema` text still reads "regardless of the number of nights". The render stage must carry the declared reinterpretation next to it so the two are seen together.
- `loyalty_missing_stay_credit` "at check-out" sentence: still undeclared (CG-6). It remains an observation, re-checked per task.
- Every other sentence keeps its revision-1 conclusion (F or D). The disguised forms were re-checked: no 0/1 multiplier and no dropped branch.

### factor_ladders (revision 2)

| Factor | Revision-2 ladder | Pairwise-disjoint tiers? | Values distinct? | Monotone in tier and nights? | Real? |
| --- | --- | --- | --- | --- | --- |
| `transfer_allowance_tier` | Titanium/Ambassador ≥ 75: 300,000; Platinum ≥ 50 or Titanium/Ambassador 50–74: 200,000; else the cap (100,000) | yes | yes | yes. No higher tier now receives less than a lower tier at the same net nights: Titanium 50–74 = Platinum 50–74 = 200,000; Titanium ≥ 75 300,000 > Platinum ≥ 75 200,000; below 50 every tier has the cap | yes. **CG-4 is closed.** |
| `reversal_goodwill_waiver` | Platinum+ ≥ 50: 2,000; Gold ≥ 25 or Platinum+ 25–49: 1,000; else 0 | yes | yes | yes. Gold ≥ 50 now keeps 1,000, so no member's waiver falls as engagement rises | yes. **CG-5 is closed.** |
| `award_stay_tier_crediting` | unchanged ladder | — | — | — | `cross_difficulty` now `null`, which matches what decides its tier (the membership tier). **CG-9 is closed.** The night-credit policy keeps `award_stay_length_credits` (booking) as a genuine cross-difficulty factor |

Every other factor is unchanged and keeps its revision-1 conclusion.

Counts, declared = surviving:

| Policy | Factors | Parameter / method |
| --- | --- | --- |
| night credits | 4 | 3 / 1 |
| relocation | 6 | 5 / 1 |
| late redeposit | 4 | 3 / 1 |
| transfer | **4** | 3 / 1 |
| elite bonus | 5 | 4 / 1 |
| welcome | 5 | 4 / 1 |
| reversal | **4** | 3 / 1 |
| purchase | 5 | 4 / 1 |

- Multi-source factors. T-transfer: card credits, units, night value, retained share and transfer allowance. T-purchase: card add-on, welcome units, welcome card supplement, bonus-bearing spend and goodwill waiver.
- Cross-difficulty factors. T-transfer: booking (length, units, uplift, brand, lead, value, night value, notice). T-purchase: booking and folio, as in revision 1.

### findings (revision 2)

| Finding | Status in revision 2 |
| --- | --- |
| CG-1 | **closed** (declared supersession; unique merged semantics) |
| CG-2 | **closed** (declared reinterpretation; unique merged semantics) |
| CG-3 | **closed** at charter level (the E5 sentence is now exactly as wide as the condition and the resolving rule; the task-1 check is in `1.md` revision_2) |
| CG-4 | **closed** (monotone ladder) |
| CG-5 | **closed** (monotone ladder) |
| CG-9 | **closed** (label corrected) |
| CG-6, CG-7 (E1–E4, E6), CG-8, CG-10, CG-11, CG-12, CG-13, CG-14 | unchanged; observations, re-checked per task |
| R2-O1, R2-O2 | new; observations with no consequence in this difficulty |

No new charter-global RED.

### closing_checklist (revision 2)

Written after the revision-2 reveal (15:35:57Z). The charter-global part of revision 2 above was written before it.

- **Audit files.** `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`. Revision 1 is preserved unedited, and revision 2 is appended under `## revision_2` in all three files. Both revision-2 comparison sections carry **PASS**.
- **Coverage and scope.**
  - The eight extended policies are fully covered by the two `charter_scope`s, which are disjoint and each span a whole tree: task 0 {transfer, night credits, relocation, redeposit}, task 1 {purchase, elite bonus, welcome, reversal}.
  - Task tools and GT are closed.
  - The uuid8s are independent and unchanged.
- **Trees.** Each tree has 3 prerequisite problems, 3 value_input edges (floor 2), a user-owned root and no cycle. The difficulty-wide graph is two disjoint stars, a DAG.
- **Factors.**
  - Every computation has a self-sufficient baseline and 4–6 factors (2 or more `parameter`, 1 `method`).
  - Each task has multi-source and cross-difficulty factors.
  - Every ladder has ≥ 3 distinct, real tiers stated in its rule.
  - Every factor bears weight against an honest baseline on its task's world, and every full baseline differs from gold.
- **Gates.** Per this skill the auditor does not run gates. The orchestrator's post-rework snapshot `/tmp/env0036_views/loyalty_points_and_elite_status/GATES.txt` shows all seven OK on the final form (`loyalty.extended.yaml` `f8505449…e1a3`, `task_tools.py` `99421265…5e6a`); traceability is deferred to the render stage.
- **Remaining observations** (not grounds for rework): CG-6, CG-7 (E1–E4, E6), CG-8, CG-10, CG-11, CG-12, CG-13, CG-14, R2-O1 and R2-O2.

**The difficulty passes the source-layer audit in revision 2.**
