# Policy-task audit — service_contract_claims / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-22T03:16:27Z (file mtime; before any task GT reveal, which happened at 03:18:11Z), auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiator.
- Inputs and hashes (sha256, 16-char prefixes; they match the coordinator snapshot's 12-char prefixes): `vsc.extended.yaml` 91c274dc14063fd2, `task_tools.py` ea016c56831d3746, `tasks/0.json` 1f99a30856a52dfd, `tasks/1.json` b972dd1520ca1939. Masked views: `r1/0.view.json` 5569daa8decb66e4, `r1/1.view.json` 79617661a1f9563c.
- Entry conditions: the coordinator brief carried the gate snapshot (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; traceability deferred) and the masked-view hashes. Complete; gates not re-run by the auditor.
- Read: blueprint.yaml, db_schema.json, share_tools.py, products/{vsc,service,loaner,maintenance,warranty}.yaml (the parts relevant to this charter's reads), vsc.extended.yaml, task_tools.py, the two masked views, audits/render_source/XF_recipe.md.
- Masked / not read before freeze: tasks/*.json (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), plan.md, worklog.md, other difficulties' audits and tasks, every other env/ scenario.
- Scratch: /tmp/audit_service_contract_claims_0075/ (probe.py evaluates the charter's own compute through `check_compute.build_env/eval_compute` on the view seeds and on scratch decoy worlds; no gold input).

### policy_conflict_scan
Six extended policies, all `category: vsc`:

| policy | target_tool (owner) | computes | trigger | scope key |
| --- | --- | --- | --- | --- |
| vsc_ext_waiting_denial_reimbursement | reimburse_waiting_denial_repair_5808cf06 (agent) | amount | state_due | denied component_repair line, denial_reason waiting_period, contract with purchase_deal_id |
| vsc_ext_claim_rental_reimbursement | pay_claim_rental_line_3f5378a0 (agent) | amount | state_due | claim with paid component_repair line and a loaner agreement on its RO |
| vsc_ext_kept_vehicle_refund | accept_kept_vehicle_cancellation_d270783c (user) | refund_amount | on_request | submitted request, cancel_reason customer_request |
| vsc_ext_maintenance_denial_reimbursement | reimburse_maintenance_denial_repair_6315e699 (agent) | amount | state_due | denied engine/transmission/drive_axle line, denial_reason lack_of_maintenance, Kessler Care visit in look-back |
| vsc_ext_coverage_denial_reimbursement | reimburse_coverage_denial_repair_73971dca (agent) | amount | state_due | denied line, denial_reason component_not_covered, group switch true |
| vsc_ext_traded_vehicle_refund | accept_traded_vehicle_cancellation_f71aca80 (user) | refund_amount | on_request | submitted request, cancel_reason vehicle_sold_or_traded |

- Overlapping subjects: the three re-decision policies all write `vsc_claim_paid/component_repair`; their scopes are disjoint because a ledger line carries exactly one `denial_reason` (waiting_period / lack_of_maintenance / component_not_covered). Kept and traded refunds are disjoint by `cancel_reason`. Rental pays `claim_line_type rental` only. No two policies reach different conclusions on one line in one world.
- Base interplay: base `vsc_evt_claim_payment` "A claim is paid only on a contract in active status." (eligibility `active_contract_for_claim`) makes every claim write impossible after either refund policy cancels the contract; this agrees with the declared prerequisite direction (claims before cancellation).
- Time anchors: re-decision/rental lines are dated "today" (tool); refunds are effective on the request date (base + both refund rules). No conflict.
- Cross-category reads: service (RO lines, account tier), loaner (agreement, program params, charges), maintenance (plan, ledger), purchase (deal fields). All read-only; share tools expose no write to another category (share_tools.py: every non-vsc tool is `rw="read"` except verify/transfer), so XF recipe 16 ("owed at once" writes by other products moving these reads mid-conversation) has no producible path in this scenario.
- Task scope partition (from the views' worlds, not from charter_scope): task 0's world triggers only waiting + rental + kept (one waiting_period denial, a loaner on that RO, a customer_request request; no lack_of_maintenance / component_not_covered denial). Task 1's world triggers only maintenance + coverage + traded (no waiting_period denial, no loaner agreement, a vehicle_sold_or_traded request). The two trees are disjoint and together cover all six extended policies.

### rule_compute_equivalence
Mechanical sweep (scratch script): every `compute_basis` quotation of all six policies is verbatim in that policy's `rule`; every compute binding has a basis; every `replaced_by` is verbatim in the rule; every `superseded_clause` is verbatim in the cited base rule; every `baseline.rule` is a sentence of the rule; every `policy_source` is verbatim in the blocked rule (XF 10 clean). Every `factors[].ladder` tier is a sentence of the rule and a branch of its `decides` binding, and every branch is a stated tier (all 30 ladders have 3 tiers).

Two-way findings (detail in `findings`):
- Rule promises not implemented (RED-C7): waiting rule "while the base rules on active status, the term, covered component groups and the aggregate claim limit still apply" — compute has no coverage-switch test (no eligibility entry carries it either); coverage rule "...the waiting period, maintenance proof and the aggregate claim limit still apply" — compute has no maintenance-proof test; base `vsc_evt_claim_payment` "Where prior_authorization_required is true, a repair begun before a claim number was issued is not paid" is inherited by all three re-decision policies and tested by no compute and no eligibility entry.
- Probe reads whose result departs from the rule on producible worlds (RED-C4), see findings.
- Rounding: every re-decision total "is then capped at ... and is rounded to the cent" = `RND(MN(MX(0, ...), limit_left), 2)`; supplies/hazwaste proportions are rounded per their sentences; refunds "rounded to the cent, less the cancellation fee, never below 0.00" = `RND(MX(0, RND(price*share,2) - fee),2)`; rental "rounded to the cent" = RND. Placement matches.
- Zero-division / None / negative lag: supplies and hazwaste divisions are guarded (`ro_labor_all <= labor_charged` branch catches 0/0); rental `MX(0, DAYS()+1)`; refunds `MX(0.0, ...)`; None reads fall to the stated fall-through. Clean.

### action_binding_and_uuids
- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above).
- uuid8s: 5808cf06, 3f5378a0, d270783c, 6315e699, 73971dca, f71aca80 — six distinct values, no shared prefix or arithmetic progression; no factor id is a substring of any tool name (XF 7 clean).
- Tool bodies perform the documented single write and validate nothing (no refusal, no error, no hint when a prerequisite is unresolved). Docstrings carry no example values and no composite args (XF 17 clean). Observation O1: the three reimbursement docstrings say "...paid the store for on customer pay after the contract had denied that claim line" — the word "after" describes record history (the seeded denial), not a tool's position in a sequence and names no other tool; no consequence.
- Trigger rule (XF 18): tools write vsc_claim_paid (triggers []) and vsc_contract_cancelled, whose base trigger `vsc:vsc_refund_calculated {entry_date: closed_date}` the accept tools book in the same call. Nothing lands in another category.

### prerequisite_graph
| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| rental | waiting | state_gate | vsc_ledger.claim_line_type | state | reimburse_waiting_denial_repair_5808cf06 |
| kept | waiting | value_input | redecided_count | state | reimburse_waiting_denial_repair_5808cf06 |
| kept | rental | state_gate | vsc_ledger.claim_line_type | state | pay_claim_rental_line_3f5378a0 |
| traded | maintenance | value_input | redecided_count | state | reimburse_maintenance_denial_repair_6315e699 |
| traded | coverage | state_gate | vsc_ledger.claim_line_type | state | reimburse_coverage_denial_repair_73971dca |

Waiting, maintenance and coverage carry `prerequisite: []`. Every `problem` is an extended policy id of this file; no self-edge; acyclic (waiting -> rental -> kept, waiting -> kept; maintenance -> traded, coverage -> traded). All forms are `state`, no `fallback_reason` needed. Each `policy_source` is verbatim in the blocked rule. `value_input` gates name bindings that exist (`redecided_count` in kept and traded compute) and the resolving write moves them (the paid component_repair line makes `COUNT(..., claim_number=denied_claim)` > 0). The three `state_gate` edges name a ledger column rather than an eligibility id (observation O2: the gate is carried by the rule sentence; no eligibility entry exists in the extended policies). No authoring-viewpoint wording in any prerequisite text. Conditions restate the sentences at the same strength.

### prerequisite_sentences
Four-point test, per edge:
1. rental <- waiting: "A rental line is booked only after the records carry a paid component-repair line under the same claim number." Connective "only after"; state = a paid component-repair ledger line on the claim; no tool / id / snake_case. Derivation: the claim's only component line is denied (waiting_period); the policy whose rule pays such a line back is the waiting re-decision policy -> its write. Observation O3: in other worlds the same state is produced by the maintenance or coverage re-decision write (the denial reason selects one per world), but only the waiting edge is declared.
2. kept <- waiting: "The refund on such a cancellation is fixed only after the records carry a paid component-repair line for every claim line the contract denied for the waiting period while it was sold on its vehicle's purchase deal." State form; one resolving write (waiting re-decision). Scope finding RED-C6 (the state is demanded for lines the waiting policy itself does not pay).
3. kept <- rental: "The refund on such a cancellation is not computed until every claim whose repair order supported a Kessler loaner, and whose component-repair line the contract has paid or has denied for the waiting period while it was sold on its vehicle's purchase deal, carries its paid rental line." State form; only the rental tool books rental lines. Scope finding RED-C6 (claims whose rental benefit is nil).
4. traded <- maintenance: "The refund on a traded-vehicle cancellation is not computed until the records carry a paid component-repair line for every engine, transmission or drive-axle line the contract denied for lack of maintenance although a visit redeemed on a Kessler Care plan for the vehicle was dated on or before that line's repair-order diagnosis and fewer than the coverage level's maintenance look-back months before it." State form; one resolving write. RED-C6 (declined repairs).
5. traded <- coverage: "The refund on a traded-vehicle cancellation is fixed only after every component-repair line the contract denied as not covered, for a component group its coverage level covers, carries a paid component-repair line under the same claim number." State form; one resolving write. RED-C6 (declined repairs; base gates).
The depended-on rules do not restate any of these sentences; no rule names another policy's tool or id; no rule states a cross-problem order that grounds no edge (the fee tiers of kept/traded read "the contract's latest denied claim line was later paid as a component-repair line" — a record test, not an order; see O3).

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry (findings only):
- vsc_evt_claim_payment, for waiting and maintenance: sentences 1–4 (active status, term, covered groups, prior authorization) followed/inherited; labor, parts, deductible, line-total and diagnosis sentences superseded and declared (5 overwrites each); the expiration-date counting sentence inherited. For coverage: labor, parts, diagnosis, line-total superseded (4 overwrites); the deductible sentence is NOT superseded and the coverage baseline restates it as "taken once for the visit ... not taken where ... another component-repair line ... already took it under a coverage level that takes its deductible once per visit" — equal to base for per_visit levels and for one line per group under per_repair; differs only for a second same-group line on one RO under per_repair (observation O7, no producible-world consequence demonstrated).
- vsc_agg_vehicle_and_limit: the remaining-limit cap is kept in every claim compute (`limit_left`).
- vsc_evt_waiting_period / vsc_evt_maintenance_proof / vsc_combo_factory_warranty: the re-decisions agree with them (a waiting-period denial on a contract sold on its deal, or a lack-of-maintenance denial with a qualifying plan visit, is wrong under base). A factory-warranty-covered failure cannot reach any re-decision scope because the service charter's coverage priority never bills such a line on customer pay.
- vsc_evt_claim_benefits (rental): the rental sentence superseded and declared; "paid only together with a covered component repair", "no deductible", "a benefit whose per-day amount or day limit is 0 is not part of the coverage level" kept.
- vsc_evt_cancellation_refund (kept, traded): request/effective-date, active-only, signed-request, free-look, unwound, total-loss-fee, floor and precedence sentences inherited; pro-rata and unused-share sentences superseded and declared (2 overwrites each).
- Overwrite hygiene (XF 13): every one of the 19 `replaced_by` sentences names its own scope ("For a ... line/refund, and only for such a ...") but none restates the still-in-force content for out-of-scope cases, and the sibling overwrites of one clause (3x labor/parts/diag/line-total, 2x deductible, 2x pro-rata/unused share) do not exclude each other by name -> RED-C5.

### factor_ladders
Counts (declared): waiting 6 (method: covered_labor_basis, visit_deductible_rule; parameter: 4); rental 4 (method: rental_window_start, rental_window_end; parameter: 2); kept 5 (method: elapsed_term_measure; parameter: 4); maintenance 6 (method: lube_labor_rule, lube_visit_deductible; parameter: 4); coverage 5 (method: cover_labor_rule; parameter: 4); traded 5 (method: trade_measure_day; parameter: 4). All `decides` are inputs (none is `result`); binding sets are pairwise disjoint; mechanical transitive scan: no factor binding reads another factor's binding (XF 1 clean); shared selections (covered_line, labor_charged, ro_labor_all, delivered_late, deal_delivery, certified, request_day) are plain bindings stated once (XF 2 clean); assembly lives in `result` only (XF 3 clean).

Multi-source factors (every non-fall-through tier a condition set over distinct records): free_courtesy_days (loaner agreement + program + service account), cancel_fee_standing (request + deal + ledger + plan), trade_measure_day (new deal + contract + request / plan ledger), trade_fee_rule (ledger denial + paid line / service account), rental_window_start/end (loaner + RO + ledger). Cross-difficulty reads: service (all re-decision factors, rental end, free days, trade fee), purchase (term_miles_start, elapsed_term_measure, trade_measure_day, trade_reading, trade_miles_start), maintenance (mileage_reading_tier, cancel_fee_standing).

All-pairs method-tier table (XF 5; distinguishing input per pair):

| factor | T1 vs T2 | T1 vs T3 | T2 vs T3 |
| --- | --- | --- | --- |
| covered_labor_basis / lube_labor_rule / cover_labor_rule | MN(amount of labor rows, std) vs MN(list_amount − comeback credit amount, std) | charged amount vs hours×min(rate,cap) | list−credit vs hours×min(rate,cap) |
| visit_deductible_rule / lube_visit_deductible | 0 vs deductible×COUNT(decided lines) | 0 vs deductible | ×COUNT vs once (equal when one line — see RED-C1) |
| rental_window_start | loaner out_date vs denial entry_date | out_date vs diagnosis line_date | denial date vs diagnosis date |
| rental_window_end | loaner return_date vs covered line's last labor date | return_date vs RO last labor date | covered-line last labor vs RO last labor |
| elapsed_term_measure | floor(d/30)·30 vs MONTHS()·30 | floor vs raw days | MONTHS·30 vs raw days |
| trade_measure_day | new deal contract_date vs plan refund entry_date | contract_date vs request_date | plan entry_date vs request_date |

T2 (some producible world where the factor alone moves the result, every other factor at baseline): holds for every factor. Min-of shapes: the labor lesser-of picks bind whenever the posted rate is at or below the cap; the refunds' min(time share, mileage share) lets each time-side factor (elapsed_term_measure, unusable_days_credit, trade_measure_day, trade_credit_days) move the result in worlds where the time share is the lesser, and each mileage-side factor (mileage_reading_tier, term_miles_start, trade_reading, trade_miles_start) where the mileage share is the lesser; both occur in producible worlds (in both task worlds the mileage share binds, yet every time-side factor still moves the result there — see the task files).

Ladder realism (XF 22) and label honesty — results:
- RED-C1: visit_deductible_rule / lube_visit_deductible tiers 2 and 3 take deductibles no per-visit or per-component-group contract takes (see findings).
- RED-C2: elapsed_term_measure conditions the elapsed-term counting method on who arranged the vehicle financing — a condition VSC refund computation does not weigh.
- RED-C3: six factors labelled `parameter` whose tier 2 is a proportional allocation formula (method shape).
- Realistic: covered/lube/cover labor and parts (reimburse what the holder actually paid, capped at the standard amount), diagnostic share (uncredited part), shop-supplies/hazwaste (the baseline "shop fees are not reimbursed" matches common VSC exclusions; reimbursing a share on a make-whole re-decision is defensible), rental window start/end and day amount, free courtesy days (mirrors loaner charter rule "free for courtesy_days_included days, plus rewards_bonus_courtesy_days ... Gold or Platinum ... active"), mileage reading (higher recorded odometer), term-miles start (pre-delivery miles), credited days (pre-delivery days), cancel fee tiers (goodwill waiver / loyalty fee), trade measuring day and appraisal reading (refund as of the trade). Observations: O4 (rental free days subtracted as a count, not by overlap), O5 (rental starts on the denial day — read as the claim decision date), O6 (hazwaste reimbursed by system for waiting/coverage but for any repair for maintenance), O10 (standalone contracts credited the waiting-period days; home-delivery start adds the distance even when delivery precedes the sale).

Near-duplicate repricing sentences (coordinator question): the labor/parts/diagnostic/deductible/shop-fee sentences of the waiting, maintenance and coverage policies are distinct rules: each is scoped by a self-naming phrase keyed to a recorded `denial_reason` ("For a waiting-period re-decision line", "For a maintenance re-decision line", "For a coverage re-decision line", each "and only for such a line"), lives in its own policy's rule, and differs materially where it matters — the deductible is a factor (tiers 0 / ×decided lines / once) in waiting and maintenance but a baseline clause with a per-visit "already took it" exception in coverage; hazwaste is system-conditioned in waiting and coverage and unconditioned in maintenance; the diagnostic tiers are ordered differently. They are KB-locatable through the denial reason on the denied line. The one substantive defect the duplication exposes is that waiting and maintenance lack coverage's per-visit exception (RED-C1).

### findings
(Charter-global; each names the tasks it bears on. "Demonstrated" figures come from the charter's own compute on scratch decoy worlds, /tmp/audit_service_contract_claims_0075/scripts/decoys.py.)

**RED-C1 — SOURCE-FACTOR (unreal ladder), XF 22/A5.** Policies vsc_ext_waiting_denial_reimbursement (factor visit_deductible_rule) and vsc_ext_maintenance_denial_reimbursement (lube_visit_deductible). Symptom: tier 2 "where the coverage level takes its deductible per component group, the deductible chosen at sale is taken once for each component-repair line the contract decided on that repair order" (`deductible_chosen * lines_decided`, `lines_decided = COUNT('vsc_ledger', repair_order_number=ro, claim_line_type='component_repair')`, paid and denied lines of every group) and tier 3 "otherwise the deductible chosen at sale is taken once". Root cause: the tiers ignore deductibles other lines of the visit already took. Consequence: Kessler Shield Powertrain (per_repair, deductible 100), RO with a paid engine line (deductible 100 already taken) and a waiting-denied transmission line -> tier 2 takes 200 on the transmission repayment where the base per_repair rule ("once per component group repaired") takes 100; Kessler Shield Select at a non-selling store (per_visit, 100), RO with a paid electrical line that took the deductible and a waiting-denied AC line -> tier 3 takes a second 100 on one visit where base per_visit takes 0 (the coverage sibling's own baseline excludes exactly this case). With a single decided line tier 2 equals tier 3 (same value), so tier 2 is either a duplicate of the fall-through or a treatment no administrator publishes. Bears on: task 0 and task 1 structurally (both worlds sit on tier 1; the method floor of both policies survives through the labor factor, so no scored consequence).

**RED-C2 — SOURCE-FACTOR (unreal ladder condition), XF 22.** vsc_ext_kept_vehicle_refund factor elapsed_term_measure: "where it was financed on an installment contract the store arranged, in whole 30-day periods completed, a part period not counted; where it was financed through a lender the holder arranged, in whole calendar months completed, each counted as 30 days; otherwise as counted." The condition (who arranged the vehicle loan) is not something a VSC administrator weighs when measuring elapsed term: the contract form fixes days or months for every holder, and financing changes only the payee (already handled by base `refund_to_lienholder_when_financed`). Tiers 1 and 2 are two near-identical month approximations told apart only by that condition. It is the kept computation's only `method` factor, so striking it leaves kept with 0 method factors — the consequence is demonstrated in `0.md` (task 0). Bears on: task 0.

**RED-C3 — SOURCE-FACTOR (mislabelled effect), XF 5.** shop_supplies_share, hazwaste_fee_share, lube_supplies_share, lube_waste_share, cover_supplies_share, cover_waste_share are labelled `parameter`, yet their tier 2 is a proportional allocation "the fee times the covered concern line's labor charge over all customer-pay labor charged, rounded to the cent" (`RND(fee * labor_charged / ro_labor_all, 2)`) — added inputs and operations, i.e. the formula's shape changes. Re-labelling them `method` leaves each policy's floors intact (waiting/maintenance/coverage keep covered/lube/cover parts and diagnostic as 2 parameters), so no count consequence; the labels are dishonest. Borderline, recorded as observation O8: the "list amount less that credit" / "uncredited part" tiers of the parts and diagnostic factors and the "odometer at sale plus the deal's one-way delivery distance" tier of term_miles_start/trade_miles_start are net-value reads with a subtraction/addition. Bears on: tasks 0 and 1 (labels only).

**RED-C4 — SOURCE-POLICY (rule != compute on decoy/second-record reads), XF 9/12.** Members:
1. Waiting / maintenance / coverage select the line by `LATEST(... denial_reason=...)` and test `already_repaid` on that claim only. Two waiting-period denials, the newer already repaid, the older not: rule says the older is a re-decision line and is paid; compute returns 0.00 (probe P1).
2. Maintenance `visit_day = XLATEST(... maintenance_visit_redeemed)` takes the plan's latest visit overall; the rule is existential ("a visit ... dated on or before the diagnosis date ... and fewer than the ... look-back months before it"). Adding a visit after the failure (2026-09-10) to task 1's world: compute `visit_proof` 0, result 0.00; rule 6783.37 (probe P2). The same read (and kept's `visit_reading`) counts a redeemed visit later reversed by `maintenance_visit_reinstated`, which the maintenance charter's own measure excludes ("latest maintenance_visit_redeemed entry that has not been reinstated"). The same existential sentence is traded's prerequisite sentence 4.
3. `CFIELD('maintenance','maintenance_plan_id', vehicle_id=...)` (kept reading, maintenance proof, traded measuring day) is first-match: a fulfilled/expired older plan on the vehicle listed first makes compute ignore the current plan's visits (probe P4: kept reading falls to the certified odometer).
4. Traded `CFIELD('purchase', ..., variant_name='New Vehicle Retail Purchase')` is first-match, unfiltered by status, excludes New Vehicle Factory Order Purchase although the rule says "new-vehicle purchase deal", and no record ties the appraisal to the covered vehicle. A cancelled NVRP deal with an appraisal listed first moves the measuring day to its contract date: 2019.00 vs the rule's 2035.27 on task 1's world (probe P5); a trade of a different vehicle feeds its appraisal odometer into this contract's mileage share.
5. Covered concern line = `XLATEST(line_letter, event_type='service_diagnostic_fee_charged')`; the service charter charges "one diagnostic fee ... per concern line", so an RO with two diagnosed concerns has no unique "concern line ... that carries the repair order's diagnostic fee". Task 0's RO with line B also diagnosed: compute picks B and pays 434.47 instead of 1667.15 (probe P6).
6. `CFIELD('loaner', ..., repair_order_number=ro)` / `CPARAM` are first-match: two sequential agreements on one RO (allowed — "at most one courtesy or warranty loaner at a time") take dates/program from whichever is listed first.
7. Kept/traded RO reading `XLATEST(odometer_in, date_field='line_date', vehicle_id=...)` is the odometer of the RO with the latest-dated row of any type, not of "the latest repair order a group store wrote": a credit/payment posted on an older RO after a newer RO opened selects the older odometer.
8. Tie and month-end conventions unstated: "the contract's latest denied claim line" (kept/traded fee tier 1) has no same-day tie rule though several lines of one claim are routinely denied the same day; "whole calendar months completed" (kept tier 2) and "fewer than ... months, counted in whole calendar months" (maintenance scope, traded sentence 4) use MONTHS() (day-of-month comparison), which contradicts the charter's own stated month-end convention ("a month without that day ends on its last day", base vsc_evt_sale): 2026-01-31 -> 2026-02-28 is one completed month by that convention, 0 by MONTHS().
Bears on: neither task world (single deal, single plan, single diagnosed concern per RO, single denial per reason, no ties), so no scored consequence in tasks 0/1.

**RED-C5 — SOURCE-POLICY (overwrite hygiene), XF 13.** All 19 overwrites (waiting 5, maintenance 5, coverage 4, rental 1, kept 2, traded 2) replace a base sentence with a self-scoped `replaced_by` but restate nothing for out-of-scope cases, and the sibling overwrites of one base clause do not exclude each other by name. Consequence: the merged semantics for an out-of-scope case is not unique — e.g. a rental at an outside agency on an ordinary covered claim: base "Rental is reimbursed at rental_per_day_usd per calendar day ... from the day the repair order is opened to the day the repair is completed" is superseded and the only replacement covers "a rental line this policy pays" (a Kessler loaner), so one reading pays rental_per_day × days open-to-complete and the other finds no rental rule; likewise an ordinary claim line's labor ("Labor is paid at the allowed hours times labor_rate_paid ...") and a total-loss or unwound-deal cancellation's pro-rata clause. Bears on: no task world directly; affects the KB the tasks' solvers read.

**RED-C6 — SOURCE-POLICY (prerequisite wait broader than its resolver).** The four refund prerequisite sentences demand states that the depended-on policy does not produce in producible worlds, so the root can never be computed (or only by booking a 0.00 paid claim line, which XF 19 forbids):
1. kept <- rental: a claim with a Kessler loaner on a Kessler Shield Powertrain contract (rental_per_day_usd 0.0 — "has no rental benefit"), or one whose free courtesy days cover the window. Task 0's world with the loaner returned 2026-09-11: rental compute = 0.00 (probe P9), yet "not computed until every claim ... carries its paid rental line".
2. kept <- waiting: a waiting-period denial on a contract sold on its deal where the holder declined the repair (no customer-pay repair -> not a "waiting-period re-decision line"), yet "fixed only after the records carry a paid component-repair line for every claim line the contract denied for the waiting period".
3. traded <- maintenance and traded <- coverage: the same with a declined repair, and (coverage) a not-covered denial on a covered group that base gates (term, waiting period, maintenance proof) still deny.
Bears on: neither task world (in both, every waited-on line is payable and pays > 0).

**RED-C7 — SOURCE-POLICY (rule promise not in compute), XF 8.** (a) Waiting rule "the base rules on ... covered component groups ... still apply": a Kessler Shield Powertrain contract (covers_air_conditioning false) with an AC line denied for the waiting period and paid on customer pay -> rule: not covered, nothing repaid; compute: full repayment. (b) Coverage rule "... maintenance proof ... still apply": an engine line denied as not covered where no qualifying service exists in the look-back -> base lack-of-maintenance denial stands; compute repays. (c) Base "Where prior_authorization_required is true, a repair begun before a claim number was issued is not paid" is inherited by all three re-decision policies (not superseded) and implemented by no compute and no eligibility entry. Bears on: neither task world (AC and cooling are covered by Kessler Shield Exclusionary; the repairs began after the claim numbers were issued).

Observations (not grounds for rework): O1–O8, O10 above; O11 the reimbursement tools record `deductible_applied 0.0` on lines whose total already netted a deductible, so coverage's "already took it" record test cannot see a deductible taken inside a re-decision total.

## closing_checklist
Written after both reveals (2026-10-22T03:18:11Z); the charter-global section above was frozen before them and is unchanged except for the freeze-timestamp line.
- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; this is revision_1 (no older revision).
- Comparisons: task 0 matches GT on every write, argument, order, tree edge and factor figure, but carries SOURCE-FACTOR RED F0-1 (kept computation left with no method factor by RED-C2) and SOURCE-POLICY RED F0-2 (stale scope text in design_rationale). Task 1 matches GT item by item and carries no per-task RED.
- Coverage: the six extended policies are fully covered; task scopes (task 0: waiting, rental, kept; task 1: coverage, maintenance, traded) are pairwise disjoint and jointly complete; six task tools, each with its own independently frozen uuid8.
- Trees: each task has 2 prerequisite problems, 1 value_input edge (= max(n−1,1)), a user-owned root write, no cycle; the difficulty graph is a DAG.
- Factors: every declared factor bears weight on its task's world against the stated baseline, and every all-baseline figure is definite and differs from gold; the open defects are structural (RED-C1, RED-C2, RED-C3) and, for task 0, the method floor (F0-1).
- Gates not re-run by this audit (snapshot in the brief, hashes unchanged at audit time).
- Difficulty NOT closed: charter REDs RED-C1 … RED-C7 and task-0 REDs F0-1, F0-2 are open.

Charter RED ids: RED-C1 (deductible tiers 2–3 unreal, waiting + maintenance), RED-C2 (elapsed_term_measure financing condition unreal, kept), RED-C3 (proportional supplies/hazwaste shares labelled parameter, 6 factors), RED-C4 (decoy / second-record / tie / month-end reads, 8 members), RED-C5 (19 overwrites lack out-of-scope restatement and sibling exclusion), RED-C6 (refund prerequisite waits broader than the resolving policies), RED-C7 (rule promises — covered groups, maintenance proof, prior authorization — absent from compute).

VERDICT revision_1: task0=RED task1=PASS charter=RED-C1,RED-C2,RED-C3,RED-C4,RED-C5,RED-C6,RED-C7

## revision_2

## charter_global_frozen (revision_2)
- Frozen 2026-10-22T05:28:41Z (file write time), before either task's revision-2 GT was opened. Auditor: same independent auditor as revision_1.
- Entry gate: last line of tasks/service_contract_claims/worklog.md = `REWORK round 2: gates 7/7 green`. Snapshot run by the auditor: `/tmp/erl0075_coord/snapshot.sh service_contract_claims 2` (2026-10-22T05:23:56) => EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 vsc.extended.yaml 8d4d0c552534, task_tools.py 3fa9c534c04c, tasks/0.json 94148e166bc2, tasks/1.json 4c0ee9bf3f02. Views r2/0.view.json 5569daa8decb66e4 and r2/1.view.json 79617661a1f9563c — byte-identical to r1 (seeds unchanged).
- Both shared inputs changed (vsc.extended.yaml 91c274dc1406 -> 8d4d0c552534, task_tools.py ea016c56831d -> 3fa9c534c04c), so every charter-global section is re-derived below; nothing is carried forward by reference.
- Mechanical re-sweep: every compute_basis quote verbatim in its rule; every binding has a basis; replaced_by/baseline/policy_source verbatim in the rule; superseded clauses verbatim in base; base policies and variants identical to blueprint/products/vsc.yaml; no factor binding reads another factor's binding; no factor id inside a tool name. Clean.
- Recomputation of both task worlds under the new compute (scripts t0.py, t1.py): every scored value, every factor-substitution figure and every all-baseline figure is unchanged from revision_1.

### revision_2 — closure of revision_1 REDs (verified against the artifacts)
- **RED-C1 closed.** visit_deductible_rule / lube_visit_deductible now read: none at the selling store under the disappearing deductible; "where that is not so and the coverage level takes its deductible once per repair visit, the deductible chosen at sale less the contract deductibles the store already billed the holder on that repair order, never below zero" (`MX(0, deductible_chosen − XSUM(... pay_type='service_contract_deductible'))`); otherwise once (per component group: this line's own group). Each tier is a treatment the base per_visit / per_repair rules give; T2 has an added input (billed deductibles), so the method label holds.
- **RED-C2 closed.** elapsed_term_measure is now keyed on the contract form: Exclusionary / Exclusionary Wrap — whole 30-day periods completed; Preferred / Select — 30-day periods with a started period counted whole; otherwise raw days. Counting elapsed time by contract form is a contract term administrators do publish; floor vs ceiling vs raw days are three distinct shapes.
- **RED-C3 closed.** The six supplies/hazardous-waste factors are now labelled `method`. Floors: waiting and maintenance 4 method / 2 parameter, coverage 3 method / 2 parameter.
- **RED-C4 mostly closed.** (1) re-decision scopes are now "the contract's latest component repair line denied for …" with a stated same-day tie rule (first in the claim history = LATEST's first-row behaviour); (2) the maintenance scope now names "the latest visit redeemed on the vehicle's Kessler Care plan in active status [that] has not been reinstated", matching `XLATEST` + `visit_reinstated == 0`; (3) plan reads filtered `status='active'` (the maintenance charter allows one active plan per vehicle); (4) traded deal reads filtered `variant_name='New Vehicle Retail Purchase', status='closed'` with a stated first-listed convention, and the rule names that deal type; (5) "a diagnostic fee on exactly one concern line" is now a scope condition (`diag_lines == 1`); (6) the loaner convention "the first one the loaner records list" is stated; (7) the repair-order reading is now "the one whose labor was closed last" over labor rows; (8) denial tie rules stated; the maintenance month count now states MONTHS()'s convention in words. Residual members: see RED-C4r.
- **RED-C5 mostly closed.** 18 of the 19 replaced_by sentences now name their siblings and restate the base content for every other line/refund. Residual: see RED-C5r (rental).
- **RED-C6 partly closed.** Each refund prerequisite sentence now restates its resolver's scope (latest line, group/switch, term, waiting period, single diagnosed concern, customer-pay labor closed on or after the decision), so the declined-repair and base-gate deadlocks are gone. Residual: see RED-C6r.
- **RED-C7 closed.** The waiting scope requires a non-lubricated group with its switch true (no maintenance proof needed); the coverage scope excludes lubricated groups and requires the waiting period over or waived; the term and prior authorization are scope record tests in all three ("labor … closed on or after the day the contract decided the line, which the records take as the repair not having begun before the claim number was issued"); the compute implements each (`group_switch_on`, `lube_group`, `waiting_over`, `in_term`, `begun_after_claim`).
- Tool bodies (coordinator check): all six now validate their docstring formats — amounts `> 0` for claim lines and `>= 0` for refunds, rental `days >= 1`, odometer integer `>= 0`, component_group and cancel_method against their enumerations (docstrings now mark `not_applicable` as not accepted), effective_date `YYYY-MM-DD`; money is rounded half-up to the cent (`_Fmt.cents`), as the docstrings now state. Invalid input returns an `Error:` string and writes nothing. The checks are format checks; no body reads a prerequisite. O1 ("after the contract had denied") remains in three docstrings, no consequence.

### revision_2 — remaining charter REDs (all members, one pass)
**RED-C6r — SOURCE-POLICY (prerequisite wait the resolver cannot satisfy).**
1. kept <- waiting, traded <- maintenance, traded <- coverage: when the in-scope line's repayment works out to 0.00, no paid line can be booked, so the wait never clears. The re-decision computes are `RND(MN(MX(0, … − deductible_taken), limit_left), 2)` and the tools now refuse `amount <= 0`. Probe R1 (task 0's world with the RO written at a non-selling store and a small line-A repair, labor 67.05 + parts 19.00, deductible 100): waiting result 0.00; `reimburse_waiting_denial_repair_5808cf06(..., amount=0.0)` returns "Error: amount must be a USD figure above 0.00 …"; yet kept says the refund "is fixed only after the records carry a paid component-repair line under the claim number of the contract's latest component repair line denied for the waiting period …". A contract at its aggregate limit (`limit_left` 0) gives the same deadlock, and so does a rental line whose result is capped to 0.00 by the limit (kept <- rental).
2. kept <- rental, scope mismatch. Kept waits on a rental line "wherever that claim's repair order supported a Kessler loaner on which the holder was charged daily rental". The rental policy prices only "the first one the loaner records list" and only "the claim of the contract's latest paid component-repair line". Probe R2: RO 446215 with an uncharged Same-Day Courtesy agreement listed first and the charged Compact agreement second — kept waits (a charged Kessler loaner supported the RO), rental compute reads the first agreement (charged_rental_days 0) and gives 0.00 -> deadlock. Likewise, if the waiting claim was repaid in an earlier conversation and a later ordinary claim was paid since, kept waits on a rental line for the waiting claim, which is not the latest paid claim and so is outside the rental policy.

**RED-C5r — SOURCE-POLICY (out-of-scope restatement incomplete, XF 13).** The rental replaced_by restates base only for "every other rental, on a loaner the holder was not charged for or a rental from outside the group". A Kessler loaner on which the holder was charged daily rental, but on a claim that is not the contract's latest paid component-repair claim or under an agreement that is not the first listed, is in neither bucket. The superseded base sentence is the only other rental rule, so the merged charter gives such a rental no rule, or two.

**RED-C4r — SOURCE-POLICY / realism (decoy reads still open, XF 9/22).**
1. Traded trade_measure_day tier 1 and trade_reading tier 1 still do not tie the New Vehicle Retail Purchase deal's trade-in to the covered vehicle; purchase_deals has no field naming the trade-in vehicle. Producible: a holder trades a second vehicle at a group store and sells the covered one privately — the policy measures this contract's term to that deal's date and its mileage at the other vehicle's appraisal odometer. No administrator publishes that treatment.
2. Traded tier 2 `CFIELD('maintenance','maintenance_plan_id', vehicle_id=…, status='cancelled')` is first-match among cancelled plans. An earlier plan cancelled at the holder's own request, listed first, hides a later plan cancelled for the vehicle being sold or traded, which the rule ("the vehicle's Kessler Care plan in cancelled status carries a refund calculated on a cancellation for the vehicle being sold or traded") would use. Only reachable when tier 1 does not apply.
3. Kept and traded "the latest repair order a group store wrote for the vehicle (the one whose labor was closed last)" states no tie rule. Two repair orders whose last labor rows fall on the same day take the first-listed row's odometer_in (XF 9: state the tie rule).
None of RED-C4r, C5r or C6r has a consequence on either task world (single re-decision line per reason with a positive repayment, a single charged loaner agreement on the waiting claim's RO, one closed trade deal whose appraisal is the Pilot's, one plan, one RO per date).

### revision_2 — observations
- O12 (kept reading, wording): "the latest visit redeemed on the vehicle's Kessler Care plan in active status, where it has not been reinstated" — compute reads it as "the latest visit, if not reinstated" (falls to the certified odometer otherwise). The ladder's "the latest visit …, not reinstated" also admits "the latest non-reinstated visit", which is the maintenance charter's own measure. Two readings differ only when the latest visit was reinstated and an earlier one sits above the certified odometer.
- O13 (scope realism): the maintenance re-decision now requires the plan's latest visit to precede the diagnosis, so a holder who kept up plan visits after the repair falls out of scope; the waiting re-decision now excludes lubricated groups. Both are coarse exact scope tests (XF 12), stated as record tests, with no producible contradiction.
- O14: the rental "never below one day where the holder was charged daily rental" floor pays one day even when the charged days fall outside the covered window; defensible because the holder paid for loaner days on that RO.
- Observations O1–O11 of revision_1 otherwise unchanged (O7/O11 coverage deductible test).

## closing_checklist (revision_2)
Written after both revision-2 reveals (2026-10-22T05:29:10Z).
- Gold is unchanged in both tasks and matches the frozen re-derivations item by item (writes, arguments, order, tree, every factor and baseline figure).
- Closed: RED-C1, RED-C2, RED-C3, RED-C7; task-0 F0-1, F0-2. Mostly closed with residual members: RED-C4 -> RED-C4r (3), RED-C5 -> RED-C5r (1), RED-C6 -> RED-C6r (2).
- New in revision_2: tasks/0.json F0-3 and tasks/1.json F1-1 (stale `lines_decided` trace lines; ROUND 2 rationale claims "satisfiable in every world" (task 0) and "every overwrite … restates base for every other case" (both)).
- Trees: both still have 2 prerequisite problems, 1 value_input edge, a user-owned root, and are acyclic. Factor floors met in every computation with no factor struck: waiting 4M/2P, rental 2M/2P, kept 1M/4P, maintenance 4M/2P, coverage 3M/2P, traded 1M/4P.
- Tool bodies enforce their docstring formats and rounding; no prerequisite is judged by a tool.
- Difficulty NOT closed.

VERDICT revision_2: task0=RED task1=RED charter=RED-C4r,RED-C5r,RED-C6r

## revision_3

## charter_global_frozen (revision_3)
- Written before either task's revision-3 GT and before reading the worklog body. Entry gate: the last non-blank worklog line is `REWORK round 3: gates 7/7 green`. Snapshot run by the auditor: `/tmp/erl0075_coord/snapshot.sh service_contract_claims 3` (2026-10-22T06:03:04) => EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 vsc.extended.yaml 1b0ba1315cca, task_tools.py 3fa9c534c04c (unchanged since revision_2), tasks/0.json 467208a200f4, tasks/1.json 5ea776377948. Views: r3/0.view.json 5569daa8decb66e4 (identical to r1/r2); r3/1.view.json 54148bdbd5d1c690 (changed — see task 1).
- The charter changed, so the charter-global sections are re-derived; the tool module is unchanged and its revision_2 conclusions carry forward on hash 3fa9c534c04c (format checks, half-up cents, no prerequisite judged). Mechanical re-sweep clean (quotes, bases, overwrites, baselines, prerequisite sources, factor independence, ids vs tool names, base copy identical to blueprint). Factor labels and counts are unchanged from revision_2. A copy of this charter is saved at /tmp/audit_service_contract_claims_0075/r3/ for the next diff.

### revision_3 — revision_2 REDs, verified against the artifacts
- **RED-C4r closed.** (1) The traded measuring day and first reading tier no longer read a new-vehicle deal. They read "the Kessler Care plan sold on the contract's purchase deal"'s refund calculated on a sold-or-traded cancellation (its date / its odometer), then "the GAP waiver sold on the contract's purchase deal"'s loan payoff date. Both records are tied to the covered vehicle through the contract's own deal (`CFIELD(..., purchase_deal_id=F('purchase_deal_id'))`), and the latest/tie conventions are stated. (2) The first-match among cancelled plans is gone (plan keyed by deal). (3) The repair-order tie rule is stated: "where two closed labor on the same day, the one listed first in the service records".
- **RED-C5r closed.** The rental replaced_by now restates base for "every rental this policy does not price — on any other claim, under a loaner agreement other than the first one listed for the repair order, on a loaner the holder was not charged for, or from outside the group".
- **RED-C6r items 1–2 closed as stated.** Every refund wait now also requires "no deductible falls on that line" and "claims paid less reversals … below the coverage level's aggregate claim limit". Re-decision scopes now require customer-pay labor "not wholly credited back as a comeback repair". Under those conditions the repayment is a positive amount the tools accept. Kept's rental wait now names exactly the rental scope (the claim of the latest component-repair line, paid or denied; the first agreement listed; charged daily rental; rental benefit > 0; below the limit). Probe R1 is no longer under a wait, and probe R2's world no longer engages the wait.
- Realism of the new traded tiers: a Kessler Care cancellation for the vehicle being sold or traded, and a GAP loan payoff, are records administrators accept as evidence of when the vehicle left the holder. The maintenance scope's narrowing to "the Kessler Care plan sold on the contract's purchase deal" is a coarse record-keyed scope (observation O15).

### revision_3 — remaining / new charter REDs (all members, one pass)
**RED-C6r2 — SOURCE-POLICY / SOURCE-CHAIN (value dependency left unordered by the narrowed waits; regression introduced by the RED-C6r fix).** The fee tiers of both refunds read whether "the contract's latest denied claim line … was later paid as a component-repair line on the same claim number". Every re-decision is state_due and payable only while the contract is active ("the base rules on active status … still apply"). Narrowing the waits to deductible-free lines leaves every line on which a deductible falls — the ordinary case off the selling store, or where the holder chose a deductible above 0 at a non-disappearing level — with no stated order against the refund. Two terminal states are then equally defensible. Probe (decoys_r3.py): task 0's world with RO 446215 written at another group store (KHB) — the waiting repayment is 1567.15 (deductible 100). Kept's waiting wait is not engaged ("no deductible falls on that line" is false), and so neither is the rental wait. Order A, repay then cancel: 1567.15 paid and refund 3780.75 (fee 0.00). Order B, cancel first: refund 3755.75 (Kessler Care holder fee 25.00), and the repayment is no longer payable on a cancelled contract. Members:
  (a) kept <- waiting (fee tier 1);
  (b) kept <- rental (the rental wait is gated on the waiting wait's line);
  (c) traded <- maintenance (trade_fee_rule tier 1);
  (d) traded <- coverage, where the not-covered line is the contract's latest denied line (trade_fee_rule tier 1).
**RED-C9 — SOURCE-POLICY (rule != compute rounding; new in revision_3).** Every rule now says "rounded half up to the cent"; the compute implements this as `RND(x + 0.000001, 2)`. That is correct at exact ties, but rounds up any value lying within 0.000001 below a half cent. The proportional fee shares can land there with producible inputs. Gold tier (6% shop supplies, cap 39.95): covered-line labor 468.42 of 852.74 customer-pay labor, fee 39.95 -> exact share 21.944999648…; half up = 21.94; compute 21.95. Shop supplies at 8% capped 49.95, labor 2333.43 of 2535.73 -> exact 45.964999625…, rule 45.96, compute 45.97. Hazardous waste 4.95, labor 1311.70 of 2064.52 -> exact 3.144999806…, rule 3.14, compute 3.15. Members — the tier-2 sites `supplies_reimbursed` / `hazwaste_reimbursed` (waiting), `supplies_repaid` / `waste_repaid` (maintenance, coverage): 6 sites. The other nudged sites are safe: labor (whole-dollar rates × tenth-hours), refund shares (denominators ≤ 2557 days or term miles, so no value falls within 0.000001 of a half cent without being a tie), and sums of cents. Neither task world is affected (28.9689…, 3.6367…, 46.0786…, 4.5664…, 40.52/4.95 whole).

### revision_3 — observations
- O15: the maintenance scope and the kept/traded plan reads now key on "the Kessler Care plan sold on the contract's purchase deal", so a plan bought on its own, or on a later deal, no longer proves maintenance or supplies a reading. This is a coarse scope with no contradiction.
- O12–O14 unchanged.

## closing_checklist (revision_3)
Written after both revision-3 reveals (2026-10-22T06:07:19Z).
- Gold is unchanged in both tasks and matches the frozen re-derivations item by item, every factor and baseline figure included.
- Closed: RED-C4r, RED-C5r, RED-C6r (as stated); task F0-3, F1-1. No revision_2 PASS item regressed: trees, factor floors and labels, tool contracts (unchanged module) and every base copy are as before.
- Task 1's seed changed: the Kessler Care plan is cancelled for the trade with a 0.00 refund, a valid state under the maintenance charter.
- New: RED-C6r2 (the waits' deductible carve-out leaves owed, positive re-decisions unordered against the refund; 4 members); RED-C9 (the 0.000001 nudge misrounds non-tie values within 0.000001 below a half cent; 6 proportional fee-share sites); task proof-text REDs F0-4 and F1-2 (both rationales call a deductible-bearing line a 0.00 case).
- Trees: 2 prerequisite problems, 1 value_input edge, user root, acyclic, in both tasks. Factor floors met with no factor struck.
- Difficulty NOT closed.

VERDICT revision_3: task0=RED task1=RED charter=RED-C6r2,RED-C9

## revision_4

## charter_global_frozen (revision_4)
- Written before reading the worklog body and before either task's revision-4 GT. Gate: the last non-blank worklog line is `REWORK round 4: gates 7/7 green`. Snapshot run by the auditor: `/tmp/erl0075_coord/snapshot.sh service_contract_claims 4` (2026-10-22T07:08:10) => EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 vsc.extended.yaml 178b01937fa0, task_tools.py 3fa9c534c04c (unchanged), tasks/0.json e02cc0221aff, tasks/1.json c0f480c3ebaf. Views r4/0.view.json 5569daa8decb66e4 and r4/1.view.json 54148bdbd5d1c690, both byte-identical to r3.
- Diffed against the saved round-3 charter (/tmp/audit_service_contract_claims_0075/r3/). Base sections are identical. What changed:
  - every money RND nudge, 0.000001 -> 0.000000001;
  - the rental days floor "never below one day where the holder was charged daily rental" removed from the replaced_by and from `days_paid`;
  - the four refund wait sentences and their `prerequisite` conditions.
  Nothing else changed: no scope, ladder, factor, label or other compute binding. The mechanical sweep is clean. The tool module is unchanged, so its revision_2 conclusions carry forward on hash 3fa9c534c04c.
- Re-run on both views (t0.py, t1.py, RV=r4): every scored value, all 31 factor-substitution figures and all six all-baseline figures are unchanged.
- Coordinator ruling applied: a "half up" rule implemented as RND(x + 0.000000001, 2) is accepted; values within 1e-9 below a half cent are DSL-known residue, not RED. A floor that creates an amount the rule does not owe is RED.

### revision_4 — revision_3 REDs, verified against the artifacts
- **RED-C9 closed under the ruling.** All 21 nudged sites now use 1e-9. The misround window is ≤ 1e-9 (residue). An exact-tie check (200,000 half-cent values up to 50,000.00) gives 0 misrounds, so the rule "rounded half up to the cent" and the compute agree beyond 1e-9.
- **Rental floor (coordinator ruling).** Removed. `days_paid = MN(MX(0, days_counted − free_days), MX(0, max − days_already))`, and the rule no longer pays a day the window does not owe. Clean.
- **RED-C6r2 closed in substance.** The three re-decision waits now engage whenever "the deductible taken on that line is less than the amount the line repays before the deductible … and the contract's claims paid less reversals are below the … aggregate claim limit". That is exactly the set where the resolver pays above 0.00. The rental wait engages whenever "the rental days that claim's rental line pays (the window days, both counted, less the days the store gave free, within the rental days left on the claim) are above zero". Re-run of the round-3 counter-example (decoys_r3.py; task 0's world, RO at KHB, deductible 100): repayment 1567.15. The kept waiting wait is now engaged (100 < 1667.15 and limit far off), and so is the rental wait, so the only order is repay -> rental -> refund (3780.75). The two-terminal-state ambiguity is gone for all four members.

### revision_4 — remaining charter RED (all members, one pass)
**RED-C10 — SOURCE-POLICY (prerequisite sentences condition on the resolver's computation, XF 15: "never 'if policy X would compute …'").** The fix for RED-C6r2 makes each wait depend on the depended-on policy's computed figures rather than on a record-visible state. Each sentence can only be evaluated by running the other policy's ladders: covered-line labor/parts/diagnostic tiers, shop-fee shares, deductible ladder, rental window and free-day tiers. The structured conditions say so outright: "the deductible taken on the line is below the line's repayable amount before the deductible (its result is above 0.00)"; "the rental days payable on the claim (window days less free days, within the days left) are above zero". The check-6 state-form test fails too: what is waited on is not a state named in the words the tables use. Members:
  1. kept <- waiting: "… the deductible taken on that line is less than the amount the line repays before the deductible (its labor, parts and diagnostic fee repaid and its shares of the repair order's shop fees) …";
  2. kept <- rental: "… the rental days that claim's rental line pays (the window days, both counted, less the days the store gave free, within the rental days left on the claim) are above zero …";
  3. traded <- maintenance: same deductible-versus-repayment clause;
  4. traded <- coverage: same clause.
Consequence: the blocked rules restate the depended-on rules' computation. A reader must price the other problem to know whether the refund waits, which XF 15 excludes and which the KB renderer will carry as a cross-policy computation inside a prerequisite sentence. No scored value of either task moves: in both worlds every condition holds with a positive repayment.

### revision_4 — observations
O12–O15 unchanged. The aggregate-limit clause of each wait is a plain record test and is fine.

## closing_checklist (revision_4)
Written after both revision-4 reveals (2026-10-22T07:09:43Z).
- Gold is unchanged and matches the frozen re-derivations item by item in both tasks.
- Closed: RED-C6r2 (all four members), RED-C9 (under the coordinator's 1e-9 ruling), the rental floor, and task F0-4 / F1-2.
- No revision_3 PASS item regressed: trees, factor floors and labels, scopes, tool module (unchanged) and base copy are all as before.
- Remaining: RED-C10. Each wait's "the resolver pays above 0.00" carve-out is expressed through the resolver's own computation, an XF 15 member (4 sentences/conditions).
- Per-task relationships PASS on both worlds.
- Difficulty NOT closed while RED-C10 stands.

VERDICT revision_4: task0=PASS task1=PASS charter=RED-C10

## revision_5

## charter_global_frozen (revision_5)
- Written before reading the worklog body and before either task's revision-5 GT. Gate: the last non-blank worklog line is `REWORK round 5: gates 7/7 green`. Snapshot run by the auditor: `/tmp/erl0075_coord/snapshot.sh service_contract_claims 5` (2026-10-22T07:21:30) => EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 vsc.extended.yaml 38e8d29d26de, task_tools.py 3fa9c534c04c (unchanged), tasks/0.json 57017c903857, tasks/1.json f9415a067eaa. Views r5/0.view.json 5569daa8decb66e4 and r5/1.view.json 54148bdbd5d1c690, byte-identical to r4. Charter copy saved at /tmp/audit_service_contract_claims_0075/r5/.
- Diff against the saved round-4 charter: base and variants identical. Only the four refund wait sentences and their `prerequisite` entries changed, all now `form: action` with a `fallback_reason`; no compute binding, scope, ladder or factor changed. Mechanical sweep clean: every policy_source verbatim in its rule; no snake_case, tool name or policy id in the sentences; every action edge carries a fallback_reason. Re-run of both views (RV=r5): every scored value, all 31 factor figures and all baselines are unchanged.
- Rulings applied: the 1e-9 rounding residue is accepted; a floor that creates an amount is RED; an action-form prerequisite with a valid fallback_reason is acceptable.

### revision_5 — RED-C10 verified against the artifacts
- **RED-C10 closed.** The waits no longer condition on the resolver's computation; each names the depended-on action in business words:
  - "fixed only after the contract's latest component repair line denied for the waiting period has been re-decided and whatever that re-decision owes the holder has been paid";
  - "not computed until the rental benefit of the claim of the contract's latest component-repair line, paid or denied, has been settled and whatever rental it owes the holder has been paid";
  - "not computed until the contract's latest component repair line denied for lack of maintenance has been re-decided and …";
  - "fixed only after the contract's latest component repair line denied as not covered has been re-decided and …".
  The fallback_reason ("A re-decision that repays nothing books no line, so no record state tells a decided line from an undecided one") is valid: a 0.00 re-decision or a 0-day rental leaves no record, so no state singles out the write (accepted per ruling). Four-point test: ordering connective present; action in business words; no tool, id or snake_case token.

### revision_5 — new charter RED (all members, one pass)
**RED-C11 — SOURCE-POLICY (action-form wait broader than its resolver's scope and stronger than its condition: second reading).** Each sentence waits on "the contract's latest component repair line denied for [reason]" being "re-decided", with none of the scope conditions under which the depended-on policy re-decides anything. Each re-decision policy applies "only to such a line": waiting — sold on its deal, group not lubricated with switch true, within the term, one diagnosed concern, customer-pay labor not wholly comeback-credited and closed on or after the decision; maintenance — lubricated group, qualifying Kessler Care visit on the deal's plan, etc.; coverage — switch true, not lubricated, waiting period over, etc. When the latest denial of that reason is a correct denial outside that scope (e.g. a waiting-period denial on a contract sold on its own within its first 30 days; a lack-of-maintenance denial with no qualifying visit; a not-covered denial on a group whose switch is false — all ordinary worlds), the charter has no re-decision for it. Two readings follow:
(A) nothing is owed, so the refund is computed now — the structured `condition` reads this way: "where it owes nothing, no line is booked";
(B) the line "has been re-decided" is literally false and no policy or tool can make it true, so the refund is never computed and the call goes to a human (a scored write).
The two readings give different scored solutions (accept-now vs transfer), so the sentence is stronger than its condition (check 6). Members:
  1. kept <- waiting;
  2. traded <- maintenance;
  3. traded <- coverage;
  4. kept <- rental: "the rental benefit of the claim … has been settled", for a claim with no charged Kessler loaner, or on a level with no rental benefit, where no rental policy settles anything.
The revision_4 state-form sentences carried the scope conditions and had no such reading; this was introduced with the action-form rewrite. No consequence on either task world: every latest denial there is in its resolver's scope and owes a positive amount.

### revision_5 — observations
- O16: the action-form sentences no longer restate the "same-day tie: first in the claim history" rule for "the contract's latest … line"; the depended-on scopes state it, so the line is still unique. No consequence.
- O12–O15 unchanged.

## closing_checklist (revision_5)
Written after both revision-5 reveals (2026-10-22T07:22:49Z).
- Gold is unchanged and matches item by item in both tasks; both tasks' proof text is consistent with the round-5 charter.
- Closed: RED-C10 (action form with a valid fallback_reason, per ruling).
- No earlier PASS item regressed: computes, scopes, ladders, labels, tools (unchanged), base copy and the rental <- waiting state-form edge are as before.
- New: RED-C11. The action-form waits name "the contract's latest … denial … has been re-decided" without the resolver's scope, which gives a second, deadlocking reading whenever that latest denial is a correct, out-of-scope denial. 4 members.
- Difficulty NOT closed while RED-C11 stands.

VERDICT revision_5: task0=PASS task1=PASS charter=RED-C11

## revision_6

## charter_global_frozen (revision_6)
- Written before reading the worklog body and before either task's revision-6 GT. Gate: the last non-blank worklog line is `REWORK round 6: gates 7/7 green`. Snapshot run by the auditor: `/tmp/erl0075_coord/snapshot.sh service_contract_claims 6` (2026-10-22T07:30:29) => EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 vsc.extended.yaml 96f5c0ae9cc6, task_tools.py 3fa9c534c04c (unchanged), tasks/0.json 0b8f2355f8d2, tasks/1.json 800007931d05. Views r6/0.view.json 5569daa8decb66e4 and r6/1.view.json 54148bdbd5d1c690, byte-identical to r5. Charter copy saved at /tmp/audit_service_contract_claims_0075/r6/.
- Diff against the saved r5 charter: base and variants identical. Only the four refund wait sentences and their `prerequisite.condition` changed: same action form and fallback_reason, now with each resolver's scope appended ("wherever …") plus the same-day tie rule (also closes O16). No compute, scope, ladder, factor or label changed. All 47 scored, factor and baseline figures re-run unchanged (RV=r6).

### revision_6 — RED-C11 verified against the artifacts
- Member 1, kept <- waiting: **closed.** The sentence now adds "wherever that line was denied while the contract was sold on its vehicle's purchase deal, its component group is not an internally lubricated one … and has its coverage switch true, the repair order's diagnosis date and the line's odometer fall within the term, and that repair order carries a diagnostic fee on exactly one concern line together with the store's customer-pay labor on that concern line, not wholly credited back as a comeback repair, closed on or after the day the line was decided". That is the waiting re-decision scope test for test. The condition adds "A latest waiting_period denial outside those tests is outside the wait". A correct out-of-scope denial now plainly does not block the refund. A 0.00 in-scope re-decision is made by the waiting policy itself, so "has been re-decided" holds once it is decided.
- Member 3, traded <- maintenance: **closed.** The scope is mirrored test for test (lubricated group with its switch true; latest non-reinstated visit on the plan sold on the deal, with the stated month count; waiting period over or waived; term; single diagnosed concern; labor not wholly comeback-credited, closed on or after the decision).
- Member 4, traded <- coverage: **closed.** Mirrored (not lubricated, switch true, waiting period, term, single diagnosed concern, labor test).
- Member 2, kept <- rental: **closed for the cases revision_5 named** (no charged Kessler loaner as first agreement; a level without rental benefit — both now outside the wait). **One sub-case remains open**, see RED-C11r.
- XF 15 / check 6 on the changed sentences: each is still action form with a valid fallback_reason (ruling), an ordering connective, and no tool, id or snake_case token. The appended scope clauses are record tests in table words. No wait prices another policy.

### revision_6 — remaining charter RED (all members, one pass)
**RED-C11r — SOURCE-POLICY (kept <- rental wait engaged on a claim the rental policy does not cover; second reading).**
- The rental wait engages "wherever that claim carries a paid component-repair line or its latest line is the one the previous sentence waits on".
- The rental policy applies only "where that claim carries a paid component-repair line" (`repair_paid > 0` in compute).
- When the waiting re-decision is in scope but owes 0.00, the claim never gets a paid component-repair line. Example: deductible at least the repayable amount at a non-selling store.
- Its latest line then stays the waiting-period line the previous sentence names, so the wait is engaged. But no policy settles that claim's rental benefit: the rental policy is out of scope, and base vsc_evt_claim_benefits pays benefits "only together with a covered component repair under the same claim number".
- Reading A: nothing is owed, so the refund proceeds. The condition reads this way: "no line where it owes nothing".
- Reading B: "has been settled" is false and no action can make it so, so the refund is blocked and handed to a human.
- Probe (decoys_r6.py; task 0's world with the RO at a non-selling store and a small line-A repair, labor 67.05 + parts 19.00, deductible 100):
  - waiting re-decision in the wait's scope = 0.00, no line booked;
  - rental compute on CLM-4471208: repair_paid 0, 3 charged daily-rental days, result 0.00;
  - the kept rental wait is engaged through its "or its latest line is the one the previous sentence waits on" disjunct.
- Single member: kept <- rental, the in-scope 0.00 re-decision sub-case. The disjunct is needed for the pending state before the repayment, but it also captures the settled 0.00 state.
- No consequence on either task world.

## closing_checklist (revision_6)
Written after both revision-6 reveals (2026-10-22T07:31:56Z).
- Gold is unchanged and matches item by item in both tasks; proof text is consistent.
- RED-C11: members 1, 3 and 4 closed; member 2 closed for the cases revision_5 named. One sub-case remains as RED-C11r (kept <- rental after an in-scope 0.00 waiting re-decision).
- Nothing regressed: compute, scopes, ladders, labels, tools (unchanged) and base copy are as before.
- O16 closed (tie rule now in the sentences).
- Difficulty NOT closed while RED-C11r stands.

VERDICT revision_6: task0=PASS task1=PASS charter=RED-C11r

## revision_7

## charter_global_frozen (revision_7)
- Written before reading the worklog body and before either task's revision-7 GT. Gate: the last non-blank worklog line is `REWORK round 7: gates 7/7 green`. Snapshot run by the auditor: `/tmp/erl0075_coord/snapshot.sh service_contract_claims 7` (2026-10-22T07:49:01) => EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 vsc.extended.yaml 2467c2b7cfc9, task_tools.py 3fa9c534c04c (unchanged), tasks/0.json 8b9f651a16eb, tasks/1.json e798b2286db1. Views r7/0.view.json 5569daa8decb66e4 and r7/1.view.json 54148bdbd5d1c690, byte-identical to r6. Charter copy saved at /tmp/audit_service_contract_claims_0075/r7/.
- Diff against the saved r6 charter: base and variants identical. Exactly one sentence changed — kept's rental wait, plus its `prerequisite.policy_source` and `condition`. The disjunct "or its latest line is the one the previous sentence waits on" was removed, so the wait now engages only "wherever that claim carries a paid component-repair line, the first loaner agreement … is a Kessler loaner on which the holder was charged daily rental, and the coverage level's rental amount per day and rental day limit are both above zero". No compute, scope, ladder, factor or label changed. All 47 figures re-run unchanged (RV=r7).

### revision_7 — RED-C11r graded against the artifacts
- **RED-C11r: genuinely closed.** The wait's engagement test is now the rental policy's own scope, test for test: claim of the latest component-repair line with its tie rule; a paid component-repair line on that claim; first-listed agreement charged daily rental; rental benefit above zero. Re-run of the revision_6 probe (decoys_r6.py, RV=r7): the waiting re-decision owes 0.00 and books no line, so CLM-4471208 carries no paid component-repair line. The rental wait is then not engaged, and the refund proceeds with nothing owed — a single reading.
- Sweep for further members of RED-C11/C11r (action-form wait engaged where its resolver does not act): kept <- waiting, traded <- maintenance and traded <- coverage each engage only inside their resolver's full scope; the rental wait now does too. No further member.
- XF 15 / check 6 on the changed sentence: still action form with its fallback_reason (ruling); ordering connective "not computed until"; record tests in table words; no tool, id or snake_case token; it prices nothing.

### revision_7 — new defect introduced by the fix
**RED-C12 — SOURCE-CHAIN (kept <- rental no longer unmet at the opening; the tree cannot be derived from the policy and the opening world).**
- With the disjunct gone, the kept <- rental edge's condition is satisfied vacuously at the opening of any world where the waited-on claim has only its denied line. That includes task 0's world (see `0.md` revision_7).
- The skill's tree walk — "for each [prerequisite sentence], use the raw DB to decide whether that state holds at frozen_time" — therefore drops rental from the opening tree. The rental write is still entailed later, because the kept wait re-engages once the waiting repayment lands (handling-time evaluation), so it is a prerequisite created mid-conversation rather than one unmet at the opening.
- The declared tree (waiting -> rental -> kept, rental -> kept) and the tree derived from the policy plus the opening world (waiting -> kept) differ, which is the "prerequisite that is not in fact unmet at the opening" shape.
- Charter-wide sweep: the same shape exists only on this edge. traded <- maintenance and traded <- coverage, and kept <- waiting, name lines already denied at the opening, so their engagement does not depend on an earlier write.
- The conflict is between two tests on this one edge: (i) engaged and unmet at the opening (true in round 6, via the disjunct); (ii) engaged only where the rental policy acts (true now). Round 6 met (i) but not (ii); round 7 meets (ii) but not (i).

## closing_checklist (revision_7)
Written after both revision-7 reveals (2026-10-22T10:03:03Z).
- RED-C11r is genuinely closed; there are no further members of its class.
- Nothing else regressed: compute, scopes, ladders, labels, tools (unchanged), base copy; task 1 unchanged and PASS.
- New: RED-C12 (charter) / F0-5 (task 0). The kept <- rental edge is satisfied vacuously at the opening, which task 0's closure itself states ("this wait is not yet engaged"). The declared tree is therefore not the tree derivable from the policy and the opening world. Single member.
- Difficulty NOT closed.

VERDICT revision_7: task0=RED task1=PASS charter=RED-C12

## revision_8

## charter_global_frozen (revision_8)
- Written before reading the worklog body and before either task's revision-8 GT. Gate: the last non-blank worklog line is `REWORK round 8: gates 7/7 green`. Snapshot run by the auditor: `/tmp/erl0075_coord/snapshot.sh service_contract_claims 8` (2026-10-22T10:22:32) => EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 vsc.extended.yaml cbdcb751a3a0, task_tools.py 3fa9c534c04c (unchanged), tasks/0.json 9cb20eddc309, tasks/1.json 5641703a8d5a. Views r8/0.view.json 5569daa8decb66e4 and r8/1.view.json 54148bdbd5d1c690, byte-identical to r7. Charter copy saved at /tmp/audit_service_contract_claims_0075/r8/.
- Diff against the saved r7 charter: base and variants identical. Changes:
  (1) the rental policy's scope sentence now applies to the claim of the latest component-repair line whose first agreement is a charged Kessler loaner, and adds "where it carries none, its rental benefit is settled with nothing owed and no rental line is booked, since benefits beyond the repair are paid only together with a covered component repair" (its compute_basis quotes re-pulled; compute unchanged — `repair_paid > 0` already gated the result);
  (2) kept's rental wait drops "wherever that claim carries a paid component-repair line" and now engages wherever the first agreement is a charged Kessler loaner and the coverage level has a rental benefit; its condition adds "(only once the claim carries a vsc_claim_paid component_repair line)".
  Mechanical sweep clean; all 47 figures re-run unchanged (RV=r8).

### revision_8 — RED-C12 graded against the artifacts
- **RED-C12 / F0-5: genuinely closed.** The kept <- rental wait's engagement test no longer needs a paid component-repair line, so it is engaged at the opening of task 0: CLM-4471208's first agreement LA-448312 is a charged Kessler loaner, and Exclusionary pays 50.00/day for up to 7 days. The rental policy now covers that claim in both states. The action the wait names — settling that claim's rental benefit — has not been performed at frozen_time. The rental policy's own state-form wait, "A rental line is booked only after the records carry a paid component-repair line under the same claim number", places the settlement after the pending waiting re-decision.
- So the tree walked from the root on the opening world is waiting -> rental -> kept, with waiting -> kept as the value input — the declared tree.
- **RED-C11r stays closed.** In the revision_6 probe world (decoys_r6.py, RV=r8: re-decision 0.00, no paid line, rental compute 0.00) the rental policy itself now settles the benefit "with nothing owed and no rental line … booked", so "has been settled" holds by the policy's own act: one reading.
- Sweep of the two classes (C11: a wait engaged where its resolver does not act; C12: a declared edge already satisfied at the opening):
  - kept <- waiting, traded <- maintenance and traded <- coverage each engage only inside their resolver's scope and name a line denied at the opening;
  - kept <- rental now engages exactly where the rental policy acts (both branches);
  - no edge's condition holds at the opening of either task world.
  No member remains.
- Residual reading noted (observation O17, no RED): a reader could "settle with nothing owed" the rental benefit of a claim whose re-decision is still pending, before the waiting write. The kept wait is evaluated at the refund's handling time ("whatever rental it owes the holder has been paid"), by which point the claim carries the paid line and owes 45.00, so the scored order and values are the same under both readings.
- XF 15 / check 6 on the changed sentences: action form with its fallback_reason (ruling); ordering connective; record tests in table words; no tool, id or snake_case token; nothing priced. The new rental scope sentence restates base vsc_evt_claim_benefits ("paid only together with a covered component repair under the same claim number") accurately — no undeclared override.

## closing_checklist (revision_8)
Written after both revision-8 reveals (2026-10-22T10:24:10Z).
- Per-task files correspond one to one with the tasks. Both comparisons match GT item by item (writes, arguments, owners, order, tree edges, all 47 figures) and both carry PASS.
- Open REDs of revision_7: RED-C12 / F0-5 genuinely closed. RED-C11 / C11r remain closed.
- Every earlier RED id (C1–C12, C4r, C5r, C6r, C6r2, C9 under the 1e-9 ruling, C10, C11, C11r; F0-1 … F0-5, F1-1, F1-2) is closed, and none regressed. The tool module (3fa9c534c04c) has been unchanged since revision_2 and enforces its docstrings.
- "render_r1 items": no KB render or render audit exists for this difficulty — there is no audits/render_source/service_contract_claims or audits/policy_kb/service_contract_claims — so there is no render_r1 item to re-check here.
- Six extended policies fully covered by two pairwise-disjoint task scopes. Six task tools, each with its own frozen uuid8.
- Trees: each has 2 prerequisite problems, 1 value_input edge, a user-owned root, and is acyclic; the difficulty graph is a DAG.
- Every computation keeps 4–6 factors with ≥2 parameter and ≥1 method, a multi-source and a cross-difficulty factor per task, each bearing weight against an honest baseline, and an all-baseline figure that differs from gold.
- Gates re-run on the final form by the coordinator snapshot (10:22:32): 7/7 OK.
- Observations O12–O15 and O17 remain (non-blocking).
- Difficulty closed at the source layer.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

## charter_global_frozen (revision_9)
- Input: the renderer's scan-first findings F1–F5 in audits/render_source/service_contract_claims/render_r1.md, read in full. They were found after my CLEAN revision_8. F1–F5 are classes my revisions 1–8 did not report (rental start-day tier 2 condition, the claim-only "later paid" fee test, the claim-only "already repaid" test, standalone plans matched through an empty deal id, in-service-date terms in the starting-odometer tiers); they are acknowledged here as misses of this audit.
- Written before reading the worklog body and before either task's revision-9 GT. Gate: the last non-blank worklog line is `REWORK round 9: gates 7/7 green`. Snapshot run by the auditor: `/tmp/erl0075_coord/snapshot.sh service_contract_claims 9` (2026-10-22T10:52:58) => EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 vsc.extended.yaml 7606ebd47dfc, task_tools.py 3fa9c534c04c (unchanged), tasks/0.json c72608e1cf2d, tasks/1.json 8c4e8da8c4d3. Views r9/0.view.json 5569daa8decb66e4 and r9/1.view.json 54148bdbd5d1c690, byte-identical to r8. Charter copy saved at /tmp/audit_service_contract_claims_0075/r9/.
- Diff against the saved r8 charter: base and variants identical.
  - Compute: rental `start_day` tier 2 now requires `loaner_out == diag_day`. kept/traded fee tier: new bindings denied_claim (component_repair only), denied_ro, denied_group, denied_day, repaid_day, and `redecided_count` now counts by claim, RO and group with `repaid_day > denied_day`. `already_repaid` in all three re-decisions counts by claim, RO and group. Every deal-keyed plan/GAP read is guarded by a non-empty purchase_deal_id. kept/traded `run_from` tiers 1–2 are gated on `term_start_basis == 'sale_date'`.
  - Rule sentences rewritten to match: "(a contract sold on its own has no such plan)"; "later paid as a component-repair line on the same claim number, repair order and component group"; "where the contract's term counts from its sale date …; otherwise, including every term counted from the vehicle's in-service date, the term start odometer".
  - The re-decision labor/parts tiers dropped "under an Owner Rewards labor/parts discount" — now "charged below its list amount", which equals the compute test.
  Mechanical sweep clean (quotes, bases, overwrites, prerequisite sources, factor independence). All 47 task figures re-run unchanged (RV=r9).

### revision_9 — F1–F5 graded against the artifacts (renderer witness worlds re-run: witness_r9.py on the r8 vs r9 charters)
- **F1 closed.** Witness: loaner out 09-07, diagnosis 09-08, denial 09-09. r8 starts 09-09, 5 days, 45.00. r9 starts on the diagnosis day 09-08, 6 days, 90.00 — the rule's otherwise tier.
- **F2 closed as reported.** Witness: paid engine line plus denied rental line on CL-1. r8: fee 0.00, 2035.27. r9: denied_claim None (rental denials no longer count), fee 25.00, 2010.27 — what the rule gives.
- **F3 closed.** Witness: CLM-4439217 also carrying a paid steering line. r8 already_repaid 1, 0.00. r9 already_repaid 0, 1080.91.
- **F4 closed.** Witness: standalone contract and standalone plan. r8 picks the plan, visit_proof 1, 6783.37. r9 plan_id None, 0.00.
- **F5 closed.** Witness: an Exclusionary Wrap term, delivered late. r8 run_from 41236. r9 run_from 0 (the term start odometer), so pre-sale miles count as used.

### revision_9 — class sweep (all members, one pass)
- F1 class (a tier's stated condition only partly implemented): every tier of every ladder was rechecked condition by condition. All implemented, except as below.
- F2 class (the fee tier's "later paid" test): **one residual pair, RED-R9a.**
- F3 class: rental `days_already` and `repair_paid` are claim-level by their own rule text — consistent. No other member.
- F4 class: deal reads return nothing for an empty id, and GAP reads are guarded. No other member.
- F5 class: credited days and elapsed days count only post-sale or from term start, consistent with the in-service clause. No other member.
- A further second-record member surfaced in the sweep: **RED-R9b.**

**RED-R9a — SOURCE-POLICY (fee tier "later paid" has no same-day convention; F2-class residual).**
- Both fee tiers now read "the contract's latest denied component-repair line (by decision date; on a same-day tie, the one that appears first in the claim history) was later paid as a component-repair line on the same claim number, repair order and component group".
- The compute implements "later" as `repaid_day > denied_day`, a strict date comparison. The rule states a tie rule for "latest" but none for "later".
- Witness (witness_f2r.py, task 0's world moved to a single day): denial of CLM-4471208, line-A labor close and the holder's call all on 2026-10-21. The waiting re-decision is in scope (begun_after_claim 1) and repays 1667.15 on 2026-10-21, after the denial in the claim history. Rule: the line "was later paid", so no fee and the refund is 3780.75. Compute: repaid_day = denied_day, so redecided_count 0, fee 25.00, refund 3755.75.
- Members: (1) kept cancel_fee_standing tier 1; (2) traded trade_fee_rule tier 1.

**RED-R9b — SOURCE-POLICY (second-record read without a stated selection, XF 9).**
- Rental tier 2 reads "where the loaner went out on that day and a line of the claim was denied after it, the day of that denial".
- A claim routinely carries several denied lines (one per component group or benefit), but "that denial" does not say which when two or more were denied after the diagnosis day.
- The compute takes the latest: `denial_day: LATEST(... event_type='vsc_claim_denied', claim_number=claim)`.
- Producible world (witness_r9b.py, confirmed): task 0's claim with a second line denied 09-11 (e.g. a pre-existing-condition denial of another group). Rule reading "the first such denial" starts 09-09 (5 window days − 4 free = 1 day, 45.00). Compute starts 09-11, window 09-11…09-13 = 3 days − 4 free, so the result is 0.00.
- Single member: rental_window_start tier 2.

Neither RED-R9a nor RED-R9b has a consequence on either task world: denial and repayment fall on different days, and each claim has one denied line.

## closing_checklist (revision_9)
Written after both revision-9 reveals (2026-10-22T10:55:57Z).
- Renderer findings F1–F5 are all genuinely closed. Each witness world was re-run on the r8 and r9 charters and now gives the rule's figure.
- No regression: gold and all 47 figures are unchanged; trees, scopes, factor floors and labels hold; tools are unchanged; every revision_1–8 RED stays closed.
- Remaining: RED-R9a (F2-class residual — "later paid" read as a strict date comparison with no stated same-day convention; 2 members) and RED-R9b (rental tier 2 "the day of that denial" with several post-diagnosis denials on the claim; 1 member).
- Difficulty NOT closed.

VERDICT revision_9: task0=PASS task1=PASS charter=RED-R9a,RED-R9b

## revision_10

## charter_global_frozen (revision_10)
- Written before reading the worklog body and before either task's revision-10 GT. Gate: the last non-blank worklog line is `REWORK round 10: gates 7/7 green`. Snapshot run by the auditor: `/tmp/erl0075_coord/snapshot.sh service_contract_claims 10` (2026-10-22T12:04:11) => EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 vsc.extended.yaml 3cfdcd5e20ef, task_tools.py 3fa9c534c04c (unchanged), tasks/0.json 8ccca773bb6d, tasks/1.json 6689eadc98b9. Views r10/0.view.json 5569daa8decb66e4 and r10/1.view.json 54148bdbd5d1c690, byte-identical to r9. Charter copy saved at /tmp/audit_service_contract_claims_0075/r10/.
- Diff against the saved r9 charter: base and variants identical. Three sentences changed — the rental start-day sentence, and the kept and traded fee sentences — together with their ladders. One compute change: `redecided_count` uses `repaid_day >= denied_day` in kept and traded. Mechanical sweep clean; all 47 task figures re-run unchanged (RV=r10).

### revision_10 — RED-R9a / RED-R9b graded against the artifacts
- **RED-R9a: genuinely closed (both members).** Both fee sentences now state the same-day convention, "(a paid line entered on or after the day of that denial counts as later)", and the compute is `repaid_day >= denied_day`. The same-day witness (witness_f2r.py; denial, labor close and repayment all on 2026-10-21) gives redecided_count 1, fee 0.00, refund 3780.75, which the rule now also gives. No earlier same-day paid line can share a denied line's claim, RO and group: the ledger grain is one line per claim, line type and group, so only a re-decision line can match.
- **RED-R9b: genuinely closed.** The rental tier 2 now reads "the day of the claim's latest denial (by decision date; several lines denied on that same day share it)", matching `LATEST(... vsc_claim_denied, claim_number=claim)`. The witness (witness_r9b.py, a second line denied 09-11) gives start 09-11 and 0.00 under both rule and compute. Observation O18: starting the rental from the claim's last decision can leave a holder who paid loaner days with no rental line. That follows a stated, record-keyed rule with no contradiction, so it is not RED.
- **render_r1 items stay closed.** F1–F5 witnesses re-run on r10 (witness_r9.py): F1 90.00, F2 fee 25.00 / 2010.27, F3 1080.91, F4 0.00, F5 run_from 0 — all the rule's figures.
- Sweep for further members of both classes:
  - "after/later" date comparisons: rental tier 1 "after the day of … diagnosis", tier 2 "after it [that day]", re-decision "closed on or after the day the contract decided the line", traded tiers "after this contract's sale date and on or before the request date", and the fee "on or after the day of that denial" — each now states its day-level convention.
  - Second-record selections: every "latest"/"first" read has a stated order and tie rule.
  - No member remains.

## closing_checklist (revision_10)
Written after both revision-10 reveals (2026-10-22T12:05:04Z).
- RED-R9a and RED-R9b are genuinely closed. render_r1 F1–F5 stay closed (witnesses re-run on r10).
- Every RED id of revisions 1–9 stays closed; nothing regressed: gold and all 47 figures are unchanged; trees, scopes, factor floors and labels hold; the tool module (3fa9c534c04c) is unchanged.
- Coverage, scope disjointness, trees (2 prerequisite problems, 1 value_input edge, user-owned root, acyclic), factor floors and honest baselines: as recorded in revision_8's checklist, with no change since.
- Gates 7/7 OK on the final form (snapshot 12:04:11).
- Observations O12–O15, O17 and O18 remain (non-blocking).
- Difficulty closed at the source layer.

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN

## revision_11

## charter_global_frozen (revision_11)
- Seed-only round for the KB audit's source-side items SRC-1, SRC-2 and SRC-3 (audits/policy_kb/service_contract_claims/_difficulty.md, KB revision_1, read in full together with its task file 1.md).
- Written before reading the worklog body and before either task's revision-11 GT. Gate: the last non-blank worklog line is `REWORK round 11: gates 7/7 green`. Snapshot run by the auditor: `/tmp/erl0075_coord/snapshot.sh service_contract_claims 11` (2026-10-22T12:41:26) => EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; sha256 vsc.extended.yaml 3cfdcd5e20ef and task_tools.py 3fa9c534c04c — both byte-identical to my saved r10 copies (cmp) — tasks/0.json 6a79576e5071, tasks/1.json 163899285f35. Views r11/0.view.json 7313ac717a29a617 and r11/1.view.json a411bf1865f1077a, both changed from r10 (seed only).
- Charter and tools are unchanged, so every charter-global section of revision_10 carries forward on hashes 3cfdcd5e20ef / 3fa9c534c04c. The F1–F5, R9a and R9b witnesses re-run on the r11 views give the same rule figures.

### revision_11 — seed diff (r10 -> r11) and the three items
- **SRC-1 (task 0) — closed.**
  - New service_repair_authorizations rows: RO 446215 line A, estimate 1634.54 (= customer-pay labor 482.76 + parts 1151.78), authorized 2026-09-09; line B, estimate 273.70 (= 174.33 + 99.37), authorized 2026-09-12.
  - The 149.00 diagnostic_applied_to_repair credit dated 09-09 now rests on an authorization the same day as the diagnosis-plus-one. Both lines are billed within their estimates, and line B is authorized before its 09-14 labor.
  - The diagnostic-fee tier (credited in full -> 0.00) is unchanged, and so is the scored 1667.15.
- **SRC-2 (task 1) — closed.** The Kessler Care Plus 6-Visit sold-or-traded refund calculation (2026-09-28, odometer 73684) is now 85.95, with a maintenance_refund_paid 85.95 to the lienholder on 2026-10-06. Re-priced against the published maintenance documents:
  - financed on the installment contract -> pro rata 521.55 × 1/6 = 86.93 (retail_refund_method_financing_and_term_6746c928);
  - the Passport vehicle_price charge posted 2026-09-28, fewer than 1 whole month before the effective date -> fee 0.00 (trade_up_cancellation_fee_d54a541c);
  - Silver -> +10.00 (owner_rewards_refund_credit_f1edd2c8);
  - sold on deal at 521.55 below 549.00, 29 whole months in force -> −0.4 × 27.45 = −10.98 (bundle_discount_recapture_2eddb3c3);
  - combined and rounded -> 85.95 (retail_cancellation_refund_figure_38d01dc3);
  - paid once, in full, to the lienholder named on a financed plan, 8 days after processing (refund_payment_terms_af8536cf).
  This is the figure the KB audit derived. The traded refund reads only this row's date and odometer, both unchanged.
- **SRC-3 (tasks 0 and 1) — closed.** purchase_transactions are now seeded for every deal the tasks hold: deposit received, contract-date postings (vehicle price, documentary, filing, title fees, sales tax, and negative equity 18.42 on the Passport deal), deposit applied at delivery, cash and lender-funding payments. Each deal nets to 0.00, matching its closed status and balance_due 0.00:
  - KHR-26-41087: 29723.15 posted = 500 + 1634.75 + 27588.40.
  - KHB-24-40517: 33995.38 = 1000 + 3852.75 + 29142.63.
  - KHB-26-41862: 46864.07 = 1000 + 9451.49 + 36412.58.
  Sales tax follows the price less the trade allowance (21380 × 6.75% = 1443.15). The Passport deal's trade_payoff_amount moved 11842.37 -> 23618.42, so allowance 23600 less payoff gives the posted negative equity of 18.42. No VSC compute reads any purchase transaction or the trade payoff.
- **Scored values:** none moved. All 47 figures re-run on the r11 views (t0.py, t1.py; RV=r11) equal revision_10's. No factor's tier or weight changed, and no VSC binding reads a row this round added or edited — authorizations, purchase transactions and trade payoff are unread; the Kessler Care refund amount is unread, and its date and odometer did not change.
- **Persona:** both user_scenario texts are byte-identical to r10. Nothing in either persona concerns authorizations, deal postings or the plan refund amount, so there is no conflict with the new rows.

## closing_checklist (revision_11)
Written after both revision-11 reveals (2026-10-22T15:04:31Z).
- SRC-1, SRC-2 and SRC-3 are closed against the seed and the owning products' published documents, as itemized above. The worklog's same-class check is confirmed on the views: every customer-pay RO line in both worlds has an authorized estimate equal to its billed amount; every deal nets to 0.00; there are no other plan refund rows.
- No scored value moved. Charter and tools are byte-identical (3cfdcd5e20ef / 3fa9c534c04c). Personas are unchanged and consistent with the seed.
- Nothing regressed: all 47 figures and every revision_1–10 closure hold, and render_r1 F1–F5 plus R9a/R9b re-run on r11 give the rule figures.
- Gates 7/7 OK (snapshot 12:41:26).
- Difficulty closed at the source layer.

VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN
