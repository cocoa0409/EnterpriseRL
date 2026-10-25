# Policy-task audit — resident_trust_fund_accounts / charter-global

## revision_1

## charter_global_frozen
- auditor: independent policy-task auditor (erl-task-policy-audit), round 1, 2026-10-22. This file replaces the stub left by a cut-off predecessor (header + entry conditions only, no findings); nothing of it is relied on.
- `trust.extended.yaml` sha256 5b3d8426d8bda586f91aea9ae724df42a24f361570366da6bf5af1661aa8ea68 (matches coordinator snapshot)
- `task_tools.py` sha256 d7502b01771ab1827810bf13b9e7170e13a44576a8728c3866de659222d5f7ef (matches coordinator snapshot)
- masked views: task0.view.json 0b5a3bf2…8c94, task1.view.json 04a6e5e1…66ed (both re-hashed, match the brief)
- read for this section: blueprint/blueprint.yaml (scope only), blueprint/products/{trust,ancillary,bedhold,medicare,medicaid,private}.yaml (targeted sections), blueprint/share_tools.py (signatures: all reads plus verify/hand-off), blueprint/db_schema.json (medicare_ledger fields), the extended charter, task_tools.py, audits/render_source/XF_recipe.md, the gate snapshot, skills/erl-task-instantiate/scripts/check_compute.py (DSL semantics only).
- masked / unread before the freeze: tasks/*.json, tasks/resident_trust_fund_accounts/worklog.md, plan.md, every other file under audits/, every other env.
- Entry conditions: gate snapshot supplied (7 gates rc=0, traceability deferred), masked views + hashes supplied → entry conditions met.
- Scratch (outside the write domain, read-only use): /tmp/erl0074_pta_trust/{sweep.py,evalc.py,t0.py,t1.py} — compute_basis/baseline/prerequisite sweep and a DSL replay harness built on check_compute.build_env.
- Nothing in this section is derived from any revealed GT (written before either task's reveal).

### policy_conflict_scan
- Base section (lines 1–1136) is byte-identical to blueprint/products/trust.yaml (`diff` empty).
- Six extended policies: P1 trust_ext_covered_service_return (return_improper_transfer_e2970e4f, agent), P2 trust_ext_ancillary_authorization_amount (sign_bill_payment_authorization_74e4ddf9, user), P3 trust_ext_patient_pay_transfer (post_patient_pay_transfer_45809d6d, agent), P4 trust_ext_bed_hold_transfer (post_bed_hold_transfer_446aaea8, agent), P5 trust_ext_coinsurance_transfer (post_coinsurance_transfer_51d626ac, agent), P6 trust_ext_spare_withdrawal (sign_withdrawal_request_c6615816, user).
- Graph: P2 ← P1; P6 ← P3, P4, P5. Two disjoint trees {P1,P2} and {P3,P4,P5,P6}; together they cover all six policies once → M=2 scopes can be exclusive and jointly complete (confirmed against charter_scope only after the reveal, see closing notes).
- Overlapping subject "the resident's coinsurance percent": P2 (`coinsurance_share`: K/L only with no QMB, full-coinsurance or QMB → 0) vs P5 (`block_resident_percent`: current supplemental tier's share when a Medigap effective date precedes the block, QMB → 0). Because medicare_coverage_tier_change places a QMB coverage in the QMB tier (share 0) "whatever Medigap is on file", both give 0 for QMB+Medigap; no conflicting conclusion found. Different anchors (today vs the block's first day) are legitimate (future run-up vs a past block).
- Overlapping subject "price of a held bed night": P2 `held_bed_buildup` prices at "the daily rate of the most recent room-and-board charge on the resident's private-pay agreement"; P4 `room_held_nightly_rate` prices at the charge's daily rate / 427 / 398; the owning bedhold charter (bedhold_evt_charges) prices at "the private pay schedule's daily rate in effect on those days for the tier of the room held". Three different methods for one quantity → F-6 and F-7 below.
- Overlapping subject "patient pay of the month eligibility starts mid-month": P3 tier 2 says nothing (private-pay month) while medicaid_evt_patient_pay_actual bills every eligible month at the notice amount and reduces only "months before the eligibility start date" → F-9.
- Cross-category read boundaries: every read is through CFIELD/CPARAM/EXISTS/X* on medicare, medicaid, bedhold, ancillary, private; no write lands outside trust (tools write trust_ledger / trust_requests / trust_accounts only; events trust_reversal and trust_bill_transfer have `triggers: []`).

### rule_compute_equivalence
- Scratch sweep (/tmp/erl0074_pta_trust/sweep.py): every `compute_basis` quote is verbatim in its own rule (all 6 policies); every compute binding has a basis; every baseline.rule sentence is in the rule; every prerequisite `policy_source` is verbatim in the blocked rule; factor binding sets are pairwise disjoint; no factor `decides: result`; no factor binding reads another factor's binding (transitive closure over the compute) — XF A1/A2/A5 and B9 PASS mechanically.
- Mismatches found by reading (each a finding below): P6 `income_last` (F-3), P4 `reserved` second branch (F-4), P6 `co_open_all` filter on a field adjustment rows lack (F-5), P3 inner `RND(pp_days * ma_rate, 2)` vs "rounded half up to the cent once, on the final amount only" (F-10), missing same-day tie rules on LATEST/XLATEST reads (F-11), P6 `anc_kept` "the authorized amount" with no selection rule (F-12).
- DSL note (not a finding): RND is Python round (half-even on binary floats) while every rule says half up; no task value lands on a half cent (checked: 63.00, 61.50, 599.80, 1244.00, 759.50, 1559.65).

### action_binding_and_uuids
- (target_tool, computes) pairs: six distinct tools, each claimed by exactly one policy, `computes: amount` each. PASS.
- uuid8s e2970e4f, 74e4ddf9, 45809d6d, 446aaea8, 51d626ac, c6615816: no shared prefix/suffix, no sequence, no reuse. PASS. No factor id is a substring of a tool name (XF 20 PASS).
- Imports: only `from erlbench import ToolContext, tool`; date helper not needed; `_Cents` static methods (XF 23 PASS). Every write tool calls ctx.create/update in its own body (XF 22 PASS). No composed multi-value string args (XF 21 PASS). frozen_time format `YYYY-MM-DD HH:MM:SS EDT` in both views (XF 24 PASS).
- Tool bodies vs docstrings: amounts "positive … rounded half up" → `_Cents.positive` (abs + half up) on return/transfer/withdrawal tools; authorization amount "decimal … rounded half up" → `_Cents.half_up`; balance moves as stated; no tool validates any prerequisite, authorization, balance or posting day. PASS.
- Docstrings carry no concrete example values. Ordering words: see F-13.

### prerequisite_graph
- Every extended policy fills `prerequisite` (`[]` for P1, P3, P4, P5). Edges: P2→P1, P6→P3, P6→P4, P6→P5; all `kind: value_input`, `gate: balance_now` (a binding that exists in both P2 and P6 compute), `form: state`, no `fallback_reason` (correct for state form), `resolved_by` = the depended-on policy's target_tool. Acyclic. `effect` sentences are true of the tools (each write moves the trust balance that `balance_now` sums).
- `condition` vs `policy_source` scope: all four edges' sentences are broader than their conditions → F-1.
- No authoring-viewpoint phrasing in `prerequisite` fields. PASS otherwise.

### prerequisite_sentences
- Four-point test, per edge:
  - P2→P1 "The amount a new per-bill authorization covers is fixed only after the account's ledger carries a return for every transfer that paid a charge for a service a payer covers." Ordering connective "only after" ✓; record-visible state (a return on the ledger) ✓; no tool/id/snake_case ✓; scope: "every transfer that paid a charge for a service a payer covers" (any bill category, every such transfer) vs condition (ancillary transfers only) and vs P1's rule (returns only "the most recent transfer to an ancillary charge") ✗ → F-1.
  - P6→P3 "The spare amount is not worked out until the account's ledger carries a transfer naming the patient pay charge of every month that a standing authorization for patient pay covers and whose due day has passed." ✓✓✓; scope "every month … whose due day has passed" vs condition "the patient pay charge of the latest service month" and P3's rule (only the latest service month) ✗ → F-1 (bites task 1).
  - P6→P4 "…a transfer for every bed-hold charge a per-bill authorization names once that authorization's posting day has come." vs condition "the bed-hold charge named by the most recent per-bill bed-hold authorization …" and P4's rule (most recent authorization only) ✗ → F-1.
  - P6→P5 same shape for coinsurance ✗ → F-1.
- State form honoured; for each edge exactly one tool of this difficulty writes the waited-on row kind (trust_reversal ← return_improper_transfer; trust_bill_transfer by category ← the three post_* tools). Derivation sentence + records + depended-on rule → resolving action holds in a single reading only where one qualifying record exists (both task worlds except task 1's patient-pay edge, see task1.md).
- No rule names another problem's tool or id; no depended-on rule restates the sentence; the rules carry no second wording of a dependency. P2/P4/P5 "posted on the second business day after the authorization is signed" orders a transfer after an authorization signature, but no extended policy owns bed-hold/coinsurance authorization signing, so it grounds no undeclared problem edge (base eligibility `authorized_transfer`).

### override_declarations
All six policies carry `overwrite: []`. Sentence-by-sentence against base_policy_refs:
- trust_evt_reversals (P1): "returned … within the improper charge reversal business days, for the improper part only, naming the original entry" — P1 follows and defines the improper part; "An entry is returned once per reason" — inherited (dedup). No conflict.
- trust_evt_bill_transfers (P2–P5): standing vs per-bill authority — followed; "A bill transfer is made only under …" — followed; payee/PNA sentences — n/a to self-directed; "A transfer pays at most the open balance of the named charge and never exceeds the available balance" — P4/P5 state both caps; P2 caps the authorization at the open balance; **P3 states only the available-balance cap and its compute has no open-balance cap** → F-2 (undeclared override); "Nothing Medicare or Medicaid pays for is ever paid from the account" — followed.
- trust_evt_withdrawals (P6): written request by the tier's signer — followed; "never exceeds the available balance" — spare ≤ available. No conflict.

### factor_ladders
Counts as declared (factors / parameter / method / cross_difficulty):
- P1 4 / 2 (transfer_paid_part, absorbed_balance) / 2 (covered_days_source, refund_order) / 1 (medicare). Multi-source: refund_order (ancillary payment date vs trust transfer date), covered_days_source tier 2.
- P2 5 / 3 (coinsurance_share, full_coverage_left, held_bed_buildup) / 2 (covered_run_end, awaiting_authorization) / 5 (medicare×4, bedhold). Multi-source: awaiting_authorization, covered_run_end tier 2.
- P3 4 / 3 / 1 (named_month_patient_pay) / 4 (medicaid). Multi-source: named_month_patient_pay tiers (case + charge).
- P4 4 / 2 (room_held_nightly_rate, resident_part_already_paid) / 2 (reserved_nights_on_leave, nights_after_hold_ended) / 4. Multi-source: reserved_nights_on_leave (medicaid case + bedhold reservation).
- P5 5 / 4 / 1 (block_benefit_day_count) / 5 (medicare).
- P6 5 / 4 / 1 (coming_patient_pay_kept) / 3 (medicaid×2, bedhold). Multi-source: coming_patient_pay_kept (trust account standing authorization + trust ledger deposits).
Every ladder has ≥3 tiers stated in the rule and implemented in compute (sweep). Structural defects (each listed in full under findings):
- F-14 one tier written as two or three — tiers whose values are one expression evaluated on different domains (13 factors).
- F-15 `block_days_past_coverage_end` tier 2 is 0 on every medicare-charter-producible world.
- F-6 `room_held_nightly_rate` tiers 2/3 and baseline vs the bedhold charter's own rate.
- F-8 `other_unsigned_bills_kept` tier 2 conjunct "no such bed-hold balance exists".
- F-9 unreal tier outcomes on government-program quantities (P1 covered_days_source tier 2, P3 named_month_patient_pay tier 2 and tier-1 sub-branch, P5 block_benefit_day_count tier-1 numbering).
- F-16 mislabelled effect: awaiting_authorization (`method`) selects among numbers (open balance / 0 / authorized amount) fed to the same subtraction.
After striking the factors these tests remove, survivors per policy: P1 refund_order only (0 parameter); P2 coinsurance_share, covered_run_end, held_bed_buildup (3 < 4; held_bed_buildup also F-7); P3 none clean; P4 reserved_nights_on_leave (with F-4); P5 block_resident_percent only; P6 resident_allowance_kept, coming_patient_pay_kept, recurring_services_kept (3 < 4). No policy keeps 4 factors with ≥2 parameter and ≥1 method → F-17.

### findings
Every finding below is charter-global; the task files demonstrate the consequence on their own worlds where one exists. "Bears on" names the task(s).

**F-1 SOURCE-POLICY RED — prerequisite sentences broader than their conditions and than what the depended-on rule can write (all 4 edges).**
Symptom: each sentence waits on "every" qualifying record; each `condition` and each depended-on rule names only the most recent / latest one. Members: (a) P2→P1: "a return for every transfer that paid a charge for a service a payer covers" vs condition "…every trust_bill_transfer that paid an ancillary charge…" vs P1 rule "The transfer returned is the most recent transfer to an ancillary charge"; (b) P6→P3: "the patient pay charge of every month that a standing authorization for patient pay covers and whose due day has passed" vs condition "the patient pay charge of the latest service month" vs P3 rule "the patient pay charge of the latest service month"; (c) P6→P4: "every bed-hold charge a per-bill authorization names once that authorization's posting day has come" vs condition/P4 rule "the most recent such authorization"; (d) P6→P5: same for coinsurance. Consequence: in any world with a second qualifying record (two ancillary transfers that paid covered charges; two bed-hold or coinsurance authorizations past their posting day with the earlier one untransferred; an earlier covered month without a transfer) the sentence's state is never reached by any write of the charter while the condition reads as met → two readings (proceed vs never work the figure out). Bears on task 1 (edge b, demonstrated in task1.md); edges a, c, d have one qualifying record in their task worlds.

**F-2 SOURCE-POLICY RED — P3 drops the base open-balance cap without an overwrite.** Base trust_evt_bill_transfers: "A transfer pays at most the open balance of the named charge and never exceeds the available balance." (formula `min(amount, trust_msr_bill_open_balance, trust_msr_available_balance)`). P3 rule: "…less the payments already naming that charge, never more than the available balance and never below zero"; compute `RND(MX(0, MN(available, month_pp - credit_reaching - paid_named)), 2)` — no open-balance term; `overwrite: []`. Producible world: October estimate 1300.00 billed while pending, approval with notice patient pay 1400.00 effective before October, trueup_increase 100.00 posted for October (medicaid_evt_patient_pay_actual), no payments, nothing else. P3 names the estimate (recorded first for the month), month_pp = 1400.00, other_charged = 100.00, credit = 0 → 1400.00; base cap → 1300.00. Two answers. Bears on neither task's value (task 1: 599.80 < open 1389.70).

**F-3 SOURCE-POLICY RED — P6 `income_last` ≠ rule.** Rule: "the case's patient pay less the most recent pension or benefit deposit"; compute `(LATEST(…pension_direct_deposit) or LATEST(…ssa_benefit_as_payee) or 0)` takes the latest pension deposit whenever one exists, even if a later SSA benefit deposit exists. World: pension 1000.00 on 09-03, SSA benefit 1200.00 on 10-03 → rule 1200.00, compute 1000.00. No bite in task 1 (no such deposits).

**F-4 SOURCE-POLICY RED — P4 `reserved` second branch over-counts.** Rule: "the nights of the charge from the eligibility start date that fall within the first reserved nights per hospitalization counted from the departure date". Compute `MX(0, MN(bh_nights - DAYS(bh_from, elig_start), K - DAYS(leave_start, elig_start)))` ignores how far the charge starts after the eligibility start. World: departure 09-08, eligibility starts 09-10, charge for 10-01..10-31 (31 nights) on the same hold: rule 0 (the first 15 nights end 09-22); compute MN(31+21, 15−2) = 13. No bite in task 1 (branch 1 taken).

**F-5 SOURCE-POLICY RED — P6 `co_open_all` subtracts no coinsurance adjustments.** Rule: "resident coinsurance charges other than the one … carry an open balance, that open balance" (open balance = charge less payments and adjustments). Compute filters `medicare_coinsurance_adjustment` and payments by `liable_party='resident'`; medicare_coinsurance_adjustment has no liable_party field (medicare.yaml event fields; liable_party on a payment is "party that paid") → adjustments never subtracted. World: a second resident coinsurance charge 2387.00 with an uncertified-day adjustment 108.50 → rule keeps 2278.50, compute 2387.00. XF 12 decoy class. No bite in task 1 (single resident charge, the authorized one).

**F-6 SOURCE-FACTOR RED (realism, XF 27/29) — P4 `room_held_nightly_rate` ladder and baseline contradict the owning bedhold charter.** bedhold_evt_charges: "The bed-hold daily rate is the tier's bed-hold percent of the private pay schedule's daily rate in effect on those days for the tier of the room held" (all bed-hold tiers 100%); private schedule: Semi-Private LTC 384 (2025-07-01) / 398 (2026-07-01), Semi-Private Secure Memory Care 412 / 427. Tiers 2/3 hard-code 427 / 398: on every charter-produced charge for nights from 2026-07-01 they equal tier 1's "daily rate on the named charge" (one tier written as three); for earlier nights they price at a rate the bedhold charter does not charge (398 vs 384). The fall-through/baseline "each at the semi-private nightly rate" prices a private-room hold at the semi-private rate, which no SNF publishes and the owning charter contradicts — the straw-man baseline in another form. Bears on task 1 (see factor_weight there).

**F-7 SOURCE-FACTOR RED (realism, XF 29) — P2 `held_bed_buildup` prices held nights at "the daily rate of the most recent room-and-board charge on the resident's private-pay agreement".** Owning charter: schedule rate of the room tier held, in effect on those days. Producible divergence: a resident moved to a semi-private room (private_agreements.last_room_change_date) whose latest room-and-board charge is a reissued private-room month (task 1's world has exactly this: latest charge 635741bb Private LTC 436.00, room now semi-private) → P2 would build up 436.00 a night where the bedhold charter charges 398.00. No bite in task 0 (room held semi-private, latest charge 398.00).

**F-8 SOURCE-FACTOR RED (unreal ladder) — P6 `other_unsigned_bills_kept` tier 2 conjunct.** "where no such bed-hold balance exists and resident coinsurance charges other than … carry an open balance" — whether an unsigned bed-hold bill is open is not something any business weighs in deciding whether to keep money for an unsigned coinsurance bill; with both open, the ladder keeps only the bed-hold balance. World: unsigned bed-hold 421.00 and unsigned coinsurance 759.50 open → kept 421.00 where a business keeps 1180.50. Bears on task 1's ladder structure (task 1 has no second coinsurance charge, so tier 1 alone acts there).

**F-9 SOURCE-FACTOR RED (realism, XF 27) — government-program tiers that are not the real rule / contradict the owning charter.** Members:
- P1 `covered_days_source` tier 2: "every charged day when the eligibility start date is on or before the first day of the service month and none otherwise" — for a month in which Medical Assistance starts mid-month, the days on/after the start are MA days (ancillary_account_lifecycle: tier follows payer "on the date of service"; ancillary_payer_coverage: "A Medicaid resident is never charged for anything the Medicaid per diem includes"; oxygen is in medicaid_covered_categories); "none" keeps resident funds paying for MA-covered days (42 CFR 483.10(f)(11)(i)).
- P3 `named_month_patient_pay` tier 2: "where … its eligibility start date is after the first day of the service month, nothing, because that month is a private-pay month" — medicaid_evt_patient_pay_actual bills every eligible month at the notice amount and reduces as not_eligible_month only "Estimates billed for months before the eligibility start date"; the start month is not before the start date.
- P3 `named_month_patient_pay` tier-1 sub-branch: "otherwise the most recent estimate reconciled by a trueup decrease less that decrease" — infers this month's County Assistance Office amount from whichever month was trued up last; no business reads one month's notice amount off another month's reconciliation (medicaid_eligibility_decision records the notice's patient pay and effective date; the method exists only because the record lacks the month's amount). Bears on task 1 (tier taken; see task1.md).
- P5 `block_benefit_day_count` tier 1: renumbers by `DAYS(cov_start, blk_from) + prior_days + 1` (calendar days); medicare_agg_benefit_period numbers a day as "the SNF days already used in the period before the episode, plus the net covered days booked earlier in the same episode, plus one" (leave-of-absence/hospital days are not benefit days). World: an earlier block of the episode with a reversed leave day → calendar count is one too high.

**F-10 SOURCE-POLICY RED (XF 10) — P3 rounding.** Rule: "rounded half up to the cent once, on the final amount only"; compute rounds an intermediate `RND(pp_days * ma_rate, 2)` in the partial-month branch. No numeric bite while ma_daily_rate is in cents (task 1 does not take this branch).

**F-11 SOURCE-POLICY RED (XF 11) — LATEST/XLATEST reads with no stated same-day tie rule.** Members: P2 auth_bill/auth_cat/auth_amt ("the most recent per-bill authorization"), coins_rate ("the most recent coinsurance charge" — task 0 has two on 2026-10-10, both 217.00), room_rate ("the most recent room-and-board charge"); P3 tu_charge/tu_last/tu_est ("the most recent estimate reconciled by a trueup decrease" — task 1 has two on 2026-10-21, equal amounts), last_dep_avail/last_dep_amt; P4 last_dep_*; P5 last_dep_*; P6 last_dep_*, income_last, svc_start_at/svc_item ("most recent request to start a recurring service"), svc_last_charge, bh_auth_charge ("the most recent bed-hold authorization"), co_auth_charge. (Rules that do state ties: P1 transfer, P2 item charge, P3 charge, P4/P5 authorization.) The ties present in the task worlds select equal values, so no task value moves.

**F-12 SOURCE-POLICY RED — P6 `anc_kept` names no authorization.** Rule: "where a per-bill authorization names an ancillary charge and the ancillary account carries more than the authorized amount, the balance less the authorized amount" — with two ancillary authorizations (or one whose transfer already posted) the rule admits latest-amount, sum-of-amounts and only-untransferred readings; compute takes the latest (`anc_auth_amt` LATEST) and counts all (`anc_auths` COUNT). No bite in task 1 (no ancillary authorization).

**F-13 SOURCE-POLICY RED (XF 19, check 3) — ordering words in tool docstrings.** sign_bill_payment_authorization_74e4ddf9: "The signer can afterwards see the authorization"; sign_withdrawal_request_c6615816: "a withdrawal request already open"; return_improper_transfer_e2970e4f: "an earlier transfer or withdrawal", "the earlier entry" (×3), "any later account lookup"; post_patient_pay_transfer_45809d6d / post_bed_hold_transfer_446aaea8 / post_coinsurance_transfer_51d626ac: "next statement", "any later account lookup". None names another tool or a write order; listed as the XF 19 class because the recipe makes any member RED.

**F-14 SOURCE-FACTOR RED (XF 7, unreal ladder) — one tier written as two or three: every tier's value is one expression evaluated on that tier's domain.** Members (expression in brackets):
- P1 transfer_paid_part tiers 2+3 [xfer − returned_wrong]; P1 absorbed_balance all tiers [max(0, charge − payments − those credits)];
- P2 full_coverage_left tiers 2+3 [limit − prior − band1] (tier 3 is tier 2 at prior=0); P2 awaiting_authorization tiers 1+3 [min(authorized, open)];
- P3 credited_reconciliation_amount all tiers [trueup + redetermination on other charges]; credited_not_eligible_amount all tiers [not-eligible + cost-of-care]; unapplied_patient_pay_payments all tiers [max(0, unallocated − refunds)];
- P4 resident_part_already_paid all tiers [card/check/ACH + trust payments naming the charge]; nights_after_hold_ended tiers 1+3 [nights after a date] (release date vs hospital-discharge date, same method);
- P5 block_benefit_day_count tier 1 + fall-through [max(0, min(days, limit+1 − first)) with first renumbered] (the fall-through's domain is exactly "renumbering agrees"); block_days_away all tiers [LOA + hospital]; block_days_center_bears all tiers [uncertified + booking error];
- P6 unsigned_ancillary_bills_kept all tiers [max(0, ancillary balance − authorized amount)].
Demonstration (each): substitute the first tier's expression for every tier on every input; no output changes. Effect on counts → F-17.

**F-15 SOURCE-FACTOR RED (XF 7) — P5 `block_days_past_coverage_end` tier 2 is 0 on its whole producible domain.** medicare_agg_benefit_period: "A day is booked only when its benefit-period day number does not exceed the benefit-period day limit" → `blk_first + blk_days − 1 − period_limit ≤ 0` on every charter-booked block, so tier 2 selects the fall-through's 0.

**F-16 SOURCE-FACTOR RED (label) — P2 `awaiting_authorization` labelled `method`:** its tiers select a number (that charge's open balance / 0 / the authorized amount) subtracted in the same place; no tier changes the computation's shape.

**F-17 SOURCE-FACTOR RED — factor floor after striking.** Counting only factors that pass the ladder tests (F-6…F-9, F-14…F-16): P1 1 (refund_order; 0 parameter), P2 3 (coinsurance_share, covered_run_end, held_bed_buildup — the last also F-7), P3 0 clean, P4 1 (reserved_nights_on_leave, with F-4), P5 1 (block_resident_percent), P6 3 (resident_allowance_kept, coming_patient_pay_kept, recurring_services_kept). Every policy is below 4 factors / 2 parameter / 1 method. Bears on both tasks.

Observations (not grounds for rework):
- O-1 P6 `resident_allowance_kept` tier 1 keeps only the protected VA pension (90.00) for the VA reduced pension tier; whether Pennsylvania lets that resident keep the 45.00 personal needs allowance in addition was not verifiable from the artifacts.
- O-2 P5's `share_pct` uses the episode's *current* tier share for any Medigap effective before the block; medicare_evt_coinsurance prices by the tier in effect on the days of service (a QMB determination after the block would give 0 where the medicare charter keeps the earlier split).
- O-3 P2 `full_left` can go negative (no floor) when prior SNF days plus band-1 bookings exceed the limit; only reachable on a misnumbered booking.
- O-4 P4/P5 post "on the second business day after the authorization is signed" but define the available balance "after today"; a late posting uses today's balance (unique reading, recorded for the renderer).
- O-5 owed-but-unposted cross-product corrections and non-producible seed rows are per-world; they are listed in each task file under XF 29.

Pre-reveal charter verdict: charter = F-1 … F-17 (no CLEAN).

## closing_checklist
(written after both reveals at 2026-10-22T07:26:36Z; nothing above this heading was changed after the reveal)
- Task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; this is revision_1 (the predecessor's stub carried no findings).
- Scopes (charter_scope): task 0 {P1, P2}, task 1 {P3, P4, P5, P6} — pairwise disjoint, jointly cover all six extended policies, each with its own uuid8 tool. PASS.
- Problem trees: task 0 one prerequisite, one value_input edge, user write P2; task 1 three prerequisites, three value_input edges, user write P6; whole-difficulty graph acyclic. PASS. Every edge bears weight (skip tests in the task files).
- Blind derivations equal GT on every scored value and the write order in both tasks.
- Not closed: F-1 (with a demonstrated second reading in task 1), F-2…F-5, F-10…F-13 (SOURCE-POLICY, charter-level), F-6…F-9, F-14…F-17 (SOURCE-FACTOR), task XF 29 items T0-X1, T1-X1…T1-X7. Every computation is below the factor floor once struck factors are removed.
- Gates were not re-run by this auditor (the difficulty does not close this round); the coordinator's snapshot (7/7 rc=0) is the entry evidence only.

VERDICT revision_1: task0=RED[F-14,F-16,F-17,T0-X1] task1=RED[F-1b,T1-X1,T1-X2,T1-X3,F-6,F-8,F-9,F-14,F-15,F-17,T1-X4,T1-X5,T1-X6,T1-X7] charter=F-1,F-2,F-3,F-4,F-5,F-6,F-7,F-8,F-9,F-10,F-11,F-12,F-13,F-14,F-15,F-16,F-17

## revision_2
### entry (round 2, started 2026-10-22T15:23Z)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh resident_trust_fund_accounts 2` at 2026-10-22T15:23:18 — [check_extended] rc=0 EXTENDED OK; [check_task_tools] rc=0 TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 REPLAY OK; [check_solvability] rc=0 SOLVABILITY OK; [check_compute] rc=0 COMPUTE OK; [check_grounding] rc=0 GROUNDING OK; [check_cross_fire] rc=0 SCOPE OK.
- Hashes: task_tools.py 9a8c12b55045706b7f233410d591e591339da7cf1572a5d82339f03c46dda231; trust.extended.yaml 278626855e987a8608eec044d96c64b3d07e691ac3b7c889aa5fef74c724bdad; task0.view.json 9aa41f780ff9057c9a61a0a9773cac17fc95c259d9f407308020ea7eb39592ab; task1.view.json 4dee0d01bdda051c5e6854e931ebe3e3d8a42590d20b321a70f0684e5a049874. Both shared inputs changed → charter-global section re-derived in full.
- contamination_disclosure: this auditor revealed round-1 GT (both tasks) in revision_1; round-2 blind derivations are therefore not independent of round-1 gold values. They are re-derived from the new views and charter before tasks/*.json or the round-2 worklog section are opened.

### charter_global_frozen (revision_2, written before tasks/*.json or the round-2 worklog section were opened)
- Read: new trust.extended.yaml (base section still byte-identical to blueprint/products/trust.yaml), new task_tools.py, both rebuilt views, targeted sections of medicare/bedhold/medicaid/private charters (adjustment open-balance cap, payment posting, bedhold end events, bedhold_day_reversed fields, isolation_billing_tier). Harness: /tmp/erl0074_pta_trust/r2.py, r2b.py.
- Policy set now: P1 trust_ext_covered_service_return, P2 trust_ext_ancillary_authorization_amount, P3 trust_ext_patient_pay_transfer, P4 **trust_ext_bed_hold_return** (return_bed_hold_overcharge_0789df0a, agent, trust_reversal), P5 **trust_ext_coinsurance_return** (return_coinsurance_overcharge_2cf6d12d, agent, trust_reversal), P6 trust_ext_spare_withdrawal. Edges P2←P1; P6←P3, P4, P5 (all value_input, gate balance_now, state form). Acyclic.
- Mechanical sweep (sweep.py): every compute_basis quote verbatim in its rule; every baseline.rule sentence in the rule; every policy_source verbatim; binding sets disjoint; no factor decides result; no factor reads another factor's binding (transitive). PASS.
- Tools: six write tools, each claimed by one policy; uuid8s e2970e4f, 74e4ddf9, 45809d6d, 0789df0a, 2cf6d12d, c6615816 independent; only `from erlbench import ToolContext, tool`; every body creates/updates itself; no prerequisite/balance validation; no ordering word in any docstring (grep before/after/afterwards/first/then/until/prior/once/earlier/later/next/already/beforehand: none); no example values. trust_reversal / trust_bill_transfer triggers []. PASS.

### round-1 items re-checked
| id | round-1 finding | revision_2 |
| --- | --- | --- |
| F-1 | sentences broader than conditions | (b) closed (P6 patient-pay sentence now "the latest service month"); (a)(c)(d) **not closed** — reworded but still select a different transfer from the depended-on rule → R2-1 |
| F-2 | P3 drops open-balance cap | closed (`open_named` cap, rule sentence added) |
| F-3 | P6 income_last | closed (later of the two kinds, tie → pension) |
| F-4 | P4 reserved branch | closed by removal (P4 replaced) |
| F-5 | P6 coinsurance open filter | closed by removal |
| F-6 | P4 rate ladder vs bedhold charter | closed (P4 prices by room tier held and the schedule of the night) |
| F-7 | P2 held-bed rate | closed (schedule rate of the room tier held, 2025/2026 schedule split) |
| F-8 | unreal "only one kind kept" conjunct | **not closed** — same shape in the two replacement factors → R2-6 |
| F-9 | unreal government-program tiers | P1 MA tier closed; P5 numbering closed by removal; P3 tier-1 sub-branch removed; **P3 tier 2 not closed** → R2-5 |
| F-10 | P3 inner rounding | closed |
| F-11 | missing tie rules | closed (tie rules on every LATEST/XLATEST read that can tie) |
| F-12 | P6 anc_kept authorization | closed ("the most recent per-bill authorization naming an ancillary charge") |
| F-13 | ordering words in docstrings | closed |
| F-14 | one tier written as several | partly closed (absorbed, awaiting, recon, part_paid, benefit_day_count, days_away, center_bears, unsigned_ancillary gone or re-shaped); **remaining/new members** → R2-7 |
| F-15 | P5 zero-domain tier | closed by removal |
| F-16 | awaiting_authorization label | closed by removal |
| F-17 | factor floor after striking | **not closed** → R2-10 |

### findings (revision_2; charter-global; task files demonstrate consequences)
**R2-1 SOURCE-POLICY RED — prerequisite sentences still select a different transfer than the depended-on rule (3 edges).** Each sentence puts the restriction on the charge inside the noun phrase ("the most recent transfer to [a charge that …]"), i.e. the most recent of the transfers whose charge qualifies; each depended-on rule returns "the most recent transfer to a … charge" whatever its charge; each `condition` follows the rule. Members: P2→P1 "a payer-covered return for the most recent transfer to an ancillary charge whose service a payer covers" vs P1 "The transfer returned is the most recent transfer to an ancillary charge"; P6→P4 "a wrong-amount return for the most recent transfer to a bed-hold charge that billed more than the hold let it bill" vs P4 "The transfer returned is the most recent transfer to a bed-hold charge"; P6→P5 "…the most recent transfer to a Medicare coinsurance charge that billed more coinsurance than the resident owes" vs P5 "The transfer returned is the most recent transfer to a Medicare coinsurance charge". World: an older ancillary transfer paid a Part A-covered oxygen month and the latest ancillary transfer paid an uncovered outing → sentence: wait for a payer-covered return naming the older transfer (no rule writes it, so the figure is never fixed); condition/P1: the latest transfer is not covered, no wait. No bite in either task world (one transfer of each kind).

**R2-2 SOURCE-POLICY RED (realism, XF 27; intra-charter conflict) — P2 counts leave nights inside the unbilled run as coinsurance days.** P2: "The unbilled run is the days of the active Part A episode not yet booked, starting … on the coverage start date where no block is booked yet" — every calendar day; compute `DAYS(cover_start, hold_start)`. medicare_evt_day_counting: "A leave-of-absence day … is neither a covered day nor a benefit day"; P1 in the same charter takes the same nights off ("because a night away at midnight is not a covered day"). Same night (task 0: bedhold 9912bcf7, 2026-09-20) is a covered day for P2 and not for P1. Bears on task 0 (moves the scored value, task0.md).

**R2-3 SOURCE-FACTOR RED (realism) — P2 `coinsurance_year_rate` takes the run's year from the last booked block's last day.** Rule: "the calendar year of the run, taken as the year of the most recent booked block's last day or, where no block is booked yet, of the coverage start date". The run starts the day after that block; a block ending 2025-12-31 makes a 2026 run priced at 209.50, while medicare_evt_coinsurance prices days "at the daily coinsurance rate of the calendar year in which those days of service fall". No bite in task 0 (run in 2026).

**R2-4 SOURCE-POLICY RED (XF 12 decoy/prior-period) — P1 `nights_away`.** (i) bedhold_day_reversed carries no service_month (bedhold.yaml event fields: days_entry_id, day_payer, from_date, day_count, adjustment_reason, entry_date) so `XSUM(… 'bedhold_day_reversed', service_month=charge_month)` never matches and "less any of them reversed" is never applied — world: a September leave night booked then reversed → rule 0, compute 1. (ii) the nights counted are every leave night of the service month, also those before the payer's start date that `days_from_start` already excluded — world: leave night 09-05, Part A from 09-09 → covered days 21 instead of 22. No bite in task 0 (one leave night, 09-20, unreversed, after 09-09).

**R2-5 SOURCE-FACTOR RED (realism, XF 27) — P3 `named_month_patient_pay` tier 2 and the missing tier-1 branch.** Tier 2 "where the case is eligible and its eligibility start date is after the first day of the service month, nothing, because the approval left that month out and its estimate is reduced in full" — medicaid_evt_patient_pay_actual reduces as not_eligible_month only "Estimates billed for months before the eligibility start date"; the start month is billed at the notice amount (F-9 member carried over). New gap: tier 1's value is stated only "when its effective date is on or before the first day of the month"; for an eligible estimate month whose notice patient pay takes effect later, the rule gives no number while compute falls through to the billed estimate (XF 11 absent-branch). No bite in task 1 (start and effective date 2026-07-01).

**R2-6 SOURCE-FACTOR RED (unreal ladder; F-8 class) — keep only the authorized amount while an authorization awaits.** P6 `ancillary_bills_kept` and `bed_hold_bills_kept`: tier 1 keeps every open balance "where … no per-bill authorization naming a … charge awaits its transfer"; tier 2 keeps only "its authorized amount, never more than that charge's open balance", dropping every other open charge of that kind. Whether one charge has an authorization pending is not what a business weighs in keeping money for the other open bills. World: bed-hold charges 421.00 (unsigned) and 9156.00 with an awaiting authorization of 1000.00 → kept 1000.00, versus 9577.00 kept with no authorization. In task 1 tier 1 acts (both authorizations already transferred).

**R2-7 SOURCE-FACTOR RED (XF 7; F-14 class) — tiers that are one expression on their domains.** Members: P1 `transfer_paid_part` tiers 2+3 [transfer less wrong-amount returns] — base trust_evt_bill_transfers caps a transfer at its charge's open balance, so "never more than the charge" never binds on a producible world; P2 `run_day_numbering` tiers 2+3 [max(0, limit − prior SNF days)] (tier 3 is tier 2 at prior = 0); P3 `credited_not_eligible_amount` [not-eligible + cost-of-care reductions on other charges]; P3 `unapplied_patient_pay_payments` [max(0, unallocated − refunds)]; P4 `hold_end_nights` tiers 2+3 — bedhold_released and bedhold_expired both record end_date "last held day", so a released hold's end_date is its release date and tier 3's expression gives tier 2's value; P4 `hold_first_night` tiers 1+2+3 [the later of the charge's first night, the notice delivery date and the private hold start] split into a precedence ladder (see R2-8).

**R2-8 SOURCE-FACTOR RED (realism) — P4 `hold_first_night` precedence.** "where the transfer notice was delivered after the departure date, it is the notice's delivery date …; where the notice was not late and the private hold starts after the departure date, it is that start date". When both are late, bedhold_election ("a later election holds it only from the day of election") and bedhold_evt_payments_adjustments (notice_not_given) together give the later of the two; tier 1 takes the notice date. World: departure 06-10, notice 06-12, election (private_hold_start_date) 06-14 → P4 counts 06-12 and 06-13 as due nights the hold never held. No bite in task 1 (election date = departure).

**R2-9 SOURCE-POLICY / SOURCE-FACTOR RED — P5 reads that do not match their rule or the owning charter.** (i) `recert_on` = medicare_coverages.last_certification_date ("A signed physician recertification is recorded as the last certification date") while the rule tests "the episode's first recertification" — a timely first recertification followed by a later one makes the compute treat the later date as the first (XF 13: rule word names a fact the record does not keep). (ii) `block_plan_share` ignores the supplemental effective date; medicare_evt_coinsurance: "days before the supplemental effective date keep the earlier split" — a Plan K card effective after the block gives 50 where the medicare charter keeps 100. No bite in task 1 (one recertification 2025-12-27; Plan K effective 2025-12-01 before the block).

**R2-10 SOURCE-FACTOR RED — factor floor after striking.** Struck: P1 transfer_paid_part (R2-7), nights_away_taken (R2-4 ii, unreal value) → 2 left (0 parameter); P2 run_day_numbering (R2-7), coinsurance_year_rate (R2-3) → 3 left; P3 credited_not_eligible_amount, unapplied_patient_pay_payments (R2-7), named_month_patient_pay (R2-5) → 1 left; P4 hold_end_nights, hold_first_night (R2-7/R2-8) → 3 left (1 method); P5 block_plan_share (R2-9 ii) → 3 left; P6 ancillary_bills_kept, bed_hold_bills_kept (R2-6) → 3 left. No policy keeps 4 factors with 2 parameter and 1 method.

**R2-11 SOURCE-POLICY RED (rule/compute) — P3 `recon_credit` tier 2 test.** Rule: "every estimate billed while the case was pending is the same amount above the case's patient pay"; compute tests only `est_max == pp_amt` (the largest estimate equals the named charge). World: estimates 1300.00 (June) and 1389.70 (July–October), notice patient pay 1276.40, no trueup posted → rule: tier 2 does not apply (0); compute: 3 × 113.30. No bite in task 1 (tier 1, trueups posted).

Observations: O2-1 P4 `hold_rate_schedule` fall-through prices nights before 2025-07-01 at the schedule of the billing date (no earlier schedule exists in the private charter). O2-2 bedhold returned holds in both seeds record end_date = return date while the bedhold charter defines end_date as the last held day (no scored read uses it for returns).

Pre-reveal charter verdict revision_2: R2-1 … R2-11.

### closing_checklist (revision_2, after the reveal at 2026-10-22T15:32:43Z)
- Gates: snapshot round 2 7/7 rc=0 (cited above); scopes task 0 {P1, P2}, task 1 {P3, P4, P5, P6}: disjoint, complete; graph acyclic; trees: task 0 one value_input edge + user write; task 1 three value_input edges + user write; every edge bears weight.
- Blind derivations equal GT on every scored value in both tasks (disclosed: not formally blind after revision_1).
- Not closed: R2-1 … R2-11 (charter), task 0 R2-2 consequence and T0-R2-X1 (both move the scored authorization 61.50 → 115.70), task 1 T1-X2. Every policy below the factor floor after striking (R2-10).

VERDICT revision_2: task0=RED[R2-2,T0-R2-X1,R2-7,R2-10,T0-X1] task1=RED[T1-X2,R2-7,R2-10] charter=R2-1,R2-2,R2-3,R2-4,R2-5,R2-6,R2-7,R2-8,R2-9,R2-10,R2-11

## revision_3
### entry (round 3, started 2026-10-22T19:17Z)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh resident_trust_fund_accounts 3` at 2026-10-22T19:16:51 — [check_extended] rc=0 EXTENDED OK; [check_task_tools] rc=0 TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 REPLAY OK; [check_solvability] rc=0 SOLVABILITY OK; [check_compute] rc=0 COMPUTE OK; [check_grounding] rc=0 GROUNDING OK; [check_cross_fire] rc=0 SCOPE OK.
- Hashes: task_tools.py 17af45361bc07400b31d190235b724ce2a0b785d088f60fb00f27507a44b8766; trust.extended.yaml 96ef94e9b56e91875f3c3ae2d0cb51391e39b23ef9f0f3521c12684fd1848ee2; task0.view.json c73a5c0719292c283d95eaf891576b373bb1a1a19dd5c66d9216d6c4158ec1af; task1.view.json f63b9277dcd9a37bd52fda1f1f9d1e02f06dd6414cf983ef117a4cde27fee4f4. Both shared inputs changed → charter section re-derived.
- contamination_disclosure: GT of rounds 1–2 seen in earlier revisions; the round-3 worklog section is read (permitted) after the blind derivation below is frozen.
- Coordinator ruling applied: half-up rules computed as RND(x + 1e-9, 2) on non-negative values; the sub-1e-9 residue is DSL-KNOWN, not a finding.

### charter_global_frozen (revision_3, before tasks/*.json or the round-3 worklog section were opened)
- Base section byte-identical to blueprint/products/trust.yaml. Mechanical sweep (sweep.py) clean: compute_basis quotes verbatim, baseline sentences in rule, policy_sources verbatim, disjoint bindings, no factor reads another factor transitively.
- Tools (task_tools.py 17af4536…): same six tools/uuid8s; rounding helper now `decimal.Decimal` quantize ROUND_HALF_UP (no forbidden import or substring); bodies create/update themselves, validate nothing; no ordering word in any docstring (grep empty); no example values. Results computed as RND(x + 1e-9, 2) per the coordinator ruling.
- Harness: /tmp/erl0074_pta_trust/r3.py, r3b.py.

### round-2 items re-checked
| id | revision_3 |
| --- | --- |
| R2-1 | closed — each sentence now selects "the most recent transfer to a … charge, where part of that transfer …", matching the depended-on rule and condition |
| R2-2 | the leave-night conflict is gone from task 0's world, but replaced by an unreal rule → R3-1 |
| R2-3 | closed — each run day priced at its own calendar year's rate |
| R2-4 | closed by removal (P1 no longer takes nights away) |
| R2-5 | closed — start month eligible; explicit "otherwise the charge as billed" |
| R2-6 | closed — ancillary keeps the balance less the part an authorization leaves out; bed-hold keeps every open balance (+ accruing nights) |
| R2-7 | hold_end_nights, run_day_numbering, unapplied removed; transfer_paid_part still a member; new members → R3-2 |
| R2-8 | closed — first chargeable night is the latest of the three dates |
| R2-9 | (i) closed ("no certification recorded … after its coverage start date" reads last_certification_date honestly); (ii) closed (effective date inside / before the block) |
| R2-10 | not closed → R3-5 |
| R2-11 | closed (count × max = sum test) |

### findings (revision_3)
**R3-1 SOURCE-FACTOR / SOURCE-POLICY RED — P2 keeps nothing for the run when a returned leave began inside it.** Rule: "Where a leave the resident has returned from began inside the unbilled run, nothing is kept for the run, because a night away at midnight is not a covered day and the run's covered days are known only once the coverage office books the month." (i) Realism: one night at home makes the business keep nothing for every other coinsurance day it knows is coming; the leave nights are on the bed-hold ledger (bedhold_day_booked), so the covered days are knowable — no business publishes "keep nothing". (ii) Compute ≠ rule (XF 12 decoy): `leave_last_from` is the latest bedhold_day_booked from_date across all reservations and is not tested for a return; a hold still in progress across a month end is booked at month end (bedhold_evt_day_counting) and its first night falls after the run's end, yet `DAYS(run_anchor, leave_last_from) >= run_start_gap` is true → run-up 0 where the rule keeps the run. No bite in task 0 (no leave inside the run).

**R3-2 SOURCE-FACTOR RED (XF 7; F-14 class) — tiers that are one expression on their domains.** P1 `transfer_paid_part` tiers 2+3 [transfer − wrong-amount returns]; P1 `credits_counted` all tiers [credits naming the charge − payer-coverage credits]; P2 `share_effective_split` tiers 1+2 [max(0, offset of the supplemental effective date from the run's first day)]; P2 `held_bed_buildup` tiers 1+2 [nights so far − the held tier's reserved nights per hospitalization − nights charged] (payer_reserved_days_per_hospitalization is 0 on the private-pay and Medicare skilled-stay tiers); P3 `credited_reconciliation_amount` tiers 1+3 [posted trueup decreases on other charges] (= the baseline); P3 `credited_not_eligible_amount` tiers 1+3 [posted not-eligible reductions] (= the baseline); P6 `ancillary_bills_kept` tiers 2+3 [max(0, ancillary open balance)]; P6 `bed_hold_bills_kept` tiers 1+2 [open balances + uncharged nights beyond the held tier's reserved nights].

**R3-3 SOURCE-FACTOR RED — fall-through tier is not the baseline.** P1 `payer_start_days`: fall-through "count no charged day: no payer covers the charge" vs baseline "every charged day"; P4 `hold_night_schedule`: fall-through "the charge's own daily rate" (nights before 2025-07-01) vs baseline "the schedule in effect on the date the charge was billed"; P6 `bed_hold_bills_kept`: fall-through "the open balance of every bed-hold charge" vs baseline 0.

**R3-4 SOURCE-POLICY / SOURCE-FACTOR RED (realism, XF 12 decoys) — reads that miss a charter-produced record.** (i) P3 `credited_not_eligible_amount` tier 2 credits "that estimate for each month from the requested eligibility date's month up to the month before the eligibility start date" whether or not an estimate was billed for the month — a retro request (requested date before the application month; estimates are billed only while pending) credits reductions for months never billed (world: requested 2026-04-01, application 06-12, start 07-01 → April and May credited 2 × 1389.70 that no charge carries). (ii) P5 `center_borne_days` gives 0 where the first recertification was signed late but the coverage office has not yet reversed the uncertified days (medicare_evt_day_counting: such days "are provider liable … and are never billed to the resident"). (iii) P5 owed days subtract leave-of-absence and hospital reversals but not booking_error reversals inside the covered window (medicare_evt_secondary_and_qmb: reversed covered days reduce the coinsurance). No bite in task 1 (request month = first estimate month; uncertified days already reversed; the booking_error day is past the last covered date).

**R3-5 SOURCE-FACTOR RED — factor floor after striking.** Survivors: P1 1 (refund_order); P2 3 (covered_run_end, coinsurance_share, held_room_tier); P3 2 (named_month_standing, named_month_amount); P4 3 (hold_notice_night, hold_room_tier, hold_refund_order); P5 4 (block_covered_end, block_plan_share, service_year_rate, coinsurance_refund_order — center_borne_days struck by R3-4 ii) — **P5 meets the floor**; P6 3 (resident_allowance_kept, coming_patient_pay_kept, recurring_services_kept).

Observations: O3-1 P5 `sec_days` reads the latest secondary charge on the block; a denied-and-rebilled carrier share would leave two rows (rule says "the days the coverage office charged the secondary party for"). O3-2 P5 `pay_last` cannot tell the trust transfer's own medicare payment row (posted as ACH) from an outside payment if the two carry different dates.

Pre-reveal charter verdict revision_3: R3-1, R3-2, R3-3, R3-4, R3-5.

### post-reveal addendum (revision_3; from the round-3 worklog T2 table, verified by recomputation — no GT value involved)
**R3-6 SOURCE-FACTOR RED (XF 5/6 — T2 fails: factor acts only through another factor's quantity).** Members: P1 `credits_counted` and P1 `refund_order` (with payer_start_days at baseline every charged day is improper, the refundable part is at least the payments made, and the return is capped at the paid part whatever the credits counted or the order); P2 `held_room_tier` (with held_bed_buildup at baseline no night builds up); P2 `share_effective_split` (with coinsurance_share at baseline every day is at the whole coinsurance); P3 `named_month_amount` (with named_month_standing at baseline the month keeps the charge as billed). The worklog's own T2 table labels each "gated by …".
Revised survivor counts (R3-5): P1 0; P2 2 (covered_run_end, coinsurance_share); P3 1 (named_month_standing); P4 3; P5 4 (meets the floor); P6 3.

### closing_checklist (revision_3, after the reveal at 2026-10-22T19:22:18Z)
- Gates 7/7 rc=0 (snapshot round 3); scopes disjoint and complete; trees hold, every edge bears weight, user write in each tree; blind = GT on every scored value in both tasks.
- Not closed: R3-1 … R3-6 (charter), T0-R3-X1 (task 0). P5 is the only policy meeting the factor floor.

VERDICT revision_3: task0=RED[T0-R3-X1,R3-2,R3-3,R3-5,R3-6,T0-R3-X2] task1=RED[R3-2,R3-3,R3-5,R3-6] charter=R3-1,R3-2,R3-3,R3-4,R3-5,R3-6

## revision_4
### entry (round 4, started 2026-10-22T19:31Z)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh resident_trust_fund_accounts 4` at 2026-10-22T19:30:59 — [check_extended] rc=0 EXTENDED OK; [check_task_tools] rc=0 TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 REPLAY OK; [check_solvability] rc=0 SOLVABILITY OK; [check_compute] rc=0 COMPUTE OK; [check_grounding] rc=0 GROUNDING OK; [check_cross_fire] rc=0 SCOPE OK.
- Hashes: task_tools.py 17af45361bc07400b31d190235b724ce2a0b785d088f60fb00f27507a44b8766 (unchanged since revision_3 → tool checks carried forward); trust.extended.yaml 9b901c35921fd8c1761344598d0007fcd5e11a974d20e451ad192f59735d6ea0 (changed → charter re-derived); task0.view.json 2068bdfb2942ca279343f0099528a63f0e7fa45a77ca960e33818ef40f95ad59 (changed); task1.view.json f63b9277dcd9a37bd52fda1f1f9d1e02f06dd6414cf983ef117a4cde27fee4f4 (unchanged since revision_3).
- contamination_disclosure: GT of rounds 1–3 seen earlier; round-4 worklog read only after the freeze below. Rounding ruling applied (RND(x + 1e-9, 2), residue DSL-KNOWN).

### charter_global_frozen (revision_4, before tasks/*.json or the round-4 worklog section were opened)
- Base section byte-identical; sweep.py clean (quotes, baseline sentences, policy_sources verbatim; disjoint bindings; no factor reads another factor). Tool module unchanged (17af4536…) → revision_3 tool conclusions carried forward.
- Changes found: P1 covered days zero without a payer and payer_start_days tiers conditioned on "start falls after the charge's first charged day"; P2's "nothing kept" sentence replaced by "every day of the run is reserved as a day in the center, a night away included …"; P3 not-eligible in-flight tier counts only months with an estimate billed before the start month; P4 earlier nights priced at the billed-date schedule; P6 bed-hold fall-through 0. P5 unchanged.

### round-3 items re-checked
| id | revision_4 |
| --- | --- |
| R3-1 | closed — the run reserves every day; P1 also counts every day from the payer's start, so the two policies agree on leave nights (the compute's leave read is gone) |
| R3-2 | **not closed** — every member still has the same ladder (P1 transfer_paid_part, credits_counted; P2 share_effective_split, held_bed_buildup; P3 credited_reconciliation_amount, credited_not_eligible_amount; P6 ancillary_bills_kept, bed_hold_bills_kept) plus a new member (R4-1) |
| R3-3 | closed — P1, P4, P6 fall-throughs now equal their baselines |
| R3-4 | (i) closed (only months with an estimate billed); (ii) and (iii) **not closed** — P5 unchanged |
| R3-5 | **not closed** |
| R3-6 | **not closed** — baselines unchanged: credits_counted and refund_order still act only through payer_start_days; held_room_tier through held_bed_buildup; share_effective_split through coinsurance_share; named_month_amount through named_month_standing |

### findings (revision_4)
**R4-1 SOURCE-FACTOR RED (XF 7; joins the R3-2 class) — P1 `payer_start_days` fall-through is the clamp of tiers 1/2.** Tiers: "Part A active and its coverage start date falls after the charge's first charged day → the charged days on or after it"; "… MA eligible and its start falls after … → the charged days on or after it"; "otherwise → every charged day". On the fall-through's Part A / MA part (start on or before the first charged day) the tier-1/2 method ("charged days on or after the start") gives every charged day — the "falls after" conjunct only marks where the count's floor binds (compute `… if DAYS(charge_from, payer_start) > 0 else charged_days`).
**Full R3-2/R4-1 member list (one class):** P1 payer_start_days (fall-through ≡ tiers 1/2 clamped), P1 transfer_paid_part (tiers 2+3), P1 credits_counted (all tiers: credits − payer-coverage credits), P2 share_effective_split (tiers 1+2: max(0, effective-date offset)), P2 held_bed_buildup (tiers 1+2: uncharged nights beyond the held tier's reserved nights, which are 0 on private-pay/Medicare tiers), P3 credited_reconciliation_amount (tiers 1+3 = posted trueups = baseline), P3 credited_not_eligible_amount (tiers 1+3 = posted not-eligible reductions = baseline), P6 ancillary_bills_kept (tiers 2+3: max(0, open balance)), P6 bed_hold_bills_kept (tiers 1+2: open balances + uncharged nights beyond reserved; tier 2 is tier 1 with no hold, and 2+3: max(0, open balance)).
**R4-2 SOURCE-POLICY RED (XF 12 decoy, new read) — P3 `ne_months`.** Rule: "estimates were billed for months before the eligibility start date's month → that estimate for each of those billed months"; compute counts `est_count − (months from the start month to the latest estimated month + 1)`, i.e. it assumes one estimate per month with no gap. A second estimate for one month (the rule's own "of two charges for the same month" case) or a month with no estimate shifts the count: world — estimates June, July, August, a second July estimate, no September, October; start 07-01 → rule: 1 (June); compute: 5 − 4 = 1 by luck here, but with estimates June, July, July-duplicate, October and start 07-01 → rule 1; compute 4 − 4 = 0.
**R3-4 (ii)(iii) carried:** P5 gives 0 center-borne days where the first recertification was signed late but no uncertified reversal is posted yet; booking_error reversals inside the covered window are not subtracted.
**R3-6 carried** (5 members above).
**R4-3 SOURCE-FACTOR RED — floor after striking (was R3-5).** Survivors: P1 refund_order struck (R3-6), payer_start_days/credits_counted/transfer_paid_part (R4-1 class) → 0; P2 covered_run_end, coinsurance_share → 2; P3 named_month_standing → 1; P4 hold_notice_night, hold_room_tier, hold_night_schedule, hold_refund_order → **4 (2 method, 2 parameter) — P4 now meets the floor**; P5 4 (meets the floor, center_borne_days struck by R3-4 ii); P6 resident_allowance_kept, coming_patient_pay_kept, recurring_services_kept → 3.
Observation O4-1: P2's justification "a night away during a Part A stay is billed instead as a held night at the private rate of the room held" holds only where a hold is elected (bedhold_election: "Holding the bed is the resident's choice"); the reserve itself is a stated conservative rule, so no second reading results.

Pre-reveal charter verdict revision_4: R3-2 (with R4-1), R3-4 (ii, iii), R3-6, R4-2, R4-3.

### post-reveal notes (revision_4; worklog round-4 section read, claims checked against the charters)
- T0-R3-X1 closed (private_tier_placement: a payer-converted agreement keeps its tier).
- R3-4 (ii): the worklog cites medicare_evt_day_counting ("days after a lapsed certification are provider liable, are reversed as uncertified_day") and keys P5 on the posted reversal; a seed with a late recertification and no reversal would carry an owed medicare correction (XF 30), so the read keyed on posted records is the accepted route → downgraded to observation O4-2.
- R3-4 (iii) stands as R4-4: a booking_error reversal inside the covered window (a day booked in error before the last covered date) stays an owed day in P5 although medicare_evt_secondary_and_qmb reduces the coinsurance for reversed days; the worklog's reason (no per-row date filter; the covered end already drops post-LCD booking errors) is a DSL limit, not a rule — the rule's own owed-days sentence omits these days.
- The worklog states R3-2/R3-5/R3-6 are structural and need a coordinator decision; nothing in the charter closes them.

### closing_checklist (revision_4)
- Gates 7/7 rc=0 (snapshot round 4); scopes disjoint/complete; trees hold, edges bear weight, user writes present; blind = GT in both tasks.
- Open: R3-2 with R4-1 (9 factors, one class), R3-6 (5 factors), R4-2 (P3 ne_months decoy), R4-4 (P5 booking_error days), R4-3 (floor: P1 0, P2 2, P3 1, P6 3 below; P4 and P5 meet it).

VERDICT revision_4: task0=RED[R3-2,R4-1,R3-6,R4-3] task1=RED[R3-2,R3-6,R4-3] charter=R3-2,R4-1,R3-6,R4-2,R4-3,R4-4

## revision_5
### entry (round 5, started 2026-10-22T19:41Z)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh resident_trust_fund_accounts 5` at 2026-10-22T19:40:48 — [check_extended] rc=0 EXTENDED OK; [check_task_tools] rc=0 TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 REPLAY OK; [check_solvability] rc=0 SOLVABILITY OK; [check_compute] rc=0 COMPUTE OK; [check_grounding] rc=0 GROUNDING OK; [check_cross_fire] rc=0 SCOPE OK.
- Hashes: task_tools.py 17af4536…8766 (unchanged); trust.extended.yaml 08c37520ffad1194e39021ff42b3e7f1692af9e5c726eb648bcab208933d7699 (changed → charter re-checked); task0.view.json 2068bdfb…ad59 and task1.view.json f63b9277…e4f4 (both unchanged since revision_4 → per-task world conclusions carried forward, recomputed under the new charter).
- Coordinator decisions applied: rounding RND(x + 1e-9, 2), residue DSL-KNOWN; a factor failing only XF A.6 T2 is accepted when it passes T1 on its task world, its tier sentence acts on a quantity the baseline defines and its baseline is the plain standard method (R3-6 class not RED on T2 alone; counted in the floor); coinciding tiers (R3-2/R4-1 class) remain RED.
- contamination_disclosure: GT of rounds 1–4 seen earlier; round-5 worklog read after the freeze below.

### charter_global_frozen (revision_5, before tasks/*.json or the round-5 worklog section were opened)
- Diff against the round-4 charter (copy taken at revision_4, sha 9b901c35…): only P1 payer_start_days/days_from_start, P3 ne_months (application-month count) and P5 owed days (booking-error reversals) changed; P2, P4, P6 unchanged. sweep.py clean; base byte-identical; tools unchanged.

### round-4 items re-checked
| id | revision_5 |
| --- | --- |
| R4-1 | closed — tiers are now Part A active / MA eligible / neither payer; the fall-through domain (no payer) is disjoint from the counted tiers and equals the baseline ("every charged day"; covered days then none by a plain sentence) |
| R4-2 | closed — ne months counted from the application month to the month before the start month (medicaid_evt_pending_estimate: "the resident pays an estimated patient pay each month" while pending); no estimate-row count left to miscount; probe 06-12 application / 07-01 start → 1 month |
| R4-4 | closed — booking-error reversals on or before the covered end are subtracted (one stretch: its days inside the covered window; several stretches: the block's days less every reversed day, capped at the covered end — the rule states this branch and its reason; it relies on the coverage office's reversals being posted, the premise accepted at O4-2) |
| R3-6 | accepted under the coordinator decision: P1 credits_counted/refund_order, P2 held_room_tier/share_effective_split, P3 named_month_amount each pass T1 on their task world, act on a quantity the baseline defines, and keep the plain standard-method baseline. **Except** the members that also coincide (R3-2) stay RED on that ground |
| R3-2 | **not closed** — unchanged ladders (members below) |
| R4-3 | **not closed** (recounted below) |

### findings (revision_5)
**R3-2 SOURCE-FACTOR RED (coinciding tiers; unchanged since revision_4).** Members: P1 `transfer_paid_part` (tiers 2+3 = transfer − wrong-amount returns); P1 `credits_counted` (all tiers = credits − payer-coverage credits); P2 `share_effective_split` (tiers 1+2 = max(0, effective-date offset)); P2 `held_bed_buildup` (tiers 1+2 = uncharged nights beyond the held tier's reserved nights, 0 on private-pay/Medicare tiers); P3 `credited_reconciliation_amount` (tiers 1+3 = posted trueups = baseline); P3 `credited_not_eligible_amount` (tiers 1+3 = posted not-eligible reductions = baseline); P6 `ancillary_bills_kept` (tiers 2+3 = max(0, open balance)); P6 `bed_hold_bills_kept` (tiers 1+2 = open balances + uncharged nights beyond reserved, tier 2 being tier 1 without a hold; tiers 2+3 = max(0, open balance)).
**R5-1 SOURCE-FACTOR RED — factor floor (replaces R4-3), counting accepted R3-6 members and striking R3-2 members.** P1: payer_start_days, refund_order → 2 (0 parameter); P2: covered_run_end, coinsurance_share, held_room_tier → 3; P3: named_month_standing, named_month_amount → 2; P4: hold_notice_night, hold_room_tier, hold_night_schedule, hold_refund_order → 4 ✓; P5: block_covered_end, center_borne_days, block_plan_share, service_year_rate, coinsurance_refund_order → 5 ✓; P6: resident_allowance_kept, coming_patient_pay_kept, recurring_services_kept → 3. P1, P2, P3, P6 below 4.
No new defect found in the changed reads (P1 payer selection; P3 MONTHS-based count; P5 booking-error stretch reads with tie-free single-row XLATEST on the one-stretch branch).

Pre-reveal charter verdict revision_5: R3-2, R5-1.

### post-reveal notes and closing_checklist (revision_5)
- Round-5 worklog read: it closes R4-1, R4-2, R4-4 (confirmed above) and states the R3-2 class and the floor are not closed (each member being, in its words, "one formula on their domains"); the coordinator decision keeps coinciding tiers RED.
- Gates 7/7 rc=0; scopes disjoint/complete; trees hold, edges bear weight, user writes present; blind = GT in both tasks.
- Open: R3-2 (8 members: P1 transfer_paid_part, credits_counted; P2 share_effective_split, held_bed_buildup; P3 credited_reconciliation_amount, credited_not_eligible_amount; P6 ancillary_bills_kept, bed_hold_bills_kept) and R5-1 (floor: P1 2, P2 3, P3 2, P6 3; P4 4 and P5 5 meet it).

VERDICT revision_5: task0=RED[R3-2,R5-1] task1=RED[R3-2,R5-1] charter=R3-2,R5-1

## revision_6
### entry (round 6, started 2026-10-23T06:03Z)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh resident_trust_fund_accounts 6` at 2026-10-23T06:02:27 — [check_extended] rc=0 EXTENDED OK; [check_task_tools] rc=0 TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 REPLAY OK; [check_solvability] rc=0 SOLVABILITY OK; [check_compute] rc=0 COMPUTE OK; [check_grounding] rc=0 GROUNDING OK; [check_cross_fire] rc=0 SCOPE OK.
- Hashes: task_tools.py 17af4536…8766 (unchanged); trust.extended.yaml 954a9fcdf04040bfa262988a8d12fcf492295bdd1f9091a92dcdafe5cb55901e (changed); task0.view.json c732d5a3fa5b995a60b2605a83d67c96fd7e7b9fa4ec09250733bcad7c0a1288 (changed); task1.view.json f63b9277…e4f4 (unchanged).
- Decisions applied: rounding RND(x + 1e-9, 2) (residue DSL-KNOWN); T2-only failures accepted per the coordinator decision; coinciding tiers remain RED. contamination_disclosure: earlier GT seen; round-6 worklog read after the freeze.

### charter_global_frozen (revision_6, before tasks/*.json or the round-6 worklog section were opened)
- Base byte-identical; sweep.py clean; tools unchanged (17af4536…). Copy of this charter kept at /tmp/erl0074_pta_trust/r6_charter.yaml for the next diff.
- Changed: P1 `credits_counted` (now keyed on the ancillary account's tier) and `transfer_paid_part` (ancillary ledger's applied trust payment / authorization amount / whole transfer; unauthorized or duplicate return → nothing as a plain sentence); P2 `share_effective_split` and `held_bed_buildup` made plain sentences, new factors `run_year_rate` and `hold_first_night`. P3–P6 unchanged.
- Coinciding test applied (the R4-1 criterion the coordinator ruled on): two tiers coincide when one tier's own method or value, read on the other tier's domain, already gives that tier's value (e.g. "the charged days on or after a start date" on a world whose start precedes the charge = every charged day). On re-applying it to every ladder, two P5 members present since revisions 2–3 also meet it; they were missed in revisions 3–5 and are listed now (disclosed).

### round-5 items re-checked
- R3-2 P1 transfer_paid_part, credits_counted: re-laddered, tiers no longer coincide — closed as coinciding (credits_counted fails on another ground, R6-2).
- R3-2 P2 share_effective_split, held_bed_buildup: now plain sentences — closed.
- R3-2 P3 credited_reconciliation_amount / credited_not_eligible_amount, P6 ancillary_bills_kept / bed_hold_bills_kept: unchanged — **not closed**.
- R5-1 floor: recounted below — **not closed**.

### findings (revision_6)
**R6-1 SOURCE-FACTOR RED (coinciding tiers) — full member list.** P3 `credited_reconciliation_amount` (tier 1 "those trueup decreases" on tier 3's domain = 0); P3 `credited_not_eligible_amount` (same with not-eligible reductions); P6 `ancillary_bills_kept` (tier 2 "that open balance" on tier 3's domain = 0); P6 `bed_hold_bills_kept` (tier 1 "open balances plus the hold's uncharged nights" with no hold = tier 2; tier 2 on tier 3's domain = 0); **P5 `block_covered_end`** (tier 2 "the owed days run through that last covered date" where the last covered date is on or after the block's last day = every day the charge priced = fall-through; missed since revision_2); **P5 `block_plan_share`** (tier 4 "that coverage's share on the days the secondary party was charged for, the whole coinsurance on the other owed days" read on tiers 1–3 and the fall-through gives each of their values, because medicare_evt_coinsurance charges the secondary party for every coinsurance day the supplemental coverage is in effect and charges none without it; missed since revision_3).
**R6-2 SOURCE-FACTOR RED (unreal ladder condition) — P1 `credits_counted` keyed on the account's current tier.** "where the ancillary account is in the consolidated billing tier, every credit naming the charge except a credit for a consolidated billing item; where … Medical Assistance, Part B or Medicare Advantage tier … except a credit for a payer-covered item …". Whether a credit "records the improper part itself" depends on the credit's reason, not on the tier the account sits in today (ancillary_account_lifecycle moves the account with the payer). World: June charge under the Medical Assistance tier credited payer_covered_item, account moved to the consolidated-billing tier in July → tier 1 counts the coverage credit against the unpaid balance, which the rule's own reason forbids.
**R6-3 SOURCE-POLICY RED (XF 12 prior-period decoy) — P1 payer read is the current payer, not the payer of the charge's days.** `payer_start` = coverage start of the active Part A episode, else the eligible MA start. World: the most recent ancillary transfer paid a June charge covered by Medical Assistance; Part A became active in July → days on or after the July start = 0 → nothing returned, though MA covered every June day (ancillary_payer_coverage: "A Medicaid resident is never charged for anything the Medicaid per diem includes").
**R6-4 SOURCE-POLICY RED (rule/compute edge, XF 11) — P2 `run_year_rate`.** Rule: "a coinsurance day of the run falls in 2026 → the 2026 rate". Compute: `rate_26 = K(2026) if run_anchor < '2026-12-31' else latest_rate` — with no block booked the anchor is the coverage start; a coverage starting 2026-12-31 (prior SNF days ≥ 20) puts its one 2026 coinsurance day at the latest charge's rate (0 with none). Same for `rate_25` at 2025-12-31.
**R6-5 SOURCE-FACTOR RED — factor floor (replaces R5-1).** P1: payer_start_days, transfer_paid_part, refund_order (accepted R3-6) → 3; P2: covered_run_end, coinsurance_share, run_year_rate, hold_first_night (acts through the held nights; T1 moves; accepted), held_room_tier (accepted) → 5 ✓; P3: named_month_standing, named_month_amount → 2; P4: 4 ✓; P5: center_borne_days, service_year_rate, coinsurance_refund_order → 3; P6: resident_allowance_kept, coming_patient_pay_kept, recurring_services_kept → 3. Below the floor: P1, P3, P5, P6.
Re-checked and not coinciding (value test): P2 covered_run_end (a last covered date after today gives a run past yesterday), P2/P4 notice-night factors (the delivery date on the other domain is earlier than the first held day — a different value, inert only through the downstream "latest of"), P1 payer_start_days (fall-through domain has no payer start), P2 run_year_rate, P4 hold_night_schedule, P3 named_month_standing, P6 coming_patient_pay_kept, recurring_services_kept.

Pre-reveal charter verdict revision_6: R6-1, R6-2, R6-3, R6-4, R6-5.

### post-reveal notes and closing_checklist (revision_6)
- Worklog round-6 section read. Its credits_counted reason ("the credit of another payer's coverage settled the charge for days that payer covered") makes the tier condition coherent with P1's current-payer scope: R6-2 withdrawn as an unreal-ladder finding; R6-3 kept as observation O6-2 (P1 returns only the current payer's days; another payer's coverage is settled through that payer's posted credit — the "posted at once" premise accepted at O4-2). P1 floor recounted: payer_start_days, credits_counted (T2-only, accepted), transfer_paid_part, refund_order → 4 ✓.
- T0-R6-X1 withdrawn to O6-1 (consistency with the accepted task-1 rate-year error state).
- R6-1 P5 members are additions found by re-applying the coinciding test to every ladder this round; they were present (and missed) since revisions 2–3.
- Gates 7/7 rc=0; scopes disjoint/complete; trees hold; blind = GT in both tasks.
- Floor (with accepted T2-only members): P1 4 ✓, P2 5 ✓, P3 2 ✗, P4 4 ✓, P5 3 ✗, P6 3 ✗.
- Open: R6-1 (6 members: P3 credited_reconciliation_amount, credited_not_eligible_amount; P5 block_covered_end, block_plan_share; P6 ancillary_bills_kept, bed_hold_bills_kept), R6-4 (P2 run_year_rate rate_25/rate_26 anchor edge), R6-5 (floor P3, P5, P6).

VERDICT revision_6: task0=PASS task1=RED[R6-1,R6-5] charter=R6-1,R6-4,R6-5

## revision_7
### entry (round 7, started 2026-10-23T06:17Z)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh resident_trust_fund_accounts 7` at 2026-10-23T06:16:24 — [check_extended] rc=0 EXTENDED OK; [check_task_tools] rc=0 TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 REPLAY OK; [check_solvability] rc=0 SOLVABILITY OK; [check_compute] rc=0 COMPUTE OK; [check_grounding] rc=0 GROUNDING OK; [check_cross_fire] rc=0 SCOPE OK.
- Hashes: task_tools.py 17af4536…8766 (unchanged); trust.extended.yaml 0035432fa4dcad50b5e5e8f3e864f1930ec78f90ad3dfcc8e30c16d685b022d5 (changed; diffed against the revision_6 copy 954a9fcd…); task0.view.json c732d5a3…1288 and task1.view.json f63b9277…e4f4 (both unchanged).
- Decisions applied: rounding RND(x + 1e-9, 2); T2-only failures accepted; coinciding tiers RED. contamination_disclosure: earlier GT seen; round-7 worklog read after the freeze.

### charter_global_frozen (revision_7, before tasks/*.json or the round-7 worklog section were opened)
- Diff against the revision_6 charter: only P2 `rate_25`/`rate_26` conditions and P5 `block_covered_end` / `block_plan_share` (with the effective-date split moved into a plain `share_days` sentence) changed. Base byte-identical; sweep.py clean (quotes verbatim, baseline sentences in rule, no factor reads another); tools unchanged.

### round-6 items re-checked
| id | revision_7 |
| --- | --- |
| R6-4 | closed — `(run_anchor or '') <= '2026-12-31'` (and 2025) now prices a run day in that year at that year's rate whatever the anchor; a coverage starting 2026-12-31 with no block gets 217.00 |
| R6-1 P5 block_covered_end | closed — tiers are QIO upheld / a last covered date on file (through it, never past the block's last day) / no last covered date; the fall-through's domain (no date) is disjoint and the tiers no longer coincide; decoy (last covered date before the block's first day) → 0 days, as the rule says |
| R6-1 P5 block_plan_share | closed — tiers now select the share by coverage (K / L / full-coinsurance or QMB / otherwise), distinct constants; which days take it is a plain sentence (`share_days`) |
| R6-1 P3 credited_reconciliation_amount, credited_not_eligible_amount | **not closed** (unchanged) |
| R6-1 P6 ancillary_bills_kept, bed_hold_bills_kept | **not closed** (unchanged) |
| R6-5 floor | P5 back to 5 ✓; P3 2 and P6 3 still below |

### findings (revision_7)
**R7-1 SOURCE-FACTOR RED (coinciding tiers; carried from R6-1).** Members: P3 `credited_reconciliation_amount` (tier 1 "those trueup decreases" on tier 3's domain = 0), P3 `credited_not_eligible_amount` (same with not-eligible reductions), P6 `ancillary_bills_kept` (tier 2 "that open balance" on tier 3's domain = 0), P6 `bed_hold_bills_kept` (tier 1 with no hold = tier 2; tier 2 on tier 3's domain = 0).
**R7-2 SOURCE-FACTOR RED — floor.** P1 4 ✓, P2 5 ✓, P3 2 (named_month_standing, named_month_amount), P4 4 ✓, P5 5 ✓, P6 3 (resident_allowance_kept, coming_patient_pay_kept, recurring_services_kept). Below: P3, P6 — both task 1's.
No new defect in the changed reads.

Pre-reveal charter verdict revision_7: R7-1, R7-2.

### post-reveal notes and closing_checklist (revision_7)
- Worklog round-7 section read: claims for R6-4 and the two P5 members confirmed above; P3/P6 stated as not closable inside the claimed policy set without a coordinator decision.
- Gates 7/7 rc=0; scopes disjoint/complete; trees hold; blind = GT in both tasks; floor P1 4, P2 5, P4 4, P5 5 ✓ — P3 2, P6 3 ✗.
- Open: R7-1 (P3 credited_reconciliation_amount, credited_not_eligible_amount; P6 ancillary_bills_kept, bed_hold_bills_kept), R7-2 (floor P3, P6).

VERDICT revision_7: task0=PASS task1=RED[R7-1,R7-2] charter=R7-1,R7-2

## revision_8
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh resident_trust_fund_accounts 8` at 2026-10-23T06:19:37 — [check_extended] rc=0 EXTENDED OK; [check_task_tools] rc=0 TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 REPLAY OK; [check_solvability] rc=0 SOLVABILITY OK; [check_compute] rc=0 COMPUTE OK; [check_grounding] rc=0 GROUNDING OK; [check_cross_fire] rc=0 SCOPE OK.
- Source hashes equal the revision_7 snapshot: task_tools.py 17af4536…8766, trust.extended.yaml 0035432f…22d5, task0.view.json c732d5a3…1288, task1.view.json f63b9277…e4f4 → nothing changed; every revision_7 conclusion carries forward by reference.
- Open items at revision_7 were R7-1 and R7-2 only.
- COORDINATOR DECISION recorded (logged by the coordinator as BLUEPRINT-KNOWN): R7-1 (coinciding tiers in P3 credited_reconciliation_amount, credited_not_eligible_amount and P6 ancillary_bills_kept, bed_hold_bills_kept) and R7-2 (factor floor: P3 2/4, P6 3/5) are WAIVED. The coordinator's reason: the frozen trust charter is thin, and the base sentences the reworker cited leave P3 and P6 without further genuine levers. A different trust write was checked and none was found. The members agree with base on every in-scope world and move no scored value, GT or unique solution. Auditor's note: the waiver is a coordinator decision. The audit finding itself stands as written in revision_7. It is not counted RED in this verdict.
- Per task: task 0 — PASS (revision_7). Task 1 — chain PASS, unique solution PASS (blind = GT), policy self-consistency PASS; factor relationship RED only on the waived R7-1/R7-2.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9
### entry (round 9, started 2026-10-23T09:56Z)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh resident_trust_fund_accounts 9` at 2026-10-23T09:55:33 — [check_extended] rc=0 EXTENDED OK; [check_task_tools] rc=0 TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 REPLAY OK; [check_solvability] rc=0 SOLVABILITY OK; [check_compute] rc=0 COMPUTE OK; [check_grounding] rc=0 GROUNDING OK; [check_cross_fire] rc=0 SCOPE OK.
- Hashes: task_tools.py 17af4536…8766 (unchanged); trust.extended.yaml 1f2e7e1aec9ecc97e50095246fd5f24c97f39c6627cd904ee165d462fc717001 (changed; diffed against the revision_7/8 copy 0035432f…); task0.view.json c732d5a3…1288 and task1.view.json f63b9277…e4f4 (unchanged).
- Inputs read: audits/render_source/resident_trust_fund_accounts/render_r1.md (in full; renderer findings 1–3 and three non-blocking notes); round-8 worklog section (read after the charter check below — disclosed). R7-1/R7-2 waiver stands. Rounding ruling RND(x + 1e-9, 2).
- Auditor's note: renderer findings 1 (available balance against the base measure counting every held deposit) and 2 (0.00 patient pay read as absent) are classes these audits missed in revisions 2–8. They are taken up here.

### charter re-check (revision_9)
- Diff against the revision_7/8 charter: P1 presence tests (`returned_void`, `applied_n`, `auth_n` counts); P2 spare balance (`held_deposits`, `pna_left`); P3 `held_deposits`, `available`, `pna_left`, `month_amount` guard, `tu_n`/`ne_n`, `recon_credit`, `ne_credit`, result cap; P4 schedule wording for earlier nights; P6 `held_deposits`/`available` and the no-room-tier sentence; baselines now carry the plain sentences. Base byte-identical; sweep.py clean; tools unchanged.

### render_r1 findings re-checked (classes swept on every policy)
| item | revision_9 |
| --- | --- |
| Finding 1 — available balance counts only the latest held deposit (P3, P6 vs `trust_msr_available_balance`, `within_balance`) | closed. Class = every balance a transfer, authorization or withdrawal may draw on: P2 spare, P3 available, P6 available now subtract every deposit with available_date after today (`SUM(all) − SUM(within_months=100000, date_field='available_date')`; check_compute `_within` keeps a row exactly when its available_date is on or before today). P1, P4, P5 are returns (no balance cap). Probe (task 1 copy): check 500.00 held to 10-27 plus a pension 300.00 available 10-22 → 500.00 excluded. |
| Finding 2 — 0.00 patient pay read as absent | closed. Class = every presence test on an amount, swept by script over all six computes: P3 `month_amount` now tests the eligible case, `recon_credit` drops the patient-pay guard, posted trueup/not-eligible reductions detected by row count; P1 applied payment / authorization / void returns detected by row count. Remaining bare numeric tests are deliberate: P1 `charged_days` as a divisor guard, P4 room-tier rate `… or charge_rate` (the rule's "where no room tier can be priced"), date-string tests. Probe: case patient pay 0.00, no trueup posted → reconciliation 3 × 1389.70 = 4169.10, month patient pay 0.00, as the rule says. |
| Finding 3 — PNA on Medicaid payee accounts | closed. Class = every bill-transfer size the charter sets: P3 caps at the available balance less the case's PNA where `center_is_representative_payee` and `medicaid_pna_retained`; P2's authorization spare does the same; P6 already keeps the PNA for every eligible tier. Probe: task 1 account switched to the payee tier → pna_left 45.00, transfer unchanged at 486.50 (balance ample). |
| Note — P2 p0/plan_effective not in the baseline | closed. The baseline rule now carries the share-days and held-nights plain sentences. |
| Note — P4 billed_rate reads `charge_billed`, a binding listed in hold_night_schedule | rule gap closed. The rule now states "a charge billed before 2025-07-01 … keeps the charge's own daily rate". Placement remains: the plain `billed_rate` reads a record listed in the factor's bindings. It is not a rule-vs-compute mismatch, and substituting the factor's baseline overrides `cut_*` only. Recorded as observation O9-1 under the placement stop rule. |
| Note — no room tier prices nights at 0 (P2, P6) | closed. Both rules now say a reservation that records no room tier prices no night. |
- Regression check: harness recomputation of all six computations on both worlds. Task 0: P1 67.11, P2 56.11. Task 1: P3 486.50, P4 3280.75, P5 1837.92, P6 4595.64. All T1 figures and all-baseline figures are unchanged. These equal tasks/0.json and tasks/1.json (expected, baseline_result and factor_sensitivity, read after the check; earlier GT seen — disclosed). Problem chains unchanged; the floor is unchanged (P3/P6 under the standing R7-1/R7-2 waiver).
- Round-8 worklog section read; its claims match the checks above.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN

## revision_10
### entry (round 10, started 2026-10-23T11:04Z)
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh resident_trust_fund_accounts 10` at 2026-10-23T11:03:49 — [check_extended] rc=0 EXTENDED OK; [check_task_tools] rc=0 TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 REPLAY OK; [check_solvability] rc=0 SOLVABILITY OK; [check_compute] rc=0 COMPUTE OK; [check_grounding] rc=0 GROUNDING OK; [check_cross_fire] rc=0 SCOPE OK.
- Hashes: task_tools.py 17af4536…8766 (unchanged); trust.extended.yaml cddc8af02869543e17c6fcd027b9d4fb6a1c674ecf46beed8ffcdb2f4606d31e; task0.view.json feb66f236adfdae9d8e5f54f42668930b5366185ba4e6055a6b187b9268f1279; task1.view.json 7afcf12d9fb6c0a4f1dedebc3af807a2dd2c16b90f7b2150393667097db6dc57 (all three changed).
- Inputs read: audits/policy_kb/resident_trust_fund_accounts/_kb_verdict.md (S1–S8; S4 not routed); the round-9 REWORK section of the worklog (claims and its seed pass — disclosed; it states gold moved for task 1's bed-hold return and spare amount without printing the new figures); docs/bedhold, docs/medicare, docs/medicaid, docs/ancillary, docs/private as needed. R7-1/R7-2 waiver stands; rounding RND(x + 1e-9, 2).

### routed source items re-checked (revision_10)
| item | revision_10 |
| --- | --- |
| S1 — P4 priced a charge the Bed-Hold corpus prices by agreement | closed. P4 now names the charge types that docs/bedhold `charge_basis` ("Current basis") excludes from the base clause. These are the single resident-private entry of an ended Private Pay Hospital Leave hold; the opening entry, or the closing entry once ended, of a multi-entry Medicaid Hospital Leave Reserved Bed; and the opening or closing entry of a released multi-entry Private Pay Therapeutic Leave hold. For these P4 takes the posted (signed or posted) charge as the amount due. Compute `agreement_priced` is an exact record test on variant, status, resident-private entry count and the entry's first/last day, and it matches the hubs hs/hc/ho/tc/to. Class (P2, P6 held-night reserves): both rules now state that a held night is reserved at the full bed-hold rate because an agreement's extended-hold percent or dietary credit depends on the leave's final length. Task 1's leave is a returned single-entry therapeutic hold, which the base clause prices: 13 × 384.00. |
| S2 — P5 baseline compute vs rule | closed. The covered end is a plain clause read in the baseline as well, so the all-baseline figure is 217.00, the KB memo's figure. The replacement factor `coinsurance_paid_part` (applied ACH payment / authorization / whole transfer) has tiers on distinct records and moves on task 1 (1845.16). |
| S3 — September coinsurance at 209.50 (task 0) | closed. 9531985d is now 20 × 217.00 = 4340.00, as medicare_evt_coinsurance prices it. run_year_rate has become a plain sentence. The new factor `run_start_day` (block booked / coverage start / no episode) has no coinciding tiers and moves on task 0. |
| S5 — trust transfer as ACH on the Medicare ledger | closed. P5's rule states it ("the coverage office's list of payment methods naming no other method for it"). The 62.00 remainder returns to the payer as in medicare_evt_payment_posting and is posted 01-16 as refund_from_center. |
| S6 — held tier vs converted agreement | closed. Both worlds rest on private_tier_placement ("Only an open, active agreement changes tier"): the semi-private bed is taken at conversion, and the reservation records the bed held. |
| S7 — owed Medicaid reconciliation moving P3 | closed. With equal pending estimates, P3 projects the reconciliation whether it is unposted, partly posted or fully posted. Posted reductions are read only where the estimates differ. XF 30 holds. |
| S8 — resources above the MA limit on 07-01 | closed. The 10000.00 check is now deposited 07-06, so the balance at the first moment of July is 62.24 and of August 1907.56. |
- Class sweep for "every seeded cross-product row matches the owning product's published rules": the reworker's seed table (round-9 worklog, read and disclosed) was spot-checked against docs/bedhold (charge basis, notice terms, billing terms), docs/medicare (pricing year, payment posting remainder) and the Medicaid accrual rule, and it holds. The remaining premise rows (8de9416f, 49354ce0, c642cc84, f0840981, 1e5a41d1) are the error states the return policies exist to correct, each with the owning product's correction capped or posted. Rows no gold step reads (June accrual / re-charge pricing) are accepted residue.
- Mechanical: sweep.py clean; base byte-identical; tools unchanged. Factor floor: P1 4, P2 5, P4 4, P5 5 meet it; P3 and P6 fall under the standing R7-1/R7-2 waiver. No coinciding tiers in P1, P2, P4 or P5 (value test re-applied to run_start_day and coinsurance_paid_part).
- Gold moved (task 1 bed-hold return 3709.22, spare 5084.99). Both were re-derived blind before the reveal, and both equal GT.

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN

## revision_11
- Snapshot run by this auditor: `/tmp/erl0074_coord/snapshot.sh resident_trust_fund_accounts 11` at 2026-10-23T11:23:36 — [check_extended] rc=0 EXTENDED OK; [check_task_tools] rc=0 TASK TOOL CONTRACT OK; [replay_tasks --check] rc=0 REPLAY OK; [check_solvability] rc=0 SOLVABILITY OK; [check_compute] rc=0 COMPUTE OK; [check_grounding] rc=0 GROUNDING OK; [check_cross_fire] rc=0 SCOPE OK.
- Hashes: task_tools.py 17af4536…8766 (unchanged); trust.extended.yaml c58f2f8fbbb4a26de2ada0150311a8e3c9f1e8e640f261c205c31c1cee613115 (changed); task0.view.json feb66f23…1279 and task1.view.json 7afcf12d…6dc57 (both unchanged since revision_10).
- Read: _kb_verdict.md revision_2 (source item N2) and the round-10 worklog section (disclosed). The R7-1/R7-2 waiver stands.
- Diff against the revision_10 charter (copy cddc8af0…): compute, factors, prerequisites and params are unchanged in all six policies. Only rule and baseline text changed, in P2 (rule + baseline), P3 (baseline) and P4 (rule + baseline). Base byte-identical; sweep.py clean (every compute_basis quote and every baseline sentence verbatim in its rule).
- **N2 closed.** P2's run sentence now reads "the days of the active Part A episode from the run's first day through the run's end". The standard-method sentence says the run "starts on the episode's coverage start date and ends yesterday, every day of the episode from that date counted in it". That is the baseline compute (start_off 0, booked_before 0, end yesterday). The "not yet booked" reason now sits only in run_start_day's own sentence. Neither "not yet booked" nor "unbilled" remains in the baseline.
- **Class sweep** (baseline text that pre-empts a factor tier or differs from the baseline compute), every policy:
  - P1: baseline text gives 120.00 = all-baseline compute.
  - P2: 0.00. Run 09-09..10-20 at the whole coinsurance swamps the balance.
  - P3: 1389.70. The month-standing ladder left the baseline; "every month's patient pay is the charge as billed" remains.
  - P4: 2616.00. Every night 06-10..06-24 (last held day 06-24) at the agreement tier on the billing-date schedule, 15 × 436.00 = 6540.00; excess 2616.00 to the transfer. The nightly-rate sentence now says "the rate schedule applying to that night", leaving the night-date tier to hold_night_schedule.
  - P5: 217.00. P6: 6939.39.
  - No baseline sentence states a tier.
- Regression check by harness on both unchanged worlds. Task 0: 67.11 / 56.11. Task 1: 486.50 / 3709.22 / 1837.92 / 5084.99. Every T1 and all-baseline figure is identical to revision_10, and identical to the gold read in revision_10.

VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN
