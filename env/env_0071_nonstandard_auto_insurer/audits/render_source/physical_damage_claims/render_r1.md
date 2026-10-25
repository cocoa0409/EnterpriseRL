# render_r1 — physdam (physical_damage_claims): STOPPED on source scan, no doc written

Gate: `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN` (present).
Source: tasks/physical_damage_claims/physdam.extended.yaml + task_tools.py. The DSL semantics cited below were checked against skills/erl-task-instantiate/scripts/check_compute.py: XLATEST is scoped to the customer and filtered only by its keyword filters; DAYS(a, b) is signed, b minus a.

## F1 — physdam_ext_lienholder_settlement / factor recent_purchase: prior-term decoy row (XF8, XF11, XF12)

Rule sentence:
> A recent-purchase cap limits the vehicle value paid to a loss payee by the vehicle's acquisition date recorded on the owner term's vehicle change for the coverage's VIN, counted in calendar days from that acquisition date to the date of loss (the date of loss counted, the acquisition date not): held fewer than the recent-purchase days, the cap is the coverage's value at binding; held at least the recent-purchase days but fewer than the second-window days, the cap is the value at binding times the second-window cap factor; held longer, or no acquisition date recorded, no cap.

Compute line:
> acquired_on: "XLATEST('auto', 'auto_policy_changes', 'vehicle_acquired_date', date_field='change_effective_date', event_type='auto_vehicle_added', vehicle_vin=F('vehicle_vin'))"

Mismatch: the rule reads only the owner term's vehicle change. The compute reads every term the customer holds, filtering only by VIN, because no `auto_policy_id=F('auto_policy_id')` filter is applied. Compare `sr_vehicle_added_on` in physdam_ext_totaled_coverage_return, which does scope to the owner term. In the auto charter, `auto_renewal_issued` carries the vehicles over (`vehicle_count: vehicles carried over`, `triggers: []`), so a renewal term has no `auto_vehicle_added` row for a vehicle it carried over.

Reachable world: a renewal-term coverage (term_number 2 or more), with the vehicle added and acquired on the prior term, and a date of loss fewer than 365 days after acquisition. Under the rule, no acquisition date is recorded on the owner term, so there is no cap. The compute caps the value at the value at binding (or that value times 1.10) from the prior term's row.

## F2 — physdam_ext_deductible_refund / factor rental_part_measure: negative lag not floored (XF8, XF11)

Rule sentence (second branch):
> when no benefit has been paid but a rental was authorised on the claim, the authorised daily rate times the rental days from the authorised start date to the end of the rental, the start date counted and the end not;

and
> the rental ends on the claim's latest closing entry when that closing is dated on or after that authorisation's entry date, and otherwise runs to today, since a closing dated before it belongs to an earlier authorisation.

Compute lines:
> rental_end: "rental_closed_on if (rental_closed_on != None and rental_auth_entry != None and DAYS(rental_auth_entry, rental_closed_on) >= 0) else NOW"
> rental_part: "(rental_paid - rental_reversed + (rental_auth_rate * MX(0, DAYS(rental_paid_through, rental_end) - 1) if (rental_auth_rate != None and rental_paid_through != None) else 0)) if rental_paid > 0 else ((rental_auth_rate * DAYS(rental_auth_start, rental_end)) if rental_auth_rate != None else 0)"

Mismatch: the second branch has no floor, unlike the first branch's `MX(0, ...)`. When the authorised start date is after the end of the rental, DAYS(rental_auth_start, rental_end) is negative and the rental part becomes negative. Two cases produce this:
- no closing, and the start date is after today;
- a closing dated on or after the authorisation's entry date but before the start date.

The rule's words ("the rental days from the authorised start date to the end") give zero days. A negative rental part lowers `refund_damages`, which raises the refund, or zeroes it through `0 if refund_damages <= 0`.

Reachable world: the rental charter sets the start date as `date_the_vehicle_is_left_at_the_repair_facility_or_the_date_of_loss_when_not_drivable` (non_theft_start_rule), which can come after the authorisation entry. A closing can be recorded before the rental starts (close_reason `customer_declined`).

## F3 — physdam_ext_totaled_coverage_return / factor short_rate_share: later-dated decoy and an unstated window boundary (XF8)

Rule sentence:
> The share kept from the coverage return replaces the owner package's short-rate retention percent as follows: when the latest claim records a total loss declaration, nothing is kept; when it does not and a vehicle was added to the owner term within the owner package's replacement-vehicle reporting days before today (a vehicle substitution), the substitution short-rate percent; otherwise the owner package's short-rate retention percent.

Compute lines:
> sr_vehicle_added_on: "XLATEST('auto', 'auto_policy_changes', 'change_effective_date', date_field='change_effective_date', event_type='auto_vehicle_added', auto_policy_id=F('auto_policy_id'))"
> sr_added_days_ago: "DAYS(sr_vehicle_added_on, NOW) if sr_vehicle_added_on != None else -1"
> short_rate_pct: "0 if sr_decl_count > 0 else (K('substitution_short_rate') if (sr_decl_count == 0 and sr_added_days_ago >= 0 and sr_added_days_ago <= sr_window) else sr_package_pct)"

Mismatches:
- (a) The rule asks whether *a* vehicle was added within the window. The compute tests only the latest add by effective date. A vehicle-added change dated after today hides an earlier add that falls inside the window: the rule gives the substitution percent and the compute gives the package percent.
- (b) The rule does not state either boundary of "within N days before today". It does not say whether an add effective today (0 days, which the compute includes) counts, or whether an add exactly N days before today (which the compute includes, `<=`) counts.

## F4 — physdam_ext_totaled_coverage_return: assembly names factor-only quantities, and the combination of the two minimum-earned shares is never stated (XF1, XF2, XF3)

Rule sentences:
> A minimum-earned charge is taken off the coverage return, and at the standard it is the whole of the standard minimum-earned percent of the full-term rate.

> Each adjustment below changes the full-term rate, the return days, the share kept, the minimum-earned percent, the part of the minimum-earned charge kept or the renewal share of that charge, as it states, and the adjustments apply by kind: replacements first, the rate times the return days divided by the owner term's days less the share kept being then figured, then the amounts taken off, then the rounding and the floor at zero.

> The part of the minimum-earned charge kept from the coverage return follows how long the coverage has been in force, ...: at least the first minimum days but fewer than the second minimum days, half of it; the second minimum days or more, none of it; fewer than the first minimum days, the whole of it.

> The renewal share of the minimum-earned charge follows the tenure of the owner term the coverage belongs to, ...: on a renewal term whose term number is at least the long-renewal term number, none of it; on any other renewal term (term number two or more), half of it; otherwise (a new-business term), the whole of it.

Compute line:
> minimum_earned_charge: "return_rate * minimum_earned_pct / 100 * minimum_earned_share * minimum_earned_renewal_share"

Mismatch:
- "The part of the minimum-earned charge kept" and "the renewal share of that charge" are quantities that only factors use. The baseline does not define them ("the whole of the standard minimum-earned percent").
- The assembly names them but never says how the two shares combine. Each one is stated as a fraction ("half of it") of the same minimum-earned charge.
- The compute multiplies them, so a 90-to-179-day coverage on term 2 keeps one quarter. Reading each "half of it" as a share of the charge also supports keeping one half.
- In the rendered corpus the two shares sit in two independent factor documents, and the computation document must stay silent. No document can therefore state the product, and a solver holding both documents has two readings.

## Clean on this scan (no finding)

- physdam_ext_repair_assignment: rounding, floor, missing-date and negative-lag edges, and the enum coverage of cause, operator and garaging state all match the compute.
- physdam_ext_owner_tax_title: the tax base, title-clearing (payoff 0.00), late-days floor and title-fee floor all match the compute.
- Overwrite scopes of the two sibling pairs name each other (settlement deductible clause; total-loss settlement clause).
