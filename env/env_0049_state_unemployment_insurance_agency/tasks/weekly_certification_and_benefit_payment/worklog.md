# Instantiate worklog — weekly_certification_and_benefit_payment (category claim), M=2

## Step 0 draw (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3, factor_counts=[4,4,4,4]
- task 1: prerequisite_problems=3, factor_counts=[5,6,4,5]

## Design snapshot (round 1, resumed)
Numeric acts available in the claim category are few (payments, supplemental, waiting week, entitlement credits,
certification figures, payment-method lead). Allocation (scopes pairwise disjoint):
- Task 0 (Extended Benefits on top of a regular claim paid short in its last week; Labor Day holiday-pay week):
  - claim_ext_parent_shortfall_supplement -> issue_supplemental_payment_38b81267 (agent, amount) [4 factors]
  - claim_ext_extension_entitlement -> determine_extension_entitlement_db601fac (agent, entitlement amount) [4]
  - claim_ext_holiday_pay_report -> certify_week_by_phone_ea18d1f2 (USER, other_pay_amount) [4]
  - claim_ext_extension_weekly_payable -> issue_extension_payment_613cfda4 (agent, amount) ROOT [4]
  - edges: root<-entitlement (value_input), root<-certification (value_input), entitlement<-supplement (state_gate:
    parent exhausted), certification<-entitlement (state_gate: EB claim active)
- Task 1 (regular claim after identity-theft re-verification; dependents added; held weeks):
  - claim_ext_dependency_redetermination -> record_dependency_redetermination_c7b3c182 (agent, credit) [5]
  - claim_ext_waiting_week_value -> record_waiting_week_428070c9 (agent, amount) [5]
  - claim_ext_payment_election_lead -> elect_payment_method_0e517696 (USER, lead_business_days) [4]
  - claim_ext_regular_weekly_payable -> issue_weekly_payment_6cd10c49 (agent, amount) ROOT [6]
  - edges: root<-waiting week (value_input), root<-redetermination (value_input), waiting week<-redetermination
    (value_input), root<-election (state_gate)

## Task 0 — closed (round 1)
- Reworked allocation: payments on Regular/CWC/EB programs carry state_chargeable / eb_shared codes whose
  charge:charge_benefit_posted trigger would write another category, so every payment of this difficulty is on a
  non-charged program (UCFE/UCX); the EB claim's own payments are not part of any tree (only its determination).
- Final tree: root claim_ext_extension_entitlement (EB determination on a UCFE parent) <- supplemental (action form,
  value_input) <- redetermination (value_input) ; supplemental <- redetermination (value_input), <- claimant's own
  election (state_gate). Expected: RD 18, EL 15, SUP 170.00, TD 7090.
- Gate fixes: history floor failed for EL/SUP (prenote new-account 3 -> 2; supplemental "already paid" split into the
  weekly payment read with LATEST plus SUMs of supplemental/reissue) -> all 7 per-task gates OK; validate_scenario run.

## Task 1 — closed (round 1)
- Tree: root claim_ext_regular_weekly_payable (UCFE week 2026-09-12) <- waiting-week value (value_input), <- dependency
  disallowance (value_input), <- claimant's own phone-line certification with holiday pay (value_input); waiting week
  <- disallowance (value_input); certification <- waiting week (state_gate, pins the order so the waiting-week value
  reads the first week). Expected: RED 135, WW 429.00, CT 73.26, WP 477.00.
- Backdating was dropped as a problem: a weeks-moved figure cannot carry 4-6 load-bearing factors (every cap is a min);
  replaced by the dependency disallowance (claim_entitlement_reduced).
- Fixes: threshold factors made load-bearing (W1 hours 17.0; W2 7.0 h with part-week fraction 0.2); a half-cent
  rounding tie in holiday pay removed (earlier-claim week 2026-02-21 earnings 227.50); history floor for the
  waiting-week value (week earnings read by SUM); 'waiver_pending' code token removed from rule prose.

## Final gates (difficulty-wide)
EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK;
CACHE-DIFF INFO (optional). check_traceability deferred until the KB is rendered. validate_scenario: only
"required document ... not found" errors for the 8 policy ids (KB not rendered yet) plus "not mentioned in any KB
document" warnings; no frozen_time or tool-source lint errors.

## Round 2 — rework of policy-task audit revision_1 (audits/policy_task/weekly_certification_and_benefit_payment/)
- F-1: claim_ext_dependency_redetermination.overwrite now also supersedes the base dependency-allowance sentence (replaced_by its per-dependent tier sentence).
- F-2: claim_ext_parent_shortfall_supplement.overwrite now supersedes the base other-pay sentence; the pension factor became a genuine method (small claimant-contributed pension: disregard of 0.10 x WBA, then the program share). Task 0 seed rebalanced (balance 152.00 -> 150.00, MBA 12032 -> 12030, BPW 36099.61 -> 36093.61) so the corrected supplemental (170.00 -> 168.00) still empties the parent; EB 7090 -> 7089.
- F-2b: claim_ext_regular_weekly_payable.overwrite now supersedes the base payable-amount sentence (replaced_by the allowance-paid tier).
- F-3: claim_ext_dependency_disallowance.overwrite now supersedes the base allowance and maximum-benefit sentences.
- F-4: waiting-week value follows base serving rules (program full-time threshold; not valued once the count is served); its own 36/34 figure is now an "hours base" for partial-week fractions only.
- F-5: the wage-cap fraction tiers state "entitlement credited already reaches the wage-capped amount" in the rule; compute tests exactly that (credits >= int(fraction x BPW)).
- F-6: waiting-week other-pay deduction stated in full in the rule (vacation/holiday in full, pensions at program shares, severance none) and implemented.
- F-7: other-verification tier reads the most recently verified case (XLATEST) and is stated as "no theft re-verification within the days and the most recent verified case within the days".
- F-8: payment_cycle_rounding tiers now different algorithms (round up to paper-check cycle / add card activation days / as counted); excess-rate factors (supplemental, waiting, weekly) and holiday_history_window relabelled parameter; supplemental gains the pension method, waiting week gains a prorating allowance method (429 -> 430).
- F-9: holiday-pay baseline rate is the wage-record rate only; the rate ladder's fall-through equals the baseline.
- F-10: EB measure tiers disjoint (any fraud -> zero; else net of the sum of established non-fraud principal, via XCOUNT/XSUM); integrity tiers rebuilt on balance due within a 12-month window (open -> 60, all repaid -> 40), disjoint.
- Overpay seed (task 1): claimant-error overpayment can never be waiver-pending; it is now repaid in full 2026-05-29 (status paid_in_full, balance 0, repayment ledger row), waiver-request row and its read removed (step replaced by a claim-requests read), persona updated. Integrity amount stays 40 (repaid tier).
- Observations closed: O-1 (rate tier needs latest-week hours, stated), O-2 (fraud test counts both fraud classifications), O-4 (conditions trimmed), O-7 (EB <- supplemental now state form, no fallback), O-8 (duplicate waiting wording removed from the weekly baseline), O-9 (only the MBA clause of the EB sentence superseded; minimum-weeks eligibility inherited), O-10 (pensions restored in weekly other pay), O-11 (training-week value stated in the EB baseline); task 0 persona no longer states the supplemental's payment method; false headroom figure and stale backdating note removed; task 1 false multi-source claim and over-broad recall-waiver line fixed. Not changed: O-3, O-5, O-6, O-12, O-13 (observations without a defect to correct).

## Round 3 — rework of policy-task audit revision_2
- R2-F1 (task 0, EB minimum-weeks eligibility unevidenced): claim_ext_extension_entitlement now declares in overwrite that the base
  clause "the claimant must show the minimum weeks of full-time base-period employment" is replaced by an extended sentence showing
  it through its wage equivalent (parent base-period wages >= 40 x the parent's weekly benefit amount, the federal EB alternative);
  compute returns 0 when the test fails; the EB-fraction tiers moved to a separate high-wage test (60 x WBA) so their fall-through
  stays reachable. Task 0 world evidences it on the parent claim row (36093.61 >= 18000.00); no persona answer needed; all
  values unchanged (EB 7089). Tracing, factor trace/tier_taken and rationale updated.
- R2-F2 (task 0 proof defect): edge_load_bearing[0] no longer claims the parent stays unexhausted (150.00 empties the 150.00
  balance); only the amounts differ.
- R2-O1, R2-O2, R2-O3: observations with no world consequence; left unchanged so task 1 (PASS in revision_2) is not regressed.

## Round 4 — rework of policy-task audit revision_3 (task 0 design_rationale only; task 1 and the charter untouched)
- R3-F1: problem-tree card "Deletion sensitivity" no longer says the parent is not exhausted when the redetermination is skipped; it
  now repeats the corrected prerequisite_closure entry (150.00 empties the 150.00 balance, parent exhausted either way).
- R3-F2: factor card TD eb_fraction line now names the current tier (long-claim weekly payments AND base-period wages >= 60 x WBA)
  with its evidence (31 weekly payments; 36093.61 >= 27000.00).
- R3-O1 and earlier observations: no world consequence; left unchanged.

## Round 5 — policy-side items from audits/policy_kb and audits/runtime_context (no scored value moved; tools unchanged)
- Weekly full-time threshold (rule vs compute): the weekly payment's threshold factor sentence now states the threshold is both
  the hours at which the week pays nothing and the base of the partial-week fractions, matching compute `hours >= thr`; the
  vacuous `gross_q >= 0` term is gone (the allowance-paid tier now reads the week's hours through its own binding).
- Child-support order lookup without a claim filter: the disallowance rule now speaks of any current-support order binding the
  claimant on any of the claimant's claims, counted by status (XCOUNT active+suspended / requested), with disjoint tiers.
- Verification-days lookup: both tiers read the most recently verified case (XLATEST), the first of re-verification cases, the
  second of whatever pathway — rule text changed to match.
- Holiday-pay baseline listing min_hours: removed from baseline.params (it lives in the rate ladder).
- Redetermination/disallowance computations listing the weekly benefit amount: the `wba` binding is now owned by the
  allowance-ceiling factor in both policies (the standard method never reads it).
- EB computation lacking the training-week default: the baseline sentence now states the training addition as a step
  (zero weeks, each valued at the weekly benefit amount, so the addition is zero).
- Stale "classification penalty share" note: replaced by what the compute reads (fraud count, sum of established non-fraud principal).
- Task traces/rationale updated (tier texts, binding names). KB-EXPLICIT "before any other limit" is the renderer's item;
  facet residues of base parameter descriptions are frozen (coordinator).
