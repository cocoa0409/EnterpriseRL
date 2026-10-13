# Policy-task audit — membership_fees_renewals_and_cardholders / charter-global

## charter_global_frozen

- Scenario: `env/env_0039_warehouse_club_retailer`; difficulty `membership_fees_renewals_and_cardholders` (category `membership`, product file `blueprint/products/membership.yaml`).
- Freeze hashes (sha256, verified against the coordinator brief on 2026-10-05):
  - `tasks/membership_fees_renewals_and_cardholders/membership.extended.yaml` 86dedd94fd154b510634ee6c7cd9effef4a774a830caf3ad248e83c1c1821aed
  - `tasks/membership_fees_renewals_and_cardholders/task_tools.py` 1434bc1e9467ec9cc448d81031c04e95824c72b0d0796be02e2e9a3aa098dd31
  - masked views `audits/views/policy_task/membership_fees_renewals_and_cardholders/0.view.json` 989de1dd…2e8, `1.view.json` f9ffdb8f…32ac
- Freeze time: 2026-10-05T21:37Z (written before any task's GT was revealed). Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit), not the instantiating agent.
- Fields read for this section: blueprint (`blueprint.yaml` difficulty entry, `products/membership.yaml`, `products/card.yaml` and `products/order.yaml` variant names/return windows, `db_schema.json`, `share_tools.py` signatures), the extended charter, `task_tools.py`, and the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`MONTHS`, `DAYS`, `_within`, `LATEST`, `CFIELD`, `XSUM`).
- Explicitly masked / not read: `tasks/*/tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), `worklog.md`, any existing audit. No recursive search touched `tasks/`.
- Entry conditions (Step 0): gate snapshot supplied in the brief — EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; TRACEABILITY NOT OK, declared as expected because the KB `docs/` is not rendered yet (deferred). Masked views and their hashes supplied. Entry conditions met; the TRACEABILITY deferral is recorded, not re-run.

### policy_conflict_scan

Base section of the extended charter is byte-identical to `blueprint/products/membership.yaml` up to the `extended_policies:` key (`diff` shows only the appended key). Six extended policies:

| id | target_tool | owner | computes | prerequisite |
| --- | --- | --- | --- | --- |
| membership_ext_lapsed_renewal_fee | pay_lapsed_membership_renewal_7a245505 | user | renewal_fee | [] |
| membership_ext_upgrade_fee | upgrade_membership_to_plus_9f256f7b | agent | upgrade_fee | lapsed_renewal_fee (value_input, state) |
| membership_ext_plus_guarantee_refund | confirm_plus_guarantee_claim_e9c317f9 | user | guarantee_refund | [] |
| membership_ext_downgrade_difference_refund | refund_downgrade_difference_0adda8cc | agent | refund_amount | plus_guarantee_refund (value_input, state) |
| membership_ext_addon_removal_refund | refund_removed_addon_card_fee_e7b2031f | agent | refund_amount | [] |
| membership_ext_cancellation_refund | confirm_membership_cancellation_5b4de829 | user | refund_amount | addon_removal_refund, downgrade_difference_refund (both value_input, state) |

Overlap scan across subjects, triggers, eligibility, time anchors, parameters, terminal states and cross-category reads:

- Subjects: `membership_fee_refunded` is the subject of four policies (guarantee, downgrade, addon removal, cancellation); they are separated by `refund_reason` (shortfall_guarantee / downgrade_difference / addon_card_removed / cancellation_*) and by the source charge they book against (prior-year Plus-premium charge / current-year renewal charge / an add-on fee charge / current-year renewal-or-new charge). No two policies compute the same refund entry.
- The downgrade policy's tier test reads the tier the guarantee policy writes; the cancellation reads `refund_includes_addon_fees` / `refund_deducts_annual_reward` / `full_refund_window_days` of the tier held at its own handling time, so a guarantee confirmed earlier in the same session changes the cancellation's parameters (Business Plus → Business flips `refund_deducts_annual_reward` true → false). This coupling is through declared edges (guarantee → downgrade → cancellation) and is not a conflict.
- The addon-removal refund reads `P('full_refund_window_days')`, which is 60 on both Business tiers, so a tier move by the guarantee claim does not alter it; add-on cards exist only on Business tiers (`max_addon_cards` 0 elsewhere).
- Terminal states: renewal (expired→active), upgrade (tier change), guarantee (request confirmed + tier move), cancellation (cancelled + all cards deactivated). No two policies drive the same field to different terminal values in one situation.
- Cross-category reads: card (renewal credit: active or restricted; guarantee bonus: active only — two policies, two deliberately different status sets, each stated in its own rule), order (upgrade spend credit 12 months, downgrade volume 12 months, cancellation recent purchases 2 whole months).
- Scope: the claimed scopes are masked until reveal. From the charter alone the six policies split into two connected components — {lapsed_renewal_fee, upgrade_fee} and {plus_guarantee_refund, downgrade_difference_refund, addon_removal_refund, cancellation_refund} — which, with M=2, can be pairwise disjoint and jointly complete only if each task claims exactly one component. Confirmed or refuted in the closing checklist after reveal.

### rule_compute_equivalence

Machine sweep: every `compute_basis` quotation of all six policies is a verbatim substring of its own `rule`; every compute key has a basis and vice versa; every `baseline.rule` is a verbatim substring of its `rule`; every factor `decides` an existing binding. Manual sweep, sentence by sentence and binding by binding:

- **lapsed_renewal_fee.** `rf_paid_years` (new_term + renewal_term − duplicate_charge refunds) = "counted as its new membership and renewal fee charges … less every charge that was refunded as a duplicate charge". `rf_loyalty_reduction`, `rf_card_product`/`rf_card_credit` (active or restricted; closed never), `rf_days_lapsed` = `DAYS(expiry, NOW)` ("expiry date itself not counted"), `rf_late_fee` (>45 → 10, >14 → 5) and `result` (fee − loyalty − credit + late, floor 0, round once) are equivalent. **Defect E1 (`rf_anniversary_kept`):** compute is `MONTHS(F('expiry_date'), NOW) < late_renewal_anchor_months`; the governing rule (base `membership_renewal_dating`, quoted by the extended rule's "dated by the late renewal rule") is inclusive: "keeps its original anniversary only when the renewal fee is paid no later than late_renewal_anchor_months calendar months after the expiry date … boundary: inclusive". On the boundary day itself `MONTHS` equals the anchor and compute says *not kept*, the rule says *kept*. The binding only feeds `rf_verification_margin`, so the scored fee diverges only for a Student/Heroes membership whose verification lapses between expiry+1 and the payment date. Example: Heroes, expiry 2026-08-31, verified through 2026-09-15, paid 2026-10-31 → rule: anniversary kept, year starts 2026-09-01, verification valid → Heroes fee 45.50 basis; compute: not kept → margin `DAYS(2026-10-31, 2026-09-15)+1 = −45` → converted, 65.00 basis.
- **upgrade_fee.** `uf_days_into_year` (≤ 60), `uf_months_left` (`MONTHS(NOW, expiry)` = whole months remaining), `uf_base_fee_paid` (new+renewal charges − their refunds for the current term_start), `uf_fee_basis` (three branches), `uf_net_purchases`/`uf_purchase_lines` (order_line_sold − order_line_returned within 12 months), `uf_spend_credit` (AND of amount and line count), `uf_service_fees` (fees charged at amount 45.50 within 36 months), `uf_tenure_credit` (96/48 months on `opened_date`) and `result` are equivalent. No defect.
- **plus_guarantee_refund.** `gb_year_end` (term_end of the latest certificate issuance), `gb_year_earned`, `gb_upgrades`/`gb_upgrade_date`/`gb_months_held` (`MONTHS(upgrade, year_end)+1`), `gb_premium_basis` (three branches), `gb_prior_claims` (36 months, `transaction_date`), `gb_claim_share`, `gb_card_product` (active only), `gb_addon_in_use` (issued − deactivated business_addon), `gb_member_uplift` (84/36) and `result` (shortfall × share + three add-ons, 0 when shortfall ≤ 0) are equivalent. No defect.
- **downgrade_difference_refund.** All bindings equivalent; `dd_downgrades_older` (72-month count minus 36-month count) realises "the latest was paid 36 to 71 whole months before" only as a fall-through below the 36-month tier, which is how the rule orders them. No defect.
- **addon_removal_refund.** The rule's tier-1 bound is the literal "more than 30 and no more than 60 days" while compute uses `P('full_refund_window_days')` for the upper bound; equal (60) on every tier that can carry add-on cards, so no reachable divergence (observation O5). All other bindings equivalent.
- **cancellation_refund.** All bindings equivalent except observation O6: "A cancellation request the member withdrew in the twelve months before the cancellation" — `membership_requests` records no withdrawal date (fields: membership_request_id, customer_id, membership_id, request_type, status, requested_date, created_at), and compute windows on `requested_date`. Divergence is only possible when a request was raised more than 12 (or 24) months before and withdrawn inside the window; the rule's own quantity is not record-visible, compute substitutes the request date.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above); every task tool is the target of exactly one extended policy.
- Owners: two `owner=user` writes per possible tree (renewal; guarantee confirmation and cancellation confirmation), agent writes for upgrade, downgrade refund and add-on refund.
- Function bodies (task_tools.py): every tool performs its writes unconditionally from the passed arguments — no status check, no amount computation, no refusal or hint when a prerequisite is unresolved (e.g. `upgrade_membership_to_plus_9f256f7b` updates `variant_name` on whatever holding it is given; `refund_downgrade_difference_0adda8cc` books regardless of tier). The tool layer judges no prerequisite.
- Docstrings name no other tool and state no position in a sequence. Ordering words present are local, not cross-problem: "read out to the member before the call" (argument provenance in the three user tools) and "after the primary member removed that cardholder" (the trigger fact, a seeded deactivation, in `refund_removed_addon_card_fee_e7b2031f`). Recorded as observation O7.
- uuid8s: 7a245505, 9f256f7b, e9c317f9, 0adda8cc, e7b2031f, 5b4de829 — six distinct values, no shared prefix or suffix, no sequential/adjacent pattern, none reused. Pass.

### prerequisite_graph

- `prerequisite` is filled in on all six policies (`[]` on three).
- Edges: upgrade → lapsed_renewal; downgrade → plus_guarantee; cancellation → addon_removal; cancellation → downgrade. Every `problem` is another extended policy id of this file, none a base policy, none self. Graph is acyclic (longest path cancellation → downgrade → guarantee).
- Every `policy_source` is a verbatim substring of its own policy's `rule` (machine-checked).
- `form` is `state` on all four edges; no `fallback_reason` present and none required.
- `kind` is `value_input` on all four edges and each `gate` is an existing binding of the blocked policy's compute (`uf_fee_basis`, `dd_premium`, `ca_addon_fees_net`, `ca_base_fees_net`).
- `resolved_by` is the depended-on policy's `target_tool` in all four; each tool's body writes the state the edge waits on (renewal: status active + renewal_term charge for the new year; guarantee: request confirmed + `variant_name` base tier; add-on refund: `addon_card_removed` refund with `source_txn_id`; downgrade refund: `downgrade_difference` refund against the stated renewal charge).
- `condition` vs sentence strength: the downgrade edge's condition adds "with its shortfall_guarantee refund entry booked", which the sentence ("tier stands at the base tier its confirmed guarantee claim moved it to") does not carry; the only write producing either is the same guarantee call, so no reachable divergence (observation O8). The other three conditions match their sentences.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

Four-point test on each edge:

1. upgrade → lapsed_renewal: "The upgrade fee is fixed only after the membership stands active with a renewal or new membership fee for its current membership year recorded on the membership ledger." Connective "only after"; state named in table words (status active; a renewal/new membership fee for the current membership year on the ledger); no tool, id or snake_case; strength matches. Writes of this difficulty that can bring "active + renewal fee for the current year" about: only `pay_lapsed_membership_renewal_7a245505` (the others write refunds, a tier, or `cancelled`). Derivation: records show status `expired` → the state is false → the policy whose rule describes making an expired membership active with a renewal fee is `membership_ext_lapsed_renewal_fee` ("An expired membership is renewed back to active by the primary member paying one renewal fee") → its target tool. Single reading. PASS.
2. downgrade → plus_guarantee: "The downgrade difference refund is not booked until the membership's tier stands at the base tier its confirmed guarantee claim moved it to." Connective "not … until"; state = tier on the holding + a confirmed guarantee claim request; no tool name. Only write that confirms a claim and moves the tier: `confirm_plus_guarantee_claim_e9c317f9`. Single reading. PASS. The same rule opens with a second statement of the same dependency ("When a confirmed Plus guarantee claim moves a membership to its base tier, the Plus premium already paid … is refunded"); it reaches the same conclusion as the prerequisite sentence, so no different outcome can be shown — observation O9.
3. cancellation → addon_removal: "The cancellation refund is fixed only after every add-on card fee of the current membership year whose card the primary member has removed carries a removal refund entry against that fee." Connective "only after"; state = refund entry against each removed card's current-year add-on fee; closed set named by kind. Only write: `refund_removed_addon_card_fee_e7b2031f`. PASS.
4. cancellation → downgrade: "The cancellation refund is not worked out until, where a Plus guarantee claim request is dated within the current membership year, the current year's renewal charge carries its downgrade difference refund entry." Connective "not … until"; conditional scope stated; state = downgrade-difference refund entry on the current renewal charge. Only write: `refund_downgrade_difference_0adda8cc`. PASS. The hop downgrade → guarantee is discoverable from the downgrade rule's own sentence (edge 2).

The depended-on policies' rules do not restate any of these sentences. No extended rule states a cross-problem order outside the four declared edges. Base sentences that state a cross-problem order and overlap a tree: `membership_upgrade` "An upgrade is processed only on a membership whose status is active." — the task tree that uses this hop also rests on the extended sentence 1, so this is an observation (O10), not a red light.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (scored quantity is the criterion):

- **lapsed_renewal_fee** (refs renewal_dating, status_tier_renewal, fee_schedule). Declared: renewal_dating "The renewal fee follows membership_fee_schedule."; fee_schedule "A new_term or renewal_term fee equals the annual_fee_usd of the tier the membership year is held at." **Undeclared:**
  - **D1** `membership_status_tier_renewal`: "When either condition fails, the renewal is taken at the tier's eligibility_lapse_conversion_tier and charged that tier's annual fee, and the membership stays at the converted tier from then on" — states the charged amount (the conversion tier's annual fee); the extended rule charges that fee less loyalty reduction less card credit plus late fee. Not named in `overwrite`.
  - **D2** `membership_renewal_dating`: "When the primary member has confirmed a downgrade_at_renewal request, the next renewal is taken at the tier's downgrade_target_tier and charged that tier's annual fee" — same quantity, same omission.
  - **D3 (dropped branch)** `membership_status_tier_renewal`: "A Student Club membership also keeps its tier only while membership_msr_student_terms is below the tier's discounted_term_limit. When either condition fails, the renewal is taken at the tier's eligibility_lapse_conversion_tier and charged that tier's annual fee" — the extended selector has no tier for the term limit; a Student membership with valid verification and 4 paid Student terms falls to "Any other lapsed membership has the annual fee of the tier it is held at chosen" (32.50) where base converts it (65.00). Not declared.
  - Followed: status gate (active/expired), late-renewal dating, verification-validity test, fee as one renewal_term entry.
- **upgrade_fee** (refs upgrade, tier_benefits, fee_schedule). Declared: the fee_schedule upgrade_difference sentence including "it is never prorated" (the proration tier is therefore declared). membership_upgrade's "The upgrade_difference fee is charged on the upgrade date, the expiry_date does not change" is followed. tier_benefits followed. No undeclared conflict.
- **plus_guarantee_refund** (refs plus_guarantee, cancellation_refund, cardholders, tier_benefits). Declared: the refund-amount/booking sentence ("The refund equals plus_premium_usd minus membership_msr_completed_year_reward, …"). **Undeclared — D5:** base "For a completed membership year whose membership_msr_completed_year_reward is below plus_premium_usd, the primary member may claim the difference" is a separate sentence that fixes both the entitlement condition (reward below the full premium) and the amount ("the difference" = premium − reward). The extended rule claims a different amount (prorated basis − reward, × repeat-claim share, + three add-ons) and a different entitlement ("a year without a guarantee shortfall pays nothing", where the shortfall is measured against the prorated basis — e.g. a year upgraded with fewer than three months at Plus has basis zero and pays nothing although its reward is below plus_premium_usd). The sentence is not named in `overwrite`. Window, status, one-per-year and "keeps any certificate" followed.
- **downgrade_difference_refund** (refs plus_guarantee, cancellation_refund, cardholders). Declared: "A confirmed claim moves the membership … the plus_premium_usd of the current year is also refunded …". No undeclared conflict.
- **addon_removal_refund** (refs cardholders, cancellation_refund, plus_guarantee). Declared: the add-on removal refund sentence (covers both the full-in-window and nothing-after statements the share ladder departs from). No undeclared conflict.
- **cancellation_refund** (refs cancellation_refund, plus_guarantee, cardholders). Declared: the full-window sentence, the per-charge booking sentence, the reward-deduction sentence. **Undeclared:**
  - **D4** `membership_cancellation_refund`: "After that window the tier refunds membership_msr_unused_whole_months twelfths of the current-year fees where prorated_refund_after_window is true, and nothing where it is false." The extended tier "When the cancellation comes after the full refund window and the member has no recent Northgate purchases, the cancellation refund share is the whole of the refundable current-year fees" refunds the whole where base refunds twelfths (or nothing on a non-prorating tier). Not named.
  - The base measure `membership_msr_unused_whole_months` ("whole calendar months … that begin after the requested_date") and the extended "whole months from the cancellation date to the expiry date" coincide on anniversary-aligned years; no divergence shown — not recorded.

### factor_ladders

| policy | factor | label | ladder tiers | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| lapsed_renewal_fee | renewal_tier_fee | method | 3 | tier 2 only (holding + requests) | — |
| | renewal_loyalty_reduction | method | 3 | no (ledger) | — |
| | renewal_cardmember_credit | parameter | 4 | no (card holding) | null (reads card) |
| | renewal_late_reinstatement_fee | parameter | 3 | no (holding date) | — |
| upgrade_fee | upgrade_fee_basis | method | 3 | yes as written (holding dates AND ledger base fee) | — |
| | upgrade_spend_credit | parameter | 3 | amount AND line count, both over order_lines | order |
| | upgrade_service_member_credit | parameter | 3 | no | — |
| | upgrade_member_since_credit | parameter | 3 | no | — |
| plus_guarantee_refund | guarantee_premium_basis | method | 3 | yes (ledger upgrade charge AND date span) | — |
| | repeat_claim_share | method | 3 | no | — |
| | cardmember_guarantee_bonus | parameter | 4 | no | null (reads card) |
| | business_cardholder_guarantee_uplift | parameter | 3 | no | — |
| | long_standing_member_guarantee_uplift | parameter | 3 | no | — |
| downgrade_difference_refund | downgrade_premium_basis | method | 3 | yes (holding dates AND reward ledger) | — |
| | repeat_downgrade_retention_charge | parameter | 3 | no | — |
| | plus_history_downgrade_credit | parameter | 3 | no | — |
| | business_volume_downgrade_credit | parameter | 3 | no | order |
| addon_removal_refund | removed_card_refund_share | method | 3 | yes (fee-charge date AND card issue date AND holding term_start) | — |
| | northgate_card_refund_bonus | parameter | 3 | no | — |
| | repeat_removal_processing_charge | parameter | 3 | no | — |
| | card_replacement_cost_recovery | parameter | 3 | no | — |
| cancellation_refund | cancellation_refund_share | method | 3 | yes (holding dates AND order lines) | order |
| | recent_certificate_recovery | parameter | 3 | no | — |
| | automatic_renewal_courtesy_credit | parameter | 3 | yes (holding auto_renew AND ledger tender/date) | — |
| | repeat_cancellation_administration_charge | parameter | 3 | no | — |
| | billing_error_courtesy_credit | parameter | 3 | no | — |

Structure checks:

- Counts per policy (as declared): 4/4/5/4/4/5 factors; parameter ≥ 2 and method ≥ 1 everywhere. Bindings of each factor are disjoint from every other factor's; every `decides` is an input, never `result`.
- Every tier of every ladder (condition and value/method) is stated in its `rule` and every branch of each `decides` binding is a tier the rule states. Every fall-through equals its factor's `baseline`, and every `baseline` equals what the policy's `baseline.rule` gives for that input.
- **F1 — renewal_tier_fee: two tiers select the same value, and the label is not honest.** Tier 1 selects "the annual fee of the Northgate Club Membership the renewal converts to" = 65.00 (`K('conversion_tier_fee_usd')`); tier 2 selects "the Plus annual fee less the Plus premium" = `P('annual_fee_usd') − P('plus_premium_usd')`, which is 130.00 − 65.00 = 65.00 on both Plus tiers (Club Plus and Business Plus are the only tiers with `plus_premium_usd` > 0). Every customer on tier 1 or tier 2 is charged a 65.00 fee basis; one tier has been written as two, leaving two distinct outcomes (65.00 vs the held tier's own fee). All three tiers only substitute a fee figure into the same formula (fee − loyalty − credit + late fee) — a `parameter` labelled `method`.
- **F2 — repeat_claim_share: mislabelled.** Its tiers select 0.5 / 0.75 / 1 as a multiplier in the unchanged formula `shortfall × share + …` — a rate, i.e. a `parameter`, labelled `method`.
- **F3 — upgrade_fee_basis: a conjunct that holds of every customer who reaches the write.** Tiers 1 and 2 each require "a base fee stands paid for that year". The policy's own prerequisite sentence ("fixed only after the membership stands active with a renewal or new membership fee for its current membership year recorded on the membership ledger") guarantees a recorded, positive (`renewal_fee` is "always positive" in the tool contract) base fee for the current year for every customer the write reaches; no fee type a write of this charter books against a current year can net it to zero short of cancellation, which ends the membership. The conjunct restates the policy's scope instead of dividing its customers, and it is the conjunct that makes this factor's tiers multi-source (the remaining conjunct reads only the holding's dates).
- Honest-label check of the other `method` factors: renewal_loyalty_reduction (percentage of the chosen fee vs a flat amount vs none — changes the computation), upgrade_fee_basis, guarantee_premium_basis, downgrade_premium_basis, removed_card_refund_share, cancellation_refund_share (each changes how the quantity is computed: proration by months, subtraction of paid fee/reward, halving, whole) — honest.
- Business-reality observations (no consequence demonstrable from the charter alone; re-examined per task where a world could show it): O2 northgate_card_refund_bonus and the downgrade/cancellation add-on credits can make a refund exceed the fee charge it is booked against; O3 cancellation_refund_share tier 1 prorates a cancellation that falls inside the published full-refund window because the member shopped recently; O4 repeat_claim_share pays a published guarantee only in part to repeat claimants.
- After striking F1 (ladder collapses to two distinct outcomes, fewer than three tiers), lapsed_renewal_fee has 3 surviving factors (< 4). After relabelling F2, plus_guarantee_refund still has 1 method + 3 parameter + the relabelled one (≥ 4, bounds hold). Whether these bear on a task depends on which policies the task claims — demonstrated in the task files.

### findings

| id | class | finding | bears on |
| --- | --- | --- | --- |
| D1 | SOURCE-POLICY RED | Undeclared override: base status_tier_renewal "charged that tier's annual fee" vs extended lapsed-renewal fee formula | any task claiming membership_ext_lapsed_renewal_fee on a Student/Heroes world with lapsed verification (demonstrated in the task file) |
| D2 | SOURCE-POLICY RED (charter) | Undeclared override: base renewal_dating downgrade_at_renewal "charged that tier's annual fee" | tasks whose world holds a confirmed downgrade_at_renewal request (none known pre-reveal) |
| D3 | SOURCE-POLICY RED (charter) | Dropped branch: Student discounted_term_limit conversion absent from the extended selector, undeclared | Student-tier worlds only |
| D4 | SOURCE-POLICY RED (charter) | Undeclared override: base after-window twelfths sentence vs extended "after window + no recent purchases → whole" | cancellation worlds after the full-refund window |
| D5 | SOURCE-POLICY RED | Undeclared override: base plus_guarantee "may claim the difference" (amount and entitlement) vs extended guarantee refund | any task claiming membership_ext_plus_guarantee_refund on a world with a guarantee claim (demonstrated in the task file) |
| E1 | SOURCE-POLICY RED (charter) | rf_anniversary_kept strict `<` vs the base rule's inclusive late-renewal boundary | lapsed Student/Heroes renewals paid exactly on the boundary day |
| F1 | SOURCE-FACTOR RED | renewal_tier_fee tiers 1 and 2 select the same value (65.00); method label dishonest; ladder has two distinct outcomes; lapsed_renewal_fee left with 3 surviving factors | any task claiming lapsed_renewal_fee |
| F2 | SOURCE-FACTOR RED | repeat_claim_share labelled method, tiers are multipliers (parameter) | any task claiming plus_guarantee_refund |
| F3 | SOURCE-FACTOR RED | upgrade_fee_basis conjunct "a base fee stands paid for that year" holds of every customer the write reaches | any task claiming upgrade_fee |
| O2–O10 | observations | see sections above | — |

## closing_checklist

Written after both reveals (2026-10-05T21:37Z); nothing above this heading was changed after any reveal.

- Per-task files: `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`; this is revision 1 (no earlier revisions). Both comparison sections are written; **neither carries an overall PASS**:
  - task 0 — SOURCE-POLICY RED (D1), SOURCE-FACTOR RED (F1, F3); problem tree PASS; no independent SOURCE-TASK defect.
  - task 1 — SOURCE-POLICY RED (D5), SOURCE-FACTOR RED (F2); problem tree PASS; no independent SOURCE-TASK defect.
- Coverage and scope: `charter_scope` of task 0 = {lapsed_renewal_fee, upgrade_fee} with their two tools; task 1 = {plus_guarantee_refund, downgrade_difference_refund, addon_removal_refund, cancellation_refund} with their four tools. Pairwise disjoint, jointly complete over the six extended policies and six task tools, each scope spanning its whole tree — as predicted from the graph's two components in `policy_conflict_scan`. Task tools and GT are closed (every gold write is one of the six tools; every tool appears in exactly one task's GT). uuid8s independent (see `action_binding_and_uuids`).
- Problem trees: task 0 — 1 prerequisite problem, 1 value_input edge, user-owned renewal, acyclic. Task 1 — 3 prerequisite problems, 3 value_input edges (≥ 2), user-owned guarantee confirmation and cancellation, acyclic. The difficulty-wide `prerequisite` graph has two disjoint components and no cycle.
- Factors: every computation declares a self-sufficient baseline whose fall-back differs from gold (45.50/53.50, 65.00/51.25, 35.72/23.60, 65.00/41.54, 65.00/47.34, 236.12/172.49) and every declared factor bears weight on its world. Not satisfied: F1 (renewal_tier_fee — two tiers share 65.00, label dishonest, renewal left with 3 surviving factors), F2 (repeat_claim_share label), F3 (upgrade_fee_basis universal conjunct; task 0 left without a multi-source factor on surviving conditions).
- Policy self-consistency: undeclared overrides D1 (bears on task 0) and D5 (bears on task 1); D2, D3, D4 and rule/compute defect E1 are charter defects whose consequence no current task world reaches.
- Gates: not re-run by the auditor (Step 0 — the auditor cites, does not run). The audited artifacts are byte-identical to the gate snapshot's inputs: extended charter 86dedd94…1aed and task_tools.py 1434bc1e…dd31 re-hashed at close; task files hashed at close 0.json 122f7dea…c723, 1.json d1ed54d6…e7. The coordinator snapshot (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; TRACEABILITY deferred pending KB render) therefore applies to the final form.
- **Difficulty status: does not pass the source-layer audit** (policy self-consistency and factors-bear-weight fail on both tasks; problem tree and unique solution under the extended reading hold).

## revision_2

### charter_global_frozen (revision 2)

- Round-2 inputs (sha256, verified against the coordinator's round-2 brief): `membership.extended.yaml` 0209ea4a02313adf96719a1f29ee3fd855b11ada7206ee59d10ff8ba0b6c0bbe (round 1: 86dedd94…1aed — **changed**), `task_tools.py` 3015b1222258b180598c37e01c3d9b2de51801c5548e365f7dad7fe74f1503f3 (round 1: 1434bc1e…dd31 — **changed**). Both shared inputs moved, so every charter-global section is re-derived in full below; the round-1 text above is left untouched.
- Base section still byte-identical to `blueprint/products/membership.yaml` (diff shows only the appended `extended_policies:` key).
- Freeze time 2026-10-05T22:19Z, before either round-2 task JSON was opened. Auditor: the same independent auditor as round 1.
- contamination_disclosure (difficulty level): the auditor read the round-1 task JSONs (GT, computations, design_rationale) after the round-1 freeze. That knowledge is prior-revision context, not round-2 GT; round-2 sections below are derived from the round-2 charter, tool module and views only. Nothing derived from round-2 GT is written in this section.
- Gate snapshot supplied with the round-2 brief: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY deferred (KB not rendered). Cited, not re-run.

### policy_conflict_scan (revision 2)

Same six policies, target tools, owners and `computes` as round 1; same four prerequisite edges; same two connected components ({lapsed_renewal, upgrade}; {guarantee, downgrade, addon_removal, cancellation}). Subject overlaps resolve exactly as in round 1 (refund_reason + source charge). The cancellation still reads the tier held at its own handling time (Business Plus → Business flips `refund_deducts_annual_reward`), through declared edges. No new overlap: the new lapsed-renewal grace credit reads only the holding's verification date and dates. No conflict found.

### rule_compute_equivalence (revision 2)

Machine sweep: every `compute_basis` quote is verbatim in its own rule; compute keys and basis keys correspond one-to-one; every `baseline.rule` is verbatim in its rule; factor bindings are pairwise disjoint in every policy.

- **lapsed_renewal_fee.** E1 re-examined: `rf_anniversary_kept` is now `MONTHS(NOW, expiry) >= -late_renewal_anchor_months`. Checked against the base inclusive rule (with the month-end clamp) on: expiry 2026-08-31 paid 10-31 kept / 11-01 not kept; expiry 2026-06-30 paid 08-30 kept / 08-31 not kept; expiry 2026-12-31 paid 2027-02-28 kept / 03-01 not kept; expiry 2026-08-30 paid 10-30 kept / 10-31 not kept — all agree with the rule. **E1 closed.** `rf_verification_gap` (kept: `DAYS(verified_through, expiry)+1`, i.e. to the day after expiry; not kept: `DAYS(verified_through, NOW)`) equals "ended … before that first day" in both datings. `rf_tier_fee` equals the rule's held-tier sentence (Club Membership 65.00 on conversion; Plus fee less premium = 65.00 = base tier fee on a confirmed downgrade; own fee otherwise). **New defect E2:** `rf_student_terms` = all `new_term` + `renewal_term` charges, with no deduction for charges refunded as duplicates; the rule says "a Student Club membership that has already paid as many Student Club membership years as its discounted term limit", and the same rule defines paid membership years as charges "less every charge that was refunded as a duplicate charge". Situation: Student membership, verification valid, three term charges plus one duplicate renewal charge refunded as `duplicate_charge`, renewing after lapse → rule: 3 paid Student years < 4 → stays Student, fee basis 32.50; compute: 4 ≥ 4 → converted, 65.00. Two conclusions. No task world is a Student membership.
- **upgrade_fee.** New binding `uf_prior_upgrades` (count of `upgrade_difference` charges) = "A first upgrade is one made on a membership whose ledger carries no upgrade difference fee from any earlier upgrade". Tier 1 / tier 2 / fall-through equivalent. No defect.
- **plus_guarantee_refund, downgrade_difference_refund.** Unchanged computes; rules equivalent (the guarantee rule now also carries the D5 replacement sentence; the downgrade rule's opening sentence was reworded — no binding rests on it). No defect.
- **addon_removal_refund.** Rule tier bounds now read "more than 30 days and no more than the tier's full refund window of days" and "more than the tier's full refund window of days and no more than 120 days", matching `P('full_refund_window_days')` in compute. **O5 closed.**
- **cancellation_refund.** Rule now reads "A cancellation request the member raised in the twelve months before the cancellation, by its request date, and later withdrew …" and "one raised 12 to 23 whole months before and later withdrawn", matching the `requested_date` windows in compute. **O6 closed.**

### action_binding_and_uuids (revision 2)

- Pairs `(target_tool, computes)` unchanged and unique; uuid8s unchanged (7a245505, 9f256f7b, e9c317f9, 0adda8cc, e7b2031f, 5b4de829), distinct, not batch-derived.
- Function bodies re-read: still unconditional writes from arguments — no status/tier/prior-refund check, no computation, no refusal or hint.
- Docstrings: "read out to the member before the call" is now "read out to the member"; the add-on refund docstring now reads "the add-on card fee of a business add-on cardholder whom the primary member has removed". No ordering word, no other tool named. **O7 closed.**

### prerequisite_graph (revision 2)

Same four edges, all `state` form, all `value_input`, gates `uf_fee_basis`, `dd_premium`, `ca_addon_fees_net`, `ca_base_fees_net` present in compute; every `policy_source` verbatim in its own rule (machine-checked); `resolved_by` = the depended-on policy's target tool; acyclic. The downgrade edge's condition now reads "membership_holdings.variant_name equals the downgrade_target_tier of the Plus tier the membership held, and the membership's shortfall_guarantee_claim request that moved it there has status confirmed" — the strength of its sentence, no extra refund-entry clause. **O8 closed.**

### prerequisite_sentences (revision 2)

The four prerequisite sentences are textually unchanged; the round-1 four-point test, single-resolving-write analysis and derivations stand on the round-2 text (re-read, not carried by reference). The downgrade rule's opening sentence is now "A membership that leaves its Plus tier for its base tier during a membership year it has already paid at the Plus fee gets the Plus premium of that year back as a downgrade difference refund, booked against the current year's renewal charge and returned to that charge's tender." — a trigger statement with no ordering connective and no mention of the guarantee claim; the dependency is stated once, by the prerequisite sentence. **O9 closed.** O10 (base `membership_upgrade` status sentence) unchanged — observation.

### override_declarations (revision 2)

- **lapsed_renewal_fee.** `overwrite` now names four base sentences: renewal_dating "The renewal fee follows membership_fee_schedule."; renewal_dating "When the primary member has confirmed a downgrade_at_renewal request, the next renewal is taken at the tier's downgrade_target_tier and charged that tier's annual fee"; status_tier_renewal "When either condition fails, the renewal is taken at the tier's eligibility_lapse_conversion_tier and charged that tier's annual fee"; fee_schedule "A new_term or renewal_term fee equals the annual_fee_usd …". All four are verbatim in base; all four map to the lapsed-renewal total sentence, which is verbatim in the rule; the rule restates the tier each renewal is held at, so the superseded tier-taking content is carried, not lost. **D1 closed, D2 closed.** Student term limit: the rule now converts "a Student Club membership that has already paid as many Student Club membership years as its discounted term limit" — the dropped branch is restored. **D3 closed** (its compute counting defect is the new E2 above). Observation O13 (pre-existing, missed in round 1): the superseded fee_schedule and renewal_dating sentences also govern on-time renewals and new-term fees, while the replacement is worded "The renewal fee of a lapsed membership is …"; the merged charter is unique only on the reading that the replacement is scoped to lapsed renewals (the policy's subject), leaving base in force for other renewals. No task writes an on-time renewal or enrollment.
- **upgrade_fee.** Unchanged declaration; no undeclared conflict.
- **plus_guarantee_refund.** `overwrite` now also names "For a completed membership year whose membership_msr_completed_year_reward is below plus_premium_usd, the primary member may claim the difference", replaced by "The primary member may claim the guarantee for a completed membership year only where that year shows a guarantee shortfall, and the amount the claim pays is the guarantee refund worked out below rather than the plain difference between the Plus premium and the year's Annual Reward." — verbatim in the rule; merged semantics unique. **D5 closed.**
- **downgrade_difference_refund, addon_removal_refund.** Unchanged; no undeclared conflict.
- **cancellation_refund.** `overwrite` now also names "After that window the tier refunds membership_msr_unused_whole_months twelfths of the current-year fees where prorated_refund_after_window is true, and nothing where it is false.", replaced by the "after the full refund window and no recent purchases → whole" sentence. **D4 closed.**

### factor_ladders (revision 2)

| policy | factors (label) | method / parameter | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- |
| lapsed_renewal_fee | renewal_loyalty_reduction (M), renewal_cardmember_credit (P), renewal_conversion_grace_credit (P), renewal_late_reinstatement_fee (P) | 1 / 3 | grace credit: holding variant/verification + dates (one record) — none multi-source | — (card read, null) |
| upgrade_fee | upgrade_fee_basis (M), upgrade_spend_credit (P), upgrade_service_member_credit (P), upgrade_member_since_credit (P) | 1 / 3 | upgrade_fee_basis: holding dates AND ledger upgrade history | order |
| plus_guarantee_refund | guarantee_premium_basis (M), repeat_claim_share (P), cardmember_guarantee_bonus (P), business_cardholder_guarantee_uplift (P), long_standing_member_guarantee_uplift (P) | 1 / 4 | guarantee_premium_basis | — (card read, null) |
| downgrade_difference_refund | unchanged (1 M, 3 P) | 1 / 3 | downgrade_premium_basis | order |
| addon_removal_refund | unchanged (1 M, 3 P) | 1 / 3 | removed_card_refund_share | — |
| cancellation_refund | unchanged (1 M, 4 P) | 1 / 4 | cancellation_refund_share, automatic_renewal_courtesy_credit | order |

- **F1 closed.** `renewal_tier_fee` is no longer a factor; which tier's fee is charged now lives in the baseline (`baseline.rule` states the held-tier sentence, with `conversion_tier_fee_usd`, `plus_premium_usd`, `discounted_term_limit` among its params), which is the base charter's own conversion rule — an honest standard method. The new `renewal_conversion_grace_credit` (10.00 / 5.00 / 0 by days between the verification's end and the new year's first day) has three distinct values, every tier stated in the rule and implemented in compute, fall-through 0 = baseline, condition not universal (renewals that do not convert, or whose verification ended long before, fall through), and a courtesy a club plausibly extends when a member is moved off a status discount. Lapsed renewal: 4 factors, 3 P + 1 M.
- **F2 closed.** `repeat_claim_share` is labelled `parameter`; guarantee: 4 P + 1 M.
- **F3 closed.** upgrade_fee_basis tiers now conjoin a date condition with "no upgrade difference fee from an earlier upgrade stands on the ledger" — a condition that divides customers (a member who upgraded in an earlier year, as the task-1 member did, fails it) and that a club plausibly weighs (renewal-style pricing once per membership). The universal "a base fee stands paid" conjunct is gone. The factor is multi-source (holding dates + ledger).
- All other ladders unchanged from round 1; every fall-through equals its baseline; every baseline equals its `baseline.rule` input. O2–O4 remain observations.

### findings (revision 2)

| id | round-1 class | round-2 status |
| --- | --- | --- |
| D1, D2 | SOURCE-POLICY RED | closed (declared; merged semantics unique) |
| D3 | SOURCE-POLICY RED (charter) | closed (branch restored) — but see E2 |
| D4, D5 | SOURCE-POLICY RED | closed (declared) |
| E1 | SOURCE-POLICY RED (charter) | closed (boundary verified on eight dates) |
| F1, F2, F3 | SOURCE-FACTOR RED | closed |
| O5, O6, O7, O8, O9 | observations | closed |
| O2–O4, O10–O12 | observations | unchanged |
| **E2 (new)** | — | **SOURCE-POLICY RED (charter)**: `rf_student_terms` counts duplicate-refunded charges, the rule's "paid … Student Club membership years" does not; no task world is Student, so no task-level consequence |
| **O13 (new, pre-existing)** | — | observation: lapsed-only replacement of base sentences that also govern on-time/new-term fees; unique only on the subject-scoped reading |

### closing_checklist (revision 2)

Written after the round-2 reveals (2026-10-05T22:20:39Z); nothing in `revision_2` above this heading was changed after the reveal.

- Files: `0.md`, `1.md` each carry an untouched round-1 section and an appended `revision_2` with frozen derivation, comparison (PASS) and findings; old revisions traceable.
- Round-1 REDs: D1, D2, D3, D4, D5, E1, F1, F2, F3 closed; O5–O9 closed; O2–O4, O10–O12 remain observations — all as the reworker claimed, each verified above, none accepted on the claim alone.
- New in round 2: **E2 — SOURCE-POLICY RED (charter only)**: the Student term-limit count (`rf_student_terms`) includes charges refunded as duplicates, which the rule's "paid … Student Club membership years" excludes. It was introduced by the D3 fix and reaches no task world (task 0 is Heroes; task 1 has no lapsed renewal). Observations O13 (lapsed-only replacement of base sentences that also govern on-time/new-term fees) and O14 (stale task-1 design_rationale text).
- Coverage and scope: task 0 = {lapsed_renewal_fee, upgrade_fee}; task 1 = {plus_guarantee_refund, downgrade_difference_refund, addon_removal_refund, cancellation_refund}; disjoint, jointly complete; task tools and GT closed; uuid8s independent.
- Trees: task 0 — 1 prerequisite, 1 value_input, user-owned renewal; task 1 — 3 prerequisites, 3 value_input, user-owned guarantee and cancellation; difficulty graph acyclic (two components).
- Factors: every computation has a self-sufficient, honest baseline whose fall-back differs from gold (65.00/43.50, 65.00/61.25, 35.72/23.60, 65.00/41.54, 65.00/47.34, 236.12/172.49); 4–5 factors each, ≥ 1 method and ≥ 2 parameter; every factor bears weight; each task has a multi-source and an order (cross-difficulty) factor.
- Gates: not re-run by the auditor; round-2 coordinator snapshot (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; TRACEABILITY deferred to KB render) applies to the audited hashes (extended 0209ea4a…bbe, tools 3015b122…3f3, task files 38536a7e…7eb7 and be9d656b…94).
- **Status:** both tasks PASS on all four relationships. The difficulty does **not** fully close: charter-level policy self-consistency still carries one SOURCE-POLICY RED (E2; its two conclusions are demonstrated on a constructed Student situation, as E1 was in round 1). No task world reaches it, so neither task's verdict changes, but the charter the KB render will publish still contains it.

## revision_3

### charter_global_frozen (revision 3)

- Round-3 inputs: `membership.extended.yaml` 5d50219035c3715266068b55e388776a628fa3950ba503642b8bbf5a44df49cb (round 2: 0209ea4a…bbe — **changed**); `task_tools.py` 3015b122…3f3 (**unchanged**); views 0 (989de1dd…2e8) and 1 (2b2e8df6…bbfa) unchanged since round 2. Base section still byte-identical to `blueprint/products/membership.yaml`.
- Because the charter hash moved, every charter-global section below is re-derived on the round-3 file. `action_binding_and_uuids` rests on the tool module (unchanged hash 3015b122…3f3) plus the charter's `target_tool`/`computes` pairs; it is carried from revision 2 after re-confirming the pairs.
- Freeze time 2026-10-05T22:42Z, before either round-3 task JSON was opened. Auditor: same as rounds 1–2.
- contamination_disclosure: round-1 and round-2 task JSONs were read after their freezes (prior-revision GT known). Round-3 sections use only the round-3 charter, the unchanged tool module and the unchanged views.
- Coordinator gate snapshot for round 3: all OK, TRACEABILITY deferred. Cited, not re-run.

### what moved

Per-policy line spans: lapsed_renewal_fee 213 lines (round 2: 203); the other five policies have the same line counts as round 2 (189 / 204 / 181 / 163 / 278), and every round-2 marker sentence checked in revision 2 is still present verbatim (first-upgrade sentence and `uf_prior_upgrades == 0`; the D5 replacement; `repeat_claim_share` labelled parameter; the reworded downgrade opener; the add-on window wording; the cancellation request-date wording; the D4 superseded clause; the O8 condition). The machine sweep below covers all six policies, and the per-task recomputations reproduce every round-2 figure for the five unchanged policies. The changes are all in `membership_ext_lapsed_renewal_fee`:
1. `rf_student_terms` now subtracts charges refunded as `duplicate_charge`.
2. A new rule sentence: "The Student Club membership years a Student Club membership has paid are counted as its new membership and renewal fee charges less every charge that was refunded as a duplicate charge." (its `compute_basis`).
3. A fifth `overwrite`: base status_tier_renewal "A Student Club membership also keeps its tier only while membership_msr_student_terms is below the tier's discounted_term_limit." replaced by that counting sentence.
4. The four earlier `overwrite` entries now share a new `replaced_by` (anchor `lapsed_scope`): "When an expired membership is renewed, the renewal fee of a lapsed membership set out below takes the place of the plain annual fee; an on-time renewal, a new membership, and a conversion or downgrade taken at an on-time renewal are still charged the annual fee of the tier the membership year is held at." This sentence is also inserted in the rule.

### policy_conflict_scan (revision 3)

Unchanged from revision 2: same policies, tools, owners, edges, components, subject separation. No new overlap.

### rule_compute_equivalence (revision 3)

Machine sweep (all six policies): every `compute_basis` quote verbatim in its rule; compute and basis keys correspond; every `baseline.rule` verbatim in its rule; every superseded clause verbatim in its base policy and every `replaced_by` verbatim in its rule.
- **E2 re-examined.** `rf_student_terms` = new_term + renewal_term charges − duplicate_charge refunds, which is the new rule sentence. The revision-2 demonstration case (Student, verification valid, three term charges plus one duplicate renewal charge refunded, lapsed renewal) now gives 3 paid Student years → below the limit 4 → stays Student, 32.50 basis — the same as the rule. **E2 closed.**
- All other bindings as in revision 2; E1 boundary behaviour unchanged (`rf_anniversary_kept` text identical).

### action_binding_and_uuids (revision 3)

Carried from revision 2 (tool module hash unchanged; `(target_tool, computes)` pairs re-confirmed identical and unique).

### prerequisite_graph and prerequisite_sentences (revision 3)

Four edges unchanged (form, kind, gate, `policy_source` verbatim, `resolved_by`, conditions); acyclic. No new cross-problem order in any rule: the two inserted lapsed-renewal sentences mention no other problem. Unchanged from revision 2.

### override_declarations (revision 3)

- **lapsed_renewal_fee.** Five declared supersessions, all verbatim. The counting replacement for the base Student term-limit sentence is what makes the extended count (net of duplicates) legal against base `membership_msr_student_terms` (which counts charges without that deduction) — the E2 change is declared.
- **O13 re-examined.** The shared `replaced_by` now states its own scope: a lapsed renewal is charged the lapsed-renewal fee, and an on-time renewal, a new membership, and a conversion or downgrade at an on-time renewal are still charged the annual fee of the tier held. The fee for every renewal kind is now fixed whatever reading of overwrite scope is taken. **O13 closed** for the fee quantity.
- **New observation O15 (introduced by the E2 fix).** The fifth supersession replaces the base sentence that makes a Student Club membership lose its tier at the term limit ("keeps its tier only while membership_msr_student_terms is below the tier's discounted_term_limit") with a sentence that only says how the years are counted. The extended rule states the consequence of reaching the limit (conversion to Northgate Club Membership) for **lapsed** renewals only. If supersession applies outside the policy's own subject — which the new scope sentence assumes by talking about on-time renewals — then for an **on-time** Student renewal at the limit, no remaining rule sentence says the tier is lost. The only trace left is the parameter description `discounted_term_limit: "maximum number of consecutive membership years at this discounted tier"`, and even that does not name the target tier (`eligibility_lapse_conversion_tier` is described for failed verification only). If supersession stays within the policy's subject, base still governs on-time renewals and the result is unique. No task writes an on-time renewal, so this stays an observation, the same class as O13 in revision 2; it is listed because it is new text.
- Other five policies: unchanged declarations (revision 2).

### factor_ladders (revision 3)

Unchanged from revision 2 for all six policies: lapsed_renewal_fee keeps loyalty (M), card credit (P), conversion grace credit (P), late fee (P). The baseline's held-tier sentence now relies on the net-of-duplicates Student-year count; it is still the base charter's own conversion rule and the declared count, so it is an honest standard method. Counts: 4/4/5/4/4/5 factors, each ≥ 1 method and ≥ 2 parameter; ladders ≥ 3 distinct tiers; fall-through = baseline throughout.

### findings (revision 3)

| id | revision-2 status | revision-3 status |
| --- | --- | --- |
| E2 | SOURCE-POLICY RED (charter) | **closed** (compute nets duplicates, rule states it, override declared; demonstration case now agrees) |
| O13 | observation | **closed** for the fee (scope sentence fixes the fee of every renewal kind) |
| O14 | observation (task-1 design_rationale) | checked in `1.md` revision_3 after reveal |
| D1–D5, E1, F1–F3, O5–O9 | closed | still closed (texts present; recomputations unchanged) |
| O2–O4, O10–O12 | observations | unchanged |
| **O15 (new)** | — | observation: the Student term-limit supersession leaves an on-time renewal at the limit without a stated consequence if supersession is read globally; no task world reaches it |

### closing_checklist (revision 3)

Written after the round-3 reveals (2026-10-05T22:42:46Z); nothing in `revision_3` above this heading was changed after the reveal.

- Files: `0.md`, `1.md` carry rounds 1–2 untouched plus `revision_3` (frozen derivation, comparison with PASS, findings).
- Round-2 items: E2 closed; O13 closed (fee scoped explicitly); O14 closed. All earlier closures (D1–D5, E1, F1–F3, O5–O9) still hold. Reworker's round-3 claims verified, none accepted unchecked.
- New: O15 (observation) — the declared replacement of the base Student term-limit sentence leaves the consequence of reaching the limit at an **on-time** renewal unstated if supersession is read beyond the policy's subject. The task-0 design_rationale states the subject-scoped reading. No task world reaches it.
- Coverage/scope: unchanged, disjoint, jointly complete; tools and GT closed; uuid8s independent.
- Trees: task 0 — 1 prerequisite, 1 value_input, user-owned renewal; task 1 — 3 prerequisites, 3 value_input, user-owned guarantee and cancellation; graph acyclic.
- Factors: every computation has an honest, self-sufficient baseline with a fall-back different from gold (65.00/43.50, 65.00/61.25, 35.72/23.60, 65.00/41.54, 65.00/47.34, 236.12/172.49); 4–5 factors each with ≥ 1 method and ≥ 2 parameter; every factor bears weight; each task has a multi-source factor and an order-reading cross-difficulty factor.
- Gates: not re-run by the auditor; the round-3 coordinator snapshot (all OK, TRACEABILITY deferred to KB render) applies to the audited hashes (extended 5d502190…49cb, tools 3015b122…3f3, task files 0b709857…117d and 3bbef04a…7567).
- **Difficulty status: PASS** at the source layer. Both tasks pass all four relationships; no SOURCE-POLICY / SOURCE-CHAIN / SOURCE-FACTOR / SOURCE-TASK red remains. Open observations: O2–O4, O10–O12, O15.
