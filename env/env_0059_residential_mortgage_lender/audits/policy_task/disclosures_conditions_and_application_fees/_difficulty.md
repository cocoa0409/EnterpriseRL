# Policy-task audit — disclosures_conditions_and_application_fees / charter-global

## charter_global_frozen

- Scenario: env/env_0059_residential_mortgage_lender (Larkspur Home Lending), category `loan`, M=2.
- Freeze hashes (verified with sha256sum at audit start, equal to the coordinator brief):
  - `tasks/disclosures_conditions_and_application_fees/loan.extended.yaml` sha256=ee06ab3062d368337501dd5d8f72dc14ac126448eacffdb567698e3de24898b5
  - `tasks/disclosures_conditions_and_application_fees/task_tools.py` sha256=5a2dd561da67f4ac0f6e7fab46d22b0d3c2ed8a49c064f721ca71dd8b6f9bcbb
  - `.audit_views/.../0.view.json` sha256=5912f48cf5f01ad6beaf84cfec60d68417995c7b72fa56c6566857b9c7cbc994
  - `.audit_views/.../1.view.json` sha256=1323d720e1b6b3f5a2d7265c92e855ce898b54be7eb0ec3abbdafd8919c1abef
- Freeze time: 2026-10-13T05:50Z (written before any task's GT was revealed; this section contains nothing derived from a revealed GT).
- Auditor: independent policy-task auditor (did not author any artifact of this difficulty).
- Read: blueprint/{blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml (variants and base policies of loan, lock, appraisal, funding, credit, preapproval)}, this difficulty's `loan.extended.yaml`, `task_tools.py`, the two masked views, and the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (for the semantics of COUNT/SUM/LATEST/CFIELD/CPARAM/XSUM/MONTHS/DAYS).
- Masked / not read: every key the views list under `_masked_keys` (charter_scope, computations, db_closure, db_closure_matches_initial_state, design_rationale, evaluation_criteria, prerequisite_closure, required_documents, solvability_contract); `tasks/*.json`; both worklogs; any other env/ scenario; sibling difficulties' tasks dirs; /tmp/*_0059 instantiator scratch.
- Entry conditions (Step 0): gate snapshot supplied by the coordinator — check_extended OK, check_task_tools OK, replay_tasks --check OK, check_solvability OK, check_compute OK, check_grounding OK, check_cross_fire OK, check_traceability NOT OK only on 6 `unlock_*_discoverable_tool:tool_name` misses (KB not yet rendered; re-run after rendering, out of scope here). Masked views and hashes supplied. Input complete.
- Base copy: the base section of `loan.extended.yaml` (everything but `extended_policies`) is equal, key by key, to `blueprint/products/loan.yaml` (parsed comparison: `a == b` True, no differing key).

### policy_conflict_scan

Six extended policies, six task tools, one per policy:

| policy | trigger | subject | target_tool (owner) | base refs | prerequisite (kind, form) |
|---|---|---|---|---|---|
| loan_ext_credit_report_repull_fee | on_request | loan_credit_report_fee_charged | authorize_credit_report_repull_408eaf54 (user) | loan_agg_shared_credit_report | [] |
| loan_ext_corrected_cd_nonrecurring_costs | on_request | loan_cd_corrected | issue_corrected_closing_disclosure_de3eb1f4 (agent) | loan_closing_disclosure_timing | repull (value_input, state) |
| loan_ext_application_fee_due | on_request | loan_application_fee_collected | pay_application_fee_6c3f9eab (user) | loan_evt_application_fee | [] |
| loan_ext_revised_le_zero_tolerance | state_due | loan_le_revised | issue_revised_loan_estimate_22df4f86 (agent) | loan_changed_circumstance | application fee (value_input, state) |
| loan_ext_zero_tolerance_cure | state_due | loan_tolerance_cure_assessed | assess_tolerance_cure_d5e015cb (agent) | loan_tolerance_cure | revised LE (value_input, state) |
| loan_ext_closing_disclosure_lender_credit | state_due | loan_cd_issued | issue_closing_disclosure_6debf4ff (agent) | loan_closing_disclosure_timing | application fee, cure (both value_input, state) |

- Overlapping subjects: none — each event type is the subject of exactly one extended policy. Two extended policies cite the same base policy (loan_closing_disclosure_timing: initial CD and corrected CD); the base policy speaks only to waiting periods and never to lender credits or nonrecurring costs, so the two extended computations do not compete for any base-governed quantity.
- Overlapping inputs read by several policies with the same ladder wording: Verified/Underwritten pre-approval level (application fee rate, revised-LE underwriting relief, cure underwriting add-back), Hometown Heroes occupation (application fee discount, revised-LE processing relief, cure processing add-back), the application fee collected (revised-LE fee line, cure add-back, CD fee credit), borrower-borne lock extensions in the last month (revised-LE extension line, cure extension re-baselining), appraisal rush (revised-LE rush line, cure rush re-baselining), the funded earlier Larkspur closing (application fee and CD returning tiers). Each pair is internally coherent: the relief a revised LE takes off is exactly what the cure adds back, and the borrower-requested increase the revised LE adds is exactly what the cure takes out; no two policies reach incompatible conclusions on the same record.
- Time anchors: every extended computation is evaluated on the date of its own write (`NOW`); "scheduled closing date" is bound in every compute to `loan_files.estimated_closing_date` (see observation O-2).
- Eligibility/status: base eligibilities are inherited (application fee only in processing..clear_to_close; revised LE only before any CD and in processing..clear_to_close; CD timing; credit report window on a new file). No extended rule weakens them.
- Cross-category read boundaries: every `cross_category` entry names exactly the fields its compute reads (lock pricing events, appraisal order/fee ledger/variant params, funding closing fields/params, credit award status/balance/occupation, pre-approval level). Within this scenario's blueprint the difficulties are lock, appraisal, loan (this one), credit, funding; preapproval is not a difficulty, which is why the pre-approval factors carry `cross_difficulty: null`.
- Task scopes (derived by the auditor from the policies' prerequisite graph and the two worlds, before any reveal): task 0 = {corrected CD, credit report repull}; task 1 = {initial CD lender credit, application fee, zero-tolerance cure, revised LE}. Pairwise disjoint and jointly complete over the six extended policies (to be confirmed against `charter_scope` after the reveal).

### rule_compute_equivalence

Swept every binding of every extended policy against its `compute_basis` quotation and back against the `rule`:

- loan_ext_credit_report_repull_fee: recent/year windows ("less than N whole months before the pull date" ↔ `within_months` = `0 <= MONTHS(entry, NOW) < N`), unit price ladder, widest pull (no window in either face), joint/individual bundle, delivery fee keyed to the scheduled closing date, Larkspur vs borrower extension days (`XSUM` over every lock_extension_booked row of the customer; borrower days = total extension days − Larkspur days), share ladder, "delivery fee added to the report cost first, share applied once, rounded at the end" ↔ `RND((report_cost + delivery_fee) * borrower_share, 2)`. Equivalent.
- loan_ext_corrected_cd_nonrecurring_costs: prior figure (latest CD), credit report line (3 tiers), appraisal age from inspection date (report type's validity_days / max_age_with_update_days / reinspection_fee / base_fee via CPARAM), title age from the latest cleared title-commitment document date, VOE age from the latest cleared VVOE resolved date (per-borrower fee), redraw line (drawn and expiring before closing → doc_redraw_fee; drawn and still signable → reschedule_fee; not drawn → 0), "each line added once … rounded to the cent". Equivalent.
- loan_ext_application_fee_due: level rate, heroes discount, e-sign discount (ITP via e-sign portal and LE delivery methods), returning-borrower discount (MONTHS from the funded closing's disbursement), credit report offset (recent charges' borrower coverage vs file borrower count), "rate first, four amounts taken off one after another, never below zero, rounded at the end" ↔ `RND(MX(0.0, fee*rate - …), 2)`. Equivalent (the extra `recent_report_amount > 0` guard in `report_offset` changes no reachable value).
- loan_ext_revised_le_zero_tolerance: fee sheet (5 program fees + credit report per borrower + appraisal base_fee + origination % rounded), extension/relock line, surcharge line, rush line, underwriting relief, processing relief, collected-fee line, "each line once, rounded". Equivalent.
- loan_ext_zero_tolerance_cure: **not equivalent at `measured_increase`** — see finding F-1.
- loan_ext_closing_disclosure_lender_credit: fee credit (credited_at_closing), initial-LE credit, lock credit (negative net price → points × loan_amount_at_lock / 100; zero/positive → 0; no locked lock → initial-LE credit), open cures vs balance, digital closing credit, returning credit, notice credit, award line, "added together once, rounded". Equivalent.
- Factor ladders vs rule prose vs `decides` bindings: every tier of every `factors[].ladder` is a sentence of its rule and a branch of its binding; no binding branch lacks a rule tier. Equivalent.

### action_binding_and_uuids

- `(target_tool, computes)`: (authorize_credit_report_repull_408eaf54, amount), (issue_corrected_closing_disclosure_de3eb1f4, nonrecurring_closing_costs), (pay_application_fee_6c3f9eab, amount), (issue_revised_loan_estimate_22df4f86, zero_tolerance_total), (assess_tolerance_cure_d5e015cb, cure_amount), (issue_closing_disclosure_6debf4ff, lender_credit_amount) — each claimed by exactly one policy.
- uuid8 tails 408eaf54, de3eb1f4, 6c3f9eab, 22df4f86, d5e015cb, 6debf4ff: pairwise distinct, no shared prefix or suffix, no sequential or adjacent pattern; consistent with independent generation.
- Tool bodies (task_tools.py): every function performs one `ctx.create` (plus a balance update for the fee/cure tools) with the caller's values; none reads another table to validate eligibility, ordering or amounts, none refuses or hints. The tool layer judges no prerequisite.
- Docstrings: no docstring names another tool. Ordering words that occur are about business events, not the position of the call among task tools: "before the loan is signed" (corrected CD), "Afterwards the borrower and the agent can see …" (repull, application fee), "adds the first Closing Disclosure (sequence 1 …)" (initial CD). Recorded as observation O-6; no sequence between task tools is stated.

### prerequisite_graph

Edges (blocked → depended-on): corrected CD → repull; revised LE → application fee; cure → revised LE; initial CD → application fee; initial CD → cure.

- `prerequisite` present on all six policies ([] on repull and application fee). Every `problem` is another extended policy id of this file; none points at a base policy or itself. The graph is acyclic (two components: {corrected CD, repull} and {CD, cure, revised LE, application fee}).
- Every `policy_source` is found verbatim as the last sentence(s) of its own policy's `rule` (checked by string search on the parsed YAML).
- All five edges `form: state`, no `fallback_reason` (correct for state form).
- `resolved_by` equals the depended-on policy's `target_tool` on every edge, and each tool's body creates exactly the row the condition tests (fee ledger credit report charge; fee ledger application fee collection; loan_disclosures loan_estimate row with coc_documented_date; loan_tolerance_cures assessed zero_tolerance row).
- `kind: value_input` on every edge and every `gate` names a real binding of the blocked compute: credit_report_line, fee_collected_line, latest_estimate_total, fee_credit, cure_credit.
- No authoring-viewpoint wording ("in this task", "at the opening", "current world") in any `prerequisite` field.
- `condition` vs sentence strength: see observation O-3 (cure ← revised LE condition narrows "the changed circumstance documented most recently on the file" to the latest lock request; the only record-visible changed-circumstance log in the schema is the lock request log, so no world in this difficulty separates the two).

### prerequisite_sentences

Four-point test on each edge:

1. corrected CD ← repull: "The nonrecurring closing costs on a corrected Closing Disclosure are fixed only after the file's fee ledger carries a credit report fee charge whose report is still within the credit report validity window on the scheduled closing date." Connective "only after"; state form (a fee-ledger row and the base policy's "credit report validity window", counted from entry_date over credit_report_max_age_days); no tool, id or snake_case token; strength equals the condition. The only write in this difficulty that books a `loan_credit_report_fee_charged` row is the repull tool; the repull rule does not restate the sentence. Derivation: sentence → "a credit report fee charge" → the policy whose own rule books "one credit report fee charge on the file" on the borrower's authorization (repull). Single reading. PASS.
2. revised LE ← application fee: "The zero-tolerance total on a revised Loan Estimate is not fixed until the fee ledger shows the application fee actually collected on the file." "not … until"; state; clean wording; only `pay_application_fee_6c3f9eab` books `loan_application_fee_collected`. Single reading. PASS on the four points — but see finding F-3 (unreachable state for a zero application fee).
3. cure ← revised LE: "A zero-tolerance cure is assessed only after the latest Loan Estimate on the file carries the changed circumstance documented most recently on the file." "only after"; state; clean; only the revised-LE tool writes a Loan Estimate. The revised-LE rule fixes the documented date of a lock extension as "the date the borrower's extension request was logged in the lock request log", which is how a reader resolves "documented most recently". Single reading. PASS (observation O-3 on the condition's scope).
4. initial CD ← application fee: "The lender credits on a Closing Disclosure are fixed only after the fee ledger carries the application fee collected on the file." PASS on the four points (F-3 applies).
5. initial CD ← cure: "The lender credits on a Closing Disclosure are not fixed until every zero-tolerance increase over the good-faith baseline has a cure entry assessed on the file." "not … until"; state (a cure entry on the file); clean; only the cure tool writes `loan_tolerance_cures`. A reader determines "every zero-tolerance increase over the good-faith baseline" by applying the cure policy's own rule. Single reading. PASS.

- Depended-on rules never restate the blocked sentence; no rule names another policy's tool or id.
- Cross-problem orders stated in rules that ground no declared edge: the revised-LE rule's trigger "before any Closing Disclosure has been issued" and the base sentence "A revised Loan Estimate may be issued only while no Closing Disclosure has been issued" both order revised LE before the initial CD; this order is already entailed by the declared chain CD ← cure ← revised LE, so the two orders never disagree (observation O-4). The corrected-CD trigger "a file that already has a Closing Disclosure" presupposes the initial CD; no task places both in one tree (observation O-4).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- repull vs loan_agg_shared_credit_report: "pulls one tri-merge … reuses it … while it is valid" — followed. "A credit report fee is charged on a new loan file only after the … window … has run out" — governs a new loan file; the repull is on the existing file; followed where it applies (observation O-1: the upgrade tier "< 6 whole months" can price a repull inside the 120-day window on the same file, which base never addresses). "Inside the window … reissued to the new file at no charge" — new file only; not touched. "Outside the window … the fee booked is credit_report_fee_per_borrower … times the number of borrowers pulled" — **declared** in `overwrite` (replaced by the four-part charge). "bona fide third-party charge … never refunded" — followed. Declaration complete.
- corrected CD vs loan_closing_disclosure_timing: every base sentence concerns receipt, waiting periods and rescheduling; the extended rule computes nonrecurring costs, a field base never governs. `overwrite: []` correct.
- application fee vs loan_evt_application_fee: TRID no-fee-before-ITP, status window, once per file — followed. "The amount is application_fee of the program … where that value is 0.00 no fee record is booked" — **declared**. "A later program change never triggers a top-up …", "A fee collected while … application_received or disclosed is … refunded in full" — followed. Declaration complete.
- revised LE vs loan_changed_circumstance: valid-COC list, Larkspur-caused extension exclusion, status/no-CD window, 3-business-day timeliness, 4-specific-business-day receipt — followed (the extension line adds only `cost_bearer='borrower'` entries). "A timely revised Loan Estimate becomes the good-faith baseline for the charges the circumstance actually affected" — the extended revised LE restates other charges too (appraisal surcharge, rush, reliefs, application fee line), but base says nothing about the revised LE's total; the baseline consequence is handled by the cure policy (below). `overwrite: []` acceptable; observation O-5.
- cure vs loan_tolerance_cure: "At closing the charges on the final Closing Disclosure are compared with the good-faith baseline (the initial Loan Estimate, or the latest timely revised Loan Estimate …)" — **declared**. "In the zero-tolerance bucket the cure is the amount by which zero_tolerance_total on the Closing Disclosure exceeds the baseline …" — **declared**. 10-percent bucket, no cross-bucket netting, untoleranced charges, credit_at_closing before consummation, post-closing refund window, "each payment names the assessed cure" — followed. Declaration complete. Residual: the sentence "A timely revised Loan Estimate becomes the good-faith baseline for the charges the circumstance actually affected" lives in loan_changed_circumstance (not a ref of the cure policy) and still speaks of "the good-faith baseline", while the cure rule names the initial LE as `baseline_disclosure_id`; the cure's re-baselining lines reproduce the economic effect, and the cure rule names the baseline disclosure explicitly — observation O-5 (no scored value shown to move).
- initial CD vs loan_closing_disclosure_timing: base never speaks of lender credits. `overwrite: []` correct. Consistent with loan_evt_fee_refund ("credited on the Closing Disclosure" when application_fee_credited_at_closing is true).
- Disguised forms: no anonymous intermediate overriding a base quantity, no 0/1 multiplier zeroing a base amount, no dropped base branch found. The cure's floor issue is a rule/compute defect, not an override (F-1).

### factor_ladders

| policy | factor | label | decides | tiers (fall-through last) | multi-source | cross_difficulty |
|---|---|---|---|---|---|---|
| repull | repull_unit_price | parameter | unit_price | 61.80 / 78.40 / P(92.40) | no | – |
| repull | joint_bundle | method | report_cost | joint×1.40 / joint+individual / individual | yes (ledger borrower_count AND file borrower_count) | – |
| repull | closing_delivery_speed | parameter | delivery_fee | 25 / 10 / 0 | no | – |
| repull | delay_bearer_share | parameter | borrower_share | 0 / 0.5 / 1.0 | yes (two aggregates) | lock |
| corrected CD | report_line_source | method | credit_report_line | booked recent / per-borrower estimate / nothing | tier 2 yes | – |
| corrected CD | appraisal_recertification | parameter | appraisal_update_line | base_fee / reinspection_fee / 0 | no | appraisal |
| corrected CD | title_bringdown | parameter | title_line | 150 / 75 / 0 | no | – |
| corrected CD | employment_reverification | parameter | voe_line | 62.50×n / 24.00×n / 0 | no | – |
| corrected CD | closing_package_redraw | parameter | redraw_line | doc_redraw_fee / reschedule_fee / 0 | yes (closings row AND file closing date) | funding |
| application fee | preapproval_level_rate | parameter | level_rate | 0.50 / 0.75 / 1.0 | no | – (preapproval is not a difficulty) |
| application fee | heroes_fee_discount | parameter | heroes_discount | 100 / 50 / 0 | yes | credit |
| application fee | edisclosure_discount | parameter | esign_discount | 40 / 20 / 0 | yes (ITP row AND LE rows) | – |
| application fee | returning_borrower_discount | parameter | returning_discount | 100 / 50 / 0 | tier 1 yes | funding |
| application fee | credit_report_offset | method | report_offset | booked amount / per-borrower × covered / nothing | tier 1 yes | – |
| revised LE | lock_extension_line | method | extension_line | extension cost / relock fees / nothing | no | lock |
| revised LE | appraisal_surcharge_line | method | surcharge_line | size surcharges / visit charges / nothing | no | appraisal |
| revised LE | appraisal_rush_line | method | rush_line | booked rush / schedule rush_fee / nothing | yes | appraisal |
| revised LE | pre_approval_underwriting_relief | parameter | underwriting_relief | P(underwriting_fee) / 300 / 0 | no | – |
| revised LE | heroes_processing_relief | parameter | processing_relief | P(processing_fee) / 200 / 0 | yes | credit |
| revised LE | collected_fee_line | method | fee_collected_line | collected − fee / −fee / 0 | yes | – |
| cure | extension_rebaseline | method | extension_taken_out | extension cost / relock fees / nothing | no | lock |
| cure | rush_rebaseline | method | rush_taken_out | booked rush / schedule rush_fee / nothing | yes | appraisal |
| cure | underwriting_addback | parameter | underwriting_added_back | P(underwriting_fee) / 300 / 0 | no | – |
| cure | processing_addback | parameter | processing_added_back | P(processing_fee) / 200 / 0 | yes | credit |
| cure | collected_fee_addback | method | fee_added_back | fee − collected / fee / 0 | yes | – |
| initial CD | lock_pricing_credit | method | lock_credit | lock credit / 0 / initial-LE credit | yes (status AND points) | lock |
| initial CD | open_cure_credit | method | cure_credit | open cures / cure balance / 0 | no | – |
| initial CD | digital_closing_credit | parameter | digital_credit | 250 / 150 / 0 | no | funding |
| initial CD | returning_borrower_credit | parameter | returning_credit | 250 / 100 / 0 | tier 1 yes | funding |
| initial CD | notice_period_credit | parameter | notice_credit | 100 / 50 / 0 | no | – |
| initial CD | reserved_award_line | method | award_credit | balance / fixed_credit_amount / 0 | no | credit |

Counts per policy (declared): repull 4 (3p/1m); corrected CD 5 (4p/1m); application fee 5 (4p/1m); revised LE 6 (2p/4m); cure 5 (2p/3m); initial CD 6 (3p/3m). Every factor has ≥3 tiers stated in the rule and implemented in compute; bindings are disjoint within each policy; no `decides` is `result`; every fall-through equals the factor's `baseline`, and each policy's `baseline.rule` is a verbatim sentence of its rule from which a definite number follows with no factor applied. Labels are honest (method tiers switch the source/algorithm; parameter tiers switch a number).

Structural defects found (detailed in findings):
- F-2: closing_package_redraw — middle tier `reschedule_fee` is 0.00 for every one of the seven closing methods in `blueprint/products/funding.yaml`, the same value as the fall-through 0.0.
- F-4: tiers made dead at handling time by the policy's own prerequisite: report_line_source tier 2 (corrected CD), collected_fee_line tier 3 (revised LE), collected_fee_addback tier 3 (cure, transitively).
- Realism observations (no RED demonstrated): O-7 (delay share keyed on lock-extension bearers; CD short-notice credit rewards a late CD), O-8 (Desktop appraisal max_age_with_update_days 0 < validity_days 120 makes the reinspection tier empty for that report type).

### findings

**F-1 — SOURCE-POLICY RED (charter-global; demonstrated in task 1 as SOURCE-TASK RED).** Symptom: the sign of "the measured increase" in loan_ext_zero_tolerance_cure is not fixed by the rule, and the compute disagrees with its own compute_basis. Root cause: the rule never defines "the measured increase"; the only quantitative sentence about it is "The standard zero-tolerance cure is the amount by which the zero-tolerance total on the latest Loan Estimate on the file exceeds the zero-tolerance total on the initial Loan Estimate, and nothing when it does not exceed it." `compute_basis.measured_increase` quotes exactly that floored sentence, while the binding is `measured_increase: "latest_estimate_total - initial_estimate_total"` (unfloored, can be negative); the floor appears again only on the final `result`. Two readings: (A) signed difference, adjust, then floor; (B) floor the increase at zero first ("the amount by which … exceeds …, and nothing when it does not exceed it"), then adjust. The rule's rationale clause "because a fee decrease never offsets an increase in another charge" favours (A), but the text, and the artifact's own basis mapping, support (B). Consequence: whenever the latest LE total is below the initial LE total and add-backs apply, the two readings give different cures (task 1: see 1.md). Location: loan.extended.yaml › loan_ext_zero_tolerance_cure › rule, compute_basis.measured_increase, compute.measured_increase. Bears on: task 1.

**F-2 — SOURCE-FACTOR RED (charter-global structure; affects task 0).** Symptom: two tiers of the closing_package_redraw ladder select the same value. Root cause: tier 2 "closing documents were drawn and may still be signed on the scheduled closing date → CPARAM('funding', 'reschedule_fee')" and the fall-through "no closing documents drawn → 0.0"; `reschedule_fee: 0.0` for Larkspur Traditional Wet, Escrow Dry-Funding, Mobile Notary, Hybrid eClosing, Remote Online Notarization, Power of Attorney and Mail-Away Closing (blueprint/products/funding.yaml variants). Consequence: the ladder has two distinct outcomes, not three; the factor cannot count toward the bounds. Location: loan.extended.yaml › loan_ext_corrected_cd_nonrecurring_costs › factors[closing_package_redraw], rule sentence "where they have been drawn and may still be signed on the scheduled closing date, the closing method's reschedule_fee is added". Bears on: task 0.

**F-3 — SOURCE-POLICY RED (charter-global; moves no scored value of task 0 or task 1).** Symptom: for a program whose application fee due is 0.00 the revised LE and the initial CD can never be fixed. Evidence: base loan_evt_application_fee and the extended replacement both say "where the amount due is 0.00 no fee record is booked"; program application_fee is 0.00 for Larkspur VA 30-Year Fixed and Larkspur HomeReady 30-Year Fixed (products/loan.yaml variants), and the extended fee can also reach 0.00 through `MX(0.0, …)`. The revised-LE rule says "When a changed circumstance is documented on a file before any Closing Disclosure has been issued, Larkspur issues a revised Loan Estimate …" and "The zero-tolerance total on a revised Loan Estimate is not fixed until the fee ledger shows the application fee actually collected on the file"; the CD rule says "Larkspur issues the initial Closing Disclosure of a file that is clear to close …" and "The lender credits on a Closing Disclosure are fixed only after the fee ledger carries the application fee collected on the file." Same situation (a VA file, clear to close, CoC documented): the issuing sentences require the disclosure; the prerequisite sentences forbid fixing it forever. Both tasks are Conventional 30-Year Fixed files whose fee due is above zero, so neither scored value moves. Location: the two `policy_source` sentences and their `condition`s.

**F-4 — SOURCE-FACTOR RED (charter-global structure; demonstrated in task 0, structural only in task 1).** Symptom: a tier of a factor's ladder can never hold at the handling time of its own write, because the policy's prerequisite sentence asserts its negation. Evidence: (a) corrected CD, report_line_source tier 2 "no such recent charge, and the latest credit report fee charge would be more than credit_report_max_age_days days old on the scheduled closing date" vs the prerequisite "fixed only after the file's fee ledger carries a credit report fee charge whose report is still within the credit report validity window on the scheduled closing date" (condition: latest charge no more than credit_report_max_age_days before estimated_closing_date) — once the prerequisite holds the second conjunct of tier 2 is false for every customer; the tier exists only as the value of a skipped prerequisite. (b) revised LE, collected_fee_line fall-through "no collection on the ledger" vs prerequisite "not fixed until the fee ledger shows the application fee actually collected" — the part "an application fee collection is on the fee ledger" of tier 1 holds of every customer who reaches the write. (c) cure, collected_fee_addback fall-through "no application fee collection is on the ledger" — unreachable transitively (cure waits on the revised LE, which waits on the collection). Consequence: each of these ladders has at most two live tiers at handling time, below the three-tier floor; struck factors: report_line_source, collected_fee_line, collected_fee_addback. After striking, revised LE keeps 5 factors (2p/3m) and the cure 4 (2p/2m) — within bounds; the corrected CD keeps appraisal_recertification, title_bringdown, employment_reverification (and closing_package_redraw is struck by F-2): 3 factors, 0 `method` — below the 4-factor / 1-method floor. Bears on: task 0 (bounds fail); task 1 (structural defect in two of its computations, bounds still met).

Observations (no RED demonstrated):
- O-1 repull upgrade tier vs base window: the < 6-month upgrade price can apply inside the base 120-day "reusable" window on the same file; base's no-charge reissue speaks only of a new file. No task places a repull inside the window (task 0: 124 days).
- O-2 "scheduled closing date" is bound to `loan_files.estimated_closing_date`, while `closings.scheduled_closing_date` carries the same name; equal in both worlds (2026-10-30; 2026-10-22).
- O-3 cure ← revised LE `condition` narrows "the changed circumstance documented most recently on the file" to the latest lock request date; equal in task 1's world.
- O-4 the revised-LE trigger/base "only while no Closing Disclosure has been issued" and the corrected-CD trigger "a file that already has a Closing Disclosure" state cross-problem orders that ground no declared edge; each is consistent with the declared edges and with both worlds. A side effect visible in task 0's world: after a CD exists, a new lock-extension CoC can never be carried by a Loan Estimate, so the cure policy's prerequisite can never hold there (its adjusted increase is ≤ 0 in that world, so nothing is owed).
- O-5 the loan_changed_circumstance sentence "A timely revised Loan Estimate becomes the good-faith baseline for the charges the circumstance actually affected" coexists with the cure rule naming the initial LE as the baseline disclosure; the cure rule is explicit and its re-baselining lines reproduce the economic effect; no scored value shown to move.
- O-6 docstring ordering words describe business events ("before the loan is signed", "Afterwards … can see", "the first Closing Disclosure"), not the order of task-tool calls.
- O-7 realism: the repull delay share keys the borrower's share to who bore lock-extension days (a proxy for who caused the delay — plausible); the initial-CD short-notice credit pays the borrower more the later the CD is issued relative to closing (plausible as a service-recovery credit, unusual).
- O-8 Desktop appraisal `max_age_with_update_days: 0` < `validity_days: 120`, so the reinspection tier is empty for that report type (not used by either task).
- O-9 `CFIELD` returns the first matching cross-category holding; the returning-borrower tiers ("an earlier Larkspur closing", "the customer's only funded Larkspur closing") and the award line ("the closing cost credit reserved against the file") are therefore order-dependent when a customer has several such holdings; each world has exactly one.

## closing_checklist

Written after both reveals (2026-10-13T05:58Z). Everything above this heading was frozen before any reveal (sha256 1aa88aff…65cd at freeze) and has not been edited.

**The difficulty is NOT closed: the four relationships do not all PASS.**

| task | policy self-consistency | problem tree | factors | unique solution |
|---|---|---|---|---|
| 0 (corrected CD ← repull) | PASS | PASS | SOURCE-FACTOR RED (F-2, F-4a: corrected CD left with 3 factors, 0 method) | PASS (all args equal GT) |
| 1 (CD ← fee, cure ← revised LE ← fee) | SOURCE-POLICY RED (F-1) | SOURCE-CHAIN RED (false "cure 0.00" in prerequisite_closure) | SOURCE-FACTOR RED (F-4b,c; bounds still met) | SOURCE-TASK RED (cure 150.00 vs 326.90; CD 2,525.10 vs 2,702.00) |

Checklist items:
- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; `_difficulty.md` sits alongside; first revision (no older revisions). Comparison sections do not all carry PASS.
- Coverage and scopes: charter_scope 0 = {loan_ext_credit_report_repull_fee, loan_ext_corrected_cd_nonrecurring_costs}; charter_scope 1 = {loan_ext_application_fee_due, loan_ext_revised_le_zero_tolerance, loan_ext_zero_tolerance_cure, loan_ext_closing_disclosure_lender_credit} — equal to the scopes derived before the reveal; pairwise disjoint; jointly cover all six extended policies and six task tools; each uuid8 independent.
- Trees: task 0 one prerequisite, one value_input edge, owner=user repull; task 1 three prerequisites, four value_input edges, owner=user application fee; the difficulty-wide graph is acyclic.
- Factors: every declared factor bears weight against an honest baseline on its task's world and every whole-baseline number differs from gold (184.80/6,842.35; 450.00/2,879.90/0.00/473.10); ladder defects F-2 and F-4 remain; the corrected-CD computation is below bounds after the tests.
- Charter-global REDs with no scored consequence in either task: F-3 (zero application fee makes the revised LE and initial CD unfixable).
- Instantiation-stage gates: not re-run by this audit (the coordinator supplied the snapshot; check_traceability NOT OK pending KB render, out of scope).

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2. Input hashes (verified by sha256sum, equal to the coordinator brief): `loan.extended.yaml` befac70315b7cc1381f58cc66bfc618f1cb6d123144964e99d19e10585e11496 (changed from ee06ab30…); `task_tools.py` ea7810eae70f69417b73de45af34caef39ecc62db1d2adb91880d3dda95f1bfa (changed from 5a2dd561…); `0.view.json` bcc78dd2…6c4d; `1.view.json` a1f8c7f4…766a. Both shared inputs changed, so every charter-global section is re-derived below; the round-1 text above is left untouched.
- Freeze time 2026-10-13T11:36Z, before either round-2 task file was opened. Nothing in this section comes from a revealed GT. Same masked/unread set as round 1 (views list the same `_masked_keys`); worklogs not read; no recursive search.
- Base copy: the base section still equals `blueprint/products/loan.yaml` (parsed equality True).
- Gate snapshot (coordinator, round 2): EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; TRACEABILITY NOT OK only on 6 unlock tool-name misses (pre-KB, out of scope).

### What changed (charter and tools)

- Repull: a fifth factor `inquiry_supplement` (parameter: 2+ issued credit_inquiry_explanation conditions → 45.00; exactly 1 → 25.00; none → 0), added to the report cost with the delivery fee before the share. `overwrite.replaced_by` updated to "five parts".
- Corrected CD: `report_line_source` is no longer a factor (the credit report line is now a single sentence: charges booked < 1 month before the issue date are added at their booked amount); `closing_package_redraw` removed; `title_bringdown` became a `method` (new commitment priced at 1.10 per $1,000 of base loan amount when > 180 days / flat 75.00 date-down when > 90 days / nothing); new `closing_service_line` (method, cross: funding): closing now scheduled opened after the latest CD + Mobile Notary + Saturday/Sunday → closing_method_fee + after_hours_signing_fee; opened after the latest CD + Mobile Notary or RON on a weekday → closing_method_fee; otherwise nothing.
- Application fee: zero-fee programs book no record; a fee-charging program whose amount due works out to 0.00 books a 0.00 collection. Overwrite `replaced_by` carries the new wording. Tool docstring amount now "0.00 or more".
- Revised LE / initial CD prerequisite sentences now end "wherever the program the file is in charges an application fee"; conditions add "or the program the file is in has an application_fee of 0.00"; the fee-line / add-back fall-through tiers now read "(no collection on the ledger, as for a program that charges no application fee)".
- Cure: "The measured increase of the cure is … minus …, kept with its sign, so that it is negative when the latest total is the lower one"; standard cure = measured increase where above zero; result "adjusts the signed measured increase"; a third overwrite declares the loan_changed_circumstance sentence "A timely revised Loan Estimate becomes the good-faith baseline …" (replaced by "For the cure the initial Loan Estimate stays the baseline disclosure …"), and `base_policy_refs` now lists loan_changed_circumstance; the cure ← revised LE condition now reads "no earlier than the date of the changed circumstance documented most recently on the file (for a lock extension, the request_date …)".
- Initial CD: new dating sentence "A Closing Disclosure is never dated on a day on which a Loan Estimate was issued on the file: when a Loan Estimate was issued on the file on the day the Closing Disclosure is prepared, the Closing Disclosure is dated and delivered on the next business day …; otherwise it is dated and delivered on the day it is prepared." Returning and notice credits are measured from "the day the Closing Disclosure is prepared". Cure-credit tier 2 is now unpaid `post_closing_refund` cures moved onto the CD (was: the tolerance cure balance). Tool `issue_closing_disclosure_6debf4ff` gained `issued_date` ("today's date or a later delivery date, never empty") and writes it as the disclosure's issued_date.

### Re-derived checks (revision 2)

- policy_conflict_scan: still one subject per policy and one tool per policy; scopes as in round 1 ({repull, corrected CD}; {fee, revised LE, cure, CD}), disjoint and complete.
- rule_compute_equivalence: repull, application fee, revised LE (except N-1), cure, CD equivalent; the cure's `compute_basis.measured_increase` now quotes the signed sentence and the binding is signed — **F-1 closed**. Corrected CD equivalent except N-2. `signing_weekday` = DAYS('2026-01-03', date) % 7 with 2026-01-03 a Saturday, so 0/1 = Saturday/Sunday — a faithful implementation of "falls on a Saturday or Sunday".
- action_binding_and_uuids: unchanged tool names/uuid8s; each (target_tool, computes) claimed once; tool bodies still validate nothing (the CD tool writes the passed `issued_date` without checking it). Docstrings name no other tool.
- prerequisite_graph: same five edges, acyclic, all state-form value_input, gates exist; every `policy_source` verbatim in its own rule; conditions now match their sentences' scope (cure ← revised LE condition is the sentence's general CoC with the lock example) — **O-3 closed**.
- prerequisite_sentences: four-point test passes on all five; for the two fee edges the qualifier "wherever the program the file is in charges an application fee" matches the widened condition and makes the waited-on state reachable for every program (a 0.00 collection is booked where a charging program works out 0.00) — **F-3 closed**.
- override_declarations: repull and fee overwrites name the base sentences and carry the new wording; the cure now declares the loan_changed_circumstance baseline sentence — **O-5 closed**. Corrected CD and CD `overwrite: []` still correct (base never governs nonrecurring costs, lender credits or the CD's date; the dating sentence is stricter than, not contrary to, base loan_closing_disclosure_timing and loan_changed_circumstance).
- factor_ladders: repull 5 (4p/1m: unit price, delivery, supplement, share / joint bundle); corrected CD 4 (2p/2m: appraisal, VOE / title, closing service); fee 5 (4p/1m); revised LE 6 (2p/4m); cure 5 (2p/3m); CD 6 (3p/3m). Every ladder ≥ 3 distinct outcomes: closing_service_line 250.00 (Mobile weekend) / 175.00 or 25.00 (weekday) / 0; title 1.10 × base/1000 / 75.00 / 0; supplement 45 / 25 / 0. **F-2 closed** (redraw gone). **F-4a closed** (credit report line no longer a factor). **F-4b/F-4c closed**: the fall-through "no collection on the ledger" is now the handling-time state of every zero-fee program (prerequisite exempts them), so it divides customers. No ladder is dead at handling time.
- CD dating (coordinator question): TRID-realistic — Reg. Z §1026.19(e)(4)(ii) bars providing a revised Loan Estimate on or after the date the Closing Disclosure is provided, so a CD must not carry the date of a same-day revised LE; dating and delivering it on the next business day is the minimal compliant practice, and the base 3-specific-business-day receipt rule is then counted from the actual receipt. Uniquely entailed: the date depends only on whether a Loan Estimate row is dated the preparation day and on the stated business-day definition (Mon–Fri excluding Fed holidays). The amounts that depend on "the day the Closing Disclosure is prepared" (returning, notice) are anchored to the preparation day, not to the dated day, by explicit wording.

### findings (revision 2, charter-global)

Round-1 items: F-1 closed; F-2 closed; F-3 closed; F-4a, F-4b, F-4c closed; O-3 closed; O-5 closed. O-1, O-2, O-4, O-6, O-7, O-8, O-9 unchanged (still observations).

**N-1 — SOURCE-POLICY RED (new, introduced by the F-3 rework; moves no scored value of either task).** Symptom: a 0.00 application-fee collection — now booked by rule "where a program that charges one works out an amount due of 0.00, the collection is booked at 0.00" — is treated by the rule as a collection and by the compute as no collection. Evidence: revised-LE rule "where an application fee collection is on the file's fee ledger and none of it has been refunded, the program's application_fee in the fee sheet is replaced by the amount actually collected" vs compute `fee_collected_line: (fee_collected - P('application_fee')) if (fee_collected > 0 and fee_refunded == 0) else (…) else 0.0`; cure rule "where the application fee collected on the fee ledger has not been refunded and is below the program's application_fee, the difference … is added back" vs compute `fee_added_back: … if (app_fee_paid > 0 and …)`. Demonstration (auditor probe on task 1's file with a 0.00 collection row): rule gives fee line −450.00 and add-back +450.00; compute gives 0.00 and 0.00. Reachable: Conventional 30 (450.00) with an Underwritten pre-approval (225.00), first-responder Heroes (−100), full e-sign (−40), recent returning (−100) → 0.00. Location: loan.extended.yaml › loan_ext_revised_le_zero_tolerance compute.fee_collected_line; loan_ext_zero_tolerance_cure compute.fee_added_back. Neither task's world books a 0.00 collection (task 1 fee 105.10).

**N-2 — SOURCE-POLICY RED (new; moves no scored value of either task).** Symptom: the corrected-CD closing service ladder gives no rule outcome for a Remote Online Notarization closing opened after the latest CD that signs on a Saturday or Sunday, while compute adds the RON closing_method_fee (25.00). Evidence: rule tiers — (1) "is a Larkspur Mobile Notary Closing and its scheduled closing date falls on a Saturday or Sunday", (2) "is a Larkspur Mobile Notary Closing or a Larkspur Remote Online Notarization Closing on a weekday", (3) "opened before the latest Closing Disclosure was issued, or is of any other method"; compute tier 2 `CPARAM(... 'closing_method_fee' ...) if (service_opened_after_cd and (service_method == 'Larkspur Mobile Notary Closing' or service_method == 'Larkspur Remote Online Notarization Closing'))` has no weekday test. The case is in neither rule tier, so compute supplies a basis the rule lacks. Location: loan_ext_corrected_cd_nonrecurring_costs rule (closing service sentences), compute.closing_service_line. Task 0's closing is a Mobile Notary on Friday 2026-10-30 — unaffected.

Observations (revision 2):
- O-10 the CD dating sentence makes the CD's `issued_date` depend on whether the revised LE was issued that day — a value link to another problem stated outside a prerequisite sentence. It orders nothing (the CD is last in the declared chain CD ← cure ← revised LE either way) and it is quoted in the CD's own rule, so it is discoverable; no second order or terminal state arises.
- O-11 corrected CD: `baseline.rule` ("carried forward unchanged") gives 6,842.35-type figures while the non-factor credit report line is always added at handling time (the prerequisite guarantees a charge < 1 month old), so "all factors at baseline" and "baseline.rule alone" differ by that line; both differ from gold in task 0.
- O-12 realism of new factors: credit-inquiry supplement (bureaus charge per supplemented account — plausible); closing service fee for a newly opened Mobile Notary/RON closing with the funding schedule's after-hours fee on weekends (consistent with funding_closing_fees: after_hours fee on Saturday/Sunday where after_hours_available is true — true for Mobile Notary).

### closing_checklist (revision 2)

Written after both round-2 reveals (2026-10-13T11:40Z); the revision_2 charter-global text above was frozen before them.

| task | policy self-consistency | problem tree | factors | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS (F-2, F-4a closed) | PASS |
| 1 | PASS (F-1 closed) | PASS (false proof figures corrected) | PASS (F-4b, F-4c closed) | PASS (signed cure unique; CD dated 2026-10-16) |

- Round-1 REDs: F-1, F-2, F-3, F-4a, F-4b, F-4c, task-1 SOURCE-CHAIN, task-0 SOURCE-FACTOR, task-1 SOURCE-FACTOR/SOURCE-TASK — all verified closed; O-3, O-5 closed. No regression in either task's scored solution (task 1's four values unchanged; task 0's values changed only through the new world rows and factors, all re-derived blind and equal to GT).
- Scopes: charter_scope 0 = {repull, corrected CD}, 1 = {fee, revised LE, cure, CD} — disjoint, complete, equal to the pre-reveal derivation. Trees: task 0 n=1, task 1 n=3, all edges value_input, one owner=user write each, graph acyclic. Factors: every factor bears weight against an honest baseline; bounds met; whole-baseline figures differ from gold.
- **Not closed:** two new charter-global SOURCE-POLICY REDs remain open, neither moving a scored value of task 0 or task 1: N-1 (a 0.00 application-fee collection, introduced by the F-3 rework, is a collection to the rule and no collection to the revised-LE fee line and the cure add-back compute) and N-2 (closing service line: RON signing on a Saturday/Sunday has no rule tier, compute adds the RON closing_method_fee).
- Instantiation-stage gates: coordinator's round-2 snapshot (all OK except the pre-KB traceability unlock misses); not re-run by the auditor.

## revision_3

### entry gate (revision 3)

- `/tmp/erl0059_coord/gates.sh disclosures_conditions_and_application_fees --trace`, run by the auditor from the repository root at 2026-10-13T12:5xZ: EXTENDED OK ("[PASS] compatible charter; … all policies are covered across the suite with disjoint scopes"); TASK TOOL CONTRACT OK (6 tools); REPLAY OK (0.json 16 acts True True 0 32 32 True; 1.json 23 acts True True 0 30 30 True); SOLVABILITY OK (1.json True 4 6 16 True); COMPUTE OK (history_rows_max=10(>= 8), branches_max=80(>= 5)); GROUNDING OK (1.json 2 4 4 8 True); SCOPE OK (2 tasks, policies=6, hard-fails=0); TRACEABILITY OK (0.json copied 20 missing 0; 1.json copied 33 missing 0). No red gate; entry admitted.
- `.venv/bin/python /tmp/erl0059_coord/mkviews.py disclosures_conditions_and_application_fees` printed: 0.view.json sha256=bcc78dd25f18e00338ba92540ded9d4f73e9173cc8811c7817d9d47340966c4d; 1.view.json sha256=a1f8c7f4d356d058809d13fcf0d08da282db78776ca5e251889ab42d3480766a (both identical to round 2 — worlds and personas unchanged); task_tools.py sha256=50108d564086df670b300b57121bec54444059c6297096d2087b8124f0f57ace (changed); loan.extended.yaml sha256=2fc1682a9c44fe2ee5f7808079b8bccefcd70c833549640ef487b30e13fd133d (changed).
- Freeze: this section and the revision_3 derivations of 0.md/1.md were written before either round-3 task file was opened. Base copy still equals blueprint/products/loan.yaml.

### What changed (charter and tools, revision 3)

- Revised-LE fee line and cure add-back: tier 1 now "where an application fee collection entry is on the … fee ledger, whatever its amount (a 0.00 collection included), and … not … refunded"; compute keys on `COUNT(... loan_application_fee_collected) >= 1` instead of `amount > 0`; cure add-back adds "which is nothing when the full program fee was collected".
- Corrected-CD closing service tier 2: "… a Larkspur Mobile Notary Closing signing on a weekday, or a Larkspur Remote Online Notarization Closing signing on any day …" (matches compute).
- Corrected-CD baseline: "The standard corrected figure is the nonrecurring closing costs shown on the latest Closing Disclosure issued on the file, carried forward, plus the credit report fee charges booked on the file less than recent_charge_months whole months before the issue date at their booked amount." (baseline.params [recent_charge_months]).
- Repull joint-bundle fall-through adds "or the file now has a single borrower" (closes the widest-pull ≥ 2 / one-borrower gap). Application-fee credit report offset: "the booked amount of those charges, whatever it is (a 0.00 charge included)", compute guard `recent_report_amount > 0` dropped. Returning tier 2 (fee and CD): "the customer's funded Larkspur closing funded returning_window_months or more months before" (was "only funded"). Corrected-CD tool docstring: borrower_requested_change = "a change to the loan or the transaction that the borrower asked for".

### Class re-check (revision 3)

- Mechanical: every `compute_basis` quote, every `overwrite.replaced_by`, every prerequisite `policy_source` and every `baseline.rule` is a verbatim substring of its own rule (all six policies, whitespace-normalised); every `superseded_clause` is verbatim in the named base policy; cure `base_policy_refs` lists both overwritten base policies.
- Every compute branch has a rule tier, and every rule tier a branch — swept branch by branch: repull (unit price 3/3; bundle 3/3 incl. the new single-borrower case; delivery 3/3; supplement 3/3; share 3/3); application fee (rate, heroes, e-sign, returning, offset 3/3 each); revised LE (extension, surcharge, rush, reliefs, fee line 3/3 each — fee line now count-based as the rule says); cure (same, signed measured increase, floor only on the result); CD (lock 3/3, cure credit 3/3, digital, returning, notice, award 3/3). Exception: N-3 below (corrected-CD closing service, same-day opening).
- Sign/floor conventions: cure signed then floored once (rule = compute); application fee floored at zero once (rule = compute); lock credit "as a positive amount" (compute negates negative points). Consistent.
- Probes on task 1's file (auditor scratch, charter compute): a 0.00 application-fee collection now gives revised-LE fee line −450.00 and cure add-back +450.00 — exactly the rule's tier 1 → **N-1 closed**. RON on a weekend: rule tier 2 now covers it and compute's tier 2 has no weekday test → **N-2 closed**. O-11 closed (baseline.rule now includes the always-present credit report line; all-factor baseline = baseline.rule figure).
- Docstrings: no tool names another tool or states a call order. See N-4.

### findings (revision 3, charter-global)

Round-2 items: N-1 closed; N-2 closed; O-11 closed. O-10 (CD date depends on a same-day LE) and O-12 (realism) unchanged, still observations. Round-1 observations O-1, O-2, O-4, O-6, O-7, O-8 unchanged; O-9 (first-match CFIELD) persists and is now sharper in wording: the returning tier 2 reads "the customer's funded Larkspur closing funded … 36 or more months before" while compute reads only the first funded closing found, so a customer with one recent and one old funded closing can be read into tier 2 by compute and tier 1 by the rule — no task world has two funded closings.

**N-3 — SOURCE-POLICY RED (new class instance; moves no scored value of either task).** The corrected-CD closing service ladder still leaves one compute branch without a rule tier: a Mobile Notary or RON closing **opened on the same day** the latest Closing Disclosure was issued. Rule: tiers 1–2 need "opened after the latest Closing Disclosure was issued", tier 3 needs "opened before the latest Closing Disclosure was issued, or is of any other method". Compute: `service_opened_after_cd = DAYS(latest CD issued_date, closing opened_date) > 0`, so a same-day opening falls to 0.00. Probe on task 0's file with the Mobile Notary closing's opened_date set to 2026-10-02 (the CD's date): compute 0.00; the rule states no outcome (a reader may equally count a same-day opening as "after" the CD and add 175.00). Location: loan_ext_corrected_cd_nonrecurring_costs rule (closing service sentence) / compute.service_opened_after_cd. Task 0's closing opened 2026-10-09, a week after the CD.

**N-4 — SOURCE-POLICY RED (tool contract vs rule; moves no scored value of either task).** The repull rule books "one credit report fee charge on the file" whatever the share, and its first delay-share tier makes "the borrower's share … zero" (charge 0.00); the application-fee rule now names "(a 0.00 charge included)" for credit report charges. The repull tool's contract still says `amount: … US dollars as a positive number with exactly 2 decimal places`. In the zero-share situation the rule requires booking a 0.00 charge (and the corrected CD's prerequisite waits on that row), while the contract excludes 0.00 as an argument — two artifacts, two conclusions. Location: task_tools.py `authorize_credit_report_repull_408eaf54` Args.amount; loan_ext_credit_report_repull_fee rule. Task 0's share is 0.50 (charge 60.76).

Observation O-13: the closing-service compute selects the closing with `status='scheduled'`; a file whose current closing sits in `docs_out` (drawn package, still set for the date) has no such row, and `DAYS(…, None)` gives no number, while the rule's "the closing now scheduled on the file" would still name that closing. The funding lifecycle sends a redrawn package back to `scheduled` when the signing is reset, so a moved closing normally reaches the corrected CD as `scheduled`; not reachable in either world.

### closing_checklist (revision 3)

Written after both round-3 reveals (2026-10-13T12:57Z).

- Per task: task 0 PASS on all four relationships; task 1 PASS on all four. Every scored value (task 0: 60.76, 7,376.11 and the CD's sequence/reason/date; task 1: 105.10, 2,703.00, 150.00, 2026-10-16, 2,525.10 and their ids/enums) is re-derived blind and equals GT; no regression from round 2.
- Round-2 REDs: N-1 closed (0.00 collection now a collection in rule and compute, probe −450.00 / +450.00); N-2 closed (RON any day in rule and compute). O-11 closed.
- Gates: the auditor's own run of gates.sh --trace — all eight OK, TRACEABILITY 0 misses.
- Still open, charter-global, moving no scored value of either task: **N-3** (corrected-CD closing service: a Mobile Notary/RON closing opened the same day as the latest CD has no rule tier; compute gives 0.00) and **N-4** (repull rule books a 0.00 charge on the zero-share tier; the repull tool contract allows only a positive amount). Observations O-9 (first-match CFIELD vs "an earlier / the customer's funded closing"), O-10, O-12, O-13 recorded.
- The difficulty passes the per-task source-layer audit; it is not fully closed while N-3 and N-4 stand, unless the coordinator logs them as known charter issues with no scored effect.

task0=PASS  task1=PASS

## revision_4

### entry gate (revision 4)

- `/tmp/erl0059_coord/gates.sh disclosures_conditions_and_application_fees --trace`, run by the auditor at 2026-10-13T14:1xZ: EXTENDED OK; TASK TOOL CONTRACT OK (6 tools); REPLAY OK (0.json 16 True True 0 32 32 True; 1.json 24 True True 0 31 31 True); SOLVABILITY OK (1.json True 4 6 16 True); COMPUTE OK (history_rows_max=10(>= 8), branches_max=90(>= 5)); GROUNDING OK (1.json 2 4 4 8 True); SCOPE OK (2 tasks, policies=6, hard-fails=0); TRACEABILITY OK (0.json 20/0 missing, 1.json 34/0 missing). No red gate; entry admitted.
- `mkviews.py` printed: 0.view.json sha256=bcc78dd25f18e00338ba92540ded9d4f73e9173cc8811c7817d9d47340966c4d (unchanged); 1.view.json sha256=611cf5d8577a0595c74b496745bfbc5e9915faefdfbf835b381f87c78607b45d (changed: one `funding_wires` row added — `3c0f7e7a…` funding_wire_sent on the 2019 closing `38aa6fe8…`, wire_date 2019-06-12, equal to that closing's disbursement_date; persona unchanged); task_tools.py sha256=ec0bb1f1f9dfdf113713bca75d6d90aa64b7c0ee039e3395890d8e70b278dc4e; loan.extended.yaml sha256=b7e75bb85c0624da856d625908bd665cf1252466cb166243448d57b81683c20e.
- Also read, as instructed: `audits/render_source/disclosures_conditions_and_application_fees/render_loan_r1.md` (renderer's source findings against the round-2 source; no task values in it).
- Freeze: this section and the revision_4 derivations of 0.md/1.md were written before either round-4 task file was opened. Base copy still equals blueprint/products/loan.yaml.

### Render findings and round-3 REDs, verified in the round-4 source

| item | round-4 source | verdict |
|---|---|---|
| R-1 repull overwrite narrows the retired base fee clause | replaced_by: "For a credit report pulled again on an existing loan file at the borrower's authorization, and only for such a repull, the charge is worked out in five parts …; every other pull made outside the window or for a customer with no earlier charge, including the first pull on a new loan file, is still charged credit_report_fee_per_borrower of the file's program times the number of borrowers pulled." | closed — base fee kept for every non-repull pull |
| R-2 cure overwrite[0] drops the 10 percent bucket | replaced_by: "For the zero-tolerance bucket before consummation, and only for it, …; the 10 percent bucket, and any violation found only after consummation, are still compared on the final Closing Disclosure with the good-faith baseline (the initial Loan Estimate, or the latest timely revised Loan Estimate whose changed circumstance affected the charge)." | closed |
| R-2b cure overwrite[1] | replaced_by now also keeps "A zero-tolerance violation found only after consummation is still the amount by which zero_tolerance_total on the final Closing Disclosure exceeds the baseline zero_tolerance_total." | closed (post-closing zero-tolerance kept) |
| R-3 cure overwrite[2] drops the CoC baseline rule outside the cure | replaced_by: "For the zero-tolerance cure assessed before consummation, and only for it, the initial Loan Estimate stays the baseline disclosure …; for every other comparison, including the 10 percent bucket and the final Closing Disclosure after consummation, a timely revised Loan Estimate still becomes the good-faith baseline …, and an untimely one … still leaves the earlier Loan Estimate as the baseline." | closed |
| R-4 0.00 collection | closed in round 3 (count-based) | still closed |
| R-5 Desktop appraisal ladder overlap (max_age_with_update_days 0 < validity_days 120) | tier 1 now "older than its report type's validity_days and also older than its max_age_with_update_days"; compute `appraisal_age > validity_days and appraisal_age > max_age_with_update_days`; tier 2 "older than validity_days but no older than max_age_with_update_days". Tiers pairwise disjoint for every report type (Desktop: ≤ 120 → 0, > 120 → base_fee; others: ≤ 120 → 0, 121–365 → reinspection, > 365 → base). This also closes my round-1 O-8, which I had recorded only as an empty tier and had missed as an overlap. | closed |
| R-6 RON weekend | closed in round 3 | still closed |
| R-7 several old funded closings | returning tiers (fee and CD) now "read from the date of the most recent funding wire Larkspur sent on any closing of the customer": < 36 whole months → recent; ≥ 36 → earlier; no wire → nothing; compute `XLATEST('funding','funding_wires','wire_date', event_type='funding_wire_sent')`. One latest date, three disjoint tiers, no first-match dependency. | closed (also closes the returning part of my O-9) |
| R-8 report_offset guard; joint bundle with one borrower | closed in round 3 | still closed |
| R-9 base `loan_condition_management` vs `loan_msr_overdue_conditions` class mismatch | base section (frozen blueprint); no extended policy reads it; no task tree touches suspension | base known issue B-1, moves no scored value |
| N-3 corrected-CD closing service, same-day opening / no scheduled closing | rule: "read from the file's closing in scheduled status: where that closing was opened on a date later than the issue date of the latest Closing Disclosure …; where it was opened on or before the issue date …, or is of any other method, or the file has no closing in scheduled status, nothing is added"; compute guards `if service_method else False/-1`. Probes on task 0's file: same-day opening → 0.00, no scheduled closing → 0.00, both now stated by the rule. | closed (also closes O-13) |
| N-4 repull 0.00 charge vs tool contract | rule: "the borrower's share is zero and the charge is booked at 0.00"; tool Args.amount "a number of 0.00 or more … (0.00 records a pull whose cost the borrower does not bear)". CD tool lender_credit_amount likewise "an amount of 0.00 or more". | closed |

### Class re-check (revision 4)

- Mechanical: every compute_basis quote, every replaced_by, every prerequisite policy_source and every baseline.rule is verbatim in its own rule; every superseded_clause is verbatim in its base policy; base_policy_refs list every overwritten base policy.
- Scoped replacements, siblings: each replaced_by names its own case with "only for" and restates the base text for every other case verbatim (repull: base fee for non-repull pulls; cure: 10 percent bucket and post-consummation comparisons on the final CD with the base baseline; CoC baseline for every comparison other than the pre-consummation zero-tolerance cure; application fee: no record for zero-fee programs). The three cure replacements agree with each other (the "good-faith baseline" of the pre-consummation cure is the initial Loan Estimate in all three; the restated base baseline applies only outside it) and none reinstates, inside the cure's case, what another retires. The application-fee and repull replacements touch different base policies.
- Every compute branch has a rule tier and every tier a branch: repull 5 ladders, corrected CD 4 ladders + plain credit line, fee 5, revised LE 6, cure 5, CD 6 — swept; no gap found. Sign/floor: cure signed, floored once; fee floored once; lock credit positive; 0.00 amounts allowed exactly where the rules book them (repull, fee, CD credits), cure_amount stays positive (a non-positive adjusted increase books nothing).
- Docstrings: no tool names another tool or a call order.
- Factor bounds unchanged (repull 5 = 4p/1m; corrected CD 4 = 2p/2m; fee 5 = 4p/1m; revised LE 6 = 2p/4m; cure 5 = 2p/3m; CD 6 = 3p/3m); ladders pairwise distinct; no ladder dead at handling time.

### findings (revision 4, charter-global)

Closed: N-3, N-4, render R-1…R-8, O-8, O-13, the returning part of O-9.

Remaining observations (no RED demonstrated, no scored value in either task):
- O-9 (narrowed): `CFIELD` first match still decides "the closing on the file" for the CD's digital closing credit (no status filter, unlike the corrected CD's "closing in scheduled status"), "the rate lock on the file" and "the closing cost credit reserved against the file". On a file carrying a cancelled and a scheduled closing (as task 0's file does) the CD digital credit would read whichever row is stored first. Task 1's file has one closing, one lock and one credit, so its CD is unaffected; task 0 does not issue an initial CD.
- O-1, O-2, O-4, O-6, O-7, O-10, O-12 unchanged.
- B-1 (base, render R-9): `loan_condition_management` suspends on overdue prior-to-documents conditions while `loan_msr_overdue_conditions` counts every class; frozen blueprint, outside every task tree.

### closing_checklist (revision 4)

Written after both round-4 reveals.

- Task 0: PASS on all four relationships; task 1: PASS on all four. Every scored value re-derived blind on the round-4 charter equals GT (task 0: 60.76; 2 / borrower_requested_change / 2026-10-09 / 7,376.11. Task 1: 105.10; 3 / rate_lock_extension / 2026-10-13 / 2,703.00; 150.00 against 08362cf0…; 2026-10-16 / 2,525.10); no regression from round 3.
- Round-3 REDs N-3 and N-4 closed; render findings R-1…R-8 closed in the source (scoped replacements keep the base rules in force outside each policy's own case; the three cure replacements are mutually consistent; no sibling reinstates what another retires); R-9 is base known issue B-1.
- Scopes disjoint and complete; trees, edges, owner=user writes and factor bounds as in revision_3; gates all OK on the auditor's own run (TRACEABILITY 0 misses).
- No open charter RED. Open observations only: O-9 (narrowed — first-match selection of "the closing / rate lock / closing cost credit on the file" on multi-row files, unexercised by either world), O-1, O-2, O-4, O-6, O-7, O-10, O-12, and base B-1.
- The difficulty passes the source-layer audit.

task0=PASS  task1=PASS
charter=CLEAN

## revision_5

### entry gate (revision 5)

- `/tmp/erl0059_coord/gates.sh disclosures_conditions_and_application_fees --trace` (auditor's run, 2026-10-13): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 16 True True 0 32 32 True; 1.json 24 True True 0 31 31 True); SOLVABILITY OK (1.json True 4 6 16 True); COMPUTE OK (history_rows_max=10(>= 8), branches_max=97(>= 5)); GROUNDING OK; SCOPE OK; TRACEABILITY OK (0.json 20/0, 1.json 34/0). No red gate.
- `mkviews.py`: 0.view.json bcc78dd25f18e00338ba92540ded9d4f73e9173cc8811c7817d9d47340966c4d (unchanged); 1.view.json 611cf5d8577a0595c74b496745bfbc5e9915faefdfbf835b381f87c78607b45d (unchanged); task_tools.py ec0bb1f1f9dfdf113713bca75d6d90aa64b7c0ee039e3395890d8e70b278dc4e (unchanged); loan.extended.yaml 0015379b52ce624f0aa323885c2768c223a5b87910e409c7fec0db9297f87174 (changed). Read `render_loan_r2.md` as instructed (two items: first-match selection O-9; stale cross_category note; B-1 base).
- Freeze: written before either round-5 task file was opened. Base copy still verbatim; every compute_basis quote, replaced_by, policy_source and baseline.rule still verbatim in its own rule.

### Items verified

- Stale note: `loan_ext_application_fee_due.cross_category[funding].note` now "the returning-borrower discount is decided by the date of the most recent funding wire Larkspur sent on any closing of the customer" — **closed**. All other notes match their computes.
- O-9 / render r2-1, the reads the renderer named — **closed**: CD lock pricing credit "read from the file's rate lock in locked status" ↔ `CFIELD('lock', …, status='locked')` (lock charter: one pending/locked/expired lock per file); CD digital credit "read from the file's closing in scheduled status … or where the file has no closing in scheduled status, nothing" ↔ `status='scheduled'` (funding charter: one scheduled/docs_out/signed/in_rescission closing per file); CD closing-cost credit line now the customer's standing credit-ledger balance (award + guarantee payout − applied − reduced − forfeited) where any award is booked, else a reserved credit's fixed_credit_amount, else nothing — rule and compute agree; pre-approval read by the file's `preapproval_id` (unique); corrected-CD appraisal read from the file's standard order in delivered status (appraisal charter: one non-cancelled standard_order per file → unique).

### Whole-class sweep of the remaining single-row reads

Every `CFIELD`/`CPARAM` of the charter was listed and checked against the product charters' uniqueness rules. Three reads still select one row from a set the charters allow to hold several, and their rules name a single record:

**N-5 — SOURCE-POLICY RED (first-match selection left; moves no scored value of either task).**
- (a) Revised LE and cure: `standard_order = CFIELD('appraisal', 'appraisal_order_id', loan_file_id=HID, order_reason='standard_order')` — no status filter. The appraisal charter (appraisal_agg_orders_per_file) limits only standard orders "whose status is not cancelled" to one, so a file may carry a cancelled standard order and a live one. The rules read "the file's standard appraisal order (the order placed on the file with order reason standard_order)"; the base_fee of the fee sheet, the surcharge/visit lines and the rush line/rush re-baselining then follow whichever row is stored first (contrast the corrected CD, which filters `status='delivered'`).
- (b) Fee, revised LE and cure: `CFIELD('credit', 'status'|'heroes_occupation', variant_name='Larkspur Hometown Heroes Credit', loan_file_id=HID)` — no status filter. The credit charter (credit_agg_stacking) allows only one credit of a program "in reserved, verified or applied status" per file, so an expired/revoked/forfeited Hometown Heroes Credit can sit beside a verified one. Rule: "where the Hometown Heroes Credit reserved against the file is verified …". Probe on task 1's file with an expired Hometown Heroes row stored ahead of the verified one: compute heroes discount 0.00; the rule's reading (the verified credit) 50.00.
- (c) CD closing-cost credit tier 2: `CFIELD('credit', 'status', loan_file_id=HID, status='reserved')` / `CPARAM(... 'fixed_credit_amount' ..., status='reserved')`. Two stackable programs may both be reserved on one file; the rule's "a closing cost credit against the file is in reserved status, that credit program's fixed_credit_amount is added" does not say whether one or both are added; compute adds the first stored.
- Classification note: in round 4 I carried this class as observation O-9 and wrote charter=CLEAN. Under the same standard I applied to N-2/N-3 (a charter-legal world in which rule and compute give two different numbers, demonstrated by probe), the class is a SOURCE-POLICY RED; (b) is demonstrated by probe here, (a) and (c) by the quoted charter rules. Neither task's world holds two such rows (task 1: one appraisal order, one Hometown Heroes Credit, no reserved credit; task 0 computes none of these reads), so no scored value moves.

Other observations unchanged: O-1, O-2, O-4, O-6, O-7, O-10, O-12; base B-1 (BLUEPRINT-KNOWN). New observation O-14: the CD closing-cost credit line now sums the customer's credit ledger across all files (rule says "the customer's closing cost credits"); rule and compute agree; a credit standing on another open file would count on this CD — unusual but stated.

### closing_checklist (revision 5)

- Task 0 and task 1 PASS on all four relationships; every scored value re-derived blind on the round-5 charter equals GT; no regression.
- Closed this round: the stale funding note; the O-9 reads the renderer named (lock, closing, closing-cost credit balance, pre-approval, corrected-CD appraisal).
- Open: N-5 (a) revised-LE/cure standard appraisal order read without a status filter, (b) Hometown Heroes Credit read without a status filter in fee / revised LE / cure (probe: 0.00 vs 50.00), (c) CD reserved-credit estimate with two reserved programs — charter-global SOURCE-POLICY RED, no scored value of either task moved. Base B-1 BLUEPRINT-KNOWN.

task0=PASS  task1=PASS
charter=N-5

## revision_6

### entry gate (revision 6)

- `/tmp/erl0059_coord/gates.sh disclosures_conditions_and_application_fees --trace` (auditor's run): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 16 True True 0 32 32 True; 1.json 24 True True 0 31 31 True); SOLVABILITY OK; COMPUTE OK (history_rows_max=10(>= 8), branches_max=115(>= 5)); GROUNDING OK; SCOPE OK; TRACEABILITY OK (0.json 20/0, 1.json 34/0). No red gate.
- `mkviews.py`: 0.view.json bcc78dd25f18e00338ba92540ded9d4f73e9173cc8811c7817d9d47340966c4d; 1.view.json 611cf5d8577a0595c74b496745bfbc5e9915faefdfbf835b381f87c78607b45d; task_tools.py ec0bb1f1f9dfdf113713bca75d6d90aa64b7c0ee039e3395890d8e70b278dc4e (all unchanged); loan.extended.yaml 7392c07c8582e545185c5cb8b7b14a3281dc30956dbd616cd954f9339543a3db (changed).
- Freeze: written before either round-6 task file was opened. Base copy verbatim; every compute_basis quote, replaced_by, policy_source and baseline.rule verbatim in its own rule.

### N-5 re-check

- (a) revised LE / cure standard order: compute now takes the standard_order row in any non-cancelled status (delivered, under_reconsideration, completed, inspected, on_hold, assigned, ordered); rule "the order placed on the file with order reason standard_order that is not cancelled; a file carries at most one such order" — matches appraisal_agg_orders_per_file. **Closed** for files that have such an order (see N-6a for files that do not).
- (b) Hometown Heroes reads filtered `status='verified'` in fee, revised LE and cure; rule "the Larkspur Hometown Heroes Credit reserved against the file is verified"; one credit of a program in reserved/verified/applied status per file → unique. **Closed.**
- (c) CD reserved estimate: sum over every program of `fixed_credit_amount` for the file's reserved credit of that program; rule "the fixed_credit_amount of every program reserved against the file (one credit per program) is added up as an estimate, a percentage or guarantee program counting 0.00". **Closed.**

### Whole-charter sweep (every read and every branch, reported in one round)

Every binding of all six computes was listed and each single-row or latest/max read checked against the product charters' uniqueness rules and the rule wording:
- Unique by charter or by the rule's own ordering: latest CD / latest LE "the one with the highest disclosure sequence" (`MAX(disclosure_sequence)` then that row); initial LE (one loan_le_issued per file); title "most recent document date among the cleared title commitment conditions" and VOE "most recent resolved date among the cleared verbal verification of employment conditions" (the max date itself, row-independent); lock "in locked status" (one pending/locked/expired lock per file); closing "in scheduled status" (one scheduled/docs_out/signed/in_rescission closing per file); delivered standard appraisal order (one non-cancelled standard order per file); pre-approval by `preapproval_id`; Hometown Heroes verified; reserved credits per program; funding wire `XLATEST` (max date); customer-wide XSUM/XCOUNT on lock pricing and credit ledger (rules say "any rate lock of the customer" / "the customer's closing cost credits"). No read left where rule and compute select different records.
- Branch coverage: every compute branch has a rule tier, except the three cases below where the compute has **no definite value** and the rule states no tier.

**N-6 — SOURCE-POLICY RED (cases with no rule tier and no compute value; moves no scored value of either task).**
- (a) Revised LE fee sheet on a file whose live primary appraisal is not a standard order. The appraisal charter allows the one non-cancelled primary order to have order_reason `transferred_in` or `new_order_after_expiration` (appraisal_agg_orders_per_file). The rule prices "the base_fee of the report type of the file's standard appraisal order (… not cancelled …)" and reads surcharge/rush charges from that order; with none, the rule gives no fee-sheet appraisal amount and `CPARAM('appraisal','base_fee', appraisal_order_id=None)` makes the fee sheet `float + None`. Probe on task 1's file with the order's reason set to transferred_in: no number (TypeError).
- (b) Corrected CD employment re-verification line on a file whose verbal VOE condition is not yet cleared. Base loan_condition_management makes the VVOE condition prior-to-funding and loan_clear_to_close lets prior-to-funding conditions stay open at clear-to-close, so a file with a Closing Disclosure and an open VVOE is charter-legal. The rule measures "from the most recent resolved date among the cleared verbal verification of employment conditions"; with none, no tier applies and `DAYS(None, …)` gives no number. Probe on task 0's file with the cleared VVOE row removed: no number (ValueError).
- (c) Corrected CD title line on a file with no cleared title commitment condition (the condition waived — base allows waiver — or never issued): same shape; probe on task 0's file without the cleared title row: no number (ValueError).
- These reads date from round 1; I did not test the empty case in earlier rounds. Neither task's world is in these cases (task 0: one cleared VVOE, one cleared title commitment; task 1: one delivered standard order).

Observations (no RED): O-14 widened — the CD closing-cost credit line's tier 1 keys on award entries on any of the customer's credits, so an award fully applied on an earlier file (standing balance 0.00) displaces the reserved-credit estimate for this file; rule and compute agree. O-15 — the corrected CD appraisal line and the cure's rush re-baselining read only the standard order, so a transferred-in or replacement appraisal is ignored (rule and compute agree). O-1, O-2, O-4, O-6, O-7, O-10, O-12, base B-1 unchanged.

### closing_checklist (revision 6)

- Tasks 0 and 1 PASS on all four relationships; every scored value re-derived blind equals GT; no regression.
- N-5 (a)(b)(c) closed; the whole-charter sweep finds no remaining read where rule and compute can select different records.
- Open: N-6 (a) revised-LE fee sheet on a file whose live appraisal is transferred_in / new_order_after_expiration, (b) corrected-CD VOE line with no cleared VVOE condition yet, (c) corrected-CD title line with no cleared title commitment condition — each a charter-legal case where the rule states no tier and the compute yields no number. No scored value of either task moved. Base B-1 BLUEPRINT-KNOWN.

task0=PASS  task1=PASS
charter=N-6

## revision_7

### entry gate (revision 7)

- `/tmp/erl0059_coord/gates.sh disclosures_conditions_and_application_fees --trace` (auditor's run): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 16 True True 0 32 32 True; 1.json 24 True True 0 31 31 True); SOLVABILITY OK; COMPUTE OK (history_rows_max=10(>= 8), branches_max=146(>= 5)); GROUNDING OK; SCOPE OK; TRACEABILITY OK (0.json 20/0, 1.json 34/0). No red gate.
- `mkviews.py`: 0.view.json bcc78dd25f18e00338ba92540ded9d4f73e9173cc8811c7817d9d47340966c4d; 1.view.json 611cf5d8577a0595c74b496745bfbc5e9915faefdfbf835b381f87c78607b45d; task_tools.py ec0bb1f1f9dfdf113713bca75d6d90aa64b7c0ee039e3395890d8e70b278dc4e (all unchanged); loan.extended.yaml 9516b83c18e2510fb0785052343ad3b5bc9fb62b355f9f0c435efe7695fce026 (changed).
- Freeze: written before either round-7 task file was opened. Base copy verbatim; every compute_basis quote, replaced_by, policy_source and baseline.rule verbatim in its own rule.

### N-6 re-check

- (a) Revised LE / cure: the order read is now "the file's live primary appraisal order (… standard_order, transferred_in or new_order_after_expiration that is not cancelled; a file carries at most one such order)", with "or nothing for the appraisal where the file has no live primary appraisal order" in the fee sheet and "or the file has no live primary appraisal order, nothing is added/taken out" in the surcharge, rush and rush re-baselining tiers; compute tries the three reasons × seven non-cancelled statuses and guards `if standard_order else 0.0`. Unique by appraisal_agg_orders_per_file. **Closed** (also closes O-15 for these lines).
- (b) Corrected-CD VOE: "or a file with no cleared verbal verification of employment condition yet, adds nothing" ↔ `voe_age = … if voe_resolved_date … else -1` → 0. **Closed.**
- (c) Corrected-CD title: "or a file with no cleared title commitment condition, adds nothing" ↔ same guard. **Closed.** Corrected-CD appraisal now reads the delivered primary order of any of the three reasons, "or a file with no primary appraisal order in delivered status, adds nothing" (closes O-15 there).

### Whole-charter edge sweep (absent records, None, zero division, date differences)

- Automated: each of the six computes was evaluated on both worlds (task 0 after its repull row; task 1 opening) with, in turn, every non-holding table emptied, all of them emptied together, every event_type/status/condition_code subset of loan_conditions, loan_disclosures, loan_fee_ledger, closings, appraisal_orders and closing_credits removed, and the loan file's borrower_count = 0, estimated_closing_date = "", preapproval_id = None and base_loan_amount = 0. 0 exceptions (no TypeError/ValueError/ZeroDivision) across all cases.
- Rule coverage of every guard: repull delivery "or the file has no scheduled closing date on or after the pull date, no delivery fee" ↔ `0.0 if days_to_closing < 0` (absent date → −1); CD short-notice "or the file has no scheduled closing date on or after that day, nothing" ↔ same; corrected-CD appraisal/title/VOE absent-record clauses ↔ −1 sentinels; revised-LE/cure live-primary-order clauses ↔ `if standard_order else 0.0`; closing service "or the file has no closing in scheduled status" ↔ guard; lock "no rate lock in locked status" → initial-LE credit; pre-approval absent → full fee / no relief / no add-back (rule "otherwise"); no funding wire → nothing; no award and no reserved credit → nothing. Same-day/negative date differences: title/VOE/appraisal ages ≤ thresholds fall to "adds nothing" (rule tiers are "no more than …"); closing date equal to the pull/preparation day → 0 days → rush / short-notice tier, as the rule's "… or fewer calendar days" states. Divisions are only by the constants 100 and 1000.
- Unreachable sentinels (no rule tier needed): prior CD figure `or 0.0` (the corrected CD's trigger requires a CD on the file); latest/initial LE totals and initial-LE credit `or 0.0` (a revised LE / cure / CD presuppose the initial LE); corrected-CD lines with no scheduled closing date (the trigger is a moved closing date).
- No read left where rule and compute select different records (re-checked from revision_6; the new reads are unique by appraisal_agg_orders_per_file).

### findings (revision 7)

N-6 (a)(b)(c) closed. No new RED. Observations: O-16 — the fee sheet and corrected-CD new-appraisal tier price a transferred-in report at its report type's base_fee, while appraisal_fee_schedule charges transferred orders transfer_review_fee; rule and compute agree, no task affected. O-14 (widened), O-1, O-2, O-4, O-6, O-7, O-10, O-12, base B-1 unchanged.

### closing_checklist (revision 7)

- Tasks 0 and 1 PASS on all four relationships; every scored value re-derived blind equals GT; no regression.
- N-6 (a)(b)(c) closed; the edge sweep (absent records, None, zero division, date differences) finds no compute exception and no guard without a rule tier; no read where rule and compute select different records.
- No open charter RED. Observations only (O-1, O-2, O-4, O-6, O-7, O-10, O-12, O-14, O-16) and base B-1 (BLUEPRINT-KNOWN).
- The difficulty passes the source-layer audit.

task0=PASS  task1=PASS
charter=CLEAN

## revision_8

### entry gate (revision 8)

- `/tmp/erl0059_coord/gates.sh disclosures_conditions_and_application_fees --trace` (auditor's run): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 16 True True 0 32 32 True; 1.json 24 True True 0 31 31 True); SOLVABILITY OK; COMPUTE OK (history_rows_max=10(>= 8), branches_max=152(>= 5)); GROUNDING OK; SCOPE OK; TRACEABILITY OK (0.json 20/0, 1.json 34/0). No red gate.
- `mkviews.py`: 0.view.json bcc78dd25f18e00338ba92540ded9d4f73e9173cc8811c7817d9d47340966c4d; 1.view.json 611cf5d8577a0595c74b496745bfbc5e9915faefdfbf835b381f87c78607b45d; task_tools.py ec0bb1f1f9dfdf113713bca75d6d90aa64b7c0ee039e3395890d8e70b278dc4e (all unchanged); loan.extended.yaml f719a9995cb32dddf9bd6c107969ea05d93c07aee2f5ce7a329583b241c1d8ea (changed).
- Read as instructed: `render_loan_r3.md` (2 source items + B-1) and `kb_audit_notes_r1.md` (6 notes; KB verdict task0=PASS task1=PASS).
- Freeze: written before either round-8 task file was opened. Base copy verbatim; every compute_basis quote, replaced_by, policy_source and baseline.rule verbatim in its own rule.

### Items verified

| item | round-8 source | verdict |
|---|---|---|
| R3-1 corrected CD, no scheduled closing date | appraisal "… or a file with no primary appraisal order in delivered status or no scheduled closing date, adds nothing"; title "… or no scheduled closing date, adds nothing"; VOE "… or no scheduled closing date, adds nothing"; closing service "… or the file carries no Closing Disclosure, or a Mobile Notary Closing has no scheduled closing date, nothing is added" — each matches its −1 / False guard (RON needs no date: "signing on any day") | closed |
| R3-2 bindings under no factor | `delivered_order` now in appraisal_recertification; cure `standard_order` in rush_rebaseline; revised-LE `standard_order` stays a baseline binding read by the fee sheet's base_fee (stated in baseline.rule) and by the surcharge/rush factors. Remaining unfactored bindings in every policy are baseline bindings named by its baseline.rule (latest CD sequence/figure + credit report line; fee sheet; latest/initial LE totals and measured increase; fee credit + initial-LE credit) | closed |
| KB-6 waived lock costs | revised-LE lock line and cure extension re-baselining: "their dollar cost, less any lock cost waivers Larkspur booked on the customer's locks in that period and never below zero" (same for relock fees) ↔ `MX(0.0, extension_cost - waived_lock_cost)` with `waived_lock_cost = XSUM(... event_type='lock_cost_waived', within the window)`; schema: cost_amount positive. Probe on task 1's file with a 368.00 waiver of `2aae0f4d…` on 2026-10-14: line 0.00, as the rule says | closed |
| KB-2 partly Larkspur-borne extension | rule tests "borrower-borne lock extension entries" = cost_bearer borrower; lock charter books any extension with charged days as cost_bearer borrower — consistent, single reading | observation (no change needed) |
| KB-3 notice counted from preparation day | rule wording explicit ("the day the Closing Disclosure is prepared") | observation |
| KB-4 Hometown Heroes "verified occupation" | rule reads the credit record's verified occupation, not the caller's statement; task 1's verified occupation (nurse) agrees with the caller | observation |
| KB-5 / B-1 | cross-product wording; blueprint-known | observations |

### Sweep of the changed policies

- Corrected CD, revised LE, cure: every compute branch has a rule tier (including the new no-date and waiver clauses), no read selects a record differently from the rule, signs/floors as stated (new floor "never below zero" ↔ `MX(0.0, …)`), factor bounds unchanged (4 = 2p/2m; 6 = 2p/4m; 5 = 2p/3m), ladders distinct and live.
- Absent-record fuzz re-run on both worlds (every non-holding table emptied singly and together, × estimated_closing_date "" and preapproval_id None): 0 exceptions across all six computes.

### findings (revision 8)

All reported items closed; no new RED. New observation O-17: the waiver deduction subtracts every lock_cost_waived entry booked on the customer's locks in the window, whatever entry it offsets (an extension, a relock or a float-down fee); rule and compute agree, no task world carries a waiver. Earlier observations and base B-1 unchanged.

### closing_checklist (revision 8)

- Tasks 0 and 1 PASS on all four relationships; every scored value re-derived blind equals GT; no regression.
- render_loan_r3 items 1–2 and KB note 6 closed in the source; KB notes 2–5 are observations needing no source change; B-1 BLUEPRINT-KNOWN. No open charter RED; observations O-1, O-2, O-4, O-6, O-7, O-10, O-12, O-14, O-16, O-17.
- The difficulty passes the source-layer audit.

task0=PASS  task1=PASS
charter=CLEAN
