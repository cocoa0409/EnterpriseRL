# Policy-task audit — personal_payments_limits_and_account_access / charter-global

## charter_global_frozen

- Round: r1 (first audit of this difficulty; no earlier revision exists).
- Freeze time: 2026-09-25T00:05Z. Auditor: independent policy-task auditor (not the authoring agent).
- Frozen inputs (sha256 re-computed by the auditor and equal to the brief):
  - `tasks/personal_payments_limits_and_account_access/wallet.extended.yaml` = `78c8f5389ac9415dc26d96700b3e43f3b8f16969b88b5e88411197fca3063726`
  - `tasks/personal_payments_limits_and_account_access/task_tools.py` = `e619d5c436c6e094952967ac2d611f547f88513a2da3b6882a1e0f3a23b652da`
  - masked views `coord/views/policy/personal_payments_limits_and_account_access/r1/0.view.json` = `f53dc100…fc9b`, `1.view.json` = `f7c63a3e…a45a` (each has only task_index, frozen_time, user_scenario, initial_state).
- Read: `blueprint/blueprint.yaml`, `blueprint/products/wallet.yaml` (+ spot reads of `rewards.yaml`, `savings.yaml`, `advance.yaml`, `business.yaml` and `db_schema.json` for seeded-row consistency), `blueprint/share_tools.py` signatures, the extended charter, `task_tools.py`, the two masked views, `coord/snap/d1_r1.txt`.
- Masked and not read when this section was written: `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), the difficulty `worklog.md`, the scenario `worklog.md`, the shared scratchpad, audits of other difficulties. No recursive search was run over `tasks/` or the scenario root.
- Nothing in this section is derived from a revealed GT.

### entry_conditions (Step 0)

- Gate snapshot supplied (`coord/snap/d1_r1.txt`): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 15 acts / 1.json 12 acts, match True), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. check_traceability deferred (KB not yet published) — noted, not a defect of this stage.
- Masked views supplied with hashes; hashes verified. Entry conditions complete.
- Base copy: `diff` of lines 1–1491 of the extended charter against `blueprint/products/wallet.yaml` shows only the four-line `extended_policies` banner added after line 1491 — the base section is verbatim.

### policy_conflict_scan

Extended policies (4): `wallet_ext_renewal_plan_fee` (agent, `charge_plan_fee_0f985a0a`, computes fee_amount), `wallet_ext_available_balance_transfer` (user, `transfer_balance_to_bank_3181bc35`, computes amount), `wallet_ext_protection_reimbursement` (agent, `post_protection_reimbursement_5be5cf5a`, computes amount), `wallet_ext_claim_money_instant_fee` (user, `send_instant_cash_out_cd9063e1`, computes fee_amount).

- Overlapping subjects: `wallet_fee` is a subject of renewal_plan_fee (plan_fee rows) and claim_money_instant_fee (instant_transfer_fee rows) — disjoint by fee_type and by target tool. `wallet_cash_out` is a subject of available_balance_transfer (standard) and claim_money_instant_fee (instant) — disjoint by transfer_speed, tool and trigger wording ("move everything they can … to their linked bank" vs "money reimbursed on a claim sent instantly to a linked debit card"). No two extended policies reach a conclusion on the same written quantity.
- Triggers: two `state_due` (renewal fee on the renewal date; reimbursement on an approved, unreimbursed purchase-protection claim), two `on_request`. No trigger of one policy is the trigger of another.
- Eligibility / time anchors: every extended rule restates the base gate it keeps (plan-fee waiver; cash-out status/daily limit/ledger ceiling; protection window, one-claim-per-payment, claims-team approval; instant maximum). Windows are all stated as "dated later than the same calendar day N months before the handling date" (or renewal date — see O-4).
- Cross-category read boundaries: renewal reads rewards/savings/card; transfer reads advance/business; reimbursement reads rewards; claim-money reads card/savings. Each declared under `cross_category` with the fields read; compute uses only CFIELD/XLATEST/XCOUNT on those categories.
- Terminal states: renewal → one plan_fee row + plan_renewal_date moved; transfer → one standard wallet_cash_out; reimbursement → one wallet_claim_reimbursement; claim-money → one instant wallet_cash_out + one instant_transfer_fee row. Compatible.
- Scope exclusivity (pre-reveal, from the worlds and personas only): task 0's customer asks for the whole-balance standard transfer (root = available_balance_transfer; prerequisite = renewal_plan_fee); task 1's customer asks for the claim money by instant transfer (root = claim_money_instant_fee; prerequisite = protection_reimbursement). The two trees are disjoint and together cover all four extended policies. To be confirmed against `charter_scope` after the reveal (in the closing checklist, not here).

### rule_compute_equivalence

Swept every binding of the four policies against its `compute_basis` quotation and back against the rule.

- renewal_plan_fee: dd_total/dd_count (window) ✓ except the anchor (O-4); dd_discount_pct three tiers ✓; rw_status/rw_tier/rewards_discount_pct ✓; vault_total/vault_discount_pct ✓; card_tier/card_discount_pct ✓; total_discount_pct "added together … applied once" ✓; discounted_fee ✓; period_start "date of the previous plan fee entry" ✓; period_days ✓ except the anchor (O-4); restricted_credit both branches + fall-through ✓ (reason, date comparison, later-of, grace, never below zero); result MX(0,…) then single RND ✓. Waiver sentence is an eligibility (no booking) — not in compute, correctly.
- available_balance_transfer: ledger_now ✓; advance_reserve (active status, latest disbursement due date, 0..3 / >3..10 days, % of outstanding) ✓; sales_hold (new seller = all-ever count equals 3-month count; established = some before 3 months; never = 0; 2-month vs 1-month sums) ✓; topup_hold (linked_bank, customer-requested = empty source_txn_id, 1 month, age tiers) ✓; business_reserve (balance < 0, sale count in last month) ✓; total_kept_back once, MX(0) ✓. The cash-out gates are eligibility, not compute ✓.
- protection_reimbursement: claim_amt/pp_txn (approved PP claim) ✓ (see O-5 for selector scope); funding_fee_part three branches ✓; seller/back_personal/back_gs/seller_deduction ✓; covered ✓; prior_claims "other than the one being paid" implemented as `COUNT(...) - 1` (O-5); coverage_share ✓; ceiling_multiplier ✓; ceiling ✓; result order (share, then compare with raised ceiling, MX 0, single RND) ✓.
- claim_money_instant_fee: reimb_amt "most recent claim reimbursement" ✓; quota ✓; instant_used (rolling month, less returns) ✓ (O-10); dd_measure three windows ✓; dd_1m_count ✓; deposit_rate three tiers ✓; card_age/card_cut ✓; bal_now "ledger balance before the transfer"/balance_cut ✓; fee_rate "cuts subtracted together, floor rate_floor_pct" ✓; saver_pct ✓; clamped_fee (clamp before rounding) and result (saver after clamp, single rounding, 0 inside quota) ✓.
- Every declared factor's ladder tiers appear as rule sentences and as branches of the `decides` binding, and vice versa (no tier present only in compute or only in the rule).
- No compute binding invents a basis the rule lacks; no rule quantity sentence is left unimplemented, except the anchor divergence O-4.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (charge_plan_fee_0f985a0a, fee_amount), (transfer_balance_to_bank_3181bc35, amount), (post_protection_reimbursement_5be5cf5a, amount), (send_instant_cash_out_cd9063e1, fee_amount) — each claimed by exactly one policy.
- Owners: charge_plan_fee agent, transfer_balance_to_bank user, post_protection_reimbursement agent, send_instant_cash_out user — matching the blueprint's split (fee/credit postings are agent service actions; moving the customer's own money is the customer's).
- Tool bodies (task_tools.py lines 23–172): each performs one create (two for the instant cash-out: the cash-out row and a fee row pointing to it) and one ledger update with caller-supplied values; no `if`, no raise, no status or prerequisite check, no computation beyond rounding the given figure. The tool layer judges no prerequisite and no eligibility.
- Docstrings: none names another tool, none states a position in a sequence; the only "then" words describe the tool's own visible effect ("The customer then sees…"). No added confirmation or review step.
- uuid8s: 0f985a0a, 3181bc35, 5be5cf5a, cd9063e1 — four unrelated hex strings, no shared prefix/suffix, no arithmetic adjacency; the shared tool module uses none of them. PASS.

### prerequisite_graph

| policy | prerequisite | kind / gate | form | resolved_by = depended-on target_tool | gate binding exists |
|---|---|---|---|---|---|
| renewal_plan_fee | `[]` | — | — | — | — |
| available_balance_transfer | renewal_plan_fee | value_input / ledger_now | state (no fallback_reason) | charge_plan_fee_0f985a0a ✓ | `ledger_now: F('ledger_balance')` ✓ |
| protection_reimbursement | `[]` | — | — | — | — |
| claim_money_instant_fee | protection_reimbursement | value_input / reimb_amt | state (no fallback_reason) | post_protection_reimbursement_5be5cf5a ✓ | `reimb_amt: LATEST(... wallet_claim_reimbursement)` ✓ |

- Every policy fills `prerequisite`; every `problem` is an extended policy id of this file, never a base id, never self. Graph: transfer → renewal, claim-money → reimbursement — two disjoint edges, acyclic.
- `policy_source` verbatim in the blocked policy's own rule: transfer rule sentence 4 ("A transfer of the whole available balance is not sized until …") ✓; claim-money rule sentence 2 ("An instant cash-out of claim money is priced only after …") ✓.
- `effect` holds: the plan-fee row's booking lowers `ledger_balance` (tool line 50) which is `ledger_now`; the reimbursement row becomes the latest `wallet_claim_reimbursement` (tool line 121) which is `reimb_amt`, and raises `ledger_balance` read by `bal_now`.
- `condition` strength: claim-money condition adds `provisional_credit_posted false`, which every purchase-protection claim satisfies by base rule ("carry … no provisional credit") — equal in effect to the sentence. Transfer condition is limited to "a paid plan on monthly billing", the sentence is not (see O-3).
- No authoring-viewpoint wording ("in this task", "at the opening") in any prerequisite field.

### prerequisite_sentences

1. Transfer ← renewal. Sentence: "A transfer of the whole available balance is not sized until the account carries a plan fee entry for every billing period whose renewal date has arrived." Four-point test: ordering connective "not … until" ✓; waited-on state is record-visible (plan fee entries on the activity, the renewal date on the account) with no actor/tool ✓; no tool name, policy id, snake_case token or row id ✓; scope: states "every billing period whose renewal date has arrived", broader than the monthly-only condition (O-3). Single resolving write: the only write in this difficulty that books a plan fee entry is `charge_plan_fee_0f985a0a`, and the only rule that describes booking it for a period whose renewal date has arrived is renewal_plan_fee's first sentence ("On monthly billing the renewal plan fee is booked on the renewal date as one plan fee entry …"). Derivation: sentence → look for the rule that books a plan fee entry on an arrived renewal date → renewal_plan_fee → its fee formula → its tool. One reading.
2. Claim-money ← reimbursement. Sentence: "An instant cash-out of claim money is priced only after every approved purchase protection claim on the account carries its reimbursement entry." "only after" ✓; state (approved PP claim / reimbursement entry on the activity) ✓; no tool/id ✓; scope equals the condition ✓. Single resolving write: only `post_protection_reimbursement_5be5cf5a` books a claim-reimbursement credit; the only rule describing it for an approved purchase-protection claim is protection_reimbursement ("an approval is paid as one reimbursement entry pointing to the disputed payment …"). One reading.
- Neither depended-on rule restates its dependent's sentence; neither blocked rule carries a second wording of its dependency. No docstring states sequence.
- Undeclared cross-problem orders: none in the four extended rules. Base sentences with an order (e.g. wallet_closure "moves any remaining balance out by cash-out first") ground no edge of this difficulty — nothing to record.

### override_declarations

- renewal_plan_fee vs `wallet_plan_fee`: s1 (charge on renewal date, amount monthly/annual, move renewal date) — superseded, declared; replacement covers monthly billing only (O-3: the annual half of s1 is dropped with nothing in the extended charter taking its place). s2 trial, s3 upgrade proration, s5–s6 annual refund window — different events, followed. s4 waiver — restated verbatim in substance ("The plan-fee waiver for restricted accounts still applies") ✓. s7 "Monthly plan fees … are never refunded …; a plan fee is not charged at all on a plan whose monthly_plan_fee is 0.00" — the 0.00 clause restated ✓; the restricted-days credit reduces the new period's fee and books no refund row, so it does not contradict "never refunded" on the scored quantity (the new fee's amount, whose override is declared). `wallet_funding_fees`, `wallet_instant_transfer_fee`, `wallet_evt_receiving`: no sentence governs the plan fee amount — followed.
- available_balance_transfer (`overwrite: []`) vs `wallet_instant_transfer_fee` s1 (standard cash-out free) — followed (no fee on the standard transfer). vs `wallet_cash_out_rules`: s1 status — extended keeps active/closure_pending and does not cover the closed-for-risk release, which remains governed by base s5 (one standard cash-out of the whole remaining balance) — no conflict because extended's own gate excludes that account; s2 cash_out_enabled inherited; s3 daily/instant limits restated; s4 ledger ceiling restated. No base sentence fixes the amount of a customer-chosen cash-out, so the hold deductions override nothing; `[]` is correct.
- protection_reimbursement vs `wallet_purchase_protection`: s1 coverage, s2–s3 window, s4 one-claim — followed/restated; s5 amount ("lower of the claim amount and purchase_protection_max_amount … together with the refund of any credit card funding fee") — superseded, declared. vs `wallet_unauthorized_claims`: its approval/reimbursement sentences are scoped to unauthorized claims (its s1); followed. No undeclared override.
- claim_money_instant_fee vs `wallet_instant_transfer_fee`: s3 quota (calendar month measure → rolling month less returns) declared; s4 rate choice (previous-calendar-month DD measure) declared, with "free quota takes precedence" and "rates never combine" preserved by the replacement; s5 (round then clamp → clamp then single rounding) declared; s2 fee row, s6 no courtesy waiver followed. vs `wallet_cash_out_rules` restated. `wallet_plan_fee`, `wallet_funding_fees`, `wallet_evt_receiving`: nothing on the instant fee — followed.
- No anonymous intermediate factor, no 0/1 multiplier on a base-fixed quantity, and no dropped branch except O-3. No author note calls base output a "wrong value".

### factor_ladders

| policy | factor | label | decides | tiers (fall-through incl.) | tiers in rule | multi-source (distinct records) | cross_difficulty |
|---|---|---|---|---|---|---|---|
| renewal_plan_fee | payroll_deposit_reduction | parameter | dd_discount_pct | 3 (25 / 10 / 0 %) | ✓ | count & total over the same DD rows — weak | — |
| | rewards_member_reduction | parameter | rewards_discount_pct | 3 (15 / 10 / 0 %) | ✓ | status & tier, one record | rewards |
| | vault_saver_reduction | parameter | vault_discount_pct | 3 (10 / 5 / 0 %) | ✓ | single field | savings (unclaimed category, O-8) |
| | debit_card_reduction | parameter | card_discount_pct | 3 (10 / 5 / 0 %) | ✓ | status & tier, one record | card |
| | restricted_days_credit | method | restricted_credit | 3 (full pro rata / pro rata beyond grace / none) | ✓ | reason & end date, one record | — |
| available_balance_transfer | advance_repayment_reserve | parameter | advance_reserve | 3 (100 / 50 / 0 % of outstanding) | ✓ | line status (advance_lines) & due date (advance_ledger) ✓ | advance |
| | sales_receipt_hold | method | sales_hold | 3 (2-month sum / 1-month sum / nothing) | ✓ | all-ever vs 3-month counts | — |
| | bank_topup_hold | parameter | topup_hold | 3 (100 / 50 / 0 %) | ✓ | age only | — |
| | business_shortfall_reserve | parameter | business_reserve | 3 (100 / 50 / 0 % of shortfall) | ✓ | profile balance & business_transactions sale count ✓ | business |
| protection_reimbursement | funding_fee_part | method | funding_fee_part | 3 written (whole fee / proportional fee / nothing) — **collapse, F-1** | ✓ | payment funding (payment row) & claim vs payment amount (claim row) ✓ | — |
| | seller_return_deduction | method | seller_deduction | 3 written (P + net G&S / P / nothing) — **collapse, F-2** | ✓ | same row set | — |
| | repeat_claim_share | parameter | coverage_share | 3 (80 / 90 / 100 %) | ✓ | claim rows | — |
| | rewards_protection_multiplier | parameter | ceiling_multiplier | 3 (2.0 / 1.5 / 1) | ✓ | status & tier, one record | rewards |
| claim_money_instant_fee | deposit_rate_tier | parameter | deposit_rate | 3 (dd rate − cut / dd rate / base rate) | ✓ | measure (DD rows over an age-selected window) & 1-month count | — |
| | deposit_measure_window | method | dd_measure | 3 (3-month avg / 2-month avg / 1-month total) | ✓ | age (wallet_accounts) & DD rows ✓ | — |
| | card_tenure_cut | parameter | card_cut | 3 (0.25 / 0.10 / 0 pp) | ✓ | status & activation date, one record | card |
| | balance_rate_cut | parameter | balance_cut | 3 (0.20 / 0.10 / 0 pp) | ✓ | balance & age, one record | — |
| | saver_fee_reduction | parameter | saver_pct | 3 (20 / 10 / 0 %) | ✓ | single field | savings (O-8) |

- Counts per policy (declared): renewal 5 (4 parameter, 1 method); transfer 4 (3 parameter, 1 method); reimbursement 4 (2 parameter, 2 method); claim-money 5 (4 parameter, 1 method). All within 4–6 with ≥2 parameter and ≥1 method as declared.
- Bindings of each factor are disjoint from the other factors' bindings; no `decides` is `result`.
- Every `baseline` binding equals what that policy's `baseline.rule` gives for the input (the baseline rules state the unreduced standard method, so each input's standard value is 0 %, 0, 100 % share, multiplier 1, base rate, 1-month DD total ... see note): renewal (all reductions 0, credit 0 = monthly_plan_fee) ✓; transfer (all holds 0 = ledger balance) ✓; reimbursement (fee part 0, deduction 0, share 100, multiplier 1 = min(claim, max)) ✓; claim-money (base rate, no cuts, no saver) ✓. Note on `deposit_measure_window`: its baseline `dd_1m` is not read by `baseline.rule` at all, because the baseline rate is `instant_transfer_fee_rate_pct` whatever the measure; substituting it alone is still meaningful because the gold deposit tier consumes it.
- Every fall-through tier is the baseline value. Each ladder's non-fall-through tiers are pairwise disjoint as stated.
- Realism: plan-fee loyalty discounts, a pro-rata credit for days lost to a takeover lock, holds on new-seller receipts and on young-account ACH top-ups, a reserve ahead of an advance autopay and against a negative business balance, a funding-fee refund on an approved claim, a seller-refund offset, a rewards-tier uplift of a protection ceiling, direct-deposit/tenure/balance/saver fee cuts — each is a treatment a US payments app plausibly publishes. Observation O-9 on the repeat-claim share.
- Label honesty: see F-1/F-2 (method ladders that are one formula written as several tiers) and O-7 (method ladders whose tiers substitute a window length or grace constant).

### findings

**F-1 — SOURCE-FACTOR RED (bears on task 1): `funding_fee_part` is one method written as three tiers.**
- Symptom: the ladder of `wallet_ext_protection_reimbursement.factors.funding_fee_part` lists "add the whole credit card funding fee" (claim covers the whole payment), "add the funding fee in proportion to the claim amount over the payment amount" (claim covers part), and "add nothing" (funded any other way).
- Root cause: the three tiers are cases of the single method "funding fee on the payment × claim amount ÷ payment amount". On the whole-payment tier the ratio is 1, so the proportional method returns the whole fee (a claim never exceeds the payment it disputes — the only situation where tier 1 and tier 2 differ); on the fall-through, `wallet_funding_fees` s1 books a credit_card_funding_fee only on a payment funded by a linked credit card, so `cc_fee` is 0 and the proportional method returns 0.
- Evidence: rule sentence "when the payment was funded by a linked credit card and the claim covers the whole payment amount, the whole funding fee is added; when it was funded by a linked credit card and the claim covers only part of the payment, the funding fee is added in the same proportion …; when the payment was funded any other way, nothing is added."; compute `funding_fee_part: "cc_fee if (... claim_amt >= pay_amt) else (RND(cc_fee * claim_amt / pay_amt, 2) if (...) else 0)"`; base `wallet_funding_fees` "A payment funded by a linked credit card carries a credit_card_funding_fee …; Payments funded by the balance, a linked bank account or a linked debit card carry no funding fee".
- Demonstrated consequence: see `1.md` (the adjacent tier's method on task 1's world returns the same figure as the tier taken). Struck as a factor, the reimbursement computation is left below four factors.
- Affected: extended charter, `wallet_ext_protection_reimbursement` rule sentence 4, `factors[funding_fee_part]`, compute `funding_fee_part`.

**F-2 — SOURCE-FACTOR RED (bears on task 1): `seller_return_deduction` is one method written as three tiers.**
- Symptom: tiers "deduct personal payments in full and goods-and-services payments net of the seller fee" / "deduct those personal payments in full" / "deduct nothing".
- Root cause: tier 1's method evaluated on a tier-2 world (no goods-and-services payment back) is `personal + net(0)` = personal in full, tier 2's outcome; evaluated on the fall-through world (nothing back) it is 0, the fall-through's outcome. Every tier is the one method "deduct what the customer netted from the seller".
- Evidence: rule sentence 5; compute `seller_deduction: "(back_personal + RND(back_gs * (1 - P('goods_services_fee_rate_pct') / 100), 2)) if back_gs > 0 else (back_personal if back_personal > 0 else 0)"` — the `else` branches are the `if` branch with back_gs = 0 (and back_personal = 0).
- Demonstrated consequence: see `1.md`.
- Affected: `wallet_ext_protection_reimbursement` rule sentence 5, `factors[seller_return_deduction]`, compute `seller_deduction`.
- Joint effect of F-1 and F-2 (charter-global): counting only rules that pass the ladder tests, `wallet_ext_protection_reimbursement` has 2 factors (repeat_claim_share, rewards_protection_multiplier), both `parameter`, 0 `method` — below the 4-factor floor and without a method factor.

**O-3 — observation: annual billing is dropped, and the transfer's prerequisite sentence is broader than its condition.** renewal_plan_fee supersedes the whole of `wallet_plan_fee` s1 (which covers monthly and annual) with a monthly-only replacement, and `charge_plan_fee_0f985a0a` accepts only a YYYY-MM billing period; the transfer's sentence waits on "a plan fee entry for every billing period whose renewal date has arrived" (any billing), while its `condition` reads only "a paid plan on monthly billing". For an annual-billing account on its renewal date the sentence blocks the transfer on an entry no write of this difficulty can book, and the condition says the edge holds. Neither task's world is on annual billing, so no scored solution is affected; recorded as observation.

**O-4 — observation: renewal-date anchor vs handling-date anchor.** Rule: deposits "dated later than the same calendar day one month before the renewal date"; period length "the calendar days from that date to the renewal date". Compute: `within_months=1` relative to NOW and `DAYS(period_start, NOW)`. Identical whenever the fee is booked on the renewal date; they diverge if booked later (which the transfer's condition "plan_renewal_date is on or before the handling date" contemplates). Task 0 books on the renewal date; no consequence.

**O-5 — observation: reimbursement selector scope.** `pp_txn`/`claim_amt` take the latest approved purchase-protection claim by resolution date without excluding one already reimbursed, and `prior_claims` subtracts 1 unconditionally (assuming the paid claim's filing lies inside the 12-month window). Rule: "only an approved purchase protection claim with no provisional credit is reimbursed, once" and "other than the one being paid". Task 1 has one approved claim, filed inside the window; no consequence.

**O-6 — observation:** `wallet_ext_available_balance_transfer.baseline.params` names `daily_cash_out_limit`, which `baseline.rule` never uses (the baseline figure is the ledger balance). The baseline still yields a definite number.

**O-7 — observation (label honesty, not red-lit):** `sales_receipt_hold` (sum over 2 / 1 / 0 months), `deposit_measure_window` (sum over 3 / 2 / 1 months divided by the same N) and `restricted_days_credit` (days to recovered date less 0 vs days to lifted date less review_grace_days vs none) can each be written as one formula with a substituted constant; the tiers nonetheless select different record windows/intervals and averaging vs totalling, which this auditor accepts as a `method` choice. Flagged for the coordinator's calibration; if the stricter reading is adopted, each of transfer and claim-money has no honest `method` factor.

**O-8 — observation:** `vault_saver_reduction` and `saver_fee_reduction` are labelled `cross_difficulty: savings`, but no difficulty in `blueprint.yaml` claims the savings category. Each task nevertheless has other cross-difficulty factors reading claimed difficulties (card, rewards, advance, business).

**O-9 — observation:** `repeat_claim_share` lowers purchase-protection coverage to 90 % / 80 % for customers with earlier claims, counting denied claims. Unusual for a payments-app buyer protection, but not demonstrably a treatment no business would publish.

**O-10 — observation:** `instant_used` subtracts `wallet_cash_out_return` rows filtered by `transfer_speed='instant'`; whether return rows carry the original transfer speed is not stated by the charter. Neither world has a return.

**O-11 — observation:** "Where rate adjustments apply, the instant fee rate is the deposit rate tier less …" makes the deposit tier conditional on "adjustments applying"; a reader could take "adjustments" to mean only the two cuts, so that with a deposit tier but no cut the rate falls back to instant_transfer_fee_rate_pct. Task 1's customer has both cuts, so no second reading arises there.

## closing_checklist

Written after both reveals (2026-09-25T00:08:38Z); nothing above this heading was changed after the reveal.

- Not closed in r1: task 0 SOURCE-FACTOR RED (`0.md` T0-F1, a false near-miss assertion in the proof; scored values correct), task 1 SOURCE-FACTOR RED (`1.md` T1-F1, resting on F-1 and F-2 above). Policy self-consistency, the problem tree and the unique solution PASS on both tasks; both blind derivations land on GT value for value (every write argument, every expected, baseline_result and factor_sensitivity figure, and the prerequisite_closure values).
- Items that already hold: one audit file per task (`0.md`, `1.md`) beside this file; `charter_scope` of the two tasks is {renewal_plan_fee, available_balance_transfer} and {protection_reimbursement, claim_money_instant_fee} — pairwise disjoint and together covering all four extended policies and all four task tools; each tree has 1 prerequisite problem, 1 value_input edge, an owner=user root and no cycle, and the difficulty's graph (two disjoint edges) is acyclic; uuid8s independent.
- Items that do not yet hold: the reimbursement computation's factor floor (F-1, F-2); the task-0 proof sentence (T0-F1).
- Gate re-run on the final form: not performed by this auditor (the brief supplies the coordinator's snapshot; this skill cites it and does not run the gates).

## revision_2

### charter_global_frozen (r2)

- Freeze 2026-09-25T00:30Z (before any r2 task JSON was read). Auditor: same independent auditor as r1.
- Shared inputs changed, so every charter-global section is re-derived in full: `wallet.extended.yaml` r1 `78c8f538…3726` → r2 `d1b48c7d92c85628a5c0d4e67bfc1415d429969061e65c75c768450ca3cc8a1e`; `task_tools.py` r1 `e619d5c4…652da` → r2 `a638c39cd956444b7ca00d050edbdc95ddb65372ec2d452022f5846dd7a0a8a8`. Base section still verbatim (`diff` of lines 1–1491 against `blueprint/products/wallet.yaml` is empty).
- Gate snapshot `coord/snap/d1_r2.txt`: EXTENDED, TASK TOOL CONTRACT, REPLAY (0.json 15 acts / 36 rows, 1.json 12 acts / 32 rows), SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK. Masked r2 views verified: `0.view.json` 4d45939d…226a, `1.view.json` 7429ad3c…ae32.
- Masked when this section was written: r2 `tasks/*.json`, both worklogs, scratchpad.
- contamination_disclosure (r2): this auditor read the r1 GT of both tasks at 00:08:38Z. The r2 charter-global sections below are built from the r2 charter and tools alone, but the auditor's knowledge of the r1 scored values and conventions cannot be removed; the r2 per-task derivations are independent recomputations, not blind derivations, and are labelled so in each task file.

### what changed in the charter (r1 → r2)

- renewal_plan_fee: an annual-billing sentence was added to the rule and the baseline (annual_plan_fee, billing period = year, renewal moves one calendar year; reductions and credit monthly-only); `result` branches on `billing_cycle == 'annual'`; the DD window and period length are anchored on the handling date; the vault sentence adds "(a vault that is time_locked, frozen or closed does not count)"; `baseline.params` adds annual_plan_fee. Factors unchanged.
- available_balance_transfer: `baseline.params` is now `[]`; the prerequisite `condition` now reads "a paid plan (monthly or annual billing)". Rule and factors unchanged.
- protection_reimbursement: rewritten. funding_fee_part and seller_return_deduction are gone as factors; the funding-fee part (pro rata) and the seller deduction (personal in full + G&S net) are now part of the covered amount in the rule and in `baseline.rule`. New sentence "The claim paid is the purchase protection claim most recently approved on the account, and it is paid once …". New factors `claim_lookback_window` (method: count other claims over 6 / 9 / 12 months by account age 730 / 365 days) and `claim_review_delay_credit` (parameter: +2 % / +1 % / 0 % for 30+ / 15+ / under-15 days from report to approval); `repeat_claim_share` now counts inside the look-back window; `rewards_protection_multiplier` unchanged. `prior_*` bindings subtract the paid claim's own filed rows.
- claim_money_instant_fee: quota sentence adds "(a return carries the speed of the transfer it returns)"; the rate sentence now reads "Whatever deposit rate tier applies, the instant fee rate is that tier less the card-tenure rate cut and less the balance rate cut (each cut being 0 where it does not apply)"; vault parenthesis as above. Factors unchanged.
- task_tools.py: only `charge_plan_fee_0f985a0a`'s docstring changed (monthly or annual; billing_period YYYY-MM or YYYY). Bodies of all four tools still perform only create/update with caller values — no branch, raise or prerequisite read. uuid8s unchanged (0f985a0a, 3181bc35, 5be5cf5a, cd9063e1).

### policy_conflict_scan (r2)

Same four policies, owners, tools, triggers and subjects as r1; no two policies decide the same written quantity. The annual branch now lives in renewal_plan_fee alone. Cross-category reads unchanged (reimbursement still reads only rewards). No new conflict.

### rule_compute_equivalence (r2)

- renewal: the anchor divergence of r1 O-4 is gone for the DD window (rule and compute both relative to the handling date). Residual: the period is still called "the billing period that ends on the renewal date" while its length runs "to the handling date"; the two coincide when the fee is booked on its date (O2-1). Annual branch: rule sentence 2 ↔ `result` `RND(P('annual_plan_fee'), 2) if F('billing_cycle') == 'annual'` ✓. Vault parenthesis ↔ `status='active'` ✓.
- transfer: unchanged, ✓.
- reimbursement: pp_txn "most recently approved" ✓; funding_fee_part "same proportion … nothing when no such fee" ↔ `RND(cc_fee * claim_amt / pay_amt, 2) if pay_amt > 0 else 0` ✓ (cc_fee is 0 when no fee is booked); seller_deduction ↔ `back_personal + RND(back_gs * (1 − rate))` ✓; look-back ladder ↔ `prior_claims` selector ✓, "other than the claim being paid" ↔ subtraction of the paid claim's own filed rows in the same window ✓; delay credit "calendar days from the paid claim's report date to its approval date" ↔ `DAYS(pp_reported, pp_approved)` on the approved row ✓; order "multiplied by the coverage share, then raised by the delay credit percentage, only this figure compared with the raised ceiling … never below 0.00 … rounded once" ↔ `result` ✓. "paid once: a claim whose disputed payment already carries a reimbursement entry is not paid again" is an eligibility sentence and has no compute counterpart, correctly (O2-2 on its interaction with the prerequisite).
- claim-money: returns carry the transfer speed ↔ `transfer_speed='instant'` on the return count ✓ (r1 O-10 closed); rate sentence ↔ `fee_rate = MX(floor, deposit_rate − card_cut − balance_cut)` ✓ unconditionally (r1 O-11 closed).

### action_binding_and_uuids (r2)

Unchanged from r1 and still PASS: four `(target_tool, computes)` pairs each claimed once; owners as r1; tool bodies judge nothing; docstrings name no other tool and no position in a sequence; uuid8s independent.

### prerequisite_graph and prerequisite_sentences (r2)

- Graph unchanged: transfer → renewal_plan_fee (value_input, ledger_now, state), claim-money → protection_reimbursement (value_input, reimb_amt, state); acyclic; policy_sources verbatim in the blocked rules.
- Transfer edge: `condition` now covers "a paid plan (monthly or annual billing)", equal in scope to the sentence "every billing period whose renewal date has arrived"; and `charge_plan_fee_0f985a0a` now accepts a YYYY billing period, so the waited-on state is reachable on annual billing too. r1 O-3 closed.
- Claim-money edge: unchanged, four-point test passes; single resolving write. O2-2: the reimbursement rule now pays only "the purchase protection claim most recently approved"; in a world with two approved unpaid claims the earlier one could never carry its entry and the claim-money sentence ("every approved purchase protection claim … carries its reimbursement entry") could never be met. Neither task's world has two approved claims — observation.

### override_declarations (r2)

- renewal vs `wallet_plan_fee` s1: the declared supersession stays; the annual half of s1, dropped in r1, is now restated in the extended rule (annual_plan_fee, year billing period, one calendar year) — r1 O-3's dropped branch closed. The restatement omits s1's "falling back to the last day of the month when that day does not exist" for annual renewals (O2-3, only a 29 February renewal is affected).
- reimbursement vs `wallet_purchase_protection` s5: still declared; the replacement ("already includes any credit card funding fee part") is what the rule's covered amount now computes pro rata. No undeclared override.
- claim-money: the three declared overwrites unchanged; the added parentheticals do not touch a base sentence.
- transfer: `[]` still correct.

### factor_ladders (r2)

| policy | factor | label | tiers | multi-source | cross_difficulty |
|---|---|---|---|---|---|
| renewal | payroll_deposit_reduction / rewards_member_reduction / vault_saver_reduction / debit_card_reduction | parameter | 3 each, unchanged | as r1 | — / rewards / savings / card |
| renewal | restricted_days_credit | method (label test below) | 3 | one record | — |
| transfer | advance_repayment_reserve / bank_topup_hold / business_shortfall_reserve | parameter | 3 each, unchanged | advance ✓, business ✓ | advance / — / business |
| transfer | sales_receipt_hold | method (label test below) | 3 | — | — |
| reimbursement | claim_lookback_window | method (label test below) | 3 (6 / 9 / 12 months by age 730 / 365) | age only | — |
| reimbursement | repeat_claim_share | parameter | 3 (80 / 90 / 100 %) | claim rows | — |
| reimbursement | claim_review_delay_credit | parameter | 3 (2 / 1 / 0 %) | report and approval dates of one claim | — |
| reimbursement | rewards_protection_multiplier | parameter | 3 | one record | rewards |
| claim-money | deposit_rate_tier / card_tenure_cut / balance_rate_cut / saver_fee_reduction | parameter | 3 each, unchanged | deposit_rate_tier: 3-month measure and 1-month count read different deposit sets (accepted, weak) | — / card / — / savings |
| claim-money | deposit_measure_window | method (label test below) | 3 | age only | — |

- The collapsed ladders of r1 F-1 and F-2 no longer exist as factors: the funding-fee part and the seller deduction are single rules of the covered amount, stated in `baseline.rule`. **F-1 and F-2 are closed.**
- No two tiers of any r2 ladder select the same value; every tier is stated in its rule and implemented in compute.
- claim_review_delay_credit (a percentage uplift when review took long) and the age-dependent look-back are treatments a payments app could publish; accepted.

#### Decision on the O-7 calibration (the label of window-length and constant-substitution `method` factors)

The coordinator returned this question to the auditor. Decision, by the skill's own words: a tier is `method` only if it "changes the algorithm", and a factor is mislabelled when "its tiers only substitute a different number into the same formula (a rate, a fee, a threshold)". The test applied: write one formula with a free constant; if that single formula, with the constant each tier names, reproduces every tier's outcome (the fall-through included), the tiers substitute a number and the factor is `parameter`, whatever the tier prose says. In r1 this auditor accepted such factors because they "select different record windows"; on re-examination that is exactly what a changed number in the same aggregate does, so r1's acceptance was too lenient. This is a change of the auditor's calibration, not a regression introduced by the rework, and it is recorded as such.

Applying the test to every `method` factor of the charter:

| factor | single formula reproducing every tier | constant substituted | verdict |
|---|---|---|---|
| restricted_days_credit (renewal) | discounted fee × max(0, days of the most recent restriction inside the ending period − g) ÷ period length, where the restriction's days run from the later of its start and the period start to its end (recovered or lifted date); no restriction ending in the period → 0 days | g = 0 (lock) / review_grace_days = 5 (limitation) | parameter — **mislabelled** |
| sales_receipt_hold (transfer) | sum of G&S receipts dated in the last N months | N = 2 (new seller) / 1 (established) / any N on an empty set (never received) | parameter — **mislabelled** |
| claim_lookback_window (reimbursement) | count of other PP claims reported in the last N months | N = 6 / 9 / 12 | parameter — **mislabelled** |
| deposit_measure_window (claim-money) | total of DDs dated in the last N months ÷ N | N = 3 / 2 / 1 (a one-month total is the one-month average) | parameter — **mislabelled** |

**F2-1 — SOURCE-FACTOR RED (bears on tasks 0 and 1): no computation of the charter has an honest `method` factor.** Symptom: each of the four policies declares exactly one `method` factor. Root cause: each of those four factors' tiers substitute a constant into one formula (table above). Evidence: the rule sentences of each factor (renewal rule sentences 10–11; transfer rule sentence 6; reimbursement rule sentence 7; claim-money rule sentence 7) and their compute bindings (`restricted_credit`, `sales_hold`, `prior_claims`, `dd_measure`), each of which evaluates to the one formula of the table. Demonstrated consequence: counting only honestly labelled factors, every computation has 0 `method` factors against a floor of 1; the per-task files show it on each world. Affected: `wallet.extended.yaml` `factors[restricted_days_credit]`, `factors[sales_receipt_hold]`, `factors[claim_lookback_window]`, `factors[deposit_measure_window]`, and the four computations of `tasks/0.json` and `tasks/1.json`.

### r1 findings — status (charter-global, pre-reveal)

| id | r1 | r2 status | evidence |
|---|---|---|---|
| F-1 | RED | **closed** | funding_fee_part no longer a factor; pro-rata funding fee is a baseline rule |
| F-2 | RED | **closed** | seller_return_deduction no longer a factor; baseline rule |
| O-3 | obs | closed | annual sentence + tool YYYY + condition "monthly or annual" |
| O-4 | obs | mostly closed; residual O2-1 | DD window and period length anchored on the handling date |
| O-5 | obs | closed | "paid once" sentence; `prior_*` subtract the paid claim's rows; new O2-2 on multiple approved claims |
| O-6 | obs | closed | `baseline.params: []` |
| O-7 | obs | **escalated to F2-1** by the auditor's calibration decision | above |
| O-8 | obs | unchanged (savings unclaimed) | — |
| O-9 | obs | unchanged (repeat-claim share realism) | — |
| O-10 | obs | closed | "a return carries the speed of the transfer it returns" |
| O-11 | obs | closed | "Whatever deposit rate tier applies …" |

New observations: O2-1 (period "ends on the renewal date" yet its length runs to the handling date), O2-2 (only the most recently approved claim is payable, while the claim-money sentence waits on every approved claim), O2-3 (annual renewal restatement omits the last-day-of-month fallback).

### closing_checklist (r2)

Written after the r2 reveals (2026-09-25T00:30:31Z); nothing in `## revision_2` above this heading was changed after them.

- r1 REDs: F-1, F-2, T1-F1, T0-F1 — **all genuinely closed** (evidence in the r2 sections of `_difficulty.md`, `0.md`, `1.md`). r1 observations O-3, O-5, O-6, O-10, O-11, T0-O2, T1-O2 closed; O-4 closed but leaves O2-1; T1-O3 addressed; O-8, O-9, T0-O1, T1-O1 unchanged and still observations.
- Regression check: no regression. Both r2 derivations land on r2 GT value for value (every write argument, expected, baseline_result, factor_sensitivity figure and prerequisite_closure value). Policy self-consistency, the problem tree and the unique solution PASS on both tasks; scopes disjoint and complete; graph acyclic; tools judge nothing; uuid8s unchanged and independent.
- Not closed: F2-1 (SOURCE-FACTOR RED on both tasks). It comes from the auditor's decision on the O-7 calibration, which the coordinator returned to the auditor. It is not a defect the rework introduced, except that the rework's new `claim_lookback_window` has the same shape. Per-task: `0.md` T0-F2, `1.md` T1-F2.
- New observations: O2-1, O2-2, O2-3 (charter), T0-O3, T1-O4 (tasks).
- Gate re-run: not performed by this auditor; the coordinator's r2 snapshot (all OK) is cited.

## revision_3

### charter_global_frozen (r3)

- Written before any r3 task JSON was read. Auditor: same.
- `wallet.extended.yaml` r2 `d1b48c7d…8a1e` → r3 `d6b0e9f41aecbbc1967adbc4e87f286fe06cc7a1c646466f1b2e82be4d123903` (changed → charter sections re-derived); `task_tools.py` `a638c39c…a8a8` unchanged since r2 (the r2 `action_binding_and_uuids` conclusion is carried forward on that hash). Base section still verbatim. Gate snapshot `coord/snap/d1_r3.txt`: all seven gates OK (replay 15/36 and 12/32, match True). Masked views: r3 `0.view.json` 6aa148d7…13c9 (persona changed, initial_state identical to r2), r3 `1.view.json` 7429ad3c…ae32 (identical to r2).
- contamination_disclosure (r3): as in r2 — the auditor has read the r1 and r2 GT of both tasks; the r3 per-task sections are independent recomputations, not blind derivations.

### what changed in the charter (r2 → r3)

- renewal: the restricted-days credit's limitation tier is now "all or nothing — the whole discounted fee when the days … are more than half the period's length, and nothing when they are not" (compute `discounted_fee if DAYS(…) * 2 > period_days else 0`); `review_grace_days` removed; the period is "the ending billing period, which runs from the date of the previous plan fee entry to the handling date … and whose length is the calendar days between those two dates"; the annual sentence adds the last-day-of-month fallback.
- transfer: established-seller tier of the sales receipt hold is now "only the single most recent goods-and-services payment it received is held" (compute `gs_latest`, LATEST by txn_date); `gs_1m` removed.
- reimbursement: `claim_lookback_window` relabelled `parameter` (tier values "a six- / nine- / twelve-month look-back"); `claim_review_delay_credit` relabelled `method`: 30+ days → simple interest at `delay_interest_pct` 18 % a year × review days ÷ 365 on the amount after the coverage share; 15–29 days → flat 1 %; under 15 → none (compute `shared_amount`, `delay_credit`; `result` = RND(MX(0, MN(shared_amount + delay_credit, ceiling)))).
- claim-money: the prerequisite sentence now waits on "the purchase protection claim most recently approved on the account" (condition: the latest approved PP claim by resolution_date carries a reimbursement entry); the direct deposit measure is now the middle value of the last three monthly totals (≥ 365 days), the lower of the last two monthly totals (≥ 180 days), or the last month's total, the monthly total N months back being "the deposits dated inside the window of N months less those dated inside the window of N − 1 months" (compute `dd_month2`, `dd_month3`, `dd_median3` = sum − max − min, `dd_lower2` = MN).

### rule_compute_equivalence (r3)

Each new sentence ↔ binding checked: all-or-nothing "more than half" ↔ `* 2 > period_days` ✓; period "from the previous plan fee entry to the handling date" ↔ `DAYS(period_start, NOW)` ✓ (r2 O2-1 closed); annual fallback ✓ (O2-3 closed); `gs_latest` ↔ "the single most recent goods-and-services payment it received" ✓; `delay_credit` ↔ interest / flat / none ✓ and `result` order "multiplied by the coverage share, the claim-review delay credit is then added … compared with the raised ceiling" ✓; median / lower / last-month ↔ `dd_median3`, `dd_lower2`, `dd_1m` with monthly totals as window differences ✓. No orphan params remain (`review_grace_days`, `delay_long_pct`, `gs_1m`, `dd_2m_avg`, `dd_3m_avg` all gone). Unchanged policies' sections as r2.

### prerequisite_graph and prerequisite_sentences (r3)

Graph unchanged and acyclic. Claim-money sentence "An instant cash-out of claim money is priced only after the purchase protection claim most recently approved on the account carries its reimbursement entry." — "only after" ✓, record-visible state ✓, no tool/id ✓, scope now equals both the condition and the reimbursement rule's "The claim paid is the purchase protection claim most recently approved on the account" ✓; the single resolving write is `post_protection_reimbursement_5be5cf5a`. r2 O2-2 closed. Transfer edge unchanged, ✓.

### override_declarations (r3)

No overwrite entry changed; the new tiers touch no base sentence (base has no restricted-days credit, no sales hold, no delay credit, and the DD measure's base form is already declared superseded). Unchanged conclusions from r2.

### factor_ladders (r3) — label test re-applied (same test as the r2 decision on O-7)

| factor | tiers | one formula with a substituted constant reproduces them? | verdict |
|---|---|---|---|
| restricted_days_credit (renewal, method) | pro rata by locked days / whole fee iff limited > ½ period else 0 / none | no — a proportional share vs a threshold step function | honest `method` ✓ |
| sales_receipt_hold (transfer, method) | sum of 2-month G&S receipts / the single latest receipt / nothing | no — a windowed sum vs a latest-row read | honest `method` ✓ |
| claim_lookback_window (reimbursement, parameter) | 6 / 9 / 12-month look-back | yes — a number, now labelled `parameter` | honest `parameter` ✓ |
| claim_review_delay_credit (reimbursement, method) | interest × days ÷ 365 at 18 % / flat 1 % / none | no — a day-proportional accrual vs a flat percentage | honest `method` ✓ |
| deposit_measure_window (claim-money, method) | median of 3 monthly totals / minimum of 2 / last-month total | no — median vs minimum vs single total | honest `method` ✓ |

- Counts: renewal 5 (4 parameter, 1 method); transfer 4 (3 parameter, 1 method); reimbursement 4 (3 parameter, 1 method); claim-money 5 (4 parameter, 1 method). Every ladder has three tiers with distinct outcomes, stated in the rule and implemented in compute; each fall-through is the baseline.
- Realism: an all-or-nothing fee credit for a limitation spanning most of a period, holding only the latest receipt for an established seller, prompt-payment interest (18 % a year is a common statutory prompt-pay rate) on slow claim decisions, and a median-of-months income measure for tenured accounts are treatments a payments business plausibly publishes. Accepted.
- **F2-1 is closed.**

### r2 findings — status (charter-global)

| id | r2 | r3 |
|---|---|---|
| F2-1 | SOURCE-FACTOR RED | **closed** (table above) |
| O2-1 | obs | closed |
| O2-2 | obs | closed |
| O2-3 | obs | closed |
| O-8, O-9 | obs | unchanged, still observations |

No new charter-global finding.

### closing_checklist (r3)

Written after the r3 reveals (2026-09-25T00:40:02Z); nothing in `## revision_3` above this heading was changed after them.

- r2 REDs: F2-1, T0-F2, T1-F2 — **all genuinely closed**. r2 observations O2-1, O2-2, O2-3, T0-O3, T1-O4 closed.
- Regression check: no regression. Both r3 recomputations match r3 GT on every write argument, expected, baseline_result, factor_sensitivity figure and prerequisite_closure value.
- Per-task verdicts r3: task 0 **PASS** on all four relationships; task 1 **SOURCE-FACTOR RED** on T1-F3 only (a false intermediate, 44.8957 for 44.90, in three proof fields of `tasks/1.json`; scored values correct), plus observation T1-O5 (stale factor_trace label).
- Difficulty-level items that hold: one audit file per task beside this one, all revisions appended with older text untouched; the extended charter is fully covered by the two disjoint scopes; each tree has 1 prerequisite problem, 1 value_input edge, an owner=user root and no cycle, and the difficulty graph is acyclic; the task tools are closed, judge nothing, and use independent frozen uuid8s; every computation has 4–5 factors with ≥2 parameter and exactly 1 honest method, three-tier ladders stated in their rules, honest baselines whose fall-back numbers (9.99, 4343.38, 2500.00, 25.00) differ from gold, every factor bearing weight, a genuine near-miss per computation, and per task at least one multi-source and one cross-difficulty factor on seeded rows.
- Not yet closed: T1-F3. The difficulty is not closed in r3.
- Gate re-run on the final form: not performed by this auditor; the coordinator's r3 snapshot (all OK) is cited.

## revision_4

### charter_global (r4) — carried forward

- Written 2026-09-25T00:43:59Z. `wallet.extended.yaml` `d6b0e9f4…3903` and `task_tools.py` `a638c39c…a8a8` are byte-identical to r3 (sha256 re-computed), so every charter-global section of `## revision_3` (and the r2 action-binding section it carries) stands unchanged on those two hashes; nothing is re-derived. Base section still verbatim.
- Masked views r4 = r3 (0.view 6aa148d7…13c9, 1.view 7429ad3c…ae32, re-hashed).
- Gate snapshot `coord/snap/d1_r4.txt`: all seven gates OK.
- contamination_disclosure: as r2/r3 — the auditor knows every earlier GT; r4 per-task derivations are carried forward, not re-derived blind.

### closing_checklist (r4)

- r3 RED T1-F3: **genuinely closed** (`1.md` `## revision_4`). r3 observation T1-O5 closed.
- Regression check: none. Both task files' scored fields (every write argument, expected, baseline_result, factor_sensitivity, prerequisite_closure values, charter_scope) equal the r3 values the auditor recomputed; `user_scenario`, `initial_state` and `frozen_time` of both task files equal the r4 views.
- Per-task verdicts r4: task 0 **PASS**, task 1 **PASS** on all four relationships.
- Step 4 checklist:
  - one audit file per task (`0.md`, `1.md`) beside this one; revisions 1–4 appended, older text untouched; each task's latest comparison section carries PASS ✓;
  - the four extended policies are covered by the two disjoint scopes (task 0: renewal_plan_fee + available_balance_transfer; task 1: protection_reimbursement + claim_money_instant_fee), task tools and GT closed, each task tool with an independent frozen uuid8 ✓;
  - each tree: 1 prerequisite problem, 1 value_input edge (≥ max(n−1,1) = 1), an owner=user root, no cycle; the difficulty graph (two disjoint edges) is acyclic ✓;
  - each computation: a self-sufficient baseline (fall-backs 9.99, 4343.38, 2500.00, 25.00, all ≠ gold), 4–5 factors with ≥ 2 parameter and exactly 1 honest method, every ladder three tiers stated in its rule with distinct outcomes and realistic conditions, every factor bearing weight, a genuine near-miss per computation; per task ≥ 1 multi-source (task 0: advance and business reserves; task 1: deposit_rate_tier, weak) and ≥ 1 cross-difficulty factor on seeded rows ✓;
  - instantiation-stage gates on the final form: the coordinator's r4 snapshot (all OK) is cited; this auditor does not run them.
- Open observations (not grounds for rework): O-8 (savings labelled cross-difficulty, no difficulty claims savings), O-9 (repeat-claim share realism), T0-O1 / T1-O1 (passive persona lines), and new in r4 T0-O4, T0-O5, T1-O6 (see the task files).
- **The difficulty passes the source-layer audit in r4.**
