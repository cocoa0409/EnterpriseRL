# Policy-task audit — placed_account_servicing / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit (independent agent; did not author these artifacts). Revision 1.
- Freeze time: 2026-10-09T09:12Z. Written before any task's GT was revealed; this section contains nothing taken from a revealed GT.
- Frozen inputs (sha256, re-computed by the auditor, equal to the brief):
  - `tasks/placed_account_servicing/account.extended.yaml` = `8a922f5aa311545d44332e40de3fda89933a83bb0125dbeb40a3415cdb7f39a2`
  - `tasks/placed_account_servicing/task_tools.py` = `74b1ec23ffb1ebce74f69663dfa1d0fcbf53f987156e92dbb6ef1da56658d457`
  - masked views `/tmp/env0050_views/placed_account_servicing/r1/0.view.json` = `a2c92e79…fe086`, `1.view.json` = `a7e33913…8e9e2` (both re-hashed and matching).
- Read: `blueprint/blueprint.yaml` (difficulty summary), `blueprint/products/account.yaml`, `blueprint/products/plan.yaml` (installment/down-payment field meanings and measures only), `blueprint/db_schema.json` (field meanings), `blueprint/share_tools.py`, the extended charter, `task_tools.py`, the two masked views, and the gate DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (to know the semantics of `MONTHS`, `DAYS`, `CFIELD`, `XLATEST`, `RND`).
- Masked / not read: `tasks/placed_account_servicing/tasks/{0,1}.json` (all of `evaluation_criteria`, `computations`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `charter_scope`, `required_documents`, closure fields), `tasks/placed_account_servicing/worklog.md`, the scenario `worklog.md`, any other `env/` scenario, any sibling difficulty's tasks directory. No recursive grep was run over the scenario or the difficulty directory.
- Entry conditions (Step 0): gate snapshot supplied in the brief and all green (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; traceability deferred because the KB is not published). Masked views supplied with hashes. Entry conditions satisfied.

### policy_conflict_scan

Base section: parsed `account.extended.yaml` minus `extended_policies` equals `blueprint/products/account.yaml` key for key, and a textual diff of lines 1–1759 against the blueprint file differs only by one trailing blank line. The base copy is verbatim.

Extended policies (all `trigger: on_request`, all `subject: [account_payment_posted]`, all `computes: amount`):

| policy | target tool (owner) | channel / desk | prerequisite |
| --- | --- | --- | --- |
| `account_ext_phone_debit_card_ceiling` | `take_debit_card_payment_cc21c0ad` (agent) | debit card, phone | `[]` |
| `account_ext_phone_credit_card_ceiling` | `take_credit_card_payment_bec5ec25` (agent) | credit card, phone | phone debit (value_input, action) |
| `account_ext_portal_bank_debit_ceiling` | `make_portal_bank_payment_436b09cd` (user) | bank debit, portal | phone credit (value_input, action) |
| `account_ext_portal_debit_card_ceiling` | `make_portal_debit_card_payment_fc4d38a9` (user) | debit card, portal | `[]` |
| `account_ext_portal_credit_card_ceiling` | `make_portal_credit_card_payment_7a2662c6` (user) | credit card, portal | portal debit (value_input, action) |
| `account_ext_reporting_floor_paydown` | `take_phone_bank_payment_d463b192` (agent) | bank debit, phone | portal credit (value_input, action) |

Overlap scan:
- Subjects overlap on `account_payment_posted` for all six, but each is partitioned by channel × desk (phone vs portal) and by request kind ("pay the most an account will accept in one day" for the four ceilings, "paying an account down in one day … by … the payment portal" for the two portal cards, "bring a placed account's balance below the credit-reporting minimum and authorizes the phone desk to debit their bank account" for the pay-down). No two policies bind the same tool, so for one channel × desk × request there is at most one applicable extended policy.
- Phone debit vs portal debit, phone credit vs portal credit, portal bank vs phone bank: same ledger effect (a `debit_card` / `credit_card` / `ach_bank_debit` row dated today), distinguished only by who performs it (agent at the phone desk vs consumer on the portal). Which applies is fixed by the consumer's stated choice of desk; no overlapping conclusion.
- Eligibility, status gates, minimum payment, returned-payment block: none of the six restates or modifies them; they are inherited from `account_evt_payment_channels` (see override_declarations).
- Time anchors: every window is "fewer than N whole calendar months, a whole month reached on the same day of a later month" (DSL `MONTHS`); "on the handling date" = `txn_date = NOW`. Consistent across policies.
- Cross-category read boundaries: plan (phone debit, phone credit, portal bank), hardship (phone credit, portal debit, portal credit, pay-down). Each declared in `cross_category` and read through `CFIELD`/`XCOUNT`/`XLATEST` only.
- Scope partition (derived from the charter alone, before reveal): the prerequisite graph has exactly two weakly connected components, {phone debit → phone credit → portal bank} and {portal debit → portal credit → reporting-floor pay-down}. With M = 2, the only partition that is disjoint and jointly complete is one component per task. The worlds and personas agree (task 0: debit + credit by phone, checking on the portal; task 1: both cards on the portal, checking by phone). Confirmation against `charter_scope` is deferred to each task's reveal.

### rule_compute_equivalence

Mechanical part: every `compute_basis` value of all six policies is a verbatim substring of its own `rule` (whitespace-normalised; checked by script, 0 misses). Every `baseline.rule` sentence is a sentence of the `rule` (all True). Every `overwrite.replaced_by` is a sentence of the `rule` (all True).

Sentence-by-sentence sweep (rule → compute and back), per policy:

- Balance due (all six): "placed balance plus supplemental additions, returned payments and refunded overpayments, less consumer payments, direct payments, client credits and settlement waivers" ↔ `*_placed_in + *_supp_in + *_ret_in + *_ref_in - *_pay_out - *_direct_out - *_credit_out - *_waive_out`. Equal, and equal to the base `accounts.balance_due` meaning.
- Windows: "fewer than N whole calendar months … a whole month being reached on the same day of a later month" ↔ `_within`: `0 <= MONTHS(d, NOW) < N`, with `MONTHS` subtracting one when the day-of-month has not been reached. Equal.
- Final selection (all six): "the smallest of the rounded figure, the stage's … and the balance due, and it is never below zero" ↔ `RND(MX(0, MN(figure, P(cap), balance)), 2)`. Equal.
- Phone debit: rolling limit (3 tiers by returns in 6 months), plan-standing % (broken date × missed count), counted debit window (by stage), track allowance (count × card returns ever), "multiplied … added … subtracted; rounded once" ↔ `ceiling_figure = RND(rolling_limit * plan_standing_pct + track_allowance - debit_counted, 2)`. Equal except finding F2 (any-plan vs first-plan) and F4 (rounding).
- Phone credit: card limit (debt type × charge-off age; "or that has no charge-off date" ↔ `F('charge_off_date') or NOW` → age 0), cancellation % (close reason × closed-date recency), counted cards (returns × card payments in last month; three tiers), hardship cushion (tier × ended within 6 months; no ended date ↔ `'1900-01-01'` → no cushion), "multiplied … subtracted … subtracted; rounded once after both subtractions" ↔ `RND(card_limit * cancel_pct - credit_counted - hardship_cushion, 2)`. Equal except F2.
- Portal bank: limit (return reasons in 6 months), same-day counting (plan close reason; returns), retest % (latest bank return vs latest bank payment, "on or after" ↔ `>=`), installment allowance (paid minus returned plan installments), "subtracted … multiplied … added; rounded once" ↔ `RND((bank_limit - same_day_counted) * retest_pct + installment_allowance, 2)`. Equal except F2.
- Portal debit: limit (returns in 6 months), assistance % (FA Review Hold × denied × ended recency), counted window (debt type), clean-record allowance, "multiplied … subtracted … added" ↔ `RND(portal_debit_limit * assistance_pct - pd_counted + clean_allowance, 2)`. Two divergences: F1 (a denied FA hold with no ended date) and F2 (first hold / any hold's decision).
- Portal credit: limit ("charge-off or final-bill date" ↔ `charge_off_date`, whose schema meaning is "charge-off or final-bill date reported by the client"), assistance % (latest decision on the account's holds ↔ `XLATEST(... account_id=HID)`), counted cards, appeal cushion (rebill in 6 months × insurance credit ever), dispute % (billing/other dispute × verification, both in 6 months), steady-use allowance, "multiplied … then by … ; … subtracted …; … added" ↔ `RND(limit * assist * dispute - counted - cushion + steady, 2)`. Equal except F4.
- Pay-down: reporting floor (debt type × first-delinquency age), margin (latest decision × returns), provisional add-back (returns × bank payments in 2 months), card cushion (credit payment today × card chargeback ever), "reportable balance = balance + add-back; floor subtracted; margin and cushion added; rounded once" ↔ `RND(f_balance_now + provisional_addback - reporting_floor + paydown_margin + card_cushion, 2)`. Equal except F4.

Every `factors[].ladder` tier is a clause of the `rule` and a branch of the `decides` binding, and every branch of each `decides` binding is a tier the rule states, with the exception recorded in F1.

### action_binding_and_uuids

- `(target_tool, computes)`: six distinct pairs, each claimed by exactly one policy; no base policy claims a task tool.
- Docstrings: each describes one atomic booking (one charge/debit, one `account_payment_posted` row dated today, balance reduced by the amount). None names another tool, none states a position in a sequence. The two agent-owned card tools and the phone bank tool contain "The consumer can afterwards quote the confirmation number" — "afterwards" refers to the consumer's later use of the receipt, not to an order between tools (observation O5, no consequence). No docstring adds a confirmation, review or wait.
- Function bodies: each body does `find` → `round(amount, 2)` → `create` ledger row → `update` balance; no branch tests eligibility, a limit, a prior payment or a prerequisite; an unknown account only yields `balance_due_after = None`. The tool layer judges no prerequisite.
- uuid8s: `cc21c0ad`, `bec5ec25`, `436b09cd`, `fc4d38a9`, `7a2662c6`, `d463b192`. All distinct, no shared prefix or suffix, no sequential or adjacent pattern, none reused with a different tail. No sign of batch derivation.

### prerequisite_graph

- `prerequisite` present on all six (two `[]`).
- Edges: phone credit → phone debit; portal bank → phone credit; portal credit → portal debit; pay-down → portal credit. Every `problem` is an extended policy id in this file, none is a base policy, none is self. The graph is two disjoint chains of three, acyclic.
- `policy_source`: each of the four is a verbatim sentence of the blocked policy's own `rule` (script check: all True).
- `form: action` on all four, each with a `fallback_reason`; no state-form edge exists.
- `kind: value_input` on all four; `gate` names a real binding of the blocked compute: `credit_counted` (phone credit), `same_day_counted` (portal bank), `portal_credit_counted` (portal credit), `card_cushion` (pay-down). Each named binding reads today's ledger rows of the depended-on channel, so the resolving write does change its value (checked per world in the task files).
- `resolved_by` equals the depended-on policy's `target_tool` in all four.
- `condition` restates the action-form sentence as the ledger row the write leaves (channel, date, desk, "at the … ceiling of the day"). It neither strengthens nor weakens the sentence.
- `effect` texts match what the compute does: the depended-on payment enters the counted set or the cushion test and lowers the balance due.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") in any `prerequisite` field.

### prerequisite_sentences

Four-point test, per edge:

1. Phone credit ← phone debit: "When a consumer who also offers a debit card asks to pay the most an account will accept in one day, the credit-card ceiling of the day is fixed only after the day's debit-card payment has been taken by the phone desk." Ordering connective "only after". Action form in business words ("debit-card payment … taken by the phone desk"). No tool, policy id, snake_case or row id. Strength matches the condition: same desk, same day, the debit payment of a "pay the most" request. PASS.
2. Portal bank ← phone credit: "When a consumer who also offers a credit card asks to pay the most an account will accept in one day, the portal bank-debit ceiling of the day is not fixed until the day's credit-card payment has been taken by the phone desk." Connective "not … until". Action form. Clean. PASS.
3. Portal credit ← portal debit: "When a consumer who also pays by debit card through the payment portal is paying an account down in one day, the portal credit-card ceiling of the day is fixed only after the day's portal debit-card payment has been made." PASS.
4. Pay-down ← portal credit: "Where the consumer also pays part of it by credit card through the payment portal, the reporting-floor pay-down is not fixed until the day's portal credit-card payment has been made." PASS.

Fallback test: in each case the waited-on write leaves a row (`event_type=account_payment_posted`, `payment_channel` ∈ {`debit_card`, `credit_card`}, `txn_date` = today). The sibling tool for the other desk books the same row, and the two differ only in the generated `payment_ref` prefix (`pdc_`/`wdc_`, `pcc_`/`wcc_`), which is not a business state any finder exposes as such. No record-visible state would single out the one write, so all four fallbacks are justified.

Derivation (sentence + records + depended-on rule → resolving action), single reading each:
- (1) "the day's debit-card payment … taken by the phone desk" → the only rule whose result is a phone-desk debit-card payment is the phone debit-card ceiling ("the phone desk takes one debit-card payment equal to the debit-card ceiling of the day").
- (2) "the day's credit-card payment … taken by the phone desk" → only the phone credit-card ceiling rule.
- (3) "the day's portal debit-card payment" → only the portal debit-card ceiling rule.
- (4) "the day's portal credit-card payment" → only the portal credit-card ceiling rule.

Each depended-on rule is silent about the dependent: the phone debit rule never mentions credit, the phone credit rule never mentions the portal, the portal debit rule never mentions credit, and the portal credit rule never mentions the pay-down. No rule carries a second wording of an edge, a tool name or a policy id.

Undeclared orders: a sweep of every extended rule for ordering connectives (before, after, until, only once, first, prior to) finds only the four declared sentences. Two value reads cross a non-adjacent node: the portal bank same-day tier 1 counts today's debit-card payments, and the pay-down's "every payment of the handling date included" counts the portal debit. Both are covered transitively by the declared chain, and neither rule states an order of its own. No base rule sentence grounds an edge.

### override_declarations

Every extended policy cites `account_agg_payment_application` and `account_evt_payment_channels`; the pay-down also cites `account_evt_credit_reporting`.

`account_evt_payment_channels`, sentence by sentence:
- S1 status gate (placed … hardship_hold; never solicit in dispute_hold, accept consumer-initiated): followed (not touched).
- S2 channels by stage (credit card only where `credit_card_payments_accepted`): followed; both credit policies restate the stage gate.
- S3 "A single card payment … may not exceed card_payment_max_per_transaction_usd, and account_msr_card_payments_30d plus the new card payment may not exceed card_payment_max_rolling_30d_usd": handled differently by all four card policies (per-transaction cap kept, rolling-30-day test replaced by each ceiling). Declared in each card policy's `overwrite`, and the superseded clause is verbatim in base. The merged semantics are unique: each card payment is bounded by its own channel × desk ceiling.
- S3' "a single ACH payment may not exceed ach_payment_max_per_transaction_usd": handled differently by portal bank and pay-down (the per-transaction cap is kept inside the ceiling). Declared in both.
- S4 "Every payment must be at least min_payment_amount_usd unless it equals the full balance_due": not overridden, so it is inherited. A ceiling below the stage minimum means no payment. Checked per world.
- S5 posting date / payment_ref: followed by the tools.
- S6 return booking: not touched.
- S7 returned-payment block (threshold within lookback blocks ach/debit/credit until the block period passes): not overridden, so it is inherited. It bears on every tier that conditions on two or more returns in six months (phone debit and portal debit tier 1): at the threshold of 2, such an account is usually electronically blocked. Checked per world.

`account_agg_payment_application`: multi-account split and the exclusion of accounts with an unanswered dispute. The extended policies all act on one named account and do not alter the allocation. Followed, and checked per world (single account, disputes answered).

`account_evt_credit_reporting` (pay-down only): `reporting_min_balance_by_debt_type` (medical 500, auto/PSL 250, others 100) and the obsolescence bar ("after the obsolescence date only a deletion may be furnished"). The extended reporting floor follows the per-type minimum while the first delinquency is under `reportable_age_days` = 2737 days. For a debt at or beyond 2737 days it switches every type to `general_floor` 100. This conflicts with the base, which gives a medical or auto/PSL minimum of 500/250 regardless of age and treats a debt past obsolescence as not reportable at all. No `overwrite` entry names `account_evt_credit_reporting`. See F3.

Disguised forms: no anonymous intermediate factor, no 0/1 multiplier on a base-fixed quantity, no dropped base branch found. No author note calls the base output wrong.

### factor_ladders

| policy | factor | label | decides | tiers | multi-source | cross_difficulty | honest label? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| phone debit | debit_rolling_limit | parameter | rolling_limit | 1200 / 2400 / stage rolling | no | — | yes |
| phone debit | debit_plan_standing | parameter | plan_standing_pct | 0.75 / 0.90 / 1.00 | yes (plan broken date ∧ missed rows) | plan | yes |
| phone debit | debit_counting_window | method | debit_counted | debit sum last 3 / 2 / 1 months | no | — | **no**: F5 |
| phone debit | debit_track_record | parameter | track_allowance | 500 / 250 / 0 | yes (card count ∧ card returns) | — | yes |
| phone credit | credit_card_on_card_limit | parameter | card_limit | 4500 / 5500 / stage rolling | same-record fields | — | yes |
| phone credit | credit_plan_cancellation | parameter | cancel_pct | 0.80 / 0.90 / 1.00 | same-record fields | plan | yes |
| phone credit | credit_counting_basis | method | credit_counted | all cards 2m / all cards 1m / credit only 1m | yes (returns ∧ card payments) | — | yes (channel set changes) |
| phone credit | credit_hardship_cushion | parameter | hardship_cushion | 150 / 75 / 0 | same-record fields | hardship | yes |
| portal bank | bank_return_limit | parameter | bank_limit | 3000 / 5000 / stage ACH cap | yes (reason sets) | — | yes |
| portal bank | bank_same_day_basis | method | same_day_counted | all channels today / credit+bank today / bank today | tier 2 yes | plan | yes (channel set changes) |
| portal bank | bank_retest | parameter | retest_pct | 0.50 / 0.75 / 1.00 | yes (return ∧ payment dates) | — | yes |
| portal bank | bank_installment_record | parameter | installment_allowance | 200 / 100 / 0 | no | plan | yes |
| portal debit | portal_debit_return_limit | parameter | portal_debit_limit | 800 / 1600 / stage rolling | no | — | yes |
| portal debit | portal_debit_assistance | parameter | assistance_pct | 0.60 / 0.80 / 1.00 | yes (hold tier ∧ decision event ∧ ended date) | hardship | yes (see F1) |
| portal debit | portal_debit_window | method | pd_counted | debit sum last 3 / 2 / 1 months | no | — | **no**: F5 |
| portal debit | portal_debit_clean_record | parameter | clean_allowance | 200 / 100 / 0 | yes (debit returns ∧ debit count) | — | yes |
| portal credit | portal_credit_bill_limit | parameter | portal_credit_limit | 3000 / 4000 / stage rolling | same-record fields | — | yes |
| portal credit | portal_credit_assistance | parameter | credit_assistance_pct | 0.70 / 0.85 / 1.00 | no | hardship | yes |
| portal credit | portal_credit_counting_basis | method | portal_credit_counted | all cards 2m / cards today / credit 1m | yes | — | yes (channel set changes) |
| portal credit | portal_credit_appeal_cushion | parameter | appeal_cushion | 120 / 60 / 0 | yes (rebill ∧ insurance credit) | — | yes |
| portal credit | portal_credit_dispute_history | parameter | dispute_pct | 0.90 / 0.95 / 1.00 | yes (dispute ∧ verification) | — | yes |
| portal credit | portal_credit_steady_use | parameter | steady_allowance | 150 / 75 / 0 | yes | — | yes |
| pay-down | paydown_reporting_floor | parameter | reporting_floor | 500 / 250 / 100 | same-record fields | — | yes (see F3) |
| pay-down | paydown_margin_rule | parameter | paydown_margin | 25 / 10 / 0.01 | yes (decision ∧ returns) | hardship | yes |
| pay-down | paydown_provisional_addback | method | provisional_addback | bank sum 2m / bank sum 1m / nothing | yes | — | **no**: F5 |
| pay-down | paydown_card_cushion | parameter | card_cushion | 75 / 25 / 0 | yes (credit today ∧ chargeback) | — | yes |

Structural checks:
- Factor counts are 4, 4, 4, 4, 6, 4, all within 4–6. Every policy declares ≥2 `parameter` and exactly 1 `method`.
- Bindings are disjoint within each policy, and no `decides` is `result`.
- Every ladder has three pairwise-disjoint tiers, stated in full in the `rule` with condition and value or method, and implemented in `compute`. F1 is the one exception at the boundary.
- No two tiers of a ladder share a value or method. Stage-parameter fall-throughs never coincide with the fixed tiers: the stage rolling caps are 5000/10000/10000/7500/5000/20000 and the ACH caps 10000/25000/25000/25000/15000/50000.
- Every fall-through tier equals the policy's `baseline` for that input, and every factor's `baseline` binding is what `baseline.rule` states: stage cap, ×1, the one-month (or same-day) standard window, and 0 allowance or cushion. Each `baseline.rule` is self-sufficient: it yields a definite number from the records and stage parameters with no factor applied.
- Per component: the {phone debit, phone credit, portal bank} tasks carry cross-difficulty factors reading plan and hardship. The {portal debit, portal credit, pay-down} tasks carry cross-difficulty factors reading hardship. Each component has several multi-source factors.

Label honesty (finding F5): three of the six `method` factors change only a number inside the same aggregate, so they are `parameter` factors under a `method` label.
- `debit_counting_window` binds `debit_1m`/`debit_2m`/`debit_3m`, which are the identical expression `SUM('account_transactions','amount', within_months=N, date_field='txn_date', event_type='account_payment_posted', payment_channel='debit_card')` with N ∈ {1, 2, 3}.
- `portal_debit_window` binds `pd_debit_1m`/`pd_debit_2m`/`pd_debit_3m`, the same expression with N ∈ {1, 2, 3}.
- `paydown_provisional_addback` binds `bank_sum_2m`/`bank_sum_1m`/`0`, the same `SUM(... payment_channel='ach_bank_debit')` with N ∈ {2, 1}. Its third tier ("no bank-debit payment in the last two months" → nothing) is extensionally the same as either window on its own domain, because both sums are 0 there.

The other three method factors (`credit_counting_basis`, `bank_same_day_basis`, `portal_credit_counting_basis`) change which channels' payments are counted, and are honest. With F5, the phone debit, portal debit and pay-down computations each have zero honest `method` factors, below the floor of one per computation.

Industry realism of conditions and outcomes:
- Returned-payment, broken-plan, chargeback, card-on-card and denied-assistance risk tiers are things collection agencies do weigh for payment acceptance limits and paydown buffers.
- The medical 500 floor matches the bureaus' medical-collection threshold, and the provisional ACH add-back matches the ACH return window.
- Weighting a debit-card velocity window by placement stage or by debt type (F5's two window factors) has no evident industry basis (observation O3). It is not demonstrable as "no business publishes this", so it is not raised beyond F5.
- The pay-down fall-through for debts ≥2737 days ("general_floor") prices a reporting floor for a debt the base says can no longer be reported. That is part of F3.

### findings

- **F1: SOURCE-POLICY RED (charter-global; bears on task 1's portal debit policy).**
  - Symptom: the portal debit-card assistance ladder leaves a gap that `compute` fills with a tier the rule does not state.
  - Evidence:
    - Rule: "fa_recent_pct where the account's Financial Assistance Review Hold carries a recorded assistance decision of denied and ended in the last fa_recency_months months, fa_older_pct where that hold … ended fa_recency_months or more months before the handling date, and standard_pct where the account has no Financial Assistance Review Hold with a denied decision."
    - Compute: `d_hold_ended_months: "MONTHS(CFIELD('hardship','ended_date', account_id=HID) or NOW, NOW)"`.
  - Situation: an FA Review Hold with a recorded `denied` decision and no `ended_date` yet. The hardship business allows this: in task 1's own world the decision is dated 2026-08-28 and the hold ended 2026-09-27, so the state held for 30 days.
  - Under the rule, no tier applies: not ended, so tiers 1 and 2 fail; a denied FA hold exists, so tier 3 fails. Under compute, `MONTHS(NOW, NOW)` = 0 < 3, which gives fa_recent_pct 0.60.
  - Root cause: the fall-through is stated as a specific condition rather than "every other case", and compute substitutes NOW for a missing date. The sibling policy uses `'1900-01-01'` for the same gap.
  - Task 1 picks up the consequence check; task 1's hold carries `ended_date` 2026-09-27.
- **F2: SOURCE-POLICY RED (charter-global; bears on phone debit, phone credit and portal bank in task 0, and portal debit in task 1).**
  - Symptom: the rule quantifies over any plan or hold of the account, but compute reads only the first matching holding row.
  - Evidence:
    - "where a payment plan on the account carries a broken date" vs `CFIELD('plan','broken_date', account_id=HID)`.
    - "where a payment plan on the account was closed with close reason broken_not_reinstated" vs `CFIELD('plan','close_reason', account_id=HID)` (phone credit, portal bank).
    - "the account's hardship hold is a Documented Hardship Hold that ended …" vs `CFIELD('hardship','variant_name'…)`/`CFIELD('hardship','ended_date'…)`.
    - "the account's Financial Assistance Review Hold carries a recorded assistance decision of denied" vs `XLATEST(... account_id=HID)` over all holds' decisions combined with `CFIELD` of the first hold.
    - `check_compute.CFIELD` returns `hs[0].get(field)`.
  - Situation: an account with two plans, the first not broken and the second broken and closed `broken_not_reinstated`. The plan charter allows several plans per account (`plan_msr_broken_plans_12m` counts them). The rule then gives broken tiers while compute gives the standard tier.
  - Each task file checks whether its world has more than one plan or hold on the account.
- **F3: SOURCE-POLICY RED (charter-global; bears on task 1's pay-down).**
  - Symptom: an undeclared override of `account_evt_credit_reporting`.
  - Evidence:
    - Base: "An initial report also requires balance_due at or above the debt type's amount in reporting_min_balance_by_debt_type … and a handling date before the obsolescence date …; after the obsolescence date only a deletion may be furnished", with `medical: 500.00`, `auto_deficiency: 250.00`, `private_student_loan: 250.00`.
    - Extended: "… and general_floor for any other debt type or for a debt whose first delinquency date is reportable_age_days or more calendar days before the handling date".
  - Situation: a medical debt with first delinquency 2737 or more days back. The base minimum is still 500 (or the debt is not reportable at all past obsolescence). The extended pay-down targets a balance under 100, so the same "bring it below the reporting minimum" request yields two amounts that differ by up to 400.
  - The `overwrite` of `account_ext_reporting_floor_paydown` names only `account_evt_payment_channels`. The fall-through tier's outcome for such debts (a $100 floor for a debt that cannot be reported) is also not a treatment a business would publish.
  - Task 1 checks whether its world reaches it.
- **F4: observation (charter-global).** Every rule says "rounded half up to the cent", while `RND` is Python `round`, which rounds half to even on the binary float. They diverge only on figures ending in an exact half-cent (for example the bank figure `(3000 − 2050.01) × 0.5` = 474.995). No task world in this difficulty produces a half-cent (checked per task).
- **F5: SOURCE-FACTOR RED (charter-global structure; bears on task 0's phone debit computation and on task 1's portal debit and pay-down computations).** These are mislabelled `method` factors.
  - Evidence: the six compute bindings quoted above, identical except for `within_months` (N = 1, 2, 3 for the two window factors; N = 2, 1 for the add-back), plus the add-back's "nothing" tier, which coincides with either window on its own domain.
  - The tiers substitute a different number (a look-back length) into one formula, which is the `parameter` kind under the skill's definition.
  - Consequence: after striking the label, the phone debit, portal debit and pay-down computations each have 0 `method` factors, below the floor of 1 per computation. Each task file demonstrates this on its own computations.
- **O1: observation.** The base returned-payment block (S7) is inherited untouched. The tier "two or more returned payments in the last six months" (phone debit and portal debit) can only be reached without a block when the latest return is older than the stage's `returned_payment_block_days` but under six months old. No world uses that tier.
- **O2: observation.** The difficulty's claim covers 14 event types (disputes, holds, verification, tradelines, restrictions, protected status, returns to client, letters), but all six extended policies are payment-posting ceilings. The gates pass, and coverage of the claim beyond `account_payment_posted` is outside this audit's four relationships.
- **O3: observation.** A debit-card counting window that depends on placement stage or debt type has no evident industry basis. It is raised only through F5.
- **O5: observation.** "afterwards" in three tool docstrings is about the consumer quoting the receipt, not about tool order.

## closing_checklist

Status after both reveals (2026-10-09T09:16Z+): **the difficulty does not close**, so the Step 4 checklist is not certified. What does hold:
- The per-task files `0.md` and `1.md` correspond one-to-one with tasks 0 and 1. Each has a frozen derivation and a comparison section. This is the first revision.
- `charter_scope` matches the partition derived pre-reveal: task 0 = {phone debit, phone credit, portal bank} with their three tools; task 1 = {portal debit, portal credit, pay-down} with their three tools. The scopes are pairwise disjoint, cover all six extended policies, and have independently generated uuid8s.
- Each tree has 2 prerequisite problems, 2 `value_input` edges and ≥1 `owner=user` write. The graph is acyclic across tasks.
- Every derived value, order, owner, tree edge and factor sensitivity equals GT.

What blocks closure:
- F5 (SOURCE-FACTOR RED): task 0's phone debit computation and task 1's portal debit and pay-down computations have no honest `method` factor.
- F1, F2 and F3 (SOURCE-POLICY RED at charter level): they reach no task world but stand in the charter.

The gates were not re-run by this audit: the artifacts are unchanged and the auditor does not run them (Step 0).

## revision_2

### charter_global_frozen (revision 2)

- Auditor: erl-task-policy-audit (independent; did not author the rework). Re-audit round 2, written 2026-10-10 before either task's round-2 GT (`tasks/{0,1}.json`) or the reworker's appended `worklog.md` record was read.
- Inputs, re-hashed by the auditor (equal to the brief):
  - `account.extended.yaml` = `efe0de649179d5e919b63300a8f69f917dd0ec6c43bce9cadb749f456ecd766f`. Changed since revision 1 (`8a922f5a…`).
  - `task_tools.py` = `acfd404f9b690ffd2edf896ca7fd55c07fc9ccd8085f5b9ab1ba04fbcde2447d`. Changed (`74b1ec23…`).
  - Views r2: `0.view.json` `a2c92e79…fe086` (byte-identical to r1); `1.view.json` `ea0b5e53…f37e` (`initial_state` and `frozen_time` identical to r1; one persona sentence changed).
- Both shared inputs changed, so every charter-global section below is re-derived in full rather than carried forward.
- Gate snapshot (from the coordinator): `/tmp/env0050_views/gates/env0050_placed_account_servicing_gates.txt`. All green: EXTENDED, TASK TOOL CONTRACT (6), REPLAY (24/24, 19/19), SOLVABILITY, COMPUTE (branches 39.50, max 41), GROUNDING, SCOPE. Entry conditions are satisfied.
- Contamination disclosure (charter-global): the auditor carries the round-1 GT values from its own revision-1 reveal. The coordinator's brief lists the reworker's claimed item ids, with no values. Nothing from round-2 GT or the round-2 worklog was read before this section and the two per-task revision_2 frozen sections were on disk.
- Scratch: `/tmp/env0050_audit_account/` (DSL cross-check only).

### policy_conflict_scan (r2)

- The base copy is still verbatim: the parsed non-extended keys equal `blueprint/products/account.yaml`.
- The six extended policies keep their ids, target tools, owners, triggers and subjects. The channel × desk partition and the two weakly connected prerequisite components ({phone debit → phone credit → portal bank}, {portal debit → portal credit → pay-down}) are unchanged, so the only disjoint and complete M = 2 partition is still one component per task.
- No new overlapping conclusion was found.

### rule_compute_equivalence (r2)

- Mechanical checks:
  - Every `compute_basis` value is a verbatim substring of its rule (0 misses).
  - Every compute binding has a basis entry.
  - Every `baseline.rule` sentence is a rule sentence.
  - Every `replaced_by` is a rule sentence.
- Re-swept sentence by sentence. The changed passages:
  - **Phone debit.** Plan standing now reads "any payment plan on the account carries a broken date", implemented as `XLATEST('plan','payment_plans','broken_date', date_field='broken_date', account_id=HID)`, which returns '' only when no plan of the account has a broken date. Equal.
    - New counted basis: "every card and bank-debit payment received in the last month where one or more credit-card payments were received in the last month and one or more bank-debit payments were received in the last three months, the debit-card and credit-card payments … where one or more credit-card payments … and no bank-debit payment … in the last three months, and the debit-card payments received in the last month in every other case" ↔ `debit_counted` over `dx_*`. Equal.
  - **Phone credit.** Cancellation uses "the most recent closing of a payment plan on the account with close reason broken_not_reinstated", implemented as `XLATEST(... 'closed_date' ..., close_reason='broken_not_reinstated')`. Equal.
    - The cushion reads "a Documented Hardship Hold on the account ended …; pause_cushion where no Documented … but a 30-Day Hardship Pause … did", implemented as two `XLATEST` over holds by tier with a guard on the documented tier. Equal.
  - **Portal bank.** "any payment plan on the account was closed with close reason broken_not_reinstated" ↔ `XCOUNT('plan','payment_plans', …, close_reason='broken_not_reinstated') >= 1`. Equal.
  - **Portal debit.** "fa_recent_pct where the latest assistance decision recorded on the account's hardship holds is denied and the most recent ending of a Financial Assistance Review Hold on the account falls in the last fa_recency_months months, fa_older_pct where … that most recent ending falls fa_recency_months or more months before …, and standard_pct in every other case, including a Financial Assistance Review Hold that has not yet ended" ↔ `d_fa_outcome` (latest decision over the account's holds) and `d_fa_ended_on` (latest FA-hold `ended_date`, '' when none), with the guard `d_fa_ended_on != ''` and the default `'1900-01-01'`. The fall-through is now "every other case" and an un-ended hold maps to standard in both faces. Equal.
    - New counted basis: same shape as phone debit, implemented by `pdx_*`. Equal.
  - **Pay-down.**
    - The floor is "the debt type's amount in the credit reporting minimums: medical_floor …, installment_floor …, general_floor for any other debt type" ↔ `reporting_floor` with no age term. Equal.
    - Margin: denied × decision recency ↔ `f_fa_outcome` / `f_fa_decided_on` / `f_decision_months`. Equal.
    - Add-back: return-reason sets ↔ `consumer_reversals_6m` / `bank_side_returns_6m` / `bank_sum_2m` / `card_sum_2m`. Equal.
    - Card cushion: unchanged.
    - New recoupment reserve: insurance credit within three months × rebill within six months ↔ `recoup_reserve`. Equal.
    - The figure "balance + add-back − floor + margin + cushion + reserve; rounded once" ↔ `paydown_figure`. Equal.
  - **All six policies.** "rounded to the cent (half to even)" ↔ `RND` (Python `round`). See R2-O1.
- Every factor ladder tier is a rule clause and a branch of its `decides` binding, and the reverse holds too.

### action_binding_and_uuids (r2)

- The six `(target_tool, computes)` pairs are unchanged and each is claimed once. The uuid8s are unchanged (`cc21c0ad`, `bec5ec25`, `436b09cd`, `fc4d38a9`, `7a2662c6`, `d463b192`): independent, not batch-derived.
- Docstrings: "The consumer can afterwards quote the confirmation number" is now "The receipt gives the consumer the confirmation number". No docstring states a sequence or names another tool.
- Bodies: same `find` → `create` → `update` shape, with no eligibility, limit or prerequisite test.
- The module docstring still says "decided from the published policy before the call". That is not a tool docstring and states no tool order.

### prerequisite_graph (r2)

- Unchanged edges, all action-form with a `fallback_reason` and all `value_input`: phone credit → phone debit (`credit_counted`), portal bank → phone credit (`same_day_counted`), portal credit → portal debit (`portal_credit_counted`), pay-down → portal credit (`card_cushion`).
- `policy_source` is verbatim in each blocked rule. `resolved_by` equals each depended-on `target_tool`. The graph is acyclic.
- No authoring-viewpoint phrasing appears in any `prerequisite` field. PASS.

### prerequisite_sentences (r2)

- The four sentences and fallbacks are textually unchanged, so the revision-1 four-point test, fallback test and single-reading derivations still hold.
- Undeclared-order sweep over the rewritten rules: the remaining connectives are computational ("after the subtraction", "before the handling date", "after the most recent such return") or the four declared sentences.
- The new counted bases make the phone debit ceiling read credit-card payments of the last month, and the portal debit ceiling read credit and bank payments of the last month. Same-day credit payments would therefore enter the debit figure if taken first. That order is excluded by the declared sentences (each credit ceiling waits on its debit ceiling), so no second order is defensible. PASS.

### override_declarations (r2)

- `account_evt_payment_channels`: S3/S3′ overrides are still declared verbatim in each policy. S1, S2, S4 (minimum), S5, S6 and S7 (block) are inherited untouched.
- `account_evt_credit_reporting` (pay-down): the reporting floor now equals `reporting_min_balance_by_debt_type` for every type (medical 500; auto_deficiency / private_student_loan 250; bank_card, utility, telecom, retail_installment 100). The age carve-out is gone, and the rule adds "Whether the account can still receive an initial report at all is decided by the credit reporting rule, which this pay-down does not restate." There is no longer any conflict with the base minimum or the obsolescence bar. **F3 is closed.**
- No disguised override was found.

### factor_ladders (r2)

| policy | factors (label) | parameter / method | multi-source present | cross_difficulty |
| --- | --- | --- | --- | --- |
| phone debit | rolling_limit (p), plan_standing (p), **exposure_basis (m)**, track_record (p) | 3 / 1 | plan_standing, exposure_basis (credit 1m ∧ bank 3m), track | plan |
| phone credit | card_on_card_limit (p), plan_cancellation (p), counting_basis (m), hardship_cushion (p) | 3 / 1 | counting_basis, hardship_cushion (documented ∧ pause tiers) | plan, hardship |
| portal bank | return_limit (p), same_day_basis (m), retest (p), installment_record (p) | 3 / 1 | retest, same_day tier 2 | plan |
| portal debit | return_limit (p), assistance (p), **exposure_basis (m)**, clean_record (p) | 3 / 1 | assistance (decision event ∧ FA-hold ending), exposure_basis, clean | hardship |
| portal credit | bill_limit (p), assistance (p), counting_basis (m), appeal (p), dispute (p), steady (p) | 5 / 1 | appeal, dispute, counting | hardship |
| pay-down | margin (p), **provisional_addback (m)**, card_cushion (p), **recoupment_reserve (p, new)** | 3 / 1 | addback, card_cushion, recoupment (credit ∧ rebill) | hardship |

Label honesty (F5 re-test):
- `debit_exposure_basis` and `portal_debit_exposure_basis` now select {debit + credit + bank, last month} / {debit + credit, last month} / {debit, last month}. The window is fixed at one month and the tiers change the set of channels counted, which is a change of population, the same kind as the accepted `credit_counting_basis`. Honest.
- `paydown_provisional_addback` now selects {bank + card, two months} / {bank, two months} / nothing. The tiers change the channel set, and the third tier differs from the second on its own domain (bank payments inside two months still exist when no qualifying return exists). Honest.
- **F5 is closed.** Every computation now has one honest `method` factor.

Other structural checks:
- Counts are 4, 4, 4, 4, 6, 4; each policy has ≥2 `parameter` and 1 `method`.
- Bindings are disjoint, and no `decides` is `result`.
- Three disjoint tiers each, distinct outcomes: the margin tiers are 25 / 10 / 0.01 and the reserve tiers 40 / 20 / 0.
- Each fall-through equals its baseline, and each factor's `baseline` is what `baseline.rule` states. The pay-down baseline is now "balance due less the reporting floor plus cent_margin", with the debt-type floor inside the baseline and `params` listing the three floors.
- Each `baseline.rule` is self-sufficient.

Realism:
- Return-reason-sensitive add-back (consumer reversals add card payments back; NSF or closed-account returns add bank payments only), insurer recoupment reserves on medical accounts, and a decision-recency margin are all treatments a medical-collection desk would plausibly publish.
- A cross-channel "exposure" count inside a debit-card ceiling, triggered by recent credit-card and bank-debit activity, is unusual but not demonstrably unreal. Observation R2-O3.

### findings (r2) — status of revision-1 charter-global items

- **F1 (SOURCE-POLICY): closed.** The ladder fall-through is "every other case, including a Financial Assistance Review Hold that has not yet ended". Compute maps a missing ending to standard (`d_fa_ended_on != ''` guard, default `'1900-01-01'`). For a denied FA hold not yet ended, both faces give standard_pct.
- **F2 (SOURCE-POLICY): closed.** The single-row `CFIELD` reads are replaced by account-wide `XLATEST` / `XCOUNT`, and the rule text says "any payment plan", "the most recent closing", "a Documented Hardship Hold on the account" and "the latest assistance decision recorded on the account's hardship holds". With two plans (first unbroken, second broken and closed), both faces now give the broken and recent-closing tiers.
- **F3 (SOURCE-POLICY): closed.** See override_declarations (r2).
- **F4 (observation): partly addressed.** The rule now names "half to even", but `RND` is Python `round` on binary floats, which is not decimal half-even for every half-cent. For example, 2.675 gives 2.67 under `round` and 2.68 under decimal half-even (checked). No task world produces a half-cent figure. Carried as **R2-O1**.
- **F5 (SOURCE-FACTOR): closed.** See factor_ladders (r2).
- **O1 (block), O2 (claim breadth): unchanged.** Still observations.
- **O3: moot.** The window factors it concerned were removed.
- **O5: closed** (docstring wording).
- **New: R2-O2 (observation).** The `inputs` metadata of phone debit still lists `{sum debit_card, within_months: 2}`, and portal debit still lists `{sum debit_card, within_months: 3}`. No binding computes either since the rework. This is metadata only and does not touch rule, compute or any scored value.
- **New: R2-O3 (observation).** See the realism note above.
- **New: R2-O4 (observation).** Portal debit, when an account carries two Financial Assistance Review Holds, one ended and one not: the rule's "including a … Hold that has not yet ended" can be read as forcing standard_pct, while tiers 1 and 2 (and compute) key on the most recent ending among the holds that did end. No task world has two FA holds, so this is not demonstrable on any scored value.
- **No new SOURCE-POLICY or SOURCE-FACTOR finding at charter level.**

## closing_checklist (revision 2)

Written after both round-2 reveals (2026-10-10). Both tasks PASS on all four relationships.

- The per-task files `0.md` and `1.md` correspond one-to-one with tasks 0 and 1. `_difficulty.md` sits alongside them. Revision 1 is preserved verbatim above each `## revision_2`. Each revision-2 comparison section carries a PASS.
- Coverage and scopes:
  - All six extended policies are covered.
  - `charter_scope` is task 0 = {phone debit, phone credit, portal bank} and task 1 = {portal debit, portal credit, pay-down}. The scopes are pairwise disjoint, and each spans its whole tree.
  - Task tools and GT are closed: each scored write is one of that task's three tools.
  - The uuid8s are independently generated and frozen (unchanged since revision 1).
- Trees: each has 2 prerequisite problems, 2 `value_input` edges and ≥1 `owner=user` write (task 0: portal bank; task 1: portal debit and portal credit). Neither tree has a cycle, and the difficulty-wide graph is two disjoint acyclic chains.
- Factors:
  - Every computation declares a self-sufficient baseline and 4–6 factors (4, 4, 4 | 4, 6, 4), each with ≥2 parameter and 1 honest method.
  - Each task has ≥1 multi-source factor and ≥1 cross-difficulty factor (task 0: plan and hardship; task 1: hardship), with seeded rows.
  - Every ladder has three tiers stated in full in its rule, with distinct outcomes.
  - Every factor bears weight against an honest baseline, and each whole baseline gives a definite number different from gold. Task 0: 4651.44 / 3601.44 / 2601.44 vs 1050.00 / 1000.00 / 675.00. Task 1: 2058.49 / 1098.49 / 138.50 vs 960.00 / 460.00 / 478.49.
- Gates: re-run on the final form by the coordinator after the rework, on the same hashes this audit froze (`efe0de64…`, `acfd404f…`). All green: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE. Snapshot: `/tmp/env0050_views/gates/env0050_placed_account_servicing_gates.txt`. `check_traceability` is still deferred until the KB is published.
- Remaining observations (not grounds for rework):
  - R2-O1: Python `round` vs decimal half-even at half cents.
  - R2-O2: stale `inputs` metadata in phone debit and portal debit.
  - R2-O3: realism of a cross-channel exposure count.
  - R2-O4: wording for two FA holds.
  - O1 / O2 carried from revision 1.

**Source-layer audit of `placed_account_servicing`: PASS (revision 2).**
