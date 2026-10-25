# worklog — hecm_line_draws_and_plan_servicing (env_0064), rework round 2

Scratch log: /tmp/hecm_line_draws_and_plan_servicing_0064/plan.md

Round-2 rework (audit: audits/policy_task/hecm_line_draws_and_plan_servicing/{_difficulty,0,1}.md):
- T0: new world (stopped check visible as a withdrawn draw request; loan past its first anniversary). Gold: void 6,276.25; payment release 34,867.38; draw ceiling 179,734.81.
- T1: world + 2026-09-14 annual reset (6.480 -> 6.610). Gold: restoration 1,933.62; designated amount 170,170.82; new payment 2,893.85 starting 2026-12.
- All six extended policies were rebuilt: HUD baselines for release/reset, every tier reachable, method factors change the formula's shape, the only roundings are the stated ones, overwrites are declared with scoped replaced_by, and each assembly is stated once.
- Full gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; CACHE-DIFF INFO; TRACEABILITY lists only the six unlock tool-name misses expected before render.
REWORK round 2: gates 7/7 green

Round-3 rework (audit revision_2: F-POL-7, F-FAC-3b, F-FAC-4b, F-FAC-4c, F-FAC-6b, F-XF-1; XF_recipe.md applied to all six policies):
- T0 gold: void 6,276.67; release 34,892.19; ceiling 179,759.62. T1 gold: restoration 1,933.62; designated amount 169,078.82; payment 2,757.72 from 2026-11 (T1 world adds a 588.00 flood advance on 2026-09-18).
- Every baseline paragraph defines every combined quantity with its standard value and states the combination once; every factor replaces or adds only its own quantity; solo and removal tests move every factor in its task world.
- process_payout_plan_change_72a1f37c now returns an error for the HECM Line of Credit or Fixed-Rate plan.
- Full gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; CACHE-DIFF INFO; TRACEABILITY only the six unlock tool-name misses (pre-render).
REWORK round 3: gates 7/7 green

Round-4 rework (audit revision_3: F-FAC-4d, F-FAC-6c, observations, same-day tie check):
- queued_request_earmark and designation_queued_hold relabelled parameter; the designation's inspection hold and the ceiling's inspection reserve are methods (schedule basis vs ledger basis).
- Ceiling insurance reserve covers hazard and flood; reset escrows no longer defined by reference to the designation; void accrual months counted as calendar months (no 1st-of-month over-count).
- Tie rules: stopped check by created_at; cured case = the case of the most recent cure confirmation notice; accruals and growth credits post once a month; one submitted change request at a time.
- All scored values unchanged (T0 6,276.67 / 34,892.19 / 179,759.62; T1 1,933.62 / 169,078.82 / 2,757.72).
- Full gate block: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; CACHE-DIFF INFO; TRACEABILITY only the six unlock tool-name misses (pre-render).
REWORK round 4: gates 7/7 green

Round-5 rework (renderer render_r1 findings):
- Draw ceiling: a new overwrite of the base first-anniversary sentence, scoped to ceiling-sized requests, states the whole-month count the compute uses (probe: a 2024-02-29 closing is still in its first year on 2025-02-28 and past it on 2025-03-01). Overwrite #1 restates the base first-year limit with hecm_msr_first_year_draws for every other draw; the ceiling's own first-year room is its only definition for ceiling-sized requests.
- Payment reset and designation apply only to a loan whose current plan pays no scheduled payments (no release arises, so the base processing order and "after any release" hold); process_payout_plan_change_72a1f37c returns an error for a loan already on scheduled payments.
- The whole-month convention is stated wherever whole months or years are counted (release, reset, restoration).
- No scored value moved; solo tests re-run; full gate block: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; CACHE-DIFF INFO; TRACEABILITY only the six unlock tool-name misses (pre-render).
REWORK round 5: gates 7/7 green

Round-6 rework (renderer render_r2 notes):
- The month-end convention ("whole calendar months … complete on the same day number, or on the first day of the following month when that day does not exist; whole years are twelve whole months") now sits inside every sentence that counts whole years or months: the release's age (in its overwrite and age sentences) and processing-credit months, the restoration's wait period, and the reset's overwrite age. The draw ceiling's anniversary sentence already carried it.
- restoration_grace_months was removed from the restoration's baseline params; it stays with the wait-period factor.
- Wording only: no scored value moved, no tool changed. Full gate block: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE, TRACEABILITY OK; CACHE-DIFF INFO.
REWORK round 6: gates 7/7 green
