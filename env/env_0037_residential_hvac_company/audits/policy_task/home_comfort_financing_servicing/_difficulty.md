# Policy-task audit — home_comfort_financing_servicing / charter-global

## charter_global_frozen

- Freeze time: 2026-10-05T15:48:55Z (file mtime; written before any task's GT was revealed; contains nothing derived from a revealed GT).
- Auditor: erl-task-policy-audit (independent of the instantiation author; no answers were supplied with the brief).
- Freeze hashes (match `/tmp/erl37/views/home_comfort_financing_servicing/charter.sha256`):
  - `finance.extended.yaml` 37be8a42fb7763c34ab8fc788ee55166b5ed88fe39c6f5ac4b20a04bfd4f07f1
  - `task_tools.py` 44f740be87ab5843e42de2b1ee86f68af60db9a3d2e416f56c0411fbaaef0be9
  - masked views `task_0.masked.json` 1f1a435c…13a1, `task_1.masked.json` 899b5a65…a409ea41 (recomputed, match).
- Fields read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py` (signatures), `blueprint/products/finance.yaml`, `blueprint/products/plan.yaml` (lifecycle/field names only, for the cross-difficulty reads), `tasks/home_comfort_financing_servicing/finance.extended.yaml`, `task_tools.py`, the masked views (frozen_time, user_scenario, initial_state), and the compute DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/within_months/CFIELD/RND).
- Fields masked and unread: everything in `tasks/*.json` other than the three view fields (evaluation_criteria, computations, db_closure, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure); `env/env_0037_residential_hvac_company/worklog.md` was not opened. No search ran over `tasks/` or `env/`.
- Entry conditions (Step 0): gate snapshot `/tmp/erl37/gates/home_comfort_financing_servicing.snapshot.txt` present — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; masked views and hashes present. Input complete.

### policy_conflict_scan

Base copy: lines 1–1265 of `finance.extended.yaml` are byte-identical to `blueprint/products/finance.yaml` (`diff` empty, 1265 lines each).

Six extended policies, each with a distinct target tool and a distinct subject/quantity:

| policy | subject | computes | target_tool | owner | prerequisite |
| --- | --- | --- | --- | --- | --- |
| finance_ext_late_fee_schedule | finance_statement_charge (late_fee) | amount | post_late_fee_ce58c754 | agent | [] |
| finance_ext_post_promo_interest | finance_statement_charge (interest, promotional plans after promo end) | amount | post_post_promo_interest_b0f5a17d | agent | [] |
| finance_ext_payoff_figure | finance_payment, finance_payoff | amount | submit_payoff_payment_45ecd350 | user | late fee (value_input), post-promo interest (value_input) |
| finance_ext_fixed_rate_interest | finance_statement_charge (interest, interest_rate_type fixed) | amount | post_fixed_rate_interest_d84dbec7 | agent | [] |
| finance_ext_makeup_payment | finance_payment | amount | submit_makeup_payment_e9bd505b | user | fixed-rate interest (state_gate) |
| finance_ext_returned_payment_fee | finance_statement_charge (returned_payment_fee) | amount | post_returned_payment_fee_928f04f0 | agent | make-up payment (value_input) |

Overlaps examined:
- The two interest policies share line_type `interest` but have disjoint scopes by plan: post-promo applies "On a promotional plan whose promotion has ended"; fixed-rate "On a plan whose interest_rate_type is fixed" (promotional plans carry `interest_rate_type: promotional`). No account is in both scopes. Compatible.
- Payoff and make-up both post a `payment`; their triggers differ ("pays the account off in full" vs "brings a missed or returned installment up to date") and their terminal states differ (paid_off vs open). Compatible.
- Late fee / returned-payment fee: separate line types, separate base sentences, separate overwrite entries. The base sentence "a returned payment also leaves the payment it replaced unpaid, so a late fee may follow if the grace period then passes" is consistent with both.
- Shared reliefs: member (plan), account-age and payment-record reliefs recur with policy-specific percentages; each is stated in its own policy's rule under its own name ("late-fee member relief", "post-promotional member relief", ...). The payoff reliefs on a post-promo account use the same percentages as the post-promotional interest reliefs (15/8, 10/5, 10/5, 20/10), so the per-diem rate and the posted charge's rate agree; no contradiction.
- Time anchors: every extended charge posts "on the first day after that period's statement closes" (late fee, post-promo, fixed-rate) and the returned-payment fee "on the first day after that period's statement closes or on the day the fee is fixed if later"; consistent with base `statement_period_basis` (calendar month).
- Cross-category read boundary: every policy reads only `plan` (`status`, `consecutive_terms`), declared in `cross_category`, `inputs.cross_category` and the member-relief factor; no undeclared read.

Scope exclusivity (to be confirmed against the tasks' own trees in their files): the two trees the graph admits are {payoff, late fee, post-promo interest} and {returned-payment fee, make-up payment, fixed-rate interest}; they are disjoint and jointly cover all six extended policies.

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quotation and back against the rule, per policy:

- **late fee**: lookback (`lf_rev_recent`, `lf_rev_last`, `lf_window_age`, `lf_lookback`) ↔ "The late-fee lookback covers … less than lookback_months whole months …; where a late fee reversal was posted … as many whole months … as have passed since the most recent late fee reversal; where no late fee reversal … and the account funded at least long_account_months … short_lookback_months"; `within_months=N` implements "less than N whole months" (MONTHS < N). Occurrence schedule ↔ 25/32/late_fee_usd sentence. Member/age/record ↔ their sentences. `lf_cap` ↔ "never more than late_fee_max_pct_of_payment_due percent of the account's monthly_payment"; `result` = RND(MN(scheduled×(100−relief)/100, cap)) ↔ "reduced once … never more than … rounded … only at the end". No unbacked binding; no rule sentence without a binding. The posting-day sentence ("posted on the first day after that period's statement closes") is a timing statement, not a quantity.
- **post-promo interest**: `ip_days` = (DAYS(promo_end, NOW) − 1) when no interest posted, else DAYS(last interest, NOW) ↔ "from the day after promo_end_date … otherwise from the day the previous interest charge posted, up to but not including the day this charge posts" (correct day count both ways). `ip_base` three branches ↔ the three-branch base sentence incl. "a base below zero counts as zero" (MX(0,…)). Leftover ↔ "amount_financed less every payment that stood … in units of the account's monthly_payment". `ip_rate` ↔ "reduced once by … added together". Equivalent.
- **payoff**: `po_principal` ↔ "account_balance less every late fee, returned-payment fee and interest charge posted less than one whole month before the day of payoff, and never below zero". `po_rate_base` four branches ↔ the four-tier starting-rate sentence. Record and leftover reliefs carry the "applies only when the plan's promotion has ended" gate (`po_post_promo`). `po_days` ↔ the three-tier per-diem-days sentence: +1 for "both days counted"; DAYS(promo_end, NOW) for "from the day after promo_end_date through the day of payoff"; DAYS(last payment, NOW) for "from the day after the most recent payment through"; DAYS(funded, NOW)+1 for "from the funded_date through". Equivalent.
- **fixed-rate interest**: `fx_days` ↔ "from the day the previous interest charge posted, or from the funded_date when none has posted, up to but not including"; base ladder, autopay standing (0 / exactly 1 / otherwise), member, age, `fx_rate` ↔ "reduced once by … the two reliefs". Equivalent.
- **make-up**: `mu_owed` three branches ↔ the three-branch "installment still owed" sentence; `mu_pull_pct` ↔ 100/50/0 sentence; `mu_pull` ↔ "monthly_payment multiplied by the pull-forward share and then reduced once by … added together". Equivalent.
- **returned-payment fee**: `rf_window` ↔ the three-branch lookback sentence; `rf_prior` = MX(0, COUNT − 1) ↔ "the payment this fee concerns not counted"; `rf_gap` = DAYS(last return, last payment) with tiers 0–3 / 4–10 / else ↔ "on the day … or no more than prompt_days_short days after it … more than prompt_days_short but no more than prompt_days_long … zero when no payment has posted since the return or it posted later"; `result` = RND(MX(0, …)) ↔ "never below zero, … rounded". Equivalent.

Every factor's ladder tiers are sentences of its rule and branches of its `decides` binding, and vice versa (checked factor by factor; no tier lives only in `compute` or only in the rule).

Implementation-level notes (no rule/compute disagreement on either world; recorded as observations O-2, O-3, O-4 below): "the most recent payment was returned" is implemented as a date comparison of LATEST(payment_returned) ≥ LATEST(payment), not by `source_txn_id`; RND is Python `round` (float, ties-to-even) whereas the rule says half up; CFIELD('plan', …) reads the customer's first plan agreement without filtering by status.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). No base policy names any of the six tools.
- Docstrings: each tool states one atomic write and its receipt; no tool names another tool, states a position in a sequence, or uses an ordering word (grep for before/after/first/then/until/prior/later finds only "the balance owed after the fee/charge" — a balance description — and "pays once" for one-time payment methods).
- Function bodies: each only `find`s the account, `create`s one `finance_transactions` row and `update`s the balance (and, for payoff, `status=paid_off`, `closed_date`). None checks eligibility, timing, prerequisite or amount; none raises or hints.
- uuid8 tails: ce58c754, b0f5a17d, 45ecd350, d84dbec7, e9bd505b, 928f04f0 — six distinct, no shared prefix, no sequence or adjacency pattern; consistent with independent generation.

### prerequisite_graph

Every extended policy fills `prerequisite` (three with `[]`). Edges:

- E1 payoff → late fee (`value_input`, gate `po_bal`, form state).
- E2 payoff → post-promo interest (`value_input`, gate `po_days`, form state).
- E3 make-up → fixed-rate interest (`state_gate`, gate `finance_transactions.line_type`, form state).
- E4 returned-payment fee → make-up (`value_input`, gate `rf_gap`, form state).

All `problem` ids are extended policies of this file, none self-referential; the graph is two disjoint chains/fans and acyclic. Every `policy_source` is verbatim in its own policy's `rule` (checked by string match). No edge is action-form, so no `fallback_reason` is required and none is present. `resolved_by` equals the depended-on policy's `target_tool` in all four. `kind`/`gate`: `po_bal`, `po_days`, `rf_gap` are real compute bindings of the blocked policy; E3's gate names the line type the state is read from. Conditions restate the sentences at the same strength (E1 "every statement period whose required payment was still unpaid more than late_fee_grace_days … after its due date"; E2 "every statement period that closed after promo_end_date"; E3 "On a fixed-rate account, … every statement period that has closed since funding"; E4 "a payment posted on or after the most recent payment_returned entry, or the returned installment's due date is more than late_fee_grace_days calendar days past"). Effects: E1 true (fee raises balance, payoff principal excludes it); E2 true (charge raises balance and moves the per-diem start); E4 true (make-up becomes the most recent payment, `rf_gap` changes); E3's effect claims only that the payment may then be taken — the make-up amount reads no interest row (observation O-9). No authoring-viewpoint phrasing in any `prerequisite` text.

### prerequisite_sentences

Four-point test, per edge:

- **E1** "The payoff figure is fixed only after the account carries the late fee owed for every statement period whose installment stayed unpaid past its grace period." — connective "only after"; waited-on state is record-visible (a `late_fee` line per statement period); names no tool, id or snake_case token; scope matches the condition (every such period). The one write of this difficulty that creates a `late_fee` line is `post_late_fee_ce58c754`, whose policy's own rule describes it ("A late fee is charged for every statement period whose required payment is still unpaid more than late_fee_grace_days calendar days after its due date"). Derivation: sentence → records (which periods were unpaid past grace and lack a late fee) → late-fee rule → post that period's late fee. One reading.
- **E2** "The payoff figure is not fixed until the account carries the post-promotional interest charge for every statement period that closed after the promotion ended." — "not … until"; record-visible (`interest` line per period after promo end); no tool/id. Two tools write `line_type = interest`, but the state is named "post-promotional interest charge" and the fixed-rate policy is scoped to `interest_rate_type` fixed, so on any account where the sentence can bite (a promotional plan) only `post_post_promo_interest_b0f5a17d` brings it about (observation O-8). One reading.
- **E3** "The make-up amount on a fixed-rate account is not fixed until the account carries the closing interest charge for every statement period that has closed." — "not … until"; record-visible; "closing interest charge" is the fixed-rate policy's own term ("posted … as a closing interest charge"); only `post_fixed_rate_interest_d84dbec7` applies on a fixed-rate account. One reading.
- **E4** "The returned-payment fee is fixed only after a replacement payment has posted for the returned installment or the installment's grace period has run out." — "only after"; record-visible (a payment line after the return, or the calendar); no tool/id; the disjunction is carried into the condition verbatim. The payoff tool also posts a payment line, but the make-up policy's rule is the one that describes "a borrower who brings a missed or returned installment up to date" — i.e. a replacement payment for the installment; a payoff is not a replacement for an installment and is not within a fee-only caller's need (observation O-7). One reading. The grace disjunct is a calendar state; where neither disjunct holds at handling, resolving today requires the make-up write (no wait needed).

No rule carries a second wording of its dependency, a tool name or another problem's id; no depended-on rule restates the sentence. No other cross-problem order appears in any extended rule. Base sentences with an order flavour — finance_payoff_rules "An account is paid off on the day its account_balance reaches 0.00 after every posted charge", finance_late_and_returned_fees "so a late fee may follow if the grace period then passes" — ground no declared edge and no tree rests on them (observation O-10).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- **late fee** (refs payment_terms, deferred_interest, late_and_returned_fees): follows the grace sentence, the day-0 counting sentence and the one-per-period sentence; the amount sentence "The late fee is late_fee_usd, never more than late_fee_max_pct_of_payment_due percent of the payment that was due" is handled differently (schedule, reliefs, cap on monthly_payment) and is declared in `overwrite`. payment_terms' "returned payment … treated as never made" is followed by the payment-record relief (payments less returned payments). deferred_interest sentences do not govern a late fee. No undeclared override.
- **post-promo interest** (refs payment_terms, deferred_interest, late_and_returned_fees): the two base sentences that set post-promo accrual ("From the day after promo_end_date any remaining balance … accrues interest at post_promo_apr_pct, posted monthly as interest"; "On equal-payment plans … simply starts accruing at post_promo_apr_pct") are both named in `overwrite`. "Merchant refunds and payments … count toward paying the promotional balance" and the deferred-interest assessment sentences govern other quantities. payment_terms' "on equal-payment 0% plans no interest posts during the promotional period" is respected (charges only after promo end). The variant parameter `interest_accrual_basis` ("daily simple interest on the daily principal balance, 365-day year") is not a rule sentence and is not named (observation O-1).
- **payoff** (refs payment_terms, payoff_rules, servicing_changes): payoff_rules' quote sentence is named; servicing_changes' autopay-APR clause is named (probation tier). "An account is paid off on the day its account_balance reaches 0.00 …; a payment of less than the full balance never closes the account" is followed (payoff = full balance + per diem; tool sets 0.00). payment_terms' no-prepayment-penalty sentence is followed. No undeclared override.
- **fixed-rate interest** (refs payment_terms, deferred_interest, late_and_returned_fees, servicing_changes): payment_terms' fixed-rate accrual sentence and servicing_changes' autopay clause are named. late_and_returned_fees' "When autopay_removal_after_returns autopay payments have been returned within 12 months, autopay is removed and any autopay APR reduction ends" agrees with the standing ladder at two or more returns (full apr_pct). No undeclared override.
- **make-up** (refs payment_terms, payoff_rules; `overwrite: []`): payment_terms' "the original payment is treated as never made" is followed by the operative ladder (tier 1: full monthly_payment owed). The rule's "standard method" sentence, read alone, counts a returned payment posted in the month as made; that is the declared baseline of the factor ladder, not the merged semantics (observation O-11). payoff_rules sentences do not govern the make-up quantity. No undeclared override.
- **returned-payment fee** (refs payment_terms, deferred_interest, late_and_returned_fees): "Each returned payment is charged one returned_payment_fee of returned_payment_fee_usd naming that payment" is named; "naming that payment" is retained in the extended rule. Other sentences followed. No undeclared override.

Disguised forms checked: no anonymous intermediate factor, no 0/1 multiplier on an amount base, no dropped base branch; no rule or note calls base's output a "wrong value".

### factor_ladders

| policy | factor | label | tiers | outcome values | honest label | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- | --- |
| late fee | late_fee_occurrence_schedule | parameter | 3 | 25 / 32 / 39 | yes | no | — |
| late fee | late_fee_lookback_convention | method | 3 | since last reversal / 6 m / 12 m | yes (event-anchored window vs rolling; O-5) | no (tier 1 single-source) | — |
| late fee | late_fee_member_relief | parameter | 3 | 20 / 10 / 0 % | yes | no (one agreement row) | plan |
| late fee | late_fee_account_age_relief | parameter | 3 | 15 / 10 / 0 % | yes | no | — |
| late fee | late_fee_payment_record_relief | parameter | 3 | 10 / 5 / 0 % | yes | no | — |
| post-promo | post_promo_interest_base | method | 3 | bal − last interest − recent fees / bal − recent fees / bal | yes | no | — |
| post-promo | post_promo_member_relief | parameter | 3 | 15 / 8 / 0 % | yes | no | plan |
| post-promo | post_promo_account_age_relief | parameter | 3 | 10 / 5 / 0 % | yes | no | — |
| post-promo | post_promo_payment_record_relief | parameter | 3 | 10 / 5 / 0 % | yes | no | — |
| post-promo | post_promo_leftover_relief | parameter | 3 | 20 / 10 / 0 % | yes | no | — |
| payoff | payoff_rate_start | parameter | 4 | post_promo_apr / apr − disc / apr − ½disc / apr | yes | yes (plan term × promo date; autopay × returns) | — |
| payoff | payoff_member_relief | parameter | 3 | 15 / 8 / 0 % | yes | no | plan |
| payoff | payoff_account_age_relief | parameter | 3 | 10 / 5 / 0 % | yes | no | — |
| payoff | payoff_payment_record_relief | parameter | 3 | 10 / 5 / 0 % | yes | yes (promo ended × count) | — |
| payoff | payoff_leftover_relief | parameter | 3 | 20 / 10 / 0 % | yes | yes (promo ended × measure) | — |
| payoff | payoff_per_diem_anchor | method | 3 | from last interest (both days) / from day after promo end / from day after last payment | yes | no | — |
| fixed-rate | fixed_rate_interest_base | method | 3 | as post-promo base | yes | no | — |
| fixed-rate | fixed_rate_autopay_standing | parameter | 3 | apr − disc / apr − ½disc / apr | yes | yes (autopay flag × returns) | — |
| fixed-rate | fixed_rate_member_relief | parameter | 3 | 15 / 8 / 0 % | yes | no | plan |
| fixed-rate | fixed_rate_account_age_relief | parameter | 3 | 10 / 5 / 0 % | yes | no | — |
| make-up | makeup_installment_owed | method | 3 | full monthly_payment / mp − net stood / max(0, mp − gross) | yes | no | — |
| make-up | makeup_pull_forward_share | parameter | 3 | 100 / 50 / 0 % | yes | yes (returned × autopay flag) | — |
| make-up | makeup_pull_forward_member_relief | parameter | 3 | 50 / 25 / 0 % | yes | no | plan |
| make-up | makeup_pull_forward_account_age_relief | parameter | 3 | 30 / 20 / 0 % | yes | no | — |
| returned fee | returned_fee_occurrence_schedule | parameter | 3 | 15 / 20 / 25 | yes | no | — |
| returned fee | returned_fee_lookback_convention | method | 3 | 12 m / 6 m / 24 m | **no — see F-1** | yes (autopay × age) | — |
| returned fee | returned_fee_prompt_replacement_relief | parameter | 3 | 30 / 15 / 0 % | yes | no | — |
| returned fee | returned_fee_member_relief | parameter | 3 | 20 / 10 / 0 % | yes | no | plan |
| returned fee | returned_fee_account_age_relief | parameter | 3 | 10 / 5 / 0 % | yes | no | — |
| returned fee | returned_fee_payment_record_relief | parameter | 3 | 10 / 5 / 0 % | yes | no | — |

Counts per policy (declared → surviving the label test): late fee 5 (4 P, 1 M); post-promo 5 (4 P, 1 M); payoff 6 (5 P, 1 M); fixed-rate 4 (3 P, 1 M); make-up 4 (3 P, 1 M); returned fee 6 declared (5 P, 1 M) → **6 P, 0 M** after F-1. Every policy has at least one `cross_difficulty` (plan) factor; the multi-source factors are in payoff, fixed-rate, make-up and returned fee (so each tree carries one).

Structural checks: every factor's bindings are disjoint from every other factor's and its `decides` is an input, never `result`; every ladder has three or four pairwise-disjoint tiers with a fall-through; every fall-through equals the factor's `baseline` and is what the policy's `baseline.rule` states (late_fee_usd / rolling lookback_months / zero reliefs / account_balance / apr_pct / day after last payment / max(0, mp − payments in month) / no pull-forward / returned_payment_fee_usd / standard_lookback_months); every tier's value comes from the policy's `params` or the plan parameters; no two tiers of one ladder select the same value or method as stated (on plans whose `autopay_apr_discount_pct` is 0.00 the payoff_rate_start tiers 2–4 coincide numerically — O-6). Every policy's `baseline.rule` is a sentence-for-sentence subset of its `rule` and yields a definite number from the records with no factor applied; `baseline.params` names the plan keys it uses (make-up `[]` — it uses only the account's monthly_payment).

Business realism: member (loyalty), account-age, payment-record, leftover/near-payoff, prompt-replacement and step-up occurrence schedules (first/second/subsequent, as in card-act style safe harbours) are conditions consumer lenders weigh for fees and goodwill rate relief; the interest-base ladder excludes unpaid non-principal charges using the last-payment-returned / recent-fees state as the record that shows them unpaid; the make-up pull-forward is keyed on a returned payment while autopay still points at the account that returned it. No tier condition holds of every customer who reaches its write; no fall-through is a treatment no lender would publish.

### findings

- **F-1 — SOURCE-FACTOR RED (structure; bears on task 1).**
  - Symptom: `returned_fee_lookback_convention` is labelled `effect: method` but every tier selects only a different constant window length for the same count.
  - Root cause: ladder `method` texts "count payments returned less than autopay_lookback_months whole months …", "… less than short_lookback_months whole months …", "… less than standard_lookback_months whole months …"; compute `rf_window: K('autopay_lookback_months') if rf_autopay_on == True else (K('short_lookback_months') if rf_age_window >= K('long_account_months') else K('standard_lookback_months'))`, consumed unchanged by `COUNT('finance_transactions', within_months=rf_window, …)`. The algorithm is identical across tiers; only the number (12 / 6 / 24) changes — a `parameter` effect.
  - Consequence: relabelled honestly, `finance_ext_returned_payment_fee` declares 6 parameter factors and **0 method factors**, below the "at least 1 `method`" floor for that computation. (Contrast `late_fee_lookback_convention`, whose first tier anchors the window on the most recent reversal record rather than a fixed length — accepted, O-5.)
  - Affected: `finance.extended.yaml` → `finance_ext_returned_payment_fee.factors[returned_fee_lookback_convention]`; task 1's returned-fee computation.
- Observations (no RED; consequences not demonstrable on the two worlds or charter-only):
  - O-1 Variant parameter `interest_accrual_basis` ("daily simple interest on the daily principal balance") is not named in any overwrite while the extended interest and payoff methods use a balance-based base × days. The rule-level sentences that govern those quantities are declared; on task 0 the principal is constant 341.84 over the accrual days, on task 1 the principal (payments applied fees→interest→principal, returned payments as never made) is 5746.56, equal to the tier-1 base — no divergence demonstrated.
  - O-2 "most recent payment was returned" is implemented by date comparison (`DAYS(LATEST payment, LATEST payment_returned) >= 0`), not via `source_txn_id`; differs from the rule when a return of an older payment posts after a newer payment. Both worlds: identical.
  - O-3 RND is float `round` (ties-to-even on exact binary ties) vs "half up"; no tie arises on either world.
  - O-4 `CFIELD('plan', …)` takes the customer's first plan agreement regardless of status; differs from "holds an active Comfort Club agreement" for customers with several agreements. Both worlds hold exactly one.
  - O-5 `late_fee_lookback_convention`: tiers 2–3 are constant windows (6 / 12); tier 1 is event-anchored. Accepted as `method`; borderline.
  - O-6 `payoff_rate_start` tiers 2–4 coincide in value on plans with `autopay_apr_discount_pct` 0.00 (all promotional plans before promo end).
  - O-7 E4's state "a replacement payment has posted" is also produced by the payoff payment tool; the make-up rule is the one describing a replacement for an installment.
  - O-8 E2's state is written as line_type `interest`, which the fixed-rate tool also writes; scope ("post-promotional", "interest_rate_type is fixed") separates them.
  - O-9 E3 is a pure `state_gate`: the make-up amount reads no interest row, so posting the closing interest charge never changes it; permitted by the max(n−1,1) floor when the tree's other edge is `value_input`.
  - O-10 Base ordering sentences (payoff "after every posted charge"; "a late fee may follow") ground no edge.
  - O-11 The make-up rule's standard-method sentence alone counts a returned payment posted in the month as made, contrary to payment_terms' "treated as never made"; the operative ladder restores base, so the merged semantics follow base.
  - O-12 Schema `finance_accounts.apr_pct` means "Contract APR in effect for the plan after any autopay reduction" (5.74 on task 1's account), whereas the rules start from "the plan's apr_pct" (plan parameter 5.99). The schema meaning disambiguates; a reader who takes the account field and subtracts the discount again gets a different rate (demonstrated in task 1's file).

## closing_checklist

Written 2026-10-05 after both tasks' `source_gt_comparison` sections were on disk (post-reveal; kept below the pre-reveal charter-global section, which was not edited after the reveal except to replace its typed freeze time with the file mtime).

- Per-task files: `0.md`, `1.md` correspond one-to-one to `tasks/0.json`, `tasks/1.json`; `_difficulty.md` alongside; no older revision exists (first audit). Comparison sections: task 0 — policy PASS, chain PASS, **factors SOURCE-FACTOR RED (T0-F1)**, unique solution PASS; task 1 — policy PASS, chain PASS, **factors SOURCE-FACTOR RED (T1-F1 / F-1)**, unique solution PASS. Not every comparison carries a PASS.
- Coverage and scopes: GT `charter_scope` — task 0 {late fee, post-promo interest, payoff} + their three tools; task 1 {fixed-rate interest, make-up, returned fee} + their three tools; pairwise disjoint over whole trees, jointly all six extended policies and all six task tools. Each tool's uuid8 independent and frozen (§ action_binding_and_uuids). Task tools and GT closed (every GT write is one of the claimed tools; REPLAY OK).
- Trees: task 0 — 2 prerequisite problems, 2 value_input edges, user write `submit_payoff_payment_45ecd350`, acyclic; task 1 — 2 prerequisite problems, 1 value_input + 1 state_gate edge (floor 1), user write `submit_makeup_payment_e9bd505b`, acyclic. Difficulty-wide graph E1–E4 acyclic, no cross-task reference.
- Factors: every computation declares a self-sufficient baseline giving a definite number ≠ gold (task 0: 39.00 / 2.99 / 358.27; task 1: 28.40 / 0.00 / 25.00) and four to six factors with three- or four-tier ladders stated in full in the rule. **Not met**: the post-promotional interest computation's only method factor bears no weight in a policy-permitted order on task 0 (T0-F1); the returned-fee computation has no honest method factor (F-1, task 1). Multi-source and cross-difficulty (plan) factors present in both tasks; cross-difficulty rows seeded.
- Gates on the final form: the audited artifacts are unchanged since the coordinator's gate run (hashes at close: `finance.extended.yaml` 37be8a42…07f1, `task_tools.py` 44f740be…be9, `tasks/0.json` c013562d…c49e, `tasks/1.json` f9eb2731…77b9; extended/tool hashes equal the brief's), so the snapshot `/tmp/erl37/gates/home_comfort_financing_servicing.snapshot.txt` (all green) stands for the final form; check_traceability remains deferred to KB publication per the brief.

Difficulty result: **does not pass** the source-layer audit — both tasks carry a SOURCE-FACTOR RED; policy self-consistency, problem trees and unique solutions pass for both.

## revision_2

### charter_global_frozen (revision 2)

- Written 2026-10-05T18:19:42Z (file mtime), before any round-2 task GT was opened; contains nothing derived from a round-2 GT. Round-1 text above is untouched.
- Hashes (match `/tmp/erl37/views_r2/home_comfort_financing_servicing/charter.sha256`): `finance.extended.yaml` **2aedde4d62b46c0acf38b21547862664b161c211d5ef669ee00f0162c25bdcb5** (round 1: 37be8a42…07f1 — changed, so every charter-global section is re-derived below); `task_tools.py` 44f740be…be9 (unchanged — tool contracts, docstrings, function bodies and uuid8s carried forward from round 1 by hash). Masked views r2: task_0 1f390f24…3022, task_1 7a26971a…37da.
- Gate snapshot `/tmp/erl37/gates/home_comfort_financing_servicing.r2.snapshot.txt`: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; CACHE-DIFF INFO. Input complete.
- Read domain as in round 1. Prior-knowledge disclosure: this auditor read the round-1 GT of both tasks after the round-1 freeze; that knowledge cannot be unread. The round-2 re-derivation below rests on the charter, the r2 masked views and the policy's own compute only; `tasks/*.json` were not reopened before both round-2 task freezes.

### What changed in the charter (located by re-reading; base copy still byte-identical to `blueprint/products/finance.yaml`, 1265 lines)

1. `finance_ext_post_promo_interest`: new rule sentence and new prerequisite edge **E5** → `finance_ext_late_fee_schedule`, `kind: state_gate`, `gate: finance_transactions.line_type`, `form: state`, `policy_source`: "The post-promotional interest charge for a statement period is worked out only after the account carries the late fee owed for that same period whenever its installment stayed unpaid past its grace period, so that the interest base is measured on the period's closed fee position."
2. `finance_ext_returned_payment_fee`: `returned_fee_lookback_convention` removed (params `autopay_lookback_months`, `short_lookback_months` removed; the lookback is now the single sentence "The returned-payment lookback covers payments returned less than standard_lookback_months whole months before the date of handling", compute `rf_prior` uses `K('standard_lookback_months')`); new `method` factor `returned_fee_payment_record_count` (`decides: rf_paid_selected`) with rule sentence "The returned-payment payment-record count follows how the borrower pays: when autopay is enrolled it counts the autopay drafts posted less than record_window_months whole months before the date of handling, less the returned payments posted in that time; when autopay is not enrolled but autopay drafts were posted in that time, the borrower having just left autopay, it counts only the payments other than autopay drafts posted in that time, less the returned payments; otherwise it counts every payment posted in that time, less the returned payments."; `returned_fee_payment_record_relief` now reads that count.
3. All six policies: `CFIELD('plan', 'status'|'consecutive_terms', status='active')` (was unfiltered).
4. Late fee, payoff, fixed-rate interest and make-up: rule, params, compute (apart from item 3), factors, baselines, prerequisites and overwrites re-read and unchanged from round 1.

### policy_conflict_scan (r2)

Round-1 scan re-run over the changed charter: no new overlap. E5 adds an order between two agent statement charges of the same period (late fee before post-promotional interest); it touches no other policy's subject, trigger or terminal state. The returned-fee changes stay inside that policy's quantity. Scopes: the graph still splits into {payoff, late fee, post-promo interest} and {returned fee, make-up, fixed-rate interest}, disjoint and jointly complete.

### rule_compute_equivalence (r2)

- Post-promo: the new sentence is a prerequisite sentence (no quantity); compute unchanged apart from CFIELD. Equivalent.
- Returned fee: `rf_prior` ↔ the single lookback sentence (`within_months=24`); `rf_rec_drafts` (payment_method autopay_ach), `rf_rec_all`, `rf_paid_selected` three branches ↔ the three-clause record-count sentence (enrolled → drafts; not enrolled with drafts in window → all − drafts; otherwise → all); `rf_rec_returns`, `rf_paid12 = rf_paid_selected − rf_rec_returns` ↔ "less the returned payments posted in that time"; `rf_record_pct` ↔ the relief sentence on "the returned-payment payment-record count". No unbacked binding; no sentence without a binding; the removed lookback tiers survive nowhere in rule, compute_basis, params or inputs (inputs now carry the 24-month return count and the 12-month draft/all-payment counts).
- CFIELD with `status='active'` now implements "holds an active Comfort Club agreement" directly.

### action_binding_and_uuids (r2)

Carried forward by hash (`task_tools.py` unchanged); each `(target_tool, computes)` still claimed by exactly one policy.

### prerequisite_graph (r2)

Edges E1, E2, E3, E4 unchanged; new E5 (post-promo → late fee). All `problem` ids are extended policies, none self-referential; graph payoff→{late fee, post-promo}, post-promo→late fee, returned fee→make-up→fixed-rate — acyclic. E5 `policy_source` verbatim in the post-promo rule (string match); form state, no `fallback_reason` (correct); `resolved_by: post_late_fee_ce58c754` = the late-fee policy's target tool; condition ("a late_fee entry for the statement period being closed whenever that period's required payment was still unpaid more than late_fee_grace_days calendar days after its due date") matches the sentence's scope ("for that same period whenever its installment stayed unpaid past its grace period"); `state_gate` on `finance_transactions.line_type`; effect ("the fee posted this month is one of the charges the base leaves out, so the base ladder is read on the world in which the period's fees stand") is true of the compute (`ip_fees_recent` includes a late fee posted on the day of handling). No authoring-viewpoint phrasing.

### prerequisite_sentences (r2)

- **E5**: connective "only after"; waited-on state record-visible (a `late_fee` line for the period); no tool, id or snake_case token; strength matches the condition. Only `post_late_fee_ce58c754` writes a `late_fee` line, and the late-fee rule describes it. One reading. The trailing purpose clause ("so that the interest base is measured on the period's closed fee position") states no second dependency. The late-fee rule does not restate the sentence.
- E1–E4 unchanged (round-1 conclusions stand; their quotations re-verified verbatim).
- No new cross-problem order elsewhere in the extended rules.
- Observation R2-O1: E5 is value-neutral for the interest charge — the fee it requires is exactly a charge the interest-base ladder subtracts, so the charge is the same with or without the fee on the account; what E5 fixes is the order, and therefore the world on which the base ladder is read. Permitted for a `state_gate` within the value-input floor.

### override_declarations (r2)

Returned fee: the new lookback and record-count sentences govern quantities no base sentence of `finance_payment_terms`, `finance_deferred_interest` or `finance_late_and_returned_fees` addresses; the base amount sentence remains declared. Post-promo: the new sentence is an ordering of two extended charges; no base sentence orders them. All other policies unchanged. No undeclared override.

### factor_ladders (r2)

Changed rows only (others as round 1):

| policy | factor | label | tiers | outcomes | honest label | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- | --- |
| returned fee | returned_fee_payment_record_count | method | 3 | count drafts only / count non-draft payments only / count every payment (each less returns) | yes — the tiers change which records are counted, not a number | no (tier 1 single-source; tier 2 autopay flag × draft history) | — |
| returned fee | returned_fee_payment_record_relief | parameter | 3 | 10 / 5 / 0 % on the selected count | yes | no | — |
| returned fee | (returned_fee_lookback_convention) | — | — | removed | — | — | — |

Returned fee: 6 factors, 5 `parameter` + 1 `method`; fall-through of the new method = its baseline (`rf_rec_all`, "every payment posted in that time") ✓; bindings disjoint from the record-relief factor's (`rf_rec_returns`, `rf_paid12`, `rf_record_pct`) ✓; `decides` an input ✓; every tier in the rule and in compute ✓. Counts per policy now: late fee 5 (4P/1M), post-promo 5 (4P/1M), payoff 6 (5P/1M), fixed-rate 4 (3P/1M), make-up 4 (3P/1M), returned fee 6 (5P/1M).

Business realism of the new method: tier 1 (autopay enrolled → the scheduled drafts are the record; manual extras and cures are not separate installments) and tier 3 (all payments) are treatments a lender applies. Tier 2 (a borrower who left autopay within the window has only the non-draft payments counted, i.e. the drafts drop out of the record) is unusual — it reads as "the record since the change of payment method" — but no consequence can be demonstrated on either world (task 1's borrower is on tier 1) and it is not a treatment that can be shown never to be published; recorded as observation R2-O2.

### findings (r2) — status of round-1 charter-global items

- **F-1 (SOURCE-FACTOR RED)** — closed in the charter: the mislabelled lookback factor is gone and the returned-fee computation now carries an honest `method` factor. Whether it bears weight is task 1's question (its file).
- **O-4** — closed: CFIELD filters `status='active'`.
- O-1, O-2, O-3, O-5, O-6, O-7, O-8, O-9, O-10, O-11, O-12 — unchanged, re-verified against the changed file; stand as observations.
- New observations: R2-O1 (E5 value-neutral, order-fixing), R2-O2 (record-count tier 2 realism). No new charter-global RED.

### closing_checklist (revision 2)

Written after both round-2 comparisons were on disk.

- Per-task files `0.md`, `1.md` each carry an appended `## revision_2` (frozen derivation, then comparison, then findings); round-1 text untouched; `_difficulty.md` carries this revision_2 alongside.
- Round-1 REDs: T0-F1 closed (E5 fixes the order; the interest-base factor bears weight on the only handling world); F-1/T1-F1 closed (honest weight-bearing method factor in the returned-fee computation). Round-1 observations the reworker marked changed: O-4, T0-O2, T0-O4, T0-O5, T1-O1 — all verified closed. Items marked unchanged — verified unchanged.
- Coverage and scopes: task 0 {late fee, post-promo interest, payoff}, task 1 {fixed-rate interest, make-up, returned fee}; disjoint over whole trees, jointly complete; tools closed; uuid8s unchanged and independent.
- Trees: task 0 — 2 prerequisite problems, 2 value_input + 1 state_gate edges, user write payoff, acyclic; task 1 — 2 prerequisite problems, 1 value_input + 1 state_gate, user write make-up, acyclic. Whole graph (E1–E5) acyclic.
- Factors: every computation has a self-sufficient baseline giving a definite number ≠ gold; 4–6 factors with ≥ 2 parameter and 1 method each; every factor bears weight on its task's handling world; multi-source and cross-difficulty (plan, seeded) factors in both tasks.
- New defects: none. New observations: R2-O1 (E5 value-neutral, order-fixing), R2-O2 (record-count tier 2 realism, unreached), T1-R2-O1.
- Gates on the final form: the coordinator's round-2 snapshot (`/tmp/erl37/gates/home_comfort_financing_servicing.r2.snapshot.txt`, all seven OK + CACHE-DIFF INFO) was taken on the hashes audited here (`finance.extended.yaml` 2aedde4d…bcb5, `task_tools.py` 44f740be…be9; tasks 0/1 f3c4a429…c5ca / 34617e69…c547 at reveal). check_traceability still deferred to KB publication.

Difficulty result (revision 2): **passes** the source-layer audit — policy self-consistency, problem tree, factors and unique solution PASS for both tasks.
