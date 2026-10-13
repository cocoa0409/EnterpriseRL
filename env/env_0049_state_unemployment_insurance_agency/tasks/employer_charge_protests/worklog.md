# employer_charge_protests — instantiation worklog (M=2)

Full per-task dossiers are in each task's `design_rationale`. This file is the summary.

## Draws (draw_counts.py)
- task 0: prerequisite_problems 1, factor_counts [6, 4]
- task 1: prerequisite_problems 1, factor_counts [5, 4]

## Claims (pairwise disjoint, together cover all 4 extended policies)
| task | root (agent) | prerequisite (user) | edge |
|---|---|---|---|
| 0 | charge_ext_protest_relief_credit / grant_charge_protest_0f56e95e (4 factors) | charge_ext_protest_amount / file_charge_protest_73ec7ae2 (6 factors) | value_input, state form, "only after" |
| 1 | charge_ext_response_relief_credit / determine_charge_relief_e2b9af19 (4 factors) | charge_ext_response_disputed_amount / submit_separation_response_153a3a70 (5 factors) | value_input, state form, "not ... until" |

Cross-difficulty evidence comes from taxacct in both tasks: the reimbursement bill, interest, payment and amended wage reports in task 0, and (after round 2) the tax account class with its reserve credits in task 1.

## Gold values
- task 0: protested_amount 274.88, relief_credit_amount 272.16 (baseline results 0.00 / 0.00)
- task 1: disputed_charge_amount 345.60, relief_credit_amount 345.60 (baseline results 0.00 / 0.00); before round 2 both were 295.49

## Schema constraint noted
charge_requests has no amount column. The user-side amounts (amount protested, disputed charge amount) are therefore carried by the submission reference, which is minted from every argument, and echoed in the receipt. A wrong amount still yields a different row and a different terminal hash.

## Revisions
1. A dangling FK came from employer_tax_ledger.account_request_id = ''. It is now null.
2. Quantity names collided at the prose layer: support share, standing share, promptness share, and "relief reach". Each was renamed so it is unique to one policy.
3. The R0 netting tier wording was aligned with compute: "credits for cancelled payments ... but none for a recovered overpayment".
4. Task 1 tax ledger: late-payment interest was added for the two late-paid quarters.

## Final gate run (difficulty-wide)
EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (59/59, 44/44 closure), SOLVABILITY OK, COMPUTE OK (branches mean 28.50, steps mean 14.50, history_rows_max 48, branches_max 34), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
check_traceability is deferred until the KB is rendered. validate_scenario's only errors are "required document not found", because no documents have been rendered yet.

## Rework round 2 (audits/policy_task/employer_charge_protests: _difficulty.md, 0.md, 1.md)
The base is untouched. Every change is in charge.extended.yaml, tasks/0.json or tasks/1.json. Scratch scripts were kept in /tmp/rw0049_ch and removed afterwards.

- **F1 / T0-1 (two readings of "since that quarter").** The credits_taken_out rule, ladder and compute_basis now say "credits posted on the position in a quarter other than the statement's quarter". The rule gives the reason: credits in the statement's own quarter are already netted in what was billed or posted. Tier 2 now reads "no recovered-overpayment credit outside that quarter, but cancelled-payment credits", and tier 3 reads "otherwise". Compute bindings were renamed to *_outside, so the rule is exactly equivalent to compute. Gold 274.88 is unchanged, and the 0.json tracing no longer relies on an "after" reading.
- **F4 / T0-2 (unreal reserve-interest tier).** The protest_interest_rate factor (with 0.005 reserve interest) is removed, along with params reserve_interest_rate and no_interest_rate. Its replacement is protest_interest_basis (method, cross-difficulty taxacct), with three tiers:
  1. Interest assessed for the quarter: the latest assessed month × protested principal / amount billed.
  2. None assessed yet, reimbursing, and the bill is past due: principal × the class late-payment rate.
  3. Otherwise: none.
  Protest interest = RND(monthly × interest months). W0 still gives 39.08 × 272.16 / 3,908.10 = 2.72, so the total is 274.88. Counts are still 6 (4 method, 2 parameter). Sensitivity is 272.16.
- **F5 / T1-1 (late-report standing shares).** Both standing shares are removed. Task 1's cross-difficulty factor is now response_financing_basis (method, multi-source, taxacct). For a contributory account whose reserve has been credited with contributions, the counted charges reach that reserve. For a reimbursing account that has been billed, the measure is the billed amount. Otherwise it is nothing. The persona's late-report line and the matching required_user_input were dropped. EC8, EC9 and EC10 now give the tax-account reads their real role.
- **F6 / T1-2 (5-day tier inside the window).** Removed. The new parameter factors follow only the timeliness rule in the base:
  - answer_window_share: within the window → 1.00; late while still noticed → 0.90; lapsed → 0.
  - relief_answer_share: on time or late with good cause → 1.00; late without good cause → 0.90; no response → 0.
  The other new parameter factors come from the class relief grounds:
  - response_class_share: separation-ground class → 1.00; part-time-only class → latest charge ÷ counted; otherwise 0.
  - relief_ground_share: reported ground allowed → 1.00; part-time → latest charge ÷ window; otherwise 0. It absorbs the old relief_reach and is multi-source.
  Draw [5,4] is now the disputed amount with 5 factors and the relief with 4. Gold changes from 295.49 to 345.60 in both writes, which is the whole remaining charge, as a real voluntary-quit relief would be. Total charged ends at 0.00. The task-1 JSON was updated to match: gold args, objectives, expected values, factor_trace, factor_sensitivity, tracing, prerequisite_closure, business_effect and design_rationale.
- **F2 (undeclared override of the late-response bar).** Both relief policies now declare an overwrite of charge_evt_notice_and_response, "otherwise payments issued before the late response stay charged even if relief is later granted". It is replaced by their answer-abatement or answer-share sentence.
- **F3 (remaining-charge cap).** The protest relief credit is now MN(…, charge still standing on the position). The rule, basis and compute were updated, and the credits_deducted sensitivity is now 340.20. The response relief nets every standing credit by construction, so it can never exceed the standing charge. The rule says so instead of adding a cap that would hide credits_netted.
- **O1 (protest baselines always 0.00).** Kept, with a stated reason. A wage-record protest with no amended report on file has no documented amount. The baseline is definite and differs from gold.
- **O2 (synthetic haircut values 0.80 / 0.90).** Kept, and the same convention is used for the task-1 answer shares. The conditions are ones the business weighs; the values are this policy's own params.
- **O3 (reports counted, rule said "cover quarters").** The wage-record relief share rule and ladder now say "number at least four / one to three", matching XCOUNT.
- **O4 (status missing from the prerequisite sentence).** The sentence now reads "carries a pending written protest of the statement". The policy_source, 0.json design_rationale and prerequisite_closure were updated.
- **Scope observation (charge_chargeability_determined and charge_protest_denied have no policy).** Not changed. No extended policy computes a value on those events, and every claimed event used by the two trees is covered.

Gate run after round 2:
- EXTENDED OK; TASK TOOL CONTRACT OK
- REPLAY OK (0.json 14 acts, closure 59 = 59; 1.json 15 acts, closure 44 = 44)
- SOLVABILITY OK
- COMPUTE OK (0.json factors 10, cross 5, history 48, branches 37; 1.json factors 9, cross 1, history 7, branches 25; suite means 31.00 / 14.50)
- GROUNDING OK; CACHE-DIFF INFO; SCOPE OK
- check_traceability is deferred: it fails only on the task tool names that the KB will expose once it is rendered.
- validate_scenario: tasks_ok 10/10; the only errors are the pre-render "required document not found" ones. No forbidden tokens in task_tools.py, which was not edited. frozen_time formats are unchanged.

## Rework round 3 (audits/policy_task/employer_charge_protests: revision_2 sections of _difficulty.md, 0.md, 1.md)
Task 0 was PASS in revision 2. Its world, gold, factors and sensitivities are untouched; the only change is the R2-O1 wording below. Scratch was kept in /tmp/rw0049_ch3 and removed afterwards.

- **R2-F1 (response_class_share fall-through reached by no class).**
  - Tier 1 now requires "the position charges a regular or combined wage claim and its class allows relief for a quit, misconduct and refused work". The compute adds `'Extended Benefits' not in F('variant_name')`.
  - The fall-through (0) is now the Extended Benefits state-share class, whose relief follows the determination on the regular claim. That class is a real charter variant, so the fall-through is reachable.
  - The baseline rule names that tier. W1 stays on tier 1 (1.00); its baseline result is still 0.00.
- **R2-F2 (answer_window_share fall-through unreachable at a response write).**
  - The "position no longer awaiting / 0.00" tier is gone. The ladder is now: within the window → 1.00; after the due date with no benefit charge posted after it → 0.90; otherwise (after the due date, with a charge posted after it) → 0.75.
  - The baseline is that reachable late tier (0.75). W1 (on time) takes 1.00, and its baseline result is 259.20.
- **R2-F3 (relief_answer_share fall-through "no response on record"; the baseline contradicted the prerequisite).**
  - The ladder is now: on time or late with good cause → 1.00; late without good cause and no charge after the due date → 0.90; otherwise → 0.75 (baseline).
  - The baseline rule now describes a determination on a response that was received late. The late-response bar overwrite was restated to match.
  - W1 takes 1.00, and its baseline result is 259.20.
- **R2-T1-2 (no near-miss).**
  - W1's notice is now mailed 2026-11-03 (one business day after the 2026-11-02 filing), so the response is due 2026-11-13. Frozen time is 2026-11-13 14:35 CST, a Friday, and the persona's weekday was updated to match.
  - The response therefore lands on the inclusive tenth day. Counting the mailing day as day one would make it late (0.90), which gives one near-miss in each computation.
  - Gold is unchanged at 345.60 / 345.60. Traces, tracing, solvability boundary_check, seed_consistency and design_rationale were updated.
- **A tried-and-dropped alternative.** I first moved W1 to a response two days late. check_solvability then requires `satisfied: true` for the response_window base gate at the response write, so a late response cannot be gold. I reverted that world.
- **R2-O1 (task 0, "already netted" aside false for the listed-charges tier).** The aside was removed from the credits_taken_out rule and from the credits_in_quarter basis. The operative sentence is unchanged, and task 0's numbers are unchanged (274.88 / 272.16).
- **R2-O2, R2-O3, R2-O4, O1, O2, scope observation.** Left as observations, unchanged.
  - R2-O2 is inert without a bill.
  - R2-O3 does not apply when a single charge stands.
  - R2-O4: the reserve-credit condition keeps the financing basis tied to seeded reserve credits.
- **Observation (design_rationale miscount).** "employer_tax_ledger (26)" is corrected to 24.

Gate run after round 3:
- EXTENDED OK; TASK TOOL CONTRACT OK
- REPLAY OK (0.json 14 acts, 59 = 59; 1.json 15 acts, 44 = 44)
- SOLVABILITY OK
- COMPUTE OK (0.json factors 10, cross 5, history 48, branches 37; 1.json factors 9, cross 1, history 7, branches 27; suite means 32.00 / 14.50)
- GROUNDING OK; CACHE-DIFF INFO; SCOPE OK
- check_traceability is deferred: it fails only on the four task tool names, which have no source until this difficulty's KB is rendered.
- validate_scenario: tasks_ok 10/10, documents 82. The only errors are "required document not found"; this difficulty's four policies are not rendered yet.

## Rework round 4 (revision_3 sections of _difficulty.md, 0.md, 1.md)
Task 0 is untouched: PASS in revision 3, with no file content of its own changed. No scored value moved in either task (274.88 / 272.16; 345.60 / 345.60). All factor sensitivities and baseline results are unchanged. Scratch was kept in /tmp/rw0049_ch4 and removed afterwards.

- **R3-T1-1 (proof field names a relief-answer-share "zero tier" that no longer exists).**
  - tasks/1.json prerequisite_closure.edge_load_bearing[0].skipped_effect and design_rationale [2] now state the actual skip-world mechanism.
  - The ground share takes its zero tier because no response reports a ground. The relief answer share stays at the whole because no late answer is on record.
  - Result: RND(MX(0, 691.20 x 0.00 - 345.60) x 1.00) = 0.00, compared with 345.60.
- **R3-O1 (baseline narratives describe a standard case that cannot exist).** Both response policies' baseline sentences, in the rule and in baseline.rule, now list each default value with its own reason instead of one joint "standard response/determination".
  - Disputed amount: no charge counted, financing basis nothing, nothing left out, response class share 0 (as on an Extended Benefits state-share position), answer window share 0.75 (as for a late answer after a payment was charged while overdue).
  - Relief credit: relief window no charge, nothing netted, relief ground share 0 (as for a reported separation earning no relief), relief answer share 0.75 (as for a late answer without good cause after a payment was charged).
  - Each paragraph still gives the definite 0.00.
- **R3-O2 (base lapse vs late response).** Left unchanged. The tension is inside the frozen base, and task 1's response is timely, so it is not exercised.
- **O1, O2, R2-O3, R2-O4, scope observation.** Left unchanged, as observations.

Gate run after round 4:
- EXTENDED OK; TASK TOOL CONTRACT OK
- REPLAY OK (0.json 14 acts, 59 = 59; 1.json 15 acts, 44 = 44)
- SOLVABILITY OK
- COMPUTE OK (0.json factors 10, cross 5, history 48, branches 37; 1.json factors 9, cross 1, history 7, branches 27; suite means 32.00 / 14.50)
- GROUNDING OK; CACHE-DIFF INFO; SCOPE OK
- check_traceability is deferred: its only 4 findings are the task tool names, which have no source until this difficulty's KB is rendered.
- validate_scenario: tasks_ok 10/10, documents 132. The only errors are "required document not found"; this difficulty has 4 of them.

## Rework round 5 (audits/policy_kb/employer_charge_protests, audits/runtime_context/employer_charge_protests)
Both KB audits passed both tasks; they recorded policy-side items P1–P4. Every edit is in the extended section of charge.extended.yaml; the base section and blueprint/ are untouched. Tools, signatures and docstrings are unchanged. No scored value moved (274.88 / 272.16; 345.60 / 345.60), and all sensitivities and baseline results are unchanged. Scratch was kept in /tmp/rw0049_ch5 and removed afterwards.

- **P2 (monthly protest interest: the rule divided by the billed amount without a guard).** In charge_ext_protest_amount, tier 1 of the rule, the protest_interest_basis ladder and compute_basis now read "interest assessed for the statement's quarter **and an amount billed for that quarter**". This matches the compute's `billed_for_quarter > 0`. Where interest is assessed but nothing was billed, both rule and compute now give "nothing otherwise".
- **P3 (interest months: the rule said "the bill was paid", the compute used the latest payment of any component).**
  - Rule, ladder and basis now say "the latest payment applied to the reimbursement bill for the statement's quarter was received after the bill's due date" and "no payment has been applied to that bill".
  - The compute `bill_paid_on` now filters `component='reimbursement'`. The inputs and the cross_category reads now declare employer_tax_ledger.component.
  - In W0 this is the same 2026-11-19 payment, so the result stays at 1 month.
- **P1 (the retired late-response bar is still encoded by the base variant term relief_bar_for_payments_before_late_response).** The base term was not edited. Each relief policy's rule now states how that term reads under the retired clause, and overwrite[2].replaced_by now carries that sentence:
  - Protest decision: "For a protest decision the class term that payments issued before a late response stay charged even if relief is later granted is applied only through the answer abatement: … no payment is kept charged on that account beyond it."
  - Response determination: the same sentence, applied only through the relief answer share.
- **P4 (the kept base clause "an appeal decision relieving the employer credits as a relief does" points at a retired clause).** Each relief policy's rule now adds "This replacement governs only the relief credit of a protest decision / of a determination on a separation response; a relief that an appeal decision grants still credits the whole remaining charge of every posting within the relief's scope." overwrite[1].replaced_by (charge_evt_credits) now carries the formula sentence plus this sentence; the two are consecutive and verbatim in the rule.
- design_rationale in both task JSONs got a one-line revision note. No other task field changed.

Gate run after round 5:
- EXTENDED OK; TASK TOOL CONTRACT OK
- REPLAY OK (0.json 14 acts, 59 = 59; 1.json 15 acts, 44 = 44)
- SOLVABILITY OK
- COMPUTE OK (0.json factors 10, cross 5, history 48, branches 37; 1.json factors 9, cross 1, history 7, branches 27; suite means 32.00 / 14.50)
- GROUNDING OK; CACHE-DIFF INFO; SCOPE OK
- TRACEABILITY OK (0.json 22 copied / 0 missing; 1.json 23 / 0)
- validate_scenario: VALID (5 difficulties, 10 tasks, 10 ok, 55 tools, 321 documents)

## Rework round 6 (revision_5 of audits/policy_task/employer_charge_protests)
Only proof text in tasks/0.json changed. charge.extended.yaml and task_tools.py were not touched; their hashes are unchanged (ebe9951a25d999b5… / 811d5e08b5df06bf…), so the re-rendered KB stays valid. No scored value or sensitivity moved. Scratch was kept in /tmp/rw0049_ch6 and removed afterwards.

- **R5-T0-1 (false quotient in the protest-interest trace).** "39.08 x 272.16 / 3,908.10 = 2.7216" is corrected to 2.72153 (the true value is 2.721530…), together with the "RND(2.7216 x 1)" steps that follow it. That makes six substitutions in four fields:
  - design_rationale [5] (factor card and arithmetic line)
  - evaluation_criteria[11].argument_uniqueness_tracing.protested_amount (quotient and RND step)
  - computations[0].factor_trace[5] (protest_interest_basis)
  - computations[0].factor_trace[6] (plumbing)
  The scored value is unchanged: RND(2.72153 x 1) = 2.72, so the total stays 274.88.
- **Sweep of trace arithmetic in both tasks.** A script evaluated every "expression = figure" in the proof text of tasks/0.json (18 equations) and tasks/1.json (9 equations), at the precision each figure is stated. It found 0 mismatches after the fix; run on the pre-fix backup, it flags the old 2.7216. I also checked the worded multiplications by hand and found no other slip:
  - payment x share 0.7000 / 0.8000 x regular share
  - 4,286.10 x 0.80 capped at 340.20
  - 340.20 x 0.80
  - 691.20 x 0.00 - 345.60

Gate run after round 6:
- EXTENDED OK; TASK TOOL CONTRACT OK
- REPLAY OK (59 = 59; 44 = 44)
- SOLVABILITY OK
- COMPUTE OK (0.json factors 10, cross 5, history 48, branches 37; 1.json factors 9, cross 1, history 7, branches 27; suite means 32.00 / 14.50)
- GROUNDING OK; CACHE-DIFF INFO; SCOPE OK
- TRACEABILITY OK (0.json 22 / 0; 1.json 23 / 0)
- validate_scenario: VALID (5 difficulties, 10 tasks, 10 ok, 55 tools, 321 documents)
