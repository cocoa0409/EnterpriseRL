# worklog — residential_bill_credits_and_charges (home), M=2

## Step 0 — pre-check and draw
draw_counts.py --tasks 2:
- task 0: prerequisite_problems=2, factor_counts=[6,6,4]
- task 1: prerequisite_problems=2, factor_counts=[5,6,4]

Base read: home.yaml (lifecycle, 9 claimed events, policies home_evt_subscription_charge / _credit_correction /
_payment_application / _late_fee / home_billing_arrangement / home_benefit_basis), db_schema, share_tools (verify K=2).
Claimed events and their base triggers (F4 trigger list):
- home_charge_billed: [] ; home_late_fee_assessed: [] ; home_returned_fee_assessed: [] ; home_payment_received: []
  (the four events my tools write — none has a trigger, so nothing lands in another category).
- not written by my tools: home_credit_posted -> home:home_charge_billed; home_credit_reversed -> home:home_billing_credited;
  home_payment_returned -> home:home_returned_fee_assessed (all same-category).

Realism constraints found while reading (decisions recorded):
- D1 Subscription-charge price is fixed by home_benefit_basis (own plan savings rate only) -> no factor may sit on an actual
  charge's price; computations go on estimates, fees and payments (realism bar "Design consequence").
- D2 The Income-Eligible Priority Waitlist accepts only NY_VDER / IL_SHINES / MD_CS; garden is MN-only. A household cannot
  carry both LMI evidence and a garden share. Both task worlds are therefore NY / MD worlds and the cross-difficulty evidence
  is the waitlist (IE Priority reservation queued on the same utility account). No garden rows are seeded.
- D3 Late fees on estimates are excluded by base ("never ... estimates later offset") -> no late-fee-on-estimate policy.
- D4 The compute DSL selects rows only by exact-value filters and whole-month windows counted back from today; every
  selection below is written in those terms in the rule (C5).
- D5 Payment amounts: base has no rule for how much a call payment collects; the two payment policies define it (no base
  conflict, overwrite []), with the subscriber paying through the secure portal (owner ruling (b)).
- D6 The two late-fee policies price the same line kind for two disjoint subtypes (charge never settled by a returned
  payment / charge reopened by a returned payment) and carry identical ladders (coordinator mirror rule); their overwrites of
  the base fee sentence each name both cases (E3).
- D7 Factor kinds that are company schedules (R6) are tagged in the factor-reads table below.

## Policy set (6 policies, 2 trees)
task 0 (NY, National Grid, closed residential share, late utility statements):
- home_ext_final_balance_payment (root, owner=user, on_request, 4 factors)
- home_ext_estimated_charge (prereq, agent, state_due, 6 factors) -- value_input into the root
- home_ext_overdue_late_fee (prereq, agent, state_due, 6 factors) -- value_input into the root
task 1 (MD, BGE, active share, card payment reversed by the card issuer):
- home_ext_reversed_payment_replacement (root, owner=user, on_request, 4 factors)
- home_ext_returned_payment_fee (prereq, agent, state_due, 5 factors) -- value_input into the root
- home_ext_reopened_late_fee (prereq, agent, state_due, 6 factors) -- value_input into the root

## Tool names (uuid8 drawn once per tool with uuid.uuid4().hex[:8])
bill_estimated_charge_232393a8, assess_overdue_charge_late_fee_df41ca22, pay_final_balance_42abd449 (task 0);
assess_returned_payment_fee_1f86a5ed, assess_reopened_charge_late_fee_2381e61d, pay_reversed_payment_replacement_378a2026 (task 1).

## Task 0 — design thesis
Surface goal: Marit Halvorsen (closed Standard 10 share, NY National Grid) pays off what is left today by card.
Root: home_ext_final_balance_payment (owner=user). Prereqs: home_ext_estimated_charge (September 2026 estimate owed since
2026-11-14), home_ext_overdue_late_fee (July 2026 charge past grace since 2026-11-15). Chain: goal -> payment rule's two
prerequisite sentences -> estimate (6 factors) + late fee (6 factors) -> payment (4 factors) -> card payment by the caller.
Draw [6,6,4]: estimate 6, late fee 6, payment 4. Both edges value_input (>= 1 required).

### Capability contract cards
- bill_estimated_charge_232393a8 — owner agent / write; object: one residential subscription; effect: one home_billing line
  home_charge_billed, charge_basis estimated, no credit ref, billing_type dual, bill_date today, due_date as given; receipt
  status/home_bill_id/home_sub_id/billing_month/amount/bill_date/due_date; event triggers [] (stays in home).
- assess_overdue_charge_late_fee_df41ca22 — owner agent / write; one home_late_fee_assessed line referring to the overdue
  charge; receipt status/home_bill_id/home_sub_id/home_ref_bill_id/amount/bill_date/due_date; triggers [].
- pay_final_balance_42abd449 — owner user / write; one home_payment_received line (ach|card), billing_month = month of
  payment; receipt status/home_bill_id/home_sub_id/amount/payment_method/bill_date/billing_month; triggers [].
  Owner ruling (b): holder-completed portal payment, method not on file (rule text + persona).

### What each factor reads (A1) — task 0 policies
| policy | factor | kind | reads (bindings) | reads another factor? | R-tag |
|---|---|---|---|---|---|
| estimate | est_standing | method | open dispute id (home_requests), disputed charge in window, billing-error credits in window | no (window sums are plain) | R2/real practice |
| estimate | est_season | parameter, multi-source | actual-charge count on record AND charge invoiced 13 whole months back | no | R2 |
| estimate | est_capacity | method | latest subscriber increase/decrease effective_date, charges after it, kW filings | no (window average is plain) | R3 |
| estimate | est_credit_rate | method | latest posted credit value/kWh vs window value/kWh | no | R4 (utility rate moves) |
| estimate | est_run | parameter | latest charge basis, estimates in last 2 months | no | R6 |
| estimate | est_lag | parameter | days since latest credit posting | no | R2 |
| overdue fee | ofl_priced_amount | method | returned payments of the month, latest payment date/amount vs due_date | no (unpaid amount is plain) | R2 anchor |
| overdue fee | ofl_months | parameter | whole months from due_date to today | no | R2 |
| overdue fee | ofl_household_income | parameter, cross-difficulty, multi-source | access status/recert_due_date; waitlist IE reservation status/account | no | R1 LMI |
| overdue fee | ofl_repeat | parameter | late fees in last 12 months | no | R6 |
| overdue fee | ofl_size | parameter | overdue charge amount | no | R6 |
| overdue fee | ofl_banked_share | method | banked_value / credit_value of the priced credit line | no | R6 |
| final payment | fbp_standing | method | status, removal_notice_date, due-dated sums | no | R2 |
| final payment | fbp_dispute_hold | method | open dispute, disputed line kind/amount/payments/credits/fees | no | real consumer protection |
| final payment | fbp_household_income | parameter, cross-difficulty | access/waitlist as above | no | R6 |
| final payment | fbp_open_estimates | parameter | status, latest charge basis | no | R6 |
Assembly (plain): estimate = blend then one multiplying step then one rounding; late fee = priced amount x pct x
multipliers, one rounding, then min/max; payment = covered lines less deductions, each on its own lines, one rounding.

### Defining-sentence table (A4) — task 0
- "The estimate window holds ..." / "The estimate basis is the average ..." -> baseline (estimate).
- "the same-season reference charge is ..." -> est_season; "the latest change is the filing line ..." -> est_capacity;
  "the latest credit rate ... window credit rate ... relative change" -> est_credit_rate; "The estimated charge's run
  percentage ..." -> est_run; "lag percentage ... calendar days from the latest posted_date" -> est_lag; "settled by the
  standing of the window's charges" -> est_standing.
- "The overdue charge is ... its unpaid amount is ..." -> baseline (overdue fee); "The amount the overdue-charge late fee
  is priced on" -> ofl_priced_amount; month / household-income / repeat / size / banked-share multiplier sentences -> one
  factor each.
- "covers the lines due on or before today" -> baseline (payment); "The lines the final-balance payment covers are settled
  by the subscription's standing" -> fbp_standing; "dispute hold" -> fbp_dispute_hold; "fee share" + "recent fee lines"
  -> fbp_household_income (recent fee lines is a plain shared selection); "estimate share" + "open estimates" ->
  fbp_open_estimates (open estimates plain shared selection).

### Probe table (C1) — task 0 reads
| read | decoy | absent | second record |
|---|---|---|---|
| open dispute (LATEST requests, outcome received) | decided/withdrawn disputes filtered out by outcome | 'none' -> standing/hold tiers fall through | latest received_date wins, same day first on record (stated) |
| estimate window charges | estimates excluded by charge_basis actual | window empty -> estimate 0.00, none billed (stated) | all window charges averaged |
| same-season charge | charges 12 or 14 months back excluded by the exact-13 window | none -> weight 0 | several in that month averaged |
| latest subscriber change | removals (cancellation_removal) not subscriber changes | '0001-01-01' -> ratio 1 | later effective_date wins |
| latest credit posting | reversals excluded (event home_credit_posted) | rate change 0 | same-day postings: first on record (stated) |
| overdue charge | estimates and consolidated charges excluded | 'none' -> fee 0 | latest bill_date, first on record |
| IE reservation | other classes / lapsed / withdrawn excluded by variant and status filters; another account fails the account test | 'none' -> multiplier 1 | at most one open IE reservation per customer (class limit 1) |
| Access subscription | closed Access excluded by status active | none -> next tier | first match (status active) |
| priced credit line | n/a | 'none' -> multiplier 1 | one credit per charge |
Edges: DAYS with no posting -> NOW (0 days); MONTHS with no change -> large; zero divisions guarded by count/positivity tests.

### Pairwise method-tier table (B1) — task 0
- est_standing: (a) average without the disputed charge vs (b) sum less billing-error credits / n vs (c) plain average —
  distinguishing inputs: disputed charge amount; billing-error credits.
- est_capacity: (a) post-change charges average / window average vs (b) kW held / kW before vs (c) 1 — inputs: charges after
  the change vs kW filings.
- est_credit_rate: (a) 1 + change vs (b) 1 + change/2 vs (c) 1 — different operations on the same relative change.
- ofl_priced_amount: (a) charge less credits (payments ignored) vs (b) unpaid + latest late payment vs (c) unpaid — inputs:
  returned payments; latest payment after due date.
- ofl_banked_share: (a) 0 vs (b) 1 - banked/value vs (c) 1 — input: banked_value.
- fbp_standing: (a) every line vs (b) lines due before today vs (c) lines due on or before today — inputs: lines not yet due;
  lines due today.
- fbp_dispute_hold: (a) charge unpaid + its late fees vs (b) fee less credits vs (c) 0 — input: disputed line kind.

### Task 0 — verification run (scratch /tmp/residential_bill_credits_and_charges_0082/gen0*.py, task0*.py)
Seeded own-category rows priced by the extended rules at their own dates (H2): June late fee 2026-08-15 = 2.00 (raw 1.50,
minimum); July estimate 2026-09-15 = 97.85 (offset 2026-10-14 by its true-up credit); August estimate 2026-10-16 = 152.36.
Gold at 2026-12-05: estimate 96.71 (raw 96.714382), overdue late fee 3.16 (raw 3.159135), final-balance payment 251.55
(raw 251.552). Factor sensitivity: estimate 99.66/112.58/98.05/85.53/113.78/101.80, all-baseline 131.53; late fee
2.43/2.00/3.95/2.63/3.33/3.55, all-baseline 2.00; payment 151.68/398.14/252.34/351.18, all-baseline 398.69.
Commute: late fee after estimate 3.16, estimate after late fee 96.71. Edge deletion: skip estimate -> 193.53, skip late fee
-> 249.18. Revision: estimate_share_closed 0.5 -> 0.6 (symptom: payment raw 226.645 on a half cent; root cause: 0.5 x odd
cents; change: share 0.6/0.8; rerun raw 251.552). Revision: policy_source carried the token estimate_wait_days (check_extended
red) -> reworded "the plan's estimate wait". Revision: empty id fields seeded as '' were read as dangling FKs -> null.
Revision: closure missed utility account, projects, reviews -> reads find_utility_accounts / find_projects /
find_home_reviews added (each feeds a decision). Revision: estimate tool has no credit-line argument, so the base dedup
"Each posted credit statement line is priced by exactly one actual subscription charge." is retired for estimates by a
self-scoped overwrite that restates it for credit lines.

## Task 1 — design thesis
Surface goal: Desmond Adeyemi (Commit 5, MD BGE, active, dual) makes good the 2026-10-01 card payment (259.13) his issuer
reversed on 2026-11-09 and pays what he owes today by ach. Root home_ext_reversed_payment_replacement (owner=user);
prereqs home_ext_returned_payment_fee (fee for the reversed item, owed since 2026-11-09) and home_ext_reopened_late_fee
(August charge reopened, past grace). Draw [5,6,4]: returned-payment fee 5, reopened late fee 6, payment 4. Both edges
value_input. Headroom at task 0 claim time: these three policies were left untouched by task 0 (disjoint tools/policies).

### Capability contract cards (task 1)
- assess_returned_payment_fee_1f86a5ed — agent/write; one home_returned_fee_assessed line referring to the returned payment;
  receipt status/home_bill_id/home_sub_id/home_ref_bill_id/amount/bill_date/due_date; triggers [].
- assess_reopened_charge_late_fee_2381e61d — agent/write; one home_late_fee_assessed line referring to the reopened charge;
  same receipt; triggers [].
- pay_reversed_payment_replacement_378a2026 — user/write; one home_payment_received line (ach|card); receipt as the
  final-balance tool; triggers [].

### What each factor reads — task 1 policies
| policy | factor | kind | reads | R-tag |
|---|---|---|---|---|
| returned fee | rpf_item_base | method | returned amount (latest returned-payment line) | R4-shaped (greater-of statutory form) / R5 (never exceeds item) |
| returned fee | rpf_item_kind | parameter | payment_method of the returned line | R6 |
| returned fee | rpf_reversal_time | parameter | days from the payment's receipt to its return | R6 |
| returned fee | rpf_repeat | parameter | returned-payment lines in 12 months | R6 |
| returned fee | rpf_household_income | parameter, cross waitlist, multi-source | access status/recert; IE reservation status/account | R1 LMI |
| reopened fee | rfl_* (6) | mirror of ofl_* | same reads on the reopened charge (object = charge of the month on the latest returned line) | as ofl_* |
| replacement | rpp_return_record | method | returned-payment lines in 12 months; fees assessed today | R2 |
| replacement | rpp_dispute_hold | method (mirror of fbp_dispute_hold) | open dispute and disputed line | consumer protection |
| replacement | rpp_household_income | parameter (mirror of fbp_household_income), cross waitlist | access/waitlist | R6 |
| replacement | rpp_reversal_kind | parameter | payment_method of the latest returned line; late fees on the reopened charge | R6 |
No factor reads another factor's binding; assembly is the plain product / plain deduction sum stated once per policy.

### Probe table — task 1 reads
| read | decoy | absent | second record |
|---|---|---|---|
| latest returned-payment line | the May ACH return is older (latest bill_date wins) | 'none' -> fee 0, no line | same day: first on record (stated) |
| returned item's receipt date | n/a | falls back to the return date (0 days) | one payment per returned line |
| reopened charge | estimates and other months excluded by billing_month and charge_basis filters | 'none' -> fee 0 | one actual charge per statement month |
| returned lines in 12 months | lines 12+ whole months back excluded | 0 -> fall-through | counted |
| open dispute | decided/withdrawn excluded by outcome | 'none' -> no hold | latest received_date |

### Pairwise method-tier table — task 1
- rpf_item_base: (a) greater of fee and pct x amount vs (b) the returned amount vs (c) the fee — inputs: amount above the
  large-item threshold; amount below the fee.
- rpp_return_record: (a) every line vs (b) lines due on/before today plus fees assessed today vs (c) lines due on/before
  today — inputs: not-yet-due lines; today's fees.
- rfl_* tiers as ofl_* (mirror).

### Task 1 — verification run
Seeded rows priced by the extended rules at their own dates: May returned-payment fee 2026-05-08 = 15.00 (20.00 x 0.75);
July late fee 2026-09-17 = 2.00 (overdue-charge rule, raw 1.43, minimum; the July charge was the latest-invoiced charge
that day because the August statement was posted 2026-09-14 and invoiced 2026-09-19). Gold at 2026-11-12: returned-payment
fee 22.78 (raw 22.775098), reopened late fee 3.02 (raw 3.019451), replacement payment 246.47. Sensitivity: fee
17.58/18.22/30.37/18.22/30.37, all-baseline 20.00; late fee 2.25/2.00/3.77/2.52/3.18/3.21, all-baseline 2.00; payment
220.67/338.89/253.42/247.98, all-baseline 321.55. Commute: late fee after fee 3.02, fee after late fee 22.78. Edge deletion:
skip fee -> 229.39, skip late fee -> 245.72. Revision: large_item_usd 250 -> 200 (the multi-month card payment is 259.13;
the large-item tier must be reachable by the realistic catch-up payment). Revision: the open dispute was moved from the
July late fee to the September charge (a fee line both held and counted as a recent fee would be deducted twice).

## Manual values gates (both tasks) — results
- Length/breadth: each tree = root payment waiting on two state-form sentences; each prerequisite is a 5-6 factor
  computation over 27-40 months of ledger plus the waitlist record of another difficulty; the owner=user write is the
  holder's portal payment (owner ruling b; method not on file stated in rule and persona).
- Persona boundary: neither persona names a fee, estimate or prerequisite; identity on request; asks nothing the charter
  does not decide; last reaction answers the payment step.
- Chronology: every volunteered fact (cancellation effective 2026-10-01; card payment of 2026-10-01 reversed in November)
  has a seed row.
- Time gates: after_grace checked with just-before / at-boundary cases (temporal_feasibility); estimate wait 2026-11-14.
- Draft recomputation from published rules only (prose of the six rules, schemas, find-tool returns): reproduces the same
  write order and the same figures (scratch scripts evaluate the published compute, not a private formula).
- Known weak points for the audit (honest list): the payment computations' fee/estimate shares and reversal share, the
  late-fee repeat, size and banked-share multipliers, the run percentage of the estimate and the returned-fee item and
  reversal-time multipliers are company schedules (R6) chosen to meet the drawn factor floor; the charter offers no further
  honest levers for a payment amount (D1, D5). The late-fee and payment policies are split by subtype and mirrored (D6).

## Final gate block (difficulty level, no --task)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK
(cache-diff: info only; traceability pre-render: only the six unlock tool names lack a source, which the KB render supplies)
ROUND 1: gates 7/7 green (superseded by the round-2 rework below)

## REWORK round 2 (audit revision_1: CG-1..CG-18, F-T0-1/2, F-T1-1/2; realism_bar AMENDMENT 1) — ids and dispositions only
Redesign summary (no figures): estimate loses the run haircut and lag percentage (AMENDMENT 1.4) and gains a reversal-standing
method and an unpriced-latest-credit weight; its credit-rate factor becomes a parameter (CG-3). Both payment policies lose the
scope factors (CG-1, CG-2) and gain a mirrored pending-statement method (the unpriced latest posting's coming charge, less the
open estimate it replaces); their baseline is every open line. Both payment policies overwrite the payment-application order:
lines under an open dispute and their late fees are settled by no payment, and each payment records the statement month of
the oldest open line it settles; the payment tools take that month (CG-18). The returned-payment fee drops the reversal-time
factor (CG-16) for a committed-term parameter (R1 plan term), caps a returned check at the plan fee and every item at a fee
ceiling (CG-17). Worlds rebuilt with FIFO-consistent payment labels and waitlist rows inside the headroom on their own
submission date (F-T0-1/2, F-T1-1/2); every own-category seeded row re-priced by the rules as they now stand.

### Lever catalogue (AMENDMENT 1.2) — home charter
Plan parameters (P): eligible_customer_types / eligible_programs / min_annual_usage_kwh / min_allocation_kw /
max_allocation_kw / allocation_increment_kw / sizing_cap_pct / usage_data_max_age_months / credit_review_required /
income_verification_required / utility_data_authorization_required — unusable (enrollment and sizing, amount-neutral for bills);
pricing_method / fixed_rate_per_kwh / annual_escalator_pct — constant across home plans (pct_of_credit, 0); savings_rate_pct —
USED (unpriced-line and pending-statement charges priced at the plan's own rate; benefit_basis forbids any other cut);
charge_rounding — used (half up); invoice_issue_days_after_posting — used (why a posting is still unpriced);
estimated_billing_allowed / estimate_wait_days — used (estimate gate); estimate_basis_months — replaced by the declared window
(overwrite); max_consecutive_estimates — used (run gate); billing_types_offered — used (estimates dual only);
invoice_due_days — used (due dates); late_fee_grace_days — used (gate); late_fee_pct / late_fee_min_usd / late_fee_max_usd —
used (constant across plans, so they cannot key a tier); returned_payment_fee_usd — used (constant across plans; base of the
returned fee and the check cap); payment_methods / payment_application_order — used (portal methods; overwritten order);
nonpayment_removal_* / removal_notice_days — unusable (a removal-notice payment would make clearing the notice an owed write
outside the tree); security_deposit_months / deposit_refund_on_time_months — unusable (0 on every home plan);
allocation_changes_per_contract_year / max_decrease_pct_per_contract_year / excess_decrease_fee_per_kw_usd /
min_months_before_first_change / increase_waitlist_when_full — unusable (allocation-change fees, not bill items of these
trees); term_months — USED (committed-term multiplier); post_term_renewal — used through term_end_date;
cancellation_notice_days / preactivation_cancel_fee_usd / etf_* / rescission_business_days / transfer_* / successor_* —
unusable (closing events of other trees; no ETF on Standard 10, T1 not closing); production_guarantee_pct /
annual_review_enabled / oversize_review_threshold_pct / resize_target_pct — unusable here (true-ups complete, no shortfall);
recert_interval_months — 0 on home plans; dispute_late_fee_hold / dispute_resolution_days — used (base hold; decision dates).
Holding fields: status — used (estimate share); billing_type — used (estimates dual only); activation_date / term_end_date —
used (contract years; committed-term multiplier); allocation_kw — unusable after closing (0) and shadowed by filings, which are
used; closed_date / notice_date / scheduled_end_date — used for standing only; removal_notice_date — unusable (no removal tree);
contract_kw, sales_channel, signed/approved dates, move/pending fields — amount-neutral.
Event fields: home_billing amount / bill_date / due_date / billing_month / charge_basis / home_credit_id / home_ref_bill_id /
payment_method / credit_reason / event_type — used; billing_type on lines — constant dual in both worlds. home_credits
credited_kwh / credit_value / banked_value / posted_date / statement_month / home_reversed_credit_id — used. home_allocations
kw / effective_date / filing_reason — used. home_requests request_type / home_disputed_bill_id / received_date / outcome — used;
requested_kw — allocation changes only. home_reviews — no open item (completed reviews only).
Other categories: waitlist variant_name / status / utility_account_id — used (household income tiers); access status /
recert_due_date — used (Access tier); garden / biz / farm / civic — unreadable for these households (garden is Minnesota-only
and the income-eligible waitlist serves no Minnesota program; the other lines take no residential customer).
R6 factors that remain because no unused honest lever exists on that computation in that world: overdue / reopened late fee
repeat, size and banked-share multipliers; returned-payment fee item kind and repeat; payment fee share, open-estimate share and
reversal kind. None acts only through another factor, moves a utility- or state-set figure, cuts a charge or an estimate, or is
X1–X4. R-tags of the others: estimate standing / reversals (R2 estimating hygiene), season (R2), capacity (R3), credit rate (R4
utility rate moves), unpriced line (R2); late fee priced amount (R2 anchor), months (R2), household income (R1 LMI); returned fee
item base (R5 item bound), committed term (R1 plan term), household income (R1); payment dispute hold (consumer protection),
pending statement (final-bill practice).

### What each factor reads (round 2)
- estimate: est_standing — open dispute id, disputed window charge, billing-error credits; est_reversals — reversal-correction
  credits in the window, charges one month beyond it; est_unpriced_line — latest posting, charges pricing it, estimates of its
  month; est_season — charge count, charges thirteen months back; est_capacity — latest subscriber filing and its date, later
  charges, kW filings; est_credit_rate — latest posting value/kWh, window postings. None reads another factor's binding; the
  window sums are plain; the assembly line is stated once.
- late fees (mirrored): unchanged reads; the reopened rule's object is the latest-invoiced actual dual charge of the month on
  the latest returned-payment line.
- returned fee: item base — returned amount; item kind — returned line's method; committed term — term_months and
  term_end_date; repeat — returned lines in 12 months; household income — access / waitlist.
- payments (mirrored where shared): dispute hold — open dispute, disputed line kind / amount / month payments / credits / fees;
  pending statement — latest posting, its pricing charges, its month's open estimate (with its own dispute read); fee share —
  access / waitlist; open-estimate share (final balance) — status, latest charge basis; reversal kind (replacement) — latest
  returned line's method. The recent-fee, open-estimate and reopened-fee selections are plain bindings with their own dispute
  and pending reads.

### Defining-sentence table (round 2, changes only)
- "No estimate is billed while the latest subscription charge ... max_consecutive_estimates ..." -> plain run gate (estimate).
- "The estimate's reversal standing ..." -> est_reversals; "The estimate's unpriced-credit weight ..." -> est_unpriced_line.
- "... covers every open line ..." -> payment baselines; "... pending-statement addition ..." -> pending_statement (both).
- "For every payment on a residential subscription ... settled by no payment while the dispute is open ..." -> overwrite
  sentence of both payment policies (identical text, one ruling).
- "The returned-payment fee's term multiplier ..." -> rpf_committed_term; "... limited to fee_ceiling_usd, and for a returned
  check to returned_payment_fee_usd ..." -> plain cap.

### Probe table (round 2 additions; scratch probe.py on copies of the task worlds)
| read | decoy | absent | second record |
|---|---|---|---|
| dispute hold line kind | dispute naming a payment line -> no hold (probed) | withdrawn dispute -> no hold (probed) | latest received_date |
| pending statement | reversal rows excluded by event filter; a priced posting -> no addition | no posting -> none (probed) | same-day postings: first on record |
| unpriced line | priced latest posting -> weight 0 (probed) | none -> 0 | first on record |
| reversal standing | estimate_trueup / billing_error credits excluded by credit_reason | none -> nothing taken off | several corrections summed and counted |
| capacity | future effective date -> ratio 1 (probed) | none -> 1 | latest effective date |
| late-fee zero edge | tiny unpaid -> raised to the minimum unless the product rounds to 0.00 (probed) | — | — |
| returned item | — | none -> no fee | first on record same day |

### Pairwise method-tier table (round 2 changes)
- est_reversals: (a) offset sum and count off vs (b) the same plus the charges one month beyond the window vs (c) nothing —
  distinguishing inputs: correction credits; charges of the extra month.
- pending_statement: (a) coming charge less the replaced open estimate vs (b) coming charge alone vs (c) nothing —
  inputs: open estimate of the posting's month; the unpriced posting's credit_value.
- dispute_hold: (a) charge unpaid plus its late fees vs (b) fee less credits vs (c) nothing — input: disputed line kind.
- rpf_item_base: (a) greater of plan fee and percent of item vs (b) the item amount vs (c) the plan fee.

### Item dispositions
See audits/policy_task/residential_bill_credits_and_charges/rework_r2_claims.md (one line per item id).
REWORK round 2: gates 7/7 green
