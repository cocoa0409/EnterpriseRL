# returns_and_exchanges — instantiation worklog (M=2)

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3, factor_counts=[6, 4, 4, 5]
- task 1: prerequisite_problems=3, factor_counts=[5, 5, 4, 6]

## Difficulty-level feasibility findings (Step 0)
- Writable money events in this category without a cross-category trigger: returns_refund_credited,
  returns_fee_assessed (method / restocking / missing box), returns_refund_issued only with tender
  card_or_wallet, returns_instant_credit_reversed only with recovered_from original_card,
  returns_hold_placed / released / captured. Stored-value refunds (credit_issued /
  credit_refunded_to_instrument), RSC clawbacks (credit_clawed_back), exchange shipments
  (orders_placed) and the settled transition (loyalty_points_reversed) trigger into other categories,
  so no tool of this difficulty writes them (worlds are laid so none of them is owed in-task).
- Customer-owned acts with an amount: the Instant Exchange card hold (blueprint) and the cardholder's
  authorization of a new charge on the original card for instant store credit already spent
  (declared as an overwrite of returns_evt_instant_credit: the base sentence "any shortfall already
  spent is charged to the original card" now requires the cardholder's own authorization, as any
  merchant-initiated card charge does). Two disjoint user tools are therefore available, one per task.
- A tree with >= 2 value_input edges needs a consumer reading the return's ledger (card refund or
  card recovery) or fees reading the credit entry; feeders are credit, restocking, box and method fee.

## Base defects routed around (base untouched)
- returns_settled triggers loyalty:loyalty_points_reversed unconditionally, so the settled status move
  is never written by a returns tool; settlement entries (credits, fees, refunds, recoveries) are the
  desk's writes and the status move posts with the loyalty reversal (outside these tasks).
- returns_line_inspected lists credit / fee triggers dated at inspection; the extended charter books the
  credit entry and the inspection fees through the desk (blueprint: the agent "books fees") on the day
  it books them.
- returns_evt_exchange: the hold_consent gate binds return_cases.return_id to a caller statement, so
  the Instant Exchange RMA number (the number the customer sees on the confirmation) is in the persona.

## Tasks
- task 0 (E-task): root courtesy return-by extension (agent) <- sg <- spent-credit card charge (user)
  <- vi <- restocking fee, credit entry; restocking <- vi <- credit entry.
- task 1 (H-task): root Instant Exchange card hold (user) <- sg <- final card refund on the order's
  earlier return <- vi <- method (return shipping) fee, missing-box fee.

## Gate runs
(appended below as they run)
- task 0 verification run (authoring script, handling-time replay through the real tools):
  every declared factor of returns_ext_line_credit (4), returns_ext_grade_b_restocking (6),
  returns_ext_spent_credit_recovery (4) and returns_ext_courtesy_extension (5) moves `result` when its
  baseline is substituted; every whole-baseline differs from gold; skipping the credit entry changes the
  restocking fee and the card charge, skipping the restocking fee changes the card charge.
- task 0 per-task gates (first pass): REPLAY OK (after widening reads so every seeded row is in the
  closure and dropping unread Unlimited ledger rows), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK,
  TASK TOOL CONTRACT OK; EXTENDED NOT OK only because task 1's four tools are not yet named by a policy
  (and a module-level helper was counted as a tool -> inlined).
- task 1 verification run: every factor of returns_ext_return_shipping_fee (6), returns_ext_shoebox_fee (5),
  returns_ext_final_card_refund (4), returns_ext_exchange_hold (5) moves `result`; whole baselines differ
  from gold; skipping either fee changes the card refund; booking the two fees in either order gives the
  same refund (they commute).
- task 1 per-task gates: first REPLAY run showed 2 seeded return lines (old jeans return) outside the
  closure -> the two return-line reads merged into one customer-wide read; re-run REPLAY OK; EXTENDED,
  TASK TOOL CONTRACT, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK.
- final difficulty run (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK,
  COMPUTE OK (suite means branches 86.50 / steps 23.50; history_rows_max 9; branches_max 89),
  GROUNDING OK, CACHE-DIFF INFO (no cache trap designed), SCOPE OK.
- check_traceability NOT run: it needs the published KB (docs/), which does not exist yet.

## Known limits to watch in the audits
- The final card refund and the spent-credit card charge are ledger consumers; their factors are
  payout/recovery rules (shipping refund for a not-as-pictured return, write-offs, spend goodwill), and
  the refund_due measure of base no longer nets to zero once they apply.
- Several factor ladders are stylized desk rules (courtesy-extension day ladders, hold shares, label
  reliefs); each is declared as an overwrite of the base clause it replaces.
- Old settled returns used only as loyalty-reversal anchors are seeded as return_cases rows without
  their own lines/settlements (except task 1's jeans return, which carries its full settlement).

## Rework round 2 — closure of audits/policy_task/returns_and_exchanges (_difficulty.md, 0.md, 1.md)
- F-F1 line_credit.post_list_reductions: removed. The base net unit price paid (all post-list reductions) is now
  the baseline itself; new parameter factor claim_compensation_taken_off (claims, cross-difficulty; base claims
  "never compensated again ... through a return"), seeded as a Damaged in Transit Claim with a Goodwill Credit on
  the tote line in task 0.
- F-F1 exchange_hold.exchange_value_basis: tiers are now three distinct methods (reference price recorded on a
  price adjustment / price paid for a promoted line / booked price).
- F-F2 relabels: grade_b_restocking.return_frequency_multiplier -> parameter; shoebox_fee.pair_price_class and
  box_return_frequency -> parameter; final_card_refund.delivery_charge_tax_refund -> method; line_credit's split
  restructured as parameter delivery_charge_taxable_share (the tier selects the taxed share of the delivery
  charge entering one fixed formula); spent_credit_recovery's goodwill -> parameter spend_goodwill_share.
- F-F3 counts: spent_credit_recovery gains method spend_history_window (24/36/12-month spend history by tier;
  claims fee-share factor dropped); shoebox_fee gains method reversal_counting_window (6/18/12 months by tier;
  delivery-service share dropped; task 1 seeds a 2025-08-18 reversal inside 18 months, outside 12);
  line_credit now 2 parameter + 2 method.
- F-P1 return_shipping_fee: closing formula now "the label fee times the number of labels, ..."; label-fee
  baseline sentence says "charged for one label per return".
- F-P2 E5/E6 sentences scoped to return types carrying those fees (conditions updated).
- F-C1 shoebox cap now reads the pair's net unit price paid from the order, not the credit entry.
- F-C2 not changed: an edge from the final refund to the restocking fee would merge the two prerequisite
  components (task 1's tree would absorb task 0's policies); no world in this difficulty has a grade B unit on a
  return refunded to the card, recorded as residual.
- F-G2 restocking cap applied after the frequency multiplier (declared in the replacing sentence).
- F-G3 final card refund capped at the card's refundable remainder (captures less refunds on the order and on
  this return); remainder follows the orders charter's priority. Residual: refunds of other returns on the same
  order are not readable by the DSL (primary-category scoping).
- O-G2 effect wordings generalised; O-G3 waiver tiers (restocking, shoebox, label) read as held since on or
  before the authorization date; O-G4 extension window honours loyalty_window_extension_applies and cites
  returns_authorization (holiday/footwear windows not expressible in the DSL - residual); extension start-date
  tier 2 compute now equals its rule; fee tools accept 0.00 ("non-negative ... 0.00 when fully waived").
- Task 1 finding 5: half-up rounding now exact in the refund compute (half_up_nudge); baseline figures recomputed.
- Task 0 obs. 5/notes: rationale no longer asserts a status move; tools_do_not_block names all four tools.
- Residual observations kept: O-G1 (state_gate gates name table fields, as the template allows), exchange_hold
  single-line / single-active-instrument reads, returns_evt_method_fee cited by restocking and shoebox because it
  governs every returns_fee_assessed subject (gate requirement).

## Rework round 3 — closure of audits/policy_task/returns_and_exchanges revision_2 (_difficulty.md, 0.md, 1.md)
- F-R2-1 / 0.md R2-A: returns_ext_line_credit.overwrite gains a second entry on returns_evt_refund_settlement whose
  superseded_clause quotes base's value sentence ("For each line, the value credited is the net unit price paid —
  ... — times the accepted units") and whose replaced_by is the rule's claim-compensation sentence. Checked it
  retires no eligibility gate (neither refund_settlement gate condition contains or is contained in it). Task 0
  rationale no longer grounds the deduction in the claims charter; it cites the declared overwrite.
- F-F3 spent_credit_recovery / 0.md R2-B: spend_history_window (window length N by tier) replaced by method
  spend_measure_basis: Platinum/Icon/Atelier = better membership year (larger of the last 12 months' and the
  prior 12 months' earned qualifying spend); Gold = gross spend (earned qualifying spend, 12 months); otherwise =
  kept spend (earned less reversed_spend_usd of reversals, same months). Params senior/gold/base_spend_months
  replaced by spend_year_months 12; spend thresholds unchanged. Task 0: Gold gross 1595.50 -> x0.9; baseline kept
  1234.10 -> x1; card charge, its trace, sensitivities and the two value_input skip figures recomputed.
- F-F3 shoebox_fee / 1.md R2-A and O-R2-2: reversal_counting_window replaced by method return_rate_measure over one
  12-month span for everyone (no longer a longer look-back for Silver/Gold): Platinum/Icon/Atelier by points
  (points reversed over earning + bonus points), Silver/Gold by value (reversed spend over earned qualifying
  spend), otherwise by count (reversal postings over orders placed); zero when nothing to divide by.
  box_return_frequency thresholds are now rates (frequent_return_rate 0.5 -> 2, regular_return_rate 0.2 -> 1.5).
  Task 1: Silver by value 261.00/1166.40 = 0.224 -> x1.5; baseline by count 3/3 -> x2. Shoebox fee, final card
  refund (value_input from it), traces, sensitivities, skip figures recomputed; the 2025-08-18 reversal is now a
  near-miss outside the 12 months. Two read-step descriptions corrected (orders read now names three earlier
  orders; the pass-membership read had carried the ledger read's wording).
- 0.md R2-C: restocking compute adds K('half_up_nudge') 0.000001 before each RND (per-unit percentage, multiplied
  fee, final), so "rounded half up" holds on binary floats: scan_timing 25.43 and return_reason 15.26; gold
  unchanged.
- O-R2-1: E4 condition (charter and task 0 prerequisite_closure) now reads "whose instant credit exceeds its credit
  entries less its fees withheld plus its store-credit balance" (no "carried").
- Residuals unchanged: F-C2 (no grade B line on a card-refunded return in this difficulty; an extra edge would
  merge the two components); F-G3 remainder routing outside the tools; O-G1; O-G4 partial (footwear/holiday/QI
  windows not expressible).
- Gates after round 3 (full block, no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0: 78/78, 1: 56/56),
  SOLVABILITY OK, COMPUTE OK (suite means branches 99.50 / steps 23.50; history_rows_max 9; branches_max 103),
  GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. check_traceability not run (no published KB).

## Rework round 4 — validator lint (forbidden 'from datetime')
- task_tools.py: dropped `from datetime import date, timedelta`; extend_return_deadline_be33eaa2 now adds the
  extension days with inline calendar arithmetic (month lengths, Gregorian leap rule, carries both ways), no
  helper function. Checked identical to date + timedelta on 200,000 random dates/offsets (-1500..1500 days).
  No other tool, docstring, charter or task file changed.
- Gates re-run (full block): EXTENDED, TASK TOOL CONTRACT, REPLAY (78/78, 56/56), SOLVABILITY, COMPUTE (branches
  99.50 / steps 23.50; history_rows_max 9; branches_max 103), GROUNDING, SCOPE OK; CACHE-DIFF INFO.
  validate_scenario: only the 8 expected "required document ... not found" errors remain for this difficulty.
