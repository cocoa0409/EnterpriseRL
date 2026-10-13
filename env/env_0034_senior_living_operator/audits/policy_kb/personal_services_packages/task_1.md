# Policy-KB bijection audit — personal_services_packages / task 1

## revision_1

Auditor: erl-kb-doc-policy-audit sub-agent, round 1, 2026-10-05. Written after the blind answer in `runtime_context/personal_services_packages/task_1.md` was frozen.
Source: `tasks/personal_services_packages/services.extended.yaml` (policies in scope: `services_ext_package_fit` (root), `services_ext_missed_visit_hours` (prerequisite), base `services_package_change`, `services_late_cancellation`, `services_hours_and_billing`; tier parameters read), `task_tools.py` (`sign_services_package_change_2a41e92a`, `post_services_order_hours_8d682fe6`). Corpus: `docs/services/*.json` (title/content; meta only to locate homes).

### Entry conditions (Step 0)

As for task 0 (policy-side PASS round 3; DOCS OK; TRACEABILITY OK; instantiation gates OK; runtime view and DB access path supplied with hashes, re-verified). Input complete.

## source_to_kb

### A. `services_ext_package_fit` (root, on_request)

Hub `package_fit_requests_38bd82e6.json`: rule sentence 1 (lowest package whose monthly hours allotment is at least the required hours, among the packages the residence allows; assisted living never above Companion; effective first day of next month if signed by the cutoff day, else the month after next), the prerequisite sentence, what the signed change records, and the invocation block of `sign_services_package_change_2a41e92a` (customer's own tool; `services_plan_id`, `target_variant_name` with the seven enum values incl. `none`, `pending_change_date` YYYY-MM-01; return keys) — all match the source and `task_tools.py`.

Computation document `required_hours_and_package_fitting_a9ca1c11.json`:

| Baseline atom | KB home | Judgement |
|---|---|---|
| Hours used = hours drawn + hours charged beyond the allotment for delivered visits, posted within the 3 whole months before the request | Clause 1 | equivalent |
| Review months counting (fewer than 3 whole months elapsed; same-day boundary outside, next day inside) | Clause 2 + boundary table (15 June out / 16 June in / 14 Sept in) | equivalent |
| "…; the last whole month before the request is counted the same way with one month." | **not in the computation document**; carried in factor doc `recent_month_use_trend_deb73bdc.json` ("Last whole month. The last whole month before the request is counted in the same way as the review months, with one month …", window boundary 15/16 August) | **misplaced** — finding B3 |
| Average = hours used ÷ 3; required = average rounded to 2 dp half up | Clause 3 | equivalent |
| Fitting: lowest package whose allotment ≥ required among the packages the residence allows; assisted never above Companion; residence = the one the plan serves | Clause 4, worked example, "A required-hours figure of zero is met by a package whose allotment is zero" (derivation: PAYG allotment 0, compute `required_hours <= 0 → Pay-As-You-Go`) | equivalent |
| Product figures: monthly_hours_allotment, change_notice_cutoff_day; own constant review_months 3 | allotment named, values in facet `package_fees_and_monthly_hours_04c4feb4.json` (0/4/8/12/20/30); cutoff in hub + facet `enrollment_commitment_and_notice_terms_8240773d.json` (20); 3 stated | equivalent; fall-back definite (task 1: Essentials) |

Extended-rule atoms outside the baseline:

| Atom | KB home | Judgement |
|---|---|---|
| "The required hours are the average monthly use plus the headroom and the trend adjustment, rounded …, and the package is fitted on that figure." | distributed: headroom doc "The headroom is added before the required hours are rounded"; trend doc "The adjustment is made before the required hours are rounded"; late-entries doc "added to the hours used"; divisor doc "the divisor of the average monthly use"; trend doc "The comparison is made with the average monthly use as calculated, before any rounding" | entailed (addition is order-free; single rounding at the end) |
| Prerequisite sentence | hub, section "When the package is chosen" | see C |

Factors:

| Factor | Document | Ladder | Judgement |
|---|---|---|---|
| `review_divisor` (change in window → fees for package now in effect; no change and < 3 fees → fees posted; else 3; never < 1) | `months_counted_in_the_use_average_f8a8f7a9.json` | 3 methods, records read (package fee entries, charged on a package change, package charged for), "never less than one" (compute `MX(1, …)`) | complete |
| `missed_visit_use` (≥ 2 entries → in full; 1 → 0.5; 0 → none) | `late_cancellation_hours_in_measured_use_a778077a.json` | all tiers, entries drawn or charged, posting date in the review months | complete |
| `home_headroom` (Cottage Home / Two-Bedroom Deluxe → 1.5; other type double with second occupant named → 1.0; else 0) | `home_size_and_shared_occupancy_headroom_24b3b613.json` | all tiers incl. "Double / No", "Single", "No active independent living residency"; names the Independent Living Residency Agreement and the fields read | complete |
| `use_trend` (≥ 2.0 above → +2.0; ≥ 2.0 below → −1.0; else 0; last whole month; every draw and hourly charge whatever the reason) | `recent_month_use_trend_deb73bdc.json` | all tiers with figures, boundary 8.0/7.75/4.25/4.0, window definition | complete |

Base `services_package_change` (`package_change_terms_f0edcd33.json`): all seven source clauses (effective date by cutoff, one pending change, commitment for a move down, counting the commitment, change-date effects, assisted-living limit, active-only) are carried with the 20th-cutoff and 3-month commitment boundary tables. `overwrite: []` and nothing in the document is marked retired. Equivalent.

### B. `services_ext_missed_visit_hours` (prerequisite, state_due)

Hub `hours_for_late_cancelled_and_missed_visits_9a3ce491.json`: posted by the desk once the cancellation/no-show is on record, one order at a time from the most recently recorded, against that order with its own draw basis and the billing month of its service date, from available hours or charged at the hourly rate where none remain; invocation block of `post_services_order_hours_8d682fe6` (agent-side; seven parameters, enums, "dated today", return keys) matches `task_tools.py`.

Computation document `missed_visit_hours_owed_7351ca1d.json`: the same posting rule; "A cancellation received two or more calendar days before the visit owes no hours and is not posted"; band hours = the package's late-cancellation hours; hours owed = band hours rounded to 2 dp; no weekend/holiday surcharge (extended-rule sentence, rendered here); booking from available hours or charged. Product figures named (late-cancellation hours → facet `cancellation_and_no_show_hours_schedule_5e9e3107.json`; hourly rate → rate card). Complete; fall-back definite (task 1: 0.50).

Factors:

| Factor | Document | Ladder | Judgement |
|---|---|---|---|
| `missed_visit_band` (no-show → no-show hours; day-before cancellation → late-cancel hours × 0.5; same-day → late-cancel hours) | `day_of_cancellation_hour_bands_b359a969.json` | all tiers, per-package table, 0.5 stated, calendar-day reading | complete |
| `missed_visit_basis` (booked < band → booked; laundry ≥ band → band × 0.5; else band) | `booked_hours_and_laundry_basis_db122a5e.json` | all methods, 0.5 stated | complete |
| `cancellation_pattern` (≥ 2 → 1.2; 0 → 0.5; 1 → 1; 6-month look-back to the posting date) | `recent_cancellation_record_multiplier_942fd825.json` | all tiers, entries drawn or charged, look-back boundary 21/20 Feb | complete |
| `rebooking_relief` (0–2 days → 0.25; >2–7 → 0.6; else 1; latest booking of the same service) | `rebooking_after_a_missed_visit_09724240.json` | all tiers, boundary 9/10/12/13/17/18 June | complete |
| `entrance_hours_reduction` (lifecare 0.20; fee-for-service 0.10; else 0) | `life_plan_reduction_on_missed_visit_hours_90c03d04.json` | all tiers; names the Entrance Fee Agreement and contract type | complete |

Order of work ("basis × pattern, then × rebooking, then − entrance reduction, remainder never below zero, rounded to 2 dp"): pattern doc "multiplied … before they are rounded"; rebooking doc "multiplied … before they are rounded"; reduction doc "subtracted … after every multiplication of those hours has been made; the remainder is never below zero and is rounded … only after the subtraction"; basis doc "worked from the visit's basis hours". Multiplication order is immaterial; the subtraction, floor and single rounding are pinned. Entailed.

Overwrite / retired surface (2 superseded clauses of `services_late_cancellation`): both shown as "Retired wording, no longer in force" in `visit_cancellation_terms_54ef176b.json`; the in-force terms 1–4 (right to cancel, no surcharges, hospital admission exemption, one cancellation per order) are the unretired source clauses. Base `services_hours_and_billing` (also a base ref here) as recorded in task 0: retired surface correct. PASS on the retired surface.

### C. Prerequisite edge `services_ext_package_fit → services_ext_missed_visit_hours`

- `policy_source`: "The package that fits the resident's use is not chosen until every service order recorded in the review months as a late cancellation or a no-show carries its hours entry for that cancellation on the plan's ledger."
- Carried verbatim (exact string match) in the blocked hub `package_fit_requests_38bd82e6.json`, section "When the package is chosen", with a same-form "Put another way" restatement. Form: state; connective "not … until" intact; strength: hard gate.
- No other document carries it (corpus-wide scan over every product: 1 hit).
- Resolution basis: depended-on hub states its own rule in the sentence's words — "Each posting is one hours entry for that cancellation on the plan's ledger", "posted by the Resident and Family Services desk once the cancellation or no-show is on record" — plus the records (SO-2610-1064 `cancellation_type 'no_show'`, no ledger row with that order reference). The depended-on documents do not disclose who waits on them. `condition`, `resolved_by`, `effect` appear nowhere.
- Judgement: carried at the same strength and form.

## kb_to_source

- Every normative sentence of the 13 documents of the two policies, the two base documents and the facets they name traces to the source or is a provable derivation (boundary tables; "The divisor is never less than one" from `MX(1, …)`; "A required-hours figure of zero is met by a package whose allotment is zero"; "Every hours draw and every hourly charge … whatever the reason" from the unfiltered `latest_month_hours`; "the calendar day is the date part of that moment").
- Additions (confirmation, review, notification, failure procedure): none.
- Cross-problem operational guidance: none — the fit hub names only `sign_services_package_change_2a41e92a`; the posting hub names only `post_services_order_hours_8d682fe6`.
- A task's opening world state written as a policy fact: none (all examples hypothetical).
- Omission/misplacement: B3.

## bijection_verdict

**KB-BIJECTION RED** (task 1, revision 1) — one finding, no task-1 number affected.

**B3 — a baseline window clause of the fit policy is homed in a factor document, not in the computation document.**
- Symptom: the computation document defines the review months but not "the last whole month before the request", which `baseline.rule` defines alongside them.
- Root cause: `baseline.rule` ends its review-months sentence with "; the last whole month before the request is counted the same way with one month."; the corpus renders this only in `recent_month_use_trend_deb73bdc.json` ("**Last whole month.** The last whole month before the request is counted in the same way as the review months, with one month: …"), and `required_hours_and_package_fitting_a9ca1c11.json` Clause 2 stops at the review months.
- Entailment at corpus level is preserved; this departs from "the computation document carries `baseline.rule` complete".
- Nature: source-induced — the clause sits in `baseline.rule` but only the `use_trend` factor reads it; stated in the computation document it would announce a last-month adjustment (policy-side note N6).

No relation to previous revisions (first revision).

### Policy-side notes (do not change this skill's verdict)

- N6: `services_ext_package_fit.baseline.rule` contains a window that only a factor consumes (root of B3).
- N7: the fit rule ("the lowest package whose monthly_hours_allotment is at least the required hours") is silent when the required hours exceed 30; the compute returns the Concierge Package. The corpus is silent in the same way (render Value 0) — not a document defect.
- N8: `late_cancel_notice_hours` keeps its description "Hours before the scheduled start below which a cancellation is late" although the hour-based lateness clause is retired and lateness is now read in calendar days; the facet `cancellation_and_no_show_hours_schedule_5e9e3107.json` renders the description faithfully ("the notice period below which a cancellation of a booked service visit is late", 24 hours). `missed_visit_hours_owed_7351ca1d.json` ("counted in calendar days …, not in hours") and the retired-clause notice resolve it for a careful reader.
- N5 (as task 0) applies to `entrance_hours_reduction`: the contract type is a variant parameter, visible through the background / entrance corpus.

## dependency_form

Blind hop marks (frozen): P1 → P2 **state-derived**; no hop pre-solved. Whole-corpus scan:

| Check | Result |
|---|---|
| Prerequisite sentence verbatim on the blocked side, state form kept | yes — `package_fit_requests_38bd82e6.json`; "Put another way" restatement keeps the state form, names no action, performer or tool |
| State-form sentence restated as an action / performer / other problem | none |
| Other problem's tool named outside its own hub | none |
| Dependency or order between problems beyond the source sentence, or in a second document | none |
| Aggregated table / checklist / route / ordered step list | none |
| Wrong-vs-correct contrast, named mistake, chain-walking example | none |
| Titles / openings mirroring a task | none; "Moving to the Package That Fits a Resident's Use" names the on_request policy's own request type |
| Depended-on document reachable only via the dependent's phrasing | no — "no-show errand hours owed", "late cancellation no-show entries" return the posting hub, its computation document and factors |
| Factor document stating a tier, a mistake to avoid, or evidence rows as fact | none |
| Computation documents hinting at modification | none (`required_hours_and_package_fitting_a9ca1c11.json`, `missed_visit_hours_owed_7351ca1d.json`) |
| Factor document naming / pointing at the computation document or another factor | none. Examined and not RED: `life_plan_reduction_on_missed_visit_hours_90c03d04.json` "after every multiplication of those hours has been made" — the minimal carriage of the source's order atom for this factor's own step, quantifying over multiplications without asserting any or naming a document; `recent_month_use_trend_deb73bdc.json` "counted in the same way as the review months" — the source's own wording ("counted the same way"), restated in full mechanics in the same paragraph, naming no document |

**Verdict: KB-EXPLICIT PASS** (task 1, revision 1).

## part_verdicts (task 1, revision 1)

- Runtime blind audit: **KB-RUNTIME PASS**
- Full-domain two-way scan: **KB-BIJECTION RED** (B3 baseline "last whole month" clause homed in a factor document)
- Dependency-form scan: **KB-EXPLICIT PASS**

## revision_2

Round-2 re-audit, 2026-10-05 (~11:55Z); inputs as in task 0 revision_2. Revision 1 text untouched.

### Closure of round-1 findings

| Item | Round-2 evidence | Status |
|---|---|---|
| B3 "last whole month" clause | The source moved it out of `baseline.rule`: the fit `baseline.rule` now ends at "…rounded to two decimal places half up", and the trend sentence of the rule carries "a posting falls within the last whole month before the request when less than one whole month has elapsed from its posting date to the request date, a whole month elapsing on the same day of the next month". KB: `recent_month_use_trend_deb73bdc.json` states the same window on its own terms (boundary 15/16 August), no longer by reference to the review months; the computation document carries exactly the new `baseline.rule`. | **closed** |
| N7 (policy-side) | Source rule/baseline now adds "and where the required hours exceed every allotment an independent living resident is fitted to the Personal Services Concierge Package"; rendered in the hub and the computation document (clause 4). | rendered |
| N8 (policy-side) | Missed-visit `baseline.rule` now adds "lateness is read in calendar days, so the package's late_cancel_notice_hours plays no part under this rule"; rendered in `missed_visit_hours_owed_7351ca1d.json` clause 1. | rendered |
| N5 | Entrance reduction ladder names the plans; rendered in `life_plan_reduction_on_missed_visit_hours_90c03d04.json`. | rendered |

### source_to_kb / kb_to_source (revision 2, changed surface)

- Fit: `baseline.rule` (incl. the Concierge clause) → computation document clauses 1–4; the four factor ladders are unchanged and complete. Missed-visit: `baseline.rule` (incl. the calendar-day sentence) → computation document; the five ladders are unchanged and complete. Prerequisite sentence unchanged, verbatim, state form, only in `package_fit_requests_38bd82e6.json`.
- Base documents touched by the re-render (`hours_draw_and_service_billing_bfbe74de.json`, which is a base ref of the missed-visit policy) match the base rule text, now fully in force.
- No addition, omission or change of meaning; no cross-problem guidance; no task-1 world state in any document (string scan for task-1 figures and identifiers: none).

### bijection_verdict (revision 2)

**PASS** — B3 closed; nothing regressed.

### dependency_form (revision 2)

All checks repeated: prerequisite carriage, tool names, routes, aggregation, titles and computation-document silence all still clean. The trend document no longer refers to the review months. X1 (task 0 revision_2) is a corpus-level example that mirrors task 0's records, not task 1's; it is recorded on task 0.

**Verdict revision 2: KB-EXPLICIT PASS.**

## part_verdicts (task 1, revision 2)

- Runtime: **KB-RUNTIME PASS** (not blind)
- Full-domain two-way scan: **KB-BIJECTION PASS** (B3 closed)
- Dependency-form scan: **KB-EXPLICIT PASS**

## revision_3

Round-3 re-audit, 2026-10-05 (~12:00Z); inputs and change inventory as in task 0 revision_3 (seven documents changed only in their hypothetical examples; rule, ladder and invocation text identical to revision 2). For task 1's policies the changed example is `booked_hours_and_laundry_basis_db122a5e` (laundry 0.25 h → basis 0.25, faithful; the former 0.75-hour row, equal to SO-2610-1064's booked 0.75 h, is gone). The missed-visit and fit documents are otherwise unchanged; the B3 passage is untouched. The prerequisite sentence and tool-name scans were re-run (unchanged), and no task-1 figure or identifier appears in any example.

- bijection_verdict (revision 3): **PASS** — nothing regressed.
- dependency_form (revision 3): **PASS** — no new defect.

## part_verdicts (task 1, revision 3)

- Runtime: **KB-RUNTIME PASS** (not blind)
- Full-domain two-way scan: **KB-BIJECTION PASS**
- Dependency-form scan: **KB-EXPLICIT PASS**

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
