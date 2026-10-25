# Policy-task audit — premium_billing_and_grace / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-18T03:27Z by the independent policy auditor (round 1). Built from the charter, schema and tool contracts only; nothing in this section is derived from any revealed GT.
- `billing.extended.yaml` sha256=24a5e811ee8c77e0c1a3d96d78034430f8d3ef54cff021ec582302a9a387fbdc; `task_tools.py` sha256=87aa55fbd4c5e1ae7b09c08724ce26b24e819ef8012880ec0002a8932792107f (both match the brief).
- Masked views used: `.audit_views/policy/premium_billing_and_grace/r1/task_0.json` sha256=a15744447e…85c5, `task_1.json` sha256=e3b13def…f420 (match the brief). They carry only frozen_time, user_scenario, initial_state; `_masked_keys` = charter_scope, computations, db_closure, db_closure_matches_initial_state, design_rationale, evaluation_criteria, prerequisite_closure, required_documents, solvability_contract.
- Read: blueprint.yaml, db_schema.json, share_tools.py (signatures), products/billing.yaml, dental.yaml / vision.yaml / ortho.yaml (rates and the clauses cited), the extended charter, task_tools.py, audits/render_source/XF_recipe.md, coordinator notes, `skills/erl-task-instantiate/scripts/check_compute.py` (DSL semantics only). Not read: tasks/*.json, plan.md, worklog.md, any other audit, any sibling difficulty or other scenario.
- Gate snapshot (from the brief, not re-run): check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire all rc=0. Entry conditions are met.
- Scratch: `/tmp/audit_premium_billing_and_grace_0070/derive.py` (replays every compute on the masked worlds with the check_compute DSL) and `probes.py` (decoy / hypothetical-world probes cited below as P-a … P-e).

### policy_conflict_scan
- Base copy: the non-extended part of the charter parses identical to `blueprint/products/billing.yaml` (every key equal). Verbatim.
- Five extended policies: billing_ext_vision_term_credit (VTC, agent, `book_vision_term_credit_956578a0`), billing_ext_grace_cure_payment (GCP, user, `submit_grace_cure_payment_5521c4c8`), billing_ext_dental_tier_credit (DTC, agent, `book_dental_tier_credit_2a6e4a9b`), billing_ext_rider_end_credit (REC, agent, `book_rider_end_credit_fb22198c`), billing_ext_renewal_payment (RNP, user, `submit_renewal_payment_53926ce3`).
- Prerequisite graph: GCP→VTC; RNP→DTC; RNP→REC. Two disjoint trees, so the M=2 scopes {GCP,VTC} and {RNP,DTC,REC} are mutually exclusive and jointly complete over the five policies.
- Overlapping subjects: VTC, DTC, REC all write `billing_premium_credit`; distinct product_line / credit_reason keys (vision+termination_unearned, dental_ppo+plan_change_difference, ortho_rider+termination_unearned), so the base `distinguish_by` keys never collide between them. GCP and RNP both write `billing_payment_received` (purpose grace_cure vs regular).
- Conflicts found: VTC vs REC sibling overwrites of the same base clause contradict each other (finding C1); RNP prices the added vision plan against the in-force base invoicing clause without an overwrite (C2); RNP's savings presuppose invoices the in-force base invoicing clause cannot issue (C3); GCP's held-payment add-back departs from base payment application without an overwrite (C4); GCP's own overwrite scope contradicts two of its own tiers (C5).
- Trigger rule (XF-14): the task tools write only `billing_premium_credit` (base triggers: billing:billing_paid_through_update) and `billing_payment_received` (base triggers: billing:billing_paid_through_update). No trigger lands in another category. CLEAN. (Observation O1: neither tool body performs the same-category paid-through update its event triggers.)

### rule_compute_equivalence
- Mechanical sweep: every `compute_basis` quote of all five policies is verbatim in its rule (whitespace-normalised); every compute binding has a basis; every `baseline.rule` sentence is in the rule; every factor ladder tier is a rule sentence and a branch of its `decides` binding.
- DSL semantics relied on (check_compute.py): `_within` = 0 ≤ MONTHS(date, NOW) < N (matches each rule's anniversary sentence); LATEST/XLATEST keep the first-recorded row on a tie (strict `>`); XSUM/XCOUNT/XLATEST are scoped to the customer, not to an enrollment or account unless filtered; CPARAM(cat, p, variant_name=X) returns a parameter only if the customer holds a holding of variant X, else None.
- Gaps (all in C9): r_dental tier 2 cannot be computed (CPARAM on a plan the customer does not hold returns None; P-b raises TypeError) though the rule promises "the requested plan's premium"; g_disc tier 1 rule "no longer carries an AutoPay discount" vs compute `P('autopay_discount_monthly') == 0` (no history test); vtc_month rule "has collected at least one regular automatic bank draft" vs compute counting eft payment rows whether or not later returned; the three credit tools' booked `coverage_month` / `months_covered` are fixed by rule sentences ("The credit is booked … whose first coverage month is … and whose months covered are …") with no compute binding; absent subscriber active dental enrollment (DTC sub_plan, RNP ds_plan = None while an LOE dependent exists) has no rule sentence and the compute raises; unstated selection/tie rules (DTC sub_tier/sub_plan/sub_change and tier_req_eff; RNP ds_tier/ds_plan, dq_plan/dq_eff, v_eff/v_elected/v_plan, rc_plan); RNP carries no month-counting convention sentence although it counts whole months (MONTHS(renewal_start, v_eff)).
- Rounding: every policy rounds once at the end with RND(…,2), matching "rounded half up to the cent once, at the end". Order sentences (XF-3) present in all five and matching compute placement of the floor.

### action_binding_and_uuids
- (target_tool, computes) pairs unique: five tools, five policies, one each.
- uuid8s: 956578a0, 5521c4c8, 2a6e4a9b, fb22198c, 53926ce3 — distinct, no shared prefix/suffix, no sequence. PASS.
- Docstrings: no ordering words, no other tool named, no example values (format descriptions only). No factor id is a substring of any tool name (mechanical check). Tool bodies validate no prerequisite, status or eligibility (each only creates one ledger row and lowers balance_due).
- Observation O2: `submit_grace_cure_payment_5521c4c8` docstring opens "to bring it out of its grace period" (purpose); the body does not change status (grace→active is a system transition in the base lifecycle), so no false effect claim.

### prerequisite_graph
- Every policy has `prerequisite` (VTC/DTC/REC `[]`). Edges point at extended policy ids in this file, none at base or self; graph acyclic.
- Each `policy_source` is verbatim in the blocked policy's own rule (mechanical check). `form: state` on all three, no `fallback_reason` (correct). `gate` names exist as compute bindings (`past_due` in GCP, `bal` in RNP); `kind: value_input` honest (the credit enters cred_all / bal). `resolved_by` is the depended-on policy's target tool. `condition` matches the sentence's scope (both say "each … unit/enrollment/rider"). No authoring-viewpoint words.

### prerequisite_sentences
- GCP: "The grace-cure payment is fixed only after the account's ledger carries vision-line termination credits covering every month billed after the termination month of each vision plan unit it funds whose subscriber enrollment ended by voluntary termination." — ordering connective "only after"; record-visible state (vision-line termination credits and their months on the ledger); no tool/id/snake_case; only `book_vision_term_credit_956578a0` writes product_line vision + termination_unearned → single resolving write; derivation: sentence → ledger credits on the vision line → the policy whose rule books "a termination credit … on the vision line" = VTC.
- RNP edge 1: "The renewal payment is not fixed until the account's ledger carries dental-line plan-change difference credits covering every prepaid month after the termination date of each dependent dental enrollment the account funds that ended for loss of eligibility." — "not … until"; only DTC books dental_ppo plan_change_difference. Edge 2: "The renewal payment is fixed only after the account's ledger carries rider-line termination credits covering every prepaid month after the termination date of each orthodontic rider the account funds that has ended." — "only after"; only REC books ortho_rider termination_unearned. Depended-on rules do not restate the sentences; no second wording, no cross-problem order elsewhere in any rule.
- Defect (C11): all three sentences quantify over "each" unit / dependent enrollment / ended rider, while each resolving policy selects exactly one record ("where more than one such enrollment is on record, it is the one with the latest termination date"). With two qualifying records the waited-on state can never be brought about by the resolving policy, so the sentence is broader than the write that resolves it.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry:
- VTC vs billing_credits_refunds: termination_unearned clause retired (declared, scoped). Other sentences (free_look, prepay_unearned, plan_change, overpayment, aptc, retro, refund-after-claim) untouched/inherited. vs billing_agg_credit_application: followed (credit stays on account). Sibling exclusion broken (C1).
- GCP vs billing_evt_payment_application: threshold sentence retired (declared, scoped). "A payment is applied to the oldest unpaid coverage month first" is not retired, yet g_hold says a booked grace-cure bank transfer "does not count" and adds it back (C4, undeclared). vs billing_evt_invoicing: AutoPay-discount sentence retired with scope "only to those [past-due] months", contradicted by g_next tier 2 and g_disc tier 1 (C5). vs billing_grace_and_lapse: cure sentence followed; vs billing_evt_returned_payment: fee rules followed (fees are already booked; g_fee only decides what the cure amount collects).
- DTC vs billing_credits_refunds: plan_change_difference clause retired (declared, scoped, no sibling). Inherited otherwise.
- REC vs billing_credits_refunds: termination_unearned clause retired, but its replaced_by keeps the vision credit "under the base rule" (C1).
- RNP vs billing_agg_credit_application: "applied to the next invoice unless … refund" retired for overpayment credits (declared). vs billing_evt_invoicing (listed as a base ref, no overwrite): r_vtier prices the added vision plan at a tier other than "that plan's monthly premium for its coverage tier" (C2); r_dental/r_rider tier 1 and r_vstart re-price the invoice issued last on the premise that it was not priced by the in-force invoicing clause (C3). vs billing_evt_payment_application: followed.
- Disguised forms: no 0/1 multiplier; anonymous intermediates found only as C6 couplings; dropped branch: none.

### factor_ladders
| policy | factor | effect | tiers | multi-source tier | cross_difficulty | structural verdict |
|---|---|---|---|---|---|---|
| VTC | vtc_month | parameter | 3 | yes (arrangement param + draft/invoice history) | – | ok |
| VTC | vtc_offset | method | 3 | yes (vision enrollment dates + vision claims) | vision | ok (tier1 data-selected window vs tier2 fixed 12; passes XF-15) |
| VTC | vtc_prior | parameter | 3 | – | – | ok; coupled to vtc_int (C6) |
| VTC | vtc_int | parameter | 3 | – | – | reads vtc_prior's selection (C6) |
| VTC | vtc_recover | parameter | 3 | yes (vision request + billing invoices) | vision | ok; realism observation O3 |
| GCP | g_next | method | 3 | yes | – | tiers 1≡2 on every arrangement with autopay_discount_monthly 0 (C7) |
| GCP | g_disc | parameter | 3 | yes | – | ok; rule/compute "no longer" gap (C9) |
| GCP | g_fee | parameter | 3 | – | – | duplicate selection with g_relief (C6); unwindowed last fee (C10) |
| GCP | g_relief | parameter | 3 | yes | – | duplicate selection (C6) |
| GCP | g_hold | parameter | 3 | yes | – | duplicate selection with g_next (C6); undeclared override (C4) |
| GCP | g_tol | parameter | 3 | – | dental | unreal ladder (C8-i) |
| DTC | dtc_basis | parameter | 3 | yes | – | tier 2 unreal (C8-ii) |
| DTC | dtc_window | method | 3 | – | dental | tier 2 unreachable in effect (C7) |
| DTC | dtc_dup | parameter | 3 | – | – | coupled to dtc_int (C6) |
| DTC | dtc_int | parameter | 3 | – | – | reads dtc_dup's selection (C6) |
| DTC | dtc_recover | parameter | 3 | – | – | condition not weighed (C8-iii) |
| REC | rc_months | method | 3 | – | – | ok (data-selected end anchors) |
| REC | rc_basis | parameter | 3 | yes | – | tier 2 unreal (C8-ii); duplicate selection (C6) |
| REC | rc_dup | parameter | 3 | – | – | booking args coupled (C6) |
| REC | rc_recover | parameter | 3 | – | – | condition not weighed (C8-iii) |
| RNP | r_dental | parameter | 3 | yes (dental enrollments + invoice) | dental | tier 2 uncomputable (C9) |
| RNP | r_rider | parameter | 3 | yes | ortho | ok structurally |
| RNP | r_vstart | method | 3 | – | vision | tiers 1≡2 (C7) |
| RNP | r_vtier | parameter | 3 | yes | vision | gated through r_vstart (C6); undeclared override (C2) |
| RNP | r_giveback | method | 3 | – | – | method-shape FAIL (C7); tier 1 unreal (C8-iv) |

Counts as declared: VTC 5 (2+ param, 1 method), GCP 6 (5 param, 1 method), DTC 5 (4 param, 1 method), REC 4 (3 param, 1 method), RNP 5 (3 param, 2 method). Every ladder has three disjoint tiers stated in the rule with its fall-through equal to the baseline. Cross-difficulty factors read dental (g_tol, dtc_window, r_dental), vision (vtc_offset, vtc_recover, r_vstart, r_vtier), ortho (r_rider). REC alone declares none. After the strikes in C7/C8: GCP keeps g_next as its only method and loses it on non-AutoPay worlds; DTC keeps no honest method; RNP keeps no honest method (r_vstart and r_giveback both fail).

Method-shape all-pairs (XF-15):
- vtc_offset: T1 SUM(plan_paid, window from effective date) − rate×tenure | T2 SUM(plan_paid, 12 m) − rate×12 | T3 0. T1/T2 differ by data-selected window and data-selected multiplier: PASS. T1/T3, T2/T3: T1/T2 only fire when positive: PASS.
- g_next: T1 last_amt | T2 last_amt + P(autopay_discount_monthly) | T3 0. T1/T2 PASS only where P > 0; on Quarterly Bill / Annual Prepay accounts paying by eft (reachable: both accept eft), T2 ≡ T1. FAIL on part of the reachable domain.
- dtc_window: T1 MONTHS(dep_end, paid_thru) | T2 MONTHS(request eff, paid_thru)+1 | T3 MONTHS(tier change, paid_thru)+1. T2 fires only when no LOE dependent exists, where tier_diff = 0, so T2 and T3 give the same scored credit (0.00) over T2's whole domain (P-c: 0.00 under T2 and 0.00 under baseline). FAIL.
- rc_months: T1 MONTHS(end, paid_thru) | T2 MONTHS(end, NOW)+1 | T3 MONTHS(end, last invoice month)+span. Different data-selected end anchors: PASS (observation O4: all three are window lengths).
- r_vstart: T1 12 | T2 12 − MONTHS(renewal_start, v_eff) | T3 0. T2 evaluated on T1's domain (v_eff = renewal_start) gives 12: one formula written as two tiers. FAIL.
- r_giveback: T1 SUM(amount, premium credits) | T2 SUM(amount, premium credits, reason=overpayment) | T3 0. Same field, different filter: FAIL (a parameter labelled method).

### findings
Each finding: verdict — symptom — root cause — evidence — demonstrated consequence — artifact/location — tasks it bears on.

**C1 SOURCE-POLICY RED — sibling overwrites of one base clause contradict each other (XF-8).** VTC overwrite replaced_by: "For a vision plan unit … the termination credit is settled by this policy; every other termination credit remains under the base rule, which credits the premium billed for whole coverage months after the termination month". REC overwrite replaced_by: "For an orthodontic rider … the rider credit is settled by this policy; every other termination credit, including one for a vision plan unit settled by its own policy, remains under the base rule". VTC's text puts every rider termination credit under the base rule; REC's text puts the vision-unit credit under the base rule. Neither excludes the sibling's case. Same situation, two conclusions: the base rule credits every billed month after the termination month at the billed premium, with no offset, interest, recovery or prior-credit deduction. Consequences demonstrated in task_0.md (vision credit) and task_1.md (rider credit). Location: billing.extended.yaml VTC overwrite[0].replaced_by and rule sentence 1; REC overwrite[0].replaced_by and rule sentence 1. Tasks 0, 1.

**C2 SOURCE-POLICY RED — undeclared override of base invoicing tier pricing (RNP r_vtier).** Base billing_evt_invoicing: "the monthly premium is the sum, over every applied or active plan the account funds, of that plan's monthly premium for its coverage tier". RNP: "when no child's vision enrollment is applied although the elected tier … is family or member_children, it is the plan's premium for member_spouse … ; when a child's … but no spouse's …, it is the plan's premium for member_children". RNP's only overwrite retires a credit-application sentence; nothing retires the tier-pricing sentence. Consequence demonstrated in task_1.md. Tasks 1.

**C3 SOURCE-POLICY RED (charter, no task-1 value effect) — renewal savings presuppose invoices the in-force invoicing clause cannot issue.** r_dental tier 1 fires "when a dependent's dental enrollment … ended for loss of eligibility … before the invoice issued last was issued"; r_rider tier 1 the same for an ended rider; r_vstart adds an applied vision plan. Under base billing_evt_invoicing an invoice issued after those events already bills the lower tier, no ended rider and every applied plan. Same situation, two conclusions: on any world whose renewal invoice is priced by the base clause, RNP deducts 12 × (old − new tier premium) × 0.96 and 12 × rider premium × 0.96 a second time and bills the applied vision plan twice; the tiers test the invoice's issue date, never what it billed. In task 1 the seeded renewal invoice is stale (see task_1.md O-T1-1), which is why the value there is not moved. Location: RNP rule (dental saving, rider saving, added-plan sentences).

**C4 SOURCE-POLICY RED — held bank transfer "does not count" (GCP g_hold) departs from base payment application without an overwrite.** Base billing_evt_payment_application: "A payment is applied to the oldest unpaid coverage month first". GCP: "A grace-cure payment by bank transfer is held until it clears, and a held payment is added back because it does not count". GCP's overwrites retire the threshold sentence and the AutoPay-discount sentence only. Consequence demonstrated in task_0.md. Tasks 0.

**C5 SOURCE-POLICY RED (charter, no task effect) — GCP's own overwrite scope contradicts its tiers.** Overwrite[1].replaced_by: "the discount is added back to the past-due months this policy names, and only to those months". g_next tier 2 adds "the arrangement's monthly AutoPay discount" with the invoice issued last, whose coverage month "has not yet begun" (not past due); g_disc tier 1 adds it "for the oldest past-due month and the month after it", the latter not past due when one month is past due. In task 0 g_next takes tier 1 and g_disc tier 2, so no value moves.

**C6 SOURCE-FACTOR RED — factor coupling and duplicated shared selections (XF-1, XF-2, XF-16).** (i) RNP result sentence "the premium of a plan added for the renewal year is its premium per month times its months, reduced by the prepay discount percentage" multiplies r_vtier by r_vstart: r_vtier bears weight only when r_vstart is off its fall-through (gated through another factor). (ii) VTC interest base "less the months covered by the termination credits on the vision line already deducted above", and VTC booking args "that no termination credit already deducted above covers", read vtc_prior's selection; compute uses plain `prior_months`, so under vtc_prior's baseline the words and the compute diverge (task_0.md). (iii) DTC lag base "not covered by the plan-change difference credits deducted above" and DTC booking args read dtc_dup's selection (task_1.md). (iv) REC booking months "less the months those credits cover" read rc_dup's selection. (v) Identical selections owned by two factors instead of one plain binding stated once: fee_last (g_fee) = relief_fee (g_relief), the sentence "the returned-payment fee booked last (of two booked on the same day, the one recorded first)" stated twice; last_draft_ret (g_next) = hold_ret_date (g_hold); annual_12r (rc_basis) = annual_12m (rc_months). Tasks 0, 1.

**C7 SOURCE-FACTOR RED — method ladders whose tiers coincide or are mislabelled (XF-4, XF-15).** All-pairs table above: r_vstart T1≡T2; r_giveback T1/T2 same windowed sum (a parameter); dtc_window T2 produces the fall-through's result over its whole domain (P-c); g_next T1≡T2 wherever autopay_discount_monthly is 0. Consequences: RNP and DTC have no surviving method factor (task_1.md); GCP's only method fails on three of the four in-scope arrangements (charter; task 0 is AutoPay, so its value is not moved).

**C8 SOURCE-FACTOR RED — unreal ladders (realism).** (i) g_tol: the tolerated premium shortfall is tiered by the subscriber's dental-plan tenure and deducted from the amount quoted to cure grace. A carrier's premium-payment tolerance is an arrangement-level, uniformly applied de minimis threshold (the base already has premium_payment_threshold_pct and group_underpayment_tolerance per arrangement; the federal payment-threshold rule for exchange coverage, 45 CFR 155.400(g), requires uniform application). No carrier conditions it on tenure in another product, or tells its reps to quote a short amount on purpose. (ii) dtc_basis / rc_basis tier 2: "carries a prepay discount but has issued no such invoice in that period → reduced by 50 percent of the prepay discount percentage". The months being credited were billed at the full prepay discount. The condition only measures how long ago the last annual invoice was issued, and no carrier refunds prepaid months at half the discount it charged. (iii) dtc_recover / rc_recover: the condition "the account's invoice issued last was issued one or more days after the termination date" is met by any routine next-cycle invoice or correctly priced renewal invoice. It does not tell a billing error from normal billing, so it is not a condition a carrier weighs for a flat compensation amount. (iv) r_giveback tier 1: "every premium credit booked on the account is added back" re-charges credits already consumed by earlier invoices, and adds back the credits the two RNP prerequisites just booked. P-a: in task 1's world with a confirmed refund request, the renewal payment is 1254.41 with both credits, 1254.41 skipping the dental credit and 1254.41 skipping the rider credit, so both edges stop bearing weight. Tier 2 charges the customer a standing credit now so it can be refunded separately, which is not a published treatment. Tasks 0 (i), 1 (ii–iv).

**C9 SOURCE-POLICY RED (charter; no task effect unless noted) — rule words ≠ compute, edges without a rule sentence (XF-5, XF-6).** Members listed in rule_compute_equivalence above: r_dental T2 uncomputable (P-b TypeError); g_disc "no longer carries"; vtc_month "collected" counting returned drafts; booking args without compute in VTC/DTC/REC (consequence shown per task: the scored coverage_month / months_covered rest on prose only); absent subscriber active dental enrollment unstated (crash); unstated selection/tie rules in DTC and RNP; missing month-counting sentence in RNP.

**C10 SOURCE-POLICY RED (charter) — decoy-row reads whose answer moves (XF-7).** (i) VTC ben_unit/ben_12 sum every vision service of the customer from the unit's effective date to the credit date, with no end at the termination date and no enrollment scope: P-d adds one later Cascade vision service under another enrollment dated 2026-08-20 to task 0, and the credit moves from 57.11 to 20.54. (ii) VTC req_date takes the customer's latest confirmed voluntary-termination request for any vision enrollment, not the unit's. (iii) GCP fee_last / relief_fee are unwindowed: P-e (one fee-exempt return in 12 months, last fee booked 2024-05-03) gives g_fee 25.00, which collects a two-year-old fee. (iv) GCP "automatic bank draft" is every eft return, including the holder's own bank transfers that the same rule calls "payment by bank transfer".

**C11 SOURCE-POLICY RED (charter, no task effect) — prerequisite sentences broader than their resolving write.** See prerequisite_sentences.

Observations (not grounds for rework): O1 tools do not perform the same-category paid-through trigger; O2 grace docstring purpose phrase; O3 VTC/DTC/REC flat recovery amounts are goodwill payments of a kind insurers rarely publish (C8-iii records the demonstrable part); O4 rc_months / dtc_window tiers are end/start-anchor choices of one month count.

## closing_checklist
Written after both reveals (2026-10-18T03:31Z). It does not alter the pre-reveal section above.
- Per-task files task_0.md and task_1.md correspond one-to-one with the tasks; `_difficulty.md` sits beside them. First revision, so nothing to trace.
- Both independent derivations land on GT exactly: every write, argument, owner, order, factor_sensitivity figure and baseline_result. But neither comparison carries a PASS: both tasks carry SOURCE-POLICY and SOURCE-FACTOR REDs.
- Coverage and scope: the five extended policies are fully covered by {GCP,VTC} (task 0) and {RNP,DTC,REC} (task 1). The scopes are disjoint; tools and GT are closed; uuid8s are independent.
- Trees: task 0 has 1 prerequisite problem / 1 value_input edge; task 1 has 2 / 2. Each has one owner=user root, no cycle, and the difficulty graph is acyclic. Every edge is unmet at the opening and bears weight (289.23 vs 232.12; 1147.79 and 1022.08 vs 975.80).
- Factors: every declared factor moves its scored value on its world against the declared baseline. The bounds fail once C7/C8 strike their members: DTC and RNP keep no honest method factor, and every computation of task 1 falls below 4 surviving factors. Several tiers are unreal (C8) or rest on seeded rows their owning charter cannot produce (task_0.md T0-F4; task_1.md T1-F5, T1-F6).
- Instantiation gates were not re-run (round 1; snapshot from the brief, all rc=0). A green gate does not cover C1–C11.
- Difficulty does **not** pass the source-layer audit.

Defect classes for rework, each member listed in the findings above: sibling-overwrite contradiction (C1); undeclared overrides of base invoicing / payment application (C2, C3, C4); overwrite-scope contradiction (C5); factor coupling and duplicated selections (C6); method tiers that coincide or fail the shape test (C7); unreal ladders (C8); rule ≠ compute, absent-record and tie gaps, booking args without compute (C9); decoy-moving reads (C10); prerequisite sentences broader than their single-record resolvers (C11); task-world seed rows not producible by their owning charter (T0-F4, T1-F5, T1-F6).

VERDICT revision_1: task0=RED task1=RED charter=C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11

---

## revision_2

## charter_global_frozen (revision_2)
- Re-audit round 2, independent policy auditor, frozen 2026-10-18T06:34Z, before any round-2 GT field was read. Gate protocol `/tmp/erl0070_coord/reaudit_gate.txt` followed: worklog tail = `REWORK round 2: gates 7/7 green`; claims line lists C1–C11, T0-F1…F6, T0-O1…O3, T1-F1…F8, O-T1-1…3.
- Gate snapshot, run by me with `/tmp/erl0070_coord/snapshot.sh premium_billing_and_grace 2` at 2026-10-18T06:26:55: check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire all rc=0 (OK lines). Input complete.
- Rebuilt masked views: r2/task_0.json sha256=379e08050b8a33611732899263f96d36fbb1cbfa1a38e3d2dd218e7b4948b77c; r2/task_1.json sha256=e2d510d94ef5759bc9b5bbe16078245beda96d6193ac5a72273abe6304895924. Sources: billing.extended.yaml sha256=051f6139344f19e86b05f33ab9edaed2e177147d5fd10f52cec84f32cc12abd9, task_tools.py sha256=b19f12afdf2130ae0559f2b3d67cba9d125d4f5870db20849e75533a8d418b34. Both changed since revision_1, so every charter-global section is re-derived in full below (no carry-forward).
- Scratch: `/tmp/audit_premium_billing_and_grace_0070/derive2.py` (replays every compute of the new charter on the r2 worlds) and `probes2.py` (P2-a … P2-f, hypothetical/decoy worlds).

### policy_conflict_scan (r2)
- Base copy verbatim (key-by-key equal to products/billing.yaml).
- Policies and tools unchanged in identity; trees unchanged: GCP←VTC; RNP←DTC, RNP←REC. Scopes disjoint and complete.
- Trigger rule (XF-14): tools still write only billing_premium_credit and billing_payment_received (both trigger only billing:billing_paid_through_update). CLEAN.
- Overwrites now: VTC and REC replaced_by each name the sibling's case (C1 closed). GCP: AutoPay-discount sentence (scope now "past-due months and the not-yet-begun month of the invoice issued last"), and "A payment is applied to the oldest unpaid coverage month first" retired for a held grace-cure transfer/check (C4, C5 closed). DTC unchanged. RNP: "Each invoice bills billing_frequency_months whole coverage months starting with the next unbilled month" retired for a vision plan applied after the renewal invoice; threshold sentence retired for the corrected renewal invoice; the vision plan is priced at its recorded tier (C2 closed).

### rule_compute_equivalence (r2)
- Mechanical: every compute_basis quote verbatim in its rule; every binding has a basis; every baseline.rule sentence in its rule; mechanically only `result` reads factor-owned bindings (XF-1 closure clean in all five policies).
- Closed since r1: booking args now have compute (`post_month`, `book_months`) in VTC/DTC/REC; absent subscriber enrollment and ties stated (DTC, RNP); RNP carries the month-counting sentence; r_dental's uncomputable tier removed; vtc_month "collected" now nets returned drafts.
- Remaining / new members (C9-r2): (i) g_disc T1 "its arrangement no longer carries an AutoPay discount because automatic draft was removed" — compute tests only `P('autopay_discount_monthly') == 0` plus eft history: P2-b (task 0 world re-labelled Quarterly Bill, an arrangement that accepts eft and never had an AutoPay discount or a removal rule) gives g_disc 2.00. (ii) DTC and REC book `months_covered` = whole months from the end date to the paid-through date less months already credited, while the amount covers `dtc_window` / `rc_months` months; on the grace-period and billed-through tiers these differ (P2-e: dtc_window 3 or 4 vs book_months 2), so the scored months_covered contradicts the tool's own Args text "the number of coverage months the credit gives back". (iii) "an automatic draft is a returned payment by bank draft that had paid a coverage month" / "each one that had paid a coverage month" are implemented as `months_covered=1`; a quarterly draft (months_covered 3) paid coverage months but is excluded (GCP last_draft_ret, VTC draft_rets_12 / err_rets, REC draft_rets_12r).

### action_binding_and_uuids (r2)
- Unchanged pairs and uuid8s (956578a0, 5521c4c8, 2a6e4a9b, fb22198c, 53926ce3): PASS. Docstrings: coverage_month is now "the coverage month of the invoice the credit is posted against" (matches the rules' posting sentence); no examples, no ordering words, no factor id inside a tool name; bodies validate nothing. See C9-r2 (ii) for the months_covered Args text.

### prerequisite_graph / prerequisite_sentences (r2)
- Three state-form edges, verbatim in their own rules, acyclic, resolved_by = depended-on target tool, gates `past_due` / `bal` exist, kind value_input.
- New wording: "…fixed only after the account's ledger carries a vision-line termination credit posted against the coverage month of the invoice issued last, whenever a vision plan unit the account funds ended by voluntary termination before that month" (GCP); RNP edges analogous for the dental line ("not fixed until") and rider line ("only after"). Connective, record-visible state (a credit row on a named line whose coverage month equals the last invoice's), no tool/id; exactly one write per line can bring it about, and the depended-on rule's posting sentence ("The credit is posted against the coverage month of the invoice issued last") lets the reader resolve the hop. The state is now satisfiable by the single credit each resolver books — C11 closed.

### override_declarations (r2)
- Sentence sweep repeated against every base ref: no undeclared departure found in VTC, GCP, DTC, REC. RNP: bills_old / bills_rider tests and the three savings/additions sentences now carry their own premises, but see C3-r2.

### factor_ladders (r2)
| policy | factor | effect | struct. verdict |
|---|---|---|---|
| VTC | vtc_month | parameter | T1 infers "billed on AutoPay" from eft drafts on any arrangement (C13) |
| VTC | vtc_offset | method | PASS (window now bounded at termination) |
| VTC | vtc_prior | parameter | ok |
| VTC | vtc_int | parameter | ok |
| VTC | vtc_recover | parameter | ok (request now the unit's own) |
| VTC | vtc_feeback (new) | parameter | T1/T2 one rule split by count (C12); gives back a fee never charged (C10-r2) |
| GCP | g_next | method | PASS (T2 now P(discount) only, AutoPay arrangements) |
| GCP | g_disc | parameter | rule≠compute on T1 (C9-r2 i) |
| GCP | g_fee | parameter | tiers collapse to one rule (C12, regression from the C10-iii fix) |
| GCP | g_relief | parameter | ok |
| GCP | g_hold | parameter | held selection includes a returned transfer (C10-r2) |
| DTC | dtc_window | method | PASS (prepay / grace / billed-through anchors, as rc_months) |
| DTC | dtc_dup | parameter | ok |
| DTC | dtc_int | parameter | ok |
| DTC | dtc_recover | parameter | "still bills the dropped tier" proxy fires on correctly priced invoices (C3-r2) |
| REC | rc_months | method | PASS |
| REC | rc_basis | parameter | T1 as vtc_month (C13); shares a duplicated selection with rc_months (C6-r2) |
| REC | rc_dup | parameter | ok |
| REC | rc_int (new) | parameter | ok |
| REC | rc_recover | parameter (cross vision) | proxy counts a vision plan applied after the invoice (C3-r2) |
| RNP | r_dental | parameter | bills_old proxy (C3-r2) |
| RNP | r_rider | parameter | bills_rider proxy (C3-r2) |
| RNP | r_vbinder (new) | method | T1 = span×rate×disc vs T2 = rate×disc; span ≡ 12 on every Annual Prepay renewal invoice, so the tiers differ by a constant multiplier: method-shape FAIL (C7-r2) |
| RNP | r_fee (new) | parameter | tiers collapse (C12) |
| RNP | r_relief (new) | parameter | ok |
Counts: VTC 6 (5 param / 1 method), GCP 5 (4/1), DTC 4 (3/1), REC 5 (4/1), RNP 5 (4 param / 1 "method" that fails). Cross-difficulty: vtc_offset, vtc_recover (vision); rc_recover (vision); r_dental (dental), r_rider (ortho), r_vbinder (vision). GCP and DTC declare none.
Method all-pairs: vtc_offset PASS (as r1). g_next T1 last_amt | T2 P(autopay_discount_monthly) only where P>0 | T3 0 — distinct inputs, no coincidence: PASS. dtc_window / rc_months T1 MONTHS(end, paid-through) | T2 MONTHS(end, NOW)+1 | T3 MONTHS(end, last invoice month)+span — data-selected anchors: PASS. r_vbinder T1 span·v·d | T2 v·d | T3 0 — FAIL (constant multiplier; a months count 12 vs 1 labelled method).

### findings (r2)
Round-1 items, re-checked:
- C1 CLOSED (sibling overwrites now exclude each other by name). C2 CLOSED (recorded tier). C4 CLOSED (declared overwrite of the application sentence, scoped). C5 CLOSED. C11 CLOSED.
- C3 NOT CLOSED → **C3-r2 SOURCE-POLICY RED (charter)**. The savings and re-billing amounts are now gated on "the renewal invoice bills the former tier when its amount is at least its months' premium for the former tier, reduced by the prepay discount" (RNP; DTC dtc_recover the same test). The test compares the whole invoice with the dental former-tier premium alone, so any invoice carrying other plans passes. P2-d: in task 1's world, a renewal invoice correctly priced for member_spouse dental + an active child rider + Choice 175 family vision (12×(80.92+12.60+52.77)×0.96 = 1685.26) gives bills_old True, r_dental 578.88 deducted and dtc_recover 25.00 added, although it does not bill the former tier. bills_rider / rc_recover price "the subscriber's vision enrollment" that is not terminated, including one applied after the invoice, contradicting RNP's own sentence "an enrollment applied for on or before the renewal invoice's date being billed on that invoice" (a family-tier vision unit applied after the invoice can make an invoice that does bill the rider fail the test).
- C6 PARTLY CLOSED → **C6-r2 SOURCE-FACTOR RED (charter)**: (i)–(iv) closed ("months already credited" is now a plain quantity stated once; r_vtier gone). (v) persists for REC: `annual_12m` (rc_months) and `annual_12r` (rc_basis) are the same selection owned by two factors. GCP/RNP fee selections are now plain and stated once.
- C7 NOT CLOSED → **C7-r2 SOURCE-FACTOR RED**: g_next and dtc_window fixed, r_vstart / r_giveback removed, but the replacement r_vbinder fails the method-shape test; RNP keeps no honest method factor.
- C8 (i) (ii) (iv) CLOSED (g_tol, half-discount tiers, r_giveback removed). (iii) CLOSED for REC (test now includes rider and current tiers), NOT CLOSED for DTC (C3-r2).
- C9 PARTLY CLOSED → **C9-r2 SOURCE-POLICY RED (charter)**: members (i)–(iii) in rule_compute_equivalence.
- C10 (i)–(iv) CLOSED. New member → **C10-r2 SOURCE-POLICY RED (charter)**: (a) GCP "the payment held is the account's latest grace-cure payment by check or by bank transfer" does not exclude a payment already returned; P2-c (task 0 world without the 09-19 check) holds the returned 60.00 transfer, which ret_all already adds back, so it is added twice (held_amt 60.00 on top of past_due 146.34). (b) VTC vtc_feeback adds "the arrangement's returned-payment fee" per qualifying return whether or not a fee was booked; P2-f (task 0 world with no fee rows) still gives back 25.00.
New classes:
- **C12 SOURCE-FACTOR RED — ladders whose tiers are one rule.** g_fee: T1 "every returned-payment fee booked within the whole calendar months from the grace-period start date … plus one", T2 "the returned-payment fee booked last if it counts as booked in the grace period", T3 nothing. With exactly one return in twelve months the only fee that can sit in the grace window is that return's fee (one_fee_per_return; the fee is booked with its return), so T2 = T1's formula on T2's domain; with no return in twelve months T1's formula gives 0 = T3. The return count changes nothing a business weighs; they differ only where month-granular windows reach a few days before the grace start. r_fee (RNP) is the same construction against the renewal invoice date. vtc_feeback T1 "the arrangement's returned-payment fee for each of those returns" vs T2 "that fee added once" is n×fee written as two tiers. Regression note: g_fee collapsed when its T2 was windowed to the grace period (the r1 C10-iii fix).
- **C13 SOURCE-FACTOR RED — "billed on AutoPay" inferred from eft drafts on any arrangement.** VTC vtc_month T1 and REC rc_basis T1: "when the account collected at least one regular automatic bank draft within twelve months … and fewer of its automatic drafts were returned … than it collected, the months were billed on AutoPay, and the amount per month is … less the AutoPay arrangement's monthly discount (autopay_discount_basis)…". Annual Prepay and Quarterly Bill accept eft (base variants) and never carry an AutoPay discount, and on Annual Prepay T1 pre-empts the prepay tier. P2-a: task 1's world with its annual check payments made by eft gives rc_basis 12.10 (rider premium − 1.00/2) instead of 12.096 and a credit of 174.83; P2-b: task 0's world as Quarterly Bill gives vtc_month 35.95 though no month was ever discounted. The condition does not establish what its tier asserts; no carrier refunds a discount it never gave.

## closing_checklist (revision_2)
Written after the round-2 reveals (2026-10-18T06:35:41Z); the pre-reveal r2 section above is unchanged.
- Both independent r2 derivations land on GT exactly (all writes, arguments, owners, order, sensitivities, baselines, load-bearing figures).
- Closed since r1: C1, C2, C4, C5, C11; C8 (i)(ii)(iv); C10 (i)–(iv); C6 (i)–(iv); C7 for g_next / dtc_window; C9 members on booking args, absent records, ties, month sentence, uncomputable tier; all task seed items (T0-F4, T1-F5, T1-F6) and observations O1, O-T1-1/2/3. Problem trees hold in both tasks (unmet at the opening, load-bearing, commuting parallel edges, user-owned roots, tools validate nothing).
- Still open or new (all members listed in findings (r2)): C3-r2 (invoice "still bills" proxies, DTC/RNP/REC), C6-r2 (REC duplicated selection), C7-r2 (r_vbinder method-shape FAIL → RNP has no method), C9-r2 (g_disc T1 removal not tested; DTC/REC months_covered vs credited months; "paid a coverage month" = months_covered 1), C10-r2 (held payment may be a returned one; feeback gives back a fee never booked), C12 (g_fee, r_fee, vtc_feeback tiers are one rule — g_fee a regression from the C10-iii fix), C13 (AutoPay inferred from eft drafts on any arrangement in vtc_month / rc_basis).
- Gates: round-2 snapshot (run by me) all rc=0. Difficulty does not yet pass the source-layer audit.

VERDICT revision_2: task0=RED task1=RED charter=C3-r2,C6-r2,C7-r2,C9-r2,C10-r2,C12,C13

---

## revision_3

## charter_global_frozen (revision_3)
- Re-audit round 3, frozen before any round-3 GT field was read. Gate protocol followed: worklog tail `REWORK round 3: gates 7/7 green`; claims C3-r2, C6-r2, C7-r2, C9-r2, C10-r2, C12, C13, T0-R2-F1, T0-R2-O1, T1-R2-F1, T1-R2-F2.
- Snapshot run by me (`snapshot.sh premium_billing_and_grace 3`, 2026-10-18T12:34:10): all 7 gates rc=0. Views r3/task_0.json sha256=379e0805…b77c and r3/task_1.json sha256=e2d510d9…5924 — identical to r2 (worlds and personas unchanged). billing.extended.yaml sha256=54d70546ee107f053b67a7e378b2f9f61f5de23704691b6506bd2c9b7b58b22b (changed → charter sections re-derived); task_tools.py sha256=b19f12af…8b34 (unchanged → tool/uuid section carried forward from revision_2 on that hash).
- Scratch: `derive3.py` (replay on r3), `probes3.py` (P3-a … P3-c); charter copy `/tmp/audit_premium_billing_and_grace_0070/ext_r3.yaml`.

### re-derived checks (r3)
- Base verbatim; trigger rule CLEAN (same two events); every compute_basis quote verbatim; every binding has a basis; baseline sentences in rules; mechanically no binding other than `result` reads another factor's binding; no factor id inside a tool name.
- Prerequisite graph and sentences unchanged from revision_2 (three state edges, verbatim, single resolving write each): PASS.
- Overrides: no new departure; VTC/REC sibling scopes intact; GCP/RNP overwrites as in r2 (RNP's invoicing overwrite now also states the no-discount rule for a mid-year vision start).
- Factor structure: VTC 6 (vtc_month, vtc_prior, vtc_int, vtc_recover parameter; vtc_window, vtc_offset method — vtc_feeback removed, vtc_window new with the prepay / grace / billed-through anchors); GCP 5 (g_next method); DTC 4 (dtc_window method); REC 5 (rc_months method); RNP 5 (r_vbinder method). Method all-pairs: vtc_window as dtc_window / rc_months PASS; r_vbinder T1 span·v·d vs T2 (span − MONTHS(start, v_eff))·v — T2 adds a data-selected month count and drops the discount; on T1's domain T2 would give 12·v ≠ 12·v·0.96: PASS.

### findings (r3) — round-2 items
- C3-r2 CLOSED in substance: DTC, REC and RNP now test that the invoice amount equals, to the cent, the premium rebuilt from its plans with the former tier / ended rider priced in. Residual member → **C3-r3 SOURCE-POLICY RED (charter, no task effect)**: the rebuilt premium prices "each active orthodontic rider" and the subscriber's dental and vision plans only, while base billing_evt_invoicing bills "every applied or active plan the account funds … plus ortho_monthly_premium_per_enrollee for each applied or active orthodontic rider". P3-a: task 1's world plus a child's rider applied 2026-11-02 for 2027-01-01, invoice priced per base with the stale family tier (12×(131.17+12.60+12.60)×0.96 = 1801.38) → bills_old False, r_dental 0.00 although the invoice bills the former tier. Same for DHMO plans the account funds.
- C6-r2 CLOSED (REC reads one plain `annual_12`).
- C7-r2 CLOSED (r_vbinder passes; RNP has a method factor).
- C9-r2 CLOSED: g_disc / g_fee / r_fee use "left AutoPay" = no AutoPay discount, eft not accepted, regular drafts collected (only a Direct Bill account moved by removal); months_covered = months counted less months already credited in VTC/DTC/REC; "automatic draft" covers 1, 3 or 12 months.
- C10-r2 (b) CLOSED (vtc_feeback removed). (a) PARTLY CLOSED → **C10-r3 SOURCE-POLICY RED (charter, no task effect)**: the held payment now skips a returned one, but "a payment counting as returned when the latest returned payment by the same method that had paid no coverage month is for the same amount and dated on or after its receipt" matches by amount instead of the return's original_billing_txn_id (schema: "for a returned payment, the payment returned"). P3-b: transfer A 60.00 (09-15) returned 09-18, unreturned transfer B 60.00 (09-17) → B counted as returned, held 0.00 instead of 60.00. And "its latest grace-cure payment by bank transfer that has not been returned" reads naturally as the latest among unreturned transfers, while compute takes the latest transfer and drops it if returned. P3-c: unreturned 30.00 (09-14) + returned 60.00 (09-15) → natural reading holds 30.00, compute 0.00.
- C12 CLOSED for vtc_feeback (removed) and g_fee (new ladder by how the account pays: left AutoPay → fees of 12 months; no AutoPay discount otherwise → fees of the grace period; AutoPay → none — distinct and reachable). NOT CLOSED for r_fee → **C12-r3 SOURCE-FACTOR RED**: RNP settles only an Annual Prepay account's coming-year payment, and Annual Prepay accepts eft and carries no AutoPay discount, so r_fee T1 ("the account left AutoPay", which requires an arrangement that does not accept bank draft) and T3 ("an arrangement that drafts", i.e. one carrying an AutoPay discount) can never fire for any customer who reaches this write; one reachable tier remains.
- C13 CLOSED (VTC and REC infer AutoPay billing only from a carried AutoPay discount or from drafts on an arrangement that cannot draft).

## closing_checklist (revision_3)
Written after the round-3 reveal (2026-10-18T12:38:05Z); the pre-reveal r3 section above is unchanged.
- Both r3 derivations land on GT exactly (writes, arguments, owners, order, sensitivities, baselines, load-bearing).
- Closed in round 3: C6-r2, C7-r2, C9-r2, C10-r2 (b), C12 (vtc_feeback, g_fee), C13; C3-r2 in substance. Task 0 passes all four relationships.
- Open: C3-r3 (rebuilt invoice omits applied riders and DHMO plans that base invoicing bills — P3-a), C10-r3 (held payment matched to returns by amount, not by the return's original_billing_txn_id; "latest … that has not been returned" read two ways — P3-b, P3-c), C12-r3 (r_fee T1/T3 unreachable on the only arrangement RNP serves; task 1 gold carries it).
- Gates: round-3 snapshot (run by me) all rc=0. Difficulty does not yet pass.

VERDICT revision_3: task0=PASS task1=RED charter=C3-r3,C10-r3,C12-r3

---

## revision_4

## charter_global_frozen (revision_4)
- Re-audit round 4, frozen before any round-4 GT field was read. Worklog tail `REWORK round 4: gates 7/7 green`; claims C12-r3, C3-r3, C10-r3, T1-R3-F1, T0-R3-O1.
- Snapshot run by me (`snapshot.sh premium_billing_and_grace 4`, 2026-10-18T13:14:12): all 7 gates rc=0. Views r4/task_0.json 379e0805…b77c and r4/task_1.json e2d510d9…5924 (identical to r2/r3). billing.extended.yaml sha256=6c768f34cc910208e73d8b61e52be0374b6b8cc705cb74e656bef193d3b351c4 (changed; diffed policy-by-policy against my r3 copy `ext_r3.yaml`, changed sections re-derived); task_tools.py b19f12af…8b34 unchanged (tool/uuid section carried forward on that hash). Base section verbatim.
- Scratch: `derive4.py`, `probes4.py`, charter copy `ext_r4.yaml`.

### changes found and re-derived (r4)
- VTC: standard credit now counts only billed months that have begun (baseline.rule updated, sentence in rule); vtc_window T2 now "an account in a grace period whose automatic draft … was returned on or after the grace-period start date … so every month billed after the termination month counts", T3 the begun months. Method all-pairs: T1 MONTHS(end, paid-through) | T2 months billed through the last invoice | T3 MIN(months billed, MONTHS(end, NOW)+1) — distinct anchors / an added MIN: PASS (observation: T2 and T3 agree whenever every billed month has begun, e.g. a credit date before the next invoice is cut). The T2 condition is the same draft-returned-in-grace test as GCP g_next T1, so the month GCP collects is the month VTC credits.
- GCP: the held payment is now "take the account's latest grace-cure payment by check and its latest by bank transfer …; set aside either one that a returned payment on the account names as the payment it returns, without taking an earlier payment of that kind in its place" — compute uses COUNT of returns with original_billing_txn_id = the payment's id. Explicit and link-based.
- DTC: new factor dtc_basis (parameter): T1 prepay discount, T2 exchange account with APTC — (former-tier premium − APTC)⁺ − (current-tier premium − APTC)⁺, T3 tier difference. Checked against base billing_evt_invoicing (net of APTC on the whole monthly premium): an exchange account can fund only exchange dental PPO enrollments (riders, vision and DHMO are sold in individual/group markets only), so the dental plan is its whole premium and the two nettings coincide. PASS. Lag interest base now states the prepay reduction itself.
- DTC / REC / RNP rebuilt-invoice tests now price riders "active or applied" and the subscriber's DHMO enrollment applied on or before the invoice; RNP's r_fee removed, returned-payment fees moved into the balance due (baseline.rule updated).
- Mechanical sweep: compute_basis verbatim; every binding has a basis; baselines in rules; only `result` reads factor bindings; trigger rule CLEAN; prerequisite graph and sentences unchanged (PASS). Factor counts: VTC 6 (4/2), GCP 5 (4/1), DTC 5 (4/1), REC 5 (4/1), RNP 4 (3/1); every ladder 3 reachable tiers; cross-difficulty: vtc_offset, vtc_recover, rc_recover (vision), r_dental (dental), r_rider (ortho), r_vbinder (vision).

### findings (r4) — round-3 items
- C12-r3 CLOSED (r_fee removed; fees are part of the balance due).
- C10-r3 CLOSED (link-based returned test; single reading).
- C3-r3 CLOSED for the members reported (P4-a: the P3-a world now gives bills_old True). Residual member → **C3-r4 SOURCE-POLICY RED (charter, no task effect)**: the new sentence "riders of one plan applied for after the invoice's date being those applied on the latest application date of that plan when that date is later than the invoice's date and being left out" defines the post-invoice riders as only the latest-dated group of that plan. P4-b: task 1's world plus two Child 1500 riders applied 2026-11-18 and 2026-11-20 (both after the 2026-11-17 invoice) → the 11-18 rider is priced in, bills_old False, r_dental 0.00 and dtc_recover 0.00 although the invoice bills the former tier. Same wording in DTC, REC and RNP.

## closing_checklist (revision_4)
Written after the round-4 reveal (2026-10-18T13:16:46Z).
- Both tasks' r4 derivations land on GT (one auditor arithmetic slip on the DTC baseline_result recorded in task_1.md; GT correct). Task 0 and task 1 pass all four relationships: policy self-consistent on their worlds, problem trees hold (1 and 2 prerequisites, value_input, user-owned roots, unmet at the opening, load-bearing, commuting), every factor bears weight against an honest baseline with 3 reachable distinct tiers, unique solution.
- Coverage/scope: five extended policies covered by two disjoint trees; tools/uuids frozen and distinct; graph acyclic. Per task: multi-source and cross-difficulty factors present (task 0 vision; task 1 dental/ortho/vision).
- Gates: round-4 snapshot (run by me) all rc=0.
- Open charter item: C3-r4 (post-invoice riders defined as the latest-dated group of a plan only — P4-b). No other open finding.

VERDICT revision_4: task0=PASS task1=PASS charter=C3-r4

---

## revision_5

## charter_global_frozen (revision_5)
- Re-audit round 5, frozen before any round-5 GT field was read. Worklog tail `REWORK round 5: gates 7/7 green`; claims: C3-r4.
- Snapshot run by me (`snapshot.sh premium_billing_and_grace 5`, 2026-10-19T07:16:06): all 7 gates rc=0. Views r5 task_0 379e0805…b77c, task_1 e2d510d9…5924 (unchanged since r2). billing.extended.yaml sha256=ebe90c03f4d71ed4e0a53eec3cd21e210207dd7bc8de264ee4f3824056d25add (changed); task_tools.py b19f12af…8b34 unchanged (tool/uuid section carried forward on that hash).
- Diff against my r4 copy (`ext_r4.yaml` → `ext_r5.yaml`): base section identical; VTC and GCP unchanged; in DTC, REC and RNP only the rebuilt-invoice reading changed (rule sentence, `*_inscope` / `inscope` binding gating billed_old / bills_rider, compute_basis entries for it). All other sections carried forward from revision_4 on that diff.

### C3-r4 re-check
- New wording (DTC/REC/RNP): riders "applied for after the invoice's date being left out", and "This reading … is made only on an account on which, for each orthodontic rider plan, the applied riders of that plan were either all applied for on or before the invoice's date or all applied for on one date …; on any other account the invoice is not taken to have billed the tier before the drop [the ended rider] and no re-billing amount is added" (RNP: "neither the dental saving nor the rider saving is deducted").
- Rule ↔ compute: the scope binding tests, for each of the six rider plans (all six enumerated in every copy), "no applied rider, or latest applied date ≤ invoice date, or every applied rider on the latest date"; inside that scope the priced set leaves out exactly the riders applied after the invoice; outside it the stated residue outcome is computed (bills_old / bills_rider False). Rule words == compute; the residue has a single stated, computed answer.
- P4-b rerun (two Child 1500 riders applied 2026-11-18 and 2026-11-20): out of scope → bills_old False, r_dental 0.00, dtc_recover 0.00 — now exactly what the rule states, not a misreading. P4-a (applied before the invoice): bills_old True.
- XF-1/XF-2: in DTC and REC the scope binding is owned by dtc_recover / rc_recover only; in RNP `inscope` is a plain binding stated once and read by r_dental's and r_rider's bindings. Mechanical sweep: compute_basis verbatim, every binding has a basis, only `result` reads factor bindings.
- **C3-r4 CLOSED.** No new defect found; nothing regressed (task replays unchanged, below).
- Observation O-r5-1 (realism, not a red): on an out-of-scope account whose renewal invoice is stale, RNP takes no saving, so the holder is charged the stale invoice. This is the stated residue routed by the coordinator.

## closing_checklist (revision_5)
Written after the round-5 reveal (2026-10-19T07:17:07Z).
- Per-task files and `_difficulty.md` correspond one-to-one; revisions 1–5 traceable, old text untouched; both comparison sections carry PASS.
- Five extended policies fully covered by two disjoint trees ({GCP ← VTC}, {RNP ← DTC, RNP ← REC}); task tools and GT closed; uuid8s independent and frozen.
- Trees: 1 and 2 prerequisite problems, all value_input, user-owned roots, unmet at the opening, load-bearing, no cycle; difficulty graph acyclic.
- Factors: VTC 6, GCP 5, DTC 5, REC 5, RNP 4; each has ≥2 parameter and ≥1 method factor passing the method-shape test; every ladder has 3 reachable distinct tiers stated in its rule; every factor bears weight on its world against an honest baseline, and the all-baseline number differs from gold; multi-source and cross-difficulty factors in both tasks (task 0 vision; task 1 dental, ortho, vision).
- Gates re-run on the final form: round-5 snapshot (run by me) all 7 rc=0.
- Open findings: none. Observation O-r5-1 recorded.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

---

## revision_6

## charter_global_frozen (revision_6)
- Re-audit round 6 (rework input: renderer pre-scan `audits/render_source/premium_billing_and_grace/render_r1.md`, findings 1–8), frozen before any round-6 GT field was read. Worklog tail `REWORK round 6: gates 7/7 green`; claims render_r1-1 … render_r1-8.
- Snapshot run by me (`snapshot.sh premium_billing_and_grace 6`, 2026-10-19T08:47:48): all 7 gates rc=0. Views r6 unchanged (379e0805…b77c, e2d510d9…5924). billing.extended.yaml sha256=11a9b88f97da1991f0c609c3475482fd1f1fababb61eafe8c24f3d5652f1204a (changed); task_tools.py b19f12af…8b34 unchanged (tool/uuid section carried forward).
- Diff r5 → r6 (`ext_r5.yaml` → `ext_r6.yaml`, `diff_r5_r6.txt`): base identical; changes only in the sentences/bindings named by findings 1–8 (VTC window sentence; GCP g_fee, g_relief; DTC/REC/RNP dependent selection, invoice reading, scope sentence, window sentences; RNP r_relief). Mechanical sweep on r6: compute_basis verbatim, every binding has a basis, baselines in rules, only `result` reads factor bindings; every ladder 3 tiers; counts unchanged (VTC 6, GCP 5, DTC 5, REC 5, RNP 4). Scratch: `derive6.py`, `probes6.py`.

### render_r1 findings, each probed with its quoted example
| # | item | r6 change | probe (P6-n) | status | should this audit have caught it? |
|---|---|---|---|---|---|
| 1 | g_fee T2 "on or after the grace-period start" vs month window | T2 now "the returned-payment fee booked last is collected when it counts as booked in the grace period" (date test `DAYS(gstart, fee) ≥ 0`) | Quarterly account, grace 2026-08-01, payment 2026-10-19, fee 2026-07-28 → g_fee 0.00 (fee not in grace) | CLOSED | Yes. In revision_2 (C12) I noted the T1/T2 windows "differ only where month-granular windows reach a few days before the grace start" and did not record it as an XF-5 inclusive/exclusive-bound mismatch. |
| 2 | g_relief "before its grace period" vs month counts | rule now states the counting itself ("both counted the way a record counts as falling within a number of months … so a return in the last days of the month before the grace-period start counts with the latter, and one dated exactly twenty-four whole months before the payment date with neither") | (a) return 2024-09-30 → rets_before 0, relief 12.50; (b) return 2026-07-28 → counted in the grace window, relief 12.50 — both exactly as the rule now says | CLOSED (rule == compute) | Yes (same XF-5 class). |
| 3 | r_relief lookback vs invoice-date window | same restatement for the renewal invoice | invoice 2026-08-17, payment 2026-10-19, return 2026-08-10 → 1 − 1 = 0, relief 25.00, as the rule now states | CLOSED | Yes (same class). |
| 4 | active riders applied after the invoice priced in | scope sentence now covers "its active riders and, separately, its applied riders"; compute leaves out the latest-dated active group when later than the invoice | task 1 world + active Child 1500 rider applied 2026-11-20 (after 2026-11-17 invoice) → in scope, act_r 0.00, bills_old True, r_dental 578.88, DTC 25.00 / REC 10.00 re-billing kept | CLOSED | Yes. In revision_3/4 I probed applied riders only (P3-a, P4-b), not active riders whose application post-dates the invoice. |
| 5 | prepay branch with no paid-through date unstated | VTC/DTC/REC window sentences add "an account with no paid-through date on record being taken under the cases that follow instead" | task 1 world, paid-through cleared → dtc_window 25 = std (falls through), rc_months 25 — as stated | CLOSED | Yes (XF-6 absent-record member; I checked absent-record cases of the selection bindings but not of this branch's paid-through read). |
| 6 | "the dependent" not filtered by relationship | dependent = "the subscriber's child, spouse or domestic partner"; per-relationship XLATEST with child-first tie | task 1 world + subscriber's own LOE enrollment ended 2026-03-31 → dep_end / dd_end stay 2025-11-30 (Gabriel), qd_tier family | CLOSED | Yes. I considered it in revision_1 ("would include a subscriber … LOE, subscriber can't be LOE usually") and dismissed it instead of recording an XF-7 decoy member. |
| 7 | vision enrollment "funded by the account" missing in the invoice reading | words added in DTC/REC | wording only (compute already filtered by the account) | CLOSED | Yes (XF-5 wording member; I did not re-scan the invoice-reading sentences added in r3–r5 sentence by sentence). |
| 8 | REC current tier without selection/tie rule | "its current tier being the coverage tier recorded on the subscriber's active dental enrollment funded by the account with the latest coverage effective date (of two, the one recorded first)" | wording only | CLOSED | Yes (XF-6 tie member; same re-scan gap). |

### new-defect / regression scan (r6)
- The renderer's classes were re-swept over every sentence of all five rules: remaining month-count windows all state their counting in the rule (anniversary sentence; "booked since … when the whole calendar months …"); RNP "counts as booked since the renewal invoice when its date is on or after that invoice's date" is a date test in compute too; every XLATEST that picks a person or plan has its relationship filter and tie rule stated (vision unit, subscriber dental, departed dependent, ended rider, subscriber vision and DHMO enrollments); absent paid-through / absent record cases stated in every window and interest base. No new member found.
- Task replays unchanged (below). No regression.
- Observation O-r6-1 (realism, not a red): g_fee T2 now collects only the last fee booked in the grace period, so a second fee in the same grace period (two returned checks on a non-drafting arrangement) is left out of the cure amount. Observation O-r6-2: g_relief / r_relief now spell out month-count artefacts as policy (a return a few days before the grace start or the renewal invoice counts "with the latter") — explicit and computable, if unusual wording for a published rule.

## closing_checklist (revision_6)
Written after the round-6 reveal (2026-10-19T08:49:47Z).
- render_r1 findings 1–8 all closed (each probed with its quoted example); no new member of their classes in a full re-sweep; no regression; both tasks land on GT exactly and pass all four relationships. Gates (round-6 snapshot, run by me) all rc=0.
- Self-assessment: all eight findings were within this audit's remit (XF-5 bounds 1–3, decoy/active-rider 4, absent-record branch 5, unfiltered selection 6, wording/tie 7–8); 1 and 6 were noticed and wrongly dismissed, 4/7/8 came from not re-sweeping sentences introduced in rounds 3–5 sentence by sentence.
- Observations O-r6-1, O-r6-2 recorded; no open finding.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

---

## revision_7

## charter_global_frozen (revision_7)
- Re-audit round 7 (rework input: KB audit items KB-B0-1 / SRC-1 in `audits/policy_kb/premium_billing_and_grace/`), frozen before any round-7 GT field was read. Worklog tail `REWORK round 7: gates 7/7 green`; claims KB-B0-1, SRC-1, R0-1.
- Snapshot run by me (`snapshot.sh premium_billing_and_grace 7`, 2026-10-19T13:14:08): all 7 gates rc=0. Views r7 unchanged (379e0805…b77c, e2d510d9…5924). billing.extended.yaml sha256=97709e531d229e8311cfdec33b3abdfd057d825df4f038d5d51b336c824dece6 (changed); task_tools.py b19f12af…8b34 unchanged.
- Diff r6 → r7 (`ext_r6.yaml` → `ext_r7.yaml`): base identical; only VTC changed — the unit sentence, the benefits sentence, two new plain bindings `v_all` / `v_acct` owned by vtc_offset, and a guard on `vtc_offset`. GCP, DTC, REC, RNP identical (carried forward from revision_6 on that diff). Mechanical sweep on r7: compute_basis verbatim, every binding has a basis, baselines in rules, only `result` reads factor bindings. Scratch: `derive7.py`, `probes7.py`.

### SRC-1 / KB-B0-1 at source
- New unit sentence: "The vision plan unit is the plan unit of the subscriber's vision enrollment funded by the account that shows a voluntary termination, that is every vision enrollment of the subscriber funded by the account, the subscriber's own and each enrollee's, which share that enrollment's plan, coverage tier and dates and are read from it …" — agrees with vision.yaml vision_agg_shared_plan ("All vision enrollments of one subscriber funded by the same billing account form one plan unit").
- New benefits sentence: "the vision benefits paid are the plan payments on the vision services of the unit, that is of every enrollment in it, … ; the services are read from all of the subscriber's vision claims, so the benefits paid are counted only when every vision enrollment the subscriber holds is funded by the account, and when the subscriber also holds a vision enrollment funded by another account no offset is deducted." Compute: `vtc_offset = 0 if v_all != v_acct else …` with customer-scoped XSUM.
- Whose claims count is now stated (the unit = every enrollment of the subscriber on the account), and on this world it equals the compute: all five vision rows of the subscriber are on the account (v_all = v_acct = 5), benefits 370.00, offset 79.76 — the household reading I derived in revision_1. The narrow reading KB-B0-1 adopted (subscriber enrollment only, 45.00 → credit 154.32) is no longer available. **SRC-1 CLOSED at source** (the KB doc KB-B0-1 itself is a render item outside this audit's write domain; the source it must carry is now unambiguous).
- Self-assessment: I should have caught this. Revision_1 observation T0-O2 recorded exactly this ambiguity (subscriber-enrollment reading → offset 0, credit 128.37 then) and I filed it as an observation because I judged the household reading "favoured"; a second defensible reading with a different scored value is a SOURCE-TASK RED by this skill's own test.

### new-defect scan (r7)
- **C-r7-1 SOURCE-POLICY RED (charter, no task effect)** — "when the subscriber also holds a vision enrollment funded by another account no offset is deducted" vs compute `v_all = XCOUNT('vision','vision_plans')` (every vision record of the customer, any status, any date). P7-a: task 0's world plus a vision enrollment of the subscriber that ended by voluntary termination on 2021-12-31 on an earlier, closed billing account (producible: the 12-month lockout had long run and the individual-market family allows a new account once the old one is closed) → v_all 6 ≠ v_acct 5 → offset 0.00, credit 154.32 instead of 74.56. "Holds" reads naturally as a current enrollment; the compute counts a terminated one from years before, whose claims could never fall inside this unit's window anyway. Two readings, two credits.
- Observation O-r7-1: P7-b (a paid claim dated 2025-10-27 under a non-unit enrollment on the same account) would be counted by the month-granular window (credit 29.56) though the rule now says "services of the unit"; under the vision charter no such claim can exist (a second enrollment of the subscriber on the same account is in the unit by vision_agg_shared_plan; a voluntary predecessor is locked out for 12 months; a cancelled application carries no paid claim), so recorded as an observation.
- Observation O-r7-2 (realism): a subscriber who also holds a current vision enrollment on another account gets no offset at all — a stated residue, coarse but explicit.
- Task replays unchanged (task 0 74.56 / 267.62; task 1 682.15 / 174.77 / 337.15, every sensitivity as revision_6). No regression in GCP/DTC/REC/RNP (byte-identical).

## closing_checklist (revision_7)
Written after the round-7 reveal (2026-10-19T17:06:43Z).
- SRC-1 closed at source (unit = every vision enrollment of the subscriber on the account, as the vision charter's plan unit; benefits = that unit's services; compute agrees on every charter-producible world except C-r7-1's). Both tasks land on GT exactly and pass all four relationships; gates (round-7 snapshot, run by me) all rc=0; GCP/DTC/REC/RNP unchanged.
- Open: C-r7-1 (the "holds a vision enrollment funded by another account" guard counts every vision record of the customer, terminated ones on closed accounts included — P7-a, credit 154.32 vs 74.56).

VERDICT revision_7: task0=PASS task1=PASS charter=C-r7-1

---

## revision_8

## charter_global_frozen (revision_8)
- Re-audit round 8, frozen before any round-8 GT field was read. Worklog tail `REWORK round 8: gates 7/7 green`; claims C-r7-1.
- Snapshot run by me (`snapshot.sh premium_billing_and_grace 8`, 2026-10-19T18:19:02): all 7 gates rc=0. Views r8 unchanged (379e0805…b77c, e2d510d9…5924). billing.extended.yaml sha256=d97963e864d9d40dcfa2841fa35484c4dfcf0a850e87846f733e35206463998a (changed); task_tools.py b19f12af…8b34 unchanged.
- Diff r7 → r8 (`ext_r7.yaml` → `ext_r8.yaml`): base identical. VTC: guard `v_all != v_acct` replaced by `v_other` = other-account vision enrollments of the subscriber that are active, applied, or terminated within the unit's window (month-count test), with the benefits sentence restated accordingly and "a cancelled enrollment carries no services and is not counted". DTC/REC/RNP: wording only — "not terminated" → "applied or active (neither terminated nor cancelled)" for the subscriber's DHMO / vision enrollment (compute unchanged; its `termination_reason='not_terminated'` filter already excluded terminated and cancelled rows, which carry another reason). GCP identical. Mechanical sweep: compute_basis verbatim, every binding has a basis, baselines in rules, only `result` reads factor bindings. Scratch: `derive8.py`, `probes8.py`.

### C-r7-1 re-check
- P7-a rerun (subscriber's vision enrollment ended by voluntary termination 2021-12-31 on a closed account): now not counted (terminated outside the window) → credit 74.56. The rule now names the statuses it counts; "holds" is gone. **C-r7-1 CLOSED** as reported.

### exhaustive status / ownership decoy battery (P8, every person/plan/ledger read of the five policies)
Task 0 world (VTC base 74.56, GCP 267.62):
| read | decoy | result | verdict |
|---|---|---|---|
| vt_* unit (subscriber, voluntary, account) | older voluntary unit on the same account (2024) | 74.56 | ok (latest termination chosen) |
| v_other | other-account enrollment cancelled | 74.56 | ok (stated: cancelled not counted) |
| v_other | other-account enrollment terminated before the window (2024) | 74.56 | ok |
| v_other | other-account enrollment terminated inside the window (2026-03-31, group) | 154.32 | ok — stated, and such an enrollment can carry window services |
| v_other | **other-account group vision active since 2026-08-01 (coverage starts after the unit's window)** | **154.32** | **member (C-r8-1)** |
| v_other | **other-account group vision applied, coverage from 2026-11-01** | **154.32** | **member (C-r8-1)** |
| v_other | other-account individual enrollment overlapping the unit | 154.32 | not producible (vision one-enrollment-per-person rule), ignored |
| ben_unit | denied claim after the end | 74.56 | ok |
| req_date | later withdrawn request; confirmed request on the spouse's row | 74.56 / 74.56 | ok (unit enrollment, confirmed only) |
| plan_units | active rider on another account; terminated rider on the account | 74.56 / 74.56 | ok |
| GCP ledger | returned payment on another account | 267.62 | ok (holding-scoped) |
Task 1 world (DTC 682.15, REC 174.77, RNP 337.15) — every decoy leaves all three unchanged: LOE child on another account (later end); child ended voluntarily (later); older LOE child on the account (2022); child's cancelled application; subscriber's older terminated enrollment on the account; subscriber's active enrollment on another account (later effective); rider terminated on another account (later); older terminated rider on the account (2021); cancelled rider on the account (later); active rider on another account; subscriber vision cancelled (later effective); subscriber vision terminated on the account; subscriber vision applied on another account (later effective); returned-payment fee on another account. All ok.

### findings (r8)
- **C-r8-1 SOURCE-POLICY RED (charter, no task effect) — the remaining member of the C-r7-1 class.** The rule gives the guard's purpose ("counted only when no vision enrollment of the subscriber funded by another account could carry services inside the unit's coverage window") and then equates it with "none funded by another account is applied or active", which also catches other-account enrollments whose coverage begins after the window ends and so cannot carry a single window service. Producible: after a voluntary termination the 12-month lockout bars individual vision only, so the subscriber can take Cascade group vision through an employer (group account, subscriber = the employee). P8: group vision active from 2026-08-01, or applied for 2026-11-01, on task 0's world → offset 0.00, credit 154.32 instead of 74.56. The two clauses of one sentence disagree on such a record. No other member found in the battery.
- No regression: GCP byte-identical; DTC/REC/RNP compute unchanged; task replays unchanged (task 0 74.56 / 267.62 and every sensitivity; task 1 682.15 / 174.77 / 337.15).

## closing_checklist (revision_8)
Written after the round-8 reveal (2026-10-19T18:21:00Z).
- C-r7-1 closed as reported; the exhaustive status/ownership decoy battery over all five policies (ended, cancelled, other-account, inside-window) found exactly one remaining member, C-r8-1. Both tasks land on GT exactly and pass all four relationships; gates (round-8 snapshot, run by me) all rc=0; no regression.

VERDICT revision_8: task0=PASS task1=PASS charter=C-r8-1

---

## revision_9

## charter_global_frozen (revision_9)
- Re-audit round 9, frozen before any round-9 GT field was read. Worklog tail `REWORK round 9: gates 7/7 green`; claims C-r8-1. Coordinator route (logged decision): the guard is an exact, coarse, stated record test; judged here for rule words == compute and as a coherent, realistic stated residue.
- Snapshot run by me (`snapshot.sh premium_billing_and_grace 9`, 2026-10-19T18:33:45): all 7 gates rc=0. Views r9 unchanged. billing.extended.yaml sha256=a57d1adc9100a391660209b51d6f05694d6e175fad104b5078f969c05270df88 (changed); task_tools.py b19f12af…8b34 unchanged.
- Diff r8 → r9: base identical; only VTC's guard sentence and `v_other` changed. New rule: "… so the benefits paid are counted only when no vision enrollment of the subscriber other than a cancelled application has ever been funded by another billing account; otherwise no offset is deducted." Compute: `v_other` = (all vision records of the customer − status cancelled) − (those on the account − status cancelled); `vtc_offset = 0 if v_other > 0`. GCP/DTC/REC/RNP byte-identical. Mechanical sweep clean. Scratch: `derive9.py` (probes P9 inline).

### C-r8-1 re-check and the new guard
- The purpose clause is gone; the guard is a pure record test, so the round-8 disagreement between its two clauses cannot recur. P9-d (other-account group vision active from 2026-08-01) and P9-c (other-account voluntary enrollment ended 2021 on a closed account) now give no offset (credit 154.32) — exactly what the rule says. **C-r8-1 CLOSED.**
- Coherence/realism: the residue is coarse (any non-cancelled vision enrollment of the subscriber ever funded by another account forgoes the offset) but coherent with its stated reason (the offset reads every vision claim of the subscriber, so the carrier forgoes it whenever any of those claims could belong to another account's coverage) and conservative toward the member (the credit can only be larger). Accepted as a stated residue (observation O-r9-1).
- Rule words vs compute, probed per status: P9-a other-account withdrawn application (status cancelled, reason application_withdrawn) → not counted, offset kept, 74.56 — matches "other than a cancelled application". **P9-b other-account plan returned in the free-look period (vision lifecycle "active → cancelled … coverage is void from the start", reason free_look) → compute does not count it (status cancelled), offset kept, 74.56; the rule's exception covers only "a cancelled application", and a free-look return is a plan that was issued and active, not an application — read literally it is a non-cancelled-application enrollment once funded by another account, giving no offset, 154.32.** P9-e (same-account free-look return) moves nothing.

### findings (r9)
- **C-r9-1 SOURCE-POLICY RED (charter, no task effect)** — rule words ≠ compute on free-look returns: the exception "other than a cancelled application" vs compute excluding every `status='cancelled'` record, which per vision.yaml also covers "An individual subscriber returns the plan within the free-look period". Producible (a 2019 plan returned under free look on an earlier account). P9-b: 74.56 (compute) vs 154.32 (literal rule). No other member: the guard's only read is this count; all other status/ownership reads were battery-tested in revision_8 and are byte-identical.
- No regression: task replays unchanged (task 0 74.56 / 267.62 and every sensitivity; task 1 682.15 / 174.77 / 337.15).

## closing_checklist (revision_9)
Written after the round-9 reveal (2026-10-19T18:34:38Z).
- C-r8-1 closed; the coarse record-test guard is accepted as a coherent stated residue (O-r9-1). Both tasks land on GT exactly and pass all four relationships; gates (round-9 snapshot, run by me) all rc=0; no regression.
- Open: C-r9-1 — the guard's exception says "a cancelled application" while the compute excludes every cancelled record, free-look returns included (P9-b: 74.56 vs 154.32).

VERDICT revision_9: task0=PASS task1=PASS charter=C-r9-1

---

## revision_10

## charter_global_frozen (revision_10)
- Re-audit round 10, frozen before any round-10 GT field was read. Worklog tail `REWORK round 10: gates 7/7 green`; claims C-r9-1.
- Snapshot run by me (`snapshot.sh premium_billing_and_grace 10`, 2026-10-19T18:37:25): all 7 gates rc=0. Views r10 unchanged. billing.extended.yaml sha256=50297dc0208bd32420cb13cc9ebba028a9644e14ac4d941ce2e4fe93693519e5; task_tools.py b19f12af…8b34 unchanged.
- Diff r9 → r10: base identical; only VTC's guard sentence and its compute_basis quote changed; compute and every other policy byte-identical. New exception: "other than one whose status is cancelled (an application withdrawn before its start, an application cancelled for an unpaid binder, or a plan returned in the free-look period)" — exactly the three `→ cancelled` transitions of vision.yaml's lifecycle, and exactly the compute's `status='cancelled'` exclusion.
- Probes (P10, task 0 world, decoy enrollment on another account): withdrawn application → offset kept, 74.56; binder-unpaid cancellation → 74.56; free-look return → 74.56 (the round-9 P9-b case, now what the rule says); voluntary enrollment ended 2021 on a closed account → 154.32; group vision active from 2026-08-01 → 154.32 (both as stated). Mechanical sweep: compute_basis verbatim, every binding has a basis.
- **C-r9-1 CLOSED.** No new defect; no regression (task replays unchanged: task 0 74.56 / 267.62 and every sensitivity; task 1 682.15 / 174.77 / 337.15).

## closing_checklist (revision_10)
Written after the round-10 reveal (2026-10-19T18:37:53Z).
- C-r9-1 closed; no open finding. Both tasks land on GT exactly and pass all four relationships (policy self-consistency, problem tree, factor weight, unique solution); five policies covered by two disjoint trees; tools/uuids frozen; gates (round-10 snapshot, run by me) all rc=0; no regression. Observations O-r5-1, O-r6-1, O-r6-2, O-r7-1, O-r7-2, O-r9-1 stand as recorded.

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN

---

## revision_11

## charter_global_frozen (revision_11)
- Seed-only re-audit round 11 (rework input: KB re-judge items SRC-R3-1..3, `audits/policy_kb/premium_billing_and_grace/_difficulty.md` revision_3), frozen before any round-11 GT field was read. Worklog tail `REWORK round 11: gates 7/7 green`; claims SRC-R3-1, SRC-R3-2, SRC-R3-3.
- Snapshot run by me (`snapshot.sh premium_billing_and_grace 11`, 2026-10-20T06:17:35): all 7 gates rc=0. billing.extended.yaml sha256=50297dc0208bd32420cb13cc9ebba028a9644e14ac4d941ce2e4fe93693519e5 and task_tools.py sha256=b19f12afdf2130ae0559f2b3d67cba9d125d4f5870db20849e75533a8d418b34 — both as required (unchanged since revision_10), so every charter-global section carries forward from revision_10 on those hashes. Views changed: r11/task_0.json sha256=852c7a55cf6df3ac1ec4d029325e7f5e876d9403ef0ab8ca0f3302b27c07dac9, r11/task_1.json sha256=12ce698fe63a522889261a20ba04433887dc9fcd72a64173bfe1cbfebd87bc53. Scratch: `derive11.py`.

### seed items (charter-side reading of each changed row)
- SRC-R3-1 (task 0 frames `38308cc5…` Lucia, `d1840869…` Mateo: plan_paid 65.00 → 90.00, member_paid 124.00 → 99.00): blueprint vision.yaml's Select 130 `oon_frame_reimbursement` is 65.00 with no child amount; the 90.00 children's out-of-network frame amount is the vision product's published amount cited by the KB re-judge (`childrens_out_of_network_frame_amount_2a99675d`, from the vision difficulty's extended policy, which my read domain excludes). Accepted on that citation; retail 189.00 = plan 90.00 + member 99.00 consistent. CLOSED (per the cited owning-product rule).
- SRC-R3-2 (task 1 vision `08852f82…`, `c1a26c05…`: application_date 2026-11-20 → 2026-12-02, frozen_time 2026-11-24 → 2026-12-04, persona "applied this week, on December 2"): vision.yaml "Individual applications take effect on the first day of the month following receipt" → 2026-12-02 gives 2027-01-01 = the recorded effective date. Producible now. CLOSED.
- SRC-R3-3 (task 0 riders `99429870…` active, `1da95e2f…` withdrawn: rider_effective_date 2025-06-01 → 2026-01-01): ortho.yaml `ortho_add_occasions = with_dental_enrollment_or_benefit_period_start`; the attached dental enrollments' benefit period starts 01-01, so 2026-01-01 is a permitted occasion (applications 2025-05-12, children aged 12 and 9, within the age gate; Mateo's withdrawn 2025-05-20 before its start). Billing rows moved with it: 2025-07..10 invoices/payments 106.66 (= 107.66 dental family − 1.00 AutoPay), 2025-11..12 142.94 (+ 36.28 vision), from 2026-01 156.34 (+ 13.40 rider); balance_due 332.68 still equals the ledger. CLOSED.

## closing_checklist (revision_11)
Written after the round-11 reveal (2026-10-20T06:19:12Z).
- SRC-R3-1..3 closed (SRC-R3-1 on the KB re-judge's citation of the vision product's children's out-of-network frame amount, outside my read domain; SRC-R3-2 and SRC-R3-3 verified against vision.yaml / ortho.yaml). Every changed seed row checked; ledgers reconcile; prior credits reproducible; personas consistent.
- Both tasks re-derived blind on the changed worlds and land on GT exactly (task 0: 24.56 / 317.62; task 1: 684.53 / 175.37 / 334.17); every edge unmet at the opening and load-bearing; every factor bears weight; no stale proof text; charter and tools unchanged (hashes as required); gates (round-11 snapshot, run by me) all rc=0.

VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN
