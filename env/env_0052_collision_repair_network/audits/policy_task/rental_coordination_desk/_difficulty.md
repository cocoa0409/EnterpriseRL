# Policy-task audit — rental_coordination_desk / charter-global

## charter_global_frozen

- Freeze inputs (re-hashed by the auditor, matching the coordinator brief):
  - `tasks/rental_coordination_desk/rental.extended.yaml` sha256 prefix `d01e7c79e13a1720`
  - `tasks/rental_coordination_desk/task_tools.py` sha256 prefix `358e28ceb5898337`
  - masked views `.audit_views/policy/rental_coordination_desk/0.masked.json` `366e3dd663aa4d44`, `1.masked.json` `7a51d7099cd7d818`
- Freeze time: 2026-10-11 01:51–01:54 UTC (written before any task JSON or the difficulty worklog was opened). Auditor: independent policy-task auditor (not the instantiating agent).
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/{rental,retail,claim,adas,warranty,estimate}.yaml` (variant parameters and lifecycles only for the cross-category reads), the extended charter, `task_tools.py`, the two masked views, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (to know what `CFIELD`/`XLATEST`/`DAYS`/`MONTHS` mean).
- Masked / unread at freeze: `tasks/rental_coordination_desk/tasks/*.json` (all of `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, closures), `tasks/rental_coordination_desk/worklog.md`, the scenario-level `worklog.md`, other difficulties' tasks/audit views/audits.
- Entry conditions: the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cache_diff, check_cross_fire; check_traceability deferred) and the masked-view hashes came with the brief; cited, not re-run. Base section of the extended charter is byte-identical to `blueprint/products/rental.yaml` (first 1280 lines `diff` clean; every top-level key equal).
- This file contains nothing derived from a revealed GT. The `closing_checklist` heading at the bottom is written after the reveals.

### policy_conflict_scan

Seven extended policies, each with its own `(target_tool, computes)`:

| policy | target_tool (owner) | computes | trigger | prerequisite edges |
| --- | --- | --- | --- | --- |
| rental_ext_time_charge_correction | credit_rental_billing_error_4d32ac17 (agent) | amount_usd | state_due | — |
| rental_ext_repair_customer_discount | credit_repair_customer_discount_d339b3bd (agent) | amount_usd | state_due | -> time_charge_correction (value_input) |
| rental_ext_young_renter_fee | charge_young_renter_fee_a6a6d206 (agent) | amount_usd | state_due | — |
| rental_ext_delay_goodwill | accept_rental_goodwill_credit_52804ea3 (user) | amount_usd | on_request | -> repair_customer_discount (value_input), -> young_renter_fee (value_input) |
| rental_ext_network_courtesy_days | authorize_network_courtesy_days_8334cede (agent) | days_count | state_due | — |
| rental_ext_insurer_extension_days | authorize_insurer_extension_days_b8e4d7d7 (agent) | days_count | state_due | -> network_courtesy_days (state_gate) |
| rental_ext_self_pay_days_charge | authorize_self_pay_days_charge_125d1a79 (user) | amount_usd | on_request | -> network_courtesy_days (value_input), -> insurer_extension_days (value_input) |

- Overlapping subjects: three policies write `rental_customer_credit` (billing_error / customer_pay_discount / goodwill — distinct `credit_reason`, distinct tools); two write `rental_customer_charge` (young_renter / uncovered_days on insurance rentals — distinct `charge_type`); two write `rental_authorization` (network_delay_courtesy paid by network / insurer-paid extension naming a request). No two policies claim the same reason/kind on the same subject; outcomes do not collide.
- Cross-reads among extended policies are consistent: discount reads billing-error credits (written by time_charge_correction); goodwill reads all standing credits and the young-renter charge; self-pay reads all authorizations and the courtesy authorizations. Each reader's reading matches the writer's row shape (`credit_reason`, `charge_type`, `authorization_reason`, `paid_by`).
- Cross-category read boundaries: warranty (status), claim (status, delivered_date, supplements, labor_hours_per_production_day), retail (dates, discount_program, tier parameters), adas (order dates, events), estimate (status). All read-only; no extended policy writes outside the rental tables.
- Scope partition (to be confirmed per task): the two trees the prerequisite graph forms are {goodwill, discount, time_charge_correction, young_renter_fee} (customer-pay rental tied to a customer-pay repair) and {self_pay, network_courtesy, insurer_extension} (insurance rental). They share no node, so two tasks rooted at goodwill and self-pay would be pairwise disjoint and jointly cover all seven extended policies.
- Base conflicts found by this scan are written under `override_declarations` and `findings` (CG-1, CG-2, CG-3).

### rule_compute_equivalence

Every `compute_basis` value was checked to be verbatim in its policy's `rule` (normalised whitespace). One basis (`rental_ext_time_charge_correction.corrected_time_charge`) is the concatenation of two rule sentences separated by other text; each half is verbatim — acceptable. Sweep back, rule -> compute, per policy:

- **time_charge_correction**: posted charge/days (final uncovered_days), prior billing-error credits, priced days (whole days; +1 when return time later than pickup time; posted days when no return), block rate (span ladder 21/14), extra-day rate (warranty x recent claim delivery), price structure (>=7 / >=threshold / shorter), result `RND(MX(0, posted - corrected - prior))` — all implemented. Gaps: (a) `prior_claim_delivered = CFIELD('claim','delivered_date', status='closed')` filters on `status='closed'`; the rule says "had a network insurance claim repair delivered fewer than loyalty_lookback_months calendar months before the credit date" and names no status; and `CFIELD` returns the first matching row, not "a" qualifying repair (CG-4). (b) "the return time as counted" is implemented as raw `F('return_time') <= F('pickup_time')`, with no `return_grace_minutes` (CG-5).
- **repair_customer_discount**: base choice, period share (`DAYS(pickup, date)+1` days starting on/before the date, capped at rental days), business-day overrun (Mon–Fri, start date excluded, end date included), calibration points (sublet && failed>=1 / failed>=1 / 0), program points (retail tier parameters) — implemented. The business-day counting convention (start excluded) is not stated in the rule ("counted in business days (Monday to Friday) from the repair start date to the ready date"); no task outcome turns on it (observation).
- **young_renter_fee**: fee days, age/span fee, hold days, reliability — implemented. Compute takes tier 1 of hold days only when both `sublet_date` and `completed_date` exist; the rule's tier 1 condition is "was sublet to a dealer" alone (observation; latent). `CFIELD('adas', ..., retail_repair_id=F('retail_repair_id'))` on an insurance rental would match on the string `'None'` (observation; latent, both tasks unaffected).
- **delay_goodwill**: delay days, authority days, lost-day time value, lost-day fee value, share, limit, cap at standing time charge — implemented. The rule's scope is "a network repair the rental is tied to" (any repair) while every repair read in compute is `CFIELD('retail', ...)`; an insurance rental's repair would read as absent (observation; latent).
- **network_courtesy_days**: lost days, window close, allowance, alignment, review days, share, ceiling — implemented. `courtesy_review_decided` takes the latest decision on the repair, not the decision of the reviewed submission (observation; latent with several supplements).
- **insurer_extension_days**: most recently decided approval, ground ladder, approved share, added days, late-request days, `MN(approved, supported)` — implemented. Tier 2 of late-request days compiles to `(reach - request_day) * 24 < lead_hours` under `request_day == reach`, i.e. `0 < 24`, always true (observation O-3). "computed from the supplement" does not say which supplement when several exist; compute takes the latest submission (observation; latent).
- **self_pay_days_charge**: rental days, covered days ladder, self-pay days, day rate, adjusted weekly, pricing, standing reduction — implemented.

No compute binding without a rule sentence other than CG-4's `status='closed'` filter; no rule sentence without a binding.

### action_binding_and_uuids

- Seven `(target_tool, computes)` pairs, each claimed by exactly one policy (table above). Tool owners: agent for the five state_due writes; user for the two on_request writes (`accept_rental_goodwill_credit_52804ea3`, `authorize_self_pay_days_charge_125d1a79`).
- Function bodies (`task_tools.py`): every tool only `ctx.create`s one `rental_ledger` row with the given values; none reads a balance, validates a prerequisite, refuses, errors, or hints. `authorize_insurer_extension_days_b8e4d7d7` reads only the request's `request_reason` to stamp `authorization_reason`. No tool checks order or eligibility.
- Docstrings name no other tool and state no position in a sequence. The two authorization tools describe `authorization_number` as "the next ordinal after the authorizations already on the rental" — an ordinal definition, not a sequencing instruction (observation O-1).
- uuid8s: `4d32ac17`, `d339b3bd`, `a6a6d206`, `52804ea3`, `8334cede`, `b8e4d7d7`, `125d1a79` — seven distinct values, no shared prefix or suffix, no sequence pattern. Cross-difficulty reuse could not be checked without reading sibling tool modules (out of the read domain).

### prerequisite_graph

- Every extended policy has `prerequisite` filled in (`[]` for time_charge_correction, young_renter_fee, network_courtesy_days).
- Edges: discount->time_charge_correction; goodwill->discount; goodwill->young_renter_fee; insurer_extension->network_courtesy; self_pay->network_courtesy; self_pay->insurer_extension. Every `problem` is an extended policy id in this file, none a base policy, none self. Acyclic (two DAGs, depth 3 and 2).
- `policy_source` is verbatim in the blocked policy's own `rule` for all six edges; not restated in the depended-on rule.
- `form: state` on all six; no `fallback_reason` (correctly absent).
- `resolved_by` = the depended-on policy's `target_tool` on all six, and that tool's row is exactly the state named.
- `kind`/`gate`: the five `value_input` gates (`discount_base_amount`, `lost_day_time_value`, `lost_day_fee_value`, `selfpay_covered_days` x2) are real compute bindings of the blocked policy. The one `state_gate` (insurer_extension->network_courtesy) names `gate: rental_ledger.authorization_reason`; `rental_ext_insurer_extension_days` carries no `eligibility` entry, so the gate is a ledger field, not an eligibility gate, and its stated `effect` is only that the extension "carries the next authorization ordinal" (observation O-2; whether it bears weight is judged in task 1).
- `condition` texts match the sentences in strength and scope (closed set "every young-renter fee the renter owes", "every extension the insurer approved"; conditional "where the network's calibration window ... supports courtesy days"). No authoring-viewpoint wording.

### prerequisite_sentences

Four-point test on all six sentences:

| blocked policy | sentence | connective | waited-on state (record-visible) | the one write that brings it about |
| --- | --- | --- | --- | --- |
| discount | "The repair-customer discount is worked out only after any amount by which the time charge was posted above the rental's correct time charge stands credited against it as a billing error." | only after | a `rental_customer_credit` with `credit_reason=billing_error` against the time charge | billing-error credit (time_charge_correction) — the only writer of reason billing_error |
| goodwill | "A goodwill credit for lost rental days is not fixed until the repair-customer discount owed on the time charge stands against it." | not ... until | a `customer_pay_discount` credit against the time charge | repair-customer discount (discount) |
| goodwill | "The goodwill credit for lost rental days is fixed only after every young-renter fee the renter owes on the rental stands as a charge on it." | only after | a `rental_customer_charge` with `charge_type=young_renter` | young-renter fee (young_renter_fee) — the only writer of that kind |
| insurer_extension | "An insurer extension is posted on the rental only after the courtesy days the network owes for its own delay on the same repair stand on the reservation." | only after | a `rental_authorization` with reason `network_delay_courtesy` | network courtesy (network_courtesy_days) |
| self_pay | "The self-pay charge is fixed only after the days the network's own calibration trouble cost the repair stand on the reservation as network courtesy days." | only after | same | network courtesy |
| self_pay | "A self-pay charge is not booked until every extension the insurer approved on the reservation stands as authorized days." | not ... until | an insurer-paid authorization naming each approved request | insurer extension (insurer_extension_days) |

- All six are state form, name no tool, no policy id, no snake_case token, no row id; strength matches `condition`.
- Derivation sentence + records + depended-on rule -> resolving action, single reading: e.g. "credited against it as a billing error" + rental_ledger has no billing_error credit + time_charge_correction's rule ("A billing-error credit corrects the time charge ... when that posted time charge is above the time charge the rental should carry") -> compute and book that credit. The same pattern holds for each row; no state can be brought about by two writes of this difficulty.
- No rule carries a second wording of a dependency or a cross-problem order that grounds no edge. Base rules carrying cross-problem orders ("recorded only after the insurer has authorized the repair itself", "The rental has been returned before its invoice is split") ground no edge of either tree (observation only).

### override_declarations

Each `base_policy_refs` entry checked one sentence at a time against the quantity the extended policy scores (findings only; consequences are shown in the task files):

- **time_charge_correction** (refs: customer_settlement, settlement_split, rental_days). settlement_split's customer-pay weekly sentence: replaced, declared. customer_settlement "billing_error corrects a wrong charge": followed. rental_days "a return no more than return_grace_minutes minutes into a new period does not start it": the extended priced-day count ("where the return time as counted is later than the pickup time of day ... plus one") is implemented with no grace, and the overwrite does not name this base sentence -> CG-5 (latent). rental_days "at least min_rental_days_billed day is billed": not restated; no consequence (zero-day rentals cannot carry a final time charge).
- **repair_customer_discount** (refs: customer_settlement, settlement_split). The customer_pay_discount sentence is replaced and declared. "Credits name the charge they reduce and never exceed it": followed.
- **young_renter_fee** (refs: settlement_split, options_and_fees, class_and_renter). class_and_renter's fee sentence is replaced and declared. settlement_split "young-renter fees ... are always the customer's": followed. options_and_fees: its enumerated options do not include the young-renter fee, so no conflict.
- **delay_goodwill** (ref: customer_settlement). The goodwill cap sentence is replaced and declared. "Credits name the charge they reduce and never exceed it": followed (cap at standing time charge).
- **network_courtesy_days** (refs: initial_authorization, extension). extension "The insurer's approval of the extension request is recorded." is replaced and declared. extension "Days lost to a delay the network caused ... are authorized as network_delay_courtesy, paid by the network ... without an insurer request": followed. extension **"Every authorization moves the coverage end date by the days authorized."** is not overwritten. It is therefore inherited, but no tool of this difficulty (or share tool) writes `coverage_end_date` -> CG-3.
- **insurer_extension_days** (refs: initial_authorization, extension). The supplement-days sentence is replaced and declared. The extension sentence **"One request asks for no more than max_extension_days_per_request days and reaches the insurer at least extension_request_lead_hours hours before the current coverage end; a later request may only cover days from the date of approval."** governs the same quantity as the extended late-request days. The extended tier "a request that reached the insurer on the insurer coverage end day itself, inside extension_request_lead_hours, and was decided after it loses those days less one", and the fall-through "any other request loses none" (which includes a request reaching the insurer the day before coverage end but inside 24 h), let a late request cover days before the date of approval. Neither sentence is named in `overwrite` -> CG-1 (undeclared override). Also inherited and not overwritten: "Every authorization moves the coverage end date ..." -> CG-3.
- **self_pay_days_charge** (refs: settlement_split, options_and_fees, rental_days, coverage_end). settlement_split's "Every rental day not covered is an uncovered_days charge at partner_daily_rate_usd" is replaced and declared. coverage_end **"Every rental day starting after the coverage end date is the customer's at the partner rate."** prices the same days at the partner rate and is not named -> CG-2 (undeclared override). rental_days **"Covered days used are the rental days that start on or before the coverage end date, up to the covered days remaining (rental_msr_covered_days_remaining)"** counts covered days against the coverage end date. The extended covered-days tier 1 ("where no repair notice stands and the days authorized ... reach past the coverage end recorded on the reservation, they are those authorized days") counts them differently whenever the recorded end lags the authorizations, and it is not named -> CG-2 (together with CG-3).

### factor_ladders

Per policy: factor id (label) — tiers — notes. Every tier of every ladder was found in the rule prose and in the `decides` binding. Bindings are disjoint within each policy, and no `decides` is `result`.

**time_charge_correction** — baseline.rule: posted days x partner rate (self-sufficient; every sentence in rule; `params: [partner_daily_rate_usd]`).
- priced_day_count (parameter): return<=pickup time -> whole days / return later -> whole+1 / no return recorded -> posted days. **The fall-through tier "no return recorded" is unreachable for any customer who reaches this write.** The write corrects "the time charge the rental partner posted on the final invoice", and base `rental_evt_settlement_split` gates every final-invoice charge on `rental_returned` ("The rental has been returned before its invoice is split."). So the ladder has two live tiers, and its fall-through (= the factor's baseline) is never taken -> CG-6.
- time_charge_structure (method): >=7 blocks + extras capped / threshold..6 lesser-of / shorter partner rate. Genuine method; distinct.
- long_rental_block_rate (parameter): span>=21 -> -15% / 14..20 -> -10% / else weekly. Distinct values. Its fall-through (weekly_rate_usd) is not stated by the baseline method, which has no blocks (observation O-4).
- standing_extra_day_rate (parameter, cross_difficulty warranty; multi-source warranty x claim): both -> weekly/7 / exactly one -> min(partner, weekly/6) / neither -> partner.
- Counts as declared: 4 factors, 3 parameter, 1 method. Counting only tiers that survive (CG-6 strikes priced_day_count): **3 factors (<4)**.

**repair_customer_discount** — baseline.rule: customer_pay_discount_pct of final time charge (self-sufficient; in rule).
- discount_base_choice (method): corrected / final - billing-error credits / final. Live; distinct.
- repair_period_share (method): released & returned after -> days to release / ready not released -> days to ready / else 1. Tiers 1–2 are the same formula with a different date. Labelled method; arguably a date parameter (observation O-5; does not change counts because discount_base_choice is a method).
- overrun_discount_rate (parameter): >3 -> 2x / 1..3 -> +5 / none -> pct.
- calibration_points (parameter, cross_difficulty adas; multi-source sublet x failed attempts).
- program_points (parameter; reads retail, which no difficulty claims, so `cross_difficulty: null` is honest).
- Counts: 5 factors, 3 parameter, 2 method; survives.

**young_renter_fee** — baseline.rule: class fee x rental days (self-sufficient; in rule).
- weekly_fee_days (method): >=7 -> 5/week + rem<=5 / threshold..6 -> min(days,5) / shorter -> every day.
- age_span_daily_fee (parameter): age<=22 & span>=14 -> fee+5 / **age > young_renter_max_age -> zero** / else fee. **The second tier's condition is the negation of the policy's own scope** ("A renter who is young at pickup owes a young-renter charge on the rental"), so no customer who reaches this write is on it. Two live tiers -> CG-6.
- calibration_hold_days (parameter, cross_difficulty adas).
- booking_reliability_reduction (parameter, cross_difficulty estimate; multi-source converted x no-show).
- Counts as declared: 4 (3 parameter, 1 method). After CG-6: **3 factors (<4)**.

**delay_goodwill** — baseline.rule: overrun business days capped at class authority x partner rate x share_standard (self-sufficient; in rule).
- calibration_delay_days (method, cross_difficulty adas): first failed & sublet -> first attempt..completion / first failed & later pass -> first attempt..pass / else business-day overrun. Tier 3 is a different algorithm, so the method label holds.
- goodwill_authority_tier (parameter, cross_difficulty warranty; multi-source sublet x warranty).
- lost_day_time_basis (method): credits stand -> (final - credits)/rental days / no credit & time charge -> final/posted days / **no time charge -> partner rate**. **The third tier cannot reach the result.** The credit "names the rental's time charge" and is capped at "the time charge still standing after the credits against it". With no time charge that cap is <= 0, so the result is 0 whatever the tier selects -> CG-6. After CG-6: 4 factors remain, including 1 method.
- lost_day_fee_basis (parameter): young charge stands -> charge/rental days / none but renter young -> class fee / else 0. Tier 2 is reachable at the correct handling time only when the renter's young-renter charge works out to zero (then it values a fee the renter never paid) — observation O-6.
- delay_goodwill_share (parameter; multi-source overrun x sublet).
- Counts: 5 declared (3 parameter, 2 method); 4 survive (3 parameter, 1 method) — within bounds.

**network_courtesy_days** — baseline.rule: calendar days opening..completion less one allowance day (self-sufficient; in rule; `allowance_static_days` = 1 matches "one allowance day").
- lost_day_start (method, adas): first failed & sublet -> first attempt..close / first failed & pass -> first attempt..pass / else opening..close.
- window_closing_date (method, adas): return recorded & (no completion or completion after return) -> return date / no return & no completion -> today / else completion date. **Every tier selects a date substituted into the same `DAYS(start, close)`. The tiers change a value, not the algorithm, so the label is dishonest** -> CG-7. Relabelled, the counts are 5 parameter and 1 method (lost_day_start), still within bounds.
- procedure_allowance, alignment_days (parameter, adas), insurer_review_days (parameter, claim), responsibility_share (parameter, adas; multi-source DTC x sublet).
- Counts: 6 declared (4 parameter, 2 method).

**insurer_extension_days** — baseline.rule: days the insurer approved (self-sufficient; in rule; `params: []`).
- supported_days_ground (method): supplement computation / parts min(asked, max) / approved.
- supplement_added_days (parameter, claim; multi-source structural x calibration), supplement_approved_share (parameter, claim), late_request_days (parameter; multi-source request day x decision day x reach). Tier 2's "inside extension_request_lead_hours" is vacuous once "on the insurer coverage end day itself" holds (O-3).
- Counts: 4 (3 parameter, 1 method).

**self_pay_days_charge** — baseline.rule: calendar days pickup..return both counted less days starting on/before the recorded coverage end, at partner rate (self-sufficient; in rule).
- selfpay_rental_day_count (parameter): return<=pickup time -> whole / later -> whole+1 / **no return recorded -> none**. The fall-through cannot be reached: the charge is "booked as one uncovered_days customer charge on the final invoice of the returned rental". Also, the factor's `baseline` (`whole_days + 1` when a return exists) is not its fall-through tier. It equals tier 2's value -> CG-6.
- selfpay_coverage_reach (method), selfpay_pricing_structure (method), selfpay_day_rate_tier (parameter, claim; multi-source repair open x courtesy days), selfpay_standing_reduction (parameter, warranty; multi-source warranty x converted booking).
- Counts: 5 declared (3 parameter, 2 method); 4 survive (2 parameter, 2 method) — within bounds.

Cross-difficulty categories read: warranty, claim, adas, estimate (all difficulties of this scenario). Retail is read but no difficulty claims it.

### findings

- **CG-1 — SOURCE-POLICY RED (undeclared override), bears on task 1.** Symptom: `rental_ext_insurer_extension_days` late-request days ("a request that reached the insurer on the insurer coverage end day itself, inside extension_request_lead_hours, and was decided after it loses those days less one; any other request loses none") decide the same quantity as the inherited base sentence of `rental_evt_extension` ("reaches the insurer at least extension_request_lead_hours hours before the current coverage end; a later request may only cover days from the date of approval"), and the two disagree. Root cause: `overwrite` names only the supplement-days sentence. Evidence: rental.extended.yaml `rental_ext_insurer_extension_days.overwrite[0].superseded_clause` vs base `rental_evt_extension.rule`. Consequence: shown in `1.md`.
- **CG-2 — SOURCE-POLICY RED (undeclared override), bears on task 1.** `rental_ext_self_pay_days_charge` lists `rental_evt_coverage_end` and `rental_evt_rental_days` in `base_policy_refs` but declares only settlement_split's sentence. Base coverage_end "Every rental day starting after the coverage end date is the customer's at the partner rate." prices the self-pay days at partner_daily_rate_usd. Base rental_days "Covered days used are the rental days that start on or before the coverage end date" counts covered days against the coverage end date. The extended rule prices at a discounted self-pay day rate with adjusted weekly blocks and a standing reduction, and counts covered days by authorized days that "reach past the coverage end recorded on the reservation". Consequence: shown in `1.md`.
- **CG-3 — SOURCE-POLICY (inherited provision with no executable path), bears on task 1.** Base `rental_evt_extension` "Every authorization moves the coverage end date by the days authorized." is inherited by both authorization policies (not overwritten), and `rental_coverage_end_update` is a subject of the base policy. Yet no task tool or share tool writes `rental_reservations.coverage_end_date`. The extended self-pay covered-days tier 1 exists only for a recorded end that lags the authorizations, which is the state this inherited sentence forbids. Consequence: shown in `1.md` (it feeds the second reading of CG-2).
- **CG-4 — SOURCE-POLICY (rule/compute filter not in rule), latent.** `prior_claim_delivered = CFIELD('claim','delivered_date', status='closed')` vs rule "had a network insurance claim repair delivered fewer than loyalty_lookback_months calendar months before the credit date". Take a customer whose only network claim repair is `delivered` (not yet `closed`) one month ago. Under the rule that customer is recent. Under compute `prior_claim_recent=False`, which drops them a tier. With several closed repairs, `CFIELD` reads the first row, not any qualifying one. Neither task world exercises it (task 0 has one claim repair, closed); recorded for the charter.
- **CG-5 — SOURCE-POLICY (undeclared deviation from base day counting), latent.** Base `rental_evt_rental_days` "a return no more than return_grace_minutes minutes into a new period does not start it" vs extended priced/rental days "+1 where the return time as counted is later than the pickup time of day" (implemented without grace in time_charge_correction, repair_customer_discount, young_renter_fee, delay_goodwill and self_pay). Example: pickup 08:10, return 08:30. Base counts no new day; compute counts +1. "as counted" may be read to include the grace, in which case compute contradicts the rule instead. Neither task world exercises it (returns at 07:30 vs 08:10 and 08:40 vs 09:15).
- **CG-6 — SOURCE-FACTOR RED (unreal ladders: a tier no customer who reaches the write can occupy, or that cannot reach the result).** Four factors: `time_charge_correction.priced_day_count` (fall-through "no return recorded"), `young_renter_fee.age_span_daily_fee` (tier "older than young_renter_max_age -> zero"), `delay_goodwill.lost_day_time_basis` (fall-through "no time charge -> partner rate"; result capped to 0), and `self_pay_days_charge.selfpay_rental_day_count` (fall-through "no return recorded -> none"; baseline equals tier 2's value instead of the fall-through). Effect on factor counts: time_charge_correction and young_renter_fee each fall to 3 surviving factors (<4) — bears on task 0. delay_goodwill (4) and self_pay (4) stay within bounds, but the struck factors remain unreal ladders — bear on tasks 0 and 1 respectively.
- **CG-7 — SOURCE-FACTOR RED (mislabelled effect).** `network_courtesy_days.window_closing_date` is labelled `method`, but its three tiers only choose which recorded date (return date / today / completion date) enters the same `DAYS(start, close)`. Counts stay within bounds after relabelling. Bears on task 1.
- Observations: O-1 (ordinal wording "after" in two docstrings), O-2 (state_gate names a ledger field, not an eligibility gate), O-3 (vacuous lead-hours conjunct in late-request tier 2), O-4 (block-rate fall-through not stated by the baseline method), O-5 (repair_period_share tiers 1–2 differ only in the date), O-6 (lost_day_fee_basis tier 2 reachable only when the young-renter charge is zero), and the latent compute-scope notes under rule_compute_equivalence.

## closing_checklist

Written 2026-10-11 after both reveals. Everything above this heading was written before any reveal and is left unchanged.

- Per-task files: `0.md` and `1.md` match tasks 0 and 1 one to one, each with a frozen derivation followed by a post-reveal comparison. This is the first revision; no older revisions exist.
- Comparison sections all PASS: **no**.
  - task 0 — SOURCE-FACTOR RED (T0-1, T0-2, T0-3) and SOURCE-TASK RED (T0-4: scored young-renter `days_count` 17 not entailed).
  - task 1 — SOURCE-POLICY RED (T1-1 = CG-1, T1-2 = CG-2/CG-3) and SOURCE-FACTOR RED (T1-3, T1-4).
- Coverage and scopes: all 7 extended policies are covered. Task 0 = {time_charge_correction, repair_customer_discount, young_renter_fee, delay_goodwill}; task 1 = {network_courtesy_days, insurer_extension_days, self_pay_days_charge}. The scopes are pairwise disjoint and jointly complete. Task tools and GT are closed (each `charter_scope.task_tools` equals that tree's target tools). The seven uuid8s are distinct and show no batch pattern.
- Trees:
  - task 0 — 3 prerequisite problems, 3 value_input edges, user-owned root.
  - task 1 — 2 prerequisite problems, 2 value_input edges + 1 state_gate whose ordinals are scored, user-owned root.
  - Both acyclic, and the difficulty graph as a whole is two disjoint DAGs. **Holds.**
- Factors: every declared factor bears weight on its task's world, and every all-baseline number is definite and differs from gold (verified figure for figure against GT). **Does not hold structurally:**
  - CG-6: four factors have a tier no customer reaching the write can occupy. Time_charge_correction and young_renter_fee fall to 3 real factors.
  - CG-7: one mislabelled method.
- Policy: **does not hold**. CG-1 and CG-2/CG-3 are undeclared overrides with demonstrated second readings on task 1. CG-4 and CG-5 are latent rule/compute and base-counting gaps that no task world exercises.
- Instantiation-stage gates on the final form: not re-run by this audit, which runs no gates. The coordinator's snapshot (all green, traceability deferred) is the one cited; it does not detect any finding above.
- Difficulty verdict: **does not pass the source-layer audit.**

Post-reveal addendum (a charter fact noticed while reading `worklog.md`, recorded here rather than in the pre-reveal sections): `self_pay_days_charge.factors[selfpay_pricing_structure].bindings` lists `selfpay_whole_days`, which `selfpay_priced` does not read. The worklog says it was "moved ... to it" so the factor would show record evidence. Likewise `time_charge_correction.factors[time_charge_structure].bindings` lists `corrected_whole_days`, which feeds `corrected_priced_days` (another factor's input). The pricing tier itself rests on the self-pay / priced day count, which does rest on seeded dates, so no weight test changes. Observation O-7.

## revision_2

### charter_global_frozen (revision 2)

- Inputs re-hashed by the auditor: `rental.extended.yaml` `9199ad81c715274f` (changed from `d01e7c79e13a1720`); `task_tools.py` `26ade7605f8dc2ac` (changed from `358e28ceb5898337`); masked views `0.masked.json` `283d1d1b1a82edd1`, `1.masked.json` `5db7c1ab982b833d`. The blueprint base `rental.yaml` is unchanged and the extended base section is still byte-identical to it.
- Both shared inputs changed, so every charter-global section below was re-derived in full rather than carried forward. Round-1 text above is untouched.
- Written before `tasks/*.json` (round 2) or the round-2 `worklog.md` was opened.
- **contamination_disclosure:** the auditor revealed and read round-1 GT (all of `tasks/0.json` and `tasks/1.json` as of round 1, plus the round-1 worklog). Round-2 derivations are therefore not blind to round-1 scored values and conventions. They are recomputed from the revised charter and the revised masked seeds, and every value that moved is tied to a changed rule sentence or seed row, not to recollection.
- Tools: the bodies still only `ctx.create` one `rental_ledger` row each (seven creates; the only other lookup is the extension tool reading `request_reason`). There is still no validation, refusal or hint. Docstrings now define the ordinal as "one more than the highest authorization number already on the rental": **O-1 closed**. The uuid8s are unchanged.

### round-1 items — closure check

| item | round-1 finding | revision-2 state | status |
| --- | --- | --- | --- |
| CG-1 | late-request tier "less one" contradicted base lead-time sentence | late-request days are no longer a ladder. The rule now says "a request that reaches the insurer later may only cover days from the date of approval, so it loses as late-request days the days from the day after the insurer coverage end up to the day before the decision; a request that reached the insurer in time loses none", which follows base `rental_evt_extension`. The compute `MX(0, decision_day - 1 - reach) if (reach - request_day)*24 < lead` matches the rule's "whole days ... at twenty-four hours each" test | **closed** |
| CG-2 | self-pay vs base coverage_end and rental_days covered-days sentences undeclared | both sentences are now named in self_pay `overwrite` with verbatim `replaced_by` sentences of the rule | **closed** |
| CG-3 | inherited "Every authorization moves the coverage end date" with no tool | named and superseded in both courtesy and extension `overwrite` ("it does not itself move the coverage end recorded on the reservation, which only the desk's coverage-end update sets") | **closed**. Residual observation O-8: the "desk's coverage-end update" it names has no tool in this difficulty, but no rule now requires it in either tree |
| CG-4 | `status='closed'` filter not in rule | rule now reads "has a closed network insurance claim repair". Compute is `EXISTS('claim', status='closed')`, so rule and compute agree. The look-back parameter was removed | **closed** |
| CG-5 | grace minutes undeclared | the `rental_evt_rental_days` grace sentence is named in the overwrite of every policy that counts rental days by time of day (time_charge_correction, repair_customer_discount, young_renter_fee, delay_goodwill, self_pay) | **closed** |
| CG-6 (time_charge) | `priced_day_count` fall-through "no return recorded" unoccupiable | factor removed. It was replaced by `remainder_pricing`, **whose fall-through tier is itself a non-tier** (R2-1 below) | **not closed — reappears in a new form** |
| CG-6 (young fee) | `age_span_daily_fee` tier "older than max age -> zero" outside scope | tiers now: <=22 & span>=14 -> fee+5 / <=22 & shorter -> fee+2.50 / other young renter (23–24) -> fee. All three are reachable within the scope "no older than young_renter_max_age" and select distinct values | **closed** |
| CG-6 (goodwill) | `lost_day_time_basis` fall-through "no time charge -> partner rate" capped to zero | fall-through is now "final time charge divided by the days posted on it" (= baseline). **But the scope change makes tiers 2 and 3 unoccupiable at handling time** (R2-2 below) | **not closed — the defect moved within the factor** |
| CG-6 (self-pay) | `selfpay_rental_day_count` fall-through unoccupiable | factor removed. The rental-day count is now a plain rule sentence | **closed** |
| CG-7 | `window_closing_date` labelled method | relabelled `parameter` | **closed** |
| O-1 | "after" in ordinal docstrings | reworded | closed |
| O-2 | state_gate names a ledger field | unchanged | open (observation) |
| O-3 | vacuous lead-hours conjunct | the factor is gone; the lead-time test is now a single rule sentence | closed |
| O-4 | block-rate fall-through not in the baseline method | unchanged (baseline still has no blocks) | open (observation) |
| O-5 | repair_period_share tiers 1–2 differ only by date | unchanged | open (observation) |
| O-6 | lost_day_fee_basis tier 2 reachable only when the young charge is zero | unchanged | open (observation) |
| O-7 | bindings listing an unread input | `time_charge_structure` still binds `corrected_rental_days`, which it reads directly, so that half is resolved. `selfpay_pricing_structure` now binds `selfpay_rental_days`, which `selfpay_priced` does not read | open (observation) |
| latent compute-scope notes | young/goodwill CFIELD on `retail_repair_id='None'`; goodwill scope vs retail-only compute; hold-days tier 1 without completion; courtesy decision not tied to the reviewed submission; "the supplement" unspecified | all CFIELDs are now guarded by `if F('retail_repair_id')` / `if F('claim_repair_id')`; goodwill scope is narrowed to customer-pay repairs; hold-days tier 1 now says "and has a completion date"; courtesy reads the decision by `supplement_number`; the extension supplement is chosen by a stated ladder | closed |

### policy_conflict_scan / rule_compute_equivalence / action_binding / prerequisite graph and sentences (revision 2)

- The seven `(target_tool, computes)` pairs are unchanged and uniquely claimed. The six prerequisite edges are unchanged (same `policy_source` sentences, verbatim in each blocked rule, not restated by the depended-on rule, state form, gates are real bindings, acyclic). The four-point test and single-write resolution from round 1 still hold: same sentences, same writers.
- Every `compute_basis` value is verbatim in its rule (sentence by sentence), and every compute binding has a basis. No rule sentence lacks a binding.
- Override sweep, sentence by sentence, against each `base_policy_refs` entry (refs now add `rental_evt_rental_days` to discount, young fee and goodwill): every conflicting base sentence found in round 1 is now named. No new extended sentence handles a base-governed quantity differently without a declaration. The extension's parts-delay supported days (asked days, capped) and the base "for a parts delay, the business days of the back-order beyond the planned repair days" are compatible: base defines what is asked, and extended takes what was asked.

### factor_ladders (revision 2)

- **time_charge_correction**: time_charge_structure (method), remainder_pricing (method, new), long_rental_block_rate (parameter), standing_extra_day_rate (parameter, warranty; multi-source warranty x closed claim). Baseline.rule: rental days x partner rate (self-sufficient, in rule).
  - `remainder_pricing` tiers: >= weekly_rate_threshold_days remaining -> one more block rate / 1..threshold-1 -> extra-day rate capped at weekly / **"no remainder is charged at partner_daily_rate_usd per remaining day, which is nothing"**. The fall-through condition is "no day remains", and its "method" yields zero by construction. On zero remaining days any per-day method yields zero, so the tier selects no treatment and divides no customers on price. The ladder has two real tiers -> **R2-1**. With it struck, the policy has 3 real factors (<4).
- **repair_customer_discount**: unchanged structure (5 factors; 3 parameter, 2 method).
- **young_renter_fee**: weekly_fee_days (method), age_span_daily_fee (parameter, three live distinct tiers), calibration_hold_days (parameter, adas), booking_reliability_reduction (parameter, estimate; multi-source). 4 real factors.
- **delay_goodwill**: calibration_delay_days (method, adas), goodwill_authority_tier (parameter, warranty; multi-source), lost_day_time_basis (method), lost_day_fee_basis (parameter), delay_goodwill_share (parameter; multi-source). Baseline.rule now values a credited day at "the time charge posted on the final invoice divided by the days posted on it". That is self-sufficient and equals `lost_day_time_basis`'s fall-through.
  - **R2-2:** the rule's scope is now "the network customer-pay repair the rental is tied to". `rental_ext_repair_customer_discount` says "A customer-pay rental tied to a network customer-pay repair receives a repair-customer discount credit", and goodwill's own prerequisite sentence makes the credit "not fixed until the repair-customer discount owed on the time charge stands against it". So at goodwill's handling time a discount credit always stands, and `lost_day_time_basis` is always on tier 1 ("credits stand"). Tier 2 ("no credit stands but a corrected time charge stands") and tier 3 / fall-through ("otherwise") are occupied only if the prerequisite is skipped. In round 1 the scope admitted insurance rentals, where no discount applies, and those tiers were reachable. The factor has one live tier. Goodwill keeps 4 real factors (1 method), so the bound holds, but the factor is not a real ladder.
- **network_courtesy_days**: lost_day_start (method), window_closing_date (parameter), procedure_allowance, alignment_days, insurer_review_days (claim), responsibility_share (multi-source). 1 method, 5 parameter.
- **insurer_extension_days**: supported_days_ground (method), extension_supplement_choice (method, claim; new; tiers latest full approval / latest partial approval / latest submitted — a record-selection rule, accepted as method on the same footing as discount_base_choice), supplement_added_days (parameter, claim; multi-source), supplement_approved_share (parameter, claim). 2 method, 2 parameter. The late-request deduction is now a plain rule sentence, not a factor.
- **self_pay_days_charge**: selfpay_coverage_reach (method), selfpay_pricing_structure (method), repair_status_discount (parameter, claim: on_hold 15 / authorized-in_repair = customer_pay_discount_pct / else 0), network_delay_discount (parameter: >=3 courtesy days 10 / 1–2 5 / none 0), selfpay_standing_reduction (parameter, warranty; multi-source). All tiers are reachable within the scope (repair may be closed or complete; courtesy may be absent). Baseline.rule: rental days less days on or before the recorded end, at partner rate (self-sufficient, in rule).

### findings (revision 2, charter-global)

- **R2-1 — SOURCE-FACTOR RED (bears on task 0).** `rental_ext_time_charge_correction.factors[remainder_pricing]` fall-through "no remainder is charged at partner_daily_rate_usd per remaining day, which is nothing" is a filler tier. Its condition admits only zero remaining days, where every method costs zero. Real tiers: 2. Real factors for the policy: 3 (<4). This is the round-1 CG-6 defect for this policy reappearing in a new factor.
- **R2-2 — SOURCE-FACTOR RED (bears on task 0; bounds hold).** `rental_ext_delay_goodwill.factors[lost_day_time_basis]`: after the scope narrowing to customer-pay repairs, only tier 1 is occupiable at handling time (see factor_ladders). This is new in revision 2 and caused by the rework.
- Observations: O-2, O-4, O-5, O-6, O-7 (self-pay half) remain. New **O-8**: the coverage-end overwrite refers to "the desk's coverage-end update", which no tool of this difficulty performs. No rule in either tree requires it.

### closing_checklist (revision 2)

Written after the revision-2 reveal (2026-10-11 04:33:05 UTC).

- Per-task files: revision 2 is appended to `0.md` and `1.md`; round-1 text is untouched.
- Comparison sections all PASS: **no**.
  - task 0 — SOURCE-FACTOR RED (R2-1, R2-2); policy, tree and unique solution PASS.
  - task 1 — all four relationships PASS.
- Round-1 REDs genuinely closed: CG-1, CG-2, CG-3, CG-4, CG-5, CG-7, T0-2, T0-4, T1-1, T1-2, T1-3, T1-4.
- Not genuinely closed:
  - T0-1 / CG-6 (time_charge) — the dead tier moved into the new `remainder_pricing` fall-through (R2-1);
  - T0-3 / CG-6 (goodwill) — the old dead tier was removed, but the scope narrowing made the factor's other two tiers unoccupiable (R2-2).
- Regressions: R2-2 is caused by the rework (goodwill scope narrowing). No other regression was found: all scored values of task 0 are unchanged, and the task-1 movement (extension 2 -> 1, self-pay 193.68 -> 227.51) is entailed by the revised rule and seed.
- Scopes, tool closure, uuid8s, trees and DAG: unchanged and holding.
- Instantiation gates: the coordinator's revision-2 snapshot (all green, traceability deferred) is cited, not re-run; it does not detect R2-1/R2-2.
- Difficulty verdict (revision 2): **does not pass the source-layer audit** (task 0 SOURCE-FACTOR).

## revision_3

### charter_global_frozen (revision 3)

- Inputs re-hashed: `rental.extended.yaml` `e651c4dfc3edaecd` (changed from round 2 `9199ad81c715274f`); `task_tools.py` `26ade7605f8dc2ac` (unchanged); masked views `283d1d1b1a82edd1` / `5db7c1ab982b833d` (unchanged). The base section is still byte-identical to `blueprint/products/rental.yaml`.
- Because the charter changed, its global sections were re-derived. To do it, the auditor diffed a normalised dump of every extended policy against the round-2 dump (`/tmp/audit_0052_rental/r2_all.txt` vs `r3_dump.txt`). The only differences are in `rental_ext_time_charge_correction` (remainder ladder) and `rental_ext_delay_goodwill` (overwrite replaced_by, rule, compute, factors, baseline, cross_category). The other five policies are unchanged, and so is the tool module. Their revision-2 conclusions therefore carry forward by reference, on the grounds of identical policy text and the unchanged `task_tools.py` hash.
- Written before round-3 `tasks/*.json` or `worklog.md` were opened. **contamination_disclosure:** rounds 1 and 2 GT were revealed earlier, so this revision is not blind to prior scored values. Every value below is recomputed from the round-3 charter and seed.

### round-2 items — closure check

| item | revision-3 state | status |
| --- | --- | --- |
| R2-1 (`remainder_pricing` filler fall-through) | tiers: remainder >= weekly_rate_threshold_days -> one more block rate / 2..threshold-1 -> extra-day rate capped at weekly / "a remainder of a single day, or of none, is charged at partner_daily_rate_usd per remaining day". The fall-through now prices a real one-day remainder at the partner rate (= baseline method). It is distinct from tier 2 (extra-day rate) and from tier 1 (block rate). Rule, compute (`>= 2` boundary), ladder and baseline agree | **closed**. time_charge_correction has 4 real factors (2 method, 2 parameter) |
| R2-2 (`lost_day_time_basis` one live tier) | tiers are now keyed on a **billing-error** credit, not on any credit: BE credit stands -> (final - all credits) / rental days; no BE credit but a corrected time charge stands -> (corrected - credits) / corrected days; otherwise -> (final - credits) / posted days (= baseline). On customer-pay rentals tied to a customer-pay repair, a BE credit stands only where the partner over-posted, and a corrected invoice may or may not exist, so all three tiers can be occupied at the goodwill handling time | **closed** |
| O-6 (fee-value tier 2 reachable only with a zero charge) | lost-day fee value is now a plain rule sentence, "the young-renter charge standing on the rental divided by the rental days, or zero where no young-renter charge stands", with no class-fee tier. The prerequisite effect is reworded to "instead of zero" | **closed** |
| O-2, O-4, O-5, O-7 (self-pay half), O-8 | unchanged | open (observations) |

### revision-3 checks of the changed text

- Every `compute_basis` value is verbatim in its rule; every compute binding has a basis; every `baseline.rule` sentence is in the rule; every overwrite `superseded_clause` is verbatim in base, and every `replaced_by` is verbatim in the rule. Both goodwill prerequisite sentences are unchanged and verbatim.
- Goodwill `overwrite` now replaces the base goodwill cap with a formula including "by one hundred plus the program uplift". It is declared; base "Credits ... never exceed it" is still honoured by the standing-time-charge cap.
- New goodwill factor `program_uplift` (parameter): military -> tier military_discount_pct / returning_customer -> tier returning_customer_discount_pct / else 0. The three values are distinct and reachable. It reads retail (no difficulty claims retail), so `cross_difficulty: null` is honest. Goodwill now has 5 factors (3 parameter, 2 method) and keeps its cross-difficulty factors (calibration_delay_days adas, goodwill_authority_tier warranty) and multi-source factors (authority, share).
- New goodwill baseline.rule values a credited day at "(final time charge less every standing credit) / days posted on the time charge, plus the lost-day fee value", times share_standard. Every sentence is in the rule, and a definite number results.
- Observation **O-9:** `lost_day_time_basis` tiers 1 and 3 differ only in the divisor (rental days vs posted days), while tier 2 changes the base amount. The method label rests on tier 2. This is the same footing as O-5 and is not a RED.

### findings (revision 3, charter-global)

- No RED. R2-1 and R2-2 are closed; O-6 is closed. Open observations: O-2, O-4, O-5, O-7 (self-pay binding), O-8, O-9.

### closing_checklist (revision 3)

Written after the revision-3 reveal (2026-10-11 05:29:17 UTC).

- Per-task files carry revision_3 sections appended after revisions 1 and 2. Older text is untouched.
- Every comparison section carries PASS: task 0 PASS on all four relationships, and task 1 PASS on all four relationships.
- All seven extended policies are covered. The scopes are disjoint and jointly complete: task 0 = time_charge_correction, repair_customer_discount, young_renter_fee, delay_goodwill; task 1 = network_courtesy_days, insurer_extension_days, self_pay_days_charge. Task tools and GT are closed. The seven uuid8s are independent and unchanged.
- Trees:
  - task 0 — 3 prerequisites, 3 value_input edges.
  - task 1 — 2 prerequisites, 2 value_input edges plus a state_gate that is scored through the ordinals.
  - Both roots are user-owned; both graphs are acyclic, and so is the difficulty graph as a whole.
- Every computation has a self-sufficient baseline and 4–6 real factors:
  - billing-error 4, discount 5, young fee 4, goodwill 5;
  - courtesy 6, extension 4, self-pay 5.
  - Each has at least 2 parameter and 1 method factor, and each task has at least one multi-source and one cross-difficulty factor.
  - Every factor bears weight on its world, and every all-baseline number is definite and differs from gold (verified figure for figure against GT).
- Every round-1 and round-2 RED is closed: CG-1…CG-7, T0-1…T0-4, T1-1…T1-4, R2-1, R2-2.
- Open observations (not grounds for rework): O-2, O-4, O-5, O-7 (self-pay binding), O-8, O-9, T1-O1, T1-O2.
- Instantiation gates: the coordinator's round-3 snapshot (all green; traceability deferred to the KB step) is cited, not re-run by this audit.
- **Difficulty verdict (revision 3): passes the source-layer audit.**
