# Policy-task audit — practicepay_patient_financing / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit subagent (Claude Opus 5.5), independent of the instantiator; revision_1.
- Freeze time: 2026-10-16 05:00:49 UTC (file birth time). Every line in this section was written before any task's GT was revealed and contains nothing derived from a revealed GT.
- Frozen inputs (sha256, re-verified at the start of the audit):
  - `tasks/practicepay_patient_financing/pos.extended.yaml` = `866dbd5baf569962d1e38c14d1e244c9468d2f1d55d10e3a10b0383593478e62`
  - `tasks/practicepay_patient_financing/task_tools.py` = `adfc929739f7f6c295e89496ac554a8a28870396df227bc63da1615dd03e0afb`
  - masked views `.audit_views/policy/practicepay_patient_financing/r1/task_0.json` = `bc0561…6429c`, `task_1.json` = `62066d…0e03` (hashes match the coordinator brief).
- Fields read: blueprint (`blueprint.yaml` difficulty entry, `db_schema.json`, `share_tools.py`, `products/pos.yaml`, the parts of `products/loan.yaml` that the cross-category reads touch: multi-holding cap, refinance closure, late-fee grace and WI fee schedule), the extended charter, `task_tools.py`, the masked views (frozen_time, user_scenario, initial_state), the DSL helpers in `skills/erl-task-instantiate/scripts/check_compute.py` (to know how `MONTHS`, `DAYS`, `within_months`, `LATEST`, `CFIELD`, `XCOUNT`, `RND` evaluate), and `audits/render_source/XF_recipe.md`.
- Fields masked / not read before the freeze: everything in `_masked_keys` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*), the raw `tasks/*.json`, `worklog.md`, any earlier audit. No recursive search touched `tasks/*/tasks/`.
- Entry conditions (Step 0): gate snapshot supplied (`.audit_views/policy/practicepay_patient_financing/r1/gate_snapshot.txt`): EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK with only `unlock_*_discoverable_tool:tool_name` misses (KB not rendered yet). Masked views and their hashes supplied. Entry conditions met; the traceability state is pre-publication and is not a finding of this audit.
- Base copy: `diff` of extended lines 1–1325 against `blueprint/products/pos.yaml` is empty (only the 4-line `extended_policies` header comment is appended). The base is verbatim.

### policy_conflict_scan

Six extended policies, owners and target tools (tool owners from `task_tools.py`):

| id | trigger | computes | target_tool | owner | prerequisite |
| --- | --- | --- | --- | --- | --- |
| pos_ext_returned_item_fee (RIF) | state_due | fee_amount | assess_returned_payment_fee_f9ef5ea0 | agent | [] |
| pos_ext_late_fee_schedule (LFS) | state_due | fee_amount | assess_late_fee_02ab9d3a | agent | RIF (value_input, same_event_fee) |
| pos_ext_payoff_quote (PQ) | on_request | payment_amount | pay_off_plan_f18fb847 | user | LFS (value_input, plan_bal) |
| pos_ext_deferred_interest_bill (DIB) | state_due | billed_amount | bill_deferred_interest_8f2fb1f1 | agent | [] |
| pos_ext_disputed_interest_credit (DIC) | state_due | credit_amount | credit_disputed_deferred_interest_91950e60 | agent | DIB (value_input, billed_amount) |
| pos_ext_post_promo_reset (PPR) | on_request | monthly_payment_amount | reset_payment_and_autopay_03cef1f2 | user | DIC (value_input, plan_bal) |

- Overlapping subjects: RIF/`pos_returned_payment_fee_assessed`, LFS/`pos_late_fee_assessed`, PQ/`pos_payment_posted`, DIB/`pos_deferred_interest_billed`+`_cleared`, DIC/`pos_fee_waived` (dispute_resolved credit of a DI billing entry), PPR/`pos_plan_terms_updated`. No two extended policies claim the same event with the same quantity. DIB and PPR both retire the same base sentence of `pos_deferred_interest` ("If it fails, the whole memo …"); each `replaced_by` names the sibling's case (DIB: "or at the rate a post-promotion payment reset sets where the payment-reset schedule applies"; PPR: "a plan billed but not reset keeps the plan APR, and the amount billed follows the deferred-interest billing schedule"). The merged reading is unique: billed amount per DIB; rate after billing = plan APR unless PPR reset.
- Triggers / eligibility / time anchors: base eligibility (late-fee grace, one late fee per due date, fee-bearing return codes, dispute window for dispute_resolved waivers, payable status) is inherited untouched by every extended policy; no extended rule weakens it. DIB's billing date (promo_end_date + 1) equals the base `billed_after_promo` anchor.
- Terminal states: compatible, except the PPR rule/tool terminal-state conflict recorded as CG-6.
- Cross-category read boundary: every policy reads the customer's Larkspur personal loan (`loans` row + `loan_transactions`), declared under `cross_category` with `category: loan`; read-only. The read's object selection is ambiguous when the customer has more than one loan (CG-1).
- Scope partition (pre-reveal, from the trees each world forces — see the task files): task 0 = {RIF, LFS, PQ}; task 1 = {DIB, DIC, PPR}. Pairwise disjoint and jointly complete over the six extended policies. The comparison against `charter_scope` is done after the reveal in the task files.

### rule_compute_equivalence

- Mechanical sweep (scratch script, normalised whitespace): every `compute_basis` quote of all six policies is a substring of that policy's `rule`; every compute binding has a `compute_basis` entry; every `baseline.rule` sentence and every overwrite `replaced_by` is verbatim in the rule; every `superseded_clause` is verbatim in the named base policy. XF5 clean.
- Rounding (XF6): RIF `RND(MN(fee_before_cap,item_amount),2)` = "capped … rounded to the nearest cent once, at the end"; LFS `RND(MX(0, MN(fee_before_cap,unpaid_part) - same_event_fee),2)` = "reduction … after the cap at the unpaid part and before the rounding"; PQ/DIB single `RND` at the end; DIC `RND(MN(…, billed_amount),2)` = "capped at the deferred-interest billing entry, … rounded … once, at the end"; PPR ceil-to-cent then `MX(min_monthly_payment_usd, …)` = "rounded up to the next cent and never below min_monthly_payment_usd". Consistent.
- Semantic sweep, sentence by sentence back from compute: every quantity, window (`within_months` = fewer than N whole months by the rule's own whole-month convention), filter, tier, cap and rounding has its sentence. Departures found:
  - CG-1 (loan reads): rules say "the customer's Larkspur personal loan", "an active personal loan with no late fee dated within the last 12 months" / "whose active personal loan shows a late fee" (RIF, LFS, DIB, DIC, PPR) and "a payment on the customer's Larkspur personal loan came back … and that loan now shows an amount past due" (PQ); compute counts `XCOUNT('loan','loan_transactions', …)` over every loan of the customer (closed/refinanced ones included) and reads `CFIELD('loan','amount_past_due', status='active')` from the first active loan found.
  - CG-2 (LATEST without a tie rule), CG-3 (negative DIC credit days): the rule states no branch for the case the compute resolves silently.
  - LFS `unpaid_part = MX(0, …)`: the floor is not a rule sentence, but the rule's scope ("only for such a due date" with part of the payment still unpaid) gives the same 0 → observation O-7.
- Factor ladders against the rule: every tier named in `factors[].ladder` is a sentence of the rule and a branch of its `decides` binding, and every branch is a stated tier (checked for all 32 factors). No tier lives in only one face.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy; no base policy has a target tool.
- uuid8s: f9ef5ea0, 02ab9d3a, f18fb847, 8f2fb1f1, 91950e60, 03cef1f2 — six distinct values, no shared prefix/suffix, no sequence, no visible derivation. Pass.
- Tool bodies: every write tool calls `ctx.create`/`ctx.update` itself; no tool reads another row to refuse, error or hint; no `datetime/time/random/uuid/secrets` import (XF13 pass). No factor id is a substring of any tool name (XF10 pass; scratch sweep).
- Docstrings (XF7): no example values; no ordering words between task tools except one reference to another tool's output: `credit_disputed_deferred_interest_91950e60`, arg `related_txn_id`: "as shown by the PracticePay ledger lookup or the billing receipt" — "the billing receipt" is the receipt of `bill_deferred_interest_8f2fb1f1` ("the receipt confirms both entries") → CG-5.
- Terminal state vs rule: `reset_payment_and_autopay_03cef1f2` writes only `monthly_payment_amount` and `autopay_enrolled`; `plan_apr` and `next_due_date` are untouched → CG-6.

### prerequisite_graph

- `prerequisite` present on all six (`[]` on RIF and DIB). Edges: RIF→LFS, LFS→PQ, DIB→DIC, DIC→PPR. Every `problem` is an extended id of this file, never a base policy, never self. Two disjoint chains; acyclic.
- `policy_source` of every edge is verbatim in the blocked policy's own rule (sweep). `form: state` on all four; no `fallback_reason` (none needed). `kind: value_input` on all four; `gate` names a real binding (`same_event_fee`, `plan_bal`, `billed_amount`, `plan_bal`). `resolved_by` = the depended-on policy's target_tool on all four. No authoring-viewpoint phrasing.
- `effect` text checked against the compute: LFS ("while it is missing same_event_fee is 0 and the late fee is overstated"), PQ ("the payoff amount rises by exactly that fee" — fee enters `plan_bal` and `late_owed`, so the interest base is unchanged and the result rises by the fee), DIC ("while it is missing billed_amount is 0 and the credit is 0.00"), PPR ("Booking the credit lowers the plan balance … the reset monthly payment fall[s]"). All hold as stated.
- `condition` vs sentence: E2 (PQ) and E4 (PPR) conditions are narrower than their sentences → CG-4.

### prerequisite_sentences

| edge | sentence (verbatim, blocked rule) | connective | state named | one write brings it about |
| --- | --- | --- | --- | --- |
| E1 RIF→LFS | "A late fee is fixed only after the plan's ledger carries the returned-payment fee owed for every payment that came back with a fee-bearing return code." | only after | ledger carries RPF per fee-bearing return | `assess_returned_payment_fee` only |
| E2 LFS→PQ | "A payoff amount is not worked out until the plan's ledger carries the late fee owed for every monthly due date whose grace period has ended unpaid." | not … until | ledger carries late fee per due date unpaid past grace | `assess_late_fee` only |
| E3 DIB→DIC | "A deferred-interest credit is not booked until the plan's ledger carries the deferred interest billed for its promotional period." | not … until | ledger carries the DI billing entry | `bill_deferred_interest` only |
| E4 DIC→PPR | "The reset monthly payment is fixed only after the plan's ledger carries the deferred-interest credit owed on every billing dispute the provider resolved with a credit." | only after | ledger carries the dispute-resolved DI credit | `credit_disputed_deferred_interest` only |

- Four-point test: explicit ordering connective (all four); record-visible state in table words, no action/performer/tool (all four); no tool name, policy id, snake_case token or row id (all four); strength and scope vs `condition`: E1 and E3 match; **E2 and E4 do not** (CG-4).
- Written derivation (sentence + records + depended-on rule → resolving action, single reading): E1 — returned-payment entry with a fee-bearing code and no `pos_returned_payment_fee_assessed` naming it → RIF's rule ("The returned payment the fee is for is the latest returned-payment entry …") sets that fee → assess it. E2 — `next_due_date` past its 10-day grace with `amount_past_due` > 0 and no late-fee entry for that `installment_due_date` → LFS's rule ("The due date the late fee is for is the plan's oldest unpaid due date as the plan shows it") → assess it. E3 — promotional payoff test failed (balance − open disputes > 0 at end of promo_end_date) and no `pos_deferred_interest_billed` → DIB → bill it. E4 — a `resolved_merchant_credit` dispute with a posted refund and no dispute-resolved waiver naming the DI billing entry → DIC → credit it. Single reading in each case within the conditions; E2/E4 have the second reading of CG-4 outside them.
- No second wording of any edge, no tool name, no other problem's id in the blocked rules; the depended-on rules do not restate the sentences. Cross-problem mentions outside edges: DIB↔PPR sibling-overwrite references (required by XF4, state no order: O-4); PPR's scope sentence "on a deferred-interest plan whose deferred interest has been billed" (a state its declared chain already implies; no alternative terminal state: O-3). No base rule sentence grounds any edge.
- Docstring silence about sequence: violated once (CG-5).

### override_declarations

Sentence by sentence against each `base_policy_refs` entry (finding half only):

- RIF vs `pos_evt_payments_and_fees`: the returned-payment-fee sentence is the only one governing the scored quantity; retired and replaced (declared, self-scoped, out-of-scope R07/R10/R29/CB restated). Allocation, cutoff, late-fee, refund sentences followed. vs `pos_agg_combined_exposure`: no sentence governs the fee (ref only grounds the loan read). No undeclared override.
- LFS vs `pos_evt_payments_and_fees`: late-fee amount sentence retired and replaced (declared; cap at unpaid part, one per due date, dispute exclusion restated). Grace sentence followed. vs `pos_evt_billing_disputes`: dispute exclusion followed. No undeclared override; the same-event reduction is part of "the amount this fee schedule sets".
- PQ (`overwrite: []`) vs `pos_evt_payments_and_fees` (allocation, excess treatment — followed), `pos_plan_terms_and_interest` (simple daily interest on balance excluding fees — followed with APR/36,500; payoff stub/good-through not addressed by base), `pos_evt_billing_disputes` (open-dispute exclusion concerns amount past due and payoff test, not payoff amount — no conflict), `pos_evt_closure_and_charge_off` (credit balance refund — followed). No base sentence fixes a payoff amount, so `overwrite: []` holds. Observation O-5: the "credit still to post" carve-out sits beside `pos_evt_provider_refunds` ("A refund reduces the plan balance on its posting date"), which PQ does not list; the carve-out does not say the refund reduces the balance earlier, so no two-clause fight is demonstrable.
- DIB vs `pos_deferred_interest`: "If it fails, the whole memo …" retired (declared). Accrual-basis and "late payment does not cancel the promotion" sentences followed. "A partial provider refund does not reduce deferred interest already posted to the memo" — DIB's dispute relief bills less without reducing the memo ("any part of the memo the schedule does not bill is not owed", declared). vs `pos_evt_billing_disputes`: followed. Observation O-6: the base event field `pos_deferred_interest_billed.amount` is described "Deferred interest billed (the full memo)" — an events-section description, not a policy clause.
- DIC vs `pos_deferred_interest`: partial-refund sentence retired (declared, real conflict, self-scoped). vs `pos_evt_fee_waiver`: three sentences retired — "A late or returned-payment fee may be waived once.", the courtesy-count sentence and the courtesy-window sentence — each `replaced_by` repeats the base sentence verbatim and appends a clause about DI credits; none of the three base sentences governs a DI credit, so none conflicted → CG-7. vs `pos_evt_billing_disputes`: dispute-window eligibility for dispute_resolved waivers inherited (DIC compute does not re-test it; both worlds' disputes are inside the window).
- PPR vs `pos_plan_terms_and_interest`: payment-method clause and AutoPay "no rate discount" clause retired (declared, self-scoped). Due-day sentence ("the payment amount does not change") concerns due-day changes only. vs `pos_deferred_interest`: rate-after-billing clause retired (declared, sibling named). No undeclared override.
- Disguised forms: no anonymous intermediate factor, no 0/1 multiplier on a base-fixed amount (RIF's `fee_bearing_item` zero restates the base no-fee codes), no dropped base branch.

### factor_ladders

Counts as declared (P = parameter, M = method; X = cross_difficulty `loan`; MS = multi-source):

| policy | factors (label) | P/M | MS | X |
| --- | --- | --- | --- | --- |
| RIF | returned_item_level (P, MS: returns × late fees), return_reason_share (P), item_size_rule (M), plan_age_band (P), ledger_balance_band (P), personal_loan_standing (P, MS: loans row × loan_transactions, X) | 5/1 | 2 | 1 |
| LFS | late_record_level (P), partial_payment_rule (M), late_plan_age_band (P), late_ledger_balance_band (P), late_loan_standing (P, MS, X) | 4/1 | 1 | 1 |
| PQ | stub_interest_span (M), disputed_carve_out (P), return_record_hold (P), return_reason_hold (P), personal_loan_return_hold (P, MS: loan_transactions × loans row, X) | 4/1 | 1 | 1 |
| DIB | di_unposted_span (M), disputed_interest_relief (M), bill_shortfall_band (P), bill_payment_record (P), bill_autopay_count (P), bill_loan_standing (P, MS, X) | 4/2 | 1 | 1 |
| DIC | credit_days_rule (M), credit_shortfall_band (P), credit_payment_record (P), credit_autopay_count (P), credit_loan_standing (P, MS, X) | 4/1 | 1 | 1 |
| PPR | remaining_payments_rule (M), reset_loan_rate_cut (P, MS, X), reset_record_rate_cut (P), reset_autopay_rate_cut (P), reset_paydown_rate_cut (P) | 4/1 | 1 | 1 |

- Structure that passes for all 32: bindings disjoint within each policy; `decides` is an input, never `result`; ladders have three pairwise-disjoint tiers each stated in the rule and implemented in compute; values drawn from `params`/variant parameters; fall-through = baseline in every factor; no factor binding reads another factor's binding (XF1, listed per policy in the scratch sweep); assembly stated once with order fixed (XF2); baselines are complete standard methods whose sentences are all in the rule (O-1 notes two dangling back-references).
- Method honesty / tier distinctness (XF9) — fails for six method factors (CG-8):
  - PQ `stub_interest_span`: tier 2 "accrual from the purchase date through today" and tier 3 "accrual from the latest statement closing through today" are the same single-span formula `interest_base × daily_rate × DAYS(start, NOW)`; only the window start differs.
  - DIB `di_unposted_span`: tiers 2 and 3 likewise (`accrual_base × daily_rate × DAYS(start, promo_end)`, start = purchase date vs latest posting).
  - DIB `disputed_interest_relief`: tiers 1 and 2 are both `dispute_amount × daily_rate × DAYS(filed, end)`; only the window end differs (resolution date vs promo_end_date); tier 3 is the value 0.
  - DIC `credit_days_rule`: all three tiers are the same credit formula over a count of days; they differ only in which date windows are counted (purchase→filing + resolution→refund; purchase→filing; resolution→refund).
  - PPR `remaining_payments_rule`: tiers 1 and 3 are both `term − MONTHS(purchase, anchor)` with a different anchor (oldest unpaid due date vs reset date); tier 2 is the same with a third anchor and a constant −1.
  - RIF `item_size_rule`: tiers 2 ("fixed floor": 0.5) and 3 ("flat": 1) are the same method — a constant share — with different numbers.
  - LFS `partial_payment_rule` passes (ratio; max(floor, ratio); constant 1 — three shapes).
- Realism of conditions and outcomes (XF12, Core table "unreal ladder") — fails (CG-9):
  - (a) RIF `return_reason_share`: a returned-payment fee cut to 80 % because the account was closed / not found / invalid (R02–R04) and to 90 % for a frozen or non-transaction account (R16/R20). US lenders' returned-payment fees are flat per returned item (subject to the cap at the payment amount); the return code decides fee-bearing or not, never a discount on the fee.
  - (b) RIF `plan_age_band`, LFS `late_plan_age_band`: penalty fees discounted 20 % / 10 % because the plan is young. No lender publishes penalty fees scaled by account age (the real first-vs-repeat distinction is already the history factor).
  - (c) RIF `item_size_rule` tier 1: the returned-payment fee scaled by the ratio of the returned amount to the monthly payment. The real rule is a flat fee capped at the amount returned (the rule's own cap); a proportional returned-item fee is not a published practice (unlike a late fee set as a percentage of the unpaid installment, which LFS's partial-payment rule mirrors and which is real).
  - (d) DIB `bill_shortfall_band`, `bill_payment_record`, `bill_autopay_count`, `bill_loan_standing`: shares of 0.8–0.98 that forgive part of the retroactive deferred interest for a small remaining principal, a clean record, AutoPay history or a current personal loan. The defining term of a US deferred-interest promotion — and this charter's own base ("the whole memo - every period since the purchase date, not only the unpaid part") — is that all accrued interest is assessed when the promotion is not paid off; partial forgiveness keyed to behaviour is not a practice any deferred-interest lender publishes.
  - (e) DIB `disputed_interest_relief` tier 1 condition "resolved with a provider credit **or as no error**": withholding interest on the disputed amount when the dispute ends as no error is not real practice (a no-error outcome makes the disputed amount and its finance charges payable; cf. Reg Z §1026.13(g)); that part of the compound condition is one no lender weighs toward relief.
  - (f) DIC `credit_shortfall_band`, `credit_payment_record`, `credit_autopay_count`, `credit_loan_standing`: the interest credit on an amount that was billed in error is cut by 2–20 % for paying down, a clean record, AutoPay history or a current loan — a billing-error correction scaled down by good behaviour. And `credit_days_rule` puts `incorrect_amount_charged` among "any other dispute reason", so the purchase→filing interest on an overcharge that was never owed is not credited while a duplicate charge's is — a distinction no lender draws between two billing errors.
  - (g) PPR `remaining_payments_rule` tier 2 ("term less the whole calendar months from the purchase date to that next due date, less one, since that installment was already billed at the old amount"): the installment billed at the old amount is still collected, yet the reset balance keeps its principal and the count drops it, so the reset payment amortises the whole reset balance over one payment fewer than will actually be collected — the schedule over-collects by design (demonstrated in task 1: about $180 overpaid at the end). No lender publishes a re-amortisation that sizes payments to over-collect.
- Counts after striking the factors CG-8/CG-9 strike (CG-10): RIF 3 survive (returned_item_level, ledger_balance_band, personal_loan_standing; 0 method) — below 4 and below 1 method; LFS 4 survive (3 P, 1 M) — passes; PQ 4 survive, 0 method — fails; DIB 0 survive; DIC 0 survive; PPR 4 survive, 0 method — fails. Every task still has ≥1 multi-source and ≥1 cross-difficulty survivor (personal-loan factors).
- Stamps: no record field names a factor tier (pos_plans has no tier fields; the loan's `fee_schedule` stamp belongs to the loan's own fee and no factor reads it).

### findings

Charter-global findings; each names the tasks it bears on. Per-task demonstrations live in `task_0.md` / `task_1.md`.

- **CG-1 SOURCE-POLICY RED — personal-loan reads have no defined object when the customer has a second loan (XF8 second-record decoy; rule↔compute).** Symptom: rule "an active personal loan with no late fee dated within the last 12 months" / "a payment on the customer's Larkspur personal loan came back … and that loan now shows an amount past due" vs compute `XCOUNT('loan','loan_transactions', …)` over all of the customer's loans and `CFIELD('loan','amount_past_due', status='active')` taking the first active loan. Root cause: the rule names "the customer's … personal loan" in the singular; the loan charter allows two open loans (`loan_agg_multi_holding.max_per_customer: 2`) and closes refinanced loans (`closure_reason: refinanced`). Demonstrated consequence (charter-level): customer with an active loan A (current, no late fee) and a paid-off loan B (closed by refinance) whose late fee is 4 months old — the rule gives RIF's relationship share `loan_current_share` 0.9 (A shows no late fee), the compute gives 1 (XCOUNT counts B's fee); same split for LFS, DIB, DIC, PPR; for PQ a 3-month-old return on B gives `loan_current_extra_days` by compute and 0 by the rule's "that loan". Affected: all six policies' `cross_category` loan bindings. Bears on: tasks 0 and 1 — neither world seeds a second loan, so no task-level consequence (see task files).
- **CG-2 SOURCE-POLICY RED — LATEST reads without a stated same-day tie rule (XF8).** Members: LFS "the plan's latest returned payment" (`latest_return_id/_date`); PQ "its latest returned payment" (`last_return_*`) and "the plan's latest payment entry" (`last_pay_*`); DIB "its latest returned payment" (`last_return_*`), "the plan's latest payment entry" (`last_pay_*`), "the plan's latest billing dispute" (`dispute_*` by filed_date); DIC "the plan's latest billing dispute" (`dispute_*`); PPR "its latest returned payment" (`last_return_*`). (RIF and LFS's partial-payment sentence do state "the one recorded first"; latest closing/posting are one per statement month; DIC's latest refund date is a date, so a tie is harmless.) Consequence: two same-day returns (or payments, or disputes) with different amounts give two readings of the fee owed / stub base / disputed amount; the compute silently keeps the first stored row. Bears on: neither task world has a same-day tie among these reads.
- **CG-3 SOURCE-POLICY RED — DIC credit days negative (XF8 negative date difference).** Rule tier 3 and the baseline: credit days "from the dispute's resolution date through the date the provider refund posted"; a provider refund that posts before the resolution date (any reason other than duplicate/service-not-rendered) gives negative days and a negative credit (`DAYS(dispute_resolved, refund_date) < 0`), while the tool takes "a positive amount". No rule branch covers it. Bears on: task 1 is a duplicate charge with refund after resolution — not reached.
- **CG-4 SOURCE-POLICY RED — prerequisite sentences broader than their conditions (check 6).** E2: sentence "every monthly due date whose grace period has ended unpaid" vs condition "For the plan's oldest unpaid due date …"; LFS can assess only "the plan's oldest unpaid due date as the plan shows it". World: due dates 09-02 and 10-02 both unpaid past grace, 09-02 already carries its late fee — the condition holds (PQ proceeds), the sentence does not and no rule of this difficulty can book the 10-02 fee (PQ never workable). E4: sentence "on every billing dispute the provider resolved with a credit" vs condition "For the plan's latest billing dispute resolved with a provider credit whose refund has posted"; DIC credits only the latest dispute and a DI billing entry "is credited on the dispute-resolved basis once". World: two credited disputes, or a credited dispute followed by a later withdrawn one — the sentence is unsatisfiable while the condition is met (or vacuous). Bears on: tasks 0/1 have a single unpaid due date / a single dispute, so the readings coincide there.
- **CG-5 SOURCE-POLICY RED — DIC tool docstring points at another tool's output (check 3 / XF7).** `credit_disputed_deferred_interest_91950e60` docstring, `related_txn_id`: "as shown by the PracticePay ledger lookup or the billing receipt". The only "billing receipt" in the tool set is `bill_deferred_interest_8f2fb1f1`'s ("the receipt confirms both entries"); the phrase places the credit after a billing done in the same conversation — the E3 order stated on the tool surface instead of being derived from the rule. Bears on: task 1.
- **CG-6 SOURCE-POLICY RED — PPR's stated effect is not a state the tool leaves (check 3, terminal state).** Rule: "interest from the reset onward is charged at the reset rate this schedule sets" and tier 2 "since that installment was already billed at the old amount"; tool body: `ctx.update("pos_plans", pos_plan_id, monthly_payment_amount=amount, autopay_enrolled=True)` — `plan_apr` and `next_due_date` unchanged; base `pos_plan_terms_and_interest`: interest "at the plan APR". After the gold write the record reads APR = old plan APR and monthly payment = the new amount due on the already-billed next due date; the rule reads APR = reset rate and that installment at the old amount. Two terminal readings (demonstrated in task 1). Bears on: task 1.
- **CG-7 SOURCE-POLICY RED — three overwrites retire base clauses that never conflicted (XF4).** DIC's overwrites of `pos_evt_fee_waiver` ("A late or returned-payment fee may be waived once."; the courtesy-count sentence; the courtesy-window sentence) each restate the base sentence verbatim and add a clause about the DI credit; none of the three base sentences governs a DI credit or a dispute-resolved waiver. Consequence: the charter declares three overrides where the merged semantics are unchanged, and the KB renders three "replaced" base clauses whose replacement is the same clause. Bears on: task 1 (DIC is in its tree); no scored-value consequence.
- **CG-8 SOURCE-FACTOR RED — method factors whose tiers differ only by a window, an anchor or a constant (XF9).** Members listed in factor_ladders (PQ stub_interest_span, DIB di_unposted_span, DIB disputed_interest_relief, DIC credit_days_rule, PPR remaining_payments_rule, RIF item_size_rule). Bears on: task 0 (RIF, PQ), task 1 (DIB, DIC, PPR).
- **CG-9 SOURCE-FACTOR RED — unreal ladders (realism, XF12).** Members (a)–(g) in factor_ladders. Bears on: task 0 ((a), (b), (c)), task 1 ((d), (f), (g); (e) and the incorrect-amount part of (f) are charter-only — not on task 1's path).
- **CG-10 SOURCE-FACTOR RED — surviving factor counts below the bounds.** RIF (3, 0 method), PQ (0 method), DIB (0), DIC (0), PPR (0 method). Bears on: task 0 (RIF, PQ), task 1 (DIB, DIC, PPR).

Observations (no RED; recorded for completeness):
- O-1 baseline.rule back-references: RIF "for that returned payment" and LFS "that monthly payment … that due date" point at sentences outside `baseline.rule` (the selection sentences). Both worlds give a definite baseline number anyway (task 0: the fee is 15.00 whichever return is read; one unpaid due date).
- O-2 E1 resolver reach: the sentence (= condition) covers every fee-bearing return, RIF computes a fee only for the latest one; an older un-fee'd return would block LFS with no rule able to fee it. Not reachable in task 0 (the older return carries its fee).
- O-3 PPR's scope sentence restates a transitive dependency on DIB as a scope state; the declared chain already fixes the order.
- O-4 DIB↔PPR sibling references (required by XF4).
- O-5 PQ carve-out of a provider credit not yet posted vs base "A refund reduces the plan balance on its posting date"; the payoff "in full today" leaves the plan open until the refund posts.
- O-6 base event description "(the full memo)" for `pos_deferred_interest_billed.amount`.
- O-7 LFS `MX(0, …)` floor on the unpaid part.
- O-8 Personal-loan "behind" tiers give a fee discount / rate cut (smaller than the current tier) to a customer currently past due on the loan; monotone in risk, questionable.
- O-9 PQ good-through hold days by return history (plausible funds-hold practice); PPR paydown rate cut (unusual) and record/AutoPay/relationship rate cuts (real forms).
- O-10 `within_months` boundary for a row dated exactly N months back is not stated (MONTHS convention excludes it).
- O-11 factor id `personal_loan_standing` equals a base eligibility id in `pos_agg_combined_exposure`.
- O-12 PQ `disputed_carve_out` is labelled parameter while its tiers draw the amount from different aggregates.

## closing_checklist

Written after both reveals (2026-10-16 05:03:18 UTC); nothing above this heading was changed by them except the freeze-time line, corrected to the file's actual birth time.

- Per-task files: `task_0.md`, `task_1.md`, one per task, alongside this file; revision_1 (no older revision exists).
- Both independent derivations equal GT on every scored item (tools, owners, order, arguments, terminal rows). Neither comparison section carries a PASS: task 0 is RED (SOURCE-FACTOR, SOURCE-CHAIN), task 1 is RED (SOURCE-POLICY, SOURCE-FACTOR, SOURCE-CHAIN).
- Coverage and scopes: `charter_scope` task 0 = {RIF, LFS, PQ} + their three tools, task 1 = {DIB, DIC, PPR} + their three tools — pairwise disjoint, jointly complete over the six extended policies and six task tools; uuid8s independent (§ action_binding_and_uuids).
- Trees: each has 2 prerequisite problems, 2 value_input edges, an `owner=user` root, no cycle; the difficulty graph (two disjoint chains) is acyclic.
- Factors: not closed — CG-8/CG-9/CG-10 leave RIF, PQ, DIB, DIC and PPR without a surviving method factor (RIF also below four factors; DIB and DIC with none). Every declared factor does bear weight against an honest baseline, and every whole-baseline number is definite and ≠ gold (task files).
- Proof text: one false skip figure per task (T0-1, T1-1), a false statement-closing date (T1-2) and three stale tier labels (T1-3).
- Gate re-run on the final form: not applicable — the difficulty does not pass, so there is no final form to close.
- The difficulty does **not** pass the source-layer audit.

VERDICT revision_1: task0=RED SOURCE-FACTOR+SOURCE-CHAIN task1=RED SOURCE-POLICY+SOURCE-FACTOR+SOURCE-CHAIN charter=CG-1,CG-2,CG-3,CG-4,CG-5,CG-6,CG-7,CG-8,CG-9,CG-10

## revision_2

### charter_global_frozen (revision_2)

- Auditor: erl-task-policy-audit subagent (Claude Opus 5.5), same auditor as revision_1, independent of the reworker. Written before any revision_2 GT field was read; contains nothing derived from a revealed GT.
- Entry gate: last line of `tasks/practicepay_patient_financing/worklog.md` is exactly `REWORK round 2: gates 7/7 green` (only that line was read).
- Gate snapshot (coordinator script `/tmp/erl0067_coord/snapshot.sh practicepay_patient_financing 2`, run 2026-10-16T12:01:27): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; TRACEABILITY NOT OK — 3 misses per task, every one an `unlock_*_discoverable_tool:tool_name` value (confirmed by re-running the traceability check and reading its miss lines). No gate RED.
- Frozen inputs: `pos.extended.yaml` sha256 `07c8b5bdfaacaa9f40b8408b6e0bd019fe547eea7dd29b166e9cb26ba24e3886`, `task_tools.py` `83033717f7f25bcdea32a19118745aa8d9a725e617a791ec44d17320decddc93` (both changed since revision_1 → every charter-global section is re-derived in full, none carried by reference); views `r2/task_0.json` `45a6e424…a1c7`, `r2/task_1.json` `0aec24ec…3a07`.
- contamination_disclosure: the traceability miss lines printed the unlock tool names of each task's gold (task 0: `assess_late_fee_02ab9d3a`, `reverse_returned_payment_fee_68fd6551`, `pay_off_plan_f18fb847`; task 1: `assess_returned_payment_fee_f9ef5ea0`, `grant_courtesy_fee_waiver_c5ffad08`, `reset_payment_and_autopay_03cef1f2`) before the blind derivations. This discloses each task's tool set (its scope), no argument, amount, order or owner. Both trees were nevertheless walked from the root's rule and the world; the scope partition below must be read as not blind.
- Read: rework claims (`rework_r2_claims.md`, ids only), the new charter, tools, views, the loan/line charters' event lists and the DB schema. Not read before the freeze: `tasks/*.json`, `worklog.md` (beyond its last line).
- Base copy: lines 1–1325 still identical to `blueprint/products/pos.yaml`.

### policy_conflict_scan (revision_2)

| id | computes | target_tool (owner) | prerequisite |
| --- | --- | --- | --- |
| pos_ext_returned_item_fee (RIF) | fee_amount | assess_returned_payment_fee_f9ef5ea0 (agent) | [] |
| pos_ext_late_fee_schedule (LFS) | fee_amount | assess_late_fee_02ab9d3a (agent) | [] |
| pos_ext_make_good_reversal (MGR, new) | reversal_amount | reverse_returned_payment_fee_68fd6551 (agent) | [] |
| pos_ext_payoff_quote (PQ) | payment_amount | pay_off_plan_f18fb847 (user) | LFS (state, plan_bal), MGR (action, plan_bal) |
| pos_ext_courtesy_returned_fee_waiver (CRW, new) | waived_amount | grant_courtesy_fee_waiver_c5ffad08 (agent) | PPR (state, autopay_on) |
| pos_ext_post_promo_reset (PPR) | monthly_payment_amount (+ stored rate) | reset_payment_and_autopay_03cef1f2 (user) | RIF (state, reset_balance) |

DIB and DIC are retired. MGR and CRW both write `pos_fee_waived` with `waiver_reason='courtesy'` naming a returned-payment fee entry (identical record shape). Scope partition: task 0 = {LFS, MGR, PQ}, task 1 = {RIF, PPR, CRW} (disjoint, complete; not blind — see disclosure). Conflicts found: R2-1, R2-2, R2-5, R2-10, R2-11 below.

### rule_compute_equivalence, action_binding_and_uuids, prerequisite_graph (revision_2)

- Sweeps (scratch): every `compute_basis` quote, `baseline.rule` sentence, `replaced_by` and `policy_source` is verbatim in its own rule; every `superseded_clause` verbatim in its base policy; every compute binding has a basis; no `CFIELD` remains; rounding sentences match `RND` placement (XF5, XF6 pass).
- Loan/FlexLine reads: rule "every … the customer has held" + "holds an active …" ↔ `XCOUNT` over all accounts + `EXISTS(status='active')` — equivalent (CG-1 closed).
- LATEST reads: every one carries "the one recorded first where two share that date", or reads a row unique by construction (fee per return, late fee per due date, closing per month, the returned payment's own row) (CG-2 closed).
- Tools: six uuid8s (f9ef5ea0, 02ab9d3a, f18fb847, 68fd6551, c5ffad08, 03cef1f2) distinct, independent; bodies validate nothing; imports only `erlbench`; docstrings name no other tool or receipt and carry no ordering word between tools or example value (CG-5 closed). The reset tool now stores `plan_apr` (CG-6 terminal half closed).
- Graph: RIF→PPR→CRW and LFS→PQ←MGR; acyclic; every `problem` an extended id; kinds `value_input` on all four; gates exist. The PQ←MGR action form carries a `fallback_reason` that holds (MGR's and CRW's records are indistinguishable, so no state singles out the reversal). CRW←PPR's gate `autopay_on` is a boolean that zeroes the waiver — a state gate in substance (observation O2-1; the floor of value_input edges is met by RIF→PPR in task 1).
- Sentences vs conditions: PQ←LFS, PPR←RIF, CRW←PPR now match their conditions (CG-4's two members closed); PQ←MGR does not (R2-4).

### override_declarations (revision_2)

- RIF, LFS: unchanged declarations; hold.
- MGR: retires the courtesy-count sentence (real conflict: a waiver booked without request) and restates it; the courtesy-window sentence stays in force and MGR states no window (observation O2-2: a late make-good is reversed by MGR's rule and barred by the base window for "courtesy" waivers). The "not counted" clause cannot be represented in the records (R2-2).
- PQ (`overwrite: []`): undeclared departure from base `pos_deferred_interest` (R2-5).
- CRW (`overwrite: []`): undeclared departure from the in-force courtesy sentence (R2-1).
- PPR: three declared overwrites; the payment-method `replaced_by` drops the activation method (R2-12). The three DIC fee-waiver no-op overwrites are gone (CG-7 closed).

### factor_ladders (revision_2)

| policy | factors (P/M; X = cross-difficulty) | method shapes (XF9) |
| --- | --- | --- |
| RIF | returned_item_level P, large_item_surcharge_rule M, returned_fee_balance_band P, returned_fee_loan_record P X(loan), returned_fee_flexline_record P X(line) | graduated / proportional / none — distinct |
| LFS | late_record_level P, partial_payment_rule M, late_principal_band P, late_fee_loan_record P X, late_fee_flexline_record P X | ratio / floored ratio / 1 — distinct |
| MGR | make_good_extent_rule M, make_good_timing_band P, make_good_return_record P, make_good_loan_record P X, make_good_flexline_record P X | amount ratio / day ratio / 1 — distinct |
| PQ | interest_since_closing_rule M, dispute_carve_out_rule M, return_record_hold P, return_reason_hold P, personal_loan_return_hold P X, flexline_return_hold P X | none / split / single span; read / difference / none — distinct |
| CRW | waiver_sizing_rule M, courtesy_history_band P X(loan), courtesy_autopay_band P, courtesy_loan_record P X, courtesy_flexline_record P X | capped / excess / whole — distinct |
| PPR | reset_payment_method M, five rate cuts P (loan X, line X, record, autopay, paydown) | re-amortize / re-divide / keep — distinct |

- XF9: all method factors now change shape (CG-8 closed).
- XF1 fails for PPR's five rate cuts (R2-7) and PQ's interest factor reaches outside its bindings (R2-6).
- Realism (XF12): the revision_1 members (return-reason and plan-age shares, proportional item size, DI forgiveness shares, scaled billing-error credits, over-collecting count, no-error relief) are gone. New members: R2-8 (RIF surcharge, same class as CG-9(c)), R2-9 (MGR fractional reversal). Personal-loan/FlexLine relationship shares and rate cuts, hold days and the AutoPay condition for a courtesy waiver are real forms (observations only).
- Counts after strikes (CG-10 class): RIF 4 survive, 0 method; MGR 4 survive, 0 method; PPR 1 survives (the method factor); LFS 5 (1 M), PQ 6 (2 M; R2-6 is a baseline-honesty defect, not a strike), CRW 5 (1 M) — pass.

### findings (revision_2)

Closure of revision_1 items (charter-global): CG-1 closed; CG-2 closed; **CG-3 not closed** — the DIC member is gone but MGR adds a new member of the class (R2-3), and the claim "make-good days only when something was made good after the return" is false; CG-4 closed for its two members, **class reopened** by PQ←MGR (R2-4); CG-5 closed; CG-6 closed (rate stored, no already-billed tier); CG-7 closed; CG-8 closed; **CG-9 not closed** — its listed members are gone, new members R2-8 (same sub-class as CG-9(c)) and R2-9; **CG-10 not closed** — RIF, MGR, PPR below the bounds after R2-7/8/9.

New charter-global REDs:

- **R2-1 SOURCE-POLICY RED — CRW departs from the in-force courtesy sentence without an overwrite.** In force (base as restated by MGR): "A courtesy waiver is granted on request when fewer than the plan's courtesy waivers per 12 months have been granted on the plan". CRW (`overwrite: []`): "A courtesy waiver of a returned-payment fee is not granted until the plan shows AutoPay turned on" and sizes the waiver below the fee (capped/excess tiers, four shares). Same request, two answers: the base gives the fee waived (customer asked, count 0 < limit, inside the window); CRW gives 0.00 while AutoPay is off and a sized fraction once it is on. Bears on task 1 (demonstrated there).
- **R2-2 SOURCE-POLICY RED — a make-good reversal "is not counted among those courtesy waivers", but the records count it.** MGR's tool books `waiver_reason='courtesy'`, identical to CRW's; base measure `pos_msr_courtesy_waivers_12m` = "Count of pos_fee_waived rows on this plan with waiver_reason = courtesy"; PQ's own `fallback_reason` states no record singles out the reversal. World: a 6-Month DI plan (1 courtesy per 12 months) with a make-good reversal three months ago; the customer asks for a courtesy waiver — the measure says 1 granted (refuse), MGR's clause says 0 counted (grant). Charter-only.
- **R2-3 SOURCE-POLICY RED — MGR treats a payment made before the bounce as making it good (XF8 negative span; CG-3 class).** Rule: "A returned payment is made good by the payments credited toward the due date it was for, other than the payment that came back"; compute `made_good = SUM(payments toward that due date) - returned_amount`, `days_to_make_good = DAYS(return_date, last_make_good)` with no test that the make-good payment follows the return. World: 50.00 credited 10-01 and 90.00 on 10-02 toward due date 10-02, the 90.00 returned 10-06, nothing after — made-good 50.00, extent 50/90, timing span −4 days → share 1: a reversal is booked for a bounce nobody replaced. Charter-only.
- **R2-4 SOURCE-POLICY RED — PQ←MGR condition stronger than its sentence (CG-4 class).** Sentence: "A payoff amount is worked out only after the make-good reversal owed on the returned-payment fee of the plan's latest returned payment has been booked." Condition: "When the plan's latest returned payment carries a returned-payment fee and has been made good in whole or in part, a pos_fee_waived entry names that fee entry." With three or more returns in 12 months `third_return_share = 0` → reversal owed 0.00, which the tool ("a positive amount") cannot book: the sentence is met (nothing owed), the condition never is. Charter-only.
- **R2-5 SOURCE-POLICY RED — PQ charges interest from the purchase date on a deferred-interest plan whose deferred interest is already billed (undeclared override; unreal baseline).** In force (`pos_deferred_interest` as restated by PPR): the memo "is billed to the balance on the day after promo_end_date and the plan continues … with monthly interest charged from then on". PQ (`overwrite: []`, refs include `pos_deferred_interest`): baseline and the one-span tier run interest "from the purchase date when no monthly interest charge has posted yet". On task 1's seeded world (DI 267.03 billed 2026-10-09 for 04-09..10-08, no `pos_interest_charged` row) PQ computes 219.22 of interest for 04-09..10-12 on top of the billed deferred interest — the promotional period charged twice; base gives interest only from the billing date on (a few days). Charter-level (PQ is not in task 1's tree).
- **R2-6 SOURCE-FACTOR RED — PQ's interest factor reaches outside its bindings; baseline dishonest for promotional plans (XF1/XF3).** The tier "no interest is added, neither since the closing nor for any good-through day" is implemented in the plain binding `hold_interest = 0 if promo_running …`; substituting the factor's baseline leaves the good-through interest at 0, while `baseline.rule` states "plus simple interest … for standard_hold_days days of good-through period". On a DI plan inside its promotion the compute's all-baseline payoff and the baseline.rule payoff differ by two days' interest. Charter-only (task 0 is a reduced-APR plan).
- **R2-7 SOURCE-FACTOR RED — PPR's five rate cuts do not contribute on their own against the baseline (XF1).** The baseline keeps the current payment and APR; a rate cut moves the result only under the re-amortize tier of `reset_payment_method`. Each cut alone with every other factor at baseline returns the current payment (task 1: 155.52 for all five). Bears on task 1.
- **R2-8 SOURCE-FACTOR RED — RIF `large_item_surcharge_rule` scales a returned-payment fee by the size of the returned item (realism; CG-9(c) class).** US returned-payment fees are flat per item (capped at the payment amount); a 5 % / 2 % graduated surcharge on the returned amount is not a published practice. RIF's only method factor → 0 surviving method factors. Bears on task 1 (600.00 return → +15.00).
- **R2-9 SOURCE-FACTOR RED — MGR `make_good_extent_rule` reverses a flat fee in fractions by formula (realism).** "made-good amount divided by the amount that came back" and "grace-period days divided by the days from the due date to the latest make-good payment" — fee reversals for a replaced payment are granted or not; fractional reversal formulas are not a practice any lender publishes. MGR's only method factor → 0 method. Bears on task 0 (amount-ratio tier taken: 30/90).
- **R2-10 SOURCE-POLICY RED — AutoPay enrollment exists only bundled with a payment/APR reset.** In force: "AutoPay can be turned on or off at any time and carries no rate discount, except that a payment reset under this schedule counts the AutoPay debits"; the only write that sets `autopay_enrolled` is `reset_payment_and_autopay_03cef1f2`, which also writes a payment and an APR, and PPR's method tier re-amortizes every reset of a plan that carries a deferred-interest billing entry. On such a plan the base sentence cannot be executed: turning AutoPay on is a contract reset (payment and rate change). Bears on task 1 (demonstrated there as SOURCE-TASK).
- **R2-11 SOURCE-POLICY RED — PPR re-amortizes over fewer payments than the rest of the term.** PPR: "the remaining payments are the term less the whole calendar months from the purchase date to the plan's next due date"; PPR's own restated base: "the plan continues for the rest of its term". When the first due date falls a whole month or more after purchase (purchase 2026-04-09, due day 20 → first due 05-20; next due 10-20 = payment 6), the formula gives 24 − 6 = 18 while 19 payments remain (10-20 through 2028-04-20): the reset ends one month early. Charter-only (task 1's first due date is 25 days after purchase, so the count is right there).
- **R2-12 SOURCE-POLICY RED — PPR's payment-method overwrite drops the activation method (XF4, out-of-scope content not restated).** Retired: "a level payment that repays the financed amount at the plan APR over the term (monthly rate = plan APR divided by 1200) for deferred-interest, reduced-APR and standard plans"; `replaced_by`: "A plan keeps the monthly payment it was set at activation unless a payment reset … sets a new one" — how that activation payment is set for the out-of-scope plans is no longer stated in any rule. Present in revision_1's PPR too and not reported there (miss of revision_1).

Observations: O2-1 CRW←PPR gate is a boolean; O2-2 base courtesy window vs MGR's request-less reversal; O2-3 relationship shares/cuts, hold days and the "behind" tiers as in revision_1 O-8/O-9; O2-4 PQ's credit-still-to-post carve-out (O-5) unchanged.

### closing_checklist (revision_2)

Written after the revision_2 reveal (2026-10-16 12:10:59 UTC); nothing in § revision_2 above was changed by it.

- Both derivations equal GT on every scored write (task 0: 22.10 / 1.47 / 2,209.67; task 1: 20.95 / 107.91 @ 24.24 / 4.75), owners and order; scopes disjoint and complete; uuid8s independent; gates green except pre-publication traceability (unlock names only).
- Closed from revision_1: CG-1, CG-2, CG-5, CG-6, CG-7, CG-8; CG-4's two members; T0-1, T0-2, T1-1 … T1-6 in their revision_1 form.
- Not closed / reopened: CG-3 (new member R2-3), CG-4 class (R2-4), CG-9 (R2-8, R2-9), CG-10 (RIF, MGR, PPR below the bounds).
- New: R2-1, R2-2, R2-5, R2-6, R2-7, R2-10, R2-11, R2-12 (R2-12 was present in revision_1 and missed there).
- Task verdicts: task 0 RED (SOURCE-FACTOR: R2-9); task 1 RED (SOURCE-POLICY: R2-1, R2-10; SOURCE-FACTOR: R2-7, R2-8; SOURCE-TASK: authorisation).
- The difficulty does not pass the source-layer audit; no gate re-run on a final form.

VERDICT revision_2: task0=RED SOURCE-FACTOR task1=RED SOURCE-POLICY+SOURCE-FACTOR+SOURCE-TASK charter=CG-3,CG-9,CG-10,R2-1,R2-2,R2-3,R2-4,R2-5,R2-6,R2-7,R2-8,R2-9,R2-10,R2-11,R2-12

## revision_3

### charter_global_frozen (revision_3)

- Auditor as before; written before any revision_3 GT field was read; nothing here is derived from a revealed GT.
- Entry gate: last line of `worklog.md` is exactly `REWORK round 3: gates 7/7 green`.
- Gate snapshot (`/tmp/erl0067_coord/snapshot.sh practicepay_patient_financing 3`, 2026-10-16T22:14:43): EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; TRACEABILITY NOT OK. The script prints only the verdict line for traceability this round and the coordinator forbade running the check myself, so the kind of its misses was not verified (expected pre-publication; not a finding).
- Frozen inputs: `pos.extended.yaml` sha256 `f0a41858d207bbf0259f0b967b4914ebab7862a2f0452732985d495f07dfe22e`, `task_tools.py` `a2765a87783af6f2247203e2bbf1b6ccce1fffa3b2790cd776e0cc54e2f45837` (both changed → full re-derivation); views `r3/task_0.json` `f7d9cc71…df739`, `r3/task_1.json` `5093027e…bf471`.
- contamination_disclosure: none this round (no tool name or GT field seen before the freeze; claims file read by item id only).
- Base copy: lines 1–1325 identical to `blueprint/products/pos.yaml`.

### policy_conflict_scan (revision_3)

| id | computes | target_tool (owner) | prerequisite |
| --- | --- | --- | --- |
| pos_ext_payoff_quote (PQ) | payment_amount | pay_off_plan_f18fb847 (user) | LFR (state), RFR (state) |
| pos_ext_late_fee_relief (LFR, new) | relief_amount | relieve_late_fee_b1a4bf3c (agent) | [] |
| pos_ext_returned_fee_relief (RFR, new) | relief_amount | relieve_returned_payment_fee_3fbe4785 (agent) | [] |
| pos_ext_late_fee_schedule (LFS) | fee_amount | assess_late_fee_02ab9d3a (agent) | [] |
| pos_ext_returned_item_fee (RIF) | fee_amount | assess_returned_payment_fee_f9ef5ea0 (agent) | LFS (state, same_due_late) |
| pos_ext_payment_reset (PR) | monthly_payment_amount (+ APR) | reset_monthly_payment_233e8b10 (user) | RIF (state, reset_balance) |

Graph LFR→PQ←RFR and LFS→RIF→PR; acyclic. Scope partition derived from the worlds (blind): task 0 = {LFR, RFR, PQ}, task 1 = {LFS, RIF, PR}; disjoint and complete. Conflict found: R3-2 (LFR and RFR draw on one courtesy count).

### rule_compute_equivalence, action_binding_and_uuids, prerequisite_graph (revision_3)

- Sweeps: all `compute_basis`, `baseline.rule`, `replaced_by`, `policy_source` verbatim in their rules; superseded clauses verbatim in base; every binding has a basis; no `CFIELD`; no factor binding reads another factor's binding (XF1); no factor id inside a tool name (XF10); rounding placement matches (XF6).
- LATEST reads all carry the tie rule or are unique by construction (CG-2 stays closed). Loan/FlexLine reads cover every account (CG-1 stays closed).
- Tools: uuid8s f9ef5ea0, 02ab9d3a, f18fb847, b1a4bf3c, 3fbe4785, 233e8b10 — distinct and independent; bodies validate nothing; imports only `erlbench`; docstrings name no other tool, carry no example value; the reset tool writes only payment and APR (AutoPay untouched) — R2-10 closed.
- Edges: all state form; sentences match conditions for PQ←LFR, PQ←RFR, PR←RIF; RIF←LFS does not (R3-1). Each state has one writer (late-fee relief entries name a late-fee entry, returned-fee relief entries name a returned-payment fee entry).
- Remaining-payment count (PR): probes on the four reachable shapes (first due under / over a month after purchase, month-end purchase, 48-month plan) match the plan's actual remaining due dates — R2-11 closed.

### override_declarations (revision_3)

- LFR retires the courtesy-count sentence (real conflict: a waiver without request) and restates it with the make-up reliefs counted; RFR relies on that restated sentence; the window and once-per-fee sentences stay in force and both reliefs apply them. R2-1 / R2-2 closed (no request-free waiver is claimed to be uncounted; no extra gate on the on-request waiver).
- RIF, LFS unchanged; PQ (`overwrite: []`) no longer departs from `pos_deferred_interest` (closing = the deferred-interest billing date when later) — R2-5 closed.
- PR: four declared overwrites, each self-scoped; the payment-method overwrite restates the activation method for every plan type — R2-12 closed.

### factor_ladders (revision_3)

| policy | factors (method in bold) | X |
| --- | --- | --- |
| PQ | **interest_since_closing_rule**, **dispute_carve_out_rule**, return_record_hold, return_reason_hold, personal_loan_return_hold, flexline_return_hold | loan, line |
| LFR | **late_relief_size_rule** (capped / keep-back / whole), late_relief_timing_band, late_relief_autopay_record, late_relief_loan_record, late_relief_flexline_record | loan, line |
| RFR | **returned_relief_size_rule** (capped / keep-back / whole), returned_relief_timing_band, returned_relief_principal_band, returned_relief_loan_record, returned_relief_flexline_record | loan, line |
| LFS | late_record_level, **partial_payment_rule**, late_principal_band, late_fee_loan_record, late_fee_flexline_record | loan, line |
| RIF | returned_item_level, **one_penalty_limit_rule** (one event / capped at the payment / unlimited), returned_fee_balance_band, returned_fee_loan_record, returned_fee_flexline_record | loan, line |
| PR | **reset_payment_method** (re-divide / re-amortize / activation method at the reset rate), five rate cuts | loan, line |

- XF9: every method factor changes shape (CG-8 stays closed). XF1: PQ's good-through accrual is inside its interest factor (R2-6 closed); PR's cuts each move the payment alone against the baseline (R2-7 closed, probe in task 1).
- Realism: the one-penalty limit (one penalty per event, capped at the payment due) is a real form; the item-size surcharge and fractional make-good formula are gone (R2-8, R2-9 closed). New member: PR's third method tier (R3-4). Relationship/record shares, courtesy sizing and hold days remain real forms (observations).
- Counts: PQ 6 (2 M), LFR 5, RFR 5, LFS 5, RIF 5 (1 M each) pass; PR has 0 method factors once R3-4 strikes `reset_payment_method` (CG-10 class).

### findings (revision_3)

Closure of revision_2 items: R2-1, R2-2, R2-3, R2-5, R2-6, R2-7, R2-8, R2-9, R2-10, R2-11, R2-12 closed; CG-3 closed (the make-good reversal is retired; both reliefs require the make-up/replacement to be dated after the fee/return and not returned); CG-9's listed members closed; **R2-4 closed for its member, class reopened by R3-1**; **CG-10 reopened by R3-4**.

New charter-global REDs (each class listed in full):

- **R3-1 SOURCE-POLICY RED — RIF's prerequisite condition demands a late fee no rule can book (CG-4 class; only member).** Sentence: "A returned-payment fee for a payment that was credited toward a monthly due date is set only after the plan's ledger carries the late fee owed for that due date." Condition: when that due date "has passed its grace period with part of that monthly payment unpaid …, a pos_late_fee_assessed entry with that installment_due_date stands". LFS books a late fee only for "the plan's oldest unpaid due date as the plan shows it". World: 09-04 and 10-04 both unpaid past grace, 09-04's late fee already booked, the latest return is the 10-04 payment — LFS owes nothing for 10-04 (the sentence is met vacuously) while the condition waits for a 10-04 late-fee entry no write can produce; RIF and the reset behind it never proceed under the condition. Charter-only (task 1's returned payment is toward the oldest unpaid due date).
- **R3-2 SOURCE-POLICY RED — the two make-up reliefs draw on one courtesy count, and nothing orders them (only member).** LFR's restated sentence: every make-up relief "counts among those courtesy waivers"; both LFR and RFR are owed only "when fewer than the plan's courtesy waivers per 12 months have been granted". On a plan with one courtesy waiver per 12 months (6-Month DI, 6-Month NI, 12-Month DI, 12-Month NI, 24-Month Reduced APR) the first relief booked makes the other not owed, and PQ's two sentences are then both met. Demonstrated on task 0's world with the plan set to the 24-Month Reduced APR Plan: late-fee relief first → 7.31 booked, returned-fee relief 0.00; returned-fee relief first → 8.31 booked, late-fee relief 0.00 — two terminal states and two payoffs. Charter-only (task 0's 48-Month plan allows two).
- **R3-3 SOURCE-POLICY RED — the reliefs' "less the returned payments that reversed payments toward it" reads a field the return event does not write (XF8 exclusion; members: LFR `reversed_toward`, RFR `reversed_toward`).** Compute sums `pos_payment_returned` rows by their own `installment_due_date`; the base event `pos_payment_returned` defines no such field (txn_date, amount, related_txn_id, return_code, payment_channel, bank_account_id); the correct join is through `related_txn_id`. On task 0's world with the 10-06 return row written as the base event defines it and the 10-13 make-up reduced to 20.00, the late-fee relief computes 7.31 (the bounced 116.87 counted as a credit) where the rule gives 0.00. The task worlds seed the field on return rows, so neither task is affected.
- **R3-4 SOURCE-FACTOR RED — PR's fall-through method sets a payment that does not repay the plan (realism; only member).** Tier 3: "any other plan keeps its activation method at the reset rate, its payment being the level payment that repays the financed amount at the reset rate over the term". After a rate cut mid-term this payment ignores the balance and the payments already made: on task 0's plan (48-Month Reduced APR, 14.99 → 12.74, balance 3,924.72, 43 payments left) the reset payment 112.14 leaves 109.43 unpaid after the last scheduled payment — a balloon no lender's re-pricing produces (real re-pricing re-amortizes the balance over the remaining term). Striking this ladder leaves PR without a method factor (CG-10 class). Bears on task 1 (PR is its root; its scored tier is re-amortize).

Observations: O3-1 PQ's split-accrual tier adds back only "that payment's amount" (the one recorded first) — in task 0 two 116.87 payments posted on 10-13, so the closing-to-payment span runs on a balance 116.87 lower than the real one (≈ 1.15 of interest), covered by the good-through excess; O3-2 PQ's clause "the billed deferred interest already covering every earlier day" — billed memo stops at the last memo posting (task 1: 09-13), so 09-14…10-08 is charged nowhere (consistent with the seeded billing; customer-favourable); O3-3 "rounded to the nearest cent" does not state half-cent handling (seeded fee 25 × 0.95 × 0.98 = 23.275 is booked 23.27); O3-4 relationship/record shares, courtesy sizing and hold days as in O2-3; O3-5 after a reset of a past-due plan the record keeps `amount_past_due` from the old payment while the reset schedule counts the past-due due date among its payments.

### closing_checklist (revision_3)

Written after the revision_3 reveal (22:22:21 UTC); § revision_3 above unchanged by it.

- Derivations equal GT on every scored write (task 0: 7.31 / 8.31 / 3,919.28; task 1: 11.37 / 9.58 / 111.11 @ 24.49), owners, order and trees; scopes disjoint and complete; uuid8s independent; gates green except pre-publication traceability (miss kinds not visible this round).
- Closed since revision_2: R2-1, R2-2, R2-3, R2-5 … R2-12, CG-3, CG-9's listed members; T0-R2-1, T1-R2-1 … T1-R2-3.
- Open: R3-1 (CG-4 class), R3-2, R3-3, R3-4 (with CG-10 class: PR has no method factor).
- Task verdicts: task 0 PASS; task 1 RED (SOURCE-FACTOR, via R3-4).
- The difficulty does not pass the source-layer audit (charter REDs open; task 1 RED); no gate re-run on a final form.

VERDICT revision_3: task0=PASS task1=RED SOURCE-FACTOR charter=R3-1,R3-2,R3-3,R3-4

## revision_4

### charter_global_frozen (revision_4)

- Written before any revision_4 GT field was read. Entry gate: last line of `worklog.md` is exactly `REWORK round 4: gates 7/7 green`.
- Gate snapshot (`snapshot.sh … 4`, 2026-10-16T23:37:59): EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; TRACEABILITY NOT OK (verdict line only; pre-publication, per coordinator every miss has been an unlock tool name — not a finding).
- Frozen inputs: `pos.extended.yaml` `79154afa3cca8789e7565326ba81ef63cff79df811bd8f55167e68ba6fdbda45` (changed → moved parts re-derived in full), `task_tools.py` `a2765a87783af6f2247203e2bbf1b6ccce1fffa3b2790cd776e0cc54e2f45837` (unchanged since revision_3 → § action_binding_and_uuids of revision_3 carried by reference on that hash); views `r4/task_0.json` `91375230…c43a`, `r4/task_1.json` `fc2218a0…b05a`. World changes vs revision_3: return rows no longer carry an installment due date; task 0's seeded fee 23.28 (half-up) and balance 3,924.73; task 1's persona asks that "the balance is paid off over the rest of your term".
- contamination_disclosure: none. Base copy verbatim.

### re-derived sections (revision_4)

- Policy set, graph, owners and scope partition unchanged (task 0 {LFR, RFR, PQ}; task 1 {LFS, RIF, PR}); acyclic.
- Sweeps: all quotes/sources/baselines/replaced_by verbatim; superseded clauses verbatim; no XF1 cross-reads; every money rule states "rounded half up to the nearest cent" and computes `int(RND(x·100, 6) + 0.5)/100`; the reset states "rounded up to the next cent" and computes a ceiling (O3-3 closed).
- RIF: the prerequisite sentence and condition are scoped to "the plan's oldest unpaid due date", the one date LFS books; other dates wait on nothing — R3-1 closed.
- LFR/RFR: made-up / replaced now read the plan's next due date and the latest payment toward the due date matched to returns through `related_txn_id`; no due date is read from a return row — R3-3 closed.
- PQ: the split adds every payment entry dated on the latest payment date (O3-1 closed); the closing sentence no longer claims coverage of earlier days (O3-2 closed).
- PR: methods re-divide / principal-and-interest / re-amortize (re-amortize = standard method); the activation-formula tier is gone (R3-4's member closed); the reset leaves the amount past due standing and spreads the rest over the payments after the next due date (O3-5 closed); each rate cut moves the payment alone (task 1 probe).
- Priority for a last courtesy waiver: restated courtesy sentence ("a make-up relief already owed takes it before a request, and a late-fee relief takes it before a returned-payment-fee relief") plus RFR's withholding sentence — the both-orders defect of R3-2 is gone for the case where both reliefs are owed (probe: on a one-waiver plan only the late-fee relief is owed at the start, 7.31; returned-fee relief 0.00).

### findings (revision_4)

Closed: R3-1, R3-3, O3-1, O3-2, O3-3, O3-5; R3-2 and R3-4 for their listed members. Classes reopened: R3-2's (R4-1) and R3-4's / CG-10's (R4-2).

- **R4-1 SOURCE-POLICY RED — the last courtesy waiver can be withheld from both reliefs (R3-2 class; only member).** Restated courtesy sentence: only "a make-up relief already owed" takes the last waiver ahead of others, and "A late-fee relief that works out to 0.00 is not owed". RFR: "When only one courtesy waiver remains … and the plan's latest late fee is still awaiting its late-fee relief, because it carries no waiver entry, the plan's next due date is later than its due date, the latest payment entry … is dated after that fee's assessment date, has not come back and was made at least returned_relief_clearing_days calendar days before today, and today is no later than the fee waiver request window …, that courtesy waiver goes to the late-fee relief and no returned-payment-fee relief is owed." The listed conditions omit "above 0.00". Probe (task 0's world on a one-waiver plan, latest late fee 4.50, one return in 6 months): the late-fee relief works out to 0.00 (keep-back above 5.00) and is not owed; RFR still finds the late fee "awaiting" and withholds — 0.00 / 0.00 — while under the courtesy sentence the returned-fee relief (8.31 there) takes the waiver. Two readings of the same world. Charter-only (task 0 has two waivers).
- **R4-2 SOURCE-FACTOR RED — PR's principal-and-interest tier sets a payment that does not fit the remaining term (R3-4 class; only member) → PR has no method factor again (CG-10 class).** Tier: "the reset balance divided equally over the reset payments plus one month's interest on the reset balance at the reset rate …, a payment that repays the balance by the final due date, the final payment absorbing the difference". A fixed payment equal to the first month's principal-plus-interest overpays every later month as the balance falls: on task 1's world (1,629.85 over 18 payments at 24.49 %) 123.81 retires the balance at the 16th payment (63.25 overpaid there), two due dates before the final one; the level payment for the same 18 is 109.11. The rule's "repays the balance by the final due date, the final payment absorbing the difference" describes a rounding residue, not two whole payments; no lender publishes a fixed payment sized on the first month's interest (real principal-plus-interest payments decline each month). Bears on task 1 (its scored tier).

Observations: O4-1 PQ's split still adds back only payments on the latest payment date (earlier post-closing payments ignored; exact in both worlds); O4-2 relationship/record shares, courtesy sizing and hold days as before.

### closing_checklist (revision_4)

Written after the revision_4 reveal (23:41:30 UTC); § revision_4 above unchanged by it.

- Derivations equal GT on every scored write (task 0: 7.31 / 8.31 / 3,920.45; task 1: 11.37 / 9.58 / 123.81 @ 24.49), trees, owners, order and scopes; gates green except pre-publication traceability.
- Closed since revision_3: R3-1, R3-3, O3-1, O3-2, O3-3, O3-5; R3-2's and R3-4's listed members.
- Open: R4-1 (R3-2 class), R4-2 (R3-4 class; with it CG-10 — PR has no method factor).
- Task verdicts: task 0 PASS; task 1 RED (SOURCE-FACTOR via R4-2; SOURCE-TASK — the scored payment does not fit the term the customer asked for).
- The difficulty does not pass the source-layer audit; no gate re-run on a final form.

VERDICT revision_4: task0=PASS task1=RED SOURCE-FACTOR+SOURCE-TASK charter=R4-1,R4-2

## revision_5

### charter_global_frozen (revision_5)

- Written before any revision_5 GT field was read. Entry gate: last line of `worklog.md` is exactly `REWORK round 5: gates 7/7 green`.
- Gate snapshot (`snapshot.sh … 5`, 2026-10-17T02:05:26): EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; TRACEABILITY NOT OK (verdict line only; pre-publication, not a finding).
- Frozen inputs: `pos.extended.yaml` `cec70c6eb4cfdc2aee50f55e656c5d4a8efa858c2b25f7f7c17955b3fda3988e` (changed: LFR/RFR owed conditions, PR methods and the restated deferred-interest sentence → re-derived in full); `task_tools.py` `a2765a87…5837` (unchanged → tool checks carried by reference); views `r5/task_0.json` and `r5/task_1.json` identical to revision_4's (`91375230…c43a`, `fc2218a0…b05a`) → worlds and personas carried, computations re-run. contamination_disclosure: none. Base copy verbatim.
- Sweeps: every quote/source/baseline/replaced_by verbatim; every binding has a basis; factor counts unchanged (PQ 6/2 M; LFR, RFR, LFS, RIF 5/1 M; PR 6/1 M).

### re-derived sections (revision_5)

- LFR/RFR: owed = cleared make-up/replacement, inside the request window, no prior waiver — no courtesy count; RFR's awaiting condition deleted; the restated courtesy sentence (LFR overwrite) grants make-up reliefs "whatever the number already granted", counts them among courtesy waivers and routes a fee with an owed relief to its schedule. The reliefs no longer share a limit: on task 0's world set to a one-waiver plan both are owed in either order (7.31 and 8.31) — R4-1 closed.
- PR: re-divide (no-interest) / split (deferred interest billed: the billed deferred interest, capped at the reset balance, interest-free in equal parts plus a level payment on the rest) / re-amortize (standard). PR's overwrite of the deferred-interest sentence excludes the unrepaid deferred-interest part from the interest base for reset plans only. Each rate cut moves the payment alone (task 1: 110.31 / 110.71 / 110.71 / 110.91 / 110.91 against the 111.12 baseline). The principal-and-interest tier of R4-2 is gone.

### findings (revision_5)

Closed: R4-1; R4-2's member (the fixed first-month P&I payment); CG-10's reopening (PR keeps a method factor with three amortizing shapes — subject to R5-2 below for the split tier).

- **R5-1 SOURCE-POLICY RED — make-up reliefs are courtesy waivers without any frequency limit (realism; members: LFR and RFR, both under the restated courtesy sentence).** "it is also granted without a request as a make-up relief … whatever the number already granted; every make-up relief is booked on the courtesy basis and counts among those courtesy waivers". The base parameter the plan carries says what that number is: "courtesy_waivers_per_12_months: Courtesy waivers of a late or returned-payment fee per plan in any rolling 12 months (integer)" (1 or 2 by plan). After the rework a plan books courtesy waivers beyond that number every month a customer is late and catches up within the 45-day window — e.g. a 24-Month Reduced APR plan late and made up in each of six months gets six courtesy-basis waivers of each late fee and returned-payment fee while its limit is one. No US lender publishes an unlimited automatic courtesy waiver of every penalty fee that is caught up; the count the parameter defines stops being a limit for the very waivers it counts.
- **R5-2 SOURCE-POLICY RED — PR's split payment repays "with exactly the reset payments" only if the billed deferred interest is repaid in equal parts, which the in-force allocation sentence contradicts (only member).** PR: "Every reset payment method repays the reset balance with exactly the reset payments, the last reset payment taking only the rounding difference"; split tier: the deferred-interest part "divided equally over the reset payments … bears no further interest", and interest runs on the balance "excluding the part of the reset's deferred-interest part not yet repaid". In force, not overwritten (`pos_evt_payments_and_fees`): "Each payment is applied to billed interest and billed deferred interest first, then fees, then the remaining plan balance". Reading A (equal parts): task 1's 18 payments of 106.07 end at −0.19. Reading B (the allocation sentence: each payment pays the remaining billed deferred interest first, interest on the interest-bearing rest): the same 18 payments leave 51.46 owed. The rule's exactness claim and the in-force allocation give different terminal states for the same schedule; PR declares no overwrite of the allocation sentence. Bears on task 1.

Observations: O5-1 PQ's split adds back only payments on the latest payment date (as O4-1); O5-2 relationship/record shares, relief sizing and hold days as before.

### closing_checklist (revision_5)

Written after the revision_5 reveal (02:07:24 UTC); § revision_5 above unchanged by it.

- Derivations equal GT on every scored write (task 0: 7.31 / 8.31 / 3,920.45; task 1: 11.37 / 9.58 / 106.07 @ 24.49); trees, owners, order and scopes unchanged; gates green except pre-publication traceability.
- Closed since revision_4: R4-1, R4-2 (and the CG-10 reopening), T1-R4-1, T1-R4-2.
- Open: R5-1 (unlimited make-up courtesy reliefs; LFR and RFR), R5-2 (split payment vs the in-force allocation order).
- Task verdicts: task 0 PASS; task 1 RED (SOURCE-POLICY via R5-2).
- The difficulty does not pass the source-layer audit; no gate re-run on a final form.

VERDICT revision_5: task0=PASS task1=RED SOURCE-POLICY charter=R5-1,R5-2

## revision_6

### charter_global_frozen (revision_6)

- Written before any revision_6 GT field was read. Entry gate: last line of `worklog.md` is exactly `REWORK round 6: gates 7/7 green`.
- Gate snapshot (`snapshot.sh … 6`, 2026-10-17T03:25:58): EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; TRACEABILITY NOT OK (verdict line only; pre-publication).
- Frozen inputs: `pos.extended.yaml` `7d16261789248c32f30fb27423099693218c52fcc87c04ba182d12bc4fe259c2` (changed: restated courtesy sentence, RFR owed condition, PR overwrite of the payment-application sentence); `task_tools.py` `a2765a87…5837` unchanged; views `r6/task_*` identical to revision_5's → worlds carried, computations re-run. contamination_disclosure: none. Base verbatim; all verbatim sweeps clean; superseded clauses verbatim.

### re-derived sections (revision_6)

- **Courtesy route (R5-1).** Restated sentence (LFR overwrite): make-up reliefs are granted "when fewer than that number have been granted", count among courtesy waivers, and "where only one courtesy waiver remains … the late-fee relief takes it only if a late-fee relief above 0.00 is owed, and otherwise the returned-payment-fee relief takes it". LFR owed: cleared, in window, count < limit, no waiver. RFR owed: the same plus "where only one courtesy waiver remains …, no late-fee relief above 0.00 is owed on the plan's latest late fee"; its compute re-evaluates the late-fee relief in full (`lr_result`). Probed on 16 variants of task 0's world (one- and two-waiver plans; late fee 18.62 or 4.50; one or two returns in 6 months; zero or one prior courtesy waiver): `lr_result` equals LFR's own result in every case, and both booking orders end in the same state in every case — including the 0.00 late-fee relief with one waiver left (returned-fee relief 8.31 takes it). Stated exactly; one end state; the limit binds both reliefs (realism restored). **R5-1 closed.** (An on-request courtesy waiver has no write in this difficulty's tool surface, so request-versus-relief ordering is unreachable.)
- **Allocation (R5-2).** PR declares a self-naming overwrite of "Each payment is applied to billed interest and billed deferred interest first, then fees, then the remaining plan balance": on a reset plan only, each payment goes to its equal share of the deferred-interest part, then interest billed since the reset, then fees, then the balance; every other plan keeps the first order. Under that order the split payment fits the reset payments (task 1: −0.19 after 18). **R5-2 closed.**

### findings (revision_6)

- **R6-1 SOURCE-POLICY RED — readers of the reset plan's balance still charge interest on the interest-free deferred-interest part (class: two members).** In force (PR's restated deferred-interest sentence): on a reset plan "interest then running on the plan balance excluding fees and excluding the part of the reset's deferred-interest part not yet repaid".
  - Member 1, PQ: "The interest-bearing balance is the plan balance less those fees still owed." On task 1's world after its gold reset (balance 1,735.37, deferred-interest part 267.32, fees 11.37 + 9.58), PQ's interest base is 1,714.42 — the 267.32 included — so a payoff quoted that day carries about 2.15 of interest on it (1.97 over the 16 good-through days, the rest in the stub), where the reset rule says it bears none. PQ (`overwrite: []`) states no exception for reset plans.
  - Member 2, PR on a second reset: "the reset's deferred-interest part, which is the deferred interest billed on the plan but never more than the reset balance" — a plan reset again after some equal shares were repaid takes the whole billed amount as interest-free again, not "the part … not yet repaid" its own sentence names.
  - Present since revision_5 (when the interest-free deferred-interest part was introduced) and not reported there — a miss of revision_5. Charter-only: task 0 has no reset; task 1's tree ends at its first reset.

Observations: O6-1 PQ's split adds back only payments on the latest payment date; O6-2 shares, relief sizing and hold days as before.

### closing_checklist (revision_6)

Written after the revision_6 reveal (03:27:47 UTC); § revision_6 above unchanged by it.

- Derivations equal GT on every scored write in both tasks (task 0: 7.31 / 8.31 / 3,920.45; task 1: 11.37 / 9.58 / 106.07 @ 24.49); trees, owners, order, scopes and every factor sensitivity unchanged and re-verified; gates green except pre-publication traceability.
- Closed since revision_5: R5-1 (the coordinator's courtesy route is stated exactly and gives one end state in every probed reachable world), R5-2, T1-R5-1.
- Both task files PASS on all four relationships for revision_6.
- Open charter-wide: R6-1 (reset plan's interest-free deferred-interest part still charged interest by the payoff, and re-counted in full by a second reset; present since revision_5, missed there).
- The difficulty does not pass the source-layer audit while R6-1 is open; no gate re-run on a final form.

VERDICT revision_6: task0=PASS task1=PASS charter=R6-1

## revision_7

### charter_global_frozen (revision_7)

- Written before any revision_7 GT field was read. Entry gate: last line of `worklog.md` is exactly `REWORK round 7: gates 7/7 green`.
- Gate snapshot (`snapshot.sh … 7`, 2026-10-17T03:42:34): EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; TRACEABILITY NOT OK (verdict line only; pre-publication).
- Frozen inputs: `pos.extended.yaml` `820f8e002a91bd8d1c7aac716d438410e1668c3729938650b27096fe1a3a46a2` (changed: PQ interest base on reset plans; PR's once-only window for deferred-interest plans and the split tier's own payment count); `task_tools.py` `a2765a87…5837` unchanged; `r7/task_0.json` identical to revision_6's; `r7/task_1.json` `117ac891af87a7f54642604696273e8df82983b36ea8369c2c83c748904a6647` changed (the 50.00 payment moved from 10-09 to 10-08, persona text to match) → task 1 re-derived in full. contamination_disclosure: none. Base verbatim; all verbatim sweeps and XF1 cross-read sweep clean; superseded clauses verbatim; counts PQ 6/2 M, LFR, RFR, LFS, RIF 5/1 M, PR 6/1 M.

### re-derived sections (revision_7)

- **R6-1 member 1 (PQ).** "The interest-bearing balance is the plan balance less those fees still owed and, on a plan reset to a split payment under the reset schedule, less the reset's deferred-interest part not yet repaid", the unrepaid part being "the deferred interest billed times the reset payments still due divided by the reset payments", still-due counted from the plan's next (oldest unpaid) due date, so a missed payment keeps its share unrepaid. Probe: task 1's world after its gold reset — PQ now excludes 267.32 (interest base 1,447.10). Closed.
- **R6-1 member 2 (second reset).** "A plan whose deferred interest was billed is reset under this schedule only once, only while no payment has posted on it since the billing, and only before the first due date after the billing"; a barred plan "is not reset, and its monthly payment and plan APR stay as they are". Probe: a second reset of task 1's plan after its gold reset is barred (payment and APR unchanged). On a split plan the reset payments are "the due dates after the deferred-interest billing date through the final due date". Closed.
- R6-1 class: the only interest-running policies are PQ and PR (and base statement interest, restated by PR); the fee and relief schedules read balances only for bands. Closed.

### findings (revision_7)

- **R7-1 SOURCE-POLICY RED — the general reset count removes one payment however many installments are past due (class: one sentence, used by the re-divide tier and by the re-amortize tier, which is also the standard method).** "The reset balance is the plan balance, fees owed included, less the plan's amount past due, which stays due as it stands; the reset payments are the remaining payments, less the next due date's payment when the plan has an amount past due, never fewer than one, and the reset payment applies from the first due date among them." With two installments past due, the balance leaves out both but the count leaves out one: the first reset payment falls on the second past-due due date, which the standing past-due amount already covers. Probe on task 0's 48-month plan with 09-10 and 10-10 unpaid (past due 233.74): 44 reset payments of 112.12 against 43 due dates after 10-10 — 110.53 is left after the final due date (or 10-10 is charged twice). The rule's own "Every reset payment method repays the reset balance with exactly the reset payments" fails there. The split tier counts from the billing date and is not affected; neither task world has two installments past due (charter-only). Present since revision_4 (O3-5's fix) and missed in revisions 4–6.

Observations: O7-1 a reset leaves no ledger record — PQ and PR recognise a reset plan by its monthly payment differing from the activation payment, which a reset that happened to land on the activation figure would defeat (coincidence only); O7-2 a barred reset "is not reset" while the compute returns the current payment (no write is the reading the rule gives); O7-3 PQ's unrepaid share moves only when the oldest unpaid due date advances, so a partial payment that the reset allocation sends to the deferred-interest share is not credited until the installment is complete; O7-4 shares, relief sizing, hold days as before.

### closing_checklist (revision_7)

Written after the revision_7 reveal (03:45:04 UTC); § revision_7 above unchanged by it.

- Derivations equal GT on every scored write (task 0: 7.31 / 8.31 / 3,920.45; task 1: 11.37 / 9.58 / 106.07 @ 24.49); trees, owners, order, scopes and sensitivities re-verified; gates green except pre-publication traceability.
- Closed since revision_6: R6-1 (both members and the class).
- Both task files PASS on all four relationships for revision_7.
- Open charter-wide: R7-1 (general reset count with two or more installments past due; present since revision_4, missed until now).
- The difficulty does not pass the source-layer audit while R7-1 is open; no gate re-run on a final form.

VERDICT revision_7: task0=PASS task1=PASS charter=R7-1

## revision_8

### charter_global_frozen (revision_8)

- Written before any revision_8 GT field was read. Entry gate: last line of `worklog.md` is exactly `REWORK round 8: gates 7/7 green`.
- Gate snapshot (`snapshot.sh … 8`, 2026-10-17T04:26:50): EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; TRACEABILITY NOT OK (verdict line only; pre-publication).
- Frozen inputs: `pos.extended.yaml` `a1471296cca98aeaae807b3639e8a6d403f4d24dfb84f27082207e4e2154db0b` (changed: PR's past-due count, reset recognition by payment or APR, no-change / refused reset = 0.00 and no write; PQ's recognition); `task_tools.py` `a2765a87…5837` unchanged; views `r8/task_*` identical to revision_7's → worlds carried, computations re-run. contamination_disclosure: none. Base verbatim; verbatim and XF1 sweeps clean; superseded clauses verbatim; counts unchanged (PQ 6/2 M; LFR, RFR, LFS, RIF 5/1 M; PR 6/1 M).

### re-derived sections (revision_8)

- **R7-1.** PR: "the reset payments are the remaining payments when the plan has no amount past due and, when it has one, the due dates after the latest due date before today, every installment due before today staying in the amount past due and an installment due today counting among the reset payments". The compute's due-date count was checked against an independent calendar count over purchase dates 2026-04-20 / 2026-01-31 / 2025-12-05 / 2026-02-28, due days 1 / 10 / 20 / 28, next due dates 0–2 months back and three reset dates — 0 mismatches. Probe of revision_7 (task 0's plan with 09-10 and 10-10 past due): now 43 reset payments of 114.17, ending at −0.45 (rounding) after the final due date. Closed; the sentence serves re-divide, re-amortize and the standard method alike; the split tier keeps its billing-date count.
- **O7-1 / O7-2.** PQ and PR recognise a reset plan by a monthly payment *or* plan APR different from the plan's own, and "a reset that would leave both the monthly payment and the plan APR as they are makes no change and is not made", so recognition cannot miss a made reset; a refused or no-change reset "is 0.00 and nothing is written", matching the compute (probe: a second reset of task 1's plan → 0.00). Closed.
- XF recipe re-checked on PQ and PR (the moved policies): XF1–XF14 no member (rounding half up / ceiling stated and implemented; LATEST tie rules; absent-record and negative-span guards; no factor id in a tool name; docstrings unchanged).

### findings (revision_8)

- No charter-global RED open. Closed since revision_7: R7-1, O7-1, O7-2.
- Observations (no RED; no reading of a scored value differs): O8-1 PQ defines the unrepaid deferred-interest part by its own schedule proxy (due dates still due from the oldest unpaid one), so a partial payment that the reset allocation sends to a deferred-interest share is reflected only when the installment completes — PQ's definition is explicit and the good-through days carry the cents (was O7-3); O8-2 PQ's split adds back only payments on the latest payment date; O8-3 relationship/record shares, relief sizing and hold days are real forms.

### closing_checklist (revision_8)

Written after the revision_8 reveal (04:28:46 UTC); § revision_8 above unchanged by it.

- Per-task files `task_0.md`, `task_1.md` sit beside this file; revisions 1–8 are appended in order, older text untouched; both revision_8 comparison sections carry PASS on all four relationships.
- Scopes: task 0 = {pos_ext_late_fee_relief, pos_ext_returned_fee_relief, pos_ext_payoff_quote}, task 1 = {pos_ext_late_fee_schedule, pos_ext_returned_item_fee, pos_ext_payment_reset} — pairwise disjoint, jointly complete over the six extended policies and six task tools; uuid8s independent and frozen (tool module unchanged since revision_3).
- Trees: each has two prerequisite problems, two value_input edges, an `owner=user` root (payoff; reset) and no cycle; the difficulty graph (LFR→PQ←RFR, LFS→RIF→PR) is acyclic.
- Factors: every computation has five or six factors with at least two parameters and one shape-changing method factor; each task has multi-source and cross-difficulty (loan, FlexLine) factors; every factor bears weight against an honest baseline; every whole-baseline number is definite and differs from gold.
- Derivations equal GT on every scored write (task 0: 7.31 / 8.31 / 3,920.45; task 1: 11.37 / 9.58 / 106.07 @ 24.49).
- Gates on the final form: the coordinator's revision_8 snapshot (2026-10-17T04:26:50) is the re-run on this form — all instantiation gates OK; traceability not OK pre-publication only (the coordinator re-checks it after rendering).
- No charter-global RED is open; observations O8-1 … O8-3 remain recorded.
- The difficulty passes the source-layer audit at revision_8.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

### charter_global_frozen (revision_9)

- Written before any revision_9 GT field was read. Inputs to verify: renderer source scan `audits/render_source/practicepay_patient_financing/render_r1.md` (D1–D6) and `rework_r9_claims.md` (ids only). Entry gate: last line of `worklog.md` is exactly `REWORK round 9: gates 7/7 green`.
- Gate snapshot (`snapshot.sh … 9`, 2026-10-17T13:34:48): EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; TRACEABILITY NOT OK (verdict line only; pre-publication).
- Frozen inputs: `pos.extended.yaml` `58f6c0be86cadb7cde5311a6f4eeda7a74045e79e9c0d78133da2f6748d46b08` (changed); `task_tools.py` `a2765a87…5837` unchanged; views `r9/task_*` identical to revision_8's. contamination_disclosure: none. Base verbatim; verbatim / basis / XF1 sweeps clean; every declared param of every policy is used by its compute and named in its rule; superseded clauses verbatim; counts unchanged (PQ 6/2 M; LFR, RFR, LFS, RIF 5/1 M; PR 6/1 M).

### re-derived sections (revision_9)

- **D1.** RFR no longer recomputes the late-fee relief and no longer carries its constants (its params are its own fifteen). It now has a prerequisite on LFR — "A returned-payment-fee relief is set only after the plan's ledger carries the late-fee relief owed on the plan's latest late fee, which takes a last remaining courtesy waiver first when it is above 0.00." (state form, `state_gate`, gate `courtesy_12m`; condition "When a late-fee relief above 0.00 is owed on the plan's latest pos_late_fee_assessed entry …, a pos_fee_waived entry names that late-fee entry"; sentence and condition match; one writer). Its owed test is the plain courtesy limit. Graph now LFR→RFR, LFR→PQ, RFR→PQ, LFS→RIF→PR; acyclic. Re-probed on the 16-world grid of revision_6 with the late-fee relief booked first as the edge requires: one end state in every case, including the 0.00 late-fee relief with one waiver left (returned-fee relief 8.31). Closed with its class (no other policy recomputes another's factors: XF1 / param sweep clean).
- **D2.** LFS late-fee level: "a late fee dated within the last 6 months" / "no late fee dated within the last 12 months" / "a late fee dated within the last 12 months but none within the last 6 months", with the whole-month window in the same sentence — a partition. Probes: a prior late fee exactly 6 whole months back → 27.00 (tier 3), exactly 12 → 20.00 (tier 2). Every other three-tier ladder of the charter re-checked for gaps/overlaps (RIF item level, LFR/RFR size, timing and principal bands, loan/FlexLine records and holds, PQ return holds, PR record/AutoPay/paydown cuts): each is a partition. Closed with its class.
- **D3.** Every factor that needs a month window or a day span now carries the convention in its own sentence; the remaining convention sentences outside factors serve non-factor quantities only (PQ's daily-rate span sentence; LFR's and RFR's courtesy-count window); no baseline carries an unused window sentence. Closed with its class.
- **D4.** PR's `reset_payment_method` owns `interest_free_part` and `method_payments`; the payment is assembled by one generic binding (interest-free part over the method payments plus a level payment on the rest), stated once. Closed.
- **D5.** "only while no payment dated on or after the billing date has posted on it" ↔ `last_pay_date >= di_bill_date`; probe: task 1's 50.00 moved onto the billing date bars the reset (0.00). Closed.
- **D6.** RIF's one-penalty sentence carries the grace-period definition its `within_grace` uses; the "decided once that due date's grace period has ended" sentence relies on the base grace definition (`pos_evt_payments_and_fees`), which is in force. Closed.

### findings (revision_9)

- No charter-global RED open (D1–D6 closed with their classes; nothing from revision_8 regressed).
- Observations: O9-1 RFR's new edge is labelled `state_gate` with gate `courtesy_12m`, a compute binding rather than an eligibility gate id (extended policies declare no eligibility blocks; the binding is the state the edge waits on); O9-2 the new edge is a pure ordering gate that changes RFR's value only on a plan with one courtesy waiver left (see task 0); O8-1 … O8-3 unchanged.

### closing_checklist (revision_9)

Written after the revision_9 reveal (13:36:53 UTC); § revision_9 above unchanged by it.

- Derivations equal GT on every scored write (task 0: 7.31 / 8.31 / 3,920.45; task 1: 11.37 / 9.58 / 106.07 @ 24.49) and on both trees.
- Renderer findings D1–D6 closed with their classes; nothing from revision_8 regressed in the charter.
- Task 0 RED: the D1 rework added RFR→LFR to task 0's tree, and in task 0's world (two courtesy waivers, none used) that edge bears no weight (T0-R9-1; GT's own closure says "8.31 either way"). Task 1 PASS.
- No charter-global RED open.
- The difficulty does not pass the source-layer audit while task 0's tree carries a decorative edge; no gate re-run on a final form.

VERDICT revision_9: task0=RED SOURCE-CHAIN task1=PASS charter=CLEAN

## revision_10

### charter_global_frozen (revision_10)

- Written before any revision_10 GT field was read. Entry gate: last line of `worklog.md` is exactly `REWORK round 10: gates 7/7 green`.
- Gate snapshot (`snapshot.sh … 10`, 2026-10-17T13:41:30): EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; TRACEABILITY NOT OK (verdict line only; pre-publication).
- Frozen inputs: `pos.extended.yaml` `350171099f68b934664b521ba8560f10820bad5ef8feccf640e59084148b3e81` (changed: RFR's size factor and its edge to LFR); `task_tools.py` unchanged; views `r10/task_*` identical to revision_9's. contamination_disclosure: none. Base verbatim; verbatim / basis / XF1 / param sweeps clean; counts unchanged.

### re-derived sections (revision_10)

- RFR → LFR edge is now `value_input` (gate `same_due_late_relieved`): RFR's size reads whether the late fee of the same due date already carries a waiver. Sentence and condition unchanged and matching; one writer. The renderer classes stay closed: RFR recomputes nothing of LFR (it reads only the waiver entry LFR's write leaves), carries only its own params, keeps its window/span conventions in its factor sentences; the courtesy grid of revision_9 still ends in one state per world.
- New size ladder (`returned_relief_size_rule`, method): tier 1 "the late fee of the due date the payment that came back was credited toward already carries a waiver entry" → capped: the fee, never more than returned_relief_cap_usd (12.00); tier 2 "that late fee carries no waiver entry, or no late fee names that due date but a late fee on the plan within the last 6 months" → keep-back: the fee above returned_relief_keep_usd (5.00); tier 3 → whole. The rule gives tier 1's reason: "so that the same missed payment has been relieved once".

### findings (revision_10)

- **R10-1 SOURCE-FACTOR RED — RFR's size ladder gives the larger relief to the event already relieved once, at the plan's own standard fee levels (unreal ladder; only member).** Capped (≤ 12.00) and keep-back (fee − 5.00) cross at a 17.00 fee, so for every returned-payment fee up to 17.00 the "already relieved once" tier relieves more than the tier whose late fee was not relieved — the opposite of the restraint the rule states as tier 1's reason. Probe on task 0's world (same shares 0.9 × 0.9 × 0.9 × 0.95): fee 15.00 (the standard returned_payment_fee_usd) → 8.31 when the same event's late fee was relieved, 6.93 when it was not; fee 10.00 (first_item_fee_usd) → 6.93 vs 3.46; only at 23.28 does the order run the stated way (8.31 vs 12.66). No lender's courtesy schedule hands a bigger second relief to the customer who already got the first. RFR's only method factor is struck → RFR has no surviving method factor (CG-10 class). New this revision (the tier-1 condition was introduced by the T0-R9-1 rework).
- Observations unchanged (O8-1 … O8-3, O9-1 now moot: the edge is `value_input`).

### closing_checklist (revision_10)

Written after the revision_10 reveal (13:43:04 UTC); § revision_10 above unchanged by it.

- Derivations equal GT on every scored write and on both trees (task 0: 7.31 / 8.31 / 3,920.45; task 1: 11.37 / 9.58 / 106.07 @ 24.49).
- Closed: T0-R9-1 (every edge of task 0's tree now bears weight). Renderer classes D1–D6 remain closed; nothing else regressed.
- Open: R10-1 (returned-fee relief size ladder inverted at the standard fee levels; strikes that policy's only method factor) → task 0 RED SOURCE-FACTOR; task 1 PASS.
- The difficulty does not pass the source-layer audit while R10-1 is open.

VERDICT revision_10: task0=RED SOURCE-FACTOR task1=PASS charter=R10-1

## revision_11

### charter_global_frozen (revision_11)

- Written before any revision_11 GT field was read. Entry gate: last line of `worklog.md` is exactly `REWORK round 11: gates 7/7 green`.
- Gate snapshot (`snapshot.sh … 11`, 2026-10-17T14:41:20): EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; TRACEABILITY NOT OK (verdict line only; pre-publication).
- Frozen inputs: `pos.extended.yaml` `823f0adef71561b1a966c4e0913ebe8fd841c24f9d02ad04b71dd19802a46a89` (changed: the size ladders of RFR and LFR); `task_tools.py` unchanged; views `r11/task_*` identical to revision_10's. contamination_disclosure: none. Base verbatim; verbatim / basis / XF1 / param sweeps clean; counts unchanged.

### re-derived sections (revision_11)

- **R10-1 (RFR).** Tier 1 (the same due date's late fee already relieved): "the part of the returned-payment fee above returned_relief_keep_usd, never below 0.00 and never more than returned_relief_cap_usd"; tier 2: the keep-back without the cap; tier 3: the whole fee. Tier 1 ≤ tier 2 ≤ tier 3 for every fee. Probes on task 0's world (same shares): fee 10.00 → 3.46 / 3.46; 15.00 → 6.93 / 6.93; 18.00 → 8.31 / 9.00; 23.28 → 8.31 / 12.66 (relieved / unrelieved). Tiers 1 and 2 agree up to a 17.00 fee and differ above it — a reachable distinguishing input (the repeat level 25.00 × shares; task 0's 23.28), so they are distinct method shapes (cap vs no cap). The task 0 edge still moves the value (12.66 → 8.31). Closed.
- **R10-1 class (LFR).** The late-fee relief's ladder carried the same inversion in revision_10 — two or more returns gave "the late fee but never more than late_relief_cap_usd" against one return's keep-back, so for late fees up to 15.00 the worse record got the larger relief — and revision_10 did not list it (a miss of revision_10). It now reads "the part of the late fee above late_relief_keep_usd, never below 0.00 and never more than late_relief_cap_usd" for two or more returns. Probes: fee 10.00 → 3.66 / 3.66; 15.00 → 7.31 / 7.31; 18.62 → 7.31 / 9.96; 30.00 → 7.31 / 18.28 (two returns / one return). Closed.
- **Every other ladder** re-checked for direction against its rule: timing (slower → less relief), AutoPay (fewer debits → less), loan / FlexLine records (late fee < returned payment < clean, for reliefs; the reverse for fees), fee levels (repeat > standard > first), balance / principal bands, payoff hold days (more risk → more days), reset cuts (better record / more paydown / more AutoPay → larger cut): each monotone in the direction its rule states. The returned-fee relief's principal band (higher principal → smaller share) is a stated design choice, not an inversion.
- Courtesy grid of revision_6/9 re-run under the new ladders (late-fee relief first, as the edge requires): one end state in every world.

### findings (revision_11)

- No charter-global RED open (R10-1 and its class closed; D1–D6 stay closed; nothing regressed).
- Observations unchanged (O8-1 … O8-3).

### closing_checklist (revision_11)

Written after the revision_11 reveal (14:42:42 UTC); § revision_11 above unchanged by it.

- Per-task files `task_0.md`, `task_1.md` beside this file; revisions 1–11 appended in order, older text untouched; both revision_11 comparison sections carry PASS on all four relationships.
- Scopes: task 0 = {late-fee relief, returned-fee relief, payoff}; task 1 = {late-fee schedule, returned-item fee, payment reset} — disjoint, jointly complete over the six extended policies and six task tools; uuid8s independent and frozen (tool module unchanged since revision_3).
- Trees: task 0 LFR→RFR, LFR→PQ, RFR→PQ (three value_input edges, two prerequisite problems, user root); task 1 LFS→RIF→PR (two value_input edges, user root); every edge bears weight; the difficulty graph is acyclic.
- Factors: every computation has five or six factors with ≥ 2 parameters and ≥ 1 shape-changing method factor; every ladder is a partition, monotone in the direction its rule states; each task has multi-source and cross-difficulty (loan, FlexLine) factors; every factor bears weight against an honest baseline; whole-baseline numbers definite and ≠ gold.
- Derivations equal GT on every scored write (task 0: 7.31 / 8.31 / 3,920.45; task 1: 11.37 / 9.58 / 106.07 @ 24.49).
- Renderer findings D1–D6 closed with their classes; R10-1 and its class closed (the revision_10 miss on the late-fee relief's ladder is recorded above).
- Gates on the final form: the coordinator's revision_11 snapshot (2026-10-17T14:41:20) — all instantiation gates OK; traceability not OK pre-publication only (re-checked by the coordinator after rendering).
- No charter-global RED open; observations O8-1 … O8-3 recorded.
- The difficulty passes the source-layer audit at revision_11.

VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN

## revision_12

### charter_global_frozen (revision_12)

- Written before any revision_12 GT field was read. Inputs to verify: the KB audit's source list `audits/policy_kb/practicepay_patient_financing/1.md` S2, S3, S4 (S1 excluded by coordinator decision) and `rework_r12_claims.md` (ids only); only the S-items of the KB audit were read. Entry gate: last line of `worklog.md` is exactly `REWORK round 12: gates 7/7 green`.
- Gate snapshot (`snapshot.sh … 12`, 2026-10-17T19:09:20): EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING, SCOPE, TRACEABILITY all OK.
- Frozen inputs: `pos.extended.yaml` `2920d0573e23e7b701526ae5972ada210129d33ba86b52faa0c6653b60c83cc9` (changed: wording in PQ, RIF, LFR, RFR); `task_tools.py` unchanged; views `r12/task_*` identical to revision_11's. contamination_disclosure: none beyond the KB audit's S2 line, which names the two candidate payoffs of task 0 (3,920.45 / 3,919.39) — both already known from my own revisions. Base verbatim; verbatim / basis / XF1 / param sweeps clean; superseded clauses verbatim; counts unchanged.

### re-derived sections (revision_12)

- **S2 (PQ, order of a non-commuting deduction — XF2).** Added to the carve-out sentence: "the amount left out is subtracted from the payoff amount only, the interest-bearing balance and the interest it carries staying as they are" — the one reading the compute implements (task 0: interest base 3,909.11 with the 60.00 credit still to post outside it → 3,920.45; the other reading, 3,919.39, is now excluded by text). This was an XF2 member present since revision_2 that my revisions missed. Class sweep — every other combination of deductions with a base: LFS (unpaid part = smaller of the monthly payment and the past due less open disputes; product capped at the unpaid part), RIF (level × shares, then the one-penalty limit, then the cap at the amount returned, one rounding), LFR / RFR (size × shares, capped at the unwaived part), PR (reset balance less the past due; interest-free part capped at that reset balance; cuts → reset rate; payment rounded up), PQ's interest base (fees still owed and the unrepaid deferred-interest part, the latter capped at the balance less those fees): each order stated in its rule. Closed with its class.
- **S3 (RIF).** The scope sentences now read "… set only after the plan's ledger carries the late fee owed for that due date" and "A returned-payment fee for a payment credited toward a due date that is not the plan's oldest unpaid due date waits on no late fee."; the standing-late-fee reading lives only in the one-penalty factor's sentence ("a late fee for that due date still stands on the plan after any waiver of it"). Closed.
- **S4 (LFR / RFR).** The restated courtesy sentence (LFR's overwrite) no longer states the priority between the reliefs; the priority sits on the waiting side, in RFR's rule ("Where only one courtesy waiver remains … the late-fee relief takes it only if one above 0.00 is owed on the plan's latest late fee, and otherwise the returned-payment-fee relief takes it") and in its prerequisite sentence. LFR's rule carries only its own content. Courtesy grid re-run: one end state in every world. Closed with its class (no depended-on rule of the charter states anything about the policy that waits on it: LFS, RIF, LFR checked).

### findings (revision_12)

- No charter-global RED open (S2–S4 closed with their classes; D1–D6 and R10-1 stay closed; nothing regressed).
- Observations unchanged (O8-1 … O8-3).

### closing_checklist (revision_12)

Written after the revision_12 reveal (19:10:53 UTC); § revision_12 above unchanged by it.

- Both revision_12 comparison sections PASS on all four relationships; derivations equal GT on every scored write (task 0: 7.31 / 8.31 / 3,920.45; task 1: 11.37 / 9.58 / 106.07 @ 24.49), trees and sensitivities.
- Scopes, trees, factor floors and the acyclic difficulty graph as recorded in revision_11's checklist, unchanged.
- KB-audit source items S2, S3, S4 closed with their classes (S2 was an XF2 member these audits had missed since revision_2); renderer D1–D6 and R10-1 stay closed.
- Gates on the final form: the coordinator's revision_12 snapshot (2026-10-17T19:09:20) — all eight gates OK, traceability included.
- No charter-global RED open; observations O8-1 … O8-3 recorded.
- The difficulty passes the source-layer audit at revision_12.

VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN

## revision_13

### charter_global_frozen (revision_13)

- Written before any revision_13 GT field was read. Seed-only rework for the KB re-judge's cross-product seed items X1–X4 (`audits/policy_kb/practicepay_patient_financing/1.md`, revision_3; only its X-items were read). Entry gate: last line of `worklog.md` is exactly `REWORK round 13: gates 7/7 green`.
- Gate snapshot (`snapshot.sh … 13`, 2026-10-17T21:07:24): all eight gates OK, traceability included.
- Byte identity: `pos.extended.yaml` `2920d0573e23e7b7…` and `task_tools.py` `a2765a87783af6f2…` — unchanged since revision_12, so every charter-global section of revision_12 (and the D1–D6 / R10-1 / S2–S4 closures) is carried by reference on these two hashes. Views changed: `r13/task_0.json` `19fa26c6…0428b`, `r13/task_1.json` `329420a6…0b13`; frozen times and personas unchanged; no `pos_*` row changed in either world. contamination_disclosure: none (the X-items quote scored values I had already derived).
- What moved (row diff r12 → r13): FlexLine — returned-payment fee rows 15.00 → 2.12 and their replacement payments 115.00 → 102.12, every interest charge, outstanding balance and minimum payment; Personal Loans — late fee rows 10.00 → 9.00 with the matching fee-payment amounts (task 0's 2025-08-12 payment 342.52 → 341.52), task 1's scheduled payment 326.06 → 326.05 in every installment row with re-split interest / principal portions and principal balance 5,172.22, a 9.00 fee-payment line on 2025-06-03 added and the 2025-06-05 courtesy waiver removed.

### seed verification (revision_13) — every seeded row against its owning rules

- **FlexLine (docs/line).** Replay of each line ledger under "Interest is charged at each statement closing on the average daily balance of the cycle (draws accrue from the draw date …) times the APR divided by 365 times the days in the cycle, rounded to the cent": 19 (task 0) and 17 (task 1) interest rows, 0 mismatches; replayed outstanding balances 1,405.35 / 1,710.64 equal the seed; minimum payment 3 % of the balance (42.16 / 51.32) equals the seed. Returned-payment fee per "How the FlexLine Returned-Payment Fee Is Figured" (R01 below 1,000.00 → 2.5 % of 100.00 = 2.50, never more than the tier fee) × return-history share 0.85 ("the only return in the last 24 months"), other shares 1 → 2.125, "an exact half cent to the even cent" → 2.12 = the seed (X1 closed); replacement 102.12 = 100.00 + 2.12.
- **Personal Loans (docs/loan).** Replay under "Interest accrues daily as simple interest on the unpaid principal … actual/365 …" and "accrued interest, then unpaid fees (oldest fee first, each as its own fee payment line), then principal": every payment's interest / principal portions match (0 mismatches in both loans), replayed principal 5,443.33 / 5,172.22 equals the seed, no unpaid fee left. Late fees: schedule C flat 10.00 × first-late share 0.9 ("no late fee in that time and fewer than 12 such payments") = 9.00 in both loans (X2 closed), paid by the next payment (task 0 341.52 = 332.52 + 9.00; task 1's 2025-06-03 line of 9.00, X3 closed — no courtesy waiver of an already-paid fee remains). Task 1 scheduled payment: 12,500.00 at 11.49/1200 over 48 = 326.0516 → 326.05 (X4 closed); task 0's 332.5184 → 332.52 unchanged.
- **PracticePay (own rows).** Unchanged since revision_12; their consistency checks of revisions 3–12 (late fee 18.62, returned-payment fees 8.82 / 23.28, interest postings, deferred-interest memo and billing) stand.

### re-derived sections (revision_13)

- Cross-product reads that the moved rows feed: loan late fees within 12 / 6 months (counts only — both loans' late fees lie outside every window: 2025-08-09 is 14 whole months before task 0's 2026-10-16, 2025-05-31 is 16 before task 1's 2026-10-15), loan returns (2026-08-27; 2026-02-18 — unchanged), FlexLine returns and late fees (2026-06-18; 2026-04-14; no FlexLine late fee — unchanged). No policy reads a FlexLine fee amount, a loan fee amount, a loan courtesy waiver or a FlexLine interest amount. Every tier is therefore unchanged; re-run confirms every value, skip figure and sensitivity (task 0: 7.31 / 8.31 / 3,920.45, RFR 12.66 before the late-fee relief, skips 3,923.46 / 3,928.90, opening 3,936.34; task 1: 11.37 / 9.58 / 106.07 @ 24.49, skips 12.57 / 105.43).
- Prerequisites still unmet at the opening (no `pos_*` row moved): task 0 — late fee `d1186249` carries no waiver, fee `aa692538` carries no waiver; task 1 — no late fee for 10-04 (grace ended 10-14), no fee on return `c09e564c`.

### findings (revision_13)

- No charter-global RED open; X1–X4 closed; nothing regressed.

### closing_checklist (revision_13)

Written after the revision_13 reveal (21:09:33 UTC); § revision_13 above unchanged by it.

- Charter and tool module byte-identical to revision_12 (`2920d0573e23e7b7…`, `a2765a87783af6f2…`); revision_12's charter-global conclusions carried on those hashes.
- Every seeded row of both worlds — PracticePay, Personal Loans and FlexLine — is what its owning rules produce (replays above); X1–X4 closed.
- Both tasks: prerequisites unmet at the opening, every edge and factor bearing weight, derivations equal GT on every scored write (task 0: 7.31 / 8.31 / 3,920.45; task 1: 11.37 / 9.58 / 106.07 @ 24.49); proof text free of stale sibling claims; both comparison sections PASS on all four relationships.
- Gates on the final form: the revision_13 snapshot (2026-10-17T21:07:24) — all eight gates OK.
- No charter-global RED open. The difficulty passes the source-layer audit at revision_13.

VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN
