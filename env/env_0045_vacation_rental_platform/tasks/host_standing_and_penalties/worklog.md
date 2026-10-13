# worklog — host_standing_and_penalties (erl-task-instantiate, M=2)

## Step 0 — difficulty pre-check (2026-10-07)
- Draw (`draw_counts.py --tasks 2`):
  - task 0: prerequisite_problems=1, factor_counts=[6, 4]
  - task 1: prerequisite_problems=1, factor_counts=[4, 5]
- Category `host` (holding host_accounts, events host_account_events, intake host_appeals).
- Hard constraints discovered while reading the gates / DSL (they shape every design below):
  1. The compute DSL can read history only from host-owned tables (SUM/COUNT/MAX/LATEST are
     rejected on another category's table), and every cross read (CFIELD/XSUM/...) is scoped to
     rows whose customer_id is the host. A hosted stay belongs to its *guest*
     (stays.customer_id), so no computation of this difficulty can read a hosted stay's frozen
     amounts or dates. The cancellation-penalty base and the host-funded refund amount behind a
     host-fee refund are therefore not machine-computable here.
  2. host_cancellation_penalty_charged / _waived and host_account_reinstated declare triggers
     into payout with no `when`; per Principle D no task tool may write them.
  3. Every user (owner=user) act the blueprint names for hosts (appeal, closure, tax form) has no
     numeric field; a user problem's scored value is therefore either a categorical value or the
     one host-owned numeric record a host can accept in person (the Superhost travel credit).
  4. replay_tasks requires every seeded row to enter the read closure, and the customers finder
     may run only once (step 0): seeded guest customer rows can never be read, so seeded stays
     would need a null guest. Task 0 avoids stays entirely.
- Consequence: the claimable, computable, trigger-free host writes are host_tier_updated
  (variant_name), host_travel_credit_issued (amount), host_service_fee_refunded (amount, only
  where the refund base already sits on host-owned rows) and host_cancellation_recorded (band —
  rejected: notice factors would contradict the band enum names).
- Plan (headroom): task 0 = Superhost decision on an assessment held during an overturned
  suspension (agent, 4 factors) -> Superhost travel credit claim (user, 6 factors);
  task 1 reserved for the professional-tier / host-fee family (user enrollment into a
  professional tier + agent host-fee re-rating), which shares no policy, tool or event with task 0.

## Task 0 — closed
- Tree: host_ext_superhost_travel_credit (root, user tool claim_superhost_travel_credit_0d8c95c2, 6 factors)
  <- host_ext_superhost_redecision (agent tool apply_superhost_decision_f25b833f, 4 factors), value_input on tier_credit,
  state-form sentence "The travel credit for a run is fixed only after the account holds the host tier that its most
  recent Superhost assessment earns it."
- verify.py t0: S=Superhost (all factor baselines + full baseline = Standard Host); D=212.00 (factor baselines
  162/201/208/202/192/202, full baseline 109.00); D with the decision skipped = 0.00.
- Revision r1: rating-floor factor moved from summed listing quality review counts (rolling 365-day counts, double
  counting) to tenure (met assessments over the history); listing cross read dropped from the decision policy.
- Per-task gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK. check_traceability deferred (docs/ not rendered).

## Task 1 — closed
- Tree: host_ext_professional_fee_rerating (root, agent tool refund_rerated_host_fee_9248fd19, 5 factors)
  <- host_ext_professional_plus_enrollment (user tool enroll_professional_tier_a874e389, 4 factors), value_input on
  tier_pct, state-form sentence in the negated direction "A host service fee is not re-rated until the account holds
  the professional tier that its live listings and listing ratings qualify it for."
- verify.py t1: enrollment = Professional Host Plus (every factor baseline and the full baseline = Professional Host);
  re-rating = 46.71 (factor baselines 0.00/38.06/38.06/39.79/41.52, full baseline 0.00); without the enrollment 0.00.
- Revisions: r1 live-listing count method moved from "notice with open cure deadline" (contradicts the listing
  charter: suspension only after the deadline) to "registration-suspended listings with submitted reinstatement
  requests"; r2 four more June-September stays/assessments seeded so the business's fee ledger is credible (none is
  re-rated); persona detail on listings softened to facts the seed entails; task-0 persona no longer describes
  listings that are not seeded.
- Seeded hosted stays carry customer_id null: guest profiles cannot enter the read closure (the customers finder runs
  once, for the caller), so the guest is withheld from the host-side view.

## Difficulty-level closure
- Coverage: task 0 = {host_ext_superhost_redecision, host_ext_superhost_travel_credit}; task 1 =
  {host_ext_professional_plus_enrollment, host_ext_professional_fee_rerating}; scopes and tools pairwise disjoint;
  all 4 extended policies covered; each task has one user tool; prerequisite sentences use both directions.
- Final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite means
  branches 43.00, steps 11.50; history max 29; branches max 55), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
- check_traceability: TRACEABILITY NOT OK by design until docs/ is rendered — the only findings are the four hidden
  task-tool names, which reach the agent through the published KB (target_tool) once rendered.
- Known limits for the audits: the claimed penalty / waiver / reinstatement events are not instantiated (payout
  triggers, Principle D; hosted-stay amounts unreadable by the DSL); host_travel_credit_issued (claimed by no
  difficulty) carries the only numeric in-person host act.

## Rework round 2 (audit audits/policy_task/host_standing_and_penalties/)
- D-1 / T0-1 / T1-1 (undeclared override of base entry_gate / parameter meanings / measures): every published threshold is
  now kept (Superhost 4.80 / 90.00 / below 1.00 / 10 stays or 3 + 100 nights; Professional Host Plus 25 live listings /
  4.70). Factors moved from thresholds onto the figures compared with them, declared through the overwrites of the
  host_tier_assignment criteria sentence and Professional Host Plus clause (both name the measures). Task 0's 2026-Q4
  assessment is now recorded not_met (enum met / not_met respected) and the decision write records met / promoted on that
  record, so base host_msr_consecutive_met_quarters counts it; the credit rule reads the base measure and gates on it.
  Task 1's world rebuilt so the account genuinely reaches the published Professional Host Plus thresholds on those figures
  (26 counted live listings, listing rating 4.70; 26 listings, four 2026 quality rounds).
- Residual (cannot be routed inside this charter): the travel credit amount (212.00) still differs from the parameter
  meaning of superhost_travel_credit_usd ("Roamhaven travel credit issued after the required consecutive met
  assessments"). The credit is the only in-person host act in the host charter that carries a number; appeal, closure and
  tax-form acts carry none, and every tier move is pinned by an entry_gate. A credit fixed at superhost_travel_credit_usd
  cannot carry the six load-bearing factors the draw requires, so either the bonuses stay (this residual) or task 0 has
  no valid user problem. Needs a coordinator decision (accept the declared amount override, or allow structured base
  fields in `overwrite`).
- Observations closed: D-O4 (run gate in compute), D-O6 / T1-O3 (tier tools state which tiers they never set),
  D-O7 (edge condition), D-O8 (re-rating opening sentence in state form), D-O9 (decision keyed on "appeal stands
  approved"), D-O10 (precedence restated), D-O11 (assessment percentage restated), D-O12 (refund tool drops the
  host-fee base; 0.00 written), T0-O3 (credit accepted by the host stated in rule and persona), T1-O2 (complete 2026
  quality history), D-O14 / D-O17 (no published standard waived; clean-record floor removed). Unchanged by design:
  D-O1, D-O2, D-O3, D-O5, D-O13, D-O15 (now measure-level only), D-O16, T0-O2, T1-O1.

## Rework round 3 (validate_r1: frozen_time format)
- tasks/0.json frozen_time 2026-10-06T10:15:00 -> "2026-10-06 10:15:00 CDT" (Nashville host); tasks/1.json
  2026-10-06T14:30:00 -> "2026-10-06 14:30:00 PDT" (San Diego host). No other field referenced the old strings; every
  task tool and the compute DSL use only the date part (ctx.now()[:10] / NOW), so dates, quarters, windows and scored
  values are unchanged (Superhost / 212.00; Professional Host Plus / 46.71). validate_scenario: 0 errors for this
  difficulty. Full gate block re-run green (TRACEABILITY OK now that the KB is rendered).
