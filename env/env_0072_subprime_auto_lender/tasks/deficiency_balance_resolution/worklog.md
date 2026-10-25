# worklog — deficiency_balance_resolution (env_0072)

## Relaunch (round 1)
- Carried on from predecessor's plan.md, task_tools.py (2 tools) and scratch computes.yaml/world.py.
- Revised design against audits/render_source/XF_recipe.md: replaced the predecessor's recovery-expense carve-out
  (a tier selecting the base a rate acts on) and the "extension beyond band max" count factors; all settlement figures stay
  at or above the base band minimum, so L/S/I declare overwrite []; R/P declare scoped overwrites of deficiency_payment_plan.
- Policies authored as sentence lists (scratch spec_t0.py / spec_t1.py) so every compute_basis quote is the rule sentence
  verbatim; gen_yaml.py appends extended_policies to the base charter text unchanged.
- Subjects chosen so base eligibility is satisfiable at the write: R/P deficiency_payment_posted (posting_account_status),
  L/S deficiency_settlement_waiver (policy_scope of deficiency_settlement), I deficiency_settlement_started
  (settlement_offer_accepted + settlement_offer_in_time).
- Task tools added: record_lump_sum_settlement_offer_7c3d7537, accept_installment_settlement_d1722676 (user),
  start_installment_settlement_185f50ba. TASK TOOL CONTRACT OK after each addition.

## Task 0 (Renata Szabo) — draw prerequisite_problems=1, factor_counts [5, 6]
- Values (build_t0.py, check_compute build_env + real tool writes): restart down payment 336.34 (baseline 558.22),
  plan installment 122.41 (baseline 131.15; with the down payment skipped 133.75).
- Symptom -> fix log:
  - check_extended: paydown factor read only F fields -> rebuilt from the ledger (posted + credits - returned).
  - check_extended: I's prerequisite sentence carried the token offer_status -> reworded ("an installment settlement offer
    that the borrower has accepted").
  - replay: empty-string arrangement_offer_id counted as a dangling FK -> seed and pay tool use null; dealer rows were
    unread noise -> dropped, contract dealer link null.
  - solvability: intent_source.kind must be user_scenario; gate evidence must list the account id path.
- Per-task gates task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## Task 1 (Marcus Thornbury) — draw prerequisite_problems=2, factor_counts [5, 6, 5]
- Values: lump-sum offer 3797.68 (baseline 3675.18), installment settlement 5361.92 (baseline 4614.39; lump-sum offer
  skipped 1564.24), settlement installment 1340.48 over 4 (baseline 893.66 over 6; acceptance skipped 2041.77).
- Symptom -> fix: solvability rejected 'variants.settlement_offer_valid_days' as temporal evidence -> cite the account's band row.
- Per-task gates task 1: all 7 OK.

## Cross-task review (manual value gates)
- Rewording pass after reading the generated rules: assembly sentences made generic (no factor quantity named), with the
  replacement-first order stated ("A schedule that replaces the standard ... is applied first"); every factor states its own
  whole-month convention; baseline paragraphs carry the read sentences they need (lump-sum figure; settlement amount);
  P gained "A plan offer states no down payment of its own ..." so the offer's down_payment_usd 0.00 is a stated rule.
- Decoy / absent-record probes run on scratch copies (results quoted in each design_rationale): window edges at exactly
  12 / 6 whole months exclude; older broken arrangement ignored by the latest-broken read; returned contract payment
  subtracted; sale-proceeds contract payment not counted; expired payment-plan offer not a lapsed settlement offer; a
  lump-sum offer dated yesterday is not today's figure; absent accepted settlement -> whole balance; absent
  last_payment_date -> idle days from opening.
- Shape tables (all pairs differ by an input or an operation): make_good_addition, installment_basis_method,
  hardship_reduction_method, premium_method, count_method (tables in each design_rationale).
- Base-minimum check: every settlement figure in the whole domain stays >= the band minimum (surcharges only; hardship lowers
  by at most hardship_extra_discount_pct points; count only <= max_settlement_installments) -> L/S/I overwrite [].
- Scope: task 0 = {R, P} + {pay_restart_down_payment_04892a83, record_payment_plan_offer_3f4fb3a9}; task 1 = {L, S, I} +
  {record_lump_sum_settlement_offer_7c3d7537, accept_installment_settlement_d1722676, start_installment_settlement_185f50ba};
  disjoint, covering all 5 policies / 5 tools; each task has one owner=user write.
- Scratch authoring scripts deleted at the end of the run (coordinator rule); scratch data files kept.

## Final gates (no --task)
- EXTENDED OK
- TASK TOOL CONTRACT OK
- REPLAY OK
- SOLVABILITY OK
- COMPUTE OK (suite means branches 46.00, steps 14.00; history_rows_max 24; branches_max 57)
- GROUNDING OK
- SCOPE OK
- (CACHE-DIFF INFO only; check_traceability waits for the rendered KB)

REWORK round 1: gates 7/7 green

## Round 2 (policy audit revision_1: task0 PASS, task1 RED; charter R-ABSENT, R-TIE, R-MONTHEND)
- Charter edited in place with a scratch script that substitutes each changed sentence across rule, compute_basis,
  baseline.rule, replaced_by and policy_source (quotes stay verbatim); base copy untouched.
- P4 absent lump-sum offer -> base band minimum; P5 absent acceptance -> nil, edge re-declared state_gate; MAX reads replace
  LATEST(created_at); explicit whole-month count in every month sentence; tie fact in P2/P4/P5; negative-count and
  missing-figure tiers worded.
- Re-evaluated both tasks at handling time: all gold values, factor substitutions and baselines unchanged; factor_trace
  plain lines regenerated; task 1 closure (edge kind, flips, load-bearing) and design_rationale §8/§9/§11/§12 rewritten;
  task 0 §12 added. Probe table appended to plan.md. Claims in rework_claims_r2.md.
- Final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Scratch scripts deleted.
REWORK round 2: gates 7/7 green

## Round 3 (policy audit revision_2: task0 PASS, task1 RED; charter R-ABSENT P4 changed form, R-BASELINE)
- P4 no-offer state -> nil, no installment settlement offered (one answer with its prerequisite sentence); si_band_min removed; effect text fixed.
- Tie fact moved from P4/P5 baseline.rule into the premium / count method sentences; P5 nil sentence split from the baseline read sentence.
- Task 1 proof text and closure rewritten; plain trace lines regenerated; gold, factor substitutions and baselines re-verified unchanged; task 0 untouched.
- Final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Scratch scripts deleted.
REWORK round 3: gates 7/7 green

## Round 4 (policy audit revision_3: task0 PASS, task1 PASS; charter R-SHAREDCONV in P2)
- P2 tie statement moved from a standalone sentence into its two broken-arrangement factor sentences (basis method, rebreak surcharge); quotes regenerated verbatim; no compute or value change.
- Sweep: no other standalone convention sentence serves several factors.
- Task 1 careless-error label corrected (whole baseline, not base minimum); §14 added.
- Final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Scratch scripts deleted.
REWORK round 4: gates 7/7 green

## Round 5 (render_r1: STOP on RED-1; low note on empty last_payment_date)
- Lump-sum rule: hardship document order ssa_award_letter > medical_disability_statement > unemployment_determination; worlds and GT agree.
- Installment settlement rule: idle days counted from opened_date when last_payment_date is empty (= compute).
- Selection sweep: settlement installment rule now names the offer the settlement starts under (the one its largest accepted amount comes from); no other member.
- Quotes regenerated verbatim; task 1 tracing quote and §15 updated; no figure moved.
- Final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Scratch scripts deleted.
REWORK round 5: gates 7/7 green

## Round 6 (KB audit kb=CLEAN, src=S1..S5)
- S2/S3: cross-product rows re-priced by the published contract/recovery docs; one exhaustive pass over every other-product row of both worlds (all other rows matched). S5: lump-sum hardship-document rule fixed (handed-in document recorded; reduction reads earlier offers only).
- Deficiency histories and gold rebuilt in date order; texts swept (figure scan), probes re-run, traces regenerated. S1/S4 no action.
- Final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (TRACEABILITY OK as well). Scratch scripts deleted.
REWORK round 6: gates 7/7 green

## Round 7 (policy audit revision_6: both tasks PASS; charter R-HANDIN)
- Lump-sum hardship-document sentence: stated order applied to handed-in documents too (one sentence). O16/O17 left as observations.
- Final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Scratch scripts deleted.
REWORK round 7: gates 7/7 green
