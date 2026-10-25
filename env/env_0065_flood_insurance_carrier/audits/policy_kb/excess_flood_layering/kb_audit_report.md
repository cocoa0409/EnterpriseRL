# KB-doc policy audit — env_0065 / excess_flood_layering (product `excess`) — round 1

Auditor: KB-audit agent, round 1, 2026-10-17. Independent of the renderer and of the policy-side auditor. No artifact was edited.

## Step 0 — entry conditions (cited, not re-run)
- Policy-side verdict (brief): `VERDICT revision_8: task0=PASS task1=PASS / charter=CLEAN`.
- Gate snapshot `.audit_views/kb/excess_flood_layering/snapshot_kb1.txt` (2026-10-17T14:05:15Z):
  - check_docs excess: `DOCS OK` (docs=51; roles factor 23 / baseline 4 / facet 8 / policy 12 / hub 4).
  - post-publication check_traceability: `TRACEABILITY OK` (0.json 15/0, 1.json 13/0).
  - extended / task_tools / replay / solvability / compute / grounding / cross_fire: OK.
- `validate_scenario` reads INVALID in the snapshot. That is consistent with other difficulties' docs being unpublished; it is not an entry gate of this skill. Recorded only.
- Docs last modified 14:03:47, before the snapshot. Concatenated `docs/excess/*.json` sha256 at audit time: 89045b0a…a3cf. Charter mtime 13:10:03.
- Runtime views: 0.runtime.json sha256 fc423f8a…69cf1 and 1.runtime.json sha256 40d1ee0b…ef074, both matching the snapshot. DB access only through `db_query.py`, so the blind phase was blind on the DB side.

## Per-task verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Files |
|---|---|---|---|---|
| 0 (to-value limit increase ← renewal booking) | PASS | PASS | PASS | `runtime_context/excess_flood_layering/0.md` (+ `0.freeze.sha256`), `policy_kb/excess_flood_layering/0.md` |
| 1 (sale cancellation ← loss-of-use payment) | PASS | PASS | PASS | `runtime_context/excess_flood_layering/1.md` (+ `1.freeze.sha256`), `policy_kb/excess_flood_layering/1.md` |

- Both blind answers were frozen before any source read. All 8 scored arguments of the 4 writes match GT exactly: 1503.36; 1450000 / 2026-10-01 / 175.93 / 1679.29; 11898.50; 2026-09-15 / 1588.38. Every factor tier and both fall-backs match too: 1795.00, 182.56, 71459.46, 1742.32.
- Both prerequisite hops are state-derived from the verbatim sentence, the depended-on hub's own wording and the records. No hop was pre-solved.
- Cross-product: task 1's HomeFlood Premier loss-of-use limit (50,000) is published in `docs/homeflood`, so nothing is CONDITIONAL. Task 0's NFIP Dwelling reads are record fields only and need no unpublished doc figure.

## KB defects
None.

## Source-side findings (not KB-translation defects; they do not change the KB verdicts)

**SRC-1 (medium). Parameter meanings restate, unscoped, base content that an overwrite retired or scoped. The KB tier-table docs carry them faithfully as in-force statements that contradict the extended rules.**

The class is "retired base clauses still carrying in-force content". The overwrites retire the base clauses, but the parameter_schema meanings were not brought into line:

| Parameter meaning (source) | Rendered in | Contradicts | Bears on |
|---|---|---|---|
| `loss_of_use_limit`: "Additional living expense limit, paid from the first dollar because NFIP primary policies carry none" | `claim_terms_f5e85733`: "Loss-of-use coverage is paid from the first dollar, because NFIP primary policies carry none." | `excess_ext_loss_of_use_payment` overwrite of the first-dollar clause and factor `primary_lou_offset` (HomeFlood tier limit / 10% other carrier) | task 1 (HomeFlood-offset tier) |
| `minimum_earned_premium_pct`: "fully earned once the policy is bound, whatever the cancellation date"; `cancellation_refund_method`: "Method for returning premium on an insured's cancellation" | `return_premium_terms_e158daf4`: the row text, plus "'Pro rata with minimum earned' is the single return method of every tier: ... never less than the 25 percent share fixed at binding" | sale-cancellation overwrite ("in place of the base pro rata method with minimum earned premium") and factor `tenure_minimum_waiver` (nothing / 10%) | task 1 (10% tier). Reading the 25% floor here gives 1529.50 instead of 1588.38. |
| `no_refund_after_paid_claim`: "term premium is fully earned when a claim in the term has been paid" | `return_premium_terms_e158daf4` row | sale overwrite of the paid-claim bar (the latest-DOL paid claim with DOL ≥ term start, net of voids) | sale cancellations generally (not decisive in task 1) |
| `standard_waiting_days`: "... and for mid-term increases" | `servicing_periods_df0e8765` row | `excess_ext_limit_increase_premium` overwrite and factor `signing_window` (flat as of the term start) | task 0 (flat tier) |

At runtime the unique answer still holds. The hubs say "in place of ...", the base docs mark the clauses "no longer in force", and the specific factor docs govern; my own blind pass reached GT without hesitation. But the corpus carries, in a second document, unscoped content the source has retired. The root is on the policy side: parameter meanings are not covered by overwrite hygiene.

**SRC-2 (low). A rule sentence contradicts two of the same rule's reads.**
- `excess_ext_renewal_term_premium` rule: "The NFIP policy of the home is ... and the HomeFlood policy of the home is ...; **only their claim files and certificates are read**."
- But the occupancy tier reads the NFIP policy's primary-residence designation, and the account tier reads the existence and status of those policies. Neither is a claim file or a certificate.
- The KB carries the sentence verbatim in `account_relationship_04b08679` (whose own tier reads policy existence) and `loss_history_878a2e03`. `residence_designation_9e089e6c` omits it.
- No scored value changes. It is a literal self-contradiction a careful reader may stumble on.

## Observations (no action requested)
- **O-1, policy side.** Task 1's all-factor-free fall-back lands on an exact half-cent tie: 2323.10 × 0.75 = 1742.325. Compute gives 1742.32 (float); a decimal half-up reading gives 1742.33. The KB says only "rounded to the cent", with no tie rule. No scored value sits on a tie: 1503.36, 175.9296, 1679.2896, 11898.5007, 1588.3762.
- **O-2, seed realism, for the cross-product re-judge.** Task 1's HomeFlood records are skeletal. HFL-4825561 (Premier, cancelled PROPERTY_SOLD 2026-08-28) has no claim file and no billing, although the excess file records its settlement HFC-4402173 (995,000 building / 180,000 contents); the new-home HFL-4917380 also has no billing. Task 0's NFIP policy likewise has no billing rows. Nothing read depends on these, but a reviewer would expect the underlying claim on the HomeFlood file.
- **O-3, accepted form.**
  - The source's generic assembly sentences are rendered into each factor doc of their group: renewal net adjustment ×5, increase loading ×3, LOU order ×4, sale retention/charge ×2, days removed ×1. They name only baseline quantities and no sibling factor, so this is not KB-EXPLICIT.
  - The factor docs' "otherwise = baseline" tiers are written as "not set by this provision", "not on this schedule" or "not waived". That keeps the computation doc unreferenced and is equivalent.
- **O-4, realism, positive.** The seeded histories are produced by the extended rules themselves:
  - task 1's 2026 renewal premium 2323.10 (net +13%) and the three prior loss-of-use payments (2,500 / 14,710 / 14,760);
  - task 0's February endorsement (191.88 = 345 × 203/365) and the renewal offer and payment (1795.00 / 2061.70).
  - Surplus lines tax 6% with no stamping fee matches South Carolina.

## Closing checklist
- [x] Audit files map one-to-one to tasks 0 and 1 (revision_1). Blind answers are frozen with hashes before the reveal.
- [x] Every normative atom of the four extended policies and their base policies is entailed by `docs/excess`. Overwrites: 6 retired surfaces, each written as retired with the in-force remainder, and nothing retired that was not declared.
- [x] Both prerequisite sentences are verbatim, in state form, in the blocked hub only, and each hop is resolvable from the depended-on hub plus records. No other problem's tool name, route or aggregated chain appears anywhere.
- [x] All 23 factor ladders are carried in full, every tier exact, each in its own document, findable from record words. Cross-product products are named by official name.
- [x] check_docs and check_traceability as cited in the coordinator snapshot. The docs are unchanged since then (mtime 14:03:47 < snapshot 14:05:24), so I did not re-run them.

KB VERDICT round 1: task0=PASS task1=PASS
kb=CLEAN
src=SRC-1,SRC-2

## revision_2 — re-audit round 2 (2026-10-17)

### Gate and entry
- Gate first: `_difficulty.md` tail reads `VERDICT revision_9: task0=PASS task1=PASS` / `charter=CLEAN`. The newest docs/excess file (14:55:46) is newer than `excess.extended.yaml` (14:52:28). PASS.
- I ran these myself:
  - `check_docs.py env/env_0065_flood_insurance_carrier excess`: `DOCS OK` (51 docs; factor 23 / baseline 4 / facet 8 / policy 12 / hub 4; 2 prerequisite edges; mechanical gates PASS). The "required document not found" lines belong to other difficulties and were filtered out.
  - `check_traceability.py …/tasks/excess_flood_layering`: `TRACEABILITY OK` (0.json 15/0, 1.json 13/0).
  - `mkruntime.py excess_flood_layering`: views re-made with sha256 identical to round 1 (fc423f8a…, 40d1ee0b…).
- Docs sha256 (concatenated) is now 3f868203318c0653…. 45 docs are byte-unchanged since round 1. Re-rendered: account_relationship, certificate_source, loss_history, residence_designation, claim_terms, return_premium_terms.

### Round-1 items
- **SRC-2: closed.**
  - Source rule now reads "of these two policies only their status, the NFIP policy's primary-residence designation, their claim payments and voided payments and the NFIP policy's applied Elevation Certificates are read". This agrees with every read of the account, occupancy, loss-history and certificate tiers and with compute.
  - The old sentence is gone from all docs (grep "only their claim files": 0 hits). The new sentence is carried verbatim in account_relationship, certificate_source, loss_history and residence_designation.
- **SRC-1:** logged BLUEPRINT-KNOWN by the coordinator. Not re-raised; no scored value changes. The re-render made the two base tier tables carry the parameter meanings verbatim as row labels and dropped the derived unscoped restatements, which is less pull toward the wrong reading.
- KB items from round 1: none (kb=CLEAN).

### No new defect, nothing regressed
- Per-task re-checks (`runtime_context/…/0.md`, `1.md`, `policy_kb/…/0.md`, `1.md` under revision_2): KB-RUNTIME, KB-BIJECTION and KB-EXPLICIT all PASS.
- Seeded worlds, prerequisites, ladders, overwrites, baselines and GT are unchanged. The 8 scored arguments are the same as round 1.
- Both prerequisite sentences are still verbatim in their blocked hubs only, and tool names appear only in their own hubs.
- The re-rendered docs add no claim and name no sibling factor or tool.
- Observations O-1 (half-cent tie in task 1's fall-back), O-2 (skeletal HomeFlood/NFIP billing and claim rows) and O-3 (accepted assembly form) still stand. No action requested.

KB VERDICT round 2: task0=PASS task1=PASS
kb=CLEAN
src=NONE

## revision_3 — cross-product re-judge, round 3 (2026-10-17)

### (3) Corpus and charter unchanged since round 2
- `docs/excess` is byte-identical to round 2 (concatenated sha256 3f868203318c0653…; 51 docs; newest 14:55:46).
- `excess.extended.yaml` (14:52:28), `task_tools.py` and `tasks/*.json` (14:52:38) are unchanged.
- I re-ran, execute-only:
  - `check_docs.py … excess` → `DOCS OK`;
  - `check_traceability.py …/tasks/excess_flood_layering` → `TRACEABILITY OK` (0.json 15/0, 1.json 13/0).
- All seven products are now published: bizflood 21, dwelling 74, excess 51, forceplaced 59, homeflood 68, nfipcom 65, parametric 15.

### (1) Cross-product hops and figures, against the final docs
| Task | Hop / figure | Owning product's final doc | Result |
|---|---|---|---|
| 0 | NFIP policy of the home: status `in_force`, same policy number | dwelling status vocabulary (in force / renewal grace / lapsed / cancelled) | holds |
| 0 | certificate_source: latest **applied** EC (2021-03-02), LFE − BFE | `dwelling/elevation_certificate_rerating_rule`: applied vs "kept on file as not applied" | holds; 0.85 |
| 0 | loss_history: NFIP **building** payments; primary_loss_recency: any coverage | `dwelling/loss_settlement_basis`, `mortgagee_rights` (building vs contents items) | holds; +10 / 10 |
| 0 | residence_designation / zone surcharge: NFIP primary_residence, flood_zone | `dwelling/occupancy_tiers_and_coverage_limits` (Primary Single-Family Home = primary residence) | holds; −3 / 5 |
| 1 | sale scope / closing date: HomeFlood cancelled PROPERTY_SOLD, effective 2026-08-28 | `homeflood/insured_cancellation_and_refund_terms` C2 (property sold → closing date) | holds |
| 1 | primary_lou_offset: HomeFlood Premier loss-of-use limit | `homeflood/additional_coverages_and_settlement_terms`: Premier 50,000 | holds; 50,000 |
| 1 | underlying_expiry_cut: declarations expiry 2027-06-25 (HomeFlood term end, same date) | HomeFlood record term 2026-06-25→2027-06-25 | holds; 6 days |

Nothing is CONDITIONAL any more. Both tasks remain PASS on all three relationships.

### (2) Seeded cross-category rows vs the owning product's published rules
Read only through `db_query.py`.

**Producible (consistent):**
- **Task 0 NFIP 4400918275:**
  - The Primary Single-Family Home tier matches primary_residence True. Building 250,000 meets the RC test (lower of 80% × 1.7M and the 250,000 statutory maximum), so losses settle at replacement cost.
  - Building payments: 11,850 − 2,000 = **9,850** and 38,400 − 2,000 = **36,400**. Each is ≤ its sworn proof of loss, which was received within 60 days of the loss (20 and 57 days), and each was paid within 60 days of it.
  - Contents: ACV 6,900 − 2,000 = **4,900**.
  - Payees: building INSURED_AND_MORTGAGEE (mortgage required, Seaboard Coastal Bank), contents INSURED alone.
  - Deductibles 2,000/2,000 are electable defaults. Status in_force, zone AE, mortgage required.
  - The 2021 EC is applied, which matches ec_on_file True and first_floor_height 3.1. The 2019 EC is not applied. FFH 3.1 differs from LFE − BFE 2.6, which is realistic: they are different EC quantities.
  - The contents payment has no contents proof of loss, but the dwelling rule allows payment on an adjuster's report signed in lieu: FINAL report 2024-09-18, paid 63 days later (≤ 90).
- **Task 1 HomeFlood HFL-4825561 (Premier):**
  - RCV 3.1M ≥ 400,000; dwelling 1,000,000 inside 250,000–2,000,000; personal property 250,000 ≤ 500,000.
  - Deductible 5,000 is a Premier option and ≤ 10,000, so it keeps the compliance aid statement.
  - credits_applied_pct 5 = the Premier package credit (5): an active Excess Flood policy at the address on the 2026-06-25 term start, claims-free not met because of the 2025-10-03 loss.
  - Cancelled PROPERTY_SOLD effective on the closing date, as C2 requires.
- **Task 1 HomeFlood HFL-4917380 (Plus, new home):**
  - RCV 640,000; dwelling 600,000 ≤ RCV and within 100,000–1,000,000; personal property 150,000.
  - Deductible 2,500; LENDER_ESCROW; mortgage required with the statement.
  - LOAN_CLOSING basis with application 2026-08-20 ≤ closing 2026-08-28, effective on the closing date.

**Not producible, so this is a seed-side finding:**

**SRC-3 (medium, realism). Cross-category states the excess tasks read are present without the trace rows the owning product's published rules always write with them.** No scored value moves.
1. *Task 1, HomeFlood cancellation.*
   - HFL-4825561 is `cancelled` / PROPERTY_SOLD / effective 2026-08-28 / closed 2026-09-03.
   - But `find_homeflood_requests` and `find_homeflood_billing` return nothing for the customer.
   - Under `homeflood/signed_cancellation_processing` and C1, a cancellation is processed only when the named insured's signed request is on file. Processing books one CANCELLATION credit of the term premium item referenced to that request, and C7 sets it against the balance and refunds the remainder.
   - So the cancelled state cannot exist without a signed request row and a credit row. The 6,412.00 term also has no premium or payment rows.
   - This record is load-bearing for task 1: the sale scope and the sale closing date in four factors.
2. *Task 1, HomeFlood claim.*
   - The excess file records underlying claim HFC-4402173 and an underlying settlement of 995,000 building / 180,000 contents (2026-01-28).
   - But `find_homeflood_claims` is empty: no report, proof of loss or payment.
   - Also, under `homeflood/claim_settlement_basis` the dwelling fails the insurance-to-value test (1,000,000 < 80% × 3,100,000), so it settles at actual cash value with the deductible taken from the loss before the cap. The 995,000 figure is producible only if the ACV dwelling loss was exactly 1,000,000, and no HomeFlood adjuster report exists to show it.
3. *Task 0, NFIP certificate and billing.*
   - The 2021-03-02 EC is `ec_applied` True.
   - Under `dwelling/elevation_certificate_rerating_rule`, an applied certificate is credited as re-rate components (risk, ICC, Reserve Fund Assessment) from the receipt date.
   - `find_dwelling_billing` returns nothing at all: no re-rate credits and no premium or remittance rows for a policy rated at 1,842 + 63 + 50.
   - The applied flag is load-bearing for task 0 (certificate_source → 0.85).
- Effect: none on any scored figure. Every read field is consistent with the published rules, as the table above shows. But a careful agent or reviewer looking at the owning product's file finds an account history those rules could not have left behind.

### Round-2 verdicts
All still hold. SRC-2 stays closed. SRC-1 remains BLUEPRINT-KNOWN and is not re-raised. Observations O-1 and O-3 are unchanged. O-2 is now judged and superseded by SRC-3.

KB VERDICT round 3: task0=PASS task1=PASS
kb=CLEAN
src=SRC-3

## revision_4 — seed-only confirm, round 4 (2026-10-17)

### Gate and freeze
- `_difficulty.md` tail reads `VERDICT revision_10: task0=PASS task1=PASS` / `charter=CLEAN`.
- `excess.extended.yaml` sha256 1a06fa0f8f9beb85… and `task_tools.py` sha256 8c315e853830b65a… are byte-identical to `/tmp/erl0065_coord/seedonly_freeze.sha256`.
- `docs/excess` is byte-identical to rounds 2–3 (3f868203318c0653…), so no re-render is needed.
- I ran, execute-only:
  - `check_docs … excess` → `DOCS OK`;
  - `check_traceability …/tasks/excess_flood_layering` → `TRACEABILITY OK` (0.json 16/0, 1.json 17/0; the counts rose with the added read actions);
  - `mkruntime.py excess_flood_layering` → views unchanged (fc423f8a…, 40d1ee0b…).

### SRC-3 — closed
All checks below used `db_query.py` only, against the published owning-product rules.

1. **Task 1, HomeFlood cancellation.**
   - The signed request is now on file: `homeflood_requests` fcfbdab7…, CANCELLATION / PROPERTY_SOLD / requested effective 2026-08-28 / SETTLEMENT_STATEMENT / SIGNED, created 2026-09-03 (= closed_date).
   - A CANCELLATION credit of the term premium item, 17.50, was posted 2026-09-03 referencing that request. A refund of 17.50 went to the INSURED on 2026-09-08, matching premium payor INSURED (C7).
   - Recomputed under `homeflood/cancellation_earning_basis`, `paid_claim_share_of_return`, `loss_of_use_charge_return`, `policy_fee_return_on_cancellation` and `cancellation_exit_fee`:
     - The earning basis is pro rata (property sold with a settlement statement).
     - Claim payments for the 2025-10-03 loss (11 whole months before 2026-09-03) total 1,230,000. That is ≥ 25% of 1,250,000, so the premium-return share, including the loss-of-use part, is nothing.
     - Policy-fee return: 64 days after the term start, with 9 whole months left, gives 17.50.
     - Exit fee: 62 whole months in force, so none.
     - Credit = **17.50**. ✓
   - Premium history (now seeded):
     - The base before credits is 2,457.56 + the 160 loss-of-use charge, which gives the 2021/2022 terms 2,617.56 with no credit. The excess policy only became effective 2022-07-01, and the claims-free history was under 3 years.
     - 2023 is 2,494.68 (package 5%). 2024 and 2025 are 2,371.81 (package 5 + claims-free 5). 2026 is 2,494.68 (package only, after the 2025 loss).
     - This matches credits_applied_pct 5 and term_premium 2,494.68 on the record. The policy fee is 35, and each term's payment equals its charges.
2. **Task 1, HomeFlood claim HFC-4402173.** It is now on the HomeFlood file.
   - Reports: PRELIMINARY 2025-10-17, then FINAL 2025-11-19 (dwelling RC 1,265,000 / ACV 1,086,400; contents RC 180,000), then SUPPLEMENTAL 2026-04-08 (loss of use 71,900).
   - Proofs of loss on 2025-11-28 (56 days after the loss, within 60): dwelling 1,000,000, personal property 180,000.
   - Dwelling: the insurance-to-value test fails (1,000,000 < 80% × 3,100,000), so ACV applies. 1,086,400 − 5,000 is capped at the limit, giving **1,000,000**, paid to the insured alone (no mortgagee).
   - Personal property: Premier replacement cost, with the deductible already exhausted, gives **180,000**.
   - Loss of use: 28,400, then 21,600, reaching the Premier limit of 50,000 within 12 months.
   - The excess file's underlying-settlement record now reads 1,000,000 / 180,000, consistent with these payments. The excess building payment of 265,000 (1,265,000 − the 1,000,000 attachment) is unchanged.
3. **Task 0, NFIP 4400918275.** The ledger is now seeded for terms 2019–2026: RISK, ICC, Reserve Fund (18%), HFIAA 25, Federal Policy Fee 50, and escrow payments that equal the charges. The 2026 figures 1,842 / 63 / 342.90 / 25 / 50 match the policy's rated figures.
   - The applied 2021-03-02 EC re-rated 2,310/75 to 1,620/63 on the 2020-05-15 term. With 74 days left of 365:
     - RISK 690 × 74/365 = **139.89**;
     - ICC 12 × 74/365 = **2.43**;
     - RFA 18% of 142.32 = **25.62**.
   - All three are posted as RERATE credits referencing the EC, with the refund of 167.94 to LENDER_ESCROW.
   - The 2019 EC re-rated higher (2,295 + 75 vs 2,240 + 75), so it is not applied, as the rule requires.
   - Renewal offers equal the booked risk premiums.

### Runtime path to scored values
- Every field the excess computations read is unchanged in both worlds: values, dates and statuses.
- GT write arguments and baselines are identical: 1503.36; 1450000 / 2026-10-01 / 175.93 / 1679.29; 11898.50; 2026-09-15 / 1588.38. The fall-backs 1795.00 / 182.56 / 71459.46 / 1742.32 are also identical.
- GT gained only read actions (find_dwelling_billing, find_homeflood_requests/claims/billing/changes), each with "No figure is taken from it". Scoring compares write effects plus the prerequisite order (`erlbench/scoring.py`), so these reads add no scored step.
- No new KB or source defect. SRC-1 stays BLUEPRINT-KNOWN, and SRC-2 stays closed.

KB VERDICT round 4: task0=PASS task1=PASS
kb=CLEAN
src=NONE
