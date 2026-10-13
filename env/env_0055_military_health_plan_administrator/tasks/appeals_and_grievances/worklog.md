# appeals_and_grievances — instantiation worklog

- draw (draw_counts.py --tasks 2): task 0 → prerequisite_problems 2, factor_counts [5,4,4]; task 1 → prerequisite_problems 3, factor_counts [6,5,6,5].
- Computable quantity: the only numeric field the appeal tables carry is appeal_cases.amount_in_dispute, booked by appeal_file and appeal_escalate; every problem is therefore a filing or an escalation that books it. Agent-side document / representative / track updates carry no number and are not problems.
- task 0 (closed): Select late-filed claim — open reconsideration on line 4 (80.84) → join line 5 (154.92) → formal review of WAP-26-118204 (50.60). Tools file_select_line_reconsideration_8918facf, join_select_line_reconsideration_711ff8e9, request_formal_review_d6793db3. Per-task gates: TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, EXTENDED OK, GROUNDING OK, SCOPE OK.
- task 1 (closed): Select inpatient mental health stay — Allowable Charge Review on line 1 (940.80) → join line 2 (1,209.60) → second-level request on WAP-26-121907 (5,391.36) → expedited telephone reconsideration of the denied continued-stay request (3,594.24, root, agent). Tools file_allowable_charge_review_fa2a3df4, join_line_charge_review_4bed256c, request_second_level_reconsideration_e1311ea5, take_expedited_reconsideration_1b494fd4.
- final suite: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite history max 9, branches max 179), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. check_traceability not run (needs the published KB).

## Round 2 — policy-task audit rework (audits/policy_task/appeals_and_grievances/)
- Extended policies regenerated from one generator (base section verbatim, checked key by key); factor ids renamed per policy (fl_/jl_/fr_/ar_/jr_/sl_/ex_). Scored values unchanged in both tasks.
- G-1 / G-4 / task-1 finding 1: first-case rules now open only on the claim's lowest-numbered standing posting (CFR) / lowest-numbered disputed paid line (ACR); E2/E4/E6 now wait on the highest-numbered posting/line standing *joined to* a case opened on an earlier posting/line — a state only the joining write produces; conditions restate the sentences exactly; P6/P7 daily-allowed tier 1 reads the same joined state.
- G-5: P3's second wording ("The next level hears a claim only once ...") removed; E2 sentence is the only statement of the dependency.
- G-6: no billed amount above an allowed amount enters dispute — billed fall-backs divide a nonparticipating provider's billed amount by one plus the balance-billing limit; P6/P7 default daily rate is the stay's paid rate.
- G-3: P6/P7 state they apply only to a stay with a paid day line; divisions guarded.
- G-7: payment-method tiers decided by the counted other-insurer payment against the allowed amount; the always-true "TRICARE pays second" condition removed (all seven policies).
- G-8: inpatient percentage ladder = non-network with a percentage basis / network with a lesser-of basis / none — all reachable; Retiree A network now takes its 20 percent.
- G-9: P4–P7 basis ladder gains the per-admission-copayment tier; P1–P3 network lines on fixed-copayment tiers take the class copayment.
- Observations: O-2 joining lookup accepts filed or under-review cases; O-4 P4–P7 read the schedule of the enrollment the lines were billed under; O-3 rule wording now matches the max over the claim's postings of the service date; G-2/O-1 (customer-row target) kept as the gate-supported reading and noted.
- Proof text swept in both tasks (tracing, closure, factor traces/tiers from the ladders, solvability semantics, rationale rewritten for round 2).
- Final gate block round 2: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (history max 9, branches max 205), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred (needs published KB).

## Round 3 — post-render traceability
- check_traceability flagged the find_providers(provider_id) argument in both tasks (id not yet returned by any earlier read). Fix: in evaluation_criteria the provider lookup now runs right after find_select_claim_lines, whose return carries that provider_id (task 0: reads 0 customers, 1 verify, 2 DEERS, 3 cases, 4 documents, 5 claim lines, 6 provider, 7 enrollments; task 1: 0 customers, 1 verify, 2 DEERS, 3 enrollment, 4 authorizations, 5 unit ledger, 6 claim lines, 7 provider, 8 cases, 9 documents). Write steps and scored values unchanged.
- Text swept: step references in tracing (task 0 claim lines step 5, cases step 3; task 1 cases step 8 — the old "step 9" was already off by one), standard-solution read order in both rationales, provider-read objective wording, revision notes.
- appeal.extended.yaml and task_tools.py not modified this round (no re-render needed).
- Gate block round 3: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, TRACEABILITY OK, CACHE-DIFF INFO, SCOPE OK.
