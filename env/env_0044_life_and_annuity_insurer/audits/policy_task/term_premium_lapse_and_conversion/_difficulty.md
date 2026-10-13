# Policy-task audit — term_premium_lapse_and_conversion / charter-global

## charter_global_frozen

- Freeze time: 2026-10-08T03:05Z (revision 1; the audit directory was empty, so there is no earlier revision).
- Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit). I did not write these artifacts.
- Frozen inputs (sha256 checked against the brief before reading):
  - `tasks/term_premium_lapse_and_conversion/term.extended.yaml` = `34b9f585813220761a7e65587647255b89a39f45ff85e7230baa2733e9b4dcb7`
  - `tasks/term_premium_lapse_and_conversion/task_tools.py` = `a80f7e8affb39f2c947c0a7e39a61ab48ca1809e996de5510d3f43123ba4b69b`
  - Masked views `/tmp/erl0044_views/term_premium_lapse_and_conversion/task_0.masked.json` = `a77fefe6…327a` and `task_1.masked.json` = `36054642…7426` (each holds only `frozen_time`, `user_scenario`, `initial_state`).
- Fields I was allowed to read: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/term.yaml, products/whole.yaml, products/ul.yaml), the extended charter, task_tools.py, the two masked views, `erlbench/`, and the DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py`, which I used only to apply the restricted-expression semantics (MONTHS, DAYS, COUNT within_months, CFIELD, XSUM, XCOUNT).
- Fields explicitly masked while this section was written: all of `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), plus `worklog.md`. This section is built only from the charter, the schema and the tool contracts. No search touched the tasks directory.
- Entry conditions (Step 0): the brief supplied the gate snapshot (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred to render) and the masked views with their hashes. The entry conditions are complete. I cite the gates and did not re-run them.

### policy_conflict_scan

The charter has eight extended policies:

| policy | target_tool (owner) | computes | prerequisite edges |
|---|---|---|---|
| term_ext_eft_quarterly_conversion | convert_to_quarterly_billing_2bfb08af (agent) | new_modal_premium | [] |
| term_ext_waiver_expiry_repricing | end_expired_waiver_rider_bcdc46e8 (agent) | new_modal_premium | [] |
| term_ext_grace_cure_remittance | remit_grace_premium_a5ae3e41 (user) | remittance_amount | ← eft_quarterly (value_input, mode_factor); ← waiver_expiry (value_input, waiver_charge) |
| term_ext_face_decrease_repricing | apply_face_decrease_78b62126 (agent) | new_modal_premium | ← grace_cure (state_gate, term_face_decrease.decrease_status) |
| term_ext_lapse_installment_billing | bill_back_installment_903386f9 (agent) | billed_amount | [] |
| term_ext_reinstatement_collection | pay_reinstatement_amount_3f8d4404 (user) | reinstatement_amount | ← lapse_installment_billing (value_input, back_premium) |
| term_ext_adb_expiry_repricing | end_expired_adb_rider_b05b3f4a (agent) | new_modal_premium | ← reinstatement_collection (state_gate, term_rider_changes.rider_change_status) |
| term_ext_accelerated_lien | pay_accelerated_advance_7c43a05b (agent) | lien_amount | ← adb_expiry (value_input, premium_set_aside); ← reinstatement_collection (state_gate, acceleration_status) |

- **Overlapping subjects:** `term_rider_removed` is the subject of both waiver_expiry and adb_expiry, but they act on different riders through different tools. `new_modal_premium` is computed by four policies through four different tools. No subject, tool or computed quantity is claimed twice.
- **The shared field `term_holdings.modal_premium`:** eft_quarterly and waiver_expiry each write a whole installment premium into the same field. Each one prices the installment from what the other has or has not yet written. eft_quarterly charges a waiver charge "When the waiver of premium rider is attached on record"; waiver_expiry uses "the modal factor ... of the premium mode on record". No rule orders these two writes against each other. Both are prerequisites of grace_cure, so this pair is a parallel pair with a shared field and no declared order. The cost lands on whichever task's tree contains both (see the findings, F-C1).
- **Time anchors:** every repricing policy reads "the most recent policy anniversary on or before today". Grace, reinstatement, conversion and other windows are inherited from base and not overwritten.
- **Cross-category reads:** whole and ul holdings (status, face_amount) feed band and fee_share in six policies. In accelerated_lien, whole_transactions `whole_tiadb_advance_paid` feeds room and courtesy. Every read is scoped to the customer, matching the rule's "owner's" or "same insured" wording.
- **Scope partition implied by the prerequisite graph:** two connected components of four policies each.
  - {eft_quarterly, waiver_expiry, grace_cure, face_decrease}
  - {lapse_installment_billing, reinstatement_collection, adb_expiry, accelerated_lien}
  
  With M=2 these are disjoint and jointly cover all eight extended policies. Whether each task claims exactly one component is checked against `charter_scope` at reveal time, in the task files.

### rule_compute_equivalence

I swept every compute binding of the eight policies against its `compute_basis` quotation, and every rule sentence back against compute.
- All quantities, windows, filters, tiers, cross reads, caps and roundings have verbatim quotations in `compute_basis`. Every quotation is a sentence of the policy's own `rule`.
- All declared factor ladders appear both as rule prose and as a branch of their `decides` binding. I found no tier that lives in only one face.
- Mismatches and loose ends found:
  1. **grace_cure, internal (F-P2):** sentence 1 says "the overdue billed premium plus **every** installment that has fallen due without being billed plus the returned-item charge". The later sentence says "**One further installment** has fallen due without being billed when a full month or more has passed ... and no installment is counted otherwise". The compute (`newly_due_count: 1 if ... else 0`) implements only the second. Example situation: a monthly-EFT policy issued in CA (grace_period_state_overrides CA: 60), two or more full months past its latest billed due date and still in grace. Sentence 1 counts two unbilled installments; sentence 3 and the compute count one.
  2. **CFIELD reads only the first matching row:** `CFIELD('whole','face_amount', insured_name=..., status='in_force')` returns the first match. The rule says "plus both permanent face amounts", which presumes at most one whole and one ul policy. An owner with two in-force whole policies on the same insured has no defined reading. No world in this difficulty has that shape (observation).
  3. `anniv_age` is written as `MONTHS(DOB,NOW) - MONTHS(issue,NOW) % 12`. It matches "whole years from the insured's date of birth to the most recent policy anniversary on or before today" on both worlds, so I raise no finding.
- Compute invents nothing beyond the rule. The rule promises nothing compute omits, apart from item 1.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy.
- uuid8 tails: 2bfb08af, bcdc46e8, a5ae3e41, 78b62126, 903386f9, 3f8d4404, b05b3f4a, 7c43a05b. They are pairwise distinct, share no prefix or suffix, and are not sequential. That is consistent with independent generation.
- Tool bodies: none of the eight reads status, eligibility, age, window or ledger before writing. remit_grace_premium and pay_reinstatement_amount read `paid_to_date` only to stamp the payment's `premium_due_date`. No tool refuses, errors or hints when a prerequisite is unresolved.
- Docstrings: none names another task tool or a prerequisite. Several use "Afterwards the policy record shows ..." to describe the call's own effect, and the Args say "read from the term policy lookup before the call", which refers to a share read. Neither gives a task-write position in a sequence. I record this as an observation (O-3).

### prerequisite_graph

- `prerequisite` is filled in on all eight policies (`[]` on four).
- Every `problem` names an extended policy id in this file. None names a base policy or itself.
- The graph is acyclic. Topological orders:
  - Component 1: {eft_quarterly, waiver_expiry} (unordered between themselves) → grace_cure → face_decrease.
  - Component 2: lapse_billing → reinstatement → adb_expiry → accelerated_lien. The reinstatement → accelerated_lien edge is implied by the chain and does not change the order.
- Every `policy_source` is verbatim in its own policy's `rule`:
  - grace_cure: "The grace remittance is fixed only after the premium mode on record shows quarterly direct billing for a policy whose bank drafts returned in the last 12 months have reached the returned-draft limit." / "Before the grace remittance is worked out, the waiver of premium rider on record must already be detached from a policy whose insured's anniversary age has reached the waiver rider expiry age."
  - face_decrease: "The installment after the face decrease is not recorded until the policy status on record has moved from the grace period back to in force."
  - reinstatement: "The reinstatement amount is fixed only after the ledger carries a billed installment for every premium due date from the paid-to date at lapse through today."
  - adb_expiry: "The installment after the accidental death rider ends is not set until the policy status on record has moved from lapsed back to in force."
  - accelerated_lien: "Before the lien is worked out, the accidental death rider amount on record must already be zero for an insured whose anniversary age has reached the rider expiry age." / "The advance is paid only once the policy status on record has returned from lapsed to in force."
- All edges are `form: state` and none carries a `fallback_reason`, which is correct.
- `resolved_by` equals the depended-on policy's `target_tool` on every edge.
- `kind`/`gate` check:
  - The value_input gates exist as compute bindings in the blocked policy: mode_factor and waiver_charge in grace_cure, back_premium in reinstatement, premium_set_aside in accelerated_lien.
  - The state_gate gates are real base eligibility ids: term_face_decrease.decrease_status (in_force), term_rider_changes.rider_change_status (in_force/grace_period), term_evt_accelerated_benefit.acceleration_status (in_force).
- Each `condition` matches its sentence's strength. The `condition` fields contain no authoring-viewpoint phrasing.

### prerequisite_sentences

Every one of the 7 sentences passes the four-point test:
- an ordering connective ("only after", "Before", "not ... until", "only once");
- a record-visible state in table words (premium mode quarterly; waiver rider detached; status moved grace→in force; billed installment on the ledger for every due date; status moved lapsed→in force; ADB rider amount zero);
- no tool name, policy id, snake_case token or row id;
- strength equal to the condition (each says "for a policy whose ..." or "for an insured whose ...").

For each state-form edge, exactly one write of the difficulty brings the state about:
- "premium mode ... quarterly": only convert_to_quarterly_billing writes `premium_mode`.
- "waiver ... detached": only end_expired_waiver_rider writes `waiver_of_premium_rider`.
- "moved from the grace period back to in force": only remit_grace_premium, the write of the grace-cure policy whose own rule restores "a policy in its grace period".
- "billed installment for every premium due date": only bill_back_installment creates `term_premium_billed`.
- "moved from lapsed back to in force": only pay_reinstatement_amount, the write of the policy that restores "a lapsed policy".
- "accidental death rider amount ... zero": only end_expired_adb_rider writes `adb_rider_amount`.

Single-reading derivations (sentence + records + depended-on rule → resolving action):
- Mode quarterly → eft_quarterly's own rule: "When a policy's monthly bank-draft privilege ends because its returned bank drafts reach the product's returned-draft limit, Ashgrove converts the policy to quarterly direct billing".
- Rider detached → waiver_expiry: "Ashgrove then detaches the rider".
- Grace → in force → grace_cure: "A policy in its grace period is restored to in force by the owner's grace remittance".
- Billed installment → lapse_billing: "Every installment that would have fallen due while a policy was lapsed is billed on the ledger".
- Lapsed → in force → reinstatement: "A lapsed policy with an approved reinstatement application is reinstated when the owner pays the reinstatement amount".
- ADB zero → adb_expiry: "Ashgrove then removes the rider amount".

Other checks:
- No blocked rule states its dependency a second time, and no depended-on rule restates the sentence.
- No extended rule states a cross-problem order that grounds no edge.
- One base rule states a cross-problem order: term_conversion, "a policy in its grace period is converted only after the overdue premium is paid". No extended policy and no task tree rests on it (observation O-4).

### override_declarations

I checked sentence by sentence against each `base_policy_refs` entry.

- **term_premium_calculation**, cited by the six repricing policies:
  - The face-premium/band sentence, the annual-premium sentence and the rider-charges sentence are declared superseded in all six. Band aggregation, fee size, fee share, rider rates and waiver base therefore lie inside declared overrides.
  - **The installment sentence** "The installment premium is the annual premium times the modal factor of the premium mode (...), rounded to the cent." is declared superseded **only** by eft_quarterly. waiver_expiry and grace_cure follow it (modal factor of the mode on record). The other three replace it without declaring it:
    - lapse_installment_billing: the modal factor "follows the billing frequency shown by the installments billed on the ledger in the 12 months ending today".
    - adb_expiry_repricing: same wording.
    - face_decrease_repricing: "the product's quarterly factor when quarterly is on record, or when monthly bank draft is on record and the returned bank drafts of the last 12 months have reached the product's returned-draft limit".
    
    Example situation: a monthly-EFT policy with eight billed installments in the last 12 months (issued eight months ago). Base gives the monthly factor 0.0875; lapse_billing and adb_expiry give the quarterly factor 0.265. These are **undeclared overrides** (F-P1).
    
    For face_decrease the deviation coincides with base term_evt_returned_eft ("the premium mode is changed to quarterly direct billing effective with the next installment due"), so its second reading needs a record that still shows monthly after the limit is reached.
  - The "standard modal factor ... is the product's annual factor, so the standard installment is the annual premium" sentences (face_decrease, lapse_billing, adb_expiry) also contradict the inherited installment sentence for any non-annual mode. They are baseline sentences, but they are rule sentences and they are not declared (F-P1, same root).
- **term_evt_returned_eft and term_mode_change** (eft_quarterly): the extended version follows base. It uses quarterly direct billing and the EFT-only count. One base sentence is not followed: "monthly EFT may be elected again only after eft_reenroll_wait_months" is not acted on, and it is not needed.
- **term_expiry_and_renewal and term_rider_changes** (waiver_expiry, adb_expiry): followed. The rider ends at the anniversary at the expiry age; rider_change_status is inherited as the gate.
- **term_evt_premium_application** (grace_cure, which cites it in `base_policy_refs` without overwriting it):
  - Base says "A remittance is applied to the oldest billed installment that is still unpaid, one installment per payment record, and the paid-to date then moves forward by one premium-mode period" and "Money left unapplied after every billed installment is paid is ... refunded to the payer as an overpayment when it exceeds [overpayment_refund_threshold]".
  - The grace remittance bundles three things into one payment record: the overdue billed installment, an **unbilled** installment, and a returned-item charge that is not premium.
  - Read against base, everything after the one billed installment is unapplied money above 25.00 that base refunds. Base also does not say where the paid-to date lands when one record pays two installments of different modes.
  - The overwrite names only term_grace_and_lapse's cure sentence. These are undeclared overrides of term_evt_premium_application (F-P3). The cost falls on the grace-cure write's `new_paid_to_date` (see task 0).
- **term_grace_and_lapse:** the cure sentence is declared superseded. The grace length and the last-day count are inherited.
- **term_face_decrease:** followed (status in_force, policy year ≥ 2, one per policy year, minimum face). The recalculation sentence is covered by the term_premium_calculation overrides.
- **term_reinstatement:** the reinstatement-amount sentence is declared superseded in reinstatement_collection. The window, evidence ladder, approval and contestability are inherited. lapse_billing cites term_reinstatement without overwriting it. Its "back installment" stays inside "each billed at the premium in effect", because the premium in effect is the extended calculation it declares.
- **term_evt_accelerated_benefit and term_agg_insured_face_limit** (accelerated_lien): the paid-amount/lien sentence and the elected-amount limit sentence are declared superseded. The agg-limit cap ("may never exceed tiadb_max_amount") is a cap that the extended room respects, so there is no conflict. "Once per policy", in_force and LE ≤ 12 are inherited.
- Disguised forms: no 0/1 multiplier and no dropped base branch. The anonymous intermediate "fee before sharing" (60.00 / 50.00 / product fee) sits inside the declared annual-premium override.

### factor_ladders

Per policy I list each factor (label, decides, bindings) and the structural verdict. Bindings are pairwise disjoint within every policy, and no `decides` is `result`. eft_quarterly's `conversion_method` decides `converted`, which is the result's sole operand (observation O-5).

**term_ext_eft_quarterly_conversion** — 4 factors.
- Factors:
  - size_band P (band; whole/ul faces);
  - fee_share P (owns_whole/owns_ul);
  - waiver_issue_age_rate P (issue_age; 0.14/0.09/0.11);
  - conversion_method M (eft_returns_12m, unauthorized_returns_12m).
- **conversion_method is unreal.** The rule's opening sentence fixes the write's scope: "When a policy's monthly bank-draft privilege ends because its returned bank drafts reach the product's returned-draft limit, Ashgrove converts the policy to quarterly direct billing". Every customer who reaches convert_to_quarterly_billing has therefore reached the limit.
  - The "have reached the returned-draft limit" part of tiers 1 and 2 restates scope.
  - The fall-through "when they have not reached the limit, the policy keeps the installment of the mode on record" can never be taken at this write.
  - The fall-through, which is also the baseline, prices a "converted quarterly installment" at the monthly bank-draft factor. No insurer publishes that as a quarterly installment.
  - Only one dividing condition remains (unauthorized debit or not), so the ladder has two reachable tiers.
- Struck count: 3 factors and no `method` factor, below the bounds (F-F1).

**term_ext_waiver_expiry_repricing** — 4 factors.
- Factors: size_band P, fee_share P, adb_age_rate P (1.08 / 0.84 / product 0.96), waiver_end_method M.
- **waiver_end_method is unreal.** The rule's opening sentence: "The waiver of premium rider ends on the policy anniversary at which the insured's anniversary age reaches the product's waiver rider expiry age; Ashgrove then detaches the rider and sets the installment after the waiver rider ends". Every customer who reaches end_expired_waiver_rider has reached the expiry age.
  - Tier 1's disjunct "the insured's anniversary age has reached the product's waiver rider expiry age" holds for all of them.
  - Tiers 2 and 3 ("that age has not been reached") can never be taken.
  - The baseline "The standard waiver charge of the installment after the waiver rider ends is, while the waiver rider is attached on record, the waiver rate times the face premium" charges a waiver premium in the installment that exists because the rider ended. No insurer publishes that (straw man).
- Struck count: 3 factors and no `method` factor (F-F2).

**term_ext_grace_cure_remittance** — 4 factors.
- fee_share P (cross: whole).
- adb_age_rate P.
- returned_item_rate P: 25.00 for ≥3 / 15.00 for 2 / nothing otherwise. The baseline "nothing" is the fall-through; base has no returned-item charge.
- items_charged M, multi-source: tier 1 holds permanent ∧ ≥1 return; tier 2 holds neither ∧ ≥3; cross: whole.

The tiers are distinct and the conditions are ones a carrier weighs (returned items, other in-force coverage, attained age). Structure passes.

**term_ext_face_decrease_repricing** — 6 factors.
- band_measurement M (requested face + permanent faces; cross: whole).
- size_band P (bindings term_face, band).
- fee_size P: 60.00 below 250,000 / 50.00 at ≥ 1,000,000 / product annual fee.
- fee_share P.
- adb_age_rate P.
- mode_in_force P: quarterly on record ∨ (monthly ∧ limit reached) → quarterly; monthly ∧ below limit → monthly; semiannual; otherwise annual.

Defects:
- (a) **fee_size duplicates a tier on the ART variant.** The Ashgrove Annual Renewable Term's `annual_policy_fee` is 60.00, so the "below 250,000 → 60.00" tier and the fall-through "the product's annual policy fee" select the same value on that variant (F-F3). Level-term variants carry 70.00 and the tiers are distinct there.
- (b) **mode_in_force's tier conditions are the premium-mode field itself.** "quarterly is on record → the product's quarterly factor" reads its tier off the field that names the outcome. Its baseline "the product's annual factor, so the standard installment is the annual premium" contradicts the inherited base installment sentence (F-P1), which for a quarterly record gives exactly the tier value. The factor bears weight only against that straw-man baseline (F-F4). Whether the cost lands depends on the world; see the task files.

**term_ext_lapse_installment_billing** — 4 factors.
- size_band P, fee_share P.
- billing_frequency_mode P: ≥10 / 3–9 / 2 / otherwise → monthly / quarterly / semiannual / annual.
- premium_in_effect M.

Defects:
- **premium_in_effect is unreal.** The opening sentence fixes scope: "Every installment that would have fallen due while a policy was lapsed is billed on the ledger as the back installment billed for reinstatement". The "while the policy is lapsed" part of tiers 1 and 2 holds of every customer at this write, and the fall-through "when the policy is not lapsed, it is the installment premium on record" can never be taken. The two reachable tiers differ only by dropping the accidental death charge addend, which is a number substitution, so the `method` label is doubtful as well (F-F5).
- **billing_frequency_mode** infers the modal factor from a billing count. On any record whose `premium_mode` is consistent with its ledger, the mode field names the same tier, and the inherited base installment sentence gives the tier value (F-F4).

**term_ext_reinstatement_collection** — 5 factors.
- elapsed_rate P: lapse gap ≤31 / 32–180 / longer → 3% / 4.5% / product rate.
- long_standing_concession P: 20+ / 10–19 / otherwise → 1pp / 0.5pp / 0.
- relationship_share P, multi-source (both / one); cross: whole.
- interest_day_anchor M: from the signed date / from the lapse date / from the paid-to date at lapse.
- repeat_reinstatement_charge P: 50 / 25 / 0.

Defect: **elapsed_rate and interest_day_anchor use exactly the same cut points (0–31 / 32–180 / 181+) as base `reinstatement_evidence_ladder`** (none / statement_of_good_health / full_underwriting). The approved application's `evidence_type` field therefore names the tier of both factors. A world whose request carries `evidence_type` lets the tier be read off that stamp (F-F6). The cost depends on the world; see task 1.

**term_ext_adb_expiry_repricing** — 4 factors.
- band_measurement M, fee_share P.
- adb_end_rate P: age reached expiry → nothing; 60–69 → 1.08; otherwise → product 0.96.
- billed_frequency_mode P (same ladder as above).

Defects:
- **adb_end_rate is unreal.** The opening sentence: "The accidental death rider ends on the policy anniversary at which the insured's anniversary age reaches the product's accidental death rider expiry age; Ashgrove then removes the rider amount and sets the installment after the accidental death rider ends". Every customer at end_expired_adb_rider is at the expiry age, so tier 1 always holds and tiers 2 and 3 can never be taken. The baseline (charge the product's ADB rate in the installment after the ADB rider ends) is a straw man (F-F7).
- billed_frequency_mode has the same defect as F-F4.
- Struck count: 2 factors.

**term_ext_accelerated_lien** — 6 factors.
- acceleration_room M, multi-source; cross: whole_transactions.
- lien_charge_method M: LE ≤3 / 4–9 / longer → 0 / discount × LE/12 / discount.
- admin_charge_level P: 0 / 100.00 / product fee.
- whole_advance_courtesy P, multi-source (a whole advance in 12 months ∧ LE band); cross: whole.
- installment_months P: 1 / 3 / 6 / 12 by billed count.
- premium_months_method M: waiver claim / LE ≤ 12 / otherwise → 0 / LE / 12.

Notes:
- premium_months_method's tiers select numbers, so its label is doubtful. Two other `method` factors survive, so the counts hold (O-5).
- installment_months has the same structural weakness as F-F4: the months per installment are the premium mode's months.
- All tiers are reachable. LE qualifies at ≤ 12 under base, so the 10–12 band is reachable.

Counts per component (task-level pairing confirmed at reveal):
- Component 1 (eft_quarterly, waiver_expiry, grace_cure, face_decrease):
  - multi-source factors: fee_share (four policies), items_charged, mode_in_force, band_measurement;
  - cross_difficulty factors (whole): size_band, fee_share, items_charged, band_measurement.
- Component 2 (lapse_billing, reinstatement, adb_expiry, accelerated_lien):
  - multi-source factors: fee_share, relationship_share, acceleration_room, whole_advance_courtesy;
  - cross_difficulty factors (whole): size_band, fee_share, relationship_share, band_measurement, acceleration_room, whole_advance_courtesy.

### findings

- **F-P1 — SOURCE-POLICY RED (charter):** undeclared override of base term_premium_calculation "The installment premium is the annual premium times the modal factor of the premium mode ..." by lapse_installment_billing, adb_expiry_repricing and face_decrease_repricing (ladder and "standard modal factor ... annual" sentences). The second reading is demonstrated above for a monthly policy with eight billed installments. Bears on: task carrying component 2 (lapse_billing, adb_expiry) and task carrying component 1 (face_decrease). Each task file states whether its world produces a different number.
- **F-P2 — SOURCE-POLICY RED (charter):** grace_cure says "every installment that has fallen due without being billed" and also "One further installment ... no installment is counted otherwise". These conflict for a policy two or more months past its latest billed due date while still in grace (CA 60-day grace). Bears on: the component-1 task (demonstrated or not in its file).
- **F-P3 — SOURCE-POLICY RED (charter):** grace_cure's bundled remittance is not declared against term_evt_premium_application. Base says "one installment per payment record, and the paid-to date then moves forward by one premium-mode period", and unapplied money above overpayment_refund_threshold is refunded. The paid-to date after a grace remittance that pays a monthly overdue installment plus a quarterly newly-due installment has no single reading. Bears on: the component-1 task (`new_paid_to_date` of the user write).
- **F-C1 — parallel pair with a shared field and no order (charter fact):** eft_quarterly and waiver_expiry both rewrite `modal_premium`, each prices from the other's on-record state, and no rule orders them. Bears on: the component-1 task (both orders demonstrated there).
- **F-F1 / F-F2 / F-F5 / F-F7 — SOURCE-FACTOR RED (charter structure):** conversion_method, waiver_end_method, premium_in_effect and adb_end_rate each have a tier condition, or a part of one, that holds of every customer reaching the write, and a fall-through that can never be taken at it. The quoted scope sentences above demonstrate this. After striking:
  - eft_quarterly has 3 factors / 0 method;
  - waiver_expiry has 3 / 0 method;
  - lapse_billing has 3 / 0 method (2 if F-F4 also strikes billing_frequency_mode);
  - adb_expiry has 3 (2 with F-F4).
  
  Bears on: component 1 (F-F1, F-F2) and component 2 (F-F5, F-F7).
- **F-F3 — SOURCE-FACTOR RED (charter structure):** fee_size's tiers "below 250,000 → 60.00" and fall-through "product's annual policy fee" both select 60.00 on the Ashgrove Annual Renewable Term. Bears on: the component-1 task only if its policy is ART.
- **F-F4 — structural weakness:** mode_in_force, billing_frequency_mode, billed_frequency_mode and installment_months key their tier to the premium mode. The record's `premium_mode` names the tier outcome, and the inherited base installment sentence gives it. Whether this becomes a red light (stamp agreement / decoration against an honest baseline) is demonstrated per world in the task files.
- **F-F6 — structural weakness:** elapsed_rate and interest_day_anchor share base evidence-ladder cut points, so `evidence_type` on the approved reinstatement request names their tier. Demonstrated per world in the task file.
- **O-1 (observation):** CFIELD's first-row reading against "both permanent face amounts".
- **O-3 (observation):** the docstrings use "Afterwards …" and "read from the term policy lookup before the call". Neither orders task writes.
- **O-4 (observation):** a base cross-problem order (term_conversion) grounds no edge.
- **O-5 (observation):** `conversion_method` decides the result's sole operand. premium_months_method is labelled `method` but selects numbers.
- **O-6 (observation):** the six repricing policies carry divergent ADB-rate ladders. adb_expiry has no "< 45 → 0.84" tier, and the other five charge the product rate at 70+ while base ends the ADB rider at 70. No task world exercises the divergence.

## closing_checklist

Written 2026-10-08T03:12Z, after both task reveals. Nothing above this heading was changed after any reveal.

**The difficulty does NOT close:** not every task passes all four relationships.

| item | status |
|---|---|
| per-task audit files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; `_difficulty.md` alongside; revision 1, no older revisions | ✓ |
| each comparison section carries a PASS | ✗ (task 0: SOURCE-POLICY RED + SOURCE-FACTOR RED; task 1: SOURCE-FACTOR RED) |
| extended policies fully covered; scopes pairwise disjoint | ✓ (task 0 = component 1, task 1 = component 2, per charter_scope) |
| task tools and GT closed; uuid8s independent | ✓ |
| each tree has 1–3 prerequisite problems, ≥ max(n−1,1) value_input edges, a user write, no cycle | ✓ (both: n = 3, 2 value_input, one user write) |
| the whole difficulty graph is a DAG | ✓ |
| every computation has a self-sufficient baseline and 4–6 surviving factors (2 P / 1 M), and every factor bears weight against an honest baseline | ✗ (see below) |
| instantiation gates re-run on the final form | not re-run by me. The brief's snapshot (all green) is the final form audited; no artifact changed during this audit. |

Charter-global findings, with their per-task outcome as demonstrated in the task files:
- **F-P1** (undeclared modal-factor override): RED at charter level; costs nothing in either world.
- **F-P2** (grace "every" vs "one further"): RED at charter level; costs nothing in task 0.
- **F-P3** (bundled grace remittance vs base premium application): **demonstrated in task 0** on `new_paid_to_date`. 2026-07-15 and 2026-09-15 both give a final hash different from gold's 2026-10-15.
- **F-C1** (unordered parallel pair sharing `modal_premium`): no scoring cost. The engine replay shows both orders reach the gold hash. Downgraded to an observation.
  - Related, task 0 only: the two parallel writes' `new_modal_premium` values do not reach the scored state at all, because the root write overwrites `modal_premium`.
  - So all 8 factors of eft_quarterly and waiver_expiry bear no weight on the score (task 0 finding 1).
- **F-F1, F-F2** (unreal conversion_method / waiver_end_method): demonstrated in task 0.
- **F-F5, F-F7** (unreal premium_in_effect / adb_end_rate): demonstrated in task 1.
- **F-F3** (fee_size duplicate tier on ART): no cost (both worlds are Level Term 25).
- **F-F4** (mode-keyed ladders read off `premium_mode`): demonstrated in task 0 (mode_in_force) and task 1 (billing_frequency_mode, billed_frequency_mode, installment_months).
- **F-F6** (evidence_type stamp): demonstrated in task 1.

Per-task verdicts: task0 = SOURCE-POLICY RED + SOURCE-FACTOR RED (problem tree PASS, unique solution PASS); task1 = SOURCE-FACTOR RED (policy PASS, problem tree PASS, unique solution PASS).

## revision_2

### charter_global_frozen (revision 2)

- Freeze: 2026-10-08T07:55Z. Auditor: the same independent auditor. The revision 1 text above is left untouched.
- Inputs (sha256 checked): `term.extended.yaml` = `dc0464dcde1ddd80cb6451f4eb96abefba1f2b97828c1a90556d777e2cc64e0f` (**changed**, so this section is re-derived in full, not carried forward); `task_tools.py` = `a80f7e8a…a4b69b` (unchanged, so action_binding_and_uuids is carried forward by reference to revision 1).
- The base section (lines 1–1306) is still byte-identical to `blueprint/products/term.yaml`.
- Masked while writing this section: the revision 2 tasks/0.json and tasks/1.json beyond the rebuilt masked views (`task_0` 8872c005…d875, `task_1` 7821c94c…6ea3), and worklog.md.
- contamination_disclosure: I carry the revision 1 GT in memory (round-1 gold values, order A, paid-to convention). The rework changed every seeded premium (151.13 → 150.91; 261.40 → 260.07) and most formulas, so no round-1 figure can stand in for a round-2 one. Every figure below was recomputed. Nothing from the revision 2 GT has been seen.
- Gate snapshot supplied (all green, traceability deferred). Entry conditions are complete.

### policy_conflict_scan (r2)

| policy | tool | prerequisite edges (r2) |
|---|---|---|
| eft_quarterly_conversion | convert_to_quarterly_billing | [] |
| waiver_expiry_repricing | end_expired_waiver_rider | **← eft_quarterly (value_input, record_installment)** — new |
| grace_cure_remittance | remit_grace_premium (user) | ← eft_quarterly (vi, mode_factor); ← waiver_expiry (vi, waiver_charge) |
| face_decrease_repricing | apply_face_decrease | ← grace_cure (state_gate, decrease_status); **← waiver_expiry (vi, record_installment)** — new |
| lapse_installment_billing | bill_back_installment | [] |
| reinstatement_collection | pay_reinstatement_amount (user) | ← lapse_billing (vi, back_premium) |
| adb_expiry_repricing | end_expired_adb_rider | ← reinstatement (state_gate) |
| accelerated_lien | pay_accelerated_advance | ← adb_expiry (vi, premium_set_aside); ← reinstatement (state_gate) |

- The two components are unchanged:
  - {eft_quarterly, waiver_expiry, grace_cure, face_decrease}
  - {lapse_billing, reinstatement, adb_expiry, accelerated_lien}
  
  With M=2 they are disjoint and jointly complete.
- The shared field `modal_premium` is now written in a pinned order. conversion → waiver_expiry → face_decrease form a **value chain**: waiver_expiry and face_decrease each take a delta off "the installment premium on record". **Revision 1's F-C1 is closed.**

### rule_compute_equivalence (r2)

- Every `compute_basis` value is a verbatim substring of its policy's rule. Every compute binding has a basis, apart from the `term_face` alias. Every baseline sentence is a rule sentence.
- Factor ladders appear both in rule prose and as branches.
- **F-P2 is closed.** grace_cure now reads "exactly one such installment is then counted, and none is counted otherwise", and its first sentence was rewritten to "when one has fallen due without being billed".
- **N-1 (new, regression), lapse_installment_billing due date.**
  - The rule now reads "Every installment that would have fallen due while a policy was lapsed is billed ... at the premium in effect on its due date, which falls one modal period of the premium mode on record **after the paid-to date on record**". The compute uses `F('paid_to_date')`. Billing does not move the paid-to date (bill_back_installment writes only a ledger row).
  - Example situation: a quarterly policy whose lapse spans two due dates. Reinstatement's prerequisite sentence demands "a billed installment for every premium due date from the paid-to date at lapse through today". The lapse rule gives the same date (paid-to + 3 months) for the second back installment as for the first, so no reading reaches the second due date.
  - Revision 1's wording ("one modal period after the latest billed due date") advanced with each billing; the rework lost that. This is SOURCE-POLICY RED at charter level. Its cost lands only on a world with two or more back installments.
- **N-2 (new), eft_quarterly modal factor.**
  - The rule says "The modal factor for the converted quarterly installment is that of the premium mode on record: ... the product's monthly bank-draft factor for monthly bank draft ..." and then "The converted quarterly installment is the annual premium times the product's quarterly factor".
  - This write applies only to a policy whose monthly bank-draft privilege has just ended, so the mode on record is **always** monthly_eft. The first sentence therefore always names 0.0875 as "the modal factor for the converted quarterly installment"; the second always uses 0.265. The compute evaluates `mode_factor` and never uses it.
  - Revision 2 also dropped the installment-sentence entry from this policy's `overwrite`, so the inherited base sentence ("annual premium times the modal factor of the premium mode") joins the first sentence in supporting the 0.0875 reading.
  - SOURCE-POLICY RED at charter level. The cost is demonstrated in the component-1 task.
- Observation O-7: waiver_expiry's rule still defines a policy fee, an annual premium and the fee concession "of the waiver removal reckoning". None of them feeds its result (record installment − waiver share), so they are dead sentences that give no second answer.

### action_binding_and_uuids (r2)

- Carried forward by reference to revision 1: task_tools.py hash unchanged; each `(target_tool, computes)` pair still claimed once.

### prerequisite_graph (r2)

- Every policy fills `prerequisite`. All problems name extended policies.
- Acyclic. Component 1 is totally ordered: conversion → waiver → grace → face. Component 2: billing → reinstatement → ADB → lien.
- All `policy_source` sentences are verbatim in their own rules. All edges are form `state` with no fallback, and `resolved_by` equals the target tool.
- New value_input gates exist as bindings: `record_installment` in waiver_expiry and in face_decrease.
- Conditions name record fields.

### prerequisite_sentences (r2)

- New edge waiver ← conversion: "The installment after the waiver rider ends is set only after the installment premium on record has been converted to quarterly direct billing for a policy whose returned bank drafts of the last 12 months have reached the returned-draft limit." Connective "only after"; record state (`premium_mode` and `modal_premium`); single writer convert_to_quarterly_billing ✓.
- New edge face ← waiver: "The released premium is taken from the installment on record only after that installment no longer carries the charge of a waiver rider whose insured has passed the rider's expiry anniversary." Single writer end_expired_waiver_rider ("Ashgrove then detaches the rider and sets the installment ... by taking the waiver charge out of the installment premium on record") ✓.
  - Observation O-8: "passed the rider's expiry anniversary" is a hair stricter than the condition "has reached the waiver rider expiry age". They differ only on the anniversary day itself.
- The remaining sentences are unchanged from revision 1 and still pass. No new cross-problem order is stated without an edge.

### override_declarations (r2)

- **F-P1 is closed.**
  - waiver_expiry and face_decrease now declare the base installment sentence superseded (record installment less a share).
  - lapse_billing, adb_expiry and grace_cure use "the modal factor ... of the premium mode on record", which is the base sentence itself.
  - eft_quarterly's quarterly factor matches base term_evt_returned_eft ("the premium mode is changed to quarterly direct billing"). Its own conflicting sentence is N-2.
- **F-P3 is closed.** grace_cure's `overwrite` now names both term_evt_premium_application sentences ("one installment per payment record ...", "Money left unapplied ...") and states the paid-to rule: "the paid-to date moves forward by one modal period of the mode in which each covered installment falls due".
- F-F3's root (fee_size tiers) is fixed: "product's annual policy fee less 10.00 / less 20.00 / product's annual policy fee". On the ART these are 50 / 40 / 60, which are distinct.

### factor_ladders (r2)

| policy | factors (label) | structural verdict |
|---|---|---|
| eft_quarterly | size_band P, fee_share P (xd whole), waiver_issue_age_rate P, waiver_charge_base M | conversion_method removed (**F-F1 closed**). All tiers reachable at this write. 4 factors / 1 method ✓ |
| waiver_expiry | size_band P, adb_age_rate P, waiver_issue_age_rate P, waiver_charge_base M | waiver_end_method removed (**F-F2's cited factor closed**), but **N-3** (below): adb_age_rate is unreal here. 3 surviving ✗ |
| grace_cure | size_band P, fee_concession P, fee_share P (xd), adb_age_rate P, returned_item_rate P, items_charged M (multi-source, xd) | 6 ✓ |
| face_decrease | band_measurement M (xd), size_band P, fee_size P, fee_share P (xd) | mode_in_force removed (**F-F4 closed** for it). 4 ✓ |
| lapse_billing | band_measurement M (xd), size_band P, fee_share P, adb_rate_in_effect P | premium_in_effect and billing_frequency_mode removed (**F-F5, F-F4 closed**). adb_rate_in_effect: due age ≥ expiry / 60–69 / < 45 / otherwise, all reachable for a lapsed policy. 4 ✓ |
| reinstatement | elapsed_rate P (≤15 / 16–90 / longer), long_standing_concession P, relationship_share P (xd), interest_day_anchor M (≤15 / 16–120 / longer), repeat_reinstatement_charge P | Cut points no longer coincide with the evidence ladder (0–31 / 32–180 / 181+). `evidence_type = none` spans rate tiers 1 and 2, so the stamp no longer names the tier (**F-F6 closed**). 5 ✓ |
| adb_expiry | band_measurement M (xd), size_band P, fee_concession P, fee_share P | adb_end_rate removed (**F-F7 closed**); billed_frequency_mode removed (**F-F4 closed**). 4 ✓ |
| accelerated_lien | acceleration_room M (xd), lien_charge_method M, admin_charge_level P, whole_advance_courtesy P (xd), premium_months P, paid_ahead_offset M | installment_months removed (F-F4 closed). **N-4** below: premium_months and paid_ahead_offset are unreal. 4 surviving ✓ (2 P, 2 M) |

- **N-3 — SOURCE-FACTOR RED (new; present but not raised in revision 1, an auditor miss): adb_age_rate in waiver_expiry.**
  - The write's scope sentence: "The waiver of premium rider ends on the policy anniversary at which the insured's anniversary age reaches the product's waiver rider expiry age". `waiver_rider_expiry_age` is 65 on all six variants.
  - So the anniversary age at this write is 65, and the tier "from 60 through 69 → 1.08" holds of every customer who reaches it. The tiers "below 45" and "otherwise" can never be taken.
  - After striking, waiver_expiry keeps 3 factors (size_band, waiver_issue_age_rate, waiver_charge_base), below the 4-factor floor.
- **N-4 — SOURCE-FACTOR RED (accelerated_lien), two factors.**
  - (a) premium_months ("none while an approved waiver of premium claim is on file, the life expectancy in months when it is 12 months or less, and 12 months otherwise"). Base term_evt_accelerated_benefit grants an advance only to an insured "certified ... to have a life expectancy of tiadb_life_expectancy_months or less" (12 on every variant). So "12 months or less" holds of every approved claim, and the "otherwise" tier is unreachable at this write. The same ladder existed in revision 1 as premium_months_method; I noted only its label then (auditor miss).
  - (b) paid_ahead_offset's tier "when the paid-to date is on or before today and the policy is in its grace period" is unreachable. The advance is paid only while status is in_force (base acceleration_status, allowed [in_force]), and the rule's own sentence says "The advance is paid only once the policy status on record has returned from lapsed to in force".
  - Both are struck. The policy keeps 4 (acceleration_room M, lien_charge_method M, admin_charge_level P, whole_advance_courtesy P), within bounds.
- **O-5 is closed in its label part** (premium_months is now a parameter). The ladder defect is N-4(a).

### findings (r2, charter)

- **Closed:** F-P1, F-P2, F-P3, F-C1, F-F1, F-F3, F-F4, F-F5, F-F6, F-F7.
- **F-F2:** the factor it cited is gone, but waiver_expiry still falls below bounds through N-3.
- **Open / new:** N-1 (SOURCE-POLICY, regression, no cost unless two or more back installments), N-2 (SOURCE-POLICY; cost in component 1), N-3 (SOURCE-FACTOR; component 1), N-4 (SOURCE-FACTOR; component 2).
- **Observations:** O-7, O-8; O-1, O-3, O-4, O-6 as in revision 1.

### closing_checklist (revision 2)

Written after both revision 2 reveals (07:53:29Z). The revision 2 charter-global section above was frozen at 07:52:07Z (file mtime); the "07:55Z" written in its header is a drafting estimate.

**The difficulty does NOT close.**

| item | status |
|---|---|
| audit files 1:1 with tasks; revisions 1 and 2 kept, revision 1 text untouched | ✓ |
| every comparison section PASS | ✗ (task 0: SOURCE-POLICY RED (N-2) + SOURCE-FACTOR RED (N-3); task 1: SOURCE-FACTOR RED (no near-miss in ADB expiry; N-4)) |
| coverage, disjoint scopes, tools/GT closed, uuid8 | ✓ (charter_scope: task 0 = component 1, task 1 = component 2) |
| trees: 1–3 prerequisite problems, value_input floor, user write, acyclic, whole-difficulty DAG | ✓ (task 0: n = 3, 4 vi; task 1: n = 3, 2 vi) |
| factors: 4–6 surviving per computation, honest baselines, all bear weight | ✗ (waiver_expiry 3 surviving; ADB expiry no near-miss; accelerated_lien 2 struck factors) |
| GT values equal independent derivation | ✓ (every scored argument in both tasks) |
| gates re-run on the final form | not re-run by me; the brief's revision 2 snapshot is all green |

Round-1 claims, judged:
- **Closed:** F-P1, F-P2, F-P3, F-C1, F-F1, F-F3, F-F4, F-F5, F-F6, F-F7, O-5 (label); 0.md #1–#5; 1.md #1–#5, #7, obs 6.
- **F-F2:** the cited factor was closed, but waiver_expiry still fails its count through N-3.

New or regressed:
- **N-1:** lapse-billing due date anchored on the paid-to date. A regression; no task cost.
- **N-2:** conversion modal-factor contradiction; cost in task 0.
- **N-3:** waiver_expiry adb_age_rate unreal. Revision 1 auditor miss.
- **N-4:** accelerated_lien premium_months (revision 1 auditor miss) and paid_ahead_offset (new) unreal.
- **ADB-expiry near-miss lost** in task 1 (regression).

Per-task r2 verdicts: task0 = SOURCE-POLICY RED + SOURCE-FACTOR RED; task1 = SOURCE-FACTOR RED.

## revision_3

### charter_global_frozen (revision 3)

- Freeze: 2026-10-08T10:20:23Z (captured by the shell at write time). The revision 1 and 2 text above is untouched.
- Inputs: `term.extended.yaml` = `1495d36195936d2bf7c2ce0293276f8292bbbd51c4119ddf86dc6f6f7fcbd12e` (**changed**, re-derived in full); `task_tools.py` unchanged (`a80f7e8a…`, action_binding_and_uuids carried forward). The base section is still byte-identical to products/term.yaml.
- Masked: revision 3 tasks/*.json beyond the views (task_0 view unchanged, `8872c005…`; task_1 view `b63e22b6…`).
- contamination_disclosure: I carry the revision 1 and revision 2 GT in memory. Revision 3 did not change task 0's world or any formula that produces its scored figures, so revision 2 numbers are expected to recur. They were recomputed regardless, and none was copied.

### Re-derivation summary (r3)

- **policy_conflict_scan / prerequisite_graph / prerequisite_sentences:** unchanged in structure from revision 2.
  - Two components; component 1 is totally ordered conversion → waiver → grace → face, component 2 is billing → reinstatement → ADB → lien. Acyclic.
  - All policy_source sentences are verbatim in their own rules, and all edges are form state.
  - face ← waiver now reads "... no longer carries the charge of a waiver rider whose insured's anniversary age has reached the waiver rider expiry age.", which equals the condition's strength. **O-8 is closed.**
- **rule_compute_equivalence:** every compute_basis is a verbatim substring of its rule, and every baseline sentence is a rule sentence.
  - **N-2 is closed.** eft_quarterly no longer carries "The modal factor for the converted quarterly installment is that of the premium mode on record"; its compute has no `mode_factor` binding; its `overwrite` again names the base installment sentence. One reading remains: annual × the quarterly factor.
  - **O-7 is closed.** waiver_expiry's rule no longer defines a fee, concession or annual premium, and its `overwrite` drops the annual-premium entry accordingly.
  - **N-1 is closed in mechanics.** lapse_billing now has `unpaid_billed` = billed − paid + returned (counts), and the due date = paid-to + one modal period × unpaid_billed. After one back bill the next due date advances (task 1 world: 2026-08-01, then 2026-11-01).
  - **N-5 (new) — SOURCE-POLICY RED: the rule text misstates the identity.**
    - It reads: "that due date falls one modal period of the premium mode on record after the latest billed due date, **which is the paid-to date on record advanced by one modal period for every billed installment still unpaid on the ledger**".
    - The paid-to date is the due date of the first unpaid installment, so paid-to + period × (unpaid billed) is the **next** due date, not the latest billed one.
    - Read with "which" attached to its antecedent "the latest billed due date", the sentence gives latest billed = 2026-05-01 + 3 months = 2026-08-01, and so a due date of **2026-11-01**. Read off the ledger (latest billed due 2026-05-01), it gives **2026-08-01**; the compute also gives 2026-08-01.
    - The second reading is weak: 2026-11-01 has not "fallen due" by today, and the ledger shows the true latest billed due date. But the two clauses reach different dates in the same world. The cost is demonstrated in task 1.
- **override_declarations:** F-P1 and F-P3 remain closed. The eft_quarterly installment override is declared again.

### factor_ladders (r3)

| policy | factors | verdict |
|---|---|---|
| eft_quarterly | size_band P, fee_share P, waiver_issue_age_rate P, waiver_charge_base M | 4 ✓ (unchanged) |
| waiver_expiry | **band_measurement M** (xd whole), size_band P, waiver_issue_age_rate P, waiver_charge_base M | adb_age_rate is no longer a factor; the ADB rate stays a compute binding whose 60–69 tier is the scope at this write, which is not a factor defect. **N-3 is closed** (4 factors, 2 P / 2 M). **F-F2 is closed.** |
| grace_cure | unchanged, 6 | ✓ |
| face_decrease | unchanged, 4 | ✓ |
| lapse_billing | unchanged factors, 4 | ✓ |
| reinstatement | unchanged, 5 | ✓ |
| adb_expiry | unchanged, 4 | ✓ |
| accelerated_lien | premium_months P now: waiver claim → none / LE ≤ 6 → 6 / otherwise → LE; paid_ahead_offset M now: paid-ahead covers all → nothing / covers part → subtract / not after today → as is | Every tier is reachable at an in-force write with LE ≤ 12. **N-4(a) and N-4(b) are closed.** 6 ✓ |

### findings (r3, charter)

- **Closed:** N-1 (mechanics), N-2, N-3, N-4(a), N-4(b), O-7, O-8, F-F2.
- **New:** N-5 (SOURCE-POLICY, lapse-billing due-date sentence misstates "latest billed due date"; cost in component 2).
- Observations O-1, O-3, O-4, O-6 as before.

### closing_checklist (revision 3)

Written after both revision 3 reveals (10:20:53Z). The charter section was frozen at 10:20:23Z.

**The difficulty does NOT close.** One open item remains: N-5.

| item | status |
|---|---|
| audit files 1:1; revisions 1–3 kept | ✓ |
| every comparison PASS | ✗ (task 0 PASS on all four; task 1 SOURCE-POLICY RED (N-5), others PASS) |
| coverage, disjoint scopes, tools/GT closed, uuid8 | ✓ |
| trees (n = 3 each; vi floor; user write; acyclic; difficulty DAG) | ✓ |
| factors: 4–6 surviving per computation (≥ 2 P, ≥ 1 M), honest baselines, weight-bearing, near-miss per computation, ≥ 1 multi-source and ≥ 1 cross-difficulty per task | ✓ (conversion 4, waiver 4, grace 6, decrease 4; bill 4, reinstatement 5, ADB 4, lien 6) |
| GT equals the independent derivation | ✓ (both tasks, every scored argument) |
| gates on the final form | not re-run by me; the brief's revision 3 snapshot is all green |

Revision 2 claims judged:
- **Closed:** N-1 (mechanics), N-2, N-3, N-4(a), N-4(b), O-7, O-8, F-F2.
- **New:** N-5 (lapse-billing "latest billed due date" identity off by one period; GT tracing contradicts the identity it quotes).

Per-task r3 verdicts: task0 = PASS (all four relationships); task1 = SOURCE-POLICY RED (N-5).

## revision_4

### charter_global_frozen (revision 4)

- Freeze: 2026-10-08T12:31:40Z (shell clock). Earlier revisions are untouched.
- Inputs: `term.extended.yaml` = `e9d6a066326b0e33886b8faa6a0958ddb84d82e163d9da9ed8d594082e285a69` (changed); `task_tools.py` unchanged (`a80f7e8a…`). Base section byte-identical to products/term.yaml. Both masked views are unchanged from revision 3 (`8872c005…`, `b63e22b6…`).
- contamination_disclosure: I carry the revision 1–3 GT. Everything here was re-derived from the revision 4 charter.
- Re-derivation method: I parsed every policy again and checked, by script, the following:
  - every compute_basis sentence appears verbatim in its rule;
  - every baseline sentence is a rule sentence;
  - factor ids and labels;
  - prerequisite edges.
  
  I also read each rule sentence by sentence against the revision 3 reading, and re-ran every computation and every factor substitution on both worlds.
  - Seven policies: structure, sentence list, factors, prerequisites and every computed figure are identical to revision 3.
  - lapse_installment_billing: only its first sentence changed.
- **N-5 is closed.** The sentence now reads: "that due date is the paid-to date on record advanced by one modal period of the premium mode on record for every billed installment still unpaid on the ledger (the billed installments less the remittances applied plus the payments returned), which is the due date one modal period after the latest billed due date."
  - The expression now defines the **due date** itself, and the appositive correctly calls it one period after the latest billed due date.
  - Task 1 world: 2026-05-01 + 3 months × 1 = 2026-08-01, and one period after the latest billed 2026-05-01 = 2026-08-01. Both clauses agree, and they match compute (due = paid-to + mode_months × unpaid_billed).
  - After one back bill the next due date advances to 2026-11-01. There is no regression of N-1.
- Observation O-10: `compute_basis.due_age` quotes two non-adjacent rule sentences joined together (the due-date sentence and "The insured's age for the due date ..."). Each is verbatim in the rule, so no rule/compute gap results.
- All other charter-global sections (conflict scan, uuid8s, prerequisite graph and sentences, override declarations, factor ladders) carry their revision 3 conclusions unchanged. No new defect.

### closing_checklist (revision 4)

Written after both revision 4 reveals (12:31:44Z). The charter section was frozen at 12:31:40Z.

**The difficulty closes at the source layer.**

| item | status |
|---|---|
| audit files 1:1 with tasks; revisions 1–4 kept and untouched; every revision 4 comparison PASS | ✓ |
| eight extended policies fully covered; task scopes pairwise disjoint (task 0 = {eft_quarterly, waiver_expiry, grace_cure, face_decrease}; task 1 = {lapse_billing, reinstatement, adb_expiry, accelerated_lien}); tools and GT closed; uuid8s independent | ✓ |
| trees: task 0 n = 3 with 4 value_input edges, task 1 n = 3 with 2; each has a user write (remit_grace_premium / pay_reinstatement_amount); acyclic; the whole-difficulty graph is a DAG; every edge unmet at the opening and load-bearing | ✓ |
| computations: self-sufficient baselines; 4–6 surviving factors with ≥ 2 P and ≥ 1 M (4/4/6/4 and 4/5/4/6); all bear weight; all-baseline numbers definite and different from gold; a near-miss per computation; multi-source and cross-difficulty (whole) factors in each task | ✓ |
| GT equals the independent derivation on every scored argument (both tasks) | ✓ |
| instantiation gates on the final form | not re-run by me; the brief's revision 4 snapshot (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING OK, SCOPE OK, CACHE-DIFF INFO; traceability deferred to render) is all green |

Remaining observations, none of them grounds for rework:
- O-1: CFIELD reads only the first matching row.
- O-3: docstring "Afterwards …" / "before the call".
- O-4: base conversion order grounds no edge.
- O-6: ADB-rate ladders differ across policies.
- O-10: due_age basis quotes two non-adjacent sentences.
- Task 0: the seeded 150.91 is not reproduced by the formula.

Per-task revision 4 verdicts: task0 = PASS; task1 = PASS.
