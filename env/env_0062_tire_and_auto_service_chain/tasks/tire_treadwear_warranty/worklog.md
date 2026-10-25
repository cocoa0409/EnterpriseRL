# worklog — tire_treadwear_warranty (category tires), M=2

## Step 0 draw (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3, factor_counts=[4,5,6,5]
- task 1: prerequisite_problems=1, factor_counts=[5,4]

## Feasibility analysis (recorded before design)
- DSL facts that shape the design: compute reads only the target set's own fields/events, the
  intake rows keyed by tire_set_id, and other categories' holdings/ledgers. Vehicle fields
  (usage_class, tpms_type) and OTHER tire sets are not readable. A value_input edge therefore
  needs the depended-on write to land on the SAME tire set as the dependent computation.
- Claimed computing writes per set state: active set -> treadwear adjustment (ADJ), workmanship
  replacement (WRK), adjustment credit applied (CRA), satisfaction-trial return (SAT, on a set in
  trial); ordered set -> order cancellation (CAN). Booking / installation completion / inspection /
  closures carry no policy-computed number (or are not synchronous).
- Counting: task 0 needs 2 value edges (3 same-set nodes) + 1 more node; task 1 needs 1 value edge
  (2 same-set nodes) and each tree needs an owner=user write. Only the satisfaction return is a
  base-sanctioned customer write; applying one's own credit is a payment-like customer act.
- Result: the claim supports the trees only with (a) two credit-application writes (toward a
  replacement ticket / toward a pending workmanship share), (b) SAT made value-dependent on an
  in-trial workmanship replacement of the same set, (c) the order cancellation as the one
  state-gate leaf. Declared as overwrites where base sentences are departed from.

## Structure (round 2, on disk)
- task 0 (set A 38b2800d, All-Season 50K on the Highlander, business owner with fleet roster):
  root CRT tires_ext_ticket_redemption (user, scored balance_due) <- ADJ (value_input, credit_issued)
  ; CRT <- CRS (value_input, credit_remaining) ; CRS <- ADJ (value_input) ;
  CRT <- CAN (state_gate tire_sets.status; set C eb3df77d, LT order for the F-250, 5 days past hold)
  factor counts taken from draw [4,5,6,5]: CRS 4, CRT 5, ADJ 6, CAN 5.
- task 1 (set D dd495945, Highway Terrain LT on the Ram, inside its 45-day trial):
  root SAT tires_ext_trial_refund (user, scored amount) <- WRK (value_input, wrk_shares).
  factor counts [5,4]: WRK 5, SAT 4.
- tools (uuid8 one per tool): issue_treadwear_adjustment_f769c805 (agent, ADJ),
  apply_credit_to_workmanship_share_57ed5afc (user, CRS), apply_credit_to_replacement_ticket_eafdabc1
  (user, CRT), cancel_lapsed_tire_order_8987209f (agent, CAN), record_workmanship_replacement_cc1528ea
  (agent, WRK), confirm_trial_return_33503dcd (user, SAT).

## Gold figures (round 2)
- task 0: CAN 429.44 -> ADJ 66.74 (RR, 47%, price paid 142.00, selling price recorded 159.99)
  -> CRS 10.10 (LF share 28.50 apportioned) -> CRT credit 56.64, balance_due 112.35.
- task 1: WRK 3.31 (RF belt_shift, store 1452 Fairlawn, dated 2026-10-12) -> SAT 872.70 to the bank card on T-16034418 + share refund 3.31 on T-16188204 to the Crestline card (round 4).
- all-baseline: CAN 404.60, ADJ 97.28, CRS 0.00, CRT 128.10, WRK 86.00, SAT 862.00 (all differ from gold).
- edge deletion (round 3, replayed without the prerequisite and every write depending on it): skip ADJ
  -> CRS 0.00 and CRT 22.38 (round-2 figure 32.48 was wrong: it kept a 10.10 settlement of a credit never
  issued); skip CRS -> CRT 102.25; skip CAN -> CRT 112.35, set C stays ordered, no refund row (terminal
  state differs); skip WRK -> SAT 756.70.

## Pairwise method-tier tables (tiers.py: each tier forced in the task world)
| policy | method binding | tier A | tier B | tier C | gold tier |
|---|---|---|---|---|---|
| ADJ treadwear_credit | age_deduction | linear 66.74 | flat 62.48 | none 68.16 | linear |
| CRS share_settlement | settlement_order | share_first 28.50 | apportion 10.10 | ticket_first 0.00 | apportion |
| CRT ticket_redemption | tire_line | unit_price 122.35 | lower_of 112.35 | recorded 130.34 | lower_of |
| CAN lapsed_order_refund | storage_basis | one_week 429.44 | three_weeks 413.44 | weekly 437.44 | one_week |
| WRK workmanship_share | prorated_share | mileage 3.31 | time 1.52 | tread 22.80 | mileage |
| ADJ price_paid_basis (parameter) | price_paid | fleet-charged, 34.00 invoice discount 62.74 | other tender with savings 66.74 | unit price 71.44 | other tender with savings |
| SAT trial_refund | usage_charge | per_mile 872.70 | flat 895.90 | none 919.90 | per_mile |
Each method changes the formula shape (deduction form, settlement order, price basis, storage
count, proration basis, usage charge form); all tiers pairwise distinct in their world.
- symptom -> cause -> change -> rerun: CAN 'capped' (at most three whole weeks) coincided with
  'weekly' at 5 days (both 0 weeks, 437.44) -> a cap is only reached past 28 days, so the tier is
  stated as a flat three weeks (identical over its own range, >28 days = 4+ weeks) -> 413.44, distinct.

## Factor independence (harness deps(): no factor's bindings read another factor's binding)
- ADJ: age_deduction reads miles_run/term_used (plain); price_paid reads its own ticket_refunds.
- CRS: settlement_order reads adj_odo/order_share_odo (plain); result assembles plain bindings.
- CRT: tire_line reads line_tire_price (plain own copy), not recorded_price used by road_hazard_line.
- CAN: storage_basis code only; storage_charge (plain) assembles weekly_rate x storage_basis.
- WRK: days_after_install from def_date (plain); SAT: days_kept plain, restock reads own restock_days.

## Probe table (round 2, probe.py on scratch copies of the step world)
| policy | probe | gold | probe result |
|---|---|---|---|
| ADJ | decoy: later RR inspection (1/32) copied onto ordered set B | 66.74 | 66.74 |
| ADJ | absent: Highlander roster enrollment removed | 66.74 | 97.98 |
| CRS | absent: LF workmanship share row removed | 10.10 | 0.00 |
| CRS | decoy: same share copied onto set C | 10.10 | 10.10 |
| CRT | absent: road hazard certificate removed | 112.35 | 98.75 |
| CRT | decoy: certificate status expired | 112.35 | 98.75 |
| CRT | absent: alignment plan removed | 112.35 | 113.42 |
| CAN | decoy: booking copied onto set B | 429.44 | 429.44 |
| CAN | absent: set C booking removed | 429.44 | 468.00 |
| CAN | absent: F-250 roster enrollment removed | 429.44 | 422.30 |
| WRK | decoy: defect inspection copied onto returned Civic set | 3.31 | 3.31 |
| WRK | absent: alignment plan removed | 3.31 | 3.73 |
| WRK | absent: hazard certificate removed | 3.31 | 32.31 |
| SAT | decoy: Civic 2023 refund removed (other set) | 872.70 | 872.70 |
| SAT | decoy: alignment plan bought 2026-10-20 (outside window) | 872.70 | 887.70 |
| SAT | absent: alignment plan removed | 872.70 | 887.70 |
| SAT | absent: card account and card purchase removed (round 4) | 872.70 | 872.70 |
| SAT | set D fleet-charged, tires invoice discount 43.10 (round 4) | 872.70 | 831.75 |
Decoys on other sets never move a holding-scoped figure; absent cross-category records fall to the
stated lower tier.

## Round-2 closure (audits/policy_task/tire_treadwear_warranty/{0,1,_difficulty}.md)
- F-UNDECL-MILES: ADJ overwrites the base sentence "miles_driven is the inspection odometer minus
  install_odometer." by name, scoped "For a treadwear adjustment credit this policy computes, and only
  for such a credit" (latest inspection = the inspection the adjustment rests on).
- F-RC 1-2: WRK rule now states the defect selection priority and every timing tier is measured at the
  replacement visit (def_date = source inspection date), not today; compute matches the sentences.
- F-LABEL: every method factor changes the formula shape (table above); the old number-substitution
  "methods" (settleable_portion, price_paid_basis-as-method, worn_measure_basis, redemption_base_rule)
  are gone or relabelled parameter (price_paid_basis is a parameter).
- F-REAL-1: invented redemption/settlement percentages, per-ticket caps and card/hazard "points" are
  removed; CRT computes the real replacement-ticket balance (tire line, mounting line with labor rates,
  road hazard line, disposal), CRS apportions the credit between the share and the ticket in real
  currency; no card account or card factor remains in either world.
- F-LADDER-WEEKLY: CAN baseline states standard weekly storage; weekly_storage_rate tiers truck 4.00 /
  long-hold 3.00 / standard 2.00 each charged; storage basis tiers pairwise distinct (413.44/429.44/437.44).
- F-BUNDLE: ADJ price_paid_basis has no bundle tier (instant savings / more tires / unit price); SAT
  recapture anchors on install_date with the plan bought within the bundle window after it, as the
  alignment charter's tire bundle reads.
- F-CHAIN-WRK (coordinator decision B): the RF replacement was physically made by the Fairlawn store on
  2026-10-12 and the customer paid his share at the counter; only the warranty posting is missing; the
  posting is a real back-office precondition because the trial refund returns the paid share. Tool
  takes store_id and dates the entry at the source inspection.
- O-ORDERED-TICKET: card purchase rows removed; set B paid cash_or_debit with nothing rung yet; CAN's
  ordered-ticket overwrite narrowed to the set it cancels and yields to the replacement-ticket rule
  (no sibling-overwrite collision with CRT's tires_purchase_ticket overwrite).
- O-REPLACED-BY: ADJ covered-mileage replaced_by names every point; WRK customer-pays replaced_by names
  the proration basis, defect-class rate, discounts and mounting waiver.
- O-SHARE-SENTENCE: CRS prerequisite sentence reads "for every position ... without a recorded defect".
- O-TIER-EQ: old S/T factors removed; storage tiers fixed; SAT refunded_installation_part fall-through
  equals tier 1 only on lines that already refund installation (not this world: 116.00 vs 0.00).
- O-AFTERWARDS: "Afterwards" replaced by "Once booked" in task tool docstrings (grep: 0).
- O-RECAPTURE-ZERO: ladder "used for exactly its purchase-visit alignment" matches compute (== 1).
- O-T0-1 / O-T0-2: share-settlement edge restated; persona LF line no longer says when the share is settled.

## Residuals (recorded, not closable within the frozen blueprint)
- valve-stem/TPMS line excluded from the replacement balance and the lapsed-order refund: vehicle
  tpms_type is not readable by compute; declared in the overwrites ("rung when the tire is mounted").
- company-schedule constants (care/rotation/even-wear points, labor rates, apportioning, storage rates)
  are invented but plausible store schedules declared in params and rule sentences.
- CAN state gate rationale (an open lapsed order blocks fixing a replacement balance) is a business
  housekeeping rule, weaker than the value edges.
- (closed round 3) Task 1 counter payment now on record: Crestline card purchase 2026-10-12, T-16188204, 3.53.
- check_traceability reports only unlock tool-name misses (task tool names), expected before KB render.

## Round-3 closure (audits r2: F-PRICE-TIER, R2-1, F-MOUNT-HALF, O-T1-EVIDENCE)
- F-PRICE-TIER: ADJ price_paid_basis tiers: (1) ticket charged to a fleet account -> unit_price less the
  instant-savings share less the fleet discount on the tires invoice posted for the vehicle on
  purchase_date (fleet_evt_invoice discount_amount) / tire_count; (2) other tender, >= min tires with
  savings -> unit_price - savings / tire_count; (3) unit_price. "no refund entry" removed. Forced in task 0:
  62.74 / 66.74 / 71.44. Same fleet clause added to CAN and SAT tire price paid and CRT tire line, so
  "price paid" is one quantity across the charter (no seeded set is fleet-charged; no gold moves).
- R2-1: all deletion figures replayed (skips.py): 22.38 / 0.00 / 102.25 / 112.35 / 756.70; swept from
  tasks/0.json prerequisite_closure.edge_load_bearing (both adjustment edges), design_rationale, worklog.
- F-MOUNT-HALF: CRS certificate-without-mounting tier now "half of the line's mounting part" (line_mount/2),
  matching WRK's mount_part; both worlds take the includes-mounting tier, no value moves.
- O-T1-EVIDENCE: task 1 seeds the Crestline card account (ending 1846, balance 3.53) and its card purchase
  2026-10-12 at Fairlawn, ticket T-16188204, 3.53 (share 3.31 + 0.22 POS tax; tires charter: a ticket
  paid with the Crestline card posts to the card account, tax never in a charter computation); persona
  pays with the Crestline credit card; gold reads find_card_accounts / find_card_transactions (steps 11-12);
  posting/confirmation now steps 14/16; WRK stage evidence and closure why_false cite the card row.
- Probes (probe3.py): ADJ fleet invoice present but bank-card ticket -> 66.74 (decoy); fleet-charged ticket
  with invoice on another date -> 66.74 (absent invoice); CRT set A fleet-charged with 34.00 discount ->
  103.85; CAN set C fleet-charged with 23.80 discount -> 407.07. Factor independence re-run: clean.
- Task 1 re-verified after shared edits: 3.31 / 876.01 at round 3 (superseded in round 4: 872.70).

## Round-4 closure (audits r3: F-TENDER, O-FLEET-DISC)
- F-TENDER: the trial refund no longer carries the card-paid share to the bank card. SAT rule: the refund on
  the set's ticket = tire price paid + installation part - usage - recapture - restock, to the set ticket's
  tender; every share paid for a store-replaced tire is refunded in the amount recorded on its workmanship
  entry, on the counter ticket it was paid on, to the tender that paid it, never added to the set's refund;
  sales tax is returned by the POS tax line. confirm_trial_return_33503dcd takes share_ticket_number /
  share_payment_method / share_amount and books a second tires_refund entry (crestline_card on T-16188204 =
  the entry the card merchandise credit is posted from, tires charter trigger). The tool may not write card
  tables (check_extended: primary-category writes only), so the card posting stays the charter trigger.
  Base tires_refund_tender holds for both tickets. Gold: 872.70 + share 3.31 (T-16188204, crestline_card).
  Gate wrk_shares -> install_part. Sensitivities 756.70 / 919.90 / 887.70 / 915.80; all-baseline 862.00.
  Skip posting replayed: 756.70 (and no entry to refund the share from). Card evidence kept (reads, rows).
- O-FLEET-DISC: one sentence in ADJ, CRT, CAN, SAT rules: the tires-invoice discount is one percentage on
  every discountable line; the whole discount_amount is counted against the tire price, mounting and kit
  parts included, since those lines are never figured below the line's own charges here and an ordered
  set's ticket carries the tire price alone. No seeded set is fleet-charged.
- Task 0 re-verified: 429.44 / 66.74 / 10.10 / 112.35, all 20 sensitivities and 4 all-baselines unchanged;
  skips 22.38 / 0.00 / 102.25 / 112.35. Factor independence clean on all six policies.

## Gate block (difficulty-wide, final run)
EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK (0.json 19 acts clos 33=33; 1.json 17 acts clos 19=19)
SOLVABILITY OK (0.json 4 calls 11 gates 20 seed rows; 1.json 2/7/8) | COMPUTE OK (branches mean 74.00,
steps 18.00, history_rows_max 22, branches_max 106) | GROUNDING OK | CACHE-DIFF INFO (no trap selected)
SCOPE OK | TRACEABILITY NOT OK: 0.json 29 copied / 4 missing, 1.json 26 / 2 - all six misses are
unlock_*_discoverable_tool:tool_name (the six task tool names), expected before the KB is rendered.
REWORK round 4: gates 7/7 green

## Round-5 closure (audits/render_source/tires/notes.md)
- Section 1 (assembly sentences naming several factor quantities): every factor now contributes on its own
  against a baseline quantity; assembly stated once generically, no ordering sentence between factors.
  ADJ: commercial use as points taken off 100 (cut 50 here), care/rotation/even points added; covered 70 as
  before. CRT: balancing / fleet / member reliefs each a percentage of mounting_balancing_charge_per_tire
  (40 / 15 / 10), mounting 21.00 - 8.40 - 3.15 - 2.10 = 7.35. CAN: restocking fee = rate x price paid; fleet
  restocking relief = 20% of the line's full fee (14.28); storage at the standard rate x weeks per basis;
  truck storage surcharge per started week (4.00). WRK: defect class (structural 40 / bead 25), maintained
  and alignment discounts each a percentage of the prorated share taken off (3.31 unchanged). SAT: parts
  returned / charges taken stated once generically (872.70 unchanged).
- Section 2: share settlement order is now a plain rule clause read from odometers; its method factor is
  the apportioning tire line (unit price / lower of recorded and paid / recorded); the share's mounting part
  and two mounting reliefs are parameters; settleable/base are plain assemblies. Factor-independence (deps)
  clean on all six policies.
- Section 3: every replaced_by restates the retired base clause in full for cases outside the policy, then
  names the policy's scope (miles_driven; commercial-use reading incl. usage_class, with ADJ scoped to
  personal-use vehicles; effective miles under commercial use incl. "though workmanship replacement still
  applies"; without commercial use; credit_pct; credit amount; credit redemption - CRS and CRT each exclude
  both cases by name; purchase-ticket total - CRT and CAN each exclude both cases; order cancellation;
  workmanship customer-pays; trial confirmation; trial amount).
- Section 4: ADJ enrollment under one whole month takes nothing off; SAT miles run 0 with no inspection;
  WRK defect selection returns no share (0.00) when no defect entry exists (compute guarded).
- Section 5: confirm_trial_return docstring: books only tire refund entries; the card merchandise credit is
  posted by the refund event's card trigger, not by the call.
- Figures moved (task 0): seeded LF share re-figured under the restated workmanship rule 28.50 -> 26.60;
  CAN 436.58; ADJ 66.74 (unchanged); CRS 9.63; CRT credit 57.11, balance 109.59; all-baselines 404.60 /
  97.28 / 2.00 / 127.63; deletion replays: skip ADJ -> CRS 0.00, CRT 20.09; skip CRS -> 99.96; skip CAN ->
  109.59 (state gate). Task 1 unchanged: 3.31 / 872.70 / share refund 3.31; skip posting 756.70.
- Method tiers: age 66.74/62.48/68.16; apportioning tire line 9.13/9.63/8.77; tire line 119.59/109.59/127.58;
  storage 436.58/428.58/440.58; proration 3.31/1.52/22.80; usage 872.70/895.90/919.90.
- Probes: CRS enrollment removed 9.47, plan removed 9.52, certificate removed 2.29; CRT enrollment removed
  112.74, plan removed 111.69, rotations removed 117.99; CAN booking removed 468.00, F-250 enrollment removed
  422.30, 30 days past hold 412.58; ADJ enrolled under a month 97.98; WRK defect cleared 0.00, bead leak 4.55;
  SAT no inspections 919.90; set A fleet-charged (34.00 discount) ADJ 62.74 / CRT 101.09 / CRS 10.10.
- Gate block: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK (33=33, 19=19) | SOLVABILITY OK | COMPUTE OK
  (branches mean 83.50, steps 18.00) | GROUNDING OK | SCOPE OK | CACHE-DIFF INFO | TRACEABILITY NOT OK only on
  the six unlock tool names (pre-render).
REWORK round 5: gates 7/7 green

## Round-6 closure (audit r5: F-ASSEMBLY-L)
- F-ASSEMBLY-L: the lapsed-order policy's tires_purchase_ticket replaced_by (and its rule copy) now names the
  replacement-ticket case only: "a one-tire replacement ticket written against a treadwear adjustment credit
  carries the balance figured under that ticket's own rule." (no tire line / reliefs / road hazard line).
- Charter sweep (every rule sentence naming two or more computed quantities): the share settlement's
  credit-redemption replaced_by named the ticket policy's tire line in its exclusion tail; now "is settled
  under that ticket's own rule". Remaining multi-quantity sentences are baseline definitions or the single
  generic assembly sentence of each policy (no factor quantity of another policy, no ordering between factors).
- No scored value moved (436.58 / 66.74 / 9.63 / 57.11 / 109.59; 3.31 / 872.70 / 3.31); text-only change.
- Gate block: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK (33=33, 19=19) | SOLVABILITY OK | COMPUTE OK
  (branches mean 83.50, steps 18.00) | GROUNDING OK | SCOPE OK | CACHE-DIFF INFO | TRACEABILITY NOT OK only on
  the six unlock tool names (pre-render).
REWORK round 6: gates 7/7 green

## Round-7 closure (audits/policy_kb + runtime_context; runtime PASS both tasks, bijection PASS)
- KB-E1: share-settlement rule "follows the set's age and the line's price basis, as the replacement ticket
  figures its tire line:" -> "follows the set's age and the line's price basis:" (rule + compute_basis).
- KB-E2: "follows the road hazard certificate on the set, as the workmanship replacement was charged:" ->
  "follows the road hazard certificate on the set:" (rule + compute_basis haz_mount).
- Sweep for "as <another policy/factor> figures it": no other member (only "as the line sets it" = the line's
  own parameter, and "as stated above" self-references).
- S2 (workmanship baseline "Miles run" unused by the baseline formula): removed from the baseline rule and the
  general rule; stated inside the proration tier and the maintained-set tier, each factor owning its binding
  (miles_run/def_odo in proration_basis_method; maint_odo/maint_miles in maintained_set_discount).
- KB-E3 source side: the trial refund's general "days kept / miles run" sentence removed; days kept stated in
  the installation-part tier (own binding days_kept) and the usage tier (own usage_days), miles run in the
  usage tier, the truck restock tier counts days after install_date itself.
- Same class swept with a script (plain bindings the baseline formula never reads): ticket balance
  recorded_price -> road_hazard_line, line_fleet_discount -> tire_line_basis; lapsed-order bookings ->
  missed_slot_charge, dead days_past_hold dropped. No other member.
- No scored value moved: 436.58 / 66.74 / 9.63 / 57.11 / 109.59; 3.31 / 872.70 / 3.31; all sensitivities and
  all-baselines equal (assert in the regen script); factor independence clean. Probes: WRK +3 rotations
  3.31; SAT installed 2026-09-25 -> 936.76.
- Gate block: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK (33=33, 19=19) | SOLVABILITY OK | COMPUTE OK
  (branches mean 84.00, steps 18.00) | GROUNDING OK | SCOPE OK | CACHE-DIFF INFO | TRACEABILITY OK (0.json 29/0,
  1.json 26/0).
REWORK round 7: gates 7/7 green
