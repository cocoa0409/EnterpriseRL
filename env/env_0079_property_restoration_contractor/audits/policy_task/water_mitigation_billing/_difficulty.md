# Policy-task audit — water_mitigation_billing / charter-global

## revision_1

## charter_global_frozen
- freeze time: 2026-10-23T21:10Z; auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiator.
- sha256 `water.extended.yaml` = 15d11e84791d02fde36727fabe369b483f9ff0e9095ac7fc819d1b21ac2afecd; `task_tools.py` = 8ab9323cfbe5752b6b6e1915d544704a1ee890c4afc2970bc2d7a60d5b9adbb4 (both equal the coordinator snapshot `.audit_views/policy/water_mitigation_billing/snapshot_r1.txt`).
- Read for this section: blueprint.yaml (difficulty entry), db_schema.json, share_tools.py, products/water.yaml and, for the cross-category reads/E9, products/claims.yaml, fire.yaml, account.yaml (rules + variants); water.extended.yaml; task_tools.py; audits/render_source/XF_recipe.md and identifier_bands.md; the compute DSL semantics in skills/erl-task-instantiate/scripts/check_compute.py.
- Masked / unread when this section was written: every task JSON under tasks/water_mitigation_billing/tasks/, plan.md, worklog.md, and every masked key of the views (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*). Nothing here comes from a revealed GT.
- Entry conditions (Step 0): gate snapshot present with actual output lines; all 7 instantiation gates green (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK); check_traceability deferred until docs exist (coordinator note); masked-view hashes 0.json a5e0b773…e84268f and 1.json eecf6a66…ee1933ee1 recomputed and equal. Input complete.
- Base copy: `diff` of extended lines 1-1823 against blueprint/products/water.yaml is empty, so the base section is verbatim.
- Scratch probes live in /tmp/erl0079_audit_wmb/ (recompute.py, probes.py). They use the DSL evaluator from check_compute.py on copies of the masked worlds.

### policy_conflict_scan
Extended policies (5), each with its target tool, trigger and status gate:
| policy | target_tool (owner) | subject / computes | status gate in rule |
|---|---|---|---|
| water_ext_tearout_debris | book_tearout_debris_a8b773d4 (agent) | mitigation_service_charge / amount (charge_code debris_haul) | authorized, drying, drying_complete |
| water_ext_tearout_antimicrobial | book_tearout_antimicrobial_173ee43e (agent) | mitigation_service_charge / amount (antimicrobial) | authorized, drying, drying_complete + antimicrobial_required tier |
| water_ext_drying_deposit | pay_drying_deposit_ee9a2909 (user) | customer_payment / amount | authorized, self_pay only |
| water_ext_final_hepa_vacuum | book_final_hepa_eb899e1c (agent) | mitigation_service_charge / amount (hepa_vacuum) | drying_complete |
| water_ext_insured_share | pay_insured_share_cc172b06 (user) | customer_payment / amount | not closed, insurance_claim job linked to a claim file |

- Overlapping subjects. The three charge policies share `water_mitigation_service_charge` but bind disjoint charge codes, and each one's `replaced_by` excludes itself and both siblings by name. The two payment policies bind disjoint funding sources (self_pay against insurance_claim) and different status windows. No two policies give one quantity two values.
- Triggers and time anchors. Every policy reads its dates from the job record: loss_date, opened_date, the latest flood_cut service_date, drying_complete_date, and NOW for the fire due-date lag. The policies agree with one another.
- Cross-category reads: deposit reads fire (`CFIELD('fire', balance_due|payment_due_date, status='invoiced')`); share reads claims (`CFIELD('claims', variant_name|ordinance_law_limit, claim_file_id=F('claim_file_id'))`). Both reads are keyed by exact values. A conflict between the share and the claims charter's writeoff rule is recorded as finding **C-01**.
- Terminal states: each write adds one line or one payment; no policy changes job status.
- Scope: the claimed categories/events (water; mitigation_service_charge, customer_payment) are inside the blueprint claim. Exclusivity and completeness of the two tasks' scopes can only be judged against charter_scope after the reveal. Per-task trees derived blind are task 0 = {deposit, debris, antimicrobial} and task 1 = {share, final HEPA}. They are disjoint and together cover all 5 policies.

### rule_compute_equivalence
- Mechanical sweep (scratch script). Every `compute_basis` quote is verbatim in its own rule (B6), and every `baseline.rule` sentence is verbatim in the rule. Every overwrite `superseded_clause` is verbatim in the cited base rule, and every `replaced_by` is verbatim in the extended rule. Every prerequisite `policy_source` is verbatim in the blocked rule.
- Every binding was checked by hand against its quote: windows (none; all life-of-job aggregates), filters (exact charge_code / event_type), tiers, cross reads, grouping, caps and floors, rounding (RND(x+1e-9,2) wherever the rule says half up; the residue is DSL-KNOWN). Four places disagree in producible worlds. They are recorded as **C-05** (debris baseboard-only world; share negative balance; HEPA zero-square-foot world) and **C-07** (per-day against aggregate equipment coverage).
- Every factor ladder tier appears as a rule sentence and as a branch of its `decides` binding, with one exception. In lgr_capacity_block the fall-through "every billed LGR unit-day is covered" is not a branch of `dehu_block_sqft` (that branch yields the number 0). It is implemented in the plain binding `covered_lgr_unit_days` (`… if dehu_block_sqft > 0 else lgr_unit_days`). Recorded with **C-04**.
- Absent-record outcomes (B1): fire absent gives `or 0` and the rule says "including a customer with no invoiced fire and smoke job … 1"; claims O&L absent gives `or 0`. More than one invoiced fire job is a stated referral (accepted route). LATEST flood_cut absent gives None and the window multiplier falls to 1, as the rule's "in any other case" says.
- Grouping (A9) sentences reviewed: antimicrobial "the treated floor plus the treated wall and ceiling area, multiplied by the coverage factor"; HEPA "the vacuumed floor plus the vacuumed wall, contents and plate areas, multiplied by every pass factor"; share "the unit-days billed above the placement count times the number of air mover lines". In each, the scope sentences fix the reading: coverage applies to "material that stood wet", pass factors "apply to the job", and "(U−C)×L" is dimensionally absurd. Recorded as observation O-03, not RED.

### action_binding_and_uuids
- Each `(target_tool, computes)` pair is claimed by exactly one policy. Every tool body performs only a format check, a single `ctx.create` and a balance `ctx.update` in its own body (D4). No tool checks a business precondition or a prerequisite. The three charge tools reject non-positive amounts, which matters for C-05(c).
- The uuid8s a8b773d4, 173ee43e, ee9a2909, eb899e1c and cc172b06 share no prefix, no sequence and no tail pattern, so they read as independently generated.
- Docstrings contain no example values (D1) and no composed arguments (D3). They name no other write tool and state no position of the write among the business writes. The phrases "read from the water mitigation job lookup before the call" and "already rounded … before the call" describe where an argument comes from, not where the write sits in the sequence. Observation O-05.
- Forbidden tokens (D5): none (Decimal helper as a class static method; `ctx.now()`).

### prerequisite_graph
| blocked policy | problem | kind / gate | form | resolved_by | acyclic | verdict |
|---|---|---|---|---|---|---|
| water_ext_drying_deposit | water_ext_tearout_debris | value_input / charges_posted (binding exists) | state | book_tearout_debris_a8b773d4 (= debris target_tool) | yes | PASS |
| water_ext_drying_deposit | water_ext_tearout_antimicrobial | value_input / charges_posted | state | book_tearout_antimicrobial_173ee43e | yes | PASS |
| water_ext_insured_share | water_ext_final_hepa_vacuum | value_input / sh_hepa_sqft (binding exists) | state | book_final_hepa_eb899e1c | yes | condition narrower than sentence: C-06 |
- Debris, antimicrobial and HEPA declare `prerequisite: []`. Every `problem` names an extended policy of this file. No edge is a self-edge or points at a base policy. No edge carries a `fallback_reason` (all are state form). No authoring-viewpoint phrasing appears.

### prerequisite_sentences
- D1 (deposit to debris): "On a job carrying pad removal, carpet removal or flood cut lines, the amount collected before drying equipment is set is fixed only after the job carries a debris haul-off line."
  - Four-point test: the connective is "only after"; the state is record-visible (a water_charges line, charge_code debris_haul, visible through find_water_charges); no tool, policy id or row id is named; its scope matches the condition.
  - Exactly one write of this difficulty creates a debris_haul line: book_tearout_debris (no share tool writes). Derivation: the reader finds the line missing, finds the rule whose subject is "a job's tear-out debris … billed as one debris haul-off line", and books it.
  - The debris rule does not restate the sentence. PASS.
- D2 (deposit to antimicrobial): "On a tier that requires antimicrobial treatment, the amount collected … is not worked out until the job carries an antimicrobial line." Same tests pass: "not … until"; only book_tearout_antimicrobial writes an antimicrobial line. PASS.
- S1 (share to HEPA): "The insured's share of a job whose drying is complete and that carries pad removal, carpet removal or flood cut lines is fixed only after the job carries a HEPA vacuuming line." The connective, the state and the single resolver pass. The sentence's scope ("whose drying is complete") is broader than the declared condition ("A job in drying_complete status") and broader than the resolver's own gate ("The job must be in drying_complete status when the final HEPA vacuuming line is charged"). Finding **C-06**.
- No rule states an undeclared cross-problem order. No base sentence grounds an edge.

### override_declarations
Each base sentence of each `base_policy_refs` entry was given a conclusion:
- **debris, antimicrobial, HEPA → water_evt_mitigation_services.**
  - s1 (status) is carried verbatim. HEPA narrows it to drying_complete, which is a stricter necessary condition and not a conflict.
  - s2 (tier unit rate × quantity) is overwritten and declared. Each `replaced_by` keeps every other line at base pricing and excludes its own line and the two sibling lines by name, so C2 holds.
  - s3 (mapping/imaging once) and s5-s8 (carpet, pad, labor multiplier) are untouched.
  - s4: antimicrobial carries "antimicrobial is billed only on tiers where antimicrobial treatment is required" verbatim.
  - s9 (half-up rounding) is carried.
  - The anonymous-intermediate, 0/1-multiplier and dropped-branch forms were checked; none found.
- **debris, antimicrobial, HEPA → water_regulated_materials.** Billability of lead-safe setup and asbestos sampling is untouched; the extended rules only read those lines. Observation O-04 covers the debris trim tiers hauling away baseboard that the base line schema prices as "Baseboard detach (and bag for reset)".
- **deposit → water_authorization.** s3 (deposit ≥ tier self-pay deposit) is overwritten and declared, and the replacement covers every self-pay job. s4 ("Insurance-funded jobs require no deposit…") is restated verbatim. s1, s2 and s5 are consistent.
- **deposit → water_evt_customer_payment.** s2 (tenders) is overwritten and declared: the deposit excludes credit card. The surcharge and credit-balance sentences are consistent.
- **deposit → water_evt_equipment_days, water_tier_assignment.** The estimate's cap±1 days are an estimate and never a billing quantity, so there is no conflict. The funding source is read as base defines it.
- **share (overwrite: []) → customer_payment, insurance_payment, mitigation_services, tier_assignment, same_loss_job.** Sentence by sentence, no base sentence of the water charter yields a different scored share. The cross-charter conflict is with claims_evt_writeoff (C-01), which an extended overwrite cannot retire (E9).
- Result: no undeclared override within the water base.

### factor_ladders
Labels and counts (P = parameter, M = method; MS = multi-source, a conjunction over distinct records in every non-fall-through tier; XD = cross_difficulty):
| policy | factors (label) | P / M | MS | XD |
|---|---|---|---|---|
| debris | wet_flooring_load P; class_cut_height P (MS); trim_disposal M; carry_out_access P (MS); dispatch_haul_window P (MS); sealed_bagging P (MS) | 5/1 | 4 | 0 |
| antimicrobial | class_wetted_surfaces M; exposed_subfloor M; stood_wet_coverage P; regulated_wet_wipe P (MS) | 2/2 | 1 | 0 |
| deposit | iicrc_air_mover_plan M; iicrc_dehumidifier_grade P (MS); standing_water_days P; tearout_dust_scrubbers P (MS); past_due_fire_credit P (XD fire); shared_structure_chamber P | 5/1 | 2 | 1 (fire) |
| HEPA | cut_cavity_vacuum P (MS); moved_contents_vacuum P (MS); regulated_dust_passes P (MS); lifted_carpet_back M; bottom_plate_strip P (MS); silt_residue_pass P | 5/1 | 4 | 0 |
| share | ordinance_law_code_work M (XD claims, MS); emergency_premium_split P (MS); air_mover_placement_cap M; lgr_capacity_block P (MS); hepa_stripped_floor_cover M (MS); contents_room_allowance P (MS) | 3/3 | 5 | 1 (claims) |

Every ladder has 3 tiers including a fall-through, and every fall-through equals its factor's `baseline`. Each factor's binding set is disjoint from every other factor's, and no `decides` is `result`. A1 factor-reads table: every factor reads only its own bindings plus plain or baseline bindings (area, floor_movers, standard_scrubbers, standard_floor, am_unit_days, lgr_unit_days). None reads another factor's binding, directly or transitively.

**All-pairs method-tier table (A7).** The distinguishing input is named for each pair. Aggregates of one field count as one input whatever their filter.
| method factor | pair | shapes | verdict |
|---|---|---|---|
| trim_disposal | T1/T2 | ceil(run/150) as its own term vs run/120 unrounded | PASS (adds an operation) |
| trim_disposal | T1/F, T2/F | term vs 0 (not 0 across its domain) | PASS |
| class_wetted_surfaces | T1/T2 | run×8 + F(affected_area) vs run×2 | PASS (adds input F(affected_area)) |
| class_wetted_surfaces | T1/F, T2/F | vs 0 | PASS |
| exposed_subfloor | T1/T2 | SUM(quantity, pad_removal) vs SUM(quantity, carpet_removal) | **FAIL**: same field, filter swap (C-03) |
| exposed_subfloor | T1/F, T2/F | SUM(quantity, …) vs F(affected_area_sqft) | PASS |
| iicrc_air_mover_plan | T1/T2 | ⌈a/60⌉+⌈r/14⌉+⌈a/125⌉ vs ⌈a/60⌉+⌈r/14⌉ | PASS (extra separately rounded term) |
| iicrc_air_mover_plan | T2/F | adds input r (baseboard run) | PASS |
| lifted_carpet_back | T1/F | S(pad)+S(detach) vs S(pad)+S(carpet_removal) | **FAIL**: identical combination, filter swap (C-03) |
| lifted_carpet_back | T2/F | S(pad) vs S(pad)+S(carpet_removal) | **FAIL**: same field, filter difference only (C-03) |
| lifted_carpet_back | T1/T2 | S(pad)+S(detach) vs S(pad) | **FAIL**: same field |
| ordinance_law_code_work | T1/T2 | T (when L=0) vs T−L | **FAIL** semantically: T1 is T2's method at L=0, and F is the same method floored at 0 (C-02) |
| air_mover_placement_cap | T1/T2, T2/F | as in iicrc_air_mover_plan; F = billed unit-days | PASS |
| hepa_stripped_floor_cover | T1/T2 | max(0,H−P) vs max(0,H−P−4C) | PASS (C, flood-cut feet, enters only T2; on a T1 world T2's method gives a different number) |
| hepa_stripped_floor_cover | T1/F, T2/F | vs 0 | PASS |

**Defining-sentence ownership (A3).** One sentence is owned by the wrong place. The debris baseline rule defines "the baseboard run is the total linear feet on its baseboard removal lines", but only trim_disposal uses that quantity (`trim_lf` is a trim_disposal binding). Finding C-08. Every other baseline sentence defines a plain binding or a fall-through value.

**Ladder reality (E1).** Every tier outcome is distinct within its ladder except C-02. No condition holds of every customer who reaches the write. Most levers are recognisable restoration practice: IICRC class wall/ceiling area and air-mover placement (1 per 50-70 sq ft floor, 1 per 10-16 lf wall, 1 per 100-150 sq ft ceiling), desiccant for class 4, XL LGR for class 3, cat-3 sealed bagging, long-carry and after-hours haul, RRP and asbestos handling, deposit credit-risk uplift. The share ladders emergency_premium_split and contents_room_allowance give outcomes per billing arrangement that the frozen claims charter forbids for Carrier Program and AOB files (C-01). Weaker but not RED: billing a 1.5× or 1.25× "coverage" on square feet, the 1.1 asbestos-sampling handling uplift before results, and the shared_structure multiplier. Observation O-02.

**Cross-difficulty (XD).** past_due_fire_credit reads the fire category. No difficulty of this blueprint claims fire (the 5 difficulties claim water, mold, rebuild, contents and claims). Observation O-01; only the coordinator can rule on it.

### findings
- **C-01 SOURCE-POLICY RED (cross-charter conflict, E9/E1): water_ext_insured_share bills the insured, on Carrier Program and AOB files, for amounts the frozen claims charter says are never billed to the customer.**
  - Symptom: the share rule says "on a Carrier Program Claim Billing file with a premium above zero the whole premium is a non-covered amount; on a Direction to Pay …, Assignment of Benefits … or Commercial Large Loss … file … 40 percent of the premium is a non-covered amount". It sets room allowances for "Assignment of Benefits … and 3 rooms on a Carrier Program … file". Its air-mover, LGR and HEPA caps apply on every arrangement. All of it is collected from the insured as "the insured's own payment".
  - claims_evt_writeoff (frozen base, claims.yaml) says: "program_price_adjustment applies only on Carrier Program Claim Billing, where the carrier's program pricing review is final and the difference is never billed to the insured. carrier_denied_line records a line the carrier declined after approval; … on Assignment of Benefits and Carrier Program files it is never billed to the customer". Claims variants carry `denied_line_billable_to_customer: false` and `program_price_writeoff_allowed: true` on Carrier Program, and `denied_line_billable_to_customer: false` on AOB.
  - Root cause: the share's arrangement ladders run opposite to the claims charter's billability. Program and AOB carry the largest insured burden; Homeowner Direct Pay and Public Adjuster, where denied lines are billable, carry none. An extended overwrite cannot retire another charter's sentence.
  - Demonstrated consequence: on a producible Carrier Program job with an after_hours dispatch (Gray Standard: premium 295.65 − 219.00 = 76.65), the water rule puts 76.65 in the insured's share. The claims rule says that difference is never billed to the insured, giving 0.00 for that component. That is two defensible shares.
  - Affected: water.extended.yaml water_ext_insured_share rule and compute (premium_share, covered_rooms, covered_am_unit_days, covered_lgr_unit_days, hepa_outside_sqft); factors emergency_premium_split and contents_room_allowance.
  - Bears on: task 1 is a Direction to Pay file, where denied lines are billable. The component conflict is not engaged there; task 1's own coverage contradiction is separate (see 1.md).
- **C-02 SOURCE-FACTOR RED (unreal ladder: two tiers, in fact all three, select the same method): ordinance_law_code_work.**
  - Ladder: T1 "total above zero and limit zero → whole total"; T2 "limit above zero but below total → total less limit"; F "otherwise → nothing".
  - Applying T2's method on any T1 world gives total − 0 = total, which is T1's outcome. On any F world (limit ≥ total, or total = 0), max(0, total − limit) = 0, which is F's outcome. The ladder is one min/max-of-bounds computation, max(0, T − L), written as three tiers (XF A6: "derive one cap").
  - Bears on: task 1, where T1 is taken: 770.00 under T1 and 770.00 under T2's method. Labelled `method`; it is not a distinct method.
- **C-03 SOURCE-FACTOR RED (mislabelled method, XF A7): exposed_subfloor (antimicrobial) and lifted_carpet_back (final HEPA).**
  - exposed_subfloor: T1 `pad_sqft` vs T2 `carpet_out_sqft` is a filter swap on SUM(water_charges.quantity).
  - lifted_carpet_back: T1 `hv_pad_sqft + hv_detach_sqft`, T2 `hv_pad_sqft` and F `hv_pad_sqft + hv_carpet_out_sqft` are all combinations of SUM(water_charges.quantity) differing only by filter. Every pair fails.
  - Consequence for the counts, counting only factors that pass: HEPA has 0 honest `method` factors (floor is 1), and antimicrobial has 3 factors (floor is 4).
  - Bears on: task 0 (antimicrobial) and task 1 (HEPA).
- **C-04 SOURCE-FACTOR RED (mislabelled parameter): lgr_capacity_block.**
  - Labelled `parameter`. T1 and T2 put a number (400 or 500 sq ft) into ⌈area/block⌉×lines. The fall-through "0 (no cap: every billed LGR unit-day covered)" replaces the algorithm: covered = billed.
  - That branch lives outside the `decides` binding, in the plain `covered_lgr_unit_days`. Read as a value of `dehu_block_sqft`, the 0 is a division by zero.
  - The sibling air_mover_placement_cap, which has the same structure, is labelled `method`.
  - Bears on: task 1. It does not change task 1's counts (share keeps 4 factors and 2 parameters after the strikes).
- **C-05 SOURCE-POLICY RED (rule ≠ compute in producible worlds, B1/E6).** Three members:
  - (a) Debris. The rule says "a job that … carries no pad removal, carpet removal or flood cut line, is billed no tear-out debris line". Compute returns 0 only if `prior_debris_lines > 0 or loads <= 0`, and `loads` includes `trim_load_term`. Probe P1: a pre-1978 job with 104 lf baseboard_removal and no pad, carpet or flood-cut line gives result 214.00 against the rule's "no line". The same holds for a 1995 category_3 job (P1b, 214.00).
  - (b) Share. The rule says "never more than the job's balance due; when it is zero or less nothing is paid". Compute is `MN(F('balance_due'), MX(0, …))`. Probe P3: with balance_due −120.00 compute returns −120.00, against the rule's nothing paid; the tool rejects a non-positive amount.
  - (c) HEPA. The rule bills "one final HEPA vacuuming line in square feet" on any job carrying a flood cut line, with no zero exemption. Probe P2: a category_1 / class_1 job with only flood-cut lines gives hepa_sqft 0.00 and result 0.00, and the tool rejects 0. On such an insurance job, S1 waits for a HEPA line that can never be booked (E6/E7).
  - Bears on: none of the two task worlds directly. All three are charter defects.
- **C-06 SOURCE-POLICY RED (check 6/7 + E7): the share's prerequisite sentence is broader than its condition and its resolver.**
  - The sentence covers "a job whose drying is complete", which includes an `invoiced` job (drying_complete_date and drying_outcome filled). The condition says "A job in drying_complete status". The resolver's rule says "The job must be in drying_complete status when the final HEPA vacuuming line is charged".
  - Consequence: on an invoiced insurance job that carries pad or flood-cut lines and no HEPA line, the sentence holds the share until a HEPA line exists, but no policy can book one. The share is never fixed under the sentence; under the condition it is computed at once. Two readings.
  - Bears on: task 1 is drying_complete, so both readings coincide there. Charter defect.
- **C-07 SOURCE-POLICY RED (two readings of the equipment coverage rule): air movers and LGR.**
  - The share rule says "Air movers are covered up to the IICRC placement count for each billed day" and "LGR dehumidifiers are covered up to one unit for each block … per billed day", which is a per-day cap. The next clause and the compute aggregate across days: max(0, Σq − count×lines).
  - Probe P4 on task 1's job with air-mover days alternating 20/34 units against a placement count of 27: aggregate non-covered = 0 unit-days (share 3332.00); per-day reading = 21 unit-days (share 3930.50).
  - Bears on: task 1's seeded days are uniform (30/day, 4/day), so both readings give the same value there. Charter defect.
- **C-08 SOURCE-FACTOR RED (XF A3, defining sentence owned by the baseline): debris baseline.**
  - The debris baseline rule and the shared sentence define "the baseboard run is the total linear feet on its baseboard removal lines". Only trim_disposal uses it (`trim_lf` is its own binding), and the baseline's own trim load term is zero.
  - Bears on: task 0 (debris) structurally. No numeric consequence.
- Observations (not grounds for rework):
  - O-01: fire as XD is not a difficulty of this blueprint (needs a coordinator ruling).
  - O-02: weak realism items listed under factor_ladders.
  - O-03: A9 grouping sentences resolved by scope.
  - O-04: debris trim tiers vs the base baseboard line schema "detach (and bag for reset)".
  - O-05: docstring phrases "before the call" are argument provenance only.
  - O-06: no task tool or share tool can book `water_card_surcharge`, so a share paid by credit card (allowed by the share rule) cannot carry the surcharge the base customer-payment rule owes (D8). Not engaged by either persona.
  - O-07: exposed_subfloor and lifted_carpet_back T1/T2 overlap as stated (pad + detach + carpet removal). That world cannot be produced under the base rule ("carpet that may be salvaged on the job's tier is billed as detach and reset, and carpet that may not be salvaged is billed as carpet removal").

## closing_checklist
Written after both reveals. The charter-global section above is pre-reveal and unchanged.
- Audit files map one-to-one to the tasks (0.md, 1.md), with _difficulty.md alongside. This is revision_1; there is no earlier revision.
- Scope against the revealed charter_scope: task 0 = {water_ext_tearout_debris, water_ext_tearout_antimicrobial, water_ext_drying_deposit} with their three tools; task 1 = {water_ext_final_hepa_vacuum, water_ext_insured_share} with their two tools. The two are pairwise disjoint and together cover all 5 extended policies and all 5 task tools. Each tree has 1-2 prerequisites, every edge is value_input, each tree has an owner=user root, and the difficulty-wide prerequisite graph is acyclic.
- Cross-task pattern found at reveal (per-task findings F0-3 and F1-4): every wrong `factor_sensitivity.tier_taken` / `factor_trace` tier is the ladder's first tier, in 7 places across the two tasks, while every scored figure is right. Both task files list every member.
- **Closing not reached.** The difficulty does not pass the source-layer audit: charter REDs C-01 to C-08 and per-task REDs in both tasks. The instantiation gates were not re-run; that is the coordinator's job after rework.
VERDICT revision_1: task0=RED task1=RED charter=C-01,C-02,C-03,C-04,C-05,C-06,C-07,C-08

## revision_2

## charter_global_frozen (revision_2)
- Freeze time: 2026-10-24T13:40Z. Auditor: same independent auditor. Entry check: the last line of tasks/water_mitigation_billing/worklog.md reads `REWORK round 2: gates 7/7 green`. Of the worklog I read only its `## REWORK round 2` section, which lists the item-id claims.
- Gate snapshot: `.audit_views/policy/water_mitigation_billing/snapshot_r2.txt`, which I produced by executing /tmp/erl0079_coord/snapshot.sh water_mitigation_billing 2. All 7 gates are green: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. check_traceability is deferred.
- Masked views: 0.json sha256=bb95f6720ae8ead744e7cad3eec3a6cdf581e5bf53af653ac9007ec3fc7d067b; 1.json sha256=ad295006ab14d6bb6db90bb522b6e8a0c131c856b5cf8345eb11fd05862bed75. I recomputed both and they are equal to the snapshot.
- Source hashes:
  - water.extended.yaml changed: 524d4ebfde43642277eab4926097945792da0e97eb58971c8b9197c61574bac0 (round 1: 15d11e84…). **The charter-global section is therefore re-derived in full.**
  - task_tools.py is unchanged (8ab9323c…bbb4), so action_binding_and_uuids is carried forward by reference to revision_1 on that hash.
  - Every blueprint product is unchanged.
- Base copy: diff of lines 1-1823 against products/water.yaml is empty.
- Masked or unread at freeze: tasks/*.json, plan.md, and every worklog section other than `REWORK round 2`.
- Scratch: /tmp/erl0079_audit_wmb/show.py, t0r2.py, t1r2.py, probes_r2.py.

### policy_conflict_scan (r2)
- Five extended policies; target tools, triggers and the subject/charge-code split are unchanged.
- final HEPA narrows its trigger to jobs carrying a pad or carpet removal line.
- The insured share adds a billability scope. It reads the claims arrangement's `denied_line_billable_to_customer` through CPARAM keyed on claim_file_id, and it now reads claims {denied_line_billable_to_customer, ordinance_law_limit}.
- The deposit's cross read moves from fire to mold (`CFIELD('mold', balance_due|payment_due_date, status='invoiced')`). Mold is claimed by mold_remediation_jobs, so O-01 is resolved.
- Mold charter facts used: the lifecycle has `invoiced`; the fields balance_due and payment_due_date exist; mold_invoicing sets the due date as invoice date + terms; mold_evt_late_fee.
- No two policies give one quantity two values. Blind trees: task 0 = {deposit; debris, antimicrobial}, task 1 = {share; HEPA}. They are disjoint and together complete.

### rule_compute_equivalence (r2)
- Mechanical sweep: every compute_basis quote and every baseline.rule sentence is verbatim in its own rule; every overwrite clause is verbatim in its base rule; every replaced_by is verbatim in its extended rule; every prerequisite source is verbatim in its blocked rule. Every compute binding has a basis.
- Factor binding sets are pairwise disjoint within each policy.
- Hand check of the changed bindings:
  - debris `result` now gates on `debris_tearout_lines == 0`, as the rule's "carries no pad removal, carpet removal or flood cut line" says.
  - antimicrobial `treated_floor`: T1 is A + detach, T2 is max(A, carpet removal), F is A, matching the rule.
  - HEPA `hepa_tearout_lines` (pad and carpet removal only) and `vacuumed_floor`: T1 is pad + A, T2 is max(A, pad), F is pad + carpet, matching the rule.
  - share: `noncovered_code_work`, `premium_share` (stand days), `covered_lgr_unit_days` (floor + wall terms × lines), `room_block_sqft` / `covered_rooms` and `result` (`0 if balance_due <= 0 … noncovered_total if sh_billable else 0`) all match their sentences.
- Probes (probes_r2.py):
  - P1, debris baseboard-only: 0, the rule's "no line".
  - P2, HEPA on a flood-cut-only category_1/class_1 job: 0, and the rule now bills no line.
  - P3, share at balance −120.00: 0.
  - P5, share on an AOB file and on a Carrier Program file: 17.70, finance charges only.
- Absent claims file: CPARAM returns None, so there is no non-covered amount, consistent with "Only an insurance_claim job linked to a claim file carries an insured's share".
- Grouping (A9): the air mover and LGR sentences now spell out "the covered … unit-days are … multiplied by the number of … lines, and the total unit-days on those lines above the covered unit-days". One reading.

### action_binding_and_uuids (r2)
Carried forward from revision_1: task_tools.py hash 8ab9323c… is unchanged, and so are the uuid8s, bodies and docstrings. The (target_tool, computes) claims are still each held by one policy.

### prerequisite_graph and prerequisite_sentences (r2)
- D1 and D2 (deposit ← debris, antimicrobial) are unchanged: PASS, as in revision_1.
- S1 now reads "The insured's share of a job whose drying is complete and whose final invoice has not yet been issued, and that carries pad removal or carpet removal lines, is fixed only after the job carries a HEPA vacuuming line."
  - The condition reads "A job in drying_complete status (drying complete, not yet invoiced) that carries pad_removal or carpet_removal lines carries a water_charges line with charge_code hepa_vacuum".
  - The resolver's scope ("drying_complete status"; "carries no pad removal or carpet removal line, is billed no final HEPA vacuuming line") now matches the sentence and the condition.
  - In every engaged world the resolver books a positive line: the vacuumed floor is at least the pad or carpet square feet, which is greater than 0 (E7). PASS.
- The graph is acyclic, every kind is value_input, every gate binding exists, every form is state, and no edge carries a fallback_reason.

### override_declarations (r2)
- The overwrite texts for debris, antimicrobial, HEPA and deposit are unchanged and still verbatim. The share keeps `overwrite: []`.
- Every base sentence of each `base_policy_refs` entry was reviewed again against the changed rules. No undeclared departure from a water base sentence.
- Cross-charter: the share's billability scope now follows claims_evt_writeoff and the claims variants' `denied_line_billable_to_customer`. P5: AOB and Program give 17.70; Homeowner Direct Pay, Public Adjuster and Commercial Large Loss give 1949.75 on the task 1 opening world.

### factor_ladders (r2)
| policy | factors (label) | P/M | XD |
|---|---|---|---|
| debris | unchanged (5P/1M) | 5/1 | 0 |
| antimicrobial | class_wetted_surfaces M; carpet_lift_treatment M; stood_wet_coverage P; regulated_wet_wipe P | 2/2 | 0 |
| deposit | iicrc_air_mover_plan M; iicrc_dehumidifier_grade P; standing_water_days P; tearout_dust_scrubbers P; past_due_mold_credit P (XD mold); shared_structure_chamber P | 5/1 | mold |
| HEPA | cut_cavity_vacuum P; moved_contents_vacuum P; regulated_dust_passes P; lifted_carpet_back M; bottom_plate_strip P; silt_residue_pass P | 5/1 | 0 |
| share | ordinance_law_code_work M (XD claims); emergency_premium_timing P; air_mover_placement_cap M; lgr_iicrc_sizing M; hepa_stripped_floor_cover M; contents_room_block P | 2/4 | claims |

All-pairs method-tier table for the changed method factors (A7):
| factor | pair | shapes | verdict |
|---|---|---|---|
| carpet_lift_treatment | T1/T2 | A + S(detach) vs max(A, S(carpet_removal)) | PASS (max operation) |
| carpet_lift_treatment | T1/F, T2/F | add an aggregate input / max operation vs A | PASS |
| lifted_carpet_back | T1/T2 | S(pad) + A vs max(A, S(pad)) | PASS |
| lifted_carpet_back | T1/F | S(pad) + F(affected_area) vs S(pad) + S(carpet_removal) | PASS (job field input) |
| lifted_carpet_back | T2/F | max op | PASS |
| lgr_iicrc_sizing | T1/T2 | (⌈A/500⌉ + ⌈r/50⌉)×L vs ⌈A/500⌉×L | PASS (adds input r) |
| lgr_iicrc_sizing | T2/F | formula vs billed unit-days, the fall-through being a branch of its own binding | PASS |
| ordinance_law_code_work | T1/T2 | S(amount, lead_safe_setup + asbestos_sampling) vs P(asbestos_sampling_fee) × COUNT(asbestos_sampling) | **FAIL**, see C-09(a) |
| ordinance_law_code_work | T1/F, T2/F | vs 0 | PASS |

- A1: every factor reads only its own bindings plus plain bindings. `covered_rooms` (plain) reads `room_block_sqft` (the factor's output) as assembly.
- A3: debris now defines the baseboard run inside the trim_disposal sentence; the share's baseline sentences (room coverage, billability) define plain bindings. No member found.
- Ladder outcomes are distinct within every ladder.
- E1 on the new ladders:
  - emergency_premium_timing (premium non-covered when the loss stood 2+ days, 40% at 1 day) is plausible carrier treatment of a non-emergent after-hours call. Observation O-10.
  - contents_room_block (category-dependent room block) is plausible.
  - lgr_iicrc_sizing is plausible.
  - ordinance T2: see C-09(b).

### findings (r2)
Round-1 items, verified one by one:
- **C-01 CLOSED.** The share's arrangement-keyed ladders are gone. Non-covered amounts are gated on `denied_line_billable_to_customer`. P5: AOB and Program give 17.70 (finance only), so nothing the claims charter forbids is billed. There is no remaining ladder keyed on the billing arrangement.
- **C-02 CLOSED** as the round-1 defect: the three tiers no longer collapse to one formula. On the task 1 world T1 gives 770.00 while T2's method would give 425.00. The rebuild introduces C-09 (new).
- **C-03 CLOSED** for its two round-1 members (carpet_lift_treatment replaces exposed_subfloor; lifted_carpet_back reshaped). The class is not empty: see C-09(a).
- **C-04 CLOSED.** lgr_iicrc_sizing is labelled `method` and its fall-through is a branch of `covered_lgr_unit_days`.
- **C-05 CLOSED.** (a) P1 gives 0; (b) P3 gives 0; (c) HEPA and S1 are scoped to pad or carpet removal, and P2 gives "no line".
- **C-06 CLOSED.** The sentence, the condition and the resolver gate coincide.
- **C-07 CLOSED.** The coverage sentences state the aggregate across lines.
- **C-08 CLOSED.** The baseboard-run definition now sits in the trim_disposal sentence.
- O-01 resolved (mold is claimed). O-06 unchanged and not engaged.

New:
- **C-09 SOURCE-FACTOR RED (introduced by the C-02 rebuild): ordinance_law_code_work.**
  - (a) Mislabelled method (XF A7, the same class as round-1 C-03). Tier 2's "tier's asbestos sampling fee times the number of asbestos sampling lines" equals the recorded asbestos_sampling line amount in every producible world: base water_evt_mitigation_services bills each line "at the unit rate of the job's tier … by the each", and water_regulated_materials bills it "once per job". So T1 vs T2 is SUM(amount) over {lead_safe_setup, asbestos_sampling} against SUM(amount) over {asbestos_sampling}, the same aggregate with a filter difference. The tariff-times-count form only disguises it. Consequence: the `method` label is dishonest. The share still keeps 3 M / 2 P without it, so no count floor fails.
  - (b) Unreal tier (E1 realism). T2 says that whenever "the limit is above zero, the ordinance or law coverage pays the lead-safe work the renovation rule requires" whatever the limit's size. db_schema defines the limit as "ordinance or law (code upgrade) coverage limit on this loss". claims_evt_supplement caps code-upgrade requests at "the ordinance or law limit less the code upgrade amounts already approved on the file". No carrier pays a covered amount beyond the policy limit. Probe P6b, task 1 world with the limit at 100.00: the rule gives non-covered code work 425.00, treating the full 345.00 lead-safe setup as covered under a 100.00 limit. A limit-faithful treatment gives at least 425.00 + 245.00 = 670.00. The tier also ignores O&L already consumed by approved code upgrades on the same claim file.
  - Bears on: task 1. T1 is taken there, so (b)'s figure is not engaged, but (a) is a structural fact about the factor in task 1's computation.
- Observations:
  - O-10: emergency_premium_timing realism; discovery delay as the coverage trigger is plausible but thin.
  - O-11: the task 1 claims estimate (2026-09-30) prices equipment and monitoring days through 2026-10-04 exactly as later billed. That is plausible as a projected estimate.
  - O-05 and O-06 are carried.

## closing_checklist (revision_2)
- Audit files are one-to-one with the tasks, and every revision_2 section is appended after revision_1, which is untouched.
- Scope (revealed charter_scope): task 0 = {debris, antimicrobial, deposit}, task 1 = {HEPA, share}. Pairwise disjoint and complete; all 5 tools covered.
- Trees: each has 1-2 prerequisites, all value_input, an owner=user root, and the graph is acyclic.
- The GT writes and every proof figure of both tasks equal the blind recomputation. Every tier label is now correct.
- Round-1 REDs C-01 to C-08 are verified CLOSED, each with a probe or recomputation (see findings (r2)).
- Regression check: no round-1 closed item reopened. One new defect, introduced by the C-02 rebuild: C-09 (ordinance_law_code_work, a mislabelled method whose T2 is unreal on the limit's size).
- **Closing not reached** because of C-09. Gates were re-run once (snapshot_r2.txt, 7/7 green).
VERDICT revision_2: task0=PASS task1=RED charter=C-09

## revision_3

## charter_global_frozen (revision_3)
- Freeze time: 2026-10-24T18:20Z. The last worklog line reads `REWORK round 3: gates 7/7 green`. I read only the worklog's `## REWORK round 3` section.
- Gate snapshot: `.audit_views/policy/water_mitigation_billing/snapshot_r3.txt`, produced by executing snapshot.sh. 7/7 green: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK; traceability deferred.
- Masked views: 0.json sha256 bb95f672…7d067b (identical to round 2); 1.json sha256 aff227ba1dfd85953636a3a2ba85f03d68403a04e883eac4ff30a97e102849cc.
- Source hashes:
  - water.extended.yaml a8f77407… has changed, so the charter-global section is re-derived. Evidence that only the insured share moved:
    - the debris, antimicrobial, deposit and HEPA rules, computes and factors recompute to identical figures and identical per-factor baselines on both worlds (t0r2.py and t1r2.py);
    - the mechanical sweep is clean for all five policies (every compute_basis quote, baseline sentence and prerequisite source is verbatim in its rule; every binding has a basis).
  - task_tools.py 8ab9323c… is unchanged, so action_binding_and_uuids is carried from revision_1.
  - Blueprint products are unchanged; the base copy is still verbatim.
- Masked or unread at freeze: tasks/*.json, plan.md, and the worklog outside `REWORK round 3`.

### What changed (water_ext_insured_share only)
- `ordinance_law_code_work` is replaced by **ordinance_law_commitments** (method, XD claims). It decides `ol_remaining`:
  - T1: the latest code-upgrade supplement request on the linked claim file carries a carrier approval → limit − the approved amount (`XSUM claims_approvals.amount` keyed on that request);
  - T2: the request has no approval → limit − requested amount;
  - F: limit.
- The regulated-materials cap is now one plain derived binding: `noncovered_code_work = MX(0, regulated_total − MX(0, ol_remaining))` when regulated lines exist.
- More than one code-upgrade request is routed to a human by a stated referral.
- All other share sentences, the prerequisite S1 and the billability scope are unchanged.

### Checks on the change
- Rule against compute: the "taken as zero when the remaining coverage is below zero" sentence matches `MX(0, ol_remaining)`. The absent request gives F; a request with no approval gives T2 (claims has no supplement-denial path; claims_msr_pending_supplements counts unapproved requests as pending). Write-off rows carry no claim_request_id (claims_receivable_writeoff fields), so the approval XSUM cannot pick them up. The single-request scope plus the referral is an accepted route.
- A7: T1 (claims_approvals.amount) vs T2 (claims_requests.requested_amount) read different tables and fields → PASS. T1/F and T2/F add an input → PASS.
- A6: one derived cap held in a plain binding.
- A1: the factor reads only its own bindings; ol_limit is plain.
- Factor counts for the share: 6 factors, 4 M / 2 P. Every ladder has distinct outcomes.

### findings (r3)
- **C-09 CLOSED.**
  - (a) No tier restates a recorded line amount as tariff × count. A sweep of all method factors found no other member.
  - (b) The limit's size is respected. Probe P8 (task 1 world, no request, limit 100): non-covered code work 670.00 (= 770 − 100).
- C-01 to C-08 stay CLOSED. The other four policies are unchanged and the share keeps every round-2 fix: billability scope, balance guard, aggregate coverage wording, the S1 scope.
- **C-10 SOURCE-FACTOR RED (new, introduced by the C-09 rebuild; E1/E2 realism): ordinance_law_commitments subtracts a code-upgrade commitment from the O&L limit even when that commitment pays for this job's own regulated lines.**
  - Symptom: the rule says "Code-upgrade amounts already committed against the limit reduce what remains of it: when the latest code-upgrade supplement request … carries a carrier approval, the ordinance or law coverage remaining is the limit less the amount the carrier approved on that request; when that request has no carrier approval yet … the limit less the amount the request asks for". The job's lead-safe setup and asbestos sampling total is then charged against that remainder.
  - Neither the rule nor the compute asks what scope the supplement covers. claims_requests carries `related_job_id` ("the … job … the request concerns"), and on a file whose only code-upgrade work is this job's regulated lines, the supplement is the carrier's payment for exactly those lines.
  - Demonstrated consequence: probe P7, task 1 world, limit 1000.00, a code-upgrade supplement with related_job_id = this water job, requested 770.00 and approved 770.00. The rule gives remaining 230.00 and non-covered code work 540.00. But the carrier has approved those same 770.00 of lines, so a coverage-faithful share has 0.00 non-covered for them.
  - A pending request concerning this job "reserves" coverage against itself in the same way. Probe P9: pending 700.00 gives non-covered 470.00.
  - The same 770.00 of work is funded twice: by the carrier's supplement approval and by the insured's share.
  - Affected: water.extended.yaml water_ext_insured_share (the code-upgrade commitment sentence; compute `ol_remaining`); factor ordinance_law_commitments.
  - Bears on: task 1 (see 1.md F1-6).
- Observations O-05, O-06, O-10 and O-11 are carried.

## closing_checklist (revision_3)
- Revision_3 sections are appended to all three files; earlier revisions are untouched.
- Scope (revealed charter_scope) is unchanged: disjoint and complete. Trees are acyclic, all value_input, with owner=user roots. The gates were re-run once (snapshot_r3.txt, 7/7).
- Task 0: GT is identical to revision_2, and all four relationships PASS.
- Task 1: every GT figure equals the blind recomputation of the policy as written, but there is a second defensible share (C-10 / F1-6).
- Round-2 RED C-09 is CLOSED. No round-1 item regressed. New: C-10, introduced by the C-09 rebuild.
- Closing not reached because of C-10.
VERDICT revision_3: task0=PASS task1=RED charter=C-10

## revision_4

## charter_global_frozen (revision_4)
- Freeze time: 2026-10-24T23:20Z. The last worklog line reads `REWORK round 4: gates 7/7 green`. I read only the worklog's `## REWORK round 4` section.
- Gate snapshot: `.audit_views/policy/water_mitigation_billing/snapshot_r4.txt`, produced by executing snapshot.sh. 7/7 green; traceability deferred.
- Masked views: 0.json sha256 bb95f672…7d067b (unchanged since round 2); 1.json sha256 1706306e6f7933656f11f5bd386dbae1885383154e411474637a60efd914fcc7.
- Source hashes:
  - water.extended.yaml 310c7651… has changed. Per-policy canonical dump hashes for debris (279f6929b9e7), antimicrobial (9988d6d273f6), deposit (be66e66bc6eb) and HEPA (d2db86a65f3f) are identical to round 3, so only water_ext_insured_share moved (now 83f8a15bbc81). Its section is re-derived; the rest is carried from revision_3.
  - task_tools.py 8ab9323c… is unchanged.
  - Blueprint products are unchanged; the base copy is still verbatim.
- Masked or unread at freeze: tasks/*.json, plan.md, and the worklog outside `REWORK round 4`.

### What changed (water_ext_insured_share only)
- `ordinance_law_commitments` is replaced by **code_upgrade_supplement_decision** (method, XD claims). It decides `code_work_covered`:
  - T1: the latest code-upgrade request on the file names this job (`related_job_id == HID`) and carries an approval → min(approved, limit);
  - T2: it names this job and is pending → min(requested, limit);
  - F: max(0, limit).
- Non-covered code work = max(0, regulated_total − code_work_covered).
- A request naming another job or no job, or more than one request, is a stated referral (accepted B7 route; the compute residue is not used).

### Checks on the change
- Mechanical sweep: clean (compute_basis, baseline sentences and the prerequisite source are all verbatim; no shared factor bindings).
- Rule and compute agree on all six branches. Probes (probes_r4.py, task 1 world):
  - own request approved 770 of 770 → 0.00;
  - own request approved 500 → 270.00;
  - own request pending 770 under limit 1000 → 0.00;
  - own request pending 770 under limit 600 → 170.00;
  - no request at limits 0 / 100 / 1000 → 770.00 / 670.00 / 0.00.
  - The other-job branch is the stated referral.
- A7: T1 (claims_approvals.amount) vs T2 (claims_requests.requested_amount) read different fields → PASS. T1/F and T2/F add an input plus a min operation → PASS.
- A1: the factor reads only its own bindings plus ol_limit (plain). A6: one derived cap.
- Realism (E1/E2):
  - The covered amount is now tied to the supplement that concerns this job and is capped at the limit. The carrier's partial approval leaves the remainder with the insured, which is billable on DTP.
  - No branch funds the same work twice: the carrier's supplement amount and the insured's non-covered amount always sum to the regulated total, or the job is covered by the limit.
- Class sweep (any read that subtracts or reserves an amount without checking what the record concerns): debris, antimicrobial and HEPA read only this job's lines; the deposit reads a status-filtered sibling mold holding; the share's other non-covered amounts read only this job's lines. No member.

### findings (r4)
- **C-10 CLOSED.** The commitment is now keyed on `related_job_id == this job`. Other-job and file-wide requests are referrals. Probes show no double funding.
- C-01 to C-09 stay CLOSED. The other four policies are byte-identical to round 3, and the share keeps the billability scope, the balance guard, the aggregate coverage wording and the S1 scope.
- New defect: none.
- Observations carried: O-05, O-06, O-10, O-11.
- O-12 (new, observation): with no own-job request, the fall-through counts code work as covered up to the full limit before any supplement is filed. This is plausible as the standard, since the company pursues code work by supplement under claims_evt_supplement. Not engaged on task 1, which takes T1.

## closing_checklist (revision_4)
- **Audit files:** one per task (0.md, 1.md) with _difficulty.md alongside. Revisions 1-4 are kept in order and older text is untouched. Every revision_4 comparison section carries PASS.
- **Coverage and scope:** the 5 extended policies are fully covered. Task scopes (revealed charter_scope) are task 0 = {debris, antimicrobial, deposit} and task 1 = {HEPA, share}, spanning each whole tree; they are pairwise disjoint. Task tools and GT are closed. Each tool's uuid8 is independently generated and frozen (a8b773d4, 173ee43e, ee9a2909, eb899e1c, cc172b06; tools unchanged since revision_1).
- **Trees:**
  - task 0 has 2 prerequisites, both value_input, with an owner=user deposit;
  - task 1 has 1 prerequisite, value_input, with an owner=user share;
  - the difficulty-wide prerequisite graph is acyclic.
- **Computations:** every computation has a self-sufficient baseline and 4-6 factors: debris 6 (5P/1M), antimicrobial 4 (2P/2M), deposit 6 (5P/1M), HEPA 6 (5P/1M), share 6 (2P/4M).
  - Each task has multi-source factors and a cross-difficulty factor (task 0: mold; task 1: claims).
  - Every ladder has 3 tiers, stated in full in its rule, with distinct outcomes.
  - Every factor bears weight on its task's world against an honest baseline, and every all-baseline fall-back differs from gold (642.00, 331.20, 9521.77, 254.20, 82.50).
- **Gates:** the instantiation gates were re-run on the final form (snapshot_r4.txt, 7/7 green). check_traceability stays deferred to the KB stage per the coordinator.
- **Status:** all charter REDs C-01 to C-10 are CLOSED, and no defect is open. The difficulty passes the source-layer audit.
VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- Freeze time: 2026-10-25T02:15Z.
- Inputs:
  - The last worklog line reads `REWORK round 5: gates 7/7 green`. I read only the worklog's `## REWORK round 5` section.
  - The renderer findings: audits/render_source/water_mitigation_billing/render_r1.md.
  - The realism bar: audits/render_source/realism_bar.md (R1-R6, X1-X4, RULE-1..5), applied in full for the first time this round.
- Gate snapshot: `.audit_views/policy/water_mitigation_billing/snapshot_r5.txt`, produced by executing snapshot.sh. 7/7 green; traceability deferred.
- Masked views are unchanged from revision_4: 0.json bb95f672…7d067b; 1.json 1706306e…14fcc7.
- Source hashes:
  - water.extended.yaml f8752b18… has changed.
  - The deposit's canonical dump is identical to revision_4 (be66e66bc6eb).
  - Debris, antimicrobial, HEPA and share dumps changed. Every compute recomputes to identical figures, identical per-factor baselines and identical skip effects on both worlds. The round-4 code-upgrade probes and the round-2 edge probes (P1-P3, P5) give identical results. So the change is text-only, as the reworker states.
  - task_tools.py 8ab9323c… is unchanged. Blueprint products are unchanged; the base copy is still verbatim.
- Masked or unread at freeze: tasks/*.json, plan.md, and the worklog outside `REWORK round 5`.

### Renderer items (render_r1.md), verified one by one
- **R5-1 (render blocker, XF C2/C3: replaced_by points back to the retired units clause): CLOSED.**
  - All three sibling `replaced_by` texts (debris, antimicrobial, HEPA) now restate the full units list of the retired base sentence ("extraction, antimicrobial, pad and carpet work and HEPA vacuuming by the square foot, … lead-safe setup and asbestos sampling by the each").
  - Each one names its own scope and excludes its two siblings by name.
  - Each one is verbatim in its own rule.
  - Class sweep: I regex-searched every extended rule for back-references ("mitigation service rule", "base rule", "the units", "as the … rule sets/provides/states", "retired", "that rule") and found none.
  - The deposit's two replaced_by texts restate their in-force parts (insurance no-deposit; the tender list). The share has no overwrite.
  - No member remains.
- **R5-2 (A9, hepa_stripped_floor_cover grouping): CLOSED.**
  - The rule and the T2 ladder text now read "the square feet on those lines above the sum of the pad removal square feet and 4 square feet for each linear foot on the flood cut lines".
  - That has one reading, matching `MX(0, sh_hepa_sqft − sh_pad_sqft − sh_cut_lf × 4)`.
  - Class sweep of every multi-operator sentence in the five rules:
    - debris "the total rounded up";
    - deposit air-mover, LGR and collection sentences ("each term rounded up on its own"; a plain additive chain);
    - share air-mover and LGR coverage ("the covered … unit-days are … multiplied by …, and the total unit-days … above the covered unit-days"), the premium ("line amounts less the tier's fee for each of those lines"), code work ("the amount by which … total more than the code work covered");
    - antimicrobial class_3 wall area ("run times 8 feet … plus the affected floor area"; the other grouping is dimensionally void);
    - HEPA T1 ("pad square feet plus the affected floor area").
    - Each has one reading.
    - The two "A plus B, multiplied by C" sentences (antimicrobial billed square feet, HEPA billed square feet) stay observation O-03. Their scope sentences ("material that stood wet", "every pass factor that applies to the job") fix the reading, and the renderer read them without flagging. No member remains.
- **R5-3 (B1, line date undefined on a carpet-removal-only job): CLOSED.**
  - Debris and antimicrobial lines are now "dated the service date of the job's latest flood cut line, or of its latest pad removal line when it has no flood cut line, or of its latest carpet removal line when it has neither". That covers every billed case: a line is billed only when the job carries a pad removal, carpet removal or flood cut line.
  - Class sweep: final HEPA is dated the drying complete date, which every in-scope job (drying_complete status) carries; the two payment tools stamp the posting date. No member remains.
- **R5-4 (base: parameter_schema.monitoring_visit_fee "included visits")**: recorded as an observation (BLUEPRINT-KNOWN, frozen base). No extended policy reads that parameter. O-14.

### Realism-bar grading (every factor of the charter; RULE-1..5)
| policy | factor | shape | grade |
|---|---|---|---|
| debris | wet_flooring_load | R2 (days since loss) | accepted |
| debris | class_cut_height | R1/R4 (IICRC class) | accepted |
| debris | trim_disposal | R1/R4 (year built vs RRP cutoff, category) | accepted |
| debris | carry_out_access | R1 (property type) | accepted |
| debris | dispatch_haul_window | R1 (dispatch window) | accepted |
| debris | sealed_bagging | R1/R4 (IICRC category) | accepted |
| antimicrobial | class_wetted_surfaces | R4 | accepted |
| antimicrobial | carpet_lift_treatment | R1 (recorded line kinds) | accepted |
| antimicrobial | stood_wet_coverage | R2 | accepted |
| antimicrobial | regulated_wet_wipe | R4 (RRP / asbestos cutoffs) | accepted |
| deposit | iicrc_air_mover_plan | R4 | accepted |
| deposit | iicrc_dehumidifier_grade | R4 | accepted |
| deposit | standing_water_days | R2 | accepted |
| deposit | tearout_dust_scrubbers | R1 | accepted |
| deposit | past_due_mold_credit | R2 (days past due); claimed sibling mold (RULE-1) | accepted |
| deposit | shared_structure_chamber | R1 (property type), gated on days since loss ≥ 1 | accepted; O-13 |
| HEPA | cut_cavity_vacuum | R1 | accepted |
| HEPA | moved_contents_vacuum | R1 | accepted |
| HEPA | regulated_dust_passes | R4 | accepted |
| HEPA | lifted_carpet_back | R1 | accepted |
| HEPA | bottom_plate_strip | R1/R4 | accepted |
| HEPA | silt_residue_pass | R2 | accepted |
| share | code_upgrade_supplement_decision | R5/R4 (O&L limit, approved amount applied once) | accepted |
| share | emergency_premium_timing | R2 | accepted |
| share | air_mover_placement_cap | R4 | accepted |
| share | lgr_iicrc_sizing | R4 | accepted |
| share | hepa_stripped_floor_cover | R1/R4 | accepted |
| share | contents_room_block | R1 | accepted |

- Rejected shapes:
  - X1: no tenure, loyalty or relief perks.
  - X2: no discounts or caps stacked on one amount. The share's caps act on distinct line families, and no charge is split into two factors that sum back.
  - X3: no factor is embedded in a recorded amount. code_upgrade_supplement_decision reads the recorded approval as input and moves the result (3234.43 at baseline against 3504.43).
  - X4: none. The billed-square-feet multipliers (coverage, passes) stay observation O-02 under R1 company schedules.
- R6: no factor is tagged, and none is needed.
- RULE-1: task 0 reads mold and task 1 reads claims, both claimed siblings.
- RULE-2: every cross-category record a scored factor reads is a state its charter produces and is read by gold. The mold job and ledger were verified at revision_2; the claims file, supplement request and approvals were verified at revision_4.
- RULE-4: the REWORK round 5 section carries no figures.
- RULE-3 and RULE-5 are not applicable.
- Observations:
  - O-13: shared_structure_chamber is a second factor touching the days-since-loss dimension in the deposit, besides standing_water_days. It is keyed primarily on property type, decides a different quantity (estimate multiplier against drying days) and does not split one convention. Noted against R2, not RED.
  - O-14: the monitoring_visit_fee "included visits" base text (BLUEPRINT-KNOWN).

### findings (r5)
- R5-1, R5-2 and R5-3 are CLOSED. R5-4 is an observation.
- C-01 to C-10 stay CLOSED; no compute, seed or gold moved.
- New defect: none.
- Observations carried: O-02, O-03, O-05, O-06, O-10, O-11, O-12; new O-13, O-14.

## closing_checklist (revision_5)
- Audit files are one per task; revisions 1-5 are kept in order, and every revision_5 comparison carries PASS.
- Scope (charter_scope unchanged) is disjoint and complete. The trees and acyclicity are as revision_4. Tools and uuid8s are unchanged.
- Each computation keeps its self-sufficient baseline and 4-6 factors. Every factor bears weight against an honest baseline, and every all-baseline fall-back differs from gold.
- Every factor is graded accepted under realism_bar.md; there are no R6 waivers. RULE-1 and RULE-2 are met in both tasks.
- The renderer's three source items (R5-1 units back-reference, R5-2 A9 grouping, R5-3 undated line) are closed with empty class sweeps. The base note is logged as BLUEPRINT-KNOWN.
- Gates re-run on the final form: snapshot_r5.txt, 7/7 green. check_traceability is deferred to the KB stage.
- No open defect. The difficulty passes the source-layer audit, and a fresh render can start from Step 0.
VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

## charter_global_frozen (revision_6)
- Freeze time: 2026-10-25T06:15Z.
- Inputs:
  - The last worklog line reads `REWORK round 6: gates 7/7 green`. I read only the worklog's `## REWORK round 6` section.
  - The items: audits/policy_kb/water_mitigation_billing/_difficulty.md (KB re-judge revision_2: SRC-1, SRC-2).
  - The published docs: docs/mold and docs/claims.
  - realism_bar.md (RULE-1..7).
- Gate snapshot: `.audit_views/policy/water_mitigation_billing/snapshot_r6.txt`, produced by executing snapshot.sh. 7/7 green.
- **Charter and tools unchanged:** water.extended.yaml sha256 f8752b18e127ac45739ea1b23edcf68448a663ee73fb021b7642eff7e02b1c64 and task_tools.py 8ab9323cfbe5752b6b6e1915d544704a1ee890c4afc2970bc2d7a60d5b9adbb4, both equal to the coordinator's stated hashes and to revision_5.
  - Every charter-global section is therefore carried forward by reference to revision_5, on those two hashes. RULE-6 and RULE-7 add nothing to judge: no factor changed, and the rebuild-only rule does not apply.
- Masked views: 0.json sha256 87671eae5a7b8d046c66fe6dbfb1b550a9d5f20b45326a20dfa53d2db76b165a (changed: task 0 seed); 1.json 1706306e…14fcc7 (unchanged since revision_4).

### Seed items, verified against the published mold docs (task 0 world)
- **SRC-1 CLOSED.** mold_payments b63f1977 is now 350.00 (debit_card, 2026-06-03, the signing date).
  - Published mold_ext_signing_deposit (`signing_deposit_amount_cb00dee0`): tier self-pay deposit 150.00 (Spot), minus any credit floored at 0, plus raises and prepayments, plus charge lines booked at signing (none: every line is dated 2026-06-04 or later), minus prior payments (none).
  - Raises:
    - `short_notice_deposit_raise_5e3fb1a8`: notice = 2026-06-04 − 2026-06-03 = 1 day, which is ≤ 2, so the raise is max(200.00, 20% × 150.00 = 30.00) = 200.00;
    - `carrier_payment_route_deposit_raise_24dae287`: no linked claim file, so none;
    - `claim_coverage_deposit_credit_3309fe1a`: no claim file, so none;
    - `contaminated_water_deposit_raise_7fe584a8`: no linked water job, so none;
    - `lead_paint_prepayment_57c6a9de`: no linked water job and built 1994 ≥ 1978, so none.
  - The hub's waits (pre-removal asbestos sampling for a pre-1981 building; work-plan visit on a protocol tier) are not engaged (1994; Spot has protocol_required false).
  - 150.00 + 200.00 = 350.00 ✓.
- **SRC-2 CLOSED.** mold_charges 7ee290b9 is now present: debris_disposal 2026-06-04, quantity 1 × 214.00 = 214.00.
  - Published mold_ext_disposal_line (`debris_haul_off_charge_c2b63a41`, `haul_off_line_amount_8173b50e`): dated the latest drywall/insulation removal date (2026-06-04).
  - Loads: drywall only, 8 sq ft ≤ the 400 roll-off threshold, so ⌈8/160⌉ = 1 (`bagging_stream_load_counts_a5b9cc0c`).
  - Fee: no linked water job, so the tier's 214.00 fee (`debris_class_load_fees_2383922d`).
  - Trip charge (`haul_trip_charges_6c9d7959`): the single removal date equals the containment date 2026-06-04, so none.
  - Wet debris (`wet_debris_charges_4859b390`): no linked water job, so none.
  - The line is 214.00 ✓.
- Mold job totals:
  - Final invoice 678.50 = 20.80 + 18.80 + 16.40 + 49.20 + 168.50 + 95.40 + 95.40 + 214.00, the scope, equipment and disposal lines at invoicing. That is at least the 395.00 minimum job charge, so no minimum_charge line.
  - Late fees 2026-08 and 2026-09: max(25.00, 1.5% × 328.50 or 353.50), so 25.00 each ✓.
  - balance_due 378.50 = 678.50 − 350.00 + 50.00 ✓. Due date 2026-07-25 = invoice + 15 days, unchanged.
- **Exhaustive re-pricing (task 0 mold rows):** every other published mold extended line policy was checked against the Spot job.
  - The work-plan visit (`work_plan_visit_charge_c58d7744`) belongs only to tiers that require a protocol, and Spot does not.
  - Pre-removal asbestos sampling (`asbestos_presampling_charge_8b37f2c2`) applies only before the 1981 cutoff, and the building is 1994.
  - The mold insured share does not apply to a self-pay job.
  - The remaining lines are base-priced at Spot rates (hepa_vacuum 0.52, drywall_removal 2.35, antimicrobial 0.41, ppe 24.60, technician 84.25 business hours, dehumidifier 95.40 × 2 days within cap 2). The clearance is supervisor_visual with a 0.00 fee, so no line. No member remains.
- **Exhaustive re-pricing (task 1 claims rows):**
  - The code-upgrade supplement 69c7761f is on a Direction to Pay file. The published claims_ext_regulated_scope_supplement is scoped to Public Adjuster Coordinated files ("Any other supplement is handled under the base supplement rule"), so the base rule governs: approved status, within the 180-day window, at least the 250.00 minimum, at most the limit 1000.00 less approved code upgrades 0.00.
  - The deductible assessment of 1500.00 is per the declarations under base claims_evt_deductible.
  - The initial and supplement approvals are recorded carrier acts with no formula.
  - Match ✓, the same as the KB re-judge.
- **Own-category history:**
  - task 0 seeds no line an extended rule prices;
  - task 1's debris (cbe53561, 1530.10) and antimicrobial (55304f9d, 1500.24) lines re-price exactly under the current rules (seed check);
  - the other lines are base-priced (verified at revisions 1-4).
- Realism bar: the factor grades are unchanged from revision_5. RULE-2: the cross-category rows the scored factor reads (the mold job, its balance and due date) are states the mold charter produces under its published rules and are read by gold.

### findings (r6)
- SRC-1 and SRC-2 are CLOSED.
- The exhaustive cross-product and own-history re-pricing found no remaining member.
- C-01 to C-10 and R5-1 to R5-3 stay CLOSED.
- New defect: none.

## closing_checklist (revision_6)
- Revision_6 is appended to all three files. The charter and tools hashes are unchanged (f8752b18…, 8ab9323c…), so the charter-global checklist of revision_5 stands by reference.
- SRC-1 and SRC-2 are closed. The exhaustive other-product re-pricing (task 0 mold rows against docs/mold; task 1 claims rows against docs/claims) and the own-category history check found no remaining member.
- Gold is unmoved in both tasks, the proof text is consistent, and the gates are re-run (snapshot_r6.txt, 7/7 green).
- No open defect.
VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
