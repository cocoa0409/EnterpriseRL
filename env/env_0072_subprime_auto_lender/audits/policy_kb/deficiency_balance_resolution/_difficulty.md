# KB-doc policy audit — deficiency_balance_resolution (product `deficiency`, Deficiency Balance Accounts), M=2

## round 1 (2026-10-20)

### Entry conditions (cited, checked)
- Policy-side verdict: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN` (audits/policy_task/deficiency_balance_resolution/_difficulty.md, as supplied in the brief).
- Coordinator gate snapshot 2026-10-20T11:39:11: DOCS OK; TRACEABILITY OK, 0 misses; EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK. Hashes match on disk: deficiency.extended.yaml 9b65506c94b87f8c2288c8aca3a7d419ae36317625ec57b37342f0c6fbe04f9e; task_tools.py da468bc401b602144ae484eef713d03a9688373b414a43a0c9a6a6ad4e520dd1.
- Re-run by this audit (`/tmp/erl0072_coord/kb_snapshot.sh deficiency_balance_resolution deficiency`, 2026-10-20T11:51:40): check_docs DOCS OK; traceability TRACEABILITY OK, misses 0; check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK; same two source hashes.
- Runtime views 0/1.runtime.json hashes match the brief (3e1bfee2…afec, 10547552…3aa). DB side blind (db_query.py share reads only). No contamination: blind answers frozen (sha256 0.md 292f56c3…c5a7f, 1.md e0b3e45b…c057d) before any source file was opened; no grep over tasks/ or audits/.

### Per-task part verdicts
| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 (Renata Szabo; restart down payment → plan offer) | PASS — blind 336.34 / 122.41, tree and order identical to GT | PASS | PASS |
| 1 (Marcus Thornbury; lump-sum offer → acceptance → start) | PASS — blind 3797.68 + unemployment_determination / 5361.92 / 1340.48, tree identical | PASS | PASS |

Fall-back numbers (computation document alone) are definite and differ: task 0 558.22 (restart) / 131.15 (plan); task 1 3675.18 / 4614.39 / 893.66. Every one of the 27 factor documents of the five policies was reached from the customers' record words; none is referenced by a computation document or another factor.

### KB defects
None. kb=CLEAN.

### Source-side items (KB cannot fix) — exhaustive list
- **S1 — parameter label carries the retired installment basis.** `parameter_schema.plan_min_payment_pct_of_balance` = "Minimum monthly plan installment as a percent of the balance on the acceptance date (the installment is the greater of this and plan_min_monthly_payment_usd, rounded up to the cent)". This is the content of the base clause that `deficiency_ext_plan_installment.overwrite` retires (current basis: the balance on the day the offer is made, the greatest of three figures, then the adjustment schedules). The KB carries the label faithfully and unmarked as a row label of payment_plan_terms_schedule_42c5e759, so the corpus states the retired basis as a live term next to the retirement marker in payment_plan_rules §4. Not gold-moving here: plan_offer_recording_535b6a7f says "in place of the greater of the two minimums on the balance on the acceptance date" and its Q&A settles the day. Only member.
- **S2 — seeded voluntary surrender fee not producible by the published recovery rules (task 0).** Recovery case 4178ae4a… (Class 1, TX, voluntary_surrender, opened 2025-07-21, recovery 2025-07-23, lot "Bayou City Vehicle Storage", book value 12,600.00) carries expense `voluntary_surrender_fee` 150.00. Published current basis: surrender_fee_charge_basis_f5e1bdb8 (class fee 150.00, limit first, then reductions and credits, floor 25.00) + state_limits_on_surrender_fees (TX: none) + surrender_fee_vehicle_value_reduction (≥10,000: none) + prompt_surrender_timing_credit_31307d4f (came in 2 days after the opened date → credit 30.00) + company_dropoff_lot_credit (not a drop-off lot: none) → 120.00. The base posting line "the voluntary surrender fee for voluntary surrender" is retired in recovery_expense_charging_rules. Flows on: expenses 1,460.00 → 1,430.00, net proceeds 2,890.00 → 2,920.00, original deficiency 6,768.93 → 6,738.93 (with S3 also: 6,722.47), notice stated amount 1,239.38 → 1,209.38, account balance and both task-0 gold values move (still Band 3; tiers unchanged). Only member (task 1's involuntary agency fee 425.00 is reproduced exactly: OH limit 550 not binding, book value ≥12,000, key-replacement posted, Tuesday recovery).
- **S3 — seeded contract late charges not producible by the published contract late-charge rules (tasks 0 and 1).** late_charge_amount_computation_6b51eac6 (current basis; the base "lesser of percent and cap" amount clause is retired in late_charge_eligibility_and_limits) applies combined reductions before the cap: autopay_late_charge_relief_d2dbc562 and first_delinquency_late_charge_relief_b205986e. Members:
  - task 0, contract 3d18332a…, late charge 2025-06-26 for installment 2025-06-15, seeded 23.52: 11 autopay drafts in the rolling 12 months (20%) + no late charge in 12 months (50%) → 470.43 × 5% × 30% = 7.06.
  - task 1, contract e748dc51…, late charge 2025-07-01 for installment 2025-06-20, seeded 25.00: autopay 11 (20%) + none prior (50%) → 562.31 × 5% × 30% = 8.43.
  - task 1, late charge 2025-07-31 for installment 2025-07-20, seeded 25.00: not bookable at all under late_charge_booking_9b8681f7 / late_charge_eligibility ("booked on the oldest unpaid installment … the one due on the contract's next due date"; one per installment due date) — the oldest unpaid installment was 2025-06-20, already charged. (Were it bookable, autopay 10 (20%) + one prior (25%) → 15.46.)
  Flows on: sale-proceeds fees applied, principal applied, original deficiency (task 1: 9,925.46 → 9,883.89 with only the one charge of 8.43; task 0: 6,768.93 → 6,752.47), notice stated amounts (1,239.38; 2,561.93), balances, and every gold value of both tasks (task 1 premium reads the original deficiency directly). Bands unchanged.
- **S4 — advisory realism, conditional on `cpi` (not yet published).** Background: "Every financed vehicle has an insurance tracking record under the Collateral Protection Insurance program". Neither customer has a cpi_coverages row (find_cpi_coverages returns none for 5a10de2f… and 4f79125b…). No deficiency figure depends on it (no CPI refund credit on either account); non-scoring.
- **S5 — hardship-document bootstrap: the seeded first hardship-bearing offers are not producible by the published lump-sum rule (tasks 0 and 1).** lump_sum_hardship_reduction (source rule of deficiency_ext_lump_sum_settlement) grants a reduction, and records a hardship document, only from documents carried by the account's arrangement offers dated within the look-back; no published policy or tool records a hardship document otherwise (the plan tool always records none). Members:
  - task 0, offer 52b0fb8c… (lump-sum, 2025-11-05, medical_disability_statement, 3,547.22): no earlier offer existed; the published rule gives 6,568.93 × 59.0% = 3,875.67 with hardship none. The seeded 3,547.22 = 3,875.67 − 328.45 (5.0% of the balance) applies the reduction from the document the offer itself introduces.
  - task 1, offer a8193c4d… (lump-sum, 2025-11-12, unemployment_determination, 4,720.02): the only earlier offer (plan 2025-10-28) carries none; the published rule gives 9,525.46 × 59.0% = 5,620.02, hardship none. The seeded 4,720.02 = 5,620.02 − 900.00 (6 × 150.00).
  These rows are the evidence for task 0's restart hardship relief (3.0 points) and plan basis row 1, and for task 1's lump-sum hardship reduction and the gold `hardship_document`. (All other seeded deficiency offers — task 0 plan 2025-12-01 140.96 × 47; task 1 plans 2025-10-28 239.33 × 40 and 2026-01-20 152.10 × 60 — reproduce exactly under the published plan rule given these rows.)
- Cross-category rows checked and consistent with the published contract and recovery docs: installment interest/principal splits; sale-proceeds waterfall (expenses first, then contract: interest 667.10 / 1,284.75 at actual/365 for 97 / 120 days, fees, principal) and balance transfer = original deficiency; storage 26 × 25.00 and 20 × 30.00 (2 free days); transport, key replacement, reconditioning within caps, auction fees by class; notice of intent to sell mailed 1 day after recovery with a 15-day sale period (no late-mailing, servicemember or funds days apply; TX/OH base 15); post-sale explanations mailed 5 days after sale stating the original deficiency; no late charge after repossession.

### Policy-side notes (no verdict effect)
- N1 — plan_offer_recording renders the replaced_by phrase "by the standard method and the adjustment schedules of this policy" as "by the method of this policy"; every schedule is carried in its own factor document, so the entailed results are unchanged.
- N2 — the depended-on restart rule's own first sentence ("…the restart down payment that a new payment plan requires…") names its consumer; carried as source text.
- N3 — every computation's source assembly sentence ("the percentage adjustments of the schedules that apply…", "any reduction amount a schedule sets…", "the installment cuts … and the installment additions…") tells a reader that modifiers exist; rendered verbatim as the source's baseline assembly, so not a KB finding.

### Closing checklist
- Audit files 1:1 with tasks: runtime_context/deficiency_balance_resolution/{0,1}.md, policy_kb/deficiency_balance_resolution/{0,1}.md (revision_1, no earlier revision).
- Every normative atom of the difficulty's source is entailed by docs/deficiency; three prerequisite sentences verbatim on their blocked sides only; every hop state-derived; every factor ladder complete and findable; no tool name, route or aggregated chain beyond the sentences.
- Gate lines re-run and on record above.

VERDICT kb_round1: task0=PASS task1=PASS kb=CLEAN src=S1,S2,S3,S4,S5

## round 2 (2026-10-20)

### Entry conditions
- Gate: `tail -1 audits/render_source/deficiency_balance_resolution/RENDER.log` = `RENDER round 3: DOCS OK`; `tail -1 audits/policy_task/deficiency_balance_resolution/_difficulty.md` = `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`. (An earlier round-2 call was BLOCKED on `RENDER round 2: DOCS OK` / `revision_6 … charter=R-HANDIN`.)
- kb_snapshot 2026-10-20T20:03:33: DOCS OK; TRACEABILITY OK, misses 0; EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; deficiency.extended.yaml cb8adfadaaae06e0eac6fbfb43f9ccf408ad99619dc3c8db72651cf61397c1ea; task_tools.py efdae9f34fd8cf640add14f9e2eeda01e6f99f230956c90f1d9bb7f801a2ba27.
- Runtime views re-hashed: unchanged (0: 3e1bfee2…afec; 1: 10547552…3aa). Fresh blind derivation over the re-priced worlds frozen before reveal (runtime_context 0.md 050cd82d…08ad7, 1.md 6d3f9ff6…f65937).
- **Input note:** 1.runtime.json is stale against tasks/1.json — the task's user_scenario gained "If asked whether you have any new hardship paperwork to hand in today, you say no" (rework round 6). The blind answer had assumed no document handed in today and shown the result is identical either way; no verdict effect, but the view should be rebuilt before any further round. 0.runtime.json matches tasks/0.json.

### Per-task part verdicts
| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS — blind 333.96 / 121.54 = GT; tree and order identical | PASS | PASS |
| 1 | PASS — blind 3779.65 + unemployment_determination / 5337.02 / 1334.26 = GT; tree identical | PASS | PASS |
Fall-backs remain definite and different (task 0: 554.27 / 130.22; task 1: 3657.73 / 4592.48 / 889.51).

### Round-1 source items
- S2 closed: task 0 voluntary surrender fee now 120.00 (= 150.00 − 30.00 prompt-surrender credit; TX no limit; book value ≥ 10,000; not a drop-off lot); expenses 1,430.00, net 2,920.00, sale-proceeds split 667.10 / 7.06 / 2,245.84, transfer and post-sale explanation 6,722.47, notice stated amount 1,192.92 all follow.
- S3 closed: late charges 7.06 (task 0, 2025-06-15 installment) and 8.43 (task 1, 2025-06-20 installment) = 5% of the scheduled installment × (100 − 20 autopay − 50 first-delinquency)%; task 1's second charge removed (oldest unpaid installment already charged); task 1 sale-proceeds split 1,284.75 / 8.43 / 5,151.82, transfer and explanation 9,883.89, notice stated amount 2,520.36.
- S5 closed: the published rule now records a handed-in document and reads only offers already recorded; the seeded first hardship offers reproduce exactly — task 0 2025-11-05: 6,522.47 × 59.0% = 3,848.26, no reduction, records medical_disability_statement; task 1 2025-11-12: 9,483.89 × 59.0% = 5,595.50, no reduction, records unemployment_determination.
- S1 (BLUEPRINT-KNOWN) and S4 (advisory) dispositioned by the coordinator; still present, not re-raised.

### Exhaustive cross-product seed pass (both worlds; published contract, recovery; cpi/gap still unpublished and no rows exist for either customer)
Every row reproduces: 23 + 14 installment interest/principal splits at actual/365 (0 mismatches); late charges and their absence after the first per delinquency/after repossession; task 0 surrender fee, transport 125.00, reconditioning 240.00, storage 26 × 25.00, auction 295.00; task 1 agency fee 425.00 (OH limit 550 not binding, book ≥ 12,000, key replacement posted, Tuesday recovery), transport 150.00, key replacement 250.00, reconditioning 480.00, storage 20 × 30.00, auction 350.00; expense settlements; proceeds order and splits (interest 97 / 120 days); balance transfers = original deficiencies = post-sale explanations (mailed 5 days after sale); notices of intent mailed 1 day after recovery with 15-day sale periods (TX/OH base, no additions) and reinstatement amounts as stated; deficiency history (plans 139.97 × 47; 238.29 × 40; 151.40 × 60; returns, breaks, balances 5,542.68 and 8,128.29). Unproducible members: none.

### KB defects
None. kb=CLEAN.

VERDICT kb_round2: task0=PASS task1=PASS kb=CLEAN src=none

## round 3 (2026-10-21) — cross-product re-judge, all seven products published

### Entry conditions
- kb_snapshot 2026-10-21T00:12:48: DOCS OK; TRACEABILITY OK, misses 0; EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; deficiency.extended.yaml cb8adfadaaae06e0eac6fbfb43f9ccf408ad99619dc3c8db72651cf61397c1ea; task_tools.py efdae9f34fd8cf640add14f9e2eeda01e6f99f230956c90f1d9bb7f801a2ba27 (both unchanged from round 2).
- Runtime views: 0.runtime.json 3e1bfee2…afec (unchanged, equals tasks/0.json); 1.runtime.json 73a3e9d0e4fa8ebce92fa4587c8bfedab42f9cb5094e561daaf3885162ac4917 (rebuilt; equals tasks/1.json — round-2 input note closed).
- Blind side refrozen before reveal (runtime_context 0.md 06e447d3…8cdc, 1.md 286bcc3e…a851); DB dumps byte-identical to round 2; deficiency corpus unchanged.

### Per-task part verdicts
| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS (333.96 / 121.54 = GT) | PASS | PASS |
| 1 | PASS (3779.65 + unemployment_determination / 5337.02 / 1334.26 = GT) | PASS | PASS |

### Conditional figures settled
- No deficiency figure in either task rests on cpi or gap: neither account has a credit row; the only CPI/GAP-sensitive atoms (refund credits) agree with the now-published cpi/gap/vsc destination rules (see 0.md/1.md revision_3). Nothing that was conditional changes a scored value.
- Round-1 S4 (missing CPI tracking records, conditional on cpi) is now settled against published text — see S4 below.

### Exhaustive cross-product seed pass (both worlds; contract, recovery, cpi, gap, vsc, dealer)
Reproduced (no action): contract tier, APR, term, amount and LTV at purchase (task 0 score 452 → Tier 6, 27.99% in 24.99–29.99, 48 ≤ 48, 13,500 ≤ 14,000, LTV 107.1% ≤ 110%, vehicle age 6 ≤ 12; task 1 score 497 → Tier 5, 25.99% in 21.99–27.49, 54 ≤ 54, 17,800 ≤ 18,000, LTV 112.7% ≤ 115%, age 7 ≤ 11); scheduled payments 470.43 / 562.31 (amortised), maturity dates; all 37 installment splits (actual/365); late charges 7.06 / 8.43 and no others; recovery referral (task 0 voluntary surrender; task 1 61 days past due ≥ 60), no right-to-cure notice (TX, OH not on the schedule), assignment-to-recovery within 60 days; every recovery expense, the agency fee and surrender fee with their factors, storage, expense settlement, proceeds order and splits, balance transfers, post-sale explanations, notices of intent (window, 15-day period, stated amounts); deficiency history and balances; no GAP addendum or service contract (optional products; no rule requires one).
Unproducible members — complete list:
- **S4 (settled; was advisory/conditional)** — cpi tracking_records_per_contract_c51d6880: "Every contract the company books opens one insurance tracking record on its contract date"; premium_cancellation_and_refund_rule_b37a0bda: "A tracking record closes when its contract leaves active servicing (… liquidated …), on the contract's closed date." Neither world has one (find_cpi_coverages / find_cpi_activities by customer and by contract: none). Members: task 0 contract 3d18332a… (record due from 2023-06-08, closed 2025-08-20); task 1 contract e748dc51… (from 2024-03-15, closed 2025-09-17). Non-scoring: a record showing the borrower's own insurance and no placed premium leaves every deficiency figure unchanged; only a placed premium refunded after liquidation would add a deficiency credit (and move paydown shares).
- **S6 (new; dealer was already published in round 1 and my rounds 1–2 passes did not cover it — recorded here honestly)** — contract_purchase_funding_and_unwind_6a315ae0: "A booked contract stays pending funding until the dealer clears every funding stipulation, and it moves to active when the dealer's initial funding is disbursed"; dealer contract_funding_99f9c172: "A contract is funded only to a dealer whose agreement status is active or on watch … A funding is recorded once per funded contract"; contract_tier_buying_matrix_0ee46bae (Tier 6 needs Dealer Program Gold or above, Tier 5 Silver or above). Both contracts carry dealer_agreement_id None and no dealer funding row (find_dealer_transactions by contract: none), yet both were serviced as active and paid installments. Members: task 0 contract 3d18332a… (contract date 2023-06-08); task 1 contract e748dc51… (2024-03-15). Non-scoring: no deficiency figure reads dealer records.
- S1 (BLUEPRINT-KNOWN) not re-raised. S2, S3, S5 stay closed.

### KB defects
None. kb=CLEAN.

VERDICT kb_round3: task0=PASS task1=PASS kb=CLEAN src=S4,S6
