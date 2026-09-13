# Network accounting instantiation

Checkpoint 0: frozen network claim read. Exactly two seed-fresh tasks; task scopes and tool names are disjoint. One workflow reserved. Customer identifier band +12025550160..179, documents 40000000..49999999, d4- emails.

Task 0 design thesis: customer asks to settle a precisely identified overpayment now. The refund requires the source billing review to be resolved and its overcharge credited first. Review derives the corrected transfer amount from chronological usage, tier pricing, negative entitlement branches and a numeric support portfolio factor. Credit consumes the review; refund consumes the newly reduced receivable. Refund authorization and bank payment already exist before opening. Three distinct accounting problems, chain review -> correction -> refund, two value-input edges.

Remaining task 1 space: the mutually separate unbilled transfer invoice domain, with a customer-only signed change confirmation and at least four synchronous accounting writes. No task 0 refund/correction tools or extended policies will be reused.

Base automatic clauses: no nonzero setup, restoration or termination fees in selected tiers; no resource closure or collection transition requested; active contracts and clear payment_status prevent suspension obligations. Tax review, exact-source correlation and original-payment destination are inherited. Cross-category numeric pricing requires explicit sentence-level override of the combination no-price-effect sentence; no blueprint editing.

Task 0 capability cards: assess is agent/write, completes an accountant decision for the selected preexisting review by updating its corrected net and approved/incorrect status; success returns review reference and net_amount. Credit is agent/write and creates one negative correction linked to the original charge and approved review; receipt event_id and amount. Refund is agent/write and creates one positive payout linked to the exact original payment and authorization; receipt event_id and amount. All writes are synchronous ledger decisions, not external investigations. Numeric cross-category refinement: support tier portfolio_discount caps an assisted correction and immediate refund as fractions of the source principal; remaining refundable balance stays on account. The cap is explicit in the revised available-refund sentence.

Task 0 verified standard solution: 8 August meter exports total 20000 GB, less 10000 tier allowance, times 0.067 USD/GB and one 0.04 support-limited discount = corrected net 643.20. Original source 660.00 less target gives credit -16.80, below 26.40 assisted cap. Previous net receivable -20.00 becomes -36.80; original payment 680.00 gives assisted limit 27.20, so payout 27.20 leaves -9.60. Source tax is approved us_untaxed, hence zero tax. Prior March–July 67.00 charges and -67.00 payments cancel and cannot alter August source pricing. Archived second network contract is excluded by holding. Source/external-reference linkage makes the review and refund endpoints unique.
Sensitivity: skip review => correction -26.40 instead of -16.80; skip correction => payout 20.00 instead of 27.20. The ledger changes without any tool rejection. All supporting events are preexisting; the three writes are actual accountant decisions/entries and fit one frozen clock.
Manual gates: customer authorization is an existing exact-source request and her opening authorizes execution today. Persona supplies two credentials only when asked and closes on payout completion, with no extra deliverable. Rule/compute sweep binds each ordered calculation sentence to its named factor; source-month history, negative negotiated entitlement, support tier rate and caps all have explicit sources. No base time gate applies to correction/refund; the SLA filing deadline is inapplicable to source_subtype correction. Draft prose-only recomputation reached 643.20, -16.80, 27.20 and the same source/payment references. Verification entry point: .venv/bin/python env/enterprise_cloud_service_accounting/tasks/network_accounting/verify.py 0; machine outputs in verification_0.json.

Checkpoint task 0 closed: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (32 rows); SOLVABILITY OK; COMPUTE OK (21 factors, 38 history touches, 14 branches); GROUNDING OK; SCOPE OK. Cross-off probing exposed a missing-value arithmetic issue; CPARAM fallback now explicitly returns zero, matching the rule. Published traceability deferred.

Task 1 claim: assisted final invoicing of an unbilled monthly transfer export. Occupied task 0 covers erroneous issued invoices and existing overpayment refunds; task 1 covers a not-yet-issued invoice and contains no correction credit or refund. The customer alone accepts a bounded invoice authorization; the accountant establishes the net price, posts the net invoice and the separate tax component. The four-step workflow is immediate and cannot reorder accepted ceiling -> priced net -> posted net -> tax because each next amount reads the preceding write. Root is completion of the final bill. The customer does not name these prerequisite problems.
Capability cards: authorize is user/write, files one signed acceptance of the calculated invoice ceiling and returns its event_id/net_amount; price is agent/write, completes a draft invoice assessment under that acceptance and returns event_id/net_amount; invoice is agent/write, posts exactly one net invoice and returns event_id/amount; tax is agent/write, adds the separately identified tax debit against that invoice and returns event_id/amount. Actual numerical reviews are desk arithmetic against exports already complete; no external provisioning or review wait is implied.

Task 1 handling-time result: source 35000 GB less 5000 GB allowance gives 30000 GB at 0.071 = raw 2130.00. Support $250k fraction 0.045 gives acceptance ceiling 2225.85. Network fraction 0.035 is smaller, so assessed net is 2130*(1-0.035)=2055.45 and below the accepted ceiling. Assisted posting exposure bound is 2130*0.045*64=6134.40, above assessed net, giving one net charge 2055.45. Approved us_taxable rate 0.0825 gives tax 169.57. Total final bill is 2225.02. All prior source invoices are individually settled and excluded by source_event_id and period. No cache is used.
Independent deletion sensitivity: without customer acceptance the priced amount is 0 rather than 2055.45; without assessment the net invoice is 0 rather than 2055.45; without net invoice the tax is 0 rather than 169.57. Tool execution remains callable in every omitted-prerequisite world.
Zero-wait causal cards: step 0 consumes initial_state_preexisting completed export source 45214aa5-33d6-4d46-9a9b-2910ec4a9a97 and current_user_input exact reference MM-AUG-ACCEPT, and immediately creates the signed acceptance. Step 1 consumes that prior_synchronous_tool_effect acceptance event plus initial_state_preexisting source tier and signoff; accountant arithmetic itself completes the assessment. Step 2 consumes the actual prior_synchronous_tool_effect approved review and issues one net invoice. Step 3 consumes the actual prior_synchronous_tool_effect net-invoice identifier and amount, and posts its tax. No status label pretends to be external work.
Base-invariant card: request filing is customer-only and portal is authorized; SLA claim_deadline is a conditional service_credit-only rule and is inapplicable to the invoice request, with hypothetical inclusive day-boundary cases recorded without inventing an incident. Review signoff, source and holding correlate via source 45214aa5-33d6-4d46-9a9b-2910ec4a9a97 and evidence e2bb2eea-6968-4c80-818f-de129a462a05. Source export is posted, ended at 2026-09-01T00:00:00Z before frozen time; no prior primary/portfolio charge for this source and period exists. Tax review is approved. Tax debit source_subtype supplemental is not an incorrect-billing correction.
Manual visible-context draft: masking compute and GT, reading the assistance ceiling clause, source tier and support fraction produces 2225.85; reading pricing and accepted ceiling produces 2055.45; the net-only posting and separate-tax rules produce 2055.45 and 169.57 in that order. Customer receives each figure from the agent and only invokes the real user tool after handover. No computed figure or generated identifier is in his persona. The final reply closes exactly at final-bill completion. Each binding quotes its rule sentence and reverse sweep covers source filters, ceilings, zero branches, cap order and final half-up rounding. Runnable verification: .venv/bin/python env/enterprise_cloud_service_accounting/tasks/network_accounting/verify.py 1.

Final checkpoint: exactly two tasks, seven disjoint extended policies, seven independently named tools, one four-step workflow claimed only by task 1. All customer identifiers are in the assigned d4 band. Every created event now carries its customer reference, keeping post-write customer queries complete. Temporary authoring scripts and identifier staging files were removed. Retained verification plans are inputs to verify.py, not temporary generators. Published-KB traceability is deferred until rendering.

## check_extended

```text
🔎 EXTENDED gate  (category=network, extended_policies=7, cross-cat=7, workflows=1, task_tools=7, tasks=2, workflow_guided_tasks=1, no_handoff=True)
  [PASS] compatible charter; every policy has a real cross-category factor; one task closes the unique workflow and all policies are covered across the suite
EXTENDED OK
```

## check_task_tools

```text
🔎 TASK-TOOL-CONTRACT gate  (7 tools)
  [PASS] complete business effects, Args coverage, four-way parameter typing, and success returns
TASK TOOL CONTRACT OK
```

## replay_tasks

```text
🔎 REPLAY gate  (2 tasks)
task                         acts  det  nonvac errs  clos  init  match
0.json                         11 True    True    0    32    32   True
1.json                         13 True    True    0    25    25   True
REPLAY OK
```

## check_solvability

```text
🔎 SOLVABILITY gate  (2 tasks, category=network)
   identity preamble: find_customers -> verify_customer_identity (K=2, log=verification_log)
task         verify calls base gates  seed rows   ok
0.json         True     3          6         30 True
1.json         True     4         13         23 True

SOLVABILITY OK
```

## check_compute

```text
🔎 COMPUTE gate  (2 tasks, 7 extended_policies, 7 cross-category)
task                         comps fact hist brch step  match
0.json                           3   21   38   14   11   True
1.json                           4   24   10   19   13   True

suite means:  factors=22.50(>= 5.0)   branches=16.50(>= 4.0)   steps=12.00(>= 4.0)
suite depth:  history_rows_max=38(>= 8)   branches_max=19(>= 5)

COMPUTE OK
```

## check_grounding

```text
🔎 GROUNDING & DISCLOSURE gate  (2 tasks)
task           idAttrsUsed  answers  writes  cond    ok
0.json                   1        3       3     5  True
1.json                   1        4       4     8  True

GROUNDING OK
```

## check_cache_diff

```text
🔎 CACHE-DIFF diagnostic  (2 tasks)  holding=network_holdings  quantity_fields=[]
task                        reconciled QF (field: seeded vs true)  recheck info
0.json                                                     (none)    False    -
1.json                                                     (none)    False    -

CACHE-DIFF INFO (optional; no correctness gate)
```

## check_cross_fire

```text
🔎 SCOPE gate  (2 tasks, policies=7, workflows=1, hard-fails=0)
  [PASS] policy ownership, trigger declarations, and task scopes are structurally consistent; no business applicability or tool-rejection behavior was inferred
SCOPE OK
```

Manual final review: policy spaces separate correction/refund of an issued source from first issuance of a monthly source. Every problem has a finite synchronous accounting effect; user acceptance is personally signed, with the real receipt entering the next step. Automatic lifecycle fees are zero and neither seed demands a suspension or resource transition. Source, billing period, tax evidence, and source-specific offsets are authoritative. Rule/compute grouping, cap order, and final rounding have been swept in both directions. Artifact provenance and visible-KB blind audit remain the next pipeline stage.

# Policy audit rework round 2

Read the complete _difficulty.md, 0.md and 1.md from audits/policy_task/network_accounting. F1 is an undeclared source-allocation override with an activated task-0 ambiguity; F2 is exact-source rule/compute drift demonstrated by unrelated historical reviews and three additional selector omissions. O1 concerns explicit workflow zero-wait metadata; O2 correctly observes permissive tools and requires preserving their direct CRUD boundary. The auditor's two evidence-argument corrections are not artifact findings: refund retains consent request Q and invoice retains posted meter S. No source/tool suffix, customer identity, prerequisite graph or existing gold amount needs to change.

F1 response in progress: define the monthly-aggregate correction boundary explicitly, declare the inherited source-allocation sentences it replaces, and preserve original charge identity. F2 response follows separately: derive each source through the selected review/request and add all quoted source/status/meter/period predicates. Domain counterexamples will be tested in memory with the same real verifier and no tool guards.

F1 closed in the policy/task layer: added three clause-level overwrite declarations (pricing allocation, pricing remaining allowance, category chronological allocation), each bound to the explicit monthly aggregate corrected-target sentence. Narrow route requires sole monthly primary charge, matching recorded aggregate/reconciliation quantities, completed month, same unchanged tier/attributes, us_east and full-month activation. The original invoice reference still owns the correction; outside-route allocation is untouched. Task 0 remains 643.20 / -16.80 / 27.20. EXTENDED per-task validation follows.

F2 task-0 selector closure: the cycle is anchored to its exact latest pending refund authorization, then its related review, then that review's original charge. Assessment now dereferences the charge's period. Credit original requires posted, target requires selected review ID plus exact source/approval/decision/cause, and prior offsets admit only financial correction credits/debits for that source. Refund principal and returns/refunds use the same selected payment, with posted ACH explicit. Each selector and every filter is a verbatim rule/basis sentence; unrelated older reviews cannot enter any target.

F2 task-1 selector closure: all four policies select one exact invoice review, dereference its source bundle, and obtain the billing month from that posted primary internet_egress meter. Quantity now reads only that exact full-month source; the route explicitly requires it to be the sole such meter in the month, preserving ordinary source allocation rather than extending task 0's override to this route. Acceptance also matches related_review; assessed matches both selected review ID and source bundle; issued matches source, primary subtype, portfolio component, internet_egress meter and source period. Older unrelated approved reviews can remain on the same holding without affecting the invoice or tax. Every new binding/filter is quoted in rule and compute_basis.

O1 closed: requires_external_wait=false and concrete zero_wait_proof are now explicit on the workflow and each step, with matching solvability statements. O2 preserved without a code change: task_tools.py SHA256 dfa53d76568d1fdc55380d1ecb2085aba8a31367a3bc4f8cc148b2d6dbd9c6f6 exactly matches the audited freeze; no prerequisite checks, duplicate checks, guards or extra tool effects were added. Auditor-corrected refund consent Q and invoice posted-meter S bindings remain unchanged. All round-2 compute/factor/argument/rule references are propagated from fresh verification results, and numerical amounts and actual receipt IDs still match round 1.

# Network accounting — policy audit rework round 2

Read all three assigned reports in full: _difficulty.md, 0.md and 1.md.

- **F1 closed.** The assessment now declares three verbatim source-allocation overrides and their exact monthly-aggregate replacement. Its route requires the sole monthly primary charge, matching invoice/reconciliation aggregate quantity, a completed full month, unchanged source/holding attributes, and us_east. Original invoice attribution stays fixed. The existing task-0 target is uniquely 643.20; the first-export-only zero target is expressly outside the replacement basis.
- **F2 closed.** The correction chain follows the selected pending refund authorization to its exact review and original charge; assessment dereferences the charge period. Credit original explicitly requires posted, target requires both selected-review and source IDs, and prior offsets select only posted financial corrections for that source. The invoice chain selects one review and its exact full-month source. Accepted authorization also matches the selected review; assessed net matches review and source; issued net additionally matches internet_egress and source period. The narrow full-month-source invoice scope preserves inherited source allocation.
- **O1 addressed.** Workflow and each of its four steps now carry requires_external_wait=false and concrete zero_wait_proof, propagated to the per-action solvability ledger.
- **O2 preserved.** Tools remain permissive atomic CRUD, with no new source, deduplication or prerequisite guards. task_tools.py SHA256 remains the exact audited value dfa53d76568d1fdc55380d1ecb2085aba8a31367a3bc4f8cc148b2d6dbd9c6f6.
- **Auditor derivation corrections preserved.** Refund uses consent request Q as network_event_id; invoice uses posted meter S. Neither was an artifact defect, and neither argument changed.

The runnable verify_audit_regressions.py checks both reported historical-review countermodels using local alternate-history snapshots with settled prior-source accounting. A 100.00 unrelated review leaves credit -16.80, invoice 2055.45 and tax 169.57 unchanged. It also checks all eight source/status/meter/period predicates highlighted by F2 and the explicit F1/O1 metadata. Result: AUDIT REGRESSIONS OK. The original task seeds are unchanged.

Fresh verify.py results retain task-0 amounts [643.20, -16.80, 27.20] and task-1 amounts [2225.85, 2055.45, 2055.45, 169.57], their original receipt identifiers and all prerequisite sensitivities. Factor traces, argument proofs, rule-based action necessity, solvability action semantics and task rationales were propagated together. No blueprint, runtime, skill, audit or sibling artifact was changed.

Full final gate snapshot: gate_snapshot_round_2.txt. Machine-readable equivalent: gate_results_round_2.json. EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all pass with EXIT_CODE=0; the optional cache diagnostic also exits zero. Task closure counts remain 32/32 and 25/25; compute factors are now 30 and 36, reflecting the explicit source-selection bindings. Published-KB traceability remains deferred.

Final checkpoint: the round-2 full gate block was executed after all policy/task changes. The two local temporary rework scripts were then removed; verify.py and verify_audit_regressions.py are retained runnable verification artifacts.

## Rework round 3 — audit revision 2

Read all four audit files in full, including original and revision_2 sections and all calculation evidence. F1/F2 remain auditor-closed, O1 addressed, O2 preserved. New preexisting F3 is the assisted invoice discount bypassing inherited portfolio eligibility and pricing priority. Repair will explicitly declare the narrowly scoped assisted-route replacements inside the extended charter, propagate its policy justification into task1, and retain original seeds, arithmetic and tool bodies. Full gates and local regression checks will follow.

F3 charter checkpoint: network_ext_price and network_ext_invoice now each declare four exact base-clause replacements covering monetary usage selection, inclusive threshold applicability, priority restriction, and primary price priority. The price selects its existing assisted fraction independently of the ordinary portfolio test; invoice consumes the exact approved assessment without a second price selection. Both replacements preserve primary-net-only application and the ordinary rules outside the existing narrow source route. Blueprint values and compute expressions remain unchanged.

F3 task checkpoint: task1 factor traces, monetary argument uniqueness, evaluation necessity, per-action semantics, and rationale now cite the scoped pricing authority. It explicitly records standard monetary usage 2485 < 25000 and rejects the competing 2130/175.73/2305.73 path through source overrides, not caps. Existing expected 2225.85/2055.45/2055.45/169.57 and all seed/closure records are unchanged. Task0 JSON untouched.

# Network accounting — round 3 audit response

Read `_difficulty.md`, `0.md`, `1.md` and `revision_2_calculation_evidence.json` completely, including preserved original and revision_2 sections.

- **F1 remains closed.** No assessment allocation rule or task-0 content was edited in this round. Its three exact allocation overrides remain present; local regression confirms the sole aggregate quantity 20000 and corrected target 643.20.
- **F2 remains closed.** Every exact-source binding remains unchanged. The unrelated approved-review100 countermodels still leave correction -16.80, invoice2055.45 and tax169.57 unchanged. Eight additional source/status/meter/period predicates remain explicit.
- **F3 closed in source artifacts, pending independent re-audit.** Both `network_ext_price` and `network_ext_invoice` now expressly replace four exact base clauses: usage-based portfolio selection, inclusive threshold applicability, the portfolio higher-priority restriction, and primary discount priority. Their rule text limits the replacements to the existing completed single-source assisted on-demand invoice route. The assessment selects the declared assisted fraction independently of ordinary portfolio eligibility; issuance uses that exact approved assessment without a second price selection. Each replacement is literal in its rule, and the affected discount/assessed compute_basis, task factor traces, argument proofs, action necessity, solvability semantics and rationale were propagated. This is a charter defect repaired in the extended scope; the frozen blueprint is unchanged.
- **O1 remains addressed.** Workflow and every step retain explicit synchronous no-wait metadata; all four step proofs pass the regression check.
- **O2 remains preserved.** The exact frozen tool hash remains `dfa53d76568d1fdc55380d1ecb2085aba8a31367a3bc4f8cc148b2d6dbd9c6f6`; no policy validation or extra effect was added to any atomic tool.
- **Auditor derivation corrections preserved.** Task-0 refund uses consent Q; task-1 invoice uses posted meter S. These were audit derivation corrections, not artifact findings.

The F3 local Decimal check explicitly reproduces standard monetary portfolio usage2485 <25000 and the excluded ordinary net2130/tax175.73. It then verifies the declared assisted assessment and invoice2055.45 and tax169.57. Both candidate nets fit the accepted ceiling and posting cap; the new explicit source clauses supply uniqueness. The existing task amounts, initial records, exact receipt dataflow and prerequisite sensitivities remain intact.

Final validation: both local gold verifiers, the F1/F2/F3 regression verifier, and all seven mandatory gates pass with EXIT_CODE=0. Optional CACHE-DIFF also exits0. Replay remains deterministic and nonvacuous; task0 closure32/32, task1 closure25/25. Computations retain30 and36 factors; the task suite remains exactly2 tasks with exactly1 four-write workflow, including its user-owned acceptance.

Full command/output/exit-code snapshot: `gate_snapshot_round_3.txt`. Machine-readable snapshot: `gate_results_round_3.json`. Regression evidence: `audit_regressions_round_3.json`; gold receipts and sensitivities: `verification_0.json`, `verification_1.json`. No temporary authoring script was created this round; none remains. Published-KB traceability remains deferred by pipeline instruction.


## Rework round 4 — prepublication provenance diagnostic

Read the exact full traceability diagnostic. Seven unavailable tool-name strings are publication-dependent and remain deferred. The eighth finding is task1 call_agent_discoverable_tool arguments.request_id network_authorize554a0ec893fa: the actual user receipt is visible at runtime, but unchanged check_traceability excludes user calls. Diagnose a legitimate seeded unsigned authorization object, signed by the real customer write, so its stable ID is query-visible before signing and its approval/value remain load-bearing. No persona ID hardcoding or gate/runtime edits.

Round-4 world/tool/charter checkpoint: seeded one unsigned nonfinancial network_service_record form, pending/request subtype with empty notice and zero ceiling, exact S/R links and random stable UUID. Customer-only authorize now directly updates that same form into the filed pending network_request and returns its ID. The accepted SUM still requires network_request; the unsigned form is explicitly excluded. Existing monetary formulas and all F1/F2/F3 overrides are untouched. No new validation guard exists.

# Network accounting — round 4 provenance response

Input read completely: `gate_snapshots/traceability/network_accounting/round_prepublication_diagnostic_20260913T041628652492Z.txt`.

- **Diagnostic task1 `call_agent_discoverable_tool:arguments.request_id` — CLOSED.** The old generated authorization reference was available in the real user receipt, but the unchanged traceability checker excludes user calls. A legitimate unsigned source-specific form is now seeded as `network_service_record`, pending/request subtype, with empty notice and zero net_amount. Its random UUID is returned by the ordinary earlier find_network_events query. The real customer-owned authorize action accepts this form's request_id and updates the same record into a filed pending network_request, stamping the exact customer reference and frozen filing times and setting the accepted ceiling. Its actual receipt returns the same identifier. No ID or tool name was placed into the persona, and no gate/runtime behavior was changed.
- **Seven diagnostic `unlock_*_discoverable_tool:tool_name` findings — publication-dependent, deferred.** The unchanged full traceability run still exits1 with exactly these seven unpublished tool-name misses and no internal-reference miss. Nothing was inserted into another source to make unpublished tool names pass.
- **F1 preserved.** The correction route retains all three exact aggregate-allocation overrides and its 643.20 target. Task0 bytes remain unchanged from the round4 starting checkpoint.
- **F2 preserved.** Exact source/review/status/meter/period bindings remain unchanged. Old-review countermodels still leave credit-16.80, invoice2055.45 and tax169.57 unchanged.
- **F3 preserved.** All eight exact threshold/priority replacements remain intact across price and invoice, with their narrow route and authoritative-assessment semantics. Monetary portfolio usage2485<25000 remains acknowledged, and the assisted net2055.45/tax169.57 remains uniquely selected.
- **O1 preserved.** Workflow and four steps remain explicitly synchronous. The user signs the existing form at consultation; the three agent writes consume actual preceding effects.
- **O2 preserved in behavior.** Only the authorization tool's direct atomic effect and signature changed: it updates the specified preexisting form instead of creating a newly generated identifier. It remains owner=user/rw=write. No prerequisite checks, source guards, deduplication checks or hidden calculations were introduced. The prior tool byte hash therefore intentionally changes; ownership and permissive atomic behavior remain intact.

The form's existence does not satisfy authorization: accepted sums only filed pending network_request records, so the unsigned service record contributes zero. Live Engine evidence shows its ID in the earlier agent query, its real user receipt after filing, pricing0 before and2055.45 after, and omission pricing0. Full live execution matches strict scoring replay hash `87d1ab137a4c368a23e99b183b7fd7326240700784ada047639199330f14f39f`. This runtime probe uses no KB content and makes no tool-discovery claim. The user-owned step and all three value-input edges remain load-bearing.

Stable authorization form/receipt: `eeaa749f-348c-4b78-8b3e-ee5df43ed372`. New actual invoice receipt: `network_invoice98547fb7c99e`. All downstream arguments/proofs and verification receipts were propagated. Existing task amounts remain [643.20,-16.80,27.20] and [2225.85,2055.45,2055.45,169.57]. Task1 gains exactly one unsigned form, giving26 closure/seed rows; task0 remains32. The bundle still contains exactly2 tasks and exactly1 four-write workflow with one user write.

Final gates: EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE and optional CACHE-DIFF all exit0; both gold verifiers, regression verifier and live Engine verifier exit0. TRACEABILITY exits1 solely for the seven deferred unpublished tool names. Full outputs are in `gate_snapshot_round_4.txt`, with machine equivalent `gate_results_round_4.json`. Runtime evidence: `live_provenance_round_4.json`; regressions: `audit_regressions_round_4.json`. All changed source and evidence paths/fingerprints are listed in `changed_files_round_4.json`.

Only own task scope was written. Every base YAML value and task0 bytes are preserved. No temporary authoring scripts were created or remain; runnable verify scripts are retained evidence. Ready for the original source auditor and fresh Network renderer.

