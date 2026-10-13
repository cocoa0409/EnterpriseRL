# Policy-task audit — driver_account_holds_and_deactivations / charter-global

## charter_global_frozen

- Frozen inputs (sha256 re-computed by the auditor, identical to the coordinator's HASHES.txt):
  - `tasks/driver_account_holds_and_deactivations/driver.extended.yaml` 45c6bef61973a45f40243b84f6876b7a663648019558bb87d37520ebd319d55a
  - `tasks/driver_account_holds_and_deactivations/task_tools.py` b6ac364f35d6adb4ec4323fc543dcd80dc508037fdf5a6a01a58c9c6d9d0853d
- Freeze time: 2026-10-11 ~11:50Z, before the GT reveal at 11:55:32Z. Auditor: erl-task-policy-audit subagent (independent of the instantiator).
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/products/driver.yaml`, `blueprint/products/earnings.yaml` (Pro tier rule only), `blueprint/db_schema.json` (via the gate's evaluator), `blueprint/share_tools.py`, the extended charter, `task_tools.py`, the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/COUNT/LATEST/CFIELD).
- Masked and not read: every `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure); no other scenario or difficulty was opened. Nothing in this section is derived from a revealed GT.
- Gate snapshot supplied by the coordinator (all rc=0; traceability deferred to render). Accepted as the entry condition, not as proof.

Short names used below:

| Id | Policy | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| A | driver_ext_document_lapse_allowance | deactivate_for_document_lapse_e185dacd (agent) | allowance_days | [] |
| B | driver_ext_insurance_binder_acceptance | record_insurance_binder_0f7a5736 (agent) | accepted_days | A (value_input, state) |
| C | driver_ext_temporary_license_acceptance | upload_temporary_license_ef094b46 (user) | accepted_days | B, A (value_input, state) |
| D | driver_ext_cancellation_warning_sequence | record_cancellation_warning_d72ae138 (agent) | notice_sequence | [] |
| E | driver_ext_registration_hold_start | place_registration_hold_154e4b50 (agent) | grace_days | D (value_input, state) |
| F | driver_ext_inspection_validity | record_inspection_validity_ad704ee2 (agent) | validity_days | [] |
| G | driver_ext_temporary_permit_acceptance | upload_temporary_permit_14d2792d (user) | accepted_days | F, E (value_input, state) |

### policy_conflict_scan

- Base copy: lines 1-971 of the extended file are byte-identical to `blueprint/products/driver.yaml` (diff shows only the trailing blank line). PASS.
- Overlapping subjects. Four policies (B, C, F, G) each override the same base sentence of driver_document_compliance ("An uploaded document updates the expiry date on the agreement only when it is of a required type and its expiry date is later than the one on file."). Each does so for a different document type: B insurance binder, C temporary license, F inspection, G temporary permit. None of them writes another one's field. The tools confirm this: B writes only `insurance_expiry_date`, C writes `license_expiry_date` plus one drivers_license upload, F writes only `inspection_expiry_date`, and G writes `commercial_permit_expiry_date` plus one commercial_permit upload. No two policies fight over one quantity.
- Status writers: A (on_hold→deactivated, document_lapse) and E (active→on_hold, document_expired). They act on disjoint source states. A acts on a hold that has outlived its allowance. E acts on an active agreement whose registration grace has run out.
- Interaction A/E (observation O-4). A's "lapsed document" reads only the agreement's expiry fields ("the required document with the earliest expiry date on the agreement"). The vehicle registration is a required document but is not a field of `driver_agreements`; it lives only on uploads. A registration hold placed under E that later outlives its allowance would therefore have its notice tier read off a non-lapsed document. No task in this difficulty reaches that point: E places its hold today. So this is not demonstrable and is recorded as an observation.
- Time anchors. Every extended computation evaluates at the handling day: "the day the allowance is worked out", "the recording day", "the upload day" or "the day the grace is worked out". Each is the clock of its own write. No policy anchors on a future date or waits for one.
- Cross-category reads. A, B, C, D and E read `earnings_accounts.variant_name` (Wayfare Pro status), which is a read only. F and G read nothing outside driver.
- Scopes. The prerequisite graph has exactly two weakly connected components: {A, B, C} with root C, and {D, E, F, G} with root G. With M=2, the two trees jointly cover all seven extended policies and are pairwise disjoint if each task claims one component. Each task file derives its own tree. The comparison with `charter_scope` happens only after the reveal, in the task files.

### rule_compute_equivalence

Every binding was checked against its `compute_basis` quotation and back against the rule, sentence by sentence. Results per policy:

- A: PASS.
  - standard_length is P(document_hold_max_days).
  - days_active is DAYS(activated_date, NOW), matching "counted from its activation date to the day the allowance is worked out".
  - The tenure, Pro and rating ladders are exact.
  - lapse_kind is computed as `insurance_days_past>=0` (meaning "on or before"), else license, else 0. This is exact.
  - The warnings count is COUNT(within_months=6) over every quality warning of any basis. That matches "quality warnings dated fewer than warn_window_months whole calendar months". The DSL `_within` is 0 <= MONTHS < 6.
  - lapsed_expiry is the min of license, insurance and inspection, with the permit counted only on the Black levels. This is exact.
  - The notices count filters on document_expiry_date = lapsed_expiry, matching "whose covered expiry date is the lapsed document's expiry date".
  - Rounding is (x*pct+99)//100, which is ceiling on integers ("rounded up").
  - "Five adjustments" counts as 5. Nothing is invented in compute and no promise in the rule is left empty.
- B: PASS.
  - The binder is LATEST auto_insurance upload, by date and expiry.
  - The cap is MN(standing, DAYS(NOW, printed_end)), "applied last".
  - lapse is `>60` / `>=1` / else, matching "more than" / "at least one but no more than" / "recording day or later".
  - The late count covers second notices for auto_insurance within 24 months.
  - pro_tenure is a conjunction of Pro status and days_active>=1095.
  - The uploads count is within 36 months, binder included.
  - The term is DAYS(upload, printed_end).
  - The standing rule uses floor 80% when deactivated with date ≤ NOW, ceiling 90% when on hold with start ≤ NOW, and is unchanged otherwise. Observation O-7 notes that compute's `else` also covers states the rule does not name, such as on_hold with a future start date.
- C: PASS.
  - The old-license ladder works on DAYS(NOW, license_expiry_date): ≥15, ≥1, else.
  - The background-check ladder works on DAYS(background_check_date, NOW): <180, <365, else.
  - short_documents counts insurance and inspection, plus the permit on the Black levels only, each with a `< 30` test that includes dates already past.
  - The late count covers second notices for any document within 24 months: ≥3, ≥1, else.
  - In the Pro ladder Gold sits in the mid tier with Silver. This differs from A and B, but C's rule states it.
  - The standing rule is 50% floor or 75% ceiling.
- D: PASS with observation O-8.
  - The cycle_window ladder sets 24 months for Black and Black SUV, 18 for Comfort and XL, and 12 otherwise.
  - The earlier-warnings count covers cancellation-basis warnings within the cycle window.
  - The tenure method is 50% floor or 75% ceiling.
  - Forgiveness and severity are taken on RND(latest_rate − threshold, 1).
  - sequence = 1 + severity + MX(0, counted − forgiven), matching "never below zero".
  - O-8: the `compute_basis` of `earlier_warnings` and of `result` quote the baseline sentence ("…window_other_months…") even though the expressions use `cycle_window` and the factor-adjusted number. The cycle-window rule sentence covers the expression, so no basis is invented.
- E: PASS.
  - The tenure ladder is 6/3/0.
  - The late count covers second notices for vehicle_registration within 36 months: ≥3 gives −3, 1-2 gives −1.
  - The Pro-and-rating ladder is a conjunction.
  - The uploads count is within 36 months: ≥3 gives 3, exactly 2 gives 2, otherwise 0.
  - The standing-on-record rule checks for any quality warning within 3 months (50% floor), then an unsafe_driving report within 6 months (75% ceiling), then unchanged.
  - "Four adjustments" counts as 4. The binding `registration_expiry` feeds only the tool argument.
- F: PASS.
  - The inspection date is LATEST vehicle_inspection upload event_date.
  - The standard is 12×30, or 6×30 on the Black levels.
  - current_year is derived from NOW, and vehicle age is current_year − model_year.
  - The late count covers second notices for vehicle_inspection within 24 months.
  - yearly_trips = lifetime_trips×365/days_active. The MX(1, …) guard is harmless.
  - The registration ladder uses the LATEST registration upload: <0, <30, else.
  - The clock-start ladder works on days_ahead = DAYS(inspection_date, expiry on file): ≥7 adds days_ahead, <0 subtracts min(−days_ahead, 30), and 0-6 leaves the value unchanged.
- G: PASS.
  - The old-permit ladder works on the agreement's permit date.
  - The rating ladder is ≥4.9 gives 6, ≥4.85 gives 3.
  - Short documents are insurance and inspection on the agreement plus the registration from its latest upload.
  - The check ladder is the same as C's.
  - Permit uploads are counted within 36 months.
  - The standing rule is 40% floor or 60% ceiling.

Every `factors[].ladder` tier is a sentence of its rule and a branch of its `decides` binding, and the reverse also holds. No tier lives in only one face.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (see the table above). No two policies share a target tool.
- uuid8s: e185dacd, 0f7a5736, ef094b46, d72ae138, 154e4b50, ad704ee2, 14d2792d. All seven are distinct, share no common prefix or suffix, are not sequential, and none is a re-tailed copy of another. PASS.
- Tool bodies validate nothing. Each performs exactly one unconditional `ctx.update`/`ctx.create`, and each body was read. None checks status, dates or prerequisites. The module docstring states "None of them checks a business condition". PASS for "tool layer judges no prerequisite".
- Docstrings (observation O-6). They describe their own effect only and never name another write or a position among writes. They do contain "Afterwards …", which describes the post-call state of the same call, and they cite "the driver agreement lookup" / "the standing record lookup" as the source of an argument value. Neither states a sequence among problems, so no consequence is demonstrable.

### prerequisite_graph

- Every policy has `prerequisite` filled in. A, D and F are `[]`.
- Edges: B→A, C→B, C→A, E→D, G→F, G→E. Every `problem` is an extended policy id in this file. None is a base policy and none points at itself.
- The graph is acyclic, with topological orders A, B, C and D, E, F, G (F is independent of D and E).
- All edges are `form: state` and none carries `fallback_reason`, which is consistent.
- Every `policy_source` was located verbatim in its own policy's `rule`:
  - B: "The binder acceptance days are fixed only after the agreement's status and deactivation date already show any deactivation for document lapse that its document hold has run into."
  - C: "The temporary license acceptance days are not worked out until the auto insurance expiry date on the agreement carries the accepted period of every insurance binder uploaded to the standing record."
  - C: "Before the temporary license acceptance days are worked out, the agreement's status must already show the deactivation for document lapse owed by any document hold that has run past its lapse allowance."
  - E: "The registration grace days are fixed only after the standing record carries the quality warning owed for every rating review that found the cancellation rate above the level's threshold."
  - G: "The temporary permit acceptance days are not worked out until the vehicle inspection expiry date on the agreement carries the validity of the latest inspection uploaded to the standing record."
  - G: "Before the temporary permit acceptance days are worked out, the agreement must already carry the document hold owed for a vehicle registration whose grace days have run out."
- `kind`/`gate`: every edge is `value_input`, and every `gate` names a real binding of the blocked policy's compute: standing_binder_days (B), short_doc_adj and standing_license_days (C), registration_grace (E), short_doc_adj and standing_permit_days (G).
- `resolved_by` is in every case the depended-on policy's `target_tool`, and its tool body really changes the value named in `effect`:
  - A changes status, which moves the standing tier.
  - B changes insurance_expiry_date, which feeds short_doc.
  - D creates a quality-warning row, which moves the standing-on-record tier.
  - F changes inspection_expiry_date, which feeds short_doc.
  - E changes status and hold_started_date, which moves the standing tier.
- `condition` restates each sentence at the same strength. Phrases such as "whenever …" and "for every binder upload" are general text with no authoring viewpoint.
- PASS.

### prerequisite_sentences

Each sentence was checked on four points: connective, form, no tool or id names, and strength. Each was then checked for a unique resolving write, and the derivation is written out.

1. B ← A, "fixed only after the agreement's status and deactivation date already show any deactivation for document lapse that its document hold has run into".
   - The connective is "only after", and the sentence is in state form: status and deactivation date are agreement fields shown by the agreement lookup.
   - It names no tool, id or snake_case token, and "any … has run into" matches the condition's "whenever".
   - Unique writer: the only write in this difficulty that sets a deactivation is `deactivate_for_document_lapse_e185dacd` (A).
   - Derivation: the records show a document hold that has outlived the allowance; A's rule says such a hold "ends in deactivation for document lapse"; A's write brings that about.
   - PASS.
2. C ← B, "not worked out until the auto insurance expiry date on the agreement carries the accepted period of every insurance binder uploaded to the standing record".
   - The connective is "not … until", the sentence is in state form, and it names no tool.
   - Unique writer: only `record_insurance_binder_0f7a5736` sets `insurance_expiry_date`.
   - Derivation: an auto-insurance upload whose period the agreement does not carry is a binder not yet recorded; B's rule ("A binder updates the agreement only when support records it") names the write.
   - PASS.
3. C ← A, "Before … worked out, the agreement's status must already show the deactivation for document lapse owed by any document hold that has run past its lapse allowance".
   - Connective "Before … must already", state form, unique writer A.
   - PASS.
4. E ← D, "fixed only after the standing record carries the quality warning owed for every rating review that found the cancellation rate above the level's threshold".
   - Connective "only after", state form on standing-record rows.
   - Unique writer: only `record_cancellation_warning_d72ae138` creates a `driver_quality_warning`.
   - What makes a warning "owed" comes from the base cancellation standard ("A rate above the level's cancellation_rate_threshold_pct brings a cancellation warning"). D's rule gives its number.
   - PASS. Observation O-9 notes that D's rule says "The warning records the cancellation rate shown at the latest rating review", while the edge speaks of a warning owed for *every* above-threshold review. If the owed review were not the latest one, the two sentences would point at different rates. Whether this bites is demonstrated per task.
5. G ← F, "not worked out until the vehicle inspection expiry date on the agreement carries the validity of the latest inspection uploaded to the standing record".
   - State form. Unique writer: only `record_inspection_validity_ad704ee2` sets `inspection_expiry_date`.
   - PASS.
6. G ← E, "Before … worked out, the agreement must already carry the document hold owed for a vehicle registration whose grace days have run out".
   - State form (status and hold reason).
   - Unique writer: `place_registration_hold_154e4b50` is the only active→on_hold write. A moves on_hold→deactivated.
   - PASS.

No rule restates another policy's prerequisite sentence. No rule names a tool or another policy id. No extended rule states a cross-problem order beyond these six sentences. No base rule sentence grounds an edge.

### override_declarations

Each `base_policy_refs` entry was checked sentence by sentence:

- A (refs: rating, cancellation, document_compliance, recheck, safety, voluntary_close). driver_document_compliance's "A document hold still in place document_hold_max_days after hold_started_date ends in deactivation for document_lapse" is replaced by the allowance, and this is declared. The other document_compliance sentences (hold on the day after expiry, release only when every document is unexpired, document_lapse_reactivation, the upload rule) are followed. The sentences of the other five refs govern quantities A does not touch: warnings, cancellation holds, rechecks, safety holds, voluntary close and the fraud payout hold. A follows them.
- B. "An uploaded document updates the expiry date …" is replaced, declared. The base event `driver_document_submit` triggers `driver_document_update`, which is the base's automatic update. The declared replacement ("only when support records it … whatever end date is printed") supersedes it for the binder. B defines "the binder" as "the latest auto insurance upload on the standing record". Observation O-7b: the record carries no binder marker, so under the merged reading every latest insurance upload is handled by B.
- C, F and G. The same upload sentence is replaced for their own document type, and each is declared.
  - Observation O-5 on F: the base `parameter_schema` gloss "inspection_interval_months: Months a vehicle inspection stays valid from the inspection date" (calendar months, anchored on the inspection date) is not a sentence of a cited base rule. F's declared replacement fixes the expiry as inspection date plus validity days, with a 30-day month and a clock-start that can anchor on the old expiry. Whether a reader holding both reaches a second answer is demonstrated per task.
- E. "On the day after a required document expires without an unexpired replacement on file, the agreement goes on hold with reason document_expired" is replaced for the registration, declared. The standard grace of 1 day reproduces "the day after".
- D (refs: rating_standard, cancellation_standard; `overwrite: []`). The cited rules never fix the warning's number, so no cited sentence is contradicted. Two base surfaces still sit next to D (observation O-3, demonstrated per task):
  - (a) the base event gloss `notice_sequence: "1 for the first warning in the current cycle."` and the 90-day `warning_validity_days` / `driver_msr_live_warnings`. D's 12/18/24-month cycle window and its severity addition can give a cycle's first warning a number above 1.
  - (b) driver_cancellation_standard, inherited in full: "a further breach while cancellation_warnings_before_hold warning is on record within warning_validity_days places the agreement on hold for cancellation_hold_days … When breaches in the lookback reach cancellation_breaches_for_deactivation, the agreement is deactivated for cancellation_rate instead of held". When D's owed warning is such a further breach, the base owes a cancellation hold or deactivation as well. No write in this difficulty places a cancellation_rate hold.

### factor_ladders

| Policy | Factors (effect) | parameter / method | Multi-source factors | cross_difficulty |
| --- | --- | --- | --- | --- |
| A | tenure(p), pro_status(p), lapsed_insurance_or_license(p), review_rating(p), recent_warnings(p), expiry_notice_rule(m) | 5 / 1 declared; **0 honest method** (finding G-1) | expiry_notice_rule: agreement expiry fields × notice rows | pro_status → earnings |
| B | insurance_lapse(p), late_insurance_renewals(p), pro_status_and_tenure(p), insurance_history(p), binder_term(p), agreement_standing(m) | 5 / 1 | pro_status_and_tenure (earnings holding ∧ agreement activation date, on both non-fall-through tiers) | pro_status_and_tenure → earnings |
| C | old_license_remaining(p), background_check_recency(p), other_documents_on_file(p), late_renewals(p), pro_status(p), agreement_standing(m) | 5 / 1 | other_documents_on_file (insurance, inspection, permit fields — one row) | pro_status → earnings |
| D | cycle_window(p), tenure(m), pro_forgiveness(p), severity(p) | 3 / 1 | severity (review row × level threshold) | pro_forgiveness → earnings |
| E | tenure(p), late_registration_renewals(p), pro_status_and_rating(p), registration_history(p), standing_on_record(m) | 4 / 1 | pro_status_and_rating (earnings holding ∧ review row) | pro_status_and_rating → earnings |
| F | vehicle_age(p), late_inspections(p), vehicle_use(p), registration_on_file(p), clock_start(m) | 4 / 1 | clock_start (upload row × agreement field) | none |
| G | old_permit_remaining(p), review_rating(p), other_vehicle_documents(p), background_check_recency(p), permit_renewal_history(p), agreement_standing(m) | 5 / 1 | other_vehicle_documents (agreement fields × registration upload row) | none |

- Every factor has four to six bindings, all disjoint from one another. Every `decides` is an input binding, never `result`. Every ladder has three pairwise-disjoint tiers.
- No two tiers of any ladder select the same value or method. The outcomes per ladder are: A 10/5/0, 10/5/0, −20/−10/0, 8/4/0, −10/−5/0, ×125↑/×110↑/×1. B −10/−5/0, −6/−3/0, 8/4/0, 6/3/0, 10/5/0, ×80↓/×90↑/×1. C 8/4/0, 6/3/0, −12/−6/0, −6/−3/0, 6/3/0, ×50↓/×75↑/×1. D 24/18/12, ×50↓/×75↑/all, 2/1/0, 2/1/0. E 6/3/0, −3/−1/0, 4/2/0, 3/2/0, ×50↓/×75↑/×1. F −30/−15/0, −20/−10/0, −20/−10/0, −20/−10/0, +ahead/−min(lapsed,30)/×1. G 8/4/0, 6/3/0, −12/−6/0, 6/3/0, 5/2/0, ×40↓/×60↑/×1.
- Every factor's fall-through equals its `baseline`. Every `baseline.rule` is verbatim the leading sentences of its rule and gives a definite number with no factor applied: A 90 (= document_hold_max_days), B 45 capped at the printed end, C 30, D 1 + cancellation warnings within 12 months, E 1, F interval×30, G 30.
- Label honesty:
  - **G-1 (finding).** A's `expiry_notice_rule` is labelled `method`, but its three tiers are one formula with a different rate. The tiers are ⌈adjusted×125/100⌉, ⌈adjusted×110/100⌉ and "taken unchanged". Since `adjusted_length` is an integer, the last equals ⌈adjusted×100/100⌉, so all three are ⌈adjusted×r/100⌉ with r∈{125,110,100}. The rounding direction is the same in all three, so only the number changes. That is a parameter. Without it A has no honest `method` factor (5 parameter, 0 method).
  - Observation O-1: the `method` factors of B, C, D (tenure), E and G all take the shape "×p% rounded down / ×q% rounded up / unchanged". They differ from a rate substitution only because the rounding direction also changes between tiers. They pass the letter of the test because the tiers are not "only a different number", but the method content is thin. Only F's `clock_start`, which re-anchors the validity on a different date, is an unambiguous change of algorithm.
- Realism (observation O-2): the conditions and outcomes are plausible as platform leniency or risk signals: tenure, Pro status, rating, warning history, lapse length, renewal lateness. The weakest are C/G scaling a DMV-issued temporary document's acceptance by Pro status and agreement standing, and F shortening an inspection's validity because the separate registration is near expiry. No condition holds of every customer who reaches its write at charter level. No fall-through is a treatment the line would not publish. Nothing here is demonstrable as RED.
- Per task, with the weight demonstrated in the task file:
  - The A/B/C tree carries a multi-source factor (B pro_status_and_tenure) and cross-difficulty factors (A, B, C read the earnings holding).
  - The D/E/F/G tree carries multi-source factors (E pro_status_and_rating, F clock_start, G other_vehicle_documents) and cross-difficulty factors (D, E read the earnings holding).
  - Within the D/E/F/G tree, F and G have no cross-difficulty factor of their own. That is allowed: the requirement is per task.

### findings

- **G-1 — SOURCE-FACTOR RED (bears on task 0)**
  - Symptom: A declares `expiry_notice_rule` as its only `method` factor, but the factor only substitutes a rate.
  - Root cause: all three tiers are ⌈adjusted_length × r / 100⌉ with r ∈ {125, 110, 100}, the same rounding in each. "Taken unchanged" equals r=100 on an integer.
  - Evidence: A compute `lapse_allowance: (adjusted_length * K('no_notice_pct') + 99) // 100 if lapse_notices == 0 else ((adjusted_length * K('one_notice_pct') + 99) // 100 if lapse_notices == 1 else adjusted_length)`, together with the rule sentence "with two or more such notices, the adjusted length is taken as the lapse allowance days unchanged".
  - Consequence: A's computation has 0 honest `method` factors, below the bound of 1.
  - Location: `driver.extended.yaml` → driver_ext_document_lapse_allowance.factors[expiry_notice_rule] and the compute binding `lapse_allowance`.
- O-1 — observation (bears on both tasks): the method factors of B, C, D, E and G are rate-plus-rounding-direction ladders, not distinct algorithms.
- O-2 — observation: realism of the C/G and F adjustments, as described above.
- O-3 — observation, to be demonstrated per task (task 1). D sits next to the base gloss "notice_sequence: 1 for the first warning in the current cycle", the 90-day warning validity, and the inherited cancellation-hold escalation of driver_cancellation_standard. D declares no overwrite.
- O-4 — observation: A's lapsed-document definition cannot see the vehicle registration. No task world exercises this.
- O-5 — observation, to be demonstrated per task (task 1): F against the base gloss on inspection_interval_months.
- O-6 — observation: the docstrings carry "Afterwards" (the same call's post-state) and name the lookups as argument sources. They state no write sequence.
- O-7 — observation: in B, C, E and G the compute `else` gives "unchanged" for states the rule's standing tiers do not name (for example on_hold with a future start date). In B, the record carries no binder marker, so "the binder" is simply the latest insurance upload.
- O-8 — observation: the `compute_basis` of D's `earlier_warnings`/`result` and of E's `result` quote the baseline sentence rather than the factor-adjusted one.
- O-9 — observation, to be demonstrated per task (task 1): D's "records the cancellation rate shown at the latest rating review" set against E's edge "the quality warning owed for every rating review that found the cancellation rate above the level's threshold".

## closing_checklist

Written 2026-10-11 ~11:58Z. Both task files were frozen before any reveal (task 0, then task 1). GT for both was revealed at 11:55Z and the comparisons were appended. This section is the only post-reveal content in this file.

**The difficulty does NOT close.** Two of the four relationships fail on at least one task, so the source-layer audit is not passed.

| Checklist item | Status |
| --- | --- |
| One audit file per task, plus `_difficulty.md` | `0.md`, `1.md` and `_difficulty.md` are present. This is a first audit, so there are no older revisions. |
| Every comparison carries a PASS | **No.** 0.md: Factors are SOURCE-FACTOR RED (T0-1). 1.md: Factors are SOURCE-FACTOR RED (T1-1, T1-2). |
| Extended policies fully covered; scopes pairwise disjoint | Yes. `charter_scope` of task 0 is {A, B, C} and of task 1 is {D, E, F, G}. That is all seven, disjoint, and each tree spans exactly its claimed scope. |
| Task tools and GT closed | Yes. Each claimed tool is called exactly once in its task's GT, with the arguments derived blind. |
| uuid8s independent | Yes (see `### action_binding_and_uuids`). |
| Every tree has 1-3 prerequisite problems | Task 0 has 2 prerequisite problems and task 1 has 3. |
| At least max(n−1, 1) value_input edges | Task 0 has 3 against a floor of 1; task 1 has 3 against a floor of 2. |
| At least one problem resolved by an owner=user tool | Task 0: C. Task 1: G. |
| No cycle, and the whole graph is a DAG | Yes. |
| Every edge bears weight | Yes, for both tasks. |
| Every computation has a self-sufficient baseline and 4-6 factors | Yes. |
| ≥2 `parameter` and ≥1 `method` per computation | **No for A** (G-1 / T0-1): 0 honest method factors. All other computations satisfy this by the letter; O-1 notes they are thin. |
| Every factor bears weight against an honest baseline, and the all-baseline value differs from gold | Yes, for all seven computations. |
| No stamp shortcut | **No for D** (T1-1): the previous warning's `notice_sequence` + 1 = gold. |
| Cross-difficulty evidence seeded and consistent with its product's charter | Task 0: yes (Silver is reachable). **Task 1: no** (T1-2): Q4 Platinum is unreachable under the earnings tier rule given the seeded review cancellation rates. |
| Instantiation gates re-run on the final form | Not re-run by the auditor, by design. The coordinator's snapshot (all rc=0, traceability deferred) is the cited entry condition. The artifacts were not edited, so the final form equals the gated form. |

## revision_2

### charter_global_frozen (revision_2)

- Inputs, re-hashed by the auditor and matching the coordinator's HASHES.txt:
  - `driver.extended.yaml` 8c53e9801b919fa827bbe7ca9c2fc4df3035f1567b8e70f1666d1ded9b653619. This **changed** from round 1, so every charter-global section below is re-derived in full.
  - `task_tools.py` b6ac364f35d6adb4ec4323fc543dcd80dc508037fdf5a6a01a58c9c6d9d0853d is **unchanged**. The tool-body conclusions of round 1 (`### action_binding_and_uuids`: uuids, no condition checks, docstring observation O-6) are carried forward by reference on that hash.
- Freeze: written 2026-10-11 13:29Z (system clock), before any round-2 GT was read. Auditor: the same erl-task-policy-audit subagent as round 1.
- Masked fields: the same as in round 1.
- contamination_disclosure: this auditor saw the round-1 GT of both tasks during round 1, and the reworker's claim list arrived by item id only. Round-1 gold values do not carry over, because the charter and both worlds changed. Nothing in this section uses a round-2 GT field.
- Base copy: lines 1-971 are still byte-identical to `blueprint/products/driver.yaml`. The seven `(target_tool, computes)` pairs are unchanged and each is claimed by exactly one policy.

### policy_conflict_scan (revision_2)

- Subjects, status writers and field writers are unchanged from round 1, and no two policies write one quantity.
- A's lapsed document now also reads "the vehicle registration on file, which is the latest vehicle registration upload on the standing record". The compute's `lapsed_expiry` includes `LATEST(...vehicle_registration...)`. **O-4 is closed.**
- D now defines its own cycle explicitly: continue for a latest warning fewer than 3 months back, recount at 3-11 months, fresh start at 1 for 12 months or more or for no earlier warning. A fresh cycle "always starts at one", in line with the base gloss "notice_sequence: 1 for the first warning in the current cycle". **O-3(a) is closed.** O-3(b), the base cancellation escalation, is still inherited and is checked per task.
- B, C and G now state "on an agreement in any other standing, they do not change", so the compute `else` has a rule sentence behind it. **O-7 is closed.**
- Scopes: the graph still has two components, {A,B,C} and {D,E,F,G}.

### rule_compute_equivalence (revision_2)

- Every binding has a `compute_basis` quotation, and every quotation is verbatim in its rule (machine-checked over all seven policies).
- D's and E's `result` quotations now cite the shaping sentence, not the baseline sentence. **O-8 is closed.**
- New or changed bindings, each checked in both directions:
  - **A `clock_shift`.** DAYS(hold start → latest second notice covering lapsed_expiry) when there are 2 or more notices; DAYS(hold start → lapsed_expiry) when there is 1; 0 otherwise. Result = adjusted + shift, with no rounding. This matches the "Lapse-clock rule … a clock day before the hold start date makes the days … negative". Edge case: two covering notices with no sequence-2 notice among them would make the second-notice date undefined. The rule says "both expiry notices", so this is an observation only; no world exercises it.
  - **B.** `standing_adj` is −6 / −3 / 0. `takeover_shift`:
    - when the insurance on the agreement is later than the recording day, the days until it ends;
    - when the insurance expired before the upload date, −(the days from upload to recording);
    - otherwise 0.
    Result = MN(MX(0, adjusted + shift), days to the printed end). This matches "never below zero, and the cap at the binder's printed end date is applied last". It has five adjustments (lapse, late, pro_tenure, term, standing), matching "Five adjustments".
  - **C.** `late_adj` has 4 tiers (≥5 / 3-4 / 1-2 / 0). `standing_adj` is −8 / −4 / 0. `takeover_shift = license_left if license_left > 0 else (license_left if −license_left ≥ 14 else 0)`. Result = MX(1, …), matching "never below one". The five adjustments are check, short, late, pro and standing.
  - **D.** `continued_number` is the latest notice_sequence + 1 + severity, or 1 when there is no earlier warning. `months_since_warning` uses MONTHS. `sequence_number` gives 1 at 12 months or more, recount (1 + severity + MX(0, count − forgiven)) at 3 months or more, and continued otherwise. This matches the "Cycle rule". Forgiveness is 3 / 2 / 0.
  - **E.** `clock_shift`:
    - DAYS(expiry → second notice covering it) when there is a warning within 3 months and that notice exists;
    - DAYS(expiry → first notice) when there is no warning, there is an unsafe_driving report within 6 months, and that notice exists;
    - 0 otherwise.
    Result = MX(1, adjusted + shift). This matches the "Grace-clock rule … never fewer than one".
  - **F** is unchanged.
  - **G.** Same shape as C: `standing_adj` −10 / −5 / 0, `takeover_shift` on `permit_left` with relapse_days 14, result MX(1, …).
- No ladder tier lives in only one face.

### action_binding_and_uuids (revision_2)

Carried forward from round 1 on the unchanged `task_tools.py` hash b6ac364f…. The target_tool/computes pairs were re-checked and are unchanged.

### prerequisite_graph (revision_2)

- The edges are the same six as in round 1: B→A, C→B, C→A, E→D, G→F, G→E.
- The graph is acyclic. All edges are state form, and none carries a fallback.
- Every `policy_source` is verbatim in its own rule (re-checked by machine).
- Gates changed with the rework. Each new gate is a real binding and each `effect` is restated to match:
  - B → `standing_adj`
  - C → `short_doc_adj` and `standing_adj`
  - E → `clock_shift`
  - G → `short_doc_adj` and `standing_adj`
- E's effect is restated as "clock_shift changes from 0 to the (negative) days between the expiry date and that notice". That holds only when the registration's second notice is on record. This is checked per task.
- PASS.

### prerequisite_sentences (revision_2)

- All six sentences are textually unchanged from round 1, and each still has a single resolving write.
- The round-1 four-point results stand: connective, state form, no tool or id names, and strength. They are re-confirmed against the new rules, and no new cross-problem order appears in any rule. PASS.

### override_declarations (revision_2)

- Declared overwrites are unchanged: A replaces the 90-day lapse clause; B, C, F and G replace the upload sentence for their own document; E replaces the day-after hold sentence; D has `overwrite: []`.
- A sentence-by-sentence re-check against each base ref finds no new conflict.
- D's continued tier, "latest earlier number + 1", and its fresh tier, "1", agree with the base gloss.
- The O-5 observation on F stands unchanged, because F is unchanged.

### factor_ladders (revision_2)

| Policy | Factors (effect) | p / m | Multi-source | Cross-difficulty |
| --- | --- | --- | --- | --- |
| A | tenure, pro_status, lapsed_insurance_or_license, review_rating, recent_warnings (p); lapse_clock (m) | 5 / 1 | none | pro_status → earnings |
| B | insurance_lapse, late_insurance_renewals, pro_status_and_tenure, binder_term, agreement_standing (p); takeover_clock (m) | 5 / 1 | pro_status_and_tenure | pro_status_and_tenure |
| C | background_check_recency, other_documents_on_file, late_renewals (4 tiers), pro_status, agreement_standing (p); license_takeover (m) | 5 / 1 declared, **0 honest m** (G2-1) | none | pro_status |
| D | cycle_window, pro_forgiveness, severity (p); cycle_rule (m) | 3 / 1 | none | pro_forgiveness |
| E | tenure, late_registration_renewals, pro_status_and_rating, registration_history (p); grace_clock (m) | 4 / 1 | pro_status_and_rating; grace_clock (warning ∧ notice row) | pro_status_and_rating |
| F | unchanged (4 p / 1 m: clock_start) | 4 / 1 | clock_start | none |
| G | review_rating, other_vehicle_documents, background_check_recency, permit_renewal_history, agreement_standing (p); permit_takeover (m) | 5 / 1 declared, **0 honest m** (G2-1) | other_vehicle_documents | none |

- **Method honesty.**
  - A's `lapse_clock` re-anchors the clock on three different days: the second notice's date, the lapsed expiry date, or the hold start. These are distinct algorithms. **G-1 is closed.**
  - B's `takeover_clock` anchors on three different days: the insurance end, the upload date, or the recording day.
  - D's `cycle_rule` chooses among continuing, recounting or restarting.
  - E's `grace_clock` anchors on the second notice, the first notice, or the expiry.
  - F's `clock_start` is unchanged.
  - With these, the "×p% and round" methods are gone. **O-1 is closed.**
- **G2-1 (finding): C's `license_takeover` and G's `permit_takeover` each have two tiers that select the same method.**
  - Compute: `takeover_shift: license_left if license_left > 0 else (license_left if (0 - license_left) >= K('relapse_days') else 0)`, and identically on `permit_left` for G. The tier-1 and tier-2 branches are the same expression, DAYS(upload day, expiry on file).
  - The rules confirm it in prose:
    - Tier 1: "the temporary license takes over when that license ends, so its cover is counted from that expiry date".
    - Tier 2: "the cover is counted from that expiry date, so the uncovered days are not made up".
    - G's permit sentences say the same.
  - So one method ("count the cover from the old document's expiry date") is written as two tiers. Only tier 3 ("counted from the upload day") is a different method. Each ladder therefore has two distinct outcomes, not three.
  - Under "no two tiers, the fall-through included, select the same value or method", these factors do not survive. C and G are each left with 5 `parameter` and **0 `method`**.
- Every other ladder has pairwise-distinct outcomes. Every factor's fall-through equals its `baseline`.
- Each `baseline.rule` gives a definite number:
  - A: 90
  - B: 45, capped at the printed end
  - C: 30
  - D: the latest earlier warning number + 1, or 1. This is now the stamp reading itself, stated honestly as the standard method.
  - E: 1
  - F: interval × 30
  - G: 30
- Per-task requirements are met in principle: task 0 has a multi-source factor (B pro_status_and_tenure) and a cross-difficulty one (A, B and C Pro); task 1 has multi-source factors (E ×2, F, G) and cross-difficulty ones (D, E). Each task file demonstrates them.

### findings (revision_2)

- **G2-1 — SOURCE-FACTOR RED (new in round 2; bears on task 0 via C and on task 1 via G).**
  - Symptom: `license_takeover` (C) and `permit_takeover` (G) give their first two tiers the same method.
  - Root cause: both tiers compute `takeover_shift = DAYS(upload day, old expiry on file)`, and the rule describes both as "counted from that expiry date". This is a single tier written as two.
  - Consequence: each ladder has only 2 distinct outcomes, so C and G each have 0 honest method factors.
  - Location: `driver.extended.yaml` → driver_ext_temporary_license_acceptance and driver_ext_temporary_permit_acceptance: `factors[license_takeover / permit_takeover]`, the `takeover_shift` compute binding, and the "License takeover rule" / "Permit takeover rule" sentences.
  - Relation to round 1: the factor was introduced by the rework, replacing old_license_remaining / old_permit_remaining. It is not a regression of a closed item.
- Status of the round-1 charter items:

  | Item | Status |
  | --- | --- |
  | G-1 | closed |
  | O-1 | closed |
  | O-3(a) | closed |
  | O-4 | closed |
  | O-7 | closed |
  | O-8 | closed |
  | O-2 | stands (realism, unchanged in substance) |
  | O-5 | stands (F unchanged) |
  | O-6 | stands (tools unchanged) |
  | O-9 | stands, checked per task |
  | O-3(b) | stands, checked per task |

- New observation O2-1: A's `clock_shift` would fail to evaluate if two covering notices existed without a sequence-2 notice among them. No world exercises this.

## closing_checklist (revision_2)

Written 2026-10-11 ~13:33Z. Both round-2 frozen sections were written before the round-2 reveal at 13:30:38Z, and the comparisons were then appended. The round-1 `closing_checklist` above is left untouched.

**The difficulty still does NOT close.** The factors relationship fails on both tasks, through new finding G2-1.

| Item | Status |
| --- | --- |
| Round-1 REDs | G-1/T0-1, T1-1 and T1-2 are **closed**, verified on the reworked charter and seeds (see `0.md` / `1.md` → `## revision_2`). |
| Round-1 observations claimed closed | O-1, O-3(a), O-4, O-7, O-8, O-T0-a, O-T0-b, O-T1-a: **closed**, verified. |
| Comparisons carry PASS | **No.** Factors are SOURCE-FACTOR RED in both tasks: R2-T0-1 (C) and R2-T1-1 (G), both from G2-1. Task 1 also has a proof-text defect, R2-T1-2. |
| Unique solution | Both tasks PASS; GT is identical to the blind derivation. |
| Problem tree | Both tasks PASS. |
| Policy self-consistency | Both tasks PASS. |
| Coverage and scope disjointness | Unchanged and passing: {A,B,C} and {D,E,F,G}. |
| Tools and uuids | Unchanged; carried forward by hash. |
| Tree shape (1-3 prerequisite problems, enough value_input edges, a user write, a DAG) | Passes for both tasks. |
| Baselines and 4-6 factors | Pass. Every factor bears weight, and every all-baseline result differs from gold (task 0: 90/45/30 vs 76/32/21; task 1: 8/1/180/30 vs 6/6/138/44). |
| ≥1 honest method per computation | **No for C and G** (G2-1). Every other computation passes. |
| Multi-source and cross-difficulty factors per task | Pass. The cross-difficulty holdings are now charter-consistent (task 0 Silver, task 1 Gold). |
| Gates | Not re-run by the auditor. The coordinator's round-2 snapshot (all rc=0) is cited. |

## revision_3

### charter_global_frozen (revision_3)

**Inputs.** I re-hashed every input; each matches the coordinator's list.

| Input | sha256 | Status | Treatment this round |
| --- | --- | --- | --- |
| `driver.extended.yaml` | d7a54f85736513c593ba19bd76cfb15104883ab7149ede771acebb4ce234a5cd | changed | re-derived in full below |
| `task_tools.py` | b6ac364f…853d | unchanged | carried forward by reference |
| Both views | db522c8a… and b5418b5b… | unchanged | — |

**Freeze.** Written 2026-10-11 14:30Z by the system clock, before any round-3 GT was read. The masking is the same as in earlier rounds.

**contamination_disclosure.** I saw the round-1 and round-2 GT in earlier rounds. Because the worlds are unchanged, I know the round-2 gold values for both tasks. To compensate, every round-3 value below was recomputed from the round-3 charter on the views, never copied.

**Base copy.** Lines 1-971 are still byte-identical to the blueprint charter.

**What changed against revision_2.** I compared the full rules, computes and factors of all seven policies.

| Policy | Change |
| --- | --- |
| A | The lapse-clock rule now says "when only one of them is on record, which includes two covering notices of which neither is a second notice". `clock_shift` now also requires a sequence-2 notice date before taking the second-notice tier. |
| B | The late-renewal ladder gains a top tier: "three or more … late_three_adj (−10)". It now has 4 tiers. |
| C | License-takeover tier 2 now reads "the cover is counted from the upload day and the uncovered days beyond relapse_days are taken off, at most lapse_cap_days days" (lapse_cap_days = 10). The compute is `0 - MN((0 - license_left) - relapse_days, lapse_cap_days)`. The structure sentence is now "the license takeover rule then adds days to them or takes days off them as it states". |
| D, E, F | Unchanged. |
| G | The same change as C, on `permit_left`. |

### rule_compute_equivalence (revision_3)

- Re-checked by machine. Every binding has a `compute_basis`, and every quotation appears verbatim in its rule.
- Every prerequisite `policy_source` sits in its own rule.
- Every gate is a real binding of its policy.
- The changed bindings match their sentences in both directions:
  - A: the guard.
  - B: the 4-tier late ladder.
  - C and G: the tier-2 deduction, with its cap.

### action_binding_and_uuids / prerequisite_graph / prerequisite_sentences / override_declarations (revision_3)

All four checks still pass:

- **Tools.** Unchanged, and carried forward on the unchanged hash.
- **Prerequisite edges.** The six edges, their sentences and their gates are textually unchanged from revision_2, and the graph is still acyclic.
- **Overrides.** The declared overwrites are unchanged, and none of the changed sentences conflicts with a base sentence.

### factor_ladders (revision_3)

**Factor counts per policy are unchanged.** A, B, C and G have 5 parameter and 1 method; D has 3 and 1; E and F have 4 and 1.

**G2-1 is closed.** The takeover ladders of C and G now select three distinct methods:

| Tier | Method |
| --- | --- |
| 1 | Anchor on the old document's expiry and add the days to it. |
| 2 | Anchor on the upload day and take off the uncovered days beyond relapse_days, capped at lapse_cap_days. |
| 3 | Anchor on the upload day and take nothing off. |

- Tiers 2 and 3 share an anchor but differ in algorithm: tier 2 applies a computed, capped deduction. This is the same structure as F's `clock_start`, which the audit has accepted since round 1.
- Probing the charter compute on the task-0 world (adjusted 16) with synthetic license dates gives 21 (tier 1, +5), 9 (tier 2, 21 days lapsed, −7), 6 (tier 2, capped at −10) and 16 (tier 3).
- **Observation O3-1.** At exactly relapse_days (14 days lapsed) tier 2's deduction is 0, so it coincides with tier 3 at that single boundary point. This is an edge where the outcomes meet, not a duplicated method, so it is not RED.

**B's late-renewal ladder.** It now has 4 pairwise-distinct tiers: −10, −6, −3, 0.

**Other ladders.** Every other ladder is unchanged from revision_2.

### findings (revision_3)

| Round-2 item | Status in round 3 | Basis |
| --- | --- | --- |
| G2-1 | **closed** | See factor_ladders above. |
| O2-1 | **closed** | A's guard plus its rule sentence. |
| O-2, O-5, O-6, O-9, O-3(b) | stand unchanged | — |

There is no new charter-global RED. The one new item is the boundary observation O3-1.

## closing_checklist (revision_3)

Written 2026-10-11 ~14:32Z, after the round-3 reveal at 14:30:52Z. The earlier closing checklists above are left untouched.

**The difficulty closes at the source layer.** All four relationships PASS on both tasks.

| Item | Status |
| --- | --- |
| Audit files | One per task (`0.md`, `1.md`) plus `_difficulty.md`. revision_1, revision_2 and revision_3 are preserved, and each comparison section in revision_3 carries PASS. |
| Round-2 REDs | All closed and verified: G2-1, R2-T0-1, R2-T1-1, R2-T1-2. |
| Round-2 observations | O2-T0-a and O2-1 closed. |
| Round-1 REDs | G-1/T0-1, T1-1, T1-2 remain closed and did not regress. |
| Coverage | The extended policies are fully covered. Scopes are pairwise disjoint ({A,B,C} and {D,E,F,G}). Task tools and GT are closed, and the uuid8s are independent (unchanged tool module). |
| Trees | Task 0 has 2 prerequisite problems and 3 value_input edges; task 1 has 3 prerequisite problems and 3 value_input edges. Each tree contains a user write (C, G). The whole graph is acyclic. |
| Factors per computation | Every computation has a self-sufficient baseline and 4-6 factors, with at least 2 parameter and exactly 1 honest method each. |
| Multi-source and cross-difficulty factors | Each task has at least 1 of each. Both cross-difficulty holdings are consistent with the earnings charter. |
| Factor weight | Every factor bears weight. Every all-baseline value differs from gold: task 0 is 90/45/30 against 76/32/21, and task 1 is 8/1/180/30 against 6/6/138/44. |
| Near-misses | Every computation has a genuine near-miss: A 71, B 28, C 17, D 7, E 8, F 128, G 47. |
| Observations still open | O-2 (realism of some C/G/F adjustments), O-5 (base parameter gloss vs F), O-6 (docstring "Afterwards"), O-9 / O-3(b) (checked per task; neither bites), and O3-1 (tier 2 meets tier 3 at the 14-day boundary). None is RED. |
| Instantiation gates | Not re-run by the auditor. The coordinator's round-3 snapshot (all rc=0, traceability deferred to render) is the cited evidence for the final form. |
