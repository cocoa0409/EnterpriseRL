# plan — prepaid_service_hours (category timebank), M=2

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[4,4,5]
- task 1: prerequisite_problems=3, factor_counts=[5,5,5,6]

## Policy space (7 extended policies, 7 task tools; pairwise disjoint per task)
Natural event decomposition of TimeBank work: each pending/mistaken ledger item on a block is its own posting.
User-side (client signs an order form, quoted_amount_usd): repeat order (task 0 root), extension (task 1 root).
Agent-side: travel entry, visit-draw correction (task 0); remote draw, onsite draw, project draw (task 1).

### Task 0 — root: repeat-order quote (user), block C = TimeBank 10-Hour Block (client on ClearPath Standard)
- R0 timebank_ext_repeat_order_quote (user, 5 factors): price of a new block of the same size as C, signed on an order form.
- P0a timebank_ext_visit_travel_entry (agent, 4 factors): travel entry owed for an onsite visit already drawn on C.
- P0b timebank_ext_visit_draw_correction (agent, 4 factors): reversal of the hours a visit draw took beyond the minutes its ticket substantiates.
- edges: R0 <- P0a (value_input: consumption read by the price), R0 <- P0b (value_input). P0a, P0b commute.

### Task 1 — root: extension quote (user), block A = TimeBank 160-Hour Block (client on ClearPath Professional)
- R1 timebank_ext_extension_quote (user, 6 factors): extension fee on A's remaining hours.
- P1a timebank_ext_remote_session_draw (agent, 5)
- P1b timebank_ext_onsite_visit_draw (agent, 5)
- P1c timebank_ext_project_time_draw (agent, 5)
- edges: R1 <- P1a/P1b/P1c, all value_input on A's hours_balance; the three draws commute (no draw reads the balance).

## Constraints carried (XF_recipe + coordinator)
- no factor reads another factor; shared selections are plain bindings; result assembles with one generic combination sentence.
- no factor id substring of a tool name; docstrings carry formats only.
- frozen_time 'YYYY-MM-DD HH:MM:SS EDT'; task_tools.py: no datetime/random/uuid imports; ordinal-day helper only as class static method (not needed: tools take dates from ctx.now()).
- identifiers: phones 41055503xx, EIN4 3000-3999, PIN 3xxxxx, org/contact surnames I-L, persona refs 30000-39999, domains from own names.
- scratch only in /tmp/prepaid_service_hours_0069/.

## Status log
- design committed; task 0 policies, tools, world and task JSON written; per-task gates green.
- task 1 written and green; final difficulty-wide gate block 7/7 green.
- task 1 refined: prerequisites = remote-session draw (post_remote_session_draw_4c084c45), installation-visit draw (post_install_visit_draw_14ae60a8, flat per-unit install minutes from the delivered hardware order) and project-time draw (post_project_time_draw_e9603a55); root extension quote signed by the client (sign_block_extension_cebc1113). Onsite non-install visits stay under base conversion so the task-0 correction (recorded band/level) stays consistent.

## Round 2 rework plan (audit policy_task/prepaid_service_hours r1)
- P3 correction is dropped (no 4 honest factors possible: floor/rounding bite only on a 10-hour block, which cannot hold the visit history; band/level on the recorded draw are lookups). Replacement in task 0: timebank_ext_service_visit_draw (agent, state_due, new tool) = draw of an ordinary (non-installation) onsite service visit: band param, call-out method (first hour at emergency rate / after-hours floor / as recorded), dispatch level param, ClearPath after-hours courtesy param.
- Task 0 tree: root repeat-order quote <- service-visit draw (value_input) and <- travel entry (value_input); travel waits on the visit's own draw (value_input: same-day and per-ticket counts), single-record sentences.
- All selectors single-record ("most recent ... routed to the block" + "not yet on the ledger" test + tie rules), prerequisite sentences single-record.
- P2: day-split method (shared date / same ticket same date / one trip), parity tier 2 uncapped value of the trip charge, scoped to sizes drawing travel.
- P4: band -> parameter factor; call-out method (first-hour weighting / weekend floor / as rounded); ClearPath rate tiers Professional / Standard-Essentials-Monitor (all reachable); band overwrite declared.
- P5: install minutes method (staged per-unit / standard max(billable, per-unit) / billable); rush tiers same-day / within window / none; non-installation visits figure 0; band overwrite declared.
- P6: band param + minutes method (weekend cutover floor / after-hours window whole hours / as logged); class factor dropped; minutes+band overwrites declared; tie rule (most minutes first).
- P1/P7 payment schedules key on the block invoice's own payments (full/partial/unpaid).
- XF26: no plain binding reads a factor-owned binding (combinations move into result).
- Seeds: managed seat changes, renewal counts on 12-month renewal terms, managed fee/payment rows, security endpoint/IR ledgers, hardware and project invoices/payments, project discount per project charter; every historic draw recomputed under the round-2 rules.
