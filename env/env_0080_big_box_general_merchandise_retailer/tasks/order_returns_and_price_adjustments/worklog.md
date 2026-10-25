# worklog — order_returns_and_price_adjustments (category order), M=2

## Step 0 — difficulty pre-check
- Read: references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/order.yaml (full),
  db_schema.json (order/membership/plan/card tables), share_tools.py (finders, verify threshold = 2 details),
  account-wide rules membership_delivery_benefit, card_cardholder_benefits, membership cash earn/reverse, plan
  coverage/claim/settlement, gift refunds; XF_recipe.md (all 30 points), owner_ruling.md.
- Draw (draw_counts.py --tasks 2):
  {"task": 0, "prerequisite_problems": 3, "problems": 4, "factor_counts": [4, 6, 4, 6]}
  {"task": 1, "prerequisite_problems": 1, "problems": 2, "factor_counts": [4, 6]}
- Base automatic clauses (order): ready->unclaimed cancel after pickup_hold_days; fulfilment transitions (system);
  mark returned when every unit returned/refunded; fee refund on a fault return / whole order not received.
- Trigger table (base `triggers` of every order event my tools may write):
  order_return_line -> card:card_post_credit {refund_method original_payment, payment_method_type northgate_card};
                       gift:gift_issue_card {refund_method merchandise_return_card_*}; plan:plan_cancel {plan_id non-empty}
  order_adjust_price / order_refund_charge -> card:card_post_credit {payment_method_type northgate_card}
  order_charge_fee -> membership:membership_benefit_use {fee_waiver_source membership}
  order_reschedule / order_cancel / order_mark_returned -> none
  DECISION: every task tool hard-codes payment_method_type=external_card, card_account_id="", plan_id="",
  refund_method=original_payment, receipt_type=receipt, fee_waiver_source=none, so no row it writes satisfies any
  `when` above; worlds are seeded so the refunded orders were paid with an external card.
- Owed-write class (recipe 21): membership cash earn/reverse is membership's own rule (not a declared trigger);
  task worlds avoid it (task 0 order not fulfilled -> no cash; task 1 membership canceled on the fulfilment
  date -> no cash earned, so a return reverses nothing). No plan covers any refunded unit.
- DSL limits noted: history primitives scoped to the order; filters are literal values; refund rows carry
  fee_type = the refunded fee's type so fee rows and their refunds can be netted per fee type.

## Design log
- Many tree shapes were rejected before claiming (recorded so the audit can see why):
  * price adjustment as a computed policy: the lower price lives in no record the DSL can read -> rejected.
  * cancellation-based trees: a full cancellation refund has no real factor levers; consequences (refunds of
    every line and fee) would be owed after a cancel root -> rejected.
  * fault return as root: a fault return makes the fee refund owed after it (obligation outside the tree).
  * two return tools (fault / changed mind): near-synonym tools + no value-linked hidden prerequisites.
  * membership-sourced fee corrections: would make a membership_benefit_use write owed in membership.
- Claimed design (plan.md v2): task 0 large-item late change tree; task 1 Same-Day changed-mind Drive Up return.

## Task 0 — large-item late change (written: 4 policies in order.extended.yaml, 4 tools in task_tools.py)
- Tools (uuid8 fresh via uuid4): reschedule_large_item_delivery_d930ab59 (user), credit_missed_appointment_73d9a081,
  credit_replacement_haul_away_849732e1, refund_late_change_fee_56da608d (agent). check_task_tools: TASK TOOL CONTRACT OK.
- World: Marisol Navarro (CO 80219); order 4108836215 Scheduled Large-Item Delivery placed 2026-10-08, fridge 1699.99 +
  range 799.99, delivery 49.00, haul-away 50.00 (2 old items), late-change fee 49.00 (2026-10-19, own 3rd change);
  reschedule_count 4 vs 3 confirmed own requests -> 1 Northgate move (missed 10-22, moved to 10-24). Old fridge plan
  (Standard 3-Year, 849.99) settled by eGift reimbursement 2026-10-06. frozen 2026-10-24 08:10 MDT (delivery day).
- Scratch run (/tmp/.../t0/run.py, check_compute build_env/eval_compute):
  D0 missed-appointment credit 41.85 (fs: moves 32.05, wait 36.95, haul 39.40, value 39.40, own req 39.40, flat 31.85; all-baseline 9.80)
  H0 replacement haul-away credit 23.75 (timing 13.75, kind of settlement 18.75, item kind 21.25, basis 47.50; all 12.50)
  L0 late-change goodwill refund 46.65 (moves 34.40, recency 34.40, crew 41.75, standby 41.65; all 12.25)
  U0 late-change fee 53.40 on the world after D0,H0,L0 (notice 95.25, earlier fee 43.40, crew 27.15, install 33.40,
     own req 48.40, courtesy 68.40; all-baseline 49.00). Edge sensitivity: skip D0 -> 95.25, skip H0 -> 77.15,
     skip L0 -> 63.40. D0/H0/L0 read only charges (not standings) and write different fee rows -> they commute.
- tasks/0.json written; per-task gates 7/7 green (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK,
  COMPUTE OK, GROUNDING OK, SCOPE OK) after fixes: symptom replaced_by not in rule -> appended each replaced_by
  sentence to its rule; factors whose bindings held no evidence primitive -> each factor owns its COUNT binding;
  "" foreign keys counted as dangling -> seed uses null and tools no longer write empty card/plan ids; DOB pinned
  verbatim (1984-06-17); discriminators carry action_arg fee_event_id.
- Recipe sweeps (sweep.py): every compute_basis quote verbatim in its rule, baseline sentences in rule, no factor id
  inside a tool name, no forbidden substrings in task_tools.py -> 0 issues. Added day-count convention sentence
  (start day out, end day in) to all four rules and a same-date tie rule for the plan settlement read.
- Probe table (task 0): XLATEST plan settlement {absent: lag -1/method None/category None -> all extras 0;
  decoy later repair settlement: rule reads "most recent", compute same; tie: first recorded}; LATEST late fee
  {absent: fee_age 9999 -> 0}; COUNT requests {absent: moves = reschedule_count}; SUM fee rows {no refund rows -> 0}.
- Defining-sentence table: each "standard ..." sentence belongs to its policy's baseline; each "The <credit
  name> extra for ..." sentence belongs to exactly one factor; assembly sentences name no factor quantity.

## Task 1 — Same-Day changed-mind Drive Up return (design)
- Draw: prerequisite_problems=1, factor_counts=[4,6]: B1 return refund (user root) 6; C1 late-express credit 4.
- World: Northgate+ Monthly member (cancel_pending on order date 2026-10-20, canceled 2026-10-21 = fulfilment
  date -> member fees on the order, no Northgate Cash earned, nothing to reverse). Same-Day express order: smart
  plugs x2 (electronics, 59.98 after a 10.00 promotion, price drop adjustment 6.00 on 10-23), yogurt (grocery,
  non_returnable), towels (kept), phone stand returned 10-24 (changed mind). Same-day fee 0.00 (member waiver),
  express fee 10.00 (member price). Delivered 10-21 (express promise missed). Return at Drive Up on 2026-11-02.
- Edge B1<-C1 value_input: the restocking relief reads the late-express credit standing on the order.
- tasks/1.json written. Fixes during gates: discriminator phrase made verbatim ("changed your mind"); eligibility
  evidence lists now carry the gate field paths; the return tool argument renamed original_event_id to match the
  blueprint's units_available action binding (docstring/body/gold/tracing propagated).
- Scratch (/tmp/.../t1/run.py): C1 8.50 (lateness 6.50, basket 7.50, price 8.00, grocery 7.50; all-baseline 4.00);
  B1 42.84 on the world after C1 (category 46.99, holding 44.04, history 44.04, relief 38.59, basis 48.84,
  small-order 49.83; all-baseline 59.98); skip C1 -> 40.59 (restocking 6.40 instead of 4.15).
- Probe table (task 1): CFIELD membership canceled_date {absent membership: CPARAM None -> deduction tier fails ->
  0; active membership (canceled None) -> member; canceled on/before order date -> 0}; LATEST adjustment {absent ->
  basis = net amount}; COUNT changed-mind returns {none -> 0}; SUM express refunds {none -> flat relief 2.00 when
  fulfilled late, else 0}.

## Closing (difficulty level)
- Coverage: 6 extended policies, task 0 = {late_change_fee, missed_appointment_credit, replacement_haul_away_credit,
  late_fee_goodwill_refund}, task 1 = {drive_up_return_refund, late_express_credit}; scopes and tools disjoint;
  every policy computed at its gold call. owner=user: reschedule (task 0), Drive Up return (task 1).
- Identifier band: Navarro / Ortega (M-P), CO 80219 and AZ 85016, phones 3035550124 / 6025550137, DOB 1984/1988,
  order numbers 4108836215 / 4024315587 / 4207719346, return numbers 418306257731 and tool-built 4xxxxxxxxxxx.
- Known realism risks left for the audit: credit percentages and flat amounts of the missed-appointment,
  goodwill, haul-away and late-express schedules are company schedules worded as Northgate's own; the express fee is
  read as charged in addition to the same-day fee (both rows seeded); the plan settlement's eGift card (gift) and
  the membership fee ledger are unread cross-product rows (recipe 29 residue).
- Final gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (suite branches 38.50, steps 12.50, history max 28, branch max 49), GROUNDING OK, SCOPE OK.
ROUND 1: gates 7/7 green

## Rework round 2 (audit: audits/policy_task/order_returns_and_price_adjustments/{_difficulty,0,1}.md)
- Every finding was verified against the artifacts first (the audit's probes reproduced in /tmp/.../probes.py); none disputed.
- Charter changes: F1 ladders made reachable (moves 3+/2/single, lateness 3+/2/single day, express price lever replaced by
  an alcohol age-check lever, haul basis tiers by item count and pre-benefit charge); F2 goodwill and replacement rules
  rewritten as record tests, edge B/C sentences and conditions aligned; F3/O2 caps on fee standing (charged less refunds),
  goodwill on the most recent late-change fee row; F4/F10 drive-up scope record tests (adjustments on the line; external
  card alone); F5/F6/F7 small-order deduction removed, Marketplace changed-mind return history added (cross-difficulty
  market, XCOUNT over twelve whole months, any seller answer); F8 drive-up restocking baseline = standard ten percent;
  F9 "charged above zero" carve-outs in every credit rule and edge; O1 external-card wording; O3 free reschedules priced;
  O6 waiting counted to the scheduled date; O7 own requests counted before the present one.
- Seeds: task 0 now records two Northgate moves (reschedule_count 5 vs 3 own requests), the 2026-10-19 late-change fee is
  79.00 (= charter compute on the 2026-10-19 world: 49.00 + 25.00 crew + 20.00 install - 15.00 courtesy, verified by
  re-run), plan ledger gains a 2025-06-20 repair settlement (186.40; reimbursement now 663.59 = net price less earlier
  settlement) as the near-miss. Task 1: fulfilled 2026-10-22 (two days late), sparkling wine line added, Marketplace Pro
  Seller order (speaker changed-mind return refunded, cable defective return refunded with original shipping, case kept).
- New figures: task 0 D0 41.85, H0 23.75, L0 72.15, U0 38.40 (skip D0 80.25 / H0 62.15 / L0 48.40; permutation-stable);
  task 1 C1 9.50, B1 52.13 with restocking 1.85 (skip C1 49.38).
- Probe table (probes.py): H0 absent settlement / same-day tie (first recorded) / settlement after order (out of scope) /
  promo-lowered single item / full single item; L0 second older fee (latest read) / earlier refund (net cap) / single move;
  D0 withdrawn request and other request type excluded, 2024 order fee not read (holding scope); U0 opening world 114.00,
  free reschedule 0.00; C1 on-time out of scope; B1 Marketplace request beyond twelve months excluded, inside counted,
  absent history, competitor match, no adjustment, on-time order (no relief). All match the rule words.
- Recipe re-check: compute_basis verbatim, baseline sentences in rule, factor ids not in tool names, forbidden substrings,
  half-cent distances (all raw values > 1e-6 from a half cent) -> sweep issues 0. Stale-text sweep of both task files for
  every round-1 figure and wording -> none left.
- rework_claims_r2.md written (no figures).
REWORK round 2: gates 7/7 green

## Rework round 3 (audit revision_2: F11, N1, N2, N3; task 1 PASS kept)
- Verified each item on scratch copies first (probes_r3.py); none disputed. Noted DSL fact used below: filter values in
  SUM/XCOUNT may be bindings (dynamic filters), e.g. item_category=settle_category.
- F11 + N2: order_ext_replacement_haul_away_credit rebuilt — scope record test (most recent settlement is a replacement
  or eGift reimbursement, of a category the order carries, 0-90 days before the order, haul-away above 0.00, external
  card); factors timing (0-30/31-60/61-90), kind of item replaced (major appliance / furniture or fitness / other large),
  settled value (>=1000 / 500-999.99 / less), credited haul (method: fee x lesser of matching settlements in six whole
  months and old items / one item's fee / the charge). Each factor owns an evidence read.
- N3: goodwill keyed on the latest late-change fee row with an amount above 0.00; reschedule tool now books no fee row
  for a 0.00 fee (TASK TOOL CONTRACT OK).
- N1 class: every retired base clause restated for Northgate-Card-paid orders (late-change, missed-appointment x2,
  replacement, goodwill, late-express); edge conditions A/B/C name external-card orders.
- New task 0 figures: D0 41.85, H0 22.50 (timing 12.50, kind 17.50, value 21.25, basis 45.00; all 12.50), L0 72.15,
  U0 39.65 (notice 81.50, earlier fee 29.65, crew 12.15, install 19.65, own req 34.65, courtesy 69.65; all 49.00);
  skip D0 81.50 / H0 62.15 / L0 49.65. Task 1 unchanged (C1 9.50, B1 52.13, probes identical).
- Probe table (H0): absent settlement / latest repair / other category / 99 days (out) -> 0.00; 90 days boundary (in,
  timing none); 60 days (31-60); same-day lag 0; later TV repair after the order (latest read, out); second appliance
  reimbursement (two settlements, two items -> 45.00); same-date tie with repair first (first recorded, out); one item
  full charge; one item promo-lowered (11.25); haul-away 0.00 (out). L0: older second fee (latest read), same-date tie.
- Sweeps: compute_basis verbatim, baseline in rule, factor ids not in tool names, forbidden substrings -> 0 issues;
  stale-figure sweep of tasks/0.json -> none.
- rework_claims_r3.md written (no figures).
REWORK round 3: gates 7/7 green

## Rework round 4 (audit revision_3: N4, N5, O9; both tasks PASS kept)
- Verified each item: N4 reproduced (six members priced or scoped by tender); base card-credit path checked: order_refund_charge
  and order_return_line with tender northgate_card trigger card:card_post_credit (merchant credit) — exists for refunds; no base
  order-to-card path for a fee charge, so the late-change rule routes a card-paid fee through the card charter's purchase posting.
- N4 fix: one generic posting sentence per rule (tender decides only where money posts, refund tender order Cash -> gift card ->
  primary payment method); every replaced_by restated tender-blind; drive-up scope no longer tests the tender; edge conditions
  drop the tender; all six tools refuse orders not paid by external card or with Cash/gift redemptions (docstrings say so).
- N5 fix: replacement credited-haul count anchored on the settlement read's date (dynamic event_date filter). O9 fix: goodwill
  recency counted from the fee row's date to the scheduled date.
- Re-run: task 0 D0 41.85, H0 22.50, L0 72.15, U0 39.65; task 1 C1 9.50, B1 52.13 — all unchanged. Drift probe: H0 and L0
  identical when worked out on 2026-10-24 and 2027-05-01; same-category settlement on another date not counted, on the same
  date counted (credited haul doubles with two old items); goodwill recency boundaries 7/8 and 30/31 days as the ladder states.
- Sweeps: compute_basis verbatim, baseline in rule, factor ids not in tool names, forbidden substrings -> 0; stale-text sweep of
  both task files for tender-scope and six-month wording -> fixed in necessity/rationale/tracing text.
- rework_claims_r4.md written (no figures).
REWORK round 4: gates 7/7 green

## Rework round 5 (audit revision_4: N6, O10; both tasks PASS kept)
- N6 verified: on task 0 records with a northgate_card tender, edge A was engaged but its resolver refuses -> no solution; same
  on task 1 with a Cash redemption. Route applied: one booking-scope record test per rule ("paid in full by an external card with
  no Northgate Cash or gift card redeemed on it"); outside it the same figure applies and its posting is made by a human
  representative (POLICY_NOT_COVERED handoff), nothing booked at the desk; card-charter fee route and base card-credit path
  sentences removed; the record test is verbatim in all four waiting prerequisite sentences and in their conditions, so a wait is
  engaged only where its resolver books. Tool docstrings aligned; bodies unchanged.
- O10 kept as an observation (no base contradiction); reasoning in rework_claims_r5.md.
- Re-run: task 0 D0 41.85, H0 22.50, L0 72.15, U0 39.65; task 1 C1 9.50, B1 52.13 — unchanged. Sweeps 0 issues; stale-text sweep
  of both task files (card-credit / card charter / posting wording) -> none.
- rework_claims_r5.md written (no figures).
REWORK round 5: gates 7/7 green

## Rework round 6 (renderer scan-first stop: audits/render_source/order_returns_and_price_adjustments/render_r1.md)
- Verified R-1..R-5 and the A2 observation on the source; all confirmed, none disputed.
- R-1 drive-up replaced_by restores the changed-mind reason condition; R-2 replacement credited_haul_basis owns haul_standard and
  haul_items; R-3 late-change own_requests made a plain binding with a defining sentence, the surcharge factor reads its own
  requests_on_order count; R-4 late-change baseline names the standard notice charge, combining sentence "each schedule's value
  standing in place of its standard value"; R-5 is_date is a real calendar check (2026-02-30 and 2027-02-29 refused, 2028-02-29
  accepted); R-obs combining sentences of late-express, drive-up and replacement made generic.
- Class sweeps: replaced_by vs superseded clause for all seven overwrites; single-reader plain bindings in all six policies;
  standard-method reads of factor-owned bindings; docstring claims vs bodies — no further members.
- Re-run: task 0 D0 41.85, H0 22.50, L0 72.15, U0 39.65; task 1 C1 9.50, B1 52.13 — unchanged. Sweep 0 issues; stale-text sweep
  of both task files -> none.
- rework_claims_r6.md written (no figures).
REWORK round 6: gates 7/7 green

## Rework round 7 (seed-only; KB cross-product re-judge t0_plan_settlement_rows, t0_plan_registration)
- Charter/tools byte-identical (sha256 6aec2c3b597adfc4..., 351e913f110a43c8...).
- Read docs/plan (settlement terms, settlement authority schedule, registration valuation, delivery charges in limit, repair charge,
  service call, item age, parts, inspection). Re-seeded task 0's plan history so the published rules produce it: old fridge line
  1899.99 less 100.00 = 1799.99 (Standard 3-Year band 199.00), registered limit 1948.99 (1899.99 + 49.00 delivery / 1 line);
  repairs 2025-04-25 374.00 (age 394 d), 2025-11-14 374.00 (598 d), 2026-05-18 404.00 (781 d) = 249 + 65 + age + 30 parts, each
  under 80% x 1799.99; fourth mechanical failure (incident 2026-09-29, settled 2026-10-06) reached the repair count of 3 ->
  replacement, reimbursed by eGift at 1799.99 - 1152.00 = 647.99 (no like item); remaining limit 149.00, plan fulfilled.
  Verified by a scratch re-pricing script against those rules.
- Gold unchanged: D0 41.85, H0 22.50 (value tier still 500-999.99), L0 72.15, U0 39.65; task 1 unchanged (9.50 / 1.85 / 52.13).
- Near-miss for the replacement credit is now the three earlier repair settlements.
- Stale-text sweep of tasks/0.json for every superseded plan figure -> none. TRACEABILITY OK (pre-check).
- rework_claims_r7.md written (no figures).
REWORK round 7: gates 7/7 green
