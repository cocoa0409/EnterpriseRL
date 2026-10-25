# worklog project_engagements (env_0069)
- task 0 closed: S0 project_ext_sow_signature_rate_lock (user, 5 factors) -> D0 project_ext_signature_deposit (agent root, 6 factors); per-task gates 7/7 green.
- task 1 closed: project_ext_milestone_billing -> project_ext_restart_repricing (user) -> project_ext_restart_change_order_fee -> project_ext_restart_remobilization (root); per-task gates green.
INSTANTIATE round 1: gates 7/7 green

## REWORK round 2 (audit revision_1: T0-1, T1-1..T1-6, C1..C15) — plan
- C1 generic assembly sentences (5 rules); C2/C3/C4/C14 restart change order identified as the signed change order with the highest change order number, registered on or after resumed_date; fees summed by that number (no tie); conditions mirror sentences.
- C5 (a) start-lead states a start on/before signature; (b) a change order registered before resumed_date is not a restart change order; (c) a restart change order always carries a fee (no waiver), so the remobilization wait is never vacuous.
- C6 replaced_by restate base content for out-of-scope engagements; C7 hold-length definition moved into the factor sentence; C8 short-duration tier becomes a floor at min_contract_value_usd; C9 docstrings: no example values, no half-up claims.
- C10 client-standing as points off the class deposit_pct; C11 monotone hold ladders (each longer tier adds to the shorter one); C12 fee basis continuous and monotone, third tier adds a review block.
- C13/T1-5 milestone factors become retentions explicitly released by the next true-up or the final invoice (no credits).
- C15/T1-6 the client's signature applies the change order: contract_value_usd += delta and change_order_count += 1; every policy reads contract_value_usd.
- T1-1 persona states customer_id, change order number, value change. T0-1/T1-2 complete ledgers (Sentinel for Premier, all monthly fees, onboarding fee, seat baseline, TimeBank orders/invoices, managed tickets for draws, hardware quote approvals).

### method-shape all-pairs (XF 23)
- prepaid_hours_component: flat K | K x hours/threshold (adds hours) | none (0 only with no hours granted) — pass.
- planned_duration: est | est x 90/duration (adds duration) | max(est, min_contract_value_usd) (adds floor) — pass.
- change_order_schedule: share x cv | share-through x cv - billed (adds billed) | share x original (original replaces cv) — pass.
- hold_length: u x R | u x R + block (adds tariff) | + e x R x months (adds months) — pass, monotone.
- fee_basis: A | A + p(d - W) (adds d) | + review hours x architect rate (adds tariff) — pass, continuous, monotone.
- hold_span: F | F + w x weeks (adds weeks) | + F x months/3 (adds months) — pass, monotone.

### probe table (scratch probes.py; expected -> probe result)
| probe | policy | expected | result | rule tier |
|---|---|---|---|---|
| cancelled ClearPath Enterprise listed first | rate lock / deposit | 13.1 / 14,077.80 | 13.1 / 14,077.80 | active agreement only |
| no ClearPath agreement | rate lock / deposit | 13.1 / 14,077.80 | 1.1 / 14,077.80 | every managed tier "otherwise" |
| scheduled start before signature | deposit | 14,077.80 | 13,150.52 | start-lead top tier (stated) |
| planned duration 18 days | deposit | 14,077.80 | 22,524.48 | floor tier |
| cancelled ClearPath first / none | milestone, re-pricing, remob | 53,088.00 / 8,469.28 / 3,929.70 | unchanged / 53,088.00, 10,668.96, 5,689.70 | "otherwise" tiers |
| same-day duplicate completion of milestone 2 | milestone | 53,088.00 | 53,088.00 | highest milestone number |
| withdrawn higher-numbered change order | fee / remob | 360.30 / 3,929.70 | 360.30 / 3,929.70 | signed only |
| restart CO registered before resumed_date | fee | 360.30 | 0.00 | not a restart change order |
| resumed_date absent | fee | 360.30 | 0.00 | no restart change order |
| second CO fee same day for another CO | remob | 3,929.70 | 3,929.70 | fees summed by restart CO number |

### round 2 claims
- T0-1: Sentinel MDR Standard seeded (ordered before the Premier signing) with complete billing; ClearPath ledger complete (baseline proration, 30 monthly fees, payments, two late fees); TimeBank order forms, invoices, payments; tickets behind every draw; hardware quote approvals; gold gains the supporting reads. Gold values unchanged (13.1, 14,077.80).
- T1-1: persona passes customer_id, change order number and value change (the tool's arguments).
- T1-2: ClearPath onboarding fee 9,000.00, seat baseline, baseline proration and every monthly fee present.
- T1-3 / C11: hold ladders monotone (each longer tier adds to the shorter tier's formula).
- T1-4 / C12: fee basis continuous and monotone; restart change orders never waived.
- T1-5 / C13: milestone credits replaced by retentions that the next true-up or the final invoice bills again; no credit exists to be billed back.
- T1-6 / C15: the client's signature updates contract_value_usd and change_order_count; all policies read contract_value_usd or the signed change-order deltas consistently.
- C1 generic assembly sentences; C2/C3 restart change order = signed change order with the highest number, registered on or after resumed_date (quotes swept); C4 fees summed by that change order's number; C5 negative lead and pre-resume change orders stated, restart fee never zero; C6 out-of-scope base content restated; C7 hold definition inside the factor sentences; C8 floor tier; C9 docstrings (no example values, no half-up claims); C10 points off the class deposit_pct; C14 conditions mirror their sentences.
- Gold after rework: task 0 13.1 -> 14,077.80; task 1 53,088.00 -> 8,469.28 -> 360.30 -> 3,929.70.
REWORK round 2: gates 7/7 green

## REWORK round 3 (audit revision_2: T0-1 residual, T1-7, T1-8, C1-r, N1, N2, N3) — plan
- T0-1: re-seed TimeBank draws earliest-expiry-first (2026-03-12 and 2026-04-14 part on the 20-hour block of 2025-09, rest of 2026-04-14 and 2026-09-22 on the 40-hour block); ClearPath baseline proration carried on the next monthly invoice (both tasks); full cross-product sweep recorded.
- T1-7: ClearPath onboarding fee paid before onboarding_start_date.
- T1-8 / N2: milestone factors become a change-order delta billed with the milestone that delivers it (method) and retainage components extended to clients by engagement class with a ClearPath relationship and by good standing — a late payer is billed more, never less; no retention for pending change orders.
- N1: milestone method tiers add or subtract the change-order delta (structurally different).
- C1-r: combination sentences and parameter sentences name only baseline quantities or the result.
- N3: deposit percentage floored at a positive minimum.

### XF 20/25 cross-product sweep (round 3)
- ClearPath (both tasks): seat rates = list less term discount; seat baseline at go-live; baseline proration now carried on the next monthly invoice (task 0 INV-044002, task 1 INV-045103) and paid with it; every monthly fee from the first full service month to October 2026; late fees 1.5 percent (above the tier minimum) on the first of the month after grace; balances reconcile. Task 1 onboarding fee 9,000.00 paid 2025-05-16, before onboarding_start_date 2025-05-19.
- Sentinel (task 0): ordered before the Premier signing, no bundle, 36-month discount, onboarding minimum 750.00, fees from the month after activation, balance 604.80.
- TimeBank (task 0): order forms signed, invoices paid before activation, grants on activation, draws earliest-expiry-first (C20 20 -> 8 -> 5 -> 0 on 2026-04-14; A40 40 -> 37 -> 30.5 -> 21.5 -> 17.5; B20 20), each on an out-of-scope ticket.
- Hardware (task 0): unit price = cost x 1.19, handling 15.00, late fees max(1.5 percent, 25.00), quote approvals signed, orders closed after the return window and full payment.

### method-shape all-pairs (round 3 change)
- scope_change_billing: share x cv | share x (cv - delta) (adds delta) | share x (cv - delta) + delta (adds the delta term) — all pairs pass.

### probe table (round 3 additions)
| probe | policy | expected | result |
|---|---|---|---|
| scope addition registered on the milestone 1 invoice date | milestone | 52,377.60 | 47,616.00 (standard share) |
| scope addition registered after milestone 2 completion | milestone | 52,377.60 | 46,425.60 (delta excluded) |
| no signed scope addition | milestone | 52,377.60 | 47,616.00 |
| ClearPath agreement cancelled | milestone | 52,377.60 | 53,785.60 (lower relationship retainage) |

### round 3 claims
- T0-1: TimeBank draws re-seeded earliest-expiry-first (balances 0.00 / 17.50 / 20.00); full cross-product sweep recorded above; gold unchanged (13.1, 14,077.80).
- T1-7: onboarding fee paid 2025-05-16, before onboarding started 2025-05-19.
- T1-8 / N2: no retention on late payers or pending change orders; milestone factors are the scope addition billed with the milestone that delivers it, relationship retainage by class and ClearPath tier, and good-standing retainage (late payers get less retainage, so are billed more); all four bear weight on task 1.
- N1: milestone method tiers add or subtract the change-order delta (structurally distinct from the standard share).
- C1-r: combination sentences of milestone, restart re-pricing, change-order fee and remobilization name only baseline quantities or the result; change-order fee parameter sentences multiply the administration fee.
- N3: deposit percentage floored at min_deposit_pct (5 percent), so a deposit is never 0.00.
- Gold after round 3: task 0 13.1 -> 14,077.80; task 1 52,377.60 -> 8,125.41 -> 353.21 -> 3,936.79.
REWORK round 3: gates 7/7 green

## REWORK round 4 (audit revision_3: T0-2, T0-3, T1-9, T1-10, C1-r2, N4, N5, C16) — plan
- N4/T1-9: every milestone share excludes the signed scope additions (sum of their deltas); the highest-numbered addition registered in the milestone's window is billed in full once; the milestone invoice before retainage is capped at contract_value_usd less everything billed.
- N5: good-standing retainage only for a client with ClearPath billing; absent case stated.
- C1-r2: anonymous combination sentences in restart, fee, remob; neutral tiers "left unchanged".
- C16/T0-3: scoped self-naming overwrite of the base change-request registration clause for the SOW signature.
- T0-2/T1-10: baseline seat rows carry no ticket number; schema sweep of every seeded cross-product row; EST labels outside DST.

### probe table (round 4)
| probe | expected | result |
|---|---|---|
| milestones 3 and 4 after the addition billed with milestone 2 | — | 44,640.00 and 22,320.00 (no addition re-billed); progress billing 218,832.00 <= contract 256,000.00 |
| +96,000.00 addition delivered with milestone 1 (Major) | — | 133,200.00 / 44,400.00 / 43,920.00 / 21,960.00; total 291,480.00 <= 336,000.00, final 44,520.00 |
| client with no ClearPath billing | — | good-standing retainage none (stated tier) |
- method-shape scope_change_billing: share x cv | share x (cv - sum of additions) (adds the sum) | share x (cv - sum) + delta (adds the delta term) — pass.
- schema sweep: every seeded row of both tasks — fields exist, enum values valid, baseline seat rows without ticket numbers, timestamp zones match DST.

### round 4 claims
- N4 / T1-9: a signed scope addition is billed exactly once, with the milestone that delivers it; every schedule share excludes the signed additions; the milestone invoice before retainage is capped at contract_value_usd less everything billed. Task 1 milestone 2 = 54,400.00 before retainage, 50,592.00 after.
- N5: good-standing retainage requires ClearPath billing; a client with none gets none (stated, implemented).
- C1-r2: restart re-pricing, change-order fee and remobilization combination sentences anonymous ("unless an adjustment figures it another way"); neutral tiers "left unchanged".
- C16 / T0-3: scoped self-naming overwrite of the base change-request registration clause for the SOW signature; every other client commitment stays registered as a change request.
- T0-2 / T1-10: baseline seat rows carry no ticket number; EST labels on winter timestamps; full schema sweep clean.
- Gold after round 4: task 0 13.1 -> 14,077.80 (unchanged); task 1 50,592.00 -> 8,205.76 -> 354.87 -> 3,935.13.
REWORK round 4: gates 7/7 green

## REWORK round 5 (audit revision_4: N6, N7)
### probe (round 5)
| probe | result |
|---|---|
| CO-044310-02A (+3,000.00, 2026-05-18) beside CO-044310-02 (+6,400.00, 2026-05-15) in milestone 2's window | milestone 2 = 20 % x (259,000.00 - 19,000.00) + 3,000.00 = 51,000.00 before retainage (47,430.00 after); CO-044310-02's 6,400.00 billed in full by the final invoice, as the rule now states |
| gold world (one addition per window) | milestone 2 50,592.00, unchanged |

### round 5 claims
- N6: no exact milestone key exists on change orders (schema has none), so the rule now states the computed treatment of every signed scope addition: the highest-numbered addition in a milestone's window is billed in full with that milestone; an addition sharing a window with a higher-numbered one is billed in full by the final invoice on acceptance (no schedule share includes it). Each addition is billed exactly once; rule words == compute.
- N7: the signature overwrite now covers every statement of work, fixed-fee and time-and-materials: the client e-signs the issued SOW directly and a fixed-fee SOW keeps its issue-date rate discount; change orders, termination notices and acceptance sign-offs/rejections stay registered as change requests.
- No gold value moved: task 0 13.1 -> 14,077.80; task 1 50,592.00 -> 8,205.76 -> 354.87 -> 3,935.13.
REWORK round 5: gates 7/7 green

## REWORK round 6 (render scan render_r1.md, findings 1-3)
### XF 16 sweep — every overwrite's replaced_by against its retired clause
- rate lock / classification_and_pricing: issue-date discount rule restated for fixed-fee SOWs — complete.
- rate lock / client_signed_changes: registration of change orders, termination notices, acceptance sign-offs and rejections restated, and "never signs on the client's behalf" now restated for every item — complete (finding 3).
- deposit / signature_deposit_and_kickoff: fixed-fee deposit (deposit_pct of original_value_usd, half up) restated — complete.
- milestone / fixed_fee_billing: final invoice "contract_value_usd minus everything already billed" restated — complete.
- restart re-pricing / schedule_and_holds: client-caused hold definition (client_request, client_dependency or nonpayment), termination option and re-pricing option for every other engagement restated — complete (finding 2).
- change-order fee / change_orders: fee, waiver and pure-schedule-change rule for every other change order restated — complete.
- remobilization / schedule_and_holds: base fee for every other resumption, with the client-caused hold definition, restated — complete (finding 2).
### XF 13 sweep — empty-list / None branches (scratch probes)
| probe | result |
|---|---|
| Assessment Engagement and Quick Start Project (milestone_pcts empty) | restart re-pricing evaluates, no phase points (14,750.40 on the probe world); milestone invoice 0.00 (no milestone) — no error |
| no milestone recorded | milestone invoice 0.00 (stated tier) |
| no ClearPath agreement, no ClearPath/TimeBank/hardware billing, no change orders, no work logs | every policy evaluates (rate lock 0.0, deposit 13,736.25, milestone tiers fall through, fee 0.00, remobilization 5,500.00) — no error |
| gold worlds | unchanged (13.1, 14,077.80; 50,592.00, 8,205.76, 354.87, 3,935.13) |

### round 6 claims
- 1: phases_remaining states that a class schedule with no milestones has none (no milestone open, no points); compute returns 0 milestones for an empty schedule; milestone invoice guards the empty schedule and an engagement with no recorded milestone (stated). Probed Assessment Engagement and Quick Start Project.
- 2: restart re-pricing replaced_by defines a client-caused hold (client_request, client_dependency or nonpayment) as in-force content; remobilization replaced_by restates the same definition.
- 3: signature overwrite replaced_by restates that the service desk never signs any change request on the client's behalf.
- No scored value moved.
REWORK round 6: gates 7/7 green

## REWORK round 7 (audit revision_6: N8)
### XF 16 re-sweep — each replaced_by against its retired clause, by sub-case
| policy / base clause | retired content | fixed-fee | T&M | signed / unsigned, in / out of scope | result |
|---|---|---|---|---|---|
| rate lock / classification_and_pricing (issue-date discount) | discount formula on the issue date | kept | kept from issue; replaced at signature under this policy | unsigned T&M keeps the issue-date figure | fixed (N8): formula stated for every SOW |
| rate lock / client_signed_changes (registration) | change request with CO number, type, value delta, new target date, pending e-signature; never signs for the client | SOW e-signed directly | SOW e-signed directly | change orders, termination notices, acceptance sign-offs/rejections registered with the same contents; never signs any | complete |
| deposit / signature_deposit_and_kickoff | "On signature the deposit is invoiced: deposit_pct of original_value_usd, half up" | deposit_pct of original, half up, on signature | invoiced on signature as the policy figures it (half up, stated) | — | complete |
| milestone / fixed_fee_billing | invoiced when recorded complete; share x contract value at that moment, half up | invoiced when recorded complete (now restated); figured by the policy, half up | T&M has no milestones (base) | no milestone recorded -> none (stated) | fixed: timing restated |
| restart / schedule_and_holds | client-caused hold definition; terminate or re-price after a hold longer than max | — | — | resumed fixed-fee in scope; every other: terminate or re-price; definition restated | complete |
| CO fee / change_orders | admin fee per signed change, waiver below threshold, schedule-only charged | — | — | restart CO in scope; every other CO restated | complete |
| remob / schedule_and_holds | fee when a client-caused hold exceeds the threshold | — | — | longer than max in scope; every other resumption: base fee, with the hold definition | complete |
- Task 0 provisional 7.5 reproduced by the restated sentence (Advanced clearpath_rate_discount_pct 7.5; ClearPath Premier rank 5 >= 4, active on the issue date 2026-09-21).

### round 7 claims
- N8: the rate-lock overwrite states the issue-date discount for every statement of work; a T&M SOW signed under the policy replaces it at signature, and an unsigned T&M SOW keeps it. Task 0's provisional 7.5 follows from that sentence.
- Re-sweep: the milestone overwrite now also restates that a fixed-fee milestone is invoiced when it is recorded complete; the other overwrites restate everything their retired clauses carried.
- No scored value moved: task 0 13.1 -> 14,077.80; task 1 50,592.00 -> 8,205.76 -> 354.87 -> 3,935.13.
REWORK round 7: gates 7/7 green

## REWORK round 8 (render_r2: Findings 1, 2)
### Sweep: record tests (compute vs the rule's noun) and date anchors (NOW vs a recorded date named by the rule)
| policy | binding | rule's noun or anchor | compute | verdict |
|---|---|---|---|---|
| rate lock | cp_tier, cp_term, cp_seats, cp_golive | active ClearPath agreement | CFIELD status='active' | equal |
| rate lock | tb_granted | hours granted across all TimeBank blocks | timebank_hours_granted (rolled_in/reversed excluded) | equal |
| rate lock | tenure_days, tb_granted window | signature date | NOW; the signing write records signed_date = today, so no earlier recorded date exists | equal |
| deposit | cp_late12 / hw_late12 | late fee on ClearPath / Hardware billing | managed_late_fee / hardware_late_fee (the only late-fee kinds) | equal |
| deposit | ach6 | payments received by ACH | managed_payment, payment_method='ach' | equal |
| deposit | cp_tier, cp_due, cp_monthly | active ClearPath agreement | CFIELD status='active' | equal |
| deposit | lead_days | days after the signature date | was DAYS(NOW, start) | fixed (F2): DAYS(F('signed_date'), start); the NOW fallback only covers an unsigned record, which the prerequisite keeps out of scope |
| deposit | cp_late12, hw_late12, ach6 windows | from the signature date | within_months is NOW-anchored (DSL) | fixed (F2): the rule now says the signature date is the day the deposit is invoiced, and the tool posts the deposit today |
| milestone | cp_billing | ClearPath billing (any entry) | was managed_monthly_fee only | fixed (F1): XCOUNT over every managed_billing entry |
| milestone | cp_late12, own_late12 | late fee on ClearPath / engagement billing | managed_late_fee / project_late_fee | equal |
| milestone | sa_at, sa_delta, add_sum | signed scope addition | request_status='signed', change_type='scope_addition' | equal |
| milestone | billed_to_date | deposit and milestone invoices | project_deposit_invoice + project_milestone_invoice | equal |
| milestone | ms_pos, ms_done | milestone recorded complete | project_milestones (completion records only) | equal |
| milestone | windows | invoice date | NOW; the invoice being figured is posted today | equal |
| re-pricing | remaining_value, additions, remob12, ms_open | deposit+milestone invoices; signed scope additions; remobilization fees; milestones not recorded complete | same filters | equal |
| re-pricing | cp_tier, cp_seats | active ClearPath agreement | CFIELD status='active' | equal |
| re-pricing | remob12, cp_late12 windows | re-pricing date (not defined) | NOW | fixed (sweep): the rule now says the re-pricing date is the day the client signs the restart change order |
| re-pricing | hold_days, hold_months | on_hold_date to resumed_date | F fields | equal |
| CO fee | rco_num, rco_at, delta_abs | signed change order, highest number, registered on/after resumed_date | LATEST signed by change_order_number, created_at vs resumed_date | equal |
| CO fee | co_seq | signed scope additions, scope reductions, schedule changes | the same three change_types, signed | equal |
| CO fee | growth_pct | every change order the client has signed | SUM signed value deltas | equal |
| CO fee | since_resume | registered ... days after resumed_date | DAYS(resumed_date, rco_at) | equal (no NOW) |
| remob | arch_min, ah_min | architect / after-hours time logged on the engagement | project_work_logs resource_level='architect' / time_band='after_hours' | equal |
| remob | share_pct, co_fee_net | deposit+milestone invoices; admin fees for the restart CO | same filters; change_order_number=rco_num | equal |
| remob | remob12 window | invoice date | NOW; the remobilization fee is posted today | equal |
- Probes: (F1) task-1 milestone world with the client's agreement applied and its ClearPath billing reduced to one onboarding fee gives cp_billing 1, cp_ret 2.5, invoice 51,136.00 (before the fix: 0, 0.0, 52,496.00). With no ClearPath billing it gives 0.0 and 52,496.00. (F2) task-0 deposit world with signed_date moved to 2026-10-05 gives lead_days 28, not 18.

### round 8 claims
- Finding 1: the milestone policy's cp_billing counts every ClearPath billing entry, so an applied or onboarding agreement whose billing holds only an onboarding fee gets cp_clean_pct. The rule, the basis quotes and the ladder are unchanged.
- Finding 2: the deposit's lead_days reads F('signed_date'). The window sentence now names the signature date as the day the deposit is invoiced, which is the day the windows count back from. Task 0 is unchanged: signed_date 2026-10-15 = today, lead 18 days, 14,077.80.
- Sweep: one more anchor fixed (the re-pricing date is now defined as the day the client signs the restart change order); every other row is equal (table above). Every combination sentence and its order is kept.
- No scored value moved: task 0 13.1 -> 14,077.80; task 1 50,592.00 -> 8,205.76 -> 354.87 -> 3,935.13.
REWORK round 8: gates 7/7 green

## REWORK round 9 (KB audit revision_1: S1-S4; seed-only, project.extended.yaml and task_tools.py byte-identical)
### Cross-product re-price, row by row (published docs/managed, docs/hardware, docs/security; TimeBank per blueprint/products/timebank.yaml)
| task | rows | rule applied | was | now |
|---|---|---|---|---|
| 0 | ClearPath monthly fees 2024-05..2026-10 (30) | current-month schedule as of each posting date: Sentinel bundle 3.0 (active 36-month subscription since 2024-01-24, 52 endpoints >= 50 seats) + volume break 11 x 2.0 / 50 = 0.44 -> RND(8,977.50 x 96.56 %) = 8,668.67, plus server fee 4 x 60.00 = 240.00; no seat change in any month, no F3/Business Premium, no Continuum | 8,977.50 | 8,908.67 |
| 0 | April 2024 baseline proration (on the May 2024 invoice) | seat addition proration, 30/30 x 50 x 179.55 (not a monthly fee) | 8,977.50 | 8,977.50 |
| 0 | late fee INV-044015, 2025-08-01 (only unpaid invoice) | rate 1.0 (no late fee, 11 payments in 12 months); bands 10.00 + 20.00; 25 % recent payment + 10 % Sentinel relationship; minimum 10.00 at 16 months | 134.66 | 19.50 |
| 0 | late fee INV-044026, 2026-07-01 (only unpaid invoice) | rate 1.5 (2025-08-01 fee inside 12 months); bands 45.00; 35 % off; minimum 5.00 at 27 months | 134.66 | 29.25 |
| 0 | payments | follow the invoices: 2024-05-24 17,886.17 (proration + May fee); monthly 8,908.67; late-fee checks 19.50 / 29.25 | 17,955.00 / 8,977.50 / 134.66 | as stated |
| 0 | September 2026 payment (added for the compute gate, see S1) | check CHK 32104 for 8,800.00, a partial payment the payment rules allow; 108.67 left open, still inside grace (assessment 2026-11-01) | ACH 8,977.50 | check 8,800.00 |
| 0 | balance_due_usd | open October fee 8,908.67 + September 108.67 | 8,977.50 | 9,017.34 |
| 1 | ClearPath monthly fees 2025-08..2026-10 (15) | volume break (35 x 2.0 + 46 x 4.0) / 120 = 2.1167 % -> 16,976.49; no Sentinel/Continuum/CSP/server records | 17,343.60 | 16,976.49 |
| 1 | onboarding 9,000.00 (75.00 x 120, 24-month term); July 2025 proration 17,343.60 (31/31) | signing terms / seat proration | same | same |
| 1 | late fee INV-045103, 2025-10-01 (only unpaid invoice) | rate 1.25 (no late fee, 2 payments); bands 37.50; 25 % recent payment = 28.13; Professional minimum 35.00 at 3 months | 520.31 | 35.00 |
| 1 | late fee INV-045108, 2026-03-01 (only unpaid invoice) | rate 1.5; bands 45.00; 25 % = 33.75; minimum 35.00 at 8 months | 260.15 | 35.00 |
| 1 | payments, balance | 2025-10-06 34,320.09 + 35.00; 2026-03-06 16,976.49 + 35.00; monthly 16,976.49; balance 16,976.49 | 34,687.20 / 520.31 / 260.15 / 17,343.60 | as stated |
| 0 | contract rates, onboarding, term dates, renewal | Premier 189.00 x 0.95 = 179.55, 36-month term waives onboarding, term end 2027-03-31; renewal_count 0, so no renewal rows | match | - |
| 0 | ClearPath tickets (6 resolved) | out of scope, routed to TimeBank under L6 (an active block covers the minutes); P4 first response 29 min <= 480; no labor or credit rows | match | - |
| 0 | Sentinel (subscription, 2 endpoint rows, 67 billing rows) | 11.40 / 24.00 less 6 % = 10.72 / 22.56, no bundle (ordered before ClearPath); onboarding max(416, 750) = 750.00 on the order date; 48 x 10.72 + 4 x 22.56 = 604.80 from 2024-02 (33); payments; balance 604.80 | match | - |
| 0 | Hardware (2 orders, 2 approvals, 8 billing rows) | Accessory markup 22 - 3 = 19 %: 224.91 / 490.28; totals + 15.00 handling; no deposit (0 %); final invoices on delivery; late fees 1.5 % on 2025-08-01 / 2026-08-01 = 44.35 / 81.19 (> 25.00); payments | match | - |
| 0 | TimeBank (3 orders, 3 blocks, 6 billing rows, 10 ledger rows) | 20-hour 3,160.00 (no discount), 40-hour 6,000.00 less 3 % = 5,820.00; activation on full payment, 12-month expiry; technician business-hours draws at 1.0, 15-minute increments, earliest expiry first (the 2026-04-14 draw split 5.00 + 3.00); balances 0 / 17.5 / 20 | match | - |
| both | licensing, backup | no records | - | - |

### round 9 claims
- S1: every ClearPath row in both tasks is now re-priced under the published rules: monthly fees under the seat-pricing schedule, late fees under the late-fee schedule, payments and balances follow. The re-price alone moved task 0 to 12,904.65 with an open-balance tier of +2.5. But check_compute then failed: the deposit's cross-category points cancelled (-5 + 5 - 2.5 + 2.5 = 0). So the September 2026 invoice is now short-paid by an 8,800.00 check (allowed partial payment, 108.67 open, still in grace). The balance due is 9,017.34, which is at least the 8,977.50 seat charge, so the open-balance tier is +5.0. There are now three ACH payments in six months, still the mid tier. Deposit 14,077.80 (30 % x 46,926.00). Rate lock 13.1. Factor baselines are 16,424.10, 11,731.50, 12,904.65, 15,250.95, 11,731.50 and 22,524.48; all-baseline 18,770.40; skipping the signature gives 14,985.00. The proof text in the traces, tracing, objectives, contract and rationale is updated.
- S2: task 1 monthly fees are 16,976.49 and the balance is 16,976.49. No task-1 factor reads ClearPath amounts, so 50,592.00, 8,205.76, 354.87 and 3,935.13 are unchanged.
- S3: the four late fees are 19.50, 29.25, 35.00 and 35.00, and their payments match. Late-fee counts are unchanged.
- S4: the factor trace names one_late_off_pts 5.0 off deposit_pct 25 and says the discount is locked at step 19. The task 0 contract says signed at step 19. In task 1, "step 12" is now step 13 in two places, the restart change order signature. All other step references point at the right tool, and every snake_case token in proof text is a parameter, binding, field, enum, tool or policy id.
- Hashes: project.extended.yaml 43eec9bdb4f65e54, task_tools.py 543e7e166bba6cce (unchanged).
REWORK round 9: gates 7/7 green
