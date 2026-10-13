# guest_cancellations_and_refunds — instantiation worklog (M=2)

## Step 0 — difficulty pre-check
- Category: stay (Stays). Claimed events: stay_guest_cancelled, stay_payment_lapse_cancelled, stay_altered,
  stay_payment_collected, stay_refund_issued.
- Draws (draw_counts.py --tasks 2):
  - task 0: prerequisite_problems=3, factor_counts=[4,5,5,6]
  - task 1: prerequisite_problems=2, factor_counts=[6,4,4]
- Hard environment facts that shape every tree:
  1. stay_refund_issued declares a trigger into payout/host when {funded_by: host, refund_stage: after_payout_release};
     no task tool may write such a row. Earnings are released 24h after the start of the check-in date
     (payout_evt_release), so host-funded refunds are writable only before check-in or on the check-in date itself.
  2. The guest's own acts that carry a number are collections (stay_payment_collected); cancelling and submitting a
     request carry no computed value, so every tree's owner=user problem is a collection paid by the guest.
  3. Compute primitives are scoped to one stay (SUM/COUNT...) or to the guest's own holdings in other categories,
     so listing rates, other stays and host records are not computable inputs; the guest-wide service-fee refund
     cap (other stays) cannot enter compute and is kept out of the scored worlds (no other capped refunds).
  4. Every stay_refund_issued write is governed by 9 subject-scoped gates (windows, request approvals, dedup);
     refund tools therefore carry stay_id, charge_component, refund_reason and request_id.
- Families chosen (disjoint):
  - task 0: Long-Term stay cancelled by the guest on its check-in date; pet-fee, extra-guest-fee and
    service-fee refunds + the guest paying the unpaid notice night (4 problems).
  - task 1: Long-Term stay on its check-in date with an approved travel issue while installment 1 is still unpaid
    after declined collections; nightly and service-fee travel refunds + the guest paying installment 1 (3 problems).

## Task 0 — design thesis (claimed first; nothing occupied before it)
- World: Long-Term stay in TX-AUSTIN (75 nights, monthly installments, split fee, 1 pet, 1 extra guest, monthly
  discount), installment 1 collected at booking partly with Rewards credits; the guest cancelled in the app on the
  check-in date (13:40) and calls the same afternoon, before the host's earnings for the stay are released.
- Surface goal: "I left the monthly rental on the day I arrived; the app says I still owe for the notice — I want
  to pay what I owe now." Root = the notice charge (owner=user collection).
- Hidden prerequisites (policy prerequisite sentences): the notice charge is not collected until the stay's ledger
  carries the guest-cancellation refunds owed on the pet fee, the extra-guest fee and the guest service fee
  (state_gate x3); the service-fee refund is fixed only after the ledger carries the pet-fee and extra-guest-fee
  refunds (value_input x2: the refunded service-fee base is read from those entries).
- Tree: R=charge -> {pet refund, extra-guest refund, service-fee refund}; service-fee refund -> {pet, extra}.
  prerequisite problems = 3 (draw), value_input edges = 2 (>= max(3-1,1)).
- Factor allocation (draw [4,5,5,6]): charge 6, pet 5, extra-guest 5, service fee 4.
- Space left for task 1: travel-issue family (nightly travel refund, travel service-fee refund, first-installment
  payment by the guest) — disjoint policies and tools.
- Tools (fresh uuid8 each): pay_notice_charge_caff8891 (user), refund_pet_fee_41a7068c (agent),
  refund_extra_guest_fee_b492f389 (agent), refund_service_fee_f4bed6e4 (agent).

## Task 0 — closed
- Values (handling-time): pet-fee refund 78.58, extra-guest-fee refund 331.78, service-fee refund 55.33 (6.48 with no
  add-on refund on the ledger), notice charge 115.33 (installment 2). All-baseline results 0.00 for every computation.
- Revisions: (1) refund tools could not use module-level helpers (every top-level function counts as a tool) ->
  inlined; (2) every stay_refund_issued write is governed by the travel-issue and major-disruptive-event approval
  gates -> the departure service-fee rule now scopes those approval sentences to request-based refunds (declared
  overwrites, gates retired); (3) dedup gates need ledger rows carrying the refunded component -> the guest's 2025
  cancellation at the same bungalow (pet and extra-guest refunds) and the 2026 one (service-fee refund) are seeded;
  (4) replay closure: history moved onto the same listing/host, the listing is read by host account and the host's
  payout ledger by host + stay, empty FKs seeded as null; (5) installment count switched from request_id='' to
  "collections minus alteration increases" after (4).
- Per-task gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK. check_traceability deferred (no published KB yet).

## Task 1 — design thesis
- Occupied by task 0: the four departure policies and their tools. Task 1 claims the travel-issue family only.
- Draw (draw_counts.py --task 1): prerequisite_problems=2, factor_counts=[6,4,4].
- World: Long-Term stay in CO-DENVER (60 nights, exempt from occupancy tax, split fee, monthly installments,
  request-to-book accepted the evening before check-in); installment 1 was declined at confirmation and on the
  morning retry (inside the 48-hour grace); on the check-in date the guest reported a misrepresented listing about
  three hours after discovering it, and Roamhaven approved it the same evening (host earnings not yet released).
- Surface goal: "my host says she'll handle her side; I want Roamhaven's own service fee back for a place that isn't
  as described". Root = travel-issue service-fee refund.
- Hidden chain: the service-fee refund is fixed only after the ledger carries the nightly refund of that travel
  issue (value_input); the nightly refund is not fixed until the ledger carries the collection of every installment
  whose first night has arrived (value_input) -> the guest pays installment 1 herself (owner=user).
- Factor allocation: nightly travel refund 6, travel service-fee refund 4, installment 1 payment 4.
- Tools: refund_travel_nightly_d238de09 (agent), refund_travel_service_fee_041715de (agent),
  pay_first_installment_26275b3d (user).

## Task 1 — closed
- Values: installment 1 paid by the guest 3648.80 (declined automatic attempts show the pre-upgrade 3857.60),
  nightly travel refund 2132.41 (0.00 before installment 1), travel service-fee refund 289.62 (35.09 before the
  nightly refund).
- Revisions: hour-based arrival window not expressible -> date-based first-night treatment + Rewards tier uplift;
  installment 1 needed a second parameter factor -> Rewards fee courtesy (tax kept as a factor, credit offset moved
  into the baseline); tuple syntax replaced; stale declined amount made legitimate by today's Rewards upgrade.

## Difficulty closure
- 7 extended policies, all claimed; task scopes/tools pairwise disjoint; every policy recomputed at its gold call.
- Task 0 later revision: accepted guest-count change (installment-0 increase) seeded and read on the target stay for
  suite history depth (history_rows_max 10); values unchanged.
- Final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (branches mean 66.50, steps mean 16.00, history max 10, branches max 72), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
- check_traceability: TRACEABILITY NOT OK only for the 7 hidden tool names (4 in task 0, 3 in task 1), which reach
  the agent through the published KB; docs/ is not rendered yet, so this gate is deferred to after erl-kb-doc-render.

## Round 2 — rework against audits/policy_task/guest_cancellations_and_refunds/ (rev 1)
Plan per item:
- F-1: declare overwrites of stay_evt_payment_schedule "the cleaning, pet and extra-guest fees are collected with
  installment 1, and each installment carries ..." in the departure charge and the first-installment policy (plus the
  pay-in-full sentence in the latter); scope the installment-1 Rewards courtesy to monthly stays (multi-source tier)
  and reseed task 0's installment 1 at the courtesy amount so records agree with the charter.
- F-2: the notice charge becomes a departure charge for any guest who leaves a stay in progress owing kept nights
  (incl. a stay whose first payment was declined) so every tier is occupied by customers reaching the write;
  factors: notice nights (tier params), owed share of later nights (after_check_in_refund_pct), fee rate,
  occupancy-tax exemption, Rewards tier relief, loyalty relief; coverage and fees become general plumbing.
- F-3: drop the payment-plan fee-base ladder; the refunded fee base is every refunded service-fee component; the
  fourth factor becomes a loyalty uplift (credit earnings); scope widened to every guest cancellation (closes F-7).
- F-4: next-day first-night treatment becomes max(share, 75) — never below the other nights.
- Proof fields: task 0 "only ledger entry" and "958 hours" corrected.
- Observations fixed where cheap: F-5 (credit tier-2 denominator no longer reads posted refunds), O-1 (unspent
  nights capped at the stay's nights), O-2/O-3 (pay-part-now handling), O-4 (tool docstrings).

### Round 2 closure (per audit item)
- F-1 (SOURCE-POLICY RED): stay_ext_departure_notice_charge and stay_ext_first_installment_payment now declare an overwrite of
  stay_evt_payment_schedule "each installment carries the guest service fee and occupancy tax attributable to the amounts it
  collects" (each replaced_by states its own carve-out); the installment-1 courtesy is scoped to monthly stays and follows the tier
  active at collection; task 0's installment 1 reseeded 3990.08 -> 3772.04 (Gold at booking) so the record follows the rule;
  task 1's declined attempts (scheduled under Silver) stay at 3857.60. Notice charge also declares the booking-terms exemption
  sentence (kept-night back tax).
- F-2 (SOURCE-FACTOR RED): notice charge reworked into the charge for the kept nights the collections have not paid on any stay in
  progress (long monthly stays, and stays checked in while installment 1 was still declined, any tier); factors notice_length,
  later_nights_kept (new), notice_fee_rate, notice_tax_exemption, rewards_fee_relief, returning_guest_relief (new); coverage, the
  uncollected fees and the credit offset became plumbing. Task 0 charge 115.33 -> 114.02.
- F-3 (SOURCE-FACTOR RED): refunded_fee_base ladder removed; the fee base is every refunded fee-bearing amount for everyone;
  late_cancellation_fee_share (on/after check-in 50, within 7 days 75, else 100) added. Task 0 SF refund 55.33 -> 30.91.
- F-4 (SOURCE-FACTOR RED): next-day first night = max(arrival_next_day_pct, share). Task 1 unchanged (tier 1).
- Proof fields (task 0): why_false now names both collections (3772.04 + 672.00); grace hours 953.97; load-bearing figures
  26.23 / 11.15 / 6.48.
- F-5: tier-2 card share = 1 - outstanding credits / total price (no read of earlier refunds) in all five credit factors.
- F-7: departure SF scope sentence = every guest cancellation outside the full window and grace, subject to the cap (F-9 too).
- O-1: pet/extra refundable nights capped at the stay's nights. O-2: pay-part-now installment 1 carries the deposit share of the
  flat per-night tax. O-3: deposit share reaches the first affected night. O-4: travel tool stay_id text; installment and notice
  tool texts. GT tier_taken labels full.
- No change: F-6, F-8, F-10, O-5, O-6, O-7 (observations; consistent with the Rewards charter / blueprint claim).

### Round 3 (audit revision_2)
- task 0 finding 2 (SOURCE-FACTOR RED, proof field): design_rationale INITIAL_STATE counterfactual corrected — removing installment 1
  leaves the installment-0 collection, so the pet/extra shares stay on the monthly tier (78.58 / 331.78; SF 30.91); only removing both
  collections drops them to 0.00.
- task 0 observation 3: "plumbing" wording replaced by "part of the baseline method rather than declared factors".
- R2-O1 / R2-O2 (charter observations): no change — the cap is enforced by base stay_agg_service_fee_refund_cap (in force, count 1 < 3
  here); tier 2 of the first-night ladder differs as a rule. Charter, tools and task 1 untouched (task 1 PASS kept).

### Round 4 (validate_scenario: frozen_time format)
- frozen_time rewritten in the 'YYYY-MM-DD HH:MM:SS TZ' form the loader accepts: task 0 '2026-10-07 17:05:00 CDT' (TX-AUSTIN,
  Central daylight time), task 1 '2026-10-07 19:30:00 MDT' (CO-DENVER, Mountain daylight time); same wall-clock moments.
- The seven task tools now book posted_at as str(ctx.now())[:19] with the 'T' separator, so every row they write keeps the
  YYYY-MM-DDTHH:MM:SS form their docstrings promise (2026-10-07T17:05:00 / 2026-10-07T19:30:00, unchanged), matching the seeded
  ledger rows. No scored value, date span or elapsed-hours figure moves.
