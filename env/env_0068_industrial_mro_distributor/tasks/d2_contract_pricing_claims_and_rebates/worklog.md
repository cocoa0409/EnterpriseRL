# worklog — d2_contract_pricing_claims_and_rebates (round 1, fresh relaunch)

## Step 0 — draw (scripts/draw_counts.py --tasks 2)
{"task": 0, "prerequisite_problems": 2, "problems": 3, "factor_counts": [5, 6, 4]}
{"task": 1, "prerequisite_problems": 3, "problems": 4, "factor_counts": [6, 5, 4, 5]}
Task 0 assignment: final_rebate_check 6, termination_forfeiture 5, return_clawback 4 (multiset {6,5,4} = draw).

## Step 0 — difficulty pre-check
- Base pricing charter closes; d2 claims signed/withdrawn/renewed/terminated, item added/repriced/removed,
  claim filed/decided, rebate paid/reversed. Accrual (pricing_rebate_accrued) is not a d2 write.
- Trigger ban (Principle D): pricing_claim_decided outcome=approved and pricing_rebate_paid
  payout_method=credit_memo trigger credit:credit_memo_issued -> no d2 tool writes either.
- Lifecycle writes carry dates only; the DSL has no date arithmetic -> no lifecycle problem is claimed.
- Base automatic clauses to watch in every seed: rebate accrual per quarter (day after period end),
  payout within rebate_payout_days_after_period, forfeiture on early termination, renewal window /
  auto-renew, removal notice, escalation notice/lock, claim decision within business days.
- Plan v1 (earlier cut-off agent) adopted for the draw and task 1's storyline; task 0 redesigned (see
  plan.md "v1 -> v2 revisions").

## Capability contract cards (Step 2)
- book_rebate_return_clawback_ccd0c1e2 — owner agent / write. Object: one RMA's clawback on the agreement's
  rebate ledger. Atomic action: create one pricing_rebates line event_type pricing_rebate_reversed
  (rebate_period, qualifying_spend = -returned value, rate, amount, payout_method none, event_date = call
  date, source_reference = RMA number) and lower pricing_agreements.rebate_balance by amount. Event
  pricing_rebate_reversed has no triggers. Receipt: status, rebate_line_id, rebate_period,
  source_reference, amount, rebate_balance.
- book_termination_rebate_forfeiture_47cc59ce — owner agent / write. Object: the forfeiture of an
  early-terminated agreement. Atomic action: create one pricing_rebate_reversed line (qualifying_spend 0,
  rate 0, source_reference = agreement number read from the agreement, payout_method none) and lower the
  rebate balance. No triggers. Receipt: status, rebate_line_id, rebate_period, source_reference, amount,
  rebate_balance.
- request_final_rebate_check_d4aa8dfe — owner user / write. Object: the customer's instruction to pay the
  unpaid rebate by check. Atomic action: create one pricing_rebate_paid line with payout_method check (the
  only payout method whose trigger stays inside pricing), payout reference minted in the tool
  (RBC-2NNNNN), event_date = call date; lower the rebate balance. Receipt: status, rebate_line_id,
  payout_reference, payout_method, amount, rebate_balance.
- check_task_tools: TASK TOOL CONTRACT OK (3 tools). Note: the rebate_period value is routed through a
  local label so the schema's example text ("e.g. 2026-Q2") is not copied into a docstring (coordinator
  rule: no concrete example values in docstrings); the format YYYY-Qn is fully described.

## Task 0 — final rebate settlement (Strategic, terminated 2026-09-30)
- Scope: pricing_ext_final_rebate_check (root, user) <- pricing_ext_termination_forfeiture <- pricing_ext_return_clawback.
- Policies written piece by piece into pricing.extended.yaml; tools in task_tools.py; seed built by scratch
  builder (/tmp/d2_contract_pricing_claims_and_rebates_0068/t0_seed.py, deterministic uuid4).
- Handling-time results (gate evaluator): clawback 24.61, forfeiture 9,939.90, final check 25,017.33.
- Prerequisite sensitivity: skip forfeiture -> check 34,062.64; skip clawback -> forfeiture 9,952.82.
- Factor sensitivity (baseline substituted, result): clawback 17.23 / 32.82 / 49.23 / 32.82, all-baseline 61.26;
  forfeiture 15,619.84 / 10,886.56 / 10,413.23 / 10,886.56 / 10,886.56, all-baseline 18,933.14;
  check 26,132.82 / 25,714.51 / 25,435.64 / 25,367.33 / 25,027.39 / 25,296.20, all-baseline 27,887.24.
- Revisions: symptom -> root cause -> change -> re-run
  - COMPUTE "history not load-bearing" (clawback, check) -> only LATEST/X-reads touched the holding -> clawback
    period cap (SUM accrued - reversed) and ledger-recomputed balance in the check -> COMPUTE OK.
  - EXTENDED "factor bindings read no record" (size share, alignment relief) -> both read a plain binding ->
    each factor now owns its own read (size_credit, align_gap) -> EXTENDED OK.
  - REPLAY closure missing ship_to row -> no gold read selected it -> added find_ship_to_accounts (step 5);
    all step indices shifted (+1) and propagated to computations / solvability / tracing.
  - Realism sweep: unit prices re-derived from Strategic category discounts; on-account return credit drawn
    by the next payment (FC-2260531 94.05); forfeiture net rebate subtracts payouts too. Builder re-run, all
    figures regenerated from t0_vals.json (no hand-typed stale numbers: grep for old values = 0 hits).
- Per-task gates (all 8): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK,
  GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.

### Task 0 manual values gates
- Length/breadth/hidden test: surface goal (check) -> sentence "not issued until ... forfeiture entry" ->
  forfeiture rule -> sentence "fixed only after ... clawback entry for every return ..." -> order returns ->
  RMA-208152. Breadth: 15 factors over 5 other-category record sets (order returns, order shipments, credit
  account, credit ledger, StockSmart/VendPoint holdings) plus 12-month, 3-month and date-span windows.
  owner=user: the check request is the customer's own payout instruction (base: "the payout method the
  customer chose"); completed on the spot.
- Need/simulator boundary: object (agreement CPA-20417), timing (today), authorisation (Corbett bookkeeping by
  the agent; the check request run by Dana), write not quote — all explicit; no extra asks; closes on the
  payout reference.
- Opening chronology: every volunteered fact (notice in February, ended September 30th, last check April) is a
  seed row; nothing gold produces is foreseen.
- Base eligibility/time anchor: no time gate on the three writes; the completed termination satisfies the
  180-day notice gate (225 days).
- Authority/business object: RMA receipt, accrual, termination status are system records; excluded RMAs listed
  in the dossier with their grounds.
- Reachability/no waits: all writes synchronous; no visit, delivery or approval awaited.
- Prerequisite sentences: E1 negated ("is not issued until"), E2 affirmative ("is fixed only after") — the
  charter is not one-direction; both state form; exactly one writer each; rule carries nothing else about
  either dependency.
- rule/compute two-way: sweep.py (basis quotes verbatim, baseline sentences in rule, overwrite replaced_by and
  policy_source in rule, no factor reads another factor's binding, no factor id inside a tool name) -> OK.
- Factors/labels/baseline honest: method factors change the formula shape (value basis: qty x price vs credit +
  fee vs credit; commitment relief: fixed share vs sliding share vs none; administration: flat vs per-month vs
  none) with pairwise distinguishing inputs recorded in the dossier; parameter factors select values.
- Draft recomputation from visible context agrees with gold (dossier section 13).

### XF recipe (13 points) — task 0 policies
1 factor independence: sweep shows no factor binding reads another factor's binding; shared reads (accrual,
  RMA selection, term_net, bal) are plain bindings stated once. 2 assembly: one generic combination sentence per
  policy ("Every share this policy sets multiplies ...", "The reliefs this policy sets are added together ...",
  "The holdbacks this policy sets are added together ..."), no factor quantity named. 3 order: shares multiply,
  reliefs/holdbacks are each worked on the same base and summed once (commutative); cap/floor and rounding moments
  stated. 4 no "as another policy figures it". 5 overwrites retire genuinely conflicting clauses, restate the
  in-force base content for every out-of-scope case and name their own scope; no sibling retires the same clause.
  6 basis quotes verbatim (sweep). 7 rounding sentences match RND placement (once, at result). 8 docstrings carry
  no example values (schema example text kept out via a local label); every claimed effect is in the body.
  9 edges: no same-day ties on LATEST/XLATEST reads; whole-month counts are MONTHS(); absent records / None /
  zero-division probed (plan.md probe table). 10 every stated filter is in compute and vice versa (status,
  event types, single receipt line, ship window, windows by date field). 11 method tiers distinct (above).
  12 the RMA and period are single record-visible candidates (latest receipt, latest accrual) with two-date DAYS
  tests inside the scope. 13 other-category rows priced by their charters (Premier Route return terms, Net 60
  Corporate finance charge 1 percent after 15 days, 25.00 returned payment fee, certified funds by wire, return
  credits within 2 business days, memo application rules).

## Task 1 — substitute claim on a discontinued contract item (Category Contract)
- Design note: v1's tree had the open-claim decision as a state gate on the protection. v2 turns it into a
  value edge on the close-out (the discontinued item's close-out price starts from the price the desk decides
  on the pending escalation claim), so all three edges carry value (>= 2 required). The decision is the
  only state-due d2 write left once the rebate policies sit in task 0; its numeric is the unit price the
  agreement sets for the claimed line, reviewed under Corbett's escalation-review schedule (overwrite of
  the base escalation sentence for that one escalation). Realism trade-off recorded: several factors are
  Corbett's own schedules (cap reductions, close-out and protection concessions, claim credits) keyed on
  real customer evidence; the strongest real-world rules used are the lower-of / shared-gap substitute
  start, returns net of the claim quantity, invoice tax and prompt-payment discount in the settlement.
- Capability cards (Step 2):
  - decide_pending_price_claim_4f6327a3 — agent/write. One pricing_claim_decided line for a named pending
    claim; copies invoice and sku from the filing; records quantity, billed and agreement prices, claim
    amount 0.00, outcome denied | referred_to_pricing_desk (approved is excluded: its trigger would write a
    credit memo in another category). Receipt: status, price_claim_id, claim_reference, outcome,
    contract_unit_price, claim_amount. The outcome value is routed through a local name so the schema's
    four-value enum is not offered (two values are legal here); both are described.
  - close_out_discontinued_item_dd8bcab8 — agent/write. One pricing_item_removed line (copies category,
    list, cost and current price from the item's latest line; notice date = call date; change reference
    PCH-2NNNNN minted). Receipt: status, contract_item_id, sku, effective_date, contract_unit_price,
    change_reference. No triggers.
  - protect_substitute_price_656c6d72 — agent/write. One pricing_item_added line, change_reason
    discontinued_substitute, category copied from the replaced item, list/cost 0.00 (not carried on a
    protection line), prior price = the substitute's regular billed price. Receipt as above.
  - file_contract_price_claim_992a36b2 — user/write. One pricing_claim_filed line, outcome pending, claim
    reference PCL-2NNNNN minted and returned. No triggers.
- Handling-time results: decision 61.4594 (referred), close-out 59.6156, protection 59.5405, claim 1,726.58.
- Prerequisite sensitivity: skip protection -> claim 0.00; skip close-out -> protection 0.0000; skip
  decision -> close-out 59.3640.
- Factor sensitivity: decision 62.6688 / 61.7654 / 61.6124 / 61.7654 / 61.6124 / 61.5206 (all 63.6480);
  close-out 61.7386 / 60.2302 / 60.5375 / 59.9229 (all 63.6480); protection 58.2742 / 60.1497 / 59.8451 /
  59.8451 / 59.6928 (all 59.6156); claim 2,014.34 / 1,629.99 / 1,687.49 / 1,714.85 / 1,710.94 (all 1,824.13).
- Revisions: SOLVABILITY one_claim_per_line evidence missing pricing_claims sku/event_type -> added rows;
  COMPUTE history floor (close-out, protection) -> COUNT-backed decision tier and close-out presence;
  docstring ordering words removed; contract items' prior prices re-derived from the category schedule.
- Per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK.

### Task 1 manual values gates
- Length/breadth: goal (file a claim) -> claim sentence -> protection rule -> protection sentence -> close-out
  rule -> close-out sentence -> pending claim PCL-210356; 20 factors over order (shipments, backorder,
  fill, returns), credit (invoices, tax, discounts, payments, memos) and StockSmart/VendPoint holdings.
  owner=user: filing a claim is the customer's act under the base rule; completed on the spot.
- Need/simulator boundary: object (INV-2260930 line, AB-21795), timing (today), authorisation (Corbett
  records by the agent, the filing by Renee), a write — explicit; no extra asks; closes on the claim reference.
- Opening chronology: every volunteered fact (invoice, item, 140 at 72.57, discontinued in August) is on the
  seed rows; the 20 returned boxes only when asked (RMA-213377 receipt).
- Time gate: inside_claim_window anchor 2026-09-30, last day 2026-12-29 inclusive, filing day 16.
- Prerequisite sentences: two affirmative ("is fixed only after"), one negated ("is not set until"); state
  form, exactly one writer each, rule carries nothing else about the dependency.
- rule/compute two-way: sweep.py OK; method tiers pairwise distinct with distinguishing inputs (dossier §7).
- Draft recomputation from the visible context agrees with gold.

### XF recipe (13 points) — task 1 policies
1 independence: sweep.py finds no factor binding reading another factor's binding; shared selections
  (claimed item, backorder/fill, latest price, ending price, invoice) are plain bindings. 2 assembly: one
  generic sentence per policy ("The reductions this policy sets are added together ...", "The concessions this
  policy sets are added together ...", "... plus the credits this policy sets ..."). 3 order: reductions and
  concessions are summed once against one base; the claim's credits are worked on the overbilling before the
  settlement multiplier (stated); floors and rounding moments stated. 4 no quantity defined "as another policy
  figures it": the close-out names the decision line's recorded price, the protection the close-out line's
  price, the claim the protection line's price — record reads. 5 overwrites: decision (escalation sentence),
  close-out (removal-notice sentence), protection (substitute-billing and quote sentences), claim (claim-amount
  sentence); each restates the in-force base content for every other case and names its own scope; no two
  policies retire the same clause. 6 basis quotes verbatim (sweep). 7 rounding: prices to 4 decimals once, the
  claim to the cent once, matching RND. 8 docstrings: no example values, no ordering words; every claimed
  effect is in the body. 9 edges: no same-day ties on LATEST/XLATEST reads; MONTHS() for whole months; absent
  records, zero division and None probed (plan.md). 10 filters stated and implemented (event types, sku,
  change_reason, windows by date field, single fill on the latest backorder). 11 method tiers distinct.
  12 single record-visible candidates: latest filed claim, latest backorder and its fill, latest regular
  shipment, latest invoice; two-date DAYS tests inside each scope. 13 other-category rows priced by their
  charters (Route Delivery returns 10 percent restocking, pickup free, 60-day window; backorder substitute
  billed at the lower of its own and the original price; Net 30 Preferred 1 percent discount on merchandise
  inside 10 days; return credits applied to the invoice that billed the item).

## Final (difficulty-wide) gate block — 2 tasks, 7 extended policies, 7 task tools
- check_extended: EXTENDED OK (all 7 policies covered, scopes disjoint, multi-source + cross-difficulty per task)
- check_task_tools: TASK TOOL CONTRACT OK (7 tools)
- replay_tasks: REPLAY OK (0.json 17 acts, 1.json 20 acts; deterministic, non-vacuous, closures match)
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK (suite means branches 85.5 / steps 18.5; history_rows_max 43; branches_max 96)
- check_grounding: GROUNDING OK
- check_cache_diff: CACHE-DIFF INFO (optional diagnostic, no trap used)
- check_cross_fire: SCOPE OK
- check_traceability: deferred until the KB is rendered (no docs yet).
- erlbench.validate_scenario (filtered to d2): only "required document ... not found" (KB not rendered yet);
  tool lint and replay clean.
- Write domain clean: plan.md, pricing.extended.yaml, task_tools.py, tasks/0.json, tasks/1.json, worklog.md;
  scratch builders stay in /tmp/d2_contract_pricing_claims_and_rebates_0068/; gate __pycache__ removed.
INSTANTIATE round 1: gates 8/8 green

## Rework round 2 (audit revision_1: audits/policy_task/d2_contract_pricing_claims_and_rebates/)
Read in full: _difficulty.md, 0.md, 1.md. Every RED and observation answered below; each class closed across
all seven policies, not only the cited member. Patches were applied with exact-match scripts (count-checked)
in /tmp/d2_contract_pricing_claims_and_rebates_0068/r2/; pre-rework copies kept there.

- CG-1 (XF5, T1-1) undeclared override of pricing_price_basis s1. Change: open_claim_decision adds
  pricing_price_basis to base_policy_refs and declares an overwrite of its first sentence ("The price of a
  billed line is ... not in the schedule."); replaced_by (verbatim in the rule) scopes the reviewed price to
  "the claimed line of an escalation this policy reviews on a pending claim, and only for such a line" and
  restates the base sentence for every other billed line. pricing_evt_price_claim s1/s5 measure against the
  price pricing_price_basis sets, so with s1 retired for that line no in-force clause gives 63.6480. Class
  sweep (every base sentence departed from): clawback (rebate s5), forfeiture (rebate s6), final check (rebate
  s4), decision (escalation s5 + price basis s1), close-out (contract items s6), protection (contract items s7,
  s2), claim (price claim s5) — each declared; no other departure found; no two policies retire one clause.
- CG-2 (T1-2) close-out rule stated what the protection carries. Change: removed "; that is the price a
  protection of the substitute carries" from the close-out rule. Class sweep (depended-on rules speaking for
  their dependants): the forfeiture's replaced_by said earlier periods are "kept and paid" (the payout's
  business) -> now "stays on the rebate ledger unforfeited"; no other depended-on rule (clawback, decision,
  close-out, protection) mentions its dependant's result.
- CG-3 (T1-3) gap reference ambiguous. Change: the gap concession now reads "the contract unit price on the
  discontinued item's latest price line" (the baseline's own words) in the rule, its two basis quotes and its
  ladder. Class sweep of "latest ... price" references: close-out reference tiers now "the latest decision
  recorded on a price claim for the item" / "the contract unit price on the item's latest price line";
  protection reads "the substitute's unit price on its latest regular shipment"; decision reads "the line that
  added the item (its new-item line)" — each names one record.
- CG-4 (XF7, T0-1) intermediate rounding vs "once, on the final figure" — all seven policies. Change: every
  baseline sentence now ends unrounded and the rounding is a single stated final step ("... is rounded half up
  to ... once, on the final figure"); every assembly sentence says the factor contributions act on the
  unrounded figure "before that ... rounding" (clawback also states its cap and 0.00 floor, closing O-6).
  Compute rounds only at `result` in all seven (checked). No gold value sits on a half-cent tie.
- CG-5 (XF9, T0-2) whole-month, day and tie conventions — all members. Change: every rule that counts months
  now states "Whole months between two dates are the difference in calendar months between them, less one when
  the later date's day of the month is earlier than the earlier date's" (exactly MONTHS()); every rule states
  the calendar-day convention ("count the later date and not the earlier one", exactly DAYS()) and the tie rule
  ("among records of the same date the one recorded first", exactly the DSL's strict-> first-row LATEST). The
  substitute claim carries the day and tie sentence (it counts no months). Tenure stays 29 under the stated
  convention (probe: effective 2024-03-30 -> 30, long tier). No world tie exists (probed: a same-date decoy keeps
  the first-recorded row).
- CG-6 (SOURCE-FACTOR, T1-4) settlement multiplier discounted tax. Change: tier 1 is now "one plus the tax rate
  less the discount rate, the discount having been earned on the merchandise only and never on the sales tax"
  (credit_evt_cash_discount s1); compute `settle_mult` = 1 + t - d; ladder method text updated. Claim
  1,726.58 -> 1,727.71; all claim sensitivity figures regenerated.
- CG-7 (XF2) assembly sentences named factor quantities. Change: claim assembly is now "The multiplier this
  policy sets multiplies the unrounded claim amount, and every credit this policy sets adds its percent of that
  same unrounded claim amount, before that rounding"; close-out and protection method tiers now redefine the
  baseline quantity itself ("the close-out price is instead ...", "the protected price is instead ...") and the
  assembly takes concessions "off the close-out price" / "off the protected price". The other five assembly
  sentences name only baseline quantities (re-read).
- CG-8 (XF1) ship_order/ship_line plain but used by one factor. Change: moved into returned_quantity_basis's
  bindings. Class sweep script r2/xf1.py: no other plain binding is used by exactly one factor.
- CG-9 (XF10) filter mismatches. Change: the claim scope now states the test the compute applies ("on the
  customer's most recent invoice ... when that invoice is dated on the shipment's ship date or within
  invoice_window_days days after it"); the decision states "the line that added the item (its new-item line)"
  for the change_reason filter. Class sweep of every compute filter against its rule: clean.
- O-4: the final check's prerequisite sentence now names "the rebate period in which the termination took
  effect" itself. O-5/quantifier class: the forfeiture now waits on "a clawback entry for the customer's most
  recently received return whenever that return is of termination-period merchandise ..." (the clawback books
  exactly that return); the decision is scoped to the latest backorder's item and its most recently filed claim,
  and the close-out waits on "the price claim most recently filed on that item" — every waited-on state is one
  the depended-on policy can write. O-6: clawback floor stated. O-7: the decision's denied branch now also covers
  "the overbilling is below the tier's price_claim_min_usd", matching base s6 and the tool docstring.
  O-1/O-2/O-3 kept (basis-selection methods are honest selections; prompt-claim credit and proposal-date tenure
  recorded as Corbett schedules).
- T0-O1 persona no longer pre-states acceptance of a forfeiture/holdback explanation. T0-O2 realism: the 2026-Q2
  rebate is now paid by check on 2026-07-28 (inside the 30-day window); the opening balance is the 2026-Q3 accrual
  only; persona: "the last rebate check ... the one for the second quarter, in July; the third quarter's rebate
  has not come yet". New task-0 figures: clawback 24.61, forfeiture 9,939.90, check 7,823.79 (all-baseline
  8,993.24; skip forfeiture 16,869.10; holdbacks 1,169.45 stay on the balance).
- T1-O1 persona: no protection expectation ("you believe that line was billed above what your agreement
  allows") and the returned boxes' reason matches the record (no longer needed). T1-O2 realism: PCL-210356 now
  filed 2026-10-13 (3 business days before the call, inside the 7-business-day decision period); PCL-209915's
  filing carries the billed 0.3950 against a claimed 0.3820 (52.00), consistent with its denial.
- Proof-text sweep: tasks' factor_trace, factor_sensitivity, tracing, objectives, prerequisite_closure
  (policy_source copies, why_false, flips, skipped_effect, order_uniqueness), solvability seed checks and both
  design_rationale dossiers regenerated from the evaluator values (t0_vals.json / t1_vals.json); grep for every
  superseded figure and sentence returns none outside the dated revision notes.
- XF recipe re-applied to all seven policies (sweep.py basis/baseline/overwrite/prerequisite quotes verbatim;
  xf1.py; rounding placement table; filter sweep; method-tier pairwise table in plan.md; probes in plan.md).
- Final gate block (round 2, both tasks): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK,
  COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; validate_scenario (d2) reports only the not-yet-rendered
  KB documents; traceability deferred until the KB is rendered; gate __pycache__ removed from the write domain.
REWORK round 2: gates 8/8 green

## Rework round 3 (renderer source scan: audits/render_source/d2_contract_pricing_claims_and_rebates/render_r1.md)
Read in full (F1-F6). Minimal edits: only the cited sentences and their class members changed wording; every
combination sentence keeps its wording and order. Patches: /tmp/d2_contract_pricing_claims_and_rebates_0068/r2/p_r3.py,
p_r3b.py (count-checked exact replacements; pre-round-3 charter copy kept as pricing.extended.r2.yaml there).
- F1 (final check, minimum vs rounding): the rule's order is floor, then rounding, then minimum; the compute now
  tests the minimum on the rounded figure: result = RND(check, 2) if RND(check, 2) >= rebate_min_payout_usd else 0
  (a distributor issues the check it would actually print). Class sweep of every minimum/floor/rounding order:
  clawback (limit, floor, rounding) = RND(MX(0, MN(cap, x))); forfeiture (floor, rounding) = RND(MX(0, x));
  decision (allowance floored at 0, price raised, rounded once); close-out and protection (concessions, rounding
  once); claim (overbilling per unit floored at 0, rounding once) — all already matched. Probe: 99.996 -> 100.00.
- F2 (claim, paid-invoice credit, unassigned case): rule now "an invoice not yet covered, or covered without any
  customer payment on it, takes no credit" (a carrying credit compensates money the customer paid; credits and
  discounts alone carry nothing); compute already returned 0. Class sweep of every ladder for an unassigned case:
  clawback frequency (zero lines -> F5); forfeiture notice relief had no tier for negative extra notice -> now
  "fewer than one extra day takes no notice relief"; protection starting price had no tier for a substitute with
  no regular shipment -> now "otherwise, or where the substitute has no regular shipment, it is the ending price";
  all other ladders (reason/size/value shares, commitment/tenure/program/alignment reliefs, every holdback,
  every decision reduction, close-out reference and concessions, adoption/program/prompt/tenure concessions,
  claim quantity, settlement, repeat and prompt-claim credits) already cover every input with an "otherwise",
  "fewer", "none", "less" or "no ... on record" tier. Compute unchanged for these (fall-through already).
- F3 (decision, adding line): scope now checked as stated — the compute adds new_item_lines = COUNT(new-item
  lines of the item) and requires exactly one, besides item_lines == 2; an item added by any other kind of line
  (e.g. a substitute's protection line) is out of scope instead of measuring from a zero cost. Class sweep of
  scope filters: protection (no price line for the substitute yet: COUNT == 0), claim (the protection line by its
  change reason), close-out (removal line count) — matched. Probe: substitute-added item -> 0.0000.
- F4 (decision, two groupings): the sentence now reads "when the overbilling, which is the claimed quantity times
  the difference between the billed unit price and that unit price, exceeds ...". Class sweep of every arithmetic
  sentence: protection's "the ending price plus gap_share times the difference" now "plus the product of
  gap_share and the difference between the two"; every other sentence is a pure product, a quotient or "A less
  B" with one reading (the claim's out-of-scope restatement keeps the base sentence verbatim, as an overwrite's
  restatement must). T1 tracing text updated to quote the new outcome sentence.
- F5 (clawback, zero receipt lines): "one such line or none carries first_return_share" (the compute's
  `<= 1`), ladder text likewise. Probe (window forced to 0): first_return_share.
- F6 (close-out, contract-line check): scope now "when the agreement carries an added price line for that item"
  and the compute requires bo_added >= 1; class member: the protection's replaced item gets the same check
  ("one for which the agreement carries an added price line", bo_item_added >= 1). Probe: item off the contract
  -> both out of scope.
- No scored value moved (24.61 / 9,939.90 / 7,823.79; 61.4594 / 59.6156 / 59.5405 / 1,727.71; every factor
  sensitivity unchanged, re-run in t0_vals.py / t1_vals.py); proof-text sweep for the replaced sentences: only
  the T1 decision tracing quoted one (fixed); grep of both task files for every replaced phrase returns none.
- XF recipe re-applied: sweep.py (basis/baseline/overwrite/prerequisite quotes verbatim, no factor id in a tool
  name, no factor reads another factor) clean; xf1.py (no plain binding used by one factor; new scope counts are
  plain bindings read by in_scope) clean; rounding/floor/minimum order table above; new branches probed
  (plan.md round-3 probe table).
- Gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK; validate_scenario (d2) reports only the not-yet-rendered KB documents.
REWORK round 3: gates 8/8 green

## Rework round 4 — seed only (KB-VERDICT revision_2: audits/policy_kb/d2_contract_pricing_claims_and_rebates/)
Read in full: _verdict.md, 0.md, 1.md. pricing.extended.yaml and task_tools.py untouched (hashes verified below).
Published rules read for the fixes: docs/credit (catch-up discount amount, contract-tier share, finance-charge share,
disputed/returned merchandise, cash-discount conditions, hold and limit schedule), docs/vmi (enrollment and go-live,
program fee schedule and rules, replenishment and billing), docs/vending (placement terms schedule, monthly usage billing).
- SRC-1 (task 1, credit, gold-moving): the eight discount lines on invoices dated inside the live Category Contract's
  current term (from 2026-02-01) are now the catch-up figure 1 % x 0.75 x 1 on merchandise less applied return
  credits: 26.31, 23.42, 47.20, 24.39, 40.77, 21.60, 357.55, 88.45; each payment is re-seeded so the invoice settles
  (INV-2260930: 14,049.54 - memo 1,306.26 - discount 88.45 = payment 12,654.83). The four earlier invoices keep the
  base 1 % (outside the current term). Gold follows: settlement multiplier 1.065748, paid-invoice credit still 0.75 %
  (covered), claim 1,727.71 -> 1,732.79; claim sensitivities 2,021.59 / 1,629.99 / 1,693.70 / 1,721.06 / 1,717.16,
  all-baseline 1,824.13. Prompt-payment concession unchanged (12 discount lines).
- SRC-2 (task 0, credit/order): kept the 1,000,000.00 limit and the exposure holdback (an equally realistic fix that
  leaves the scored values) by removing the two three-invoice overlaps the credit rules forbid: the September 2025
  invoice was short-paid by 21,480.00 (paid 2025-11-24 408,020.00, remainder 2026-01-08; 39 days past due, under the
  45-day hold trigger; finance charge FC-2251231 214.80), and the returned check is the one that paid that finance
  charge (RTN-2260302 2026-03-02, fee RPF-2260302 25.00, wire re-payment 03-06; certified funds by wire through
  2026-06-02, so the January invoice is paid by wire 03-27). Daily replay: peak receivable 890,834.80 <= 1,100,000.00,
  no hold, shipments continue. At the call: receivable 839,699.52, 2 finance charges, 1 returned payment — every
  task-0 figure unchanged (24.61 / 9,939.90 / 7,823.79).
- SRC-3: VMI-20533 is now a StockSmart Monthly Service program (enrolled 2023-05-02, live 2023-05-19, 13 business days
  <= 15; the Weekly tier's 300-bin gate was not one this plant meets); VMI-21177 live 2024-05-24 (14 business days <= 15).
- SRC-4: VP-217730 installed 2023-02-24 (8 business days <= 10); 12-month term and 30-day notice still met.
- O-3 (rows the owning rules produce where due): each StockSmart program now carries 76 bins set at go-live (the
  Monthly gate's 75 bins met, 200 included -> no bin fee) and one scheduled visit a month on the 4th Tuesday across
  the ledger window (task 0 2025-09..2026-09, task 1 2025-10..2026-09; the October 2026 visit falls after the call)
  with three replenishment lines at the price-basis price on the delivery date (task 0 Strategic category discounts,
  task 1 contract items not escalated) and one billing line a month of 2,055-2,117, above the 2,000.00 minimum spend,
  so no minimum fee is due and none is owed on the call day; billing sits inside the monthly consolidated invoice
  (no new invoice, totals unchanged). Fairhaven's VendPoint machine carries usage bills for 2025-09..2025-11 (1,318-1,486,
  above the 1,250.00 minimum), none after its 2025-11-14 removal. New gold reads (closure): find_vmi_bins,
  find_vmi_activity (both tasks) and find_vending_transactions (task 0), placed with the other program reads; write
  steps shifted (task 0: 13 / 15 / 19, task 1: 15 / 17 / 19 / 21) and every step reference regenerated.
- Proof text: computations, traces, sensitivities, tracing, prerequisite closures, solvability seed checks, read-node
  objectives and both design_rationale dossiers regenerated or patched from t0_vals.json / t1_vals.json; grep of both
  task files for every superseded figure and row reference (131.00, 12,612.28, 1.061775, 4,295, RTN-2260402, Weekly,
  2026-06-05, 2026-06-03) returns none outside dated revision notes. Persona unchanged (no line touches the changed rows).
- Probe table re-run (plan.md round-4 section).
- Final gate block (round 4): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK; extra: TRACEABILITY OK (docs now published; 0.json 28 copied / 0 missing, 1.json 34 / 0);
  validate_scenario (d2): no errors beyond rendering-free checks, no d2 warnings. Hashes: pricing.extended.yaml
  70d9fe4e6f18bfda…, task_tools.py 063dbb2aa6bc4517… — byte-identical to the brief.
REWORK round 4: gates 8/8 green
