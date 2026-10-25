# worklog — d5_vendpoint_usage_and_machine_billing (vending), M=2

## Step 0 — difficulty pre-check
- Read: references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/vending.yaml,
  db_schema.json (vending_*, credit_*, ship_to_accounts, vmi_*, pricing_*), share_tools.py (verify K=2),
  audits/render_source/XF_recipe.md.
- Base closes: lifecycle requested/active/suspended/removal_pending/removed; removal notice is by:user.
  Base automatic clauses: monthly usage bill on the last day of the month; monthly shortfall/badge/cellular fees;
  install fee at installation; slow-mover removal at planogram reviews; credit-hold lock; cycle counts (shrink for
  locker/smart crib). Each seeded world is checked against them (no un-carried obligation lit).
- Draw (draw_counts.py --tasks 2):
  {"task": 0, "prerequisite_problems": 1, "problems": 2, "factor_counts": [4, 6]}
  {"task": 1, "prerequisite_problems": 2, "problems": 3, "factor_counts": [6, 4, 6]}
- Headroom: task 0 claims the selection/emergency pair (planogram + emergency fee); task 1 claims the monthly
  shortfall, the installation fee and the removal notice. Disjoint events within vending_fee_charged by fee_type.
- Known risk recorded: vending_fee_charged / vending_usage_billed declare an unconditional trigger into
  credit:credit_invoice_posted. The blueprint d5 claim and summary name fees as this difficulty's writes and no
  other vending write carries a customer-in-person amount, so fee rows are written; the task tools write only the
  vending fee line (no credit row), the invoice posting being the billing consequence of the line.

## Task 0 — emergency restock on an emptied coil (root) <- start-up par review
- Design decision log: hidden prerequisites must be state-due writes visible in the records (credits need a customer
  report, so they cannot be hidden); per-object DSL scope = the machine, so the par review is scoped to "the item most
  recently added" (highest planogram request reference, deterministic). Draw {"prerequisite_problems": 1,
  "factor_counts": [4, 6]} -> par review 6, emergency fee 4.
- Capability card resize_selection_par_58ce1bb4 (agent, write): object = one selection of one machine; atomic action =
  create one vending_selection_set entry (par_change, change_source corbett, today, new VPC reference), category and
  special flag copied from the selection's entries; no trigger; receipt keys status, vending_slot_id,
  vending_machine_id, slot_label, sku, par_qty, change_reference, effective_date.
- Capability card place_emergency_restock_request_36839656 (user, write): object = one machine; atomic action =
  create one vending_fee_charged line (fee_type and billing_period as given, amount given, VER reference, today);
  trigger credit:credit_invoice_posted is the billing consequence (not written); receipt keys status, vending_txn_id,
  request_reference, fee_type, emergency_restock_fee, billing_period. fee_type/billing_period are parameters because
  the base dedup gate one_monthly_fee_per_machine binds them on every vending_fee_charged write.
- Handling-time run (scratch v_t0.py): A on opening world -> 37 (factor baselines 30/31/44/46/31/41, all-baseline 32);
  B skipping A -> 35.00; B after A -> 17.50 (factor baselines 35.00/30.00/26.25/8.75, all-baseline 60.00).
- Revisions: (1) ceil written -int(-x) gave floor (36) -> int(-(-x // 1)) -> 37. (2) dedup gate needs fee_type and
  billing_period args -> added; October source row = replacement badge card fee VBC-552840 (2026-10-05, 2 x 4.00).
  (3) replay: empty FK strings flagged -> ship_to_id None on non-relocation lines; unread vmi_activity rows dropped
  (credit invoices of VV-557104/381/652 keep the StockSmart minimum visible); order lines read by customer so the
  ST-51843 decoy is in the closure; ship-to and pricing-agreement reads added.
- Method pairwise tables. demand_pattern_basis (avg a, largest v, starter s=24, trigger t=0.25): tier1 max(a,v);
  tier2 max(a, s(1-t)) [only when v<a and days<28]; tier3 a. Distinguishing input a=8, v=10 (tier1 10), a=8,v=5,days 20
  (tier2 max(8,18)=18), a=8,v=5,days 40 (tier3 8): pairwise distinct. visit_schedule_callout (fee f=60, interval i=3.5,
  days d): tier1 0; tier2 f*i/d; tier3 f. d=8 -> 0, d=6 -> 35, d=3 -> 60; tier2 equals tier3 only at d=i (belongs to
  tier3); all coincide only when f=0 (no callout is ever booked, rule's own sentence).
- Probe table (scratch copies of the world, verify.py):
  | read | decoy / absent | result |
  | LATEST add entry by change_reference | later-dated customer par_change VPC-518022 (filtered by change_type) | still VPC-517641 |
  | CFIELD vmi program (status active) | no active program -> None | bins 0, backup 1.0 |
  | XCOUNT bins new_bin vs removal | removed AB-50926 bin, other-sku critical bin | AB-53318 only, 1>0, critical False |
  | CFIELD credit status (closed_date '') | a closed older account would be skipped; absent account -> None | factor 1.0 unless returns >= 2 |
  | XCOUNT returned payments 12m | 2025-09-08 return (13 months) | excluded, count 1 |
  | XLATEST contract line by effective_date | earlier lines; a later removal line would win | substitute line PCH-552311 |
  | XSUM order shipped 3m, ship-to filter | ST-51843 shipment, June AB-50926 line | 10 units |
  | LATEST scheduled restock | 2026-09-02 emergency visit (visit_type emergency) | 2026-10-08; none on record -> days 0 -> full fee |
  | COUNT Corbett par change today | absent (opening) | 0 -> no relief (35.00) |
  | COUNT emergency fees 3m | June-or-older fee outside window | 1 |
  Edges: days_in_machine 0 -> counted 1 (MX); avg uses visits per week >= 1 for every model; ceil on exact integers
  verified (baseline 32.0 -> 32).

## Task 1 — removal notice (root) <- month shortfall fee, installation fee
- Draw {"prerequisite_problems": 2, "factor_counts": [6, 4, 6]} -> shortfall 6, installation 4, early removal 6.
- Capability cards: charge_month_shortfall_fee_b04c8474 (agent; one vending_fee_charged line, reference = billing
  month), charge_installation_fee_f4f2dbbd (agent; one fee line, VIN work order reference),
  give_machine_removal_notice_4669343a (user; sets the machine removal_pending with today's notice date and books the
  early removal fee line, VRN reference — notice and fee are one written-notice act). Receipts: status,
  vending_txn_id, txn_reference, fee_type, amount, billing_period (+ termination_notice_date for the notice).
- Dedup-gate sources (fee_type / billing_period must be system values): usage_shortfall_fee from the June line,
  install_fee and early_removal_fee from the removed sibling VP-547730 (its 2023 installation and 2025 early removal),
  2025-12 / 2026-09 from the December / September bills, 2026-10 from the October badge card line VBC-562977.
- Handling-time run (scratch v_t1.py): C 43.95 (factor baselines 70.95/88.95/60.83/60.83/88.95/58.60, all 298.60);
  D 41.67 (62.50/125.00/66.67/58.33, all 250.00); E after both 1153.33 (1625.83/1258.33/945.00/1678.33/1573.33/
  1363.33, all 3500.00); skip C -> 995.83, skip D -> 1195.00; C after D 43.95, D after C 41.67 (commute).
- History pricing: June/July/August shortfall lines recomputed with the shortfall compute on the world as of each bill
  date (8.65, 79.82, 81.16; April 0, May 0); September emergency fee 22.50 recomputed with the emergency rule as of
  2026-09-09. Revisions: September emergency moved from a non-empty bay to the test-lead bay emptied 2026-09-09 (first
  draft placed it where the ledger showed stock); planogram rows dropped (no read uses them).
- Method pairwise tables. plant_shutdown_share (minimum m, days n, paused p): tier1 0; tier2 m(n-p)/n; tier3 m —
  p=30/n=30 -> 0, p=5 -> 2500, p=0 -> 3000. installation_lead_basis (fee f, lead L, actual a): tier1 0 (a>2L); tier2
  fL/a; tier3 f — a=45 -> 0, a=30 -> 166.67, a=18 -> 250. agreement_fee_basis (fee f, term T, run r): linear
  f(T-r)/T; stepped f(T/12-(r//12+1))/(T/12); flat f — r=9,T=36: 2625 / 2333.33 / 3500. Linear equals stepped
  only if 36-r = 24-12(r//12), i.e. r = 12(r//12)+12, impossible; flat equals linear only at r=0 and stepped never
  (stepped <= 2/3 f), so the three never coincide on a reachable run month.
- Probe table (scratch probe_t1.py): closed Onsite StockSmart program listed first at the ship-to -> ignored (C 43.95,
  D 41.67); later credit-hold pause line -> ignored (C 43.95); January shutdown pause -> not latest; 2026-03-30 vend
  error credit -> outside six months; 2026-06-18 shipment -> outside three months; sibling fee lines -> other
  machine. Absent records: no StockSmart program -> fall-through tiers (C 115.95, D 58.33, E 1475.00); no agreement ->
  full rates (C 58.60, D 125.00, E 1431.25); no usage bill -> no month is tested (rule scope); plant shutdown lines
  always carry a planned last day (VMI charter), credit-hold pauses are filtered; installation on the request day ->
  lead 0, full fee, no division; no scheduled restock -> days 0, full callout.

## XF recipe (13 points) — how each is met for all five policies
1 Factor independence: scratch check of each factor's bindings — no factor binding reads another factor's binding;
  shared reads (months_run, avg_interval, trigger_fraction, model fee, month_end) are plain bindings stated once.
2 Assembly only in plain bindings/result (sized_units, tested_minimum, credited_usage, result), each stated once in a
  generic "To size / To fix / To figure" sentence that names categories (allowances, factors, shares, reliefs, credits)
  not factor quantities.
3 Order fixed where operations do not commute: shortfall (minimum first, then credit, then shortfall, rate, rounding,
  cap); early removal (basis x record x (1 - credits), floor, then recovery added, rounding at the end); par
  (allowances added, factors multiplied, divided by trigger, ceiling at the end).
4 No quantity is defined "as another policy figures it": the emergency fee reads Corbett par change entries, the early
  removal fee reads shortfall and installation fee lines — records, not another policy's figure.
5 Overwrites retire only conflicting clauses and restate the in-force remainder with self-naming scopes (shortfall:
  machines tested on their own; installation: cellular fee kept; removal: notices with three months left, later
  notices stay under base at removal; emergency: every other fee stays under base). The two vending_evt_fees clauses
  retired by C and E are different sentences from B's; no sibling retires the same clause.
6 Every compute_basis quote verbatim in its rule — scratch sweep: 0 misses in 5 policies; every binding claimed.
7 Rounding: par "rounded up to a whole unit only at the end" = int(-(-x // 1)) on the final product; fees "rounded to
  the cent only at the end" / shortfall "rounded half up to the cent and only then capped" = single RND in result
  before MN; world values avoid half-cent ties.
8 Docstrings: every effect named is in the body (fee line, machine status/notice date, par entry); no example values
  (sweep: no e.g./for example/such as; formats described only).
9 Edges: same-day ties — add entries chosen by highest request reference; latest usage bill / pause line by date with
  single candidates; MONTHS convention stated in words ("a month counting once the same day of the month is reached";
  "fewer than N whole months separate its date from today"); absent / None / zero-division branches in the probe
  tables above.
10 Filters stated both ways: change_type add_item / par_change, change_source corbett, visit_type scheduled,
  pause_reason plant_shutdown, closed_date '' (open program / account), status active (agreement), ship-to filter on
  order lines, fee_type filters — each appears in its rule sentence.
11 Method tiers change the formula shape (max with peak vend / max with starter cover / average; zero / proration /
  flat; zero / lead proration / flat; linear / stepped / flat); pairwise tables above with distinguishing inputs.
12 No cross-record date windowing: per-object reads use one candidate (latest add entry, latest bill, latest pause
  line); windows run from today only.
13 Cross-category seeds are charter states: Category / Net-Price contracts with a discontinued-substitute line priced
  at the old contract price (pricing protection rule); StockSmart Weekly / Twice-Weekly programs with bins and plant
  shutdown pauses within pauses_per_year and pause_max_days; credit ledgers with returned payments carrying the 35.00
  fee and certified-funds repayments, no hold below the hold count; order lines with route / parcel methods and free
  freight thresholds met; VMI spend minimums met via replenishment invoices.

## Final gate block (difficulty-wide, traceability excluded until docs exist)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means branches 45.50, steps 17.00;
history_rows_max 76; branches_max 57) / GROUNDING OK / CACHE-DIFF INFO (optional) / SCOPE OK.
validate_scenario: only "required document ... not found" for d5 (KB not rendered yet).
INSTANTIATE round 1: gates 7/7 green

## REWORK round 2 — audit audits/policy_task/d5_vendpoint_usage_and_machine_billing/ (revision_1), item by item
- F-C11 (P3 shutdown ladder was one proration formula labelled method). Changed: plant_shutdown_share is now an honest
  parameter ladder (>= 10 paused days -> unpaused share; 1-9 days -> short-shutdown share 0.95; none -> 1), and P3's
  method factor is the new contract_usage_basis, which selects HOW the usage tested is taken: Strategic -> larger of
  the month's usage and the prior month's usage (two-candidate selection); Net-Price / Cost-Plus -> larger of the
  month's usage and the three-month bill average; otherwise the month's usage. The old contract_rate_share (same
  agreement condition) was removed so no two factors repeat a condition. Class swept: every method ladder in the
  charter (pairwise table below); P1, P2, P4, P5 were already distinct and stay so.
- F-C5 (a) P5: overwrite #1 replaced_by and rule now say a later notice carries "the model's early removal fee ...
  once at removal", no deferral to the retired base clause. (b) P2: replaced_by and rule now keep only "the
  relocation, model swap, replacement badge card and planogram change fees named with it" under that base sentence.
  (c) P3: scope is now "a machine that is not tested as part of a pooled site under the site minimum rules", which
  covers the mixed-site machine. Class swept: all five overwrite tails re-read; P4's tail keeps the cellular half; no
  extended rule defers to a clause any overwrite retires.
- F-C9 (month counts, rolling windows, ties). Each of P1, P2, P3, P5 now carries one convention sentence ("Whole months
  between two dates are counted as the difference in calendar months, less one when the day of the month of the later
  date is before the day of the month of the earlier date; a record counts in a stated number of months ending today
  when fewer whole months than that number, counted this way, separate its date from today"), and every month count
  and window sentence says "counted this way" / "counted by <date>": P1 add-entry age, units, returned payments, order
  units; P2 repeat lines; P3 ramp-up ("the model's number of full calendar months following the installation month"),
  months in service, the two- and three-month bill windows, spend; P5 months run, the three-month scope ("months run
  at most the minimum term months less three"), shortfall lines, shipments, faults. Ties: P3 pause line = highest pause
  reference (both dates read from that one line, date_field activity_reference); P1 bin = latest bin set entry by
  highest bin request reference; P1 contract line replaced by "a substitute line and no removal line" (no tie possible);
  P2/P1 planogram references now issued in sequence by the tool (O3).
- F-C10 (P1 bin filter). Rule now states "the item's latest bin set entry ..., new bin or par change", matching the
  compute's vmi_bin_set filter; only member.
- F-C8 (docstring effects). Removed every "program billing" claim and "for the current billing month" from the three
  fee tools; docstrings now claim only the vending line and its fee history. Re-read the skill's trigger rule: the
  tools write no other category; vending_fee_charged's unconditional trigger into credit:credit_invoice_posted is the
  billing consequence the credit side posts; the blueprint's d5 claim names these fee events as this difficulty's
  writes and no other d5 event carries an amount, so the writes are kept and this is flagged to the coordinator as
  the one open interpretation (no tool claims or performs the credit posting).
- T1-F1: closed by F-C11 (P3 now has contract_usage_basis as an honest method; tier taken Net-Price 590.98 vs month
  usage 511.65).
- T1-F2 (119.00 vend error credits above the 75.00 desk limit credited same day). Seed now dates them on the next
  restock visits that confirm them (2026-07-16, 2026-09-24); the 21.80 credit stays a same-day desk credit. Class swept:
  the only other vend error rows (task 1 VE-562140, none in task 0) are within the limit.
- T1-F3: closed by F-C5 (b).
- Observations taken up: O1 P2 thresholds renamed twice-weekly / weekly (values unchanged); O2 P5 basis tiers swapped
  (Strategic = stepped by contract year, Net-Price / Cost-Plus = pro rata), so Strategic is never charged more on the
  same inputs; O3 sequential VPC references; O5 zero-fee months book no line (P2, P3 rules); O7 bindings now include
  month_first, month_days (shutdown) and term_months (fee basis); O8 quiet-site tier now also requires no open
  StockSmart program at the ship-to, and task 1's Dearborn ship-to is suspended (last order 2025-07-28, Route Delivery
  inactivity 12 months), so the idle-site tier (0.35) is the one taken; O9 holidays counted as weekdays stated;
  T1-O2 sibling early removal recomputed by P5 as of its notice (1108.33) with the ST-52608 shipment of 2025-01-14
  seeded; T0-O1 rationale multi-source list corrected; T0-O2/O3 persona no longer volunteers the substitute history and
  says "since yesterday morning"; both personas' consent lines are now generic ("Whatever the agent says Corbett has to
  do on its own side, you let them go ahead without questions").
- Seed history re-priced by the reworked P3: the month-end fee run of a month is made early in the following month
  (as-of worlds 2026-05-04, 06-02, 07-02, 08-03, 09-02): April-June 0.00 (no line), July 84.01, August 102.39.
  Sibling installation 250.00 recomputed as of 2023-09-11 with no agreement then in effect.
- New gold: task 1 shortfall 74.28 (baselines 83.80/85.08/142.68/99.93/99.93/134.28, all 298.60), installation 41.67
  (unchanged), early removal 917.08 (1153.33/995.83/708.75/1507.70/1743.95/1153.33, all 3500.00); skip C 798.96,
  skip D 958.75. Task 0 unchanged: par 37, emergency fee 17.50 (skip par review 35.00).
- Method pairwise table (distinguishing inputs): P1 demand_pattern_basis (a=8, v=10 -> 10; v=5, days 20 -> 18; v=5,
  days 40 -> 8); P2 visit_schedule_callout (d=8 -> 0, d=6 -> 35.00, d=3 -> 60.00); P3 contract_usage_basis (u=511.65,
  prior=623.20, avg3=590.98 -> 623.20 / 590.98 / 511.65); P4 installation_lead_basis (a=45 -> 0, a=30 -> 166.67, a=18
  -> 250.00); P5 agreement_fee_basis (r=9, T=36 -> stepped 2333.33 / pro rata 2625.00 / flat 3500.00; stepped equals
  pro rata only if 36-r = 24-12(r//12), impossible).
- Probe table round 2 (scratch probe_r2.py): second pause line same record day, higher reference, 12 days -> share
  18/30, fee 0.00; no pause line -> share 1 (85.08); whole-month pause -> 0.00; Strategic -> 70.42 (E 775.00);
  no-tier agreement -> 83.80 (E 1037.50); fee run on the 31st sees only two bills in the three-month window (rule
  behaviour as stated, 83.80); Dearborn active with an open StockSmart program -> no quiet credit (E 1529.69); active,
  no StockSmart, no shipments -> quiet credit (E 1628.13); task 0 later removal entry for the bin -> no bin carried
  (par 44); item removed from contract -> no substitute allowance (31); no contract lines -> 31; two Corbett entries
  today, highest reference PPE -> relief 1.0, fee 0.00 (no line). Earlier probes (round 1) still hold.
- XF recipe re-applied (all 13): scratch sweep — basis verbatim 0 misses, every binding claimed, baseline sentences in
  rule, no factor binding reads another factor's binding, no code tokens in rules, no factor id inside a tool name;
  assembly only in plain bindings / result; order sentences unchanged (P3 updated to "every share ... reliefs ...
  credit ... rate ... rounding ... cap"); overwrites per F-C5; rounding sentences match RND placement (world values
  checked for no half-cent ties: 74.282, 917.08); docstrings per F-C8; edges per probes; filters stated both ways
  (P1 bin set filter, P5 open-program condition); method shapes per table; no cross-record windowing; cross-category
  seeds re-checked against their charters (order suspension rule, credit returned-payment fees, pricing effective
  dates, VMI pauses within pauses_per_year / pause_max_days).
- Proof text swept: design_rationale (both), prerequisite_closure, tracing, factor_trace, sensitivities,
  solvability seed checks and read-node objectives regenerated from the reworked builders.
- Gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 2: gates 7/7 green

## REWORK round 3 (audits/policy_task/d5_vendpoint_usage_and_machine_billing/{_difficulty,0,1}.md read in full; coordinator ruling applied)

### Ruling: no task tool writes vending_fee_charged or vending_usage_billed
- Both events declare an unconditional trigger into credit:credit_invoice_posted, so every row of them satisfies it. The four fee tools are removed (place_emergency_restock_request_36839656, charge_month_shortfall_fee_b04c8474, charge_installation_fee_f4f2dbbd, give_machine_removal_notice_4669343a). So are the four policies only they served (emergency restock, month shortfall, installation fee, early removal notice): no task triggers them now, so they were dropped rather than kept unused.
- Every scored write is now one of three vending events whose base `triggers` are []: vending_selection_set (resize_selection_par_58ce1bb4, place_substitute_selection_72f4b244, set_substitute_selection_par_5d8137ae), vending_item_returned (return_startup_item_units_bfc1c22c) and vending_vend_error_credited (credit_retired_item_vends_2f4f7780). I checked these in blueprint/products/vending.yaml. Unlock, move, swap and removal-notice events were considered and rejected: they carry no figure a computation could fix.
- Step-0 draws are kept exactly:
  - task 0: n=1, [4, 6]. Root start-up return (4 factors) ← start-up par review (6).
  - task 1: n=2, [6, 4, 6]. Root substitute settling par (6) ← substitute placement (6) ← retired-item vend credit (4).
- Customer-owned writes that carry a computed figure:
  - task 0: the return's unit credit, 5.74;
  - task 1: the par change, 46.
- Why this design is the most realistic one within the ruling:
  - A start-up item that ran out between visits, and units an employee returns unused, are everyday VendPoint events. So is a retired contract item whose bay keeps logging vends after it runs out, which Corbett must credit and replace with its approved substitute (the pricing charter's discontinued-item protection).
  - Every per-object choice is identified from records:
    - the newest add entry by planogram reference;
    - the removal and substitute lines by the highest change reference;
    - the latest vend by its vend timestamp.
- Seeded fee and usage-bill rows survive only as base-producible history, each with its credit invoice:
  - the Carousel 90's one-time 250.00 installation fee: task 0 VIN-551274 / INV-5214988; task 1 VIN-562219 / INV-5326615;
  - monthly usage bills per cost center, each with its invoice.
  No emergency, badge, shortfall or removal fee row remains. Both machines sit inside ramp-up, so no minimum is ever tested.

### Item closures
- **T1-F4 (XF-13, other-category reference formats), closed as a class.**
  - Neither world seeds any vmi_activity row, so no pause reference exists to carry the wrong prefix.
  - A script swept every reference field in both worlds:
    - credit: INV/ACH/ADB/WIR/RTN/CHG;
    - order: SO/PL;
    - pricing: SPQ/PCH;
    - vmi: VBR/VMI;
    - vending: VT/VRS/VR/VWS/VIN/VPC.
  - Every reference conforms to its charter, and every minted number starts with 5.
  - The other-category rows were re-checked against their charters:
    - The T0 removal notice was moved to 2026-07-24, giving the Category Contract its 30 days' notice. The substitute lines carry no notice date, because added lines have no such field. Each substitute is billed at the discontinued price inside the protection days.
    - The T0 competitive match of 6.85 → 6.55 is a 4.4 percent cut (limit 5 percent), leaves a 23 percent margin (floor 8 percent), and uses a quote 7 days old (limit 30).
    - The T1 Net-Price removal gives 31 days' notice.
- **F2-C1 / T1-F5 (mislabelled effect), closed as a class.**
  - plant_shutdown_share was dropped together with the shortfall policy.
  - Every factor of all five policies was swept by its tier contents:
    - Each `parameter` tier selects a K() constant, 1 or 0.
    - Each tier that computes a formula sits in a factor labelled `method`: fill_level_shape, dispense_unit_basis, substitute_demand_basis, settling_demand_basis, demand_pattern_basis.
  - The first draft of the return policy had a "contract_price_source" factor whose tiers read different price fields. It was removed: its tiers coincided with the prior vend price in the world, and it made the cross-category read decorative. The price is now the base read, the current contract unit price.
- **Charter observations from round 2:**
  - Closed with the dropped policies: O4, O8, O10, O11, O12 and O14.
  - O3 (sequential references): all four new tools issue VPC/VR/VE as one above the highest on record (`_Ledger.next_reference`).
  - O15 (rounding mode): "rounded half up to the cent" is stated in the return and credit rules, in their baselines and in the tool param descriptions. The tools round half up (`_Ledger.cents_half_up`). Every scored and counterfactual figure was checked exactly, and none sits on a half cent.
  - O6 (unconditional baseline sentence inside the rule) remains the accepted pattern.
  - O13 (DSL month convention) is unchanged.

### XF recipe, 13 points × 5 policies
1. **Independence.**
   - sweep_r3.py reports 0 issues: no factor binding reads another factor's binding.
   - In the placement policy, the order-sized method tier was replaced by a largest-vend tier, because it read the channel factor's order units.
   - Shared selections (retired units, average, ledger, price) are plain bindings.
2. **Assembly.** Each policy states its combination once, generically:
   - return: "shaped by the fill level first and then multiplied by each share that applies";
   - credit: "one plus the service shares that apply added together";
   - placement and settling par: "one plus the allowance that applies and then by each share and factor that applies".
   No factor is gated through another factor.
3. **Order.** The non-commuting step in the return (the subtractive overstock shape) is stated first. Every other step multiplies or adds. Ceilings and RND apply only at the end.
4. **No "as another policy figures it".** Each policy defines its own ledger, units and average where it uses them.
5. **Overwrites.**
   - return: retires base S4 (return credit basis) for start-up returns of the newest item only, and states that every other return stays at the vend price.
   - credit: retires the report-hours sentence only for a retired item's vends logged after it ran out, and keeps the desk limit.
   - settling par: retires "The customer may ask … par quantities …" only for par changes on a Corbett-placed substitute in its first three months.
   - P1 and placement have no overwrite; neither departs from a base sentence.
6. **Verbatim.** Every compute_basis quote, replaced_by, baseline sentence and policy_source is verbatim in its rule (sweep).
7. **Rounding.**
   - RND appears once, at the result (return and credit), and matches "rounded half up to the cent only at the end".
   - Ceilings appear once, at the result (pars), and match "rounded up to a whole unit only at the end".
8. **Docstrings.** Every claimed effect is in the body: the sequential reference, the copied item, category, badge and price fields, and the consigned stock update on returns and credits. No example values appear.
9. **Edges.**
   - Ties: planogram LATEST by the sequential VPC reference; removal and substitute lines by the sequential PCH change reference; the latest vend by timestamp.
   - Month convention: stated in each rule.
   - Absent and None cases are stated and guarded: no removal line or no vend → no credit owed; no list price → step 1; no contract line → latest vend price, or share 1.
   - Zero division is guarded: lot 0, list price 0.
   - All of these appear in the probe table in plan.md.
10. **Filters.** Every compute filter is stated in its rule:
    - event types, change_type add_item, change_reason discontinued_substitute;
    - the active program at the ship-to;
    - shipped lines to the machine's ship-to.
11. **Method shape.** Each method tier computes a different formula. The pairwise table with distinguishing inputs is in plan.md.
12. **Cross-record windows.** None remain: the windowed price-source tier was removed, and every DAYS test pairs a record date with today.
13. **Other-category seeds.** See T1-F4 above.

### Fresh recomputation (scratch harness over check_compute.build_env)
- **Task 0** (frozen 2026-10-05 10:40 EDT):
  - Par review: 28.
    - baseline 20;
    - demand 19, wear 23, backup 33, exposure 35, lead 23, channel 31.
  - Start-up return after the review: 5.74.
    - baseline 6.55;
    - fill 6.04, trial 5.92, return rate 5.85, handling 5.92.
  - Skip the review: 5.35.
- **Task 1** (frozen 2026-10-07 14:20 EDT):
  - Credit: 50.76 (4 units).
    - baseline 28.20;
    - dispense 38.07, category 41.36, delay 48.88, storeroom 48.88.
  - Placement after the credit: 55.
    - baseline 60;
    - demand 67, wear 37, list step 46, bin 65, exposure 69, channel 61.
    - Skip the credit: 56.
  - Settling par: 46.
    - baseline 50;
    - demand 42, wear 31, bin 54, exposure 57, value 51, channel 51.
    - Skip the placement: 108. Skip the credit: 47.
- All proof text (argument tracing, factor traces, prerequisite closure, solvability, seed consistency, design_rationale) was regenerated from these runs. The round-2 tasks were backed up to scratch r1/ and are not reused.

### Gate block (round 3)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK (0.json 17 acts, closure 239 = init 239; 1.json 19 acts, closure 283 = init 283)
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK
- Info only:
  - check_cache_diff: optional.
  - check_traceability flags the unlock tool names as not yet reachable. They enter the agent's context through the KB render, which comes after this step.
REWORK round 3: gates 7/7 green

## REWORK round 4 (audits/policy_task/d5_vendpoint_usage_and_machine_billing/{_difficulty,0,1}.md revision_3 read in full)

### Item closures
- **F3-C1 / T1-F7: vend error semantics. Closed as a class; the retired-item credit is the only vend-error writer.**
  - The credit now follows the base event:
    - one credit against the one failed vend;
    - quantity = the units that vend did not dispense;
    - unit price = the price billed on that vend;
    - credited once, so one_credit_per_vend holds.
  - The overwrite is scoped and self-naming: "for a retired item whose shortfall is no more than the units of its latest vend and only for such a vend".
    - That scope guarantees the latest vend is the only vend that dispensed fewer units than it logged (XF-12).
    - A larger shortfall stays under the base rules: the probe gives 0.0.
  - Report hours: the overwrite retires only the report-hours sentence, for that scope. The desk-limit sentence is kept.
  - The carousel round-up to whole vends is gone. The dispense method is now:
    - carousel or locker: the shortfall;
    - crib: the shortfall less the shrink-tolerance units;
    - otherwise: the vend's units (the baseline, the whole vend reversed).
  - Task 1 world: the latest vend VT-5626378 logged 2 units with 1 in the bay, so the ledger is -1. The credit is 1 unit at 11.592 × 0.9 = 10.43.
- **O16: credit above the amount billed. Closed.**
  - The credit is the units not dispensed × the billed price × min(1, late-find share 0.5 + shares). It can never exceed what was billed for the missing units.
  - At most the shares reach 0.95, so the cap never has to bind: the probe gives 11.01 against the 11.59 billed.
- **F3-C2 / T0-F1: prerequisite effect text. Closed as a class, all three edges rewritten to the move that happens in the world:**
  - start-up return: overstock handling charge → near-full credit share (ledger 24 = old par 24; 24 ≥ 22.4 under the new par 28);
  - placement: retired units 260 → 259, sizing tier unchanged, par 56 → 55;
  - settling par: moves into the settling tier with interval usage max(9.9615, 55 × 0.2) = 11.
  - The task closures and rationales repeat the same moves.
- **F3-C3: ties and the removal-line branch. Closed as a class.** No price read orders by "latest effective date" any more:
  - start-up return: credits the price paid (see O17) and reads no contract line.
  - placement: the retired item's list price comes from its new-item line with the highest quote reference.
  - settling par: the value share reads the contract price on the substitute line with the highest change reference.
  - Removal and substitute lines are chosen by the sequential change reference.
  - Latest-vend reads in the return and credit policies now order by the sequential vend transaction number, so there are no same-second ties (probe: a re-timed decoy at 7.10 → still 6.00).
  - No "current contract unit price" read remains, so the removal-line branch cannot arise.
- **F3-C4: "larger of" grouping. Closed as a class.** Every "larger of" with an operand expression now reads "the larger of two figures, A and the product/quotient of …":
  - placement T2;
  - settling par T1;
  - start-up review T2.
  These match MX(a, b op c). The compute is unchanged.
- **T1-F6: vend prices after a removal. Closed as a class.** Every other-category-priced row in both worlds was re-checked against pricing_price_basis:
  - Task 1: every SF-55233 vend on or after the 2026-09-14 removal (26 vends, 51 units) is priced at 13.80 less the Net-Price safety_ppe discount of 16 percent = 11.592. The September usage bills and their invoices are recomputed from those rows.
  - Task 0: the AB-50926 removal now takes effect on 2026-08-26, after 30 days' notice from 2026-07-27. Its last vend and its 2026-08-25 withdrawal therefore fall while its contract price stood. The AB-53318 substitute line takes effect the same day.
  - Both worlds: no vend falls on or after the task 0 competitive match. All restocks are priced at contract while the contract stood. Order lines are at contract, or at the protected substitute price.
- **O17: return price. Closed.**
  - The start-up return applies only to a return against the newest item's latest vend.
  - It is figured from the price paid on that vend: 6.85 for VT-5515953, the returned vend.
  - Today's 6.55 competitive match is a near-miss the rule ignores.
  - The task 0 vend order was swapped so that the caller's 3-unit vend by badge 57769 (10:28) is the latest vend. The 2-unit vend by badge 57716 (07:01) is the decoy.
- **O18: persona echoing a rule phrase. Closed.** The task 1 persona says he "has no number in mind and wants Corbett to work out what the bay should carry". No rule phrase is echoed.

### XF recipe, 13 points (re-applied)
1. **Independence:** sweep_r3.py reports 0. The dispense method owns its tolerance-units read.
2. **Assembly:** generic, once per policy.
3. **Order:** stated.
4. **"As another policy figures it":** none.
5. **Overwrites:**
   - start-up return: scoped to returns against the newest item's latest vend; every other return stays at its vend price.
   - credit: scoped as above; the desk limit is kept.
   - settling par: unchanged.
6. **Verbatim:** sweep clean.
7. **Rounding:** RND half up only at the end (return, credit); ceilings only at the end (pars). Stated in each rule, baseline and tool description.
8. **Docstrings:** unchanged; every claimed effect is in the body; no examples.
9. **Edges:** ties, absent records, None, zero division and the scope edge are all probed (plan.md round 4 probe table).
10. **Filters:** stated (change_reason new_item and discontinued_substitute; event types).
11. **Method shape:** pairwise table in plan.md (round 4).
12. **Cross-record windows:** none; the credit's single-candidate scope is stated.
13. **Other-category seeds:** see T1-F6.

### Fresh recomputation
- **Task 0:**
  - Par review: 28.
    - baseline 20;
    - demand 19, wear 23, backup 33, exposure 35, lead 23, channel 31.
  - Start-up return: 6.00.
    - baseline 6.85;
    - fill 6.32, trial 6.19, return rate 6.12, handling 6.19.
  - Skipping the review gives 5.62.
- **Task 1:**
  - Credit: 10.43.
    - baseline 11.59;
    - dispense 20.87, category 7.53, delay 9.27, storeroom 9.85.
  - Placement: 55.
    - baseline 60;
    - demand 67, wear 37, list step 46, bin 65, exposure 69, channel 61.
    - Skipping the credit gives 56.
  - Settling par: 46.
    - baseline 50;
    - demand 42, wear 31, bin 54, exposure 57, value 51, channel 51.
    - Skipping the credit gives 47; skipping the placement gives 120.
- No figure sits on a half cent. Exact products checked: 6.000447, 10.4328, 11.592, 20.8656, 7.5348, 9.2736, 9.8532.
- All proof text was regenerated from these runs and swept for round-3 figures.

### Gate block (round 4)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK (0.json closure 239 = init 239; 1.json closure 280 = init 280)
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK
REWORK round 4: gates 7/7 green

## REWORK round 5 (audits/render_source/d5_vendpoint_usage_and_machine_billing/render_r1.md read in full)
This round changes wording and binding ownership only. The compute expressions are unchanged except for the move of bindings into factors, so no scored value moved:
- task 0: 28 / 6.00;
- task 1: 10.43 / 55 / 46.
Every sensitivity and every probe result is the same as in round 4. probe_r3.py was re-run and its output diffs empty against round 4.

### Item closures
- **A1 (start-up return).** units_loaded, units_vended, units_back and units_out are now bindings of fill_level_shape, alongside stock_ledger, selection_par and fill_tier. The stock-ledger and selection-par definitions now sit inside the fill-level sentence only; the separate ledger sentence was removed.
- **A2 (retired-item credit).** last_vend_date is now a binding of credit_delay_share. Its definition is in the delay sentence only.
- **A3 (placement).**
  - avg_interval and trigger_fraction are now bindings of substitute_demand_basis. The average's definition moved into the method sentence ("its average per restock interval, those units divided by …"), and was cut from the retired-units sentence.
  - retired_par left the method's bindings. It is the baseline's quantity: "The standard par is the retired item's par …".
- **A4 (settling par).** add_date is now a binding of settling_demand_basis.
- **Same class elsewhere, by mechanical check.** Definitions of method-only quantities were folded into their factor sentences:
  - settling par: starter par and largest single vend;
  - start-up par review: largest single vend and starter par.
- **Mechanical check (owners2.py).** For every factor it lists the bindings read transitively (output in scratch). It confirms:
  - no plain binding is read by only one factor unless the baseline uses it;
  - no factor owns a quantity the baseline uses.
  - Result: 0 violations across the 5 policies.
- **B1–B5 (assembly naming a factor quantity, and the result defined twice).** Each rule now defines the result once:
  - The baseline sentence names the standard figure: "The standard par …", "The standard unit credit …", "The standard credit value …".
  - Each method sentence states that it replaces a named quantity of that standard figure, and its ladder method texts say "… replaces the …" / "… stands".
  - The assembly sentence is generic: "each method that applies first replaces the quantity of the standard … it names; … the allowances that apply … each share and factor that applies …, rounded … only at the end". It names no quantity a factor decides.
  - Order by kind (the start-up return has the one non-commuting step): "so that a charge a method subtracts comes before any share; each share that applies then multiplies the figure".
  - Credit: "the shares that apply are then added to the late-find share, that sum never above one". The late-find share is a baseline parameter.
- **C (resize docstring).** The unsupported claim "applies from the next restock visit" was removed. The docstring now claims only the entry the body writes and the receipt it returns.
- **Proof text.** One stale rule quote in task 0 was fixed ('never more units than that vend issued'). Every rule phrase quoted in either task was re-checked as verbatim in its rule. Both tasks were regenerated.

### XF recipe, 13 points (re-applied)
1. Independence: sweep 0, ownership check 0.
2. Assembly: generic; one definition per result.
3. Order: by kind.
4. "As another policy figures it": none.
5. Overwrites: unchanged.
6. Verbatim: sweep 0.
7. Rounding: RND half up and the ceiling only at the end, matching the assembly sentences.
8. Docstrings: resize fixed; the other four were re-read and pass.
9. Edges: probes unchanged.
10. Filters: unchanged.
11. Method shape: the pairwise table in plan.md (round 4) still holds; the formulas are unchanged.
12. Cross-record windows: none.
13. Other-category seeds: unchanged.

### Gate block (round 5)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK
REWORK round 5: gates 7/7 green

## REWORK round 6 (audits/policy_kb/d5_vendpoint_usage_and_machine_billing/{_verdict,0,1}.md read in full)

### SRC-1: a "no value" case against a zero value. Closed as a class.
- **The member.** In `vending_ext_substitute_placement`, list_price_step treated a substitute list price of 0 as a ratio of 0, giving the cheaper share of 1.2. The rule says "no list price" gives a share of one. The published pricing KB says protected substitute lines carry list price zero.
- **The fix.**
  - Rule (and its price_step basis): "otherwise, or when either line carries no list price or a list price of zero, the share is one."
  - Compute: `list_ratio` is 1.0 when sub_list is None or 0, or retired_list is None or 0.
- **New probes:** substitute list price 0 gives 46 (step 1); retired list price 0 gives 46 (step 1).
- **Class sweep of every absent/zero read in all five policies.**

| policy | read | absent case | zero case | rule and compute |
| --- | --- | --- | --- | --- |
| start-up return | latest vend price | no credit | MX(0, …) gives 0 | consistent |
| retired-item credit | latest vend quantity | out of scope | out of scope ("shortfall more than the units of its latest vend") | consistent |
| retired-item credit | latest vend date | delay 0 | — | consistent |
| retired-item credit | backup program | "no such program" share | — | consistent |
| substitute settling par | substitute contract price | share 1 | 0 is "below the mid value price", share 1 | consistent |
| start-up par review | days in machine | — | counted as one | stated |
| all | critical flag (bin_critical) | "not flagged critical" | — | consistent |
| all | open credit account | "otherwise one" | — | consistent |
| placement | retired item's largest vend | "ever vended" false | "ever vended" false | consistent |

  The list-price step was the only member.

### SRC-3: rule words for record fields. Closed as a class.
- "the highest quote reference (Corbett issues quote references in sequence)" now reads "the highest change reference (Corbett issues these references in sequence)". This is the pricing_items field change_reference, which the compute sorts on. It appears 3 times: the rule, the retired_list basis and the list_ratio basis. The task 1 proof text and rationale were swept to match.
- Every other reference word in the five rules was checked against the field descriptions in db_schema and the events, and each matches:

| rule word | record field and its description |
| --- | --- |
| "change reference" | pricing_items.change_reference |
| "planogram request reference" | vending_planogram.change_reference, "Request reference." |
| "bin request reference" | vmi_bins.change_reference, "Request reference." |
| "vend transaction number" | vending_transactions.txn_reference, "Vend transaction number from the machine log" |

- Field words also match: list price, contract unit price, unit price, product category, par, effective date, flagged critical, new-bin and bin removal entries, add entry, non-catalog special item, and "written as a new item / removal / Corbett-approved substitute for a discontinued item" (change_reason).

### SRC-2
SRC-2 is a placement note the coordinator is not routing. The combining sentence is left as it is.

### Regression check
- No scored value moved:
  - task 0: 28 / 6.00;
  - task 1: 10.43 / 55 / 46.
- All sensitivities are unchanged. The probe outputs equal round 5 plus the new line.
- sweep_r3.py reports 0 issues and owners2.py reports 0 violations.
- XF recipe re-applied:
  - 9 (absent and zero edges) and 10 (filters stated) gain this round's changes;
  - all other points are unchanged from round 5.

### Gate block (round 6)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK
REWORK round 6: gates 7/7 green

## REWORK round 7 (seed-only; audits/policy_kb/d5_vendpoint_usage_and_machine_billing/{_verdict,0,1}.md revision_3 read in full)
vending.extended.yaml (8b0a7e3be1a7ee56) and task_tools.py (1dee5f0cb4c3247b) are byte-identical; both hashes were checked after the run. Only other-product seed rows, one new read step per task, and proof text changed. The seed patches are seed_t0r7.py and seed_t1r7.py (scratch), applied after the vending builders.

### Item closures
- **SRC-4 / SRC-5 (StockSmart).** Both programs are now StockSmart Self-Scan. Self-Scan is the floor tier with a 25-bin gate, which keeps the world proportionate.
  - **Enrollment and go-live:** each program goes live 10 business days after enrollment:
    - VMI-55210: 2026-04-20 → 2026-05-04;
    - VMI-55618: 2026-03-02 → 2026-03-16.
  - **Bins:** each holds 25 bins at go-live. The existing bins were re-dated and re-referenced in sequence (VBR-5511xx / VBR-5561xx). The new bins carry contract items.
  - **Fees:** a 250.00 setup fee, and a 90.00 bin-add fee for the 20 adds beyond the 5 included in the go-live month. Each fee has its own fee row and invoice.
  - **Scan orders:** every self-scan order has:
    - its scan row (self_scan_order);
    - one delivery row per bin, filled to max, priced at the contract price on the delivery date, delivered 2 business days after the scan;
    - one billing row and one invoice. Freight is 0 under Route Delivery terms.
  - **Monthly minimum:** every month's program spend is above the 500.00 minimum, so no minimum fee is owed.
  - **Par reviews:** Self-Scan has no par reviews, so no idle-bin removal is owed.
  - **Old invoices:** the three unbacked VV- invoices in task 0 and their payments were removed.
  - **Scored rows kept:**
    - AB-53318's plain bin (VBR-551204);
    - SF-55233's opened-and-removed bin (now VBR-556101 / VBR-556188);
    - SF-55247's plain bin (VBR-556189).
- **SRC-6 (credit limit).** The task 1 credit limit is now 45000.00, inside the Net 30 Standard band.
- **SRC-7 (agreements).**
  - Task 0, CPA-55107 (Category Contract):
    - commitment 75000.00;
    - first term 2025-11-01 to 2026-10-31, status renewal_pending since the 60-day window opened (it auto-renews; nothing is owed on the call);
    - 25 contract items (22 new_item lines SPQ-551823..551844).
  - Task 1, CPA-55342 (Net-Price Contract):
    - proposed 2025-06-02, signed 2025-07-01, 24-month first term to 2027-06-30;
    - auto_renew False, commitment 250000.00;
    - 50 contract items (47 new_item lines; the three original lines re-dated to quote 2025-06-16 / effective 2025-07-01);
    - 218493.84 net shipped in the year before its first anniversary (2026-07-01), above the 80% shortfall threshold.
  - No new line is a removal or substitute line, and none touches a scored sku.
- **SRC-8 (cutoff).** SO-5520117 was booked 08:41, before the 16:00 Standard cutoff, so it now ships 2026-09-08. Its delivery is 09-10 and INV-5219733 is dated 09-08.
- **SRC-9 (ship-to reviews).** Order history now backs each recorded anniversary review, and each review keeps its level (12 or more route shipments, ship-tos open at least 60 months, so the lower of the 12-month figure and twice the 6-month figure is used):

| task | ship-to | recorded | basis | spend vs threshold |
| --- | --- | --- | --- | --- |
| 0 | ST-51842 | 2026-06-02 | 12 route lines | 51943.80 / 51467.36 ≥ 42000 |
| 0 | ST-51843 | 2026-03-16 (first handling after the Saturday anniversary) | — | 6225.85 / 5496.26 ≥ 3000 |
| 1 | ST-52611 | on its anniversary 2026-10-01 | 14 route lines | 56592.97 / 56655.82 ≥ 42000 |
| 1 | ST-52614 | on its anniversary 2026-04-06 | 12 route lines | 163486.04 / 163611.22 ≥ 105000 |

  - **ST-52611:** with its 2026-10-01 review on file, no review falls due on either call day.
  - **Last order dates** are booking dates: 2026-09-15 / 2026-09-08 (task 0) and 2026-09-18 / 2026-09-25 (task 1).
  - **Returned-payment history:** its invoices now carry real orders. Task 0 has SO-5497731 and SO-5508812; task 1 has SO-5590117 and SO-5617735. The amounts follow the order lines; the return dates are unchanged, so the exposure tiers are unchanged.
  - **Invoicing:** every shipment and scan order is invoiced per shipment (due +30), and paid by ACH debit 25 days later when that date is before the call. No invoice is past due.
- **SRC-2:** not routed (stop rule).

### Reads, regression and runtime risk
- **New read step:** a find_vmi_activity read (by program) after the bins read in both tasks, so that replay closure covers the activity rows.
  - Later steps shift by one: task 0 writes at steps 15 and 17; task 1 at steps 15, 17 and 19.
  - Every proof text that names a step was re-derived.
- **Scored values unchanged:**
  - task 0: 28 / 6.00;
  - task 1: 10.43 / 55 / 46.
- **Sensitivities and probes:** every sensitivity is unchanged, and the probe table output is identical to round 6.
- **Stale-text sweep:** clean (no Weekly tier, no 2023/2024 program dates, no old bin references, no old step numbers).
- **Rationale seed cards:** rewritten for the new rows.
- **No due obligation lit on either call day:**
  - no VMI anniversary;
  - no agreement anniversary in task 0 (2026-11-01);
  - the task 1 commitment test passed;
  - no ship-to inactivity, no backorders, no past-due invoices.
- **Personas:** unchanged, and consistent with the new seed (neither mentions StockSmart, pricing or orders).

### Gate block (round 7)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK (0.json closure 446 = init 446; 1.json closure 572 = init 572)
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK
- check_traceability (info): TRACEABILITY OK, 0 non-unlock misses
REWORK round 7: gates 7/7 green
