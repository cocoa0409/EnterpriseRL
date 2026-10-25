# KB-doc policy audit — gap_waiver_cancellations_and_claims (product `gap`, GAP Waiver Addenda)

## revision kb_round1 (2026-10-20)

### Entry conditions (Step 0)
- Policy-side verdict on record: `VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN` (audits/policy_task/gap_waiver_cancellations_and_claims/_difficulty.md, as supplied in the brief).
- Gate snapshot supplied by the coordinator (2026-10-20T22:30:09). Fresh execute-only re-run of `/tmp/erl0072_coord/kb_snapshot.sh gap_waiver_cancellations_and_claims gap` at 2026-10-20T22:39:43: check_docs DOCS OK; traceability TRACEABILITY OK, 0 misses; check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK; gap.extended.yaml 8cef85fe…f2c6, task_tools.py b862ea9d…bd0 (unchanged from the brief). check_traceability was not run directly by this auditor.
- Runtime views verified: 0.runtime.json 9ad914b4…da55, 1.runtime.json 46410545…1edf. DB access via `db_query.py` (tool-shaped): both blind audits blind on the DB side. The access path exposes share read tools only, so the identity-verification write was outside the blind view (not a KB matter).
- Input complete.

### Order and isolation
- Blind answers frozen before any source read (runtime_context/…/0.md sha 1f8e62d9…3fc5, 1.md sha e7cff335…41de); gt_comparison appended afterwards; blind sections untouched. contamination_disclosure: none. Doc `meta` not read. No other scenario and no sibling difficulty's tasks read. Writes limited to the two audit directories; scratch `/tmp/kbaudit_gap_0072/`.
- CPI corpus unpublished: the one figure depending on it (CollateralGuard Plan B borrower maximum deductible, task 0's deductible reimbursement and everything downstream) was frozen as conditional and resolved at reveal from `blueprint/products/cpi.yaml` (500.00); every other figure is independent of CPI documents.

### Charter-wide base and variant map (shared by both tasks)
| Base policy / variant block | KB home | Judgement |
|---|---|---|
| gap_agg_multi_holding (no per-borrower limit; max 1 open per contract) | `19ce3d02`, `e2fc1854` | equivalent |
| gap_agg_contract_portfolio (own contract; VSC refund and CPI premium clauses retired for Premier/Plus; VSC cancel on total loss; force-placed never primary; independent cancellation) | `8497c5dc` | equivalent; retired surface correct |
| gap_enrollment_terms + prices 495/595/695/795/895/995, LTV 120–150, terms 60/66/72/75/75/75, max financed 25k–60k, age 10, excluded uses, signing only, coverage period, non-transferable | `f83210c5`, `dbe7a477`, `e2fc1854` | equivalent |
| gap_claim_benefit (filing status/notice, one decided claim, theft wait, denial order, benefit clauses (a)–(e) with per-plan retirement, credit/denial/withdrawal) + 90/90/30/30/10/10, documents, max LTV/benefit/deductible tables | `47385208`, `39c3d6f3`, `3d7573b3`, `4baa6c7e` | equivalent; (e) retired for Premier only |
| gap_voluntary_cancellation (signature, 10 days, effective date, free look, no payment change) | `ff7ca509`, `50856ae7` | equivalent |
| gap_company_cancellation (payoff other than total loss, repo sale, unwind; reinstatement keeps) + effective-date basis, 30 days | `e2357f26`, `50856ae7` | equivalent |
| gap_cancellation_refund (cancelled only, once, full refunds, pro rata less fee, fee waived on payoff for Plus/Premier, min 10.00, fully earned, destinations) + free look 30/30/30/30/60/60, fees 75/75/50/50/50/25 | `023d2fb4`, `c693fc5d` | equivalent |
| gap_expiry | `e10e78dc` | equivalent |
| measures (unearned ratio, scheduled balance, excess LTV) | `023d2fb4`, `47385208` (a)/(b) | equivalent |

### Per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS (conditional on the CPI corpus rendering Plan B's borrower maximum deductible 500.00 under that name) | PASS | PASS |
| 1 | PASS | PASS | PASS |

### KB defects
None.

### Observations (no verdict effect)
- O1: the baseline sentence defining whole months ("the difference in calendar months between them, less one when the later date's day of the month is below the earlier date's") has no verbatim home; the KB's ordinary-sense "whole months" plus its boundary examples (`0897a06c`, `bd9ca42b`, `dcd3ed8d`, `3128269f`) entail the same count on every date pair, month-ends included.
- O2: the unlock description of `record_claim_worksheet_benefit_931d4ebc` names no plan; the visible KB scopes it to Premier and makes the Plus benefit the borrower's own acceptance.
- P1 (policy-side): factor-reads-factor in the Premier deductible reimbursement (`pd_proof_standing` reads the insurer `pd_policy_at_loss` selects; `pd_allowance_test` reuses the naming-proof test); rendered faithfully.

### Source-side items (exhaustive, separate from KB defects)
- **S1** (task 0 seed legality): March claim 7297a6ca… has no `gap_claim_withdrawn` record although the persona and the GT objective call it withdrawn and the addendum is `claim_open`; the base filing rule (addendum status active) cannot produce the 2026-08-19 filing 5314daaf… from that state. Score unaffected.
- **S2** (task 0 seed realism, CONDITIONAL on the CPI corpus): CPI tracking e043d3e3… still `compliant` after its policy on file (Buckeye, expiring 2026-09-18) lapsed with no accepted replacement (Keystone proof rejected 2026-04-06) and no lapse detection or first notice by 2026-10-05, against cpi.yaml's compliant → lapse_notice transition and 5-day first-notice rule. No GAP figure reads that status.
- Checked and reproducible from published docs (no item): every contract ledger row read by the factors in both tasks (late charges, extension fees and eligibility, SCRA caps and end dates, due-date changes, payment allocations spot-checked), VSC refunds 162.77 / 287.59; CPI premiums and refunds reproduce under cpi.yaml (conditional on the CPI corpus).

### Closing checklist
- Audit files one per task in both directories; blind answers frozen first; every comparison section carries PASS.
- Every normative atom of `gap.extended.yaml` (base, variants, six extended policies incl. overwrite, 3 prerequisites in task 0's closure and 1 in task 1's, 32 factor ladders) has an equivalent home; every prerequisite sentence verbatim on its blocked side only; every factor ladder complete and findable from the record words; no tool name, route or chain beyond the sentences.
- Gates re-run on the final form (snapshot above).

VERDICT kb_round1: task0=PASS task1=PASS kb=CLEAN src=S1,S2

## revision kb_round2 (2026-10-21)

### Entry conditions
- `tail -1 audits/policy_task/gap_waiver_cancellations_and_claims/_difficulty.md` = `VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN`.
- `tail -1 audits/render_source/gap_waiver_cancellations_and_claims/RENDER.log` = `RENDER round 3: DOCS OK`.
- `/tmp/erl0072_coord/kb_snapshot.sh gap_waiver_cancellations_and_claims gap` (execute only), run 2026-10-21T00:31:33:
  - check_docs DOCS OK; traceability TRACEABILITY OK with 0 misses; check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK.
  - gap.extended.yaml a718751875355d3a83095d05eec2cf7ad2a4a84d6684f7c316c7469ab0b78375 (changed since round 1); task_tools.py b862ea9d…bd0 (unchanged).
- Runtime views re-hashed: 0.runtime.json 9ad914b4…da55 and 1.runtime.json 46410545…1edf, both unchanged. Each equals its task's current `user_scenario` and `frozen_time`, so no persona drift.
- The task 0 world changed: the CPI tracking status, lapse date and a new first lapse notice. A fresh visible-context derivation was frozen first (runtime_context 0.md revision_2, sha 16224fe6…9d0d; 1.md revision_2, sha af5a9b37…a36). The task 1 world is identical.

### Round-1 items
| Item | Status | Evidence |
|---|---|---|
| CPI conditional (task 0) | settled | Plan B 500.00 published in `docs/cpi/7c8e0fa1`; derivation 500.00 / 1084.05 / 2646.07 equals GT |
| O1 whole months | closed | definition verbatim in the five computation documents |
| S1 March withdrawal | closed (not upheld) | gap.yaml: `gap_claim_withdrawn` targets `gap_addenda` (status transition); db_schema: no withdrawal event type in `gap_activities` |
| S2 CPI lapse | closed | world now lapse_notice / lapse_date 2026-09-18 / first notice 2026-09-21; consistent with `docs/cpi/dbab18db`, `c1be1044` |
| P1 factor-reads-factor | closed at factor level | `pd_proof_standing` ladder and `38716b6a` no longer refer to the other factor's insurer |

### Regression and new findings
- **K1 (KB-EXPLICIT RED, task 0):** `f9b2f5a7` step 2 now frames the computation document's standard inputs as slots ("Put generally … Here the insurer whose declarations are read is the insurer of the policy on file, and the proofs that count are those the tracking record shows as accepted"), in the two factor documents' own vocabulary. This tells the reader of the baseline that the insurer and the counting proofs vary, which pre-solves the search for `e1d56f59` and `38716b6a`. It is a new defect that came in with the P1 rework.
- **S3 (source-side, policy structure):** the round-11 combination sentence is a rule-level assembly over the outputs of `pd_policy_at_loss` and `pd_proof_standing`. It is outside the baseline and outside both ladders, so every one of its renderable homes meets a discreteness constraint. Reported without a remedy.
- Nothing else regressed. The diff of the full gap corpus against round 1 shows only the whole-months additions and the two reimbursement documents. The bijection holds for every changed atom, prerequisite sentences and tool homes are unchanged, and no seed or scored value appears in any document.
- Cross-category rows, one exhaustive pass over both worlds:
  - contract ledgers, VSC refunds and CPI rows (the latter now against the published CPI docs) all reproduce;
  - recovery and deficiency rows: none seeded.
  - The CPI-corpus retirements of the proof-effective refund clause and the acceptance-time deductible ceiling are noted as outside this audit's range.

### Per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | RED (K1) |
| 1 | PASS | PASS | PASS |

VERDICT kb_round2: task0=RED task1=PASS kb=K1 src=S3

## revision kb_round3 (2026-10-21)

### Entry conditions
- `tail -1 audits/policy_task/gap_waiver_cancellations_and_claims/_difficulty.md` = `VERDICT revision_14: task0=PASS task1=PASS charter=CLEAN`.
- `tail -1 audits/render_source/gap_waiver_cancellations_and_claims/RENDER.log` = `RENDER round 4: DOCS OK`.
- `/tmp/erl0072_coord/kb_snapshot.sh gap_waiver_cancellations_and_claims gap` (execute only), run 2026-10-21T01:28:25:
  - check_docs DOCS OK; traceability TRACEABILITY OK with 0 misses; check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK.
  - gap.extended.yaml 43a560911da6fbeeb99b9702128ce2c47f522d259eab69160b4788a5782dd093; task_tools.py b862ea9d…bd0 (unchanged).
- Earlier gated calls were answered BLOCKED: revision_12 and revision_13 were RED, the render was still round 3 and check_docs was NOT OK. Nothing was written then.
- Runtime views 9ad914b4…da55 and 46410545…1edf are unchanged and equal to each task's current `user_scenario` / `frozen_time` (no persona drift).
- Worlds are byte-identical to round 2. Task 0's reimbursement rule changed, so a fresh visible-context derivation was frozen first (runtime_context 0.md revision_3, sha b0c7e457…997b; 1.md revision_3, sha 5e1e0f09…b79b).

### Round-2 items
| Item | Status | Evidence |
|---|---|---|
| K1 (KB-EXPLICIT, `f9b2f5a7`) | closed | step 2 plain standard ("latest proof ... shows as accepted"), step 4 "The reimbursement maximum is 250.00"; no generalising frame, factor vocabulary or pointer |
| S3 (combination sentence) | closed | removed from the rule; insurer and proof standing merged into `pd_policy_at_loss` (`e1d56f59`), `38716b6a` deleted |

### Regression check (whole corpus)
- Changed gap documents since round 2:
  - the reimbursement set: `f9b2f5a7`, `e1d56f59`, `908aa1bf` (wording), `fd721c07` (new), `38716b6a` (deleted);
  - plus the hypothetical worked examples of `7d5da9df`, `fde6800d` and `c6625e52`. Their arithmetic was re-checked and correct, no rule text changed, and no seed or gold value appears.
  - Every other gap document is byte-identical, and the cpi, contract and vsc corpora are byte-identical.
- Prerequisite sentences and tool homes are unchanged. No seed or scored value appears in any document.
- GT unchanged: task 0 500.00 / 12363.73 / 1084.05 / 2646.07; task 1 14142.25 / 1027.96. Both equal the frozen derivations. Every reimbursement factor bears weight under the substitution test (250 / 250 / 250 / 1000 vs 500).
- Cross-category rows, checked once over both worlds: all reproduce (contract ledgers, VSC refunds, CPI rows against the published CPI docs). No repossession or deficiency rows are seeded.

### New items
- KB defects: none.
- **S4** (source-side, low, no KB effect): the reimbursement baseline names the factor's schedule ("the figure the Harborline GAP Waiver Premier 150 deductible reimbursement schedule sets for a comprehensive loss, 250.00"). The render carries only the figure.
- O3 (observation): the rule defines "the latest accepted proof of the policy on file", which no clause uses. The KB omits it, which is equivalent in entailment.

### Per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

VERDICT kb_round3: task0=PASS task1=PASS kb=CLEAN src=S4
