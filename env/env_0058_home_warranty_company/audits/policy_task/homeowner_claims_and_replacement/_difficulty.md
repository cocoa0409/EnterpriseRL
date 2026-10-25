# Policy-task audit — homeowner_claims_and_replacement / charter-global

## charter_global_frozen

- Frozen: 2026-10-12 13:37 UTC, before any task's GT was revealed. Auditor: independent erl-task-policy-audit agent (not the instantiating agent).
- Hashes verified on entry (match the coordinator brief):
  - `tasks/homeowner_claims_and_replacement/homeplan.extended.yaml` sha256=d6a3018a4ef34a1877bd6c29797673791d319bfd92587be5f55e0b61930b29ae
  - `tasks/homeowner_claims_and_replacement/task_tools.py` sha256=e2fef2ffb7a09f24b36cc9ba2e7a4d574afbb04f24e4f2a207fc10d30c4a3194
  - `.audit_views/.../0.view.json` sha256=fa0290...163b, `1.view.json` sha256=3b5a6d...b938
- Read: `blueprint/blueprint.yaml`, `blueprint/share_tools.py`, `blueprint/db_schema.json` (via the DSL evaluator), `blueprint/products/{homeplan,addon,lineplan}.yaml` (addon/lineplan only to check that seeded cross-category rows agree with their own charters), the extended charter, `task_tools.py`, the DSL primitives in `skills/erl-task-instantiate/scripts/check_compute.py`, and the two masked views.
- Not read (masked): `tasks/homeowner_claims_and_replacement/tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), `worklog.md`, any other scenario, any sibling difficulty's tasks or audits. No recursive search was run over the scenario directory.
- This section contains nothing derived from a revealed GT.

### Entry conditions (Step 0)

Gate snapshot supplied with the brief: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (`--check`), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; TRACEABILITY NOT OK only for the unlock tool names of the 5 task tools (pre-docs, expected); validate_scenario only "required document not found". Masked views were supplied with hashes, and those hashes match the files. The inputs are complete.

Base copy: every base key of the extended file (`category` … `policies`) is equal to `blueprint/products/homeplan.yaml`. The only difference in the text is a trailing newline. The base section is verbatim.

### policy_conflict_scan

The five extended policies, their target tools and owners:

| policy | target_tool | owner | computes | prerequisite |
| --- | --- | --- | --- | --- |
| homeplan_ext_stalled_repair_replacement | authorize_stalled_repair_replacement_b6f80e12 | agent | amount | [] |
| homeplan_ext_customer_elected_cash | elect_cash_in_place_of_replacement_b1a5678d | user | cash_amount | ← stalled (value_input, state form) |
| homeplan_ext_haul_away_on_completed_replacement | book_supplemental_allowance_cce1a240 | agent | amount | [] |
| homeplan_ext_company_elected_cash_offer | issue_company_cash_offer_eabc2067 | agent | amount | ← haul_away (state_gate, state form) |
| homeplan_ext_company_cash_acceptance | accept_company_cash_offer_2503240a | user | payment_amount | ← offer (value_input, state form) |

- Overlapping subjects. `homeplan_cash_in_lieu_payment` + `homeplan_authorization_reversal` are claimed by customer_elected_cash and by company_cash_acceptance. The two are kept apart by an explicit switch in customer_elected_cash's rule: "A customer-elected settlement is available only on a replacement that a network contractor can install: when every network contractor of the request's trade whose service ZIP codes include the property_zip is suspended, Bridgewell elects cash itself and the settlement is company-elected." The company_elected_cash_offer rule uses the same condition, so the two cash routes do not overlap.
- Triggers and eligibility. Stalled replacement waits on a repair authorization that has stalled (more than parts_lead_time_replace_days without completion) and been reversed for customer_declined_work. Haul-away waits on a completion report for a Bridgewell replacement. Neither of these is a write of this difficulty: no task tool creates `homeplan_work_completion` or `customer_declined_work` reversals, and every shared tool except identity/handoff is read-only. So neither condition is a cross-problem order.
- Selectors and their anchors:
  - stalled: "the service request whose repair authorization was most recently reversed because the customer declined the work"
  - customer-elected: "the replacement authorization most recently issued on the contract"
  - haul-away: "the replacement whose completion report is the most recent one on the contract"
  - offer and acceptance: "the replacement authorization most recently issued on the contract"
  - These selectors are compatible with one another within each tree, because each later write reads the row the earlier write created or the seeded standing row.
- Cross-category reads:
  - stalled reads lineplan (variant_name/status/property_address, CFIELD + EXISTS)
  - offer reads addon (status via EXISTS only)
  - acceptance reads addon (premium_balance via CFIELD)
  - Each read is declared in `cross_category`.
- Scope: the five policies split into two disjoint trees, {stalled, customer_elected} and {haul_away, offer, acceptance}. These jointly cover all five. Whether each task claims exactly one of these trees is confirmed per task after reveal.

### rule_compute_equivalence

Every compute binding has a `compute_basis` quotation that appears in the rule, and every ladder tier in `factors[].ladder` is a rule sentence and a branch of its `decides` binding. This was checked binding by binding for all five policies. Every overwrite `replaced_by` sentence is carried verbatim in its policy's rule. Every `superseded_clause` is verbatim in the named base policy. Every `baseline.rule` sentence is a sentence of the rule (checked mechanically).

There is one divergence, and it is shared by all five computations:

- The rule says: "A payment counts for the current term when its event date falls on or after term_start_date". In haul-away and the offer the wording is "a payment counts for the current term when its event date falls on or after term_start_date".
- Compute implements this as `term_window: "MONTHS(F('term_start_date'), NOW) + 1"` with `within_months=term_window`. Per `_within` in check_compute.py, a row is kept when `0 <= MONTHS(event_date, NOW) < term_window`, that is, when event_date lies after the same calendar day `term_window` months before today.
- This equals "on or after term_start_date" only when today's day-of-month is the day before term_start_date's. Otherwise the window reaches back into the prior term.
- Example: term_start_date 2026-04-16 and today 2026-10-20. MONTHS = 6, so term_window = 7, so every row dated after 2026-03-20 is counted. Prior-term payments dated 2026-03-21..2026-04-15 then enter item_paid and aggregate_paid, which the rule excludes.
- This is a rule/compute divergence → **SOURCE-POLICY RED** (F1 below). On both task worlds today's date is exactly term_start_date − 1 day-of-month (task 0: 2026-10-14 vs 2025-11-15; task 1: 2026-10-15 vs 2026-04-16), so the window coincides with the rule and the divergence produces no second number there. Each task file records this.

Smaller compute/rule gaps, recorded as observations:

- customer_elected `stall_span_days` takes the latest reversal of any kind on the request. The rule ties it to "the request carries no reversed repair authorization". These differ only if a request carries a non-repair reversal, and neither world has one.
- acceptance `rider_owed` reads the first attached rider only (CFIELD). The rule says "an attached rider". These differ only with two riders, and the world has one.
- haul-away computes for the single most recent completion. The offer's gate asks that *every* completed replacement in the term carry a haul-away allowance. If two completed replacements lacked one, the haul-away policy defines a payment for only one of them. The world has one, so no consequence.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy. Five distinct tools.
- The tool bodies only `ctx.create` rows. None reads state, refuses, errors or hints, so no tool judges a prerequisite.
- uuid8s: b6f80e12, b1a5678d, cce1a240, eabc2067, 2503240a. They do not share a prefix, a sequence number or adjacent values.
  - Observation O1: `b1a5678d` contains the run `5678`, which looks hand-typed rather than drawn. The other four look random. A consequence cannot be demonstrated.
- Docstrings name no other tool. However, every docstring carries the ordering word "Afterwards …". The offer docstring also says "nothing is paid and no benefit is used until the homeowner accepts it", which places the acceptance after the offer. The stalled docstring says the standing authorization is one "that the customer and the network contractor can act on".
  - Observation O2: this fails the letter of check 3 ("carries an ordering word such as before, after or first"). It does not hand either task a second answer, because the same orders are stated by the blocked rules' own prerequisite sentences. No consequence can be demonstrated, so it is not a RED.

### prerequisite_graph

- `prerequisite` is filled on every policy: `[]` on stalled and on haul_away.
- Edges: customer_elected → stalled, offer → haul_away, acceptance → offer. Each `problem` is an extended id. No edge points at a base policy or a self-loop. The graph is acyclic: two chains of length 1 and 2.
- Each `policy_source` is verbatim in its own rule and absent from the depended-on rule (checked mechanically).
- `form: state` is on all three edges, with no `fallback_reason`. Correct.
- `resolved_by` equals the depended-on policy's `target_tool` on all three.
- `kind`:
  - value_input `live_replacement_amount` exists in customer_elected compute.
  - value_input `accepted_offer_amount` exists in acceptance compute.
  - state_gate `gate: homeplan_claim_events.allowance_type` points at a record field, not at a named eligibility entry. Extended policies carry no `eligibility` list, so the gate is the rule sentence itself. Observation O3: this is acceptable, because the sentence is the gate.
- `condition` vs sentence:
  - customer_elected: the condition adds "and has no homeplan_work_completion row", while the sentence says only "a replacement authorization that carries no reversal stands". The same policy's first sentence ("holds a replacement authorization that is neither completed nor reversed") supplies the completion clause. Observation O4: the sentence is slightly broader than the condition. No world here has a completed but unreversed replacement on the request in question, so there is no consequence.
  - The other two edges match their sentences.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any prerequisite field.

### prerequisite_sentences

| edge | sentence | connective | waited-on state (record-visible) | writes of this difficulty that bring it about | derivation |
| --- | --- | --- | --- | --- | --- |
| customer_elected ← stalled | "A customer-elected cash settlement on a service request is fixed only after a replacement authorization that carries no reversal stands on that request." | only after | an unreversed `homeplan_replacement_authorization` on the request | only `authorize_stalled_repair_replacement_b6f80e12`. No other task tool creates replacement authorizations, and the shared tools are read-only. | Reader sees the request has a reversed repair authorization and no replacement → searches the rules for a policy whose result is a replacement authorization on such a request → stalled rule: "Bridgewell replaces the item by issuing a replacement authorization on the same request with replacement_basis parts_unavailable". One reading. |
| offer ← haul_away | "A company-elected cash-in-lieu offer is issued only once every Bridgewell replacement completed on the contract in the current term carries a haul-away allowance on the records." | only once | `homeplan_supplemental_allowance` with allowance_type haul_away on each in-term completed replacement's request | only `book_supplemental_allowance_cce1a240` (haul_away) | Reader finds an in-term completed replacement without haul_away → haul-away rule: "a haul-away allowance is owed on that service request as soon as the completion report is on file". One reading. |
| acceptance ← offer | "The cash paid on accepting a company-elected settlement is not fixed until an unexpired company-elected cash-in-lieu offer stands on the service request." | until | an unexpired `homeplan_cash_in_lieu_offer` with settlement_basis company_elected | only `issue_company_cash_offer_eabc2067` | Reader sees no offer → offer rule: "The offer is recorded on the request with settlement_basis company_elected …". One reading. |

- None of the sentences names a tool, a policy id, a snake_case token or a row id.
  - The sentences use the business words "replacement authorization", "haul-away allowance" and "company-elected cash-in-lieu offer". These are the words the finders' docstrings use.
- No rule restates another policy's sentence.
- No rule states an undeclared cross-problem order between two problems of this difficulty.
- No base sentence grounds an edge.
- Observation O5 (realism of the offer ← haul-away gate):
  - Within the charter, the gate is well formed.
  - As a business rule, it is not one a US home warranty company would plausibly hold. It withholds a company-elected cash offer on one item (here a water heater with no installer) until a haul-away allowance has been booked on a different, already-completed replacement of another item.
  - Haul-away allowances are a back-office allowance owed to the installer or customer and are independent of a later claim on another item.
  - The skill provides no RED class for an unrealistic gate whose consequence is only realism, so this is recorded as an observation the coordinator should weigh under this run's realism criterion.

### override_declarations

Base sentences were swept sentence by sentence for each `base_policy_refs` entry.

- stalled (refs repair_or_replace, benefit_caps):
  - The amount sentence is replaced by declaration.
  - The "parts_unavailable" basis, "one open authorization per request", like-unit and reversal sentences are followed.
  - **Not declared**: benefit_caps "A payment counts in the term in which its service request's request_date falls, even when authorized after a renewal." The rule instead says "A payment counts for the current term when its event date falls on or after term_start_date".
- customer_elected (refs cash_in_lieu, benefit_caps, repair_or_replace, service_request_and_fees):
  - Offer-and-acceptance, offer-amount, payment-equals-offer and no-fee-refund are declared.
  - Reversal the same day, once per request, and as-if-reversed remaining benefits are followed.
  - The same benefit_caps term-anchor sentence is not declared.
- haul_away (refs supplemental_allowances, benefit_caps):
  - Both haul-away sentences are declared, including "a tier whose allowance is 0.00 pays nothing for that type", which is inside the superseded clause.
  - "once per type per request", "aggregate but not item cap" and "live authorization" are followed.
  - The term-anchor sentence is not declared.
- offer (refs cash_in_lieu, repair_or_replace, benefit_caps):
  - The offer-amount sentence is declared.
  - Company-elected basis, expiration and like-unit are followed.
  - The term-anchor sentence is not declared.
- acceptance (refs cash_in_lieu, benefit_caps, repair_or_replace, service_request_and_fees):
  - Payment-equals-offer and no-fee-refund are declared.
  - Acceptance-within-validity, customer records it, once per request, and "no repair or replacement authorized once cash is paid" are followed.
- Disguised forms: no 0/1 multiplier and no dropped branch were found. The anonymous intermediate is the term anchor itself, and it is reported as F2.

Undeclared override (F2): base `homeplan_evt_benefit_caps` says "A payment counts in the term in which its service request's request_date falls, even when authorized after a renewal". Each extended rule says "A payment counts for the current term when its event date falls on or after term_start_date". In the same situation the two give different counts:

- Example: request dated 2026-04-10 under a term ending 2026-04-15, authorized 2026-04-20 after renewal.
- Base counts that payment in the prior term.
- The extended rule counts it in the current term.

→ **SOURCE-POLICY RED**. Neither task world contains a payment whose request date and event date fall in different terms. Task 0's request 85bcdeb2 of 2025-10-10 was paid 2025-10-20, and both are in the prior term. Task 1's requests were all paid within their own term. So the defect produces no second number on either world. Each task file records that.

### factor_ladders

Counts are per policy as declared, before the realism tests below.

| policy | factors | parameter | method | multi-source (as declared) | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| stalled | 6: price_list_escalation (P), stall_day_count_basis (M), tenure_upgrade_ladder (P), line_plan_bundle_ladder (P, lineplan), missed_contact_ladder (P), unit_recurrence_ladder (P) | 5 | 1 | tenure_upgrade_ladder (start_date × returned_payment charges) | lineplan (CFIELD value) |
| customer_elected | 4: cash_starting_figure_basis (M), elected_cash_rate_ladder (P), stall_fee_share_ladder (P), repeat_repair_bonus_ladder (P) | 3 | 1 | elected_cash_rate_ladder (customer-elected cash payments × service requests) | none |
| haul_away | 5: removed_equipment_class (P), carry_out_ladder (P), after_hours_removal_ladder (P), unit_size_ladder (P), late_booking_day_count (M) | 4 | 1 | carry_out_ladder (property_type × request trade) | none |
| offer | 6: tenure_cash_rate (P), self_install_permit_ladder (P), installation_delay_day_count (M), rider_holder_ladder (P, addon), billing_loyalty_ladder (P), repeat_failure_ladder (P) | 5 | 1 | billing_loyalty_ladder (billing_frequency × returned_payment charges) | addon (EXISTS only) |
| acceptance | 4: acceptance_rate_ladder (P), setoff_scope_method (M, addon), visit_fee_return_ladder (P), prompt_acceptance_ladder (P) | 3 | 1 | visit_fee_return_ladder (dispatch rows × request urgency) | addon (CFIELD value) |

Structural checks, as declared:

- Every ladder has three tiers.
- Every rule states every tier with its condition and value or method.
- Every `decides` names an input, not `result`.
- Binding sets are disjoint.
- Every fall-through equals the factor's `baseline`.
- Every `baseline.rule` is a sentence-for-sentence subset of the rule.

Label honesty:

- The method labels on the starting figure, stall-day count, late-booking count and delay-day count change the algorithm: a subtraction vs a multiplication, or a different counting anchor or unit. They are honest.
- **setoff_scope_method is not**, and is reported as F4.

Tier distinctness and realism. The test is whether each condition is one a US home warranty company weighs for that quantity, and whether each value is a treatment it would publish for customers in that situation. The rest of this section rests on this test.

These factors pass:

- price_list_escalation: a quoted like-unit cost re-priced to the current price list as it ages.
- stall_day_count_basis: a parts-delay service-recovery credit counted from the request date for emergencies, and from the authorization for fast-service tiers.
- missed_contact_ladder: service recovery for missed contact windows.
- cash_starting_figure_basis: cash in lieu excludes the delivery/connection or licensed-installation share the company no longer incurs. This is consistent with "cash at our cost" practice.
- stall_fee_share_ladder: a service-fee refund when the company's own repair stalled.
- removed_equipment_class: refrigerant recovery and tank disposal cost more.
- carry_out_ladder: carry-out from attached units.
- unit_size_ladder: larger units cost more to remove.
- self_install_permit_ladder: the homeowner must pull the permit once Bridgewell is not installing.
- installation_delay_day_count: no-heat, no-hot-water and no-refrigeration days counted from day 1.
- visit_fee_return_ladder: fee returned when Bridgewell's own contractor missed contact.

Recorded as observations, because the concept is real and only the magnitude or placement is doubtful:

- after_hours_removal_ladder (O6): the removal happens at the installation visit, and the condition reads the original request's visit window.
- late_booking_day_count (O7): late-payment interest exists in insurance practice, but $0.50/day on a ~$100 allowance is far above prompt-pay interest.
- repeat_repair_bonus_ladder and repeat_failure_ladder (O8): repeat-failure ("lemon") rules exist, but they trigger replacement, not a cash bonus.

These fail the test → **SOURCE-FACTOR RED (unreal ladder)**, finding F3. Each makes a claim payment depend on something a home warranty company does not weigh when settling that quantity. Loyalty, bundle and payment-method benefits in this line are delivered through premium pricing, not through the dollars committed to a like-unit replacement or a cash settlement.

- stalled `tenure_upgrade_ladder`: +$200 or +$100 on a replacement authorization for 60+ or 24+ months' tenure.
- stalled `line_plan_bundle_ladder`: +$150 or +$75 on a refrigerator or furnace replacement for holding a utility line plan at the address. This is the policy's only cross-difficulty factor.
- stalled `unit_recurrence_ladder`: +$250 or +$125 because Bridgewell replaced the same item 0–36 or 36–60 months earlier. A prior replacement has no bearing on the contracted cost of today's like unit.
- customer_elected `elected_cash_rate_ladder`: the cash rate is cut from 1.00 to 0.95 for customers with 4+ requests in 12 months, and to 0.90 (the fall-through) for anyone who took customer-elected cash in the past 36 months. Claim frequency and prior settlements are underwriting and renewal considerations, not settlement-amount ones.
- offer `tenure_cash_rate`: the cash basis is raised 5% or 10% for tenure.
- offer `rider_holder_ladder`: +$75 or +$40 for having a rider attached. This is the policy's only cross-difficulty factor.
- offer `billing_loyalty_ladder`: +$100 for annual pay or +$40 for monthly pay.
- acceptance `acceptance_rate_ladder`: Bridgewell pays 97% or 95% of an offer the customer has *accepted*, depending on prior cash settlements. Even the base charter states "The payment equals the accepted offer amount". No warranty company publishes a policy of paying less than the offer the customer accepted.
- acceptance `prompt_acceptance_ladder`: +$50 for accepting on the offer date, or +$25 within 7 days. Where the offer is a prerequisite issued in the same contact, its tier is also fixed by the tree rather than by the records (see task 1).

F4 — acceptance `setoff_scope_method`: the ladder collapses, and the method label is dishonest.

- Tier 1: when both owe, set off "both balances". Tier 2: when only the rider owes, set off "the rider's balance". Fall-through: "the contract's own premium balance owed, if any".
- On tier 2's domain the contract owes 0, so tier 1's method gives the same number as tier 2's. On the fall-through's domain the rider owes 0, so tier 1's method gives the same number as the fall-through's.
- All three tiers are one formula, `contract_owed + rider_owed`. Two tiers (tier 1 and tier 2) select the same method.
- The only real variation is whether a rider balance is added, which is a number, not an algorithm. So the `method` label is dishonest.
- Struck from the counts, this leaves the acceptance policy with **no method factor**.

Counts after striking the factors that fail (F3, F4):

| policy | surviving factors | P | M | multi-source surviving | cross-difficulty surviving |
| --- | --- | --- | --- | --- | --- |
| stalled | escalation, stall_day, missed_contact | 2 | 1 | none (tenure struck; stall_day tier 1 is a single condition; missed_contact is single-source) | none (bundle struck) |
| customer_elected | starting_figure, stall_fee_share, repeat_bonus | 2 | 1 | none (cash_rate struck) | none |
| haul_away | all 5 (O6 and O7 are observations) | 4 | 1 | carry_out | none |
| offer | permit, delay, repeat | 2 | 1 | none (billing struck; delay's item and age come from one authorization row) | none (rider struck) |
| acceptance | visit_fee_return | 1 | 0 | visit_fee_return | none (setoff struck) |

This leaves 3, 3, 5, 3 and 1 factors, against the bound of 4 to 6. The stalled, customer_elected, offer and acceptance policies fall below 4. Neither task keeps a cross-difficulty factor.

### findings

- **F1 SOURCE-POLICY RED — the compute term window differs from the rule's term window** (all five policies; bears on tasks 0 and 1).
  - Symptom: `term_window = MONTHS(term_start_date, NOW) + 1` with `within_months`.
  - Root cause: a month-granular approximation of "event date on or after term_start_date".
  - Evidence: rule sentence and compute bindings quoted above, and `_within` in check_compute.py.
  - Consequence demonstrated: with term_start 2026-04-16 and NOW 2026-10-20, the rule excludes 2026-03-21..04-15 and compute includes it.
  - Affected: the `term_window`, `item_paid` and `aggregate_paid` bindings of every extended policy.
  - On both task worlds it is not reached (day-of-month coincidence). See the task files.
- **F2 SOURCE-POLICY RED — undeclared override of the benefit_caps term anchor** (all five policies; bears on tasks 0 and 1).
  - Symptom: the event-date anchor replaces the request-date anchor with no `overwrite` entry.
  - Root cause and evidence: quoted above.
  - Consequence demonstrated: in the hypothetical, the request falls in the prior term and is authorized after renewal, giving different remaining benefits.
  - Affected: the `overwrite` lists of all five policies.
  - Not reached on either world.
- **F3 SOURCE-FACTOR RED — unreal ladders.**
  - Stalled: tenure_upgrade_ladder, line_plan_bundle_ladder, unit_recurrence_ladder.
  - Customer-elected: elected_cash_rate_ladder.
  - Offer: tenure_cash_rate, rider_holder_ladder, billing_loyalty_ladder.
  - Acceptance: acceptance_rate_ladder, prompt_acceptance_ladder.
  - Each condition or value is named above together with why no US home warranty company weighs it for that quantity.
  - It bears on task 0 (stalled, customer_elected) and task 1 (offer, acceptance). Each task file shows the tier taken and the dollars it moves.
- **F4 SOURCE-FACTOR RED — setoff_scope_method collapses into one formula and is mislabelled `method`.**
  - Demonstrated algebraically above. On task 1's world, replacing the ladder by `contract_owed + rider_owed` reproduces the same payment.
  - Bears on task 1.
- **F5 SOURCE-FACTOR RED — factor bounds after striking.**
  - The stalled, customer_elected, offer and acceptance policies keep fewer than 4 factors.
  - Acceptance keeps no method factor.
  - Neither task keeps a cross-difficulty factor or a multi-source factor in its claimed computations, except task 1's haul_away (carry_out) and acceptance (visit_fee_return).
  - Bears on both tasks.
- Observations O1–O8 as above.

## closing_checklist

Not written. The difficulty does not pass: see the RED findings above and in `0.md` and `1.md`. Per Step 4, the closing checklist is written only once all M tasks pass.

Post-reveal note (written after both tasks' comparisons):

- `charter_scope` confirms the two disjoint trees found pre-reveal: task 0 has {stalled, customer_elected}; task 1 has {haul_away, offer, acceptance}. Together they cover all five policies.
- Per-task verdicts:
  - task 0: SOURCE-TASK RED, SOURCE-FACTOR RED, inherited SOURCE-POLICY RED (not reached); the problem tree holds.
  - task 1: SOURCE-FACTOR RED, SOURCE-CHAIN RED (proof text only), SOURCE-TASK RED (proof text only), inherited SOURCE-POLICY RED (not reached).

## revision_2

### charter_global_frozen (revision 2)

- Frozen: 2026-10-12 18:15 UTC, before either task's round-2 GT was revealed. Auditor: the same independent audit agent.
- The text of revision 1 above is left untouched. Round-1 report hashes at the start of round 2:
  - _difficulty.md 1e53bedb…
  - 0.md 4c87f4a4…
  - 1.md 8496f754…
- Inputs, with hashes verified against the coordinator brief:
  - extended.yaml sha256 e8fb121a…60ff
  - task_tools.py sha256 7eb93e60…cf91
  - 0.view.json 4b63ef21…d069
  - 1.view.json 1c1442ee…2951
- Both shared inputs changed since round 1, so every charter-global section is **re-derived in full** below. None is carried forward by reference.
- The base section is still verbatim to blueprint/products/homeplan.yaml (all 10 base keys equal).
- Gate snapshot supplied: all green except TRACEABILITY, whose only misses are the unlock tool names (pre-docs). Entry conditions are complete.
- Read domain as in round 1, plus `blueprint/products/lineplan.yaml` parameters and the `addon_riders.water_source` enum in db_schema.json, both to test the new cross-difficulty ladders. No task JSON had been opened when this section was written.

### policy_conflict_scan (r2)

- Five policies, five tools: stalled → authorize_stalled_repair_replacement_b6f80e12 (agent); customer_elected → **elect_cash_in_place_of_replacement_7cf483ad** (user, renamed); haul_away → book_supplemental_allowance_cce1a240 (agent); offer → issue_company_cash_offer_eabc2067 (agent); acceptance → accept_company_cash_offer_2503240a (user).
- Prerequisite edges are unchanged in shape: customer_elected ← stalled (value_input), offer ← haul_away (state_gate), acceptance ← offer (value_input).
- The customer-elected and company-elected routes are still separated by the suspended-network clause.
- Cross-category reads:
  - stalled reads lineplan via CPARAM `interior_plumbing_occurrence_cap`.
  - offer reads lineplan (same parameter) and addon via EXISTS on `water_source`.
  - Acceptance and customer_elected read no other category.
- Scope: the same two disjoint trees, {stalled, customer_elected} and {haul_away, offer, acceptance}. Together they cover all five policies.

### rule_compute_equivalence (r2)

- Mechanically checked:
  - every `compute_basis` quotation is a sentence of its rule
  - every `replaced_by` sentence is in its rule
  - every `superseded_clause` is verbatim in the named base policy
  - every `baseline.rule` sentence is in its rule
- Round-1 F1 is closed. All five policies now state "A payment counts toward the remaining benefits when its event date falls within the twelve months before today, that is after the same calendar day twelve months earlier, whatever term its request fell in" (haul-away uses the aggregate-only wording). The compute uses `within_months=12`, which per `_within` keeps exactly the rows with MONTHS(event_date, NOW) < 12, i.e. dated after the same calendar day twelve months earlier. The rule and the compute now agree for every date.
- Round-1 observations on the compute are closed:
  - customer_elected now ties the stall reversal to `reversed_authorization_number = stalled_auth_number`.
  - Acceptance no longer reads a rider balance.
- New arguments that the rules now state:
  - The stalled rule says "recording as its replacement_cost the re-priced like-unit cost described below and as its amount the stalled-repair replacement payment".
  - The offer rule says "the re-quoted like-unit cost described below as its replacement_cost".
  - The haul-away rule says "records the contracted disposal charge described below as its invoice_amount".
- New residual observation, O-r2-1: the edge condition for offer ← haul_away reads "the replacement authorization named on the most recent homeplan_work_completion row". The haul-away compute likewise takes the latest completion of any kind. The sentence, however, says "the Bridgewell replacement most recently completed". These diverge if a repair completion is dated after the last replacement completion. That does not happen on task 1's world, where the latest completion is replacement 1260629471.

### action_binding_and_uuids (r2)

- Each `(target_tool, computes)` pair is claimed by exactly one policy.
- The tool bodies only call `make_id`, `now` and `create`. No tool judges a prerequisite.
- O1 is closed. `elect_cash_in_place_of_replacement_7cf483ad` has a freshly drawn tail. The other four uuid8s (b6f80e12, cce1a240, eabc2067, 2503240a) share no prefix and no sequence.
- O2 is closed. No docstring carries before / after / first / until / then / once / afterwards / next / later; each now ends "On success …". No docstring names another tool.

### prerequisite_graph (r2)

- `prerequisite` is filled on every policy, `[]` on stalled and haul_away.
- The graph is acyclic: two chains.
- Each `policy_source` is verbatim in its own rule and absent from the depended-on rule (mechanical check).
- `form` is `state` on all edges, with no `fallback_reason`.
- `resolved_by` equals the depended-on `target_tool` on every edge.
- value_input gates exist in compute: `live_replacement_amount` and `accepted_offer_amount`.
- O3 (the state_gate is named by a field) is unchanged, as the reworker stated.
- O4 is closed. The customer-elected sentence now reads "a replacement authorization that carries neither a reversal nor a completion report stands on that request", which matches its condition.

### prerequisite_sentences (r2)

| edge | sentence | connective | the one resolving write |
| --- | --- | --- | --- |
| customer_elected ← stalled | "A customer-elected cash settlement on a service request is fixed only after a replacement authorization that carries neither a reversal nor a completion report stands on that request." | only after | only the stalled tool creates replacement authorizations |
| offer ← haul_away | "A company-elected cash-in-lieu offer is issued only once the Bridgewell replacement most recently completed on the contract carries its haul-away allowance on the records." | only once | only book_supplemental_allowance_cce1a240 writes allowances |
| acceptance ← offer | "The cash paid on accepting a company-elected settlement is not fixed until an unexpired company-elected cash-in-lieu offer stands on the service request." | until | only issue_company_cash_offer_eabc2067 writes offers |

- All three pass the four-point test. No tool, policy id or code token appears in any of them. There is no undeclared cross-problem order.
- O5 (realism of the haul-away gate) is mitigated in substance. The gate now concerns *the most recently completed* replacement. In task 1's re-storied world that replacement is the original installation of the water heater whose recall carries the standing authorization. Closing out the original job's haul-away before settling its recall in cash is a defensible back-office order. Residual: the gate is still bookkeeping rather than a customer-facing condition. Recorded as a closed observation.

### override_declarations (r2)

- Round-1 F2 is closed. Each extended policy now names, in its `overwrite`, these base `homeplan_evt_benefit_caps` sentences:
  - "A payment counts in the term in which its service request's request_date falls, even when authorized after a renewal."
  - "the cap is shared by every repair, replacement, cash-in-lieu settlement and out-of-network reimbursement for that item in the term, counted by homeplan_msr_item_benefit_paid_term". Haul-away omits this one, correctly, because allowances never touch an item cap.
  - "Every payment on the contract, supplemental allowances included, counts toward aggregate_term_limit, counted by homeplan_msr_term_benefit_paid."
  Each is replaced by a scoped "measured against the payments dated within the twelve months before today" sentence.
- Observation O-r2-2: the base sentence "The remaining item benefit is the item cap less homeplan_msr_item_benefit_paid_term and the remaining aggregate benefit is aggregate_term_limit less homeplan_msr_term_benefit_paid, each floored at zero" is not itself named. The scoped replaced_by sentences fix the measurement window explicitly, so the merged semantics are unique.
- Observation O-r2-3 (realism): a rolling twelve-month window for item caps and the aggregate limit departs from the per-term limits that US home warranty contracts actually state, and from this charter's own base. It is declared and scoped, and is not a factor, so it is not red-lighted.
- Observation O-r2-4 (disguised allowances on cash settlements; contestable):
  - The base `homeplan_evt_supplemental_allowances` says "Allowances are never paid on a cash-in-lieu settlement or an out-of-network reimbursement, because Bridgewell performs no installation there." That sentence is named in no overwrite, and supplemental_allowances is not in the base_policy_refs of customer_elected, offer or acceptance.
  - Yet those three policies add installation-type costs inside a cash settlement:
    - customer_elected: "disposal addition"
    - offer: "code-compliance addition … pays for the pan and discharge line"
    - acceptance: "self-installation permit addition … pays for the permits" and "disposal addition"
  - customer_elected and offer do declare the twin clause in cash_in_lieu ("supplemental allowances and service call fees are never added") superseded. Acceptance declares only "The payment equals the accepted offer amount".
  - If these additions are read as allowances, this is an undeclared override. The amounts at stake are given in each task file.
  - It is recorded as an observation because the additions are named cash components, not allowance types: the haul_away and permit allowances pay for work Bridgewell itself performs. The coordinator may rule otherwise.
  - Disclosure: round 1's offer already carried a permit addition built from `permit_fee_allowance`, and my round-1 audit did not record this point.

### factor_ladders (r2)

| policy | factors (label) | P | M | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| stalled | price_list_escalation (P), interior_line_hookup_ladder (P, lineplan), stall_day_count_basis (M), missed_contact_ladder (P), attached_dwelling_carry_in (P), install_window_premium (P) | 5 | 1 | attached_dwelling_carry_in (contract property_type × reversal-row item) | lineplan (CPARAM) |
| customer_elected | cash_starting_figure_basis (M), stall_fee_share_ladder (P), regulated_disposal_ladder (P), food_spoilage_ladder (P) | 3 | 1 | none (food_spoilage's item and date are on one request row) | none |
| haul_away | removed_equipment_class, carry_out_ladder, unit_size_ladder, after_hours_removal_ladder (P); late_booking_day_count (M) | 4 | 1 | carry_out_ladder | none |
| offer | offer_requote_ladder (P), supply_line_plan_coordination (P, lineplan), attached_dwelling_code_pan (P), network_miss_ladder (P), early_failure_method (M), thermal_expansion_ladder (P, addon) | 5 | 1 | attached_dwelling_code_pan (request item × contract property_type) | lineplan (CPARAM), addon (EXISTS) |
| acceptance | outage_day_count (M), recall_fee_return_ladder (P), failed_unit_disposal (P), owner_permit_ladder (P) | 3 | 1 | recall_fee_return_ladder (request type/urgency × dispatch rows) | none |

Structural checks:

- Every ladder has three stated tiers, each stated in the rule and implemented in compute.
- Every fall-through equals its baseline.
- `decides` is never `result`.
- The method labels are honest:
  - starting figure: subtraction vs multiplication
  - stall days / outage days: anchor or exclusion change
  - late booking: per day vs per full week
  - early_failure: a multiplicative share vs a flat amount
- Round-1 F3 is closed. Every ladder named there is gone: tenure, line-plan bundle, recurrence, cash rate, offer tenure, rider holder, billing loyalty, acceptance rate, prompt bonus.
- Round-1 F4 is closed. setoff_scope_method is gone.
- O6 is closed: the after-hours removal now states why the window matters ("the old unit is carried out at the installation visit held in the window the replacement request asked for").
- O7 is mitigated: late credit is now 0.10 per day and 0.50 per week.
- O8 is closed: the repeat bonuses are gone.

Realism of the new ladders:

- These pass:
  - escalation and re-quote: a quote re-priced as it ages
  - stall and outage day counts
  - missed-contact and network-miss service recovery
  - attached-dwelling carry-in, and attached-dwelling drain/condensate pan (code-required pans where a leak would reach a neighbour)
  - install-window premium
  - regulated disposal (refrigerant recovery, tank disposal)
  - food spoilage: a published benefit of real US home warranty plans
  - early-failure installation share or goodwill on a recall within the labor guarantee
  - recall visit-fee return
  - failed-unit disposal
  - owner permits
- Observation O-r2-5: on a recall that needed a missed-contact re-dispatch, offer's network_miss_ladder and acceptance's recall_fee_return_ladder both fire on the same `redispatch_missed_contact` row. This is double recovery for one service failure. It is plausible as two distinct remedies (a credit and a fee refund), so it is not red-lighted.
- Observation O-r2-6: the acceptance payment now exceeds the offer the customer accepted. It adds outage, fee return, disposal and permits on top of the offer. The offer no longer states what the customer is paid. This is customer-favourable and not a ladder defect.

**R2-F1 SOURCE-FACTOR RED: the two line-plan coordination ladders have only two real tiers.** This affects `interior_line_hookup_ladder` (stalled) and `supply_line_plan_coordination` (offer).

- Tier 2 reads "such a plan covers the address but its interior plumbing occurrence limit is below the hookup charge" (offer: "… below the reconnection charge").
- In `blueprint/products/lineplan.yaml`, the only plans that cover `interior_supply_line` are Bridgewell Interior Plumbing and Drainage Plan and Bridgewell Total Home Lines Plan. Both have `interior_plumbing_occurrence_cap: 3000.0`. Every other plan has 0.0.
- The charges are `water_hookup_charge` 145.00 and `supply_reconnection_charge` 130.00.
- So no customer of this scenario can satisfy tier 2. Each ladder is in substance two-tier: a plan exists → 0; no plan → the full charge.
- In addition, the three tiers as written are one coordination-of-benefits formula, `max(0, charge − limit)` (limit 0 when no plan). The middle tier and the fall-through select the same computation. This is the shape round-1 F4 red-lighted, here carrying a `parameter` label.
- Realism note: an interior-plumbing line plan covers failures of the home's supply and drain lines. Connecting a newly supplied refrigerator or water heater is installation, not a line failure.
- These are the **only cross-difficulty factors of the stalled policy** and **one of the two of the offer**.

**R2-F2 SOURCE-FACTOR RED: thermal_expansion_ladder's fall-through is not a treatment the business would publish.**

- The ladder pays expansion_tank_municipal or expansion_tank_well "when a coverage rider attached to the contract states the property's water source as municipal / as a private well", and "nothing when no attached rider states a water source".
- `addon_riders.water_source` is an enum {municipal, private_well} carried on every rider. So "no attached rider states a water source" means "no rider is attached".
- The rule therefore withholds the code-required thermal expansion control for a self-installed water heater from every customer who holds no rider. Rider-holding is not a condition a home warranty company weighs in pricing that item. The real condition, the water source, would apply to every water heater.
- The rider-existence part of the compound condition fails the realism test taken on its own, and so does the fall-through value for water heaters.
- This is the offer's only addon factor.

Counts after striking R2-F1 and R2-F2:

| policy | surviving factors | in bounds? | cross-difficulty surviving |
| --- | --- | --- | --- |
| stalled | 5 (P4, M1) | yes | **none** |
| customer_elected | 4 (P3, M1) | yes | none |
| haul_away | 5 (P4, M1) | yes | none |
| offer | 4 (P3, M1) | yes | **none** |
| acceptance | 4 (P3, M1) | yes | none |

Per-task consequence (R2-F3 SOURCE-FACTOR RED): neither task's computations retain a factor that decides its tier from another difficulty's records. Task 0's only one is interior_line_hookup_ladder. Task 1's are supply_line_plan_coordination and thermal_expansion_ladder. Each task still keeps a multi-source factor: task 0 attached_dwelling_carry_in; task 1 carry_out_ladder, attached_dwelling_code_pan and recall_fee_return_ladder.

### findings (r2), with status of the round-1 items

| round-1 item | r2 status | evidence |
| --- | --- | --- |
| F1 term-window rule/compute divergence | **closed** | 12-month rule ⇔ `within_months=12` |
| F2 undeclared term-anchor override | **closed** | three benefit_caps sentences named in every overwrite (O-r2-2 residual) |
| F3 unreal ladders | **closed** | all ten removed |
| F4 setoff collapse | **closed** (factor removed). The same shape **recurs** in R2-F1. | — |
| F5 bounds after striking | factor counts **closed**; cross-difficulty **not closed** → R2-F3 | — |
| O1 / O2 / O4 / O6 / O8 | closed | — |
| O3 | unchanged (as stated) | — |
| O5 | mitigated → closed observation | — |
| O7 | mitigated | — |

New findings:

- **R2-F1 SOURCE-FACTOR RED**: the line-plan ladders have only two real tiers and collapse to one formula. Bears on tasks 0 and 1.
- **R2-F2 SOURCE-FACTOR RED**: the expansion-tank fall-through is conditioned on holding a rider. Bears on task 1.
- **R2-F3 SOURCE-FACTOR RED**: no surviving cross-difficulty factor in either task.
- Observations O-r2-1 to O-r2-6.

### closing_checklist (r2)

Not written. The difficulty does not pass (R2-F1, R2-F2, R2-F3).

Post-reveal note (r2), written after both tasks' r2 comparisons:

- `charter_scope` confirms the two disjoint trees.
- Every r2 GT write, argument, factor sensitivity and closure value matches the frozen derivations.
- Per-task verdicts:
  - task 0: SOURCE-FACTOR RED (R2-F1 and R2-F3); the policy, the tree and the unique solution pass.
  - task 1: SOURCE-FACTOR RED (R2-F1, R2-F2 and R2-F3); the policy, the tree and the unique solution pass.
- Freeze-time stamps of 18:17 and 18:19 written in the task files were estimates. The reveal command's clock (18:15 UTC) and the hashes it printed before reading any task JSON are the authoritative record of order.

## revision_3

### charter_global_frozen (revision 3)

- Clock: the system clock read 2026-10-12 20:41:09 UTC just before this section was first written.
  - A first append at that time was garbled by shell expansion of backticks. It was removed by truncating the file back to its exact round-2 content (sha256 a8964f03…, re-verified), and this section was re-appended. The re-append time is recorded at the end of this section.
  - No task JSON was read at any point before or during this section.
- Revisions 1 and 2 above are untouched. Report hashes at the start of round 3:
  - _difficulty.md a8964f03…
  - 0.md 817fa4b6…
  - 1.md e0c7f208…
- Inputs, with hashes verified against the brief:
  - extended.yaml 16eb714c…a251 (**changed**)
  - task_tools.py 7eb93e60…cf91 (**unchanged** since r2)
  - 0.view c36dbc68…3fd
  - 1.view de812c1b…53f2
- Because the charter changed, every section that depends on it is re-derived below. § action_binding_and_uuids rests only on task_tools.py plus the unchanged target_tool / computes claims, so it is carried forward from revision 2 by reference, on the grounds of the unchanged tool hash and target tools.
- The base section is still verbatim.
- Gates: all green except TRACEABILITY, whose only misses are the unlock tool names. Entry conditions are complete.

### policy_conflict_scan (r3)

- The same five policies, tools and edges; the same two disjoint trees, which together cover all five.
- Cross-category reads now:
  - stalled reads addon claim history: XCOUNT of addon_contractor_dispatch rows with redispatch_missed_contact in the last 12 months.
  - acceptance reads lineplan claim history: XCOUNT of lineplan_contractor_dispatch rows with redispatch_missed_contact in the last 12 months.
  - offer reads no other category.
- R2-F1 is **closed**: both line-plan coordination ladders were removed.
- R2-F2 is **closed**: the expansion-tank ladder was removed.

### rule_compute_equivalence (r3)

- Mechanically checked:
  - every compute_basis quotation is in its rule
  - every replaced_by sentence is in its rule
  - every superseded_clause is verbatim in its base policy
  - every baseline.rule sentence is in its rule
- The 12-month window is unchanged and exact.
- O-r2-1 is **closed**. The haul-away selector now reads "the replacement that the most recent completion report on the contract closes". The offer's sentence and condition both read "the most recent completion report … when it closes a Bridgewell replacement". The sentence, the condition and the haul-away compute now name the same row.

### action_binding_and_uuids (r3)

Carried forward from revision 2, on the grounds above: task_tools.py hash 7eb93e60… unchanged, target tools unchanged. The five tools are claimed once each; tool bodies only create rows; there are no ordering words.

### prerequisite_graph and prerequisite_sentences (r3)

- The edges, kinds, forms and resolving writes are unchanged.
- Each policy_source is verbatim in its own rule and absent from the depended-on rule.
- The new offer sentence passes the four-point test: "A company-elected cash-in-lieu offer is issued only once the most recent completion report on the contract, when it closes a Bridgewell replacement, has that replacement's haul-away allowance on the records." It uses "only once", waits on a record-visible state, names no tool or id, and only book_supplemental_allowance_cce1a240 writes allowances. Its condition matches it exactly.
- O3 is unchanged.

### override_declarations (r3)

- **O-r2-2 closed.** All five policies now name the base sentence "The remaining item benefit is the item cap less homeplan_msr_item_benefit_paid_term and the remaining aggregate benefit is aggregate_term_limit less homeplan_msr_term_benefit_paid, each floored at zero".
- **O-r2-4 closed.**
  - customer_elected and offer now list homeplan_evt_supplemental_allowances in base_policy_refs. Each names "Allowances are never paid on a cash-in-lieu settlement or an out-of-network reimbursement, because Bridgewell performs no installation there." with a scoped replaced_by that states which installation costs the cash carries and that no allowance row is booked.
  - The acceptance no longer carries permit or disposal additions; these moved into the offer, where they are declared.
- O-r2-3 (realism of the rolling 12-month cap window) is unchanged, as the reworker stated.
- **New observation O-r3-1 (contestable).**
  - The stalled rule says "The water-line connection charge pays for connecting the like unit to the home's water supply, which the contracted like-unit cost does not include".
  - The charter's own definition of replacement_cost (events > homeplan_replacement_authorization > replacement_cost) is "Bridgewell's contracted replacement cost (equipment plus installation)". The stalled tool docstring says the same: "the like-unit cost (equipment plus installation)".
  - For a water heater, whose "hot and cold supply connections and relief discharge line are all remade", connecting is the installation, so the two statements disagree on whether the 145.00 is already in replacement_cost.
  - For a refrigerator or dishwasher, ice-maker or inlet hook-ups are commonly excluded from "standard installation", so the 65.00 tier is defensible.
  - The water-heater tier is applied on neither task's world. Recorded as an observation.
  - Disclosure: the round-2 hookup charge had the same premise and was not recorded then.

### factor_ladders (r3)

| policy | factors (label) | P | M | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| stalled | price_list_escalation (P), water_line_connection_ladder (P), stall_day_count_basis (M), missed_contact_ladder (P, addon), attached_dwelling_carry_in (P), install_window_premium (P) | 5 | 1 | missed_contact_ladder (homeplan dispatch × addon dispatch history); attached_dwelling_carry_in | addon (XCOUNT) |
| customer_elected | cash_starting_figure_basis (M), stall_fee_share_ladder, regulated_disposal_ladder, food_spoilage_ladder (P) | 3 | 1 | none | none |
| haul_away | removed_equipment_class, carry_out_ladder, unit_size_ladder, after_hours_removal_ladder (P); late_booking_day_count (M) | 4 | 1 | carry_out_ladder | none |
| offer | offer_requote_ladder, supply_reconnection_ladder, attached_dwelling_code_pan, failed_unit_disposal, owner_permit_ladder (P); outside_installer_method (M) | 5 | 1 | attached_dwelling_code_pan | none |
| acceptance | outage_day_count (M), recall_fee_return_ladder (P), early_failure_method (M), network_miss_ladder (P, lineplan) | 2 | 2 | network_miss_ladder (homeplan dispatch × lineplan dispatch history) | lineplan (XCOUNT) |

Structural checks:

- Every ladder has three tiers, distinct in outcome, each stated in the rule and implemented in compute.
- Every fall-through equals its baseline. decides is never result.
- Method labels are honest:
  - outside_installer_method: a percentage of cost vs a flat gap
  - early_failure_method: a share of the earlier amount vs flat goodwill
  - outage, stall and late counts: anchor or exclusion change
  - starting figure: subtraction vs multiplication
- Every policy has between 4 and 6 factors, at least 2 parameter and at least 1 method.

Realism of the new or changed ladders:

- **Pass:**
  - supply_reconnection_ladder: connectors and relief line, line set or flue connector
  - outside_installer_method: an outside installer charges more than network labor
  - failed_unit_disposal and owner_permit_ladder on the offer
  - recall_fee_return_ladder: the full original fee back when a Bridgewell-installed unit failed outright, half when a repair failed
  - early_failure_method and outage_day_count on the acceptance
  - missed_contact_ladder's repeat tier: service-recovery escalation when the household has already suffered a missed contact in the last year
- **Observation O-r3-2.** Both repeat-miss ladders count a prior miss only when it was on another product's request: a rider request for stalled, a line-plan request for acceptance. A prior miss on the household's own homeowner-contract requests would not raise the tier, although a real service-recovery policy would count it first. Each condition, taken on its own, is still one the business weighs (a prior missed contact for the household), so this is a scope observation, not a red light. Neither world holds an excluded homeplan miss.
- **Observation O-r2-6, judged on the merits as the reworker asked: acceptable.**
  - The offer now states only the cash that replaces the unit; the rule says "the credits owed on the request for Bridgewell's own service failures are not part of it".
  - The acceptance pays that offer as stated, plus the service-failure credits Bridgewell owes on the request: outage, visit-fee return, early failure and network miss. The stated reason is that accepting the cash closes the claim.
  - Settling outstanding goodwill credits in the closing payment of a claim is ordinary claim-closure practice. The customer is never paid less than the offer she accepted, and the payment is fully determined by published rules and records.
  - One residual realism point (O-r3-3): the outage credit accrues "up to and including today", i.e. to the acceptance date. A customer who holds an offer open for up to 30 days keeps accruing outage days that are no longer Bridgewell's delay. This is not reached on task 1's world, where offer and acceptance fall on the same day.
- O-r2-5 is **closed**. The network-miss credit now lives only in the acceptance, and the visit-fee return is keyed to the recall's earlier work, not to the missed contact. One missed-contact event now earns one credit.

**R3-F1 SOURCE-FACTOR RED: network_miss_ladder (acceptance) reads line-plan rows that contradict the line-plan charter, and its stated rationale cannot hold under that charter.**

- The repeat tier reads "an assignment on a request under the customer's Bridgewell line plan was also re-dispatched after a missed contact window … so that the miss repeats a failure of **the plumbing network** the household has already met".
- blueprint/products/lineplan.yaml § lineplan_evt_dispatch states: "The request goes to a network contractor with trade **utility_line** (electrical for an electrical line) …".
- So under the line-plan charter, a line-plan assignment is never made to the plumbing network, and the condition does not measure the "repeat plumbing-network failure" the rule gives as its reason.
- The world that exercises the tier (task 1) seeds line-plan dispatches to plumbing-trade contractors, which the line-plan charter does not allow. See 1.md revision_3 for the rows.
- This is the acceptance's only cross-difficulty factor, and task 1's only one.

The stalled policy's addon ladder has no such conflict. addon.yaml § addon_evt_dispatch routes a second-refrigerator rider request to the appliance trade, the same network as the refrigerator request. Task 0's seeded addon rows go to the appliance contractors serving 46220.

### findings (r3), with status of the round-2 items

| r2 item | r3 status |
| --- | --- |
| R2-F1 line-plan coordination ladders | **closed** (removed) |
| R2-F2 expansion-tank ladder | **closed** (removed) |
| R2-F3 no cross-difficulty factor | task 0: **closed** (missed_contact_ladder, addon, sound). Task 1: **not closed** → R3-F1 |
| O-r2-1 | closed |
| O-r2-2 | closed |
| O-r2-3 | unchanged |
| O-r2-4 | closed |
| O-r2-5 | closed |
| O-r2-6 | judged acceptable; residual O-r3-3 |

New items:

- **R3-F1 SOURCE-FACTOR RED** (task 1).
- Observations O-r3-1, O-r3-2 and O-r3-3.

### closing_checklist (r3)

Not written. Task 1 does not pass (R3-F1).
(re-appended at: 2026-10-12 20:42:24 UTC)

Post-reveal note (r3), written after both comparisons (reveal at 2026-10-12 20:43:03 UTC):

- `charter_scope` again confirms the two disjoint trees.
- Every r3 GT write, argument, closure value and factor sensitivity matches the frozen derivations.
- Task 0: **PASS** on all four relationships.
- Task 1: **SOURCE-FACTOR RED** (R3-F1); policy, tree and unique solution pass.


## revision_4

### charter_global_frozen (revision 4)

- Written at 2026-10-12 23:33:08 UTC (system clock), before either task's round-4 GT was revealed. Revisions 1 to 3 above are untouched.
- Report hashes at the start of round 4:
  - _difficulty.md ffb152f6…
  - 0.md d5e2ddb8…
  - 1.md 530ccc23…
- Inputs, with hashes verified against the brief:
  - extended.yaml 79d3e498…e0de (**changed**)
  - task_tools.py 7eb93e60… (unchanged)
  - 0.view c36dbc68… (unchanged)
  - 1.view ad6faba9… (changed)
- Because the charter changed, every section depending on it is re-derived below. § action_binding_and_uuids is carried forward from revision 2 by reference, on the grounds that the tool hash and every target_tool / computes claim are unchanged.
- The base section is still verbatim.
- Gates: green except TRACEABILITY, whose only misses are the unlock tool names.

### policy_conflict_scan (r4)

- The same five policies, tools, edges and owners; the same two disjoint trees, which together cover all five.
- Cross-category reads:
  - stalled reads addon dispatch history (XCOUNT)
  - acceptance reads lineplan dispatch history (XCOUNT)
  - no other cross reads

### rule_compute_equivalence (r4)

- Mechanical check over all five policies:
  - every replaced_by sentence is in its rule
  - every superseded_clause is verbatim in its base policy
  - every baseline.rule sentence is in its rule
  - every prerequisite sentence is in its own rule and absent from the depended-on rule
  - every compute binding has a compute_basis entry and vice versa
- **One compute_basis quotation is no longer verbatim.**
  - Acceptance `compute_basis.outage_item` still reads "the days are counted by the item and by how long the request has stood". The rule, after the O-r3-3 change, reads "the days are counted by the item and by how long the request had stood on the date of the accepted offer".
  - The compute (outage_age = DAYS(outage_start, outage_end), with outage_end the offer date) and `compute_basis.outage_end` both follow the new rule. Only the provenance string of one input binding is stale.
  - No second number follows: the compute is the rule's, and on task 1's world the offer date is today.
  - Recorded as **observation O-r4-1**, a stale quotation; check 2 is not met verbatim, but no consequence can be demonstrated.

### action_binding_and_uuids (r4)

Carried forward from revision 2 (unchanged tool module and target tools).

### prerequisite_graph and prerequisite_sentences (r4)

- Unchanged from revision 3: three state-form edges, one resolving write each, all sentences verbatim and passing the four-point test.
- O3 is unchanged.

### override_declarations (r4)

- Unchanged from revision 3. All base conflicts are named, including the remaining-benefit sentence and the allowance-on-cash sentence.
- O-r2-3 (the rolling 12-month cap window) remains an observation.
- **O-r3-1 closed.** The water-line connection charge now reads "pays for the water hook-ups that the contracted like-unit cost (equipment plus standard installation) leaves out". The tiers are now:
  - refrigerator ice-maker / dispenser line, an "add-on hook-up beyond standard installation": 65.00
  - dishwasher / clothes_washer supply and drain hoses replaced with the unit: 40.00
  - "nothing for a water_heater or any other item, whose connections are part of the contracted installation"
  The charge no longer contradicts "equipment plus installation", and the water-heater tier is gone.

### factor_ladders (r4)

| policy | factors | P | M | multi-source | cross-difficulty |
| --- | --- | --- | --- | --- | --- |
| stalled | escalation, water_line_connection, stall_day (M), missed_contact (addon), carry_in, install_window | 5 | 1 | missed_contact, carry_in | addon |
| customer_elected | starting_figure (M), stall_fee_share, regulated_disposal, food_spoilage | 3 | 1 | — | — |
| haul_away | equipment_class, carry_out, unit_size, after_hours_removal, late_booking (M) | 4 | 1 | carry_out | — |
| offer | requote, supply_reconnection, outside_installer (M), code_pan, failed_unit_disposal, owner_permit | 5 | 1 | code_pan | — |
| acceptance | outage_day_count (M), recall_fee_return, early_failure (M), network_miss (lineplan) | 2 | 2 | network_miss, recall_fee_return | lineplan |

- Every ladder has three tiers, distinct in outcome, stated in the rule and implemented in compute, with fall-through = baseline and honest labels.

**O-r3-2 closed.** Both repeat-miss ladders now count the household's prior missed contacts in the last twelve months on *another of its homeowner-contract requests* first, and then on a rider request (stalled) or a line-plan request (acceptance).

- Compute:
  - `household_misses = COUNT(homeplan redispatch_missed_contact within 12 months) − COUNT(those on the request itself)`
  - the repeat tier fires on `household_misses ≥ 1 or rider_misses / line_plan_misses ≥ 1`
- A real service-recovery policy counts any prior miss for the household, and this one now does.
- The cross-product read still decides the tier whenever the household has no other homeowner-contract miss.

**O-r3-3 closed.** The outage credit now stops at the offer date: "by how long the request had stood on the date of the accepted offer, because from that date the homeowner holds the cash that ends the outage". Holding an offer open no longer accrues credit.

**Realism check on the re-seeded cross-category evidence, against the owning charters.**

- lineplan.yaml § lineplan_evt_dispatch: "a network contractor with trade utility_line … whose service ZIP codes include the property_zip, preferred before standard, never suspended … a missed window leads to re-dispatch".
- addon.yaml § addon_evt_dispatch: rider requests go to the trade matching the component (appliance for the second refrigerator).
- Results are in each task file.

### findings (r4)

| item | r4 status |
| --- | --- |
| R3-F1 (line-plan rows contradicted the line-plan charter; "plumbing network" premise) | rule text **closed**: the premise is now "Bridgewell's contractor network". World: see 1.md r4. |
| O-r3-1 | closed |
| O-r3-2 | closed |
| O-r3-3 | closed |
| O-r2-3, O3 | unchanged observations |
| O-r4-1 | new observation: stale compute_basis quotation for acceptance `outage_item` |


Post-reveal note and closing_checklist (r4), written after both comparisons (reveal at 2026-10-12 23:33:14 UTC):

- Per-task files correspond one-to-one with the tasks, and this file sits alongside them. Revisions 1 to 4 are preserved in order. Every r4 comparison section carries PASS.
- The five extended policies are fully covered by the two tasks. Task scopes, per `charter_scope`, are disjoint across each whole problem tree:
  - task 0: {stalled, customer_elected}
  - task 1: {haul_away, offer, acceptance}
  Task tools and GT are closed. Each tool's uuid8 is independently drawn (O1 closed in r2).
- Problem trees: each has 1 or 2 prerequisite problems; value_input edges meet max(n − 1, 1); each tree's root is an owner=user write; there are no cycles. The difficulty-wide prerequisite graph (two chains) is acyclic.
- Factors:
  - every computation has a self-sufficient baseline and 4 to 6 factors, with at least 2 parameter and at least 1 method
  - every ladder has three tiers, stated in its rule, distinct in outcome, and passed the realism test
  - every factor bears weight against an honest baseline, and every all-baseline fall-back is definite and differs from gold
  - task 0 has multi-source factors (carry_in, missed_contact) and a cross-difficulty factor (missed_contact, addon)
  - task 1 has multi-source factors (carry_out, code_pan, recall_fee_return, network_miss) and a cross-difficulty factor (network_miss, lineplan)
  - the cross-difficulty rows conform to their owning charters
- Gates: the coordinator's post-rework snapshot for this final form (replay with --check) is green except TRACEABILITY, whose only misses are the 5 unlock tool names pending the render. Per Step 0, I cite this rather than re-running it.
- Open observations, which are not grounds for rework: O3, O-r2-3 (rolling 12-month cap window), O-r4-1 (stale compute_basis quotation), and the minor line-plan wording note.

**This difficulty passes the source-layer audit on all four relationships, for both tasks.**


## revision_5

### charter_global_frozen (revision 5)

- Written at 2026-10-13 04:25:58 UTC (system clock), before either task's round-5 GT was revealed. Revisions 1 to 4 above are untouched.
- Report hashes at the start of round 5:
  - _difficulty.md 19b66600…
  - 0.md 512dafae…
  - 1.md 3345ba2a…
- Inputs, with hashes verified against the brief:
  - extended.yaml 59394a98…6090 (**changed**)
  - task_tools.py 7eb93e60… (unchanged)
  - 0.view c36dbc68… (unchanged)
  - 1.view ad6faba9… (unchanged)
- Additionally read, as the brief instructs: `audits/render_notes/homeplan.md`. No other audit file and no task JSON was read before the freeze.
- The charter changed, so the sections that depend on it are re-derived below. § action_binding_and_uuids is carried forward from revision 2 by reference (unchanged tool module and target tools).
- The base section is still verbatim.
- Gates: all green, including TRACEABILITY.

### Routed render-note items

**1. compute_basis mismatch (= O-r4-1): closed.** A mechanical check over all five policies found:

- every `compute_basis` quotation is a verbatim substring of its rule; acceptance `outage_item` now matches "had stood on the date of the accepted offer";
- every compute binding has a basis entry and vice versa;
- every baseline sentence, `replaced_by` sentence and prerequisite sentence is in its own rule;
- every `superseded_clause` is verbatim in its named base policy.

**2. Haul-away on zero-allowance tiers: closed.**

- The rule's opening sentence now reads "a haul-away allowance is owed on that service request as soon as the completion report is on file, provided the tier's haul_away_allowance is above 0.00 (a tier whose haul_away_allowance is 0.00 owes and books none)".
- The first supplemental-allowance replaced_by now restates the retired half: "and a tier whose haul_away_allowance is 0.00 still pays nothing for that type, so no haul-away allowance is owed or booked on it".
- So no haul-away write exists on ApplianceCare, SystemsCare or HomeCare Bronze. The positive-`amount` contract of book_supplemental_allowance_cce1a240 can no longer be asked to record 0.00.
- The offer gate was adjusted to match: "… when it closes a Bridgewell replacement on a tier that pays a haul-away allowance, has that replacement's haul-away allowance on the records". Its condition adds "and the tier's haul_away_allowance is above 0.00". Sentence and condition agree, the sentence passes the four-point test, and only the allowance tool can bring the state about.
- **Residual observation O-r5-1.** The haul-away `result` binding is not guarded for a zero tier. Evaluated there it would return the late-booking credit. The rule removes the write on such a tier, so that number is never written or scored. No consequence, and not reached on either world.

**3. Retired more than replaced: closed, together with the reworker's class sweep.**

- Each policy's benefit-caps overwrite is now split per base sentence, and every replaced_by restates the still-in-force part of its retired clause:
  - the item cap "is still shared by every repair, replacement, cash-in-lieu settlement and out-of-network reimbursement for that item";
  - "every payment on the contract, supplemental allowances included, still counts toward aggregate_term_limit";
  - "the remaining item benefit is still the item cap less the payments counted toward that item and the remaining aggregate benefit is still … each floored at zero". Haul-away adds "which no allowance enters".
  Only the counting window changes, to twelve months.
- The other overwrites restate their retained parts:
  - fees: "while fees are still not refunded because a failure is determined not covered or because the customer declines a covered repair or replacement"
  - customer-elected offer amount: "still limited to the remaining item benefit and the remaining aggregate benefit … and still rounded to the cent"
  - company offer amount: "still limited … still rounded … the additions this rule names take the place of supplemental allowances and no service call fee is added"
  - payment-equals-offer: "carries the offer's settlement_basis company_elected" / "carries settlement_basis customer_elected"
  - haul_away scope: "it still pays toward removing and disposing of the equipment Bridgewell replaced and only on a replacement authorization … so that credit may carry the payment above haul_away_allowance"
- I swept all 31 overwrite pairs. None retires a part it does not restate or replace.
- The customer-elected replaced_by lists "the stall fee credit and the disposal addition" as additions, but not the food spoilage allowance. This is not a gap: the retired clause bars only "supplemental allowances and service call fees", and spoilage is neither.

**4. Sentences that list all of a policy's factors (no source change): agree.** This is a rendering matter. The structured policy is unaffected, and the renderer split those sentences without changing their meaning. It falls to the KB-document audit, not to this one.

### Re-check of the rest of the charter

- Policies, tools, edges and owners are unchanged; the trees are the same two disjoint ones.
- Factor lists, ladders, params, labels and cross-category reads are unchanged from revision 4. The tier text, compute and baselines are unchanged except for the haul-away zero-tier wording above.
- Revision 4's factor_ladders and realism conclusions therefore stand on the unchanged parts.
- The new and changed text introduces no further factor tier, no cross-problem order, and no tool name or id in a rule.

### findings (r5)

- No RED.
- Render items 1 to 3 are closed; item 4 is a render matter.
- O-r4-1 is closed.
- New observation O-r5-1 (unguarded zero-tier `result`; no consequence).
- Carried observations: O3 and O-r2-3.


Post-reveal note and closing_checklist (r5), written after both comparisons (reveal at 2026-10-13 04:26:04 UTC):

- Per-task files correspond one-to-one with the tasks, and this file sits alongside them. Revisions 1 to 5 are preserved in order. Every r5 comparison section carries PASS.
- Coverage and scope are as in revision 4: five extended policies; disjoint task scopes, confirmed by `charter_scope`; task tools and GT closed; independently drawn uuid8s.
- Problem trees are as in revision 4. The adjusted offer gate is still a real, unmet-at-opening state gate in task 1. The difficulty-wide graph is acyclic.
- Factors are as in revision 4: counts, labels, ladders, realism, cross-difficulty and multi-source factors, and weight against honest baselines. Every figure was re-verified on the r5 charter.
- Gates: the coordinator's snapshot for this final form (replay with --check) is fully green, including TRACEABILITY. Cited per Step 0.
- Open observations, which are not grounds for rework: O3, O-r2-3, O-r5-1, and the line-plan wording note from r4.

**This difficulty passes the source-layer audit on all four relationships, for both tasks.**
