# Policy-task audit — protection_contract_claims / charter-global

## charter_global_frozen

- Scenario: env/env_0037_residential_hvac_company; difficulty protection_contract_claims; category warranty; M=2.
- Auditor: claude-opus-5-5, running erl-task-policy-audit as an independent auditor (did not author the artifacts).
- Freeze time of this section: 2026-10-05T15:48:30Z (file mtime). It was written before any task's GT was revealed. It holds nothing taken from a revealed GT.
- Freeze hashes (sha256, recomputed by the auditor; they match /tmp/erl37/views/protection_contract_claims/charter.sha256):
  - `tasks/protection_contract_claims/warranty.extended.yaml`: a6c5442913e84983d13add73a6973f18449018f1740ccc02d992c6f4bf6bd873
  - `tasks/protection_contract_claims/task_tools.py`: 8fa070d29dbef6f804e9d74a94a81c8f07d5359947cd33c2efa77be392dcc57f
  - masked view task_0: 8023491eb78ac59c2767563178b123e09e5d8a51b75c58234fafcf4171be6dc1; masked view task_1: ca12f543baa6ce4268f5ea2be41a906012e1e584e504bcda9110fa3a235eabcd
- Fields this section was built from: blueprint.yaml (difficulty entry), db_schema.json, share_tools.py, products/{warranty,service,plan,install}.yaml (parameter lookups only), warranty.extended.yaml (base + extended_policies), task_tools.py, and the compute-DSL semantics in skills/erl-task-instantiate/scripts/check_compute.py (`build_env`). The DSL file is read only to know what SUM/LATEST/XLATEST/CFIELD/MONTHS/DAYS evaluate to.
- Masked and unread: tasks/*.json (only the masked views were used), worklog.md (scenario-level and difficulty-level), evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, and every other audits/ directory.
- Entry conditions (Step 0): the gate snapshot came with the brief (/tmp/erl37/gates/protection_contract_claims.snapshot.txt). EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are all OK, and CACHE-DIFF is INFO. The masked views and their hashes came with the brief and were re-verified. check_traceability is deferred until the KB is published. Input is complete.
- Base copy check: `diff <(sed -n 1,1448p warranty.extended.yaml) blueprint/products/warranty.yaml` shows only the trailing banner comment. The base section is a verbatim copy of the constitution.

### policy_conflict_scan

The structured policy has the 13 base policies plus five extended policies:

| id | tiers | subject / computes | target_tool (owner) | prerequisite |
| --- | --- | --- | --- | --- |
| P1 warranty_ext_labor_plan_claim_decision | 5-Yr Labor, 10-Yr Labor | warranty_claim_decide / approved_amount | decide_labor_plan_claim_66c3e056 (agent) | [] |
| P2 warranty_ext_visit_claim_service_fee | 5-Yr Labor, 10-Yr Labor | warranty_charge / fee_amount | charge_claim_service_fee_b62a9756 (agent) | P1 (value_input, state form) |
| P3 warranty_ext_cancellation_refund | 5-Yr Labor, 10-Yr Labor | warranty_cancel / refund_amount | confirm_protection_cancellation_57f0aac4 (user) | P1 (value_input), P2 (state_gate), both state form |
| P4 warranty_ext_parts_labor_claim_decision | 10-Yr P&L, 12-Yr Total, 12-Yr Total Plus | warranty_claim_decide / approved_amount | decide_parts_labor_claim_22401446 (agent) | [] |
| P5 warranty_ext_transfer_benefit_carryover | 10-Yr P&L, 12-Yr Total, 12-Yr Total Plus | warranty_limit_grant / carried_benefit | confirm_protection_transfer_64743e30 (user) | P4 (value_input, state form) |

- Overlapping subjects: P1 and P4 both write `warranty_claim_decide`. Their tier sets are disjoint and together cover tiers 2 to 6. A labor-only contract can only be decided under P1, and a parts-and-labor contract only under P4. The Harbison 2-Year Workmanship Warranty is in neither, so its claims stay under base rules and no extended policy decides them. No other two extended policies share a subject.
- Triggers and eligibility: P1 and P4 decide the original decision only (round 1) and defer to the base coverage tests for approve/deny. P2 keeps the base one-fee-per-visit dedup and the Comfort Club waiver. P3 keeps base holder confirmation, the `cancellation_allowed` gate and the full-refund window. P5 keeps base holder confirmation, the transfer window, `transfers_max` and the same-address buyer rule. No extended policy weakens a base eligibility.
- Time anchors: P1/P4 use the failure date (= the ticket's completed_date). P2 uses the ticket completed_date (membership) and the date of handling (12-month repeat window). P3 uses the date of confirmation, the refund start date and the purchase date. P5 uses the closing date on the request and the date of handling. No two policies anchor the same quantity on different dates.
- Action parameters and terminal states: each tool writes only its own rows (decision entry / fee charge / cancel+credit+payout / transfer+new contract+grant+fee). The decide tools state that they move neither claim_limit_remaining nor the service invoice. P3 and P5 read approved-but-unpaid decisions through "approved amounts of original decisions not yet matched by payouts", which agrees with that tool contract.
- Cross-category read boundaries: P1 reads service/install/plan; P2 service/plan; P3 install/plan; P4 service/install/plan; P5 plan/service/install. All are declared in `cross_category`.
- Scope exclusivity and completeness, judged from the policy surface alone: the two task worlds are a labor-only cancellation (task 0) and a parts-and-labor transfer (task 1). Their trees derived from the rules are {P3, P1, P2} and {P5, P4}. These are pairwise disjoint and jointly cover all five extended policies. (This was derived per task. The masked charter_scope field was not used.)

### rule_compute_equivalence

Check 2, for each policy. "Quoted" means a verbatim `compute_basis` sentence exists in the `rule` and the binding implements it.

- P1: every binding has a verbatim compute_basis quotation that is in the rule. The ladders (after_hours_labor_basis, unit_age_share, maintenance_recency_share, purchase_timing_share, diagnostic_component_share, call_class_premium_share) each appear both in the rule and as branches of their `decides` binding. Divergences found:
  - (a) `paid_maint_date` = XLATEST over every `maintenance_tuneup` line of the customer, with no date bound. `last_maint_date` then falls back to `plan_maint_date` whenever the latest paid line is later than the failure date, and `plan_maint_date` has no bound on the failure date either. The rule says "the latest documented maintenance on or before the failure date". An earlier paid tune-up that is on or before the failure date is discarded whenever a later one exists. The compute also never tests that the line was paid ("paid precision tune-up line"). Latent: neither task world has a `maintenance_tuneup` line, so neither scored value moves (see each task file).
  - (b) `diag_discount` / `premium_discount` subtract every `service_discount` posted against the line. The rule says "less the member discount posted against it". A courtesy (senior/veteran) discount against the diagnostic line would be subtracted by compute but not by the rule. Latent: both task customers have `discount_program: none`, and every discount in both worlds is a member line.
  - (c) "the labor net up to the component sublimit multiplied by that labor multiplier" can also be parsed as "(labor net up to the sublimit) × multiplier". That second parse can pay more than the labor line billed. The base payout rule rules it out ("pays the failed component's lines on the service invoice"; measure: "labor capped at the component's labor sublimit"). This leaves the compute's MN(net, cap×mult) as the only coherent reading. The same holds for P4. Recorded as considered and excluded.
- P2: the bindings are quoted and the ladders (member_fee_share, after_hours_visit_fee, claim_size_fee_share, repeat_visit_fee_share) are in both faces. Divergences:
  - (a) `member_status_active` reads the agreement's current status, but the rule anchors membership to "the completed date of the service call". Latent: both worlds' agreements are active, with a term covering the call dates.
  - (b) `approved_claims_12m` counts decision entries (round 1 and round 2), not claims. A claim decided twice in the window would count twice against "the number of other claims". Latent: no appeal rows exist in either world.
  - (c) CFIELD('plan', …) returns the first agreement found for the customer. Every plan-reading policy has this. Latent: each world has exactly one agreement.
- P3: the bindings are quoted and the ladders (refund_start_anchor, unused_share_day_count, equipment_age_refund_share, claims_experience_share, claims_deducted_method, member_admin_fee_share) are in both faces. Divergences:
  - (a) `full_refund_case` tests DAYS(purchase_date, NOW). The rule (and base) say "gives notice within the tier's full-refund days", and notice can come before the date of confirmation (a written request received earlier). Latent: in task 0 both dates are years past the window.
  - (b) `claims_deducted` tier 1 takes MX(payouts, approved originals). This equals the rule's "payouts plus the approved amounts not yet matched by payouts" only when every payout belongs to a round-1 approval. A round-2 appeal payout would break the equality. Latent: there is no appeal in task 0's world.
- P4: the bindings are quoted and the ladders (after_hours_sublimit_basis, member_sublimit_uplift, refrigerant_pounds_method, manufacturer_part_handling, leak_search_component_share, booking_premium_share) are in both faces. No divergence was found that moves a value on any reachable record set beyond the shared CFIELD-first-agreement point (P2 c).
- P5: the bindings are quoted and the ladders are in both faces. Divergence: `primary_maint`, `paired_maint` and `paid_maint` have no bound on the closing date, while the rule says "on or before the closing date on the transfer request". Latent: in task 1's world every maintenance record predates the closing date.
- Sweep back (does the rule promise anything the compute lacks?): no rule sentence of P1–P5 lacks a binding. The P1/P2/P3 rules' first sentences are scope sentences ("This policy sets/fixes …"), and their scope is carried by the tool's tier restriction.

### action_binding_and_uuids

- (target_tool, computes): (decide_labor_plan_claim_66c3e056, approved_amount) belongs to P1 only. (charge_claim_service_fee_b62a9756, fee_amount) belongs to P2 only. (confirm_protection_cancellation_57f0aac4, refund_amount) belongs to P3 only. (decide_parts_labor_claim_22401446, approved_amount) belongs to P4 only. (confirm_protection_transfer_64743e30, carried_benefit) belongs to P5 only. Each pair has exactly one claimant.
- Docstrings: none places a call in a sequence, names another tool, or uses before/after/first as an ordering word. The only hits are inside the denial-reason enum definitions ("filed after the filing deadline", "the failure came before coverage started"), which describe facts and not call order. No tool adds a confirmation, review or wait outside the policy.
- Tool bodies: none checks a prerequisite, status, eligibility or amount (read at task_tools.py lines 61–76, 105–117, 150–181, 245–260, 297–331). Each tool `find`s the contract only to copy customer_id/balance and then writes.
- uuid8s: 66c3e056, b62a9756, 57f0aac4, 22401446, 64743e30. They share no prefix or suffix, are not sequential, are not adjacent values and are not reused. Nothing suggests batch derivation.
- Observation (enum superset): both decide tools offer `waiting_period_not_elapsed` and `contract_not_active` as denial reasons, and base warranty_evt_claim_coverage does not list either as a denial_reason. Neither task's derived decision uses them.

### prerequisite_graph

Check 7:
- `prerequisite` is filled on all five policies (P1 [], P4 []).
- Edges: P2→P1, P3→P1, P3→P2, P5→P4. Every `problem` is another extended policy id in this file (none is a base id or a self-loop). The graph is acyclic: topological orders are P1<P2<P3 and P4<P5.
- `policy_source` is a verbatim sentence of the blocked policy's own rule in every case: P2 rule "The claim service fee for a service call is fixed only after every claim filed on that call against the contract carries its original decision."; P3 rule "A cancellation refund is not fixed until every claim filed on the contract carries its original decision." and "Before a cancellation refund is recorded, the contract must carry the claim service fee owed for every service call on which a claim against it was approved."; P5 rule "The claim benefit carried to the buyer is fixed only after every claim filed on the seller's contract carries its original decision."
- All four edges have `form: state`, and none carries `fallback_reason`, which is consistent.
- `resolved_by` equals the depended-on policy's target_tool in each case. Each `effect` genuinely holds per the tool bodies and the computes. The decision entry feeds `approved_on_visit` (P2), `approved_original`/`last_decision_date`/`approved_claim_count` (P3) and `approved_original`/`approved_36m` (P5). The fee charge raises contract_balance, which the P3 tool nets against the credit before paying out.
- `kind`: the value_input gates `approved_on_visit` (P2), `claims_deducted` (P3) and `reserved_claims` (P5) are real compute bindings. P3→P2 is a state_gate whose `gate` names a field (`warranty_billing_entries.line_type`) rather than an eligibility id. No base eligibility exists for it; the gate is the P3 sentence itself (observation O-6).
- `condition` against the sentence: P2/P3/P5 decision conditions match the sentence's strength. The P3→P2 condition says "approved or partially approved … unless the fee is waived", while the sentence says "approved" and "the claim service fee owed". "Owed" absorbs the waiver. "Approved" read in business language covers a partial approval, and P2's own rule independently makes the fee owed on a partial approval, so the reader reaches the same gate (observation O-7).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "current world") appears in any prerequisite field.

### prerequisite_sentences

Check 6, for each edge:

| edge | ordering connective | waited-on state (record-visible) | names a tool / id / snake_case? | strength = condition? |
| --- | --- | --- | --- | --- |
| P2→P1 | "fixed only after" | every claim filed on the call against the contract carries its original decision (a round-1 decision entry in the claim history) | no | yes |
| P3→P1 | "not fixed until" | every claim filed on the contract carries its original decision | no | yes |
| P3→P2 | "Before … is recorded" | the contract carries the claim service fee owed for every call with an approved claim (a claim_service_fee billing entry naming the call) | no | yes (O-7) |
| P5→P4 | "fixed only after" | every claim filed on the seller's contract carries its original decision | no | yes |

- Which write brings each state about, as a reader would find it:
  - "carries its original decision": two writes of this difficulty post a round-1 decision, P1's and P4's. The blocked policy fixes the tier set (P2/P3 are labor-only, P5 is parts-and-labor). The depended-on rules state their own tiers ("filed against a Harbison 5-Year Labor Protection or Harbison 10-Year Labor Protection contract" vs "… 10-Year Parts & Labor Protection, … 12-Year Total Protection or … 12-Year Total Protection Plus contract"). So for any contract the blocked policy can apply to, exactly one write qualifies. There is a single reading.
  - "the contract must carry the claim service fee owed": only P2 charges a `claim_service_fee` on a labor-only contract. There is a single reading.
- No second wording, tool name or other problem's id appears in any blocked rule. The depended-on rules (P1, P2, P4) do not restate the sentences that wait on them.
- Undeclared cross-problem orders in extended rules: none. In base rules, `warranty_billing` says "A transfer fee is due from the buyer before the buyer's next claim is paid", and `warranty_agg_one_contract_per_unit` says "must cancel the existing contract first". These are base cross-problem orders that ground no edge, and neither task's tree rests on them (observation O-8).

### override_declarations

Check 1, finding half, taken sentence by sentence against each `base_policy_refs` entry:

- P1 vs warranty_evt_claim_coverage: every coverage test, the filing deadline, the maintenance-current test, the excluded causes, limit_exhausted and the labor-term sentence are followed ("the coverage tests of the base claim rules decide whether the claim is approved at all"). The parts/manufacturer sentence is not overwritten, and P1 adds "Parts are never paid on a labor-only tier". Base's "When the manufacturer warranty supplies the part, the claim is partially_approved with denial_reason manufacturer_parts_coverage_applies … otherwise a claim passing every test is approved" therefore still governs the decision label on a labor-only contract. P1 gives no sentence on whether that label applies when the tier pays no parts at all. This is finding F-1, whose consequence is demonstrated in task_0.md.
- P1 vs warranty_evt_claim_payout:
  - "labor is paid up to the labor sublimit": superseded and declared. The replaced_by text carries only the after-hours basis. The age, maintenance-recency and purchase-timing shares on labor payable are stated in the rule, and the approved-amount sentence is also superseded (overwrite 3), so the override is declared. The replaced_by text is incomplete (observation O-1).
  - The diagnostic/premium clause is superseded and declared. Its replaced_by text covers the diagnostic share only, and the premium-share sentence is in the rule (O-1).
  - The refrigerant and leak-search clauses are not touched. Labor tiers have refrigerant_covered and refrigerant_leak_search_covered false, so the base gives zero and nothing conflicts.
  - The cap and allocation sentence is followed. The approved-amount sentence is superseded and declared.
- P1 vs warranty_evt_claim_appeal and warranty_evt_no_lemon: P1 decides round 1 only. Labor tiers carry no no-lemon guarantee. Nothing conflicts.
- P2 vs warranty_agg_claim_service_fee_per_visit: one fee per visit, no fee when all claims are denied, no fee at 0.00 highest fee, the Comfort Club waiver ("a waived fee is not charged at all"), and due-with-invoice are all followed. The fee amount ("the single fee is the highest of their claim_service_fee_usd values") is superseded and declared, so the after-hours basis and the three shares are declared. warranty_purchase_eligibility, warranty_pricing, warranty_home_sale_transfer and warranty_billing govern no quantity P2 computes, so nothing conflicts.
- P3 vs warranty_cancellation: holder confirmation, effective date, cancellation_allowed, the full-refund window and the payout to the original method are followed, and the "Otherwise the refund is …" sentence is superseded and declared. Not superseded, and latent:
  - (i) "A contract still pending is cancelled on the same terms and counts its full term as unused." P3 counts unused value from the refund start date for any labor-only contract. A pending post-install contract whose price is unpaid past day 60 would get two different numbers. The base lifecycle itself allows user cancellation only from `active`, so the clash is between base sentences as much as with P3 (finding F-2, latent).
  - (ii) "… or, for a tier bought on the installation contract, naming no charge on this contract". P3 says "the refund is credited against the contract-price charge", and the tool requires a `source_billing_id` (F-2, latent).
  Neither bears on task 0, whose contract is active, post_install_window, with a contract_price charge on file.
- P4 vs warranty_evt_claim_coverage / payout / appeal / no_lemon:
  - The labor clause, the refrigerant + leak-search clause, the manufacturer-supplies-part clause and the after-hours premium clause are superseded and declared. The member-sublimit uplift is in the labor replaced_by text. The leak-search share is under the superseded refrigerant clause, but the replaced_by text omits it (O-1).
  - The diagnostic sentence is followed. The decision label is followed ("a claim whose part the manufacturer supplies is partially approved for the parts").
  - No-lemon on 12-Yr Total Plus is not addressed and is inherited from base. Neither task involves it.
- P5 vs warranty_activation / warranty_home_sale_transfer: the carry-over amount is superseded in both base policies and declared. The window, transfers_max, same-address buyer, same tier/scope/units/dates, transfer fee and "claims filed before the transfer stay with the seller's contract" are all followed.
- Disguised forms: no anonymous intermediate (every multiplicative share is named in the rule) and no 0/1 multiplier zeroing a base-fixed amount. P2's member share of 0 reproduces the base waiver and does not override it. No dropped branch, and no "wrong value" / "avoid" wording anywhere in the extended section.

### factor_ladders

Structure only. Whether each factor bears weight is decided in each task's `factor_weight` section.

| policy | factor | effect | decides | tiers (incl. fall-through) | multi-source (every non-fall-through tier a conjunction over distinct records) | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | after_hours_labor_basis | method | labor_allowed | 3: cap×mult / net÷mult / standard cap | weak: symptom and call class both sit on the service ticket (the multiplier is the class's catalogue parameter) | service |
| P1 | unit_age_share | parameter | age_share | 3: 0.80 / 0.90 / 1 | no | install |
| P1 | maintenance_recency_share | parameter | maint_share | 3: 0.85 / 0.95 / 1 | the input is the later of a plan record and a service record (a disjunction over distinct records) | plan |
| P1 | purchase_timing_share | parameter | timing_share | 3: 0.85 / 0.95 / 1 | no | none |
| P1 | diagnostic_component_share | parameter | diag_share | 3: 1.00 / 0.50 / tier coverage (0 on both labor tiers) | no | none |
| P1 | call_class_premium_share | parameter | premium_share | 3: 1.00 / 0.50 / tier coverage (0 on both labor tiers) | no | service |
| P2 | member_fee_share | parameter | member_fee_share | 3: 0 / 0.50 / 1 | yes: agreement status/term/tier (plan) AND the ticket's completed date (service) | plan |
| P2 | after_hours_visit_fee | method | after_hours_visit_fee | 3: ×mult / +25% of premium / unchanged | no | service |
| P2 | claim_size_fee_share | parameter | claim_size_fee_share | 3: 0.50 / 0.75 / 1 | no | none |
| P2 | repeat_visit_fee_share | parameter | repeat_visit_fee_share | 3: 0.25 / 0.50 / 1 | no | none |
| P3 | refund_start_anchor | method (see O-4) | refund_start | 3: scheduled replacement date / request-received date / effective date | tier 2 only (install AND change request); tier 1 is a single install record | install |
| P3 | unused_share_day_count | method | unused_share | 3: daily / short-rate×monthly / monthly | no | none |
| P3 | equipment_age_refund_share | parameter | refund_age_share | 3: 0.80 / 0.90 / 1 | no | install |
| P3 | claims_experience_share | parameter | experience_share | 3: 0.85 / 0.95 / 1 | no | none |
| P3 | claims_deducted_method | method | claims_deducted | 3: max(payouts, approved) / nothing / payouts | yes: decision dates AND payout dates (distinct entry kinds) | none |
| P3 | member_admin_fee_share | parameter | admin_fee_share | 3: 0 / 0.50 / 1 | no: status and consecutive_terms are on one agreement record | plan |
| P4 | after_hours_sublimit_basis | method | labor_allowed | 3: cap×mult / net÷mult / standard cap | yes: call class (service ticket) AND tier's after-hours coverage (contract tier) | service |
| P4 | member_sublimit_uplift | parameter | member_uplift | 3: 1.25 / 1.10 / 1 | no: one agreement record and its tier parameter | plan |
| P4 | refrigerant_pounds_method | method | lbs_paid | 3: none / billed−earlier / billed, capped | no | service |
| P4 | manufacturer_part_handling | parameter | parts_paid | 3: ≤150 / ≤60 / standard parts | yes: install registration/term AND failed component | install |
| P4 | leak_search_component_share | parameter | leak_share | 3: 0.50 / 0.75 / tier coverage (1 on all P&L tiers) | no | none |
| P4 | booking_premium_share | parameter | premium_share | 3: 0 / 0.50 / tier coverage | no (one ticket) | service |
| P5 | maintenance_continuity_share | parameter | continuity_share | 3: 0.75 / 0.90 / 1 | the input is the latest of plan records on two units and service lines | plan |
| P5 | equipment_age_transfer_share | parameter | equipment_age_share | 3: 0.80 / 0.90 / 1 | no | install |
| P5 | term_proration_method | method | proration_share | 3: remaining/term / 1−excess/term / 1 | no | none |
| P5 | transfer_claims_experience_share | parameter | transfer_experience_share | 3: 0.85 / 0.95 / 1 | no | none |
| P5 | transfer_timing_share | parameter | timing_share | 3: 0.93 / 0.97 / 1 | no | none |

- Counts per policy (all within bounds):
  - P1: 6 factors (5 parameter, 1 method).
  - P2: 4 (3 parameter, 1 method).
  - P3: 6 (3 parameter, 3 method).
  - P4: 6 (4 parameter, 2 method).
  - P5: 5 (4 parameter, 1 method).
- Per task:
  - Task 0 (P1+P2+P3) has a multi-source factor: P2 member_fee_share, and also P3 claims_deducted_method. It has cross-difficulty factors on service, install and plan.
  - Task 1 (P4+P5) has multi-source factors: P4 after_hours_sublimit_basis and manufacturer_part_handling. It has cross-difficulty factors on service, install and plan.
- Every `decides` names an input binding, never `result`. Binding sets are disjoint within each policy. Every factor's `baseline` equals its fall-through tier and matches the policy `baseline.rule` sentence for that input. Every tier is stated in the rule prose with its condition and value or method, and is a branch of the decides binding.
- Every ladder's tiers are pairwise disjoint as stated.
- Distinct outcomes:
  - Every ladder selects three distinct values or methods for every tier set it applies to, with one exception: P4 booking_premium_share on a Harbison 10-Year Parts & Labor Protection contract. That tier has after_hours_premium_covered false, so the "symptom other than no heat/no cooling/CO" tier gives 0 and the fall-through ("the tier's own after-hours coverage") also gives 0. Two tiers of one ladder select the same value.
  - On that same tier, a booked-ahead urgent call is paid half the premium while a same-day emergency call is paid nothing. The ladder pays more for the less urgent booking, which is an outcome a business would not publish. This is finding F-3 (SOURCE-FACTOR shape at charter level). The other two P&L tiers (12-Year Total and Total Plus) cover the premium, so their fall-through gives 1 and the ladder is real for them. Task 1's contract is a 12-Year Total Protection, so F-3 does not bear on task 1.
  - Similarly, P1's diagnostic and premium fall-through gives 0 on both labor tiers, which is distinct from 1.00 and 0.50, so P1's ladders are real.
- Labels: P3 refund_start_anchor is labelled `method`, but its tiers swap one input date into the same unused-share formula, which is a parameter-like substitution. P3 keeps two honest methods (unused_share_day_count, claims_deducted_method) without it, so no count bound fails (O-4). Every other label is honest. Every method tier names a computation the rule states.
- Realism (conditions and outcomes a residential HVAC protection-contract business would hold), recorded as observation O-5. None is demonstrable as a red from the artifacts alone, because the charter is the only stated business. The weakest:
  - P1 purchase_timing_share: a permanent 5%/15% labor haircut because the contract was bought after installation or on existing equipment. Real service contracts handle purchase timing through waiting periods and price, not a payout haircut.
  - P3 equipment_age_refund_share: a cancellation refund reduced by the equipment's age. Pro-rata or short-rate refunds do not normally depend on unit age.
  - P5 maintenance/age/experience/timing haircuts on the carried claim benefit. A transferred service contract normally carries the remaining limit unchanged, which is exactly what base warranty_home_sale_transfer says.
  - P2 repeat_visit_fee_share: a lower deductible for a frequent claimant.

### findings

- **F-1, SOURCE-TASK (decision label on a labor-only claim; charter-global root cause, demonstrated per task).**
  - Symptom: the decision label is not uniquely entailed when the manufacturer's parts warranty is in term and the claim is on a labor-only tier.
  - Root cause: P1's "Parts are never paid on a labor-only tier" sits beside an untouched base sentence, "When the manufacturer warranty supplies the part, the claim is partially_approved with denial_reason manufacturer_parts_coverage_applies for the parts and pays the remaining covered components; otherwise a claim passing every test is approved". The base sentence carries no tier condition. "The manufacturer term is the registered_parts_years confirmed by the installation's registration entry", which is per installation and not per serial.
  - Affects tasks with a P1 decision while a registration is in term: task 0. Task 1 is a P4 decision, and P4's rule states the label explicitly.
  - Demonstration: task_0.md.
- **F-2, latent undeclared base/extended conflicts in P3** (pending contract counts its full term as unused; with-installation contracts' credit names no charge). The demonstration is hypothetical only. It bears on no task in this bundle.
- **F-3, P4 booking_premium_share ladder on Harbison 10-Year Parts & Labor Protection.** Tier 1 and the fall-through both select 0, and the booked-ahead tier pays more than a same-day emergency. It bears on no task in this bundle (task 1 is 12-Year Total Protection).
- **F-4, latent rule/compute non-equivalences.** P1 (a, b), P2 (a, b, c), P3 (a, b), P5 (maintenance date bound): see rule_compute_equivalence. Each was checked against both worlds, and none moves a scored value in either. Each task file records that check.
- Observations O-1 to O-8 (no consequence demonstrable):
  - O-1: replaced_by texts in P1/P4 are incomplete relative to the rule sentences they license.
  - O-2: the tool enum is a superset of the base denial reasons.
  - O-3: XLATEST/CFIELD-first-agreement selection.
  - O-4: refund_start_anchor is mislabelled `method`.
  - O-5: realism of P1 timing, P3 age, P5 haircuts and P2 repeat discount.
  - O-6: the P3→P2 state_gate names a field, not an eligibility id.
  - O-7: "approved" in the P3 gate sentence vs "approved or partially approved" in its condition.
  - O-8: base cross-problem orders (transfer fee before next claim; cancel before higher tier) ground no edge.

## closing_checklist

Written after the reveal of both tasks (2026-10-05T15:50:45Z). It sits below the pre-reveal charter-global section and leaves that section unchanged. **The difficulty is not closed**, because not every task passes all four relationships.

- Per-task files: 0.md and 1.md, one for each of tasks/0.json and tasks/1.json, plus this file. First revision; there are no older revisions. Each comparison section is present.
  - Task 0: SOURCE-TASK RED (T0-1, root cause F-1) and SOURCE-CHAIN RED (T0-2).
  - Task 1: PASS on all four relationships.
- Coverage and scopes: the five extended policies are covered. charter_scope task 0 = {labor-plan decision, visit claim service fee, cancellation refund}; task 1 = {parts-and-labor decision, transfer carryover}. These are pairwise disjoint over whole trees, and the task tools are disjoint. All uuid8s were independently generated (§ action_binding_and_uuids).
- Trees:
  - Task 0 has 2 prerequisite problems and 2 value_input edges, with owner=user cancellation and no cycle, but edge P3←P2 is not unmet at the opening (T0-2).
  - Task 1 has 1 prerequisite problem and 1 value_input edge, with owner=user transfer.
  - The difficulty-wide graph {P2→P1, P3→P1, P3→P2, P5→P4} is acyclic.
- Factors: every computation has a self-sufficient baseline and 4–6 factors (≥2 parameter, ≥1 method). Each task has at least one multi-source and one cross-difficulty factor. Every factor bears weight on its task's world, and every fall-back differs from gold. Charter-global defects that bear on no task in this bundle:
  - F-3 (P4 booking_premium_share collapses on the Harbison 10-Year Parts & Labor Protection tier).
  - O-4 (mislabelled refund_start_anchor).
- Open charter-global items:
  - F-1: root cause of T0-1.
  - F-2: latent undeclared base/extended conflicts in P3.
  - F-3: as above.
  - F-4: latent rule/compute non-equivalences in P1/P2/P3/P5.
- Gate re-run on the final form: not performed by this audit. The supplied snapshot (all green) predates the audit, and no artifact was changed by it.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit started at 2026-10-05T16:55Z. Auditor: claude-opus-5-5, the same independent auditor as round 1. This section was written before any round-2 GT was revealed.
- Hashes recomputed and matched against /tmp/erl37/views_r2/protection_contract_claims/charter.sha256:
  - warranty.extended.yaml 66229a8ca115b3dac4abf9c8e3a167e97d7f57560f0dda4ec8f9863be8ce96d2 (round 1: a6c54429…). **Changed.**
  - task_tools.py 2e498e3b304065739c140d28ef759a102d4b53f877e26f2da67ab4355947b22f (round 1: 8fa070d2…). **Changed.**
  - masked task_0 3b4aee28…4d69 (round 1: 8023491e…). **Changed.**
  - masked task_1 ca12f543…abcd. Unchanged.
- Both shared inputs changed, so every charter-global section below is **re-derived in full**. Nothing is carried forward by reference.
- Gate snapshot r2: /tmp/erl37/gates/protection_contract_claims.r2.snapshot.txt. All 7 gates are OK and CACHE-DIFF is INFO. Input is complete.
- Base copy: `diff <(sed -n 1,1444p warranty.extended.yaml) blueprint/products/warranty.yaml` gives no output, so the base section is still verbatim.
- contamination_disclosure (round 2): this auditor revealed and read the round-1 GT of both tasks (round 1 § source_gt_comparison). Round-2 derivations therefore cannot be blind to round-1 conventions or values.
  - They are re-derived from the round-2 charter and worlds anyway. Wherever a round-2 conclusion coincides with a round-1 GT value, the concurrence is not evidence.
  - tasks/*.json (round 2) were not opened before this section and both task revision_2 frozen sections were on disk. tasks/protection_contract_claims/worklog.md was never read.

### policy_conflict_scan (revision 2)

- The policy set, tiers, subjects, target tools and owners are unchanged from round 1 (table in round 1 § policy_conflict_scan).
- Overlaps:
  - The P1/P4 decide subjects are still split by disjoint tier sets.
  - P2 and P3 now both select the holder's agreement "in active status" (compute `status='active'` filters, EXISTS). This removes the first-agreement ambiguity, and their membership reads no longer differ in anchor: P2 reads it against the call's completed date, P3 on the confirmation date.
  - The diagnostic/premium "once per visit" notion now differs between tiers: P1 uses "the lead claim of the service call", P4 keeps "the first claim decided on that service call". The tier sets are disjoint, so no contract is subject to both. Observation N-O1.
- Scope exclusivity, from the policy surface: unchanged. {P3, P1, P2} and {P5, P4} are disjoint and complete.

### rule_compute_equivalence (revision 2)

- P1:
  - Maintenance recency. The rule now reads "the latest documented maintenance recorded by the date of handling, being the later of … the latest precision tune-up charge line … and fewer than nine months, a record dated after the failure included, takes … one". The compute is MX(plan, paid) with no date bound, and `paid_maint_date` is filtered by `task_code='precision_tuneup'`. The two faces are now equivalent, which **closes F-4 P1(a)** (the "paid" wording is also gone from both faces).
  - The diagnostic and premium nets are typed (`member_diagnostic_rate`, `member_premium_discount`) in both faces, which **closes F-4 P1(b)**.
  - New lead-claim binding. The rule says "the lead claim of the service call, which is the claim whose failed component carries the largest repair labor line charged on that call". The compute uses `labor_gross >= XMAX(repair_labor on the call)`. Equivalent, except when the largest repair_labor line on the call is one no claim component carries (e.g. a refrigerant_leak_search labor line): then no claim is lead under either face and the diagnostic/premium is never paid. Ties make two claims lead. Both are latent observations (N-O2).
  - The (c) parse ambiguity is still excluded as in round 1.
- P2:
  - Membership "in active status on the date of handling, read against the completed date" equals EXISTS(active) plus a term-covers test. **F-4 P2(a) is closed** by rewording to match the compute.
  - `approved_claims_12m`, `approved_count` and `approved_on_visit` now filter `decision_round=1`, matching "on their original decision". **F-4 P2(b) is closed.**
  - The CFIELD selectors filter `status='active'`. **F-4 P2(c)/O-3 is closed for the plan reads.**
- P3:
  - `notice_date` = the latest cancellation request created_at, else NOW; the full-refund test uses MN(notice, NOW), matching "the day the written cancellation request was received or else the date of confirmation". **F-4 P3(a) is closed.** Latent: LATEST takes any cancellation request regardless of request_status (a withdrawn earlier request would count). Observation.
  - claims_deducted tier 1 now reads "the larger of the total of every claim payout made … and the total approved on its original decisions", which equals MX. **F-4 P3(b) is closed.**
  - New pending branch. The rule says "A contract still pending counts its whole term as unused, so its unused share is one", and the compute's first branch is `1 if status == 'pending'`. Equivalent to the rule.
  - But the factor ladder lists the pending case inside the fall-through parenthetical ("otherwise (a contract still pending takes a share of one)") while stating the fall-through method as the whole-month share. The pending branch is therefore a fourth compute branch that the ladder does not state as a tier of its own, and the factor's fall-through/baseline (whole-month share) is not what a pending contract receives. Latent: neither task's contract is pending. Finding N-2 (charter-level, latent).
- P4: the nets are typed per line in both faces. The premium share and the member reads are filtered by active status. Equivalent.
- P5: continuity is "recorded by the date of handling … a record dated after the closing included" in both faces, with unbounded MX. **The F-4 P5 item is closed.**
- Sweep back: no rule sentence lacks a binding.

### action_binding_and_uuids (revision 2)

- (target_tool, computes): unchanged, one claimant each. The uuid8s are unchanged and still independent.
- Tool bodies were re-read: still no prerequisite, status, eligibility or amount check.
- The only docstring change: confirm_protection_cancellation_57f0aac4 `source_billing_id` now reads "pass an empty value where the tier was bought on the installation contract and no contract-price charge stands on the contract". This matches P3's new rule sentence.
- There are no ordering words in docstrings beyond the enum fact descriptions.
- O-2: the enum superset (`waiting_period_not_elapsed`, `contract_not_active`) is unchanged and remains an observation; the reworker stated no change.
- Fee tool docstring: "naming the claim whose approval made it due". Base warranty_agg_claim_service_fee_per_visit (not superseded on this point) says "naming the first approved claim of the visit". On a call where more than one claim is approved, these two descriptions can point at different claims. This is examined per task (task 0 has two approved claims on one call in round 2).

### prerequisite_graph (revision 2)

- The edges are unchanged: P2→P1, P3→P1, P3→P2, P5→P4. The graph is acyclic.
- Every policy_source is verbatim in its blocked rule. The P3→P2 sentence now reads "…on which a claim against it was approved or partially approved", and its condition reads "Every service call that carries an approved or partially approved original decision on the contract has a claim service fee charge entry … unless the fee is waived for the holder's Comfort Club tier". Sentence and condition now have the same strength, which **closes O-7**.
- form/fallback consistent. resolved_by and effect are genuine.
- O-6 (the state_gate names a field rather than an eligibility id) is unchanged. The reworker stated no change. It remains an observation.

### prerequisite_sentences (revision 2)

- All four sentences pass the four-point test, as in round 1. The P3→P2 sentence is now at condition strength.
- The single-write analysis is unchanged: "carries its original decision" is resolved by tier (P1 vs P4), and "carry the claim service fee owed" by P2.
- No new cross-problem order appears in any extended rule.
- O-8 (base cross-problem orders) is unchanged and remains an observation.

### override_declarations (revision 2)

- P1 vs warranty_evt_claim_coverage: the manufacturer label sentence is now **superseded and declared**. Its replaced_by text is also a rule sentence: "a claim on a labor-only contract that passes every coverage test is approved with no denial reason, whether or not the manufacturer's parts warranty is still in term". The merged semantics are unique. **The F-1 root cause is closed.**
- P1 vs warranty_evt_claim_payout:
  - The labor clause's replaced_by now carries the age, maintenance-recency, purchase-timing and labor-payable sentences.
  - The diagnostic/premium clause's replaced_by now carries both shares and "only on the lead claim of the service call". The base's "each only on the first claim of the visit" is part of the superseded text, so the lead-claim rule is declared.
  - **O-1 is closed for P1.**
- P1 vs warranty_evt_claim_appeal (base sentence "…whereas maintenance performed after the failure date never can [change the outcome]"):
  - P1 decides round 1 only, so this sentence does not literally govern P1's quantity, and no conflict is recorded.
  - However, P1's maintenance-recency share now expressly lets "a record dated after the failure" take the full share of one. That is the same evidence the base charter refuses on appeal. See N-1 under factor_ladders.
- P2: unchanged and declared.
- P3 vs warranty_cancellation:
  - Pending contracts now follow base ("counts its whole term as unused"), which closes F-2(i).
  - The credit names "no charge on the contract where the tier was bought on the installation contract", which follows base and closes F-2(ii). The tool docstring agrees.
  - **F-2 is closed.**
- P4: the leak-search share is now inside the refrigerant clause's replaced_by text (**O-1 closed for P4**). The premium replaced_by matches the new ladder.
- P5: unchanged and declared.
- Disguised forms: none.

### factor_ladders (revision 2)

- Labels and counts:
  - P3 refund_start_anchor is relabelled `parameter`, with its tiers stated as values (dates). This **closes O-4**.
  - P3 now has 4 parameter and 2 method factors. P1: 5p/1m; P2: 3p/1m; P4: 4p/2m; P5: 4p/1m. All are within bounds.
- **F-3 is closed.** P4 booking_premium_share tiers 1–2 now require "the tier covers the after-hours premium", and the fall-through is "the tier's own after-hours coverage".
  - On a 12-Year tier the three outcomes are 0, 0.50 and 1, all distinct.
  - On the 10-Year Parts & Labor tier only the fall-through (0) is reachable, so no two reachable tiers select the same value. The booked-ahead inversion is gone.
- **N-1 (new, charter-level SOURCE-FACTOR shape, latent).** P1 maintenance_recency_share's fall-through condition now includes "a record dated after the failure". A protection-contract business weighs maintenance recency as evidence the unit was cared for **before** it failed. A tune-up performed after the failure cannot be that evidence, and this charter's own base appeal rule says such maintenance "never can" change a claim outcome.
  - Consequence when it applies: a holder with a stale pre-failure record (e.g. 14 months → 0.85) and a tune-up between the failure and the filing date gets 1. The approved amount rises by about 17.6% of labor payable through a post-failure record.
  - Demonstrable only on a hypothetical world. Neither task world has a maintenance record dated after its failure date (task 0: furnace 2024-12-03, AC 2025-06-10, no precision_tuneup lines; task 1 is P4, which has no maintenance factor).
  - P5's analogous "a record dated after the closing included" is less objectionable: the seller still holds the contract until the transfer is confirmed, and maintenance in that interval is genuine continuity. Recorded as an observation (N-O3).
- Multi-source: P2 member_fee_share is still multi-source (active agreement × call completed date). P4 after_hours_sublimit_basis is still multi-source.
- The O-T0-a / O-T1-a labelling claims live in design_rationale (task files) and are rechecked after the reveal.
- **O-5 (realism)**:
  - P2 repeat_visit_fee_share now carries a stated business rationale ("keeps the service fees of a holder whose equipment needs repeated repairs within a year from stacking up"), which addresses the doubt about this factor.
  - The P1 purchase-timing, P3 equipment-age and P5 haircut texts are unchanged. Their doubt remains an observation, not demonstrable from the artifacts.

### findings (revision 2)

| round-1 item | round-2 status | evidence |
| --- | --- | --- |
| F-1 (root of T0-1) | closed | P1 overwrite on warranty_evt_claim_coverage plus rule sentence "approved with no denial reason, whether or not the manufacturer's parts warranty is still in term" |
| F-2 | closed | P3 rule: pending share one; credit against no charge for an installation-bought tier; tool docstring empty source_billing_id |
| F-3 | closed | P4 premium ladder gated on the tier covering the premium |
| F-4 (P1a, P1b, P2a, P2b, P2c, P3a, P3b, P5) | closed | each by rule rewording to match the compute, or by typed/filtered compute (see rule_compute_equivalence) |
| O-1 | closed | P1 and P4 replaced_by texts complete |
| O-2 | unchanged (stated no change) | observation stands |
| O-3 | closed for plan reads | `status='active'` selectors |
| O-4 | closed | relabelled parameter |
| O-5 | partly addressed (P2); rest unchanged | observation stands |
| O-6, O-8 | unchanged (stated no change) | observations stand |
| O-7 | closed | P3 gate sentence "approved or partially approved" |

- New in round 2:
  - **N-1** (charter-level unreal fall-through condition in P1 maintenance recency, latent, bears on no task).
  - **N-2** (P3 unused_share_day_count pending branch is not a stated ladder tier, and its fall-through/baseline is not what a pending contract gets; latent, bears on no task).
  - Observations: N-O1 (lead claim vs first claim across tiers), N-O2 (lead-claim edge cases: no lead claim or tied leads), N-O3 (P5 post-closing record), and the latent P3 LATEST request-status point.

### closing_checklist (revision 2)

Written after the round-2 reveal (2026-10-05T16:59:04Z). **The difficulty is not closed.**

- Per-task files 0.md and 1.md each carry revision_2. Round-1 text is untouched, apart from the round-1 freeze-time correction recorded in round 1.
  - Task 0: T0-1 closed and T0-2 closed, but a **new SOURCE-TASK RED, T0-3**: the fee's claim_id has two readings once a second approved claim was added to the call by the T0-2 rework.
  - Task 1: PASS on all four relationships, with no regression.
- Coverage and scopes: unchanged. The five policies are covered and the two scopes are disjoint. The task tools and uuid8s are unchanged and independent.
- Trees:
  - Task 0: n=2 with two value_input edges and an owner=user root. The P3←P2 gate is now genuinely unmet at the opening.
  - Task 1: n=1 with one value_input edge and an owner=user root.
  - The difficulty-wide graph is acyclic.
- Factors: every computation is within bounds after the O-4 relabel, and every factor bears weight on its task's world. Fall-backs differ from gold.
- Charter-global:
  - F-1, F-2, F-3 and F-4 are closed. O-1, O-3, O-4 and O-7 are closed.
  - O-2, O-6 and O-8 are unchanged observations. O-5 is partly addressed.
  - New: N-1 (P1 maintenance-recency fall-through counts a post-failure record; latent) and N-2 (P3 pending branch not a stated ladder tier; latent). Observations N-O1–N-O3.
- Gate re-run on the final form: the coordinator's r2 snapshot is all green. It does not see T0-3 (its argument is structurally valid).

## revision_3

### charter_global_frozen (revision 3)

- Re-audit started at 2026-10-05T18:27Z, by the same independent auditor. Written before any round-3 GT was revealed.
- Hashes (recomputed; they match /tmp/erl37/views_r3/protection_contract_claims/charter.sha256):
  - warranty.extended.yaml 4e1b65700f2b4dd629d0c4ecbdfb55f7091435de5e347b1ce8d633c0687a5802: **changed** from r2 66229a8c….
  - task_tools.py 833a404cf9c73f0c6425c4101f5e9598e9a5280be0e3afb1ab94524abda88c13: **changed** from r2 2e498e3b….
  - masked task_0 3b4aee28…4d69 and task_1 ca12f543…abcd: both **unchanged** from r2.
- Both shared inputs changed, so the charter-global sections are re-derived in full below.
- Base copy is still verbatim (`diff` of lines 1–1444 against products/warranty.yaml is empty).
- Gate snapshot r3: all 7 OK, CACHE-DIFF INFO.
- contamination_disclosure: the auditor has seen the round-1 and round-2 GT of both tasks. The worklog has never been read, and the round-3 tasks/*.json were not opened before the freezes below.

### Re-derived charter-global checks (revision 3)

The extended section was re-read (2878 lines vs 2871 in r2). Located changes:

- P1 maintenance recency (rule, overwrite replaced_by, compute_basis, ladder and compute all agree):
  - New text: "twelve months or more before the failure takes the twelve-months-or-more maintenance share, and so does a latest record dated after the failure date, because maintenance done after a failure is no evidence of care before it". Compute: `0.85 if (months_since_maint >= 12 or last_maint_date > failure_date)`.
  - The record is still selected as "the latest … recorded by the date of handling" (unbounded MX).
  - Rule ⇔ compute are equivalent. The ladder states the compound tier-1 condition. Distinct outcomes (0.85 / 0.95 / 1) are preserved.
- P2: new rule sentence "The fee charge names the first approved claim of the service call, which is the claim on that call whose approving original decision was posted earliest, even where a later decision on the same call is the one that lets the fee be fixed." It names no tool, id or snake_case token and states no cross-problem order (it identifies an object; the existing prerequisite sentence is unchanged).
  - The tool docstring is now neutral: "naming one claim of that service call"; claim_id is "the claim-file entry's reference number of a claim on that service call". The tool no longer offers a competing description.
  - This agrees with base "naming the first approved claim of the visit" and gives a unique reading.
- P3 (rule ⇔ compute equivalent, no new branch inside a factor):
  - The pending case moved out of the factor into a separate binding, `unused_share_applied = 1 if status == 'pending' else unused_share`, quoted from "A contract still pending counts its whole term as unused, so its unused share is one."
  - The unused_share_day_count ladder now has three clean tiers ("otherwise (held more than twelve and up to thirty-six months)"), its fall-through equals its baseline, and the compute has exactly three branches.
  - `notice_date` / `request_received` now filter `request_status='pending_customer_confirmation'`, and the rule says "the holder's pending written cancellation request".
- No other policy changed: P4 and P5 rule/compute text is as in r2.
- Re-checks:
  - action_binding_and_uuids: unchanged (5 tools, one claimant each, uuid8s unchanged). Bodies have no checks; only the fee docstring changed. No ordering words.
  - prerequisite_graph and prerequisite_sentences: unchanged from r2 (all pass).
  - override_declarations: the P1 maintenance replaced_by text is updated identically to the rule. P2's new naming sentence restates the base clause and does not override it. Nothing undeclared.
  - Factor counts and labels: unchanged from r2 (P1 5p/1m, P2 3p/1m, P3 4p/2m, P4 4p/2m, P5 4p/1m).

### Findings (revision 3)

| item | r3 status | evidence |
| --- | --- | --- |
| T0-3 root (claim named on the fee) | closed at charter level; task-level confirmation in 0.md after the reveal | P2 rule naming sentence + neutral tool docstring |
| N-2 | **closed** | pending handled outside the factor; ladder fall-through = baseline; three branches |
| latent request-status point | **closed** | `request_status='pending_customer_confirmation'` in both faces |
| N-1 | **changed, not closed (N-1′)** | see below |
| N-O1, N-O2, N-O3, O-2, O-6, O-8, remaining O-5 | unchanged (stated no change) | observations stand |

**N-1′ (charter-level SOURCE-FACTOR shape, latent, bears on no task).**
- The maintenance record is still chosen as "the latest documented maintenance recorded by the date of handling". When that latest record is after the failure, the claim takes the twelve-months-or-more share whatever the pre-failure record shows.
- The rule's own justification ("maintenance done after a failure is no evidence of care before it") supports ignoring the post-failure record and reading the latest record on or before the failure. Base warranty_msr_last_maintenance_date measures "on or before the failure_date". It does not support treating the holder as unmaintained.
- Demonstration (hypothetical world): a completed tune-up on the failed unit 2 months before the failure, plus a precision tune-up the day after the failure. The rule gives 0.85. Reading the latest pre-failure record gives 1. So a holder is paid about 15% less labor for having had extra maintenance.
- That is an outcome a protection-contract business would not publish. The tier condition "a latest record dated after the failure date" is not one that business weighs as stated.
- Neither task world has a post-failure maintenance record:
  - Task 0: furnace 2024-12-03, AC 2025-06-10, no precision_tuneup lines.
  - Task 1: P4 has no maintenance factor.
- So no scored value moves.

### closing_checklist (revision 3)

Written after the round-3 reveal (2026-10-05T18:29:02Z).

- Per-task files 0.md and 1.md carry revision_3. All four relationships PASS in both tasks:
  - Task 0: T0-1, T0-2 and T0-3 are all closed, with no regression.
  - Task 1: unchanged PASS.
- Coverage and scope: the five extended policies are covered by two pairwise-disjoint whole-tree scopes. The task tools are closed, and each uuid8 is independent and frozen.
- Trees:
  - Task 0: two prerequisite problems, two value_input edges, owner=user root, every edge unmet at the opening and load-bearing.
  - Task 1: one prerequisite problem, one value_input edge, owner=user root.
  - The difficulty-wide graph {P2→P1, P3→P1, P3→P2, P5→P4} is acyclic.
- Factors:
  - Every computation has a self-sufficient baseline and 4–6 factors (≥2 parameter, ≥1 method).
  - Each task has a multi-source factor and cross-difficulty factors on seeded rows.
  - Every factor bears weight against an honest baseline, and every fall-back differs from gold.
- Gates: the coordinator's r3 re-run on the final form is all green (7 OK, CACHE-DIFF INFO).
- **Outstanding charter-level item that keeps this checklist from being clean:**
  - **N-1′**: the P1 maintenance-recency tier treats a latest record dated after the failure as twelve-plus months, discarding a recent pre-failure record. This is an unreal tier condition and outcome, demonstrated on a hypothetical world. It is latent and moves no scored value in either task.
  - Observations N-O1–N-O3, O-2, O-6, O-8 and the remaining O-5 stand as no-consequence observations.
- Per the skill, both tasks pass the source-layer audit. The difficulty closes **subject to N-1′**, which the coordinator may treat as a charter defect to fix before reuse with other worlds.

## revision_4

### charter_global_frozen (revision 4)

- Re-audit started at 2026-10-05T18:39Z, by the same independent auditor. Written before any round-4 GT was revealed.
- Hashes (recomputed; they match /tmp/erl37/views_r4/protection_contract_claims/charter.sha256):
  - warranty.extended.yaml 062183974f91c6a89794bec45a6c286b6937405deb55130cd7a3b208a4435141: **changed** from r3 4e1b6570….
  - task_tools.py 833a404c…8c13: **unchanged** from r3.
  - masked task_0 3b4aee28…4d69 and task_1 ca12f543…abcd: **unchanged**.
- Base copy is verbatim. Gate snapshot r4: all 7 OK, CACHE-DIFF INFO.
- contamination_disclosure: round-1 to round-3 GT were seen earlier. The worklog was never read.
- The tool module is unchanged, so § action_binding_and_uuids (r3) is carried forward on the unchanged hash. The charter changed, so the charter checks are re-run.
- Located change: P1 maintenance-recency only. This matches the reworker's claim. Spot checks confirm that the r3 fixes elsewhere are intact:
  - The P2 naming sentence is present.
  - The P3 `unused_share_applied` binding and the pending-request filters are present.
  - The P4 premium gate and the `status='active'` selectors are present.
  - The five policy ids and their order are unchanged.

### P1 maintenance recency, re-derived (revision 4)

- Rule (also the replaced_by of the labor overwrite):
  - "set by the latest documented maintenance completed on or before the failure date, read from the failed unit's most recent heating-season Comfort Club tune-up, its most recent cooling-season Comfort Club tune-up and the most recent precision tune-up charge line on the holder's Harbison invoices, each of these three records counting only when it is dated on or before the failure date …; twelve months or more, or no counting record at all, takes the twelve-months-or-more maintenance share …".
- Compute: `heat_maint_date` and `cool_maint_date` are XLATEST by `season`; `paid_maint_date` is XLATEST over precision lines; each is kept only if `<= failure_date`; then MX.
- The ladder states the same three tiers with "or there is none" on tier 1. The compute_basis quotes are verbatim.
- The rule's procedure and the compute are equivalent. Tier outcomes stay distinct (0.85 / 0.95 / 1). The fall-through equals the baseline (1).
- **N-1′ is closed for the case it was demonstrated on.** A pre-failure tune-up from a different source than the post-failure one now counts, and post-failure records never count, which is in line with base warranty_msr_last_maintenance_date "on or before the failure_date". The r3 example (Comfort Club tune-up 2 months before the failure plus a precision tune-up the day after) now gives 1.
- **Residual, N-1″ (charter-level, latent, bears on no task).** The rule's lead clause ("the latest documented maintenance completed on or before the failure date") and its read procedure ("the most recent … each … counting only when dated on or before the failure date") diverge when **the same source** holds both a pre-failure record and a later post-failure record. The procedure, followed by the compute, then discards the source entirely instead of falling back to its pre-failure record.
  - Demonstration A (hypothetical world): precision tune-up lines at failure − 2 months and failure + 1 day, and no Comfort Club tune-ups. Lead clause: latest on or before the failure is 2 months → share 1. Procedure/compute: the most recent precision line is after the failure → no counting record → 0.85.
  - Demonstration B (hypothetical, within the filing window): heating tune-up H1 = 2024-12-01, failure 2025-11-10, next heating tune-up H2 = 2025-11-25 recorded before handling on 2025-12-01, no cooling or precision record. Lead clause: 11 months → 0.95. Procedure: H2 masks H1 → none → 0.85.
  - Two readings of one rule sentence produce different scored values. This is a SOURCE-POLICY / SOURCE-FACTOR shape at charter level. The outcome it produces (a holder maintained within the window is paid as if unmaintained because a further tune-up followed the failure) is the same kind of unreal outcome N-1′ named, now confined to same-source masking.
  - Bears on neither task:
    - Task 0's failed unit (furnace 1f853b8a) has one heating tune-up (2024-12-03, before the 2026-02-14 failure), no cooling tune-up and no precision line. Both readings give 0.85.
    - Task 1 (P4) has no maintenance factor.
- Minor observation: P1 `cross_category.reads` for plan lists only `plan_service_entries.entry_date`, while the compute now also filters on `season`. The gate passes. This is recorded as an observation only.

### Other charter sections (revision 4)

- rule_compute_equivalence, override_declarations, prerequisite_graph, prerequisite_sentences and factor counts and labels for P2–P5 are unchanged from r3, verified by the spot checks above together with the unchanged hash of the tool module.
- The P1 override text was updated identically to the rule, so it is still declared.
- The P1 factor still has 3 tiers and the parameter label. P1 counts are 5p/1m.

### closing_checklist (revision 4)

Written after the round-4 reveal (2026-10-05T18:40:06Z).

- Both tasks PASS all four relationships, with no regression from r3. Every item closed in rounds 1–3 is still closed.
  - Task 0: T0-1, T0-2 and T0-3 remain closed.
  - Task 1: PASS throughout.
- Coverage, scopes, uuid8s, trees and the difficulty-wide DAG are as in the r3 checklist and still hold.
- Factors: every factor bears weight against an honest baseline in both tasks, and every fall-back differs from gold.
- Gates: the coordinator's r4 re-run on the final form is all green.
- Charter-level:
  - N-1′ is **closed for its demonstrated case**: a post-failure record from another source no longer displaces a recent pre-failure record.
  - **N-1″ remains (latent):** P1's lead clause "latest documented maintenance completed on or before the failure date" and its read procedure ("most recent" per source, discarded if after the failure) give different shares when one source holds both a pre-failure and a later post-failure record. Two such cases are shown on hypothetical worlds: two precision lines, or heating tune-ups in consecutive terms.
  - The round-4 rationale's "one tune-up per season per term" argument covers only same-term same-season masking, so it does not dispose of N-1″.
  - No scored value of either task moves.
- **The difficulty does not close unconditionally.** Both tasks pass the source-layer audit, but closure remains subject to the latent charter-level N-1″.
  - The standing observations (N-O1–N-O3, O-2, O-6, O-8, the remaining O-5, and the P1 `season` filter missing from cross_category.reads) carry no consequence.
