# KB-doc policy audit — order_returns_and_price_adjustments (product order, docs/order, 56 documents)

## revision_1

Auditor: fresh KB auditor (brief kb_d4), independent of the renderer and of the policy-side auditor. Runtime view: published docs/order title/content, runtime tool schemas, `.audit_views/runtime/order_returns_and_price_adjustments/task<i>.runtime.json`, DB through the tool-shaped `db_query.py` path. Both blind answers were frozen before the source layer was read: task0 hash d14da8e32bf5aaf3, task1 hash d9e51c668df601f2. No contamination.

### Per-task part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 (reschedule; 3 state edges) | PASS: every value equals the GT (41.85 / 22.50 / 72.15 / 39.65); all hops state-derived | **KB-BIJECTION RED** B1 (late_change_baseline_qualifier) | PASS |
| 1 (Drive Up return; 1 state edge) | PASS: every value equals the GT (9.50 / 1.85 / 52.13); hop state-derived | PASS | PASS |

### Findings

- **kb: late_change_baseline_qualifier** (task 0). docs/order/late_change_fee_computation_642f339e.json, "**3. Amount.**", first sentence. The source baseline.rule "The standard late-change notice charge is the program's late cancellation fee, and the standard late-change fee is that notice charge, rounded half up to the cent." is rendered without either "standard". The default therefore reads as an unconditional rule: the same paragraph defines the late-change fee twice ("is that notice charge" / "is the total of …"), and it fixes the notice charge at the late cancellation fee against the short-notice schedule. This is a strength change on the visible surface; the scored numbers are unaffected.
- **Renderer departures, judged as asked.**
  1. Handoff reason written in business words ("with the reason policy not covered"): equivalent at entailment. The transfer tool's enum has exactly two values, and the business words map uniquely onto POLICY_NOT_COVERED. PASS.
  2. Stale base descriptions of the cutoff-hours and free-reschedule columns, kept verbatim: carrying base parameter_schema text as written is correct rendering, so there is no KB defect. The substance is a source-layer conflict, src=schema_cutoff_free_desc.
- **src: schema_cutoff_free_desc.** The base parameter_schema still says `cancel_cutoff_hours_before_scheduled` means "Hours before the scheduled delivery date before which a large-item order can be canceled or rescheduled without a fee". It also describes `large_item_reschedules_free` as "Number of delivery reschedules made before the cutoff that carry no fee". order_ext_late_change_fee, however, frees only reschedules "made two or more days ahead" while the confirmed requests are fewer than the free reschedules, and charges "every other reschedule". These descriptions are base vocabulary that no overwrite retires, so they conflict on untriggered branches: a request before the 48-hour cutoff after the free reschedules are used up, and a request two calendar days ahead but under 48 hours. Neither task triggers either branch.
- Observations, not RED: (a) the computation documents' assembly appositions ("The credited haul-away, which is the haul-away charge on the order"; "the late-express lateness rate of one half"; "the refund basis, which is the line's net amount as charged") drop the source's "or the amount a schedule below sets in its place". The discrete topology requires this of a computation document, and each factor document says its schedule "sets" the value. (b) In the drive-up Assembly paragraph the restocking multiplicand and the refund basis are kept in separate sentences, as in the source. A reader could still route the restocking base through the apposition, but that reading is not equally reasonable.

### Closing checklist

- Audit files match the tasks one to one: runtime_context/order_returns_and_price_adjustments/task0.md and task1.md, and policy_kb/order_returns_and_price_adjustments/task0.md and task1.md, each under revision_1.
- Every normative atom of order.extended.yaml relevant to the two tasks has a KB home. That covers the base clauses governing the subjects, all 8 overwrites (with their retired surfaces), 6 baselines, 30 factor ladders with every tier, 4 prerequisite sentences and 6 tool contracts. The one exception is B1, a changed strength.
- Every prerequisite sentence stands verbatim and in state form in its blocked policy's hub, and in no other document. No other problem's tool name, route or aggregated chain appears anywhere.
- No document example or tool schema equals a scored value.
- Gates re-run on the final form (kb_snapshot.sh, executed only): `DOCS OK`; `TRACEABILITY OK` (0.json 22/0 True, 1.json 15/0 True); EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; docs/order tree hash 4246d2268df53b62.
- Difficulty closes: **no**. Task 0 carries KB-BIJECTION RED B1.
- Coverage note: cross-product contradictions are outside this skill's range. The card and market corpora are not yet published, but neither task's scored figures depend on them. The market-side factor of task 1 reads only Marketplace records, and the order document names that product. So no figure here is conditional.

KBVERDICT revision_1: task0=RED task1=PASS kb=late_change_baseline_qualifier src=schema_cutoff_free_desc

## revision_2

Re-audit (coordinator round 2). RENDER.log tail `RENDER round 2: DOCS OK`. kb_snapshot.sh (executed only): DOCS OK; TRACEABILITY OK (0.json 22/0, 1.json 15/0); 7/7 instantiate gates OK; source hashes unchanged; docs/order tree hash 7f236facbf67bf41. Only late_change_fee_computation_642f339e and pickup_hold_and_order_changes_table_e8466089 changed.

| Task | Runtime | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS | PASS (B1 closed: baseline "standard" restored verbatim) | PASS |
| 1 | PASS | PASS (no regression) | PASS |

- The renderer's "Rule in force" paragraph beside the verbatim base descriptions is exact: it restates replaced_by 1 without its self-scope tail, the free-reschedule sentence verbatim and the cancellation tail verbatim. It adds nothing.
- Observation: the paragraph splits the column-meaning list, leaving the "Report days" bullet under it. This is layout only.
- src=schema_cutoff_free_desc: BLUEPRINT-KNOWN per the coordinator; still a source-layer item, unchanged.
- Contamination: revision_2 is a non-blind re-check by the revision_1 auditor. The revision_1 blind answers stay frozen.
- Difficulty closes: **yes** (all three parts PASS for both tasks).

KBVERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=schema_cutoff_free_desc

## revision_3

Cross-product re-judge (coordinator round 3; all seven products published). kb_snapshot.sh (executed only, 2026-10-25T04:51:56Z): DOCS OK; TRACEABILITY OK (0.json 22/0, 1.json 15/0); 7/7 instantiate gates OK; source hashes unchanged; docs/order tree hash 7f236facbf67bf41 (unchanged since revision_2).

| Task | Runtime | Two-way scan | Dependency form | Cross-product seed re-pricing |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | **rows not producible**: plan_register_item 0.00 (published registered limit 948.99); repair 2025-06-20 186.40 (published 344.00); **settlement 2026-10-06 reimbursement_egift_card 663.59 (published: repair at 374.00) — gold-bearing**, being the settlement H2's owed test and three haul-away factors read; holding fulfilled with liability 0.00 (published: active, 230.99) |
| 1 | PASS | PASS | PASS | every row producible (membership holding, membership-priced fee rows, no Cash, Pro Seller market ledger); missing membership fee, benefit-use and request rows are unread-row residue |

- (1) All conditional readings are resolved against the published corpora, with no cross-product KB contradiction: kb CLEAN.
- (3) No write that another product's published rules make owed at once can move a scored read in either world.
- Accepted residue (not routed): task 0's missing eGift card of the reimbursement (gift, unread); task 1's missing membership fee charges, benefit uses and cancellation request (unread).
- Per this skill's discipline, the seed findings are source-layer items (task initial_state against the plan product's published rules). They do not change the KB verdict, but the t0 settlement item moves gold if corrected toward the published rules.

KBVERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=schema_cutoff_free_desc,t0_plan_settlement_rows,t0_plan_registration

## revision_4

KB confirm after the seed-only round (rework_claims_r7; policy re-audit revision_7). kb_snapshot.sh (executed only): DOCS OK; TRACEABILITY OK (0.json 22/0, 1.json 15/0); 7/7 instantiate gates OK; source hashes unchanged; docs/order tree hash 7f236facbf67bf41 (unchanged).

| Task | Runtime (blind-view consistency) | Two-way scan | Dependency form | Changed rows |
|---|---|---|---|---|
| 0 | PASS (22.50 / 41.85 / 72.15 / 39.65, unchanged) | PASS | PASS | all producible: 2024 line 1799.99, plan price 199.00, registration 1948.99, repairs 374.00 / 374.00 / 404.00, reimbursement 647.99 after the repair count was reached, liability 149.00 |
| 1 | PASS | PASS | PASS | none changed |

- t0_plan_registration and t0_plan_settlement_rows are closed. schema_cutoff_free_desc remains BLUEPRINT-KNOWN.
- Coordinator note (not a verdict item): `.audit_views/runtime/order_returns_and_price_adjustments/task0.runtime.json` is stale. Its user_scenario still says "repaired it once last year", while tasks/0.json now says "repaired three times …". Refresh the view before any further blind audit.

KBVERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=schema_cutoff_free_desc
