# Policy-task audit — warranty_claims_and_transfers / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), run 2026-10-13, scratch /tmp/audit_d4_0060/.
- Frozen inputs (sha256, re-verified at start of audit, identical to the coordinator brief):
  - `afecc2adf1eb63897f8d541105b1a412e87f6d35721fcc3dcc390169cca917c8  warranty.extended.yaml`
  - `1aa601f78ac8e9e0cafd96048e20a3ffe94e7ad20891322af9c47eb136ac746d  task_tools.py`
  - views `0.view.json` 3bb2d4fb…7441, `1.view.json` da1a57e1…b7d9 (match the brief).
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py` (signatures), `blueprint/products/warranty.yaml` and the cross-read products `service.yaml`, `window.yaml`, `install.yaml`, `order.yaml`, `door.yaml` (parameters/events/policies only); the extended charter; `task_tools.py`; the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, `MONTHS`, `DAYS`, `RND`).
- Masked and unread while this section was written: everything in `tasks/*.json` other than the masked views (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`). Nothing in this section is derived from a revealed GT.
- Entry conditions (Step 0): gate snapshot supplied (all green except TRACEABILITY, deferred for unrendered docs — tool-name provenance only; validate_scenario errors only "required document not found"); masked views supplied with hashes; frozen artifact hashes supplied. Complete.

### policy_conflict_scan

Five extended policies, one per target tool:

| policy | target_tool (owner) | computes | trigger | prerequisite |
|---|---|---|---|---|
| warranty_ext_missed_visit_fee (P1) | bill_missed_visit_fee_18fefa1f (agent) | amount (no_show_fee) | state_due | [] |
| warranty_ext_visit_trip_billing (P2) | bill_visit_trip_5cd049ac (agent) | amount (trip_charge) | state_due | P1, value_input, gate missed_visit_credit |
| warranty_ext_transfer_fee_confirmation (P3) | confirm_coverage_transfer_ce1107bd (user) | transfer_fee | on_request | P2, state_gate |
| warranty_ext_visit_labor_billing (P4) | bill_visit_labor_b6354c72 (agent) | amount (labor_charge) | state_due | [] |
| warranty_ext_prorated_share_acceptance (P5) | accept_prorated_glass_share_5fbbc0c6 (user) | share_amount (prorated_parts_share) | on_request | P4, value_input, gate visit_credit |

- Base copy: every top-level key of the base charter (`category` … `policies`) is `==` identical to `blueprint/products/warranty.yaml` (python yaml compare, /tmp/audit_d4_0060/mech.py). PASS.
- Overlapping subjects: all five write `warranty_charge_assessed` but each a distinct `charge_kind` (no_show_fee / trip_charge / transfer_fee / labor_charge / prorated_parts_share); P2 and P4 both overwrite the same base clause of `warranty_service_charges` and each names the other's quantity as outside its scope ("the labor billed on such a visit is not set by this policy" / "the trip charge on such a visit is not set by this policy"). No two policies set the same quantity.
- Time anchors: P1 and P2 date their charges with the visit date; P4 likewise; P3 and P5 book on the handling date (tool body `ctx.now()`), consistent with their rules ("the confirmation date as the date the transfer was requested"; "on the date the owner accepts").
- Cross-category reads are all branch/history reads of service, install, order, window, door holdings scoped to the customer (`_cross` / `_xrows` filter on `customer_id`), none writes outside warranty.
- Scope claim: two task roots are visible in the views — task 0 is a transfer confirmation (P3 root), task 1 a prorated-share acceptance (P5 root). The prerequisite graph splits the five policies into two connected components {P1,P2,P3} and {P4,P5}; on that reading the claimed scopes are pairwise disjoint and jointly cover the charter. (Confirmed against `charter_scope` only after reveal, in the task files.)
- No conflicting conclusions found between extended policies on overlapping subjects. One base-vs-extended latent issue is listed under findings (F-G3: a zero trip charge vs the P3 gate and the tool's "positive amount").

### rule_compute_equivalence

Mechanical sweep (/tmp/audit_d4_0060/mech.py): every `compute_basis` value is a verbatim substring of its policy's `rule` (whitespace-normalised); `compute_basis` keys == compute binding names for all five; every `baseline.rule` sentence is a sentence of the `rule`; every `superseded_clause` is verbatim in the named base rule and every `replaced_by` verbatim in the extended rule.

Semantic sweep, policy by policy (rule sentence -> binding):
- P1: claim/visit selection, CareLine-ready test (`DAYS(enrolled, missed_date) > waiting_period_days` = "waiting period had ended by the date of the missed visit", consistent with service charter "benefits begin on the day after the last waiting day"), three counting tiers, repeat place = counted − free count, fee schedule tiers, day rate via `DAYS(ref_sunday, date) % 7` (2026-01-04 is a Sunday — verified), crew tiers, zero when place < 1. Each tier stated in the rule and implemented. One divergence: the rounding sentence (F-G1). One reading gap: "dated less than the member counting window in whole months before the date the fee is billed" is implemented with `within_months` measured to NOW (handling date), while the same rule dates the fee "with the date of the missed visit" (F-O2).
- P2: standard trip (no-defect vs out-of-term), CareLine free-trip / lower-of / standard tiers, plan year `MONTHS(enrolled, visit)//12+1`, crew, day, access (upper-story fee × method), handling (build class), program discount, rebook credit (latest no-show on the same claim, 0 < days ≤ 30), order of operations `(trip×crew×day + access + handling) × (1 − discount) − credit`, floor 0. Implemented as stated. Rounding sentence: F-G1.
- P3: request on file, closing date, days after closing to NOW, timing tiers (≤10 → ×0.8; >30 → +25; else flat), size tiers (≥20 / ≤5 / else), member tiers (CareLine ≥12 whole months → 0; CareLine <12 → 0.5; else 1; On-Call excluded as "CareLine"), remaining-term share (≤0 → 0; <24 → m/24; else 1), product, zero when no request on file. Implemented. The state gate ("is not placed in transfer pending, and its fee is not charged, until …") has no compute branch — it governs whether/when to act, not the amount (observation F-O4). Rounding: F-G1.
- P4: billable hours by three methods, unit-count minimum, lead-safe allowance, crew rate, crew-hours `RND(…,1)` ("stated to one decimal place"), discounted rate, day rate. Implemented. Rounding: F-G1. A naming gap between "billable labor hours" and "billed crew-hours" for the tool's hours argument is F-O6.
- P5: proration share from plan + full years to filing date (K constants reproduce the variant ladders: Limited 0.5 from year 5, Limited Plus 0.5 from year 10, Lifetime Limited 0.25 from year 10, others 0 — checked against `variants[].insulated_glass_proration`), build-class glass charge, insulating/glazing add-ons on change orders covering every opening, volume rate, owner discount (CareLine parts discount if ready by acceptance date, else contract program rate), visit credit (≤30 days trip+labor, ≤60 trip, else 0) on this claim only, order `share×(charge+addons)×units×(1−vol)×(1−disc) − credit`, floor 0. Implemented. Rounding: F-G1.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are unique across the five policies; no base policy has a target_tool.
- Tool bodies (task_tools.py) perform one write each with the caller's value; none reads a prerequisite, refuses, errors or hints (bodies only `find` the registration/claim to copy `customer_id`/`component`). PASS.
- Docstrings: no concrete example value (only format words: YYYY-MM-DD, "2 decimal places", "1 decimal place"); no ordering words (grep for before/after/first/then/prior over task_tools.py: no hit); no other tool named; effects claimed are present in the bodies (component copied, one row created, status/transfer_requested_date set for the confirm tool, request row untouched). The docstrings repeat "rounded half up" (F-G1) and describe bill amounts as "a positive amount" (F-G3).
- uuid8s: 18fefa1f, 5cd049ac, ce1107bd, b6354c72, 5fbbc0c6 — five distinct, no shared prefix/suffix, no arithmetic progression, not derived from one another. PASS.
- No factor id is a substring of any tool name (mechanical check). PASS.

### prerequisite_graph

- `prerequisite` present on all five (P1 [], P4 []). Edges: P2→P1, P3→P2, P5→P4. Each `problem` is another extended policy id in this file; no self-edge; acyclic (two chains of length ≤2).
- `policy_source` verbatim in the blocked policy's own rule for all three edges (mechanical). `form: state` on all three; no `fallback_reason` (none needed).
- `resolved_by` equals the depended-on policy's target_tool on all three.
- `kind`/`gate`: P2 edge value_input → `missed_visit_credit` (a real binding); P5 edge value_input → `visit_credit` (a real binding); P3 edge state_gate → `warranty_activities.charge_kind`, a field name, not an eligibility gate id (extended policies carry no `eligibility` list); observation F-O4.
- `condition` vs sentence: P2's condition is narrower than its sentence (F-O3); P3 and P5 conditions match their sentences.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any prerequisite field.

### prerequisite_sentences

- P2 ← P1: "The trip charge of a visit that rebooks a chargeable missed visit on the same claim is fixed only after the records carry the no-show fee entry for that missed visit." Ordering connective "only after"; waited-on state is record-visible (a no-show fee entry on the warranty charges for that missed visit); no tool, id or snake_case token. The one write of this difficulty that creates a `charge_kind=no_show_fee` row is bill_missed_visit_fee_18fefa1f (share_tools.py has no warranty write; the other four task tools write trip/transfer/labor/share kinds). Reader's derivation: sentence → "a no-show fee entry for that missed visit" → P1's rule "prices the no-show fee for a missed technician visit … and books it on the warranty charges … dated with the date of the missed visit" → bill the no-show fee first. Single reading. Scope: sentence carries no rebooking-window bound, condition does (F-O3).
- P3 ← P2: "A transfer request is not placed in transfer pending, and its fee is not charged, until every completed technician visit on the registration that the warranty terms bill a trip charge for carries its trip charge entry on the warranty charges of the registration." Connective "until"; state form; unique writer of `trip_charge` rows is bill_visit_trip_5cd049ac. Derivation: sentence → visits billed a trip "under the warranty terms" (base: outside the labor term, or no covered defect found) lacking a trip entry → P2's rule prices exactly that trip charge. Single reading. Realism: settling outstanding service charges before a coverage transfer is ordinary practice.
- P5 ← P4: "The owner's share of a prorated replacement is fixed only after the records carry a labor charge entry for every technician visit on the claim that the warranty terms bill labor for." Connective "only after"; state form; unique writer of `labor_charge` rows is bill_visit_labor_b6354c72. Single reading.
- No rule restates another policy's prerequisite sentence; no rule names another tool or policy id; no base sentence grounds an edge; no cross-problem order is stated in any rule without a declared edge.

### override_declarations

Sentence-by-sentence against each extended policy's `base_policy_refs` (all five list the same five base policies; the quantities touched are in `warranty_service_charges`, `warranty_transfer`, `warranty_proration`).

- `warranty_service_charges`
  - "An approved claim is remedied by a technician visit … or … by shipping the parts …" — followed by all.
  - "A visit inside the labor term carries no labor or trip charge for the covered repair." — kept verbatim in sense by P2 ("a visit inside the labor term at which a covered defect is repaired still carries no trip charge") and P4 ("a visit inside the labor term still carries no labor charge for the covered repair").
  - "A visit outside the labor term carries the plan's out-of-term trip charge plus labor at the plan's hourly rate …" — overwritten twice, by P2 (trip part) and P4 (labor part); each replaced_by names its own scope and excludes the sibling's. Declared.
  - "When the technician finds no covered defect, the plan's no-defect trip charge applies even inside the labor term." — overwritten by P2; the still-in-force part (a no-defect visit is billed a trip even inside the labor term) survives in P2's scope sentence ("a visit outside the labor term or a visit at which the technician found no covered defect") and standard-trip sentence. Declared.
  - "A visit where nobody gives access … no-show; … up to the plan's free count … no fee and each later one carries the plan's no-show fee." — overwritten by P1, replaced_by keeps "a visit where nobody gives access within the wait time is still the no-show, and the plan's free no-show count still applies". Declared. Note: base measure `warranty_msr_no_shows` window is "up to and including the visit being handled"; P1's fall-through counts "all the no-show visits recorded on the registration" — declared as part of the replaced counting ("in place of the registration's lifetime count").
  - Parts shipment fee, discontinued parts — untouched.
  - Base `formula.labor_charge: round(rate * max(min, hours), 2)` omits the increment rounding its own rule states — base-internal, superseded for P4's scope (observation F-O7).
- `warranty_transfer`
  - "The plan's transfer fee is charged to the seller on the request date." — overwritten by P3, declared; every other transfer condition expressly inherited.
  - P3 sets "the confirmation date as the date the transfer was requested"; this matches the base event `warranty_transfer_requested` (active→transfer_pending, field transfer_requested_date) which is what the confirm tool writes. No undeclared override.
- `warranty_proration`
  - Share sentence and booking-date sentence — overwritten by P5, both declared. "A share of zero books nothing." — kept verbatim.
  - The base event `warranty_claim_decided` carries a trigger to `warranty_charge_assessed` (prorated_parts_share) on the decision date; P5 moves booking to acceptance. The trigger is a base `events` entry, not a policy sentence; whether the seed carries a decision-date share row is checked per task.
- `warranty_agg_claims_per_registration`, `warranty_glass_breakage`: followed (all aggregates are holding-scoped, per-claim filters used).
- No anonymous intermediate factor, 0/1 multiplier or dropped branch found beyond the declared overwrites. One exception at the charter-text level: P3's remaining-term share zero tier ("When none remain … the remaining-term share is zero") is a 0 multiplier, but it is declared inside P3's own overwrite scope ("adjusted by the paragraphs below").

### factor_ladders

| policy | factor | effect | tiers | decides | multi-source (check_compute.multi_source) | cross_difficulty |
|---|---|---|---|---|---|---|
| P1 | counting_window | method | 3 | missed_counted | no | service |
| P1 | repeat_rate_ladder | parameter | 3 | repeat_rate | no | – |
| P1 | fee_schedule | parameter | 3 | schedule_fee | no | service |
| P1 | weekend_day_rate | parameter | 3 | day_rate | no | – |
| P1 | crew_rate_ladder | parameter | 3 | crew_rate | no | install |
| P2 | member_trip_rate | method | 3 | trip_rate | no (tool) / yes by reading: plan + plan-year service_calls | service |
| P2 | crew_size_rate | parameter | 3 | crew_rate | no | install |
| P2 | weekend_visit_rate | parameter | 3 | day_rate | no | – |
| P2 | upper_story_access | parameter | 3 | access_surcharge | yes (install_activities fee × install job method) | install |
| P2 | build_class_handling | parameter | 3 | handling_surcharge | no | order |
| P2 | signing_program_discount | parameter | 4 | program_discount | no | window |
| P3 | request_timing_rate | parameter | 3 | timed_fee | no | – |
| P3 | coverage_size_rate | parameter | 3 | size_rate | no | window |
| P3 | careline_member_rate | parameter | 3 | member_rate | no | service |
| P3 | remaining_term_share | method | 3 | term_share | no | – |
| P4 | labor_hours_method | method | 3 | billable_labor_hours | no (tool) / tier 1 reads visit row + charge rows | – |
| P4 | unit_count_minimum | parameter | 3 | labor_minimum | no | – |
| P4 | lead_safe_hours | parameter | 3 | lead_safe_allowance | yes (install fee × claim component) | install |
| P4 | technician_crew | parameter | 3 | labor_crew_rate | no | install |
| P4 | labor_weekend_rate | parameter | 3 | labor_day_rate | no | – |
| P4 | labor_program_rate | parameter | 4 | labor_program_discount | no | window |
| P5 | glass_build_charge_tier | parameter | 3 | glass_build_charge | no | order |
| P5 | insulating_upgrade_tier | parameter | 3 | insulating_upgrade | yes (change orders × contract opening count) | window |
| P5 | glazing_upgrade_tier | parameter | 3 | glazing_upgrade | yes | window |
| P5 | replacement_volume_tier | parameter | 3 | volume_rate | no | – |
| P5 | owner_discount_tier | parameter | 3 | owner_discount | no | service |
| P5 | inspection_credit_window | method | 3 | visit_credit | no | – |

- Counts: P1 5 factors (4 parameter, 1 method), P2 6 (5/1), P3 4 (3/1), P4 6 (5/1), P5 6 (5/1). All within 4–6, ≥2 parameter, ≥1 method as labelled.
- Each `decides` is a non-`result` binding; binding sets within a policy are disjoint (P1 `lifetime_missed` appears in repeat_rate_ladder's bindings and feeds counting_window's `missed_counted` — listed only once per factor; disjoint as sets). Every tier is stated in the rule (condition + value/method) and implemented in its `decides` binding; no tier lives only in compute.
- Every fall-through is the policy baseline's value (P1 lifetime count / warranty fee / 1.0; P2 standard trip / 1.0 / 0; P3 plan fee / 1.0; P4 min-then-increment / plan minimum / 0 / 1.0; P5 published charge / 0 / 0 / 0 / 0).
- Label honesty:
  - **P1 counting_window is labelled `method` but its tiers substitute a window length into one counting algorithm** (F-G2): tier 1 = count of the registration's no-shows dated less than 12 whole months before the billing date (`within_months=K('member_window_months')`), tier 2 = the same count with 24 (`within_months=K('service_account_window_months')`), fall-through = the same count with no bound. This is a threshold substitution, the case the skill names as a mislabelled `method`. With it struck, P1 has 0 honest `method` factors (its other four are `parameter`).
  - P2 member_trip_rate (zero / lower-of two fees / standard), P3 remaining_term_share (zero / pro-rata by months / full), P4 labor_hours_method (increment-only / flat minimum / minimum-then-increment) change formula shape: accepted.
  - P5 inspection_credit_window selects which charge kinds enter the deduction (trip+labor / trip only / none) rather than a number; accepted as `method` with a note (F-O8).
- Distinct outcomes: all ladders give pairwise-distinct values/methods by construction, except that P1 fee_schedule's tier 1 ("that CareLine plan's own no-show fee") and tier 2 ("the On-Call Service Account's no-show fee") coincide at 79.00 for a CareLine Basic member (service.yaml: CareLine Basic no_show_fee 79.0, On-Call 79.0); the tiers are reference-valued and differ for every other plan (observation F-O9).
- Realism of conditions and outcomes (window/door warranty practice):
  - Real and weighed: trip-charge vs no-defect trip, crew size for bay/bow and large trim-wrapped or masonry openings, upper-story ladder/lift access, impact/specialty glass handling and build-class glass cost, weekend premiums, repeat no-show escalation, look-back windows for no-shows, prompt/late transfer handling, prorated transfer fee on remaining transferable term, unit-count labor minimums, lead-safe (EPA RRP) allowances in pre-1978 homes, diagnostic-visit credit toward an accepted repair, volume rate on multi-unit glass orders, member parts discounts.
  - Company-own schedules (worded as Ridgeline's own): carrying a signing-time military/first-responder/senior program rate onto warranty trip/labor/share charges; CareLine member pricing applied to warranty-visit trip and no-show fees; transfer fee scaled by opening count. Plausible as a company's own published schedule; no tier is one that "no such business would publish". Observation F-O10 on crew size: the crew rate is keyed on installation method for every component, including hardware and screen claims where a second technician is not ordinarily sent.
  - No tier condition holds of every customer reaching the write (each policy's scope is "a visit / a request / an acceptance", and every tier divides that population).

### findings

- **F-G1 SOURCE-POLICY RED (charter-global; rule ≠ compute on rounding).** Symptom: every extended rule says "rounded half up to the cent once, at the end" (P1, P2, P3, P4 result; P5 "the share is rounded half up to the cent once"), and every tool docstring says "rounded half up to 2 decimal places"; every `result` uses `RND(x, 2)` = Python `round(float(x), 2)` (check_compute.py line 388), which rounds exact binary ties to even. Evidence/demonstration: P1 for a CareLine Plus member (no_show_fee 59.0), second chargeable missed visit (1.25), Sunday (1.5), crew 1: 59 × 1.25 × 1.5 = 110.625 exactly; rule → 110.63, compute `round(110.625, 2)` → 110.62. P3 for a Ridgeline Lifetime Limited seller (fee 95), ≤5 openings (0.75), new CareLine member (0.5), share 1: 35.625 → rule 35.63, compute 35.62. Two answers in the same situation. Bears on both tasks; per-task files check whether their scored values sit on a tie.
- **F-G2 SOURCE-FACTOR RED (charter-global structure; P1 mislabelled method).** See factor_ladders. P1 `counting_window` tiers differ only in the window bound (12 / 24 / none) of one count; P1 therefore has no honest `method` factor. Bears on task 0 (whose tree contains P1).
- **F-G3 observation (latent, no task world affected — verified per task).** A P2 trip charge can legitimately compute to 0.00 (CareLine free trip, or a missed-visit credit ≥ the trip), P2 has no "a zero charge books nothing" sentence, P3's gate requires every billable visit to "carry its trip charge entry", and the trip tool's docstring describes `amount` as "a positive amount". In such a world one reading books a 0.00 entry and proceeds, the other books nothing and the transfer can never be placed. Not demonstrable on task 0/1 (see task files).
- F-O2 observation: P1 "dated less than the member counting window in whole months before the date the fee is billed" — the fee is dated with the missed-visit date, compute measures to NOW. Two readings differ only when a no-show sits between 12 months before the missed visit and 12 months before handling; checked per task.
- F-O3 observation: P2 sentence ("a visit that rebooks a chargeable missed visit on the same claim") carries no window bound; the condition adds "within the rebooking credit window". Broader sentence than condition; consequence only in a world where the rebooked chargeable no-show is >30 days earlier (credit zero either way, only the write order is affected). Not present in task 0.
- F-O4 observation: P3's state_gate `gate` field names a column, not an eligibility gate id; the gate lives only in the rule sentence and has no compute branch.
- F-O6 observation (checked per task): P4's rule books the charge "with its billable labor hours" while also defining "billed crew-hours … stated to one decimal place"; the tool argument is `billable_hours` ("the billable labor hours the charge is priced on"). Where lead-safe allowance or crew rate ≠ 1, "billable labor hours" (method output) and "billed crew-hours" differ.
- F-O7 observation: base `warranty_service_charges.formula.labor_charge` omits the increment rounding its rule states (base-internal; superseded for P4's scope).
- F-O8 observation: P5 inspection_credit_window accepted as `method` (selects which charge kinds enter the credit).
- F-O9 observation: P1 fee_schedule tiers 1 and 2 coincide at 79.00 for CareLine Basic.
- F-O10 observation: crew-rate factors (P1, P2, P4) key crew size on installation method for every component.
- F-O11 observation: the "late request" tier of P3 (more than 30 days after closing) is unreachable for Ridgeline Lifetime Limited (transfer window 30 days, base rejects later requests); reachable for the 60/90-day plans.
- F-O12 observation: P1/P2/P4/P5 select the priced object as the latest claim by `created_at` and the latest visit on it; the rules say "the claim the visit was booked for/served" without "latest". Object uniqueness is checked per task.

## closing_checklist

Written after both reveals (nothing above this heading was edited after a reveal).

- Per-task files: `0.md`, `1.md` correspond one-to-one with tasks/0.json, tasks/1.json; `_difficulty.md` alongside; first revision (no older revision to preserve).
- Comparison verdicts: task 0 — SOURCE-FACTOR RED (F-G2 demonstrated); task 1 — SOURCE-TASK RED (labor `billable_hours`, the F-O6 gap demonstrated on task 1's scored write). Not every comparison carries a PASS → **the difficulty does not pass the source-layer audit**.
- Scope: charter_scope task 0 = {P1, P2, P3} + their three tools, task 1 = {P4, P5} + their two tools; pairwise disjoint, jointly all five extended policies and all five task tools ✓ (matches the pre-reveal graph-component reading).
- Trees: task 0 n=2, 1 value_input edge, owner=user root; task 1 n=1, 1 value_input edge, owner=user root; whole-difficulty graph acyclic ✓.
- Factors: 4–6 per computation ✓; ≥2 parameter ✓; ≥1 honest method — fails for P1 (F-G2); multi-source per task ✓ (task 0 upper_story_access; task 1 lead_safe_hours, insulating/glazing upgrades); cross-difficulty with seeded rows per task ✓; every factor bears weight against an honest baseline and every all-baseline number differs from gold ✓ (95.00/0.00/95.00 vs 184.38/24.87/27.71; 297.50/530.00 vs 565.25/110.67).
- Charter-global RED outstanding: F-G1 (rounding sentence "half up" vs `RND` = Python `round`, ties to even; latent — no scored value in this difficulty sits on a tie where the two differ).
- Gate re-run on final form: not performed by this auditor (Step 0: gates are supplied, not run; the coordinator snapshot of 2026-10-13 ~12:45 UTC is the record). Required again after any rework.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit started 2026-10-13 ~15:10 UTC; same auditor; scratch /tmp/audit_d4_0060/ (round-2 copies of the frozen artifacts in /tmp/audit_d4_0060/r2/).
- Frozen inputs (sha256, verified equal to the coordinator brief): `242649fc3ac462e78dfb2b69aec5e229fe7da9541637867fa571b6f0aa904c6e warranty.extended.yaml`, `101f543633c332e83a2dee2bfb58d66e88b11f3522d026a387f6043bd2881fac task_tools.py`; views 0 `c5aeed1d…5f63`, 1 `85a57543…8018`. Both charter hashes changed from round 1 (afecc2ad…, 1aa601f7…), so every charter-global section is re-derived below, not carried forward.
- Gate snapshot supplied (2026-10-13 ~15:05 UTC): all green except TRACEABILITY (5 unlock tool-name misses, docs unrendered). Entry conditions complete.
- Nothing in this subsection is derived from a revealed round-2 GT; written before tasks/*.json was reopened.

### re-derivation summary (all sections)

- Base copy: still `==` the blueprint for every base key. Overwrites: same five declarations; superseded clauses verbatim in base, replaced_by verbatim in rules; compute_basis verbatim; baseline sentences in rules; prerequisite sources verbatim (mech.py rerun, no miss).
- action_binding_and_uuids: unchanged tool names/uuid8s; bodies still write unconditionally; no ordering words, no example values (grep). PASS.
- prerequisite_graph: unchanged edges P2→P1, P3→P2, P5→P4; acyclic.
- prerequisite_sentences: unchanged sentences; P2's `condition` now reads "…a no-show fee entry on the claim dated with the date of the chargeable missed visit on the same claim that the visit being billed rebooks" — same scope as its sentence (F-O3 closed).
- factor_ladders: P1 now `counting_window` (parameter, values are the three counted sets), `repeat_rate_ladder`, **`missed_visit_fee_basis` (method, 4 tiers: zero via a CareLine free no-show left in the plan year / lower of CareLine and warranty no-show fee / On-Call fee / warranty fee; decides `schedule_fee`; baseline `P('no_show_fee')`)**, `weekend_day_rate`, `crew_rate_ladder` → 5 factors, 4 parameter, 1 method. The new method changes formula shape (constant zero / `MN` of two fees / one fee) — honest. Every tier is in the rule and in `schedule_fee`; fall-through = baseline ("the warranty plan's no-show fee"). P2–P5 factor structure unchanged from round 1. Multi-source (check_compute.multi_source): P2 upper_story_access, P4 lead_safe_hours, P5 insulating/glazing upgrades (unchanged).
- rule_compute_equivalence: every `result` is now `int(x * 100 + 0.5 + 0.000001) / 100` and every rounding sentence adds "an amount exactly halfway between two cents going to the higher cent". All five results are non-negative by construction (MX(0,…) or products of non-negative terms), so `int` truncation is a floor and the expression is half-up; the 1e-6-cent epsilon only absorbs float error (all inputs are cents × rates of at most two decimals or /24, whose cent fractions are never within 1e-6 of ½ unless exactly ½). Round-1 demonstrations now agree: 110.625 → 110.63, 35.625 → 35.63 (python check). P4 `billable_labor_hours = RND((method_hours + allowance) × crew, 1)` — values are multiples of 0.5, never a tie at one decimal.
- P4 hours term: rule now says "the method hours … are raised by the lead-safe allowance and the sum is multiplied by the labor crew rate, giving the billable labor hours, which are booked on the labor charge to one decimal place"; tool doc "the billable labor hours of the visit as the warranty labor terms define them, the hours the labor amount is priced on". The baseline sentence "The billable labor hours of a visit are its method hours, booked on the labor charge to one decimal place" remains; read with "the labor crew rate and the labor day rate are one, unless a paragraph below sets them" it is the default case (allowance 0, crew 1 ⇒ (method + 0) × 1 = method), the same baseline-then-factors pattern the charter uses for every amount (e.g. "the labor charge is the billable labor hours times the warranty plan's hourly labor rate" before the discount and day rate). Observation R2-O1: the baseline sentence states an identity the factor paragraphs then change; no reading other than the factor-applied one survives the "unless a paragraph below sets them" sentence.
- F-G3: P2 now says "A trip charge that works out to zero is still booked, as a zero entry, so that the visit carries its trip charge entry"; tool amount "a non-negative amount (zero when the trip owed works out to nothing)". Closed.

### findings (revision 2)

- F-G1 (round-1 SOURCE-POLICY RED, rounding): **closed** — compute now half-up, matching every rule and docstring.
- F-G2 (round-1 SOURCE-FACTOR RED, P1 mislabelled method): **closed** — relabelled parameter; new honest method factor.
- F-G3, F-O3, F-O6: closed (above).
- **New latent observation R2-O2** (introduced with the new P1 tier): P1 now says "A missed visit whose fee works out to zero books nothing", and its first fee-basis tier makes a missed visit that is chargeable by place (counted > free count) cost zero when a CareLine free no-show is left; P2's prerequisite waits until "the records carry the no-show fee entry for that missed visit" of "a chargeable missed visit". In such a world one reading waits forever (no entry will be booked), the other treats a zero-fee missed visit as not chargeable. The same shape F-G3 had, now on the P1→P2 edge. Not present in either task world (checked per task); recorded as a latent observation, consistent with the round-1 treatment of F-G3.
- R2-O3 observation: the free no-show tier counts "missed plan visits logged in that plan year" from `service_calls`; a warranty no-show that "uses one of those free no-shows" is never logged there, so the allowance is not consumed by warranty no-shows. Latent (no task world reaches tier 1).
- Observations carried, unchanged artifacts' text: F-O4, F-O7, F-O8, F-O9 (now moot: fee_schedule replaced; the new tiers are method-distinct), F-O10, F-O11, F-O12.

### closing_checklist (revision 2)

Written after the revision-2 reveals; nothing above this heading in revision_2 was edited after a reveal.
- Per-task files carry revision_2 sections; round-1 text untouched. Both revision-2 comparisons PASS.
- Scope: charter_scope task 0 {P1, P2, P3} + three tools, task 1 {P4, P5} + two tools — disjoint, jointly complete ✓.
- Trees: task 0 n=2 with 1 value_input edge, task 1 n=1 with 1 value_input edge; owner=user root in both; acyclic ✓.
- Factors: every computation 4–6 factors, ≥2 parameter, 1 honest method (P1 now missed_visit_fee_basis); multi-source per task ✓; cross-difficulty with seeded rows ✓; every factor bears weight and every all-baseline figure differs from gold ✓.
- Round-1 REDs: F-G1 closed, F-G2 closed, task-1 SOURCE-TASK RED closed. No new RED. New latent observations R2-O1 (P4 baseline sentence identity), R2-O2 (zero-fee chargeable missed visit vs P2's wait), R2-O3 (free no-show allowance not consumed by warranty no-shows) — none reached by either task world.
- Gates: coordinator snapshot 2026-10-13 ~15:05 UTC (all green except TRACEABILITY, unrendered docs only) is the record for the final form; not re-run by the auditor.
- **The difficulty passes the source-layer audit at revision 2.**

## revision_3

### charter_global_frozen (revision 3)

- Re-audit 2026-10-13 (after the round-3 rework); same auditor; scratch /tmp/audit_d4_0060/r3/ (copies of the frozen artifacts; `diff` against /tmp/audit_d4_0060/r2/).
- Frozen inputs (sha256, equal to the brief): `7012ab12734d04ed078abc10f6740fe83a83caf32a6a176fecc8206a41432ae9 warranty.extended.yaml`, `4ee23430a67f8d7d513cec6bd30d2cf85bfcd2ee3c9bda21a8e90abe73c572bd task_tools.py`; views 0 `c5aeed1d…5f63`, 1 `85a57543…8018` — **identical to round 2** (worlds and personas unchanged).
- Both charter hashes moved, so the charter-global sections are re-derived from the round-2 → round-3 diff plus a full mechanical rerun (mech.py: base copy `==` blueprint; overwrites, compute_basis, baseline sentences and prerequisite sources all verbatim; no miss).
- Also read on the coordinator's instruction: `audits/render_source/warranty_claims_and_transfers/warranty_round1.md` (renderer source findings F1–F5; contains no GT value). Disclosed here as an input; it does not touch any task's blind derivation.
- Gate snapshot supplied: all eight gates OK (TRACEABILITY now OK). Entry conditions complete.
- Written before tasks/*.json (round 3) was reopened.

### diff review (round 2 → round 3)

1. task_tools.py: only `bill_missed_visit_fee_18fefa1f.amount` doc changed to "a non-negative amount (zero when the missed visit owes a fee entry of nothing)". No example value, no ordering word, body unchanged (it already accepted any amount). PASS.
2. P1 (missed-visit fee): "A missed visit is chargeable only when the missed visits counted are more than the plan's free no-show count; a missed visit that is not chargeable carries no fee and nothing is booked" and "A chargeable missed visit whose fee works out to zero is still booked, as a zero no-show fee entry, so that the missed visit carries its fee entry". P2's prerequisite ("…only after the records carry the no-show fee entry for that missed visit" of "a chargeable missed visit") can now always be met. **R2-O2 closed.**
3. P1 free no-show tier now reads "the missed plan visits logged in that plan year, together with the owner's missed visits on the registration that already drew a free no-show as shown by their zero no-show fee entries, are fewer than the plan's free no-show count"; new binding `drawn_free_missed = COUNT(no_show_fee entries with amount 0.0)` over the registration, added to the factor's bindings; compute_basis verbatim. The allowance is now consumed by warranty no-shows. **R2-O3 closed**, with observation R3-O2 below.
4. "A CareLine plan in this policy is any plan of the CareLine Service Plans other than the On-Call Service Account." added to P1, P2, P3, P5 (the four rules that name a CareLine plan; P4 names none). Matches every `plan_name != 'On-Call Service Account'` test. **Renderer F3 closed.**
5. P5 proration step wording: "once five full years have been reached … once ten full years have been reached". Matches `full_years >= 5/10`. **Renderer F2 closed.**
6. P4: "The billable labor hours of a visit start from its method hours and are booked on the labor charge to one decimal place" (baseline sentence). The identity is gone. **R2-O1 closed.**
7. P5 full-year count and P3 month count now carry their own 29-February convention — judged in R3-G1 below.
8. Renderer F1 (base formula omits increment rounding) = my F-O7, base-only, unchanged; F5 (no-defect trip scope kept by P2's opening sentence) agrees with my round-1 override_declarations finding.

### findings (revision 3)

- **R3-G1 SOURCE-POLICY RED (charter-global; undeclared override of the base anniversary convention, P5 and P3).**
  - Symptom: P5 now says "counting a year only once the date in that year with the coverage start date's month and day has been reached, a start on 29 February reaching it on 1 March in a year without that day … this count of full years serves the share only, and every coverage term stays counted as the warranty terms set it". P3 now says "a month being complete once the day of the month of the original coverage start date is reached and, in a month that lacks that day, only on the first day of the next month; this count serves the fee only, and every coverage term stays counted as the warranty terms set it".
  - Base text: `warranty_registration_and_terms` — "Every term is counted from the coverage start date in whole years: coverage runs through the day before the anniversary that ends the term, and when that anniversary falls on a day the month lacks, it falls back to the last day of the month." The base measure `warranty_msr_full_years` ("Whole years elapsed, counting a year only once its anniversary date has been reached") is what the base claim decision (`warranty_claim_decision`, not overwritten) uses to make a claim `approved_with_proration`, and what the base share sentence P5 overwrote cited.
  - Neither P5's nor P3's `overwrite` names either base sentence; P5's replaced_by keeps "the full years since the coverage start date" with no convention; P3's single overwrite is the fee-date sentence. The "serves the share/fee only" clause is a scope assertion, not a declaration.
  - Demonstration (check_compute.MONTHS, which both computes use):
    - P5: Ridgeline Limited Warranty, coverage start 2020-02-29, seal claim filed 2025-02-28. Base: the 2025 anniversary falls back to 2025-02-28 → 5 full years reached → the base decision is `approved_with_proration` (share ½). P5: the year is reached only on 2025-03-01 → 4 full years → proration share 0 → "A share of zero books nothing". The same claim is approved with proration by the base and owes no share under P5 (`MONTHS("2020-02-29","2025-02-28")//12` = 4).
    - P3: Lifetime Limited (transferred product term 10 years), coverage start 2016-02-29, confirmation 2026-02-28. Base: the term ending anniversary falls back to 2026-02-28, so transferable product coverage ran through 2026-02-27 and nothing remains → the share rule's own "When none remain … the remaining-term share is zero" gives a 0.00 fee. P3: 119 whole months elapsed (`MONTHS("2016-02-29","2026-02-28")` = 119) → 1 month remains → share 1/24 → a non-zero fee.
  - Consequence: two defensible answers in the same situation. Neither task world has a 29-February coverage start (2017-11-18, 2018-06-20), so neither task's scored value moves; the defect is charter-global and latent per task.
  - Relation to previous revisions: the compute has used `MONTHS` since round 1, while the rounds 1–2 rule said "counting a year only once its anniversary has been reached", which by default took the base fallback. That was a latent rule/compute split which I did not flag in rounds 1–2 (the renderer raised it as F4). The round-3 wording makes the departure from base explicit without declaring it.
- **R3-O1 observation:** zero-amount charge entries (P1's zero no-show fee, P2's zero trip charge since round 2) depart from the base event field `warranty_charge_assessed.amount: "Charge amount (positive)."` It is a schema description, not a policy sentence. Both rules state the zero entry outright and the tools accept it, and no task world books one. I missed this in round 2 and record it now.
- **R3-O2 observation (company rule, as the reworker flagged):** `drawn_free_missed` counts zero no-show fee entries over the whole registration, while the tier speaks of "free no-shows left in the plan year of the missed visit". The service charter defines the allowance per plan year ("No-show visits per plan year without a fee"). The rule's "together with … missed visits on the registration that already drew a free no-show" carries no plan-year bound, so the compute follows the literal clause. A reader who bounds it to the plan year differs only when an earlier plan year holds a drawn free no-show. A zero entry from a CareLine Estate member (no-show fee 0.00) would also be counted as "drawn". Latent: no task world has a zero no-show entry.
- Closed this round: R2-O1, R2-O2, R2-O3 (with R3-O2), renderer F2, F3. Carried observations: F-O4, F-O7 (= renderer F1), F-O8, F-O10, F-O11, F-O12, T1-O2.

### closing_checklist (revision 3)

Written after the revision-3 reveals; nothing above this heading in revision_3 was edited after a reveal.
- Both revision-3 comparisons match GT figure for figure. Trees, factor weights, scopes (task 0 {P1, P2, P3}, task 1 {P4, P5}), the value_input floors, the owner=user roots and acyclicity all hold, as in revision 2.
- Items from revision 2 and the renderer:
  - Closed: R2-O1, R2-O2, R2-O3, renderer F2, renderer F3.
  - Unchanged: renderer F1 (base-only); F5 verified.
  - F4 is now R3-G1.
- Open RED: **R3-G1 SOURCE-POLICY RED (charter-global).** P5's full-year count and P3's month count adopt a "1 March / first of next month" rule for 29-February starts. Neither policy's `overwrite` declares a departure from the base's "falls back to the last day of the month" anniversary rule (`warranty_registration_and_terms`, `warranty_msr_full_years`). The departure gives different answers for a 29-February coverage start (P5: share ½ vs 0; P3: fee 0 vs 1/24 share). Neither task world reaches it.
- New observations: R3-O1 (zero charge entries vs the base field text "Charge amount (positive)") and R3-O2 (drawn free no-shows counted over the whole registration vs a per-plan-year allowance). Both are latent.
- Gates: the coordinator's post-round-3 snapshot (all eight OK) is the record; the auditor did not re-run them.
- **The difficulty does not pass the source-layer audit at revision 3; the only blocker is the charter-global R3-G1.**

## revision_4

### charter_global_frozen (revision 4)

- Re-audit 2026-10-13 (after the round-4 rework); same auditor; scratch /tmp/audit_d4_0060/r4/ (artifact copies; diffs against r3/).
- Frozen inputs (sha256, equal to the brief): `c1d4cdf1e6e34ce45d07b090f385e68080293916d158d11f8ecfec73e6ae399c warranty.extended.yaml`, `afbde65ba37788195ecf896572da248eb1495f9f32f6257be77cc870e231b08f task_tools.py`; views 0 `c5aeed1d…5f63`, 1 `85a57543…8018` — identical to rounds 2–3.
- Gate snapshot supplied: all eight OK. Written before tasks/*.json (round 4) was reopened. No input beyond the charter, tools, views, blueprint and the DSL evaluator was read.

### diff review (round 3 → round 4) and re-derivation

1. **R3-G1 (undeclared departure from the base anniversary fallback).**
   - P5 rule now reads "counting a year only once its anniversary has been reached, an anniversary that falls on a day the month lacks falling back to the last day of that month". This is the base convention of `warranty_registration_and_terms` and `warranty_msr_full_years`.
   - P3 now reads "a month being complete once the day of the month of the original coverage start date is reached and, in a month that lacks that day, on the last day of that month". This is the same fallback applied monthly, so P3's month count ends on the base term-end anniversary.
   - Both "serves the … only" clauses are gone.
   - Compute: civil-date decomposition from `DAYS('1600-03-01', date)` with integer arithmetic (the standard days→civil algorithm; checked term by term), then `MONTHS(start, end) + 1` when the end day is the last day of a month that lacks the start day.
   - Independent check (/tmp/audit_d4_0060/r4/datecheck.py): both bindings were compared against my own base-anniversary reference (add k months, clamp to the month's last day). On 20,007 date pairs (20,000 random spanning 1990–2064 plus the round-3 demonstration pairs and month-end edges) there were **0 mismatches**. Round-3 demonstrations now agree with base: 2020-02-29 → 2025-02-28 gives 5 full years (share ½, consistent with the base `approved_with_proration`); 2016-02-29 → 2026-02-28 gives 120 months elapsed, 0 remaining, share 0.
   - No departure from base remains, so no overwrite is needed. **R3-G1 closed.**
2. **R3-O1 (zero charge rows vs base "Charge amount (positive)").**
   - P1 now says "A chargeable missed visit whose fee works out to zero books nothing and owes no fee entry". P2 now says "A trip charge that works out to zero books nothing and owes no trip charge entry". The no-show and trip tool docstrings say "a positive amount" again.
   - The P2 and P3 prerequisite sentences now carry "…the no-show fee entry owed for that missed visit, a missed visit whose fee works out to zero owing none" and "…carries its trip charge entry …, a visit whose trip charge works out to zero owing none". Their `condition`s add the matching "unless … works out to zero". Sentence and condition have the same scope.
   - Both waits are now always satisfiable: an entry is booked whenever one is owed, and none is owed when the amount is zero.
   - Four-point test still holds: ordering connective "only after" / "until", record-visible state, no tool or id named. The unique writers are unchanged.
   - **Closed for P1/P2.** Residue in R4-O3.
3. **R3-O2 (free no-show draw).**
   - Removed. `missed_visit_fee_basis` now has three tiers: a CareLine plan past its waiting period on the missed-visit date takes the lower of the CareLine and warranty no-show fees; an On-Call Service Account takes its own fee; everyone else takes the warranty fee.
   - Compute is `MN(CareLine fee, warranty fee) / On-Call fee / P('no_show_fee')`, with compute_basis verbatim. Cross-category reads are trimmed to match. The "plan year" sentence left with the tier.
   - **Closed.** See R4-O2 for the method label.
4. task_tools.py: only the two amount docstrings changed ("positive amount"); bodies, names and uuid8s unchanged. No example value and no ordering word. PASS.
5. Mechanical rerun (mech.py):
   - The base copy is identical to the blueprint.
   - Overwrites, compute_basis quotes, baseline sentences and prerequisite sources are all verbatim.
   - No factor id appears in a tool name.
   - The prerequisite graph is unchanged and acyclic.
   - Exception: 13 calendar-helper bindings in P3 and 13 in P5 carry no `compute_basis` entry (R4-O1).

### findings (revision 4)

- R3-G1 — **closed** (see 1).
- R3-O1 — closed for no-show and trip entries (see 2).
- R3-O2 — closed (see 3).
- **R4-O1 observation:** these P3 and P5 bindings have no `compute_basis` quote: `start_day_of_era`, `start_year_of_era`, `start_day_of_year`, `start_month_index`, `start_day`, the `confirm_*`/`filing_*` equivalents, `*_month_days` and `*_year`. They are pure calendar arithmetic implementing the quoted fallback sentence (whose quote sits on `start_ordinal`, `confirm_ordinal`/`filing_ordinal`, `months_elapsed` and `full_years`). They invent no business basis, and the rule makes no promise they leave unkept (verified by the 20,007-pair check). The gate snapshot (EXTENDED OK) accepted them.
- **R4-O2 observation:** `missed_visit_fee_basis` keeps its `method` label on the strength of its "lower of the CareLine plan's own no-show fee and the warranty plan's no-show fee" tier, which compares two fees. The On-Call and fall-through tiers are single fee lookups. This is the same shape as P2's `member_trip_rate` (accepted since round 1: zero / lower-of / standard), so I accept it as honest. The label's method content now rests on one tier.
- **R4-O3 observation (residue of R3-O1; the reworker's "no zero-amount charge row is ever booked" does not hold everywhere):**
  - P3's rule still says the confirmation "books the fee as a transfer fee on the warranty charges", and the confirm tool always creates the fee row (docstring "a non-negative amount").
  - A seller with a CareLine plan enrolled at least 12 whole months before confirmation (member rate 0), or one with no transferable months left (share 0), gets a 0.00 `transfer_fee` row. That still departs from the base field text "Charge amount (positive)".
  - Latent: task 0's fee is 27.71.
- Carried observations: F-O4, F-O7 (= renderer F1), F-O8, F-O10, F-O11, F-O12, T1-O2.

### closing_checklist (revision 4)

Written after the revision-4 reveals; nothing above this heading in revision_4 was edited after a reveal.
- Both revision-4 comparisons match GT figure for figure, and both carry PASS.
- Scopes are disjoint and complete: task 0 is {P1, P2, P3}, task 1 is {P4, P5}.
- Trees: task 0 has n=2 with one value_input edge; task 1 has n=1 with one value_input edge. Both roots are owner=user. The graph is acyclic.
- Factors:
  - Every computation has 4–6 factors, at least 2 parameter and 1 method (P1's method is `missed_visit_fee_basis`, R4-O2).
  - Each task has a multi-source factor and a cross-difficulty factor whose rows are seeded.
  - Every factor bears weight, and every all-baseline figure differs from gold.
- REDs: none open. R3-G1 closed; earlier REDs F-G1, F-G2 and the task-1 SOURCE-TASK RED were closed in revision 2 and have not regressed.
- Open observations (none reached by either task world): R4-O1, R4-O2, R4-O3, plus the carried F-O4, F-O7, F-O8, F-O10, F-O11, F-O12 and T1-O2.
- Gates: the coordinator's post-round-4 snapshot (all eight OK) is the record. The auditor did not re-run them.
- **The difficulty passes the source-layer audit at revision 4.**
