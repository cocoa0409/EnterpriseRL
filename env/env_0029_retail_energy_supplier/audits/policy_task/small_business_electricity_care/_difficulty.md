# Policy-task audit — small_business_electricity_care / charter-global

## charter_global_frozen

- Revision: round 1 (first audit of this difficulty; no older revision exists).
- Freeze time: 2026-10-04 (UTC session clock 16:1x), written before any task's GT was revealed.
- Auditor: independent policy-task auditor (Claude agent), not the author of the artifacts.
- Frozen inputs (sha256, re-computed by the auditor and equal to the orchestrator's HASHES.txt):
  - `env/env_0029_retail_energy_supplier/tasks/small_business_electricity_care/bizpower.extended.yaml` f6ecaf697aad0a191d3a56058b9bd18138e770c299cdc71e08dfe6b7e7a8c594
  - `env/env_0029_retail_energy_supplier/tasks/small_business_electricity_care/task_tools.py` 6250cb0b97ee463285f2a2c7401fd4b240631018829c8798a437b03a913639d8
- Fields permitted: the whole charter (base + `extended_policies`), `task_tools.py`, `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml), `erlbench/`; the DSL semantics of `compute` were read from the primitive definitions in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS/DAYS/SUM/COUNT/LATEST/CFIELD/CPARAM/XSUM/RND; no task data read).
- Fields masked for this section: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`; worklogs. Nothing in this section is derived from a revealed GT.
- Entry conditions (Step 0): the brief supplied the gate snapshot (check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cache_diff INFO; check_cross_fire SCOPE OK; check_traceability deferred until the KB is rendered), the masked views and their hashes. The traceability gate is deferred, not green — recorded as observation O-0 below; it is outside the four relationships of this audit.
- Base copy: lines 1–1208 of the extended charter are byte-identical to `blueprint/products/bizpower.yaml` (`diff` shows only the trailing blank line 1209). Base is verbatim.

### policy_conflict_scan

Six extended policies, all in category `bizpower`:

| id | subject | target_tool (owner) | computes | trigger |
| --- | --- | --- | --- | --- |
| ext_multi_site_credit_amount | bizpower_credit (multi_site_credit) | post_multi_site_credit_fd52d0a7 (agent) | credit_amount_usd | state_due |
| ext_renewal_rate_on_acceptance | bizpower_renew (on or before end) | accept_renewal_offer_d4784688 (user) | renewal_rate_cents_kwh | on_request |
| ext_closure_termination_fee | bizpower_fee_charge (early_termination_fee) | post_early_termination_fee_113aa1f4 (agent) | fee_amount_usd | state_due |
| ext_renewal_loyalty_credit | bizpower_credit (renewal_loyalty_credit) | post_renewal_loyalty_credit_e53d7f06 (agent) | credit_amount_usd | state_due |
| ext_grace_renewal_rate | bizpower_renew (after rollover, in grace) | accept_grace_period_renewal_906a45d5 (user) | renewal_rate_cents_kwh | on_request |
| ext_relocation_transfer_fee | bizpower_site_transfer (+ site_transfer_fee line) | transfer_agreement_site_58988442 (agent) | transfer_fee_usd | on_request |

Overlaps examined:
- `bizpower_renew` is claimed by two policies. Their domains are disjoint by the record: renewal_rate_on_acceptance governs an acceptance "on or before the contract end date" (new term starts the day after the end date); grace_renewal_rate governs an agreement that "has rolled over to month-to-month" (new term starts on the acceptance date). Both declare the same base sentence of `bizpower_renewal` superseded with replacements that partition the situation. No conflict.
- The base sentence "Each explicit renewal earns one renewal_loyalty_credit ..." is superseded twice — by renewal_loyalty_credit ("accepted on or before the contract end date earns one renewal loyalty credit") and by grace_renewal_rate ("A renewal accepted after the agreement has rolled over earns no renewal loyalty credit"). The two replacements are complementary. No conflict.
- `bizpower_credit` is claimed by multi_site and loyalty for different `line_type`s and different tools. No conflict.
- Base `bizpower_site_transfer_terms` "A month-to-month plan is not transferred; the business cancels it and enrolls the new site." stays in force; ext_relocation adds the path "not recorded until the agreement again shows a fixed term". Compatible: the base sentence still forbids moving a month-to-month agreement; it offers cancel+enroll as an alternative path, whose selection depends on the customer's wish (judged per task).
- Cross-category reads: bizgas (multi_site, renewal_rate, grace, relocation) and cni (closure, loyalty), all read-only through CFIELD/CPARAM/XSUM; no write touches another category.
- Terminal states: renewal tools set renewal_election=accepted, auto_renewed=false and new term fields; transfer sets premise_id/site_transfer_date and bills a fee; credit/fee tools add one line each. No two policies write the same field to different values in one situation.

Scope: there are 6 extended policies and M=2. Claimed scope per the brief covers the category and event types; the partition by problem tree can only be read from the tasks' worlds and is settled in the task files. Structurally, the only prerequisite edges are loyalty→{renewal_rate, multi_site, closure} and relocation→grace, so the charter splits naturally into two trees {loyalty, renewal_rate, multi_site, closure} and {relocation, grace}: disjoint and jointly complete.

### rule_compute_equivalence

Swept every `compute` binding of every extended policy against its `compute_basis` (all 6 policies: every `compute_basis` quotation is verbatim in that policy's `rule`, checked mechanically) and back from every rule sentence to compute.

- multi_site: plan_credit / cycle_kwh / load_addon / gas_addon / continuity / cycle_days / length_factor / subtotal / single final rounding each have their sentence. The minimum-site posting condition and the zero-plan sentence are posting gates (result is 0 when plan_credit = 0). Equivalent.
- renewal_rate: offer selection (init_ok 60..90 days inclusive, final_ok ≥30 days, three branches), five adjustments, single application and final rounding — each implemented. `peak_kwh` is MAX over all energy lines with no window, matching "the largest kWh billed on any one energy line of the agreement" (the window is attached only to the average). The renewed-term date sentence is an argument rule (no compute binding), as is the plan/term taken "offered in the final options notice". Equivalent.
- closure: termination anchor three-way branch; remaining months (`MX(0,-MONTHS(end,term))` reproduces "12×years + months, +1 when the end day-of-month is later" — checked on 2026-10-01→2027-03-31 = 6 and on equal/earlier day-of-month cases); winding-down three branches; damages rate; minimum by spend; portfolio deduction; waiver disjunction; assembly order (rate×kWh rounded, max with minimum, minus deduction). Equivalent.
- loyalty: accepted / net_spend (all lines, 12 months by posted_date) / spend tiers / commitment (MONTHS(start,end)+1) / portfolio / continuity / decision bonus / timing / subtotal × multiplier / final rounding — each implemented. One rule promise is not implemented: the `accepted` binding tests renewal_election == accepted with dates present, but not that the acceptance was "on or before the contract end date" (a grace-period acceptance would evaluate `accepted` = True). See O-3.
- grace: expired_end from the final options notice's effective_date; make-good three branches incl. `MN(final_rate, held_rate)` and the 0.15 adder on renewal_election == declined; quick-return DAYS(plan_change_date, NOW); site gas; rollover gap; full-year count; single final rounding. Equivalent.
- relocation: plan_fee, months_left (0 when no end date), term credit, gas-move (pending first, then active-only), usage credit, tenure multiplier, `MX(0, …)` floor, single rounding, zero-fee plan → 0. Equivalent.
- Rounding: every rule says "rounded half up"; `RND` is Python `round` (binary float, ties not half-up). Only an exact tie at the rounding digit could diverge; checked per task (O-2).

### action_binding_and_uuids

- `(target_tool, computes)` pairs are pairwise distinct (table above); each tool is the target of exactly one policy.
- Docstrings: none names another tool, none places the action in a sequence, none carries before/after/first. "while its current term is still in force" (accept_renewal_offer) and "has already rolled over … within the grace period that follows the rollover" (accept_grace_period_renewal) describe the agreement's own state, not another action. No added confirmation, review or wait.
- Function bodies: every tool writes unconditionally (`ctx.update` / `ctx.create`) — no status check, no prerequisite check, no computed value, no refusal or hint. The tool layer judges no prerequisite.
- uuid8s: fd52d0a7, d4784688, 113aa1f4, e53d7f06, 906a45d5, 58988442 — six distinct values, no shared prefix or suffix, no sequential pattern. Pass.

### prerequisite_graph

- Every extended policy has `prerequisite` filled ([] on multi_site, renewal_rate, closure, grace).
- Edges: loyalty→renewal_rate_on_acceptance (value_input, gate `accepted`, form action, fallback_reason present); loyalty→multi_site (value_input, gate `net_spend`, state); loyalty→closure (state_gate, gate `bizpower_billing.line_type`, state); relocation→grace (value_input, gate `months_left`, state). Every `problem` is an extended policy id of this file, none is base, none self. Graph acyclic (two stars of depth 1).
- Every `policy_source` is verbatim in the blocked policy's own `rule` (checked mechanically after whitespace normalisation).
- `fallback_reason` present exactly on the one action-form edge.
- `resolved_by` equals the depended-on policy's `target_tool` on all four edges.
- `kind`/`gate`: the three value_input gates (`accepted`, `net_spend`, `months_left`) are real bindings of the blocked policy's compute. The state_gate's `gate` names a field (`bizpower_billing.line_type`), not an eligibility id; the extended policy carries no `eligibility` list to point at, and the condition is a posting precondition stated in the rule. Observation O-4.
- `condition` vs sentence: (a) loyalty→renewal: condition "renewal election date no later than the expiring contract end date" vs sentence "accepted its renewal offer before the contract end date" (and rule sentence 1 "accepted on or before the contract end date") — "before" is narrower than "no later than" for an acceptance dated on the end date itself. O-5. (b) relocation→grace: condition adds "a plan whose site transfers are allowed" — drawn from the same rule's first sentence, not from the prerequisite sentence; not a strengthening of what the sentence waits on. No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

Four-point test per edge:

1. loyalty → renewal_rate_on_acceptance, action form. "The loyalty credit is fixed only after the business has accepted its renewal offer before the contract end date." Ordering connective "only after"; names the action in business words; no tool, id or snake_case; scope see O-5. Derivation: reader of the loyalty rule learns its result waits on the business accepting the renewal offer before the end date → the policy whose rule describes that acceptance is renewal_rate_on_acceptance ("A business that explicitly accepts its renewal offer on or before the contract end date …") → the write is the customer's acceptance (owner=user). Single reading (the grace policy concerns an agreement that has already rolled over, so it cannot be "before the contract end date"). Fallback test: the fallback_reason claims no record state singles the on-time acceptance out; but the record does: an on-time acceptance leaves a renewal election accepted whose date is earlier than the plan change date (the new term starts the day after the old end), whereas a grace acceptance leaves the election date equal to the plan change date — the relocation edge of this same charter uses exactly that state ("a renewal election accepted on the day its new term began") to single out the grace write. Fallback unjustified → observation O-1 (naming the state "renewal election accepted, dated before the day its new term began").
2. loyalty → multi_site, state form. "The loyalty credit is worked out only once every billed cycle of the agreement in the 12 months before the handling date carries the multi-site credit due on it." Connective "only once"; state named in record words (billed cycle, multi-site credit); no tool/id. The only write in this difficulty that adds a multi-site credit line is post_multi_site_credit (multi_site policy). Single write. Note the multi_site rule computes the amount only for "the agreement's latest billed cycle"; if the uncredited cycle in a world is not the latest, the depended-on rule gives no amount for it — judged per task.
3. loyalty → closure, state form. "The loyalty credit is not posted until every other agreement of the business that stands drop pending or closed with an early termination fee owed carries that fee on its bill." Connective "not … until"; state named in record words; no tool/id. The only write adding an early termination fee line is post_early_termination_fee (closure policy). Single write. "owed" is decided by the closure policy's own rule (method, waiver).
4. relocation → grace, state form. "The relocation of an agreement that rolled over to month-to-month is not recorded until the agreement again shows a fixed term, with a term length, a contract end date and a renewal election accepted on the day its new term began." Connective "not … until"; state named; no tool/id. Writes that could bring it about: accept_grace_period_renewal (grace rule: "The renewed term starts on the acceptance date") — yes; accept_renewal_offer (new term starts the day after the contract end date, so the election date precedes the start) — no. Single write.

The blocked rules carry no second wording, tool name or other problem id about these dependencies; the depended-on rules (renewal_rate, multi_site, closure, grace) do not restate the sentences. The grace rule mentions that a post-rollover renewal earns no loyalty credit — a statement of its own scope, not an order between problems. No rule states a cross-problem order that grounds no declared edge, except the base sentence "A month-to-month plan is not transferred; the business cancels it and enrolls the new site." (base, an alternative path, not an order between declared problems; no task tree rests on it) — observation O-6.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (finding half only).

- multi_site vs `bizpower_agg_multi_site`: s1 (combined across sites) followed; s2 (amount = plan credit when ≥ minimum) declared superseded; s3 (each site from own plan; 0.00 plan counts but receives nothing) followed (amount still starts from the site's own plan credit; zero-plan sentence restated); s4 (C&I sites do not count) followed, inherited; s5 (one per cycle) followed. vs `bizpower_signup_credit`: credits only while active/drop_pending — inherited; credits additive, own line — followed. vs `bizpower_renewal`: no sentence governs the multi-site amount. Pass.
- renewal_rate vs `bizpower_renewal`: s1 (offered plan/term/rate) declared superseded; s2 active only — inherited; s3 start day after end — followed; s4/s5 grace window — out of this policy's domain; s6 loyalty — not this quantity. vs `bizpower_expiry_notices`: the "final options notice governs" sentence declared superseded; compliance windows (s3/s4) are re-used with the same numbers. Pass. Note: the replacement of the expiry-notices sentence drops "Each notice states the plan offered …" content; the plan/term are re-stated in the ext rule ("takes the plan and the term offered in the final options notice"). No scored quantity left ungoverned.
- closure vs `bizpower_etf`: s1 status gate followed; s2 one fee followed ("billed once"); s3 termination date declared superseded; s4 months-remaining formula restated verbatim in substance; s5 per_remaining_kwh sentence declared superseded as a whole (the declared clause names the base fee formula, rate and minimum, so the damages-rate, minimum-by-spend and portfolio-deduction changes fall under a named superseded clause; the replacement text itself only restates the monthly-usage part — O-7); s6 waivers restated; s7 cni waiver restated; s8 closure/relocation do not waive — followed (no waiver added for closure; the anchor change is declared). vs `bizpower_site_transfer_terms`: "A relocation that cannot be transferred is not a ground for waiving" — followed. Pass, with O-7.
- loyalty vs `bizpower_renewal` s6 declared superseded; vs `bizpower_agg_multi_site` / `bizpower_signup_credit`: "Business bill credits are posted only while the agreement is active or drop_pending" inherited; "none offsets a fee or sales tax" — the spend tier reads net spend but does not offset any line. Pass.
- grace vs `bizpower_renewal`: s1 and s6 declared superseded; s3 "when it is made after a rollover, the new term starts on the acceptance date" followed; s4/s5 grace window inherited (15 days). vs `bizpower_auto_renewal`: rollover rate / held rate sentences are read, not changed; "A decline can be reversed only by an explicit renewal acceptance" followed. Pass.
- relocation vs `bizpower_site_transfer_terms`: s1 restated ("is moved" for "may be moved"); s2 active only inherited; s3 new-site conditions inherited; s4 fee declared superseded; s5 month-to-month not transferred — followed and extended by the prerequisite; s6 followed. Pass.

Disguised forms: no anonymous intermediate replacing a base quantity without declaration found; the 0/1 multipliers present (`if plan_credit > 0 else 0`, `if accepted else 0`, `if plan_fee > 0 else 0`) each restate a base existence condition (zero-plan credit, loyalty only for explicit acceptance, zero-fee plan) rather than zeroing a base-fixed amount; no dropped branch (flat and none ETF methods kept; zero-plan multi-site kept).

Unlabelled baseline sentences (closure): the closure rule states its baseline sentences without the word "standard" except the first ("The standard early termination fee measures the termination from …"); the sentences "The site's monthly usage is the average kWh per energy line over … 12 months …" and "Under the per-remaining-kWh method the fee is the remaining kWh times the plan's damages rate per kWh … but not less than the plan's minimum fee" read literally as unconditional, while the later factor sentences and the assembly sentence ("Under the per-remaining-kWh method the fee is put together in this order …") replace them. The more specific sentences and the explicit assembly sentence settle the reading; recorded as O-8 and checked against task 0's world in that task's file.

### factor_ladders

Per policy (effect label as declared → auditor's reading):

| policy | factor | label | decides | tiers | multi-source tier | cross_difficulty | auditor |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_site | site_load_addon | parameter | load_addon | 3 (+4/+2/0) | no | – | ok |
| multi_site | same_site_gas_addon | parameter | gas_addon | 3 (+2.40/+1.00/0) | status ∧ plan term (one bizgas row + its plan) | bizgas | ok |
| multi_site | multi_site_continuity | method | continuity_mult | 3 (×1.25/×1.10/×1) | no | – | **mislabelled**: tiers substitute a number into one fixed formula `subtotal × m` |
| multi_site | credited_cycle_length | method | length_factor | 3 (×days/30 / ×0.5 / ×1) | no | – | ok (tier 1 is a proportional-to-length computation) |
| renewal_rate | renewal_offer_selection | method | start_rate | 3 (init rate / expiring contract rate / final rate) | yes (two notices' dates + rates) | – | ok |
| renewal_rate | renewal_annual_load | parameter | load_adj | 3 | no | – | ok |
| renewal_rate | renewal_load_shape | parameter | shape_adj | 3 (−0.08/+0.10/0) | no | – | ok |
| renewal_rate | renewal_same_site_gas | parameter | gas_adj | 3 | agreement + bizgas billing | bizgas | ok |
| renewal_rate | renewal_tenure | parameter | tenure_adj | 3 | no | – | ok |
| renewal_rate | renewal_history | parameter | history_adj | 3 (−0.04/−0.02/0) | tier 1: loyalty lines ∧ auto_renewed | – | ok |
| closure | termination_anchor | method | term_date | 3 (drop effective / close date / confirmation date) | same agreement row | – | ok |
| closure | winding_down_usage | method | monthly_kwh | 3 (3m avg / mean / 12m avg) | no | – | ok |
| closure | supplied_tenure_damages_rate | parameter | damages_rate | 3 (0.0100/0.0115/plan) | no | – | ok |
| closure | site_size_minimum_fee | parameter | minimum_fee | 3 (100/125/plan) | no | – | ok |
| closure | portfolio_deduction | parameter | portfolio_deduction | 3 (40/20/0) | status ∧ end date of the cni row | cni | ok |
| loyalty | spend_based_loyalty | method | spend_amount | 3 (1.5% of spend / plan + 0.5% / plan) | no | – | ok |
| loyalty | renewal_commitment_bonus | parameter | commitment_bonus | 3 | no | – | ok |
| loyalty | large_facility_portfolio_bonus | parameter | portfolio_bonus | 3 | no | cni | ok |
| loyalty | supply_continuity_bonus | parameter | continuity_bonus | 3 | no | – | ok |
| loyalty | opt_out_decision_bonus | parameter | decision_bonus | 3 | notice ∧ acceptance date | – | ok |
| loyalty | acceptance_timing_multiplier | method | timing_mult | 3 (×1.25/×1.10/×1) | no | – | **mislabelled** (number in a fixed formula) |
| grace | late_notice_make_good | method | grace_start_rate | 3 (min(final, held) / final+0.15 / final) | yes (two notices; notices ∧ renewal_election) | – | ok |
| grace | quick_return | parameter | quick_return_adj | 3 | no | – | ok |
| grace | site_gas_plan | parameter | site_gas_adj | 3 | status ∧ plan term | bizgas | ok |
| grace | rollover_gap | parameter | gap_adj | 3 | no | – | ok |
| grace | full_year_supply | parameter | full_year_adj | 3 | no | – | ok |
| relocation | remaining_term_credit | parameter | term_credit | 3 | no | – | ok |
| relocation | gas_move_credit | parameter | gas_move_credit | 3 | pending row / active row | bizgas | ok |
| relocation | site_usage_credit | parameter | usage_credit | 3 | no | – | ok |
| relocation | transfer_tenure_multiplier | method | tenure_mult | 3 (×0.5/×0.75/×1) | no | – | **mislabelled** (number in a fixed formula) |

Structure checks:
- Counts: multi_site 4 (2 parameter, 2 method declared), renewal_rate 6 (5/1), closure 5 (3/2), loyalty 6 (4/2), grace 5 (4/1), relocation 4 (3/1). All within 4–6 as declared.
- Every ladder has 3 pairwise-disjoint tiers, every tier stated in prose in the rule (condition and value/method) and implemented as a branch of the `decides` binding; no tier lives only in compute; no two tiers of one ladder select the same value or method. Bindings of different factors within a policy are disjoint; no `decides` is `result`.
- Fall-through of every factor equals the baseline sentence of its policy (load/gas/bonuses 0, multipliers 1, start rate = final rate, anchor = confirmation date, monthly usage = 12-month average, damages rate = plan rate, minimum = plan minimum, deduction 0, spend amount = plan credit). Every `baseline.rule` is a sentence (or, for closure, a run of sentences) of the rule.
- Industry realism: the conditions weighed (cycle load, dual-fuel bundling, credit continuity, cycle length, notice compliance, annual load and load factor, tenure, renewal history, winding-down usage, size, C&I portfolio, net spend, term commitment, early decision, quick return after rollover, rollover gap, remaining term, gas following the move) are all quantities retail suppliers do weigh for these amounts; no tier condition holds of every customer reaching the write, with one partial exception: in grace's make-good tier 2 ("both notices inside their windows and the business had declined automatic renewal"), every fixed plan of this charter has `auto_renew_enabled: true`, so a fixed-term agreement that rolled over with both notices compliant must have declined (or have been drop_pending at expiry); the "declined" conjunct therefore nearly restates the other conjunct for customers reaching the grace write, and the fall-through ("otherwise", both compliant and not declined) is reachable only through the drop-pending path. The ladder still has three reachable, distinct tiers; recorded as O-9.
- **Mislabelled `method` factors (F-1)**: `multi_site_continuity`, `acceptance_timing_multiplier` and `transfer_tenure_multiplier` are labelled `method` but each tier only substitutes a different constant into one fixed formula (`subtotal × m`, `subtotal × m`, `reduced_fee × m`, m ∈ {1.25, 1.10, 1} / {1.25, 1.10, 1} / {0.5, 0.75, 1}). Relabelled honestly as `parameter`: multi_site keeps 1 honest method (credited_cycle_length), loyalty keeps 1 (spend_based_loyalty), **relocation keeps 0** — below the floor of 1 `method` per computation.
- Multi-source factors by tree: tree {loyalty, renewal_rate, multi_site, closure} has renewal_offer_selection (two notice records); tree {relocation, grace} has late_notice_make_good. Cross-difficulty: tree 1 has bizgas (same_site_gas_addon, renewal_same_site_gas) and cni (portfolio_deduction, large_facility_portfolio_bonus); tree 2 has bizgas (site_gas_plan, gas_move_credit). Seeding and weight are per task.

### findings

- **F-1 — SOURCE-FACTOR RED (charter-global; bears on task 0 via multi_site and loyalty, on task 1 via relocation).** Symptom: three factors labelled `method` are numeric multipliers. Root cause: `factors[].effect: method` on `multi_site_continuity` (ladder "multiplied by 1.25 / 1.10 / taken as it stands"), `acceptance_timing_multiplier` ("multiplied by 1.25 / 1.10 / left unchanged") and `transfer_tenure_multiplier` ("halved / multiplied by 0.75 / left as it stands"); compute `continuity_mult`, `timing_mult`, `tenure_mult` are constants consumed by an unchanged expression (`RND(multi_site_subtotal * continuity_mult * length_factor, 2)`, `RND(loyalty_subtotal * timing_mult, 2)`, `RND(reduced_fee * tenure_mult, 2)`). Demonstrated consequence: each tier selects a number, not an algorithm, so the label is dishonest; for `bizpower_ext_relocation_transfer_fee` the honest count is 0 `method` factors (remaining_term_credit, gas_move_credit, site_usage_credit, transfer_tenure_multiplier are all number-selecting), below the required 1. Affected: `bizpower.extended.yaml` → extended_policies[0].factors[2], [3].factors[5], [5].factors[3] (and the relocation computation as a whole).
- **O-0** traceability gate deferred (KB not rendered); outside this audit's relationships.
- **O-1** loyalty→renewal_rate fallback_reason unjustified: the state "a renewal election accepted, dated before the day its new term began" singles out the on-time acceptance (the grace acceptance is dated on the day its term begins).
- **O-2** `RND` is Python `round`, not half-up; diverges only on exact ties — checked per task.
- **O-3** loyalty compute's `accepted` does not implement "accepted … on or before the contract end date"; consequence only in a world with a grace-period acceptance (none expected in the loyalty tree) — checked per task.
- **O-4** state_gate edge loyalty→closure names a field (`bizpower_billing.line_type`) as its gate; the extended policy has no eligibility id to point at.
- **O-5** "before the contract end date" (prerequisite sentence) vs "on or before" (rule sentence 1) and "no later than" (condition): differ only for an acceptance dated on the end date itself — checked per task.
- **O-6** base `bizpower_site_transfer_terms` "the business cancels it and enrolls the new site" offers an alternative path for a month-to-month agreement — checked against task 1's persona.
- **O-7** closure overwrite #2 names the whole base per_remaining_kwh sentence as superseded, but its `replaced_by` text restates only the monthly-usage part; the rate, minimum and deduction changes are carried by the rule, not by the replacement text.
- **O-8** closure rule's baseline sentences are unlabelled ("the plan's damages rate", "the plan's minimum fee", "monthly usage is the 12-month average") and literally conflict with the factor sentences; settled by specificity and the assembly sentence — checked per task 0.
- **O-9** grace make-good tier 2's "declined" conjunct nearly restates its other conjunct for rolled-over fixed-term agreements (all fixed plans auto-renew), leaving the fall-through reachable only via drop-pending-at-expiry.

## closing_checklist

Written after both tasks' derivations were frozen and compared (reveal 2026-10-04 16:21 UTC). The sections above were written before any reveal and are left untouched.

- Per-task files: `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` alongside. First revision; no older revision to trace.
- Comparison verdicts: task 0 — policy PASS, tree PASS, unique solution PASS, factors **SOURCE-FACTOR RED** (F-1, labels). Task 1 — policy PASS, tree PASS, unique solution PASS, factors **SOURCE-FACTOR RED** (F-1, transfer-fee computation has no honest `method`). Not every comparison carries a PASS, so the difficulty is **not closed**.
- Coverage and scope: the six extended policies are fully covered — task 0 {renewal_loyalty_credit (root), renewal_rate_on_acceptance, multi_site_credit_amount, closure_termination_fee}, task 1 {relocation_transfer_fee (root), grace_renewal_rate}; the two scopes are disjoint, and each task's tools are exactly its policies' target tools. Task tools and GT are closed (every GT write is one of the six tools; every tool is used by exactly one task). uuid8s independently generated (see action_binding_and_uuids).
- Trees: task 0 has 3 prerequisite problems with 2 `value_input` edges (≥ 2) and one `owner=user` write; task 1 has 1 prerequisite problem with 1 `value_input` edge and one `owner=user` write. Each is acyclic and the difficulty-wide graph (two disjoint stars) is a DAG with no cross-task reference.
- Factors: every computation declares a self-sufficient baseline whose fall-back number differs from gold (10.00 / 9.26 / 348.73 / 100.00 / 9.05 / 50.00 vs 22.55 / 8.65 / 91.25 / 341.65 / 8.16 / 18.00); every factor bears weight on its task's world; ladders are three-tier, distinct and stated in full in the rule; multi-source and cross-difficulty factors are present and seeded in both tasks. **Failing item:** three factors are mislabelled `method` (F-1), and the relocation transfer-fee computation is left with 0 honest `method` factors.
- Gate re-run on the final form: not performed by this auditor (the brief's snapshot is cited in charter_global_frozen; the auditor does not run gates). Traceability remains deferred until the KB is rendered.

Difficulty verdict: **SOURCE-FACTOR RED** (F-1). Policy self-consistency, problem trees and unique solution PASS on both tasks; both blind derivations land on GT on every scored value, owner and order.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2. Written 2026-10-04 ~17:50 UTC, before any round-2 task JSON was opened. Auditor: same independent auditor as round 1. The round-1 text above is left untouched.
- Hash comparison against round 1:
  - `bizpower.extended.yaml`: round 1 f6ecaf69…a8c594 → round 2 **be163ace425f74be28f56cda116da1f27003564c5752d07533412d776e3546dc** (changed → every charter-global section re-derived below).
  - `task_tools.py`: 6250cb0b…3639d8 in both rounds (unchanged → `action_binding_and_uuids` is carried forward by reference: no docstring, body, owner or uuid8 changed).
  - Masked views: task_0.view.json 8d3a44eb… and task_1.view.json 002dfd02… are identical to round 1 (same worlds, same personas).
- Base copy: lines 1–1208 still identical to `blueprint/products/bizpower.yaml` (only the trailing blank line differs); base is verbatim.
- Entry conditions: the brief's round-2 gate snapshot (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred) and rebuilt masked views with hashes were supplied.
- Contamination disclosure: the round-1 GT of both tasks was revealed to this auditor in round 1 and is in its context. The worlds are unchanged, so any round-2 per-task value is not a blind derivation in the round-1 sense; round-2 per-task sections re-derive only what the charter change can move, from the charter text and the world, and say so.

### policy_conflict_scan (revision 2)

Same six policies, same subjects, target tools, `computes` and triggers as round 1; no policy added or removed. The overlap analysis of round 1 (two disjoint `bizpower_renew` domains; complementary replacements of the base loyalty sentence; distinct credit line types; cancel-and-enroll base path) still holds on the new text. Scope partition unchanged: {loyalty, renewal_rate, multi_site, closure} and {relocation, grace}.

### rule_compute_equivalence (revision 2)

Mechanical check on the new file: every `compute_basis` quotation is verbatim in its rule; every compute binding has a basis; every `replaced_by` is verbatim in its rule; every `baseline.rule` is in its rule. Changed bindings checked by hand:
- loyalty `accepted` now adds `DAYS(renewal_election_date, plan_change_date) >= 1`, implementing "a renewal election marked accepted, dated earlier than the day its renewed term begins" — the round-1 gap O-3 is closed.
- loyalty `net_spend` basis now says "the handling date itself included"; `within_months=12` on posted_date includes the handling date (MONTHS = 0). Equivalent.
- closure: `remaining_kwh`, `per_kwh_fee` and `result` now quote the assembly sentence ("first the remaining kWh, the monthly usage times the remaining months rounded half up to a whole kWh, are multiplied by the damages rate …"); the baseline sentences are now marked "standard" ("The standard monthly usage of the site …", "the standard fee is …"). Equivalent.
- grace `grace_start_rate` adds `DAYS(renewal_election_date, expired_end) >= K('early_decline_days')` (7) to tier 2, matching "declined automatic renewal at least 7 days before the expired contract end date". Equivalent.
- relocation: `tenure_mult` replaced by `tenure_charged_fee` = `reduced_fee × 0.5` (≥36 months) / `reduced_fee × months_left / term_months` (12–35 months and term_months > 0) / `reduced_fee`; `result` = `RND(tenure_charged_fee, 2) if plan_fee > 0 else 0`. Each branch is a sentence of "Tenure charging: …"; assembly sentence matches. Equivalent.
- multi_site, renewal_rate: compute unchanged.

### action_binding_and_uuids (revision 2)

Carried forward by reference to round 1 (`task_tools.py` hash unchanged; targets and `computes` unchanged in the charter).

### prerequisite_graph (revision 2)

- Edges: loyalty→renewal_rate (value_input, `accepted`, **form now state**, no `fallback_reason`); loyalty→multi_site (unchanged); loyalty→closure (unchanged); relocation→grace (unchanged). Acyclic; all `problem`s are extended ids; all `policy_source` verbatim in the blocked rule; `fallback_reason` absent on every edge and every edge is state form — consistent.
- `condition` of loyalty→renewal_rate: "renewal election accepted with a renewal election date earlier than its plan change date, the plan change date being the day after the expiring contract end date, so the acceptance was made on or before that end date." The first clause matches the sentence; the appended clause about the plan change date being the day after the expiring end date is not in the sentence (and is not tested by compute) — a slight strengthening, observation R2-O3.
- O-4 (state_gate `gate` names a field) unchanged — carried.

### prerequisite_sentences (revision 2)

1. loyalty → renewal_rate, now state form: "The loyalty credit is fixed only after the agreement shows a renewal election marked accepted, dated earlier than the day its renewed term begins." Connective "only after"; record-visible state in record words (renewal election, accepted, date, renewed term begins = plan change date); no tool/id/snake_case. Writes that bring it about: accept_renewal_offer (renewal_rate rule: "The renewed term starts on the day after the contract end date", acceptance on or before that end date → election date earlier than term start) — yes; accept_grace_period_renewal (grace rule: "The renewed term starts on the acceptance date") — election date equals term start, not earlier — no. Exactly one write; single reading. It is consistent with rule sentence 1 ("accepted on or before the contract end date"), since a start the day after the end date makes "earlier than the start" ≡ "on or before the end". **O-1 and O-5 closed.**
2–4. Unchanged from round 1 (multi_site, closure, grace edges): pass.
No rule gained a second wording, tool name or problem id for a dependency; depended-on rules do not restate the sentences; docstrings unchanged.

### override_declarations (revision 2)

Round-1 sentence-by-sentence conclusions stand for multi_site, renewal_rate, loyalty and grace (their overwrite blocks are unchanged). Changes:
- closure overwrite #2 now replaces the base per_remaining_kwh sentence with the full assembly sentence (remaining kWh × damages rate, rounded; larger of that and the minimum fee; minus the portfolio deduction), so the replacement text now carries every changed quantity of the superseded clause. **O-7 closed.**
- relocation overwrite unchanged (base fee sentence superseded); the new tenure-charging rule falls under that declared replacement ("its amount worked out as this policy states"). Pass.

### factor_ladders (revision 2)

| policy | factor | label | auditor |
| --- | --- | --- | --- |
| multi_site | multi_site_continuity | **parameter** (was method) | honest now |
| multi_site | credited_cycle_length | method | honest (proportional-to-days tier) |
| loyalty | acceptance_timing_multiplier | **parameter** (was method) | honest now |
| loyalty | spend_based_loyalty | method | honest |
| relocation | transfer_tenure_charging | **method** (replaces transfer_tenure_multiplier) | honest: tier 2 prorates the reduced fee by months left / term months, a different computation from tier 1 (fixed one half) and tier 3 (as it stands) |
| grace | late_notice_make_good | method, tier 2 now "declined … at least 7 days before the expired contract end date" | see O-9 below |

Counts: multi_site 4 (3 parameter / 1 method), renewal_rate 6 (5/1), closure 5 (3/2), loyalty 6 (5/1), grace 5 (4/1), relocation 4 (3/1). Every computation now has ≥ 2 honest `parameter` and ≥ 1 honest `method` factor. **F-1 closed.** Fall-through = baseline for every factor (relocation's `tenure_charged_fee` baseline `reduced_fee` = "charged the reduced fee as it stands"); all ladders three-tier, disjoint, stated in the rule; no two tiers share an outcome.

Ladder realism re-checked on the changed ladders:
- **relocation `transfer_tenure_charging` tier 2 "12 to 35 whole months, with a term on record"** and fall-through "fewer than 12 months, or no term on record": the conjunct "with a term on record" holds of every customer who reaches the transfer write. The rule's own first sentence limits the write to "an agreement whose plan allows site transfers"; base `bizpower_site_transfer_terms` says "A month-to-month plan is not transferred"; every plan with `site_transfer_allowed: true` (Fixed 12/24/36, Green 24/36) has `term_months` 12–36; and the policy's own prerequisite sentence holds the write until "the agreement again shows a fixed term, with a term length". So "with a term on record" restates the policy's scope rather than dividing its customers, and the fall-through's "or no term on record" never occurs. **New finding R2-F2 (SOURCE-FACTOR RED, unreal-ladder clause).** The ladder still divides customers by supplied months, so the scored value does not move; the defect is the decorative scope condition the skill's ladder test forbids.
- grace `late_notice_make_good` tier 2: the added "at least 7 days before the expired contract end date" never bites. Tier 2 also requires both notices inside their windows, so the final options notice is ≥ 30 days before the end; base `bizpower_auto_renewal` accepts a decline only "no later than opt_out_window_days [15] calendar days after the final options notice was issued", i.e. ≥ 15 days before the end. Every accepted decline under tier 2's other conjunct is therefore ≥ 15 days before the end, and the rule's example of the fall-through, "a decline made in the last days before the end", cannot occur. The conjunct "declined …" as a whole still divides customers (declined vs not), so this is not a scope restatement; the fall-through remains reachable only through "an expiry while a cancellation was pending", as in round 1. **O-9 not closed (cosmetic change); stays an observation**, now with the impossible example added (R2-O1).
- relocation: the remaining-term credit (more months left → larger credit) and tier 2's proration (more months left → larger charged share) move the fee in opposite directions on the same input. Each is a treatment a supplier could publish; recorded as observation R2-O2, not a demonstrated unreal tier.
- relocation `remaining_term_credit` fall-through "fewer than 6 months, or no contract end date on record": the "no contract end date" disjunct never occurs at the transfer write for the same scope reason (pre-existing since round 1, missed then). It names a case that never occurs rather than a condition that holds of everyone; observation R2-O4.

### findings (revision 2)

Status of round-1 items:
- F-1 — **closed** (labels honest; relocation has a genuine method factor).
- O-1 — closed (edge now state form; the waited-on state singles out the on-time acceptance).
- O-3 — closed (`accepted` tests election date < plan change date).
- O-5 — closed ("dated earlier than the day its renewed term begins" agrees with "on or before the contract end date").
- O-7 — closed. O-8 — closed.
- O-9 — **not closed** (the 7-day qualifier is vacuous under base's opt-out window; observation, see R2-O1).
- O-0, O-2, O-4, O-6 — unchanged, as the reworker states; still observations.

New items:
- **R2-F2 — SOURCE-FACTOR RED (charter-global; bears on task 1).** Symptom: tier 2 and the fall-through of `transfer_tenure_charging` are conditioned on "with a term on record" / "or no term on record". Root cause: `bizpower.extended.yaml` extended_policies[5] rule sentence "Tenure charging: … an agreement supplied 12 to 35 months, with a term on record, is charged … ; an agreement supplied fewer than 12 months, or with no term on record, is charged the reduced fee as it stands." and compute `tenure_charged_fee` (`… if (supplied_months >= K('tenure_mid_months') and F('term_months') > 0) else reduced_fee`). Demonstrated consequence: every agreement that reaches `transfer_agreement_site_58988442` is on a plan with `site_transfer_allowed: true`, all of which carry `term_months` ≥ 12 (base products, rows `variants[1..5].parameters`), and the relocation's own prerequisite sentence holds the write until the agreement "again shows a fixed term, with a term length"; so the condition holds of every customer at this write and divides no one. Affected: extended_policies[5].rule, .compute.tenure_charged_fee, .factors[3].ladder[1..2]. Scored value of task 1 unaffected (it rests on supplied months).
- R2-O1 (O-9 continued): grace tier 2's 7-day qualifier is vacuous, and its example "a decline made in the last days before the end" is impossible under base `bizpower_auto_renewal`.
- R2-O2: relocation's remaining-term credit and tier-2 proration act in opposite directions on months left.
- R2-O3: loyalty→renewal_rate `condition` appends "the plan change date being the day after the expiring contract end date", which the sentence does not state and compute does not test.
- R2-O4: relocation remaining-term fall-through disjunct "or no contract end date on record" never occurs at the transfer write (pre-existing).

### closing_checklist (revision 2)

Written after both revision-2 derivations were frozen and compared (reveal 2026-10-04 17:51 UTC). The revision-2 charter-global sections above were written before that reveal.

- Files: `0.md`, `1.md` and `_difficulty.md` each carry round 1 untouched plus a `revision_2` section; one-to-one with `tasks/0.json`, `tasks/1.json`.
- Comparison verdicts: task 0 — PASS on all four relationships. Task 1 — policy, tree and unique solution PASS; factors **SOURCE-FACTOR RED** (R2-F2). Not every comparison carries a PASS, so the difficulty is **not closed**.
- Coverage/scope: unchanged — six policies fully covered, scopes disjoint, tools and GT closed, uuid8s unchanged and independent.
- Trees: unchanged — task 0 n = 3 with 2 value_input and an owner=user write; task 1 n = 1 with 1 value_input and an owner=user write; the difficulty graph is a DAG; every edge now state form.
- Factors: every computation has 4–6 factors with ≥ 2 honest `parameter` and ≥ 1 honest `method` (F-1 closed); every factor bears weight against an honest baseline; fall-back numbers differ from gold; multi-source and cross-difficulty factors present and seeded. **Failing item:** R2-F2 (relocation tenure-charging conjunct "with a term on record" holds of every customer at the transfer write).
- Round-1 item status: F-1, O-1, O-3, O-5, O-7, O-8, T0-O1, task-0 obs 4, task-1 obs 3 closed; O-9 not closed (cosmetic; observation R2-O1); O-0, O-2, O-4, O-6 unchanged observations. No regression found.
- Gate re-run on the final form: the brief's round-2 snapshot is cited; traceability still deferred.

Difficulty verdict (revision 2): **SOURCE-FACTOR RED** (R2-F2, bearing on task 1 only). Task 0 passes the source-layer audit.

## revision_3

### charter_global_frozen (revision 3)

- Re-audit round 3. Written 2026-10-04 ~18:10 UTC, before any round-3 task JSON was opened. Same auditor. Rounds 1 and 2 above are left untouched.
- Hashes vs round 2: `bizpower.extended.yaml` be163ace… → **c9fc58a2cc7301b47a7bcfec01f0b4d9745dda1dbf6c8bf0570869de8dadbc89** (changed); `task_tools.py` 6250cb0b… (unchanged → action_binding_and_uuids carried forward); task_0.view.json 8d3a44eb… and task_1.view.json 002dfd02… unchanged (same worlds and personas).
- Base copy still verbatim (lines 1–1208 equal `blueprint/products/bizpower.yaml`). Policy start lines and file length identical to round 2; the changed text was located by reading every extended policy's rule, compute, prerequisite and factors again. Changes found only in: loyalty→renewal_rate `condition`; grace make-good tier 2 (rule, compute, ladder); relocation remaining-term fall-through (rule, compute, ladder) and tenure-charging tiers (rule, compute, ladder). multi_site, renewal_rate and closure read identically to round 2.
- Entry conditions: round-3 gate snapshot and masked views supplied. Contamination disclosure: rounds 1–2 GT of both tasks are in this auditor's context; round-3 per-task sections re-derive only what the changes can move.

### re-derived sections (revision 3)

- policy_conflict_scan: unchanged conclusions (same policies, subjects, tools, scopes).
- rule_compute_equivalence: mechanical check passes (every basis verbatim, every binding has a basis, every `replaced_by` and `baseline.rule` in its rule). Changed bindings:
  - grace `grace_start_rate` tier 2 now `… F('renewal_election') == 'declined' and DAYS(g_final_date, F('renewal_election_date')) <= K('early_decline_days')`, matching "declined automatic renewal no more than 7 days after the final options notice's date". Equivalent.
  - relocation `months_left` = `MONTHS(NOW, F('contract_end_date'))` (guard for an empty end date removed, matching the removal of "or no contract end date on record" from the rule); `tenure_charged_fee` tier 2 no longer tests `term_months > 0`, matching "an agreement supplied 12 to 35 months is charged the reduced fee prorated …". Within the policy's domain (only agreements whose plan allows site transfers, all of which carry a term and an end date) both are total. Outside it — e.g. a month-to-month agreement with no end date — the compute is undefined (MONTHS on an empty date; division by term_months 0); the rule also gives no fee there because no transfer is recorded. Observation R3-O1 (no rule sentence is left unimplemented, and no in-scope input is affected).
- action_binding_and_uuids: carried forward (tool module unchanged).
- prerequisite_graph: unchanged edges, all state form; loyalty→renewal_rate `condition` is now "renewal election accepted with a renewal election date earlier than its plan change date" — exactly the sentence's state. **R2-O3 closed.**
- prerequisite_sentences: unchanged sentences; round-2 single-write derivations stand.
- override_declarations: overwrite blocks unchanged; round-2 conclusions stand.
- factor_ladders:
  - relocation `transfer_tenure_charging`: tiers "36 or more whole months" (one half) / "12 to 35 whole months" (prorated by months left / term months) / "otherwise (fewer than 12 months)" (as it stands). The scope-restating conjunct "with a term on record" and the fall-through's "or no term on record" are gone; each tier condition is supplied months only, which divides transferable customers. **R2-F2 closed.** Label still honest (tier 2 is a distinct computation).
  - relocation `remaining_term_credit` fall-through is now "otherwise (fewer than 6 months)"; the never-occurring "no contract end date" disjunct is gone. **R2-O4 closed.**
  - grace `late_notice_make_good` tier 2: "both notices inside their windows and the business declined automatic renewal no more than 7 days after the final options notice's date". Under base `bizpower_auto_renewal` a decline is accepted on days 1–15 after the final options notice, so the 7-day bound now genuinely splits declining customers: days 1–7 → tier 2 (adder), days 8–15 → fall-through (the rule's example "a decline made later in the opt-out window" is now possible). The fall-through is reachable through a late-in-window decline as well as through an expiry while a cancellation was pending. **O-9 / R2-O1 closed.** The distinction (a prompt deliberate opt-out later reversed is re-quoted) is a treatment a supplier could publish; no unreal tier.
  - Counts unchanged: multi_site 3/1, renewal_rate 5/1, closure 3/2, loyalty 5/1, grace 4/1, relocation 3/1 (parameter/method); every ladder three disjoint tiers stated in the rule; fall-through = baseline throughout.

### findings (revision 3)

- R2-F2 — **closed**. O-9/R2-O1 — **closed**. R2-O3 — **closed**. R2-O4 — **closed**.
- Unchanged, as stated by the reworker: R2-O2 (remaining-term credit and proration pull opposite ways on months left), O-0, O-2, O-4, O-6 — observations.
- New: R3-O1 (observation) — relocation compute is undefined outside the policy's domain (empty contract end date / term 0) now that the guards are removed; no in-scope consequence. Checked against task 1's proof fields after the reveal.
- No new RED found in the charter.

### closing_checklist (revision 3)

Written after both revision-3 sections were frozen and compared (reveal 2026-10-04 18:06 UTC).

- Files: `0.md`, `1.md`, `_difficulty.md` each carry rounds 1–2 untouched plus `revision_3`; one-to-one with the tasks.
- Every comparison carries a PASS: task 0 — PASS on all four relationships; task 1 — PASS on all four relationships.
- Coverage/scope: six extended policies fully covered by two disjoint scopes ({loyalty, renewal_rate, multi_site, closure}; {relocation, grace}); task tools and GT closed; uuid8s independently generated and unchanged.
- Trees: task 0 — 3 prerequisite problems, 2 value_input edges, one owner=user write; task 1 — 1 prerequisite problem, 1 value_input edge, one owner=user write; all edges state form, each stated by a prerequisite sentence of the blocked rule; the difficulty graph is a DAG with no cross-task reference.
- Factors: every computation declares a self-sufficient baseline and 4–6 factors with ≥ 2 honest `parameter` and ≥ 1 honest `method`; each task has a multi-source factor (renewal_offer_selection; late_notice_make_good) and cross-difficulty factors on seeded rows (bizgas, cni; bizgas); every ladder three disjoint tiers stated in full in its rule, conditions dividing the customers who reach the write; every factor bears weight against an honest baseline, and every fall-back number differs from gold.
- Round-2 items: R2-F2 closed; O-9/R2-O1 closed; R2-O3 closed; R2-O4 closed. Open observations (no rework required): O-0 (traceability deferred), O-2 (Python round vs half-up; no tie in either world), O-4 (state_gate names a field), O-6 (base cancel-and-enroll path, excluded by persona), R2-O2 (opposing remaining-term effects), R3-O1 (relocation compute undefined outside the policy's domain), R3-O2 (task 1 skip-effect wording). No regression.
- Gate re-run on the final form: the orchestrator's round-3 snapshot is cited (all green; traceability deferred until the KB is published); the auditor does not run gates.

Difficulty verdict (revision 3): **PASS** — policy self-consistency, problem tree, factors and unique solution hold on both tasks; the difficulty passes the source-layer audit, with the traceability gate still pending the published KB.
