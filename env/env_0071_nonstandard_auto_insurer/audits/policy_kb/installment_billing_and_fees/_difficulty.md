# KB-doc policy audit — installment_billing_and_fees (billing) — difficulty close-out

## revision_1

- Auditor: KB-doc policy auditor, 2026-10-21. Independent of the renderer and of the policy-side auditor.
- Entry conditions (cited, not re-judged): policy side `VERDICT revision_18: task0=PASS task1=PASS charter=CLEAN`; coordinator gate snapshot 2026-10-21T06:34:17 (DOCS OK; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY OK, 0 misses; validate_scenario VALID); runtime views 0/1.runtime.json; DB access through db_query.py only (blind audit not contaminated by raw initial_state).
- Blind answers frozen before any source read: runtime_context/installment_billing_and_fees/0.md sha256 f4ad5228c4242d4009d345994ce700e8e69f4067268c31f9407e64b35ca1b529, 1.md sha256 ac407fca0bea95216360fbb980d57220b3145e8d53aada420c1c57f78215b45e (hash of each file up to `END OF BLIND ANSWER`); frozen 2026-10-21T06:42:24, reveal after that. contamination_disclosure: none.

## Per-task part verdicts

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Notes |
|---|---|---|---|---|
| 0 | PASS — blind 336.36/31.00/−40.00/327.36 then 43.97, all equal to GT; one state-derived hop | PASS | PASS | OBS-XF (deposit, draft-notice computation docs); PN-3 |
| 1 | PASS — blind 519.36, 153.88, then 215.69/31.00/−137.59/109.10, all equal to GT; two state-derived hops, leaves commute | PASS | PASS | SRC-1; PN-2, PN-3, PN-4; OBS-XF (makeup, SDP, first-invoice computation docs) |

## KB defects

None.

## Source-side items (separate from KB defects)

- SRC-1 (PLAUSIBLE): undeclared override. Base billing_installment_fee_rule "After a mid-term plan switch, invoices issued from the switch date carry the new plan's fee; invoices already issued keep theirs." is still in force (not a `superseded_clause` anywhere), while billing_ext_direct_bill_switch's first invoice after the move, issued on the switch date, carries the state schedule's fee (FL 6.00 / GA, TX 7.50) instead of the Six-Pay plan's 9.00. The parallel billing_plan_switch sentence was retired, this one was not. Task 1 figure under the base clause: minimum due 112.10 vs 109.10. The visible corpus resolves it through the scoped "and only that invoice" sentences, and the KB carries both clauses as the source has them. Details: policy_kb/1.md bijection_verdict.

## Policy-side notes (no verdict effect)

- PN-2: SDP rule "the representative first takes the switch down payment that move requires" (depended-on side states the dependency); KB: "the move requires a switch down payment".
- PN-3: "the filing charter" authoring wording in the shared fee-clause replaced_by, carried verbatim.
- PN-4: billing_delinquency's past-due trigger ("unpaid at the end of its due date") leaves a return posted after the due date without a past-due move; task-1 seed (plan current, no nonpayment notice) agrees with the literal rule.
- OBS-XF (complete class, 5 computation documents): endorsement_deposit_computation "Assembly …"; draft_notice_minimum_due_computation §2 closing sentences; first_direct_bill_invoice_computation §2 closing sentences; returned_payment_makeup_computation "Assembly …" (+ "Standard makeup"); switch_down_payment_computation "Assembly and rounding …"; plus the source label "Standard endorsement deposit". These are the source rules' assembly clauses placed once in each computation document, as the render rule requires; they name no factor, document or customer group. Judged within form; listed so the class is on record in one pass.

## Closing checklist

- Audit files one-to-one with tasks: runtime_context/…/0.md, 1.md; policy_kb/…/0.md, 1.md (all revision_1, no earlier revisions existed).
- Every normative atom of the five extended policies (rule, baseline, 25 factor ladders with every tier, 10 overwrites, 3 prerequisites) and of the referenced base policies and variant parameters is entailed by docs/billing; one document per declared factor (25), one computation document per policy (5), one hub per policy (5); retired surface complete; no KB-only rule.
- Each prerequisite sentence verbatim, state form, in its blocked hub only; every hop resolvable from it, the depended-on documents and the records.
- No other problem's tool name, route or aggregated chain anywhere; titles general.
- No scored value in any document example or tool schema.
- Final-form gates re-run 2026-10-21T06:50:08 via kb_snapshot.sh: `check_docs billing: DOCS OK`; `check_traceability: TRACEABILITY OK` (misses total 0, non-unlock 0); instantiation gates all rc=0; source sha256 unchanged (8abc2f31…ac68f, 3e96d5cc…c828d); 58 billing docs.
- Coverage note: only the billing product as claimed by this difficulty is audited; distractor corpora outside any difficulty are not covered by this skill.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=SRC-1

## revision_2

Re-audit round 2 requested 2026-10-21. Gate checked first, before any document or source read:

- `tail -1 audits/render_source/installment_billing_and_fees/RENDER.log` -> `RENDER round 3: DOCS OK` (required: `RENDER round 4: DOCS OK`). Gate not met.
- Additional context observed (cited only, nothing judged): policy-side `VERDICT revision_19: task0=PASS task1=PASS charter=CG-42` (not CLEAN); `kb_snapshot.sh` 2026-10-21T19:25:31 -> `check_docs billing: DOCS NOT OK`, instantiation gates rc=0, `check_traceability: TRACEABILITY OK` (0 misses), billing.extended.yaml sha256 now 362357063796dcb3cb8f82fd6e3e5f14680dc874bddf2ca25aaa21ff724561ed (changed from revision_1), task_tools.py unchanged 3e96d5cc…c828d.
- No document, source or task file was read for revision_2; SRC-1 closure, gold re-derivation and regression scan not performed. Revision_1 text untouched.

BLOCKED revision_2

## revision_2b

Re-audit round 2 (second dispatch), 2026-10-21. Supersedes the BLOCKED stub above for this round; revision_1 and revision_2 (BLOCKED) left untouched.

- Gate: `tail -1 audits/render_source/installment_billing_and_fees/RENDER.log` -> `RENDER round 4: DOCS OK`. Gate met.
- Policy side: `VERDICT revision_20: task0=PASS task1=PASS charter=CLEAN`.
- kb_snapshot 2026-10-21T20:04:58: `check_docs billing: DOCS OK`; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK (rc=0); `check_traceability: TRACEABILITY OK` (misses 0, non-unlock 0); billing.extended.yaml 7910eec5c5fcb3acbfaacde9f965467bf63d0ca29e95f7d1a63083bcc28336bc, task_tools.py 3e96d5cc…c828d; 58 docs.
- contamination_disclosure: revision_2 re-derivations are not blind (source and GT seen in revision_1); world via db_query only, unchanged.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Gold |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | unchanged: 327.36 notice min due; 43.97 deposit |
| 1 | PASS | PASS | PASS | unchanged: 519.36; 153.88; 109.10 (fee 6.00 + 25.00) |

- SRC-1: closed (overwrite declared in source; KB registers the base clause "no longer in force as written"; one reading of the first direct-bill invoice's fee: the state schedule's).
- Corpus changes found in the full re-read: installment_fee_rule new retired-clause block (SRC-1 fix); new §2a in draft_notice_minimum_due_computation and first_direct_bill_invoice_computation (source rule sentence on avoided installments, faithfully carried, no effect on either task); one hypothetical row 40.00 -> 45.00 in credit_carrying_on_draft_notices. No new KB defect; nothing regressed (all prerequisite sentences, tool placements, factor ladders and retired clauses as in revision_1).
- Policy-side notes PN-2, PN-3, PN-4 and the OBS-XF class stand as recorded in revision_1 (no verdict effect).

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=none
