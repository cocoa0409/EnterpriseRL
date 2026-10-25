# Policy-task audit — optional_coverage_riders / charter-global

## charter_global_frozen

- Frozen: 2026-10-12, written between 13:39Z and 13:43Z, before any task's GT was revealed (first GT read 13:43:15Z). Auditor: independent policy-task auditor (not the instantiating agent).
- Hashes verified on disk at audit start (match the coordinator brief):
  - `tasks/optional_coverage_riders/addon.extended.yaml` sha256=07b5bffc1adccce5d080c9c27694cffba8912499efb53faa56aca40be14894fd
  - `tasks/optional_coverage_riders/task_tools.py` sha256=765a074e4fba5423ed0c876d652d7c4488d535d692279596f7ed4f24dfde1d72
  - `.audit_views/policy_task/optional_coverage_riders/0.view.json` sha256=a71cefd1…f414; `1.view.json` sha256=cb8d480c…81f3
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/products/addon.yaml` (and, for cross-category parameters only, `homeplan.yaml` tier params / enrollment rule and `hvaccare.yaml` lifecycle / inspection event), `blueprint/db_schema.json` (hvaccare_agreements.inspection_result, homeplan_contracts.service_call_fee), `blueprint/share_tools.py` (function list), the extended charter and `task_tools.py`, and the erlbench DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/within_months/LATEST/X* definitions).
- Masked and unread at the time this section was written: every field of `tasks/optional_coverage_riders/tasks/*.json` other than what the masked views carry (`frozen_time`, `user_scenario`, `initial_state`); no recursive search touched `tasks/`.
- Entry conditions (Step 0): gate snapshot supplied in the brief (EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; TRACEABILITY NOT OK only for the pre-docs tool_name unlock; validate_scenario only "required document not found"). Masked views and hashes supplied. Entry conditions complete.
- Base copy: the extended file's section before `extended_policies:` is byte-identical to `blueprint/products/addon.yaml` except for the three trailing comment lines that introduce `extended_policies` (verified by diff). Base copy verbatim: PASS.

### policy_conflict_scan

Extended policies (6), subject, target tool, owner, trigger:

| policy | subject | target_tool (owner) | trigger | prerequisite |
| --- | --- | --- | --- | --- |
| addon_ext_annual_premium_correction (PC) | addon_premium_credit (billing_correction) | post_rider_premium_correction_851994d3 (agent) | state_due | [] |
| addon_ext_rider_work_authorization (RW) | addon_benefit_authorization (repair/replacement) | authorize_rider_work_f2a2f75a (agent) | state_due | [] |
| addon_ext_rider_removal_credit (RC) | addon_rider_removal + addon_premium_credit (rider_removal_credit) | remove_rider_with_credit_c919c4de (user) | on_request | PC (value_input, state), RW (state_gate, action) |
| addon_ext_rider_visit_fee (VF) | addon_service_fee_charge | charge_rider_visit_fee_fc58860f (agent) | state_due | [] |
| addon_ext_haul_away_allowance (HA) | addon_benefit_authorization (allowance/haul_away) | authorize_haul_away_allowance_ee656dca (agent) | state_due | [] |
| addon_ext_cash_settlement (CL) | addon_benefit_authorization (cash_in_lieu) | accept_rider_cash_settlement_51ff485a (user) | on_request | VF (value_input, state), HA (state_gate, state) |

Overlaps examined:
- RW, HA and CL share the subject `addon_benefit_authorization`; each scopes itself by resolution type ("For a repair or replacement authorization this policy sets…", "For a haul-away allowance…", "For a cash settlement the customer takes…"). RW's "owed one repair or replacement authorization, unless the customer settles it in cash" and CL's "no replacement is authorized on that request once it is taken" agree (mutual exclusion on one request), and base `one_open_rider_resolution` is inherited by both. No conflict in conclusion.
- PC and RC both post `addon_premium_credit`; each scopes its own credit reason (billing_correction vs rider_removal_credit) and each overwrites the base one-credit-per-reason sentence only "for such a credit". No conflict.
- Time anchors: all four term-window clauses use the same "whole months … fewer than one more than the whole months from the term start" convention (PC/RC on the correction/removal date, RW/HA/CL on the authorization/settlement date). Consistent.
- Cross-category reads: homeplan (term_number, variant_name, square_footage, service_call_fee, tier params, billing/claim/request ledgers), lineplan (status, variant_name), hvaccare (status, inspection_result). All are read-only.
- Scope exclusivity / completeness: the six policies form exactly two trees by their `prerequisite` edges: {RC ← PC, RW} and {CL ← VF, HA}. With M=2, two disjoint trees cover all six policies. The claimed task scopes are compared item by item after reveal in each task file.

### rule_compute_equivalence

Check 2, policy by policy. Every compute binding has a `compute_basis` quotation that is a verbatim fragment of the policy's rule; sweep-back findings only:

- PC: every rule sentence implemented. `base_home_sqft … or 0`, `prepay_days … else -1` encode "no homeowner premium payment is on file" / non-homeowner base. The "billed annually" condition of the first rule sentence is not tested in compute, but a monthly-billed rider carries no `prorated_annual_rider_premium` charge, so `charged`=0 and the result is 0; no divergence. PASS.
- RW: `request_paid` subtracts every `addon_authorization_reversal` on the request (allowance reversals included) while the rule nets reversals of "repair, replacement and cash-in-lieu amounts" only — divergence only when an allowance on the same request is reversed; no such row in either world. Observation O-1.
  The `hvac_uplift` "pending" branch reads `inspection_result=='pending'` on an *active* agreement — see factor_ladders F-3 (the branch is unreachable under the hvaccare charter).
- RC: `unearned_share` monthly branch divides by `MX(1, MONTHS(...))`; the guard is not in the rule (only matters when the rider term is under one whole month). `inputs.history` lists only `homeplan_repair_authorization` while compute and rule also read replacement authorizations (metadata only). Observation O-2.
- VF: `same_trade_recent = COUNT(…within_months=1, trade=req_trade) - 1` assumes the request being charged is itself inside the one-month window; if the fee were charged more than a whole month after the request date the "- 1" would discard another request. Observation O-3 (not reachable in either world).
- HA: PASS (equipment list in compute = "a pump, a motor or a blower" over the variants' component names; renewals formula verbatim).
- CL: PASS.
- DSL notes (from `check_compute.py`): `RND` is Python `round` (half-even on binary floats) whereas the tool contracts say "rounded half up to the cent"; no scored value in either world sits on a half-cent boundary (checked in the task files). Observation O-4.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are unique: each of the six tools is claimed by exactly one policy, `computes: amount` in each.
- uuid8 tails 851994d3, f2a2f75a, c919c4de, fc58860f, ee656dca, 51ff485a: no shared prefix, no sequence, no common derivation visible. PASS.
- Docstrings: no ordering words (before/after/first), no other tool named, no sequence position. The tool bodies check no policy condition, eligibility or prerequisite (each body only reads the rider/request/latest determination and writes the row as given). PASS for "tool layer judges no prerequisite".
- Finding F-1 (SOURCE-POLICY RED, check 3 — business reading of a tool not unique): `authorize_rider_work_f2a2f75a` is the target tool of RW, which sets the amount only "for a repair or replacement authorization", but its contract advertises `resolution_type` values `cash_in_lieu` ("when a cash settlement is paid in place of a replacement"), `septic_pumping` and `allowance` ("toward an ancillary cost such as removal, permits…"). Those are the business writes that CL's user-owned `accept_rider_cash_settlement_51ff485a` and HA's `authorize_haul_away_allowance_ee656dca` perform. For cash the two tools are byte-equivalent in effect: both create `make_id("ace_", req, "cash_in_lieu", amount)` with authorization number `make_id("4", req, "cash_in_lieu", amount)` and the same fields (component, resolution_type, repair_estimate, replacement_cost, amount). So the agent-owned tool books exactly the row the customer's own write is supposed to book, and nothing in the docstring confines it to repair/replacement. Bears on task 1 (consequence demonstrated there).

### prerequisite_graph

Check 7:
- `prerequisite` filled on all six (`[]` on PC, RW, VF, HA). Every `problem` names another extended policy id in this file; none points at a base policy or itself. Graph: PC→RC, RW→RC, VF→CL, HA→CL. Acyclic, two components.
- `policy_source` of all four edges is verbatim in the blocked policy's own rule (RC rule sentences 3 and 4; CL rule sentences 4 and 5). PASS.
- `form`/`fallback_reason`: PC→RC state (no fallback), RW→RC action (fallback present), VF→CL state, HA→CL state. PASS.
- `kind`/`gate`: PC→RC value_input, gate `retained_premium` (a binding of RC compute — exists); VF→CL value_input, gate `fee_entries` (exists in CL compute). RW→RC state_gate with gate `addon_claim_events.authorization_number`; HA→CL state_gate with gate `addon_claim_events.allowance_type`. Neither RC nor CL declares an eligibility entry, so the two state_gate "gates" point at record fields rather than at an eligibility gate of the blocked policy. Observation O-5.
- `resolved_by` = the depended-on policy's `target_tool` on all four edges. PASS.
- `condition` vs sentence strength: PC→RC and VF→CL match. RW→RC and HA→CL — see prerequisite_sentences F-2.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field. PASS.

### prerequisite_sentences

Check 6, per edge:

1. PC→RC — "The removal credit is fixed only after every prorated annual rider premium charged in the current term above the corrected term premium carries its billing correction on the rider's ledger." Connective "only after"; state form (a billing-correction credit on the rider ledger); no tool, id or snake_case token ("corrected term premium" is a business quantity defined in PC's own rule). Exactly one write of this difficulty leaves a `credit_reason=billing_correction` credit: `post_rider_premium_correction_851994d3`. Derivation: RC sentence → look for the policy whose rule describes posting a billing correction → PC ("A rider whose base contract is billed annually is owed a premium billing correction when …") → its write. Single reading. PASS.
2. RW→RC — "The removal credit is not fixed until Bridgewell has authorized the repair or replacement owed on every covered rider service request." Action form. Fallback tested: a state naming "a repair or replacement authorization" would hold back cash-settled requests; a state naming "a repair, replacement or cash-in-lieu authorization" is brought about by two writes (RW's agent write or CL's user write). The fallback is justified. Derivation: "the repair or replacement owed on … covered request" → RW ("A rider service request with a covered coverage determination on file is owed one repair or replacement authorization, unless the customer settles it in cash") → its write.
3. VF→CL — "The cash settlement is fixed only after the rider service request being settled carries any service call fee entry it owes." State form; one write (`charge_rider_visit_fee_fc58860f`) books `addon_service_fee_charge`. Derivation → VF ("Every new-failure rider service request … owes one rider visit fee, collected on the request"). PASS.
4. HA→CL — "The cash settlement is not fixed until every component replaced under the rider whose removal cost is documented on its coverage determination carries its haul-away allowance authorization." State form. Writes that can bring the state about: `authorize_haul_away_allowance_ee656dca` (allowance_type haul_away) and, under F-1, `authorize_rider_work_f2a2f75a(resolution_type="allowance")`, whose contract describes an allowance "toward … removal". The second candidate is a consequence of F-1 rather than of the sentence itself; recorded under F-1.

- F-2 (SOURCE-POLICY RED, latent — the waiting sentence is broader than the depended-on rule can ever satisfy): the two blocked rules wait on **every** qualifying record, while the depended-on rules owe their write on **one** record only.
  - CL: "…until every component replaced under the rider whose removal cost is documented on its coverage determination carries its haul-away allowance authorization" vs HA: "A haul-away allowance is owed once on the component most recently authorized for replacement under a rider". On a rider with two replaced components, each with a documented removal cost and neither with an allowance, HA owes one allowance (latest component) while CL waits on both: CL can then never be fixed under the charter, or the agent must issue an allowance HA does not owe. The sentence also carries no term limit, so a component replaced in an earlier term blocks the same way.
  - RC: "…until Bridgewell has authorized the repair or replacement owed on every covered rider service request" vs RW: "the request authorized is the rider's most recently placed service request" (and its figures are "those of the rider's most recent covered coverage determination"). With two covered requests both unauthorized, RW authorizes only the most recently placed one, so RC waits forever, or the agent must authorize an earlier request on figures RW's rule does not define.
  Two passages, two conclusions in the same situation. Neither task world has two pending records (task 0: one unauthorized covered request; task 1: one replaced component), so neither task's scored solution changes. Recorded at charter level.
- Docstrings say nothing about sequence (see above). The depended-on rules do not restate the blocked sentences. No second wording of any dependency appears in RC or CL.
- Undeclared cross-problem orders: CL's "no replacement is authorized on that request once it is taken" states an order between CL and RW that grounds no declared edge. It is a mutual exclusion that base `addon_evt_benefit_authorization` already states ("the replacement authorization it replaces is reversed in full" / one open resolution per request). In neither task is RW owed on the request CL settles (task 1: the customer settles in cash, so RW is not owed), so the two orders do not produce two terminal states in any world here. Observation O-6.

### override_declarations

Check 1, finding half, sentence by sentence against `base_policy_refs`:

- PC vs addon_rider_pricing: monthly-billing sentence n/a (follows); annual prorated sentence → declared overwrite #1; real-estate annual sentence follows; "Payments are applied to the rider's own balance" follows; landlord-portfolio sentence follows; billed-while-open follows; suspended-base sentence n/a. PC vs addon_rider_removal_and_credit: one-credit-per-reason → declared overwrite #2 (scoped to billing corrections). All other sentences n/a. PASS.
- RW vs addon_evt_benefit_authorization: covered-before-benefit follows (rule sentence 1); replace/repair threshold sentence → declared overwrite #1; amount sentence → declared overwrite #2 (scoped to repair/replacement); pumping, allowance and cash-in-lieu sentences n/a; one-open-resolution and reversal sentences follow. The request limit above `per_request_cap` and the uncapped after-hours addition are covered by overwrite #2. The parameter_schema gloss "per_request_cap: Maximum rider benefit on one service request" is a definition rather than a policy sentence; RW can pay above it (Observation O-7).
- RC vs addon_rider_removal_and_credit: customer-decision/effective-date sentence follows; removal-allowed sentence follows; monthly-billing sentence follows ("credited zero"); annual free-look/pro-rata sentence → declared overwrite #1; "No admin fee … negative credited as zero" → declared overwrite #2 (negative-as-zero carried into #1's replacement); base-cancellation sentence ("credited by the same method") is scoped back to the base rule by RC's first sentence. After overwrite #1 the base clause it points to ("the same method") has been superseded without a scope qualifier, so which text governs a base-termination credit is not stated (Observation O-8; no task in this difficulty reaches a base termination). One-credit-per-reason → declared overwrite #3. Refund-route sentence follows. PASS.
- VF vs addon_evt_service_request_and_fees: active-rider and base-in-force sentences follow; fee sentence → declared overwrite (scoped to homeowner base); concurrent-visit sentence follows; recall/pumping no-fee sentence: VF says any recall carries no visit fee, while base exempts a recall "placed no later than repair_guarantee_days…", but base assigns a fee only to `new_failure` requests in the first place, so the conclusions do not differ. Refund and pumping-limit sentences n/a. PASS.
- HA vs addon_evt_benefit_authorization: allowance sentence → declared overwrite (scoped to haul-away); "once per type per request, count toward term_cap" carried ("owed once", "counts toward the rider's term_cap"). PASS.
- CL vs addon_evt_benefit_authorization: cash-in-lieu sentence → declared overwrite #1; amount sentence → declared overwrite #2 (scoped to cash settlements); one-open-resolution follows. PASS.

No undeclared override found, and no anonymous intermediate, 0/1 multiplier or dropped branch.

### factor_ladders

Structure per policy (labels as declared; P=parameter, M=method; MS=multi-source; XD=cross_difficulty):

| policy | factors (label) | P / M | MS factors | XD factors |
| --- | --- | --- | --- | --- |
| PC | pc_guest_size (P), pc_prepayment (P), pc_bundle (P), pc_tenure (P), pc_autopay (P), pc_billed_span (M) | 5 / 1 | guest_size (rider stated sqft ∧ homeplan sqft), bundle (lineplan ∧ hvaccare) | homeplan ×5, lineplan |
| RW | rw_work_basis (M), rw_request_limit (P), rw_hvac_member (P), rw_clean_history (P), rw_after_hours (P) | 4 / 1 | request_limit (tier ∧ term), hvac_member (component ∧ hvaccare), after_hours (urgency ∧ weekday) | homeplan, hvaccare |
| RC | rc_unearned_share (M), rc_retention (P), rc_processing_fee (P), rc_offset_share (P) | 3 / 1 | retention (lineplan ∧ hvaccare), offset_share (homeplan premium ∧ homeplan claims) | homeplan ×3, lineplan |
| VF | vf_fee_basis (M), vf_tenure_cut (P), vf_line_cut (P), vf_repeat_cut (P), vf_autopay_cut (P) | 4 / 1 | fee_basis (trade ∧ fee vs tier fee), line_cut (lineplan ∧ trade) | homeplan ×3, lineplan |
| HA | ha_start_limit (M), ha_equipment (P), ha_removal_share (P), ha_renewals (P), ha_household (P), ha_rider_autopay (P) | 5 / 1 | removal_share (determination cost ∧ replacement cost) | homeplan ×2 |
| CL | cl_cash_basis (M), cl_line_rate (P), cl_autopay_rate (P), cl_settlement_deduction (P), cl_payment_record (P), cl_tier_bonus (P) | 5 / 1 | settlement_deduction (fee entry ∧ determination date) | homeplan ×3, lineplan |

Mechanical checks, all policies: 4–6 factors, ≥2 parameter and ≥1 method by label; each ladder has 3 tiers stated in full in the rule and implemented as the branches of the `decides` binding; no two tiers of one ladder select the same value or method; `decides` is always an input, never `result`; binding sets are disjoint; each factor's fall-through equals its `baseline`; each policy's `baseline.rule` is a subset of its rule sentences, and its default keys match `baseline.params` (VF's `params: []` is consistent, since its baseline uses only the homeowner contract's elected fee). Labels are honest: the six `method` factors change how the quantity is formed (proration day/month/coverage-start basis; recall-zero / replacement / repair basis; free-look/day/month share; max/min/as-is fee basis; max/average/own allowance; replacement/average/repair basis). Each `parameter` factor swaps a number.

Realism of the ladders (the brief makes realism first-class; judged against how US home-warranty add-on programs actually price, credit and settle):

- **F-3 (SOURCE-FACTOR RED) rw_hvac_member — the middle tier can never be reached.** RW reads "hvac_uplift_pending when that inspection is still pending" on "the customer's active HVAC maintenance agreement" (compute: `CFIELD('hvaccare','inspection_result', status='active') == 'pending'`). Under the hvaccare charter an agreement becomes active only after a passed inspection: lifecycle `enrolled → active` "The qualifying inspection finds the equipment serviceable and the agent activates the agreement"; event `hvaccare_activation` "The agreement becomes active after a passed inspection"; rule "An agreement is activated only when the qualifying inspection result is passed…". So the `pending` tier never applies, the ladder has two reachable tiers (passed → 400; otherwise → 0), and the three-tier requirement fails for this factor.
- **F-4 (SOURCE-FACTOR RED) pc_billed_span — the condition is not one any warranty business weighs for this quantity.** The method used to prorate a rider's annual premium (days from coverage start / whole months / days from add date) is selected by how many *homeowner service requests* the customer placed in the last 12 months. Rider and contract premiums are prorated by a fixed published convention (daily or monthly, often per state filing). No business switches proration method on a customer's claim count under a different contract. With this factor struck, PC has no `method` factor.
- **F-5 (SOURCE-FACTOR RED) rc_unearned_share — tier 2 condition is not weighed for this quantity.** Whether the unearned premium of a removed rider is prorated by days or by whole months depends on whether the *base homeowner contract* is in its 3rd term or later. US warranty cancellation refunds follow one pro-rata convention, typically set by state service-contract law, and that convention does not change with tenure on another contract. The free-look tier (share one) is real.
- **F-6 (SOURCE-FACTOR RED) rc_offset_share — the condition is not weighed for this quantity.** Whether rider benefit already paid is deducted from the rider's removal credit is decided by the 24-month loss ratio of the customer's *homeowner* contract (zero offset when homeowner claims ≤ 25% of homeowner premium). Real programs deduct claims paid under the cancelled coverage itself, or do not deduct at all, uniformly. None waives that deduction because a different contract ran clean. With F-5 and F-6 struck, RC keeps 2 factors and no `method` factor.
- **F-7 (SOURCE-FACTOR RED) cl_cash_basis — unreal fall-through and unreal condition.** The cash basis of a cash-in-lieu settlement is "the repair estimate" (fall-through and baseline, then ×0.80 − 50), the average, or the replacement cost, depending on the base homeowner term number. Cash in lieu is offered in place of a *replacement*: the industry (and this scenario's own base rule, "Cash in lieu equal to the contracted replacement_cost") prices it from the contracted replacement cost. No warranty company pays a replacement-due customer from the repair estimate, and none makes the basis depend on tenure.
- **F-8 (SOURCE-FACTOR RED) cl_autopay_rate and cl_payment_record — conditions not weighed for this quantity.** The cash value of a failed pool pump or other component rises with the payment *method* of the homeowner premium (ACH/card) and with the count of rider premium payments in the last six months. Neither is a settlement input in any warranty program. With F-7 and F-8 struck, CL keeps 3 factors and no `method` factor.
- **F-9 (SOURCE-FACTOR RED) vf_autopay_cut — condition not weighed for this quantity.** The rider service call fee drops by $10/$5 with the payment method of the homeowner premium. Service call fees are the fixed per-visit amount the contract elects; autopay incentives, where they exist, discount premiums, not trip charges.
- **F-10 (SOURCE-FACTOR RED) ha_household and ha_rider_autopay — conditions not weighed for this quantity.** The haul-away allowance pays toward a *documented* disposal cost. It rises when the customer placed no homeowner service requests in 12 months, and when ≥6 rider premium payments were made by ACH. No program sizes a disposal/removal allowance on claim frequency under another contract or on premium payment method. With both struck, HA keeps 4 factors (1 method).

Weaker realism concerns, recorded as observations (each has an analog in warranty or adjacent insurance practice, so no consequence can be demonstrated):
- O-9 pc_prepayment: the published 10% annual-pay discount becomes the fall-through for *late* payers only, while an ordinary customer who pays at or before term start gets 12%/15%. PC's `home_sqft_mark` 3000 sits beside the same company's homeowner oversize threshold of 5000 sq ft (`oversize_home_threshold_sqft`).
- O-10 rw_request_limit (tenure/tier raising the per-request cap to 3200/2800 above the rider's own cap) and rw_clean_history (claim-free uplift of the per-request limit): limit increases for loyalty or claim-free history are not a known home-warranty practice (the closest analog is "vanishing deductible" auto programs).
- O-11 ha_start_limit / ha_renewals (tenure and renewal loyalty raising a disposal allowance), cl_tier_bonus / cl_line_rate (tier and bundle bonuses on a cash settlement), vf_repeat_cut, vf_tenure_cut, vf_line_cut, pc_bundle/pc_tenure/pc_autopay (bundle, tenure and autopay premium discounts are real marketing levers; on fees, allowances and settlements they are fabricated but not demonstrably impossible).

Counts surviving the tests above: PC 5 (0 method) — FAIL; RW 4 (1 M, 3 P) — passes count but F-3 stands; RC 2 — FAIL; VF 4 (1 M, 3 P) — passes count but F-9 stands; HA 4 (1 M, 3 P) — passes count but F-10 stands; CL 3 (0 M) — FAIL. Whether each surviving factor bears weight, and the per-computation near-miss, is judged in each task's `factor_weight`.

### findings

| id | verdict | summary | bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-POLICY RED (check 3) | `authorize_rider_work_f2a2f75a` advertises `cash_in_lieu` / `allowance` / `septic_pumping`, so the agent-owned tool can book the cash-in-lieu row CL hands to the customer, with identical row id and fields | task 1 (demonstrated there) |
| F-2 | SOURCE-POLICY RED (check 6, latent) | RC and CL wait on *every* covered request / replaced component, while RW and HA owe their write on the *most recent* one only; with two pending records the root can never be fixed | no consequence on either current world (tasks 0 and 1 each have one pending record) |
| F-3 | SOURCE-FACTOR RED | rw_hvac_member "pending" tier unreachable for an active hvaccare agreement | task 0 |
| F-4 | SOURCE-FACTOR RED | pc_billed_span: proration method chosen by homeowner service-request count | task 0 |
| F-5 | SOURCE-FACTOR RED | rc_unearned_share: day vs month proration chosen by base-contract tenure | task 0 |
| F-6 | SOURCE-FACTOR RED | rc_offset_share: rider-benefit offset waived by the homeowner contract's loss ratio | task 0 |
| F-7 | SOURCE-FACTOR RED | cl_cash_basis: cash in lieu of a replacement priced from the repair estimate, method chosen by tenure | task 1 |
| F-8 | SOURCE-FACTOR RED | cl_autopay_rate, cl_payment_record: payment method / payment count change a cash-in-lieu amount | task 1 |
| F-9 | SOURCE-FACTOR RED | vf_autopay_cut: homeowner payment method changes the rider service call fee | task 1 |
| F-10 | SOURCE-FACTOR RED | ha_household, ha_rider_autopay: claim frequency / ACH count change a documented-disposal allowance | task 1 |
| O-1…O-11 | observations | see sections above | — |

## closing_checklist

Written 2026-10-12T13:47Z, after both reveals. This is the only post-reveal section; the sections above were written before any GT was read and have not been edited.

The difficulty **does not close**: not every task passes all four relationships.

- Per-task files: `0.md`, `1.md`, one per task, with `_difficulty.md` alongside. This is the first revision, so there are no older revisions. Each file carries a frozen derivation followed by a comparison.
  - Task 0: SOURCE-FACTOR RED.
  - Task 1: SOURCE-POLICY RED (F-1) + SOURCE-TASK RED + SOURCE-FACTOR RED.
- Coverage and scope: the six extended policies are covered exactly once (task 0 {PC, RW, RC}, task 1 {VF, HA, CL}). Scopes are pairwise disjoint and span each whole tree. Task tools and GT are closed, and the six uuid8s are independent. — holds.
- Trees: each has 2 prerequisite problems, 1 value_input edge (≥ max(1,1)), an owner=user root, and no cycle. The two components of the difficulty graph are acyclic. — holds.
  - Latent charter defect F-2 ("every" vs "most recent") is not exercised by either world.
- Factors: every declared factor bears weight on its world against an honest baseline, and every baseline-alone number is definite and ≠ gold (all figures agree with `computations`). But the realism tests strike:
  - F-3 / F-4 / F-5 / F-6 (task 0);
  - F-7 / F-8 / F-9 / F-10 (task 1);
  - the VF computation lacks a near-miss.
  PC, RC and CL then fall below the factor bounds. — fails.
- Gates: this audit does not re-run them. The coordinator snapshot (all instantiation gates green except the pre-docs traceability unlock) stands as supplied.

Observations that arose at reveal and belong to the tasks are recorded in each task file: T0-O4, T1-O3 (rationale near-miss claims that are false or cannot flip a tier), and the T1 revision-log evidence for F-10.

## revision_2

### charter_global_frozen (revision 2)

- Written before any round-2 GT was read. Auditor: same independent auditor as round 1. The round-1 text above is untouched.
- Hashes verified on disk, matching the coordinator brief:
  - `addon.extended.yaml` sha256=0c739f9b90afb5d73659ee1e9a1239a6eed1825185760bcb304e52206dbd6fc1
  - `task_tools.py` sha256=9506b31ae0c0699f4f3d5588802b6b3b48fcd3c315c43d6797ecb2ac77b16556
  - views 0=d3ce0605…fa23, 1=cae8df63…30eb
- Both shared inputs changed, so every charter-global section is re-derived in full; nothing is carried forward by reference.
- Base copy: still byte-identical to `blueprint/products/addon.yaml` apart from the three trailing comment lines. The blueprint files are unchanged (mtimes 11:59–12:13).
- Entry conditions: gate snapshot supplied (all green except the pre-docs traceability tool-name unlocks); masked views and hashes supplied. Complete.
- Round-2 reading scope:
  - the full rewritten `extended_policies` and `task_tools.py`;
  - homeplan tier parameters (oversize threshold, Silver/Platinum premiums, townhome discount);
  - the hvaccare variant list and the `hvaccare_tuneup_visit` event;
  - `db_schema.json` enums for `hvaccare_visit_events.visit_status`, `addon_claim_events.component` and `homeplan_contracts.property_type`.
  - Realism spot-check: public statute summaries (Tex. Occ. Code §1304.1581; Cal. Ins. Code §12825) on refund pro-rata and claims deduction.

### policy_conflict_scan (revision 2)

- The six policies, their targets and owners are unchanged. Owners: `remove_rider_with_credit_c919c4de` and `accept_rider_cash_settlement_51ff485a` are owner=user; the other four are agent. Graph PC→RC, RW→RC, VF→CL, HA→CL; acyclic; the same two trees.
- New overlap: CL now allows cash "in place of the repair or replacement owed" on the rider's most recently placed request, and RW owes "one repair or replacement authorization, unless the customer settles it in cash" on the same request. The two rules agree, as an exclusion.
- VF now defines "serviced alongside a base visit" as a same-day, same-trade base homeowner request, "whatever the rider request's own concurrent-visit flag shows". Base `addon_evt_service_request_and_fees` exempts a request "serviced in the same visit and trade as an open base contract request". Read on the facts, both require the same trade. VF adds "same day" and drops "open"; the two differ only for an open base request in the same trade placed on another day, and neither world has such a request. Observation O-12 (no consequence demonstrable).
- Scopes: the two trees remain disjoint and jointly cover all six policies.

### rule_compute_equivalence (revision 2)

Every binding re-swept against its rule sentence. All tiers of all ladders appear both in the rule and as branches of the `decides` binding. Findings:

- O-1 (changed form; not closed): RW `item_paid` nets `addon_authorization_reversal` rows filtered by `component=det_comp`. The reversal event's declared fields (addon_service_request_id, event_date, reversed_authorization_number, reversal_reason, amount) carry no component, so a reversal would never be netted, while the rule says "net of every reversal of them". No reversal rows exist in either world. Observation.
- O-2 closed: the RC divisor floor is now in the rule ("counting that divisor as at least one month"). The homeplan-claims inputs are gone.
- O-3 closed: VF `self_in_window` matches "the request being charged is never counted as another request".
- O-4 persists by construction (DSL `RND` is float half-even, tools say half-up). No scored value in either world sits on a half-cent. Task 1's VF tier-credit substitution, (125+25−40)×1.0825 = 119.075, does sit on one; checked against `factor_sensitivity` at reveal.
- PC, RC, VF, HA, CL: no other divergence.

### action_binding_and_uuids (revision 2)

- **F-1 closed.** `authorize_rider_work_f2a2f75a` now books repair or replacement only: "This tool books repair or replacement work only … Any other value is booked as repair". Its row id prefix is `acw_` and its authorization prefix `4w`, distinct from the cash tool (`ace_`, `4`). The agent tool can no longer produce the customer's cash-in-lieu row.
- uuid8 tails unchanged and independent; `(target_tool, computes)` unique; docstrings carry no sequence words; no tool body checks a prerequisite. PASS.

### prerequisite_graph / prerequisite_sentences (revision 2)

- RC: "The removal credit is not fixed until Bridgewell has authorized the repair or replacement owed on the rider's most recently placed service request, when that request's coverage determination is covered." It now selects the same single record RW's rule owes ("The rider's most recently placed service request, when its coverage determination is covered, is owed one repair or replacement authorization"). Action form; fallback still justified (cash or repair/replacement both settle it).
- CL: "The cash settlement is not fixed until the component most recently authorized for replacement under the rider, when its removal cost is documented on its request's coverage determination, carries its haul-away allowance authorization." This selects the same record HA owes ("owed once on the component most recently authorized for replacement … documented on that request's coverage determination"). State form; exactly one write (`authorize_haul_away_allowance_ee656dca`). With F-1 closed, the work tool cannot book an allowance.
- **F-2 closed.**
- PC→RC and VF→CL sentences unchanged. They pass the four-point test as in round 1. VF→CL's `condition` now names the same-day/same-trade test.
- O-5 (state_gate "gates" are record fields) and O-6 (CL's "no repair or replacement is authorized on that request once it is taken" grounds no edge) unchanged; observations.

### override_declarations (revision 2)

- Re-swept sentence by sentence.
- CL's overwrite #1 now also extends cash to the place of a repair; this is declared.
- RW's limit is now "already authorized on the rider for the same component in the current term" instead of per request; this falls under the declared amount overwrite.
- VF: see O-12 above.
- No undeclared override found. O-7 and O-8 unchanged.

### factor_ladders (revision 2)

| policy | factors (label) | P / M | multi-source | cross-difficulty |
| --- | --- | --- | --- | --- |
| PC | guest_size (P), prepayment (P), bundle (P), tenure (P), autopay (P), state_proration (M) | 5/1 | guest_size (rider stated area ∧ homeplan sqft vs tier threshold), bundle | homeplan ×5, lineplan |
| RW | work_basis (M), item_limit (P), hvac_member (P), maintenance_share (P), after_hours (P) | 4/1 | hvac_member (component ∧ agreement level), maintenance_share (component ∧ visits), after_hours | homeplan, hvaccare ×2 |
| RC | unearned_share (M), retention (P), processing_fee (P), offset_share (P) | 3/1 | unearned_share (timing ∧ ZIP), retention | homeplan ×3, lineplan |
| VF | fee_basis (M), weekend_visit (P), tier_credit (P), follow_up (P), sales_tax (P) | 4/1 | fee_basis | homeplan ×3 |
| HA | limit_source (M), equipment (P), access (P), disposal_state (P), removal_share (P), reassignment (P) | 5/1 | removal_share | homeplan ×3 |
| CL | cash_basis (M), tier_rate (P), class_rate (P), tax_exclusion (P), settlement_deduction (P), diagnosis_offset (P) | 5/1 | settlement_deduction, cash_basis (repair history ∧ estimate vs cost) | homeplan ×2 |

Every ladder has three tiers, distinct outcomes, its fall-through equal to its baseline, the tiers stated in the rule, and an honest label.

Round-1 realism findings, re-judged:
- **F-3 closed.** rw_hvac_member is now keyed on the active agreement's level (Plus / Dual-System Plus / Premier vs Essential / Standard / Dual-System). All three tiers are reachable under the hvaccare charter.
- **F-4 closed.** pc_billed_span is replaced by pc_state_proration: started-month, completed-month or day count by the state rate filing of the property. Proration convention set by state filing is a real mechanism.
- **F-5 / F-6 closed.** rc_unearned_share and rc_offset_share now follow the refund law of the property's state. State service-contract statutes do govern pro-rata refunds and whether paid claims may be deducted: Tex. Occ. Code §1304.1581 prorates and lets the provider deduct claims; Cal. Ins. Code §12825 allows a pro-rata refund less claims paid. The specific attributions (Ohio/NY bar claims deduction; Oklahoma half; Ohio/Texas refund by the day) could not be verified and may misstate real statutes. Observation O-13.
- **F-7 / F-8 closed.** cl_cash_basis now values the work owed: zero under a repair guarantee, the repair estimate when a repair is owed, otherwise replacement cost. Its fall-through and baseline equal the base charter's replacement cost. The autopay and payment-record factors are gone. The new factors are realistic in kind: tier rate, equipment-class wear rate, exclusion of the sales tax Bridgewell avoids by paying cash, and an offset for diagnosis trips already paid.
- **F-9 closed.** vf_autopay_cut is gone. New factors are weekend-visit surcharge, tier credit and state sales tax on the service call.
- **F-10 closed.** ha_household and ha_rider_autopay are gone. New factors are dwelling access (condo/townhome), state disposal fees and reassignment trips.
- **O-9 closed**: prepayment fall-through is now the published rate for ordinary on-time payers, and the size mark is the homeplan tier's own oversize threshold.
- **O-10 closed**: the clean-history uplift is gone; item limit by base tier.
- O-11 partly remains, as observation O-11′:
  - ha_reassignment ties disposal cost to the number of contractor assignments, a weak causal link;
  - cl_class_rate applies a "wear" rate to cash in place of a *repair*;
  - cl_diagnosis_offset deducts trips for which the customer also pays a service call fee;
  - cl_settlement_deduction keeps its 3-day timing tier;
  - vf_follow_up and rc_retention / rc_processing_fee remain marketing-style.
  Each has an industry analog and no demonstrable "no business weighs this", so none is a RED.

Counts: all six policies within 4–6 factors with ≥2 P and ≥1 M after the tests.

### findings (revision 2, charter-global, pre-reveal)

| id | round-1 verdict | round-2 status |
| --- | --- | --- |
| F-1 | SOURCE-POLICY RED | closed (tool restricted to repair/replacement, distinct ids) |
| F-2 | SOURCE-POLICY RED (latent) | closed (RC and CL sentences select the same single record as RW and HA) |
| F-3…F-10 | SOURCE-FACTOR RED | closed (see factor_ladders) |
| O-1 | obs | changed form, persists (reversal netting by component) |
| O-2, O-3, O-9, O-10 | obs | closed |
| O-4, O-5, O-6, O-7, O-8 | obs | persist (no change claimed for O-5…O-8; O-4 is inherent to the DSL) |
| O-11 | obs | partly persists as O-11′ |
| O-12, O-13 | — | new observations (VF concurrency wording vs base; unverified state-law attributions) |

No new charter-global RED.

### closing_checklist (revision 2)

Written after the round-2 reveal at 19:22:56Z; the sections above it were written before.

- Per-task files 0.md and 1.md each carry `## revision_2` with a frozen derivation, then a comparison. Round-1 text is untouched.
  - Task 0: **PASS**.
  - Task 1: **PASS**.
- Coverage and scope: six policies, each claimed once; disjoint trees; tools and GT closed; uuid8s independent. — holds.
- Trees: each has 2 prerequisite problems, 1 value_input edge, a user-owned root and no cycle; the difficulty graph is acyclic. F-2 is closed. — holds.
- Factors: every computation has 4–6 factors (≥2 P, ≥1 M); each task has multi-source and cross-difficulty factors; every factor bears weight against an honest baseline; each baseline alone gives a definite number ≠ gold; every computation has a near-miss. Every figure agrees with `computations`. — holds.
- Gates: the coordinator's round-2 snapshot is all green except the pre-docs traceability tool-name unlocks, as supplied. Not re-run by this audit.
- Round-1 REDs: F-1…F-10 and the VF no-near-miss item are closed. Nothing regressed: the owners of both user tools, the six uuid8s, the base copy and the four edges are unchanged.
- Outstanding observations (not grounds for rework):
  - O-1′ — reversal netting by component;
  - O-4 — DSL half-even rounding;
  - O-5 … O-8 — unchanged from round 1;
  - O-11′ — marketing-style ladders;
  - O-12 — VF concurrency wording vs base;
  - O-13 — unverified state-law attributions, including the Ohio claims-deduction bar that decides task 0's offset;
  - T0-O1 / T1-O1 — state-gate edges carry no value on these worlds;
  - T1-O4 — the self-contradictory concurrency flag.
- **The difficulty passes the source-layer audit in revision 2.**

## revision_3

### charter_global_frozen (revision 3)

- Written before any round-3 GT was read (system clock when this section was written: 2026-10-12T23:29:55Z). Auditor: same independent auditor. Earlier revisions are untouched.
- Hashes verified on disk, matching the brief:
  - extended `7a725100…b4f6`
  - tools `ca7e3284…fae4`
  - views 0=`c760acc4…9a25`, 1=`5d33f19e…2402`
- Both shared inputs changed, so every charter-global section is re-derived. The extended file is re-serialised (list indentation changed), so the comparison is by content, not by diff.
- Base copy: still byte-identical to `blueprint/products/addon.yaml` apart from the three trailing comment lines. The blueprint files are unchanged (mtimes 11:59–12:13).
- Also read: `audits/render_notes/addon.md`, the five render-surfaced items routed by the coordinator.
- Gate snapshot supplied: all green, including TRACEABILITY.

### routed render items (verification)

1. **Item 1 (RW retired the parts-lead-time / cannot-be-repaired cases): closed in text.**
   - RW's replaced_by and rule now carry "or when the covered determination records no repair estimate because the contractor found that the component cannot be repaired or that its parts cannot be obtained within parts_lead_time_replace_days calendar days, the component is replaced".
   - CL mirrors it: "when a repair estimate is recorded and is below … a repair is owed …; otherwise the contracted replacement cost". The two policies read a missing estimate the same way.
   - The departure from base is declared: base replaced on a lead-time overrun even with an estimate on file, and RW now replaces only when no estimate is recorded.
   - Residual, **O-15 (latent rule/compute gap)**: the record offers no field for the cause or the lead time, so the test actually applied is "no repair estimate recorded". RW computes `det_est <= 0` and CL computes `det_est > 0` on `LATEST(…) or 0`, which also treats a *recorded* 0.00 estimate as missing. Read literally, the rule treats a recorded 0.00 as an estimate below threshold: RW repairs at 0 and CL owes a repair with a basis of 0. The compute replaces. Neither world has a missing or zero estimate, so no scored value can change.
2. **Item 2 (RC retired clause, scope unstated): scope now named, restatement lossy — NOT fully closed. R3-1.**
3. **Item 3 (VF concurrency vs base, undeclared): closed.**
   - The base sentence "When concurrent_visit_single_fee is true and the rider component is serviced in the same visit and trade as an open base contract request, no rider fee is charged." is now declared superseded. The replaced_by is scoped to homeowner-base riders, keeps "concurrent_visit_single_fee being true, no rider visit fee is charged", and leaves the base test for rental and real estate riders.
   - `same_day_base` now filters `homeplan_contract_id=F('homeplan_contract_id')`, matching "that same homeowner contract".
   - The rule no longer says "whatever the … flag shows". **O-12 closed.**
4. **Item 4 (base pumping rule vs base formula): untouched.** It is in the frozen base (BLUEPRINT-KNOWN) and out of this difficulty's write scope. Recorded as **O-18**: base rule and base formula disagree on the term-cap limit for the included pumping. Neither task touches pumping.
5. **Item 5 (pc_prepayment with a non-homeowner base): closed.**
   - The rule now says "or when no premium payment is on file for the base homeowner contract or the rider's base is not a homeowner contract", and the autopay sentence says "including when the rider's base is not a homeowner contract".
   - `last_base_payment` and `base_pay_method` now filter `homeplan_contract_id=F('homeplan_contract_id')`, matching "the latest premium payment on the base homeowner contract".

### override_declarations (revision 3)

Sentence-by-sentence re-sweep of all eight overwrite entries against the "replaced_by restates every still-in-force part of its retired clause and names its scope" criterion:

- PC → addon_rider_pricing (annual clause): the replaced_by restates the billing occasion ("still billed on the add date or on each renewal term start") and sets the amount for "that premium, and only for that premium, while monthly billing and the real estate buyer-year billing remain under the base rule". See R3-1(b).
- PC → one-credit-per-reason: scoped, unchanged. OK.
- RW → repair/replace clause: see item 1. RW → amount clause: scoped ("every other settlement under a rider remains under the base rule"). OK.
- RC → annual removal clause and → admin-fee clause: both replaced_by texts now say "This removal credit applies to a rider the customer removes, and only to such a rider; a rider that ends because its base contract is cancelled is still credited by the earlier method, under which …". See R3-1(a).
- RC → one-credit-per-reason: scoped. OK.
- VF → fee clause and → concurrency clause: scoped. OK (item 3).
- HA → allowance clause: now restates the other allowances in full ("every other allowance (permit, refrigerant on a sealed-system repair, code violation) still pays the lower of its invoice amount and its allowance, once per type per request, and counts toward term_cap"). OK.
- CL → cash-in-lieu clause: now restates the Bridgewell-offered branch in full ("Cash that Bridgewell itself offers because a like component cannot be sourced remains under the base rule: it equals the contracted replacement cost within the caps, must be accepted no later than …, is paid within …, and the replacement authorization it replaces is reversed in full"). CL → amount clause: scoped. OK.

**R3-1 — SOURCE-POLICY RED, charter-global, latent (no task's scored solution changes).** Two replaced_by texts route an excluded scope back to a retired clause without restating that clause's still-in-force content exactly. A reader of the published charter therefore reaches a different conclusion from the base in a situation the base governs.

- **(a) RC.** The retired base clause reads: "On an annual-billed or real estate base, when removal_credit_on_annual is true, a removal no later than rider_free_look_days … is credited all rider premium paid in the term less addon_msr_term_benefit_paid; a later removal is credited … less addon_msr_term_benefit_paid." The base sentence still in force, "When the base contract is cancelled, the rider ends with it and its unused premium is credited by the same method", sits beside "On a monthly-billed base, rider billing stops from the next base billing period and nothing already billed is credited."
  - RC's restatement, "a rider that ends because its base contract is cancelled is still credited by the earlier method, under which a credit no later than rider_free_look_days … is all rider premium paid in the term less the rider benefit authorized in the term, a later credit is the rider premium paid in the term times the unexpired days divided by the rider term days …", drops three parts:
    - the scope "On an annual-billed or real estate base";
    - the condition "when removal_credit_on_annual is true";
    - the netting of `addon_msr_term_benefit_paid` ("minus addon_authorization_reversal amounts"), now "the rider benefit authorized in the term".
  - Demonstration on a monthly-billed rider whose homeowner base is cancelled mid-term:
    - base: the monthly method applies and nothing already billed is credited;
    - RC's restated "earlier method": premium paid in the term × unexpired/term days is credited.
  - Demonstration on an annual rider whose base is cancelled after a fully reversed authorization:
    - base: the measure nets the reversal (0 offset);
    - restatement: "the rider benefit authorized in the term" deducts the authorized amount.
- **(b) PC.** The base sentence "A rider on a real estate contract is billed as annual-billed for each 12-month buyer contract year" draws its amount from the retired annual clause. PC's replaced_by says "the real estate buyer-year billing remain[s] under the base rule" but restates no formula, so the published charter states no amount for a real-estate rider premium.
  - PC's own first sentence, "A rider whose base contract is billed annually is owed a premium billing correction when the prorated annual rider premium charged for its current term is higher than its corrected term premium", can reach a real-estate rider, since the base says it is "billed as annual-billed". PC's bundle rate is customer-level, so such a rider's corrected premium falls below its charge whenever the customer holds an active line plan and HVAC agreement. The scope sentence says its amount remains under the base rule, and sentence 1 says it is owed a correction.
  - Two conclusions in one situation.
- Neither world has a cancelled base or a real-estate rider, so neither task file carries a consequence. This is the same latent class as round-1 F-2.

### rule_compute_equivalence (revision 3)

Full re-sweep. Changes since round 2:
- PC: prepayment and autopay now read the base contract's payments (item 5). OK.
- RW: `work_cost` gains `det_est <= 0`; see O-15. `item_paid` reversal netting now matches "net of every reversal recorded for that component", so **O-1′ closed** (rule and compute agree; reversal rows carry no component in the base event, so none is recorded and none is netted, consistently).
- RC: no change beyond the replaced_by texts.
- VF: `same_day_base` is contract-scoped (item 3). New sentence: "A rider request placed on a Saturday or Sunday is logged without its fee, and the fee is collected by the representative who next handles the request with the customer." It has no compute counterpart and needs none: it states when the fee entry is booked, not its amount, which is still computed for the request (weekend surcharge by request day) "on the day it is charged". It departs from the base *event trigger* metadata (`addon_service_request` → `addon_service_fee_charge` when new_failure and not concurrent). That metadata is not a policy sentence, so no overwrite is required. Observation **O-16**. Realism: weekend claims logged online and the fee collected on the next contact is a plausible operating practice.
- HA: rewording only ("disposal fee schedule Bridgewell's network applies in the region"). Compute unchanged. OK.
- CL: `cash_basis` gains `det_est > 0` (O-15); the tax wording is reworded to "Bridgewell's tax schedule". OK.
- **O-4 closed** as an artifact claim: tool docstrings now say "rounded to the nearest cent" instead of "half up". The DSL tie behaviour stays unspecified.

### action_binding_and_uuids (revision 3)

Owners unchanged (remove and accept are user; the other four are agent). The work tool still books repair/replacement only, under `acw_`/`4w`, so F-1 stays closed. uuid8s unchanged. No sequence words; no tool checks a prerequisite. PASS.

### prerequisite_graph / prerequisite_sentences (revision 3)

All four edges are unchanged in text, form, kind, gate and resolved_by, and pass as in revision 2. F-2 stays closed. O-5 and O-6 unchanged.

### factor_ladders (revision 3)

- Factor sets, labels and ladders are unchanged from revision 2 except the wording of four schedules. They no longer claim a statute; each is now Bridgewell's own rider rate schedule, filed contract terms, tax schedule or network disposal schedule by region. **O-13 closed.**
- The values and tiers are identical, so counts, labels and ladder structure stand as in revision 2.
- Realism: region-specific company schedules are a real form. The sales-tax schedule correctly carries a tax the state levies; only the attribution wording changed.

### findings (revision 3, charter-global, pre-reveal)

| id | status |
| --- | --- |
| render item 1 | closed in text; residual O-15 (recorded 0.00 vs missing estimate) |
| render item 2 | **not fully closed → R3-1 SOURCE-POLICY RED (latent)** |
| render item 3 / O-12 | closed |
| render item 4 | base, untouched → O-18 |
| render item 5 | closed |
| PC pricing overwrite (tightened) | R3-1(b) latent gap for real-estate riders |
| HA, CL overwrites (tightened) | closed |
| O-1′, O-4, O-13 | closed |
| O-5, O-6, O-7, O-11′ | unchanged (observations) |
| O-8 | superseded by R3-1(a): the base-termination scope is now named but restated lossily |
| new | O-15, O-16, O-18 (observations); R3-1 (latent RED) |

### closing_checklist (revision 3)

Written after the round-3 reveal (2026-10-12T23:30:38Z). The sections above it were written before.

- Per-task results: task 0 **PASS** and task 1 **PASS**. Each figure equals GT, and each file carries `## revision_3`, frozen and then compared.
- Coverage and scope: six policies, each claimed once; disjoint trees; tools and GT closed; uuid8s independent; user-owned roots in both trees; acyclic graph. — holds.
- Factors: unchanged from revision 2 apart from schedule wording; every factor bears weight; honest baselines; near-misses present. — holds.
- Gates: the coordinator snapshot is all green. Not re-run by this audit.
- Routed render items:
  - 1, 3 and 5: closed.
  - 4: base, out of scope (O-18).
  - **2: not fully closed.** The scope is now named, but the restatement for base-cancelled riders is lossy: it drops the annual/real-estate scope, the removal_credit_on_annual condition and the netting of reversals. The tightened PC pricing overwrite leaves real-estate rider billing pointing at a retired formula, while PC's first sentence can still owe that rider a correction. Together these are **R3-1, a latent charter-global SOURCE-POLICY RED**. Neither task's world exercises them, so no task verdict changes, but the charter does not fully meet the routed criterion that "every replaced_by restates every still-in-force part of its retired clause and names its scope".
- Regressions: none. Owners, edges, the work-tool restriction (F-1), the single-record prerequisite sentences (F-2) and all revision-2 factor closures are intact.
- New observations:
  - O-15: a recorded 0.00 repair estimate is read as "missing" by both computes but not by the rule text.
  - O-16: the weekend fee-collection sentence departs from base event-trigger metadata. It is consistent and realistic.
  - O-18: render item 4, a base defect.
- **Closing status:** both tasks pass. The difficulty closes on every per-task relationship, with one latent charter-global item, R3-1, left open against render item 2.


## revision_4

### charter_global_frozen (revision 4)

- Written 2026-10-13T04:06:54Z (system clock), before any round-4 GT was read. Auditor: same independent auditor. Earlier revisions are untouched.
- Hashes verified:
  - extended `eb3dc1d1…9b9f` (changed);
  - tools `ca7e3284…fae4` (unchanged since revision 3);
  - views 0=`c760acc4…9a25` and 1=`5d33f19e…2402` (unchanged since revision 3).
- Base copy is still byte-identical apart from the three trailing comment lines. The blueprint is unchanged.
- The tools did not change, so § revision_3 → action_binding_and_uuids is carried forward by reference on the unchanged hash `ca7e3284…fae4`. Every section that depends on the extended file is re-derived below.
- Mechanical sweep (script, scratch, deleted after):
  - each of the **12** overwrite entries' `replaced_by` appears verbatim in its policy's rule (2 PC, 2 RW, 3 RC, 2 VF, 1 HA, 2 CL);
  - every `compute_basis` quotation is verbatim in its rule;
  - every compute binding has a basis;
  - all four `policy_source` sentences are verbatim in the blocked rules.
  - The reworker's brief cites "13" replaced_by sentences; the file has 12. Count only, no consequence.
- Params, factor ids, labels, ladder lengths, target tools and triggers are identical to revision 3.

### R3-1 and O-15 (verification)

- **R3-1(a) closed.** Both RC replaced_by texts now restate the retired clause for a rider whose base contract is cancelled, in full:
  - the scope "on an annual-billed or real estate base";
  - the condition "when removal_credit_on_annual is true";
  - the free-look branch "less the rider benefit authorized in the term net of reversals" (= addon_msr_term_benefit_paid);
  - the pro-rata branch "the calendar days after the end date through the term end date divided by the days from the later of the term start date and the add date through the term end date, both days counted" (= addon_msr_unexpired_term_days / addon_msr_rider_term_days), "less that same net benefit";
  - "no admin fee applies, a negative result is credited as zero", and "on a monthly-billed base nothing already billed is credited".
  Each part matches the base clause and measures one for one. The round-3 demonstrations (a monthly rider on a cancelled base; a fully reversed authorization) now reach the base's conclusion.
- **R3-1(b) closed.**
  - The PC pricing replaced_by now restates the real-estate premium in full ("at monthly_rider_premium times 12 reduced by annual_pay_discount_rate, multiplied by the days from the later of its term start date and add date through its term end date, both days counted, divided by the number of days in its base term, and rounded to the cent"). This matches addon_msr_rider_term_days.
  - It states the rider "is owed no correction under this policy".
  - PC's first sentence is narrowed to "A rider whose homeowner or rental property base contract is billed annually …".
  - The compute adds `realty_base: F('base_category') == 'realty'` and `result: 0 if realty_base else …`, with a verbatim basis.
  - The round-3 two-conclusion situation (a real-estate rider of a customer holding a line plan and an HVAC agreement) now has one conclusion: no correction.
- **O-15 closed.**
  - RW: "or when the covered determination records no repair estimate above zero because …" ⇔ `det_est <= 0`.
  - CL: "when a repair estimate above zero is recorded and is below …" ⇔ `det_est > 0 and det_est < …`.
  - A recorded 0.00 now reads the same in rule and compute (replacement).
- Further tightened overwrites:
  - RW amount clause and CL amount clause: both now restate the Bridgewell-offered cash amount identically ("the lowest of the contracted replacement cost, per_request_cap less the repair, replacement and cash-in-lieu amounts already authorized on the request net of reversals, and term_cap less the rider benefit authorized in the term net of reversals"). This matches addon_msr_request_benefit_paid (excluding allowances, net of reversals) and addon_msr_term_benefit_paid.
  - CL's cash-in-lieu clause carries the same amount plus the base validity, payment and reversal terms.
  - VF's fee and concurrency clauses now restate the rental and real-estate rules ("still carries the base tier's service_call_fee"; "when concurrent_visit_single_fee is true, no rider fee is charged when the component is serviced in the same visit and trade as an open request on that base contract").
  - The PC and RC one-credit clauses now restate "every other rider credit is still limited to one per credit reason and period".
  All are complete against their retired clauses.

### class sweep (revision 4): every replaced_by vs its retired clause

| policy / retired clause | still-in-force remainder restated? | scope named? |
| --- | --- | --- |
| PC / annual pricing | yes (billing occasion; real-estate formula; monthly unaffected) | yes |
| PC / one credit per reason | yes | yes |
| RW / repair-or-replace | yes (lead-time and cannot-repair cases via "no repair estimate above zero") | yes |
| RW / amount | yes (Bridgewell-offered cash; customer cash routed to CL) | yes |
| RC / annual removal credit | yes (full earlier method for cancelled-base riders) | yes |
| RC / admin fee & zero floor | yes (same text) | yes |
| RC / one credit per reason | yes | yes |
| VF / fee | yes (rental and real-estate tier fee) | yes |
| VF / concurrency | yes (rental and real-estate same-visit test) | yes |
| HA / allowances | yes (permit, refrigerant, code violation) | yes |
| CL / cash in lieu | yes (Bridgewell-offered cash, full terms) | yes |
| CL / amount | yes (refers to the restatement above) | yes |

No undeclared override found.

New latent wording point, **O-19** (observation): RC's prerequisite sentence waits on "every prorated annual rider premium charged in the current term above the corrected term premium". PC now states that a real-estate rider "is owed no correction under this policy", but it still defines the corrected premium in generic sentences. A reader could compute a "corrected term premium" for a real-estate rider below its charge and treat RC as waiting on a correction PC never owes. The natural reading — the correction PC owes — resolves it (real-estate: none owed). Neither world has a real-estate rider. Recorded as an observation because a coherent single reading exists.

### rule_compute_equivalence / prerequisite / factor_ladders (revision 4)

- No change beyond the items above.
- Rule and compute agree everywhere (mechanical sweep plus the item checks).
- The four edges are unchanged and pass.
- Factor structure and realism are as in revision 3.
- O-5, O-6, O-7, O-11′, O-16 and O-18 are unchanged (observations).

### findings (revision 4, charter-global, pre-reveal)

| id | status |
| --- | --- |
| R3-1(a), R3-1(b) | closed |
| O-15 | closed |
| new | O-19 (latent wording, observation) |
| regressions | none found |

No charter-global RED.


### closing_checklist (revision 4)

Written 2026-10-13T04:07:33Z (system clock), after the round-4 reveal at 2026-10-13T04:07:17Z. The sections above it were written before.

- Per-task results: task 0 **PASS** and task 1 **PASS**. Every scored value, baseline and factor figure equals GT.
- Coverage and scope: six policies, each claimed once; disjoint trees with user-owned roots; acyclic graph; tools unchanged (owners, uuid8s, the repair/replacement-only work tool). — holds.
- Charter: R3-1(a), R3-1(b) and O-15 are closed. All 12 replaced_by texts restate their retired clause's in-force remainder and name their scope. Rule and compute agree. No undeclared override. **No charter-global RED remains.**
- Gates: the coordinator's snapshot is all green, including TRACEABILITY. Not re-run by this audit.
- Open observations (not grounds for rework):
  - O-5, O-6, O-7 and O-11′ — unchanged from earlier revisions;
  - O-16 — the weekend fee-collection rule vs the base trigger metadata;
  - O-18 — base render item 4, out of scope;
  - O-19 — the real-estate "corrected term premium" wording in RC's prerequisite sentence (latent; a single natural reading exists);
  - T0-O1 / T1-O1 — the state-gate edges carry no value on these worlds;
  - the reworker's "13 replaced_by" count (the file has 12).
- **The difficulty passes the source-layer audit in revision 4.**
