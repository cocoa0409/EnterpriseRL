# Policy-task audit — good_faith_estimates_and_disputes / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-20T14:18Z (before any task GT was revealed). Auditor: erl-task-policy-audit subagent, independent of the instantiator.
- Inputs and hashes, checked against the brief: `tasks/good_faith_estimates_and_disputes/estimate.extended.yaml` sha256 cbde888f3f92…, `task_tools.py` sha256 05518c79d89c…; views `r1/0.view.json` af7d606cb90f1cf8, `r1/1.view.json` 964eb11fc70fa95f.
- Read: blueprint.yaml, db_schema.json, products/{estimate,encounter,assist,visit}.yaml, the extended charter, task_tools.py, `audits/render_source/XF_recipe.md`, the DSL evaluator semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (RND, MONTHS, _within, CFIELD, CPARAM, XLATEST).
- Masked and not read before the freeze: tasks/*.json, worklog.md, /tmp/*_0073/, and in the views every key except frozen_time, user_scenario and initial_state (charter_scope, computations, db_closure, db_closure_matches_initial_state, design_rationale, evaluation_criteria, prerequisite_closure, required_documents, solvability_contract).
- Entry conditions: the gate snapshot (7 commands, all OK) and the view hashes came with the brief. Gates were not re-run here.
- Base copy: `diff <(head -812 estimate.extended.yaml) blueprint/products/estimate.yaml` gives no output, so the base section is a verbatim copy.

### policy_conflict_scan
Extended policies (P1–P5):

| id | target_tool (owner) | prerequisite |
|---|---|---|
| P1 estimate_ext_surgical_deposit | pay_surgery_package_deposit_c16ec91c (user) | [] |
| P2 estimate_ext_late_change_fee | retain_late_change_fee_0cd5c1f6 (agent) | P1 (value_input, state) |
| P3 estimate_ext_surgical_balance | pay_surgery_package_balance_24461a4e (user) | P1, P2 (value_input, state) |
| P4 estimate_ext_maternity_deposit | pay_maternity_enrollment_deposit_610ee08c (user) | [] |
| P5 estimate_ext_maternity_balance | pay_maternity_delivery_balance_fb9f749b (user) | P4 (value_input, state) |

- P1 and P4 retire the same base clause ("At scheduling the patient pays a deposit of deposit_pct…"). Each `replaced_by` excludes its own case and names the sibling's case, so the two do not overlap. P3 and P5 do the same for the BALANCE_BEFORE_SERVICE clause, also without overlap.
- P2 and the base `estimate_cancellation_and_deposit_refund` conflict on in-force base text: see finding CG-1.
- P2 and the visit charter's `visit_missed_fees`: a procedure slot cancelled by the patient with less than 72 hours' notice also carries the visit-side $50 late-cancellation fee. Both fees then fall on the same act. Recorded as an observation (the visit fee is a separate holding's fee, and no seeded world triggers it).
- P2 and the visit charter's `visit_reschedule_and_cancellation`: the visit charter moves an appointment through visit_rescheduled (same row, reschedule_count+1, within reschedule_limit=2). P2 recognises a move only as a cancelled-by-patient slot plus a later estimate version. A late move made by reschedule therefore never meets P2's scope. Observation (scope gap; neither seeded world shows a reschedule).
- P4 and P5 handle the same approved assistance case differently. P4 has a hardship-cap tier and P5 does not. See CG-10.
- Cross-category reads stay inside each policy's `cross_category` declarations (encounter, visit, assist). No extended policy writes another category's events: estimate_deposit_collected and estimate_cancellation_fee_retained both have `triggers: []`.
- Scopes. The surgery chain {P1, P2, P3} and the maternity chain {P4, P5} are disjoint by variant. Expected claims are task 0 = surgery chain and task 1 = maternity chain; this is checked against charter_scope after the reveal. Together the two claims cover all five extended policies.

### rule_compute_equivalence
- Mechanical sweep (scratch script; whitespace-normalised substring test): every `compute_basis` value of P1–P5 is a verbatim substring of its rule, every compute binding has a `compute_basis`, every `baseline.rule` is in its rule, every `superseded_clause` is in the named base rule, every `replaced_by` is in the extended rule, and every edge `policy_source` is in the blocked rule.
- Sentence-by-sentence sweep back: windows, filters, caps and floors have their rule sentences. P1 MN(package_price,…), pct cap 100, MX(0,…) on implant_total. P3 and P5 MX(0,…) "never below zero". P2 MN(deposits_held,…). XCOUNT filters carry exactly the stated exclusions: FINAL_NOTICE only; statements "of every kind"; fees "later waived still counting". The month windows match `_within` (0 ≤ MONTHS < n; a date exactly n months back is outside), and P1, P3, P4-agency and P5 each state "a month counts once its day of the month is reached". First-listed tie rules are stated for CFIELD reads of agency accounts and the cancelled slot.
- Defects: CG-2 (P2 scope gate weaker than the rule), CG-4 (rounding mode), CG-5 (P4 missed-visit month convention not stated), CG-6 (P1 framing clause).

### action_binding_and_uuids
- Each `(target_tool, computes=amount)` pair is claimed by exactly one policy.
- uuid8 tails c16ec91c, 0cd5c1f6, 24461a4e, 610ee08c, fb9f749b. They share no prefix and no sequence, are not reused, and are not adjacent values.
- Tool bodies: every write tool calls ctx.create and ctx.update itself. No body validates any prerequisite, deposit, notice or status. There are no datetime/time/random/uuid/secrets imports, no module-level helper and no example values (formats only). No factor id is a substring of any tool name (checked mechanically).
- Docstrings and ordering words: CG-9.

### prerequisite_graph
- `prerequisite` is filled on all five policies (P1 [], P4 []). Every `problem` points at an extended policy in this file. The graph P1→P2→P3, P1→P3, P4→P5 is acyclic.
- Every edge is `form: state` with no `fallback_reason`. Every `resolved_by` equals the depended-on policy's target_tool. Every `gate` (deposits_held) is a real binding in the blocked compute, and `kind: value_input` holds: deposits_held feeds the result of P2 (cap), P3 (rest_of_package) and P5.
- Each `condition` matches its sentence, with one exception: the P3←P2 condition and sentence ("for every late patient move") cannot be satisfied when the fee figures to 0.00. See CG-3.

### prerequisite_sentences
- E1 (P2←P1) "The late-change fee is retained only once an initial deposit collection stands on the surgery booking."
  - Connective: "only once".
  - State: an estimate_deposit_collected row with deposit_stage INITIAL_DEPOSIT on the surgery estimate.
  - Only one write brings it about: pay_surgery_package_deposit. The maternity enrollment-deposit tool also writes INITIAL_DEPOSIT, but "on the surgery booking" excludes it.
  - No tool name or id; P1's rule does not restate the sentence. Derivation: sentence + records (no collection) + P1's rule (the initial deposit on a surgery package) → the patient pays the P1 amount. One reading.
- E2 (P3←P1) "The pre-service balance is fixed only after the booking carries its initial deposit collection." Same analysis as E1; one reading.
- E3 (P3←P2) "The pre-service balance is not fixed until the booking shows a retained late-change fee entry for every late patient move of its procedure slot."
  - Connective: "not until". State: estimate_cancellation_fee_retained. Only one write brings it about: retain_late_change_fee.
  - "Late patient move" has the meaning P2's own rule gives it. One reading, except for the zero-fee case (CG-3).
- E4 (P5←P4) "The pre-delivery balance is not fixed until an enrollment deposit collection stands on the maternity booking." One reading; only pay_maternity_enrollment_deposit brings it about.
- No rule states a cross-problem order that grounds no declared edge.
- The base `estimate_package_pricing` order (deposit at scheduling, then balance) grounds no edge. The extended rules carry their own sentences, so this is an observation only.

### override_declarations
Sentence by sentence, against each `base_policy_refs` entry:
- P1/P4 vs estimate_package_pricing:
  - The deposit clause is declared.
  - "package price" changes from the schedule price to the sum of the facility and professional lines carrying the principal code. This is inside the declared clause. On both seeded worlds the line sums equal the schedule (5290 for 49505; 9850 for 59400).
  - The all-inclusive sentence, exclusions, PACKAGE_PRICE_ADJUSTMENT and deposit_methods are followed.
- P3/P5 vs estimate_package_pricing:
  - The balance clause is declared.
  - The all-inclusive sentence ("the patient is billed the package price and nothing else for the package, except the package_exclusions") is not retired. P3 and P5 collect amounts above the package price that no rule can ever bill (CG-8). Because they are deposits, not bills, this is recorded as a realism defect, not an undeclared override.
- P2 vs estimate_cancellation_and_deposit_refund:
  - The later-cancellation clause is declared; the medical-reason waiver is dropped for moves by declaration.
  - "Refunded at most once / original method", "Only the patient can cancel" and "Riverbend-initiated never incurs the fee" are followed.
  - The full-refund sentence ("A cancellation made at least full_refund_cancel_days calendar days before the scheduled service date (counting back from the service date, the cancellation date being on or before that day) refunds every deposit in full") is not retired. P2 replaces its calendar-day test with an hours test: CG-1.
- P2 vs estimate_revision: followed. A date change produces a new version, and P2 reads the current version.
- None of the three disguised forms (anonymous intermediate, 0/1 multiplier, dropped branch) was found beyond CG-1 and CG-10.

### factor_ladders
| policy | factor | label | tiers | cross_difficulty | multi-source |
|---|---|---|---|---|---|
| P1 | collections_security | method | 3: whole price / MAX(250, 5%·price) / 0 | encounter | yes (agency balance AND final notice) |
| P1 | moved_booking_points | parameter | 3: 10/5/0 pts | – | no |
| P1 | days_left_points | parameter | 3: 25/10/0 | – | no |
| P1 | missed_visit_points | parameter | 3: 10/5/0 (visit, not a difficulty) | – | no |
| P1 | implant_points | parameter | 3: 10/5/0 | – | no |
| P2 | fee_basis | method | 3: 3%·price / MAX(fee, 4%·price) / fee | – | no |
| P2 | notice_share | parameter | 3: .5/.75/1 | – | no |
| P2 | acute_care_share | parameter | 3: 0/.5/1 | encounter | yes (room OR obs; no stay AND ER) |
| P2 | postponement_share | parameter | 3: .5/.75/1 | – | no |
| P2 | booking_lead_share | parameter | 3: .5/.8/1 | – | no |
| P3 | prepay_credit | method | 3: 2%·rest / $40 / 0 | – | no |
| P3 | implant_share | parameter | 3: 1/.5/0 | – | no |
| P3 | statement_reserve | parameter | 3: 10%/5%/0 | encounter | no |
| P3 | rebooking_reserve | parameter | 3: $200/$100/0 | – | no |
| P4 | aid_basis | method | 4: 0 / price·(100−d)% / MIN(price, cap) / price | assist | yes (assist case × estimate date) |
| P4 | enrollment_points | parameter | 3: 15/5/0 | – | no |
| P4 | agency_points | parameter | 3: 15/10/0 | encounter | conjunction on one account row |
| P4 | missed_appointment_points | parameter | 3: 10/5/0 | – | no |
| P4 | late_payment_points | parameter | 3: 10/5/0 | – | no |
| P5 | aid_share | parameter | 3: 0 / (100−d)% / 1 | assist | yes |
| P5 | early_payment_credit | method | 3: 2%·price / $75 / 0 | – | no |
| P5 | cesarean_reserve | parameter | 3: $2,850 / $1,425 / 0 | encounter | no |
| P5 | agency_reserve | parameter | 3: 10%/5%/0 | encounter | no |

- Counts. P1: 5 factors (1 method, 4 parameter). P2: 5 (1, 4). P3: 4 (1, 3). P4: 5 (1, 4). P5: 4 (1, 3). All within 4–6, with at least 2 parameter and 1 method.
- Per chain: the surgery chain has multi-source factors (collections_security, acute_care_share) and cross-difficulty factors reading encounter. The maternity chain has multi-source factors (aid_basis, aid_share) and cross-difficulty factors reading assist and encounter.
- Every ladder is stated in full in its rule and implemented in its `decides` binding. Every fall-through equals its baseline. Every `decides` is an input, not `result`.
- No factor reads another factor's binding (XF A1). The shares in P2 multiply fee_basis only in `result` (A2/A3). Assembly sentences are generic and fix the order.
- Method structure (XF C14), all pairs:
  - collections_security: tier 2 adds MAX/floor; tier 1 reads price, tier 3 is constant 0.
  - fee_basis: tier 2 adds MAX; tier 1 reads price, tier 3 does not.
  - prepay_credit and early_payment_credit: the rate tier reads an input, the flat tier is constant, the "nothing" tier is not shadowed.
  - aid_basis: 0 / discount-scaled / MIN with cap / identity.
  - All pass structurally. fee_basis fails in-scope: CG-7.
- Realism defects: CG-8 (reserve class), CG-10 (P5 hardship fall-through).
- Observations:
  - collections_security (P1), agency_points (P4) and agency_reserve (P5) require a larger payment before medically necessary care because of unpaid prior bills. Under 26 CFR 1.501(r)-6(b)(1)(iii) that is an extraordinary collection action. The charters never tie these factors to the 501(r) reasonable-efforts conditions. For P1 and P4 this stays an observation, because the amount stays within the package price.
  - The moved_booking_points count agrees with the `estimate_version` field by construction, so reading the field gives the same tier.
  - booking_lead_share charges a smaller share for short-lead bookings. The direction is arguable but not unreal.

### findings
Each charter-global RED below names the tasks it bears on. The per-task demonstration lives in 0.md / 1.md.

**CG-1 SOURCE-POLICY RED: undeclared departure from an in-force base sentence (XF D17)**
- Symptom: P2 decides whether a move is "late" with an hours test. The base full-refund sentence, which is not retired, decides it with a calendar-day test.
- Evidence:
  - Base estimate_cancellation_and_deposit_refund: "A cancellation made at least full_refund_cancel_days calendar days before the scheduled service date (counting back from the service date, the cancellation date being on or before that day) refunds every deposit in full."
  - P2 rule: "…and the slot's notice is fewer whole hours than twenty-four times the tier's full-refund days"; compute `cancel_notice_hours < P('full_refund_cancel_days') * 24`.
  - P2's overwrite retires only the "A later cancellation retains…" sentence.
- Consequence: take a 07:30 slot on day D, moved by the patient at 10:30 on D−7. The base gives 7 calendar days, "on or before that day", so a full refund and no fee. P2 gives 165 h < 168, a late move, and keeps the fee. Two answers for the same move.
- Bears on: task 0 (the policy is claimed there). Task 0's world (4 days / 93 h) is late under both readings, so it has no task-level consequence.
- Affected: estimate.extended.yaml P2 overwrite and rule.

**CG-2 SOURCE-POLICY RED: P2 scope gate in compute is weaker than the rule (XF B6)**
- Evidence:
  - Rule: "the estimate is not cancelled and continues in a later version with the new scheduled service date".
  - Compute `late_move_on_record`: `F('status') != 'cancelled' and F('estimate_version') > 1 and …`. It never tests that the later version carries a date different from the slot's appointment_date, or that the version postdates the cancellation.
- Consequence: take an estimate at v2 because of an earlier implant change, with scheduled_service_date still equal to the slot date, and a slot cancelled by the patient with 93 h notice and not yet rebooked. The rule says this is not a move, so P2's fee does not apply. The compute returns late_move_on_record = 1 and keeps the share-weighted fee.
- Bears on: task 0. On task 0's world v2 carries 2026-11-05 ≠ 2026-10-08, so the readings agree there.

**CG-3 SOURCE-POLICY RED: the P3←P2 prerequisite sentence can be unsatisfiable (XF B6 0.00 / E24)**
- Evidence:
  - P3: "The pre-service balance is not fixed until the booking shows a retained late-change fee entry for every late patient move of its procedure slot."
  - P2 acute-care tier: "when the patient's Riverbend hospital accounts carry an inpatient room charge (revenue code 0120) or an observation charge (revenue code 0762) with a service date equal to the change date, no fee is kept". The `MN(deposits_held, …)` cap also gives 0.00 when nothing is held.
  - db_schema estimate_transactions.amount is "positive magnitude", and the retain tool's `amount` is "positive magnitude".
- Consequence: in a world where the late move coincided with an inpatient room day, the fee is 0.00. No retained-fee entry can exist, so the pre-service balance is "not fixed" for ever. The task has no feasible solution.
- Bears on: task 0. Its acute share is 0.5, so no consequence there.

**CG-4 SOURCE-POLICY RED: rounding mode in the rule differs from RND in compute (XF B10)**
- Evidence:
  - P2 rule: "the product is rounded half-up to the cent once". P3 rule: "the total is rounded half-up to the cent once at the end".
  - The DSL `RND = round(float(x), n)` is Python round, which rounds an exact binary half to even.
- Consequence:
  - In P2's own domain (the five surgery schedule prices × all share tiers), 31 combinations land on an exact half cent and round down. Example: package 47562 at $7,450, fee_basis 223.50, notice share 0.75, other shares 1 gives 167.625. The compute returns 167.62; the rule gives 167.63. Another: 5875 × 3% × .5 × .5 × .5 × .8 = 17.625, compute 17.62.
  - P3 is reachable too: a rest of the package ending in .25 makes the 2% credit end in .125, so the total ends in .125 and RND rounds down.
- Bears on: task 0 (P2 and P3). On task 0's world the half case 35.7075 rounds to 35.71 under both, so there is no task-level consequence.

**CG-5 SOURCE-POLICY RED: P4 missed-visit factor has no month convention of its own (XF A4/B8)**
- Evidence:
  - P4 missed-visit sentence: "…with an assessment date fewer than twelve whole months before today's date are counted, … the date exactly twelve months back being outside". It does not state the "a month counts once its day of the month is reached" convention.
  - P4 states that convention only inside the agency-points sentence ("A month counts once its day of the month is reached, so a placement exactly twenty-four months back is outside").
  - P1's missed-visit sentence does state its own.
- Consequence: a fee dated 2024-02-29 with today 2025-02-28. Compute: MONTHS = 11, so it is counted. A month-end-fallback reader treats 2025-02-28 as exactly twelve months back, so it is outside. The tier differs.
- Bears on: task 1. Its fee is 6 months back, so no consequence there.

**CG-6 SOURCE-POLICY RED: P1 framing clause asserts a fact no record holds (XF B12)**
- Evidence: P1 "the implant total is the sum of the Riverbend facility lines of the current version less the facility line for the principal service code, that is the above-standard implants the package excludes".
- Root cause: no estimate_transactions field marks a line as an implant, let alone an above-standard one. The clause turns every non-principal facility line into an "above-standard implant" by assertion. P3 reads the same residual as its "implant total".
- Consequence: on task 0 the residual is HCPCS C1781 (implantable mesh) on a 49505 open inguinal repair. Mesh is the standard of care for that repair, not an above-standard implant. The clause's assertion is false there (see 0.md).
- Bears on: task 0.

**CG-7 SOURCE-FACTOR RED: two tiers of fee_basis select the same value across the policy's scope (XF B13)**
- Evidence: the outpatient-surgery package_price_schedule {47562: 7450, 29881: 5875, 49505: 5290, 45378: 1640, 66984: 3380}. The mid tier ($2,000–$4,999.99: "the larger of the tier's late-cancellation fee and four percent") holds only 3380, which gives MAX(150, 135.20) = 150.00. The fall-through (<$2,000) holds only 1640, which gives 150.00.
- Consequence: in every in-scope world the mid tier and the fall-through select $150.00. The ladder is effectively two tiers (plus a non-monotone jump at $5,000, where 4% of $4,999 is $199.96 but 3% of $5,000 is $150.00).
- Bears on: task 0, where fee_basis is a claimed factor. Task 0 sits on the top tier.

**CG-8 SOURCE-FACTOR RED: pre-service reserves above the all-inclusive package price, a ladder no real hospital publishes (XF F27; unreal ladder)**
Members (every one):
- P3 statement_reserve: "three or more such statements add ten percent of the surgical package price, one or two add five percent".
- P3 rebooking_reserve: "two or more late-change fee entries retained on the estimate add $200.00, exactly one adds $100.00".
- P5 agency_reserve: "when an account of the patient is with the collection agency carrying a balance of $1,000.00 or more, ten percent of the delivery package price is added; … above zero and below $1,000.00, five percent".

Root cause:
- The pre-service balance already brings the deposits up to 100% of the package price. These tiers add more on top.
- estimate_package_pricing (in force) says "the patient is billed the package price and nothing else for the package, except the package_exclusions". estimate_agg_deposit_application says "whatever remains of the deposits after that is refunded". So no rule can ever apply these sums to a charge. They are pure holds of the patient's money until after the final bill.
- The conditions are unrelated to the service:
  - Statement reserve: any statement of any kind on any account in the last two months. A first routine statement qualifies, so the tier fires on ordinary patients with a current bill.
  - Agency reserve: a prior bill with the agency, figured on the undiscounted price even for an FAP-approved patient.
  - Rebooking reserve: re-penalises a move the late-change fee has already charged.
- Federal rule: requiring payment before medically necessary care because of bills for prior care is an extraordinary collection action under 26 CFR 1.501(r)-6(b)(1)(iii). The statement reserve can fire inside the 120-day notification period that Riverbend's own encounter charter imposes before any ECA.
- Contrast: cesarean_reserve and implant_share stand behind billable items (the package upgrade differential and the package exclusions), so they are not members of this class.

Bears on: task 0 (statement_reserve, rebooking_reserve) and task 1 (agency_reserve). Demonstrated in each task file.

**CG-9 SOURCE-POLICY RED: a docstring conveys a prerequisite (check 3)**
- Evidence: the retain_late_change_fee_0cd5c1f6 `source_estimate_txn_id` arg says "as shown by the booking's deposit activity or by the receipt of the deposit payment before the call".
- Root cause: it points at the output of another write tool (the deposit-payment receipt) with an ordering word. It tells the agent that a deposit payment precedes the fee in the same conversation. That is the content of edge E1, which only P2's prerequisite sentence may carry.
- Related observation: all five docstrings say the estimate_id is "as shown by the estimate lookup for this patient before the call". That is an ordering word attached to a read and conveys no edge.
- Bears on: task 0.

**CG-10 SOURCE-FACTOR RED: P5's aid_share fall-through gives a hardship-cap award holder a treatment no hospital publishes, and contradicts P4**
- Evidence:
  - P4 has a tier "when such a case carries no tier discount but a hardship liability cap above zero, the deposit base is the smaller of the delivery package price and that cap".
  - P5's ladder has no such tier: "in every other case the whole delivery package price is owed before delivery".
  - assist_agg_award_coverage: "Under a medical hardship award the patient's liabilities across all covered encounters together never exceed hardship_liability_cap_usd".
- Consequence: take a Medical Hardship award with cap $2,000 covering the delivery date. P4 gives a deposit base of 2,000 and a deposit of 25% = 500. P5 then requires 9,850 − 500 = 9,350 before delivery, against a liability the assist charter caps at 2,000.
- Bears on: task 1. Its case is a 40% discount, so no consequence there.

Observations (not grounds for rework):
- Both seeded estimates have no deposit weeks after scheduling, although base says "At scheduling the patient pays a deposit". On task 0 the base balance due date (7 days before the original 2026-10-08 slot) had also passed.
- The P2 "or no recorded notice" tier is unreachable: the schema gives every cancellation a notice, and the gate excludes None.
- Deposit and balance are paid in the same call, so the deposit factors only move money between the two scored payments. Each payment is scored separately, so they still bear weight.
- The DSL RND behaviour is engine-wide. CG-4 records only where it contradicts this charter's stated rounding.

## closing_checklist
Written after both reveals.
- One audit file per task (0.md, 1.md) sits next to this file. This is revision_1; there are no older revisions.
- Scopes: task 0 = {surgical_deposit, late_change_fee, surgical_balance}; task 1 = {maternity_deposit, maternity_balance}. They are disjoint and together cover all five extended policies. Tool closure and uuid8s pass (§action_binding_and_uuids).
- Trees: task 0 has n=2 prerequisites and 3 value_input edges; task 1 has n=1 and 1. Each has user-owned writes, and the graph over the whole difficulty is acyclic.
- Factors: counts and weight pass on both worlds (GT factor_sensitivity equals the audit's figures). Realism and structure REDs remain open: CG-7, CG-8, CG-10, T1-F1.
- Blind derivation and GT agree on every scored value of both tasks.
- The difficulty does NOT pass the source-layer audit. Open charter REDs: CG-1, CG-2, CG-3, CG-4, CG-5, CG-6, CG-7, CG-8, CG-9, CG-10. Open per-task REDs: T0-F1..F3, T1-F1..F2.
- Gates were not re-run by this audit (the brief's snapshot is the entry evidence). Re-running them on the final form belongs after rework.

VERDICT revision_1: task0=RED task1=RED charter=CG-1,CG-2,CG-3,CG-4,CG-5,CG-6,CG-7,CG-8,CG-9,CG-10

## revision_2

## charter_global_frozen (revision_2)
- Re-derived 2026-10-20 by the erl-task-policy-audit subagent. Both shared inputs changed, so this section is re-derived in full rather than carried forward:
  - estimate.extended.yaml: cbde888f3f92 → d8bdfe7ce535
  - task_tools.py: 05518c79d89c → 86c266c1a342
- Views: r2/0.view.json 0876dc5cf7efc1f1, r2/1.view.json a321b984585189ea. Gate snapshot 2026-10-20T19:00:35 is 7/7 OK (cited, not re-run).
- Not blind. Per the coordinator, the round-1 GT was already seen and the reworker's worklog was read (lines 113–188, the item-by-item response).
- contamination_disclosure: the worklog grep output showed probe figures [2028.0, 0, 1321.11] and [1825.2, 0, 1287.31] for task 0 before this round's derivation. The changed policies and worlds were still derived from the charter and the seeds; the figures were not taken from the worklog.
- The base section is still verbatim (`diff` against products/estimate.yaml gives no output).

### policy_conflict_scan (revision_2)
- Same five policies, same target tools and owners, same prerequisite graph (P2←P1, P3←P1, P3←P2, P5←P4). Acyclic.
- Sibling overwrites (P1/P4 and P3/P5) still exclude each other by name.
- P2 vs base estimate_cancellation_and_deposit_refund: lateness now uses the base's calendar-day test. The rule says "the change date falls fewer calendar days before the slot date than the tier's full-refund days, counting back from the slot date"; the compute is `0 <= DAYS(change_date, slot) < P('full_refund_cancel_days')`. That is the exact complement of the base full-refund sentence. No conflict remains.
- P2 vs visit charter: the double-fee and reschedule-vs-cancel observations from revision_1 are unchanged.
- Scopes: task 0 = {P1, P2, P3}, task 1 = {P4, P5} (checked against charter_scope after the reveal).

### rule_compute_equivalence (revision_2)
- Mechanical sweep: every compute_basis value is a verbatim substring of its rule, every compute key has a basis, every baseline.rule is in its rule, every superseded_clause is in its base rule, every replaced_by is in its rule, and every policy_source is in the blocked rule.
- Rounding: every RND is now `RND(x + 0.000001, 2)` on non-negative figures. A sweep of P2's whole in-scope domain (5 schedule prices × 3×3×3 shares × 5 award shares = 675 cases) against Decimal half-up gives 0 mismatches. P1, P3, P4 and P5 figures carry at most 4 decimals, so the offset cannot carry a value across a cent. The rules say "rounded half-up to the cent (an exact half cent goes up)".
- Month windows: P1 and P4 missed-visit and P5 cesarean each state "a month counts once its day of the month is reached" in their own sentence.
- Edge inputs (XF B6):
  - Each carve-out of a 100% award or used-up hardship cap is stated in words and gives 0 = outside the rule (P1, P2, P3, P4, P5).
  - A stay on the change date is outside P2.
  - A figure of zero or less is outside P3 and P5.
  - "No initial deposit on record" is stated for the pay-in-full credits.
  - P2's gate now tests the version date, the new date and the window (CG-2).
- XSUM of `fap_liability_usd` over assist_encounter_applied matches "the liabilities already booked on encounters under that case". The field exists in db_schema. Applications later reversed (assist_adjustment_reversed) are counted the same way by rule and compute; observation only.

### action_binding_and_uuids (revision_2)
- Same tools and uuid8 tails, each claimed once.
- Docstrings: estimate_id "as listed by the estimate lookup for this patient"; source_estimate_txn_id "as listed in the booking's deposit activity". There is no "before", "after" or "first", and no other write's receipt (CG-9).
- No imports beyond erlbench. No validation of prerequisites in any body.

### prerequisite_graph / prerequisite_sentences (revision_2)
- E1, E2 and E4: unchanged sentences; the single-reading analysis from revision_1 holds.
- E3 (P3←P2): "The pre-service balance is not fixed until the booking shows a retained late-change fee entry for each move of its procedure slot, that is a slot the patient cancelled while the booking continued at a new date, made fewer calendar days before the slot date than the tier's full-refund days and outside a Riverbend inpatient or observation stay."
  - The zero-fee cases now fall outside the sentence: hospital stays are excluded by the sentence, and 100%/used-cap bookings are excluded from P3 altogether. P2's lowest share product is 0.5×0.5×0.5×0.2 = 0.025 > 0, so CG-3 is closed.
  - New: the sentence's "each move" against the edge condition's singular slot. See R2-2.

### override_declarations (revision_2)
- P1/P4: the deposit clause is declared. The all-inclusive sentence is followed: the deposit is never more than the amount it acts on.
- P3/P5: the balance clause is declared. Every amount above the package now stands behind a billable item:
  - premium or other above-standard implants (package exclusions, billed at actual charges less the uninsured discount);
  - the cesarean differential, which P5 says "is applied to it or refunded … at the final bill".
- No unbillable holds remain (CG-8 closed).
- P2: the declared clause, with the calendar test aligned to the in-force full-refund sentence (CG-1 closed).

### factor_ladders (revision_2)
| policy | factors (label, tiers) | cross_difficulty | multi-source |
|---|---|---|---|
| P1 | aid_basis (method, 3); lead_share_pct (parameter, 3: 100/75/tier 50); late_deposit_points (parameter, 3); moved_booking_points (parameter, 3); missed_visit_points (parameter, 3) | aid_basis → assist | aid_basis |
| P2 | fee_basis (method, 3: fee+1%·price / MAX(fee, 5%·price) / fee); notice_share (parameter, 3, by calendar days); acute_care_share (parameter, 3: .5/.75/1); postponement_share (parameter, 3); aid_fee_share (parameter, 3: 1−d / .5 / 1) | acute → encounter; aid_fee_share → assist | aid_fee_share; acute_care_share (see R2-3) |
| P3 | aid_price (method, 3); implant_share (parameter, 3: 1/.5/0 by listed codes); early_credit_pct (parameter, 3); full_credit_pct (parameter, 3) | aid_price → assist | aid_price |
| P4 | enrollment_aid_basis (method, 3); delivery_lead_share (parameter, 3: 100/50/tier 25); enrollment_points; missed_appointment_points; late_payment_points (parameter, 3 each) | assist | enrollment_aid_basis |
| P5 | delivery_aid_price (method, 3); early_payment_credit (parameter, 3); cesarean_amount (parameter, 3: $2,850 / $1,425 / 0); pay_in_full_credit (parameter, 3) | aid → assist; cesarean → encounter | delivery_aid_price |

- Counts: 5/5/4/5/4 factors, each with 1 method and the rest parameter, each with at least 2 parameter.
- fee_basis over the schedule: 7450 → 224.50, 5875 → 208.75, 5290 → 202.90, 3380 → 169.00, 1640 → 150.00. The in-scope tiers are distinct and monotone (CG-7 closed).
- Every method tier set passes XF C14: price×(100−d)%, MIN(price, cap−used) and the identity are pairwise distinct shapes. For fee_basis, the fee plus a price-scaled amount, MAX, and a constant are distinct.
- The four award ladders share one structure, and P2's aid_fee_share mirrors it (CG-10 closed).
- Removed: collections_security, agency_points, statement_reserve, rebooking_reserve, agency_reserve. This closes CG-8 and the revision_1 501(r) observations.
- Realism:
  - FAP applied to the self-pay package price and to the late-change fee is plausible as Riverbend's own schedule.
  - Premium IOL (V2787/V2788) as a patient-elected upgrade outside the package is realistic.
  - The cesarean amount for a prior C-section is backed by the billable differential.
  - The C1713/C1776 "other above-standard implants" tier is unlikely to be reached by any of the five scheduled codes. Observation.

### findings (revision_2)
Status of the revision_1 REDs:
- CG-1 closed. The calendar-day test is aligned with the base.
- CG-2 closed. The gate tests the new date ≠ slot date, version furnished on or after the change date, and change on or before the slot date.
- CG-3 closed. Zero-fee cases are carved out in record terms, and the minimum share product is above 0.
- CG-4 closed. The rounding sweep shows 0 mismatches.
- CG-5 closed.
- CG-6 closed. Implants are read only by listed codes, and the definition is stipulated by code, not asserted of records.
- CG-7 closed.
- CG-8 closed. Every reserve is removed; what remains above the price is backed by billable items.
- CG-9 closed.
- CG-10 closed.

New in revision_2:

**R2-1 SOURCE-POLICY RED: shared record selections are declared inside factors and read from outside them (XF A2/A4)**
- Symptom: the scope carve-out binding `no_payment_owed` in every policy reads the bindings aid_discount, aid_cap, aid_cap_used and aid_covers. Those are declared in the award factor's `bindings`. P3's assembly `balance_figure` also reads premium_lens_total and other_implant_total, which are declared in implant_share's `bindings`.
- Members (every one):
  - P1 no_payment_owed ← aid_basis
  - P2 no_payment_owed ← aid_fee_share
  - P3 no_payment_owed ← aid_price
  - P3 balance_figure ← implant_share (premium_lens_total, other_implant_total)
  - P4 no_payment_owed ← enrollment_aid_basis
  - P5 no_payment_owed ← delivery_aid_price
- Evidence: the scratch sweep listing "plain binding reads factor-internal bindings" (the compute and factors blocks of each policy).
- Consequence:
  - Withdraw a factor to its baseline (its bindings belong to it): the hub's scope gate, and P3's assembly, have no definite value.
  - In the rule text, the award-period convention ("runs from its award start date through its award end date, both counted") is stated only inside each factor's sentence. The hub carve-out ("with an award period including the scheduled service date") relies on it.
  - P3's hub needs the implant amount (share × total) while the total is defined only in the factor's sentence.
  - XF A2 requires shared selections to be plain non-factor bindings stated once.
- Bears on: tasks 0 and 1.

**R2-2 SOURCE-POLICY RED: the P3←P2 prerequisite sentence is broader than its edge condition and than what P2 can produce (check 6/7; missed in revision_1)**
- Evidence:
  - Sentence: "…a retained late-change fee entry for each move of its procedure slot…".
  - Edge condition: "for the patient-cancelled procedure slot moved … estimate_transactions carries an estimate_cancellation_fee_retained row".
  - P2 rule: "where the patient has cancelled more than one such slot, the first one the appointment record lists is the one read … The fee is kept once".
- Consequence: take a patient who moved the procedure twice, both times inside the 7-day window (two patient-cancelled slots, the booking continuing).
  - The sentence requires two fee entries before the balance is fixed.
  - P2 settles a fee only for the first-listed slot, once.
  - The condition is met by one row.
  - Reading 1 (one entry): the balance is fixed after one fee. Reading 2 (each move): the balance is never fixed, because P2 gives no amount for the second entry.
- Bears on: task 0. Its world has one moved slot.

**R2-3 SOURCE-FACTOR RED: acute_care_share has a compound condition part that holds for every customer who reaches the write (unreal ladder)**
- Evidence:
  - Ladder: "no room or observation charge on the change date AND latest emergency room charge on the change date or the day before"; "no room or observation charge on the change date AND latest emergency room charge two to seven days before".
  - P2 rule: "A move made while the patient's Riverbend hospital accounts carry an inpatient room charge (revenue code 0120) or an observation charge (revenue code 0762) with a service date equal to the change date is a medically documented change, not a late patient move, and carries no fee; … both are outside this rule". The compute gate requires `stay_charges_on_change == 0`.
- Consequence: the "no room or observation charge on the change date" part is true for every booking that reaches the fee write. It restates the scope rather than dividing customers. The factor is single-source (latest ER date only), and its declared conjunction is hollow.
- Bears on: task 0. Task 0 keeps other multi-source factors, so its multi-source floor still holds.

Observations (revision_2):
- P2 "is a medically documented change" labels a stay charge as physician documentation. No record holds documentation; the label stands in for the base's medical-reason waiver.
- 501(r)(5): whether package price × (1 − discount) stays at or below AGB × (1 − discount) of the eventual gross charges cannot be checked from the charter.
- Both worlds' FPL percentages (340.0% for a household of 2, 332.6% for a household of 3) use the 2025 HHS guideline, while the assist charter specifies the guideline in effect on the 2026 application date. The tier would not change (not verified against the 2026 figures).
- Revision_1 observations on deposits unpaid at scheduling, versions vs. estimate_version, and the visit double fee still stand.

## closing_checklist (revision_2)
- All ten revision_1 charter REDs (CG-1–CG-10) and all five task REDs (T0-F1–F3, T1-F1–F2) are verified closed against the d8bdfe7ce535 / 86c266c1a342 artifacts and the r2 worlds.
- Blind derivation and GT agree on every scored value and every factor_sensitivity figure in both tasks. Scopes are disjoint and complete; the graph is acyclic.
- New open charter REDs:
  - R2-1: shared award and implant selections are declared inside factors and read by the scope gate and P3's assembly. 6 members, P1–P5.
  - R2-2: P3's "each move" sentence is broader than its edge condition and than what P2 produces (missed in revision_1).
  - R2-3: acute_care_share's "no room or observation charge" part is constant over the write's scope.
- The difficulty does not yet pass. Gates were not re-run by this audit.

VERDICT revision_2: task0=RED task1=RED charter=R2-1,R2-2,R2-3

## revision_3

## charter_global (revision_3)
- Re-audited 2026-10-20 by the erl-task-policy-audit subagent.
- Inputs:
  - estimate.extended.yaml d8bdfe7ce535 → 81a6fb58d013 (changed, so the touched parts are re-derived below);
  - task_tools.py 86c266c1a342 (unchanged, so §action_binding_and_uuids of revision_2 carries forward);
  - r3 views identical to r2 (`diff` empty), so the seeds are unchanged.
- Gate snapshot 2026-10-20T22:11:06 is 7/7 OK (cited, not re-run). Base section still verbatim.
- Not blind: earlier GT was seen. The worklog's round-3 response and probe table were read before re-deriving.

### Re-check of touched policies (all five) against XF_recipe.md
- Mechanical sweep: every compute_basis is in its rule; no compute key lacks a basis; every baseline.rule is in its rule; superseded/replaced clauses are verbatim; every policy_source is in its rule.
- R2-1 class sweep: no binding reads a factor's non-deciding binding, and no factor reads another factor's binding.
  - The award records (aid_case, aid_tier, aid_cap, aid_cap_used, aid_cap_left, aid_start, aid_end, aid_covers) are plain bindings. Each policy defines them in one sentence of its own, "For <quantity>, the patient's award is … both counted; the award's cap left is …".
  - Each award factor owns only aid_discount and its decided binding.
  - P3's implant_total is plain and defined once; implant_share owns only the line-presence counts.
- Carve-outs:
  - The 100% carve-out now tests the tier name ("Riverbend Presumptive Charity Care" or "Riverbend Full Charity Care (0-200% FPL)"). In assist.yaml these are exactly the two variants with discount_pct 100, so this is equivalent to the revision_2 discount test. The rule words match the compute.
  - Hardship: rule "carries a hardship liability cap with no cap left", compute `aid_cap > 0 and aid_cap_left <= 0`.
- Compound condition parts:
  - Every aid ladder still says "above zero and below one hundred percent". "Below one hundred percent" is not constant over the write's reachers: a 100%-tier holder whose award does not cover the date reaches the write with discount 100. Not a member of the R2-3 class.
  - The hardship tier's "has cap left" is false for every non-hardship reacher. Not constant.
- R2-3: acute_care_share is now single-source on the latest 0450 date: day-of/day-before 0.5, 2–7 days 0.75, otherwise 1. The constant part is gone. Task 0 keeps multi-source through the award factors (assist dates × estimate date, with discount or cap left).
- R2-2: P2 adds "a booking carries at most one late-change fee, so once a retained late-change fee entry stands on the booking no further fee is kept" (compute `fee_entries_before == 0`). P3's sentence and the edge condition both name "the first patient-cancelled Outpatient Procedure Appointment the appointment record lists" with "at most one such entry". Sentence and condition now have the same scope.
- Unchanged and still holding: rounding (half-up offset), month conventions, method structure (XF C14), sibling overwrites, docstrings, tools. Factor counts are unchanged at 5/5/4/5/4, each with 1 method.

### findings (revision_3)
- R2-1 closed. All six members are cleared (sweep above).
- R2-2 closed. One fee per booking; sentence and condition agree on the first-listed slot.
- R2-3 closed.

New in revision_3:

**R3-1 SOURCE-POLICY RED: P3's prerequisite sentence covers moves that P2's scope never charges, so the balance can never be fixed (CG-3 / R2-2 class, check 6)**
- Evidence:
  - P3 sentence: "The pre-service balance is not fixed until the booking shows a retained late-change fee entry whenever its procedure slot, the first patient-cancelled Outpatient Procedure Appointment the appointment record lists, was cancelled while the booking continued at a new date, fewer calendar days before the slot date than the tier's full-refund days and outside a Riverbend inpatient or observation stay; a booking carries at most one such entry."
  - P2 scope: "the estimate is not cancelled and its current version, furnished on or after the change date, carries a scheduled service date different from the slot date". Compute: `DAYS(change_date, F('issued_date')) >= 0`.
- Root cause: P3's sentence omits P2's "current version furnished on or after the change date" condition.
- Consequence: take a world where the new date was agreed and v2 (scheduled 2026-11-05) was furnished on 2026-10-03, and the old slot (2026-10-08) was cancelled by the patient on 2026-10-04.
  - P2: the version predates the change, so this is not a late move; no fee and no entry can be written.
  - P3's sentence: the slot was cancelled while the booking continued at a new date, 4 days before the slot, outside a stay. So it requires a retained fee entry.
  - The pre-service balance is never fixed and the task has no feasible solution.
  - The reworker's own round-2 probe "T0 CG-2: v2 furnished before the change" builds exactly this world. The compute returned a balance of 1287.31 there because it does not test the entry's existence; the rule text would not allow it.
- Bears on: task 0 (P3). On task 0's world v2 was furnished 2026-10-05, on or after the 2026-10-04 change, so there is no consequence there.

Observations (revision_3):
- "or with no initial deposit on record" (P3) and "or with no enrollment deposit on record" (P5) in the pay-in-full fall-through tiers are dead disjuncts: each balance is fixed only after the deposit. They are harmless, because the fall-through value equals the baseline.
- Revision_2 observations carry forward.

## closing_checklist (revision_3)
- R2-1, R2-2 and R2-3 are verified closed. Nothing that passed in revision_2 regressed:
  - gold is unchanged and equals the audit's derivation (task 0 1825.20 / 19.01 / 1287.31; task 1 4137.00 / 2951.75);
  - every factor_sensitivity and baseline_result figure is unchanged;
  - scopes, tree shape, owners and order are unchanged.
- Open: R3-1 (bears on P3, task 0). Task 1's policies (P4, P5) carry no open RED.

VERDICT revision_3: task0=RED task1=PASS charter=R3-1

## revision_4

## charter_global (revision_4)
- Re-audited 2026-10-21 by the erl-task-policy-audit subagent. Not blind (earlier GT seen).
- Entry chain:
  - `tail -n 1 worklog.md` reads `REWORK round 4: gates 7/7 green`.
  - `/tmp/erl0073_coord/snapshot.sh good_faith_estimates_and_disputes 4` was executed (not read). It built r4/0.view.json 0876dc5cf7efc1f1 and r4/1.view.json a321b984585189ea, both identical to r2/r3, so the seeds are unchanged. Gate snapshot 2026-10-21T01:36:22: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
  - sha256: estimate.extended.yaml 1256c85c82d4 (changed from 81a6fb58d013); task_tools.py 86c266c1a342 (unchanged); tasks/0.json af4ae0b639ae; tasks/1.json c3bdb2712628.
- Base section still verbatim.

### R3-1 re-check (P2, P3)
- One record-test definition, "A late patient move of a surgery booking is a cancellation of its procedure slot, the first patient-cancelled Outpatient Procedure Appointment the appointment record lists, made on or before the slot date and fewer calendar days before it than the tier's full-refund days, while the estimate is not cancelled and its current version, a later version furnished on or after the cancellation date, carries a scheduled service date different from the slot date, with no Riverbend inpatient room charge (revenue code 0120) or observation charge (revenue code 0762) dated on the cancellation date.", is carried verbatim in the P2 and P3 rules (regex extraction, `a == b`).
- Compute parity:
  - P3 `late_patient_move` tests exactly the definition: status, version > 1, date ≠ slot, issued_date ≥ cancellation date, 0 ≤ days < full-refund days, no 0120/0762 on the cancellation date.
  - P2 `late_move_on_record` is the same test plus P2's own award carve-out and one-fee carve-out.
- P3 prerequisite sentence: "The pre-service balance is not fixed until the booking shows a retained late-change fee entry for its late patient move, where it has one; a booking carries at most one such entry." The edge condition names the same test. Compute: `fee_wait_open = late_patient_move AND no fee entry`, which gives result 0 = not fixed.
- Every case where P3 waits is a case P2 can satisfy:
  - Late move with no award carve-out and no fee: P2 writes a positive fee (minimum share product 0.025 × fee basis ≥ 3.75; deposits held > 0 after the initial deposit).
  - Late move with a fee already on the booking: the wait is closed.
  - Late move under the award carve-out: P3 is itself out of scope (same carve-out words, same scheduled date).
- The revision_3 counter-world (v2 furnished 2026-10-03, slot cancelled 2026-10-04) is not a late patient move under the shared definition. P3 does not wait there; the reworker's probe gives 1268.30 with no fee written. **R3-1 closed.**

### Class sweep (waits whose depended-on rule can legitimately write nothing)
Checked independently:
- P2←P1 and P3←P1: P1 writes nothing only under its award carve-out (100% tier or no cap left, covering the scheduled service date). P2 and P3 carry the same carve-out on the same date (P2 says "the new scheduled service date", which is the current scheduled date). Otherwise P1 is positive (aid basis > 0 × percentage ≥ 50).
- P5←P4: P4 writes nothing only under the same carve-out on the expected delivery date, and P5 carries it too. Otherwise P4 is positive.
- P3←P2: covered above.
- The sweep is complete; no other edge exists.

### XF_recipe.md on the touched policies (P2, P3)
- A1/A2/A4: no binding reads another factor's internal binding. The new P3 bindings (slot_date, slot_cancel_date, stay_on_cancel_date, late_patient_move, fee_entries_on_booking, fee_wait_open) are plain.
- A3: assembly sentences unchanged. A5: the wait is a record test, not "as policy X would compute".
- B6: the definition states every edge input: no slot, Riverbend-cancelled, 7-day notice, stale version, stay, cancelled estimate. The reworker's probes match the rule on each.
- B10: rounding unchanged. B11: the compute_basis sweep is clean for all five policies. B12: no new framing assertion.
- C14: method tiers unchanged.
- D15–D17: P2's replaced_by now points to the definition sentence; it is verbatim in the rule and its base clause is still verbatim.
- E: tools unchanged. F: seeds unchanged.
- Cross-category: P3 adds visit and encounter reads for the definition, and declares them.
- Observation: P2 keeps its earlier sentence "A move made while … 0120 … or … 0762 … is a medically documented change, not a late patient move", which is now redundant with the definition. It does not conflict.

### findings (revision_4)
- R3-1 closed. No new RED.
- Observation (task 1 file): tasks/1.json is c3bdb2712628 in this snapshot, against 2528516574a0 at revision_3 (verified then with sha256sum). The worklog claims "Task 1's files are byte-identical (cmp against the pre-edit copy)", which does not hold against the audited revision_3 file. No pre-edit copy lies inside this audit's read domain, so the changed bytes could not be located. Every field that carries a relationship was re-checked and is unchanged: view fields (hash identical), evaluation_criteria writes and amounts, computations (expected, baseline_result, every factor_sensitivity figure), prerequisite_closure edge and order, and charter_scope. design_rationale ends at section 13 (round 3); there is no round-4 section.

## closing_checklist (revision_4)
- Per-task files correspond one-to-one with the tasks; revisions 1–4 are traceable.
- Scopes are disjoint and complete. Tool contracts and uuid8s are unchanged.
- Trees: task 0 has 2 prerequisites and 3 value_input edges; task 1 has 1 and 1. Each has customer-owned writes. Acyclic.
- Factors: 5/5/4/5/4, each with 1 method and at least 2 parameter. Every factor bears weight against an honest baseline on its task's world (figures equal GT). Multi-source: the award factors. Cross-difficulty: assist (plus encounter).
- Gold: task 0 1825.20 / 19.01 / 1287.31; task 1 4137.00 / 2951.75, equal to the audit's derivation.
- Gates: the coordinator snapshot of the final form is 7/7 OK (not re-run by the auditor).

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global (revision_5)
- Re-audited 2026-10-21 by the erl-task-policy-audit subagent. Not blind.
- Entry chain:
  - The worklog tail reads `REWORK round 5: gates 7/7 green`.
  - `/tmp/erl0073_coord/snapshot.sh good_faith_estimates_and_disputes 5` was executed (not read). Views r5/0 0876dc5cf7efc1f1 and r5/1 a321b984585189ea, unchanged since r2. Gate snapshot 2026-10-21T05:28:49: EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK.
  - sha256: estimate.extended.yaml 107bdea6bd73; task_tools.py cb2ea284a3af (changed); tasks/0.json a2d97f3fc0e9; tasks/1.json c3bdb2712628 (equal to revision_4, so the worklog's byte-identical claim holds this round).
- Inputs: `audits/render_source/good_faith_estimates_and_disputes/render_r1.md`, read in full (renderer items 1–3), and the worklog round-5 section.
- A scratch copy of the tool helper was tested in /tmp/audit_r5_0073 and then deleted.

### Honesty note
All three renderer items were members I had passed:
- Item 1: P3's plain `implant_total` was created by the round-3 rework. Revision_3 and revision_4 explicitly endorsed it as "plain and defined once" and missed XF A4 (a quantity only one factor uses belongs to that factor).
- Item 2: the docstrings' "rounded half-up to the cent when recorded" against `round(float(amount), 2)` was present since revision_1. I never checked tool-body rounding against docstring claims (XF 21).
- Item 3: the unstated zero-version edge of moved_booking_points was present since revision_1.

### Renderer items re-checked
**Item 1 (A4) closed.**
- implant_total is now in implant_share's bindings. The factor decides `implant_amount = implant_share × implant_total` (baseline 0), and balance_figure adds implant_amount.
- The definition is folded into the factor's own sentence ("Implant share of the pre-service balance: the implant total is …"). The rule mentions "implant total" only inside that sentence (3 occurrences).
- Class sweep (independent): across all five policies, the plain bindings read by exactly one factor and nothing else are only package_price (P1) and delivery_price (P4). Each is the baseline quantity itself: the factor's baseline expression is that price, and baseline.rule states it. Not members.
- No plain binding reads a factor-internal binding, and no factor reads another factor's binding (R2-1 stays closed).

**Item 2 (XF 21) closed.**
- All five bodies call `_Cents.half_up(amount)`: a class static method, no imports, `int(abs(v)*100 + 0.5 + 1e-6)/100`.
- Tested against Decimal ROUND_HALF_UP: the named half cases (10.125, 0.015, 2.675, 1.005, 0.285, 167.625, 35.7075, …) all agree; 300,000 random 3-decimal values agree; every exact-cent value checked is the identity, so gold amounts are unchanged.
- deposit_held_usd stays `round(held ± amount, 2)` on cent sums. Its docstring claims only "2 decimal places", not a rounding mode.
- Other docstring claims vs bodies, re-swept: PMT- plus 7 digits, deposit_stage, receipt fields, and "an empty value is not accepted" (float('') raises) all hold.

**Item 3 (XF 6/13) closed for its member.**
- moved_booking_points now reads "exactly two add five, and one, or none recorded, adds none".
- P4's days-to-delivery share now adds "a passed expected delivery date included".

### Class sweep "ladder edge without a sentence" (independent; incomplete in the rework)
Every ladder input was checked for empty, zero, negative and before-anchor values:
- Stated or impossible:
  - P1 lead share (passed date stated), late-deposit (scheduling cannot follow today), versions (now stated), missed (none stated).
  - P2 fee basis (all prices), notice (the definition requires on or before the slot date), acute (later or no ER charge covered by "every other case"), award share.
  - P3 implant (none stated), pay-in-full credit (no deposit stated; a negative is impossible).
  - P4 enrollment, missed and late-payment (negatives impossible), lead share (now stated).
  - P5 cesarean (none / 60+ stated), pay-in-full credit.
- Not stated: see R5-1.

### findings (revision_5)
**R5-1 SOURCE-POLICY RED: date-before-anchor edges with no rule sentence (XF B6; same class as renderer item 3 and the P4 passed-date edit)**
Members (every one):
1. **P2 postponement_share.**
   - Rule: "the postponement days run from the original slot date to the new scheduled service date, the slot date not counted and the new date counted; fourteen or fewer postponement days keep half…".
   - A late move may go to an earlier date: the definition requires only "a scheduled service date different from the slot date".
   - Compute: `DAYS(slot, new) <= 14` gives 0.5 for a negative count.
   - The rule's counting sentence does not define a count running backwards. Is an earlier date a "postponement" at all? One reader takes half (−2 ≤ 14); another takes "not a postponement" and keeps all (1.00).
   - Example world: slot 2026-10-08 cancelled 2026-10-04, new date 2026-10-06.
2. **P3 early_credit_pct.**
   - Rule: "the days to surgery run from today's date to the scheduled service date, today not counted and the service date counted; … fewer than fourteen days take off nothing".
   - There is no passed-date sentence. P1's analogous sentence carries "a passed service date included", and P4 now carries "a passed expected delivery date included". The compute gives 0 for a negative count.
   - The rework added the clause to P4's "thirty or fewer" but not to this "fewer than fourteen" ladder of the same shape.
3. **P5 early_payment_credit.** Same as member 2: "fewer than thirty-five days take off nothing", with no passed expected delivery date sentence.

I had passed all three members in revisions 1–4. Bears on: task 0 (members 1 and 2) and task 1 (member 3). No consequence on either world (postponement 28 days; days to surgery 16; days to delivery 42).

Observations:
- Each of these comparatives ("or fewer", "fewer than") does cover a negative number arithmetically. Members 2 and 3 are listed because the charter now marks passed dates explicitly in its sibling ladders (P1, P4), so the omission reads as a gap rather than a choice.
- Everything else re-checked on the touched policies (P1, P3, P4, tools) is unchanged and clean:
  - compute_basis quotes, baseline-in-rule, edge sentences, overwrites;
  - rounding (compute and tools);
  - method structure;
  - factor counts 5/5/4/5/4;
  - seeds.

## closing_checklist (revision_5)
- Renderer items 1–3 are closed, and the item 1 and item 2 classes are fully swept.
- Gold is unchanged and equal to the audit's derivation: task 0 1825.20 / 19.01 / 1287.31; task 1 4137.00 / 2951.75. Every factor_sensitivity and baseline figure is unchanged, as are scopes, trees and owners.
- Open: R5-1 (3 members across P2, P3 and P5).

VERDICT revision_5: task0=RED task1=RED charter=R5-1

## revision_6

## charter_global (revision_6)
- Re-audited 2026-10-21 by the erl-task-policy-audit subagent. Not blind.
- Entry chain:
  - The worklog tail reads `REWORK round 6: gates 7/7 green`.
  - `/tmp/erl0073_coord/snapshot.sh good_faith_estimates_and_disputes 6` was executed (not read). Views r6/0 0876dc5cf7efc1f1 and r6/1 a321b984585189ea (unchanged since r2). Gate snapshot 2026-10-21T06:09:06: all 7 OK.
  - sha256: estimate.extended.yaml a0f4bc486fb4; task_tools.py cb2ea284a3af (unchanged); tasks/0.json a2d97f3fc0e9 and tasks/1.json c3bdb2712628, both equal to revision_5 (the worklog's byte-identical claim holds).

### R5-1 re-check
- Member 1 (P2 postponement) closed. The rule adds "a new date earlier than the slot date counting as zero postponement days"; the compute is `postponement_days = MX(0, DAYS(slot, new))`, giving the "fourteen or fewer" tier.
- Member 2 (P3 early credit) closed. "fewer than fourteen days, a passed service date included, take off nothing" (compute 0).
- Member 3 (P5 early credit) closed. "fewer than thirty-five days, a passed expected delivery date included, take off nothing" (compute 0).

### Reworker's six additional edge sentences: each checked against compute
| edge sentence | compute | agrees |
|---|---|---|
| P1 and P4: "a scheduling date later than today's date counting as zero days" | `DAYS(sched, NOW)` < 0 falls in the < 30 tier (0) | yes |
| P1 and P4: "a fee dated after today's date not counting" | `_within`: MONTHS(d, NOW) < 0 is excluded | yes |
| P4: "an expected delivery date on or before the scheduling date counting as zero lead days" | DAYS ≤ 0 falls in the < 112 tier (+15) | yes |
| P2: "one dated after the change date included" (acute) | er_gap < 0 falls in the else tier (1) | yes |
| P3 and P5: "or with one dated after today's date, takes off nothing" | days_since_deposit < 0 gives 0 | yes |
| P5: "a charge dated after today's date counting as zero months back" | MONTHS < 0 falls in the < 18 tier (full differential) | yes |

### Exhaustive ladder-edge pass (independent, every ladder × every edge)
Sources for the pass:
- the full rule text of P1–P5 (printed and read);
- every compute binding feeding a ladder;
- the DSL semantics (`_within`, MONTHS, DAYS, CFIELD first-listed, XLATEST);
- the record vocabularies of the source tables: encounter_transactions event_type and credit_reason_code, assistance lifecycle and events, appointment_transactions event types.

Each ladder was checked for zero/empty, missing record, negative/before-anchor/passed date, future-dated record, boundary values, ties and multiple records, and reversed/credited/waived records.

Results:
- The reworker's table is accurate row by row for zero/empty, negative/before-anchor and boundaries.
- Every boundary pair is stated in its rule and matches compute: 7/8, 20/21, 29/30, 59/60, 13/14, 14/15, 30/31, 34/35, 35/36, 60/61, 111/112, 167/168, the 17/18 and 59/60 whole months under the stated month convention, $2,500.00/$5,000.00 and $1,000.00 lines.
- Ties: CFIELD first-listed reads are stated (slot, award). XLATEST/LATEST return the date itself, so ties are immaterial.
- Award edges:
  - A revoked case leaves status approved (lifecycle state `revoked`), so assist_adjustment_reversed can never stand under an approved case. The "liabilities already booked" read has no reversal edge.
  - Expired or non-covering awards fall to "every other case".
  - A non-hardship tier's 0.00 cap field does not "carry a hardship liability cap", and the compute agrees (`aid_cap > 0`).
- Waived visit fees are stated ("a fee later waived still counting").
- Gap found in the reversed/credited-record edge: see R6-1.

### findings (revision_6)
- R5-1 closed (all three members).

**R6-1 SOURCE-POLICY RED: charge lines later credited (reversed) are read as charges with no rule sentence (XF B6/B9 "reversed rows")**
- Root cause:
  - The encounter charter lets any posted charge line be credited in whole: encounter_charge_credited, with credit_reason_code including SERVICE_NOT_RENDERED and DUPLICATE_CHARGE.
  - The credit is a separate row (`source_txn_id` → the charge). The original encounter_charge_posted row stays.
  - Every charge-reading rule below says "charge" with no sentence on credited lines. Every compute counts the posted row regardless of a credit.
- Members (every read):
  1. P2 acute_care_share: "the latest emergency room charge (revenue code 0450) … has a service date on the change date or the day before it" (`XLATEST … event_type='encounter_charge_posted', revenue_code='0450'`).
  2. P2 late-patient-move definition: "with no Riverbend inpatient room charge (revenue code 0120) or observation charge (revenue code 0762) dated on the cancellation date" (`stay_charges_on_change`). The same clause appears in P2's "medically documented change" sentence.
  3. P3, the same late-patient-move definition sentence (`stay_on_cancel_date`).
  4. P5 cesarean_amount: "the latest cesarean delivery charge (procedure code 59514) … is read by its service date" (`XLATEST … cpt_hcpcs_code='59514'`).
- Consequences, demonstrated on task-0 and task-1 worlds with one producible credit row added:
  - (a) Credit the ER line d01fdb27 (0450, 2026-10-03) in full as SERVICE_NOT_RENDERED. The compute still takes 2026-10-03 as the latest ER charge, so acute 0.5 and fee 19.01. A reader who treats a not-rendered charge as no charge has no ER charge, so acute 1.00 and fee 38.03.
  - (b) A 0120 room charge dated on the cancellation date, credited as SERVICE_NOT_RENDERED: the compute says not a late move (no fee, and the balance does not wait). The other reading says late move, a fee is due and the balance waits for it.
  - (c) The task-1 59514 line credited as SERVICE_NOT_RENDERED: the compute adds 1,425.00; the other reading adds 0.00.
- I passed every member in revisions 1–5. None is reachable on the seeded worlds (no credit rows), so there is no consequence on either task's scored solution.

Observations (revision_6):
- An "unrelated older cancellation shadows the current one" risk comes from the first-listed slot rule. Rule and compute agree, so this is a design choice.
- A package price of 0 in P1/P4 (no principal lines) would give a 0.00 deposit with no sentence. It is unreachable: estimate_content_and_lines makes every issued package version list its package-price lines.
- "The fee is kept … from the most recent deposit collection that can cover it" has no sentence for the case where no single collection covers the fee. This is inherited base text; it needs two collections each smaller than the fee and is not reachable on either world.

## closing_checklist (revision_6)
- R5-1 closed. Every boundary, zero, negative and future-dated edge is stated and agrees with compute.
- Gold is unchanged and equal to the audit's derivation: task 0 1825.20 / 19.01 / 1287.31; task 1 4137.00 / 2951.75. Task files are byte-identical to revision_5, and every factor_sensitivity figure is unchanged.
- Open: R6-1 (4 read sites in P2, P3 and P5). Reported in full this round; no further members found.

VERDICT revision_6: task0=RED task1=RED charter=R6-1

## revision_7

## charter_global (revision_7)
- Re-audited 2026-10-21 by the erl-task-policy-audit subagent. Not blind.
- Entry chain:
  - The worklog tail reads `REWORK round 7: gates 7/7 green`.
  - `/tmp/erl0073_coord/snapshot.sh good_faith_estimates_and_disputes 7` was executed (not read). Views r7/0 0876dc5cf7efc1f1 and r7/1 a321b984585189ea (unchanged since r2). Gate snapshot 2026-10-21T19:21:04: all 7 OK.
  - sha256: estimate.extended.yaml ac1055d37814; task_tools.py cb2ea284a3af, tasks/0.json a2d97f3fc0e9 and tasks/1.json c3bdb2712628, all three unchanged.
- Sweep: compute_basis verbatim, every key has a basis, baseline in rule, edge sentences in rule; no binding reads another factor's internal binding. The late-patient-move definition is identical in P2 and P3 (regex `a == b`).

### R6-1 re-check
All four sites now carry a "credited in full" test with matching compute:
- P2 ER read: er_line / er_line_credited; a credited line gives gap −1, so the full share.
- P2 and P3 room/observation reads in the shared definition: chg_/cnl_ room_line, room_open, obs_line, obs_open. P2's "medically documented change" sentence reads them "as the definition … reads it".
- P5 cesarean read: ces_line / ces_line_credited; a credited line gives 9999 months, so nothing added.
- The reworker's probes for full and partial credits behave as the rule words say for a single full-amount credit.
- The specific readings R6-1 named (a line credited in full as SERVICE_NOT_RENDERED read as a charge) are closed. Two new defects in the chosen test are below.

### Sweep of every cross-category read (independent)
- Encounter charge reads (0450, 0120, 0762, 59514) are the only cross-category charge reads. They now carry the credit test (see R7-1 and R7-2).
- Visit fees (P1, P4 missed points):
  - The visit charter has assessed, waived and paid events only; no reversal or refund event exists. The waiver is stated.
  - The appointment lifecycle has no transition out of `cancelled`, so the slot read cannot be undone.
- Award reads (all five): assist_adjustment_reversed follows only revocation, and the lifecycle state `revoked` is filtered out by `status='approved'`. Expired and withdrawn cases are filtered the same way.
- Not read anywhere: encounter payments, refunds, adjustments, statements; claims; plans.
- The reworker's sweep items 5–8 are confirmed.

### findings (revision_7)
- R6-1 closed in substance: each site now tests credits.

**R7-1 SOURCE-POLICY RED: the "credited in full" rule wording and the compute disagree when a line carries several credit entries (XF B2/B6)**
- Rule (all four sites, same words): "a line credited in full, that is one carrying a charge-credit entry for its whole amount".
- Compute (all four sites): `XSUM(credited amounts with source_txn_id = line) < XSUM(posted amount of that line)`. That sums every credit entry.
- The encounter charter's grain is "one row per credit against one charge line for one reason", so several partial credits on one line are producible.
- Consequence: task-0 world, ER line d01fdb27 (1,420.00) carrying UNITS_CORRECTION 100.00 plus SERVICE_NOT_RENDERED 1,320.00.
  - Compute: credits total 1,420, so the line is credited in full, there is no ER charge, acute share 1.00 and the fee is 38.03.
  - Rule words: no single "entry for its whole amount" exists, so the line counts, acute share 0.5 and the fee is 19.01.
- The same split decides the late-move test for 0120/0762 lines (P2, P3) and the cesarean amount (P5: 1,425.00 against 0.00).
- Members:
  1. P2 ER read
  2. P2 room
  3. P2 observation
  4. P3 room
  5. P3 observation
  6. P5 cesarean read

**R7-2 SOURCE-FACTOR / SOURCE-POLICY RED: reading a single first-listed line makes the outcome depend on which duplicate line carries the credit, not on whether the service took place (unreal treatment)**
- Rule: "the first such line the account activity lists where several share that date, a line credited in full … counting as no emergency room charge"; the same construction for 59514 and for each of 0120/0762 on the cancellation date.
- Consequence 1 (duplicate twins). Two identical 0450 lines dated 2026-10-03, i.e. one ER visit billed twice, with one line credited DUPLICATE_CHARGE.
  - If the credit sits on the first-listed line, the rule says no ER charge, acute 1.00, fee 38.03.
  - If it sits on the second line, the ER charge counts, acute 0.5, fee 19.01.
  - The business facts are identical: one ER visit on 2026-10-03, billed once net.
  - The same holds for duplicate 59514 lines (cesarean amount 1,425.00 against 0.00) and for duplicate 0120/0762 lines on the cancellation date. In the latter case the move is a late move (fee owed, balance waits) or a medically documented stay (no fee), depending on which twin was credited.
- Consequence 2 (a voided latest line hides earlier real ones). A real ER visit 5 days before the change date and a mistaken 0450 line dated the day before, credited SERVICE_NOT_RENDERED.
  - The rule reads only the latest line, finds it credited and treats the patient as having "no emergency room charge", so the fee is all kept.
  - The genuine ER visit inside the 2–7 day tier (three quarters) is ignored.
  - The cesarean read behaves the same way: a voided later 59514 line hides a genuine earlier cesarean.
- A hospital weighing recent acute care or prior cesareans would not publish a treatment that turns on which duplicate was voided.
- Members:
  1. P2 acute_care_share (factor)
  2. P2 late-move definition room/obs reads (scope)
  3. P3 late-move definition room/obs reads (scope)
  4. P5 cesarean_amount (factor)

Neither R7-1 nor R7-2 is reachable on the seeded worlds (no credit rows), so there is no consequence on either task's scored solution. Both arise from the round-7 rework. No other member was found in the full cross-category sweep.

## closing_checklist (revision_7)
- R6-1 closed in its original form. Gold is unchanged and equal to the audit's derivation: task 0 1825.20 / 19.01 / 1287.31; task 1 4137.00 / 2951.75. Task files and tools are byte-identical to revision_6. The rest of the charter has not regressed.
- Open: R7-1 (6 read sites) and R7-2 (4 read sites), both in the credit test introduced this round.

VERDICT revision_7: task0=RED task1=RED charter=R7-1,R7-2

## revision_8

## charter_global (revision_8)
- Re-audited 2026-10-21 by the erl-task-policy-audit subagent. Not blind.
- Entry chain:
  - The worklog tail reads `REWORK round 8: gates 7/7 green`.
  - `/tmp/erl0073_coord/snapshot.sh good_faith_estimates_and_disputes 8` was executed (not read). Views r8/0 0876dc5cf7efc1f1 and r8/1 a321b984585189ea (unchanged since r2). Gate snapshot 2026-10-21T19:58:01: all 7 OK.
  - sha256: estimate.extended.yaml d791707e1ecc; task_tools.py cb2ea284a3af, tasks/0.json a2d97f3fc0e9 and tasks/1.json c3bdb2712628, all three unchanged.
- Route judged as the coordinator's accepted DSL-limit route: decide each read on account-level net amounts, with any residue stated plainly. Acceptable if rule == compute and the residue is realistic.

### R7-1 / R7-2 re-check (all sites)
- No "credited in full" phrase remains anywhere in the charter.
- Every read now decides on the hospital account of the selected line: XSUM of that account's encounter_charge_posted amounts less XSUM of its encounter_charge_credited amounts, filtered exactly by encounter_id (db_schema: every encounter_transactions row carries encounter_id). The read counts only when the net is above zero.
- Rule == compute at every site:
  - **P2 acute ER read.** "the first such line the account activity lists where several share that date, and it counts only when the hospital account it is posted on carries charges net of the charge credits recorded on that account above zero, otherwise counting as no emergency room charge, an earlier emergency room charge not being looked for". Compute: er_acct = XLATEST encounter_id (ties: first listed); er_acct_net; gap −1 unless the net is above zero, which gives the "every other case" tier. The bindings belong to the factor.
  - **P2 and P3 late-move definition room/obs reads.** "such a charge counting only when the hospital account it is posted on, for each of the two codes the account of the first such line the account activity lists for that date, carries charges net of the charge credits recorded on that account above zero, so that a credited line on an account that still carries net charges still counts". Compute: chg_/cnl_ room_acct and obs_acct, with open = net > 0. The sentence is identical in P2 and P3 (regex `a == b`). P2's "medically documented change" sentence still reads them "as the definition … reads it".
  - **P5 cesarean read.** The same construction. Compute: ces_acct, ces_acct_net; months 9999 unless the net is above zero, which gives the nothing tier.
- R7-1 closed: there is no single-entry test, and partial credits in any number of entries net on the account.
- R7-2 closed: duplicate twins on one account give the same result whichever copy carries the credit, because the visit is the account.
- The reworker's probe matrix is consistent with the rule words in every row I re-derived by hand:
  - twins credited on either copy: unchanged (19.01; balance 2951.75);
  - two partial credits with the account still net above zero: unchanged;
  - a voided later ER account over the real 10-03 visit: 38.03;
  - a fully voided ER account, or no ER lines: 38.03;
  - a real room stay on the cancellation date: no fee;
  - a voided observation account: fee 19.01, and with the fee skipped the balance waits (0);
  - a voided later cesarean account, or no line: 1526.75.

### Residues (stated in the rules; judged realistic under the accepted route)
- A wholly voided later account (a registration or duplicate-account error) hides an earlier genuine ER visit or cesarean: "an earlier … not being looked for". This is rare in hospital billing, and the rule states it plainly.
- A credited room/obs line on an account that still carries net charges still counts, and so does a credited ER line on an ED account with other surviving charges. Both are stated, and the episode of care is real.
- I accept both as residues of the route, not REDs.

### Regression sweep (all five policies)
- compute_basis verbatim, every key has a basis, baseline in rule, edge sentences in rule, overwrites verbatim.
- No binding reads another factor's internal binding. The only single-factor plain reads are package_price (P1) and delivery_price (P4), which are the baseline quantities themselves (accepted in revision_5).
- Tools, task files and seeds are byte-identical.
- XF A1–A5, B6/B7/B9/B11/B12, C14, D15–D17, E and F were rechecked on P2, P3 and P5 with no member found.

### findings (revision_8)
- R7-1 closed. R7-2 closed. No new RED.

## closing_checklist (revision_8)
- Per-task files map one-to-one onto the tasks; revisions 1–8 are traceable.
- Scopes are disjoint and complete. Tool contracts and uuid8s are frozen.
- Trees: task 0 has 2 prerequisites and 3 value_input edges; task 1 has 1 and 1. Each has customer-owned writes. Acyclic.
- Factors: 5/5/4/5/4, each with 1 method. Multi-source and cross-difficulty floors are met. Every factor bears weight against an honest baseline.
- Gold (task 0 1825.20 / 19.01 / 1287.31; task 1 4137.00 / 2951.75) equals the audit's derivation and GT factor_sensitivity.
- The coordinator gate snapshot on the final form is 7/7 OK.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

## charter_global (revision_9)
- Re-audited 2026-10-21 by the erl-task-policy-audit subagent. Short round, not blind.
- Entry chain:
  - The worklog tail line reads `- REWORK round 9: gates 7/7 green`. The text matches, but it carries a leading list bullet; noted, not treated as BLOCKED.
  - `/tmp/erl0073_coord/snapshot.sh good_faith_estimates_and_disputes 9` was executed (not read). Views r9/0 0876dc5cf7efc1f1 and r9/1 a321b984585189ea (unchanged since r2). Gate snapshot 2026-10-21T22:04:15: all 7 OK.
  - sha256: estimate.extended.yaml d791707e1ecc, tasks/0.json a2d97f3fc0e9 and tasks/1.json c3bdb2712628 are unchanged since revision_8. task_tools.py changed: cb2ea284a3af → 96980f077dcc.
- Input: only the src-1 item of audits/policy_kb/good_faith_estimates_and_disputes/_difficulty.md was read. Runtime context was not read.

### src-1 re-check (task_tools.py, body-only change)
- Names, decorators (owner and rw) and signatures are unchanged for all five tools (ast).
- Docstrings: the retain tool's text equals the revision_2 reading word for word ("as listed by the estimate lookup for this patient" / "as listed in the booking's deposit activity"). None carries "before the call" or another write's receipt.
- New body checks, all format or reference checks:
  - All five tools: an empty or None amount, an unknown estimate_id, or an amount ≤ 0 after half-up rounding returns an "Error: …" string with no write.
  - Retain tool: `source_estimate_txn_id` must name an existing estimate_transactions row of the same estimate with event_type estimate_deposit_collected.
- Not checked: no body tests deposit stage, deposits held, slot status, the late-move test, award state, amount correctness, or any order between tools. There is no eligibility or prerequisite refusal.
- Every write still calls ctx.create and ctx.update in its own body. There are no imports beyond erlbench, and the _Cents class helper is unchanged.
- The probe from src-1 (source "x", amount −5) now returns an error.
- src-1 closed.

### Gold and regression
- Gold calls pass the new checks:
  - deposit 1825.20 > 0 on estimate 13e359ed;
  - fee 19.01 drawn on the step-1 deposit row of that estimate (an estimate_deposit_collected row);
  - balance 1287.31; maternity 4137.00 / 2951.75.
- The charter and task files are byte-identical, so every revision_8 conclusion carries forward unchanged.
- Observation: before any deposit exists on the booking there is no row the retain tool's source argument can name, so it errors. That follows from the argument's declared meaning (a deposit collection on that booking), which predates this round. The error text repeats only that docstring wording, with no order word, tool name or policy. I do not count it as the tool layer judging the P2←P1 edge: the edge is carried by P2's rule sentence and by deposits_held, and the tool tests only that the reference exists.

### findings (revision_9)
- src-1 closed. No new RED.

## closing_checklist (revision_9)
- The revision_8 closing checklist stands unchanged (charter and task files identical).
- Tool contracts: names, signatures and docstrings unchanged; bodies add format and reference checks only.
- Gate snapshot 7/7 OK.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN

## revision_10

## charter_global (revision_10)
- Re-audited 2026-10-22 by the erl-task-policy-audit subagent. Short, seed-only round, not blind.
- Entry chain:
  - The worklog tail reads `REWORK round 10: gates 7/7 green`.
  - `/tmp/erl0073_coord/snapshot.sh good_faith_estimates_and_disputes 10` was executed (not read). Views: r10/0 0876dc5cf7efc1f1 (unchanged) and r10/1 8c52f3f0bcf2e89e (changed, as expected for a seed edit). Gate snapshot 2026-10-22T01:03:36: all 7 OK.
  - sha256: estimate.extended.yaml d791707e1ecc, task_tools.py 96980f077dcc and tasks/0.json a2d97f3fc0e9 are unchanged, as required. tasks/1.json is now 49f17d4d4f77.
- Inputs: the src-2 item of audits/policy_kb/…/_difficulty.md; the worklog's "Rework round 10" section; the published docs under docs/encounter/ for the self-pay payoff (policy encounter_ext_selfpay_payoff, all 7 docs) and the prompt-pay terms. Runtime context was not read.

### src-2 re-check (task 1, inpatient account d9d8d4ca, 2022-04-15 payoff)
- View diff r9 → r10 (task 1): only two rows changed.
  - encounter_transactions cb9554cd: amount 6846.75 → 6470.55.
  - d03553ab: 1208.25 → 1584.45.
  - user_scenario, frozen_time and every other row are identical. db_closure equals initial_state.
- Independent re-pricing from the published docs:
  - Balance standing = 17,900.00 − 9,845.00 = 8,055.00. Prompt-pay eligibility holds: Inpatient Admission minimum 500.00; PORTAL_CARD is an eligible channel; no charity adjustment; no plan.
  - Discount percent:
    - Inpatient 15 (prompt-pay terms).
    - Gross charges standing: 17,900.00, no credits, ≥ 7,500, so +3.
    - Ledger balance: 17,900 − 9,845 = 8,055, ≥ 2,000, so +1.
    - Statement recency: latest summary statement 2022-03-28, payment 2022-04-15, 18 days, so 0.
    - E-statement: US_MAIL, so 0.
    - Registration (point-of-service) payments: none, so 0.
    - Total 19%: 19% × 8,055.00 = 1,530.45.
  - Window credit: 45-day window less 18 days counted = 27 left, which is ≥ 10, so 27 × 2.00 = 54.00.
  - Payoff amount = 8,055.00 − 1,530.45 − 54.00 = **6,470.55**. Discount posted (the whole difference) = **1,584.45**.
  - The account closes at 0.00 on 2022-04-15. Both figures match the seed.
- The "when the amount is fixed" gate (coverage-terminated liability with a service-recovery courtesy) does not apply: there are no coverage-terminated postings.
- The reworker's bounded table for the other seeded rows matches my earlier per-row checks (revision_1/revision_2 seed verifications). No further miss found.
- Honesty note: revision_1 and revision_2 checked this payoff only against the base encounter charter (15% of 8,055 = 1,208.25). The extended self-pay payoff rule lives in a sibling difficulty this audit may not read, and was only checkable once its KB was published. **src-2 closed.**

### Gold and regression
- tasks/1.json: evaluation_criteria writes 4137.00 / 2951.75; computations and every factor_sensitivity figure (6895.0/2659.5/3841.5/3841.5/3546.0; 6891.75/3050.25/1526.75/3099.5) and baselines (2462.5/5713.0) are unchanged.
- No estimate factor reads encounter payments or adjustments. cesarean_amount reads the 59514 line and its account's net charges (17,900.00 − 0 > 0), so 1,425.00 is unchanged.
- The charter, tools and task 0 are byte-identical, so every revision_9 conclusion carries forward.

### findings (revision_10)
- src-2 closed. No new RED.

## closing_checklist (revision_10)
- The revision_8/revision_9 checklists stand. Seeds re-priced per published docs; gold unchanged; gate snapshot 7/7 OK.

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN
