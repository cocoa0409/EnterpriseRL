# Policy-task audit — utility_line_repairs / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiating agent.
- Freeze time: 2026-10-12T13:36Z. Written before any task's GT was revealed; nothing below derives from `evaluation_criteria`, `computations`, `charter_scope`, `prerequisite_closure`, `solvability_contract`, `design_rationale` or `required_documents`.
- Frozen inputs (sha256, verified on disk at audit start, equal to the brief):
  - `tasks/utility_line_repairs/lineplan.extended.yaml` c1f9660bc30ce797793ffd21d341038182c5fe03b18c9e223511b73c8bff8c8f
  - `tasks/utility_line_repairs/task_tools.py` 8571f32d973cff92403a3fd280b5bf55b2906a6adc53b1ffd091cebd4f5ca543
- Read: `blueprint/products/lineplan.yaml`, `blueprint/products/homeplan.yaml` (variant parameters and plan-upgrade rule only), `blueprint/share_tools.py`, `blueprint/db_schema.json`, the extended charter, the tool module, and the evaluator semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/LATEST/SUM/CPARAM/CFIELD/within_months).
- Masked / not read: every field listed under `_masked_keys` of the coordinator's views; `worklog.md`; any other scenario; any sibling difficulty.
- Entry conditions (Step 0): gate snapshot supplied in the brief (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; TRACEABILITY NOT OK only for pre-docs unlock misses; validate_scenario only "required document not found"). Masked views and hashes supplied. Entry conditions met; not re-run by the auditor.

### policy_conflict_scan

- Base copy: the ten base sections of the extended file (`category` … `policies`) parse equal to `blueprint/products/lineplan.yaml` (mechanical YAML equality, every key SAME).
- Five extended policies, all with subject `lineplan_repair_authorization`, separated by the object they book:
  - `lineplan_ext_slab_access_payment` — allowance type slab access, interior supply/drain lines (`authorize_slab_access_payment_bcc8b3fe`, `payment_amount`).
  - `lineplan_ext_interior_work_payment` — customer-approved permanent work on interior supply/drain lines (`approve_interior_line_work_4d5cfcfa`, `bridgewell_payment`).
  - `lineplan_ext_public_way_payment` — allowance type public way restoration, exterior water/sewer/gas lines (`authorize_public_way_restoration_c5bbe6ee`, `payment_amount`).
  - `lineplan_ext_lawn_restoration_payment` — allowance type landscaping restoration, exterior lines (`authorize_lawn_restoration_4590e15f`, `payment_amount`).
  - `lineplan_ext_exterior_work_payment` — customer-approved permanent work on exterior lines (`approve_exterior_line_work_7ea09e9b`, `bridgewell_payment`).
- No two policies settle the same quantity on the same object: allowance types are disjoint, and the two permanent-work policies split on interior vs exterior line types. Triggers (`on_request`), eligibility (inherits base `line_covered_before_work`), time anchor (request date), terminal state (one new `lineplan_claim_events` authorization row) are compatible.
- Cross-category reads: homeplan only (status, property_address, start_date, slab_leak_access_allowance / plumbing_leak_cap / variant_name) — read-only branch inputs, no write to homeplan.
- Scope partition derivable from the prerequisite graph: {slab → interior} and {public way, lawn → exterior}; two disjoint trees covering all five policies, consistent with M=2. (Whether each task claims exactly one tree is checked per task after reveal.)
- Sibling inconsistency (observation O-4 below): for a "continuation" request (new failure within 14 days after a temporary repair authorized on another request), the three allowance policies bound their payment by an open benefit that does NOT deduct the temporary-repair request's amounts (`s_open`/`w_open`/`l_open` deduct only this request and, for a recall, the completed-repair request), while the two permanent-work policies DO deduct them (`i_committed`/`e_committed` continuation tier). Neither task world contains a continuation request, so no consequence is demonstrable here.

### rule_compute_equivalence

- Mechanical sweep: for all five policies every `compute_basis` value is a verbatim substring of that policy's `rule` (whitespace-normalised); every compute binding has a basis and every basis key a binding; every sentence of every `baseline.rule` is in the `rule`; every `overwrite[].replaced_by` is in the `rule`; every prerequisite `policy_source` is in the blocked policy's `rule`.
- Manual sweep, per tier: every ladder tier of every factor is a sentence of the rule and a branch of its `decides` binding, and every branch of each `decides` binding is a stated tier (slab: recall offset 3, alignment 3, depth 3, tenure 3; interior: scope 3, workmanship 3, reroute 3, household 3; public way: offset 3, scope 3, partner 3, household 3, coverage 3, plating 3; lawn: offset 3, excavation 3, household 3, backfill 3, tenure 3; exterior: scope 3, workmanship 3, coverage 3, material 3, co-funding 3).
- Order of operations: slab `s_figure = allowance × alignment × depth + tenure`, then offset, then `MN(…, s_open)`, `RND(…,2)` once — matches "multiplied first by … and then by …, with the slab tenure addition then added; the slab recall offset acts on that figure, and the interior occurrence benefit still open limits the result last … rounded to the cent once, at the end". Same verified for public way (scope × partner × household + coverage + plating) and lawn (excavation × household + backfill + tenure). Interior `RND(i_open + i_restored + i_reroute + i_household,2)` and exterior `RND(e_open + e_restored + e_coverage + e_material + e_cofund,2)` match their "plus … plus …" sentences.
- Window convention: "an entry falls within a public-way/exterior window when fewer whole months than the window separate its posting date from that day" ↔ `_within`: `0 <= MONTHS(entry_date, NOW) < window`. "Counted in whole months from … start date to the request date" ↔ `MONTHS(start, request_date)` (day-of-month floor). Recall "no later than the plan's repair guarantee days after" ↔ `DAYS(done, date) <= P('repair_guarantee_days')`.
- Wording residue (observation O-3/O-5): the rules say the payment is "figured once … as of its request date", and the public-way/exterior windows "run back from the day the payment is figured", while `_within` measures from `NOW` (frozen date). On both task worlds the two anchors select the same rows (shown per task), so no consequence is demonstrable.
- No compute invents a basis; no rule sentence is left unimplemented. PASS.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are five distinct pairs, each claimed by one policy.
- Docstrings: each describes only its own row effect; none names another tool or states a sequence position. Ordering-word scan finds only "The authorization then appears in the plan's claim history" in the two approve tools — an intra-call effect, not a cross-tool order. No confirmation/review/wait procedure is added.
- Tool bodies: each does one `ctx.create("lineplan_claim_events", …)` with the passed values; none checks a determination, a prior allowance, a cap or any prerequisite; none computes an amount. The tool layer judges no prerequisite.
- uuid8s: bcc8b3fe, 4d5cfcfa, c5bbe6ee, 4590e15f, 7ea09e9b — pairwise distinct, no shared prefix/suffix, no sequence pattern. PASS.

### prerequisite_graph

- `prerequisite` present on all five policies (`[]` on slab, public way, lawn).
- Edges: interior → slab (`value_input`, gate `i_this_net`); exterior → public way (`value_input`, gate `e_this_net`); exterior → lawn (`value_input`, gate `e_this_net`). Every `problem` is another extended policy id; none points at a base policy or itself; the graph is acyclic (depth 1).
- `form: state` on all three; no `fallback_reason` key on any (correct for state form).
- `resolved_by` equals the depended-on policy's `target_tool` in all three; each tool adds an authorization row on the request, and `i_this_net`/`e_this_net` sum all authorizations on the request net of reversals, so the effect ("falls by exactly that payment") holds.
- `gate` names a real binding of the blocked compute in each case. No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite`.
- `condition` vs sentence: the conditions add "net of any reversal of it", a precision the sentences ("carries its slab access entry", "carries the public-way restoration entry owed", "must carry the lawn restoration entry owed") leave implicit; this neither widens nor narrows the state on any reachable world (a reversed entry is no longer "carried" in any ordinary reading). PASS.

### prerequisite_sentences

1. Interior ← slab: "For an interior line that lies beneath a concrete slab or foundation, the interior permanent-work payment is fixed only after the service request carries its slab access entry."
   - Ordering connective "only after"; own result (interior permanent-work payment) joined to a record-visible state (the request carries a slab access entry = an authorization with allowance type slab access on that request, visible through `find_lineplan_claim_events`); no tool name, policy id, snake_case token or row id; scope "an interior line that lies beneath a concrete slab or foundation" matches the condition.
   - Exactly one write of this difficulty creates an allowance of type slab access: `authorize_slab_access_payment_bcc8b3fe` (the other four tools write public_way_restoration, landscaping_restoration, or a non-allowance permanent-work authorization).
   - Derivation: sentence → "slab access entry" → the slab policy's own rule "booked as one allowance authorization of type slab access" → that policy's write. Single reading.
2. Exterior ← public way: "The exterior permanent-work payment is not fixed until the service request carries the public-way restoration entry owed where that work opens a public sidewalk, curb or street."
   - Connective "not … until"; state form; scope "where that work opens a public sidewalk, curb or street" (the public-way rule adds "a whole-line replacement always opens the public way"). Only `authorize_public_way_restoration_c5bbe6ee` writes allowance type public_way_restoration.
3. Exterior ← lawn: "Before the exterior permanent-work payment is worked out, the service request must carry the lawn restoration entry owed where that work is dug by open trench through the yard."
   - Connective "Before"; state form; scope "dug by open trench through the yard". Only `authorize_lawn_restoration_4590e15f` writes allowance type landscaping_restoration. The sentence says "lawn restoration entry" while the record says `landscaping_restoration`; the lawn rule bridges the two in one sentence ("The lawn restoration payment is … booked as one allowance authorization of type landscaping restoration"), so the hop resolves uniquely (observation O-6 only).
- No second wording of any dependency in the blocked rules; the depended-on rules (slab, public way, lawn) do not restate the sentence or mention the permanent-work payment; no cross-problem order is stated in any rule without a declared edge (the "temporary repair" references concern base events, not charter problems). No base rule sentence grounds any edge. PASS.

### override_declarations

Base policy referenced by all five: `lineplan_evt_repair_authorization`. Sentence by sentence:

| Base sentence | Slab / Public way / Lawn | Interior / Exterior |
| --- | --- | --- |
| "Line work is authorized only after a covered determination is on file for the service request." | followed ("covered … service request") | followed |
| "Each occurrence is paid up to the plan's occurrence cap … counted by lineplan_msr_occurrence_benefit_paid, and occurrences are not limited in number." | followed — "never more than the occurrence benefit still open" | deviates (additions above the cap) — declared in `overwrite[1]` |
| "The contractor repairs the failed section, except that the whole line … is replaced when …" | not governed (allowances) | followed (the whole-line proxy, see O-7) |
| "Trenchless methods are used only when …" | n/a | followed (not touched) |
| "When emergency_temporary_repair_covered is true, a temporary repair … counts toward the same occurrence." | followed for a temporary repair on the same request; for one on another request see O-4 | followed (continuation tier deducts it) |
| "Restoration allowances are paid inside the occurrence cap … slab_access_allowance … public_way … landscaping …" | deviates (figure ≠ bare allowance) — declared in `overwrite[1]`, still inside the cap | not governed |
| "Private driveways and patios are restored only when hardscape_restoration_covered is true." | followed (not touched) | followed |
| "Each authorization pays the lower of its invoice_amount and the remaining occurrence benefit …" | deviates — declared in `overwrite[0]` | deviates — declared in `overwrite[0]` |
| "A recall is paid under the original occurrence and its remaining benefit." | followed (recall deducts the completed-repair request) | followed for the open benefit; the additions above the cap are the declared overwrite |
| "An authorization is reversed in full … never after completion." / "The completion report starts the repair guarantee." | followed | followed |

Disguised forms: no anonymous intermediate deviates from base without declaration; no 0/1 multiplier zeroes a base amount; no base branch is dropped. No rule calls a base output a "wrong value". Every conflict found is declared and the merged semantics are unique on both worlds. PASS (findings only; consequences per task).

### factor_ladders

| Policy | Factor | Label | Tiers | Decides | Multi-source | Cross-difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| slab | slab_recall_offset | method | 3 | s_after_offset | yes (request type + completion row / temp-repair row + dates) | — |
| slab | slab_household_alignment | parameter | 3 (1.5 / 1.25 / 1.0) | s_align_rate | yes (homeplan row + allowance + request date) | homeplan |
| slab | slab_depth_rate | parameter | 3 (1.4 / 1.2 / 1.0) | s_depth_rate | no (line_type + urgency on one request row) | — |
| slab | slab_tenure_addition | parameter | 3 (150 / 75 / 0) | s_tenure_add | no (contract start + request date) | — |
| interior | interior_occurrence_scope | method | 3 | i_committed | yes | — |
| interior | interior_workmanship_recovery | parameter | 3 (1.0 / 0.5 / 0) | i_restore_share | yes | — |
| interior | interior_reroute_contribution | parameter | 3 (600 / 400 / 0) | i_reroute | yes (variant param + completion row + request line) | — |
| interior | interior_household_extension | parameter | 3 (300 / 150 / 0) | i_household | yes | homeplan |
| public way | pw_recall_offset | method | 3 | w_after_offset | yes | — |
| public way | pw_scope_rate | parameter | 3 (1.25 / 0.5 / 1.0) | w_scope_rate | yes | — |
| public way | pw_partner_schedule | parameter | 3 (1.1 / 1.05 / 1.0) | w_partner_rate | yes (contract partner + billing rows) | — |
| public way | pw_household_rate | parameter | 3 (1.1 / 1.05 / 1.0) | w_hh_rate | yes | homeplan |
| public way | pw_coverage_addition | parameter | 3 (100 / 50 / 0) | w_cov_add | yes (start date + billing rows) | — |
| public way | pw_plating_addition | parameter | 3 (250 / 125 / 0) | w_plating | yes (request urgency + claim rows) | — |
| lawn | lawn_recall_offset | method | 3 | l_after_offset | yes | — |
| lawn | lawn_excavation_rate | parameter | 3 (2.0 / 0.5 / 1.0) | l_exc_rate | yes | — |
| lawn | lawn_household_rate | parameter | 3 (1.25 / 1.1 / 1.0) | l_hh_rate | yes | homeplan |
| lawn | lawn_backfill_addition | parameter | 3 (60 / 30 / 0) | l_backfill | yes | — |
| lawn | lawn_tenure_addition | parameter | 3 (40 / 20 / 0) | l_tenure_add | no | — |
| exterior | exterior_occurrence_scope | method | 3 | e_committed | yes | — |
| exterior | exterior_workmanship_recovery | parameter | 3 (1.0 / 0.5 / 0) | e_restore_share | yes | — |
| exterior | exterior_coverage_credit | parameter | 3 (400 / 200 / 0) | e_coverage | yes | — |
| exterior | exterior_material_upgrade | parameter | 3 (750 / 250 / 0) | e_material | yes | — |
| exterior | exterior_partner_cofunding | parameter | 3 (500 / 250 / 0) | e_cofund | yes | — |

- Counts as declared: slab 4 (3 parameter, 1 method); interior 4 (3/1); public way 6 (5/1); lawn 5 (4/1); exterior 5 (4/1). All within 4–6, ≥2 parameter, ≥1 method. `decides` is an input binding (never `result`) in every factor; binding sets are disjoint within each policy.
- Tiers: every ladder has three pairwise-disjoint tiers with pairwise-distinct outcomes; every tier is stated in prose in its rule and implemented in compute; each fall-through equals the policy baseline (rate 1.0 / addition 0 / offset "figure in full" / scope "only this request").
- Labels: the five `method` factors change which amounts are deducted (an algorithmic change, stated in the rule); every `parameter` factor substitutes a number into a fixed formula. Honest.
- `baseline.rule` of each policy is self-sufficient (flat allowance or open benefit, capped, rounded once), all its sentences are in the rule, and its `params` keys are the plan parameters it uses.
- Realism of ladders — see findings F-1 (RED) and O-1/O-2 (observations).

### findings

**F-1 — SOURCE-FACTOR RED (unreal ladder: cross-product household factors). Bears on tasks 0 and 1.**
- Symptom: every cross-difficulty factor of the charter raises a line-plan payment because the household also holds a Bridgewell HomeCare home-warranty contract of a given tier or limit:
  - `slab_household_alignment` — slab access allowance × 1.5 when the HomeCare plan's `slab_leak_access_allowance` ≥ 750 (and contract ≥ 12 months), × 1.25 when it is above zero but below 750;
  - `interior_household_extension` — +$300 / +$150 paid *above the interior occurrence cap* when the HomeCare plan's `plumbing_leak_cap` ≥ 2000 / above zero;
  - `pw_household_rate` — public sidewalk/curb/street restoration allowance × 1.1 when the HomeCare plan is Gold or Platinum, × 1.05 for any other HomeCare tier (contract ≥ 24 months);
  - `lawn_household_rate` — lawn restoration allowance × 1.25 for Gold/Platinum, × 1.1 for any other HomeCare tier.
- Root cause: the condition of every non-fall-through tier ("an active HomeCare contract on the same property … whose HomeCare plan carries a slab leak access allowance of at least …", "… plumbing leak cap of at least …", "… when its HomeCare plan is Bridgewell HomeCare Gold or Bridgewell HomeCare Platinum") is not one a utility line protection program weighs when settling a slab-access, public-way-restoration or lawn-restoration allowance or a permanent line-work payment.
- Evidence / demonstration:
  1. The quantities are fixed contractual per-occurrence amounts tied to the restoration or access work itself: base `parameter_schema` — "public_way_restoration_allowance: Per-occurrence amount for cutting and restoring a public sidewalk, curb or street", "landscaping_restoration_allowance: Per-occurrence amount for basic lawn restoration (backfill, seed and straw)", "slab_access_allowance: Per-occurrence amount for accessing interior lines through a slab or foundation". US line protection programs (utility-partnered service-line warranty programs and utility-branded line plans) publish these as flat per-occurrence limits that vary by plan and partner program; none scales the cost of re-pouring a city sidewalk, reseeding a yard or opening a slab by the tier of an unrelated home-warranty contract the household holds. A multi-product relationship is rewarded in this industry, if at all, on the premium (bundle pricing), never as a multiplier on a claim allowance.
  2. The scenario's own base charter publishes the one interaction Bridgewell has between the two products on the same property, and it is coordination of benefits, not enhancement: `lineplan_agg_no_overlapping_lines` — "Line protection plans and home warranty contracts on the same property do not exclude each other: when a failure is covered by both, the line protection plan pays first and the home warranty contract pays only what remains under its own caps." Under that published rule the line plan (primary payer) settles on its own terms and the home warranty's limits govern only its own residual payment; the household factors invert this by making the primary payer's figure depend on the secondary contract's limits (slab, interior) or tier label (public way, lawn). The interior extension in particular pays a fixed sum above the line plan's cap keyed to the HomeCare plumbing cap, for a failure the published coordination rule already routes to HomeCare up to that cap.
  3. The tier labels "Gold or Platinum" for a public-way or lawn rate (`pw_household_rate`, `lawn_household_rate`) have no relation at all to the restoration work being paid; the condition restates which product tier the customer bought from another line of business.
- Demonstrated consequence: four declared factors fail the "condition that line of business actually weighs" test. Struck out, the factor counts fall to slab 3 and interior 3 (below the floor of 4), and neither task retains any factor that decides its tier from another difficulty's records (the only cross-difficulty factors of the charter are these four; `lineplan_ext_exterior_work_payment` declares `cross_category: []`). Per-task consequences in `0.md` and `1.md` under `factor_weight`.
- Affected artifacts: `lineplan.extended.yaml` → `extended_policies[lineplan_ext_slab_access_payment].factors[slab_household_alignment]` and its rule sentence "Slab household alignment rate: …"; `[lineplan_ext_interior_work_payment].factors[interior_household_extension]` and "Interior household extension: …"; `[lineplan_ext_public_way_payment].factors[pw_household_rate]` and "Public-way household rate: …"; `[lineplan_ext_lawn_restoration_payment].factors[lawn_household_rate]` and "Lawn household rate: …"; the `cross_category` blocks of those four policies; the seeded `homeplan_contracts` rows of both tasks that exist to drive them.
- Relation to previous revisions: first audit of this difficulty.

**O-1 — observation (tenure/loyalty additions).** `slab_tenure_addition` (+150/+75), `lawn_tenure_addition` (+40/+20), `pw_coverage_addition` (+100/+50, with no returned-payment charge in 12 months) and `exterior_coverage_credit` (+400/+200, same standing test) add loyalty money to cost-defined allowances/payments. Not a feature of the mainstream US line-protection programs this auditor knows, but tenure-and-good-standing claim enhancements do exist in US consumer protection products (e.g. vanishing-deductible programs), so the "no such business would publish it" demonstration is not made; recorded for the author's realism review.

**O-2 — observation (partner-schedule remittance condition).** `pw_partner_schedule` and `exterior_partner_cofunding` condition the partner rate/co-funding on the premium having been remitted through the partner utility's bill within 12 months. Partner-specific program terms and utility co-funding of customer-side service-line replacement are real; tying them to the billing channel is plausible as "the plan is still billed inside the partner program". No demonstration of unreality.

**O-3 — observation ("figured as of the request date").** Every rule says its payment is "figured once (per service request), as of its/the request date, from the plan's own records", while the prerequisite sentences make the permanent-work payment wait on an allowance entry that the agent books on the handling date (after the request date). A snapshot reading ("only records dated on or before the request date") would leave the new entry out of `i_this_net`/`e_this_net`; that reading makes the same rule's prerequisite sentence ("fixed only after the service request carries its slab access entry") idle, and the "already authorized … net of reversals" clause carries no date cut-off, so it is not taken as a second defensible reading. The snapshot figures are recorded per task for completeness.

**O-4 — observation (continuation case).** The three allowance policies' open benefit ignores a temporary-repair request's amounts in the "continuation" case, while the two permanent-work policies' occurrence-scope continuation tier deducts them; and the base measure `lineplan_msr_occurrence_benefit_paid` defines an occurrence as "a new_failure service request together with any recall request that names it", which does not join a temporary-repair request on another request number. No task world contains a continuation request (task 0 and task 1 are recalls), so no consequence is demonstrable.

**O-5 — observation (window anchor).** "Public-way/Exterior windows counted in months run back from the day the payment is figured" vs "figured … as of its request date" vs compute `_within` anchored at the frozen date. Same rows selected on task 1 (request 2026-10-02, frozen 2026-10-03); no consequence.

**O-6 — observation (entry naming).** The exterior prerequisite sentence says "lawn restoration entry"; the record value is `landscaping_restoration`; the lawn rule's first sentence bridges them. Resolves uniquely.

**O-7 — observation (whole-line proxy and recall link).** The scope/reroute/material/co-funding tiers test "full replacement break count above zero and the most recent completed repair on the same line within the replacement lookback days", a proxy for the base measure `lineplan_msr_prior_breaks_in_lookback >= full_replacement_break_count - 1`; the recall link is "the most recent completed repair on the same line" rather than "the request it names". Both coincide with the base on both task worlds.

## closing_checklist

Not closed. Written after both reveals (2026-10-12T13:39Z); the charter-global section above was frozen before them and is unchanged.

- Per-task files `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; first revision.
- Scopes: task 0 {slab, interior}, task 1 {public way, lawn, exterior} — pairwise disjoint, jointly complete over the five extended policies; task tools closed; uuid8s independent.
- Trees: task 0 n=1 (1 value_input), task 1 n=2 (2 value_input); each has an owner=user root; the difficulty-wide graph is acyclic.
- Factors: FAIL — F-1 (SOURCE-FACTOR RED) on both tasks; after it, slab and interior fall to 3 factors and neither task has a surviving cross-difficulty factor.
- Proof assertions: FAIL — T0-2 and T1-2 (SOURCE-CHAIN RED, false "only claim event" sentences in `prerequisite_closure`/`design_rationale`).
- Unique solution: both tasks' independent derivations equal GT on every scored argument.
- Gate re-run on the final form: not applicable until the reds are reworked.

## revision_2

### charter_global_frozen (revision 2)

- Freeze time: 2026-10-12T18:06Z, before any revision-2 task JSON was opened. Round-1 text above is untouched.
- Inputs: `lineplan.extended.yaml` df3fc4bfa69a9076172b00a5611573cbd6880eadf48d539c0aca50127d63b422 (changed from round 1 → every charter-global section re-derived in full below); `task_tools.py` 8571f32d973cff92403a3fd280b5bf55b2906a6adc53b1ffd091cebd4f5ca543 (unchanged → the tool-body and uuid8 half of `action_binding_and_uuids` is carried forward by reference to round 1 on the strength of this hash). Gate snapshot supplied by the coordinator (all OK; TRACEABILITY only the five pre-docs unlock misses).
- Masked: as in round 1 (`_masked_keys` of the rebuilt views); `worklog.md` not read; no other scenario or difficulty read.

### policy_conflict_scan (r2)

- Base copy still equal to `blueprint/products/lineplan.yaml` (all ten keys SAME).
- Same five policies, same five `(target_tool, computes)` pairs, same disjoint objects (slab access / public way / landscaping allowances; interior / exterior permanent work). Cross-category reads are now only `homeplan.square_footage` (with status, property_address) in the interior and exterior policies; slab, public way and lawn read no other category.
- Round-1 O-4 inconsistency is gone: the slab, public-way and lawn rules now bound the payment by an open benefit that deducts "the service request and … the earlier request whose occurrence it belongs to: for a recall … the request of that completed repair, and for a new failure reported no more than the … continuation days after a temporary repair was authorized on another request for the same line, that temporary-repair request", and `s_link_net`/`w_link_net`/`l_link_net` implement both branches — the same occurrence the permanent-work scope factors use.
- Scope partition unchanged: {slab → interior}, {public way, lawn → exterior}.

### rule_compute_equivalence (r2)

- Mechanical sweep repeated: every `compute_basis` value verbatim in its rule; bindings ↔ basis keys one-to-one; every `baseline.rule` sentence in its rule; every `replaced_by` and `policy_source` in its rule.
- New tiers checked one by one against compute: slab opening rate (drain 1.4 / supply on a townhome or duplex 1.2 / 1.0 — `F('property_type')`), slab cutting addition (emergency and first dispatch, `dispatch_sequence=1` on this request, on the request date 200 / later day 100 / 0), slab partner schedule (Prairie Gas and Light 1.15 / Tri-County Electric Cooperative 1.1 with a utility-bill remittance in 12 months / 1.0); interior wall restoration (whole-line work and HomeCare living area ≥ 2000 → 450 / whole-line and below or none → 300 / 0); public-way cold-weather addition and lawn season rate (Dec–Mar / Nov–Apr / other month: `MONTHS('2000-01-01', date) % 12` gives month − 1, so `== 11 or <= 2` = Dec–Mar and `== 10 or == 3` = Nov/Apr — exact); lawn partner schedule; exterior material upgrade (4 tiers: galvanized + area ≥ 2000 → 1050 / galvanized + below or none → 750 / other material → 250 / 0, all under whole-line work on a water line); exterior frost excavation (Dec–Mar 600 / Nov–Apr 300 / 0); exterior commissioning (whole-line water 175 / whole-line sewer lateral 225 / 0). Each tier is a rule sentence and a branch of its binding, and vice versa.
- Order of operations re-checked against "multiplied first by … then by … with … then added; the … recall offset acts on that figure, and the … benefit still open limits the result last … rounded to the cent once, at the end" for slab (allowance × opening × partner + cutting), public way (× scope × partner + plating + cold), lawn (× excavation × season × partner + backfill); and the "plus … plus …" sums of interior (open + recovery + reroute + wall) and exterior (open + recovery + material + co-funding + frost + commissioning). Match.
- Handling-time wording now: "figured once …, on the day it is booked and from the plan's records as they stand that day; periods said to run to the request date end on the service request's request date", and "… windows counted in months run back from the day the payment is booked". This matches compute (unfiltered sums = records as they stand; `_within` anchored at the booking date; MONTHS/DAYS to the request date). Round-1 O-3 and O-5 closed.
- PASS.

### action_binding_and_uuids (r2)

- Five distinct pairs, one policy each (unchanged). Tool module hash unchanged → docstrings, bodies (single `ctx.create`, no prerequisite or amount check) and uuid8s carried forward from round 1 `action_binding_and_uuids`. PASS.

### prerequisite_graph (r2)

- Same three edges (interior ← slab; exterior ← public way; exterior ← lawn), all `value_input`, `form: state`, no `fallback_reason`, gates `i_this_net`/`e_this_net` exist, `resolved_by` = depended-on target tools, acyclic. Conditions now say "not reversed" instead of "net of any reversal of it" — same state. PASS.

### prerequisite_sentences (r2)

- Interior: unchanged sentence ("… fixed only after the service request carries its slab access entry"); round-1 analysis stands.
- Exterior ← public way: unchanged.
- Exterior ← lawn: now "Before the exterior permanent-work payment is worked out, the service request must carry the landscaping restoration entry owed where that work is dug by open trench through the yard." The state is now named in the record's own words (`landscaping_restoration`); only `authorize_lawn_restoration_4590e15f` writes it. Round-1 O-6 closed.
- No second wording, no tool/policy/snake_case token in any rule (re-scanned), depended-on rules silent about the permanent-work payment, no base sentence grounds an edge. PASS.

### override_declarations (r2)

- Same two declared overwrites per policy (the "lower of invoice amount and remaining occurrence benefit" sentence; the restoration-allowance sentence for the three allowance policies; the occurrence-cap sentence for the two permanent-work policies, whose `replaced_by` now names the new additions: wall restoration; material upgrade, co-funding, frost excavation, commissioning).
- Sentence-by-sentence table of round 1 still holds, with two residues recorded as observations (no task world exercises a consequence):
  - O-11: base "Restoration allowances are paid inside the occurrence cap, never in addition to it: … and permits, camera inspection and cleanout installation where … camera_inspection_covered … are true" names camera inspection as inside the cap; the exterior commissioning contribution for a sewer lateral ("for the camera inspection of the finished lateral") is paid on top of the cap. The exterior overwrite names the occurrence-cap sentence, not this one. The base camera inspection is defined as one "to locate a sewer or drain failure", so the two may be different items; no task has a sewer lateral.
  - O-12: the interior wall restoration is a restoration paid on top of the cap; the base restoration-allowance sentence lists the allowance types it governs (public way, landscaping, slab access, permits, camera, cleanout) and drywall is not among them, and the interior overwrite explicitly declares the wall restoration above the cap. One merged reading.
- PASS.

### factor_ladders (r2)

| Policy | Factor | Label | Tiers (outcomes) | Multi-source | Cross-difficulty |
| --- | --- | --- | --- | --- | --- |
| slab | slab_recall_offset | method | 3 | yes | — |
| slab | slab_opening_rate | parameter | 3 (1.4 / 1.2 / 1.0) | partly (tier 2: request line + contract property_type) | — |
| slab | slab_cutting_addition | parameter | 3 (200 / 100 / 0) | yes (request urgency + dispatch row) | — |
| slab | slab_partner_schedule | parameter | 3 (1.15 / 1.1 / 1.0) | yes (contract partner + billing rows) | — |
| interior | interior_occurrence_scope | method | 3 | yes | — |
| interior | interior_workmanship_recovery | parameter | 3 (1.0 / 0.5 / 0) | yes | — |
| interior | interior_reroute_contribution | parameter | 3 (600 / 400 / 0) | yes | — |
| interior | interior_wall_restoration | parameter | 3 (450 / 300 / 0) | yes (completion row + plan param + homeplan row) | homeplan |
| public way | pw_recall_offset | method | 3 | yes | — |
| public way | pw_scope_rate | parameter | 3 (1.25 / 0.5 / 1.0) | yes | — |
| public way | pw_partner_schedule | parameter | 3 (1.1 / 1.05 / 1.0) | yes | — |
| public way | pw_plating_addition | parameter | 3 (250 / 125 / 0) | yes | — |
| public way | pw_cold_weather_addition | parameter | 3 (300 / 150 / 0) | no (request date) | — |
| lawn | lawn_recall_offset | method | 3 | yes | — |
| lawn | lawn_excavation_rate | parameter | 3 (2.0 / 0.5 / 1.0) | yes | — |
| lawn | lawn_season_rate | parameter | 3 (1.3 / 1.15 / 1.0) | no | — |
| lawn | lawn_partner_schedule | parameter | 3 (1.1 / 1.05 / 1.0) | yes | — |
| lawn | lawn_backfill_addition | parameter | 3 (60 / 30 / 0) | yes | — |
| exterior | exterior_occurrence_scope | method | 3 | yes | — |
| exterior | exterior_workmanship_recovery | parameter | 3 (1.0 / 0.5 / 0) | yes | — |
| exterior | exterior_material_upgrade | parameter | 4 (1050 / 750 / 250 / 0) | yes (contract material + completion row + homeplan row) | homeplan |
| exterior | exterior_partner_cofunding | parameter | 3 (500 / 250 / 0) | yes | — |
| exterior | exterior_frost_excavation | parameter | 3 (600 / 300 / 0) | no | — |
| exterior | exterior_commissioning | parameter | 3 (175 / 225 / 0) | yes | — |

- Counts: slab 4 (3 parameter / 1 method), interior 4 (3/1), public way 5 (4/1), lawn 5 (4/1), exterior 6 (5/1). Within bounds. `decides` never `result`; binding sets disjoint within each policy; tiers pairwise disjoint with distinct outcomes; every tier in the rule and in compute; fall-throughs equal the baselines; labels honest (method = which requests are deducted / offset; parameter = number substituted).
- Cross-difficulty factors: `interior_wall_restoration` (task tree slab→interior) and `exterior_material_upgrade` (tree public way, lawn → exterior), both read `homeplan_contracts.square_footage` of the active HomeCare contract at the same address.
- Realism review of every ladder (round-1 F-1 whole-class sweep):
  - The four HomeCare-tier factors of round 1 are gone. The new cross-difficulty factors weigh home size: wall restoration for an overhead reroute "grows with the size of the home", and a whole-line water service replacement "sized by the plumbing code to the home's water demand, so a larger home needs the next pipe size up". Both are quantities a line contractor and a line plan actually price by house size; the HomeCare record is used only as Bridgewell's record of the living area, not as a reward for holding the product. No unreal condition is demonstrable. Observation O-9: a home without a HomeCare contract falls to the standard tier however large it is ("or with no living area recorded on such a contract"), so the evidence source rather than the house can decide the tier for such a customer; neither task world is such a customer.
  - Tenure/loyalty factors of round 1 (O-1) are gone; nothing replaces them.
  - Seasonal factors (public-way cold weather, lawn season, exterior frost excavation) are calendar-month ladders applied nationwide. Winter street-cut temporary patching, dormant-season sod/erosion blankets and frost excavation are real cost drivers in cold-climate service territories; a single calendar rule would pay frost excavation in a frost-free territory (observation O-10). Task 1's world (Milwaukee, December) is squarely the case the ladder describes.
  - Slab opening rate (attached homes, deeper drain lines), slab cutting addition (same-day vs next-day emergency callout of a cutting crew), commissioning (pressure test/flush/disinfection of a new water service; camera of a finished lateral), partner schedules and co-funding: practices this industry has. The next-day cutting tier carries no rationale sentence of its own (observation O-8), but a next-day emergency premium is not unreal.
- No SOURCE-FACTOR finding at charter level.

### findings (r2)

- Round-1 F-1: **closed** (no factor conditions on a home-warranty tier or limit; replacement cross-difficulty factors weigh home size).
- Round-1 O-1, O-3, O-4, O-5, O-6: closed (see sections above). O-2 (partner remittance condition, now also on the slab and lawn partner schedules) and O-7 (whole-line proxy; recall link to the most recent completed repair) unchanged, still observations.
- New observations: O-8 (next-day cutting tier rationale), O-9 (no-HomeCare households take the standard size tier), O-10 (seasonal ladders not tied to climate), O-11 (sewer commissioning camera vs base camera-inside-cap sentence), O-12 (wall restoration vs base restoration-allowance sentence). None has a consequence on either task world.
- No charter-global RED in revision 2.

### closing_checklist (revision 2)

Written after both revision-2 reveals (2026-10-12T18:07Z); the revision-2 charter-global sections above were frozen before them.

- Per-task files `0.md` and `1.md` each carry round 1 untouched plus `revision_2` with a frozen derivation, a comparison and a PASS on all four relationships; `_difficulty.md` alongside.
- Extended policies fully covered: task 0 {slab, interior}, task 1 {public way, lawn, exterior}; scopes pairwise disjoint (whole trees); task tools closed; uuid8s independently generated and frozen (tool module unchanged from round 1).
- Trees: task 0 one prerequisite, one value_input edge; task 1 two prerequisites, two value_input edges; each root is the customer's own write; the difficulty-wide graph is acyclic.
- Factors: every computation declares a self-sufficient baseline and 4–6 factors (≥ 2 parameter, 1 method); every ladder has ≥ 3 distinct tiers stated in its rule; each task has a multi-source and a cross-difficulty factor (task 0 `interior_wall_restoration`, task 1 `exterior_material_upgrade`, both reading seeded homeplan rows); every factor bears weight against an honest baseline, and every all-baseline figure is definite and differs from gold.
- Round-1 REDs F-1, T0-1, T1-1, T0-2, T1-2: closed. Round-1 observations O-1, O-3, O-4, O-5, O-6: closed; O-2, O-7: unchanged. New observations O-8–O-12: no consequence on either world. No regression found.
- Gates on the final form: re-run by the coordinator after rework (snapshot in the round-2 brief: all OK, TRACEABILITY only the five pre-docs unlock misses); not re-run by the auditor.
- Difficulty passes the source-layer audit.

## revision_3

### charter_global_frozen (revision 3)

- Freeze time: 2026-10-12T20:56Z (system clock), before any revision-3 task JSON was opened. Revision-1 and revision-2 text above untouched.
- Inputs: `lineplan.extended.yaml` 0996935d4dd66e0232d9346b29123dc1f84ebc8743aeba3c544088b8954bd2ef (changed since revision 2 → charter-global sections re-derived); `task_tools.py` 8571f32d… (unchanged → tool half of `action_binding_and_uuids` carried forward from round 1); `audits/render_notes/lineplan.md` (items 1–3 routed, item 4 base). Gate snapshot from the coordinator: all OK including TRACEABILITY.
- Base copy still equal to `blueprint/products/lineplan.yaml` (all ten keys SAME).

### routed render items

1. **Public-way scope vs calculation — closed.** The rule's scope stays "a covered exterior water service line, sewer lateral or gas service line service request", and the cap sentence now names the cap per line in scope: "(the water line occurrence cap for a water service line, the sewer line occurrence cap for a sewer lateral, the gas line occurrence cap for a gas service line)". `w_cap` now maps only those three (`… if w_line == 'sewer_lateral' else …`, septic removed; any other line → 0.0, i.e. outside the scope). Rule and compute now agree exactly. The lawn and exterior rules received the same parenthetical for their own five-line scopes, matching `l_cap`/`e_cap` (sewer cap for "a sewer lateral or a septic line", electrical cap for an electrical service line) — exact.
2. **Unit for living area — closed.** "at least the large-home area in square feet" / "below the large-home area in square feet" and "at least the upsizing area in square feet" / "below the upsizing area in square feet", in the rules and in both ladders; `square_footage` is the field read. Exact.
3. **Recovery share netting — closed.** The rules now read "the … full recovery share of the payment on the authorization that completion closed is added, where that authorization is a section repair (a completed authorization is never reversed, so its payment stands as authorized); … the … half recovery share of that section repair payment is added". Compute: `i_orig_auth`/`e_orig_auth` = `LATEST(work_completion.authorization_number, line)`, `i_orig_repair`/`e_orig_repair` = `SUM(amount, repair_authorization, resolution_type='section_repair', authorization_number=…)`. The unnetted sum is justified by the base sentence "An authorization is reversed in full when the work will not be performed and never after completion", which the parenthetical restates. The quantity moved from "section repair payments on the request" to "the section repair the completion closed"; on both worlds each completed request carries exactly one section repair, which is the authorization its completion row names, so no value moves.
4. **Base cancellation-date conflict — base, BLUEPRINT-KNOWN, not this audit's object;** no extended policy of this difficulty touches cancellation. Recorded only.

### observations of revision 2

- O-8 closed: the cutting ladder's next-day tier now has its own rationale ("a crew called out the next day for a leak that is still running charges a smaller emergency premium").
- O-9 closed as a declared policy choice: "Bridgewell sizes it from the living area on its own records, so a home with no living area on those records is restored at the standard size" (and the same for the galvanized upsizing). The fall-back is stated in the rule.
- O-10 addressed by a frost-zone territory definition — see finding R3-F1.
- O-11 closed: a third scoped overwrite on the exterior policy names the restoration-allowance sentence ("… and permits, camera inspection and cleanout installation where … camera_inspection_covered … are true") and replaces it only "For the acceptance camera inspection of a sewer lateral replaced whole …; every other camera inspection remains under the base rule that it is paid inside the occurrence cap." Its `replaced_by` is in the rule.
- O-12 closed: "drywall is not one of the restoration allowances the base rule pays inside the occurrence cap".
- O-2, O-7 unchanged.

### charter re-derivation (revision 3)

- Rule/compute equivalence: mechanical sweep repeated (every basis verbatim in its rule; bindings ↔ basis keys one-to-one; baseline sentences in rule; all `replaced_by` and `policy_source` in rule). New binding `w_zip_digit`/`l_zip_digit`/`e_zip_digit` = `int(F('property_zip')) // 10000` = first digit of the five-digit ZIP (leading-zero ZIPs give 0); the seasonal tiers now test `(month tier) and (digit in {0,1,4,5,6})`, matching "on a property in the frost zone, a request placed in …; a request on a property outside the frost zone, or placed in any other month, adds/takes …". Exact.
- Prerequisite graph and sentences: unchanged (three state-form value_input edges; sentences verbatim as in revision 2); no snake_case tokens in any rule. PASS.
- Action binding: five pairs unchanged; tools unchanged. PASS.
- Override declarations: revision-2 table plus the third exterior overwrite (O-11). PASS.
- Factor ladders: same factors, labels, tier counts and outcomes as revision 2; the three seasonal factors are now compound (frost zone AND month: contract ZIP + request date). Counts unchanged (4/4/5/5/6). Reachability of the frost zone: `property_zip` is a field of the plan record returned by `find_lineplan_contracts`; the rule states the test in full; nothing hidden.

### findings (revision 3)

**R3-F1 — SOURCE-FACTOR RED (unreal ladder condition: the frost-zone territory). Bears on task 1.**
- Symptom: `pw_cold_weather_addition`, `lawn_season_rate` and `exterior_frost_excavation` now pay their winter and shoulder tiers only "on a property in the frost zone", defined in all three rules as: "A property is in the frost zone when the ZIP code recorded for it on the plan begins with 0, 1, 4, 5 or 6, the northern service territories where the ground freezes below service-line depth in winter."
- Root cause: the territory test is the first digit of the ZIP code, a postal sorting region, and it does not follow where the ground freezes. Bridgewell is "a national home warranty company … in 46 states" (`blueprint.yaml`), so the published definition governs the whole national book:
  - It excludes deep-frost territories: ZIP 800–816 Colorado, 820–831 Wyoming, 832–838 Idaho, 840–847 Utah and 870–884 New Mexico (first digit 8); 995–999 Alaska and 990–994 eastern Washington (first digit 9); and 247–268 West Virginia (first digit 2). Design frost depths in Wyoming, the Colorado and Utah mountains and Alaska exceed those of most included territories.
  - It includes frost-free and shallow-frost postal areas: 006–009 Puerto Rico and the U.S. Virgin Islands, 090–098 overseas military mail (first digit 0), and 400–427 Kentucky / southern Missouri (63–65).
  - The stated basis is also physically inverted: service lines are laid below the local frost line, so winter excavation cost comes from frozen soil above the line. Saying the ground "freezes below service-line depth" describes a frozen line, not a frozen trench.
- Demonstrated consequence: the condition "ZIP begins with 0, 1, 4, 5 or 6" is not one a utility line protection program weighs when settling cold-weather restoration, dormant-season lawn work or frost excavation. Programs that pay for frost conditions do so by climate or frost-depth territory (state or county lists, or frost-depth maps), not by postal first digit. Two customers show it:
  - A Cheyenne, WY (820xx) water-line replacement dug in January takes the "outside the frost zone" fall-through (no frost excavation, no winter patch, no dormant-season lawn rate).
  - A San Juan, PR (009xx) request in January takes the winter tiers.
  No business publishes either treatment for customers in those situations.
- On task 1's own world, Milwaukee 53211 is correctly in the zone and December is correctly winter, so no scored value would move under a correct territory list. The defect is in the ladder's published condition, which task 1's three load-bearing seasonal factors rest on (`1.md` → revision 3). Task 0 has no seasonal factor and is unaffected.
- Affected: `lineplan.extended.yaml` — the frost-zone sentence in `lineplan_ext_public_way_payment`, `lineplan_ext_lawn_restoration_payment` and `lineplan_ext_exterior_work_payment`; `w_zip_digit`/`l_zip_digit`/`e_zip_digit` and the zone clause of `w_cold`/`l_season_rate`/`e_frost`; the three factors' first two ladder tiers.
- Relation to previous revisions: new in revision 3. It replaces revision-2 observation O-10 (calendar months applied without regard to climate) with a territory test that is itself unreal.

**Observation O-13.** Reachability of the frost zone: PASS (contract `property_zip`, rule states the test).

### closing_checklist (revision 3)

Not closed (written pre-reveal from the charter; confirmed after the revision-3 reveal at 2026-10-12T20:57Z — GT unchanged, task 0 PASS, task 1 SOURCE-FACTOR RED): R3-F1 bears on task 1. Everything else in the revision-2 checklist holds on the revision-3 charter: routed items 1–3 closed with rule and compute in exact agreement, O-8/O-9/O-11/O-12 closed, no scored value moved on either world (recomputed), no regression in prerequisite graph, sentences, tools, scopes or factor weights.

## revision_4

### charter_global_frozen (revision 4)

- Freeze time: 2026-10-12T23:53Z (system clock), before any revision-4 task JSON was opened. Earlier revisions untouched.
- Inputs: `lineplan.extended.yaml` fe37e612eed219e47a9daf56cfddc8dc16e5e36fcadb2f8caae651d5211ad487 (changed → re-derived); `task_tools.py` 8571f32d… (unchanged → tool half carried forward from round 1). Gate snapshot from the coordinator: all OK.
- Base copy still equal to the blueprint (all ten keys SAME).

### R3-F1 re-check

- New definition (identical in the public-way, lawn and exterior rules): "A property is in the frost territory when it lies in a state whose plumbing code sets a design frost depth of at least 36 inches for buried water lines across most of the state, because there the soil over a service line freezes deep enough in winter that excavation must break frozen ground: Alaska, Colorado, Connecticut, Illinois, Iowa, Maine, Massachusetts, Michigan, Minnesota, Montana, Nebraska, New Hampshire, New York, North Dakota, Rhode Island, South Dakota, Vermont, Wisconsin and Wyoming." and "The state is read from the first three digits of the ZIP code recorded for the property on the plan: 005, 010 through 069, 100 through 149, 480 through 629, 680 through 693, 800 through 831 and 995 through 999 are the frost territory, and every other ZIP code is outside it."
- **The ZIP-3 ranges match the state list.** 005 and 100–149 are New York. 010–027 MA, 028–029 RI, 030–038 NH, 039–049 ME, 050–059 VT and 060–069 CT. 480–499 MI, 500–528 IA, 530–549 WI, 550–567 MN, 570–577 SD, 580–588 ND, 590–599 MT and 600–629 IL. 680–693 NE. 800–816 CO and 820–831 WY (817–819 unassigned). 995–999 AK. No listed state's ZIP-3 is left out. No unlisted state falls inside: NJ 070–089, military 090–099, PA 150–196, MO 630–658, KS 660–679, ID 832–838 and UT 840–847 all fall outside. 006–009 (PR/VI) is excluded because the first range is the single prefix 005.
- **Rule and compute agree.** `w_zip3`/`l_zip3`/`e_zip3` = `int(F('property_zip')) // 100`, which is the first three digits of a five-digit ZIP, leading zeros included (00501 → 5, 01002 → 10). The zone clause in `w_cold`/`l_season_rate`/`e_frost` is exactly the seven listed ranges.
- **Probe on task 1's world** (only `property_zip` substituted, public-way payment recomputed):
  - inside, winter tier taken: 00501, 01002, 02903, 10001, 48201, 53211, 60601, 68102, 80202 Denver, 82001 Cheyenne, 99501 Anchorage;
  - outside, fall-through taken: 00901 San Juan, 07030, 09012, 15213, 44101, 63101, 66101, 83702, 84101, 85224.
- **Realism.** The listed states are ones whose code or local design frost depth for water service is commonly 36 inches or more over most of the state, from northern-plains and upper-Midwest depths of 42–80 inches to 36–48 inches in New England, New York, Colorado and Wyoming. Every round-3 counter-example now falls the right way: Cheyenne, Denver and Anchorage are in; San Juan and military mail are out. The stated basis is now physically correct ("the soil over a service line freezes deep enough in winter that excavation must break frozen ground"). A state-level list read through ZIP-3 is a territory definition a line protection program can publish.
- **Reachability.** `property_zip` is on the plan record (`find_lineplan_contracts`), and the rule lists the ranges in full.
- **R3-F1: closed.**
- **Observation O-14.** A state-level list is coarse at its margins. Pennsylvania, Ohio, Idaho and Utah have 36-inch-plus zones in part of the state but are excluded under the stated "across most of the state" criterion, and southern Illinois is included under the same criterion. This is a disclosed granularity choice, not a misclassification the rule's own criterion contradicts, and it has no consequence on either world.

### regression sweep (revision 4)

- Mechanical sweep repeated:
  - every basis verbatim in its rule, and bindings ↔ basis one-to-one;
  - baseline sentences in the rule;
  - all `replaced_by` (two, two, two, two and three) and all three `policy_source` sentences in their rules;
  - no snake_case tokens in any rule.
- Factor sets, labels, tier counts and outcomes are unchanged (4/4/5/5/6). The prerequisite graph is unchanged.
- Routed render items 1–3 and observations O-8, O-9, O-11 and O-12 remain closed (scope parenthetical, "in square feet", authorization-level recovery and the third overwrite are all still present). O-2 and O-7 are unchanged.
- Recomputed on both unchanged worlds:
  - every payment, skip figure, commuted-order figure, factor baseline and all-baseline figure is identical to revisions 2 and 3;
  - no regression.

### findings (revision 4)

- R3-F1 closed. No new RED. New observation O-14 only.
- Editorial note (2026-10-12, after the revision-4 reveal): when this section was first written, shell command substitution removed the backticked identifiers from three bullets (Rule and compute agree; Probe; Reachability). Those identifiers were restored after the reveal, with exactly the text drafted before it. No conclusion, figure or verdict was changed.

### closing_checklist (revision 4)

Written after the revision-4 reveal (2026-10-12T23:53Z, system clock).

- Per-task files carry revisions 1–4 in order, each later revision frozen before its reveal. Both tasks PASS all four relationships in revision 4.
- Scopes are disjoint and jointly complete over the five extended policies. The tools are unchanged and closed, with independent uuid8s.
- Trees: task 0 has one prerequisite, task 1 has two. All edges are value_input, each root is the customer's own write, and the whole graph is acyclic.
- Factors: every computation has a self-sufficient baseline and 4–6 honest factors with at least three tiers stated in the rule. Each task has a multi-source factor and a cross-difficulty factor (home size read from seeded homeplan rows). Every ladder's conditions and outcomes are real, including the frost territory as now defined. Every factor bears weight, and each all-baseline figure is definite and different from gold.
- Every RED from revisions 1–3 is closed (F-1, T0-1, T1-1, T0-2, T1-2, R3-F1, R3-T1-1). The routed render items 1–3 are closed. Open observations: O-2, O-7 and O-14.
- Gates on the final form: the coordinator's revision-4 snapshot is all OK, including TRACEABILITY. I did not re-run them.
- **The difficulty passes the source-layer audit.**
