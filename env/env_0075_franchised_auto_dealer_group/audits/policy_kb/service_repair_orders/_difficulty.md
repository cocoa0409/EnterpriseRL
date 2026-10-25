# KB-layer audit — difficulty service_repair_orders (product service, M=2)

## revision_1

Auditor: independent KB-audit agent, 2026-10-22. Brief: `/tmp/erl0075_coord/kbaudit.md`.

### Entry conditions (cited, not re-judged)
- Policy-side verdict: `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`.
- Entry snapshot `kb_snapshot.sh service_repair_orders service` (2026-10-22T10:20:30): `check_docs.py service => DOCS OK`; coordinator's post-publication `check_traceability.py service_repair_orders => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`; `EXTENDED OK`, `TASK TOOL CONTRACT OK`, `REPLAY OK`, `SOLVABILITY OK`, `COMPUTE OK`, `GROUNDING OK`, `SCOPE OK`; 82 docs; sha256 `9a94105a86d9 a146a457904d e9a0b8d27439 35b21e794ded`; runtime views `0.runtime.json 750253571ad7f10d`, `1.runtime.json bedf796788bee35a`.
- Closing re-run (2026-10-22T10:31:34): identical lines and hashes. check_traceability was not run by the auditor (brief).
- Published: purchase, service, maintenance, warranty, loaner; vsc and gap unpublished.

### Order and isolation
Blind answers frozen 2026-10-22T10:26 (`runtime_context/service_repair_orders/0.md` sha256 `79442789...`, `1.md` `5a5902d8...`) before any read of extended.yaml, task_tools.py, tasks/*.json, plan or worklog. DB only through `db_query.py`; greps limited to docs/ and, after the reveal, to task_tools.py. No contamination.

### Per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Note |
|---|---|---|---|---|
| 0 (redemption <- points <- overage; redemption <- expiry) | PASS (118.56 / 4666 / 2026-10, 3278 / 27541, 441.56 all equal GT) | PASS | PASS | Shield-dependent figures CONDITIONAL on the vsc publication |
| 1 (diagnostic credit <- estimate; <- EPD <- comeback) | PASS (645.54 / 3.89 / 2847.19 / 76.36 all equal GT) | PASS | PASS | no unpublished dependency |

### KB defects (renderer)
None.

### Source-side items (instantiator) — all non-scoring
- **SRC-1 (seed realism, cross-product maintenance, task 1).** Plan KC-2404183 on the 2021 Silverado 2500HD (c3d451) records `odometer_at_sale 66150` on `sale_date 2024-04-02` (`expiration_odometer 141150`), but the service ledger records the same vehicle at `odometer_in 61200` on RO 250312 dated 2025-03-12 — the odometer runs backwards 11 months after the sale. The published maintenance rule fixes the term's end "at the odometer at signing plus the plan's term miles" (`term_and_visit_schedule`: Fleet 12-Visit 75000 miles), so the reading at signing is a state that rule and the ledger cannot both produce. Scored values unaffected (every factor reads only the plan's `active` status, which holds at 78400 miles under any reading at signing at or above 3400).
- **SRC-2 (seed realism, cross-product maintenance, tasks 0 and 1).** The Kessler Care plans carry `visits_remaining` below the visits included — KC-2408317 (Plus 6-Visit) 2 of 6, KC-2409266 (Fleet 12-Visit) 8 of 12, KC-2404183 5 of 12 — while `find_maintenance_plan_ledger` returns no rows for either customer. The published maintenance docs count unused visits as "the visits loaded, less visits redeemed, plus visits reinstated, as the plan ledger shows", so these holdings are not states the maintenance rules produce from an empty ledger. Scored values unaffected.

### Policy-side notes (do not change the verdict)
- **P-1.** The computation documents carry the source rules' assembly sentences ("every rate this policy sets out that increases the overage", "every share this policy sets out that reduces the credit", "every bonus rate / dollar credit / multiplier / fixed number of points / lengthening / protected points / addition / allowance / index ... this policy sets out"). These sentences announce that modifiers exist; they come from each extended rule (not its baseline) and have no other lawful home, since an assembly step moved into a factor document would be a bijection red. Recorded as a source-form observation, not a KB defect.
- **P-2.** Redemption <- month-end expiry is declared action form with a `fallback_reason`; the sentence is rendered verbatim on the blocked side and the depended-on document performs the named run. The blind derivation reached it through the missing October entry; it is not pre-solved.

### Closing checklist
- One runtime_context and one policy_kb file per task, each with blind_answer / gt_comparison and source_to_kb / kb_to_source / bijection_verdict / dependency_form; first revision, nothing overwritten.
- Every normative atom of the four extended policies per task, their base clauses, the retired surfaces (8 superseded clauses, each rendered as no longer in force, with the remaining clauses in force) and all 42 factor ladders across the 8 extended policies are entailed by docs/service; all 7 prerequisite sentences stand verbatim, in declared form, in the blocked hub only; each service tool is named only in its own hub; no route, chain or mirror title.
- Coverage gap stated: cross-product contradictions with the unpublished vsc/gap corpora are outside this pass; task 0's Shield-dependent figures need the re-judge once vsc is published.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=SRC-1,SRC-2

## revision_2

Confirm round, 2026-10-22T10:40, after the instantiator's seed-only fix of SRC-1 and SRC-2 (policy-side `VERDICT revision_7 CLEAN`, as reported by the coordinator).

### Snapshot (`kb_snapshot.sh service_repair_orders service`, 2026-10-22T10:40:35)
`check_docs.py service => DOCS OK`; `check_traceability.py service_repair_orders => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`; `EXTENDED OK`, `TASK TOOL CONTRACT OK`, `REPLAY OK`, `SOLVABILITY OK`, `COMPUTE OK`, `GROUNDING OK`, `SCOPE OK`; 82 docs; sha256 `9a94105a86d9 a146a457904d 8d4d6a961afd a81373f9ef8b`. Against revision_1, extended.yaml and task_tools.py are byte-identical and only tasks/0.json and tasks/1.json changed. Runtime views are unchanged (`750253571ad7f10d`, `bedf796788bee35a`). No docs/ file is newer than the revision_1 freeze.

### Source items, checked against the rebuilt runtime records
- **SRC-1 — CLOSED.** KC-2404183 (Silverado c3d451) now has `odometer_at_sale 47850` on 2024-04-02 and `expiration_odometer 122850` (= 47850 + the 75000 Fleet 12-Visit term miles of `term_and_visit_schedule`). Merged with the service ledger, the readings rise in date order: 47850 (2024-04-02), visits 52856 (2024-08-09) and 57862 (2024-12-16), service RO 250312 61200 (2025-03-12), visits 62843 (2025-05-09), 67859 (2025-11-02), 72874 (2026-04-28) and 77862 (2026-10-21), diagnostic fee 78400 (2026-11-09). The plan is still active (2027-04-02 / 122850 > 78400).
- **SRC-2 — CLOSED.** `find_maintenance_plan_ledger` now carries, for each plan, one visits-loaded row on its sale date (6 / 12 / 12) and visit-redeemed rows numbered 1..n, so the visits remaining equal loaded less redeemed: KC-2408317 6 − 4 = 2; KC-2409266 12 − 5 = 7 (holding updated from 8); KC-2404183 12 − 6 = 6 (updated from 5). The visit readings sit about 5000 miles apart (the plan's service interval) and fall in order between the service-ledger check-ins (CR-V: 5062 < 6210 on 2024-08-06, 10059 < 11050, 14965 < 15200, 18640 < 20062 < 20410; F-250: 36498 < 38500 on 2026-02-02, 46491 < 50100 on 2026-10-30). The visit ROs are not billed on the service ledger, as the coverage priority rule requires ("recorded in that program's records and never billed here").

### No regression
- The service-side records that feed the scored inputs read the same as in revision_1: account tier, opened date, balance and points; customer-pay labor and parts ledger totals; authorizations, deals, Shield contracts, vehicles and stores. Every factor reading a Kessler Care plan reads only plan status (`active`) on the same vehicle, so no factor's tier moved. GT is unchanged (118.56 / 4666 / 2026-10, 3278 / 27541, 441.56; 645.54 / 3.89 / 2847.19 / 76.36) and still equals the revision_1 blind answers.
- No new KB defect and no new source item. The policy-side notes P-1 and P-2 stand. Task 0's Shield-dependent figures remain CONDITIONAL on the vsc publication.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS (vsc CONDITIONAL) | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3

Cross-product re-judge, 2026-10-22T12:20. All seven products are published (docs/purchase 73, service 82, maintenance 57, vsc 62, gap 68, warranty 23, loaner 18 — 383 docs).

### Snapshot (`kb_snapshot.sh service_repair_orders service`, 2026-10-22T12:20:26)
`check_docs.py service => DOCS OK`; `check_traceability.py service_repair_orders => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`; `EXTENDED OK`, `TASK TOOL CONTRACT OK`, `REPLAY OK`, `SOLVABILITY OK`, `COMPUTE OK`, `GROUNDING OK`, `SCOPE OK`; 82 docs; sha256 `9a94105a86d9 a146a457904d 8d4d6a961afd a81373f9ef8b`, identical to revision_2. Runtime views `750253571ad7f10d` / `bedf796788bee35a` are unchanged. No docs/service file changed.

### Round-2 state
Round 2 had no RED. SRC-1 and SRC-2 stay closed: the plan rows and plan ledgers read the same as in revision_2. No regression.

### KB side, re-checked on the full 383-doc corpus
- Each of the 7 service prerequisite sentences still occurs only in its blocked service hub.
- No non-service document names any of the 8 service tools.
- The vsc, gap, warranty and loaner documents mention "Service Accounts and Repair Orders records" only as evidence for their own factors (diagnostic-fee credit, deductibles billed, the store on a repair order, loaner free days). They restate no service rule and contradict none.
- kb=CLEAN.

### CONDITIONAL figures re-judged (task 0)
The figures 4666, 3278 and 441.56 depended on the Kessler Shield factors. The vsc corpus is now published and both seeded contracts are rule-produced (checked against `contract_sale_conditions`, `sale_eligibility_and_term_schedule`, `deductible_schedule` and `contract_expiration`):
- **KS-2416950** — Exclusionary, new 2024 CR-V. Age 0 against 6 years; odometer 12 against 80000. Term 60/75000, counted from the sale, ends 2029-04-20 / 75012. Deductible 100 is offered. Price 2895.00 against a 4495.00 ceiling. Active.
- **KS-2305581** — Select, certified pre-owned 2021 Camry. Age 2 against 10 years; odometer 24105 against 120000. Term 48/60000 ends 2027-06-17 / 84105. Deductible 100. Price 2195.00 against a 3295.00 ceiling. Active.

The vsc ledgers are empty, so there is no claim to price. **Task 0 PASS, no longer conditional.**

### Other-product rows in the tasks' records, priced against the published docs
- **Maintenance**, all rule-produced:
  - KC-2408317 (Plus 6-Visit, sold on the CR-V purchase deal): 549.00 less the 5% bundle discount = 521.55; 36 months / 35000 miles gives 2027-04-20 / 35012. Within the 6-year / 50000-mile sale limits. 6 visits loaded, 4 redeemed at KHB (all group stores honored), with readings 5062 / 10059 / 14965 / 20062, each 4000 or more miles after the last. 2 remain.
  - KC-2409266 and KC-2404183 (Fleet 12-Visit, bought on their own): 1029.00 retail, below the 10-plan fleet-volume threshold, outside the fleet-addendum scope (deals closed). Terms 36 months / 75000 miles. Ages 2 and 3 within the 8-year limit. 7 and 6 visits remain. Spacing is met. Both plans are active.
  - Factory complimentary maintenance does not affect these plans (Honda and Ford 0 visits; the Chevrolet 12-month term ended before the plan's 2024 sale).
- **Purchase**, mismatches listed below:
  - The documentary fee, title filing window and markup cap are met where recorded (CR-V: buy rate 5.49, APR 6.49, markup 1.0 against the 2.0 cap; title filed 4 and 4 days after delivery on the two retail deals).
  - Deal closure from delivered status and fleet incentive eligibility are consistent: the fleet volume minimum is 5 units a year, and Hollister's in-service years hold at most 3 units, so no incentive is owed.
- **Vsc:** as above.
- **Gap, loaner, warranty claims, cancellation requests, handoff and verification logs:** none seeded for either customer.

### Source items (instantiator), all members
- **SRC-3 (purchase hold expiry, task 0) — 2 members.**
  - KHB-24-21873 (New Vehicle Retail Purchase, hold 5 days, extensions +3 up to 2): reserved 2024-04-10, `hold_expires_date 2024-04-24` with `hold_extension_count 0`. The rules give 2024-04-15 (or at most 04-21 with 2 extensions). With 0 extensions the hold could have been released from 04-16, before the 04-18 contract.
  - KTD-23-20946 (Certified Pre-Owned Vehicle Purchase, hold 3, +3, at most 1 extension): reserved 2023-06-10, `hold_expires_date 2023-06-24`, 0 extensions. The rules give 06-13 (06-16 with the one extension), and the contract is dated 06-15.
  - Sources: purchase.yaml `hold_expires_date: reservation date plus the hold days`; `deal_types_and_reservation_holds`; `hold_lapse_and_release`.
  - Moves no scored value: the factors read the deal's status, financing type and vehicle.
- **SRC-4 (fleet purchase deals, task 1) — 2 members.** KCV-22-20417 and KCF-21-21388 (both closed, showroom-delivered) carry `hold_expires_date None` (the rule gives reservation + 14: 2022-03-15 and 2021-02-22) and `title_application_date None`. A closed deal's title application is filed within 30 days after delivery (`contract_fees_and_title_schedule`, `title_registration_and_taxes`). Moves no scored value.
- **SRC-5 (fleet net terms before the service account, task 1) — 1 deal, 2 facts.**
  - KCF-21-21388 (Silverado) is contracted 2021-02-15 with `financing_type fleet_net_terms`. Net terms are allowed "only while the buyer holds a Commercial Fleet Account - Net 15 or Net 30 service account in active status ... at the time the deal is contracted" (`fleet_net_terms_eligibility`), but the buyer's service account `opened_date` is 2021-05-03.
  - The customer's `profile_opened_date` (schema: "date the customer profile was first created at any store of the group") is also 2021-05-03, after this deal's 2021-02-08 reservation.
  - Moves no scored value as seeded: no factor reads this deal, and the account's opening date feeds only the early-payment tenure addition (66 months, tier ≥ 60). A changed opening date keeps that tier only if the account stays at least 60 whole months old on 2026-11-11.
- **SRC-6 (runtime-visible repair component, task 0) — 1 member.**
  - The persona states the open repair order RO 262245 is for "new front struts" on the 2024 CR-V (in service 2024-04-20; 22180 miles on 2026-10-29). Under the published warranty docs, a Factory Basic Limited Warranty registered at first retail delivery (Honda 36 months / 36000 miles from the in-service date, so in force until 2027-04-20) covers the Suspension group. Struts are not among the listed wear items (pads, rotors, wipers, tires, filters, bulbs). The service coverage-priority rule then pays an in-force warranty before customer pay.
  - The seeded ledger books the line as customer pay, and the warranty coverage rows are absent (unread residue, below). So the visible records support the GT. But the visible persona fact and the published warranty rules point the other way.
  - Moves no scored value as seeded. If that line were not customer pay, RO 262245 would carry no customer-pay charges and the redemption figure would change.

### Notes (not RED)
- **Hidden-narrative note (task 1).** The design rationale calls RO 260205 / RO 261030 the F-250's "EGR repair". Published warranty docs give the Ford a Federal Emissions Performance Warranty (96 months / 80000 miles from the 2022-03-15 in-service date) covering emission control components, which would pay before customer pay. The component appears on no runtime-visible record (ledger, persona or EC text), and no warranty coverage is seeded, so the visible world is consistent. Recorded for the instantiator's awareness only.
- **Accepted residue (unread rows the replay closure forbids seeding):**
  - Warranty coverages that `coverage_registration_and_term` registers at delivery for the CR-V, Camry (incl. the CPO Powertrain), Silverado and F-250.
  - Purchase transactions (same-day reservation deposits, charges, payments).
  - Purchase deals for Hollister's other 8 units.
  - The component identity of earlier customer-pay service lines.
- **Policy-side notes P-1 and P-2 stand.**

### Owed-at-once writes of other products — none can move a scored read
- **Purchase:**
  - fleet late balance fee — deals closed, balance 0.
  - fleet incentive — below the 5-unit minimum.
  - home-delivery fee correction — showroom deliveries.
  - hold extension and deposit — no reserved deal.
- **Maintenance:** no plan reached its expiration date or odometer (CR-V 22180 / 35012; F-250 50100 / 96480; Silverado 78400 / 122850). Cancellations and moves happen only on request.
- **Vsc:** no contract reached expiry; there are no claim lines for rental or re-decision writes.
- **Gap, loaner, warranty:** no rows.
- No other product's tool writes service ledger, service account or authorization rows. The other-product fields the service factors read (deal status and financing, plan status, contract status) are untouched by any of these writes.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS (CONDITIONAL resolved) | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=SRC-3,SRC-4,SRC-5,SRC-6

## revision_4

Confirm round, 2026-10-22T12:38, after the instantiator's seed-only fix of SRC-3 to SRC-6 (policy-side `VERDICT revision_8 CLEAN`, as reported by the coordinator).

### Snapshot (`kb_snapshot.sh service_repair_orders service`, 2026-10-22T12:38:35)
- Checks: `check_docs.py service => DOCS OK`; `check_traceability.py service_repair_orders => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`; `EXTENDED OK`, `TASK TOOL CONTRACT OK`, `REPLAY OK`, `SOLVABILITY OK`, `COMPUTE OK`, `GROUNDING OK`, `SCOPE OK`.
- sha256 `9a94105a86d9 a146a457904d 6a877b7203a2 24ca1cf3f3ae`: extended.yaml and task_tools.py are byte-identical, and only tasks/0.json and 1.json changed.
- Runtime views: `0.runtime.json 24a70195ab9c77cd` (changed: persona repair wording), `1.runtime.json bedf796788bee35a` (unchanged).
- No docs/ file of any product is newer than revision_1.

### Round-3 source items, checked against the rebuilt runtime records and the published docs
- **SRC-3 — CLOSED.**
  - KHB-24-21873: reserved 2024-04-10 + 5 hold days = 04-15, + 1 extension of 3 days = `hold_expires_date 2024-04-18` with `hold_extension_count 1` (within the limit of 2). The 04-18 contract falls on the last held day, which the hold covers in full (`hold_lapse_and_release`).
  - KTD-23-20946: 2023-06-10 + 3 = 06-13, + 1 extension of 3 days = `2023-06-16`, count 1 (the limit). The contract is 06-15.
- **SRC-4 — CLOSED.**
  - KCV-22-20417: reserved 2022-03-01 + 14 = `hold_expires_date 2022-03-15`, 0 extensions, contracted 03-08 inside the hold. `title_application_date 2022-03-18` is 3 days after the 03-15 delivery, within 30.
  - KCF-21-21388: 2021-02-08 + 14 = `2021-02-22`, contracted 02-15. Title 2021-02-25 is 3 days after the 02-22 delivery.
- **SRC-5 — CLOSED.** The service account (`Commercial Fleet Account - Net 30`, active) now has `opened_date 2021-01-11`, and the customer's `profile_opened_date` is 2021-01-11. Both precede the KCF-21-21388 reservation (2021-02-08) and contract (2021-02-15), so net terms were written while an active Net 30 account existed (`fleet_net_terms_eligibility`), as they were for KCV-22-20417 (2022-03-08).
  - Moved figure re-derived: the early-payment tenure addition counts 70 whole months from 2021-01-11 to 2026-11-11, still ≥ 60 → +0.5%, so the early-payment discount stays 3.89. No other task-1 factor reads `opened_date`.
- **SRC-6 — CLOSED.** The persona now says RO 262245 is for "new front and rear brake pads and rotors". These are wear items that neither the published warranty coverages ("wear items (brake pads and rotors, ...)" are not covered) nor any Kessler Shield level ("pads, shoes and rotors never") pays, so customer pay is the rule-produced outcome. The ledger row is unchanged. The persona's figures, identity lines and if/else branches are unchanged.

### No regression
- The record digests are identical to round 2/3 for both tasks' service ledgers, authorizations, Kessler Shield contracts and vehicles. Task 0's account is unchanged. The maintenance plans are still active with 2 / 7 / 6 visits remaining.
- GT is unchanged: 118.56 / 4666 / 2026-10, 3278 / 27541, 441.56; 645.54 / 3.89 / 2847.19 / 76.36. Both still equal the revision_1 blind answers.

### Same-class neighbour observation (not RED)
The service account's entry condition requires a fleet business with at least 10 (Net 30) or 3 (Net 15) registered fleet vehicles. Of the 10 vehicles on file, only one (the 2020 F-350, in service 2020-06-11) was in service by 2021-01-11. This was the same at the old 2021-05-03 date (2 vehicles), so it did not arise from this fix. The records carry no registration history and no tier-change history, and earlier units may since have been retired, so the condition can be neither proved nor disproved from the visible records. No figure reads it. Not listed as a source item.

No new KB defect and no new source item. The policy-side notes P-1 and P-2 and the round-3 residue notes stand.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=NONE
