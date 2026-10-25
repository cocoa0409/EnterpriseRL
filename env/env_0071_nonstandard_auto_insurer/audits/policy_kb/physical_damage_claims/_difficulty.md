# KB-doc policy audit — physical_damage_claims (physdam), difficulty close-out

## revision_1

### Entry conditions (Step 0, cited from the brief and re-run snapshot)
- Policy-side verdict: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN` (audits/policy_task/physical_damage_claims/_difficulty.md, that line only).
- Coordinator gate snapshot 2026-10-20T15:08:33 and auditor re-run of `/tmp/erl0071_coord/kb_snapshot.sh physical_damage_claims physdam` at 2026-10-20T15:18:21: check_docs physdam → DOCS OK; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK (rc=0); check_traceability → TRACEABILITY OK, 0 misses. Source sha256 unchanged (yaml f165003a…13db, task_tools 43a3e10b…2b54). 56 physdam docs.
- Runtime view and DB access path supplied; both blind audits were DB-blind (tool-shaped queries only). Input complete.

### Per-task part verdicts
| Task | Runtime blind audit | Two-way scan | Dependency form | Files |
|---|---|---|---|---|
| 0 | PASS — blind answer 4,975.50 / 450.00 / seq 2 then 29.36 equals GT; tree 1 hop, state-derived | PASS | PASS | runtime_context/…/0.md, policy_kb/…/0.md |
| 1 | PASS — blind answer 5,830.00 / 450.00; 294.25 / 478.75 / 33.00; 155.33 / 49 / 612.00 equals GT; tree 2 hops, state-derived | PASS | PASS | runtime_context/…/1.md, policy_kb/…/1.md |

Blind answers frozen before any source read: `runtime_context/physical_damage_claims/_freeze_revision_1.sha256` (0.md 1acd0199…dfbbe, 1.md 1760b305…29ced). No contamination.

### Closing checklist
- Audit files one-to-one with tasks 0 and 1; every comparison section PASS; revision_1 is the first revision (directories were empty).
- Every normative atom of the five extended policies (hub scope, overwrite replaced_by, baseline rules, all 28 factor ladders tier by tier, tool contracts) and of the governing base policies is entailed by the physdam docs; retired clauses (settlement ×3, recoveries ×1, premium_rule ×1, inspection_rule ×1) are each written as no longer in force; no KB-only retirement; no claim from outside the source.
- All three prerequisite sentences stand verbatim (exact-string check), state form, in the blocked hub only; every hop resolvable from the sentence + depended-on hub + records.
- Every tool name occurs only in its own hub's invocation block; no route, chain, cross-problem guidance or task-mirroring title.
- Coverage note: towing and rental corpora are outside this difficulty's scope (rental docs were read only as context for the rental factor's product name and authorisation semantics).

### Source-side items (reported separately; not KB defects)
- **S1 — undeclared override, variant parameter `loss_payee_paid_first` vs physdam_ext_lienholder_settlement overwrite (PLAUSIBLE runtime risk on task 1).** The parameter (true in all six variants; schema text "Whether a total loss payment goes first to the listed loss payee up to the payoff amount") is rendered as in force in total_loss_and_theft_schedule_18c42af2, "Further settlement terms, the same in every package": "Loss payee paid first. Yes: a total loss payment goes first to the listed loss payee, up to the payoff amount." The overwrite retires the base sentence carrying the same meaning ("it is paid first to the loss payee up to the payoff amount and the rest to the named insured") and replaces it with "the vehicle value … is paid in full to the loss payee, which applies it to its payoff and returns any excess to the named insured", but the parameter itself is not retired. Task 1 sits exactly on the divergent branch (vehicle value 5,830.00 > payoff 5,410.00): a reader applying the facet would cap the loss-payee payment at 5,410.00. I judged the visible solution still unique because the LP hub's "and only for such a loss … paid in full … returns any excess" is the specific rule, so no KB-RUNTIME RED; the conflict originates in the source and the KB renders both atoms faithfully.
- **S2 — baseline wording names factor-decided quantities (topology weakening, source form).** physdam_ext_totaled_coverage_return `baseline.rule`: "the minimum-earned percent of the full-term rate, times the time-in-force share …, times the tenure share …; at the standard … both shares are one". The baseline doc must carry it (coverage_return_figure_2319b995 item 5: "multiplied by the time-in-force share of the charge and by the tenure share of the charge. Each share is one"), and those terms are the vocabulary of minimum_earned_time_in_force_cccf3086 and minimum_earned_renewal_tenure_afa9bd7b, so the baseline tells a reader that those two shares can differ from one. Not a KB finding (verbatim source baseline); it lowers the discovery burden for two of the six return factors.
- Notes (no id): (a) the rental-part rule's "its authorisation with the latest entry date" is shared source/doc wording; the runtime finder returns the closing row (`rental_authorization_closed`, rate 0.00) in the same table with a later entry date; GT and the blind reading both take the `rental_authorized` row; (b) the owner-payment prerequisite sentence "more than a quarter of the declared actual cash value plus …" parses two ways (¼ of the sum, or ¼ of ACV plus the rest); outcome-independent on task 1's records; (c) tool name `remove_totaled_coverage_12b8272a` says "totaled" while its policy covers every requested removal; (d) seeds: no rule-vs-compute divergence (all 5 scored figures and 5 baselines reproduced from the docs alone); seed rows look realistic (duplicate-invoice rental reversal, second valuation report after the declaration, Altima substitution decoy); no cross-product row found that the owning charter would not produce (rental rows checked against the rental docs).

### Cross-product-pending (re-judge when auto, billing, fr, nonowner are published)
- Owner Auto Policy package short-rate percents (10.0 / 0.0) and 30 replacement-vehicle reporting days — stated in physdam short_rate_retention_b8529521 and matching `blueprint/products/auto.yaml`; the auto corpus's own rendering is not yet published.
- Owner Auto Policy term fields (term number, violation points, garaging state, vehicle-added change with acquisition date) and the Installment Payment Plans plan names, as read by the physdam factor docs — figures and names match the auto/billing charters; contradiction check against their corpora pending.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=S1,S2

## revision_2

### Gate and snapshot
- `tail -1 audits/render_source/physical_damage_claims/RENDER.log` → `RENDER round 3: DOCS OK` (gate met).
- `/tmp/erl0071_coord/kb_snapshot.sh physical_damage_claims physdam` at 2026-10-20T16:16:16: check_docs physdam → DOCS OK; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK (rc=0); check_traceability → TRACEABILITY OK, misses 0 (non-unlock 0); yaml f165003a…13db and task_tools 43a3e10b…2b54 unchanged; 56 docs.

### Round-1 items
- No KB RED existed in revision_1 (kb=CLEAN). S1 (source-side, reader-facing ambiguity in total_loss_and_theft_schedule_18c42af2) was routed as a placement fix: the scoped lienholder-settlement replaced_by now sits under the base `loss_payee_paid_first` line in that document. A reader of the facet alone now finds that a loss-payee total loss is paid in full to the loss payee, with any excess returned → one answer on task 1. **Closed for the reader.** The underlying source fact remains (the base parameter cannot be overwritten; coordinator logged BLUEPRINT-KNOWN), so it is no longer listed as an open src id.
- S2 (baseline wording names the time-in-force and tenure shares) — not routed (coordinator decision: placement-only). Still present, unchanged and verbatim to `baseline.rule`; kept on record as an open source-side note.

### Regression sweep
- Corpus diff: total size 100,470 → 101,218 bytes; the +748 bytes are exactly the new sub-bullet; 14 load-bearing hub/baseline/factor sentences re-found verbatim; roles 5/5/28/11/7 unchanged; 56 titles.
- Five tool names still each occur only in their own hub; three prerequisite sentences still verbatim only in their blocked hubs; no route, chain or cross-problem guidance; no gold-valued example (sweep of all task 0/1 scored values: absent).
- Runtime: tasks/*.json and runtime views unchanged since revision_1; revision_1 blind answers stay valid (revision_2 is non-blind by necessity — see contamination_disclosure in runtime_context files).

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=S2

## revision_3

### Gate and snapshot
- Every product is published (docs tree: auto 74, billing 58, fr, nonowner, physdam 56, rental 14, towing). `/tmp/erl0071_coord/kb_snapshot.sh physical_damage_claims physdam` at 2026-10-21T19:08:12: DOCS OK; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK (rc=0); TRACEABILITY OK, 0 misses; yaml f165003a9f59…13db and task_tools 43a3e10b642a…2b54 confirmed unchanged.
- Physdam corpus: files were re-touched 2026-10-21 06:33, but the content is identical to revision_2 (title+content dump 101,218 bytes, the same as revision_2; S1 governing-rule sub-bullet present once; tool name still only in its own hub).

### Round-2 items
- No KB RED was open after revision_2. S1 stays closed (sub-bullet in place). S2 stays open as a coordinator-decided non-route.

### Cross-product-pending items resolved
- **Owner Auto Policy short-rate percents.** auto `return_premium_methods_cea8bbd2`: 10 on Cardinal Point Minimum Limits, 50/100/50, 100/200/50 and 100/300/50 Liability; 0 on 100/300/100 and 250/500/100 Liability. auto `Filed Short-Rate Table…` uses the same "package's short-rate retention percentage" 10 / 0. physdam short_rate_retention_b8529521 states 10.0 / 0.0 on the same packages → **match**. (The auto table halves the percentage after day 60 for owner-term cancellations. physdam's baseline names "the owner package's short-rate retention percent", which the auto doc defines as the package figure, not the halved one. No conflict; not reached in task 1 anyway, because the total-loss tier keeps nothing.)
- **Replacement-vehicle reporting days.** auto `midterm_change_terms_9916785d`: "Reporting window, replacement vehicle | 30 calendar days after acquisition" → matches physdam's "Every Owner Auto Policy package sets 30 replacement-vehicle reporting days".
- **Installment Payment Plans names.** Billing corpus (official name "Installment Payment Plans") names exactly Paid-in-Full, Two-Pay, Four-Pay, Six-Pay Direct Bill, Monthly EFT, Monthly Card Autopay → matches minimum_earned_by_payment_plan_4311a07e.
- **Other cross-product vocabulary** in physdam factor docs: "Owner Auto Policy" term number / violation points / garaging state / vehicle-added change with acquisition date (auto uses the same terms); "Rental Reimbursement Coverage" authorised daily rate, invoice periods, reversals, closing (rental `Claims Manual Section on Rental Authorizations`, `Reversal of Paid Rental Benefits`, `Period of Rental`) → consistent. No cross-product RED.

### Exhaustive re-judge of every seeded row of another product (db_query, all non-physdam finders by customer)
Empty for both tasks: auto_policy_documents, auto_cancellation_requests, billing_authorizations, fr_filings / transactions / documents, nonowner (4 tables), towing (4 tables), identity_verifications, human_handoffs; task 1 also has no rental rows.

**Task 0 (Quintero, GA)** — 17 rows:
1. auto_policies 60b5aa95 (term 1, expired, 50/100/50, 2026-01-01→07-01, term_days 181, premium 1164, fees 25, 2 pts): 6-month term (structure limits), 181 actual days, new-business fee 25 (fee schedule), points within 16 (acceptability) → producible.
2. auto_policies e3b1a7a6 (term 2, in force, 07-01→2027-01-01, 184 days, 1212, fee 15, prior term 60b5aa95, opened 06-01): offer issued 30 days before expiration (renewal underwriting, 50/100/50 = 30), term number +1, same policy number, renewal fee 15 → producible.
3–6. auto_premium_transactions: 1164 premium_written new_business; 25 policy fee; 1212 premium_written renewal (booked on acceptance 06-26, before expiration → no lapse); 15 renewal fee → "Premium written equals the term's full-term premium … booked once" → priced correctly.
7–8. billing_plans bb23b041 (Paid-in-Full, closed 07-01, down payment 1189 = 1164 + 25) and 3cd37597 (Paid-in-Full, paid_in_full, down payment 1227 = 1212 + 15, enrolled 06-01 with the renewal offer) → plan schedule (Paid-in-Full down payment 100 %), paid-in-full status (balance 0, no installment) → producible.
9–14. billing_transactions: charges 1164 / 25 and payment 1189 (term 1); charges 1212 / 15 and payment 1227 against the renewal invoice (term 2); each charge references its auto txn ("Posting Policy Premium…": same amount, same day, referencing it) → balances 0 → producible.
15. billing_invoices 9db8e757 renewal bill (06-01, due 07-01 = expiring term's expiration, premium 1212 × 100 % + fee 15 = 1227) → "Installment Payment Plans Renewal Bill" → priced correctly.
16. rental_coverages 2108bc03 ($30/$900, active, on physdam c8ca1ee7, benefits_paid_total 630) and rental_premium_transactions 512e422c (92.00, 184/184 days, coverage_added) → full-term proration from the effective date → producible.
17. rental_authorizations bd72d6bb (authorized 09-23, the day of the recorded coverage confirmation; start 09-21 = date of loss, vehicle towed so not drivable; rate 30 ≤ $30 package limit) and eff5cee1 (closed 10-16, vehicle_repaired); rental_benefit_transactions: 210 × 4 paid on 7-day periods at 30/day, one duplicate (09-28..10-04) reversed once on 10-08 for duplicate_invoice; net 630 ≤ 900 per-loss maximum → rental authorization, payment, reversal and period rules → producible.

**Task 1 (Pruitt, TX)** — 27 rows:
1. auto_policies 5b7e2c19 (term 1, expired, Minimum Limits, 11-15→05-15, 181 days, 1248, written 1277.73 = 1248 + 298.64 − 268.91, 3 pts ≤ 24) → producible.
2. auto_policies f4c3e8be (term 2, in force, 05-15→11-15, 184 days, full-term 1386, written 1518.59 = 1386 + 132.59, 2 vehicles ≤ 4, opened 04-15 = 30 days before) → producible.
3–9. auto_premium_transactions: 1248 + 25 (new business); 298.64 Accord added 04-06 = 1386 × 39 / 181; 268.91 Camry removed 04-06 = 1248 × 39 / 181; 1386 + 15 (renewal, booked 05-12 before expiration); 132.59 Altima added 10-08 = 642 × 38 / 184 ("Added vehicle: the vehicle's full-term premium share, prorated", half-up) → all priced correctly.
10–13. auto_policy_changes: Camry removed 04-06; Accord added 04-06 (acquired 04-06, a replacement within 30 days → coverage from acquisition); Altima added 10-08 (acquired 10-08) → producible. **Camry `auto_vehicle_added` 7c5e1a93 effective 2025-11-15 (the new-business effective date) with no matching additional premium**: the auto charter defines `auto_vehicle_added` as "An additional or replacement vehicle is scheduled on the term". auto's rate worksheets treat the term's recorded full-term premium as already "the rating of the named insured and the scheduled vehicles", with "plus the vehicle's share on every vehicle-added change" on top. So a bind-time vehicle-added change is not a state the auto rules produce, and the rules would price it as a 1,248.00 addition that was never charged. Task 0's new-business Corolla, consistently, has no such row → **S3** (below).
14–15. billing_plans a2c94e71 (Paid-in-Full, closed 05-15, down 1273 = 1248 + 25) and 793b890c (Paid-in-Full, paid_in_full, down 1401 = 1386 + 15, enrolled 04-15) → producible.
16–26. billing_transactions: 1248 / 25 charges + 1273 payment; 298.64 charge and 268.91 credit on 04-06, each referencing its auto txn, + 29.73 payment (net); 1386 / 15 charges + 1401 payment against the renewal invoice; 132.59 charge on 10-08 + 132.59 payment → posting rule satisfied, balances 0 → producible.
27. billing_invoices 4f61d0a8 renewal bill (04-15, due 05-15, 1386 + 15 = 1401) → priced correctly.

### Writes another product's corpus owes, made mid-conversation — can any move a scored figure?
One exhaustive pass over every member:
- Task 0, rental: no invoice is pending and no rule calls for an immediate payment. Even if a final benefit for 10-12..10-15 (4 × 30 = 120) were paid, the physdam rental part is unchanged: paid 960 − reversed 210 = 750, plus uninvoiced days from 10-16 to the 10-16 end = 0 → 750, the same as 630 + 4 × 30. The refund (29.36) does not move.
- Task 0, auto / billing: no request is pending, plans are paid in full, there is no open invoice or cancellation request → nothing owed.
- Task 1, auto: removing the totaled Accord from the owner term (or cancelling the term) is neither requested nor owed under the auto corpus ("A vehicle is removed on the date requested"). Even if it were made, physdam reads only term number, violation points, garaging state, term days, vehicle-*added* changes (recent-purchase cap for the Accord VIN; the short-rate substitution tier, which the total-loss tier pre-empts) and the plan name. A removal or its return premium changes none of these → 5,830.00 / 294.25 / 155.33 unaffected.
- Task 1, billing: the billing corpus posts only owner-term premium transactions (`source_auto_txn_id`), and no tool posts physdam premium to a plan. No billing write is owed, and none would change the plan name the minimum-earned percent reads.
- Task 1, rental / towing / fr / nonowner: no holdings.
- Result: no cross-product write can move a scored figure in either task.

### Source-side items
- **S2** (open; coordinator-decided non-route): unchanged.
- **S3 (new, minor, non-scoring)** — task 1 seed row `auto_policy_changes` 7c5e1a93 (2009 Toyota Camry, `auto_vehicle_added`, effective 2025-11-15 = new-business inception, vehicle_term_premium 1248, no matching `auto_additional_premium`) is not a state the auto charter produces, for the reason given in row 10–13 above. It sits on the expired term 1 and is read by no physdam rule (the recent-purchase cap reads the Accord VIN; the substitution tier reads term 2), so no scored figure moves. It is a realism/consistency defect of the cross-product seed (task 0 follows the other convention).
- Note (no id): the physdam base clause "billed on the owner term's billing plan" has no counterpart in the billing corpus, which posts only owner-term transactions. The seeds follow the billing corpus (no physdam or rental postings on any plan), and no scored figure depends on it.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=S2,S3

## revision_4

### Gate and snapshot
- `grep "VERDICT revision_6" audits/policy_task/physical_damage_claims/_difficulty.md` → `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN` (gate met).
- `/tmp/erl0071_coord/kb_snapshot.sh physical_damage_claims physdam` at 2026-10-21T20:18:43: check_docs physdam DOCS OK; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK (rc=0); TRACEABILITY OK, 0 misses; hashes f165003a9f59…13db / 43a3e10b642a…2b54 unchanged; 56 physdam docs, content identical to revision_3 (101,218 bytes).

### S3 (round-3 source item) — closed
- Task 1 `auto_policy_changes` now holds 3 rows: Camry `auto_vehicle_removed` 2026-04-06, Accord `auto_vehicle_added` 2026-04-06 (acquired 04-06, 1386), Altima `auto_vehicle_added` 2026-10-08 (acquired 10-08, 642). The bind-time Camry `auto_vehicle_added` (7c5e1a93, effective 2025-11-15) is gone.
- Checked against docs/auto: `auto_vehicle_added` is "an additional or replacement vehicle"; the term's recorded full-term premium is "the rating of the named insured and the scheduled vehicles", plus the share on every vehicle-added change and less the share on every vehicle-removed change. Term 1 now reconciles: 1248 + 1386 − 1248 = 1386 current rate, and written premium 1248 + 298.64 − 268.91 = 1277.73, which matches the term record and its additional/return premium rows (298.64 = 1386 × 39 / 181; 268.91 = 1248 × 39 / 181). The remaining removal row still carries the Camry's 2025-11-08 acquisition date, which is a fact about the vehicle, not a pricing input. Task 0 follows the same convention (no bind-time vehicle-added row). **S3 closed.**

### Gold and regression
- GT unchanged in both tasks (evaluation_criteria writes and computations: 4975.5 / 450.0 / seq 2, 29.36; 5830.0 / 450.0, 294.25 / 478.75 / 33.0, 155.33 / 49 / 612.0; baselines 4560.5, 80.18, 7160.0, 329.55, 20.25).
- Exhaustive db_query re-read of all 31 finders per customer. Task 0: 14 non-empty finders, row counts and every value identical to revision_3. Task 1: identical except the one removed row. The rental-part invariance, the cross-product no-move analysis and the auto/billing/rental producibility judgements of revision_3 all still hold. With the Camry row removed, task 1 auto changes are all producible.
- No doc changed, so no new KB defect and no regression. Tool names occur only in their own hubs; prerequisite sentences are verbatim in their blocked hubs only; there are no gold-valued examples.

### Source-side items
- S1 closed (revision_2), S3 closed (this revision). **S2** remains open as the coordinator-decided non-route.

KB-VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=S2
