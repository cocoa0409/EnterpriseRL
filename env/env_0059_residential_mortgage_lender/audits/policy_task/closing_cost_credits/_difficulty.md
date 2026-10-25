# Policy-task audit — closing_cost_credits / charter-global

## charter_global_frozen
- freeze time: 2026-10-13T05:54:06Z (file mtime; the clock was read at 05:52:47Z just before writing) (written before any task's GT was revealed; nothing in this section is derived from a revealed GT)
- auditor: erl-task-policy-audit agent (independent of the instantiator; no instantiator worklog or /tmp/*_0059 scratch read)
- frozen inputs (sha256, matched against the brief):
  - `tasks/closing_cost_credits/credit.extended.yaml` 71ce252ce8913178be1396e72ace66866a6eff5dea00003616cf5bbe33ac73ee
  - `tasks/closing_cost_credits/task_tools.py` b8570f8a2b840ce7ccb69466d03031e7a4d89ac7e230bfb03f5cb180f46a7ac3
  - `.audit_views/policy_task/closing_cost_credits/0.view.json` 2eb3e5a8f108d66643057acb5ff262018843bb79d334b2c4b4d1e4c5b2c3111c
  - `.audit_views/policy_task/closing_cost_credits/1.view.json` ecff7b1778b54137c3f0d9db7eacba993841b1251209dee983f2242c579832a6
- permitted: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml), the extended charter, task_tools.py, the two masked views (frozen_time, user_scenario, initial_state), `erlbench/` and the DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (only `build_env`/`eval_compute`/`substitute` imported; its `main`, which reads task JSON, was never run).
- masked until every task's derivation was on disk: evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*, all worklogs.
- entry conditions: the gate snapshot came with the brief (check_extended, check_task_tools, replay_tasks --check, check_solvability, check_compute, check_grounding, check_cross_fire all OK; check_traceability NOT OK only for the unlock_*_discoverable_tool names awaiting rendered docs — out of scope, accepted as stated). Masked views and hashes supplied and verified. Input complete.
- base copy: `head -1003 credit.extended.yaml` vs `blueprint/products/credit.yaml` differs only by one trailing blank line → base section verbatim.

### policy_conflict_scan
Six extended policies, two disjoint chains (the trees are inferred from the `prerequisite` graph; the claimed scopes are masked and are compared after reveal):

| id | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- |
| P1 credit_ext_neighborhood_grant_award | certify_grant_occupancy_149507f1 (user) | award_amount | [] |
| P2 credit_ext_grant_closing_cost_entry | post_closing_cost_credit_e81a44da (agent) | entry_amount | P1 (value_input, state) |
| P3 credit_ext_grant_down_payment_entry | post_down_payment_credit_64b83335 (agent) | entry_amount | P2 (value_input, state) |
| P4 credit_ext_heroes_validity_extension | extend_credit_validity_45c9966f (agent) | extension_days | [] |
| P5 credit_ext_heroes_recertified_award | recertify_hero_occupation_0487fd94 (user) | award_increase (+ copied basis_loan_amount) | P4 (value_input, state) |
| P6 credit_ext_heroes_unpaid_cost_reduction | reduce_unusable_credit_facd0be5 (agent) | entry_amount | P5 (value_input, state) |

- Subjects: P1 {credit_verified, credit_award_booked}; P2/P3 {credit_applied_at_closing}; P4 {credit_expiration_extended}; P5 {credit_award_booked}; P6 {credit_reduced}. P2 and P3 share an event type but split it by cost_category (nonrecurring_closing_costs vs down_payment) and by tool; P1 and P5 share credit_award_booked but split by program (Neighborhood Access Grant vs Hometown Heroes). No two policies produce the same row kind on the same program.
- Triggers / time anchors: P1, P4, P5 on_request; P2, P3 state_due "At consummation"; P6 state_due "Before closing". P2/P3's anchor (consummation) is a real-world event — see finding F-3 and task 0.
- Eligibility inheritance: base `credit_program_eligibility`, `credit_validity` (on-time request, max_extensions, extension_allowed_file_statuses), `credit_application_at_closing` (verified_before_application) all stay in force; no extended text weakens them.
- Cross-category read boundaries: every cross read is declared in `cross_category` and `inputs`; P2/P6 read lock/funding/appraisal/buydown/preapproval only through CFIELD/CPARAM/XSUM keyed to the customer (and, for holdings, the loan file).
- Scope: P1–P3 form one chain (grant: award → closing-cost entry → down-payment entry), P4–P6 the other (Heroes: extension → re-certified award → reduction). Two tasks, two disjoint chains covering all six policies — consistent with exclusive and complete scopes if task 0 claims P1–P3 and task 1 claims P4–P6 (verified after reveal).

### rule_compute_equivalence
Swept every binding of every policy against its `compute_basis` quotation and back against the rule. All quantities, windows (`XLATEST … disclosure_form=closing_disclosure` / `loan_estimate`), tiers, acting bases, caps/floors and rounding conventions have a verbatim basis and an implementing expression, every ladder tier named in `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and no compute branch lacks a rule tier — with these exceptions/notes:
1. **P3 `dp_room`, top tier — the rule prose admits two parses (finding F-2).** Rule: "above 95 percent, the room is 85 percent of the down payment less the part of the reserve kept in it, rounded down to the whole dollar". Compute: `int(room_before_ltv * 0.85)` = 85% × (down payment − reserve kept in it). The ladder entry adds parentheses ("85 percent of (down payment less the reserve kept in it)") that the rule text, which is the only face rendered to a solver, does not carry. Reading "(85 percent of the down payment) less the reserve kept in it" is grammatical and yields a different number.
2. P6 `costs_left` floor placement: rule floors only "the payable closing costs plus the prepaid items … less the seller and agent concessions … never below zero", then adds/takes out the buydown, paid-charge and held-money tiers with no further floor; compute applies one `MX(0, …)` after all adjustments. Divergent only when the pre-adjustment sum is negative and an add-back follows; not the case in task 1 (1,965.00 before adjustments). Observation O-4.
3. P2 `cc_unpaid`: the rule floors the unpaid amount then "takes out" carve-outs; compute floors once at the end; because every later term is a subtraction and `result` is `MX(0, MN(…))`, the two are equivalent. Pass.
4. P4 `compute_basis.result` quotes the baseline sentence ("The standard extension … adds the program's extension_days") while `result = int(extension_granted)` implements the block-rounding ladder; the ladder sentence is quoted under `extension_granted`. Cosmetic. Observation O-5.
5. P2 rule scopes the lock and convenience carve-outs to "the rate lock of the file" / "the closing"; compute `XSUM` over `lock_pricing_events` / `funding_fee_ledger` is scoped to the customer, not to the file's lock/closing. Equivalent whenever the customer holds one lock and one closing (both task worlds). Observation O-6.
6. P1 `transformed_grant` top tier uses `(0-((0-x*1.15)//10))*10` (ceil to ten); float-exact for the values in these worlds. Pass.

### action_binding_and_uuids
- Six `(target_tool, computes)` pairs, each claimed by exactly one policy; every task tool is the target of exactly one policy.
- Docstrings: grep for before/after/first/then/prior to/until in `task_tools.py` returns nothing; no docstring names another tool or a sequence position. Each states one business effect. `certify_grant_occupancy` mentions "Neighborhood Access Grant or Neighborhood Access Grant Plus" while P1's rule speaks only of the Neighborhood Access Grant — no task world carries a Plus (observation O-7).
- Function bodies validate nothing: no status, expiration, basis or ledger check; every tool writes unconditionally (`certify` sets verified + award entry; `post_*` book an entry and lower `credit_balance`; `recertify` sets verified_date/basis and books an award entry; `extend` adds days and +1 count; `reduce` books a `credit_reduced` entry). The tool layer judges no prerequisite.
- uuid8s: 149507f1, 64b83335, e81a44da, 0487fd94, 45c9966f, facd0be5 — pairwise distinct, no shared prefix/suffix, no sequence pattern. Pass.

### prerequisite_graph
Mechanically checked (scratch script, deleted): every policy has `prerequisite` (`[]` on P1, P4); each `problem` is an extended policy id of this file, never base, never self; graph P1→P2→P3, P4→P5→P6 is acyclic; each `policy_source` is verbatim in its own `rule` (whitespace-normalised); all four edges `form: state`, none carries `fallback_reason`; each `resolved_by` equals the depended-on policy's `target_tool`; each `gate` is a compute binding of the blocked policy (`credit_balance_left`, `borrower_cost_share`, `extension_charge`, `heroes_balance`) and `kind: value_input` matches.
- `condition` strength matches the sentence on all four edges.
- **E3 (P5←P4) `effect` carries world-specific values** — "the days extended beyond award_validity_days rise above 45 and the extension charge in the re-fixed award moves from 0.00 to 50.00". As general charter text this is false: under any lock other than the 90/120/180-day products P4 grants the program's extension_days (30 for Heroes), so days_extended = 30 and P5's ladder gives 25.00, not 50.00. Finding F-5.

### prerequisite_sentences
| edge | sentence (own rule) | 4-point test | the one write bringing the state about |
| --- | --- | --- | --- |
| E1 P2←P1 | "A neighborhood grant's closing-cost entry is booked only after the grant stands verified with an award entry on its ledger." | "only after"; state (status verified + award entry on ledger, both visible via find_closing_credits / find_credit_ledger); no tool/id/snake_case; strength = condition | certify_grant_occupancy (only write that moves a grant to verified and books its award entry; recertify books award entries only on a verified Heroes credit) |
| E2 P3←P2 | "The down payment entry of a neighborhood grant is not fixed until its ledger carries the closing-cost entry for the Closing Disclosure the loan closes on." | "not … until"; state (ledger entry, cost category nonrecurring, naming the CD); clean; = condition | post_closing_cost_credit (only write booking a nonrecurring_closing_costs application entry) |
| E3 P5←P4 | "The re-certified Hometown Heroes award is fixed only once the credit's expiration date reaches the closing date scheduled for the loan." | "only once"; state (closing_credits.expiration_date ≥ closings.scheduled_closing_date); clean; = condition ("on or after") | extend_credit_validity (only write moving expiration_date) |
| E4 P6←P5 | "A Hometown Heroes credit's reduction against the Loan Estimate is not fixed until the credit's basis stands at the base loan amount now on the loan file." | "not … until"; state (basis_loan_amount = loan_files.base_loan_amount); clean; = condition | recertify_hero_occupation (only write setting basis_loan_amount) |

Derivations (sentence + records + depended-on rule → action): E1 → P1 rule "A Neighborhood Access Grant is verified when the borrower signs the twelve-month owner-occupancy certification, and the grant award is fixed on that certification and booked once as an award entry" → certification handed to the borrower. E2 → P2 rule "For a Neighborhood Access Grant the closing-cost entry is booked at consummation, one application entry naming the Closing Disclosure …" → closing-cost entry. E3 → P4 rule "A Hometown Heroes credit's validity is extended on request …" (the only rule that moves an expiration date) → extension. E4 → P5 rule "The re-fixed award is computed on the base loan amount then on the loan file, which becomes the credit's basis" → re-certification. Each has one reading.
- Second wordings / extra order statements (observations, no differing conclusion): P3's first sentence "pays the down payment with what its closing-cost entry leaves" restates E2's order in action words (O-8); P5's "a Hometown Heroes credit whose loan program changed after verification stands only once the borrower re-certifies" sits in the depended-on rule of E4 (O-8); base `credit_application_at_closing` "A credit is applied at closing only while the credit status is verified" states an order overlapping E1, but P2 carries its own sentence, so it grounds nothing (O-8).
- E3 wording "the closing date scheduled for the loan": the schema describes `loan_files.estimated_closing_date` as "closing date currently scheduled on the file" (2027-01-08 in task 1) while `closings.scheduled_closing_date` is "date the signing is scheduled" (2027-01-22). The two readings name different states, but P4's own extension (computed from the closing record) reaches both, so no resolving action or value moves. Observation O-9.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry:
- **P1** (credit_program_eligibility, credit_award_amount): "A fixed credit awards fixed_credit_amount." → declared, replaced for the Neighborhood Access Grant. "At verification the award amount is fixed" / "The verified award is booked once as an award entry" → followed. Eligibility tests, deadlines → inherited. "Eligibility is verified from verification_documents within verification_deadline_days" vs P1's "verified when the borrower signs the twelve-month owner-occupancy certification": P1 adds the act that verifies; it moves no number (observation O-10).
- **P2** (credit_agg_stacking, credit_application_at_closing): the application sentence ("At consummation each verified credit … against nonrecurring_closing_costs, prepaid_items_total and discount_points_amount …") → declared. Stacking "concessions first, then credits in ascending application_order, each filling its applicable_cost_categories in the listed order up to the cost still unpaid in that category" → the "listed order … up to the cost still unpaid" clause is declared superseded in **P3's** overwrite (replaced_by scoped to the down payment entry); P2's narrowing of the nonrecurring cost (payable scope, carve-outs) is therefore not named in P2's own list. Merged semantics remain unique because the superseded clause leaves nothing in base to fight P2's explicit rule, and P2 ≤ the base caps ("never pays a cost another source has already paid", total-cost ceiling). Observation O-11.
- **P3**: the listed-order clause declared (above). NAG Plus lists down_payment first; P3's "neighborhood grant" text and supersession would also reverse a Plus's listed order — no task carries a Plus. Observation O-7.
- **P4** (credit_validity): "An extension adds extension_days … and raises extension_count by one" → declared; replaced_by is scoped "a credit backed by a rate lock of 90 days or more" while the rule is scoped to Hometown Heroes — for a non-Heroes credit on a 90+-day lock the replaced_by supersedes the base sentence with no rule saying how to size it (observation O-12; no task world affected). On-time request, max_extensions, status list, expiry counting → inherited.
- **P5** (credit_program_eligibility, credit_award_amount): "a credit that still passes keeps its award amount except that percentage credits are re-sized" → declared. "If the base loan amount changes before closing the award is re-sized the same way" → declared. **"A fixed credit awards fixed_credit_amount." — not declared by P5 (P1's declaration is replaced only for the Neighborhood Access Grant).** Base variant *Larkspur Hometown Heroes Credit*: `credit_amount_type: fixed`, `fixed_credit_amount: 1000.0`, `min_credit_amount: 1000.0`, `credit_cap: 1000.0`. P5's rule and baseline: "The standard Heroes award is 0.15 percent of the base loan amount, rounded to the cent, never below 500.00 and never above the program's credit_cap." Two passages, same situation (the standard award of a Heroes credit), different conclusions (1,000.00 vs 0.15 % of base loan floored at 500.00). Finding F-1. The re-fixed award itself is explicitly governed by P5's declared replacement ("The re-fixed Heroes award is the transformed amount …"); what is undeclared is the "standard" the baseline and the fall-through starting rate rest on.
- **P6** (credit_agg_stacking, credit_application_at_closing): "What remains after every eligible cost is paid is booked as credit_reduced with exceeds_eligible_costs." → declared. Concessions-first sentence: P6's buydown add-back says part of the recorded concessions does not pay closing costs; base also treats a buydown subsidy as a cost category credits/concessions may pay, so the add-back is consistent with a base reading. Observation O-11.

### factor_ladders
Counts as declared (parameter / method): P1 5/1; P2 3/1; P3 3/1; P4 3/2; P5 5/1; P6 3/1 — all within 4–6, ≥2 parameter, ≥1 method. Every `decides` is an input (none is `result`); binding sets disjoint; every tier is stated in its rule and branched in compute; every ladder has three stated tiers.

Real-ladder test (no two tiers selecting the same value or method, every condition one the business weighs):
- **Collapsed ladders — the fall-through equals the tier above it whenever it applies (finding F-4):**
  - P2 `cc_lock_pricing_carveout`: `extension_costs if extension_costs > 0 else (relock_fees if relock_fees > 0 else 0)`. Under the fall-through's condition (no borrower-borne relock fee) tier 2's value "the relock fee" is 0 — tiers 2 and 3 are one tier ("take out the relock fee"). Effective ladder: two tiers. Tier 2's compound part "no borrower-borne extension cost" is also a condition no lender weighs when deciding whether a relock fee the borrower chose to pay is grant-payable (the rule's own reason, "Rate lock pricing the borrower chose to pay is not payable by a grant", covers both fees).
  - P2 `cc_convenience_carveout`: same shape (after-hours fee else courier fee else 0); tiers 2/3 collapse; "no after-hours signing fee" is a condition no lender weighs for whether a courier fee is a convenience.
  - P2 `cc_prepaid_charge_carveout`: `appraisal_paid + upfront_paid if (FHA/VA and upfront_paid > 0) else (appraisal_paid if appraisal_paid > 0 else 0)`; under the fall-through (no appraisal charges) tier 2's value "the appraisal charges" is 0 — tiers 2/3 collapse. Effective ladder: two tiers.
  - P6 `heroes_already_paid_charges`: tier 1 (appraisal and up-front both collected → both) and tier 2 (appraisal collected, no up-front fee → appraisal) both evaluate to appraisal + up-front (up-front is 0 under tier 2) — tiers 1/2 collapse; and the fall-through gives 0 even when up-front fees were paid without an appraisal charge, contradicting the rule's own reason ("Charges the borrower has already paid toward the Loan Estimate are taken out").
  - P6 `heroes_held_money`: tiers are numerically distinct, but tier 2's part "no such deposit is held" is a condition no lender weighs for whether a rate-hold fee it holds and credits at closing is taken out (the rule's reason, "Money Larkspur already holds and credits at closing", covers both). Judged unreal on that part.
- Surviving factors per computation: P1 6 (all constants distinct); P2 **1** (`cc_payable_scope`); P3 4; P4 5; P5 6; P6 **2–3** (`heroes_le_payable_scope`, `heroes_buydown_addback`, and `heroes_held_money` only if its tier-2 condition is accepted). P2 and P6 fall below the 4-factor floor.
- Label honesty: P1 `nag_housing_burden_transform` (×1.15 ceil-to-ten / ×1.10 floor-to-dollar / as is) and P5 `heroes_occupation_transform` (×1.25 floor-to-ten / ×1.10 floor-to-ten / as is) change multiplier and rounding — method accepted (the P5 one differs only in multiplier between tiers 1 and 2; observation O-13). P3 `dp_ltv_room_method`, P4 `heroes_target_date_choice`/`heroes_block_rounding`, P2/P6 payable-scope factors change the formula — honest. All `parameter` labels select numbers.
- Multi-source: by the gate's field-level test P1 `nag_starting_amount`, P2 `cc_lock_pricing_carveout`/`cc_prepaid_charge_carveout`, P3 `dp_pricing_reserve`/`dp_repair_reserve`, P6 `heroes_buydown_addback`/`heroes_already_paid_charges`/`heroes_held_money` qualify. Over *distinct records*: P3 `dp_repair_reserve` (appraisal_orders.subject_to_completion × loan_files.variant_name) and P6 `heroes_already_paid_charges` (appraisal_orders.fee_balance × loan_files.prepaid_fee_balance). The latter is struck by F-4, leaving P6's surviving multi-source factors (`heroes_buydown_addback`: one buydown row; `heroes_held_money`: lock row × lock product parameter) as field-level only (observation O-14).
- Cross-difficulty: P1 loan; P2 loan/lock/funding/appraisal; P3 loan/appraisal; P4 funding/appraisal/loan/lock; P5 loan/preapproval; P6 loan/buydown/appraisal/lock.
- Business realism of the remaining tiers: P1's credit-score holdback (a grant shrinking for lower scores) and the purchase-price add for dearer homes are unusual but sized and gated as a need-based grant would plausibly be; P3, P4 tiers read as genuine practice. Not red.

### findings
- **F-1 SOURCE-POLICY RED (charter-global; bears on task 1)** — undeclared override of base `credit_award_amount` "A fixed credit awards fixed_credit_amount." for the Hometown Heroes credit (base variant fixed 1,000.00, floor 1,000.00, cap 1,000.00) by P5 "The standard Heroes award is 0.15 percent of the base loan amount, rounded to the cent, never below 500.00 …" and the starting-rate fall-through "a middle-income tract takes the standard 0.15 percent". Root cause: P5's `overwrite` names two other base sentences but not this one; P1's declaration of it is replaced only for the grant. Affected: P5 rule/baseline, factor `heroes_starting_rate` fall-through, P5 `overwrite`. Consequence demonstrated in 1.md.
- **F-2 SOURCE-TASK RED root (charter-global; bears on task 0)** — P3 rule sentence for base-loan-to-value above 95 % admits two parses (rule_compute_equivalence item 1). Affected: P3 rule, `dp_room`. Consequence demonstrated in 0.md.
- **F-3 SOURCE-TASK RED root (charter-global; bears on task 0)** — P2/P3 time the entries "at consummation" (P2: "For a Neighborhood Access Grant the closing-cost entry is booked at consummation"; P3: "At consummation a verified Neighborhood Access Grant pays the down payment …"; base lifecycle "verified → applied … at consummation"), a real-world event, while P6 shows the charter has wording for "Before closing". Consequence (act now vs wait) demonstrated in 0.md.
- **F-4 SOURCE-FACTOR RED (charter-global structure; bears on tasks 0 and 1)** — collapsed/unreal ladders listed above; P2 keeps 1 factor, P6 2–3. Weight on each world in the task files.
- **F-5 SOURCE-POLICY RED (charter-global; moves no scored value)** — E3 `effect` states world-specific values ("rise above 45", "moves from 0.00 to 50.00") that P4+P5 contradict for any credit not on a 90/120/180-day lock (30 extended days → 25.00). Affected: P5 `prerequisite[0].effect`. True on task 1's world, so no task's scored value moves.
- Observations O-4 … O-14 as numbered above.

## closing_checklist
Written after both reveals (2026-10-13T05:55:39Z onward). Nothing above this heading was changed by the reveals except the freeze-time line, which was corrected from an estimate to the file's actual mtime (05:54:06Z).
- Per-task files `0.md`, `1.md` correspond one-to-one with tasks/0.json, tasks/1.json; this is revision 1 (no older revision exists).
- Comparison sections do **not** all carry PASS: task 0 = SOURCE-TASK RED (F-2 parse → 3,193.00 vs 3,048.00; F-3 consummation timing) + SOURCE-FACTOR RED (F-4: P2 keeps 1 real factor); task 1 = SOURCE-POLICY RED (F-1 undeclared override of the Heroes standard award) + SOURCE-FACTOR RED (F-4: P6 keeps 2–3 real factors). All six scored values matched the blind derivation figure for figure (4,620.00 / 1,417.49 / 3,193.00; 135 / 40.00 / 773.80), as did every factor_sensitivity and baseline_result figure.
- Coverage and scope: charter_scope task 0 = P1–P3, task 1 = P4–P6; pairwise disjoint over whole trees, jointly complete over the six extended policies; tools and GT closed; uuid8s independent (action_binding_and_uuids).
- Trees: each has two prerequisite problems, two value_input edges, one owner=user problem (P1 certify / P5 recertify), no cycle; the difficulty-wide prerequisite graph is a DAG (two disjoint chains).
- Factors: each computation declares 4–6 factors with ≥2 parameter / ≥1 method and every declared factor bears weight on its world, but P2 and P6 fall below four once the collapsed/unreal ladders (F-4) are struck; the P5 baseline is not unique (F-1).
- Gates: not re-run by this audit (the brief supplies the snapshot; the auditor does not run gates). The difficulty does **not** pass the source-layer audit.
- Charter-global F-5 (SOURCE-POLICY, E3 `effect` world-specific values) moves no scored value in either task.
- Observation numbering in this file starts at O-4; O-1…O-3 are unused.

## revision_2

### charter_global_frozen (revision 2)
- Written before either round-2 task JSON was opened (freeze = this file's mtime after the append; the reveal time is recorded in the task files). Auditor: erl-task-policy-audit agent, same independence and read isolation as round 1 (no worklog, no /tmp/*_0059 instantiator scratch, no other scenario or sibling difficulty).
- Inputs (sha256, matched against the round-2 brief): extended 2bf27a716699cbc43c239b38f1fe70c7fe4dd542d91860d029905faab1e5b870 (changed); task_tools ed9a1dd7bdfd2fdbc7ff9fe77b81b1ae503b63380b92d5c9f86a042d07f9f42f (changed); 0.view 0a9667fc…5bde5; 1.view ced45252…bdc06. Both shared inputs changed, so every charter-global section is re-derived in full below, not carried forward. The round-1 text above is untouched.
- Base copy: still verbatim (differs from `blueprint/products/credit.yaml` by one trailing blank line only).
- Entry conditions: round-2 gate snapshot supplied (all OK except TRACEABILITY, which misses only the unlock_* tool names before the KB exists — out of scope). Reworker's closure claims were taken as a checklist only, not as evidence.

### policy_conflict_scan (r2)
Same six policies, targets, owners and `computes`; same two chains (P1→P2→P3 grant, P4→P5→P6 Heroes). Subjects unchanged. Timing anchors: P2/P3 are now "On the day of the scheduled closing, while the loan file is clear to close and its Closing Disclosure has been issued, … the application entries being booked that day ahead of the signing" (declared in P2's overwrite of the base application sentence); P6 "Before closing"; P1, P4, P5 on request. Cross reads are now keyed to the file's own lock (`lock_id=CFIELD('lock','lock_id',…)`) and closing (`closing_id=…`). No overlap or conflict between policies. Scopes still split into two disjoint chains covering all six.

### rule_compute_equivalence (r2)
Every binding of the six policies re-swept against its `compute_basis` quote and back:
- P1: tract-only starting amount; holdback 500/250/0; price, household, burden unchanged; new income adjustment (−25.00 per whole point above 80 % AMI / +300.00 at or below 50 % / 0); order stated ("first the credit-score holdback … then the purchase-price, household-income and closing-cost burden adjustments … then the income adjustment …; lowered to credit_cap … rounded to the cent") = compute. Pass.
- P2: unpaid = payable − concessions − (appraisal fee_balance + prepaid_fee_balance) − booked closing-cost entries − lock exclusion − closing-service exclusion, floored once, × tract share, rounded; entry = min(balance, share). The rule says the two exclusions are "subtracted together with the other deductions, before the floor at zero" and the share applies to "the unpaid closing costs so found" — matches compute. One extra term: `lock_pricing_costs` subtracts every `lock_cost_waived` amount on the lock, while the rule names only "the borrower-borne extension and relock costs booked on that lock". Equivalent wherever "borne" means "net of waivers" and the waiver is of an extension or relock; it diverges only for a waived float-down fee. Observation R2-O1 — no waiver rows in either world.
- P3: the room order is now explicit: "first the part of the reserve kept in the down payment is taken from the down payment, never below zero; then that amount is multiplied by the share … 75 percent above 95 percent, 90 percent above 90 and at most 95 percent, and the whole amount at 90 percent or below; the product is rounded down to the whole dollar" = `int(room_before_share * ltv_share + 1e-6)`. **F-2 closed** — there is now one parse. The program-specific reserve offset (FHA/VA: closing costs still paid; HomeReady: charges paid before closing; others: none) = compute. Pass.
- P4: unchanged apart from the Heroes-scoped replaced_by and `compute_basis.result` now quoting the block-rounding sentence. **O-5 closed.**
- P5: order explicit (start → purpose, pre-approval, program, occupation → minus extension charge → floor 500.00 / cap credit_cap) = compute; extension charge linear (25.00 + 0.50 per day beyond 45) / flat 25.00 / 0 = compute. Pass. The rule also says "where the re-fixed award is below the available balance, the difference is taken off as a reduction entry instead". No tool in this difficulty books that entry (`recertify` books award entries only, and `reduce_unusable_credit` books only `exceeds_eligible_costs`). This is not triggered in task 1 (883.34 > 870.40) — observation R2-O2.
- P6: the standard now deducts already-paid charges (appraisal + up-front, always) and held money (credited lock deposit + credited rate-hold fee, summed). The refinement adds the buydown add-back and the re-disclosure cushion "before the floor at zero", then subtracts the excess tolerance after it — matches compute, so **O-4 closed**. Pass.

### action_binding_and_uuids (r2)
- Six `(target_tool, computes)` pairs, one policy each. uuid8s unchanged and distinct (149507f1, 64b83335, e81a44da, 0487fd94, 45c9966f, facd0be5).
- task_tools.py: the only docstring change is that `certify_grant_occupancy` now names the Neighborhood Access Grant only (**O-7 closed** on the tool side; P2/P3 now say "Neighborhood Access Grant" too). No ordering words, no cross-tool names. Function bodies still check nothing.

### prerequisite_graph (r2)
Mechanically re-checked: four edges (P2←P1, P3←P2, P5←P4, P6←P5), each `policy_source` verbatim in its own rule, `form: state`, no fallback_reason, `resolved_by` = the depended-on target_tool, `gate` a compute binding, `kind: value_input`, graph acyclic. E3 `effect` now reads "the days extended beyond award_validity_days, counted from the reserved date to the new expiration date, set the extension charge subtracted in the re-fixed award" — general, no world values. **F-5 closed.**

### prerequisite_sentences (r2)
- E1 "A Neighborhood Access Grant's closing-cost entry is booked only after the grant stands verified with an award entry on its ledger." — passes the 4-point test; only `certify` brings the state about.
- E2 "The down payment entry of a Neighborhood Access Grant is not fixed until its ledger carries the closing-cost entry for the Closing Disclosure the loan closes on." — passes; only `post_closing_cost_credit`.
- E3 "The re-certified Hometown Heroes award is fixed only once the credit's expiration date reaches the signing date scheduled with the settlement agent for the loan." — passes; now names the closing record's date unambiguously (**O-9 closed**); only `extend_credit_validity`.
- E4 unchanged — passes; only `recertify`.
- Second wordings: P3's "pays the down payment with what its closing-cost entry leaves" is gone; P5's "stands only once the borrower re-certifies" is now "the borrower's re-certification … re-fixes its award" (no order statement). The base `credit_application_at_closing` "only while the credit status is verified" still overlaps E1, but it is base text and grounds nothing. **O-8 closed** as far as extended text can close it.

### override_declarations (r2)
- P1: "A fixed credit awards fixed_credit_amount." declared, replaced for the grant by the order sentence. P1's rule now opens "With its verification documents on file, a Neighborhood Access Grant is verified when the borrower signs …". This turns base's "Eligibility is verified from verification_documents" into an explicit precondition, but no table records documents; the only record-side evidence is `closing_credits.eligibility_basis` and the loan file's tract/income fields. Observation R2-O3 (O-10 transformed rather than closed); moves no number.
- P2: declares the base application sentence and, now, the stacking "listed order … up to the cost still unpaid" clause (replaced for the closing-cost entry). **O-11 closed.**
- P3: declares the stacking clause (down payment entry). Two program-scoped replacements of one base clause are compatible.
- P4: replaced_by now "For a Hometown Heroes credit backed by a rate lock of 90 days or more …" — matches the rule's scope. **O-12 closed.**
- **P5: now declares "A fixed credit awards fixed_credit_amount." → "The standard Hometown Heroes award is 0.15 percent of the base loan amount, rounded to the cent, never below 500.00 and never above the program's credit_cap."**, plus the re-size sentence ("While the loan program on the file is unchanged, each change of the base loan amount re-sizes …") and the eligibility clause. The base sentence that fought P5's standard is now declared, and the merged semantics are unique for the Heroes award. **F-1 closed.** Residue: the base sentence is now superseded twice, each time scoped to one program (grant, Heroes), so the First Home Credit (fixed 2,500.00) is left with no restated award sentence in the extended text. No task carries one — observation R2-O4.
- P6: declares "What remains after every eligible cost is paid …"; the buydown add-back is still consistent with base treating a buydown subsidy as a cost concessions may pay.

### factor_ladders (r2)
| policy | factors (label) | count p/m |
| --- | --- | --- |
| P1 | nag_tract_start (p), nag_score_holdback (p), nag_price_adjustment (p), nag_household_adjustment (p), nag_cost_burden_adjustment (p), nag_income_shaping (m) | 5/1 |
| P2 | cc_payable_scope (m), cc_short_lock_exclusion (p), cc_signing_convenience_exclusion (p), cc_tract_cost_share (p) | 3/1 |
| P3 | dp_own_funds_floor (p), dp_repair_reserve (p), dp_reserve_offset_rule (m), dp_ltv_share (p) | 3/1 |
| P4 | target_date (m), signing_cushion (p), appraisal_buffer (p), conditions_buffer (p), block_rounding (m) | 3/2 |
| P5 | starting_rate, purpose, preapproval, program, occupation_supplement (p); extension_charge (m) | 5/1 |
| P6 | heroes_le_payable_scope (m), heroes_buydown_addback (p), heroes_redisclosure_cushion (p), heroes_excess_tolerance (p) | 3/1 |
- Real-ladder test, re-run on every factor: no ladder has the `A if A>0 else (B if B>0 else 0)` collapse any more. The P2 lock and closing-service exclusions select whole / half / none of a sum, and these differ whenever the sum is positive. The P2 tract share selects 90 % / 80 % / 100 %. P6 `heroes_buydown_addback` keeps a real fall-through (borrower- or Larkspur-funded buydowns add nothing even when subsidy > 0); cushion 5 % / 2.5 % / 0; tolerance 100 / 50 / 0. The former `already_paid` and `held_money` are now unconditional terms of the standard, so there are no unweighed "no such X" conditions. Every condition is one a lender would weigh (lock term chosen, signing method chosen, tract, days to signing and clear-to-close status, changed-circumstance type). **F-4 closed** — P2 and P6 each keep 4 real factors.
- Label honesty: `nag_income_shaping` (linear phase-down / flat supplement / none), `heroes_extension_charge` (linear / flat / none), `dp_reserve_offset_rule` (different offset quantity by program), payable scopes, target date, block rounding — each tier changes the form of the computation: method, accepted. `dp_ltv_share` (75/90/100 %) and the occupation supplement (125/75/0) are now `parameter` — honest. **O-13 closed.**
- Multi-source over distinct records: P3 `dp_repair_reserve` (appraisal × loan file); P6 `heroes_redisclosure_cushion` (closing date × loan-file status); P5 `heroes_occupation_supplement` tier 1 (credit occupation × loan program). **O-14 closed.**
- Cross-difficulty: P1 loan; P2 loan/lock/funding; P3 loan/appraisal; P4 funding/appraisal/loan/lock; P5 loan/preapproval; P6 loan/buydown/funding.
- "Closing-service fees" (P2) is not defined further; compute takes every fee charged on the closing net of reversals (method, after-hours, courier, wire, POA review, redraw). The stated reason ("a travelling or remote signing is a convenience the borrower chose") fits the method/after-hours/courier fees better than a wire or redraw fee. Both task-0 fees (method 175.00, after-hours 75.00) fit either reading — observation R2-O5.

### findings (r2, charter-global)
- Round-1 REDs: F-1 closed, F-2 closed, F-3 closed (verified per task in 0.md), F-4 closed, F-5 closed.
- Round-1 observations: O-4, O-5, O-6 (cross reads now keyed to the file's own lock and closing), O-7, O-9, O-11, O-12, O-13, O-14 closed; O-8 closed in extended text; O-10 transformed into R2-O3.
- New: no RED. Observations R2-O1 (waiver subtraction scope), R2-O2 (reduction-on-re-certification has no tool), R2-O3 (documents-on-file precondition with no record), R2-O4 (First Home Credit left without a restated award sentence), R2-O5 ("closing-service fees" undefined). None moves a scored value in either world.

### closing_checklist (revision_2)
Written after both round-2 reveals (09:27:16Z).
- Files: `0.md`, `1.md`, `_difficulty.md` — revision_1 text untouched; revision_2 appended to each.
- Per-task verdicts r2: task 0 PASS; task 1 PASS. All six scored values and every factor_sensitivity / baseline_result figure matched the blind derivation (task 0: 4,700.00 / 1,118.24 / 3,342.00; task 1: 135 / 12.94 / 411.14).
- Round-1 REDs F-1…F-5 (T0-1, T0-2, T0-3, T1-1, T1-2) are each closed, with the closure verified against the charter text and the task's own world, not against the reworker's list.
- Scopes: P1–P3 / P4–P6, pairwise disjoint, jointly complete; tools and GT closed; uuid8s unchanged and independent.
- Trees: two prerequisite problems each, two value_input edges each, one owner=user problem each, no cycle; the difficulty-wide graph is a DAG.
- Factors: every computation has 4–6 real factors (≥2 parameter, ≥1 method) that bear weight against an honest, definite baseline different from gold; each task has a multi-source factor over distinct records and cross-difficulty factors on seeded rows.
- Remaining observations (none moves a scored value): R2-O1…R2-O5, T0-O1, T0-O4, T1-O1.
- Gates: not re-run by this audit (round-2 snapshot supplied in the brief; TRACEABILITY's pre-KB unlock misses are out of scope).
- **The difficulty passes the source-layer policy-task audit at revision 2.**

## revision_3

### entry (r3)
- Gate snapshot (auditor-run `/tmp/erl0059_coord/gates.sh closing_cost_credits --trace`, from the repo root): EXTENDED OK; TASK TOOL CONTRACT OK; replay --check 0.json 20 acts, closure 18=18, 1.json 21 acts, closure 22=22, REPLAY OK; SOLVABILITY OK; COMPUTE OK (history_rows_max=11, branches_max=80); GROUNDING OK; SCOPE OK; **TRACEABILITY OK** (0.json 26 copied / 0 missing, 1.json 24 / 0). No red gate, so no RED-INPUT stub.
- Views rebuilt with `mkviews.py closing_cost_credits`: 0.view sha256 0a9667fc1c461104a0c885c05c2389a0ad343f16b882fef3b427a9df9ad5bde5, 1.view ced45252ef3979d6cd6763481cf5fb02afd9efa96b3d789faecfc9c95e1bdc06 (both identical to round 2 — no seed or persona change). task_tools.py ed9a1dd7bdfd2fdbc7ff9fe77b81b1ae503b63380b92d5c9f86a042d07f9f42f (unchanged). credit.extended.yaml **29f675d92ad06cae84560ec703ed339ab4f8d0525878bf11471ab9c792f1325f** (changed).
- The extended file was re-serialised: the base section differs from `blueprint/products/credit.yaml` in YAML flow style only, and loads to an identical structure key for key (checked with yaml.safe_load), so the base copy is semantically verbatim. Observation R3-O1: byte-level verbatimness is lost; any tool that diffs the text will show formatting noise.
- Input read as instructed: `audits/render_source/closing_cost_credits/render_credit_r1.md` (renderer source mismatches 1–4 and two minor notes). The instantiator worklog was not read.
- Shared inputs changed (extended), so every charter-global check below is re-derived; round-1/2 text untouched.

### render-report items vs source (r3)
1. **Scoped replaced_by completeness and scope.**
   - "A fixed credit awards fixed_credit_amount." P1: "For a Neighborhood Access Grant, and only for such a credit, the award is the result of the order stated below …; every other fixed credit except the Hometown Heroes Credit, whose award follows the Hometown Heroes award rule, still awards its fixed_credit_amount." P5: "For a Hometown Heroes Credit, and only for such a credit, …; every other fixed credit except the Neighborhood Access Grant, whose award is sized on the borrower's occupancy certification, still awards its fixed_credit_amount." Each keeps the base rule for First Home and Neighborhood Access Grant Plus (fixed) and names the sibling's carve-out instead of reinstating fixed_credit_amount for it. Closed, no mutual reinstatement.
   - "each filling its applicable_cost_categories in the listed order …" P2 and P3 now describe the same carve-out (the grant's nonrecurring closing costs and down payment only) and keep the listed-order rule "for every other credit, and every other cost category". Neither reinstates the other's category. Closed.
   - "An extension adds extension_days … and raises extension_count by one": P4 keeps both halves for every other credit and keeps the count increment for the sized Heroes extension. Closed.
   - "If the base loan amount changes before closing the award is re-sized the same way": no longer retired (P5's overwrite list dropped it), so the base sentence stands for every credit, including the two percentage credits. Closed. See R3-F1 for the interaction it leaves.
   - "a credit that still passes keeps its award amount except that percentage credits are re-sized under the award policy.": P5 keeps it for every other credit. Closed.
   - "What remains after every eligible cost is paid is booked as credit_reduced with exceeds_eligible_costs.": P6's overwrite is now `[]`, and its rule says "This reduction comes in addition to the base rule: what remains on any credit after every eligible cost is paid at closing is still booked as credit_reduced with exceeds_eligible_costs." Base does not confine reductions to closing (the event meaning of credit_reduced is "taken off the balance before or at closing"), so the pre-closing reduction is an addition, not a departure. Closed.
2. **Waivers in `lock_pricing_costs`.** The rule now reads "the whole of the borrower-borne extension and relock costs booked on that lock, less any of those costs Larkspur later waived". The compute subtracts every `lock_cost_waived` amount on the lock. The lock charter's waiver ("a booked lock cost is waived because Larkspur bears it", one row per waived pricing entry) could in principle waive a float-down fee, which compute would also subtract. Narrow residue, no waiver rows in either world — observation R3-O2 (successor to R2-O1).
3. **P2 rounding.** The rule now says "half of that amount, rounded to the cent" / "half of those fees, rounded to the cent"; `cc_unpaid` is now `RND(MX(0,…),2)` = "never below zero, rounded to the cent". Rule and compute place every rounding identically. Closed.
4. **P6 cushion rounding.** The rule now says "adds 5 percent of the payable closing costs, rounded to the cent; … 2.5 percent of them, rounded to the cent" = `RND(payable_le_costs*cushion_pct/100,2)`. Closed.
- Minor (P5 reduction branch): the rule now says "where the re-fixed award is not above the available balance, the re-certification books no entry and the balance stands" — matches `MX(0,…)` and the tool. But see R3-F1.
- Minor (P4): the rule now says "any other appraisal order, whether completed or delivered as is, under reconsideration or cancelled, adds none" and "a count that is already a whole number of blocks stands as it is" — both match compute. Closed.

### six-kind sweep over the whole charter (r3)
- Rule/compute rounding and floors: P1 (one RND at the end, after the cap), P2 (above), P3 (explicit order; ⌊⌋ to the dollar; floors where stated), P4 (block ceil, exact multiple stands), P5 (RND of the sum before floor/cap; start amount RND), P6 (single floor after add-backs; cushion RND; final RND) — all equal.
- compute_basis quotes: mechanically checked — every quote is verbatim in its own rule, and the compute_basis keys equal the compute bindings for all six policies.
- replaced_by completeness and scope: every replaced_by is verbatim in its own rule and is scoped "and only for such a credit … every other … still …". The two sibling pairs (fixed-credit sentence P1/P5; listed-order clause P2/P3) name each other's carve-out consistently.
- Overwrites retiring nothing or non-conflicting clauses: each `superseded_clause` is verbatim in its base policy's rule; none retires a clause it does not depart from; P6 retires nothing.
- Undeclared base departures: one found — R3-F1 below.
- Docstrings vs bodies: unchanged since r2; each effect stated equals its body; no example values (no numeric figures in any docstring); no ordering words.

### findings (r3, charter-global)
- **R3-F1 SOURCE-POLICY RED (charter-global; moves no scored value in either task) — undeclared departure from base `credit_award_amount` re-size sentence.**
  - Root cause: P5 dropped its declaration of base "If the base loan amount changes before closing the award is re-sized the same way, and a decrease is booked as a credit_reduced entry for the difference with reduction_reason loan_amount_decreased, and an increase as a further award entry for the difference" (that sentence now stands for every credit, Heroes included). P5 at the same time states "where the re-fixed award is not above the available balance, the re-certification books no entry and the balance stands".
  - Demonstration: take a Hometown Heroes credit whose loan program changes and whose base loan amount falls before closing, so that the re-fixed award comes out below the available balance. The base sentence (base loan amount changed → re-sized → "a decrease is booked as a credit_reduced entry for the difference") books a reduction. P5 books no entry, and the balance stands. Same situation, two different terminal ledgers.
  - Scope: in task 1 the re-fix is an increase (883.34 > 870.40), so both readings agree there.
  - Affected: credit_ext_heroes_recertified_award `rule` (re-certification entry sentence) and `overwrite` (no entry for the base re-size sentence).
- Observations: R3-O1 (re-serialised base), R3-O2 (waiver scope).
- Observations R2-O3 (documents-on-file) and R2-O5 ("closing-service fees" undefined) persist unchanged.
- R2-O2 is resolved in wording (no tool-less reduction branch), at the cost of R3-F1.
- R2-O4 is closed: fixed credits other than the grant and Heroes keep fixed_credit_amount.
- R3-O3: in task 1's world both the program and the base loan changed. The standing base re-size sentence could be read to re-size the Heroes award at once, before any extension (82.94 rather than 12.94). P5's "a change of the base loan amount alone re-sizes … and a change of the loan program re-fixes it on the borrower's re-certification", together with the gate sentence on the re-certified award, makes P5's path the specific one, and the only tool that books a Heroes award entry is the re-certification. So this is not counted as a second defensible answer, but it is the same interaction as R3-F1 seen from the increase side.

### closing_checklist (revision_3)
- Written after the r3 reveal (12:06:17Z). All six scored values, factor_sensitivity and baseline figures unchanged from r2 and re-confirmed (task 0: 4,700.00 / 1,118.24 / 3,342.00; task 1: 135 / 12.94 / 411.14).
- Render-report items 1a–1f, 2, 3, 4 and both minor notes: closed in the source, except for two residues. Item 2 leaves the observation R3-O2. Closing the P5 minor note created R3-F1.
- Scoped replacements: each keeps the base rule for every other program and category, and the sibling pairs (P1/P5 fixed-credit sentence; P2/P3 listed-order clause) name each other's carve-out without reinstating each other.
- Regression check: every r2 closure still holds (F-1…F-5, O-4…O-14, T0-*, T1-*).
- Trees, scopes, uuids, gates: unchanged and green (gate snapshot above).
- **task0=PASS  task1=SOURCE-POLICY RED**

## revision_4

### entry (r4)
- Gate snapshot (auditor-run `/tmp/erl0059_coord/gates.sh closing_cost_credits --trace`): EXTENDED OK; TASK TOOL CONTRACT OK; replay --check 0.json 20 / closure 18=18, 1.json 21 / closure 22=22, REPLAY OK; SOLVABILITY OK; COMPUTE OK (history_rows_max=11, branches_max=89); GROUNDING OK; SCOPE OK; TRACEABILITY OK (0.json 26/0, 1.json 24/0). No red gate.
- `mkviews.py closing_cost_credits`: 0.view 0a9667fc1c461104a0c885c05c2389a0ad343f16b882fef3b427a9df9ad5bde5, 1.view ced45252ef3979d6cd6763481cf5fb02afd9efa96b3d789faecfc9c95e1bdc06 (unchanged since r2); task_tools.py **c646e479839f106d753149a88723f6af7b55030d3d459d535645481a699dde94** (changed); credit.extended.yaml **fb21ca60ad5d032395145f6c42ac7653e2c74132a47214a66b8450046bc518b0** (changed). Both shared inputs changed → charter-global checks re-derived below.

### round-3 items (r4)
- **R3-F1 closed.** P5 now declares the whole base sentence "If the base loan amount changes before closing the award is re-sized the same way, and a decrease is booked as a credit_reduced entry … and an increase as a further award entry for the difference". Its replacement partitions the cases:
  1. Heroes, base loan changed, program unchanged → re-sized by the Heroes award rule (increase → award entry; decrease → credit_reduced, loan_amount_decreased).
  2. Heroes, program changed, with or without a loan change → re-fixed on re-certification (increase → award entry; not above the balance → no entry, "so a re-certified Heroes credit is never lowered").
  3. Every other credit → "still re-sized the same way …", the base text restated in full.
  - The eligibility replacement ("a change of the base loan amount alone re-sizes … a change of the loan program re-fixes it on the borrower's re-certification") and the re-certification sentence ("books no entry and the balance stands") say the same thing for each case.
  - Every Heroes re-size or re-certification case has exactly one rule, and the base sentence stays in force for every other credit.
  - R3-O3 is dissolved: on task 1's file (program changed and base loan changed) only case 2 applies.
- **R3-O2 closed.** The rule now reads "the whole of the borrower-borne extension, relock and float-down costs booked on that lock, less any of those costs Larkspur later waived". Compute sums the borrower-borne `lock_extension_booked`, `lock_relock_fee_booked` and `lock_float_down_fee_booked` entries, less `lock_cost_waived`. The lock charter's booked costs carrying cost_amount are exactly those three (`lock_cost_waived` = "a booked lock cost is waived"; `lock_cost_settled_at_closing` only applies at closing), so every waiver is one of "those costs". Rule = compute.
- **R3-O1 closed.** `head -1003 credit.extended.yaml` vs `blueprint/products/credit.yaml` again differs only by the trailing blank line — byte-verbatim.
- **Docstring/body rounding (class issue) closed.** Every money argument docstring now says "stored as given, rounded to 2 decimal places", and every body uses `round(float(x), 2)`. The "half-up" claim is gone, so docstring and body agree. Every gold argument is an exact cent value anyway.

### six-kind sweep (r4, whole charter)
- compute_basis: every quote verbatim in its own rule; the basis keys equal the compute bindings (all six policies, mechanical check).
- replaced_by: each verbatim in its own rule; scoped "only for such a credit" with the base kept for every other credit or category. Sibling pairs P1/P5 (fixed-credit sentence) and P2/P3 (listed-order clause) name each other's carve-out; neither reinstates the other.
- superseded clauses: each verbatim in its base policy; P6 retires nothing (its pre-closing reduction is an addition).
- Rule/compute rounding and floors: unchanged from r3 and equal, plus the P2 lock sum above.
- Undeclared base departures: none found. The r3 departure is now declared.
- Docstrings: effects equal the bodies; bodies check nothing; no example or gold value in any docstring; no ordering words; uuid8s unchanged (149507f1, 64b83335, e81a44da, 0487fd94, 45c9966f, facd0be5).
- Base text verbatim (above). Remaining observations: R2-O3 ("with its verification documents on file" has no record) and R2-O5 ("closing-service fees" undefined) — unchanged and value-neutral.

### blind values (r4, written before the reveal)
DSL replay on the r4 charter and the unchanged views: task 0 P1 4,700.00, P2 1,118.24, P3 3,342.00 (factor substitutions and fall-backs identical to r2/r3; skip P2 → 3,543; skip P1 → 0); task 1 P4 135, P5 12.94, P6 411.14 (identical; skip P4 → 82.94; skip P5 → 398.20). Contamination disclosure: prior-round GT for both tasks is known; the views are unchanged and the r4 edits do not touch these computations, so this is a re-confirmation.

### closing_checklist (revision_4)
- Reveal at 12:41:56Z; both tasks' GT matched the frozen r4 values figure for figure.
- R3-F1 (and T1-R3-1), R3-O1, R3-O2 and the docstring-rounding class issue are closed. No new defect was found in the six-kind sweep, and no earlier closure regressed.
- Scopes, trees, factors, uuids and gates are as in r2/r3 and green.
- Remaining observations, none of which moves a scored value: R2-O3 (documents-on-file precondition has no record) and R2-O5 ("closing-service fees" undefined).
- The difficulty passes the source-layer policy-task audit at revision 4.
- **task0=PASS  task1=PASS**
