# Policy-task audit — gap_waiver_claims / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-22T03:15Z (before any task GT was revealed), auditor: independent erl-task-policy-audit agent (not the instantiator).
- Inputs read: `blueprint/products/gap.yaml` (+ the vsc/maintenance/purchase charters only for the cross-category rows the policies read), `blueprint/db_schema.json`, `blueprint/share_tools.py`, `tasks/gap_waiver_claims/gap.extended.yaml` sha256 `685f7ab918ac01138c103016618a7bd3f7b9ee8ae2ca8c7ed078090b7371e062`, `tasks/gap_waiver_claims/task_tools.py` sha256 `2d25ba499d417444a2ef8565b0deb480f190fe8024d9b48d20d0b837e1107703`, `audits/render_source/XF_recipe.md`, DSL semantics from `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`).
- Hashes equal the coordinator's gate snapshot (685f7ab918ac / 2d25ba499d41). Masked views used: `r1/0.view.json` sha256 9dc88e186ddabaf9…, `r1/1.view.json` sha256 833381f328fa28a6… (both re-hashed, match).
- Masked / not read before freeze: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`; `plan.md`, `worklog.md`; prior audits. No recursive grep was run over `tasks/` or the scenario tree.
- Entry conditions: gate snapshot with command lines and OK lines supplied (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK); masked views with hashes supplied. Entry complete.
- Base copy: every base key of `gap.extended.yaml` (category … policies) is equal to `blueprint/products/gap.yaml` (programmatic dict equality, all True).

Policy ids used below: P1 `gap_ext_holder_cancellation_refund`, P2 `gap_ext_lienholder_refund_release`, P3 `gap_ext_balance_benefit`, P4 `gap_ext_addon_overpayment_recovery`, P5 `gap_ext_payoff_termination_refund`, P6 `gap_ext_holder_refund_release`, P7 `gap_ext_replacement_credit`.

### policy_conflict_scan
- Subjects / tools: P1 confirm_gap_cancellation (gap_waiver_cancelled+refund_calculated), P2 release_refund_lienholder (refund_paid, payee lienholder, loan open), P3 pay_gap_balance (benefit_paid gap_balance + claim_settled), P4 recover_benefit_overpayment (benefit_reversed), P5 terminate_paid_off_waiver (terminated+refund_calculated), P6 release_refund_holder (refund_paid, payee holder, payoff on file), P7 apply_replacement_allowance (benefit_paid replacement_vehicle_credit). One (target_tool, computes) per policy.
- **Overlap P1 × P5 (finding C1).** P1 rule: "This policy prices the cancellation refund booked when the holder confirms a signed cancellation request recorded for an active waiver; a termination after a lienholder payoff report is outside it." and its effective-date ladder tier "where the lienholder's reported loan payoff date is earlier than the signed request date, the cancellation is effective on that payoff date". P5 rule: "This policy prices the termination refund booked when an active waiver whose loan the lienholder has reported paid off or refinanced away (loan_payoff_date on file) is terminated; a holder's cancellation on a signed request is outside it." Base (not retired for this case): "Where refund_on_payoff_automatic is true, a waiver whose contract the lienholder reports paid off … is terminated". World: active waiver, loan_payoff_date on file, a submitted signed request dated after the payoff. P1 → cancellation (confirm_gap_cancellation, effective = payoff date, P1 charges/admin 40/60/bundle recapture); P5/base → termination (terminate_paid_off_waiver, P5 ladders, admin 30/45, retention, trade credit). Each policy excludes the other only by naming the other's outcome, so the world is claimed by both: two tools, two terminal statuses (cancelled vs terminated), two amounts.
- Payee boundary P2 / P6: P2 only while loan_payoff_date empty, P6 only with it on file; sibling overwrites of the same base sentence each exclude the other by name. No overlap.
- Time anchors: P1 effective date (signed / recorded / payoff), P5 (sale date / replacement contract_date / payoff date), P2/P6 effective date = closed_date. Consistent between writer and reader policies (P2 and P6 read the closed_date the writer set).
- Cross-category read boundaries: P1 purchase(variant,status), vsc(status), maintenance(status); P2/P6 purchase(contract_apr); P3 purchase(trade figures, variant, cash_price); P4 maintenance(plan, closed_date, refund_paid ledger), purchase(contracted deal); P5 purchase(waiver deal variant/AF, contracted deal); P7 purchase(contracted deal, stores). All reads; no task tool writes another category (checked in task_tools.py bodies).
- Scope partition (pre-reveal, from the trees the policies' prerequisite fields imply): {P2,P1,P3} and {P7,P4,P6,P5} — the seven policies are covered and the two sets are disjoint. Confirmed against the charter_scope fields only after reveal (see closing section).

### rule_compute_equivalence
Mechanical sweep: every `compute_basis` quote is verbatim in its rule (0 misses); every baseline.rule sentence is in the rule (0 misses); every overwrite's superseded_clause is verbatim in the cited base rule and every replaced_by is verbatim in the extended rule; every factor ladder tier appears as a rule sentence and as a branch of its decides binding. Two-way content sweep findings:
- **C4 (P2, P6 late-interest gate).** Baseline sentence kept in both rules: "Where the release is made more than refund_payment_days calendar days after the effective date of the cancellation, late-release interest is added …" (P6: "Where the holder release is made more than refund_payment_days calendar days after the effective date of the termination, holder late interest is added …"). The interest-days ladders' tiers 1/2 ("interest runs for every calendar day from the signed date to the release date", "…from the recorded date…"; P6 "…from the effective date…", "…from the loan_payoff_date…") and the compute (`late_interest: RND(refund_due * (interest_rate + rate_premium) * interest_days / 365.0, 2)` with no window test) add interest when the release is inside the window. World: P2, request recorded the day it was signed, release 20 days after the effective date → rule gate: no late-release interest (refund only); ladder/compute: 20 days of interest at the contract APR. Two amounts.
- **C5 (rounding mode).** Every rule says only "rounded to the cent"; every money arg docstring in task_tools.py says "rounded half up to the cent before it is passed"; the compute's `RND` is `round(float(x), 2)` (Python round: an exactly representable half rounds to even). On an exact tie the docstring's convention and the compute disagree (demonstrated on task 0: 825 × 57/72 = 653.125 exactly → RND 653.12, half up 653.13).
- **C6 (zero APR, P2/P6).** Rule: "where it carries a contract APR of apr_floor_pct or less, the interest runs at apr_floor_pct". Compute: `… if (deal_apr and float(deal_apr) > K('apr_floor_pct')) else (K('apr_floor_pct') / 100.0 if deal_apr else K('standard_late_rate'))` — a contract_apr of 0.00 (a financed deal at 0.00 APR; purchase charter: "A financed deal names its lienholder, amount financed, lender buy rate and contract APR", nothing bars 0.00) is falsy and lands on standard_late_rate (5 %) instead of the floor (7 %; P6 6 %).
- **C7 (absent-record probes).** P3 rule: "A waiver with no claim line for the GAP balance on file has no claim figures, and its GAP balance line is 0.00." Compute `payoff: float(LATEST(...))` raises on None before `result` is reached → no number. P4 rule: "A waiver with no paid GAP balance line on file has no add-on overpayment reversal." Compute `addon_counted: 0.0 if plan_effective < line_loss_date …` compares a str with None when the waiver has no ledger rows (TypeError), and with `''`/None `line_paid_date` when only non-claim rows exist. P7 rule: "A waiver with no paid GAP balance line on file receives no replacement vehicle credit." Compute evaluates `DAYS(line_paid_date, repl_signed)` with line_paid_date None whenever a new-vehicle contracted deal exists → error before the guarded `result`.
- **C8 (P4 claim-figure source).** P4 rule: "the claim figures are those on the waiver's most recent claim line, paid or denied: the loss type, the loss date, the insurer's settlement date and deductible and the add-on refunds recorded" and, in the same rule, "The uncredited plan refund is the plan refund received less the add-on refunds recorded on the paid line", "the insurer's deductible on the paid line", "The reversal loss-age is whole calendar months from sale_date to the loss date of the paid line". Compute: `line_loss_type/line_loss_date/line_settlement_date/line_deductible/line_credited: LATEST('gap_ledger', <field>, date_field='entry_date')` with **no** event_type / benefit_line_type filter (every ledger row of the waiver). World: a denied replacement-credit line (base gap_claim_denied writes no deductible / add-on figures, so 0.00) dated after the paid GAP balance line → "most recent claim line" reading and compute take deductible 0.00 / credited 0.00 from the denied line; the "paid line" reading takes the paid line's figures → different uncredited refund and loss allowance.
- **C10 (month-end convention).** P1, P3, P4, P5, P6, P7 state "whole calendar months from X to Y" with no month-end rule; compute `MONTHS()` drops a month whenever the end day-of-month is smaller than the start's. Example P5 whole-month share: effective 2026-01-31, expiration 2030-06-30 → MONTHS = 52; reading June 30 as the month-end anniversary of Jan 31 gives 53. Not reached in either task world (task 0: 2026-08-26→2031-06-20; task 1: 2026-09-18→2029-05-20).
- Sweep-back otherwise clean: no compute binding without a rule sentence; P3/P5/P7 assembly-order sentences match the compute order.
- **C9 (decoy / second-record reads, XF9/XF12).** (a) P4, P5, P7 read "the holder's group purchase deal in contracted status" through `CFIELD('purchase', <field>, status='contracted')` = first match over all the customer's deals; the rule speaks of one such deal and states no rule for two (a household with two signed, undelivered orders is producible) → the bonus / allowance / effective-date tier rests on dict order. P5 and P7 even read different fields of possibly different first matches only by luck of the same order. (b) P2 `signed_date` / `recorded_stamp` use `LATEST('gap_cancellation_requests', …)` with no request_status filter while P1 filters `request_status='submitted'`; a later-dated `declined` request (request_status enum includes declined) is taken by P2 as "a signed cancellation request on file" → different interest-days tier and courtesy tier than the request P1 priced. (c) P1 `contract_status` / `plan_status` are first-match CFIELDs on purchase_deal_id; a deal carrying a cancelled and a later active service contract (re-sold after a cancellation) can return the cancelled one → bundle recapture 0 instead of 50. None of (a)–(c) is reached in the two task worlds (one contracted deal in task 1, none in task 0; one request; one VSC).

### action_binding_and_uuids
- Seven task tools, seven policies, each `(target_tool, computes)` claimed once. Tool bodies (task_tools.py) record the values passed and validate nothing: no eligibility, prerequisite or amount check, no refusal path, no hint (confirm/terminate/pay/recover/apply/release bodies read the waiver row only to copy customer_id / totals / names). The tool layer judges no prerequisite.
- Docstrings: no concrete example values, no other tool named, no sequence words about actions (the only "before" is "rounded half up to the cent before it is passed", a format statement). One enumerated arg per field (cancel_method enum). The confirm tool's docstring requires "the signed cancellation request already on file" (relevant to C19).
- uuid8: 0d8763f7, c4427cd3, 0b87221e, 99b30941, cdefd282, 88a68523, bc39910a — pairwise distinct, no shared prefix/suffix, no sequence pattern. No factor id is a substring of any task or share tool name (mechanical check, 0 hits).
- Trigger rule (XF18): confirm and terminate book gap_refund_calculated dated on the closing date as base gap_waiver_cancelled / gap_waiver_terminated triggers require; pay books the paid line and the claim_settled transition with closed_date today; recover books gap_benefit_reversed with status unchanged ("A reversal does not reopen the waiver"); release tools book gap_refund_paid. Nothing lands in another category.

### prerequisite_graph
Edges: P2←P1 (value_input, gate refund_due, state), P2←P3 (state_gate, gap_waivers.status, state), P6←P5 (value_input, refund_due, state), P7←P4 (value_input, setoff, state), P7←P6 (state_gate, gap_ledger.refund_payee, state). P1, P3, P4, P5 declare `[]`. Every `problem` is an extended policy id of this file, none self-referential; the graph is acyclic (two components). Every `policy_source` is verbatim in the blocked policy's own rule (mechanical check). All five are `form: state`, no fallback_reason, consistent. `resolved_by` equals the depended-on policy's target_tool in all five. `gate` names: refund_due (P2, P6) and setoff (P7) are compute bindings of the blocked policy; state gates name real fields. No authoring-viewpoint phrasing in the prerequisite text. Condition-vs-sentence strength: see C12 (P7←P4 broader sentence).

### prerequisite_sentences
Four-point test per edge (connective / state named in record words / no tool, id, snake token, row id / strength):
- P2←P1 "A lienholder refund release is made only after the waiver stands cancelled with a refund calculation entry for that cancellation on its ledger." — passes. Only confirm_gap_cancellation produces status cancelled + gap_refund_calculated (terminate yields terminated). Derivation: sentence → waiver is active with a submitted request → P1's rule ("…booked when the holder confirms a signed cancellation request…") → confirm_gap_cancellation, owner user. Single reading.
- P2←P3 "A lienholder refund release is not made until no other waiver of the same holder financed by the same lienholder stands active with a claim line on its ledger." — **C11**: the waited-on state (the other waiver out of active status) is brought about by three writes of this difficulty: pay_gap_balance (→ claim_settled), confirm_gap_cancellation on the other waiver (→ cancelled; P1 even allows it with no request on file: "Where no signed request is on file, the holder signs on the day of the confirmation"), terminate_paid_off_waiver (→ terminated, where a payoff is on file). The sentence does not single out the GAP balance payment the `condition`/`resolved_by` declare. Also **C13(c)**: where the other waiver's claim line is a final denial (e.g. not_total_loss, appeal window lapsed; the waiver legitimately stays active), only a cancellation of the holder's other waiver can ever unblock the release.
- P6←P5 "A refund release to the holder is not made until the waiver stands terminated with a refund calculation entry for that termination on its ledger." — passes; only terminate_paid_off_waiver yields terminated + refund calculation.
- P7←P4 "A replacement vehicle credit is fixed only after the claim's paid GAP balance line carries a reversal entry wherever a refund of a product financed on the same deal reached the lienholder without being counted on that line." — **C12**: sentence covers any product financed on the deal (Kessler Shield service contract included); `condition`: "…for the add-on overpayment of the Kessler Care plan refund…"; P4 scope: "a service contract refund, a reopened or withdrawn insurer settlement and a recovered stolen vehicle are outside it". World with an uncounted service-contract refund paid to the lienholder: the sentence demands a reversal entry no policy of this difficulty prices (base gap_evt_benefit_reversal covers only a reopened settlement / recovered theft) → credit can never be fixed. **C13(b)**: where P4 prices 0.00 (e.g. plan refund 60.00 counted less admin_error_absorb 50.00 less allowances) the recover tool takes "a positive number"; no reversal entry can exist → credit never fixed although the sentence's "wherever a refund … reached the lienholder without being counted" holds.
- P7←P6 "A replacement vehicle credit is not applied until every other waiver of the holder whose loan was reported paid off on or after the replacement purchase's contract date carries a refund payment to the holder." — four-point test passes; only release_refund_holder books a holder refund payment. **C13(a)**: where that other waiver's termination refund is 0.00 (late in term: P5 floors at 0.00), P6 "A holder release is not made for a refund due of 0.00" and base "A refund of 0.00 is not paid" → the state can never hold → the replacement credit base gap_evt_replacement_credit grants (P7 keeps it: "every other holder whose GAP balance benefit has been paid receives replacement_vehicle_credit_usd …") can never be applied.
- No rule carries a second wording, tool name or other problem's id for its edges; depended-on rules (P1, P3, P4, P5, P6) do not restate the blocked sentences. No base rule sentence grounds an edge. No undeclared cross-problem order found in rules.

### override_declarations
Sentence by sentence against each `base_policy_refs` entry (F = followed/inherited, O = declared overwrite, U = undeclared departure):
- P1 / gap_evt_cancellation_refund: "may cancel … effective on the request date" O(1); "cancelled only from active status" F; **"A waiver is cancelled only on the holder's signed cancellation request recorded for the waiver." U (C19)** — P1: "Where no signed request is on file, the holder signs on the day of the confirmation and that day is the request date." (no request recorded; the confirm tool requires "the signed cancellation request already on file"); "Where refund_on_payoff_automatic is true … is terminated …" **departed from by P1's payoff-date tier (C1)**; free look F (measured on P1's effective date per O(1)); unwound F; "Otherwise … less cancellation_fee_usd;" O(2) — **replaced_by restates nothing for cancellations/terminations outside P1 (C3)**; below-0 F; settled-no-refund F.
- P2 / gap_evt_refund_payment: sentence 1 O (restates the out-of-scope content, excludes P6's case by name); payee sentence F; 0.00 not paid F; once per calculation F; payoff-report sentence F.
- P3 / gap_evt_benefit_calculation: payoff/ACV basis F; deductible O; exclusions O; LTV O; round/floor/cap F; payee/settles F. gap_evt_claim_conditions F (eligibility inherited). gap_agg_vehicle_and_claims F. gap_evt_expiration F. **gap_combo_addon_products "the amount subtracted is the refund each product's own charter computes with the loss date as the effective cancellation date, whether or not the cancellation has yet been processed" U (C20)** — P3: "The claim figures are those recorded on the waiver's most recent claim line … add-on refunds …" and compute `addon_refunds: float(LATEST('gap_ledger','addon_refunds_credited', …))`. Negative-equity sentence F.
- P4 / gap_evt_benefit_reversal: both overwrites declared and restated; "reversed at most once" F; "does not reopen" F.
- P5 / gap_evt_cancellation_refund: auto-termination sentence O(1); "Otherwise …" O(2) — **no restatement for out-of-scope cases (C3)**; **"Unwound deal — where deal_unwind_flat_cancel is true, a waiver on a purchase deal that has been unwound is refunded its full retail_price (cancel_method flat_deal_unwound)." U — dropped branch (C2)**: P5's rule and compute never produce it (`result: MX(0.0, RND(shared_refund - term_charge - financing_retention + trade_credit, 2))` unconditionally); waived-fee sentence F; below-0 F.
- P6 / gap_evt_refund_payment: as P2 (mirror), F/O clean.
- P7 / gap_evt_replacement_credit: sentence 1 O (restated); window sentence F (eligibility); store/no-cash/once-per-claim F; gap_evt_claim_conditions claim_settled F.
- Sibling overwrites of one clause: P1 O(2) and P5 O(2) both retire "Otherwise the refund follows the waiver's refund_method …" — each excludes the other's case by name, **but neither restates the pro-rata content for a termination outside P5** (C3: base gap_evt_expiration "a contract assumed by another borrower ends the waiver as a termination under gap_evt_cancellation_refund" — no loan_payoff_date, outside P5, not a holder cancellation → no refund method left in force). P2/P6 retire the same refund-payment sentence and each restates it — clean.

### factor_ladders
Every ladder has 3 tiers stated in the rule (condition + value/method) and implemented as the branches of its `decides` binding; tiers are pairwise disjoint as stated; `decides` is never `result`; binding sets are disjoint across factors. Per-factor verdicts (R = struck by a RED finding):

| policy | factor (label) | tiers distinct | multi-src | cross | realism / structure verdict |
|---|---|---|---|---|---|
| P1 | eff_date_rule (m) | yes | yes (payoff on waiver + request row) | – | ok (mail-grace rule is real practice) |
| P1 | share_convention (m) | yes | no | – | ok (months / Rule-of-78 / daily are real GAP refund methods) |
| P1 | cancel_charge_tier (p) | yes | no | – | obs O1: part "request states the reason customer_request" holds of nearly every pro-rata canceller (enum has only customer_request / deal_unwound) |
| P1 | admin_portion_tier (p) | yes | no | purchase | ok |
| P1 | early_charge_tier (p) | yes | no | – | obs O2: a second tenure fee on the same 12/24-month bands as cancel_charge (one fee schedule split in two, XF23 padding) |
| P1 | bundle_recapture_tier (p) | yes | yes (vsc + maintenance) | vsc | ok (package-discount recapture is real) |
| P2 | release_rate_source (p) | yes | no | purchase | **R C15** |
| P2 | release_interest_days (m) | **no (window swap)** | yes | – | **R C14** |
| P2 | release_rate_premium (p) | yes | no | – | obs O3 |
| P2 | release_courtesy_credit (p) | yes | no | – | obs O3 |
| P3 | deductible_cover_tier (p) | yes | no | – | obs O4 (tenure gating of deductible cover is not a standard GAP term) |
| P3 | past_due_allowance_tier (p) | yes | no | – | obs O4 |
| P3 | late_charge_allowance_tier (p) | yes | no | – | ok |
| P3 | deferral_treatment (m) | yes | no | – | ok |
| P3 | cap_basis_tier (p) | yes | yes (deal type/cash + waiver basis) | purchase | ok (lesser of price/book value is real) |
| P3 | ltv_reduction_tier (m) | yes | yes (deal trade + waiver AF/basis) | purchase | ok |
| P4 | plan_timing_count (m) | yes (0 / R−50 floored / R) | yes | maintenance | ok (marginal shape: added deduction + floor) |
| P4 | reversal_tenure_tier (p) | yes | no | – | **R C16** |
| P4 | reversal_loss_tier (p) | yes | no | – | **R C16** |
| P4 | reversal_return_tier (p) | yes | no | purchase | **R C16** |
| P4 | reversal_lag_tier (p) | yes | no | maintenance | **R C16** |
| P5 | termination_anchor (m) | yes | yes (waiver payoff + contracted deal) | purchase | ok (trade date ends GAP — real) |
| P5 | termination_share_rule (m) | yes | no | – | **R C17 (XF1)** |
| P5 | termination_charge_tier (p) | yes | no | – | ok |
| P5 | termination_admin_tier (p) | yes | no | purchase | ok |
| P5 | financing_retention_tier (p) | yes | yes | purchase | **R C16** |
| P5 | trade_in_credit_tier (p) | yes | no | purchase | obs O5 (loyalty bonus inside an unearned-charge refund); **C18 (XF2)** |
| P6 | holder_rate_source (p) | yes | no | purchase | **R C15** |
| P6 | holder_interest_clock (m) | **no (window swap)** | yes | – | **R C14** |
| P6 | holder_rate_premium (p) | yes | no | – | obs O3 |
| P6 | payoff_courtesy_tier (p) | yes | no | – | obs O3 |
| P6 | tenure_goodwill_tier (p) | yes | no | – | obs O3 |
| P7 | new_vehicle_bonus_tier (p) | yes | no | purchase | obs O6 (dealer-owned loyalty incentive, plausible) |
| P7 | credit_age_rule (m) | yes | no | – | ok |
| P7 | return_store_bonus_tier (p) | yes | yes (two stores, trade) | purchase | obs O6 |
| P7 | deductible_reimbursement_tier (p) | yes | no | – | obs O7 (compares with base deductible_covered_cap_usd although P3's ladder may already have covered up to 1250/1500 → same deductible covered twice) |
| P7 | replacement_price_tier (p) | yes | no | purchase | obs O6 |

All-pairs method tiers (XF5), with a distinguishing input per pair:
- P1 eff_date_rule: payoff date | recorded date (created_at) | request_date — three different record fields, every pair distinct by input. share_convention: whole months MONTHS(eff,exp)/term | SoD u(u+1)/T(T+1) | DAYS ratio — shapes differ pairwise.
- **P2 release_interest_days: tier1 DAYS(signed,NOW) | tier2 DAYS(recorded,NOW) | fall-through MX(0, DAYS(eff,NOW)−30).** Pair (1,2) distinct by input. Pair (1,fall-through): effective date = closing date = the signed date whenever the request was recorded within mail_grace_days (P1 ladder) → the same day count from the same anchor with and without the constant 30-day window. Pair (2,fall-through): effective date = recorded date whenever the request was recorded more than mail_grace_days late → same anchor, constant window. **FAIL** (window-length swap).
- P3 deferral_treatment: 0 | MX(0,D−300)·switch | D·switch — (0, full) passes (full not 0 over its domain when switch true); (allowance, full) added floor/subtraction. ltv_reduction_tier: G−max(0,AF−cap) | G | G·min(1,cap/AF) (or the waiver's exclude-excess, but tier 1 requires proportional) — pairwise distinct.
- P4 plan_timing_count: 0 | MX(0,R−50) | R — distinct (floor + deduction).
- P5 termination_anchor: sale date | contracted deal contract_date | payoff date — distinct inputs. termination_share_rule: months | SoD | days — distinct shapes, but **its binding term_share reads unused_months / unused_days, which read effective_date, the output of termination_anchor (C17, XF1)**.
- **P6 holder_interest_clock: tier1 DAYS(eff,NOW) | tier2 DAYS(payoff,NOW) | fall-through MX(0, DAYS(eff,NOW)−30).** Pair (1,fall-through): identical anchor in every world, constant window. Pair (2,fall-through): effective date = payoff date in P5's fall-through anchor → identical anchor, constant window. **FAIL**.
- P7 credit_age_rule: C·DAYS(loss,exp)/DAYS(sale,exp) | MN(C, retail) | C — distinct.

T2 (a producible world where the factor alone moves the result, every other factor at baseline): exists for every factor (P3 deferral needs a variant with exclude_deferred_payments true, e.g. Waiver 125/150; P5 termination_charge needs a fee-not-waived variant, e.g. Used Vehicle 140; P2 courtesy tier 2 needs a seeded cancelled waiver with no request on file). T1 is per task (task files, `factor_weight`).

Counts after strikes: P1 6 (2 m / 4 p) pass. **P2 4 → 2, 0 method: FAIL.** P3 6 pass. **P4 5 → 1: FAIL.** P5 6 → 4 (anchor m, charge/admin/trade p) — counts pass, but C17/C18 stand. **P6 5 → 3, 0 method: FAIL.** P7 5 (1 m / 4 p) pass. Per task: task 0 {P1,P2,P3} and task 1 {P4,P5,P6,P7} each keep ≥1 multi-source and ≥1 cross-difficulty factor (task 0: bundle_recapture/vsc, admin/purchase, cap_basis; task 1: termination_anchor/purchase, plan_timing/maintenance).

XF2 shared selections (C18): P5 reads the contracted deal's trade_in_allowance as `repl_trade` (a termination_anchor binding) and again inline in `trade_credit` (trade_in_credit_tier); P4 reads the plan's closed_date as `plan_effective` (plan_timing_count binding) and again inline in `refund_lag` (reversal_lag_tier) — selections used by two factors that are not plain bindings stated once. (P1/P3 inline the same MONTHS() months-in-force in several factors — derived, recorded as obs O8.)

### owed_at_once_and_seed_realism (XF16, XF20, XF25)
- XF16: the reads another product could move mid-conversation are P1 bundle (vsc/maintenance status on the waiver's deal), P3 add-on refunds, P4 maintenance refund paid, P4/P5/P7 contracted deal. P3 and P4 read recorded figures (claim line; a refund already paid), not a live other-product computation, so a VSC/maintenance cancellation made mid-call cannot move them. P1's bundle read moves only if the same deal's service contract or plan is cancelled; per task: task 0's Tucson VSC has no owed cancellation (vehicle kept, no total loss); task 1 has no read that an owed write moves (maintenance refund already paid 2026-08-27; contracted deal awaiting delivery, nothing owed). No XF16 member found in either world.
- XF20 (cross-category seeded rows, both tasks): task 1 Kessler Care Plus 8-Visit — purchase_price 664.05 = 699.00 × (1 − 0.05 bundled discount); refund 414.15 = 664.05 − 2 × 124.95 (retail_value_deduction, fee waived on total_loss) — reproduces the maintenance charter; paid to lienholder 21 days after processing (≤ 30) as financed_on_contract 'true' requires; ledger complete (loaded, 2 redeemed, cancelled, refund calculated, refund paid) with its completed request. Task 0 Kessler Shield Preferred 2895.00 ≤ max_retail_price 3795, 72/100000 term option valid, financed 'true'. Purchase deals carry contract APRs only on dealer-arranged installments, trade figures consistent with the claim lines' negative equity (task 0 8280.00 = 14480 − 6200; task 1 4350.00 = 10850 − 6500). Purchase ledgers (purchase_transactions) are not seeded — unread residue per XF20.
- XF25: both worlds' prerequisite situations (an unprocessed mailed cancellation; a theft claim denied inside the waiting period and payable after it; an add-on refund that reached the lender uncounted; a payoff on a traded vehicle not yet terminated) are states real GAP administration produces; none needs a real-world wait.

### findings
Charter-global findings (consequence per task is demonstrated or disclaimed in `0.md` / `1.md`):

| id | verdict | class / where | tasks it bears on |
|---|---|---|---|
| C1 | SOURCE-POLICY RED | P1 payoff-date tier vs P5 + base auto-termination: same world claimed by a cancellation and a termination (policy_conflict_scan) | neither world (task 0 W1 has no payoff; task 1 W_B has no request) — charter |
| C2 | SOURCE-POLICY RED | P5 drops base unwound-deal flat refund (override_declarations) | charter (task 1 deal closed) |
| C3 | SOURCE-POLICY RED | P1 O(2) + P5 O(2) retire the pro-rata sentence with no out-of-scope restatement; assumption termination has no refund method (XF13) | charter |
| C4 | SOURCE-POLICY RED | P2/P6 baseline late-interest gate vs interest-days tiers and compute (rule_compute_equivalence) | charter (both task releases are past the window) |
| C5 | SOURCE-POLICY RED | rounding mode: rule silent, docstrings half-up, RND half-even on exact ties | **task 0 (demonstrated tie)** |
| C6 | SOURCE-POLICY RED | P2/P6 compute sends 0.00 APR to standard_late_rate, rule to the floor | charter |
| C7 | SOURCE-POLICY RED | absent-record probes: P3, P4, P7 compute errors where the rule promises 0.00 | charter |
| C8 | SOURCE-POLICY RED | P4 "most recent claim line" vs "paid line" + unfiltered LATEST | charter (task 1 latest row is the paid line) |
| C9 | SOURCE-POLICY RED | decoy / second-record first-match reads (P4/P5/P7 contracted deal; P2 request without status filter; P1 VSC/plan status) | charter |
| C10 | SOURCE-POLICY RED | "whole calendar months" with no month-end rule vs MONTHS() | charter |
| C11 | SOURCE-POLICY RED | P2←P3 state gate brought about by three writes | task 0 (see 0.md: the second write is not executable in its world) |
| C12 | SOURCE-POLICY RED | P7←P4 sentence broader than its condition (any financed product vs Kessler Care) | charter (task 1 has no service contract) |
| C13 | SOURCE-POLICY RED | gates no write can satisfy: (a) P7←P6 with a 0.00 termination refund, (b) P7←P4 with a 0.00 reversal, (c) P2←P3 with a finally denied other claim | charter |
| C14 | SOURCE-FACTOR RED | P2 release_interest_days, P6 holder_interest_clock are window-length swaps (XF5) → P2 and P6 keep 0 method factors | **task 0 (P2), task 1 (P6)** |
| C15 | SOURCE-FACTOR RED | P2/P6 rate ladders: "no contract APR" tier/baseline reachable by no GAP holder (every waiver sits on a dealer-arranged installment that names its APR); "carries a contract APR" holds of every customer | **task 0, task 1** |
| C16 | SOURCE-FACTOR RED | realism (XF22/XF24): P4 tenure / loss / return-purchase / refund-lag allowances discount the recovery of an amount paid in error on facts that do not bear on that amount (P4 left with 1 factor); P5 financing_retention keeps part of an unearned-charge refund on LTV at sale | **task 1** |
| C17 | SOURCE-FACTOR RED | XF1: P5 termination_share_rule reads termination_anchor's output (effective_date) | **task 1** |
| C18 | SOURCE-FACTOR RED | XF2: shared selections duplicated across factors (P5 contracted trade-in; P4 plan closed_date) | **task 1** |
| C19 | SOURCE-POLICY RED | P1 "no signed request on file → holder signs at confirmation" departs from base signed_request eligibility without overwrite (tool also needs a request id) | charter (task 0 has a request on file) |
| C20 | SOURCE-POLICY RED | P3 takes add-on refunds from the recorded claim line instead of base gap_combo_addon_products' charter-computed refund at the loss date, undeclared | charter; task 1's W_A history is a live instance (see 1.md) |

C14 evidence: P2 rule "where a signed cancellation request is on file and was recorded on the day the holder signed it, interest runs for every calendar day from the signed date to the release date; … in every other case it runs only for the calendar days past refund_payment_days after the effective date"; compute `interest_days: (DAYS(recorded_stamp, NOW) if DAYS(signed_date, recorded_stamp) > 0 else DAYS(signed_date, NOW)) if recorded_stamp else MX(0, DAYS(effective_date, NOW) - P('refund_payment_days'))`. P6 compute `holder_days: DAYS(effective_date, NOW) if effective_date < payoff_date else (DAYS(payoff_date, NOW) if DAYS(payoff_date, NOW) > P('refund_payment_days') else MX(0, DAYS(effective_date, NOW) - P('refund_payment_days')))`. XF5: "never swap a multiplier or window length … two tiers that are the same combination of the same sums FAIL".

C15 evidence: gap.yaml gap_evt_sale "A waiver is sold only on a purchase deal financed by a dealer-arranged installment contract"; purchase.yaml "A financed deal names its lienholder, amount financed, lender buy rate and contract APR on the contract; a cash deal leaves them empty or 0.00."; db_schema contract_apr "empty when not financed". P2 ladder "where no contract APR is on the deal, the interest runs at standard_late_rate" = baseline `interest_rate: K('standard_late_rate')`; P6 likewise with holder_late_rate.

C16 evidence: P4 rule "The overpayment is the uncredited plan refund, never more than the amount paid on the line" — the amount paid in error is fixed by the plan refund and the paid line; the four ladders subtract tenure_allow (months sale→loss), collision_deductible_allow / slow_theft_allow (loss facts), return_new_allow / return_used_allow (a pending group purchase), lag_allow (days the plan refund took) — none changes how much of the benefit was paid in error, and an administrator recovering an overpaid GAP benefit does not publish discounts keyed on them. P5 "where the amount_financed … is more than 125 percent of the waiver's vehicle_value_basis, ltv_retention_high is kept from the termination refund" — the refund is of the unearned part of a fixed retail_price (base: retail_price × unused share less a fee); the LTV at sale is not a cost the unearned part carries, and no GAP refund schedule retains on it.

C19 evidence: base signed_request eligibility "A waiver is cancelled only on the holder's signed cancellation request recorded for the waiver." vs P1 "Where no signed request is on file, the holder signs on the day of the confirmation and that day is the request date." World: active waiver, no request on file, holder asks to cancel → base: no cancellation until a request is recorded (no tool records one); P1: confirm today, refund priced on today.

C20 evidence: base gap_combo_addon_products "the amount subtracted is the refund each product's own charter computes with the loss date as the effective cancellation date, whether or not the cancellation has yet been processed" vs P3 "The claim figures are those recorded on the waiver's most recent claim line … add-on refunds …". World (task 1's W_A as of its 2026-08-18 denial): claim line addon_refunds_credited 0.00, Kessler Care plan financed on the deal, charter refund at the loss date 414.15 → P3 3380.36, base 2966.21.

Observations: O1–O8 as tagged above; O9: base gap_claim_denied writes no payoff/ACV/deductible figures, yet P3/P4/P7 read claim figures from denied lines and the seeds populate them; O10: no rule states a same-day tie rule for "most recent" lines (LATEST keeps the first row); O11: P5 trade-in tier does not tie the trade-in to the waiver's vehicle; O12: P2←P3 and P7←P6 cross-waiver holds are not a GAP-administration practice (a refund or credit on one waiver held for another waiver's claim or refund).

## closing_checklist
Written after both reveals (2026-10-22T03:21Z); the charter-global sections above were frozen before any reveal and are unchanged.
- Audit files: `_difficulty.md`, `0.md`, `1.md` — one per task, each with a frozen derivation, a GT comparison and findings. revision_1 (no earlier revision exists).
- Coverage and scope: charter_scope task 0 = {P1, P3, P2} with {confirm, pay, release_lienholder}; task 1 = {P4, P5, P6, P7} with {recover, terminate, release_holder, apply} — all seven extended policies covered, pairwise disjoint, equal to the pre-reveal partition. uuid8s independent (action_binding_and_uuids).
- Trees: task 0 n = 2 (1 value_input, user write P1); task 1 n = 3 (2 value_input, user write P7); difficulty-wide graph acyclic. **But** task 0's customer names its prerequisite (0.md T0-F1).
- Factors: **not closed** — P2 and P6 keep no honest method factor (C14, C15), P4 keeps 1 factor (C16), P5 carries C16/C17/C18; proof traces in both tasks assert false month counts (T0-F4, T1-F4). Every surviving factor bears weight on its task's world (T1 all moved), all-baseline fall-backs definite and ≠ gold.
- Unique solution: task 0 has a second defensible value pair 543.13 / 575.41 (C5, T0-F2); task 1 unique.
- Gates: coordinator snapshot (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK) cited, not re-run by the auditor; the source-layer audit does **not** pass.
- Proof-text sweep (XF26, post-reveal): stale/false assertions recorded in 0.md (14 months; "exactly one write" out of active; pro-rata overwrite "restating the base") and 1.md (tenure 40; clock pair "distinguishing input" = the window).

Per-task verdicts: task 0 RED (SOURCE-CHAIN T0-F1, SOURCE-TASK T0-F2, SOURCE-FACTOR T0-F3/T0-F4); task 1 RED (SOURCE-FACTOR T1-F1…T1-F4). Charter RED: C1–C20.

VERDICT revision_1: task0=RED task1=RED charter=C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20

## revision_2

## charter_global_frozen (revision_2)
- Frozen 2026-10-22T05:47Z, before any round-2 GT was read; same independent auditor as revision_1. Entry gate: last line of `tasks/gap_waiver_claims/worklog.md` = `REWORK round 2: gates 7/7 green` (only that line read; the rest of the worklog is read after the freeze). `/tmp/erl0075_coord/snapshot.sh gap_waiver_claims 2` run by the auditor: views `r2/0.view.json` sha256 bdf6adf1688751cc, `r2/1.view.json` sha256 80851bef77208155 (masked: charter_scope, computations, db_closure, db_closure_matches_initial_state, design_rationale, evaluation_criteria, prerequisite_closure, required_documents, solvability_contract); gate snapshot 2026-10-22T05:39:08 — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 gap.extended.yaml c31e91b5ca0b, task_tools.py 5d32969c4cda, tasks/0.json afd6673a8233, tasks/1.json 544d52967dd9.
- Both shared inputs changed (685f7ab918ac → c31e91b5ca0b; 2d25ba499d41 → 5d32969c4cda), so every charter-global section is re-derived in full below.
- contamination_disclosure: the auditor read the round-1 GT of both tasks during revision_1 (recorded there). Round-2 derivations rest on the r2 views and the current charter only; round-2 task JSON, the reworker's reply and the worklog body were not read before this freeze. Round-1 GT shapes (tool order, argument names) are known to the auditor; no round-2 value was seen.
- Mechanical sweep (current files): base copy equal to blueprint (all keys); every compute_basis quote verbatim in its rule; every compute binding has a basis; every baseline.rule sentence in its rule; every overwrite clause verbatim in the cited base rule and every replaced_by verbatim in the extended rule; every prerequisite policy_source verbatim in its rule; no factor id is a substring of a tool name; uuid8s unchanged and distinct.

### closure of revision_1 findings (verified against the artifacts)
| id | status | evidence |
|---|---|---|
| C1 | closed | P1 overwrite 3 and P5 overwrite 1 retire the same base auto-termination clause; P1: "For an active waiver that carries a submitted signed cancellation request, and only for such a waiver, the holder's cancellation ends the waiver even where its lienholder has reported the contract paid off …; every other waiver … is terminated …"; P5: "a waiver that carries a submitted signed cancellation request is not terminated by this sentence and ends by the holder's cancellation"; P5 compute `in_scope` excludes a submitted request. One owner per world. (New consequence: C21.) |
| C2 | closed | P5 rule "Where deal_unwind_flat_cancel is true, a waiver whose purchase deal has been unwound is refunded its full retail_price on termination, with cancel_method flat_deal_unwound"; compute `deal_unwound` → `RND(0.000001 + F('retail_price'), 2)`; terminate tool now takes cancel_method pro_rata / flat_deal_unwound. |
| C3 | closed | both replaced_by sentences now end "… any other ending of a waiver that neither this rule nor the termination [cancellation] rule prices keeps the retail_price times gap_msr_unused_term_share, rounded half up to the cent, less cancellation_fee_usd." |
| C4 | closed | P2/P6 rules: interest only "for each calendar day past refund_payment_days after the window start"; compute `late_days: MX(0, DAYS(window_start, NOW) - P('refund_payment_days'))`; no tier accrues inside the window. |
| C5 | closed | every rule now says "rounded half up to the cent"; compute `RND(0.000001 + x, 2)`; every money arg docstring "rounded half up to the cent (a half cent goes up)" and bodies apply `_GapRecords.cents` (integer half-up). Residual observation O13 below (sign of a half-up on P1's negative adjustment). |
| C6 | closed | P2 `deal_apr: float(CFIELD(...) or 0) / 100.0`; ladder tier 3 "contract APR of standard_late_rate or less, 0.00 included, or no contract APR"; P6 likewise. |
| C7 | closed | P3 `float(LATEST(...) or 0)`, `loss_date … or F('sale_date')`; P4 `line_* … or NOW`, guarded result; P7 `line_paid_date … or NOW`, `line_loss_date … or F('sale_date')`. No absent-record path raises (probed by reading every binding). |
| C8 | closed | P4 every line figure now `LATEST(…, event_type='gap_benefit_paid', benefit_line_type='gap_balance')`; rule speaks only of "the paid line … the add-on refunds recorded on it". |
| C9 | closed | (a) P4 no longer reads a contracted deal; P5/P7 define "the holder's most recently signed group purchase deal, the deal whose vehicle price was charged last (of two charged the same day, the one recorded first), where that deal stands in contracted status" = `XLATEST('purchase','purchase_transactions','purchase_deal_id', date_field='txn_date', event_type='purchase_charge_posted', charge_code='vehicle_price')` (tie keeps the first row, matching "recorded first"); (b) P2 reads the `completed` request ("The signed request a lienholder release reads is the waiver's completed cancellation request"); (c) P1/P5 bundle tests are `EXISTS(…, status='active')`. |
| C10 | closed | P1, P3, P5, P6, P7 now state "a whole calendar month counts each time the start date's day of the month is reached; an end date on an earlier day of the month does not complete the month, and there is no month-end adjustment" = `MONTHS()`; P2/P4 no longer count months. |
| C11 | closed | P2 gate now "… also carries a paid GAP balance line": only pay_gap_balance books a gap_benefit_paid gap_balance line (apply books replacement_vehicle_credit). |
| C12 | closed | P7 sentence now names "a Kessler Shield service contract or Kessler Care maintenance plan … cancelled on or after the loss date … exceed the add-on refunds recorded on that line" = its condition; P4 now prices both products. |
| C13 | **partly open** | (a) closed — P7 gate 2 now "has left active status with no refund due on it"; a 0.00 termination satisfies it. (b) **open, narrowed** — see R2-C13b. (c) **open, narrowed** — see R2-C13c. |
| C14 | closed for the window-swap form | P2 `release_late_window` and P6 `holder_late_window` now select the window's start date from different records (unwind closed_date / signed date / effective date; payoff date / unwind closed_date / effective date) — XF5 "data-selected window". P6 has a new overlap defect (R2-F2). |
| C15 | closed | fall-through tier now holds for APR ≤ 5 % (incl. 0.00) — reachable; values 9 % cap, APR, 5 %. |
| C16 | closed | P4's tenure/loss/return/lag allowances removed (new factors judged below); P5 financing_retention removed (replaced by termination_bundle_tier). |
| C17 | closed | P5 share now "from the loan_payoff_date" (`unused_months: MONTHS(payoff_date, …)`); the backdating credit is a separate binding; the share factor reads no factor output. |
| C18 | closed | P5 `repl_trade`/`repl_contracted`/`repl_id` are plain bindings read by backdating and trade credit; P4 `plan_closed` is a plain binding read by plan timing and plan adjustment. |
| C19 | closed | P1 "A waiver with no submitted signed cancellation request on file is not cancelled under this policy, and its cancellation refund is 0.00"; compute `result … if request_on_file else 0.0`; confirm tool refuses a request that is not submitted for this waiver. |
| C20 | closed | P3 overwrite 4 of gap_combo_addon_products, self-scoped, restating the base for every other GAP benefit. |

### policy_conflict_scan / rule_compute_equivalence (revision_2, re-derived)
- Scope owners per world: holder cancellation (P1: submitted request, active) vs payoff termination (P5: payoff on file, no submitted request) now partition the active waivers; P2 (loan open, cancellation refund) vs P6 (payoff on file, termination refund) unchanged. **Gap C21**: a cancellation refund on a waiver whose payoff is on file (now produced by P1's payoff-date tier and its precedence clause) is owed to the holder by base gap_evt_refund_payment ("once the lienholder has reported the loan paid off, the refund is paid to the holder"), is outside P2 ("loan_payoff_date empty") and outside P6 ("releases to the lienholder and cancellation refunds are outside it"), and no tool is documented for it: release_refund_holder "Release the refund owed on a terminated Kessler GAP waiver", release_refund_lienholder "on a cancelled … to the lienholder".
- Rule ↔ compute two-way sweep of all seven policies: no unmatched promise found except **R2-F1** (P1 `factors[].ladder` face vs rule). P1's assembly ("the effective-date adjustment, itself rounded half up to the cent, and every charge are applied after that rounding") = `MX(0.0, RND(0.000001 + shared_refund + eff_adjustment - cancel_charge - early_charge - bundle_recapture, 2))`; P4 "the waivers … never take it below one half of the overpayment" = `MX(overpayment / 2.0, overpayment - review_waiver - stale_waiver)`; P5 order = compute; P2/P6 interest = compute.
- Probe table (decoy / absent / zero / tie / month-end) on every changed read: P1 request reads filter submitted, EXISTS for bundle; P2 completed request (one per cancellation), APR None/0 → 5 %; P3 no claim → 0.00; P4 no paid line → 0.00, no plan/contract → 0 counts, `MX(1, DAYS(...))` guards a contract closed on its expiration date, plan_reason from the refund-paid row; P5/P7 replacement deal = latest vehicle_price charge (tie keeps the first-recorded row, as the rule states), non-contracted latest → no replacement purchase; P6 APR as P2. Month counts: convention stated where MONTHS() is used. No probe failure outside the findings below.

### action_binding_and_uuids (revision_2)
- Same seven tools, uuid8s unchanged. Bodies now enforce their docstrings: request/entry kind checks, non-negative or positive amounts, enum sets, half-up cents (`_GapRecords.cents`), terminate's payoff / no-submitted-request test (stated in its own docstring). **R2-T1**: `_GapRecords.is_date` accepts any day 1–31 in any month, so "2026-02-30" passes while confirm_gap_cancellation and terminate_paid_off_waiver document "the date must be a real calendar date in the stated form … otherwise an Error line is returned and nothing is written" (members: confirm.effective_date, terminate.effective_date).
- No tool refuses on an unresolved prerequisite state: the release tools' check "source_entry_id must name a refund calculation entry of this waiver" is a reference-kind check that adds nothing beyond the argument's own docstring ("reference number of the refund calculation entry being paid") — O14. No docstring names another tool or a sequence.

### prerequisite_graph / prerequisite_sentences (revision_2)
Edges unchanged in shape: P2←P1 (value_input, state), P2←P3 (state_gate, gap_ledger.event_type), P6←P5 (value_input), P7←P4 (value_input, setoff), P7←P6 (state_gate, gap_waivers.refund_due_balance). Acyclic; policy_source verbatim; resolved_by = target tools; form state everywhere.
- P2←P3 "…not made until every other waiver of the same holder financed by the same lienholder that carries a GAP balance line denied for the theft waiting period, with that waiting period run, also carries a paid GAP balance line." — one resolving write (pay_gap_balance). **R2-C13c**: where the stolen vehicle was recovered before theft_waiting_days ran, base makes the claim unpayable ("A theft claim is paid only after the vehicle has stayed unrecovered for theft_waiting_days calendar days"), the denial stands, the period has run → no write can ever book the paid line → the holder's other refund can never be released.
- P7←P4 — **R2-C13b**: the sentence fires when refunds "as paid to the lienholder" exceed the recorded add-on refunds; P4 counts a plan refund cancelled between loss and payment "less admin_error_absorb, but never less than half". World: plan refund 60.00 paid to the lienholder, cancelled after the loss and before the payment, line records 40.00 → sentence demands a reversal (60.00 > 40.00); P4: counted MX(30.00, 10.00) = 30.00, uncredited MX(0, 30.00 − 40.00) = 0.00, reversal 0.00; recover tool: "amount must be above 0.00" → no reversal entry can exist → the credit is never fixed.
- P7←P6 "…has left active status with no refund due on it" — resolved by the holder release when the termination refund is positive, by the termination alone when it is 0.00 (C13(a) closed); C21 adds a world (cancelled waiver with payoff on file) whose refund has no documented paying tool.
- P6←P5, P2←P1: unchanged, pass.

### factor_ladders (revision_2, changed factors; unchanged ones as revision_1 table)
| policy | factor (label) | verdict |
|---|---|---|
| P1 | eff_date_rule (m) | shapes: +retail·DAYS(payoff,signed)/T, −retail·DAYS(signed,recorded)/T, 0 — distinct inputs/sign; ok. |
| P1 | share_convention (m) | **R2-F1**: ladder face says "from the effective date"; rule/compute "from the signed request date". |
| P2 | release_rate_source (p) | 9 % cap / APR / 5 % — reachable, real; ok. |
| P2 | release_late_window (m) | start = unwind closed_date / signed date / effective date — data-selected, disjoint by reason; ok (O16 realism note). |
| P4 | plan_timing_count (m) | 0 / MX(R/2, R−50) / R — ok. |
| P4 | contract_restatement (m) | 0 / R·DAYS(loss,exp)/DAYS(closed,exp) / R — ok, real (refund restated to the loss date as base gap_combo prescribes). |
| P4 | plan_adjustment_tier (p) | **R2-F3**: tier "cancelled on or after the loss date for deal_unwound" holds of no customer who reaches this write (a deal is unwound only from conditionally_delivered or by an exchange return of a delivered vehicle — purchase lifecycle — impossible for a vehicle already paid as a GAP total loss) → 2 live tiers; and that tier's value "retail_value_per_visit_usd times the visits redeemed" is a computation over a record count under a `parameter` label (XF5 "Parameter factors select values, not methods"). Tier 1 (+fee for customer_request / vehicle_sold_or_traded) is real (restates the plan refund to its total-loss value, fee waived). |
| P4 | review_waiver_tier (p) | ok (administrator absorbing part of a recovery caused by its own denial-then-review handling; O17). |
| P4 | stale_payoff_tier (p) | ok (same rationale; O18 decoy note). |
| P5 | termination_share_rule (m) | ok (reads payoff date, no factor output). |
| P5 | termination_backdating (m) | credit = retail·DAYS(sale,payoff)/T / retail·DAYS(contract,payoff)/T / 0 — distinct inputs; real (trade date ends the coverage). |
| P5 | termination_bundle_tier (p) | ok (mirrors P1's bundle recapture). |
| P6 | holder_rate_source (p) | ok. |
| P6 | holder_late_window (m) | **R2-F2**: tiers 1 and 2 overlap as stated — "where the effective date of the termination is earlier than the loan_payoff_date, the late window starts on the loan_payoff_date …; where the waiver's purchase deal stands unwound, the late window starts on that deal's closed_date" — an unwound deal terminated in the free look (P5 effective = sale date < payoff) satisfies both; window from payoff date vs from the unwind date. Counting only factors that pass, P6 keeps 0 method factors. |
Counts after strikes: P1 6 (ladder-face RED stands); P2 4 (1 m) pass; P3 6 pass; P4 5 → 4 (2 m / 2 p) — counts pass, R2-F3 stands; P5 6 pass; **P6 5 → 4, 0 method: fail**; P7 5 pass. XF1/XF2 sweep on changed policies: no factor reads another factor's binding; shared selections are plain bindings (P1 signed_date, P2 recorded_stamp/effective_date, P4 plan_closed/plan_id/contract_id, P5 repl_id/repl_trade/repl_contracted, P6 effective/payoff dates, P7 repl_id/repl_type).

### findings (revision_2)
| id | verdict | tasks it bears on |
|---|---|---|
| R2-F1 | SOURCE-POLICY RED — P1 share_convention ladder face ≠ rule (effective vs signed date) | task 0 (see 0.md) |
| R2-F2 | SOURCE-FACTOR RED — P6 holder_late_window tiers overlap as stated | task 1 (P6 has no surviving method factor) |
| R2-F3 | SOURCE-FACTOR RED — P4 plan_adjustment_tier dead deal_unwound tier + parameter label on a computed tier | task 1 |
| R2-C13b | SOURCE-POLICY RED — P7←P4 gate unsatisfiable when plan counting falls below the recorded credit | charter |
| R2-C13c | SOURCE-POLICY RED — P2←P3 gate unsatisfiable when the stolen vehicle was recovered | charter |
| C21 | SOURCE-POLICY RED — cancellation refund with payoff on file owed to the holder, no policy/tool documented for it | charter |
| R2-T1 | SOURCE-POLICY RED (tool contract, XF17) — date validation weaker than documented (2 members) | charter |
Observations (revision_2): O13 P1 tier-2 adjustment is a negative amount and `RND(0.000001 + x)` rounds an exact negative half toward zero while "the refund gives up … rounded half up" rounds the given-up amount up (exact ties need e.g. a 1096-day term and a 137-day recording lag); O14; O15 module docstring "a tool refuses only a malformed value or a reference to a record of the wrong kind" vs terminate's state test; O16 P1 places a late-recorded request's effective date on the recorded date (holder bears the mail delay) while P2 starts late interest from the signed date (company bears it); O17; O18 the stale-payoff tier fires on any add-on refund that reached the lienholder before payment, including one of a product cancelled before the loss that P4 does not count; O19 task-1 seed: the plan cancelled "after the crash" carries reason customer_request (fee 75.00 charged) beside a VSC cancelled the same day for total_loss — producible. Carried: O1, O2, O3, O4, O5, O6, O7, O8, O10, O11, O12.

## closing_checklist (revision_2)
Written after both round-2 reveals; the revision_2 charter sections above were frozen before them and are unchanged.
- Files: `_difficulty.md`, `0.md`, `1.md` each carry revision_1 untouched and an appended revision_2 (frozen derivation, comparison, findings).
- Blind = GT on every write, owner, order, argument and on every expected / baseline_result / factor_sensitivity figure in both tasks (21 + 16 figures).
- Coverage/scope: charter_scope task 0 {P1, P3, P2}, task 1 {P4, P5, P6, P7} — all seven covered, disjoint; uuid8s unchanged and independent.
- Trees: task 0 n = 2 (1 value_input, user write), task 1 n = 3 (2 value_input, user write); acyclic; persona of task 0 no longer names the prerequisite.
- Factors: not closed — P6 has no disjoint method factor (R2-F2), P4 plan_adjustment_tier has two live tiers and a computed tier labelled parameter (R2-F3); P1 share ladder face ≠ rule (R2-F1).
- Charter gates/edges: R2-C13b, R2-C13c (unsatisfiable waits), C21 (cancellation refund with payoff on file has no documented release), R2-T1 (date validation weaker than documented).
- Revision_1 ids C1–C12, C14–C20 closed (table above); C13 partly open (b, c); task items T0-F1…F4, T1-F1…F4 closed.
- Gates: coordinator snapshot r2 cited (7/7 OK); not re-run by the auditor.

Per-task verdicts: task 0 RED (SOURCE-POLICY R2-F1 demonstrated: 549.84 vs 538.39); task 1 RED (SOURCE-FACTOR R2-F2, R2-F3).

VERDICT revision_2: task0=RED task1=RED charter=R2-F1,R2-F2,R2-F3,R2-C13b,R2-C13c,C21,R2-T1

## revision_3

## charter_global_frozen (revision_3)
- Frozen 2026-10-22T06:07Z, before any round-3 GT was read; same independent auditor. Entry gate: last non-blank line of `tasks/gap_waiver_claims/worklog.md` = `REWORK round 3: gates 7/7 green` (only that line read before this freeze). `/tmp/erl0075_coord/snapshot.sh gap_waiver_claims 3` run by the auditor: views `r3/0.view.json` sha256 bdf6adf1688751cc (identical to r2), `r3/1.view.json` sha256 35db1b12805a8f97; gate snapshot 2026-10-22T06:04:26 — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 gap.extended.yaml 4d1bd4ca0ff7, task_tools.py 06364358bae7, tasks/0.json 2f8fc61ebe2c, tasks/1.json 43924bbea5be.
- Both shared inputs changed again → charter sections re-derived (policy-by-policy diff against the revision_2 copy kept in the auditor's scratch, then a full re-read of every changed policy). All seven policies changed: P1 (ladder face, rounding form), P2 (payee sentence, gate), P3 (rounding form), P4 (rebuilt: claim-standing cap, recovery floor, fee add-back, prompt-payment interest), P5 (rounding form), P6 (scope widened to holder releases of cancellation refunds, window ladder reordered), P7 (gate thresholds, rounding form). Task-1 world: settlement_date 2026-08-12 → 2026-07-31 on the three claim lines; persona line updated to match. Task-0 view unchanged.
- contamination_disclosure: revision_1 and revision_2 GT of both tasks were read in earlier rounds; the round-3 derivation rests on the r3 views and the current charter; round-3 task JSON and the worklog body were not read before this freeze.
- Mechanical sweep: base copy equal to blueprint; every compute_basis quote verbatim in its rule; every binding has a basis; baseline sentences in rules; overwrite clauses/replaced_by verbatim; prerequisite sources verbatim; no factor id inside a tool name; uuid8s unchanged. Ladder-face sweep: every date anchor in a ladder method is the rule's anchor (abbreviated wording only).

### closure of revision_2 findings
| id | status | evidence |
|---|---|---|
| R2-F1 | closed | P1 share_convention ladder now "whole calendar months from the signed request date …" / "calendar days from the signed request date …" = rule and compute. |
| R2-F2 | closed | P6 rule and ladder: "where the waiver's purchase deal stands unwound … closed_date; where the deal is not unwound and the effective date … is earlier than the loan_payoff_date … loan_payoff_date; in every other case …"; compute tests unwound first. Tiers pairwise disjoint. |
| R2-F3 | closed | plan_adjustment_tier removed; fee_addback_tier (parameter: both fees / that product's fee / 0.00) — no dead tier (customer_request and vehicle_sold_or_traded are reasons a holder states on any cancellation), no computed tier. |
| R2-C13b | closed | P7 sentence and P4 now share the threshold: P7 "wherever that line paid more than 60.00 and the refunds … exceed the add-on refunds recorded on that line by more than 60.00"; P4 "Where the paid line paid no more than recovery_floor_usd, or the refunds … exceed … by no more than recovery_floor_usd, nothing is reversed" (`floor_excess`). Proof that P4 is positive whenever P7 demands a reversal: plan counted ≥ received − 50 (MX(R/2, R − 50)), contract counted ≥ received (restating to the earlier loss date multiplies by DAYS(loss,exp)/DAYS(closed,exp) ≥ 1), fee add-back ≥ 0 → uncredited ≥ excess − 50 > 10; overpayment ≤ claim standing ≥ paid line > 60; result ≥ half the overpayment > 5 → the recover tool accepts it. |
| R2-C13c | closed | P2 gate now a record test on the other waiver's most recent GAP balance line ("…has, as its most recent GAP balance line, a denial for the theft waiting period whose waiting period has run"); a later paid or denied GAP balance line ends it, so a recovered vehicle leaves an ordinary wait for the administrator's next decision rather than an unsatisfiable state. Only pay_gap_balance among this difficulty's writes books a GAP balance line (apply books replacement_vehicle_credit; recover books not_applicable). |
| C21 | closed | P2 and P6 now carry the payee sentence "A refund computed on a waiver whose loan_payoff_date is empty is released to the lienholder; a refund computed on a waiver whose loan_payoff_date is on file, whether a termination refund or a cancellation refund, is released to the holder"; P6 "prices every release of a refund to the holder, a termination refund or a cancellation refund"; P6 overwrite restated for "a refund released to the holder"; tools: release_refund_holder "on a terminated or cancelled … waiver whose lienholder has reported the loan paid off", release_refund_lienholder "whose loan is still open", each body refusing the other side. |
| R2-T1 | closed | `_GapRecords.is_date` now checks month 1–12 and the month's length with the leap-year rule. |
- No regression found in the revision_1 closures (C1–C20 re-checked on the changed text: partition sentences, unwound branch, restatements, interest windows, half-up rounding, APR ladders, absent-record guards, paid-line reads, latest-charge replacement deal, month-count sentences, record-test gates, declared add-on overwrite).

### rounding at exact ties (revision_3)
Every RND now has the form `RND(x + 0.000001, 2)` applied to a non-negative x (P1's adjustment is now RND(MX(0, a)) − RND(MX(0, b)), the given-up magnitude rounded half up, then signed — O13 closed). An exact half (e.g. 825 × 57/72 = 653.125) becomes 653.125001 → 653.13 = the rules' "rounded half up"; tool bodies round passed amounts with integer half-up (`int(abs(v)*100 + 0.5 + 1e-7)`). Margin: for retail × day ratios the distance from a half-cent is ≥ 1/(2·term_days) cent > 1e-6 dollars, so the epsilon never rounds a non-tie up; for interest products (rate with 4 decimals × days/365) a true value within 1e-6 dollars below a half-cent is arithmetically possible — observation O20, no consequence in either world (P2 5.0031…, P4 1.4217…, P6 0.3452…).

### policy_conflict_scan / prerequisite_graph (revision_3)
- Payee partition (P2 loan open / P6 payoff on file) and ending partition (P1 submitted request / P5 payoff without request) are complete and disjoint; sibling overwrites of the refund-payment sentence each exclude the other's case by name.
- Edges unchanged in shape and kind; P6←P5 sentence now "A termination refund is not released to the holder until the waiver stands terminated with a refund calculation entry for that termination on its ledger" (scope-correct now that P6 also releases cancellation refunds). Each state-form edge has one resolving write in this difficulty. Acyclic.
- Tool layer: bodies enforce every docstring promise (dates real, enums, non-negative/positive amounts, reference kinds, payee and ending partitions); no tool refuses on an unresolved prerequisite state beyond the argument's own reference kind (O14).

### factor_ladders (revision_3, changed)
| policy | factor | verdict |
|---|---|---|
| P4 | plan_timing_count (m) | as revision_2, ok |
| P4 | contract_restatement (m) | ok |
| P4 | fee_addback_tier (p) | both fees / one product's fee / 0.00 — distinct values, multi-source (plan + contract), real (restates a fee-bearing refund to its total-loss value) |
| P4 | prompt_pay_rate_tier (p) | late_pay_rate_high / late_pay_rate / 0.00 — real (prompt-payment interest the administrator owes on a late benefit, set against the recovery) |
| P4 | stale_payoff_tier (p) | now reads only add-ons cancelled on or after the loss (O18 closed) |
| P6 | holder_late_window (m) | disjoint, data-selected start dates — ok |
Counts: P1 6 (2 m), P2 4 (1 m), P3 6 (2 m), P4 5 (2 m / 3 p), P5 6 (2 m), P6 5 (1 m), P7 5 (1 m). XF1: no factor reads another factor's binding (P4 `late_pay_credit`, `uncredited`, `overpayment`, `floor_excess`, `claim_standing` are plain).
**R3-F1 (XF2) SOURCE-FACTOR RED**: the service contract's cancellation date — `CFIELD('vsc', 'closed_date', purchase_deal_id=F('purchase_deal_id'), financed_on_contract='true')` — is a record selection read inline by three factors' bindings (contract_restatement → `contract_counted`, fee_addback_tier → `fee_addback`, stale_payoff_tier → `first_refund_paid`) and by the plain `floor_excess`, not stated once as a plain binding (the plan's counterpart `plan_closed` is). Members: contract_counted, fee_addback, first_refund_paid (+ floor_excess). Same class as revision_1 C18. No numeric consequence (all reads return the same row: one financed contract per deal in both worlds).

### findings (revision_3)
| id | verdict | tasks |
|---|---|---|
| R3-F1 | SOURCE-FACTOR RED (XF2 recipe point; coordinator: any member is RED) | task 1 (P4) |
Observations: O20 (epsilon margin on interest products); O21 task-1 seed: the 2026-08-18 GAP balance denial is for no_primary_insurance while the same line records the insurer's 2026-07-31 settlement — producible only as a denial made before the settlement letter reached the administrator; P4's prompt-payment tier measures from the settlement date while base claim_payment_days runs from the last document (company term, stated); carried O1–O8, O10–O12, O14–O17, O19.

## closing_checklist (revision_3)
Written after both round-3 reveals; the revision_3 charter sections above were frozen before them and are unchanged.
- Blind = GT on every write, owner, order, argument and on every expected / baseline_result / factor_sensitivity figure in both tasks.
- Revision_2 REDs: R2-F1, R2-F2, R2-F3, R2-C13b, R2-C13c, C21, R2-T1 — all closed (table above, verified against the artifacts). Revision_1 closures re-checked: no regression.
- Coverage/scope: task 0 {P1, P3, P2}, task 1 {P4, P5, P6, P7}; disjoint, complete; uuid8s unchanged.
- Trees: task 0 n = 2 (1 value_input), task 1 n = 3 (2 value_input); user write in each; acyclic; personas raise only the root.
- Factors: counts pass in every policy; every factor bears weight on its task's world; all-baselines definite and ≠ gold; ladders disjoint, real, faces = rules. Remaining: R3-F1 (XF2 shared VSC cancellation-date selection inlined across three P4 factors).
- Rounding: half up in rules, compute (`RND(x + 0.000001, 2)` on non-negative x) and tool bodies agree at exact ties (O20 margin note).
- Tool bodies enforce every docstring promise (dates, enums, amounts, references, partitions).
- Gates: coordinator snapshot r3 cited (7/7 OK); not re-run by the auditor.

Per-task verdicts: task 0 PASS; task 1 RED (R3-F1 only).

VERDICT revision_3: task0=PASS task1=RED charter=R3-F1

## revision_4

## charter_global_frozen (revision_4)
- Frozen 2026-10-22T07:09Z, before any round-4 GT was read; same independent auditor. Entry gate: last non-blank line of the worklog = `REWORK round 4: gates 7/7 green` (only that line read before this freeze). `/tmp/erl0075_coord/snapshot.sh gap_waiver_claims 4` run by the auditor: views `r4/0.view.json` sha256 bdf6adf1688751cc, `r4/1.view.json` sha256 35db1b12805a8f97 (both identical to r3); gate snapshot 2026-10-22T07:07:36 — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 gap.extended.yaml 3b086a6b8d20, task_tools.py 01f56d007e10, tasks/0.json 7e24a23768d7, tasks/1.json 2e74e51c79d1.
- Coordinator ruling applied: `RND(x + 0.000000001, 2)` under a "half up" rule is accepted; a value within 1e-9 below a half cent is DSL-KNOWN residue, not a RED; any larger rule/compute rounding mismatch, or a floor that creates an amount where the rule owes nothing, is RED.
- contamination_disclosure: GT of rounds 1–3 read in earlier revisions; round-4 derivation rests on the r4 views and the current charter; round-4 task JSON and worklog body not read before this freeze.
- Diff against the revision_3 copy (auditor scratch): rules, ladders, prerequisites, overwrites, params and baselines of all seven policies unchanged. Compute changes only: (1) every rounding epsilon 0.000001 → 0.000000001 (all seven policies); (2) P4 new plain binding `contract_closed: CFIELD('vsc', 'closed_date', purchase_deal_id=F('purchase_deal_id'), financed_on_contract='true') or '9999-12-31'` (basis = the contract-restatement ladder sentence) now read by `floor_excess`, `contract_counted`, `fee_addback`, `first_refund_paid`; (3) P3 `deferral_cut` reads the plain `loss_type` instead of a second LATEST, `negative_equity` reads `ltv_trade_payoff`/`ltv_trade_allowance`, and deferral_treatment's bindings now list `deferred`. Tools: `_GapRecords.cents` now `Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`; nothing else changed. Task views unchanged.
- Mechanical sweep: base copy equal; compute_basis quotes verbatim; every binding has a basis; baseline sentences, prerequisite sources, overwrites verbatim; no factor id in a tool name; uuid8s unchanged.

### closure of revision_3 findings
| id | status | evidence |
|---|---|---|
| R3-F1 | closed | the VSC cancellation date is now selected once (`contract_closed`, plain) and read by contract_counted, fee_addback, first_refund_paid and floor_excess; a sweep of every CFIELD/CPARAM/X*/LATEST/SUM/COUNT/EXISTS call string in every policy finds no selection repeated across factor bindings (the VSC expiration_date is read twice, both inside contract_counted, one factor). |

### regression and recipe re-check on the changed compute
- Rounding (XF8): every RND has the form `RND(x + 0.000000001, 2)` on a non-negative x (P1's adjustment as two non-negative magnitudes). Exact halves round up (653.125 → 653.13, 0.285 → 0.29, 1.005 → 1.01, 2.675 → 2.68 probed); a value within 1e-9 below a half cent is DSL-KNOWN residue by ruling. Tool `cents` rounds the decimal string half up — agrees. No floor creates an amount where the rule owes nothing: `MX(0.0, …)` floors return 0.00 (RND(1e-9) = 0.00); P4's `MX(overpayment / 2.0, …)` applies only when the rule's floor and threshold tests pass ("the late-payment interest owed and the stale-payoff waiver are subtracted from the overpayment but never take it below one half of the overpayment"); P7's `P('replacement_vehicle_credit_usd')` path is the rule's "a credit toward a replacement in any other status is replacement_vehicle_credit_usd".
- XF1/XF2 on P3: `negative_equity` (plain, feeding the baseline's negative-equity cut) now reads `ltv_trade_payoff`/`ltv_trade_allowance`, which are listed among ltv_reduction_tier's bindings. No factor tier reads another factor's binding, and the selection is not shared by several factors, so this is not a recipe-2 member; substituting ltv_reduction_tier's baseline (`ltv_method` only) leaves both trade reads in place — recorded as observation O22 (binding ownership). `deferred` is read only by deferral_cut (its own factor). No change to any figure.
- Figures: the charter compute evaluated on the r4 views reproduces P1 549.84, P3 2970.75, P4 332.73, P5 331.96 — unchanged from revision_3.
- Nothing that passed in revisions 1–3 regressed (rules, ladders, prerequisites, overwrites untouched; tool contracts unchanged except the half-up helper).

### findings (revision_4)
None. Observations: O20 superseded by the coordinator's 1e-9 ruling; O22 (above); carried O1–O8, O10–O12, O14–O17, O19, O21.

## closing_checklist (revision_4)
Written after both round-4 reveals; the revision_4 charter sections above were frozen before them and are unchanged.
- One audit file per task plus this file; revisions 1–4 preserved in order; every revision_4 comparison section carries PASS.
- Blind = GT on every write, owner, order, argument and on every expected / baseline_result / factor_sensitivity figure in both tasks.
- All seven extended policies covered; scopes disjoint (task 0 {P1, P3, P2}; task 1 {P4, P5, P6, P7}); tools closed; uuid8s independent and frozen.
- Trees: task 0 n = 2 (1 value_input), task 1 n = 3 (2 value_input); each has an owner=user write; difficulty-wide graph acyclic; personas raise only the root; every edge unmet at the opening and load-bearing; no tool refuses on an unresolved prerequisite.
- Factors: 4–6 per computation, ≥ 2 parameter / ≥ 1 method each, multi-source and cross-difficulty present per task; ladders of 3 disjoint, real tiers stated in the rules with matching ladder faces; every factor bears weight on its world; all-baselines definite and ≠ gold; recipe points 1–2 hold (R3-F1 closed, no other member).
- Rounding agrees with the rules at exact ties under the coordinator's 1e-9 ruling; tool bodies enforce every docstring promise.
- Gates: coordinator snapshot r4 cited (7/7 OK); not re-run by the auditor.

Per-task verdicts: task 0 PASS; task 1 PASS. Charter: no open RED.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- Frozen 2026-10-22T07:37Z, before any round-5 GT was read; same independent auditor. Input: the renderer's scan `audits/render_source/gap_waiver_claims/render_r1.md` (read in full; items A1–A6, B1, C1–C7, D1–D4, E1–E2). Entry gate: last non-blank worklog line = `REWORK round 5: gates 7/7 green`. `/tmp/erl0075_coord/snapshot.sh gap_waiver_claims 5` run by the auditor: views `r5/0.view.json` sha256 bdf6adf1688751cc, `r5/1.view.json` sha256 35db1b12805a8f97 (both identical to r3/r4); gate snapshot 2026-10-22T07:35:15 — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 gap.extended.yaml 16b1c6b1839e, task_tools.py 01f56d007e10 (unchanged), tasks/0.json 466acc763d0f, tasks/1.json 4f00d01d7b61.
- Rulings applied: RND(x + 0.000000001, 2) under half up accepted (within-1e-9 residue DSL-KNOWN); a floor creating an amount where nothing is owed is RED; action-form prerequisites with a valid fallback_reason acceptable (none present — all five edges remain state form).
- contamination_disclosure: GT of rounds 1–4 read in earlier revisions; round-5 derivation rests on the r5 views and the current charter; round-5 task JSON and the worklog body not read before this freeze.
- Diff against the revision_4 copy (auditor scratch): all seven policies changed (rule sentences, overwrites, compute, factor bindings, two baselines, P4 cross_category); base keys unchanged; tools unchanged. Mechanical sweep: base copy equal; compute_basis quotes verbatim; every binding has a basis; baseline sentences, prerequisite sources, overwrite clauses/replaced_by verbatim; no factor id inside a tool name.

### render_r1 items — graded against the artifacts
| item | grade | evidence |
|---|---|---|
| A1 (P7 credit priced when replacement_vehicle_credit_usd is 0.00) | closed | rule + baseline "A waiver whose replacement_vehicle_credit_usd is 0.00 receives no replacement vehicle credit."; compute `… if (line_on_file and P('replacement_vehicle_credit_usd') > 0) else 0.0`. Probe (Waiver 150, contracted new deal same store) → 0.00 = rule. No floor creates an amount. |
| A2 (P7 two loss dates) | closed | "the loss date … most recent claim line" sentence removed; `line_loss_date` now `LATEST(…, event_type='gap_benefit_paid', benefit_line_type='gap_balance')` = "the loss date of the paid line"; the deductible-reimbursement ladder keeps its own explicitly stated read ("on the waiver's most recent GAP balance claim line, paid or denied") — one source per stated quantity. |
| A3 (P1 unused-month convention) | closed | "In counting a cancelled waiver's whole calendar months, both the months it was in force and its unused months, a whole calendar month counts each time the start date's day of the month is reached …". Sweep: P3 (months at loss), P5 (both counts), P6 (tenure), P7 (loss-age) all state the convention for every MONTHS() they use; P2/P4 count no months. |
| A4 (P3 LTV threshold rounding) | closed | ladder now "reading the recorded cap amount, ltv_cap_pct times the waiver's vehicle_value_basis rounded half up to the cent … above the recorded cap amount … by no more than ltv_tolerance_pct of the recorded cap amount" = `recorded_cap_amount`. |
| A5 (P4 "first" refund) | closed | rule "the date its refund was last paid to the lienholder, where the earlier of those dates …" = MN of the per-product XLATEST. |
| A6 (P2 no completed request) | closed | courtesy ladder third tier "… or no completed cancellation request is on file, no courtesy credit is added"; compute gated on `COUNT(…, request_status='completed') > 0`. |
| B1 (P4 framing clause) | closed | the clause "a refund paid on a cancellation for a reason other than total_loss … carried its product's cancellation fee" is gone; the ladder keys on the stated reasons only. Sweep of every rule for other framing clauses asserting unrecorded facts: none found. |
| C1–C7 (assembly / overwrite sentences naming factor quantities) | closed | every replaced_by now refers to "the ladders of this rule" / "the order this rule states" / "the amount this rule assembles"; every assembly sentence is generic ("any reduction of the price that a ladder of this rule makes …", "every amount a ladder adds …", "any starting credit a ladder of this rule substitutes …") and still fixes the non-commuting order (reductions before the share, rounding points, floor last). |
| D1 (P4 late_pay_credit / half floor) | closed | prompt_pay_rate_tier now decides `late_pay_credit` (bindings line_settlement_date, late_pay_rate, late_pay_credit); the half-overpayment floor is a generic assembly bound inert at baseline (no amount where nothing is owed: it applies only to an overpayment > 0 the rule owes). |
| D2 (P1 single-factor plains) | closed | share_convention owns unused_months/unused_share; eff_date_rule owns recorded_stamp; cancel_charge_tier owns request_reason. |
| D3 (P3) | closed | ltv_reduction_tier owns recorded_cap_amount; late_charge_allowance_tier owns settlement_date; `deferred` is plain; `negative_equity` now reads the claim line (declared overwrite of gap_combo_addon_products' negative-equity sentence, self-scoped, restated for every other GAP benefit). |
| D4 (P7, P2) | closed | credit_age_rule owns line_loss_date/credit_age; new_vehicle_bonus_tier owns line_paid_date; release_late_window owns signed_date. |
| E1, E2 (P4 metadata) | closed | baseline.params [recovery_floor_usd]; cross_category reads now cancel_reason / cancellation requests / cancellation_fee_usd. |

Class sweeps (one pass, every policy): no plain binding is read by only one factor (mechanical); no factor binding is read by another factor (only assembly reads decided outputs); no selection is repeated across factor bindings; no assembly or replaced_by sentence names a factor quantity; ladder faces = rule anchors.

### new defect
**R5-F1 SOURCE-POLICY RED (rule ≠ compute at a decoy, XF8/XF9) — P3 deferral ladder's theft test.** Rule: "The loss type and the loss date the ladders of this rule read are those recorded on the same claim line" (the waiver's most recent GAP balance line) and "Deferral ladder: where the loss is a total_loss_theft, deferred payments are not subtracted; where the loss is a total_loss_collision, only deferred payments above deferral_allowance are subtracted …". Compute (changed this round): `deferral_cut: 0.0 if COUNT('gap_ledger', benefit_line_type='gap_balance', loss_type='total_loss_theft') > 0 else (…)` — the theft tier fires if **any** GAP balance line of the waiver ever carried total_loss_theft, while the other ladders (deductible, late charge) read the most recent line's `loss_type`. Probe (task-0 world plus one later GAP balance line on W2 reclassified total_loss_collision after recovery, same figures): compute 2425.75 (theft tier for deferral, collision tiers elsewhere); rule 2153.71 (collision tier: 572.04 − 300.00 = 272.04 subtracted). Producible (a theft claim re-figured as a collision total loss after the vehicle is found). Introduced in round 5 (r4 read `loss_type`). Not reached in either task world (one GAP balance line per claim figure set; task 0's only line is theft).

### observations (revision_5)
O23: P1 `flat_refund` (the baseline's free-look/unwound test) reads `effective_date`, a binding listed under eff_date_rule whose baseline sets it to the signed date as the baseline rule defines — the factor varies a baseline-defined quantity; unchanged since revision_2 and value-consistent under substitution. Carried: O1–O8, O10–O12, O14–O17, O19, O21, O22 (O22 resolved: `negative_equity` no longer reads ltv bindings).

## closing_checklist (revision_5)
Written after both round-5 reveals; the revision_5 charter sections above were frozen before them and are unchanged.
- Blind = GT on every write, owner, order, argument and figure in both tasks; tools unchanged; views unchanged.
- render_r1 items A1–A6, B1, C1–C7, D1–D4, E1–E2: all genuinely closed (table above); class sweeps found no further member.
- Regression: one — R5-F1, introduced by this round's edit of P3's deferral binding (the theft test moved from the most recent line's loss_type to "any GAP balance line with total_loss_theft"); every other revision 1–4 closure re-checked and holds.
- Gates: coordinator snapshot r5 cited (7/7 OK); not re-run by the auditor.

Per-task verdicts: task 0 PASS; task 1 PASS. Charter: R5-F1 open.

VERDICT revision_5: task0=PASS task1=PASS charter=R5-F1

## revision_6

## charter_global_frozen (revision_6)
- Frozen 2026-10-22T10:03Z; same independent auditor. Input: the open revision_5 id R5-F1. Entry gate: last non-blank worklog line = `REWORK round 6: gates 7/7 green`. `/tmp/erl0075_coord/snapshot.sh gap_waiver_claims 6` run by the auditor: views `r6/0.view.json` sha256 bdf6adf1688751cc, `r6/1.view.json` sha256 35db1b12805a8f97 (both identical to r3–r5); gate snapshot 2026-10-22T07:49:47 — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 gap.extended.yaml d71d97b2d1f7, task_tools.py 01f56d007e10 (unchanged), tasks/0.json 5b0015673ad2, tasks/1.json 8cfcd274fd34. (A duplicate of this request arrived after an account cut; this is the single revision_6.)
- contamination_disclosure: GT of rounds 1–5 read in earlier revisions. In this round the worklog's round-6 section (which restates the unchanged task figures) was read before this freeze, while checking the rework's rationale for the binding change; the per-task derivations below are unchanged from revision_3–5 on unchanged views, and they were re-evaluated with the charter compute rather than taken from the worklog.
- Diff against the revision_5 copy (auditor scratch): only P3 (gap_ext_balance_benefit) changed — `deferral_cut` reads the plain `loss_type` again, and deferral_treatment's bindings are `[deferred, deferral_cut]` (`deferred` re-claimed by the factor). Rules, overwrites, baselines, prerequisites, params, the other six policies and the tools unchanged; mechanical sweep clean.

### closure of revision_5 findings
| id | status | evidence |
|---|---|---|
| R5-F1 | closed | `deferral_cut: 0.0 if loss_type == 'total_loss_theft' else (…)` where `loss_type = LATEST('gap_ledger', 'loss_type', date_field='entry_date', benefit_line_type='gap_balance')` = "the loss type … recorded on the same claim line" (the most recent GAP balance line), the same read as the deductible and late-charge ladders. Probe (task-0 world + a later collision line): compute 2153.71 = rule 2153.71. Sweep of every COUNT / SUM / EXISTS / LATEST read in all seven policies against its rule: no other "any line" vs "most recent line" member. |

### regression check on the changed binding (render_r1 class D, recipe 4)
**R6-F1 SOURCE-FACTOR RED — regression of render_r1 D3 (graded closed in revision_5).** render_r1 D3: "factor-claimed bindings deferred (deferral_treatment) … are read by the baseline (deferral baseline …)". Revision_5 closed it by making `deferred` plain; round 6 re-claims it: deferral_treatment `bindings: [deferred, deferral_cut]` while its own `baseline: {deferral_cut: "deferred if P('exclude_deferred_payments') else 0.0"}` — the computation document's "deferred payments … are each subtracted in full where the waiver's switch for that item is true" reads a raw claim-line figure that the deferral factor claims and does not vary (no tier of the deferral ladder changes the deferred payments; it changes only how much of them is cut). No number changes (deferral baseline on task 0: 2398.71, as before). Class sweep (factor-claimed binding read by a baseline/plain binding, one pass): members — P3 `deferred` (above, RED). Also matched by the mechanical pattern but **not** a member: P1 `effective_date` (eff_date_rule) read by the baseline's free-look test `flat_refund` — the factor varies it (payoff / recorded / signed date) and its baseline binding states the baseline value `effective_date: signed_date` exactly as the baseline rule defines it ("The effective date of the cancellation is the request date the holder signed …"), so the baseline reads the factor's own varied quantity at its stated default (O23, unchanged since revision_2, not flagged by the renderer). No other member.

### XF_recipe re-check on the changed sentence
No rule sentence changed. Points 1–2 (independence, shared selections): deferral_cut reads the shared plain `loss_type` (also read by deductible and late-charge ladders) — correct form. Points 8–9 (rule = compute, decoy probe): pass. Point 4: see R6-F1.

### findings (revision_6)
| id | verdict | tasks |
|---|---|---|
| R6-F1 | SOURCE-FACTOR RED (regression of render D3) | task 0 (P3; structural, no numeric consequence) |

## closing_checklist (revision_6)
- Blind = GT on every write, owner, order, argument and figure in both tasks; views and tools unchanged.
- R5-F1 genuinely closed (rule = compute at the decoy, 2153.71). Regression: R6-F1 (render D3 re-opened by re-claiming `deferred` under deferral_treatment); every other closure of revisions 1–5 unchanged (no other policy or tool changed).
- Gates: coordinator snapshot r6 cited (7/7 OK); not re-run by the auditor.

Per-task verdicts: task 0 RED (R6-F1, structural); task 1 PASS.

VERDICT revision_6: task0=RED task1=PASS charter=R6-F1

## revision_7

## charter_global_frozen (revision_7)
- Frozen 2026-10-22T10:23Z, before any round-7 GT or the worklog body was read; same independent auditor. Input: the open revision_6 id R6-F1. Entry gate: last non-blank worklog line = `REWORK round 7: gates 7/7 green`. `/tmp/erl0075_coord/snapshot.sh gap_waiver_claims 7` run by the auditor: views `r7/0.view.json` sha256 bdf6adf1688751cc, `r7/1.view.json` sha256 35db1b12805a8f97 (identical to r3–r6); gate snapshot 2026-10-22T10:22:10 — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 gap.extended.yaml 8dc4939fac31, task_tools.py 01f56d007e10 (unchanged), tasks/0.json e28f8aba8720, tasks/1.json 0acc5a916fbe.
- contamination_disclosure: GT of rounds 1–6 read in earlier revisions; nothing of round 7 read before this freeze.
- Diff against the revision_6 copy: only P3 changed — (1) deferral_treatment's bindings no longer list `deferred` (plain again, basis = the baseline sentence "Past-due payments, late fees and charges, deferred payments, … are each subtracted in full where the waiver's switch for that item is true"); (2) the deferral ladder's collision tier gains a tenure condition — rule "where the loss is a total_loss_collision and the waiver had been in force 12 or more months at the loss, only deferred payments above deferral_allowance are subtracted …; in every other case, any other loss type or a collision in the first 12 months, deferred payments are subtracted in full where that switch is true", compute `… if (loss_type == 'total_loss_collision' and MONTHS(F('sale_date'), loss_date) >= 12) else (deferred if P('exclude_deferred_payments') else 0.0)`, ladder face and evidence ['history', 'date'] updated to match. Other six policies, base keys and tools unchanged. Mechanical sweep clean.

### closure of revision_6 findings
| id | status | evidence |
|---|---|---|
| R6-F1 | closed | `deferred` is a plain binding again; deferral_treatment's bindings are `[deferral_cut]`; its baseline `deferred if P('exclude_deferred_payments') else 0.0` reads only plain bindings. Sweep (one pass, all policies): no factor baseline reads a factor-owned binding; the only plain read of a non-decided factor binding is P1 `flat_refund` → `effective_date`, not a member (O23, reasoning in revision_6). |

### XF_recipe re-check on the changed sentence (P3 deferral ladder)
- Rule = compute = ladder face (three tiers, disjoint as stated: theft / collision with ≥ 12 months / everything else); month count uses the convention P3 already states ("In counting the months a GAP waiver was in force at its loss …"). Point 1: reads only plain `loss_type`, `loss_date`, `deferred`. Point 5: tiers 0 | MX(0, D − 300)·switch | D·switch — distinct shapes; the tenure condition only moves a world between existing shapes. Point 6: T1 on task 0 (theft tier) 2398.71 vs 2970.75 — moves; T2: a ≥12-month collision with deferred payments and the switch true (Waiver 125/140/150) — exists. Point 22: a smaller deferral deduction for collisions after a year of payments (deferrals granted after a record of payments) is a credible company term; the 12-month cut-off is the same boundary already used by P3's other tenure ladders. Probes: task-0 world + a later collision line at 23 months → 2153.71 (allowance tier); with a 5-month loss date → 2198.71 (full subtraction, early-collision deductible tier) — both as the rule states.
- render_r1 items A1–A6, B1, C1–C7, D1–D4, E1–E2: no other sentence or binding changed since revision_5, where each was graded closed; D3 is back to its revision_5 closed form. Revision 1–5 closures hold (no other policy or tool changed).
- Figures: charter compute on the r7 views — P1 549.84, P3 2970.75 (factor substitutions 2470.75 / 2770.75 / 2925.75 / 2398.71 / 3878.25 / 4158.49), P4 332.73, P5 331.96.

### findings (revision_7)
None. Observations carried (O23 and earlier).

## closing_checklist (revision_7)
- Blind = GT on every write, owner, order, argument and figure in both tasks; views and tools unchanged since r3/r5.
- R6-F1 genuinely closed; render_r1 items all remain closed; revision 1–6 closures hold; the one changed sentence (P3 deferral ladder) passes XF points 1, 5, 6, 8, 9, 22 and its probes.
- Factors: counts, tiers, weights and baselines as revision_5/6 (P3 deferral_treatment T1 2398.71 ≠ 2970.75).
- Gates: coordinator snapshot r7 cited (7/7 OK); not re-run by the auditor.

Per-task verdicts: task 0 PASS; task 1 PASS. Charter: no open RED.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

## charter_global_frozen (revision_8)
- Frozen 2026-10-22T10:36Z, before any round-8 GT or the worklog body was read; same independent auditor. Input: renderer round-2 finding N1 in `audits/render_source/gap_waiver_claims/render_r2.md` (read in full; it also re-confirms render_r1 A1–E2 closed). Entry gate: last non-blank worklog line = `REWORK round 8: gates 7/7 green`. `/tmp/erl0075_coord/snapshot.sh gap_waiver_claims 8` run by the auditor: views `r8/0.view.json` sha256 bdf6adf1688751cc, `r8/1.view.json` sha256 35db1b12805a8f97 (unchanged); gate snapshot 2026-10-22T10:35:39 — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 gap.extended.yaml 8a7e2433a8ce, task_tools.py 01f56d007e10 (unchanged), tasks/0.json e4fe86efd88f, tasks/1.json af56acc2c991.
- contamination_disclosure: GT of rounds 1–7 read in earlier revisions; nothing of round 8 read before this freeze. Self-correction: revision_1–7 did not flag N1, which was present since round 3's fee add-back; this revision grades it on the artifacts.
- Diff against the revision_7 copy: only P4 changed — the fee add-back ladder sentence, its factor face, `plan_reason` (now `XLATEST('maintenance', 'maintenance_cancellation_requests', 'cancel_reason', date_field='request_date', maintenance_plan_id=plan_id, request_status='completed')`) and the maintenance cross_category reads/note. Other six policies, base keys and tools unchanged; mechanical sweep clean.

### N1 — graded against the artifacts
| item | grade | evidence |
|---|---|---|
| N1 (P4 fee add-back: rule silent on the lienholder-payment gate; plan reason read from a refund-paid row) | closed | rule now "reading each add-on's reason from its completed cancellation request and counting only an add-on whose refund was paid to the lienholder, where both … were cancelled on or after the loss date for the reason customer_request or vehicle_sold_or_traded and both refunds were paid to the lienholder, … both fees …; where only one of them was so cancelled with its refund paid to the lienholder, that product's cancellation_fee_usd is added; in every other case nothing is added" = compute (fee gated on `plan_refund > 0` / `contract_refund > 0`, the lienholder-paid sums; reasons from the completed requests on both products); factor face updated to the same three tiers. Renderer's probe (plan refund 0.00 or paid to the customer; contract cancelled for customer_request, paid to the lienholder): rule and compute both add only the contract's fee. Task 1: plan reason from request 64d3a37b… = customer_request → 75.00 (unchanged). |

### sweep: rule-ladder vs compute-gating (one pass, every factor of every policy)
Each factor's compute was read against its ladder sentence for gates the rule does not state (or rule conditions the compute omits): P1 (6 factors), P2 (4), P3 (6), P4 (5), P5 (6), P6 (5), P7 (5), and every result-level gate (P1 `request_on_file`/`flat_refund`, P2 `payee_lienholder`, P3 `claim_on_file`, P4 floor test, P5 `in_scope`/`deal_unwound`, P6 `payee_holder`, P7 `repl_type` / credit > 0). Every gate is a stated condition or a stated definition (e.g. P4 "refunds … paid to the lienholder" defining the refunds received; P5/P7 "where that deal stands in contracted status"; P6/P2 payee sentence). No further member.

### regression
P4 figures: charter compute on the r8 view 332.73 (fee add-back substitution 257.73, unchanged); P1 549.84, P3 2970.75, P5 331.96 unchanged. render_r1 items and revision 1–7 closures hold (no other policy or tool changed).

### findings (revision_8)
None.

## closing_checklist (revision_8)
- Blind = GT on every write, owner, order, argument and figure in both tasks; views and tools unchanged.
- N1 genuinely closed; the rule-ladder vs compute-gating sweep over all 37 factors and every result gate finds no further member; render_r1 items and revision 1–7 closures hold.
- Gates: coordinator snapshot r8 cited (7/7 OK); not re-run by the auditor.

Per-task verdicts: task 0 PASS; task 1 PASS. Charter: no open RED.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

## charter_global_frozen (revision_9)
- Frozen 2026-10-22T12:29Z, before any round-9 GT or the worklog body was read; same independent auditor. Input: KB audit source item S1 (`audits/policy_kb/gap_waiver_claims/_difficulty.md`: the seeded Kessler Care refund 339.15 is the maintenance baseline; the published retail-cancellation docs give 409.06 — pro rata 498.04, fee 75.00, bundle recapture 13.98; moves the reversal 332.73 → 402.64 and the credit 1912.27 → 1842.36). Entry gate: last non-blank worklog line = `REWORK round 9: gates 7/7 green`. `/tmp/erl0075_coord/snapshot.sh gap_waiver_claims 9` run by the auditor: views `r9/0.view.json` sha256 bdf6adf1688751cc (unchanged), `r9/1.view.json` sha256 b07a721f8283c62d; gate snapshot 2026-10-22T12:26:49 — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 gap.extended.yaml 8a7e2433a8ce, task_tools.py 01f56d007e10, tasks/0.json dc454e000826, tasks/1.json ecc8a9bed338.
- Seed-only confirmed: gap.extended.yaml and task_tools.py are byte-identical (`cmp`) to the auditor's revision_8 copies (8a7e2433a8ce / 01f56d007e10). View diff r8 → r9: task 0 identical; task 1 only `maintenance_plan_ledger` ee8c7e34… (maintenance_refund_calculated) and 4ce5f41a… (maintenance_refund_paid, lienholder, 2026-08-27) amount 339.15 → 409.06; persona and frozen_time unchanged.
- contamination_disclosure: GT of rounds 1–8 read earlier; the KB audit file states the two moved values (402.64, 1842.36) — read before this freeze as the round's input; the re-derivation below was done independently from the r9 view and the charter compute and agrees with it.

### S1 — re-priced rows against the published maintenance docs
Plan KC-5308126 (Kessler Care Plus 8-Visit, price 664.05, retail price 699.00, financed 'true', sold 2024-03-16 on deal 13afa180…, 2 visits used), cancelled on request 64d3a37b… for customer_request, request date 2026-08-06 = processing date (created 2026-08-06 15:42, refund entry 2026-08-06) → in scope of `maintenance_ext_retail_cancel_refund` (docs/maintenance/retail_plan_cancellation_desk_4f8235e8: "a … Plus … plan cancelled for a reason other than a total loss on a request processed on its own request date"). Factors from the published docs:
- refund basis (retail_refund_method_financing_and_term_6746c928): financed → "purchase price times unused visits, divided by visits included" = 664.05 × 6/8 = 498.0375 → **498.04**;
- retail cancellation fee (trade_up_cancellation_fee_d54a541c): no vehicle-price charge fewer than 3 whole months before 2026-08-06 (charges 2023-05-20, 2024-03-16; the 2026-09-08 charge is after the effective date) → the plan's fee **75.00**;
- bundle recapture (bundle_discount_recapture_2eddb3c3): sold on a deal below the retail plan price (699.00 − 664.05 = 34.95), 28 whole months in force (24–47) → 0.4 × 34.95 = **13.98**;
- Owner Rewards refund credit (owner_rewards_refund_credit_f1edd2c8): no service account in the world → none;
- free look / unwound: no.
Refund = 498.04 − 75.00 − 13.98 = **409.06** = both re-priced rows; paid to the lienholder (financed) 21 days after processing (≤ 30, refund_payment_terms) — **S1 closed**. The Kessler Shield rows (not re-priced) re-checked against docs/vsc: a total-loss cancellation stays on clauses 6–7 (cancellation_and_refund_clauses_668cc0f8: "Every other refund, for example a total-loss cancellation, is still worked as clauses 6 and 7 read") → 2895.00 × 1318/2191 = 1741.49, fee waived on total loss; loss-date restatement 1758.67 = the paid line's recorded add-on figure. The KB's vsc conditional is thereby resolved PASS. XF16: no maintenance/vsc write owed at the opening (refunds paid within 30 days, refund-due 0.00, requests completed).

### moved figures — re-derived from the r9 view (task 1)
- P4: plan refund received 409.06, cancellation 2026-08-06 between loss (2026-07-24) and payment (2026-09-03) → counted MX(204.53, 359.06) = 359.06; contract restated 1741.49 × 1331/1318 = 1758.667; fee add-back (plan reason customer_request from its completed request, refund paid to the lienholder) 75.00, contract (total_loss) 0.00; uncredited 359.06 + 1758.667 + 75.00 − 1758.67 = 434.057; claim standing 1621.69; floor test 409.06 + 1741.49 − 1758.67 = 391.88 > 60 and line 1621.69 > 60; prompt-payment 1.42 (34 days, 8 %); stale-payoff 30.00 → RND(MX(217.03, 402.637)) = **402.64**. Factor substitutions (charter compute): plan timing 452.64, contract restatement 385.46, fee add-back 327.64, prompt-pay 404.06, stale-payoff 432.64 — all move; all-baseline 391.88 ≠ 402.64.
- P7: 1095.00 + 500.00 + 300.00 + 250.00 + 100.00 − 402.64 = **1842.36**; substitutions credit-age 2247.36, new-vehicle 1342.36, store 1542.36, deductible 1592.36, price 1742.36; all-baseline 1097.36.
- P5 331.96 and P6 367.31 do not read the plan (unchanged); task 0 unchanged (549.84 / 2970.75 / 579.84).

### regression / recipe check
Charter and tools byte-identical → every revision 1–8 closure, render_r1/r2 item and class sweep holds. P7←P4 wait still met only by a positive reversal (excess 391.88 > 60 → 402.64 > 0). No floor creates an amount: P4's half-overpayment bound and MX(0,…) floors unchanged.
Observation O24 (new, not a RED): with the published maintenance extended rules, a customer_request cancellation of a financed plan is refunded on a pro-rata basis less fee and bundle recapture (409.06), so P4's fee add-back no longer restores the plan's loss-date total-loss value (docs/maintenance total-loss rule: 414.15 standard refund + 20.00 plan relationship credit = 434.15) — it counts 409.06 + 75.00 = 484.06 before the timing absorb. P4's rule states the add-back as a company term and is applied exactly as written (unique value, factor bears weight); recorded for the coordinator's realism review.

### findings (revision_9)
None.

## closing_checklist (revision_9)
- Seed-only round confirmed (charter and tools byte-identical); S1 closed: both re-priced Kessler Care rows = 409.06 under the published docs/maintenance retail-cancellation rule; the Kessler Shield rows reproduce under docs/vsc.
- Moved gold re-derived from the r9 view: reversal 402.64, credit 1842.36 (blind = GT); every task-1 factor still bears weight (P4 five, P7 five substitutions all ≠ gold; all-baselines 391.88 / 1097.36 ≠ gold); task 0 unchanged.
- No regression; O24 recorded for realism review (not a RED).
- Gates: coordinator snapshot r9 cited (7/7 OK); not re-run by the auditor.

Per-task verdicts: task 0 PASS; task 1 PASS. Charter: no open RED.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN
