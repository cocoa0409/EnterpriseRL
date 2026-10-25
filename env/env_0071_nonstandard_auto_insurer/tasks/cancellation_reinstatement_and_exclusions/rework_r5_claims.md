# Rework round 5: claims per revision_4 audit item

No scored values are given here. NC/RE/IC = nonpayment return / reinstatement / insured-request return (task 0); AD/EX/AB = re-listing / reported-resident exclusion / exclusion lift (task 1).

## R4-01: run-off retention beyond the fr liability window

**Closed.** I struck every state, form, type and out-of-state run-off day (NC and IC factors, and IC's plain out-of-state days).

- **What the run-off keeps now.** NC and IC keep exactly the fr charter's window:
  - certificate_runoff_days after the SR-26;
  - plus the SR-26 transmission days. These are the days from the ending date to the processing date, never more than sr26_transmit_within_days.
- **SR-26 already transmitted.** Unchanged: the run-off runs from the recorded certificate_end_date.

**Task 0 counts are met with record-keyed, real dimensions only:**

| Computation | Factors |
|---|---|
| NC | run-off rule; SR-26 transmission days; acquisition expense, withheld once on a term at its first cancellation; installment-plan cancellation charge |
| IC | run-off rule; SR-26 transmission days; short-rate retention; installment-plan cancellation charge (charged again only because the reinstatement reactivated the plan and this cancellation closes it again); daily-basis method |

The IC daily-basis method has three shapes:
- the re-written entry's daily rate;
- the whole re-written entry, when the cancellation takes effect inside the lapse;
- the recorded rate.

**RE's computation is changed within its event.** It now computes the reinstatement fee, using only point-25 service-charge keys:
- fee basis from the company's state schedule;
- how coverage is restored: the lapse length, and the certificate's SR-26 standing;
- certificate form;
- certificate type;
- filing state against garaging state.

The re-written premium is now a plain rule. The base auto_fees clause is overwritten, with the overwrite declared.

**Edges changed:**
- IC -> RE is now value_input (on the re-written entry).
- RE -> NC is now state_gate.

**World change, task 0 only.** The request now takes effect on the day it was received, so the insured-request cancellation is processed one day after its ending date. The persona is updated to match.

## R4-02: unreachable tiers

**Closed.**
- The run-off tier for a filing state outside the company's states is gone: the run-off keys were struck.
- The out-of-state fee charge's tiers are an FR-44 filing state, any other filing state, or the same state / no certificate. All three are reachable.
- The fee's lapse ladder starts at one day. Its fall-through, fewer than fee_lapse_days_mid days, is reachable.

## R4-03: ad_points_change_rel

**Closed.** It stays a parameter. Each tier now names its own value: low to mid, low to high, mid to high, mid to low, high to mid, high to low, unchanged.

## R4-04: occasional-operator count

**Closed.**
- **Charter convention.** The term rules (NC, RE, IC) and AB now state it: every rated driver other than the named insured, including a driver rated when the term was bound, is carried by a driver-added change. The recorded full_term_premium is the rating of the named insured and the scheduled vehicles.
- **Effect on the count.** Drivers rated at binding are therefore counted.
- **Seeds.** Both worlds already conform: no driver other than the named insured is rated at binding without an entry.

## R4-05: class change gated on an owner-operator certificate

**Closed.** It is struck with no replacement, and the prior-lapse relativity of the re-write is struck too.
