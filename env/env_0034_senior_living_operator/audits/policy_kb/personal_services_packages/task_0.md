# Policy-KB bijection audit — personal_services_packages / task 0

## revision_1

Auditor: erl-kb-doc-policy-audit sub-agent, round 1, 2026-10-05. Written after the blind answer in `runtime_context/personal_services_packages/task_0.md` was frozen.
Source: `tasks/personal_services_packages/services.extended.yaml` (policies in scope: `services_ext_suspension_months` (root), `services_ext_short_visit_credit` (prerequisite), base `services_suspension`, `services_hours_and_billing`, `services_disputes_and_corrections`, `services_cancellation_and_end`; tier parameters read), `task_tools.py` (`sign_services_suspension_89d6021d`, `post_services_visit_credit_5ef485c2`). Corpus: `docs/services/*.json` (title/content; meta used only to locate candidate homes).

### Entry conditions (Step 0)

Supplied with the brief and only cited: policy-side verdict PASS (erl-task-policy-audit round 3, both tasks); `check_docs.py … services -> DOCS OK`; `check_traceability.py …/personal_services_packages -> TRACEABILITY OK`; instantiation gates EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; runtime view + DB access path supplied with hashes (re-verified). Input complete.

## source_to_kb

### A. `services_ext_suspension_months` (root, on_request)

Baseline (`baseline.rule`) — computation document `suspension_length_calculation_14825d7c.json` ("Personal Services Plan Suspension Length — First Month and Number of Months"):

| Baseline atom | KB home | Judgement |
|---|---|---|
| First month = first calendar month whose first day is at least suspension_notice_days after signing; ends on the last day of its last month; records first month + count | computation doc "The first suspended month" + worked example (25 May → June, 26 May → July); hub "What the signed suspension shows" | equivalent |
| Months = max_suspension_months_per_12m − months counted for the most recent suspension, never below zero; PAYG nothing to suspend | computation doc "The number of months" | equivalent (verbatim in substance) |
| "The months counted toward time in force are, as the standard, the whole months since the plan's effective date." | **not in the computation doc**; carried in factor doc `long_standing_plan_months_75df9d81.json` ("The months counted toward time in force are, as the standard, the whole months since the plan's effective date…") and as row 3 of factor doc `counting_time_in_force_dded501d.json` | **misplaced** — see finding B2 |
| Only months ending fewer than 12 whole months before the request counted; nothing where none on record; whole-month counting "for the suspension and for the plan's time in force" | computation doc "Months counted for the most recent suspension" + "Equivalently…" + table (30 Jan / 29 Jun / 30 Jun 2026) — the suspension half; the time-in-force half sits in the two factor docs | suspension half equivalent; time-in-force half misplaced (B2) |
| Product figures read: max_suspension_months_per_12m, suspension_notice_days | named in business words ("the package's maximum suspended months per rolling 12 months", "the package's suspension notice days"); values in facet `suspension_allowance_and_residency_end_terms_ce014827.json` (0/2/2/3/3/3; 7) | equivalent; definite fall-back (task 0: 0) |
| window_months 12 (own constant) | computation doc "fewer than 12 whole months", "12 less the whole months" | equivalent |

Extended-rule atoms outside the baseline:

| Atom | KB home | Judgement |
|---|---|---|
| Final assembly: "The months a suspension may run are the package's max_suspension_months_per_12m, plus the months added for an absence and for time in force, less the months deducted for the amount past due and the months counted for the most recent suspension, never below zero and always a whole number, the Pay-As-You-Go Plan having none." (compute `result = 0 if max_base == 0 else MX(0, max_base + absence_extra + tenure_extra - standing_deduction - counted_prior)`) | **no home**. The computation doc floors only `max − counted` ("…less the months counted for the plan's most recent recorded suspension, never below zero"); the factor docs say "2 months are added to the number of months a suspension may run" / "2 months are deducted from the number of months a suspension may run" with no floor on the total | **omitted / meaning changed** — finding B1 |
| Prerequisite sentence | hub `package_suspension_requests_c7e6d00e.json`, section "When the number of months is fixed" | see C |

Factors (whole ladders):

| Factor | Factor document | Ladder carried | Judgement |
|---|---|---|---|
| `medical_absence_extension` (on leave + hospital/rehab → 2; active, returned ≤ 30 days → 1; otherwise 0) | `hospital_and_rehabilitation_absence_months_e38583b8.json` | all three tiers + "any other reason, or none" + "No assisted living residency"; window counted in calendar days from the return date; boundary 30/31 days; records named (status, absence reason, return date) on "the Assisted Living Residency and Care Agreement" | complete |
| `time_in_force_count` (method: from Larkspur IL with move-in on record → months since IL move-in; else with recorded suspension → months since effective less that suspension; else months since effective) | `counting_time_in_force_dded501d.json` | all three methods, "so that years as a Larkspur resident carry over", "so that months on hold do not count", whole-month counting, months of a suspension = calendar months covered; names the Assisted Living Residency and Care Agreement and the Independent Living Residency Agreement | complete |
| `time_in_force_extension` (≥ 48 → 2; 24–47 → 1; else 0) | `long_standing_plan_months_75df9d81.json` | all tiers with figures 24/48 and boundaries 23/24/47/48 | complete |
| `account_standing_deduction` (≥ 100.00 → 2; > 0 and < 100.00 → 1; ≤ 0 → 0; past due = ledger balance owed less the package fee charged on the 1st of the current month) | `account_standing_and_suspension_length_1f654a81.json` | all tiers, threshold 100.00, the ledger reading table, boundary 100.00/99.99/0.01/0.00 | complete |

Overwrite / retired surface: superseded clause "Suspended months in any rolling 12 months … may not exceed max_suspension_months_per_12m …; the Pay-As-You-Go Plan has nothing to suspend." — rendered as retired in base doc `package_suspension_terms_43a8c9be.json` ("Retired wording, no longer in force …"); its replacement is carried by the computation doc. Remaining `services_suspension` clauses (grounds/min absence, notice, notice counting, during suspension, resumption) are carried as "Terms in force" 1–5 with the 7-day boundary table. No clause retired that the source does not retire. PASS on the retired surface.

Tool `sign_services_suspension_89d6021d`: hub invocation block — owner (customer's own tool, resident or financial agent), parameters (`services_plan_id`, `first_suspended_month` YYYY-MM-01, `suspended_months` positive integer), effect (start = first day of first month; end = last day of last month; status unchanged) and return keys match `task_tools.py`. Equivalent.

### B. `services_ext_short_visit_credit` (prerequisite, state_due)

Hub `overbilled_visit_charge_corrections_a4cecfad.json`: desk corrects, without waiting, within the dispute window of posting; one at a time from the most recently posted hourly charge for a delivered visit; one service_dispute credit referencing the charge carrying its billing month. Tool block matches `post_services_visit_credit_5ef485c2` (enum `service_dispute`/`billing_error`/`residency_end_proration`, amount 2 dp half up, return keys). Equivalent.

Computation doc `visit_charge_re_rating_7bf2ec06.json`: charge/visit selection and order-record inputs; billable time = delivered minutes rounded up to the increment, in hours, floored at the companion / per-visit minimum; covering = hours the order drew; re-rated charge = hours beyond covering × hourly rate beyond the allotment, rounded to the cent; credit = posted − re-rated, never more than posted; a charge whose re-rated charge is not below the posted charge is credited nothing. Product figures (increment, minimums, hourly rate) named; values in facets `visit_time_measurement_85596384.json` and `package_fees_and_monthly_hours_04c4feb4.json`. Dispute window named in the hub (60 days in `statement_and_fee_terms_77123827.json`). Complete; fall-back definite (task 0: 55.00).

Factors:

| Factor | Document | Ladder | Judgement |
|---|---|---|---|
| `delivered_time_billing` (fewer → round down; more → booked minutes; equal → round up) | `billed_time_for_short_and_long_visits_b7d9e78f.json` | all three methods, increment 15 stated, boundary table 89/76/74/90/91/130; "billed minutes … before it is expressed in hours" keeps the baseline floor (compute `MX(billed_minutes/60, floor)`) | complete |
| `date_surcharge` (holiday % / weekend % / 0) | `re_rated_visit_date_surcharges_4b0ef082.json` | all tiers per package, holiday calendar 2025–2027 matching compute `is_holiday`, holiday precedence, rounding only after the increase | complete |
| `illness_relief` (0–3 days → 0.5; >3–7 → 0.8; else 1; only for a visit ended short with a hospital/rehab absence on the AL residency) | `illness_relief_on_shortened_visits_e0b96f08.json` | all tiers incl. "before the visit date" and "any other reason"; boundary 9/10/13/14/17/18 March; rounding after the multiplication. Source says "the surcharged billable hours are multiplied"; the doc says "the visit's billable hours are multiplied" and both docs defer rounding until after their own step — the product of the two multipliers and the single rounding are entailed identically | complete, equivalent |
| `covering_hours_rule` | `hours_covering_a_re_rated_visit_16fbd512.json` | three tiers, expiry precedence over restore, month-end vs plan-end expiry | complete |
| `entrance_overage_rate` (lifecare −4.00; fee-for-service −2.00; else rate) | `life_plan_hourly_rate_for_re_rated_visits_4f87d96e.json` | all tiers, both reductions stated as resulting rates per package, "not recorded as occupied does not change the rate"; names the Entrance Fee Agreement and its contract type. The contract type is not a record field (compute `CPARAM('entrance','contract_type')`); the visible link from plan name to contract type is the company background ("LifeChoice … on a fee-for-service basis, … LifeCare … with lifecare benefits") | complete |
| `dispute_goodwill` (≥ 2 → 25.00; 1 → 10.00; 0 → 0; 12-month look-back) | `goodwill_on_repeat_service_disputes_005b6c47.json` | all tiers, look-back counting and boundary 16/15 Oct 2025, assembly "added … capped at the posted hourly charge and rounded" (from the extended rule's assembly sentence) | complete |

Overwrite / retired surface (5 superseded clauses): in `hours_draw_and_service_billing_bfbe74de.json` clause 2 (delivered-time rounding), clause 4 "The resulting hours are drawn from the hours available on the plan." and "the rest are charged … as one hourly charge on the same order" — each shown as "Retired wording, no longer in force"; the residue "where fewer hours remain than are needed, the remaining hours are drawn, each amount being rounded to the cent half up" is the exact source residue. In `disputes_and_corrections_07d62226.json` "an upheld dispute of a money charge is credited as a service dispute referencing that charge" and "A draw or charge that matches … is not an error" are shown retired; rules in force 1–5 match the unretired source clauses. Nothing retired beyond the source. PASS on the retired surface.

### C. Prerequisite edge `services_ext_suspension_months → services_ext_short_visit_credit`

- `policy_source`: "The number of months a suspension may run is fixed only after every hourly charge on the plan that its visit record shows billed on more time than was delivered carries a service dispute credit referencing it."
- Carried verbatim (exact string match) in the blocked policy's hub `package_suspension_requests_c7e6d00e.json`, section "When the number of months is fixed"; a same-form restatement follows in the same section ("Put another way: while any hourly charge … is without a service dispute credit referencing it, the number of months … is not yet fixed."). Form: state; connective "only after" intact; strength: hard gate.
- No other document carries it (corpus-wide string scan over all products: 1 hit).
- Resolution basis: depended-on hub `overbilled_visit_charge_corrections_a4cecfad.json` states its own rule in the same words — "corrected by the Resident and Family Services desk whenever it is found within the package's dispute window … posted as one service dispute credit referencing that hourly charge" — plus the records (`services_hourly_charge` `0cf232c7-…`, order `actual_minutes 70`). The depended-on documents do not disclose who waits on them. `condition`, `resolved_by`, `effect` appear nowhere in the corpus.
- Judgement: carried at the same strength and form.

## kb_to_source

Sentence-level reverse scan of the 14 documents of the two policies plus the four base documents and the facets they name:

- Every normative claim traces to `rule`/`baseline.rule`/factor ladders/base rules/`task_tools.py` docstrings or is a provable derivation (boundary tables, "Equivalently…" re-statement of the counted-months min/max, "(expiries recorded because the plan ended are not month-end expiries)" from the `expiry_basis='month_end'` filter, "the correction being made does not count itself" from "posted … before the correction", "the visit's billable hours are stated to two decimal places" which is exact for quarter-hour values).
- Additions: none found (no confirmation, review, notification, re-verification or failure procedure that the source lacks).
- Cross-problem operational guidance ("if unmet, first call …"): none. The blocked hub names only its own tool; the depended-on hub names only its own tool.
- A task's opening world state written as a policy fact: none; every example is marked hypothetical and uses invented figures.
- Omissions / rewrites: B1 (assembly floor) and B2 (baseline time-in-force sentences homed in factor documents) — see verdict.

## bijection_verdict

**KB-BIJECTION RED** (task 0, revision 1). Neither finding changes any task-0 number; both concern the whole domain.

**B1 — the suspension months' final assembly and its floor are not carried; the corpus entails a different floor point.**
- Symptom: from the corpus a reader computes `max(0, max − counted) + additions − deductions` with no floor on the total; the source computes `max(0, max + additions − deductions − counted)`.
- Root cause: the extended rule's final sentence ("The months a suspension may run are the package's max_suspension_months_per_12m, plus the months added for an absence and for time in force, less the months deducted for the amount past due and the months counted for the most recent suspension, never below zero and always a whole number …") has no home. The only floor in the corpus is attached to the partial `max − counted` in `suspension_length_calculation_14825d7c.json` ("…less the months counted for the plan's most recent recorded suspension, never below zero and always a whole number"); `hospital_and_rehabilitation_absence_months_e38583b8.json`, `long_standing_plan_months_75df9d81.json` and `account_standing_and_suspension_length_1f654a81.json` add to or deduct from "the number of months a suspension may run" with no floor.
- Evidence of a reachable divergence: this plan itself, after the 3-month suspension task 0 signs (Nov 2026–Jan 2027, exceeding the Companion maximum of 2, as the in-force rule allows), asking again in March 2027 while on leave, 85+ months in force, nothing past due: counted = min(3, 12 − 1) = 3. Source: `MX(0, 2 + 2 + 2 − 0 − 3)` = 3. Corpus: `max(0, 2 − 3)` = 0, + 2 + 2 = 4. And with max − counted = 0, no addition and a 2-month deduction, the corpus gives −2 (nothing floors it) where the source gives 0.
- Nature: source-induced in part — `baseline.rule` itself floors the partial sum ("…less the months counted …, never below zero"), while the extended rule floors only the total; the corpus carries the first and drops the second. Recorded as a policy-side note (N1) as well; the KB verdict stands.
- Affected: `suspension_length_calculation_14825d7c.json` ("The number of months"); the three suspension factor documents (their "Rule" paragraphs).

**B2 — baseline atoms of the suspension policy are homed in factor documents, not in the computation document.**
- Symptom: the computation document does not state how "the months counted toward time in force" are counted by default.
- Root cause: `baseline.rule` sentences "The months counted toward time in force are, as the standard, the whole months since the plan's effective date." and the clause "whole months for the suspension and for the plan's time in force are counted from the earlier date to the date of the request …" are rendered in `long_standing_plan_months_75df9d81.json` (Clause, 2nd paragraph, verbatim incl. "as the standard") and `counting_time_in_force_dded501d.json` (row 3, "Whole months are counted …"), not in `suspension_length_calculation_14825d7c.json`, which carries only the suspension half of the counting clause.
- Entailment at corpus level is preserved (no number changes); this is a departure from "the computation document carries `baseline.rule` complete".
- Nature: source-induced — the sentence belongs to `baseline.rule` but only a factor consumes it, and its wording "as the standard" signals a variation wherever it is placed (see N2 and dependency_form E1).

No relation to previous revisions (first audit revision for this difficulty).

### Policy-side notes (do not change this skill's verdict)

- N1: `services_ext_suspension_months.baseline.rule` floors `max − counted` while the full rule floors only the total (root of B1).
- N2: `baseline.rule` contains a factor-only default whose wording ("as the standard") announces a non-standard count; it cannot be rendered verbatim in the computation document without a hint, nor in a factor document without moving a baseline atom (root of B2/E1).
- N3: `max_suspension_months_per_12m` keeps its description "Maximum suspended calendar months in any rolling 12-month window" although the in-force rule adds months beyond it (task 0's own answer, 3, exceeds the Companion figure 2). The facet `suspension_allowance_and_residency_end_terms_ce014827.json` faithfully renders the description and adds the note "the Essentials and Companion Packages allow 2", which reads as a cap; the retired-clause notice in `package_suspension_terms_43a8c9be.json` and the factor documents resolve it for a careful reader.
- N4: the `services_ext_short_visit_credit` overwrites retire `services_hours_and_billing`'s general draw and overage-charge clauses ("The resulting hours are drawn from …", "the rest are charged … as one hourly charge on the same order") for every delivered visit, replacing them with re-rating rules; the base document faithfully leaves "where fewer hours remain than are needed, the remaining hours are drawn, each amount being rounded to the cent half up" as the only in-force drawing clause.
- N5: the Entrance Fee Agreement contract type the two entrance factors read is a variant parameter, not a record field; the services corpus names "contract type — lifecare or fee-for-service" and the mapping from plan name is visible only through the company background / entrance corpus (cross-product, outside this skill's criterion surface).

## dependency_form

Blind hop marks (frozen): P1 → P2 **state-derived**; no hop pre-solved. Whole-corpus scan (49 services documents; tool-name and prerequisite-sentence string scan over every product's corpus):

| Check | Result |
|---|---|
| Prerequisite sentence verbatim on the blocked side, state form kept | yes — `package_suspension_requests_c7e6d00e.json`; its "Put another way" restatement in the same section keeps the state form and names no action, performer or tool |
| State-form sentence restated as an action / performer / other problem | none |
| Other problem's tool named in the blocked hub or any non-owning document | none — `post_services_visit_credit_5ef485c2` appears only in its own hub; `sign_services_suspension_89d6021d` only in its own hub |
| Dependency or order between problems stated beyond the source sentence, or in a second document | none |
| Aggregated table / checklist / route / ordered step list across problems | none |
| Wrong-vs-correct contrast, named mistake, chain-walking example/FAQ | none across problems. Examined: `account_standing_and_suspension_length_1f654a81.json` worked example "Had the credit not been on the ledger, the amount past due would be 106.00 USD and 2 months would be deducted" — a hypothetical boundary illustration of the factor's own input ("less every payment and credit"); it names no correction, credit reason or other problem. Not RED |
| Titles / openings mirroring a task | none; "Requests to Suspend a Package for the Longest Allowed Period" names the on_request policy's own request type (general subject) |
| Depended-on document reachable only through the dependent's phrasing | no — KB_search with record/sentence words ("hourly charge billed more time than delivered credit", "service dispute credit") returns the correction hub / its computation document |
| Factor document stating a customer's tier, a "mistake to avoid", or evidence rows as fact | none |
| Computation document hinting at modification | none — `suspension_length_calculation_14825d7c.json` and `visit_charge_re_rating_7bf2ec06.json` contain no "unless", "adjustments", "certain customers", "elsewhere" or pointer |
| Factor document naming / pointing at the computation document or another factor | **E1 (below)** |

**E1 — a factor document signals that another counting rule exists.**
- Location: `long_standing_plan_months_75df9d81.json`, "Clause", 2nd paragraph: "The months counted toward time in force are, **as the standard**, the whole months since the plan's effective date, counted to the date of the request …".
- What it states: that the effective-date count is only the standard one — i.e. that some other rule varies the count — which points, without naming it, at the separate factor document `counting_time_in_force_dded501d.json`. The blind audit recorded this wording as a signal before the reveal (runtime_context task_0, counter-proof notes).
- Effect on this task: the counting factor was in any case reachable from the records (`admission_source 'larkspur_independent'`, IL `move_in_date`), so the hop was not pre-solved and the solution is unchanged.
- Nature: the words are the source's own (`baseline.rule`: "The months counted toward time in force are, as the standard, …"); their placement in a factor document is the rendering's (see B2, N2).

**Verdict: KB-EXPLICIT RED** (task 0, revision 1) — E1 only.

## part_verdicts (task 0, revision 1)

- Runtime blind audit: **KB-RUNTIME PASS**
- Full-domain two-way scan: **KB-BIJECTION RED** (B1 assembly floor omitted/changed; B2 baseline time-in-force atoms homed in factor documents)
- Dependency-form scan: **KB-EXPLICIT RED** (E1 "as the standard" in a factor document)

## revision_2

Round-2 re-audit, 2026-10-05 (~11:55Z). Inputs: round-4 `services.extended.yaml`, unchanged `task_tools.py`, re-rendered `docs/services` (49 documents: `long_standing_plan_months_75df9d81.json` deleted; `share_of_the_previous_suspension_70f12af8.json` added). Gate lines are as the coordinator supplied them (DOCS OK (49 docs); TRACEABILITY OK; instantiation gates OK); erl-task-policy-audit round 4 PASS. Revision 1 text above is untouched.

### Closure of round-1 findings

| Item | Round-2 evidence | Status |
|---|---|---|
| B1 assembly floor | Source rule + `baseline.rule` + overwrite `replaced_by` now read: "The months a suspension may run are worked out as one total: … that total is never below zero, the floor being applied once to the final number of months and never to a part of it" (compute `result = 0 if max_base == 0 else MX(0, max_base + absence_extra + tenure_extra - standing_deduction - counted_prior)`). KB: `suspension_length_calculation_14825d7c.json` clause 1 carries it verbatim in substance, with the "Floor on the total" example (2 − 3 → 0; 2 + 1 − 3 = 0; 2 + 2 − 3 = 1); the factor documents now add to or deduct from "the total months a suspension may run" (`hospital_and_rehabilitation_absence_months_e38583b8.json`, `account_standing_and_suspension_length_1f654a81.json`). The round-1 counter-example (counted 3 > maximum 2, additions 4) now gives the same number from corpus and source. | **closed** |
| B2 baseline time-in-force atoms in factor documents | The source now puts the effective-date ladder in `baseline.rule` ("Time in force adds loyalty_long_extra months where the whole months since the plan's effective date are at least loyalty_long_months …"); `time_in_force_extension` is no longer a factor; whole-month counting is a baseline sentence. KB: the computation document carries clause 2 (ladder 24/48 with figures, table, boundary) and clause 4 (whole months); the old factor document is deleted; `counting_time_in_force_dded501d.json` carries only the `time_in_force_count` method ladder (3 methods, complete). | **closed** |
| E1 "as the standard" | The phrase no longer appears in the source or in any document (corpus-wide grep: 0 hits). | **closed** |
| N3 (policy-side) | Source now says "the package's max_suspension_months_per_12m, which is the starting allowance and not a ceiling"; rendered in the computation document; the facet note now reads "The figure is 0 months … 2 months … 3 months" (no "allow"). | rendered |
| N4 (policy-side) | `services_ext_short_visit_credit` no longer overwrites `services_hours_and_billing`; its remaining overwrites both target `services_disputes_and_corrections`. KB: `hours_draw_and_service_billing_bfbe74de.json` carries clauses 2 and 4 in force, matching the base rule text, with nothing marked retired; the measure `services_msr_hours_available` is rendered ("granted, rolled over and restored, less … drawn and … expired, as booked up to the moment of the draw"). The replacement for "A draw or charge that matches … is not an error" ("A charge re-rated under this rule is corrected on the re-rated figure even where it matches … those rules stay in force for every first posting …") is carried in the correction hub `overbilled_visit_charge_corrections_a4cecfad.json`, and the clause is still shown as retired in `disputes_and_corrections_07d62226.json`. | rendered, faithful |
| N5 (policy-side) | Source ladders now name the plans ("the LifeCare Declining Balance Plan or the LifeCare 90% Refundable Plan"; "any LifeChoice plan"); rendered in `life_plan_hourly_rate_for_re_rated_visits_4f87d96e.json`. | rendered |

### source_to_kb (revision 2, changed surface)

- `baseline.rule` of `services_ext_suspension_months` (first month; one total with floor; time-in-force ladder; months counted for the most recent suspension; whole months) → computation document clauses 1–4 and tables. Product figures named (maximum suspended months, notice days → facet); own constants (24/48/1/2, 12) stated. Fall-back definite: task 0 → 2 + 1 − 2 = 1.
- Factors: `medical_absence_extension` (complete, unchanged ladder, "added to the total"); `account_standing_deduction` (complete, "deducted from the total"); `time_in_force_count` (3 methods complete); **new** `previous_suspension_share` → `share_of_the_previous_suspension_70f12af8.json`: all three tiers (lay within a recorded hospital/rehab absence → none; otherwise ended ≥ 3 whole months before → 0.5, rounded down; otherwise in full), the "lay within" test as compute `prior_in_medical_absence` (reason hospital/rehab, absence start on or before the suspension's first day, return not recorded or on/after its last day), whole-month counting, rounding down (`int(window_counted * prior_share)`), boundary 29/30 September, names the Assisted Living Residency and Care Agreement. Complete.
- Overwrite surface: the one `services_suspension` clause is still shown retired in `package_suspension_terms_43a8c9be.json`; the two `services_disputes_and_corrections` clauses are shown retired; nothing else retired.
- Prerequisite: sentence unchanged and still verbatim, state form, only in `package_suspension_requests_c7e6d00e.json` (corpus-wide: 1 hit); depended-on hub unchanged in that respect.
- Short-visit credit: ladders unchanged; GT 87.50 unchanged.

### kb_to_source (revision 2)

New normative sentences checked: "starting allowance and not a ceiling", "floor … applied once to the final number", the time-in-force ladder, the share rule, the correction-hub sentence, the restored billing clauses, the measure definition — each has a source sentence. No added step, confirmation or procedure. No cross-problem guidance. One derived example restates a task's world (X1, below).

### bijection_verdict (revision 2)

**PASS** — B1 and B2 closed; no new omission, change of meaning or addition.

### dependency_form (revision 2)

All round-1 checks repeated over the re-rendered corpus: the prerequisite sentence is verbatim and only on the blocked side; no other problem's tool is named; there is no route, aggregation or chain example; titles are general; the computation document has no hint (its "starting allowance and not a ceiling" and "never to a part of it" refer to its own components). `counting_time_in_force_dded501d.json` names the quantity it changes ("the whole months of time in force that decide the time-in-force months") and `share_of_the_previous_suspension_70f12af8.json` names "the months counted for that suspension". Neither names a document; each states what its tiers change. Not RED. E1 closed.

**New finding X1 — a derived example restates task 0's initial state.**
- Location: `hours_draw_and_service_billing_bfbe74de.json`, Clause 4: "*Hypothetical illustration:* a visit counted at 2.5 hours on a plan with 0.5 hour available draws the 0.5 hour and charges the other 2.0 hours as one hourly charge on the same order; at an hourly rate of 44.00 USD that charge is 88.00 USD."
- Mirrored rows (task 0 records): order SO-2609-0389's draw `4bf2aa6c-…` of 0.5 h, which exhausted the 0.5 h left in September (grant 8.0 less 7.5 drawn); the hourly charge `0cf232c7-…` of 2.0 h, 88.00 at the Companion rate 44.00 on the same order. These are exactly the figures of the charge that task 0's prerequisite is about.
- Why it counts: the render rule "Derived examples are isolated from tasks: … must never read or restate a task's … initial state" — the "hypothetical" label does not change that the inputs are the task's own posting. The example is new in this rendering (the round-1 Clause 4 had none).
- Effect: the solution is unchanged (the correction hub says the charge "is corrected on the re-rated figure even where it matches … the rules that govern hours when they are first drawn and charged"), but the example presents the very posting the task asks the solver to question as the standard billing outcome.
- Observation, not RED: `share_of_the_previous_suspension_70f12af8.json` uses "A suspension of March and April" in a within-absence example; task 0's earlier suspension is also March–April, but the example's absence dates (20 Feb – 10 May) and its conclusion (none counted) do not match task 0's records, so it does not restate them.

**Verdict revision 2: KB-EXPLICIT RED** (X1).

## part_verdicts (task 0, revision 2)

- Runtime: **KB-RUNTIME PASS** (not blind)
- Full-domain two-way scan: **KB-BIJECTION PASS** (B1, B2 closed)
- Dependency-form scan: **KB-EXPLICIT RED** (E1 closed; new X1 task-mirroring example in `hours_draw_and_service_billing_bfbe74de.json` Clause 4)

## revision_3

Round-3 re-audit, 2026-10-05 (~12:00Z). Source, tools, task JSONs, views and DB access unchanged since revision 2. Coordinator gate lines: DOCS OK (49 docs); TRACEABILITY OK. Revision 1–2 text untouched.

### What changed in the corpus

Content lengths were compared document by document against revision 2 (all 49 present, none added or removed). Five documents changed length (`hours_draw_and_service_billing_bfbe74de`, `share_of_the_previous_suspension_70f12af8`, `package_fees_and_monthly_hours_04c4feb4`, `account_standing_and_suspension_length_1f654a81`, `illness_relief_on_shortened_visits_e0b96f08`). Two changed with the same length (`goodwill_on_repeat_service_disputes_005b6c47`, `booked_hours_and_laundry_basis_db122a5e`). In all seven the rule/clause/ladder/definition sections were re-read and are identical to revision 2; only the hypothetical examples differ. The documents carrying B1/B2/B3/E1 (`suspension_length_calculation_14825d7c`, `counting_time_in_force_dded501d`, `recent_month_use_trend_deb73bdc`, `required_hours_and_package_fitting_a9ca1c11`) keep their revision-2 content length, so the passages verified as closed in revision 2 are untouched.

### X1 — closed

`hours_draw_and_service_billing_bfbe74de.json` Clause 4 now reads: "*Hypothetical illustration:* a visit counted at 1.75 hours on a plan with 0.25 hour available draws the 0.25 hour and charges the other 1.5 hours as one hourly charge on the same order; at a hypothetical hourly rate of 50.00 USD that charge is 75.00 USD." Arithmetic correct (1.5 × 50.00 = 75.00). 50.00 is no tier's rate. Neither 1.75/0.25/1.5 nor 75.00 matches any task-0 or task-1 record. **Closed.**

### Changed examples — faithfulness and task-mirroring check

| Document | New example | Faithful to its rule? | Mirrors a task's records? |
|---|---|---|---|
| `share_of_the_previous_suspension_70f12af8` | January–February suspension within a rehab absence 20 Dec – 10 Mar → none counted; other examples unchanged (2×0.5=1; 1.5→1; 0.5→0) | yes (start on/before the first day, return on/after the last day → share 0) | no (task 0's suspension was March–April 2026, and its absence starts 2026-09-24) |
| `package_fees_and_monthly_hours_04c4feb4` | Companion: 3 further hours × 44.00 = 132.00; Premier 3 × 40.00 = 120.00 | yes (rate card figures) | see observation O1 |
| `account_standing_and_suspension_length_1f654a81` | hypothetical fees 3 × 300.00 + 120.00 + 18.00 = 1038.00; payments 600.00 + credit 70.00 = 670.00; balance 368.00; less 300.00 → 68.00 → 1 month; without the credit 138.00 → 2 | yes (all sums check; 300.00 is no tier's fee) | no |
| `illness_relief_on_shortened_visits_e0b96f08` | 3 h booked, 90 min, 1.50 h: +2 days → 0.75; +6 days → 1.20; 1.25 h, +1 day → 0.625 → 0.63 | yes (tiers 0–3 → 0.5, >3–7 → 0.8; rounding only after the multiplication) | no (task 0: 2 h booked, 70 min, +5 days) |
| `goodwill_on_repeat_service_disputes_005b6c47` | 70−30+25 = 65 (≤ 70); 48−24+25 = 49 → cap 48; 48/48 → nothing | yes | no (the former 44.00 figure, equal to task 0's July charge, is gone) |
| `booked_hours_and_laundry_basis_db122a5e` | laundry 0.25 h booked → basis 0.25 (fewer than band 1.0) | yes | no (the former 0.75-hour row, equal to task 1's booked hours, is gone) |

Observations (not RED; recorded so the record is complete):
- O1: the rate-card example's 132.00 equals the sum of task 0's two hourly charges (44.00 + 88.00, 3.0 h at the Companion rate). It is a single generic multiplication of the card's own figure (hours × the tier's rate), with no ledger structure, order, or available-hours setup. It does not restate a record. (The revision-1/2 version, "two further hours … 88.00 USD", equalled task 0's 88.00 charge; I did not record it then; it has since been replaced.)
- O2 (pre-existing since revision 1, unchanged): `counting_time_in_force_dded501d.json` example "a plan [that] took effect on 1 March 2024 and was suspended for March and April 2025" shares task 0's plan effective date (2024-03-01) and the months of its earlier suspension (March–April, 2026 in the record). The example's resident is independent living, its suspension year differs, and its method row (effective date less suspension) is not task 0's. It does not restate task 0's records, but the overlap is noted.

### source_to_kb / kb_to_source (revision 3)

No normative sentence changed. All revision-2 judgements stand: every rule and ladder is carried and every retired clause is shown retired. The prerequisite sentence is still verbatim and only in the blocked hub, and each tool name still appears only in its own hub (corpus-wide scan re-run). There is no addition or cross-problem guidance, and no task world state in any example (scan for task figures and identifiers re-run: only O1/O2 above).

### bijection_verdict (revision 3)

**PASS** — nothing regressed.

### dependency_form (revision 3)

X1 closed; no new route, aggregation, tool naming, chain example or task-mirroring example; E1 still absent ("as the standard": 0 hits).

**Verdict revision 3: KB-EXPLICIT PASS.**

## part_verdicts (task 0, revision 3)

- Runtime: **KB-RUNTIME PASS** (not blind)
- Full-domain two-way scan: **KB-BIJECTION PASS**
- Dependency-form scan: **KB-EXPLICIT PASS** (X1 closed)

## difficulty_closing (revision 3)

All three parts PASS for task 0 and task 1 (revision 3). Closing checklist:
- Audit files correspond one-to-one with tasks 0 and 1 in both `runtime_context/` and `policy_kb/`; revisions 1–3 are kept in order, older text unchanged.
- Every normative atom of the round-4 source in scope is carried by `docs/services` with no omission, change of meaning or addition.
  - Both prerequisite sentences stand verbatim, in state form, only in the hubs of the policies they block, and each hop resolves from that sentence, the depended-on hub and the records.
  - Every declared factor ladder is complete and can be found from record words.
  - No other problem's tool name, no route and no aggregated chain appears anywhere.
- Final-form gate re-run by the auditor (2026-10-05 ~12:05Z):
  - `.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0034_senior_living_operator services` → `[PASS] mechanical gates …` / `DOCS OK`
  - `.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0034_senior_living_operator/tasks/personal_services_packages` → `TRACEABILITY OK`
- Caveat on record: the revision-2/3 runtime derivations are not blind (disclosed); the revision-1 blind derivation was clean, and the round-4 changes it predates are covered by the non-blind re-derivation and the GT match.
