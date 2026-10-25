# plan.md — contents_packout_and_storage (env_0079), M=2

Draws (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=2 (3 problems), factor_counts [4, 6, 6]
- task 1: prerequisite_problems=3 (4 problems), factor_counts [6, 6, 6, 6]

## Charter constraints found at Step 0 (drive the whole design)
- Only three contents writes are the customer's own: contents_authorization (by:user, no computable number:
  declared_value is the customer's election), disposal-authorization signing (item_count is the presented list,
  not computable from records) and the customer's own payment (F1 b). => the owner=user problem of each task is a
  customer payment through the secure payment channel.
- The DSL has no date arithmetic producing dates and no range filters (exact-match only), so no computed date
  (return_scheduled_date / payment_due_date) can be a scored parameter, and windows over storage periods must be
  expressed by exact keys (bill_to, charge_code) or by DAYS() on recorded dates.
- Billable work must be evidenced by a record of performance: storage periods (custody_start_date), pack-back work
  (returned_date), late fees (invoiced). Cleaning / disposal hauls have no performance record -> not used as owed writes.
- Every contents event has triggers: [] -> no task tool write lands in another category (XF D7).
- Account charter binds no contents pricing (SLA credit / service-call waiver are water/fire only) -> E9 nothing to stack.

## Task 0 — "the carrier stopped paying storage; I want to pay my storage" (in custody, Direction to Pay)
Surface goal: insured homeowner, Full Contents Packout, contents in storage after a sewer-backup (Category 3) loss;
the carrier's approved storage end date has passed; she wants to pay what she now owes for storage.
Tree (fan-out, root = customer payment):
  C0 root  contents_ext_storage_settlement   (owner=user payment)          factors 4
  A0       contents_ext_customer_vault_period (vault line, begun customer-billed period, state_due)   factors 6
  B0       contents_ext_customer_valuation_period (declared-value line for that period, state_due)  factors 6
Edges: C0 <- A0 value_input (state form: every storage period begun carries its vault line);
       C0 <- B0 value_input (state form: every storage period begun on a declared-value job carries its coverage line).
Why false at opening: period beginning 2026-10-21 carries no lines.

## Task 1 — "my things came home; I want to pay off the contents job" (returned, Homeowner Direct Pay)
Surface goal: insured homeowner (carrier pays the insured; insured pays the company in full), High-Value or Full
packout returned a few days ago after the rebuild finished; pack-back lines not yet billed; she wants to pay off.
Tree (fan-out with one chain):
  D1 root  contents_ext_return_settlement   (owner=user payment)   factors 6
  A1       contents_ext_pack_back_boxes     (pack_back_box line)   factors 6
  B1       contents_ext_furniture_reset     (furniture_reset line) factors 6
  C1       contents_ext_return_trips        (truck_trip line for the return loads) factors 6
Edges: D1 <- A1, D1 <- B1, D1 <- C1 (value_input via the balance); C1 <- A1 (value_input: loads read the boxes
returned as booked) is optional — decide at authoring.

## Factor plan (sketch; finalized in the yaml and the worklog tables)
- A0 vault line: vault count billed (method: recorded / consolidated after a hauled disposal / capacity count),
  contaminated-loss sealed-vault handling (parameter, water job category — cross-difficulty), climate requirement
  (parameter), carrier-approval straddle (method), oversized..., program pricing (parameter, claims).
- B0 valuation: covered value basis (method), coverage rate by tier/coverage (parameter), ...
- C0 payment: customer-billed storage and valuation standing unpaid (baseline measure) with insured-only proceeds
  (parameter, claims, multi-source), extension hold (method, claims requests), ...
- A1/B1/C1 pack-back: boxes returned basis (method), unpack/high-value handling (parameter), property access
  (rebuild property_type, cross), loads per truck (method), ...
- D1 payment: balance due with depreciation hold (method, claims approvals/requests), ...
Thin-charter note: customer-payment computations have few record-backed levers in this charter; candidates for a
BLUEPRINT-KNOWN note are recorded in the worklog as they arise.
