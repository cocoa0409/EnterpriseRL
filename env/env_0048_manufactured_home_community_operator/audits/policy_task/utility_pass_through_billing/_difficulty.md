# Policy-task audit — utility_pass_through_billing / charter-global

## charter_global_frozen

- Scenario: `env/env_0048_manufactured_home_community_operator`, difficulty `utility_pass_through_billing`, M=2 (tasks 0, 1).
- Freeze hashes (sha256, recomputed by the auditor and equal to the coordinator's HASHES.txt):
  - `tasks/utility_pass_through_billing/utility.extended.yaml` a7477801561ceacc6e13b873c7765032e4459dd416a75142045cb24de781d456
  - `tasks/utility_pass_through_billing/task_tools.py` d4887cd0794bae55d9b0076a343f1f4ed5c4ba0a5ac51dac5402b62d88467d0d
- Freeze time: 2026-10-08T23:10Z (written before any task's GT was revealed). Auditor: independent policy-task auditor (Claude agent), not the instantiating agent.
- Read for this section: `blueprint/blueprint.yaml` (difficulty entry lines 34-43), `blueprint/products/utility.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, the extended charter, `task_tools.py`, and the restricted-expression evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (for the meaning of `within_months`, `MONTHS`, `DAYS`, `LATEST`, `CFIELD`, `XCOUNT`).
- Masked and not read: every `tasks/utility_pass_through_billing/tasks/*.json` field (evaluation_criteria, computations, design_rationale, solvability_contract, prerequisite_closure, charter_scope, required_documents, closure fields); no other difficulty's tasks or audit views; no other scenario.
- Entry conditions (Step 0): gate snapshot supplied in the brief and on disk at `.audit_views/policy_task/utility_pass_through_billing/GATES.txt` — check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cache_diff (info), check_cross_fire all rc=0; check_traceability deferred to render. Masked views 0/1 supplied with hashes that match the files on disk. Entry conditions complete.

Charter shape: base section (lines 1-1071) + 5 extended policies.

| id | target_tool | owner | computes | prerequisite |
| --- | --- | --- | --- | --- |
| utility_ext_estimated_water_read (A) | post_estimated_water_read_4835faa0 | agent | consumption | [] |
| utility_ext_water_usage_charge (B) | post_water_usage_charge_d31cd699 | agent | amount | A (value_input, gate billed_kgal, state form) |
| utility_ext_final_statement_prepayment (C) | prepay_final_statement_ca2cf476 | user | amount | B (value_input, gate balance, state form) |
| utility_ext_statement_late_fee (D) | post_late_fee_5fe5b1d1 | agent | amount | [] |
| utility_ext_final_credit_refund (E) | request_credit_refund_3a7a9c57 | user | amount | D (value_input, gate credit, state form) |

### policy_conflict_scan

- Base copy: `diff` of charter lines 1-1071 against `blueprint/products/utility.yaml` shows only a trailing blank line — the base section is verbatim.
- Overlapping subjects: A writes `utility_meter_read` (estimated water read); B writes `utility_usage_charge` (water); C writes `utility_payment` (prepayment); D writes `utility_late_fee`; E writes `utility_credit_refund`. No two extended policies write the same event type, so no two claim the same quantity. Base policies that also govern these event types: `utility_evt_statement_billing` / `utility_evt_estimates_and_rereads` (A, B), `utility_evt_payments` / `utility_agg_account_settlement` (C), `utility_evt_late_fee` (D), `utility_agg_account_settlement` / `utility_final_billing` (E) — each is in the corresponding policy's `base_policy_refs` and is swept in `override_declarations`.
- Triggers / eligibility / time anchors: A, B, D are `state_due` desk writes; C, E are `on_request` customer writes. The inherited base gates that remain in force: A — the estimate streak cap (`max_consecutive_estimated_reads`, `utility_msr_estimate_streak`); B — none beyond "a charge is posted for a service only when the schedule bills that service"; C — `accepted_payment_channels` and oldest-first application; D — grace-period end (`utility_grace_ended`), unpaid-at-grace-end minimum, once per statement, no fee on a fee; E — the account is final-billed, never netted to another account or the lease ledger. No two of them reach different conclusions on a shared subject.
- Cross-category read boundaries: A reads lease (`lease_requests`, `status`, `vacate_date`) and rules (`rules_records` guest registrations); B reads lease (`total_occupant_count`, `variant_name`) and rules; C reads lease (`status`, `vacate_date`, `lease_ledger`) and rules; D reads lease (`status`, `lease_ledger`, `lease_requests`); E reads lease (`lease_ledger`). All are read-only; none writes another category, in keeping with `utility_agg_account_settlement` ("A utility balance never moves to or from the site-lease ledger").
- Claimed scopes of the M tasks (inferred from the charter graph and the two personas only, pre-reveal): task 0 = tree C <- B <- A (prepay the estimated final statement), task 1 = tree E <- D (credit refund on a final-billed account). The two trees are vertex-disjoint and together cover all five extended policies: mutually exclusive and jointly complete. (Confirmed or contradicted against `charter_scope` only in the per-task comparisons.)

### rule_compute_equivalence

Swept per policy, binding by binding, against `compute_basis` and back against every rule sentence.

A (estimated water read)
- `std_cons/std_reads` (`within_months=4`, `read_type='actual'`, water) <- "average consumption of the actual water reads taken in the last four months, ... fewer than four whole months separate its read date from the handling date"; evaluator `_within` is `0 <= MONTHS(d, NOW) < N`, matching "fewer than N whole months".
- `year_ago_*` (`within 13` minus `within 12`, i.e. MONTHS == 12) <- "an entry taken twelve whole months before the handling date is one separated from it by exactly twelve whole months".
- `household_changes` (`XCOUNT lease_requests occupant_registration accepted, within 12, date_field requested_date`) <- "has had an occupant registration accepted in the last twelve months". See observation O-2 (which date "accepted in" reads).
- `basis_use` ternary order (year-ago tier requires `household_changes == 0`, recent tier requires `> 0`) — tiers disjoint, rule order matches.
- `days_covered` (LATEST trash `days_billed`) and `converted = basis * days / 30` <- "multiplying it by the days of service billed on the trash charge of the latest statement and dividing by 30".
- shares: `estimate_history_share` (estimated water reads, 12 months: >=2 -> 0.85, ==1 -> 0.93, else 1.0); `guest_share` (latest-begun stay, began within 2 months, span >=14 -> 1.25, <14 -> 1.10, else 1.0); `move_out_share` (lease status notice_to_vacate and DAYS(NOW, vacate) <=30 -> 0.85, >30 -> 0.95, else 1.0); `leak_share` (leak_adjustment credits within 4 -> 0.80, else within 12 -> 0.95, else 1.0). Each tier is a rule sentence and each rule tier is a branch.
- `result = RND(converted * shares, 2)` <- "rounded half up to two decimal places ... once, on the final figure". See O-1 (RND is Python `round`).
- Sweep back: no rule sentence without a binding; no binding without a quoted basis.

B (water usage charge)
- `billed_kgal` = LATEST water read consumption <- "bills the consumption carried by the water read it bills, which is the latest water read on the account".
- `household_share` (occupants <=1 -> 0.75, >=5 -> 1.5, else 1.0), `guest_widening` (0.5 / 0.25 / 0.0 of the schedule bound), `lot_share` (Greenbelt/Lakefront multi -> 1.4, Standard/Preferred multi -> 1.2, else 1.0), `bound1 = L1*household + L1*widening`, `bound2 = L2*lot` — each quoted verbatim.
- `block_charge` (three blocks on bound1/bound2), `water_charge` ternary: estimated and >=2 estimated water reads in 2 months -> all at block-1 rate; estimated and ==1 -> part above bound2 at (r2+r3)/2; else block_charge — matches the rule's three pricing branches; single rounding on the total.
- The rule's statement "the water base charge is billed separately as a fixed charge and is never part of the usage charge" has no binding of its own and needs none (it excludes a term).
- Sweep back: complete.

C (final-statement prepayment)
- `balance = F('utility_balance')`; `final_days = DAYS(latest water read date, service_end_date)`; `daily_use` ternary on `MONTHS(service_start_date, NOW)` (>=12 -> 12-month actual average/30; <4 -> latest actual/30; else 4-month average/30); `move_share` (14-day split, 0.8/0.9/1.0); `guest_share` (latest-begun stay with planned last day after NOW: span >=14 -> 1.25, <14 -> 1.10, else 1.0); `unit_price = latest water usage charge amount / its consumption`; `projected_usage = RND(daily_use*final_days*shares*unit_price, 2)`; `monthly_fixed = SUM fixed charges within_months=1`; `final_fixed` ternary (<15 days -> x days / latest trash `days_in_period`; 15-29 -> x days / 30; >=30 -> whole month; prorations rounded); `final_estimate = projected_usage + final_fixed + admin fee`; `cushion_share` (returned payment on lease or utility in 12 months -> 0.2; else utility or lease late fee in 12 months -> 0.1; else 0); `reserve_share` (latest water read estimated and >=2 estimated in 2 months -> 0.30; ==1 -> 0.15; else 0) on the latest water usage charge; `result = RND(balance + final_estimate + cushion + reserve, 2)`.
- Each quoted verbatim. "the fixed charges dated in the last whole month" is implemented as `within_months=1` (fewer than one whole month before the handling date) — see O-3.
- Sweep back: the rule's channel sentence ("accepted only by card through the resident portal or by cashier's check") is not a compute input; it binds the `payment_channel` argument, not `amount`. Complete.

D (statement late fee)
- `stmt_*` = entries with MONTHS(entry_date, NOW) == 1 (`within 2` minus `within 1`) <- "the statement dated one whole month before the handling date when whole months are counted from the statement date to the handling date"; `fee_basis` ternary (>=150 -> RND(6% of charges); <40 -> RND(late_fee_amount * charges / 40); else late_fee_amount); `repeat_share` (0 utility late fees in 12 months -> 0.5; >=3 -> 1.5; else 1.0); `tenure_share` (MONTHS(service_start, NOW) >=120 -> 0.8; >=60 -> 0.9; else 1.0); `risk_share` (lease or utility returned payment in 12 months -> 1.25; else lease late fee in 6 months -> 1.10; else 1.0); `closed_share` (lease status closed and accepted notice_to_vacate -> 0.75; closed and none -> 0.9; else 1.0); `result = RND(product, 2)`.
- The eligibility sentences (unpaid at grace end >= minimum, once per statement, no fee on a fee) are gates, not quantities; they are not in compute and need not be.
- Sweep back: complete.

E (final credit refund)
- `credit = max(-balance, 0)`; `check_hold_days` (returned payment 12 months -> 15; no returns and a utility late fee AND a lease late fee in 12 months -> 10; else 5); `held_check` = latest office_personal_check payment if DAYS(receipt, NOW) < hold; `bank_hold_days` (lease ach_autopay payment in 6 months -> 1; none and <=1 utility bank-account payment (portal ACH + autopay) in 12 months -> 4; else 2); `held_bank` = latest online_portal_ach payment if DAYS < hold; `reserve_share` (latest water read estimated and DAYS <=30 -> 0.5; 31-60 -> 0.25; else 0); `reserve_base` (>=2 estimated water reads in 2 months -> sum of water usage charges in 2 months; ==1 and latest trash `days_billed` < 10 -> latest charge * 30 / days; else latest charge); `refund_limit` (MONTHS(service_start, NOW) >=180 -> 1000; >=60 -> 600; else 250); `result = RND(min(max(credit - held_check - held_bank - reserve, 0), limit), 2)`.
- Each quoted verbatim. Sweep back: complete.

Observations (no consequence demonstrable charter-wide; each task file checks its own world):
- O-1 `RND` is Python `round(float, 2)` while every rule says "half up". They differ only on a value whose binary float is an exact or just-below half cent. Per-task check.
- O-2 `lease_requests` carries no acceptance date. `requested_date` is "the date the request names — ... the effective date of a change"; `created_at` is "moment the request was taken". A's "an occupant registration accepted in the last twelve months" is implemented on `requested_date`. A world whose registration effective date and creation moment straddle the 12-month line would read two ways. Per-task check.
- O-3 C's "the fixed charges dated in the last whole month" is anchored by "the fixed charges billed on the latest statement, which are ..."; a reading of "last whole month" as the previous calendar month would pick the prior statement instead. Consequence only where the two statements' fixed charges differ. Per-task check.
- O-4 `CFIELD('lease', ...)` and `XCOUNT('lease'/'rules', ...)` are scoped to the customer, while A/B/C/D's rules say "the lease the account serves". They coincide whenever the customer holds one lease. Per-task check.

### action_binding_and_uuids

- `(target_tool, computes)`: (post_estimated_water_read_4835faa0, consumption), (post_water_usage_charge_d31cd699, amount), (prepay_final_statement_ca2cf476, amount), (post_late_fee_5fe5b1d1, amount), (request_credit_refund_3a7a9c57, amount) — each claimed by exactly one policy.
- uuid8s 4835faa0, d31cd699, ca2cf476, 5fe5b1d1, 3a7a9c57: no shared prefix or suffix, no sequence, no near-neighbour values; each is consistent with an independent draw. No uuid8 is reused.
- Function bodies (`task_tools.py`): every tool books its row unconditionally (`ctx.create` + balance update); none checks status, dates, prior rows, the streak cap, the grace period or a channel restriction; none raises or returns a hint. The tool layer judges no eligibility and no prerequisite.
- Docstrings: no tool name of another tool, no policy id, and no ordering word (before / after / first / once / until) in any tool docstring (the only "before" is in the module docstring line 6, "before calling", which addresses the desk in general). Observation O-5: `post_estimated_water_read` says the read is one "that a usage charge can bill" and its receipt id is "used by a usage charge as the read it bills"; `post_water_usage_charge` says `source_entry_id` may be taken "from the receipt that recorded the read". These describe objects of another action (no ordering word, no tool name) and so pass check 3 as written, but they tell a reader of the tool list that a recorded estimated read feeds a usage charge.
- Business reading of each docstring matches the policy subject; no confirmation, review or wait is added.

### prerequisite_graph

- `prerequisite` is filled in on all five policies (A: [], D: [], B/C/E one edge each). Every `problem` is another extended policy id in this file, none is a base policy, none is self. Graph edges B->A, C->B, E->D: acyclic (two chains).
- `policy_source` of each edge is verbatim in its own policy's `rule` (normalised whitespace check) and absent from the depended-on rule.
- `form: state` on all three; no `fallback_reason` present; none required.
- `kind: value_input` on all three; each `gate` names a real compute binding of the blocked policy (`billed_kgal` in B, `balance` in C, `credit` in E).
- `resolved_by` equals the depended-on policy's `target_tool` in all three.
- `effect` claims, against the tool bodies: B<-A — the estimated read row becomes the latest water read, so `billed_kgal` and `latest_read_type` come from it (true: LATEST by entry_date; the new read is dated the missed read day, later than every earlier read). C<-B — the usage charge raises `utility_balance` by its amount and becomes the latest water usage charge (true: tool adds `amount` to `utility_balance`; entry dated `ctx.now()`). E<-D — the late fee raises the balance by the fee, so `credit` shrinks by exactly the fee (true while the credit exceeds the fee). Note: D's write also adds a row to E's `utility_late` count (check-holding ladder), a second value path the `effect` does not mention; it can only strengthen the edge.
- `condition` wording: B "A water read row ... stands on the account for the read cycle the latest statement bills, carrying that cycle's statement month"; C "For every read cycle whose read day has passed, a water usage charge row ... stands on the account for that cycle's statement month"; E "For every statement whose unpaid amount at the end of its grace period reached the schedule's late-fee minimum, a utility late fee row ... stands on the account for that statement month". Each is the record form of its sentence, neither stronger nor weaker. No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` text.

### prerequisite_sentences

Four-point test per edge.

1. B <- A: "A water usage charge for a read cycle is fixed only after a water read stands on the account for that cycle's read day."
   - Ordering connective: "only after". Waited-on state: "a water read stands on the account for that cycle's read day" — record-visible (`utility_ledger` meter read, `entry_date` = read day). No tool, no policy id, no snake_case token, no row id. Strength: one read for the cycle's read day = condition's one water read row for that cycle.
   - Writes in this difficulty that create a water read: only `post_estimated_water_read_4835faa0` (A). Exactly one.
   - Derivation: the read day of the cycle being billed has passed and the ledger carries no water read dated that day -> the usage charge cannot be fixed -> the only rule that records a water read is A ("When a water submeter could not be read on its read day, the desk records an estimated water read for that read cycle so that the cycle can be billed") -> record it, then price it. Single reading.
2. C <- B: "The prepayment of an estimated final statement is worked out only after a water usage charge stands on the account for every read cycle whose read day has passed."
   - "only after"; state: a water usage charge row per read cycle whose read day has passed; no tool / id / token. Strength matches the condition ("every read cycle whose read day has passed").
   - Writes creating a water usage charge: only `post_water_usage_charge_d31cd699` (B). Exactly one.
   - Derivation: a passed read day with no water usage charge for its cycle -> B's rule prices the charge ("A water usage charge bills the consumption carried by the water read it bills") -> B is itself gated by edge 1. Single reading.
3. E <- D: "A credit balance is not refunded until a late fee stands on the account for every statement whose unpaid amount at the end of its grace period reached the late-fee minimum."
   - "not ... until"; state: a late fee row per qualifying statement; no tool / id / token; "every statement whose ..." is an open set stated open, as in the condition.
   - Writes creating a utility late fee: only `post_late_fee_5fe5b1d1` (D). Exactly one.
   - Derivation: a statement unpaid at grace end at or above the minimum with no late fee -> D's rule ("A late fee on a utility statement left unpaid past its grace period is posted in the month after the statement month and is figured on that statement ...") -> post it. Single reading in the abstract; whether D's anchoring ("the statement dated one whole month before the handling date") reaches every qualifying statement is world-dependent and checked per task.
- No rule carries a second wording of any dependency, a tool name or another problem's id; the depended-on rules (A, B, D) do not restate the sentences. A's "so that the cycle can be billed" states A's own purpose, not B's gate.
- Undeclared cross-problem orders: C's rule reads values that A writes ("the date of the latest water read", "where the latest water read is an estimated read") but states no order; the order C-after-A is already entailed by C->B->A. No rule states a cross-problem order outside the three edges. No base sentence is used to ground an edge.

### override_declarations

Sentence-by-sentence over each `base_policy_refs` entry.

A refs `utility_evt_statement_billing`, `utility_evt_estimates_and_rereads`
- estimates_and_rereads s1 ("estimated read set at utility_msr_estimate_daily_use times the days in the cycle") — handled differently (4-month window average, trash-days/30 conversion, four shares): declared in `overwrite` (superseded_clause verbatim in base; replaced_by verbatim in A's rule). The whole base sentence is superseded, so the shares and the conversion sit inside the replaced quantity; merged semantics unique (only A's rule sets the estimate).
- s2 (streak cap: no more than `max_consecutive_estimated_reads` consecutive estimated cycles; then an actual read) — followed (inherited eligibility). Per-task check of the streak.
- s3 (first actual read after estimates trues up) and s4 (high-bill re-read) — not about an estimated read's quantity; followed.
- statement_billing: read day, statement day, due date, rounding — followed (A sets `read_date` = the read day; no conflict).

B refs `utility_evt_statement_billing`, `utility_meter_accuracy`
- statement_billing s2 (water block pricing incl. base charge) — handled differently (household/guest-adjusted bound1, lot-adjusted bound2, estimated-read pricing branches, base charge split out): declared (whole sentence superseded). The replaced_by quotes only the bound1 sentence, but the superseded clause names the entire base sentence, so the bound2 and pricing-branch changes are inside the declared replacement — not an undeclared override. The "plus water_base_charge_monthly" part is consistent with B's "billed separately as a fixed charge".
- s1 (read day / statement day / due date payment_due_days after statement date) — followed; B's `due_date` argument is bound by it.
- s6 (consumption never prorated), s7 (rounding half up) — followed.
- meter_accuracy — governs credits/back-bills after a meter test; not the regular usage charge; followed.

C refs `utility_agg_account_settlement`, `utility_evt_payments`, `utility_final_billing`, `utility_evt_statement_billing`
- payments s2 (certified-funds channel restriction) — replaced, declared; adds the prepayment channel restriction (card in portal / cashier's check). Merged reading unique: the restriction is a subset of `accepted_payment_channels` (s1, followed).
- payments s1 (accepted channels, oldest first), s3-s5 — followed.
- settlement s1-s3 — followed (prepayment applied only to this account).
- final_billing s2 ("final statement issued ... with fixed charges prorated to the service end date and one administration fee") and statement_billing s6 (proration "monthly amount divided by the days in the cycle times the days of service") govern the final statement actually issued later; C's scored quantity is a prepayment quote of an *estimated* final statement, which no base sentence sets. Not an override. Observation O-6: where the quote's final-cycle fixed charges (C's ladder) and the base proration of the real final statement differ on a task's world, an agent may be tempted to mirror the base proration — checked per task.

D refs `utility_evt_late_fee`
- s3 (fee = late_fee_amount, once, unpaid >= minimum, no fee on a fee) — the amount part replaced, declared; the once / minimum / no-fee-on-fee conditions are restated verbatim in D's own rule, so nothing of s3's gates is lost. The four shares sit inside the superseded amount.
- s1-s2 (grace period end, posting no earlier than the day after the last grace day) — followed (inherited). s4 (courtesy waiver) — another subject. s5 (no suspension) — followed.
- Observation O-7 (base sentence outside D's refs): `utility_evt_payments` s5 "it is pursued through late fees while the account is open and through collections after the final statement". D's closed-lease share and E's prerequisite contemplate a late fee on a final-billed account. `final_billed` is not the lifecycle's `closed` state, so "while the account is open" covers it; the second reading ("no late fee after the final statement") is weak. Per-task check whether it would change a scored value.

E refs `utility_agg_account_settlement`, `utility_final_billing`
- settlement s3 ("refunded by check to the former resident at closing rather than carried to any other account") — replaced, declared (partial refund, limit, rounding). E's rule restates "refunded by check to the former resident at the mailing address on the profile". The "at closing" timing is relaxed by "any credit not refunded stays on the account for a later refund" — inside the declared replacement.
- settlement s1-s2 (no netting, never to the lease ledger) — followed. final_billing s3 ("account closes when the final balance reaches zero, a credit balance being refunded under utility_agg_account_settlement") — followed; consistent with a partial refund leaving the account final-billed.
- No undeclared override found in any policy. No author text calls a base output a "wrong value".

### factor_ladders

| policy | factor | effect | decides | tiers | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| A | estimate_basis_cycle | method | basis_use | 3 | both non-fall-through tiers conjoin a utility-ledger read condition with a lease_requests condition | lease |
| A | estimate_history_share | parameter | estimate_history_share | 3 | no | — |
| A | estimate_guest_share | parameter | guest_share | 3 | no (one rules record: start and span) | rules |
| A | estimate_move_out_share | parameter | move_out_share | 3 | no (one lease row: status and vacate date) | lease |
| A | estimate_leak_share | parameter | leak_share | 3 | no | — |
| B | household_block_share | parameter | household_share | 3 | no | lease |
| B | guest_block_widening | parameter | guest_widening | 3 | no | rules |
| B | lot_block_share | parameter | lot_share | 3 | no | lease |
| B | estimated_read_pricing | method | water_charge | 3 | yes (latest read's type + count of other estimated reads) | — |
| C | projected_daily_use_basis | method | daily_use | 3 | no | — |
| C | projection_move_share | parameter | move_share | 3 | no | lease |
| C | projection_guest_share | parameter | guest_share | 3 | no | rules |
| C | final_cycle_fixed_proration | method | final_fixed | 3 | no | — |
| C | prepayment_cushion_share | parameter | cushion_share | 3 | yes (lease ledger / utility ledger disjunction) | lease |
| C | true_up_reserve_share | parameter | reserve_share | 3 | yes (latest read type + count) | — |
| D | late_fee_basis | method | fee_basis | 3 | no | — |
| D | late_fee_repeat_share | parameter | repeat_share | 3 | no | — |
| D | late_fee_tenure_share | parameter | tenure_share | 3 | no | — |
| D | late_fee_risk_share | parameter | risk_share | 3 | yes (lease ledger / utility ledger) | lease |
| D | late_fee_closed_lease_share | parameter | closed_share | 3 | yes (lease status + lease_requests) | lease |
| E | check_holding_period | parameter | check_hold_days | 3 | yes (lease + utility returns; utility AND lease late fees) | lease |
| E | bank_payment_holding_period | parameter | bank_hold_days | 3 | yes (lease ledger + utility ledger) | lease |
| E | true_up_reserve_rate | parameter | reserve_share | 3 | yes (latest read type + its date) | — |
| E | true_up_reserve_base | method | reserve_base | 3 | yes (estimated-read count + trash days) | — |
| E | refund_limit_tenure | parameter | refund_limit | 3 | no | — |

- Counts per policy: A 5 (4 parameter, 1 method); B 4 (3, 1); C 6 (4, 2); D 5 (4, 1); E 5 (4, 1). All within 4-6, each with >=2 parameter and >=1 method.
- Per task (scopes as inferred above): task 0 (A+B+C) multi-source: estimate_basis_cycle, estimated_read_pricing, prepayment_cushion_share, true_up_reserve_share; cross-difficulty: lease, rules. Task 1 (D+E) multi-source: late_fee_risk_share, late_fee_closed_lease_share, check_holding_period, bank_payment_holding_period; cross-difficulty: lease.
- Binding sets: within each policy every factor's `bindings` are disjoint from every other factor's, and every `decides` names an input binding, never `result`.
- Ladders: each has three tiers, pairwise disjoint as stated (numeric thresholds split cleanly; status/count conditions are complements); every tier is stated in the policy's own `rule` with its condition and its value or method, and implemented as a branch of the `decides` binding; every branch is a rule tier. No tier lives only in `compute`.
- Distinct outcomes: no two tiers of one ladder select the same value or method (e.g. A history 0.85/0.93/1.0; C proration days/cycle-days vs days/30 vs whole month; E reserve base sum/scaled/latest; E limits 1000/600/250).
- Fall-through = baseline: every factor's fall-through tier is the policy's `baseline.rule` value for that input (A basis = 4-month average; shares 1.0; B bounds at schedule values and three-block pricing; C 4-month average/30, whole month of fixed charges, no shares, no cushion, no reserve; D schedule late_fee_amount, shares 1.0; E 5-day and 2-day holds, no reserve, 250.00 limit). Every `baseline.rule` sentence is a sentence of its `rule` (mechanical check) and is self-sufficient: it names a definite method and default values (`baseline.params` keys exist in `params` or the schedule parameters).
- Label honesty: A estimate_basis_cycle selects a different averaging object (one year-ago read / 3-month average / 4-month average) — method. B estimated_read_pricing changes the pricing algorithm (flat first-block / midpoint top block / three blocks) — method. C projected_daily_use_basis (12-month average / latest single read / 4-month average) — method. C final_cycle_fixed_proration: tier 3 (no proration) versus tiers 1-2 (prorate) is a change of algorithm, and tiers 1 vs 2 are two day-count conventions (actual cycle days vs 30-day month); honest as `method`, recorded as observation O-8 that the tier-1/tier-2 difference alone is a divisor substitution. D late_fee_basis (percentage of charges / proportional to charges / flat) — method. E true_up_reserve_base (two-month sum / scaled latest / latest) — method. All `parameter` factors substitute a number into a fixed formula.
- Business reality: the conditions weighed (prior estimates, guest stays, an imminent move-out, a recent leak adjustment for an estimate; household size, guests and lot size for an allowance-style block bound; tenure-based projection basis, coming move, guest stay, bill-history cushion and estimate true-up reserve for a final-bill prepayment; bill size, repeat lateness, tenure, payment-risk history and closed-lease status for a late fee; uncleared-funds holds, an estimate true-up holdback and a tenure-based refund cap for a credit refund) are ones a submetering / utility-billing operator plausibly weighs for those quantities, and every fall-through is an ordinary published default (standard average, full fee, standard hold, standard limit). No tier condition restates a policy's whole scope.
  - Observation O-9 (E true_up_reserve_rate): E applies only to a final-billed account. Under the base lifecycle the final statement follows a final read (`utility_final_bill` triggers `utility_meter_read` with `read_type: final`), so on a final-billed account the latest water read is ordinarily the final read and the two "estimated" tiers would hold of no one. They are reachable only where the service end date coincides with a read day whose read is estimated (base `utility_evt_estimates_and_rereads` s1, "When a submeter cannot be read on the read day ..."); holding back part of a refund after an estimated final bill is a real business practice. Recorded as an observation, not a red light; the task that relies on this tier must show its seed reaches it through records the charter admits.

### findings

- No charter-global SOURCE-POLICY RED. Override declarations, rule/compute equivalence, action binding, uuid8s, the prerequisite graph and the prerequisite sentences all hold.
- Observations O-1 through O-9 as recorded above. The ones a task file must test against its own world: O-1 (rounding) both tasks; O-2 (occupant registration date) task 0; O-3 (last whole month) task 0; O-4 (customer-scoped reads) both; O-5 (docstrings) both, no world dependence; O-6 (base final-cycle proration) task 0; O-7 (late fee after final statement) task 1; O-8 (proration label) task 0; O-9 (estimated read on a final-billed account) task 1.

## closing_checklist

Written after both tasks' derivations were frozen (23:17Z) and their GT revealed and compared; nothing above this heading was edited after a reveal.

- Files: `_difficulty.md`, `0.md`, `1.md` — one per task plus this charter file. First revision (no earlier audit of this difficulty existed). Both comparison sections end in PASS on all four relationships.
- Coverage and scope: `charter_scope` task 0 = {utility_ext_estimated_water_read, utility_ext_water_usage_charge, utility_ext_final_statement_prepayment} with tools {post_estimated_water_read_4835faa0, post_water_usage_charge_d31cd699, prepay_final_statement_ca2cf476}; task 1 = {utility_ext_statement_late_fee, utility_ext_final_credit_refund} with {post_late_fee_5fe5b1d1, request_credit_refund_3a7a9c57}. Pairwise disjoint over whole trees, jointly covering all five extended policies and all five task tools — as inferred pre-reveal in § policy_conflict_scan. Task tools and GT are closed (every GT write is one of the five tools or a share tool); every uuid8 independently drawn (§ action_binding_and_uuids).
- Trees: task 0 — 2 prerequisite problems, 2 value_input edges, owner=user root (prepayment), acyclic; task 1 — 1 prerequisite problem, 1 value_input edge, owner=user root (refund), acyclic. The difficulty-wide `prerequisite` graph (B->A, C->B, E->D) is a DAG with no cross-task edge.
- Factors: every computation declares a self-sufficient baseline and 4-6 factors with >=2 parameter and >=1 method (A 5, B 4, C 6, D 5, E 5); per task >=1 multi-source and >=1 cross-difficulty factor (task 0: lease + rules; task 1: lease); every ladder three tiers stated in full in its rule, outcomes distinct; every factor bears weight on its task's world against an honest baseline, and each whole baseline gives a definite number different from gold (A 21.42, B 119.42, C 312.92, D 10.00, E 250.00).
- Gates: no artifact of this difficulty was edited during the audit (sha256 of `utility.extended.yaml`, `task_tools.py`, `tasks/0.json` fa0326be…2253 and `tasks/1.json` af846bfc…aa5 unchanged from the inputs the coordinator's gate snapshot was taken on), so the snapshot in `.audit_views/policy_task/utility_pass_through_billing/GATES.txt` (all rc=0) stands for the final form; per this skill's Step 0 the auditor cites rather than re-runs the gates. check_traceability remains deferred to the render step.
- Observations carried (no red light): O-1…O-9 above; per task F0-1, F0-2 (task 0) and O-T1-1 (task 1).

Difficulty verdict: policy self-consistency PASS + problem tree PASS + factors PASS + unique solution PASS for tasks 0 and 1 — the difficulty passes the source-layer audit.
