# cni_contract_care — instantiation worklog (difficulty-level)

Per-task dossiers live in each task's `design_rationale`; this file records difficulty-level notes.

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[6, 6, 4]
- task 1: prerequisite_problems=3, factor_counts=[4, 6, 6, 4]

## Base-layer constraints routed around (blueprint untouched)
- The compute DSL reads only the target holding, its own event/intake tables, tier parameters and other
  categories; customer and premise fields (commercial_credit_grade, annual_kwh_usage, tags) are unreachable.
  Every factor therefore rests on contract fields, the contract's bill/deposit/notice ledgers and other
  categories' holdings and ledgers. The grade used at execution is read from the contract's posted deposit
  (credit_grade_basis), which base itself names as the grade that counts; the profile grade is a near-miss.
- The only customer-owned write that carries a computable number is a security deposit receipt (signing,
  renewal and termination writes carry dates the DSL cannot construct). Both user problems are therefore
  security remittances by the authorized signatory (termination security; anniversary review), split by
  subtype into two tools. The blueprint summary lists deposits among agent actions; the remittance itself is
  the business paying from its own account, so it is owner=user here.
- Base cni_etf counts remaining months with "+1 when the end day is later"; the DSL MONTHS() decrements instead.
  The base count equals 0 - MONTHS(contract_end_date, termination date), which compute uses verbatim-equivalently.
- replay gate treats "" in *_id fields as a dangling key: seeds and tools use null for empty references.

## Task 0 gate log (per task)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (closure 103 = init 103) / SOLVABILITY OK / COMPUTE OK
(3 comps, 16 factors, 4 cross-difficulty) / GROUNDING OK / SCOPE OK / CACHE-DIFF INFO (no cache field).
check_traceability deferred: needs the published KB.

## Task 1 gate log (per task)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK (closure 135 = init 135) / SOLVABILITY OK / COMPUTE OK
(4 comps, 20 factors, 1 cross-difficulty) / GROUNDING OK / SCOPE OK.

## Final difficulty-wide run (no --task)
EXTENDED OK; TASK TOOL CONTRACT OK (7 tools); REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means
branches=52.50, steps=18.50; history_rows_max=82; branches_max=53); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK.
check_traceability: deferred until the KB is rendered and published.

## Scope closure
task 0: cni_ext_termination_security (root, user) <- cni_ext_noticed_termination_damages (value_input),
        cni_ext_preflow_termination_damages (state_gate)
task 1: cni_ext_anniversary_security_review (root, user) <- cni_ext_passthrough_block_rebill (value_input),
        cni_ext_passthrough_index_rebill (value_input), cni_ext_contract_exit_damages (state_gate)
All 7 extended policies and 7 task tools claimed exactly once.

## Known soft spots for the audits
- The two line corrections carry a carrying-credit rate and a carrying-period convention (declared override of
  the base "billed minus correct" sentence) to reach the drawn four factors; they are the least natural factors.
- Cross-contract state gates (security waits on damages of other contracts of the same business) rest on a
  credit-desk ordering rather than on a value the security reads.

## Round 2 (policy-task audit, audits/policy_task/cni_contract_care/)
- F-1: cni_ext_preflow_termination_damages overwrite now also retires base cni_termination's clause
  "the early termination fee is computed on the full term per etf_preflow_basis." (replaced by its
  enrollment-stage months sentence).
- F-2 / F-5: cni_ext_passthrough_index_rebill rewritten to follow base holdover billing (all metered kWh on
  real-time index and holdover cycles; holdover adder unless waived for a missing or non-compliant expiry
  notice); only the partial-cycle block proration is a deviation, declared against cni_energy_billing.
- F-3 / F-4: the block-line policy became cni_ext_passthrough_fixed_price_rebill (block lines and fixed energy
  lines; new tool credit_fixed_price_line_5b24cf0d replaces credit_block_line_fffec1b8). Price ladder: keep the
  prior price / day-weight across the end of the owed notice period / new rate (declared override of the
  cycle-level cni_market_notices sentence); kWh ladder: prorated block on a partial cycle / block / metered kWh.
- F-6: enrollment_stage_months relabelled effect parameter (tiers are caps on term_months).
- F-7: carrying day-count removed as a factor (fixed 30/360 convention); fourth factor of both corrections is a
  repeat-error uplift read from rebill credits for other cycles; task 1 world gained a settled June 2026
  capacity correction.
- Task 1 finding 3: index_price_loading tier recorded as the smaller-share tier everywhere.
- Observations closed: O-1 (three-month tier wording now matches compute in both security policies);
  task 0 Limerick premise usage raised above the C&I minimum (small-business window kWh raised, pre-flow damages
  re-evaluated); task 0 rationale multi-source labels corrected.
- Gates (final, no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK,
  GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred.
