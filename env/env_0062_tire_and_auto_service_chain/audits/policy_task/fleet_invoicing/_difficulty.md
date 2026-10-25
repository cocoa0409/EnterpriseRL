# Policy-task audit — fleet_invoicing / charter-global

## charter_global_frozen
- auditor: erl-task-policy-audit (independent of the instantiator), round 1, frozen 2026-10-15 (resumed after the 23:15Z cut; content derived before any GT reveal).
- freeze hashes (sha256, re-verified against the gate snapshot): `fleet.extended.yaml` 594ac93d055aef5507de822876739477334538060025d8956989c129abd3f2dc; `task_tools.py` 007720d97f5242269fc953e16cd10d699700be0fb82929c45c146f9823346cd8; views `0.json` 3d9b96a4…fd932, `1.json` e14254e3…7cd7608.
- read: blueprint.yaml, db_schema.json, share_tools.py (signatures), products/fleet.yaml, tires.yaml / brakes.yaml / hazard.yaml (parameter and event excerpts only), the extended charter, task_tools.py, the masked views, and the DSL semantics in skills/erl-task-instantiate/scripts/check_compute.py (MONTHS/DAYS/LATEST/COUNT/XCOUNT/_within/RND).
- masked / unread: evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure; worklog.md, plan.md; any /tmp/*_0062 scratch; other scenarios and sibling difficulties. Nothing below is derived from GT.
- entry conditions: gate snapshot supplied (all d_gates green; validate_scenario INVALID and check_traceability NOT OK only on pre-render items, out of scope); masked views and hashes supplied and match. Input complete.

### policy_conflict_scan
- Base copy (lines 1–1056) is byte-identical to blueprint/products/fleet.yaml (diff empty).
- Six extended policies; targets disjoint: `file_fleet_overlimit_dispute_8d937b85` (disputed_amount), `credit_fleet_early_pay_23cbfed3` (amount), `file_fleet_trip_fee_dispute_f6605125` (disputed_amount), `credit_fleet_tire_discount_840e1cf3` (amount), `credit_fleet_brake_discount_3a9816af` (amount), `assess_fleet_late_charge_341e13fe` (amount).
- Overlapping subjects: tire and brake both write `fleet_credit_memo` / `pricing_correction`; each rule self-scopes ("only for such a tire invoice … including one on a brake invoice, remains under … its own rule" and the mirror) — no overlap on one invoice. Both dispute policies write `fleet_invoice_disputes`; scopes disjoint (invoice of the latest remittance vs latest mobile_service_call invoice); recorded reasons differ (unauthorized_purchase / discount_not_applied).
- Cross-reads: early-pay `disputed_open` sums every open dispute on the invoice (any reason); late charge `open_disputed` sums every open dispute on the account. Late charge and early-pay both read `fleet_late_charge` history (12 whole months); tire `standing_factor` too. No two policies write a quantity the other overrides.
- Prerequisite graph has two components: {early_pay ← overlimit} and {late ← tire, brake, trip}. With M=2 the only exclusive and complete partition is one component per task; confirmed against charter_scope only after reveal (closing_checklist).
- Inherited base provisions that bind the extended writes: dispute window (`dispute_window_days`, pricing_correction and dispute_resolution credits / invoice disputes), desk limit (`credit_memo_desk_limit`), one late charge per statement month, no late charge on Public Sector, account `active` for invoicing.

### rule_compute_equivalence
Every compute line has a compute_basis quote that is verbatim in its rule, except `fleet_ext_overlimit_dispute.compute_basis.disp_invoice` ("files a dispute …" vs rule "contests that part by filing a dispute …") — wording drift, same meaning (observation O-6). Every factor ladder tier is a rule sentence and a branch of its `decides` binding, both directions. Gaps between rule and compute (none moves a value in either seeded world; see each task file):
- O-1 `fleet_ext_trip_fee_dispute.vehicles_served`: rule counts "the vehicles with an invoice dated the visit day from the store", compute counts invoice rows (a vehicle with two invoices that day counts twice).
- O-2 `fleet_ext_tire_discount_restore` / `fleet_ext_brake_discount_restore`: rule scope "an account invoiced without sales tax" has no compute counterpart (`tr_invoice`/`br_invoice` filter only category and discount 0.00).
- O-3 `fleet_ext_month_end_late_charge`: "measured oldest first" is an empty promise (aggregate netting); `due_total` adds a 240-month due_date lookback the rule does not state.
- O-4 `fleet_ext_brake_discount_restore.enrolled_vehicles` = total enrollments − total removals; rule is per vehicle ("its enrollments … outnumber its removals"). Equal unless a vehicle carries ≥2 enrollments net.
- O-5 DSL `RND` is Python `round` (binary float, ties-to-even), rule says half up; differs only on exact half-cent ties.

### action_binding_and_uuids
Each `(target_tool, computes)` claimed once. Docstrings: each describes one atomic write, names no other tool, states no sequence position (the word "Afterwards" describes the call's own visible effect), carries no concrete example amount, no default; parameters typed by class only. No factor id is a substring of any tool name (checked mechanically over 28 factor ids × 6 tools). uuid8s 8d937b85, 23cbfed3, f6605125, 840e1cf3, 3a9816af, 341e13fe: distinct, no shared prefix/suffix, no sequence. No tool validates eligibility or prerequisites (bodies only `find` the account and `create`/`update`). Owners: both dispute filings `owner="user"`, the four credits/charges `owner="agent"`. PASS.

### prerequisite_graph
- Every extended policy has `prerequisite` (`[]` for overlimit, trip, tire, brake). Edges: early_pay→overlimit (value_input, gate `disputed_open`), late→tire (value_input, `credit_memo_total`), late→brake (value_input, `credit_memo_total`), late→trip (value_input, `open_disputed`). All `problem` ids are extended ids, none self, graph acyclic.
- Every `policy_source` is verbatim in its own rule (checked mechanically); all `form: state`, no `fallback_reason`; `resolved_by` equals the depended-on policy's `target_tool`; each gate names a real compute binding; no authoring-viewpoint wording. `condition` texts match the sentence strength ("covers the part left unpaid" ↔ disputed_amount ≥ open; "each … invoice" ↔ every such invoice). PASS.

### prerequisite_sentences
1. early_pay: "The early-pay discount on an invoice that a remittance has paid only in part is credited only after an open dispute of an unapproved over-limit ticket registered for that invoice covers the part left unpaid." Connective "only after"; waited-on state = an open dispute row of the unapproved-over-limit kind on that invoice whose amount covers the open part (finder: `find_fleet_invoice_disputes`); no tool/id/snake_case. Single write bringing it about: the overlimit policy's filing (the trip-fee filing records another reason and targets a visit-fee invoice). Derivation: sentence → state absent on records → which rule's write registers such a dispute → `fleet_ext_overlimit_dispute` ("contests that part by filing a dispute of an unapproved over-limit ticket on the invoice its most recent remittance was applied to"). One reading. PASS.
2. late←tire: "The late charge of a month-end is not assessed until each tire invoice past due at that month-end that was posted with no fleet discount carries a pricing correction credit memo." State form, single resolver (tire rule is the only one scoped to tire invoices without discount). PASS, but see O-7.
3. late←brake: "Before the month-end late charge is fixed, each brake invoice past due … must carry its own pricing correction credit memo as well." PASS ("as well" refers back to sentence 2; no second wording of either edge). See O-7.
4. late←trip: "The month-end late charge is fixed only after the mobile service visit fee the business contests stands under an open dispute registered on that fee invoice." State form; resolver = trip-fee filing. The "the business contests" clause makes the edge depend on the customer's stated intent (elicitable). PASS.
- Depended-on rules do not restate any sentence. No rule states a cross-problem order that grounds no edge. No base sentence grounds an edge.
- O-7 (observation, latent gate/resolver scope mismatch): sentences 2/3 demand a credit memo on *each* past-due no-discount tire/brake invoice, while the resolving rules correct only "the account's most recent tire [brake] invoice of that kind" and only on an account invoiced without sales tax. On a world with two such invoices, or a taxed one, the gate can never be satisfied by any write. Not present in the seeded world (one invoice each, tax-exempt account).

### override_declarations
Sentence-by-sentence over `base_policy_refs`:
- overlimit (refs fleet_evt_credit_memo, fleet_evt_invoice; `overwrite: []`): follows dispute-window, one-invoice-per-ticket-and-category, roster and off-roster sentences. **Departs, undeclared**, from fleet_evt_invoice "A ticket above the account's ticket_approval_limit needs the fleet manager's approval before work starts." — the extended rule makes "the account's ticket approval limit plus a safety allowance and a weekend allowance" the authorized amount, i.e. up to 175.00 above the limit is deemed authorized without approval. → finding F-1.
- early_pay (refs payment, credit_memo, late_charge): two overwrites, both superseded clauses verbatim in base and replaced_by verbatim in rule. Follows "Credit memos … not the discount base", period counting, program-0 sentence. Latent: base "a full payment that already deducted the discount is applied as payment plus the discount row" is not overridden yet the extended paid-in-full test (`left_open_beyond_dispute <= 0`) would refuse such a remittance (O-8; not in either world).
- trip (refs credit_memo, invoice): overwrite of the mobile-fee sentence declared, scoped to contested fees.
- tire / brake (refs credit_memo, invoice): overwrite of "A pricing_correction restores the category_discount_pct the invoice should have received" declared. Not declared: the tire tier "the fleet discount and the instant savings do not combine" and the brake tier "Severe-Duty … pad sets are sold to fleet accounts at a net fleet price" both restate how the ticket is priced in a way fleet_evt_invoice's discount_amount sentence (with tires_purchase_ticket / brakes fleet_discount_applicable) does not — recorded under F-2 (same rework class as F-1).
- late (ref late_charge): main clause superseded and declared; one-per-month, nothing-past-due, rate-0, open-dispute and Public Sector sentences followed.
- O-9: every extended rule states its baseline sentence unqualified before refining it; the early-pay rule re-asserts verbatim ("the discount is early_pay_discount_pct percent of the invoice amount, rounded half up to the cent") a clause its own overwrite declares superseded. Pattern required by the baseline-in-rule design; recorded, not red.

### factor_ladders
| policy | factors (effect) | multi-source | cross_difficulty |
|---|---|---|---|
| overlimit | ticket_measure (m), safety_work_allowance (p), weekend_ticket_allowance (p), repeat_unapproved_deductible (p) | ticket_measure (roster rows + same-day invoices) | none |
| early_pay | remit_speed_points (p), approval_tenure_points (p), tire_program_bookings (p), invoiced_volume_points (p), remit_channel_points (p), disputed_invoice_base (m) | remit_speed_points (payment row + late-charge rows) | tire_program_bookings → tires |
| trip | visit_size_schedule (m), weekend_visit_surcharge (p), visit_tire_install_credit (p), visit_route_credit (p) | none | visit_tire_install_credit → tires |
| tire | ticket_promotion_method (m), tire_volume_pricing (p), same_day_fleet_pricing (p), commercial_lt_program_pricing (p), late_record_standing (p) | ticket_promotion_method (tire set + line params) | ticket_promotion_method → tires; commercial_lt_program_pricing → hazard |
| brake | brake_line_scope (m), brake_volume_pricing (p), brake_axle_points (p), brake_fleet_size_pricing (p), brake_tenure_pricing (p) | brake_line_scope (both axle jobs + line params) | none declared (O-10) |
| late | seasoned_account_tiering (m), utilization_rate_adjust (p), closing_remittance_relief (p), invoiced_volume_rate_adjust (p) | seasoned_account_tiering (approval_date + late-charge rows) | none |
- Counts per policy within 4–6, ≥2 parameter, ≥1 method. Every ladder has 3 pairwise-disjoint tiers stated in the rule, distinct outcomes, fall-through = baseline. Labels honest (method tiers change the computation; parameter tiers change one number). Per component: {early_pay, overlimit} has multi-source and a tires cross-difficulty factor; {late, tire, brake, trip} has multi-source and tires/hazard cross-difficulty factors.
- Realism (F-2, RED): tire `ticket_promotion_method` tier 1 ("fleet discount and instant savings do not combine; the rate applies to the price with the savings added back, less the savings") and brake `brake_line_scope` tier 2 ("Severe-Duty … pad sets sold at a net fleet price; the rate applies only to labor and rotor work") are methods for a *pricing correction* — the restoration of a discount the invoice failed to receive — that give less than the posting rule gives the same ticket. Base fleet_evt_invoice applies category_discount_pct "to the ticket's pre-tax price excluding discount_excluded_items"; tires_purchase_ticket defines that pre-tax price net of set_instant_savings (so at posting the two combine); brakes charter sets `fleet_discount_applicable: true` for the Severe-Duty line with no pad exception (and lists no shop item besides shop supplies as excluded). A business does not publish a "correction" that leaves the customer paying more than a correctly posted identical ticket. Same class, second form (observation O-11, not red): the tire and brake "points" (volume, same-day, Commercial LT, standing; volume, axle, fleet size, tenure) raise the correction rate above category_discount_pct, a rate the posting rule never gives any invoice; defensible only as a make-good.
- Other realism notes (observations): O-12 trip-fee schedule applies "only" to contested fees (weekend surcharge exists only for contested visits) — defensible as an on-request courtesy re-rate; O-13 early-pay "tire program points" (cash discount boosted by tire bookings) and overlimit repeat deductible (reduces a dispute because earlier ones were upheld) are unusual but plausible; O-14 "Commercial LT program points" count allowance grants on any plan that grants roadside calls (Plus 36, Life-of-Tread too) — label narrower than rule.

### findings
- **F-1 SOURCE-POLICY RED — undeclared override (class: extended departs from a fleet_evt_invoice sentence not named in overwrite).** Symptom: `fleet_ext_overlimit_dispute` (overwrite []) deems the ticket authorized up to "the account's ticket approval limit plus a safety allowance and a weekend allowance". Root cause: base fleet_evt_invoice "A ticket above the account's ticket_approval_limit needs the fleet manager's approval before work starts." is handled differently and not declared. Consequence: two readings of the unapproved part (with/without allowances). Class members across the charter: (a) this sentence in overlimit [bears on the overlimit-claiming task]; (b) tire tier-1 "do not combine" vs fleet_evt_invoice discount_amount sentence; (c) brake Severe-Duty "net fleet price" vs fleet_evt_invoice discount_amount sentence + brakes fleet_discount_applicable — (b)(c) also F-2. Affected: extended.yaml fleet_ext_overlimit_dispute.rule/overwrite (and tire/brake overwrite lists).
- **F-2 SOURCE-FACTOR RED — unreal ladder (class: pricing-correction method that restores less than the posting rule gives).** Members: tire `ticket_promotion_method` tier 1; brake `brake_line_scope` tier 2. Bears on the task claiming tire/brake; consequence demonstrated there. Second-form members O-11 (points).
- Observations O-1…O-14 as above; none moves a scored value in either seeded world (checked in task files).

## closing_checklist
Written after both reveals; the difficulty is **not closed**.
- Files: 0.md, 1.md, _difficulty.md present; round 1, no prior revision.
- Scopes (from charter_scope): task 0 {overlimit, early_pay}, task 1 {tire, brake, trip, late} — pairwise disjoint, jointly complete over the six extended policies and six tools; uuid8s independent.
- Trees: task 0 n=1 (1 value_input, 1 user write), task 1 n=3 (3 value_input, 1 user write); whole graph acyclic.
- Factors: mechanical weight proved on both worlds (all GT figures equal the auditor's); F-2 strikes tire `ticket_promotion_method` and brake `brake_line_scope` on reality grounds.
- Open items: **F-1** (SOURCE-POLICY, task 0), **F-2** (SOURCE-FACTOR, task 1). Gates to be re-run on the reworked form.

## revision_2

### charter_global_frozen (round 2)
- frozen 2026-10-15 before any round-2 GT reveal. extended.yaml 1af9a4d72582ebca5929e868927ae244551dace7da9be770dfecb9ab8dbb8b70 (changed → every charter-global section re-derived); task_tools.py 007720d9…46cd8 (unchanged → action_binding_and_uuids carried forward). Base copy still byte-identical to blueprint/products/fleet.yaml.

### rule_compute_equivalence / prerequisite_graph / prerequisite_sentences (round 2)
- Every compute_basis quote verbatim in its rule (O-6 closed); every baseline.rule in its rule; every overwrite superseded_clause verbatim in base and replaced_by verbatim in rule; every factor binding exists in compute; no factor id ⊂ tool name.
- O-1 closed by rewording (trip rule now counts "the invoices dated the visit day … so a vehicle invoiced for two kinds of work counts twice"); realism note R2-O4: a real visit fee would count vehicles, not work orders — no effect where each van carries one invoice.
- O-2 closed (`tax_free_account` / `tax_free_brake_account` gate the result). O-3 closed ("oldest first" dropped; "less than twenty years old" now in the rule). O-4 closed for brake (fleet-size points removed); the same aggregate count is now used by trip `visit_fleet_size_credit` with matching rule wording ("roster shows 50 or more enrollments beyond its removals").
- O-7 closed: late-charge gates now read "the account's most recent tire [brake] invoice posted with no fleet discount, when it is past due at that month-end on an account invoiced without sales tax", the same scope the resolvers correct. Graph unchanged (early_pay←overlimit; late←tire, brake, trip), acyclic, state form, sources verbatim, single resolver per edge.
- R2-O1 (new, latent): early-pay overwrite #1 now passes the paid-in-full test with the early-pay discount itself still open, while the prerequisite sentence demands that the dispute "cover the part left unpaid"; when open − disputed is positive but ≤ the discount the two sentences disagree. Not reachable in either seeded world.

### override_declarations (round 2)
- F-1 class: (a) overlimit now declares the approval sentence (scoped to disputed tickets); (b) tire "do not combine" and (c) brake "net fleet price on pads" no longer exist — the restored discounts follow fleet_evt_invoice's discount_amount sentence. **F-1 closed.**
- O-8 closed (deducted-discount remittance accommodated). Other sentence-by-sentence conclusions unchanged from round 1.
- R2-O3: the overlimit allowance and the tire/brake make-goods are scoped by self-naming ("only for such a ticket/invoice"); tire/brake make-goods apply only on accounts invoiced without sales tax (taxed accounts fall back to the base restoration) — a scope artifact a real program would not tie to tax status; no effect in either world.

### factor_ladders (round 2)
| policy | factors (effect) | cross_difficulty |
|---|---|---|
| overlimit | ticket_measure (m; tiers: split ticket combined / single invoice less credit memos / invoice), safety (p), weekend (p), repeat deductible (p) | none |
| early_pay | unchanged 6 (5 p, 1 m) | tires |
| trip | visit_size_schedule (m), weekend (p), tire install credit (p), route credit (p), fleet size credit (p, new) | tires |
| tire | tire_makegood_line (m: mount/balance back for ≥4 tires / one tenth of restored discount for 1–3 / none), repeat_billing_error_credit (p), road_hazard_program_credit (p), tire_invoice_volume_credit (p) | tires, hazard |
| brake | brake_makegood_line_method (m: shop supplies back for both axles / 10.00 courtesy for one / none), volume (p), tenure (p), standing (p) | none declared (O-10 unchanged) |
| late | seasoned_account_tiering (m), utilization (p), closing remittances (p), volume (p), remittance_record_rate_adjust (p, new) | none |
- All within 4–6, ≥2 p, ≥1 m; three disjoint tiers each, distinct outcomes, fall-through = baseline, every tier stated in the rule. Labels honest (method tiers change where the amount comes from). Independence: no tier reads another factor's binding or output; no result assembled inside a factor binding.
- F-2 re-check: the corrections now restore exactly what fleet_evt_invoice gives the ticket, and the make-good adds a non-negative service-recovery credit. Real fleet desks do give billing-error make-goods (fees credited back, a fixed courtesy, larger for repeat errors and for long-standing, high-volume, clean-paying accounts). **F-2 closed; O-11 closed** (points removed).
- Realism observations: R2-O2 the tire make-good's road hazard program credit scales a tire billing make-good by certificate activations (customer-value weighting, unusual link); R2-O5 late `remittance_record_rate_adjust` counts remittance *applications* (one ACH paying four invoices counts four) — a payment-history depth proxy, plausible; O-12, O-13 unchanged; O-14 closed (credit now named for "roadside allowances granted on the business's road hazard certificates").

### findings (round 2)
- F-1 closed; F-2 closed. Open observations only: O-5, O-9, O-10, O-12, O-13, R2-O1…R2-O5. No new RED found pre-reveal.

### closing_checklist (round 2)
- Files 0.md, 1.md, _difficulty.md carry round 1 untouched and revision_2 appended; both comparison sections PASS.
- Scopes: task 0 {overlimit, early_pay}, task 1 {tire, brake, trip, late} — disjoint, jointly complete; tool uuid8s unchanged and independent.
- Trees: task 0 n=1 (1 value_input, 1 user write), task 1 n=3 (3 value_input, 1 user write); graph acyclic.
- Factors: every computation 4–6 factors with ≥2 p and ≥1 m, ladders stated in full, outcomes distinct and real; every factor bears weight against an honest baseline whose fall-back differs from gold (214.41, 9.64, 85.79, 107.99, 0.00, 32.80); multi-source and cross-difficulty (tires, hazard) present per task.
- Gates: snapshot_r2 shows all d_gates green on the final form; validate_scenario / check_traceability pending render only (out of scope).
- Open items: none RED. Observations O-5, O-9, O-10, O-12, O-13, R2-O1…R2-O5 recorded, no scored value moved.

## revision_3
- Gate: worklog tail "REWORK round 3: gates 7/7 green"; snapshot_r3 built via coordinator script — all d_gates green, check_traceability OK, validate_scenario errors only pre-render. extended.yaml a96c1a6f…c3111f, task_tools.py 96262107…801e09 (both changed → charter-global checks re-run): base copy byte-identical; every compute_basis quote, baseline sentence, overwrite clause/replaced_by and prerequisite source verbatim; all bindings exist; no factor id ⊂ tool name; uuid8s unchanged; tool bodies judge nothing; graph and state-form edges unchanged and acyclic.
- Renderer notes (render_source/fleet/notes.md): 1 closed (early-pay no longer restates the retired clause); 2 closed ("every other invoice remains under the base rule"); 3 closed (channel tiers exhaustive, = compute); 4 closed (trip excludes every visit-fee invoice in rule and compute); 5 closed (early-pay uses rotations; trip uses same-day tire invoices — no booking counts remain); 6 closed (late-charge windows count from the day the charge is assessed).
- KB-audit source items: N1 closed for early-pay, trip (replaced_by and docstring), tire and brake; over-limit replaced_by still names "work that a driver may authorize alone in an emergency" (softened; observation R3-O2, no scored effect). N2 base-layer, left as instructed. N3 closed (= renderer note 6).
- Factor structure: early-pay `tire_care_rotation_points` (p, tires) replaces bookings; trip `visit_tire_work_credit` (p, fleet ledger) replaces bookings — trip loses its cross-difficulty factor, task 1 keeps tires + hazard via tire policy. Counts still 4–6 per computation with ≥2 p, ≥1 m; ladders 3 tiers, distinct, in rule; no factor reads another factor's binding (R3-O1: trip served count and tire credit share input rows).
- Prior REDs F-1, F-2 remain closed; no new RED; nothing regressed (all gold figures unchanged and re-derived blind).
- Open observations: O-5, O-10, O-12, O-13, R2-O1…R2-O5, R3-O1, R3-O2, N2 (base).
VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4
- Gate: worklog tail "REWORK round 4: gates 7/7 green"; snapshot_r4 green (traceability OK). Only extended.yaml changed (81713931…5ac4fc); charter-global mechanical checks re-run: base copy identical, every compute_basis quote / baseline sentence / overwrite clause and replaced_by / prerequisite source verbatim, compute, factors and params unchanged, tools unchanged.
- Renderer round-2 note 1 (floor vs ceiling) closed: tire and brake rule + replaced_by now read "at least the restored discount … except that it never exceeds the invoice amount less the credit memos and early-pay discounts already on the invoice, that limit prevailing", matching `MN(room, restored + make-good)`. Class sweep: no other floor/ceiling pair in the charter can conflict (over-limit 0.00 floor vs invoice-amount cap is always consistent; trip fee has floors only; late charge has a minimum and no ceiling; early-pay has neither).
- Note 2 closed: early-pay baseline.rule is now a contiguous passage of the rule (prerequisite sentence moved after it, still verbatim).
- Note 3 / N2: base layer, unchanged by design.
- No new RED; nothing regressed. Open observations unchanged from revision_3.
VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN
