# worklog — virtual_visit_booking_and_fees (env_0081), round 1

## Step 0 — draws
```
{"task": 0, "key": "env_0081_virtual_primary_care_provider/virtual_visit_booking_and_fees/0", "prerequisite_problems": 3, "problems": 4, "factor_counts": [5, 4, 6, 5]}
{"task": 1, "key": "env_0081_virtual_primary_care_provider/virtual_visit_booking_and_fees/1", "prerequisite_problems": 2, "problems": 3, "factor_counts": [4, 6, 4]}
```

## Step 0 — charter / DSL pre-check (findings that shape every design)
- Holding = one visit_appointments row. SUM/COUNT/MAX/LATEST are auto-scoped to visit_id=HID; X* reads
  forbid the primary category. => cross-visit counters (courtesy waivers -> visit_msr_fee_occurrences_12m,
  included visits -> visit_msr_included_used_year, sponsor plan-year visits, established status) are not
  computable. DECISION: no late-cancellation / no-show fee policy (courtesy count uncomputable; a compute
  that ignored it would silently contradict an in-force base clause), no path decided by a counter.
- Status / path / reschedule events carry no amount: they stay opening facts; every problem is a priced
  write (visit_charges / visit_estimates) on ONE visit, so value_input edges run through that visit's
  posted lines (SUM) and estimates (LATEST).
- Compute has no subscripting: catalogue maps keyed by tier/plan are restated as K params, quoted as
  "the price the visit catalogue lists for the tier".
- Time of day is only testable by string comparison of scheduled_start against F('booked_date')+' HH:MM';
  exact for the Urgent Care Video Visit (booking_horizon_days 0: start date = booking date), the only type
  whose after_hours_surcharge is above zero.
- Path pack_credit triggers pack writes (D4): never written.
- FLOOR NOTE (sent to coordinator 2026-10-25): base visit amounts carry <= 2 independent priced
  dimensions each (fee = path x tier; surcharge = time; cost share = coverage figures). Reaching the
  drawn 4-6 factors per computation needs Larkspur-published keyed schedules (realism bar R1/R2/R5) on
  top of base; each such factor is listed below as ENGINEERED with its realism argument, for the audit.

## Step 0 — feasibility of the drawn factor counts (2026-10-25, blocking; coordinator messaged twice)
Per-computation ceiling of INDEPENDENT factors that can all bite in ONE task world (A1: no factor reads
another's binding; A5/A7: no multiplicative split / masking cap):
| amount (one line on one visit) | realistic biting factors in one world | why it stops there |
|---|---|---|
| visit fee / its billing-error refund | 1 (member price of the tier live on the booking date) | path x tier x standing gate each other (A1/A5); sponsor fees and member prices are exclusive paths |
| after-hours surcharge (Urgent Care only) / its correction | 2 (local clock by location zone; overnight band rate) | weekend/holiday make the whole day after-hours and mask the clock; Plus/Premier waiver zeroes everything |
| Good Faith Estimate (fee + surcharge) | 3 (member price, local clock, band) | sum of the two above |
| insured time-of-service collection | 3 (payer contract allowed, deductible stage, OOP cap); 6 only with a verified secondary coverage (COB terms) | an insured visit carries no other priced line, so it cannot host a 3-4 problem tree |
| late-cancel / no-show fee | n/a | courtesy count needs the patient's other visits (not computable) |
Draws need task0 = {6,5,5,4} on ONE visit (value_input edges only flow inside a visit) and task1 =
{6,4,4}. Ceiling on one visit is about {3,2,2,1}. Reaching the draw requires inventing 9-13 Larkspur
tariff items (clinician-type prices, rebooking charges, cash-pay rates ...) per task, i.e. X1/X5
realism failures. Ruling requested from the coordinator: (a) waive the per-computation floor for this
difficulty to the realistic ceiling, or (b) accept invented tariff items.
Artifacts so far: visit.extended.yaml (base section verbatim, extended_policies empty), plan.md,
task_tools.py (issue_good_faith_estimate_d8f09896; TASK TOOL CONTRACT OK).

## Round 3 — coordinator ruling (AMENDMENT 1) applied; re-check against the frozen visit.yaml and the gates
- Ruling read in full: (a) refused, invented tariffs refused, fill order R1-R5 levers -> richer write -> minimal R6.
- Premise check: the ruling assumes XSUM/XCOUNT over visit_charges / visit_estimates aggregate across all of the
  patient's visits. check_extended.py rejects it: line 283 `elif oc == cat:` -> "references the primary category
  (cross_category must be OTHER categories)" (also line 480 for cross_category). check_compute.py would evaluate it
  (its `cross` map holds every product), so the block is in check_extended only. Without it, courtesy waivers,
  included-visit and sponsor plan-year counters remain uncomputable, so the late-cancel/no-show settlement and the
  counter-decided path steps the ruling lists cannot be priced.
- Path-order levers (sponsor window, plan covers type, membership standing, tier price) select ONE path; in any
  single world only the levers of the decisive path bear weight (T1); the others sit on their fall-through.
- Re-counted ceiling on one visit with every R1-R5 lever of the frozen charter plus the two R6 items that meet all
  six conditions (local-time clock keyed on patient_location_state; overnight band keyed on the local start):
  GFE 4, after-hours surcharge 3, fee correction 2, surcharge correction 1-2; insured cost share 6 only with a
  verified secondary coverage, and an insured visit carries no other priced line. Task 0 needs {6,5,5,4} on one
  visit (value_input), task 1 needs {6,4,4}: 9-13 further R6 slots per task, which no recorded field supports
  without X1/X2/X5 items.
- Decision recorded: no further invented factors; report the concrete gate-level blocker with the one-line
  unblock (allow X* over the primary category's EVENT tables in check_extended, as the ruling already assumes).
