# Policy-task audit — claim_repair_billing_desk / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit subagent (Claude Opus 5.5), independent of the instantiating agent.
- Freeze time: 2026-10-11 01:52 UTC, before any task's GT was revealed.
- Freeze inputs (sha256, first 16 hex; re-hashed by the auditor and matching the brief):
  - `tasks/claim_repair_billing_desk/claim.extended.yaml` = `72b5bbd6efa4df1c`
  - `tasks/claim_repair_billing_desk/task_tools.py` = `1bafc3ca4248a394`
  - masked views `0.masked.json` = `4787511ca59951e0`, `1.masked.json` = `905324258da280f3`
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/{claim,estimate,adas,warranty,retail}.yaml` (variant parameters and the policies cited below), the extended charter, `task_tools.py`, and the erlbench DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`MONTHS`, `DAYS`, `CFIELD`, `CPARAM`, `LATEST`, `XSUM` definitions only).
- Masked and not read: every `tasks/claim_repair_billing_desk/tasks/*.json`, the env-level `worklog.md`, any other audit, any `.audit_views` of other difficulties. Nothing in this section derives from a revealed GT.
- Entry conditions (Step 0): the gate snapshot came with the brief (check_extended / check_task_tools / replay / solvability / compute / grounding / cross_fire all green, cache-diff info-only, traceability deferred to the KB step), and the masked views came with their hashes. Entry conditions met. check_traceability is deferred by design (KB not rendered); it is recorded, not treated as missing input.

### policy_conflict_scan

Base section: lines 1-1804 of the extended charter are byte-identical to `blueprint/products/claim.yaml` (`diff` shows only one trailing blank line). Four extended policies:

| policy | subject | target_tool | computes | trigger | prerequisite |
| --- | --- | --- | --- | --- | --- |
| claim_ext_unrelated_addition_price | claim_customer_charge | sign_unrelated_damage_addition_ef94c675 (user) | amount_usd | on_request | [] |
| claim_ext_authorization_repair_days | claim_authorize, claim_insurer_approval | record_insurer_authorization_cee3bb86 (agent) | estimated_repair_days | state_due | -> unrelated_addition_price (value_input, a_addition_hours) |
| claim_ext_denied_operation_price | claim_customer_charge | accept_denied_operations_addition_a285270b (user) | amount_usd | on_request | [] |
| claim_ext_overpayment_refund | claim_customer_refund | issue_overpayment_refund_b142d0d2 (agent) | amount_usd | state_due | -> denied_operation_price (value_input, r_committed) |

- Overlapping subjects: the two addition-price policies share `claim_customer_charge` and both supersede the same base clause of `claim_evt_customer_pay_additions`; they are separated by `addition_kind` (unrelated_damage vs denied_operation) in their compute filters and in their first rule sentences ("An unrelated-damage addition is priced ..." / "A denied-operation addition is priced ..."). No overlap in conclusion on any consent.
- Triggers / eligibility / time anchors: all four price or record at "today" (`frozen_time`); no conflicting anchor. Base eligibilities inherited (`consents_signed` for claim_authorize, `refund_names_payment` for claim_customer_refund, `addition_consent_signed` for the charge) are compatible with the extended rules.
- Terminal states: authorization moves `assigned -> authorized` (base lifecycle); additions move a consent `pending_customer -> signed`; refund books a `claim_customer_refund`. No two policies write the same field to different values.
- Cross-category read boundaries: declared `cross_category` blocks match the compute reads (warranty/estimate for unrelated price; estimate/adas for authorization; adas/warranty for denied price; estimate/warranty for refund). The gate snapshot's check_extended confirms "cross-category reads declared exactly".
- Scope: the prerequisite graph splits the four policies into two disjoint trees, {authorization_repair_days -> unrelated_addition_price} and {overpayment_refund -> denied_operation_price}. With M = 2, the only partition that keeps each tree inside one task's scope is one tree per task; that partition is mutually exclusive and jointly complete. (Pre-reveal inference; confirmed or refuted against `charter_scope` only in the task files' comparison sections.)
- Blueprint event types for this difficulty include claim_authorize, claim_insurer_approval, claim_customer_charge and claim_customer_refund; every extended subject is inside the claimed list.

### rule_compute_equivalence

Mechanical sweep: every `compute_basis` quotation of all four policies is a verbatim substring of its own `rule` (0 misses), every `baseline.rule` sentence is verbatim in its `rule`, and every `overwrite.replaced_by` is verbatim in its `rule`. Binding-by-binding read-back:

- claim_ext_unrelated_addition_price: hourly ladder (<= 4.0 touch-up 96, > 24.0 collision 108, else panel 104), work amount rounded to the cent, returning-customer ladder (5 / 2 / 0 %, whole calendar months), supplies (0 if another addition consent signed; cap 45 when 6 % exceeds it; else 6 % rounded), waste fee (0 if an unrelated/upgrade charge is posted; 4.95 within touch-up hours; else 6.95), scan credit (full within the estimate tier's conversion credit window, 50 % up to its validity days, else 0), single final rounding - all implemented as stated. **One filter has no basis in the rule**: `u_quote_booking` selects `status='estimate_written'`, while the rule says "a written customer-pay estimate of the same vehicle that was never converted" (finding F-1).
- claim_ext_authorization_repair_days: allowance by source estimate type (Photo +20 %, Drive-In/Scheduled/Mobile +10 %, else as written, rounded to 1 decimal), signed customer-pay hours added, daily-hours ladder (6.5 / 4.0 / class), ceiling division, calibration days 2/1/0 by tier, revision days 2/1/0, parts days 2/1/0, stage days 2/1/0, sum with intake days - all implemented as stated; no invented basis.
- claim_ext_denied_operation_price: most recently decided supplement, written hourly value, calibration line by decision (partial: price - allowance floored at 0; approved: 0; else full), hourly rate 118/115/104, billed hours (min 1.0 / cap at supplement hours / as written), alignment ladder, warranty discount (10/5/0 %), scan charge (full > 14 days, 50 % > 7 days), single final rounding - implemented as stated.
- claim_ext_overpayment_refund: excess (payments + credits - charges - refunds), committed (signed addition consents not yet charged), payment choice (card within 120 days / ACH at least 5 days old / most recent payment), reinspection reserve, deductible exposure, betterment exposure, clearing hold, other-desk hold, floor 0 and cap at the payment - implemented as stated. Rule wording "otherwise the most recent ACH payment, when one was made at least the ACH return days before today" reads the age off "one" ACH payment while compute reads the latest ACH payment; the two coincide unless an older settled ACH coexists with a newer unsettled one (observation O-6).
- Aggregation caveats recorded as observations (no task world exercises them): `u_hours` / `q_hours` SUM every pending consent of the kind while the rule speaks of "that consent" (O-7); `CFIELD` takes the first matching warranty when several active warranties of one plan exist (O-7); `r_committed` nets aggregates rather than consent by consent (O-7).

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy: (sign_unrelated_damage_addition_ef94c675, amount_usd), (record_insurer_authorization_cee3bb86, estimated_repair_days), (accept_denied_operations_addition_a285270b, amount_usd), (issue_overpayment_refund_b142d0d2, amount_usd).
- uuid8s `ef94c675`, `cee3bb86`, `a285270b`, `b142d0d2`: pairwise distinct, no shared prefix or tail, no sequence pattern. PASS.
- Docstrings: no tool name of another tool, no sequence words relative to other actions (the only hits of before/after/once/then are "rounded ... before it is recorded", "once the signature is recorded", "can then see" - all internal to one call). PASS.
- Function bodies: none reads a consent status, a balance, a pending form or a supplement before writing; `record_insurer_authorization` does not check `consents_signed` or pending additions; `issue_overpayment_refund` does not check pending consents. The tool layer judges no prerequisite. PASS.
- Observations: `record_insurer_authorization_cee3bb86` books the original-estimate approval with `betterment_usd=0.0` whereas base `claim_evt_authorization` books it "with the insurer's betterment" (O-8); the two addition tools only flip the consent to signed - no tool of this difficulty posts the `claim_customer_charge` row both addition policies name as their subject (O-8). Neither changes a scored value in either task world.

### prerequisite_graph

- `prerequisite` filled on all four (two `[]`). Each `problem` names another extended policy in this file, none is a base policy or itself. Graph: authorization -> unrelated_price; refund -> denied_price. Acyclic, two disjoint components.
- `policy_source` verbatim in the blocked policy's own rule: both edges, verified mechanically.
- `form: state` on both, no `fallback_reason` - consistent.
- `condition` ("No customer-pay addition consent of the repair order has consent_status pending_customer; every one issued is signed or revoked ...") matches the strength and scope of the sentence ("every customer-pay addition consent issued on the repair order stands signed or revoked") - neither strengthened nor weakened.
- `resolved_by` equals the depended-on policy's `target_tool` on both edges; the tool's effect (`consent_status='signed'`, `amount_usd=price`) changes the gated binding (`a_addition_hours` sums signed hours; `r_committed` sums signed amounts). `kind: value_input` with `gate` naming a real binding of the blocked compute on both edges. PASS.
- Observation O-4: each edge's `effect` is phrased around "the pending unrelated-damage consent" / "the pending denied-operation consent" - a world-specific presupposition inside general text.

### prerequisite_sentences

Edge A (authorization): "The planned repair days are fixed only after every customer-pay addition consent issued on the repair order stands signed or revoked."
Edge B (refund): "An overpayment is not refunded until every customer-pay addition consent issued on the repair order stands signed or revoked."

Four-point test, both edges: (1) ordering connective present ("only after", "not ... until") joining the policy's own result to the waited-on state; (2) the waited-on thing is a record-visible state in record words (`claim_consents.consent_type = customer_pay_addition`, `consent_status in {signed, revoked}`), no action, performer or tool; (3) no tool name, policy id, snake_case token or row id; (4) closed set ("every ... issued on the repair order"), the same scope as `condition`. PASS.

Derivation the reader performs (sentence + records + the depended-on rule):
- A pending `customer_pay_addition` consent on the repair order makes the state false. Its `addition_kind` names which rule prices it: "An unrelated-damage addition is priced when its customer-pay addition consent is signed ..." or "A denied-operation addition is priced when its customer-pay addition consent is signed ...". The write that makes the state true is the customer's signature at that rule's price (`revoked` has no write in this difficulty; it is reachable only if the customer withdraws, which the reader asks about).
- Uniqueness per world: exactly one write per pending consent, selected by `addition_kind`. In the abstract the state can be brought about by either of the two signing writes, so the hop resolves from the records, not from the sentence alone (observation O-3): the refund edge's declared `problem` is the denied-operation policy, but its sentence is kind-agnostic - in a world holding a pending unrelated-damage consent at refund time it would lead to the other signing write, which `prerequisite` does not list. Neither task world contains such a mix (checked per task).
- Sentence not restated in the depended-on rules; no second wording, tool name or other problem id in either blocked rule. Docstrings silent about sequence (above). PASS.
- Observation O-5: the authorization edge adds a gate (planned days, hence the authorization write, wait on pending additions) that base `claim_evt_authorization` does not have ("A repair order is authorized when the insurer approves the original estimate ... Without both signatures the authorization is not recorded"); the base sentences state necessary conditions, so an added necessary condition is not a contradiction of their text and is not listed in `overwrite`. Recorded, not raised.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- unrelated_addition_price vs `claim_evt_customer_pay_additions`: price clause ("charged at the amount on the written customer-pay estimate line") - superseded, declared; consent sentence ("The customer's customer-pay addition consent for that amount is signed.") - superseded, declared; "The charge carries the consent_id." - followed; unrelated hours cap (`unrelated_damage_max_labor_hours`) - followed (but see F-2: it makes a tier unreachable); withdrawal credit - followed; "never billed to the insurer and never reduce the deductible" - followed. vs `claim_evt_deductible_betterment`, `claim_evt_withdrawal` - not touched. vs `claim_evt_storage` - the eligibility sentence "The vehicle is still at the center more than the tier's pickup free days after the vehicle-ready date." is declared superseded by a sentence about additions (O-1).
- authorization_repair_days vs `claim_evt_authorization`: repair-days clause superseded, declared; approval booking, consents gate, route and response days, "no other approval type" - followed. vs `claim_evt_total_loss` - not touched. Added pending-addition gate - O-5.
- denied_operation_price: same three declared supersessions as the unrelated policy (price clause, consent sentence, storage eligibility sentence); vs `claim_evt_supplement_decision` ("Denied operations are not performed unless the customer signs a customer_pay_addition consent ...") - followed; deductible/withdrawal - not touched.
- overpayment_refund vs `claim_evt_customer_payments`: the excess-refund sentence superseded, declared; "The refund names the payment it returns." - followed; payments, financing and credits sentences - followed. The dropped "one refund per payment" is still enforced by the inherited `refund_names_payment` dedup.
- Disguised forms: no anonymous intermediate, 0/1 multiplier or dropped branch found that conflicts with an undeclared base sentence. No sentence of any rule calls a base output "wrong".
- Composition observation O-1: two policies each supersede the same base clauses of `claim_evt_customer_pay_additions` and the same eligibility sentence of `claim_evt_storage` with different replacement texts. Read per addition kind the merged semantics stay unique; the storage replacements remove `claim_evt_storage`'s own eligibility sentence on their face, but the remaining storage sentences ("when a completed vehicle is not collected in time", the day-zero counting rule) carry the same timing, so no conclusion changes. Neither task world has a storage charge.

Undeclared overrides: none found. Conflict half of check 1: PASS.

### factor_ladders

Per policy (effect label / decides / tiers / multi-source / cross_difficulty):

claim_ext_unrelated_addition_price (5 declared)
- addition_scope_rate / parameter / u_hourly / 3 tiers (<= 4.0 h touch-up, > 24.0 h collision, else panel) / single-source / -. **The > 24.0 h tier is unreachable** (F-2).
- returning_customer_discount / parameter / u_returning_pct / 3 tiers (5, 2, 0 %) / tier 2 a disjunction over two distinct warranty records, tier 1 a conjunction of holding and age of one warranty record / warranty.
- once_per_order_supplies / method / u_supplies / 3 tiers (none, flat cap, percentage of work) / single-source / -. Label accepted: the cap tier and the percentage tier compute the amount differently (flat vs proportional); it is a clamp, noted O-9.
- once_per_order_waste_fee / parameter / u_waste_fee / 3 tiers (0, 4.95, 6.95) / tier 2 compound (no posted charge AND within touch-up hours) / -.
- estimate_scan_credit / parameter / u_scan_credit / 3 tiers (full, 50 %, 0) / compound (estimate exists AND age within the tier window) / estimate.
- Baseline: "labor hours x panel rate + 6 % supplies + 6.95 waste fee, rounded" - self-sufficient, every sentence in the rule, params [panel_hourly_usd, supplies_pct, waste_fee_usd] match. Every fall-through equals the baseline input.
- Counts after striking addition_scope_rate: 4 factors (3 parameter, 1 method) - within bounds.

claim_ext_authorization_repair_days (6 declared)
- hidden_damage_allowance / method / a_estimate_hours / 3 tiers / single-source / estimate. **Mislabelled**: all three tiers are one formula, hours x (1 + p/100) rounded to one decimal, with p in {20, 10, 0} (F-4).
- production_daily_hours / parameter / a_daily_hours / 3 tiers (6.5, 4.0, class) / declared compound with "no submitted supplement adding structural operations" - **that part holds of every customer who reaches this write** (F-3); the ladder survives on plan size alone.
- calibration_days / parameter / 3 tiers (2, 1, 0) / single-source / adas.
- estimate_revision_days / parameter / 3 tiers (2, 1, 0) / single-source / estimate. Two revisions reachable (Scheduled/Teardown/Structural Blueprint allow 2-3 free revisions).
- parts_lead_days / parameter / 3 tiers (2, 1, 0) / tier 2 compound (disclosure signed AND no upgrade signed) / -.
- customer_pay_stage_days / parameter / 3 tiers (2, 1, 0) / -. The large tier (> 8.0 signed customer-pay hours at authorization) is reachable only through oem_upgrade consents carrying labor hours, since unrelated hours are capped at <= 8.0 in every class and no denied-operation consent can exist before authorization (O-10).
- Baseline: "estimated hours + signed customer-pay hours, / class hours per day, ceiling, + intake days" - self-sufficient, verbatim in the rule, params match; every fall-through equals the baseline.
- Counts after the tests: 6 factors, **0 honest `method`** (F-4) - below the floor of 1.

claim_ext_denied_operation_price (6 declared)
- insurer_calibration_allowance / method / q_calibration_line / 3 tiers (price - allowance floored at 0; none; full price) / compound (calibration added AND decision) / - . Genuine method. Tier 2 ("approved in full") and minimum_billable_hours tier 2 ("hours above the supplement's own labor hours") are reachable only when the most recently decided supplement is not the one whose operations the consent covers (O-2).
- denied_work_hourly_rate / parameter / 3 tiers (118, 115, 104) / tier 2 compound / -.
- minimum_billable_hours / method / 3 tiers (floor 1.0, cap at supplement hours, as written) / - . Clamp; label accepted on the same footing as supplies (O-9).
- customer_alignment_checks / parameter / 3 tiers / compound (line remains AND tier requires alignment AND corrected / checks) / adas.
- calibration_warranty_discount / parameter / 3 tiers (10, 5, 0 %) / tier 2 disjunction over distinct warranty records / warranty.
- pre_calibration_scan / parameter / 3 tiers (79.95-type full fee, 50 %, 0) / compound (line remains AND age) / -.
- Baseline: "full calibration price when the supplement added calibrations + consent hours x body rate, rounded" - self-sufficient, verbatim, params match; every fall-through equals the baseline. Counts: 6 (4 parameter, 2 method).

claim_ext_overpayment_refund (6 declared)
- refunded_payment_choice / method / r_refund_cap / 3 tiers / tier 2 compound over card and ACH rows / -.
- reinspection_reserve / parameter / 3 tiers (50, 25, 0) / compound (undecided AND route) / -. Realism concern O-11.
- deductible_exposure_hold / parameter / 3 tiers / compound over supplement rows and the deductible ledger / -. Multi-source.
- betterment_exposure_hold / parameter / 3 tiers / compound / -.
- funds_clearing_hold / parameter / 3 tiers / ordered over check and ACH rows / -.
- other_desk_charges_hold / parameter / 3 tiers / ordered over estimate and warranty ledgers / estimate (tier 2 reads warranty).
- Baseline: "excess - signed uncharged additions, against the most recent payment, capped at it, rounded" - self-sufficient, verbatim; params [refund_processing_business_days] match the only parameter the baseline names. Counts: 6 (5 parameter, 1 method).

Per-task floors (assuming one tree per task, confirmed per task): tree {authorization, unrelated price} has cross-difficulty factors (estimate, adas, warranty) and a multi-source factor (returning_customer_discount); tree {refund, denied price} has cross-difficulty factors (adas, warranty, estimate) and a multi-source factor (deductible_exposure_hold).

Every tier of every ladder is stated in its `rule` (condition and value/method) and implemented in `compute`; no tier lives only in `compute`. Two tiers of one ladder never share a value or method.

### findings

- **F-1 SOURCE-POLICY RED - scan-credit filter invented by compute.**
  Symptom: the compute and the rule pick different source estimates for the scan credit. Root cause: `u_quote_booking: "CFIELD('estimate','booking_id', vehicle_id=F('vehicle_id'), payer_type='customer_pay', status='estimate_written')"` filters on `status='estimate_written'`, while the rule says "A pre-repair scan fee charged on a written customer-pay estimate of the same vehicle that was never converted is credited against the addition". Evidence: `db_schema.estimate_bookings.status` lists `declined` alongside `estimate_written`, and a declined booking keeps its `estimate_written_date` ("Date the booking reached cancelled, no_show, declined or expired"); estimate_evt_expiry keeps a declined estimate's charges due. Demonstrated consequence: a customer-pay Scheduled Estimate written 9 days ago, scan fee 49.95 paid, then declined - the rule credits 49.95 (within the 14-day window); the compute credits 0. Affected: `claim.extended.yaml` -> claim_ext_unrelated_addition_price -> compute `u_quote_booking`. Bears on: task 0 only by policy; task 0's world has no declined customer-pay estimate (its only one is `estimate_written`), so no scored value of task 0 moves.
- **F-2 SOURCE-FACTOR RED - unreachable tier in addition_scope_rate.**
  Symptom: the "more than the panel scope hours (24.0) -> collision hourly rate" tier can never be selected. Root cause: base `claim_evt_customer_pay_additions` (inherited, not overwritten) keeps "the unrelated work on one repair order ... within unrelated_damage_max_labor_hours (claim_msr_unrelated_hours)", and that parameter is at most 8.0 in every class (Express 4.0, Standard 8.0, Major 8.0, Structural 6.0, Certified Structural 6.0, Aluminum 4.0), while `u_hours` reads only `addition_kind='unrelated_damage'` consents. Demonstrated consequence: no unrelated-damage consent that can lawfully be signed exceeds 8.0 hours, so the ladder is a two-tier ladder (touch-up / panel) on every reachable world. Affected: claim_ext_unrelated_addition_price -> rule sentence "an addition of more than the panel scope hours takes the collision hourly rate" and factor `addition_scope_rate`. Bears on: task 0 (the factor still moves task 0's price; the policy keeps 4 factors after striking).
- **F-3 SOURCE-FACTOR RED - vacuous condition in production_daily_hours.**
  Symptom: "on a repair order with no submitted supplement adding structural operations" / "or a repair order with a submitted supplement adding structural operations" divides no customer at this write. Root cause: the write is the authorization, which the lifecycle allows only `from: assigned` ("The insurer's authorization of the repair estimate is recorded on the repair order"), and base `claim_evt_supplement_routing` eligibility `work_not_finished` admits a supplement only in "authorized, in_repair or on_hold status". Demonstrated consequence: at every authorization `a_structural_supplements = 0`; the compound condition holds of every customer who reaches this write, and the factor's multi-source shape is illusory - it is a single-source plan-size ladder. Affected: claim_ext_authorization_repair_days -> rule sentence on daily hours, factor `production_daily_hours` (`evidence: [history, tier_param]`). Bears on: task 0 (ladder still three tiers on plan size; see 0.md for weight).
- **F-4 SOURCE-FACTOR RED - mislabelled `method` leaves the authorization computation with no method factor.**
  Symptom: `hidden_damage_allowance` is labelled `method`, but its tiers are "raised by the photo allowance percentage (20) and rounded to one decimal place", "raised by the inspected allowance percentage (10) and rounded to one decimal place", "taken as written" - one formula, hours x (1 + p/100) rounded to one decimal, with p = 20, 10, 0 (on a 1-decimal input the rounding at p = 0 is the identity). Root cause: a rate substitution labelled as a change of algorithm. Every other factor of the policy is labelled `parameter`. Demonstrated consequence: the computation has 0 factors whose tier changes how the quantity is computed, below the floor of 1. Affected: claim_ext_authorization_repair_days -> `factors[hidden_damage_allowance].effect`. Bears on: task 0.
- Observations (not grounds for rework): O-1 duplicated supersession of the same base clauses by two policies, including `claim_evt_storage`'s eligibility sentence; O-2 denied-price tiers that bind to "the most recently decided supplement" rather than the supplement the consent's operations came from; O-3 kind-agnostic prerequisite sentence vs a fixed `problem` on the refund edge; O-4 world-specific phrasing in `effect`; O-5 authorization gate added without a base declaration (necessary-condition reading); O-6 "when one was made" (ACH) wording vs latest-ACH compute; O-7 aggregation caveats (SUM over several pending consents, first-match CFIELD, aggregate netting of committed additions); O-8 tool books `betterment_usd=0.0` and no tool posts the addition charge; O-9 supplies and minimum-billable-hours are clamps labelled `method` (accepted); O-10 large stage-days tier reachable only via upgrade consents with labor hours; O-11 the refund's reinspection reserve holds money against no customer charge type the charter defines (`charge_type`: deductible, betterment, customer_pay_upgrade, unrelated_damage, withdrawal_teardown, storage), while the same supplement's deductible and betterment exposure are held by their own factors - a realism concern not raised to RED because it shows only that the charter has no matching charge, not that no shop holds such a reserve.

## closing_checklist

Written after both reveals (2026-10-11 01:55:03 UTC); the charter-global section above was frozen at 01:53:25 UTC and is unchanged.

- Audit files one-to-one with tasks: `0.md`, `1.md`, alongside this file. First revision; no older revisions.
- Comparison PASS status: task 0 - unique solution PASS, problem tree PASS, policy PASS, **factors SOURCE-FACTOR RED**; task 1 - all four PASS.
- Coverage and scope: `charter_scope` of task 0 = {claim_ext_unrelated_addition_price, claim_ext_authorization_repair_days}, of task 1 = {claim_ext_denied_operation_price, claim_ext_overpayment_refund} - pairwise disjoint, jointly all four extended policies, each scope containing its whole tree. Task tools closed over GT; uuid8s independent (`action_binding_and_uuids`).
- Problem trees: each has 1 prerequisite problem, 1 value_input edge, an owner=user write, no cycle; the difficulty's graph is two disjoint edges, acyclic.
- Factors: every computation has a self-sufficient baseline giving a definite non-gold number (381.77, 5, 957.40, 120.00) and every declared factor bears weight on its world. Not met: claim_ext_authorization_repair_days has no honest `method` factor (F-4); production_daily_hours carries a vacuous condition (F-3); addition_scope_rate has an unreachable tier (F-2).
- Policy: F-1 (scan-credit status filter without a rule basis) is a charter-level SOURCE-POLICY RED with no consequence on either task world.
- Gates: the auditor did not re-run the instantiation gates; the coordinator snapshot of 2026-10-11 (all green; traceability deferred to the KB step) is cited, and the audited artifacts' hashes (`72b5bbd6efa4df1c`, `1bafc3ca4248a394`) match the snapshot's freeze inputs.

Difficulty result: **does not pass** the source-layer audit - task 0 fails the factors relationship (SOURCE-FACTOR RED: F-4, F-3, F-2), and the charter carries SOURCE-POLICY RED F-1. Task 1 passes all four relationships.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: erl-task-policy-audit subagent (Claude Opus 5.5). Started 2026-10-11 04:21 UTC; this section frozen before any round-2 task JSON was opened.
- Inputs (sha256, first 16): `claim.extended.yaml` = `3bf60d07bd689da5` (**changed** from `72b5bbd6efa4df1c`), `task_tools.py` = `1bafc3ca4248a394` (unchanged), masked views `4787511ca59951e0` / `905324258da280f3` (unchanged, so both worlds are byte-identical to round 1).
- Because the charter hash changed, every charter-global section is re-derived in full below. Because the tool module did not change, the round-1 `action_binding_and_uuids` conclusions about the tools (uuid8s, docstrings, function bodies) carry forward by reference on hash `1bafc3ca4248a394`; the `(target_tool, computes)` claims are re-checked against the new charter.
- Contamination disclosure (round level): this auditor read the round-1 GT (`evaluation_criteria`, `computations`, `prerequisite_closure`, `design_rationale`, `solvability_contract`) at 01:55 UTC in round 1. The round-2 per-task derivations below are therefore **not blind** to the round-1 scored values. They are re-derived from the round-2 charter's rule text and the worlds. The round-1 frozen derivations above are left untouched.
- The reworker's claims (closed F-1..F-4, O-4, T1-O5, T1-O6) were not used as evidence.

### base and diff scope

- Base section lines 1-1804 still byte-identical to `blueprint/products/claim.yaml`, apart from the same trailing blank line.
- `claim_ext_denied_operation_price` and `claim_ext_overpayment_refund`: rule, overwrite, params, compute, factor ladders and baselines are identical to my round-1 reading. The only change is the prerequisite `effect` text of the refund edge.
- `claim_ext_unrelated_addition_price`: the hourly-rate ladder was replaced (`panel_max_hours`/`collision_hourly_usd` removed, `certified_hourly_usd: 112.0` added), and the scan-credit source wording was changed.
- `claim_ext_authorization_repair_days`: `inspected_allowance_pct: 10` was replaced by `inspected_allowance_hours: 1.5` (an additive reserve), the structural-supplement condition was removed from the daily-hours ladder, and the edge `effect` was reworded.

### policy_conflict_scan (r2)

Same four policies, subjects, target tools, triggers and two disjoint prerequisite trees as in round 1. No new overlap. The certified tier reads the repair class's `oem_certified_procedures_required`, a class parameter that base `claim_repair_class_assignment` fixes ("The class fixes every per-class parameter of this charter"), so it is not a new cross-category read. Declared `cross_category` blocks still match the compute reads. Scope partition unchanged. PASS.

### rule_compute_equivalence (r2)

- Mechanical sweep on the new file: all `compute_basis` quotations are verbatim in their rules (0 misses), compute keys equal basis keys in all four policies, all `baseline.rule` sentences are verbatim in their rules, and all `overwrite.replaced_by` sentences are verbatim in their rules.
- Hourly rate. Rule: "an addition of no more than the touch-up scope hours takes the touch-up hourly rate; an addition of more than the touch-up scope hours on a repair order whose class requires manufacturer-certified procedures takes the certified hourly rate ...; any other addition takes the panel hourly rate". Compute `u_hourly` implements exactly that, using `P('oem_certified_procedures_required') == True`. Equivalent.
- Scan credit. Rule: "a customer-pay estimate of the same vehicle that still stands as a written estimate, neither converted nor declined nor expired". Compute filters `payer_type='customer_pay', status='estimate_written'`. In `db_schema.estimate_bookings.status`, the statuses other than `estimate_written` that a written estimate can reach are converted, declined and expired, and all three are now excluded by the rule. Equivalent. **F-1 closed.**
- Hidden-damage allowance. Rule: the Photo Estimate "scales them up by the photo allowance percentage, rounded to one decimal place"; the Drive-In/Scheduled/Mobile Estimate "adds the inspected allowance hours to them as a fixed reserve"; any other estimate type keeps the hours as written. Compute implements `RND(h*1.2,1)` / `RND(h+1.5,1)` / `h`. The `RND(…,1)` on the additive branch is a no-op on a one-decimal input plus 1.5. Equivalent.
- Daily hours. Rule: "a plan of more than the two-technician minimum hours takes the two-technician daily hours; a plan of no more than the small-job hours takes the single-bay daily hours; any other plan takes the class's labor hours per production day". The compute has no supplement read left, and `a_structural_supplements` is gone from compute, basis and `inputs`. Equivalent.
- Denied-operation price and refund: unchanged and equivalent (round-1 section stands on identical text).
- Observations O-6 and O-7 still apply, on unchanged text.

### action_binding_and_uuids (r2)

The four `(target_tool, computes)` pairs are unchanged and each is claimed by exactly one policy. Tool conclusions carry forward on hash `1bafc3ca4248a394`. O-8 still applies. PASS.

### prerequisite_graph (r2)

Both edges unchanged in `problem`, `kind`, `gate`, `form`, `policy_source`, `condition` and `resolved_by`. `policy_source` is verbatim in each blocked rule (re-verified). The gate bindings `a_addition_hours` and `r_committed` still exist. The graph is acyclic.

The `effect` texts are now general: "When a customer-pay addition consent awaiting the customer is signed, its labor hours join …" and "… its signed price joins …". **O-4 closed.**

`a_addition_hours` is now also listed in the bindings of the `production_daily_hours` factor. It appears in no other factor's bindings, so the factors' binding sets stay disjoint. PASS.

### prerequisite_sentences (r2)

The two sentences are unchanged, so the round-1 four-point test and derivation stand. O-3 (a kind-agnostic sentence against the fixed `problem` on the refund edge) and O-5 still apply, on unchanged text. PASS.

### override_declarations (r2)

- The three overwrites of the unrelated-price policy and the one overwrite of the authorization policy are unchanged and still match base verbatim.
- The new certified tier uses a class parameter the base already defines and contradicts no base sentence.
- The new additive allowance sits inside the already-superseded repair-days clause.
- No undeclared override. O-1 still applies.

PASS.

### factor_ladders (r2)

- **claim_ext_unrelated_addition_price / addition_scope_rate**, parameter. Its tiers are: touch-up 96 (≤ 4.0 h); certified 112 (> 4.0 h and the class requires certified procedures); panel 104 otherwise.
  - Reachability: certified procedures are required by Certified Structural (unrelated cap 6.0) and Aluminum Certified Structural (cap 4.0). The certified tier is therefore reachable for Certified Structural orders between 4.0 and 6.0 hours. The panel tier is reachable for Standard and Major orders between 4.0 and 8.0 hours, and for Structural orders between 4.0 and 6.0 hours.
  - Every tier is reachable and the three values are distinct. A certified labor rate above the panel rate on a certified-structural order is a real industry practice.
  - **F-2 closed.**
- **claim_ext_authorization_repair_days / hidden_damage_allowance**, method. Its tiers are: proportional scaling (×1.20, rounded); a fixed additive reserve (+1.5 h); as written.
  - Scaling and adding a fixed reserve are different algorithms. With round-1 and round-2 parameters, no single "hours × (1 + p)" or "hours + c" form reproduces both of the first two tiers. The label is honest.
  - The method count of this computation is now 1. **F-4 closed.**
- **production_daily_hours**, parameter. It is now a single-source, three-tier ladder on plan size: > 16.0 → 6.5; ≤ 6.0 → 4.0; otherwise the class rate.
  - Every condition divides customers at the authorization write.
  - The factor no longer claims multi-source, and its `evidence` stays `[history, tier_param]`.
  - **F-3 closed.**
- All other ladders are unchanged from round 1. Every tier is stated in its rule and implemented in compute. No two tiers of one ladder share a value or method. Every fall-through equals its baseline.
- Counts:
  - unrelated price: 5 factors (4 parameter, 1 method).
  - authorization: 6 factors (5 parameter, 1 method).
  - denied price: 6 factors (4 parameter, 2 method).
  - refund: 6 factors (5 parameter, 1 method).
- Per tree:
  - Tree 0 multi-source: returning_customer_discount. addition_scope_rate's tier 2 is now also a compound condition over the consent and the repair class.
  - Tree 1 multi-source: deductible_exposure_hold.
  - Cross-difficulty factors remain in both trees.

### findings (r2, charter-global)

- F-1 closed; F-2 closed; F-3 closed; F-4 closed (evidence in the sections above).
- O-4 closed.
- No new charter-global defect found in the reworked text.
- Observations still open on unchanged text: O-1, O-2, O-3, O-5, O-6, O-7, O-8, O-9, O-11.
- O-10 now reads: the large stage-days tier is reachable only through upgrade consents that carry labor hours, as before.

### closing_checklist (revision 2)

Written after the round-2 reveals at 04:23 UTC. The revision-2 charter-global section above was frozen first and has not been changed since.

- Audit files: `0.md` and `1.md` match the two tasks one-to-one. Each now carries revision 1, untouched, followed by revision 2.
- Comparison status, revision 2: task 0 PASS on all four relationships; task 1 PASS on all four.
- Round-1 REDs:
  - F-1 (SOURCE-POLICY): closed.
  - F-2, F-3, F-4 and their task-0 demonstrations T0-F1..F3 (SOURCE-FACTOR): closed.
  - Reworker-addressed observations O-4, T1-O5 and T1-O6: closed.
- New defects: none found.
  - The new certified tier is reachable on Certified Structural orders between 4.0 and 6.0 hours.
  - The additive inspected reserve is an honest `method` tier.
  - Removing the supplement read from task 0 leaves every rule input reachable.
- Regressions: none.
  - The denied-operation and refund policies are textually unchanged.
  - All 23 factor sensitivities and the 4 baselines recompute to the same figures as in round 1.
- Coverage and scope:
  - The two scopes are disjoint and jointly cover all four extended policies.
  - The task tools close over GT.
  - The uuid8s carry forward unchanged (tool hash `1bafc3ca4248a394`).
- Prerequisite trees: each has 1 prerequisite problem, 1 value_input edge and an owner=user write. The difficulty's graph is acyclic.
- Factors:
  - The four computations have 5, 6, 6 and 6 factors.
  - Each computation has at least 2 `parameter` factors and at least 1 honest `method` factor.
  - Each tree has a multi-source factor and a cross-difficulty factor, with the other products' rows seeded.
  - Every factor bears weight against an honest baseline.
  - Every whole baseline is definite and differs from gold: 381.77 / 5 / 957.40 / 120.00.
- Gates: the coordinator's post-rework snapshot is cited (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; traceability deferred to the KB step). The auditor did not re-run the gates. The audited hashes `3bf60d07bd689da5` and `1bafc3ca4248a394` match the snapshot's inputs.
- Open observations (not grounds for rework): O-1, O-2, O-3, O-5, O-6, O-7, O-8, O-9, O-10, O-11; T0-O1..O3; T1-O1..O4.

Difficulty result (revision 2): **passes** the source-layer audit. Both tasks PASS policy self-consistency, the problem tree, factor weight and unique solution.
