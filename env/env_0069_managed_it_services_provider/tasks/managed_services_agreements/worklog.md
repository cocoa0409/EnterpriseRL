# worklog managed_services_agreements (env_0069)
- draw_counts --tasks 2: t0 prerequisite_problems=3 factor_counts=[6,4,6,6]; t1 prerequisite_problems=3 factor_counts=[6,6,4,5]
- design: see plan.md (T0 ETF tree E<-R,M,Rn; T1 upgrade tree U<-L<-B,O)
- T0 policies written: R, M, Rn, E (managed.extended.yaml)
- T0 assembled; check_extended/check_compute --task 0 OK
- T0 per-task gates 7/7 green (round 1); rationale in tasks/0.json
- T1 policies written: B, O, L, U
- T1 per-task gates 7/7 green; frozen_time moved 2026-10-15 -> 2026-10-14 so INV-013814 stays one day short of the 45-day suspension threshold (no unclaimed system obligation)
- XF sweep (scratch): compute_basis quotes verbatim, baseline sentences in rule, no factor id inside a tool name, no factor binding reaching another factor's binding; scoped self-naming overwrites; sibling labor overwrites name each other's case
- validate_scenario: only "required document not found" (KB not yet rendered); frozen_time format and task_tools forbidden tokens clean
INSTANTIATE round 1: gates 7/7 green

## REWORK round 2 — plan (audit revision_1: T0-F1..F3, T1-F1..F3, C-1..C-6)
- C-2/T1-F1: re-tree task 1. The late fee no longer waits on labor. It prices the first late fee on the monthly invoice posted two months before the assessment month with no payment applied, measured only on what that invoice carried when posted. The upgrade root waits on three things: the late fee (standing discount), the after-hours remote labor and the onsite visit labor of September tickets. Both labor lines bill on the October invoice, which is not yet due. The labor reaches the upgrade through a labor-conversion discount (labor invoiced in the last 3 months against the monthly seat charge), which replaces the out-of-scope ticket count.
- C-1: the loyalty dollar rates become percentage tenure discounts off the tier rate (always below standard).
- C-3: one generic combination sentence per policy (only baseline-defined quantities, order fixed).
- C-4: sibling labor overwrites name the sibling's exact case (most recent invoice-route ticket of that class).
- C-5(a): exit scope = notices whose requested date is the later of the two, with base restated otherwise. C-5(b): onsite scope = wholly billable visits, with the base carve-out kept for partly included visits.
- C-6(a): fee scope = at most one active F3 and one active Business Premium subscription. C-6(b): exit scope = exactly one early termination request awaiting signature.
- T0-F1/T1-F2: cross-product rows priced by their charters on the order date (Continuum BDR without bundle 113.05/13.30/3.56). Balances backed by invoice/payment rows, counts by ledgers. Gold gains read steps.
- T0-F2: tier-moving near-misses: a service credit posted 12 months ago (renewal), a partial payment 2026-09-25 (cure speed).
- T0-F3/T1-F3: proof text regenerated from the seed; no hand-typed dates.
- Exit fee half-cent (T0-O2): avoided.

## round 2 — probe table (scratch probes.py; columns: probe | probe result | gold | rule tier that settles it)
- T0 fee: second cancelled F3 subscription with 12 licenses | 4586.4 | 4586.4 | frontline rule reads the active F3 only
- T0 fee: no active F3 (absent record) | 5408.84 | 4586.4 | frontline fall-through: every billed seat at seat_rate_usd
- T0 fee: Business Premium expired (absent record) | 4658.64 | 4586.4 | CSP credit fall-through 0
- T0 fee: closed prior Sentinel subscription | 4586.4 | 4586.4 | bundle credit reads the active subscription only
- T0 fee: Continuum plan closed (absent) | 4682.72 | 4586.4 | Continuum credit fall-through 0
- T0 reinstatement: second payment on the same latest date | 140.0 | 140.0 | same date, same cure days
- T0 reinstatement: latest payment before suspended_date | 160.0 | 140.0 | counts as no payment: cure reduction 0
- T0 exit: later withdrawn early termination request | 15368.89 | 15368.89 | only the request awaiting signature counts
- T0 exit: no request awaiting signature (absent) | 0.0 | 15368.89 | no notice to sign: fee 0
- T0 exit: no active Sentinel (absent) | 16793.82 | 15368.89 | security retention 0
- T0 renewal: never suspended (empty suspended_date) | 123.07 | 124.23 | price protection fall-through: lower of uplifted and list
- T1 after-hours: older unbilled after-hours ticket | 308.55 | 308.55 | latest resolution only
- T1 onsite: visit opened the day before (date-difference edge) | 362.5 | 362.5 | dispatch rule tier 'next day': recorded + 30
- T1 late fee: a line back-posted onto the August invoice today | 11.08 | 11.08 | not in the invoice's posting window: excluded
- T1 upgrade: no active Sentinel (absent) | 95.08 | 93.55 | training overlap 0
- T1 onsite next-day vs same-day coincide at 90 recorded minutes (120 either way); at 60 recorded minutes they give 90 vs 120, so the tiers are distinct.
- Same-minute ties: the labor rules state that the platform never stamps two resolutions of one agreement in the same minute. The exit rule scopes itself to exactly one request awaiting signature (C-6b), so no tie can arise. Reinstatement: two payments on the latest date give the same cure days.
- Half-cent: the exit fee moved from 15267.105 to 15368.89 (security_retention_short_pct 7.0). No scored amount in either task lands on a half-cent (308.546875, 11.08065, 93.5496, 4406.402).

## round 2 — XF23 method-shape all-pairs tables (any windowed sum of a field = one input; constant multipliers ignored)
- price_protection_rule (renewal): T1 uplifted only = rate x (1+u); T2 hold = rate; T3 lower of (rate x (1+u), list). T1 vs T2: T1 adds the uplift input. T1 vs T3: T3 adds the list input and a min. T2 vs T3: T3 adds uplift, list and min. PASS.
- frontline_seat_rule (fee): T1 = rate x (b - f) + rate x f x share; T2 = rate x (b - f) + flat; T3 = rate x b. T1 vs T3: T1 adds the F3 input f. T2 vs T3: T2 adds f and the flat tariff. T1 vs T2: T2 adds the flat tariff parameter. PASS.
- environment_revalidation_rule (reinstatement): T1 = fee + per-seat x seats; T2 = fee + flat; T3 = fee. T1 adds the seat input; T2 adds a tariff; T1 vs T2 differ by the seat input. Neither added tier is 0 over its domain. PASS.
- exit_billing_basis_rule (exit): T1 = sum(recent monthly fees) / 3; T2 = rate x covered seats (ledger); T3 = rate x ceil(contracted x pct). Each uses a different input (fee sum, seat ledger, contracted floor with a ceiling). PASS.
- after_hours_callout_rule (after-hours): T1 = max(m, 60); T2 = m + 15; T3 = m. T1 adds a max, T2 adds a tariff. PASS.
- onsite_dispatch_rule (onsite): T1 = max(m, 120); T2 = m + 30; T3 = m. T1 adds a max, T2 adds a tariff. PASS. They coincide only at m = 90.
- balance_band_rule (late fee): T1 = p x 1000 + p/2 x 4000 (no balance input); T2 = p x 1000 + p/2 x (b - 1000); T3 = p x b. T2 vs T3: T2 adds the band tariff. T1 vs T2 and T1 vs T3: they add the balance input. PASS.
- upgrade_pricing_rule (upgrade): T1 = c + (s - c) x share; T2 = c x list_std / list_own; T3 = s. T1 adds the current-rate input to s. T2 uses c and the own-list tariff. PASS.

## round 2 — XF24 events written by task tools and their base triggers (all stay inside managed)
- record_renewal_term: managed_renewed (no triggers). post_monthly_fee: managed_monthly_fee (none).
- record_reinstatement: managed_reinstated, which triggers managed:managed_reinstatement_fee (inside managed); it writes that row itself.
- sign_early_termination_notice: managed_notice_given, which triggers managed:managed_early_termination_fee when notice_type is early_termination (inside managed).
- post_remote_after_hours_labor / post_onsite_visit_labor: managed_billable_labor (none). The tools write no managed_ticket_resolved row, whose timebank trigger would cross categories.
- post_late_fee: managed_late_fee (none). sign_tier_upgrade: managed_tier_changed (none).

## round 2 — XF25 complete ledgers (seed)
- Task 0:
  - Sentinel: onboarding fee 1250.00 (bundle condition false on 2024-08-05), every monthly fee from 2024-10 to 2026-10 priced on the endpoint count of the 25th, and payments. The balance equals the unpaid 2026-10 fee. IR grants and forfeit back the 10.00 hours.
  - Continuum BDR: 113.05/13.30/3.56 (no bundle), onboarding 750.00, monthly fees 2024-10 to 2026-10 (3 x 113.05), and payments. The balance is 339.15. Three protected-server rows.
  - Licensing:
    - Order forms for every subscription and the cancellation.
    - Initial-purchase and cancellation license changes.
    - Annual cycle charges and payments.
    - For the cancelled P1M F3: 48.00 charged, a 44.80 refund (9.60 x 5 x 28/30) and a 3.20 payment.
  - Managed:
    - Every monthly fee carries the credits whose conditions held on its posting date (no CSP credit before 2025-03).
    - The near-miss credit of 2025-10-01 is netted in that month's payment.
    - The 2026-09-25 partial wire lowers the 2026-10-01 late fee on the July invoice to 35.71.
- Task 1:
  - Sentinel: onboarding fee 1250.00, enrollment of 28 workstations, monthly fees 2025-12 to 2026-10 (28 x 15.90), and payments. The balance equals the 2026-10 fee. One IR grant.
  - Continuum Plus: onboarding 250.00, monthly fees 2024-07 to 2026-10 (75.05), payments, and one protected server.
  - Managed: historical labor priced by each class's schedule at its posting. The 2025-04-01 late fee follows the first-late-fee schedule as of that day (25.00, where the minimum binds).

## round 2 — XF26
- Every plain binding that read a factor-owned binding was folded into `result`: uplifted/selected/net, seat_amount/frontline_seats/credit, built_fee, monthly_basis/reduction, billed_minutes, banded_amount, built_rate. The sweep reports no plain binding reading a factor binding.
- Factor sentences now name the result quantity they modify (e.g. "… of the renewal rate", "… on the monthly fee").

## round 2 claims (audit revision_1)
- C-1: `loyalty_remote_rate` and `onsite_loyalty_rate` are replaced by the percentage tenure discounts `tenure_labor_discount` and `tenure_visit_discount` (5 / 2.5 / 0 percent off the tier's own rate). No tier reaches or exceeds the standard rate on any ClearPath tier.
- C-2 / T1-F1: task 1 is re-treed. The late fee has no prerequisite and is measured only on the lines the invoice carried when posted. Its scope is the first fee on the invoice posted two months back, with nothing applied to it and no other invoice in its month. Back-posted lines are excluded (probe). The September labor bills on the not-yet-due October invoice. The upgrade waits on the late fee (standing discount) and on both labor charges (new labor-conversion discount). The tree is U <- {L, B, O}, with 3 value_input edges.
- C-3: every policy carries one generic combination sentence that fixes the order: replacements, then the combined percentage applied once, then flat additions / minimum / cap. Factor sentences name the result quantity (XF26).
- C-4: each sibling labor overwrite names the other's exact case (the most recent invoice-route ticket of that class).
- C-5(a): the exit scope is notices whose requested date is the base later-of date, with the base fee restated otherwise. C-5(b): the onsite scope is wholly billable visits, and the base partial-inclusion carve-out is restated.
- C-6(a): the fee scope is at most one active F3 and one active Business Premium subscription. C-6(b): the exit scope is exactly one request awaiting signature, and the "most recently registered" clause is removed. The probe table is above.
- T0-F1 / T1-F2: other-category rows are priced by their own charters on the order date (Continuum BDR 113.05/13.30/3.56, no bundle). Onboarding fees, monthly fees, payments, endpoint/device/license ledgers, IR grants and order forms are complete, so balances and counts are reproducible. Gold gains read steps.
- T0-F2: tier-moving near-misses: a 2025-10-01 service credit just outside the renewal window, and a 2026-09-25 partial wire against the latest-payment cure test.
- T0-F3 / T1-F3: design_rationale, traces, tracing and closure are regenerated from the executed run and seed, with no hand-typed dates or amounts.
- Observations: O-2 effect text generalised; O-3/T0-O2 half-cent removed (exit fee now 15368.89); O-8 XSUM reads the client's whole Sentinel ledger, as the rule says; O-4/O-5 unchanged (observations).
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 2: gates 7/7 green

## REWORK round 3 — relative-outcome / monotonicity sweep of every ladder (C-1r class)
Format: factor: tiers (most specific → fall-through) | outcome versus the standard, on every tier where the policy applies | direction | verdict.
- Auto renewal rate:
  - first_renewal_uplift_schedule: cap−2 / cap−1 / cap | always below the cap (Enterprise 1.5 / 2.5 / 3.5) | longer commitment or tenure → lower uplift | OK
  - price_protection_rule (method): uplifted only / lowest of (uplifted, list, expiring × (1 + 2%)) / lower of (uplifted, list) | the loss-of-protection tier is a penalty for suspension; the loyalty tier is never above the standard | OK (C-7 fixed)
  - seat_growth_adjustment: −1.0 / −0.5 / 0 | reductions only | more growth → more off | OK
  - service_level_renewal_adjustment: −1.5 / −0.75 / 0 | reductions | more credits → more off | OK
  - payment_standing_renewal_adjustment: +1.0 / +0.5 / 0 | surcharge for late fees, capped by the uplift cap | more late fees → more | OK
  - service_intensity_renewal_adjustment: +1.0 / −0.5 / 0 | more tickets per seat → higher | OK
- Current month fee:
  - seat_volume_price_break: 4 / 2 / 0 % off | more seats → more off | OK
  - sentinel_bundle_credit: 3 / 1.5 / 0 | deeper commitment → more off | OK
  - frontline_seat_rule (method): F3 seats at 50% / F3 seats out plus min(flat 95, those seats at rate) / every seat at rate | both tiers ≤ standard on every tier (Monitor 1 F3 seat → min(95, 38.50) = 38.50 = standard, never above) | OK (C-1r(c) fixed)
  - server_management_charge: 50 each (≥5) / 60 each (1–4) / 0 | the total never falls when a server is added (4 → 240, 5 → 250) | OK (volume price moved from 45 to 50)
  - continuum_bundle_credit: 2 / 1 / 0 | OK
  - csp_licensing_credit: 1.5 / 0.75 / 0 | OK
- Reinstatement charge:
  - first_suspension_relief: 50% / 75% / 100% of the fee | relief ≤ standard | an established payment record → more relief | OK
  - environment_revalidation_rule (method): fee + 150 + 2.50 × seats / fee + 150 / fee | a longer suspension never costs less | OK (C-1r(b) fixed)
  - cure_speed_reduction: 25 / 10 / 0 | faster cure → more off | OK
  - monitoring_continuity_reduction: 20 / 10 / 0 | OK
- Signed exit fee:
  - tenure_exit_schedule: pct−20 / pct−10 / pct | longer tenure → lower | OK
  - exit_billing_basis_rule (method): average of the last 3 fees / rate × covered seats / rate × floor | a basis, not a relief; it applies only where covered seats exceed the floor (actual billing replaces the commitment floor) | OK
  - security_retention_reduction 15 / 7 / 0; service_failure_exit_reduction 25 / 10 / 0; notice_lead_reduction 10 / 5 / 0; backup_retention_reduction 5 / 2.5 / 0 | all reductions, monotone | OK
- After-hours remote labor:
  - after_hours_day_multiplier: tier multiplier +0.5 (Sunday) / +0.25 (Saturday) / tier multiplier | always ≥ the tier's own after-hours multiplier on every tier (Monitor 2.0 → 2.25 / 2.5) | OK (relative)
  - tenure_labor_discount: 5 / 2.5 / 0 % off | OK
  - after_hours_callout_rule (method): max(m, 60) + 15 / m + 15 / m | P1 ≥ P2 ≥ P3/P4 for every m | OK (P1 no longer below P2)
  - remote_scope_courtesy 15 / 5 / 0; soc_overlap_reduction 10 / 5 / 0; after_hours_frequency_reduction 5 / 2.5 / 0 | OK
- Onsite visit labor:
  - shared_trip_schedule: 0 / 50% of the tier trip charge / the tier trip charge | the policy is scoped to tiers whose trip charge is above zero, so the three outcomes are distinct and ≤ standard | OK (C-1r(a) fixed)
  - onsite_dispatch_rule (method): max(m + 30, 120) / m + 30 / m | same-day ≥ next-day ≥ later for every m | OK (same-day no longer below next-day)
  - tenure_visit_discount 5 / 2.5 / 0; onsite_visit_courtesy 10 / 5 / 0 | OK
- First late fee:
  - payment_record_rate: 1.0 / 1.25 / tier rate (1.5) | below the standard | OK
  - tenure_late_fee_minimum: 5 / 10 / tier minimum (25–50) | below | OK
  - balance_band_rule (method): capped / graduated / flat | banded ≤ p × b, continuous and non-decreasing in b | OK
  - relationship_courtesy 20 / 10 / 0; recent_payment_courtesy 25 / 10 / 0 | OK
- Essentials upgrade rate:
  - upgrade_pricing_rule (method): c + 50% (s − c) / c + (s − c) × elapsed / term / s | the current Essentials rate c ≤ 89.00 < s ≥ 119.04, and elapsed < term, so both tiers are below the standard | OK (the ratio tier, equal to the standard at c = list, is replaced)
  - upgrade_volume_discount 4 / 2 / 0; term_commitment_discount 2 / 1 / 0; upgrade_standing_discount 2 / 1 / 0; training_overlap_discount 3 / 1.5 / 0; labor_conversion_discount 3 / 1.5 / 0 | OK

## round 3 — XF23 re-check of the changed method factors
- price_protection_rule:
  - T3 = min(uplifted, list, expiring × (1 + ceiling)). Against T1 (uplifted only) it adds the list input and a min; against the fall-through min(uplifted, list) it adds the ceiling tariff.
  - The uplift schedule stays live in T3 (u < ceiling selects the uplifted rate).
  - PASS.
- after_hours_callout_rule: max(m, 60) + 15 versus m + 15: the max is an added operation. PASS.
- onsite_dispatch_rule: max(m + 30, 120) versus m + 30: the max is an added operation. PASS.
- environment_revalidation_rule: fee + flat + per-seat × seats versus fee + flat: the seat input is added. PASS.
- frontline_seat_rule: tier 2 now carries a min (an added operation) against tier 1. PASS.
- upgrade_pricing_rule: tier 2 adds the elapsed-term input against the fixed-share phase. PASS.
- Values of both worlds are unchanged after the re-run: T0 140.00 / 124.23 / 4586.40 / 15368.89; T1 308.55 / 362.50 / 11.08 / 93.55. All factor and baseline figures are unchanged.

## round 3 claims (audit revision_2)
- C-1r(a): the shared trip is now relative (50 percent of the tier's trip charge), and the onsite schedule is scoped to tiers whose onsite_trip_charge_usd is above zero. The sibling after-hours overwrite names that scope.
- C-1r(b): re-validation after 30+ days = fee + flat 150 + 2.50 × seats, never below the 15–29-day fee + 150.
- C-1r(c): the frontline flat fee is min(95.00, the removed seats at seat_rate_usd), never above billing those seats.
- C-1r class sweep (table above). Further members found and fixed:
  - the day multiplier was absolute (on Monitor, Saturday fell below the weekday multiplier); it is now tier multiplier + 0.25 / + 0.5;
  - a P1 call-out billed less than P2 at long minutes; it is now max(m, 60) + 15;
  - a same-day dispatch billed less than next-day at long minutes; it is now max(m + 30, 120);
  - the server volume price let a fifth server lower the total; it is now 50.00;
  - the renewal-term upgrade ratio tier equalled the standard at the list rate; it is now a term-spread step-up.
- C-7: the "held at expiring rate" tier is replaced by the lowest of (uplifted, list, expiring × (1 + loyalty_ceiling_pct)). It is structurally distinct and keeps the uplift schedule live.
- No task value regresses (both worlds re-run; computations, gold and traces unchanged except the method wording in traces). Rationales carry a revision-3 note.
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 3: gates 7/7 green

## REWORK round 4 — band-boundary probes (scratch probes.py on the task worlds; columns: probe | n | total)
- fee total, covered seats | 39 | 3998.59
- fee total, covered seats | 40 | 3998.59
- fee total, covered seats | 74 | 8077.29
- fee total, covered seats | 75 | 8192.18
- upgrade rate x seats | 24 | 2294.16
- upgrade rate x seats | 25 | 2387.75
- upgrade rate x seats | 49 | 4707.92
- upgrade rate x seats | 50 | 4801.0
- renewal rate x seats (contracted 40) | 43 | 5368.98
- renewal rate x seats (contracted 40) | 44 | 5492.96
- renewal rate x seats (contracted 40) | 49 | 6114.22
- renewal rate x seats (contracted 40) | 50 | 6238.0
- renewal rate x seats (contracted 160) | 175 | 21850.5
- renewal rate x seats (contracted 160) | 176 | 21973.6
- renewal rate x seats (contracted 160) | 199 | 24831.22
- renewal rate x seats (contracted 160) | 200 | 24956.0
- fee total, F3 users added as new seats (seats = 38 + F3) | 8 | 4686.16
- fee total, F3 users added as new seats (seats = 38 + F3) | 9 | 4695.13
- fee total, F3 users added as new seats (seats = 38 + F3) | 10 | 4751.57
- fee total, F3 users added as new seats (seats = 38 + F3) | 11 | 4845.33
- frontline charge 9 -> 10 users at Monitor rate 38.5 (never above f x rate) | 9/10 | 103.5 / 122.75 (f x rate: 346.5 / 385.0)
- frontline charge 9 -> 10 users at Essentials rate 89.0 (never above f x rate) | 9/10 | 103.5 / 148.0 (f x rate: 801.0 / 890.0)
- frontline charge 9 -> 10 users at Standard rate 124.0 (never above f x rate) | 9/10 | 103.5 / 165.5 (f x rate: 1116.0 / 1240.0)
- frontline charge 9 -> 10 users at Enterprise rate 236.0 (never above f x rate) | 9/10 | 103.5 / 221.5 (f x rate: 2124.0 / 2360.0)
- server charge 4 -> 5 servers | 4/5 | 240 / 250
- late fee: line added to INV-013814 on 2026-08-20 (before its due date) | 2315.9 | 9.12
- late fee: same line posted on the assessment day | 2165.9 | 8.71
- Every total is non-decreasing from n to n+1 at each band boundary:
  - fee 39 -> 40 is equal: the floor of 40 billed seats applies to both, and the volume break now reads the billed seats.
  - fee 74 -> 75, upgrade 24 -> 25 and 49 -> 50, renewal growth (contracted 40: 43 -> 44 and 49 -> 50; contracted 160: 175 -> 176 and 199 -> 200), F3 users 8 -> 11 added as new seats, and servers 4 -> 5 all rise.
- Each frontline charge is ≤ f × seat rate on every tier.
- C-8 probe: a line added to INV-013814 on 2026-08-20 (before its due date) is in the late-fee base (2315.90 -> fee 9.12). The same line posted on the assessment day is left out (2165.90 -> 8.71).

## round 4 — all-units ladder sweep (any ladder whose total can fall when one unit is added)
- Graduated now:
  - seat_volume_price_break (fee): per billed seat, from the 40th and the 75th seat.
  - upgrade_volume_discount: per covered seat, from the 25th and the 50th.
  - seat_growth_adjustment (renewal): per seat from the first seat 10 / 25 percent above contracted.
  - frontline_seat_rule: per F3 user, frontline_user_fee_usd 11.50 each for the first 9 users and 50 percent of the rate for each further one; the cap at the seat rate is kept.
- Already monotone:
  - server_management_charge (240 -> 250 at 4 -> 5).
  - balance_band_rule (graduated and continuous).
- Not unit-priced totals, so not members: shared_trip_schedule (per-visit charge by visit history), the frequency, credit-count and courtesy ladders (a percentage of one charge chosen by history), and labor_conversion_discount (labor dollars are not billed units of the rate).

## round 4 claims (audit revision_3)
- C-1r(d): the renewal-term upgrade tier is now min(current rate + (Standard list − own list), standard upgraded rate × (1 − renewal_upgrade_cap_pct 3%)). It is always above the current rate and below the standard. XF23: the list inputs and the min are added against both other tiers.
- C-1r(e): the frontline schedule is graduated. 1–9 F3 users pay frontline_user_fee_usd 11.50 each (never above the seat rate). From 10 users, the first 9 pay 11.50 and each further user pays 50 percent of the rate. The charge rises with every user and never exceeds billing those seats.
- C-1r(f): the fee volume break, the upgrade volume discount and the renewal seat-growth adjustment are graduated (each band's percentage is earned only by the seats inside it). The fee volume break reads the billed seats. The probe table above shows no total decreases at any band boundary.
- C-8: the late fee measures the invoice's own lines as they stood at the end of the day before the assessment day. It includes a line added before the due date and leaves out entries posted on the assessment day. The scope is the fee assessed and posted on the first day of the month on the agreement's only invoice unpaid at the end of the previous day. Task 1 is frozen on that assessment day (2026-10-01), with no window counted back from today.
- Values re-run:
  - Task 0: reinstatement 140.00, renewal 124.82, October fee 4686.16, exit 15656.52. The T0 history fees, credits, late fees and payments were re-priced by the revised schedules.
  - Task 1: after-hours 308.55, onsite 362.50, late fee 8.71, upgrade 95.44.
  - Traces, tracing, closure and rationales were regenerated from the run, so no stale figures remain outside the revision-history notes.
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 4: gates 7/7 green

## REWORK round 5 — probes (scratch chk.py)
- Task 1 world: late-fee base 2165.90, fee 8.71 (unchanged). The 2025-04-01 late fee sits on a settled invoice and nets out.
- Probe, C-10: INV-013814 carries an unpaid prior late fee of 30.00 (2026-09-01). The base stays 2165.90 because that fee is left out; the fee changes only because the payment-record rate now sees a late fee in 12 months.
- Probe: as above, plus a 500.00 partial payment on 2026-09-20. The base is 1665.90 (the payment counts in full against the other lines, as in the base measure).
- Seat-quantity wording sweep (C-9 class):
  - Fee: the volume break uses the billed seats (covered or floor, whichever is greater), billed seats for the fee use seat_count or the floor, and the Sentinel and CSP tests use seat_count.
  - Renewal: growth uses covered seats on the ledger; intensity now says seat_count.
  - Reinstatement: now "every seat of seat_count".
  - Exit basis: covered seats on the ledger or the floor.
  - Upgrade volume: covered seats on the ledger.
  - Every rule word now names the quantity compute reads.

## round 5 claims (audit revision_4)
- C-9: the volume-break rule now reads "the billed seats for the break, which are the covered seats on the seat ledger … or the minimum-commitment floor, whichever is greater". Each band's percentage is counted and divided over billed seats, matching compute's MX(covered_seats, floor_seats). Basis and ladder are updated. The sweep fixed two further wording members: intensity ("seat_count") and re-validation ("every seat of seat_count").
- C-10: "late fees are not themselves assessed late fees" is now stated in the late-fee rule. Compute subtracts the late fees on the invoice that carries the agreement's most recent late fee when that invoice is still unpaid. Settled invoices' late fees net out against their payments, and payments count in full against the other lines, which equals the base measure. The scope adds "no other invoice assessed a late fee on the day of that invoice's most recent late fee" (tie rule). Probed with a prior unpaid late fee on the invoice.
- Neither task's values move (T0 140.00 / 124.82 / 4686.16 / 15656.52; T1 308.55 / 362.50 / 8.71 / 95.44). Each rationale has a revision-5 note.
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 5: gates 7/7 green

## REWORK round 6 — probes (scratch chk.py on the task-1 world; result = late-fee base, fee)
- World: (2165.90, 8.71), unchanged.
- Prior unpaid late fee 30.00 on the assessed invoice INV-013814: base 2165.90. The late-fee line is excluded (found by exact invoice key: the invoice of the most recent late fee, still unpaid). The fee is 13.06 only because the payment-record rate sees a late fee in 12 months.
- The same, plus a 500.00 partial payment on INV-013814: base 1665.90. The payment counts in full against the invoice's other lines.
- Unpaid 25.00 late fee on another invoice INV-013756 whose principal was paid: that invoice has an amount unpaid (late fees included), so the fee is out of this schedule's scope and falls under the base rule. For reference, compute also leaves the 25.00 out (base 2165.90).
- DSL note (C-10r route):
  - The compute language can select a row only by exact filter values or by the latest date. It has no way to derive the assessed invoice's number when that invoice carries no earlier late fee: no record points at it, and strings cannot be built.
  - The exact key is therefore used where a record supplies it (the invoice of the most recent late fee).
  - The scope sentence makes every other invoice settled in full, late fees included, so the ledger balance less that exact-keyed late-fee sum equals the invoice's own balance in every in-scope case.
  - The same-day clause stays: it is what makes the most-recent-late-fee read single-valued.

## round 6 claims (audit revision_5)
- C-10r:
  - The rule now defines the base as the assessed invoice's own charge lines other than late-fee lines, a line added before its due date included, less every payment, service credit and credit memo applied to it, with payments counting in full. It says that no late-fee line enters that balance.
  - The scope is now "the agreement's only invoice with any amount unpaid … its late fees included, so that every other invoice is settled in full together with any late fee it carries". The auditor's invoice B (principal paid, late fee unpaid) is therefore out of scope and under the base rule.
  - The assessed invoice's own late fees are removed by exact invoice key.
  - Probes for all three requested cases are above.
  - Deviation from the prescribed route: the invoice number of a first-time-assessed invoice cannot be keyed in the compute DSL, so the ledger identity is kept, made exact by the scope. The same-day clause is kept because the late-fee read needs it (see DSL note).
- No value moves (T1 late fee 8.71; all other figures unchanged). The task-1 rationale has a revision-6 note.
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 6: gates 7/7 green

## REWORK round 7 — renderer findings (render_r1.md)
### probes (scratch probe.py, current-month fee on the task-0 world with the seat ledger, seats, rate and F3 count set as shown)
- billed 8 / F3 12 / rate 40.00: 266.02  rule: (8-8) x 40 + 8 x 11.50 = 92.00 before credits; with F3 9: 266.02 F3 8: 266.02
- billed 46 rate 124.82, F3 8 -> 4686.16
- billed 46 rate 124.82, F3 9 -> 4580.55
- billed 46 rate 124.82, F3 10 -> 4522.39
- billed 46 rate 124.82, F3 11 -> 4464.22
- billed 46 rate 124.82, F3 12 -> 4406.06
- seats 39 -> fee 3883.93
- seats 40 -> fee 3998.59
- seats 74 -> fee 8077.29
- seats 75 -> fee 8192.18
- Billed 8 / F3 12: the treated F3 seats are min(12, 8) = 8. The top tier bills 8 x 11.50 = 92.00 (no flat fee beyond the treated seats, no negative further term), the same as the 1–9 tier, as the rule says.
- At fixed billed seats, more F3 users lower the fee: an F3 user replaces a full seat. Seat boundaries 39 -> 40 and 74 -> 75 still rise.

### overwrite sweep: retired clause vs out-of-scope restatement in replaced_by
| policy / base clause | content of the retired clause | restated for out-of-scope cases |
| --- | --- | --- |
| auto_renewal_rate / renewal uplift | uplift by cap; rounded half up; list-less-term-discount comparison; lower applies | all (finding 2: rounding and "in which case the lower rate applies" added) |
| current_month_fee / monthly fee | invoiced in advance on monthly_invoice_day; rate x billed seats; rounded half up | all (finding 5: invoicing day added) |
| reinstatement_charge / reinstatement fee | fee of reinstatement_fee_usd; invoiced on the reinstatement date; falls due under normal terms | in scope for every reinstatement; invoicing date and due terms restated in the scope sentence |
| signed_exit_fee / exit fee | pct x rate x floor seats x service months after the effective date to term end; rounded half up; invoiced on the date the notice takes effect | all (finding 6: invoicing date added) |
| after_hours_remote_labor and onsite_visit_labor / labor amount | minutes/60 x remote or onsite hourly rate; x after-hours multiplier; rounded half up; + trip charge per wholly billable onsite visit | all, now named remote_hourly_rate_usd / onsite_hourly_rate_usd and "each onsite visit that is wholly billable" (same tail in both siblings) |
| first_late_fee / late fee amount | late_fee_pct_monthly of the unpaid balance on the assessment day (the measure); rounded half up; or the minimum if greater | all (the measure name added) |
| essentials_upgrade_rate / tier-change rate | new list less new tier's term discount for the current term; rounded half up; longest offered term not exceeding it; or none if no such term | all (finding 3: "or none if there is no such term" and the parameter names added) |
| essentials_upgrade_rate / registration | registers a service request carrying request type, target tier, computed effective date; pending signature; never applies the change itself | all (finding 4: what the request carries added) |

## round 7 claims (render_r1 findings)
- 1: the frontline top-tier compute now caps the per-user fee count at the treated F3 seats, min(min(F3, billed), frontline_group_min - 1), and the further term at max(treated - (frontline_group_min - 1), 0). The rule and compute agree; probe billed 8 / F3 12 gives 92.00 before credits. Band boundaries were re-probed and are non-decreasing.
- 2: the renewal replaced_by restates the base rule in full, rounding and "in which case the lower rate applies" included.
- 3: the tier-change replaced_by restates the base rate rule in full, "or none if there is no such term" included.
- 4: the registration replaced_by restates that the request carries the request type, the target tier for a tier change and the effective date computed under this charter.
- 5: the monthly-fee replaced_by restates "invoiced in advance on monthly_invoice_day of that month".
- 6: the exit-fee replaced_by restates "invoiced on the date the notice takes effect on the agreement".
- Sweep: the two labor siblings (hourly-rate names) and the late fee (measure name) were also aligned with their retired clauses. The reinstatement overwrite was already complete.
- No value moves (T0 140.00 / 124.82 / 4686.16 / 15656.52; T1 308.55 / 362.50 / 8.71 / 95.44). Combination sentences and their order are unchanged.
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 7: gates 7/7 green

## REWORK round 8 — C-11 probes (scratch probe.py, exit fee on the task-0 world after the gold writes; columns: fee count, fee sum, basis rule, exit fee)
- world (count, sum, rule, fee): (3, 13824.74, 2, 15656.52)
- four fees in the window (July fee posted 2026-07-09): (4, 18282.51, 2, 15528.71)
- two fees in the window (August fee posted 2026-07-02, outside): (2, 9255.45, 3, 19507.49)
- With four fees in the window, the basis is the average of all four (18282.51 / 4), as the rule now says. With two fees, the "fewer than three" tier applies (seat_rate_usd x covered seats). The world has exactly three fees, so its value is unchanged.

### count-based tier sweep (rule words vs compute operator)
| policy.factor | rule words | compute | agree |
| --- | --- | --- | --- |
| renewal.first_renewal_uplift_schedule | renewal_count is 0 / three or more renewals / 24 months or more | == 0 / >= 3 / >= 24 | yes |
| renewal.price_protection_rule | live rate_hold_min_tenure_months months or more | >= K | yes |
| renewal.service_level / payment_standing | high count or more / one up to high less one / none | >= K / >= 1 / else | yes |
| renewal.service_intensity | 3 or more per seat of seat_count / fewer than seat_count | >= 3 x seat_count / < seat_count | yes |
| renewal.seat_growth | each seat from the first at least 10 / 25 % above | ceil thresholds, >= | yes |
| fee.volume / upgrade.volume | from the 40th (25th) / 75th (50th) seat | >= K, graduated counts | yes |
| fee.sentinel_bundle | 36 months or more AND endpoints at least seat_count | >= / >= | yes |
| fee.frontline | group_min or more / one up to group_min less one | >= K / >= 1 | yes |
| fee.server_management | servers_volume_min or more / one up to min less one / none | >= K / >= 1 | yes |
| fee.csp | at least seat_count / one up to seat_count less one | >= seat_count / >= 1 | yes |
| reinstatement.relief | no earlier fee AND relief_payments_min or more / fewer | == 0 and >= K / < K | yes |
| reinstatement.revalidation | long_days or more / mid up to long less one / shorter | >= / >= / else | yes |
| reinstatement.cure_speed | fast_days or fewer / more than fast up to mid / later | <= / <= / else | yes |
| exit.tenure | 36 or more / 24 up to 35 | >= / >= | yes |
| exit.billing_basis | three or more fees (fixed, C-11) / fewer than three | >= 3 / < 3 | yes (fixed) |
| exit.security / backup retention | 365 days or more / zero up to 364 | >= 365 / >= 0 | yes |
| exit.service_failure | high count or more / one up to high less one | >= / >= 1 | yes |
| exit.notice_lead | long or more / mid up to long less one / fewer | >= / >= | yes |
| after_hours.frequency | high count or more / two up to high less one / one | >= K / >= 2 | yes |
| after_hours.tenure, onsite.tenure | 24 or more / 12 up to 23 | >= / >= | yes |
| onsite.shared_trip | waiver count or more / two up to waiver less one / single | >= K / >= 2 | yes |
| onsite.dispatch | same day / next day / later | DAYS == 0 / == 1 / else | yes |
| late_fee.rate | no late fee AND payments_min or more / fewer | == 0 and >= K / < K | yes |
| late_fee.minimum | long or more / mid up to long less one | >= / >= | yes |
| late_fee.band | band_high or more / band_low up to band_high | >= / >= | yes |
| late_fee.recent_payment | one or more in 1 month / none then but one or more in 3 | >= 1 / >= 1 | yes |
| upgrade.pricing | renewal_count 0 / 1 or more, AND tenure months or more | == 0 / >= 1, >= K | yes |
| upgrade.commitment | long or more / mid up to long less one / fewer | >= / >= | yes |
| upgrade.standing | none / exactly one / two or more | == 0 / == 1 / else | yes |
| upgrade.training | full or more / one up to full less one | >= / >= 1 | yes |
| upgrade.labor_conversion | at least high share / at least mid share but less than high | >= / >= | yes |

## round 8 claims (audit revision_7)
- C-11: the exit billing-basis rule now reads "when three or more monthly fees were posted in that window and the covered seats exceed the floor, the basis is the average of the monthly fees posted in that window, their sum divided by their number". Compute divides by the count (recent_fee_sum / recent_fee_count); the ladder and basis are updated. Probes: four fees -> the average of four; two fees -> the fewer-than-three tier.
- Count-tier sweep: every count-based tier's words match compute's operator (table above); no other member found.
- No value moves (T0 exit fee 15656.52 with exactly three fees; all other figures unchanged).
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 8: gates 7/7 green

## REWORK round 9 (seed only) — exhaustive cross-product pass against the published products
Hashes are unchanged: managed.extended.yaml 1a19b120e61f8a88, task_tools.py 819877d3171b8861.

| task | row / holding | published rule checked | state |
| --- | --- | --- | --- |
| T0 | Sentinel MDR Advanced, ordered 2024-08-05 | ordering_and_pricing: list less 6% (36-month), bundle only with an active ClearPath of rank ≥4 (not met: ClearPath went live 2024-10-01, Standard is rank 3); onboarding fee max(10 x 45, 1250) = 1250 posted on the order date | consistent |
| T0 | Sentinel activation 2024-09-01, term to 2027-08-31 | deployment_and_activation: 90% of 45 contracted needs 41; 47 enrolled; term ends the day before the anniversary | consistent |
| T0 | Sentinel monthly fees 2024-10..2026-10 | endpoint_true_up_billing: workstations and servers counted on the 25th, floor 41, first fee the month after activation; paid on the 24th; 2026-10 open = balance 790.07 | consistent |
| T0 | Sentinel IR ledger | ir_hours_ledger: a grant at activation and at each anniversary, unused hours forfeited (0% rollover) | **fixed S2**: 2025-09-01 forfeit 10 and 2026-09-01 grant 10 added |
| T0 | Continuum BDR, ordered 2024-08-05 | ordering_rates_and_tier_changes: term discount only, no bundle (ClearPath not active); tier_entry_requirements: 3 items, 1 server (3 servers); onboarding max(195 x 3, 750) = 750 | consistent |
| T0 | Continuum monthly fees 2024-10..2026-10 | monthly_plan_fee: 3 x 113.05; first fee the month after activation; 2026-10 open = balance 339.15 | consistent |
| T0 | Microsoft 365 Business Premium (P1Y annual, 48) and F3 (P1Y annual, 8) | purchase pricing: annual charge qty x 12 x price; renewal at the price list; order forms signed | consistent |
| T0 | M365 administration fees | monthly_administration_fee_invoicing + coverage share (0% while ClearPath is active or notice given; any other status gives no reduction): every month before 2026-10-01 posted at 0% (no entry); 2026-09 fee owed 2026-10-01 while suspended | **fixed S4**: Premium 76.80, F3 14.00 posted 2026-10-01 on new invoices; balances 76.80 / 14.00 |
| T0 | cancelled F3 P1M (5 licenses, 2026-06-10 / 06-12) | prompt_cancellation_refund_basis case A: refunded as never used, 9.60 x 5 = 48.00; no deductions | **fixed S5**: refund 48.00, residual 3.20 payment removed, balance 0 |
| T1 | Sentinel MDR Advanced, ordered 2025-10-06 | list rates (Essentials rank 2 < 4), onboarding 1250, activation 2025-11-01 (28 ≥ 24 of 26 contracted), IR grant at activation, next anniversary 2026-11-01 after frozen; monthly fees 2025-12..2026-10 at 28 x 15.90; 2026-10 open | consistent |
| T1 | Continuum Backup Plus, ordered 2024-05-20 | tier_entry_requirements: 3 items at order | **fixed S3**: two workstations protected 2024-06-15 (3 items); monthly fee 75.05 + 2 x 10.93 = 96.91 re-priced 2024-07..2026-10 with payments; balance 96.91 |
| T0/T1 | timebank, hardware, project | — | no holdings seeded in either task, so no look-back window applies |

Scored values are unchanged in both tasks (managed factors read only status, tier, term, endpoint and license quantities). check_compute and replay are green.

## round 9 claims (KB audit revision_2 src items)
- S2: the task-0 Sentinel IR ledger now carries the 2026-09-01 anniversary: a forfeit of 10.00 hours for contract year 2025-09-01 and a grant of 10.00 for 2026-09-01. The balance stays 10.00.
- S3: the task-1 Continuum Backup Plus plan now protects three items at order (server CDA-FS01, workstations CDA-WS-PRINC01 and CDA-WS-CAD02). protected_count is 3; every monthly fee and payment is re-priced to 96.91, and the balance is 96.91.
- S4: the task-0 2026-09 Microsoft 365 administration fees are posted 2026-10-01 under the published schedule: Premium 76.80, F3 14.00. The coverage share is full because ClearPath was suspended on the posting day. Balances are 76.80 / 14.00.
- S5: the task-0 cancelled F3 refund is 48.00 (refunded as never used), and the residual 3.20 payment is removed. This supersedes the 44.80 recorded in the round-2 XF25 note.
- Exhaustive pass: table above; no further member found. Scored values are unchanged; the rationales have revision-9 notes.
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 9: gates 7/7 green
