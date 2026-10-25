# vehicle_purchase_deals worklog (round 1, fresh relaunch)

- Draws (draw_counts.py --tasks 2): task0 prerequisite_problems=3 factor_counts=[5,6,5,5]; task1 prerequisite_problems=1 factor_counts=[6,4].
- Adopted predecessor plan.md tree; recipe-driven changes recorded in plan.md ("Round-1 relaunch" section).
- task_tools.py written (6 tools, uuid8 per tool); TASK TOOL CONTRACT OK after adding "identifier" wording to Id-class args.
- purchase.extended.yaml: 4 task-0 policies authored. check_extended red #1: factors keyed only on plain deal fields
  (cash_price, odometer, planned delivery, financing_type) -> "tier must rest on history/date/other category".
  Fix: price class read from the vehicle_price charge in the ledger; odometer demo factor and trade factors dropped;
  P_hdf method = late-delivery chargeable miles (date); P_inc method = model-year closeout (date + ledger price);
  P_ord re-cut to standing/late-history/extended-hold/check-funds params + account-exposure method. Gate now red only
  on missing tasks / task-1 tools (expected at this point).
- Gate-source read (check_solvability): every purchase_charge_posted write inherits purchase_evt_late_balance's
  one_late_fee_per_month dedup (binds billing_month). A home-delivery-fee *posting* tool cannot carry billing_month
  honestly, so the delivery-fee problem is re-cut as a correction: the store posted the fee on the standard schedule
  at delivery (157.50 = base formula); the fleet schedule gives a lower fee and the excess is reversed by one
  purchase_charge_reversed entry pointing at the posted fee (same pattern as the base doc-fee correction).
  Tool post_fleet_delivery_fee_06fda118 dropped; new tool reverse_fleet_delivery_fee_<fresh uuid8>.
  Incentive tool gains customer_id (purchase_evt_returned_payment certified_funds_period gate binds customer_id
  on every purchase_payment_posted write).
- Task 0 written (tasks/0.json) from scratch builders; verify.py (handling-time replay through the real tools +
  check_compute's environment) gives reversal 55.16 / incentive 3648.60 / late fee 166.22 / order deposit 5166.87;
  baselines 0.00 / 1150.00 / 348.82 / 3634.00; edge skips 166.55 and 187.95 vs 166.22. Cancellation guard: the
  order-deposit add-ons first summed to exactly the 0.10 standard rate (an agent skipping all four rate factors would
  have scored) -> held_short_addon 0.015 -> 0.02 (total 0.105).
- Per-task gates task 0: TASK TOOL CONTRACT OK, REPLAY OK (closure 97 = seed 97), SOLVABILITY OK, COMPUTE OK,
  GROUNDING OK, SCOPE OK; EXTENDED red only on the two task-1 tools (claimed next).
- XF10 sweep: 10 compute_basis quotes joined non-adjacent sentences -> each re-pointed to one sentence or an adjacent run;
  sweep now clean (every quote, replaced_by and baseline sentence verbatim in its own rule). No factor id is a substring of
  any tool name. Docstrings: no ordering words, no example values, no table/row wording. No datetime/random/uuid in tools.
- Domain guards added (rule sentence + MX(0, ...)): order deposit / extension deposit collect nothing when deposits held
  already cover the requirement; delivery-fee correction nets earlier reversals. Gold values unchanged.
- Task 1 written: extension deposit 1940.25 (user, debit card; baseline 1063.00) -> extension 7 days (2026-10-25 Sunday ->
  2026-11-01; baseline 3); edge skip gives 6. Per-task gates 7/7 green.
- plan.md "Round-1 relaunch" section rewritten to the final design (factor tables with T1/T2, all-pairs method tables,
  probe table, events/triggers); stale stub tables (demo-mileage, trade, delivery-fee posting) superseded there.
- Final difficulty run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK (suite means
  branches 49.0, steps 14.0; history_rows_max 9; branches_max 69) / GROUNDING OK / SCOPE OK. Traceability deferred to
  post-render. Authoring scripts deleted from /tmp/vehicle_purchase_deals_0075/ (ids.json, tools.txt, seeds kept).
REWORK round 1: gates 7/7 green

## Rework round 2 (audits/policy_task/vehicle_purchase_deals: C1-C10, T0-1, T0-3, T1-1, T1-2)
- Read 0.md, 1.md, _difficulty.md in full. Authoring scripts from round 1 were deleted; round-2 edits are made by small
  patch scripts in /tmp/vehicle_purchase_deals_0075/ (deleted at the end).
- FOUND at round-2 start: purchase.extended.yaml (04:01), task_tools.py (04:02) and plan.md (03:53) had been overwritten by
  another writer after the round-1 audit freeze (hashes 2a6939935f0c / 3148936cfdc4 vs audited 1a68702ec9bd /
  908f3efa4823): different policy ids (purchase_ext_home_delivery_charge ...) and tools (post_home_delivery_charge_9b350808
  ...), plan.md reverted to the predecessor stub; it wrote pol_*.yaml + build_ext.sh into my scratch dir; tasks/*.json were
  not touched, so the tree was inconsistent. Its files are preserved in /tmp/vehicle_purchase_deals_0075/foreign_writer_0353_0402/.
  Round 2 rebuilds the audited design (my tool names/uuids from tools.txt) with every audit item closed.
- Round-2 closure (charter rebuilt from fresh builders; hashes now purchase.extended.yaml 8ac4125fd70c, task_tools.py 28698d49db86):
  C1  extension_deposit overwrites base "Extensions carry no fee and leave the deposit unchanged." (replaced_by names the non-fleet
      scope and restates no-fee + unchanged deposit for fleet); purchase_evt_hold_extension added to its base_policy_refs.
  C2a late fee <- delivery fee now ACTION form ("...has been checked against the fleet home delivery fee and any excess reversed.")
      with fallback_reason (the check leaves an entry only when an excess exists). C2b extension <- deposit now a record test
      ("...until a deposit received on the handling date stands on the deal."); extension deposit floored at 250 so it always books.
  C3  order-deposit sentence adds "with a balance still due above 0.00" = condition.
  C4  late-fee scope excludes buyers whose service account is on credit hold (base fee and timing kept, computed exactly);
      days after the assessment day floored at 0.
  C5  start-day weekend tier = 7 - weekday (Sat 2, Sun 1): differs from the fall-through by an input.
  C6a free radius is no longer a factor (standing share instead); late-delivery tiers never zero the miles (cap / half-floor),
      so no factor makes another inert. C6b credit-hold exposure tier = rate x price + whole open balance (rate factors still act).
  C7  incentive assembly sentence generic ("any adjustment to the summed incentive comes next").
  C8  vehicle price read by one factor only (unit_price_class); C9c/C10a/C10b upfit and model-year closeout factors removed,
      replaced by quarterly_program (delivery quarter), order_bank_lead (contract -> delivery days) and registration_report_timing
      (method). C9a/b/d/e framing reworded (spend, deposits received, weekend start, payment_method check).
  T0-1 service open_balance 10724.70 = its repair-order ledger (was 11677.79). T0-3 find_purchase_transactions necessity now
      states the posted 157.50 fee. T1-1 rule "Each request ... one extension"; persona asks once and declines a second.
  T1-2 closed by C1. Observations: O1 tools round half up (Decimal), no gold on a half-cent; O2 kept (field gate, documented);
      O3-O8 unchanged/acknowledged.
  Class probes added (reversed earlier late fee, refunded card / collected deposits) -> rules + compute fixed; probe table,
  defining-sentence table and date anchors in plan.md. Tool bodies enforce half-up cents, amount > 0, YYYY-MM, whole days > 0,
  and the reversal's source row. New golds: t0 26.33 / 2750.00 / 171.74 / 5066.79; t1 1940.25 / 7.
  Proof text swept (rationales rewritten, tracing, necessity, closure, seed checks). Authoring scripts deleted.
REWORK round 2: gates 7/7 green

## Rework round 3 (audit revision_2: N1, N2, N3, T0-4; task 1 had PASSED — values kept)
- Read 0.md, 1.md and _difficulty.md revision_2 sections in full; artifacts at round start matched the r2 snapshot (8ac4125fd70c / 28698d49db86).
- N1 (class: every replaced_by restating retired in-force content): delivery-fee replaced_by now reads "...never less than
  home_delivery_min_fee_usd, and every home delivery fee, this one included, is posted once per deal under charge_code
  home_delivery_fee on the delivery date."; the separate fleet posting sentence was folded into it. Other replaced_by checked:
  incentive (threshold restated), late fee (rounding/min/billing_month/timing restated), extension pair (no fee, deposit unchanged,
  count +1, never from the request date) - complete.
- N2 (class: method tiers that shrink a concession): late_delivery_miles >15-days tier is now min(late_floor_share x beyond,
  late_long_cap_miles) <= the 1-15-day tier for every distance; scan of beyond 1..150 x lateness 0..40 found 0 increases.
  Other ladders checked for direction: standing/tenure shares, report-timing deduction (grows with lag, same floor), late-fee
  basis, deposit tiers - all monotone in their stated direction.
- N3 (class: state waits met by records other writes produce): both extension policies now cover only an extension asked for on a
  day after the reserved_date (a reservation-day request keeps the base extension, no deposit - restated in both replaced_by), and
  the extension-deposit rule says a deposit added after the reserved_date on such a deal is the extension deposit; plain binding
  requested_on_reserved_date (probe: same-day world -> 0 deposit, 3 days). Other state waits: order deposit <- late fee (only the
  late-fee rule books late_balance_fee rows), late fee <- incentive (only the incentive rule books manufacturer_incentive rows).
- Zero-amount edges (recipe 19): every waited-on write is floored above 0 (late fee min 50, incentive floor half, extension deposit
  min 250) or is the action-form check that books nothing when there is no excess; the root order deposit may be 0 (nothing waits).
- Rounding: every money RND now RND(x + 0.000001, 2) on non-negative amounts; exact-tie probe 55.255 -> 55.26. Tools unchanged
  (Decimal half-up helper).
- T0-4: seed check now "a 2500.00 deposit with payment_method check"; sweep found no other "personal" framing (task 1 hits are the
  vehicles' usage_class value). Proof text synced: task 0 rationale round-3 note and late-tier line, task 1 rationale N3/C1 quotes,
  prerequisite_closure edges re-copied from the charter, plan.md (late tier, N3, rounding contract, zero-amount edges, sentence
  table rows, refreshed probe table).
- Gold, baselines and every factor sensitivity unchanged on both tasks (r3_check MATCHES_TASK=True x6). Hashes: purchase.extended.yaml
  3d8a1e6677e4, task_tools.py 28698d49db86. Authoring scripts deleted.
REWORK round 3: gates 7/7 green

## Rework round 4 (audit revision_3: T1-3, R1; coordinator rulings on rounding and zero amounts; task 0 had PASSED)
- T1-3: deposit_received_record tier_taken "TBD" -> "at least resv_mid_ratio and less than resv_high_ratio of cash_price". Swept every
  tier_taken and factor_trace in both tasks (no other placeholder; every tier_taken matches the tier the world takes).
- R1: all 7 money roundings now RND(x + 0.000000001, 2) (delivery fee x2, incentive, late fee x2, order deposit, extension deposit).
  Tie check over all 52 rounding arguments behind every scored, baseline and factor-sensitivity figure: two task-1 sensitivity figures
  were exact half cents (1763.865, 2155.835) -> task 1 cash_price 41260.00 -> 41265.00 (tiers and the 7-day result unchanged; deposit
  1940.49, baseline 1063.25, sensitivities 2293.30 / 1587.67 / 1764.08 / 2156.10 / 2042.62 / 940.49); closest argument now 0.00125 from a
  half cent. Only remaining exact tie: the task-0 delivery-fee intermediate 163.965 under one factor's baseline, whose figure is 0.00 either
  way (compared with the 157.50 posted fee). Task 0 figures unchanged.
- Zero-amount ruling (class): extension deposit - credited deposits capped at max_credit_share 0.6 of the requirement after shares, so
  an amount is always owed and the 250.00 minimum never creates one (probe 694.49 where the held deposit covers the requirement);
  late fee - returns 0 with no minimum when balance_due <= 0 (new rule clause; probes 0 / 0). Other members unchanged: incentive floor
  (positive for any qualifying deal), delivery-fee action-form check (books nothing when no excess), order deposit root (nothing waits).
- Proof text swept: task 1 rationale/trace/tracing/solvability/closure figures, task 0 rationale epsilon text, plan.md (values,
  rounding contract, zero-amount section, round-4 probe table). Hashes: b0268ec31415 28698d49db86 bfc994931a83 9773908734be. Authoring scripts deleted.
REWORK round 4: gates 7/7 green

## Rework round 5 (audit revision_4: R4-1; both tasks had PASSED)
- R4-1 (both members): the credit cap is now part of the standard method. The baseline sentence reads "Every deposit received on the deal
  and still held (deposit_held_balance) is credited toward the extension deposit required, but the deposits credited never exceed
  max_credit_share of the extension deposit required, so part of every extension deposit is new money." (rule and baseline.rule;
  max_credit_share added to baseline.params); the separate cap sentence that read the shares' output was removed; compute
  credit_applied = MN(credited_deposits, max_credit_share x extension_required), i.e. before any share. Auditor world (guest, 2000.00 cash,
  >4 days): every factor at baseline -> 825.30 = the baseline paragraph. Zero-amount ruling still holds: every share product >= 0.765 > 0.6.
  Realism (R4-O1): kept as the store's own schedule — an extension deposit is at least partly new money.
- No figure of either task changed (cap 1361.75 never binds in task 1); rounding ruling and all other closures untouched. Proof text
  swept (task 1 rationale, plan.md cap lines and probes; held-5000 probe now 374.48). Hashes: 875a1ffe9065 28698d49db86 e78c228357f5 ea400d243509. Authoring scripts deleted.
REWORK round 5: gates 7/7 green

## Rework round 6 (render_source/vehicle_purchase_deals/render_r1.md: F1 + low note; both tasks had PASSED)
- F1 (class: assembly sentences naming factor quantities): the incentive assembly sentence is now generic with the same order -
  "Every amount added to the per-unit amount is added first, giving the summed incentive; any adjustment to the summed incentive comes
  next, and rounding to the cent comes last." - in the rule, compute_basis.summed_incentive and compute_basis.result. Swept the other
  five assembly sentences: already generic (no factor quantity named).
- Low note on order_account (class: plain binding shared by two factors whose compute_basis was one factor's ladder sentence; recipe
  A2/A4 member): added the plain sentence "The buyer's active service account is the buyer's service account in active status,
  identified by its tier (variant_name)." to the order-deposit rule (after its assembly sentence) and made it order_account's
  compute_basis. Mechanical sweep of all six policies: no other plain binding is shared by two factors or quotes a ladder sentence.
- Compute unchanged: no gold, baseline or sensitivity moves; rulings (RND 1e-9, zero amounts, action-form fallback) untouched.
  plan.md sentence table updated. Hashes: c9d5d4252466 28698d49db86 233d1414491e 3ae5d6f76369. Authoring scripts deleted.
REWORK round 6: gates 7/7 green

## Rework round 7 (policy_kb audit: S1, seed only; charter c9d5d4252466 and tools 28698d49db86 byte-identical)
- S1 (class: service early-payment discount credits and the payments that settle them; exhaustive over both worlds - task 0 has the
  only two, task 1 is a retail Gold account with no early-payment terms): re-priced by the published service docs as of each payment
  date - discount = (tier rate 2% [unit is a 2022 F-250, not bought on a closed group Fleet Vehicle Purchase Agreement] + tenure addition
  0.5% [Net 30, 83 / 86 whole months]) x discountable total (customer-pay labor + parts, ACH, no Kessler Care plan, no comeback/overage/
  goodwill credits) x standing share 0.5 [2025-08-05 late fee within 12 whole months, no returned payment]; no prompt-payer addition
  (fewer than 8 payments in 12 months); ACH window 15 days (paid after 7). RO 160342: 465.40 -> 5.82 (was 9.31), payment 477.96 (was
  474.47); RO 160497: 1330.05 -> 16.63 (was 26.60), payment 1343.64 (was 1333.67). Credit rows now on labor line A (the published
  booking line). Ledger: charges 13546.84 - credits 22.45 - payments 2799.69 = 10724.70 = open_balance (unchanged).
- No scored value moved (service_early_payer still counts 2 credits; no factor reads their amounts). Proof text: task 0 rationale.
REWORK round 7: gates 7/7 green

## Rework round 8 (policy_kb revision_3: S2, seed only, bounded; charter c9d5d4252466 and tools 28698d49db86 byte-identical)
- S2 (class: Owner Rewards points-earned rows and the points balance they make up; exhaustive over both worlds - task 0's Net 30
  account earns 0 points and has no points rows): re-priced by the published service docs on each crediting date (the payment date that
  left the RO paid in full): earning rate 2 x whole dollars of customer-pay labor+parts, x 1.25 tenure multiplier (Gold, opened 2018-05-14,
  60+ whole months), fraction dropped, + 250 frequent-visit bonus where at least 3 payments fall in the 12 whole months up to the crediting
  date; no Kessler Care / Kessler Shield / group-bought-vehicle addition (the Camry is on no closed group deal); cap 10000 not reached.
  RO 512248 376 -> 470; RO 517903 1034 -> 1292; RO 521577 272 -> 590 (4 payments in window); RO 525014 756 -> 1195 (5 payments);
  rewards_points_balance 2438 -> 3547 (no redemptions or expiries; first expiry 2027-03).
- No scored value moved (no task read uses points); replay closure still equals the seed. Proof text: task 1 rationale.
REWORK round 8: gates 7/7 green