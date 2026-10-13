# rental_reimbursement_claims — instantiation worklog (category: rental, M=2)

## Step 0 — difficulty pre-check
- Base read: products/rental.yaml (7 base policies), db_schema rental_coverages / rental_ledger, share_tools finders
  (find_rental_ledger searches by option/customer/entry; claim scoping is done by the agent on claim_number).
- Writable events: rental_coverage_add / rental_option_change / rental_coverage_remove are NOT used: each declares an
  unconditional trigger into auto:auto_coverage_change (cross-category write). liability_transfer / authorization_closed
  carry only date results (the DSL has no date arithmetic) and are not claimed.
- Claimed events: rental_authorization, rental_extension, rental_vendor_payment, rental_reimbursement_payment (split by
  vendor subtype: rideshare_taxi_transit vs other_agency), rental_payment_recovery (vendor_credit).
- The DB holds no invoice/receipt intake table: amounts are computed from authorization rows (start, authorized days,
  recorded daily rate, closed end date) and payment rows; invoice/receipt identifiers and their day counts come from the
  customer's own paper (persona, verbatim).

Draw (scripts/draw_counts.py --tasks 2):
- task 0: prerequisite_problems=3, factor_counts=[4,4,5,5]
- task 1: prerequisite_problems=1, factor_counts=[4,5]

## Space budget
- task 0 claims: rental_ext_extension_day_room (root, 4 factors), rental_ext_upgrade_acceptance_days (user, 5),
  rental_ext_partner_invoice_settlement (5), rental_ext_rideshare_day_allowance (user, 4).
- task 1 claims (reserved headroom, independent): rental_ext_own_rental_reimbursement (user root, 5),
  rental_ext_overbilling_credit (4).
- Tools (uuid8 drawn one by one): extend_rental_authorization_97458fea, accept_upgraded_rental_aa4639f2,
  pay_partner_rental_invoice_bf34992c, submit_rideshare_receipts_3a988a26, submit_own_rental_receipts_258c32b3,
  record_agency_overbilling_credit_d02c6cb6.

## Design notes (min-structure)
- Day results are min(increment, days left[, affordable days]); to make every factor bear weight the factors of the
  extension act only on the day-room side (cap allowance, partner days counted, rideshare weight, comeback tow-in days)
  and the world is laid so the day room binds below the increment.
- The upgrade acceptance (authorization of the running comeback rental) carries no payment read (base first-authorization
  day cap is declared overwritten; the day maximum is applied when the rental is extended), so it commutes with the two
  payments that are its siblings under the extension.

(Per-task cards, runs and gate outputs live in each task's design_rationale; this file logs the sequence.)

## Task 0 — closed
- Tree: rental_ext_extension_day_room <- {rental_ext_upgrade_acceptance_days (user), rental_ext_partner_invoice_settlement,
  rental_ext_rideshare_day_allowance (user)}; 3 value_input edges, state form, both sentence directions used.
- Gold values (harness, handling time): agency payment 724.46, rideshare 52.00, acceptance 6 (returns RA-EF22EC48),
  extension 3. Skip runs: extension 0 / 5 / 5 without acceptance / payment / rideshare.
- Revisions: r1 invoice once-only gate restated through a declared overwrite (a new invoice number has no pre-action
  system row to correlate); r2 per-factor evidence: recalibration conversion reads its own shop binding, the
  rideshare allowance owns the authorized-days read, the comeback test of the acceptance counts closed rentals (COUNT)
  and the rideshare end test counts car authorizations entered on the closing day (COUNT), so history bears weight.
- Per-task gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK.

## Task 1 — closed
- Tree: rental_ext_own_rental_reimbursement (user root) <- rental_ext_overbilling_credit (value_input, state form,
  negated direction). Gold: credit 455.86, reimbursement 205.50 (145.00 if the credit is skipped).
- Revision: the generator's tool-name constant was shadowed by the tracing dict (charter_scope became a dict) — fixed
  by importing the tracing module under its own name; all gates re-run.
- Per-task gates (--task 1): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK.

## Difficulty closing
- Union of scopes = all 6 extended policies; scopes and tools pairwise disjoint; every task calls a user tool.
- Final run: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (branches mean 54.00, steps mean
  15.50, history_rows_max 46, branches_max 71), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
- check_traceability not run: the KB is not yet published.
- Temporary authoring scripts (_authoring/) removed after the final run.

## Rework round 2 (audits/policy_task/rental_reimbursement_claims: _difficulty.md, 0.md, 1.md)
- F1 upgrade double statement: default now only 'Under the standard method ...'; declared override replaced_by is the
  factor total ('The authorized days are the repair days plus the package days ...').
- F2 'closed' vs end_date: rideshare and own-rental last-day tiers reworded to 'entered on the end date of the ...
  closing' (compute unchanged: closing end_date).
- F3 mislabelled method: recalibration_shop_conversion replaced by recalibration_scheduling (larger-of / sublet
  sequential sum plus transfer day / sequential sum).
- F4 tow-mileage factors removed from upgrade and extension; task 0's 2026-09-14 tow row removed, calls remaining 4.
- F5 package share of agency rates removed from partner invoice and credit.
- F6 dead tier: invoiced_covered_days removed; closing allowance by close reason (base end rules) added to partner
  invoice, extension (agency days counted) and credit.
- F7 own rental: TE set-off removed (and its physdmg_payments seed row, which contradicted physdmg's own rule); first-day
  tier 2 is now the base theft waiting period.
- New factors to meet the draw: rideshare package top-up; extension package day-room addition and agency rental closing
  allowance; credit closing allowance and owed rate convention.
- World/persona: task 0 invoice 24 days (car dropped back 2026-09-11), persona closes only after the extension is
  confirmed recorded; task 1 payment 24 days / 1412.40, physdmg payments removed, consent line without 'first'.
- New gold: task 0 = 779.22 / 57.00 / 5 / 3 (extension skip runs 0, 5, 5); task 1 = credit 552.00, reimbursement 235.50
  (87.60 without the credit).
- Observations kept as-is (not reds): E2/E3 prerequisite realism, per-day rideshare allowance, unilateral credit record.

## Rework round 3 (revision_2 audit: only N1 open; task 1 PASS untouched)
- N1: partner-invoice rule's flat covered-days sentence (cap at authorized days) moved under 'Under the standard
  method', both in rule and baseline.rule; the closing-allowance cap sentence now states it applies 'in place of the
  standard cap at the authorized days'. compute, factors, values, worlds and personas unchanged; task 0 rationale and
  step-11 tracing annotated.
