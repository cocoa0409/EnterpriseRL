# plan — contract_payments_fees_and_servicing (env_0072), M=2  (v2, relaunch)

Draw (scripts/draw_counts.py --tasks 2):
- task 0: prerequisite_problems=2, factor_counts=[6, 6, 4]
- task 1: prerequisite_problems=2, factor_counts=[6, 6, 5]

v2 revisions vs predecessor plan (reasons):
- T0 factor split changed: agreement months = 6, late charge = 4, extension fee = 6 (months is a min-of-allowances
  computation where six independent allowances all bind; the late charge has few non-masking real factors).
- T0 seeds a CLOSED recovery case (recalled, account_brought_current): base gate extension_no_open_recovery needs a
  recovery_cases row to bind, and it is the cross-difficulty evidence of the fee's recovery-review charge.
- T1 never seeds an OPEN recovery case: a payoff would leave the case owing a recall (recovery charter), an
  obligation outside this difficulty. T1's recovery evidence is a closed (recalled) case.
- Returned-item fee policy subject = [contract_payment_returned] (subject contract_fee_assessed would drag the
  late-charge gates into the returned-fee write).
- Sign tool signs the borrower's OPEN online hardship request (pending_signature row seeded, created two days
  before frozen_time): base gates extension_signed_agreement / signature_in_time bind service_request_id pre-action.

## Space budget (6 extended policies, pairwise disjoint per task)

| task | problem (policy id) | tool (owner) | computes | factors |
|---|---|---|---|---|
| 0 | contract_ext_hardship_extension_charge (ROOT) | grant_hardship_extension_883d335d (agent) | extension_fee_usd | 6 |
| 0 | contract_ext_deferral_agreement_months | sign_extension_agreement_772d986b (user) | requested_extension_months | 6 |
| 0 | contract_ext_delinquency_late_charge | assess_late_charge_1a8e6313 (agent) | amount_usd | 4 |
| 1 | contract_ext_borrower_payoff_amount (ROOT) | authorize_payoff_payment_7f0b790b (user) | amount_usd | 6 |
| 1 | contract_ext_payoff_statement_amount | issue_payoff_quote_f4f38627 (agent) | quoted_payoff_usd | 6 |
| 1 | contract_ext_returned_item_fee | assess_returned_payment_fee_c98c0726 (agent) | amount_usd | 5 |

Edges:
- T0 (fan): charge <- agreement (value_input: deferred installments enter charged units / lifetime review charge;
  state form "only after ... signed agreement naming the installments"); charge <- late charge (value_input:
  late-charge credit on the oldest deferred installment; state form, negated direction "not ... until").
  Agreement and late charge commute (neither reads the other's rows).
- T1: payoff amount <- statement (state_gate: payoff taken against a standing statement dated on the posting date);
  payoff amount <- returned item fee (value_input: fees counted); statement <- returned item fee (value_input).

## T0 design (frozen 2026-10-20 11:05:00 EDT; Renata Castellanos, Atlanta GA; Tier 4 Standard)
World: contract 2023-08-03, first due 2023-09-08, due day 8, term 60, AF 21480.00, APR 22.49; one earlier
extension (1 inst, eff 2024-05-14); recovery case recalled account_brought_current 2025-02 (cure of Dec/Jan);
late charge in rolling 12m: one (Apr 2026); autopay 10 drafts in 12m; Oct 2 $250 self-service partial;
next_due 2026-10-08 (dpd 12, grace ended Oct 18, late charge unassessed); open online hardship request
(pending_signature, created 2026-10-18); CPI compliant, lapse notice 2025-05 (outside 12m).
Late charge (4): delinquency_rate_schedule (param, state+signing date, multi-source), charge_basis (method:
 final installment / on-time partial credit / scheduled), first_delinquency_relief (param, prior late count 12m),
 autopay_relief (param, autopay count 12m). amount = RND(MN(cap, rate/100*basis*(100-reliefs)/100)).
Months (6, min of allowances; result 2, each baseline 1): insured_collateral (cpi, X-diff, multi-source),
 account_seasoning, remaining_term, deferral_scope (method), deferral_spacing, due_change_recency; plus base caps.
Fee (6): deferral_charge_schedule (param, state+date), charge_units (method, value_input from months),
 late_charge_credit (method, value_input from late charge), delinquency_stage_charge, lifetime_deferral_charge,
 referral_review_charge (recovery X-diff). fee = RND(MX(0, charge*units + handling - credit)) * first-waiver.

## Trigger rule (events my tools write, with base triggers) — none lands outside contract
- sign_extension_agreement: contract_service_requests update (intake; no event, no triggers).
- assess_late_charge / assess_returned_payment_fee: contract_fee_assessed -> contract:contract_servicing_update.
- grant_hardship_extension: contract_extension_granted -> contract:contract_servicing_update,
  contract:contract_fee_assessed (fee_treatment fee_assessed) -> contract:contract_servicing_update.
- issue_payoff_quote: contract_payoff_quoted -> [].
- authorize_payoff_payment: contract_payment_posted with payment_type FIXED payoff -> contract:contract_fee_paid,
  contract:contract_servicing_update, contract:contract_paid_off (-> contract:contract_lien_released, NOT written:
  funds are not final on the posting date). payment_type is never reinstatement/redemption (recovery triggers).
Never written: recovery reinstated/redeemed/sold, deficiency opened, dealer funding, any cpi/gap/recovery row.

## Scratch
/tmp/contract_payments_fees_and_servicing_0072/ (authoring scripts deleted at the end).

## T1 design (frozen 2026-10-23 14:20:00 CDT, Friday; Gunnar Lindqvist, Mobile AL; Tier 3 Advantage; AL contract+title)
World: autopay history; Aug-2025 late charge left unpaid (payments of exactly one installment never reach fees);
Nov-2025..Jan-2026 delinquency, referral 2026-01-19 (AL needs no cure notice), cured 2026-02-04, case recalled
account_brought_current; May-2026 autopay returned NSF (fee priced by the returned-item policy at that date);
payoff quote issued 2026-10-05 (sale fell through); 2026-10-14 phone payment (ach_agent, agent fee) returned
2026-10-21 account_closed -> next_due back to 2026-10-18 (5 days late, within grace), returned fee unassessed.
Returned-item fee (6): return_fee_schedule (state+amount, multi-source), subsequent_return_charge, return_reason_charge,
 failed_payment_offset (method), late_return_handling, restriction_review_charge.
Payoff statement (6): statement_window (delinquency/returns), funds_cushion (returns vs tier threshold),
 late_estimate_basis (method), title_release_days (paper title), repeat_statement_cut (quotes in rolling month),
 window_anchor (quote day of week -> next business day).
Borrower payoff (5): interest-through-funds-final conventions (funds_final_days by return history, weekend_posting_days,
 referral_verification_days [recovery X-diff], return_hold_days, delinquency_hold_days). Payoff = principal + fees due +
 interest through the posting date plus the hold days; tool books fees in full, interest as the remainder.
Known weakness (honest): the payoff amount has little legitimate variability beyond base; its five factors are company
 funds-finality/hold conventions. Interest accounting stays consistent (no refund obligation is created).
Edges: payoff <- statement (state_gate), payoff <- returned fee (value_input), statement <- returned fee (value_input).

## v3 — rework round 2 (policy-task audit revision_1: CW-1..CW-9)
- Months: every delinquency/spacing test keyed to the signing date; windows in the rolling convention; seasoning and
  remaining term counted as monthly due dates; generic assembly sentence.
- Fee: generic assembly ("charge x number of charges + amounts added - amount taken"), self-contained replaced_by;
  prerequisite sentence requires a signed, not yet applied agreement; recovery review reads the unique reinstated case
  (CFIELD) and a cured recalled case by EXISTS.
- Returned-item fee: tie rule stated; late-return handling replaced by bank-charge recovery (state schedule); state cap
  schedule (FL/LA 40, AL/MS/GA 30); a zero fee is never booked; generic assembly.
- Statement: repeat-statement and recovery shortening replaced by insurance-lapse shortening (cpi, cross-difficulty) and
  remittance-method days; business-day anchor relabelled parameter; rolling windows; tie rule; generic assembly.
- Payoff: same-day payoff good through the posting date plus review days (per diem through that good-through date);
  weekend days carry it to Monday (3/2/1); autopay-history hold replaced by referral-history review (recovery,
  cross-difficulty, unique reinstated CFIELD + EXISTS); tie rules; prerequisite gate field = effective_date.
- Seeds: one late charge per delinquency stretch (oldest unpaid installment only); T0 amount financed 21490.00 (no
  half-cent tie); T1 moved to Florida (Tampa) with a CPI tracking record (lapse notice 2026-02-12, cured 2026-02-24).

### adversarial probe table (scratch copies; result vs rule expectation; all agree)
| probe | read/edge | result | rule says |
|---|---|---|---|
| LC: no posted payment | LATEST None | scheduled basis | partial tier needs a payment on/before due date |
| LC: next_due = maturity | DAYS == 0 | final-installment basis | lesser of installment and principal+interest |
| DM: no cpi record / closed record (decoy) | EXISTS false | 1 | every other case: one installment |
| DM: cpi force_placed | EXISTS | 0 (no agreement) | allowance zero |
| DM: no earlier extension | LATEST None | spacing top | no earlier extension |
| DM: current account | DAYS <= 0 | per-request cap | next_due on/after signing date |
| DM: spacing 2024-10-20 vs 2026-10-20 / 2024-10-21 | MONTHS boundary | 2 / 1 | on or before the same day 24 months back |
| DM: 2024-02-29 vs 2026-02-28; 2024-03-31 vs 2026-03-30/31 | month-end | 1; 1 / 2 | same-day anchor with month-end fallback |
| HF: no signed agreement | LATEST None -> 0 | one charge, no review | every other case one; no extension applies |
| HF: second recalled case (decoy) | EXISTS | unchanged | a case closed as recalled ... |
| HF: reinstated case 10 months back | CFIELD unique | adds reinstated review | reinstated within the window |
| HF: no recovery case | CFIELD None, EXISTS false | adds nothing | otherwise |
| HF: credit above charges | MX(0) | 0, fee_waived | never below zero; zero -> fee_waived |
| RPF: two returns same date | LATEST tie | first recorded priced | same date: first recorded |
| RPF: autopay return | channel | autopay credit taken | autopay draft tier |
| RPF: AL contract | cap | <= 30.00 | state cap schedule |
| RPF: computed zero | MX(0) | no fee booked | zero -> not booked |
| STMT: latest payment not returned | COUNT 0 | unpaid interest carried | returned -> reversed interest only |
| STMT: no cpi / lapse_notice status | EXISTS/XCOUNT | 0 / placed cut | insurance-lapse tiers |
| STMT: days below zero | MX(0) | quote date | never earlier than the quote date |
| PAY: no return | LATEST None | no return review days | otherwise |
| PAY: Sunday posting | weekday 6 | 1 day | Sunday adds sunday_review_days |
| PAY: reinstated case recent | CFIELD unique | 3 days | reinstated within lookback |
| all: rows created at the frozen clock | same-day | fee/quote rows are not read by LATEST/COUNT of another kind | n/a |

### round-3 probes (remittance-method read)
| probe | result | rule says |
|---|---|---|
| task-1 world (one-time payment later returned) | one_time_days | counted whether or not later returned |
| window payments all third_party_remittance | 0 | every other case |
| all ach_autopay | 0 | every other case |
| a check_mail payment | mail_days | mailed check |
| wire_transfer / moneygram | one_time_days | one_time_channels |
| no payments in window | 0 | every other case |
