# Policy-task audit — small_business_payouts / charter-global

## charter_global_frozen

- Freeze time: 2026-10-04T16:36Z (written before any task's GT was revealed; nothing in this section is derived from a revealed GT field).
- Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiating agent.
- Inputs and hashes (sha256, checked against the coordinator's VIEW_MANIFEST.txt and against the live files):
  - `env/env_0030_money_transfer_service/tasks/small_business_payouts/business.extended.yaml` = `8b964dc2c622f063dcafce1f3c446ab7dab047749b0cb868c08a8d2e55fceec2` (masked-view copy has the same hash)
  - `env/env_0030_money_transfer_service/tasks/small_business_payouts/task_tools.py` = `885a29547b918441011b91c9e25222e7a9c742287f762c007c58a1775a621bdd` (masked-view copy has the same hash)
  - `blueprint/products/business.yaml`, `blueprint/blueprint.yaml`, `blueprint/share_tools.py`, `blueprint/products/account.yaml` (level_number ladder only)
- Fields permitted here: the charter, the tool module, the blueprint and the shared tool schemas. Fields masked: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`; every worklog.
- Entry conditions (Step 0): gate snapshot supplied in the brief and in `/tmp/erl0030_gates/small_business_payouts.txt` — check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cache_diff INFO, check_cross_fire SCOPE OK; check_traceability not run (needs the published KB). Masked views constructed with hashes. Observation E-1: the replay snapshot prints a row only for `1.json` (`1.json 15 True True 0 211 211 True`); no row for `0.json` appears in the snapshot. The gate line is still `REPLAY OK`; recorded, not treated as a defect of the artifacts.
- Base-section verbatim check: the first 1483 lines of `business.extended.yaml` are byte-identical to `blueprint/products/business.yaml` (`diff` shows only the appended `extended_policies` banner).

### policy_conflict_scan

Six extended policies, each with its own subject, target tool and computed quantity:

| policy | subject | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| business_ext_period_subscription_charge | business_reinstated | collect_overdue_subscription_325cf5bc (agent) | amount_usd | [] |
| business_ext_downgrade_termination_charge | business_downgrade_scheduled | schedule_plan_downgrade_6c5bcb1c (user) | early_termination_fee_usd | -> subscription_charge (value_input, state) |
| business_ext_mid_period_seat_charge | business_user_added | charge_extra_seats_0d292d98 (agent) | amount_usd | [] |
| business_ext_card_deposit_fee | business_balance_deposited | charge_card_deposit_fee_e69fd8f7 (agent) | fee_usd | [] |
| business_ext_upgrade_proration_settlement | business_proration_credited | settle_upgrade_proration_4280c277 (agent) | amount_usd | [] |
| business_ext_withdrawable_balance | business_balance_withdrawn | withdraw_business_balance_ad66ed9d (user) | amount_usd | -> seat, proration, card fee (3 x value_input, state) |

- Overlapping subjects/terminal states: no two extended policies write the same fee_type or the same row kind (subscription_fee / early_termination_fee / extra_seat_fee / deposit_fee / proration_charge / business_balance_withdrawn). The base dedup `charge_once_per_period` (fee_type + billing_period_start, distinct by payout/deposit reference and seq_in_period) is compatible with each tool's row shape.
- Triggers/time anchors: every extended computation is evaluated on "the day the charge is worked out" = the handling day (NOW). Windows are uniformly "from the day after the same calendar day N months earlier up to and including that day".
- Eligibility inherited from base and not overridden: `account_active` (plan change only while active) for the downgrade; `account_open_for_users`/`seat_cap` for users; `withdrawal_status` and verified-bank-account destination for withdrawals; `deposit_status` for deposits.
- Cross-category read boundaries: three policies read the owner's Personal Sender Account (account category) and declare it in `cross_category` (subscription: level_number,status; downgrade: opened_date,status; withdrawable: level_number,status). Base `business_agg_entity_separation` says the two are "separate contracts" for limits, balance and allowance; it does not forbid pricing on the personal relationship. No conflict.
- Claimed scopes (from the masked worlds' shapes and each task's root request; confirmed after reveal in the per-task files): task 0 = {downgrade_termination_charge, period_subscription_charge}; task 1 = {withdrawable_balance, mid_period_seat_charge, upgrade_proration_settlement, card_deposit_fee}. Pairwise disjoint, jointly complete over the six extended policies.
- Observation O-G1 (claim boundary): `business_ext_card_deposit_fee.subject = [business_balance_deposited]`, which is not in this difficulty's claimed `event_types` in `blueprint.yaml` (the row it actually writes, `business_fee_charged`/deposit_fee, is). `business_ext_upgrade_proration_settlement.subject = [business_proration_credited]` while its tool writes a `business_fee_charged` row with `fee_type=proration_charge` and no `business_proration_credited` row. Labelling only; no world consequence.

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quotation and back from every rule sentence to a binding.

- period_subscription_charge: every binding has a verbatim rule quotation; the five ladders (activity_billing, tenure_discount, personal_relationship_credit, deposit_relationship_credit, returns_servicing_surcharge) are each stated in full in the rule and implemented branch-for-branch in compute (tier 2 of tenure "15 to 29" = `>= 15` after the `>= 30` branch; activity "half ... rounded down to the whole dollar" = `(fee/2)//1`, "three quarters ... rounded up to the whole dollar" = negated floor). The collection sentence ("worked out on the day of collection as above") fixes NOW as the handling day.
  - Observation O-G2 (rule promise without compute): "An annually billed account is charged the plan's annual fee at the start of every twelfth period, unchanged" has no compute branch and no `compute_basis` entry; compute always returns the monthly-path result. Neither task world is an annually billed account at this write (task 0 is `billing_cycle: monthly`), so no consequence can be demonstrated.
- downgrade_termination_charge: every binding quoted; months_charged, month_price, retention, upgrade-loyalty, personal-customer credit and fee-offset ladders match rule and compute branch-for-branch; the combined-percentage step ("first added into one percentage ... reduced once") = `RND(gross * (100 - (retention_pct + upgrade_loyalty_pct)) / 100, 2)`.
  - Observation O-G3: the upgrade-loyalty rule names three tiers "12 or more whole months", "1 to 11 whole months", "an account that has been on the committed plan since approval"; an account upgraded fewer than one whole month after approval (0 whole months, plan_effective_date != kyb_approved_date) is described by no tier sentence; compute gives 0. Task 0's gap is 18 whole months, so no consequence there.
  - Observation O-G4: the rule's first sentence restricts the charge to a downgrade "the owner schedules before the commitment end date"; compute has no branch returning 0 outside that, so it relies on the reader's scope check. No task world sits outside the commitment.
- mid_period_seat_charge: every binding quoted; "the active users being the owner plus every user added less every user removed" = `1 + COUNT(added) - COUNT(removed)`; days_left/period_days inclusive counts; both period-method branches round up to the cent (negated floor on x100), fall-through rounds half up. Equivalent in both directions.
- card_deposit_fee: every binding quoted; size-rate fall-through = `P('card_deposit_fee_pct')`; bank-funding tiers match; charging method tier 1 `(deposit - 1000) * rate / 100`, tier 2 `MN(75, ...)`, fall-through whole deposit; final `MX(0, ...)` = "never below 0.00". Equivalent.
- upgrade_proration_settlement: every binding quoted; unused_days = plan_effective_date..period_end inclusive, days_used = period_start..day before upgrade; settled-share ladder, incentive, SWIFT rebate and deposit credit match. Equivalent.
  - Observation O-G5 (ladder shape): the upgrade incentive gives 25 % for >= 150,000.00 USD with >= 24 whole months, 10 % for 60,000.00-149,999.99 USD with >= 12 whole months, and 0 % otherwise — so an account with >= 150,000.00 USD of payout principal approved 12-23 whole months earlier gets nothing while a smaller-volume account of the same age gets 10 %. Recorded as an observation on ladder realism; whether it touches task 1's world is settled in `1.md`.
- withdrawable_balance: every binding quoted; reserve basis, ACH hold, reserve rate, reserve relief (level_number >= 4 = Enhanced/Premier/Private Client per `blueprint/products/account.yaml` ranks 4-6; level 3 = Verified Plus), next-charge reserve and withdrawal-fee terms match. The standing reserve rounds up to the cent (negated floor), the result rounds half up. Equivalent.
  - Observation O-G6: the rule reads the plan parameter `ach_deposit_hold_business_days` (defined in `parameter_schema` as "Paloma business days") as a count of calendar days ("while fewer calendar days than the plan's ACH hold days have passed"). Declared inside the superseded withdrawal-limit clause; whether a weekend makes the two readings diverge on a task world is checked in `1.md`.

No tier lives only in compute or only in the rule. No SOURCE-POLICY RED from check 2.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: six distinct tools, each claimed by exactly one policy; no base policy claims a task tool.
- Docstrings: each describes one atomic write, its row and its balance effect; none names another tool, a policy id or a sequence position. Each contains the sentence "Afterwards the owner sees ..." describing the call's own visible effect; this is not an ordering between actions (observation O-G7 only).
- Tool bodies: none reads a prerequisite, an eligibility state or a computed amount; each creates one ledger row with the given values and subtracts it from `balance_usd` (collect also sets `status=active`, `past_due_since=""`; downgrade also sets `scheduled_variant_name`/`scheduled_change_date`).
- uuid8 tails: 325cf5bc, 6c5bcb1c, 0d292d98, e69fd8f7, 4280c277, ad66ed9d — no shared prefix or suffix, no sequence, no adjacent values; consistent with independent generation.
- Observation O-G8: base `business_evt_balance` keeps "each later one carries withdrawal_fee_usd as withdrawal_fee with the same seq_in_period" (not superseded); the withdrawable rule subtracts that fee from the withdrawable amount, but no tool of this difficulty books a `withdrawal_fee` row. Consequence only where the period's free withdrawals are already used; checked against task 1's world in `1.md`.

### prerequisite_graph

- `prerequisite` filled on all six policies (`[]` on four). Edges: downgrade -> period_subscription_charge; withdrawable -> mid_period_seat_charge, upgrade_proration_settlement, card_deposit_fee. No edge targets a base policy or itself; graph acyclic (both trees have depth 1).
- Each `policy_source` located verbatim in the blocked policy's own `rule` (checked by string match): downgrade line 1719-1720; withdrawable lines 2474-2475, 2476-2477, 2478.
- `form: state` on all four; no `fallback_reason` present; none required.
- `kind: value_input` on all four; `gate` bindings exist in the blocked compute: `months_charged` (downgrade), `balance_now` (withdrawable x3).
- `resolved_by` equals the depended-on policy's `target_tool` on all four edges, and each tool's effect makes the stated state hold: collect writes a subscription_fee row for `current_period_start` and clears `past_due_since`; charge_extra_seats writes an extra_seat_fee row and lowers `balance_usd`; settle_upgrade_proration writes a proration_charge row and lowers `balance_usd`; charge_card_deposit_fee writes a deposit_fee row tied to `deposit_reference` and lowers `balance_usd`.
- `condition` strength: downgrade "no past-due date and its most recently collected subscription fee entry is booked for the current billing period" = the sentence "carries no subscription charge still owed for a billing period that has already started" for a monthly-billed account (the only reading for a monthly account). Withdrawable conditions restate their sentences at the same scope, with one scope point recorded under prerequisite_sentences (card fee).
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any prerequisite field.

### prerequisite_sentences

Four-point test on every edge:

1. Downgrade: "The early termination charge of a downgrade is fixed only after the account carries no subscription charge still owed for a billing period that has already started." — connective "only after"; state form ("carries no subscription charge still owed for a billing period that has already started", read off `business_accounts.status/past_due_since` and the ledger's subscription_fee rows); no tool, id or snake_case token; scope = any started period with an owed charge. Single resolving write: the only policy whose rule produces "collects that period's subscription charge ... and the account returns to active with no past-due date" is `business_ext_period_subscription_charge` (last sentence of its rule). No other write of this difficulty books a subscription fee. Derivation: sentence -> records show `past_due_since` set and no subscription_fee row for `current_period_start` -> the subscription rule's collection sentence -> collect_overdue_subscription. One reading.
2. Withdrawable/seats: "The withdrawable amount is not worked out until the balance carries an extra seat fee for every user added in the past month while more users were active than the plan includes." — connective "not ... until"; state form; no tool name. Single resolving write: only the seat policy books `extra_seat_fee` mid-period (the base period-start seat charge is a system event at period start, not a write of this difficulty). One reading.
3. Withdrawable/proration: "The withdrawable amount is worked out only after an upgrade that took effect inside the current billing period carries its proration charge on the balance." — "only after"; state form; single resolving write = settle_upgrade_proration (the only policy booking a proration charge). One reading.
4. Withdrawable/card fee: "Before the withdrawable amount is worked out, every debit-card deposit must carry its deposit fee on the balance." — "Before"; state form; single resolving write = charge_card_deposit_fee. Observation O-G9 (scope): the sentence says "every debit-card deposit", while the card-fee rule works out a fee only "for the most recent debit-card deposit on the account's ledger"; where two or more card deposits lack a fee row, the waited-on state cannot be reached by the depended-on policy as written. Whether any world has more than one unfeed card deposit is checked in `1.md`.

- No rule restates another rule's prerequisite sentence; no extended rule states a cross-problem order beyond these four sentences. The base contains order sentences that ground no edge — `business_evt_closure` "the owner withdraws the balance and every payout is paid, cancelled or returned first" and `business_evt_plan_change` "A plan can be changed only while the account status is active" (an eligibility gate that coincides with edge 1) — neither task's tree rests on a base sentence alone (task 0's edge has its own extended sentence). Observation O-G10.
- Docstrings silent about sequence (see action_binding_and_uuids).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- period_subscription_charge vs `business_evt_subscription_billing`: S1 period definition — followed. S2 "At the start of every period the subscription is charged ... monthly_fee_usd ... annual_fee_usd ..." — replaced; declared in `overwrite`. S3 period-start extra_seat_fee — followed (untouched). S4 "When the balance cannot cover a charge in full, nothing is taken, the charge stays owed, and the account becomes past_due ..." — followed. S5 grace, S6 suspension point — followed. S7 "When the owner has deposited enough, the agent collects every overdue charge from the balance and the account returns to active" — followed in act; the amount is the replaced S2 quantity, and the extended rule fixes its evaluation day ("worked out on the day of collection as above"). Observation O-G11: S4's "the charge stays owed" could be read as the period-start amount persisting; base fixes no amount outside the superseded S2, so the extended sentence is the only statement of the evaluation day and no undeclared override arises. The per-task file states the period-start number for comparison. S8 "Fees are never charged twice for one period" — followed.
- downgrade_termination_charge vs `business_evt_plan_change`: owner's decision — followed (user tool); active-only — followed; downgrade at next period — followed ("the downgrade itself still takes effect on the first day of the next billing period"); seats/channels gate — followed; ETF sentence — replaced; declared (including the "taking effect" -> "schedules" scope change); "Allowance, limits, fees and seats of the new plan apply ... after the change" — followed. Upgrade sentences are not in this policy's scope (handled by the proration policy).
- mid_period_seat_charge vs `business_evt_seats`: role/owner-counts-as-one — followed (active-user formula equals the base measure unless an email is re-added after removal); active/past_due — followed; seat cap — followed; mid-period charge sentence (including "not prorated and not refunded") — replaced; declared; "already active is not added again", removal at once — followed.
- card_deposit_fee vs `business_evt_balance`: deposit methods, deposit status, ACH hold for payouts, max balance — followed; card/wire fee sentence — replaced; declared (wire part kept "unchanged"); withdrawal sentences — outside scope.
- upgrade_proration_settlement vs `business_evt_plan_change`: proration sentence (credit + proration_charge) — replaced by one net proration charge; declared; "An upgrade takes effect on the day it is made" — followed; free payouts not changed — followed.
- withdrawable_balance vs `business_agg_entity_separation`, `business_evt_balance`: own-balance-only, verified-US-bank destination — followed; withdrawal status — followed; "it may not exceed the available balance less charges still owed" — replaced; declared (the replacement drops "charges still owed" and redefines the ACH hold); "each later one carries withdrawal_fee_usd as withdrawal_fee" — kept, see O-G8; "The balance never goes below 0.00" — followed.

No undeclared override found. Three disguised forms checked: no anonymous intermediate replaces a base quantity outside a declared clause; the existence-condition multipliers (`latest_ach_amount * (ach_age_days < ...)`) sit inside the declared withdrawable replacement; no base branch is dropped by a selector except the annual-billing branch noted in O-G2.

### factor_ladders

| policy | factor | effect | decides | tiers | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| subscription | activity_billing | method | billed_fee | 3 | yes (approval date on account row + payout rows) | - |
| subscription | tenure_discount | parameter | tenure_discount_pct | 3 | yes (approval date + paid payout rows) | - |
| subscription | personal_relationship_credit | parameter | relationship_credit | 3 | level + status of one row | account |
| subscription | deposit_relationship_credit | parameter | deposit_credit | 3 | no | - |
| subscription | returns_servicing_surcharge | parameter | return_surcharge | 3 | no | - |
| downgrade | months_charged_basis | method | months_charged | 3 | yes (ledger subscription row + account dates) | - |
| downgrade | month_price_selection | method | month_price | 3 | no (approval date) | - |
| downgrade | retention_discount | parameter | retention_pct | 3 | yes (debit/credit-back rows + returned payout rows) | - |
| downgrade | upgrade_loyalty_discount | parameter | upgrade_loyalty_pct | 3 | no | - |
| downgrade | personal_customer_credit | parameter | personal_credit | 3 | opened_date + status of one row | account |
| downgrade | payout_fee_offset | parameter | fee_offset_pct | 3 | no | - |
| seats | seat_period_method | method | period_charge | 3 | yes (approval date + period dates) | - |
| seats | seat_volume_reduction | parameter | volume_reduction | 3 | no | - |
| seats | approver_seats | parameter | free_seats | 3 | no | - |
| seats | batch_operations_reduction | parameter | batch_reduction | 3 | no | - |
| card fee | deposit_size_rate | parameter | size_rate | 3 | no | - |
| card fee | card_volume_reduction | parameter | volume_points | 3 | no | - |
| card fee | bank_funding_reduction | parameter | bank_points | 3 | yes (ACH rows + card rows) | - |
| card fee | card_fee_charging_method | method | card_fee | 3 | no | - |
| proration | settled_share_method | method | settled_share | 3 | yes (billing_cycle + period dates) | - |
| proration | upgrade_incentive | parameter | incentive_pct | 3 | yes (debit rows + approval date) | - |
| proration | swift_rebate_rate | parameter | swift_pct | 3 | no | - |
| proration | upgrade_deposit_credit | parameter | deposit_credit | 3 | no | - |
| withdrawable | reserve_basis_window | method | reserve_basis | 3 | no | - |
| withdrawable | ach_hold_method | method | ach_held | 3 | yes (approval date + ACH rows) | - |
| withdrawable | reserve_rate_by_returns | parameter | reserve_rate | 3 | no | - |
| withdrawable | personal_reserve_relief | parameter | relief_pct | 3 | level + status of one row | account |
| withdrawable | next_charge_reserve | parameter | next_reserve | 3 | no | - |

- Counts per policy: subscription 5 (1 method, 4 parameter); downgrade 6 (2 method, 4 parameter); seats 4 (1 method, 3 parameter); card fee 4 (1 method, 3 parameter); proration 4 (1 method, 3 parameter); withdrawable 5 (2 method, 3 parameter). All within 4-6, each with >= 2 parameter and >= 1 method.
- Per task: task 0 (subscription + downgrade) carries multi-source factors and two `account` cross-difficulty factors; task 1 (withdrawable + seats + card + proration) carries multi-source factors and one `account` cross-difficulty factor (personal_reserve_relief). The categories read: `account` only.
- Bindings disjoint within each policy; every `decides` is an input, never `result`. Every tier (condition and value/method) is a sentence of the rule and a branch of the binding; no two tiers of one ladder select the same value or method; each fall-through equals the policy's `baseline` for that input.
- Labels: every `method` factor changes how the quantity is computed (fee fraction with different rounding; months formula vs constant; latest vs largest vs list price; prorated vs half vs full; whole vs excess-over-1,000 vs capped; share = 1 vs /30 vs /period; 1-, 3- or 6-month principal window; no hold vs same-day hold vs N-day hold). Every `parameter` factor substitutes a number. Labels honest.
- Ladder realism — one failure:
  - **F-G1 (SOURCE-FACTOR RED; bears on task 0).** `months_charged_basis` tier 1 is the compound condition "the most recently collected subscription charge is booked for the current billing period, its period starts three or more whole months after the committed plan took effect, and the account has no past-due date". The part "the account has no past-due date" holds of every account that reaches this write: the downgrade write is gated by the inherited base eligibility `account_active` ("A plan can be changed only while the account status is active", `state_contract.allowed: [active]`), and in the charter's lifecycle an account reaches `active` only through `business_kyb_approved` (no past-due date yet) or `business_reinstated` (whose event fields say `past_due_since: "Cleared."`). That part therefore restates the policy's scope instead of dividing its customers. The demonstration on task 0's world is in `0.md`.
  - Observations (no demonstrable consequence on the charter alone): O-G5 above (upgrade incentive hole for >= 150,000.00 USD at 12-23 months). O-G12: "Approver seats are freed by the payouts a second user approved" uses an approval count as the gate for waiving seats, which is unusual pricing but internally coherent. O-G13: the card-fee bank-funding reduction lowers a card rate for ACH-heavy funders; this is relationship pricing, coherent.
- Baselines: every policy's `baseline.rule` is a verbatim sentence (or pair) of its rule, names the params in `baseline.params`, and on its own yields a definite number from the records (subscription: monthly fee; downgrade: ETF months x committed monthly fee; seats: users charged x extra seat fee; card: plan pct x whole deposit; proration: standard two-term formula; withdrawable: balance less N-day ACH hold, less 1 % of 3-month principal rounded up, less withdrawal fee when due).

### findings

1. **F-G1 — SOURCE-FACTOR RED (affects task 0).** Symptom: one part of the tier-1 condition of `months_charged_basis` cannot be false at the downgrade write. Root cause: the tier condition carries "and the account has no past-due date", which the inherited base gate `account_active` together with the lifecycle (reinstatement clears `past_due_since`) makes true for every account the downgrade can be written for. Evidence: `business.extended.yaml` downgrade rule ("when that charge was booked for the current billing period, its period starts three or more whole months after the committed plan took effect, and the account has no past-due date"); compute `months_charged: "... and F('past_due_since') == '') ..."`; base `business_evt_plan_change.eligibility[account_active]`; base event `business_reinstated.fields.past_due_since: "Cleared."`. Demonstrated consequence: see `0.md` (at the downgrade write the conjunct is true by construction). Affected: `business_ext_downgrade_termination_charge` rule tier 1, `factors[months_charged_basis].ladder[0].when`, compute `months_charged`.
2. Observations O-G1 to O-G13 above. None is a red light on the charter alone; O-G5, O-G6, O-G8 and O-G9 are checked against task 1's world in `1.md`, and O-G11 against task 0's world in `0.md`.

## closing_checklist

Written after both reveals (2026-10-04T16:42:17Z). The sections above were written before any reveal and have not been changed since.

**Status: NOT CLOSED.** Step 4 requires every task to PASS all four relationships; task 0 is SOURCE-FACTOR RED (F-G1, demonstrated in `0.md`). Checklist as it stands:

- Per-task files: `0.md` and `1.md` correspond one-to-one to `tasks/0.json` and `tasks/1.json`, with `_difficulty.md` alongside; first revision, nothing earlier to trace. Comparison verdicts: task 0 SOURCE-FACTOR RED; task 1 PASS.
- Coverage and scopes: GT `charter_scope` — task 0 {period_subscription_charge, downgrade_termination_charge}, task 1 {mid_period_seat_charge, upgrade_proration_settlement, card_deposit_fee, withdrawable_balance} — equals the scopes derived before the reveal; pairwise disjoint over whole trees; union = all six extended policies. Task tools closed (each GT write uses its policy's tool); uuid8s independent (see § action_binding_and_uuids).
- Trees: task 0 has 1 prerequisite problem and 1 value_input edge; task 1 has 3 prerequisite problems and 3 value_input edges; each tree has an owner=user root (downgrade; withdrawal); the difficulty's four edges form a DAG with no cross-task reference.
- Computations: every computation has a self-sufficient baseline and 4-6 factors (5, 6, 4, 4, 4, 5) with >= 2 parameter and >= 1 method; each task has a multi-source and an `account` cross-difficulty factor with the row seeded; every factor bears weight against an honest baseline, and every full baseline gives a definite number different from gold (299.00, 897.00, 35.00, 90.02, 300.00, 16,035.89). Outstanding: F-G1 (one conjunct of `months_charged_basis` tier 1 divides no customer).
- Gate re-run on the final form: not performed. The difficulty has not reached a final form (F-G1 is open), and per Step 0 this auditor cites the coordinator's gate snapshot instead of running gates.

## revision_2

### charter_global_frozen (revision_2)

- Written 2026-10-04 before any round-2 GT reveal; nothing here is derived from a revealed GT field. Round-1 text above is left untouched.
- Inputs: `business.extended.yaml` sha256 `694c91e47d5392b27a28b28bb666fd99ded2bff50f15be23e6df1433bab89adb` (changed from round 1's `8b964dc2…eec2`, so every charter-global section is re-derived below, not carried forward); `task_tools.py` `885a29547b918441011b91c9e25222e7a9c742287f762c007c58a1775a621bdd` (unchanged, so § action_binding_and_uuids is carried forward by reference). The base section (first 1483 lines) is still byte-identical to `blueprint/products/business.yaml`. The masked view matches the live files' hashes.
- Method: `diff` of the round-1 archived charter (`/tmp/erl0030_views/archive/small_business_payouts.r1/business.extended.yaml`) against the current one, then a re-check of every section the changed lines touch. Changed lines: subscription compute `result` and its `compute_basis`; downgrade rule (new no-commitment sentence, removal of the past-due conjunct, upgrade-loyalty fall-through wording), compute (`months_charged`, new `outside_commitment`, `result`), `compute_basis`, ladders; proration incentive rule/compute/basis/ladder; withdrawable card-fee prerequisite sentence, `policy_source` and `condition`. Nothing else changed.
- Entry conditions: round-2 gate snapshot `/tmp/erl0030_gates/small_business_payouts.r2.txt` — EXTENDED, TASK TOOL CONTRACT, REPLAY (rows `0.json 11 … True` and `1.json 15 … True`), SOLVABILITY, COMPUTE, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, all exit 0; check_traceability deferred. E-1 (only one replay row) no longer applies: the snapshot shows rows for both tasks.

### policy_conflict_scan (revision_2)

Unchanged from round 1: the same six policies, subjects, tools, computed quantities and edges; triggers, time anchors and cross-category reads are unchanged. The downgrade's new sentence ("A downgrade scheduled on a plan with no commitment end date, or on or after the commitment end date, carries no early termination charge, that is 0.00.") agrees with the base, which carries an ETF only inside the commitment. The scope partition is unchanged (task 0: subscription + downgrade; task 1: withdrawable + seats + proration + card fee). O-G1 still stands, as an observation.

### rule_compute_equivalence (revision_2)

- O-G2 (annual sentence without compute): **partly closed.** Compute now reads `result: "RND(P('annual_fee_usd'), 2) if F('billing_cycle') == 'annual' else …"`, and `compute_basis.result` quotes the annual sentence. Remaining gap (observation O-G2b): the rule charges the annual fee "at the start of every twelfth period", but compute returns the annual fee for an annually billed account in every period, with no twelfth-period test. Separately, `compute_basis.result` now joins two rule sentences with "…"; each fragment is verbatim. No task world is annually billed, so no consequence can be shown.
- O-G3: **closed.** The rule now says "fewer than 1 whole month, including an account on the committed plan since approval, earns none", which covers the compute fall-through `else 0`. The ladder and basis are worded the same way.
- O-G4: **closed.** The new rule sentence is quoted in `compute_basis.outside_commitment` and implemented as `F('commitment_end_date') == '' or F('commitment_end_date') <= NOW` -> result 0. "On or after the commitment end date" = commitment end <= the scheduling day, which matches. The scope difference from the base ("taking effect before") is still inside the round-1 declared overwrite.
- O-G5: **closed.** Incentive tier 2 now reads "60,000.00 USD or more with approval at least 12 whole months earlier, not meeting both first-tier conditions", implemented as `(vol >= 60000 and months >= 12) and (vol < 150000 or months < 24)`. The ladder now has no hole: >= 150,000 at 12-23 months gets 10 %. Rule, basis, ladder and compute agree.
- F-G1 edit: the conjunct is removed consistently from the rule, `compute_basis.months_charged`, `factors[months_charged_basis].ladder[0].when` and compute `months_charged`. The fall-through and tier 2 are unchanged.
- No other binding changed. All other round-1 conclusions of this section stand.

### action_binding_and_uuids (revision_2)

`task_tools.py` is unchanged (same sha256) and the policies' `target_tool`/`computes` pairs are unchanged, so the round-1 section is carried forward by reference. O-G7 and O-G8 still stand as observations.

### prerequisite_graph (revision_2)

Same four edges, kinds, gates, forms and resolved_by values. The changed `condition` of the card-fee edge ("The most recent debit-card deposit on the ledger has a deposit fee entry tied to its deposit reference, and the balance reflects it.") matches its new sentence at the same scope. The graph is still acyclic, and every `policy_source` is still verbatim in its blocked rule (checked by string match, including the changed card-fee sentence).

### prerequisite_sentences (revision_2)

- Card fee edge: "Before the withdrawable amount is worked out, the most recent debit-card deposit must carry its deposit fee on the balance." It uses the connective "Before", is state form, and names no tool or id. Its scope now equals the card-fee rule's object ("worked out for the most recent debit-card deposit on the account's ledger"), and charge_card_deposit_fee is the single resolving write. **O-G9 closed.**
- The other three sentences are unchanged and their round-1 conclusions stand. O-G10 still stands, as an observation.

### override_declarations (revision_2)

Re-swept only the changed policies. The subscription charge now implements the base's annual branch, so the base sentence S2 on annual billing is honoured ("unchanged" except for the O-G2b twelfth-period gap). In the downgrade, the zero-charge sentence for no commitment, or on/after its end, follows the base. In proration, the incentive change sits inside the declared net-proration replacement. In the withdrawable rule, the narrower card-fee sentence overrides no base sentence. No undeclared override. O-G11 still stands as an observation.

### factor_ladders (revision_2)

- Factor counts, labels, `decides` bindings and fall-through baselines are unchanged (5/6/4/4/4/5).
- **F-G1 — closed.** The `months_charged_basis` tier 1 condition now has two conjuncts: "the most recently collected subscription charge is booked for the current billing period" and "its period starts three or more whole months after the committed plan took effect". Re-tested with the same standard used in round 1:
  - "Three or more whole months after the committed plan took effect" divides accounts early in a commitment from later ones.
  - "Booked for the current billing period" is false for an annually billed account outside the first period of its twelve-period cycle, since annual billing charges "at the start of every twelfth period". Annual billing is allowed on every committed plan (`annual_billing_available: true` on Scale/Enterprise). So this conjunct divides customers, though on monthly-billed accounts it is always true at an active write (observation O-G14: its dividing power rests on annual billing alone).
  
  No conjunct now holds of every customer who reaches the write.
- Upgrade incentive ladder: three pairwise-disjoint tiers, now with no hole. O-G5 closed.
- O-G12 and O-G13 still stand as observations.

### findings (revision_2)

- F-G1: closed (evidence above).
- No new charter-global red light.
- Observations: O-G2b and O-G14 are new. O-G1, O-G6, O-G7, O-G8, O-G10, O-G11, O-G12 and O-G13 stand unchanged. O-G2 is partly closed; O-G3, O-G4, O-G5 and O-G9 are closed. E-1 no longer applies.

### closing_checklist (revision_2)

Written after both round-2 reveals (2026-10-04T17:26:01Z). The revision_2 charter-global sections above were written before the reveal and have not been changed since.

**Status: CLOSED — the difficulty passes the source-layer audit.**
- Per-task files `0.md` and `1.md` each carry a revision_2 with a frozen derivation, then a comparison, both PASS. The round-1 text is preserved above each revision_2, and round-1's task 0 RED is traceable to its closure.
- Coverage and scopes: GT `charter_scope` is unchanged — task 0 {subscription, downgrade}, task 1 {seats, proration, card fee, withdrawable}. The scopes are disjoint over whole trees, and together they cover all six policies. Task tools are unchanged and closed; the uuid8s are independent.
- Trees:
  - task 0 has 1 prerequisite problem and 1 value_input edge;
  - task 1 has 3 prerequisite problems and 3 value_input edges;
  - each tree has an owner=user root;
  - the four edges form a DAG.
- Computations:
  - 5/6/4/4/4/5 factors, each with >= 2 parameter and >= 1 method factors;
  - each task has a multi-source factor and an `account` cross-difficulty factor, backed by a seeded row;
  - every factor bears weight against an honest baseline, and every full baseline is definite and differs from gold;
  - every ladder has three disjoint tiers stated in the rule, and no conjunct restates the write's scope (F-G1 closed).
- Gates on the final form: cited from the coordinator's round-2 re-run (`/tmp/erl0030_gates/small_business_payouts.r2.txt`): EXTENDED, TASK TOOL CONTRACT, REPLAY (both tasks), SOLVABILITY, COMPUTE, GROUNDING and SCOPE OK, CACHE-DIFF INFO, all exit 0. check_traceability is deferred to the KB stage. The round-2 hashes are the final form audited here: charter `694c91e4…9adb` and tools `885a2954…1bdd`.
- Open observations (not red lights): O-G1, O-G2b, O-G6, O-G7, O-G8, O-G10–O-G14, O-T1-2 and O-T1-3.
