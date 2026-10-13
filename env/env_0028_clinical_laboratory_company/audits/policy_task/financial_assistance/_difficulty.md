# Policy-task audit — financial_assistance / charter-global

## charter_global_frozen

- Auditor: Claude (erl-task-policy-audit), independent of the instantiating agent; unattended run.
- Freeze time: 2026-10-04T16:50Z (wall clock). Written before any task's GT was revealed; nothing below is derived from `evaluation_criteria`, `computations`, `prerequisite_closure`, `charter_scope`, `solvability_contract`, `design_rationale` or `required_documents` of any task.
- Freeze hashes (sha256, recomputed by the auditor, identical to `audits/_views/policy_task/financial_assistance/HASHES.txt`):
  - `tasks/financial_assistance/assistance.extended.yaml` 1e06045ef4dc7a08e25a94b865358acc69a8c4b555c4f393b3cda5c85fc63961
  - `tasks/financial_assistance/task_tools.py` 4260086cf5991a2493eafabdd61206eb824863e512b4be6b8d25e9fed60382e9
  - `task0.view.json` 3a695b812788214b156021a109e8b7316e7cfcdd08da99126ad777ce0541841b, `task1.view.json` 9aee0b1b5fe829c21433648f2dc78ce45946f63654a0a4376668895f8703ae01
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/assistance.yaml`, the cross-category product files (`coverage/invoices/orders/plans/visits.yaml`, only their `binding` block, to evaluate cross reads), `assistance.extended.yaml`, `task_tools.py`, the two masked views, `erlbench`-side DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`/`eval_compute`, used read-only as an evaluator).
- Masked / not read: `tasks/financial_assistance/tasks/*.json`, the scenario `worklog.md`, any instantiate notes. No recursive search touched `tasks/` or the scenario root.
- Entry conditions (Step 0): gate snapshot supplied in the brief (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; traceability deferred pending KB). Masked views and hashes supplied. Entry conditions met.

### policy_conflict_scan

Base section: lines 1–853 of the extended file are byte-identical to `blueprint/products/assistance.yaml` (diff shows only one trailing blank line). Five extended policies:

| id | subject | computes | target_tool (owner) | prerequisite |
| --- | --- | --- | --- | --- |
| assistance_ext_award_discount | assistance_discount_applied | discount_amount | apply_award_discount_6c746b08 (agent) | [] |
| assistance_ext_renewal_tier | assistance_application_submitted | variant_name | submit_renewal_application_d691b1b8 (user) | award_discount (state, value_input, window_relief) |
| assistance_ext_countable_percent | assistance_tier_redetermined | fpl_percent | reassess_assistance_percent_a70c4477 (agent) | [] |
| assistance_ext_document_period | assistance_documents_requested | response_days | request_assistance_documents_a6db5abf (agent) | countable_percent (action, value_input, agency_days) |
| assistance_ext_document_extension | assistance_documents_extended | extension_days | request_document_extension_ca0bff0a (user) | document_period (state, value_input, days_left) |

- Overlapping subjects: none — each event type is claimed by one extended policy. `assistance_ext_countable_percent` and `assistance_ext_renewal_tier` both override sentences of `assistance_tier_determination`, but different sentences (FPL formula + redetermination sentence vs. best-tier + catastrophic sentences) and on different events (redetermination of a submitted case vs. a renewal application); no sentence is overridden twice, no clash.
- `assistance_ext_document_period` and `assistance_ext_document_extension` both override `assistance_evt_documentation`, on disjoint sentences (due-date + document-period counting vs. the extension sentence). The two replacements are mutually consistent: the extension writes the new due date onto the case and the document-period replacement counts the period "through the documents due date the case records, including any extension granted".
- Triggers/time anchors: award_discount and countable_percent and document_period are `state_due`, renewal and extension `on_request`; all are evaluated at the frozen clock (`NOW` = frozen date); no policy needs a future date.
- Terminal states: each tool writes only `assistance_cases` / `assistance_events` of this category. Cross-category reads (coverage, invoices, orders, plans, visits) are reads only.
- Scope partition: the prerequisite graph has exactly two connected components — {award_discount ← renewal_tier} and {countable_percent ← document_period ← document_extension}. With M=2 the natural, mutually exclusive and jointly complete partition is one component per task (to be confirmed against `charter_scope` after the reveal, in each task file).

### rule_compute_equivalence

Mechanical sweep: every `compute_basis` quotation is verbatim in its own policy's `rule` (5/5 policies, 0 misses), every compute binding has a basis, every `baseline.rule` sentence is verbatim in the `rule`, every ladder tier is a branch of its `decides` binding and vice versa. Sentence-level reading, per policy:

- award_discount: eligible / balance_due / working_amount / points / cap / owed share / limit all match the rule. `balance_due` enumerates five non-FA adjustment types; `db_schema.invoice_transactions.adjustment_type` has exactly six values (the sixth is `financial_assistance`), so "every adjustment ... other than a financial-assistance discount" is implemented completely. Imprecision (observation O-1): the individual-plan tier tests `employer_group_size_band == 'not_employer_plan'`, which the schema defines as "individual and government plans", whereas the rule says "a plan bought individually rather than through an employer group"; a government plan would get the individual-plan points under compute. No task world in this difficulty holds an active government plan on the discounted invoice, so no consequence is demonstrable here.
- renewal_tier: matches. Latent defect (observation O-2): `burden_months` evaluates `ended_on >= F('application_date')` where `ended_on` is `CFIELD(... status='terminated')`; for a household with no terminated coverage this compares `None` with a string (evaluation error), and with two terminated coverages CFIELD takes an arbitrary first row while the rule says "a coverage that ended on or after". Neither arises in a task world here.
- countable_percent: matches. Observation O-3: `disregard` tests only the latest-received unemployment statement (`LATEST ... document_date`) while the rule admits "an unemployment benefit statement received whose date is no more than the benefit-recency days"; differs only when the latest-received statement is stale and an earlier one is not.
- document_period: matches; `request_weekday` uses 2024-01-01 (a Monday) so 4 = Friday, 5 = Saturday, 6 = Sunday, as the rule requires. `latest_return` takes the latest-received return rather than the latest tax year (observation O-4, no world consequence).
- document_extension: matches. Observation O-5: `business_span` adds 2 days whenever `due_weekday + rem > 4`, which also fires when the current due date is itself a Saturday/Sunday and `rem = 0`, where the rule ("when those remaining days run past a Friday") would add nothing; no task world has a weekend due date.

Layering (observation O-6, charter-wide): each rule states its baseline sentence unconditionally and then a factor sentence that refines it ("The recognition rate is the insured rate." / "The recognition rate depends on ..."; "The award discount is never more than the invoice's balance still due" / "an invoice on which a payment was posted on its date of service ... is limited only to its working amount, the deposit beyond the owed share becoming a credit"; same for burden window, catastrophic share, response days, extension days). This layering is what the framework requires (baseline sentences in the rule, factor fall-through = baseline). The later sentence states itself as the dependency of the same quantity and, in the limit case, explicitly names the resulting credit, so the specific sentence governs and a single reading results. The strongest instance (the word "never") is examined against task 0's world in `task0.md`.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: five policies, five distinct tools, each tool named by exactly one policy. Subjects and terminal states admit one reading each.
- Tool bodies: no tool raises, refuses, errors or hints on an unmet prerequisite (`apply_award_discount` books whatever it is given; `submit_renewal_application` creates a submitted case; `reassess_assistance_percent` overwrites percent+tier; `request_assistance_documents` sets status/requested/due; `request_document_extension` falls back to today when no due date exists and still succeeds). The tool layer judges no prerequisite.
- Docstrings: no docstring names another write tool or states a position in a sequence. "After success ..." and "after today"/"after this line" describe the call's own effect; references to "the assistance-case lookup", "the invoice lookup", "the profile lookup" are provenance notes for id arguments pointing at share read tools, not ordering (observation O-7, wording only). `request_document_extension` says "on their pending financial-assistance application", a descriptive state word, not a check.
- uuid8s: 6c746b08, d691b1b8, a70c4477, a6db5abf, ca0bff0a — five distinct values, no shared prefix beyond one hex digit (a70c…/a6db…), no sequence or adjacency pattern; consistent with independent generation.
- Declared event triggers not executed by the tools (observation O-8): base event `assistance_discount_applied` declares a trigger `invoices:invoices_adjustment_posted`, and `assistance_application_submitted` declares `invoices:invoices_hold_placed`; the hidden tools post neither ("it does not post anything else"). No policy of this difficulty reads an `adjustment_type='financial_assistance'` line or an assistance-review hold created in-episode, so no scored value can move; recorded as an observation on terminal-state completeness.

### prerequisite_graph

- `prerequisite` filled in on all five policies (`[]` on award_discount and countable_percent).
- Edges: renewal_tier → award_discount; document_period → countable_percent; document_extension → document_period. Every `problem` is an extended policy id of this file, none is a base policy or self. Acyclic (two chains).
- `policy_source` of each edge is verbatim in the blocked policy's own `rule` (mechanically checked, 3/3).
- `form`: two `state`, one `action`; `fallback_reason` present exactly on the action edge.
- `resolved_by` equals the depended-on policy's `target_tool` on all three edges; `kind: value_input` on all three, and each `gate` is a real binding of the blocked policy's compute (`window_relief`, `agency_days`, `days_left`) that the resolving write moves (discount line enters `window_relief`; reassessed `fpl_percent` enters `recorded_pct` → `agency_days`; documents due date enters `due` → `days_left`/`due_weekday`).
- `condition` vs. sentence: renewal edge condition ("date of service in the approved award's window, no undecided appeal, final patient responsibility posted, has a discount line under that award") matches the sentence's "every invoice the award being renewed covers whose payer decision is final carries that award's discount line"; extension edge condition is the sentence's state verbatim in substance; document_period edge condition ("recorded percent equals the countable percent ... at the time the request is issued") is the handling-time content of "reassessed on the household's countable income". None strengthened or weakened.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "current world") in any `prerequisite` block.

### prerequisite_sentences

1. renewal_tier ← award_discount (state). "The tier a renewal application is assessed at is set only after every invoice the award being renewed covers whose payer decision is final carries that award's discount line." Connective "only after"; waited-on state = an invoice carrying the award's discount line (record-visible: an `assistance_events` row `assistance_discount_applied` with that `invoice_id` under the case); no tool, id or snake_case token. Exactly one write of this difficulty creates such a line (`apply_award_discount_6c746b08`). Derivation: sentence → find covered, payer-final invoices lacking a line under the award → the policy whose rule fixes "the award discount on that invoice" is award_discount → its rule computes the amount. Single reading.
2. document_period ← countable_percent (action, fallback). "The response period of a documents request is fixed only after the case's percent of the poverty guideline has been reassessed on the household's countable income." Connective "only after"; names the action in business words ("reassessed on the household's countable income"), which is exactly countable_percent's own subject. Fallback test: the reassessment write changes only `fpl_percent` and `variant_name` on the case — no event row, no date stamp, no flag — so no record-visible state distinguishes a reassessed percent from an intake percent; the fallback is justified.
3. document_extension ← document_period (state). "The extended due date is not fixed until the case carries a documents-requested date and a documents due date." Connective "not ... until"; state = the case's `documents_requested_date` and `documents_due_date` populated. Only `request_assistance_documents_a6db5abf` writes `documents_requested_date` (the extension tool writes the due date only, and is the blocked write itself). Single reading: sentence → the policy whose rule sets a due date on a documents request = document_period.

Restatement on the depended-on side (observation O-9, check 6): countable_percent's own rule opens "Before a documents request is issued on a submitted application, the case's percent of the poverty guideline is reassessed as the countable percent and recorded together with the income tier that percent falls in, whether or not the tier changes." This states the same order as edge 2 from the depended-on policy's side (it is also that policy's trigger and the `replaced_by` text of its overwrite). It grounds no additional edge and points in the same direction as the declared edge, so the two passages reach the same conclusion in every situation — no second answer is demonstrable, hence an observation, not a red light. No other rule states a cross-problem order; no rule names another problem's tool or id. Base rule sentences with order words ("When every required document is in, the case goes to review", "An application can be withdrawn only by the applicant") ground no edge of any tree.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (the scored quantity is the criterion):

- award_discount vs `assistance_evt_discount_application`: followed — approved-case gate, invoice-status gate, own-customer / eligible billing class / DOS in award window / no claim awaiting decision or under appeal, insured-balances sentence, consumer/collection-fee exclusions, once-per-invoice, payment-plan sentence, credit-refund sentence, collections recall, prompt-pay stacking (concerns a prompt-pay discount taken on the remainder after the award, a different situation from the extended limit tier that withdraws a prompt-pay discount already taken), hardship sentence (not the income/presumptive path). Handled differently: "For an income or presumptive tier the discount is discount_pct percent ... limited to the balance still due" — declared in `overwrite` verbatim and replaced; the extended percent, cap, working amount and limit all replace this one sentence. Declared; merged semantics unique.
- renewal_tier vs `assistance_agg_multi_holding` (followed), `assistance_agg_single_open_case` (followed: renewal window 30 days before award end; awards cap and reapplication wait untouched), `assistance_tier_determination` (two sentences declared and replaced: best-tier selection; catastrophic applicability; the income-band, presumptive and household sentences are followed — the renewal reads the award's documented income/percent), `assistance_evt_award_term_and_review_holds` (channel sentence declared and replaced by the portal-only renewal sentence; holds sentence followed). Observation O-10: the base sentence "annual household income ... taken from the most recent accepted income document" is not overridden while both extended policies that read income read the figure recorded on the case; no record carries document amounts, so no competing number is computable on any world here.
- countable_percent vs `assistance_tier_determination`: FPL formula sentence and redetermination sentence declared and replaced. Income-band sentence followed (tier recorded = band of the countable percent).
- document_period vs `assistance_evt_documentation`: due-date sentence and document-period counting sentence declared and replaced; accepted-document, Medicaid-screening, extension, review and denial sentences followed.
- document_extension vs `assistance_evt_documentation`: extension sentence declared and replaced; maximum extensions kept.
- Disguised forms: no anonymous intermediate (every deviation sits inside a declared replaced sentence), no 0/1 multiplier, no dropped base branch on the policies' own subjects, no author note calling base output "wrong".

Conclusion: no undeclared override.

### factor_ladders

| policy | factor | label | tiers | multi-source (all non-fall-through tiers compound over distinct records) | cross_difficulty | notes |
| --- | --- | --- | --- | --- | --- | --- |
| award_discount | coverage_points | parameter | 10 / 5 / 0 | no (tier 1 single) | coverage | honest |
| | responsibility_points | parameter | 10 / 5 / 0 | no (tier 2 single) | coverage | honest |
| | late_finalization_points | parameter | 5 / 3 / 0 | no | — | honest |
| | service_class_cap | parameter | 300 / 600 / none | no | orders | honest |
| | working_amount_basis | method | 3 formulas | no (tier 1 single) | — | honest (different subtraction sets) |
| | discount_limit_rule | method | 3 formulas | no (tier 1 single) | — | honest |
| renewal_tier | catastrophic_share | parameter | 12.5 / 7.5 / 10 | yes (case percent AND coverage status) | coverage | honest |
| | burden_window | method | months from coverage end +1 / award months / 12 | partly | coverage | label defensible (two tiers derive the window from different records); O-11 |
| | amount_in_question | parameter | posted resp. of reprocessing invoice / dispute invoice balance / 0 | no | — | O-11 |
| | plan_carried_balances | parameter | − installments paid / + returned fees / 0 | no | plans | O-11 |
| countable_percent | deduction_window | method | months from coverage end +1 / 18 / 12 | no | coverage | label defensible (tier 1 procedural); O-11 |
| | recognition_rate | parameter | 100 / 75 / 50 | yes (coverage status AND order test-charge count) | orders | honest |
| | payment_kinds | method | 3 formulas | no | — | honest |
| | plan_installments | parameter | all / 50 % / 0 | no | plans | honest |
| | collection_fees | parameter | all fees / trip+add.+weekend / 0 | no | visits | O-11 |
| | benefit_disregard | parameter | 1000 / 500 / 0 | no | — | honest |
| document_period | agency_allowance | parameter | 15 / 5 / 0 | partly | coverage | honest |
| | tax_return_allowance | parameter | 12 / 10 / 0 | no | — | honest |
| | household_earner_allowance | parameter | 10 / 7 / 0 | partly | — | honest |
| | file_credit | parameter | 3 / 1 / 0 | no | — | honest |
| | **response_start** | **method** | **3 / 1 / 0 days added** | no | — | **mislabelled — F-1** |
| | weekend_move | parameter | 2 / 1 / 0 | no | — | honest |
| document_extension | stay_allowance | parameter | 7 / 4 / 0 | no | visits | honest |
| | time_left_credit | parameter | 5 / 2 / 0 | no | — | honest |
| | household_letter_allowance | parameter | 3 / 2 / 0 | no | — | honest |
| | coverage_loss_allowance | parameter | 3 / 1 / 0 | no | coverage | honest |
| | pending_coverage_allowance | parameter | 5 / 2 / 0 | no | coverage | honest |
| | counting_convention | method | business+3 / business / calendar | no (tier 1 single) | — | honest |

- Every factor: `decides` is an input binding (never `result`); binding sets disjoint within each policy; every ladder has three pairwise-disjoint tiers, fall-through = the factor's `baseline`, every tier stated in the `rule` (condition and value/method) and implemented in `compute`; no two tiers of a ladder select the same value or method; every tier value is drawn from the policy's params.
- Business realism: no tier condition holds of every customer reaching its write (e.g. "no active coverage" can hold or fail at a discount write after a coverage ends; "documented above 300 %" fails for 50 %/75 %/Full renewals), and every fall-through is the ordinary standard treatment (no straw-man default). Values are within what a clinical-laboratory charity-care program plausibly publishes (price caps on genetic/esoteric tests, HSA/FSA exclusion, mailbox rule, weekend roll-forward, Medicaid-screening allowance).
- Counts (labels as declared): award_discount 6 (4P/2M), renewal_tier 4 (3P/1M), countable_percent 6 (4P/2M), document_period 6 (5P/1M), document_extension 6 (5P/1M). Counting only honest labels: document_period has 6P/**0M** (F-1).
- Multi-source factors exist in the renewal component (catastrophic_share) and the documents component (recognition_rate). Cross-difficulty factors exist in both components (coverage, orders, plans, visits); whether their rows are seeded is per task.
- O-11 (label borderline, no red light): burden_window / deduction_window decide a window length but two (resp. one) of their tiers derive it from different records (coverage end date, the award's own term), which is a different procedure, not a different constant; amount_in_question / plan_carried_balances / collection_fees select which record-derived amount enters a fixed slot of the formula. The labels are defensible either way and no count bound flips for renewal_tier or countable_percent under the reading adopted here.

### findings

- **F-1 — SOURCE-FACTOR RED (charter-global structure; bears on the task whose tree contains `assistance_ext_document_period`).**
  - Symptom: `assistance_ext_document_period` declares exactly one `method` factor, `response_start`, and its tiers only add a constant number of days.
  - Root cause: the factor is labelled `method` although every tier selects a number from the params and adds it to the same sum.
  - Evidence: ladder `response_start` (lines 1840–1854) tiers "count from the following Monday" / "count from the next day" / "count from the request date"; rule: "counts from the following Monday **by adding the Friday start days**; such a mailed request issued on any other day counts from the next day **by adding the mail start days**"; compute `start_days: "(K('friday_start_days') if request_weekday == 4 else K('mail_start_days')) if (...) else 0"` and `counted_days: "P('documents_due_days') + agency_days + tax_days + earner_days - file_credit + start_days"` — structurally identical to `agency_days`/`tax_days`/`earner_days`, all labelled `parameter`; params `friday_start_days: 3`, `mail_start_days: 1`.
  - Demonstrated consequence: the tiers substitute 3 / 1 / 0 into the same formula ("a factor labelled method whose tiers only substitute a different number into the same formula"); with the label corrected the computation has 6 parameter factors and 0 method factors, below the bound of at least 1 `method` per computation.
  - Affected: `assistance.extended.yaml` → `assistance_ext_document_period.factors[response_start].effect` (and the policy's factor set as a whole); every task scoring `request_assistance_documents_a6db5abf.response_days`.
- Observations O-1 … O-11 above (no red light; consequences not demonstrable on the task worlds of this difficulty; O-6 and O-9 examined further in the task files where relevant).

No SOURCE-POLICY red light at charter level: base copy verbatim, every conflict declared, rule/compute two-way equivalent, all prerequisite sentences in the blocked rule, quotable, state form honoured with a justified fallback, graph acyclic.

## closing_checklist

Written after both tasks' frozen derivations were hashed and both GTs revealed (2026-10-04T16:53–16:55Z). The difficulty does **not** close: not every task passes all four relationships.

| item | status |
| --- | --- |
| One audit file per task (`task0.md`, `task1.md`) + this file; first revision, no older revisions to trace | done |
| Every comparison section carries a PASS | **no** — task 0: SOURCE-TASK RED (T0-1); task 1: SOURCE-FACTOR RED (T1-1 = F-1) |
| Extended policies fully covered; scopes pairwise disjoint and jointly complete | yes — `charter_scope`: task 0 {award_discount, renewal_tier}, task 1 {countable_percent, document_period, document_extension}; matches the two graph components predicted above |
| Task tools and GT closed; uuid8s independent and frozen | yes (5 tools, each claimed once, used only by its own task) |
| Each tree: 1–3 prerequisite problems, ≥ max(n−1,1) value_input edges, an owner=user problem, acyclic; whole-difficulty graph acyclic | yes — task 0: n=1, 1 value_input, user renewal; task 1: n=2, 2 value_input, user extension; union of edges is two disjoint chains |
| Every computation: self-sufficient baseline, 4–6 factors with ≥2 parameter and ≥1 method, ≥1 multi-source and ≥1 cross-difficulty per task, real ladders, every factor bears weight, baseline ≠ gold | **no** — `assistance_ext_document_period` has 0 honest method factors (F-1); everything else holds (all 28 factors bear weight on their task world; all baselines definite and ≠ gold) |
| Instantiation gates re-run on the final form | not run — closure not reached (the brief's gate snapshot stands as the entry record) |

Per-task verdicts: task 0 — policy PASS, tree PASS, factors PASS, unique solution SOURCE-TASK RED; task 1 — policy PASS, tree PASS, factors SOURCE-FACTOR RED, unique solution PASS.

---

## revision_2

### charter_global_frozen (round 2)

- Auditor: Claude (erl-task-policy-audit), same independent auditor as round 1; unattended. Written before any round-2 GT was revealed.
- Round-2 inputs (sha256, recomputed, identical to `audits/_views/policy_task/financial_assistance/HASHES.txt` "# round 2"): `assistance.extended.yaml` **e00215b4bd31aa277b00627428b7732a4fdc04088017825d44b7045bbf8efeb1** (changed from round 1's 1e06045e…); `task_tools.py` 4260086cf5991a2493eafabdd61206eb824863e512b4be6b8d25e9fed60382e9 (unchanged); `task0.view.json` 3a695b81…41b (unchanged); `task1.view.json` **856ff29f18a31e9f5af051ab675652ba2993251bea1790b7e1f7417593c5d2e0** (changed).
- Because the charter hash changed, every charter-global section is re-derived in full below; the tool-module conclusions are re-checked against the new charter (module unchanged).
- Gate snapshot (coordinator, after rework): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; traceability deferred. Entry conditions met.
- Read: the same files as round 1 plus the round-2 views. Masked until the freeze: all GT fields of `tasks/*.json`, worklog. No recursive search over `tasks/` or the scenario root.
- Base section: lines 1–853 still identical to `blueprint/products/assistance.yaml` (trailing blank line only).

### What changed in the charter (from the round-1 text quoted in this file and the round-2 file)

| policy | change |
| --- | --- |
| award_discount | baseline sentence "never more than the invoice's balance still due" → "is limited to the invoice's balance still due"; individual-plan tier → "a plan not sponsored through an employer group, an individually bought or government plan, adds the non-employer-plan points" (param `non_employer_plan_points`) |
| renewal_tier | burden-window tier 1 now "a household whose ended coverage ended on or after that award's application date"; tier 2 gains the conjunct "and whose latest patient responsibility was posted on or after that award's application date" (new binding `latest_billing = XLATEST(invoices … responsibility_posted)`); `burden_months` guards `ended_on` with `(ended_on or '')` |
| countable_percent | opening sentence (and its `overwrite.replaced_by`) "Before a documents request is issued on a submitted application, the case's percent … is reassessed …" → "**A submitted application that carries no documents-requested date has its percent of the poverty guideline reassessed as the countable percent**, recorded together with the income tier that percent falls in, whether or not the tier changes."; disregard tier now "a case whose most recently received unemployment benefit statement is dated …" |
| document_period | `response_start` (constant +3/+1/0) replaced by `response_count_convention` (method): mail → business days from the request date; phone + no portal + mail/phone payments → calendar days from the next business day; otherwise calendar days from the request date; tax tier now "most recently received tax return"; params `friday_start_days`/`mail_start_days` removed |
| document_extension | business-day span adds 2 only when a remainder exists (`adjusted_days % 5 > 0`) |

### policy_conflict_scan (round 2)

- Subjects, triggers, time anchors and scope partition as in round 1 (two prerequisite components; five tools each claimed once).
- **New overlap on one field (R2-F1 below):** `assistance_ext_renewal_tier` writes `variant_name` of a renewal case at submission ("assessed at … otherwise at the tier of the award being renewed"), and the rewritten trigger of `assistance_ext_countable_percent` ("A submitted application that carries no documents-requested date has its percent … reassessed … recorded together with the income tier that percent falls in, whether or not the tier changes") is `state_due` on every submitted case without a documents-requested date — which is exactly the state the renewal tool leaves the new case in (`status="submitted"`, `documents_requested_date=None`, `fpl_percent=None`). The charter states no precedence and no exclusion of renewal cases from the reassessment.

### rule_compute_equivalence (round 2)

Mechanical sweep repeated: every `compute_basis` quotation verbatim in its own rule (5/5), every binding has a basis, every `baseline.rule` sentence in the rule, every ladder tier is a branch of its binding.
- O-1 closed: rule now names "individually bought or government plan", matching `not_employer_plan` ("individual and government plans" in the schema).
- O-3 closed: rule now reads "most recently received unemployment benefit statement", matching `LATEST(... document_date)` keyed on receipt date.
- O-4 closed: "most recently received tax return" matches `latest_return`.
- O-5 closed: extension `business_span` adds 2 only when `adjusted_days % 5 > 0`; same guard in the new document-period mail tier.
- O-6 closed: "limited to" replaces "never more than"; the deposit tier ("limited only to its working amount … becoming a credit") is now a plain refinement of the baseline limit.
- O-2 partly closed, residual observations: (a) `(ended_on or '')` removes the `None >= str` failure; (b) **new** latent gap — `latest_billing` is `None` for a household with no responsibility postings, and `latest_billing >= F('application_date')` then raises when `award_months ≤ 6`, whereas the rule makes that conjunct simply false (→ standard months); (c) the rule now says "the household's ended coverage" (singular) while `CFIELD(... status='terminated')` takes an arbitrary first row when two coverages ended. Neither (b) nor (c) arises on either task world (task 0: postings exist, one terminated coverage). The reworker's disclosed "cross-category-read gate passing via a crash path" is a property of the gate script (disabling invoice reads makes `latest_billing` `None` and the evaluation raise); on the merits it does not create or remove a factor's cross-difficulty read — `burden_window` reads coverages (`ended_on`) for real, and its tier on task 0 rests on the seeded terminated coverage and the award dates. Observation R2-O1.
- New observation R2-O2: document-period phone tier says "from the next business day after the request date (the following Monday for a request issued on a Friday, the next day otherwise)"; for a Saturday request "next business day" is Monday (+2) but "the next day otherwise" and the compute (`3 if request_weekday == 4 else 1`) give +1. No task world issues a request on a weekend.
- Layering observation O-6 general form remains for the other baseline/factor pairs (unchanged, framework-mandated).

### action_binding_and_uuids (round 2)

`task_tools.py` unchanged (same hash); five `(target_tool, computes)` pairs still each claimed once against the new charter; docstrings and uuid8s as in round 1 (carried forward on the unchanged module hash). Tool bodies still judge no prerequisite. O-7, O-8 unchanged.

### prerequisite_graph (round 2)

Same three edges, same kinds/gates/forms; `policy_source` still verbatim in each blocked rule; `fallback_reason` only on the action edge; `resolved_by` = depended-on `target_tool`; gates are real bindings; acyclic; no authoring phrasing. Unchanged conclusion.

### prerequisite_sentences (round 2)

- Edges 1–3: sentences unchanged; four-point test, single resolving write and single-reading derivations as in round 1.
- O-9 closed: countable_percent's rule no longer states the reassess-before-request order; its opening sentence is now a state trigger ("A submitted application that carries no documents-requested date …"). No rule restates any prerequisite sentence (mechanical check: no `policy_source` appears in another policy's rule).
- Fallback test of edge 2 re-run: the reassessment still writes only `fpl_percent`/`variant_name`; the trigger state ("no documents-requested date") is the state *before* the request, not a mark left by the reassessment, so it cannot stand for "reassessed"; fallback still justified.

### override_declarations (round 2)

Sentence-by-sentence conclusions of round 1 hold; the changed `replaced_by` of countable_percent is verbatim in its rule and still replaces the base redetermination sentence. No undeclared override.

### factor_ladders (round 2)

| policy | factors | P / M (honest) | changes |
| --- | --- | --- | --- |
| award_discount | coverage_points, responsibility_points, late_finalization_points, service_class_cap, working_amount_basis, discount_limit_rule | 4 / 2 | coverage tier wording (O-1) |
| renewal_tier | catastrophic_share, burden_window, amount_in_question, plan_carried_balances | 3 / 1 | burden_window tier 2 gains "latest patient responsibility posted on or after the award's application date" — a condition a hardship desk can plausibly weigh (no new billing since the award → the short award window says nothing, use 12 months); it does not hold of every renewing household; label method still defensible (O-11) |
| countable_percent | unchanged six | 4 / 2 | disregard wording (O-3) |
| document_period | agency_allowance, tax_return_allowance, household_earner_allowance, file_credit, **response_count_convention**, weekend_move | **5 / 1** | `response_count_convention` tiers are three different counting algorithms (business-day conversion from the request date; calendar count from the next business day; calendar count from the request date) — tier 1 converts business to calendar days, which is not a constant; label `method` honest. Distinct outcomes, fall-through = baseline `allowance_days`, all tiers in the rule and in `counted_days` |
| document_extension | unchanged six | 5 / 1 | O-5 |

**F-1 closed**: every computation now has ≥ 2 parameter and ≥ 1 honest method factor. Multi-source and cross-difficulty availability unchanged.

### findings (round 2, charter-global)

- **F-1 — closed** (see factor_ladders).
- **O-1, O-3, O-4, O-5, O-6, O-9 — closed.** **O-2 — partly closed** (R2-O1 residuals). O-7, O-8, O-10, O-11 unchanged.
- **R2-F1 — SOURCE-POLICY RED (new; bears on task 0).**
  - Symptom: the rewritten countable-percent trigger makes a reassessment state-due on the renewal case the customer creates, and that reassessment records a tier different from the one the renewal rule assessed.
  - Root cause: closing O-9 changed the countable-percent trigger from "Before a documents request is issued on a submitted application" to an unconditional state — "A submitted application that carries no documents-requested date has its percent … reassessed … whether or not the tier changes" — without excluding renewal applications; `submit_renewal_application_d691b1b8` creates exactly such a case (`status="submitted"`, `documents_requested_date=None`).
  - Evidence: renewal rule "A renewal application is assessed at the Catastrophic Medical Hardship Adjustment when … otherwise it is assessed at the tier of the award being renewed."; countable rule as quoted; `assistance_ext_countable_percent.trigger: state_due`; tool body of `submit_renewal_application_d691b1b8`.
  - Demonstrated consequence: shown on task 0's world in `task0.md` → `revision_2` — the renewal rule gives "Financial Assistance 25% Discount"; the countable rule, applied to the new renewal case right after the customer submits, gives 292.1 → "Financial Assistance 50% Discount". Two rules, the same case, two tiers.
  - Disclosure: a weaker, two-step version existed in round 1 (the base/extended documents rule "An application that needs documents and lacks them is set to pending documents" could make a documents request — and with it the old "before a documents request" reassessment — due on the new renewal case). The round-1 audit did not raise it; that was a miss of the round-1 audit, recorded here rather than rewriting round-1 text.
  - Affected: `assistance.extended.yaml` → `assistance_ext_countable_percent.rule` (opening sentence) and `overwrite[1].replaced_by`; interaction with `assistance_ext_renewal_tier` and `submit_renewal_application_d691b1b8`.
- R2-O1, R2-O2 observations above.

### closing_checklist (round 2)

Written after the round-2 reveals (2026-10-04T18:09Z). The difficulty does **not** close.

| item | status |
| --- | --- |
| Round-1 REDs | F-1 / T1-1 closed; T0-1 closed |
| Round-1 observations claimed closed | O-1, O-3, O-4, O-5, O-6, O-9, O-T1-2 closed; O-2 partly (R2-O1 residuals, no world consequence) |
| New defects | **R2-F1** SOURCE-POLICY RED (countable-percent trigger captures the renewal case; task 0); **R2-T1-1** SOURCE-TASK RED (stale gold-step references in task 1 proof prose) |
| Regressions | both new REDs were introduced by the rework (R2-F1 by the O-9 fix, R2-T1-1 by the O-T1-2 fix); scored values of both tasks unchanged from round 1 |
| Scopes / tools / uuid8s / trees / graph | unchanged and as in round 1 (disjoint, complete, acyclic, one user-owned problem per tree) |
| Factor bounds | met in every computation (document_period now 5 P / 1 M); every factor bears weight; baselines definite and ≠ gold |
| Gates re-run on final form | not run — closure not reached |

Per-task verdicts (round 2): task 0 — policy SOURCE-POLICY RED (R2-F1), tree PASS, factors PASS, unique solution affected by R2-F1 (T0-1 closed); task 1 — policy PASS, tree PASS, factors PASS, unique solution SOURCE-TASK RED (R2-T1-1).

---

## revision_3

### charter_global_frozen (round 3)

- Same auditor; written before any round-3 GT was revealed; unattended.
- Inputs (sha256, recomputed, identical to HASHES.txt "# round 3"): `assistance.extended.yaml` **106936904391ddafde648faeea0521d9a89f6a51830bc698ba7f57c556ac8c24** (changed from round 2's e00215b4…); `task_tools.py` 4260086c…2e9 (unchanged); `task0.view.json` 3a695b81…41b and `task1.view.json` 856ff29f…e0 (both unchanged from round 2).
- Gate snapshot (coordinator, post-rework): all seven OK; traceability deferred. Entry conditions met. No `replay_tasks` run by the auditor.
- Base section still verbatim. Charter changed → charter-global sections re-derived; tool-module conclusions carried forward on the unchanged module hash.

### What changed (round 2 → round 3, normalised text diff of every extended policy)

1. `assistance_ext_countable_percent` opening sentence and its `overwrite[1].replaced_by`: "A submitted application that carries no documents-requested date **and is not a renewal application (one submitted while the household's award is approved)** has its percent … reassessed …, whether or not the tier changes; **a renewal application keeps the tier its renewal assessment gave it.**"
2. `assistance_ext_document_period` rule and its `overwrite[0].replaced_by` gain: "**A renewal application on which the applicant reports no change of household or income relies on the documents already received for the award being renewed and needs no documents request.**"
3. `assistance_ext_document_period` phone tier: "(the following Monday for a request issued on a Friday **or a Saturday**, the next day otherwise)"; compute `3 if request_weekday == 4 else (2 if request_weekday == 5 else 1)`.
No other policy text, compute, factor, baseline, prerequisite or param changed.

### Re-derived checks (round 3)

- Mechanical sweep (all five policies): compute_basis verbatim, baseline sentences in rule, every `overwrite` superseded clause verbatim in its base policy and every `replaced_by` verbatim in the rule, every `policy_source` verbatim in its own rule and in no other rule, no snake_case token in any rule; factor sets unchanged (6/4/6/6/6; 4P2M, 3P1M, 4P2M, 5P1M, 5P1M).
- policy_conflict_scan: the renewal_tier / countable_percent overlap on a renewal case's tier (R2-F1) is removed — the countable trigger now excludes "a renewal application (one submitted while the household's award is approved)" and states that it "keeps the tier its renewal assessment gave it", agreeing with the renewal rule. The documents leg is also removed for a no-change renewal. Both carve-outs are placed inside overwrites that already supersede the base sentence they narrow (base redetermination sentence; base "needs documents … and lacks them … pending_documents" sentence), so they are declared. The definition of a renewal ("submitted while the household's award is approved") is record-decidable (another case of the customer `approved` on the submission date); "reports no change of household or income" is a caller fact the renewal tool's own arguments carry.
- prerequisite_sentences: the new sentences state no cross-problem order and ground no edge; "keeps the tier its renewal assessment gave it" refers to another policy's outcome without an ordering connective, tool, id or route — scope exclusion, not a dependency (observation R3-O1, wording only). Edges 1–3 unchanged and still pass.
- rule_compute_equivalence: R2-O2 closed (Friday/Saturday → Monday in rule and compute; Sunday → next day = Monday, consistent with "next business day"). R2-O1 (b) and (c) unchanged — judged below.
- override_declarations: no undeclared override.
- factor_ladders: unchanged except the document-period phone tier's Saturday case; F-1 stays closed.

### R2-O1 (b) on the merits — the reworker's gate argument

- What the compute does: `burden_months` evaluates `latest_billing >= F('application_date')` where `latest_billing = XLATEST('invoices', …, event_type='invoices_responsibility_posted')`. For a household with no responsibility postings and a ≤ 6-month award the rule's conjunct is simply false (→ "any other household counts the standard burden months") but the compute raises `TypeError`. This remains a rule→compute gap on that input domain.
- What the gate does (`check_compute.py`, "LOAD-BEARING cross-category" block): it forces **every** cross-category read off at once and counts an exception as "a change" (`except Exception: pass`). On task 0's post-discount world the renewal compute then raises (auditor's run: `TypeError: '>=' not supported between 'NoneType' and 'str'`). With the guard `(latest_billing or '')` the same all-off run returns **"Financial Assistance 25% Discount" = gold** (auditor's run), because with every invoice/coverage/plan read zeroed the burden collapses below the threshold and the result falls through to the award's own tier.
- Does the renewal policy's cross-category evidence genuinely bear weight? Yes, by the skill's test, factor by factor, on task 0's world: catastrophic_share (reads coverages) baseline → Catastrophic; plan_carried_balances (reads plans) baseline → Catastrophic; burden_window baseline → Catastrophic; amount_in_question baseline → Catastrophic; and forcing only the coverage read off flips catastrophic_share (no active coverage, 300.3 > 200 → standard share 10 → threshold 4700.00 < burden 5600.00 → Catastrophic). The whole-input all-off test fails only because the gold tier *is* the rule's fall-through (O-T0-1): a world with no cross data at all also lands on the award's own tier. That is a property of the gate heuristic meeting this world, not a factor that fails to bear weight; it is not a skill criterion, and every skill criterion (each factor flips; all-baseline Catastrophic ≠ gold; tiers on seeded rows) holds.
- Verdict: no red light. Two observations stand: (b) the compute knowingly does not implement the rule on the "no postings, ≤ 6-month award" domain — reached by no task world of this difficulty; and the gate's pass for the renewal computation on task 0 rests on that raise, so the gate is not evidence of load-bearing cross reads here (the auditor's per-factor runs are). (c) "the household's ended coverage" vs `CFIELD` first-row choice — no world with two ended coverages. Recorded as R2-O1 (unchanged), with this round-3 assessment.

### findings (round 3, charter-global)

- **R2-F1 — closed** (both legs: reassessment and documents request no longer due on a no-change renewal case).
- **R2-O2 — closed.**
- R2-O1 (b)(c) — observation, assessed above; R3-O1 new wording observation.
- No new red light at charter level.

### closing_checklist (round 3)

Written after the round-3 reveals (2026-10-04T18:20Z).

| item | status |
| --- | --- |
| Round-2 REDs | R2-F1 closed (charter carve-outs, verified on task 0's world); R2-T1-1 closed (step prose = call indices) |
| Other round-2 claims | R2-O2 closed; R2-O1 (b)(c) left in code — on the merits not a red light: per-factor cross-category weight holds on task 0, and the (b) raise domain ("no responsibility postings") is unreachable for a household holding an approved award (base `balances_not_eligible` denial; invoices charter: amounts owed arrive as responsibility postings); the gate's whole-off pass for the renewal computation relies on that raise and is not itself evidence |
| New defects / regressions | none found (mechanical sweep, conflict scan, both task worlds recomputed, all proof prose re-checked) |
| Every comparison section carries a PASS | yes — task 0 and task 1 PASS on all four relationships |
| Coverage / scopes / tools / uuid8s | five extended policies, scopes {award_discount, renewal_tier} and {countable_percent, document_period, document_extension} disjoint and complete; five tools each claimed once; uuid8s independent (module unchanged since round 1) |
| Trees | task 0: n=1, 1 value_input, user renewal; task 1: n=2, 2 value_input, user extension; whole-difficulty graph two acyclic chains |
| Factors | every computation 4–6 factors with ≥2 P and ≥1 honest M (6/4/6/6/6; 4P2M, 3P1M, 4P2M, 5P1M, 5P1M); per task ≥1 multi-source (catastrophic_share; recognition_rate) and ≥1 cross-difficulty on seeded rows; every factor bears weight; every all-baseline definite and ≠ gold |
| Instantiation gates on the final form | coordinator's post-rework snapshot: all seven OK (traceability deferred to KB publication); auditor did not re-run (`replay_tasks` not run, per instruction) |

Difficulty verdict (round 3): **PASS** on the source-layer audit — task 0 PASS, task 1 PASS. Open observations (no rework required): O-7, O-8, O-10, O-11, O-T0-1, O-T1-3, R2-O1 (b)(c), R3-O1, R3-O2.
