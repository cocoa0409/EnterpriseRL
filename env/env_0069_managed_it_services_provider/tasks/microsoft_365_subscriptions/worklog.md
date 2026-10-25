# microsoft_365_subscriptions worklog

## Step 0 — draws
draw_counts.py --tasks 2:
- task 0: prerequisite_problems=2, factor_counts=[4, 6, 4] -> reduction credit 4, late charge 6, payment arrangement 4
- task 1: prerequisite_problems=2, factor_counts=[4, 6, 5] -> seat partial charge 4, admin fee 6, window cancellation 5

## Step 1/2 — policies and tools
- Six extended policies written (licensing.extended.yaml generated from scratch spec; base section copied verbatim).
- check_extended (no tasks yet): only cardinality/coverage red, policy structure clean.
- Tools (uuid8 one per tool): post_reduction_credit_23f8ed2c, assess_late_charge_e02563fc,
  pay_arrangement_instalment_a0d5f2e9 (user), post_admin_fee_5104ae31, post_seat_addition_charge_bba679a2,
  cancel_subscription_in_window_d46a60fb (user). check_task_tools: TASK TOOL CONTRACT OK.
- Revision: cancel tool gained customer_id (the verified_contact gate binds identity_verifications.customer_id to an
  action argument named customer_id); module-level invoice helper moved into a class static method (validator rule).

## Step 3/5 — handling-time recomputation (calc via check_compute engine, gold replayed)
- T0: reduction credit 880.25 (baseline 780.56), late charge 21.66 (baseline 41.55), first instalment 729.10 (baseline 955.47).
- T1: admin fee 3.55 (baseline 67.50), seat partial charge 257.66 (baseline 269.28), cancellation refund 1884.41 (baseline 1773.90).
- Every factor substitution moves result (see computations[].factor_sensitivity in each task).

## Task 0 — closed (per-task gates)
- Revisions: replay red on empty-string foreign keys (managed_billing.managed_seat_change_id='') -> root cause: empty *_id
  fields seeded/written as '' -> seeds drop empty id fields, tools no longer write empty id fields; reduction-credit
  compute used only LATEST so the history floor failed -> licenses removed now read by SUM over the reduction's own
  submission moment (rule sentence added); credited_days treats a missing source id as no source.
- Gates --task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Values: credit 880.25, late charge 21.66, first instalment 729.10.

## Task 1 — closed (per-task gates)
- Revisions: replay closure mismatch (10 TimeBank ledger/billing rows no gold read touches) -> dropped those rows; the
  TimeBank block holdings (active 20-Hour Block 14.5 h, expired 2024 decoy) stay. Seat-charge compute reads the licenses
  added by SUM over the addition's own submission moment (history floor), rule sentence added.
- Values: admin fee 3.55, seat partial-cycle charge 257.66, cancellation refund 1884.41.

## Difficulty-level closure
- XF sweeps (scratch): no factor id is a substring of a tool name; every compute_basis quote is verbatim in its rule;
  task_tools.py free of datetime/time/random/uuid/secrets; only class-static helper; frozen_time 'YYYY-MM-DD HH:MM:SS EDT'.
- validate_scenario: only 'required document not found' (KB not yet rendered).
- Final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (branches mean 41.50, steps
  15.00, history_rows_max 12, branches_max 44), GROUNDING OK, SCOPE OK; CACHE-DIFF INFO.
INSTANTIATE round 1: gates 7/7 green

## Round 2 rework (audit audits/policy_task/microsoft_365_subscriptions, revision_1)

### Probe table — every CFIELD / CPARAM / first-match / LATEST / XSUM read (scratch copies of each step's handling-time world)
| policy | probe (decoy / absent / edge) | scratch result | rule tier that settles it |
|---|---|---|---|
| reduction_credit | decoy: closed ClearPath Premier agreement added | change_fee=0.0; result=880.25 | fee tier 1 (active Standard) still; vcio from the active agreement |
| reduction_credit | absent ClearPath agreement | review_pct=0; result=835.0 | fee fall-through 25.00; review 'no active ClearPath' -> 0 |
| reduction_credit | zero vCIO: tier switched to Monitor | review_pct=0; result=850.0 | fee tier 2 (10.00); review 'no vCIO review' -> 0 |
| reduction_credit | source named, record absent | prorated=805.5616438356165; result=875.7 | anchor fall-through (standard prorated 805.56) |
| reduction_credit | LATEST decoy: older 2024 reduction (seeded) | red_at=2026-08-12 16:30; result=880.25 | latest submission moment 2026-08-12 16:30 chosen |
| late_charge | decoy: cancelled ClearPath Premier | min_charge=35.0; result=21.66 | minimum tier 2 (35.00) from the active Standard |
| late_charge | absent ClearPath agreement | min_charge=25.0; result=17.14 | minimum fall-through late_fee_minimum_usd 25.00 |
| late_charge | LATEST decoy: 2024 / 2025 cycle invoices (seeded) | inv=INV-024118; result=21.66 | latest cycle charge INV-024118 chosen |
| late_charge | date edge: 30 days past due | month_share=1.0; result=29.53 | accrual tier 1 at d=30 -> 30/30 = 1 (meets the fall-through only here) |
| payment_arrangement | decoy: closed ClearPath Enterprise (9 renewals) | n_instal=6; result=819.68 | count tier 1 (6) from the active agreement; dedicated manager not taken from the closed one |
| payment_arrangement | absent ClearPath agreement | late_upfront=21.66; result=1338.55 | count fall-through 3; late tier 2 (no DAM tier held) -> up front |
| payment_arrangement | zero: no late charge this month | late_upfront=0; result=802.53 | late fall-through: nothing set aside |
| admin_fee | decoy: Sentinel cancelled (XDR, ITDR true) | upkeep=0.5; result=3.92 | upkeep tier 2 (0.50): no active Sentinel |
| admin_fee | decoy: closed Continuum DRaaS plan | bundle_pct=95.0; result=3.55 | bundle tier 2 (95) from the active plan |
| admin_fee | absent ClearPath agreement | cover_pct=100; result=7.1 | coverage fall-through 100 |
| admin_fee | edge: held 30+ days, suspended 2026-09-20 | month_part=0.6333333333333333; result=22.48 | held tier 2: (30 - 11)/30 |
| seat_partial_charge | decoy: second active block with 3.0 h (F4 case) | tb_hours=17.5; result=257.66 | hours tier 1 (2.00): 17.5 h across blocks |
| seat_partial_charge | LATEST decoy: earlier seat addition 2026-09-29 | add_qty=4.0; result=257.66 | latest seat addition (4) charged |
| seat_partial_charge | covered: ClearPath Standard | covered_work=True; result=249.66 | no provisioning fee (covered work) |
| seat_partial_charge | absent hours ledger | prov_fee=6.0; result=273.66 | hours fall-through 6.00 |
| window_cancellation | decoy: cancelled Continuum Backup Plus | deprov_rate=1.0; result=1884.41 | deprov tier 2 (1.00) from the active Standard plan |
| window_cancellation | absent ClearPath agreement | admin_return=0; result=1880.86 | admin return fall-through 0; work charges kept |
| window_cancellation | covered: ClearPath Standard | covered_work=True; result=1939.41 | reversal and seat change charges waived |

### Round 2 claims (by audit item)
- 0-R1 / F7: the arrangement setup fee is removed (the scope sentence now says an arrangement carries no fee); its slot is
  front_loading (share weight by the earlier late-charge record); the only write is the client's payment and the terminal
  ledger equals the rule (no fee is collected anywhere).
- 0-R2: ClearPath Standard repriced per managed_renewal_and_uplift: seat_rate 124.00 after renewals (119.04 was the
  36-month initial rate); monthly fees 2,604.00, late fees 39.06, payments 2,643.06; contracted_seats = seat_count = 21.
  The rationale line now states the derivation.
- 1-R1: TimeBank blocks backed by signed orders, block invoices and payments (activation on full payment), hours-ledger
  grants, draws (on billable ClearPath tickets with their minutes) and the 2024 forfeiture; the provisioning factor now
  reads the hours ledger itself.
- 1-R2: ClearPath Monitor onboardings backed by P4 user_onboarding tickets (opened >= 5 business days before, first
  response, resolved), proration rows on the 2026-09-01 and 2026-10-01 monthly invoices, monthly fees and the September
  payment; contracted_seats 24 = seat_count on 2026-02-28; the August onboarding moved to a business day (2026-08-28).
  Observations closed too: the E5 purchase now has its signed new_subscription order form; Continuum Backup Standard sits
  on its monthly renewal term. Gold gained read-only steps for the new records.
- F1 (A3): every rule's combination sentence is generic ("The adjustments below change the standard X in this order: ..."),
  names no factor quantity and fixes the order where adjustments do not commute.
- F2 (A5): the down payment is a share of the arrangement balance (a baseline quantity); the month's late charge is an
  amount set aside up front or left out by its own factor; "principal" no longer exists.
- F3 (A6): early_release_anchor tier 2 reverses the source seat addition's billed partial-cycle charge in proportion
  (shape: billed amount x removed/added); prompt_cancel_anchor tier 2 refunds a renewed annual term by whole months plus
  the month in progress over 12; held_days_month_fraction tier 2 charges the part of the month before suspension
  ((30 - days suspended)/30). Pairwise: anchor T1 no day count / T2 billed-charge ratio / T3 days over cycle; cancel T1
  no day count / T2 months/12 / T3 days/cycle; held T1 held/30 / T2 (30-suspended)/30 / T3 constant 1.
- F4 (B14): prepaid hours = hours-ledger grants + rollovers in + reversals - draws - rollovers out - forfeitures across all
  the client's blocks (XSUM); probe with a second active block confirms the rule's tier.
- F5 (C18): the base ClearPath waiver sentence is superseded and restated: coverage is read as it stands on the posting day
  for the month just ended.
- F6: post_reduction_credit and post_seat_addition_charge take cycle_start_date; the cancellation tool takes
  invoice_number and cycle_start_date and no longer looks anything up; both refund overwrites credit every in-window
  credit / whole cancellation to the invoice that billed the cycle refunded.
- F8 / D21: license work charges (P5 provisioning fee, P6 order reversal fee and seat change charges) are not charged to a
  client whose active / notice_given ClearPath tier covers Microsoft 365 administration (stated once per policy; probes
  confirm); seat change charges now fall with volume (5.00 / 4.00) and price every seat addition the cancellation reverses.
- Observations: O5 no-vCIO case named; O6 wording aligned; O7 Monitor clause added to the rule; O9 absent source record
  stated (standard method); multi-source labels in the rationales corrected (instalment_count, coverage_share,
  order_window_convention not counted).
- Values after rework: task 0 880.25 / 21.66 / 819.68; task 1 3.55 / 257.66 / 1884.41. XF sweeps clean (basis, baseline,
  replaced_by verbatim; no factor id inside a tool name; task_tools free of datetime/time/random/uuid/secrets).
REWORK round 2: gates 7/7 green

## Round 3 rework (audit revision_2: task0=PASS task1=RED:1-R3 charter=G1,G2, O12; XF points 23-26)

### Events written by the task tools and their base triggers (XF 24)
| tool | events / rows written | base triggers | lands in |
|---|---|---|---|
| post_reduction_credit_23f8ed2c | licensing_refund_credit | [] | licensing |
| assess_late_charge_e02563fc | licensing_late_fee | [] | licensing |
| pay_arrangement_instalment_a0d5f2e9 | licensing_payment | [] | licensing |
| post_admin_fee_5104ae31 | licensing_admin_fee | [] | licensing |
| post_seat_addition_charge_bba679a2 | licensing_prorated_charge | [] | licensing |
| cancel_subscription_in_window_d46a60fb | licensing_cancelled_in_window -> licensing_licenses_removed (cancellation) -> licensing_refund_credit; signed licensing_change_requests intake row | licensing:licensing_licenses_removed; licensing:licensing_refund_credit | licensing |
No tool writes an event whose triggers cross into another category.

### All-pairs method-shape table (XF 23; same-field aggregates count as one input, constant multipliers ignored)
| factor | pair | shapes | verdict |
|---|---|---|---|
| early_release_anchor | T1 / T2 | amount x qty vs billed partial charge x qty / added qty (adds the billed-charge input) | PASS |
| early_release_anchor | T1 / T3 | amount x qty vs amount x qty x days / cycle (adds the day count) | PASS |
| early_release_anchor | T2 / T3 | billed charge ratio vs day count (different inputs) | PASS |
| first_period_accrual | T1 / T2 | d / 30 vs floor(d / 30) (adds floor; domains d<=30 vs d>60) | PASS |
| first_period_accrual | T1 / T3 | d / 30 vs constant (adds d) | PASS |
| first_period_accrual | T2 / T3 | floor(d / 30) vs constant | PASS |
| month_late_treatment | T1 / T2 | late charge excluded from spread and from up front vs added up front | PASS |
| month_late_treatment | T1 / T3 | late charge subtracted from the spread base vs not | PASS |
| month_late_treatment | T2 / T3 | late charge up front and out of the spread vs inside the spread | PASS |
| held_days_month_fraction | T1 / T2 | DAYS(purchase_at) / 30 vs (30 - MN(DAYS(suspended_date), 30)) / 30 (different field, adds MN) | PASS |
| held_days_month_fraction | T1 / T3 | held days / 30 vs constant | PASS |
| held_days_month_fraction | T2 / T3 | suspension days with MN vs constant | PASS |
| order_window_convention | T1 / T2 | whole cycle (never 0) vs nothing | PASS |
| order_window_convention | T1 / T3 | whole cycle vs remaining days / cycle | PASS |
| order_window_convention | T2 / T3 | nothing vs remaining days (T3 > 7 days on its domain, never 0) | PASS |
| prompt_cancel_anchor (round 3) | T1 / T2 | amount x licenses vs latest addition's billed charge + amount x (licenses - added) x days / cycle (adds charge and day count) | PASS |
| prompt_cancel_anchor | T1 / T3 | amount x licenses vs amount x licenses x days / cycle | PASS |
| prompt_cancel_anchor | T2 / T3 | adds the billed-charge input | PASS |
| admin_fee_return | T1 / T2 | fee billed vs fee billed x days / cycle (adds the day count) | PASS |
| admin_fee_return | T1 / T3 | fee billed vs nothing (T1 positive wherever a fee is billed) | PASS |
| admin_fee_return | T2 / T3 | pro rata vs nothing | PASS |
G1 reachable-domain probe for the new prompt_cancel_anchor tier 2 (scratch copies of the task-1 handling-time world):
| policy | probe | scratch result | tier |
|---|---|---|---|
| window_cancellation | lag 3 (task world): tier 1 | refund_base=1971.00; result=1884.41 |
| window_cancellation | lag 5, seat addition 1 day before: tier 2 | refund_base=1795.04; result=1713.59 |
| window_cancellation | lag 5, seat addition 1 day before but no charge: tier 3 | refund_base=1773.90; result=1884.41 |
| window_cancellation | lag 7, seat addition 5 days before: tier 3 | refund_base=1773.90; result=1692.45 |

### Round 3 claims (by audit item)
- G1 (XF A6 / 23): prompt_cancel_anchor tier 2 replaced. It now applies when the cancellation comes more than three days
  after the window opened but within three days of the latest seat addition, which carries a partial-cycle charge. Those
  licenses are refunded as never used (their billed charge in full), and the others are refunded under the standard day
  count. It is reachable inside the 168-hour window: lag 5 gives 1,795.04 against 1,971.00 for tier 1 and 1,773.90 for tier 3.
  The all-pairs table above covers every method factor of the charter.
- G2 (XF 5): the opening lag now lives in early_release_anchor's own sentence and bindings. The whole class was swept:
  days past due moved into first_period_accrual (removed from the baseline paragraph), and the arrangement's invoice moved
  into down_payment_share (with down_amt among its bindings).
- XF 26: the plain bindings that read factor-owned bindings (P2 monthly_charge, P4 rate, P6 licence_refund) were folded
  into result. Each fee or discount sentence now names the result it modifies (reduction credit, late charge, first
  instalment, administration fee, partial-cycle charge, cancellation refund).
- 1-R3: the five onboarding tickets are now billable_out_of_scope, because Monitor's helpdesk_remote_included is false.
  Their 30 remote business-hour minutes are drawn from the active TimeBank block (five 0.5 h draws). The block balance is
  12.0 h, and the provisioning tier is unchanged.
- XF 25 (complete ledgers):
  - Task 0: ClearPath monthly fees for every month 2025-07..2026-10, each with its payment (card autopay on invoice day;
    the two failed months carry their late fees and late ACH payments), plus the seat ledger baseline reproducing 21
    seats. Gold gained one read.
  - Task 1: Sentinel endpoint enrollments (29 + 2), retainer hours ledger (10.0 h), and monthly fees of 523.10 with
    payment. Continuum monthly fees of 189.50 with payment. Gold gained four reads.
  - All scored values are unchanged: 880.25 / 21.66 / 819.68; 3.55 / 257.66 / 1884.41.
- O12: the covered-work scope sentence now sits in the baseline paragraph of P5 and P6, and each fee ladder sentence opens
  with "For license work not covered by ClearPath". The fee factors are thereby scoped to uncovered clients, so they bear
  weight on their whole domain. For a covered client the fee is 0 by definition, so no fee factor can carry weight there.
  That case lies outside the factors' scope by design.
- Proof text swept: rationale seed lines, the TimeBank hour figures, the ticket necessity text, and the round-change notes
  in both tasks.
REWORK round 3: gates 7/7 green

## Round 4 rework (render_source/microsoft_365_subscriptions/render_r1.md, renderer scan-first STOP)

### Probes (scratch copies of the handling-time worlds)
| policy | probe | scratch result | rule tier that settles it |
|---|---|---|---|
| MONTHS check | Jan 31 -> Feb 28 | MONTHS('2026-01-31','2026-02-28')=0; MONTHS('2026-01-01','2026-02-01')=1 | the onboarding window no longer exists; every remaining month window counts rows posted on the 1st (late charges), where MONTHS and the anniversary rule agree |
| payment_arrangement | F1 task world: balance 0.00 | n_instal=6; result=819.68 | tier 1 (6) for <= 0, tier 2 (4) when a balance is owed |
| payment_arrangement | F1 credit balance -150.00 | n_instal=6; result=819.68 | tier 1 (6) for <= 0, tier 2 (4) when a balance is owed |
| payment_arrangement | F1 owes 10.00 | n_instal=4; result=1079.12 | tier 1 (6) for <= 0, tier 2 (4) when a balance is owed |
| admin_fee | F3 task world | m365_protected=22; result=3.55 | tier 2 (95): 22 of the active plan |
| admin_fee | F3 decoy: closed old plan with 12 M365 protections, no removals | m365_protected=22; result=3.55 | tier 2 (95): only the active plan's 22 counted (would be 34 >= 30 -> 90 if pooled) |
| seat_partial_charge | F2 task world | onboardings=5; result=257.66 | tier 1 (3%): 29 - 24 = 5 >= 4 |
| seat_partial_charge | F2 decoy: closed agreement listed first (80 vs 20 seats) | onboardings=5; result=257.66 | status filter: active agreement's 5 |
| seat_partial_charge | F2 absent ClearPath agreement | onboardings=0; result=265.54 | fall-through: no discount |

### XF 8 / 12-14 / 26 sweep (whole charter, once)
- 8 (rule == compute):
  - The F1-F4 phrases are fixed.
  - The four edited sentences and their bindings were re-read for every other policy. Each rule clause has its binding and
    each binding its clause; compute_basis, baseline and replaced_by stay verbatim in their rules (scratch check).
- 12 (month-end): the remaining whole-month windows are these.
  - Late charges less than twelve whole months back (P2 rate).
  - ClearPath late fees, twelve months (P2 escalation).
  - The past month's late charge and the twenty-four-month count (P3).
  - All of them count rows posted on the 1st of a month: licensing and ClearPath late charges are assessed only on the 1st.
    On those dates MONTHS() and the anniversary rule agree.
  - The only window on rows dated any day of the month (the onboarding count) has been removed.
- 13 (absent / None / zero):
  - No active ClearPath agreement: fall-through in every ClearPath ladder (probed in rounds 2 and 4).
  - No active Continuum plan: cont_plan is None and the count is 0, so the bundle rate is the whole rate.
  - No hours ledger: the standard provisioning fee.
  - Credit balance: tier 1.
  - Contracted seats above the seat count (a negative difference): no discount.
  - Ternary guards keep DAYS() off a missing suspended_date or seat-addition date.
- 14 (decoys, first-match reads): every CFIELD/CPARAM filters status='active'. Probes in rounds 2 and 4 used closed or
  cancelled second records (ClearPath, Sentinel, Continuum, TimeBank) and an earlier seat addition or reduction; the rule
  tier held in each.
- 26: no plain binding reads a factor-owned binding (cont_plan is owned by backup_bundle_rate); every fee or discount
  sentence names the result it modifies; no rule word now rests on a field the records lack ("missed licenses" and
  "same tenant" are removed).

### Round 4 claims (by finding)
- F1: the instalment-count test is cp_owed <= 0, and the rule says "owes nothing (a balance of zero or a credit)". Probed:
  a credit of -150.00 gives 6 instalments, owing 10.00 gives 4.
- F2: the dated "less than one whole month" onboarding window is replaced by a record test with no month-end question:
  the seats the active ClearPath agreement covers beyond its contracted seats (staff taken on since its last renewal).
  Task 1 gives 29 - 24 = 5 >= 4, so the tier and the value (257.66) are unchanged. Probes covered a closed agreement
  listed first and an absent agreement. MONTHS Jan 31 -> Feb 28 = 0 is recorded above.
- F3: the bundle count is keyed on the active Continuum plan's id (cont_plan, exact value), and the rule says other plans'
  protections are not counted. Probe: a closed old plan with 12 Microsoft 365 protections leaves 22, so the tier stays 95.
- F4: "shows that Stratton Bay's pre-renewal license review missed licenses" became "A reduction made in a renewal window
  carries Stratton Bay's pre-renewal review goodwill on the reduction credit:", and ", which watches the same tenant" is
  removed.
- No scored value moved: 880.25 / 21.66 / 819.68; 3.55 / 257.66 / 1884.41. Stale proof text in task 1 was swept (seat
  ledger necessity, onboarding factor trace and sensitivity tiers, tracing, near-miss line, bundle trace).
REWORK round 4: gates 7/7 green

## Round 5 rework (render_source/microsoft_365_subscriptions/render_r2.md)

### Probes (scratch copies of the handling-time worlds)
| policy | probe | scratch result | rule tier that settles it |
|---|---|---|---|
| window_cancellation | R2-3 task world (Standard, 22 M365 users) | deprov_rate=1.0; result=1884.41 | tier 2 (1.00) |
| window_cancellation | R2-3 BDR plan protecting only servers | deprov_rate=0; result=1914.41 | fall-through: no Microsoft 365 user protected -> nothing |
| window_cancellation | R2-3 BDR plan protecting 22 M365 users | deprov_rate=0.5; result=1899.41 | tier 1 (0.50) |
| payment_arrangement | R2-2 mid-month arrangement 2026-10-15, only late charge posted 2026-10-01 | late_24m=0; result=715.9 | not counted (posted less than one whole month before): one share |
| payment_arrangement | R2-2 task world (2025-10-01 charge counted) | late_24m=1; result=819.68 | one earlier charge: 1.25 shares |

### Sweep, every policy once
- (i) Baseline paragraphs naming factor quantities:
  - reduction_credit: only the standard license change fee, which the standard method uses.
  - late_charge, payment_arrangement, admin_fee: none.
  - seat_partial_charge: the provisioning fee is a standard-method amount, and its coverage sentence stays.
  - window_cancellation: the old "order reversal fee and the seat change charges" sentence is replaced by a plain scope
    sentence that names no factor ("no license-work charge against the cancellation refund" for covered work). The
    standard "administration fee is left as billed" sentence is the standard treatment the return factor departs from.
- (ii) Factor sentences relying on a window or definition stated only in another factor:
  - front_loading now defines its own excluded window.
  - The renewal window (P1) remains a shared plain definition read by two factors (XF A.2, as the renderer noted).
  - All other factor sentences rely only on baseline-defined quantities: the prorated amount, the month's charge, the
    arrangement balance, the licenses counted or added, the cycle.
- (iii) Framing clauses asserting facts compute does not test:
  - Deprovisioning now tests the active plan's Microsoft 365 protections.
  - "for the account manager to settle" is replaced by "stays on the invoice outside it".
  - The remaining framing ("credited as never renewed", "billed as part of the order", "refunded as never used",
    "administered month to month", "a separate Partner Center change") restates what the tier's own test and method
    already are, and asserts no untested fact.

### Round 5 claims (by finding)
- R2-1: the cancellation's baseline paragraph keeps the covered-work exemption only as a plain scope sentence that names
  no factor quantity: "Stratton Bay makes no license-work charge against the cancellation refund of a client holding a
  ClearPath agreement whose status is active or notice_given and whose tier has m365_administration_included true, that
  work being covered." The factor sentences keep "For license work not covered by ClearPath".
- R2-2: the front-loading sentence reads "not counting those posted less than one whole month before the arrangement",
  exactly as compute does. A mid-month probe gives one share.
- R2-3: the deprovisioning charge applies only where the active Continuum plan (keyed on its id) protects at least one
  Microsoft 365 user, and the rule and the ladder say so. Probe: a BDR plan protecting only servers charges nothing.
- No scored value moved: 880.25 / 21.66 / 819.68; 3.55 / 257.66 / 1884.41. Proof text swept (deprovisioning trace and
  tracing, front-loading trace, round notes in both rationales).
REWORK round 5: gates 7/7 green

## Round 6 rework (policy audit revision_5: task0=PASS task1=RED:R5-4 charter=R5-1..R5-4)

### Probes (scratch copies of the handling-time worlds)
| policy | probe | scratch result | rule tier / count |
|---|---|---|---|
| window_cancellation | R5-4 task world: 30 cancelled, 22 protected | result=1892.41 | 1.00 x MN(30, 22) = 22.00 |
| window_cancellation | R5-4 42 protected, 30 cancelled | result=1884.41 | 1.00 x MN(30, 42) = 30.00 |
| seat_partial_charge | R5-2 seat addition 2026-10-05 09:00 (162.9 h, lag 7) | result=199.41 | standard method: lag 7 > six days, as the sentence now states |

### replaced_by tails vs retired clauses (XF C16), element by element
| policy | retired clause element | restated in the replaced_by |
|---|---|---|
| reduction_credit | "where refund_on_window_reduction is true" | in scope: "whose plan has refund_on_window_reduction true"; out of scope: "still refunded, where refund_on_window_reduction is true" |
| reduction_credit | unit_price x licenses removed x days from effective_at through cycle end inclusive / days in cycle, half up | out of scope: verbatim |
| reduction_credit | "credited to the next invoice" | retired for every in-window reduction, declared: "credited to the invoice that billed the cycle it refunds, not to the next invoice" |
| window_cancellation | the same four elements | the same restatements ("whose plan has refund_on_window_reduction true", "still refunded, where refund_on_window_reduction is true", formula verbatim, credited-invoice sentence); the reduction sibling named |
| late_charge | "On the first day of each calendar month" | in scope and, for every other invoice, "on the first day of each calendar month" |
| late_charge | "still unpaid more than late_fee_grace_days calendar days after its due date" | in scope and for every other invoice, verbatim |
| late_charge | "one late fee of late_fee_pct_monthly percent of its unpaid balance, or late_fee_minimum_usd if greater, rounded half up" | for every other invoice, verbatim |
| admin_fee (1) | first day of each month; previous month; subscriptions active or suspended at month end | verbatim; amount retired to "worked out under this schedule from the licenses the subscription carries when the fee posts" |
| admin_fee (2) | "Where admin_fee_waived_with_clearpath_admin is true" | "Where admin_fee_waived_with_clearpath_admin is true" (and the whole fee where it is false); compute now tests P('admin_fee_waived_with_clearpath_admin') |
| admin_fee (2) | "no fee is posted" for covered months (active or notice_given, m365_administration_included true) | "no fee is posted" for the same coverage, read on the posting day (declared) |
| admin_fee (2) | "a ClearPath Monitor agreement does not waive the fee" | retired, declared: an active Monitor agreement is charged half |
| seat_partial_charge | "charged for the rest of the billing cycle in which it is submitted" | in scope ("the partial-cycle charge for the rest of the billing cycle in which it is submitted") and out of scope, verbatim |
| seat_partial_charge | the formula, half up | out of scope, verbatim |
| seat_partial_charge | "later cycles include the added licenses in the cycle charge" | in scope and out of scope, verbatim |

### Round 6 claims (by audit item)
- R5-4: the deprovisioning charge is now per Microsoft 365 user taken off the active Continuum plan. Users taken off are
  counted as the lesser of the licenses cancelled and that plan's own protected Microsoft 365 users (compute
  `deprov_users = MN(lic_held, cx_m365)`), and the rule says exactly that.
  - Task 1's refund moves from 1,884.41 to 1,892.41: 1.00 x 22 instead of 1.00 x 30.
  - The other figures were recomputed: factor sensitivities 1700.45 / 1888.86 / 1942.41 / 1914.41 / 1897.41; all-baseline
    1773.90 unchanged; skip admin fee 1888.86; skip seat charge 1634.75.
  - Proof text swept: expected, gold argument, tracing, factor trace, sensitivities, edge effects, order_uniqueness,
    rationale.
- R5-1: the onboarding framing is gone. The sentence reads "The partial-cycle charge takes an onboarding discount set by
  the seats the active ClearPath agreement covers beyond its contracted seats".
- R5-2: the order-window framing names its test: "A seat addition on a subscription that has never renewed, submitted no
  more than six calendar days after the date the cancellation window opened, is billed with the order". The 162.9 h /
  lag-7 counter-case is now consistent (standard method).
- R5-3: every replaced_by tail restates all in-force content of its retired clause (table above). The
  admin_fee_waived_with_clearpath_admin switch is now tested in compute.
- Task 0 is untouched in value: 880.25 / 21.66 / 819.68. Task 1 is 3.55 / 257.66 / 1,892.41.
REWORK round 6: gates 7/7 green

## Round 7 rework (KB audit policy_kb revision_1: kb=CLEAN, six src items)

### Probes
| policy | probe | scratch result | rule tier |
|---|---|---|---|
| reduction_credit | Business Basic P1M, 1 license, 24/30 days, no ClearPath (fee 25.00) | result=0.0 | floor 0.00 -> no credit posted where it would be negative |
| reduction_credit | Business Basic P1M, 1 license, 24/30 days, ClearPath Monitor (fee 10.00) | result=0.0 | floor 0.00 -> no credit posted where it would be negative |
| reduction_credit | Business Basic P1M, 1 license, 24/30 days, ClearPath Standard (covered, fee 0) | result=5.76 | floor 0.00 -> no credit posted where it would be negative |

### Cross-product rows re-checked against the owning product's published docs
- Task 0, ClearPath Standard (docs/managed):
  - Monthly fees (monthly seat-pricing schedule) are 21 x 124.00 = 2,604.00 every month with no credit: there is no
    Business Premium, Sentinel or Continuum, the client has fewer than 40 seats, and no server is enrolled.
  - Late fees (late-fee schedule; each invoice is the agreement's only unpaid invoice):
    - 2025-09-01: 1.25% (no late fee and 1 payment in 12 months) on the band (1,000 at the rate, 1,604 at half) = 22.525,
      less 10% (the 2025-08-01 payment is one whole month back, inside the 3-month window) = 20.27. The minimum is 5.00
      (24+ months live), and there is no relationship courtesy.
    - 2026-04-01: 1.5% (late fee in the window) = 27.03, less 10% = 24.33.
    - Payments are 2,624.27 and 2,628.33; the balance is 0.00.
- Task 1, ClearPath Monitor (docs/managed):
  - Monthly fees: Sentinel bundle 1.5% (12-month term) plus Continuum bundle 1.0% (Backup Standard has no local
    appliance) = 2.5%, plus the server management fee of 2 x 60.00. There is no Business Premium, and the client has
    fewer than 40 seats.
    - September: 962.50 less 2.5% = 938.44, + 120.00 = 1,058.44.
    - October: 1,116.50 less 2.5% = 1,088.59, + 120.00 = 1,208.59.
  - Prorations (published seat-ledger rule) are unchanged: 4.97, 12.83, 11.55, 3.85, 2.57.
  - The September invoice was paid 1,063.41; the balance is 1,239.39.
  - Onboarding tickets are billable out of scope and settled from TimeBank (published labor settlement L1/L4: 30 minutes
    remote).
- Task 1, Sentinel (docs/security endpoint true-up, IR ledger):
  - 29 x 15.90 + 2 x 31.00 = 523.10, above the 27-endpoint commitment.
  - Retainer: 10 hours granted per contract year, and the 2024-25 year forfeited at the 0% rollover share.
- Task 1, Continuum (docs/backup monthly plan fee): 2 servers x 59.00 + 22 Microsoft 365 users x 3.25 = 189.50. There is
  no workstation charge, and the storage overage is 0.00.
- TimeBank has no published docs yet, so it was checked against blueprint timebank.yaml: price 3,160.00, activated on
  full payment, and draws converted at the technician ratio in business hours.

### Round 7 claims (by src item)
- reduction_credit_no_floor: the rule now says the credit "never falls below 0.00: where the license change fee leaves
  nothing, no reduction credit is posted", and compute is RND(MX(..., 0), 2). The Business Basic P1M probe (1 license,
  24 of 30 days) gives 0.00 with no ClearPath and 0.00 with Monitor, so nothing is posted; a covered client gets 5.76.
- every_x_prerequisite_vs_latest_x_rule: each prerequisite sentence now waits on exactly the record its depended-on rule
  prices, each with its 0.00 case.
  - Late charge: "the subscription's latest in-window reduction carries its reduction credit ..., unless that credit comes
    to 0.00 and so is not posted".
  - Cancellation:
    - "the administration fee owed on the first day of the current month for the month just ended ..., where the
      subscription was active or suspended at that month's end and the fee comes to more than 0.00";
    - "the subscription's latest seat addition carries its partial-cycle charge ..., unless that charge comes to 0.00
      and so is not posted".
  - The partial-cycle charge rule states that a 0.00 charge is not posted, so a covered client's tail-day seat addition
    lets the cancellation be priced.
  - Conditions and prerequisite_closure copies were updated verbatim in both tasks.
- xprod_seed_managed_late_fees_t0: repriced under the published schedule (20.27, 24.33) with payments reconciled. The
  escalation count is unchanged (one ClearPath late fee in the 12-month window).
- xprod_seed_managed_monthly_fees_t1: repriced under the published schedule (1,058.44, 1,208.59); the payment is 1,063.41
  and the balance 1,239.39. Licensing reads only the tier, status and seats, so nothing moves.
- gold_find_customers_legal_name: gold now locates the client by an identifier the caller states. Task 0 uses
  find_customers(phone_number="9195550231"); task 1 uses find_customers(email="trevor.esposito@grangerhollis.com").
- cancellation_baseline_license_work_hint: not routed (placement only), left as is.
- Scored values are unchanged: 880.25 / 21.66 / 819.68; 3.55 / 257.66 / 1,892.41. Proof text swept (rationales, the
  escalation trace, prerequisite sentences and conditions).
REWORK round 7: gates 7/7 green

## Round 8 rework (policy audit revision_7: task0=RED:R7-1 task1=RED:R7-2 charter=R7-3)

### ClearPath rows, row by row, against the published docs/managed rules
Renewal rates (automatic-renewal schedule: uplift schedule, price protection, then the net adjustment of late fees,
tickets, seat growth and service credits; cap last):
- Task 0, 2025-04-08 (4th renewal, 3 already recorded): uplift 4%, giving 128.96. Live 72 months, never suspended:
  the lowest of 128.96, list 124.00 and 126.48 is 124.00. Net adjustment -0.5% (no late fee, no service credit, no
  seat growth, 0 tickets < 21 seats). Rate 123.38.
- Task 0, 2026-04-08 (5th): the lowest of 128.32, 124.00 and 125.85 is 124.00. Net 0 (2 late fees +0.5, 0 tickets
  -0.5). Rate 124.00, the seeded seat_rate_usd.
- Task 1, 2026-03-01 (5th): uplift 4%, giving 40.04. Live 59 whole months, so no long-tenure protection: the lower of
  40.04 and 38.50 is 38.50. Net -0.5% (0 tickets opened 2025-03-01..2026-02-28 < 24 seats). Rate 38.31. This holds for
  any expiring rate of 37.02 or more, because the list caps it.
| task | row | rule | amount |
|---|---|---|---|
| 0 | 2025-07-01 managed_monthly_fee INV-020731 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2590.98 |
| 0 | 2025-08-01 managed_monthly_fee INV-020737 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2590.98 |
| 0 | 2025-08-01 managed_payment INV-020737 | payment of the invoice named (autopay on invoice day / ACH) | 2590.98 |
| 0 | 2025-09-01 managed_late_fee INV-020731 | late-fee schedule (bands, rate by payment record, recent-payment courtesy, minimum 5.00) | 20.20 |
| 0 | 2025-09-01 managed_monthly_fee INV-020774 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2590.98 |
| 0 | 2025-09-01 managed_payment INV-020774 | payment of the invoice named (autopay on invoice day / ACH) | 2590.98 |
| 0 | 2025-09-05 managed_payment INV-020731 | payment of the invoice named (autopay on invoice day / ACH) | 2611.18 |
| 0 | 2025-10-01 managed_monthly_fee INV-020811 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2590.98 |
| 0 | 2025-10-01 managed_payment INV-020811 | payment of the invoice named (autopay on invoice day / ACH) | 2590.98 |
| 0 | 2025-11-01 managed_monthly_fee INV-020848 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2590.98 |
| 0 | 2025-11-01 managed_payment INV-020848 | payment of the invoice named (autopay on invoice day / ACH) | 2590.98 |
| 0 | 2025-12-01 managed_monthly_fee INV-020885 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2590.98 |
| 0 | 2025-12-01 managed_payment INV-020885 | payment of the invoice named (autopay on invoice day / ACH) | 2590.98 |
| 0 | 2026-01-01 managed_monthly_fee INV-020922 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2590.98 |
| 0 | 2026-01-01 managed_payment INV-020922 | payment of the invoice named (autopay on invoice day / ACH) | 2590.98 |
| 0 | 2026-02-01 managed_monthly_fee INV-023402 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2590.98 |
| 0 | 2026-03-01 managed_monthly_fee INV-020996 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2590.98 |
| 0 | 2026-03-01 managed_payment INV-020996 | payment of the invoice named (autopay on invoice day / ACH) | 2590.98 |
| 0 | 2026-04-01 managed_late_fee INV-023402 | late-fee schedule (bands, rate by payment record, recent-payment courtesy, minimum 5.00) | 24.24 |
| 0 | 2026-04-01 managed_monthly_fee INV-021033 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2590.98 |
| 0 | 2026-04-01 managed_payment INV-021033 | payment of the invoice named (autopay on invoice day / ACH) | 2590.98 |
| 0 | 2026-04-07 managed_payment INV-023402 | payment of the invoice named (autopay on invoice day / ACH) | 2615.22 |
| 0 | 2026-05-01 managed_monthly_fee INV-021070 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2604.00 |
| 0 | 2026-05-01 managed_payment INV-021070 | payment of the invoice named (autopay on invoice day / ACH) | 2604.00 |
| 0 | 2026-06-01 managed_monthly_fee INV-021107 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2604.00 |
| 0 | 2026-06-01 managed_payment INV-021107 | payment of the invoice named (autopay on invoice day / ACH) | 2604.00 |
| 0 | 2026-07-01 managed_monthly_fee INV-021144 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2604.00 |
| 0 | 2026-07-01 managed_payment INV-021144 | payment of the invoice named (autopay on invoice day / ACH) | 2604.00 |
| 0 | 2026-08-01 managed_monthly_fee INV-021181 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2604.00 |
| 0 | 2026-08-01 managed_payment INV-021181 | payment of the invoice named (autopay on invoice day / ACH) | 2604.00 |
| 0 | 2026-09-01 managed_monthly_fee INV-021218 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2604.00 |
| 0 | 2026-09-01 managed_payment INV-021218 | payment of the invoice named (autopay on invoice day / ACH) | 2604.00 |
| 0 | 2026-10-01 managed_monthly_fee INV-021255 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 2604.00 |
| 0 | 2026-10-01 managed_payment INV-021255 | payment of the invoice named (autopay on invoice day / ACH) | 2604.00 |
| 0 | agreement ClearPath Standard seat_rate / balance | renewal schedule / ledger sum | 124.00 / 0.00 |
| 1 | 2026-09-01 managed_monthly_fee INV-025104 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 1053.81 |
| 1 | 2026-09-01 managed_proration_charge INV-025104 | seat proration: rate x days to month end / days in month | 4.94 |
| 1 | 2026-09-12 managed_payment INV-025104 | payment of the invoice named (autopay on invoice day / ACH) | 1058.75 |
| 1 | 2026-10-01 managed_monthly_fee INV-025730 | monthly seat-pricing schedule (seats x rate in force; credits/server fee as stated above) | 1203.22 |
| 1 | 2026-10-01 managed_proration_charge INV-025730 | seat proration: rate x days to month end / days in month | 12.77 |
| 1 | 2026-10-01 managed_proration_charge INV-025730 | seat proration: rate x days to month end / days in month | 11.49 |
| 1 | 2026-10-01 managed_proration_charge INV-025730 | seat proration: rate x days to month end / days in month | 3.83 |
| 1 | 2026-10-01 managed_proration_charge INV-025730 | seat proration: rate x days to month end / days in month | 2.55 |
| 1 | agreement ClearPath Monitor seat_rate / balance | renewal schedule / ledger sum | 38.31 / 1233.86 |
Other ClearPath rows: task 1's onboarding and TimeBank-draw tickets settle labor through TimeBank (published labor
settlement), the seat ledger reproduces seat_count 29, and contracted_seats is 24 (renewal rule). No ClearPath row
differs from the published rules.

### Round 8 claims (by audit item)
- R7-1: task 0's ClearPath rates follow the published automatic-renewal schedule on the seeded ledger: 123.38 from
  2025-04-08 and 124.00 from 2026-04-08.
  - Monthly fees are 2,590.98 for 2025-07..2026-04 and 2,604.00 for 2026-05..2026-10.
  - The late fees are 20.20 and 24.24, with ACH payments of 2,611.18 and 2,615.22; every autopay payment equals its
    invoice, and the balance is 0.00.
  - The escalation count is unchanged, so no licensing figure moves.
- R7-2: task 1's ClearPath Monitor rate follows the 2026-03-01 automatic renewal: 38.31.
  - Fees are 1,053.81 and 1,203.22.
  - Prorations are 4.94 / 12.77 / 11.49 / 3.83 / 2.55.
  - The September payment is 1,058.75 and the agreement balance 1,233.86.
  - No licensing figure moves.
- R7-3: every prerequisite sentence now waits only on a record-visible line:
  - "the subscription's latest in-window reduction carries its reduction credit line";
  - "the administration fee line for the month just ended stands on its billing ledger, where the subscription was
    active or suspended at that month's end";
  - "the subscription's latest seat addition carries its partial-cycle charge line".
  - The depended-on rules post the line even at 0.00: "a reduction credit line of 0.00, no credit being due", "a
    partial-cycle charge line of 0.00, nothing being due", and "no fee is charged and the month carries an
    administration fee line of 0.00". The overwrite declaring the waiver change was updated with them.
  - The three tools now accept "a number of 0.00 or more". Conditions and prerequisite_closure copies were updated
    verbatim.
- Scored values are unchanged: 880.25 / 21.66 / 819.68; 3.55 / 257.66 / 1,892.41. Proof text swept (both rationales'
  ClearPath lines, the escalation trace, prerequisite sentences and conditions).
REWORK round 8: gates 7/7 green

## Round 9 (revision_8: task0=RED:R8-2a,R8-2b,R8-2c task1=RED:R8-2d charter=R8-1)

### R8-1: positive amount contracts, each 0.00 edge handled
The three tools again take "a positive number to 2 decimal places", and no 0.00 billing row exists or is posted.
- reduction credit, route (a): the depended-on policy now says "the license change fee never taking more than half
  the prorated amount, so every reduction carries a reduction credit above 0.00". The compute uses
  `MN(change_fee, prorated * K('fee_cap_share'))` with fee_cap_share 0.5. The late charge's wait ("latest in-window
  reduction carries its reduction credit line") therefore always resolves.
- seat partial charge, route (b): a covered client's tail-day addition costs nothing and carries no line. The
  cancellation's wait carves it out by record: covered ClearPath tier active or under notice AND the addition was
  submitted with 7 or fewer days left in its cycle AND it is not within 6 days of the window opening of a
  never-renewed subscription.
- admin fee, route (b): a covered client under the waiver switch gets "no fee is posted". The cancellation's wait
  carves this out by record (the waiver switch AND a covered tier). The wait also applies only "where the subscription
  was active at that month's end", so a subscription suspended all month (0.00) is outside it.
- No wait reads another policy's computed amount. Each one tests records only: tier, status, dates, the switch and
  renewal_count.

Probe table (scratch worlds, check_compute evaluator):
| policy | probe | result | edge handling |
|---|---|---|---|
| reduction_credit | Business Basic P1M, 1 license, 24/30 days, no ClearPath | 2.88 | fee capped at half of 5.76; the credit line always exists |
| reduction_credit | same, ClearPath Monitor, reduction on day 29 (2 days left) | 0.24 | the 10.00 fee is capped at half of 0.48; still > 0 |
| seat_partial_charge | covered (Standard) addition 2026-09-26, 5 days left, not part of the order | 0.00 | no line; carved out of the cancellation's wait by record |
| seat_partial_charge | same addition, ClearPath Monitor (not covered) | 12.00 | positive line; the wait applies |
| admin_fee | covered (Standard), waiver switch true | 0.00 | no fee posted; carved out of the wait by record |
| admin_fee | Monitor, suspended 2026-08-20 | 0.00 | not active at month end, so outside the wait |
The gold paths hit none of these edges. T0's reduction credit (880.25) and T1's partial charges and admin fee are
positive and are posted as before.

### R8-2a..d: ClearPath history seeded from signing, so every look-back reads seeded rows
T0's agreement (ClearPath Standard, 21 seats) runs from signing on 2024-03-11 and go-live on 2024-04-08.
T1's (ClearPath Monitor, 24 contracted seats) runs from signing on 2025-02-10 and go-live on 2025-03-01. Each has
every monthly invoice, payment, ticket and seat change since signing. Every row is priced by the published
docs/managed/ rules.
| task | row | rule | look-back window | seeded rows read | value |
|---|---|---|---|---|---|
| 0 | 2024-03-11 onboarding fee + 2024-03-13 ACH | signing: per seat x seats, min | none (signing) | agreement seats 21 | 1,750.00 |
| 0 | 2024-05-01 proration (service month 2024-04) | baseline proration from go-live | 2024-04-08..2024-04-30 | baseline seat add 2024-04-08 (21) | 1,996.40 |
| 0 | 2024-05..2025-04 monthly fees | rate 124.00 x 21 | none | seat ledger | 2,604.00 |
| 0 | 2025-04-08 first renewal (R8-2a) | auto-renewal net adjustments | 2024-04-08..2025-04-07 | 5 tickets (06-12, 08-20, 11-05, 01-22, 03-04) < 21 seats: -0.5%; 0 late fees; 0 credits; no seat growth | 123.38 |
| 0 | 2025-05..2026-04 monthly fees | 123.38 x 21 | none | renewal above | 2,590.98 |
| 0 | 2025-09-01 late fee on the 2025-07 invoice (R8-2b) | late-fee schedule | payments 2024-10-01..2025-08-31: 10 (no late fee) -> 1.0%; the 2025-08-01 card payment is a whole month before (not within 1), so the 3-month 10% courtesy applies; live 16 months -> minimum 10.00 | 2,590.98 balance, the only unpaid invoice | 16.16 (ACH 2,607.14 on 2025-09-05) |
| 0 | 2026-04-01 late fee on the 2026-02 invoice (R8-2c) | late-fee schedule | late fees 2025-04-01..2026-03-31: 2025-09-01 -> 1.5%; 2026-03-01 payment -> 10% | 2,590.98, the only unpaid invoice | 24.24 (ACH 2,615.22 on 2026-04-07) |
| 0 | 2026-04-08 second renewal | auto-renewal | 2025-04-08..2026-04-07 | 6 tickets (05-13, 07-08, 10-14, 12-02, 02-17, 03-24) < 21: -0.5%; 2 late fees (2025-09-01, 2026-04-01): +0.5%; net 0 | 124.00 |
| 0 | 2026-05..2026-10 monthly fees, balance | 124.00 x 21; ledger sum | none | all payments | 2,604.00 / 0.00 |
| 1 | 2025-02-10 onboarding fee + 2025-02-12 ACH | signing | none | agreement | 600.00 |
| 1 | 2025-04-01 proration (service month 2025-03) | baseline proration | 2025-03-01..2025-03-31 | baseline seat add 2025-03-01 (24) | 924.00 |
| 1 | 2025-04..2026-02 monthly fees | signing rate with the credits combined | none | agreement, Sentinel/Continuum holdings | 1,020.90 |
| 1 | 2026-03-01 first renewal (R8-2d) | auto-renewal, lower of uplift and list | 2025-03-01..2026-02-28 | 0 tickets (first ticket 2026-05-19) < 24: -0.5%; 0 late fees; 0 credits; no seat growth (first add 2026-08-28) | 38.31 |
| 1 | 2026-03..2026-08 monthly fees, ACH on the 10th | 38.31-based seat pricing | none | renewal above | 1,016.45 |
| 1 | 2026-09 / 2026-10 fees, prorations, balance | seat pricing; seat proration | seat adds 2026-08-28..2026-09-29 | 5 user_onboarding seat adds | 1,053.81 / 1,203.22; 4.94 / 12.77 / 11.49 / 3.83 / 2.55; 1,233.86 |
Changes from round 8:
- T0's 2025-09-01 late fee moves from 20.20 to 16.16, and its ACH payment from 2,611.18 to 2,607.14. The window now
  holds 10 seeded payments, so the 1.0% rate applies.
- T1's expired TimeBank block, its orders, billing and ledger rows, and ticket SB-0161204 were removed. They predated
  the re-dated history and nothing priced reads them.
- A find_managed_tickets gold read was added to T0, so replay closure covers the ticket rows.

Gate block (round 9): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 113/113, 1.json 130/130), SOLVABILITY OK,
COMPUTE OK, GROUNDING OK, SCOPE OK, TRACEABILITY OK; CACHE-DIFF info only. validate_scenario: 10/10 tasks ok, and no
errors in this difficulty.

### Round 9 claims (by audit item)
- R8-1: there are no 0.00 billing rows. The amount_usd contracts of post_reduction_credit, post_seat_addition_charge
  and post_admin_fee are positive again.
  - The reduction credit can no longer be zero: the license change fee is capped at half the prorated amount.
  - The seat-addition and admin-fee zero cases are carved out of the cancellation's waits by record tests: covered tier
    plus a tail-day addition, and covered tier plus the waiver switch. The admin-fee wait applies only to a
    subscription active at month end.
  - No wait reads a computed amount, and every edge was probed (table above).
- R8-2a: task 0's first renewal (123.38) reads 2024-04-08..2025-04-07, which is all seeded: signing 2024-03-11 and
  go-live 2024-04-08, with every invoice, payment and ticket since then.
- R8-2b: task 0's 2025-09-01 late fee reads payments from 2024-10-01 onward, all seeded, so the rate is 1.0%. The fee
  is recomputed to 16.16 and the ACH to 2,607.14, and the proof text was swept.
- R8-2c: task 0's 2026-04-01 late fee (24.24) and the second renewal (124.00) read only seeded rows.
- R8-2d: task 1's 2026-03-01 renewal (38.31) reads 2025-03-01..2026-02-28, which is all seeded from the 2025-02-10
  signing. The pre-signing TimeBank block and ticket were dropped.
- Combination sentences keep their order. Scored values are unchanged: 880.25 / 21.66 / 819.68 and
  3.55 / 257.66 / 1,892.41.
REWORK round 9: gates 7/7 green

## Round 10 (revision_9: task0=PASS task1=PASS charter=R9-1,R9-2)
Minimal charter edits. No seed, gold step or scored figure changed.

### R9-1: the fee cap moves into the standard method
- The standard-method sentence (rule, baseline.rule and compute_basis.std_prorated) now reads: "less the standard
  license change fee of 25.00 USD, never more than half the prorated amount, so a reduction always carries a
  reduction credit above 0.00, rounded half up to the cent". baseline.params gains fee_cap_share.
- The combination sentence is generic again (XF 3): "... and fixed amounts are added or subtracted last; the result is
  rounded half up to the cent once, at the end."
- The fee factor's own sentence says that whichever fee applies is netted, as under the standard method, never more
  than half the prorated amount.
- Baseline check on the Business Basic case: the standard method alone gives 5.76 - min(25.00, 2.88) = 2.88. Compute
  with every factor at baseline also gives 2.88.

### R9-2: zero and negative cases against positive-only tools
- P4 (admin fee): the month-part sentence now ends "... over 30, and one suspended 30 or more days before the posting
  day has no part of the month left to charge, so no fee is posted". The P6 wait still applies only "where the
  subscription was active at that month's end", a record test on status and suspended_date. A subscription
  suspended at month end is therefore never waited on.
- P6 (cancellation refund): a rule that keeps it positive, stated in the standard method (rule and baseline.rule):
  "Charges deducted from a cancellation refund never take, together, more than half of the refund they are deducted
  from (the license refund with any amounts returned), so a cancellation always carries a refund above 0.00."
  - Compute adds cx_gross, cx_charges and result = RND(cx_gross - MN(cx_charges, cx_gross * K('charge_cap_share')), 2)
    with charge_cap_share 0.5 in baseline.params.
  - The combination order is unchanged.
- Sweep (P3, found by the sweep): a balance made up only of a late charge left out for a dedicated account manager
  gave a 0.00 first instalment. The month_late_treatment sentence now adds "a balance no greater than that late charge
  leaves nothing to arrange, so no arrangement is made".

Sweep of every computation for a reachable result <= 0 against a positive-only tool (scratch worlds, check_compute
evaluator):
| policy | probe | result | why the tool never sees <= 0 |
|---|---|---|---|
| reduction_credit (P1) | Business Basic P1M, 1 of 4 licenses, 24/30 days, no ClearPath | 2.88 | the fee is never more than half the prorated amount, and every method's prorated amount is > 0 (at least 1 day; a reversal only when the source charge is > 0) |
| late_charge (P2) | annual invoice 72.00, 30.00 paid, 12 days past due | 5.00 | in scope only when unpaid past the grace period (days past due >= 11); the minimum of 25.00 or more x share x multipliers, all > 0 |
| payment_arrangement (P3) | balance 25.00 = the month's late charge, left out (dedicated account manager) | 0.00 | the rule now says no arrangement is made (no tool call) |
| payment_arrangement (P3) | same, balance 325.00 | 75.00 | positive whenever the balance exceeds the late charge left out (shares <= 1.5/3 < 1) |
| admin_fee (P4) | Monitor, suspended 2026-08-20, posting 2026-10-01 | 0.00 | no fee is posted (rule); suspended at month end, so outside P6's wait |
| admin_fee (P4) | same, suspended 2026-09-20 | 8.17 | 19/30 of the month; covered + waiver also gives "no fee is posted" (round 9) |
| seat_partial_charge (P5) | covered (Standard) addition with 5 days left, outside the order window | 0.00 | no line (round 9); carved out of P6's wait by record; otherwise it is the provisioning fee or > 0 days |
| window_cancellation (P6) | audit case: Basic P1M, 10 licenses, 10 seat additions, 26/30 days, Backup Basic x 10 users | 31.20 | was -12.60; charges are capped at half of 62.40. The license refund is >= 1 day and the cycle is always billed (a cycle charge is triggered at provisioning and at each renewal) |
Task worlds: P1 880.25, P2 21.66, P3 819.68, P4 3.55, P5 257.66 and P6 1,892.41 are all unchanged. Neither cap binds
there (P1's fee is 0.00; P6's charges are far below half of about 1,900). The baselines and factor sensitivities are
identical. Task 0's rationale now has a one-line Round-10 note.

Gate block (round 10): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (113/113, 130/130), SOLVABILITY OK, COMPUTE OK,
GROUNDING OK, SCOPE OK, TRACEABILITY OK; CACHE-DIFF info only. validate_scenario: 10/10 tasks ok, and no errors in
this difficulty.

### Round 10 claims (by audit item)
- R9-1: P1's change-fee cap is stated in the standard method (baseline.rule, with fee_cap_share in baseline.params)
  and in the fee factor's sentence. It is gone from the combination sentence. On the Business Basic case the standard
  method gives 2.88, the same as compute at baseline.
- R9-2: P4 states that no fee is posted for a subscription suspended 30 or more days before the posting day, and P6's
  wait stays consistent through the record test "active at that month's end". P6 caps the charges at half the refund,
  so the refund is always above 0.00 (the audit case gives 31.20, not -12.60).
- R9-2 sweep: every computation was swept for a result <= 0. One more case was found and stated in the rule: P3's
  balance made up only of a late charge left out of the arrangement, where no arrangement is made. The probe table
  above covers every policy.
- No regression: both tasks' seeds, gold steps and the six scored values are unchanged.
REWORK round 10: gates 7/7 green

## Round 11 (revision_10: task0=PASS task1=PASS charter=R10-1)
One compute-only edit in P6 (window_cancellation). The rule, baseline wording, combination order, seeds, gold steps,
task JSONs, task_tools.py and task 1's TimeBank rows are all unchanged.

### R10-1 (XF 26): P6's cap intermediates folded back into result
- Removed the plain bindings cx_gross and cx_charges, which read refund_base, admin_return, reversal_fee,
  change_rate, seat_changes, deprov_rate and deprov_users.
- result now carries the whole assembly:
  `RND((MN(refund_base, billed_cycle) + admin_return) - MN((0 if covered_work else reversal_fee + change_rate * seat_changes) + deprov_rate * deprov_users, (MN(refund_base, billed_cycle) + admin_return) * charge_cap), 2)`.
- The cap's share is a plain binding that reads only its parameter: `charge_cap = K('charge_cap_share')` (0.5).
  - Its basis quotes the generic cap sentence unchanged: "Charges deducted from a cancellation refund never take,
    together, more than half of the refund they are deducted from (the license refund with any amounts returned), so
    a cancellation always carries a refund above 0.00."
  - result's basis quotes the unchanged combination sentence.
- Probe, the audit's R9-2 world (Basic P1M, 10 licenses, 10 seat additions, Backup Basic x 10): round 10 gives 31.20
  and round 11 gives 31.20. Task 1's P6 stays 1,892.41.

Mechanical check "no plain binding reads a factor-owned binding" (plain = compute bindings that are neither result nor
in any factor's bindings/decides; reads = identifiers in the expression, string literals stripped):
| policy | plain bindings | factor-owned bindings | plain -> factor reads |
|---|---|---|---|
| reduction_credit | 7 | 12 | 0 |
| late_charge | 6 | 13 | 0 |
| payment_arrangement | 1 | 13 | 0 |
| admin_fee | 1 | 16 | 0 |
| seat_partial_charge | 6 | 8 | 0 |
| window_cancellation | 7 (was 8) | 19 | 0 (was 2 bindings / 7 reads) |

Gate block (round 11): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (113/113, 130/130), SOLVABILITY OK, COMPUTE OK,
GROUNDING OK, SCOPE OK, TRACEABILITY OK; CACHE-DIFF info only. validate_scenario: 10/10 tasks ok, and no errors in
this difficulty.

### Round 11 claims
- R10-1: cx_gross and cx_charges are folded into P6's result. The only new plain binding, charge_cap, reads a
  parameter alone. The plain -> factor sweep is 0 on all six policies.
- The cap wording stays generic and the combination order is unchanged.
- No regression: all six scored values (880.25 / 21.66 / 819.68; 3.55 / 257.66 / 1,892.41), the baselines and the
  factor sensitivities are unchanged. Task 1's TimeBank rows are unchanged.
REWORK round 11: gates 7/7 green
