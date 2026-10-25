# gap_waiver_claims — plan (M=2)

Draws (draw_counts.py): task 0 prerequisite_problems=2, factor_counts [6,6,4]; task 1 prerequisite_problems=3, factor_counts [5,6,5,5].

## Why this shape (thin charter)
Every value_input edge needs a same-waiver successor that reads the predecessor's write (DSL F/SUM/LATEST are scoped to the target waiver; own-category CFIELD is forbidden). In the gap charter the only same-waiver successor writes are: the replacement vehicle credit (reads the paid GAP balance line) and the refund release (reads the refund calculation). Task 1 needs 2 value_input edges -> two chains joined by a record-test state gate; task 0 needs 1.

## Problems / tools (7, pairwise disjoint)
| id | tool (owner) | event(s) written (base triggers) | computes | task | factors |
|---|---|---|---|---|---|
| gap_ext_holder_cancellation_refund | confirm_gap_cancellation_* (user) | gap_waiver_cancelled -> triggers gap:gap_refund_calculated (same category, booked in the same call); request marked completed | refund_amount | 0 | 6 |
| gap_ext_lienholder_refund_release | release_refund_lienholder_* (agent) | gap_refund_paid (triggers []) | amount_paid | 0 (root) | 4 |
| gap_ext_addon_overpayment_recovery | recover_benefit_overpayment_* (agent) | gap_benefit_reversed (triggers []) | amount | 0 | 6 |
| gap_ext_balance_benefit | pay_gap_balance_* (agent) | gap_benefit_paid (gap_balance) + gap_waiver_claim_settled (triggers []) | amount | 1 | 6 |
| gap_ext_replacement_credit | apply_replacement_allowance_* (user) | gap_benefit_paid (replacement_vehicle_credit) (triggers []) | credit_amount | 1 (root) | 5 |
| gap_ext_payoff_termination_refund | terminate_paid_off_waiver_* (agent) | gap_waiver_terminated -> triggers gap:gap_refund_calculated (same category) | refund_amount | 1 | 5 |
| gap_ext_holder_refund_release | release_refund_holder_* (agent) | gap_refund_paid (triggers []) | amount_paid | 1 | 5 |
No tool writes any other category; no event written has a cross-category trigger.

## Trees
Task 0 (customer Gordon Whitlock): root lienholder_refund_release(W_D)
 - -> holder_cancellation_refund(W_D) value_input (refund due read by the release) [user tool]
 - -> addon_overpayment_recovery(W_X) state_gate (release to a lienholder waits until any overpayment that lienholder holds on another waiver of the holder stands reversed; same lienholder)
Task 1 (customer Teresa Vasquez-Yoder -> surname band S-Z): root replacement_credit(W_A) [user tool]
 - -> balance_benefit(W_A) value_input (credit reads the paid GAP balance line)
 - -> holder_refund_release(W_B) state_gate (credit waits until every waiver on a vehicle traded into the replacement purchase carries a paid refund)
 - holder_refund_release(W_B) -> payoff_termination_refund(W_B) value_input

## Owed-at-once check (recipe 16)
VSC / maintenance products read by any factor are seeded already cancelled with refunds calculated and paid (or never cancellable without a holder signature), so nothing in another product is owed at once; reads are keyed on recorded entries.

(Factor tables, all-pairs method tables, T1/T2 tests and probe tables follow below as each policy is written.)

## Round 1 resume — task 1 redesign (balance benefit went to task 0)
Task 0 on disk claims holder_cancellation_refund + balance_benefit + lienholder_refund_release (not the recovery). Task 1 claims the remaining four writes, the only money writes left in the gap charter:
| id | tool (owner) | event written (base triggers) | computes | factors |
|---|---|---|---|---|
| gap_ext_addon_overpayment_recovery | recover_benefit_overpayment_99b30941 (agent) | gap_benefit_reversed (triggers []) | amount | 5 |
| gap_ext_payoff_termination_refund | terminate_paid_off_waiver_88a68523 (agent) | gap_waiver_terminated -> gap:gap_refund_calculated (same category, booked in the same call) | refund_amount | 6 |
| gap_ext_holder_refund_release | release_refund_holder_bc39910a (agent) | gap_refund_paid payee customer (triggers []) | amount_paid | 5 |
| gap_ext_replacement_credit | apply_replacement_allowance_cdefd282 (user) | gap_benefit_paid replacement_vehicle_credit (triggers []) | credit_amount | 5 |

Task 1 tree (customer Teresa Vasquez-Yoder): root replacement_credit(W_A, RAV4 claim GC-5240617) [user tool]
 - -> addon_overpayment_recovery(W_A) value_input (credit sets off the overpayment reversed on the claim) — affirmative "fixed only after"
 - -> holder_refund_release(W_B, Civic) state_gate (credit waits until every other waiver whose loan was reported paid off on/after the replacement purchase's contract date carries a refund payment to the holder) — negated "not applied until"
 - holder_refund_release(W_B) -> payoff_termination_refund(W_B) value_input (refund due + effective date) — negated "not made until"
Order: recovery and termination commute (different waivers); release after termination; credit last.
Replacement purchase locator (recipe 12 coarse exact test): the holder's group purchase deal in contracted status (signed buyer's order awaiting delivery) — a factory-order RAV4 Hybrid with the Civic taken in trade at signing (customer drives a loaner until arrival).
Owed-at-once (recipe 16): the Kessler Care plan on the RAV4 deal is seeded cancelled (total_loss, effective 2026-08-06) with refund calculated and paid to the lienholder 2026-08-27; nothing in maintenance is owed. Deal R is contracted (factory order) — no delivery/late-balance obligation is due.
Events written by task-1 tools: gap_benefit_reversed, gap_waiver_terminated + gap_refund_calculated, gap_refund_paid (refund_payee customer), gap_benefit_paid (replacement_vehicle_credit). None has a cross-category trigger.

## Task 1 factor tables — round 1 (historical, superseded by the round-3 tables below)
| policy | factor | effect | tiers (fall-through last) | world tier | T1: baseline-alone result (expected) | T2: producible world where it alone moves |
|---|---|---|---|---|---|---|
| recovery | plan_timing_count | method (x maint) | eff < loss: 0 / loss<=eff<paid: MX(0,refund-absorb) / else refund | middle | 349.15 (299.15) | any plan cancelled before the loss (-> 0) |
| recovery | reversal_tenure_tier | param | >=36: 25 / 24-35: 15 / <24: 0 | 15 | 314.15 | holder with 24+ months, other tiers baseline |
| recovery | reversal_loss_tier | param, multi | collision & deductible>cover: 25 / theft & settled >30d: 35 / 0 | 25 | 324.15 | collision with deductible above cover |
| recovery | reversal_return_tier | param, x purchase, multi | new contracted order >= loss: 15 / used: 10 / 0 | 15 | 314.15 | contracted new order only |
| recovery | reversal_lag_tier | param, x maint | lag >30: 20 / 15-30: 10 / 0 | 10 | 309.15 | plan refund paid 15+ days after cancel |
| termination | termination_anchor | method, x purchase | payoff within free look: sale date / trade-in order <=30d before payoff: contract date / payoff date | middle | 337.92 (348.33) | any trade-in order crossing a month boundary |
| termination | termination_share_rule | method | term>=72: whole months / term<=48: sum of digits / days | whole months | 348.60 | any 72-month waiver whose day share differs |
| termination | termination_charge_tier | param, multi | switch false & >=36m: 15 / false & 24-35: 30 / fee or 0 | 15 | 313.33 | Used 140 waiver 36+ months |
| termination | termination_admin_tier | param, x purchase | new deal: 30 / used-cpo-value: 45 / 0 | 45 | 368.33 | any used deal |
| termination | financing_retention_tier | param, x purchase | >125%: 40 / >100%: 20 / 0 | 20 | 368.33 | financed above value |
| termination | trade_in_credit_tier | param, x purchase, multi | trade & new: 50 / trade & used: 25 / 0 | 50 | 298.33 | contracted order with trade |
| holder release | holder_rate_source | param, x purchase | APR>6: APR / APR<=6: 6% / none: 5% | APR 8.49 | 385.28 (386.41) | any late release with APR on deal |
| holder release | holder_interest_clock | method | eff<payoff: days from eff / payoff >30d before: days from payoff / days past window | first | 383.69 | backdated termination |
| holder release | holder_rate_premium | param | >45d: +2% / 21-45: +1% / 0 | +1% | 386.08 | release 21+ days after eff with interest days |
| holder release | payoff_courtesy_tier | param | payoff >10d before: 20 / 4-10: 10 / 0 | 20 | 366.41 | payoff report left unprocessed |
| holder release | tenure_goodwill_tier | param | >=36m: 15 / 24-35: 8 / 0 | 15 | 371.41 | long-held waiver |
| credit | new_vehicle_bonus_tier | param, x purchase, multi | new order 0-30d after paid line: 500 / new >30d: 250 / 0 | 500 | 1445.85 (1945.85) | new order, other tiers baseline |
| credit | credit_age_rule | method | loss-age>=36: credit x day share / 24-35: MN(credit, price) / credit | MN pick | 2350.85 | price below credit at 24-35 months |
| credit | return_store_bonus_tier | param, x purchase, multi | same store & trade: 300 / same store: 150 / 0 | 300 | 1645.85 | same-store order |
| credit | deductible_reimbursement_tier | param | collision & ded>cover: 250 / other & ded>cover: 150 / 0 | 250 | 1695.85 | deductible above cover |
| credit | replacement_price_tier | param, x purchase | >=40k: 200 / >=25k: 100 / 0 | 100 | 1845.85 | any order >= 25k |
All-pairs (method factors): plan timing 0 vs refund-absorb (input refund, absorb) / 0 vs refund (refund) / refund-absorb vs refund (absorb); anchor sale date vs contract date vs payoff date (three distinct record dates); share whole months vs sum of digits (u(u+1)/T(T+1)) vs days (day counts); clock days-from-eff vs days-from-payoff (eff vs payoff) vs days-past-window (window 30); credit age credit x day share vs MN(credit, price) (price) vs credit (share). No two tiers of any ladder select the same value or method.
Independence (recipe 1): every factor's tier test reads records or plain bindings (claim line, plan, contracted order, waiver fields, payoff date); none reads another factor's binding (termination months in force are counted to the loan_payoff_date, not to the factor-chosen effective date).

## Task 1 probe table — round 1 (historical, superseded below)
| read | probe | result |
|---|---|---|
| plan CFIELD by deal + financed | plan cancelled before loss | rec 0.00 (timing tier 1) |
| same | cancelled after the line was paid | rec 359.15 (full refund counted) |
| plan refund XSUM payee lienholder | payment to the customer instead (decoy payee) | rec 0.00 |
| same | no plan / plan bought for cash (financed false) | rec 0.00 |
| contracted-order CFIELD | no contracted order | rec 314.15; ter 287.92 (payoff anchor, no trade credit); cr 1500.00 (out of scope: flat credit) |
| same | order signed 40 days before payoff / after payoff | ter 337.92 (payoff anchor) |
| same | order without trade-in | ter 287.92 |
| same | order at another store | cr 1945.00 |
| same | order signed before the GAP payment (negative lag) | cr 1745.00 (no new-vehicle bonus; base window also fails) |
| credit lines SUM | an earlier paid credit of 500 on the claim | cr 1745.00 |
| refund calculation SUM | none (opening world) | rel 0.00 (not released) |
Known limit: two contracted orders at once -> CFIELD first match; the rule names "the holder's group purchase deal in contracted status" (one open replacement order), stated as a plain record test.

## Round 2 / round 3 (supersedes the round-1 task-1 tables and probe table above; figures updated in round 3)
Trees unchanged in shape. Task 0: root lienholder release <- holder cancellation (value_input, user tool) + GAP balance payment (state_gate: the other same-lender waiver's run theft-waiting-period denial must carry a paid GAP balance line). Task 1: root replacement credit (user tool) <- add-on overpayment reversal (value_input) + holder release (state_gate: other paid-off waivers out of active status with no refund due); holder release <- payoff termination (value_input).
Events written (base triggers): confirm -> gap_waiver_cancelled + gap_refund_calculated (same category, booked in the call); pay -> gap_benefit_paid + gap_waiver_claim_settled; release_lienholder / release_holder -> gap_refund_paid; recover -> gap_benefit_reversed; terminate -> gap_waiver_terminated + gap_refund_calculated (pro_rata or flat_deal_unwound); apply -> gap_benefit_paid (replacement_vehicle_credit). No trigger lands in another category.
Record partition (C1), verbatim in P1 and P5: "An active waiver that carries a submitted signed cancellation request recorded for it ends by the holder's cancellation, whether or not its lienholder has reported a loan payoff date; an active waiver with a loan_payoff_date on file and no submitted signed cancellation request ends by termination." Tools enforce it (confirm needs a submitted request of the waiver; terminate refuses a waiver with one or without a payoff date).
Rounding (C5): one convention, half up to the cent — rule sentences say "rounded half up to the cent", docstrings say "(a half cent goes up)", tool bodies use _GapRecords.cents (integer half-up), compute uses RND(x + 0.000000001, 2) on non-negative values at the rule's rounding points (round 4: epsilon 1e-9).

### Factor table (T1 = that factor's baseline alone on the task world; T2 = a producible world where it alone moves)
| policy | factor | effect | tiers (fall-through last) | world tier | T1 (expected) | T2 |
|---|---|---|---|---|---|---|
| P1 cancellation | eff_date_rule | m | payoff before signing: payoff date + days credited / recorded > grace: recorded date, days given up / signed date | recorded | 554.58 (549.84) | any late-recorded request |
| P1 | share_convention | m | term>=72 & >=12m: whole months / term<=60 & <12m: sum of digits / days (from the signed date) | months | 552.11 | 72-month waiver past a year |
| P1 | cancel_charge_tier | p | >=24m & customer_request: 0 / 12-23m & customer_request: 25 / fee | 25 | 524.84 | 12-23 month canceller |
| P1 | admin_portion_tier | p, x purchase | new: 40 / used: 60 / 0 | 40 | 582.07 | any dealer deal |
| P1 | early_charge_tier | p | <12m: 75 / 12-23: 35 / 0 | 35 | 584.84 | early canceller |
| P1 | bundle_recapture_tier | p, x vsc/maint | active VSC: 50 / active plan: 25 / 0 | 50 | 599.84 | active VSC on the deal |
| P2 lienholder release | release_rate_source | p, x purchase | APR>ceiling: 0.09 / standard<APR<=ceiling: APR / standard | APR | 578.27 (579.84) | any late release, APR 5-9 |
| P2 | release_late_window | m | unwound reason & deal: unwind date / mail late: signed date / effective date | signed date | 578.26 | late-recorded request |
| P2 | release_rate_premium | p | >60d: +0.02 / 31-60: +0.01 / 0 | +0.01 | 579.27 | release 31-60 days late |
| P2 | release_courtesy_credit | p | recorded >30d before: 25 / 15-30: 10 / 0 | 25 | 554.84 | old request |
| P3 GAP balance | (unchanged six factors) | | | | 2470.75 / 2770.75 / 2925.75 / 2398.71 / 3878.25 / 4158.49 (2970.75) | as round 1 |
| P4 reversal | plan_timing_count | m | before loss: 0 / loss..payment: max(half, R-50) / R | middle | 452.64 (402.64) | plan cancelled between loss and payment |
| P4 | contract_restatement | m, x vsc | before loss: 0 / after loss: R x days(loss,exp)/days(eff,exp) / R | after loss | 385.46 | VSC cancelled after the loss |
| P4 | fee_addback_tier | p, x maint/vsc | both add-ons fee-bearing: plan fee + contract fee / exactly one: its fee / neither: 0 | plan fee 75 | 327.64 | holder-requested cancellation of one add-on |
| P4 | prompt_pay_rate_tier | p | paid > 2 x claim_payment_days after settlement: 0.12 / > claim_payment_days: 0.08 / within: 0 | 0.08 (interest 1.42) | 404.06 | any line paid 31+ days after settlement |
| P4 | stale_payoff_tier | p, x | counted refund before pay: 30 / first within 30d after: 15 / 0 | 30 | 432.64 | counted refund before the payment |
| P5 termination | termination_share_rule | m | term>=72: months / <=48: SoD / days (from the payoff date) | months | 332.23 (331.96) | 72-month waiver |
| P5 | termination_backdating | m, x purchase | free-look payoff: sale-date credit / trade order <=30d: order-date credit / none | order | 328.33 | trade-in payoff |
| P5 | termination_charge_tier | p, multi | switch false & >=36m: 15 / false & 24-35: 30 / fee or 0 | 15 | 296.96 | Used 140 waiver 36+ months |
| P5 | termination_admin_tier | p, x purchase | new: 30 / used: 45 / 0 | 45 | 351.96 | any dealer deal |
| P5 | trade_in_credit_tier | p, x purchase, multi | trade & new: 50 / trade & used: 25 / 0 | 50 | 281.96 | contracted order with trade |
| P5 | termination_bundle_tier | p, x vsc/maint | active VSC: 40 / active plan: 20 / 0 | 40 | 371.96 | active VSC on the deal |
| P6 holder release | holder_rate_source | p, x purchase | APR>ceiling: 0.09 / APR: APR / standard | APR | 367.18 (367.31) | late release, APR 5-9 |
| P6 | holder_late_window | m | deal unwound: unwind date / not unwound & effective<payoff: payoff date / effective date | payoff | 368.17 | backdated termination |
| P6 | holder_rate_premium | p | >45d: +0.02 / 21-45: +0.01 / 0 | +0.01 | 367.27 | release 21-45 days after effective |
| P6 | payoff_courtesy_tier | p | payoff >10d before: 20 / 4-10: 10 / 0 | 20 | 347.31 | unprocessed payoff report |
| P6 | tenure_goodwill_tier | p | >=36m: 15 / 24-35: 8 / 0 | 15 | 352.31 | long-held waiver |
| P7 credit | new_vehicle_bonus_tier | p, x purchase, multi | new & 0-30d: 500 / new >30d: 250 / 0 | 500 | 1342.36 (1842.36) | prompt new order |
| P7 | credit_age_rule | m | >=36m: credit x day share / 24-35: min(credit, price) / credit | min | 2247.36 | price below credit at 24-35 months |
| P7 | return_store_bonus_tier | p, x purchase, multi | same store & trade: 300 / same store: 150 / 0 | 300 | 1542.36 | same-store order |
| P7 | deductible_reimbursement_tier | p | collision & ded>cover: 250 / other & ded>cover: 150 / 0 | 250 | 1592.36 | deductible above the cover |
| P7 | replacement_price_tier | p, x purchase | >=40k: 200 / >=25k: 100 / 0 | 100 | 1742.36 | order >= 25k |
All-pairs (methods): every pair is distinguished by an input (P1 eff: payoff/recorded/signed dates; P1 share & P5 share: months/SoD/days; P2 window: unwind/signed/effective dates — the signed-date tier exists only where the effective date is the later recorded date; P4 plan timing: 0 / R-50 floored at R/2 / R (fee add-back and prompt-payment rate are parameters); P4 contract: 0 / R x ratio / R; P5 backdating: sale-date / order-date / none; P6 window: unwind/payoff/effective dates (unwound deals first, so the tiers are disjoint); P7 credit age: x share / min with price / credit). No pair differs only by a window length or a constant multiplier.
Independence: no factor's tier or method reads another factor's binding (P1's share reads the signed request date and the effective-date ladder adds or gives up the days between; P5's share reads the loan_payoff_date; the backdating ladder reads the order and the payoff; P6 premium reads the effective date, courtesy the payoff date, the window ladder compares them).

### Probe table (scratch probe.py on copies of each task world; result of the probed policy)
| policy | probe | result |
|---|---|---|
| holder_cancellation_refund | task-0 world | 549.84 |
| holder_cancellation_refund | EXACT TIE: signed and recorded 2026-08-21 -> 825 x 57/72 = 653.125 -> 653.13, refund 543.13 | 543.13 |
| holder_cancellation_refund | no request on file | 0.0 |
| holder_cancellation_refund | request declined (decoy status) | 0.0 |
| holder_cancellation_refund | payoff 2026-08-10 before signing (request still wins; payoff tier adds the days) | 556.16 |
| holder_cancellation_refund | request recorded same day (signed-date tier) | 554.58 |
| holder_cancellation_refund | VSC cancelled (decoy status) -> no recapture | 599.84 |
| holder_cancellation_refund | cancelled VSC listed before the active one (second record) | 549.84 |
| holder_cancellation_refund | deal unwound -> flat full price | 865.0 |
| holder_cancellation_refund | month-end: sale 2025-01-31, signed 2026-02-28 | 566.04 |
| lienholder_refund_release | task-0 world after confirmation | 579.84 |
| lienholder_refund_release | contract APR 0.00 -> standard 0.05 | 578.27 |
| lienholder_refund_release | contract APR 12.90 -> ceiling 0.09 | 580.56 |
| lienholder_refund_release | later declined request (decoy) ignored | 579.84 |
| lienholder_refund_release | no refund calculation (opening world) | 0.0 |
| lienholder_refund_release | payoff on file after the cancellation (C21: holder side) -> 0.00 here | 0.0 |
| lienholder_refund_release | unwound deal + deal_unwound reason -> window from unwind date 2026-08-01 | 581.55 |
| holder_refund_release | C21: cancelled Tucson waiver with payoff 2026-09-30 on file -> holder release prices it | 569.84 |
| balance_benefit | task-0 world (CR-V) | 2970.75 |
| balance_benefit | no claim line (absent record) | 0.0 |
| addon_overpayment_recovery | task-1 world | 402.64 |
| addon_overpayment_recovery | no paid GAP line (absent) | 0.0 |
| addon_overpayment_recovery | plan cancelled 2026-07-20, before the loss | 0.0 |
| addon_overpayment_recovery | plan refund paid to the holder (decoy payee) | 0.0 |
| addon_overpayment_recovery | plan cancelled for total_loss (no fee add-back) | 327.64 |
| addon_overpayment_recovery | contract also cancelled for customer_request (both fees added back) | 452.64 |
| addon_overpayment_recovery | no service contract (absent) | 0.0 |
| addon_overpayment_recovery | contract cancelled on the loss date (as received) | 385.46 |
| addon_overpayment_recovery | add-ons paid after the GAP payment (2026-09-20) | 417.64 |
| addon_overpayment_recovery | ZERO EDGE: plan refund 60.00, line credited so the excess is 50.00 (<= 60.00 floor) -> nothing reversed | 0.0 |
| addon_overpayment_recovery | ZERO EDGE: excess 61.00 just above the floor -> positive reversal | 91.26 |
| addon_overpayment_recovery | paid within 30 days of settlement (no late-payment interest) | 404.06 |
| addon_overpayment_recovery | paid 70 days after settlement (high late-payment rate) | 382.73 |
| payoff_termination_refund | task-1 world | 331.96 |
| payoff_termination_refund | no payoff date (absent) | 0.0 |
| payoff_termination_refund | submitted request on file (cancellation side, C1) | 0.0 |
| payoff_termination_refund | Civic deal unwound -> full price | 795.0 |
| payoff_termination_refund | order signed 2026-08-10 (39 days before payoff) | 328.33 |
| payoff_termination_refund | a later-charged closed deal (latest deal not contracted) | 278.33 |
| payoff_termination_refund | same-day vehicle-price charge on another deal recorded after (tie: first recorded kept) | 331.96 |
| payoff_termination_refund | Civic service contract cancelled -> no recapture | 371.96 |
| holder_refund_release | task-1 world after termination | 367.31 |
| holder_refund_release | opening world (no refund calculation) | 0.0 |
| holder_refund_release | contract APR 0.00 -> standard | 367.18 |
| holder_refund_release | effective = payoff (no backdating) -> window from the effective date | 367.31 |
| holder_refund_release | R2-F2 overlap world: deal unwound and backdated termination -> unwind tier only | 467.21 |
| replacement_credit | task-1 world after reversal (set-off 402.64) | 1842.36 |
| replacement_credit | no paid GAP line (absent) | 0.0 |
| replacement_credit | latest-charged deal not contracted (out of scope -> flat credit) | 1500.0 |
| replacement_credit | order at another store | 1945.0 |
| replacement_credit | order signed before the GAP payment (2026-08-30) | 1745.0 |
| replacement_credit | earlier paid credit line 500.00 on the claim | 1745.0 |

Tie rules stated: "most recent" lines and the latest vehicle-price charge keep the first-recorded row on a same-day tie (stated in P5/P6/P7 rules for the order); month counts use whole calendar months with no month-end adjustment (stated in P1/P3/P5/P6/P7).

### Defining-sentence table (recipe A4: each rule sentence -> baseline / the single factor that uses it / plain shared binding / scope)
| policy | sentence | used by |
|---|---|---|
| holder_cancellation_refund | This policy prices the cancellation refund booked when the holder confirms the submitted signed cancellation r… | scope / partition / convention (no binding) |
| holder_cancellation_refund | An active waiver that carries a submitted signed cancellation request recorded for it ends by the holder's can… | scope / partition / convention (no binding) |
| holder_cancellation_refund | The cancellation refund starts from the waiver's retail_price. | baseline |
| holder_cancellation_refund | The effective date of the cancellation is the request date the holder signed on the request recorded for the w… | baseline; plain bindings signed_date |
| holder_cancellation_refund | A waiver with no submitted signed cancellation request on file is not cancelled under this policy, and its can… | baseline; plain bindings request_on_file |
| holder_cancellation_refund | A cancellation whose effective date falls within free_look_days calendar days after the sale date, or whose pu… | baseline; plain bindings deal_status, flat_refund |
| holder_cancellation_refund | Otherwise the cancellation refund is the retail_price times the unused share, which is calendar days from the … | baseline; plain bindings term_days, unused_days |
| holder_cancellation_refund | A cancellation refund below 0.00 is 0.00. | baseline |
| holder_cancellation_refund | For a holder's cancellation priced under this policy, and only for such a cancellation, the effective date is … | overwrite replaced_by |
| holder_cancellation_refund | For a holder's cancellation priced under this policy, and only for such a cancellation, the refund is assemble… | overwrite replaced_by |
| holder_cancellation_refund | The cancellation refund is assembled in this order: any reduction of the price that a ladder of this rule make… | plain bindings result, shared_refund |
| holder_cancellation_refund | The waiver's months in force are whole calendar months from sale_date to the request date the holder signed. | scope / partition / convention (no binding) |
| holder_cancellation_refund | In counting a cancelled waiver's whole calendar months, both the months it was in force and its unused months,… | scope / partition / convention (no binding) |
| holder_cancellation_refund | For an active waiver that carries a submitted signed cancellation request, and only for such a waiver, the hol… | overwrite replaced_by |
| holder_cancellation_refund | Effective-date ladder for a cancellation: where the lienholder's reported loan payoff date is earlier than the… | factor eff_date_rule |
| holder_cancellation_refund | Share ladder for a cancellation: where the contract term is 72 months or longer and the waiver has been in for… | factor share_convention |
| holder_cancellation_refund | Cancellation-charge ladder: where the waiver has been in force 24 or more months and the request states the re… | factor cancel_charge_tier |
| holder_cancellation_refund | Administrator-portion ladder: where the waiver's purchase deal is a New Vehicle Retail Purchase or a New Vehic… | factor admin_portion_tier |
| holder_cancellation_refund | Early-cancellation ladder: where the waiver has been in force fewer than 12 months, the early cancellation cha… | factor early_charge_tier |
| holder_cancellation_refund | Bundle-recapture ladder: where a Kessler Shield service contract sold on the same purchase deal is in active s… | factor bundle_recapture_tier |
| lienholder_refund_release | This policy prices the release of a cancellation refund to the lienholder while the waiver's loan is still ope… | scope / partition / convention (no binding) |
| lienholder_refund_release | A refund computed on a waiver whose loan_payoff_date is empty is released to the lienholder; a refund computed… | plain bindings payee_lienholder |
| lienholder_refund_release | A lienholder refund release is made only after the waiver stands cancelled with a refund calculation entry for… | prerequisite sentence |
| lienholder_refund_release | A lienholder refund release is not made until no other waiver of the same holder financed by the same lienhold… | prerequisite sentence |
| lienholder_refund_release | The lienholder release pays the refund due, which is the amount of the refund calculation entry on the waiver'… | baseline; plain bindings refund_due |
| lienholder_refund_release | The effective date of the cancellation is the waiver's closing date, or the release date where the waiver carr… | baseline; plain bindings effective_date |
| lienholder_refund_release | The late window of a lienholder release starts on the effective date of the cancellation. | baseline |
| lienholder_refund_release | Where the release is made more than refund_payment_days calendar days after the late window starts, late-relea… | baseline; plain bindings late_days |
| lienholder_refund_release | The lienholder release amount is the refund due plus the late-release interest, rounded half up to the cent. | baseline |
| lienholder_refund_release | A lienholder release is not made for a refund due of 0.00. | baseline |
| lienholder_refund_release | For a cancellation refund released to the lienholder under this policy, and only for such a release, the relea… | overwrite replaced_by |
| lienholder_refund_release | The signed request a lienholder release reads is the waiver's completed cancellation request, and a contract A… | factor release_late_window, release_rate_source; plain bindings recorded_stamp |
| lienholder_refund_release | Late-rate ladder for a lienholder release: where the waiver's purchase deal carries a contract APR above apr_c… | factor release_rate_source |
| lienholder_refund_release | Late-window ladder for a lienholder release: where the signed request states the reason deal_unwound and the w… | factor release_late_window |
| lienholder_refund_release | Rate-premium ladder for a lienholder release: where the release is made more than 60 calendar days after the e… | factor release_rate_premium |
| lienholder_refund_release | Courtesy-credit ladder for a lienholder release: where the signed request was recorded more than refund_paymen… | factor release_courtesy_credit |
| lienholder_refund_release | The lienholder release is assembled in this order: the late-release interest is the refund due times the yearl… | plain bindings late_interest, result |
| balance_benefit | This policy prices the GAP balance line paid on a total-loss claim under an active waiver; the replacement veh… | scope / partition / convention (no binding) |
| balance_benefit | The claim figures are those recorded on the waiver's most recent claim line for the GAP balance, whether that … | scope / partition / convention (no binding) |
| balance_benefit | The loss type and the loss date the ladders of this rule read are those recorded on the same claim line. | plain bindings loss_date, loss_type |
| balance_benefit | For a GAP balance line priced under this policy, and only for such a line, negative equity carried into the de… | overwrite replaced_by; plain bindings negative_equity |
| balance_benefit | A waiver with no claim line for the GAP balance on file has no claim figures, and its GAP balance line is 0.00… | baseline; plain bindings claim_on_file |
| balance_benefit | For a GAP balance line priced under this policy, and only for such a line, the refunds of cancelled financed p… | overwrite replaced_by |
| balance_benefit | The GAP balance starts from the payoff at loss less the ACV settlement. | baseline; plain bindings acv, payoff |
| balance_benefit | The insurer's deductible above deductible_covered_cap_usd is subtracted. | baseline; plain bindings deductible |
| balance_benefit | Past-due payments, late fees and charges, deferred payments, add-on refunds, negative trade equity carried int… | baseline; plain bindings addon_refunds, salvage |
| balance_benefit | Financing above the loan-to-value cap, ltv_cap_pct times the waiver's vehicle_value_basis rounded half up to t… | baseline |
| balance_benefit | The GAP balance benefit is that result rounded half up to the cent, floored at 0.00 and capped at the lesser o… | baseline; plain bindings benefit_cap, result |
| balance_benefit | For a GAP balance line priced under this policy, and only for such a line, the insurer's deductible is covered… | overwrite replaced_by; plain bindings deductible_excess |
| balance_benefit | For a GAP balance line priced under this policy, and only for such a line, the payoff items the waiver exclude… | overwrite replaced_by; plain bindings late_cut, other_cuts, past_due_cut |
| balance_benefit | For a GAP balance line priced under this policy, and only for such a line, the loan-to-value cap amount is ltv… | overwrite replaced_by; plain bindings after_ltv, cap_amount |
| balance_benefit | The waiver's months in force at the loss are whole calendar months from sale_date to the loss date. | scope / partition / convention (no binding) |
| balance_benefit | In counting the months a GAP waiver was in force at its loss, a whole calendar month counts each time the star… | scope / partition / convention (no binding) |
| balance_benefit | Deductible ladder: where the loss is a total_loss_theft and the waiver had been in force 12 or more months at … | factor deductible_cover_tier |
| balance_benefit | Past-due allowance ladder: where the waiver had been in force 24 or more months at the loss, the past-due allo… | factor past_due_allowance_tier; plain bindings past_due |
| balance_benefit | Late-charge allowance ladder: where the loss is a total_loss_theft, the late-charge allowance is late_allow_th… | factor late_charge_allowance_tier; plain bindings late_fees |
| balance_benefit | Deferral ladder: where the loss is a total_loss_theft, deferred payments are not subtracted; where the loss is… | factor deferral_treatment; plain bindings deferred |
| balance_benefit | Cap-basis ladder: where the purchase deal is a Used Vehicle Retail Purchase or a Value Line Used Vehicle Purch… | factor cap_basis_tier |
| balance_benefit | Loan-to-value ladder: reading the recorded cap amount, ltv_cap_pct times the waiver's vehicle_value_basis roun… | factor ltv_reduction_tier |
| balance_benefit | The GAP balance line is assembled in this order: the substitutions above replace the standard figures first, t… | plain bindings gap_before_ltv |
| addon_overpayment_recovery | This policy prices the reversal of the overpaid part of a paid GAP balance line whose holder's Kessler Shield … | scope / partition / convention (no binding) |
| addon_overpayment_recovery | The paid line is the waiver's most recent paid GAP balance line, with its amount paid, its loss date, the date… | baseline; plain bindings claim_no, line_credited, line_loss_date, line_paid, line_paid_date |
| addon_overpayment_recovery | The add-on refunds received are the refunds of a Kessler Shield service contract and of a Kessler Care mainten… | baseline; plain bindings contract_id, contract_refund, plan_id, plan_refund |
| addon_overpayment_recovery | The uncredited add-on refund is the add-on refunds received less the add-on refunds recorded on the paid line,… | baseline; plain bindings uncredited |
| addon_overpayment_recovery | The overpayment is the uncredited add-on refund, never more than the benefits standing on the claim, the amoun… | baseline; plain bindings claim_standing, overpayment |
| addon_overpayment_recovery | The add-on overpayment reversal is the overpayment rounded half up to the cent. | baseline |
| addon_overpayment_recovery | A waiver with no paid GAP balance line on file has no add-on overpayment reversal. | baseline; plain bindings line_on_file |
| addon_overpayment_recovery | Where the paid line paid no more than recovery_floor_usd, or the refunds of a Kessler Shield service contract … | baseline; plain bindings floor_excess |
| addon_overpayment_recovery | For a paid GAP balance line reversed under this policy, and only for such a line, the benefit is paid in error… | overwrite replaced_by |
| addon_overpayment_recovery | For a paid GAP balance line reversed under this policy, and only for such a line, the reversal is one gap_bene… | overwrite replaced_by |
| addon_overpayment_recovery | Plan timing ladder for an overpayment reversal: where the plan's cancellation took effect before the loss date… | factor plan_timing_count; plain bindings plan_closed |
| addon_overpayment_recovery | Contract restatement ladder for an overpayment reversal: where the service contract's cancellation took effect… | factor contract_restatement; plain bindings contract_closed |
| addon_overpayment_recovery | Fee add-back ladder for an overpayment reversal: where both the plan and the service contract were cancelled o… | factor fee_addback_tier |
| addon_overpayment_recovery | Prompt-payment interest ladder for an overpayment reversal: where the paid line was paid more than twice claim… | factor prompt_pay_rate_tier |
| addon_overpayment_recovery | Stale-payoff waiver ladder for an overpayment reversal: reading, for each add-on cancelled on or after the los… | factor stale_payoff_tier |
| addon_overpayment_recovery | The add-on overpayment reversal is assembled in this order: each product's refund is counted as the ladders of… | plain bindings result |
| payoff_termination_refund | This policy prices the termination refund booked when an active waiver whose loan the lienholder has reported … | scope / partition / convention (no binding) |
| payoff_termination_refund | An active waiver that carries a submitted signed cancellation request recorded for it ends by the holder's can… | scope / partition / convention (no binding) |
| payoff_termination_refund | The termination refund starts from the waiver's retail_price. | baseline |
| payoff_termination_refund | The effective date of the termination is the waiver's loan_payoff_date. | baseline; plain bindings payoff_date |
| payoff_termination_refund | The termination refund is the retail_price times the unused termination share, which is calendar days from the… | baseline; plain bindings term_days, unused_days |
| payoff_termination_refund | Where deal_unwind_flat_cancel is true, a waiver whose purchase deal has been unwound is refunded its full reta… | baseline; plain bindings deal_unwound |
| payoff_termination_refund | A termination refund below 0.00 is 0.00. | baseline |
| payoff_termination_refund | A waiver with no loan_payoff_date on file, or one carrying a submitted signed cancellation request, is not ter… | baseline; plain bindings in_scope |
| payoff_termination_refund | For a termination priced under this policy, and only for such a termination, the waiver is terminated and its … | overwrite replaced_by |
| payoff_termination_refund | For a termination priced under this policy, and only for such a termination, the termination refund is assembl… | overwrite replaced_by |
| payoff_termination_refund | The termination's months in force are whole calendar months from sale_date to the loan_payoff_date. | factor termination_charge_tier |
| payoff_termination_refund | In counting a terminated waiver's months, a whole calendar month counts each time the start date's day of the … | scope / partition / convention (no binding) |
| payoff_termination_refund | The holder's replacement purchase is the holder's most recently signed group purchase deal, the deal whose veh… | plain bindings repl_contracted, repl_id, repl_trade |
| payoff_termination_refund | Termination share ladder: where the contract term is 72 months or longer, the unused termination share is whol… | factor termination_share_rule |
| payoff_termination_refund | Backdating ladder for a termination: where the loan_payoff_date falls within free_look_days calendar days afte… | factor termination_backdating |
| payoff_termination_refund | Termination-charge ladder: where cancellation_fee_waived_on_payoff is false and the termination's months in fo… | factor termination_charge_tier |
| payoff_termination_refund | Termination administrator-portion ladder: where the waiver's purchase deal is a New Vehicle Retail Purchase or… | factor termination_admin_tier |
| payoff_termination_refund | Trade-in credit ladder for a termination: where the holder's replacement purchase carries a trade-in and is a … | factor trade_in_credit_tier |
| payoff_termination_refund | Termination bundle-recapture ladder: where a Kessler Shield service contract sold on the waiver's purchase dea… | factor termination_bundle_tier |
| payoff_termination_refund | The termination refund is assembled in this order: any reduction of the price that a ladder of this rule makes… | plain bindings result, shared_refund |
| holder_refund_release | This policy prices every release of a refund to the holder, a termination refund or a cancellation refund, onc… | scope / partition / convention (no binding) |
| holder_refund_release | A refund computed on a waiver whose loan_payoff_date is empty is released to the lienholder; a refund computed… | plain bindings payee_holder |
| holder_refund_release | A termination refund is not released to the holder until the waiver stands terminated with a refund calculatio… | prerequisite sentence |
| holder_refund_release | The holder release pays the refund due, which is the amount of the refund calculation entry on the waiver's le… | baseline; plain bindings refund_due |
| holder_refund_release | The effective date of the waiver's ending, by termination or by cancellation, is the waiver's closing date, or… | baseline; plain bindings effective_date |
| holder_refund_release | The late window of a holder release starts on the effective date of the waiver's ending. | baseline |
| holder_refund_release | Where the holder release is made more than refund_payment_days calendar days after the late window starts, hol… | baseline; plain bindings late_days |
| holder_refund_release | The holder release amount is the refund due plus the holder late interest, rounded half up to the cent. | baseline |
| holder_refund_release | A holder release is not made for a refund due of 0.00. | baseline |
| holder_refund_release | For a refund released to the holder under this policy, and only for such a release, the release is one payment… | overwrite replaced_by |
| holder_refund_release | The holder's tenure is whole calendar months from sale_date to the effective date of the waiver's ending; a wh… | factor tenure_goodwill_tier |
| holder_refund_release | A contract APR read by a holder release is a yearly rate, the printed APR divided by 100. | factor holder_rate_source |
| holder_refund_release | Holder late-rate ladder: where the waiver's purchase deal carries a contract APR above holder_rate_ceiling, th… | factor holder_rate_source |
| holder_refund_release | Holder late-window ladder: where the waiver's purchase deal stands unwound, the late window starts on that dea… | factor holder_late_window; plain bindings payoff_date |
| holder_refund_release | Holder rate-premium ladder: where the holder release is made more than 45 calendar days after the effective da… | factor holder_rate_premium |
| holder_refund_release | Payoff courtesy ladder: where the loan_payoff_date is more than 10 calendar days before the release date, hold… | factor payoff_courtesy_tier |
| holder_refund_release | Tenure goodwill ladder: where the holder's tenure is 36 months or more, holder_goodwill_three_years is added t… | factor tenure_goodwill_tier |
| holder_refund_release | The holder release is assembled in this order: the holder late interest is the refund due times the yearly int… | plain bindings holder_interest, result |
| replacement_credit | This policy prices the replacement vehicle credit the holder applies to a replacement purchase that stands in … | scope / partition / convention (no binding) |
| replacement_credit | A replacement vehicle credit is fixed only after the claim's paid GAP balance line carries a reversal entry wh… | prerequisite sentence |
| replacement_credit | A replacement vehicle credit is not applied until every other waiver of the holder whose loan was reported pai… | prerequisite sentence |
| replacement_credit | The paid line is the waiver's most recent paid GAP balance line. | baseline |
| replacement_credit | A waiver whose replacement_vehicle_credit_usd is 0.00 receives no replacement vehicle credit. | baseline |
| replacement_credit | The replacement vehicle credit starts from replacement_vehicle_credit_usd. | baseline |
| replacement_credit | The overpayment set-off is the total of the benefit reversal entries on the waiver's ledger. | baseline; plain bindings setoff |
| replacement_credit | The credit already given is the total of the amounts on the waiver's replacement vehicle credit lines, a denie… | baseline; plain bindings credit_given |
| replacement_credit | The replacement vehicle credit is the starting credit less the overpayment set-off and less the credit already… | baseline |
| replacement_credit | A waiver with no paid GAP balance line on file receives no replacement vehicle credit. | baseline; plain bindings line_on_file |
| replacement_credit | For a replacement vehicle credit applied under this policy, and only for such a credit, a holder whose GAP bal… | overwrite replaced_by |
| replacement_credit | The replacement purchase is the holder's most recently signed group purchase deal, the deal whose vehicle pric… | plain bindings repl_id, repl_type |
| replacement_credit | The credit loss-age is whole calendar months from sale_date to the loss date of the paid line; a whole calenda… | factor credit_age_rule |
| replacement_credit | New-vehicle bonus ladder for a replacement credit: where the replacement purchase is a New Vehicle Retail Purc… | factor new_vehicle_bonus_tier |
| replacement_credit | Credit-age ladder: where the credit loss-age is 36 months or more, the starting credit is replacement_vehicle_… | factor credit_age_rule |
| replacement_credit | Return-store bonus ladder: where the replacement purchase is at the store that sold the waiver's purchase deal… | factor return_store_bonus_tier |
| replacement_credit | Deductible reimbursement ladder: reading the loss type and the insurer's deductible on the waiver's most recen… | factor deductible_reimbursement_tier |
| replacement_credit | Replacement-price bonus ladder: where the replacement purchase's cash_price is price_high_usd or more, price_b… | factor replacement_price_tier |
| replacement_credit | The replacement vehicle credit is assembled in this order: any starting credit a ladder of this rule substitut… | plain bindings result |

Notes: P1 "The waiver's months in force ..." and the five month-count convention sentences define the shared whole-month count read inline by several factors (share, charges, allowances); scope sentences and the record-partition sentence bind no compute binding.

### Round 3 additions
- Payee partition (C21), verbatim in P2 and P6: "A refund computed on a waiver whose loan_payoff_date is empty is released to the lienholder; a refund computed on a waiver whose loan_payoff_date is on file, whether a termination refund or a cancellation refund, is released to the holder." P6 owns every holder release (termination or cancellation refund); release_refund_lienholder refuses a waiver with a payoff date, release_refund_holder one without.
- Zero-amount waits: P2 waits on the other waiver's most recent GAP balance line being a run theft-waiting-period denial (a later denial or the payment, which may be 0.00 and is accepted, releases it); P7 waits on a reversal only where the paid line paid more than 60.00 and the counted refunds exceed the recorded add-on refunds by more than 60.00, and P4 reverses nothing at or under recovery_floor_usd 60.00, so the reversal it waits on is always positive; P6's wait on a terminated waiver is met by a termination of any amount (0.00 accepted); P7's second wait (no refund due) is met by the termination alone when its refund is 0.00.
- Rounding: every money RND is RND(x + 0.000000001, 2) (round 4; was 0.000001 in round 3) on a non-negative amount (MX inside where a difference could go negative; P1's adjustment is a non-negative credit minus a non-negative give-up); exact-tie probe in the table (653.125 -> 653.13).
- Exact one anchor per quantity: P1's share counts from the signed request date in rule, ladder and compute; P5's from the loan_payoff_date.

### Round 4 additions
- Shared selections (XF2, R3-F1 class): every record selection read by more than one binding is now a plain binding stated once — P4 contract_closed (the RAV4 service contract's cancellation date, read by contract restatement, fee add-back, stale-payoff and the de-minimis floor); P3 negative_equity reads the deal's trade figures through the loan-to-value factor's ltv_trade_payoff / ltv_trade_allowance bindings and deferral_cut reads the plain loss_type (deferred payments moved into the deferral factor's bindings). A scan of every compute binding finds no selection read twice.
- Rounding: tool bodies use exact Decimal half-up (_GapRecords.cents); every RND argument on both worlds (gold, all-baseline and factor-sensitivity evaluations, 121 calls) sits at least 0.000238 from a half cent, so the 1e-9 epsilon never moves a figure.
- Zero amounts: no floor creates an amount where nothing is owed (P4 reverses nothing at or under recovery_floor_usd; the half-of-overpayment floor applies only to a positive overpayment); every wait on a write that can be 0.00 is either met by a 0.00 write the tool accepts (cancellation, termination, GAP balance) or carved out by the 60.00 record test (P7 on the reversal).

### Round 5 additions (render scan render_r1)
- Combination order (recipe A3): every overwrite replaced_by and every assembly sentence is generic — no factor quantity is named; each policy states its order once (P1, P2, P4, P5, P6, P7 assembly sentences rewritten; P3's closing order sentence was already generic; its three overwrites now refer to 'the ladders of this rule').
- Single-factor quantities (recipe A4): moved into their factor's text and bindings — P1 unused months and the share branches (share_method folded into the share factor's unused_share), recorded stamp, request reason; P2 signed date; P3 settlement date, recorded cap amount, loss type/date stated as a shared ladder input; P4 settlement date and the late-payment interest (now in the prompt-payment ladder sentence and bindings); P5 term months; P7 paid date and loss date. Baseline quantities kept plain: P3 negative trade equity (now read from the claim line under a declared scoped overwrite of gap_combo_addon_products, so the loan-to-value factor's deal trade reads are its own). (Round 6: P3 deferred payments are again the deferral factor's own evidence — see the round-6 note.)
- Edges: P7 0.00-credit tiers guarded (A1); P7 loss date = the paid line's (A2); P1 month convention covers unused months (A3); P3 LTV ladder on the recorded (rounded) cap amount (A4); P4 stale-payoff reads each add-on's last lienholder refund payment and the earlier of those (A5); P2 courtesy tier for no completed request (A6); P4 fee-add-back framing clause removed (B1); P4 baseline params / cross reads corrected (E1, E2).
- Values: no gold, baseline or sensitivity figure moved (verified on both worlds); 119 RND arguments, minimum distance from a half cent 0.000238.

### Round 6 additions (audit revision_5, R5-F1)
- P3 deferral ladder reads the loss type of the waiver's most recent GAP balance line (the shared plain loss_type), as the rule states and as the deductible and late-charge ladders do; the round-5 'any theft line ever' COUNT is gone. The deferral factor's own evidence is the deferred-payments read (consumed only through the deferral treatment; the baseline's 'subtracted in full where the switch is true' is that factor's fall-through). Decoy probe (task-0 world plus a later GAP balance line reclassified total_loss_collision): 2153.71, the rule's figure.
- Class sweep: every COUNT / SUM / EXISTS / XSUM / LATEST read in the seven policies checked against its rule wording (records on file / total of entries / most recent line); no other 'any line ever' vs 'most recent line' mismatch.
- Values: no gold, baseline or sensitivity figure moved.

### Round 7 additions (audit revision_6, R6-F1)
- P3 deferred payments are a plain binding the standard calculation states ("... deferred payments ... are each subtracted in full where the waiver's switch for that item is true"); the deferral factor owns only deferral_cut and varies how they are treated. Its own record evidence is the months in force at the loss: theft -> not subtracted; collision with the waiver in force 12 or more months at the loss -> only the part above deferral_allowance; any other case (other loss types, a collision in the first 12 months) -> in full (= the baseline). Disjoint as stated; T1 on task 0 unchanged (theft tier; baseline 2398.71); T2: a seasoned collision loss with deferred payments above the allowance. No figure moved.

### Round 8 additions (render scan render_r2, N1)
- P4 fee add-back ladder now states both conditions compute applies: each add-on's reason is read from its completed cancellation request (the plan's too, no longer from its refund-paid ledger row) and only an add-on whose refund was paid to the lienholder is counted. Sweep of every factor's decides binding for gates on other bindings (plan_refund, contract_refund, repl_type, payee/scope tests): the plan-timing and contract-restatement gates are the rule's own "refunds received ... paid to the lienholder", the trade-in and new-vehicle gates are the rule's "replacement purchase ... in contracted status"; no other unstated gate. No figure moved.

### Round 9 (KB audit revision_1, seed-only S1)
- Seeded Kessler Care refund on KC-5308126 re-priced from the published retail cancellation rules: financed, so pro rata 664.05 x 6/8 = 498.04, less the plan's 75.00 cancellation fee (no vehicle-price charge in the 3 months before 2026-08-06), less bundle recapture 0.40 x 34.95 = 13.98 (28 whole months in force), no owner-rewards credit -> 409.06 (was 339.15) on the calc and lienholder-paid rows. Every other seeded maintenance/vsc row in both worlds re-priced and unchanged (see worklog round 9).
- Forced gold: reversal 332.73 -> 402.64; credit 1912.27 -> 1842.36; factor table, task-1 world rows and the affected probes above re-derived (each plan-refund-counting probe moves by +69.91; credit probes outside the reversal world unchanged). Charter and tools byte-identical.
