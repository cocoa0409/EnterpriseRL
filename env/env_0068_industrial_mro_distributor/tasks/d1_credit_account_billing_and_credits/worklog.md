# worklog — d1_credit_account_billing_and_credits (instantiate round 1)

## Step 0 — pre-check and draw
- Read references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/credit.yaml,
  db_schema.json, share_tools.py, audits/render_source/XF_recipe.md.
- draw_counts.py --tasks 2:
  - task 0: prerequisite_problems=1, problems=2, factor_counts=[5, 4]
  - task 1: prerequisite_problems=1, problems=2, factor_counts=[6, 4]
- Base automatic clauses (credit): hold placement (past_due / returned_payments / over_limit), collections
  referral, monthly finance charge (dated month end), paper invoice fee (month end), temporary-increase
  reversion the day after expiry, dormancy closure, returned payment fee trigger. Every seed is checked
  against each of these (no clause may be lit that no task carries).
- Cross-category triggers out of credit: credit_hold_placed / credit_hold_released / credit_reinstated
  trigger vending and safety events (no `when`), so no d1 task tool writes those events. card payments
  trigger a card surcharge charge, so the customer payment tool fixes payment_method=ach_debit.
- DSL constraint recorded: compute reads only the target account, its own ledgers and other categories'
  holdings/ledgers; per-object figures are reached through a stated selection rule (latest payment,
  latest pending request) and every such rule is stated in the policy text with its tie convention.
- User-owned writes that can carry a computed figure: a customer payment and a customer limit request; one
  per task. Tool uuid8 values generated once each with uuid.uuid4().hex[:8]: 2280b564, 4d9f44ce, dcbbb504,
  85fdd39c.

## Task 0 (closed)
- Policies: credit_ext_window_discount_catchup (state_due, 4 factors) and credit_ext_backorder_room_payment
  (on_request, 5 factors). Tools: book_cash_discount_2280b564 (agent), pay_by_bank_debit_4d9f44ce (user).
- Capability cards: discount tool = one discount line on a named invoice (amount, payment reference, payment
  date), receivable lowered, receipt {status, discount_reference, applied_invoice_number, discount_amount,
  ar_balance}; payment tool = one ACH debit received ON-ACCOUNT today, receivable lowered, receipt {status,
  payment_reference, payment_amount, received_date, ar_balance}.
- Revisions: (1) discount rule generalized to every payment (a catch-up must not be cheaper than an ordinary
  discount) -> overwrite replaced_by restated; (2) tax shares varied per statement so the two gross-up methods
  differ on this world; (3) dropped vending restock row (dangling ship_to FK) and order_returns rows (unread),
  added find_ship_to_accounts read; (4) solvability: tool arg renamed applied_invoice_number (blueprint
  action_binding), returned-payment event_type added to evidence; (5) probe found absent-payment crash in
  pa_in_force -> inv_date guard added.
- Gate runs (--task 0): check_task_tools OK, replay OK (58=58), check_solvability OK, check_compute OK
  (134.93 / 2382.95; factor baselines 222.71/269.85/179.90/139.15 and 0/1329.62/1982.95/4182.95/1117.95),
  check_grounding OK, check_extended OK, check_cross_fire OK.
- Prerequisite sensitivity: skipping the discount line -> room payment 2517.88 (vs 2382.95).

## Task 1 (closed)
- Policies: credit_ext_permanent_request_figure (on_request, 4 factors) and credit_ext_permanent_increase_grant
  (on_request, 6 factors, overwrite of the base approval sentence). Tools: submit_limit_request_dcbbb504 (user),
  decide_limit_request_85fdd39c (agent).
- Capability cards: request tool = one pending request (kind, limit) dated today, receipt {status,
  review_reference, request_date, change_type, requested_limit}; decision tool = one decision line on a named
  request, copies requested limit/kind, applies the limit and last review date when approved, receipt
  {status, review_reference, decision, approved_limit, credit_limit}.
- Revisions: (1) pricing agreement moved from Net-Price to Category Contract (a Net-Price contract earns
  quarterly rebates the seed would have to carry); (2) finance-charge history rebuilt so FC-1250930 rests on a
  statement actually open past grace at 2025-09-30; (3) probe: with no pending request the latest decided
  request was read -> req_ref/req_decided guard, rule sentence "and no limit is granted"; (4) probe: no
  invoices raised TypeError -> latest_inv "or 0" and rule sentence for an account with no invoice.
- Prerequisite sensitivity: skipping the request -> grant 0 (latest request already decided) vs 146,575.00.

## XF recipe (audits/render_source/XF_recipe.md) — how each point is met
1. Factor independence: checked binding by binding; no factor binding reads another factor's binding (shared
   selections inv/inv_merch/pay_ref, bo_open, purch12/avg12, req are plain); assembly bindings disc_rate,
   tol_used, room_ceiling, step_used, step_room, result are plain.
2. Assembly stated once generically in each rule ("Every share of the discount rate this rule sets multiplies
   the tier's percentage", "Every amount a schedule in this rule adds ...", "Every percentage point a schedule
   ... adds to or takes from ..."); no factor binding assembles the result.
3. Order: shares multiply the tier percentage before the rate is applied once; tolerance share acts on the tier
   percentage and points are added after; step points are applied before the limit is increased and amounts
   are added after rounding; Q1 amounts are added to the base before percentages multiply.
4. No quantity is defined as another policy figures it; each quantity is defined where used.
5. Overwrites: Q0 retires the flat discount sentence and restates "freight and sales tax never earn a
   discount" for every payment; R1 retires the base approval sentence and restates the on-time test, ceiling
   cap and labels; R0 and Q1 have no base counterpart quantity ([]). No sibling overwrites.
6. compute_basis quotes verbatim: sweep.py (scratch) reports none missing.
7. Rounding sentences match RND: Q0/R0/Q1 round once on the final figure; R1 rounds the step room only.
8. Docstring effects exist in bodies; no docstring carries an example value (formats only).
9. Edges stated and computed: same-day ties of the latest payment/request scoped out in the rules; whole-month
   windows use MONTHS (probes at exactly 12 / 24 / 3 months); zero-division guards stated (ratio of zero,
   at least one month); absent records return nothing (probe tables in plan.md).
10. Filters stated = filters computed (return_credit source, denied resolution, declined/referred decisions,
    active status, finance_charge type, paper fee type, program fee type).
11. Method tiers change shape; pairwise table with distinguishing inputs in plan.md.
12. No cross-record date pairing: per-invoice reads are keyed by the selected invoice number; the agreement
    window is one holding's own dates.
13. Cross-category seeds follow their charters: ship-to backorder value = backorder deltas, StockSmart Weekly
    monthly minimum fee 400.00, VendPoint models/fees from the vending charter, Category Contract commitment =
    tier commitment 75,000.00 (not rebate-eligible, rebate balance 0), return credits are wrong-item route
    pickups (restocking waived, no label fee).
- Revision (XF 11 on task 1's world): the two StockSmart allowance methods coincided (3 x 400 both ways);
  added the 2026-08 par change fee line (12 x 1.00, Weekly Service par_change_fee_usd) so the trailing-fee
  method gives 1,212.00 against 1,200.00; grant re-propagated 146,575.00 -> 146,587.00 in gold, computations,
  traces, tracing and rationale.

## Difficulty-level closure
- Coverage: task 0 = {credit_ext_window_discount_catchup, credit_ext_backorder_room_payment}, task 1 =
  {credit_ext_permanent_request_figure, credit_ext_permanent_increase_grant}; scopes and tools pairwise
  disjoint; every extended policy fires on a gold call. No handoff in gold.
- Final gate block (no --task): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK;
  replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK (suite means
  branches/steps above 4, history max and branch max above floors); check_grounding GROUNDING OK;
  check_cross_fire SCOPE OK; check_cache_diff INFO only (no cache trap designed). Traceability deferred to
  after KB render.
- Runtime constraints: frozen_time strings 'YYYY-MM-DD HH:MM:SS EDT'; task_tools.py has no clock/random/uuid
  tokens and no module-level helper; every write tool calls ctx.create/update itself. Scratch lives only in
  /tmp/d1_credit_account_billing_and_credits_0068/.
INSTANTIATE round 1: gates 7/7 green

## Rework round 2 (audits/policy_task/d1_credit_account_billing_and_credits/ revision_1) — item by item
P1 = window_discount_catchup, P2 = backorder_room_payment, P3 = permanent_request_figure, P4 = permanent_increase_grant.
- F-C1 (P1 tie): compute now counts payment entries on the latest received date (pay_ties) and returns nothing when
  more than one carries it; rule sentence 2 now says the catch-up figure is nothing. Probe: second same-day payment -> 0.
- F-C2 (ties, whole class): P2 sales-tax ratio is taken over ALL invoices dated on the latest invoice date (SUM with
  txn_date = that date); P3 "latest statement" = invoice totals posted on the latest invoice date (summed); P4 counts
  permanent requests on the latest request date and decides nothing on a tie; P1 as F-C1. Probes for each tie in plan.md.
- F-C3 (month-end, whole class): every policy rule now states its whole-month convention, identical to MONTHS():
  "the difference in calendar months, less one when today's day of the month is earlier than that date's day of the
  month, with no move of a month-end date to a shorter month's last day" — covers every count listed (fc12, opened_m,
  ret_n, 12-month windows, ramp-up, paper fees, dec24, rev_m, denied12, open_m, vmi_live, 3-month windows, 1-month
  minimum-fee window). Base gates keep the base's own clamp convention for base counts (review interval,
  certified funds) — the two conventions now govern different quantities and each is stated.
- F-C4 (P1 rounding): left_open and full_rate_disc no longer rounded; the rule says "compared without rounding";
  the only RND is on the final figure.
- F-C5 (P3 filter): lag_days tier 2 now tests per_shipment AND invoice_delivery paper AND paper fees in 12 months.
  Probe: per-shipment email account with paper fees -> 30 days (88,702.02); paper -> 40 days (100,528.95).
- F-C6 (P1 agreements): the contract share reads the customer's single LIVE agreement (status active, else
  renewal_pending; base pricing_agg_multi_holding allows at most one live agreement) and windows the invoice date
  only against that agreement's current term. Probe: an expired Net-Price agreement seeded first is ignored.
- F-C7 (P4 multiplicity): P4 rule now carries "A customer holding more than one active StockSmart program or more
  than one active VendPoint machine is decided outside this rule." (P2 already had its own).
- F-C8 (docstring): submit tool now says "the request is recorded with its decision marked pending and changes nothing
  on the account itself"; decide tool summary and review_reference text no longer say "pending". No before/after/
  first/then/until word in any docstring (grep).
- F-C9 (P1 vs base S4): declared overwrite of the full-balance / pro rata sentence; replaced_by states the full-balance
  test (left open no more than the full-rate discount) and that the merchandise paid for follows the allocation
  schedule, for every payment.
- F-C10 (P1 vs base S5): declared overwrite of the excluded-tier "status active on the invoice date" sentence;
  replaced_by states live agreement + current-term window for every payment.
- F-C11 (P4 dropped branch): compute adds granted / result: an increase above the tier's desk approval amount gives
  0.00 (referred), and the rule restates the in-force sentence. Task 1 sensitivities now show 0.00 for step_start
  and denied-dispute baselines (increases 61,587.00 and 54,087.00 above 50,000.00).
- F-C12 (P4 ladder): step start is now one half / three quarters / the whole of the tier's largest step, monotone
  on every tier (Net 30 Standard probe: 12.5 / 18.75 / 25).
- F-C13 (method, whole class): P1 earning share replaced by payment_allocation_to_merchandise (method: freight and
  tax settled first, MX floor / nothing / whole merchandise — formula shapes differ); P1 discountable merchandise
  relabelled parameter (deduction value); P2 gross-up relabelled parameter (backorder_sales_tax_ratio deciding the
  ratio value) and P2's VendPoint billing made the method (three-month usage history / flat tariff / nothing); P3
  purchase base tier 2 replaced by a blend (latest + average) / 2 for consolidated accounts at 1.2x-1.5x growth,
  window-swap tier removed; P4 StockSmart allowance unchanged (passed). Pairwise table in plan.md.
- T0-1 (seed): the item behind CM-129966 now ships 2026-08-20, so it is billed on the August statement INV-1488081 that
  the memo is applied to; CM-130418's item ships 2026-09-18 (September statement). Near-miss now producible.
- T0-2 / T1-2 (persona): removed "happy for the representative to take care of whatever account work ..." and "whatever
  part of the paperwork has to come from the customer ..."; personas state only the root need and the hand-over of
  their own payment/request when asked; conditional reactions kept. no_user_hint rewritten to match.
- T0-3 (proof): P1 trace rewritten from the recomputation (new value 128.08, raw 128.0841).
- T1-1 (seed): DSP-139507 is now a quantity-shortage dispute the customer withdrew (base allows withdrawal; no memo,
  CM-139507 removed and the December statement payment restored to the full amount; ledger sum unchanged 63,500.00).
- T1-3 (proof): skipped_effect now says the compute returns 0.00 because the latest permanent request is already
  decided.
- Observations closed: ACH-credit payments inside the certified-funds periods converted to wires (task 0: 4 rows
  2026-05-08..06-11; task 1: 3 rows 2025-10-11..11-12); DSP-140812 now resolved 2026-04-17 (seventh business day);
  P1 "carrying" -> "charged"; P1 dispute deduction limited to quantity-shortage / goods-not-shipped disputes; P2
  StockSmart minimum fee counted only when a minimum fee was charged less than one whole month back, and seeded
  monthly minimum fee lines; P2 tolerance used capped at the tier tolerance (the room ceiling never exceeds the base
  hold point); P3 run-rate limited to monthly consolidated accounts; task 0 VendPoint usage bills and cellular fee
  lines seeded (ship_to_id None on non-relocation lines). Left as is (recorded): payments applied to account charges
  are not invoice payments for the discount window (charges carry no merchandise); the ship-to open_backorder_value
  equals the baseline quantity (not a tier stamp); P2's ramp-up test is Corbett's quoting count under the stated
  whole-month convention.
- New gold: task 0 discount 128.08 (was 134.93), room payment 2,550.42 (was 2,382.95), skip-prerequisite 2,678.50;
  task 1 request 191,236.72 (unchanged), grant 149,087.00 approved_reduced (was 146,587.00), skip-prerequisite 0.00.
  Proof text swept in both tasks (computations, tracing, prerequisite_closure, solvability business effects,
  seed_consistency regenerated from the current rows, read objectives/necessities, design_rationale).
- XF recipe re-applied to all four policies: (1) no factor binding reads another factor's binding (P1 result reads
  plain inv_merch; allocation reads plain inv_merch only); (2) assembly in plain bindings, generic sentences;
  (3) order fixed (P1 shares then rate once; P2 share, points, then cap; P4 points before the increase, amounts after
  rounding, desk test last); (4) none; (5) P1 three overwrites, P4 one, each scoped "for every payment / request";
  (6) sweep.py clean; (7) RND only where stated; (8) docstrings checked; (9) ties, month convention, absent records,
  zero division and None guards stated and probed; (10) filters stated = computed (paper delivery added; goods
  dispute reasons; live statuses); (11) pairwise method table; (12) only one live agreement is windowed;
  (13) seeds re-checked row by row (above).
- Gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK; CACHE-DIFF INFO only.
REWORK round 2: gates 7/7 green

## Rework round 3 (audit revision_2: F-C14, F-C15, T0-4)
- F-C14 (XF10 class: rule scoped to one holding, compute summed across holdings). Swept every cross-category
  history read in P1-P4. Members: P2 vend_usage3 and P2 vmi_min_fees. Both now filter to the active holding read by
  the same tier test (vend_mach = CFIELD active machine id -> XSUM ... vending_machine_id=vend_mach; vmi_prog =
  CFIELD active program id -> XCOUNT ... vmi_program_id=vmi_prog), and the rule says "on that active machine alone,
  never on another of the customer's machines" / "was itself, that active program and no other, charged". Not
  members: P2 bo_open (rule: backorders on the customer's ship-tos, all of them), P4 vmi_allow (rule: fees billed to
  the customer's StockSmart programs, all of them), P1 per-invoice reads (keyed by the invoice). Probes: a removed
  second machine with an August usage bill of 900.00 and a closed second program carrying the minimum-fee lines
  are not counted (2,550.42 / 2,150.42).
- F-C15 (P1 S5 overwrite, second reading + realism). The replaced_by / rule sentence no longer says "carries no
  contract share". It now reads the live agreement for an invoice inside its current term (effective date through
  expiration date) and gives the whole rate when the pricing records hold no agreement other than a proposed or
  withdrawn one. When an expired or terminated agreement is on record, or the invoice predates the live
  agreement's current effective date, the catch-up is not made under this rule (figure nothing), so a prior-term
  or ended net-priced invoice can never earn a whole-rate discount. Compute: pa_out_of_scope gates result; pa_end
  reads the expiration date only (a live agreement has no closed date). The other override sentences (P1 S1, S4;
  P4 S4) were re-read for a second reading: none found. Probes: expired agreement also on record -> 0; renewed
  agreement with invoice before the current effective date -> 0; no / proposed / withdrawn agreement -> whole rate.
- T0-4 (XF13 class: every seeded other-category month checked against its charter).
  - Task 0 VendPoint Coil 40 (ramp-up 3; installed 2025-11-03; tested from 2026-03): the June 2026 usage bill is
    raised to 1,318.40, and July 1,412.60, August 1,288.35 and September 1,530.90 are all at or above the 1,250.00
    minimum, so no shortfall fee is owed in any seeded month. The cellular data fee of 15.00 is seeded each month.
    No badge or relocation fees apply.
  - Task 0 StockSmart Weekly Service: the July-September monthly minimum fees of 400.00 each are owed, because no
    replenishment or consumption is billed in those months, so program spend is below the 8,000.00 minimum. No bins
    are above the 800 limit and there are no visits, so no other fee applies.
  - Task 1 (unchanged, not regressed): the StockSmart minimum fees for June-September stand on the same reasoning.
    The 12.00 August par change fee counts changes beyond the 40 included; the bin-change rows behind it are a
    truncated history. The VendPoint Locker 24 reports by ethernet and has no seeded transactions, so no cellular
    fee is owed.
- Proof text regenerated: task 0 contract-share and VendPoint / StockSmart traces, design_rationale (seed and
  overwrite lines), plan.md probe rows; sweep for the June figure, "carries no contract share" and "on the machine"
  found no stale copy outside the regenerated db_closure. Scored values unchanged (128.08, 2,550.42; 191,236.72,
  149,087.00 approved_reduced); sensitivities unchanged.
- XF recipe re-applied: (1) no factor binding reads another factor's binding (the new vend_mach and vmi_prog
  belong to their factors; pa_out_of_scope is a plain scope binding); (2)-(4) unchanged; (5) S5 replaced_by now has
  one reading and names its out-of-scope cases; (6) sweep clean; (7) RND unchanged; (8) docstrings unchanged;
  (9) absent / decoy / tie probes extended (plan.md); (10) the stated holding filters now match the compute;
  (11) pairwise method table unchanged (no method formula changed); (12) one live agreement windowed;
  (13) seeded months re-checked as above.
- Gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK; CACHE-DIFF INFO only.
REWORK round 3: gates 7/7 green

## Rework round 4 (audit revision_3: F-C16, F-C17)
- F-C16 (prerequisite state no write can bring about). The P2 prerequisite sentence (policy_source, condition, task 0
  prerequisite_closure, rationale all regenerated) now reads: "The room payment is worked out only after the
  account's most recent payment carries a discount line on the invoice it is applied to, wherever a catch-up discount
  above nothing is owed for that payment under the prompt-payment discount rule; where none is owed, the room payment
  waits on no discount line." Members (i)-(ix): (i) record share nothing, (ii) contract share nothing (now: a
  net-priced invoice), (iii) short payment on a non-partial tier, (iv) no merchandise, (v) same-date tie, and (ix) a
  zero-day tier all fix the catch-up at nothing, so no line is owed and the room payment proceeds on the receivable
  as it stands. Probe (i): P1 0.00, P2 2,678.50. (vi)/(vii) are gone as outcomes: see F-C17. (viii) older
  in-window payments are outside the sentence, which concerns only the most recent payment, the one P1 books. Other
  edge of the same shape: P4 <- P3 waits on a pending request that the customer's request write always creates
  (P3 never fixes "no request"), so it is not a member.
- F-C17 (no-catch-up branch withheld earned discounts). The branch is removed. The S5 replacement now treats an
  invoice as net-priced, earning no discount (the base outcome for a net-priced invoice), only when it was billed:
  - inside the current term of a live agreement on an excluded tier; or
  - on or after that live agreement's proposal date and before its current effective date (its earlier terms); or
  - from the effective date through the closed date of an expired or terminated agreement on an excluded tier.

  Every other invoice keeps the tier ladder (three quarters inside a live Category or Volume agreement's current
  term, the whole rate otherwise). Compute: pa_prop, pa_prior_net and ended_net (one first-match lookup per excluded
  tier and ended status) replace pa_out_of_scope, and result no longer has a scope gate. The rule names its one
  remaining scope: "A customer whose pricing records hold more than one expired or terminated agreement of the same
  tier and status is worked out outside this rule." This follows the same pattern as the P2/P4 multiplicity scopes.

  Probes:
  - live Category plus an expired Category: 128.08 (discount kept);
  - only an expired Category: 170.78;
  - an expired Net-Price agreement covering the invoice: 0.00;
  - a terminated Net-Price agreement closed before the invoice: 170.78;
  - a renewed live Cost-Plus with a prior-term invoice: 0.00;
  - a renewed live Category with a prior-term invoice: 170.78;
  - a Cost-Plus agreement proposed after the invoice: 170.78.
- Scored values unchanged in both tasks (128.08, 2,550.42; 191,236.72, 149,087.00 approved_reduced) and every
  sensitivity unchanged; task 1 untouched. Proof text touched: task 0 contract-share trace, prerequisite_closure
  (policy_source, condition, why_false, order_uniqueness), design_rationale (tree and overwrite lines), plan.md probe
  rows. Stale-phrase sweep ("every payment received inside", "out of scope", "within this rule's scope") is clean.
- XF recipe re-applied:
  1. The new bindings belong to the contract factor; no factor reads another factor's binding.
  2. Generic assembly sentences are unchanged.
  3. Order is unchanged.
  4. The P2 sentence names a record state (a discount line) and a business rule, not another policy's figure.
  5. The S5 replaced_by has one reading and restates the still-in-force base content (net-priced invoices earn
     nothing).
  6. The basis sweep is clean.
  7. Rounding is unchanged.
  8. Tools are unchanged.
  9. Absent, first-match and date edges are probed.
  10. The filters stated in the rule match the compute.
  11. The method table is unchanged.
  12. The ended-agreement lookup is per tier and status, and duplicates are scoped.
  13. The seeds are unchanged.
- Gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK; CACHE-DIFF INFO only.
REWORK round 4: gates 7/7 green

## Rework round 5 (audit revision_4: F-C18)
- F-C18, members P1 pa_prior_net (proposal-date lower bound) and P1 ended_net (last-term lower bound). Minimal edits:
  - Only the S5 replacement sentence changed, in the rule and in replaced_by. An invoice is net-priced only when it
    is dated inside the current term of a live excluded-tier agreement, or from the effective date through the
    closed date of an expired or terminated excluded-tier agreement. The sentence states that an agreement is in
    effect from the date its pricing takes effect on signing until it ends, and that an invoice dated before an
    agreement took effect keeps the tier rule. The proposal-date reach is gone, so a list-priced invoice billed
    before signing earns its discount.
  - One self-naming scope sentence was added, directly after the existing duplicate-agreement scope. The records keep
    only an agreement's latest term, so an invoice dated before that latest term's effective date of an
    excluded-tier agreement, live or ended, is worked out outside this rule (figure nothing) when the agreement was
    renewed. An agreement counts as renewed when more days than the tier's proposal validity separate its proposal
    date from that effective date. When those dates are no further apart, the latest term is the first, and the
    earlier invoice is a pre-signing invoice that keeps the tier rule.
  - Compute: pa_prior_net is replaced by the plain scope binding pa_prior_unknown, ended_prior_unknown (per excluded
    tier and ended status) is added, and result gates on both. ended_net is unchanged. The contract factor's bindings
    and ladder text are updated. Every other sentence keeps its wording and order.
  - Under the room payment's prerequisite sentence, an out-of-rule invoice owes no catch-up, so the room payment
    waits on no line.
- Window-edge probes (plan.md):
  - Live Net-Price, first term: an invoice the day before signing gets 170.78; an invoice on the day of signing gets
    0.00.
  - Expired Net-Price: an invoice on the day the agreement ended gets 0.00; an invoice the day after the end gets
    170.78.
  - Terminated first-term Net-Price, invoice before signing: 170.78.
  - Renewed live or terminated Net-Price, earlier invoice: 0 (outside the rule).
  - Renewed live Category, earlier invoice: 170.78.
- Scored values unchanged (128.08, 2,550.42; 191,236.72, 149,087.00 approved_reduced) and sensitivities unchanged.
  Proof text touched: the task 0 design_rationale overwrite line and the plan.md probe rows. The sweep for
  "proposal date" and "earlier terms" in the task proof text is clean.
- XF recipe re-applied:
  1. No factor reads another factor's binding; the new scope bindings are plain and feed only result.
  2-4. Unchanged.
  5. The S5 replaced_by has one reading and restates the base content: net-priced invoices earn nothing.
  6. The basis sweep is clean.
  7-8. Unchanged.
  9. Window edges at signing and at the end are probed; absent dates are guarded.
  10. The filters match the rule.
  11. The method table is unchanged.
  12. Agreement terms that cannot be seen are scoped by a self-naming sentence.
  13. Seeds are unchanged.
- Gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK; CACHE-DIFF INFO only.
REWORK round 5: gates 7/7 green

## Rework round 6 (audit revision_5: F-C18(c), F-C19; coordinator route-around)
- Stopped reconstructing agreement history. P1 is narrowed by one self-naming scope sentence, which replaces the two
  earlier scope sentences (duplicate ended agreements; earlier terms of renewed agreements): "This rule covers only
  an invoice dated inside the current term of the customer's single Contract Pricing Agreement, from its effective
  date through its closed date or, with no closed date, its expiration date, and an invoice of a customer with no
  agreement on record; every other invoice remains under the base cash-discount rule."
  - No out-of-scope case is given a figure of nothing any more. The pa_prop, pa_prior_unknown, ended_net and
    ended_prior_unknown bindings are removed, and result no longer has a scope gate.
  - The scope works as a write gate, like the P2/P4 multiplicity scopes: outside it no catch-up line is booked under
    this rule, so P2's sentence waits on no line.
- F-C18(c) mid-term tier change: inside the scope the contract share follows "the tier recorded on the customer's
  agreement". This is base's own reading (BLUEPRINT-KNOWN, logged by the coordinator); no stricter reading is
  invented.
- F-C19: all three P1 replaced_by sentences now name the rule's scope ("For a payment on an invoice within this
  rule's scope ...") and restate the in-force base content for every other invoice (XF 5):
  - S1: the tier percentage on the merchandise subtotal, never on freight or tax.
  - S4: the full balance less the discount, or pro rata on partial-payment tiers.
  - S5: no discount under an excluded-tier agreement active on the invoice date.

  The contradiction between rule sentences 4 and 9 is removed by construction, because sentence 9 is gone. Every
  other sentence keeps its wording and order. The one exception is "of a live Corbett Category Contract", which
  becomes "of a Corbett Category Contract", because the scope already fixes the agreement.
- Compute: the contract factor reads the single agreement (CFIELD with no status filter; end = closed date or
  expiration date). The cross_category reads and note, the factor ladder text and the basis quotes are updated.
- Window-edge probes for the scope sentence (plan.md):
  - term starting on the invoice day: in scope, 128.08;
  - term starting the day after the invoice: out of scope, base rule;
  - agreement ended on the invoice day: in scope, 128.08;
  - agreement ended the day before the invoice: out of scope;
  - Net-Price in term: 0.00 (net-priced);
  - no agreement on record: 170.78;
  - a second, ended agreement on record: out of scope;
  - renewal_pending agreement: 128.08;
  - Cost-Plus in term: 0.00.
- Scored values unchanged (128.08, 2,550.42; 191,236.72, 149,087.00 approved_reduced), sensitivities unchanged, task 1
  untouched. Proof text touched: task 0 contract-share trace, design_rationale overwrite line, plan.md probe rows
  (stale round 4/5 rows removed).
- XF recipe re-applied:
  1. No factor reads another factor's binding.
  2-4. Unchanged.
  5. Every replaced_by names its scope and restates the base content.
  6. The basis sweep is clean.
  7-8. Unchanged.
  9. Window edges probed.
  10. The filters match the rule.
  11. The method table is unchanged.
  12. Only the single agreement is windowed.
  13. Seeds unchanged.
- Gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK; CACHE-DIFF INFO only.
REWORK round 6: gates 7/7 green

## Rework round 7 (audit revision_6: F-C6 reopened, F-C20; coordinator lines)
- F-C6 (XF12). P1 again reads the live agreement by status, as rounds 2-5 did: active, else renewal_pending (pa_tier,
  pa_eff, pa_end). The scope binding live_n counts the live rows exactly, by status (active plus renewal_pending).
  The pricing charter allows at most one live agreement at a time, so two same-status live rows cannot occur.
  A customer with no live agreement, or with more than one, is out of scope (base figure). Ended rows never decide
  in-scope reads. Probe: an ended Net-Price row listed first plus a live Category gives 128.08 (live row read).
- F-C20 (scope only in the rule). The scope sentence is now rule and compute at once: "This rule covers only an
  invoice dated inside the current term ... of the customer's live Contract Pricing Agreement, meaning its one
  agreement whose status is active or renewal pending; for every other invoice, including any invoice of a customer
  with no live agreement or with more than one, the catch-up line carries exactly the base cash-discount rule's
  figure: [tier percentage of merchandise for a full payment; pro rata by payment / invoice total for a partial
  payment on a partial tier; nothing for a short payment on any other tier or for an invoice inside the term of an
  ended excluded-tier agreement], rounded to the nearest cent."
  - Compute: in_scope = live_n == 1 and pa_in_force; base_excluded, base_share and base_figure implement the base
    figure; result = extended formula in scope, base_figure otherwise; ties and no-merchandise stay nothing.
  - One reading: the rule, the compute, the three replaced_by sentences ("every other invoice remains under the base
    cash-discount rule") and P2's sentence ("a catch-up ... above nothing ... owed") now agree. Out of scope, a line
    is owed whenever the base figure is above nothing.
- Same class in the other policies (rule-only scope sentences). P2 and P4 multiplicity sentences are now computed.
  - multi_holdings = active programs on more than one tier, or active machines of more than one model (EXISTS per tier
    and per model).
  - Outcomes: P2 counts the StockSmart and VendPoint billing as nothing, and P4 adds neither allowance.
  - Several active programs of one tier, or machines of one model, are read as "the one the customer's records list
    first", which is the CFIELD order and the finder's listing order. The DSL has no holding-count primitive, so this
    is the exact computable rule.
  - P3 has no scope sentence.
- Probes (plan.md):
  - P1: no agreement, two live rows, or an invoice before the live term each give 371.07 (base figure).
  - P1: no live agreement with a terminated Cost-Plus covering the invoice gives 0 (base: net-priced).
  - P1: no agreement with a short payment on a non-partial tier gives 0.00.
  - P2: a second active program on another tier, or a second active machine of another model, gives 724.80
    (billing nothing); a second program of the same tier gives 2,550.42 (first read).
  - P4: a second active machine of another model gives 147,500.00; a second program of the same tier gives
    149,087.00.
- Scored values unchanged (128.08, 2,550.42; 191,236.72, 149,087.00 approved_reduced) and sensitivities unchanged.
  Proof text touched: the task 0 contract-share trace, the design_rationale overwrite line, and the plan.md probe rows
  (round 6 rows replaced).
- XF recipe re-applied:
  1. Factor bindings read no other factor's binding; the new scope and base bindings are plain.
  2. The assembly sentences are unchanged.
  3. Order: scope is decided first, then one formula.
  4. Unchanged.
  5. The replaced_by sentences and the scope sentence agree, and the base content is restated.
  6. The basis sweep is clean.
  7. RND only on the final figures (base figure and extended figure).
  8. Unchanged.
  9. Absent, first-match and tie cases are probed.
  10. Every stated filter and scope is computed.
  11. Unchanged.
  12. One live agreement, counted by status.
  13. Seeds are unchanged.
- Gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK; CACHE-DIFF INFO only.
REWORK round 7: gates 7/7 green

## Rework round 8 (audit revision_7: F-C21, F-C6b, F-C22; coordinator route)
- F-C22 (joint multiplicity zeroing and first-listed reads in P2/P4). Removed every per-holding read
  (vmi_tier/vmi_prog/vend_inst/vend_cell/vend_mach in P2; vmi_live/vend_model in P4), both multi_holdings bindings,
  the "more than one tier / model" sentences and every "first listed" reading. Each figure is now an aggregate over
  the customer's event rows across every program or every machine, read with XSUM/XCOUNT, standing on its own
  records and not gated on the other product.
  - P2 StockSmart billing still to post: the onsite management fees plus the monthly minimum fees charged in the last
    whole month, or the minimum fees alone when no onsite fee was charged, or nothing.
  - P2 VendPoint billing (method): the three-month usage across all machines divided by three, plus last month's
    cellular fees; or the cellular fees alone; or nothing.
  - P4 StockSmart allowance (method): the history sum of fees across programs over three whole months when a fee is
    dated two whole months back; otherwise three times last month's fees; otherwise nothing.
  - P4 VendPoint allowance: last month's usage across all machines, in whole when at least 3,000.00, one half when
    above nothing, or nothing.
  - Task 1 seed: VendPoint usage bills for VP-116052 were added (2026-08-31 812.40, a near-miss outside the month, and
    2026-09-30 750.00). Both are at or above the Locker 24 minimum of 750.00 and the machine is on ethernet, so no
    fee is owed. A find_vending_transactions read was added and the steps shifted (computations,
    solvability steps, prior_step, temporal step, tracing text).
- F-C21 and F-C6b (P1 out-of-scope exclusion). The base figure's exclusion now reads exactly as rule sentence 4
  restates base S5: "an invoice billed under an agreement on a cash-discount-excluded pricing tier whose status is
  active on the invoice date". On the records this is the customer's live agreement, recorded on such a tier with
  status active, the only status and tier the records hold. This is base's own reading (BLUEPRINT-KNOWN), and ended
  agreements are not read at all.
  - Compute: base_excluded = EXISTS active AND that agreement's recorded tier is excluded. The six ended-agreement
    first-match lookups are removed.
  - Auditor's renewed example (live Net-Price, current term effective 2026-10-01, prior-term invoice): rule sentence
    4, sentence 8 and the compute all give nothing (probe 0).
- Probes (plan.md, rows for rounds 3 and 7 replaced):
  - P1 renewed live Net-Price prior-term invoice: 0.
  - P1 the same agreement in renewal_pending: 371.07 (base figure; base reads status active).
  - P1 only an expired Net-Price covering the invoice: 371.07 (ended rows not read).
  - P1 two expired Net-Price rows plus a live Category: 128.08.
  - P2 two machines of one model, or of different models: 3,005.42 (both counted).
  - P2 two programs of one tier: 2,950.42.
  - P4 two machines of one model: 149,537.00.
  - P4 two programs of one tier: 149,487.00.
  - P4 fees only in the last whole month: 149,075.00 (projection).
  - Absent lines give the baseline figures.
  - 3,500.00 of usage last month: whole usage added, then a desk referral, so 0.
- Scored values unchanged: 128.08, 2,550.42; 191,236.72, 149,087.00 approved_reduced. Every factor sensitivity and
  all-baseline figure is unchanged. Proof text regenerated:
  - task 0 StockSmart / VendPoint traces, sensitivity tier labels, read necessities, payment tracing and rationale;
  - task 1 allowance traces, sensitivity tier labels, read necessities, approved-limit tracing and rationale;
  - plan.md probe and method tables.

  The sweep for "the only active", "ramp-up", "first listed", "Locker 24 minimum" and "records list first" is clean.
- XF recipe re-applied:
  1. Factor bindings read no other factor's binding, and no factor is gated through another product.
  2. Assembly sentences unchanged.
  3. Order unchanged.
  4. No "as another policy figures it".
  5. P1 sentence 4 and sentence 8 now state the same exclusion.
  6. Basis sweep clean.
  7. RND unchanged.
  8. Tools unchanged.
  9. Absent lines, month windows and the ties already covered are probed.
  10. Stated scopes and filters equal the compute.
  11. Method pairs are distinct: history sum against projection; history average plus fees against fees alone.
  12. No first-match read of a non-unique holding remains. The only CFIELD reads left are the live pricing agreement,
      which is unique by the pricing charter.
  13. Seeded months were re-checked against the vending charter.
- Gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK; CACHE-DIFF INFO only.
REWORK round 8: gates 7/7 green

## Rework round 9 (revision_8 F-C23, all three members; round-8 all-holdings aggregation from event rows kept)
- P2 vendpoint_month_end_billing (method): four tiers that are different formulas over the aggregated usage
  (u0/u1/u2 = usage billed less than one / one / two whole months back across all machines, c = last month's
  cellular fees across all machines): trend projection u0 + (u0 - u1) + c when usage was billed in each of the three
  months and rose each month; three-month average (u0 + u1 + u2) / 3 + c when usage was billed two whole months back
  otherwise; latest-month selection (u0, else u1) + c when usage was billed only within the last two whole months
  (new machines); nothing when no usage was billed in three whole months (dormant machines). Cellular fees moved inside
  the usage tiers, so the nothing tier differs from every other tier wherever cellular fees are charged. Rule sentence,
  compute_basis quotes and ladder rewritten; pairwise table (six pairs) and probes in plan.md.
- P2 stocksmart_month_end_billing (parameter): former whole / half / nothing ladder whose nothing rung equalled one
  half of zero is now a real share ladder over the recurring fees charged last month: whole when such fees were
  charged in each of the three months, one half in exactly two, one quarter otherwise (K quarter_share 25 added).
- P4 stocksmart_program_allowance (method): fee history (fees billed across programs in the last three whole months)
  / minimum commitment (no fee in that time but an active program: three times the largest monthly minimum fee among
  the active programs, tier parameter read through CPARAM per tier) / nothing only with no active program and no fee.
  cross_category reads now list vmi_programs.status and variant_name.
- P4 vendpoint_model_allowance (parameter): nothing rung replaced by a real rung: whole at 3,000 or more, one half
  at 500 to under 3,000 (K vend_half_usage 500), one quarter under 500 (K vending_quarter_share 25).
- Drawn counts unchanged (P2 5, P4 6); scored values unchanged (2,550.42; 149,087.00); every sensitivity unchanged.
  Proof text regenerated for the tier labels / traces / necessities / rationale cards of the four factors (task 0:
  StockSmart whole share because fees were charged in each of the three months, VendPoint not rising so the average;
  task 1: fee history vs minimum commitment 1,200.00; VendPoint half rung bounds).
- Probes (scratch, /tmp/d1_credit_account_billing_and_credits_0068/r2/probe9_out.txt): VendPoint rising 2,751.60 /
  Aug+Sep only 2,670.70 / Aug only 2,428.15 / dormant with cellular 1,124.80; StockSmart two months 2,350.42 / onsite
  fee 2,800.42 / one month 2,250.42 / none last month 2,150.42 / decoy emergency visit unchanged; P4 no fee with active
  program 149,075.00 / paused 147,875.00 / no program 147,875.00 / closed with fees 149,087.00 / last month only
  148,275.00 / two active programs 149,075.00 and 0 (2,250 allowance, increase above desk authority) / VendPoint 3,200
  -> 0 (referred) / 400 -> 148,812.00 / none 148,712.00.
- XF recipe re-applied: 1-2 (each factor reads only its own aggregates; assembly in result only), 6 (basis sweep
  clean), 7 (rounding unchanged), 9 (absent records: no usage / no fee / no active program branches stated and
  probed; CPARAM None guarded), 10 (filters: recurring fee types, active status stated and computed), 11 (pairwise
  table), 13 (seed rows unchanged).
- Gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK; CACHE-DIFF INFO only.
REWORK round 9: gates 7/7 green

## Rework round 10 (revision_9 F-C23, last member: P4 stocksmart_program_allowance fall-through vs tier 1)
- The fall-through "nothing" (no fee billed, no active program) equalled the fee-history formula (0 with no fee) on
  its whole domain. Replaced by one month's minimum commitment: the largest monthly minimum fee among the customer's
  enrolled, paused or terminating StockSmart programs (per-tier CPARAM with status filters, binding vmi_idlefee;
  nothing only as that formula's empty input, stated in the rule). Only the fall-through clause of the P4 StockSmart
  sentence changed (rule and its compute_basis quote), plus the ladder tier text, bindings list and cross_category
  note; every other sentence keeps its wording and order.
- Pairwise test (every tier's formula on every other tier's domain) tabled in plan.md with an input from each tier's
  own domain: A vs B 1,212 vs 1,200 / 0 vs 1,200; A vs C 1,212 vs 400 / 0 vs 400; B vs C 1,200 vs 150 / 0 vs 400.
- Probes (scratch, r2/probe10_out.txt): gold 149,087.00; paused with fees 149,087.00 (A); no fee + active 149,075.00
  (B); + paused Monthly 149,075.00; no fee, program paused / enrolled / terminating 148,275.00 (C 400); paused Weekly
  + enrolled Twice-Weekly 148,625.00 (C 750); only closed / none 147,875.00.
- Scored values unchanged (128.08 / 2,550.42 / 191,236.72 / 149,087.00); every sensitivity unchanged; task proof
  text needed no change (task 1 takes tier A; its trace compares tier B only). Round-9 plan probe row for the paused
  program marked superseded.
- XF recipe re-applied: 1-2 (factor reads only its own fee rows and program tier parameters; assembly unchanged),
  6 (basis sweep clean), 9 (absent record: no program / only closed program -> empty input, probed), 10 (status
  filters enrolled / paused / terminating stated and computed), 11 (pairwise table), 13 (no seed change).
- Gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK; CACHE-DIFF INFO only.
REWORK round 10: gates 7/7 green

## Rework round 11 (revision_10 F-C23: P4 stocksmart_program_allowance tier 2 vs fall-through, swapped multiplier + filter)
- Way out (1) taken: the three tiers re-shaped so every pair differs in operation structure (what is combined), not
  in a multiplier, window, constant or status filter. A (a program fee dated two whole months back, established
  billing): S3, the billed program fees of the last three whole months. B (none that far back, fees within the last
  two whole months, new billing): S2 + m, fees billed to date plus one month's forward minimum commitment. C (no fee in
  three whole months): 3 x m, the commitment projection. m = largest monthly minimum fee among ACTIVE programs only.
- Realism note closed: the one-month reserve on enrolled / paused / terminating programs is gone; a paused program
  (minimum prorated away by the vmi charter) carries no commitment reserve.
- Only the P4 StockSmart sentence changed (rule and its compute_basis quote), plus its compute bindings (vmi_m2,
  vmi_fee2, vmi_n2 added; vmi_n3, vmi_idlefee dropped), ladder text, bindings list and cross_category note; every
  other sentence keeps its wording and order.
- Structural pairwise table with each tier's operation structure written out, plus distinguishing inputs from both
  tiers' domains for all three pairs, in plan.md (round 11).
- Probes (scratch r2/probe11_out.txt): gold 149,087.00 (A 1,212); Jul fee 250 148,937.00 (A); Aug + Sep only
  149,087.00 (B 812 + 400); Sep only 148,675.00 (B 400 + 400); B with program closed 148,687.00; no fee + active
  149,075.00 (C 1,200); + Twice-Weekly active 0 (C 2,250, referred); no fee with paused / enrolled / terminating /
  closed / no program 147,875.00.
- Scored values unchanged (128.08 / 2,550.42 / 191,236.72 / 149,087.00), every sensitivity unchanged; task 1 proof
  text regenerated for the tier names (billed-fee sum because a fee is dated 2026-07-31, two whole months back;
  commitment projection 1,200.00 as the comparison) in the necessity, factor trace, tier_taken and rationale card.
- XF recipe re-applied: 1-2 (factor reads only its fee rows and active tier parameter; assembly unchanged), 6 (basis
  sweep clean), 9 (window edges "two whole months before today" = XCOUNT within 3 minus within 2; no active program
  -> m = 0 stated), 10 (active-only filter stated and computed), 11 (structural table), 13 (no seed change).
- Gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK; CACHE-DIFF INFO only.
REWORK round 11: gates 7/7 green

## Rework round 12 (revision_11 F-C23, sole member: P2 vendpoint_month_end_billing trend tier vs three-month average)
- Under the auditor's normalised-shape test (any aggregate of one field = one input; constant weights ignored) the
  trend u0 + (u0 - u1) and the average (u0 + u1 + u2) / 3 were the same combination of the same windowed sums.
  Only the trend tier re-shaped: it is now a floored trend projection, the larger of the latest month's usage plus its
  rise and the largest monthly minimum usage among the customer's active VendPoint machines (model tariff
  min_monthly_usage_usd, per-model CPARAM with status active; binding vend_floor), plus last month's cellular fees.
  A floor (max) and a tariff input now separate it from the average and from the latest-month pick.
- Only the trend clause of the VendPoint sentence changed (rule and the compute_basis quotes carrying it), plus the
  vend_floor binding and basis, the ladder text, bindings list and the vending cross_category reads/note; every other
  sentence keeps its wording and order.
- All pairs of the factor re-checked under the same rule in plan.md (round 12): T1/T2, T1/T3, T2/T3 pass on shape;
  T4 (nothing) vs T1 passes (T1 = floor + cellular on T4's domain), vs T2/T3 passes (cellular fee).
- Probes (scratch r2/probe12_out.txt): gold 2,550.42 (average); rising with Aug 1,450 2,751.60 (trend above floor);
  rising 300/500/600 2,389.80 (floor 1,250); same with the machine suspended 1,839.80 (no active floor); same with an
  active Coil 60 added 3,139.80 (floor 2,000).
- Scored values unchanged (128.08 / 2,550.42 / 191,236.72 / 149,087.00), every sensitivity unchanged; task 0 proof
  text: the factor-trace comparison renamed to the floored trend projection (larger of 1,773.45 and the Coil 40
  minimum 1,250.00).
- XF recipe re-applied: 1-2 (factor reads only its usage / cellular rows and the active machines' tariff; assembly
  unchanged), 6 (basis sweep clean), 9 (no active machine -> floor 0 stated as "largest ... among active machines",
  probed), 10 (active-status filter stated and computed), 11 (normalised-shape table), 13 (no seed change).
- Gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK; CACHE-DIFF INFO only.
REWORK round 12: gates 7/7 green

## Rework round 13 (renderer source scan render_r1.md, P1 credit_ext_window_discount_catchup binding ownership)
- Finding 1 (in_scope read pa_in_force, a contract_share_of_rate binding): inv_date, pa_eff, pa_end, pa_in_force moved
  to the plain set; the factor keeps [pa_tier, contract_share]. Their compute_basis quotes already pointed at the
  plain scope sentence.
- Finding 2 (base_share read pay_amt, inv_total, left_open, full_rate_disc of payment_allocation_to_merchandise):
  pay_amt, inv_total, applied_out, returned_in, left_open, full_rate_disc moved to the plain set; the factor keeps
  [inv_freight_tax, paid_merch]. New plain sentence after the payment-concerned sentence: "The payment amount is the
  amount of the payment concerned applied to the invoice concerned, and the invoice total is the total of the invoice
  concerned." The left-open sentence split at its colon: plain definition "What is left open on the invoice is ...
  compared without rounding with the tier's prompt-payment discount percentage of the invoice's merchandise
  subtotal." then the allocation ladder as its own sentence "When more is left open than ...". compute_basis quotes
  for pay_amt, inv_total, applied_out, returned_in, left_open, full_rate_disc re-pointed at the new plain sentences;
  paid_merch quote follows the capitalised ladder sentence. Every other sentence keeps its wording and order.
- Mechanical sweep (scratch r2/own.py) of all four policies: no plain binding reads (directly or through plain
  bindings) a factor-internal binding; no binding listed under two factors; factor outputs are read only by the
  assembly bindings. Compute expressions untouched.
- Values identical: P1 128.08 (222.71 / 256.17 / 170.78 / 132.10; all-baseline 612.50), P2 2,550.42, P3 191,236.72,
  P4 149,087.00, every sensitivity unchanged. Proof text names no moved binding (values only); nothing regenerated.
- XF recipe re-applied: 1-2 (shared selections plain and stated once; each factor holds only what it alone uses), 5
  (overwrite replaced_by texts unchanged, verbatim), 6 (basis sweep clean), 7 (RND unchanged), 9-10 unchanged.
- Gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK; CACHE-DIFF INFO only.
REWORK round 13: gates 7/7 green

## Rework round 14 (KB audit _verdict.md SRC-2, SRC-3, SRC-4; seed-only; credit.extended.yaml 96e73223486d52f3 and task_tools.py ab50360b67d22456 byte-identical)
- SRC-2 (task 1, gold-moving): the StockSmart par_change_fee row (12.00, quantity 12, 2026-08-31) implied 52 par-change entries that no bin record shows; the most realistic consistent world has no such fee, so the row is removed. Gold follows: StockSmart billed-fee sum 1,200.00, step room / granted 149,075.00 approved_reduced, increase 49,075.00 within desk authority; sensitivities 0 / 139,075.00 / 0 / 144,075.00 / 147,875.00 / 148,700.00 (all-baseline 150,000.00). Request figure 191,236.72 unchanged.
- SRC-3 (task 0): order_returns rows added behind both return credit memos: RMA-1529966 (SO-1824380 line 1, 5 x 148.43) and RMA-1530418 (SO-1825117 line 2, 3 x 620.00), each authorized (route pickup) and received unopened with reason wrong_item_shipped. On the Route Delivery level a Corbett-error return carries no restocking or label fee and is credited in full, matching CM-129966 742.15 and CM-130418 1,860.00 (issued within 3 business days of receipt); this keeps the catch-up at 128.08 and is as realistic as a customer-reason return.
- SRC-4 (both tasks): StockSmart monthly minimum fees for every month since go-live; VendPoint usage bills for every month since installation (and VP-118204's cellular data fee each month), split to the machine's single cost center as the models' cost-center billing requires, with vending_item_issued lines behind every bill (badges within the included users and the daily vend limit; ramp-up months untested; every tested month at or above the model minimum, so no shortfall fee); order lines (booked + shipped) behind every monthly consolidated statement, which bills the month's shipments plus StockSmart fees and VendPoint usage and fees as merchandise. Missing booking rows of SO-1824380 / SO-1825117 added. Task 0 statement freight is now the Tool Room's 12.95 standard freight per parcel order under 150.00 (route freight free), with tax absorbing the difference so totals and freight-plus-tax stay as billed; INV-1488218 freight 25.90 / tax 4,748.64 moves the room payment's tax ratio to 0.07753 and the room payment to 2,619.61 (all sensitivities regenerated: 0 / 1,497.09 / 2,219.61 / 4,419.61 / 1,193.99; 2,747.69 without the discount line). Ship-to last order dates match the latest booked lines (task 1 gains an order booked and shipped 2026-10-09).
- Closure: find_order_returns (task 0) and find_order_lines (task 1) reads added before the writes; computations, gold_actions, temporal_feasibility and every step reference in the proof text moved +1 (discount 14 / payment 16; submit 14 / decide 16); stale step references in two base-invariant cards corrected.
- Proof text regenerated from the evaluator (expected values, gold arguments, factor traces, sensitivities, tracing, rationale cards, cross-row descriptions, read objectives); sweep for 2,550.42 / 2,150.42 / 4,350.42 / 1,124.80 / 15,532.13 / 4,455.94 / 318.60 / 43,393.21 / 2,678.50 and 149,087 / 139,087 / 144,087 / 148,712 / 1,212.00 / par change: none left. Personas unchanged and consistent with the seeds.
- No added row lights a state_due obligation or leaves a write due on the call day (all fees through September posted, returns received and credited, shipments invoiced in their month, the 2026-10-09 shipment billed on the October statement).
- Probe tables re-run (scratch r2/probe8..12_r14_out.txt): tiers and distinguishing inputs unchanged; values shift by +69.19 (room payment) and -12.00 (limit-grant rows that carried the par change fee).
- Hashes verified: credit.extended.yaml 96e73223486d52f3, task_tools.py ab50360b67d22456.
- Gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; CACHE-DIFF INFO only.
REWORK round 14: gates 7/7 green
