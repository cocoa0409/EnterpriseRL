# Policy-KB audit — payment_plan_servicing (product plan) — difficulty close-out

## revision_1 (2026-10-21)

Inputs checked (Step 0): policy-side `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN`; runtime view 0/1.runtime.json (549ce6bce2441a6e / c031f29e05d87798); db_query.py access path (blind on the DB side); gate snapshot re-run via kb_snapshot.sh at 2026-10-21T21:05:19: check_docs.py plan => DOCS OK; check_traceability.py payment_plan_servicing => TRACEABILITY OK (0 misses); EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; sha256 503da59afb88 / 3b987caeb498 / 344635286eee / 2a711ba9efef (unchanged from brief). Corpus hash (docs/plan, 60 files) first16 42d65003612adebb.

Files: runtime_context/payment_plan_servicing/{0,1}.md (blind_answer frozen 20:45, sha256 eeb115df95fef640 / 2fdd9af680c85bf8, then gt_comparison appended); policy_kb/payment_plan_servicing/{0,1}.md.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS (conditional C-1) | PASS | PASS |
| 1 | PASS | PASS | PASS |

Blind answers reproduced every scored value with no source contact: task 0 re-age 27 / 2025-09-15, pause 31, recompute 74.98, lowered installment 62.00; task 1 re-figure 74.73 over 48, signing ACH 109.13. All fall-back numbers computable and different. No hop pre-solved.

Closing checklist
- Every extended policy (6) and base policy (10): rule, baseline, every factor ladder (24 factors, every tier with figures), every prerequisite (4 edges: 3 action-form, 1 state-form; each sentence verbatim in exactly one doc of the blocked policy), every overwrite (11 replaced_by; 9 retired base clauses written as "no longer in force"; no undeclared retirement) carried at equal strength.
- Tool names: each of the 6 task tools only in its own hub; contracts match task_tools.py bodies.
- No worked example / FAQ figure equals a scored value.

Conditional (cross-product, re-judge after the assist render)
- C-1 (task 0): the pause allowance reads the open case's determination days (30) and BadgerCare Plus screening deadline days (45) that the case's Financial Assistance Program (Charity Care) tier sets (CPARAM assist). No published doc or record field carries them now. Re-judge that the assist corpus publishes both figures for 'Riverbend Full Charity Care (0-200% FPL)' under words a reader of the case record can find ("determination days", "screening deadline days"). The scored 31 holds for any det+screening ≥ 32 days.

Observations (not KB defects, not src defects)
- O-1: re-age hub carries its replaced_by without "together with any deferrals it grants"; the deferral factor doc carries that the deferred installments move to the end together with the counted ones — corpus entailment unchanged.
- O-2: signing and re-figure computation docs carry the source rule's load-bearing, non-commuting assembly sentences ("a percentage held back …, an amount credited …, amounts added …"; "the term used is the shorter of the terms allowed"), which disclose that adjustments exist. Source-mandated (XF A.3); the KB cannot drop them.
- O-3: the KB (like the source rule) says "BadgerCare Plus screening referral notice / determination notice" while records say MEDICAID_SCREENING_REFERRAL / MEDICAID_DETERMINATION_NOTICE; the word "Medicaid" never appears in the plan KB. BadgerCare Plus is Wisconsin Medicaid and KB_search "Medicaid screening referral notice" ranks both BadgerCare docs first, so findability holds; worth keeping in mind if the assist corpus names it differently.
- O-4: re-age and pause are parallel prerequisites of the recompute; intermediate term_months differ by order (27→31 vs 28→31) but both orders reach the same final writes and scoring compares the final DB hash after the pair-order check — no scoring ambiguity.
- B-1 (base, for the coordinator's base log): add_on_balance_terms renders tier_overflow_rule REOFFER_ON_NEXT_TIER ("re-offered a plan on the next tier") while base clause 3 says "the tier matching the combined balance"; both carried verbatim from base.

Coverage note: only product plan is audited here; claim and assist corpora are unpublished; base-only distractor products are outside this skill.

VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_2 (2026-10-22, cross-product re-judge)

Snapshot 2026-10-22T00:40:20: check_docs.py plan => DOCS OK; check_traceability.py payment_plan_servicing => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0); EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; sha256 503da59afb88 3b987caeb498 344635286eee 2a711ba9efef (unchanged since revision_1); docs/plan 60 files, corpus hash 42d65003612adebb (unchanged).

- Revision_1 had no RED; the KB is unchanged, so nothing could regress, and no new KB defect was found.
- C-1 closed: assist publishes determination 30 / BadgerCare Plus screening deadline 45 days on every tier; task 0's pause 31 confirmed. O-3 closed.
- Seed-realism pass (all other-category rows of both worlds; members listed in 0.md / 1.md revision_2): task 0 has 2 misses, task 1 has none.
  - S1 (gold-moving, task 0): the 2025-11-18 pay-stub request and missing-information notice, and the pending_documents / 2025-12-18 case state they carry, are not producible under assist rules: the case was complete 2025-10-08, and income proof had already been accepted. Pause 31, recompute 74.98 and lowest 62.00 rest on them (read as a submitted case: 29 / 78.63 / 64.48).
  - S2 (no scored value, task 0): ED account missing its cycle-2 summary statement of 2025-03-26 while the plan was pending signature.
- O-5: encounter statement rule names no payment-plan exemption; the plan base clauses imply it.

VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=S1,S2

## revision_3 (2026-10-22, seed-rework confirm)

Gate: policy_task tail reads `VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN`. Snapshot 2026-10-22T01:10:22: DOCS OK; TRACEABILITY OK (0 misses); EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; sha256 503da59afb88 3b987caeb498 0976d57dc09a 2a711ba9efef. Charter, tools and plan corpus are unchanged (42d65003612adebb), so no re-render was needed. S1 and S2 are closed (rows 7415496c, f6757628, 143021a6, 46f78010 reworked; 35c178ae, dbae375f removed; a61ddf4c added; all consistent with the published assist and encounter rules). Task 0 re-derivation (not blind) lands on the unchanged gold 27 / 2025-09-15 / 31 / 74.98 / 62.00. The persona matches the records. No new defect and no regression.

VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=NONE
