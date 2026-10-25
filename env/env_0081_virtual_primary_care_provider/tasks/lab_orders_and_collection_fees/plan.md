# plan — lab_orders_and_collection_fees (env_0081), M=2

## Draw (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[4, 6]
- task 1: prerequisite_problems=1, factor_counts=[6, 5]

## Hard facts established from the blueprint (lab.yaml, db_schema, share_tools)
- Lab writes: lab_orders updates (collection_method, payment_path(+membership_id/enrollment_id/coverage_id),
  requisition_expiry_date+reissue_count, status/cancelled_date), lab_charges rows (lab_panel_charged,
  lab_collection_fee_charged, lab_charge_refunded). Only lab_ordered has a trigger (-> lab:lab_panel_charged, same
  category). D4 is clean: no lab event triggers another category.
- refund_reason enum has NO value for a collection-method change (none, cancelled_before_collection, expired_unused,
  lab_side_rejection, path_changed, billing_error) although lab_evt_collection_fees refunds the old method's fee on a
  change -> BLUEPRINT-KNOWN gap; route around inside my own policies (record in worklog).
- DSL: no subscripts (tier mappings cannot be indexed -> member prices restated as this policy's params keyed by
  tier family), no date arithmetic (computed params are amounts), evidence functions required in every factor's
  bindings (SUM/COUNT/MAX/LATEST/EXISTS/CPARAM/CFIELD/MONTHS/DAYS/X*), eq-only filters.
- verify_patient_identity: >= 2 of patient_number/date_of_birth/phone/email/home_zip.
- owner=user acts allowed (owner_ruling): choosing the collection method; choosing insurance vs paying directly;
  a personal payment (card read out / secure link) with visible necessity.
- Membership Plus Annual 299.00/yr (no trial, no enrollment fee); Plus Annual visit benefits: Annual Preventive
  Video Visit included 1/yr, Urgent Care included 6/yr, Primary Care Follow-Up member price 49.00 (GFE needed on
  member_rate when scheduled >= 3 business days ahead -> book within 2 business days).

## Identifier band
phones 6175550160-6175550179; patient numbers LH-8440000-LH-8440999; surnames Brightwater, Achterberg, Mensah,
Calloway, Zielinski, Fontaine; employers Halverson Tool & Die, Copperline Software; ref prefix 84; house 4400-4499.

## Working rules (coordinator)
- Persist piece by piece; scratch in /tmp/lab_orders_and_collection_fees_0081/; never stage whole files.
- Worklog tables required: defining-sentence, transitive factor-reads, A6 all-pairs tiers, A7 T1/T2, B2 probes,
  B1 edges, D4 events/triggers, B5 compute_basis verbatim sweep.
- Final: 7 gates green, then append `ROUND 1: gates 7/7 green` as the last worklog line.

## Status
- [x] design (trees, factors) -> worklog.md
- [x] task 0 policies -> yaml, tools, seed, persona, GT, gates
- [x] task 1 policies -> yaml, tools, seed, persona, GT, gates
- [x] final gates, worklog tail line
