# worklog — d4_stocksmart_replenishment_and_program_billing (round 1)

## Step 0
- draw_counts --tasks 2: task 0 prerequisite_problems=2 factor_counts=[6,5,6]; task 1 prerequisite_problems=2 factor_counts=[6,4,5].
- Constraint: no task tool may write vmi_replenishment_billed / vmi_program_fee_charged / vmi_buyback_billed /
  vmi_consumption_billed (unconditional trigger into credit:credit_invoice_posted). The difficulty therefore claims
  the operational writes that stay in vmi: bin entries, consigned stocking, replenishment delivery lines.
- Owner=user: the customer's own written bin requests (base: "A bin is flagged critical only at the customer's
  written request"; base: "The customer may ask to add bins, change par levels ..."). Termination notice carries no number.
- Shrink and withdrawal were considered and dropped (see plan.md "Design v2").

## Task 0 — VendPoint item onto consignment (Twice-Weekly program, Northvale Corrugated)
- Policies: vmi_ext_vended_item_fill_level (user, 6 factors), vmi_ext_consigned_reorder_point (agent, 6),
  vmi_ext_opening_consignment (agent, root, 5). Tools submit_vended_item_bin_request_0334ff8e (user),
  record_consigned_reorder_point_33b5bdc5, stock_opening_consignment_2b5b5df3 (uuid8 drawn once each).
- Harness (scratch) on the seed with simulated writes: fill-to 22, reorder point 17, opening stock 12.
  Factor baselines fill-to {usage_trend 17, restock_cover 31, route_cover 18, vend_safety 13, abc_share 24,
  payment_exposure 27}, all-baseline 19; reorder {visit_gap 16, backorder 16, rush 16, route 16, draw_buffer 15,
  supply 15}, all-baseline 7; opening {trial_level 13, credit_room 14, supply_check 13, site_age 13, return_rate 13},
  all-baseline 22.
- check_task_tools: first run failed (enum literals must be lowercase true/false; 'integer units' phrase) -> fixed -> OK.
- Task 0 tasks/0.json written by scratch builders (seed via build_t0*.py, actions/contract via build_task0*.py).
  First replay: closure 175/178 (pricing agreement and the two machines not read) -> added find_vending_machines and
  find_pricing_agreements reads -> REPLAY OK 178/178. Per-task gates on task 0: EXTENDED OK, TASK TOOL CONTRACT OK,
  REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- XF sweep (xf_sweep.py): 16 compute_basis quotes were two non-adjacent sentences joined -> basis now quotes one rule
  sentence each -> 0 findings. XF11: usage_trend rising tier used "highest month", which coincides with the
  latest-month method whenever the latest month is the peak -> rising = latest month, falling = half of latest+middle;
  pairwise on (52,35,35): 12.0 / 10.04 / 9.38. XF9: opening stock absent par entry stated as zero.

## Task 1 — slow consigned item converted during an over-limit credit hold (Onsite Storeroom, Ravenna Valley)
- Policies: vmi_ext_converted_critical_fill (user, 6), vmi_ext_conversion_reorder_point (agent, 5),
  vmi_ext_hold_converted_fill (agent, root, 4). Tools submit_critical_bin_request_f65e9169 (user),
  record_customer_owned_conversion_b1c25ecb, book_converted_bin_fill_19b3cec5.
- Seed revisions: consigned history first went negative (stockings too small) -> resized; mixed 136.80/142.50
  pricing left a -205.20 book value with zero units -> single 142.50 line; receivable 408,680 was not over the
  limit plus 10 percent -> open invoice raised, 448,680.00 (1.1217 of limit).
- Gate fixes: tuple literal in compute not allowed -> or-chain; replenish_gap had no record evidence -> reads the
  onsite daily visits completed; hold fill: XF1 (allowance share read the hold factor's credit status) -> share
  reads the hold reason only; edge fill -> request was declared value_input but the conversion entry copies the
  request's fill-to and flag, so skipping the request alone leaves the fill unchanged -> declared state_gate
  (the request -> conversion edge stays value_input: 10 vs 8); fill tool gained customer_id (credit gate binding).
- Harness/gates: fill-to 15, reorder 10, fill 7; factor baselines as in tasks/1.json factor_sensitivity.

## XF recipe (audits/render_source/XF_recipe.md) — how each point is met
1. Factor independence: every factor reads only its own evidence bindings; plain pins (item, bin, machine, visit)
   are non-factor bindings; checked by hand and by the probe runs.
2. Assembly: one generic sentence per policy ("... times the cover in weeks, which is the restock cover plus every
   added cover week, times the carried share, which is the product of every share that applies ..."); result and
   the cover/share sums are plain bindings.
3. Order: products and sums commute; the only non-commuting step (round, then add draw buffer / lumpy units; allowance
   left before division and the lesser-of) is stated in the assembly sentence.
4. No quantity is defined "as another policy figures it": the fill price is defined in full in the fill policy.
5. Overwrites: opening consignment retires "changes take effect from the next visit or scan." for its own case only
   and restates it for every other change; hold fill retires the per-visit cap clause for the converted-bin fill
   only and restates the tier cap for every other replenishment during a hold. No other base sentence is departed from.
6. compute_basis quotes: xf_sweep.py finds every quote verbatim in its rule (0 findings after the fix).
7. Rounding: rules say "taken to six decimal places and then rounded up/down"; compute uses RND(x, 6) then the
   ceiling / floor; prices "rounded half up to 4 decimal places" = RND(x, 4).
8. Docstrings: every effect claimed is in the body (create; stocking also updates the consigned value); no example
   values, formats only.
9. Edges: same-day ties (two removals / two new bins / two withdrawals -> not sized); month-age convention stated;
   absent records (no removal, no par entry, no vend, no price line) stated; zero division (credit limit 0, visits 0,
   no vends) stated and guarded; None guarded (vend price, conversion date).
10. Filters: demand machine, scheduled/onsite daily visits, ship-to, critical flag, same visit, event types — each
    stated in the rule and present in compute.
11. Method tiers change the formula shape; pairwise tables with distinguishing inputs are in each task rationale.
12. No cross-record windowing: every date test is against today (DAYS/MONTHS to NOW) on one pinned record.
13. Seeded other-category rows follow their charters: VendPoint returns only on Carousel/Locker, vend limits,
    restocks to par, machine stock values equal their ledgers; credit balances equal their ledgers, returned-payment
    fee 30.00, hold reason over_limit above limit x 1.10; expedites inside included expedites; one price line per item.

## Final gate block (repo root, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means branches 77.00, steps 18.50;
history_rows_max 93; branches_max 87); GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional). validate_scenario: the
only d4 errors are the six required documents not yet rendered (expected before KB render); no lint errors.
INSTANTIATE round 1: gates 7/7 green

## REWORK round 2 (audit revision_1: _difficulty.md F1-F8, 0.md, 1.md)
- F7 (docstrings naming another write with an ordering word): submit_vended_item_bin_request_0334ff8e and
  submit_critical_bin_request_f65e9169 now say only that the request names no reorder point (written as 0); "until
  Corbett records ..." and "quote afterwards" removed. Class sweep: grep of every docstring for before/after/first/
  then/once/next/later/until: only remaining hit was "consigned stock value after the booking" -> "including this
  booking"; the P4 tool summary no longer describes the bin as one "Corbett is taking back".
- F8 (docstring effect absent from body): book_converted_bin_fill_19b3cec5 no longer claims the line "joins the
  visit's replenishment for billing on the visit's invoice"; every remaining claimed effect is a create (and, for
  the consigned stocking, the consigned stock value update) present in the body.
- F1 (method label on window / divisor / constant swaps) — whole class closed, every method re-checked against shape:
  P0a usage_trend now projection (latest + half the rise) / recency-weighted month (3L+2M+E)/6 / plain average;
  P0b visit_gap removed (the visit gap is now the plain 30 / scheduled visits of the base) and replaced by demand_rate
  peak month / peak-and-mean blend / plain average; P5 replenish_gap and lumpy_buffer removed, replaced by safety_basis
  spread-based ((largest - average billed month) x standard days / 30) / proportional (half the standard lead demand) /
  none, plus value_class (cross pricing). P4 draw_basis tier 2 (an average over billed months = divisor swap) is now the
  peak-and-average blend. P0c trial_level and P6 fill_price_basis (substitute protection price / contract price /
  list less discount) were already shape changes. Pairwise tables with distinguishing inputs: in each rationale.
- F2 (unreachable tiers) — P0a restock_cover counts scheduled or onsite daily visits, so its Onsite tier is reachable;
  the 7-day "no visits" tiers left with the methods they belonged to (only a plain zero-division guard remains, stated in
  the baseline). Reachability re-checked for every tier of every ladder against the six vmi tiers and the other
  charters (route 0 / 1-2 / 3+ exist; hold reasons returned_payments / over_limit / past_due exist; substitute lines,
  contract lines and removals exist on every contract tier).
- F3 (P6 partial fill vs label-order stop, base fill-to-max undeclared) — P6 now declares two overwrites, each scoped to
  the first customer-owned fill of a converted critical bin during a hold: the cap clause (the fill "is not passed over
  when its whole fill would exceed what is left"; every other replenishment keeps the cap and label order) and "Every bin
  at or below its min level ... is filled to its max level" (this fill stops where the allowance stops; every other bin
  is still filled to max). One reading: 8 units.
- F4 (factors gated through hold_service) — hold_service removed as a factor; P6's scope is the hold itself (account on
  hold, critical-items-only tier, bin flagged critical; outside it the base fill applies and the schedule books nothing).
  All four factors (fill_price_basis, hold_share, conversion_release, payment_release) enter the one allowance formula.
- F5 (backorder branch only in compute) — P0b, P0c, P5 ladders now read "where some were opened and as many or more were
  filled or cancelled in those months" (the compute branch backorders > 0).
- F6 (absent-record branches) — P0b draw_buffer "or none at all, adds none"; P4 "an item with no consumption on record
  has a weekly draw of zero"; P5 lumpy_buffer removed, and its safety method states the nothing-billed case; P0a/P0b
  results "never below zero". Probe table (plan.md round 2) covers absent, None, zero-division and date edges per read.
- O8 ties — every LATEST/first-match read now has a stated tie rule: P0a removal (tie -> not sized), vend price (one
  contract price per vend date, base vend billing); P0b/P0c removal of the item (tie -> not set), special flag = any
  selection-setting entry; P0c reorder point = highest par entry; P4 special = any bin entry; P5 critical = any entry of
  the latest date; P6 fill-to = highest among latest-date entries, latest visit (tie -> not booked), latest price line
  (two on its date -> out of scope).
- O1 thin seeds — task 0: 514 bins, 11 visits, 63 replenishment and 9 billing lines, 49 price lines, 9 visit invoices;
  task 1 moved to Twice-Weekly (500-bin gate) with 518 bin entries, 47 replenishment and 9 billing lines (critical only,
  within the cap, after the hold), 44 price lines (including the three critical items O1 cited), visit invoices, payments.
  Receivables re-balanced to 149,630.40 and 448,680.00. September spend above the monthly minimum (no fee owed).
- O10 — the two March order lines of 43318 now carry 8.3580 (list 9.95 less the 16 percent safety_ppe category discount)
  since they precede the 2026-04-20 contract line.
- O2 — task 1 closure text no longer calls the 2025-11-03 entry "Corbett's". O5 — persona says crews keep drawing on the
  rings for pump repacks (no weekly claim). O6/O7/O9/O11 kept as noted observations (O11: Corbett's par entries are two
  in the month, far inside the 80 included changes).
- Proof text (PT-1, PT-2 and the task-1 "no second reading"): both rationales, factor traces, tracing and closure texts
  rewritten from the round-2 harness figures; first carousel vend 2026-05-12; usage_trend described as the projection
  it computes; task 1 second reading removed by F3.
- New figures: task 0 fill-to 26, reorder 19, opening 13; task 1 fill-to 19, reorder 8, fill 8 (sensitivities in tasks).
- Final gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (813/813, 694/694), SOLVABILITY OK, COMPUTE OK,
  GROUNDING OK, SCOPE OK; validate_scenario: only the six not-yet-rendered required documents.
REWORK round 2: gates 7/7 green

## REWORK round 3 (audit revision_2: F6, F9, F10; task 1 passed and is kept as it was)
- F6 (absent-record branch stated in the rule, not implemented) — whole class swept with sweep3.py (every MAX / XMAX /
  LATEST / XLATEST / CFIELD / CPARAM read and every consumer of it): P0b largest_draw guarded by a vend count ("or none at
  all, adds none"); P4 and P5 largest_month guarded by a consumption count ("no consumption on record -> zero"); P0c
  reorder_point guarded by a par-entry count ("zero where it has none", the round-2 regression) and fill_to guarded on the
  new-bin date; P6 fill_to guarded by the latest-date entry count; P6 contract / prior / list prices guarded on the item's
  price-line count; P6 list discount, protection days and category schedule guarded, with the new scope sentence "A
  customer with no pricing agreement on record is outside this schedule"; P6 withdrawn value guarded on the withdrawal
  date; P0c credit use and P4 limit use treat "no account on record" like no credit limit (rule sentences extended);
  P0c site age treats a missing opening date as opened today (new sentence); P0a, P0b, P5 route reads treat a service
  level not on record as adding none (new sentence; chosen over "no route" so the cross-category floor of P5 stays
  load-bearing). Every remaining unguarded read only feeds an equality filter or comparison, where an empty result selects
  nothing (listed by sweep3.py). New absent-record probes in plan.md round 3.
- F9 (shared selection inside a factor) — P6 line_kind is now a plain binding, stated once in the new rule sentence
  "The item's latest price line is its price line in the customer's agreement with the latest effective date, and its
  kind is that line's event ..."; the factor and the scope both read it. Mechanical sweep (sweep3.py) over all six
  policies: no factor evidence binding is read outside its factor, no factor reads another factor.
- F10 (other-category rows not priced by their own charter) — all seeded other-category rows re-checked:
  task 0 SO-4413870 / SO-4414112 (booked before the 2026-04-20 contract line, non-stock special order) now 5.4398
  = supplier cost 4.61 x (1 + 18 percent special-order markup) per pricing_price_basis; the four later 43318 lines and
  the backorder rows carry the contract 6.85; vending vends, returns, error credits, restocks and the withdrawal carry the
  contract 6.85 (all dated after 2026-04-20); task 1 order lines of 41827 carry the contract 142.50 (line since
  2025-01-06). Pricing tiers' contract-item minimums were not met: task 0 Net-Price now 55 lines (minimum 50), task 1
  Strategic Supply 108 lines (minimum 100), added with a separate generator so no other seeded row changed. Credit rows:
  invoice due dates at the tier's net days, returned-payment fee 30.00 (Net 45), visit and consumption invoices mapped
  as the vmi triggers map them.
- XF recipe re-applied (all 13 points, as recorded in round 2; point 6 and the F9 sweep re-run: 0 findings).
- Figures unchanged: task 0 26 / 19 / 13, task 1 19 / 8 / 8; rationales updated for the price-line counts, the two
  repriced order lines and the replay closures (819 and 758 rows).
- Final gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK.
REWORK round 3: gates 7/7 green

## REWORK round 4 (renderer source scan render_r1.md, items 1-4; policy audit revision_3 passed)
- Item 1 (two groupings of "half of A plus B") — class swept over every arithmetic sentence of the six rules: P0b
  demand_rate middle tier now "its highest month and one third of its net vends of the last three months are added
  together, the sum is halved, and the result is divided by 30" (= compute); P0a usage_trend projection and weighted
  month now state the order ("first increased by half of the rise ..., and that projected month is then multiplied by
  12 and divided by 52"; "three times the latest month, twice the middle month and the earliest month are added together
  and the sum is divided by 6, and that weighted month is then ..."); P4 draw_basis midpoint "and that midpoint is then
  multiplied by 12 and divided by 52"; P5 safety tiers "the difference between the largest month and the average billed
  month, multiplied by the standard days and then divided by 30" / "half of the product of the daily draw and the
  standard days"; P5 assembly and P6 allowance now "worked out in this order: ...". Combination order unchanged.
- Item 2 (missing "or there is none" branch) — class swept over every most-recent selection: added to P0b and P0c
  (customer removal of the item), P4 (consignment withdrawal) and P6 (no withdrawal, no service visit); P0a, P0b/P0c new
  bin and P5 already carried it. Each matches its compute guard (a count of 1 on the latest date).
- Item 3 (same-date tie on a price read) — class swept over every LATEST/XLATEST/XMAX price read: P5 value_class now
  "(zero where it has none, or where two price lines share its latest effective date)" with lines_on_price_date == 1 in
  the compute; P0a vend price is now "the highest unit price among its vends at the demand machine dated on its most
  recent vend date there" (XMAX on that date); P6 already excluded two lines on the latest date; the new P0c price read
  (item 4) carries the same rule.
- Item 4 (consigned value cap stated, not enforced) — enforced, as a real program does: P0c values the opening stock at
  the item's contract unit price on its latest price line (in effect today, alone on its date; otherwise no opening
  stock), computes the program's consigned stock value from its consigned ledger, and cuts the opening stock to the
  whole units that keep the value at or below the tier cap (cap_units, applied with MN after rounding); pricing added
  to P0c's cross_category. Same class: P0a's "consigned only on a program whose tier allows consigned bins" is now
  enforced (no fill-to level on any other tier); P6's "program whose status is active or terminating" is now enforced.
- New probes (plan.md round 4): no customer-requested removal (P0b, P0c -> 0); two price lines on one date (P0c -> 0,
  P5 -> value share 1); future-dated line (P0c -> 0); opening stock at the cap (room 13 -> 13, room 9.5 -> 9, none -> 0);
  tier without consignment (P0a -> 0); two vend prices on one date (P0a takes the highest); program paused and no visit
  (P6 -> 0). The round-3 table re-runs with identical results.
- XF recipe re-applied (13 points): basis quotes verbatim (xf_sweep 0 findings), no shared factor evidence and no
  factor reading another (sweep3), rounding sentences match RND placement, every stated restriction now in compute,
  method tiers unchanged (pairwise table in plan.md).
- Scored values unchanged (26 / 19 / 13 and 19 / 8 / 8); proof text updated for the vend-price wording, the cap check on
  the opening stock and the single price line in task 1.
- Final gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; validate_scenario: no d4 error besides the unrendered documents.
REWORK round 4: gates 7/7 green

## REWORK round 5 (policy audit revision_4: F11 three members + observation O14; both tasks passed)
- F11.1 (P3 opening stock "at the program's service visit of that day" not enforced) — enforced: visits_today = COUNT of
  visit lines dated today must be 1; new rule sentence "The opening stock is placed at the program's service visit
  dated today; where no service visit is dated today, or two or more are, no opening stock is set under this schedule."
- F11.2 (P6 "the first customer-owned fill" not enforced) — enforced: earlier_fills = COUNT of replenishment lines of
  the converted item on the program must be 0; new sentence "The fill is the bin's first customer-owned fill only while
  no replenishment line of the converted item has been booked on the program; once one has, the bin is outside this
  schedule."
- F11.3 (P4, P5, P6 "withdrawn at a par review" accepted bin-removal and program-end withdrawals) — enforced in all
  three: removal_entries = COUNT of removal entries of the converted item's bin must be 0 and the program must not be
  closed (conversion_withdrawal); new sentence in each rule "A consignment withdrawal counts as a par-review conversion
  only where the converted item's bin carries no removal entry and the program is not closed; after a withdrawal that
  follows the removal of the bin or the end of the program, no ... is set/booked under this schedule."
- O14 (prerequisite states not encoded) — encoded: P3 result requires the bin's reorder point above zero (its sentence
  "not placed until ... a reorder point above zero"); P6 result requires a latest-date entry showing the bin not
  consigned (its sentence "booked only after the bin's entries show it no longer consigned"). Closure skip-run texts
  updated (task 0: skipping the reorder point gives 0, not 8; task 1: skipping the conversion entry gives 0).
- Sweep of all six policies for further stated-but-unenforced restrictions: P1 tier / P3 cap / P6 status and hold
  (closed in round 4), P2 pin, P4 critical-on-request, P5 entry flags (tool-level), P6 "filled from empty" (a definition
  of the quantity, not a gate) — no further member.
- XF recipe re-applied (13 points): xf_sweep 0 findings, sweep3 no shared evidence / no factor-reads-factor, combination
  sentences unchanged in order, factor sets and method tiers unchanged (pairwise table in plan.md current).
- Scored values unchanged: 26 / 19 / 13 and 19 / 8 / 8; tracing for the opening stock and the hold fill now names the
  visit, reorder-point, conversion and first-fill checks.
- Final gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK.
REWORK round 5: gates 7/7 green

## REWORK round 6 (policy audit revision_5: F12, two members; both tasks passed)
- F12.1 (P5 edge E4 state not encoded) — encoded and the sentence pinned to the record state the compute tests:
  "Corbett's conversion entry for such a bin is recorded only after the bin's entries of their latest date include the
  customer's written request, a par level entry still flagged consigned that names no reorder point and sets the
  customer-owned fill-to level." Compute: request_entries = COUNT of par_change entries of the item flagged consigned
  with min_qty 0 on the latest entry date; result 0 unless > 0 ("not recorded"). entry_date moved out of hold_lead's
  bindings to a plain binding (it is now shared by the gate and the factor). Edge gate = request_entries.
- F12.2 (P6 edge E5 state not encoded) — same state encoded in P6: "That fill is not booked until the bin's entries of
  their latest date include the customer's written request for it, the par level entry naming no reorder point that
  sets its customer-owned fill-to level." result additionally requires request_entries > 0, so a bin already flagged
  critical by an earlier request gets no fill from the conversion entry alone. Edge gate = vmi_bins.min_qty.
- Only the customer's request tool writes a par level entry still flagged consigned with reorder point 0 (Corbett's par
  entries carry a computed reorder point; new-bin requests are new_bin entries), so each state-form sentence still has
  one resolving write.
- All six edges re-checked: E1, E2 (new-bin entry flagged consigned -> pins), E3 (reorder point above zero), E4, E5
  (customer request on the latest date), E6 (entry not consigned) — each waited-on state is now tested in its compute,
  and skipping the depended-on write gives the rule's not-recorded / not-booked outcome or a changed figure.
- Skip runs changed (task 1): skip the request -> conversion reorder point 0 (was 7) and fill 0; closure texts and the
  rationale's quoted prerequisite sentences regenerated. Scored values unchanged (19 / 8 / 8; task 0 26 / 19 / 13).
- XF recipe re-applied: xf_sweep 0 findings; sweep3 no shared factor evidence, no factor reading another; combination
  sentences unchanged; probes in plan.md round 6.
- Final gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK.
REWORK round 6: gates 7/7 green

## REWORK round 7 (policy audit revision_6: F13, one member; both tasks passed)
- F13 (P6 request filter consigned=True not stated in P6's rule) — a real program accepts a revised customer request
  written after the conversion (the request tool copies the bin's current consigned flag), so the compute now recognises
  the request by the fields every customer request shares: a par level entry of the item with reorder point 0 on the
  bin's latest entry date (consigned filter dropped in both P5 and P6). P5 and P6 now word the record state
  identically: "the customer's written request, a par level entry that names no reorder point and sets the
  customer-owned fill-to level"; both policy_sources verbatim in their rules; edge conditions updated.
- XF 10 sweep of every compute filter in all six policies against its rule: one further member found and closed — P6's
  customer_owned_entries counts entries of the latest date only, while its sentence said "the bin's entries show it no
  longer consigned"; the sentence now reads "That fill is booked only after the bin's entries of their latest date
  include one showing it no longer consigned." Every other filter (customer removals, demand machine, visit kinds,
  event kinds, ship-to, special/non-stock flags, critical, latest-date restrictions, consigned ledger kinds) is stated.
- Probes (plan.md round 7): a revised customer-owned request dated after the conversion -> the fill is booked; request
  and conversion the day before with nothing today -> booked on that latest date; a Corbett par entry after the
  conversion with no new request -> 0. Earlier probe tables re-run identically.
- XF recipe re-applied: xf_sweep 0 findings; sweep3 clean. Scored values unchanged (26 / 19 / 13, 19 / 8 / 8); rationale
  quotes of the two sentences regenerated.
- Final gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK.
REWORK round 7: gates 7/7 green

## REWORK round 8 (KB cross-product re-judge revision_3: src S2-S5, notes N1-N4; seed-only)
- Hashes unchanged and verified before and after: vmi.extended.yaml aa920acbff680c34, task_tools.py 805a54d8e4d6489c
  (no policy generator re-run). Scored values unchanged: task 0 26 / 19 / 13, task 1 19 / 8 / 8; S1 not routed.
- S2: CPA-41207 commitment 250,000.00 (Net-Price), CPA-44120 3,000,000.00 (Strategic Supply).
- S3: Locker 24 VP-418377 requested 2026-03-06, installed 2026-03-20 (10 business days); carousel unchanged (19 of 20).
- S4: VendPoint restocks rebuilt from the charter: scheduled visits (carousel Wed/Sat, locker Tue) restock only a
  selection at or below its trigger (6 of 30, 3 of 10) and only back to par; emergency restocks (07-09, 08-27, 10-02
  carousel; 09-21 locker) on request after the day's vends, to par. Withdrawal at the 10-12 removal now 12 units (stock
  on hand); machine stock values reconcile (0.00 / 34.25). Factor evidence unchanged (vends, returns, error, emergency
  count, largest vend, oldest vend).
- S5 task 0: every Plainfield 43318 booking ships or is wholly backordered and every backorder is filled (fills moved to
  the route days 06-29 and 09-14, promise dates on the backorder lines only); every shipment invoiced (Net 45) and paid
  when due before the call day. The six order_shipment invoices (and eleven more monthly ones 2025-09..2026-08) are
  Indianapolis sheet-plant orders with booked and shipped contract-priced lines summing exactly to each invoice. Gold read
  find_order_lines now keyed by customer (the Indianapolis lines are excluded by ship-to); proof text 09-12 -> 09-14.
- S5 task 1: both next-day-air 41827 bookings shipped the day booked and invoiced/paid; the four order invoices backed by
  booked and shipped plant lines of contract items (41827 excluded); hold onset still 2026-09-25; receivable 448,680.00.
- N1: VendPoint usage bills per machine, month and cost center (May-Sep) with one invoice each; shortfall fees from the
  first month after ramp-up (carousel Jul-Sep, locker Jun-Sep), carousel 250.00 installation fee, emergency restock
  fees 45.00 x 3 and 75.00 x 1, each invoiced; all due by the call day paid.
- N2: 2025-09 finance charge 248.46 (1.25 % of 19,876.40), dated 2025-09-30, paid by wire 2025-10-07.
- N3: 2026-Q3 Net-Price rebate accrual 1,281.69 (qualifying 128,169.14 at 1.00 %, special-order lines excluded), dated
  2026-10-01, rebate_balance 1,281.69, payout window open to 2026-11-14; no earlier quarter reaches 62,500.00. Gold read
  find_pricing_rebates added (task 0 write steps now 16 / 18 / 20; tracing, computations and rationale renumbered).
- N4: ST-40517 anniversary review 2026-06-02 recorded (trailing 210,353.00 >= 105,000.00; its trailing spend before
  2026-02-09 is 128,457.79 >= 60,000.00, so ST-41862's portfolio-allowance opening at Route Delivery is now judgeable);
  ST-44718 review 2026-09-01; Net 60 periodic credit review 2026-09-02 (on-time 100 %, tier stands).
- Receivable kept exactly: task 0 149,630.40 (ratio 0.8313, peak running balance 150,433.58 under the limit), task 1
  448,680.00. Nothing due on either call day (no open invoice due on or before it; no fee, charge, review or accrual owed).
- Rationale SEED paragraphs and closure counts (1181 / 846) regenerated; persona unchanged and consistent (gloves ran
  low in the carousel; Monday removal). Probe table (plan.md round 8) re-run identical plus new seed probes.
- validate_scenario: 0 errors. __pycache__ removed.
- Final gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK, TRACEABILITY OK (0.json 29 0 True / 1.json 26 0 True); CACHE-DIFF INFO (optional).
REWORK round 8: gates 8/8 green

## REWORK round 9 (KB re-judge revision_4: S6; seed-only)
- Hashes unchanged and verified: vmi.extended.yaml aa920acbff680c34, task_tools.py 805a54d8e4d6489c. S1 not routed.
  Scored values unchanged: task 0 26 / 19 / 13, task 1 19 / 8 / 8.
- S6 (next-day-air shipments at freight 0.00, an amount the order rules never give): no line ships next day air in
  either world now. The next-day-air bookings stay (the rush factors read bookings), but each is wholly backordered the
  next business day and filled by the level's standard method, whose freight the rules define:
  - task 0: SO-4414112 / SO-4418104 / SO-4419721 (non-stock 43318) -> BO-414112 (03-31, filled 04-02 at 5.4398),
    BO-418104 (08-28, filled 09-03), BO-419721 (10-05, filled 10-08), route truck on Plainfield route days (route
    delivery free). The backorder factors now see three opened and three filled in three months -> same tiers
    (1 day; share 0.9); proof text, computations and rationale regenerated.
  - task 1: SO-4431187 / SO-4437426 (stocked 41827, branch out of stock) -> BO-431187 (03-03, filled 03-09),
    BO-437426 (06-16, filled 06-22), ground parcel (Priority, free above 100.00). Supply cover sees two backorders in
    six months (same tier); backorder lead still reads BO-440918 alone (June is outside three months).
  - Each fill invoiced on its ship date at the price in effect; receivables held exactly (149,630.40 / 448,680.00);
    nothing due on either call day; open_backorder_value unchanged (0.00 / 4,275.00).
- Probe tables re-run identical (probe_all, round-8 seed probes); round-9 probes in plan.md. Closure 1184 / 848.
- validate_scenario: 0 errors. __pycache__ removed.
- Final gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK, TRACEABILITY OK (0.json 29 0 True / 1.json 26 0 True); CACHE-DIFF INFO (optional).
REWORK round 9: gates 8/8 green
