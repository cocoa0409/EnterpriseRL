# Policy-task audit — cgm_sensor_supply_services / charter-global

## charter_global_frozen

- Freeze time: charter-global section written 2026-10-15 08:29–08:31:09 UTC (file mtime 08:31:09, before any task GT was opened). Auditor: erl-task-policy-audit (independent auditor, revision 1).
- Frozen inputs (sha256, re-checked against the brief before reading):
  - `tasks/cgm_sensor_supply_services/cgm.extended.yaml` 558d2b16d3218ef3c8651aa904bc28fad4961c8ed4b1cfd1199ed06437d531a4
  - `tasks/cgm_sensor_supply_services/task_tools.py` 5d8f61678079afb51c1099d426d0f472c633f6170809a9f1c671a1027d6e1ed9
  - `.audit_views/policy/cgm_sensor_supply_services/0.view.json` 55992a2b…fbfd24, `1.view.json` 58cf7f62…e2bd32 (both match the brief)
- Fields permitted: `blueprint/blueprint.yaml`, `blueprint/products/cgm.yaml` (plus `pump.yaml`, `insulin.yaml`, `bgm.yaml` for the cross-category reads), `blueprint/db_schema.json`, `blueprint/share_tools.py`, the extended charter, `task_tools.py`, and each view's `frozen_time` / `user_scenario` / `initial_state`. I also read the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` for primitive semantics (DAYS, MONTHS, within_months, LATEST, CFIELD).
- Fields masked, not read before this section was frozen: all of `tasks/cgm_sensor_supply_services/tasks/*.json` (evaluation_criteria, computations, design_rationale, solvability_contract, prerequisite_closure, charter_scope, required_documents, db_closure), the instantiator's scratch and worklog, and any other difficulty's tasks/ or audits/. I ran no recursive grep over `tasks/`.
- This section is pre-reveal by construction. Nothing in it comes from a revealed GT.
- Entry conditions (Step 0): the gate snapshot and the masked-view hashes came with the brief. Seven gates are OK. `check_traceability` is NOT OK, and the coordinator explains it as unlock tool names lacking a source until the KB is rendered (deferred to step 3). I accept that reason and cite it; I did not re-run any gate. Observation: the difficulty has not yet shown one fully green instantiation-gate run.
- Verbatim checks run on the charter (script in /tmp/audit_cgm_0063/scripts): the base copy (lines 1–1973) is byte-identical to `blueprint/products/cgm.yaml`. Every `compute_basis` value is a verbatim substring of its policy's `rule`. Every `baseline.rule` sentence appears in its `rule`. Every `superseded_clause` is verbatim in the named base rule, and every `replaced_by` is verbatim in the extended rule. Every `policy_source` is verbatim in its blocked policy's own rule.

### policy_conflict_scan

Policies (id → target tool, owner, computes):

| # | policy | target_tool | owner | computes | tier scope stated in rule |
|---|---|---|---|---|---|
| P0 | cgm_ext_renewal_authorization_units | record_order_authorization_630fe26e | agent | units_authorized | Original Medicare, grant written from a renewal order |
| P1 | cgm_ext_medicare_advance_notice_units | sign_medicare_advance_notice_77a558d1 | user | notice_units | Original Medicare ABN (CMS-R-131) |
| P2 | cgm_ext_model_change_authorization_units | record_model_change_authorization_2da97677 | agent | units_authorized | prior-auth tiers, model change under the in-force PA |
| P3 | cgm_ext_plan_member_waiver_units | sign_plan_member_waiver_eca832b6 | user | notice_units | commercial tiers, plan member waiver |
| P4 | cgm_ext_payment_plan_installment | accept_payment_plan_9d194c19 | user | monthly_amount_usd | tiers whose payment_plan_max_months > 0 |
| P5 | cgm_ext_model_change_refill_units | ship_sensor_refill_e9d57917 | agent | units | tiers with refill_confirmation_required = true |

- Overlapping subjects: P0 and P2 both write `cgm_authorization_grant`. They are separated by tier: P0 is only for the Original Medicare tier (prior_auth_required false), and P2 requires a payer PA the latest refill drew on, so it only applies on PA tiers. P1 and P3 both write `cgm_liability_notice_signed`, separated by tier (Original Medicare ABN vs commercial plan member waiver). Within its own subject, no two policies reach different conclusions in one situation.
- Cross-policy inconsistencies that cost nothing in either world (observations):
  - (a) P0 reads an over-allowance order quantity that is not a per-shipment count as "no units until the prescriber corrects the order". P2 and P3 read the same order text as "the tier's allowance".
  - (b) P0 picks the review visit treating-prescriber first, then signer. P2 picks it signer first, then program prescriber.
  - (c) P4 lets a plan take in the pump program's balance. P5 then leaves the plan's whole `installments × monthly` out of the *CGM* past-due amount, so a plan that folded in pump balance is credited against CGM past-due by the pump portion too. The base rule leaves out only "the balance it covers".
  - (d) P1's overwrite #1 `replaced_by` says "every other supply, including a commercial-tier supply covered by a plan member waiver after a CGM model change, remains under the base rule". P3 counts its waiver units by its own ladder and declares `overwrite: []`, so the two declarations disagree about whether P3's notice is a base-rule notice. Base "for that item and quantity" reads naturally as the quantity expected not to be paid, so I cannot show a second number. Observation.
- Claimed scopes: the prerequisite graph splits into two components, {P0, P1} and {P2, P3, P4, P5}. With M = 2 and one tree per task, the scopes are disjoint and jointly cover all six policies. (The task-to-scope mapping is confirmed per task in the task files.)
- Time anchors, terminal states and cross-category read boundaries: no conflict beyond the items under override_declarations and findings.

### rule_compute_equivalence

Done per policy. Every binding has a verbatim `compute_basis` (checked mechanically). I swept each tier, window, rounding and counting convention back sentence by sentence. Mismatches, each demonstrable in a constructed situation, so each is a SOURCE-POLICY RED at charter level. Neither task world triggers any of them (see the task files):

- **E1 (P5, superseded_refill_timing tier 2).** Rule: "when the latest refill's proof of delivery is dated more than the tier's carrier trace business days after it shipped". Compute: `DAYS(latest_refill_ship, latest_refill_delivered) > P('carrier_trace_business_days')`, which counts calendar days. Constructed case: ship Fri 2026-10-02, POD Wed 2026-10-07. Calendar days = 5 > 3, so compute takes tier 2. Business days after shipping (Mon–Wed) = 3, not > 3, so the rule takes the fall-through. Different earliest ship date.
- **E2 (P5, past-due window boundary).** Rule: postings "more than three calendar months before the ship date". Compute: `aged = total − SUM(within_months=3)`, and `within_months` keeps `0 ≤ MONTHS(d, NOW) < 3`. A posting dated exactly three calendar months before (same day, MONTHS = 3) is counted as past due, but the rule ("more than") excludes it.
- **E3 (P1, P5, notice reads carry no notice type), one class.**
  - P1 `prior_notice_date/units` reads the latest `cgm_liability_notice_signed` of A4239 of any type, but the rule says "An earlier advance notice for the item".
  - P5 `waiver_date/waiver_units` reads the latest notice of any type, but the rule says "a plan member waiver for the item".
  - The P5←P3 edge `condition` ("A cgm_liability_notice_signed row … notice_date on or after …") likewise drops "plan member waiver". That is a weakened condition (check 7).
  - Constructed case: a program that changed tier keeps an older ABN row and now has a plan-member-waiver row, or the reverse. Compute credits or covers with the wrong notice type; the rule does not.
- Observation: some `compute_basis` quotes are verbatim but cite a neighbouring sentence rather than the one that governs the binding. For example, P2 `order_valid_through` quotes the baseline span sentence, not the valid-through ladder. P5 `allowance`, `aged_postings`, `drawn_left` and `delivery_blocks` all quote the same two-sentence block. No empty promise and no invented basis results.
- Rounding: P4 "rounded to the cent" → `RND(…,2)`. The installment rounding ladder → cent-up / dollar-up / `RND(…,0)` on cents, then "USD with 2 decimal places". The unit policies use "as a whole number of units" → `int(…)`. All placements match.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are pairwise distinct, and each tool is claimed by exactly one policy.
- uuid8s: 630fe26e, 77a558d1, 2da97677, eca832b6, 9d194c19, e9d57917. They share no prefix or suffix and show no sequence; they look independently generated (only this module was checked; other difficulties' modules are outside the read domain).
- Docstrings: no ordering words (before/after/first), no other tool named, no sequence position, no concrete example value beyond the HCPCS enum. Every claimed effect exists in the body.
- Observation: `ship_sensor_refill_e9d57917` takes `coverage_id` and the body never uses it. `sign_plan_member_waiver_eca832b6` creates its row without the `related_cgm_order_id` key. Neither changes a scored state.
- No tool validates a prerequisite or eligibility. Every body is a straight create/update. Share tools are reads plus `verify_customer_identity` and `transfer_to_human_agent`, so no share tool writes a CGM record.
- Observation: P4's `subject` is `[cgm_patient_payment]`, but its tool writes a `cgm_requests` payment-plan row.

### prerequisite_graph

Edges (blocked ← depended-on, kind, gate, form):

- P1 ← P0, value_input, gate `drawn_units_left`, state
- P3 ← P2, value_input, gate `delivery_blocks`, state
- P5 ← P2, value_input, gate `drawn_grant_id`, state
- P5 ← P3, value_input, gate `covered_rule`, state
- P5 ← P4, state_gate, gate `uncovered_past_due`, state

Checks:
- Every policy fills `prerequisite`: P0, P2 and P4 have `[]`.
- Every `problem` names another extended policy in this file, never a base policy and never itself.
- The graph is acyclic: P0→P1; P2→P3→P5; P2→P5; P4→P5.
- Every gate binding exists in its policy's compute.
- `resolved_by` is the depended-on policy's `target_tool` on every edge.
- All edges are state form, so `fallback_reason` is correctly absent.
- No authoring-viewpoint wording ("in this task", "at the opening") appears in any `prerequisite` field.
- Defect, part of E3 above: the P5←P3 `condition` drops the waiver type the sentence names, so it is weaker than its `policy_source`.
- Observation: the P5←P4 `condition` ("A cgm_requests row of request_type payment_plan with request_status approved is on the program, so the uncovered past-due amount is below the tier's past-due hold minimum") sets an existence check beside the sentence's state. That is acceptable, because the sentence's state is the uncovered past-due amount, which only an approved plan can lower with this difficulty's tools.

### prerequisite_sentences

The four-point test, per edge:

| edge | sentence (verbatim, blocked rule) | connective | waited-on state named in record words | no tool / id / snake_case | strength = condition |
|---|---|---|---|---|---|
| P1←P0 | "The units the advance notice lists are fixed only after every written order on file for the item stands recorded as an authorization grant." | only after | orders on file / authorization grant | yes | yes ("every … order on file" = condition "Every cgm_order_receipt row … has a grant") |
| P3←P2 | "The units the waiver covers are fixed only once the newest written order of the item stands recorded as an authorization grant." | only once | yes | yes | yes |
| P5←P2 | "A refill draws no units until the newest written order of the item stands recorded as an authorization grant resting on that order." | until | yes | yes | yes |
| P5←P3 | "Blocks of a refill that begin before the latest refill's supply ends ship only after a plan member waiver for the item, dated on or after the newest written order, stands signed on the program." | only after | signed waiver, dated | yes | no: condition drops "plan member waiver" (E3) |
| P5←P4 | "A refill does not ship until the program's past-due amount, once the balance an approved payment plan on the program covers is left out, is below the tier's past-due hold minimum." | until | past-due amount, approved payment plan | yes | yes |

One write per state-form edge, derived the way a reader must:

- **"Order stands recorded as an authorization grant".** Two tools in the module can create a grant row resting on any order: `record_order_authorization_630fe26e` and `record_model_change_authorization_2da97677`. But only one depended-on rule describes that write for a given program. P0's rule writes "the authorization grant it writes from a renewal written order … on the Original Medicare tier". P2's rule writes a grant "on a tier where prior authorization is required, while the payer authorization the program's latest refill of the item drew on is still in force". So the P1 edge (an Original Medicare policy) resolves to P0 alone, and the P3 and P5 edges (P3 is commercial; P5 needs the grant under the in-force PA) resolve to P2 alone. Single reading.
- **"Plan member waiver … stands signed".** P3 is the only rule describing a plan member waiver. P1 writes ABN rows, which the sentence's type excludes; the compute does not (E3). Single reading by the rule.
- **"Past-due amount … once the balance an approved payment plan covers is left out … below the minimum".** No share or task tool posts payments, adjustments or hardship decisions. The only write that changes the left-out balance is P4's accepted plan. Single reading.
- **No second wording.** No rule restates another rule's sentence, and none names another problem's tool or id. Each depended-on rule (P0, P2, P3, P4) is silent about the blocked policy.
- **Undeclared cross-problem orders.** None in any extended rule. The base liability rule ("supplies it billable … only after the customer signs") is a base order sentence, but neither tree rests on it alone, because P3's and P1's own sentences carry the edges.
- **Observation.** P1's overwrite `replaced_by` names P3's situation in business words ("a commercial-tier supply covered by a plan member waiver after a CGM model change"). That is not an ordering, but P1's hub text will mention another problem's subject.

### override_declarations

Sentence-by-sentence findings against each `base_policy_refs` entry. Consequences are demonstrated in the task files.

- **P0.**
  - `cgm_documentation_and_authorization`: the units sentence is overwritten. The valid-from/through span is kept and the rule repeats it. Followed otherwise.
  - `cgm_continued_coverage_visits`: the base defines follow-up currency as "the most recent visit date on the program's medical records with purpose continued_need_followup or initial_qualification" (any practitioner). P0's coverage-review horizon instead picks the review visit by practitioner, and its horizon value is "the tier's follow-up visit interval". P0 calls this a coverage review, not the base follow-up requirement, so I record it as an observation (O-visit). The task 0 file shows what it would cost.
  - `cgm_evt_refill_shipment`: the next-refill-date reading matches the base timing.
- **P1.**
  - `cgm_liability_notice`: two overwrites, both declared. #1 restates the base with "the counted units" (it retires the quantity the customer wants). #2 is the BLUEPRINT-KNOWN signature route-around. On its merits, #2 keeps "personally" and "no Larkfield representative can sign it for them", and retires only the caller-statement evidence. Acceptable.
  - Observation: the base trigger list ("above the tier's allowance without supporting documentation, an item the tier does not cover, or a replacement before the payer's replacement interval") is not named, yet P1 adds a trigger "when the customer's coverage conditions for the CGM are in doubt". The base's operative test, "expected not to be paid by the payer", absorbs it, so no second number results.
  - `cgm_evt_refill_shipment`: followed.
- **P2.**
  - `cgm_documentation_and_authorization`: overwrite declared, and its `replaced_by` keeps every other payer approval under the base rule.
  - **`cgm_continued_coverage_visits`: undeclared override (finding F-POL-1).** P2's rule says "The follow-up visit requirement shortens the grant by these rules: … counted from the review visit date …" and "The review visit is chosen by practitioner: when the prescriber who signed the order has a qualifying visit on file … it is that prescriber's latest one". The base sentence fixes the visit that keeps the follow-up requirement current as the most recent qualifying visit by any practitioner. P2's own baseline repeats the base: "which the latest qualifying visit by any practitioner keeps current". So one quantity (the date the follow-up requirement lapses) gets two values, and the base sentence is not named in `overwrite`. This is the anonymous-intermediate form.
  - `cgm_evt_refill_shipment`: followed.
- **P3 (`overwrite: []`).**
  - **`cgm_evt_quantity_limits`: undeclared override (finding F-POL-2).** The base says "A sensor refill (A4239) ships sensor_allowance_units_per_30_days billing unit for every 30 days of supply". P3's baseline sentence "Each at-risk block carries the billing units per 30 days written on the newest order" gives 3 per block for an order reading 3, where the base gives 1. The ladder's tier 1 then lands back on the base value.
  - `cgm_liability_notice`: the base "that item and quantity" is compatible with an at-risk count. See observation (d) under policy_conflict_scan.
  - `cgm_evt_refill_shipment`: the payer's early-refill allowance is a new quantity, not Larkfield's lead days. No conflict.
- **P4.**
  - `cgm_evt_patient_account`: overwrite declared. Its `replaced_by` is the superseded clause verbatim plus an appended clause. It retires only the implicit "program's own balance" (observation: the overwrite retires almost nothing).
  - Base "a payment is applied to the oldest unpaid posting first": the P4 set-asides take a posting's full amount whatever was paid against it. This gives a different plan balance only when payments partly paid a set-aside posting. Observation; checked per task.
- **P5.**
  - `cgm_evt_refill_shipment`: two overwrites, declared. #1 covers timing. #2 is the BLUEPRINT-KNOWN confirmation route-around. On its merits, #2 retires nothing: the customer still confirms in the call, which is the same caller statement, and only the recorded date becomes the ship date. Harmless, no consequence.
  - **Undeclared (finding F-POL-3, class): P5's departures from inherited base sentences.**
    - (i) "The past-due amount is … posted on the program more than three calendar months before the ship date, less every payment and balance adjustment posted on it". The base measure `cgm_msr_past_due_amount` counts postings "more than past_due_hold_days calendar days before the test date": 90 on HMO/PPO, 120 on MA/Original Medicare, and on Medicaid "0 = shipments are never held for a past-due balance on this tier". P5's scope ("a tier where refill_confirmation_required is true") includes all four. Constructed cases: a PPO posting dated 2026-07-16 against a 2026-10-15 ship date is past due under the base (91 days) but not under P5 (MONTHS = 2). A Medicaid program is never held under the base but is held under P5.
    - (ii) "Only the blocks that begin on or after the end of the latest refill's supply ship" (baseline and fall-through of waiver_coverage_rule), plus "the units left on the grant it draws on divided by the tier's allowance". The base: "the supply days of a shipment are the tier's supply_days_per_shipment, shortened to the whole 30-day blocks that remain before the authorization's valid-through date when fewer remain", with units capped by the program's authorized units remaining. Constructed case: no waiver, latest supply running 66 days → base ships 90 days / 3 units, P5 ships 0.
    - Neither sentence is named in P5's `overwrite`.
  - `cgm_evt_quantity_limits` and `cgm_combo_pump_compatibility`: followed.

### factor_ladders

Structure only. Whether each factor bears weight is in each task's `factor_weight`. Legend: P = parameter, M = method. "multi" means every non-fall-through tier is a conjunction or disjunction over distinct records, judged on the rule text. Every factor's `decides` is an input (never `result`), binding sets are disjoint, every tier is stated in the rule prose and implemented as a branch, and every fall-through equals the factor's `baseline`. These were checked for all 34 factors and are not repeated below. Factor independence: no factor binding reads another factor's binding. Factor outputs are combined only in non-factor bindings (P1 `next_delivery_units` / `listed_units`, P2 `horizon_cut_blocks` / `span_blocks`, P3 `at_risk_blocks`, P5 `shipped_blocks`). No result is assembled inside a factor binding.

**P0 renewal_authorization_units.** Baseline (verbatim in the rule): "The grant carries the order's billing units per 30 days times the whole 30-day blocks from the order date through the order's valid-through date, both days counted. The grant is anchored to the order date." It is self-sufficient and definite.

| factor | label | tiers | distinct? | multi | xdiff | notes |
|---|---|---|---|---|---|---|
| span_start_anchor | M | 3 | yes | no | – | anchor/start convention, so the method label is honest |
| order_quantity_convention | M | 3 | yes | no | – | divide / none / as written |
| coverage_review_horizon | P | 3 | yes | yes (closed ∧ regimen ∧ supply-end) | insulin | **realism F-FAC-5** |
| review_visit_practitioner | M | 3 | yes | no | – | candidate order |
| regimen_change_record | P | 3 | yes | yes (bgm class ∧ bgm order; ¬t1 ∧ insulin closed) | bgm | tier 2 belongs to the F-FAC-5 class |
| refill_bridge | P | 3 | yes on domain | yes | – | obs: tier 1 (no units left → blocks) is tier 2's formula `max(0, blocks − left)` at left = 0, so one rule is split in two at the units-left boundary |

Counts: 6 factors, 3 P, 3 M, ≥1 multi, 2 xdiff (insulin, bgm). Within bounds.

**P1 medicare_advance_notice_units.** Baseline: one standard shipment listed, none at risk because the program documents a qualifying regimen. That is honest for Original Medicare: an ABN is due only when denial is expected. Definite (0).

| factor | label | tiers | distinct? | multi | xdiff | notes |
|---|---|---|---|---|---|---|
| drawn_authorization | M | 3 | yes | yes | – | |
| exposure_limited_delivery | P | 3 | yes on the Original Medicare tier (3 blocks) | no (tier 1 single) | declared null, **but it reads the bgm holding** (`EXISTS('bgm', status='active')`); obs: declaration inconsistent | |
| listed_delivery_basis | M | 3 | yes | no | – | obs: on the Original Medicare tier every refill carries a confirmation (base), so tier 2 is reachable only after a tier change from a subscription tier |
| coverage_risk_scope | M | 3 | yes | no | insulin | **realism F-FAC-5** |
| prior_notice_credit | P | 3 | yes | yes | – | anchored on the insulin closed date (F-FAC-5 class); reads any notice type (E3) |

Counts: 5 factors, 2 P, 3 M. Within bounds.

**P2 model_change_authorization_units.** Baseline: grant over the order span at the order's written units per 30 days, less whole blocks of overlapping supply, no follow-up shortening. Definite.

| factor | label | tiers | defect |
|---|---|---|---|
| review_visit_practitioner | M | 3 | carries the undeclared visit override F-POL-1 |
| prescribed_quantity_reading | M | 3 | – |
| carry_end_date_rule | P | 3 | **F-FAC-1**: tier 1 value "the order's valid-through date" = fall-through value "the order's valid-through date", so it is a two-outcome ladder. **Realism F-FAC-5b**: tier 1 records a grant under the payer's PA reference beyond that PA's valid-through date because a renewal request is pending. No supplier ships against a payer authorization past its end on the strength of an undecided request. |
| superseded_supply_overlap | P | 3 | – (ceil vs floor vs 0) |
| follow_up_horizon | P | 3 | **F-FAC-2**: P2's scope is "a tier where prior authorization is required" = HMO, PPO, MA, Medicaid, whose `followup_visit_interval_months` are 6, 12, 6, 6. "interval > 0" holds for every customer in scope, so the fall-through/baseline "no horizon" is unreachable. And "a qualifying visit is on file" holds for every program whose first PA grant was recorded, because base `cgm_continued_coverage_visits` requires an initial_qualification visit on every tier with initial_visit_lookback_months > 0, which is all PA tiers. So the ladder never divides the customers in scope. |
| approval_period_count | M | 3 | **F-FAC-2**: both tiers' second conjunct, "refills have drawn on it", holds for every customer in scope. The payer authorization *is* "the authorization grant the program's latest refill of the item drew on" (rule), so `pa_drawn > 0` always. The ladder's multi-source shape comes only from that universal conjunct. |

Counts after the tests: carry_end_date_rule and follow_up_horizon struck. Left are review_visit_practitioner M, prescribed_quantity_reading M, superseded_supply_overlap P, and approval_period_count M (flagged). That is 1 parameter < 2: **F-FAC-3**.

**P3 plan_member_waiver_units.** Baseline: "No day of the latest refill's supply counts as paid by the payer, and no early-refill allowance applies. … Each at-risk block carries the billing units per 30 days written on the newest order." The baseline gives 0 at-risk units for every customer whose latest refill was billed by claim and paid. That is the policy's whole subject (a delivery beginning while a paid supply is still running). **F-FAC-4 (straw-man baseline)**: no commercial-tier supplier treats a remitted, payer-paid refill as unpaid. Its last sentence also contradicts the inherited quantity rule (F-POL-2).

| factor | label | tiers | defect |
|---|---|---|---|
| superseded_paid_supply | P | 3 | **F-FAC-1**: tier 1 "its supply days" = tier 2 "its supply days" |
| early_refill_allowance | P | 3 | – |
| pump_change_exception | P | 3 | **F-FAC-1**: tier 2 "0 blocks" = fall-through "0 blocks" (compute literally `(0 if … else 0)`) |
| listed_quantity_reading | M | 3 | **F-FAC-4b**: its baseline (`units_per_block: order_quantity_raw`) contradicts the inherited base `cgm_evt_quantity_limits` (1 unit per 30 days). The inherited standard gives exactly the tier-1 value, so the factor's weight exists only against a baseline that is not the charter's standard. |
| payer_authorization_excess | P | 3 | **F-FAC-1**: tier 2 "0 units" = fall-through "0 units" |
| frequency_edit_rule | M | 3 | – |

Counts after the tests: early_refill_allowance P, frequency_edit_rule M, listed_quantity_reading M (flagged). That is 3 < 4 and 1 parameter < 2: **F-FAC-3**. The only cross-difficulty factor (pump_change_exception) is struck.

**P4 payment_plan_installment.** Baseline: whole unpaid balance / max months, nearest cent. Honest, definite.

| factor | label | tiers | defect |
|---|---|---|---|
| hardship_pending_carve_out | P | 3 | – (the gate calls it multi, but both conditions sit on one request row) |
| convenience_charge_carve_out | P | 3 | obs: tier 2 "standard shipping charges" exist only on the self-pay tier (base), which offers no plans (max months 0), so it is reachable only via a prior self-pay period |
| statement_cycle_window | P | 3 | **F-FAC-1**: tier 2 "no window" = fall-through "no window". **F-FAC-2**: tier 2 (remittances on a self-pay program) is unreachable, because self-pay files no claims and offers no plans. Tier 1's "not on the self-pay tier" holds for every customer in scope. |
| pump_balance_fold | P | 3 | **F-FAC-1**: tier 2 "not added" = fall-through "not added" |
| pump_plan_carve_out | P | 3 | **F-FAC-1**: tier 2 "0.00" = fall-through "0.00". Obs: the rule says "at least one installment paid for each whole calendar month since it was logged", but the compute tests `paid_sum ≥ months × monthly` over a window of `age+1` months, which can reach before the log date. |
| installment_rounding | M | 3 | – |

Counts after the tests: hardship P, convenience P, rounding M → 3 < 4: **F-FAC-3**. Both cross-difficulty factors are struck.

**P5 model_change_refill_units.** Baseline: draw on the latest refill's grant, earliest date = lead days before the latest supply end, only non-overlapping blocks, every past-due posting counts. Definite.

| factor | label | tiers | defect |
|---|---|---|---|
| drawn_authorization_choice | P | 3 | **F-FAC-2**: the fall-through "otherwise it draws on the grant the latest refill drew on" is unreachable. It requires the newest order to *be* the latest refill's grant's order (otherwise tier 2) while no grant rests on the newest order (otherwise tier 1). That is contradictory whenever the latest refill's grant row carries its `related_cgm_order_id`, which every grant does by event definition. Two live outcomes only. |
| superseded_refill_timing | M | 3 | carries E1 (business vs calendar days); xdiff pump; tier 1 is multi, tier 2 is single |
| waiver_coverage_rule | M | 3 | obs (realism, PLAUSIBLE): tier 2 reuses the units of a waiver signed *before* the newest order. Plan member waivers are signed for a specific service. |
| hardship_pending_exclusion | P | 3 | – |

Counts after the tests: 3 factors, 1 P: **F-FAC-3**.

Category reads: insulin (P0, P1), bgm (P0, P1 existence), pump (P3, P4, P5).

### findings

Each entry gives verdict, symptom, root cause, evidence, consequence, location, and the task(s) it bears on. This is revision 1, with no previous revision.

- **F-FAC-1. SOURCE-FACTOR RED (class: two tiers of one ladder select the same value).**
  - Members (complete list for the charter):
    - P2 carry_end_date_rule: tier 1 = fall-through = "the order's valid-through date".
    - P3 superseded_paid_supply: tier 1 = tier 2 = "its supply days".
    - P3 pump_change_exception: tier 2 = fall-through = 0.
    - P3 payer_authorization_excess: tier 2 = fall-through = 0.
    - P4 statement_cycle_window: tier 2 = fall-through = no window.
    - P4 pump_balance_fold: tier 2 = fall-through = not added.
    - P4 pump_plan_carve_out: tier 2 = fall-through = 0.00.
  - Evidence: each factor's `ladder` in cgm.extended.yaml and the matching compute line. For example, P3 `exception_blocks: 1 if … else (0 if pump_delivery_date > latest_refill_ship else 0)`, and P4 `pump_fold: … else (0 if CFIELD('pump','status') == 'closed' else 0)`.
  - Consequence: each is a two-outcome ladder posing as three tiers. The factor does not meet the ≥3 pairwise-distinct tier floor and is struck from the counts.
  - Bears on: task 1 (all members).
- **F-FAC-2. SOURCE-FACTOR RED (class: tier conditions that hold of every customer reaching the write, or fall-through tiers no customer in scope can reach).**
  - Members (complete):
    - P2 follow_up_horizon: interval > 0 on every PA tier; visit on file is ~universal; baseline unreachable.
    - P2 approval_period_count: "refills have drawn on it" is universal by the policy's own definition of the payer authorization.
    - P4 statement_cycle_window: "not on the self-pay tier" is universal; tier 2 is unreachable.
    - P5 drawn_authorization_choice: fall-through/baseline unreachable.
  - Evidence: the tier parameters in base `variants` (followup_visit_interval_months, payment_plan_max_months, timely_filing_days = 0 on self-pay), P2's rule "the payer authorization is the authorization grant the program's latest refill of the item drew on", and P5's compute `drawn_grant_id: newest_order_grant if newest_order_grant else ('' if newest_order_id != latest_refill_order else latest_refill_grant)`.
  - Consequence: the ladder restates the policy's scope rather than dividing its customers. Where the fall-through is unreachable, the factor's baseline describes no customer.
  - Bears on: task 1.
- **F-FAC-3. SOURCE-FACTOR RED (factor counts below bounds after the tests).**
  - P2: 1 parameter.
  - P3: 3 factors, 1 parameter.
  - P4: 3 factors.
  - P5: 3 factors, 1 parameter.
  - Bears on: task 1, all four computations.
- **F-FAC-4. SOURCE-FACTOR RED (dishonest baseline, P3).**
  - (a) The baseline "No day of the latest refill's supply counts as paid by the payer, and no early-refill allowance applies" is a straw man for any refill billed by claim and remitted. It forces 0 at-risk units for the very situation the policy exists for.
  - (b) The listed_quantity_reading baseline contradicts inherited `cgm_evt_quantity_limits`, whose standard gives the tier-1 value. That ties to F-POL-2.
  - Bears on: task 1.
- **F-FAC-5. SOURCE-FACTOR RED (realism, class: the closure of Larkfield's insulin pharmacy program is read as the end of insulin treatment).**
  - Members:
    - P0 coverage_review_horizon, tiers 1–2: "when the customer's insulin pharmacy program is closed, the CGM program documents an insulin regimen …".
    - P0 regimen_change_record, tier 2: "it is that pharmacy program's closed date".
    - P1 coverage_risk_scope, tiers 1–2: "when the customer's insulin pharmacy program is closed and its latest insulin refill's supply … ends before the next delivery date, every listed unit is at risk".
    - P1 prior_notice_credit: its anchor, "on or after the date the customer's insulin pharmacy program closed".
  - Root cause: `insulin_programs.closure_reason` includes `changed_supplier` (db_schema.json), and no tier tests it. A customer who moved their insulin prescription to a retail pharmacy lands on the "every listed unit is at risk" tier, which issues an ABN, and has their renewal grant cut to a review horizon.
  - Why no real business publishes this: an Original Medicare DMEPOS supplier would not issue an ABN or curtail authorization because the patient fills insulin elsewhere. CMS ABN rules require a genuine, specific reason to expect denial, and the CGM LCD's insulin criterion does not depend on which pharmacy dispenses the insulin.
  - **F-FAC-5b**, same realism class: P2 carry_end_date_rule tier 1 (see factor_ladders).
  - Bears on: task 0 (the tiers the task takes). The task 0 world itself is consistent: closure_reason customer_discontinued, and the persona confirms stopping insulin. So the defect is the ladder's stated condition, not the world.
- **F-POL-1. SOURCE-POLICY RED (undeclared override, P2 vs `cgm_continued_coverage_visits`).** Details under override_declarations. Bears on: task 1, demonstrated there (base reading 4 units vs ext 3).
- **F-POL-2. SOURCE-POLICY RED (undeclared override, P3 baseline sentence vs `cgm_evt_quantity_limits`).** Bears on: task 1. The base reading coincides with the gold tier there, so no second answer, but it feeds F-FAC-4b.
- **F-POL-3. SOURCE-POLICY RED (class: P5's undeclared departures).** (i) The past-due window in calendar months instead of `past_due_hold_days`, including Medicaid's "never held". (ii) The shipped supply cut to non-overlapping blocks and capped by the grant's units left, instead of the base supply-days rule. Both are demonstrated with constructed situations under override_declarations. Bears on: task 1 (checked there; neither changes task 1's scored values).
- **F-POL-4. SOURCE-POLICY RED (rule/compute non-equivalence).** E1, E2, E3 (rule_compute_equivalence), plus the weakened P5←P3 condition. Constructed demonstrations only. Bears on: task 1 (E1, E2, E3 for P5) and task 0 (E3 for P1). Both are checked in the task files and change no scored value there.
- **Observations (no consequence demonstrable).**
  - O-visit (P0's practitioner-ordered review visit vs base "most recent").
  - Cross-policy items (a)–(d).
  - Overwrites that retire almost nothing (P1 #1, P4, P5 #2).
  - P1 exposure_limited_delivery's `cross_difficulty: null` though it reads bgm.
  - P0 refill_bridge's split tier.
  - P5 waiver_coverage_rule tier 2 realism (PLAUSIBLE).
  - P4 rounding-by-payment-method realism (company-specific, plausible).
  - Unused tool arguments.
  - P4 subject mismatch.
  - The traceability gate not yet green.

## closing_checklist

Written after both reveals (2026-10-15 ~08:34 UTC). Nothing above this heading was derived from GT.

- Audit files: `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, with `_difficulty.md` alongside. Revision 1, no older revision. Each file's comparison section is present. **Not every comparison carries PASS**: task 0 is RED SOURCE-FACTOR; task 1 is RED SOURCE-POLICY and SOURCE-FACTOR.
- Coverage and scope: GT `charter_scope` is task 0 = {P0, P1} and task 1 = {P2, P3, P4, P5}. That equals the graph components derived pre-reveal, so the scopes are pairwise disjoint and jointly cover the six extended policies. Each task tool belongs to exactly one scope. uuid8s are independent (§ action_binding_and_uuids).
- Problem trees:
  - Task 0: 1 prerequisite problem, 1 value_input edge, user-owned root.
  - Task 1: 3 prerequisite problems, 3 value_input edges, 2 user-owned problems.
  - Both acyclic, and the difficulty-wide graph is a DAG. PASS.
- Factors: **not closed.** F-FAC-1, F-FAC-2, F-FAC-3 and F-FAC-4 fail P2–P5 (task 1). F-FAC-5 fails the realism of P0/P1's insulin-closure tiers (task 0). Every declared factor's sensitivity figure matches GT, so the failures concern ladder reality, counts and baseline honesty, not arithmetic.
- Policy self-consistency: **not closed.**
  - F-POL-1 is demonstrated in task 1.
  - F-POL-2, F-POL-3 and F-POL-4 are charter-global with constructed demonstrations.
- Instantiation-stage gates: not re-run by this auditor (the auditor cites and does not run them, per Step 0). The snapshot in the brief still shows traceability NOT OK, deferred to KB rendering.
- **Result:** the difficulty does **not** pass the source-layer audit in revision 1.

## revision_2

### charter_global_frozen (revision 2)

- Written before any round-2 task GT was opened. Auditor: erl-task-policy-audit, revision 2.
- Inputs (sha256 re-checked against the coordinator's round-2 brief):
  - cgm.extended.yaml 5231fb1f2f7644ff7a8906ca2c367e685972c53a82c7e3de0fe10498eace0ac5 (**changed**, so every charter-global section is re-derived in full below)
  - task_tools.py 5d8f6167… (unchanged)
  - 0.view.json 55992a2b… (unchanged)
  - 1.view.json e0557293… (changed)
- The base copy is still byte-identical to `blueprint/products/cgm.yaml`. Verbatim checks re-run: every compute_basis, baseline sentence, superseded_clause, replaced_by and policy_source is verbatim in place. `factor_shape_errors` reports none.
- Gate snapshot cited from the brief, all OK except traceability (unlock names only, KB not rendered). Not re-run by me.
- contamination_disclosure: in round 1 I read round-1 GT for both tasks. Task 0's world is unchanged, so its round-1 scored values are known to me. Task 1's round-1 GT belongs to a different world. The round-2 derivations below are recomputed from the round-2 charter and views only, and I have not opened any round-2 `tasks/*.json`.

### round-1 RED closure check (charter level)

| round-1 item | round-2 state | verdict |
|---|---|---|
| F-FAC-1 (7 duplicate-outcome ladders) | carry_end_date_rule removed (the valid-through date is now a fixed "earlier of" sentence); superseded_paid_supply removed (the baseline counts paid days when billed by claim); pump_change_exception replaced by documented_change_exception (first block / every block / none); payer_authorization_excess removed; statement_cycle_window (all recent / charges only / none), pump_balance_fold (whole balance / charges only / 0) and pump_plan_carve_out (left to collect / not yet due / 0) now have three distinct outcomes | **closed**. But see N3: a new ladder in the same family. |
| F-FAC-2 (universal conditions / unreachable fall-through) | follow_up_horizon replaced by follow_up_lapse_cut, whose fall-through is now reachable (visit current and valid-through within the interval); approval_period_count's conjunct removed; statement window's self-pay tier removed; drawn_authorization_choice removed | **not fully closed**: follow_up_lapse_cut tiers 1–2 still state "the interval is greater than 0", which holds for every customer in P2's scope (PA tiers HMO 6 / PPO 12 / MA 6 / Medicaid 6). That is the same defect type round 1 recorded for approval_period_count's universal conjunct. The ladder still divides customers through its other conjuncts, so I flag the factor rather than strike it. |
| F-FAC-3 (counts) | P2 4 factors (2 P, 2 M); P3 6 (2 P, 4 M); P4 6 (4 P, 2 M); P5 6 (2 P, 4 M) | **closed** (P3 stays ≥ 4 even if N3 strikes waiver_listing_scope) |
| F-FAC-4 (P3 straw-man baselines) | baseline now "counts as paid … when it was billed by payer claim"; units per block now follow the tier allowance (quantity reading removed) | **closed** |
| F-FAC-5 / 5b (insulin-closure realism; PA carry-past-end realism) | every P0/P1 tier now requires `closure_reason = customer_discontinued` (rule and compute: `insulin_stopped`; P1 credit anchor `insulin_closed_date` set to 9999-12-31 otherwise); the carry tier is gone | **closed** |
| F-POL-1 (P2 visit override) | P2: "The follow-up visit the grant is measured against is the one the base follow-up requirement uses: the most recent visit date …" (compute `last_visit_date`, any practitioner) | **closed**. But see N2 (a new boundary conflict). |
| F-POL-2 (P3 units per block vs quantity_limits) | P3 delivery units = blocks × allowance | **closed** |
| F-POL-3 (i) past-due window, (ii) supply days | (i) is declared in an overwrite of `cgm_holds_and_closure` in both P3 and P5 (months = past_due_hold_days / 30; "no posting counts on a tier whose past_due_hold_days is 0"); (ii) is declared in a third P5 overwrite of `cgm_evt_refill_shipment` | **closed** (now declared; Medicaid handled). See N5 for a part the replaced_by drops. |
| F-POL-4 E1 (business vs calendar days) | the POD-lag tier is replaced by "latest refill shipped as expedited_no_charge" | **closed** |
| F-POL-4 E2 (exactly-N-months boundary) | rule now "counts as past due once the whole calendar months … have passed … with the same calendar day", which matches the compute (MONTHS = N → aged) | **closed** |
| F-POL-4 E3 (notice type) | P1 `notice_type='abn_cms_r_131'`, P5 `notice_type='plan_member_waiver'`, and P5←P3 condition names notice_type plan_member_waiver | **closed** |
| obs: P1 exposure `cross_difficulty` | now `bgm` | closed |
| obs (c): plan credited against CGM past-due with pump money | P3/P5 `plan_covered` = aged CGM remittance PR − credits − hardship posting, so no pump money | closed (see N5 for the dropped "installments current") |
| obs: pump plan window | P4 rule now says "within the calendar months since that plan was logged, counted back from today and including the month it was logged", which matches the compute (`age + 1`) | closed |

### new or residual defects (charter level)

- **N1. SOURCE-FACTOR RED (factor independence, a regression).** P0 `regimen_change_date` (factor regimen_change_record) reads `insulin_stopped`, which is a binding owned by factor coverage_review_horizon (P0 compute line 98; factor bindings list). In round 1 both read the unowned `insulin_status`. No value consequence: substituting coverage_review_horizon's baseline replaces only `review_horizon_months`, and the regimen_change_record rule text restates the condition in full. The defect is structural.
- **N2. SOURCE-POLICY RED (new, constructed; P2 follow_up_lapse_cut tier 2 vs base `cgm_continued_coverage_visits`).**
  - P2: "when the interval is greater than 0 and the follow-up visit is already that interval or more before the order date, the grant carries no units until a new visit note is recorded". Compute: `MONTHS(last_visit_date, order_date) >= interval → 999`.
  - Base: a refill ships when the most recent visit "is no more than followup_visit_interval_months calendar months before the ship date, counted … with the same calendar day allowed".
  - Constructed case: PPO, visit 2025-10-06, order and ship date 2026-10-06. Base says current, so the refill may ship. P2 gives MONTHS = 12 ≥ 12, so the grant carries 0 units.
  - No `overwrite` names the base sentence. No task world sits on this boundary (task 1's visit is 2025-12-19 against order 2026-10-06, 9 months).
- **N3. SOURCE-FACTOR RED + SOURCE-POLICY (PLAUSIBLE second reading), P3 waiver_listing_scope.**
  - P3's rule defines "The units at risk are the at-risk blocks less the excepted blocks times the tier's allowance, plus, when the delivery draws on a grant other than the one the latest refill drew on, the delivery's units beyond the payer authorization's units left, never more than the delivery's units". So the excess is part of "units at risk" whenever the drawn grant differs.
  - The baseline says "The waiver lists the units at risk".
  - (a) Under that definition, tier 1 ("lists the units at risk together with the delivery's units beyond those left", compute `risk_units`) and the fall-through ("the at-risk blocks less the excepted blocks times the tier's allowance") coincide on the fall-through's domain, where excess = 0. The honest baseline value of the listed quantity is `risk_units`, which is the tier-1 value. The factor's encoded baseline `'risk_only'` drops the excess the rule's own definition includes, so the factor is decoration against an honest baseline.
  - (b) Read literally, tier 1 adds the units beyond those left on top of "units at risk", which already contain them, giving a double-counted second reading.
  - Demonstrated in task 1.
- **N4. Observation (PLAUSIBLE realism / cross-policy).** On the same facts (pump open, pump delivered after the latest refill, OLJ on or after delivery):
  - P2 superseded_supply_overlap tier 1 deducts nothing, because "the superseded supply cannot be used with the new pump".
  - P3 documented_change_exception and P5 refill_change_exception tier 1 still expect the payer to refuse every overlapping block but the first ("pump transition fill").
  - Their tier 2, an OLJ with *no* pump change, excepts every at-risk block. So the stronger documented reason gets less relief.
- **N5. SOURCE-POLICY RED (new, constructed; dropped still-in-force part).**
  - The P3/P5 ship-time test: "the past-due remittance patient responsibility … counts as covered while an approved payment plan is on the program". Compute: `COUNT(approved payment_plan) > 0`.
  - Base `cgm_evt_patient_account` (in P5's base_policy_refs, not overwritten by P5; P4's replaced_by keeps it verbatim): "while an approved plan's installments are current the balance it covers is left out of the past-due test".
  - Constructed case: a plan approved months ago with no installment paid. Base: not left out, so past due ≥ minimum and the refill is held. P3/P5: left out, so it ships.
  - Not reached in task 1 (a plan accepted in the call).
- Residual observations, unchanged from round 1:
  - O-visit in P0.
  - P1 listed_delivery_basis tier 2 and P3 waiver_listing_scope tier 2 (an unconfirmed latest refill) are reachable only after a tier change.
  - P4 convenience tier 2 is reachable only via a prior self-pay period.
  - P0 refill_bridge split.
- New observations:
  - P4 pump_balance_fold tier 2 sums all pump patient charges ever posted, not the unpaid ones.
  - The P3←P4 edge is declared `value_input`, but its gate `uncovered_past_due` acts only as a ship/no-ship switch, and P4's scored amount never enters P3.
  - P3's and P5's rules each name the other's test ("the ship-time past-due test of the model-change refill policy and of the plan member waiver policy"). That is not an ordering, but each hub names another problem's subject.
- Prerequisite graph (revision 2):
  - Edges: P1←P0 (value_input); P3←P2 (value_input); P3←P4 (value_input); P5←P2 (value_input); P5←P3 (value_input); P5←P4 (state_gate).
  - Acyclic. Every `policy_source` is verbatim, state form, with an ordering connective ("only once", "until", "only after").
  - One write per state: the new "past-due … below the minimum" sentence in P3 resolves only to P4's accepted plan, since no tool posts payments.

### closing_checklist (revision 2)

Written after both round-2 reveals (10:30:53 UTC).

- **Files and scope:** 0.md, 1.md and _difficulty.md each carry `revision_2`, with the revision-1 text untouched apart from the clerical freeze-time corrections recorded in revision 1. Scopes are pairwise disjoint and jointly complete. GT `charter_scope` is {P0, P1} and {P2, P4, P3, P5}. uuid8s are unchanged.
- **Trees:**
  - Task 0: 1 prerequisite problem, 1 value_input edge.
  - Task 1: 3 prerequisite problems, 4 value_input edges, user-owned P3 and P4.
  - The DAG holds.
- **Round-1 REDs:** closed: F-FAC-1, F-FAC-3, F-FAC-4, F-FAC-5, F-FAC-5b, F-POL-1, F-POL-2, F-POL-3, F-POL-4 (E1/E2/E3), and the missing-multi-source item. **Not fully closed:** F-FAC-2 (residual universal conjunct in P2 follow_up_lapse_cut).
- **New in revision 2:** N1 (factor independence, P0), N2 (P2 boundary vs base follow-up, constructed), N3 (P3 listing scope, reached in task 1), N5 (dropped "installments are current", constructed). N4 is an observation.
- **No regression in scored values:** task 0's GT and every sensitivity figure are unchanged from revision 1. Task 1 was redesigned, and its GT matches my revision-2 derivation.
- **Gates:** cited from the brief, not re-run. Traceability is still deferred.
- **Result:** the difficulty does **not** pass the source-layer audit in revision 2.

## revision_3

### charter_global_frozen (revision 3)

- Written before any round-3 task GT was opened. Auditor: erl-task-policy-audit, revision 3.
- Inputs (sha256 re-checked against the brief):
  - cgm.extended.yaml 6b48ed7387af224d7c49a651b2e25eabaf0d72874bc12281c078fd6fff632135 (**changed**, so every charter-global section is re-derived)
  - task_tools.py 5d8f6167… (unchanged)
  - views 55992a2b… and e0557293… (both unchanged since revision 2)
- Base copy still verbatim. Every compute_basis, baseline sentence, superseded_clause, replaced_by and policy_source is verbatim. `factor_shape_errors` reports none. No factor binding reads another factor's binding (script check). P3 and P5 carry the identical `cgm_holds_and_closure` replaced_by.
- contamination_disclosure: I know round-1 and round-2 GT for both tasks. Both worlds are unchanged since round 2. Revision-3 values are recomputed from the round-3 charter on the views (scripts t0.py, t1r3.py), so treat any agreement as a recomputation, not an independent blind answer.

### round-2 RED closure check

| item | round-3 state | verdict |
|---|---|---|
| F-FAC-2 residual (P2 follow_up_lapse_cut "interval > 0") | tiers now "the follow-up visit is current on the order date and no longer current on the grant's valid-through date" / "no longer current on the order date" / "otherwise (the visit stays current through the valid-through date)"; no universal conjunct; fall-through reachable | **closed** |
| N1 (P0 regimen_change_record read coverage_review_horizon's `insulin_stopped`) | `insulin_stopped` is no longer in any factor's bindings; it is a shared rule sentence ("The customer has stopped insulin when …") read by both factors; P1 likewise | **closed** |
| N2 (P2 stale-visit boundary vs base "no more than … same calendar day allowed") | rule: "a visit counting as current on a date when it is no more than the tier's followup_visit_interval_months calendar months before that date, counted back with the same calendar day allowed (the last day of the month when that day does not exist), as the base follow-up requirement counts it"; compute `MONTHS(date, visit) >= −N` | **closed for the same-day boundary**. A visit exactly N months before is now current. Residual at month end: see N6. |
| N3 (P3 listing / units-at-risk) | "The units at risk are the at-risk blocks less the excepted blocks times the tier's allowance; the units beyond the payer authorization are, when …, the delivery's units beyond that payer authorization's units left, and none otherwise". Tier 1 lists "the units at risk and the units beyond the payer authorization, never more than the delivery's units". Baseline: "The waiver lists the units at risk only; units beyond the payer authorization are not listed". Compute `risk_units` no longer contains the excess; P5 `shipped_units` adds the excess explicitly. | **closed**: one reading; the baseline is honest; tiers 1 and 3 differ whenever excess > 0 |
| N4 (inverted pump-change relief) | P3/P5 tier 1 (pump change + OLJ) "up to the first two at-risk blocks"; tier 2 (OLJ, no pump) "the first at-risk block only, since the superseded supply can still be used" | **closed** (now consistent in direction with P2's no-deduction tier) |
| N5 (dropped "installments are current") | P3/P5 replaced_by "counts as covered while an approved payment plan's installments are current"; compute requires payments over `age+1` months ≥ age × monthly | **closed** |
| DR(i) | (checked after reveal, in 1.md) | — |
| obs: P3←P4 edge kind | now `state_gate` | closed |
| obs: P4 pump_balance_fold tier 2 | "its patient charges, never more than its balance" (`MN(pump_balance, …)`) | closed |
| obs: P4 recent window | rule now "less than one calendar month … a posting exactly one calendar month old has already been statemented", which matches `within_months=1` | consistent |

### new defects (revision 3)

- **N6. SOURCE-POLICY RED (rule/compute non-equivalence, constructed; P2 follow_up_lapse_cut, a residual of the N2 fix).**
  - The rule adopts the base month-end convention: "(the last day of the month when that day does not exist)".
  - The compute tests currency with `MONTHS(date, visit) >= −N`. MONTHS subtracts a month whenever the later date's day is smaller, so it does not implement that convention.
  - Constructed case: HMO/MA/Medicaid (interval 6), order date 2026-08-31, last visit 2026-02-28. Rule: six months back from 2026-08-31 is 2026-02-31, which does not exist, so the cutoff is 2026-02-28; the visit is current, and the lapse-cut tier depends on the valid-through date. Compute: MONTHS(2026-08-31, 2026-02-28) = −6 − 1 = −7 < −6, so the visit is not current, which gives 999 and the grant carries **0 units**.
  - Not reached by either task (task 1: PPO, visit 2025-12-19, order 2026-10-06 → −9).
- No other new defect.
  - Factor counts: P0 6 (3 P / 3 M), P1 5 (2 P / 3 M), P2 4 (2 P / 2 M), P3 6 (2 P / 4 M), P4 6 (4 P / 2 M), P5 6 (2 P / 4 M).
  - Every ladder has three distinct outcomes, and every fall-through is reachable in scope.
- Carried-forward observations, no consequence:
  - O-visit (P0).
  - The unconfirmed-latest-refill tiers (P1 listed_delivery_basis, P3 waiver_listing_scope) are reachable only after a tier change.
  - P4 convenience tier 2 (prior self-pay period only).
  - P0 refill_bridge split.
  - P3/P5 each name the other's ship-time test in business words.
- Prerequisite graph (revision 3): P1←P0 vi; P3←P2 vi; P3←P4 sg; P5←P2 vi; P5←P3 vi; P5←P4 sg. Acyclic, all state form, all verbatim, one resolving write each.

### closing_checklist (revision 3)

Written after the reveals (10:44:26 UTC).

- All three files carry `revision_3`, with earlier revisions untouched. Scopes are disjoint and complete. uuid8s unchanged.
- Trees:
  - Task 0: 1 prerequisite problem, 1 value_input edge.
  - Task 1: 3 prerequisite problems, 3 value_input edges, user-owned P3 and P4.
  - The DAG holds.
- **Round-2 REDs closed:** F-FAC-2, N1, N2 (same-day boundary), N3, N5. Observations N4, DR(i), edge kind and pump-fold tier 2 are also closed.
- **Regressions:** none. Task 0's GT and every sensitivity are unchanged across rounds. Task 1 moved only P3 (2 → 1), as the reworker reported, and that move follows from the N4 fix.
- **New:** N6 (P2 month-end currency, rule vs compute, constructed, not reached by either task).
- Per-task relationships: PASS for both tasks.
- The difficulty does not reach `charter=CLEAN` because of N6. Gates are cited from the brief, not re-run. Traceability is still deferred.

## revision_4

### entry: gates and views (run by this auditor at the coordinator's direction, 2026-10-15 ~10:50 UTC, repo root)

Gate output lines (`| tail -1`):
- check_extended → `EXTENDED OK`
- check_task_tools → `TASK TOOL CONTRACT OK`
- check_solvability → `SOLVABILITY OK`
- check_compute → `COMPUTE OK`
- check_grounding → `GROUNDING OK`
- check_cross_fire → `SCOPE OK`
- replay_tasks --check → `REPLAY OK`

All are OK, so the audit proceeds. Traceability was not in the list (still deferred to KB rendering).

Before running `/tmp/erl0063_coord/mkviews.py cgm_sensor_supply_services` I read it. It writes only `.audit_views/policy/<difficulty>/*.view.json`, keeping frozen_time, user_scenario and initial_state, and prints hashes. Its output:
- `55992a2bbbbe6fe2e0ce9db4d7c3f68188999e92541c87acb2b80edb47fbfd24` 0.view.json (unchanged)
- `e05572938a6695b2dcff76a66e002ef20302eb8bc5cc48d6a13476a1ced82020` 1.view.json (unchanged)
- `34ea6efbca7851cbd2d281a07c1a71cae8b98ba807e41c0ef5b71026fdd731cc` cgm.extended.yaml (**changed**, so every charter-global section is re-derived)
- `5d8f61678079afb51c1099d426d0f472c633f6170809a9f1c671a1027d6e1ed9` task_tools.py (unchanged)

### charter_global_frozen (revision 4)

- Frozen before any round-4 task file or reworker note was read.
- contamination_disclosure: earlier rounds' GT is known to me, and both worlds are unchanged, so the per-task results are recomputations.
- Base copy verbatim. Every compute_basis, baseline sentence, superseded_clause, replaced_by and policy_source is verbatim. `factor_shape_errors` reports none. No factor binding reads another factor's binding.
- Counts are unchanged: P0 6, P1 5, P2 4 (2 P / 2 M), P3 6, P4 6, P5 6. Every ladder has 3 distinct tiers. The prerequisite graph is unchanged from revision 3.
- **N6: closed.**
  - P2 compute now tests currency with explicit month arithmetic: `order_months`, `order_day_later`, `visit_month_end` (a month-length table with Gregorian leap years), and `order_visit_current` / `end_visit_current` = months < N, or months = N with (the visit's day not earlier than the date's day, or the visit falling on the last day of its month).
  - Property test (/tmp/audit_cgm_0063/scripts/n6test.py): 200,000 random (visit, date, N ∈ {6, 12}) cases, checked against an independent implementation of the base rule ("no more than N calendar months before …, same calendar day allowed, the last day of the month when that day does not exist"). **0 mismatches.**
  - The revision-3 constructed case (order 2026-08-31, visit 2026-02-28, N = 6) now evaluates as current = True.
- **MONTHS / month-window class sweep: verified.**
  - Every rule now carries the definition "Whole calendar months from one date to a later date are the difference in calendar months between them, less one when the later date's calendar day is earlier than the earlier date's calendar day". This matches the DSL `MONTHS` exactly.
  - Each window phrase now states the evaluator's convention:
    - P1 "fewer than 12 whole calendar months before today" = `MONTHS(notice, NOW) < 12`.
    - P3/P5 "past due once the whole calendar months … have passed from its posting date to today" = `MONTHS ≥ N`, and "within … N whole calendar months" = `within_months = N`.
    - P3/P5/P4 plan payments "fewer whole calendar months before today than one more than the whole calendar months since it was logged" = `within_months = age + 1`.
    - P4 "recent postings are those posted less than one whole calendar month before today" = `within_months = 1`.
  - P2 keeps the base month-end convention for currency (explicitly "as the base follow-up requirement counts it") and uses the defined whole-month count only for the number of blocks removed. The two conventions are stated separately and implemented separately.
  - No rule now claims a convention its compute lacks.
- New defects: **none.**
- New observation: under P2 tier 1, a visit that lapses by days, but not by a whole month beyond the interval, removes 0 blocks. That equals the fall-through's value at that edge only. The tiers stay distinct elsewhere, and the rule's sentence ("each whole calendar month … beyond the interval removes one 30-day block") is what the compute does.
- Carried observations: O-visit (P0), the tier-change-only listing tiers, P4 convenience tier 2, P0 refill_bridge split, the cross-named ship-time test in P3/P5.

### closing_checklist (revision 4)

Written after the reveals (10:52:09 UTC).

- All three files carry `revision_4`, with earlier revisions untouched. Scopes are disjoint and complete ({P0, P1}, {P2, P4, P3, P5}). uuid8s unchanged.
- Trees:
  - Task 0: 1 prerequisite problem, 1 value_input edge, user-owned root.
  - Task 1: 3 prerequisite problems, 3 value_input edges, user-owned P3 and P4.
  - The DAG holds.
- Every computation: 4–6 factors with ≥ 2 parameters and ≥ 1 method; ladders of 3 distinct tiers stated in the rule; honest, definite baselines that differ from gold; every factor bears weight. Each task has multi-source and cross-difficulty factors (task 0: insulin and bgm; task 1: pump).
- Round-3 RED N6 is **closed**, verified by property test, and the month-convention class sweep is consistent everywhere.
- No new defect and no regression. Scored values are unchanged from revision 3, and task 0 is unchanged since revision 1.
- Instantiation gates were re-run by this auditor on the final form (see § revision_4 entry): all seven OK. Traceability is still deferred to KB rendering, per the coordinator.
- **Result:** both tasks PASS all four relationships, and the charter carries no open RED. The difficulty passes the source-layer audit at revision 4, subject to the deferred traceability gate.

## revision_5

### charter_global_frozen (revision 5)

- Frozen before any round-5 task file was read. Auditor: erl-task-policy-audit, revision 5.
- Hashes re-checked:
  - cgm.extended.yaml dc1ee441afb7aebcab7e631ff974d34aae63d42d594a452d1393d3d90cf892a6 (changed)
  - task_tools.py 5d8f6167… (unchanged)
  - views 55992a2b… and e0557293… (unchanged)
- Gate snapshot cited from the brief: all OK, now including TRACEABILITY OK.
- Additional inputs read, as permitted: `audits/render_source/cgm_sensor_supply_services/findings.md` (R-1…R-25) and the source-side sections of `audits/policy_kb/cgm_sensor_supply_services/{0,1}.md` (S-1…S-3, the renderer-findings judgement). The KB audit files quote task-1 scored values, which I already knew. contamination_disclosure: as in revisions 2–4, the per-task results are recomputations.
- Base copy verbatim. Every compute_basis, baseline sentence, superseded_clause, replaced_by and policy_source is verbatim. `factor_shape_errors` reports none. No factor binding reads another factor's binding.
- Counts: P0 3 P / 3 M; P1 2 P / 3 M; P2 2 P / 2 M; P3 2 P / 4 M; P4 3 P / 3 M (pump_balance_fold relabelled method: take in whole balance / charges only / nothing); P5 2 P / 4 M.
- Compute edits are confined to P0 `review_months_left` (`MX(0, MONTHS(…))`) and P4 (pump part branches). The N6 property test re-run gives 0 mismatches in 200,000 cases.
- **Auditor's own miss, disclosed:** R-1 (P1 overwrite[1] retiring personal signing for every notice type, with no tail) was present from round 1. My revision-1 override_declarations judged that overwrite "acceptable". That judgement was wrong.

### closure check of the source-side items

| id | round-5 charter | verdict |
|---|---|---|
| R-1 | P1 overwrite[1] replaced_by now ends "every other notice remains under the base rule, the customer signing it personally, and no Larkfield representative can sign it for them" | closed |
| R-2 / R-3 | "the paid-supply end is the latest refill's ship date plus its paid supply days, less the early-refill allowance" is now a stated (baseline) definition; the frequency ladders test "against the paid-supply end". The combination sits in non-factor `paid_end_offset`. | closed (composition named in the computation document, no factor-to-factor read) |
| R-4 | "times the net blocks, the counted blocks less the deducted blocks and the blocks … removes" | closed |
| R-5 | "an over-limit justification record is dated on or after that pump delivery … the justification being the record of the change" | closed (rule = compute) |
| R-6 | "fewer units than the whole blocks of its span times the tier's allowance" | closed |
| R-7 | "the newest grant of the item, the one with the latest valid-through date … no other newer grant being considered" | closed |
| R-8 | "credited only when the customer has stopped insulin … whenever the customer has not stopped insulin, nothing is deducted" | closed |
| R-9 | "when the payer paid any amount" | closed |
| R-10 | "divided by 30, rounded down" | closed |
| R-11 | "the program's patient payments" | closed |
| R-12 | "or its ship date when no proof of delivery is recorded" | closed |
| R-13 | P5 defines "exposed units, the units at risk plus the units beyond the payer authorization"; waiver_coverage_rule tiers say "exposed units" | closed |
| R-14 | "rounded to the nearest cent, a half cent going to the even cent" (rounding ladder and plan balance) | closed |
| R-15 | P4 `pump_waiting` subtracts only recent pump charges in the charges-only branch; rule "those charges, never more than the pump balance, less the waiting pump charges" | closed |
| R-16 | "never below zero" | closed |
| R-17 | the baseline no longer cites an unread regimen field: "Medicare is expected to pay every listed unit" | closed |
| R-18 | "an insulin pharmacy program with no insulin refill on record counting as a supply that ended before it" | closed |
| R-19 | "with no refill of the item on record the latest refill's ship date counts as the order date and its supply days as 0" | closed |
| R-20 | "no insulin refill on record counting as a supply that ended on the order date" | closed (compute offset 0, which is ≤ 0) |
| R-21 | "with no such visit on file by any practitioner, the review visit date counts as earlier than every record, so no month of a horizon is left" | **not closed: introduces N7** (below) |
| R-22 | "counted as zero when the review start falls after the anchor date" (compute `MX(0, MONTHS(…))`) | closed |
| R-23 | "or no qualifying visit is on file at all, the grant carries no units" | closed |
| R-24 | renewal and model-change `baseline.params` now `[]` | closed |
| R-25 | P3/P5 prerequisite conditions now name "installments current" and "the uncovered past-due amount (aged postings less credits, the hardship set-aside and the covered remittance patient responsibility)" | closed |
| S-1 / S-2 | assembly sentences now introduced as assembly ("The grant is assembled from these rules", "the pump part is …"); every combination lives in non-factor bindings | closed (no factor-to-factor read; the composition is stated once) |
| S-3 | P1: "including a commercial-tier supply covered by a plan member waiver" (model-change wording removed). Shared holds clause: "the refill count for a delivery drawing on the grant resting on the newest written order and of the plan member waiver count" | closed |
| KB-2 | the task_tools.py docstrings carry no example value (return f-strings only) | confirmed renderer-side; nothing source-side |

### new defect (revision 5)

- **N7. SOURCE-POLICY RED (rule vs compute, constructed; P0, introduced by the R-21 fix).**
  - Rule: "with no such visit on file by any practitioner, the review visit date counts as earlier than every record, so no month of a horizon is left".
  - But "The review starts on the later of the review visit date and the regimen change date". The compute follows that: `review_start_date = MX(review_visit_date, regimen_change_date)`. So when a regimen change date exists, the horizon is counted from it and months remain.
  - The clause "so no month of a horizon is left" states a consequence the compute does not produce.
  - Demonstration (/tmp/audit_cgm_0063/scripts/n7.py): task 0's world with every medical-record row removed. The regimen change is 2026-08-12 (bgm), or 2026-08-05 (insulin closure) with bgm removed. Rule reading: 0 months left → counted blocks 0 + bridge 1 = **1 unit**. Compute: months left 6 − MONTHS(2026-08-12, 2026-12-02) = 3 → min(10, 3) + 1 = **4 units**.
  - Not reached by task 0's actual world, which has qualifying visits.
- No other new defect. All scored values are unchanged (recomputed below), which matches the reworker's "values_changed=none".

### closing_checklist (revision 5)

Written after the reveals (12:28:48 UTC).

- All three files carry `revision_5`, with earlier revisions untouched.
- Scopes, trees and the DAG are unchanged and hold: task 0 has 1 prerequisite problem and 1 value_input edge; task 1 has 3 and 3, with user-owned P3 and P4.
- Factors: bounds met, ladders distinct, baselines honest, every factor bears weight on both worlds.
- R-1 … R-25 and S-1 … S-3 closed, **except R-21, whose fix introduced N7** (P0 no-visit clause contradicts the review-start rule and the compute; constructed, unreachable in task 0). KB-2 is confirmed renderer-side.
- No regression in any scored value or sensitivity.
- Gates per the coordinator's snapshot are all OK, including traceability.
- **Result:** both tasks PASS. The charter carries one open RED, N7.

## revision_6

### charter_global_frozen (revision 6)

- Frozen before any round-6 task file was read.
- Hashes: cgm.extended.yaml 5e43679a3110f3163288958a010dbacc8912789cf66f013eba3be472c7c646e1 (changed); task_tools.py, 0.view.json and 1.view.json unchanged.
- Gate snapshot cited from the brief: all OK, including traceability.
- contamination: as in revisions 2–5.
- **The diff from revision 5 is a single P0 rule sentence** (plus its verbatim compute_basis copies). Every compute binding in all six policies is unchanged. Base copy verbatim. The verbatim, shape and independence checks are clean.
- **N7: closed.** New sentence: "with no such visit on file by any practitioner, the review visit date counts as earlier than every record, so the review starts on the regimen change date when one applies, and when none applies the review start is earlier than every record and no month of a horizon is left". This now agrees with "The review starts on the later of the review visit date and the regimen change date" and with the compute (`review_start_date = MX(review_visit_date, regimen_change_date)`).
- **Probe** (n7.py, task-0 world with every medical-record row removed):
  - with the bgm regimen change (2026-08-12), compute = 4 and the rule now reads 4;
  - with the insulin-closure date (2026-08-05), compute = 4 and the rule reads 4;
  - with neither, the review start is `'0000-00-00'`, so no month is left. That is the compute and the rule's "when none applies" branch.
- **N7 sweep:** I re-checked the round-5 absent-record sentences against the compute: R-18 (P1, no insulin refill → every unit at risk), R-19 (P0, no refill → order date / 0 days), R-20 (P0, no insulin refill → ended on the order date), R-21/N7 (above), R-23 (P2, no visit → no units). All agree, and none was changed this round.
- New defects: none.

### closing_checklist (revision 6)

Written after the reveal recorded in the task files.

- All three files carry `revision_6`, with earlier revisions untouched.
- Scopes, trees, DAG, factor bounds and honest baselines unchanged.
- Every factor bears weight.
- N7 closed. No open RED, no regression.
- Scored values and sensitivities unchanged: task 0 is 4 / 1; task 1 is grant 4, plan 6 × 27.98, waiver 1, refill 3 / 9 / 90.
- **Result:** both tasks PASS; charter CLEAN.

## revision_7

### charter_global_frozen (revision 7)

- Frozen before any round-7 task file was read.
- Hashes: cgm.extended.yaml aef5671904a4882257f1213c4c89c32132a9c0489aff0226d5a9bc2bfdbb03c4 (changed); task_tools.py and both views unchanged.
- Gates cited from the coordinator's snapshot: all OK.
- Inputs read: `audits/render_source/XF_recipe.md`, `audits/render_source/cgm_sensor_supply_services/findings_r2.md`, and the revision_2 XF and R2 sections of `audits/policy_kb/cgm_sensor_supply_services/1.md`.
- contamination: as in revisions 2–6.
- **Mechanical checks** (script; recipe item 6):
  - base copy verbatim;
  - every compute_basis, baseline sentence, superseded_clause, replaced_by and policy_source verbatim;
  - `factor_shape_errors` reports none;
  - **transitive** read check: for every factor, the bindings it reads through non-factor bindings include no other factor's binding. Empty for all six policies;
  - no factor id is named in any baseline.rule.
- **Counts:** P0 3 P / 3 M; P1 2 P / 3 M; P2 2 P / 2 M; P3 2 P / 4 M; P4 4 P / 2 M (pump_balance_fold is now a parameter that adds an amount; statement_cycle_window reads the pump's coverage record); P5 2 P / 4 M. Every ladder has 3 distinct tiers and each fall-through is "the standard … applies".
- **Renewal restructure (P0), checked:**
  - Standard method: grant = written units per 30 days × whole blocks from the order date, anchored to the order date. When the customer has stopped insulin (closure customer_discontinued) and the CGM program documents an insulin regimen, the blocks are capped at the months left of a 3-month coverage review. The review starts on the later of the most recent qualifying visit by any practitioner and the latest insulin refill's ship date.
  - Realistic for an Original Medicare supplier once the insulin criterion lapses. Base-consistent: the visit is the base follow-up rule's "most recent visit … by any practitioner".
  - Factors:
    - `coverage_review_length` (P, insulin): closed ≥ interval months before order → 0; insulin supply ended by the order date → interval; otherwise the standard 3.
    - `review_visit_practitioner` (M): treating → signer → standard.
    - `regimen_change_record` (P, bgm): bgm non-insulin with order → newest order date; bgm non-insulin, no order → bgm activation date; otherwise the standard latest insulin refill date.
    - span, quantity and bridge as before; the bridge now "adds blocks".
  - Each factor's fall-through is the standard value, reachable in scope.
- **Round-6 items:** none were open. The XF class (10 members) and R2-1/2/4/5/6/7/8 are addressed:
  - R2-1/R2-2: the renewal assembly no longer names a factor quantity; review visit and regimen date are now standard quantities.
  - R2-4: P1 credit "only when … the insulin pharmacy program carries a closed date … or the closed date is not recorded, nothing is taken off" = compute.
  - R2-5: P4 `covered_balance` no longer branches on a factor outcome.
  - R2-6: P2 lapse ladder tier 2 now "or no qualifying visit is on file at all".
  - R2-7: P3/P5 baselines carry the plain paid-supply end; units at risk = at-risk blocks × allowance.
  - R2-8: P1 delivery now "… times that allowance" for each block term, matching `next_delivery_units`.

### new defects (revision 7)

- **N8. SOURCE-POLICY RED (PLAUSIBLE second reading; P0 assembly order, reached in task 0).**
  - The standard paragraph says "the grant's blocks never exceed the months left of a coverage review". The generic assembly says "Each adjustment set out below changes the standard grant as that adjustment states, the blocks being settled before they are multiplied by the units per 30 days".
  - The block-start adjustment "replaces the standard blocks and anchor", and the bridge adjustment "adds blocks".
  - The rule never says the review cap applies to the replaced blocks (using the replaced anchor) but not to the added bridge blocks. That is what the compute does: `authorized_blocks = MN(span_blocks, review_months_left)`, and only then `+ bridge_blocks`.
  - Two other readings follow from the text:
    - (B) "never exceed" as a ceiling on all the grant's blocks, bridge included: min(10 + 1, 3) × 1 = **3**.
    - (C) the replacement of the standard (capped) blocks lifts the cap: (10 + 1) × 1 = **11**.
    - The compute gives **4** (/tmp/audit_cgm_0063/scripts/n8.py).
  - The round-6 text stated this order explicitly ("when a horizon applies the counted blocks are the fewer of the span's blocks and those months left. The grant then carries … the sum of the counted blocks and the bridge"). The recipe's generic rewording dropped it. Recipe item 4 requires a generic order statement where order matters.
- **N9. SOURCE-FACTOR RED (realism, constructed; P4 pump_plan_carve_out, a regression).**
  - The pump-plan adjustment now "takes off the plan balance what the insulin pump program's own approved payment plan still covers" whatever the pump-balance adjustment added. Compute: `covered_balance = MX(0, … + pump_taken_in − pump_plan_carve)`, with `pump_plan_carve` independent of `pump_taken_in`.
  - Revision 6 applied the carve only inside the whole-pump-balance part, floored at zero.
  - Demonstration (/tmp/audit_cgm_0063/scripts/n9.py), task-1 world with the pump program closed, or on another coverage with no pump charges: nothing is taken in from the pump, yet 39.40 of pump-plan installments still comes off the CGM plan balance, 71.04 → 31.64. No business takes a pump plan's unpaid installments off a CGM-only balance that never contained them.
  - Not reached in task 1 (same coverage, whole balance taken in → 167.84 → 27.98, unchanged).
- Observation (not RED): P3/P5 state no order between the early-refill adjustment ("moves the paid-supply end earlier") and the frequency-edit adjustment ("against the paid-supply end"). The dominant reading applies the frequency edit to the moved end, which is the compute (task-1 P3 = 1). Reading the unmoved end would give P3 = 2, with P5 still 3. I record it as an observation because the moved quantity is the natural input to every later use.
- Observation (carried): coverage_review_length gives a longer review (interval) when the insulin supply has already ended than the standard 3 months when insulin is still on hand. That is acceptable as "prescriber renewed after insulin ended".

### closing_checklist (revision 7)

Written after the reveal (16:26:42 UTC).

- All three files carry `revision_7`.
- Scopes, trees and DAG unchanged.
- Factor floors met (P0 3/3, P1 2/3, P2 2/2, P3 2/4, P4 4/2, P5 2/4).
- Multi-source and cross-difficulty factors present per task: task 0 insulin/bgm, refill_bridge; task 1 pump, superseded_supply_overlap.
- Every factor bears weight against an honest, reachable baseline.
- No factor reads another, transitively.
- Values unchanged; the renewal's all-baseline moved 36 → 9 as stated.
- **Open:** N8 (P0 assembly order; PLAUSIBLE second readings 3 / 11 on task 0) and N9 (P4 pump-plan carve applied to a pump balance never taken in; constructed).
- Task 0 RED SOURCE-POLICY; task 1 PASS.

VERDICT revision_7: task0=RED SOURCE-POLICY task1=PASS charter=N8,N9

## revision_8

### entry (2026-10-15 ~17:05 UTC)

- `tail -1 REWORK.log` → `REWORK round 8: gates green`.
- `/tmp/erl0063_coord/snapshot.sh cgm_sensor_supply_services`. I screened it before running: it only removes `__pycache__` and runs gates and hashes. Output:
  - Gates: check_extended `EXTENDED OK`; check_task_tools `TASK TOOL CONTRACT OK`; replay_tasks `REPLAY OK`; check_solvability `SOLVABILITY OK`; check_compute `COMPUTE OK`; check_grounding `GROUNDING OK`; check_traceability `TRACEABILITY OK`; check_cross_fire `SCOPE OK`.
  - Hashes:
    - `55992a2bbbbe6fe2e0ce9db4d7c3f68188999e92541c87acb2b80edb47fbfd24` 0.view.json (unchanged)
    - `e05572938a6695b2dcff76a66e002ef20302eb8bc5cc48d6a13476a1ced82020` 1.view.json (unchanged)
    - `5db502c30bd686a481bf5bce8ada11009a1d3358c6081fa12c33b70ab982d148` cgm.extended.yaml (changed)
    - `5d8f61678079afb51c1099d426d0f472c633f6170809a9f1c671a1027d6e1ed9` task_tools.py (unchanged, so tools are unchanged)

### charter_global_frozen (revision 8)

- Frozen before any round-8 task file was read. contamination: as in revisions 2–7.
- **Diff from revision 7:**
  - the P0 standard-paragraph cap sentence and the assembly sentences of all six policies;
  - P4 `statement_wait` split into CGM and pump parts (`statement_wait_pump`);
  - P4 `pump_plan_carve` gated on `pump_same_coverage`;
  - P4 `covered_balance` = `MX(0, … + MX(0, pump_taken_in − statement_wait_pump − pump_plan_carve))`;
  - P4 pump_plan_carve_out ladder tiers 1–2 now add "and the pump program bills the same coverage record".
  - No other compute change.
- Mechanical checks clean: base verbatim; every quote verbatim; no shape errors; the transitive factor-read check is empty; no factor named in any baseline. Counts unchanged (P0 3/3, P1 2/3, P2 2/2, P3 2/4, P4 4/2, P5 2/4).
- **N8: closed.**
  - P0's assembly now reads "in this order: replacements of a standard quantity are applied first, so the span's blocks and the anchor date are those as replaced; the coverage-review limit is then applied to the span's blocks so replaced, counting the months left to the anchor date so replaced; blocks added on top of the span come last and are not limited by the coverage review".
  - The standard paragraph adds "the grant's counted blocks, the blocks of its span, never exceed the months left …, blocks added on top of the span not counting toward that limit".
  - Readings B (3) and C (11) are now excluded by the text. Only the compute's reading (min(10, 3) + 1 = 4) remains.
- **Same check on the other non-commuting policies:**
  - P1 now states its order: grant/blocks/listing → payment expectation → units taken off.
  - P3/P5 now state their order: "the paid-supply end … moved … first, the at-risk blocks are then marked against the paid-supply end as moved, blocks are then taken off …, and the listing / waiting rule replaced last". This closes my revision-7 observation as well.
  - P2 states its order (subtractions commute anyway).
  - P4 states its order (pump-side deductions bounded within the pump amount, then the rest, installment last).
  - Each stated order equals the compute's evaluation order.
- **N9: closed.**
  - Rule: "The pump-plan adjustment takes off … only when that program bills the same coverage record"; assembly: "amounts taken off another program's postings come off only the amount added from that program, never taking it below zero".
  - Probe n9.py on the task-1 world with the pump closed, or on another coverage: pump-plan carve 0, covered balance 71.04 (revision 7 gave 31.64). As seeded: 27.98, unchanged.
  - pump_plan_carve_out's tiers are now compound over distinct records (plan status ∧ pump coverage), which adds a multi-source factor.
- N6 property test re-run: 0 mismatches. No new defect found.

### closing_checklist (revision 8)

Written after the reveal (17:04:35 UTC).

- All three files carry `revision_8`.
- N8 and N9 closed. No new defect, no regression.
- Values and tools unchanged.
- Gates green per the snapshot above.
- Factor floors, multi-source and cross-difficulty requirements, and honest reachable baselines hold for every computation. No factor reads another.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN
