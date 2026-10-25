# Render notes — fleet (fleet_invoicing extended charter)

Source: tasks/fleet_invoicing/fleet.extended.yaml + task_tools.py. Docs: docs/fleet/ (60 docs: 8 facet, 12 policy, 6 hub, 6 baseline, 28 factor). check_docs: DOCS OK.
Mechanical check run during render: every compute_basis quote, overwrite replaced_by, baseline.rule and prerequisite policy_source is verbatim in its rule (no misses).

## Source mismatches (reported, not rendered around)

1. **fleet_ext_early_pay_credit — retired clause restated as current (low/medium).** overwrite[1] retires from fleet_evt_payment
   "The discount is early_pay_discount_pct percent of the invoice amount, rounded half up to the cent", but the policy's own rule
   (first sentence) and baseline.rule still state "the discount is early_pay_discount_pct percent of the invoice amount, rounded half up
   to the cent." Rendered as-is: the base payment doc marks the clause "no longer in force"; the computation doc states the baseline
   (early-pay rate = program percent, discount base = invoice amount).
2. **fleet_ext_early_pay_credit overwrite[0] — replaced_by narrower than the retired clause (medium).** Retired: "The early-pay discount is
   credited on an invoice only when the remittance pays it in full." (every invoice). replaced_by speaks only of "the invoice the most recent
   remittance was applied to" and, unlike the other overwrites, does not say every other invoice stays under the base clause — so for an
   invoice paid by an earlier remittance no paid-in-full condition remains in force.
3. **fleet_ext_early_pay_credit channel points — undefined branch (low).** Rule: "0.25 when the remittance reference carries ACH or WIRE,
   minus 0.25 when it carries CHK, and none when it carries neither." A reference carrying both (e.g. ACH and CHK) is undefined; compute
   gives ACH/WIRE priority. Docs render only the three stated rows.
4. **fleet_ext_trip_fee_dispute vehicles_served — compute vs rule (low).** Rule: "the visit fee invoice itself not counted". Compute subtracts
   every mobile_service_call invoice dated that day from that store, not only the contested one; differs when a second visit fee invoice
   exists for the same day and store.
5. **Tire booking counts (low).** fleet_ext_trip_fee_dispute visit_tire_sets ("4 or more tire sets were booked for installation ... on the
   visit day") and fleet_ext_early_pay_credit tire_jobs_12m ("booked 6 or more tire installations") count tires_installation_booked rows;
   the tires charter says "a reschedule is a new row with the new slot", so a rescheduled set counts more than once, and a slot moved
   away from the visit day still counts.
6. **fleet_ext_month_end_late_charge windows (low).** Rule: "every invoice whose due date is before that day and less than twenty years
   old" and windows "before the month-end"; compute windows due_date (within 240 months, less invoices due today) and every 12-month /
   1-month window from today, not from the month-end. Equal only when today is the month-end.

## Assembly sentences that can only be stated by naming factor quantities (rendering decision, for the KB audit)

- early-pay: "the early-pay rate is the program's early_pay_discount_pct plus the remittance speed points, the tenure points, the tire
  program points, the invoiced volume points and the remittance channel points, all added together first"
- late charge: "The late-charge rate is adjusted, by adding the four adjustments together to the program's late_charge_monthly_pct, for
  credit utilization, closing-month remittances, invoiced volume and remittance record"
- tire / brake: "the make-good is the sum of a make-good line, a repeat-error credit, a road hazard program credit and a tire volume
  credit" / "... a make-good line, a brake volume credit, a tenure credit and a standing credit."
- trip fee: "The fee owed is the schedule part plus the weekend surcharge less the tire installation credit, the route credit and the fleet
  size credit, never below 0.00"
- over-limit: "The authorized amount is the account's ticket approval limit plus the driver's emergency authorization" (safety + weekend)

Not rendered as one sentence anywhere (it would be a factor inventory). The computation doc defines the named quantity at its baseline
value (rate = program percent; correction = restored discount; fee owed = program fee, never below 0.00; authorized amount = account
approval limit); each factor doc states its own contribution (points/adjustment added to the rate; credit added to the correction before
the ceiling, rounded once; credit taken off the fee owed with the 0.00 floor applied once to the fee owed as a whole; allowance added to
the authorized amount; deductible taken off the unapproved part before the single rounding). All contributions are additive, so the sum
semantics are preserved.

## Overwrite rendering (convention, no defect)

The over-limit, trip-fee, tire and brake overwrites are scoped self-naming replaced_by texts ("every other ... remains under the base
rule"). The base docs mark each clause "no longer in force as an unqualified rule" and carry the current basis, including that every
other ticket / visit / pricing correction stays under the base clause. The early-pay and late-charge base docs mark their clauses
"no longer in force" and point to the current basis without restating its figures.

## round 2

Gate: `tail -1 audits/policy_task/fleet_invoicing/_difficulty.md` = `VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN`.
Source re-read: fleet.extended.yaml sha256 a96c1a6f…111f, task_tools.py sha256 96262107…1e09. Base policies, parameter_schema and variants unchanged; the round-1 base renders stand.

Items closed:
- KB audit N1 (umbrella wording on base surfaces). The posting rules §5/§8, the credit-memo current basis and the payment current basis now carry the new replaced_by texts. The text "driver's emergency authorization", "visit fee schedule" and "billing make-good" no longer appears in the corpus. The trip-fee hub carries the new docstring ("contests part of the amount charged").
- KB audit N3 / round-1 note 6. The late-charge hub carries the three new prerequisite sentences verbatim. The computation doc carries the new baseline ("every date test … counts from the day the charge is assessed", "240 whole months"). The four adjustment docs and the seasoning doc now read "before the day the charge is assessed".
- Round-1 note 2. The payment base doc's current basis adds "every other invoice remains under the clause above".
- Round-1 note 3. The channel-points doc renders the new three-row ladder, with an ACH-and-CHK reading row.
- Round-1 note 4. The vehicles-served definition now reads "other than mobile service visit fee invoices".
- Round-1 note 5. Factors were replaced:
  - `tire_program_bookings` became `tire_care_rotation_points` (new doc `tire_care_rotation_points_*`; the old booking doc was removed).
  - `visit_tire_install_credit` became `visit_tire_work_credit` (new doc `mobile_visit_tire_work_credit_*`; the old doc was removed).
- Round-1 note 1 (retired clause restated) remains by design: the baseline names the early-pay rate and the discount base.
- Tire/brake factor docs now use the source's "make-good amounts are added to the correction". The hubs carry "credits what this rule works out for the billing error, never less than …". The trip-fee start-amount doc uses "the fee owed starts from".
- Safety and weekend allowance docs use the new reasons ("let a driver authorize safety work alone"; "the fleet desk … closed on weekends").
- Example hygiene. These hypothetical figures were changed:
  - the safety illustration limit, 750.00 (a live account figure);
  - the weekend-surcharge illustration, 30.00 (task fee owed);
  - the seasoning example, 900.00;
  - the late-charge worked figure, 30.00;
  - the visit-fee example, 30.00.
  No scored or intermediate task value now occurs in the corpus.

Remaining source mismatches (round 2):
1. **Tire and brake restore: "never less than" vs the ceiling (low).** Rule/replaced_by: "the pricing correction credits what this rule works out for the billing error, never less than the fleet discount the ticket should have carried less the discount the invoice already carried". The same rule says "it never exceeds the invoice amount less the credit memos and early-pay discounts already on the invoice". The compute result is `RND(MN(tr_credit_room, restored_discount + tire_makegood), 2)`, which is below the restored discount whenever the room is smaller. The two sentences conflict in that case. The brake rule has the same pattern.
2. **Early-pay `baseline.rule` is not a contiguous passage of the rule (informational).** The rule interposes the prerequisite sentence between "…every other invoice remains under the base rule." and "The discount is the early-pay rate…". The semantics are unchanged.
3. **Base-layer N2 (unchanged, base frozen).** fleet_evt_payment says "when remittance_advice_required is true a remittance that names no invoice is held unapplied", while `payment_application_order` is `oldest_invoice_first` on every program. Both are carried as written.

Gates: check_docs DOCS OK (60 docs: 8 facet, 12 policy, 6 hub, 6 baseline, 28 factor; 146 keys; 4 prerequisite edges). check_traceability: 0.json 19/0, 1.json 27/0, TRACEABILITY OK.
RENDER round 2: DOCS OK, TRACEABILITY OK

## round 3

Gate: `tail -1 audits/policy_task/fleet_invoicing/_difficulty.md` = `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN`.
Source: fleet.extended.yaml sha256 81713931…c4fc; task_tools.py unchanged (96262107…1e09).
Audit files read in full: policy_kb 0.md/1.md and runtime_context 0.md/1.md, revision_2. Every part is PASS, kb=CLEAN, and there is no KB item to close. C1 (tires corpus not yet published) is a cross-product conditional outside docs/fleet. N2 is a base-layer note.

Re-rendered for the round-4 source:
- Round-2 note 1 (floor and cap precedence).
  - Tire and brake correction hubs, and the credit-memo current basis: now carry the new replaced_by ("which is at least … except that it never exceeds the invoice amount less the credit memos and early-pay discounts already on the invoice, that limit prevailing").
  - The 8 make-good factor docs, under "Where the amount sits": now say the limit "is applied last, after every make-good amount, and prevails …, so a correction can fall below the restored discount only when that limit is lower; the correction is rounded half up to the cent once, after the limit".
- Round-2 note 2 (early-pay baseline not contiguous). The rule now places the prerequisite sentence after the baseline passages, so the baseline is contiguous. The computation doc and the hub already carry both texts, so no document changed.
- No other policy changed in substance. Mechanical check: every compute_basis quote, replaced_by, baseline.rule and policy_source is verbatim in its rule.

Remaining source mismatches (round 3): none found.
- Base-layer N2 is carried as written and unchanged: fleet_evt_payment "held unapplied" vs `payment_application_order` = oldest_invoice_first.

Gates: check_docs DOCS OK (60 docs; 146 keys; 4 prerequisite edges). check_traceability: 0.json 19/0, 1.json 27/0, TRACEABILITY OK.
RENDER round 3: DOCS OK, TRACEABILITY OK
