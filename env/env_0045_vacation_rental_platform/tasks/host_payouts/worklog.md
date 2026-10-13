# host_payouts — instantiation worklog (erl-task-instantiate, M=2)

## Step 0 — difficulty pre-check
- category `payout` (holding `payout_methods`, events `payout_transactions`); base policies: payout_agg_multi_holding,
  payout_agg_routing, payout_agg_negative_balance, payout_evt_release, payout_evt_transfer, payout_evt_tax_withholding,
  payout_evt_returns_and_reactivation, payout_evt_holds, payout_evt_deductions_and_credits, payout_evt_method_management.
- DSL scope constraint found: every history primitive is scoped to ONE payout method (HID); cross reads resolve by the
  host's customer_id, so `stays` / `stay_transactions` (customer_id = the guest) are unreadable from a payout computation.
  Readable cross evidence: host_accounts + host_account_events (host), listings + listing_events (listing),
  protection_plans + protection_events (protect).
- Blueprint host acts: adding/removing/re-verifying a method and choosing a default — none carries a computed amount.
  The only host-owned write that carries a computed amount on this ledger is a payout the host confirms in person
  (security confirmation of an off-cycle transfer). Both trees therefore root at a host-confirmed transfer
  (owner=user), and the agent-side prerequisites are the rail fees that must stand on the ledger first.
- Fee timing: a rail fee falls due when the transfer's outcome posts (settlement day, or the return) — so a transfer
  confirmed today owes nothing more inside the call (no obligation outside the tree).
- Draws (`draw_counts.py --tasks 2`):
  - task 0: prerequisite_problems=1, factor_counts=[6, 5]
  - task 1: prerequisite_problems=2, factor_counts=[5, 4, 5]
- Space budget: 5 extended policies / 5 tools; task 0 claims {conversion fee, on-request payout}; task 1 claims
  {return charge, returned-transfer fee, re-send}. Pairwise disjoint; union = all.

## Tools (uuid8 minted once each)
- book_conversion_fee_3c5b00cd (agent) — payout_fee_charged / cross_currency_fee
- send_on_request_payout_d225f921 (user) — payout_sent
- book_return_charge_692b7e7b (agent) — payout_fee_charged / returned_payout_fee
- book_transfer_fee_e67ff494 (agent) — payout_fee_charged / transfer_fee
- confirm_payout_resend_90576149 (user) — payout_sent

## Task 0 design thesis (filled per step in tasks/0.json design_rationale)
Canadian Superhost (Orlando condo) on a PayPal CAD default method. Yesterday's scheduled transfer settles today
(conversion fee due, not booked). A HostCover reimbursement and today's release sit on the method. Host asks for the
money now -> on-request payout (user) whose amount waits on the conversion fee (value_input on the balance).

## Task 1 design thesis
Mexican Professional Host on an International Wire (MXN). A weekly wire was returned (account_closed); host re-verified
new details; support reactivated; the 10-day new-details hold has just ended. Return charge and the returned wire's own
transfer fee are owed and unbooked -> both must stand before the re-send (two value_input edges, fan-out).

## Task 0 — closed
- Policies: payout_ext_conversion_fee (6 factors: volume x corridor rate [multi-source], small-transfer handling,
  Superhost discount [host], Rewards discount [rewards], long-held method discount, account-age settlement [method, host]);
  payout_ext_on_request_payout (5 factors: fresh-earnings share [multi-source rating x stays, host], responsiveness bonus
  [host], claim advance share [protect], claim history [protect], float rule [method]).
- World: Claire Beaudoin (CA, Superhost), PayPal CAD, 93-row ledger (weekly sweeps, fee on settlement day), 23 stays
  (guest profiles withheld -> stays.customer_id null so no guest rows enter the host-side closure).
- Gold: fee 2.77 (baseline 13.21) on the 2026-09-14 transfer; payout 1361.27 (baseline 557.93); skipping the fee -> 1364.04.
- Gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Manual: factor ladders all off fall-through; no two factors in the task share a condition (Superhost status only in the
  fee; HostCover level only in the payout; account age only in the fee; transfer count only in the float).

## Task 1 — closed
- Policies: payout_ext_return_charge (5: reason base, correspondent charge [multi-source], prompt re-verification credit,
  segment courtesy [host], account-age settlement [method, host]); payout_ext_transfer_fee (5: fixed-part share
  [multi-source count x business name, host], large-transfer surcharge, earnings-volume discount, HostCover discount
  [protect], outcome settlement [method]); payout_ext_returned_resend (4: return-history reserve, reliability holdback
  [host], listing-quality holdback [listing], float rule [method]).
- World: Mariana Ochoa Valdés (MX, Professional Host), International Wire MXN, 235-row ledger with biweekly sweeps (so a
  wire settles before the next is sent), April name_mismatch return (charges booked when its balance went out again on
  2026-05-04), 2026-08-24 wire returned 2026-09-01 (account_closed), re-verified 2026-09-11, new-details period ends
  2026-09-21, frozen 2026-09-22 (first allowed day).
- Gold: return charge 8.82 (baseline 25.00), transfer fee 5.33 (baseline 15.00), re-send 16747.88 (baseline 22257.38);
  skip charge -> 16754.49, skip fee -> 16751.87; swapped fee order identical.
- Revisions: (1) return-charge history not load-bearing (LATEST only) -> returned amount = SUM of returns on the latest
  return date; (2) replaced_by quote trimmed to a verbatim substring; (3) transfer-fee identification clause removed and
  wire runs made biweekly so "the transfer it names" is the latest transfer at booking; (4) conversion-fee rule scoped to
  rails whose cross_currency_fee_pct is above 0.00 (wire owes none); (5) surcharge 7.40/3.20 to avoid half-cent ties in
  historical fees.

## Final difficulty-level gates (no --task)
- check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability
  SOLVABILITY OK; check_compute COMPUTE OK (branches mean 38.00, steps mean 16.50, history_rows_max 340,
  branches_max 40); check_grounding GROUNDING OK; check_cache_diff CACHE-DIFF INFO; check_cross_fire SCOPE OK.
- check_traceability: TRACEABILITY NOT OK — expected, the published KB (docs/) is not rendered yet, so the hidden tool
  names have no reachable source; re-run after erl-kb-doc-render.

## Round 2 — rework after audit r1 (audits/policy_task/host_payouts/)
- CG-1: on-request edge `condition` now carries the conversion rule's exclusions (zero-pct rail, USD, returned before
  settling); copied to task 0's prerequisite_closure.
- CG-2: tenure-keyed rounding ladders removed. Conversion fee: method factor = volume window convention by method age
  (12/6/3 months); account age became an additive discount (15/8/0); one half-up rounding; fee_rounding overwrite
  withdrawn; long-held-method discount dropped (its condition now drives the window). Return charge: method factor =
  correspondent handling by size of the return (0.10 % lifting charge / flat 6.00 / none); account-age factor dropped;
  one half-up rounding; fee_rounding overwrite withdrawn; now 4 factors.
- CG-3: transfer-fee outcome ladder = half (rejected on arrival) / full + 12.00 trace charge (traced and recalled) / as
  it stands (settled); one half-up rounding; fee_rounding overwrite withdrawn.
- Re-send gained resend_conversion_buffer (MXN/CAD 1.40 %, GBP/EUR 1.00 %, USD 0 of the returned amount) so task 1's
  counts stay the draw {4,5,5}.
- Finding 3 / O-T0-2: every declared figure recomputed unrounded and checked for half-cent ties; onreq response mid
  bonus 4 pts, xfee HostCover top 11 %, buffer 1.40 % chosen so none is a tie.
- O-1 (anchors stated), O-2 (0.00 return charge not booked; edge condition), O-6 (floats no longer round), O-7 (phrase),
  O-T0-1, O-T0-3, O-T1-1, O-T1-3 addressed in charter / persona / rationale. O-3, O-4, O-5 (partly), O-8, O-9, O-T1-2:
  no change (see per-item list in the final report).
- Both ledgers re-simulated in place (row ids unchanged): fees by the revised schedules as of each booking day, sweeps
  and returns re-set. New gold: task 0 fee 5.07, payout 1345.11; task 1 return charge 12.13, transfer fee 5.25,
  re-send 16651.22.
- Final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK; TRACEABILITY NOT OK (only the 5 hidden tool names — KB not rendered yet).

## Round 3 — rework after audit r2 (revision_2 sections)
- CG-4 (conv_volume_window was a lookback length labelled method): factor removed; conversion volume window fixed at
  12 whole months (conv_volume_window_months). New method factor conv_charge_structure — how the conversion charge is
  formed by transfer size, as FX providers price small conversions: flat 4.00 below 250.00 / greater of the capped
  percentage charge and a 9.00 minimum from 250.00 to 999.99 / percentage charge alone from 1000.00 (three different
  formulas). Small-transfer handling charge dropped (same size condition); long-held method discount (method age)
  restored as a parameter; conversion fee = 5 parameter + 1 method factors.
- O-7: "the amount set out below" -> "the amount this rule gives" (on-request and re-send rules, re-send overwrite).
- O-R2-1, O-R2-2, O-3, O-4, O-5 remainder, O-8, O-9, O-T1-2: no change (observations below the RED bar).
- Task 0 ledger re-simulated (22 conversion fees + sweeps), gold: fee 4.05 (baseline 13.19), payout 1347.51 (baseline
  556.65), skip-fee 1351.56; no half-cent ties. Task 1 (PASS in r2) untouched: 12.13 / 5.25 / 16651.22.
- Gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK; TRACEABILITY NOT OK (only the 5 hidden tool names; KB not rendered).
