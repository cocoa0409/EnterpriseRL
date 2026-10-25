INSTANTIATE round 1: gates 7/7 green

## REWORK round 2 (audit revision_1: task0=RED task1=RED charter=C1..C10)

### Redesign (why)
- In standard-coordination plans (Plus, Premier, Elite) a binding standard ceiling and a network-coinsurance factor cannot both move the result; outside step-1 scopes and rollover worlds no claim computation reaches 6 valid factors; an estimate has a real method only on a rollover or pediatric world, and pediatric worlds post nothing to the maximum. The six policies were rebuilt to fit those facts with real carrier ladders only:
  - task 0 (group Premier 2000, late entrant, DHMO transfer, rollover): dental_ext_initial_wait_reprocess (6) -> dental_ext_estimate_request (4, owner=user). Edge: value_input, room.
  - task 1 (group Classic 1250 after a Value 1000 plan year, DHMO transfer, secondary coverage): dental_ext_claim_appeal_dispute (4, owner=user) <- dental_ext_upgrade_denial_reprocess (5) <- dental_ext_grace_denial_reprocess (6) <- dental_ext_upgrade_paid_reprocess (5). Edges: value d_paid, value ded_room, state (date-of-service order).
  - Dropped: dental_ext_overturned_reprocess (its seed contradicted the base appeal trigger), dental_ext_pended_line_release and the exchange world; new tools reprocess_wait_denial_e5c18a2f, reprocess_upgrade_denial_9a74d03b, reprocess_grace_denial_4c0e9d17, reprocess_upgrade_paid_line_3fd2b6c9; kept file_claim_appeal_86dbcb40 and submit_estimate_request_d87add4f.
- Every prerequisite rests on a state the charter produces: base denies or pays at the prior plan's level when no prior coverage is documented (the extended rules credit the person's own Cascade DHMO on reprocessing); the grace-period denial is a claims error, which the base dental_claim_line_adjusted event names as a reprocessing cause.
- Known residual: the June 2025 group invoice of task 1 is priced at the prior plan year's Value 1000 group rates, which the contract row (renewed 2025-07-01) no longer carries.

### Items closed
- C1: removed every one-method-as-two-tiers ladder (deductible_after_backout, maximum_room_after_backout, deductible_satisfied_so_far); backing out a replaced decision's postings and the remaining deductible are plain base readings.
- C2: the share-base substitution is a parameter factor (gracefix_share_start: 0.00 / billed / allowed); the *_share_adjustment method factors change shape (primary-payment deduction, pediatric out-of-pocket cap).
- C3: every tier is reachable in its own scope (any-market scopes where pediatric or rollover tiers live; the estimate covers any procedure; the late in-network tier lives only in the step-1 grace-period rule); the estimate has 4 valid factors incl. a method.
- C4: the initial-wait and estimate rules exclude enrollments whose plan changed; the three task-1 reprocessing rules and the appeal implement the upgrade clause and scope out prior-covered lines they do not decide.
- C5: pediatric treatment implemented wherever in scope (no annual maximum, in-network share capped at the one-child out-of-pocket remaining, tools post the pediatric out-of-pocket accumulator); two-plus-children cases scoped out; the appeal is group-only.
- C6: out-of-network preventive tier added where preventive lines are in scope; the waiting-period rules state preventive services never wait.
- C7: timely filing implemented in the step-1 grace-period rule (late line denied, payment 0.00, in-network share 0.00); the other rules' lines passed filing before their denial or payment.
- C8: rollover implemented in the initial-wait rule (limit factor; the tool books the rollover draw) and the estimate (benefit-limit tier); the other rules and the appeal scope rollover plans out.
- C9: DHMO credit reads the person's terminated DHMO whose termination date is the day before this coverage's effective date (unique key, probes below) and counts calendar months with both end months counted.
- C10: the estimate's pended-line gate is gone; every remaining edge is a same-person value edge or a same-person date-of-service ordering.
- T0-F1: the appeal rule and the tool docstring say a second-level filing names the claim line its first-level filing named, even after reprocessing.
- T0-F2: no tier is readable off a stamp (corrected lines' original decisions are denials or used another allowance).
- T0-F3: unreal backout ladders removed.
- T0-F4: group enrollments funded by the employer's Cascade Group List Bill account (contract rate x census by tier, supplementary invoice for the joining month, every remittance); DHMO direct-bill ledgers complete with confirmed closure requests.
- T0-F5: all proof text regenerated from the verified computations.
- T1-F1: the overturned-decision prerequisite is gone; the tree rests on charter-producible states.
- T1-F2: see C10.
- T1-F3: the estimate allowance is a plain lesser-of rule; the recorded allowance differs from the figure used.
- T1-F4: estimate 4 valid factors with a method; release ladder gone; share ladders rebuilt; dead tiers removed.
- T1-F5: exchange world dropped; every ledger priced and completed under the billing charter.

### (a) Decoy / absent-record probe table (scratch copies of each task world at the handling-time state of each computation; real task tools replayed for the earlier writes)

| task | policy | read | decoy / absent record | before | after | expected | outcome |
|---|---|---|---|---|---|---|---|
| 0 | initial_wait_reprocess | CFIELD dhmo (credit) | second record: older terminated DHMO 2018-03-01..2019-06-30 listed first | 250.0 | 250.0 | unchanged | unchanged |
| 0 | initial_wait_reprocess | CFIELD dhmo (credit) | cancelled DHMO ending 2025-02-28 listed first | 250.0 | 250.0 | unchanged | unchanged |
| 0 | initial_wait_reprocess | CFIELD dhmo (credit) | another person's terminated DHMO with the same dates | 250.0 | 250.0 | unchanged | unchanged |
| 0 | initial_wait_reprocess | CFIELD dhmo (credit) | DHMO ended two days before coverage (a break): tier 1 not met | 250.0 | 1400.0 | moves per rule (credit and clause tiers fail) | moves |
| 0 | initial_wait_reprocess | CFIELD dhmo (credit) | absent DHMO record | 250.0 | 1400.0 | moves per rule (tier 3, no credit) | moves |
| 0 | estimate_request | CFIELD dhmo (credit) | second record: older terminated DHMO 2018-03-01..2019-06-30 listed first | 260.0 | 260.0 | unchanged | unchanged |
| 0 | estimate_request | CFIELD dhmo (credit) | cancelled DHMO ending 2025-02-28 listed first | 260.0 | 260.0 | unchanged | unchanged |
| 0 | estimate_request | CFIELD dhmo (credit) | another person's terminated DHMO with the same dates | 260.0 | 260.0 | unchanged | unchanged |
| 0 | estimate_request | CFIELD dhmo (credit) | DHMO ended two days before coverage (a break): tier 1 not met | 260.0 | 560.0 | moves per rule (credit and clause tiers fail) | moves |
| 0 | estimate_request | CFIELD dhmo (credit) | absent DHMO record | 260.0 | 560.0 | moves per rule (tier 3, no credit) | moves |
| 0 | initial_wait_reprocess | XLATEST dhmo_services (clause) | extraction of another tooth (30) on the same date | 250.0 | 250.0 | unchanged | unchanged |
| 0 | initial_wait_reprocess | XLATEST dhmo_services (clause) | second extraction record of tooth 19 on another date | 250.0 | 250.0 | unchanged | unchanged |
| 0 | initial_wait_reprocess | XLATEST dhmo_services (clause) | non-extraction service on tooth 19 on the extraction date | 250.0 | 250.0 | unchanged | unchanged |
| 0 | initial_wait_reprocess | XLATEST dhmo_services (clause) | absent extraction record | 250.0 | 1400.0 | moves per rule (clause tier 3) | moves |
| 0 | initial_wait_reprocess | LATEST line selection | older DENIED_WAITING_PERIOD line (prior benefit year) | 250.0 | 250.0 | unchanged | unchanged |
| 0 | initial_wait_reprocess | LATEST line selection | reprocessed (adjusted) row of another line decided later | 250.0 | 250.0 | unchanged | unchanged |
| 0 | initial_wait_reprocess | SUM postings | reversed posting pair in 2026 (posting + reversal) | 250.0 | 250.0 | unchanged | unchanged |
| 0 | initial_wait_reprocess | SUM postings | prior-benefit-year deductible and maximum postings | 250.0 | 250.0 | unchanged | unchanged |
| 0 | estimate_request | LATEST estimate selection | voided estimate line issued later | 260.0 | 260.0 | unchanged | unchanged |
| 0 | estimate_request | LATEST estimate selection | older issued estimate for another procedure | 260.0 | 260.0 | unchanged | unchanged |
| 0 | estimate_request | XLATEST dhmo_services (extraction date) | older extraction record of tooth 19 | 260.0 | 260.0 | unchanged | unchanged |
| 0 | estimate_request | SUM rollover | rollover draw booked and reversed in pairs is not a row kind; a second-year credit is not producible for a 2025 enrollee | 260.0 | 260.0 | unchanged | unchanged |
| 0 | estimate_request | LATEST class | older implant line of another class label (denied, not covered) | 260.0 | 260.0 | unchanged | unchanged |
| 1 | upgrade_paid_reprocess | CFIELD dhmo (credit) | second record: older terminated DHMO listed first | 45.0 | 45.0 | unchanged | unchanged |
| 1 | upgrade_paid_reprocess | CFIELD dhmo (credit) | cancelled DHMO ending 2025-05-31 listed first | 45.0 | 45.0 | unchanged | unchanged |
| 1 | upgrade_paid_reprocess | CFIELD dhmo (credit) | absent DHMO record | 45.0 | 60.0 | moves per rule (no credit) | moves |
| 1 | grace_denial_reprocess | CFIELD dhmo (credit) | second record: older terminated DHMO listed first | 1001.0 | 1001.0 | unchanged | unchanged |
| 1 | grace_denial_reprocess | CFIELD dhmo (credit) | cancelled DHMO ending 2025-05-31 listed first | 1001.0 | 1001.0 | unchanged | unchanged |
| 1 | grace_denial_reprocess | CFIELD dhmo (credit) | absent DHMO record | 1001.0 | 1075.0 | moves per rule (no credit) | moves |
| 1 | upgrade_denial_reprocess | CFIELD dhmo (credit) | second record: older terminated DHMO listed first | 999.0 | 999.0 | unchanged | unchanged |
| 1 | upgrade_denial_reprocess | CFIELD dhmo (credit) | cancelled DHMO ending 2025-05-31 listed first | 999.0 | 999.0 | unchanged | unchanged |
| 1 | upgrade_denial_reprocess | CFIELD dhmo (credit) | absent DHMO record | 999.0 | 1085.0 | moves per rule (no credit) | moves |
| 1 | claim_appeal_dispute | CFIELD dhmo (credit) | second record: older terminated DHMO listed first | 74.0 | 74.0 | unchanged | unchanged |
| 1 | claim_appeal_dispute | CFIELD dhmo (credit) | cancelled DHMO ending 2025-05-31 listed first | 74.0 | 74.0 | unchanged | unchanged |
| 1 | claim_appeal_dispute | CFIELD dhmo (credit) | absent DHMO record | 74.0 | 0.0 | moves per rule (no credit) | moves |
| 1 | upgrade_paid_reprocess | LATEST selection (paid basic/major of the change year) | later paid preventive line in 2025 | 45.0 | 45.0 | unchanged | unchanged |
| 1 | upgrade_paid_reprocess | LATEST selection (paid basic/major of the change year) | later reprocessed (adjusted) basic row | 45.0 | 45.0 | unchanged | unchanged |
| 1 | upgrade_paid_reprocess | SUM postings (backout) | prior-benefit-year deductible posting (2024) | 45.0 | 45.0 | unchanged | unchanged |
| 1 | grace_denial_reprocess | LATEST selection | older DENIED_NOT_ELIGIBLE line dated before coverage | 1001.0 | 1001.0 | unchanged | unchanged |
| 1 | grace_denial_reprocess | SUM postings | reversed deductible pair in 2026 | 1001.0 | 1001.0 | unchanged | unchanged |
| 1 | upgrade_denial_reprocess | LATEST selection | older DENIED_WAITING_PERIOD line (prior benefit year) | 999.0 | 999.0 | unchanged | unchanged |
| 1 | claim_appeal_dispute | LATEST first-level decision | later first-level decision with outcome overturned on another line | 74.0 | 74.0 | unchanged | unchanged |
| 1 | claim_appeal_dispute | LATEST first-level decision | later second-level decision (upheld) on another line | 74.0 | 74.0 | unchanged | unchanged |
| 1 | claim_appeal_dispute | LATEST decision on the claim/line | the claim's original denial and its corrected decision both present (corrected is later) | 74.0 | 74.0 | unchanged | unchanged |
| 1 | claim_appeal_dispute | SUM postings (backout) | prior-benefit-year maximum posting | 74.0 | 74.0 | unchanged | unchanged |
Every 'moves' row is the absent/break case the rule itself sends to a lower tier; no decoy row moved a result.

### Method shapes, independence, quotes, triggers

(b) All-pairs method-shape table (XF#4/#15; N = normal benefit, o = primary payment recorded on the line, A = allowed amount, S = share base, R = remaining annual maximum = plan maximum less the person's net maximum postings, RB = rollover balance = rollover credits less rollover draws (its own accumulator, dental_msr_rollover_balance), OOP = one-child pediatric out-of-pocket maximum less the person's net pediatric out-of-pocket postings (its own accumulator)):

| factor (policies) | tier pair | shapes | verdict |
|---|---|---|---|
| *_coordination (new-plan-wait, grace-period, prior-level, claim appeal) | non-duplication vs standard | MX(0, N - o) vs MN(N, A - o) | PASS: subtraction vs ceiling (adds the MN operation and input A) |
| | non-duplication vs none | MX(0, N - o) vs N | PASS: adds input o and the floor |
| | standard vs none | MN(N, A - o) vs N | PASS: adds the ceiling operation and inputs A, o |
| *_share_adjustment (initial-wait, new-plan-wait, grace-period, prior-level) | pediatric in-network vs primary credit | MN(OOP, S - pay - o) vs S - pay - o | PASS: adds the MN operation and the OOP input (a separate accumulator) |
| | pediatric in-network vs unadjusted | MN(OOP, S - pay - o) vs S - pay | PASS: adds MN, OOP and o |
| | primary credit vs unadjusted | S - pay - o vs S - pay | PASS: adds input o; the unadjusted tier is not 0 on any domain |
| initial_maximum_limit (initial-wait) | pediatric vs rollover | no cap vs MN(pay, R + RB) | PASS: cap operation present only in one |
| | pediatric vs remaining maximum | no cap vs MN(pay, R) | PASS: drops the cap operation |
| | rollover vs remaining maximum | MN(pay, R + RB) vs MN(pay, R) | PASS: adds the rollover-balance input, a separate accumulator selected by the plan's rollover_enabled tariff parameter, and books the excess as a rollover draw; plans on the fall-through tier hold no rollover account at all |
| estimate_benefit_limit (estimate) | pediatric vs rollover | no annual cap, cost MN(OOP, cost) in network vs MN(pay, R + RB) | PASS |
| | pediatric vs preventive exemption | no annual cap plus the in-network OOP cost cap vs no annual cap | PASS: adds the OOP cost cap operation |
| | pediatric vs remaining maximum | as above vs MN(pay, R) | PASS |
| | rollover vs preventive exemption | MN(pay, R + RB) vs no cap | PASS |
| | rollover vs remaining maximum | MN(pay, R + RB) vs MN(pay, R) | PASS: adds the rollover-balance input (separate accumulator, tariff-selected) |
| | preventive exemption vs remaining maximum | no cap vs MN(pay, R) | PASS: drops the cap operation |

Parameter factors (credit months, clause months, coinsurance, allowance, share start, requested allowance/coinsurance) select values; no tier pair of any ladder selects the same value expression, and every tier is reachable inside its policy's scope (the scope sentences admit every market and class a tier names).

(c) Transitive factor-independence check (mechanical; scratch script over every compute binding):
- dental_ext_initial_wait_reprocess: 6 factors, 46 bindings; plain->factor or factor->other-factor reads (closed transitively): none; only result assembles.
- dental_ext_estimate_request: 4 factors, 36 bindings; plain->factor or factor->other-factor reads (closed transitively): none; only result assembles.
- dental_ext_upgrade_paid_reprocess: 5 factors, 46 bindings; plain->factor or factor->other-factor reads (closed transitively): none; only result assembles.
- dental_ext_grace_denial_reprocess: 6 factors, 43 bindings; plain->factor or factor->other-factor reads (closed transitively): none; only result assembles.
- dental_ext_upgrade_denial_reprocess: 5 factors, 40 bindings; plain->factor or factor->other-factor reads (closed transitively): none; only result assembles.
- dental_ext_claim_appeal_dispute: 4 factors, 38 bindings; plain->factor or factor->other-factor reads (closed transitively): none; only result assembles.
(d) Verbatim compute_basis quote sweep (whitespace-normalised substring of the policy's own rule):
- dental_ext_initial_wait_reprocess: 46 quotes, missing none; bindings without a quote none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not verbatim in base none; prerequisite sentences outside the rule none.
- dental_ext_estimate_request: 36 quotes, missing none; bindings without a quote none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not verbatim in base none; prerequisite sentences outside the rule none.
- dental_ext_upgrade_paid_reprocess: 46 quotes, missing none; bindings without a quote none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not verbatim in base none; prerequisite sentences outside the rule none.
- dental_ext_grace_denial_reprocess: 43 quotes, missing none; bindings without a quote none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not verbatim in base none; prerequisite sentences outside the rule none.
- dental_ext_upgrade_denial_reprocess: 40 quotes, missing none; bindings without a quote none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not verbatim in base none; prerequisite sentences outside the rule none.
- dental_ext_claim_appeal_dispute: 38 quotes, missing none; bindings without a quote none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not verbatim in base none; prerequisite sentences outside the rule none.
(e) Trigger-rule list (every event the six task tools write, with its base triggers):
- reprocess_wait_denial_e5c18a2f: dental_claim_line_adjusted -> dental:dental_max_reversal, dental:dental_max_posting, dental:dental_deductible_reversal, dental:dental_deductible_posting [categories ['dental']]; dental_max_posting -> no triggers; dental_rollover_draw -> no triggers; dental_deductible_posting -> no triggers; dental_ped_oop_posting -> no triggers
- reprocess_upgrade_denial_9a74d03b: dental_claim_line_adjusted -> dental:dental_max_reversal, dental:dental_max_posting, dental:dental_deductible_reversal, dental:dental_deductible_posting [categories ['dental']]; dental_max_posting -> no triggers; dental_deductible_posting -> no triggers; dental_ped_oop_posting -> no triggers
- reprocess_grace_denial_4c0e9d17: dental_claim_line_adjusted -> dental:dental_max_reversal, dental:dental_max_posting, dental:dental_deductible_reversal, dental:dental_deductible_posting [categories ['dental']]; dental_max_posting -> no triggers; dental_deductible_posting -> no triggers; dental_ped_oop_posting -> no triggers
- reprocess_upgrade_paid_line_3fd2b6c9: dental_claim_line_adjusted -> dental:dental_max_reversal, dental:dental_max_posting, dental:dental_deductible_reversal, dental:dental_deductible_posting [categories ['dental']]; dental_max_reversal -> no triggers; dental_deductible_reversal -> no triggers; dental_ped_oop_reversal -> no triggers; dental_max_posting -> no triggers; dental_deductible_posting -> no triggers; dental_ped_oop_posting -> no triggers
- file_claim_appeal_86dbcb40: dental_appeal_filed -> no triggers
- submit_estimate_request_d87add4f: dental_estimate_issued -> no triggers
  No write lands in another category: every trigger target is dental:*. dental_ped_oop_posting/reversal are written only on the pediatric in-network track (no task world uses it); dental_rollover_draw only for the rollover part of a payment.
### Full gate block (difficulty-wide, final)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK

REWORK round 2 claims: C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, T0-F1, T0-F2, T0-F3, T0-F4, T0-F5, T1-F1, T1-F2, T1-F3, T1-F4, T1-F5
REWORK round 2: gates 7/7 green

## REWORK round 3 (audit revision_2: task0=RED task1=RED charter=D1,D2,D3)

Items closed (whole class each):
- D1 (person-unscoped DHMO reads, XF#6/#7): the initial-wait and estimate rules now state once, as a plain shared selection, the person's earlier DHMO enrollment (own terminated Cascade DHMO enrollment matched by name and date of birth, ended the day before coverage) and read DHMO services only under that enrollment's id (XLATEST filtered by dhmo_plan_id); the estimate takes the extraction date from the person's own most recently decided claim line for the tooth instead of the subscriber-wide DHMO ledger. Class sweep: every other DHMO read (credit months in all six rules) is a name-and-date-of-birth CFIELD; every other history read is holding-scoped (one dental enrollment per person); probes below include a household member's DHMO enrollment and extraction of the same tooth.
- D2 (ordering gate without weight / not a real precondition): the grace-period <- prior-level state gate is gone. The prior-level line of task 1 (amalgam, DOS 2025-12-29, decided 2026-01-21) was booked to benefit year 2026, its decision year, and holds the last 5.00 of the 2026 deductible; the prior-level rule books the corrected decision to the benefit year of its date of service (tool argument benefit_year) and reverses the replaced postings in the year they were made, reopening that 5.00 for the grace-period line: a value edge (gate ded_room) that moves the grace-period figure. Class sweep: every prerequisite sentence (estimate <- initial-wait, new-plan-wait <- grace-period, grace-period <- prior-level) now names its resolver's own selection (the most recently decided line of that kind) and, for the deductible edges, the same benefit year; the claim-appeal edge names the decision under appeal. No edge orders history only.
- D3 (pediatric crossing, two readings of plan payment): every rule with the pediatric in-network share tier (initial-wait, prior-level, grace-period, new-plan-wait) now limits the share to the pediatric out-of-pocket room first, then deducts the primary payment, and states that the plan payment on such a line is the allowance less that limited share (the base crossing sentence); the estimate's pediatric tier states the estimated plan payment as the allowance less the limited cost. Compute applies the limit before the reduction (the old hidden cap at the billed amount on non-pediatric lines is gone, so rule words equal compute).
- T0-G1 (base implant interval vs the abutment estimate): the estimate rule declares an overwrite of the base interval sentence, scoped to estimates under it: implant services of the same kind share a procedure code on the tooth position (carriers limit the implant body and the abutment separately), and states this as its frequency test; after the initial-wait correction books the D6010 body on tooth 19 the D6057 estimate is not frequency-limited by the in-force rules.
- T0-G2 (proof text false at handling time): the frequency and missing-tooth base-precondition lines of the estimate call now describe the world after step 1; the prerequisite sentence, its condition and the problem-tree text were re-quoted; design_rationale gained a round-3 paragraph.
- T1-G1 (gate unresolvable for an appealed prior-level line): the only prior-level edge now quantifies over the prior-level rule's own selection (the most recently decided paid basic or major line) booked to the grace-period line's benefit year; the appealed 2025 composite is neither.
- T1-G2 (gate bore no weight across benefit years): the edge is a same-year deductible value edge; skipping the prior-level correction gives the grace-period line 999.0 instead of 1001.0 (check_compute's skip test passes), and the wrong order hands the reopened 5.00 to the new-plan-wait line.
- Stale-text sweep: task 1 prerequisite_closure (edges, order_uniqueness, edge_load_bearing), seed_consistency (amalgam row, its two 2026 postings), gold-action effects and argument tracings, computation traces, design_rationale; task 0 base preconditions, clause traces and design_rationale. Arithmetic re-checked: amalgam original (165.00 - 5.00) x 60% = 96.00 - 45.00 = 51.00; correction (150.00 - 0.00) x 70% = 105.00 - 45.00 = 60.00, share 45.00; grace-period line takes 50.00 - 45.00 = 5.00.

### (a) Decoy / absent-record probe table (scratch copies of each world at the handling-time state of each computation, earlier gold writes replayed through the real task tools)

| policy | read | decoy / absent record | gold | probe | outcome |
|---|---|---|---|---|---|
| initial_wait_reprocess | ext_plan XLATEST dhmo_services | household member's DHMO (same subscriber account, ended the same day) with an extraction of tooth 19 on 2024-09-17 | 250.0 | 250.0 | unchanged (decoy excluded) |
| initial_wait_reprocess | dhmo_id / dhmo_start CFIELD dhmo | second DHMO enrollment of the same person, terminated 2020-12-31 (prior term) | 250.0 | 250.0 | unchanged (decoy excluded) |
| initial_wait_reprocess | ext_plan XLATEST dhmo_services | referral row (dhmo_specialist_referral) for an extraction of tooth 19 on the same date under her DHMO | 250.0 | 250.0 | unchanged (decoy excluded) |
| initial_wait_reprocess | ext_plan XLATEST dhmo_services | absent: the tooth-19 extraction service removed | 250.0 | 1400.0 | moves to the stated tier (clause credit falls to the documented-months / none tier, clause bars payment) |
| initial_wait_reprocess | dhmo_id CFIELD dhmo | absent: no DHMO enrollment | 250.0 | 1400.0 | moves to the stated tier (credit 0, wait not served -> payment 0.00) |
| initial_wait_reprocess | tline LATEST denied/DENIED_WAITING_PERIOD | second DENIED_WAITING_PERIOD line decided earlier (2025-11-04) | 250.0 | 250.0 | unchanged (decoy excluded) |
| initial_wait_reprocess | ded_room / room_std SUM postings | prior-benefit-year (2025) deductible and maximum postings added | 250.0 | 250.0 | unchanged (decoy excluded) |
| initial_wait_reprocess | room_std SUM postings | reversed pair in 2026: maximum posting 300.00 and its reversal 300.00 | 250.0 | 250.0 | unchanged (decoy excluded) |
| initial_wait_reprocess | roll_bal SUM rollover | zero-amount rollover draw row (a draw that moved nothing; rollover draws have no reversal kind) | 250.0 | 250.0 | unchanged (decoy excluded) |
| estimate_request | ext_plan XLATEST dhmo_services | household member's DHMO with a later extraction of tooth 19 (2025-01-10) | 260.0 | 260.0 | unchanged (decoy excluded) |
| estimate_request | e_id LATEST estimates | voided estimate line issued later (2026-02-10) | 260.0 | 260.0 | unchanged (decoy excluded) |
| estimate_request | e_id LATEST estimates | second issued estimate line, earlier (2025-12-01, another procedure) | 260.0 | 260.0 | unchanged (decoy excluded) |
| estimate_request | e_ext LATEST claim lines (tooth) | later-decided claim line on another tooth (2026-02-10, tooth 30, no extraction date) | 260.0 | 260.0 | unchanged (decoy excluded) |
| estimate_request | e_class LATEST claim lines (category) | earlier implant-category decision recorded basic (2025-06-01) | 260.0 | 260.0 | unchanged (decoy excluded) |
| estimate_request | room SUM postings | prior-benefit-year (2025) maximum posting 500.00 | 260.0 | 260.0 | unchanged (decoy excluded) |
| estimate_request | dhmo_id CFIELD dhmo | second DHMO enrollment of the same person, terminated 2020-12-31 | 260.0 | 260.0 | unchanged (decoy excluded) |
| upgrade_paid_reprocess | pb_id LATEST paid basic | earlier-decided paid basic line (2025-11-20) | 45.0 | 45.0 | unchanged (decoy excluded) |
| upgrade_paid_reprocess | pb_id LATEST paid basic | later reprocessed (adjusted) basic decision of another line (2026-02-02) | 45.0 | 45.0 | unchanged (decoy excluded) |
| upgrade_paid_reprocess | ded_room SUM postings (2025, own back-out) | deductible posting 20.00 of another line in 2026 (the replaced decision's year) | 45.0 | 45.0 | unchanged (decoy excluded) |
| upgrade_paid_reprocess | dhmo_start CFIELD dhmo | household member's DHMO ended the day before her coverage | 45.0 | 45.0 | unchanged (decoy excluded) |
| upgrade_paid_reprocess | dhmo_start CFIELD dhmo | absent: no DHMO enrollment | 45.0 | 60.0 | moves to the stated tier (no credit -> recorded prior-plan percentage) |
| grace_denial_reprocess | tline LATEST DENIED_NOT_ELIGIBLE | earlier-decided DENIED_NOT_ELIGIBLE line dated before coverage (2025-05-20, rightly denied) | 1001.0 | 1001.0 | unchanged (decoy excluded) |
| grace_denial_reprocess | ded_room SUM postings | prior-benefit-year (2025) deductible posting 30.00 | 1001.0 | 1001.0 | unchanged (decoy excluded) |
| grace_denial_reprocess | room SUM postings | reversed 2026 maximum pair of 400.00 | 1001.0 | 1001.0 | unchanged (decoy excluded) |
| grace_denial_reprocess | dhmo_start CFIELD dhmo | household member's DHMO ended the day before her coverage | 1001.0 | 1001.0 | unchanged (decoy excluded) |
| upgrade_denial_reprocess | tline LATEST DENIED_WAITING_PERIOD | earlier-decided DENIED_WAITING_PERIOD line (2025-08-12) | 999.0 | 999.0 | unchanged (decoy excluded) |
| upgrade_denial_reprocess | ded_room SUM postings | prior-benefit-year (2025) deductible reversal 50.00 | 999.0 | 999.0 | unchanged (decoy excluded) |
| upgrade_denial_reprocess | dhmo_start CFIELD dhmo | household member's DHMO ended the day before her coverage | 999.0 | 999.0 | unchanged (decoy excluded) |
| claim_appeal_dispute | first-level decision LATEST upheld | later first-level decision on another line with outcome overturned (2026-05-20) | 74.0 | 74.0 | unchanged (decoy excluded) |
| claim_appeal_dispute | first-level decision LATEST upheld | pending first-level filing on another line (filed 2026-06-01, undecided) | 74.0 | 74.0 | unchanged (decoy excluded) |
| claim_appeal_dispute | room SUM postings (own back-out) | prior-benefit-year (2025) maximum posting 900.00 | 74.0 | 74.0 | unchanged (decoy excluded) |
| claim_appeal_dispute | dhmo_start CFIELD dhmo | household member's DHMO ended the day before her coverage | 74.0 | 74.0 | unchanged (decoy excluded) |
| initial_wait_reprocess | dhmo_id CFIELD dhmo | cancelled DHMO enrollment of the same person ending 2025-02-28, listed first | 250.0 | 250.0 | unchanged (decoy excluded) |
| initial_wait_reprocess | dhmo_id CFIELD dhmo | break: her DHMO ended 2025-02-26 (two days before coverage) | 250.0 | 1400.0 | moves to the stated tier (no earlier DHMO enrollment: credit and clause fall to lower tiers) |
| initial_wait_reprocess | ext_plan XLATEST dhmo_services | second extraction record of tooth 19 under her DHMO on another date (2023-05-02) | 250.0 | 250.0 | unchanged (decoy excluded) |
| estimate_request | ext_plan XLATEST dhmo_services | older extraction record of tooth 19 under her DHMO (2023-05-02) | 260.0 | 260.0 | unchanged (decoy excluded) |
| grace_denial_reprocess | dhmo_start CFIELD dhmo | cancelled DHMO of the same person ending 2025-05-31, listed first | 1001.0 | 1001.0 | unchanged (decoy excluded) |
| upgrade_paid_reprocess | t_year (benefit year of the correction) | the replaced decision's recorded benefit year set to 2025 (no misbooking) | 45.0 | 45.0 | unchanged (decoy excluded) |
Every 'moves' row is an absent or broken-coverage case the rule itself sends to a lower tier; no decoy row moved a result.

### Method shapes, independence, quotes, triggers

(b) All-pairs method-shape table (XF#4/#15; N = normal benefit, o = primary payment recorded on the line, A = allowed amount, S = share base, pay = plan payment, R = remaining annual maximum = plan maximum less the person's net maximum postings, RB = rollover balance = rollover credits less rollover draws (its own accumulator), OOP = one-child pediatric out-of-pocket maximum less the person's net pediatric out-of-pocket postings (its own accumulator)):

| factor (policies) | tier pair | shapes | verdict |
|---|---|---|---|
| *_coordination (new-plan-wait, grace-period, prior-level, claim appeal) | non-duplication vs standard | MX(0, N - o) vs MN(N, A - o) | PASS: subtraction vs ceiling (adds the MN operation and input A) |
| | non-duplication vs none | MX(0, N - o) vs N | PASS: adds input o and the floor |
| | standard vs none | MN(N, A - o) vs N | PASS: adds the ceiling operation and inputs A, o |
| *_share_adjustment (initial-wait, new-plan-wait, grace-period, prior-level) | pediatric in-network vs primary credit | MX(0, MN(OOP, S - pay) - o), with pay restated as A - MN(OOP, S - pay) vs MX(0, S - pay - o) | PASS: adds the MN operation and the OOP input, applied before the reduction (round 3: one reading of the crossing line's plan payment) |
| | pediatric in-network vs unadjusted | as above vs MX(0, S - pay) | PASS: adds MN, OOP and o |
| | primary credit vs unadjusted | MX(0, S - pay - o) vs MX(0, S - pay) | PASS: adds input o; the unadjusted tier is not 0 on any domain |
| initial_maximum_limit (initial-wait) | pediatric vs rollover | no cap vs MN(pay, R + RB) | PASS: cap operation present only in one |
| | pediatric vs remaining maximum | no cap vs MN(pay, R) | PASS: drops the cap operation |
| | rollover vs remaining maximum | MN(pay, R + RB) vs MN(pay, R) | PASS: adds the rollover-balance input (separate accumulator selected by the rollover_enabled tariff parameter) and books the excess as a rollover draw |
| estimate_benefit_limit (estimate) | pediatric vs rollover | no annual cap; in network cost MN(OOP, cost) and payment = allowance less that cost vs MN(pay, R + RB) | PASS |
| | pediatric vs preventive exemption | no annual cap plus the in-network OOP cost cap vs no annual cap | PASS: adds the OOP cost cap operation (on an out-of-network pediatric estimate both tiers drop the cap: different conditions, the pediatric tier still adds the in-network cost cap) |
| | pediatric vs remaining maximum | as above vs MN(pay, R) | PASS |
| | rollover vs preventive exemption | MN(pay, R + RB) vs no cap | PASS |
| | rollover vs remaining maximum | MN(pay, R + RB) vs MN(pay, R) | PASS: adds the rollover-balance input |
| | preventive exemption vs remaining maximum | no cap vs MN(pay, R) | PASS: drops the cap operation |

Parameter factors (credit months, clause months, coinsurance, allowance, share start, requested allowance/coinsurance) select values; no two tiers of a ladder select the same value expression; every tier is reachable inside its policy's scope (round 3: the clause ladders keep their documented-months tier reachable because the extraction date now comes from the person's own claim line, not from the DHMO record).

(c) Transitive factor-independence check (mechanical; scratch script over every compute binding):
- dental_ext_initial_wait_reprocess: 6 factors, 47 bindings; plain->factor or factor->other-factor reads (closed transitively): none; only result assembles.
- dental_ext_estimate_request: 4 factors, 37 bindings; plain->factor or factor->other-factor reads (closed transitively): none; only result assembles.
- dental_ext_upgrade_paid_reprocess: 5 factors, 45 bindings; plain->factor or factor->other-factor reads (closed transitively): none; only result assembles.
- dental_ext_grace_denial_reprocess: 6 factors, 43 bindings; plain->factor or factor->other-factor reads (closed transitively): none; only result assembles.
- dental_ext_upgrade_denial_reprocess: 5 factors, 40 bindings; plain->factor or factor->other-factor reads (closed transitively): none; only result assembles.
- dental_ext_claim_appeal_dispute: 4 factors, 38 bindings; plain->factor or factor->other-factor reads (closed transitively): none; only result assembles.
(d) Verbatim compute_basis quote sweep (whitespace-normalised substring of the policy's own rule):
- dental_ext_initial_wait_reprocess: 47 quotes, missing none; bindings without a quote none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not verbatim in base none; prerequisite sentences outside the rule none.
- dental_ext_estimate_request: 37 quotes, missing none; bindings without a quote none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not verbatim in base none; prerequisite sentences outside the rule none.
- dental_ext_upgrade_paid_reprocess: 45 quotes, missing none; bindings without a quote none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not verbatim in base none; prerequisite sentences outside the rule none.
- dental_ext_grace_denial_reprocess: 43 quotes, missing none; bindings without a quote none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not verbatim in base none; prerequisite sentences outside the rule none.
- dental_ext_upgrade_denial_reprocess: 40 quotes, missing none; bindings without a quote none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not verbatim in base none; prerequisite sentences outside the rule none.
- dental_ext_claim_appeal_dispute: 38 quotes, missing none; bindings without a quote none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not verbatim in base none; prerequisite sentences outside the rule none.
(e) Trigger-rule list (every event the six task tools write, with its base triggers):
- reprocess_wait_denial_e5c18a2f: dental_claim_line_adjusted -> dental:dental_max_reversal, dental:dental_max_posting, dental:dental_deductible_reversal, dental:dental_deductible_posting; dental_deductible_posting -> no triggers; dental_max_posting -> no triggers; dental_ped_oop_posting -> no triggers; dental_rollover_draw -> no triggers
- reprocess_upgrade_denial_9a74d03b: dental_claim_line_adjusted -> dental:dental_max_reversal, dental:dental_max_posting, dental:dental_deductible_reversal, dental:dental_deductible_posting; dental_deductible_posting -> no triggers; dental_max_posting -> no triggers; dental_ped_oop_posting -> no triggers
- reprocess_grace_denial_4c0e9d17: dental_claim_line_adjusted -> dental:dental_max_reversal, dental:dental_max_posting, dental:dental_deductible_reversal, dental:dental_deductible_posting; dental_deductible_posting -> no triggers; dental_max_posting -> no triggers; dental_ped_oop_posting -> no triggers
- reprocess_upgrade_paid_line_3fd2b6c9: dental_claim_line_adjusted -> dental:dental_max_reversal, dental:dental_max_posting, dental:dental_deductible_reversal, dental:dental_deductible_posting; dental_deductible_posting -> no triggers; dental_deductible_reversal -> no triggers; dental_max_posting -> no triggers; dental_max_reversal -> no triggers; dental_ped_oop_posting -> no triggers; dental_ped_oop_reversal -> no triggers
- file_claim_appeal_86dbcb40: dental_appeal_filed -> no triggers
- submit_estimate_request_d87add4f: dental_estimate_issued -> no triggers
  Trigger target categories: ['dental']; no write lands in another category. dental_ped_oop_posting/reversal are written only on the pediatric in-network track (no task world uses it); dental_rollover_draw only for the rollover part of an initial-wait payment; the prior-level tool posts its corrected amounts to the benefit year it is given (the year of the line's date of service) and reverses each replaced posting in the year it was posted to.
### Full gate block (difficulty-wide, final)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK

REWORK round 3 claims: D1, D2, D3, T0-G1, T0-G2, T1-G1, T1-G2
REWORK round 3: gates 7/7 green

## REWORK round 4 (render pre-scan render_r1.md: Finding 1, Finding 2, XF#8 note, estimate tie notes)

Items closed (whole class; no scored value moved, every combination sentence's order kept; gold values recompute unchanged):
- F1 (prior-level rule, baseline sentence defining a factor-only quantity): the pediatric out-of-pocket back-out sentence is dropped from rule and baseline.rule; the back-out now sits in the share-adjustment sentence ("...net of reversals for the line's benefit year, after any pediatric out-of-pocket posting the replaced decision made to that benefit year is backed out") and in its ladder; oop_used is that factor's binding and quotes that sentence; the benefit-year sentence no longer lists pediatric counts. Class sweep: every plain binding read by a single factor whose basis is that factor's own sentence was moved into the factor (oop_used in all five rules that carry it, the estimate's pediatric test, and the selected line's procedure, code, tooth and alternate-allowance reads in the allowance factors); the three plain bindings still read by one factor (remaining maximum in initial-wait and estimate, the decision's allowance in the claim appeal) are defined by baseline sentences and are those factors' baseline inputs. No baseline sentence now defines a quantity only a factor uses (mechanical check).
- F2 (claim appeal, unstated same-day ties): the rule now states that where several upheld first-level decisions share the latest decided date, or several decisions on the claim and line share the latest decision date, the rule is not used and the appeal states no amount under it. Class sweep: every latest-record selection in the six rules now carries a tie sentence.
- XF8 (claim appeal deductible vs base family deductible): the claim-appeal scope now admits only accounts with no more than three enrolled persons and its baseline states the sibling family-deductible sentence (family maximum three times the individual deductible, so the person's own postings decide); every other rule already carried both.
- EST-TIES (estimate class and extraction-date selections): both sentences now state that a same-date tie sends the request out of the rule.

### (a) Probe table, round 4 (scratch copies at handling time; earlier gold writes replayed through the real tools)

| policy | read | decoy / absent record | gold | probe | outcome |
|---|---|---|---|---|---|
| initial_wait_reprocess | ext_plan XLATEST dhmo_services | household member's DHMO with an extraction of tooth 19 on the same date | 250.0 | 250.0 | unchanged |
| initial_wait_reprocess | dhmo_id CFIELD dhmo | cancelled DHMO of the same person listed first | 250.0 | 250.0 | unchanged |
| initial_wait_reprocess | dhmo_id CFIELD dhmo | absent DHMO enrollment | 250.0 | 1400.0 | moves to the stated tier (no credit) |
| initial_wait_reprocess | oop_used SUM ped postings (share factor) | pediatric out-of-pocket posting 200.00 for the benefit year (adult: tier not reached) | 250.0 | 250.0 | unchanged |
| estimate_request | ext_plan XLATEST dhmo_services | household member's later extraction of tooth 19 | 260.0 | 260.0 | unchanged |
| estimate_request | e_class LATEST (category) | second implant-category decision on the same decision date as the latest (same-day tie, both major) | 260.0 | 260.0 | unchanged |
| estimate_request | e_ext LATEST (tooth) | later-decided claim line on another tooth | 260.0 | 260.0 | unchanged |
| estimate_request | e_id LATEST estimates | voided estimate issued later | 260.0 | 260.0 | unchanged |
| upgrade_paid_reprocess | pb_id LATEST paid basic | later reprocessed (adjusted) basic decision | 45.0 | 45.0 | unchanged |
| upgrade_paid_reprocess | oop_used SUM ped postings with own back-out (share factor) | pediatric out-of-pocket posting of the replaced decision in 2026 and another in 2025 (adult: tier not reached) | 45.0 | 45.0 | unchanged |
| upgrade_paid_reprocess | ded_room SUM (2025, own back-out) | deductible posting 20.00 of another line in 2026 | 45.0 | 45.0 | unchanged |
| grace_denial_reprocess | tline LATEST DENIED_NOT_ELIGIBLE | earlier-decided not-eligible line dated before coverage | 1001.0 | 1001.0 | unchanged |
| upgrade_denial_reprocess | tline LATEST DENIED_WAITING_PERIOD | earlier-decided waiting-period denial (2025) | 999.0 | 999.0 | unchanged |
| claim_appeal_dispute | first-level decision LATEST upheld | later first-level decision on another line, outcome overturned | 74.0 | 74.0 | unchanged |
| claim_appeal_dispute | first-level decision LATEST upheld | pending first-level filing on another line | 74.0 | 74.0 | unchanged |
| claim_appeal_dispute | ded_req SUM (own back-out) | prior-benefit-year (2025) deductible posting 50.00 | 74.0 | 74.0 | unchanged |
| claim_appeal_dispute | room SUM (own back-out) | prior-benefit-year (2025) maximum posting 900.00 | 74.0 | 74.0 | unchanged |
| claim_appeal_dispute | dhmo_start CFIELD dhmo | household member's DHMO ended the day before her coverage | 74.0 | 74.0 | unchanged |
No decoy row moved a result; the one 'moves' row is the absent-record tier the rule states.

(b) Method shapes: unchanged from round 3 (no ladder outcome changed; the prior-level pediatric tier keeps the shape MX(0, MN(OOP, S - pay) - o) with OOP now stated with the replaced decision's own posting backed out, as compute already did); all pairs PASS as tabled in round 3.

(c) Transitive factor-independence check (mechanical, every compute binding):
- dental_ext_initial_wait_reprocess: 6 factors, 47 bindings; cross-factor or plain->factor reads (transitive): none; plain bindings read by one factor only: ['room_std'] (each is defined by a baseline sentence and is that factor's baseline input).
- dental_ext_estimate_request: 4 factors, 37 bindings; cross-factor or plain->factor reads (transitive): none; plain bindings read by one factor only: ['room'] (each is defined by a baseline sentence and is that factor's baseline input).
- dental_ext_upgrade_paid_reprocess: 5 factors, 45 bindings; cross-factor or plain->factor reads (transitive): none; plain bindings read by one factor only: none (each is defined by a baseline sentence and is that factor's baseline input).
- dental_ext_grace_denial_reprocess: 6 factors, 43 bindings; cross-factor or plain->factor reads (transitive): none; plain bindings read by one factor only: none (each is defined by a baseline sentence and is that factor's baseline input).
- dental_ext_upgrade_denial_reprocess: 5 factors, 40 bindings; cross-factor or plain->factor reads (transitive): none; plain bindings read by one factor only: none (each is defined by a baseline sentence and is that factor's baseline input).
- dental_ext_claim_appeal_dispute: 4 factors, 38 bindings; cross-factor or plain->factor reads (transitive): none; plain bindings read by one factor only: ['d_used'] (each is defined by a baseline sentence and is that factor's baseline input).
(d) Verbatim quote sweep (whitespace-normalised):
- dental_ext_initial_wait_reprocess: 47 quotes, missing none; unquoted bindings none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not in base none; prerequisite sentences outside the rule none.
- dental_ext_estimate_request: 37 quotes, missing none; unquoted bindings none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not in base none; prerequisite sentences outside the rule none.
- dental_ext_upgrade_paid_reprocess: 45 quotes, missing none; unquoted bindings none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not in base none; prerequisite sentences outside the rule none.
- dental_ext_grace_denial_reprocess: 43 quotes, missing none; unquoted bindings none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not in base none; prerequisite sentences outside the rule none.
- dental_ext_upgrade_denial_reprocess: 40 quotes, missing none; unquoted bindings none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not in base none; prerequisite sentences outside the rule none.
- dental_ext_claim_appeal_dispute: 38 quotes, missing none; unquoted bindings none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not in base none; prerequisite sentences outside the rule none.
(e) Trigger-rule list: unchanged from round 3 (task_tools.py not edited this round); every trigger target is dental:*, nothing lands in another category.
### Full gate block (difficulty-wide, final)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK

REWORK round 4 claims: F1, F2, XF8, EST-TIES
REWORK round 4: gates 7/7 green

## REWORK round 5 (KB audit revision_1: kb=CLEAN, src=src-1)

Items closed (whole class; no compute, scored value, world row or combination sentence changed):
- src-1 (overwrite residuals narrower than the retired clause): in all five reprocessing/estimate policies the two claim-adjudication overwrites now restate every in-force part of the retired clause. The allowance overwrite states for all cases that a claim line paid on an alternate allowance carries remark PAID_ALTERNATE_BENEFIT (a reprocessed decision of it carrying ADJUSTED_REPROCESSED, as the reprocessing tools book), and its out-of-scope residual names the alternate-benefit cases and the remark. The patient-share overwrite states for all cases that an in-network practice may not bill the member more than the allowed amount, and its residual carries "and the practice may not bill more". Each replaced_by then names its own scope and its siblings as before; each rule carries the new replaced_by verbatim. Class sweep: the waiting-period credit, missing-tooth and implant-interval overwrites already restate every part of their clauses.

(a) Probe table: the round-4 table stands unchanged. No read, selection, binding or world row changed this round, and check_compute recomputes every gold value on the handling-time worlds.
(b) Method shapes: unchanged (no ladder edited).
(e) Trigger-rule list: unchanged (task_tools.py not edited).
(c)/(d) mechanical re-check after the overwrite edits:
- dental_ext_initial_wait_reprocess: cross-factor reads none; 47 quotes, missing none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not in base none; prerequisite sentences outside the rule none.
- dental_ext_estimate_request: cross-factor reads none; 37 quotes, missing none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not in base none; prerequisite sentences outside the rule none.
- dental_ext_upgrade_paid_reprocess: cross-factor reads none; 45 quotes, missing none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not in base none; prerequisite sentences outside the rule none.
- dental_ext_grace_denial_reprocess: cross-factor reads none; 43 quotes, missing none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not in base none; prerequisite sentences outside the rule none.
- dental_ext_upgrade_denial_reprocess: cross-factor reads none; 40 quotes, missing none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not in base none; prerequisite sentences outside the rule none.
- dental_ext_claim_appeal_dispute: cross-factor reads none; 38 quotes, missing none; baseline sentences outside the rule none; replaced_by outside the rule none; superseded clauses not in base none; prerequisite sentences outside the rule none.
Overwrite residual sweep (every overwrite of this charter): each replaced_by now restates every in-force part of its retired clause; the claim-adjudication allowance and patient-share overwrites (10, five policies) gained the alternate-benefit cases, the PAID_ALTERNATE_BENEFIT remark and the in-network no-balance-billing clause, stated for all cases; the waiting-period credit (6), missing-tooth (2) and implant-interval (1) residuals already restated every part of their clauses (checked clause by clause).
### Full gate block (difficulty-wide, final)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK

REWORK round 5 claims: src-1
REWORK round 5: gates 7/7 green

## REWORK round 6 (KB report revision_3, cross-product re-judge: src-2, src-3, src-4) — seed-only

dental.extended.yaml and task_tools.py are byte-identical to the round-5 files (sha256 prefixes: b51f17bf00364ed7 ff8127367901d52f ). Only tasks/0.json and tasks/1.json changed. No scored value or gold write argument moved. The gold writes shifted later by the added reads: task 0 +4 steps, task 1 +2 steps. computations, gold_actions, temporal steps and every proof text quoting a step number were renumbered.

Items closed:
- src-2 (network status and DHMO PCD assignment without provider records):
  - Task 0: every in-network row now names an active Cascade PPO Participating Dentist Agreement. That covers the 2025 exam, cleaning and filling, the 2026 root canals, and the January estimate. The agreement is Helen M. Ashford, DDS at Ashford Family Dental PLLC, with a practice profile seeded.
  - The agreement fits the provider charter: general dentist, private practice, WA; in network since 2015; decision 59 days after a complete application; recredential due 36 months after the decision; liability 1,000,000 / 3,000,000; license and liability unexpired at frozen time. The practice holds no Premier agreement, so the agreements give exactly the recorded in_network_ppo.
  - Each DHMO enrollment carries its assigned primary-care-dentist agreement (task 0: Proctor District Family Dentistry; task 1: Lincoln Avenue Dental Care). Each is an active Cascade DHMO Primary Care Dentist Agreement in force through the DHMO months, and the task-0 DHMO services name it.
  - Replay required gold reads of the new rows: task 0 gained 4 find_provider_agreements reads (agreement by id, then the practice's agreements, for each agreement); task 1 gained 2.
  - All task-1 claim lines are out of network and name no agreement, consistent with "no agreement gives out-of-network status".
- src-3 (DHMO visits without the office-visit copay): both DHMO 315 primary-care visits now carry the 5.00 office visit copay with their procedure copays (cleaning 10.00 + 5.00; surgical extraction 85.00 + 5.00), per the published Part A schedule.
- src-4 (2025 group renewal above the 12 percent cap): the prior plan year's Value 1000 group rates are set to 28.95 / 56.30 / 60.35 / 91.25. The 2025-07-01 renewal to Classic 1250 at 32.40 / 63.05 / 67.55 / 102.20 therefore rises at most 12.0 percent per tier, within the 20-49 cap. The June 2025 invoice (8/3/3/5 census = 1037.80), the supplementary June invoice (28.95) and their remittance (1066.75) are re-priced.

Bounded exhaustive pass:
- Every other-product row in both worlds was re-priced as of its own date against docs/dhmo, docs/billing, docs/group and docs/provider: DHMO enrollments, accounts, invoices, payments and closures; DHMO services; group contracts, census and member additions; list-bill invoices, payments and the January 2026 grace cure; the new practice profiles and agreements. No other miss.
- Two observations stay without an id, because no record or doc mechanism exists to fix them:
  - The supplementary late-entrant invoices ("A" invoices). Their totals equal the docs' monthly group premium; the docs state no split mechanism.
  - The prior plan year's rates, which no record carries.
- Capitation remittances to the primary-care practices are practice-level ledgers (panel-wide) and are not seeded.

(a) Probe table: the round-4 table stands. No compute, read or selection changed, and check_compute recomputes every gold value on the new handling-time worlds. The added rows are agreements and practice profiles that no extended rule reads, plus the DHMO copay field, which no rule reads.
(b)-(e): unchanged, since the charter and tools are byte-identical.
### Full gate block (difficulty-wide, final)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK

REWORK round 6 claims: src-2, src-3, src-4
REWORK round 6: gates 7/7 green

## REWORK round 7 (policy audit revision_6: E1) — seed-only

dental.extended.yaml (b51f17bf00364ed7) and task_tools.py (ff8127367901d52f) are byte-identical. Only seed fields and proof text of tasks/0.json and tasks/1.json changed. No scored value, gold argument or gold step moved.

Item closed:
- E1 (provider agreements not producible by the provider lifecycle): each of the three agreements now records a state the provider charter's events produce.
  - provider_application writes the original application date: 2014-11-10, 2015-05-26 and 2016-01-11.
  - provider_credentialing_approved fixes the effective date as the first of the month after the original decision. The original decisions were 2015-01-20, 2015-08-03 and 2016-03-28, the latter two after the DHMO site review; the effective dates are 2015-02-01, 2015-09-01 and 2016-04-01. Every original decision falls within 90 days of its application.
  - provider_recredentialed refreshed only the decision date, due date, licence and liability fields. The latest recredentialing decisions (2024-01-18, 2024-07-29, 2025-03-24, unchanged) each fall on or before the due date of the 36-month cycle started by the original decision.
  - The Proctor practice profile now opens before its first application.
  - Proof text (both design_rationale paragraphs) now describes this history; the round-6 wording "last credentialed … on a … application" is gone.
- Found in the same pass and fixed: the round-6 NPIs had 9 digits. They are now 10-digit NPIs with a valid check digit (80840-prefixed Luhn).

Exhaustive field pass over every row added or changed in round 6 (scratch checker):
- task 0, Cascade PPO Participating Dentist Agreement (Helen M. Ashford, DDS): practice profile provider_practice, WA, opened before application OK; phone 10 digits / ZIP 5 / TIN last4 / no DOB OK; NPI 10 digits, valid check digit OK; specialty and private_practice admitted OK; effective = first of a month, after application OK; latest (re)credentialing decision on/after effective OK; due = decision + 36 months OK; due, licence, liability unexpired at frozen time OK; liability >= 1,000,000 / 3,000,000 OK; active, open panel, not terminated OK; fee schedule = current annual schedule of the type and state OK; every row naming it dated on/after effective OK (rows naming it: 6)
- task 0, Cascade DHMO Primary Care Dentist Agreement (Marcus T. Ilves, DDS): practice profile provider_practice, WA, opened before application OK; phone 10 digits / ZIP 5 / TIN last4 / no DOB OK; NPI 10 digits, valid check digit OK; specialty and private_practice admitted OK; effective = first of a month, after application OK; latest (re)credentialing decision on/after effective OK; due = decision + 36 months OK; due, licence, liability unexpired at frozen time OK; liability >= 1,000,000 / 3,000,000 OK; active, open panel, not terminated OK; fee schedule = current annual schedule of the type and state OK; every row naming it dated on/after effective OK (rows naming it: 3)
- task 0, DHMO service D1110 2024-03-12: copay 15.00 = DHMO 315 procedure copay + 5.00 office visit OK; agreement = the assigned PCD OK
- task 0, DHMO service D7210 2024-09-17: copay 90.00 = DHMO 315 procedure copay + 5.00 office visit OK; agreement = the assigned PCD OK
- task 0, DHMO enrollment: assigned PCD set, pcd_effective_date 2022-01-01 = coverage effective 2022-01-01 OK
- task 1, Cascade DHMO Primary Care Dentist Agreement (Ana R. Okafor, DMD): practice profile provider_practice, WA, opened before application OK; phone 10 digits / ZIP 5 / TIN last4 / no DOB OK; NPI 10 digits, valid check digit OK; specialty and private_practice admitted OK; effective = first of a month, after application OK; latest (re)credentialing decision on/after effective OK; due = decision + 36 months OK; due, licence, liability unexpired at frozen time OK; liability >= 1,000,000 / 3,000,000 OK; active, open panel, not terminated OK; fee schedule = current annual schedule of the type and state OK; every row naming it dated on/after effective OK (rows naming it: 1)
- task 1, DHMO enrollment: assigned PCD set, pcd_effective_date 2022-05-01 = coverage effective 2022-05-01 OK
- task 1, June 2025 group billing: {'GLB-71-4482-202506/billing_invoice_issued': 1037.8, 'GLB-71-4482-202506A/billing_invoice_issued': 28.95, 'GLB-71-4482-202506/billing_payment_received': 1066.75}; base = 8x28.95+3x56.30+3x60.35+5x91.25 = 1037.80 OK; payment = 1037.80+28.95 OK; renewal increases 11.92/11.99/11.93/12.00 % <= 12 % OK
Not seeded, by design: the practice-level capitation and remittance ledgers of these agreements. They are panel-wide and no member record reads them.

(a) Probe table: the round-4 table stands. No compute, read or selection changed; check_compute recomputes every gold value.
(b)-(e): unchanged, since the charter and tools are byte-identical.
### Full gate block (difficulty-wide, final)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK

REWORK round 7 claims: E1
REWORK round 7: gates 7/7 green
