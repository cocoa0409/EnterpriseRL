# Render source notes — card (Crestline Credit Card), env_0062

Source: env/env_0062_tire_and_auto_service_chain/tasks/credit_card_promotions/card.extended.yaml + task_tools.py
Profile: extended. Base text carried verbatim; every item below is reported, not rendered around.

## Source mismatches (extended policies)

### M1 (HIGH) card_ext_payment_direction — baseline.rule contradicts the compute
baseline.rule: "The part directed is the whole of today's payments, never more than the named plan's recorded balance, rounded half up to the cent."
The compute with every factor at its baseline gives `min(t_left, available)` where
`available = MX(0, pay_today - unpaid - fees_owed - charges)` — non-factor bindings stated in the rule
("Today's payments first cover the latest statement's minimum still unpaid ..., then the fees charged for that statement and still owed, ..., and then the deferred interest ...; what is left is the amount available to direct.").
So the "whole of today's payments" is not the no-factor result. Both sentences are carried in the computation document, which therefore reads self-contradictory until the source is fixed.

### M2 (MED) card_ext_payment_direction — "the plan whose period ends last" vs compute
Rule: "may direct it ... to the deferred-interest plan whose period ends last on the account".
Compute `t_plan` picks deferred_18 if not yet ended, else deferred_12, else deferred_6 — by plan length, not by the latest end date. A recent 12-month purchase can end after an older 18-month purchase; the compute then still names the 18-month plan.

### M3 (LOW) card_ext_payment_direction — "lowered by the releases" leaves the operation open
Rule: "The holds (the returned-payment hold plus the channel hold, never above one) are lowered by the releases (the tenure release plus the relationship release, never above one)".
Compute: `net_hold = MN(1, hold + channel_hold) * (1 - MN(1, tenure_release + relationship_release))` (proportional), whereas "lowered by" also reads as subtraction. Rendered with the verbatim words plus the proportional reading the compute pins; please make the rule say it.

### M4 (MED) card_ext_statement_minimum_payment — below-floor branch vs payments since closing
Rule: "when the new balance is below the payment floor, the minimum is the whole new balance and nothing is added to it or taken off it".
Compute result: `st_nb - paid_since` (floored at 0) in that branch — the payments made toward the statement since it closed ARE taken off. Carried verbatim; the sentence and the compute disagree on whether payments come off.

### M5 (MED) card_ext_statement_minimum_payment — reversal "otherwise" branch undefined vs compute
Rule: "when it reverses a fee posted in an earlier cycle, the reversed amount is taken off the past-due amount, never more than that amount; otherwise nothing is taken off for reversals."
Compute `rev_off`: any reversal posted since closing that is not against the cycle's late fee takes `MN(r_amt, past_due)` — it never checks that the reversed fee was posted in an earlier cycle (e.g. a reversal of a returned payment fee posted in the current cycle, or of a late fee posted after closing, is taken off the past-due amount by the compute but "nothing" by the rule).

### M6 (LOW) card_ext_statement_minimum_payment — past-due floor not stated
Rule: "The past-due amount is that earlier statement's minimum less the payments made toward it and not returned" — compute `past_due = MX(0, missed_min - paid_toward_missed)`; the zero floor is not in the rule.

### M7 (LOW) card_ext_deferred_interest_assessment — reallocation cap in the second branch
Rule: "when such another plan's period did end in between, only the part of that total beyond that other plan's recorded balance counts" — compute `realloc_amt = MN(MX(0, m_tot - o6_rem - o12_rem), MX(0, ledger_left))` also caps this branch at the plan's recorded balance; the rule states the cap only for the first branch. (Also: only deferred_6/deferred_12 are checked as the in-between plan, `o18` is never computed.)

### M8 (MED, all five policies) assembly sentences naming several factor quantities
Each `result`/combination sentence names factor quantities, so it cannot sit in the computation document without telling a reader the factors exist:
- courtesy fee: "The combined share is the history share plus every bonus, and a combined share above share_full is share_full." / "The courtesy credit is the part credited outright plus the combined share of the credit basis, rounded half up to the cent once, on the final figure."
- returned fee: "The returned-fee combined share is the return-history share plus every bonus of this schedule, and a returned-fee combined share above rpf_share_full is rpf_share_full." / "The returned-fee courtesy credit is the part credited outright plus the returned-fee combined share of its credit basis, rounded half up to the cent once, on the final figure."
- minimum payment: "Above the floor test, the minimum is the core plus the installment part, plus the past-due amount, plus the late fee posted in the statement's cycle, less what is taken off for disputes and for reversals and less the payments made toward the statement since it closed, never less than zero, rounded half up to the cent."
- deferred interest: "The assessment is the recorded accruals plus the stub accrual, plus the interest added for a returned payment's allocation, less the interest taken off for a ticket refund and for the window reallocation, rounded half up to the cent once, on the final figure; it is zero when the corrected balance (the recorded balance plus the returned payment's allocation, less the ticket refund and the reallocated amount) is not above zero."
- payment direction: "The holds (...) are lowered by the releases (...); the part directed is what reaches the named plan less that net held share, never more than the named plan's recorded balance, rounded half up to the cent once, on the final figure."
Rendering applied: the computation document states baseline.rule plus the non-factor sentences that name no factor quantity, and the rounding-once rule; each factor document states how its own quantity enters the figure (added to / taken off / applied to), the caps "never above one" / "share_full" in the docs whose quantities they bound. Please restate these sentences so the assembly reads in baseline terms.

### M9 (LOW) non-factor bindings that only factors use
Forced by the gate into the computation document's `covers`, but their sentences sit in the factor documents that use them (stating them in the computation document would announce the factors):
- deferred interest: `daily_rate`, `stub_days`, `realloc_int` (the whole interest effect of the window reallocation sits outside the declared factor, whose bindings stop at `realloc_amt`), `corrected_left`.
- minimum payment: `ep_plans/ep_rate/ep_id/ep_amt/ep_ticket/ep_at_stmt/ep_mrate/ep_fixed` (equal-payment balance and fixed payment, used only by the core and installment tiers).
- courtesy fee: `fee_stmt` (used only by the fee-weight tier).

### M10 (MED) overwrites that retire text still in force
- card_evt_statement: superseded_clause = the whole minimum-payment sentence, but replaced_by says "a printed statement minimum in every other use remains under the statement rule" — the retired clause stays in force for every printed statement (and the late-fee cap reads it). The KB must mark it "no longer in force".
- card_evt_payment_allocation: superseded_clause "Second, a cardholder may instruct that amounts above the minimum go to a particular deferred-interest plan; the instruction is the cardholder's own request and applies from the next payment that posts after it is submitted." — replaced_by keeps "every other instruction still applies from the next payment that posts after it is submitted" and drops "the instruction is the cardholder's own request" (still-in-force part not restated).

### M11 (LOW) tool docstrings claiming effects the body lacks
apply_courtesy_fee_credit_68b22b43, credit_returned_payment_fee_d3814d72, assess_deferred_interest_7b31b265, pay_statement_minimum_b2a1a039 each claim "the account's current balance falls/rises by that amount" and (three of them) "appears on the cardholder's next statement"; the bodies only insert one ledger row and never update the account's balance field (db_schema calls it "identically the sum of the card_balance account deltas", so this holds only if the balance is read as derived).

### M12 (LOW) gate-forced rendering of float-noise constants
`half_up_nudge` (1e-07, all five) and `round_tolerance` (1e-06, minimum payment) are required quantitative keys; they are rendered as the rounding tolerance they implement.

## Base known issues (base text frozen, logged only)
- card_evt_statement formula `pct_minimum` omits the whole-dollar round-up the rule states.
- card_evt_returned_payment formula `fee` omits the cap "never exceeding the minimum payment due on the most recent statement".

### M13 (LOW) scope / replaced_by sentences that enumerate factor evidence, homed in hubs
- card_ext_statement_minimum_payment: "this schedule figures that minimum for an account on which at most one fee reversal has posted since the statement closed and at most one billing-error dispute is open" (names the evidence of two factors).
- card_ext_deferred_interest_assessment: "on which no payment returned unpaid before the most recent returned payment carried an allocation to the plan" and replaced_by "the plan's balance as the allocation, returned-payment and refund rules here correct it" (names three corrections — a component inventory in prose).
- card_ext_payment_direction: "on which at most one payment made toward the latest statement was returned unpaid".
These are carried verbatim in the hubs (they define the policy's scope); wherever they sit they hint at the factors.

## Rendering record
- Output: env/env_0062_tire_and_auto_service_chain/docs/card/ — 57 documents: 9 facets, 14 base policy docs, 5 hubs (each the invocation doc of its exclusive tool; two user-owned tools worded "the customer themselves"), 5 computation docs, 24 factor docs (one per declared factor).
- Retired clauses registered: card_evt_statement (1), card_evt_payment_allocation (1), card_evt_deferred_interest (1), card_evt_fee_reversal (2), each marked "no longer in force" without restating the new basis.
- Prerequisite sentences: carried verbatim in the hubs of card_ext_statement_minimum_payment (1) and card_ext_payment_direction (2), each with one same-form (state) restatement; no resolving tool, action or route named.
- Cross-difficulty factor docs name: Road Hazard Protection, Alignment Services & Plans, Battery Replacement Warranties, Tire Sets & Treadwear Limited Warranty.

## round 2
Source re-fingerprinted: card.extended.yaml sha256 b47db353…7e2c, task_tools.py 6601bbf7…faf2a (both changed). All 34 extended-policy docs re-rendered or patched; base docs unchanged except one example row.
Closed:
- KB audit E1: the card_evt_statement overwrite's replacement text (printed minimum + "the desk takes on the latest statement ... except ... 36-month or 48-month ... more than one 24-month plan") now sits in the hub `statement_minimum_payment_at_the_care_desk_8b75a7a1`; the computation document `care_desk_minimum_payment_figure_f48cacb9` carries only the baseline rule, definitions and the source's generic assembly sentence.
- M1–M8, M10–M13 are fixed in the source, and the KB now follows the new text: baseline rules restated, below-floor rule, past-due floor, the "another fee posted on or before the closing date" reversal branch, the longer-plan tie rule, the multiplicative hold/release wording, the 18-month in-between plan with the cap, generic assembly sentences, scope sentences moved into their factors' documents, docstrings no longer claim balance effects, and the nudge/tolerance constants removed.
- New factor bindings reflected in the docs' covers: fee_stmt, fee_ref, ep_rate/ep_mrate/ep_fixed, r_fdate, p_start, refund_bal, void_bal, o18_rem, realloc_int, q*_id/t_exp/w18_rem.
- Example figures re-checked against the audit's scored values; changed: late_fee_terms row 35.00 → 33.00, desk worked figure past-due 38.00 → 43.00, reversal example 41.00 → 29.00, channel-hold example 300.00 → 260.00, share example 0.9 → 0.95.
Remaining source mismatches (low):
- R1: these bindings are still outside every factor but only factors use them, so they are defined in the factor documents that use them and the computation documents claim them only in meta: `ep_at_stmt` (equal-payment balance at closing; read by both the core and installment rules) and deferred interest `daily_rate`/`stub_days` (the definitions sentence "the daily rate is ... and the stub days are ..."). If the computation document stated them, it would announce the stub, refund, allocation and reallocation adjustments.
- R2: the generic assembly sentences that now sit in the computation documents ("Every amount a rule of this schedule adds to or takes off ...", "Every share a rule of this schedule adds to the held share ...", "with every amount of interest a rule of this schedule adds or takes off") still tell a reader that other rules adjust the figure, and the direction one names "the held share". This is acceptable as source design, but it weakens the computation documents' silence.
RENDER round 2: DOCS OK, TRACEABILITY OK
