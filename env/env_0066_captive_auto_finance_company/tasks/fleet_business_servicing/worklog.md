# fleet_business_servicing — instantiation worklog (M=2)

Scratch: /tmp/fleet_business_servicing_0066/ (authoring scripts deleted at the end). Full per-task dossiers live in each task's `design_rationale`.

## Difficulty pre-check
- Category fleet (Kestrel Commercial Fleet Lease); claimed events: fleet_payment, fleet_late_charge, fleet_charge_waiver, fleet_credit_refund, fleet_termination_noticed/withdrawn, fleet_unit_turned_in, fleet_unit_charge, fleet_sale_settlement, fleet_trac_surplus_credit/deficiency_charge, fleet_purchase_quote/settlement, fleet_unit_purchased, fleet_title_transfer.
- Draws (draw_counts.py --tasks 2): task 0 = 3 prerequisites, factor counts [6,6,5,4]; task 1 = 1 prerequisite, [6,4].
- Route-around (frozen blueprint): the charter's signer acts (termination notice, purchase option) write fleet_requests rows with no numeric field, so they cannot carry a scored multi-factor value; each task's customer-owned write is instead a signer request that genuinely belongs to the business and carries a computed number (task 0: refund request; task 1: binding purchase quote request).
- DSL limits noted: no date arithmetic (no date results), first-match CFIELD (worlds hold one active contract per category), month-granular windows (within_months), no own-category cross reads (factor evidence only from this unit's ledger/fields, dates and other categories).

## Task 0 — turned-in closed-end van refund (root fleet_ext_turned_in_unit_refund, owner=user)
- Tree: refund <- {early termination charge (6 factors), excess mileage charge (5), latest-month late charge (6)}; refund has 4 factors; all 3 edges value_input on rf_credit, state form.
- Gold values (handling time, real-tool replay): 215.00 / 1197.76 / 22.87 / 1509.98; whole baselines 750.00 / 1652.42 / 25.00 / 5699.32.
- Edge sensitivity: skip termination -> refund 1724.98; skip mileage -> 2707.74; skip late charge -> 1532.85. All 6 prerequisite orders give identical values.
- Probe table (decoys, unchanged results): cancelled Platinum Care on same VIN; active Care on another VIN; paid-in-full retail; returned balloon; 13-month-old late charge; check older than a month; newer invoice on another unit.
- Factor independence table: no factor reads another factor's binding (plain bindings em_driven, lc_inv_*, lc_paid, rf_credit only); assembly only in `result`.
- Method tier tables: termination fee half/prorated(7-11)/flat; allowance daily/term/months; late-charge base dep+lease/pre-tax/whole; condition reserve percent-of-cap/flat/none — distinguishing inputs recorded in task 0 rationale §5.
- Revision: symptom — termination fee tiers "7 to 12 months prorated" and ">12 flat" coincide at 12 months; fix — prorated tier narrowed to 7-11, flat from 12; re-run unchanged (8 months).
- Revision: symptom — replay closure mismatch (2 unread rows: termination-notice request, retail late-charge posting); fix — dropped both seed rows; replay match.
- compute_basis / baseline / policy_source verbatim sweep: 0 misses.
- Per-task gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Traceability: only the 4 expected unlock tool-name misses (KB not yet rendered).

## Task 1 — TRAC deficiency payment arrangement (root fleet_ext_deficiency_arrangement_payment, owner=user)
- Tree: arrangement payment (4 factors) <- TRAC shortfall charge (6 factors); one value_input edge on pa_balance, state form, affirmative ("only after").
- Gold values: 3907.90 (deficiency) / 1257.31 (first arrangement payment); whole baselines 4860.00 / 3907.90.
- Edge sensitivity: skip the deficiency charge -> first payment 0.00.
- Probe table (unchanged results): paid-in-full older retail; closed older balloon; settlement and deficiency charge on another unit; late charge 12 whole months old. Absent-record tiers recorded in task 1 rationale §6.
- History floor: COUNT (one late charge in 12 months) and SUM (deficiency charges on the unit) both move results when zeroed.
- Method tier tables: sale expenses 5%-cap / 8%-cap / actual = 895.00 / 1432.00 / 1610.00; arrangement months to-end / 3 / 1 = 9 / 3 / 1.
- Overwrites: deficiency policy retires the net-proceeds sentence and "when they fall short the shortfall is billed as a deficiency" for short TRAC settlements only; arrangement policy retires "due trac_deficiency_payment_days calendar days after the settlement invoice" for arranged deficiencies only — disjoint clauses.
- compute_basis / baseline / policy_source verbatim sweep over all 6 policies: 0 misses.

## Difficulty closure
- 6 extended policies, each claimed by exactly one task; 6 task tools, disjoint scopes; both tasks call an owner=user tool.
- Charter directions: refund sentences "not ... until" (x2) and "only after"; arrangement sentence "only after".
- Final gate block (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 93/93, 1.json 98/98); SOLVABILITY OK; COMPUTE OK (suite means branches=63.00, steps=12.50; history_rows_max=30; branches_max=84); GROUNDING OK; CACHE-DIFF INFO (no trap selected); SCOPE OK.
- Traceability (pre-render): 6 misses, all unlock tool-name provenance (expected until the KB is published); no other misses.
- Scratch authoring scripts deleted.
ROUND 1: gates 8/8 green

---
# REWORK round 2 (audits/policy_task/fleet_business_servicing/ + render_source/XF_recipe.md)
The round-1 sections above record history only; their figures, step numbers and factor names are superseded by this section and by each task's current design_rationale.

## REWORK round 2 closure (audit item -> change)
- P-1 (late-charge "payments applied to that month" vs the base posting sentence): the late-charge rule now restates the base posting sentence ("a remittance is applied to the months it names, and a remittance naming no month to the oldest unpaid invoice month first"); compute_basis.lc_paid quotes it. Task 0 seed rebuilt so every remittance names the month it pays and sits on it (the 6,500.00 ACH credit names 2026-09, the duplicate check names 2026-08), so the October month is unpaid exactly as the base rule produces; no unnamed remittance remains on an unpaid-month unit. Class swept: lc_paid is the only payment-application read; the arrangement-payment tool's posting is now covered by a declared, scoped overwrite of the posting sentence (arrangement payments apply to the arranged deficiency).
- T0-1: closed by P-1 (single defensible late charge and refund; why_false and business-object text rewritten).
- F-1 / T0-2 (care tier unreachable for fleet; Gold row the care charter cannot produce): both care ladders now distinguish the commercial-use plans only — Platinum Plus/Elite, Platinum, none — read by EXISTS with exact plan and VIN filters. Seed care row replaced by a Kestrel Care Platinum contract within Platinum's term options (60 months / 100,000 miles), deductible options, price range and aggregate cap (40,000.00); a Platinum Elite contract on the sedan's VIN (financed in the balloon account, within that plan's limits) is the near-miss.
- F-2 / T0-3 (utilization discount rewarding heavier use): em_utilization_scale removed with its params; replaced by em_unit_age_addition (younger units lose more value per mile: +0.05 under 24 months, +0.02 for 24-35, nothing at 36+), keeping the mileage charge at its drawn 5 factors.
- F-3 (ACH hold gated on a check): rf_clearing_holdback now holds all returnable remittances (business checks and ACH debits of the last whole month) together, the share set by the unit's own 12-month late-charge history (two or more: whole; one: half; none: nothing).
- T1-1 (no near-miss in the deficiency): seeded in task 1 itself — settlement posted 2026-10-27 (64 days) vs sale 2026-10-21 (58 days); a closed 2019 balloon contract; a 13-month-old fleet late charge; a 7-month-old retail late charge. Task 0 likewise seeds its near-misses (cancelled 2026-06-03 termination request, Platinum Elite on the sedan, 13-month-old late charge, 7-month-old retail late charge, 2026-09-17 business check one whole month back).
- O-1 (first-match reads): every other-holding read is now an EXISTS with exact filters (status, days_past_due=0, plan, VIN) or an XCOUNT over the business's whole retail/balloon ledger; the retail days-past-due ladders became retail late-charge counts (late-charge delinquency addition, refund delinquency reserve, up-front count) and the contract-date ladders became funding-date counts (mileage relationship allowance, deficiency tenure credit). No CFIELD remains.
- O-2 (docstring ordering words): "before the call", "once ..." and "the first payment of" removed from all six docstrings.
- O-3 (world assertion in the arrangement edge effect): "from zero" removed.
- O-4 (deficiency scope vs a zero figure): the rule now states that a settlement recorded as a deficiency stays in scope where the figure comes to nothing, the charge then being zero.
- O-5 (minimum_term_months as a closed-end threshold): kept, named explicitly in the rule.
- O-6 (realism of the relationship concessions): kept as observations; the delinquency addition now rests on posted retail late charges rather than a single contract's days past due.
- O-7 (setoff never posted): the refund setoff became a delinquency reserve held on the unit's credit (nothing to post elsewhere).
- T0-O1 (no recorded decoy for the termination charge): cancelled June termination request seeded and read (find_fleet_requests).
- T0-O2 / T1-O2 (cross-category rows off their charters): retail Tier 2 60m APR 7.99, Tier 3 60m APR 9.99 (vehicle year 2023 on the 2023 new-vehicle contract); balloon Tier 1 48m APR 6.49 with balloon 43 percent of MSRP, Tier 2 48m APR 7.49 with 42 percent; payments, principal and interest recomputed from the sheet APR; payments made + remaining = term; next_due_date, days_past_due (as of the last nightly cycle), past_due_amount and fees_due agree with the retail late charges seeded (5 percent capped at the 30.00 company maximum).
- T0-O3 (retail days past due vs nightly cycle): kept at the last-nightly-cycle count, stated in the seed check.
- T1-O1, T1-O3: no change needed (observations agree with the design).

## Seed realism sweep (both tasks)
- Fleet units: notice, turn-in (30-60 days after notice), sale and settlement dates in lifecycle order; book value = capitalization less depreciations; charges due = sum of charges-due postings; days past due from the oldest unpaid month to the last nightly cycle.
- Retail/balloon: payments made + remaining = term; next due date follows the last paid installment; past due = unpaid installments whose due dates passed; fees due = unpaid retail late charges; no charge-off or repossession stage reached at 35-44 days past due; balloon amounts and APRs on their sheets; the closed 2019 balloon paid its balloon at maturity (pay_balloon, released_electronic).
- Care: one active plan per VIN; Platinum and Platinum Elite are commercial-use plans; terms, deductibles, prices and aggregate limits within each plan's options and caps.

## Pairwise method-tier table (distinguishing input)
| policy | factor | tiers | distinguishing input |
|---|---|---|---|
| termination charge | et_remaining_term_basis | half / prorated 7-11 / flat | 7 months: 375.00 / 437.50 / 750.00 |
| mileage charge | em_allowance_proration | days / term / months | task 0 van: 56,575.34 / 75,000 / 58,333.33 |
| late charge | lc_invoice_part_basis | components / pre-tax / gross | October invoice: 1,247.78 / 1,287.78 / 1,365.05 |
| refund | rf_condition_reserve | percent-of-cap / flat / none | task 0 van: 543.20 / 300 / 0 |
| deficiency | d_sale_expense_allowance | 5% cap / 8% cap / actual | task 1 sale: 895.00 / 1,432.00 / 1,610.00 |
| arrangement payment | pa_term_months_rule | months to end / fixed 3 / 1 | task 1: 9 / 3 / 1 |

## Factor-independence table (transitive, scripted)
Every factor binding reads only F/P/K, DAYS/MONTHS, own-unit SUM/COUNT/LATEST, EXISTS, XCOUNT, its own bindings and plain bindings; no plain binding reads a factor. Plain bindings: mileage em_driven, em_class_rate; late charge lc_inv_date, lc_inv_period, lc_inv_amount, lc_paid; refund rf_credit; deficiency d_book_retired, d_gross, d_expenses_actual; arrangement pa_balance; termination none. Single-factor reads moved into their factor (lc_inv_tax/dep/lease -> lc_invoice_part_basis; lc_inv_due -> lc_lateness_scale; rf_returnable -> rf_clearing_holdback). Script result: 0 violations.

## compute_basis verbatim sweep (scripted)
Every compute_basis quote, every baseline sentence, every policy_source and every overwrite replaced_by is verbatim in its own rule: 0 misses.

## Decoy / absent-record probe table (scratch copies; seeded decoys are in the tasks themselves)
| world change | task 0 [ET, EM, LC, RF] | task 1 [D, PA] |
|---|---|---|
| as seeded | 290.00, 1451.83, 27.87, 1965.25 | 3907.90, 1257.31 |
| no Care contracts | 350.00, 1528.24, 27.87, 1828.84 | – |
| no balloon contracts | 390.00, 1633.30, 30.44, 1681.21 | 4102.90, 2901.93 |
| no retail contract or ledger | 390.00, 1907.83, 12.87, 2424.25 | – |
| no retail ledger, active retail kept | – | 3907.90, 500.00 |
| no notice recorded on the unit | 365.00, 1451.83, 32.16, 1885.96 | 4107.90, 1301.76 |
| no returnable remittance | 290.00, 1451.83, 27.87, 3345.17 | – |
| duplicate Platinum Elite on another VIN | unchanged | – |
No probe raises; every absent-record branch lands on the tier the rule states.

## XF recipe check (policy x point; OK = applied and checked)
| point | termination | mileage | late charge | refund | deficiency | arrangement |
|---|---|---|---|---|---|---|
| 1 assembly sentences | OK generic order sentence | OK quantity-order sentence | OK | OK | OK | OK |
| 2 non-commuting order | OK replace, multiply, credit, add | OK miles, rate, amount | OK replace, multiply, add | OK (all subtractions commute) | OK replace, relief, credits | OK standard-method order |
| 3 factor independence | OK | OK | OK | OK | OK | OK |
| 4 ownership | OK | OK | OK (single-factor reads moved) | OK (rf_returnable moved) | OK | OK |
| 5 compute_basis quotes | OK | OK | OK | OK | OK | OK |
| 6 ties | n/a (no LATEST) | n/a | OK latest invoice, first posted | n/a | OK latest settlement, first posted | n/a |
| 7 counting conventions | OK whole months/days stated | OK incl. N-whole-month window | OK | OK | OK | OK incl. negative months |
| 8 every branch | OK no-notice guard | OK | OK no-turn-in/no-notice | OK | OK no-notice, zero figure | OK past end -> 1 |
| 9 base clauses | OK restated | OK restated | OK restated | OK restated | OK restated (both clauses) | OK restated (two overwrites) |
| 10 rounding | OK once at end | OK | OK | OK | OK | OK |
| 11 tools | OK | OK | OK | OK | OK | OK (names the deficiency) |
| 12 proof text | OK | OK | OK | OK | OK | OK |

## Final gate block (no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 104/104, 1.json 108/108); SOLVABILITY OK; COMPUTE OK (suite means branches=58.50, steps=14.50; history_rows_max=32; branches_max=75); GROUNDING OK; CACHE-DIFF INFO (no cache trap selected); SCOPE OK. Traceability (pre-render): 6 misses, all unlock tool-name provenance; no other misses. Scratch scripts deleted.
REWORK round 2: gates 8/8 green

---
# REWORK round 3 (audits/policy_task/fleet_business_servicing/ revision_2)
The round-2 XF rows "9 base clauses OK" and "11 tools OK (names the deficiency)" were wrong (R2-C2, R2-C3); the round-3 table below supersedes them.

## REWORK round 3 closure (audit item -> change)
- R2-C1 (late-charge rule branch "a remittance naming no month goes to the oldest unpaid month" with no compute): the rule no longer states that branch. It now reads that the payments applied to an invoice month are those the unit's ledger records against that month, each recorded against the month it was applied to when it posted, and that a payment recorded against no invoice month is not counted. This is exactly what lc_paid sums (compute_basis.lc_paid requotes it). The late-charge rule no longer restates the base posting clause.
- R2-C2 (base-clause restatement / deferral, all members; recipe point 9):
  - Member 1, mileage: scope widened to closed-end units ended by a turn-in or by a recovery after an uncured default. The only remaining ending, a purchase, is restated with the base formula and stated as outside this policy's figure.
  - Member 1, same class, termination charge: early termination likewise now covers turn-in or recovery before the scheduled end, with the purchase ending restated as base and outside its figure.
  - Member 2, deficiency: its replaced_by restates the base net proceeds for a surplus, an even result and the sale of a closed-end unit. It no longer defers to the retired clause; the policy's figure is stated as not applying to those settlements.
  - Member 3, late charge vs arrangement payment: the late-charge rule no longer restates the posting clause, so the arrangement policy is the only rule that speaks of it. The arrangement policy retires the clause for arrangement payments and restates it for every other payment.
- R2-C3 (the arrangement payment "names the arranged deficiency", an effect no tool field records): the rule sentence and the overwrite replaced_by now say the payment is booked on the unit against its charges due, recorded against no rental invoice month and never applied to one. The remit docstring now says "recorded against no rental invoice month". This is exactly what the body writes (billing_period empty, charges due reduced).
- R2-T1 (task-1 retail late charges dated one day before the retail charter's first permissible date): moved to due date + grace 10 + 1, i.e. 2026-04-08, 2026-10-09 and 2026-11-08. Window membership is unchanged: two within 6 whole months, the April one 7 months back. Persona-independent trace and rationale text updated.
- Every seeded charge date in both tasks was re-checked against its owning charter:
  - fleet late charges (Select grace 5: 2025-09-27, 2026-03-27; Preferred grace 10: 2025-10-07, 2026-05-07) all sit on the first permissible date;
  - task-0 retail late charges (2026-03-15, 06-15, 10-15) all sit on due + 11;
  - fee payments follow their charges;
  - the settlement posts while the unit is sold.
- O2-1 (care ladders' last tier wording): tier 3 of both care ladders now reads "no active Kestrel Care Platinum, Platinum Plus or Platinum Elite contract", which is exactly the compute fall-through.
- O-6 (carried): kept by design.

## Stale-text sweep
Task rationales updated (base-invariant cards for the termination, mileage, late-charge and deficiency overwrites; the arrangement-payment business effect; the task-1 retail late-charge dates in the trace, the factor_trace, the rationale and the evaluation objective). No scored value changed (task 0: 290.00 / 1451.83 / 27.87 / 1965.25; task 1: 3907.90 / 1257.31). Step numbers unchanged.

## Pairwise method-tier table (unchanged; re-checked)
| policy | factor | tiers | distinguishing input |
|---|---|---|---|
| termination | et_remaining_term_basis | half / prorated 7-11 / flat | 7 months: 375.00 / 437.50 / 750.00 |
| mileage | em_allowance_proration | days / term / months | task-0 van: 56,575.34 / 75,000 / 58,333.33 |
| late charge | lc_invoice_part_basis | components / pre-tax / gross | October: 1,247.78 / 1,287.78 / 1,365.05 |
| refund | rf_condition_reserve | percent-of-cap / flat / none | 543.20 / 300 / 0 |
| deficiency | d_sale_expense_allowance | 5% / 8% cap / actual | 895.00 / 1,432.00 / 1,610.00 |
| arrangement | pa_term_months_rule | months to end / 3 / 1 | 9 / 3 / 1 |

## Factor-independence (transitive) and compute_basis sweep (scripted)
Every compute_basis quote, baseline sentence, policy_source and overwrite replaced_by is verbatim in its own rule. No factor binding reads another factor's binding, and no plain binding reads a factor. Combined result: 0 violations.

## Decoy / absent-record probe table (gold writes replayed unchanged; seeded decoys live in the tasks)
| world change | task 0 [ET, EM, LC, RF] | task 1 [D, PA] |
|---|---|---|
| as seeded | 290.00, 1451.83, 27.87, 1965.25 | 3907.90, 1257.31 |
| no Care contracts | 350.00, 1528.24, 27.87, 1965.25 | – |
| no balloon | 390.00, 1633.30, 30.44, 1965.25 | 4102.90, 2771.93 |
| no retail contract or ledger | 390.00, 1907.83, 12.87, 2965.25 | – |
| no retail ledger, active retail kept | – | 3907.90, 500.00 |
| no notice recorded | 365.00, 1451.83, 32.16, 1965.25 | 4107.90, 1257.31 |
| no returnable remittance | 290.00, 1451.83, 27.87, 3345.17 | – |
No probe raises.

## XF recipe check (policy x point)
| point | termination | mileage | late charge | refund | deficiency | arrangement |
|---|---|---|---|---|---|---|
| 1 assembly | OK | OK | OK | OK | OK | OK |
| 2 order | OK | OK | OK | OK (commuting) | OK | OK |
| 3 independence | OK | OK | OK | OK | OK | OK |
| 4 ownership | OK | OK | OK | OK | OK | OK |
| 5 quotes | OK | OK | OK | OK | OK | OK |
| 6 ties | n/a | n/a | OK | n/a | OK | n/a |
| 7 counting | OK | OK | OK | OK | OK | OK |
| 8 branches | OK (purchase stated outside the figure) | OK (purchase stated outside the figure) | OK (no rule branch without compute) | OK | OK (surplus/even/closed-end stated outside the figure) | OK |
| 9 base clauses | OK purchase restated | OK purchase restated, recovery in scope | OK earlier months restated; posting clause not restated | OK | OK net proceeds restated for surplus, even, closed-end | OK due date and posting restated for other cases |
| 10 rounding | OK | OK | OK | OK | OK | OK |
| 11 tools | OK | OK | OK | OK | OK | OK (docstring claims only billing period empty and balance reduced) |
| 12 proof text | OK | OK | OK | OK | OK | OK |

## Final gate block (no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 104/104, 1.json 108/108); SOLVABILITY OK; COMPUTE OK (suite means branches=58.50, steps=14.50; history_rows_max=32; branches_max=75); GROUNDING OK; CACHE-DIFF INFO (no cache trap); SCOPE OK. Traceability (pre-render): 6 misses, all unlock tool-name provenance, 0 others. Scratch scripts deleted.
REWORK round 3: gates 8/8 green

---
# REWORK round 4 (audits/policy_kb/fleet_business_servicing/ + audits/render_source/fleet_business_servicing/render_r1.md)

## REWORK round 4 closure (audit item -> change)
- SRC-1 (rules say "Kestrel retail installment contract", which also fits the pre-owned and balloon products): every rule, compute_basis quote, ladder tier and note in all six policies now names the product the compute reads, "Kestrel New Vehicle Retail Installment Sale Contract", including the retail late-charge counts ("late charges posted on the business's Kestrel New Vehicle Retail Installment Sale Contracts"). The class sweep found no other bare product phrase.
- SRC-2 (Care double coverage on one VIN): both care ladders' middle tier now reads "an active Kestrel Care Platinum contract but no active Kestrel Care Platinum Plus or Kestrel Care Platinum Elite contract", so a VIN with both falls in the upper tier, exactly as the compute evaluates. A probe with both plans on the van's VIN gives the upper-tier figures.
- SRC-3 (zero deficiency vs a positive-only amount): the deficiency rule now says a deficiency whose figure comes to nothing is booked at zero, settling the terminal rental adjustment. The deficiency tool docstring now accepts "a number of zero or more"; the body already books any amount.
- SRC-4 (docstrings claiming money movement): the refund and arrangement-payment docstrings now describe only what the bodies record: one posting with its amount and channel, and the change to charges due. The channel enum lists describe the channel recorded, and "remits" became "authorizes". Traces quoting the docstrings were updated.
- SRC-5 (task 1 notice date without a completed termination-notice request): task 1 seeds the completed termination_notice request of 2026-07-02, signed by the named signer, with a requested turn-in date of 2026-08-24, and the gold now reads it through find_fleet_requests. That is the evidence the termination clause names, so the notice credit has one reading. The replay closure matches because the row is read, not because rows were dropped.
- Evidence-clause sweep of every seeded row (both tasks):
  - delivery acceptance: each unit's in-service date now has its completed delivery_acceptance request, signed within delivery_acceptance_days of delivery (task 0: 2024-06-26 to 2024-07-01; task 1: 2024-02-26 to 2024-03-01);
  - termination: task 0's notice row was already present;
  - the task-1 closed 2019 balloon now carries its maturity election (pay_balloon), wire payoff (funding account last four in band) and electronic lien release; closed_date equals the release date, as the release trigger implies;
  - retail late charges sit on due + grace + 1;
  - Care rows are within plan options;
  - fleet late charges sit on their first permissible dates.
- N-1 (generic combination sentence present in the computation documents): kept; recipe point 2 requires that sentence in the source.

## Stale-text sweep
- Task 1:
  - step numbers shifted by the new read (calls now at 10 and 12) in computations, gold_actions and prior_step references;
  - standard-solution line and business-object card updated;
  - channel traces updated.
- Task 0: business-object card and the find_fleet_requests objective updated.
- No scored value changed.

## Method-tier table: unchanged from round 3 (re-checked).

## Factor-independence and compute_basis sweeps (scripted)
0 violations, including a check that no rule keeps a bare "retail installment contract".

## Probe table (gold writes replayed unchanged)
| world change | task 0 [ET, EM, LC, RF] | task 1 [D, PA] |
|---|---|---|
| as seeded | 290.00, 1451.83, 27.87, 1965.25 | 3907.90, 1257.31 |
| no Care | 350.00, 1528.24, 27.87, 1965.25 | – |
| no balloon | 390.00, 1633.30, 30.44, 1965.25 | 4102.90, 2771.93 |
| no retail contract/ledger | 390.00, 1907.83, 12.87, 2965.25 | – |
| no retail ledger (retail kept) | – | 3907.90, 500.00 |
| no notice recorded | 365.00, 1451.83, 32.16, 1965.25 | 4107.90, 1257.31 |
| no returnable remittance | 290.00, 1451.83, 27.87, 3345.17 | – |
| Platinum and Platinum Elite both on the van VIN | 230.00, 1375.41, 27.87, 1965.25 | – |

## XF recipe check (policy x point)
Same as round 3 except:
- point 8: the care ladders now state double-coverage precedence, and the deficiency rule's zero branch is bookable;
- point 11: refund and arrangement docstrings claim only recorded effects; the deficiency docstring accepts zero.

All 12 points OK for all six policies.

## Final gate block (no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 105/105, 1.json 113/113); SOLVABILITY OK; COMPUTE OK (suite means branches=58.50, steps=15.00; history_rows_max=32; branches_max=75); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK; TRACEABILITY OK (0 misses). Scratch scripts deleted.
REWORK round 4: gates 9/9 green

---
# REWORK round 5 (audits/policy_kb/fleet_business_servicing/_difficulty.md, "re-judge (all products final)") — seed only
The round-2 seed-realism line "5 percent capped at the 30.00 company maximum" is superseded: it followed the retired base retail clause.

## REWORK round 5 closure (audit item -> change)
- SRC-6 (every seeded New Vehicle Retail late charge was 30.00, which the published retail rules cannot produce): each charge is re-priced by the published unpaid-installment late-charge rule (docs/retail), reading the contract's own records as they stood on the charge date:
  - **Task 0** (contract 5307716482, Tier 2, monthly 949.72), charges of 2026-03-15, 2026-06-15 and 2026-10-15:
    - starting rate 3.5 percent (30 or more installments satisfied, no returned payment in 24 months);
    - less 0.5 points (clean schedule: no extension or due-date change) and 0.25 points (active Kestrel Care plans financed outside this contract);
    - no lessee or partial-effort points (no lease; no payment within the last calendar month);
    - so 2.75 percent of the unpaid installment portion 949.72 = 26.12, halved and rounded down to 13.00 at 1 day beyond grace, within the 30.00 / 35.00 caps;
    - the two fee payments are re-priced to 13.00 and fees due to 13.00.
  - **Task 1** (contract 5124409863, Tier 3, monthly 815.70):
    - starting rate 3.5 percent less 0.5 clean-schedule points = 3.0 percent; no Care, lease or partial-effort points;
    - 3.0 percent of 815.70 = 24.47;
    - 2026-04-08 and 2026-10-09 (1 day beyond grace) are halved and rounded down to 12.00;
    - 2026-11-08 falls 41 days after the next due date 2026-09-28, so it is not graduated and stays 24.47;
    - the fee payment is re-priced to 12.00 and fees due to 36.47.
  - Charge counts and dates are unchanged, so no fleet tier or scored value moves (fleet reads only counts and dates). Past-due amounts (2 × monthly payment) are unchanged.
- Sweep of every other seeded retail, balloon and Care row: no change needed, and the re-judge found them producible. That covers contract states, payments made versus elapsed installments, rate-sheet APRs, balloon percentages, the closed balloon chain and the Care plan options and limits.
- fleet.extended.yaml and task_tools.py are byte-identical to round 4 (sha256 df4ccd31… / 51595cad…).
- Proof text: each task's business-object card now states the retail late-charge pricing; no other text cited the old amounts.

## Unchanged this round (re-checked)
- Method-tier table, factor-independence and compute_basis sweeps: the charter is unchanged, so they are as recorded in round 4 (0 violations).
- XF table: as recorded in round 4 (all 12 points OK, all six policies).
- Probe table: fleet values identical to round 4.

## Final gate block (no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 105/105, 1.json 113/113); SOLVABILITY OK; COMPUTE OK (suite means branches=58.50, steps=15.00; history_rows_max=32; branches_max=75); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK; TRACEABILITY OK (0 misses).
REWORK round 5: gates 9/9 green
