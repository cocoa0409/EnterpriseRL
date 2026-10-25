# Policy-task audit — service_repair_orders / charter-global

## revision_1

## charter_global_frozen

- Frozen: 2026-10-22T03:15Z, auditor: independent policy-task auditor (erl-task-policy-audit), round r1.
- Freeze hashes (sha256, 16-char prefixes): `service.extended.yaml` c1dc8dc420b9dc60, `task_tools.py` 648efe31e7cbf755, `blueprint/products/service.yaml` ee20b42232b383e1. These match the coordinator's gate snapshot (c1dc8dc420b9 / 648efe31e7cb).
- Base copy: `diff blueprint/products/service.yaml <(sed -n 1,846p service.extended.yaml)` is empty, so the base section is a verbatim copy.
- Read for this section: blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml (the service charter, plus maintenance/vsc/purchase only for seeded-row realism), service.extended.yaml, task_tools.py, audits/render_source/XF_recipe.md, and the erlbench DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS / within_months / LATEST / CFIELD).
- Masked and not read: tasks/*.json, plan.md, worklog.md (both scenario-level and difficulty-level), and every other audit. The probes below were run on scratch copies of the masked views under /tmp/audit_service_repair_orders_0075/. No GT-derived content is in this section.
- Entry conditions: the gate snapshot (7 gates green) and the masked-view hashes came with the brief. The view hashes match (0.view c6ff391b0aa9ede5…, 1.view aa6dbbc2d60c3746…). Input is complete.

Policy abbreviations used throughout:
EOC = service_ext_estimate_overage_credit, PRP = service_ext_paid_ro_points, MEPE = service_ext_month_end_points_expiry, OPR = service_ext_owner_points_redemption, CLC = service_ext_comeback_labor_credit, EPD = service_ext_early_payment_discount, REE = service_ext_repeat_repair_estimate, DGC = service_ext_diagnostic_credit.

### policy_conflict_scan

- Subjects and targets: there are 8 extended policies and 8 distinct target tools. Five of them write `service_line_credited` with distinct `credit_reason`s: estimate_overage (EOC), comeback_repair (CLC), early_payment_discount (EPD), diagnostic_applied_to_repair (DGC), and rewards_redemption (OPR, through the redemption trigger). The other three write points_earned (PRP), points_expired (MEPE) and a repair authorization (REE). No two policies write the same credit_reason or event.
- Overlapping scopes are separated by account type:
  - EOC is retail only, and its overwrite says so.
  - CLC, EPD and DGC are fleet only, and their overwrites say so.
  - PRP, MEPE and OPR cover retail rewards accounts.
  - REE has no scope restriction.
  The scope sentences are stated, but the computes do not respect them in three policies. See finding C-1.
- Cross-reads between policies form chains:
  - PRP reads EOC's credits (paid_credits).
  - OPR reads the points balance that PRP and MEPE move.
  - EPD reads CLC's credits (invoice_credits).
  - DGC reads EPD's and CLC's credits (spend_12m) and REE's authorization.
  Each read is declared as a prerequisite edge, so there are no undeclared couplings among the 8. Base clauses that still apply to every account (comeback parts not billed; diagnostic window and once-only rules; waived-when-covered; coverage priority) still bear on these policies. See C-4.
- Time anchors:
  - EOC, PRP, CLC and EPD all select "the repair order of the latest payment received on the account".
  - OPR selects the RO of the latest labor charge.
  - REE and DGC select the latest diagnostic fee.
  - No policy states a same-day tie rule for any of these selectors (C-7d).
- Claimed scopes of the M=2 tasks (inferred from the trees the policy walks out of each world; checked against GT after the reveal):
  - Task 0 has EOC, PRP, MEPE and OPR.
  - Task 1 has CLC, EPD, REE and DGC.
  - The two sets are disjoint and together cover all 8 extended policies.

### rule_compute_equivalence

Two automated sweeps passed:
- Every `compute_basis` value is a verbatim substring of its policy's `rule` (scratch script mech.py).
- Every sentence of every `baseline.rule` is verbatim in the rule.

Every factor ladder tier appears both in the rule and in the `decides` binding, and every branch of each binding is a tier the rule states.

Places where the two faces diverge (rule promise without compute, or compute basis without a rule) are given as findings C-7(a–c) and C-10. In summary:
- PRP's rule says it "sets the points a repair order earns when it is paid in full", but the compute never tests paid-in-full.
- CLC's rule says the credit "is owed only for a repeat that the store's repair warranty covers", but the compute never tests the warranty months or miles. The only test is `original_ro != paid_ro`.
- DGC's rule says the credit "is given only when an authorized decision on the line falls within diagnostic_credit_window_days", but the compute tests only the latest authorized decision.
- DGC and EPD say "within the last twelve whole months", and no counting convention for that phrase is stated in either rule. The compute uses rolling `within_months=12` (0 <= MONTHS(d, today) < 12). MEPE's own definition ("a whole month is complete on the same day of the following month") is in MEPE's rule only.
- REE declares the param `rate_lock_months: 36`, and neither the rule nor the compute uses it. This is an observation.

Rounding convention: every RND or int placement matches its rule's rounding sentence. Each is rounded once at the end, and PRP's "the fraction is dropped" maps to int().

### action_binding_and_uuids

- `(target_tool, computes)` pairs, one per policy, all unique:
  - credit_estimate_overage_3db3cf5c / credit_amount
  - credit_paid_ro_points_b77dd6a9 / points
  - expire_owner_points_a6cb3dc9 / points
  - redeem_owner_points_3e3ce956 / credit_amount
  - credit_comeback_labor_f15915d4 / credit_amount
  - credit_early_payment_discount_b0e7362c / credit_amount
  - authorize_repair_estimate_690e2aa2 / estimate_amount
  - credit_diagnostic_fee_eae01e67 / credit_amount
- The eight uuid8 values share no prefix or sequence pattern and none is reused. Nothing suggests batch derivation.
- No factor id is a substring of any tool name (recipe 7, mechanical check).
- Owners: redeem_owner_points and authorize_repair_estimate are `owner="user"`; the other six are `owner="agent"`.
- Bodies: no tool checks eligibility, prerequisites or amounts; each one only creates its row and updates the balance. No tool judges a prerequisite.
- Triggers (recipe 18): redeem books the points_redeemed row and the rewards_redemption credit it triggers, as the base `triggers` require. No tool writes outside the service category.
- Docstrings:
  - The credit_diagnostic_fee_eae01e67 summary line says "Credits part or all of a diagnostic fee back to the customer **once** the diagnosed repair has been authorized". That is an ordering connective stating the REE→DGC dependency in the tool layer (C-6).
  - Several Args descriptions say "as returned by the service account lookup / repair order ledger lookup **before the call**". These describe where an argument comes from (a read). They state no cross-problem order, so they are an observation.
  - No docstring carries example values. No argument is a composite.
- Subject observation: REE lists `subject: [service_diagnostic_fee_charged]`, but its write is a `service_repair_authorizations` intake row.

### prerequisite_graph

Edges, in the form blocked ← depended-on:
- PRP ← EOC: value_input, gate paid_credits, state form
- OPR ← PRP: value_input, gate points_on_file, state form
- OPR ← MEPE: value_input, gate points_on_file, state form
- EPD ← CLC: value_input, gate invoice_credits, state form
- DGC ← REE: value_input, gate authorized_estimate, state form
- DGC ← EPD: value_input, gate spend_12m, state form

EOC, MEPE, CLC and REE declare `prerequisite: []`.

Checks on the graph:
- Every `problem` is an extended policy id of this file.
- The graph is acyclic: EOC→PRP→OPR, MEPE→OPR, CLC→EPD→DGC, REE→DGC.
- Every `policy_source` is verbatim in the blocked policy's own rule.
- All edges are state form, and none carries a fallback_reason.
- Every `resolved_by` is the depended-on policy's target_tool, and every gate binding exists in the blocked compute.
- No `prerequisite` text uses authoring-viewpoint wording.

Condition fidelity:
- DGC←REE's `condition` adds "dated within diagnostic_credit_window_days calendar days after the diagnosis date", which the policy_source sentence does not carry. The window comes from another sentence of the same rule. Observation.
- OPR←MEPE's `condition` speaks of "aged" points (MEPE's own vocabulary), while its sentence speaks of an "expiry month" (C-5).

### prerequisite_sentences

Four-point test per edge, followed by the derivation from sentence plus records plus the depended-on rule to the resolving write.

- PRP←EOC: "The points for a paid repair order are fixed only after the records carry the overage credit owed on every line of it billed beyond its estimate tolerance."
  - Connective "only after". The state is record-visible: estimate_overage credit rows. It names no tool or id. Its scope is "every line".
  - The only write that brings the state about is credit_estimate_overage. Derivation: read EOC's rule, which reviews the paid RO's line of the latest authorized decision. That gives credit_estimate_overage on that line.
  - Observation: EOC reviews only one line per paid RO. A paid RO with two over-billed lines could never reach "every line". This is not present in either world.
- OPR←PRP: "The redemption credit is fixed only after the records carry the points earned for every repair order on the account that has been paid in full."
  - The test passes. The only write is credit_paid_ro_points.
  - Observation: PRP credits only the latest-paid RO. Any older paid RO without a points row would make the state unreachable. Not present in task 0, where every older paid RO carries points.
- OPR←MEPE: "The redemption credit is not fixed until the records carry the expiry of every point whose expiry month has ended."
  - The sentence admits a second reading (C-5). "Expiry month" belongs to the base clause that MEPE's overwrite retires. MEPE's own rule has no expiry month: a point is "aged" on a day and booked at the month-end run, which is "made on the last day of each calendar month".
- EPD←CLC: "The early-payment discount on an invoice is not fixed until the records carry the comeback credit owed on every repeat repair on that invoice that falls inside the repair warranty."
  - The test passes. The only write is credit_comeback_labor.
  - Derivation: the invoice is the latest-paid RO, and CLC's rule reviews the same RO.
- DGC←REE: "A diagnostic credit is not booked until the records carry the customer's authorized decision on the written estimate for the same concern line."
  - The test passes. The only write is authorize_repair_estimate (owner=user).
  - The same order is also stated in the tool docstring of credit_diagnostic_fee (C-6).
- DGC←EPD: "The diagnostic credit is fixed only after the records carry the early-payment discount owed on every invoice of the account paid in full inside its discount window."
  - The test passes. The only write is credit_early_payment_discount.
  - "its discount window" is EPD's defined term. Reading it as the base early_pay_discount_days (10) is weaker, because EPD's overwrite retires that clause for fleet invoices paid in full. Observation only.

No rule states a cross-problem order outside these edges. The depended-on rules do not restate their dependents' sentences.

### override_declarations

Sentence-by-sentence findings against each `base_policy_refs` entry. Findings only; the consequences are in the task files.

- EOC (refs estimate, diagnostic, payment_terms, rewards, comeback, goodwill):
  - The estimate tolerance/credit clause is overwritten with a self-naming retail scope. The other estimate sentences (authorization before work, fleet pre-authorization, declined lines) are followed.
  - The diagnostic, payment-terms, rewards, comeback and goodwill sentences do not govern the overage quantity and are followed.
  - The owner and late-completion courtesies are rule-keyed concessions booked as estimate_overage, not as base goodwill. Observation.
  - Gap: the out-of-scope (fleet) restatement is not what compute prices (C-1).
- PRP: the earning clause is overwritten. "Points are credited when the repair order is paid in full" is still in force and not computed (C-7a). The expiry, redemption and enrollment-bonus sentences are untouched.
- MEPE: the expiry clause is overwritten. That includes "oldest points used first", which tier 1 of used_points_order departs from, and it is declared. The account-close forfeiture is untouched.
- OPR: the redemption clause is overwritten. "A redemption is credited ... as credit_reason rewards_redemption" and "Tiers whose points_earn_per_usd is 0 neither earn nor redeem points" are followed.
- CLC: the comeback credit clause is overwritten for fleet. These base sentences are retained:
  - "A comeback credit is given only when the repeat repair falls within the repair warranty" is retained and not computed (C-7b).
  - "failures of parts the original repair did not replace are not comebacks" is retained. CLC's selector "the latest customer-pay parts replacement recorded on the same unit" does not test part identity, and no record carries part identity. Observation.
  - Gap: the out-of-scope (retail) restatement is not what compute prices (C-1).
- EPD: the early-payment clause is overwritten. The due-date, late-fee and hold sentences are untouched.
- REE: `overwrite: []`.
  - The parts_warranty_rule has "the parts supplier's warranty paying the rest" of the parts price. That contradicts service_combo_coverage_priority, which is in its refs: "Each concern line is paid under exactly one source ... a line is never split between two sources except for that deductible". This is an undeclared override (C-4).
  - rate_lock_rule prices labor at another store's posted rate, while base service_evt_labor_pricing bills "the posted labor rate of the store that wrote the repair order". That policy is not in REE's refs. The scored quantity is the estimate, not the billed labor, so this is an observation.
- DGC: the diagnostic credit clause is overwritten for fleet. These base sentences are retained:
  - The window, once-only and declined sentences are retained. The window is computed on the latest decision only (C-7c).
  - The waived-when-covered sentence is retained and interacts with C-4.
  - Gap: the out-of-scope (retail) restatement is not what compute prices (C-1).

### factor_ladders

Structure only. Whether each factor bears weight (T1 on a task world) is in each task's `factor_weight`. Every ladder below has 3 pairwise-disjoint tiers including the fall-through. In every policy the fall-through equals the factor's `baseline` and the baseline sentence is in the rule. No `decides` is `result`. Binding sets are disjoint across factors. No factor tier reads another factor's binding, either directly or transitively (recipe A1 holds).

| policy | factor | label | tiers: value or method | multi-source | cross-diff | all-pairs distinguishing input | realism |
|---|---|---|---|---|---|---|---|
| EOC | tenure_tolerance | parameter | 0.05 / 0.075 / P (0.10) | yes (tier + opened_date vs labor date) | — | values distinct | ok |
| EOC | supplemental_decisions | method | SUM / MAX / LATEST of authorized decisions | yes (decisions + labor date) | — | {612.40, 186.54}: 798.94 / 612.40 / 186.54 | ok |
| EOC | owner_overage_courtesy | parameter | 25 / 15 / 0 | yes (deal + tier) | purchase | values distinct | obs: keyed to financing source |
| EOC | late_completion_courtesy | parameter | 20 / 10 / 0 | yes (decision date, labor date, tier) | — | values distinct | ok |
| EOC | supplies_refund | parameter | P(shop_supplies_pct) / 0.5·P / 0 | yes (fee row + tier) | — | Gold 0.06 vs Silver 0.04 vs 0 | obs: refunds supplies on the parts part of the overage; half share for lower tiers |
| PRP | owner_earning_rate | parameter | P+2 / P+1 / P | yes | purchase | distinct | ok |
| PRP | earning_dollars_rule | method | int(total − redemption) / int(labor) / int(total) | yes (credit rows + payment and labor dates) | — | parts>0 or redemption>0 separates each pair | obs: "parts earn nothing" for late payers |
| PRP | shield_labor_bonus | parameter | 2 / 1 / 0 | yes | vsc | distinct | ok |
| PRP | tenure_multiplier_rule | parameter | 1.25 / 1.1 / 1 | yes | — | distinct | ok |
| PRP | visit_frequency_bonus | parameter | 250 / 100 / 0 | yes | — | distinct | obs: counts payments, not visits |
| PRP | care_member_bonus | parameter | 150 / 75 / 0 | yes | maintenance | distinct | ok |
| MEPE | care_plan_extension | parameter | +6 / +3 / 0 | yes | maintenance | distinct | ok |
| MEPE | shield_contract_extension | parameter | +3 / +2 / 0 | yes | vsc | distinct | ok |
| MEPE | used_points_order | method | exp+red−recent / exp+red+returned-RO points / exp+red | yes | — | recent>0 or returned points>0 | obs: tier 2 limited to below Gold |
| MEPE | long_member_reserve | parameter | 500 / 250 / 0 | yes | — | distinct | ok |
| OPR | tenure_point_value | parameter | 0.0125 / 0.011 / P | yes | — | distinct | ok |
| OPR | owner_vehicle_bonus | parameter | 0.15 / 0.10 / 0 | yes (deal + plan) | purchase, maintenance | distinct | ok |
| OPR | shield_holder_bonus | parameter | 0.05 / 0.03 / 0 | yes | vsc | distinct | ok |
| OPR | held_points_rule | method | bal−1000 (floor 0) / bal−enrollment bonus / bal | yes | — | bonus ≠ 1000 | ok |
| OPR | home_store_redemption_credit | parameter | 10 / 5 / 0 | yes | — | distinct | ok |
| OPR | frequent_visit_redemption_credit | parameter | 15 / 8 / 0 | yes | — | distinct | obs: counts payments |
| CLC | aged_repair_share | parameter | 0.7 / 0.8 / P (1.0) | no (dates only) | — | distinct | obs: prorates the store's own 12/12 warranty |
| CLC | original_store_basis | method | original labor / min(repeat, original) / repeat labor | yes | — | **tier 1 vs tier 2: none.** On tier 2's domain (repeat > original), min(repeat, original) = original labor, which is exactly tier 1's method. → C-3 | — |
| CLC | wear_deduction_rule | parameter | 0.15 / 0.05 / 0 | yes | maintenance | distinct | obs: deducts for miles inside the warranty's own mileage limit |
| CLC | declined_work_share | parameter | 0.85 / 0.90 / 1 | no (one table) | — | distinct | obs |
| CLC | duty_share_rule | parameter | 0.95 / 0.90 / 1 | yes | purchase | distinct | **RED C-8** |
| EPD | ach_window_rule | parameter | 15 / 12 / P (10) | yes | — | distinct | ok |
| EPD | fleet_deal_rate | parameter | 0.025 / 0.015 / P | yes | purchase | distinct | ok |
| EPD | prompt_payer_addition | parameter | +0.005 / +0.0025 / 0 | yes | — | distinct | obs: counts payments, not prompt payments |
| EPD | account_tenure_addition | parameter | +0.005 / +0.0025 / 0 | yes | — | distinct | ok |
| EPD | discountable_base_rule | method | labor−cr / labor+parts+supplies−cr / labor+parts−cr | yes (payment row + plan) | maintenance | parts>0 / supplies>0 | obs: a Care plan widens the discount base |
| EPD | payment_standing_share | parameter | 0.5 / 0 / 1 | yes | — | distinct | ok |
| REE | rate_lock_rule | method | earlier rate / min(two rates) / diag rate | yes (two stores + home) | — | est<prior, prior<est | ok |
| REE | diagnosis_overlap_hours | method | latest−diag / sum−diag / latest | yes | — | ≥2 labor rows | ok |
| REE | repeat_labor_allowance | parameter | 0.5 / 0.75 / 1 | yes (dates + odometers) | — | distinct | ok |
| REE | maintained_vehicle_allowance | parameter | 0.9 / 0.8 / 1 | yes | maintenance | distinct | ok |
| REE | parts_price_index | parameter | +0.06 / +0.03 / 0 | no (dates) | — | distinct | obs: indexes the old list price instead of quoting the current one |
| REE | parts_warranty_rule | parameter | 0.5 / 0.75 / 1 | yes | — | distinct | **RED C-8 / C-4** |
| DGC | spend_scaled_share | method | pct·spend/15000 / pct·estimate/1500 / pct | yes | — | different inputs | obs: pro-rates by spend |
| DGC | away_store_share_rule | parameter | 0.9 / 0.75 / 1 | yes | maintenance | distinct | obs: penalises a group-wide account at another group store |
| DGC | decision_speed_share | parameter | 0.5 / 0.75 / 1 | no (dates) | — | distinct | ok |
| DGC | diagnostic_standing_share | parameter | 0.75 / 0.5 / 1 | yes | — | distinct | ok |

Counts per policy as declared:
- EOC: 5 factors (4 parameter, 1 method).
- PRP: 6 (5 parameter, 1 method).
- MEPE: 4 (3 parameter, 1 method).
- OPR: 6 (5 parameter, 1 method).
- CLC: 5 (4 parameter, 1 method).
- EPD: 6 (5 parameter, 1 method).
- REE: 6 (4 parameter, 2 method).
- DGC: 4 (3 parameter, 1 method).

Counts after the tests strike C-3 and C-8:
- CLC loses original_store_basis (its only method) and duty_share_rule. It keeps 3 parameter factors and **no method**, which is below both the 4-factor floor and the 1-method floor.
- REE loses parts_warranty_rule and keeps 5 (3 parameter, 2 method).
- Every other policy is unchanged.

Every task-level set of computations has a multi-source factor and a cross-difficulty factor:
- Task 0's policies read purchase, vsc and maintenance.
- Task 1's policies read purchase and maintenance.

T2 (recipe A6): for every factor there is a producible world where it alone moves the result while every other factor sits at baseline. Examples:
- EOC's courtesy factors move whenever the baseline overage is above zero.
- EPD's factors move whenever the payment arrives inside the baseline window of 10 days.
- OPR's and PRP's factors move whenever their caps (points_max_redemption_pct_of_ro, max_points_per_ro) do not bind.

No factor is min-of-caps gated.

Method shape (recipe A5): every method factor except CLC original_store_basis changes the formula shape (an added or removed input, a min pick, a different base). Parameter factors only select values.

### xf_recipe_sweep

| recipe point | result |
|---|---|
| A1 independence | holds (above) |
| A2 shared selections stated once | holds |
| A3 generic assembly | **fails in all 8 policies (C-2)** |
| A4 single-factor quantity not in the baseline | **fails in EOC, REE and DGC (C-9)** |
| A5 method shape / all-pairs | **fails in CLC original_store_basis (C-3)** |
| A6 T1/T2 | T2 holds for all factors. T1 is per task (task files). |
| A7 factor id ⊄ tool name | holds |
| B8 two-way rule/compute | **fails (C-7a–c, C-10)** |
| B9 probes (decoys, ties, month conventions) | **fails (C-7, C-10)**. Probe table below. |
| B10 compute_basis verbatim | holds |
| B11 no framing clause asserting an absent fact | Observations: REE "the parts supplier's warranty paying the rest" (no record; folded into C-4); EOC "returning the supplies charged on the over-billed work" (the overage includes parts, and supplies are charged on labor only) |
| B12 DSL routes | CFIELD reads are keyed on vehicle_id plus status, or on status alone, and each is single-holding in both worlds. Out-of-scope pricing **fails (C-1)**. |
| C13 overwrite scope and restatement | The scope sentences self-name. EOC, CLC and DGC compute their out-of-scope cases differently from the restated base (C-1). There are no sibling overwrites of one clause. |
| C14 no undeclared departure | **fails in REE (C-4)**. OPR's prerequisite sentence relies on a concept from a clause MEPE retired (C-5). |
| D15 prerequisite sentences as record tests | **fails at OPR←MEPE (C-5)** |
| D16 owed-at-once writes | Neither world has another write owed at once that would move a read. Task 0: the RO 262107 diagnostic credit is already booked, no other line is over-billed and no RO qualifies as a CLC repeat. Task 1: no past-due invoice, no other over-billed line, and no other in-window invoice. The two LATEST(payment) selectors would move if a payment were posted mid-call, but no tool posts payments. |
| E17 docstrings | **fails at DGC tool, "once" (C-6)** |
| E18 trigger rule | holds |
| E19 money rows > 0 | holds in the seeds and in the tool contracts |
| E20 cross-category seeded rows | Both worlds checked against the owning charters. Plus 6-Visit plan 521.55 = 549 × 0.95 (bundled). Fleet 12-Visit 1029.00, with 2 plans below the 10-plan volume threshold. Select 2195 ≤ 3295; Exclusionary 2895 ≤ 4495. Terms and expiration odometers recomputed. The Silverado diesel plan is diesel-eligible. Ages and odometers are within limits. Financing enums are valid. Holds. |
| F22–25 realism | **fails at CLC duty_share_rule and REE parts_warranty_rule (C-8)**. Other doubtful tiers are recorded as observations in the table above. |
| G26 proof text | GT side, checked after the reveal |

Probe table (scratch copies, /tmp/audit_service_repair_orders_0075/probes.py):

| read | decoy or edge case | outcome |
|---|---|---|
| PRP paid_ro = LATEST(payment) | the latest payment is taken back (returned) | compute still credits 5108 points on task-0 RO 262107; the rule says points only when paid in full → C-7a |
| CLC original repair | original 15 months before the repeat (outside the 12-month warranty) | compute 503.39; rule "owed only for a repeat that the store's repair warranty covers" → 0 → C-7b |
| DGC decision | an in-window authorized decision followed by a later out-of-window one | compute 0; the rule ("an authorized decision on the line falls within") grants a credit → C-7c |
| LATEST(payment) in EPD, EOC, PRP, CLC | two payments on the same latest day for different ROs | paid_ro flips with row order (RO 261030 vs RO 261019); no tie rule is stated → C-7d |
| CFIELD purchase/vsc/maintenance | cancelled, expired or unwound decoy | excluded by the status filters; absent → None → fall-through tier (stated) |
| EOC / CLC / DGC out of scope | Net-15 account (EOC), Gold account (CLC, DGC) | EOC 49.86 vs base 38.89; CLC 605.59 vs base 832.66; DGC 79.98 vs base 165.00 → C-1 |
| "last twelve whole months" (DGC, EPD) | rolling vs complete calendar months | task 1 DGC 76.75 vs 79.98 → C-10 |
| OPR enrollment bonus `repair_order_number=''` | bonus row stored with null RO | SUM over '' would miss a null-RO row. Neither world has an enrollment row. Observation. |

### findings

Each finding lists every member found in one pass.

**C-1 SOURCE-POLICY — out-of-scope worlds are priced differently from the restated base (recipe B12/C13).** Bears on: tasks 0 and 1 by charter. No direct consequence in either world, because task 0 is Gold (in EOC's scope) and task 1 is Net 30 (in CLC's and DGC's scope).
- EOC.
  - Rule s1: "on any other account the customer-pay labor and parts billed ... may still exceed the authorized estimate_amount by at most estimate_overage_tolerance_pct of it, and anything billed beyond that tolerance ... is credited back".
  - Rule, later sentences: "where it closed more than late_close_days calendar days after and the account is at another tier, late_close_other dollars are added" and "at another tier, the overage is increased by supplies_refund_share_other of the tier's shop_supplies_pct".
  - The compute applies these to fleet accounts (`not upper_tier`). A Net-15 copy of the task-0 world gives 49.86, against 38.89 under the restated base.
- CLC.
  - s1: "on any other account the labor is credited at comeback_labor_covered_pct ... pointing at the repeat labor row".
  - The covered share, credit basis, wear and declined-work ladders carry no fleet condition. A Gold copy of the task-1 world gives 605.59 against the base 1.0 × 832.66 = 832.66.
- DGC.
  - s1: "on any other account ... the diagnostic fee is still credited at diagnostic_credit_pct".
  - The spend, away-store, decision and standing ladders carry no fleet condition. A Gold copy gives 79.98 against the base 165.00.
- Root cause: the scope sentence restricts the policy, but the compute and the unconditioned ladder sentences price every account.
- Affected: EOC rule and compute (late_close_courtesy, supplies_refund_rate); CLC rule and compute (covered_share, credit_basis, wear_deduction, declined_share); DGC rule and compute (credit_share, away_share, decision_share, standing_share).

**C-2 SOURCE-POLICY — the assembly sentences name factor quantities (recipe A3).** Members: all 8 policies. Their `result` sentences:
- EOC: "then it is increased by the shop supplies refund; then, only where that overage is above zero, the owner courtesy and the late completion courtesy are added". This also gates two factors on a quantity that two other factors move.
- PRP: "the earning rate times the earning dollars and the service contract labor bonus ... the tenure multiplier ... the visit bonus and the Kessler Care member bonus".
- MEPE: "the aged points under the lengthened expiry period ... then the protected reserve is taken off".
- OPR: "the owner redemption bonus and the service contract bonus ... the home store credit and the frequent visit credit".
- CLC: "reduced by the wear deduction; then it is multiplied by the declined-work share and by the duty share".
- EPD: "the discount rate and the two additions ... the discount standing share".
- REE: "the repeat allowance and the maintained-vehicle allowance ... the parts price index ... the parts warranty share".
- DGC: "the away-store share, the decision share and the diagnostic standing share".

Consequence: the assembly order is load-bearing in every policy that does not commute: EOC's overage>0 gate, PRP's int() between the multiplier and the additions, OPR's cap after the additions, MEPE's floor. It cannot be put in the baseline computation document without naming factors, and it cannot be dropped without changing the number. So a renderer either leaks each factor into the computation document or loses the order.

**C-3 SOURCE-FACTOR — two tiers of CLC original_store_basis select the same method (recipe A5).** Bears on: task 1.
- Tier 1, "where the original repair was written at a different store ... the basis is the original repair's labor charge".
- Tier 2, "where both were written at the same store and the repeat labor charge is larger than the original labor charge, the basis is the lesser of the two". Tier 2's own condition makes the lesser of the two the original labor charge.
- Both tiers therefore select "original labor charge". No input distinguishes the pair.
- Consequence: CLC loses its only method factor and fails the 1-method and 4-factor floors once C-8 is also applied.
- Affected: CLC rule, factors[original_store_basis], compute credit_basis.

**C-4 SOURCE-POLICY — REE splits a line between customer pay and a warranty without declaring an override (check 1, recipe C14).** Bears on: task 1.
- REE rule: "the indexed parts price is multiplied by parts_warranty_share_home, the parts supplier's warranty paying the rest".
- service_combo_coverage_priority, which is in REE's base_policy_refs, says: "Each concern line is paid under exactly one source ... an in-force manufacturer or dealer warranty coverage that covers the component ... a line is never split between two sources except for that deductible".
- REE has `overwrite: []`.
- In the same situation (a repeat within 24 months of the earlier part), the base gives either a wholly covered line or a wholly customer-pay line. REE gives customer pay on 50% or 75% of the parts.
- Second effect: base service_evt_diagnostic, which DGC does not overwrite, says "Where diagnostic_fee_waived_when_covered is true and the diagnosed failure is then repaired under a recall, the manufacturer warranty or a service contract ... a fee already posted for that line is credited in full". The asserted warranty share gives that clause a reading.
- The asserted supplier warranty exists in no record (recipe B11).
- Affected: REE rule, factors[parts_warranty_rule], compute parts_warranty_share; and DGC's result in task 1.

**C-5 SOURCE-POLICY — the OPR←MEPE prerequisite sentence admits a second reading (checks 6/7, recipe D15/C14).** Bears on: task 0.
- The sentence: "The redemption credit is not fixed until the records carry the expiry of every point whose expiry month has ended."
- "Expiry month" is the concept of the base clause "Points expire at the end of the calendar month that is points_expiry_months after the month they were earned", which MEPE's overwrite retires for the month-end expiry of open retail rewards accounts.
- MEPE's own rule has no expiry month. A point is "aged once more than the expiry period has passed since the date it was earned, counted in whole months", and expiries are booked at the run "made on the last day of each calendar month".
- The edge's `condition` uses MEPE's vocabulary ("no aged point remains"), while its sentence does not.
- Readings:
  - Reader A: the run due today must be booked first.
  - Reader B: the expiry month has not ended (it is the last day of the month, before month end), or under the base reading it is a different set of months. Either way the waited-on state differs from what MEPE's write produces.
- The task-0 file demonstrates the second answer.

**C-6 SOURCE-POLICY — the DGC tool docstring states the REE→DGC order (check 3, recipe E17).** Bears on: task 1.
- The docstring of credit_diagnostic_fee_eae01e67: "Credits part or all of a diagnostic fee back to the customer once the diagnosed repair has been authorized."
- "once" is an ordering connective. The dependency becomes discoverable from the tool list without reading DGC's rule, which moves part of the tree's discovery into the tool layer.

**C-7 SOURCE-POLICY — rule promises that the compute does not carry, found by probes (recipes B8/B9).** Members:
- (a) PRP: "this policy sets the points a repair order earns when it is paid in full" and base "Points are credited when the repair order is paid in full". The compute never tests paid-in-full. Probe: with the latest payment taken back, task-0 RO 262107 still earns 5108 points, where the rule gives none.
- (b) CLC: "it is owed only for a repeat that the store's repair warranty covers". The compute tests only `original_ro != paid_ro`. Probe: an original repair 15 months earlier gives 503.39, where the rule gives 0. The ≥9-month tier has no upper bound.
- (c) DGC: "is given only when an authorized decision on the line falls within diagnostic_credit_window_days". The compute uses only the latest authorized decision's date. Probe: an in-window decision followed by a later out-of-window decision gives 0, where the rule gives a credit.
- (d) No policy states a same-day tie rule for its LATEST selectors:
  - EOC: paid_ro, line_reviewed, line_vehicle
  - PRP: paid_ro, paid_vehicle
  - OPR: open_ro, redeeming_vehicle, open_ro_store
  - CLC: paid_ro, original_*
  - EPD: paid_ro, payment_method
  - REE: est_*, prior_*
  - DGC: diag_*, authorized_estimate
  
  Probe: two payments on the same latest day flip EPD's paid_ro with row order. Neither task world contains a tie on a selector it uses, so there is no per-task consequence.

**C-8 SOURCE-FACTOR — tiers no franchised dealer would publish (recipe F22).** Members:
- CLC duty_share_rule cuts the store's own workmanship comeback credit to 0.95 or 0.90 when the unit was bought from the group under a Fleet Vehicle Purchase Agreement, graduated by the account's net-terms tier.
  - Whether the dealer itself sold the unit, and the customer's credit terms, are not conditions a dealer weighs when honouring its own repair warranty.
  - The same condition earns a better early-payment rate in EPD (fleet_deal_rate), which shows it is a loyalty marker, not a cause of failure.
  - Bears on task 1.
- REE parts_warranty_rule makes the customer pay 50% of a repeated part when the earlier repair was at the home store and 75% when it was at another group store, with "the parts supplier's warranty paying the rest".
  - A supplier's or OEM parts warranty does not vary with which group store installed the part.
  - A covered part is not split with the customer (see C-4).
  - Bears on task 1.

**C-9 SOURCE-POLICY — the baseline names a quantity that only one factor uses (recipe A4).** Members:
- EOC baseline: "and the vehicle is the vehicle on the line's labor charge". Only owner_overage_courtesy reads it.
- REE baseline: "its store ... are those on that diagnostic fee". Only rate_lock_rule reads it.
- DGC baseline: "and the unit is the vehicle on it". Only away_store_share_rule reads it.

Consequence: the computation document must carry a selector that only points at a factor. Bears on: tasks 0 (EOC) and 1 (REE, DGC).

**C-10 SOURCE-POLICY — "within the last twelve whole months" has no stated counting convention (checks 2/B9).** Members:
- DGC spend_12m ("customer-pay labor and parts charges dated within the last twelve whole months less the ... credits dated within those months") and DGC standing_share.
- EPD prompt_payer_addition and payment_standing_share.

The compute uses rolling within_months=12. The equally natural reading is "the last twelve complete calendar months", which excludes the current month. MEPE's definition of a whole month is in MEPE's rule only. Bears on: task 1, where it changes the scored value (see 1.md).

Observations (not grounds for rework):
- REE `rate_lock_months` is declared and unused.
- REE's subject is service_diagnostic_fee_charged.
- PRP←EOC and OPR←PRP each wait on "every" line or RO while the depended-on policy reviews only one per call.
- "before the call" appears in Args provenance text.
- OPR consumes every redeemable point even when the cap binds. Neither world has a binding cap.
- The doubtful-realism tiers marked "obs" in the factor_ladders table.
- CLC's original-repair selector does not test part identity.
- The DGC←REE condition adds the window.

## closing_checklist

Written after the reveals of both tasks (2026-10-22T03:21Z). Nothing above this heading was changed after a reveal.

- Audit files: 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json, with _difficulty.md alongside. This is revision_1 and there is no older revision.
- Comparisons do not pass:
  - Task 0 is RED: C-5 demonstrated, plus wrong tier_taken proof text.
  - Task 1 is RED: C-3/C-8 strip CLC below the factor floors; C-4 demonstrated; C-10 demonstrated; C-6 bears on the tree.
- Coverage: the 8 extended policies split 4 + 4, the scopes are pairwise disjoint and cover the charter, and the tools and GT are closed. The uuid8s are independent.
- Trees: each has 3 prerequisite problems and 3 value_input edges, one user-owned write (OPR in task 0, REE in task 1), and no cycle. The difficulty-wide graph is a DAG.
- Factors: every factor bears weight on its world against an honest baseline, and both all-baseline figures are definite and differ from gold. The ladder-structure and realism failures are C-3 and C-8, and CLC falls below the floors.
- Gates were not re-run: Step 4 runs them only on a final form after all four relationships PASS, and they do not. The difficulty is **not closed**.

Charter RED ids (findings above):
- C-1 out-of-scope pricing in EOC, CLC, DGC.
- C-2 assembly sentences name factor quantities, in all 8 policies.
- C-3 CLC original_store_basis tiers 1 and 2 are identical.
- C-4 REE's undeclared split of a line against coverage priority.
- C-5 the OPR←MEPE prerequisite sentence's second reading.
- C-6 the DGC tool docstring's "once".
- C-7 rule promises not computed: PRP paid-in-full, the CLC warranty gate, DGC "an authorized decision", unstated LATEST tie rules.
- C-8 unreal tiers: CLC duty_share_rule, REE parts_warranty_rule.
- C-9 baseline names single-factor selectors in EOC, REE, DGC.
- C-10 the "last twelve whole months" convention in DGC and EPD.

VERDICT revision_1: task0=RED task1=RED charter=C-1,C-2,C-3,C-4,C-5,C-6,C-7,C-8,C-9,C-10

## revision_2

### charter_global_frozen (revision_2)

- Frozen: 2026-10-22T05:31Z, before either task's revision-2 GT and before the reworker's worklog claims were read. Auditor: the same independent auditor, round r2.
- Entry gate: the last non-blank line of tasks/service_repair_orders/worklog.md is `REWORK round 2: gates 7/7 green`. The file ends with one trailing empty line.
- Snapshot: ran `/tmp/erl0075_coord/snapshot.sh service_repair_orders 2` at 2026-10-22T05:26:19. Output:
  - r2 views: 0.view c6ff391b0aa9ede5, identical to r1; 1.view e58fbd1b623b86d1.
  - Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
  - sha256 prefixes: service.extended.yaml a79432726f7a, task_tools.py 2c3d279b7ca1, tasks/0.json 6cef0c15c8f2, tasks/1.json c7ed36a6f0ae.
- Both shared inputs changed from r1 (charter c1dc8dc4… → a79432726f7abb75; tools 648efe31… → 2c3d279b7ca16c74). Every charter-global section below is therefore re-derived in full, not carried forward.
- Base copy: still verbatim (diff of the first 846 lines is empty).
- View deltas, r1 → r2:
  - Task 0: none (same frozen_time, persona and initial_state).
  - Task 1: initial_state identical. The persona drops "and that a written estimate is waiting" and changes "approve the written estimate" to "approve the repair estimate".
- contamination_disclosure: to check the gate line I printed the worklog's last 400 bytes. They contained the reworker's revision-2 figures for task 1 (CLC 705.59, EPD 2.84, REE 1739.61→2859.01, DGC 76.03, with skip values) and task 0's unchanged skip values. My revision-2 numbers below come from replaying the charter's DSL on scratch copies of the views (scratch/r2/*.py), not from those figures. Disclosed here and in 1.md.

### closure_of_revision_1_items

Each item was verified against the artifacts, not against any claim.

| r1 id | status | evidence |
|---|---|---|
| C-1 out-of-scope pricing | **closed** | EOC now reads "On every account this policy sets the estimate overage credit" (overwrite and rule), so fleet is in scope; a Net-15 probe gives 49.86, which is the policy's own figure. CLC and DGC compute the restated base on retail: a `fleet_account` branch, "On any other account the credit is the repeat labor charge times comeback_labor_covered_pct ..." and "On any other account the credit is the diagnostic fee times diagnostic_credit_pct ...". Probes: Gold CLC 832.66 = base, Gold DGC 165.00 = base. |
| C-2 assembly names factor quantities | **closed** | All 8 result sentences are now generic ("every rate set out below that increases the overage", "every multiplier set out below", "every share set out below that reduces ..."). They name only baseline quantities: overage, credit basis, covered labor share, discount rate, diagnostic credit share. The order is still fixed where it matters. Observation: "set out below" points downward, while in every rule the factor sentences come before the assembly sentence. |
| C-3 CLC basis tiers identical | **closed as stated** | Tier 2 is now "same store and the posted labor rate on the repeat labor charge differs from the one on the original labor charge → repeat hours at the original rate, less the capped tier discount". Tiers 1, 2 and 3 are pairwise distinct. In task 1 they give 885.36 / (n/a) / 832.66. **But tier 2 is a pure labor-rate swap against tier 3; see N-4.** |
| C-4 REE split line | **closed for the split** | parts_warranty_rule is removed, and so is "the parts supplier's warranty paying the rest". The waived-when-covered side effect goes with it. **A different undeclared conflict of REE with a base clause remains (N-3). It was present in r1 and I missed it there.** |
| C-5 OPR←MEPE "expiry month has ended" | **closed for task 0** | The new sentence is "...records carry the month-end points expiry of the latest calendar month whose last day falls on or before the redemption date." On 2026-10-31 that is October, so the reading is unique. **The new wording creates N-1.** |
| C-6 DGC docstring "once" | **closed** | The docstring now reads "Credits part or all of the diagnostic fee charged on a diagnosed concern line back to the customer." The "before the call" provenance phrases are also gone. |
| C-7(a) PRP paid in full | **closed** | `paid_in_full = ro_balance <= 0.004` gates the result, and the rule states the test. The probe with the payment taken back now gives 0. |
| C-7(b) CLC warranty gate | **closed** | `in_warranty` matches the rule's "on or before the day comeback_warranty_months calendar months after the original repair's line date (that month's last day where it has no such day)" plus the mileage test. Boundary checks: 2026-02-02→2027-02-02 inside, →2027-02-03 outside; 2024-02-29→2025-02-28 inside, →2025-03-01 outside. The 15-month probe gives 0. |
| C-7(c) DGC "an authorized decision" | **closed** | The base window sentence is now declared overwritten "On every account ... the date of the latest authorized decision ..., a later decision superseding an earlier one", and the compute matches. The probe gives 0, as both the rule and the compute now say. |
| C-7(d) tie rules | **closed** | Every rule now states "Wherever a record is chosen as the latest of its kind and two such records share that date, the one listed first in the records counts". That matches LATEST, which keeps the first row in listing order. |
| C-8 duty_share / parts_warranty unreal | **closed** | Both factors are removed. **Their replacement in CLC, downtime_allowance_rule, conflicts with the scenario constitution (N-2).** REE's replacement, parts_volume_discount (5% at ≥10,000 and 3% at ≥5,000 of 12-month customer-pay parts), is a real fleet parts-pricing practice: ok. |
| C-9 baseline single-factor selectors | **closed** | EOC's baseline no longer names the vehicle (now in the owner-courtesy sentence). REE's no longer names the store (now in the rate-lock sentence). DGC's no longer names the unit (now in the away-store sentence). The remaining baseline selectors are each used by two or more factors or by the baseline itself: PRP vehicle, OPR redeeming vehicle, EPD unit, CLC unit. |
| C-10 twelve-whole-months | **closed** | DGC, EPD, PRP, OPR and REE each define "A record falls within the last twelve whole months when fewer than twelve whole months separate its date from [the day ...] ... so records dated on that day count", and every rule states the whole-month/month-end convention. This matches within_months (0 ≤ MONTHS < 12) and MONTHS(). MEPE does the same for "the last whole months named". |

### revision_2_scan (all recipe points on every changed policy; all 8 policies changed)

- Rule ↔ compute: the compute_basis-verbatim sweep and the baseline-in-rule sweep pass for all 8 policies. Every prerequisite policy_source is verbatim in its rule. All rounding sentences say "rounded half up". The compute uses RND (Python round), which differs from half up only on exact binary ties; no scored value lands on a tie (raw values 118.5630, 438.1150000000001, 705.586, 2.836, 2859.010, 76.034). Observation only.
- The factors[].ladder `when` texts are paraphrases. A few still say "within the last twelve months", where the rule now says "whole months":
  - PRP visit_frequency_bonus
  - OPR held_points_rule
  - OPR frequent_visit_redemption_credit
  
  Observation: these texts are not rendered and the rule governs.
- Absent-record branches: each `review_open` (no payment, no labor charge, no diagnostic fee, no earlier repair) matches a stated "Where no ... there is no ..." sentence.
- Factor counts:
  - EOC 5 (1 method), PRP 6 (1), MEPE 4 (1), OPR 6 (1), CLC 5 (1), EPD 6 (1), REE 6 (2), DGC 4 (1).
  - Multi-source and cross-difficulty factors are present in both trees.
  - T2 holds for every factor, including the new downtime_allowance_rule and parts_volume_discount.
- Owed-at-once writes (recipe D16): neither world changed in a way that adds an owed write.
- Seeded rows (recipe E20): unchanged and still consistent with the owning charters.

### findings (revision_2)

Every member found in one pass.

**N-1 SOURCE-POLICY: the new OPR←MEPE wait cannot be met in a month whose run books nothing (checks 6/7).**
- The sentence: "The redemption credit is not fixed until the records carry the month-end points expiry of the latest calendar month whose last day falls on or before the redemption date."
- MEPE's run often owes 0. The task-0 account's own history shows it: runs at April, May, June, August and September 2026 month-ends compute 0 and booked no row (only 2026-03 and 2026-07 rows exist; probe: MEPE at 2026-09-30 = 0). expire_owner_points refuses points ≤ 0 ("Error: points must be a whole number greater than zero").
- So for any redemption dated 2026-10-01 through 2026-10-30 on this same account, the waited-on September entry can never exist. One reading blocks the redemption permanently. The other treats the wait as vacuously met. Two readings, and no resolving write.
- Members: OPR prerequisite[1] policy_source and condition ("The records carry the points-expired entry the month-end run books ..."), the OPR rule sentence, and the expire tool's positive-points check.
- Bears on: charter only. Task 0 is dated 31 October, when the October run owes 3278.

**N-2 SOURCE-POLICY / SOURCE-FACTOR: CLC's new downtime_allowance_rule pays compensation for lost time, which the scenario constitution excludes from every rule.**
- blueprint.yaml (service_repair_orders summary): "a demand for compensation for lost time or a rental the customer arranged elsewhere ... fall[s] outside every rule and go[es] to a human representative as POLICY_NOT_COVERED".
- CLC: "the downtime allowance follows how long the repeat repair kept the unit in the shop: where the repeat labor charge billed at least downtime_hours_long flat-rate hours, downtime_allowance_long dollars are added to the credit ...".
- The same situation (a fleet customer down a unit during a comeback) is POLICY_NOT_COVERED under one text and an automatic +$100 / +$50 under the other.
- The tier also measures "how long the unit stayed in the shop" by billed flat-rate hours, a proxy that no shop-days record backs.
- Members: CLC factor downtime_allowance_rule, its rule sentence, and compute downtime_allowance.
- Bears on: task 1, where the 6.2 h repeat takes the +$100 tier.

**N-3 SOURCE-POLICY: REE prices in-warranty repeats as customer pay, against base service_evt_comeback (undeclared; REE has `overwrite: []`).**
- REE's scope is "a diagnosed concern line whose failure repeats the latest customer-pay parts repair recorded on the same vehicle". It has no repair-warranty exclusion, and its repeat allowance explicitly prices repeats "no more than allowance_months [24] whole months" old.
- Base service_evt_comeback: "A repeat failure of the same repair inside the repair warranty is a comeback ... On a comeback the replacement parts are not billed."
- Probe: the task-1 world with the Silverado's earlier repair moved to 8 months and 6,000 miles before the diagnosis, inside the 12/12,000 fleet warranty. REE prices 2674.94, including parts of 2860 × 0.77. The base gives no parts billed.
- Present in r1; I recorded it in r1 only as an observation, and it is a member of r1's C-4 class.
- Bears on: charter only. In task 1 the earlier repair is 19 whole months old, outside the warranty.

**N-4 SOURCE-FACTOR: method tiers that only swap the labor-rate multiplier (recipe A5 "never swap a multiplier"; skill: a method tier that "only substitute[s] a different number into the same formula (a rate ...)").**
- CLC original_store_basis tier 2 ("repeat labor charge's flat-rate hours at the original labor charge's posted rate, less the tier's labor_discount_pct ... within its cap") against tier 3 (the repeat labor charge = repeat hours × repeat rate less the same discount). The only difference is which posted rate multiplies the hours.
- REE rate_lock_rule tier 1 ("the earlier repair's posted labor rate") against the fall-through ("the posted labor rate on the diagnostic fee"). The same swap. This was present in r1 and I missed it there.

Each factor keeps a shape-changing tier (CLC tier 1: a different base; REE tier 2: a min pick), so the 1-method floors still hold. The listed tiers are still members. Bears on: task 1, where REE's rate_lock tier 1 is the tier taken (158 instead of 165).

**N-5 SOURCE-POLICY (check 3 / recipe E17): tool bodies do not enforce what their docstrings state.**
- `line_letter` is documented as "Enum class — ... one of: A ... H, not_applicable", but no tool checks it, so any string is booked. Five tools: credit_estimate_overage_3db3cf5c, authorize_repair_estimate_690e2aa2, credit_diagnostic_fee_eae01e67, credit_early_payment_discount_b0e7362c, credit_comeback_labor_f15915d4.
- `line_letter` is never cross-checked against the named `source_line_id` row, so a credit can book on line B against a line-A charge. Four credit tools: credit_estimate_overage, credit_diagnostic_fee, credit_early_payment_discount, credit_comeback_labor.
- `points` is documented as "integer, no decimals, no separators". The bodies call `int(points)` before validating, so a malformed value such as "27,541" raises an exception instead of returning the Error string. Three tools: redeem_owner_points_3e3ce956, credit_paid_ro_points_b77dd6a9, expire_owner_points_a6cb3dc9.
- The module docstring says "No tool checks ... amounts", but every money tool now rejects amounts ≤ 0 after rounding: a claimed property the body contradicts.
- Enforced correctly: half-up cent rounding (`_Fmt.cents`) on every money argument, positive amounts and points, the YYYY-MM billing_month, and source_line_id existence and type.
- The uuid8s are unchanged and unique, and no docstring carries an ordering word or an example value.
- Bears on: both tasks' tool sets.

Observations: "set out below" wording; RND vs half-up on exact ties (no scored value affected); ladder `when` paraphrases saying "twelve months"; the realism observations from r1 that still stand (EPD Care-plan supplies base, DGC away-store and spend-scaled shares, PRP payment-count visit bonus, CLC age and wear proration).

### closing_checklist (revision_2)

Written after both revision-2 reveals. Nothing above this heading in revision_2 was changed after a reveal.

- Files: 0.md, 1.md and this file each have a revision_2 section appended. The revision_1 text is untouched.
- Every r1 charter id is closed as stated (table above). Two r1 items were missed in r1 and are reported now as members of their classes: REE's in-warranty conflict (N-3) and REE rate_lock tier 1 (N-4). Nothing regressed on task 0's values.
- New in the rework:
  - N-1 from the C-5 rewording.
  - N-2 from the C-8 replacement factor.
  - N-4 member from the C-3 retier.
  - N-5 from the new tool bodies, which validate some docstring formats but not all.
- Tasks:
  - Task 0 PASS on all four relationships.
  - Task 1 RED: N-2 is demonstrated on its scored values, and N-4 bears on the REE tier it takes.
- Trees: each has 3 value_input edges and one user-owned write, with no cycle, and the difficulty-wide graph is a DAG. Scopes are disjoint and cover the charter. The uuid8s are unchanged and unique.
- Gates were not re-run by the auditor beyond the coordinator snapshot (7/7 OK at 2026-10-22T05:26:19). The difficulty is **not closed**.

Charter RED ids (revision_2):
- N-1 the OPR←MEPE wait cannot be met in a zero-run month.
- N-2 CLC downtime_allowance_rule pays lost-time compensation that blueprint.yaml excludes.
- N-3 REE prices in-warranty repeats against base service_evt_comeback, undeclared.
- N-4 multiplier-swap method tiers: CLC original_store_basis tier 2, REE rate_lock_rule tier 1.
- N-5 tool bodies do not enforce the line_letter enum or the line/source match, and `points` parse failures raise instead of returning an Error string, contrary to the module docstring.

VERDICT revision_2: task0=PASS task1=RED charter=N-1,N-2,N-3,N-4,N-5

## revision_3

### charter_global_frozen (revision_3)

- Frozen: 2026-10-22T06:08Z, before tasks/*.json revision 3 and before the worklog body were read. For the entry gate I read only the worklog's last non-blank line, `REWORK round 3: gates 7/7 green`; nothing else from the worklog was printed.
- Snapshot: ran `/tmp/erl0075_coord/snapshot.sh service_repair_orders 3` at 2026-10-22T06:04:51. Output:
  - r3 views: 0.view c6ff391b0aa9ede5 and 1.view e58fbd1b623b86d1, both identical to r2.
  - Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
  - sha256 prefixes: service.extended.yaml a3c538bc6305, task_tools.py ac881aeff29b, tasks/0.json 87b166c7d389, tasks/1.json 7e31fec6aec2.
- The charter (a79432726f7a… → a3c538bc6305c37f) and the tools (2c3d279b7ca1… → ac881aeff29bf4c6) both changed, so every charter-global section is re-derived. The base copy is still verbatim.
- Policies changed in r3:
  - CLC: basis tier 2 rewritten; downtime_allowance_rule replaced by repeat_fee_refund; owed credits floored at one cent.
  - REE: rate_lock relabelled parameter; in-warranty exclusion added.
  - EPD: returned_payment_share 0 → 0.25; one-cent floor.
  - OPR: MEPE edge now in action form with a fallback_reason.
  - MEPE: "a run that finds no points expiring is made without an entry".
  - PRP: one-point floor.
  - EOC: one-cent floor where the line is over-billed.
  - DGC: REE-edge sentence scoped to repeats outside the warranty.
  - All 8: "set out below" became "this policy sets out"; result expressions now round half up via `RND(x + 0.000001, 2)`.
- contamination_disclosure: none this round.
- Scratch: /tmp/audit_service_repair_orders_0075/r3/ (copies of the r3 charter and tools are kept there).

### closure_of_revision_2_items

| r2 id | status | evidence |
|---|---|---|
| N-1 zero-run months | **closed for zero runs** | The OPR←MEPE edge is now action form: "...not fixed until the month-end points expiry run for the latest calendar month whose last day falls on or before the redemption date has been made". Its fallback_reason holds: a zero run leaves no record, so no record-visible state could name it. MEPE adds "a run that finds no points expiring is made without an entry". For 1–30 Oct 2026 the September run computes 0, so it is made with no write. **A late-run divergence of the same edge remains (R-1).** |
| N-2 lost-time compensation | **closed** | downtime_allowance_rule is gone. Its replacement, repeat_fee_refund, credits the repeat RO's shop-supplies and hazardous-waste fees when the original RO already carried them ("so that no fee is charged twice for the same job"). That is a real comeback practice and does not conflict with the blueprint. |
| N-3 REE in-warranty repeats | **closed** | The rule now says "Where the diagnosis date is on or before the day comeback_warranty_months calendar months after the earlier repair's line date ... and the vehicle's odometer ... is no more than comeback_warranty_miles miles beyond ..., the failure is a comeback inside the store's repair warranty, its replacement parts are not billed and this policy prices nothing". `review_open` excludes `in_repair_warranty`. The r2 probe (8 months, 6,000 miles) now gives 0. DGC's REE-edge sentence is scoped to the same out-of-warranty case. |
| N-4 multiplier swaps | **closed** | CLC basis tier 2 is now "the original labor charge plus half of the amount by which the repeat labor charge exceeds it", an averaging operation; all pairs are distinct. REE rate_lock_rule is relabelled `parameter` (the tiers select a posted-rate value, and tier 2 is the lesser of two values), which is honest. Method floors still hold: REE has diagnosis_overlap_hours; CLC has original_store_basis and repeat_fee_refund. |
| N-5 tool enforcement | **closed, except one member** | The enum check (A–H, plus not_applicable where documented) is in all 5 line-letter tools. The `src[0]["line_letter"] != line_letter` cross-check is in all 4 credit tools. `_Fmt.whole` rejects "27,541", True, 2.5, "-3" and "" with the Error string. `_Fmt.money` maps non-numeric and NaN input to the Error string. The module docstring now matches the bodies. **Remaining member: `_Fmt.money("inf")` raises OverflowError, which `except (TypeError, ValueError)` does not catch, in all 6 money tools (R-2).** |

### rounding_at_exact_ties

- Every rule says "rounded half up to the cent". Every RND now adds 1e-6 before rounding. The tools' `_Fmt.cents` uses `int(abs(v)*100 + 0.5 + 1e-7)`.
- At exact ties both sides round up: 0.125 → 0.13, 2.675 → 2.68, 438.115 → 438.12, and 368.125 → 368.13 (r2's Python round gave 368.12).
- They can disagree only for values within 1e-6 below a half cent, where the compute rounds up and the tool does not. No scored value or skip value is within 1e-6 of a tie except at the tie itself. Observation.
- Note: r2's OPR skip-PRP value 368.12 is now 368.13 under half up. Checked against the GT proof text after the reveal.

### revision_3_scan

All recipe points were checked on every changed policy.
- compute_basis-verbatim and baseline-in-rule sweeps pass for all 8 policies.
- Every policy_source is verbatim in its rule. The one action-form edge carries a fallback_reason; the state-form edges do not.
- Factor counts:
  - EOC 5 (1 method), PRP 6 (1), MEPE 4 (1), OPR 6 (1), CLC 5 (2 methods: basis and fee refund), EPD 6 (1), REE 6 (1: overlap hours), DGC 4 (1).
  - All-pairs distinct. T2 holds for every factor, including the new repeat_fee_refund (any comeback whose original RO carried shop fees).
- The assembly sentences are generic ("this policy sets out") and fix the non-commuting orders.
- No docstring carries an ordering word or an example value. The uuid8s are unchanged.

### findings (revision_3)

Every member found in one pass.

**R-1 SOURCE-POLICY: late month-end runs. MEPE's compute and the expiry tool use the handling date, while MEPE's rule uses the run day.**
- OPR's wait reaches back to "the latest calendar month whose last day falls on or before the redemption date". For any redemption that is not on a month-end, the run it waits on is last month's, and if it was not made the agent makes it late.
- MEPE's rule fixes the run to its own day:
  - "A record falls within the last whole months named when fewer than that many whole months separate its date from the day of the run".
  - "The month-end run is made on the last day of each calendar month, and the expiry is booked as one points-expired entry dated on that day".
- The compute ages points at NOW (`within_months`, `MONTHS(F('opened_date'), NOW)`), and expire_owner_points books the entry "dated today".
- Probe on the task-0 account after the October booking:
  - The November run computed on 2026-11-30 gives 0.
  - Made late on 2026-12-10 (a redemption that day waits on November), the compute gives 2342. The 2024-08-09 points reach 28 whole months on 2026-12-09.
  - So the rule says "made without an entry", while the compute and the tool book 2342 points dated 2026-12-10.
- Members:
  - MEPE compute (unaged_points, recent_redeemed, returned_12m and months_open all keyed on NOW).
  - expire_owner_points_a6cb3dc9's body and docstring ("dated today").
  - OPR's action-form prerequisite, which makes late runs reachable.
- The OPR prerequisite was already present in this form in r2; I missed this then.
- Bears on: charter only. Task 0 is on the run day itself.

**R-2 SOURCE-POLICY (check 3): residual tool parse crash.**
- `_Fmt.money` catches only TypeError and ValueError. `float("inf")` turns into an OverflowError at `int(abs(v)*100 ...)`, so an "inf" amount raises instead of returning the documented Error string.
- Members: redeem_owner_points_3e3ce956, credit_estimate_overage_3db3cf5c, authorize_repair_estimate_690e2aa2, credit_diagnostic_fee_eae01e67, credit_early_payment_discount_b0e7362c, credit_comeback_labor_f15915d4.
- Impact is minimal, but this is the same class as r2 N-5.
- Observation (lenient, not a crash): `_Fmt.whole(27541.0)` and `_Fmt.money("1e3")` are accepted although the docstrings say "no decimals" and "decimal number with 2 decimal places". The module docstring says the tools enforce number formats.

**R-3 SOURCE-POLICY: the new minimum floors price nothing-owed and out-of-scope worlds above the restated base (the r1 C-1 class, regressed by the rework).**
- **EPD.** `MX(0.01, ...)` with "never less than one cent on an invoice paid in full inside its window". On a retail account (out of scope: "For a fleet invoice paid in full, this policy sets ..."), the retail tiers have early_pay_discount_days 0 and early_pay_discount_pct 0. Any retail invoice paid on its labor date is therefore "inside its window" at rate 0, and the compute prices it at 0.01, where the restated base gives none.
  - Probe: the task-0 account with the RO 262107 payment moved to 2026-10-20 gives 0.01.
  - Retail tiers pay at pickup under the base rule, so same-day payment is the ordinary retail case.
- **CLC, retail branch.** "A comeback credit that is owed is never less than one cent" plus `MX(0.01, RND(repeat_labor * pct))`. When the paid repeat RO has no customer-pay labor (for example a service-contract deductible labor row only), repeat_labor = 0 and the compute books 0.01. The restated base credits comeback_labor_covered_pct of that labor, which is nothing.
  - Probe: task-0 account, deductible-only RO 262290 inside 12 months of the CR-V's customer-pay parts repair gives 0.01.
- **CLC, fleet branch, same absent-record case.** The rule names "the repeat labor charge is its customer-pay labor charge"; with none there is no repeat to credit. The compute still prices basis tier 1 (different store → original labor charge) plus the fee refund.
  - Probe: task-1 world with RO 261030's labor row re-typed to service_contract_deductible gives 645.54 credited against a row the customer did not pay.
  - The fleet absent-labor case already existed in r2 (missed). The retail one-cent case is new.
- **PRP.** "...never less than one point on a tier whose points_earn_per_usd is above zero" and `MX(1, ...)`. The restated base in PRP's own replaced_by says "on every account shop fees, late fees and deductibles earn nothing".
  - Probe: a Silver account with no bonuses and a paid RO carrying only a 70.00 storage fee earns 1 point.
- Bears on: charter only. Neither task world reaches these cases: task 0's EPD/CLC are not in its tree, and its PRP RO has 917.72 of labor and parts; task 1's repeat labor is customer pay.

Observations:
- EOC's one-cent floor applies only where overage > 0, consistent with its rule.
- The 1e-6 vs 1e-7 rounding epsilons (above).
- The ladder `when` paraphrases still say "twelve months" (PRP visit; OPR held and frequent).
- The r1 realism observations still stand.

### closing_checklist (revision_3)

Written after both revision-3 reveals.

- Every r2 id is closed as stated (N-1 for zero runs, N-2, N-3, N-4; N-5 except its "inf" member).
- Nothing that passed in r2 regressed on either task's world:
  - Task 0's values are unchanged. Its one skip value moved from 368.12 to 368.13 under the now-correct half-up rounding.
  - Task 1's chain changed only through the replaced CLC factor.
- Remaining charter defects:
  - R-1: late month-end runs. Present in r2 and missed there.
  - R-2: the "inf" parse crash, a residual member of N-5.
  - R-3: the minimum floors price out-of-scope and nothing-owed worlds. EPD retail, CLC retail and PRP fee-only are new from the rework; the CLC fleet absent-labor member is old and was missed.
- Neither task's world reaches any of them, so both tasks PASS on all four relationships.
- The reworker's claims "never an exception" and "No waited-on write can compute 0.00 and be refused" were checked against the artifacts and do not hold; see R-2 and R-3.
- Trees: each has 3 value_input edges (one in action form with a justified fallback) and one user-owned write, with no cycle. Scopes are disjoint and cover the charter. The uuid8s are unchanged.
- Gates: coordinator snapshot 7/7 OK at 2026-10-22T06:04:51.
- The difficulty is **not closed** while the charter has open RED ids.

Charter RED ids (revision_3): R-1 (late month-end runs: MEPE ages points at the handling date, and the expire tool books entries dated today, where the rule uses the run day), R-2 (the "inf" amount raises OverflowError in the 6 money tools), R-3 (the minimum floors price nothing-owed and out-of-scope worlds above the restated base: EPD retail same-day 0.01, CLC retail zero-labor 0.01, CLC fleet absent customer-pay labor 645.54, PRP fee-only RO 1 point).

VERDICT revision_3: task0=PASS task1=PASS charter=R-1,R-2,R-3

## revision_4

### charter_global_frozen (revision_4)

- Frozen: 2026-10-22T07:16Z, before tasks/*.json revision 4 and before the worklog body were read. Before freezing I read only the worklog's last non-blank line, `REWORK round 4: gates 7/7 green`.
- Snapshot: ran `/tmp/erl0075_coord/snapshot.sh service_repair_orders 4` at 2026-10-22T07:13:36. Output:
  - r4 views: 0.view c6ff391b0aa9ede5 and 1.view e58fbd1b623b86d1, both unchanged since r2.
  - Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
  - sha256 prefixes: service.extended.yaml ebff8c140923, task_tools.py a146a457904d, tasks/0.json 7cf8b158f2e8, tasks/1.json 3c182862df2e.
- The charter (a3c538bc6305… → ebff8c140923f707) and the tools (ac881aeff29b… → a146a457904dc6d6) changed. The base copy is still verbatim.
- The changed policies were found by a policy-by-policy diff against my saved r3 copy (/tmp/audit_service_repair_orders_0075/r3/ext_r3.yaml), and every changed policy was re-checked:
  - All 8: every money RND now adds 1e-9 (coordinator ruling: accepted).
  - PRP: one-point floor removed; new "A repair order whose customer-pay labor charges, less the estimate overage, comeback, goodwill and rewards redemption credits standing on it, come to less than one dollar earns no points"; compute gate `earns_points`.
  - OPR: the PRP-edge sentence is scoped to the same ≥ $1 labor test; owner_plan_bonus_pct 0.15 → 0.16.
  - MEPE: late-run sentence ("a run not made on that day is made on the day it is made ... points are aged ... to the day the run is made; ... entry dated on the day the run is made"); the reserve is counted to the run day; result capped at the points balance.
  - CLC: one-cent floor removed; `review_open` requires customer-pay repeat labor > 0; new fleet sentence that a parts-only original line "is a parts sale rather than a repair the store performed, and no comeback credit is owed against it".
  - EPD: one-cent floor removed; new gate "No discount is given on an invoice whose customer-pay labor charges exceed the comeback, estimate overage and goodwill credits on it by less than min_discount_labor_usd" (10.00); the CLC-edge sentence is scoped to originals with labor.
  - DGC: the EPD-edge sentence is scoped to fleet invoices with ≥ $10 of net labor.
  - REE: maintained_share_high 0.9 → 0.88.
  - EEO: unchanged except rounding.
  - Tools: exact-decimal half-up parser; exponents, separators, currency signs and non-finite values are rejected with the Error string.
- contamination_disclosure: none.

### closure_of_revision_3_items

| r3 id | status | evidence |
|---|---|---|
| R-1 late month-end runs | **closed** | MEPE's rule now ages points, and takes every window and month count, "to the day the run is made", and dates the entry "on the day the run is made". That matches the compute (NOW) and the expire tool ("dated today"). Probe: November run on 2026-11-30 gives 0, made on 2026-12-10 gives 2342; both now agree with the rule. |
| R-2 "inf" parse crash | **closed** | `_Fmt.money` checks `_decimal` first. "inf", float inf, NaN, "1e3", "$5.00", "27,541", "5." and ".5" all give None and so the Error string. No exceptions in any of the 6 money tools. `_Fmt.whole` now rejects 27541.0 and " 27541". The half-up path is exact: 0.125 → 0.13, 2.675 → 2.68, 1.005 → 1.01, 0.005 → 0.01, 0.004 → 0.00 → Error. |
| R-3 floors | **closed for every r3 member** | No `MX(1,` remains, and the only `MX(0.01` is EOC's, which its own rule states ("never less than one cent where the line is billed beyond the tolerance"). Under the ruling that is not a floor creating an amount the rule does not owe, so it stays an observation. Probes: EPD retail same-day invoice 0.00; CLC retail deductible-only repeat 0; CLC fleet with no customer-pay repeat labor 0; PRP storage-fee-only paid RO 0. |

Rounding: every rule says "half up". The compute is `RND(x + 1e-9, 2)`, accepted by the coordinator ruling: a value within 1e-9 below a half cent is logged DSL-known residue. The tools round exact-decimal half up. No scored, skip or T1 value lies within 1e-9 of a tie: task-0 OPR raw is now 441.557625 and skip-PRP 370.984375, so the 438.115 and 368.125 ties are gone with the 0.16 bonus.

### revision_4_scan

XF recipe on every changed policy:
- compute_basis-verbatim and baseline-in-rule sweeps pass for all 8 policies. Every policy_source is verbatim in its rule. The single action-form edge (OPR←MEPE) keeps its justified fallback_reason.
- Factor counts are unchanged: EOC 5, PRP 6, MEPE 4, OPR 6, CLC 5 (2 methods), EPD 6, REE 6, DGC 4. Every policy keeps at least 2 parameter and at least 1 method factor. All-pairs distinct, T2 holds, assembly sentences generic.
- The new gates are rule-level scope tests, as the r2/r3 absent-record sentences were, and are not in `baseline.rule`: PRP < $1 labor, EPD < $10 net labor, CLC no repeat labor or parts-sale original. Observation, consistent with earlier rounds.
- New realism observations: PRP's "< $1 net labor earns no points" means a parts-only retail order earns nothing; EPD's $10 net-labor minimum. Both are publishable terms.

### findings (revision_4)

**R-4 SOURCE-POLICY: CLC credits a comeback against a parts-only original on a retail account, where the restated base owes none. This is the r1 C-1 class (out-of-scope pricing against the restated base). Present since r1, made visible by r4's fleet-only guard.**
- Base service_evt_comeback, still in force on every account: "A customer-pay repair performed by any store of the group carries the store's repair warranty ... A repeat failure of the same repair inside the repair warranty is a comeback."
- CLC's own r4 sentence: "an original repair line that carries no customer-pay labor charge is a parts sale rather than a repair the store performed, and no comeback credit is owed against it". It is stated "On a commercial fleet account" only, and only the fleet branch tests `original_labor > 0`.
- The retail branch credits `repeat_labor × comeback_labor_covered_pct` whenever `in_warranty`, and `in_warranty` is keyed on the latest customer-pay parts row whether or not that line had labor.
- Probe on the task-0 account: a parts-only counter sale on the CR-V (RO 262290, 2026-10-30, 114.00, no labor), then a paid customer-pay labor RO 262301 (2026-10-31, 154.80).
  - Gold account: CLC 154.80. Under the restated base, no repair was performed, so there is no repair warranty and no comeback: 0.
  - Same world on a Net-30 account: 0.
- Members: CLC retail branch of `result`; the CLC rule sentence "On any other account the credit is the repeat labor charge times comeback_labor_covered_pct ..., owed on the same warranty and repair order terms".
- Bears on: charter only. Task 1 is fleet and its original RO 260205 has labor 885.36; task 0 has no CLC.

Observations:
- EOC's rule-stated one-cent minimum.
- The 1e-9 residue (ruling).
- The new gates sit outside `baseline.rule`.
- The ladder `when` paraphrases ("twelve months").
- Earlier realism observations stand.
- CLC's original-repair selector can pick an unpaid open RO on the same unit (it is keyed only on the latest customer-pay parts row). Neither world is affected.

### closing_checklist (revision_4)

Written after both revision-4 reveals.

- Every r3 id is closed as stated (R-1, R-2, R-3), and nothing that passed has regressed: task 0's gold moved 438.12 → 441.56 and task 1's REE moved 2859.01 → 2847.19 only through the declared tie-avoiding parameter changes, and the factor, tree and solution checks still pass.
- Checked after the freeze against the worklog's r4 claims: the R-1 probe figure 1000 is the 2342 capped at the post-redemption balance, consistent with the new cap; the tie list claims match my recomputation.
- One remaining member of the out-of-scope class, R-4 (CLC retail branch credits against a parts-only original), is newly visible because the r4 fleet guard makes the inconsistency explicit.
- Trees, scopes, uuid8s and gates: unchanged and green (snapshot 07:13:36, 7/7).
- The difficulty is **not closed** while R-4 is open.

Charter RED ids (revision_4): R-4.

VERDICT revision_4: task0=PASS task1=PASS charter=R-4

## revision_5

### charter_global (revision_5)

- Entry gate: the worklog's last non-blank line is `REWORK round 5: gates 7/7 green`.
- Snapshot: ran `/tmp/erl0075_coord/snapshot.sh service_repair_orders 5` at 2026-10-22T07:21:11. Output:
  - Views: 0.view c6ff391b0aa9ede5 and 1.view e58fbd1b623b86d1, both unchanged.
  - Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
  - sha256 prefixes: service.extended.yaml b74d088c79be, task_tools.py a146a457904d (identical to r4), tasks/0.json b782eaa72a3e, tasks/1.json 6540d551e157.
- Base copy: still verbatim.
- Diff against my saved r4 copy (/tmp/audit_service_repair_orders_0075/r4/ext_r4.yaml) shows exactly three changes:
  - CLC: rule sentence widened to "On every account, an original repair line that carries no customer-pay labor charge is a parts sale rather than a repair the store performed, carries no repair warranty, and no comeback credit is owed against it". `in_warranty` gains `original_labor > 0`; the fleet-only `if original_labor > 0` branch is dropped from `result`; compute_basis quotes updated.
  - REE: new sentence "Where the earlier repair's line carries no customer-pay labor charge, it is a parts sale rather than a repair the store performed, the failure does not repeat a repair, and this policy prices nothing", plus a `prior_labor_amount` binding gating `review_open`.
  - DGC: REE-edge policy_source and condition now add "with a customer-pay labor charge on its line".
  - Nothing else in the charter or the tools changed.
- contamination_disclosure: none.

### closure_of_revision_4_items

| r4 id | status | evidence |
|---|---|---|
| R-4 CLC retail credit against a parts-only original | **closed** | The parts-sale sentence now covers every account, and `in_warranty` tests `original_labor > 0` for both branches. The r4 probe (parts-only RO 262290 on the CR-V, then paid labor RO 262301) now gives 0 on Gold and 0 on Net 30. The same class was swept consistently: REE prices nothing against a parts-only earlier line, and DGC's authorization wait is carved to earlier repairs with labor. |

### revision_5_scan (XF recipe on every changed sentence)

- compute_basis-verbatim and baseline-in-rule sweeps pass for all 8 policies, including the new CLC and REE quotes.
- All 6 policy_source sentences are verbatim in their rules. The DGC←REE edge stays state form. OPR←MEPE stays action form with its valid fallback_reason (ruling).
- Factor counts, labels, all-pairs distinctness and T1/T2 are unchanged.
- The new gates are scope tests at rule level, consistent with the earlier absent-record sentences; they introduce no floor and no ordering word.
- The three changed policies' out-of-scope branches now equal the restated base on the parts-sale case.
- Rounding: RND(x + 1e-9) per ruling. No scored, skip or T1 value is within 1e-9 of a tie.
- Both tasks' values are unchanged (task 0 118.56 / 4666 / 3278 / 441.56; task 1 645.54 / 3.89 / 2847.19 / 76.36), and both GT files match my replay item by item. Nothing regressed.

### observations (revision_5)

Not RED.
- CLC and REE take "the latest customer-pay parts row on the unit" as the original or earlier repair. A later parts-only counter sale therefore shadows an earlier labor repair, and neither policy then credits or prices. This is consistent with each rule as written. Whether the shadowed repair is "the same repair" is not record-visible. Neither world contains such a row.
- The r4 observations stand: EOC's rule-stated one-cent minimum, the gates sitting outside `baseline.rule`, the ladder `when` paraphrases, and the r1 realism notes.

### closing_checklist (revision_5)

- Every r1–r4 RED id is closed, verified against the artifacts.
- Per-task files carry revision_5. Both tasks PASS on all four relationships.
- Scopes are disjoint and cover all 8 policies. Each tree has 3 value_input edges, one user-owned write and no cycle. The uuid8s are unchanged and independent.
- Gates 7/7 OK on the final form (coordinator snapshot 07:21:11).
- No charter RED remains, so the difficulty is closed at the source layer.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

### charter_global (revision_6)

- Entry gate: the worklog's last non-blank line is `REWORK round 6: gates 7/7 green`.
- Snapshot: ran `/tmp/erl0075_coord/snapshot.sh service_repair_orders 6` at 2026-10-22T10:02:36. Output:
  - Views: 0.view c6ff391b0aa9ede5 and 1.view e58fbd1b623b86d1, both unchanged.
  - Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
  - sha256 prefixes: service.extended.yaml 9a94105a86d9, task_tools.py a146a457904d (identical to r5), tasks/0.json e9a0b8d27439, tasks/1.json 35b21e794ded.
- Input: render_source/service_repair_orders/render_r1.md (F1–F4), read in full. Those four items are source defects that my revision_5 CLEAN verdict missed:
  - F3: I noted the CLC "repeat labor charge" sum in my r1 scratch notes but never reported it.
  - F4: held_points_rule has read months_open since r1, and my factor-independence checks did not catch it.
- Diff against my saved r5 copy (/tmp/audit_service_repair_orders_0075/r5/ext_r5.yaml). Changed:
  - PRP and EPD: the paid-in-full sentence and ro_balance/invoice_balance; their baselines.
  - CLC: the repeat-labor and original-labor sentences; repeat_* bindings keyed on one customer-pay row; baseline.
  - REE: the earlier-repair, repair-hours and parts-amount sentences; baseline.
  - EOC and EPD: the booking sentences.
  - OPR: new `enrollment_age_months` binding for held_points_rule.
  - Base copy is verbatim and the tools are unchanged.
- contamination_disclosure: none. The blind replay was run before the r6 task JSONs were opened.

### closure_of_render_r1_items

| item | grade | evidence |
|---|---|---|
| F1 PRP paid-in-full counts only customer-pay rows | **closed** | Rule: "its charges, customer-pay and deductible alike, less every credit ...". `ro_balance` now sums every labor and parts row of the RO regardless of pay_type, plus diagnostic fees, shop fees and returned payments, less every credit and payment. Baseline updated. Probe: an unpaid 100.00 service-contract deductible on paid RO 262107 gives 0 points, matching the rule. |
| F2 EPD same | **closed** | Same sentence and the same `invoice_balance` change. Probe: an unpaid 100.00 warranty deductible on RO 261030 gives a discount of 0. |
| F3 CLC singular repeat labor charge vs RO sum; booking row undetermined (CLC, EPD) | **closed** | CLC: "the repeat labor charge is its latest customer-pay labor charge". repeat_labor, unit, date, odometer and store are all LATEST over the same customer-pay filter, so the same row under the stated first-listed tie rule. "its labor charge is the total of the customer-pay labor charges on the same repair order and concern line" matches the original_labor SUM. Probe: an earlier second customer-pay labor line on RO 261030 leaves CLC on the latest row (832.66), so 645.54 is unchanged. Booking rows: CLC books against "the repeat labor charge" (now one row); EPD against "the invoice's latest customer-pay labor charge"; EOC against "the line's latest customer-pay labor charge". |
| F4 OPR held_points_rule reads tenure_point_value's months_open | **closed** | held_points_rule's bindings now include its own `enrollment_age_months = MONTHS(F('opened_date'), NOW)`, and its tier 2 reads that binding. Mechanical sweep of all 8 policies, checking every factor-binding expression against every other factor's bindings: no factor reads another factor's binding, and no binding is shared between factors. |

### class sweep (revision_6, any member is RED)

- **F1/F2 class (a rule "charges/balance" phrase versus a compute filter).** No policy other than PRP and EPD defines a paid-in-full balance. Every other amount phrase names its filter and matches it:
  - EOC billed amount: "customer-pay labor and parts charges".
  - OPR cap: "customer-pay labor and parts charges".
  - DGC spend: "customer-pay labor and parts charges".
  - REE 12-month parts: "customer-pay parts charges".
  
  No member remains.
- **F3 class (a singular "the … charge" read as an aggregate, or a booking row left undetermined).** Every single-record phrase was checked against its selector:
  - EOC: "vehicle on the line's labor charge"; "line's labor closed" (LATEST on the line).
  - PRP: "vehicle on its labor charges".
  - OPR: "latest labor charge".
  - EPD: "latest line date of its labor charges".
  - REE: "the hours of the earlier repair's latest customer-pay labor charge", plus the rate and store from the same line. One RO is written at one store, so a single posted rate applies.
  - DGC: one diagnostic fee per concern line, per base.
  
  Booking targets are single rows in all 8 policies: EOC, EPD and CLC named above; DGC on the diagnostic fee; PRP, OPR and MEPE as one entry. No member remains.
- **F4 class (factor independence, recipe A1).** Mechanical sweep is clean (above).

### revision_6_scan (XF recipe on every changed sentence)

- compute_basis-verbatim and baseline-in-rule sweeps pass for all 8 policies.
- All 6 policy_source sentences are verbatim. The tasks' prerequisite_closure edges equal the charter's entries (source, condition, form).
- Factor counts, labels, all-pairs distinctness and T1/T2 are unchanged.
- No floor added. Rounding is RND(x + 1e-9) per ruling. The single action-form edge keeps its valid fallback_reason (ruling).
- No ordering word, example value or factor id appears in any tool docstring, and the tools are unchanged.
- Nothing regressed. Task values are unchanged from r4 and r5 (task 0 118.56 / 4666 / 3278 / 441.56; task 1 645.54 / 3.89 / 2847.19 / 76.36). Both GT files match my replay item by item.

### closing_checklist (revision_6)

- Every render_r1 item (F1–F4) is closed against the artifacts, and the class sweeps find no further members.
- Per-task files carry revision_6. Both tasks PASS on all four relationships.
- Scopes are disjoint and cover all 8 policies. Each tree has 3 value_input edges, one user-owned write and no cycle. The uuid8s are unchanged.
- Gates 7/7 OK (snapshot 10:02:36). No charter RED remains.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

### charter_global (revision_7)

- Entry gate: the worklog's last non-blank line is `REWORK round 7: gates 7/7 green`.
- Snapshot: ran `/tmp/erl0075_coord/snapshot.sh service_repair_orders 7` at 2026-10-22T10:38:04. Output:
  - r7 views: 0.view efb5ea63c83b02ef and 1.view 4767e9203a4f96b7 (new).
  - Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
  - sha256 prefixes: service.extended.yaml 9a94105a86d9, task_tools.py a146a457904d, tasks/0.json 8d4d6a961afd, tasks/1.json a81373f9ef8b.
- **Byte-identical:** `cmp` of service.extended.yaml against my saved r6 copy, and of task_tools.py against my saved r6 copy, both report no difference. The charter-global sections of revision_6 are therefore carried forward unchanged.
- Input: audits/policy_kb/service_repair_orders/_difficulty.md, items SRC-1 and SRC-2 (seed realism, cross-product maintenance), read in full.

### seed delta (r6 view → r7 view, every changed row)

- Persona and frozen_time: unchanged in both tasks. service_ro_lines, service_repair_authorizations, accounts, deals and contracts: unchanged in both tasks.
- Task 0:
  - +5 maintenance_plan_ledger rows on KC-2408317 (d43e08c9, CR-V): visits_loaded 6 on 2024-04-20; redeemed visit 1 (2024-07-17, KHB, 5062), visit 2 (2025-01-20, 10059), visit 3 (2025-07-15, 14965), visit 4 (2026-06-22, 20062).
- Task 1:
  - +13 maintenance_plan_ledger rows:
    - KC-2409266 (5d445bf8, F-250): loaded 12 on 2024-09-10; visits 1–5 on 2025-02-07 / 2025-07-07 / 2025-12-04 / 2026-04-13 / 2026-08-07 at 26486 / 31492 / 36498 / 41507 / 46491, all at KCV.
    - KC-2404183 (383fbd32, Silverado): loaded 12 on 2024-04-02; visits 1–6 on 2024-08-09 / 2024-12-16 / 2025-05-09 / 2025-11-02 / 2026-04-28 / 2026-10-21 at 52856 / 57862 / 62843 / 67859 / 72874 / 77862, all at KCV.
  - Changed rows:
    - 383fbd32 odometer_at_sale 66150 → 47850, expiration_odometer 141150 → 122850, visits_remaining 5 → 6.
    - 5d445bf8 visits_remaining 8 → 7.

### closure_of_SRC_items

| item | grade | evidence |
|---|---|---|
| SRC-1 Silverado plan odometer at sale ran backwards against the service ledger | **closed** | odometer_at_sale is now 47850 on 2024-04-02, below RO 250312's 61200 on 2025-03-12. The Silverado's readings are now monotonic across both ledgers: 47850 → 52856 → 57862 → **61200 (RO 250312)** → 62843 → 67859 → 72874 → 77862 → **78400 (RO 261109)**. expiration_odometer = 47850 + term_miles 75000 = 122850, matching maintenance_evt_sale ("odometer at sale plus term_miles"). Sale eligibility holds: age 2024 − 2021 = 3 ≤ 8; odometer 47850 ≤ 100000; diesel_eligible true. Price 1029.00 is unchanged and correct (2 fleet plans < fleet_volume_min_plans 10). |
| SRC-2 visits_remaining not reproducible from an empty plan ledger | **closed** | Each plan's visits_remaining now equals loaded less redeemed in its ledger: CR-V 6 − 4 = 2; F-250 12 − 5 = 7; Silverado 12 − 6 = 6. Every redemption is what maintenance_evt_visit_redemption produces (details below). |

Each redemption checked against maintenance_evt_visit_redemption:
- Plan in active status.
- Inside the term: CR-V before 2027-04-20 / 35012; F-250 before 2027-09-10 / 96480; Silverado before 2027-04-02 / 122850.
- Interval: every visit is at least service_interval_miles − interval_tolerance_miles = 4000 miles after the previous visit, or the sale for visit 1. Spacings are 4906–5097 miles. Days apart are 128–342, above min_days_between_visits (60 Plus / 45 Fleet).
- Store: honoring_store_scope is all_group_stores, and every visit is at the selling store.
- visit_number is sequential from 1.
- Odometers: every plan-visit reading is consistent with the service ledger's readings on the same vehicle.
  - CR-V: 5062 < 6210 (RO 241402, 2024-08-06); 10059 < 11050 (RO 250288); 14965 < 15200 (RO 250873); 18640 (RO 260342) < 20062 < 20410 (RO 260819).
  - F-250: 36498 < 38500 (RO 260205, 2026-02-02) < 41507; 46491 < 50100 (RO 261030).
- The visit ROs (e.g. RO 240717, RO 261021) carry no service_ro_lines, which is consistent with base service_combo_coverage_priority: "A line paid by a ... maintenance plan is recorded in that program's records and never billed here". The plan-covered oil service also draws no customer-pay hazardous-waste or shop-supplies fee under service_evt_shop_fees.
- No factory complimentary maintenance coverage is seeded, so maintenance_combo_factory_maintenance defers nothing.

### scored values (re-derived on the r7 views)

- The re-derivation is a DSL replay of the unchanged r6 charter on the r7 views (scratch r7/).
- Values:
  - Task 0: 118.56 / 4666 / 3278 / 441.56 for 27541 points.
  - Task 1: 645.54 / 3.89 / 2847.19 / 76.36.
  - Skips, T1 and all-baselines are identical to r6.
- No scored value moved, as expected: every maintenance read in this charter is a plan's `status = active` (keyed by customer or vehicle), and all three plans remain active at both frozen_times. The Silverado at 78400 is far below 122850.
- GT for both tasks is identical to r6 item by item. Each task JSON's initial_state equals its r7 view. The only rationale change is the [Revisions r7] note.

### closing_checklist (revision_7)

- SRC-1 and SRC-2 are closed against the artifacts. Every re-priced or added row is what the owning maintenance rules produce.
- The charter and tools are byte-identical to r6, so nothing regressed. Both tasks PASS.
- No charter RED.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

### charter_global (revision_8)

- Entry gate: the worklog's last non-blank line is `REWORK round 8: gates 7/7 green`.
- Snapshot: ran `/tmp/erl0075_coord/snapshot.sh service_repair_orders 8` at 2026-10-22T12:36:49. Output:
  - r8 views: 0.view 1cf8e5a0562490fb and 1.view 7b374053ef10a852.
  - Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
  - sha256 prefixes: service.extended.yaml 9a94105a86d9, task_tools.py a146a457904d, tasks/0.json 6a877b7203a2, tasks/1.json 24ca1cf3f3ae.
- **Byte-identical:** `cmp` against my saved r6 copies reports no difference for either service.extended.yaml or task_tools.py. The charter-global sections are carried forward unchanged.
- Input: policy_kb/service_repair_orders/_difficulty.md revision_3 items SRC-3, SRC-4, SRC-5 and SRC-6, read in full.

### seed and persona delta (r7 view → r8 view, every change)

- Task 0:
  - Purchase deal KHB-24-21873: hold_expires_date 2024-04-24 → 2024-04-18, hold_extension_count 0 → 1.
  - Purchase deal KTD-23-20946: hold_expires_date 2023-06-24 → 2023-06-16, hold_extension_count 0 → 1.
  - Persona: "for new front struts" became "for new front and rear brake pads and rotors".
- Task 1:
  - Purchase deal KCV-22-20417: hold_expires_date None → 2022-03-15, title_application_date None → 2022-03-18.
  - Purchase deal KCF-21-21388: hold_expires_date None → 2021-02-22, title_application_date None → 2021-02-25.
  - Customer profile_opened_date 2021-05-03 → 2021-01-11.
  - Service account opened_date 2021-05-03 → 2021-01-11.
  - Persona unchanged.
- No service ledger, authorization, plan, contract or plan-ledger row changed in either task.

### closure_of_SRC_items (against purchase.yaml and the published owning rules)

| item | grade | evidence |
|---|---|---|
| SRC-3 hold expiry (2 deals) | **closed** | New Vehicle Retail Purchase: vehicle_hold_days 5, hold_extension_days 3, max 2. Reserved 2024-04-10 + 5 = 04-15, one extension + 3 = **04-18** (count 1), and the contract on 04-18 falls on the last held day. CPO: hold 3, +3, max 1. Reserved 2023-06-10 + 3 = 06-13, one extension = **06-16** (count 1), contract 06-15. Both follow purchase_evt_hold_extension ("moves hold_expires_date forward by hold_extension_days ... counted from the current hold_expires_date ... raises hold_extension_count by one"), within the maximums. |
| SRC-4 fleet hold and title (2 deals) | **closed** | Fleet Vehicle Purchase Agreement vehicle_hold_days 14: 2022-03-01 + 14 = **2022-03-15**; 2021-02-08 + 14 = **2021-02-22**. Both contracts (03-08, 02-15) fall inside the hold. Title application filed 3 days after delivery (2022-03-18, 2021-02-25), within title_application_days 30, on delivered deals (purchase_evt_title). |
| SRC-5 net terms before the service account | **closed** | The service account and profile are now opened 2021-01-11, before the KCF-21-21388 reservation (2021-02-08) and contract (2021-02-15). That satisfies purchase_combo_fleet_terms ("only while the buyer holds a Commercial Fleet Account - Net 15 or Net 30 service account in active status"). The account is 70 whole months old on the 2026-11-11 payment date (≥ 60), so EPD's tenure addition tier is unchanged. |
| SRC-6 struts under an in-force Factory Basic warranty | **closed** | The persona's job is now "front and rear brake pads and rotors". Pads and rotors are listed wear items outside the Factory Basic Limited Warranty and outside the Kessler Shield Exclusionary contract's coverage. Under base service_combo_coverage_priority, customer pay is then what the published priority produces, so the seeded customer-pay line A on RO 262245 is consistent. The seeded line also fits a four-wheel pad-and-rotor job: labor 2.6 h × 172 = 447.20 less 10% = 402.48; parts list 588.00 less 5% = 558.60; shop supplies 6% = 24.15; no hazardous-waste fee, since no fluid service is involved; authorization 975.00. |

### scored values (re-derived on the r8 views, unchanged charter)

- DSL replay (scratch r8/):
  - Task 0: 118.56 / 4666 / 3278 / 441.56 for 27541 points.
  - Task 1: 645.54 / 3.89 / 2847.19 / 76.36.
  - Skips, T1 and all-baselines are identical to r7.
- The only factor input the delta touches is task 1's account opened_date. EPD's months_open is now 70 (was 66), still the ≥ 60 tier (+0.005), so account_tenure_addition still bears weight (T1 3.33).
- Purchase reads are unchanged: status, financing_type, variant_name and vehicle_id.
- GT for both tasks is identical to r7 item by item. Each task JSON's initial_state and user_scenario equal its r8 view.
- No stale "struts" or "2021-05-03" claim remains outside revision notes.

Observation (carried from the KB audit's note, not RED): task 1's hidden proof text calls RO 260205 / RO 261030 an "EGR cooler" repair. No runtime-visible record names a component, and no warranty coverage is seeded, so the visible world is consistent.

### closing_checklist (revision_8)

- SRC-3 to SRC-6 are closed against the artifacts and the owning products' published rules.
- Both personas are consistent with their seeds. The charter and tools are byte-identical, no scored value moved, and nothing regressed. Both tasks PASS. No charter RED.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN
