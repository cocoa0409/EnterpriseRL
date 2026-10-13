# Policy-task audit — seller_fees_and_selling_plans / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit subagent (Claude Opus 5.5), independent of the instantiating agent. Run from `/home/ubuntu/github/enterprise_rl`.
- Freeze time: 2026-10-11T04:57Z (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Frozen inputs (sha256 re-verified by the auditor, all equal to `.audit_views/policy_task/seller_fees_and_selling_plans/HASHES.txt`):
  - `tasks/seller_fees_and_selling_plans/selling.extended.yaml` 58bbf1cfa1ec3a72f2dc7ef3343a442820d2556609c7ae5d2648da2ca00b6aac
  - `tasks/seller_fees_and_selling_plans/task_tools.py` 0613ba437fccc73c01052faff80d26cd86f89f49775d4d01e8aa974185614706
  - `0.view.json` bd8a39de…c55846f (source `tasks/0.json` 3648c21f…719d2), `1.view.json` a6c8cda6…aaa23 (source `tasks/1.json` 75b1a873…0e432)
- Read: `blueprint/blueprint.yaml`, `blueprint/products/selling.yaml`, `blueprint/db_schema.json` (tables used), `blueprint/share_tools.py`, the extended yaml, `task_tools.py`, the two masked views, the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/within_months/LATEST/X* evaluators only).
- Masked / unread at this point: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*` of both tasks; any audit file of another difficulty (not opened). No recursive search touched `tasks/` or `env/`.
- Entry conditions (Step 0): gate snapshot `gates.r1.txt` supplied — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, all rc=0; masked views + hashes supplied and verified. Entry conditions met.
- Base copy: lines 1-790 of the extended yaml are byte-identical to `blueprint/products/selling.yaml` (only difference: one trailing blank line). Base is verbatim.

### policy_conflict_scan

Extended policies (6): `selling_ext_discount_dispute_credit` (dd), `selling_ext_term_change_fee` (tc), `selling_ext_chargeback_fee_credit` (kc), `selling_ext_cancellation_fee_credit` (cx), `selling_ext_early_termination_fee` (et), `selling_ext_refund_fee_credit` (rc).

- Overlapping subjects: dd, kc, cx, rc all write `selling_fee_credit` (`computes: credit_amount`), each on its own tool and keyed by a different trigger (dispute ground / chargeback debit / seller cancellation defect / seller-funded refund debit). The order sets they select are disjoint except one: a seller-funded refund debit on an order the seller cancelled before shipment is matched by both rc's object finder (`rc_order: XLATEST payout_refund_debit`) and cx's trigger. rc's own rule settles it ("an order the seller cancelled before it shipped is credited under the cancellation credit instead and earns no refund credit"), but rc's compute does not exclude such a debit when choosing the order (see findings O-3). tc and et both book a `selling_early_termination_fee` record (tc: move to monthly, plan stays open; et: plan closes); their triggers (persona asks to switch term vs. to close) are disjoint.
- Time anchors: every window is evaluated against `frozen_time` (`NOW`). "last N whole months" is evaluated by the compute as `0 <= MONTHS(event_date, NOW) < N` (rolling, counted back from the decision date). The rule says so explicitly in dd ("within that many whole months before the decision date") and rc ("the months are whole months counted back from the decision date", for the recent-defect window only); tc, et, kc and cx say "the last twelve whole months" without restating the convention (observation O-4).
- Eligibility / terminal states: no two policies set the same terminal field to different values on overlapping triggers. Base eligibility left in force: dispute window 90 days and 1 dispute per fee (dd), refund credit window 180 days and "Refunds funded by Northloop earn no credit" (rc), "Credits on one fee record, administration fees included, never exceed the fee billed" (dd/kc/cx/rc), plan change blocked while restricted (tc), annual-term early end is the seller's own decision (et, tc).
- Cross-category reads: standing (level, violation points, defects), payout (plan, balance, refund/chargeback debits), fulfill (enrollment status, units on hand, outbound shipment). All are declared in `cross_category`, and every read field exists in `db_schema.json`.
- Claimed scopes, as derived blind from the prerequisite graph and the two personas (`charter_scope` is masked): task 0 = {tc (root), kc, cx, dd}; task 1 = {et (root), rc}. The two sets are pairwise disjoint and together cover all 6 extended policies.
- Latent conflict (observation O-3): et's prerequisite sentence waits until "every seller-funded refund debited to the seller's payments account in the last twelve months carries its refund credit". rc's rule says a seller-funded refund on an order cancelled before shipment "earns no refund credit". In any world holding such a debit, the et gate can never be satisfied. Task 1's world holds no such debit, so this has no consequence here.

### rule_compute_equivalence

Every compute binding of the six policies was checked against its `compute_basis` quotation and the rule, both ways (binding-by-binding notes kept in the auditor's scratch; summary here):

- dd: the disputed record (LATEST submitted standing_discount_missing by `created_at`), billed amount, level rate (Preferred Partner / Top Rated + FBN outbound shipment / else), volume window (active ≥500 / active <500 / else), window basis (`within_months=dd_volume_window`), volume bonus (≥20000 / ≥8000 / 0), handling bonus (`DAYS(fee date, FBN ship date)` 0 / 1 / else or none → 99), tenure (`MONTHS(verified_date, NOW)` ≥36 / ≥24 / 0), defect adjustment (chargeback or guarantee_claim / negative_feedback / 1), rate = sum, `RND(billed*rate*mult,2)`. Every tier is in the rule. No invented basis. Minor: the rule's "carries a … defect" is read without netting `standing_defect_removal`. That has no effect in either world.
- tc: gap, `MONTHS(term_start,NOW)+1` term window, annual regular charge count, tenure lookback (`MN(count,3)` / `MN(count,6)` / count), 12-month net fees (subscription + insertion + FVF + ETF − credit amounts), volume / standing / payout reliefs, FBN multiplier (active ≥500 / active >0 / 1), share = 1 − Σ, `RND(gap*repaid*share*fbn,2)`. Equivalent.
- kc: the order (XLATEST chargeback debit), fee ref / date / billed / basis, prior = Σ gross credits on the record, creditable `MX(0,…)`, raw share `MN(1, cb/basis)`, share ladder (≥0.9 → 1 / <0.2 → ×0.5 / else), gross, 12-month chargeback count, admin rate, cap, timing (≤14 / ≤45 / 1), tenure, FBN relief (same day / any shipment / 0), `MX(0, MN(RND(gross*rate*t*ten,2), cap) − relief)`, result. Equivalent. The rule limits the credit to chargebacks "that the seller is liable for", but `kc_order` takes the latest debit whether or not it was later reversed (observation O-5; no reversal is seeded).
- cx: the order (XLATEST seller_cancellation defect), creditable, days, share (≥4 → 0.5 / ≥2 → 0.75 / 1), gross, 12-month cancellation count, rate (≥2 & discount level → 0.05 / ≥2 & other → 0.10 / 0), cap, refund relief (0 / 1 / else, none → 99 → 0), admin, result. Equivalent. The rule's relief ladder says "nothing when it was debited later" but is silent on no refund debit at all; the compute's 0 is the only sensible reading (observation, no consequence).
- et: fee, months left `MONTHS(next_billing_date, term_end_date)`, renewal detection `MONTHS(verified_date, term_start_date) > 0` vs the rule's "start date is later than the plan's verification date" (they differ only for a renewal less than one whole month after verification, which is impossible on a 12-month term), grace months `int(x*0.5)` / `int(x*0.75)` / x, net fees, standing relief, all-time regular charge count, loyalty relief, share = plan share − Σ, `RND(fee*months*share,2)`. Equivalent. See O-6 on the meaning of "whole calendar months … a month not completed by the term end date not being counted".
- rc: the order (XLATEST payout_refund_debit), creditable, Σ refund debits / basis capped at 1, share ladder (≥0.9 → 1 / ≤0.25 → ×0.5 / else), gross, level + recent-defect rate (`within_months=2`, any defect type), cap, 3-month refund count multiplier, tenure multiplier, FBN relief, admin, result. Equivalent, except that the "seller-funded" filter and the rule's exclusion of cancelled-before-shipment orders are not implemented in `rc_order` (O-3).

No tier lives only in compute, and no rule ladder is missing from compute.

### action_binding_and_uuids

- `(target_tool, computes)`: dd → (`uphold_fee_dispute_credit_4fd06f6c`, credit_amount); kc → (`book_chargeback_fee_credit_32d8a153`, credit_amount); cx → (`book_cancellation_fee_credit_79bf63bc`, credit_amount); rc → (`book_refund_fee_credit_a1b0f084`, credit_amount); tc → (`switch_store_to_monthly_term_ae40bf8f`, term_change_fee); et → (`end_store_term_early_4fd1aef8`, early_termination_fee). Each pair is claimed once.
- Owners: switch / end-term are `owner="user"`. They match the base rule "Cancelling a plan is the seller's own decision" and tc's "the move is the seller's own decision". The four credit tools are `owner="agent"`.
- Docstrings: no docstring names another tool, states a position in a sequence, or uses an ordering connective. "before the administration fee" / "while it was unshipped" are amount and state descriptions, not sequencing. Every function body only creates or updates rows from its arguments and judges no eligibility or prerequisite (`task_tools.py` lines 58-70, 107-120, 157-170, 196-210, 247-260, 285-298).
- The three credit tools other than dd's are functionally identical (any `credit_reason` is accepted). The policies and docstrings separate them by business reading; no consequence.
- uuid8s: 4fd06f6c, 32d8a153, 79bf63bc, ae40bf8f, a1b0f084, 4fd1aef8. **`4fd06f6c` and `4fd1aef8` share the 3-hex prefix `4fd`.** For independently drawn uuid8s, the chance that some pair among 6 shares a 3-hex prefix is about 15/4096 ≈ 0.37%. This looks like a common prefix and cannot be confirmed as independent generation (observation O-1). The other four show no shared prefix, sequence or adjacency.

### prerequisite_graph

| blocked policy | problem | kind | gate (exists in compute?) | form | resolved_by = problem's target_tool? |
| --- | --- | --- | --- | --- | --- |
| tc | kc | value_input | tc_net_fees (yes) | state | yes (`book_chargeback_fee_credit_32d8a153`) |
| tc | cx | value_input | tc_net_fees (yes) | state | yes (`book_cancellation_fee_credit_79bf63bc`) |
| kc | dd | value_input | kc_prior (yes) | state | yes (`uphold_fee_dispute_credit_4fd06f6c`) |
| et | rc | value_input | et_net_fees (yes) | state | yes (`book_refund_fee_credit_a1b0f084`) |
| dd, cx, rc | — | `prerequisite: []` | | | |

- Every policy has `prerequisite` filled in. Every `problem` is an extended policy id of this file, never a base policy and never self. The graph is acyclic: dd → kc → tc ← cx; rc → et.
- Every `policy_source` was located verbatim in the blocked policy's own `rule`: tc rule sentences 2 and 3, kc rule sentence 3, et rule sentence 2.
- `form: state` on all four edges, with no `fallback_reason`. This is consistent.
- `condition` against sentence: tc←kc ("every payout chargeback debit dated within the last twelve months … carries a seller fee credit booked with the order refund credit reason"), tc←cx ("every seller cancellation defect dated within the last twelve months … order cancellation credit reason"), kc←dd ("No seller fee dispute with status submitted names the variable … record …; every dispute on it is upheld or rejected"), et←rc ("every seller-funded payout refund debit dated within the last twelve months … order refund credit reason"). Each states, at the same scope, the record-visible form of its sentence. None is strengthened or weakened.
- `effect`: each named binding (`tc_net_fees`, `kc_prior`, `et_net_fees`) is changed by the resolving write: a new `selling_fee_credit` row dated NOW enters the 12-month net-fee sums or the prior-credit sum. Confirmed by the tool bodies (credit row with `event_type="selling_fee_credit"`, `event_date=today`, `fee_event_ref`, `gross_credit_amount`).
- No authoring-viewpoint wording ("in this task", "at the opening") appears in any `prerequisite` block.

### prerequisite_sentences

Four-point test on each sentence:

1. tc←kc: "The term change fee is not worked out until every chargeback debited to the seller's payments account in the last twelve months carries its chargeback credit on the order's variable final value fee record."
   - Connective: "not … until".
   - Waited-on state: credit present on the variable FVF record, named in finder words (payments account, chargeback, variable final value fee record).
   - No tool, id or snake_case token.
   - Scope matches the condition (open set "every chargeback … in the last twelve months").
   - Hop: "chargeback credit" is the name kc's own rule gives its write ("earns a chargeback credit on the variable final value fee record"). No other policy writes a chargeback credit. rc also books `order_refund` credits, but on refund debits, so a reader resolves the hop to kc alone.
2. tc←cx: "The term change fee is worked out only after every order the seller cancelled before shipment in the last twelve months carries its cancellation credit on the order's variable final value fee record."
   - Connective: "only after".
   - Waited-on state: a cancellation credit on the record. Only cx writes a "cancellation credit", so the resolving action is single.
3. kc←dd: "The chargeback credit on an order is fixed only after every fee dispute submitted on that order's variable final value fee record carries a decision."
   - Connective: "only after".
   - Waited-on state: dispute status ≠ submitted.
   - The only write of this difficulty that moves a dispute out of `submitted` is dd's tool. No reject tool exists, and base says "a rejected dispute books nothing", so a reader works out from base `selling_fee_disputes` whether the dispute is upheld. In every world where the dispute is upheld, the hop resolves to dd uniquely. Where the records show it must be rejected, no write of this difficulty can record the rejection. That is latent and not exercised (observation O-7).
4. et←rc: "The early termination fee is not billed until every seller-funded refund debited to the seller's payments account in the last twelve months carries its refund credit on the order's variable final value fee record."
   - Connective: "not … until".
   - Resolving action: rc ("earns a refund credit").
   - Latent over-breadth against rc's cancelled-order exclusion (O-3).

Further checks:
- The depended-on rules (kc, cx, dd, rc) do not restate the sentences, and no rule names another problem's tool or id.
- No extended rule states a cross-problem order that grounds no declared edge.
- Base rules contain one cross-problem order ("A plan that is restricted cannot change plans until the restriction is lifted", `selling_plan_change_rules`). It grounds no edge of either task, because neither plan is restricted (observation).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (finding half only; consequences are in the task files):

- dd ← `selling_fee_disputes`:
  - Window sentence: followed.
  - Limit sentence: followed.
  - "upheld only when … standing discount not applied although the standing level and handling time qualified": followed (dd decides the credit only "when the dispute is upheld").
  - "An upheld dispute credits the overcharged difference with no administration fee": declared, replaced.
  - "a rejected dispute books nothing": followed.
- dd ← `selling_final_value_fees`:
  - The discount clause ("…reduced by the discount rate") is declared superseded, but its `replaced_by` speaks only of the dispute rate. The billing-time discount and the dispute ground's "standing level and handling time qualified" lose their definition.
  - dd's level rate reads the current level (`CFIELD standing variant_name`), not "the standing level on the order date".
  - Both readings agree whenever the level did not change between order date and decision (observation O-2).
- dd ← `selling_refund_fee_credit`: the never-exceed sentence is not breached on a record with no earlier credit. dd does not net prior credits, so a dispute decided after another credit on the same record could exceed the billed fee (latent, observation).
- tc ← `selling_plan_change_rules`:
  - "A move to a lower plan, or from the annual to the monthly term, takes effect at the plan's downgrade effective point": declared.
  - Annual-term lock: applies to "a lower plan" only, so the same-plan term move is not hit.
  - Store-name, minimum-sales and restricted sentences: followed.
- tc ← `selling_cancellation`: no overwrite entry. tc's fee is "billed on the move as an early end of the annual term", and base prices an early end of the term (share × remaining committed monthly fees, when "the plan closes"). tc's rule defines the term change fee itself, and the base clause is conditioned on closing the plan, so the merged reading stays unique (observation O-8).
- kc ← `selling_refund_fee_credit`: the whole first clause ("When the seller refunds … capped at the admin fee cap") is declared superseded. The rest of that sentence, "the per-order fee is credited too when the whole order has been refunded", is not superseded and speaks of a refund, not a chargeback. The surcharge-never-credited and never-exceed sentences are followed.
- cx ← `selling_refund_fee_credit`: "A refund on an order cancelled before shipment is credited in full with no administration fee" is declared superseded. `replaced_by` describes only the administration fee. The late-cancellation share also departs from "in full", but it rests on the same declared sentence (observation: the replaced_by text under-describes the replacement).
- et ← `selling_cancellation`: the ETF sentence is declared superseded. `replaced_by` describes only the share reliefs, and the renewal-grace month reduction rests on the same declared sentence (same observation). Also against `selling_onboarding` and `selling_fee_collection`: no conflict.
- **rc ← `selling_refund_fee_credit`: UNDECLARED OVERRIDE (finding F-1).**
  - rc's `overwrite` names only "less a refund administration fee of the admin rate times that credit, capped at the admin fee cap". The preceding base words of the same sentence, "the variable final value fee of that order is credited in proportion to the refunded share of the fee basis", stay in force.
  - rc's factor `refunded_share_rule` handles exactly that quantity differently. Its rule says "the refunded share is counted as one when the refunds reach at least the whole-order refund share of the fee basis, as half of the proportional share when they are no more than the small-refund share", and compute has `rc_share: 1 if rc_raw_share >= 0.9 else (rc_raw_share*0.5 if rc_raw_share <= 0.25 else rc_raw_share)`.
  - For any refund ≤ 25% or ≥ 90% of the fee basis, the base clause and the extended clause give different gross credits for the same refund. No `overwrite` entry names the base clause. This is an anonymous intermediate factor.
- kc / cx / rc ← `selling_fee_disputes` and `selling_final_value_fees`: no sentence of either is handled differently.

### factor_ladders

Per policy: factor, label, decides, tiers, multi-source, cross_difficulty, label honesty. Bindings are pairwise disjoint within each policy, and no `decides` is `result`.

| policy | factor | label | tiers (values) | multi-source | cross_diff | label honest? |
| --- | --- | --- | --- | --- | --- | --- |
| dd | level_discount_rate | parameter | 0.15 / 0.12 / 0.10 | tier 2 only (level × FBN shipment); tier 1 single-condition | standing | yes |
| dd | volume_window | method | 6 / 3 / 1 months | no (one enrollment row) | fulfill | accepted (borderline: changes which fee records enter the measured basis) |
| dd | volume_bonus | parameter | 0.03 / 0.02 / 0 | no | — | yes |
| dd | handling_bonus | parameter | 0.01 / 0.005 / 0 | no | fulfill | yes |
| dd | tenure_bonus | parameter | 0.02 / 0.01 / 0 | no | — | yes |
| dd | defect_adjustment | method | ×0.5 / ×0.75 / ×1 | no | standing | **no: a number multiplied into the same `RND(billed*rate*mult,2)`** |
| tc | repaid_charge_lookback | method | MN(n,3) / MN(n,6) / n | no | — | accepted (switches between a fixed count and the counted charges) |
| tc | volume_relief | parameter | 0.30 / 0.15 / 0 | no | — | yes |
| tc | standing_relief | parameter | 0.20 / 0.10 / 0 | level and points of one standing row | standing | yes |
| tc | payout_plan_relief | parameter | 0.10 / 0.05 / 0 | plan and balance of one payout row | payout | yes |
| tc | fbn_stock_multiplier | method | ×0.5 / ×0.8 / ×1 | no | fulfill | **no: a number in `RND(gap*repaid*share*fbn,2)`** |
| kc | chargeback_share_rule | method | 1 / ratio×0.5 / ratio | no | — | yes (a constant vs a ratio) |
| kc | chargeback_admin_rate | parameter | 0.10 / 0.15 / 0.20 | **yes** (payout chargeback count × standing level, both non-fall-through tiers) | payout | yes |
| kc | chargeback_admin_cap | parameter | 10 / 7.5 / 5 | no | — | yes |
| kc | chargeback_timing_multiplier | method | ×1.5 / ×1.25 / ×1 | no | payout | **no: a number in `RND(gross*rate*t*ten,2)`** |
| kc | chargeback_tenure_multiplier | method | ×0.5 / ×0.75 / ×1 | no | — | **no: same** |
| kc | fbn_chargeback_relief | parameter | 3 / 1.5 / 0 | no | fulfill | yes |
| cx | late_cancellation_share | method | 0.5 / 0.75 / 1 | no | standing | **no: a number in `RND(cx_creditable*cx_share,2)`** |
| cx | cancellation_admin_rate | parameter | 0.05 / 0.10 / 0 | **yes** (standing defect count × standing record level) | standing | yes |
| cx | cancellation_admin_cap | parameter | 10 / 7.5 / 5 | no | — | yes |
| cx | prompt_refund_relief | parameter | 2 / 1 / 0 | no | payout | yes |
| et | renewal_grace_months | method | int(x·0.5) / int(x·0.75) / x | no | — | **no: the same `int(months × f)` with f ∈ {0.5, 0.75, 1}** |
| et | termination_volume_relief | parameter | 0.15 / 0.10 / 0 | no | — | yes |
| et | termination_standing_relief | parameter | 0.10 / 0.05 / 0 | level and points of one row | standing | yes |
| et | loyalty_relief | parameter | 0.10 / 0.05 / 0 | no | — | yes |
| rc | refunded_share_rule | method | 1 / ratio×0.5 / ratio | no | payout | yes |
| rc | refund_admin_rate | parameter | 0.10 / 0.15 / 0.20 | **yes** (standing level × standing_events defects) | standing | yes |
| rc | refund_admin_cap | parameter | 10 / 7.5 / 5 | no | — | yes |
| rc | refund_frequency_multiplier | method | ×1.5 / ×1.25 / ×1 | no | payout | **no** |
| rc | refund_tenure_multiplier | method | ×0.5 / ×0.75 / ×1 | no | — | **no** |
| rc | fbn_refund_relief | parameter | 3 / 1.5 / 0 | no | fulfill | yes |

- Every ladder has 3 pairwise-disjoint tiers, and the fall-through equals the factor's `baseline`.
- No two tiers of a ladder share a value or method. Every tier (condition and value) is stated in the rule and implemented in compute.
- Every `baseline.rule` sentence is a rule sentence, and its `params` are the ones it names.

Counts after striking the mislabelled factors (the skill counts "only rules that pass the tests above"):

| policy | declared (param / method) | surviving (param / method) | meets 4-6 total, ≥2 param, ≥1 method? |
| --- | --- | --- | --- |
| dd | 6 (4 / 2) | 5 (4 / 1, volume_window) | yes |
| tc | 5 (3 / 2) | 4 (3 / 1, lookback) | yes |
| kc | 6 (3 / 3) | 4 (3 / 1, share rule) | yes |
| **cx** | 4 (3 / 1) | **3 (3 / 0)** | **no** |
| **et** | 4 (3 / 1) | **3 (3 / 0)** | **no** |
| rc | 6 (3 / 3) | 4 (3 / 1, share rule) | yes |

Multi-source (strict reading: every non-fall-through tier is a conjunction over distinct records): kc.chargeback_admin_rate, cx.cancellation_admin_rate, rc.refund_admin_rate. So task 0 (via kc and cx) and task 1 (via rc) each carry at least one. Cross-difficulty: all six policies read standing, payout and/or fulfill rows.

Realism (each condition and outcome against what a marketplace actually weighs). Nothing below is demonstrable to the RED threshold, so all are recorded as observations:

- dd: the volume, handling and tenure bonuses and the defect halving are applied to a correction credit for a missed discount. Real practice credits the overcharge only. The charter, however, re-declares the credit as its own "discount dispute rate", so this is a world rule.
- tc: `payout_plan_relief` (the payout schedule tier lowers a selling-plan fee) and `fbn_stock_multiplier` ("holds some units" → ×0.8) are cross-program loyalty levers with weak real-world grounding.
- kc, rc: halving the proportional share for small chargebacks or refunds is unusual but publishable.

### findings

- **F-1 SOURCE-POLICY RED (undeclared override), bears on task 1.**
  - Symptom: base `selling_refund_fee_credit` "the variable final value fee of that order is credited in proportion to the refunded share of the fee basis" is still in force, while `selling_ext_refund_fee_credit` sizes the same credit on `rc_share` (half of the proportion at ≤ 25%, one at ≥ 90%).
  - Root cause: rc's `overwrite.superseded_clause` covers only the administration-fee clause of that sentence.
  - Evidence: extended yaml lines 616-653 (base), 2634-2641 (rc overwrite), 2679-2681 (rule ladder), 2742-2744 (compute).
  - Consequence: demonstrated in `1.md`.
- **F-2 SOURCE-FACTOR (structure), bears on task 0 (cx) and task 1 (et).**
  - Eight factors are labelled `method` while their tiers only substitute a number into one formula: dd.defect_adjustment, tc.fbn_stock_multiplier, kc.chargeback_timing_multiplier, kc.chargeback_tenure_multiplier, cx.late_cancellation_share, et.renewal_grace_months, rc.refund_frequency_multiplier, rc.refund_tenure_multiplier.
  - With these struck, cx and et each keep 3 factors and 0 `method`, below the bounds. Each task file records the per-task consequence.
- O-1 (observation): tool uuid8s `4fd06f6c` and `4fd1aef8` share a 3-hex prefix. Independent generation cannot be confirmed.
- O-2 (observation): dd supersedes the base billing-time discount clause and reads the current level instead of the level on the order date. The two readings coincide whenever the level is unchanged.
- O-3 (observation, latent): et's refund prerequisite covers every seller-funded refund debit, but rc refuses refund credits on orders cancelled before shipment, and `rc_order` does not skip them. Not exercised in task 1.
- O-4 (observation): "the last twelve whole months" in tc, et, kc and cx carries no explicit counting convention. A calendar-month reading (the 12 complete calendar months before the current month) is possible. Effects are quantified per task.
- O-5 (observation): kc's "chargeback that the seller is liable for" is not implemented in `kc_order` (a reversed chargeback would still be picked). No reversal is seeded.
- O-6 (observation): et's "whole calendar months from the next billing date to the term end date" counts 10 months for a term whose 12 monthly charges are September through the following August. A billing-month reading gives 11. Effect quantified in `1.md`.
- O-7 (observation): no write of this difficulty can record a rejected dispute, so kc←dd can be resolved only in worlds where the dispute is upheld.
- O-8 (observation): tc lists `selling_cancellation` in its base refs with no overwrite, while calling its fee "an early end of the annual term".

## closing_checklist

Written after both reveals (05:01Z). Everything above this heading was frozen at 04:59:02Z (sha256 45f0cf23…53eb) and is unchanged.

**The difficulty does not close.** Not all four relationships PASS.

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 (`0.md`) | PASS | PASS | **SOURCE-FACTOR RED** (cx at 3 factors / 0 method) | PASS |
| 1 (`1.md`) | **SOURCE-POLICY RED** (F-1, rc 129.10 vs 63.85) | PASS | **SOURCE-FACTOR RED** (et at 3 factors / 0 method) | second answer on step 13 via F-1 |

Checklist items:
- Audit files correspond one-to-one with the tasks (0.md, 1.md), with `_difficulty.md` alongside. No earlier revision exists. Every comparison section is present, but not every one carries PASS.
- Coverage and scopes: 6/6 extended policies are covered. Scopes {dd, kc, cx, tc} and {rc, et} are disjoint; both match `charter_scope` exactly. Task tools and GT are closed. uuid8 independence is unconfirmed (O-1, shared prefix `4fd`).
- Trees:
  - task 0 has 3 prerequisite problems and 3 value_input edges; task 1 has 1 and 1;
  - each root is an `owner=user` write;
  - no cycle, and the union graph dd→kc→tc←cx, rc→et is a DAG.
- Factors: every factor bears weight against an honest baseline, and every whole-baseline number is definite and ≠ gold. However, F-2 strikes eight mislabelled `method` factors, leaving cx and et below the bounds.
- Re-run of this difficulty's instantiation-stage gates on the final form: not applicable. The artifacts were not changed. The coordinator's snapshot `gates.r1.txt` stands for the audited hashes.

## revision_2

### charter_global_frozen (revision_2)

- Auditor: erl-task-policy-audit subagent (Claude Opus 5.5), the same auditor as round 1. Started 2026-10-11T06:46:50Z (system clock).
- Hashes re-verified by the auditor against `HASHES.txt` (round 2):
  - `selling.extended.yaml` ff62c037aa10e472c032967e66cea0252ce61babd7bb9a43bdc0bb3c5305ecf0 (round 1: 58bbf1cf…, **changed**)
  - `task_tools.py` 686b50dff29a8c8901f2387af260f9f8b9e10c3ef5053a8e057cc2a83ccad01e (round 1: 0613ba43…, **changed**)
  - `0.view.json` bd8a39de… and `1.view.json` a6c8cda6…, **identical to round 1**, so frozen_time, user_scenario and initial_state are unchanged.
  - Source tasks: `0.json` e87baa50…f208, `1.json` ccc59874…a60e (both changed in masked fields).
- Because the charter and the tool module both changed, every charter-global section is re-derived in full below. The round-1 text above is left untouched.
- Gate snapshot `gates.r2.txt`: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, all rc=0. Entry conditions met.
- Base copy: lines 1-790 are still byte-identical to `blueprint/products/selling.yaml` (trailing blank line only).
- Masked and unread at the time of writing: every masked field of the round-2 task files.
- Contamination disclosure: the auditor saw round-1 GT during round 1. Values that the rework did not move (dd 4.48, kc 51.52/2.80/48.72, tc 43.20, rc 63.85) are therefore not blind in this round. Values the rework moved (cx, et) are derived here from the round-2 charter before any round-2 GT is read.

### policy_conflict_scan (revision_2)

- Changes found:
  - **dd**:
    - The level is read at the disputed fee's date: the latest evaluation if it is dated ≤ the fee date, else the standard rate.
    - A cap is added: "never more than the variable fee billed … less the credits already booked".
    - `defect_adjustment` is relabelled `parameter`.
  - **tc**:
    - The net-fee window is stated ("less than twelve whole months before the decision date").
    - "as an early end of the annual term" is dropped.
    - `fbn_stock_multiplier` is relabelled `parameter`.
  - **kc**:
    - The chargeback-count window is stated explicitly.
    - The timing and tenure multipliers are relabelled `parameter`.
  - **cx**:
    - The overwrite is split into two declared fragments of base sentence 2.
    - `late_cancellation_share` is relabelled `parameter`.
    - `prompt_refund_relief` is removed.
    - A new `method` factor, `cancellation_record_window` (tenure → 12 / 9 / 6-month count window), is added.
  - **et**:
    - The prerequisite sentence is narrowed to refunds "for an order that shipped".
    - The baseline months are now the billing dates still to come (MONTHS + 1).
    - `renewal_grace_months` is replaced by `renewal_month_rule` (renewed ≤ 30 days → max(0, 3 − months elapsed); term ends within renewal notice days → 0; otherwise remaining).
    - The long loyalty relief is now 0.08.
    - The overwrite is split into two declared fragments.
    - The tool is renamed `end_store_term_early_0def8036`.
  - **rc**:
    - A second overwrite entry declares the proportional-share clause.
    - The multipliers are relabelled `parameter`.
- Scopes: unchanged and disjoint, task 0 = {tc, kc, cx, dd}, task 1 = {et, rc}.
- The round-1 latent conflict O-3 is closed. The et gate now covers only refunds "for an order that shipped", and rc refuses refund credits only for orders cancelled before shipment, so the two no longer collide.
- No new conflict between policies is found.

### rule_compute_equivalence (revision_2)

- dd:
  - `dd_level: CFIELD(standing variant_name) if CFIELD(standing last_evaluation_date) <= dd_fee_date else 'no level on record'` matches the new level sentence. The non-level value falls to `P('top_rated_fvf_discount_rate')`, as the rule says.
  - `result: MN(dd_raw, MX(0, dd_billed - dd_prior))` with `dd_prior` = Σ gross credits on the record matches the new cap sentence.
- tc / kc: `within_months=12` matches the now-explicit "less than twelve whole months before the decision date".
- cx:
  - `cx_tenure` → `cx_window` (24 → 12 months, 12 → 9 months, else 6) matches the rule. `cx_cancels` with `within_months=cx_window` matches "dated less than that many whole months before the decision date".
  - `cx_admin: MN(RND(cx_gross*cx_rate,2), cx_cap)` matches "held to the cap". The relief is gone from both rule and compute.
- et:
  - `et_months_left: MONTHS(next_billing, term_end) + 1` matches "plus one for the next billing date itself".
  - `et_to_end: DAYS(NOW, term_end)` against `P('renewal_notice_days')` matches tier 2.
  - Tier 1 `MX(0, 3 − MONTHS(term_start, next_billing))` matches.
  - The renewed test is still whole months > 0 vs the rule's "start date later than the verification date". The round-1 note stands; no consequence.
- rc: compute is unchanged and matches the rule.
- Both ways: no tier lives only in compute, and no rule ladder is missing from compute.

### action_binding_and_uuids (revision_2)

- `(target_tool, computes)` is still claimed once each. et's target_tool is now `end_store_term_early_0def8036` (owner user).
- uuid8s: 4fd06f6c, 32d8a153, 79bf63bc, ae40bf8f, a1b0f084, 0def8036. No pair shares a 3-hex prefix and no sequence is visible. **O-1 closed.**
- Docstrings: an ordering-word scan of `task_tools.py` finds only "the credit before (any) the administration fee" (an amount description). No tool names another tool.
- Bodies: switch and end-term now record `remaining_term_months = whole_months(next_billing, term_end) + 1`, consistent with the new baseline months. No body judges eligibility or a prerequisite (lines 58-70, 107-120, 157-170, 196-210, 247-260, 285-298).

### prerequisite_graph (revision_2)

- The graph is unchanged: tc←kc, tc←cx, kc←dd, et←rc. All four edges are value_input and form state. Gates `tc_net_fees`, `kc_prior` and `et_net_fees` exist, `resolved_by` is each problem's target tool, and the graph is acyclic.
- et←rc:
  - `policy_source` is now "The early termination fee is not billed until every seller-funded refund debited to the seller's payments account in the last twelve months for an order that shipped carries its refund credit on the order's variable final value fee record." It is verbatim in et's rule.
  - `condition` adds "on an order that shipped", matching the sentence, at the same strength.

### prerequisite_sentences (revision_2)

- tc and kc sentences are unchanged, so the round-1 four-point results carry over.
- et sentence: connective "not … until"; record-visible state (a refund credit on the variable record for refund debits on shipped orders); no tool or id; scope matches the condition. The hop resolves uniquely to rc ("earns a refund credit"). rc's own exclusion of cancelled-before-shipment orders now lies outside the gate's scope.
- No new cross-problem order appears in any rule.

### override_declarations (revision_2)

- **rc: F-1 closed.** A second `overwrite` entry names "the variable final value fee of that order is credited in proportion to the refunded share of the fee basis" and replaces it with the share ladder. The admin-fee clause stays declared. What remains of the base sentence is the refund-window clause and "the per-order fee is credited too when the whole order has been refunded". The ladder is variable-fee-only ("For the variable fee credit"), so the two do not collide. The merged semantics are unique.
- cx: both fragments of base sentence 2 ("A refund on an order cancelled before shipment is credited in full" / "with no administration fee.") are declared. Each `replaced_by` now states what it puts in their place (the late share, and the admin fee over the record window). The round-1 under-description observation is closed.
- et: the base ETF sentence is declared in two fragments, with replacements for the share reliefs and the renewal month rule. The round-1 under-description observation is closed.
- dd:
  - The billing-time discount clause of `selling_final_value_fees` is still superseded by a dispute-rate sentence (unchanged).
  - The level is now read at the fee's date, which coincides with the order date (fee event_date = capture date), so the base "level on the order date" and the extended reading agree by construction. **O-2 closed.**
  - The dd cap closes the round-1 latent never-exceed gap.
- tc: `selling_cancellation` is still in base refs with no overwrite. The early-end wording is gone from the rule and the replaced_by. **O-8 closed.**
- kc: unchanged; the round-1 conclusions stand.

### factor_ladders (revision_2)

| policy | factors (param / method) | method factor(s) and honesty | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| dd | 6 (5 / 1) | volume_window (accepted, borderline as in round 1) | — | standing, fulfill |
| tc | 5 (4 / 1) | repaid_charge_lookback (accepted) | — | standing, payout, fulfill |
| kc | 6 (5 / 1) | chargeback_share_rule (honest) | chargeback_admin_rate | payout, fulfill |
| cx | 4 (3 / 1) | cancellation_record_window (accepted by the same standard as dd's volume_window: the tier sets which defect records enter the count, 12 / 9 / 6 months) | cancellation_admin_rate | standing |
| et | 4 (3 / 1) | renewal_month_rule (honest: three different algorithms, namely a fixed commitment less elapsed months, zero, or the remaining billing dates) | — | standing |
| rc | 6 (5 / 1) | refunded_share_rule (honest) | refund_admin_rate | payout, standing, fulfill |

- All former multiplier "methods" are now labelled `parameter` and select a number, so their labels are honest. **F-2 closed** for every policy: all six meet 4-6 factors, ≥ 2 `parameter` and ≥ 1 `method`.
- Every ladder still has 3 disjoint tiers with distinct outcomes, its fall-through equals the factor `baseline`, and every tier is stated in the rule and implemented in compute.
- New ladders checked for realism:
  - cx record window: a tenure-scaled lookback for repeat cancellations has precedent in marketplace seller-performance windows that vary by seller profile.
  - et renewal month rule: a short commitment after an auto-renewal, and no committed months when the term is about to end, are publishable subscription terms.
  - No condition holds of every customer reaching the write.
- `baseline.rule`:
  - et's baseline now states the remaining committed months as billing dates still to come (MONTHS + 1), consistent with `et_months_left`.
  - cx's baseline is unchanged ("credited in full, with no administration fee withheld").

### findings (revision_2)

- F-1: **closed** (see `override_declarations`).
- F-2: **closed** (relabelled; cx and et each gained an honest `method`).
- O-1, O-2, O-3, O-6, O-8: **closed**.
- O-4: closed for the net-fee, chargeback-count and cancellation windows, which now state "less than N whole months before the decision date". rc's "within the last three whole months" still has no explicit counting phrase (the rate sentence of the same rule does have one). This is a residual minor observation; its effect in task 1 is quantified in `1.md`.
- O-5 (kc does not exclude reversed chargebacks) and O-7 (no rejection write): answered without change. Both remain observations, with no consequence on either world.
- Residual observation: `rc_order` still takes the latest refund debit without skipping orders cancelled before shipment. The rule excludes them, and the et gate no longer depends on them. There is no consequence in either world.
- New charter-global defects: none found.

### closing_checklist (revision_2)

Written after the round-2 reveals at 06:49:46Z. The revision_2 charter-global sections above were frozen at 06:49:08Z, before any round-2 GT was read.

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- Audit files correspond one-to-one with the tasks, `_difficulty.md` sits alongside them, and the round-1 text is untouched with revision_2 appended. Every revision_2 comparison carries PASS.
- Coverage: 6/6 extended policies are covered. Scopes {dd, kc, cx, tc} and {rc, et} are disjoint and equal `charter_scope`. Tools and GT are closed. The uuid8s are distinct with no shared prefix (O-1 closed).
- Trees:
  - task 0 has 3 prerequisite problems and 3 value_input edges; task 1 has 1 and 1;
  - each root is the customer's own `owner=user` write;
  - the union graph is a DAG.
- Factors: every computation has 4-6 factors with ≥ 2 `parameter` and 1 honest `method`. Every task has a multi-source factor and a cross-difficulty factor with seeded rows. Every factor bears weight against an honest baseline, and every whole baseline is definite and ≠ gold.
- Gate re-run on the final form: the coordinator's `gates.r2.txt` (all 8 gates rc=0) covers the audited hashes (extended ff62c037…, tools 686b50df…). The auditor did not re-run gates; that is coordinator-owned.
- **The difficulty passes the source-layer audit at revision_2.**
- Open observations, none blocking:
  - O-4 residual (rc 3-month window wording);
  - O-5;
  - O-7;
  - the residual `rc_order` note;
  - 1-O-r2 (half-cent ties in unscored proof figures);
  - the payments-mirror gap noted by the author.

## revision_3

### charter_global_frozen (revision_3)

- Auditor: erl-task-policy-audit subagent (Claude Opus 5.5), the same auditor as rounds 1-2. Started 2026-10-11T08:50:33Z; this section written at 2026-10-11T08:51:16Z (system clock).
- Hashes re-verified against `HASHES.txt` (round 3):
  - extended yaml b67d1f2b6f1d17572d608a7b7ec50b6d2562a42283f5b380a17a8802651ec6b0 (round 2: ff62c037…, **changed**);
  - `task_tools.py` 686b50df… (**unchanged** since round 2);
  - views bd8a39de… and a6c8cda6… (**unchanged**: same worlds);
  - `tasks/0.json` 1f41dc6d…, `tasks/1.json` 7f4a7954… (masked fields changed).
- `gates.r3.txt`: 9/9 rc=0 (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, CACHE-DIFF info, SCOPE, TRACEABILITY).
- Base copy lines 1-790 are still verbatim.
- Contamination disclosure: every scored value of both tasks is known to the auditor from rounds 1-2, so this round re-derives only what the changed charter can move.
- Change inventory, re-derived because the charter hash changed:
  - Base copy verified.
  - Params, prerequisite edges, `overwrite` entries and factor labels of all six policies were re-read and match revision_2.
  - The rule text changes are confined to the two items below; the file grew by 2 lines.
  - **et**: `et_renewed: DAYS(F('verified_date'), F('term_start_date'))`, still tested `> 0`, now equals the rule's "a term whose start date is later than the plan's verification date". This closes the round-1/2 rule_compute_equivalence note: whole months > 0 vs date later.
  - **rc**: the frequency window is now worded "seller-funded refund debits dated less than three whole months before the decision date". It appears in the rule (line 2743), both `compute_basis` quotations (`rc_refunds_3m`, `rc_freq_mult`) and the ladder tier. That equals `XCOUNT(…, within_months=3, …)` (unchanged). **The O-4 remainder is closed.**

### re-checked sections (revision_3)

- policy_conflict_scan, action_binding_and_uuids, prerequisite_graph, prerequisite_sentences, override_declarations, factor_ladders: re-read, unchanged from revision_2, so the revision_2 conclusions carry forward.
  - The tool module hash is unchanged.
  - The et and rc factor ladders keep their tiers, labels and baselines. Only the quoted wording of rc's frequency tier and et's renewed definition moved, and each now matches compute exactly.
- rule_compute_equivalence: both directions hold for the two changed bindings. No other binding changed.
- Findings (revision_3): no new charter-global defect. Remaining observations: O-5, O-7, the residual `rc_order` note, 1-O-r2 (unscored half-cent ties), and the payments-mirror gap.

### closing_checklist (revision_3)

Written after the round-3 reveals at 08:51:20Z.

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- Files map one-to-one to the tasks, and earlier revisions are untouched with revision_3 appended.
- Coverage, scopes and uuid8s are unchanged from revision_2 and closed.
- Trees: 3 prerequisite problems / 3 value_input edges (task 0) and 1 / 1 (task 1), each with a user-owned root. The union graph is a DAG.
- Factors: 4-6 per computation, each with ≥ 2 `parameter` and an honest `method`, all bearing weight against an honest baseline that differs from gold.
- Gates on the final form: `gates.r3.txt` 9/9 rc=0, including TRACEABILITY, for extended b67d1f2b… and tools 686b50df….
- **The difficulty passes the source-layer audit at revision_3.**
- Non-blocking observations: O-5, O-7, the residual `rc_order` note, 1-O-r2 (unscored half-cent ties), and the payments-mirror gap.
