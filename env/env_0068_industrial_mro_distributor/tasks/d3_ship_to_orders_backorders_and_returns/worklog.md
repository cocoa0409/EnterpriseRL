# worklog — d3_ship_to_orders_backorders_and_returns (round 1, fresh relaunch)

## Step 0 — difficulty pre-check
- Read: references (product_extended.yaml, task.json, task_tools.py), blueprint.yaml, products/order.yaml, db_schema.json, share_tools.py, XF_recipe.md;
  read-only scans of credit/pricing/vmi/vending charters for cross reads.
- Draw (draw_counts.py --tasks 2): task 0 {prerequisite_problems: 1, factor_counts: [4, 6]}; task 1 {prerequisite_problems: 1, factor_counts: [5, 5]}.
- Base defect routed around (blueprint frozen): every money-bearing d3 event (order_line_shipped, order_backorder_filled, order_fee_charged
  for every fee_type, order_return_received) triggers a credit:* event, and a special-order line cancellation triggers a fee; Principle D forbids a task
  tool from writing them. The scored quantities are therefore placed on writable events: the level a ship-to holds (variant_name on
  order_service_level_changed / order_ship_to_reactivated) and the quantity of a stock-rotation RMA line (order_return_authorized).
  See plan.md "Hard constraints".
- Scope split and tools: plan.md "Design v1".

## Task 0 — closed (per-task gates green)
- Policies order_ext_anniversary_review (4 factors) + order_ext_stock_rotation_return (6 factors); tools record_anniversary_review_a2ef3cef (agent),
  submit_stock_rotation_return_550cd403 (user). Seed builder: /tmp/d3_ship_to_orders_backorders_and_returns_0068/t0_*.py (scratch only).
- Revisions: (1) check_extended red "factors[1] reads no history" -> spend_6 moved into review_pace_window's bindings. (2) check_compute red
  "review history not load-bearing" (zeroed history still downgrades) -> rule/overwrite now leave a ship-to with no shipped merchandise in the
  12 months at its level (left to the inactivity suspension); result guards shipped_12 > 0. (3) replay closure missing 2 rows (sister ship-to's
  order lines never read) -> removed. (4) solvability: returnable_quantity evidence now cites the quantity fields; seed_consistency covers every
  primary row. (5) seed prices aligned with CPA-31206 (BR-31122 118.40 from 2025-07-01, list-less-12% before). (6) StockSmart tier set to Self-Scan
  (its 500.00 monthly minimum is met by ~1,667/month billed replenishment, so no minimum fee row is owed — XF13).
- Gate run (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Handling-time recompute: review -> Corbett Priority Ship-To (baseline Route); rotation -> 28 (baselines 19/40/40/17/27/24, all 23); skip review -> 40.

## Task 1 — design (policies already written into the charter)
- order_ext_reactivation_level (5): dormancy_level_drops, lost_route_drops (multi-source), payment_level_drops (credit), stocksmart_takeback (vmi),
  tenure_adjustment (method: halve / minus one / as added). Baseline = base rule (prior level).
- order_ext_requested_move_up (5): site_growth_window (method), replenishment_counted (vmi), standing_gate_share (credit), vending_counted (vending),
  commitment_gate_share (pricing). Scope: moves from Parcel/Standard only (self-naming overwrite), route levels stay under base.
- Consignment factor dropped: a consignment tier (Twice-Weekly / Onsite) carries a 20,000 / 80,000 monthly program minimum, unrealistic for this site.

## Task 1 — closed (per-task gates green)
- Tools reactivate_ship_to_971b9440 (agent) and elect_service_level_move_6cd24a6d (user). Seed builder /tmp scratch t1_*.py.
- Revisions: (1) replay red: 13 dangling FKs (empty vending_transactions.ship_to_id) -> field omitted on bill rows (it is only set on relocation lines).
  (2) compute red: reactivation cross-category reads not load-bearing as a whole (credit +1 and StockSmart -1 cancelled) -> world reset to two
  finance charges (2 payment drops) and 28 months of dormancy (1 drop); forced-off now gives Priority vs Standard. (3) consistency of the
  pre-suspension history with the anniversary-review rule: 26 route_truck shipments 2023-06..2024-06 so the 2024-06-12 review keeps Route Delivery
  (review spend 84,328 vs threshold 42,000) and the 2025/2026 reviews see no shipped merchandise (level kept, guard) — last_review_date 2026-06-15
  after the 2026-06-12 anniversary, so no review is owed in this world. (4) VendPoint machine_stock_value set to 0.00 (no stock movement rows
  seeded; the account invariant holds). (5) Consignment factor replaced by standing_gate_share (see design note).
- Handling-time recompute: reactivation -> Corbett Standard Ship-To (baselines Priority/Priority/Route/Parcel/Parcel; all Route);
  move up -> Corbett Priority Ship-To (every baseline Standard); skip reactivation -> move up keeps Route Delivery.

## Charter-wide revisions after both tasks
- order_ext_requested_move_up: added the overwrite of order_agg_ship_to_portfolio's entry-gate measurement clause (the move-up measure counts
  program streams and applies gate shares) — an undeclared departure found in the XF5 sweep; replaced_by restates the base clause and the
  new-ship-to portfolio exception for every other case.
- order_ext_stock_rotation_return: absent-record clauses (no declined line -> quantity 0; no credit account -> 0 percent standing).
- order_ext_reactivation_level: assembly sentence made generic ('after any adjustment made to the total itself'); no-last-order clause.
- task 0 tracing re-quoted the amended rotation sentence; both tasks rebuilt and all gates re-run.

## XF recipe (audits/render_source/XF_recipe.md) — how each point is met
1. Factor independence: mechanical sweep (transitive compute deps) finds no factor binding reading another factor's binding; the reactivation
   tenure method decides a rule code (tenure_rule) and the plain binding drops_total applies it; shared selections (rot_*, last_ship_*, program
   streams, spend figures) are plain bindings.
2. Assembly: combination lives in plain bindings (counted_12/6, review_spend, gross_allowance, allowance, drops_added/total, counted_site_*,
   move_measure, applied_gate) and is stated once generically in each rule.
3. Order: review — shares first, pace second; rotation — base adjustments, one product of percentages, deduction, cap, division; reactivation —
   sum, floor at zero, adjustment of the total, rank floor; move up — counted figures first; the two gate shares multiply (commutative).
4. No quantity is defined 'as another policy figures it'; each rule defines its measure in full.
5. Overwrites: review retires the base anniversary-downgrade half-sentence (replaced_by names its scope and excludes requested moves);
   rotation retires the return-window gate for stock-rotation returns only and restates it for every other customer-reason return;
   reactivation retires the prior-level clause; move up retires the requested-move half-sentence (restating Priority/route requests and the
   route-territory need) and the portfolio entry-gate measurement clause (restating it and the new-ship-to exception).
6. compute_basis sweep: every quote verbatim in its rule; every baseline sentence verbatim in its rule (scratch sweep, 0 misses).
7. Rounding: review and move up compare to the cent without rounding (no RND); rotation allowance RND(.,2) after the cap as stated; weighted
   unit price RND(.,4) as stated; units and halved drops use int() = rounded down as stated. The rotation allowance on the world is 1766.90625 ->
   1766.91 (half up and Python agree here).
8. Docstrings: every effect claimed is in the body; formats only (SO-NNNNNNN, RMA-NNNNNN, YYYY-MM-DD), no example values; no ordering words.
9. Edges: see plan.md probe table (ties, month-end, absent records, zero-division, None).
10. Filters: customer-reason credits (two return_reason sums), decline_reason outside_return_window, event types and ship methods are all named
    in the rules; no filter in compute is unstated.
11. Method pairwise tables: in each task's design_rationale (review pace, rotation scope, rotation unit value, tenure adjustment, growth window).
12. Line identity for the rotation: one declined line on the ship-to, named in the rule as 'the most recent ... outside_return_window'.
13. Cross-category rows: credit ledgers sum to ar_balance 0.00 with fees/charges at the tier's rates (Net 45 returned payment fee 30.00; Net 30
    Preferred finance charges 1.5%); pricing lines respect the Category Contract (competitive match 4.94% <= 5%, margin 23%); StockSmart Self-Scan
    bills meet the 500.00 monthly minimum; VendPoint Locker 12 bills meet the 400.00 minimum; programs placed while the ship-to was active.

## Final gate block (difficulty-wide, no --task)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
INSTANTIATE round 1: gates 7/7 green

# REWORK round 2 (audits/policy_task/d3_ship_to_orders_backorders_and_returns/ revision_1) — plan, written before edits
- C1/T1-1: StockSmart replenishment leaves the move-up measure (vmi_agg_program_portfolio S2 is in force and cannot be retired from this charter);
  the measure becomes own merchandise + VendPoint usage (no vending clause excludes it; grep of all charters). T1 world re-tuned (VendPoint Coil 40).
- C2/T0-1: one sentence fixes where every allowance percentage acts: the rate and the standing share multiply the adjusted purchase base in one
  product, before credits taken are deducted; the baseline sentence and S14 are reworded to say so.
- C3/T0-2: "the review date" is defined as the day the review is recorded; a review falls due on the anniversary. T0 world: the anniversary is
  the call date (opened_date 2019-10-14), so the windows end on the anniversary itself.
- C4/T0-5/T1-2: both pace/growth weight factors replaced by selection-rule methods (MN / MX / identity or since-opening annualization) with
  tenure / own-activity conditions; pairwise tables kept.
- C5/T1-3: lost_route_drops now reads route usage in the ship-to's last active year (12 months up to its last order), which divides suspended
  route ship-tos (multi-source: level AND count).
- C6: XF12 scoping in the rotation rule: one declined line on the latest declined date; one order_line_shipped shipment and no fill on the line;
  the price line must be the only line of the sku on its effective date and of the active agreement. First-match CFIELD reads of the program at
  a ship-to filtered by live status.
- C7: every rule states the whole-month counting convention (calendar-month difference, less one when the later date's day of month is smaller).
- C8: rotation scope tests stock_status / item_class against non_returnable_item_classes; zero-unit-value branch stated; "unopened" is the
  customer's statement (persona answers it).
- C9: rot_category and last_ship_date moved into their factors' bindings.
- T0-3: persona answers the bearings' condition. T0-4: credit invoice rebuilt from a real per-shipment posting. T1-O2: invoices equal the
  StockSmart bills they post, billing_cycle per_shipment. O3: gate shares stated as one product. O9: price lines limited to the active agreement.
- [r2 progress] charter rewritten policy by policy (pieces in /tmp scratch r2/): anniversary review (C3 review date, C4 review_tenure_basis,
  C7 convention), stock rotation (C2, C6, C7, C8, C9, O9, aged-stock tier), reactivation (C5 last-active-year route usage, C7), move up (C1, C4
  site_ordering_basis, terms_gate_share replacing replenishment_counted, C7, O3, O5, O6 machine-selection sentence). Sweep: every basis quote,
  baseline sentence, replaced_by and policy_source verbatim; no XF1 read across factors; no factor id inside a tool name.
- [r2 progress] task 0 rebuilt on the r2 charter (opened 2019-10-14 so the review falls due today; SO-3120577/1 440 units; INV-3381206 = 924.00 shipment invoice; persona states the bearings are sealed): per-task gates green.

## REWORK round 2 — item-by-item closure (audit revision_1)
- C1 (vmi_agg_program_portfolio S2 vs move-up): StockSmart replenishment removed from the move-up measure, compute (repl_* gone) and cross_category
  (vmi dropped from the move-up); the rule now says "StockSmart replenishment never counts in the move-up measure, program spend not counting toward a
  ship-to's service level spend". Class sweep: grep of every charter for "count toward"/"service level" — only that vmi clause; the rotation base
  (not a service-level, minimum or freight measure) and the reactivation take-back (reads program status, no spend) do not touch it. Replacement
  factor terms_gate_share (credit terms tier). T1-1 closed: no second answer from the vmi clause.
- C2 / T0-1: rotation rule now: "every percentage that sets the gross allowance multiplies the adjusted purchase base, all of them in one product that
  is the gross allowance; credits already taken are then deducted from that product, and the cap is applied last"; the standing sentence says "The gross
  allowance carries a standing share ..., the share being one of the percentages of the gross allowance". The share-after-credits reading (30) is
  excluded. Class sweep of non-commuting orders: review (shares, then the tenure selection), rotation (base adjustments, product, deduction, cap,
  division), reactivation (sum, floor 0, adjustment of the total, rank floor), move up (counted figures, then the measure; gate shares multiply).
- C3 / T0-2: anniversary rule defines the review date ("the review falls due on the anniversary and is recorded on the anniversary or ... on the first
  later day the ship-to is handled; the review date is the day the review is recorded"). Task 0 world: opened 2019-10-14, the anniversary is the call
  date, so the windows end on the anniversary itself (the realism point of the audit) and no second reading exists.
- C4 / T0-5 / T1-2: review_pace_window and site_growth_window removed. New method factors are selection rules, not weights:
  review_tenure_basis (open >= 60 months: lower of C12 and 2*C6; open < 24: higher of the two; otherwise C12) and site_ordering_basis (no own shipped
  line in 12 months: higher of C12 and 2*C6; young ship-to with shipments: C12 x 12 / months open; otherwise C12). Pairwise tables in the rationales.
  Class sweep of every method factor: rotation_base_scope (record selection), rotation_unit_value (lookup / markdown transform / invoiced),
  tenure_adjustment (halve / minus one / as added) — none is a weight or window swap.
- C5 / T1-3: lost_route_drops now reads route usage in the last active year (lines at least D and fewer than D+12 whole months back): none -> 2,
  1..5 -> 1, otherwise 0, for route levels; it divides suspended route ship-tos (probe: no route run -> Parcel instead of Standard). Multi-source kept.
- C6: (a) declined line: "the most recent being the one with the latest event_date ... with more than one such declined line on that latest date, has no
  rotation return under this rule" (compute declined_that_day); (b) shipments: scope to "exactly one order_line_shipped shipment and no
  order_backorder_filled line" (line_shipments, line_fills) so no shipment tie or fill exists; (c) price line: "latest by effective_date and the only line
  for that sku with that effective_date" on the active agreement (lines_that_date, agreement_id). First-match class: StockSmart program reads filtered
  by status (program_active_id / program_held_id); pricing and credit are one-per-customer (max_per_customer 1); the VendPoint machine read is named
  in the rule ("the one placement whose ship_to_id is the ship-to") — O6 remains an observation.
- C7: every rule carries "Whole months between two dates are the difference in calendar months between them, less one where the day of the month of the
  later date is smaller than the day of the month of the earlier date." (= MONTHS); baseline paragraphs that count months carry it too.
- C8: rotation scope tests stock_status stocked and item_class not in P('non_returnable_item_classes'), single shipment, no fill; the zero-unit-value
  branch is stated ("a line with no invoiced unit price above 0.00 has no allowance units"); "unopened" is the customer's statement and the persona
  answers it (T0-3).
- C9 / T0-6: rot_category moved into rotation_base_scope, last_ship_date into rotation_unit_value, dormant_months into lost_route_drops. Remaining
  plain single-user quantities all_merch_12 and last_ship_price are the baseline values those factors fall back to (baseline expressions name them).
- T0-3: persona: "If the agent asks about the condition of the bearings, you say all 40 are still sealed in their original boxes, never opened."
- T0-4: INV-3381206 is now the per-shipment invoice of SO-3112840 line 2's 2026-03-31 shipment (924.00, order_shipment, SO-3112840); payment,
  return, 30.00 fee and 954.00 repayment re-priced; ledger sums to 0.00.
- T1-O2 (seed class XF13): task 1 credit billing_cycle per_shipment; each invoice equals the StockSmart bill it posts; finance charges re-dated to the
  last day of the month in which the invoice was more than 5 days past due (2025-12-31 9.06, 2026-04-30 9.03 = 1.5%); VendPoint Coil 40 bills each
  above its 1250.00 minimum. StockSmart billing rows are not seeded in task 1 (nothing reads them).
- Observations addressed: O2 (basis entries for held_level, route_level_held), O3 (gate shares "in one product"), O5 (condition = status active),
  O9 (price lines limited to the active agreement). O1, O4, O6, O7, O8, O10, O11 unchanged (no consequence; recorded).
- XF recipe re-applied (all 13 points) after the edits: 1 sweep (no cross-factor reads); 2 assembly in plain bindings, generic sentences; 3 orders above;
  4 none; 5 overwrites unchanged in scope, the move-up's portfolio overwrite kept; vmi clause now followed; 6 basis/baseline/replaced_by/policy_source
  verbatim (sweep bad 0); 7 rounding: review and move up unrounded comparisons, rotation RND 2 after cap, markdown RND 4, units int(); 8 tool
  docstrings unchanged and consistent (unopened stocked standard item); 9 probes (plan.md r2 table: ties, same-date lines, absent records, zero
  usage, MX(1, months) guard, month-end day-of-month case); 10 filters stated both ways (decline_reason, stock_status, item_class, return_reason,
  agreement id, program status); 11 method tables; 12 one declined line per latest date; 13 cross-category rows priced by their charters.
- Proof-text sweep: tasks/0.json and 1.json design_rationale, prerequisite_closure, necessity/objective texts, factor_trace arithmetic and
  factor_sensitivity rebuilt from the r2 recompute (fac_detail run); grep for r1 figures and names (2019-09-28, pace, 49851, Locker 12, 21600,
  replenishment_counted, site_growth, route_runs_12 ...) finds none.

## Final gate block, rework round 2 (difficulty-wide, no --task)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
REWORK round 2: gates 7/7 green

# REWORK round 3 (audit revision_2: task 0 RED C11/T0-7, task 1 PASS, charter C10, C11)
- C11 / T0-7 (class: method factors whose tiers only change a divisor, rate or constant): swept every method factor — review_tenure_basis
  (MN / MX / identity), rotation_base_scope (different record populations), tenure_adjustment (halve / minus one / as added), site_ordering_basis
  (MX / proration / identity) change the formula's shape; rotation_unit_value only selects the divisor, so it is relabelled `effect: parameter`
  with `value` tiers (later lower contract price; invoiced price less aged_stock_markdown_pct; invoiced price). The rotation keeps 6 factors,
  5 parameter + 1 method (rotation_base_scope), so the method floor holds; no computation or figure changes (task 0 still Priority / 28).
- C10 (class: rule sentences reading a possibly-absent field without a stated branch matching compute): swept every F()/LATEST/CFIELD/XLATEST read.
  Fixed: reactivation route drops ("a ship-to with no last_order_date having no last active year and so no route drop"; compute returns 0 when
  last_order_date is empty — previously D = 0 counted the last 12 months); reactivation tenure, anniversary review tenure, move-up months open
  ("0 months where the ship-to has no opened_date"; reactivation months_open_now now guarded, it previously had no guard); rotation rate ("including
  one with no opened_date"); rotation unit value ("including where the sku has no price line on the active agreement or the customer has no active
  agreement"). Already stated and unchanged: rotation declined line / shipment / credit account / program; move-up machine / agreement / account;
  reactivation dormancy / payment / program. Probes for each absent case in plan.md (r3 table).
- Task 1 (PASS in r2) not regressed: its world has both dates, every figure and the gold are unchanged (reactivation Standard, move up Priority);
  rationale notes the r3 sentence changes only.
- XF recipe re-applied: sweep (verbatim quotes, baseline sentences, replaced_by, policy_source; no cross-factor reads; no factor id in a tool name)
  bad 0; points 1-13 as recorded for round 2 with the C10 branches added under point 9 and the relabel under point 11.
- Proof text regenerated: task 0 factor_trace / rationale label for rotation_unit_value; task 1 rationale revision note; grep for stale labels clean.

## Final gate block, rework round 3 (difficulty-wide, no --task)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
REWORK round 3: gates 7/7 green

# REWORK round 4 (audits/render_source/d3_ship_to_orders_backorders_and_returns/render_r1.md, five findings)
- Finding 1 (move-up, VendPoint machine first-match): the rule now names the machine read: "the one placement at the ship-to whose status is active,
  suspended or removal_pending (a removed or requested placement is never read, and this rule decides a ship-to with at most one such placement)";
  compute reads machine_active_id / machine_idle_id with status filters (CFIELD ... status='active', then 'suspended' or 'removal_pending').
  Class sweep of every CFIELD/first-match read of another category's holding: rotation pricing (status='active'; one agreement per customer,
  pricing_agg_multi_holding max 1), rotation credit (one account per customer, credit max 1), rotation StockSmart (status-filtered since r2),
  reactivation StockSmart (fixed, finding 2), move-up pricing (status='active') and credit (one per customer), move-up VendPoint (fixed). Probe:
  a removed machine listed first at the ship-to is never read (result unchanged).
- Finding 2 (reactivation, StockSmart read without status filter): program_tier_now = CFIELD('vmi','variant_name', ship_to_id=HID, status='active');
  the rule names "the ship-to's program whose status is active (a closed, paused, terminating or enrolled program is never read)". Probe: a closed
  Onsite Storeroom program listed first plus the active Self-Scan -> unchanged (Standard); paused only -> no take-back.
- Finding 3 (vending usage outside its factor; combination sentence naming it): vend_* bindings now belong to vending_counted (decides
  vend_added_12, baseline 0 for both periods); the factor's own sentence says how VendPoint usage is added to each period; the combination sentence
  is generic ("Additions to the site spend of a period are made first, giving the counted twelve-month and counted six-month site spend ... and the
  move-up measure is then formed from them"). The baseline paragraph says nothing about vending. Class sweep (plain bindings used by one factor
  only): none left except all_merch_12 and last_ship_price, which are the baseline quantities themselves (the baseline paragraph defines and uses them).
- Finding 4 (six-month figures defined only by a method factor): anniversary review — "The six-month spend is the same shipped and filled
  merchandise less return credits over the lines within the 6 months of the review date." is now a baseline sentence and the tenure factor no longer
  defines it; move-up — "The six-month site spend is the same merchandise over the 6 months before the request date." is a baseline sentence. The
  drop-ship / will-call / vending factor sentences name only baseline or plain quantities.
- Finding 5 (take-back vs halving order): reactivation combination sentence now "Every level drop a reactivation carries is added and every drop
  taken back is subtracted, all in one total taken as never below zero; any adjustment made to the total itself is made to that net total". Class
  sweep of non-commuting pairs: review (shares, then tenure selection), rotation (base additions, one product of percentages, credits, cap,
  division), reactivation (net total, then tenure adjustment, then rank floor), move-up (period additions, then measure; gate shares multiply) — each
  order stated.
- Scored values: none moves (check_compute recomputes task 0 Priority / 28 and task 1 Standard / Priority). Rationales carry a revision-4 note.
- XF recipe re-applied (13 points): sweep bad 0 (quotes, baseline sentences, replaced_by, policy_source verbatim; no cross-factor reads; no factor id
  in a tool name); assembly generic; orders stated; rounding unchanged; docstrings unchanged; probes refreshed in plan.md (decoy removed machine,
  closed + active program); filters stated both ways (status filters now in rule and compute); method tables current; cross rows unchanged.

## Final gate block, rework round 4 (difficulty-wide, no --task)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
REWORK round 4: gates 7/7 green

# REWORK round 5 (audit revision_4: tasks PASS, charter R4-1)
- R4-1 (multi-placement scope of the move-up): the self-naming overwrite now carries the scope. replaced_by (also rule S1 and the baseline's first
  sentence, same text): "for a ship-to holding Corbett Parcel Ship-To or Corbett Standard Ship-To with at most one VendPoint placement whose status is
  active, suspended or removal_pending, and only for such a ship-to, the move up ... is decided on the move-up measure ...; every other ship-to
  remains under the base rule, a ship-to holding Corbett Parcel Ship-To or Corbett Standard Ship-To with more such placements moving up to the next
  level when its trailing 12 month spend (its twelve-month site spend) meets that level's entry gate and keeping its level otherwise, and a ship-to
  holding Corbett Priority Ship-To or a route level ... keeping its level under this rule" — the in-force base content restated for the out-of-scope case.
  One new sentence fixes the count: "The VendPoint placements are counted over the ship-to's placements whose status is active, suspended or
  removal_pending, one for each status and VendPoint model found among them." Compute: placements_active / _suspended / _pending (a sum of
  exact-status, exact-model EXISTS reads), placement_count, base_move_result (own_12 against the raw next-level gate), and result gated on
  placement_count <= 1. Every other sentence keeps its wording and order.
- DSL limit, recorded honestly: the restricted DSL cannot count holdings of another category (XCOUNT accepts only event tables, and EXISTS / CFIELD
  see a set only as present / first), so the count is taken per status and model — the rule states exactly that convention, so rule and compute
  agree everywhere; two placements of one model in one status count once (probe recorded).
- Probes added (plan.md r5 table): two active machines of different models -> base rule -> keeps Standard; one active plus one suspended -> base rule
  -> keeps Standard; two of the same model and status -> counted once -> inside the rule (Priority). Earlier decoys (removed machine listed first,
  closed + active programs) unchanged.
- Scored values unchanged (task 0 Priority / 28; task 1 Standard / Priority); task 1 factor_trace, tracing and rationale note the placement count (1).
- XF recipe re-applied (13 points): sweep bad 0; the new plain bindings are scope tests (not factors) quoted from the scope and count sentences;
  point 5 now met for the out-of-scope multi-placement case (base outcome restated in replaced_by); point 12 applied (self-naming scope tested as a
  count of exact-status placements in compute).

## Final gate block, rework round 5 (difficulty-wide, no --task)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
REWORK round 5: gates 7/7 green

# REWORK round 6 (audit revision_5: R5-1) — plan, written before edits
- Route (a) is not available: vending_transactions usage bills carry no ship-to field (ship_to_id is set only on relocation lines), so no event-row
  filter isolates the usage of the machines at one ship-to. Route (b) chosen: the VendPoint part of the move-up is dropped entirely (factor,
  sentences, one-placement scope, placement count, cross_category vending).
- To keep the move-up measurable for a ship-to coming back from dormancy without any program stream, the method factor's first tier now reads the
  ship-to's own last active year (the 12 months up to its last order) spread over the months from the start of that year to the request date
  (x 12 / (D + 12)) — an anchor/window method, not a divisor swap of one quantity.
- Replacement fifth factor on a holding unique by its charter: credit_tenure_gate_share (the customer's single Commercial Credit Account, its
  opened_date); gate-share values re-set so every share bears weight; scope sentence reverts to Parcel/Standard with the out-of-scope cases restated.
- Task 1 world: the 2023-06..2024-06 own history is scaled so its last-active-year spend gives the same outcome (Priority) and the 2024-06-12 review
  still keeps Route Delivery; the VendPoint machine and its bills leave the world (no read). Scored values must stay Standard / Priority.

# REWORK round 6 — item record (R5-1)
- R5-1 closed by route (b): the VendPoint part of the move-up is removed — factor vending_counted, its eight bindings, the vending sentence, the
  placement-count sentence and bindings (placements_*, placement_count, base_move_result), the one-placement scope in replaced_by / S1 / baseline,
  and cross_category vending. The overwrite's replaced_by is back to the Parcel/Standard scope that restates the base clause for every out-of-scope
  case (Priority and route levels stay under the trailing spend against the higher level's entry gate, a route level also needing a ZIP inside a
  route territory). No "first listed" reading and no per-model existence count remains anywhere in the charter (sweep of CFIELD / EXISTS reads:
  pricing and credit are unique by their charters; StockSmart reads are status-filtered and unique by the vmi dedup).
- Route (a) was not available: vending_usage_billed rows carry no ship-to field (ship_to_id is set only on relocation lines), so no event-row filter
  isolates the usage of the machines standing at one ship-to; summing the customer's usage over all its machines would credit other sites.
- The method factor site_ordering_basis keeps its slot but its first tier now reads the ship-to's own last active year (the 12 months up to its
  last order) spread over the months from the start of that year to the request date (x 12 / (D + 12)); a ship-to with no last_order_date has no
  last active year and a measure of 0.00 (stated). Replacement fifth factor credit_tenure_gate_share reads the customer's single Commercial Credit
  Account (opened_date): 95 / 97 / 100 percent. Share values re-set so every share bears weight: commitment mid 94 (top 88), standing 95 / 97,
  terms 90 / 94, tenure 95 / 97. The move-up keeps 5 factors (4 parameter, 1 method); task 1 keeps multi-source (standing) and cross-difficulty
  factors (pricing, credit).
- Task 1 world: the 26 shipped lines of 2023-06..2024-06 scaled (x0.78) to 67655.10, so the last-active-year measure is 20296.53 against the gate
  19936.23 and every gate share flips the outcome alone; the 2024-06-12 anniversary review still keeps Route Delivery (63372.40 >= 51000.00);
  reactivation unchanged (Standard). The VendPoint machine and its bills leave the world (nothing reads them); persona no longer mentions vending.
  Evaluation: the two vending reads are dropped (calls now at steps 10 and 12). Scored values unchanged: Standard / Priority. Proof text rebuilt
  (factor_trace, factor_sensitivity, tracing, rationale; superseded vending notes of revisions 4-5 removed); grep for VP-320417, Coil, 19665,
  vending_counted, placement_count, 81707 finds none.
- Task 0 untouched (its policies unchanged); rebuilt and re-gated.
- XF recipe re-applied (13 points): sweep bad 0; assembly (gate shares in one product, stated) and orders unchanged elsewhere; absent-record
  branches stated for the new reads (last_order_date, credit account / opened_date); probes refreshed (two active machines of one model and a
  removed machine listed first at the ship-to: never read, unchanged; no last_order_date; short credit tenure; no credit account).

## Final gate block, rework round 6 (difficulty-wide, no --task)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
REWORK round 6: gates 7/7 green

# REWORK round 7 (audits/policy_kb/d3_ship_to_orders_backorders_and_returns/_verdict.md: kb=CLEAN, src=SRC-1,SRC-2,SRC-3)
- SRC-1 (rotation: order of the contract narrowing vs the StockSmart addition unstated): the generic combination sentence now reads "Adjustments
  to the rotation purchase base are made before any percentage is applied, an adjustment that narrows the merchandise the base counts being made
  first and an addition to the base being made after it, on the narrowed figure; ..." — by kind, matching the compute (purchase_base narrowed,
  then + program_added). Same edit in its compute_basis quote; every other sentence keeps wording and order. Probe: stated order 28; the reverse
  reading (addition first, narrowing after, dropping the uncategorized StockSmart bills) 17.
- XF3 sweep of all four policies for other unstated non-commuting pairs: anniversary review (share deductions commute; shares before the tenure
  selection, stated); rotation (rate x standing commute in one product; credits then cap then division, stated; now narrowing then addition);
  reactivation (drops and take-backs in one net total, then the tenure adjustment, then the rank floor, stated); move-up (gate shares multiply in
  one product, stated; one measure per tier). No other member.
- SRC-2, SRC-3: base-text items logged BLUEPRINT-KNOWN by the coordinator — no action (blueprint frozen).
- Scored values unchanged (task 0 Priority / 28; task 1 Standard / Priority); task 0 rationale carries a revision-7 note.
- XF recipe re-applied: sweep bad 0 (verbatim quotes incl. the edited basis, baseline sentences, replaced_by, policy_source; no cross-factor
  reads; no factor id in a tool name); other points unchanged from round 6.

## Final gate block, rework round 7 (difficulty-wide, no --task)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
REWORK round 7: gates 7/7 green

# REWORK round 8 (KB-VERDICT revision_3: src=SRC-R3-1..SRC-R3-5; seed-only)
- Charter and tools untouched: order.extended.yaml sha256 e78daed4f2c2787a..., task_tools.py aa4a300d258f6336... (verified after the edits).
- SRC-R3-1 (task 1, credit terms review): the periodic review the credit rules make due on 2026-04-14 (12-month cycle from 2025-04-14) is recorded
  (credit_accounts.last_review_date 2026-04-14), and the ledger now supports the tier it yields: per-shipment invoices for the StockSmart bills of
  2025-03..2026-03, of the 12 invoices due in the 12 months to 2026-04-14 eleven were paid by their due date (91 percent, rounded down, >= the
  Net 30 Preferred minimum 90) -> the account keeps Corbett Net 30 Preferred Account (limit 60000.00 inside 25000.00..149999.00); next review
  2027-04-14, so nothing is due on the call day. The late invoices are exactly those behind the two finance charges (INV-3388052 due 2025-12-23,
  charge 2025-12-31 9.06; INV-3389940 due 2026-04-22, after the review, charge 2026-04-30 9.03), so the reactivation's payment drops (2) and the
  move-up's terms share (94) are unchanged: gold stays Standard / Priority and every factor still bears weight (check_compute recomputed).
- SRC-R3-2 (task 1, StockSmart backing): VMI-32508 now carries its 250.00 setup fee at go-live, one scan-order bill every month since go-live
  (2023-10..2026-09, each at or above the 500.00 Self-Scan minimum, so no minimum fee is owed) and 25 bins set at go-live (the tier's bin gate);
  every vmi_replenishment invoice references a seeded bill of the same amount and date (INV-3290417 -> VSO-352006 2024-04-23; the 2024 returned
  payment's wire repayment moved to 2024-05-22, on time, so no May finance charge is owed). Two reads added to the evaluation (find_vmi_activity,
  find_vmi_bins) because their rows enter the closure; the calls moved to steps 12 / 14.
- SRC-R3-3 (task 1): CPA-32214 proposed 2025-03-18, signed 2025-04-01 inside the 30-day validity, first term 2025-04-01..2026-03-31, auto-renewed
  2026-04-01..2027-03-31 (seeded current term).
- SRC-R3-4 (both): go-live inside the Self-Scan 10 business days — task 0 enrolled 2023-02-13 live 2023-02-24; task 1 enrolled 2023-10-02 live
  2023-10-13. Task 0's program also carries its setup fee and monthly bills since go-live (2023-03..2025-08 added, all above the minimum).
- SRC-R3-5 (task 0): order lines shipped before CPA-31206's first term priced at the Corbett Account Price Schedule (list less 5 percent):
  SO-3091022/1 BR-31406 76.95 (2024-12-03), SO-3095581/1 BR-31122 140.60 (2025-06-10); the items' prior_unit_price set to the same figures.
  Both lines lie outside every scored window; task 0 gold unchanged (Priority / 28; rotation_base_scope's sku tier figure 6966.00 in the table).
- State-due sweep of the added rows: credit review next 2027-04-14; StockSmart bills end with the 2026-09 bill (the 2026-10 bill is later than
  the call date); no unpaid invoice, no owed fee or finance charge; agreements in term. Personas unchanged (neither mentions these rows).
- Proof text: both rationales carry a revision-8 seed note; task 1 credit/vmi read texts and seed-row text rewritten; grep for stale figures
  (VSO-352002/352056/352128, 2025-04-14, 2025-02-24, 2023-10-23, 2023-03-06, 71.28, 130.24, 6480) finds none. Probe table re-run (plan.md r8):
  every result identical to r7. SRC-2 / SRC-3 of round 1 stay BLUEPRINT-KNOWN.

## Final gate block, rework round 8 (difficulty-wide, no --task)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
REWORK round 8: gates 7/7 green

# REWORK round 9 (policy audit revision_8: R8-1, seed-only)
- R8-1 (task 1: Category Contract cannot survive its 2026-04-01 anniversary commitment review on 7307.05 of qualifying spend): route chosen —
  seed the customer's real purchasing, the realistic world for a customer whose Twinsburg warehouse sat suspended while its other site kept
  buying. Macedonia Cold Dock (ST-32688, Standard, active, last order 2026-10-01 as already seeded) now carries one two-line stocked order a month
  2024-03..2026-10, priced at the Account Price Schedule (list less 5 percent) before CPA-32214's first term and at the Category Contract's
  category discounts (janitorial 16, safety_ppe 15) from 2025-04-01; every order shipment of both ship-tos and every StockSmart bill has its
  per-shipment invoice (Net 30 due date) and a payment four days before due, except the two late StockSmart invoices behind the finance charges
  and the two invoices not yet due on the call date (StockSmart 2026-09 bill, due 2026-10-23; Macedonia 2026-10-02 shipment, due 2026-11-01);
  ar_balance = 5908.35 = those two open invoices (well under the 60000.00 limit, nothing past due).
- Windows re-checked with the new rows: pricing anniversary 2026-04-01 qualifying spend (2025-04-01..2026-03-31) 70163.05 >= 56250.00 -> Category
  Contract and 75000.00 commitment stand; proposal-time trailing purchases 95768.15 >= the Category entry gate 60000.00; credit terms review
  2026-04-14: 23 of 24 invoices due in the window paid on time = 95 percent >= 90 -> Net 30 Preferred stays (upgrade only on request); no new
  finance charge or returned payment (payment drops still 2; standing and terms shares unchanged); Macedonia's 2026-08-03 anniversary review
  (recorded 2026-08-04) keeps Standard on 62856.00 against 3000.00. Twinsburg's own ledger and every HID-scoped figure are unchanged, so the
  reactivation (Standard) and the move up (Priority) are recomputed unchanged and every factor and the edge still bear weight (check_compute).
- Periodic-review class swept on both worlds: credit terms reviews (task 0 next 2026-11-03, its 2025-11-03 window has no invoice -> 100;
  task 1 above), pricing anniversaries (task 0 2026-07-01 checked in r8; task 1 above), ship-to anniversaries (task 0 Euclid = the task;
  Bedford Heights' 2026-05-17 anniversary was unrecorded -> last_review_date 2026-05-18 recorded, its outcome a level kept; task 1 Twinsburg
  2026-06-15 and Macedonia 2026-08-04 recorded), StockSmart go-live anniversaries (Self-Scan cannot move down; both programs meet the gate),
  VendPoint (no machine in either world). No added row lights an obligation or leaves a write due on either call day.
- Evaluation: task 1's order-ledger read now by customer_id (both ship-tos' lines enter the closure); texts updated. Personas unchanged
  (task 1's names the Twinsburg warehouse, not the Macedonia dock). Rationales carry revision-9 notes; stale figures swept (ar 0.00, 11 of 12,
  91 percent, thirteen invoices). Probe table re-run (plan.md r9): identical to r8.
- order.extended.yaml and task_tools.py byte-identical (verified below).

## Final gate block, rework round 9 (difficulty-wide, no --task)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
    e78daed4f2c2787a
    aa4a300d258f6336
REWORK round 9: gates 7/7 green

# REWORK round 10 (policy audit revision_9: R9-1, seed-only, task 0; task 1 untouched)
- R9-1 closed as R8-1 was: task 0's credit ledger is now complete. An invoice (Net 45, priced as shipped) for every order_line_shipped and
  order_backorder_filled shipment of both ship-tos (grouped by packing list; SO-3112840 line 2 keeps INV-3381206), an invoice for every StockSmart
  bill and for the 250.00 setup fee; return credit memos CM-3305118 (202.50, RMA-305118, applied to SO-3112840 line 1's invoice, still open on
  2026-04-14) and CM-3305936 (369.00, RMA-305936, ON-ACCOUNT because its invoice was paid in full, drawn by the next payment); every invoice
  paid four days before its due date (outside the 10-day cash-discount window, so no discount) except the four not yet due on the call date;
  ar_balance 8705.70 = exactly those four open invoices; nothing past due, no finance charge owed.
- Bedford Heights (ST-31907) gets its own purchasing (one two-line order a month 2024-06..2026-09, last order 2026-09-22 as already seeded),
  priced at the Account Price Schedule before CPA-31206's first term (2025-07-01) and at its category discounts after.
- Reviews reproduced from the records: CPA-31206's 2026-07-01 anniversary review — qualifying spend 2025-07-01..2026-06-30 (shipment and
  StockSmart invoices less return credits) 104149.45 >= 56250.00 -> Category Contract and 75000.00 commitment stand; proposal-time trailing
  purchases 61026.10 >= the Category entry gate 60000.00; credit terms review 2025-11-03: 28 of 28 invoices due in its window paid on time ->
  Net 45 Business kept (next review 2026-11-03, after the call); Euclid's anniversary is the task's own review; Bedford's 2026-05-17
  anniversary review (recorded 2026-05-18) keeps Standard on its own spend; StockSmart go-live anniversary 2026-02-24 (Self-Scan cannot move down,
  gate met).
- Factor windows: every Euclid-scoped figure (review spend, route runs, drop-ship / will-call, rotation purchase base, credits taken from
  order_returns, StockSmart billed of 12 months, returned payments) is unchanged — the new rows sit on Bedford or in the credit ledger, and no
  returned payment or finance charge was added. check_compute recomputes Priority / 28 and every sensitivity unchanged; probes identical to r9.
- Evaluation: the order-ledger read is now by customer_id (Bedford's lines enter the closure); texts updated. Persona unchanged. Rationale
  revision-10 note and seed-row text rewritten; no stale "ar_balance 0.00" claim remains.
- order.extended.yaml and task_tools.py byte-identical (verified below).

## Final gate block, rework round 10 (difficulty-wide, no --task)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
    e78daed4f2c2787a
    aa4a300d258f6336
REWORK round 10: gates 7/7 green

# REWORK round 11 (KB-VERDICT revision_4: SRC-R4-1..SRC-R4-4; policy observation O-R10-1; seed-only final sweep)
- SRC-R4-1 (task 0, one list price per item): FS-30219's 2025-03-11 line (before CPA-31206's first term) re-priced at the Account Price
  Schedule from the same list price its 2026-09-09 Category price implies: list 2.30 -> 2.1850 (was 1.84). The line is 19 whole months before the
  call, outside every scored window; its invoice is regenerated from it. Class sweep (scratch price_check.py over every shipped / filled line of
  both worlds, regime by ship date: contract price where a contract item line is in force, Account Price Schedule list less 5 percent before the
  first term, category discount or list discount after it): every sku resolves to one list price in each world.
- SRC-R4-2 (task 0, drop-ship fee): each of the two manufacturer_dropship lines (SO-3100236/2, SO-3114471/2) carries an order_fee_charged row
  (fee_type dropship_fee, 10.00 Route Delivery tariff, per line, on the ship date) and its order_service_fee invoice, paid before due.
- SRC-R4-3 (task 0, go-live-month minimum): VMI-31477 went live 2023-02-24 with no spend in February -> monthly_minimum_fee 75.00 (billing period
  2023-02, dated 2023-02-28) with its invoice; 25 bins set at go-live (Self-Scan gate), read by an added find_vmi_bins node (calls now at
  steps 13 and 15).
- SRC-R4-4 (task 1, setup-fee invoice): INV-3380900 posts VPF-352900 (250.00, 2023-10-13, Net 30) with its payment 2023-11-08.
- O-R10-1 (task 0): CM-3305936 (RMA-305936, 369.00) is now recorded against the invoice the next payment settles with it (its own invoice was paid
  in full, so the credit was held on account and drawn by that payment); invoice balances now read the draw.
- Exhaustive self-sweep of both ledgers (scratch ledger_check.py): every shipment, fill, fee, StockSmart bill and program fee has its invoice;
  every return credit has its memo; every invoice is settled by payments / memos except those not yet due (task 0: 8705.70; task 1: 5908.35,
  each equal to ar_balance once the fee / finance-charge portions carried by the same payments are counted); no past-due balance; tariff fees per
  event checked (freight free on every shipment: route levels' threshold 0.00, Standard orders above 150.00; no small-order, expedite, liftgate,
  hazmat, Saturday or after-hours events; drop-ship fees now present; returns: restocking 10 percent 22.50, route pickup no label fee);
  StockSmart monthly minimums (every month since go-live at or above 500.00 except task 0's go-live month, now charged); cash discounts none
  (payments 26 / 41 days after invoice); finance charges only the two of task 1. Reviews unchanged: task 0 credit review 28 of 28 on time,
  CPA-31206 anniversary 104149.45; task 1 credit review 23 of 24, CPA-32214 anniversary 70163.05.
- Scored values unchanged (task 0 Priority / 28; task 1 Standard / Priority); check_compute recomputed every sensitivity; probes identical to r10.
  Rationales carry revision-11 notes; personas unchanged. order.extended.yaml and task_tools.py byte-identical (below).

## Final gate block, rework round 11 (difficulty-wide, no --task)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
    e78daed4f2c2787a
    aa4a300d258f6336
REWORK round 11: gates 7/7 green

# REWORK round 12 (policy audit revision_11: R11-1 only, seed-only)
- R11-1: CM-3305936 (RMA-305936, 369.00) applied_invoice_number set back to ON-ACCOUNT, as credit_evt_credit_memo requires when the invoice that
  billed the item (CT-30871's) is already paid in full; the next payment still draws on the open credit (paid 369.00 short of its invoice), so
  every balance reconciles (ledger sum = ar_balance 8705.70). Row identity, amounts and dates unchanged; rationale wording reverted (revision-12
  note). Nothing else changed; scored values unchanged; charter and tools byte-identical (below).

## Final gate block, rework round 12 (difficulty-wide, no --task)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
    e78daed4f2c2787a
    aa4a300d258f6336
REWORK round 12: gates 7/7 green

# REWORK round 13 (KB-VERDICT revision_5: SRC-R5-1..SRC-R5-4 only, seed-only)
- SRC-R5-1: go-live month bin-add fee seeded in both worlds (25 bins added, 5 included, 20 x 4.50 = 90.00, fee_type bin_add_fee):
  task 0 VPF-340902 (2023-02, invoiced with the program's other fees, paid before due); task 1 VPF-352901 (2023-10-31) with INV-3380901
  (due 2023-11-30) and ACH-3390901 (2023-11-26).
- SRC-R5-2: every StockSmart scan order's billed row is backed by vmi_replenishment_delivered rows under the same activity_reference
  (task 0: 43 bills; task 1: 36 bills), each line filling a bin to its max (quantity within [max-min, max]), priced by pricing_price_basis on
  the delivery date (Account Price Schedule list less 5 percent before the first term, contract price after); the lines add to each bill
  exactly, so every bill amount, invoice and payment is unchanged. Bins come due in the order they were last filled.
- SRC-R5-3: the 25 bins of each program hold StockSmart-only items (VM-34500.., VM-36100..), never on an order line, each a pricing_item_added
  line of the Category Contract from its first term (CPA-31206 2025-07-01, 27 contract items with BR-31406/BR-31122; CPA-32214 2025-04-01,
  25 items), contract price = list less the category's discount (other categories list_discount_pct 10), prior price = list less 5 percent;
  every item's usage in the year before its quote and in the first term is >= 12 units. Task 1 eval reads find_pricing_items (reactivation /
  election now steps 13 / 15; computations, outcomes and tracing re-indexed).
- SRC-R5-4: combined payments split into one application per document: task 0 WIR-3306104 924.00 -> INV-3381206 + 30.00 -> CHG-3307710;
  task 1 WIR-3201930 1200.00 -> INV-3290417 + 30.00 -> CHG-3202240, ACH-3391402 604.10 -> INV-3388052 + 9.06 -> CHG-3390615,
  ACH-3392215 601.80 -> INV-3389940 + 9.03 -> CHG-3391877. Each invoice applied exactly once.
- Verified: ar_balance 8705.70 / 5908.35 unchanged; no new open item, no billable row without invoice, nothing due on the call day;
  pricing reviews 104149.45 / 70163.05 unchanged; price_check all OK; review -> Priority, rotation 28, reactivation -> Standard,
  move-up -> Priority with every factor's baseline result unchanged; probes13 identical to probes11. Rationales carry a revision-13 note.

## Final gate block, rework round 13 (difficulty-wide, no --task)
    EXTENDED OK
    TASK TOOL CONTRACT OK
    REPLAY OK
    SOLVABILITY OK
    COMPUTE OK
    GROUNDING OK
    SCOPE OK
    e78daed4f2c2787a
    aa4a300d258f6336
REWORK round 13: gates 7/7 green
