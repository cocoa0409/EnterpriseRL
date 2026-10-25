# Render source notes — tires (env_0062, tire_treadwear_warranty)

Source: tasks/tire_treadwear_warranty/tires.extended.yaml + task_tools.py (extended profile).
Base text carried verbatim; none of the items below was "fixed" in the docs. Each is reported for the coordinator.

## 1. Assembly / ordering sentences that name several factor quantities

The computation document must stay silent about factors, and no factor document may name another factor, so these
sentences have no single legal home. In the KB each factor document states only how its own quantity enters the
result (its own part of the sentence). The full sentences are not carried word for word.

- tires_ext_treadwear_credit (overwrite replaced_by + rule): "For a treadwear adjustment credit this policy computes, the
  covered-mileage percentage is the commercial-use share plus the care-package points plus the rotation-record points
  plus the even-wear points." (commercial_use_share, care_package_points, rotation_record_points, even_wear_points)
- tires_ext_ticket_redemption (overwrite replaced_by + rule): "the balance is the tire line less the credit applied, plus
  the mounting line times the fleet labor rate and the member labor rate each taken as a percentage, plus the road
  hazard line, plus tire_disposal_fee_per_tire, rounded half up to the cent and figured before tax" (tire_line_basis,
  replacement_mounting_line, fleet_labor_rate, member_labor_rate, road_hazard_line)
- tires_ext_lapsed_order_refund (overwrite replaced_by): "the lapsed-order refund is the tire price paid less the
  restocking fee, the storage charge and the missed-slot charge"; and the ordering sentence "The order is fixed: the
  restocking rate acts on the tire price paid, the fleet share then acts on that restocking fee, and the restocking
  fee, the storage charge and the missed-slot charge are each taken off the tire price paid once" (restocking_rate_by_bookings,
  fleet_restocking_share, missed_slot_charge, plus storage factors behind "the storage charge")
- tires_ext_workmanship_share (overwrite replaced_by + rule): "the workmanship share percentage is the prorated share
  times the defect-class rate divided by 100, less the maintained-set discount and the alignment-maintained discount
  taken off together once; ... the replacement mounting part set by the road hazard certificate on the set is added";
  and "The order is fixed: the prorated share is taken first, the defect-class rate then acts on it, the two discounts
  are added together and taken off that result once" (proration_basis_method, defect_class_rate,
  maintained_set_discount, alignment_maintained_discount, replacement_mounting_waiver). The KB states in each discount
  document that percentage discounts on the workmanship share percentage are added together and taken off once,
  without naming the other discount.
- tires_ext_trial_refund (overwrite replaced_by + rule): "the trial refund on the set's ticket is the tire price paid plus
  the refunded installation part, less the usage charge, the bundle recapture and the truck-size restocking fee"
  (refunded_installation_part, trial_usage_charge, alignment_bundle_recapture, truck_size_restock)

## 2. Method factor reading other factors' outputs

- tires_ext_share_settlement, factor settlement_order_method: its methods are stated over "the settleable part" and
  "the apportioning base" ("the share settlement being the credit remaining times the settleable part divided by the
  settleable part plus the apportioning base, never above the settleable part"), and those quantities embed the
  outputs of share_mounting_part (settleable), apportioning_price_basis and apportioning_mounting (apportion_base).

## 3. Overwrites that retire a clause still in force (replaced_by scoped "only for such ..." while the base clause is retired whole)

- tires_evt_treadwear_adjustment, retired "miles_driven is the inspection odometer minus install_odometer." — replaced_by
  covers only this policy's credit and says "an adjustment resting on an older inspection is not worked out under this
  policy"; such an adjustment is left with no miles basis.
- tires_evt_treadwear_adjustment, retired "The credit amount is credit_pct percent of the per-tire price named by
  proration_price_basis ..." — replaced_by: "every other per-tire price named by proration_price_basis remains under the
  base rule", i.e. the retired clause is declared still in force for other cases.
- tires_commercial_use_coverage, retired "Commercial use is read from tires_msr_commercial_use: ..." — replaced_by:
  "every other use of commercial use remains under the base rule" (retired clause still in force). The replaced_by also
  drops vehicles whose usage_class is commercial.
- tires_commercial_use_coverage, retired "Under commercial use the effective warranted miles ... though workmanship
  replacement still applies." — replaced_by drops the still-in-force "though workmanship replacement still applies".
- tires_purchase_ticket, retired ticket-total clause (by both tires_ext_ticket_redemption and
  tires_ext_lapsed_order_refund) — both replaced_by texts say "every other ticket total remains under the base rule",
  so the ordinary purchase-ticket total is retired yet declared in force.
- tires_evt_order_cancellation, retired refund clause — replaced_by: "every customer-requested cancellation remains
  under the base rule".
- tires_evt_credit_redemption, retired "The amount applied may not exceed tires_msr_credit_remaining ..." (by both
  tires_ext_share_settlement and tires_ext_ticket_redemption) — each replaced_by covers only its own case ("every credit
  applied toward a replacement ticket / workmanship share is settled under its own rule"); a credit applied to a
  replacement ticket that is not the one-tire ticket of tires_ext_ticket_redemption is left with no cap / tire-price-only basis.
- tires_evt_workmanship_replacement, retired "Once either limit is passed the customer pays the tread_worn_share ..." —
  replaced_by: "every other workmanship charge remains under the base rule".
- tires_evt_satisfaction_trial, retired "The return is the customer's own decision ... the agent registers the request
  and the customer confirms it ..." — replaced_by: "every other return request remains under the base rule".

In the KB every retired clause is carried in its base document marked "no longer in force"; the replaced_by texts
(scope sentences included) are carried in the extended documents as written.

## 4. Undefined branches (rule silent, compute decides)

- tires_ext_treadwear_credit, commercial-use share: the rule's first branch reads "a vehicle enrolled for at least half
  of the set's active-life months takes commercial_use_mileage_pct" (no one-month floor) and the last branch is "a
  vehicle never enrolled during the set's active life keeps 100"; a vehicle enrolled during the active life for less
  than one whole month is covered by neither (compute: roster_months >= 1 required, else 100). The ladder text
  ("for at least one month and for at least half") was rendered.
- tires_ext_trial_refund: "the miles run are the odometer of the set's latest tread inspection entry minus
  install_odometer" — a set with no tread inspection entry is undefined in the rule (compute: miles_run 0).
- tires_ext_workmanship_share: the defect entry is chosen "among the set's inspection entries carrying a defect"; the
  compute falls to out_of_round when no tread separation, belt shift or bead leak entry exists, whether or not an
  out-of-round entry exists.

## 5. Docstring

- confirm_trial_return_33503dcd: "a refund entry to the Crestline credit card is the entry the card account's
  merchandise credit is posted from" — the tool body books only the tire refund entries; any card posting relies on the
  event trigger, not on the tool body. Rendered only as the docstring states it (the entry is the posting source).

## round 2 (source revision_6, charter=CLEAN; yaml sha256 7e1f6204…, task_tools.py 47bb83c0…)

Classes 1–5 above are closed by the rework (each assembly sentence now names only "every point addition / relief /
charge this policy states, each worked out on its own"; every overwrite's replaced_by restates the full base clause plus a
scoped extension; the undefined branches are now defined in the rule; the confirm_trial_return docstring now says the call
writes nothing on any card account). Remaining notes, none blocking:

- Generic assembly sentences have no single legal home. A computation document must say nothing about factors, a hub
  may not hint at components, and a factor may not describe another factor. Where the sentence sits in an overwrite's
  replaced_by, it is carried in that base clause's retirement note (base docs for commercial use coverage, purchase
  ticket, order cancellation, workmanship replacement and satisfaction trial). The share-settlement rule sentence "the
  settleable part is the share owed less the part of it this policy holds back from settlement, never below 0, and the
  apportioning base is the apportioning tire line plus the replacement ticket's mounting charge less every relief on
  that mounting this policy states, each worked out on its own, the mounting never below 0" is not an overwrite. It is
  carried split up: the road hazard factor states that its mounting part is held back, and each relief factor states
  that it is worked out on its own and that the mounting less its reliefs is never below 0. The sentence is not carried
  verbatim anywhere.
- The tires_evt_credit_redemption replaced_by texts (from share settlement and ticket redemption) each state the other
  policy's rule ("a credit applied toward a workmanship share ... settles only the tire part ..."). Those cross parts are
  carried once, in the base adjustment-credit doc's retirement note, not in either extended policy's docs.

RENDER round 1: DOCS OK, TRACEABILITY OK

## round 3 (KB rework round 2; source revision_7, yaml sha256 fde6faff…, task_tools.py 47bb83c0…)

Closed:
- KB-E3: removed "Days kept" from `trial_refund_amount`, the computation document. It is defined in each factor that
  uses it (`trial_refund_installation_part`, `trial_usage_charge`, `truck_size_trial_restocking`). Covers follow
  revision 7: days_kept goes to refunded_installation_part, usage_days to trial_usage_charge.
- Same class, workmanship share: the revision-7 baseline drops "miles run". Removed it from `workmanship_share_amount`.
  The miles-run definition is now in `defective_tire_proration_basis` (def_odo, miles_run); `maintained_set_discount`
  already defined it (maint_odo, maint_miles).
- KB-E1 / KB-E2: removed "as the replacement ticket figures its tire line" (`apportioning_tire_line`) and "as the
  workmanship replacement was charged" (`share_mounting_part_road_hazard`); both phrases are gone from the rev-7 rule too.
- Revision-7 binding moves carried in covers. Ticket redemption: recorded_price goes to road_hazard_line,
  line_fleet_discount to tire_line_basis. Lapsed order refund: bookings goes to missed_slot_charge, and the unused
  days_past_hold binding is gone (the baseline sentence defining days past hold is still carried, because the
  whole-weeks storage charge uses it).
- Checked the other computation documents for quantities used only by factors: none found.
- N2 naming: the line card column now reads "New-tire (original) tread depth" and adds "A line's new-tire tread depth is
  its original tread depth" (from the field's own label). The storage-surcharge and truck-size restocking documents use
  the same term.
No new source mismatch found.

RENDER round 2: DOCS OK, TRACEABILITY OK
