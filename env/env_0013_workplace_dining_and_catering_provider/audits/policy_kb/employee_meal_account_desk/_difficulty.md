# KB audit closeout — employee_meal_account_desk (product `meal`, M=2)

Revision 1, 2026-09-22. Auditor independent of the render agent and of the policy-side auditor for this difficulty.

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 (`meal_ext_restriction_lift_balance` tree) | **PASS** | **KB-BIJECTION RED** | **PASS** |
| 1 (`meal_ext_payroll_charge_consent` tree) | **PASS** | **KB-BIJECTION RED** | **PASS** |

Artifacts: `audits/runtime_context/employee_meal_account_desk/{0,1}.md` (blind_answer frozen before any source-layer read, hash `37f1753…`, followed by `contamination_disclosure` and `gt_comparison`) and `audits/policy_kb/employee_meal_account_desk/{0,1}.md` (`source_to_kb`, `kb_to_source`, `bijection_verdict`, `dependency_form`).

## Closeout: not reached

Closeout requires all three parts to PASS on every task. The two blind audits and both dependency-form scans pass; the two-way scan does not. `check_docs.py` and `check_traceability.py` were therefore **not** re-run on a final form, since the corpus has not been changed by this audit and no fix has been arranged — this skill edits no document.

## The findings, in one line each

| # | Finding | Where |
|---|---|---|
| S1 | The per-plan entry-gate conditions (`requires_employer_program`, `requires_payroll_consent`, `requires_manager_approval`, six plans each) are named as dimensions and never carried as values, so `meal_enrollment_terms`'s "the highest meal plan whose entry gate they meet" and `meal_plan_change_terms`'s "the highest plan whose gate they do meet is offered instead" are undecidable from the visible materials for three of four dimensions | `plan_entry_and_badge_schedule_ace7b64f.json`; `enrolment_and_badge_conditions_2bd6557e.json` §1, §4; `moving_between_meal_plans_08de3142.json` |
| S2 | An unsourced per-plan claim — "The two plans printing no entry service, no enrolment charge and no manager approval are the open end of the line" — resting on the entry-gate data of S1 and contradicted by the document's own table, where the conjunction holds for exactly one plan | `plan_entry_and_badge_schedule_ace7b64f.json`, "Points of judgement", sentence 1 |
| S3 | A per-variant parameter rendered as a line-wide constant — "the ceiling this line works to is 2 accounts" — against source `max_accounts_per_employee` = 2, 2, 2, 2, 1, 1 | `holding_accounts_at_several_sites_88ec232b.json`, "The ceiling on accounts held", sentence 1 |
| S4 | Low-weight addition: a discretionary condition with no structured source, "and the desk is satisfied it should come off" | `taking_a_spending_restriction_off_an_account_95f07956.json`, opening |

None of the four changes a scored value, a factor tier, a prerequisite, an owner or an order in either task.

## Policy-side notes (reported; they do not change this skill's verdict)

- **N-a** Prose and compute part company on whether a guest meal counts as "a meal rung against payroll": the rule text says so, the scored compute filters `transaction_code='meal_purchase'`. The KB carries the prose faithfully and inherits the gap (`allowance_application_calculation_8d744c5e.json` §1, `stretch_of_meals_carried_to_pay_cfc2fe49.json`), while rendering the exclusion explicitly wherever the source uses "meals of the employee's own". Live in this scenario's data (task 0 has two guest meals rung against payroll); changes no scored number in either task.
- **N-b** `load_arrears_paydown_ff1c695b`'s docstring still frames the payment as standing "to your credit against what you owe", which the extended rule replaced; the KB adjudicates correctly and twice, so the visible materials are unambiguous.
- **N-c** `meal_restriction_terms`'s "Where the plan requires the whole balance paid…" is not declared retired and presupposes the framing the sentence above it retires; the KB correctly keeps it in force.
- **N-d** `tasks/0.json` `evaluation_criteria` narrative names "the 38.90 charge of 2026-03-13"; that accrual is $26.50. The period and the scored value are unaffected.
- **N-e** "last calendar month" / "last three calendar months" are never defined as rolling versus named-calendar windows, in the source or the KB. The blind reading (rolling) matched GT on all six scored values.
- **S5** `payroll_charge_calculation_d6ef3365.json` §3 zeroes the stored-value term and then explains "that is why the charge carried is net of it". Both sentences are the source's own, so the KB may drop neither; comparable rationale sentences elsewhere in the same policy were homed in their factor documents instead, so the placement is not uniform.

## What the two blind audits establish

From the published corpus and tool-shaped DB queries alone, a careful reader derives, hop by hop and with no route stated anywhere:

- **Task 0** — root `meal_ext_restriction_lift_balance`; order period recovery → paydown → reinstatement; **$83.85** for `2026-03-P1`, **$134.16**, **$123.71**; all three hops state-derived, all thirteen factor tiers matched.
- **Task 1** — root `meal_ext_payroll_charge_consent`; order allowance lot → allowance application → consent; **$8.10**, **$6.35** against `POS-51002076`, **$51.30** for `2026-06-P1`; both hops state-derived, all sixteen factor tiers matched.

Both counter-proofs held in both tasks: "do only the one thing the customer asked for" is excluded by the blocked policy's own prerequisite sentences read against the records, and the all-baselines fall-back is definite and different ($125.00 / $119.30 / $154.75 and $9.50 / $9.50 / $116.50).

## Coverage gap, stated

Cross-product contradictions are outside this skill's detection range by design. Two cafe documents were read because six of this product's factor rules point a reader at them by business words; they were used only for findability and figure resolution, never as a criterion.

---

# revision_2 — closeout

Re-audit round 2, 2026-09-22T11:53:38Z. Revision 1 above is untouched.

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 (`meal_ext_restriction_lift_balance` tree) | **PASS** (revision 1; not reopened) | **PASS** | **PASS** |
| 1 (`meal_ext_payroll_charge_consent` tree) | **PASS** (revision 1; not reopened) | **PASS** | **PASS** |

## Closeout: reached

- The audit files correspond one-to-one with the tasks, and old revisions are traceable: `revision_2` is appended to `policy_kb/{0,1}.md` and `runtime_context/{0,1}.md`; no frozen `blind_answer` or `gt_comparison` was rewritten.
- Every normative atom of this difficulty's structured source is entailed by `docs/meal/`: nothing unborne, nothing borne with changed meaning, no claim from outside the source. The four round-1 exceptions are closed and re-verified against the yaml (not against revision 1's transcriptions).
- Every prerequisite's sentence stands verbatim, in its declared state form, in a document of the policy it blocks and in no other policy's — 1 hit each across all five product corpora, re-checked on the round-2 corpus; every hop resolves from that sentence, the depended-on documents and the records.
- Every declared factor's ladder is carried in full, tier by tier, in its own factor document, findable from the records its tier rests on — all 30 unchanged in this round and carried forward from revision 1's sweep.
- No other problem's tool name, route or aggregated chain is stated anywhere: each of the six task-tool names occurs in exactly one document, its own hub.
- Gates on the final form, supplied with the round-2 brief and placed on record (run by the coordinator, not by the auditor): `check_docs.py env/env_0013_workplace_dining_and_catering_provider meal` → `DOCS OK` (64 docs; roles factor 30 / baseline 6 / facet 10 / policy 12 / hub 6; 95 required quantitative keys; 6 task tools; 5 prerequisite edges; mechanical gates PASS). `check_traceability.py …/tasks/employee_meal_account_desk` → `TRACEABILITY OK`. Source fingerprints unchanged through the re-render (`a8f898ffaa1e6a3c` / `2fd04d28ab652a00`) — a documents-only change.

## The round-1 findings

| # | Round-2 disposition | Verification |
|---|---|---|
| S1 | **CLOSED** | New "entry gate, plan by plan" table in `plan_entry_and_badge_schedule_ace7b64f.json` carries all four dimensions; exact on all 24 cells against `variants[].entry_gate`. The "taken together" sentence is a faithful statement of the source's four-way conjunction, adding no threshold, ordering, tie-break or exception. Both rules that turn on "the highest plan whose entry gate they meet" are now applicable from published text alone, for all four dimensions; worked end to end in the task files. The two rule documents are byte-identical and no cross-reference was added. |
| S2 | **CLOSED** | The false conjunction is replaced by a uniqueness claim and two counts, all three true against the yaml (`['Pay-As-You-Go Badge Account']`; consent on 3, approval on 2, together on 1 of the 4 that carry either) and all three a direct read of the new table in the same document. |
| S3 | **CLOSED** | "the ceiling this line works to is 2 accounts" is absent from the corpus. The source clause stands verbatim, a per-plan column (2, 2, 2, 2, 1, 1) sits beside it, and the re-cast constant — "No plan in this line prints more than 2, and on two of the six the number printed is 1" — is true of that column and is a bounding observation, not a substitute rule. |
| S4 | **CLOSED** | "and the desk is satisfied it should come off" is absent from the corpus; the new opening is entailed by the source rule and the tool contract and adds no condition. The source's rationale clause survives verbatim in that policy's computation document. |

**No new defect; nothing regressed.** Exactly three of 64 documents changed; the other 61 are byte-identical, so every revision-1 PASS over them carries forward. The three changed documents were re-swept for routes, pointers, task mirrors and leaked world state (23 patterns, zero hits); all 5 prerequisite sentences and all 6 tool names remain singly homed; all 42 re-laid-out parameter values in the rewritten schedule are exact.

## The two declined notes — auditor's judgement

- **N-e (month-window counting basis) — declining was the right call, and the gap should be routed to the source layer.** The renderer's premise is verified on the charter: `temporal_basis` and `counting_rule` occur twice each in `policies` (the two time eligibilities, each fully specified and faithfully rendered) and **zero times in `extended_policies`**. Importing the harness's arithmetic would publish a boundary rule with no policy locator, which the skill forbids ("where the source leaves it open, the documents may not close it either"). But the openness is **outcome-determining**, demonstrated on both worlds from published sentences alone: task 0's `short_tender_deferral` takes "2 or more → $45.00" on a trailing three-month window and "Exactly 1 → $20.00" on completed named months (only the 2026-02-13 overdraft falls in December–February); task 1's meals carried are $99.30 trailing and $72.15 on completed named months (the June meals drop out). **This is a source gap: the extended policies should fix the counting basis the way the two base time eligibilities do.** It changes no verdict here and reopens no blind audit — revision 1 took the trailing reading on published grounds and landed on gold on all six scored values.
- **N-a ("meal rung against payroll" vs the narrower scored filter) — the reasoning is correct and declining is right.** Narrowing the published phrase would have the KB decide a question the source has not decided and would hide a source-layer divergence inside the documents. Two things sharpen it: the charter uses the distinct phrase "meals of the employee's own" wherever it does mean to exclude guests, and the KB renders that exclusion explicitly there; and the divergence is live in this scenario's data (task 0 carries two guest meals rung against payroll). It is outcome-neutral in both tasks. Source-layer item; the auditor does not say whether the rule text or the compute should move.

The four items the renderer recorded as source-side or out of domain — the `load_arrears_paydown_ff1c695b` docstring residue, the un-retired base clause, the GT narrative slip, and the baseline-sentence placement question (**S5**) — match revision 1's own dispositions and are rightly declined; retiring a clause the source never declared retired would be the KB legislating.

## Result

**This difficulty's rendering passes the audit:** runtime blind audit PASS + full-domain two-way scan PASS + dependency-form scan PASS, on both tasks. Remaining open items are source-layer only (N-e routed for settlement; N-a, and the three previously recorded source-side notes).

Coverage gap, restated: cross-product contradictions are outside this skill's detection range by design. Two cafe documents were read for findability and figure resolution only, never as a criterion.

---

# revision_3 — closeout, re-confirmed after the source fix

Re-audit round 3, 2026-09-22. Revisions 1 and 2 above are untouched.

This round exists because of revision 2's own determination: the month windows of all six extended policies were unfixed, the openness was outcome-determining on both worlds, and the coordinator routed it to the source layer, where it was closed and passed at a fourth source-layer audit. This is the second half of walking both step-3 stages after a source fix.

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 | **PASS** (revisions 1–2; not reopened) | **PASS** | **PASS** |
| 1 | **PASS** (revisions 1–2; not reopened) | **PASS** | **PASS** |

**Counting-basis carriage: CLOSED. No new defect; nothing regressed.** The difficulty remains closed out.

## What was verified, not relayed

- Corpus hash `2a683f16…` → `14d194b3d3262a4a05c70c290e47971c1a2e48eff577cee6ac0b46df1d53116b`; 64 documents before and after, none added or removed, **31 changed, 33 byte-identical** — the 6 computation documents and 25 of the 30 factor documents. Ids and filenames stable.
- `temporal_basis` stands on all six extended policies with the **same eight keys** as the two base time eligibilities, `unit: calendar_months`, `boundary: exclusive`, and a `counting_rule` **identical on all six**; that sentence is in the `rule` and the `baseline.rule` of all six (6/6 each) and is carried **verbatim in exactly six documents**, the six computation documents.
- **Zero unqualified month-window phrases** in any of the 64 documents, by my own sweep. All 25 factors that have a window carry every one of their source window phrases verbatim — 25/25, across the one-, two-, three- and twelve-month forms.
- **The five unchanged factor documents genuinely carry no calendar-month window**, verified from their source ladder faces and from the absence of the string in the documents: `stored_value_credit` (a 90-calendar-**day** window), `standing_pickup_share`, `employer_funded_base`, `employer_counter_topup`, `second_counter_trim`. Correspondence exact: 25 factors with a month window ↔ 25 changed documents.
- **The demonstrations that sent this to source both collapse to a single column.** Task 0's `short_tender_deferral`: boundary day 2025-12-17, both overdraft charges inside, "2 or more" — the rival $20.00 reading is now excluded by the factor document's own words. Task 1's `charge_window_basis`: boundary day 2026-03-11, the June meals inside — the rival $72.15 reading likewise.
- **The four hand-reworded sentences** were isolated mechanically (normalise every window phrase, strip the appended section: exactly four documents differ by anything more) and each checked against its source ladder face. Three preserve meaning exactly; one, in `paydown_share_bands_193e8447.json`, is a substantive tightening of a phrase revision 2 left loose, in the right direction. The other 27 changed documents differ from revision 2 only by the window phrase and/or the appended section.
- **Scoping line right.** Base-charter and facet occurrences of a monthly window (`overdraft_fees_per_month_max`, `guest_meals_per_month`, the monthly grant basis) are parameter meanings and base-rule clauses, the base charter carries no `temporal_basis`, and extending the qualifier to them would be the KB legislating. The two vocabularies are disjoint and the published counting rule is scoped in its own text ("in this policy"); `guest_surcharge_added_to_a_charge_to_pay_fcef17fa.json` carries both a parameter meaning and a policy window with no bleed in either direction. Day windows correctly untouched.
- **Regression:** the revision-2 entry-gate table (24/24 cells), the S2 uniqueness sentence and counts, the S3 source clause, re-cast constant and per-plan column, the S4 repaired opening; all 5 prerequisite sentences verbatim and singly homed; all 6 tool tokens singly homed; the 6/6/30 topology; a 23-pattern route/pointer/mirror sweep over all 31 changed documents with zero hits; and no authoring field surfacing as text in any document of any product.
- Gates on the final form, supplied with the brief and placed on record: `DOCS OK` (64 docs; roles factor 30 / baseline 6 / facet 10 / policy 12 / hub 6; 95 quantitative keys; 6 task tools; 5 prerequisite edges) and `TRACEABILITY OK`. Charter fingerprint `5e5926ed5ca38e26`; `task_tools.py` unchanged at `2fd04d28ab652a00`.

## The blind audits, unchanged and now ratified

Neither blind answer was reopened or altered. Both had declared their boundary days outright — task 0 "from 2026-02-17 / 2026-01-17 / 2025-12-17 / 2025-03-17", task 1 "from 2026-05-11 / 2026-03-11" — and the counting rule the source has now published yields **exactly those days** on both worlds. The re-render changed the documents' determinacy, not their meaning; every scored value stands.

## Three observations, none a defect

- **O1** The boundary convention is published only in the six computation documents, so a factor read alone fixes the window's anchor but not its inclusivity at the exact boundary. The source homes the sentence in `rule` and `baseline.rule` and on no ladder face, so the render put it where the source and the skill put it; a factor document may not point at the computation document; and no entry on either ledger comes closer than one day to any boundary.
- **O2** In `refunds_credited_against_meals_carried_60e78763.json` the clause carries the source face exactly ("the three **calendar** months running back from the day the account is worked") while the band table's second row and the illustration drop "calendar" and the table's third row keeps it — one table holding both spellings of one window. Qualifier intact, clause exact, no tier or value affected; the single visible seam in "reworded for readability, never for meaning".
- **O3** The counting-rule section sits in all six computation documents although none of the six baselines invokes a month window, which is a mild inference hook. Judged not a `KB-EXPLICIT RED`: the sentence asserts no variation, names none and points nowhere, and it is a source atom of each `baseline.rule` that the render must carry and that the skill homes in the computation document. Recorded as a policy-side note with both sides set out.

## The two referred observations

- **N4-1** (the counting rule is neither convention at a 31st-to-February boundary): the renderer was right to decline, holding the same line it held before the locator existed — publishing a disambiguation the source does not state would add a boundary rule with no policy locator. Verified unreachable **by margin** rather than assumption: task 0 has no entry booked later than the 28th at all; task 1 has three (2026-03-30, 2026-05-30, 2026-05-31), each 19–20 days inside its boundary. Source observation, no document consequence.
- **N4-2** (`duration_source` names a sentence rather than a field): appropriate, because the six policies' windows are not plan parameters but are written into the rule sentences, so there is no field to name. Moot on the document side twice over — `duration_source` appears in no document, and the duration travels inside every published window phrase. Worth recording at source only that the block is not mechanically resolvable to a value.

## Result

**This difficulty's rendering passes the audit**, re-confirmed after the source fix: runtime blind audit PASS + full-domain two-way scan PASS + dependency-form scan PASS, on both tasks, across three revisions. Remaining open items are source-layer observations only (N4-1, N4-2, N-a, and the three previously recorded source-side notes).
