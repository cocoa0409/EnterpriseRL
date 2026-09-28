# Policy-task audit — insurance_rejections_and_prior_auth / charter-global

## charter_global_frozen

- auditor: independent erl-task-policy-audit agent (not the instantiation agent); revision r1
- freeze time: 2026-09-24T18:17Z (written before any task's GT was revealed)
- frozen inputs:
  - `env/env_0021_retail_pharmacy_chain/tasks/insurance_rejections_and_prior_auth/coverage.extended.yaml` sha256 `397a8e5aa5833d83608d37ce5f177bf93fd64519e1e73303013c87824be8b71d` (matches the brief)
  - `env/env_0021_retail_pharmacy_chain/tasks/insurance_rejections_and_prior_auth/task_tools.py` sha256 `3ede327dd1da221b6994650d4bf11d2b514d564763ab1c93217a78a0a9f3725e` (matches the brief)
  - `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/coverage.yaml`; the delivery and refill product charters were read only for the cross-category parameters the compute names (`mail_transit_business_days`, `refill_lead_days`, `packaging_prep_days`); the compute DSL semantics were read from `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, `LATEST`/`XCOUNT`/`MONTHS`/`DAYS`), which holds no task data.
- permitted: the fields above only. Masked and unread while this section was written: every field of `tasks/0.json` and `tasks/1.json` (this section uses no task world at all), every existing audit, the instantiation transcript and scratch.
- Entry conditions (Step 0): the brief supplied the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0 with their OK lines; check_traceability deferred until the KB is published), and the masked views with their sha256 (re-hashed by this auditor: task0.view.json `9240eaa5…a031`, task1.view.json `43a99d21…9f99`, both match). Entry conditions met. The gate results are cited, not re-run.
- Base copy: `diff` of lines 1–1178 of the extended file against `blueprint/products/coverage.yaml` (1178 lines) is empty, so the base section is a verbatim copy.

### policy_conflict_scan

The charter holds 10 base policies and 4 extended policies:

| extended policy | target tool (owner) | computes | base refs | overwrite | prerequisite |
| --- | --- | --- | --- | --- | --- |
| coverage_ext_appeal_decision_window | file_coverage_appeal_f21a07b8 (user) | decision_window_days | coverage_evt_appeal | 1 (decision_due_date sentence) | [] |
| coverage_ext_continuation_supply_days | bill_continuation_supply_837ca024 (agent) | days_supply_billed | 7 base policies | 1 (PA denial sentence) | value_input ← appeal_decision_window |
| coverage_ext_corrected_rebill_patient_pay | rebill_corrected_claim_b015fa67 (agent) | patient_pay_usd | 7 base policies | [] | [] |
| coverage_ext_cash_rebill_patient_pay | submit_cash_fill_rebill_483f3c39 (user) | patient_pay_usd | 7 base policies | [] | value_input ← corrected_rebill_patient_pay |

Overlap scan:
- **Subjects/events.** Appeal policy writes `coverage_appeal_filed`; the other three write `coverage_claim_paid` rows distinguished by `claim_basis` (`emergency_pa_supply`, `retro_rebill` naming a reversed claim, `retro_rebill` for a cash fill). The two `retro_rebill` writers are separated by object: the corrected claim names a `billing_correction` reversal (`source_claim_id` is written only by `rebill_corrected_claim_b015fa67`), the cash re-bill targets a cash-paid `rx_fills` row. No two extended policies compute the same quantity on the same object.
- **Shared ledger reads.** The cash re-bill's "most recent claim re-billed on the coverage" reads `retro_rebill` rows, which the corrected-claim write produces — this is the declared value_input edge, not an undeclared conflict. The continuation's "most recent appeal on the coverage" reads the row the appeal write produces — the other declared edge.
- **Triggers / eligibility / time anchors.** Base eligibility inherited without conflict: bill only active coverage (`bill_active_coverage_only`), `max_days_supply_per_claim` cap (restated as the continuation's cap), cash re-bill window (`cash_rebill_window`, day 0 = cash fill date), appeal filing window and one-appeal-per-denial (`within_appeal_window`, `one_appeal_per_denial`), one reversal per claim. None of the extended rules weakens them.
- **Terminal states.** Each extended write creates one ledger row; no status transition is shared.
- **Cross-category reads.** delivery (plan + completed orders), refill (active enrollment + variant params), rx (fill ledger). All reads, none writes; boundaries consistent with those charters' tables.
- **Scope partition.** The two prerequisite edges split the four extended policies into two disjoint trees: {appeal_decision_window → continuation_supply_days} and {corrected_rebill_patient_pay → cash_rebill_patient_pay}. With M=2, one tree per task is exclusive and jointly complete provided each task claims one tree (confirmed per task after reveal, in the task files).

No conflict between extended and base, or between two extended policies, reaches a different conclusion in the same situation (see override_declarations for the sentence-level findings).

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quotation and back against the rule, using the DSL semantics of `check_compute.build_env` (holding-scoped `COUNT/LATEST` filter on `coverage_id`; `LATEST` = max `event_date`; `XCOUNT(within_months=n)` counts rows with `0 <= MONTHS(date, NOW) < n`; `MONTHS` = whole months with day-of-month correction; `DAYS(a,b)` = b − a).

- **coverage_ext_appeal_decision_window.** supply left (`MX(0, days − DAYS(date, NOW))`), lapse test (`DAYS(end, NOW) >= 1` ⇔ "approval_end_date is at least one day before the filing date"), three-tier review clock, three-tier extension on the latest denial reason, three-tier anchor (`days_since_denial` off if ≤ timely_appeal_days, else `−supply_left` if supply ≥ 1, else 0), three-tier continuity credit on the count of `pa_approved` paid claims, final `MX(1, …)`: each has a verbatim quotation and each rule sentence is implemented. The rule sentence "The appeal is recorded as expedited when the urgent clock applies and as standard otherwise" governs the `review_type` argument, which is not a compute binding; it is derivable from `review_clock`'s tier and is not an empty promise. The sentence "The review clock of the appeal is set by the patient's cover on the filing date" is a heading sentence with no separate quantity. PASS.
- **coverage_ext_continuation_supply_days.** days to the decision due date (0 without an appeal), delivery lead, refill-program lead, approved supply remaining, start days off, renewal courtesy, titration days, decision buffer, raw sum, `MN(max_days, MX(1, raw))` — all quoted and implemented. Two gaps between faces that no task world here exercises (observations O-2, O-3): (a) the rule's titration tiers speak of "a refill dispensed … for a dosage change", while `recent_dose_change_refills`/`earlier_dose_change_refills` filter only `fill_reason='dosage_change'` with no `event_type='rx_refill'` filter, so an original fill or remake carrying that reason would count in compute and not in the rule; (b) the renewal-courtesy rule speaks of a request "started fewer than late_renewal_window_days calendar days before the approval_end_date", while `request_lead_before_end < 7` also places a request started after the approval_end_date (negative lead) in the late tier, a case the rule's "before" does not cover. PASS for both task worlds (see the task files: the only dosage-change row is an `rx_refill`; the lead is +4).
- **coverage_ext_corrected_rebill_patient_pay.** fill identity, copay tier, supply basis, waiting share, member share, mail-service rate, override share, single end rounding — all quoted and implemented. The rule names the corrected fill twice: "for the fill the reversed claim paid for" and "The fill a corrected claim is for is the patient's most recent refill settled through insurance"; compute implements only the second. The two coincide whenever the reversed claim paid the latest insured refill; they can diverge otherwise (observation O-4; demonstrated or not per task world in the task file).
- **coverage_ext_cash_rebill_patient_pay.** re-bill rate (0 when no re-billed claim), cash fill identity, days charged, listing share, out-of-pocket share, sync share, member share on net paid claims, gap share, end rounding, cap at cash paid — all quoted and implemented. PASS.

No compute binding invents a basis the rule does not state; no factor tier exists in one face only (every ladder tier is a rule sentence and a branch of its `decides` binding, and vice versa).

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (file_coverage_appeal_f21a07b8, decision_window_days), (bill_continuation_supply_837ca024, days_supply_billed), (rebill_corrected_claim_b015fa67, patient_pay_usd), (submit_cash_fill_rebill_483f3c39, patient_pay_usd) — each claimed by exactly one policy.
- Tool bodies (`task_tools.py`): each creates exactly one row with the arguments as given; none reads the ledger, checks eligibility, checks a prior step or refuses (module docstring: "None of them checks eligibility, prior steps or amounts"). No tool judges a prerequisite.
- Docstrings: none names another tool or states a position in a sequence of actions. The word "afterwards" appears in each ("Afterwards the plan's claim history shows …") describing the tool's own visible effect, not an order relative to another action. `bill_continuation_supply_837ca024`'s summary line — "a drug whose prior authorization renewal was denied and is under appeal" — describes the subject in terms of the depended-on state (observation O-5; the same fact is already in the continuation rule's own first sentence, so the docstring discloses nothing the policy surface does not).
- uuid8s: `f21a07b8`, `837ca024`, `b015fa67`, `483f3c39` — no shared prefix, suffix, sequence or adjacency; consistent with independent generation. PASS.
- Argument-to-row fidelity: `bill_continuation_supply_837ca024` takes `claim_id` and `fill_id` but writes them only into the row id hash (no `source_claim_id`/fill column); `submit_cash_fill_rebill_483f3c39` takes `claim_id` (the turned-down claim) likewise only into the id hash. This matters for check 6: neither of these two writes sets `source_claim_id`, so only `rebill_corrected_claim_b015fa67` can bring about the cash re-bill's waited-on state.

### prerequisite_graph

| blocked policy | problem | kind | gate | form | policy_source locatable verbatim in own rule | resolved_by = problem's target_tool | gate binding exists |
| --- | --- | --- | --- | --- | --- | --- | --- |
| coverage_ext_continuation_supply_days | coverage_ext_appeal_decision_window | value_input | days_to_decision | state | yes (rule sentence 3) | yes | yes (`days_to_decision`) |
| coverage_ext_cash_rebill_patient_pay | coverage_ext_corrected_rebill_patient_pay | value_input | rebill_rate | state | yes (rule sentence 2) | yes | yes (`rebill_rate`) |

- Every extended policy fills `prerequisite` (`[]` for the two depended-on policies). Both `problem` ids are extended policies of this file, neither points at itself or at a base policy. Graph: two disjoint single edges — acyclic.
- `form: state` on both; no `fallback_reason` present, as required.
- `condition` vs the sentence: continuation — "coverage_prior_auths carries, on the coverage, a coverage_appeal_filed row whose source_pa_id is the coverage's most recent coverage_pa_denied row" = "the prior-authorization ledger carries an appeal filed against the plan's most recent denial on the coverage": same strength and scope. Cash re-bill — "every coverage_claim_reversed row on the coverage with reversal_reason billing_correction has its reversed claim named, as source_claim_id, by a coverage_claim_paid row with claim_basis retro_rebill on the same coverage" = "every claim on the coverage reversed for a billing correction is named by a re-billed claim on the claim ledger": universally quantified in both, same scope.
- `effect`: continuation — the appeal row makes `appeals_on_coverage >= 1`, so `days_to_decision` moves from 0 to `DAYS(NOW, decision_due_date)`: the effect holds. Cash re-bill — the corrected `retro_rebill` row makes `rebills_on_coverage >= 1`, so `rebill_rate` moves from 0 to its patient pay per day, and `net_paid_claims` rises by one: the effect holds (both bindings are in the cash re-bill's compute).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") in any `prerequisite` field. PASS.

### prerequisite_sentences

Edge A — continuation ← appeal. Sentence: "The days supply of a continuation supply is fixed only after the prior-authorization ledger carries an appeal filed against the plan's most recent denial on the coverage."
1. Ordering connective: "only after" joins the policy's own result (the days supply) to what it waits on. ✓
2. State form: "the prior-authorization ledger carries an appeal filed against the plan's most recent denial" — a record-visible state in the finder's words (`find_coverage_prior_auths`: "appeals the patient filed"); no performer, no tool. ✓
3. No tool name, policy id, snake_case token or row id. ✓
4. Strength/scope equals the `condition` (see prerequisite_graph). ✓
- Single writer: the only write of this difficulty that creates a `coverage_appeal_filed` row is `file_coverage_appeal_f21a07b8` (the other three create `coverage_claim_paid` rows). ✓
- Derivation, one reading: the sentence names an appeal row on the prior-authorization ledger → the reader looks for the policy whose rule records such a row → coverage_ext_appeal_decision_window ("An appeal the patient files against a prior authorization denial is recorded with an appeal decision window …"), with base coverage_evt_appeal: "An appeal is the patient's own request to the plan and is filed only by the patient, never by Kestrel" → the resolving action is the patient's own appeal filing, handed over, with the window computed under the appeal policy. No second reading.
- Second wording (observation O-1): the continuation rule's first sentence, also the `replaced_by` of its overwrite, reads "a patient who appeals the denial of a renewal is paid a continuation supply of the drug while the appeal is pending". This restates the same dependency in eligibility words ("a patient who appeals … while the appeal is pending") beside the prerequisite sentence. The two give the same conclusion on any world where the pending appeal is against the most recent denial (the prerequisite sentence is the narrower); no world here separates them, so no consequence is demonstrable. The depended-on (appeal) rule does not restate the sentence. ✓

Edge B — cash re-bill ← corrected claim. Sentence: "The patient pay of a re-billed cash fill is not fixed until every claim on the coverage reversed for a billing correction is named by a re-billed claim on the claim ledger."
1. Connective "not … until". ✓ 2. State form in the claim-history finder's words ("claim reversals and their reason"; "source_claim_id: … to find its reversal"). ✓ 3. No tool/id/snake_case. ✓ 4. Same scope as `condition`. ✓
- Single writer: only `rebill_corrected_claim_b015fa67` writes `source_claim_id` (the continuation and cash re-bill writes do not; see action_binding_and_uuids). ✓
- Derivation, one reading: a reversed-for-billing-correction claim not yet named by a re-billed claim → the policy whose rule says such a claim "is owed a corrected claim … re-billed with claim_basis retro_rebill … and the corrected claim names the reversed claim" = coverage_ext_corrected_rebill_patient_pay → agent write. No second reading. No second wording of this dependency in the cash re-bill rule; the corrected-claim rule does not restate it. ✓

Undeclared cross-problem orders: none of the four extended rules states an order between two problems other than the two sentences above. Base sentences that state cross-problem orders — coverage_evt_claim_reversal "a fill still in will-call on that day is returned to stock first"; coverage_plan_termination "a claim paid in error after termination is reversed … and re-billed"; coverage_agg_multi_holding "A third plan is added only after one of the two open records is removed or terminated" — ground no edge of either tree (observation O-6, per the skill's rule for base sentences). PASS.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (conclusion per sentence; "follows" = extended leaves the governed quantity as base sets it).

- **coverage_ext_appeal_decision_window vs coverage_evt_appeal.** S1 (patient's own request, never Kestrel) follows — target tool owner=user. S2 (filing window from denial date) follows (eligibility inherited). S3 (one appeal per denial) follows. S4 (decision_due_date = filing + standard days, or expedited hours when prescriber attests urgency) — handled differently; declared in `overwrite` as the superseded clause, replaced by "filing date plus that window". After replacement the due date is unique (the extended ladder). The replaced sentence was the only base link between `review_type` and prescriber attestation; the extended rule sets review_type by the urgent-clock tier, so the merged semantics for review_type are unique. S5 (overturned/upheld handling) follows. PASS.
- **coverage_ext_continuation_supply_days** (7 refs). coverage_evt_prior_authorization: "A denial ends the request; the patient may then pay cash … or appeal" — handled differently (adds the continuation supply); declared. "While a request is waiting, a plan whose pa_emergency_supply_days is above 0 pays one emergency supply of up to that many days with claim_basis emergency_pa_supply" — the continuation reuses `claim_basis emergency_pa_supply` with a days supply that is not capped at `pa_emergency_supply_days`; the base sentence governs the supply "while a request is waiting", and after a denial no request is waiting, so the base sentence does not reach the continuation's situation: not an override, but the shared claim_basis on classes whose `pa_emergency_supply_days` is 0 is a reading hazard (observation O-7). coverage_evt_claim_billing: active-status gate and `max_days_supply_per_claim` cap follow (the cap is restated). coverage_evt_refill_too_soon: governs routine claims; the continuation is not a routine claim — no conflict. coverage_agg_coordination_of_benefits, coverage_evt_transition_fill, coverage_evt_claim_reversal, coverage_program_restrictions: no sentence governs the continuation's days supply — follow. PASS.
- **coverage_ext_corrected_rebill_patient_pay** (7 refs, `overwrite: []`). coverage_evt_claim_reversal: "A paid claim is also reversed … to correct a billing mistake"; "Each paid claim is reversed at most once" — follow; base sets no re-bill amount for a billing correction, so the extended patient pay fills an unset quantity. coverage_evt_claim_billing: active-status gate, days-supply cap, 90-day mandate after courtesy fills, deductible, patient-pay cap, OOP cap — none of these fixes the corrected claim's patient pay differently on any class for which the extended copay rule is written; the 90-day mandate would reject a ≤34-day claim only once `coverage_msr_courtesy_fills_plan_year` reaches `courtesy_30_day_fills` (a gate, not a pay amount; judged per world in the task file). coverage_evt_refill_too_soon: governs whether a routine claim pays, not its amount; judged per world. Others: no governing sentence. `overwrite: []` holds. PASS.
- **coverage_ext_cash_rebill_patient_pay** (7 refs, `overwrite: []`). coverage_evt_claim_reversal: "A fill the patient paid in cash is re-billed to a coverage record added afterwards only when … no later than the date the cash fill was dispensed plus the cash rebill window days …; the re-billed claim carries claim_basis retro_rebill and the patient is refunded the difference …" — followed (extended restates retro_rebill, the refund and keeps the window as inherited eligibility). Base sets no re-billed patient pay; the extended fills it. Base is silent on who submits; the extended's "by the patient's own submission" adds the performer (see observation O-8 on the blueprint summary). coverage_evt_claim_billing and coverage_evt_refill_too_soon gates judged per world. `overwrite: []` holds. PASS.

Disguised forms: no anonymous intermediate replaces a base-computed quantity; no 0/1 multiplier zeroes a base-fixed amount (the 0 re-bill rate applies only where base fixes no amount); no base branch is dropped. No author note calls a base output a "wrong value".

### factor_ladders

Counts per policy (labels as declared; honesty assessed below):

| policy | factors | parameter | method | multi-source factors | cross_difficulty (declared) |
| --- | --- | --- | --- | --- | --- |
| appeal_decision_window | 4 | 3 (review_clock_choice, records_review_extension, continuity_credit_tier) | 1 (filing_anchor) | review_clock_choice (both non-fall-through tiers: approval lapse [prior-auth row] AND supply left [claim row]) | none |
| continuation_supply_days | 6 | 5 (delivery_lead_tier, refill_program_lead_tier, renewal_courtesy_tier, titration_overlap, decision_buffer_tier) | 1 (continuation_start) | delivery_lead_tier (plan variant [delivery_plans] AND completed delivery [delivery_orders], both tiers) | delivery, refill, rx |
| corrected_rebill_patient_pay | 6 | 5 (corrected_copay_tier, correction_waiting_share, new_member_share_tier, mail_service_rate_tier, override_courtesy_tier) | 1 (corrected_supply_basis) | corrected_copay_tier (product of the corrected fill AND count of other refills, both tiers); mail_service_rate_tier (plan variant AND completed delivery, both tiers) | rx, delivery |
| cash_rebill_patient_pay | 6 | 5 (late_listing_share, out_of_pocket_wait_share, sync_share_tier, established_member_share, gap_purchase_share) | 1 (cash_fill_days_charged) | none | rx, refill |

Structure checks:
- Every `decides` is an input binding, never `result`; each factor's `bindings` set is disjoint from every other factor's in its policy.
- Every ladder has exactly three pairwise-disjoint tiers, fall-through counted; every tier is stated in the rule with its condition and value/method, and implemented as a branch of the `decides` binding. Every fall-through equals the factor's `baseline`, and every `baseline` equals what the policy's `baseline.rule` yields for that input (0 / 1 / standard window / standard copay / per-day proration / days supplied).
- `baseline.rule` self-sufficiency: appeal — "filing date plus … appeal_decision_standard_days" (definite); continuation — "calendar days from the claim's date of service to the decision due date of the most recent appeal … never more than max_days_supply_per_claim; when no appeal … 0" (definite); corrected — "standard_copay for each standard_month_days days … prorated per day, rounded to the cent" (definite); cash re-bill — "re-bill rate × days the cash fill supplied, rounded, never more than cash paid; rate 0 when none re-billed" (definite). Each baseline sentence appears verbatim in its rule; `baseline.params` name the defaults used (`params: []` for the cash re-bill is correct: its baseline uses no charter default).
- No two tiers of any ladder select the same value or method for any class: review clock (`appeal_decision_expedited_hours` is 72 on every class, so the urgent clock is 3; Part D Standard/Enhanced and MA-PD: 3 / 5 / 7; Medicaid, commercial and workers' comp: 3 / 5 / 30), extension 14 / 5 / 0, anchor three distinct methods, continuity 5 / 2 / 0, delivery lead (mail plan 3, courier 1, 0), refill lead (packaging 10+3, others 4/7/10, 0), start three distinct anchors, renewal 3 / 1 / 0, titration 7 / 3 / 0, buffer 7 / 3 / 0, copay 10 / 15 / 25, supply 2.5 / 1 / prorated, waiting 0.5 / 0.75 / 1, member 0.9 / 0.95 / 1, mail 0.8 / 0.9 / 1, override 0.8 / 0.9 / 1, days charged 30 / 75 / actual, listing 0.5 / 0.75 / 1, out-of-pocket 0.9 / 0.95 / 1, sync 0.85 / 0.9 / 1, established 0.8 / 0.9 / 1, gap 0.8 / 0.9 / 1.
- Label honesty: every `parameter` factor substitutes a number. `filing_anchor` and `continuation_start` change which quantity anchors the count (days since denial / supply remaining / approval tail / nothing) — a change of anchor, accepted as `method`. `corrected_supply_basis` and `cash_fill_days_charged` switch between a flat charge regardless of length and a per-day proration — a change of pricing method, accepted as `method`. Each method tier names a rule the charter states.
- Cross-difficulty mapping: the blueprint's difficulties claim categories rx, coverage, copay, vax and delivery; **no difficulty claims the `refill` category**. `refill_program_lead_tier` and `sync_share_tier` declare `cross_difficulty: refill`, which names a category, not another difficulty (observation O-9). Tasks still meet the per-task floor through the delivery and rx factors (continuation: delivery_lead_tier, titration_overlap; corrected: corrected_copay_tier, corrected_supply_basis, mail_service_rate_tier).
- Per-tree floor: tree {appeal → continuation} has multi-source (review_clock_choice, delivery_lead_tier) and cross-difficulty (delivery_lead_tier → delivery); tree {corrected → cash re-bill} has multi-source (corrected_copay_tier, mail_service_rate_tier) and cross-difficulty (rx, delivery).

Business reality of conditions and outcomes (charter-global judgement; the per-world demonstration is in each task file):
- **F-1 (conditions scoped to the patient over per-prescription records).** The blueprint holds automated refilling "per prescription as an enrollment" and a fill's `fill_reason` belongs to its own prescription. Three tiers nevertheless decide a quantity of one prescription from any of the patient's prescriptions:
  - continuation `refill_program_lead_tier`: "Where the patient's active automated refill enrollment is Kestrel Med Sync with Adherence Packaging, …; where the patient has any other active automated refill enrollment, that program's refill_lead_days are added" — adds the processing lead of a program the continued drug may not be in (`CFIELD('refill', 'variant_name', status='active')` takes the first active enrollment of any prescription).
  - continuation `titration_overlap`: "When a refill was dispensed to the patient for a dosage change less than recent_titration_months …, recent_titration_days are added for the dose overlap" — a dose overlap for the continued drug that is decided by a dose change of any drug (`XCOUNT('rx', 'rx_fills', …, fill_reason='dosage_change')` has no prescription filter).
  - cash re-bill `sync_share_tier`: "A synchronised patient earns a sync share: when the patient's active automated refill enrollment is Kestrel Med Sync with Adherence Packaging …" — lowers the plan patient pay of a re-billed fill because some prescription of the patient is in Med Sync; medication synchronisation governs when fills are processed, not what a plan claim's patient pay is.
  A pharmacy weighs a titration overlap, a refill-program lead or a sync arrangement for the prescription being supplied or billed, not for another prescription on the profile. These are conditions no business in this line weighs for the quantity when they are met through another prescription; the consequence is demonstrable only on a world where they are so met (task files).
- **F-2 (mail-service rate decided without the fill's channel).** corrected `mail_service_rate_tier`: "A patient served by mail earns the plan's mail-service rate: when the patient holds an active Kestrel Mail Delivery plan and a delivery to the patient was completed less than mail_window_months … before the day the corrected claim is made" — a plan's mail-service rate prices fills dispensed through mail service; the rule applies it to the corrected fill whatever channel that fill went through, decided by some other order's delivery. Demonstrable only where the corrected fill was not mailed (task file).
- Observations on reality that do not reach a demonstrable red: O-10 (the cash re-bill's late-listing share gives the largest reduction, ×0.5, to the patient who added the coverage latest; the corrected claim's new-member share discounts a plan copay for the first months of membership — both are unusual treatments but coherent as Kestrel courtesies); O-11 (the charter has Kestrel compute the plan-assigned patient pay of a paid claim — a modelling convention shared with the base charter's `patient_pay_after_cap`, not something a real plan delegates); O-12 (the continuation's delivery lead adds `mail_transit_business_days`, a business-day figure, as calendar days of supply — stated so in the rule; no second reading).

### findings

| id | verdict | summary | bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-FACTOR RED (charter half; consequence per world) | Three tiers (`refill_program_lead_tier`, `titration_overlap`, `sync_share_tier`) decide one prescription's quantity from another prescription's enrollment or fill; no pharmacy weighs those records for that quantity | task 0 (refill_program_lead_tier, titration_overlap); task 1 (sync_share_tier) — demonstrated in each task file |
| F-2 | SOURCE-FACTOR RED (charter half; consequence per world) | The plan's mail-service rate is applied to a corrected claim regardless of how that fill was dispensed | task 1 — demonstrated in the task file |
| O-1 | observation | Continuation rule states its dependency twice (eligibility sentence + prerequisite sentence) | task 0 |
| O-2 | observation | Titration compute counts any `rx_fills` row with `fill_reason=dosage_change`; the rule says "a refill" | task 0 (no effect: the only such row is an `rx_refill`) |
| O-3 | observation | Renewal-courtesy compute puts a request started after the approval end (negative lead) in the late tier; the rule's "before" does not cover it | task 0 (no effect: lead +4) |
| O-4 | observation | Corrected rule names the corrected fill two ways; compute implements only "most recent refill settled through insurance" | task 1 (checked per world) |
| O-5 | observation | `bill_continuation_supply_837ca024` docstring describes the drug as "under appeal" | task 0 |
| O-6 | observation | Base sentences with cross-problem orders ground no edge | none |
| O-7 | observation | Continuation reuses `claim_basis emergency_pa_supply` on classes whose `pa_emergency_supply_days` is 0; the base sentence governs only a waiting request | task 0 |
| O-8 | observation | blueprint.yaml's difficulty summary lists "billing" among agent service actions and names appeal and plan removal as the patient's own acts; the cash re-bill is made a patient-owned submission. The KB is rendered from the charter, whose base is silent on the performer, and the owner=user tool is not in the agent's tool list, so no second scored answer arises | task 1 |
| O-9 | observation | `cross_difficulty: refill` names a category no difficulty claims | tasks 0 and 1 |
| O-10, O-11, O-12 | observation | business-reality notes above | tasks 0 and 1 |

## closing_checklist

Written after both reveals (reveal at 2026-09-24T18:22:10Z). The charter-global section above predates every reveal; its sha256 at freeze was 4d62bab2…616a. Its "freeze time" label (18:17Z) was the auditor's own estimate. The file's actual last write before the reveal was 18:19:22Z. Nothing above this heading was changed after the reveal.

**The difficulty does not close.** Both tasks carry SOURCE-FACTOR RED, so the four relationships do not all PASS.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | SOURCE-FACTOR RED (T0-F1, from F-1) | PASS |
| 1 | PASS | PASS | SOURCE-FACTOR RED (T1-F1 from F-1; T1-F2 from F-2) | PASS |

Checklist state:
- Audit files: `0.md` and `1.md` match the two tasks one to one, with `_difficulty.md` alongside. First revision, so there is no older revision to trace. Neither comparison section carries a PASS verdict. ✗
- Coverage and exclusivity: task 0's `charter_scope` is {appeal_decision_window, continuation_supply_days}. Task 1's is {corrected_rebill_patient_pay, cash_rebill_patient_pay}. The two scopes are disjoint and together cover all four extended policies and all four task tools. Each scope spans its whole tree. Every uuid8 was generated independently. ✓
- Trees: each has one prerequisite problem, one value_input edge and one owner=user write (task 0: the appeal; task 1: the cash re-bill). There are no cycles, and the difficulty-wide graph is two disjoint edges. ✓
- Factors:
  - Every computation declares a self-sufficient baseline, whose fall-back numbers are 7, 11, 23.33 and 4.32, all different from gold.
  - Every computation has 4 to 6 factors, including 2 or more parameter factors and 1 method factor.
  - Each task has at least one multi-source factor and one cross-difficulty factor.
  - Every ladder has 3 tiers stated in full, and every factor bears weight against an honest baseline.
  - However, the ladders at F-1 and F-2 hold conditions that this line of business does not weigh, and on these worlds those conditions are met through another prescription or another fill. ✗
- The instantiation-stage gates were not re-run on a final form, because no final form exists while REDs stand. The gate snapshot in the brief (all rc=0) is the latest one. This audit neither ran the gates nor edited any artifact.

## revision_2

### charter_global_frozen (r2)

- Auditor: the same independent erl-task-policy-audit agent that wrote round 1.
- Written before any round-2 task file was revealed. The freeze time is the file mtime recorded at the reveal step in the task files.
- Shared inputs:
  - `coverage.extended.yaml` sha256 `00cf8a46f8bc5a10231eb67502a56868c509b9b9dcb893d019ff8182d6b2fd1b`. It was `397a8e5a…` in r1, so it has changed.
  - `task_tools.py` sha256 `5b5b920bc220d96a3ffa716ffbbbb52a3ff272120541425aa034ac70b3b6da1f`. It was `3ede327d…` in r1, so it has changed.
  - Both hashes match the brief.
  - Because both shared inputs changed, every charter-global section below is **re-derived in full, not carried forward**.
  - Blueprint files are unchanged: every mtime is before round 1 opened, and the base section is still byte-identical to `blueprint/products/coverage.yaml` (`diff` of lines 1–1178 is empty).
- Entry conditions:
  - The coordinator's post-rework gate snapshot shows all seven gates at rc=0.
  - The r2 masked views were re-hashed and match: task0 `a131038e…d656`, task1 `049a3e36…47b9`.
- Masked and unread while this section was written: both round-2 task files.
- contamination_disclosure: I read the round-1 GT, and I know its scored values: 11, standard, 26, 4.32 and 1.52. My round-2 derivations therefore cannot be blind to what the answers were before. What is still independent is the recomputation from the reworked charter and the r2 views, which is recorded in the task files.

### policy_conflict_scan (r2)

Still four extended policies. Targets, `computes` and owners are unchanged. The two value_input edges are unchanged, so the partition {appeal → continuation} and {corrected → cash re-bill} is unchanged. No two extended policies compute the same quantity on the same object. Both `retro_rebill` writers remain distinguishable, because only the corrected claim writes `source_claim_id`.

The continuation's opening sentences changed from "a patient who appeals the denial of a renewal is paid a continuation supply … while the appeal is pending" to "When the plan denies the renewal of a prior authorization it had approved, it also pays a continuation supply of that drug … that carries no patient pay until the denial is finally resolved. A continuation supply is not the emergency supply a waiting request earns and is not limited to pa_emergency_supply_days."

Against base:
- coverage_evt_prior_authorization's emergency-supply sentence is scoped "While a request is waiting". The new sentence says in terms that the continuation is a different supply. There is no conflict, and the r1 reading hazard O-7 is closed.
- The first sentence is the declared `replaced_by`.

New reading note, R2-O1 (observation):
- The eligibility sentence now grants the continuation on any renewal denial, with no mention of an appeal. Beside it stand "The days supply of a continuation supply is fixed only after the prior-authorization ledger carries an appeal filed …" and "When no appeal is on the coverage, the days to a decision due date are 0".
- For a patient who does not appeal, the charter therefore owes a continuation whose days supply it never fixes. The "0 when no appeal" sentence invites a reader to bill without an appeal (15 days on task 0's world).
- The explicit "fixed only after" sentence rules that reading out, so no second defensible answer arises where the customer accepts the hand-over. The no-appeal case is left undefined rather than contradicted.

No other conflict.

### rule_compute_equivalence (r2)

Every binding was swept against its quotation and back.

Changes versus r1:
- **Appeal.** New `appealed_prescription` = "The appealed drug is the prescription the most recent denial on the coverage concerns". Supply left and the continuity-credit count are now filtered to that prescription, and both rule sentences say "for the appealed drug". Equivalent.
  - The `inputs.history` descriptors still list the claim reads without the prescription filter and omit the denial-prescription read. `inputs` is descriptive metadata, not the computation, so this is observation R2-O4.
- **Continuation.**
  - `continued_prescription` is quoted.
  - The refill-program lead is filtered `prescription_id=continued_prescription` on `CFIELD` and on both `CPARAM`s. The rule reads "the continued drug's own active automated refill enrollment … whatever the patient's other prescriptions are enrolled in".
  - Approved supply is now "for the continued drug".
  - The renewal courtesy tests `>= 1 and < 7`, then `>= 7 and < 14`. The rule reads "at least one but fewer than …; … otherwise, including a request started on or after that approval_end_date, no renewal courtesy". This closes r1 O-3.
  - Titration adds `event_type='rx_refill'` and `prescription_id=continued_prescription`, matching "a refill of the continued drug … a dosage change of another prescription adds nothing". This closes r1 O-2.
  - The mail lead is "each counted as one calendar day of supply", which closes r1 O-12.
  - Equivalent.
- **Corrected claim.**
  - New `corrected_source_claim` = "made for the most recent reversal … for a billing correction". `corrected_prescription` and `corrected_fill_number` are read from that reversed claim. The fill is the `rx_refill` of that prescription with that fill number.
  - The rule's two statements, "for the fill the reversed claim paid for" and "the refill of the prescription the reversed claim billed that carries the fill number the reversed claim billed", now name the same fill by construction. This closes r1 O-4.
  - The copay-tier count is "of the same prescription", with the compute filtered.
  - The mail-service rate reads `corrected_fill_release` from the `rx_pickup` row whose `source_fill_id` is the corrected fill. The rule reads "when the corrected fill was released to the patient by home delivery and the patient holds an active Kestrel Mail Delivery plan …; when … released by home delivery under any other active delivery plan …; otherwise, including a fill collected in person, by 1".
  - The baseline rule now carries the two identity sentences, and both are in the rule.
  - Equivalent.
- **Cash re-bill.** `sync_share` is replaced by `class_share`: "A drug the plan lists by handling class earns a class share, read from the re-billed fill's own prescription: … Non-Controlled Maintenance … maintenance_rebill_share; … Non-Controlled Acute … acute_rebill_share; for any other class by 1". The compute is `CFIELD('rx', 'variant_name', prescription_id=cash_fill_prescription)`, and the product formula lists "the class share". Equivalent.

No compute basis is invented and no rule promise is empty. Every factor tier exists in both faces.

### action_binding_and_uuids (r2)

- Tool module: the only change is the `bill_continuation_supply_837ca024` summary line, now "…a drug whose prior authorization renewal the plan denied", no longer "…and is under appeal". This closes r1 O-5.
- Tool bodies are byte-for-byte the same behaviour as r1: one unconditional row per call, no ledger read and no refusal.
- `(target_tool, computes)` pairs are unchanged and each is claimed by exactly one policy.
- uuid8s `f21a07b8`, `837ca024`, `b015fa67`, `483f3c39` are unchanged, independent and frozen.
- No docstring names another tool or orders an action.

### prerequisite_graph (r2)

The two edges, their `policy_source`, `form: state`, `condition`, `resolved_by`, `gate` and `effect` are textually unchanged from r1. Each `policy_source` is still locatable verbatim in its own rule. The gate bindings `days_to_decision` and `rebill_rate` still exist. The graph is still acyclic, and `prerequisite` is filled everywhere. PASS.

### prerequisite_sentences (r2)

Both sentences are unchanged and pass the four-point test as in r1. The single-writer property still holds, because the tool bodies are unchanged:
- `coverage_appeal_filed` is written only by the appeal tool.
- `source_claim_id` is written only by the corrected-claim tool.

The r1 second wording (O-1) is removed. The continuation rule no longer restates the dependency in eligibility words, and the "no appeal → 0" binding sentence is the gate's own value, not a second wording. See R2-O1 for the reading hazard the new eligibility sentence leaves.

The depended-on rules do not restate either sentence. No rule states an undeclared cross-problem order. PASS.

### override_declarations (r2)

- Appeal: unchanged declaration. The new appealed-drug sentences scope inputs and override no base sentence. PASS.
- Continuation: the declared `replaced_by` now reads "…it also pays a continuation supply of that drug … until the denial is finally resolved". It still replaces exactly the base PA-denial sentence. The new "not limited to pa_emergency_supply_days" sentence addresses a base sentence whose trigger ("While a request is waiting") the continuation does not meet, so it is a clarification, not an override. The other six base refs follow as in r1. PASS.
- Corrected claim and cash re-bill: `overwrite: []`. No new sentence governs a quantity base fixes. PASS.

### factor_ladders (r2)

| policy | factors | parameter | method | multi-source | cross_difficulty (declared) |
| --- | --- | --- | --- | --- | --- |
| appeal | 4 | 3 | 1 (filing_anchor) | review_clock_choice | none |
| continuation | 6 | 5 | 1 (continuation_start) | delivery_lead_tier | delivery (delivery_lead_tier), rx (titration_overlap); refill_program_lead_tier now `null` |
| corrected | 6 | 5 | 1 (corrected_supply_basis) | corrected_copay_tier (product AND same-prescription count); mail_service_rate_tier (fill release channel [rx_fills] AND delivery plan [delivery_plans]) | rx, delivery |
| cash re-bill | 6 | 5 | 1 (cash_fill_days_charged) | none | rx (days charged, out-of-pocket, class share, gap) |

Structure checks:
- Every ladder still has exactly three disjoint tiers, stated in the rule and implemented in the `decides` binding.
- Every fall-through equals its baseline, and every baseline equals what `baseline.rule` gives.
- No two tiers share a value: class share 0.9 / 0.95 / 1; mail 0.8 / 0.9 / 1; the rest as in r1.
- Labels are honest.
- No factor now declares `cross_difficulty: refill`, which closes r1 O-9.

Business reality:
- **F-1 (r1): closed at the charter.**
  - The refill-program lead and the titration overlap now read only the continued drug's own enrollment and dosage-change refills, and the rule says so outright.
  - The sync share is gone. Its replacement, class_share_tier, reads the re-billed fill's own prescription class. Lower cost-share for maintenance medication is a treatment plans do publish, so the condition is one the business weighs for that quantity.
  - The acute tier (0.95) and the wording "a drug the plan lists by handling class" describe Kestrel's handling class as a plan list. This is observation R2-O3: an odd attribution, but there is no demonstrable consequence.
- **F-2 (r1): closed at the charter.** The mail-service rate now requires that the corrected fill itself was released by home delivery, and a fill collected in person gets 1.
- Observations carried unchanged, as the reworker's acknowledgement states:
  - O-6: base cross-problem order sentences.
  - O-8: blueprint summary vs the patient-owned cash re-bill.
  - O-10: the late-listing share, and the new-member share.
  - O-11: Kestrel computes plan patient pay.
  - Each was re-checked against the r2 text and still applies as written in r1.

### findings (r2, charter-global)

| id | r2 status | evidence |
| --- | --- | --- |
| F-1 | **closed at the charter** (per-world confirmation in task files) | continuation rule and compute scoped to the continued prescription; sync share removed; class share reads the re-billed fill's own prescription |
| F-2 | **closed at the charter** (per-world confirmation in task 1) | mail rate conditioned on the corrected fill's own home-delivery release |
| O-1 | resolved | dependency no longer restated as eligibility |
| O-2 | resolved | titration filters `event_type='rx_refill'` |
| O-3 | resolved | renewal courtesy "at least one but fewer than …; on or after … none" in both faces |
| O-4 | resolved | the corrected fill is named once, through the reversed claim |
| O-5 | resolved | docstring no longer says "under appeal" |
| O-7 | resolved | explicit "not the emergency supply … not limited to pa_emergency_supply_days" |
| O-9 | resolved | no factor labelled `cross_difficulty: refill` |
| O-12 | resolved | "each counted as one calendar day of supply" |
| O-6, O-8, O-10, O-11 | unchanged, still observations | re-read in r2 text |
| R2-O1 | new observation | eligibility no longer mentions an appeal, so the no-appeal case is left without a fixed days supply |
| R2-O3 | new observation | class share attributed to a "plan list" of Kestrel's handling classes |
| R2-O4 | new observation | `inputs.history` descriptors of the appeal and continuation omit the new prescription filters |
| unrequested edit | verified | the appeal's supply-left and continuity-credit reads are now scoped to the appealed drug. The rule and compute agree. Whether it moves a task's number is checked in task 0 (it does not) |

No new charter-global RED.

### closing_checklist (r2)

This checklist was written after both r2 reveals, which happened at 2026-09-24T18:39:28Z. The r2 charter-global section above was last written at 18:38:26Z, before either reveal. Its text was not changed afterwards.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS (T0-F1 closed) | PASS |
| 1 | PASS | PASS | PASS (T1-F1, T1-F2 closed) | PASS |

- Audit files: `0.md` and `1.md` correspond one-to-one with the tasks, and `_difficulty.md` sits alongside them. Revision r1 is kept untouched, and r2 is appended under `## revision_2`. Both r2 comparisons carry PASS. ✓
- Coverage and exclusivity: the r2 `charter_scope` values are {appeal, continuation} and {corrected, cash re-bill}. They are disjoint and together cover all 4 extended policies and all 4 task tools. The uuid8s are unchanged, independent and frozen. ✓
- Trees: each tree has 1 prerequisite problem, 1 value_input edge and 1 owner=user write, and none has a cycle. The whole graph is two disjoint edges. ✓
- Factors: every computation has a self-sufficient baseline. The fall-back values are 7, 11, 23.33 and 4.32, and none equals gold. Each computation has 4–6 factors, with at least 2 parameter factors and 1 method factor. Each task has a multi-source factor and a cross-difficulty factor (task 0: delivery and rx; task 1: rx and delivery). Every ladder is 3 tiers, stated in full, with distinct outcomes. Every factor bears weight on its own world through records the business weighs for that quantity. F-1 and F-2 are closed. ✓
- Gates: the coordinator's post-rework snapshot is all rc=0, run on this final form (charter `00cf8a46…`, tools `5b5b920b…`). This audit did not re-run them. ✓
- Remaining observations, none a ground for rework: O-6, O-8, O-10, O-11, R2-O1, R2-O3, R2-O4, R2-T0-O1, R2-T0-O2, T0-O1, T0-O4, T1-O1, T1-O4.

**The difficulty passes the source-layer audit at r2.**

## revision_3

### charter_global_frozen (r3)

- Auditor: the same agent. Written before any r3 task file was revealed; the freeze time is the file mtime recorded at reveal in the task files.
- Shared inputs:
  - `coverage.extended.yaml` sha256 `00cf8a46f8bc5a10231eb67502a56868c509b9b9dcb893d019ff8182d6b2fd1b`, **unchanged from r2**.
  - `task_tools.py` sha256 `028164b6936ace3ac5d7d40a850ddba99b7dba59fa1cde5d78bcf4fed3097fd6`, **changed** from r2 (`5b5b920b…`).
  - The views are unchanged: task0 `a131038e…`, task1 `049a3e36…`.
  - The blueprint is unchanged: all mtimes predate round 1.
- Entry: the coordinator's post-fix gate snapshot shows all seven gates at rc=0. It was supplied, not re-run.
- contamination_disclosure: I know the r1 and r2 GT for both tasks (11 standard, 26; 4.32, 1.52). I have not read the rewritten task files, which were modified at 19:32:55Z, after the r2 reveal.

**Carry-forward decision.** The charter is unchanged, so every section that rests on the charter alone is carried forward from `revision_2` by reference, with `00cf8a46…` as grounds:
- policy_conflict_scan
- rule_compute_equivalence
- override_declarations
- factor_ladders
- prerequisite_graph

Because the tool module changed, the tool-dependent checks were re-derived in full:
- action_binding_and_uuids (check 3)
- the single-writer halves of prerequisite_sentences (check 6)
- the "tools do not judge prerequisites" check

### tool module verification (r3)

The reworker's claim is that `datetime` date arithmetic was replaced with integer civil-date arithmetic, with identical behaviour and nothing else touched. It was verified three ways.

1. **Nothing else moved: proved byte-exact.** I took the r3 module and reversed only the described edit:
   - re-inserted `from datetime import date, timedelta`
   - removed the three nested helpers `_days_from_civil`, `_civil_from_days` and `_add_days` from `file_coverage_appeal_f21a07b8`
   - restored `due = (date.fromisoformat(today) + timedelta(days=int(decision_window_days))).isoformat()` in place of `due = _add_days(today, int(decision_window_days))`

   The result hashes to `5b5b920bc220d96a3ffa716ffbbbb52a3ff272120541425aa034ac70b3b6da1f`, which is exactly the r2 module. So every other byte is identical to r2: all four signatures, owners, rw flags, docstrings (Args and Returns included), uuid8s, the `ctx.make_id` inputs, the `ctx.create` field sets and the return dicts.
2. **Identical date results.** The new `_add_days` was extracted and executed, then compared with `date + timedelta` from the standard library:
   - every 7th day from 1901-01-01 to 2099-12-31, with offsets 0, 1, 11, 28, 29, 30, 31, 59, 60, 365, 366 and 1000
   - offsets 0–399 from leap-year boundary dates (2024-02-28/29, 2025-02-28, 2000-02-28, 2100-02-28, 2026-12-31, 1999-12-31)
   - 20,000 random (date, offset) pairs

   All 147,408 cases match, with 0 mismatches. The task-0 case 2026-09-24 + 11 = 2026-10-05 is unchanged. The input is `ctx.now()[:10]`, the same slice as before.
3. **No real clock.** The module no longer contains `datetime`, `timedelta`, `time`, `random` or `uuid`. Time still comes only from `ctx.now()`, and ids only from `ctx.make_id`. The only behavioural difference possible is on malformed input: `date.fromisoformat` would raise, while the integer code would not. `ctx.now()` always supplies a valid ISO date, so this has no effect on any task.

### action_binding_and_uuids (r3, re-derived)

- `(target_tool, computes)` pairs are unchanged, each claimed once.
- The uuid8s `f21a07b8`, `837ca024`, `b015fa67`, `483f3c39` are unchanged, independent and frozen.
- The tool bodies still create one row unconditionally, with no ledger read, eligibility check or refusal. The new helpers compute a date only.
- The docstrings are byte-identical to r2: no tool is named and no action is ordered.
- Single writer: only the appeal tool writes `coverage_appeal_filed`, and only the corrected-claim tool writes `source_claim_id`. Both are unchanged.

PASS.

### findings (r3, charter-global)

- There was no round-2 RED to close.
- The tool change is verified behaviour-identical and confined to the date helper.
- No new defect and no regression. Every observation carried from r2 stands unchanged, because the charter is unchanged.

### closing_checklist (r3)

This checklist was written after both r3 reveals at 2026-09-24T19:34:43Z. The r3 charter-global section above was last written at 19:34:21Z, before those reveals, and its text was not changed afterwards.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- Audit files correspond one-to-one with the tasks. Revisions r1 and r2 are untouched, and r3 is appended in all three files. Both r3 comparisons carry PASS. ✓
- Scope, trees and factors are unchanged from r2. The charter hash `00cf8a46…` is unchanged, the views are unchanged, and every scored value, baseline and sensitivity is identical. The r2 closing checklist items carry forward. ✓
- Tool module `028164b6…`:
  - The change is confined to the appeal tool's date helper. Byte-exact reversal reproduces r2's `5b5b920b…`.
  - Its date results are identical to r2: 147,408 cases with 0 mismatches.
  - No real-clock import remains.
  - The uuid8s are unchanged, and no tool judges a prerequisite. ✓
- Gates: the coordinator's post-fix snapshot shows all seven at rc=0 on this final form. They were supplied, not re-run by this audit. ✓

**The difficulty passes the source-layer audit at r3.**
