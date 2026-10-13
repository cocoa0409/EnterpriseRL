# Policy-task audit: rental_reimbursement_claims / charter-global

## charter_global_frozen

- Frozen: 2026-10-05T10:55Z (before any task's GT was revealed). Auditor: independent erl-task-policy-audit agent (not the author).
- Frozen inputs (sha256 checked against the conductor's MANIFEST and the files in the repo; all identical):
  - `cdcfb2cb0257d3d8bcb5cf5d27a2576a111a0dcc043210f449d094c959fb0e2c  rental.extended.yaml`
  - `c2cd95ca79abc28e3df6517d7c58849d0a3013aae5a7a68b036b81fc9f0c6402  task_tools.py`
  - `fa5067cfacf61047cc3b0574d6d5eb73fef2ebd9e887a9473e0ff58f526b54f2  task_0.view.json`
  - `c816ad5959b1d35bf2ca5b21288362347811f88d374b9e4f776b3a8bef26db2a  task_1.view.json`
- Read: `blueprint/blueprint.yaml` (difficulty claim), `blueprint/products/{rental,auto,physdmg,roadside}.yaml` (targeted sections), `blueprint/db_schema.json`, `blueprint/share_tools.py`, the masked views in `/tmp/erl35_views/rental_reimbursement_claims/`. I also read the restricted-expression primitives (`DAYS`, `SUM`/`COUNT`/`LATEST`, `CPARAM`, `X*`) in `skills/erl-task-instantiate/scripts/check_compute.py` lines 225-395, only to fix the evaluation semantics. That file holds no GT. It sits outside the brief's listed read domain, so I am disclosing the read here.
- Masked and not opened: `tasks/rental_reimbursement_claims/tasks/*.json`, `tasks/rental_reimbursement_claims/worklog.md`, the scenario `worklog.md`, and all other audit directories.
- Entry conditions: the gate snapshot `/tmp/erl35_views/rental_reimbursement_claims/GATES.txt` lists EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO and SCOPE OK. check_traceability is deferred until the KB is published. The masked views and their hashes came with the brief. Entry conditions are met.
- Base copy: `rental.extended.yaml` lines 1-898 match `blueprint/products/rental.yaml` exactly (diff shows only a trailing blank line). The base copy is verbatim.

### policy_conflict_scan

| Extended policy | subject / target tool / computes | trigger | prerequisite |
| --- | --- | --- | --- |
| rental_ext_upgrade_acceptance_days | rental_authorization / accept_upgraded_rental_aa4639f2 (user) / authorized_days | on_request | [] |
| rental_ext_partner_invoice_settlement | rental_vendor_payment / pay_partner_rental_invoice_bf34992c (agent) / amount | state_due | [] |
| rental_ext_rideshare_day_allowance | rental_reimbursement_payment (rideshare) / submit_rideshare_receipts_3a988a26 (user) / amount | on_request | [] |
| rental_ext_extension_day_room | rental_extension / extend_rental_authorization_97458fea (agent) / authorized_days | on_request | upgrade, partner_invoice, rideshare (all value_input, state form) |
| rental_ext_overbilling_credit | rental_payment_recovery / record_agency_overbilling_credit_d02c6cb6 (agent) / amount | state_due | [] |
| rental_ext_own_rental_reimbursement | rental_reimbursement_payment (other_agency) / submit_own_rental_receipts_258c32b3 (user) / amount | on_request | overbilling_credit (value_input, state form) |

- Overlapping subjects:
  - rental_reimbursement_payment is claimed by both the rideshare and the own-rental policies. Their scopes are disjoint by vendor kind ("Rideshare, taxi and transit fares … during a rideshare authorization" against "A rental the customer arranged at an agency outside the partner network"), and each tool hard-codes its own `vendor_type`. No conflict.
  - rental_authorization: the extended policy covers only the customer-accepted larger class. Base `rental_evt_authorization` still governs standard authorizations, but no task tool writes those. No conflict.
- Cross-category read boundaries: physdmg (claim events, physdmg_payments), roadside (roadside_events), auto (package `rental_max_option_rank` through CPARAM). All are read-only, and none is written by this difficulty.
- Terminal states: every tool creates exactly one rental_ledger row. No status transitions.
- Scope partition (derived from the `prerequisite` graph, not from GT): task 0's tree has root extension_day_room and prerequisites upgrade_acceptance, partner_invoice and rideshare. Task 1's tree has root own_rental_reimbursement and prerequisite overbilling_credit. The two sets are pairwise disjoint and together cover all six extended policies.
- Observation (not a defect of the extended surface): the difficulty claim in `blueprint.yaml:122` lists rental_coverage_add, rental_option_change, rental_authorization_closed and rental_liability_transfer. No extended policy or task tool exercises those four event types.

### rule_compute_equivalence

I checked check 2 on all six policies sentence by sentence. Every compute binding has a `compute_basis` quotation that is a substring of the rule. Every `factors[].ladder` tier appears both in the rule prose and in the `decides` branch. The `baseline.rule` sentences are all inside the rule (verified with a normalized substring test), and every `overwrite.replaced_by` is inside the rule. Departures:

1. **"the day the … authorization closed" (rideshare `car_n`/`car_start`, own-rental `car_n`/`car_start`): the rule's word and the compute's field differ.** The rule's condition reads "when a rental car authorization on the claim was entered on the day the rideshare authorization closed" and "… entered on the day the customer-arranged rental closed". The base event `rental_authorization_closed` gives its two date fields different meanings: `end_date: Last covered rental day.` and `entry_date: Date closed.` (rental.extended.yaml lines 531-533). The compute binds the condition to `end_date` (`entry_date=r_end`, `entry_date=o_end`, where `r_end`/`o_end` are `end_date`). Elsewhere the same rules use a different phrase for `end_date`: "its closing end date" and "the end date of its closing". Read through the charter's own field meanings, "the day … closed" is `entry_date`, but the compute uses `end_date`. In both worlds the closing was entered the day after the end date, so the two readings choose different tiers (finding F2).
2. Rule "the vehicle came back to the shop on a roadside tow" (upgrade `tow_date`/`tow_miles`, extension likewise) is computed as the customer's latest tow on any roadside option, with no vehicle or claim filter. The rideshare `tow_moved`, `alt_on_report` and `alt_all` are likewise customer-wide. In both worlds only the damaged vehicle carries roadside, so there is no demonstrated consequence (observation).
3. Upgrade: the rule carries two unconditional statements of `authorized_days` (finding F1).
4. Partner invoice, rideshare, own rental and credit each open with an unconditional covered-days or owed-days sentence ("The covered days of a partner invoice are the closed span …", "The covered rideshare days run from the start date … through the end date of its closing", "The covered days of a customer-arranged rental run from its start date through the end date of its closing", "The days the agency should have been paid for are the payment's billed days"). A conditional ladder that restates the default as its "otherwise" tier refines each of them later. Read as general-then-exception, each has one reading. Recorded as an observation; the upgrade case is different (F1).

Otherwise compute invents no basis, and the rule makes no promise that compute fails to implement.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (6 tools, 6 policies).
- Tool bodies (task_tools.py) only `ctx.create` one rental_ledger row with the caller's figures. None of them reads the DB, validates, refuses or hints. The module docstring says so too ("never judges eligibility, prerequisites or amounts").
- No docstring names another tool or uses a sequencing word. The only matches for before/after/first/then are "1 for the first extension of that authorization, then 2, 3" (sequence-number format) and "from then on" (the life of the new authorization number).
- uuid8s 97458fea, aa4639f2, bf34992c, 3a988a26, d02c6cb6 and 258c32b3 share no prefix, show no run, and look independently generated.
- Fixed fields: accept writes `vendor_type=partner_direct_bill`, rideshare writes `rideshare_taxi_transit`, own rental writes `other_agency`, and credit writes `recovery_source=vendor_credit`. Each matches its policy's subject. PASS.

### prerequisite_graph

- All six policies fill in `prerequisite` (four are `[]`). Every `problem` names an extended policy in this file, none names itself or a base policy, and the graph is acyclic: extension depends on {upgrade, partner_invoice, rideshare}, own_rental depends on {overbilling_credit}, and nothing else.
- Every `policy_source` is a verbatim substring of its own policy's rule (verified mechanically). Every edge has `form: state` and no `fallback_reason`.
- `gate` names exist in compute: run_days, car_billed, ride_days_billed and benefit_left. `kind` is `value_input` on all four edges, and each gate is a compute input rather than an eligibility gate.
- `resolved_by` is in each case the depended-on policy's `target_tool`, and that tool's write produces the row the gate reads: rental_authorization, rental_vendor_payment, rental_reimbursement_payment with vendor_type rideshare, and rental_payment_recovery with source vendor_credit.
- `condition` matches the sentence's strength. There is a slight tightening on E2/E3 ("carrying its invoice's billed days" / "carrying its receipts' days and the amount"), but it is implied by any such row, so no change of scope.
- No authoring-viewpoint phrasing. PASS.

### prerequisite_sentences

| Edge | Sentence (in the blocked rule) | Connective | Waited-on state | The one write that produces it |
| --- | --- | --- | --- | --- |
| E1 extension → upgrade | "The days an extension adds are fixed only after the rental it extends stands on the rental ledger as an authorization under the claim." | only after | an authorization row for the rental being extended | rental_authorization is created only by accept_upgraded_rental_aa4639f2 in this difficulty |
| E2 extension → partner_invoice | "The days an extension adds are not settled until every closed partner direct-bill rental on the claim carries an agency payment on the rental ledger." | not … until | an agency payment on each closed partner rental | rental_vendor_payment is created only by pay_partner_rental_invoice_bf34992c |
| E3 extension → rideshare | "Before the days an extension adds are worked out, every closed rideshare, taxi or transit authorization on the claim must carry a reimbursement entry on the rental ledger." | before | a reimbursement entry on each closed rideshare authorization | two tools create rental_reimbursement_payment, but only the rideshare policy's scope ("fares a customer paid during a rideshare authorization") covers a rideshare authorization, and the own-rental policy's scope ("a rental the customer arranged at an agency outside the partner network") excludes it, so the reading is unique |
| E4 own_rental → credit | "A reimbursement for a rental the customer arranged is not made until every agency payment on the claim that billed a higher daily rate than its authorization recorded carries an agency credit entry against it." | not … until | an agency credit entry on each over-rate agency payment | rental_payment_recovery (vendor_credit) is created only by record_agency_overbilling_credit_d02c6cb6 |

- All four pass the four-point test: an explicit connective; a record-visible state in ledger words; no tool name, policy id, snake_case token or row id; and the scope matches `condition`.
- None of the depended-on rules restates the sentence. The rules carry no second wording.
- No rule states an order between problems beyond these edges. The upgrade rule's "the day maximum of the loss is applied when that rental is extended, not when it is recorded" places a cap and orders no writes.
- The base rule sentences found that order between problems (none bearing on these trees) ground no edge.

**Derivation (single reading).**
- E1: the extension rule's first sentence says it acts on "An open rental on an accepted claim". If the customer's running rental has no authorization row, "the claim's most recently entered authorization" would point at a closed one, which is not an open rental. The reader therefore needs an authorization for the running rental. The only policy whose write records an authorization is the upgrade policy, and it fits only when the car is above the option's direct-bill class.
- E2, E3 and E4: the reader scans the ledger for the named rows (a closed partner rental with no vendor payment, a closed rideshare authorization with no reimbursement, an agency payment whose `daily_rate` is above its authorization's rate with no vendor_credit recovery). The depended-on policy's own rule describes the write that creates that kind of row.

**Realism of the prerequisite settings (declared priority).**
- E1 (an extension needs an authorization on file to extend) and E4 (a self-arranged-rental reimbursement waits for the over-billed agency payment to be corrected so that the per-loss remainder is right) match how carriers run rental files.
- E2 and E3 do not. No carrier makes the extension of a running rental wait until an earlier agency invoice is paid. The day room is a count of days and can be read from the authorizations, whatever has been paid.
- No carrier makes the extension wait until the customer submits receipts for earlier rideshare fares either. Under base `rental_evt_payment` that submission is the customer's own optional request within a 60-day window. E3 therefore makes a running rental's extension depend on a reimbursement the customer may lawfully never request.
- Recorded as a realism observation. The skill's red classes for the problem tree (unmet at the opening, bearing weight, waiting, discoverability, hand-over, order) are each satisfied, and no relationship test fails on these two edges.

### override_declarations

I checked each extended policy sentence by sentence against its `base_policy_refs`.

- **upgrade_acceptance_days** (base refs: per_loss_benefit, evt_authorization, combo):
  - Inherited: claim reported and accepted, option active, start rules, direct-bill class with the customer paying the difference, notice before pickup, no rental after a liability transfer or once the maximums are used.
  - Declared: "The first authorization covers initial_authorization_days or the shop's estimated repair days if fewer, never more than the days left under max_days_per_loss" is superseded, and the `replaced_by` text says "The days an accepted larger-class rental is authorized for are initial_authorization_days, never fewer than one day". The rule then defines authorized days a second time as a sum. The declared merged semantics therefore do not equal the computed quantity (finding F1).
- **partner_invoice_settlement** (per_loss_benefit, evt_payment):
  - The three replaced sentences are declared: daily rate/covered days, payment formula, and the "paid only once" wording. The dedup rule is restated.
  - Inherited, not hit: never-paid items, everything not paid is the customer's, payment within vendor_invoice_payment_days, overbilling review threshold, rideshare/receipt sentences.
  - No undeclared override.
- **rideshare_day_allowance** (per_loss_benefit, evt_payment, combo):
  - Two sentences declared. The base sentence "reimbursed against itemized receipts under the same daily limit" is inherited. The allowances (45/35 or the daily limit) never exceed the daily limit, so it is followed.
  - receipts_in_time is restated. No undeclared override.
  - Realism observation: the amount is a per-day allowance with no reference to the fares actually on the receipts.
- **extension_day_room** (evt_extension_and_end):
  - Both replaced sentences declared, including the within_max_days eligibility, which is replaced by the comeback day maximum. End rules are inherited.
  - No undeclared override.
- **overbilling_credit** (evt_recovery), `overwrite: []`:
  - The base gives no credit formula. "lowers rental benefit paid and does give the credited amount back" is restated, and "recorded once per payment and source" is restated.
  - No conflict.
- **own_rental_reimbursement** (per_loss_benefit, evt_payment, combo):
  - Two sentences declared. "under the same daily limit" is followed (the topped-up amount is never above the daily_limit).
  - The combo base sentence "when the vehicle carries an option, the option pays and the built-in benefit does not apply" is followed through the set-off.
  - No undeclared override.

No anonymous intermediate, 0/1 multiplier or dropped branch found beyond F1.

### factor_ladders

Each row lists: factor (label, decides): tiers → values, fall-through = baseline?, cross-difficulty source, and any structural defect.

- **upgrade_acceptance_days** (5 declared: 4 parameter, 1 method):
  - repair_path_starting_days (parameter, start_days): Select comeback → 4, non-network comeback → 2, otherwise initial 7. Fall-through = baseline. physdmg. Multi-source (ledger + physdmg). Realism observation: comeback starting days are fewer than normal and depend on Select vs non-network, which is unusual but not demonstrably unreal.
  - recalibration_days_owed (parameter, calib_owed): supplement and latest estimate ≥2000 → 2, supplement and 1000-<2000 → 1, otherwise 0. physdmg. Observation: the estimate amount as a proxy for ADAS recalibration.
  - recalibration_shop_conversion (labelled **method**, calib_days): non-network → ×1.5 and round up, Select → ×0.5 and round up, otherwise taken as owed. All three tiers are the one formula `ceil(calib_owed × m)` with m ∈ {1.5, 0.5, 1} (calib_owed is an integer, so the round-up is idle at m = 1). This is a number substituted into the same formula, so the **label is dishonest** (F3).
  - comeback_tow_in_days_added (parameter, towin_add): comeback tow >10 mi → 2, ≤10 mi → 1, otherwise 0. roadside. **Unreal condition**: tow mileage decides rental days (F4).
  - package_rental_days (parameter, pkg_add): rank 6 → 2, rank 4-5 → 1, otherwise 0. auto.
  - Count after strikes: 3 parameter, **0 method** (F3, F4).
- **partner_invoice_settlement** (5 declared: 2 method, 3 parameter):
  - invoiced_covered_days (method, cover_days): span > authorized → authorized days; "the invoiced rental carries no closing on the ledger" → 0; otherwise span. The middle tier **cannot occur**: the rule defines the invoiced rental as "the claim's most recently closed rental" (compute `inv_auth` is taken from a `rental_authorization_closed` row), so every invoiced rental carries a closing. The condition separating tier 2 from the others holds for every customer who reaches this write, so only two tiers are live (F6).
  - partner_rate_convention (method, billable): ≥28 → monthly blocks 22/28, 7-27 → weekly blocks 6/7, otherwise day by day. Observation: arithmetically one block formula with (block, paid) ∈ {(28,22),(7,6),(1,1)}. Kept, because daily against weekly-rate pricing is a genuine billing-method distinction in car rental.
  - partner_program_share (parameter, net_share): Select and ≥14 → 0.90, non-network and ≥14 → 0.97, otherwise 1. physdmg. Multi-source. Observation: plausible as a negotiated network rate.
  - household_package_share (parameter, pkg_share): rank 6 → 0.95, rank 4-5 → 0.98, otherwise 1. auto. **Unreal condition**: the insured's auto-package tier sets the share of the partner agency's rate that Cardinal pays. Together with the inherited "Everything on the invoice that is not paid is the customer's responsibility", this makes the customer with the richer package pay more out of pocket (F5).
  - parts_delay_day_share (parameter, pd_share): Select → 0.85, non-network → 0.95, no parts-delay extension → 1. Observation: base `parts_delay_extension_allowed` treats a documented parts delay as justified, yet those days are short-paid with the remainder left to the customer, which is doubtful practice.
  - Count after strikes: 3 (F5, F6), below 4.
- **rideshare_day_allowance** (4 declared: 2 method, 2 parameter):
  - rideshare_first_covered_day (method, first_gap): theft → report + theft_waiting_days, non-theft and (not drivable or accident tow moved) → report date, otherwise auth start. physdmg + roadside, multi-source. Grounded in base start rules.
  - rideshare_last_covered_day (method, last_off): car auth entered on the day the rideshare closed → day before the car start, no closing → last authorized day, otherwise closing end date. The tier-1 condition is affected by F2.
  - rideshare_daily_allowance (parameter, r_rate): ≤2 days and limit ≥50 → 45, >2 days and limit ≥50 → 35, otherwise the daily limit.
  - trip_interruption_transport_setoff (parameter, alt_set): paid on the report date → full, only other dates → 0.5×, otherwise 0. roadside. Observation: setting off half of a payment made for days the rideshare may not cover is not duplicate-benefit practice.
  - Count after strikes: 4 (2 parameter, 2 method). Bounds met.
- **extension_day_room** (4 declared: 1 method, 3 parameter):
  - comeback_day_maximum_addition (parameter, comeback_add): Select comeback → +5, non-network comeback → +2, otherwise 0. physdmg, multi-source.
  - agency_days_counted (method, car_days): billed > authorized and no credit → authorized; credit and billed → billed − ⌊credit/limit⌋; otherwise billed.
  - rideshare_day_weight (parameter, ride_counted): avg ≤0.5×limit → 0.5, ≤limit → 0.75, otherwise 1. Observation: weighting maximum-days use by the cost of a rideshare day is unusual.
  - comeback_tow_in_days_left_out (parameter, run_counted): comeback tow >10 mi → −2, ≤10 mi → −1, otherwise 0. roadside. **Unreal condition** (F4).
  - Count after strikes: 3, below 4.
- **overbilling_credit** (4 declared: 1 method, 3 parameter):
  - agency_days_owed (method): billed > authorized → authorized, within authorized and span < billed → span, otherwise billed.
  - credit_program_share (parameter): Select and ≥14 → 0.90, non-network and ≥14 → 0.97, otherwise 1. physdmg, multi-source.
  - credit_package_share (parameter): rank 6 → 0.95, rank 4-5 → 0.98, otherwise 1. auto. **Unreal condition** (F5).
  - billed_extras_allowed (parameter): extras and delivery covered → ≤25, extras and not covered → 0, otherwise as billed.
  - Count after strikes: 3, below 4.
- **own_rental_reimbursement** (5 declared: 2 method, 3 parameter):
  - own_rental_first_covered_day (method): comeback and supplement dated after start → supplement date, no repairs-complete closing and not drivable → earlier of report date and start date, otherwise start. physdmg, multi-source.
    - **Unreal tier outcome**: tier 2 starts the covered days of a customer-arranged rental on the report date when that is earlier than the rental's start. That pays a receipt-based reimbursement for days on which the customer had no rental (F7).
    - Observation on tier 1: the authorization's own start day is excluded because the supplement estimate was written later.
  - own_rental_last_covered_day (method): tier-1 condition affected by F2.
  - partner_price_hold (parameter): above the latest partner rate → partner rate, not above → recorded rate, otherwise min(recorded, limit). Real practice: cap at what the preferred vendor would have charged.
  - package_daily_topup (parameter): rank 6 → +3.00, rank 4-5 → +1.50, otherwise 0. auto. Plausible as a benefit enhancement.
  - builtin_transport_setoff (parameter): built-in TE paid and comeback → 0.5× paid, paid and no comeback → all, otherwise 0. physdmg. **Unreal tier outcome**: a duplicate benefit is set off in full or recovered, and a later comeback on the claim has nothing to do with how much of an earlier built-in payment duplicated the option (F7).
  - Count after strikes: 3, below 4.
- Labels otherwise honest. No two tiers of any ladder select the same value or method.
- Every ladder is stated in full in its rule and implemented in its `decides` binding.
- Per task:
  - Task 0 (upgrade, partner, rideshare, extension) has multi-source factors (repair_path_starting_days, partner_program_share, rideshare_first_covered_day, comeback_day_maximum_addition) and cross-difficulty factors (physdmg, roadside, auto).
  - Task 1 (credit, own) has multi-source factors (credit_program_share, own_rental_first_covered_day) and cross-difficulty factors (physdmg, auto).

### findings

**F1. SOURCE-POLICY RED: upgrade_acceptance_days states the authorized days twice, with different values.** Bears on task 0.
- Symptom: two unconditional sentences of the same rule fix `authorized_days` differently.
- Evidence:
  - Rule: "The days an accepted larger-class rental is authorized for are initial_authorization_days, never fewer than one day; the day maximum of the loss is applied when that rental is extended, not when it is recorded."
  - Same rule: "The authorized days are the starting days plus the converted recalibration days, plus the tow-in days, plus the package days, never fewer than one day."
  - The first sentence is also the declared `overwrite.replaced_by` for base `rental_evt_authorization`. It is the declared merged semantics, and it carries no "standard method" qualifier, unlike the other five policies' baselines ("Under the standard method …").
- Root cause: the baseline sentence was written as the declared override, unqualified, and the factor-driven total sits beside it.
- Consequence: a reader following the declared override gets 7 days, and a reader following the last sentence gets the factor sum. The demonstration against a world is in `0.md`.
- Location: rental.extended.yaml, rental_ext_upgrade_acceptance_days `rule`, `overwrite[0].replaced_by`, `baseline.rule`.

**F2. SOURCE-POLICY RED: "the day the … authorization closed" is bound to `end_date`, while the charter's field meanings make it `entry_date`.** Bears on tasks 0 and 1.
- Evidence:
  - Base field meanings for `rental_authorization_closed`: `end_date: Last covered rental day.`, `entry_date: Date closed.`
  - Rideshare compute: `car_n: "COUNT('rental_ledger', event_type='rental_authorization', claim_number=clm, entry_date=r_end)"`, where r_end is `end_date`. Own-rental compute: `entry_date=o_end`, likewise.
  - The rules use "its closing end date" / "the end date of its closing" when they mean `end_date`, and a different phrase here.
- Consequence: in both worlds the closing entry was recorded the day after its end date, so the two readings pick different last-day tiers and different scored amounts. The demonstrations are in `0.md` (rideshare) and `1.md` (own rental).
- Location: rental_ext_rideshare_day_allowance and rental_ext_own_rental_reimbursement, `rule` (last-covered-day sentence), compute `car_n`/`car_start`, factor `*_last_covered_day` tier 1.

**F3. SOURCE-FACTOR RED: recalibration_shop_conversion is labelled `method` but is a multiplier parameter.** Bears on task 0.
- Evidence: its three tiers are `calib_owed * 1.5`, `calib_owed * 0.5` and `calib_owed` (×1), each rounded up. The round-up is a no-op on the integer ×1 tier, so they are one formula with a substituted number.
- Consequence: once the label is corrected, upgrade_acceptance_days has no honest `method` factor. The comeback tow-in factor is struck under F4, so the count is also 3, below the floor of 4.

**F4. SOURCE-FACTOR RED: tow mileage decides rental days.** Bears on task 0.
- Affected factors: comeback_tow_in_days_added (upgrade) and comeback_tow_in_days_left_out (extension).
- Tier conditions: "it ran more than towin_long_miles miles" against "towin_long_miles miles or fewer", giving 2 days against 1 day added, or 2 against 1 left out of the count.
- No personal auto carrier sets or counts rental days by how far the comeback tow ran. Rental days follow the repair time, the shop's completion date and the policy maximum. The comeback-tow part of the condition is a real consideration; the 10-mile split is not.
- Consequence: both factors are struck. The extension policy is left with 3 factors, and the upgrade policy with 3 (see F3).

**F5. SOURCE-FACTOR RED: the insured's auto-package tier sets the agency's rate share.** Bears on task 0 (household_package_share) and task 1 (credit_package_share).
- A partner agency's direct-bill rate is set by the carrier-agency agreement, not by which auto package the insured bought.
- Under the inherited "Everything on the invoice that is not paid is the customer's responsibility", the rank-6 customer is left to pay 5% of the covered day rate that a rank-1 customer would not. A richer package gives a worse outcome, a treatment no carrier would publish.
- In the credit, the same tier enlarges the clawback from the agency according to the customer's package.
- Consequence: both factors are struck, leaving partner invoice and credit with 3 factors each.

**F6. SOURCE-FACTOR RED: the invoiced_covered_days ladder has an unreachable tier.** Bears on task 0.
- "the invoiced rental carries no closing on the ledger" can never hold, because the rule picks the invoiced rental as "the claim's most recently closed rental".
- Consequence: the ladder has two live tiers, and the factor is struck as a 3-tier factor.

**F7. SOURCE-FACTOR RED: own_rental_reimbursement has unreal tier outcomes.** Bears on task 1.
- builtin_transport_setoff tier 1 sets off only own_te_comeback_share (0.5) of a duplicated built-in transportation payment because the claim later had a comeback.
- own_rental_first_covered_day tier 2 pays days before the customer-arranged rental started.
- Consequence: both factors are struck, leaving 3 factors.

**Observations (charter-global).**
- E2/E3 prerequisite realism (see prerequisite_sentences).
- Covered-days general-then-exception wording (rule_compute_equivalence item 4).
- Customer-wide roadside reads (item 2).
- Rideshare allowance ignores the fare totals.
- The partner invoice and credit rely on the customer's reading of the agency closing copy, and the agency credit is recorded unilaterally.
- Several tier values are of doubtful realism but not demonstrably unreal: comeback starting days, the recalibration proxy, rideshare day weighting, parts-delay share, and the alternate-transportation half set-off.
- The difficulty claim lists four event types with no extended policy.

## closing_checklist

Written after the reveals of both tasks. Everything above this heading was frozen before any reveal (sha256 `b9bfcd96…` checked unchanged at reveal time). The difficulty **does not close**: neither task passes all four relationships.

- Per-task files `0.md` and `1.md` correspond to tasks 0 and 1, with this file alongside. No earlier revision exists.
  - Task 0: SOURCE-POLICY RED, SOURCE-FACTOR RED, SOURCE-TASK RED; problem tree PASS.
  - Task 1: SOURCE-POLICY RED, SOURCE-FACTOR RED, SOURCE-TASK RED; problem tree PASS.
- Coverage and scope: all six extended policies are covered. The task scopes (whole trees) are disjoint: task 0 has {extension, upgrade, partner invoice, rideshare} and task 1 has {credit, own rental}, matching each task's `charter_scope`. Task tools are closed. The uuid8s are independent.
- Trees:
  - Task 0 has 3 prerequisites, 3 value_input edges and 2 owner=user writes.
  - Task 1 has 1 prerequisite, 1 value_input edge and an owner=user root.
  - Both are acyclic, and the difficulty-wide graph is a DAG.
  - Every edge bears weight (GT figures equal my blind figures).
- Factors (not met):
  - F3, F4, F5, F6 and F7 strike factors so that upgrade, partner invoice, extension, credit and own rental each fall below 4 surviving factors, and upgrade has no honest `method`.
  - Task 1's set-off evidence row contradicts physdmg's charter.
  - Every declared factor bears weight against its baseline, and every all-baseline figure is definite and differs from gold. Those parts hold.
- Gate re-run on the final form: not applicable (no final form; the artifacts need rework). The conductor's snapshot (`GATES.txt`, all green) stands as the entry condition only.

## revision_2

### charter_global_frozen (revision_2)

- Frozen: 2026-10-05, before any revision_2 GT was read. Auditor: the same independent auditor as round 1. The revision_1 text above is left untouched.
- Inputs: `/tmp/erl35_views/rental_reimbursement_claims.r2/`. I checked the hashes against MANIFEST and the repo files, and they are identical.
  - `rental.extended.yaml`: `c47bfab4…3a3199`. Changed from round 1 (`cdcfb2cb…`), so every charter-global section is re-derived in full below.
  - `task_tools.py`: `c2cd95ca…f6402`. Unchanged, so action_binding_and_uuids is carried forward on the unchanged hash.
- Masking: the same as round 1. tasks/*.json and the worklog were not opened before the freeze.
- Entry: `/tmp/erl35_views/rental_reimbursement_claims.r2/GATES.txt` is all green (traceability deferred).
- Base section lines 1-898: still verbatim against `blueprint/products/rental.yaml`.

### policy_conflict_scan (revision_2)

- Subjects, tools, triggers and the prerequisite graph are unchanged from revision_1. The scopes are still disjoint and together cover all six policies.
- New cross-category reads:
  - Rideshare and extension now read auto (CPARAM rental_max_option_rank).
  - Upgrade drops roadside.
  - Partner invoice and credit drop auto.
  - Own rental drops physdmg_payments.
- No terminal-state conflict.

### rule_compute_equivalence (revision_2)

- All `compute_basis` quotations are substrings of their rules (mechanical check). Every baseline and every `replaced_by` sits inside its rule.
- Rideshare and own rental, last covered day: the rule now reads "entered on the end date of the … closing", which matches the compute (`entry_date=r_end` / `entry_date=o_end`, the closing `end_date`). Round-1 item 1 is resolved.
- Upgrade: "Under the standard method the days … are initial_authorization_days". The final total "The authorized days are the repair days plus the package days" is the declared `replaced_by`. Round-1 item 3 is resolved.
- **New, partner invoice:**
  - The rule's sentence "The covered days of a partner invoice are the closed span of that rental, counted from its start date through the end date of its closing, both days included, never more than its authorized days." stands unqualified. It comes before the "Under the standard method" sentence and is not governed by it.
  - Later sentences contradict it: "a rental closed because repairs were complete is owed repair_complete_grace_days beyond its authorized days" and "The covered days are the closed span, never more than the authorized days plus the closing allowance."
  - Two unconditional caps apply to one quantity (finding N1).
- Unchanged observations:
  - Customer-wide roadside reads (only the rideshare set-off remains).
  - Flat covered-days opener on rideshare and own rental, and flat days-owed opener on the credit, each followed by a conditional ladder that ends in "otherwise".

### action_binding_and_uuids (revision_2)

Carried forward. The `task_tools.py` hash is unchanged at `c2cd95ca…`, and the (tool, computes) claims in the new charter are the same six pairs. PASS.

### prerequisite_graph and prerequisite_sentences (revision_2)

- The four edges, their `policy_source` sentences (verbatim in the blocked rules, mechanical check), forms, gates, kinds, conditions and `resolved_by` are unchanged. The graph is acyclic. The single-reading derivation is as in revision_1.
- No new sentence in any rule orders problems. The new closing-allowance and package sentences order nothing.
- PASS. The E2/E3 realism observation stands, as the reworker states.

### override_declarations (revision_2)

- Upgrade: the `replaced_by` now equals the rule's final total, so the merged semantics are unique (F1 closed).
- Partner invoice: `overwrite[0]` now declares the closing allowance as the replacement for base "only days inside the authorization are covered …". The declaration is legal, but the rule keeps a flat "never more than its authorized days" (N1).
- Own rental: the set-off is removed from `replaced_by` and from the rule. The base combo sentence ("when the vehicle carries an option, the option pays and the built-in benefit does not apply") is still followed.
- Rideshare, extension and credit: as in revision_1, plus the new package top-up, package days and closing allowance. All are inside declared `replaced_by` texts or have no base counterpart.

### factor_ladders (revision_2)

- **upgrade_acceptance_days** (4 factors):
  - repair_path_starting_days (parameter; 4/2/7).
  - recalibration_days_owed (parameter; 2/1/0).
  - **recalibration_scheduling** (method):
    - Select → max(starting, recalibration).
    - Non-network → starting + recalibration + sublet_transfer_days.
    - Otherwise → starting + recalibration.
    - Max against sum is a genuine algorithmic difference, so the label is honest.
    - Realistic: network shops recalibrate ADAS in house during repair, while independents sublet to a dealer, which adds transport time.
    - The "otherwise" tier fires when no estimate is on file (`repair_shop_type` has only the two enum values), so it is reachable.
  - package_rental_days (parameter; 2/1/0).
  - 3 parameter + 1 method. Multi-source factor: repair_path_starting_days. Cross-difficulty: physdmg and auto. **F3 and F4 closed** (the tow factor is gone).
- **partner_invoice_settlement** (4 factors):
  - **invoiced_closing_allowance** (parameter): repairs complete → repair_complete_grace_days; total-loss offer → total_loss_rental_end_days; otherwise 0. This is grounded in base `rental_evt_extension_and_end` end rules, and all three tiers are reachable close_reasons. **F6 closed.**
  - partner_rate_convention (method).
  - partner_program_share (parameter; multi-source).
  - parts_delay_day_share (parameter).
  - household_package_share removed. **F5 closed.**
  - 3 parameter + 1 method. The ladder structure is sound. N1 is a rule-wording defect, not a ladder defect.
- **rideshare_day_allowance** (5 factors): as in revision_1, plus rideshare_package_topup (parameter; +5.00/+2.50/0 by package rank, capped at the daily limit). A package-linked benefit enhancement is plausible. 3 parameter + 2 method.
- **extension_day_room** (5 factors):
  - comeback_day_maximum_addition (parameter).
  - agency_days_counted (method; tier 1 now "billed > authorized + closing allowance and no credit → authorized + allowance").
  - rideshare_day_weight (parameter).
  - package_day_room_addition (parameter; 3/1/0, auto).
  - agency_rental_closing_allowance (parameter; 1-or-total-loss/0, grounded in base end rules).
  - The tow-in factor is removed. **F4 closed.** 4 parameter + 1 method.
- **overbilling_credit** (5 factors):
  - agency_days_owed (method; caps at authorized + allowance).
  - credit_program_share (parameter).
  - agency_closing_allowance_owed (parameter).
  - owed_rate_convention (method; weekly/monthly blocks mirror the partner invoice convention).
  - billed_extras_allowed (parameter).
  - credit_package_share removed. **F5 closed.** 3 parameter + 2 method.
- **own_rental_reimbursement** (4 factors):
  - own_rental_first_covered_day (method): theft → later of start and report + theft_waiting_days; non-theft comeback with a supplement dated after the start → supplement date; otherwise start. The tier that paid days before the start is removed.
  - own_rental_last_covered_day (method).
  - partner_price_hold (parameter).
  - package_daily_topup (parameter).
  - builtin_transport_setoff removed. **F7 closed.** 2 parameter + 2 method.
- No two tiers share an outcome. Every ladder is stated in its rule and implemented in `decides`.
- Per task:
  - Task 0 multi-source factors: repair_path_starting_days, partner_program_share, rideshare_first_covered_day, comeback_day_maximum_addition. Cross-difficulty: physdmg, auto, roadside.
  - Task 1 multi-source factors: credit_program_share, own_rental_first_covered_day. Cross-difficulty: physdmg, auto.
- The doubtful-but-unstruck observations from revision_1 stand: comeback starting days, the recalibration estimate-amount proxy, parts-delay share, rideshare weighting, alternate-transport half set-off, and package-linked day/amount enhancements.

### findings (revision_2)

| Round-1 item | Status | Evidence |
| --- | --- | --- |
| F1 upgrade double statement | **closed** | Baseline sentence prefixed "Under the standard method"; `replaced_by` equals the final total |
| F2 "day … closed" | **closed** | Rideshare and own-rental rules say "entered on the end date of the … closing" |
| F3 mislabelled method | **closed** | recalibration_scheduling: max against sum |
| F4 tow-mile tiers | **closed** | Both tow factors removed |
| F5 package rate share | **closed** | household_package_share and credit_package_share removed |
| F6 dead tier | **closed** | invoiced_covered_days replaced by invoiced_closing_allowance (three reachable tiers) |
| F7 own-rental unreal tiers | **closed** | Set-off factor removed; tier 2 replaced by the theft tier |

**N1. SOURCE-POLICY RED (new in revision_2, introduced by the F6 rework): partner_invoice_settlement caps covered days twice.** Bears on task 0.
- Rule: "The covered days of a partner invoice are the closed span of that rental, … both days included, never more than its authorized days."
- Same rule: "a rental closed because repairs were complete is owed repair_complete_grace_days beyond its authorized days" and "The covered days are the closed span, never more than the authorized days plus the closing allowance."
- The first sentence is not under the "Under the standard method" qualifier, which the upgrade fix used for exactly this pattern.
- Consequence: on a world where the closed span exceeds the authorized days and the rental closed for completed repairs, the two sentences give different covered days. The demonstration is in `0.md` revision_2.
- Location: rental.extended.yaml, rental_ext_partner_invoice_settlement `rule` (and `baseline.rule`).

### closing_checklist (revision_2)

Written after the revision_2 reveals. The difficulty **does not close**, because task 0 fails on N1.

| Task | Policy | Tree | Factors | Unique solution |
| --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (N1) | PASS | PASS | SOURCE-TASK RED (N1) |
| 1 | PASS | PASS | PASS | PASS |

- Round-1 claims verified: F1-F7 and the task-1 physdmg-row finding are all closed. Evidence is in the revision_2 sections above and in each task file.
- New defect: N1, introduced by the F6 rework, in partner_invoice_settlement. It bears on task 0 only.
- Regressions otherwise: none. Every new factor bears weight on its task's world (GT figures equal my blind figures) and passes the realism and label tests.
- Coverage and scope disjointness, tool closure and uuid8s: unchanged, PASS.
- Trees: 3 and 1 prerequisites, value_input floors met, owner=user writes present, DAG.
- Factor bounds: upgrade 4, invoice 4, rideshare 5, extension 5, credit 5, own 4. Each has at least 2 parameter and 1 method factors, and each task has multi-source and cross-difficulty factors.
- Gate re-run on the final form: the conductor's snapshot `/tmp/erl35_views/rental_reimbursement_claims.r2/GATES.txt` is all green. The difficulty is not closable while N1 stands.

## revision_3

### charter_global_frozen (revision_3)

- Frozen: 2026-10-05, before any revision_3 GT was read. Earlier revisions are untouched.
- Inputs: `/tmp/erl35_views/rental_reimbursement_claims.r3/`. The hashes match MANIFEST and the repo.
  - `rental.extended.yaml`: `a2745d8f…9a276750`. Changed against revision_2 `c47bfab4…`.
  - `task_tools.py`: `c2cd95ca…`, unchanged.
  - Both task views are byte-identical to revision_2 (`cmp`).
- GATES.txt: all green, traceability deferred.
- The base section is still verbatim against the blueprint.
- **Scope of the change:** `diff` against revision_2 touches only rental_ext_partner_invoice_settlement, in four places:
  - Rule: "Under the standard method" is prefixed to the covered-days opener.
  - Rule: ", in place of the standard cap at the authorized days" is appended to the allowance cap sentence.
  - The same edits are mirrored in `baseline.rule` and in `compute_basis.cover_days`.
  - No compute, factor, param, prerequisite or other policy changed.
- I re-derived the charter-global checks on this text:
  - The mechanical checks pass for all six policies: baseline inside the rule, every `replaced_by` inside the rule, every `compute_basis` quotation inside the rule, every edge sentence verbatim.
  - The texts of the other five policies are byte-identical to revision_2, so their revision_2 conclusions are re-confirmed on identical input: policy_conflict_scan, rule_compute_equivalence, prerequisite_graph and prerequisite_sentences, override_declarations, factor_ladders, all PASS.
  - action_binding_and_uuids is carried forward on the unchanged tool hash.

### N1 re-check (revision_3)

- The partner-invoice rule now reads:
  - "Under the standard method the covered days of a partner invoice are the closed span of that rental, … never more than its authorized days."
  - "The covered days are the closed span, never more than the authorized days plus the closing allowance, in place of the standard cap at the authorized days."
- The authorized-days cap is now scoped to the standard method, and the allowance cap explicitly replaces it. With the closing-allowance sentence ("is owed repair_complete_grace_days beyond its authorized days"), the merged rule has one reading. The `baseline.rule` stays an honest standard method: cap at authorized days, which equals close_allow 0.
- **N1 closed.** The repeated "Under the standard method" in two consecutive sentences is wording only and changes no relationship.
- No new charter-global defect.

### closing_checklist (revision_3)

Written after the revision_3 reveals. **The difficulty passes the source-layer audit.**

| Task | Policy | Tree | Factors | Unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- **Files:** the per-task files `0.md` and `1.md` sit alongside this file. Revisions 1-3 are kept in place and traceable. Every comparison section of revision_3 carries a PASS.
- **Coverage and scope:** all six extended policies are covered. The task scopes (whole trees) are pairwise disjoint and match each task's `charter_scope`. Task tools are closed, and each of the six uuid8s is independent and frozen.
- **Trees:**
  - Task 0: 3 prerequisites, 3 value_input edges, 2 owner=user writes.
  - Task 1: 1 prerequisite, 1 value_input edge, an owner=user root.
  - The difficulty-wide graph is a DAG, and every edge bears weight.
- **Factors:**
  - Factor counts: upgrade 4, invoice 4, rideshare 5, extension 5, credit 5, own rental 4. Each policy has at least 2 parameter and at least 1 method factors.
  - Each task has multi-source and cross-difficulty factors, with the cross-difficulty rows seeded.
  - Every ladder has three distinct, realistic tiers stated in its rule.
  - Every factor bears weight against an honest baseline, and each all-baseline figure is definite and differs from gold.
- **Gates:** the conductor's re-run on the final form, `/tmp/erl35_views/rental_reimbursement_claims.r3/GATES.txt`, is all eight green (traceability deferred until the KB is published).
- **Standing observations (realism, not reds):**
  - Extension waiting on the earlier invoice and the customer's rideshare receipts (E2/E3).
  - Per-day rideshare allowance with no fare total.
  - Agency credit recorded by Cardinal only.
  - Doubtful-but-unstruck tiers.
  - tasks/1.json hash changed with no scored change.
